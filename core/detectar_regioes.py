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


@dataclass
class Achado:
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
        return self._carregar() is not None

    def _carregar(self):
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

# Quanto da tinta da pagina os blocos do modelo precisam cobrir para eu confiar
# na proposta dele. Abaixo disto ele viu so um pedaco, e o resto da tinta vira
# letra por conta propria. Ver o comentario em detectar.
COBERTURA_MINIMA_DO_LAYOUT = 0.55


def mascara_de_tinta(img: np.ndarray) -> np.ndarray:
    """Onde ha traco de qualquer especie: letra, neuma, linha de gravura.

    Sauvola local, e nao limiar global: papel envelhecido tem manchas que um
    limiar unico transforma em tinta.
    """
    from core.filtros import binarizar, janela_para_altura

    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    altura, largura = cinza.shape[:2]

    escala = min(1.0, ALTURA_ANALISE / altura)
    pequena = cv2.resize(cinza, (max(8, int(largura * escala)),
                                 max(8, int(altura * escala))),
                         interpolation=cv2.INTER_AREA) if escala < 1 else cinza

    binaria = binarizar(pequena, janela=janela_para_altura(pequena.shape[0]), k=0.20)
    tinta = binaria == 0

    folga = max(1, int(FOLGA_DA_TINTA * min(pequena.shape[:2])) | 1)
    tinta = cv2.dilate(tinta.astype(np.uint8),
                       cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (folga, folga)))

    return cv2.resize(tinta, (largura, altura), interpolation=cv2.INTER_NEAREST) > 0


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
    if _pagina_sem_conteudo(colorida):
        return selecao

    tinta = mascara_de_tinta(colorida)
    achados = _detector.achar(colorida) if usar_layout else []

    gravura_layout = np.zeros((altura, largura), bool)
    letra_layout = np.zeros((altura, largura), bool)
    for a in achados:
        x0, y0, x1, y1 = a.caixa
        fatia = (slice(int(y0 * altura), int(y1 * altura)),
                 slice(int(x0 * largura), int(x1 * largura)))
        if a.classe in CLASSES_DE_GRAVURA:
            # so e gravura de verdade se tiver meio-tom
            if _e_meio_tom(colorida, a.caixa):
                gravura_layout[fatia] = True
            else:
                letra_layout[fatia] = True
        elif a.classe in CLASSES_DE_LETRA:
            letra_layout[fatia] = True

    gravura_cor = mascara_de_cor(colorida) if usar_cor else np.zeros((altura, largura), bool)

    # A cor so acrescenta onde o layout nao viu texto: uma inicial rubricada no
    # meio de um paragrafo e letra, e transforma-la em gravura arrancaria o
    # paragrafo do preto e branco.
    gravura = gravura_layout | (gravura_cor & ~letra_layout)

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

    return selecao


def refinar_para_tinta(
    img: np.ndarray, mascara_letra: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Desce um bloco de texto ao nivel do traco.

    Devolve (letra, papel_dentro_do_bloco). O bloco marcado como texto contem
    duas coisas muito diferentes: o traco, que precisa de contraste e nitidez,
    e o papel entre as linhas, que deve ir a branco. Tratar o bloco inteiro
    como letra impede o papel de branquear justamente onde ele mais aparece.
    """
    if not mascara_letra.any():
        vazia = np.zeros(img.shape[:2], bool)
        return vazia, vazia
    tinta = mascara_de_tinta(_tres_canais_ou_cinza(img))
    return tinta & mascara_letra, (~tinta) & mascara_letra


def _tres_canais_ou_cinza(img: np.ndarray) -> np.ndarray:
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
