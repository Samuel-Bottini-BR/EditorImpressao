"""Seleção assistida por rede: clicar numa figura e recebê-la recortada.

É o equivalente do "Selecionar Objeto" dos programas de imagem. O modelo é o
MobileSAM, que roda no próprio computador, sem internet e sem placa de vídeo:
meio segundo para preparar a página e quarenta milissegundos por clique.

**A rede só aponta, nunca desenha.** Ela devolve uma máscara - onde está a
coisa - e quem mexe no pixel continua sendo código determinístico. Num livro de
1579, detalhe inventado por uma rede entraria no PDF como se fosse o original,
e isso desqualifica qualquer modelo generativo neste projeto.

Testada em julho de 2026: ela NÃO serve para achar sozinha a zona de gravura de
uma página - segmenta objeto semântico, e clicar no meio de uma estampa devolve
um pedaço de céu. Serve para o que está aqui: a pessoa clica numa figura
específica e recebe o contorno dela, para não precisar contornar à mão.

O programa funciona sem o modelo. Se ele não estiver instalado, o atalho
simplesmente não aparece.
"""

from __future__ import annotations

import threading
from pathlib import Path

import cv2
import numpy as np

PASTA = Path(__file__).resolve().parent.parent / "modelos" / "mobile_sam"
CODIFICADOR = PASTA / "mobile_sam.encoder.onnx"
DECODIFICADOR = PASTA / "sam_vit_h_4b8939.decoder.onnx"

LADO_ENTRADA = 1024

_trava = threading.Lock()
_sessoes: dict[str, object] = {}
_contexto: dict[str, object] = {}


def disponivel() -> bool:
    """Diz se o modelo esta instalado. Sem ele o resto do programa segue igual."""
    return CODIFICADOR.exists() and DECODIFICADOR.exists()


def _carregar():
    """Carrega os dois modelos uma vez so, e guarda."""
    if _sessoes:
        return _sessoes.get("codificador"), _sessoes.get("decodificador")
    if not disponivel():
        return None, None
    try:
        import onnxruntime as ort

        opcoes = ort.SessionOptions()
        opcoes.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        _sessoes["codificador"] = ort.InferenceSession(
            str(CODIFICADOR), opcoes, providers=["CPUExecutionProvider"])
        _sessoes["decodificador"] = ort.InferenceSession(
            str(DECODIFICADOR), opcoes, providers=["CPUExecutionProvider"])
    except Exception:  # noqa: BLE001 - sem a rede o programa continua
        _sessoes["codificador"] = None
        _sessoes["decodificador"] = None
    return _sessoes.get("codificador"), _sessoes.get("decodificador")


def _chave(img: np.ndarray) -> tuple:
    """Identifica a pagina sem guardar a imagem inteira."""
    return (img.shape, int(img[::37, ::37].sum()))


def preparar(img: np.ndarray) -> bool:
    """Codifica a pagina. E a parte cara - meio segundo - e vale para os cliques
    seguintes na mesma pagina."""
    codificador, _ = _carregar()
    if codificador is None:
        return False

    with _trava:
        if _contexto.get("chave") == _chave(img):
            return True

        altura, largura = img.shape[:2]
        escala = LADO_ENTRADA / max(altura, largura)
        pequena = cv2.resize(
            img, (max(1, int(largura * escala)), max(1, int(altura * escala))),
            interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(pequena, cv2.COLOR_BGR2RGB).astype(np.float32)

        try:
            embutido = codificador.run(None, {"input_image": rgb})[0]
        except Exception:  # noqa: BLE001
            return False

        _contexto.update({
            "chave": _chave(img), "embutido": embutido,
            "forma_pequena": rgb.shape[:2], "forma_original": (altura, largura),
            "escala": escala,
        })
        return True


def recortar_no_ponto(img: np.ndarray, ponto: tuple[float, float]) -> np.ndarray | None:
    """A figura que esta sob o ponto, como mascara booleana.

    ponto vem em fracao de 0 a 1. Devolve None se a rede nao estiver
    disponivel ou nao achar nada.
    """
    if not preparar(img):
        return None
    _, decodificador = _carregar()
    if decodificador is None:
        return None

    altura, largura = img.shape[:2]
    escala = float(_contexto["escala"])
    coords = np.array([[[ponto[0] * largura * escala,
                         ponto[1] * altura * escala]]], np.float32)
    rotulos = np.array([[1]], np.float32)

    try:
        with _trava:
            saidas = decodificador.run(None, {
                "image_embeddings": _contexto["embutido"],
                "point_coords": coords,
                "point_labels": rotulos,
                "mask_input": np.zeros((1, 1, 256, 256), np.float32),
                "has_mask_input": np.zeros(1, np.float32),
                "orig_im_size": np.array(_contexto["forma_pequena"], np.float32),
            })
    except Exception:  # noqa: BLE001
        return None

    mascaras, iou = saidas[0], saidas[1]
    melhor = int(np.argmax(iou[0])) if iou.size > 1 else 0
    pequena = mascaras[0][melhor] > 0
    return cv2.resize(pequena.astype(np.uint8), (largura, altura),
                      interpolation=cv2.INTER_NEAREST) > 0


def esquecer() -> None:
    """Solta a pagina guardada. Chamar ao trocar de livro."""
    with _trava:
        _contexto.clear()
