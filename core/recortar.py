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

# Abaixo deste angulo o endireitar nao gira a pagina (nao ha cunha do giro):
# o mesmo numero do rotacionar. core/endireitar so depende do cv2 e do numpy.
from core.endireitar import ANGULO_MINIMO

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

    No livro novo a pergunta e feita na pagina COMO VEIO, nao na endireitada
    (detectar_bordas, `como_veio`; conserto de 20/10/2026, Pesel 21).
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


# ---------------------------------------------------------------------------
# A cunha do giro (conserto de 13/10/2026; bug que entrou com o G6 em 12/10)
#
# No livro novo ("endireitar_antes") a pagina e girada INTEIRA antes de o
# corte ser procurado (core/pipeline._geometria_endireitando_antes), e o giro
# (core/endireitar.rotacionar) pinta de branco as cunhas que sobram nas
# beiradas. Esse branco fica entre a beirada da imagem e a borda preta do
# scanner, e a busca do corte, feita para a borda preta ENCOSTADA na beirada,
# deixava de reconhece-la de dois jeitos (verificador, 13/10, 89 paginas:
# relatorios/conferir/corte-g6-2026-10-13, ramo verif-corte-g6-2026-10-13):
#
# 1. _apagar_bordas_solidas anda da beirada para dentro enquanto a coluna (ou
#    linha) for 80% tinta; com a cunha branca a coluna de fora caia de 100%
#    para 73% e nada era apagado (Cursus 3: 16 mm de faixa preta a direita;
#    Matematica 32: 44 mm; Camoes 104).
# 2. onde o fundo do scanner e preto LISO o limiar local nao ve tinta
#    nenhuma; o degrau do branco da cunha para o preto cria "tinta" bem na
#    beirada, e a caixa da tinta ia ate o fim da folha (Antiphon 88 e 260).
#
# 3. o que encostava na beirada da imagem (o contorno da folha de baixo, no
#    canto) nao era "peca"; com a cunha branca no meio virava peca solta e
#    empurrava o corte 13 mm para dentro do preto (Antiphon 260).
#
# 4. (achado em 20/10/2026, depois da conferencia do Samuel de 13/10, quadro
#    do Pesel 21: "Ele chega a quase cortar as letras.") a pergunta "ha o
#    que recortar?" (_sem_conteudo_para_recortar) e feita pela mediana da
#    pagina. O cartao pardo do livro de bordados da Pesel tem dois tons
#    quase meio a meio (cartao ~60 a 95, tecido ~190): como veio, a mediana
#    cai no cartao e a pagina NAO e recortada (folha inteira, na ordem
#    antiga e no fase-1); girada, os ~2% de branco da cunha (e os cantos do
#    cartao que saem da imagem) fazem a mediana pular para o tecido (102 ->
#    125) e a pagina passava a ser recortada. Antes do conserto da cunha o
#    erro ficava escondido pelo degrau branco (caminho 2), que segurava o
#    corte na folha inteira; tirado o degrau, o Pesel 21 saia cortado rente
#    (15,7 x 24,1 -> 14,5 x 20,6 cm, legenda a 1 ou 2 mm da borda).
#    Conserto: a pergunta e feita na pagina como veio (detectar_bordas,
#    `como_veio`), a mesma resposta da ordem antiga. Tirar so a cunha da
#    conta nao bastava: a pagina de teste a 2 graus continuava virando,
#    pelos cantos que o giro leva embora (medido em 20/10/2026).
#
# O conserto: quando quem chama diz de quanto a pagina foi girada
# (detectar_bordas, `girada`), a busca sabe quais pontos sao cunha e os deixa
# de fora dessas contas. O apagar de sempre (_apagar_bordas_solidas e
# _apagar_riscas_de_dobra) continua igual, ponto por ponto; a mascara de
# tinta so PERDE mais duas coisas: as linhas e colunas de borda solida
# contadas so na imagem de verdade (_apagar_bordas_solidas_fora_da_cunha) e a
# tinta que so existe por causa do degrau branco (_tinta_falsa_da_cunha). E,
# so na hora de achar as pecas, o pedaco grande colado na cunha deixa de ser
# peca (_sem_as_pecas_grandes_coladas_na_cunha).
#
# Por que "somar ao apagar de hoje" em vez de trocar a conta: medido nas 43
# paginas que giram (relatorios/conserto-corte-g6, experiencia.py). Trocar a
# borda solida pela conta nova tirava do apagar das riscas a coluna que ele
# usava (Marial 7 ganhava 2 mm de faixa a direita, Camoes 66 piorava); tratar
# a cunha como "nao existe" em tudo (limiar local, riscas, pecas) desfazia o
# que o G6 melhorou (o numero da folha do Graduale 221 e 223 voltava a sair
# cortado; Egenloff 3 ganhava preto; Escola 197 perdia 3,9% da tinta). Do
# jeito adotado, o corte muda em 9 das 43 e nenhuma piora.
#
# Arriscado mudar: aplicar isto sem `girada` (o caminho do projeto antigo e
# da pagina como veio tem de continuar identico ponto por ponto); usar a
# conta nova NO LUGAR da de sempre (ver acima).
# ---------------------------------------------------------------------------

# Ponto da imagem reduzida que e imagem de verdade: coberto pela pagina
# girada em pelo menos isto. Abaixo, e cunha (ou mistura com o branco dela).
COBERTURA_DE_IMAGEM = 0.999


def _cunha_do_giro(forma, angulo: float) -> np.ndarray:
    """Quais pontos de uma imagem de forma `forma` NAO vieram da pagina,
    depois de ela ser girada `angulo` graus em volta do centro, no mesmo
    tamanho (core/endireitar.rotacionar): as cunhas das quatro beiradas, mais
    os pontos da divisa, que sao mistura da pagina com o branco.

    A conta e feita direto no tamanho de `forma` (a imagem reduzida da busca
    do corte): gira-se uma folha toda "1" com fundo "0" e fica cunha o que
    nao chega a COBERTURA_DE_IMAGEM. Custa um giro de 800 pontos de altura.

    Arriscado mudar: o centro e o sinal do giro tem de ser os do rotacionar,
    senao a cunha cai do lado errado da pagina."""
    altura, largura = forma[:2]
    matriz = cv2.getRotationMatrix2D((largura / 2.0, altura / 2.0), angulo, 1.0)
    cobre = cv2.warpAffine(np.ones((altura, largura), np.float32), matriz, (largura, altura),
                           flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return cobre < COBERTURA_DE_IMAGEM


def _preencher_a_cunha(cinza: np.ndarray, cunha: np.ndarray) -> np.ndarray:
    """A imagem com cada ponto da cunha trocado pelo ponto de imagem de
    verdade mais proximo (uma copia; `cinza` nao muda). So para a conta de
    _tinta_falsa_da_cunha: sem o degrau branco, o limiar local ve o fundo do
    scanner como ele e."""
    _distancia, rotulos = cv2.distanceTransformWithLabels(
        cunha.astype(np.uint8), cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
    # rotulos: em cada ponto, o numero do ponto de imagem mais proximo
    valores = np.zeros(int(rotulos.max()) + 1, cinza.dtype)
    valores[rotulos[~cunha]] = cinza[~cunha]
    cheia = cinza.copy()
    cheia[cunha] = valores[rotulos[cunha]]
    return cheia


def _tinta_falsa_da_cunha(cinza: np.ndarray, tinta: np.ndarray, cunha: np.ndarray) -> np.ndarray | None:
    """A "tinta" que so existe por causa do branco da cunha, em fundo escuro
    do scanner. Devolve a mascara dela (do tamanho de `tinta`), ou None
    quando nao ha nenhuma (quase toda pagina: beirada de papel).

    `cinza`: a imagem reduzida da busca do corte; `tinta`: a mascara do
    limiar local nela (antes do fechamento); `cunha`: _cunha_do_giro.

    E tinta falsa o ponto que (1) e tinta na imagem como veio, com a cunha
    branca; (2) NAO e tinta quando a cunha e preenchida com a vizinha de
    verdade (_preencher_a_cunha) - ou seja, quem o fez tinta foi o degrau
    branco; e (3) esta em fundo escuro do scanner (mais escuro que
    ESCURO_DO_SCANNER x o nivel do papel, o mesmo criterio de
    _parar_no_escuro). E o caso do Antiphon 88 e 260: fundo preto liso, 0% de
    tinta na pagina como veio e ~40% nas 8 linhas de fora depois do giro.

    A condicao (3) e de proposito: a tinta que o degrau cria em PAPEL
    (margem mais escura, beirada da folha vizinha) fica como esta. Tira-la
    tambem mudava o corte de 18 das 43 paginas medidas e desfazia melhoras do
    G6 (Graduale 221: o numero da folha voltava a sair cortado).

    Custo: uma segunda conta do limiar local na imagem reduzida, so quando
    ha fundo escuro a menos de uma janela da cunha (medido em 13/10/2026).

    Arriscado mudar: tirar a condicao do fundo escuro (ver acima);
    ESCURO_DO_SCANNER e o de _parar_no_escuro.
    """
    from core.filtros import janela_para_altura

    limite = ESCURO_DO_SCANNER * float(np.percentile(cinza[~cunha][::7], 90))
    # o limiar local so olha uma janela em volta do ponto: longe da cunha as
    # duas contas dao o mesmo, e sem nada escuro por perto nao ha o que achar
    # (conferido antes de preencher a cunha, que e a parte cara: a cunha
    # preenchida so e escura onde o ponto de imagem vizinho dela e escuro)
    janela = janela_para_altura(cinza.shape[0])
    perto = cv2.dilate(cunha.astype(np.uint8), np.ones((2 * janela + 1, 2 * janela + 1), np.uint8)) > 0
    if not ((cinza < limite) & perto & ~cunha).any():
        return None
    cheia = _preencher_a_cunha(cinza, cunha)
    escuro = cheia < limite
    falsa = (tinta > 0) & (_mascara_de_tinta_local(cheia) == 0) & escuro & perto
    return falsa if falsa.any() else None


# Peca de tinta colada na cunha do giro e maior que isto (fracao da largura
# ou da altura da pagina) nao e peca que o corte respeite: ver
# _sem_as_pecas_grandes_coladas_na_cunha. Medido em 13/10/2026: o numero da
# folha do Graduale 221 ("Cvij", que tem de continuar peca) mede 9% da
# largura; o contorno da folha de baixo do Antiphon 260 (que nao pode
# empurrar o corte), 34%. Arriscado mudar: descer para perto de 0,1 desfaz a
# melhora do Graduale 221 e 223; subir para perto de 0,35 devolve 13 mm de
# faixa preta ao pe do Antiphon 260.
PECA_COLADA_GRANDE = 0.2


def _sem_as_pecas_grandes_coladas_na_cunha(tinta: np.ndarray, cunha: np.ndarray) -> np.ndarray:
    """A mascara de tinta SO PARA ACHAR AS PECAS (_pecas_de_tinta) na pagina
    endireitada: sem os pedacos ligados que encostam na cunha do giro (a
    menos de 2 pontos) e sao grandes (mais que PECA_COLADA_GRANDE de um lado
    da pagina). Devolve `tinta` mesma quando nao ha nenhum.

    Por que: na pagina como veio, o que encosta na beirada da imagem nao e
    peca (borda de scanner, folha vizinha: _pecas_de_tinta) e nao empurra o
    corte. Depois do giro, a cunha branca fica entre essa coisa e a beirada,
    ela vira peca solta e empurra o corte ate 2% do lado (ESTICAR_NO_MAXIMO):
    no Antiphon 260 o contorno da folha de baixo, no canto, levava o pe 13 mm
    para dentro do fundo preto. A peca PEQUENA colada na cunha continua peca
    de proposito: e o numero da folha do Graduale 221 e 223, que encosta na
    beirada do scan e so sai inteiro no livro novo por causa disso.

    A tinta desses pedacos continua contando na massa da tinta
    (_faixa_com_a_tinta), como a do que encosta na beirada na pagina como
    veio: so deixam de ser peca.

    Arriscado mudar: tirar daqui tambem as pecas pequenas (o numero da folha
    do Graduale volta a sair cortado); apagar esses pedacos da mascara de
    verdade (a massa da tinta mudaria em toda pagina com borda)."""
    altura, largura = tinta.shape[:2]
    quantos, rotulos, caixas, _centros = cv2.connectedComponentsWithStats(
        tinta.astype(np.uint8), connectivity=8)
    if quantos <= 1:
        return tinta
    junto_da_cunha = cv2.dilate(cunha.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    tirar = np.zeros(quantos, bool)
    tirar[np.unique(rotulos[junto_da_cunha])] = True
    tirar &= ((caixas[:, cv2.CC_STAT_WIDTH] > PECA_COLADA_GRANDE * largura)
              | (caixas[:, cv2.CC_STAT_HEIGHT] > PECA_COLADA_GRANDE * altura))
    tirar[0] = False                                   # o fundo nao e pedaco
    if not tirar.any():
        return tinta
    return np.where(tirar[rotulos], 0, tinta).astype(tinta.dtype)

def _apagar_bordas_solidas_fora_da_cunha(tinta: np.ndarray, cunha: np.ndarray) -> np.ndarray:
    """O mesmo andar de _apagar_bordas_solidas (da beirada para dentro,
    enquanto a linha ou coluna for FRACAO_BORDA_SOLIDA de tinta), mas com a
    fracao contada SO nos pontos que sao imagem de verdade: a cunha do giro
    (e um ponto de vizinhanca dela, que e mistura) nao conta nem a favor nem
    contra. Devolve uma copia de `tinta` sem as linhas e colunas apagadas.

    Linha ou coluna sem nenhum ponto de imagem (so cunha) e passada adiante,
    como se fosse borda. A coluna ja apagada como borda tambem deixa de ser
    "imagem" para a conta das linhas (e vice-versa): com borda preta a
    direita E embaixo (Cursus 3), a cunha tira metade da linha de baixo da
    conta, e a faixa da direita, ja apagada, derrubava o que sobrava para
    menos de 80% - a faixa de baixo ficava (achado pelo teste de maquina
    tests/test_ordem_do_preparo.py, pagina torta com borda preta).

    Nao substitui _apagar_bordas_solidas: detectar_bordas usa as duas e fica
    com o que as duas apagam (ver o comentario "A cunha do giro", acima).

    Arriscado mudar: FRACAO_BORDA_SOLIDA e CORTE_MAXIMO sao os da conta de
    sempre; baixar a fracao aqui faz linha de texto encostada na borda virar
    borda."""
    limpa = tinta.copy()
    altura, largura = limpa.shape[:2]
    imagem = cv2.dilate(cunha.astype(np.uint8), np.ones((3, 3), np.uint8)) == 0

    def solida(faixa: np.ndarray, vale: np.ndarray) -> bool:
        quantos = int(np.count_nonzero(vale))
        if quantos == 0:
            return True
        return float(np.count_nonzero(faixa[vale])) / quantos >= FRACAO_BORDA_SOLIDA

    limite_x = int(largura * CORTE_MAXIMO)
    limite_y = int(altura * CORTE_MAXIMO)

    # esquerda e direita
    x = 0
    while x < limite_x and solida(limpa[:, x], imagem[:, x]):
        limpa[:, x] = 0
        imagem[:, x] = False
        x += 1
    x = largura - 1
    while x > largura - 1 - limite_x and solida(limpa[:, x], imagem[:, x]):
        limpa[:, x] = 0
        imagem[:, x] = False
        x -= 1

    # topo e base
    y = 0
    while y < limite_y and solida(limpa[y, :], imagem[y, :]):
        limpa[y, :] = 0
        imagem[y, :] = False
        y += 1
    y = altura - 1
    while y > altura - 1 - limite_y and solida(limpa[y, :], imagem[y, :]):
        limpa[y, :] = 0
        imagem[y, :] = False
        y -= 1

    return limpa


def detectar_bordas(img: np.ndarray, dpi: float | None = None,
                    girada: float | None = None,
                    como_veio: np.ndarray | None = None) -> Recorte:
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

    `girada` (conserto de 13/10/2026): de quantos graus `img` foi girada por
    core/endireitar.rotacionar antes de chegar aqui (o livro novo,
    "endireitar_antes": pipeline._geometria_endireitando_antes). Com ele, a
    cunha branca que o giro poe nas beiradas nao esconde mais a borda preta
    do scanner (ver "A cunha do giro", acima). None, ou menos que
    ANGULO_MINIMO (o rotacionar nao gira): a conta de sempre, identica ponto
    por ponto - e o caso do projeto antigo e da pagina como veio. Arriscado:
    passar um angulo que nao e o do giro de verdade (a cunha cairia no lugar
    errado e borda de verdade deixaria de ser reconhecida).

    `como_veio` (conserto de 20/10/2026, Pesel 21): a pagina ANTES do giro
    (a que foi girada `girada` graus para virar `img`), de preferencia em
    cinza. So e usada com `girada`, e so para a pergunta "ha o que
    recortar?" (_sem_conteudo_para_recortar), que assim da a mesma resposta
    da ordem antiga (ver o caminho 4 de "A cunha do giro"). None: a pergunta
    e feita em `img`, como antes. Arriscado: passar outra pagina que nao a
    de antes do giro.
    """
    # Capa de couro, guarda, foto da encadernacao: nao ha borda de scanner nem
    # margem de papel para tirar, e cortar so estraga. O Samuel apontou quatro
    # casos assim nas dezesseis imagens que conferiu.
    #
    # Na pagina endireitada (livro novo) a pergunta e feita na pagina como
    # veio, quando quem chama a da (`como_veio`): conserto de 20/10/2026, o
    # Pesel 21 (ver o caminho 4 de "A cunha do giro", acima). Sem `girada`,
    # `como_veio` nao e olhado: a conta de sempre, ponto por ponto.
    if girada is None or abs(girada) < ANGULO_MINIMO:
        como_veio = None
    if _sem_conteudo_para_recortar(img if como_veio is None else como_veio):
        # obra 26/10, etapa 10a (lista unica 4.10, Boecio 2: "Ficou um risco
        # preto fino em toda a beirada esquerda"): a folha sem o que recortar
        # continua inteira, menos a faixa escura colada na beirada (ver
        # beiradas_escuras). Sem faixa: a folha inteira, como sempre.
        return beiradas_escuras(img, girada) or Recorte.inteiro()

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

    # Pagina que chegou ja endireitada (livro novo): a cunha branca do giro
    # nao pode esconder a borda preta do scanner (conserto de 13/10/2026; ver
    # "A cunha do giro", acima). As duas mascaras abaixo so sao usadas para
    # TIRAR tinta, depois do apagar de sempre. Sem `girada`, nada disto roda.
    sem_borda_na_imagem = sem_tinta_falsa = cunha = None
    sem_fechar = tinta
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, nucleo)
    if girada is not None and abs(girada) >= ANGULO_MINIMO:
        cunha = _cunha_do_giro(cinza.shape, girada)
        if not cunha.any():
            cunha = None
        else:
            falsa = _tinta_falsa_da_cunha(cinza, sem_fechar, cunha)
            if falsa is not None:
                # fechada do mesmo jeito que a mascara de verdade, para o
                # fechamento nao deixar um resto da tinta falsa
                sem_tinta_falsa = cv2.morphologyEx(
                    np.where(falsa, 0, sem_fechar).astype(np.uint8), cv2.MORPH_CLOSE, nucleo)
            sem_borda_na_imagem = _apagar_bordas_solidas_fora_da_cunha(tinta, cunha)

    # A borda preta do scanner tambem e "escura", entao seria confundida com
    # conteudo e nada seria cortado. Ela e descartada antes.
    tinta = _apagar_bordas_solidas(tinta)

    # E as riscas finas do vinco e da beirada da folha de tras, que nao sao
    # escuras o bastante para a regra acima mas atravessam a pagina toda.
    tinta = _apagar_riscas_de_dobra(tinta)

    # ... e, na pagina endireitada, o que a cunha do giro escondia das duas
    # regras acima: a borda solida contada so na imagem de verdade e a tinta
    # que so existe pelo degrau branco em fundo escuro.
    if sem_borda_na_imagem is not None:
        tinta[sem_borda_na_imagem == 0] = 0
    if sem_tinta_falsa is not None:
        tinta[sem_tinta_falsa == 0] = 0

    # Obra 26/10, etapa 10a (lista unica 4.4, Horas 18: "deixou sobra branca
    # do lado direito; a pagina ficou torta no papel"): o tracejado da beirada
    # da folha nao conta na massa da tinta (ver _sem_o_tracejado_da_beirada).
    tinta = _sem_o_tracejado_da_beirada(tinta)

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
    # Na pagina endireitada, o pedaco GRANDE colado na cunha do giro nao e
    # peca (conserto de 13/10/2026): na pagina como veio ele encostava na
    # beirada da imagem. Ver _sem_as_pecas_grandes_coladas_na_cunha.
    pecas = _pecas_de_tinta(tinta if cunha is None
                            else _sem_as_pecas_grandes_coladas_na_cunha(tinta, cunha))
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

    # Obra 26/10, etapa 10a: a coluna de numeros da margem (Escola 197, Lista
    # de bugs de 13/10: "o corte come os numeros 1, 2 e 3 dos itens, na
    # margem esquerda") volta para dentro do corte. Ver _numeros_da_margem.
    x0e, x1e = _numeros_da_margem(respeitar_fracao, _de_letra(respeitar), x0e, y0e, x1e, y1e,
                                  folga_x)

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

    # Obra 26/10, etapa 10a (lista unica 4.10): o lado que foi ate a beirada
    # da imagem perde a faixa escura colada nela (beiradas_escuras), se houver.
    # Os outros lados ficam como estao.
    if x0e <= 0.0 or y0e <= 0.0 or x1e >= 1.0 or y1e >= 1.0:
        sem_faixa = beiradas_escuras(img, girada)
        if sem_faixa is not None:
            fx0, fy0, fw, fh = sem_faixa.tupla
            x0e = fx0 if x0e <= 0.0 else x0e
            y0e = fy0 if y0e <= 0.0 else y0e
            x1e = fx0 + fw if x1e >= 1.0 else x1e
            y1e = fy0 + fh if y1e >= 1.0 else y1e

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


# ---------------------------------------------------------------------------
# A coluna de numeros da margem (obra de 26/10/2026, etapa 10a; Lista de bugs
# de 13/10, verificador do corte: "Escola 197: na ordem nova o corte come os
# numeros 1, 2 e 3 dos itens, na margem esquerda. A causa e a regra que
# descarta de cada lado os primeiros 0,2% da tinta (SOBRA_DE_TINTA)"; D-104,
# "o corte automatico deixa de fora pecas pequenas e soltas").
#
# O descarte da tinta de fora (SOBRA_DE_TINTA) existe para a sujeira da margem
# nao segurar o corte, e ele nao sabe distinguir sujeira de um "1" sozinho na
# margem. O que distingue: os numeros dos itens (e as letras de chamada, os
# numeros de versiculo) ficam EM COLUNA, cada um na altura de uma linha de
# texto que esta dentro do corte, logo ao lado dela, e tem tamanho de letra.
# Sujeira nao faz isso. Regra: do lado esquerdo e do direito, as pecas do
# tamanho de letra (_de_letra) inteiras do lado de fora, a ate
# MARGEM_DOS_NUMEROS do lado, cada uma na altura (metade ou mais dela) de uma
# peca de dentro do corte que esteja a ate MARGEM_DOS_NUMEROS dela; com
# NUMEROS_EM_COLUNA ou mais assim, o lado vai ate elas, com a folga.
# Arriscado: baixar NUMEROS_EM_COLUNA para 1 (um cisco do tamanho de letra na
# altura de uma linha puxaria o corte); subir MARGEM_DOS_NUMEROS (as notas de
# margem longe do texto e a beirada da vizinha voltariam para dentro).
MARGEM_DOS_NUMEROS = 0.05
NUMEROS_EM_COLUNA = 2


def _numeros_da_margem(pecas: np.ndarray, letra: np.ndarray, x0: float, y0: float,
                       x1: float, y1: float, folga_x: float) -> tuple[float, float]:
    """(x0, x1) do corte com a coluna de numeros da margem dentro (ver o
    comentario acima). `pecas`: caixas (x0, y0, x1, y1) em fracao, as de
    _quem_empurra; `letra`: quais delas tem tamanho de letra. O resto do corte
    (y0, y1) so limita quem conta. Sem coluna, devolve x0, x1 como estao."""
    if len(pecas) == 0:
        return x0, x1
    a0, b0, a1, b1 = pecas[:, 0], pecas[:, 1], pecas[:, 2], pecas[:, 3]
    na_altura = (b0 >= y0) & (b1 <= y1)
    dentro = na_altura & (a0 >= x0) & (a1 <= x1)
    if not dentro.any():
        return x0, x1

    def ao_lado(i: int, esquerda: bool) -> bool:
        """A peca de fora `i` esta na altura de uma peca de dentro, perto dela."""
        h = b1[i] - b0[i]
        sobrepoe = np.minimum(b1, b1[i]) - np.maximum(b0, b0[i])
        perto = (a0 - a1[i]) if esquerda else (a0[i] - a1)
        # e do tamanho das letras da linha (metade da altura dela ou mais): o
        # cisco da margem do Palatino 7 tem tamanho de "letra" pequena, mas e
        # bem mais baixo que a linha ao lado
        do_tamanho = h >= 0.5 * (b1 - b0)
        ok = dentro & do_tamanho & (sobrepoe >= 0.5 * h) & (perto >= 0) & (perto <= MARGEM_DOS_NUMEROS)
        return bool(ok.any())

    fora_esq = np.flatnonzero(letra & na_altura & (a1 <= x0) & (a0 >= x0 - MARGEM_DOS_NUMEROS))
    coluna = [i for i in fora_esq if ao_lado(i, True)]
    if len(coluna) >= NUMEROS_EM_COLUNA:
        x0 = max(0.0, float(a0[coluna].min()) - folga_x)
    fora_dir = np.flatnonzero(letra & na_altura & (a0 >= x1) & (a1 <= x1 + MARGEM_DOS_NUMEROS))
    coluna = [i for i in fora_dir if ao_lado(i, False)]
    if len(coluna) >= NUMEROS_EM_COLUNA:
        x1 = min(1.0, float(a1[coluna].max()) + folga_x)
    return x0, x1


# ---------------------------------------------------------------------------
# A faixa escura colada na beirada da folha sem o que recortar (obra de
# 26/10/2026, etapa 10a; lista unica 4.10, "A sombra da lombada fica como faixa
# preta na beirada": Boecio 2, "um risco preto fino em toda a beirada
# esquerda"; Siebmacher 74, a lombada do livro do lado direito).
#
# A folha sem o que recortar (capa, guarda, pagina so com um decalque claro:
# _sem_conteudo_para_recortar) nao era cortada em nada, e a beirada do scan
# (o fio preto do Boecio 2) ou a lombada (Siebmacher 74) ficavam na pagina; no
# Preto e branco viram faixa preta. Aqui so sai a faixa da BEIRADA: de cada
# lado, anda-se para dentro enquanto a coluna (ou linha; a mediana do meio do
# lado, para letra solta nao contar) nao for papel limpo (abaixo de
# PAPEL_LIMPO do tom do papel), e a faixa so sai se (1) tiver alguma coluna
# escura de verdade (abaixo de BEIRADA_ESCURA do papel: amarelado da borda nao
# conta) e (2) terminar em papel limpo antes de BEIRADA_NO_MAXIMO do lado. Uma
# faixa escura larga (o cartao marrom do Pesel 21, que tem de sair inteiro; uma
# capa) chega ao limite sem achar papel e nao sai.
# A cunha branca do giro (livro novo) e preenchida com a vizinha antes da
# conta (_preencher_a_cunha), senao o branco dela parecia papel limpo.
# Arriscado: subir BEIRADA_NO_MAXIMO (um fio de moldura perto da beirada numa
# folha quase vazia sairia); baixar PAPEL_LIMPO (o papel amarelado da beirada
# viraria "papel" e a faixa nao seria achada).
PAPEL_LIMPO = 0.85
BEIRADA_ESCURA = 0.65
BEIRADA_NO_MAXIMO = 0.06


def beiradas_escuras(img: np.ndarray, girada: float | None = None) -> Recorte | None:
    """O corte da folha `img` sem a faixa escura colada em cada beirada (ver o
    comentario acima), em fracao; None quando nenhum lado tem faixa.
    `girada`: como em detectar_bordas (a cunha do giro nao conta).

    O corte fica logo depois da ULTIMA coluna escura de verdade da faixa (o
    papel amarelado que vem depois dela fica: e papel)."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    alt0, larg0 = cinza.shape[:2]
    if alt0 > ALTURA_ANALISE:
        escala = ALTURA_ANALISE / alt0
        cinza = cv2.resize(cinza, (max(8, int(larg0 * escala)), ALTURA_ANALISE),
                           interpolation=cv2.INTER_AREA)
    alt, larg = cinza.shape[:2]
    if alt < 16 or larg < 16:
        return None
    if girada is not None and abs(girada) >= ANGULO_MINIMO:
        cunha = _cunha_do_giro(cinza.shape, girada)
        if cunha.any() and not cunha.all():
            cinza = _preencher_a_cunha(cinza, cunha)
    papel = float(np.percentile(cinza[alt // 4: 3 * alt // 4, larg // 4: 3 * larg // 4], 60))
    if papel <= 0:
        return None
    por_coluna = np.median(cinza[alt // 4: 3 * alt // 4, :], axis=0)
    por_linha = np.median(cinza[:, larg // 4: 3 * larg // 4], axis=1)

    def anda(perfil: np.ndarray) -> int:
        limite = max(1, int(len(perfil) * BEIRADA_NO_MAXIMO))
        i = 0
        while i < limite and perfil[i] < PAPEL_LIMPO * papel:
            i += 1
        if i == 0 or i >= limite:
            return 0                       # sem faixa, ou faixa larga (cartao, capa)
        escuras = np.flatnonzero(perfil[:i] < BEIRADA_ESCURA * papel)
        return int(escuras[-1]) + 1 if escuras.size else 0

    x0 = anda(por_coluna)
    x1 = larg - anda(por_coluna[::-1])
    y0 = anda(por_linha)
    y1 = alt - anda(por_linha[::-1])
    if (x0, y0, x1, y1) == (0, 0, larg, alt):
        return None
    return Recorte(x0 / larg, y0 / alt, (x1 - x0) / larg, (y1 - y0) / alt)


# O tracejado da beirada da folha (obra de 26/10/2026, etapa 10a; lista unica
# 4.4, Horas 18). A beirada da folha (ou da vizinha) aparece na mascara como uma
# fila de tracinhos soltos, colada no lado da imagem: cada um pequeno, todos na
# mesma coluna estreita, cobrindo boa parte do lado. Juntos passam da sobra de
# tinta descartada (SOBRA_DE_TINTA) e seguravam o corte 2 a 3 cm alem da moldura
# (Horas 18: 0,23% da tinta nos 5% da direita). Saem da mascara os pedacos
# INTEIROS dentro de TRACEJADO_FAIXA do lado, cada um menor que
# TRACEJADO_PEDACO, todos dentro de uma coluna (ou linha) de TRACEJADO_LARGURA
# e cobrindo TRACEJADO_COBRE do lado, em TRACEJADO_MINIMO pedacos ou mais.
# Nota de margem nao entra: as palavras (letras juntas pelo fechamento) sao
# mais largas que a coluna. Arriscado: alargar TRACEJADO_FAIXA (coluna de
# numeros de versiculo colada na beirada sairia); baixar TRACEJADO_COBRE.
TRACEJADO_FAIXA = 0.04
TRACEJADO_PEDACO = 0.05
TRACEJADO_LARGURA = 0.02
TRACEJADO_COBRE = 0.4
TRACEJADO_MINIMO = 5


def _sem_o_tracejado_da_beirada(tinta: np.ndarray) -> np.ndarray:
    """A mascara sem o tracejado da beirada (ver o comentario acima); a mesma
    mascara quando nao ha tracejado."""
    altura, largura = tinta.shape[:2]
    n, rotulos, caixas, _ = cv2.connectedComponentsWithStats(tinta.astype(np.uint8), connectivity=8)
    if n <= 1:
        return tinta
    x, y, w, h = (caixas[1:, i] for i in range(4))
    tirar = np.zeros(n, bool)
    # os ciscos (menores que uma letra: _de_letra) na faixa da beirada tambem
    # nao contam na massa da tinta (Horas 18: riscos de 1 ponto e pontinhos a
    # 2% da beirada direita, 0,23% da tinta de uma pagina de calendario)
    cisco = ~_de_letra(np.stack([x, y, x + w, y + h], axis=1))
    fx, fy = int(largura * TRACEJADO_FAIXA), int(altura * TRACEJADO_FAIXA)
    na_faixa = (x + w <= fx) | (x >= largura - fx) | (y + h <= fy) | (y >= altura - fy)
    tirar[1:] |= cisco & na_faixa
    for eixo in ("x", "y"):
        lado, comp = (largura, altura) if eixo == "x" else (altura, largura)
        a0, a1 = (x, x + w) if eixo == "x" else (y, y + h)       # no eixo do lado
        b0, b1 = (y, y + h) if eixo == "x" else (x, x + w)       # ao longo do lado
        pequeno = ((a1 - a0) <= TRACEJADO_PEDACO * lado) & ((b1 - b0) <= TRACEJADO_PEDACO * comp)
        faixa = int(lado * TRACEJADO_FAIXA)
        for perto in (a1 <= faixa, a0 >= lado - faixa):
            sel = np.flatnonzero(pequeno & perto)
            if len(sel) < TRACEJADO_MINIMO:
                continue
            if a1[sel].max() - a0[sel].min() > TRACEJADO_LARGURA * lado:
                continue
            cobre = np.zeros(comp, bool)
            for i in sel:
                cobre[b0[i]:b1[i]] = True
            if cobre.mean() >= TRACEJADO_COBRE:
                tirar[sel + 1] = True
    tirar[0] = False
    if not tirar.any():
        return tinta
    return np.where(tirar[rotulos], 0, tinta).astype(tinta.dtype)


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
