"""Dividir a folha com o código do ScanTailor Advanced (item 2.1 da Fase 2).

O QUE FAZ
    Chama a função st_ferramentas_dividir da DLL comum (core/st_ferramentas.py):
    o PageLayoutEstimator::estimatePageLayout do ScanTailor Advanced v1.2.1,
    copiado sem mudança (terceiros/scantailor-advanced/src/core/filters/
    page_split/), com a cola em terceiros/scantailor-advanced/
    ligacao-ferramentas/dividir.cpp. Nada aqui reescreve a conta do ScanTailor:
    só leva a folha até a DLL e traduz a resposta para frações da largura.

    Decisões do Samuel (Registro de mudanças do plano):
      G2 (a), 05/10/2026: "Só quando o Kaique pedir, livro a livro, escolhendo
        'o do programa' ou 'o do ScanTailor', e trocando numa folha se um
        ficar ruim." -> JEITO_PROGRAMA / JEITO_SCANTAILOR (modelos.Projeto e
        ConfigFolha.dividir_como).
      G3 (b), 05/10/2026: o "corte da sobra" do ScanTailor (modo "uma página
        + sobra") entra como opção, desligada -> sobra_da_folha
        (modelos.Projeto.cortar_sobra, ConfigFolha.sobra).

OS MODOS DO SCANTAILOR (page_split::LayoutType, na mesma ordem)
    AUTOMATICO: o que o ScanTailor faz sozinho num projeto novo: folha mais
        larga que alta = duas páginas (corta na dobra); mais alta que larga =
        uma página, às vezes com a sobra cortada.
    SEM_CORTE: uma página, nada cortado.
    COM_SOBRA: "uma página + sobra": corta a beirada da folha vizinha.
    DUAS_PAGINAS: sempre divide em duas.

SE A DLL FALTAR OU FALHAR
    Nada levanta exceção: o resultado volta com `disponivel` False e o motivo
    em português; quem chama decide (a análise cai no jeito do programa).

O QUE É SEGURO MUDAR
    Os textos. A escolha de qual ponta da linha inclinada vira o corte reto
    (ver posicao_da_divisao e sobra_da_folha), desde que o teste continue
    passando.

O QUE É ARRISCADO
    - MODO_*: os números têm de ser os de page_split::LayoutType (LayoutType.h).
    - TIPO_*: os de page_split::PageLayout::Type (PageLayout.h).
    - O DPI passado: o ScanTailor mede tudo em pontos a 300 e a 150 DPI.
"""

from __future__ import annotations

import ctypes
import logging
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas

_log = logging.getLogger(__name__)

# Os jeitos de dividir que a pessoa escolhe (códigos internos, gravados no
# projeto; o texto da tela mora em NOMES_DOS_JEITOS). Nunca gravar o texto da
# tela no projeto: ele é provisório até o layout.
JEITO_PROGRAMA = "programa"
JEITO_SCANTAILOR = "scantailor"
JEITOS = (JEITO_PROGRAMA, JEITO_SCANTAILOR)
# Projeto salvo antes do item 2.1 dividia pelo nosso (core/dividir.py).
JEITO_DO_PROJETO_ANTIGO = JEITO_PROGRAMA

# Textos da tela (provisórios até o layout; ver ui/tela_opcoes.py e
# ui/tela_conferir.py). Seguro mudar.
NOMES_DOS_JEITOS = {
    JEITO_PROGRAMA: "o do programa",
    JEITO_SCANTAILOR: "o do ScanTailor",
}

# page_split::LayoutType (LayoutType.h): a ordem importa.
MODO_AUTOMATICO, MODO_SEM_CORTE, MODO_COM_SOBRA, MODO_DUAS_PAGINAS = 0, 1, 2, 3
# page_split::PageLayout::Type (PageLayout.h).
TIPO_SEM_CORTE, TIPO_COM_SOBRA, TIPO_DUAS_PAGINAS = 0, 1, 2

_NOMES_DOS_TIPOS = {TIPO_SEM_CORTE: "uma página", TIPO_COM_SOBRA: "uma página + sobra",
                    TIPO_DUAS_PAGINAS: "duas páginas"}


def jeito_valido(jeito) -> str:
    """O jeito gravado, ou o do programa se vier vazio ou estranho (projeto
    antigo, arquivo mexido à mão)."""
    return jeito if jeito in JEITOS else JEITO_PROGRAMA


@dataclass(frozen=True)
class Corte:
    """Uma linha de corte do ScanTailor, em FRAÇÃO da folha (0 a 1).

    (x_cima, y=0) e (x_baixo, y=1): as pontas nas bordas de cima e de baixo.
    A linha pode ser inclinada (a dobra fotografada torta)."""

    x_cima: float
    x_baixo: float

    @property
    def meio(self) -> float:
        return (self.x_cima + self.x_baixo) / 2.0

    @property
    def inclinacao(self) -> float:
        """Quanto a linha anda de lado do topo à base, em fração da largura."""
        return abs(self.x_cima - self.x_baixo)


@dataclass(frozen=True)
class Resultado:
    """O que o ScanTailor achou numa folha.

    tipo: TIPO_SEM_CORTE, TIPO_COM_SOBRA ou TIPO_DUAS_PAGINAS (None se
        indisponível).
    cortes: os cortes, da esquerda para a direita (0, 1 ou 2).
    motivo: por que ficou indisponível, em português (None se deu certo).
    segundos: quanto a DLL levou.
    """

    tipo: int | None
    cortes: tuple[Corte, ...] = ()
    motivo: str | None = None
    detalhe_tecnico: str | None = None
    segundos: float = 0.0

    @property
    def disponivel(self) -> bool:
        return self.tipo is not None

    @property
    def nome_do_tipo(self) -> str:
        return _NOMES_DOS_TIPOS.get(self.tipo, "?")


def _indisponivel(motivo: str, detalhe: str | None = None) -> Resultado:
    if detalhe:
        _log.warning("dividir do ScanTailor: %s (%s)", motivo, detalhe)
    return Resultado(None, (), motivo, detalhe)


def achar(img: np.ndarray, dpi, modo: int = MODO_AUTOMATICO,
          biblioteca: st_ferramentas.BibliotecaScanTailor | None = None) -> Resultado:
    """Onde o ScanTailor cortaria esta folha, no `modo` pedido.

    img: a folha (cinza 2D, ou colorida BGR como o OpenCV/pdf_io devolve).
    dpi: o DPI da imagem (número ou par). A análise do programa passa a folha
        a 150 DPI (core.pipeline.DPI_ANALISE).
    Nunca levanta exceção (ver o topo)."""
    if modo not in (MODO_AUTOMATICO, MODO_SEM_CORTE, MODO_COM_SOBRA, MODO_DUAS_PAGINAS):
        return _indisponivel("Modo de dividir desconhecido.", f"modo={modo!r}")
    if img is None or img.ndim not in (2, 3) or (img.ndim == 3 and img.shape[2] not in (1, 3)):
        return _indisponivel("A folha não veio no formato esperado.",
                             None if img is None else f"forma {img.shape}")
    try:
        dpi_x, dpi_y = st_ferramentas.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return _indisponivel("O DPI da folha é inválido.", str(erro))
    altura, largura = img.shape[:2]
    recusa = st_ferramentas.motivo_de_recusa(largura, altura, dpi_x, dpi_y,
                                             "o dividir do ScanTailor")
    if recusa:
        return _indisponivel(recusa)

    biblioteca = biblioteca or st_ferramentas.padrao()
    funcao = biblioteca.funcao("st_ferramentas_dividir")
    if funcao is None:
        return _indisponivel(biblioteca.motivo_indisponivel or "O dividir do ScanTailor não abriu.",
                             biblioteca.detalhe_indisponivel)

    if img.ndim == 3 and img.shape[2] == 1:
        img = img[:, :, 0]
    canais = 1 if img.ndim == 2 else 3
    pontos = np.ascontiguousarray(img, dtype=np.uint8)
    tipo = ctypes.c_int(-1)
    quantos = ctypes.c_int(0)
    cortes = (ctypes.c_double * 8)()
    erro = ctypes.create_string_buffer(512)
    inicio = time.perf_counter()
    codigo = funcao(pontos.ctypes.data, largura, altura, int(pontos.strides[0]), canais,
                    dpi_x, dpi_y, int(modo), ctypes.byref(tipo), ctypes.byref(quantos),
                    cortes, erro, len(erro))
    segundos = time.perf_counter() - inicio
    if codigo != st_ferramentas.OK:
        return _indisponivel("O dividir do ScanTailor falhou nesta folha.",
                             f"codigo {codigo}: {erro.value.decode('utf-8', 'replace')}")

    achados = []
    for k in range(max(0, min(2, quantos.value))):
        x1, y1, x2, y2 = cortes[4 * k: 4 * k + 4]
        # As pontas vêm nas bordas de cima e de baixo (em qualquer ordem).
        cima, baixo = (x1, x2) if y1 <= y2 else (x2, x1)
        achados.append(Corte(float(np.clip(cima / largura, 0.0, 1.0)),
                             float(np.clip(baixo / largura, 0.0, 1.0))))
    achados.sort(key=lambda c: c.meio)
    return Resultado(int(tipo.value), tuple(achados), segundos=segundos)


def posicao_da_divisao(resultado: Resultado) -> float | None:
    """A posição (fração da largura) onde a folha é dividida em duas, ou None
    se o ScanTailor achou uma página só.

    O nosso corte é reto (core/dividir.dividir_imagem); a linha do ScanTailor
    pode ser inclinada: fica o MEIO dela (no alto e embaixo, cada página leva
    no máximo metade da inclinação da outra; o quanto, ver Corte.inclinacao)."""
    if not resultado.disponivel or resultado.tipo != TIPO_DUAS_PAGINAS or not resultado.cortes:
        return None
    return resultado.cortes[0].meio


def sobra_da_folha(resultado: Resultado) -> tuple[float, float] | None:
    """(esquerda, direita): a parte da folha que FICA depois do corte da sobra,
    em fração da largura; None se não há sobra a cortar.

    O nosso corte é reto; para a linha inclinada fica a ponta que corta MENOS
    (o corte da sobra nunca entra mais na página do que a linha do ScanTailor).
    Sobra de menos de 0,5% de um lado não conta (é a borda da imagem)."""
    if not resultado.disponivel or resultado.tipo != TIPO_COM_SOBRA or len(resultado.cortes) < 2:
        return None
    esquerdo, direito = resultado.cortes[0], resultado.cortes[-1]
    a = min(esquerdo.x_cima, esquerdo.x_baixo)
    b = max(direito.x_cima, direito.x_baixo)
    a = 0.0 if a < 0.005 else a
    b = 1.0 if b > 0.995 else b
    if b - a < 0.2 or (a == 0.0 and b == 1.0):
        return None
    return (round(a, 6), round(b, 6))
