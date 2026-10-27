"""A janela de VERDADE, fora da tela (1280 x 657, o tamanho do notebook do Kaique a 150%), no
caminho do Kaique do zero e sem nada marcado (obra de 26/10/2026, etapa 6: ver o livro na área de
trabalho): o "La vida eterna" (uma CÓPIA; o original só é lido) → Automático só com "Dividir"
(pelo clique) → uma página por vez (D-007) → "Duas lado a lado" na barra de baixo (D-015) → rolar
os pares → "antes / depois" (página em Original: a frase; tecla 2, Preto e branco: o antes e
depois) → zoom "+" → "ajustar à tela" → Page Down (10 páginas) → o menu Ver com "Ver lado a lado".

Cliques e teclas por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py). Dados e TEMP numa pasta de saida_teste/, nunca a pasta
de dados do Samuel. Guarda o PID e fecha só a própria janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa6\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a cópia do código antigo para o "antes");
<prefixo> = "depois" ou "antes". Prints em relatorios/obra-etapa6/prints/.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa6" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa6" / f"janela-{PREFIXO}"
LIVRO = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf")
VK_NEXT, VK_2 = 0x22, 0x32


def _p(widget, nome: str):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png")


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def _dividir_pelo_automatico(janela, tela):
    """O Automático só com "Dividir", no livro todo, pelo clique (como nas etapas 4 e 5)."""
    from PySide6.QtCore import QPoint

    from core import automatico as A

    tela.paineis.abrir("automatico")
    base.esperar(0.8)
    painel = tela.paineis.automatico
    lista = painel.lista
    item = next((lista.item(i) for i in range(lista.count())
                 if lista.item(i).data(0x0100) == A.DIVIDIR), None)
    if item is None:
        item = next(lista.item(i) for i in range(lista.count())
                    if lista.item(i).text().startswith(A.NOMES[A.DIVIDIR]))
    ret = lista.visualItemRect(item)
    base.clique(janela, lista.viewport(), QPoint(ret.left() + 14, ret.center().y()))
    base.esperar(0.8)
    base.conferir(painel.estado.marcadas == {A.DIVIDIR}, "Automático: só 'Dividir' marcado, pelo clique")
    base.clique(janela, painel.botao_rodar)
    _esperar_ate(lambda: janela.projeto.dividir_folhas and len(janela.projeto.paginas) > 300, 600)
    base.esperar(3.0)
    tela.paineis.fechar()
    base.esperar(1.0)


def main() -> None:
    (RAIZ / "saida_teste" / "obra-etapa6").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa6" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    PRINTS.mkdir(parents=True, exist_ok=True)
    livro = TRAB / "La vida eterna.pdf"
    shutil.copy2(LIVRO, livro)                     # o original só é lido
    janela = base.nova_janela(1280, 657)
    _p(janela, "00-tela-dos-livros")
    janela.abrir_livro(str(livro))
    base.esperar(2.0)
    tela = janela.tela_conferir
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 240)
    base.esperar(1.0)
    projeto = janela.projeto
    base.conferir(not projeto.dividir_folhas and not projeto.cortar_bordas and not projeto.limpar,
                  "abrir sem nada marcado")
    _p(janela, "01-abrir-o-livro")
    _dividir_pelo_automatico(janela, tela)
    projeto = janela.projeto
    base.esperar(3.0)
    base.conferir(not tela.trabalha_com_folhas and tela.item_atual.metade in ("esquerda", "direita"),
                  "depois de dividir: uma página por vez (D-007)")
    _p(janela, "02-dividido-uma-pagina-por-vez")

    if not hasattr(tela, "botoes_mostrar"):
        # o código antigo: a barra de baixo não tem "Uma página / Duas lado a lado"
        base.conferir("lado_a_lado" not in janela.menu.acoes,
                      "código antigo: o menu Ver não tem 'Ver lado a lado'")
        base.fechar(janela)
        base.gravar_resultados(TRAB)
        return

    from ui.widgets.paginas_rolando import DUAS, UMA

    # "Duas lado a lado" na barra de baixo (D-015), na página 7 (a do teste do Kaique)
    tela.ir_para_pagina(6)
    base.esperar(2.0)
    base.clique(janela, tela.botoes_mostrar[DUAS])
    pares = tela.lado_a_lado
    base.conferir(tela.vista_da_pagina.currentWidget() is pares and tela.mostrar == DUAS,
                  "clique em 'Duas lado a lado': os pares no lugar da página")
    base.conferir(janela.menu.acoes["lado_a_lado"].isChecked(), "o menu Ver acompanha")
    _esperar_ate(lambda: all(p in pares.guardadas for p, _r in pares.retangulos()
                             if _r.intersects(pares.viewport().rect().translated(
                                 0, pares.verticalScrollBar().value()))), 120)
    base.esperar(1.0)
    base.conferir(pares.indice_da_vez() == 6, f"os pares na página da vez (7): {pares.indice_da_vez()}")
    _p(janela, "03-duas-lado-a-lado")
    # rolar os pares (a roda do mouse: rolagem pela barra, como a roda faz)
    barra = pares.verticalScrollBar()
    barra.setValue(barra.value() + pares.viewport().height())
    base.esperar(1.0)
    _esperar_ate(lambda: len(pares.guardadas) >= 6, 120)
    base.esperar(1.0)
    _p(janela, "04-rolando-os-pares")

    # "Uma página" de volta e o "antes / depois"
    base.clique(janela, tela.botoes_mostrar[UMA])
    base.conferir(tela.vista_da_pagina.currentWidget() is tela.area_imagem, "'Uma página' volta")
    tela.ir_para_pagina(6)
    base.esperar(2.0)
    base.clique(janela, tela.botao_antes_depois)
    vista = tela.vista_antes_depois
    base.conferir(tela.vista_da_pagina.currentWidget() is vista, "clique em 'antes / depois'")
    base.conferir(bool(vista.aviso), f"página em Original: '{vista.aviso}'")
    _p(janela, "05-antes-depois-pagina-em-original")
    # a tecla 2 (Preto e branco) com o foco na página, como o Kaique: desliga o antes e
    # depois, clica na página (a Mão: o clique só põe o foco), tecla 2, liga de novo
    base.clique(janela, tela.botao_antes_depois)
    base.clique(janela, tela.editor_selecao)
    base.tecla(janela, VK_2)
    base.esperar(1.0)
    base.conferir(projeto.paginas[6].filtro == "preto_e_branco", "tecla 2: a página 7 em Preto e branco")
    base.clique(janela, tela.botao_antes_depois)
    _esperar_ate(lambda: vista.antes is not None and vista.depois is not None and vista.comparando, 120)
    base.esperar(1.0)
    base.conferir(vista.comparando and vista.rotulos[1] == "depois: Preto e branco",
                  "tecla 2: antes Original × depois Preto e branco")
    _p(janela, "06-antes-depois-preto-e-branco")
    base.clique(janela, tela.botao_antes_depois)
    base.esperar(1.0)

    # zoom "+" duas vezes e "ajustar à tela"
    base.clique(janela, tela.botao_mais_zoom)
    base.clique(janela, tela.botao_mais_zoom)
    base.esperar(1.0)
    base.conferir(tela.rotulo_do_zoom.text() == "156%", f"'+' duas vezes: {tela.rotulo_do_zoom.text()}")
    _p(janela, "07-zoom-156")
    base.clique(janela, tela.botao_ajustar_a_tela)
    base.conferir(tela.rotulo_do_zoom.text() == "100%", "'ajustar à tela': 100%")

    # Page Down: 10 páginas (com o foco na página)
    base.clique(janela, tela.editor_selecao)
    antes = tela.indice_pagina
    base.tecla(janela, VK_NEXT)
    base.esperar(2.0)
    base.conferir(tela.indice_pagina == antes + 10, f"Page Down: da página {antes + 1} para a {tela.indice_pagina + 1}")
    _p(janela, "08-page-down-10-paginas")

    # o menu Ver com "Ver lado a lado"
    menu = janela.menu.menus["Ver"]
    menu.popup(janela.mapToGlobal(janela.rect().topLeft()))
    base.esperar(1.0)
    base.print_window(menu, PRINTS / f"{PREFIXO}-09-menu-ver.png", so_cliente=False)
    base.conferir(any(a.text() == "Ver lado a lado" for a in menu.actions()), "menu Ver: 'Ver lado a lado'")
    menu.close()
    base.esperar(0.5)
    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
