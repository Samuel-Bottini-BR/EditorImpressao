"""O corte que segue o conteúdo, como o ScanTailor (item 2.5 da Fase 2).

DECISÕES DO SAMUEL QUE ESTE ARQUIVO CUMPRE
    - G8 (05/10/2026): "(a) Trazer como opção 'seguir a moldura / o papel',
      desligada - eu quero pode escolher dentro do programa". É a opção do
      livro Projeto.cortar_pelo_conteudo (DESLIGADA de fábrica: livro já
      começado sai igual). Quem liga é core/pipeline.py.
    - G9 (05/10/2026): "Todas as páginas do tamanho da maior: Sim". É a conta
      do tamanho do livro (tamanho_do_livro), a do ScanTailor.
    - g8-moldura-tinta-fora (13/10/2026): "Só avisa" + "ele avisa e da opção e
      de mudar o corte e mostrar ele alargado com o que foi tirado." O corte
      fica como o ScanTailor achou; tinta_tirada diz o que ficou de fora (o
      aviso) e alargar dá o corte alargado (a opção).
    - g9-pagina-muito-maior (13/10/2026): "O programa deixa essa folha de fora
      sozinho, e avisa" + "precisamos de alternativa do que fazer com ela,
      porque ela precisa ser impressa." A folha muito maior não entra na conta
      do tamanho (muito_maior) e sai no tamanho dela; o que fazer com ela na
      impressão é a pergunta g9-folha-maior-impressao, ainda aberta.
    - Explicação da impressão (14/10/2026): "Na edição - Cada página ocupa a
      folha inteira [...] Não penso em tamanho final, formato nem margem."
      Por isso as margens do ScanTailor (10 mm dos lados, 5 mm em cima e
      embaixo) NÃO entram aqui: a margem de cada lado é só a folga de 1 mm do
      corte já aprovada (core.recortar.FOLGA_MM, conferência 5, 01/10). As
      margens de verdade são da hora de gerar o arquivo para impressão (2.6).

O QUE VEM DO SCANTAILOR E O QUE É NOSSO
    Do ScanTailor Advanced v1.2.1, sem mudança de conta:
      - a caixa do conteúdo: o ContentBoxFinder, pela DLL
        (core.caixas_scantailor), com a busca da página DESLIGADA, que é o de
        fábrica do ScanTailor (a busca da página dentro da borda preta é o
        item 2.13, que espera a pergunta g7-borda-ate-onde);
      - o tamanho do livro: Settings::Impl::computeAggregateHardSizeMMLocked
        (page_layout/Settings.cpp): a maior largura e a maior altura entre as
        páginas "alinhadas com as outras", cada uma = conteúdo + margens;
      - o alargar até o tamanho do livro: Utils::calcSoftMarginsMM
        (page_layout/Utils.cpp) com o alinhamento de fábrica dele
        (Alignment(): VCENTER, HCENTER): a diferença vai metade para cada lado.
      São contas de soma e máximo: trazidas para o Python linha a linha (as
      linhas originais estão citadas em cada função), não pela DLL.
    Nosso (não existe no ScanTailor):
      - a página "muito maior" fica de fora sozinha (no ScanTailor é a pessoa
        que tira, página por página, com "não alinhar com as outras"); a regra
        é LIMITE_DA_MUITO_MAIOR;
      - o que "ficou de fora" e o corte alargado: a conta que o pesquisador
        mostrou ao Samuel na pergunta g8-moldura-tinta-fora (12/10, ramo
        fase2-geometria-perguntas, scripts/passo2_imagens.py,
        alargar_ate_a_tinta), aqui usada sem mudança de regra;
      - caber na imagem: o ScanTailor pinta de branco o que passa da imagem;
        o corte do programa não sai da imagem (pintar é o item 2.14), então o
        corte ANDA para dentro, guardando o tamanho, e só encolhe quando a
        própria imagem é menor que o tamanho do livro (ver _caber).

O QUE É SEGURO MUDAR
    Os textos. LIMITE_DA_MUITO_MAIOR (muda só quais páginas ficam de fora da
    conta do tamanho; nenhuma imagem muda com a opção desligada).

O QUE É ARRISCADO
    - Ligar a busca da página (achar_pagina) aqui: é o 2.13 e depende da g7.
    - MARGEM_MM: muda o corte de toda página dos livros com a opção ligada.
    - Mudar o DPI que vai à DLL: a caixa muda muito com ele (ver
      core/caixas_scantailor.py, "O DPI"; e relatorios/caixa-conteudo-impl/
      ONDE-PAREI.md, "Folha grande", 20/10/2026).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Hashable, Iterable, Mapping

import numpy as np

from core import caixas_scantailor as cs
from core.recortar import FOLGA_MM

# A margem de cada lado, em mm, em volta da caixa do conteúdo: a folga de 1 mm
# do corte comum, aprovada em 01/10 (ver o topo, "Explicação da impressão").
MARGEM_MM = FOLGA_MM

# g9 (nosso): uma página é "muito maior" quando o conteúdo dela passa de
# LIMITE_DA_MUITO_MAIOR vezes a mediana do livro na largura ou na altura.
# Medido em 20/10/2026 (relatorios/caixa-conteudo-impl/): a tabela dobrável do
# Opus Majus (p. 256) tem o conteúdo bem mais largo que o das páginas comuns, e
# nas páginas comuns de um livro a caixa varia menos que isso. Seguro mudar
# (só muda quem fica de fora da conta, e cada uma avisa).
LIMITE_DA_MUITO_MAIOR = 1.25
# Com menos páginas medidas que isto, ninguém fica de fora (não dá para dizer
# o que é "o normal do livro").
PAGINAS_MINIMAS_PARA_A_REGRA = 3

# A conta do "ficou de fora" (a do pesquisador, g8): peça sozinha fora da caixa
# só conta se tiver PECA_MINIMA_MM ou mais nos dois sentidos e for escura como
# tinta (o 5º percentil dela abaixo de ESCURA_COMO_TINTA vezes o tom do papel),
# para mancha clara e risquinho não contarem.
PECA_MINIMA_MM = 1.0
ESCURA_COMO_TINTA = 0.5
PERCENTIL_DO_PAPEL = 60


@dataclass(frozen=True)
class MedidaDoConteudo:
    """A caixa do conteúdo de uma página, como o ScanTailor achou.

    largura, altura: da imagem medida (pontos).
    caixa: (x0, y0, x1, y1) em pontos dessa imagem, SEM folga; None quando a
        página não tem conteúdo ou a conta ficou indisponível.
    tamanho_mm: (largura, altura) do conteúdo em mm, como o ScanTailor guarda
        (é o que entra na conta do tamanho do livro).
    mm_por_ponto: (x, y), pelo DPI que foi dito à DLL; None se indisponível.
    motivo: por que não há caixa (texto para o log; nunca vai para a tela).
    """

    largura: int
    altura: int
    caixa: tuple[float, float, float, float] | None
    tamanho_mm: tuple[float, float] | None
    mm_por_ponto: tuple[float, float] | None
    motivo: str | None = None

    @property
    def disponivel(self) -> bool:
        return self.mm_por_ponto is not None

    @property
    def tem_conteudo(self) -> bool:
        return self.caixa is not None and self.tamanho_mm is not None


@dataclass(frozen=True)
class TamanhoDoLivro:
    """A conta do tamanho do livro (G9, "todas as páginas do tamanho da
    maior"): largura e altura em mm, já com a margem de cada lado, e as
    páginas que ficaram de fora sozinhas por serem muito maiores (g9)."""

    largura_mm: float
    altura_mm: float
    muito_maiores: frozenset = field(default_factory=frozenset)
    paginas: int = 0                     # quantas entraram na conta

    def como_tupla(self) -> tuple[float, float]:
        return (self.largura_mm, self.altura_mm)


def medir(img: np.ndarray, dpi_do_desenho=None, dpi_do_scan=None, *,
          biblioteca=None) -> MedidaDoConteudo:
    """A caixa do conteúdo de `img` (a página já girada, dividida e, no livro
    novo, endireitada), com o DPI das outras ferramentas do ScanTailor
    (core.caixas_scantailor.achar_na_pagina) e a busca da página desligada.
    Nunca levanta exceção: sem a DLL, volta sem caixa e com o motivo."""
    altura, largura = (img.shape[:2] if img is not None and getattr(img, "ndim", 0) >= 2
                       else (0, 0))
    opcoes = {"achar_pagina": False}
    if biblioteca is not None:
        opcoes["biblioteca"] = biblioteca
    r = cs.achar_na_pagina(img, dpi_do_desenho, dpi_do_scan, **opcoes)
    if not r.disponivel or r.dpi is None:
        return MedidaDoConteudo(largura, altura, None, None, None, r.motivo)
    mm = (cs.MILIMETROS_POR_POLEGADA / r.dpi[0], cs.MILIMETROS_POR_POLEGADA / r.dpi[1])
    if not r.tem_conteudo:
        return MedidaDoConteudo(largura, altura, None, None, mm, "a página não tem conteúdo")
    return MedidaDoConteudo(largura, altura, r.conteudo.como_tupla(),
                            r.tamanho_do_conteudo_mm, mm)


def tamanho_duro_mm(tamanho_mm: tuple[float, float]) -> tuple[float, float]:
    """O conteúdo mais a margem dos dois lados: o "hardSize" do ScanTailor
    (Settings::Item::hardWidthMM / hardHeightMM, Settings.cpp linhas 341-347)."""
    return (float(tamanho_mm[0]) + 2.0 * MARGEM_MM, float(tamanho_mm[1]) + 2.0 * MARGEM_MM)


def muito_maiores(tamanhos: Mapping[Hashable, tuple[float, float] | None],
                  limite: float = LIMITE_DA_MUITO_MAIOR) -> frozenset:
    """g9 (nosso): as páginas cujo conteúdo passa de `limite` vezes a mediana
    do livro na largura ou na altura. Páginas sem conteúdo (None) não contam.
    Com menos de PAGINAS_MINIMAS_PARA_A_REGRA páginas medidas: nenhuma."""
    medidas = {k: v for k, v in tamanhos.items() if v is not None}
    if len(medidas) < PAGINAS_MINIMAS_PARA_A_REGRA:
        return frozenset()
    mediana_l = median(float(v[0]) for v in medidas.values())
    mediana_a = median(float(v[1]) for v in medidas.values())
    return frozenset(k for k, v in medidas.items()
                     if float(v[0]) > limite * mediana_l or float(v[1]) > limite * mediana_a)


def tamanho_do_livro(tamanhos: Mapping[Hashable, tuple[float, float] | None], *,
                     sempre_dentro: Iterable[Hashable] = (),
                     sempre_fora: Iterable[Hashable] = ()) -> TamanhoDoLivro | None:
    """A conta do tamanho do livro.

    tamanhos: {página: (largura, altura) do conteúdo em mm, ou None sem
        conteúdo}. A chave é o que quem chama quiser (o programa usa o índice
        da página).
    sempre_dentro: páginas que o Kaique pôs de volta na conta (nunca ficam de
        fora sozinhas). sempre_fora: as que ele tirou (o "não alinhar com as
        outras" do ScanTailor).
    Conta (ScanTailor, Settings.cpp, computeAggregateHardSizeMMLocked, linhas
    607-618): a maior largura e a maior altura "duras" (tamanho_duro_mm) entre
    as páginas que entram; cada uma pode vir de uma página diferente.
    None quando nenhuma página entra."""
    dentro = set(sempre_dentro)
    fora = set(sempre_fora)
    candidatas = {k: v for k, v in tamanhos.items() if v is not None and k not in fora}
    sozinhas = frozenset(k for k in muito_maiores(candidatas) if k not in dentro)
    entram = [tamanho_duro_mm(v) for k, v in candidatas.items() if k not in sozinhas]
    if not entram:
        return None
    return TamanhoDoLivro(max(v[0] for v in entram), max(v[1] for v in entram),
                          sozinhas, len(entram))


def _caber(a: float, b: float, limite: float) -> tuple[float, float]:
    """Põe o trecho [a, b] dentro de [0, limite] guardando o tamanho (anda
    para dentro); se o trecho é maior que o limite, fica o limite inteiro."""
    if b - a >= limite:
        return 0.0, float(limite)
    if a < 0:
        b, a = b - a, 0.0
    if b > limite:
        a, b = a - (b - limite), float(limite)
    return max(0.0, a), min(float(limite), b)


def caixa_do_corte(medida: MedidaDoConteudo,
                   livro: TamanhoDoLivro | None = None) -> tuple[float, float, float, float] | None:
    """O corte desta página em pontos (x0, y0, x1, y1), ou None quando não há
    caixa (aí vale o corte comum).

    1. A caixa do conteúdo mais MARGEM_MM de cada lado (o "hard rect": Utils::
       calcPageRectPhys, extendPolyRectWithMargins com as margens duras).
    2. Com o tamanho do livro (`livro`, já sem esta página se ela ficou de
       fora): alarga até ele, metade da diferença para cada lado (Utils::
       calcSoftMarginsMM, linhas 74-176, com Alignment::HCENTER e VCENTER, o
       de fábrica). Sem diferença (esta é a maior), não alarga.
    3. Cabe na imagem (_caber): anda para dentro guardando o tamanho."""
    if not medida.tem_conteudo or medida.mm_por_ponto is None:
        return None
    mx, my = medida.mm_por_ponto
    x0, y0, x1, y1 = medida.caixa
    x0, x1 = x0 - MARGEM_MM / mx, x1 + MARGEM_MM / mx
    y0, y1 = y0 - MARGEM_MM / my, y1 + MARGEM_MM / my
    if livro is not None:
        duro_l, duro_a = tamanho_duro_mm(medida.tamanho_mm)
        delta_l = livro.largura_mm - duro_l
        delta_a = livro.altura_mm - duro_a
        if delta_l > 0:
            x0, x1 = x0 - 0.5 * delta_l / mx, x1 + 0.5 * delta_l / mx
        if delta_a > 0:
            y0, y1 = y0 - 0.5 * delta_a / my, y1 + 0.5 * delta_a / my
    x0, x1 = _caber(x0, x1, medida.largura)
    y0, y1 = _caber(y0, y1, medida.altura)
    return (x0, y0, x1, y1)


def em_fracao(caixa: tuple[float, float, float, float], largura: int,
              altura: int) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) em pontos -> (x, y, largura, altura) em fração da
    imagem, o formato de ConfigPagina.recorte e de Recorte.tupla."""
    x0, y0, x1, y1 = caixa
    return (x0 / largura, y0 / altura, (x1 - x0) / largura, (y1 - y0) / altura)


def de_fracao(recorte, largura: int, altura: int) -> tuple[float, float, float, float]:
    """O contrário de em_fracao."""
    x, y, w, h = (float(v) for v in recorte)
    return (x * largura, y * altura, (x + w) * largura, (y + h) * altura)


def tinta_tirada(corte: tuple[float, float, float, float], pecas, cinza: np.ndarray,
                 mm_por_ponto: tuple[float, float]) -> list[tuple[float, float, float, float]]:
    """O que o corte deixou de fora (o aviso da g8-moldura-tinta-fora): as
    peças de tinta, em pontos (x0, y0, x1, y1).

    corte: o corte em pontos de `cinza` (a página medida, em cinza).
    pecas: as peças de tinta do corte comum (core.recortar.Recorte.pecas: em
        fração da página, uma por linha x0, y0, x1, y1, risco; sem as que
        encostam na beirada da folha, que são fundo de scanner ou folha
        vizinha). None ou vazio: nada.
    A regra é a do pesquisador (alargar_ate_a_tinta, 12/10), sem mudança:
      - risco comprido e fino não conta;
      - peça que o corte atravessa conta (a barra de uma moldura);
      - peça inteira de fora conta só se estiver "na coluna" do corte (o meio
        dela entre a esquerda e a direita do corte: o número da página no pé,
        o reclamo), tiver PECA_MINIMA_MM ou mais nos dois sentidos e for
        escura como tinta (para mancha clara e risquinho não contarem)."""
    if pecas is None or len(pecas) == 0:
        return []
    altura, largura = cinza.shape[:2]
    x0, y0, x1, y1 = corte
    papel = float(np.percentile(cinza, PERCENTIL_DO_PAPEL))
    minimo = PECA_MINIMA_MM / min(mm_por_ponto)
    tiradas = []
    for p in np.asarray(pecas, dtype=np.float64):
        if p[4] > 0:
            continue                                         # risco comprido e fino
        px0, py0, px1, py1 = p[0] * largura, p[1] * altura, p[2] * largura, p[3] * altura
        if px0 >= x0 and py0 >= y0 and px1 <= x1 and py1 <= y1:
            continue                                         # inteira dentro
        toca = not (px1 < x0 or px0 > x1 or py1 < y0 or py0 > y1)
        if not toca:
            na_coluna = (x0 <= (px0 + px1) / 2 <= x1
                         and min(px1 - px0, py1 - py0) >= minimo)
            if not na_coluna:
                continue
            pedaco = cinza[int(py0):int(py1) + 1, int(px0):int(px1) + 1]
            if pedaco.size == 0 or float(np.percentile(pedaco, 5)) >= ESCURA_COMO_TINTA * papel:
                continue
        tiradas.append((px0, py0, px1, py1))
    return tiradas


def alargar(corte: tuple[float, float, float, float], tiradas, mm_por_ponto: tuple[float, float],
            largura: int, altura: int) -> tuple[float, float, float, float]:
    """O corte alargado até caber o que ficou de fora (a opção da g8: "mostrar
    ele alargado com o que foi tirado"), com MARGEM_MM em volta de cada peça,
    sem passar da imagem. Sem nada tirado, devolve o próprio corte."""
    x0, y0, x1, y1 = corte
    mx, my = mm_por_ponto
    for px0, py0, px1, py1 in tiradas:
        x0, y0 = min(x0, px0 - MARGEM_MM / mx), min(y0, py0 - MARGEM_MM / my)
        x1, y1 = max(x1, px1 + MARGEM_MM / mx), max(y1, py1 + MARGEM_MM / my)
    return (max(0.0, x0), max(0.0, y0), min(float(largura), x1), min(float(altura), y1))
