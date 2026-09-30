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

QUEM ACHA A GRAVURA (item 1.2 da Fase 1, ligado em 29/09/2026)
    Dois caminhos, escolhidos pelo parametro detector_de_gravura de detectar():

    - GRAVURA_SCANTAILOR: o seletor de gravura do ScanTailor Advanced, com o
      codigo original (core/gravura_scantailor.py + core/nativo/st_gravura.dll).
      So a ZONA GRAVURA vem dele; a letra e o papel continuam saindo daqui, do
      mesmo jeito (modelo de layout + tinta), agora em volta da gravura nova.
      Roda numa linha a parte, AO MESMO TEMPO que o modelo de layout e a
      mascara de tinta (a DLL solta o GIL), para a pagina nao demorar a soma
      dos dois. A pagina vai a DLL no DPI do escaneamento (nunca mais pontos
      do que o scan tem; teto de 300): ver _dpi_para_a_gravura.
    - GRAVURA_ANTIGA: o caminho de sempre (layout + cor + tinta), identico ao
      de antes do 1.2. E o padrao de detectar() para quem nao sabe o DPI da
      imagem (a aba Marcar, core/camadas.py, avaliar_selecao.py).

    Quem escolhe no processamento e core/pipeline.py (garantir_selecao), com
    DETECTOR_DE_GRAVURA_PADRAO e FORMA_DA_GRAVURA_PADRAO - o botao de ligar e
    desligar (regra 8 do plano) ainda nao existe na tela. Se a DLL faltar ou
    falhar numa pagina, cai sozinho no caminho antigo, com o motivo no log e
    em selecao.aviso_gravura; nada levanta excecao.
"""

from __future__ import annotations

import logging
import threading
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

_log = logging.getLogger(__name__)

# --- quem acha a gravura (item 1.2) -----------------------------------------

GRAVURA_SCANTAILOR = "scantailor"   # o seletor do ScanTailor Advanced (a DLL)
GRAVURA_ANTIGA = "antigo"           # layout + cor + tinta, como antes do 1.2
DETECTORES_DE_GRAVURA = (GRAVURA_SCANTAILOR, GRAVURA_ANTIGA)

# O que o processamento usa enquanto nao houver campo no projeto nem botao na
# tela (regra 8). Proposta de fabrica do implementador, a decidir pelo Samuel:
# o ScanTailor na forma "livre" (a do teste de 24/09 que o Samuel viu). A
# "retangular" cobre foto inteira (a estatua do Opus Majus 20), mas pega de
# 55% a 96% das paginas do Livro de Horas: serve para livro de foto, por
# escolha do livro, nunca de fabrica.
DETECTOR_DE_GRAVURA_PADRAO = GRAVURA_SCANTAILOR
FORMA_DA_GRAVURA_PADRAO = "livre"
# "desligada" = nao procurar gravura nenhuma (o botao de desligar da regra 8;
# decisao do Samuel de 30/09: as opcoes do ScanTailor vao para a tela).
FORMA_DESLIGADA = "desligada"
FORMAS_DA_GRAVURA = ("livre", "retangular", FORMA_DESLIGADA)

# Quem achou a gravura desta pagina, quando a forma e "desligada": ninguem.
GRAVURA_NENHUMA = "nenhuma"


@dataclass(frozen=True)
class OpcoesDaGravura:
    """As opcoes do detector de gravuras do ScanTailor Advanced (aba "Saida",
    modo Misto), com os padroes dele. Por livro: modelos.Projeto guarda cada
    uma (gravura_forma, gravura_sensibilidade, gravura_mais_sensivel,
    gravura_normalizar) e core/pipeline.escolha_da_gravura monta esta.

    forma: "livre" | "retangular" | "desligada";
    sensibilidade: 0 a 100, so vale na retangular (o ScanTailor so a usa ali);
    mais_sensivel: "maior sensibilidade de busca" (vale nas duas formas);
    normalizar: igualar a iluminacao da pagina antes de procurar.
    Seguro mudar: nada aqui muda os padroes do Samuel sem mudar modelos.py.
    """

    forma: str = FORMA_DA_GRAVURA_PADRAO
    sensibilidade: int = 100
    mais_sensivel: bool = False
    normalizar: bool = True

    def corrigida(self) -> "OpcoesDaGravura":
        """A mesma, com valor invalido trocado pelo padrao (forma
        desconhecida) ou levado para dentro da faixa (sensibilidade)."""
        forma = self.forma if self.forma in FORMAS_DA_GRAVURA else FORMA_DA_GRAVURA_PADRAO
        try:
            sensibilidade = int(self.sensibilidade)
        except (TypeError, ValueError):
            sensibilidade = 100
        return OpcoesDaGravura(forma, max(0, min(100, sensibilidade)),
                               bool(self.mais_sensivel), bool(self.normalizar))


def assinatura_da_gravura(detector: str, opcoes: OpcoesDaGravura) -> str:
    """Um texto curto que muda sempre que a gravura achada sozinha mudaria.

    Fica guardado na pagina (ConfigPagina.gravura_feita_com) junto com a
    marcacao que o detector fez: se o livro ou a pagina passam a pedir
    outras opcoes, a assinatura deixa de bater e core/pipeline.garantir_selecao
    refaz so a parte que a maquina marcou (a marcacao a mao fica). A
    sensibilidade so entra na forma retangular (e so ali que o ScanTailor a
    usa): mexer nela num livro "livre" nao refaz nada. Arriscado: tirar um
    campo daqui faz a mudanca dele nao refazer a gravura.
    """
    o = opcoes.corrigida()
    if detector != GRAVURA_SCANTAILOR:
        return detector
    if o.forma == FORMA_DESLIGADA:
        return f"{detector}|{o.forma}"
    sens = o.sensibilidade if o.forma == "retangular" else "-"
    return f"{detector}|{o.forma}|{sens}|{int(o.mais_sensivel)}|{int(o.normalizar)}"

# Teto do DPI da pagina que vai a DLL. O ScanTailor trabalha a 300 DPI por
# dentro (to300dpi): mandar mais so custa a reducao. Ver _dpi_para_a_gravura.
DPI_MAXIMO_DA_GRAVURA = 300

# Teto do tamanho em que a DLL trabalha por dentro (a pagina levada a 300 DPI),
# em milhoes de pontos. Ver _dpi_declarado_a_dll.
PONTOS_MAXIMOS_DA_GRAVURA = 7_000_000

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


def _gravura_antiga(colorida: np.ndarray, gravura_layout: np.ndarray,
                    letra_layout: np.ndarray, tinta: np.ndarray, usar_cor: bool) -> np.ndarray:
    """A zona gravura do caminho de sempre (antes do item 1.2): caixas do
    modelo + cor + buracos tapados + foto de pagina inteira.

    So foi tirada de dentro de detectar() para poder ser trocada pela do
    ScanTailor; a conta e a mesma, na mesma ordem. Arriscado mudar: e o que o
    programa faz com o ScanTailor desligado, e quando a DLL falha.
    """
    altura, largura = colorida.shape[:2]
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
    return gravura


# Onde o modelo de layout viu texto E ha letra miuda embaixo (escrita_certa),
# o texto ganha tambem da gravura do ScanTailor? Ver o comentario em
# detectar() e relatorios/melhorias.md (29/09/2026).
ESCRITA_GANHA_DO_SCANTAILOR = True

# Pedaco de gravura do ScanTailor menor que isto (fracao da pagina) sai: e
# borrao de tinta no meio do texto (Marial 150: "lugar", "Tambem", palavras
# soltas, de 0,06% a 0,15% da pagina), nao gravura. O mesmo numero que o
# filtro usa para "respingo" (core.filtros.AREA_MINIMA_DE_GRAVURA): abaixo
# dele o filtro nem limpa a gravura pelo papel dela, e so a deixaria cinza
# no meio da letra preta - e ainda faria o filtro rodar o Melhorar na folha
# inteira (a lentidao de 29/09). Seguro mudar para menos, medindo de novo.
AREA_MINIMA_DA_GRAVURA_ST = 0.002

# O ScanTailor marca como gravura a faixa escura do scanner que o corte deixou
# na beirada da pagina (Marial 150 e 153: uma moldura vermelha fina em volta
# da folha, mais grossa de um lado). No ScanTailor de verdade isso nao
# acontece: ele procura so dentro da caixa do conteudo. Aqui, o pedaco que
# ENCOSTA na beirada da imagem e vive quase todo (FRACAO_NA_BEIRADA da area)
# na faixa da beirada (BEIRADA_DO_SCANNER do menor lado) sai. Uma moldura de
# verdade fica dentro da margem do papel (nao encosta), ou tem a maior parte
# para dentro da faixa. Medido em 29/09: no Marial 150, sem esta regra, a
# faixa (4,9% da pagina) fazia o Preto e branco daquela pagina levar 12,8 s
# em vez de 2,3 s (a gravura em volta da folha inteira roda o Melhorar na
# folha toda).
# Arriscado: engordar a faixa, ou baixar a fracao, pode tirar a moldura de
# uma pagina cortada rente a ela.
BEIRADA_DO_SCANNER = 0.05
FRACAO_NA_BEIRADA = 0.80

# A mesma coisa quando a faixa e mais larga (Horas 27: a sombra da lombada, na
# beirada esquerda, 1 cm de largura por 100% da altura): o pedaco que ENCOSTA
# numa beirada da pagina e e uma tira - fino na direcao dessa beirada (ate
# TIRA_FINA do lado) e comprido ao longo dela (pelo menos TIRA_COMPRIDA) -
# sai. Moldura de verdade e um anel: a caixa dela e larga nos dois sentidos.
TIRA_FINA = 0.06
TIRA_COMPRIDA = 0.30


def _limpar_gravura_do_scantailor(mascara: np.ndarray) -> np.ndarray:
    """Tira da gravura do ScanTailor os respingos e a faixa do scanner.

    Ver AREA_MINIMA_DA_GRAVURA_ST, BEIRADA_DO_SCANNER e _sem_barras_na_beirada.
    O resto fica como o ScanTailor achou, ponto a ponto.
    """
    if not mascara.any():
        return mascara
    mascara = _sem_barras_na_beirada(mascara)
    altura, largura = mascara.shape[:2]
    num, rotulos, stats, _ = cv2.connectedComponentsWithStats(mascara.astype(np.uint8),
                                                              connectivity=8)
    minimo = AREA_MINIMA_DA_GRAVURA_ST * mascara.size
    faixa = max(1, int(round(BEIRADA_DO_SCANNER * min(altura, largura))))
    beirada = np.ones((altura, largura), bool)
    beirada[faixa:altura - faixa, faixa:largura - faixa] = False
    # quanto de cada pedaco cai na faixa da beirada
    na_beirada = np.bincount(rotulos[beirada], minlength=num)
    fica = np.zeros(num, bool)
    for k in range(1, num):
        area = int(stats[k, cv2.CC_STAT_AREA])
        if area < minimo:
            continue
        if (_encosta_na_beirada(stats[k], largura, altura)
                and na_beirada[k] >= FRACAO_NA_BEIRADA * area):
            continue
        if _e_tira_na_beirada(stats[k], largura, altura):
            continue
        fica[k] = True
    return fica[rotulos]


# A barra encostada na beirada e "fina" ate este tanto do outro lado da pagina.
# Mais larga que TIRA_FINA: no Graduale 222 a pauta cortada no alto, presa a
# faixa escura, tem 8% da altura. Uma foto que encosta na beirada tem muito
# mais (Opus Majus 20: a pagina toda).
BARRA_FINA = 0.10


def _sem_barras_na_beirada(mascara: np.ndarray) -> np.ndarray:
    """Tira as BARRAS finas encostadas na beirada da pagina, mesmo presas a
    outro pedaco da gravura.

    Item 1.2 (Graduale 222, 30/09/2026): a faixa escura da beirada direita e
    a pauta cortada no alto viravam gravura, e as duas estavam ligadas numa
    peca so, cuja caixa e larga e alta - a regra da tira (_e_tira_na_beirada)
    nao as via. Aqui as barras sao separadas do resto por abertura com uma
    linha comprida (TIRA_COMPRIDA do lado): so fica o que e comprido naquela
    direcao. A barra que encosta na beirada da pagina e e fina (ate TIRA_FINA
    do outro lado) sai. Moldura de verdade fica dentro da margem (nao
    encosta); foto que vai ate a beirada e grossa (nao e fina).
    Arriscado: engordar BARRA_FINA tira a borda de foto que encosta na beirada.
    """
    altura, largura = mascara.shape[:2]
    m = mascara.astype(np.uint8)
    fora = np.zeros_like(m)
    for deitada in (True, False):
        comprimento = int(TIRA_COMPRIDA * (largura if deitada else altura))
        if comprimento < 3:
            continue
        linha = cv2.getStructuringElement(
            cv2.MORPH_RECT, (comprimento, 1) if deitada else (1, comprimento))
        barras = cv2.morphologyEx(m, cv2.MORPH_OPEN, linha)
        if not barras.any():
            continue
        num, rotulos, stats, _ = cv2.connectedComponentsWithStats(barras, connectivity=8)
        for k in range(1, num):
            x, y, w, h = (int(v) for v in stats[k, :4])
            if deitada:
                encosta = y <= 1 or y + h >= altura - 1
                fina = h <= BARRA_FINA * altura
            else:
                encosta = x <= 1 or x + w >= largura - 1
                fina = w <= BARRA_FINA * largura
            if encosta and fina:
                fora[rotulos == k] = 1
    if not fora.any():
        return mascara
    return mascara & (fora == 0)


def _encosta_na_beirada(caixa, largura: int, altura: int) -> bool:
    """A caixa (x, y, largura, altura) toca a borda da imagem?"""
    x, y, w, h = (int(v) for v in caixa[:4])
    return x <= 1 or y <= 1 or x + w >= largura - 1 or y + h >= altura - 1


# Item 1.2 (Graduale 222, 30/09/2026): a caixa "figure" do modelo julgada
# escrita (partitura, caligrafia) tira area da gravura do ScanTailor, como a
# caixa de texto (ESCRITA_GANHA_DO_SCANTAILOR). Seguro desligar (False): o
# Graduale volta a ter faixas da pauta como gravura.
ESCRITA_DA_FIGURA_GANHA = True
# A peca da gravura que tem mais que isto dentro dessa caixa sai INTEIRA (o
# resto dela, fora da caixa, era a mesma pauta). So vale para a caixa
# "figure" julgada escrita: a caixa de texto (escrita_certa) tira so o que
# esta dentro dela - na Horas 26 ela cobre metade da moldura cheia, e a
# moldura tem de ficar.
PECA_QUASE_TODA_ESCRITA = 0.5

# Item 1.2 (Horas 13, 30/09/2026): o ScanTailor pega so a beirada de dentro
# da moldura dourada fina (37% do dourado, medido a 300 DPI): o resto da
# faixa ficava fora da gravura e ia para o filtro da pagina. A gravura
# CRESCE, ate CRESCER_ATE do menor lado da pagina, por tudo que encosta nela
# e nao e papel (mais escuro que o papel ou com outra cor): a faixa dourada
# inteira entra; o papel em volta para o crescimento. Medido nas 13 paginas
# do 1.2: a Horas 13 passa de 3,3% para 5,4% da pagina (a moldura inteira);
# as outras mudam ate 2 pontos (a beirada da foto do Opus 20, o vao escuro).
# Arriscado: crescer demais leva letra encostada na gravura (a escrita ganha
# depois, onde o modelo viu texto) e mancha do verso escura.
CRESCER_ATE = 0.02
ALTURA_DO_CRESCIMENTO = 1200    # a conta e feita numa copia reduzida (tempo)
# O que e papel, para o crescimento: claro perto do papel da pagina (L no
# percentil 90) e com a cor dele (distancia de cor no LAB).
PAPEL_CLARO = 0.85
PAPEL_COR = 14


def _nao_e_papel(img: np.ndarray) -> np.ndarray:
    """Onde a pagina NAO e papel: mais escuro que PAPEL_CLARO do papel, ou
    com cor diferente dele (distancia no LAB acima de PAPEL_COR)."""
    lab = cv2.cvtColor(_tres_canais_ou_cinza(img), cv2.COLOR_BGR2LAB).astype(np.float32)
    luz = lab[..., 0]
    nivel = float(np.percentile(luz, 90))
    claro = luz >= nivel * 0.95
    if not claro.any():
        return np.ones(luz.shape, bool)
    a0 = float(np.median(lab[..., 1][claro]))
    b0 = float(np.median(lab[..., 2][claro]))
    cor = np.hypot(lab[..., 1] - a0, lab[..., 2] - b0)
    return (luz < nivel * PAPEL_CLARO) | (cor > PAPEL_COR)


def _crescer_pela_moldura(mascara: np.ndarray, img: np.ndarray) -> np.ndarray:
    """A gravura do ScanTailor cresce pelo que encosta nela e nao e papel,
    ate CRESCER_ATE do menor lado (ver o comentario la). Nunca encolhe: o
    que o ScanTailor marcou fica. Feita numa copia de ALTURA_DO_CRESCIMENTO
    pontos de altura e levada de volta ao tamanho da pagina."""
    if not mascara.any():
        return mascara
    altura, largura = mascara.shape[:2]
    escala = min(1.0, ALTURA_DO_CRESCIMENTO / altura)
    tamanho = (max(1, int(round(largura * escala))), max(1, int(round(altura * escala))))
    pequena = cv2.resize(mascara.astype(np.uint8), tamanho, interpolation=cv2.INTER_NEAREST)
    foto = cv2.resize(img, tamanho, interpolation=cv2.INTER_AREA) if escala < 1 else img
    pode = _nao_e_papel(foto).astype(np.uint8) | pequena
    nucleo = np.ones((3, 3), np.uint8)
    atual = pequena
    for _passo in range(max(1, int(CRESCER_ATE * min(tamanho)))):
        nova = cv2.dilate(atual, nucleo) & pode
        if np.array_equal(nova, atual):
            break
        atual = nova
    crescida = cv2.resize(atual, (largura, altura), interpolation=cv2.INTER_NEAREST) > 0
    return crescida | mascara


def _e_tira_na_beirada(caixa, largura: int, altura: int) -> bool:
    """A caixa (x, y, largura, altura, area do connectedComponentsWithStats)
    encosta numa beirada da pagina e e uma tira ao longo dela? Ver TIRA_FINA."""
    x, y, w, h = (int(v) for v in caixa[:4])
    em_pe = ((x <= 1 or x + w >= largura - 1) and w <= TIRA_FINA * largura
             and h >= TIRA_COMPRIDA * altura)
    deitada = ((y <= 1 or y + h >= altura - 1) and h <= TIRA_FINA * altura
               and w >= TIRA_COMPRIDA * largura)
    return bool(em_pe or deitada)


def _dpi_para_a_gravura(dpi: float, dpi_do_scan: float | None) -> float:
    """O DPI em que a pagina vai a DLL do ScanTailor.

    O menor entre: o DPI em que a pagina foi desenhada, o do escaneamento
    (quando se sabe) e DPI_MAXIMO_DA_GRAVURA. Por que o do escaneamento:
    medido em 29/09 no Marial 150 (escaneado a 72 DPI), a mesma pagina de
    texto ia a DLL desenhada a 110 DPI e saia 98% "gravura"; desenhada a 72,
    150, 200 ou 300, saia 3% a 5%. Ampliar o scan so inventa pontos que o
    ScanTailor le de outro jeito conforme a ampliacao; no DPI do scan, a
    previa (110 DPI) e o PDF (300 DPI) dao quase a mesma imagem de entrada, e a
    mesma gravura. E e o que o ScanTailor recebeu no teste de 24/09 (as
    paginas como foram escaneadas).
    Arriscado mudar: tirar o dpi_do_scan traz de volta o caso do Marial 150.
    """
    alvo = float(dpi)
    if dpi_do_scan and dpi_do_scan > 0:
        alvo = min(alvo, float(dpi_do_scan))
    return min(alvo, float(DPI_MAXIMO_DA_GRAVURA))


def _dpi_declarado_a_dll(largura: int, altura: int, dpi: float) -> float:
    """O DPI que se diz a DLL para uma imagem de largura x altura pontos a `dpi`.

    O proprio `dpi`, a menos que a pagina levada a 300 DPI (o que a DLL faz
    por dentro) passe de PONTOS_MAXIMOS_DA_GRAVURA: ai se diz um DPI maior, na
    medida para ela caber. Por que (29/09/2026, regra 6 do plano): os livros
    que o PDF diz escaneados a 72 DPI (Marial, Livro de Horas, Graduale) viram
    folhas de 24 x 33 cm a 36 x 51 cm, e a DLL trabalha em 11 a 23 milhoes de
    pontos: 1,4 a 2,8 s por pagina, mais que todo o resto do detector - a
    previa do Marial ficava 0,6 a 1,3 s mais lenta. O 72 desses PDFs nao e a
    resolucao de verdade (e o padrao de quem gravou o PDF), e o proprio
    ScanTailor do teste de 24/09 trabalhou as paginas do Livro de Horas a 168
    DPI. Medido em 29/09 (pagina desenhada a 300 DPI, sem teto x com teto):
    com teto de 7 milhoes a DLL cai de 1,2-2,9 s para 0,7-1,2 s nessas
    paginas; onde a gravura e grande (Horas 11, 26, 47) a mascara fica igual
    (99,9% em comum); a moldura fina da Horas 13 e 27 muda o contorno (57% e
    90% em comum; cobre 3,2% e 6,9% da pagina, contra 4,9% e 6,3%), como ja
    mudava entre 72 e 150 DPI no relatorio do nucleo; o Graduale 222 marca
    menos da partitura como gravura (14% da pagina, contra 31%) e o Marial
    153 nada (contra 2,3%, uma mancha no meio do texto). Paginas que ja cabem
    (Palatino, Opus Majus, Escola, Rhetorica, Pesel, Siebmacher, Boecio) nao
    mudam. Com 6 milhoes a Escola (6,9) entraria; com 9, o Marial ficava
    0,3 a 0,6 s mais lento na deteccao.
    Arriscado mudar: subir o teto devolve a lentidao; baixar demais faz a DLL
    ver a letra pequena demais.
    """
    a_300 = (largura * 300.0 / dpi) * (altura * 300.0 / dpi)
    if a_300 <= PONTOS_MAXIMOS_DA_GRAVURA:
        return float(dpi)
    return float(dpi) * (a_300 / PONTOS_MAXIMOS_DA_GRAVURA) ** 0.5


def _gravura_pelo_scantailor(img: np.ndarray, dpi: float | None, dpi_do_scan: float | None,
                             opcoes: "OpcoesDaGravura | str") -> tuple[np.ndarray | None, str | None]:
    """(mascara bool do tamanho de img, None) ou (None, motivo em portugues).

    opcoes: as do livro (OpcoesDaGravura), ou so a forma (texto), com o resto
    no padrao. A forma "desligada" nao chega aqui (detectar() nem procura).

    Nunca levanta excecao: qualquer falha vira motivo, e vai (uma vez por
    sessao, com o detalhe tecnico) para o erros.log e para o aviso da tela
    (_avisar_uma_vez).
    """
    try:
        if not dpi or dpi <= 0:
            return _falhou("O detector de gravura do ScanTailor precisa saber a resolução "
                           "da página; usei o detector antigo.", "garantir_selecao sem dpi")
        if isinstance(opcoes, str):
            opcoes = OpcoesDaGravura(forma=opcoes)
        if opcoes.forma not in FORMAS_DA_GRAVURA:
            _log.warning("forma de gravura desconhecida: %r (usei a livre)", opcoes.forma)
        opcoes = opcoes.corrigida()
        from core import gravura_scantailor

        altura, largura = img.shape[:2]
        alvo = _dpi_para_a_gravura(dpi, dpi_do_scan)
        entrada = img
        if alvo < float(dpi) * 0.999:
            escala = alvo / float(dpi)
            entrada = cv2.resize(img, (max(1, round(largura * escala)), max(1, round(altura * escala))),
                                 interpolation=cv2.INTER_AREA)
        declarado = _dpi_declarado_a_dll(entrada.shape[1], entrada.shape[0], alvo)
        resultado = gravura_scantailor.detectar_gravura(
            entrada, declarado, forma=opcoes.forma, sensibilidade=opcoes.sensibilidade,
            mais_sensivel=opcoes.mais_sensivel, normalizar_iluminacao=opcoes.normalizar)
        if not resultado.disponivel:
            return _falhou(f"{resultado.motivo} Usei o detector antigo nesta página.",
                           resultado.detalhe_tecnico)
        mascara = resultado.mascara
        if mascara.shape[:2] != (altura, largura):
            # de volta ao tamanho da pagina, com a borda pela media (e nao em
            # degraus do tamanho do ponto reduzido)
            mascara = cv2.resize(mascara.astype(np.uint8) * 255, (largura, altura),
                                 interpolation=cv2.INTER_LINEAR) >= 128
        return _crescer_pela_moldura(_limpar_gravura_do_scantailor(mascara), img), None
    except Exception as erro:  # noqa: BLE001 - a gravura nunca derruba a pagina
        return _falhou("O detector de gravura do ScanTailor falhou nesta página; usei o "
                       "detector antigo.", f"{type(erro).__name__}: {erro}")


def _falhou(motivo: str, detalhe: str | None) -> tuple[None, str]:
    """Anota a falha (erros.log e tela, uma vez: _avisar_uma_vez) e devolve
    o (None, motivo) de _gravura_pelo_scantailor."""
    _avisar_uma_vez(motivo, detalhe)
    return None, motivo


class _ProcuraNoScanTailor:
    """A gravura do ScanTailor calculada numa linha a parte.

    Comeca ao nascer; resultado() espera acabar. A DLL solta o GIL (ctypes), e
    o modelo de layout e o OpenCV tambem: as duas contas andam juntas, e a
    pagina demora o maior dos dois, e nao a soma. Seguro mudar: rodar sem
    linha a parte (chamar _gravura_pelo_scantailor direto) da o mesmo
    resultado, so mais devagar.
    """

    def __init__(self, img, dpi, dpi_do_scan, opcoes) -> None:
        self._saida: tuple = (None, "O detector de gravura do ScanTailor não terminou; "
                                    "usei o detector antigo.")
        self._linha = threading.Thread(target=self._rodar, args=(img, dpi, dpi_do_scan, opcoes),
                                       name="gravura-scantailor", daemon=True)
        self._linha.start()

    def _rodar(self, img, dpi, dpi_do_scan, opcoes) -> None:
        self._saida = _gravura_pelo_scantailor(img, dpi, dpi_do_scan, opcoes)

    def resultado(self) -> tuple[np.ndarray | None, str | None]:
        self._linha.join()
        return self._saida


# Bug de 30/09/2026 (parecer do verificador do 1.2): o aviso de DLL faltando
# ou falhando ia so para o `logging` do Python, que o programa nao grava em
# arquivo nenhum: no programa instalado (sem console) se perdia, e a tela
# nada dizia. Agora vai para o erros.log (registro.registrar_erro, o mesmo
# de todo erro do programa), uma vez por motivo por sessao, e deixa UMA frase
# para a tela, uma vez por sessao (aviso_da_gravura_para_a_tela; quem mostra
# e ui/janela_principal.py). As falhas vem das linhas das previas e do
# processar: a tranca protege as duas listas.
AVISO_DA_GRAVURA_NA_TELA = ("O detector de gravuras não pôde ser usado; usei o antigo. "
                            "As outras funções continuam funcionando.")
_JA_AVISADOS: set[str] = set()
_TRANCA_DOS_AVISOS = threading.Lock()
_AVISO_DA_TELA = {"pendente": None, "ja_mostrado": False}


def _avisar_uma_vez(motivo: str | None, detalhe: str | None = None) -> None:
    """Anota, uma vez por sessao para cada motivo, por que o ScanTailor nao
    foi usado: no erros.log (com o detalhe tecnico, nunca na tela) e no log
    do Python; e deixa a frase da tela pendente, se ela ainda nao foi
    mostrada nesta sessao. Nunca levanta excecao."""
    if not motivo:
        return
    with _TRANCA_DOS_AVISOS:
        if motivo in _JA_AVISADOS:
            return
        _JA_AVISADOS.add(motivo)
        if not _AVISO_DA_TELA["ja_mostrado"]:
            _AVISO_DA_TELA["pendente"] = AVISO_DA_GRAVURA_NA_TELA
    _log.warning("gravura: %s (%s)", motivo, detalhe)
    try:
        from registro import registrar_erro

        registrar_erro("detector de gravura (item 1.2)",
                       motivo + (f"\ndetalhe: {detalhe}" if detalhe else ""))
    except Exception:  # noqa: BLE001 - anotar nunca derruba a pagina
        pass


def aviso_da_gravura_para_a_tela() -> str | None:
    """A frase para a tela quando o detector de gravuras falhou nesta sessao,
    UMA vez: devolve e esquece (a proxima chamada devolve None). Chamada por
    ui/janela_principal.py quando chega uma previa ou termina o processar."""
    with _TRANCA_DOS_AVISOS:
        frase = _AVISO_DA_TELA["pendente"]
        if frase is not None:
            _AVISO_DA_TELA["pendente"] = None
            _AVISO_DA_TELA["ja_mostrado"] = True
        return frase


def detectar(
    img: np.ndarray,
    usar_layout: bool = True,
    usar_cor: bool = True,
    *,
    detector_de_gravura: str = GRAVURA_ANTIGA,
    forma_da_gravura: str | None = None,
    opcoes_da_gravura: OpcoesDaGravura | None = None,
    dpi: float | None = None,
    dpi_do_scan: float | None = None,
) -> Selecao:
    """Devolve a selecao proposta para esta pagina.

    detector_de_gravura: quem acha a zona GRAVURA (ver "QUEM ACHA A GRAVURA",
        no topo). GRAVURA_SCANTAILOR precisa de `dpi` (o DPI em que `img` foi
        desenhada); sem ele, ou sem a DLL, vale o caminho antigo e o motivo
        fica em selecao.aviso_gravura.
    opcoes_da_gravura: as opcoes do ScanTailor (OpcoesDaGravura; so valem
        para ele). Sem elas, as de fabrica, com a forma de forma_da_gravura
        ("livre", "retangular" ou "desligada") quando dada. Forma "desligada"
        = nao procurar gravura: a DLL nem e chamada, e a pagina fica sem
        gravura achada sozinha (gravura_por = GRAVURA_NENHUMA). A capa e a
        foto de pagina inteira sem conteudo (_folha_nua_ou_objeto) continuam
        marcadas: e protecao do Preto e branco, nao busca de gravura.
    dpi_do_scan: o DPI do escaneamento (a imagem embutida no PDF); limita o
        DPI em que a pagina vai a DLL. None/0 = desconhecido.

    A selecao devolvida leva dois atributos a mais, que NAO vao para o
    projeto salvo: gravura_por (qual detector achou a gravura desta pagina) e
    aviso_gravura (por que o ScanTailor nao foi usado, em portugues; None se
    foi, ou se nem foi pedido).

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
    selecao.gravura_por = GRAVURA_ANTIGA
    selecao.aviso_gravura = None

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

    # Item 1.2: o ScanTailor comeca a procurar a gravura AGORA, numa linha a
    # parte, e trabalha enquanto esta linha faz a tinta e o modelo de layout.
    # E recolhido mais abaixo, onde a gravura antiga seria montada.
    opcoes = (opcoes_da_gravura or OpcoesDaGravura(
        forma=forma_da_gravura or FORMA_DA_GRAVURA_PADRAO)).corrigida()
    procura_st = None
    nao_procurar = (detector_de_gravura == GRAVURA_SCANTAILOR
                    and opcoes.forma == FORMA_DESLIGADA)
    if detector_de_gravura == GRAVURA_SCANTAILOR and not nao_procurar:
        procura_st = _ProcuraNoScanTailor(colorida, dpi, dpi_do_scan, opcoes)
    elif detector_de_gravura not in DETECTORES_DE_GRAVURA:
        _log.warning("detector de gravura desconhecido: %r (usei o antigo)", detector_de_gravura)

    tinta = mascara_de_tinta(colorida)
    if not achados:
        achados = _detector.achar(colorida) if usar_layout else []

    gravura_layout = np.zeros((altura, largura), bool)
    letra_layout = np.zeros((altura, largura), bool)
    # Onde o modelo viu texto E ha mesmo letra miuda embaixo. E o unico sinal
    # forte o bastante para tirar area da gravura, mais adiante.
    escrita_certa = np.zeros((altura, largura), bool)
    # Caixa "figure" do modelo que as medidas de baixo dizem ser ESCRITA
    # (partitura, caligrafia: nem desenho de traco, nem foto, nem meio-tom).
    # So a gravura do ScanTailor usa (ver ESCRITA_DA_FIGURA_GANHA).
    escrita_da_figura = np.zeros((altura, largura), bool)
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
                escrita_da_figura[fatia] = True
        elif a.classe in CLASSES_DE_LETRA:
            letra_layout[fatia] = True
            if _tinta_em_pedacos_de_glifo(tinta[fatia]) >= PEDACOS_DE_GLIFO_DE_ESCRITA:
                escrita_certa[fatia] = True

    gravura_st = None
    if nao_procurar:
        gravura_st = np.zeros((altura, largura), bool)
        selecao.gravura_por = GRAVURA_NENHUMA
        em_duvida = False
    if procura_st is not None:
        gravura_st, aviso = procura_st.resultado()
        if gravura_st is not None:
            selecao.gravura_por = GRAVURA_SCANTAILOR
            # A duvida "desenho ou escrita?" nasce das caixas "figure" do
            # modelo, que nao decidem mais a gravura: nao vale aqui.
            em_duvida = False
        else:
            selecao.aviso_gravura = aviso      # ja anotado (_falhou)

    if gravura_st is not None:
        gravura = gravura_st
    else:
        gravura = _gravura_antiga(colorida, gravura_layout, letra_layout, tinta, usar_cor)

    # Legenda impressa sobre a foto continua sendo legenda. No livro de bordados
    # da Pesel as legendas ficam em cima do cartao de fundo, que e colorido: a
    # mascara de cor as engolia junto com a foto e a pagina saia sem uma linha de
    # texto. Onde o modelo viu texto E ha letra miuda embaixo, o texto ganha.
    # Vale tambem para a gravura do ScanTailor (ver ESCRITA_GANHA_DO_SCANTAILOR).
    if gravura_st is None or ESCRITA_GANHA_DO_SCANTAILOR:
        gravura &= ~escrita_certa
    if gravura_st is not None and gravura.any():
        # Item 1.2 (Graduale 222, 30/09/2026): o ScanTailor marca faixas da
        # pauta como gravura; a caixa do modelo em volta da partitura foi
        # julgada ESCRITA (as medidas do detector antigo: partitura 49% a 90%
        # de tinta em pedacos de letra, xilogravura 4% a 14%). Ali o texto
        # ganha tambem. E o que sobrou (a beirada da caixa, a tira da
        # lombada) passa de novo pela limpeza.
        if ESCRITA_DA_FIGURA_GANHA and escrita_da_figura.any():
            # a peca que era quase toda escrita sai inteira (no Graduale 222,
            # a faixa da pauta que passa um pouco para fora da caixa)
            num, rotulos, stats, _ = cv2.connectedComponentsWithStats(
                gravura.astype(np.uint8), connectivity=8)
            dentro = np.bincount(rotulos[escrita_da_figura], minlength=num)
            sai = dentro > PECA_QUASE_TODA_ESCRITA * stats[:, cv2.CC_STAT_AREA]
            sai[0] = False
            gravura &= ~sai[rotulos]
            gravura &= ~escrita_da_figura
        gravura = _limpar_gravura_do_scantailor(gravura)

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
