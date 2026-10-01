r"""Print da tela "O que fazer" com a caixinha nova do Preto e branco, SEM abrir janela na tela.

Quarta conferencia do Samuel (01/10/2026). Uso (no .venv do programa):
    .venv\Scripts\python.exe relatorios\conferencia-4-2026-10-01\scripts\print_tela.py

Monta so a tela (ui/tela_opcoes.py, TelaOpcoes) com o Qt fora da tela
(QT_QPA_PLATFORM=offscreen), com um projeto de mentira apontando para o PDF de
uma pagina do gabarito (somente leitura; nenhuma pagina e processada), e grava
em relatorios/conferencia-4-2026-10-01/tela/:
  - o-que-fazer.png: a tela inteira, com o filtro Preto e branco escolhido e a
    caixinha como vem de fabrica (desmarcada);
  - caixinha.json: onde fica a caixinha "No Preto e branco, molduras e
    iluminuras tambem em preto e branco" no print (para o montar_imagens.py
    marcar o lugar por fora).
Nada e gravado em projeto nenhum (o Projeto so existe na memoria).
Mesma receita de relatorios/conferencia-2-2026-09-30/scripts/print_o_que_fazer.py.
Seguro mudar: tamanho da janela, o PDF de exemplo.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# sem isto o Qt fora da tela nao acha fonte nenhuma e as letras saem como quadradinhos
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from modelos import Projeto  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO  # noqa: E402
from ui.tela_opcoes import TelaOpcoes  # noqa: E402

SAIDA = Path(__file__).resolve().parents[1] / "tela"


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    SAIDA.mkdir(parents=True, exist_ok=True)
    tela = TelaOpcoes()
    tela.setStyleSheet(FOLHA_DE_ESTILO)
    tela.resize(1500, 950)
    pdf = RAIZ / "gabarito" / "paginas" / "horas_p013.pdf"
    projeto = Projeto(caminho_entrada=str(pdf), nome="Livro de Horas (exemplo)")
    tela.carregar(projeto, 1)
    tela.show()
    fim = time.time() + 3
    while time.time() < fim:
        app.processEvents()
    # o filtro Preto e branco escolhido, para a caixinha aparecer junto do filtro a que se refere
    # (so na tela em memoria; nada e gravado)
    tela.radios_de_filtro["preto_e_branco"].setChecked(True)
    for _ in range(20):
        app.processEvents()
    tela.grab().save(str(SAIDA / "o-que-fazer.png"))
    cx = tela.cx_decoracao_pb
    canto = cx.mapTo(tela, QPoint(0, 0))
    info = {"caixinha": [canto.x(), canto.y(), canto.x() + cx.width(), canto.y() + cx.height()],
            "marcada": cx.isChecked(), "texto": cx.text(),
            "tamanho_da_tela": [tela.width(), tela.height()]}
    (SAIDA / "caixinha.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print("gravado em", SAIDA, info)


if __name__ == "__main__":
    main()
