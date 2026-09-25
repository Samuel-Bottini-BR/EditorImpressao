"""Descobrir sozinho onde estao a gravura, a letra e o papel.

Tres sinais, porque nenhum sozinho da conta deste acervo. Cada um foi medido e
cada um tem um buraco que outro tapa:

    LAYOUT   um modelo treinado para achar REGIAO de pagina: "aqui e figura,
             aqui e mancha de texto". Acerta 8 em 10 paginas. Nao enxerga
             moldura iluminada, porque foi treinado em documento moderno e nao
             tem "orla decorativa" no vocabulario.

    COR      area intensamente colorida sobre papel claro. Pega justamente a
             moldura do Livro de Horas, que e azul e ouro, e a rubricacao. Nao
             enxerga xilogravura, que e cinza.

    TINTA    onde ha traco de qualquer especie. Serve de rede de seguranca
             quando os dois de cima nao acham nada, e e o que define o "papel":
             papel e o que sobra.

Antes destes tres eu tentei separar por textura - variancia local, meio-tom por
bloco, e o detector morfologico do ScanTailor portado para Python. Os tres
falharam no acervo, e por um motivo que nao se conserta com ajuste: o vao entre
linhas de texto de um in-oitavo do seculo XVI e MENOR que o vao entre tracos
dentro de uma xilogravura de folio. Nenhum tamanho de nucleo separa os dois
quando as duas medidas se cruzam entre livros.

O modelo de layout e opcional. Sem ele o detector continua funcionando com cor
e tinta - so fica mais fraco em separar letra de gravura em pagina cinza.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from core.selecao import (
    AUTOMATICO,
    GRAVURA,
    LETRA,
    PAPEL,
    REDE,
    RETANGULO,
    Regiao,
    Selecao,
    de_mascara,
)

# --- modelo de layout -------------------------------------------------------

CAMINHO_MODELO = Path(__file__).resolve().parent.parent / "modelos" / "doclayout.onnx"

# Nomes das classes do DocLayout-YOLO, na ordem em que ele devolve.
CLASSES = {0: "title", 1: "plain text", 2: "abandon", 3: "figure",
           4: "figure_caption", 5: "table", 6: "table_caption",
           7: "table_footnote", 8: "isolate_formula", 9: "formula_caption"}

CLASSES_DE_GRAVURA = {"figure", "table", "isolate_formula"}
CLASSES_DE_LETRA = {"title", "plain text", "figure_caption", "table_caption",
                    "table_footnote", "formula_caption"}

LADO_ENTRADA = 1024
PASSO = 32

# Corte de confianca. Medido: a 0,25 uma pagina de texto da Rhetorica saia como
# "table" com 0,28 e virava gravura por engano. A 0,35 esse caso some sem levar
# junto nenhuma deteccao boa - as certas ficam entre 0,53 e 0,98.
CONFIANCA_MINIMA = 0.35

# --- cor --------------------------------------------------------------------

# Acima desta saturacao o pixel tem cor DE VERDADE - tinta pintada, e nao papel
# envelhecido. O valor saiu de medir a distribuicao no acervo, e nao de chute:
#
#   pixels acima de 130          esperado
#   Livro de Horas   20,4%       sim, e iluminura
#   Rhetorica texto   1,2%       nao, e papel manchado
#   Boecio texto      0,4%       nao
#   Marial texto      0,1%       nao
#
# Sao 17 vezes de separacao. Com o limiar em 70, que foi onde comecei, o papel
# envelhecido do Boecio dava 5,8% e o da Rhetorica 11,9%, e paginas de texto
# puro viravam gravura por engano.
SATURACAO_DE_COR = 130
AREA_MINIMA_COR = 0.004     # fracao da pagina: mancha menor que isto e respingo
FECHAMENTO_COR = 0.02       # fracao da menor dimensao: junta o que esta perto

# --- tinta ------------------------------------------------------------------

ALTURA_ANALISE = 1200

# Borda suave padrao das regioes automaticas, em fracao da menor dimensao. A
# maquina erra a borda por alguns pixels; a rampa esconde a emenda em vez de
# deixar um degrau visivel na impressao.
SUAVIDADE = 0.004

# Folga entre o conteudo e o papel, em fracao da menor dimensao. Existe para o
# branco nao encostar na borda da letra: ali mora a rampa de antisserrilhamento,
# e apaga-la e o que faz a letra virar escada.
FOLGA_DO_PAPEL = 0.004

# Largura da orla em volta do traco que nao vira papel nem letra, em fracao do
# menor lado da pagina. Da uns dois pixels a 300 DPI. Ver refinar_para_tinta.
ORLA_DO_TRACO = 1 / 250


@dataclass
class Achado:
    """Uma caixa que o modelo de layout encontrou na pagina."""

    classe: str
    confianca: float
    caixa: tuple[float, float, float, float]   # fracoes 0 a 1


class DetectorDeLayout:
    """O modelo de layout. Carrega uma vez e serve o livro inteiro."""

    def __init__(self, caminho: Path | None = None) -> None:
        self.caminho = Path(caminho or CAMINHO_MODELO)
        self._sessao = None
        self._tentou = False

    @property
    def disponivel(self) -> bool:
        """O modelo existe em disco e carregou com sucesso?"""
        return self._carregar() is not None

    def _carregar(self):
        """Carrega a sessao ONNX uma unica vez (guarda em self._tentou).

        Se faltar o arquivo ou o onnxruntime nao estiver instalado, devolve
        None em vez de propagar erro - o resto do detector sabe lidar com
        "sem modelo" caindo nos sinais que nao dependem dele.
        """
        if self._tentou:
            return self._sessao
        self._tentou = True
        if not self.caminho.exists():
            return None
        try:
            import onnxruntime as ort

            opcoes = ort.SessionOptions()
            opcoes.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self._sessao = ort.InferenceSession(
                str(self.caminho), opcoes, providers=["CPUExecutionProvider"])
        except Exception:  # noqa: BLE001 - sem o modelo o resto continua
            self._sessao = None
        return self._sessao

    def achar(self, img: np.ndarray) -> list[Achado]:
        """Roda o modelo na pagina e devolve as caixas encontradas.

        Redimensiona para o lado de entrada do modelo (com padding cinza para
        manter a proporcao) e depois converte as coordenadas de volta para
        fracao da pagina original. Lista vazia se o modelo nao estiver
        disponivel ou a inferencia falhar - nunca levanta excecao.
        """
        sessao = self._carregar()
        if sessao is None:
            return []

        altura, largura = img.shape[:2]
        escala = min(LADO_ENTRADA / altura, LADO_ENTRADA / largura)
        nh, nw = int(round(altura * escala)), int(round(largura * escala))
        pequena = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)

        folga_x, folga_y = (-nw) % PASSO, (-nh) % PASSO
        cima, esquerda = folga_y // 2, folga_x // 2
        tela = cv2.copyMakeBorder(
            pequena, cima, folga_y - cima, esquerda, folga_x - esquerda,
            cv2.BORDER_CONSTANT, value=(114, 114, 114))

        rgb = cv2.cvtColor(tela, cv2.COLOR_BGR2RGB)
        entrada = np.transpose(rgb, (2, 0, 1))[None].astype(np.float32) / 255.0

        try:
            saida = sessao.run(None, {"images": entrada})[0]
        except Exception:  # noqa: BLE001
            return []

        preds = saida[0]
        if preds.shape[0] < preds.shape[1]:
            preds = preds.T
        preds = preds[preds[:, 4] >= CONFIANCA_MINIMA]

        achados: list[Achado] = []
        for p in preds:
            x0 = (float(p[0]) - esquerda) / escala / largura
            y0 = (float(p[1]) - cima) / escala / altura
            x1 = (float(p[2]) - esquerda) / escala / largura
            y1 = (float(p[3]) - cima) / escala / altura
            achados.append(Achado(
                classe=CLASSES.get(int(p[5]), str(int(p[5]))),
                confianca=float(p[4]),
                caixa=(max(0.0, min(1.0, x0)), max(0.0, min(1.0, y0)),
                       max(0.0, min(1.0, x1)), max(0.0, min(1.0, y1))),
            ))
        return achados


_detector = DetectorDeLayout()


# --- os sinais que nao dependem de modelo -----------------------------------

def mascara_de_cor(img: np.ndarray) -> np.ndarray:
    """Areas intensamente coloridas: iluminura, rubricacao, capa pintada.

    E o sinal que tapa o buraco do modelo de layout, que nao reconhece moldura
    decorativa. A moldura do Livro de Horas e azul e ouro saturados e cai aqui
    inteira.
    """
    if img.ndim == 2:
        return np.zeros(img.shape[:2], bool)

    altura, largura = img.shape[:2]
    escala = min(1.0, ALTURA_ANALISE / altura)
    pequena = cv2.resize(img, (max(8, int(largura * escala)),
                               max(8, int(altura * escala))),
                         interpolation=cv2.INTER_AREA) if escala < 1 else img

    saturacao = cv2.cvtColor(pequena, cv2.COLOR_BGR2HSV)[:, :, 1]
    colorida = (saturacao > SATURACAO_DE_COR).astype(np.uint8)

    lado = max(3, int(FECHAMENTO_COR * min(pequena.shape[:2])) | 1)
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))
    colorida = cv2.morphologyEx(colorida, cv2.MORPH_CLOSE, nucleo)

    num, rot, stats, _ = cv2.connectedComponentsWithStats(colorida, connectivity=8)
    minimo = AREA_MINIMA_COR * colorida.size
    limpa = np.zeros_like(colorida, bool)
    for i in range(1, num):
        if stats[i, cv2.CC_STAT_AREA] >= minimo:
            limpa |= rot == i

    return cv2.resize(limpa.astype(np.uint8), (largura, altura),
                      interpolation=cv2.INTER_NEAREST) > 0


def _caixas_para_mascara(achados, classes, altura, largura) -> np.ndarray:
    """Preenche de True os retangulos dos achados cuja classe esta em `classes`."""
    m = np.zeros((altura, largura), bool)
    for a in achados:
        if a.classe not in classes:
            continue
        x0, y0, x1, y1 = a.caixa
        m[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)] = True
    return m


# Quanto engordar o traco ao descer ao nivel da tinta, em fracao da menor
# dimensao. Precisa cobrir a rampa de antisserrilhamento em volta da letra,
# senao a borda dela fica de fora e recebe tratamento de papel.
FOLGA_DA_TINTA = 0.0015

# Quanto mais escuro que a mediana da pagina um pixel precisa ser para contar
# como conteudo, e que fracao deles precisa existir.
#
# Uma capa de couro lisa TEM meio-tom - ela e toda tom continuo - e por isso o
# teste de meio-tom a aprovava como gravura de pagina inteira. O que ela nao
# tem e CONTEUDO: nada nela e significativamente mais escuro que ela mesma.
# Medido no acervo:
#
#     capa de couro      0,44%      Boecio, pagina de poema    12,70%
#     folha em branco    0,17%      Graduale, partitura        14,62%
#                                   catecismo, texto e gravura 32,61%
#
# Sao trinta vezes de separacao. O corte em 3% fica no meio do vazio.
ESCURO_QUE_CONTA = 45
FRACAO_ESCURA_DE_PAGINA_VAZIA = 0.03

# Ate este espalhamento de tons no miolo, a folha e limpa mesmo e o veredito de
# pagina vazia fica de pe sem consultar o modelo. Ver _espalhamento_do_miolo.
ESPALHAMENTO_DE_FOLHA_LIMPA = 110

# E, na duvida, so uma caixa grande do modelo desmente a pagina vazia. Caixa
# pequena em folha clara costuma ser sujeira ou numero de pagina.
AREA_QUE_DESMENTE_PAGINA_VAZIA = 0.15

# Quanto da tinta da pagina os blocos do modelo precisam cobrir para eu confiar
# na proposta dele. Abaixo disto ele viu so um pedaco, e o resto da tinta vira
# letra por conta propria. Ver o comentario em detectar.
COBERTURA_MINIMA_DO_LAYOUT = 0.55

# Duas medidas para a mesma pergunta: esta area e ESCRITA ou e PINTURA?
#
# A pergunta decide se o buraco no meio de uma moldura iluminada e o bloco de
# texto que ela cerca (nao tapar, senao a pagina escrita inteira vira gravura) ou
# uma cena pintada que ficou de fora da mascara de cor (tapar).
#
# A primeira medida e o vao entre linhas. Escrita deixa faixas quase sem tinta
# entre uma linha e outra; pintura cobre de cima a baixo. So que ela se perde em
# PAPEL PAUTADO: na pagina 142 do Livro de Horas a pauta atravessa o painel de
# ponta a ponta, nao sobra faixa vazia nenhuma, e o texto era tapado como se
# fosse pintura.
#
# A segunda medida nao se engana com pauta: de que TAMANHO sao os pedacos de
# tinta. Escrita e feita de centenas de pedacinhos da altura de um glifo;
# pintura e feita de poucas manchas grandes. Medido nos tres casos de texto e
# nos sete de pintura das paginas 48, 95 e 142:
#
#     bloco de texto, p48     85%      paisagens da p48         6% a  9%
#     bloco de texto, p95     79%      vinheta da p95          37%
#     bloco de texto, p142    50%      vinhetas da p142        15%
#
# Basta uma das duas dizer "escrita" para o buraco ser preservado: errar para o
# lado de nao tapar so mantem o comportamento antigo, e errar para o outro lado
# transforma uma pagina de texto em gravura.
VAZIAS_DE_TEXTO = 0.30
TINTA_EM_PEDACOS_DE_GLIFO = 0.45

# Um pedaco de tinta e "do tamanho de um glifo" se for mais baixo que esta
# fracao do lado da area examinada.
ALTURA_DE_GLIFO = 1 / 12

# A mesma medida responde a outra pergunta: o modelo achou "figure" - isso e uma
# GRAVURA DE TRACO ou e uma pagina escrita? O modelo chama de figure tanto a
# xilogravura do Valades quanto a caligrafia do Palatino e a partitura do
# Graduale, e o tratamento que cada uma pede e oposto.
#
# O teste de meio-tom nao resolve: xilogravura e traco puro, e reprovava. O vao
# entre linhas tambem nao: o ornamento do Siebmacher da 23,7% e a partitura do
# Graduale 22,6%. O tamanho do pedaco separa:
#
#     xilogravura do Valades    8,7%      caligrafia do Palatino    50,1%
#     ornamento Siebmacher      4,3%      partitura do Graduale     49,1%
#     ornamento Siebmacher      7,7%      partitura do Graduale     90,2%
#     gravura do catecismo     13,6%      tabela da Rhetorica       93,0%
#
# O corte em 30% fica no vao entre 14% e 49%.
PEDACOS_DE_GLIFO_DE_ESCRITA = 0.30

# Abaixo deste tanto de papel nu a caixa nao e pagina escrita, e sim foto de um
# objeto que cobre a area. Ver _papel_a_vista, onde estao as medidas: foto de
# bordado 30% a 48%, escrita 57% a 76%. O corte fica no vao.
PAPEL_A_VISTA_DE_ESCRITA = 0.52

# O que conta como papel nu, para essa conta: claro perto do mais claro da
# caixa, e sem cor.
CLARO_DE_PAPEL = 0.80
SATURACAO_DE_PAPEL = 60

# Abaixo desta tinta o buraco e papel limpo, e papel nao vira gravura.
TINTA_MINIMA_DO_BURACO = 0.05

# Quando a pagina inteira e UMA FOTO so - capa de madeira, foto da encadernacao,
# frontispicio gravado - o modelo desenha a caixa em quase toda ela e sobra uma
# faixa fina de fora, cortada pelo retangulo. Essa faixa e o mesmo objeto, e nao
# texto: sem esta regra ela virava letra por eliminacao e o veio da madeira seria
# binarizado numa tarja no alto da capa.
#
# Nao da para decidir isso pelo tamanho do pedaco de tinta, que e a regua usada
# no resto do arquivo: o veio da madeira do Palatino da 73,6% de pedacos do
# tamanho de glifo, tao "escrito" quanto uma pagina de texto. O que decide e a
# pagina nao ter bloco de texto nenhum e a sobra ser fina.
FOTO_DE_PAGINA_INTEIRA = 0.60
SOBRA_FORA_DA_FOTO = 0.08

# Ate este tamanho, uma mancha colorida dentro de uma caixa de texto e uma
# inicial rubricada, e vale como letra. Acima disso e area pintada, e a caixa do
# modelo e que esta errada. Na pagina 48 do Livro de Horas o modelo desenhou uma
# caixa de "plain text" cobrindo a paisagem do alto junto com o texto: a moldura
# perdia o topo, deixava de ser um anel fechado, e a pintura de dentro nao tinha
# mais como ser reconhecida como buraco.
AREA_DE_INICIAL_RUBRICADA = 0.02

# So vale avisar 'desenho ou escrita?' quando a duvida cobre um pedaco
# grande da folha. Uma vinheta de 3% marcada errado nao muda a pagina.
AREA_DE_DUVIDA_QUE_IMPORTA = 0.25


def mascara_de_tinta(img: np.ndarray) -> np.ndarray:
    """Onde ha traco de qualquer especie: letra, neuma, linha de gravura.

    Sauvola local, e nao limiar global: papel envelhecido tem manchas que um
    limiar unico transforma em tinta.

    A conta e feita no TAMANHO DE VERDADE da pagina. Antes ela era feita num
    reduzido de 1200 px de altura e a resposta voltava ampliada com vizinho mais
    proximo: numa pagina de 300 DPI isso e um terco da resolucao, e a marcacao
    saia com degraus de tres pixels em volta de cada letra. Era a queixa do
    Samuel de que "as ferramentas de selecao precisam ser mais precisas". Uma
    pagina de cada vez na memoria continua valendo - o que sai daqui e uma
    mascara de um byte por pixel, e ela morre com a pagina.

    O k tambem passou a ser o mesmo que o filtro usa, medido pela espessura do
    traco da propria pagina. Com dois k diferentes, o detector e o filtro
    discordavam sobre o que era tinta na MESMA pagina.
    """
    from core.filtros import binarizar, janela_para_altura, k_para_a_letra

    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    altura, largura = cinza.shape[:2]

    binaria = binarizar(cinza, janela=janela_para_altura(altura),
                        k=k_para_a_letra(cinza))
    tinta = (binaria == 0).astype(np.uint8)

    folga = max(1, int(FOLGA_DA_TINTA * min(altura, largura)) | 1)
    return cv2.dilate(tinta, cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (folga, folga))) > 0


def blocos_de_tinta(tinta: np.ndarray) -> np.ndarray:
    """Junta o traco em BLOCOS de texto, como o modelo de layout devolveria.

    Necessario porque a selecao guarda bloco, e nao letra a letra: um poligono
    por glifo daria milhares de formas por pagina, inviaveis de editar e de
    guardar. Quem desce ao nivel do traco e refinar_para_tinta, na hora de
    aplicar.

    O fechamento e mais largo na horizontal que na vertical, porque texto se
    liga ao longo da linha e nao entre linhas - e o mesmo principio do
    algoritmo de suavizacao por corridas usado em analise de layout.
    """
    if not tinta.any():
        return tinta

    altura, largura = tinta.shape[:2]
    largo = max(3, int(0.030 * largura) | 1)
    alto = max(3, int(0.012 * altura) | 1)

    juntos = cv2.morphologyEx(
        tinta.astype(np.uint8), cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (largo, alto)))

    from scipy.ndimage import binary_fill_holes

    return binary_fill_holes(juntos > 0)


def _cor_que_a_caixa_de_texto_pode_engolir(
    gravura_cor: np.ndarray, letra_layout: np.ndarray
) -> np.ndarray:
    """Quais manchas coloridas cedem para uma caixa de texto do modelo.

    Uma inicial rubricada no meio de um paragrafo e letra: transforma-la em
    gravura arrancaria o paragrafo do preto e branco. Mas so quem e do tamanho
    de uma inicial cede. Quando a mancha e uma moldura inteira, quem esta errado
    e o modelo - ver AREA_DE_INICIAL_RUBRICADA.
    """
    from scipy.ndimage import label

    componentes, quantos = label(gravura_cor)
    cede = np.zeros_like(gravura_cor)
    for k in range(1, quantos + 1):
        mancha = componentes == k
        if float(mancha.mean()) > AREA_DE_INICIAL_RUBRICADA:
            continue
        if float(letra_layout[mancha].mean()) > 0.5:
            cede |= mancha
    return cede


def _e_uma_foto_de_pagina_inteira(
    gravura: np.ndarray, letra_layout: np.ndarray, tinta: np.ndarray
) -> bool:
    """A pagina inteira e uma foto so - capa, encadernacao, frontispicio?

    Nessas paginas o modelo desenha a caixa em quase toda a folha e sobra uma
    faixa fina de fora, cortada pelo retangulo. A faixa e o mesmo objeto, e por
    eliminacao virava LETRA: no verso da capa do Palatino, o veio da madeira do
    alto seria binarizado numa tarja preta e branca.

    Ver FOTO_DE_PAGINA_INTEIRA para por que a regua do tamanho do pedaco de
    tinta, usada no resto do arquivo, nao serve aqui.
    """
    if letra_layout.any():
        return False
    if float(gravura.mean()) < FOTO_DE_PAGINA_INTEIRA:
        return False
    return float((tinta & ~gravura).mean()) <= SOBRA_FORA_DA_FOTO


def _sem_as_manchas_por_cima_da_escrita(
    gravura_cor: np.ndarray, tinta: np.ndarray
) -> np.ndarray:
    """Tira da mascara de cor as manchas que cobrem texto.

    Papel envelhecido tem manchas que passam no corte de saturacao: na pagina
    223 da Rhetorica, que e so texto, elas cobriam 19,6% da folha e a pagina
    saia com um borrao de "gravura" por cima dos paragrafos. Antes isso passava
    despercebido porque qualquer cor sob uma caixa de texto do modelo era
    descartada; desde que a moldura inteira deixou de ceder para o modelo, a
    mancha grande tambem parou de ceder.

    O teste certo nao e o tamanho e sim o que ha DENTRO: se a tinta ali e feita
    de pedacinhos do tamanho de glifos, e escrita, e escrita nao e iluminura. A
    conta olha so os pixels da mancha, e nao o retangulo em volta dela - a
    moldura do Livro de Horas e um anel cujo retangulo contem a pagina escrita
    inteira.
    """
    if not gravura_cor.any():
        return gravura_cor

    from scipy.ndimage import label

    componentes, quantos = label(gravura_cor)
    limpa = gravura_cor.copy()
    for k in range(1, quantos + 1):
        mancha = componentes == k
        ys, xs = np.nonzero(mancha)
        janela = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        dentro = tinta[janela] & mancha[janela]
        if _tinta_em_pedacos_de_glifo(dentro) >= PEDACOS_DE_GLIFO_DE_ESCRITA:
            limpa &= ~mancha
    return limpa


def _fracao_de_linhas_vazias(tinta: np.ndarray) -> float:
    """Quanto desta area e vao entre linhas."""
    if tinta.size < 100:
        return 0.0
    perfil = tinta.sum(axis=1).astype(np.float64)
    if perfil.max() <= 0:
        return 0.0
    return float((perfil / perfil.max() < 0.10).mean())


def _tinta_em_pedacos_de_glifo(tinta: np.ndarray) -> float:
    """Que fracao da tinta vive em pedacos do tamanho de uma letra."""
    if tinta.size < 100 or not tinta.any():
        return 0.0
    num, _, stats, _ = cv2.connectedComponentsWithStats(
        tinta.astype(np.uint8), connectivity=8)
    if num <= 1:
        return 0.0
    areas = stats[1:, cv2.CC_STAT_AREA].astype(np.float64)
    alturas = stats[1:, cv2.CC_STAT_HEIGHT].astype(np.float64)
    total = float(areas.sum())
    if total <= 0:
        return 0.0
    lado = float(np.sqrt(tinta.size))
    return float(areas[alturas < lado * ALTURA_DE_GLIFO].sum() / total)


def _parece_escrita(tinta: np.ndarray) -> bool:
    """Isto e um bloco escrito, ou e area pintada? Ver TINTA_EM_PEDACOS_DE_GLIFO."""
    if _fracao_de_linhas_vazias(tinta) >= VAZIAS_DE_TEXTO:
        return True
    return _tinta_em_pedacos_de_glifo(tinta) >= TINTA_EM_PEDACOS_DE_GLIFO


def _tapar_buracos_da_iluminura(gravura: np.ndarray, tinta: np.ndarray) -> np.ndarray:
    """Fecha os vazios que a mascara de cor deixa dentro de uma iluminura.

    A moldura do Livro de Horas e ouro e azul saturados e cai inteira na mascara
    de cor, mas as CENAS PINTADAS dentro dela - a paisagem, a ponte, o laguinho -
    sao claras e pálidas, nao passam no corte de saturacao e ficam de fora. O
    buraco entao era preenchido pelo detector de tinta e a pintura saia marcada
    como LETRA: foi o manto azul virando letra que o Samuel viu.

    Tapar tudo nao serve: a moldura cerca o bloco de texto, e tapar aquele
    buraco engoliria a pagina escrita inteira. O que separa os dois esta em
    _parece_escrita.
    """
    if not gravura.any():
        return gravura

    from scipy.ndimage import binary_fill_holes, label

    cheia = binary_fill_holes(gravura)
    buracos, quantos = label(cheia & ~gravura)
    if not quantos:
        return gravura

    tapada = gravura.copy()
    for k in range(1, quantos + 1):
        buraco = buracos == k
        if float(tinta[buraco].mean()) < TINTA_MINIMA_DO_BURACO:
            continue  # papel limpo cercado pela moldura continua sendo papel
        ys, xs = np.nonzero(buraco)
        recorte = tinta[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if _parece_escrita(recorte):
            continue  # e o bloco de texto que a moldura cerca
        tapada |= buraco
    return tapada


def _area_da_caixa(achado: "Achado") -> float:
    """Area da caixa do achado, em fracao da pagina (0 a 1)."""
    x0, y0, x1, y1 = achado.caixa
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def _espalhamento_do_miolo(img: np.ndarray) -> float:
    """Quantos tons ha no meio da pagina, longe da borda do escaneamento.

    Serve para desconfiar do veredito de pagina vazia. A borda fica de fora
    porque e la que moram a sombra do vinco e a moldura preta do scanner, que
    espalham o tom de qualquer folha: medido, uma folha limpa do Livro de Horas
    da 194 de espalhamento na pagina toda e 94 so no miolo.

        folha limpa, no miolo        0 a 95
        foto sobre cartao, Pesel   132 a 148
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    altura, largura = cinza.shape[:2]
    miolo = cinza[int(altura * 0.12):int(altura * 0.88),
                  int(largura * 0.12):int(largura * 0.88)]
    if miolo.size < 100:
        return 0.0
    return float(np.percentile(miolo, 97) - np.percentile(miolo, 3))


# Uma folha de papel nua nao tem textura nem fundo escuro em volta; um objeto
# fotografado - couro, madeira, tecido, o corte do livro - tem uma coisa ou a
# outra.
#
# Contada a textura em todas as paginas sem conteudo do acervo, os dois grupos
# nao se encostam:
#
#   folha nua   0,00  1,31  1,36  1,40  1,49  1,51  1,55  1,91
#   capa                                            5,05  6,19  6,25  7,10  12,48
#
# O valor antigo era 5,5, e caia DENTRO do grupo das capas: a capa de
# pergaminho do Boecio, que marca 5,05, ficava de fora e o Preto e branco a
# apagava inteira - era o bug da capa apagada, que voltava por este caminho.
# O corte novo fica no meio do vao, com folga de mais de duas vezes para cada
# lado.
#
# A orla entra na conta a parte porque o corte do livro nao tem textura: ele e
# um bloco claro sobre fundo preto.
#
#   orla      folha nua 0,96 a 1,22 |  capa 0,48 a 0,97 (o corte do livro, 0,81)
TEXTURA_DE_OBJETO = 3.0
ORLA_ESCURA_DE_OBJETO = 0.85


def _e_objeto_e_nao_folha(img: np.ndarray) -> bool:
    """Isto e um objeto fotografado, ou uma folha de papel nua?

    A resposta muda o destino da pagina no Preto e branco, e a diferenca e
    grande. Sem marcacao nenhuma a folha inteira e binarizada: medido e
    fotografado, a capa de pergaminho do Boecio sai uma folha BRANCA, com so a
    etiqueta da biblioteca sobrando. Marcada como gravura, ela sai inteira.

    Mas o contrario tambem custa: uma folha de guarda em branco marcada como
    gravura para de ir a branco - fica no creme de 210 em vez dos 255 que o
    Kaique pediu. Entao nao da para marcar as duas iguais.
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    largura = 400
    altura = max(8, int(largura * cinza.shape[0] / max(1, cinza.shape[1])))
    pequena = cv2.resize(cinza, (largura, altura),
                         interpolation=cv2.INTER_AREA).astype(np.float32)

    media = cv2.boxFilter(pequena, -1, (9, 9))
    media_dos_quadrados = cv2.boxFilter(pequena * pequena, -1, (9, 9))
    textura = float(np.median(
        np.sqrt(np.clip(media_dos_quadrados - media * media, 0, None))))
    if textura > TEXTURA_DE_OBJETO:
        return True

    faixa = 6
    orla = np.concatenate([
        pequena[:faixa].ravel(), pequena[-faixa:].ravel(),
        pequena[:, :faixa].ravel(), pequena[:, -faixa:].ravel()])
    miolo = float(np.median(pequena))
    return miolo >= 1 and float(orla.mean()) / miolo < ORLA_ESCURA_DE_OBJETO


def _folha_nua_ou_objeto(selecao: Selecao, img: np.ndarray) -> Selecao:
    """Folha nua sai sem marcacao; objeto sai marcado como gravura inteira."""
    if _e_objeto_e_nao_folha(img):
        selecao.acrescentar(Regiao(
            tipo=GRAVURA, forma=RETANGULO, pontos=[(0.0, 0.0), (1.0, 1.0)],
            origem=AUTOMATICO, rotulo="capa"))
    return selecao


def _pagina_sem_conteudo(img: np.ndarray) -> bool:
    """Capa, folha de guarda, verso em branco: nao ha o que marcar.

    A pergunta nao e "tem meio-tom" - couro tem - e sim "tem alguma coisa
    escura de verdade". Ver ESCURO_QUE_CONTA.
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    mediana = float(np.median(cinza))
    escuros = float((cinza < mediana - ESCURO_QUE_CONTA).mean())
    return escuros < FRACAO_ESCURA_DE_PAGINA_VAZIA


# --- o detector -------------------------------------------------------------

def _papel_a_vista(img: np.ndarray, caixa) -> float:
    """Que fracao desta caixa e papel nu: claro e sem cor.

    Escrita e tinta SOBRE papel, entao a maior parte da caixa continua sendo
    papel - o vao entre as linhas, a margem dentro do bloco. A foto de um objeto
    cobre a area: no livro de bordados da Pesel, o cartao de fundo e a trama do
    tecido tomam a caixa inteira.

    E a medida que faltava para o Pesel. Nem o tamanho do pedaco de tinta nem o
    meio-tom separavam aquelas paginas de uma pagina escrita - a trama do tecido
    imita glifo, e a foto e contrastada - mas o papel a vista separa:

        foto de bordado, Pesel     30% a 48%
        caligrafia do Palatino     62% a 66%
        partitura do Graduale      57% a 76%
        texto da Rhetorica         65%
        texto do Boecio            68%
    """
    altura, largura = img.shape[:2]
    x0, y0, x1, y1 = caixa
    pedaco = img[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)]
    if pedaco.size < 100:
        return 1.0

    cinza = cv2.cvtColor(pedaco, cv2.COLOR_BGR2GRAY) if pedaco.ndim == 3 else pedaco
    saturacao = (cv2.cvtColor(pedaco, cv2.COLOR_BGR2HSV)[:, :, 1] if pedaco.ndim == 3
                 else np.zeros_like(cinza))
    claro = float(np.percentile(cinza, 95))
    return float(((cinza > claro * CLARO_DE_PAPEL) & (saturacao < SATURACAO_DE_PAPEL)).mean())


def _e_meio_tom(img: np.ndarray, caixa) -> bool:
    """Dentro desta caixa ha TOM CONTINUO, ou e traco sobre papel?

    O modelo de layout chama de "figure" tanto uma litografia colorida quanto
    uma pagina de partitura ou uma folha de caligrafia - para ele, tudo que nao
    e paragrafo de texto moderno e figura. Mas o tratamento que cada uma pede e
    oposto: meio-tom nao pode ser binarizado, traco sobre papel pode e deve.

    Meio-tom tem valores espalhados por toda a escala de cinza. Traco sobre
    papel e quase bilevel: e tinta ou e papel, quase nada no meio.
    """
    altura, largura = img.shape[:2]
    x0, y0, x1, y1 = caixa
    pedaco = img[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)]
    if pedaco.size < 100:
        return False

    cinza = cv2.cvtColor(pedaco, cv2.COLOR_BGR2GRAY) if pedaco.ndim == 3 else pedaco
    escuro = float(np.percentile(cinza, 5))
    claro = float(np.percentile(cinza, 95))
    faixa = claro - escuro
    if faixa < 25:
        return False

    meio = ((cinza > escuro + 0.3 * faixa) & (cinza < claro - 0.3 * faixa)).mean()
    return bool(meio > 0.28)


def detectar(
    img: np.ndarray,
    usar_layout: bool = True,
    usar_cor: bool = True,
) -> Selecao:
    """Devolve a selecao proposta para esta pagina.

    A marcacao desce ao NIVEL DA TINTA. O modelo de layout devolve caixas -
    "aqui tem texto" - e pintar a caixa inteira de letra estava errado: o papel
    entre as linhas nao e letra, e receber tratamento de letra o impede de ir a
    branco. Dentro de cada bloco de texto, so o traco e marcado como letra; o
    resto sobra para papel.

    Na gravura e o contrario: uma litografia e uma area continua, e a caixa
    inteira vale. Mas so quando ela e MESMO meio-tom - o modelo chama de
    "figure" tambem partitura e folha de caligrafia, que sao traco sobre papel
    e devem ser tratadas como letra.

    Tudo que sai daqui leva a origem marcada, e por isso pode ser apagado
    sozinho: limpar_origem tira a proposta da maquina e mantem o que a pessoa
    desenhou a mao.
    """
    altura, largura = img.shape[:2]
    selecao = Selecao()

    colorida = _tres_canais_ou_cinza(img)

    # Capa, folha de guarda, verso em branco: nao ha o que marcar. Sem esta
    # guarda uma capa de couro lisa virava "gravura" de pagina inteira - o
    # modelo de layout chamava de figure(0.66) e o teste de meio-tom concordava,
    # porque couro E tom continuo.
    achados: list[Achado] = []
    if _pagina_sem_conteudo(colorida):
        # A pergunta "ha algo mais escuro que a propria pagina?" nao serve numa
        # pagina de fundo escuro: no livro de bordados da Pesel, as fotos ficam
        # sobre um cartao pardo e a pagina inteira era dada como vazia. Quando o
        # miolo tem tons demais para uma folha limpa, vale acordar o modelo antes
        # de desistir - so nesse caso, para nao pagar o modelo em toda folha em
        # branco de um livro de novecentas paginas.
        if _espalhamento_do_miolo(colorida) < ESPALHAMENTO_DE_FOLHA_LIMPA:
            return _folha_nua_ou_objeto(selecao, colorida)
        achados = _detector.achar(colorida) if usar_layout else []
        if not any(_area_da_caixa(a) >= AREA_QUE_DESMENTE_PAGINA_VAZIA for a in achados):
            return _folha_nua_ou_objeto(selecao, colorida)

    em_duvida = False
    tinta = mascara_de_tinta(colorida)
    if not achados:
        achados = _detector.achar(colorida) if usar_layout else []

    gravura_layout = np.zeros((altura, largura), bool)
    letra_layout = np.zeros((altura, largura), bool)
    # Onde o modelo viu texto E ha mesmo letra miuda embaixo. E o unico sinal
    # forte o bastante para tirar area da gravura, mais adiante.
    escrita_certa = np.zeros((altura, largura), bool)
    for a in achados:
        x0, y0, x1, y1 = a.caixa
        fatia = (slice(int(y0 * altura), int(y1 * altura)),
                 slice(int(x0 * largura), int(x1 * largura)))
        if a.classe in CLASSES_DE_GRAVURA:
            # Gravura de verdade se tiver meio-tom OU se for desenho de traco.
            # O modelo chama de "figure" tambem caligrafia e partitura, que sao
            # escrita e devem ser tratadas como tal - ver
            # PEDACOS_DE_GLIFO_DE_ESCRITA.
            desenho = _tinta_em_pedacos_de_glifo(tinta[fatia]) < PEDACOS_DE_GLIFO_DE_ESCRITA
            foto = _papel_a_vista(colorida, a.caixa) < PAPEL_A_VISTA_DE_ESCRITA
            meio_tom = _e_meio_tom(colorida, a.caixa)
            if desenho or foto or meio_tom:
                gravura_layout[fatia] = True
                # Quando a folha VAI para gravura so porque sobrou pouco papel a
                # vista, e ao mesmo tempo tem cara de escrita, nao ha como saber
                # pela imagem: medidos cinco sinais diferentes, os numeros de
                # escrita e de foto se cruzam em todos - esta contado em
                # relatorios/melhorias.md. Foi assim que a partitura da pagina
                # 126 do Graduale ficou dois dias marcada como desenho.
                #
                # Entao o programa para de fingir certeza e avisa. Laranja aqui
                # quer dizer o que sempre quis: confira esta.
                if (foto and not desenho and not meio_tom
                        and _parece_escrita(tinta[fatia])
                        and _area_da_caixa(a) >= AREA_DE_DUVIDA_QUE_IMPORTA):
                    em_duvida = True
            else:
                letra_layout[fatia] = True
        elif a.classe in CLASSES_DE_LETRA:
            letra_layout[fatia] = True
            if _tinta_em_pedacos_de_glifo(tinta[fatia]) >= PEDACOS_DE_GLIFO_DE_ESCRITA:
                escrita_certa[fatia] = True

    gravura_cor = mascara_de_cor(colorida) if usar_cor else np.zeros((altura, largura), bool)

    # Mancha de papel envelhecido passa no corte de saturacao. Se ha escrita
    # embaixo dela, nao e iluminura nenhuma.
    gravura_cor = _sem_as_manchas_por_cima_da_escrita(gravura_cor, tinta)

    # A cor cede para o layout onde a mancha e do tamanho de uma inicial
    # rubricada - essa e letra, e transforma-la em gravura arrancaria o
    # paragrafo do preto e branco. Uma moldura inteira nao cede.
    gravura = gravura_layout | (gravura_cor & ~_cor_que_a_caixa_de_texto_pode_engolir(
        gravura_cor, letra_layout))

    # A pintura clara dentro da moldura nao passa no corte de saturacao e abre
    # buraco. Sem tapar, o buraco vira letra e o manto azul da figura recebe
    # tratamento de texto.
    gravura = _tapar_buracos_da_iluminura(gravura, tinta)

    # Pagina que e uma foto so: a faixa que sobrou fora da caixa e a mesma foto,
    # cortada pelo retangulo, e nao um bloco de texto.
    if _e_uma_foto_de_pagina_inteira(gravura, letra_layout, tinta):
        gravura = np.ones((altura, largura), bool)

    # Legenda impressa sobre a foto continua sendo legenda. No livro de bordados
    # da Pesel as legendas ficam em cima do cartao de fundo, que e colorido: a
    # mascara de cor as engolia junto com a foto e a pagina saia sem uma linha de
    # texto. Onde o modelo viu texto E ha letra miuda embaixo, o texto ganha.
    gravura &= ~escrita_certa

    # O que o modelo achou SOMA com o que sobrou de tinta - nao substitui.
    #
    # Escolher entre um e outro deixava furos: no catecismo o modelo achou a
    # maioria dos paragrafos e dois ficavam de fora, e como a cobertura passava
    # do limiar eu confiava nele e os dois sumiam. No Boecio era o contrario:
    # ele achou so o titulo numa pagina inteira de poema.
    #
    # Somando, o modelo contribui com o que sabe fazer - reconhecer bloco mesmo
    # onde a tinta e rala - e a tinta solta cobre o que ele deixou passar.
    tinta_fora_da_gravura = tinta & ~gravura
    sobrou = tinta_fora_da_gravura & ~letra_layout
    letra = (letra_layout | blocos_de_tinta(sobrou)) & ~gravura

    # ATENCAO: aqui a letra e guardada como BLOCO, e nao letra a letra.
    # Guardar cada glifo como poligono daria milhares de formas por pagina e
    # inviabilizaria o arquivo e a edicao a mao. O bloco e o que a pessoa
    # arrasta e corrige; a descida ao nivel do traco acontece na hora de
    # aplicar, em refinar_para_tinta. O efeito cai em cima de cada letra, o
    # papel entre as linhas continua sendo papel, e o que se edita continua
    # sendo um retangulo.
    # O PAPEL e o que sobra, e precisa ser marcado EXPLICITAMENTE.
    #
    # Sem ele o filtro nao sabe onde pode empurrar para branco sem medo, e o
    # fundo para na metade do caminho: medido, o Magico pro chegava a 219 numa
    # escala em que 255 e branco, quando a queixa do Kaique e "queremos que
    # fique branca a pagina e so as letras pretas".
    #
    # A folga em volta e para o branco nao encostar na borda da letra: ali mora
    # a rampa de antisserrilhamento, e apaga-la e o que faz a letra virar
    # escada.
    folga = max(3, int(FOLGA_DO_PAPEL * min(altura, largura)) | 1)
    ocupado = cv2.dilate(
        (gravura | letra).astype(np.uint8),
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (folga, folga)),
    ) > 0
    papel = ~ocupado

    for mascara, tipo, rotulo in ((gravura, GRAVURA, "gravura"),
                                  (letra, LETRA, "letra"),
                                  (papel, PAPEL, "papel")):
        if not mascara.any():
            continue
        origem = REDE if achados else AUTOMATICO
        for regiao in de_mascara(mascara.astype(np.uint8), tipo=tipo, origem=origem,
                                 suavidade=SUAVIDADE, rotulo=rotulo):
            selecao.acrescentar(regiao)

    # A duvida viaja junto com a selecao, e quem a usa decide o que fazer
    # com ela. Ver DESENHO_OU_ESCRITA em core/analise.py.
    selecao.em_duvida = em_duvida
    return selecao


def refinar_para_tinta(
    img: np.ndarray, mascara_letra: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Desce um bloco de texto ao nivel do traco.

    Devolve (letra, papel_dentro_do_bloco). O bloco marcado como texto contem
    duas coisas muito diferentes: o traco, que precisa de contraste e nitidez,
    e o papel entre as linhas, que deve ir a branco. Tratar o bloco inteiro
    como letra impede o papel de branquear justamente onde ele mais aparece.

    A ORLA COLADA NO TRACO nao entra em nenhum dos dois. Ela nao e traco, mas
    tambem nao pode ir a branco chapado: ali mora a rampa de antisserrilhamento,
    os poucos pixels de tom intermediario que arredondam a letra. Jogada a
    branco, a letra vira escada - medido pela regua do projeto, era a queixa de
    "letra pixelada" reaparecendo pelo caminho da selecao, com a rampa do Boecio
    caindo de 0,72 para 0,45 pixels. Sem a orla, o papel entre as linhas
    continua indo a branco igual.
    """
    if not mascara_letra.any():
        vazia = np.zeros(img.shape[:2], bool)
        return vazia, vazia
    tinta = mascara_de_tinta(_tres_canais_ou_cinza(img))

    lado = max(3, int(min(img.shape[:2]) * ORLA_DO_TRACO) | 1)
    com_a_orla = cv2.dilate(
        tinta.astype(np.uint8),
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    return tinta & mascara_letra, (~com_a_orla) & mascara_letra


def _tres_canais_ou_cinza(img: np.ndarray) -> np.ndarray:
    """Garante BGR de 3 canais - varias contas aqui usam cv2.cvtColor(..., HSV/etc)
    que exige 3 canais, mesmo quando a pagina de entrada e so cinza."""
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def modelo_disponivel() -> bool:
    """Informa se o modelo de layout esta instalado."""
    return _detector.disponivel


def explicar_em_portugues(selecao: Selecao) -> list[str]:
    """O que o programa achou, em frases para a tela."""
    if selecao.vazia:
        return ["Não achei gravura nesta página - vou tratar a folha inteira igual."]
    gravuras = sum(1 for r in selecao.regioes if r.tipo == GRAVURA)
    letras = sum(1 for r in selecao.regioes if r.tipo == LETRA)
    frases = []
    if gravuras:
        frases.append(f"Achei {gravuras} área de gravura ou foto."
                      if gravuras == 1 else
                      f"Achei {gravuras} áreas de gravura ou foto.")
    if letras:
        frases.append(f"Achei {letras} bloco de texto." if letras == 1 else
                      f"Achei {letras} blocos de texto.")
    frases.append("Confira e corrija se eu errei.")
    return frases
