"""Prints das perguntas mover-rotulo-antes e b-abas-nomes (Gradus Primus, cópia).

Gradus aberto do zero; Automático só com "Dividir folhas ao meio" (fábrica), no livro todo.
mover-rotulo-antes (página 11, ferramenta Mover):
  a. "antes / depois" ligado (como é hoje): o antes à esquerda, o depois à direita, o Mover no depois;
  b. "antes / depois" desligado, "Uma página": só a página que o Mover mexe.
b-abas-nomes (página 11):
  c. o lado direito de fábrica ("Ícones na borda"), com o painel Propriedades aberto;
  d. o menu Ver > Lado direito (os quatro jeitos);
  e. o jeito "Abas no alto" (as abas com o nome curto).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

CRU = comum.CRU / "p2"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def main():
    import faulthandler
    faulthandler.dump_traceback_later(2400, exit=True)
    comum.preparar("p2")
    from PySide6.QtCore import QPoint

    from core import automatico as A
    from ui.widgets.paineis import LADO_ABAS
    from ui.widgets.paginas_rolando import UMA
    from ui.widgets.trilha_agrupada import FERRAMENTA_MOVER

    j = comum.nova_janela()
    j.abrir_livro(str(comum.LIVROS / "gradus.pdf"))
    nota("abrir (s)", comum.esperar_tela(j))
    projeto, tela = j.projeto, j.tela_conferir
    estado = j.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("rodou o dividir", j.rodar_o_automatico(esperar=True, perguntar=False))
    comum.esperar(2.0)
    nota("paginas", len(projeto.paginas_ativas))
    try:
        j._fechar_a_janela_do_automatico()
    except Exception:
        pass
    tela.definir_mostrar(UMA)
    tela.escolher_ferramenta(FERRAMENTA_MOVER)
    tela.ir_para_pagina(10)
    comum.esperar(2.0)
    comum.esperar_previas(tela, [10])
    comum.foto(j, CRU / "b-mover-uma-pagina.png")
    nota("antes_depois ligado?", tela.botao_antes_depois.isChecked())

    tela.botao_antes_depois.click()                  # o botão "antes / depois" da barra de baixo
    comum.esperar(3.0)
    comum.esperar_previas(tela, [10])
    nota("antes_depois ligado depois do clique?", tela.botao_antes_depois.isChecked())
    comum.foto(j, CRU / "a-mover-antes-depois.png")
    tela.botao_antes_depois.click()
    comum.esperar(2.0)

    # b-abas-nomes: o lado direito de fábrica (Propriedades aberto, como na ferramenta Mover)
    comum.foto(j, CRU / "c-lado-de-fabrica.png")
    nota("jeito de fabrica", tela.paineis.jeito if hasattr(tela, "paineis") else None)
    menu_ver = None
    for acao in j.menuBar().actions():
        if acao.text().replace("&", "") == "Ver":
            menu_ver = acao.menu()
    if menu_ver is not None:
        menu_ver.popup(j.mapToGlobal(QPoint(520, 30)))
        comum.esperar(0.8)
        comum.foto(menu_ver, CRU / "d-menu-ver.png")
        lado = j.menu.menu_do_lado_direito
        lado.popup(j.mapToGlobal(QPoint(760, 200)))
        comum.esperar(0.8)
        comum.foto(lado, CRU / "d-menu-lado-direito.png")
        nota("menu lado direito", [a.text() for a in lado.actions()])
        lado.close()
        menu_ver.close()
    j._trocar_lado_direito(LADO_ABAS)
    comum.esperar(2.0)
    comum.foto(j, CRU / "e-abas-no-alto.png")
    comum.fechar(j)


if __name__ == "__main__":
    main()
