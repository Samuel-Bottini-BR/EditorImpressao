"""Tudo que demora roda aqui, fora da thread da interface.

Regra 3.2 da especificacao: a janela nunca congela. Análise, processamento e
geracao de prévia acontecem em QThread/QThreadPool, sempre com progresso e com
um cancelar que funciona de verdade.
"""

from __future__ import annotations

import traceback

import numpy as np
import shiboken6
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal

from core.pdf_io import ErroPDF, abrir_pdf
from core.pipeline import Cancelou, analisar_projeto, processar, renderizar_pagina
from modelos import Projeto
from registro import registrar_erro

# Quantas previas ficam guardadas na memoria. Cada uma tem ~900 px de altura;
# 30 delas cabem folgado e cobrem a navegacao para frente e para tras.
TAMANHO_CACHE = 30


def _emitir_se_vivo(dono: QObject, sinal, *args) -> None:
    """Emite um sinal só se o QObject dono ainda existir.

    Achado no log de produção em 08/09/2026: se a tela fecha (ou troca de
    livro) enquanto uma tarefa de fundo ainda está calculando, o objeto de
    sinais pode já ter sido destruído pelo Qt quando a tarefa termina -
    emitir nesse caso levanta `RuntimeError: Signal source has been deleted`.
    Isso não é um erro de verdade (a tela que pediria a prévia já não existe
    mais), só um resultado que ninguém vai mais usar - descartar em silêncio.
    """
    if not shiboken6.isValid(dono):
        return
    sinal.emit(*args)


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


class _SinaisCartoes(QObject):
    prontos = Signal(int, dict)   # indice_pagina, {chave_filtro: imagem}


class _TarefaCartoes(QRunnable):
    """Calcula os cartoes de filtro que faltam, fora da tela.

    A amostra ja vem pronta (sem PDF, sem pipeline) - so aplica os filtros.
    Existe por causa da regra 3.2: k_para_a_letra usa skeletonize, que pode
    levar varios segundos numa pagina de traco fino (gravura), e isso rodando
    direto na tela travava a interface inteira.
    """

    def __init__(self, indice_pagina: int, base: np.ndarray, filtros: list[str],
                 forca_preto: int, clareza: int, intensidade: int,
                 sinais: _SinaisCartoes) -> None:
        super().__init__()
        self.indice_pagina = indice_pagina
        self.base = base
        self.filtros = filtros
        self.forca_preto = forca_preto
        self.clareza = clareza
        self.intensidade = intensidade
        self.sinais = sinais

    def run(self) -> None:
        from core.filtros import aplicar_filtro

        resultados: dict[str, np.ndarray] = {}
        try:
            for chave in self.filtros:
                amostra, _ = aplicar_filtro(
                    self.base, chave, self.forca_preto, self.clareza, self.intensidade,
                )
                resultados[chave] = amostra
        except Exception:  # noqa: BLE001 - cartao que falha so fica "preparando..."
            registrar_erro("cartoes", traceback.format_exc())
        _emitir_se_vivo(self.sinais, self.sinais.prontos, self.indice_pagina, resultados)


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
            if ":recorte:" in self.chave:
                self._para_recorte()
                return
            pagina = self.projeto.paginas[self.indice_pagina]
            # Cada tarefa abre o seu proprio documento: um fitz.Document nao
            # pode ser usado por duas threads ao mesmo tempo.
            doc = abrir_pdf(self.caminho_pdf)
            try:
                img, _ = renderizar_pagina(doc, self.projeto, pagina, dpi=self.dpi)
            finally:
                doc.close()
            _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img)
        except Exception:  # noqa: BLE001 - previa que falha nao derruba a tela
            registrar_erro("previa", traceback.format_exc())
            _emitir_se_vivo(self.sinais, self.sinais.falhou, self.chave)

    def _para_recorte(self) -> None:
        """Girada e dividida, mas nunca cortada - o que a aba Bordas mostra
        enquanto o recorte está sendo ajustado. Ver `core.pipeline.
        preparar_para_recorte`: sem isso, o retângulo do recorte era desenhado
        como fração de uma prévia já cortada, e comprimia sozinho a cada
        atualização."""
        from core.pipeline import renderizar_pagina_para_recorte

        pagina = self.projeto.paginas[self.indice_pagina]
        doc = abrir_pdf(self.caminho_pdf)
        try:
            img = renderizar_pagina_para_recorte(doc, self.projeto, pagina, dpi=self.dpi)
        finally:
            doc.close()
        _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img)

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
        _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img)


class GerenciadorPrevias(QObject):
    """Fila de prévias com cache.

    Duas coisas garantem que a tela de conferir abra em segundos mesmo com 500
    páginas: só pedimos a prévia da página visivel (mais 3 adiante, de fundo) e
    guardamos as ultimas TAMANHO_CACHE em memória.
    """

    pronta = Signal(str, object)
    cartoes_prontos = Signal(int, dict)

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

        # Pool separado dos cartões de filtro. Achado ao vivo em 12/09/2026
        # (py-spy, livro Boécio): navegar rápido enche o pool de prévias acima
        # com dezenas de pedidos de pré-carregamento, e como os cartões
        # entravam na MESMA fila, um cartão podia ficar "preparando..." por
        # muito mais tempo que o razoável, sem nenhuma exceção no log -
        # parecia travado. Cartão é trabalho leve (só aplica filtro numa
        # amostra já em memória, sem tocar o PDF) e não pode esperar atrás de
        # prévia pesada.
        self._pool_cartoes = QThreadPool(self)
        self._pool_cartoes.setMaxThreadCount(1)

        self._sinais = _SinaisPrevia()
        self._sinais.pronta.connect(self._guardar)
        self._sinais.falhou.connect(self._esquecer_pedido)

        self._sinais_cartoes = _SinaisCartoes()
        self._sinais_cartoes.prontos.connect(self.cartoes_prontos.emit)

    # --- chave ------------------------------------------------------------

    def chave(self, indice: int, dpi: int) -> str:
        """A chave inclui tudo que muda a imagem: trocar o filtro invalida o
        cache daquela página sozinho, sem limpar o resto."""
        if not 0 <= indice < len(self.projeto.paginas):
            return f"{indice}:invalida"
        p = self.projeto.paginas[indice]
        f = self.projeto.folhas[p.folha]
        return (
            f"{indice}:{dpi}:{p.filtro}:{p.forca_preto}:"
            f"{p.clareza_melhorar}:{p.intensidade_magico}:{p.metade}:"
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

    # --- imagem para ajustar o recorte (aba Bordas) ------------------------

    def chave_para_recorte(self, indice: int, dpi: int) -> str:
        """Depende de girar/dividir, nunca de `recorte` - ver
        `core.pipeline.preparar_para_recorte`. Prefixo `f"{indice}:"` igual
        ao de `chave()`, para `invalidar(indice)` limpar as duas juntas."""
        if not 0 <= indice < len(self.projeto.paginas):
            return f"{indice}:recorte:invalida"
        p = self.projeto.paginas[indice]
        f = self.projeto.folhas[p.folha]
        return f"{indice}:recorte:{dpi}:{p.metade}:{f.posicao_corte:.4f}:{f.rotacao}:{f.dividir}"

    def pegar_para_recorte(self, indice: int, dpi: int) -> np.ndarray | None:
        chave = self.chave_para_recorte(indice, dpi)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        if chave not in self._pedidas and 0 <= indice < len(self.projeto.paginas):
            self._pedidas.add(chave)
            self._pool.start(
                _TarefaPrevia(chave, self.caminho_pdf, self.projeto, indice, dpi, self._sinais)
            )
        return None

    def pedir_cartoes(self, indice: int, base: np.ndarray, filtros: list[str],
                       forca_preto: int, clareza: int, intensidade: int) -> None:
        """Pede os cartoes que faltam para uma pagina, fora da thread da tela."""
        self._pool_cartoes.start(
            _TarefaCartoes(indice, base, filtros, forca_preto, clareza, intensidade,
                            self._sinais_cartoes)
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
        self._pool_cartoes.clear()
        self._pool.waitForDone(3000)
        self._pool_cartoes.waitForDone(3000)
