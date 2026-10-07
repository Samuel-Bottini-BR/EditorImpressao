"""Tudo que demora roda aqui, fora da thread da interface.

Regra 3.2 da especificacao: a janela nunca congela. Análise, processamento e
geracao de prévia acontecem em QThread/QThreadPool, sempre com progresso e com
um cancelar que funciona de verdade.
"""

from __future__ import annotations

import traceback
from pathlib import Path

import numpy as np
import shiboken6
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal

from core.misto import escolhas_da_pagina as escolhas_do_misto
from core.pontinhos_scantailor import escolha_da_pagina as pontinhos_da_pagina
from core.pipeline import faixa_da_sobra
from core.pdf_io import ErroPDF, abrir_pdf
from core.pipeline import (
    Cancelou,
    ErroPDFSalvoComOutroNome,
    analisar_projeto,
    processar,
    renderizar_com_filtro,
    renderizar_pagina,
)
from modelos import Projeto
from registro import registrar_erro

# Ordem da fila de previas (QThreadPool.start: maior sai primeiro). D4,
# 06/10/2026: a pagina que esta na tela passa na frente das adiantadas
# (pre_carregar) - depois de girar "todas", a fila estava cheia de pedidos
# adiantados do giro de antes, e a pagina da vez esperava atras deles.
# Seguro mudar: os numeros, mantendo a da vez maior.
PRIORIDADE_DA_VEZ = 1
PRIORIDADE_ADIANTADA = 0

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
        """Pede para a analise parar. E so uma bandeira - quem checa e o
        callback `cancelado` passado a analisar_projeto, entre uma pagina e
        outra, o que faz o cancelar responder rapido sem interromper no meio
        de uma pagina."""
        self._cancelar = True

    @property
    def foi_cancelada(self) -> bool:
        """Alguem pediu para parar (cancelar)? A janela usa para ignorar um
        resultado que chegue depois do cancelar (ui/janela_principal.py,
        _analise_pronta)."""
        return self._cancelar

    def run(self) -> None:
        """Ponto de entrada da QThread. Nunca deixa excecao escapar: registra
        no log e emite `falhou` com mensagem em portugues (regra 3.3)."""
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
    """Gera o PDF final.

    `antigo_preso` (conserto de 05/10/2026, achado do verificador): quando o
    PDF antigo estava aberto em outro programa e nao pode ser substituido, o
    core grava o novo como "nome (2).pdf" e sobe ErroPDFSalvoComOutroNome. Isso
    NAO e falha - o PDF ficou pronto: sai por `concluida`, com o caminho do
    "(2)", e `antigo_preso` guarda o nome do arquivo antigo, para a tela
    "Ficou pronto!" explicar (ui/janela_principal.py::_processamento_pronto).
    Nada vai para o erros.log. Vazio no caso normal. E preenchido ANTES de
    emitir `concluida`, entao quem recebe o sinal ja o ve. Arriscado: voltar a
    tratar esse caso no `except Exception` (a tela voltava para Conferir, o
    cartao nao virava "PDF gerado" e o destino guardado ficava o antigo).
    """

    progresso = Signal(int, int, str)
    concluida = Signal(str)      # caminho gravado
    falhou = Signal(str)
    cancelada = Signal()

    def __init__(self, projeto: Projeto) -> None:
        super().__init__()
        self.projeto = projeto
        self._cancelar = False
        self.antigo_preso = ""

    def cancelar(self) -> None:
        """Pede para o processamento parar entre uma página e outra (mesma
        logica de TarefaAnalise.cancelar)."""
        self._cancelar = True

    def run(self) -> None:
        """Ponto de entrada da QThread: gera o PDF final e emite concluida/
        cancelada/falhou conforme o resultado."""
        try:
            caminho = processar(
                self.projeto,
                progresso=lambda f, t, txt: self.progresso.emit(f, t, txt),
                cancelado=lambda: self._cancelar,
            )
            self.concluida.emit(caminho)
        except Cancelou:
            self.cancelada.emit()
        except ErroPDFSalvoComOutroNome as salvo:
            # pronto, com outro nome: e sucesso (ver o docstring da classe)
            antigo = getattr(salvo, "antigo", None) or self.projeto.caminho_saida or "?"
            self.antigo_preso = Path(antigo).name
            self.concluida.emit(str(salvo.caminho))
        except Exception as erro:  # noqa: BLE001
            registrar_erro("processar", traceback.format_exc())
            self.falhou.emit(_mensagem_amigavel(erro))


class TarefaConverterZonas(QThread):
    """Converte as zonas do livro inteiro para o formato novo, por tras, ao
    abrir (decisao Z1 (b) do Samuel, 05/10/2026: "O livro inteiro, por tras,
    ao abrir"). O trabalho e de core.pipeline.converter_zonas_do_livro; aqui
    so o fio, o andamento e o cancelar.

    Mexe no projeto da tela (anota ConfigPagina.geometria_das_zonas, sem
    mexer nas zonas), por isso NAO trabalha numa copia: a gravacao seguinte
    da janela leva o que foi convertido. A conta e protegida pela trava das
    zonas (core/zonas_na_folha.TRANCA_DAS_ZONAS), a mesma da gravacao.

    Prioridade NORMAL, de proposito (medido em 05/10/2026): com
    QThread.LowPriority, num computador ocupado, o Windows deixava o fio de
    prioridade baixa parado SEGURANDO o GIL do Python, e a janela inteira
    ficava 2 a 3 s sem responder (inversao de prioridade). Arriscado: baixar
    a prioridade de novo.
    """

    # Cada sinal leva a propria tarefa: a janela confere se e a da vez (um
    # sinal atrasado de uma tarefa ja parada nao entra), sem depender do
    # QObject.sender().
    andamento = Signal(object, int, int)    # tarefa, feitas, total
    terminou = Signal(object, int)          # tarefa, quantas paginas ela converteu

    def __init__(self, projeto: Projeto) -> None:
        super().__init__()
        self.projeto = projeto
        self.feitas = 0
        self._cancelar = False

    def cancelar(self) -> None:
        """Pede para parar antes da proxima pagina (so uma bandeira). O que ja
        foi convertido fica; o resto e convertido da proxima vez."""
        self._cancelar = True

    @property
    def foi_cancelada(self) -> bool:
        """Alguem pediu para parar?"""
        return self._cancelar

    def _avancar(self, feitas: int, total: int) -> None:
        self.feitas = feitas
        self.andamento.emit(self, feitas, total)

    def run(self) -> None:
        """Ponto de entrada da QThread. Nunca deixa excecao escapar: so vai
        para o log (as paginas que faltarem convertem quando forem
        desenhadas, como antes)."""
        from core.pipeline import converter_zonas_do_livro

        convertidas = 0
        try:
            convertidas = converter_zonas_do_livro(
                self.projeto, progresso=self._avancar, cancelado=lambda: self._cancelar)
        except Exception:  # noqa: BLE001 - nada pode derrubar o programa
            registrar_erro("converter_zonas", traceback.format_exc())
        self.terminou.emit(self, convertidas)


class _SinaisPrevia(QObject):
    """Sinais de uma tarefa de prévia. Existe separado de _TarefaPrevia porque
    QRunnable nao e QObject e nao pode emitir sinal Qt sozinho."""

    # chave, imagem numpy, geracao do pedido (GerenciadorPrevias._geracao_de;
    # None = folha crua, que nunca fica velha: o giro vai na chave e no pedido)
    pronta = Signal(str, object, object)
    falhou = Signal(str, object)              # chave, geracao do pedido


class _SinaisCartoes(QObject):
    """Mesma ideia de _SinaisPrevia, para as tarefas de cartao de filtro."""

    prontos = Signal(int, dict, object)   # indice_pagina, {chave_filtro: imagem}, chave


class _TarefaCartoes(QRunnable):
    """Calcula os cartoes de filtro que faltam, fora da tela.

    A amostra ja vem pronta (sem PDF, sem pipeline) - so aplica os filtros.
    Existe por causa da regra 3.2: k_para_a_letra usa skeletonize, que pode
    levar varios segundos numa pagina de traco fino (gravura), e isso rodando
    direto na tela travava a interface inteira.
    """

    def __init__(self, indice_pagina: int, base: np.ndarray, filtros: list[str],
                 forca_preto: int, clareza: int, intensidade: int,
                 sinais: _SinaisCartoes, chave: object = None) -> None:
        super().__init__()
        self.chave = chave             # volta como veio (GerenciadorPrevias.pedir_cartoes)
        self.indice_pagina = indice_pagina
        self.base = base
        self.filtros = filtros
        self.forca_preto = forca_preto
        self.clareza = clareza
        self.intensidade = intensidade
        self.sinais = sinais

    def run(self) -> None:
        """Aplica cada filtro pedido na amostra e emite todos de uma vez.
        Falha silenciosa (so vira log): o cartao so fica "preparando..." e a
        tela continua funcionando."""
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
        _emitir_se_vivo(self.sinais, self.sinais.prontos, self.indice_pagina, resultados,
                        self.chave)


class _TarefaPrevia(QRunnable):
    """Gera UMA prévia. Descartavel: o pool cuida do ciclo de vida.

    filtro: None (o padrao) desenha a pagina como ela esta. Um filtro desenha
    a pagina COMO SAIRIA com ele, sem muda-la (core.pipeline.
    renderizar_com_filtro) - item 1.1: o cartao "Tirar o fundo" e o
    "comparar" da tela ampliada, que precisam do resultado de verdade do
    core/camadas.py (le o PDF, ~1 a 2 s), por isso numa tarefa de fundo.
    """

    def __init__(self, chave: str, caminho_pdf: str, projeto: Projeto,
                 indice_pagina: int, dpi: int, sinais: _SinaisPrevia,
                 filtro: str | None = None, rotacao: int | None = None,
                 geracao: tuple | None = None) -> None:
        super().__init__()
        self.chave = chave
        # De que "geracao" da pagina e o pedido (GerenciadorPrevias._geracao_de):
        # volta junto com a imagem, e o gerenciador joga fora a que chegar de
        # antes de um invalidar (D4, 06/10/2026). None: sempre vale.
        self.geracao = geracao
        self.caminho_pdf = caminho_pdf
        self.projeto = projeto
        self.indice_pagina = indice_pagina
        self.dpi = dpi
        self.sinais = sinais
        self.filtro = filtro
        # So para a folha crua: o giro que a CHAVE promete, anotado na hora
        # do pedido (GerenciadorPrevias.pegar_folha). Ler folha.rotacao aqui,
        # no outro fio, guardaria sob a chave do giro de antes uma folha
        # girada depois (a pessoa girou enquanto a tarefa esperava na fila).
        self.rotacao = rotacao

    def run(self) -> None:
        """Renderiza a pagina (ou a folha crua) e emite o resultado pelo
        sinal - nunca levanta excecao para fora, so registra e emite falhou."""
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
                if self.filtro is None:
                    img, _ = renderizar_pagina(doc, self.projeto, pagina, dpi=self.dpi)
                else:
                    img, _ = renderizar_com_filtro(doc, self.projeto, pagina,
                                                   self.filtro, dpi=self.dpi)
            finally:
                doc.close()
            _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img, self.geracao)
        except Exception:  # noqa: BLE001 - previa que falha nao derruba a tela
            registrar_erro("previa", traceback.format_exc())
            _emitir_se_vivo(self.sinais, self.sinais.falhou, self.chave, self.geracao)

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
        _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img, self.geracao)

    def _folha_crua(self) -> None:
        """A folha inteira, sem nenhum processamento alem do giro de 90 em 90
        (self.rotacao; 0 = como veio no PDF).

        E o que a aba 'Onde cortar' precisa: o usuario tem que ver a lombada
        como ela veio para saber onde a linha deve ficar. Sem o giro
        (rotacao 0), e a base dos cartoes da aba Filtro e do "comparar" da
        tela ampliada, que passam por core.pipeline.preparar_metade - e e
        ele que gira (D1, 06/10/2026).
        """
        from core.endireitar import girar_90
        from core.pdf_io import pagina_para_array

        doc = abrir_pdf(self.caminho_pdf)
        try:
            img = pagina_para_array(doc, self.indice_pagina, dpi=self.dpi)
        finally:
            doc.close()
        rotacao = self.rotacao
        if rotacao is None:            # pedido sem o giro anotado: o de agora
            rotacao = self.projeto.folhas[self.indice_pagina].rotacao
        if rotacao:
            img = girar_90(img, rotacao)
        _emitir_se_vivo(self.sinais, self.sinais.pronta, self.chave, img, self.geracao)


class GerenciadorPrevias(QObject):
    """Fila de prévias com cache.

    Duas coisas garantem que a tela de conferir abra em segundos mesmo com 500
    páginas: só pedimos a prévia da página visivel (mais 3 adiante, de fundo) e
    guardamos as ultimas TAMANHO_CACHE em memória.
    """

    pronta = Signal(str, object)
    cartoes_prontos = Signal(int, dict, object)   # indice, {filtro: imagem}, chave do pedido

    def __init__(self, caminho_pdf: str, projeto: Projeto, parent=None) -> None:
        """Cria os dois pools (prévias e cartões, separados de propósito -
        ver o comentário abaixo) e as filas de sinal/cache vazias."""
        super().__init__(parent)
        self.caminho_pdf = caminho_pdf
        self.projeto = projeto
        self._cache: dict[str, np.ndarray] = {}
        self._ordem: list[str] = []
        # chave pedida -> geracao do pedido (None para a folha crua)
        self._pedidas: dict[str, tuple | None] = {}
        # D4 (06/10/2026): quantas vezes cada pagina (e o livro todo) foi
        # invalidada. A tarefa de previa le o projeto quando RODA, nao quando
        # e pedida: uma previa pedida antes de um giro e desenhada depois
        # dele era guardada sob a chave de antes, com a folha girada dentro
        # (e voltava do cache, errada, ao desfazer o giro). Cada pedido leva
        # a geracao em que foi feito; o que chega de uma geracao que ja
        # passou nao entra no cache nem na tela (_guardar).
        self._geracoes: dict[int, int] = {}
        self._geracao_do_livro = 0

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

    def chave(self, indice: int, dpi: int, filtro: str | None = None) -> str:
        """A chave inclui tudo que muda a imagem: trocar o filtro invalida o
        cache daquela página sozinho, sem limpar o resto.

        filtro: o da pagina (None) ou outro, para chave_com_filtro."""
        if not 0 <= indice < len(self.projeto.paginas):
            return f"{indice}:invalida"
        p = self.projeto.paginas[indice]
        f = self.projeto.folhas[p.folha]
        # modo Misto (05/10/2026): o que vale nesta pagina (dela ou do livro)
        ligado, escolhas = escolhas_do_misto(self.projeto, p)
        mist = (f"{escolhas.fora_do_texto}/{escolhas.papel_da_gravura}/"
                f"{escolhas.letras_na_moldura}" if ligado else "-")
        # "Limpar pontinhos" (06/10/2026): o que vale nesta pagina (dela ou do
        # livro) - trocar no livro tambem refaz a previa
        return (
            f"{indice}:{dpi}:{filtro or p.filtro}:{p.forca_preto}:"
            f"{p.clareza_melhorar}:{p.intensidade_magico}:{p.metade}:"
            f"{p.angulo_manual}:{p.recorte}:"
            f"{f.posicao_corte:.4f}:{f.rotacao}:{f.dividir}:"
            f"{self.projeto.limpar}:{self.projeto.endireitar}:"
            f"{self.projeto.cortar_bordas}:{mist}:"
            f"{pontinhos_da_pagina(self.projeto, p)}:"
            # item 2.1: o corte da sobra muda a pagina desenhada
            f"{faixa_da_sobra(f, p, self.projeto)}"
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

    def pedir(self, indice: int, dpi: int, prioridade: int | None = None) -> None:
        """Poe na fila do pool, se ainda nao estiver no cache nem ja pedida.

        prioridade: PRIORIDADE_DA_VEZ (o padrao; a pagina na tela) ou
        PRIORIDADE_ADIANTADA (pre_carregar)."""
        chave = self.chave(indice, dpi)
        if chave in self._cache or chave in self._pedidas:
            return
        if not 0 <= indice < len(self.projeto.paginas):
            return
        self._comecar(chave, indice, dpi,
                      PRIORIDADE_DA_VEZ if prioridade is None else prioridade)

    # --- pedidos e geracoes (D4) ---------------------------------------------

    def _geracao_de(self, indice: int) -> tuple:
        """A geracao de agora da pagina `indice`: muda a cada invalidar dela
        ou do livro todo."""
        return (indice, self._geracao_do_livro, self._geracoes.get(indice, 0))

    def _comecar(self, chave: str, indice: int, dpi: int, prioridade: int,
                 filtro: str | None = None, rotacao: int | None = None,
                 folha: bool = False) -> None:
        """Anota o pedido e poe a tarefa no pool. A folha crua (folha=True)
        nao leva geracao: o giro dela vai no pedido e na chave, e nada mais
        a muda. Prioridade maior sai primeiro (QThreadPool.start)."""
        geracao = None if folha else self._geracao_de(indice)
        self._pedidas[chave] = geracao
        self._pool.start(
            _TarefaPrevia(chave, self.caminho_pdf, self.projeto, indice, dpi, self._sinais,
                          filtro=filtro, rotacao=rotacao, geracao=geracao),
            prioridade,
        )

    # --- a pagina com outro filtro (item 1.1) --------------------------------

    def chave_com_filtro(self, indice: int, dpi: int, filtro: str) -> str:
        """Chave da pagina desenhada com `filtro` sem muda-la (ver
        pegar_com_filtro). Diferente da chave da previa normal de proposito:
        a previa normal e desenhada na pagina de verdade (e acerta os alertas
        dela), esta numa copia. Comeca com f"{indice}:", para invalidar(indice)
        limpar as duas juntas."""
        return f"{indice}:com:{self.chave(indice, dpi, filtro)}"

    def pegar_com_filtro(self, indice: int, dpi: int, filtro: str) -> np.ndarray | None:
        """A pagina como sairia com `filtro` (core.pipeline.renderizar_com_filtro).

        Item 1.1: e o cartao "Tirar o fundo" e o "comparar" da tela ampliada
        - o resultado de verdade do core/camadas.py. Mesmo jeito de `pegar`:
        devolve na hora se estiver no cache; senao pede, devolve None, e o
        sinal `pronta` avisa quando chegar (com chave_com_filtro)."""
        chave = self.chave_com_filtro(indice, dpi, filtro)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        if chave not in self._pedidas and 0 <= indice < len(self.projeto.paginas):
            self._comecar(chave, indice, dpi, PRIORIDADE_ADIANTADA, filtro=filtro)
        return None

    # --- imagem para ajustar o recorte (aba Bordas) ------------------------

    def chave_para_recorte(self, indice: int, dpi: int) -> str:
        """Depende de girar/dividir, nunca de `recorte` - ver
        `core.pipeline.preparar_para_recorte`. Prefixo `f"{indice}:"` igual
        ao de `chave()`, para `invalidar(indice)` limpar as duas juntas."""
        if not 0 <= indice < len(self.projeto.paginas):
            return f"{indice}:recorte:invalida"
        p = self.projeto.paginas[indice]
        f = self.projeto.folhas[p.folha]
        return (f"{indice}:recorte:{dpi}:{p.metade}:{f.posicao_corte:.4f}:{f.rotacao}:{f.dividir}:"
                f"{faixa_da_sobra(f, p, self.projeto)}")      # item 2.1

    def pegar_para_recorte(self, indice: int, dpi: int) -> np.ndarray | None:
        chave = self.chave_para_recorte(indice, dpi)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        if chave not in self._pedidas and 0 <= indice < len(self.projeto.paginas):
            self._comecar(chave, indice, dpi, PRIORIDADE_DA_VEZ)
        return None

    def pedir_cartoes(self, indice: int, base: np.ndarray, filtros: list[str],
                       forca_preto: int, clareza: int, intensidade: int,
                       chave: object = None) -> None:
        """Pede os cartoes que faltam para uma pagina, fora da thread da tela.

        chave: volta junto no sinal cartoes_prontos, para quem pediu saber de
        que estado da pagina e o resultado. A tela de conferir passa a chave
        dos cartoes (giro, corte, ajustes...) e descarta o que chegar de um
        estado que ja passou (D1, 06/10/2026)."""
        self._pool_cartoes.start(
            _TarefaCartoes(indice, base, filtros, forca_preto, clareza, intensidade,
                            self._sinais_cartoes, chave=chave)
        )

    # --- folha crua (aba "Onde cortar") -----------------------------------

    def _giro_da_folha(self, indice: int) -> int:
        """O giro de 90 em 90 da folha agora (0 se o indice nao existe)."""
        if 0 <= indice < len(self.projeto.folhas):
            return int(self.projeto.folhas[indice].rotacao) % 360
        return 0

    def chave_folha(self, indice: int, dpi: int, girada: bool = True) -> str:
        """Chave de cache da folha crua (aba "Onde cortar"): so muda com o giro
        manual. girada=False: a folha como veio no PDF (giro 0), qualquer que
        seja o giro dela - a mesma chave de uma folha nao girada."""
        rotacao = self._giro_da_folha(indice) if girada else 0
        return f"folha:{indice}:{dpi}:{rotacao}"

    def pegar_folha(self, indice: int, dpi: int, girada: bool = True,
                    prioridade: int | None = None) -> np.ndarray | None:
        """Equivalente a `pegar`, mas para a folha crua (sem processamento).

        girada=True (a aba Onde cortar e a tela ampliada no modo cortar): com
        o giro da folha. girada=False: como veio no PDF - e o que
        core.pipeline.preparar_metade espera receber, porque e ELE que gira
        (D1 do verificador, 06/10/2026: os cartoes da aba Filtro passavam a
        folha ja girada ao preparar_metade, e ela saia girada duas vezes).
        Arriscado: passar uma folha girada=True ao preparar_metade.

        O giro vai anotado no pedido (_TarefaPrevia.rotacao), o mesmo da
        chave: a imagem guardada sob uma chave e sempre a do giro que ela diz.
        """
        rotacao = self._giro_da_folha(indice) if girada else 0
        chave = self.chave_folha(indice, dpi, girada)
        if chave in self._cache:
            self._promover(chave)
            return self._cache[chave]
        if chave not in self._pedidas and 0 <= indice < len(self.projeto.folhas):
            self._comecar(chave, indice, dpi,
                          PRIORIDADE_DA_VEZ if prioridade is None else prioridade,
                          rotacao=rotacao, folha=True)
        return None

    def pre_carregar_folhas(self, indice: int, dpi: int, quantas: int = 3) -> None:
        """Adianta as próximas folhas cruas enquanto a pessoa olha a atual."""
        for salto in range(1, quantas + 1):
            if indice + salto < len(self.projeto.folhas):
                self.pegar_folha(indice + salto, dpi, prioridade=PRIORIDADE_ADIANTADA)

    def pre_carregar(self, indice: int, dpi: int, quantas: int = 3) -> None:
        """Adianta as próximas páginas enquanto o usuario olha a atual."""
        for salto in range(1, quantas + 1):
            self.pedir(indice + salto, dpi, prioridade=PRIORIDADE_ADIANTADA)

    def invalidar(self, indice: int | None = None) -> None:
        """Some com o cache (de uma página ou de tudo).

        D4 (06/10/2026): passa tambem a geracao da pagina (ou do livro) para
        a frente. O que ainda esta sendo desenhado foi pedido antes desta
        mudanca: quando chegar, e jogado fora (_guardar), e o pedido sai da
        lista de "ja pedidas" agora - o proximo pegar pede de novo, ja com o
        estado novo. A folha crua nao muda com nada disso (o giro vai na
        chave) e fica. Arriscado: guardar o que chega de uma geracao velha."""
        if indice is None:
            self._cache.clear()
            self._ordem.clear()
            self._geracao_do_livro += 1
            for chave in [c for c, g in self._pedidas.items() if g is not None]:
                del self._pedidas[chave]
            return
        self._geracoes[indice] = self._geracoes.get(indice, 0) + 1
        for chave in [c for c, g in self._pedidas.items() if g is not None and g[0] == indice]:
            del self._pedidas[chave]
        prefixo = f"{indice}:"
        for chave in [c for c in self._ordem if c.startswith(prefixo)]:
            self._cache.pop(chave, None)
            self._ordem.remove(chave)

    # --- interno ----------------------------------------------------------

    def _guardar(self, chave: str, img: np.ndarray, geracao: tuple | None = None) -> None:
        """Poe no cache e descarta a mais antiga se passar de TAMANHO_CACHE (LRU simples).

        geracao: a do pedido (_comecar). Se a pagina foi invalidada depois do
        pedido, a imagem e de um estado que ja passou: nao entra no cache nem
        e anunciada (D4, 06/10/2026)."""
        if geracao is not None and tuple(geracao) != self._geracao_de(geracao[0]):
            if self._pedidas.get(chave) == geracao:
                del self._pedidas[chave]
            return
        self._pedidas.pop(chave, None)
        self._cache[chave] = img
        self._ordem.append(chave)
        while len(self._ordem) > TAMANHO_CACHE:
            velha = self._ordem.pop(0)
            self._cache.pop(velha, None)
        self.pronta.emit(chave, img)

    def _esquecer_pedido(self, chave: str, geracao: tuple | None = None) -> None:
        """Tira da lista de 'ja pedidas' quando uma previa falha, para poder
        pedir de novo (so se o pedido anotado e o mesmo que falhou)."""
        if chave in self._pedidas and (geracao is None or self._pedidas[chave] == geracao):
            del self._pedidas[chave]

    def _promover(self, chave: str) -> None:
        """Move a chave para o fim da fila de LRU (foi usada agora, entao e a
        ultima que deve sair quando o cache lotar)."""
        if chave in self._ordem:
            self._ordem.remove(chave)
            self._ordem.append(chave)

    def parar(self) -> None:
        """Esvazia as filas e espera as tarefas em andamento (ate 3s cada).
        Chamar ao trocar de livro ou fechar, para nao deixar thread orfa
        escrevendo num projeto que ja foi trocado."""
        self._pool.clear()
        self._pool_cartoes.clear()
        self._pool.waitForDone(3000)
        self._pool_cartoes.waitForDone(3000)
        # O servidor de paginas fecha este livro na hora (senao, em meio
        # segundo): a pessoa pode mover ou renomear o PDF logo depois de
        # fechar ou trocar de livro (core/paginas_em_outro_processo.py).
        from core.paginas_em_outro_processo import soltar_livro

        soltar_livro(self.caminho_pdf)
