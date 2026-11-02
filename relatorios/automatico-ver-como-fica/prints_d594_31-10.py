"""Prints da 4ª rodada (31/10/2026): D-594 (as opções do painel Filtro no "Limpar a folha" do
Automático) e D-577 (o "comparar" com a aba das opções e o "usar este" em cada lado).

Roda sem tela (QT_QPA_PLATFORM=offscreen), num livro sintético (o das provas,
tests/test_decisoes_automatico._livro) e numa pasta de projetos só dele em _tmp. Grava os PNG
nesta pasta (8-*.png e 9-*.png). Uso, na raiz da cópia:
    $env:QT_QPA_PLATFORM="offscreen"; .venv\\Scripts\\python.exe relatorios\\automatico-ver-como-fica\\prints_d594_31-10.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"          # sem isto o modo sem tela desenha caixinhas no lugar das letras
AQUI = Path(__file__).resolve().parent


def main() -> None:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    import projetos
    from core import automatico as A
    from core.filtros import MAGICO_PRO, PRETO_E_BRANCO
    from tests.test_decisoes_automatico import _livro

    pasta = Path(tempfile.mkdtemp(dir=RAIZ / "_tmp", prefix="prints_d594_"))
    (pasta / "projetos").mkdir()
    projetos.pasta_dos_projetos = lambda: pasta / "projetos"
    from ui.janela_principal import JanelaPrincipal

    def assentar(n=8):
        for _ in range(n):
            app.processEvents()

    def esperar(*paineis):
        fim = time.monotonic() + 180
        while time.monotonic() < fim:
            assentar(2)
            if not any(p is not None and p.calculando() for p in paineis):
                assentar()
                if not any(p is not None and p.calculando() for p in paineis):
                    return
            time.sleep(0.03)

    janela = JanelaPrincipal()
    janela.resize(1500, 900)
    janela.show()
    janela.abrir_livro(_livro(pasta))
    assentar()
    janela.tela_conferir.ir_para_pagina(2)
    grande = janela.abrir_o_automatico()
    grande.resize(1500, 900)
    e = grande.estado
    e.marcar(A.LIMPAR, True)
    grande.mostrar_etapa(A.LIMPAR)
    grande.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    esperar(grande.antes_e_depois)
    grande.grab().save(str(AQUI / "8-automatico-limpar-preto-e-branco-mais-ajustes.png"))
    grande.combo_algoritmo_pb.showPopup()
    assentar()
    grande.grab().save(str(AQUI / "8-automatico-jeito-do-preto-e-branco.png"))
    grande.combo_algoritmo_pb.hidePopup()
    grande.radios_de_filtro[MAGICO_PRO].setChecked(True)
    grande.seletor_luz_chuvisco.setValue(30)
    grande.controles["luz_igualar"].setChecked(True)
    esperar(grande.antes_e_depois)
    grande.grab().save(str(AQUI / "8-automatico-limpar-magico-pro-chuvisco-30.png"))
    grande.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    esperar(grande.antes_e_depois)

    # o "comparar" da tela cheia
    painel = grande.antes_e_depois
    painel.abrir_em_tela_cheia()
    tela = painel.tela_cheia
    from PySide6.QtCore import Qt

    tela.setWindowState(Qt.WindowNoState)        # o modo sem tela tem uma tela pequena
    tela.resize(1800, 950)
    tela.botao_comparar.click()
    esperar(painel)
    tela.grab().save(str(AQUI / "9-comparar-abas-fechadas.png"))
    tela.lado_a.botao_opcoes.click()
    tela.lado_b.botao_opcoes.click()
    tela.lado_b.painel.mostrar_etapa(A.LIMPAR)
    tela.lado_a.painel.mostrar_etapa(A.LIMPAR)
    tela.lado_b.painel.radios_de_filtro[MAGICO_PRO].setChecked(True)
    esperar(painel, tela.lado_b.motor)
    tela.grab().save(str(AQUI / "9-comparar-abas-abertas-direita-magico-pro.png"))
    tela.lado_b.botao_usar.click()
    esperar(painel, tela.lado_b.motor)
    tela.grab().save(str(AQUI / "9-comparar-depois-de-usar-este-da-direita.png"))
    tela.accept()
    assentar()
    grande.grab().save(str(AQUI / "9-janela-depois-de-usar-este-magico-pro.png"))
    print("filtro da janela:", e.opcoes["filtro_padrao"])
    janela._fechar_a_janela_do_automatico()
    assentar()
    janela.close()


if __name__ == "__main__":
    main()
