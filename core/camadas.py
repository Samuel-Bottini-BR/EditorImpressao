"""Tirar o fundo de PDF que já vem com camadas (item 1.1 do Plano Definitivo).

Os livros do Internet Archive (Palatino, Opus Majus, Rhetorica, Siebmacher)
vêm montados em duas camadas, em todas as páginas
(docs/pesquisa/fase1-1.1-camadas-internet-archive.md):

    1. embaixo, o FUNDO: a página inteira sem máscara, quase sempre em 1/3 da
       resolução (as 10 primeiras e as 4 últimas páginas vêm inteiras);
    2. por cima, a CAMADA DE CIMA: a página inteira colorida, recortada por
       uma máscara de 1 bit (JBIG2). Ela só vale onde a máscara deixa: fora
       dela a cor é lixo (o Internet Archive enche com a cor da tinta vizinha).

Tirar o fundo = começar de uma página branca e pôr a cor da camada de cima só
onde a máscara deixa. Isso já dá papel branco, letra com a cor original (o
título vermelho do Opus Majus 3 continua vermelho) e faz sumir o que só existe
no fundo: a mancha do verso, o carimbo, a mancha d'água.

O PERIGO é a figura cujos tons só existem no fundo (a foto da estátua do Opus
Majus 20: a camada de cima tem só os pontinhos escuros). Por isso:

    - as ZONAS DE FIGURA vêm do detector de gravura do programa
      (DETECTOR_DE_FIGURAS, hoje core/detectar_regioes.py; o item 1.2 põe o
      do ScanTailor no lugar trocando só essa variável);
    - dentro de uma zona em que o FUNDO tem traço ou tom que a camada de cima
      não cobre (a foto; a hachura fina da xilogravura que a máscara do
      Internet Archive não pegou), a página fica como o PDF desenha (fundo +
      camada de cima), com o papel da zona como está; zona em que o fundo é só
      papel, mancha clara e letra "fantasma" (tabela, esquema, diagrama: tudo
      está em cima) sai branca como o resto;
    - se as zonas mantidas são a página inteira, ou se sobra no fundo, fora
      delas, uma área grande com tom de figura (bem mais escura ou mais clara
      que o papel, ou de outra cor) que não encosta na borda da imagem (REDE
      DE SEGURANÇA: foto que o detector não viu), a página fica INTACTA (o
      programa segue como hoje). Nunca apagar uma foto.

Duas funções para o resto do programa:

    camadas_da_pagina(doc, i)   reconhece a montagem só pela lista de imagens e
                                pelo conteúdo da página, SEM decodificar imagem
                                nenhuma (milissegundos);
    tirar_fundo(doc, i, dpi)    monta a página sem o fundo; devolve imagem None
                                quando não se aplica (sem camadas) ou quando a
                                página deve ficar intacta. Nos dois casos o
                                programa segue como hoje (pagina_para_array).

E uma para a conferência (conferencia.py --funcao core.camadas:tirar_fundo_do_pdf).

Regras que valem aqui (CLAUDE.md): uma página por vez na memória (as camadas
de uma página, e nada de outra); nenhum modelo desenha pixel - o detector só
aponta a zona, e o pixel que sai é sempre do próprio PDF (camada de cima ou
fundo) ou branco; este módulo não importa nada de ui/.

Seguro mudar: DPI_DA_ANALISE, LINHAS_POR_FAIXA (só tempo e memória).
Arriscado mudar: TOM_DE_FIGURA, COR_DE_FIGURA, TINTA_SO_NO_FUNDO e
AREA_DE_FIGURA_ESQUECIDA (medidos nas 14 páginas do gabarito e no livro da
Pesel; afrouxar faz foto virar pontilhado e xilogravura virar mancha, apertar
faz mancha e dobra voltarem); _cor_do_papel (o "papel" errado inverte tudo:
na Pesel o linho viraria papel e sumiria); a leitura da máscara em _ler_alfa
(a polaridade foi conferida contra o desenho do MuPDF nas duas formas de
máscara, ver tests/test_camadas.py); a ordem "fundo antes, cima depois" em
camadas_da_pagina.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np

# A mesma tranca de core/pdf_io.py: duas threads no MuPDF ao mesmo tempo podem
# travar o processo (achado de 08/09/2026). Tudo que chama o fitz aqui passa
# por ela; a detecção de figuras e as contas em numpy ficam de fora.
from core.pdf_io import _TRANCA, MAX_PIXELS

# --- o que sai -----------------------------------------------------------------

SEM_CAMADAS = "sem_camadas"          # não se aplica: o programa segue como hoje
FUNDO_TIRADO = "fundo_tirado"        # a imagem está pronta
DEIXADA_INTACTA = "deixada_intacta"  # tem camadas, mas tirar o fundo apagaria figura

# --- reconhecer -------------------------------------------------------------------

# Folga para "a imagem cobre a página inteira", em fração do lado. Medido: no
# Opus Majus 20 o fundo começa 0,05 pt abaixo do canto (0,01% da altura).
FOLGA_DA_CAIXA = 0.01

# --- montar -----------------------------------------------------------------------

# Resolução em que o detector de figuras e as medidas do fundo trabalham. A
# análise do livro já roda a 150 DPI (CLAUDE.md, seção 7) e o detector acha
# gravura no tamanho da prévia; mais que isso só custa tempo.
DPI_DA_ANALISE = 150

# A página é montada em faixas de linhas, para a conta em ponto flutuante não
# ocupar a página inteira de uma vez (a página do Opus Majus 256 tem 14
# megapixels na resolução da camada de cima).
LINHAS_POR_FAIXA = 256

# Quanto um pixel do FUNDO precisa se afastar do papel (em níveis de cinza, 0
# a 255, para mais escuro OU mais claro) para contar como tinta ou tom de
# figura. A mancha d'água, o amarelado, o verso e as letras "fantasma" que o
# Internet Archive deixa embaixo da tinta ficam 20 a 55 níveis abaixo do papel
# (fantasma no Palatino 5: 147 contra 199); hachura e sombra de foto, bem mais
# de 60. "Mais claro" existe por causa do livro de bordados da Pesel: ali o
# "papel" é o cartão pardo (cinza 95 a 105) e a foto do linho em cima dele é
# mais clara (21% a 47% da página passam de 60 de diferença).
TOM_DE_FIGURA = 60

# A mesma pergunta pela cor: distância (a, b do Lab do OpenCV) entre o pixel
# do fundo e a cor do papel. É para pintura clara e dourado, que têm quase o
# brilho do papel. Medido em 28/09/2026 (fundo onde a camada de cima não
# cobre): acima de 35 fica 0% nas 14 páginas com camadas do gabarito e no
# Palatino 66 e 67 (manchas vermelhas), e até 0,4% nas pranchas da Pesel; 40
# fica com folga. Sem exemplo de verdade de pintura clara no fundo (nenhum dos
# livros tem): é segurança, e só pode fazer a página sair MAIS como o PDF.
COR_DE_FIGURA = 40

# Até este alfa (0 a 255) a camada de cima "não cobre" o pixel: o que o fundo
# tem ali some quando o fundo sai.
ALFA_QUE_NAO_COBRE = 64

# Uma zona de figura fica como o PDF desenha quando esta fração dela tem
# "tinta só no fundo": fundo que se afasta do papel (TOM_DE_FIGURA ou
# COR_DE_FIGURA) onde a camada de cima não cobre. É a hachura que a máscara do
# Internet Archive não pegou (xilogravura) e o tom da foto. Medido na zona que
# o detector de hoje marca (28/09/2026, análise a 150 DPI):
#
#     foto do Opus Majus 20                   34%
#     capitular "Q" do Palatino 9             13% a 19%
#     molduras grossas (Palatino 9, 10, 57)   11% a 25%
#     página inteira do Palatino 5            9% (o retrato)
#     gravuras de página inteira: Rhetorica
#       5 e 255, Palatino 116                 3,1% a 4,0%
#     página inteira da Rhetorica 73          1,1% (a mancha d'água é clara)
#     tabela do Opus 256, diagramas do 165    0%   (tudo está em cima)
#
# O corte fica no vão entre 1,1% e 3,1%, puxado para baixo: errar para cima
# (manter uma zona que podia sair branca) só deixa a zona como está; errar
# para baixo quebra uma gravura. Com um corte acima de 10% o retrato do
# Palatino 5 perde a hachura fina e vira manchas (visto na rodada de
# conferência de 28/09, 18:36).
TINTA_SO_NO_FUNDO = 0.02

# Abaixo desta fração de fundo "livre" (longe de qualquer tinta de cima), a
# camada de cima é a textura de um OBJETO (capa de pano, tecido), e não tinta
# sobre papel: a página fica intacta. Tirar o fundo de uma capa deixa só os
# pontinhos da trama no branco. Medido (28/09/2026): capas do Opus Majus e da
# Pesel, 0% a 6%; todas as outras páginas medidas nos cinco livros, 30% ou
# mais (o menor: a prancha de caligrafia branca em fundo preto do Palatino 71).
PAGINA_COBERTA_PELA_MASCARA = 0.15

# Papel é claro. Quando o tom mais comum do fundo (ver _cor_do_papel) fica
# abaixo disto, a "página" é capa de couro, cartão ou objeto, e fica intacta:
# pintar de branco o couro da capa é apagar a foto da capa. Medido nas 1256
# páginas dos cinco livros com camadas (28/09/2026, cinza 0 a 255): papel de
# verdade, 136 (texto sobre cartão claro da Pesel) a 233; capas (Palatino,
# Siebmacher, Pesel), 36 a 108; cartão pardo da Pesel, 81 a 117 (o de 117 é
# uma página em branco: fica intacta, o lado seguro); pranchas escuras do
# Siebmacher, 17 a 61.
PAPEL_ESCURO_DEMAIS = 120

# Se as zonas mantidas cobrem esta fração da página, montar daria a própria
# página: ela é dada como intacta (imagem None, o programa segue como hoje).
PAGINA_INTEIRA_E_FIGURA = 0.90

# Rede de segurança: área com tom de figura no fundo, fora das zonas mantidas
# e sem encostar na borda da imagem, a partir da qual a página fica intacta.
# Em fração da página. Medido (28/09/2026): a foto do Opus Majus 20, se o
# detector não a visse, dá 4%; as outras 13 páginas com camadas do gabarito,
# até 0,12%. O preto de fora do livro no Siebmacher encosta na borda e não
# conta. Nas pranchas da Pesel a moldura clara da prancha fica fora da zona
# do detector e dá 2% a 4,5%: a página fica intacta (o lado seguro).
AREA_DE_FIGURA_ESQUECIDA = 0.015

# Densidade mínima de pixels com tom de figura dentro da área, para a área
# contar (a junção por fechamento pode costurar pontinhos esparsos numa área
# grande).
DENSIDADE_DA_FIGURA_ESQUECIDA = 0.25

# Fundo de scanner e borda da folha não são figura. Uma mancha do fundo é
# tratada como tal quando ENCOSTA na borda da imagem (a menos de BORDA_DA_IMAGEM
# do lado) e tem pelo menos METADE_NA_FAIXA dos pixels na faixa de
# FAIXA_DA_BORDA junto às bordas. A segunda condição é para uma foto que vai até
# a borda (sangrada) não ser jogada fora junto: ela encosta, mas está quase
# toda no miolo. Medido no Siebmacher (28/09/2026): o preto de fora do livro
# ocupa 7% da largura e o detector de hoje marca a página inteira como objeto;
# sem esta regra, 97 das 134 páginas (até as em branco) ficavam intactas.
BORDA_DA_IMAGEM = 0.01
FAIXA_DA_BORDA = 0.10
METADE_NA_FAIXA = 0.5

# A partir desta fração da página com "tinta só no fundo" FORA das zonas
# mantidas, a página sai com o fundo tirado mas marcada para CONFERIR (como o
# DESENHO_OU_ESCRITA do detector: não finge certeza). É o traço que some com o
# fundo: moldura grossa que a máscara furou, ou gravura inteira que o detector
# de hoje não marca. Medido no Palatino inteiro (28/09/2026): as gravuras de
# página inteira que perdem hachura (48, 66, 68, 73, 94, 95, 130) dão 2,6% a
# 3,9%; as páginas de texto com moldura grossa, 1,2% a 2,1% (e perdem o peso
# da moldura); texto sem moldura, até 0,7%. Nenhuma medida separou as duas
# primeiras (tentado: fração, densidade local, manchas compactas - os números
# se cruzam), então a decisão fica com o detector do item 1.2, e aqui só se
# avisa.
CONFERIR_TINTA_PERDIDA = 0.015

# Na margem, abaixo deste cinza é o preto de fora do livro (fundo do scanner),
# e não entra na conta da cor do papel. Medido (28/09/2026): fundo do scanner
# do Siebmacher, 17 a 61; o papel mais escuro dos cinco livros (cartão pardo
# da Pesel), 81. Sem isto, no Siebmacher 105 (a folha menor que o scanner) o
# "papel" saía 61 e uma página manuscrita ficava intacta sem precisar.
PRETO_DO_SCANNER = 70

# Quanto fundo livre (fração da página) a margem, ou o que fica fora das
# zonas de figura, precisa ter para a cor do papel ser medida ali. Ver
# _cor_do_papel.
FORA_DAS_ZONAS_PARA_O_PAPEL = 0.05


class NaoSeAplica(Exception):
    """A página não tem as camadas do Internet Archive: o programa segue como
    hoje. Só a função da conferência levanta isto; o resto devolve None."""


# ==========================================================================
# (a) reconhecer: só a lista de imagens e o conteúdo da página
# ==========================================================================


@dataclass(frozen=True)
class CamadasDaPagina:
    """Onde estão as camadas de uma página (nada decodificado ainda)."""

    xref_fundo: int
    xref_cima: int
    xref_mascara: int
    tipo_mascara: str                  # "smask" ou "estencil" (/Mask com ImageMask)
    filtro_mascara: str                # quase sempre "JBIG2Decode"
    tamanho_fundo: tuple[int, int]     # (largura, altura) em pixels
    tamanho_cima: tuple[int, int]
    rotacao: int                       # a /Rotate da página: 0, 90, 180 ou 270


@dataclass
class ResumoDasCamadas:
    """Quantas páginas do PDF têm a montagem em camadas."""

    paginas: int
    com_camadas: list[int] = field(default_factory=list)   # índices, a partir de 0

    @property
    def fracao(self) -> float:
        return len(self.com_camadas) / self.paginas if self.paginas else 0.0


# Um "pedaço" do conteúdo da página (PDF 32000, seção 7.2). O texto entre
# parênteses é tratado à parte (_pular_texto), porque pode ter parênteses
# dentro. Imagem embutida no conteúdo (BI ... ID ... EI) não é tratada: a
# página cai em "sem camadas", que é o lado seguro.
_PEDACO = re.compile(
    rb"[\x00\t\n\x0c\r ]+"                    # espaço
    rb"|%[^\r\n]*"                             # comentário
    rb"|/[^\x00\t\n\x0c\r ()<>\[\]{}/%]*"     # nome
    rb"|<<|>>"                                 # dicionário
    rb"|<[^<>]*>"                              # texto em hexadecimal
    rb"|[\[\]{}]"                              # vetor
    rb"|\("                                    # começo de texto
    rb"|[^\x00\t\n\x0c\r ()<>\[\]{}/%]+"       # número ou operador
)
_ESPACOS = b"\x00\t\n\x0c\r "
_IDENTIDADE = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _pular_texto(dados: bytes, pos: int) -> int | None:
    """Pula um (texto) com parênteses aninhados e barras de escape. Devolve a
    posição logo depois do ')' que fecha, ou None se o texto não fecha."""
    nivel, n = 1, len(dados)
    while pos < n:
        c = dados[pos]
        if c == 0x5C:          # barra invertida: o próximo caractere não conta
            pos += 2
            continue
        if c == 0x28:
            nivel += 1
        elif c == 0x29:
            nivel -= 1
            if nivel == 0:
                return pos + 1
        pos += 1
    return None


def _concatenar(m: tuple, ctm: tuple) -> tuple:
    """m seguido de ctm (o 'cm' do PDF: CTM nova = m x CTM antiga)."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = ctm
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


def imagens_desenhadas(conteudo: bytes) -> list[tuple[str, tuple]] | None:
    """Os 'Do' do conteúdo da página, na ordem em que são desenhados, cada um
    com a matriz em vigor (nome sem a barra, (a, b, c, d, e, f)).

    Só entende q, Q, cm e Do - é o que decide onde uma imagem cai. Não abre
    imagem nenhuma. Devolve None se o conteúdo tiver algo que este leitor
    simples não acompanha (imagem embutida, texto sem fim): a página vira
    "sem camadas" e o programa segue como hoje.
    """
    pos, n = 0, len(conteudo)
    ctm = _IDENTIDADE
    pilha: list[tuple] = []
    operandos: list = []
    desenhos: list[tuple[str, tuple]] = []
    while pos < n:
        achado = _PEDACO.match(conteudo, pos)
        if achado is None:
            return None
        pedaco = achado.group()
        pos = achado.end()
        primeiro = pedaco[0]
        if primeiro in _ESPACOS or primeiro == 0x25:          # espaço ou %
            continue
        if pedaco == b"(":
            fim = _pular_texto(conteudo, pos)
            if fim is None:
                return None
            pos = fim
            operandos.append(None)
            continue
        if primeiro == 0x2F:                                   # /nome
            operandos.append(pedaco[1:])
            continue
        if primeiro in b"<>[]{}":
            operandos.append(None)
            continue
        try:
            operandos.append(float(pedaco))
            continue
        except ValueError:
            pass
        # é um operador
        if pedaco == b"q":
            pilha.append(ctm)
        elif pedaco == b"Q":
            if pilha:
                ctm = pilha.pop()
        elif pedaco == b"cm":
            numeros = operandos[-6:]
            if len(numeros) != 6 or not all(isinstance(v, float) for v in numeros):
                return None
            ctm = _concatenar(tuple(numeros), ctm)
        elif pedaco == b"Do":
            if not operandos or not isinstance(operandos[-1], bytes):
                return None
            desenhos.append((operandos[-1].decode("latin-1"), ctm))
        elif pedaco == b"BI":
            return None
        operandos.clear()
    return desenhos


def _xref_de(valor: tuple[str, str]) -> int:
    """('xref', '14 0 R') -> 14; qualquer outra coisa -> 0."""
    if valor[0] != "xref":
        return 0
    try:
        return int(valor[1].split()[0])
    except (ValueError, IndexError):
        return 0


def _tipo_da_mascara(doc: fitz.Document, xref_imagem: int, xref_mascara: int) -> str | None:
    """"smask" (SMask de 1 bit), "estencil" (/Mask para uma ImageMask) ou None
    (máscara de 8 bits, máscara de cor, outra coisa: não é a montagem do IA)."""
    if _xref_de(doc.xref_get_key(xref_imagem, "SMask")) == xref_mascara:
        if doc.xref_get_key(xref_mascara, "BitsPerComponent") == ("int", "1"):
            return "smask"
        return None
    if _xref_de(doc.xref_get_key(xref_imagem, "Mask")) == xref_mascara:
        if doc.xref_get_key(xref_mascara, "ImageMask") == ("bool", "true"):
            return "estencil"
    return None


def _cobre_a_pagina(ctm: tuple, largura_pt: float, altura_pt: float) -> bool:
    """A imagem (o quadrado 0..1 levado pela matriz) cobre a página inteira, de
    pé (sem giro nem espelho), com FOLGA_DA_CAIXA?"""
    a, b, c, d, e, f = ctm
    if a <= 0 or d <= 0:
        return False
    if abs(b) > 1e-3 * a or abs(c) > 1e-3 * d:
        return False
    folga_x, folga_y = FOLGA_DA_CAIXA * largura_pt, FOLGA_DA_CAIXA * altura_pt
    return (abs(e) <= folga_x and abs(e + a - largura_pt) <= folga_x
            and abs(f) <= folga_y and abs(f + d - altura_pt) <= folga_y)


def _reconhecer(doc: fitz.Document, indice: int) -> CamadasDaPagina | None:
    """O miolo de camadas_da_pagina, já dentro da tranca do MuPDF."""
    pagina = doc[indice]
    imagens = pagina.get_images(full=True)
    if len(imagens) != 2:
        return None
    com_mascara = [i for i in imagens if i[1]]
    sem_mascara = [i for i in imagens if not i[1]]
    if len(com_mascara) != 1 or len(sem_mascara) != 1:
        return None
    cima, fundo = com_mascara[0], sem_mascara[0]
    # (xref, smask, largura, altura, bpc, espaço de cor, alt., nome, filtro, referenciador)
    if cima[2] < fundo[2] or cima[3] < fundo[3]:
        return None
    tipo = _tipo_da_mascara(doc, cima[0], cima[1])
    if tipo is None:
        return None

    desenhos = imagens_desenhadas(pagina.read_contents())
    if not desenhos or len(desenhos) != 2:
        return None
    nomes = [nome for nome, _ in desenhos]
    if nomes != [fundo[7], cima[7]]:   # fundo primeiro, camada de cima depois
        return None

    # Só a página "de papel": caixa de mídia a partir de (0, 0) e sem recorte
    # diferente dela. Outra combinação é rara e cai em "sem camadas".
    midia, recorte = pagina.mediabox, pagina.cropbox
    folga = 0.5
    if abs(midia.x0) > folga or abs(midia.y0) > folga:
        return None
    if (abs(recorte.x0 - midia.x0) > folga or abs(recorte.y0 - midia.y0) > folga
            or abs(recorte.x1 - midia.x1) > folga or abs(recorte.y1 - midia.y1) > folga):
        return None
    if not all(_cobre_a_pagina(ctm, midia.width, midia.height) for _, ctm in desenhos):
        return None
    rotacao = pagina.rotation % 360
    if rotacao not in (0, 90, 180, 270):
        return None

    filtro = doc.xref_get_key(cima[1], "Filter")
    return CamadasDaPagina(
        xref_fundo=fundo[0], xref_cima=cima[0], xref_mascara=cima[1],
        tipo_mascara=tipo, filtro_mascara=filtro[1].lstrip("/") if filtro[0] == "name" else "",
        tamanho_fundo=(int(fundo[2]), int(fundo[3])),
        tamanho_cima=(int(cima[2]), int(cima[3])), rotacao=rotacao)


def camadas_da_pagina(doc: fitz.Document, indice: int) -> CamadasDaPagina | None:
    """Esta página tem as camadas do Internet Archive? None = não.

    Critério (docs/pesquisa/fase1-1.1, seção 5.1): exatamente duas imagens;
    a primeira desenhada sem máscara (fundo) e a segunda com máscara de 1 bit
    (SMask de 1 bit ou /Mask de estêncil); as duas cobrem a página inteira, de
    pé; a de cima tem pelo menos o tamanho do fundo. Não exige JBIG2, nem o
    nome do produtor (o Siebmacher diz "Samsung Electronics").

    Não decodifica imagem nenhuma: lê a lista de imagens e o conteúdo da
    página (milissegundos). Qualquer erro vira None: na dúvida, segue como hoje.
    """
    try:
        with _TRANCA:
            return _reconhecer(doc, indice)
    except Exception:  # noqa: BLE001 - PDF estranho não derruba nada
        return None


def resumo_do_pdf(doc: fitz.Document) -> ResumoDasCamadas:
    """Todas as páginas do PDF, uma por uma, sem decodificar nada."""
    resumo = ResumoDasCamadas(paginas=doc.page_count)
    for indice in range(doc.page_count):
        if camadas_da_pagina(doc, indice) is not None:
            resumo.com_camadas.append(indice)
    return resumo


def pdf_tem_camadas(doc_ou_caminho, amostra: int = 12) -> bool:
    """Este PDF é dos que vêm com camadas? (para o botão de ligar e desligar
    nascer ligado - regra 8). Olha até `amostra` páginas espalhadas pelo livro
    e diz sim quando pelo menos metade delas tem a montagem. A decisão de cada
    página continua sendo de camadas_da_pagina, na hora de processar."""
    if isinstance(doc_ou_caminho, (str, Path)):
        with fitz.open(doc_ou_caminho) as doc:
            return pdf_tem_camadas(doc, amostra)
    doc = doc_ou_caminho
    total = doc.page_count
    if total <= 0:
        return False
    if total <= amostra:
        indices = list(range(total))
    else:
        indices = sorted({round(i * (total - 1) / (amostra - 1)) for i in range(amostra)})
    com = sum(1 for i in indices if camadas_da_pagina(doc, i) is not None)
    return com * 2 >= len(indices)


# ==========================================================================
# (b) montar a página sem o fundo
# ==========================================================================


@dataclass
class CamadasLidas:
    """As camadas de UMA página, decodificadas e já de pé.

    cima: BGR uint8 já multiplicada pela transparência (fora da máscara = 0),
          no tamanho de saída. Multiplicar ANTES de reduzir é o que impede o
          lixo de fora da máscara de manchar a cor da letra na prévia.
    alfa: uint8 no tamanho de saída; 255 = a camada de cima aparece.
    fundo: BGR uint8 na resolução em que veio (ou reduzido ao tamanho de saída,
          se era maior). compor() o amplia faixa por faixa.
    largura_pt, altura_pt: o tamanho da página como ela é mostrada (já girada).
    """

    cima: np.ndarray
    alfa: np.ndarray
    fundo: np.ndarray
    dpi: float
    largura_pt: float
    altura_pt: float

    @property
    def largura(self) -> int:
        return int(self.cima.shape[1])

    @property
    def altura(self) -> int:
        return int(self.cima.shape[0])

    def reduzir(self, largura: int, altura: int) -> "CamadasLidas":
        """As mesmas camadas num tamanho só, fundo inclusive (para o detector
        e as medidas, que comparam fundo e máscara pixel a pixel)."""
        return CamadasLidas(
            cima=_redimensionar(self.cima, largura, altura),
            alfa=_redimensionar(self.alfa, largura, altura),
            fundo=_redimensionar(self.fundo, largura, altura),
            dpi=largura / (self.largura_pt / 72.0),
            largura_pt=self.largura_pt, altura_pt=self.altura_pt)

    def no_dpi(self, dpi: float | None) -> "CamadasLidas":
        """As camadas no tamanho de saída do DPI pedido (None = como estão).
        O fundo só é reduzido se for maior que a saída; menor, ele fica como
        veio e compor() o amplia faixa por faixa."""
        largura, altura = _tamanho_de_saida(self.largura_pt, self.altura_pt,
                                            (self.largura, self.altura), dpi)
        if (largura, altura) == (self.largura, self.altura):
            return self
        fundo = self.fundo
        if fundo.shape[1] > largura or fundo.shape[0] > altura:
            fundo = _redimensionar(fundo, largura, altura)
        return CamadasLidas(
            cima=_redimensionar(self.cima, largura, altura),
            alfa=_redimensionar(self.alfa, largura, altura),
            fundo=fundo, dpi=largura / (self.largura_pt / 72.0),
            largura_pt=self.largura_pt, altura_pt=self.altura_pt)


def _redimensionar(img: np.ndarray, largura: int, altura: int) -> np.ndarray:
    if img.shape[1] == largura and img.shape[0] == altura:
        return img
    reduzindo = largura < img.shape[1] or altura < img.shape[0]
    return cv2.resize(img, (largura, altura),
                      interpolation=cv2.INTER_AREA if reduzindo else cv2.INTER_LINEAR)


def _ler_bgr(doc: fitz.Document, xref: int) -> np.ndarray:
    """Uma imagem do PDF em BGR uint8 (cinza, CMYK e transparência resolvidos)."""
    pix = fitz.Pixmap(doc, xref)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.colorspace is None or pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    dados = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    img = cv2.cvtColor(dados, cv2.COLOR_RGB2BGR)   # copia: sobrevive ao pixmap
    del pix, dados
    return img


def _ler_alfa(doc: fitz.Document, xref_mascara: int) -> np.ndarray:
    """A máscara como o MuPDF a usa para desenhar: 255 = a camada de cima
    aparece, 0 = não aparece.

    Vale para as duas formas: na SMask o MuPDF já aplica o /Decode (a Rhetorica
    tem /Decode [1 0]); no estêncil ele já inverte o "1 = escondido" da
    especificação. Conferido contra o desenho do próprio MuPDF (tests/
    test_camadas.py, sintético e páginas do gabarito). Arriscado mudar.
    """
    pix = fitz.Pixmap(doc, xref_mascara)
    dados = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    alfa = np.ascontiguousarray(dados[:, :, -1])
    del pix, dados
    return alfa


def _de_pe(img: np.ndarray, rotacao: int) -> np.ndarray:
    """Gira como o MuPDF mostra a página: /Rotate 90 = um quarto de volta no
    sentido do relógio."""
    voltas = {0: 0, 90: -1, 180: 2, 270: 1}[rotacao]
    return np.ascontiguousarray(np.rot90(img, voltas)) if voltas else img


def _tamanho_de_saida(largura_pt: float, altura_pt: float, nativo: tuple[int, int],
                      dpi: float | None) -> tuple[int, int]:
    """(largura, altura) da página montada: a da camada de cima (dpi=None) ou a
    do DPI pedido; nunca acima de MAX_PIXELS (o mesmo teto de pdf_io)."""
    if dpi is None:
        largura, altura = nativo
    else:
        largura = max(1, round(largura_pt * dpi / 72.0))
        altura = max(1, round(altura_pt * dpi / 72.0))
    if largura * altura > MAX_PIXELS:
        fator = (MAX_PIXELS / (largura * altura)) ** 0.5
        largura, altura = max(1, int(largura * fator)), max(1, int(altura * fator))
    return largura, altura


def ler_camadas(doc: fitz.Document, indice: int, dpi: float | None = None,
                camadas: CamadasDaPagina | None = None) -> CamadasLidas | None:
    """Decodifica as camadas da página, de pé, no tamanho de saída.

    dpi=None: a resolução da camada de cima (400 a 600 DPI nos quatro livros).
    Com dpi, é o mesmo que ler_camadas(...).no_dpi(dpi). None se a página não
    tiver as camadas.
    """
    camadas = camadas or camadas_da_pagina(doc, indice)
    if camadas is None:
        return None
    with _TRANCA:
        pagina = doc[indice]
        largura_pt, altura_pt = pagina.rect.width, pagina.rect.height   # já girada
        try:
            cima = _ler_bgr(doc, camadas.xref_cima)
            alfa = _ler_alfa(doc, camadas.xref_mascara)
            fundo = _ler_bgr(doc, camadas.xref_fundo)
        finally:
            # Esvazia o armazém do MuPDF, como pdf_io.pagina_para_array: sem
            # isso ele guarda as imagens decodificadas de cada página já lida.
            fitz.TOOLS.store_shrink(100)

    cima, alfa, fundo = (_de_pe(x, camadas.rotacao) for x in (cima, alfa, fundo))
    if alfa.shape[:2] != cima.shape[:2]:
        alfa = cv2.resize(alfa, (cima.shape[1], cima.shape[0]), interpolation=cv2.INTER_LINEAR)

    # Multiplica pela transparência ANTES de reduzir (ver CamadasLidas).
    canais = [cv2.multiply(canal, alfa, scale=1.0 / 255.0) for canal in cv2.split(cima)]
    cima = cv2.merge(canais)
    del canais

    # Na resolução da camada de cima (com o teto de MAX_PIXELS), e daí para o
    # DPI pedido.
    largura, altura = _tamanho_de_saida(largura_pt, altura_pt,
                                        (cima.shape[1], cima.shape[0]), None)
    if fundo.shape[1] > largura or fundo.shape[0] > altura:
        fundo = _redimensionar(fundo, largura, altura)
    nativas = CamadasLidas(cima=_redimensionar(cima, largura, altura),
                           alfa=_redimensionar(alfa, largura, altura),
                           fundo=fundo, dpi=largura / (largura_pt / 72.0),
                           largura_pt=largura_pt, altura_pt=altura_pt)
    del cima, alfa
    return nativas.no_dpi(dpi)


def _faixa(img: np.ndarray, largura: int, altura: int, y0: int, y1: int,
           x0: int = 0, x1: int | None = None) -> np.ndarray:
    """O retângulo [y0:y1, x0:x1] de img ampliada (bilinear) para largura x
    altura, sem ampliar a imagem inteira. Mesma geometria do cv2.resize
    (centro do pixel)."""
    x1 = largura if x1 is None else x1
    if img.shape[1] == largura and img.shape[0] == altura:
        return img[y0:y1, x0:x1]
    alt_src, larg_src = img.shape[:2]
    xs = (np.arange(x0, x1, dtype=np.float32) + 0.5) * (larg_src / largura) - 0.5
    ys = (np.arange(y0, y1, dtype=np.float32) + 0.5) * (alt_src / altura) - 0.5
    mapa_x = np.ascontiguousarray(np.broadcast_to(xs[None, :], (y1 - y0, x1 - x0)))
    mapa_y = np.ascontiguousarray(np.broadcast_to(ys[:, None], (y1 - y0, x1 - x0)))
    return cv2.remap(img, mapa_x, mapa_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def compor(lidas: CamadasLidas, peso_figura: np.ndarray | None = None) -> np.ndarray:
    """Monta a página: camada de cima + (fora dela) branco ou fundo.

    peso_figura (0 a 1, em qualquer tamanho; é ampliado): onde é 1 fica o fundo
    (a página como o PDF desenha); onde é 0 fica branco. None = branco em tudo.

        saída = cima + (1 - alfa) x (branco + peso x (fundo - branco))

    Nenhum pixel é inventado: cada um vem da camada de cima, do fundo ou é
    branco. Feito em faixas (LINHAS_POR_FAIXA) para a memória não passar de uma
    página.
    """
    largura, altura = lidas.largura, lidas.altura
    saida = np.empty((altura, largura, 3), np.uint8)
    for y0 in range(0, altura, LINHAS_POR_FAIXA):
        y1 = min(altura, y0 + LINHAS_POR_FAIXA)
        cima, alfa = lidas.cima[y0:y1], lidas.alfa[y0:y1]
        # Primeiro tudo com branco embaixo: conta inteira e exata (cima <= alfa
        # depois da multiplicação, então não estoura).
        saida[y0:y1] = cv2.add(cima, cv2.merge([255 - alfa] * 3))
        if peso_figura is None:
            continue
        peso = _faixa(peso_figura, largura, altura, y0, y1)
        colunas = np.flatnonzero(np.any(peso > 1e-3, axis=0))
        if colunas.size == 0:
            continue
        # Depois, só nos trechos de colunas com figura, o fundo por baixo (em
        # ponto flutuante, e só ali: duas molduras finas de cima a baixo não
        # podem custar a página inteira).
        quebras = np.flatnonzero(np.diff(colunas) > 1)
        inicios = np.concatenate(([colunas[0]], colunas[quebras + 1]))
        fins = np.concatenate((colunas[quebras], [colunas[-1]])) + 1
        for x0, x1 in zip(inicios.tolist(), fins.tolist()):
            fundo = _faixa(lidas.fundo, largura, altura, y0, y1, x0, x1).astype(np.float32)
            p = np.clip(peso[:, x0:x1].astype(np.float32), 0.0, 1.0)[:, :, None]
            base = 255.0 + p * (fundo - 255.0)
            transparencia = (1.0 - alfa[:, x0:x1].astype(np.float32) / 255.0)[:, :, None]
            saida[y0:y1, x0:x1] = np.clip(cima[:, x0:x1].astype(np.float32)
                                          + transparencia * base + 0.5, 0, 255).astype(np.uint8)
    return saida


# --- o detector de figuras (a emenda do item 1.2) ----------------------------------

DetectorDeFiguras = Callable[[np.ndarray], np.ndarray]


def figuras_pelo_detector_atual(img: np.ndarray) -> np.ndarray:
    """Onde há gravura, foto ou pintura, de 0 a 1, no tamanho de img (BGR).

    Usa o detector que o programa já tem (core/detectar_regioes.py: modelo de
    layout + cor + tinta), a zona "gravura" com a borda suavizada. O item 1.2
    troca isto pelo seletor do ScanTailor: basta outra função com a mesma
    assinatura em DETECTOR_DE_FIGURAS.
    """
    from core.detectar_regioes import detectar
    from core.selecao import GRAVURA

    altura, largura = img.shape[:2]
    selecao = detectar(img)
    return selecao.peso(altura, largura, GRAVURA).astype(np.float32)


# Troque aqui (ou passe detector_de_figuras= em tirar_fundo) para usar outro
# detector. Recebe a página como o PDF desenha, em BGR, a DPI_DA_ANALISE;
# devolve float32 de 0 a 1 do mesmo tamanho.
DETECTOR_DE_FIGURAS: DetectorDeFiguras = figuras_pelo_detector_atual


# --- decidir o que fica -------------------------------------------------------------


@dataclass
class PaginaSemFundo:
    """O que tirar_fundo devolve."""

    imagem: np.ndarray | None      # BGR uint8; None = seguir como hoje
    situacao: str                  # SEM_CAMADAS, FUNDO_TIRADO ou DEIXADA_INTACTA
    explicacao: str                # em português, para a tela e o relatório
    dpi: float = 0.0
    zonas_de_figura: int = 0       # quantas o detector achou
    zonas_mantidas: int = 0        # quantas ficaram como o PDF desenha
    medidas: dict = field(default_factory=dict)   # números crus, para o relatório
    conferir: bool = False         # fundo tirado, mas algum traço pode ter ido junto


@dataclass
class _Fundo:
    """As medidas do fundo, no tamanho da análise."""

    papel: float               # cinza do papel (ver _cor_do_papel)
    livre: np.ndarray          # longe da tinta de cima
    tom_livre: np.ndarray      # tom de figura E longe da tinta: foto (rede de segurança)
    so_no_fundo: np.ndarray    # tom de figura onde a camada de cima não cobre (zonas)


def _cor_do_papel(cinza: np.ndarray, lab: np.ndarray, livre: np.ndarray,
                  peso: np.ndarray) -> tuple[float, float, float]:
    """(cinza, a, b) do papel: o tom MAIS COMUM do fundo livre (o pico do
    histograma) na MARGEM da página (a faixa de FAIXA_DA_BORDA junto às
    bordas); se a margem tem pouco fundo livre, fora das zonas de figura; se
    nem isso, na página toda.

    O pico, e não a média nem um percentil: papel é um tom só, espalhado; foto
    e mancha espalham tons. A margem, porque papel é o que está EM VOLTA do
    conteúdo. Na Pesel, a foto do linho (clara) e o cartão pardo em volta dela
    ocupam quase o mesmo tanto da página, e o pico da página inteira caía ora
    num, ora noutro (mudou só de trocar a resolução da análise, 28/09/2026);
    quando caía no linho, o cartão virava "figura", saía com a borda (ver
    _sem_a_borda) e o linho perdia o tom - a foto apagada. Na margem o pico é
    o cartão, sempre. Na Rhetorica 73 a mancha d'água cobre quase metade da
    página: o pico cai no papel limpo ou na mancha, e com TOM_DE_FIGURA = 60 dá
    o mesmo (os dois ficam a uns 30 níveis um do outro). Se a margem for o
    preto de fora do livro, o "papel" sai escuro e a página fica intacta por
    PAPEL_ESCURO_DEMAIS: o lado seguro.
    """
    altura, largura = livre.shape
    lado = max(1, int(FAIXA_DA_BORDA * min(altura, largura)))
    margem = np.zeros_like(livre)
    margem[:lado], margem[-lado:], margem[:, :lado], margem[:, -lado:] = True, True, True, True
    # Na margem, o preto de fora do livro (fundo do scanner) não é papel.
    margem &= cinza >= PRETO_DO_SCANNER
    fora = livre & (peso < 0.5)
    minimo = FORA_DAS_ZONAS_PARA_O_PAPEL * livre.size
    if int((livre & margem).sum()) >= minimo:
        base = livre & margem
    elif int(fora.sum()) >= minimo:
        base = fora
    else:
        base = livre
    contagem = np.bincount(np.clip(cinza[base], 0, 255).astype(np.intp).ravel(),
                           minlength=256).astype(np.float64)
    contagem = np.convolve(contagem, np.ones(7) / 7.0, mode="same")
    papel = float(np.argmax(contagem))
    banda = base & (np.abs(cinza - papel) < 15)
    if int(banda.sum()) < 100:
        banda = base
    a0 = float(np.median(lab[:, :, 1][banda]))
    b0 = float(np.median(lab[:, :, 2][banda]))
    return papel, a0, b0


def _medir_fundo(pequena: CamadasLidas, peso: np.ndarray) -> _Fundo:
    """O que o fundo tem que a camada de cima não tem.

    "Tom de figura" = pixel do fundo que se afasta do papel: TOM_DE_FIGURA
    níveis de cinza (mais escuro ou mais claro) ou COR_DE_FIGURA de cor.
    Duas medidas, para duas perguntas:

    - "tinta só no fundo" (so_no_fundo): tom de figura onde a camada de cima
      não cobre. Pega a hachura fina que a máscara do Internet Archive deixou
      de fora, colada na hachura que ela pegou. As letras "fantasma" ficam
      exatamente embaixo da tinta de cima e são claras demais para contar.
      Decide as ZONAS de figura (_zonas_mantidas).
    - "tom longe da tinta" (tom_livre): só o que está a alguns pixels de
      qualquer tinta de cima. É o tom de foto, sem a hachura. Decide a REDE DE
      SEGURANÇA (_figura_esquecida), que não pode disparar em toda página de
      texto com um pouco de tinta perdida.
    """
    fundo = _redimensionar(pequena.fundo, pequena.largura, pequena.altura)
    cinza = cv2.cvtColor(fundo, cv2.COLOR_BGR2GRAY).astype(np.int16)
    tinta = (pequena.alfa > 12).astype(np.uint8)
    lado = max(3, int(round(pequena.dpi / 30)) | 1)     # 5 pixels a 150 DPI
    livre = cv2.dilate(tinta, np.ones((lado, lado), np.uint8)) == 0
    if int(livre.sum()) < 100:
        vazio = np.zeros_like(livre)
        return _Fundo(255.0, livre, vazio, vazio)
    lab = cv2.cvtColor(fundo, cv2.COLOR_BGR2LAB).astype(np.int16)
    papel, a0, b0 = _cor_do_papel(cinza, lab, livre, peso)
    fora_da_cor = ((lab[:, :, 1] - a0) ** 2 + (lab[:, :, 2] - b0) ** 2
                   > COR_DE_FIGURA ** 2)

    tom = (np.abs(cinza - papel) > TOM_DE_FIGURA) | fora_da_cor
    return _Fundo(papel, livre, livre & tom,
                  _sem_a_borda(tom & (pequena.alfa < ALFA_QUE_NAO_COBRE)))


def _manchas_da_borda(rotulos: np.ndarray, caixas: np.ndarray) -> np.ndarray:
    """Para cada rótulo de connectedComponentsWithStats, se a mancha é fundo
    de scanner ou borda da folha: encosta na borda da imagem E tem pelo menos
    METADE_NA_FAIXA dos pixels na faixa junto às bordas (ver FAIXA_DA_BORDA).
    O rótulo 0 (o que não é mancha) sai True, para ser descartado junto."""
    altura, largura = rotulos.shape
    margem_x, margem_y = BORDA_DA_IMAGEM * largura, BORDA_DA_IMAGEM * altura
    x, y, w, h, area = (caixas[:, i] for i in range(5))
    encosta = ((x <= margem_x) | (y <= margem_y)
               | (x + w >= largura - margem_x) | (y + h >= altura - margem_y))
    lado = max(1, int(FAIXA_DA_BORDA * min(altura, largura)))
    faixa = np.zeros((altura, largura), bool)
    faixa[:lado], faixa[-lado:], faixa[:, :lado], faixa[:, -lado:] = True, True, True, True
    na_faixa = np.bincount(rotulos[faixa].ravel(), minlength=len(caixas))
    da_borda = encosta & (na_faixa >= METADE_NA_FAIXA * np.maximum(area, 1))
    da_borda[0] = True
    return da_borda


def _sem_a_borda(mascara: np.ndarray) -> np.ndarray:
    """A máscara sem as manchas de fundo de scanner e borda da folha."""
    if not mascara.any():
        return mascara
    _, rotulos, caixas, _ = cv2.connectedComponentsWithStats(
        mascara.astype(np.uint8), connectivity=8)
    return mascara & ~_manchas_da_borda(rotulos, caixas)[rotulos]


def _zonas_mantidas(peso: np.ndarray, fundo: _Fundo
                    ) -> tuple[np.ndarray, int, int, list[float]]:
    """Das zonas de figura, só as que têm "tinta só no fundo".

    Devolve (peso só das zonas mantidas, zonas achadas, zonas mantidas, a
    fração de tinta só no fundo de cada zona). Uma zona sem ela tem tudo na
    camada de cima (tabela, esquema, diagrama) e sai branca como o resto; uma
    zona com ela (foto, xilogravura, moldura grossa que a máscara furou) fica
    como o PDF desenha, com o papel dela como está.
    """
    apoio = (peso > 0.02).astype(np.uint8)
    quantas, rotulos, caixas, _ = cv2.connectedComponentsWithStats(apoio, connectivity=8)
    mantido = np.zeros_like(peso, dtype=np.float32)
    achadas = mantidas = 0
    fracoes: list[float] = []
    for k in range(1, quantas):
        x, y, w, h = caixas[k, :4]
        janela = (slice(y, y + h), slice(x, x + w))
        zona = (rotulos[janela] == k) & (peso[janela] > 0.5)
        if not zona.any():
            continue
        achadas += 1
        fracao = int((fundo.so_no_fundo[janela] & zona).sum()) / int(zona.sum())
        fracoes.append(round(fracao, 4))
        if fracao >= TINTA_SO_NO_FUNDO:
            mantidas += 1
            dentro = rotulos[janela] == k
            mantido[janela][dentro] = peso[janela][dentro]
    return mantido, achadas, mantidas, fracoes


def _figura_esquecida(tom: np.ndarray, mantido: np.ndarray) -> float:
    """A maior área com tom de figura no fundo fora das zonas mantidas, em
    fração da página, sem contar fundo de scanner e borda da folha (ver
    _manchas_da_borda). 0 = nenhuma."""
    fora = (tom & (mantido < 0.5)).astype(np.uint8)
    if not fora.any():
        return 0.0
    altura, largura = fora.shape
    lado = max(3, int(0.02 * min(altura, largura)) | 1)
    junto = cv2.morphologyEx(fora, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
    quantas, rotulos, caixas, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    da_borda = _manchas_da_borda(rotulos, caixas)
    maior = 0.0
    for k in range(1, quantas):
        if da_borda[k]:
            continue
        x, y, w, h, area = caixas[k]
        janela = (slice(y, y + h), slice(x, x + w))
        com_tom = int(fora[janela][rotulos[janela] == k].sum())
        if com_tom < DENSIDADE_DA_FIGURA_ESQUECIDA * area:
            continue
        maior = max(maior, float(area) / (altura * largura))
    return maior


def _tinta_perdida(perdida: np.ndarray) -> float:
    """Que fração da página tem traço que só existia no fundo (e sai com ele).
    O fundo de scanner e a borda da folha já saíram em _medir_fundo: o preto
    de fora do livro no Siebmacher fica no fundo e não é traço de ninguém."""
    return float(perdida.mean())


def tirar_fundo(doc: fitz.Document, indice: int, dpi: float | None = None,
                detector_de_figuras: DetectorDeFiguras | None = None) -> PaginaSemFundo:
    """Monta a página `indice` sem o fundo (ver o topo do arquivo).

    dpi=None: na resolução da camada de cima. Devolve imagem None quando não se
    aplica (SEM_CAMADAS) ou quando tirar o fundo apagaria uma figura que o
    detector não marcou (DEIXADA_INTACTA): nos dois casos quem chamou segue
    como hoje (pdf_io.pagina_para_array).
    """
    camadas = camadas_da_pagina(doc, indice)
    if camadas is None:
        return PaginaSemFundo(None, SEM_CAMADAS,
                              "Esta página não vem em camadas: segue como hoje.")
    nativas = ler_camadas(doc, indice, None, camadas)
    detector = detector_de_figuras or DETECTOR_DE_FIGURAS

    # A análise, pequena: a página como o PDF desenha (é nela que a foto
    # aparece inteira para o detector) e as medidas do fundo. Sempre a
    # DPI_DA_ANALISE, tirada da resolução da camada de cima, qualquer que seja
    # o DPI de saída: a prévia (110 DPI) e o PDF final (300 DPI) têm de decidir
    # igual. Medido em 28/09: com a análise no DPI de saída, o Palatino 116 tinha
    # a gravura mantida a 150 DPI e perdida a 100 DPI.
    fator = min(1.0, DPI_DA_ANALISE / nativas.dpi)
    pequena = nativas.reduzir(max(1, round(nativas.largura * fator)),
                              max(1, round(nativas.altura * fator)))
    lidas = nativas.no_dpi(dpi)
    del nativas
    como_o_pdf = compor(pequena, np.ones((pequena.altura, pequena.largura), np.float32))
    try:
        peso = np.asarray(detector(como_o_pdf), dtype=np.float32)
        if peso.shape != (pequena.altura, pequena.largura):
            peso = cv2.resize(peso, (pequena.largura, pequena.altura),
                              interpolation=cv2.INTER_LINEAR)
    except Exception as erro:  # noqa: BLE001 - sem detector, não arrisca a figura
        return PaginaSemFundo(None, DEIXADA_INTACTA,
                              "O detector de figuras falhou nesta página; ela fica como "
                              "está, para não apagar uma figura.", lidas.dpi,
                              medidas={"erro_do_detector": f"{type(erro).__name__}: {erro}"})

    fundo = _medir_fundo(pequena, peso)
    livre = float(fundo.livre.mean())
    if livre < PAGINA_COBERTA_PELA_MASCARA:
        return PaginaSemFundo(
            None, DEIXADA_INTACTA,
            "A camada de cima cobre quase a página toda (capa, tecido, objeto "
            "fotografado); ela fica como está.", lidas.dpi,
            medidas={"fundo_livre": round(livre, 3)})
    if fundo.papel < PAPEL_ESCURO_DEMAIS:
        return PaginaSemFundo(
            None, DEIXADA_INTACTA,
            "O fundo desta página é escuro demais para ser papel (capa, cartão); "
            "ela fica como está.", lidas.dpi,
            medidas={"papel": round(fundo.papel, 1), "fundo_livre": round(livre, 3)})
    mantido, achadas, mantidas, fracoes = _zonas_mantidas(peso, fundo)
    esquecida = _figura_esquecida(fundo.tom_livre, mantido)
    cobertura = float(mantido.mean())
    perdida = _tinta_perdida(fundo.so_no_fundo & (mantido < 0.5))
    medidas = {"papel": round(fundo.papel, 1), "fundo_livre": round(livre, 3),
               "tinta_so_no_fundo_por_zona": fracoes,
               "zonas_mantidas_cobrem": round(cobertura, 3),
               # o que ainda some com o fundo, fora das zonas mantidas (fração
               # da página): hachura de figura que o detector não marcou,
               # fio grosso furado pela máscara, sujeira escura
               "tinta_so_no_fundo_fora_das_zonas": round(perdida, 4),
               "figura_fora_das_zonas": round(esquecida, 4),
               "tamanho_analise": [pequena.largura, pequena.altura]}
    if esquecida >= AREA_DE_FIGURA_ESQUECIDA:
        return PaginaSemFundo(
            None, DEIXADA_INTACTA,
            "O fundo tem uma figura (foto ou pintura) fora das zonas de "
            "figura; a página fica como está, para não apagá-la.",
            lidas.dpi, achadas, mantidas, medidas)
    if cobertura >= PAGINA_INTEIRA_E_FIGURA:
        # O detector marcou a página inteira como figura, e ela tem tinta só no
        # fundo (Palatino 5, com o detector de hoje): montar daria a própria
        # página. Dizer isso com todas as letras é melhor que fingir que tirou.
        return PaginaSemFundo(
            None, DEIXADA_INTACTA,
            "A página inteira é figura com traço ou tom que só existe no fundo; "
            "ela fica como está, para não quebrar a figura.",
            lidas.dpi, achadas, mantidas, medidas)

    imagem = compor(lidas, mantido if mantidas else None)
    if mantidas:
        explicacao = (f"Fundo tirado; {mantidas} figura(s) com traço ou tom só no "
                      "fundo ficaram como o PDF mostra.")
    else:
        explicacao = "Fundo tirado: papel branco, letra e figuras da camada de cima."
    conferir = perdida >= CONFERIR_TINTA_PERDIDA
    if conferir:
        explicacao += (" Confira: parte do traço desta página (moldura ou gravura) "
                       "só existia no fundo e pode ter ficado mais fraca.")
    return PaginaSemFundo(imagem, FUNDO_TIRADO, explicacao, lidas.dpi,
                          achadas, mantidas, medidas, conferir)


# --- a porta da conferência ---------------------------------------------------------


def tirar_fundo_do_pdf(caminho_pdf, imagem_antes: np.ndarray | None = None,
                       detector_de_figuras: DetectorDeFiguras | None = None) -> np.ndarray:
    """Para conferencia.py --funcao core.camadas:tirar_fundo_do_pdf.

    Recebe o PDF de uma página do gabarito (com as camadas originais) e devolve
    a página sem o fundo, na resolução da camada de cima. Página deixada
    intacta volta como o PDF desenha (é o que o programa mostraria). Página sem
    camadas levanta NaoSeAplica, que a conferência mostra como aviso.
    imagem_antes não é usada (a assinatura é a que a conferência pede).
    """
    from core.pdf_io import pagina_para_array

    with fitz.open(caminho_pdf) as doc:
        resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_de_figuras)
        print(f"  [camadas] {Path(caminho_pdf).stem}: {resultado.situacao} - "
              f"{resultado.explicacao} zonas={resultado.zonas_de_figura} "
              f"mantidas={resultado.zonas_mantidas} medidas={resultado.medidas}", flush=True)
        if resultado.situacao == SEM_CAMADAS:
            raise NaoSeAplica(resultado.explicacao)
        if resultado.imagem is None:
            return pagina_para_array(doc, 0, dpi=int(round(resultado.dpi)))
        return resultado.imagem
