"""Onde esta o texto da pagina, para o modo Misto (opcoes A e C) - 05/10/2026.

O PEDIDO
    Samuel, conferencia 14 (PADRAO do "So as letras"): "(1) A - Guardar a
    tinta forte, achando as linhas so com o leitor rapido (docTR); o leitor
    de manuscrito (Kraken) como segunda opiniao, que voce liga quando quiser".
    As opcoes A ("Guardar a tinta forte") e C ("So o texto achado") do Misto
    (core/misto.py) precisam saber onde estao as linhas de texto; a B nao.

O QUE FAZ (linhas_da_pagina)
    1. reduz a pagina ja preparada (dividida, cortada, endireitada) para o
       lado maior com LADO_DO_LEITOR pontos - o docTR reduz para 1024 por
       dentro de qualquer jeito, e assim a previa (110 DPI) e o PDF (300 DPI)
       mandam a ele quase a mesma imagem;
    2. roda o docTR fast_base (core/ocr_doctr.py, o "leitor rapido"), com o
       modelo aberto UMA vez por sessao e guardado (_detector);
    3. guarda as linhas achadas por pagina nesta sessao (_GUARDADAS, so os
       contornos das linhas, uns poucos KB por pagina), com a resolucao em
       que foram achadas: a previa acha uma vez, e a previa de novo (mudar a
       Forca do preto, arrastar o medidor) e o PDF usam as mesmas - a nao ser
       que a imagem de agora seja mais nitida para o leitor que a guardada
       (pagina pequena: a previa de 110 DPI tem menos de LADO_DO_LEITOR
       pontos e o PDF tem mais); ai acha de novo e guarda a melhor. A chave
       e quem chama que da (core.pipeline: o arquivo, a folha, a metade e a
       geometria da pagina - tudo que muda a imagem preparada; o filtro e a
       Forca do preto nao mudam onde esta o texto).

    Devolve a lista de resultados (core.ocr_comum.ResultadoOCR) que deram
    certo, para core.misto.mascara_das_linhas (que escala as linhas para o
    tamanho da imagem do filtro). Lista vazia = nao deu para saber onde esta o
    texto (leitor ausente ou com erro): quem chama faz o Misto B, o de sempre,
    e o motivo vai para o erros.log.

NAO TRAVA A TELA, MAS BLOQUEIA
    ~1 a 2,5 s por pagina neste PC (a primeira vez na sessao tambem abre o
    modelo, 1 a 3 s). Quem chama esta numa QThread: a previa (ui/tarefas.
    _TarefaPrevia, num QThreadPool) e o PDF (TarefaProcessar). Nada aqui usa
    Qt. Uma tranca (do proprio DetectorDoctr) faz duas previas ao mesmo tempo
    esperarem a vez, uma pagina por vez.

GANCHO DA SEGUNDA OPINIAO (Kraken) - DESLIGADO, SEM TELA (por enquanto)
    SEGUNDA_OPINIAO_DO_KRAKEN = True soma as linhas do Kraken as do docTR
    (core.misto.mascara_das_linhas faz a uniao, como na rodada da conferencia
    8). Custa 10 a 160 s por pagina e ~1,3 GB de memoria enquanto aberto; a
    tela para ligar e assunto do layout. Nao foi testado com o motor de
    verdade nesta ligacao (so com um falso, tests/test_misto_no_programa.py).

O QUE E SEGURO MUDAR
    LADO_DO_LEITOR (muda pouco as linhas; o docTR trabalha em 1024),
    GUARDAR_NO_MAXIMO, os textos do log.

O QUE E ARRISCADO MUDAR
    - Mandar a pagina inteira em 300 DPI: a previa e o PDF poderiam achar
      linhas um pouco diferentes (o PDF de outra sessao, sem as guardadas).
    - Guardar sem a geometria na chave: mudar o corte ou o angulo deixaria as
      linhas da imagem de antes, deslocadas.
    - Usar a linha guardada de uma imagem menos nitida que a de agora (o
      arrasto do medidor desenha a 55 DPI; o PDF ficaria com as linhas dele):
      ver _serve.

Nao importa ui/.
"""

from __future__ import annotations

import logging
import threading
from collections import OrderedDict

import cv2
import numpy as np

_log = logging.getLogger(__name__)

# O lado maior da pagina mandada ao leitor. O docTR (OnnxTR) reduz para 1024
# x 1024 por dentro, mantendo a proporcao: mandar ja nesse tamanho nao muda o
# que ele ve e deixa a previa e o PDF iguais.
LADO_DO_LEITOR = 1024

# Quantas paginas ficam guardadas (cada uma e uma lista de contornos, poucos
# KB). Passou disso, sai a mais antiga.
GUARDAR_NO_MAXIMO = 3000

# O gancho da segunda opiniao (ver o topo). Desligado de fabrica.
SEGUNDA_OPINIAO_DO_KRAKEN = False

_TRANCA = threading.Lock()
_GUARDADAS: OrderedDict = OrderedDict()
_DETECTOR = None
_KRAKEN = None


def _detector():
    """O docTR da sessao, aberto na primeira pagina que precisar."""
    global _DETECTOR
    with _TRANCA:
        if _DETECTOR is None:
            from core.ocr_doctr import DetectorDoctr

            _DETECTOR = DetectorDoctr()
        return _DETECTOR


def _kraken():
    """O motor do Kraken da sessao (so com SEGUNDA_OPINIAO_DO_KRAKEN)."""
    global _KRAKEN
    with _TRANCA:
        if _KRAKEN is None:
            from core.ocr_kraken import MotorKraken

            _KRAKEN = MotorKraken()
        return _KRAKEN


def _para_o_leitor(img: np.ndarray) -> np.ndarray:
    """A pagina com o lado maior em LADO_DO_LEITOR (so reduz, nunca aumenta)."""
    altura, largura = img.shape[:2]
    fator = LADO_DO_LEITOR / max(altura, largura)
    if fator >= 1.0:
        return img
    tamanho = (max(1, round(largura * fator)), max(1, round(altura * fator)))
    return cv2.resize(img, tamanho, interpolation=cv2.INTER_AREA)


def _lado_para_o_leitor(img: np.ndarray) -> int:
    """O lado maior da imagem que o leitor vai ver (nunca mais que LADO_DO_LEITOR)."""
    return min(max(img.shape[:2]), LADO_DO_LEITOR)


def _serve(guardada, img: np.ndarray) -> bool:
    """As linhas guardadas servem para esta imagem? Sim se foram achadas numa
    imagem pelo menos tao nitida (para o leitor) quanto esta. Assim o arrasto
    do medidor (55 DPI) usa as da previa, e o PDF de uma pagina pequena
    (menos de LADO_DO_LEITOR pontos na previa) acha de novo, melhor."""
    lado, _resultados = guardada
    return lado >= _lado_para_o_leitor(img)


def linhas_da_pagina(img: np.ndarray, chave=None, cancelar=None) -> list:
    """As linhas de texto da pagina `img` (ver o topo): lista de
    core.ocr_comum.ResultadoOCR que deram certo (vazia = nao deu).

    chave: o que identifica esta pagina preparada (None = nao guardar).
    cancelar: funcao sem argumentos, consultada antes de comecar.
    Nunca levanta excecao: erro vira lista vazia e log."""
    if chave is not None:
        with _TRANCA:
            guardada = _GUARDADAS.get(chave)
            if guardada is not None and _serve(guardada, img):
                _GUARDADAS.move_to_end(chave)
                return list(guardada[1])
    try:
        pequena = _para_o_leitor(img)
        resultados = [_detector().segmentar(pequena, cancelar=cancelar)]
        if SEGUNDA_OPINIAO_DO_KRAKEN:
            resultados.append(_kraken().segmentar(img, cancelar=cancelar))
    except Exception:  # noqa: BLE001 - sem linhas, o Misto de sempre
        _log.exception("linhas_do_texto: o leitor de texto falhou")
        return []
    certos = [r for r in resultados if r is not None and r.disponivel]
    for r in resultados:
        if r is not None and not r.disponivel:
            _log.warning("linhas_do_texto: %s indisponivel: %s (%s)",
                         r.motor, r.motivo, r.detalhe_tecnico)
    # so guarda o que deu certo por inteiro (um cancelamento ou um erro
    # tentam de novo na proxima), e nunca por cima de uma mais nitida
    if chave is not None and certos and len(certos) == len(resultados):
        lado = _lado_para_o_leitor(img)
        with _TRANCA:
            antes = _GUARDADAS.get(chave)
            if antes is None or antes[0] <= lado:
                _GUARDADAS[chave] = (lado, tuple(certos))
                _GUARDADAS.move_to_end(chave)
            while len(_GUARDADAS) > GUARDAR_NO_MAXIMO:
                _GUARDADAS.popitem(last=False)
    return certos


def aquecer_em_segundo_plano() -> None:
    """Abre o docTR numa thread a parte, para a primeira previa no Misto A ou
    C nao esperar por ele.

    Medido em 05/10/2026 neste PC: so importar a biblioteca do docTR leva
    ~7 s com o disco frio (20 s na rodada das 32 paginas, com o PC ocupado),
    e conferir o arquivo do modelo ~1 s - tudo isso caia na primeira previa.
    A tela chama isto quando o Misto A ou C passa a valer (ao abrir a
    conferencia, ao marcar "So as letras", ao escolher A ou C). Nunca na
    abertura do programa: quem nao usa o Misto nao paga os ~200 MB. Se ja
    estiver aberto (ou abrindo), nao faz nada. Erro aqui so vai para o log:
    a previa abre o leitor de novo, sob demanda."""
    global _AQUECENDO
    with _TRANCA:
        if _AQUECENDO or (_DETECTOR is not None and _DETECTOR.aberto):
            return
        _AQUECENDO = True

    def abrir() -> None:
        global _AQUECENDO
        try:
            detector = _detector()
            with detector._tranca:          # a mesma tranca do segmentar
                detector._abrir()
        except Exception:  # noqa: BLE001 - aquecer e so uma otimizacao
            _log.exception("linhas_do_texto: aquecer o leitor falhou")
        finally:
            with _TRANCA:
                _AQUECENDO = False

    threading.Thread(target=abrir, name="aquecer-leitor-de-texto", daemon=True).start()


_AQUECENDO = False


def esquecer() -> None:
    """Esvazia as linhas guardadas (seguro a qualquer hora; so custa tempo)."""
    with _TRANCA:
        _GUARDADAS.clear()


def soltar() -> None:
    """Solta da memoria o docTR (~200 MB) e o Kraken, se abertos. A proxima
    pagina que precisar abre de novo."""
    global _DETECTOR, _KRAKEN
    with _TRANCA:
        detector, kraken = _DETECTOR, _KRAKEN
        _DETECTOR = _KRAKEN = None
    for leitor in (detector, kraken):
        if leitor is not None:
            try:
                leitor.fechar()
            except Exception:  # noqa: BLE001 - fechar nunca derruba nada
                _log.exception("linhas_do_texto: erro ao fechar o leitor")
