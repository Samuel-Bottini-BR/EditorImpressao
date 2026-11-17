"""Prints do brasao girando e do icone, sem abrir nada na tela (D-744 a D-747, 17/11/2026).

Roda fora da tela (QT_QPA_PLATFORM=offscreen): desenha a janela de
carregamento numa imagem, em alguns angulos, e o icone nos tamanhos; poe ao
lado os prints da pagina de exemplo aprovada
(D:\\programas\\EditorImpressao-arquivos\\brasao-previas-17-11\\exemplo-arquivos\\conferencia\\)
para comparar. Grava em relatorios/brasao-2026-11-17/prints/.

    set QT_QPA_PLATFORM=offscreen
    .venv\\Scripts\\python.exe relatorios\\brasao-2026-11-17\\prints.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"  # sem isso o offscreen desenha quadradinhos
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPen  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import brasao  # noqa: E402
import gerar_brasao  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "prints"
EXEMPLO = Path(r"D:\programas\EditorImpressao-arquivos\brasao-previas-17-11\exemplo-arquivos\conferencia")
AZUL, LARANJA, VERDE = QColor("#1f5fbf"), QColor("#e07b00"), QColor("#2e8b3a")


def _fundo_da_pagina(largura: int, altura: int) -> QImage:
    """O mesmo fundo azul da area de teste da pagina de exemplo (135 graus, #0b3d91 -> #6fb3f2)."""
    img = QImage(largura, altura, QImage.Format.Format_ARGB32_Premultiplied)
    p = QPainter(img)
    g = QLinearGradient(0, 0, largura, altura)
    g.setColorAt(0.0, QColor("#0b3d91"))
    g.setColorAt(0.45, QColor("#1f6fd0"))
    g.setColorAt(1.0, QColor("#6fb3f2"))
    p.fillRect(img.rect(), g)
    p.end()
    return img


def _xadrez(largura: int, altura: int) -> QImage:
    """Fundo xadrez cinza: mostra onde a janela e transparente."""
    img = QImage(largura, altura, QImage.Format.Format_ARGB32_Premultiplied)
    p = QPainter(img)
    for y in range(0, altura, 10):
        for x in range(0, largura, 10):
            p.fillRect(x, y, 10, 10, QColor("#d9d9d9") if (x // 10 + y // 10) % 2 else QColor("#f4f4f4"))
    p.end()
    return img


def _faixa(p: QPainter, x: int, y: int, largura: int, texto: str, cor: QColor) -> None:
    p.fillRect(x, y, largura, 34, cor)
    p.setPen(QColor("white"))
    p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    p.drawText(QRectF(x, y, largura, 34), Qt.AlignmentFlag.AlignCenter, texto)


def _legenda(p: QPainter, x: int, y: int, largura: int, texto: str) -> None:
    p.setPen(QColor("#222"))
    p.setFont(QFont("Segoe UI", 10))
    p.drawText(QRectF(x, y, largura, 60), Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, texto)


def _sobre(fundo: QImage, quadro: QImage) -> QImage:
    img = fundo.copy()
    p = QPainter(img)
    p.drawImage(0, 0, quadro)
    p.end()
    return img


def print_angulos() -> Path:
    """A janela de carregamento em 0, 60, 180, 268 e 270 graus, sobre xadrez (transparente)."""
    from ui import brasao_girando as bg

    angulos = [(0, "0 grau: de frente"), (60, "60 graus: girando"),
               (180, "180 graus: de costas, aparece de frente"),
               (268, "268 graus: quase de lado, faixa fina"), (270, "270 graus: de lado exato, nada")]
    largura, altura = bg.tamanho_da_janela()
    margem, topo = 16, 50
    folha = QImage(len(angulos) * (largura + margem) + margem, topo + altura + 90,
                   QImage.Format.Format_ARGB32_Premultiplied)
    folha.fill(QColor("white"))
    p = QPainter(folha)
    _faixa(p, 0, 0, folha.width(), "Programa: a janela de carregamento (xadrez = transparente, sem quadro)", VERDE)
    for i, (angulo, texto) in enumerate(angulos):
        x = margem + i * (largura + margem)
        p.drawImage(x, topo, _sobre(_xadrez(largura, altura), bg.desenhar_quadro(angulo)))
        p.setPen(QPen(QColor("#999"), 1, Qt.PenStyle.DashLine))
        p.drawRect(x, topo, largura - 1, altura - 1)
        _legenda(p, x - 6, topo + altura + 6, largura + 12, texto)
    p.end()
    destino = SAIDA / "01-janela-de-carregamento-angulos.png"
    folha.save(str(destino))
    return destino


def print_comparar_com_o_exemplo() -> Path:
    """Lado a lado: a pagina de exemplo aprovada (azul) e o programa (verde), nos mesmos angulos.

    Os prints da pagina foram tirados em 0,3 s, 1,25 s e 1,9 s da volta de 2,5 s:
    43,2, 180 e 273,6 graus. O programa e desenhado nesses angulos, sobre o
    mesmo fundo azul, no mesmo lugar.
    """
    from ui import brasao_girando as bg

    largura, altura = bg.tamanho_da_janela()
    # Na pagina (print de 1100 x 520, escala 1), o meio do brasao fica em (550, 344).
    cx, cy = 550, 344
    casos = [("giro-0.3.png", 0.3), ("giro-1.25.png", 1.25), ("giro-1.9.png", 1.9)]
    margem, topo = 16, 50
    coluna = largura * 2 + margem
    folha = QImage(len(casos) * (coluna + 2 * margem) + margem, topo + 34 + altura + 70,
                   QImage.Format.Format_ARGB32_Premultiplied)
    folha.fill(QColor("white"))
    p = QPainter(folha)
    _faixa(p, 0, 0, folha.width(), "Mesmo momento da volta: página de exemplo aprovada (azul) e programa (verde)",
           LARANJA)
    for i, (arquivo, segundos) in enumerate(casos):
        angulo = segundos / brasao.SEGUNDOS_POR_VOLTA * 360.0
        x = margem + i * (coluna + 2 * margem)
        exemplo = QImage(str(EXEMPLO / arquivo))
        recorte = exemplo.copy(cx - largura // 2, cy - altura // 2, largura, altura)
        _faixa(p, x, topo, largura, "Página de exemplo", AZUL)
        _faixa(p, x + largura + margem, topo, largura, "Programa", VERDE)
        p.drawImage(x, topo + 34, recorte)
        programa = _sobre(_fundo_da_pagina(largura, altura), bg.desenhar_quadro(angulo))
        p.drawImage(x + largura + margem, topo + 34, programa)
        _legenda(p, x, topo + 34 + altura + 6, coluna,
                 f"{segundos:.2f} s da volta = {angulo:.1f} graus".replace(".", ","))
    p.end()
    destino = SAIDA / "02-comparar-com-a-pagina-de-exemplo.png"
    folha.save(str(destino))
    return destino


def print_icones() -> Path:
    """O icone em todos os tamanhos do .ico: tamanho real e ampliado 4 vezes (pixel a pixel)."""
    imagens = gerar_brasao.ler_ico(brasao.ICONE.read_bytes())
    margem, topo = 20, 50
    largura = sum(lado for lado in imagens) + margem * (len(imagens) + 1)
    folha = QImage(max(largura, 4 * 64 + 4 * 32 + 4 * 16 + 4 * margem), topo + 256 + 40 + 34 + 256 + 40,
                   QImage.Format.Format_ARGB32_Premultiplied)
    folha.fill(QColor("white"))
    p = QPainter(folha)
    _faixa(p, 0, 0, folha.width(), "O ícone (arquivo brasao.ico), cada tamanho desenhado do vetor", VERDE)
    x = margem
    for lado, imagem in sorted(imagens.items()):
        q = QImage(imagem.tobytes(), lado, lado, lado * 4, QImage.Format.Format_RGBA8888).copy()
        p.drawImage(x, topo + 256 - lado, q)
        _legenda(p, x - 10, topo + 256 + 4, lado + 20, str(lado))
        x += lado + margem
    y = topo + 256 + 40
    _faixa(p, 0, y, folha.width(), "Ampliado 4 vezes, sem suavizar (16, 32 e 64)", AZUL)
    x = margem
    for lado in (16, 32, 64):
        imagem = imagens[lado]
        q = QImage(imagem.tobytes(), lado, lado, lado * 4, QImage.Format.Format_RGBA8888).copy()
        grande = q.scaled(lado * 4, lado * 4, Qt.AspectRatioMode.IgnoreAspectRatio,
                          Qt.TransformationMode.FastTransformation)
        p.drawImage(x, y + 34 + 8, _sobre(_xadrez(lado * 4, lado * 4), grande))
        _legenda(p, x, y + 34 + 8 + lado * 4 + 2, lado * 4, f"{lado} (ampliado)")
        x += lado * 4 + margem
    p.end()
    destino = SAIDA / "03-icone-tamanhos.png"
    folha.save(str(destino))
    return destino


def print_icone_nos_lugares() -> Path:
    """O icone carregado pelo Qt (como a janela usa) na barra de titulo, na barra de tarefas e no atalho."""
    from PySide6.QtGui import QIcon

    icone = QIcon(str(brasao.ICONE))
    folha = QImage(760, 220, QImage.Format.Format_ARGB32_Premultiplied)
    folha.fill(QColor("white"))
    p = QPainter(folha)
    _faixa(p, 0, 0, folha.width(), "O ícone como o programa o carrega (setWindowIcon)", VERDE)
    p.fillRect(20, 60, 300, 32, QColor("white"))
    p.setPen(QColor("#ccc"))
    p.drawRect(20, 60, 300, 32)
    p.drawPixmap(30, 68, icone.pixmap(16, 16))
    p.setPen(QColor("#222"))
    p.setFont(QFont("Segoe UI", 10))
    p.drawText(54, 81, "Editor de Impressão (barra de título, 16)")
    p.fillRect(20, 120, 300, 40, QColor("#202a3a"))
    p.drawPixmap(40, 128, icone.pixmap(24, 24))
    p.drawPixmap(80, 132, icone.pixmap(16, 16))
    p.setPen(QColor("white"))
    p.drawText(110, 145, "barra de tarefas (24 e 16)")
    g = QLinearGradient(360, 60, 740, 200)
    g.setColorAt(0, QColor("#0b3d91"))
    g.setColorAt(1, QColor("#6fb3f2"))
    p.fillRect(360, 60, 380, 140, g)
    p.drawPixmap(400, 80, icone.pixmap(48, 48))
    p.drawText(QRectF(370, 132, 130, 40), Qt.AlignmentFlag.AlignHCenter, "Editor de\nImpressão")
    p.drawPixmap(540, 70, icone.pixmap(128, 128))
    p.end()
    destino = SAIDA / "04-icone-nos-lugares.png"
    folha.save(str(destino))
    return destino


def main() -> None:
    QApplication.instance() or QApplication([])
    SAIDA.mkdir(parents=True, exist_ok=True)
    for feito in (print_angulos(), print_comparar_com_o_exemplo(), print_icones(), print_icone_nos_lugares()):
        print(feito)


if __name__ == "__main__":
    main()
