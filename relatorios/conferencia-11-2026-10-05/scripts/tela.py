r"""Prints de tela da conferencia 11 (05/10/2026), SEM abrir janela (Qt fora da tela).
PROTOTIPO: nada aqui muda o programa; as mudancas sao feitas so nos widgets em memoria.

1. q1-caixinha-hoje.png: o grupo dos filtros REAL da tela "O que fazer" (ui/tela_opcoes.py,
   TelaOpcoes.painel_filtros), com o Preto e branco escolhido e a caixinha das molduras marcada.
2. q1-caixinha-simulacao.png: SIMULACAO de "como ficaria" a opcao (a) da P5: o mesmo grupo, com
   uma caixinha "Só as letras" acrescentada AQUI (ela nao existe no programa; o lugar e o texto
   finais ainda nao foram decididos) marcada, e a caixinha das molduras apagada
   (setEnabled(False)), guardando a marca que tinha.
3. q3-scantailor-janela-zona.png: a janela "Zone Properties" do ScanTailor Advanced v1.2.1,
   desenhada a partir do arquivo de tela dele (src/core/filters/output/PictureZonePropDialog.ui,
   copia local, somente leitura) - nao e foto da janela do ScanTailor rodando.

Mesma receita de relatorios/conferencia-4-2026-10-01/scripts/print_tela.py. Nenhum projeto e
gravado (o Projeto so existe na memoria). Uso: .venv\Scripts\python.exe ...\scripts\tela.py
"""
from __future__ import annotations

import os
import re
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

import comum11  # noqa: E402  (poe a worktree no caminho e isola a pasta de dados)

from PySide6.QtCore import QBuffer, QByteArray  # noqa: E402
from PySide6.QtUiTools import QUiLoader  # noqa: E402
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel  # noqa: E402

from modelos import Projeto  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO, TEXTO_FRACO, estilo_da_caixinha_com_quadrado  # noqa: E402
from ui.tela_opcoes import TelaOpcoes  # noqa: E402

UI_SCANTAILOR = (r"D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1"
                 r"\src\core\filters\output\PictureZonePropDialog.ui")


def esperar(app, s=1.0):
    fim = time.time() + s
    while time.time() < fim:
        app.processEvents()


def main() -> None:
    app = QApplication.instance() or QApplication([])
    tela = TelaOpcoes()
    tela.setStyleSheet(FOLHA_DE_ESTILO)
    tela.resize(1100, 950)
    pdf = comum11.GABARITO / "paginas" / "horas_p013.pdf"
    tela.carregar(Projeto(caminho_entrada=str(pdf), nome="Livro de Horas (exemplo)"), 1)
    tela.show()
    esperar(app, 2)
    tela.radios_de_filtro["preto_e_branco"].setChecked(True)
    tela.cx_decoracao_pb.setChecked(True)
    esperar(app, 0.5)
    painel = tela.painel_filtros
    painel.grab().save(str(comum11.AQUI / "q1-caixinha-hoje.png"))

    # --- simulacao: "Só as letras" marcada e a caixinha das molduras apagada ---
    bloco = tela.cx_decoracao_pb.parentWidget().layout()
    grade = painel.layout()
    alvo = None
    for i in range(grade.count()):
        item = grade.itemAt(i)
        if item.layout() is not None and item.layout().indexOf(tela.cx_decoracao_pb) >= 0:
            alvo = item.layout()
    assert alvo is not None, bloco
    so_letras = QCheckBox("Só as letras (simulação: esta caixinha ainda não existe)")
    so_letras.setStyleSheet(estilo_da_caixinha_com_quadrado(14))
    so_letras.setChecked(True)
    frase = QLabel("marcada, só as letras viram preto e branco; gravuras, fotos, molduras e "
                   "iluminuras ficam como no original")
    frase.setWordWrap(True)
    frase.setContentsMargins(28, 0, 0, 6)
    frase.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
    alvo.insertWidget(0, frase)
    alvo.insertWidget(0, so_letras)
    tela.cx_decoracao_pb.setEnabled(False)
    esperar(app, 0.5)
    painel.grab().save(str(comum11.AQUI / "q1-caixinha-simulacao.png"))
    print("q1 ok", tela.cx_decoracao_pb.isChecked(), tela.cx_decoracao_pb.isEnabled())

    # --- a janela de zona do ScanTailor, do arquivo .ui dele ---
    texto = open(UI_SCANTAILOR, encoding="utf-8").read()
    texto = re.sub(r'class="output::PictureZonePropDialog"', 'class="QDialog"', texto)
    texto = texto.replace("<class>output::PictureZonePropDialog</class>", "<class>Janela</class>")
    texto = texto.replace("output::PictureZonePropDialog", "Janela")
    buf = QBuffer()
    buf.setData(QByteArray(texto.encode("utf-8")))
    buf.open(QBuffer.ReadOnly)
    janela = QUiLoader().load(buf)
    janela.findChild(QCheckBox)  # nada; so para garantir que carregou
    from PySide6.QtWidgets import QRadioButton
    janela.findChild(QRadioButton, "zonepainter2").setChecked(True)
    janela.resize(340, 230)
    janela.show()
    esperar(app, 0.5)
    janela.grab().save(str(comum11.AQUI / "q3-scantailor-janela-zona.png"))
    print("janela ok", [r.text() for r in janela.findChildren(QRadioButton)])


if __name__ == "__main__":
    main()
