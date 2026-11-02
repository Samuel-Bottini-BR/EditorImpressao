"""Prints de 02/11/2026 (tirar o travamento): o Opus Majus no "Montar para imprimir".

Fora da tela (offscreen, letra Segoe UI carregada a mao, como o prints.py ao lado).
Tira 3 fotos: (1) logo depois de apertar a seta, com a folha montando no
servidor; (2) uma segunda foto 0,5 s depois, ainda montando: se a janela
estivesse parada, esta foto nao sairia na hora; (3) a folha 2 pronta. Anota
quantas vezes um relogio de 5 ms bateu enquanto a folha montava.

Rodar: .venv\\Scripts\\python.exe relatorios\\livreto-ver\\medir\\prints_opus.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
os.environ["QT_QPA_PLATFORM"] = "offscreen"
(RAIZ / "_tmp" / "dados-prints").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados-prints")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core import impressao as imp  # noqa: E402

LIVRO = RAIZ / "_tmp" / "livros" / "opusmajus.pdf"
app = QApplication.instance() or QApplication(sys.argv)
for arquivo in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf"):
    if Path("C:/Windows/Fonts", arquivo).is_file():
        QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts", arquivo)))

from ui.dialogo_impressao import DialogoImpressao  # noqa: E402


def quieta(d) -> bool:
    return (not d._relogio_da_previa.isActive() and not d._previa_pendente
            and not (d.tarefa_previa is not None and d.tarefa_previa.isRunning())
            and not d.bolinha_da_previa.carregando and d.folha_na_tela is not None)


def girar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.005)


def esperar(condicao, segundos=180.0) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim and not condicao():
        app.processEvents()
        time.sleep(0.005)


batidas = []
relogio = QTimer()
relogio.setInterval(5)
relogio.timeout.connect(lambda: batidas.append(time.monotonic()))
relogio.start()

d = DialogoImpressao(str(LIVRO))
d.resize(1000, 640)
d.show()
esperar(lambda: quieta(d))
medidas: dict = {}
batidas.clear()
inicio = time.monotonic()
d.botao_folha_seguinte.click()
girar(0.1)
d.grab().save(str(AQUI / "opus-1-seta-montando.png"))
medidas["foto_1_s"] = round(time.monotonic() - inicio, 2)
girar(0.5)
d.grab().save(str(AQUI / "opus-2-ainda-montando-meio-segundo-depois.png"))
medidas["foto_2_s"] = round(time.monotonic() - inicio, 2)
medidas["montando_na_foto_2"] = d.bolinha_da_previa.carregando
esperar(lambda: quieta(d))
medidas["folha_2_pronta_s"] = round(time.monotonic() - inicio, 2)
girar(0.1)
d.grab().save(str(AQUI / "opus-3-folha-2-pronta.png"))
medidas["batidas_do_relogio_de_5ms"] = len(batidas)
medidas["maior_intervalo_entre_batidas_s"] = round(max(
    b - a for a, b in zip(batidas, batidas[1:])), 3)
medidas["textos"] = [d.rotulos_da_face[lado].text() for lado in (imp.FRENTE, imp.VERSO)]
relogio.stop()
d.reject()
print(json.dumps(medidas, ensure_ascii=False, indent=1))
(AQUI / "prints-opus.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
