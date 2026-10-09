"""Cortar as bordas: tira a borda preta do scanner e a sombra da margem.

Como funciona, em uma frase: o corte NAO procura a beirada do papel, procura a
tinta. Poe uma caixa em volta da massa da tinta (descartando a tinta mais de
fora, para a sujeira da margem nao segurar o corte), da uma folga e, desde
28/09/2026, nunca deixa a borda da caixa passar no meio de uma peca de tinta.

Quem chama: core/pipeline.py (preparar_metade, na hora de gravar e na previa;
analisar_projeto, so para os avisos). No projeto de antes de 09/10/2026
("cortar_antes"), depois do corte vem o endireitar, e `alargar_para_o_giro`
da ao corte a folga que o giro vai precisar. No livro novo
("endireitar_antes", item 2.2, G6) o corte e achado na pagina ja endireitada
e nao ha folga do giro (core/ordem_do_preparo.py).

"Seguir a beirada do papel" (o que o Samuel espera no Livro de Horas) NAO e
feito aqui: fica para a caixa da pagina do ScanTailor (itens 2.5 e 2.13 do
plano). Decisao do Samuel em 28/09.

Arriscado mudar (vale para o arquivo todo): este corte roda em TODA pagina de
TODO livro. Cada numero aqui foi acertado contra uma queixa real - sobra de
papel branco (5 de 16 paginas conferidas), sujeira da margem do Graduale 536,
vinco do Graduale 429, moldura do Palatino, comer letra e numero de pagina
(Escola 35, 28/09). Mexer em qualquer um exige medir de novo as paginas do
gabarito: quantas pecas de tinta o corte parte (tem de dar zero ou perto) e
quanto a folha cresce.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np

# Folga deixada em volta do conteudo: PELO MENOS 1 mm de papel entre a ultima
# tinta e a borda do corte (decisao do Samuel, conferencia 5, P2, 01/10/2026:
# "Sim, 1 mm"). Sem folga nenhuma o corte encosta na letra e o texto fica
# sufocado na impressao; com folga demais sobra papel em branco, que foi a
# queixa em cinco das dezesseis paginas que o Samuel conferiu.
#
# Ate 01/10 a folga era so FOLGA (meio por cento do lado), contada em pontos
# INTEIROS da imagem reduzida (ALTURA_ANALISE) e arredondada para baixo: na
# Escola 7 sobravam 0,6 mm dos lados, no Boecio (pagina de 9 cm) 0,4 mm. Agora
# a folga de cada lado e a MAIOR entre FOLGA_MM e a de antes: o lado que ja
# tinha 1 mm ou mais (de cima a baixo em quase toda pagina; tudo nas paginas
# grandes, Horas e Graduale) fica exatamente como estava. Diminuir a folga das
# paginas grandes para 1 mm foi medido em 01/10 e piorou o Graduale 223 (o
# numero da folha, que a folga de 2,5 mm pegava inteiro, saia partido).
#
# Milimetro "da pagina" = do PDF que sai: o PDF e gravado no DPI do projeto
# (projeto.qualidade_dpi), o mesmo em que o corte e calculado, entao 1 mm
# aqui e 1 mm no PDF (11,8 pontos a 300 DPI) e a mesma fracao na previa.
# Seguro mudar: FOLGA_MM. Arriscado: diminuir FOLGA (muda o corte das paginas
# aprovadas) e tirar FOLGA_PONTOS_EXTRAS.
FOLGA_MM = 1.0

# Dois pontos a mais na folga em milimetros, na resolucao da imagem: um porque
# quem corta de verdade (fatiar) converte a fracao em pontos arredondando para
# baixo; outro porque a mascara de tinta, feita na imagem reduzida, perde a
# beirada mais clara da letra (medido em 01/10: ate 1 ponto a 300 e a 600 DPI).
# Sem eles a folga ficava em 0,93 mm.
FOLGA_PONTOS_EXTRAS = 2

# A folga de antes de 01/10, em fracao do lado, contada em pontos inteiros da
# imagem reduzida (ver acima). E tambem a unica folga quando quem chama
# detectar_bordas nao diz o DPI da imagem (ver _folga_em_fracao).
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

# Risco comprido de margem nao e peca que o corte respeite (ver _pecas_de_tinta):
# peca mais comprida que PECA_GRANDE do lado (largura ou altura) E mais fina
# que PECA_FINA do outro lado. E a beirada torta da folha vizinha, a sombra da
# lombada, que nao chegaram a encostar na beirada da imagem; se o corte fosse
# ate o fim delas, voltava a queixa de "sobra papel em branco". Peca grande e
# larga ao mesmo tempo (a moldura dourada da Horas 47, a pauta do Graduale
# 222, uma gravura) e conteudo, e conta. Medido em 28/09 nas paginas do
# gabarito: sem a excecao da peca larga, a moldura da Horas 47 saia com 8
# pontas de folha cortadas.
PECA_GRANDE = 0.5
PECA_FINA = 0.05

# Quanto cada borda do corte pode andar para fora, de uma vez, para nao
# partir uma peca de tinta (fracao do lado). Medido em 28/09 nas paginas do
# gabarito: letra, numero de pagina, clave e inicial passam da caixa justa no
# maximo 1,6% do lado; o risco tracejado da beirada da folha (Horas 11, 14 e
# 26) passa 4% ou mais e, trecho por trecho, arrastava a borda de baixo ate
# 9% da altura. Peca que precisaria de mais que isso fica como estava.
# Arriscado mudar: subir traz de volta a margem que o corte existe para tirar;
# descer volta a partir letra.
ESTICAR_NO_MAXIMO = 0.02

# A folga do giro (alargar_para_o_giro) nunca traz fundo escuro do scanner:
# cada lado que cresce para antes da primeira coluna (ou linha) nova cuja media
# fique abaixo desta fracao do nivel do papel. No Marial 7 o papel fica em
# ~215 e o fundo do scanner em 45 a 90; a transicao (a beirada da folha)
# passa por ~130. Arriscado mudar: subir faz o giro parar em mancha escura de
# papel velho; descer deixa entrar a faixa escura (bug do Marial 7, 28/09).
ESCURO_DO_SCANNER = 0.6


@dataclass(frozen=True)
class Recorte:
    """Área util da página, em fracao de 0 a 1: (x, y, largura, altura).

    `pecas` e de uso interno (nao entra na comparacao, no hash nem no repr):
    as caixas das pecas de tinta da mascara do corte, em fracao da pagina,
    uma por linha (x0, y0, x1, y1, risco) - ver _pecas_de_tinta. Serve para
    `alargar_para_o_giro` aumentar o corte sem partir peca nenhuma e sem
    refazer a mascara de tinta (o que custaria tempo em cada pagina e em cada
    previa). None quando nao ha (recorte inteiro, recorte manual).
    """

    x: float
    y: float
    largura: float
    altura: float
    encostou_no_conteudo: bool = False
    pecas: np.ndarray | None = field(default=None, compare=False, repr=False)

    @property
    def tupla(self) -> tuple[float, float, float, float]:
        """(x, y, largura, altura) como tupla simples, para serializar/comparar."""
        return (self.x, self.y, self.largura, self.altura)

    @staticmethod
    def inteiro() -> "Recorte":
        """Recorte que cobre a folha inteira - usado quando nao ha o que cortar."""
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

        # A imagem em cinza vai como esta: _pagina_sem_conteudo trabalha no
        # cinza, e cinza -> cor -> cinza devolve os mesmos valores (conferido
        # nos 256 niveis, 09/10/2026). Antes ia para cor e voltava: duas
        # conversoes da pagina inteira a toa (item 2.2, G6: o corte do livro
        # novo e medido na pagina em cinza; regra 6, velocidade).
        return _pagina_sem_conteudo(img)
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


def detectar_bordas(img: np.ndarray, dpi: float | None = None) -> Recorte:
    """Acha o retangulo que contem o conteúdo da página.

    Ideia: binarizar de forma bem tolerante, achar as linhas e colunas que tem
    tinta de verdade e envolver tudo isso. Bordas pretas do scanner ficam
    coladas na moldura, entao são descartadas por serem grandes demais para
    caberem no limite de CORTE_MAXIMO.

    Desde 28/09/2026 a borda da caixa nunca passa no meio de uma peca de
    tinta (ver _nao_partir_pecas). Quem vai endireitar depois chama
    alargar_para_o_giro com o angulo, para o giro nao levar os cantos.

    `dpi`: a resolucao em que `img` foi desenhada. Com ele, a folga em volta
    do conteudo e de pelo menos FOLGA_MM milimetros (desde 01/10/2026); sem
    ele (None), e a folga de antes (FOLGA do lado). O programa passa o DPI
    sempre que sabe (pipeline._geometria). Ver _folga_em_fracao.
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

    # Nao partir peca de tinta (conserto de 28/09/2026, Lista de bugs).
    #
    # O descarte acima olha so a SOMA da tinta por coluna e por linha, e a
    # borda da caixa caia no meio da tinta de verdade: o comeco e o fim das
    # linhas, o "7" do "37" da Escola 35, as claves do Graduale 222, o numero
    # da pagina do Opus Majus - 77 pecas partidas em 13 das paginas do
    # gabarito. Agora, quando a borda atravessa uma peca de tinta, ela vai ate
    # o fim da peca. A sujeira que o descarte existe para ignorar continua
    # ignorada: a peca que esta INTEIRA fora da caixa nao puxa nada, e a que
    # encosta na beirada da imagem (borda de scanner, folha vizinha) nem e
    # peca. Ver _pecas_de_tinta e _nao_partir_pecas.
    pecas = _pecas_de_tinta(tinta)
    respeitar, pode_x, pode_y = _quem_empurra(pecas, largura, altura)
    esticar_x, esticar_y = largura * ESTICAR_NO_MAXIMO, altura * ESTICAR_NO_MAXIMO
    x0, y0, x1, y1 = (int(v) for v in _nao_partir_pecas(respeitar, x0, y0, x1, y1,
                                                         esticar_x, esticar_y, pode_x, pode_y))

    # Daqui em diante, tudo em FRACAO da pagina (conserto de 01/10/2026,
    # conferencia 5, P2). A caixa justa acima e em pontos da imagem reduzida;
    # a folga e somada em fracao, sem arredondar para pontos inteiros da
    # imagem reduzida (era o que deixava 0,6 mm em vez de 1 mm). As pecas e o
    # limite de esticar vao para fracao tambem, como em alargar_para_o_giro.
    por_ponto = np.array([largura, altura, largura, altura], np.float64)
    pecas_fracao = np.hstack([pecas[:, :4].astype(np.float64) / por_ponto,
                              pecas[:, 4:].astype(np.float64)])
    respeitar_fracao = respeitar.astype(np.float64) / por_ponto
    x0e, y0e, x1e, y1e = x0 / largura, y0 / altura, x1 / largura, y1 / altura

    # folga (FOLGA_MM ou a de antes, a maior; ver _folga_em_fracao)
    folga_x, folga_y = _folga_em_fracao(largura, altura, largura_orig, altura_orig, dpi)
    antes_x, antes_y = _folga_em_fracao(largura, altura, largura_orig, altura_orig, None)
    justa = (x0e, y0e, x1e, y1e)
    x0e, y0e, x1e, y1e = _com_folga(justa, folga_x, folga_y)
    # A folga a mais (o que passa da folga de antes de 01/10) nunca traz o
    # fundo escuro do scanner: no Siebmacher 7 e 9 a borda de baixo ja estava
    # colada na faixa escura, e 1 mm a mais a trazia para dentro (medido em
    # 01/10). Mesma regra da folga do giro (_parar_no_escuro).
    if (folga_x, folga_y) != (antes_x, antes_y):
        x0e, y0e, x1e, y1e = _parar_no_escuro(
            img, _recorte_da_caixa(_com_folga(justa, antes_x, antes_y)), x0e, y0e, x1e, y1e)

    # limite de seguranca: nunca comer mais que CORTE_MAXIMO de um lado
    x0e, y0e = min(x0e, CORTE_MAXIMO), min(y0e, CORTE_MAXIMO)
    x1e, y1e = max(x1e, 1.0 - CORTE_MAXIMO), max(y1e, 1.0 - CORTE_MAXIMO)

    # A folga e o limite afastam a borda, e ela pode ter caido em cima de
    # outra peca (um ponto, um acento logo depois do fim da linha, o reclamo
    # no pe da pagina que o descarte da tinta de fora deixou de fora). A borda
    # vai ate o fim dessa peca e, desde 01/10/2026, se a peca e do tamanho de
    # uma letra (_de_letra), ganha a folga de novo depois dela: antes o
    # reclamo "A i" do pe do Palatino 7 ficava com 1 ponto de papel. Cisco
    # nao ganha folga: no Palatino 7 os pontinhos da margem direita levavam a
    # borda 3 mm para fora. Duas voltas bastam (a segunda so pega a peca que a
    # folga nova alcancou). O limite de ESTICAR_NO_MAXIMO vale para as voltas
    # JUNTAS, contado de onde a borda estava antes da primeira (`ate_onde`):
    # se valesse para cada volta, o risco tracejado da beirada (Horas 14)
    # voltava a arrastar a borda trecho por trecho
    # (test_o_risco_tracejado_da_beirada_nao_arrasta_o_corte).
    ate_onde = (x0e - ESTICAR_NO_MAXIMO, y0e - ESTICAR_NO_MAXIMO,
                x1e + ESTICAR_NO_MAXIMO, y1e + ESTICAR_NO_MAXIMO)
    letra = _de_letra(respeitar)
    for volta in range(3):
        antes = (x0e, y0e, x1e, y1e)
        x0e, y0e, x1e, y1e = _dentro_da_pagina(_nao_partir_pecas(
            respeitar_fracao, *antes, ESTICAR_NO_MAXIMO, ESTICAR_NO_MAXIMO,
            pode_x, pode_y, ate_onde))
        if volta == 2 or (x0e, y0e, x1e, y1e) == antes or not letra.any():
            break
        # so o lado que andou para pegar uma LETRA ganha a folga de novo
        l0, m0, l1, m1 = _dentro_da_pagina(_nao_partir_pecas(
            respeitar_fracao[letra], *antes, ESTICAR_NO_MAXIMO, ESTICAR_NO_MAXIMO,
            pode_x[letra], pode_y[letra], ate_onde))
        atual = (x0e, y0e, x1e, y1e)
        x0e = max(0.0, x0e - folga_x) if l0 < antes[0] else x0e
        y0e = max(0.0, y0e - folga_y) if m0 < antes[1] else y0e
        x1e = min(1.0, x1e + folga_x) if l1 > antes[2] else x1e
        y1e = min(1.0, y1e + folga_y) if m1 > antes[3] else y1e
        if (x0e, y0e, x1e, y1e) == atual:
            break
        x0e, y0e, x1e, y1e = _parar_no_escuro(img, _recorte_da_caixa(atual), x0e, y0e, x1e, y1e)

    # o que sobrou fora, olhado na mascara (pontos inteiros, para fora)
    encostou = _sobrou_conteudo_fora(
        tinta, int(math.floor(x0e * largura)), int(math.floor(y0e * altura)),
        int(math.ceil(x1e * largura)), int(math.ceil(y1e * altura)))

    return Recorte(
        x=x0e,
        y=y0e,
        largura=x1e - x0e,
        altura=y1e - y0e,
        encostou_no_conteudo=bool(encostou),
        pecas=pecas_fracao,
    )


def _com_folga(caixa, folga_x: float, folga_y: float):
    """A caixa (x0, y0, x1, y1), em fracao, aumentada da folga, sem passar da pagina."""
    x0, y0, x1, y1 = caixa
    return _dentro_da_pagina((x0 - folga_x, y0 - folga_y, x1 + folga_x, y1 + folga_y))


def _dentro_da_pagina(caixa):
    """A caixa (x0, y0, x1, y1), em fracao, limitada a pagina (0 a 1), em float."""
    x0, y0, x1, y1 = (float(v) for v in caixa)
    return max(0.0, x0), max(0.0, y0), min(1.0, x1), min(1.0, y1)


def _recorte_da_caixa(caixa) -> Recorte:
    """Recorte de uma caixa (x0, y0, x1, y1) em fracao (para _parar_no_escuro)."""
    x0, y0, x1, y1 = caixa
    return Recorte(x0, y0, x1 - x0, y1 - y0)


# Peca do tamanho de uma letra, em pontos da imagem reduzida (ALTURA_ANALISE):
# pelo menos LETRA_MINIMA de um lado e LETRA_FINA do outro. Abaixo disso e
# cisco (os pontinhos da margem do Palatino 7 tem 1 a 2 pontos). Uma letra de
# texto comum tem 4 pontos ou mais de altura; um ponto final, 2 x 2, e passa
# se estiver grudado na palavra (o fechamento 5 x 5 junta). Arriscado mudar:
# descer faz cisco ganhar folga (a borda vai 3 mm para fora no Palatino 7);
# subir faz letra pequena ficar sem a folga.
LETRA_MINIMA = 4
LETRA_FINA = 2


def _de_letra(pecas: np.ndarray) -> np.ndarray:
    """Quais pecas (caixas em pontos da imagem reduzida) tem tamanho de letra."""
    if len(pecas) == 0:
        return np.zeros(0, bool)
    larg = pecas[:, 2] - pecas[:, 0]
    alt = pecas[:, 3] - pecas[:, 1]
    return (np.maximum(larg, alt) >= LETRA_MINIMA) & (np.minimum(larg, alt) >= LETRA_FINA)


def _folga_em_fracao(largura: int, altura: int, largura_px: int, altura_px: int,
                     dpi: float | None) -> tuple[float, float]:
    """A folga do corte de cada lado, em fracao da largura e da altura.

    `largura`, `altura`: o tamanho da imagem reduzida em que o corte e
    calculado (a mascara de tinta). `largura_px`, `altura_px`: o tamanho da
    imagem inteira, na resolucao `dpi`.

    A folga e a maior entre FOLGA_MM milimetros (mais FOLGA_PONTOS_EXTRAS
    pontos da imagem inteira) e a folga de antes de 01/10 (FOLGA do lado,
    em pontos inteiros da imagem reduzida). Sem `dpi` (quem chamou nao sabe
    a resolucao), so a de antes.

    Arriscado mudar: contar a folga em milimetros so em pontos da imagem
    reduzida traz de volta o arredondamento que comia a folga; tirar a
    "de antes" encolhe a folga das paginas grandes e muda o corte delas.
    """
    antes_x = int(largura * FOLGA) / max(1, largura)
    antes_y = int(altura * FOLGA) / max(1, altura)
    if not dpi or dpi <= 0:
        return antes_x, antes_y
    pontos = FOLGA_MM * float(dpi) / 25.4 + FOLGA_PONTOS_EXTRAS
    return (max(antes_x, pontos / max(1, largura_px)),
            max(antes_y, pontos / max(1, altura_px)))


def _pecas_de_tinta(tinta: np.ndarray) -> np.ndarray:
    """As pecas de tinta da mascara do corte, uma por linha.

    Peca = um pedaco ligado da mascara que o corte usa (ja com o fechamento
    5x5, que junta as letras de uma palavra; sem a borda do scanner e sem as
    riscas do vinco). Cada linha: (x0, y0, x1, y1, risco), em pontos da
    mascara, com x1 e y1 um depois do ultimo ponto, como o resto do arquivo.

    A peca que encosta na beirada da imagem fica de fora: e borda de scanner,
    sombra da lombada ou folha vizinha, justamente o que o corte existe para
    tirar.

    `risco` = 1 para o risco comprido e fino: maior que PECA_GRANDE num lado e
    mais fino que PECA_FINA no outro (ver PECA_GRANDE). Quais bordas ele pode
    empurrar: ver _quem_empurra. Se ele esta dentro do corte, o giro o
    respeita (um fio de tabela, a regua embaixo do titulo). Peca grande e
    larga (moldura, gravura) nao e risco: e conteudo.

    Arriscado mudar: aceitar peca que encosta na beirada faz o corte voltar a
    manter a folha inteira em qualquer pagina com borda de scanner.
    """
    altura, largura = tinta.shape[:2]
    n, _, caixas, _ = cv2.connectedComponentsWithStats(tinta.astype(np.uint8), connectivity=8)
    if n <= 1:
        return np.zeros((0, 5), np.int64)
    x, y, w, h = (caixas[1:, i].astype(np.int64) for i in range(4))
    encosta = (x <= 1) | (y <= 1) | (x + w >= largura - 1) | (y + h >= altura - 1)
    comprida = (w > PECA_GRANDE * largura) | (h > PECA_GRANDE * altura)
    fina = np.minimum(w / largura, h / altura) < PECA_FINA
    risco = (comprida & fina).astype(np.int64)
    fica = ~encosta
    return np.stack([x[fica], y[fica], (x + w)[fica], (y + h)[fica], risco[fica]], axis=1)


def _quem_empurra(pecas: np.ndarray, largura: float, altura: float):
    """Das pecas de _pecas_de_tinta, quais podem empurrar que borda do corte.

    Devolve (caixas, pode_x, pode_y), prontos para _nao_partir_pecas.
    `largura` e `altura` na mesma unidade das pecas (pontos da mascara em
    detectar_bordas; 1.0 e 1.0 quando as pecas estao em fracao da pagina).

    - Peca comum: empurra as quatro bordas.
    - Risco comprido e fino (coluna `risco`): so empurra as bordas PARALELAS a
      ele, e so se estiver fora da faixa de MOLDURA (3%) colada na beirada da
      imagem. Um risco vertical (a beirada torta da folha vizinha, o tracejado
      da Horas 26) nunca puxa o topo ou o pe - era ele que arrastava o pe da
      Horas 14 -, e um risco colado na beirada e a propria beirada da folha.
      Mas um risco horizontal no meio da pagina e conteudo: a pauta do
      Graduale 222, com a clave grudada nela, virava uma peca so de 75% x 4%,
      e a ponta da clave saia cortada (verificador, 28/09).

    Arriscado mudar: deixar o risco empurrar a borda perpendicular traz de
    volta o tracejado arrastando o corte; tirar o teste da faixa de 3% deixa a
    beirada da folha segurar o corte.
    """
    a0, b0, a1, b1, risco = (pecas[:, i] for i in range(5))
    risco = risco > 0
    horizontal = (a1 - a0) > PECA_GRANDE * largura
    fora_da_faixa_y = (b0 >= MOLDURA * altura) & (b1 <= (1.0 - MOLDURA) * altura)
    fora_da_faixa_x = (a0 >= MOLDURA * largura) & (a1 <= (1.0 - MOLDURA) * largura)
    pode_y = ~risco | (horizontal & fora_da_faixa_y)
    pode_x = ~risco | (~horizontal & fora_da_faixa_x)
    usar = pode_x | pode_y
    return pecas[usar, :4], pode_x[usar], pode_y[usar]


def _nao_partir_pecas(pecas: np.ndarray, x0, y0, x1, y1, esticar_x, esticar_y,
                      pode_x=None, pode_y=None, ate_onde=None):
    """Afasta cada borda da caixa ate o fim de toda peca que ela atravessa.

    `pecas` e a caixa (x0, y0, x1, y1) de cada peca, na MESMA unidade da caixa
    (pontos da mascara em detectar_bordas, fracao da pagina em
    alargar_para_o_giro). Uma peca e atravessada pela borda esquerda quando
    comeca antes dela e termina depois, e esta na altura da caixa; e o mesmo
    para as outras tres bordas.

    Repete ate nenhuma borda atravessar peca nenhuma, porque afastar uma borda
    pode fazer ela cair em cima da peca vizinha. So afasta, nunca aperta: o
    corte so pode ficar do mesmo tamanho ou maior. A peca inteira do lado de
    fora continua fora (e o descarte da sujeira da margem).

    Cada borda anda no maximo `esticar_x` (esquerda, direita) ou `esticar_y`
    (topo, pe) a partir de onde estava ao entrar aqui (ver ESTICAR_NO_MAXIMO):
    a peca que precisaria de mais que isso e risco que entra pela margem, nao
    letra, e continua cortada.

    `pode_x` e `pode_y` (listas de sim/nao, uma por peca; None = todas podem)
    dizem que peca pode empurrar as bordas da esquerda e da direita (pode_x) e
    as de cima e de baixo (pode_y). Ver _quem_empurra.

    `ate_onde` (x0, y0, x1, y1), opcional: ate onde cada borda pode ir, no
    lugar de "onde estava ao entrar mais o esticar" (detectar_bordas usa para
    o limite valer para todas as voltas da folga, e nao para cada uma).

    Arriscado mudar: tirar o "esta na altura da caixa" faz uma peca do canto,
    fora da caixa, puxar a borda; tirar a repeticao deixa peca partida; tirar
    o limite deixa o risco tracejado arrastar a borda trecho por trecho.
    """
    if len(pecas) == 0:
        return x0, y0, x1, y1
    a0, b0, a1, b1 = pecas[:, 0], pecas[:, 1], pecas[:, 2], pecas[:, 3]
    todas = np.ones(len(pecas), bool)
    pode_x = todas if pode_x is None else pode_x
    pode_y = todas if pode_y is None else pode_y
    # ate onde cada borda pode ir
    x0_max, y0_max = x0 - esticar_x, y0 - esticar_y
    x1_max, y1_max = x1 + esticar_x, y1 + esticar_y
    if ate_onde is not None:
        x0_max, y0_max, x1_max, y1_max = ate_onde
    # Cada volta afasta pelo menos uma borda ate o fim de uma peca, entao o
    # numero de voltas e no maximo o de pecas; o limite so protege de laco.
    for _ in range(len(pecas) + 1):
        na_altura = (b1 > y0) & (b0 < y1)
        na_largura = (a1 > x0) & (a0 < x1)
        esquerda = pode_x & na_altura & (a0 < x0) & (a1 > x0) & (a0 >= x0_max)
        direita = pode_x & na_altura & (a0 < x1) & (a1 > x1) & (a1 <= x1_max)
        topo = pode_y & na_largura & (b0 < y0) & (b1 > y0) & (b0 >= y0_max)
        pe = pode_y & na_largura & (b0 < y1) & (b1 > y1) & (b1 <= y1_max)
        if not (esquerda.any() or direita.any() or topo.any() or pe.any()):
            break
        if esquerda.any():
            x0 = a0[esquerda].min()
        if direita.any():
            x1 = a1[direita].max()
        if topo.any():
            y0 = b0[topo].min()
        if pe.any():
            y1 = b1[pe].max()
    return x0, y0, x1, y1


def alargar_para_o_giro(recorte: Recorte, angulo: float, img: np.ndarray) -> Recorte:
    """Aumenta o corte automatico so onde o endireitar empurraria tinta para fora.

    O endireitar gira a pagina DEPOIS do corte, dentro do mesmo retangulo (ver
    core/endireitar.py, rotacionar), e os cantos do conteudo saiam da folha:
    na Escola 35 (-0,8 grau) o comeco das linhas de baixo sumia, ate 1,8 mm.

    Aqui as caixas das pecas de tinta que estao dentro do corte (guardadas em
    recorte.pecas por detectar_bordas) sao giradas pelo mesmo angulo e em
    volta do mesmo centro que o rotacionar usa, e cada lado do corte cresce o
    que for preciso para elas caberem (mais 2 pontos de arredondamento). O
    lado onde ha margem de papel sobrando nao cresce: aumentar os quatro lados
    pelo pior caso trazia a beirada do livro e o fundo escuro do scanner para
    dentro (Schon 73, 28/09). Como mudar o tamanho move o centro do giro, a
    conta e refeita 3 vezes (na ultima o centro ja quase nao anda).
    Depois, o mesmo cuidado de detectar_bordas: a borda nova nao pode partir
    peca de tinta.

    `img` e a imagem que vai ser cortada (a pagina inteira, antes do corte).
    Devolve o recorte do mesmo jeito quando o angulo e zero ou quando ele nao
    tem pecas (folha inteira, pagina em branco). Nunca passa da beirada da
    imagem: se o conteudo ja encosta nela, o giro ainda pode levar uma
    lasquinha do canto (ressalva de 28/09).

    Nunca traz fundo escuro do scanner (conserto de 28/09, noite; ver
    _parar_no_escuro e ESCURO_DO_SCANNER). No Marial 7 a beirada da folha, em
    "L" no canto de baixo a direita, estava dentro do corte; a folga do giro
    tentou protege-la e levou o corte ate o fim da imagem, e entrou uma faixa
    escura de 2 mm na borda direita inteira. Agora o giro volta a poder levar
    uma lasquinha dessa beirada no canto, como antes do conserto. A distancia
    ate a beirada NAO serve de regra: o numero da folha do Graduale 223 fica a
    2,7% do alto e precisa da folga (testes em
    tests/test_corte_nao_come_conteudo.py).

    A ordem do CLAUDE.md continua: cortar -> endireitar. So o tamanho do corte
    muda. Seguro mudar: os 2 pontos de arredondamento. Arriscado mudar: usar
    isto no recorte que a pessoa escolheu a mao (ele tem de sair como ela
    escolheu - preparar_metade so chama para o corte automatico); o centro e o
    sinal do giro, que tem de ser os do rotacionar.
    """
    if not angulo or recorte.pecas is None or len(recorte.pecas) == 0:
        return recorte
    altura_px, largura_px = img.shape[0], img.shape[1]
    x0, y0 = recorte.x, recorte.y
    x1, y1 = recorte.x + recorte.largura, recorte.y + recorte.altura
    pecas = recorte.pecas
    dentro = ((pecas[:, 0] >= x0) & (pecas[:, 1] >= y0)
              & (pecas[:, 2] <= x1) & (pecas[:, 3] <= y1))
    if not dentro.any():
        return recorte

    # os quatro cantos de cada peca de dentro, em pontos da imagem
    caixas = pecas[dentro]
    cantos = np.concatenate([
        np.stack([caixas[:, i] * largura_px, caixas[:, j] * altura_px], axis=1)
        for i in (0, 2) for j in (1, 3)
    ])
    X0, Y0, X1, Y1 = x0 * largura_px, y0 * altura_px, x1 * largura_px, y1 * altura_px
    for _ in range(3):
        centro = ((X0 + X1) / 2.0, (Y0 + Y1) / 2.0)
        matriz = cv2.getRotationMatrix2D(centro, angulo, 1.0)   # o mesmo do rotacionar
        girados = cantos @ matriz[:, :2].T + matriz[:, 2]
        X0 = max(0.0, min(X0, float(girados[:, 0].min()) - 2))
        Y0 = max(0.0, min(Y0, float(girados[:, 1].min()) - 2))
        X1 = min(float(largura_px), max(X1, float(girados[:, 0].max()) + 2))
        Y1 = min(float(altura_px), max(Y1, float(girados[:, 1].max()) + 2))

    x0, y0 = X0 / largura_px, Y0 / altura_px
    x1, y1 = X1 / largura_px, Y1 / altura_px
    respeitar, pode_x, pode_y = _quem_empurra(pecas, 1.0, 1.0)
    x0, y0, x1, y1 = _nao_partir_pecas(respeitar, x0, y0, x1, y1,
                                       ESTICAR_NO_MAXIMO, ESTICAR_NO_MAXIMO, pode_x, pode_y)
    x0, y0 = max(0.0, float(x0)), max(0.0, float(y0))
    x1, y1 = min(1.0, float(x1)), min(1.0, float(y1))
    x0, y0, x1, y1 = _parar_no_escuro(img, recorte, x0, y0, x1, y1)

    return Recorte(
        x=x0, y=y0, largura=x1 - x0, altura=y1 - y0,
        encostou_no_conteudo=recorte.encostou_no_conteudo,
        pecas=recorte.pecas,
    )


def _parar_no_escuro(img: np.ndarray, velho: Recorte, x0, y0, x1, y1):
    """Recolhe cada lado que a folga do giro fez crescer ate antes do escuro.

    Olha so a faixa nova (entre a borda de `velho` e a borda nova), coluna por
    coluna (esquerda, direita) ou linha por linha (topo, pe), andando para
    fora; para na primeira cuja media fique abaixo de ESCURO_DO_SCANNER vezes o
    nivel do papel. O nivel do papel e o percentil 90 do cinza dentro do corte
    velho (amostrado de 8 em 8 pontos: rapido, e o papel e a maioria clara).
    Tudo em fracao da pagina, como o resto do arquivo.

    Arriscado mudar: aplicar isto ao corte de detectar_bordas (e nao so a
    folga do giro) mudaria o corte de todas as paginas.
    """
    altura, largura = img.shape[:2]
    cinza_de = (lambda m: m) if img.ndim == 2 else (lambda m: cv2.cvtColor(m, cv2.COLOR_BGR2GRAY))
    vx0, vy0 = int(velho.x * largura), int(velho.y * altura)
    vx1 = int((velho.x + velho.largura) * largura)
    vy1 = int((velho.y + velho.altura) * altura)
    X0, Y0 = int(x0 * largura), int(y0 * altura)
    X1, Y1 = int(np.ceil(x1 * largura)), int(np.ceil(y1 * altura))
    if X0 >= vx0 and Y0 >= vy0 and X1 <= vx1 and Y1 <= vy1:
        return x0, y0, x1, y1                    # nada cresceu
    # A media de cada coluna (ou linha) nova, andando da borda velha para
    # fora. Calculada ANTES do nivel do papel: se nenhuma passa perto do
    # escuro (o limite nunca passa de ESCURO_DO_SCANNER x 255), nao ha o que
    # recolher e o percentil da pagina nem e calculado - o caso de quase toda
    # pagina, e o que deixou a folga de 1 mm (01/10/2026) sem custo de tempo.
    medias = {}
    if X0 < vx0:          # esquerda: da borda velha para fora
        medias["esq"] = cinza_de(img[Y0:Y1, X0:vx0]).mean(axis=0)[::-1]
    if X1 > vx1:          # direita
        medias["dir"] = cinza_de(img[Y0:Y1, vx1:X1]).mean(axis=0)
    if Y0 < vy0:          # topo
        medias["topo"] = cinza_de(img[Y0:vy0, X0:X1]).mean(axis=1)[::-1]
    if Y1 > vy1:          # pe
        medias["pe"] = cinza_de(img[vy1:Y1, X0:X1]).mean(axis=1)
    if not any(m.size and float(m.min()) < ESCURO_DO_SCANNER * 255.0 for m in medias.values()):
        return x0, y0, x1, y1
    amostra = cinza_de(np.ascontiguousarray(img[vy0:vy1:8, vx0:vx1:8]))
    if amostra.size == 0:
        return x0, y0, x1, y1
    limite = ESCURO_DO_SCANNER * float(np.percentile(amostra, 90))

    def primeira_escura(lado):
        if lado not in medias:
            return None
        escuras = np.flatnonzero(medias[lado] < limite)
        return int(escuras[0]) if escuras.size else None

    if (k := primeira_escura("esq")) is not None:
        x0 = (vx0 - k) / largura
    if (k := primeira_escura("dir")) is not None:
        x1 = (vx1 + k) / largura
    if (k := primeira_escura("topo")) is not None:
        y0 = (vy0 - k) / altura
    if (k := primeira_escura("pe")) is not None:
        y1 = (vy1 + k) / altura
    return x0, y0, x1, y1


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
    """Corta a imagem pelo retangulo relativo dado (devolve uma copia)."""
    fatia = fatiar(img, recorte)
    return img if fatia is img else fatia.copy()


def fatiar(img: np.ndarray, recorte: Recorte | tuple) -> np.ndarray:
    """O mesmo corte de aplicar_recorte, mas SEM copiar: uma vista da imagem.

    So para quem vai gerar uma imagem nova logo em seguida (o rotacionar, em
    preparar_metade): poupa copiar a pagina inteira a 300 DPI (ate 80 MB no
    Livro de Horas). Arriscado: escrever na vista escreve na imagem original.
    """
    caixa = caixa_em_pontos(img.shape, recorte)
    if caixa is None:               # recorte absurdo: melhor nao cortar
        return img
    x0, y0, x1, y1 = caixa
    return img[y0:y1, x0:x1]


def caixa_em_pontos(forma, recorte: Recorte | tuple) -> tuple[int, int, int, int] | None:
    """O retangulo relativo `recorte` em pontos (x0, y0, x1, y1) de uma imagem
    de forma `forma` (img.shape), arredondado como fatiar corta; None quando o
    recorte e absurdo (menos de 8 pontos de lado: melhor nao cortar).

    E a conta de fatiar, separada para o endireitar antes de cortar (item 2.2,
    G6, core/endireitar.rotacionar_e_cortar) cortar EXATAMENTE os mesmos
    pontos. Arriscado: mudar o arredondamento (o corte de todo livro anda um
    ponto, e o projeto antigo deixa de sair identico)."""
    if isinstance(recorte, Recorte):
        x, y, w, h = recorte.tupla
    else:
        x, y, w, h = recorte

    altura, largura = forma[:2]
    x0 = int(np.clip(x, 0.0, 1.0) * largura)
    y0 = int(np.clip(y, 0.0, 1.0) * altura)
    x1 = int(np.clip(x + w, 0.0, 1.0) * largura)
    y1 = int(np.clip(y + h, 0.0, 1.0) * altura)

    if x1 - x0 < 8 or y1 - y0 < 8:
        return None
    return x0, y0, x1, y1
