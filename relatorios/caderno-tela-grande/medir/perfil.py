"""Onde o fio da tela gasta o tempo (02/11/2026): abrir a tela grande de caderno e trocar as
páginas por caderno, com cProfile, no Gradus Primus. Só para achar a causa de uma parada.

  python relatorios/caderno-tela-grande/medir/perfil.py
"""
from __future__ import annotations

import cProfile
import io
import os
import pstats
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
TRAB = RAIZ / "_tmp" / "perfil-caderno"
if TRAB.exists():
    shutil.rmtree(TRAB)
TRAB.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(TRAB)
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))
LIVRO = TRAB / "gradus.pdf"
shutil.copy(RAIZ / "_tmp" / "livros" / "gradus.pdf", LIVRO)

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
from core import automatico as A  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402


def rodar(seg):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.002)


def esperar(p, seg=600):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        if not p.calculando():
            rodar(0.05)
            if not p.calculando():
                return
        time.sleep(0.005)


def perfil(nome, funcao):
    pr = cProfile.Profile()
    t = time.perf_counter()
    pr.enable()
    funcao()
    app.processEvents()
    pr.disable()
    total = time.perf_counter() - t
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(18)
    print(f"===== {nome}: {total:.3f} s")
    print("\n".join(s.getvalue().splitlines()[:45]))


janela = JanelaPrincipal()
janela.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
janela.resize(1280, 657)
janela.move(-32000, -32000)
janela.show()
janela.abrir_livro(str(LIVRO))
rodar(1.0)
while getattr(janela, "medida_ao_abrir", None) is not None:
    rodar(0.2)
janela.estado_do_automatico.marcadas = {A.CADERNOS}
grande = janela.abrir_o_automatico(A.CADERNOS)
grande.move(-32000, -32000)
folhas = grande.folhas_do_caderno
esperar(folhas)
if folhas.tela_grande is not None:            # já preparada: mede o preparo de novo, à parte
    folhas.tela_grande.deleteLater()
    folhas.tela_grande = None
    rodar(0.2)
perfil("preparar a tela grande (escondida)", folhas._preparar_a_tela_grande)
combo = grande.controles["paginas_por_caderno"]
perfil("trocar para 12", lambda: combo.setCurrentIndex(combo.findData(12)))
esperar(folhas)
perfil("abrir a tela grande de caderno", folhas.abrir_em_tela_cheia)
folhas.tela_grande.accept()
rodar(0.2)
lista = grande.painel_de_opcoes.lista
lista.setCurrentItem(lista.item_da_etapa(A.LIMPAR))
esperar(grande.folhear)
perfil("abrir a tela cheia do antes e depois (a de hoje)", grande.folhear.abrir_em_tela_cheia)
grande.folhear.tela_cheia.accept()
grande.reject()
rodar(0.3)
janela.close()
