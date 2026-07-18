"""Cortar as bordas: tira a borda preta do scanner e a sombra da margem."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Folga deixada em volta do conteudo, em fracao do lado. Sem folga o corte
# encosta na letra e o texto fica sufocado na impressao.
FOLGA = 0.02

# Nunca cortar mais que isso de cada lado. Protege contra o caso em que a
# deteccao se perde e devora metade da pagina.
CORTE_MAXIMO = 0.25

ALTURA_ANALISE = 800

# Se o retangulo detectado encostar no conteudo escuro, avisamos (secao 4.3).
MARGEM_ALERTA_PX = 2


@dataclass(frozen=True)
class Recorte:
    """Area util da pagina, em fracao de 0 a 1: (x, y, largura, altura)."""

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


def detectar_bordas(img: np.ndarray) -> Recorte:
    """Acha o retangulo que contem o conteudo da pagina.

    Ideia: binarizar de forma bem tolerante, achar as linhas e colunas que tem
    tinta de verdade e envolver tudo isso. Bordas pretas do scanner ficam
    coladas na moldura, entao sao descartadas por serem grandes demais para
    caberem no limite de CORTE_MAXIMO.
    """
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    altura_orig, largura_orig = cinza.shape[:2]

    if altura_orig > ALTURA_ANALISE:
        escala = ALTURA_ANALISE / altura_orig
        cinza = cv2.resize(
            cinza, (max(8, int(largura_orig * escala)), ALTURA_ANALISE),
            interpolation=cv2.INTER_AREA,
        )
    altura, largura = cinza.shape[:2]

    # Limiar tolerante: qualquer coisa nitidamente mais escura que o papel.
    nivel_papel = float(np.percentile(cinza, 80))
    limiar = max(20.0, nivel_papel * 0.75)
    tinta = (cinza < limiar).astype(np.uint8)

    # Um fechamento pequeno junta as letras em blocos de texto e evita que uma
    # unica mancha de poeira defina a borda.
    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, nucleo)

    # Uma linha/coluna so conta se tiver tinta suficiente. O limiar baixo (1%)
    # e proposital: uma linha de texto isolada precisa contar.
    limite_linha = max(2, int(largura * 0.01))
    limite_coluna = max(2, int(altura * 0.01))
    linhas = np.where(tinta.sum(axis=1) >= limite_linha)[0]
    colunas = np.where(tinta.sum(axis=0) >= limite_coluna)[0]

    if len(linhas) == 0 or len(colunas) == 0:
        return Recorte.inteiro()  # pagina em branco: nao ha o que recortar

    y0, y1 = int(linhas[0]), int(linhas[-1] + 1)
    x0, x1 = int(colunas[0]), int(colunas[-1] + 1)

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

    encostou = (x0e >= x0) or (y0e >= y0) or (x1e <= x1) or (y1e <= y1)

    return Recorte(
        x=x0e / largura,
        y=y0e / altura,
        largura=(x1e - x0e) / largura,
        altura=(y1e - y0e) / altura,
        encostou_no_conteudo=bool(encostou),
    )


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
