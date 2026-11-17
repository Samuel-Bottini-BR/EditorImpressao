"""Prints da etapa 4 (testes à distância), fora da tela do Samuel.

Gera dois prints no modelo do CLAUDE.md §10 (faixa com título, alvo em vermelho):
  1. A opção nas Configurações (parte "Testes à distância"), com a caixinha já
     marcada (ligada de fábrica, D-712) e o botão "Pôr a senha dos testes".
  2. A janela pequena da senha (primeira abertura, D-721).

Nada aparece na tela: QT_QPA_PLATFORM=offscreen. Roda com o executor de mentira,
então nada toca o Windows.

Uso: .venv\\Scripts\\python.exe relatorios\\frente-kaique-2026-11-16\\etapa4\\prints.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "prints"
SAIDA.mkdir(exist_ok=True)


def _com_faixa(imagem: QImage, titulo: str, frase: str, alvo) -> QImage:
    """Põe uma faixa verde com título e frase em cima, e um retângulo vermelho
    em volta do alvo (x, y, w, h) — sem cobrir o conteúdo (D-421)."""
    margem, faixa = 16, 64
    largura = imagem.width() + margem * 2
    altura = imagem.height() + margem * 2 + faixa
    tela = QImage(largura, altura, QImage.Format_RGB32)
    tela.fill(QColor("#f3f1ec"))
    p = QPainter(tela)
    p.fillRect(0, 0, largura, faixa, QColor("#2e7d32"))
    p.setPen(QColor("white"))
    f = QFont(); f.setPointSize(13); f.setBold(True); p.setFont(f)
    p.drawText(margem, 26, titulo)
    f2 = QFont(); f2.setPointSize(10); p.setFont(f2)
    p.drawText(margem, 48, frase)
    p.drawImage(margem, faixa + margem, imagem)
    if alvo:
        x, y, w, h = alvo
        caneta = QPen(QColor("#d32f2f")); caneta.setWidth(3); p.setPen(caneta)
        p.drawRect(margem + x - 4, faixa + margem + y - 4, w + 8, h + 8)
    p.end()
    return tela


def main() -> int:
    app = QApplication.instance() or QApplication([])
    from core import testes_a_distancia as td

    class Fake(td.Executor):
        def aplicar(self, passos, senha):
            return td.Resultado(True, passos=passos)

    td.definir_executor(Fake())

    from ui import estilo
    estilo.carregar_o_tema_guardado()

    # 1. A opção nas Configurações
    from ui.tela_configuracoes import TelaConfiguracoes
    config = TelaConfiguracoes(None, parte="Testes à distância")
    config.resize(760, 420)
    config.show()
    app.processEvents()
    img = config.grab().toImage()
    caixa = config.caixa_testes
    canto = caixa.mapTo(config, caixa.rect().topLeft())
    alvo = (canto.x(), canto.y(), caixa.sizeHint().width(), caixa.height())
    _com_faixa(img, "Configurações > Testes à distância",
               "A caixinha já vem marcada (ligada de fábrica). O alvo em vermelho é a opção.",
               alvo).save(str(SAIDA / "1-opcao-nas-configuracoes.png"))
    config.close()

    # 2. A janela da senha (primeira abertura)
    from ui.testes_a_distancia_ui import JanelaSenhaDosTestes
    janela = JanelaSenhaDosTestes(None)
    janela.resize(440, 220)
    janela.show()
    app.processEvents()
    img2 = janela.grab().toImage()
    campo = janela.campo
    alvo2 = (campo.mapTo(janela, campo.rect().topLeft()).x(),
             campo.mapTo(janela, campo.rect().topLeft()).y(), campo.width(), campo.height())
    _com_faixa(img2, "Primeira abertura — a senha dos testes",
               "A janela pequena que pede a senha. O alvo em vermelho é onde o Kaique digita.",
               alvo2).save(str(SAIDA / "2-janela-da-senha.png"))
    janela.close()

    print("prints em", SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
