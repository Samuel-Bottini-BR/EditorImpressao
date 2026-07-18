"""Tudo que demora roda aqui, fora da thread da interface.

Regra 3.2 da especificacao: a janela nunca congela. Análise, processamento e
geracao de prévia acontecem em QThread/QThreadPool, sempre com progresso e com
um cancelar que funciona de verdade.
"""

from __future__ import annotations

import traceback

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal

from core.pdf_io import ErroPDF, abrir_pdf
from core.pipeline import Cancelou, analisar_projeto, processar, renderizar_pagina
from modelos import Projeto
from registro import registrar_erro

# Quantas previas ficam guardadas na memoria. Cada uma tem ~900 px de altura;
# 30 delas cabem folgado e cobrem a navegacao para frente e para tras.
TAMANHO_CACHE = 30


def _mensagem_amigavel(erro: Exception) -> str:
    """Traduz qualquer excecao para uma frase que o Kaique entenda.

    O texto técnico vai para o arquivo de log, nunca para a tela (regra 3.3).
    """
    if isinstance(erro, ErroPDF):
        return str(erro)
    if isinstance(erro, MemoryError):
        return ("Este livro ficou grande demais para a memória do computador. "
                "Tente de novo em qualidade normal.")
    if isinstance(erro, PermissionError):
        return ("Não consegui gravar o arquivo. Ele pode estar aberto em outro "
                "programa - feche e tente de novo.")
    if isinstance(erro, OSError):
        return "Não consegui gravar o arquivo. Verifique se ha espaço em disco."
    return "Aconteceu um problema inesperado. O programa continua funcionando."


class TarefaAnalise(QThread):
    """Le o livro em baixa resolução e propoe corte, ângulo, recorte e filtro."""

    progresso = Signal(int, int, str)
    concluida = Signal(object)   # Projeto
    falhou = Signal(str)

    def __init__(self, projeto: Projeto) -> None:
        super().__init__()
        self.projeto = projeto
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            resultado = analisar_projeto(
                self.projeto,
                progresso=lambda f, t, txt: self.progresso.emit(f, t, txt),
                cancelado=lambda: self._cancelar,
            )
            if not self._cancelar:
                self.concluida.emit(resultado)
        except Cancelou:
            pass
        except Exception as erro:  # noqa: BLE001 - nada pode derrubar o programa
            registrar_erro("analise", traceback.format_exc())
            self.falhou.emit(_mensagem_amigavel(erro))


class TarefaProcessar(QThread):
    """Gera o PDF final."""

    progresso = Signal(int, int, str)
    concluida = Signal(str)      # caminho gravado
    falhou = Signal(str)
    cancelada = Signal()

    def __init__(self, projeto: Projeto) -> None:
        super().__init__()
        self.projeto = projeto
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            caminho = processar(
                self.projeto,
                progresso=lambda f, t, txt: self.progresso.emit(f, t, txt),
                cancelado=lambda: self._cancelar,
            )
            self.concluida.emit(caminho)
        except Cancelou:
            self.cancelada.emit()
        except Exception as erro:  # noqa: BLE001
            registrar_erro("processar", traceback.format_exc())
            self.falhou.emit(_mensagem_amigavel(erro))


class _SinaisPrevia(QObject):
    pronta = Signal(str, object)   # chave, imagem numpy
    falhou = Signal(str)


class _TarefaPrevia(QRunnable):
    """Gera UMA prévia. Descartavel: o pool cuida do ciclo de vida."""

    def __init__(self, chave: str, caminho_pdf: str, projeto: Projeto,
                 indice_pagina: int, dpi: int, sinais: _SinaisPrevia) -> None:
        super().__init__()
        self.chave = chave
        self.caminho_pdf = caminho_pdf
        self.projeto = projeto
        self.indice_pagina = indice_pagina
        self.dpi = dpi
        self.sinais = sinais

    def run(self) -> None:
        try:
            if self.chave.startswith("folha:"):
                self._folha_crua()
                return
            if not 0 <= self.indice_pagina < len(self.projeto.paginas):
                return
            pagina = self.projeto.paginas[self.indice_pagina]
            # Cada tarefa abre o seu proprio documento: um fitz.Document nao
            # pode ser usado por duas threads ao mesmo tempo.
            doc = abrir_pdf(self.caminho_pdf)
            try:
                img, _ = renderizar_pagina(doc, self.projeto, pagina, dpi=self.dpi)
            finally:
                doc.close()
            self.sinais.pronta.emit(self.chave, img)
        except Exception:  # noqa: BLE001 - previa que falha nao derruba a tela
            registrar_erro("previa", traceback.format_exc())
            self.sinais.falhou.emit(self.chave)

    def _folha_crua(self) -> None:
        """A folha inteira, sem nenhum processamento.

        E o que a aba 'Onde cortar' precisa: o usuario tem que ver a lombada
        como ela veio para saber onde a linha deve ficar.
        """
        from core.endireitar import girar_90
        from core.pdf_io import pagina_para_array

        doc = abrir_pdf(self.caminho_pdf)
        try:
            img = pagina_para_array(doc, self.indice_pagina, dpi=self.dpi)
        finally:
            doc.close()
        folha = self.projeto.folhas[self.indice_pagina]
        if folha.rotacao:
            img = girar_90(img, folha.rotacao)
        self.sinais.pronta.emit(self.chave, img)


class GerenciadorPrevias(QObject):
    """Fila de prévias com cache.

    Duas coisas garantem que a tela de conferir abra em segundos mesmo com 500
    páginas: só pedimos a prévia da página visivel (mais 3 adiante, de fundo) e
    guardamos as ultimas TAMANHO_CACHE em memória.
    """

    pronta = Signal(str, object)

    def __init__(self, caminho_pdf: str, projeto: Projeto, parent=None) -> None:
        super().__init__(parent)
        self.caminho_pdf = caminho_pdf
        self.projeto = projeto
        self._cache: dict[str, np.ndarray] = {}
        self._ordem: list[str] = []
        self._pedidas: set[str] = set()

        self._pool = QThreadPool(self)
        # Duas ao mesmo tempo: uma para a pagina que o usuario esta olhando e
        # outra para o pre-carregamento. Mais que isso so briga por CPU com a
        # propria interface.
        self._pool.setMaxThreadCount(2)

        self._sinais = _SinaisPrevia()
        self._sinais.pronta.connect(self._guardar)
        self._sinais.falhou.connect(self._esquecer_pedido)

    # --- chave ------------------------------------------------------------

    def chave(self, indice: int, dpi: int) -> str:
        """A chave inclui tudo que muda a imagem: trocar o filtro invalida o
        cache daquela página sozinho, sem limpar o resto."""
        if not 0 <= indice < len(self.projeto.paginas):
            return f"{indice}:invalida"
        p = self.projeto.paginas[indice]
        f = self.projeto.folhas[p.folha]
        return (
            f"{indice}:{dpi}:{p.filtro}:{p.forca_preto}:{p.metade}:"
            f"{p.angulo_manual}:{p.recorte}:"
            f"{f.posicao_corte:.4f}:{f.rotacao}:{f.dividir}:"
            f"{self.projeto.limpar}:{self.projeto.endireitar}:"
            f"{self.projeto.cortar_bordas}"
        )

    # --- uso --------------------------------------------------------------

    def pegar(self, indice: int, dpi: int) -> np.ndarray | None:
        """Devolve na hora se estiver no cache; senao pede e devolve None."""
        chave = self.chave(indice, dpi)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        self.pedir(indice, dpi)
        return None

    def pedir(self, indice: int, dpi: int) -> None:
        chave = self.chave(indice, dpi)
        if chave in self._cache or chave in self._pedidas:
            return
        if not 0 <= indice < len(self.projeto.paginas):
            return
        self._pedidas.add(chave)
        self._pool.start(
            _TarefaPrevia(chave, self.caminho_pdf, self.projeto, indice, dpi, self._sinais)
        )

    # --- folha crua (aba "Onde cortar") -----------------------------------

    def chave_folha(self, indice: int, dpi: int) -> str:
        rotacao = (
            self.projeto.folhas[indice].rotacao
            if 0 <= indice < len(self.projeto.folhas) else 0
        )
        return f"folha:{indice}:{dpi}:{rotacao}"

    def pegar_folha(self, indice: int, dpi: int) -> np.ndarray | None:
        chave = self.chave_folha(indice, dpi)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        if chave not in self._pedidas and 0 <= indice < len(self.projeto.folhas):
            self._pedidas.add(chave)
            self._pool.start(
                _TarefaPrevia(chave, self.caminho_pdf, self.projeto, indice, dpi, self._sinais)
            )
        return None

    def pre_carregar_folhas(self, indice: int, dpi: int, quantas: int = 3) -> None:
        for salto in range(1, quantas + 1):
            if indice + salto < len(self.projeto.folhas):
                self.pegar_folha(indice + salto, dpi)

    def pre_carregar(self, indice: int, dpi: int, quantas: int = 3) -> None:
        """Adianta as próximas páginas enquanto o usuario olha a atual."""
        for salto in range(1, quantas + 1):
            self.pedir(indice + salto, dpi)

    def invalidar(self, indice: int | None = None) -> None:
        """Some com o cache (de uma página ou de tudo)."""
        if indice is None:
            self._cache.clear()
            self._ordem.clear()
            return
        prefixo = f"{indice}:"
        for chave in [c for c in self._ordem if c.startswith(prefixo)]:
            self._cache.pop(chave, None)
            self._ordem.remove(chave)

    # --- interno ----------------------------------------------------------

    def _guardar(self, chave: str, img: np.ndarray) -> None:
        self._pedidas.discard(chave)
        self._cache[chave] = img
        self._ordem.append(chave)
        while len(self._ordem) > TAMANHO_CACHE:
            velha = self._ordem.pop(0)
            self._cache.pop(velha, None)
        self.pronta.emit(chave, img)

    def _esquecer_pedido(self, chave: str) -> None:
        self._pedidas.discard(chave)

    def _promover(self, chave: str) -> None:
        if chave in self._ordem:
            self._ordem.remove(chave)
            self._ordem.append(chave)

    def parar(self) -> None:
        self._pool.clear()
        self._pool.waitForDone(3000)
