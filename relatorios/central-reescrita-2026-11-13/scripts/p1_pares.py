"""Print da pergunta v-capa-aviso: os pares trocados do La vida eterna e o jeito que já existe hoje
de acertar à mão (botão direito na miniatura da capa -> "adicionar página em branco depois", D-623).

La vida eterna (cópia), aberto do zero; Automático só com "Dividir folhas ao meio" (fábrica), no
livro todo; área de trabalho em "Duas lado a lado".
  1. como é hoje: pares do começo e pares 6-7 (a ímpar impressa à esquerda);
  2. o menu do botão direito da miniatura 1;
  3. depois de "adicionar página em branco depois" da página 1: os mesmos pares.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

CRU = comum.CRU / "p1"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def fotos_dos_pares(j, tela, projeto, indices, prefixo):
    for i in indices:
        tela.ir_para_pagina(i)
        comum.esperar(2.0)
        comum.esperar_previas(tela, [k for k in (i - 1, i, i + 1) if 0 <= k < len(projeto.paginas_ativas)])
        comum.foto(j, CRU / f"{prefixo}-indice-{i:02d}.png")


def main():
    import faulthandler
    faulthandler.dump_traceback_later(2400, exit=True)
    comum.preparar("p1")
    from PySide6.QtCore import QPoint

    from core import automatico as A
    from ui import desfazer_nesta_pagina as dnp
    from ui.widgets.paginas_rolando import DUAS

    j = comum.nova_janela()
    j.abrir_livro(str(comum.LIVROS / "vida_eterna.pdf"))
    nota("abrir (s)", comum.esperar_tela(j))
    projeto, tela = j.projeto, j.tela_conferir
    estado = j.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("rodou o dividir", j.rodar_o_automatico(esperar=True, perguntar=False))
    comum.esperar(2.0)
    nota("paginas depois de dividir", len(projeto.paginas_ativas))
    tela.definir_mostrar(DUAS)
    comum.esperar(1.0)
    fotos_dos_pares(j, tela, projeto, (0, 2, 5), "hoje")

    # o menu do botão direito da miniatura 1 (o mesmo que a tira abre: da_tira=True)
    menu = dnp.abrir_menu(tela, 0, j.mapToGlobal(QPoint(120, 560)), da_tira=True)
    comum.esperar(1.0)
    if menu is not None:
        comum.foto(menu, CRU / "menu-miniatura-1.png")
        nota("menu", [a.text() for a in menu.actions()])
        menu.close()
    comum.esperar(0.5)

    # o clique em "adicionar página em branco depois" da página 1
    nota("pos a pagina em branco", tela.adicionar_pagina_em_branco(0, True))
    comum.esperar(2.0)
    nota("paginas depois", len(projeto.paginas_ativas))
    nota("historico", j.acoes.feitas[-1].descricao)
    tela.definir_mostrar(DUAS)
    fotos_dos_pares(j, tela, projeto, (0, 1, 6), "depois")
    comum.fechar(j)


if __name__ == "__main__":
    main()
