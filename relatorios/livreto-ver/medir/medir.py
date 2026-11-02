"""Copia do medir.py do verificador (02/11/2026), com SEM_GRAVAR=1 para pular o gravar.
Verificador D-574 (02/11/2026): medidas sem print no meio (o PrintWindow roda no fio da tela
e atrapalha a medida da parada). Plataforma Windows de verdade, janela fora da tela.

  python medir.py <copia>   (<copia> = a pasta do codigo: verif-livreto ou verif-livreto-antes)

Mede: (1) quanto a tela para ao criar a janela "Montar para imprimir" com o Palatino;
(2) [so no codigo novo] quanto a tela para enquanto o fio monta a folha (seta, 10 vezes;
trocar caderno); quanto tempo leva uma folha; (3) fechar com a folha montando; (4) gravar
com a folha montando (o fio da previa rodando de verdade no momento do clique).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

COPIA = Path(sys.argv[1]).resolve()
AQUI = Path(__file__).resolve().parent
TRAB = AQUI.parents[2] / "_tmp" / "verif" / f"medir-{COPIA.name}"
TRAB.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(TRAB)
os.chdir(COPIA)
sys.path.insert(0, str(COPIA))
LIVRO = AQUI.parents[2] / "_tmp" / "livros" / (os.environ.get("LIVRO", "palatino") + ".pdf")

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
from core import impressao as imp  # noqa: E402
from ui.dialogo_impressao import DialogoImpressao  # noqa: E402

MED: dict = {"copia": str(COPIA)}


class Relogio:
    def __init__(self):
        self.ultimo = time.monotonic(); self.maior = 0.0; self.batidas = 0
        self.t = QTimer(); self.t.setInterval(5); self.t.timeout.connect(self.bate); self.t.start()

    def bate(self):
        agora = time.monotonic(); self.maior = max(self.maior, agora - self.ultimo)
        self.ultimo = agora; self.batidas += 1

    def zerar(self):
        self.ultimo = time.monotonic(); self.maior = 0.0; self.batidas = 0


def rodar(seg):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.002)


def quieta(d):
    return (not d._relogio_da_previa.isActive() and not d._previa_pendente
            and not (d.tarefa_previa is not None and d.tarefa_previa.isRunning())
            and not d.bolinha_da_previa.carregando)


def esperar_quieta(d, seg=120):
    t = time.monotonic()
    while time.monotonic() - t < seg and not quieta(d):
        app.processEvents(); time.sleep(0.002)
    return round(time.monotonic() - t, 3)


rel = Relogio()
rodar(0.3)

# (1) criar e mostrar a janela
rel.zerar()
t = time.monotonic()
d = DialogoImpressao(str(LIVRO))
d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
d.move(-32000, -32000)
d.show()
d.move(-32000, -32000)
MED["criar_e_mostrar_s"] = round(time.monotonic() - t, 3)
rodar(0.05)
MED["parada_ao_criar_s"] = round(rel.maior, 3)

if not hasattr(d, "pedir_previa"):
    rodar(2.0)
    destino = TRAB / "gravado.pdf"
    if destino.exists():
        destino.unlink()
    rel.zerar(); t = time.monotonic()
    d.comecar(destino=str(destino))
    while d.tarefa is not None and d.tarefa.isRunning():
        app.processEvents(); time.sleep(0.005)
    MED["gravar"] = {"s": round(time.monotonic() - t, 1), "maior_parada_s": round(rel.maior, 3)}
    print(json.dumps(MED, ensure_ascii=False, indent=1))
    (AQUI / f"medir-{COPIA.name}-{LIVRO.stem}.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1), encoding="utf-8")
    d.close()
    sys.exit(0)

rel.zerar()
MED["primeira_folha_s"] = esperar_quieta(d)
MED["parada_enquanto_monta_a_primeira_s"] = round(rel.maior, 3)

# (2) setas: 10 folhas, cada uma medida
setas = []
for _ in range(10):
    rel.zerar()
    t = time.monotonic()
    d.passar_folha(1)
    feito = esperar_quieta(d)
    setas.append({"folha": d.folha_na_tela.numero, "s": round(time.monotonic() - t, 3),
                  "maior_parada_s": round(rel.maior, 3), "batidas_de_5ms": rel.batidas})
MED["setas"] = setas
rel.zerar(); t = time.monotonic()
d.combo_caderno.setCurrentIndex(d.combo_caderno.findData(16))
esperar_quieta(d)
MED["trocar_caderno"] = {"s": round(time.monotonic() - t, 3), "maior_parada_s": round(rel.maior, 3)}
d.combo_caderno.setCurrentIndex(d.combo_caderno.findData(20)); esperar_quieta(d)

# a montagem sozinha, sem janela (o tempo de uma folha)
o = d.opcoes()
tempos = []
for pos in (0, 5, 15, 31):
    t = time.monotonic(); imp.previa_da_folha(str(LIVRO), o, pos, 300); tempos.append(round(time.monotonic() - t, 3))
MED["previa_da_folha_sozinha_s"] = tempos

# (3) fechar com a folha montando
d.passar_folha(1)
montando = d.tarefa_previa is not None and d.tarefa_previa.isRunning()
rodar(0.05)
montando_depois_de_50ms = d.tarefa_previa is not None and d.tarefa_previa.isRunning()
rel.zerar(); t = time.monotonic()
d.close()
MED["fechar_com_a_folha_montando"] = {"montava_no_clique": montando, "montava_50ms_depois": montando_depois_de_50ms,
                                      "close_levou_s": round(time.monotonic() - t, 3),
                                      "fio_ainda_roda": d.tarefa_previa.isRunning()}
rodar(0.1)
MED["fechar_com_a_folha_montando"]["parada_s"] = round(rel.maior, 3)

if os.environ.get("SEM_GRAVAR"):  # 02/11 (construtor): o gravar e defeito antigo, fora desta tarefa
    print(json.dumps(MED, ensure_ascii=False, indent=1))
    (AQUI / f"medir-{COPIA.name}-{LIVRO.stem}.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0)

# (4) gravar com a folha montando
d2 = DialogoImpressao(str(LIVRO))
d2.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
d2.move(-32000, -32000); d2.show(); d2.move(-32000, -32000)
esperar_quieta(d2)
d2.passar_folha(1)
montando = d2.tarefa_previa is not None and d2.tarefa_previa.isRunning()
destino = TRAB / "gravado.pdf"
if destino.exists():
    destino.unlink()
rel.zerar(); t = time.monotonic()
d2.comecar(destino=str(destino))
clique = round(time.monotonic() - t, 3)
while d2.tarefa is not None and d2.tarefa.isRunning():
    app.processEvents(); time.sleep(0.005)
gravar_s = round(time.monotonic() - t, 1)
parada_gravar = round(rel.maior, 3)
esperar_quieta(d2)
import fitz  # noqa: E402
with fitz.open(str(destino)) as pdf:
    paginas = pdf.page_count
MED["gravar_com_a_folha_montando"] = {"montava_no_clique": montando, "clique_levou_s": clique,
                                      "gravar_s": gravar_s, "maior_parada_durante_o_gravar_s": parada_gravar,
                                      "paginas_no_pdf": paginas,
                                      "folha_depois": d2.folha_na_tela.numero if d2.folha_na_tela else None,
                                      "estado": d2.estado.text()[:60]}
d2.close()
rodar(0.2)
print(json.dumps(MED, ensure_ascii=False, indent=1))
(AQUI / f"medir-{COPIA.name}-{LIVRO.stem}.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1), encoding="utf-8")
