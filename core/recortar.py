"""Cortar as bordas: tira a borda preta do scanner e a sombra da margem."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Folga deixada em volta do conteudo, em fracao do lado. Sem folga nenhuma o
# corte encosta na letra e o texto fica sufocado na impressao; com folga demais
# sobra papel em branco, que foi a queixa em cinco das dezesseis paginas que o
# Samuel conferiu. Meio por cento de uma pagina A4 e cerca de um milimetro.
FOLGA = 0.005

# Nunca cortar mais que isso de cada lado. Protege contra o caso em que a
# deteccao se perde e devora metade da pagina.
CORTE_MAXIMO = 0.25

ALTURA_ANALISE = 800

# Faixa colada na moldura que NAO conta como conteudo perdido: e ali que mora
# a borda preta do scanner, justamente o que queremos cortar.
MOLDURA = 0.03

# Fracao de tinta fora do corte a partir da qual avisamos o usuario.
TINTA_FORA_MAXIMA = 0.02

# A partir de quanto uma linha (ou coluna) inteira escura e moldura de scanner
# e nao conteudo. Texto nunca chega perto disso.
FRACAO_BORDA_SOLIDA = 0.80

# Quanto de um lado uma risca precisa cobrir para ser vinco de folha, e nao
# conteudo. Medido no acervo: a moldura da gravura do Palatino cobre 81% da
# altura, o vinco do Graduale cobre 97%. O que separa os dois nao e a cobertura
# e sim encostar na borda (ver _apagar_riscas_de_dobra), mas abaixo de 70% ja
# nao e risca nenhuma: e coluna de texto.
COBERTURA_DE_RISCA = 0.70

# Que fracao da ponta da imagem conta como "encostou na borda".
PONTA_DA_IMAGEM = 0.01

# Risca de dobra e fina. Acima disso e mancha larga, e mancha larga pode ser
# conteudo - uma tarja preta, uma lombada fotografada.
ESPESSURA_DE_RISCA = 0.02

# A risca vem borrada nas laterais: a coluna do meio cobre 97% do lado, e as
# vizinhas ainda cobrem meio lado. Apagar so o meio nao adianta, porque a sombra
# em volta continua segurando o corte. Uma vez achada a risca, o borrao ao redor
# vai junto enquanto ainda for meio lado de tinta.
COBERTURA_DE_BORRAO = 0.35


@dataclass(frozen=True)
class Recorte:
    """Área util da página, em fracao de 0 a 1: (x, y, largura, altura)."""

    x: float
    y: float
    largura: float
    altura: float
    encostou_no_conteudo: bool = False

    @property
    def tupla(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.largura, self.altura)

    @staticmethod
    def inteiro() -> "Recorte":
        return Recorte(0.0, 0.0, 1.0, 1.0)


# Que fracao da tinta pode ficar de fora do corte, de cada ponta.
#
# Era um por mil, e nao dava conta da beirada picotada da folha: na pagina 536
# do Graduale a sujeira da margem esquerda carrega 0,15% da tinta, passa do um
# por mil e prende o corte na largura inteira - a queixa de "sobrou muito espaco
# do lado esquerdo". Dois por mil engole essa sujeira; uma linha de texto dessas
# paginas pesa de 1% a 3%, dez vezes mais, e continua mandando no recorte.
SOBRA_DE_TINTA = 0.002


def _sem_conteudo_para_recortar(img: np.ndarray) -> bool:
    """Capa, guarda, foto da encadernacao: nao ha o que recortar.

    Mesma pergunta que o detector de regioes faz, e pela mesma razao: uma capa
    de couro TEM textura, mas nao tem nada significativamente mais escuro que
    ela mesma. Cortar uma capa so tira pedaco dela.
    """
    try:
        from core.detectar_regioes import _pagina_sem_conteudo

        return _pagina_sem_conteudo(img if img.ndim == 3 else
                                    cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
    except Exception:  # noqa: BLE001 - na duvida, recorta como antes
        return False


def _faixa_com_a_tinta(perfil: np.ndarray) -> tuple[int, int] | None:
    """Onde comeca e termina a massa da tinta, num perfil de linhas ou colunas.

    Descarta SOBRA_DE_TINTA de cada ponta pela distribuicao acumulada, entao
    alguns pixels soltos na borda nao mandam no recorte.
    """
    total = float(perfil.sum())
    if total <= 0:
        return None
    acumulado = np.cumsum(perfil.astype(np.float64)) / total
    inicio = int(np.searchsorted(acumulado, SOBRA_DE_TINTA))
    fim = int(np.searchsorted(acumulado, 1.0 - SOBRA_DE_TINTA))
    if fim <= inicio:
        return None
    return inicio, fim + 1


def _mascara_de_tinta_local(cinza: np.ndarray) -> np.ndarray:
    """Tinta de verdade, pelo limiar local de Sauvola.

    Cai para o limiar global se a binarizacao nao estiver disponivel - melhor um
    recorte conservador que nenhum recorte.
    """
    try:
        from core.filtros import binarizar, janela_para_altura

        binaria = binarizar(cinza, janela=janela_para_altura(cinza.shape[0]), k=0.20)
        return (binaria == 0).astype(np.uint8)
    except Exception:  # noqa: BLE001
        nivel_papel = float(np.percentile(cinza, 80))
        return (cinza < max(20.0, nivel_papel * 0.75)).astype(np.uint8)


def detectar_bordas(img: np.ndarray) -> Recorte:
    """Acha o retangulo que contem o conteúdo da página.

    Ideia: binarizar de forma bem tolerante, achar as linhas e colunas que tem
    tinta de verdade e envolver tudo isso. Bordas pretas do scanner ficam
    coladas na moldura, entao são descartadas por serem grandes demais para
    caberem no limite de CORTE_MAXIMO.
    """
    # Capa de couro, guarda, foto da encadernacao: nao ha borda de scanner nem
    # margem de papel para tirar, e cortar so estraga. O Samuel apontou quatro
    # casos assim nas dezesseis imagens que conferiu.
    if _sem_conteudo_para_recortar(img):
        return Recorte.inteiro()

    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    altura_orig, largura_orig = cinza.shape[:2]

    if altura_orig > ALTURA_ANALISE:
        escala = ALTURA_ANALISE / altura_orig
        cinza = cv2.resize(
            cinza, (max(8, int(largura_orig * escala)), ALTURA_ANALISE),
            interpolation=cv2.INTER_AREA,
        )
    altura, largura = cinza.shape[:2]

    # Onde ha tinta de verdade.
    #
    # A versao anterior usava um limiar GLOBAL tolerante - qualquer coisa mais
    # escura que 75% do nivel do papel. Em papel creme manchado isso acha tinta
    # na folha inteira, e o recorte conclui que nao ha o que cortar: no Livro de
    # Horas ele mantinha 100% da altura enquanto o conteudo ocupava de 11% a 82%.
    # Era a queixa de "sobra dos lados uma parte branca".
    #
    # O limiar local de Sauvola separa tinta de mancha, que e exatamente o que
    # um limiar unico nao consegue fazer numa folha envelhecida.
    tinta = _mascara_de_tinta_local(cinza)

    # Um fechamento pequeno junta as letras em blocos de texto e evita que uma
    # unica mancha de poeira defina a borda.
    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, nucleo)

    # A borda preta do scanner tambem e "escura", entao seria confundida com
    # conteudo e nada seria cortado. Ela e descartada antes.
    tinta = _apagar_bordas_solidas(tinta)

    # E as riscas finas do vinco e da beirada da folha de tras, que nao sao
    # escuras o bastante para a regra acima mas atravessam a pagina toda.
    tinta = _apagar_riscas_de_dobra(tinta)

    # Onde esta a MASSA da tinta, e nao onde ha algum pixel dela.
    #
    # A versao anterior aceitava uma linha como "tem conteudo" se ela tivesse 1%
    # da largura em tinta - cinco pixels numa pagina de quinhentos. Sujeira de
    # borda passa nisso: no Livro de Horas a primeira linha tinha 12 pixels e a
    # ultima tinha 4, todos ruido, e o recorte mantinha a folha inteira enquanto
    # o conteudo ocupava de 11% a 82% da altura. Era a queixa de "sobra dos
    # lados uma parte branca".
    #
    # Cortando pela distribuicao acumulada, alguns pixels soltos nao movem a
    # borda: seria preciso uma fracao real da tinta estar ali.
    limites = _faixa_com_a_tinta(tinta.sum(axis=1))
    if limites is None:
        return Recorte.inteiro()  # pagina em branco: nao ha o que recortar
    y0, y1 = limites

    limites = _faixa_com_a_tinta(tinta.sum(axis=0))
    if limites is None:
        return Recorte.inteiro()
    x0, x1 = limites

    # folga
    folga_x = int(largura * FOLGA)
    folga_y = int(altura * FOLGA)
    x0e, y0e = max(0, x0 - folga_x), max(0, y0 - folga_y)
    x1e, y1e = min(largura, x1 + folga_x), min(altura, y1 + folga_y)

    # limite de seguranca: nunca comer mais que CORTE_MAXIMO de um lado
    max_x = int(largura * CORTE_MAXIMO)
    max_y = int(altura * CORTE_MAXIMO)
    x0e, y0e = min(x0e, max_x), min(y0e, max_y)
    x1e, y1e = max(x1e, largura - max_x), max(y1e, altura - max_y)

    encostou = _sobrou_conteudo_fora(tinta, x0e, y0e, x1e, y1e)

    return Recorte(
        x=x0e / largura,
        y=y0e / altura,
        largura=(x1e - x0e) / largura,
        altura=(y1e - y0e) / altura,
        encostou_no_conteudo=bool(encostou),
    )


def _apagar_bordas_solidas(tinta: np.ndarray) -> np.ndarray:
    """Descarta as faixas escuras macicas coladas nas quatro bordas.

    E assim que se distingue a moldura preta do scanner de uma linha de texto:
    a moldura preenche quase toda a linha (ou coluna) de ponta a ponta, o que
    nenhuma linha de texto faz. Caminhamos de cada borda para dentro enquanto a
    faixa continuar praticamente toda escura, e paramos na primeira que não for.
    """
    limpa = tinta.copy()
    altura, largura = limpa.shape[:2]

    limite_x = int(largura * CORTE_MAXIMO)
    limite_y = int(altura * CORTE_MAXIMO)

    # esquerda e direita
    x = 0
    while x < limite_x and limpa[:, x].mean() >= FRACAO_BORDA_SOLIDA:
        limpa[:, x] = 0
        x += 1
    x = largura - 1
    while x > largura - 1 - limite_x and limpa[:, x].mean() >= FRACAO_BORDA_SOLIDA:
        limpa[:, x] = 0
        x -= 1

    # topo e base
    y = 0
    while y < limite_y and limpa[y, :].mean() >= FRACAO_BORDA_SOLIDA:
        limpa[y, :] = 0
        y += 1
    y = altura - 1
    while y > altura - 1 - limite_y and limpa[y, :].mean() >= FRACAO_BORDA_SOLIDA:
        limpa[y, :] = 0
        y -= 1

    return limpa


def _apagar_riscas_de_dobra(tinta: np.ndarray) -> np.ndarray:
    """Apaga as riscas finas da dobra e da beirada da folha vizinha.

    Sao aquelas riscas que atravessam a pagina inteira de ponta a ponta, deixadas
    pelo vinco do livro aberto ou pela beirada da folha de tras. Elas nao sao
    escuras o bastante para _apagar_bordas_solidas, e como cada uma carrega
    muita tinta, o recorte fica preso na largura inteira: era o caso das paginas
    429 e 536 do Graduale.

    O que separa uma risca dessas da moldura de uma gravura, que precisa ser
    preservada, e ENCOSTAR NA BORDA da imagem. Conteudo nunca encosta: entre a
    borda do escaneamento e o desenho sempre sobra margem. A moldura do Palatino
    cobre 81% da altura mas comeca 29 pixels para dentro; o vinco do Graduale vai
    de y=0 a y=799 sem parar.
    """
    limpa = tinta.copy()
    altura, largura = limpa.shape[:2]

    for eixo, tamanho, comprimento in ((1, largura, altura), (0, altura, largura)):
        banda = int(tamanho * CORTE_MAXIMO)
        espessura_maxima = max(1, int(tamanho * ESPESSURA_DE_RISCA))
        ponta = max(1, int(comprimento * PONTA_DA_IMAGEM))

        candidatas = []
        for i in list(range(0, banda)) + list(range(tamanho - banda, tamanho)):
            faixa = limpa[:, i] if eixo == 1 else limpa[i, :]
            if float(faixa.mean()) < COBERTURA_DE_RISCA:
                continue
            onde = np.flatnonzero(faixa)
            # Encosta em cima ou embaixo (esquerda ou direita, no outro eixo)?
            if onde[0] <= ponta or onde[-1] >= comprimento - 1 - ponta:
                candidatas.append(i)

        # So apaga o que for fino: riscas vizinhas em grupo ate ESPESSURA_DE_RISCA.
        for grupo in _agrupar_vizinhas(candidatas):
            if len(grupo) > espessura_maxima:
                continue
            inicio, fim = _com_o_borrao(limpa, eixo, grupo, espessura_maxima)
            for i in range(inicio, fim + 1):
                if eixo == 1:
                    limpa[:, i] = 0
                else:
                    limpa[i, :] = 0

    return limpa


def _com_o_borrao(
    tinta: np.ndarray, eixo: int, grupo: list[int], espessura_maxima: int
) -> tuple[int, int]:
    """Estende a risca para os lados enquanto ainda houver o borrao dela.

    Sem isso, apagar a risca do Graduale nao movia o corte um milimetro: a
    coluna de 97% saia, e as duas ao lado, de 60%, continuavam la segurando a
    borda no mesmo lugar.
    """
    tamanho = tinta.shape[1] if eixo == 1 else tinta.shape[0]
    inicio, fim = grupo[0], grupo[-1]
    limite = espessura_maxima * 2

    def cobertura(i: int) -> float:
        faixa = tinta[:, i] if eixo == 1 else tinta[i, :]
        return float(faixa.mean())

    while inicio > 0 and (fim - inicio) < limite and cobertura(inicio - 1) >= COBERTURA_DE_BORRAO:
        inicio -= 1
    while fim < tamanho - 1 and (fim - inicio) < limite and cobertura(fim + 1) >= COBERTURA_DE_BORRAO:
        fim += 1
    return inicio, fim


def _agrupar_vizinhas(indices: list[int]) -> list[list[int]]:
    """Junta indices consecutivos: [3,4,5,40] vira [[3,4,5],[40]]."""
    grupos: list[list[int]] = []
    for i in indices:
        if grupos and i == grupos[-1][-1] + 1:
            grupos[-1].append(i)
        else:
            grupos.append([i])
    return grupos


def _sobrou_conteudo_fora(
    tinta: np.ndarray, x0: int, y0: int, x1: int, y1: int
) -> bool:
    """Diz se ficou conteúdo de verdade FORA do retangulo que vamos manter.

    O cuidado esta em não confundir com a borda preta do scanner, que e o que
    queremos jogar fora. Por isso a faixa colada na moldura (MOLDURA) e
    ignorada: sobra só o miolo entre a borda preta e o corte, que e onde
    apareceria um pedaco de texto perdido.
    """
    altura, largura = tinta.shape[:2]
    moldura_x = int(largura * MOLDURA)
    moldura_y = int(altura * MOLDURA)

    faixas = [
        tinta[moldura_y:y0, moldura_x : largura - moldura_x],            # acima
        tinta[y1 : altura - moldura_y, moldura_x : largura - moldura_x],  # abaixo
        tinta[moldura_y : altura - moldura_y, moldura_x:x0],              # esquerda
        tinta[moldura_y : altura - moldura_y, x1 : largura - moldura_x],  # direita
    ]

    for faixa in faixas:
        if faixa.size >= 100 and float(faixa.mean()) > TINTA_FORA_MAXIMA:
            return True
    return False


def aplicar_recorte(img: np.ndarray, recorte: Recorte | tuple) -> np.ndarray:
    """Corta a imagem pelo retangulo relativo dado."""
    if isinstance(recorte, Recorte):
        x, y, w, h = recorte.tupla
    else:
        x, y, w, h = recorte

    altura, largura = img.shape[:2]
    x0 = int(np.clip(x, 0.0, 1.0) * largura)
    y0 = int(np.clip(y, 0.0, 1.0) * altura)
    x1 = int(np.clip(x + w, 0.0, 1.0) * largura)
    y1 = int(np.clip(y + h, 0.0, 1.0) * altura)

    if x1 - x0 < 8 or y1 - y0 < 8:  # recorte absurdo: melhor nao cortar
        return img
    return img[y0:y1, x0:x1].copy()
