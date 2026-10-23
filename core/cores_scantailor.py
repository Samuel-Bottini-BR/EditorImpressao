"""As cores do ScanTailor Advanced: "letras com a cor delas" e "reduzir cores" (item 2.11, 20/10/2026).

O PEDIDO
    Item 2.11 do plano: "Segmentação de cor / reduzir cores". Samuel,
    conferência 10 (05/10/2026), P10: "(a) Trazer como opção, desligada de
    fábrica (recomendado)" - "letras com a cor delas". Regra da Fase 2
    (13/10/2026): igual ao ScanTailor, com os ajustes de fábrica dele,
    desligado de fábrica.

COMO O SCANTAILOR FAZ (OutputGenerator.cpp, v1.2.1; código dele em
core/nativo/st_ferramentas.dll, cola em ligacao-ferramentas/saida.cpp)
    - "Color segmentation" (só no preto e branco): depois de binarizar e limpar
      os pontinhos, cada peça preta é pintada com a cor que ela tem na página
      (a página com a luz igualada); o papel fica branco. ColorSegmenter separa
      as peças por cor (limiar em cada canal, "Reduce noise" 7 de fábrica).
    - "Posterize": reduz o número de cores (nível 4 de fábrica, "forçar preto e
      branco" ligado, sem normalizar). No preto e branco só vale junto com a
      segmentação; nos filtros de cor, vale na página filtrada.

O QUE FAZ AQUI
    aplicar(preparada, saida, filtro, letras_com_a_cor, reduzir_cores, dpi):
    o último passo do filtro da página (core.pipeline._filtrar).
    - Preto e branco com "letras com a cor delas": o ScanTailor pinta cada
      ponto PRETO da página que sai com a cor dele (tirada da página
      preparada); o resto da página que sai (papel branco, foto em cinza,
      decoração com a cor original) fica como estava. Com "reduzir cores"
      junto, as cores das letras são reduzidas.
    - Outro filtro (Original, Melhorar, Mágico pro) com "reduzir cores": a
      página filtrada é posterizada.
    - "Tirar o fundo", ou as duas caixinhas desmarcadas: nada muda.
    A página sai em cor (monocromática = False) quando muda.

    As duas escolhas moram na página (ConfigPagina.letras_com_a_cor e
    ConfigPagina.reduzir_cores), desmarcadas de fábrica: livro já começado sai
    igual ao de hoje.

O QUE É SEGURO MUDAR
    Os textos da tela (ROTULO_*, EXPLICACAO_*, FRASE_DO_DESFAZER).

O QUE É ARRISCADO
    - FABRICA: os números do ScanTailor (BlackWhiteOptions.cpp e
      ColorCommonOptions.cpp). Mudar deixa de ser "igual ao ScanTailor".
    - A regra aprovada "no Preto e branco o vermelho sai preto" (V1, 30/09)
      continua sendo a de fábrica; "letras com a cor delas" é o contrário dela,
      por isso só vale com a caixinha marcada.
    - O recuo: sem a DLL, a página sai como sairia sem as caixinhas (e o motivo
      vai para o erros.log uma vez). Trocar por "erro" pararia o livro.
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass

import cv2
import numpy as np

from core import st_ferramentas as st

_log = logging.getLogger(__name__)

ROTULO_LETRAS = "Letras com a cor delas"
EXPLICACAO_LETRAS = (
    "No Preto e branco, cada letra sai com a cor que ela tem no livro (o título "
    "vermelho sai vermelho, a letra azul sai azul) e o papel continua branco. "
    "Desmarcada, toda letra sai preta (o de sempre).")
ROTULO_REDUZIR = "Reduzir cores"
EXPLICACAO_REDUZIR = (
    "Junta as cores parecidas em poucas cores chapadas. No Preto e branco só vale "
    "com \"Letras com a cor delas\" marcada; nos outros filtros vale na página toda.")
FRASE_DO_DESFAZER = "{rotulo} na página {pagina}: {estado}"


@dataclass(frozen=True)
class Opcoes:
    """Os números de fábrica do ScanTailor (ColorSegmenterOptions e
    PosterizationOptions)."""

    normalizar: bool = True        # a página preparada com a luz igualada (preto e branco)
    ruido: int = 7                 # "Reduce noise"
    ajuste_vermelho: int = 0
    ajuste_verde: int = 0
    ajuste_azul: int = 0
    nivel: int = 4                 # "Posterize": nível
    normalizar_cores: bool = False
    forcar_preto_e_branco: bool = True


FABRICA = Opcoes()


def letras_ligadas(pagina) -> bool:
    return bool(getattr(pagina, "letras_com_a_cor", False))


def reduzir_ligado(pagina) -> bool:
    return bool(getattr(pagina, "reduzir_cores", False))


def cores(img: np.ndarray, dpi, *, preto_e_branco: np.ndarray | None = None,
          posterizar: bool = False, opcoes: Opcoes = FABRICA,
          biblioteca: st.BibliotecaScanTailor | None = None) -> st.Resultado:
    """As cores do ScanTailor numa página.

    img: uint8, cinza ou azul/verde/vermelho. Com `preto_e_branco` (uint8, 2
    dimensões, menor que 128 = preto): a segmentação - cada peça preta com a
    cor dela em `img` (o resto branco). Sem: só a posterização de `img`.
    Devolve st.Resultado: .imagem azul/verde/vermelho do tamanho da página, ou
    None com .motivo. Nunca levanta exceção; não muda as entradas.
    """
    biblioteca = biblioteca or st.padrao()
    segmentar = preto_e_branco is not None
    try:
        if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or img.ndim not in (2, 3):
            raise ValueError("a página tem de ser uint8, cinza ou com 3 canais")
        if img.ndim == 3 and img.shape[2] != 3:
            raise ValueError("a página colorida tem de ter 3 canais")
        if segmentar and (preto_e_branco.dtype != np.uint8 or preto_e_branco.shape != img.shape[:2]):
            raise ValueError("o preto e branco tem de ser uint8 do tamanho da página")
        if not segmentar and not posterizar:
            raise ValueError("nada a fazer: nem segmentar nem posterizar")
        dpi_x, dpi_y = st.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return st.indisponivel("A página não pôde ser passada às cores do ScanTailor.", str(erro))
    altura, largura = img.shape[:2]
    recusa = st.motivo_de_recusa(largura, altura, dpi_x, dpi_y, "as cores do ScanTailor")
    if recusa is not None:
        return st.indisponivel(recusa, f"página {largura}x{altura}, DPI {dpi_x}x{dpi_y}")
    funcao = biblioteca.funcao("st_ferramentas_cores")
    if funcao is None:
        return st.Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)

    entrada = np.ascontiguousarray(img)
    pb = np.ascontiguousarray(preto_e_branco) if segmentar else None
    saida = np.empty((altura, largura, 3), np.uint8)
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    try:
        codigo = funcao(entrada.ctypes.data_as(ctypes.c_void_p), largura, altura,
                        int(entrada.strides[0]), 1 if entrada.ndim == 2 else 3,
                        pb.ctypes.data_as(ctypes.c_void_p) if segmentar else None,
                        int(pb.strides[0]) if segmentar else 0,
                        dpi_x, dpi_y, int(bool(opcoes.normalizar)), int(segmentar),
                        int(opcoes.ruido), int(opcoes.ajuste_vermelho), int(opcoes.ajuste_verde),
                        int(opcoes.ajuste_azul), int(bool(posterizar)), int(opcoes.nivel),
                        int(bool(opcoes.normalizar_cores)), int(bool(opcoes.forcar_preto_e_branco)),
                        saida.ctypes.data_as(ctypes.c_void_p), int(saida.strides[0]),
                        erro, len(erro))
    except Exception as falha:  # noqa: BLE001
        return st.indisponivel("As cores do ScanTailor falharam nesta página.",
                               f"{type(falha).__name__}: {falha}")
    segundos = time.perf_counter() - inicio
    if codigo != st.OK:
        detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
        if codigo == st.ERRO_MEMORIA:
            return st.indisponivel("Faltou memória para as cores desta página.", detalhe)
        return st.indisponivel("As cores do ScanTailor falharam nesta página.", detalhe)
    return st.Resultado(saida, None, None, segundos)


_AVISADOS: set[str] = set()
_TRANCA = threading.Lock()


def _avisar_uma_vez(motivo, detalhe) -> None:
    chave = f"{motivo}|{detalhe}"
    with _TRANCA:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("cores do ScanTailor indisponíveis, a página saiu sem elas: %s (%s)", motivo, detalhe)
    st.anotar_no_erros_log("cores do ScanTailor (item 2.11): a página saiu sem elas", motivo, detalhe)


def _bgr(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def aplicar(preparada: np.ndarray, saida: np.ndarray, filtro: str, letras_com_a_cor: bool,
            reduzir_cores: bool, dpi=None, *, opcoes: Opcoes = FABRICA,
            biblioteca: st.BibliotecaScanTailor | None = None) -> tuple[np.ndarray, bool] | None:
    """O último passo do filtro da página (ver o topo). preparada: a página
    antes do filtro; saida: o que o filtro deu. Devolve (imagem, False) se
    mudou, ou None se nada muda (caixinhas desmarcadas, filtro em que elas não
    valem, ou a DLL não rodou)."""
    from core.filtros import PRETO_E_BRANCO, TIRAR_FUNDO
    from core import pontinhos_scantailor

    if filtro == TIRAR_FUNDO:
        return None
    no_pb = filtro == PRETO_E_BRANCO
    if no_pb and not letras_com_a_cor:
        return None
    if not no_pb and not reduzir_cores:
        return None
    try:
        dpi_ok = float(dpi) > 0
    except (TypeError, ValueError):
        dpi_ok = False
    if not dpi_ok:
        dpi = pontinhos_scantailor.dpi_pela_altura(saida.shape[0])
    if no_pb:
        cinza = saida if saida.ndim == 2 else cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)
        pretos = cinza == 0
        if preparada.shape[:2] != cinza.shape:
            return None
        binaria = np.where(pretos, 0, 255).astype(np.uint8)
        resultado = cores(preparada, dpi, preto_e_branco=binaria, posterizar=reduzir_cores,
                          opcoes=opcoes, biblioteca=biblioteca)
        if not resultado.disponivel:
            _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
            return None
        final = _bgr(saida).copy()
        final[pretos] = resultado.imagem[pretos]
        return final, False
    resultado = cores(saida, dpi, posterizar=True, opcoes=opcoes, biblioteca=biblioteca)
    if not resultado.disponivel:
        _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
        return None
    return resultado.imagem, False
