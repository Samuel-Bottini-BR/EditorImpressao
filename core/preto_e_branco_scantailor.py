"""Os dez jeitos de fazer o preto e branco do ScanTailor Advanced (item 2.8 da Fase 2, 20/10/2026).

O PEDIDO
    Samuel, conferência 10 (05/10/2026), P8: "(b) Trazer os dez do ScanTailor
    como opções a mais". Regra da Fase 2 (13/10/2026): igual ao ScanTailor,
    com os ajustes de fábrica dele; o que muda a imagem vem desligado de
    fábrica, para livro já começado sair igual ao de hoje.

O QUE JÁ EXISTIA (conferido em 20/10/2026, antes de começar)
    A aba Filtro tem, desde setembro, "Algoritmo: Automático / Sauvola / Otsu /
    Wolf" (core.filtros.ALGORITMOS_PB). Esses três são do DoxaPy e do OpenCV,
    NÃO do ScanTailor, e o "Automático" (o de fábrica) é receita nossa, com as
    regras que o Samuel aprovou. Nada disso muda aqui: os dez do ScanTailor
    entram como opções A MAIS na mesma lista; "Automático" continua o de
    fábrica (ConfigPagina.algoritmo_preto_branco = "auto"), então nenhum livro
    muda sozinho.

O QUE FAZ
    binarizar(img, dpi, metodo, ...): a saída "preto e branco" do ScanTailor,
    na mesma ordem dele (OutputGenerator.cpp, processWithoutDewarping):
    igualar a luz -> suavização Savitzky-Golay -> um dos dez jeitos ->
    suavização morfológica. Tudo no código original (core/nativo/
    st_ferramentas.dll, cola em terceiros/scantailor-advanced/
    ligacao-ferramentas/saida.cpp). Com os ajustes de fábrica do ScanTailor
    (BlackWhiteOptions.cpp): janela 200, k do Sauvola 0,34, k do Wolf 0,3,
    limites do Wolf 1 e 254, ajuste do limiar 0, as três etapas ligadas.

    preto_e_branco(img, metodo, forca, dpi): o mesmo, com o medidor "Força do
    preto" (0 a 100, 50 no meio) virando o ajuste do limiar do ScanTailor
    (-100 a 100, 0 no meio; ajuste_do_medidor). Devolve None se a DLL não
    puder rodar (quem chama cai no "Automático" e o motivo vai para o log).

    No programa, quem chama é core.filtros.filtro_preto_e_branco, quando a
    página tem um destes códigos em ConfigPagina.algoritmo_preto_branco. As
    regras do Preto e branco que não são o jeito de binarizar continuam
    valendo por cima, como em qualquer escolha da lista: a letra colorida sai
    preta (V1 e A1, _com_a_tinta_colorida), o "Limpar a sujeira" da página, o
    "Só as letras", a gravura em cinza.

O QUE É SEGURO MUDAR
    NOMES_NA_TELA e EXPLICACAO_NA_TELA (só a tela lê).

O QUE É ARRISCADO
    - Os códigos de METODOS: vão para o projeto.json. Mudar um faz o livro
      salvo cair no "Automático" (filtros.binarizar trata código estranho como
      Sauvola do DoxaPy, e filtro_preto_e_branco não o reconhece como do
      ScanTailor).
    - FABRICA: são os números do ScanTailor (BlackWhiteOptions.cpp). Mudar
      deixa de ser "igual ao ScanTailor".
    - ajuste_do_medidor: a régua do medidor. O meio (50) tem de dar 0, o
      ajuste de fábrica do ScanTailor.
    - O DPI: a suavização Savitzky-Golay escolhe a janela pelo DPI (5, 7 ou 11
      pontos). DPI errado = suavização errada. O programa passa o mesmo DPI
      de verdade do "Limpar a sujeira" (core.pipeline.pontinhos_da_pagina);
      sem DPI, sai pela altura (pontinhos_scantailor.dpi_pela_altura).
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas as st

_log = logging.getLogger(__name__)

# O código de cada jeito no projeto.json -> o número do BinarizationMethod do
# ScanTailor (BlackWhiteOptions.h: T_OTSU = 0 ... T_EDGEDIV = 9), na ordem dele.
METODOS = {
    "st_otsu": 0,
    "st_sauvola": 1,
    "st_wolf": 2,
    "st_fox": 3,
    "st_window": 4,
    "st_bradley": 5,
    "st_grad": 6,
    "st_edgeplus": 7,
    "st_blurdiv": 8,
    "st_edgediv": 9,
}
CODIGOS = tuple(METODOS)          # a ordem da tela (a do ScanTailor)

# Os nomes na lista "Algoritmo" da aba Filtro. São os nomes do próprio
# ScanTailor (a lista dele, "Binarization"), com "do ScanTailor" para não
# confundir com Sauvola, Otsu e Wolf que o programa já tinha (DoxaPy).
# Provisórios até o agente de layout (layout/Botoes e funcoes para o layout.md).
NOMES_NA_TELA = {
    "st_otsu": "Otsu do ScanTailor",
    "st_sauvola": "Sauvola do ScanTailor",
    "st_wolf": "Wolf do ScanTailor",
    "st_fox": "Fox do ScanTailor",
    "st_window": "Window do ScanTailor",
    "st_bradley": "Bradley do ScanTailor",
    "st_grad": "Grad do ScanTailor",
    "st_edgeplus": "EdgePlus do ScanTailor",
    "st_blurdiv": "BlurDiv do ScanTailor",
    "st_edgediv": "EdgeDiv do ScanTailor",
}
EXPLICACAO_NA_TELA = (
    "Jeito de separar a tinta do papel.\n"
    "Automático: o programa escolhe, página por página (o de sempre).\n"
    "Os \"do ScanTailor\" são os dez do programa ScanTailor, com o código dele: "
    "antes de separar, ele iguala a luz da página e alisa a borda das letras. "
    "O Otsu do ScanTailor é o que ele usa de fábrica.")


@dataclass(frozen=True)
class Opcoes:
    """As opções do preto e branco do ScanTailor (BlackWhiteOptions). Os
    números de fábrica são os dele (BlackWhiteOptions.cpp, construtor)."""

    janela: int = 200
    coef_sauvola: float = 0.34
    coef_wolf: float = 0.3
    wolf_minimo: int = 1
    wolf_maximo: int = 254
    normalizar: bool = True          # "Equalize illumination" (preto e branco)
    savitzky_golay: bool = True      # "Savitzky-Golay smoothing"
    morfologica: bool = True         # "Morphological smoothing"


FABRICA = Opcoes()

AJUSTE_MINIMO, AJUSTE_MAXIMO = -100, 100     # a tela do ScanTailor (Otsu e os outros)


def e_do_scantailor(codigo) -> bool:
    """O código de algoritmo é um dos dez do ScanTailor?"""
    return isinstance(codigo, str) and codigo in METODOS


def ajuste_do_medidor(forca) -> int:
    """O medidor "Força do preto" (0 a 100, 50 no meio) no ajuste do limiar
    do ScanTailor (-100 a 100, 0 = o de fábrica dele): o medidor inteiro
    cobre a régua inteira do ScanTailor, 2 pontos do limiar por ponto do
    medidor. Mais escuro no medidor = mais preto no ScanTailor (o mesmo
    sentido: o "Darker" dele sobe o número)."""
    try:
        valor = float(forca)
    except (TypeError, ValueError):
        valor = 50.0
    ajuste = int(round((valor - 50.0) * 2.0))
    return max(AJUSTE_MINIMO, min(AJUSTE_MAXIMO, ajuste))


def binarizar(img: np.ndarray, dpi, metodo: str = "st_otsu", ajuste: int = 0,
              opcoes: Opcoes = FABRICA, *,
              biblioteca: st.BibliotecaScanTailor | None = None) -> st.Resultado:
    """O preto e branco do ScanTailor numa página.

    img: uint8, cinza (2 dimensões) ou azul, verde, vermelho (3 canais, OpenCV).
    dpi: o DPI da imagem (um número ou um par).
    metodo: um dos CODIGOS. ajuste: o ajuste do limiar (-100 a 100).
    Devolve st.Resultado: .imagem uint8 com 0 (preto) e 255 (branco), do
    tamanho da página; None se indisponível, com .motivo em português.
    Nunca levanta exceção; não muda `img`.
    """
    biblioteca = biblioteca or st.padrao()
    try:
        if metodo not in METODOS:
            raise ValueError(f"jeito desconhecido: {metodo!r}")
        if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or img.ndim not in (2, 3):
            raise ValueError("a página tem de ser uint8, cinza ou com 3 canais")
        if img.ndim == 3 and img.shape[2] != 3:
            raise ValueError("a página colorida tem de ter 3 canais (azul, verde, vermelho)")
        dpi_x, dpi_y = st.dpi_inteiro(dpi)
        ajuste = int(ajuste)
        if not AJUSTE_MINIMO <= ajuste <= AJUSTE_MAXIMO:
            raise ValueError(f"ajuste fora de {AJUSTE_MINIMO} a {AJUSTE_MAXIMO}: {ajuste}")
    except (TypeError, ValueError) as erro:
        return st.indisponivel("A página não pôde ser passada ao preto e branco do ScanTailor.",
                               str(erro))
    altura, largura = img.shape[:2]
    recusa = st.motivo_de_recusa(largura, altura, dpi_x, dpi_y, "o preto e branco do ScanTailor")
    if recusa is not None:
        return st.indisponivel(recusa, f"página {largura}x{altura}, DPI {dpi_x}x{dpi_y}")

    funcao = biblioteca.funcao("st_ferramentas_preto_e_branco")
    if funcao is None:
        return st.Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)

    entrada = np.ascontiguousarray(img)
    canais = 1 if entrada.ndim == 2 else 3
    saida = np.empty((altura, largura), np.uint8)
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    try:
        codigo = funcao(entrada.ctypes.data_as(ctypes.c_void_p), largura, altura,
                        int(entrada.strides[0]), canais, dpi_x, dpi_y,
                        METODOS[metodo], ajuste, int(opcoes.janela),
                        ctypes.c_double(opcoes.coef_sauvola), ctypes.c_double(opcoes.coef_wolf),
                        int(opcoes.wolf_minimo), int(opcoes.wolf_maximo),
                        int(bool(opcoes.normalizar)), int(bool(opcoes.savitzky_golay)),
                        int(bool(opcoes.morfologica)),
                        saida.ctypes.data_as(ctypes.c_void_p), int(saida.strides[0]),
                        erro, len(erro))
    except Exception as falha:  # noqa: BLE001
        return st.indisponivel("O preto e branco do ScanTailor falhou nesta página.",
                               f"{type(falha).__name__}: {falha}")
    segundos = time.perf_counter() - inicio
    if codigo != st.OK:
        detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
        if codigo == st.ERRO_MEMORIA:
            return st.indisponivel("Faltou memória para o preto e branco desta página.", detalhe)
        return st.indisponivel("O preto e branco do ScanTailor falhou nesta página.", detalhe)
    return st.Resultado(saida, None, None, segundos)


_AVISADOS: set[str] = set()
_TRANCA_DOS_AVISOS = threading.Lock()


def _avisar_uma_vez(motivo: str | None, detalhe: str | None) -> None:
    """O motivo de ter caído no "Automático" vai para o erros.log uma vez por
    sessão (senão seria uma linha por página)."""
    chave = f"{motivo}|{detalhe}"
    with _TRANCA_DOS_AVISOS:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("preto e branco do ScanTailor indisponível, usei o Automático: %s (%s)",
                 motivo, detalhe)


def preto_e_branco(img: np.ndarray, metodo: str, forca=50, dpi=None, *,
                   opcoes: Opcoes = FABRICA,
                   biblioteca: st.BibliotecaScanTailor | None = None) -> np.ndarray | None:
    """O preto e branco do ScanTailor com o medidor da página (ajuste_do_medidor).

    dpi None ou inválido: sai pela altura (pontinhos_scantailor.dpi_pela_altura,
    a mesma suposição do "Limpar a sujeira"). Devolve a imagem (0 e 255) ou
    None se a DLL não puder rodar (o motivo vai para o log, uma vez)."""
    from core import pontinhos_scantailor

    try:
        dpi_ok = float(dpi) > 0
    except (TypeError, ValueError):
        dpi_ok = False
    if not dpi_ok:
        dpi = pontinhos_scantailor.dpi_pela_altura(img.shape[0])
    resultado = binarizar(img, dpi, metodo, ajuste_do_medidor(forca), opcoes,
                          biblioteca=biblioteca)
    if resultado.disponivel:
        return resultado.imagem
    _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
    return None
