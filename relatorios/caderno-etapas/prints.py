"""Prints da D-603 (04/11/2026): as folhas do caderno da etapa 7 seguem as etapas marcadas.

Janela de verdade (Windows), posta fora da tela; pasta de dados própria
(_tmp/dados-prints-caderno-etapas: nada vai para a pasta de dados do Samuel nem para a
dados-teste-rodada-de-consertos). Livro: cópia do Gradus Primus em _tmp/livros (o original não é
tocado), aberto do zero (nada dividido), como no print a-49.

Rodar: .venv\\Scripts\\python.exe relatorios\\caderno-etapas\\prints.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DADOS = RAIZ / "_tmp" / "dados-prints-caderno-etapas"
if DADOS.exists():
    shutil.rmtree(DADOS)
DADOS.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
os.environ["APPDATA"] = str(DADOS)
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication.instance() or QApplication(sys.argv)

import projetos  # noqa: E402
from core import automatico as A  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

PASTA_PROJETOS = DADOS / "projetos"
PASTA_PROJETOS.mkdir()
projetos.pasta_dos_projetos = lambda: PASTA_PROJETOS
FORA = (-4000, 50)
MED: dict = {"pasta_de_dados": str(DADOS)}
PARADA = {"ultimo": 0.0, "maior": 0.0}


def bate() -> None:
    agora = time.monotonic()
    PARADA["maior"] = max(PARADA["maior"], agora - PARADA["ultimo"])
    PARADA["ultimo"] = agora


relogio = QTimer()
relogio.setInterval(5)
relogio.timeout.connect(bate)


def rodar(seg: float) -> None:
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.005)


def esperar(painel, seg: float = 600.0) -> float:
    t = time.monotonic()
    while time.monotonic() - t < seg:
        app.processEvents()
        if not painel.calculando():
            rodar(0.05)
            if not painel.calculando():
                break
        time.sleep(0.01)
    return round(time.monotonic() - t, 2)


def foto(widget, nome: str) -> None:
    """O print. O relógio da parada não conta o próprio grab() (é deste script, não do programa)."""
    rodar(0.2)
    ligado = relogio.isActive()
    relogio.stop()
    widget.grab().save(str(AQUI / nome))
    if ligado:
        PARADA["ultimo"] = time.monotonic()
        relogio.start()


def parada(chave: str) -> None:
    """Guarda a maior parada da tela desde a última marca, e zera."""
    MED[chave] = round(PARADA["maior"], 3)
    PARADA["maior"] = 0.0


def caixinha(grande, etapa: str, marcada: bool) -> None:
    from PySide6.QtCore import Qt

    grande.painel_de_opcoes.lista.item_da_etapa(etapa).setCheckState(
        Qt.Checked if marcada else Qt.Unchecked)


def textos(folhas) -> list[str]:
    return [folhas.rotulos["frente"].text(), folhas.rotulos["verso"].text()]


janela = JanelaPrincipal()
janela.resize(1280, 657)
janela.move(*FORA)
janela.show()
rodar(0.5)
gradus = RAIZ / "_tmp" / "livros" / "gradus.pdf"
janela.abrir_livro(str(gradus))
rodar(1.0)
fim = time.monotonic() + 600
while time.monotonic() < fim and getattr(janela, "medida_ao_abrir", None) is not None:
    rodar(0.2)
MED["paginas_do_livro_aberto"] = len(janela.projeto.paginas_ativas)

estado = janela.estado_do_automatico
estado.marcadas = {A.DIVIDIR}                 # como no print a-49: só a etapa 1 marcada
grande = janela.abrir_o_automatico(A.CADERNOS)
grande.move(FORA[0] + 10, FORA[1] + 10)
grande.resize(1470, 900)          # a lista das 7 etapas inteira à vista, como no print a-49
rodar(0.3)
folhas = grande.folhas_do_caderno
relogio.start()
PARADA["ultimo"], PARADA["maior"] = time.monotonic(), 0.0
MED["01_montando_bolinha"] = folhas.calculando()
foto(grande, "01-etapa-1-marcada-montando.png")
MED["02_primeira_folha_dividida_s"] = esperar(folhas)
MED["02_textos"] = textos(folhas)
parada("parada_02_abrir_com_dividir_s")
foto(grande, "02-etapa-1-marcada-folha-1-dividida.png")

caixinha(grande, A.DIVIDIR, False)
rodar(0.05)
MED["03_desmarcar_bolinha"] = folhas.calculando()
MED["03_desmarcar_s"] = esperar(folhas)
MED["03_textos"] = textos(folhas)
parada("parada_03_desmarcar_s")
foto(grande, "03-etapa-1-desmarcada-scans-inteiros.png")

caixinha(grande, A.DIVIDIR, True)
MED["04_marcar_de_novo_s"] = esperar(folhas)
caixinha(grande, A.MARGENS, True)
rodar(0.05)
MED["04_margens_bolinha"] = folhas.calculando()
MED["04_margens_s"] = esperar(folhas)
MED["04_textos"] = textos(folhas)
parada("parada_04_margens_s")
foto(grande, "04-etapas-1-e-6-marcadas-com-margens.png")

folhas.passar_folha(1)
MED["05_seta_com_margens_s"] = esperar(folhas)
parada("parada_05_seta_s")
foto(grande, "05-etapas-1-e-6-folha-2.png")
relogio.stop()
MED["maior_parada_da_tela_s"] = max(v for k, v in MED.items() if k.startswith("parada_"))
MED["projeto_nao_mudou_paginas"] = len(janela.projeto.paginas_ativas)

grande.reject()
rodar(0.3)
(AQUI / "prints.json").write_text(json.dumps(MED, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(MED, indent=2, ensure_ascii=False))
janela.close()
rodar(0.3)
