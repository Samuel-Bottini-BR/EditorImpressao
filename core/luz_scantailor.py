"""Item 2.17: igualar a luz e suavizar, como filtro de imagem, igual ao ScanTailor.

O QUE FAZ (o que a saída do ScanTailor Advanced v1.2.1 faz, OutputGenerator.cpp,
processWithoutDewarping; o código original está na st_ferramentas.dll versão 8,
cola em terceiros/scantailor-advanced/ligacao-ferramentas/luz.cpp)

    - IGUALAR A LUZ DA PÁGINA ("Equalize illumination"): acha o fundo da página
      como uma superfície suave (EstimateBackground) e tira dela a diferença de
      luz - o canto escuro do scanner, a sombra perto da lombada. Na página
      colorida, o brilho de cada ponto acompanha o cinza igualado
      (adjustBrightnessGrayscale), sem mexer no matiz. Vale em qualquer filtro
      (vem ANTES dele), como no ScanTailor.
    - SUAVIZAR AS LETRAS (só no Preto e branco): o Savitzky-Golay no cinza antes
      de binarizar (smoothToGrayscale; janela e grau pelo DPI, como o ScanTailor)
      e a suavização morfológica depois (morphologicalSmoothInPlace: tira os
      dentinhos e buraquinhos da borda das letras). No ScanTailor as duas são
      caixinhas do preto e branco ("Savitzky-Golay smoothing" e "Morphological
      smoothing"); aqui é uma só, como ele as liga juntas de fábrica.
    - TIRAR O CHUVISCO (filtro de Wiener, "Wiener filter"): na imagem antes do
      filtro, com o coeficiente de 0 a 100 (o ScanTailor usa de 0 a 1; janela 5).

DESLIGADO DE FÁBRICA (regra da Fase 2, 13/10/2026: muda a imagem). No
ScanTailor o "igualar a luz" e as duas suavizações vêm LIGADOS no preto e
branco (BlackWhiteOptions: normalizeIllumination, savitzkyGolaySmoothing,
morphologicalSmoothing = true) e o Wiener com 0; aqui tudo vem desligado, por
página (ConfigPagina.luz_igualar, luz_suavizar, luz_chuvisco), para livro já
começado sair igual. Quando ligados, usam os números do ScanTailor.

NÃO CONFUNDIR com o "dividir pelo fundo" do Melhorar e do Mágico pro (CLAUDE.md
§9: "Não desfazer isso"). Isto é uma opção a mais, antes do filtro; a receita
deles não muda.

SEM A DLL: devolve a imagem como veio e anota o motivo no erros.log uma vez por
sessão (nunca quebra o programa).

SEGURO MUDAR: os textos da tela. ARRISCADO: a ordem (igualar → Wiener → filtro;
no preto e branco, suavizar o cinza → binarizar → suavizar o preto e branco →
limpar pontinhos por último, como o ScanTailor: "It's important to keep
despeckling the very last operation").
"""

from __future__ import annotations

import contextlib
import contextvars
import ctypes
import logging
import threading
import time

import numpy as np

from core import st_ferramentas as st

ROTULO_IGUALAR = "Igualar a luz da página"
ROTULO_SUAVIZAR = "Suavizar as letras"
ROTULO_CHUVISCO = "Tirar o chuvisco"
EXPLICACAO_IGUALAR = ("Como o ScanTailor: tira a diferença de luz da página (o canto mais escuro, "
                      "a sombra perto da lombada) antes do filtro.")
EXPLICACAO_SUAVIZAR = ("Como o ScanTailor, só no Preto e branco: alisa a borda das letras "
                       "(tira os dentinhos e os buraquinhos).")
EXPLICACAO_CHUVISCO = ("Como o ScanTailor (filtro de Wiener): tira o chuvisco da imagem. "
                       "0 = desligado.")
FRASE_DO_DESFAZER = "{rotulo} na página {pagina}: {estado}"

# Os avisos (decisões do Samuel, 22/10/2026): o "igualar a luz" vale em todos os
# filtros, com aviso no Melhorar e no Mágico pro ("mas vai ser uma opção que eu
# posso desligar e ligar né?" - sim, a caixinha); o "tirar o chuvisco" continua
# de 0 a 100, com aviso a partir de LIMITE_DO_CHUVISCO ("mas eu vou poder
# escolher a escala né?" - sim). Seguro mudar: os textos.
AVISO_IGUALAR = ("No Melhorar e no Mágico pro, igualar a luz pode deixar a tinta mais clara "
                 "(lavada). Se acontecer, desligue esta caixinha.")
AVISO_CHUVISCO = ("Acima de 20, tirar o chuvisco pode borrar a letra. Os valores que mais "
                  "ajudam ficam entre 10 e 20.")
LIMITE_DO_CHUVISCO = 20


def avisos_da_pagina(pagina) -> list[str]:
    """Os avisos das opções de luz desta página (vazio: nenhum)."""
    from core.filtros import MAGICO_PRO, MELHORAR

    avisos = []
    if igualar_ligado(pagina) and getattr(pagina, "filtro", "") in (MELHORAR, MAGICO_PRO):
        avisos.append(AVISO_IGUALAR)
    if chuvisco(pagina) > LIMITE_DO_CHUVISCO:
        avisos.append(AVISO_CHUVISCO)
    return avisos

CAMPOS = ("luz_igualar", "luz_suavizar", "luz_chuvisco")   # os de ConfigPagina
JANELA_DO_WIENER = 5            # ColorCommonOptions: m_wienerWindowSize(5)

_log = logging.getLogger(__name__)
_TRANCA = threading.Lock()
_AVISADOS: set[str] = set()

# O que vale na página que está sendo filtrada AGORA neste fio (item 2.16:
# várias páginas ao mesmo tempo, uma por fio): (suavizar, dpi). O
# core.pipeline._filtrar põe; o core.filtros.filtro_preto_e_branco lê.
_SUAVIZAR_AGORA: contextvars.ContextVar = contextvars.ContextVar("suavizar_agora", default=None)


def _avisar_uma_vez(motivo, detalhe) -> None:
    chave = f"{motivo}|{detalhe}"
    with _TRANCA:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("igualar a luz / suavizar do ScanTailor indisponível: %s (%s)", motivo, detalhe)
    try:
        st.anotar_no_erros_log("luz do ScanTailor", motivo, detalhe)  # se existir neste ramo
    except AttributeError:
        pass


# --------------------------------------------------------------- a página

def igualar_ligado(pagina) -> bool:
    return bool(getattr(pagina, "luz_igualar", False))


def suavizar_ligado(pagina) -> bool:
    return bool(getattr(pagina, "luz_suavizar", False))


def chuvisco(pagina) -> int:
    try:
        return max(0, min(100, int(getattr(pagina, "luz_chuvisco", 0) or 0)))
    except (TypeError, ValueError):
        return 0


def alguma_ligada(pagina) -> bool:
    return igualar_ligado(pagina) or suavizar_ligado(pagina) or chuvisco(pagina) > 0


def assinatura(pagina) -> str:
    """O que muda a imagem (para a chave da prévia): "-" com tudo desligado."""
    if not alguma_ligada(pagina):
        return "-"
    return f"{int(igualar_ligado(pagina))}{int(suavizar_ligado(pagina))}{chuvisco(pagina)}"


# --------------------------------------------------------------- as contas

def _canais(img: np.ndarray) -> int:
    if img.ndim == 2:
        return 1
    if img.ndim == 3 and img.shape[2] == 3:
        return 3
    raise ValueError("a imagem tem de ser cinza ou colorida (3 canais)")


def _chamar(nome: str, img: np.ndarray, extra: tuple, canais_saida: int | None = None) -> st.Resultado:
    biblioteca = st.padrao()
    try:
        if not isinstance(img, np.ndarray) or img.dtype != np.uint8:
            raise ValueError("a imagem tem de ser uint8")
        canais = _canais(img)
    except ValueError as erro:
        return st.indisponivel("A página não pôde ser passada ao ScanTailor.", str(erro))
    altura, largura = img.shape[:2]
    recusa = st.motivo_de_recusa(largura, altura, 300, 300, "o igualar a luz do ScanTailor")
    if recusa is not None:
        return st.indisponivel(recusa, f"página {largura}x{altura}")
    funcao = biblioteca.funcao(nome)
    if funcao is None:
        return st.Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)
    entrada = np.ascontiguousarray(img)
    canais_saida = canais if canais_saida is None else canais_saida
    saida = np.empty((altura, largura) if canais_saida == 1 else (altura, largura, 3), np.uint8)
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    try:
        argumentos = [entrada.ctypes.data_as(ctypes.c_void_p), largura, altura, entrada.strides[0]]
        if nome != "st_ferramentas_suavizar_preto_e_branco":
            argumentos.append(canais)
        argumentos += list(extra)
        argumentos += [saida.ctypes.data_as(ctypes.c_void_p), saida.strides[0], erro, len(erro)]
        codigo = funcao(*argumentos)
    except Exception as falha:  # noqa: BLE001
        return st.indisponivel("A conta do ScanTailor falhou nesta página.",
                               f"{type(falha).__name__}: {falha}")
    if codigo != st.OK:
        return st.indisponivel("A conta do ScanTailor falhou nesta página.",
                               f"{nome} código {codigo}: {erro.value.decode('utf-8', 'replace')}")
    return st.Resultado(saida, None, None, time.perf_counter() - inicio)


def _ou_como_veio(resultado: st.Resultado, img: np.ndarray) -> np.ndarray:
    if resultado.disponivel:
        return resultado.imagem
    _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
    return img


def igualar_luz(img: np.ndarray) -> np.ndarray:
    """transformToWorkingCs(true) do ScanTailor: a página com a luz igualada,
    no mesmo formato (cinza ou colorida)."""
    return _ou_como_veio(_chamar("st_ferramentas_igualar_luz", img, ()), img)


def tirar_chuvisco(img: np.ndarray, forca: int) -> np.ndarray:
    """wienerColorFilterInPlace do ScanTailor, com coeficiente forca/100."""
    if forca <= 0:
        return img
    coef = ctypes.c_double(min(100, int(forca)) / 100.0)
    return _ou_como_veio(_chamar("st_ferramentas_wiener", img, (JANELA_DO_WIENER, coef)), img)


def suavizar_cinza(cinza: np.ndarray, dpi: float) -> np.ndarray:
    """smoothToGrayscale do ScanTailor (Savitzky-Golay): devolve cinza."""
    dpi_x, dpi_y = st.dpi_inteiro(dpi)
    return _ou_como_veio(_chamar("st_ferramentas_suavizar_cinza", cinza, (dpi_x, dpi_y), 1), cinza)


def suavizar_preto_e_branco(binaria: np.ndarray) -> np.ndarray:
    """morphologicalSmoothInPlace do ScanTailor: 0 = preto, 255 = branco."""
    return _ou_como_veio(_chamar("st_ferramentas_suavizar_preto_e_branco", binaria, ()), binaria)


# --------------------------------------------------------------- no filtro

def antes_do_filtro(img: np.ndarray, pagina) -> np.ndarray:
    """O que vem antes do filtro da página, na ordem do ScanTailor: igualar a
    luz, depois o Wiener. Tudo desligado (o de fábrica): devolve `img` mesmo."""
    if igualar_ligado(pagina):
        img = igualar_luz(img)
    forca = chuvisco(pagina)
    if forca > 0:
        img = tirar_chuvisco(img, forca)
    return img


@contextlib.contextmanager
def suavizar_nesta_pagina(pagina, dpi: float | None):
    """Enquanto dura, o preto e branco deste fio suaviza (se a página pediu)."""
    marca = _SUAVIZAR_AGORA.set((suavizar_ligado(pagina), dpi or 300))
    try:
        yield
    finally:
        _SUAVIZAR_AGORA.reset(marca)


def cinza_para_binarizar(cinza: np.ndarray) -> np.ndarray:
    """Chamado pelo core.filtros.filtro_preto_e_branco antes de binarizar:
    suaviza o cinza se a página da vez pediu; senão devolve o mesmo."""
    agora = _SUAVIZAR_AGORA.get()
    if not agora or not agora[0]:
        return cinza
    return suavizar_cinza(cinza, agora[1])


def preto_e_branco_suavizado(binaria: np.ndarray) -> np.ndarray:
    """Chamado pelo core.filtros.filtro_preto_e_branco depois de binarizar e
    antes de limpar os pontinhos."""
    agora = _SUAVIZAR_AGORA.get()
    if not agora or not agora[0]:
        return binaria
    return suavizar_preto_e_branco(binaria)
