"""Seletor de gravura do ScanTailor Advanced, com o código original (item 1.2 da Fase 1).

O QUE FAZ
    Recebe a imagem de uma página e devolve a MÁSCARA DE GRAVURA: onde o modo
    Misto do ScanTailor Advanced acha figura (gravura, foto, iluminura) em vez
    de escrita. O trabalho é feito pela DLL core/nativo/st_gravura.dll, que é o
    código do próprio ScanTailor (terceiros/scantailor-advanced/, GPL-3)
    compilado sem mudança - só a "ligação" é nossa. A DLL é chamada por ctypes
    (não depende da versão do Python) e usa o Qt que o PySide6 já traz.

    Recompilar: .venv\\Scripts\\python.exe compilar_detector_gravura.py

SE A DLL FALTAR OU FALHAR
    Nada levanta exceção: o resultado vem "indisponível" (mascara None), com o
    motivo em português (para a tela) e o detalhe técnico (para o erros.log).
    Quem chama decide o que fazer - por exemplo, cair no detector de hoje.
    Página com DPI absurdo, minúscula ou gigante também volta "indisponível",
    SEM chegar à DLL (ver TRAVA DE SEGURANÇA abaixo): ali o código do
    ScanTailor corrompe a memória e derrubaria o programa.

AINDA NÃO ESTÁ LIGADO AO PROGRAMA (28/09/2026)
    Nem o pipeline, nem os filtros, nem a tela chamam este módulo. Ligar (com o
    botão de ligar e desligar da regra 8) é o passo seguinte. Para o item 1.1,
    figuras_pelo_scantailor() tem a mesma assinatura de
    core/camadas.DETECTOR_DE_FIGURAS.

O QUE É SEGURO MUDAR
    Os textos das mensagens; a função figuras_pelo_scantailor (é só adaptador).

O QUE É ARRISCADO
    - _preparar_funcoes(): tipos da função em C. O ctypes não confere nada; um
      tipo errado aqui vira travamento, não mensagem. Tem de bater com
      terceiros/scantailor-advanced/ligacao/st_gravura.h.
    - O DPI: o detector reduz (ou amplia) a página para 300 DPI antes de
      procurar. Passar o DPI errado muda o resultado.
    - Os padrões (normalizar_iluminacao=True, forma livre, sensibilidade 100,
      mais_sensivel=False) são os do ScanTailor Advanced no modo Misto - os do
      teste de 24/09. Mudar o padrão muda o que o Samuel aprovou.
"""

from __future__ import annotations

import ctypes
import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

_log = logging.getLogger(__name__)

CAMINHO_DLL = Path(__file__).resolve().parent / "nativo" / "st_gravura.dll"

# Tem de bater com ST_GRAVURA_VERSAO_API em st_gravura.h.
VERSAO_API = 1

# Códigos de st_gravura.h.
_CINZA, _RGB, _BGR = 1, 3, 5
_OK, _ERRO_PARAMETRO, _ERRO_MEMORIA, _ERRO_INTERNO = 0, 1, 2, 3
_FORMAS = {"desligada": 0, "livre": 1, "retangular": 2}

# O DPI em que core/camadas.py chama DETECTOR_DE_FIGURAS (camadas.DPI_DA_ANALISE).
# Repetido aqui para este módulo não depender de camadas.py.
DPI_DAS_CAMADAS = 150

# TRAVA DE SEGURANÇA (Lista de bugs, 28/09/2026, achado pelo verificador).
# Com DPI absurdo a página, reduzida a 300 DPI, vira um punhado de pontos, e o
# código do ScanTailor (a redução/ampliação de escala) ESCREVE FORA DA MEMÓRIA:
# o processo morre sem aviso (0xC0000374) ou o Python recebe "access violation".
# Não dá para consertar sem mudar o código original, então a página é recusada
# ANTES de chegar à DLL. Medido em 28/09, cada caso num processo filho com uma
# cópia da DLL:
#   - falhou com a página reduzida a 1x1 a 1200-2400 DPI (página de 3x4 pontos),
#     e, com DPI de 27.000 a 740.000, com a página reduzida a até 10x14 pontos;
#   - não falhou em nenhum dos 150 casos sorteados dentro destes limites (DPI de
#     30 a 2400, menor lado a 300 DPI entre 16 e 45 pontos, página lisa,
#     sintética e com ruído), nem nas páginas de verdade do gabarito.
# Arriscado mudar: afrouxar DPI_MINIMO/DPI_MAXIMO ou LADO_MINIMO sem medir de
# novo (em processo filho!). PONTOS_MAXIMOS não foi medido: é uma folga contra
# faltar memória (uma página de 40 MP, o teto do pdf_io, a 30 DPI viraria
# 4.000 MP a 300 DPI); 120 MP a 300 DPI é uma folha de ~ 90 x 110 cm.
DPI_MINIMO = 30
DPI_MAXIMO = 2400
LADO_MINIMO = 16                # menor lado, em pontos, na página e na página a 300 DPI
PONTOS_MAXIMOS = 120_000_000    # na página e na página a 300 DPI


@dataclass(frozen=True)
class ResultadoGravura:
    """O que detectar() devolve.

    mascara: bool, do tamanho da página (ou do retângulo de trabalho, em
        detectar_como_no_scantailor); True = gravura. None = indisponível.
    motivo: por que ficou indisponível, em português. None se deu certo.
    detalhe_tecnico: o erro de verdade, para o erros.log (nunca para a tela).
    segundos: quanto a DLL levou.
    """

    mascara: np.ndarray | None
    motivo: str | None = None
    detalhe_tecnico: str | None = None
    segundos: float = 0.0

    @property
    def disponivel(self) -> bool:
        return self.mascara is not None


def _indisponivel(motivo: str, detalhe: str | None = None) -> ResultadoGravura:
    if detalhe:
        _log.warning("gravura_scantailor: %s (%s)", motivo, detalhe)
    return ResultadoGravura(None, motivo, detalhe)


class DetectorGravuraScanTailor:
    """A DLL do ScanTailor. Carrega uma vez (na primeira chamada) e serve o livro inteiro.

    Pode ser chamada de uma QThread: enquanto a DLL trabalha, o ctypes solta o
    GIL, e a tela continua respondendo.
    """

    def __init__(self, caminho: Path | None = None) -> None:
        self.caminho = Path(caminho or CAMINHO_DLL).resolve()   # o ctypes quer caminho completo
        self._dll = None
        self._tentou = False
        self._motivo: str | None = None
        self._detalhe: str | None = None
        self._pasta_do_qt = None   # guarda o registro da pasta de DLLs do PySide6
        self._tranca = threading.Lock()

    # ------------------------------------------------------------ carregar

    def _carregar(self):
        """Abre a DLL uma única vez. Em caso de falha, guarda o motivo e devolve None."""
        with self._tranca:
            if self._tentou:
                return self._dll
            self._tentou = True
            if os.name != "nt":
                self._motivo = "O detector de gravura do ScanTailor só existe para Windows."
                return None
            if not self.caminho.is_file():
                self._motivo = ("O detector de gravura do ScanTailor não foi encontrado "
                                f"(falta {self.caminho.name}).")
                return None
            try:
                # A DLL usa o Qt6Core/Qt6Gui do PySide6: a pasta dele entra na busca de DLLs.
                import PySide6

                self._pasta_do_qt = os.add_dll_directory(str(Path(PySide6.__file__).parent))
                dll = ctypes.CDLL(str(self.caminho))
                _preparar_funcoes(dll)
                versao = dll.st_gravura_versao_api()
            except Exception as erro:  # noqa: BLE001 - nada aqui pode derrubar o programa
                self._motivo = "O detector de gravura do ScanTailor não abriu."
                self._detalhe = f"{type(erro).__name__}: {erro}"
                _log.warning("gravura_scantailor: %s", self._detalhe)
                return None
            if versao != VERSAO_API:
                self._motivo = ("O detector de gravura do ScanTailor é de outra versão "
                                "(recompile com compilar_detector_gravura.py).")
                self._detalhe = f"versão da DLL {versao}, esperada {VERSAO_API}"
                return None
            self._dll = dll
            return dll

    @property
    def disponivel(self) -> bool:
        """A DLL existe e abriu?"""
        return self._carregar() is not None

    @property
    def motivo_indisponivel(self) -> str | None:
        self._carregar()
        return self._motivo

    @property
    def origem(self) -> str | None:
        """De onde veio o código (repositório, versão, commit), gravado na DLL."""
        dll = self._carregar()
        if dll is None:
            return None
        return dll.st_gravura_origem().decode("utf-8", "replace")

    # ------------------------------------------------------------ detectar

    def detectar(self, img: np.ndarray, dpi: float | Sequence[float], *,
                 ordem: str = "BGR", normalizar_iluminacao: bool = True,
                 forma: str = "livre", sensibilidade: int = 100,
                 mais_sensivel: bool = False) -> ResultadoGravura:
        """A máscara de gravura de uma página já pronta (cortada e endireitada).

        img: uint8, altura x largura (cinza) ou altura x largura x 3 (BGR, como o
            resto do programa; ordem="RGB" para RGB). Um 4.º canal é ignorado.
        dpi: o DPI da imagem (um número, ou horizontal e vertical).
        As outras opções são as do ScanTailor Advanced (aba "Saída", modo Misto):
        forma "livre" | "retangular" | "desligada"; sensibilidade 0 a 100 (só na
        retangular); mais_sensivel = "maior sensibilidade de busca".
        """
        return self._chamar(img, dpi, None, None, ordem, normalizar_iluminacao,
                            forma, sensibilidade, mais_sensivel)

    def detectar_como_no_scantailor(self, img: np.ndarray, dpi_trabalho: float | Sequence[float],
                                    transformacao: Sequence[float],
                                    retangulo_trabalho: Sequence[int], *, ordem: str = "BGR",
                                    **opcoes) -> ResultadoGravura:
        """Refaz a conta do ScanTailor com a geometria dele (só para a régua).

        transformacao: m11 m12 m21 m22 dx dy (QTransform), da imagem original para
            o sistema de saída do ScanTailor (giro + escala para o DPI de saída).
        retangulo_trabalho: x, y, largura, altura, no sistema de saída: o
            retângulo do conteúdo com a folga de 20 pontos a 300 DPI.
        A máscara sai do tamanho do retângulo de trabalho.
        """
        return self._chamar(img, dpi_trabalho, transformacao, retangulo_trabalho, ordem,
                            opcoes.get("normalizar_iluminacao", True), opcoes.get("forma", "livre"),
                            opcoes.get("sensibilidade", 100), opcoes.get("mais_sensivel", False))

    def _chamar(self, img, dpi, transformacao, retangulo, ordem, normalizar, forma,
                sensibilidade, mais_sensivel) -> ResultadoGravura:
        dll = self._carregar()
        if dll is None:
            return ResultadoGravura(None, self._motivo, self._detalhe)
        try:
            pixels, formato = _preparar_imagem(img, ordem)
            dpi_x, dpi_y = _dpi_inteiro(dpi)
            if forma not in _FORMAS:
                raise ValueError(f"forma desconhecida: {forma!r}")
            altura, largura = pixels.shape[:2]
            if retangulo is None:
                saida_l, saida_a = largura, altura
                ret_c = None
            else:
                ret = [int(v) for v in retangulo]
                saida_l, saida_a = ret[2], ret[3]
                ret_c = (ctypes.c_int * 4)(*ret)
            if saida_l <= 0 or saida_a <= 0:
                raise ValueError("retângulo de trabalho vazio")
            xform_c = None
            if transformacao is not None:
                xform_c = (ctypes.c_double * 6)(*[float(v) for v in transformacao])
        except (TypeError, ValueError) as erro:
            return _indisponivel("A página não pôde ser passada ao detector de gravura.", str(erro))
        recusa = motivo_de_recusa(largura, altura, saida_l, saida_a, dpi_x, dpi_y)
        if recusa is not None:
            return _indisponivel(recusa, f"página {largura}x{altura}, trabalho {saida_l}x{saida_a}, "
                                         f"DPI {dpi_x}x{dpi_y}")

        mascara = np.empty((saida_a, saida_l), np.uint8)
        erro = ctypes.create_string_buffer(512)
        inicio = time.perf_counter()
        try:
            codigo = dll.st_gravura_detectar(
                pixels.ctypes.data_as(ctypes.c_void_p), largura, altura, pixels.strides[0], formato,
                dpi_x, dpi_y, xform_c, ret_c, int(bool(normalizar)), _FORMAS[forma],
                int(sensibilidade), int(bool(mais_sensivel)),
                mascara.ctypes.data_as(ctypes.c_void_p), mascara.strides[0], erro, len(erro))
        except Exception as falha:  # noqa: BLE001
            return _indisponivel("O detector de gravura do ScanTailor falhou nesta página.",
                                 f"{type(falha).__name__}: {falha}")
        segundos = time.perf_counter() - inicio
        if codigo != _OK:
            detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
            if codigo == _ERRO_MEMORIA:
                return _indisponivel("Faltou memória para achar as gravuras desta página.", detalhe)
            return _indisponivel("O detector de gravura do ScanTailor falhou nesta página.", detalhe)
        return ResultadoGravura(mascara > 0, None, None, segundos)


def _preparar_funcoes(dll) -> None:
    """Os tipos das funções em C (st_gravura.h). Ver "arriscado" no topo."""
    dll.st_gravura_versao_api.restype = ctypes.c_int
    dll.st_gravura_versao_api.argtypes = []
    dll.st_gravura_origem.restype = ctypes.c_char_p
    dll.st_gravura_origem.argtypes = []
    dll.st_gravura_detectar.restype = ctypes.c_int
    dll.st_gravura_detectar.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,   # pixels, l, a, passo, formato
        ctypes.c_int, ctypes.c_int,                                                # dpi x, y
        ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int),             # transformação, retângulo
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,                    # normalizar, forma, sens., +sens.
        ctypes.c_void_p, ctypes.c_int,                                             # máscara, passo
        ctypes.c_char_p, ctypes.c_int,                                             # erro
    ]


def _preparar_imagem(img: np.ndarray, ordem: str) -> tuple[np.ndarray, int]:
    """A imagem contígua em memória, e o formato que a DLL entende."""
    if not isinstance(img, np.ndarray) or img.dtype != np.uint8:
        raise ValueError("a página tem de ser uma imagem uint8")
    if img.ndim == 3 and img.shape[2] == 1:
        img = img[..., 0]
    if img.ndim == 2:
        formato = _CINZA
    elif img.ndim == 3 and img.shape[2] in (3, 4):
        img = img[..., :3]
        if ordem.upper() not in ("BGR", "RGB"):
            raise ValueError(f"ordem de cores desconhecida: {ordem!r}")
        formato = _BGR if ordem.upper() == "BGR" else _RGB
    else:
        raise ValueError(f"formato de imagem não suportado: {img.shape}")
    if img.shape[0] == 0 or img.shape[1] == 0:
        raise ValueError("página vazia")
    return np.ascontiguousarray(img), formato


def tamanho_a_300_dpi(largura: int, altura: int, dpi_x: int, dpi_y: int) -> tuple[int, int]:
    """O tamanho em que o detector trabalha: a conta de to300dpi() do ScanTailor."""
    return (max(1, round(largura * 300.0 / dpi_x)), max(1, round(altura * 300.0 / dpi_y)))


def motivo_de_recusa(largura: int, altura: int, trabalho_l: int, trabalho_a: int,
                     dpi_x: int, dpi_y: int) -> str | None:
    """Por que a página NÃO pode ir para a DLL (ver TRAVA DE SEGURANÇA no topo), ou None.

    largura/altura: a página que entra; trabalho_l/trabalho_a: o retângulo de
    trabalho (a própria página, sem geometria), no DPI dpi_x/dpi_y.
    """
    for dpi in (dpi_x, dpi_y):
        if not DPI_MINIMO <= dpi <= DPI_MAXIMO:
            return (f"O DPI da página ({dpi}) está fora da faixa que o detector de gravura "
                    f"aceita ({DPI_MINIMO} a {DPI_MAXIMO}).")
    reduzida = tamanho_a_300_dpi(trabalho_l, trabalho_a, dpi_x, dpi_y)
    if min(largura, altura, trabalho_l, trabalho_a, *reduzida) < LADO_MINIMO:
        return ("A página é pequena demais para o detector de gravura "
                f"(menos de {LADO_MINIMO} pontos de lado).")
    if max(largura * altura, trabalho_l * trabalho_a, reduzida[0] * reduzida[1]) > PONTOS_MAXIMOS:
        return "A página é grande demais para o detector de gravura."
    return None


def _dpi_inteiro(dpi) -> tuple[int, int]:
    """O ScanTailor guarda o DPI como número inteiro (classe Dpi)."""
    if isinstance(dpi, (int, float, np.integer, np.floating)):
        x = y = float(dpi)
    else:
        x, y = (float(v) for v in dpi)
    x_i, y_i = int(round(x)), int(round(y))
    if x_i <= 0 or y_i <= 0:
        raise ValueError(f"DPI inválido: {dpi!r}")
    return x_i, y_i


# ------------------------------------------------------------ atalhos do módulo

_padrao = DetectorGravuraScanTailor()


def disponivel() -> bool:
    """A DLL do ScanTailor existe e abriu?"""
    return _padrao.disponivel


def motivo_indisponivel() -> str | None:
    return _padrao.motivo_indisponivel


def origem() -> str | None:
    return _padrao.origem


def detectar_gravura(img: np.ndarray, dpi: float | Sequence[float], **opcoes) -> ResultadoGravura:
    """A máscara de gravura de uma página (ver DetectorGravuraScanTailor.detectar)."""
    return _padrao.detectar(img, dpi, **opcoes)


def detectar_como_no_scantailor(img: np.ndarray, dpi_trabalho, transformacao, retangulo_trabalho,
                                **opcoes) -> ResultadoGravura:
    """A conta do ScanTailor com a geometria dele (só para a régua)."""
    return _padrao.detectar_como_no_scantailor(img, dpi_trabalho, transformacao, retangulo_trabalho,
                                               **opcoes)


def figuras_pelo_scantailor(img: np.ndarray, dpi: float = DPI_DAS_CAMADAS,
                            reserva: Callable[[np.ndarray], np.ndarray] | None = None) -> np.ndarray:
    """Adaptador para core/camadas.DETECTOR_DE_FIGURAS: BGR -> float32 de 0 a 1.

    camadas.py chama o detector com a página a DPI_DA_ANALISE (150) e sem dizer
    o DPI; por isso o padrão aqui é 150. Sem a DLL, usa `reserva` (por exemplo
    camadas.figuras_pelo_detector_atual) ou, sem reserva, devolve tudo zero
    ("nenhuma figura") - quem ligar decide qual das duas.
    """
    resultado = _padrao.detectar(img, dpi)
    if resultado.disponivel:
        return resultado.mascara.astype(np.float32)
    if reserva is not None:
        return reserva(img)
    return np.zeros(img.shape[:2], np.float32)
