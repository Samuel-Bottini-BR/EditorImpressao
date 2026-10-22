"""Item 2.6: o arquivo para impressão (a "janela de imprimir" dentro do programa).

O QUE É (explicação do Samuel, 14/10/2026, literal em
relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md)
    "o programa tem duas fases separadas": na edição cada página ocupa a folha
    inteira; "Na hora de gerar o arquivo para impressão — É só nesta fase que se
    decide o formato de saída": livreto na horizontal (A4 deitada com duas A5,
    na ordem de caderno), página inteira A4 em pé, "ou todas as outras opções que
    aparecem nos prints do PDF que mandei" (a janela de imprimir do UPDF:
    Tamanho, Pôster, Múltiplo, Livreto, papel, orientação, girar e centralizar
    sozinho, escala de cinza, imprimir como imagem, reverter, intervalo).

    Este módulo pega o PDF que o processar gerou (as páginas do livro em ordem,
    cada uma do tamanho dela) e monta OUTRO PDF, com as folhas como vão para a
    impressora. Tudo roda por linha de comando, sem janela (CLAUDE.md §7).

AS DECISÕES QUE VALEM AQUI
    - g11 (14/10): margem de 1 cm "a partir de onde a impressora imprime (1,3 cm
      do papel)" em cima, embaixo e do lado de fora; 1 cm na costura; "página
      par → direita, página ímpar → esquerda" (a costura). Contadas na A5.
    - g12 (14/10) + imp-1 (21/10): escala só da esquerda / só da direita / das
      duas, para o livro todo, e a exceção vale para UMA PÁGINA SÓ ("Uma página
      só"), não para a folha A4 inteira.
    - imp-2 (21/10): no livreto o "Ajustar" de fábrica "Já entra dentro das
      margens"; e "Mas eu ainda vou poder aumentar né?": sim - a escala de cada
      lado (e a de cada página) sobe e desce em %, sobre o ajustado; se a tinta
      passar da margem, o aviso de margem abaixo de 1 cm avisa.
    - imp-3 (21/10): a página diminuída fica "No meio da sua metade".
    - imp-4 (21/10): último caderno menor (core/cadernos.tamanhos_dos_cadernos).
    - imp-5 (21/10): também manda direto para a impressora (core/impressora.py).
    - imp-6 (21/10): "Imprimir como imagem" - "Precisa: sem ela sai algo
      errado": de fábrica LIGADO (cada folha vira uma imagem só).
    - g9-folha-maior-impressao (20/10): a folha muito maior "Ajustar: gira de pé
      e reduz até caber na página A5" + "Quero que o programa avise quando isso
      estiver acontecendo." (a rotação automática; o aviso sai em `avisos`).
    - Aviso de margem (14/10): "o programa precisa avisar quando o corte deixar
      qualquer margem abaixo de 1 cm".

COMO (pesquisa da impressão, ramo pesquisa-impressao-2026-10-19, seção 3)
    Cada página entra na folha com `show_pdf_page` do PyMuPDF: sem refazer a
    imagem, os pontos do livro ficam intactos e a conta é rápida. A escala é só
    o tamanho do retângulo de destino. "Imprimir como imagem" e "escala de
    cinza" desenham cada folha montada numa imagem (uma por vez).

MEMÓRIA
    Nenhuma página aberta em pontos fica guardada; o PDF novo fica na memória
    do PyMuPDF até gravar, como o processar já faz hoje (pesquisa, seção 7).

SEGURO MUDAR: os textos dos avisos; PAPEIS_MM (acrescentar papel);
    DPI_DA_TINTA e LIMIAR_DA_TINTA (só o aviso).
ARRISCADO MUDAR: a conta de `_lados_do_livreto` (é a ordem da dobra de
    core/cadernos; a conferência simula a dobra); a regra da paridade do
    intervalo (página par sempre à esquerda: a costura); `_colocar` (o
    recorte do que passa da metade: sem ele uma página aumentada cobriria a
    vizinha).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Callable

import fitz
import numpy as np

from core import cadernos

MM_POR_PONTO = 25.4 / 72.0

# A lista de papéis da janela do UPDF (foto 3 de 14/10/2026), em mm (em pé).
PAPEIS_MM: dict[str, tuple[float, float]] = {
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "A3": (297.0, 420.0),
    "Carta": (216.0, 279.0),
    "Ofício 9": (215.0, 315.0),
    "8,5 x 13 pol.": (216.0, 330.0),
    "México-Ofício": (216.0, 341.0),
    "Ofício": (216.0, 356.0),
    "Executivo": (184.0, 267.0),
    "Envelope #10": (105.0, 241.0),
    "8 x 10 pol.": (203.0, 254.0),
    "5 x 7 pol.": (127.0, 178.0),
}

# Formatos (as abas da janela do UPDF; "Tamanho" = página inteira)
LIVRETO = "livreto"
PAGINA_INTEIRA = "pagina_inteira"
MULTIPLO = "multiplo"
POSTER = "poster"
FORMATOS = (LIVRETO, PAGINA_INTEIRA, MULTIPLO, POSTER)
NOMES_DOS_FORMATOS = {
    LIVRETO: "Livreto (A4 deitada, duas páginas por lado, na ordem dos cadernos)",
    PAGINA_INTEIRA: "Página inteira (uma página por folha)",
    MULTIPLO: "Várias páginas por folha",
    POSTER: "Pôster (página grande em várias folhas)",
}

RETRATO = "retrato"
PAISAGEM = "paisagem"

# Aba Tamanho do UPDF
AJUSTAR = "ajustar"
TAMANHO_REAL = "tamanho_real"
PERSONALIZADA = "personalizada"
REDUZIR_GRANDES = "reduzir_grandes"
ESCALAS = (AJUSTAR, TAMANHO_REAL, PERSONALIZADA, REDUZIR_GRANDES)
NOMES_DAS_ESCALAS = {
    AJUSTAR: "Ajustar", TAMANHO_REAL: "Tamanho real",
    PERSONALIZADA: "Escala personalizada (%)", REDUZIR_GRANDES: "Reduzir páginas muito grandes",
}

# Livreto: "Ordem de páginas" e "Encadernação"
AMBOS = "frente_e_verso"
SO_FRENTE = "so_frente"
SO_VERSO = "so_verso"
ESQUERDA = "esquerda"
DIREITA = "direita"

# Múltiplo
HORIZONTAL = "horizontal"
VERTICAL = "vertical"
POR_FOLHA = (2, 4, 6, 9, 16)

# O aviso de margem: a página desenhada pequena (36 pontos por polegada, um
# ponto = 0,7 mm) e "tinta" o que é mais escuro que LIMIAR_DA_TINTA. Uma linha
# ou coluna só conta com pelo menos MINIMO_DE_PONTOS pontos de tinta (um
# pontinho de poeira solto não dispara aviso).
DPI_DA_TINTA = 36
LIMIAR_DA_TINTA = 140
MINIMO_DE_PONTOS = 2


@dataclass
class OpcoesDeImpressao:
    """Tudo o que a janela de imprimir escolhe. Os de fábrica são os das
    decisões (cabeçalho do módulo). Vai e volta como dicionário
    (`para_dicionario`/`de_dicionario`) para ficar no configuracoes.json, como
    a "Predefinição: Última configuração" do UPDF."""

    formato: str = LIVRETO
    papel: str = "A4"
    orientacao: str = ""          # "" = a do formato (livreto deitado, os outros em pé)
    rotacao_automatica: bool = True
    centralizar: bool = True

    escala: str = AJUSTAR
    escala_percentual: float = 100.0

    margens: bool = True           # g11: 1 cm de onde a impressora imprime
    margem_mm: float = 10.0
    borda_da_impressora_mm: float = 3.0      # "A impressora ainda come mais uns 3 mm"

    escala_esquerda: float = 100.0  # % sobre a escala escolhida (as páginas pares)
    escala_direita: float = 100.0   # (as ímpares)
    excecoes: dict = field(default_factory=dict)   # {número da página do livro: %}

    paginas_por_caderno: int = cadernos.PAGINAS_POR_CADERNO_PADRAO
    encadernacao: str = ESQUERDA
    lados: str = AMBOS
    folhas_de: int = 0              # 0 = desde a primeira (folhas de papel, 1, 2, ...)
    folhas_ate: int = 0             # 0 = até a última

    paginas_de: int = 0             # intervalo de páginas do livro (0 = todas)
    paginas_ate: int = 0
    reverter: bool = False
    cinza: bool = False
    como_imagem: bool = True        # imp-6: "Precisa"
    dpi_da_imagem: int = 300

    multiplo_por_folha: int = 4
    multiplo_ordem: str = HORIZONTAL
    multiplo_moldura: bool = False

    poster_escala: float = 100.0
    poster_sobreposicao_mm: float = 10.0
    poster_marcas: bool = True
    poster_so_grandes: bool = True

    def para_dicionario(self) -> dict:
        dados = asdict(self)
        dados["excecoes"] = {str(k): float(v) for k, v in self.excecoes.items()}
        return dados

    @staticmethod
    def de_dicionario(dados) -> "OpcoesDeImpressao":
        """Tolerante: campo que falta ganha o de fábrica, campo que sobra sai,
        valor estranho volta ao de fábrica."""
        opcoes = OpcoesDeImpressao()
        if not isinstance(dados, dict):
            return opcoes
        for campo in fields(OpcoesDeImpressao):
            if campo.name not in dados:
                continue
            valor = dados[campo.name]
            atual = getattr(opcoes, campo.name)
            try:
                if campo.name == "excecoes":
                    valor = {int(k): float(v) for k, v in dict(valor).items()}
                elif isinstance(atual, bool):
                    valor = bool(valor)
                elif isinstance(atual, int):
                    valor = int(valor)
                elif isinstance(atual, float):
                    valor = float(valor)
                elif isinstance(atual, str):
                    valor = str(valor)
            except (TypeError, ValueError):
                continue
            setattr(opcoes, campo.name, valor)
        if opcoes.formato not in FORMATOS:
            opcoes.formato = LIVRETO
        if opcoes.escala not in ESCALAS:
            opcoes.escala = AJUSTAR
        if opcoes.papel not in PAPEIS_MM:
            opcoes.papel = "A4"
        if opcoes.multiplo_por_folha not in POR_FOLHA:
            opcoes.multiplo_por_folha = 4
        return opcoes


@dataclass
class Aviso:
    """Um aviso em português, para a tela. `pagina` é o número da página do
    livro (1, 2, ...) ou 0 quando vale para o arquivo."""

    pagina: int
    texto: str


@dataclass
class Resultado:
    folhas_de_papel: int = 0        # folhas físicas (livreto: frente + verso = 1)
    paginas_do_arquivo: int = 0
    avisos: list[Aviso] = field(default_factory=list)
    cadernos: int = 0
    instrucoes: list[str] = field(default_factory=list)
    conferencia: tuple[bool, str] | None = None


Progresso = Callable[[int, int, str], None] | None
Cancelado = Callable[[], bool] | None


class Cancelou(Exception):
    """A pessoa cancelou a montagem."""


# --------------------------------------------------------------- medidas

def mm_para_pt(mm: float) -> float:
    return mm / MM_POR_PONTO


def tamanho_do_papel_pt(opcoes: OpcoesDeImpressao) -> tuple[float, float]:
    """(largura, altura) do papel em pontos, já na orientação."""
    largura, altura = (mm_para_pt(v) for v in PAPEIS_MM.get(opcoes.papel, PAPEIS_MM["A4"]))
    orientacao = opcoes.orientacao or (PAISAGEM if opcoes.formato == LIVRETO else RETRATO)
    if orientacao == PAISAGEM:
        largura, altura = max(largura, altura), min(largura, altura)
    else:
        largura, altura = min(largura, altura), max(largura, altura)
    return largura, altura


def margem_fora_mm(opcoes: OpcoesDeImpressao) -> float:
    """A margem na beirada do papel: 1 cm de onde a impressora imprime = 1,3 cm
    do papel (g11). Sem margens: só o que a impressora come."""
    return (opcoes.margem_mm if opcoes.margens else 0.0) + opcoes.borda_da_impressora_mm


def margem_costura_mm(opcoes: OpcoesDeImpressao) -> float:
    """A margem da dobra no livreto: 1 cm (g11); a dobra não é beirada de papel."""
    return opcoes.margem_mm if opcoes.margens else 0.0


# --------------------------------------------------------------- a tinta

def caixa_da_tinta(doc: fitz.Document, indice: int) -> tuple[float, float, float, float] | None:
    """Onde há tinta na página, em fração dela (x0, y0, x1, y1); None se a
    página é branca. Desenhada pequena (DPI_DA_TINTA), uma por vez."""
    pagina = doc[indice]
    pix = pagina.get_pixmap(dpi=DPI_DA_TINTA, colorspace=fitz.csGRAY, alpha=False)
    cinza = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width]
    tinta = cinza < LIMIAR_DA_TINTA
    linhas = np.flatnonzero(tinta.sum(axis=1) >= MINIMO_DE_PONTOS)
    colunas = np.flatnonzero(tinta.sum(axis=0) >= MINIMO_DE_PONTOS)
    if linhas.size == 0 or colunas.size == 0:
        return None
    return (colunas[0] / pix.width, linhas[0] / pix.height,
            (colunas[-1] + 1) / pix.width, (linhas[-1] + 1) / pix.height)


# --------------------------------------------------------------- a escala

def _gira(pagina_rect: fitz.Rect, vaga: fitz.Rect, opcoes: OpcoesDeImpressao) -> bool:
    """Rotação automática: a página deitada numa vaga em pé (ou o contrário)
    gira 90 graus."""
    if not opcoes.rotacao_automatica:
        return False
    pagina_deitada = pagina_rect.width > pagina_rect.height * 1.02
    vaga_deitada = vaga.width > vaga.height * 1.02
    pagina_de_pe = pagina_rect.height > pagina_rect.width * 1.02
    vaga_de_pe = vaga.height > vaga.width * 1.02
    return (pagina_deitada and vaga_de_pe) or (pagina_de_pe and vaga_deitada)


def fator_base(largura_pt: float, altura_pt: float, area: fitz.Rect,
               opcoes: OpcoesDeImpressao) -> float:
    """A escala da aba Tamanho (sem a de cada lado): Ajustar enche a área,
    Tamanho real é 1, Personalizada é a %, Reduzir só diminui as grandes."""
    ajustar = min(area.width / max(largura_pt, 1e-6), area.height / max(altura_pt, 1e-6))
    if opcoes.escala == TAMANHO_REAL:
        return 1.0
    if opcoes.escala == PERSONALIZADA:
        return max(0.01, opcoes.escala_percentual / 100.0)
    if opcoes.escala == REDUZIR_GRANDES:
        return min(1.0, ajustar)
    return ajustar


def fator_do_lado(numero: int, opcoes: OpcoesDeImpressao) -> float:
    """A escala de cada lado e a exceção de uma página só (imp-1). `numero` é
    o número da página do livro (1, 2, ...): par cai à esquerda (a costura à
    direita), ímpar à direita."""
    if numero in opcoes.excecoes:
        return max(0.01, float(opcoes.excecoes[numero]) / 100.0)
    lado = opcoes.escala_esquerda if numero % 2 == 0 else opcoes.escala_direita
    return max(0.01, float(lado) / 100.0)


# --------------------------------------------------------------- colocar

@dataclass
class Colocada:
    """Onde uma página do livro ficou numa folha (para o aviso de margem)."""

    numero: int                     # página do livro (1, 2, ...)
    destino: fitz.Rect              # o retângulo inteiro dela na folha (pode passar da vaga)
    girada: bool
    vaga: fitz.Rect


def _colocar(folha: fitz.Page, origem: fitz.Document, indice: int, vaga: fitz.Rect,
             area: fitz.Rect, opcoes: OpcoesDeImpressao, numero: int,
             com_lado: bool = True) -> Colocada:
    """Põe a página `indice` da origem na `vaga` da folha.

    A escala é a da aba Tamanho medida na `area` (a vaga menos as margens) vezes
    a do lado / da página (imp-1, imp-2). A página fica no meio da vaga (imp-3);
    se assim ela passaria das margens e couber dentro delas, anda o mínimo para
    ficar dentro. O que passar da vaga NÃO é desenhado (senão uma página
    aumentada cobriria a vizinha): corta-se a origem (clip)."""
    retangulo = origem[indice].rect
    girada = _gira(retangulo, vaga, opcoes)
    largura, altura = ((retangulo.height, retangulo.width) if girada
                       else (retangulo.width, retangulo.height))
    fator = fator_base(largura, altura, area, opcoes)
    if com_lado:
        fator *= fator_do_lado(numero, opcoes)
    l, a = largura * fator, altura * fator

    if opcoes.centralizar:
        x0 = vaga.x0 + (vaga.width - l) / 2
        y0 = vaga.y0 + (vaga.height - a) / 2
        # dentro das margens, se couber: anda só o necessário
        if l <= area.width + 1e-6:
            x0 = min(max(x0, area.x0), area.x1 - l)
        if a <= area.height + 1e-6:
            y0 = min(max(y0, area.y0), area.y1 - a)
    else:
        x0, y0 = area.x0, area.y0
    destino = fitz.Rect(x0, y0, x0 + l, y0 + a)

    visivel = destino & vaga
    if visivel.is_empty or visivel.width < 0.5 or visivel.height < 0.5:
        return Colocada(numero, destino, girada, vaga)
    if visivel == destino:
        folha.show_pdf_page(destino, origem, indice, rotate=90 if girada else 0,
                            keep_proportion=False)
    else:
        # a parte da origem que cai na vaga (em coordenadas da origem)
        fx0 = (visivel.x0 - destino.x0) / destino.width
        fx1 = (visivel.x1 - destino.x0) / destino.width
        fy0 = (visivel.y0 - destino.y0) / destino.height
        fy1 = (visivel.y1 - destino.y0) / destino.height
        if girada:
            # rotate=90 do show_pdf_page gira no sentido anti-horário (medido
            # em 22/10/2026): o alto da página vai para a esquerda da folha e a
            # esquerda dela vai para baixo. x da folha = y da origem; y da
            # folha = (1 - x) da origem.
            clip = fitz.Rect(retangulo.x0 + (1 - fy1) * retangulo.width, retangulo.y0 + fx0 * retangulo.height,
                             retangulo.x0 + (1 - fy0) * retangulo.width, retangulo.y0 + fx1 * retangulo.height)
        else:
            clip = fitz.Rect(retangulo.x0 + fx0 * retangulo.width, retangulo.y0 + fy0 * retangulo.height,
                             retangulo.x0 + fx1 * retangulo.width, retangulo.y0 + fy1 * retangulo.height)
        folha.show_pdf_page(visivel, origem, indice, clip=clip, rotate=90 if girada else 0,
                            keep_proportion=False)
    return Colocada(numero, destino, girada, vaga)


def _area_da_vaga(vaga: fitz.Rect, papel: fitz.Rect, opcoes: OpcoesDeImpressao,
                  costura: str | None) -> fitz.Rect:
    """A vaga menos as margens: 1,3 cm em cada lado que é beirada do papel, 1
    cm no lado da dobra (costura "esquerda"/"direita" da vaga, ou None)."""
    fora = mm_para_pt(margem_fora_mm(opcoes))
    dobra = mm_para_pt(margem_costura_mm(opcoes))

    def lado(valor_vaga: float, valor_papel: float, e_costura: bool) -> float:
        if e_costura:
            return dobra
        return fora if abs(valor_vaga - valor_papel) < 0.5 else dobra

    x0 = vaga.x0 + lado(vaga.x0, papel.x0, costura == ESQUERDA)
    x1 = vaga.x1 - lado(vaga.x1, papel.x1, costura == DIREITA)
    y0 = vaga.y0 + lado(vaga.y0, papel.y0, False)
    y1 = vaga.y1 - lado(vaga.y1, papel.y1, False)
    if x1 - x0 < 10:
        x0, x1 = vaga.x0, vaga.x1
    if y1 - y0 < 10:
        y0, y1 = vaga.y0, vaga.y1
    return fitz.Rect(x0, y0, x1, y1)


# --------------------------------------------------------------- o intervalo

def _paginas_escolhidas(total: int, opcoes: OpcoesDeImpressao) -> list[int | None]:
    """Os índices (0, 1, ...) das páginas do livro que entram, na ordem. Um
    intervalo que começa numa página PAR ganha uma branca antes: assim toda
    página par continua à esquerda e a costura não troca de lado (pesquisa,
    seção 6, "Cuidado com a paridade")."""
    de = opcoes.paginas_de if opcoes.paginas_de > 0 else 1
    ate = opcoes.paginas_ate if opcoes.paginas_ate > 0 else total
    de, ate = max(1, min(de, total)), max(1, min(ate, total))
    if ate < de:
        de, ate = ate, de
    escolhidas: list[int | None] = list(range(de - 1, ate))
    if de % 2 == 0 and opcoes.formato in (LIVRETO, PAGINA_INTEIRA):
        escolhidas.insert(0, None)
    return escolhidas


# --------------------------------------------------------------- os formatos

def _lados_do_livreto(quantas: int, opcoes: OpcoesDeImpressao) -> list[cadernos.Lado]:
    """A ordem da dobra (core/cadernos.montar_ordem, com o último caderno menor,
    imp-4), com a encadernação à direita trocando os lados, o "só frente / só
    verso" e as folhas de/até (folhas de papel: 1 = a frente e o verso da
    primeira)."""
    lados = cadernos.montar_ordem(quantas, opcoes.paginas_por_caderno)
    if opcoes.encadernacao == DIREITA:
        lados = [cadernos.Lado(l.direita, l.esquerda, l.frente) for l in lados]
    pares = [(lados[i], lados[i + 1]) for i in range(0, len(lados), 2)]
    total_folhas = len(pares)
    de = opcoes.folhas_de if opcoes.folhas_de > 0 else 1
    ate = opcoes.folhas_ate if opcoes.folhas_ate > 0 else total_folhas
    pares = pares[max(0, de - 1):max(0, min(ate, total_folhas))]
    if opcoes.reverter:
        pares.reverse()
    saida: list[cadernos.Lado] = []
    for frente, verso in pares:
        if opcoes.lados in (AMBOS, SO_FRENTE):
            saida.append(frente)
        if opcoes.lados in (AMBOS, SO_VERSO):
            saida.append(verso)
    return saida


def _montar_livreto(origem, saida, escolhidas, opcoes, colocadas, checar) -> int:
    largura, altura = tamanho_do_papel_pt(opcoes)
    papel = fitz.Rect(0, 0, largura, altura)
    meio = largura / 2
    esquerda = fitz.Rect(0, 0, meio, altura)
    direita = fitz.Rect(meio, 0, largura, altura)
    area_esq = _area_da_vaga(esquerda, papel, opcoes, DIREITA)
    area_dir = _area_da_vaga(direita, papel, opcoes, ESQUERDA)
    lados = _lados_do_livreto(len(escolhidas), opcoes)
    for numero_do_lado, lado in enumerate(lados):
        checar(numero_do_lado, len(lados))
        folha = saida.new_page(width=largura, height=altura)
        for posicao, vaga, area in ((lado.esquerda, esquerda, area_esq),
                                    (lado.direita, direita, area_dir)):
            if posicao is None or escolhidas[posicao] is None:
                continue
            indice = escolhidas[posicao]
            colocadas.append(_colocar(folha, origem, indice, vaga, area, opcoes, indice + 1))
    return math.ceil(len(lados) / 2) if opcoes.lados == AMBOS else len(lados)


def _montar_pagina_inteira(origem, saida, escolhidas, opcoes, colocadas, checar) -> int:
    largura, altura = tamanho_do_papel_pt(opcoes)
    papel = fitz.Rect(0, 0, largura, altura)
    ordem = list(escolhidas)
    if opcoes.reverter:
        # frente e verso: inverter as FOLHAS (pares de páginas), nunca separar
        # a frente do verso de uma folha
        if len(ordem) % 2:
            ordem.append(None)
        pares = [ordem[i:i + 2] for i in range(0, len(ordem), 2)]
        ordem = [p for par in reversed(pares) for p in par]
    for n, indice in enumerate(ordem):
        checar(n, len(ordem))
        folha = saida.new_page(width=largura, height=altura)
        if indice is None:
            continue
        area = _area_da_vaga(papel, papel, opcoes, None)
        colocadas.append(_colocar(folha, origem, indice, papel, area, opcoes, indice + 1))
    return math.ceil(len(ordem) / 2)


def _grade(por_folha: int, deitada: bool) -> tuple[int, int]:
    """(colunas, linhas) da grade do Múltiplo."""
    grades = {2: (2, 1), 4: (2, 2), 6: (3, 2), 9: (3, 3), 16: (4, 4)}
    colunas, linhas = grades.get(por_folha, (2, 2))
    return (colunas, linhas) if deitada else (linhas, colunas)


def _montar_multiplo(origem, saida, escolhidas, opcoes, colocadas, checar) -> int:
    largura, altura = tamanho_do_papel_pt(opcoes)
    papel = fitz.Rect(0, 0, largura, altura)
    util = _area_da_vaga(papel, papel, opcoes, None)
    colunas, linhas = _grade(opcoes.multiplo_por_folha, largura > altura)
    intervalo = mm_para_pt(3)
    cel_l = (util.width - intervalo * (colunas - 1)) / colunas
    cel_a = (util.height - intervalo * (linhas - 1)) / linhas
    paginas = [i for i in escolhidas if i is not None]
    if opcoes.reverter:
        paginas.reverse()
    por_folha = colunas * linhas
    folhas = 0
    for inicio in range(0, len(paginas), por_folha):
        checar(inicio, len(paginas))
        folha = saida.new_page(width=largura, height=altura)
        folhas += 1
        for k, indice in enumerate(paginas[inicio:inicio + por_folha]):
            if opcoes.multiplo_ordem == VERTICAL:
                c, r = k // linhas, k % linhas
            else:
                r, c = k // colunas, k % colunas
            x0 = util.x0 + c * (cel_l + intervalo)
            y0 = util.y0 + r * (cel_a + intervalo)
            celula = fitz.Rect(x0, y0, x0 + cel_l, y0 + cel_a)
            colocada = _colocar(folha, origem, indice, celula, celula, opcoes, indice + 1,
                                com_lado=False)
            if opcoes.multiplo_moldura:
                folha.draw_rect(colocada.destino & celula, color=(0.5, 0.5, 0.5), width=0.5)
    return folhas


def _montar_poster(origem, saida, escolhidas, opcoes, colocadas, checar) -> int:
    largura, altura = tamanho_do_papel_pt(opcoes)
    papel = fitz.Rect(0, 0, largura, altura)
    borda = mm_para_pt(opcoes.borda_da_impressora_mm + (5 if opcoes.poster_marcas else 0))
    util = fitz.Rect(borda, borda, largura - borda, altura - borda)
    sobra = mm_para_pt(max(0.0, opcoes.poster_sobreposicao_mm))
    fator = max(0.01, opcoes.poster_escala / 100.0)
    folhas = 0
    paginas = [i for i in escolhidas if i is not None]
    for n, indice in enumerate(paginas):
        checar(n, len(paginas))
        retangulo = origem[indice].rect
        l, a = retangulo.width * fator, retangulo.height * fator
        if opcoes.poster_so_grandes and l <= util.width + 0.5 and a <= util.height + 0.5:
            folha = saida.new_page(width=largura, height=altura)
            folhas += 1
            destino = fitz.Rect(0, 0, l, a)
            destino = destino + (util.x0 + (util.width - l) / 2, util.y0 + (util.height - a) / 2) * 2
            folha.show_pdf_page(destino, origem, indice, keep_proportion=False)
            continue
        passo_l = max(1.0, util.width - sobra)
        passo_a = max(1.0, util.height - sobra)
        colunas = max(1, math.ceil((l - sobra) / passo_l)) if l > util.width else 1
        linhas = max(1, math.ceil((a - sobra) / passo_a)) if a > util.height else 1
        for r in range(linhas):
            for c in range(colunas):
                # o pedaço, em pontos da página aumentada
                px0, py0 = c * passo_l, r * passo_a
                px1, py1 = min(l, px0 + util.width), min(a, py0 + util.height)
                clip = fitz.Rect(retangulo.x0 + px0 / fator, retangulo.y0 + py0 / fator,
                                 retangulo.x0 + px1 / fator, retangulo.y0 + py1 / fator)
                folha = saida.new_page(width=largura, height=altura)
                folhas += 1
                destino = fitz.Rect(util.x0, util.y0, util.x0 + (px1 - px0), util.y0 + (py1 - py0))
                folha.show_pdf_page(destino, origem, indice, clip=clip, keep_proportion=False)
                if opcoes.poster_marcas:
                    _marcas_de_corte(folha, destino)
                    folha.insert_text((util.x0, papel.y1 - mm_para_pt(opcoes.borda_da_impressora_mm) - 1),
                                      f"p. {indice + 1} - pedaço {r * colunas + c + 1} de "
                                      f"{linhas * colunas} (linha {r + 1}, coluna {c + 1})",
                                      fontsize=6, color=(0.4, 0.4, 0.4))
    return folhas


def _marcas_de_corte(folha: fitz.Page, r: fitz.Rect) -> None:
    """Traços curtos fora dos quatro cantos do pedaço (para cortar e colar)."""
    t = mm_para_pt(4)
    for x, y, dx, dy in ((r.x0, r.y0, -1, -1), (r.x1, r.y0, 1, -1),
                         (r.x0, r.y1, -1, 1), (r.x1, r.y1, 1, 1)):
        folha.draw_line((x + dx * 1, y), (x + dx * t, y), color=(0, 0, 0), width=0.3)
        folha.draw_line((x, y + dy * 1), (x, y + dy * t), color=(0, 0, 0), width=0.3)


# --------------------------------------------------------------- os avisos

def _avisos_de_margem(origem, colocadas: list[Colocada], opcoes: OpcoesDeImpressao,
                      papel: fitz.Rect) -> list[Aviso]:
    """O aviso de margem abaixo de 1 cm (14/10/2026): onde a tinta de cada
    página cai na folha e quanto sobra até a beirada do papel (precisa de
    1,3 cm: 1 cm de onde a impressora imprime) e até a dobra (1 cm). Só no
    livreto e na página inteira (os dois de encadernar). Mede a tinta uma vez
    por página do livro (pequena, uma por vez)."""
    if opcoes.formato not in (LIVRETO, PAGINA_INTEIRA):
        return []
    precisa_fora = opcoes.margem_mm + opcoes.borda_da_impressora_mm
    precisa_dobra = opcoes.margem_mm
    avisos: list[Aviso] = []
    tintas: dict[int, tuple | None] = {}
    for c in colocadas:
        if c.numero not in tintas:
            tintas[c.numero] = caixa_da_tinta(origem, c.numero - 1)
        tinta = tintas[c.numero]
        if tinta is None:
            continue
        fx0, fy0, fx1, fy1 = tinta
        d = c.destino
        if c.girada:
            # rotate=90 (anti-horário, ver _colocar): x da folha = y da
            # página; y da folha = 1 - x da página
            x0, x1 = d.x0 + fy0 * d.width, d.x0 + fy1 * d.width
            y0, y1 = d.y0 + (1 - fx1) * d.height, d.y0 + (1 - fx0) * d.height
        else:
            x0, x1 = d.x0 + fx0 * d.width, d.x0 + fx1 * d.width
            y0, y1 = d.y0 + fy0 * d.height, d.y0 + fy1 * d.height
        faltas = []

        def medir(nome: str, distancia_pt: float, precisa: float) -> None:
            mm = distancia_pt * MM_POR_PONTO
            if mm < precisa - 0.05:
                faltas.append(f"{nome} {mm / 10:.1f} cm".replace(".", ",")
                              + f" (precisa de {precisa / 10:.1f} cm)".replace(".", ","))

        medir("em cima", y0 - papel.y0, precisa_fora)
        medir("embaixo", papel.y1 - y1, precisa_fora)
        if opcoes.formato == LIVRETO:
            na_esquerda = c.vaga.x0 < papel.width / 2 - 1
            if na_esquerda:
                medir("do lado de fora", x0 - papel.x0, precisa_fora)
                medir("na costura", c.vaga.x1 - x1, precisa_dobra)
            else:
                medir("do lado de fora", papel.x1 - x1, precisa_fora)
                medir("na costura", x0 - c.vaga.x0, precisa_dobra)
        else:
            medir("à esquerda", x0 - papel.x0, precisa_fora)
            medir("à direita", papel.x1 - x1, precisa_fora)
        if faltas:
            avisos.append(Aviso(c.numero, f"Página {c.numero}: a margem ficou abaixo de 1 cm - "
                                          + "; ".join(faltas)
                                          + ". Diminua a escala desta página ou do lado dela."))
    return avisos


def _avisos_de_giro(colocadas: list[Colocada]) -> list[Aviso]:
    """g9-folha-maior-impressao (20/10/2026): "Quero que o programa avise
    quando isso estiver acontecendo" (a página que gira de pé e diminui)."""
    vistas, avisos = set(), []
    for c in colocadas:
        if c.girada and c.numero not in vistas:
            vistas.add(c.numero)
            avisos.append(Aviso(c.numero, f"Página {c.numero}: era deitada e foi girada de pé e "
                                          "diminuída para caber na página."))
    return avisos


# --------------------------------------------------------------- montar

def montar_para_impressao(entrada: str | Path, saida: str | Path,
                          opcoes: OpcoesDeImpressao | None = None,
                          progresso: Progresso = None,
                          cancelado: Cancelado = None) -> Resultado:
    """Lê o PDF do livro (páginas em ordem) e grava o PDF com as folhas como vão
    para a impressora. Devolve o Resultado (folhas, avisos, instruções).

    Grava num arquivo à parte ao lado e só troca no fim (como o processar):
    cancelar ou dar erro nunca estraga um arquivo antigo de mesmo nome."""
    opcoes = opcoes or OpcoesDeImpressao()
    saida = Path(saida)
    parcial = saida.with_name(f"~{saida.name}.parcial")
    resultado = Resultado()

    def checar(feito: int, total: int, texto: str = "Montando as folhas") -> None:
        if cancelado is not None and cancelado():
            raise Cancelou()
        if progresso is not None:
            progresso(feito, total, f"{texto}: {feito + 1} de {total}")

    origem = fitz.open(str(entrada))
    montado = fitz.open()
    try:
        if origem.page_count == 0:
            raise ValueError("O arquivo do livro não tem páginas.")
        escolhidas = _paginas_escolhidas(origem.page_count, opcoes)
        colocadas: list[Colocada] = []
        montar = {LIVRETO: _montar_livreto, PAGINA_INTEIRA: _montar_pagina_inteira,
                  MULTIPLO: _montar_multiplo, POSTER: _montar_poster}[opcoes.formato]
        resultado.folhas_de_papel = montar(origem, montado, escolhidas, opcoes, colocadas, checar)

        largura, altura = tamanho_do_papel_pt(opcoes)
        papel = fitz.Rect(0, 0, largura, altura)
        resultado.avisos = _avisos_de_giro(colocadas) + _avisos_de_margem(origem, colocadas, opcoes, papel)
        if opcoes.formato == LIVRETO:
            quantas = len(escolhidas)
            resultado.cadernos = len(cadernos.tamanhos_dos_cadernos(quantas, opcoes.paginas_por_caderno))
            resultado.instrucoes = cadernos.instrucoes_de_impressao(quantas, opcoes.paginas_por_caderno)
            resultado.conferencia = cadernos.conferir_sequencia(quantas, opcoes.paginas_por_caderno)
        elif opcoes.formato == PAGINA_INTEIRA:
            resultado.instrucoes = ["Imprima frente e verso, virando na borda comprida."]

        final = montado
        if opcoes.como_imagem or opcoes.cinza:
            final = _achatar(montado, opcoes, checar)
        resultado.paginas_do_arquivo = final.page_count
        saida.parent.mkdir(parents=True, exist_ok=True)
        final.save(str(parcial), garbage=3, deflate=True)
        if final is not montado:
            final.close()
        parcial.replace(saida)
        return resultado
    finally:
        montado.close()
        origem.close()
        parcial.unlink(missing_ok=True)


def _achatar(montado: fitz.Document, opcoes: OpcoesDeImpressao, checar) -> fitz.Document:
    """"Imprimir como imagem" (imp-6) e "escala de cinza": cada folha montada
    vira UMA imagem (sem perda, PNG), uma por vez."""
    plano = fitz.open()
    espaco = fitz.csGRAY if opcoes.cinza else fitz.csRGB
    for n in range(montado.page_count):
        checar(n, montado.page_count, "Desenhando as folhas como imagem")
        pagina = montado[n]
        pix = pagina.get_pixmap(dpi=max(72, int(opcoes.dpi_da_imagem)), colorspace=espaco, alpha=False)
        nova = plano.new_page(width=pagina.rect.width, height=pagina.rect.height)
        nova.insert_image(nova.rect, pixmap=pix)
        del pix
    return plano


def montar_em_memoria(entrada: str | Path, opcoes: OpcoesDeImpressao) -> tuple[fitz.Document, Resultado]:
    """Para a impressora (core/impressora.py) e para a prévia: devolve o PDF
    montado aberto na memória (SEM o "como imagem": quem imprime já desenha
    cada folha como imagem). Quem chama fecha o documento."""
    import tempfile

    sem_achatar = OpcoesDeImpressao.de_dicionario(opcoes.para_dicionario())
    sem_achatar.como_imagem = False
    sem_achatar.cinza = False
    with tempfile.TemporaryDirectory() as pasta:
        destino = Path(pasta) / "folhas.pdf"
        resultado = montar_para_impressao(entrada, destino, sem_achatar)
        doc = fitz.open(str(destino))
        dados = doc.tobytes()
        doc.close()
    return fitz.open("pdf", dados), resultado
