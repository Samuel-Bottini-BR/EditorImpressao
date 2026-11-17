"""Dois prints que faltavam, no "La vida eterna" (CÓPIA), na janela de verdade fora da tela:
X1. o menu Marcar (barra do alto), que tem um "Procurar de novo" (procura as gravuras de novo);
X2. o botão direito numa miniatura da tira de baixo (o menu que existe ali), para comparar com a
    grade "Todas as páginas", onde o botão direito não abre nada.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum as c  # noqa: E402
from comum import base  # noqa: E402
import piloto_grade as g  # noqa: E402
import piloto_livros as lv  # noqa: E402


def main():
    pasta = c.preparar("extra")
    vida = c.copia_da_vida(12)
    j = base.nova_janela(1280, 657)
    t = c.abrir(j, vida)
    c.clicar_rodar(j, c.rodar_automatico(j, {"dividir"}))
    t = j.tela_conferir
    g.abrir_menu(j, pasta, "Marcar", "X1-menu-marcar")
    mini = t.tira._miniaturas[4]
    base.print_do_menu_que_abrir("X2-botao-direito-na-miniatura", pasta, pasta / "menus.txt")
    lv.clique_direito(j, mini)
    base.esperar(3.0)
    base.fechar(j)


if __name__ == "__main__":
    main()
