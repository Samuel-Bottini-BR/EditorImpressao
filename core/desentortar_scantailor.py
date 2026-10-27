"""Desentortar a página curva perto da lombada (item 2.12 da Fase 2, 21/10/2026).

O PEDIDO
    Item 2.12 do plano: "Desentortar página curva perto da lombada". Regra da
    Fase 2 (Samuel, 13/10/2026): "implementar igual ao ScanTailor, sem
    perguntar antes" - com os ajustes de fábrica dele e, como muda a imagem,
    DESLIGADO de fábrica (livro novo e livro já começado saem iguais ao de
    hoje).

COMO O SCANTAILOR FAZ (src/dewarping e OutputGenerator.cpp, v1.2.1)
    O livro aberto no scanner faz a folha subir perto da lombada: as linhas
    do texto saem curvas e as letras ficam espremidas ali. O ScanTailor segue
    as linhas do texto (ou as beiradas brancas de cima e de baixo), monta
    duas curvas - a de cima e a de baixo do bloco de texto -, imagina a folha
    como um pedaço de cilindro entre elas e redesenha a página reta. É
    redesenho de pontos (como girar), não inventa detalhe. A cola em C está em
    terceiros/scantailor-advanced/ligacao-ferramentas/desentortar.cpp (a
    ordem e o que foi trocado estão no topo dela).

    Modos do ScanTailor e o que veio:
      "desligado"      OFF, o de fábrica dele e o nosso;
      "automatico"     AUTO: as curvas pelas linhas do texto;
      "pelas_margens"  MARGINAL: as curvas pelas beiradas brancas de cima e
                       de baixo, e um endireitar depois (o "post deskew",
                       ligado de fábrica no ScanTailor);
      (MANUAL, a malha mexida à mão, NÃO veio: precisa de uma tela de malha
       que o programa não tem.)
    Profundidade ("Depth perception"): 2,0 de fábrica (de 1,0 a 3,0); não
    há controle para ela na tela (o ScanTailor tem um, escondido no painel).

ONDE ENTRA NO PROGRAMA
    core.pipeline._preparar_metade_e_geometria, no fim do preparo da página
    (girar 90 -> dividir -> endireitar -> cortar -> DESENTORTAR), antes do
    filtro: é onde o ScanTailor faz (na saída). Assim a prévia, os cartões e
    o PDF veem a mesma página, e a marcação automática de gravura é feita na
    página já desentortada (por isso a assinatura dela ganha
    SUFIXO_DA_GRAVURA quando o desentortar está ligado).

O CORTE É SÓ UMA MEDIDA (22/10/2026, escolha do Samuel na Central: "A — Como
o ScanTailor: cortar uma vez só, no fim")
    Até 21/10 o desentortar recebia a página JÁ CORTADA rente (1 mm de
    folga): o que ele empurrava para fora saía da imagem e o cabeçalho e o
    começo das linhas sumiam (Righetti 96, Cursus 151). No ScanTailor
    (OutputGenerator.cpp, calcAreas e processWithDewarping) o corte é só um
    retângulo guardado: o desentortar lê o escaneamento inteiro, com o papel
    em volta, e a imagem é recortada uma vez, no fim. Agora é igual:
    aplicar_no_corte() recebe a página endireitada SEM o corte e a caixa do
    corte (em pontos); a DLL (versão 8) devolve a página desentortada já do
    tamanho do corte. A caixa do conteúdo (m_contentRect) é a da tinta dentro
    do corte (caixa_do_conteudo), como a do ScanTailor, e não o corte.
    Desligado, o pipeline nem chama: corta como sempre.

O QUE É SEGURO MUDAR
    Os textos da tela (ROTULOS_NA_TELA, EXPLICACAO_NA_TELA, FRASE_DO_DESFAZER).

O QUE É ARRISCADO
    - FABRICA: tem de ser DESLIGADO. Com outro valor, todo livro (inclusive os
      já começados) muda de imagem.
    - aplicar() com o modo "desligado" tem de devolver a MESMA imagem, sem
      conta nenhuma (é a prova de que nada muda de fábrica).
    - Os códigos (DESLIGADO, AUTOMATICO, PELAS_MARGENS) ficam gravados no
      projeto.json: nunca trocar o texto deles; o texto da tela é outra coisa.
    - _CODIGO_DO_MODO: os números são os de output::DewarpingMode do
      ScanTailor (OFF 0, AUTO 1, MANUAL 2, MARGINAL 3).
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

# Códigos gravados no projeto (ConfigPagina.desentortar); nunca o texto da tela.
DESLIGADO = "desligado"
AUTOMATICO = "automatico"
PELAS_MARGENS = "pelas_margens"
MODOS = (DESLIGADO, AUTOMATICO, PELAS_MARGENS)

# O de fábrica do ScanTailor (DewarpingOptions(mode = OFF)) e o nosso.
FABRICA = DESLIGADO

# output::DewarpingMode do ScanTailor.
_CODIGO_DO_MODO = {AUTOMATICO: 1, PELAS_MARGENS: 3}

# A "Depth perception" do ScanTailor (DepthPerception.h: defaultValue 2,0,
# minValue 1,0, maxValue 3,0) e o "post deskew" (DewarpingOptions: ligado).
PROFUNDIDADE_DE_FABRICA = 2.0
PROFUNDIDADE_MINIMA = 1.0
PROFUNDIDADE_MAXIMA = 3.0
ENDIREITAR_DEPOIS_DE_FABRICA = True

# PageId::SubPage do ScanTailor: a metade da folha (modelos.METADE_*).
_LADO_DA_METADE = {"inteira": 0, "esquerda": 1, "direita": 2}

ROTULO_NA_TELA = "Desentortar perto da lombada"
ROTULOS_NA_TELA = {
    DESLIGADO: "Desligado",
    AUTOMATICO: "Automático (pelas linhas do texto)",
    PELAS_MARGENS: "Pelas margens de cima e de baixo",
}
EXPLICACAO_NA_TELA = (
    "Quando a folha sobe perto da lombada, as linhas saem curvas e as letras "
    "ficam espremidas ali. O programa segue as linhas do texto (ou as margens "
    "brancas de cima e de baixo) e redesenha a página reta, como o ScanTailor. "
    "Vem desligado; ligue só nas páginas curvas.")
FRASE_DO_DESFAZER = "Desentortar na página {pagina}: {estado}"

# Acrescentado à assinatura da marcação automática de gravura quando o
# desentortar está ligado (a página que o detector vê muda). Desligado: nada.
SUFIXO_DA_GRAVURA = "|desentortar="


@dataclass(frozen=True)
class Resultado(st.Resultado):
    """st.Resultado com o que o desentortar achou.

    achou_curvas: as curvas achadas não são as do modelo "sem curva" (False =
        o ScanTailor não achou linhas que bastem e só redesenhou a página).
    angulo_depois: o endireitar depois do desentortar, em graus (só no
        "pelas margens"; 0 se não endireitou).
    """

    achou_curvas: bool = False
    angulo_depois: float = 0.0
    # Versão 9 da DLL (22/10/2026): a marca redesenhada com o mesmo modelo
    # (uint8, do tamanho de .imagem), ou None se não foi pedida.
    marca: np.ndarray | None = None


def modo_valido(modo) -> str:
    """O modo gravado, ou DESLIGADO se vier vazio ou estranho (nunca ligar por engano)."""
    return modo if modo in MODOS else DESLIGADO


def modo_da_pagina(pagina) -> str:
    """O modo desta página (ConfigPagina.desentortar). Objeto sem o campo
    (projeto de antes do item 2.12): desligado."""
    return modo_valido(getattr(pagina, "desentortar", DESLIGADO))


def ligado(pagina) -> bool:
    return modo_da_pagina(pagina) != DESLIGADO


def lado_da_pagina(pagina) -> int:
    """0 = página única, 1 = esquerda, 2 = direita (a metade da folha)."""
    return _LADO_DA_METADE.get(getattr(pagina, "metade", "inteira"), 0)


def desentortar(img: np.ndarray, dpi, modo: str, *, lado: int = 0,
                profundidade: float = PROFUNDIDADE_DE_FABRICA,
                endireitar_depois: bool = ENDIREITAR_DEPOIS_DE_FABRICA,
                conteudo: tuple[int, int, int, int] | None = None,
                corte: tuple[int, int, int, int] | None = None,
                crescer: int = 0,
                marca: np.ndarray | None = None,
                biblioteca: st.BibliotecaScanTailor | None = None) -> Resultado:
    """O desentortar do ScanTailor numa página.

    img: uint8, cinza ou azul/verde/vermelho: a página endireitada, SEM o
    corte (com o papel do scan em volta). dpi: o DPI da imagem (número ou
    par). modo: AUTOMATICO ou PELAS_MARGENS. lado: 0 única, 1 esquerda, 2
    direita.
    corte: (x, y, largura, altura) em pontos de `img`: a página de saída do
    ScanTailor (m_outRect); None = a imagem inteira.
    conteudo: (x, y, largura, altura) em pontos de `img` (m_contentRect);
    None = o próprio corte. O preparo passa caixa_do_conteudo (a tinta).
    crescer (versão 9): pontos a mais de cada lado da saída; é a MESMA página
    desentortada (mesmo modelo, mesmo ângulo, mesmo centro), só maior.
    marca (versão 9): None, ou uint8 de 1 canal do tamanho de `img`,
    redesenhada com o mesmo modelo em .marca (fora de `img` entra 255).
    Devolve Resultado: .imagem do tamanho do CORTE mais 2 x crescer, com os
    mesmos canais, ou None com .motivo. Nunca levanta exceção; não muda a
    entrada.

    Arriscado: passar a página já cortada com corte None (volta o defeito de
    21/10: o que o desentortar empurra para fora da imagem some).
    """
    biblioteca = biblioteca or st.padrao()
    try:
        if modo not in _CODIGO_DO_MODO:
            raise ValueError(f"modo do desentortar inválido: {modo!r}")
        if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or img.ndim not in (2, 3):
            raise ValueError("a página tem de ser uint8, cinza ou com 3 canais")
        if img.ndim == 3 and img.shape[2] != 3:
            raise ValueError("a página colorida tem de ter 3 canais")
        if lado not in (0, 1, 2):
            raise ValueError(f"lado inválido: {lado!r}")
        profundidade = float(profundidade)
        if not PROFUNDIDADE_MINIMA <= profundidade <= PROFUNDIDADE_MAXIMA:
            raise ValueError(f"profundidade fora de 1 a 3: {profundidade}")
        cx, cy, cl, ca = (0, 0, 0, 0) if conteudo is None else (int(v) for v in conteudo)
        if cl < 0 or ca < 0:
            raise ValueError("caixa do conteúdo com tamanho negativo")
        alt_img, larg_img = img.shape[:2]
        kx, ky, kl, ka = (0, 0, larg_img, alt_img) if corte is None else (int(v) for v in corte)
        if kl <= 0 or ka <= 0 or kx < 0 or ky < 0 or kx + kl > larg_img or ky + ka > alt_img:
            raise ValueError(f"corte fora da página: {(kx, ky, kl, ka)} em {larg_img}x{alt_img}")
        dpi_x, dpi_y = st.dpi_inteiro(dpi)
        crescer = int(crescer)
        if crescer < 0 or crescer > 20000:
            raise ValueError(f"crescer fora de 0 a 20000: {crescer}")
        if marca is not None and (not isinstance(marca, np.ndarray) or marca.dtype != np.uint8
                                  or marca.shape != img.shape[:2]):
            raise ValueError("a marca tem de ser uint8 de 1 canal, do tamanho da página")
    except (TypeError, ValueError) as erro:
        return Resultado(*_motivo("A página não pôde ser passada ao desentortar do ScanTailor.", str(erro)))
    altura, largura = img.shape[:2]
    recusa = st.motivo_de_recusa(largura, altura, dpi_x, dpi_y, "o desentortar do ScanTailor")
    if recusa is not None:
        return Resultado(*_motivo(recusa, f"página {largura}x{altura}, DPI {dpi_x}x{dpi_y}"))
    funcao = biblioteca.funcao("st_ferramentas_desentortar")
    if funcao is None:
        return Resultado(None, biblioteca.motivo_indisponivel, biblioteca.detalhe_indisponivel)

    entrada = np.ascontiguousarray(img)
    # do tamanho do corte (mais o crescer de cada lado)
    saida = np.empty((ka + 2 * crescer, kl + 2 * crescer) + entrada.shape[2:], np.uint8)
    marca_c = None if marca is None else np.ascontiguousarray(marca)
    marca_saida = None if marca is None else np.empty(saida.shape[:2], np.uint8)
    achou = ctypes.c_int(0)
    angulo = ctypes.c_double(0.0)
    erro = ctypes.create_string_buffer(512)
    canais = 1 if entrada.ndim == 2 else 3
    inicio = time.perf_counter()
    try:
        codigo = funcao(entrada.ctypes.data_as(ctypes.c_void_p), largura, altura,
                        int(entrada.strides[0]), canais, dpi_x, dpi_y,
                        _CODIGO_DO_MODO[modo], int(lado), profundidade, int(bool(endireitar_depois)),
                        kx, ky, kl, ka,
                        cx, cy, cl, ca,
                        crescer,
                        None if marca_c is None else marca_c.ctypes.data_as(ctypes.c_void_p),
                        0 if marca_c is None else int(marca_c.strides[0]),
                        saida.ctypes.data_as(ctypes.c_void_p), int(saida.strides[0]),
                        None if marca_saida is None else marca_saida.ctypes.data_as(ctypes.c_void_p),
                        0 if marca_saida is None else int(marca_saida.strides[0]),
                        ctypes.byref(achou), ctypes.byref(angulo), erro, len(erro))
    except Exception as falha:  # noqa: BLE001
        return Resultado(*_motivo("O desentortar do ScanTailor falhou nesta página.",
                                  f"{type(falha).__name__}: {falha}"))
    segundos = time.perf_counter() - inicio
    if codigo != st.OK:
        detalhe = f"código {codigo}: {erro.value.decode('utf-8', 'replace')}"
        if codigo == st.ERRO_MEMORIA:
            return Resultado(*_motivo("Faltou memória para desentortar esta página.", detalhe))
        return Resultado(*_motivo("O desentortar do ScanTailor falhou nesta página.", detalhe))
    return Resultado(saida, None, None, segundos, bool(achou.value), float(angulo.value), marca_saida)


def _motivo(motivo: str, detalhe: str | None) -> tuple:
    r = st.indisponivel(motivo, detalhe)
    return (r.imagem, r.motivo, r.detalhe_tecnico)


_AVISADOS: set[str] = set()
_TRANCA = threading.Lock()


def _avisar_uma_vez(motivo, detalhe) -> None:
    chave = f"{motivo}|{detalhe}"
    with _TRANCA:
        if chave in _AVISADOS:
            return
        _AVISADOS.add(chave)
    _log.warning("desentortar do ScanTailor indisponível, a página saiu sem ele: %s (%s)", motivo, detalhe)
    st.anotar_no_erros_log("desentortar do ScanTailor (item 2.12): a página saiu sem ele", motivo, detalhe)


def _dpi_ou_pela_altura(dpi, altura: int):
    """O DPI dito, ou (a tela não sabe) o DPI pela altura, como nas cores
    (core.pontinhos_scantailor.dpi_pela_altura)."""
    try:
        if float(dpi) > 0:
            return dpi
    except (TypeError, ValueError):
        pass
    from core import pontinhos_scantailor

    return pontinhos_scantailor.dpi_pela_altura(altura)


def aplicar(img: np.ndarray, pagina, dpi=None, *,
            biblioteca: st.BibliotecaScanTailor | None = None) -> np.ndarray:
    """O desentortar numa página SEM papel em volta (a imagem inteira é o
    corte). Com o desentortar desligado (o de fábrica) devolve a MESMA
    imagem, sem conta nenhuma. Ligado: a página desentortada, ou a mesma
    imagem se a DLL não rodou (anotado uma vez no erros.log). dpi None (a
    tela não sabe): o DPI pela altura da página.

    O preparo da página NÃO usa mais esta função (22/10/2026): usa
    aplicar_no_corte, com o papel em volta. Fica para quem só tem a página."""
    modo = modo_da_pagina(pagina)
    if modo == DESLIGADO or img is None:
        return img
    dpi = _dpi_ou_pela_altura(dpi, img.shape[0])
    resultado = desentortar(img, dpi, modo, lado=lado_da_pagina(pagina), biblioteca=biblioteca)
    if not resultado.disponivel:
        _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
        return img
    return resultado.imagem


def caixa_do_conteudo(img: np.ndarray, caixa: tuple[int, int, int, int], dpi) -> tuple[int, int, int, int]:
    """A caixa do conteúdo (m_contentRect do ScanTailor), (x, y, largura,
    altura) em pontos de `img`: a caixa da tinta DENTRO do corte `caixa`
    ((x0, y0, x1, y1)), sem o que encosta na beirada do corte.

    Por que (medido em 22/10/2026): no ScanTailor a caixa do conteúdo é a do
    texto (etapa "Select Content"), justa, e não o corte; o desentortar usa
    ela para seguir as linhas e para saber até onde vai o texto. O corte do
    programa é muitas vezes a folha inteira (Righetti, Marial), e com ele
    como caixa do conteúdo o desentortar seguia as beiradas da folha e
    redesenhava a página errado. Conferido em seis páginas do acervo e na de
    mentira (relatorios/fase2-itens/ONDE-PAREI.md, 22/10): com a caixa da
    tinta a tinta das páginas retas fica no lugar (Marial 41: 0,49 -> 1,00;
    Cursus 176: 0,97 -> 1,00).

    Como mede: a tinta (Otsu) numa cópia a 75 DPI; ficam as manchas que não
    encostam na beirada do corte (sombra da lombada, faixa preta do scanner,
    tira da página vizinha) e não são pontinhos (menos de 4 pontos a 75 DPI)
    nem do tamanho do corte. Sem 5 manchas: o próprio corte.

    PROVISÓRIO: a caixa do conteúdo do próprio ScanTailor (ContentBoxFinder)
    é o item 2.5, em outro ramo; quando ele entrar, a caixa dele deve tomar
    o lugar desta conta. Arriscado: usar o corte como caixa (o desentortar
    segue a folha) ou tirar o "não encosta na beirada" (a faixa preta do
    scanner entra na caixa).
    """
    x0, y0, x1, y1 = caixa
    corte = (x0, y0, x1 - x0, y1 - y0)
    pedaco = img[y0:y1, x0:x1]
    if pedaco.size == 0:
        return corte
    cinza = pedaco if pedaco.ndim == 2 else cv2.cvtColor(pedaco, cv2.COLOR_BGR2GRAY)
    try:
        dpi_y = float(dpi[1]) if isinstance(dpi, (tuple, list)) else float(dpi)
    except (TypeError, ValueError):
        dpi_y = 300.0
    escala = min(1.0, 75.0 / max(1.0, dpi_y))
    pequena = cv2.resize(cinza, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    if min(pequena.shape[:2]) < 8:
        return corte
    _, tinta = cv2.threshold(pequena, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _, caixas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    altura, largura = tinta.shape
    ficam = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in caixas[i])
        if area < 4:
            continue
        if x <= 0 or y <= 0 or x + w >= largura or y + h >= altura:
            continue
        if w > 0.9 * largura or h > 0.9 * altura:
            continue
        ficam.append((x, y, x + w, y + h))
    if len(ficam) < 5:
        return corte
    ficam = _so_o_bloco_do_texto(ficam, largura)
    m = np.array(ficam)
    cx0, cy0 = int(m[:, 0].min() / escala), int(m[:, 1].min() / escala)
    cx1 = min(x1 - x0, int(np.ceil(m[:, 2].max() / escala)))
    cy1 = min(y1 - y0, int(np.ceil(m[:, 3].max() / escala)))
    if cx1 - cx0 < 8 or cy1 - cy0 < 8:
        return corte
    return (x0 + cx0, y0 + cy0, cx1 - cx0, cy1 - cy0)


# --- só o bloco do texto (etapa 10b da obra, D-493, 27/10/2026) -------------
#
# Decisão D-493 (escolha da gerente, apoiada em D-113: "o primeiro passo em uma
# pagina dessas seria tirar essa moldura preta [...] ai o desentortador não
# iria confundir as letras com moldura preta. não é?"): "O desentortar segue
# só o bloco do texto, sem as notas da margem". A etapa 10a mediu na página de
# teste do D-113 (Marial 41 encurvada, com moldura): a causa de a curva não
# ser achada não é a moldura, são as NOTAS DA MARGEM dentro da caixa do
# conteúdo - com a caixa só do bloco do texto a DLL acha a curva.
# Como acha o bloco: as manchas de tinta que ficam (as de caixa_do_conteudo)
# são juntadas em FAIXAS DE LINHA (faixas da altura mediana das manchas, de
# cima para baixo). Em cada faixa, a primeira e a última mancha dão onde a
# linha começa e acaba; a beirada do bloco é onde a MAIORIA das linhas começa
# (percentil BLOCO_PERCENTIL dos começos) e acaba (100 - BLOCO_PERCENTIL dos
# fins). A nota da margem só aparece em poucas linhas, e a mancha que fica
# que passa da beirada do bloco mais de NOTA_FOLGA_MM sai da caixa.
# Se sairia demais (mais de NOTA_MANCHAS_MAXIMA das manchas), não é nota: a
# caixa de sempre. Arriscado: subir BLOCO_PERCENTIL (a linha curta do fim do
# parágrafo passaria a mandar na beirada) ou NOTA_MANCHAS_MAXIMA.
BLOCO_PERCENTIL = 20
NOTA_FOLGA_MM = 2.0
NOTA_MANCHAS_MAXIMA = 0.15


def _so_o_bloco_do_texto(manchas: list, largura: int, pontos_por_mm: float = 75.0 / 25.4) -> list:
    """As manchas (x0, y0, x1, y1, a 75 DPI) sem as notas da margem (ver
    BLOCO_PERCENTIL). Sem nota clara, devolve as mesmas manchas."""
    if len(manchas) < 5 or largura < 4:
        return manchas
    m = np.array(manchas)
    # faixas da altura de uma linha (a altura mediana das manchas): na página
    # curva as linhas encostam umas nas outras e a projeção não as separa
    passo = max(2, int(np.median(m[:, 3] - m[:, 1])))
    centro = (m[:, 1] + m[:, 3]) / 2.0
    comecos, fins = [], []
    for a in range(int(m[:, 1].min()), int(m[:, 3].max()) + 1, passo):
        nela = m[(centro >= a) & (centro < a + passo)]
        if len(nela) >= 2:
            comecos.append(int(nela[:, 0].min()))
            fins.append(int(nela[:, 2].max()))
    if len(comecos) < 5:
        return manchas
    esquerda = float(np.percentile(comecos, BLOCO_PERCENTIL))
    direita = float(np.percentile(fins, 100 - BLOCO_PERCENTIL))
    folga = NOTA_FOLGA_MM * pontos_por_mm
    fora = (m[:, 0] < esquerda - folga) | (m[:, 2] > direita + folga)
    if not fora.any() or fora.mean() > NOTA_MANCHAS_MAXIMA:
        return manchas
    ficam = [tuple(int(v) for v in x) for x, sai in zip(m, fora) if not sai]
    return ficam if len(ficam) >= 5 else manchas


# --- a proteção e o "aumentando a página" (22/10/2026) ----------------------
#
# Respostas do Samuel às perguntas P1 e P2 do 2.12 (22/10/2026): P1 "B —
# Proteção: se a tinta passar a encostar na beirada, a página sai sem
# desentortar e vai para o 'Para revisar'"; P2 "B — A mesma proteção da
# pergunta anterior" (o "pelas margens" que entorta a página com fundo
# escuro). E, sobre a opção C da P1 ("Ainda vou poder selecionar a opção c
# para as paginas que entrarem para revisão?"): sim, só na página, pelo botão
# do aviso (ConfigPagina.desentortar_aumentar).
#
# COMO MEDE: a página reta ganha uma MARCA do mesmo tamanho (MARCA_TINTA na
# tinta da caixa do conteúdo, MARCA_PAPEL no resto do corte, MARCA_FORA fora
# do corte), e a DLL (versão 9) redesenha a marca com o MESMO modelo numa
# página CRESCER_MM maior de cada lado. Na marca redesenhada:
#   - "tinta para fora": pedaços de tinta do conteúdo (de PECA_MINIMA_MM ou
#     mais nos dois sentidos) que caíram fora do corte; PECAS_PARA_FORA ou mais
#     = o desentortar cortava letras (Righetti 96: 22 pedaços; as páginas que
#     saem certas: 0 ou 1);
#   - "fundo para dentro": a fração da página de saída que veio de fora do
#     corte; mais de FUNDO_DENTRO_MAXIMO = o desentortar puxou fundo, sombra ou
#     página vizinha para dentro (Cursus 176 e Matemática 31-66 no "pelas
#     margens": 14% a 30%; as que saem certas: até 0,7%).
# Medido em 22/10/2026 em 14 páginas (relatorios/fase2-itens/ONDE-PAREI.md).
# A página dentro do corte é a mesma, ponto por ponto, com e sem o crescer
# (conferido nas 14 x 2 modos): a medida não muda a imagem.
# SEGURO MUDAR: os limites (com nova medida nas páginas). ARRISCADO: medir na
# imagem em vez da marca (a faixa preta do scanner e a página vizinha
# confundem) ou tirar o crescer (a tinta que sai do corte não seria vista).

MARCA_TINTA, MARCA_PAPEL, MARCA_FORA = 0, 128, 255
CRESCER_MM = 10.0           # quanto a página medida cresce de cada lado
PECA_MINIMA_MM = 1.0        # pedaço de tinta que conta (largura e altura)
PECAS_PARA_FORA = 3         # a partir de quantos pedaços para fora recusa
FUNDO_DENTRO_MAXIMO = 0.02  # fração da página vinda de fora do corte
AUMENTO_MAXIMO_MM = 25.0    # o "aumentando a página": até quanto cresce
FOLGA_DO_AUMENTO_MM = 1.0   # a folga em volta da tinta (a do corte)

# --- a conferência depois do botão (resposta P5 do Samuel, 23/10/2026) ------
#
# P5 "C — Aparece sempre, mas depois do clique o programa confere de novo...",
# com o ajuste dele: "Mas o programa vai saber sempre que estiver deformada, o
# aviso deve perguntar e não fazer automaticamente." Depois do botão
# "Desentortar aumentando a página" a página NÃO volta sozinha: as mesmas duas
# medidas da proteção são feitas de novo na página aumentada e, se ela ainda
# sair deformada, Preparo.ainda_deformada = True (o pipeline põe o aviso
# analise.DESENTORTAR_AINDA_DEFORMADA, que pergunta "Desfazer" ou "Manter
# assim"). As duas medidas, na página aumentada:
#   - "tinta saindo da página": pedaços de tinta (os mesmos de PECA_MINIMA_MM)
#     cortados pela beirada da página AUMENTADA (a página já cresceu até
#     AUMENTO_MAXIMO_MM; o que ainda passa disso fica cortado). PECAS_PARA_FORA
#     ou mais = deformada (Destino do socialismo 18: 22 pedaços; Righetti 96:
#     0; medido em 23/10/2026);
#   - "fundo de fora entrando": a mesma fração de medir_o_estrago (o que veio
#     de fora do corte para dentro do lugar da página), com o limite
#     FUNDO_DENTRO_MAXIMO_AUMENTANDO. O limite é maior que o da proteção
#     porque, quando a página cresce, um pouco de papel de fora do corte entra
#     de propósito pela beirada oposta (Righetti 96: 5,7%, papel branco embaixo
#     do rodapé, e a página sai boa); as que saem deformadas: Cursus 176 e
#     Matemática 65 "pelas margens" 17,9% e 30,4%, Destino 18 39,6%.
# SEGURO MUDAR: os limites (com nova medida nas páginas). ARRISCADO: voltar a
# página sozinho (o Samuel pediu que o aviso pergunte).
FUNDO_DENTRO_MAXIMO_AUMENTANDO = 0.10


@dataclass(frozen=True)
class Preparo:
    """O passo do desentortar no preparo (preparar_no_corte).

    imagem: a página que sai. saiu_sem: a proteção recusou o desentortar (a
    imagem é o corte sem desentortar e a página vai para o "Para revisar").
    pecas_para_fora, fundo_dentro: as medidas (None se não mediu).
    ainda_deformada (23/10/2026, resposta P5): só com o "aumentando a página":
    a página aumentada ainda saiu deformada pelas medidas (a imagem é a
    aumentada mesmo assim; quem decide é a pessoa, pelo aviso).
    pecas_cortadas: os pedaços de tinta cortados pela beirada da página
    aumentada (None fora do "aumentando a página").
    """

    imagem: np.ndarray
    saiu_sem: bool = False
    pecas_para_fora: int | None = None
    fundo_dentro: float | None = None
    ainda_deformada: bool = False
    pecas_cortadas: int | None = None


def _pontos_por_mm(dpi) -> float:
    try:
        d = float(dpi[1]) if isinstance(dpi, (tuple, list)) else float(dpi)
    except (TypeError, ValueError):
        d = 300.0
    return max(1.0, d) / 25.4


def marca_da_pagina(reta: np.ndarray, caixa, conteudo) -> np.ndarray:
    """A marca da proteção: uint8 do tamanho de `reta` - MARCA_FORA fora do
    corte `caixa` ((x0, y0, x1, y1)), MARCA_PAPEL dentro, e MARCA_TINTA na
    tinta (Otsu do corte) dentro da caixa do conteúdo `conteudo`
    ((x, y, largura, altura))."""
    x0, y0, x1, y1 = caixa
    cinza = reta if reta.ndim == 2 else cv2.cvtColor(reta, cv2.COLOR_BGR2GRAY)
    marca = np.full(cinza.shape, MARCA_FORA, np.uint8)
    marca[y0:y1, x0:x1] = MARCA_PAPEL
    cx, cy, cl, ca = conteudo
    if cl > 0 and ca > 0 and y1 > y0 and x1 > x0:
        limiar, _ = cv2.threshold(cinza[y0:y1, x0:x1], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        pedaco = marca[cy:cy + ca, cx:cx + cl]
        # "<=": o Otsu devolve o limiar onde o que passa dele e papel
        pedaco[cinza[cy:cy + ca, cx:cx + cl] <= limiar] = MARCA_TINTA
    return marca


def medir_o_estrago(marca: np.ndarray, crescer: int, dpi) -> tuple[int, float]:
    """(pedaços de tinta para fora do corte, fração da página vinda de fora)
    na marca redesenhada pela DLL com `crescer` pontos a mais de cada lado."""
    altura, largura = marca.shape[0] - 2 * crescer, marca.shape[1] - 2 * crescer
    tinta = (marca < 64).astype(np.uint8)
    tinta[crescer:crescer + altura, crescer:crescer + largura] = 0
    minimo = PECA_MINIMA_MM * _pontos_por_mm(dpi)
    _, _, caixas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    pecas = int(sum(1 for c in caixas[1:] if c[2] >= minimo and c[3] >= minimo))
    dentro = marca[crescer:crescer + altura, crescer:crescer + largura]
    return pecas, float((dentro > 192).mean()) if dentro.size else 0.0


def recusar(pecas_para_fora: int, fundo_dentro: float) -> bool:
    """A regra da proteção (os limites no topo desta parte)."""
    return pecas_para_fora >= PECAS_PARA_FORA or fundo_dentro > FUNDO_DENTRO_MAXIMO


def pecas_cortadas_pela_beirada(marca: np.ndarray, dpi) -> int:
    """Resposta P5 (23/10/2026), a medida "tinta saindo da página" na página
    AUMENTADA: quantos pedaços de tinta (de PECA_MINIMA_MM ou mais nos dois
    sentidos) encostam na beirada da marca redesenhada com o crescer do
    "aumentando a página" - isto é, ainda passam do aumento máximo e ficam
    cortados. `marca`: a redesenhada pela DLL (Resultado.marca)."""
    tinta = (marca < 64).astype(np.uint8)
    if not tinta.any():
        return 0
    _, rotulos, caixas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    na_beirada = set(np.unique(np.concatenate(
        [rotulos[0], rotulos[-1], rotulos[:, 0], rotulos[:, -1]])).tolist()) - {0}
    minimo = PECA_MINIMA_MM * _pontos_por_mm(dpi)
    return int(sum(1 for i in na_beirada if caixas[i][2] >= minimo and caixas[i][3] >= minimo))


def ainda_deformada(pecas_cortadas: int, fundo_dentro: float) -> bool:
    """A regra da conferência depois do botão (resposta P5, os limites no topo
    desta parte): a página aumentada ainda saiu deformada?"""
    return pecas_cortadas >= PECAS_PARA_FORA or fundo_dentro > FUNDO_DENTRO_MAXIMO_AUMENTANDO


def _recorte_aumentado(imagem: np.ndarray, marca: np.ndarray, crescer: int, dpi) -> np.ndarray:
    """O "desentortar aumentando a página": da página desentortada com
    `crescer` a mais de cada lado, fica o corte de sempre mais o que a tinta
    do conteúdo precisou (com FOLGA_DO_AUMENTO_MM em volta). Pontinho menor
    que PECA_MINIMA_MM nos dois sentidos não faz a página crescer. Sem tinta
    para fora, sai o corte de sempre."""
    altura, largura = marca.shape[0] - 2 * crescer, marca.shape[1] - 2 * crescer
    x0, y0, x1, y1 = crescer, crescer, crescer + largura, crescer + altura
    tinta = (marca < 64).astype(np.uint8)
    minimo = PECA_MINIMA_MM * _pontos_por_mm(dpi)
    _, _, caixas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    folga = int(round(FOLGA_DO_AUMENTO_MM * _pontos_por_mm(dpi)))
    for c in caixas[1:]:
        x, y, w, h = (int(v) for v in c[:4])
        if w < minimo and h < minimo:
            continue
        x0, y0 = min(x0, x - folga), min(y0, y - folga)
        x1, y1 = max(x1, x + w + folga), max(y1, y + h + folga)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(marca.shape[1], x1), min(marca.shape[0], y1)
    return imagem[y0:y1, x0:x1].copy()


def sem_a_moldura_do_scanner(reta: np.ndarray) -> np.ndarray:
    """`reta` com a moldura escura do scanner pintada de branco (o que fica
    fora da pagina achada pela conta "so o preto" de core/borda_preta, a que o
    Samuel viu em 12/10). Sem moldura: a propria `reta` (sem copiar). So para
    o desentortar (D-113). Arriscado: usar a conta "ate a moldura" aqui (ela
    aperta no impresso e pintaria papel com letra)."""
    from core import borda_preta

    altura, largura = reta.shape[:2]
    x0, y0, x1, y1 = (int(round(v)) for v in borda_preta.so_o_preto(reta))
    if (x0, y0, x1, y1) == (0, 0, largura, altura) or x1 - x0 < 8 or y1 - y0 < 8:
        return reta
    return borda_preta.pintar_fora(reta, (x0 / largura, y0 / altura, x1 / largura, y1 / altura))


def preparar_no_corte(reta: np.ndarray, caixa: tuple[int, int, int, int] | None, pagina,
                      dpi=None, *, biblioteca: st.BibliotecaScanTailor | None = None) -> Preparo:
    """O passo do preparo (22/10/2026, "cortar uma vez só, no fim"), com a
    proteção e o "aumentando a página".

    reta: a página endireitada e AINDA SEM O CORTE (o papel do scan em volta).
    caixa: o corte medido pelo programa, (x0, y0, x1, y1) em pontos de `reta`
    (a conta de core.recortar.caixa_em_pontos); None = sem corte.
    Devolve Preparo: a página desentortada do tamanho do corte; se a proteção
    recusou, o corte sem desentortar e saiu_sem=True; com
    pagina.desentortar_aumentar, a página desentortada do tamanho que a tinta
    precisou, sem voltar sozinha (resposta P5 do Samuel, 23/10/2026: "o aviso
    deve perguntar e não fazer automaticamente"): as mesmas medidas da
    proteção são feitas de novo nela e, se ainda saiu deformada,
    ainda_deformada=True (o pipeline põe o aviso que pergunta). Se a DLL não rodou
    (anotado uma vez no erros.log): o corte da página sem desentortar (o que
    sairia com o desentortar desligado), saiu_sem=False.

    Só para página com o desentortar ligado: desligado, quem chama corta como
    sempre (o pipeline nem chama esta função; ver core.pipeline). dpi None (a
    tela não sabe): o DPI pela altura da página inteira.

    Arriscado: cortar `reta` antes de chamar (volta o defeito de 21/10) ou
    mudar a caixa (o corte medido tem de ser o mesmo do desentortar desligado).
    """
    altura, largura = reta.shape[:2]
    x0, y0, x1, y1 = (0, 0, largura, altura) if caixa is None else caixa
    sem = reta[y0:y1, x0:x1]
    modo = modo_da_pagina(pagina)
    if modo == DESLIGADO:
        return Preparo(sem.copy())
    dpi = _dpi_ou_pela_altura(dpi, altura)
    # Obra 26/10, etapa 10a (D-113, Samuel em d212-1, 23/10/2026: "o primeiro
    # passo em uma pagina dessas seria tirar essa moldura preta transformando a
    # pagina em totalmente branca sem mexer nas letras, ai o desentortador nao
    # iria confundir as letras com moldura preta"): a caixa do conteudo (o que
    # o desentortar segue: as linhas do texto) e a marca da protecao sao
    # medidas numa copia com a moldura escura do scanner (a conta "so o
    # preto", core/borda_preta) pintada de branco. Foi a causa achada pelo
    # verificador do 2.12 (img/causa-curvada2-moldura.jpg, 23/10): com a caixa
    # pegando a moldura nada mudava; com a caixa so do texto, a curva era
    # achada. A pagina que vai ao desentortar e a que sai sao as de sempre
    # (pintar a imagem tambem mudava a Marial 41 reta: 0,98 da tinta no
    # lugar). Sem moldura: nada muda.
    sem_moldura = sem_a_moldura_do_scanner(reta)
    conteudo = caixa_do_conteudo(sem_moldura, (x0, y0, x1, y1), dpi)
    marca = marca_da_pagina(sem_moldura, (x0, y0, x1, y1), conteudo)
    aumentar = bool(getattr(pagina, "desentortar_aumentar", False))
    crescer = int(round((AUMENTO_MAXIMO_MM if aumentar else CRESCER_MM) * _pontos_por_mm(dpi)))
    resultado = desentortar(reta, dpi, modo, lado=lado_da_pagina(pagina),
                            corte=(x0, y0, x1 - x0, y1 - y0), conteudo=conteudo,
                            crescer=crescer, marca=marca, biblioteca=biblioteca)
    if not resultado.disponivel:
        _avisar_uma_vez(resultado.motivo, resultado.detalhe_tecnico)
        return Preparo(sem.copy())
    pecas, fundo = medir_o_estrago(resultado.marca, crescer, dpi)
    if aumentar:
        cortadas = pecas_cortadas_pela_beirada(resultado.marca, dpi)
        return Preparo(_recorte_aumentado(resultado.imagem, resultado.marca, crescer, dpi),
                       False, pecas, fundo, ainda_deformada(cortadas, fundo), cortadas)
    if recusar(pecas, fundo):
        return Preparo(sem.copy(), True, pecas, fundo)
    h, w = y1 - y0, x1 - x0
    return Preparo(resultado.imagem[crescer:crescer + h, crescer:crescer + w].copy(), False, pecas, fundo)


def aplicar_no_corte(reta: np.ndarray, caixa: tuple[int, int, int, int] | None, pagina,
                     dpi=None, *, biblioteca: st.BibliotecaScanTailor | None = None) -> np.ndarray:
    """Só a imagem de preparar_no_corte (com a proteção). Fica para quem não
    precisa saber se a proteção recusou; o preparo da página usa
    preparar_no_corte, que diz (para o aviso do "Para revisar")."""
    return preparar_no_corte(reta, caixa, pagina, dpi, biblioteca=biblioteca).imagem
