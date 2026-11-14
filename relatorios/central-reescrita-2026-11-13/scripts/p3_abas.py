"""Print da pergunta b-abas-nomes, de novo: o menu Ver > Lado direito e o jeito "Abas no alto",
esperando mais (no p2 a barra de menu sumiu da foto do "Abas no alto": conferir se é da foto).

Gradus (cópia), aberto do zero, sem Automático; página 11.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

CRU = comum.CRU / "p3"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def main():
    comum.preparar("p3")
    from PySide6.QtCore import QPoint

    from ui.widgets.paineis import LADO_ABAS, LADO_ICONES

    j = comum.nova_janela()
    j.abrir_livro(str(comum.LIVROS / "gradus.pdf"))
    nota("abrir (s)", comum.esperar_tela(j))
    tela = j.tela_conferir
    tela.ir_para_pagina(10)
    comum.esperar_previas(tela, [10])
    comum.foto(j, CRU / "1-fabrica.png")
    lado = j.menu.menu_do_lado_direito
    nota("menu lado direito", [(a.text(), a.isChecked()) for a in lado.actions()])
    lado.popup(j.mapToGlobal(QPoint(700, 120)))
    comum.esperar(1.0)
    comum.foto(lado, CRU / "2-menu-lado-direito.png")
    lado.close()
    j._trocar_lado_direito(LADO_ABAS)
    comum.esperar(4.0)
    nota("barra de menu visivel (abas)", [w.isVisible() for w in [j.menuBar()]] if j.menuBar() else None)
    comum.foto(j, CRU / "3-abas.png")
    j.resize(1281, 657)
    comum.esperar(1.0)
    j.resize(1280, 657)
    comum.esperar(3.0)
    comum.foto(j, CRU / "4-abas-depois-de-redimensionar.png")
    j._trocar_lado_direito(LADO_ICONES)          # devolve o de fábrica (pasta de dados é só deste script)
    comum.esperar(1.0)
    comum.fechar(j)


if __name__ == "__main__":
    main()
