"""A caixa da página e a caixa do conteúdo, com o código do ScanTailor Advanced
(itens 2.13 e 2.5 da Fase 2; base para o 2.4 e o 2.6).

O QUE FAZ
    Chama a função st_ferramentas_caixas da DLL comum (core/st_ferramentas.py):
    a etapa "Select Content" do ScanTailor Advanced v1.2.1, com o código dele
    sem mudança (terceiros/scantailor-advanced/src/core/filters/select_content/
    PageFinder.cpp e ContentBoxFinder.cpp; a cola está em
    terceiros/scantailor-advanced/ligacao-ferramentas/caixas.cpp):
      - a caixa da PÁGINA: a folha sem a faixa preta do scanner (item 2.13);
      - a caixa do CONTEÚDO: o retângulo do texto e das figuras, procurado
        DENTRO da caixa da página (item 2.5).
    Nada aqui reescreve a conta do ScanTailor: só leva a página até a DLL e
    devolve as caixas em pontos da imagem e em milímetros, com o tempo gasto.

NÃO ESTÁ LIGADO AO PROGRAMA (12/10/2026)
    Ninguém chama este módulo: nem core/pipeline.py, nem a tela. O Samuel
    decidiu (conferência 9, 05/10/2026, G7 (a) e G8 (a)) que as duas contas
    entram como opção DESLIGADA de fábrica, e como ligam depende das seis
    perguntas de 12/10 (relatorios/conferir/geometria-g7-g10-2026-10-12, no
    ramo fase2-geometria-perguntas), ainda sem resposta. Aqui está só a base,
    que serve para qualquer resposta.

O QUE O PESQUISADOR MEDIU (12/10/2026) E QUE QUEM LIGAR PRECISA SABER
    - A caixa da página sozinha só tira faixa preta que cobre 95% do lado da
      folha, reta. No Siebmacher (folha torta, preto à direita) ela quase não
      corta; quem tira o preto ali é a caixa do conteúdo. Por isso as duas
      vêm juntas, numa chamada só.
    - A caixa do conteúdo erra em páginas conhecidas: deixa de fora a barra
      dourada da esquerda na Horas 14 e o número "[ 115 ]" sozinho no pé do
      Opus Majus 137. NUNCA cortar por ela sem a pessoa ver (a decisão do
      Samuel é "o programa sugere, o Kaique aceita").
    - O resultado MUDA COM O DPI (ver "O DPI").

O DPI (é o que mais muda o resultado)
    As duas contas levam a página a 150 DPI pelo DPI que se diz. Na Horas 13
    (1024 x 1453 pontos; o PDF diz 72 DPI, que não é a resolução de verdade),
    com 72 a caixa do conteúdo fica quase na folha inteira; com 150, fica por
    dentro da moldura. E com DPI baixo demais a página é AMPLIADA: a conta
    fica várias vezes mais lenta (6 a 8 s por página no Horas a 72 DPI).
    achar() usa o DPI que receber, sem mexer. achar_na_pagina() faz a MESMA
    conta do limpar pontinhos, do endireitar e do detector de gravura
    (pontinhos_scantailor.dpi_para_os_pontinhos): os quatro do ScanTailor
    veem a página do mesmo tamanho (a Horas 13 vai a ~138 DPI).
    Os milímetros devolvidos são pontos x 25,4 / DPI dito: se o DPI dito não
    é o de verdade, os milímetros também não são.

"CLARO NO ESCURO"
    O ScanTailor decide sozinho se a página é texto claro em fundo escuro e,
    se achar que sim, faz a conta na página invertida (de fábrica, ligado).
    claro_no_escuro=None deixa o ScanTailor decidir (o de fábrica dele, e o
    que o endireitar do programa já faz); False trata sempre como preto no
    branco (o que o programa de teste do pesquisador fez, e o que as imagens
    das perguntas de 12/10 mostram); True força a página invertida.
    O resultado diz o que foi usado (preto_no_branco). Medido em 12/10/2026:
    nas 37 páginas que o pesquisador mediu (gabarito e páginas com borda
    preta), o ScanTailor decidiu "preto no branco" em todas, então None e
    False dão as mesmas caixas nelas (o teste confere).

SE A DLL FALTAR OU FALHAR
    Nada levanta exceção: o resultado volta com `disponivel` False e o motivo
    em português; o detalhe técnico vai para o log. Quem chama decide.

O QUE É SEGURO MUDAR
    Os textos das mensagens. Os valores de fábrica de achar() (achar_pagina,
    ajustar_cantos, claro_no_escuro) ENQUANTO ninguém chama o módulo; depois
    de ligado, mudar um deles muda o corte sugerido de todos os livros.

O QUE É ARRISCADO
    - O DPI que se passa (ver acima). Trocar a conta de achar_na_pagina() faz
      as ferramentas do ScanTailor deixarem de ver a mesma página.
    - PONTOS_MAXIMOS_A_150: é a trava de memória (ver o comentário dela).
    - A ordem dos números das caixas (x0, y0, x1, y1) e a dos argumentos da
      função em C: o ctypes não confere nada (core/st_ferramentas.ASSINATURAS).
    - Usar `conteudo_bruto` para cortar: ele pode passar da caixa da página
      (ver caixas.cpp, "O que não é óbvio no código original"). O que vale é
      `conteudo`.
"""

from __future__ import annotations

import ctypes
import logging
import time
from dataclasses import dataclass

import numpy as np

from core import st_ferramentas

_log = logging.getLogger(__name__)

# A tolerância de fábrica do ScanTailor para o tamanho esperado da página
# (select_content::Settings, m_pageDetectionTolerance(0.1)).
TOLERANCIA_PADRAO = 0.1

# TRAVA DE MEMÓRIA. As duas contas trabalham na página levada a 150 DPI pelo
# DPI que se diz. Uma página comum (A4) tem 2,2 milhões de pontos a 150 DPI;
# as maiores do acervo (Antiphon, 46 x 63 cm) têm 10 milhões. Com um DPI
# errado para baixo, a página é ampliada sem limite (3000 x 4000 pontos ditos
# a 30 DPI virariam 300 milhões de pontos) e a memória acaba. Acima deste
# tamanho a página é recusada com mensagem, antes de ir à DLL. Medido em
# 12/10/2026, uma página por processo (relatorios/caixa-conteudo-impl/
# scripts/medir_memoria.py, dados/memoria.json): a conta pede cerca de 20 MB
# por milhão de pontos a 150 DPI (10,3 milhões = 200 MB a mais; 14,8 milhões =
# 295 MB) e cerca de 0,3 a 0,5 s por milhão. 16 milhões (uma folha de uns
# 57 x 79 cm) = uns 320 MB e 5 a 8 s. Seguro baixar (a página grande passa a
# ser recusada com mensagem). Arriscado subir sem medir de novo.
PONTOS_MAXIMOS_A_150 = 16_000_000

MILIMETROS_POR_POLEGADA = 25.4


@dataclass(frozen=True)
class Caixa:
    """Um retângulo: x0, y0 (canto de cima à esquerda) e x1, y1 (a beirada de
    fora, à direita e embaixo; largura = x1 - x0). A unidade é a de quem
    criou: pontos da imagem ou milímetros."""

    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def largura(self) -> float:
        return self.x1 - self.x0

    @property
    def altura(self) -> float:
        return self.y1 - self.y0

    def como_tupla(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)

    def em_mm(self, dpi_x: float, dpi_y: float | None = None) -> "Caixa":
        """A mesma caixa em milímetros, medida do canto de cima à esquerda da
        imagem, para uma imagem a `dpi_x` por `dpi_y` pontos por polegada."""
        dpi_y = dpi_x if dpi_y is None else dpi_y
        fx = MILIMETROS_POR_POLEGADA / float(dpi_x)
        fy = MILIMETROS_POR_POLEGADA / float(dpi_y)
        return Caixa(self.x0 * fx, self.y0 * fy, self.x1 * fx, self.y1 * fy)


@dataclass(frozen=True)
class Caixas:
    """O que o ScanTailor achou numa página.

    pagina: a caixa da página, em pontos da imagem. Com achar_pagina
        desligado é a folha inteira. None se indisponível.
    conteudo: a caixa do conteúdo, em pontos, já cortada pela caixa da página
        (o que o ScanTailor guarda). None quando a página não tem conteudo
        (em branco) ou se indisponível.
    conteudo_bruto: o que o achador devolveu ANTES do corte pela caixa da
        página (só para conferência; pode passar da página).
    pagina_mm, conteudo_mm: as mesmas caixas em milímetros, medidas do canto
        de cima à esquerda da imagem (pontos x 25,4 / DPI dito).
    tamanho_do_conteudo_mm: (largura, altura) do conteúdo em mm como o
        ScanTailor calcula e guarda (PhysSizeCalc; é o número que as margens
        do item 2.4 usam). Difere do conteudo_mm só na quarta casa (o
        ScanTailor arredonda os pontos por metro). None sem conteúdo.
    preto_no_branco: False quando a conta foi feita na página invertida.
    dpi: (x, y) ditos à DLL.
    segundos: o tempo todo da chamada; segundos_do_preparo (cinza, "claro no
        escuro"), segundos_da_pagina e segundos_do_conteudo: as partes,
        medidas dentro da DLL.
    motivo, detalhe_tecnico: por que ficou indisponível (o primeiro para a
        tela, em português; o segundo para o erros.log).
    """

    pagina: Caixa | None
    conteudo: Caixa | None = None
    conteudo_bruto: Caixa | None = None
    pagina_mm: Caixa | None = None
    conteudo_mm: Caixa | None = None
    tamanho_do_conteudo_mm: tuple[float, float] | None = None
    preto_no_branco: bool = True
    dpi: tuple[int, int] | None = None
    segundos: float = 0.0
    segundos_do_preparo: float = 0.0
    segundos_da_pagina: float = 0.0
    segundos_do_conteudo: float = 0.0
    motivo: str | None = None
    detalhe_tecnico: str | None = None

    @property
    def disponivel(self) -> bool:
        """A DLL respondeu? (página em branco também é resposta.)"""
        return self.pagina is not None

    @property
    def tem_conteudo(self) -> bool:
        return self.conteudo is not None


def _indisponivel(motivo: str, detalhe: str | None = None) -> Caixas:
    if detalhe:
        _log.warning("caixas do ScanTailor: %s (%s)", motivo, detalhe)
    return Caixas(None, motivo=motivo, detalhe_tecnico=detalhe)


def pontos_a_150(largura: int, altura: int, dpi_x: int, dpi_y: int) -> float:
    """Quantos pontos a página tem depois de levada a 150 DPI (o tamanho em
    que o ScanTailor faz as duas contas)."""
    return (largura * 150.0 / dpi_x) * (altura * 150.0 / dpi_y)


def achar(img: np.ndarray, dpi=None, *, achar_pagina: bool = True, ajustar_cantos: bool = False,
          achar_conteudo: bool = True, tamanho_esperado_mm: tuple[float, float] | None = None,
          tolerancia: float = TOLERANCIA_PADRAO, claro_no_escuro: bool | None = None,
          biblioteca: st_ferramentas.BibliotecaScanTailor | None = None) -> Caixas:
    """A caixa da página e a caixa do conteúdo que o ScanTailor acharia.

    img: a página (cinza 2D, ou colorida BGR como o OpenCV/pdf_io devolve), JÁ
        girada de 90 em 90, dividida e endireitada (no ScanTailor esta etapa
        vem depois do endireitar). As caixas saem em pontos desta imagem.
    dpi: o DPI a dizer à DLL (número ou par). É o que mais muda o resultado:
        ver "O DPI" no topo. None: supõe 10 polegadas de altura (como o
        limpar pontinhos e o endireitar).
    achar_pagina: True procura a página dentro da faixa preta do scanner
        (PageFinder, item 2.13); False, a "página" é a folha inteira (o de
        fábrica do ScanTailor). Aqui o padrão é True porque a função existe
        para dar as duas caixas; quem ligar ao programa decide.
    ajustar_cantos: o "Fine Tune Page Corners" do ScanTailor (só com
        achar_pagina). Medido pelo pesquisador: no Siebmacher 7 corta o
        enfeite de cima da moldura. De fábrica, desligado.
    achar_conteudo: True procura o conteúdo (ContentBoxFinder, item 2.5);
        False, o "conteúdo" é a própria caixa da página.
    tamanho_esperado_mm: (largura, altura) esperadas da página, em mm, para o
        PageFinder escolher entre cinco jeitos de preto e branco o que chega
        mais perto; None = sem tamanho esperado (o de fábrica).
    tolerancia: de 0 a 1; só vale com tamanho_esperado_mm e ajustar_cantos.
    claro_no_escuro: None = o ScanTailor decide; False = preto no branco;
        True = página invertida. Ver o topo.
    Nunca levanta exceção (ver o topo)."""
    if img is None or img.ndim not in (2, 3) or (img.ndim == 3 and img.shape[2] not in (1, 3, 4)):
        return _indisponivel("A página não veio no formato esperado.",
                             None if img is None else f"forma {img.shape}")
    altura, largura = img.shape[:2]
    if dpi is None:
        from core.pontinhos_scantailor import dpi_pela_altura

        dpi = dpi_pela_altura(altura)
    try:
        dpi_x, dpi_y = st_ferramentas.dpi_inteiro(dpi)
    except (TypeError, ValueError) as erro:
        return _indisponivel("O DPI da página é inválido.", str(erro))
    nome = "a caixa do conteúdo do ScanTailor"
    recusa = st_ferramentas.motivo_de_recusa(largura, altura, dpi_x, dpi_y, nome)
    if recusa:
        return _indisponivel(recusa)
    if pontos_a_150(largura, altura, dpi_x, dpi_y) > PONTOS_MAXIMOS_A_150:
        return _indisponivel(f"A página é grande demais para {nome} (com o DPI informado).",
                             f"{largura} x {altura} pontos a {dpi_x} x {dpi_y} DPI")
    try:
        if tamanho_esperado_mm is None:
            esperada_l = esperada_a = 0.0
        else:
            esperada_l, esperada_a = (float(v) for v in tamanho_esperado_mm)
        tolerancia = float(tolerancia)
    except (TypeError, ValueError) as erro:
        return _indisponivel("O tamanho esperado da página é inválido.", str(erro))
    if not (esperada_l >= 0.0 and esperada_a >= 0.0 and 0.0 <= tolerancia <= 1.0):
        return _indisponivel("O tamanho esperado da página é inválido.",
                             f"{tamanho_esperado_mm!r}, tolerância {tolerancia!r}")

    biblioteca = biblioteca or st_ferramentas.padrao()
    funcao = biblioteca.funcao("st_ferramentas_caixas")
    if funcao is None:
        return _indisponivel(biblioteca.motivo_indisponivel or "As caixas do ScanTailor não abriram.",
                             biblioteca.detalhe_indisponivel)

    if img.ndim == 3 and img.shape[2] == 1:
        img = img[:, :, 0]
    elif img.ndim == 3 and img.shape[2] == 4:
        img = img[:, :, :3]
    canais = 1 if img.ndim == 2 else 3
    pontos = np.ascontiguousarray(img, dtype=np.uint8)
    pagina = (ctypes.c_double * 4)()
    conteudo = (ctypes.c_double * 4)()
    bruto = (ctypes.c_double * 4)()
    tamanho_mm = (ctypes.c_double * 2)()
    achou = ctypes.c_int(0)
    preto_no_branco = ctypes.c_int(1)
    ms = (ctypes.c_double * 3)()
    erro = ctypes.create_string_buffer(512)
    modo_claro = -1 if claro_no_escuro is None else (1 if claro_no_escuro else 0)
    inicio = time.perf_counter()
    codigo = funcao(pontos.ctypes.data, largura, altura, int(pontos.strides[0]), canais,
                    dpi_x, dpi_y, 1 if achar_pagina else 0, 1 if ajustar_cantos else 0,
                    esperada_l, esperada_a, tolerancia, 1 if achar_conteudo else 0, modo_claro,
                    pagina, conteudo, bruto, tamanho_mm, ctypes.byref(achou),
                    ctypes.byref(preto_no_branco), ms, erro, len(erro))
    segundos = time.perf_counter() - inicio
    if codigo != st_ferramentas.OK:
        return _indisponivel("A caixa do conteúdo do ScanTailor falhou nesta página.",
                             f"codigo {codigo}: {erro.value.decode('utf-8', 'replace')}")

    caixa_da_pagina = Caixa(*(float(v) for v in pagina))
    tem = bool(achou.value)
    caixa_do_conteudo = Caixa(*(float(v) for v in conteudo)) if tem else None
    # O bruto existe mesmo quando o corte pela página não deixa nada.
    caixa_bruta = Caixa(*(float(v) for v in bruto))
    if caixa_bruta.largura <= 0 or caixa_bruta.altura <= 0:
        caixa_bruta = None
    return Caixas(
        pagina=caixa_da_pagina,
        conteudo=caixa_do_conteudo,
        conteudo_bruto=caixa_bruta,
        pagina_mm=caixa_da_pagina.em_mm(dpi_x, dpi_y),
        conteudo_mm=caixa_do_conteudo.em_mm(dpi_x, dpi_y) if tem else None,
        tamanho_do_conteudo_mm=(float(tamanho_mm[0]), float(tamanho_mm[1])) if tem else None,
        preto_no_branco=bool(preto_no_branco.value),
        dpi=(dpi_x, dpi_y),
        segundos=segundos,
        segundos_do_preparo=float(ms[0]) / 1000.0,
        segundos_da_pagina=float(ms[1]) / 1000.0,
        segundos_do_conteudo=float(ms[2]) / 1000.0,
    )


def dpi_para_as_caixas(largura: int, altura: int, dpi: float | None,
                       dpi_do_scan: float | None = None) -> float | None:
    """O DPI que se diz ao ScanTailor para uma página de largura x altura
    pontos desenhada a `dpi`: a MESMA conta do limpar pontinhos, do endireitar
    e do detector de gravura (ver o topo, "O DPI"). None se `dpi` não é um
    número positivo (aí achar() supõe 10 polegadas de altura)."""
    from core.pontinhos_scantailor import dpi_para_os_pontinhos

    return dpi_para_os_pontinhos(largura, altura, dpi, dpi_do_scan)


def achar_na_pagina(base: np.ndarray, dpi_do_desenho=None, dpi_do_scan=None, **opcoes) -> Caixas:
    """As caixas do ScanTailor numa página do programa: `base` é a página já
    girada, dividida e endireitada, desenhada a `dpi_do_desenho` (None = não
    se sabe); dpi_do_scan é o que o PDF diz do escaneamento (None = não se
    sabe). As outras opções são as de achar().

    O DPI dito à DLL é o de dpi_para_as_caixas (o mesmo das outras
    ferramentas do ScanTailor). Nunca levanta exceção (como achar).
    Arriscado: mudar a imagem ou o DPI que vão à DLL (as caixas mudam)."""
    if base is None or getattr(base, "ndim", 0) < 2:
        return achar(base, None, **opcoes)
    altura, largura = base.shape[:2]
    return achar(base, dpi_para_as_caixas(largura, altura, dpi_do_desenho, dpi_do_scan), **opcoes)
