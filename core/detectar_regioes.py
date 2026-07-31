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


# --- o detector -------------------------------------------------------------

def detectar(
    img: np.ndarray,
    usar_layout: bool = True,
    usar_cor: bool = True,
) -> Selecao:
    """Devolve a selecao proposta para esta pagina.

    Tudo que sai daqui e marcado com a origem certa, e por isso pode ser
    apagado sozinho depois - limpar_origem tira a proposta da maquina e mantem
    o que a pessoa desenhou a mao.
    """
    altura, largura = img.shape[:2]
    selecao = Selecao()

    achados = _detector.achar(img) if usar_layout else []
    gravura_layout = _caixas_para_mascara(achados, CLASSES_DE_GRAVURA, altura, largura)
    letra_layout = _caixas_para_mascara(achados, CLASSES_DE_LETRA, altura, largura)

    gravura_cor = mascara_de_cor(img) if usar_cor else np.zeros((altura, largura), bool)

    # A cor so acrescenta onde o layout nao viu nada. Onde ele achou texto, o
    # texto manda: uma inicial rubricada no meio de um paragrafo e letra, nao
    # gravura, e transforma-la em gravura arrancaria o paragrafo do preto e
    # branco.
    gravura = gravura_layout | (gravura_cor & ~letra_layout)
    letra = letra_layout & ~gravura

    for mascara, tipo, rotulo in ((gravura, GRAVURA, "gravura"),
                                  (letra, LETRA, "letra")):
        if not mascara.any():
            continue
        origem = REDE if achados else AUTOMATICO
        for regiao in de_mascara(mascara.astype(np.uint8), tipo=tipo, origem=origem,
                                 suavidade=SUAVIDADE, rotulo=rotulo):
            selecao.acrescentar(regiao)

    return selecao


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
