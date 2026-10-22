"""Item 2.4: margens iguais em todas as páginas e o alinhamento, igual ao ScanTailor.

O QUE FAZ
    É a etapa "Margens" (page_layout) do ScanTailor Advanced v1.2.1, com as
    contas de `src/core/filters/page_layout/Utils.cpp` e `Settings.cpp`
    trazidas para Python (não há imagem a desenhar em C: são contas de
    milímetros; a colagem na folha branca é uma cópia de matriz):

    1. Cada página tem o seu CONTEÚDO (no nosso programa, a página já cortada e
       endireitada, como sai do preparo) com um tamanho em mm.
    2. Em volta dele vão as MARGENS FIXAS ("hard margins"), de fábrica as do
       ScanTailor: 10 mm à esquerda e à direita, 5 mm em cima e embaixo
       (`DefaultParams::PageLayoutParams()`: `m_hardMargins(10, 5, 10, 5)`).
       Conteúdo + margens fixas = o "tamanho duro" da página
       (`Settings::Item::hardWidthMM/hardHeightMM`).
    3. O TAMANHO DO LIVRO é a maior largura e a maior altura entre os tamanhos
       duros das páginas que acompanham as outras ("Match size with other
       pages"; `computeAggregateHardSizeMMLocked`).
    4. Cada página cresce até o tamanho do livro; a sobra vira MARGEM SUAVE
       ("soft margins"), repartida pelo ALINHAMENTO (`calcSoftMarginsMM`). De
       fábrica o ScanTailor centraliza (`Alignment()`: VCENTER, HCENTER).

    Resultado: todas as páginas saem do mesmo tamanho, com o conteúdo no mesmo
    lugar - é o "Margens iguais em todas as folhas / centralizar o texto" (R3,
    12/09/2026) e o "Todas as páginas do tamanho da maior: Sim" (G9b,
    05/10/2026).

    Decisão `g9-pagina-muito-maior` (Samuel, 14/10/2026): "O programa deixa essa
    folha de fora sozinho, e avisa" - a página muito maior que as outras (a
    tabela dobrável do Opus Majus) fica fora da conta do tamanho do livro
    (no ScanTailor seria desmarcar o "Match size" dela) e mantém o próprio
    tamanho duro. Quem decide "muito maior": `paginas_muito_maiores`, com o
    limiar LIMITE_DA_FOLHA_MAIOR (decisão desta implementação, dentro da alçada
    de limiar do CLAUDE.md §6).

DESLIGADO DE FÁBRICA (regra da Fase 2, 13/10/2026): `Projeto.margens_iguais`
    vem False; desligado, o processar não chama nada daqui e o PDF sai idêntico.

O QUE NÃO VEIO DO SCANTAILOR (de propósito)
    - "Auto margins" (medir a margem que a página já tinha): desligado de
      fábrica no ScanTailor (`m_autoMargins(false)`); fica para depois.
    - O alinhamento "Original" (HORIGINAL/VORIGINAL) está aqui: usa onde o
      conteúdo estava na página (o centro do recorte), igual à conta dele.

SEGURO MUDAR: os textos da tela; LIMITE_DA_FOLHA_MAIOR (é limiar).
ARRISCADO MUDAR: `margens_suaves_mm` (é a conta do ScanTailor linha a linha:
    conferida por tests/test_margens_scantailor.py); os códigos de alinhamento
    (vão para o projeto.json).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Iterable, Sequence

import numpy as np

MM_POR_POLEGADA = 25.4


@dataclass(frozen=True)
class Margens:
    """Quatro margens em milímetros (a ordem do ScanTailor: Margins(left,
    top, right, bottom))."""

    esquerda: float = 0.0
    cima: float = 0.0
    direita: float = 0.0
    baixo: float = 0.0

    @staticmethod
    def de(valor) -> "Margens":
        """De uma lista/tupla (esquerda, cima, direita, baixo), como vem do
        projeto.json; valor estranho volta às de fábrica."""
        if isinstance(valor, Margens):
            return valor
        try:
            e, c, d, b = (max(0.0, float(v)) for v in valor)
            return Margens(e, c, d, b)
        except (TypeError, ValueError):
            return MARGENS_DE_FABRICA

    def como_lista(self) -> list[float]:
        return [self.esquerda, self.cima, self.direita, self.baixo]


# DefaultParams::PageLayoutParams(): m_hardMargins(10, 5, 10, 5)
MARGENS_DE_FABRICA = Margens(10.0, 5.0, 10.0, 5.0)

# Alignment.h: enum Vertical { TOP, VCENTER, BOTTOM, VAUTO, VORIGINAL };
#              enum Horizontal { LEFT, HCENTER, RIGHT, HAUTO, HORIGINAL };
CIMA, MEIO, BAIXO, AUTOMATICO, ORIGINAL = "cima", "meio", "baixo", "automatico", "original"
ESQUERDA, DIREITA = "esquerda", "direita"
VERTICAIS = (CIMA, MEIO, BAIXO, AUTOMATICO, ORIGINAL)
HORIZONTAIS = (ESQUERDA, MEIO, DIREITA, AUTOMATICO, ORIGINAL)
# Alignment(): m_vertical(VCENTER), m_horizontal(HCENTER)
ALINHAMENTO_DE_FABRICA = (MEIO, MEIO)          # (vertical, horizontal)

NOMES_VERTICAIS = {CIMA: "em cima", MEIO: "no meio", BAIXO: "embaixo",
                   AUTOMATICO: "o programa escolhe", ORIGINAL: "onde estava na página"}
NOMES_HORIZONTAIS = {ESQUERDA: "à esquerda", MEIO: "no meio", DIREITA: "à direita",
                     AUTOMATICO: "o programa escolhe", ORIGINAL: "onde estava na página"}

# g9-pagina-muito-maior: página com largura OU altura (tamanho duro) acima de
# 1,25 x a mediana do livro fica fora da conta. A tabela do Opus Majus tem
# 20,8 cm de largura contra 14,6 cm das comuns (1,42 x).
LIMITE_DA_FOLHA_MAIOR = 1.25

AVISO_DA_FOLHA_MAIOR = ("Esta página é bem maior que as outras e ficou fora da conta das "
                        "margens iguais: sai do tamanho dela.")


def alinhamento_valido(valor) -> tuple[str, str]:
    """(vertical, horizontal) válido; o que vier estranho vira o de fábrica."""
    try:
        vertical, horizontal = valor
    except (TypeError, ValueError):
        return ALINHAMENTO_DE_FABRICA
    if vertical not in VERTICAIS:
        vertical = ALINHAMENTO_DE_FABRICA[0]
    if horizontal not in HORIZONTAIS:
        horizontal = ALINHAMENTO_DE_FABRICA[1]
    return vertical, horizontal


def px_para_mm(px: float, dpi: float) -> float:
    return float(px) / float(dpi) * MM_POR_POLEGADA


def mm_para_px(mm: float, dpi: float) -> float:
    return float(mm) / MM_POR_POLEGADA * float(dpi)


def tamanho_duro_mm(conteudo_mm: tuple[float, float], margens: Margens) -> tuple[float, float]:
    """Settings::Item::hardWidthMM / hardHeightMM: conteúdo + margens fixas."""
    largura, altura = conteudo_mm
    return (largura + margens.esquerda + margens.direita,
            altura + margens.cima + margens.baixo)


def tamanho_do_livro_mm(tamanhos_duros: Iterable[tuple[float, float] | None]) -> tuple[float, float]:
    """computeAggregateHardSizeMMLocked: a maior largura e a maior altura das
    páginas que acompanham as outras. None (página fora da conta: alignment
    nulo no ScanTailor, influenceHard*MM = 0) não conta. Sem nenhuma: (0, 0)."""
    largura = altura = 0.0
    for tamanho in tamanhos_duros:
        if tamanho is None:
            continue
        largura = max(largura, float(tamanho[0]))
        altura = max(altura, float(tamanho[1]))
    return largura, altura


def paginas_muito_maiores(tamanhos_duros: Sequence[tuple[float, float]],
                          limite: float = LIMITE_DA_FOLHA_MAIOR) -> set[int]:
    """Os índices das páginas muito maiores que as outras (g9-pagina-muito-maior).
    Com menos de 3 páginas não há "as outras" para comparar: nenhuma sai."""
    if len(tamanhos_duros) < 3:
        return set()
    mediana_l = median(t[0] for t in tamanhos_duros)
    mediana_a = median(t[1] for t in tamanhos_duros)
    return {i for i, (largura, altura) in enumerate(tamanhos_duros)
            if largura > limite * mediana_l or altura > limite * mediana_a}


def margens_suaves_mm(tamanho_duro: tuple[float, float],
                      tamanho_do_livro: tuple[float, float],
                      alinhamento: tuple[str, str] | None,
                      centro_do_conteudo: tuple[float, float] | None = None) -> Margens:
    """Utils::calcSoftMarginsMM, linha a linha.

    alinhamento None = a página não acompanha as outras (alignment.isNull()):
    nenhuma margem suave. centro_do_conteudo: o centro do conteúdo em fração
    da página ANTES do corte (x, y) - é o que a conta do ScanTailor tira de
    contentRect/pageRect (contentRectCenterXInMm / pageRectSizeMm.width());
    None = não se sabe (a conta dele então começa com toda a sobra à direita
    e embaixo, como quando contentRect está vazio).
    """
    if alinhamento is None:
        return Margens()
    vertical, horizontal = alinhamento_valido(alinhamento)

    topo = baixo = esquerda = direita = 0.0
    delta_largura = tamanho_do_livro[0] - tamanho_duro[0]
    delta_altura = tamanho_do_livro[1] - tamanho_duro[1]

    agg_esquerda = 0.0
    agg_direita = delta_largura
    agg_topo = 0.0
    agg_baixo = delta_altura

    if centro_do_conteudo is not None:
        cx, cy = centro_do_conteudo
        if delta_largura > 0.0:
            agg_esquerda = cx * tamanho_do_livro[0] - tamanho_duro[0] / 2
            agg_esquerda = min(max(0.0, agg_esquerda), delta_largura)      # qBound
            agg_direita = delta_largura - agg_esquerda
        if delta_altura > 0.0:
            agg_topo = cy * tamanho_do_livro[1] - tamanho_duro[1] / 2
            agg_topo = min(max(0.0, agg_topo), delta_altura)
            agg_baixo = delta_altura - agg_topo

    if delta_largura > 0.0:
        if horizontal == AUTOMATICO:
            if 3 * agg_esquerda < agg_direita:
                horizontal = ESQUERDA
            elif 3 * agg_direita < agg_esquerda:
                horizontal = DIREITA
            else:
                horizontal = MEIO
        if horizontal == ESQUERDA:
            direita = delta_largura
        elif horizontal == MEIO:
            esquerda = direita = 0.5 * delta_largura
        elif horizontal == DIREITA:
            esquerda = delta_largura
        else:                                  # ORIGINAL (default: no switch)
            esquerda = agg_esquerda
            direita = agg_direita

    if delta_altura > 0.0:
        if vertical == AUTOMATICO:
            if 3 * agg_topo < agg_baixo:
                vertical = CIMA
            elif 3 * agg_baixo < agg_topo:
                vertical = BAIXO
            else:
                vertical = MEIO
        if vertical == CIMA:
            baixo = delta_altura
        elif vertical == MEIO:
            topo = baixo = 0.5 * delta_altura
        elif vertical == BAIXO:
            topo = delta_altura
        else:
            topo = agg_topo
            baixo = agg_baixo

    return Margens(esquerda, topo, direita, baixo)


def tamanho_final_px(conteudo_px: tuple[int, int], dpi: float, margens: Margens,
                     tamanho_do_livro: tuple[float, float] | None) -> tuple[int, int]:
    """O tamanho em pontos da página pronta. Acompanhando as outras, é o do
    livro (todas saem exatamente do mesmo tamanho em pontos); fora da conta,
    o tamanho duro dela."""
    largura_px, altura_px = conteudo_px
    if tamanho_do_livro is not None and tamanho_do_livro[0] > 0 and tamanho_do_livro[1] > 0:
        alvo_l = round(mm_para_px(tamanho_do_livro[0], dpi))
        alvo_a = round(mm_para_px(tamanho_do_livro[1], dpi))
    else:
        alvo_l = round(largura_px + mm_para_px(margens.esquerda + margens.direita, dpi))
        alvo_a = round(altura_px + mm_para_px(margens.cima + margens.baixo, dpi))
    return max(alvo_l, largura_px), max(alvo_a, altura_px)


def compor_com_margens(img: np.ndarray, dpi: float, margens: Margens,
                       suaves: Margens, tamanho_do_livro: tuple[float, float] | None) -> np.ndarray:
    """Cola `img` (o conteúdo) numa folha branca com as margens fixas e as
    suaves em volta. É o que o ScanTailor faz na saída: a página fica do
    tamanho de calcPageRectPhys e o que está fora do conteúdo é branco.
    `tamanho_do_livro` None = página fora da conta (fica do tamanho duro)."""
    altura_px, largura_px = img.shape[:2]
    final_l, final_a = tamanho_final_px((largura_px, altura_px), dpi, margens, tamanho_do_livro)
    x0 = round(mm_para_px(margens.esquerda + suaves.esquerda, dpi))
    y0 = round(mm_para_px(margens.cima + suaves.cima, dpi))
    # o arredondamento nunca empurra o conteúdo para fora da folha
    x0 = min(max(0, x0), final_l - largura_px)
    y0 = min(max(0, y0), final_a - altura_px)
    if img.ndim == 2:
        folha = np.full((final_a, final_l), 255, dtype=img.dtype)
    else:
        folha = np.full((final_a, final_l, img.shape[2]), 255, dtype=img.dtype)
    folha[y0:y0 + altura_px, x0:x0 + largura_px] = img
    return folha


@dataclass
class ContaDoLivro:
    """O que a primeira passada do processar mede, para a segunda usar: o
    tamanho do livro e quais páginas ficam fora da conta. Só números (dois
    por página): nenhuma imagem fica guardada (regra "uma página por vez")."""

    margens: Margens
    alinhamento: tuple[str, str]
    tamanho_do_livro: tuple[float, float]
    fora_da_conta: set[int]                  # posição na lista de páginas ativas
    centros: list = field(default_factory=list)   # centro do conteúdo de cada uma

    def margens_da_pagina(self, posicao: int, conteudo_px: tuple[int, int], dpi: float,
                          centro_do_conteudo: tuple[float, float] | None) -> tuple[Margens, tuple | None]:
        """(margens suaves, tamanho do livro ou None) da página na `posicao`."""
        if posicao in self.fora_da_conta:
            return Margens(), None
        duro = tamanho_duro_mm((px_para_mm(conteudo_px[0], dpi), px_para_mm(conteudo_px[1], dpi)),
                               self.margens)
        suaves = margens_suaves_mm(duro, self.tamanho_do_livro, self.alinhamento,
                                   centro_do_conteudo)
        return suaves, self.tamanho_do_livro


def montar_a_conta(conteudos_px: Sequence[tuple[int, int]], dpi: float, margens: Margens,
                   alinhamento: tuple[str, str]) -> ContaDoLivro:
    """Da lista dos tamanhos de conteúdo (em pontos, na ordem das páginas
    ativas), a conta do livro: tamanho duro de cada uma, as muito maiores
    fora, e o tamanho do livro com as que ficaram."""
    duros = [tamanho_duro_mm((px_para_mm(l, dpi), px_para_mm(a, dpi)), margens)
             for l, a in conteudos_px]
    fora = paginas_muito_maiores(duros)
    livro = tamanho_do_livro_mm(None if i in fora else d for i, d in enumerate(duros))
    return ContaDoLivro(margens, alinhamento_valido(alinhamento), livro, fora)
