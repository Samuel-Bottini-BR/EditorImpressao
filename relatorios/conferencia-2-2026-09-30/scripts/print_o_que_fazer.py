"""Print da tela "O que fazer" com o grupo "Gravuras e fotos", SEM abrir janela na tela.

Uso (no .venv do programa):
    .venv\\Scripts\\python.exe relatorios\\conferencia-2-2026-09-30\\scripts\\print_o_que_fazer.py

Monta so a tela (ui/tela_opcoes.py, TelaOpcoes) com o Qt fora da tela
(QT_QPA_PLATFORM=offscreen), com um projeto de mentira apontando para o PDF de
uma pagina do gabarito (somente leitura), e grava dois prints em
relatorios/conferencia-2-2026-09-30/gravuras/:
  - o-que-fazer-fabrica.png: as opcoes de fabrica;
  - o-que-fazer-tem-fotos.png: com "Este livro tem fotos" marcada.
Nada e gravado em projeto nenhum (o Projeto so existe na memoria).
Seguro mudar: tamanho da janela.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# sem isto o Qt fora da tela nao acha fonte nenhuma e as letras saem como quadradinhos
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from PySide6.QtWidgets import QApplication  # noqa: E402

from modelos import Projeto  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO  # noqa: E402
from ui.tela_opcoes import TelaOpcoes  # noqa: E402

SAIDA = Path(__file__).resolve().parents[1] / "gravuras"


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    SAIDA.mkdir(parents=True, exist_ok=True)
    tela = TelaOpcoes()
    tela.setStyleSheet(FOLHA_DE_ESTILO)
    tela.resize(1500, 950)
    pdf = RAIZ / "gabarito" / "paginas" / "opusmajus_p020.pdf"
    projeto = Projeto(caminho_entrada=str(pdf), nome="Opus Majus (exemplo)")
    tela.carregar(projeto, 1)
    tela.show()
    fim = time.time() + 3
    while time.time() < fim:
        app.processEvents()
    tela.grab().save(str(SAIDA / "o-que-fazer-fabrica.png"))
    tela.cx_tem_fotos.setChecked(True)
    for _ in range(20):
        app.processEvents()
    tela.grab().save(str(SAIDA / "o-que-fazer-tem-fotos.png"))
    print("gravado em", SAIDA)


if __name__ == "__main__":
    main()
