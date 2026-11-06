"""D-623 na janela de VERDADE: "adicionar página em branco" pelo botão direito na tira, no Gradus.

Como o piloto do mover-parou (relatorios/mover-parou/piloto.py, ramo mover-parou-2026-11-04): a
janela fora da tela, cliques e teclas por mensagens do Windows ao hwnd
(relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow. O botão direito é
WM_RBUTTONDOWN + WM_RBUTTONUP (o Qt faz dele o pedido de menu, como no mouse de verdade).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF aponta
para a cópia.

Rodar (na cópia desfazer-pagina):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\desfazer-pagina\\piloto.py
"""
from __future__ import annotations

import ctypes
import dataclasses
import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f"
               r"\scratchpad\desfazer-pagina-dados-d623")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
PRINTS = AQUI / "prints-d623"
LOG = open(AQUI / "anotacoes-d623.txt", "w", encoding="utf-8")
N = [0]
WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON = 0x0204, 0x0205, 0x0002
PAGINA = 14             # a página que "veio com defeito" (a 14 da D-621)
VIZINHA = 13            # a outra página da mesma folha


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, PRINTS / f"{N[0]:02d}-{nome}.png", so_cliente=False)


def preparar_copia() -> Path:
    """Copia o projeto e o PDF para a pasta de trabalho; o caminho do PDF vai para a cópia."""
    livros = base.TRAB / "livros"
    livros.mkdir(parents=True, exist_ok=True)
    pdf = livros / GRADUS.name
    if not pdf.exists():
        shutil.copy2(GRADUS, pdf)
    destino = base.TRAB / "projetos" / PROJ_ORIGEM.name
    if destino.exists():
        shutil.rmtree(destino)               # só a cópia, na pasta de trabalho deste script
    shutil.copytree(PROJ_ORIGEM, destino)
    for nome in ("projeto.json", "resumo.json"):
        arq = destino / nome
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados["caminho_entrada"] = str(pdf).replace("\\", "/")
        if "pasta" in dados:
            dados["pasta"] = str(destino)
        if "miniatura" in dados:
            dados["miniatura"] = str(destino / "capa.png")
        arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


def esperar_tela(j, limite=300):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)
    return round(time.time() - t, 1)


def esperar_previa(j, limite=90):
    """Espera a prévia da ferramenta da vez chegar (o visualizador para de 'carregar')."""
    t = j.tela_conferir
    vis = t.visualizadores.get(t.aba_atual)
    inicio = time.time()
    base.esperar(0.5)
    while vis is not None and time.time() - inicio < limite and (vis._pixmap is None or vis.carregando):
        base.esperar(0.2)
    base.esperar(1.0)


def campos(j, numero) -> dict:
    pg = j.projeto.paginas[numero - 1]
    return {"angulo_manual": pg.angulo_manual, "recorte": pg.recorte, "filtro": pg.filtro,
            "escala": pg.conteudo_escala, "desloc": pg.conteudo_deslocamento,
            "marcacoes": len(pg.selecao), "respeitar": pg.respeitar_gravuras_achadas,
            "mexida_a_mao": pg.mexida_a_mao, "revisada": pg.revisada, "folha": pg.folha + 1,
            "metade": pg.metade}


def botao_direito(janela, widget, ponto=None):
    """Botão direito por mensagens do Windows, no meio do widget (ou no ponto)."""
    alvo = widget.mapTo(janela, ponto if ponto is not None else widget.rect().center())
    h, lp = int(janela.winId()), base._lp(janela, alvo)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.15)
    base.user32.PostMessageW(h, WM_RBUTTONDOWN, MK_RBUTTON, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, WM_RBUTTONUP, 0, lp); base.esperar(1.0)


def clique_no_menu(menu, ponto):
    """Clique esquerdo por mensagens do Windows na janelinha do menu (ela é outra janela)."""
    h = int(menu.winId())
    lp = base._lp(menu, ponto)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.3)
    base.user32.PostMessageW(h, base.WM_LBUTTONDOWN, base.MK_LBUTTON, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, base.WM_LBUTTONUP, 0, lp); base.esperar(0.8)


def menus_abertos():
    from PySide6.QtWidgets import QApplication, QMenu
    return [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu) and w.isVisible()]


def abrir_o_submenu_e_marcar(j, marcar: list[str], nome: str, apertar=True):
    """Com o menu do botão direito aberto: clica em "Desfazer nesta página" (abre a lista), tira os
    prints, marca as caixinhas `marcar` e aperta "desfazer"."""
    from ui import desfazer_nesta_pagina as D

    menu = getattr(j.tela_conferir, "_menu_desfazer", None)
    if menu is None or not menu.isVisible():
        anotar(f"{nome}: o menu NÃO abriu", [type(m).__name__ for m in menus_abertos()])
        return None
    p(menu, f"{nome}-menu-aberto")
    anotar(f"{nome}: itens do menu", base.acoes_do_menu(menu))
    acao = next(a for a in menu.actions() if a.menu() is not None)
    clique_no_menu(menu, menu.actionGeometry(acao).center())
    sub = acao.menu()
    t0 = time.time()
    while not sub.isVisible() and time.time() - t0 < 5:
        base.esperar(0.2)
    anotar(f"{nome}: a lista abriu", sub.isVisible())
    lista = sub.lista
    anotar(f"{nome}: caixinhas", {D.NOMES[e]: {"acesa": c.isEnabled(), "marcada": c.isChecked()}
                                   for e, c in lista.caixas.items()})
    p(sub, f"{nome}-caixinhas")
    for etapa in marcar:
        caixa = lista.caixas[etapa]
        from PySide6.QtCore import QPoint
        clique_no_menu(sub, caixa.mapTo(sub, QPoint(9, caixa.height() // 2)))   # no quadradinho
    anotar(f"{nome}: marcadas", lista.marcadas())
    anotar(f"{nome}: botão desfazer aceso", lista.botao.isEnabled())
    p(sub, f"{nome}-caixinhas-marcadas")
    if apertar:
        clique_no_menu(sub, lista.botao.mapTo(sub, lista.botao.rect().center()))
        base.esperar(1.5)
        anotar(f"{nome}: menu fechou depois do desfazer", not menu.isVisible())
    return lista


def ctrl(j, tecla_vk):
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL = 0x11, 0xA2
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, VK_CONTROL, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, tecla_vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, tecla_vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    base.user32.SetKeyboardState(est); base.esperar(1.5)


def print_como_sai(j, nome):
    """Print da página como vai sair (a ferramenta dos filtros mostra a página pronta) e volta
    para a ferramenta de antes. Só para ver: a troca de ferramenta é pela tela."""
    t = j.tela_conferir
    antes = t.aba_atual
    t.escolher_ferramenta("filtros"); esperar_previa(j); base.esperar(2)
    p(j, nome)
    from ui.tela_conferir import FERRAMENTA_DA_ABA
    t.escolher_ferramenta(FERRAMENTA_DA_ABA.get(antes, "cortar")); esperar_previa(j)


def ir_pagina(j, numero):
    """Vai à página `numero` (1...) clicando a miniatura da tira."""
    from ui.widgets.tira_miniaturas import Miniatura
    t = j.tela_conferir
    mini = next((m for m in t.tira.findChildren(Miniatura) if m.numero == numero), None)
    if mini is not None:
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(1.0)
    esperar_previa(j)
    anotar(f"na página {numero}", t.indice_pagina + 1)


def rodar_o_automatico(j):
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    estado = j.estado_do_automatico
    estado.marcadas = {A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.GRAVURAS}
    estado.opcoes["filtro_padrao"] = PRETO_E_BRANCO
    estado.alcance = "livro"
    t0 = time.time()
    ok = j.rodar_o_automatico(esperar=True, perguntar=False)
    anotar("Automático rodou", {"ok": ok, "segundos": round(time.time() - t0, 1),
                                "endireitar": j.projeto.endireitar, "cortar": j.projeto.cortar_bordas,
                                "limpar": j.projeto.limpar, "gravuras": j.projeto.detectar_regioes,
                                "filtro do livro": j.projeto.filtro_padrao})
    base.esperar(3)


def clicar_no_item(menu, texto):
    """Escolhe o item `texto` do menu aberto pelo TECLADO (mensagens do Windows à janelinha do
    menu): seta para baixo até ele e Enter. (O clique esquerdo por mensagem num item comum do
    menu, com a janelinha posta fora da tela, fechava o menu sem escolher: anotado no relatório.)"""
    itens = [a for a in menu.actions() if not a.isSeparator() and a.isEnabled()]
    acao = next((a for a in itens if a.text() == texto), None)
    if acao is None:
        anotar("item não achado", [a.text() for a in menu.actions()])
        return False
    disparou = []
    acao.triggered.connect(lambda *_a: disparou.append(True))
    h = int(menu.winId())
    for _ in range(itens.index(acao) + 1):
        base.user32.PostMessageW(h, base.WM_KEYDOWN, 0x28, 1); base.esperar(0.1)   # seta para baixo
        base.user32.PostMessageW(h, base.WM_KEYUP, 0x28, 0xC0000001); base.esperar(0.2)
    anotar(f"item em destaque antes do Enter", menu.activeAction().text() if menu.activeAction() else None)
    p(menu, "menu-com-o-item-em-destaque")
    base.user32.PostMessageW(h, base.WM_KEYDOWN, 0x0D, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, 0x0D, 0xC0000001); base.esperar(2.0)
    anotar(f"{texto!r} escolhido", bool(disparou))
    return bool(disparou)


def resumo(j):
    from core import automatico as A
    pr = j.projeto
    return {"paginas": len(pr.paginas), "no_pdf": len(pr.paginas_ativas),
            "postas_a_mao": [p.indice + 1 for p in pr.paginas if p.inserida],
            "caderno_etapa7": len(A.paginas_do_pdf_depois(pr, A.Pedido(etapas=[A.DIVIDIR]))),
            "acoes": len(j.tela_conferir.acoes.feitas),
            "ultima": j.tela_conferir.acoes.feitas[-1].descricao if j.tela_conferir.acoes.feitas else None}


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=True)
    from ui.tela_conferir import UMA
    from ui.widgets.tira_miniaturas import Miniatura
    import projetos
    pasta = preparar_copia()
    resumo_do_livro = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo_do_livro.caminho_entrada, resumo=resumo_do_livro)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    base.tecla(j, ord("X")); base.esperar(1.5)
    base.clique(j, t.botoes_mostrar[UMA]); base.esperar(1.0)
    ir_pagina(j, 2)
    anotar("antes", resumo(j))
    p(j, "antes")

    # 1. botão direito na miniatura 2: o menu com o Desfazer e os dois novos
    mini = next(m for m in t.tira.findChildren(Miniatura) if m.numero == 2)
    botao_direito(j, mini)
    menu = getattr(t, "_menu_desfazer", None)
    anotar("menu aberto", menu is not None and menu.isVisible())
    p(menu, "menu-da-miniatura-2")
    anotar("itens", base.acoes_do_menu(menu))
    clicar_no_item(menu, "adicionar página em branco depois")
    esperar_previa(j)
    anotar("depois de adicionar depois da 2", resumo(j))
    base.esperar(2)
    p(j, "pagina-em-branco-na-tira")
    ir_pagina(j, 3)
    anotar("página 3", {"inserida": j.projeto.paginas[2].inserida, "em_branco": j.projeto.paginas[2].em_branco,
                        "folha": j.projeto.paginas[2].folha + 1, "metade": j.projeto.paginas[2].metade})
    print_como_sai(j, "pagina-3-em-branco")

    # 2. Ctrl+Z tira, Ctrl+Y põe de novo
    ctrl(j, ord("Z")); esperar_previa(j)
    anotar("depois do Ctrl+Z", resumo(j)); p(j, "ctrl-z")
    ctrl(j, ord("Y")); esperar_previa(j)
    anotar("depois do Ctrl+Y", resumo(j)); p(j, "ctrl-y")

    # 3. "antes" na miniatura 1
    mini = next(m for m in t.tira.findChildren(Miniatura) if m.numero == 1)
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    botao_direito(j, mini)
    clicar_no_item(t._menu_desfazer, "adicionar página em branco antes")
    esperar_previa(j)
    anotar("depois de adicionar antes da 1", resumo(j))
    p(j, "antes-da-1")

    # 4. "tirar do livro" na página em branco (agora a 4)
    ir_pagina(j, 4)
    base.clique(j, t.botao_tirar_do_livro); base.esperar(2)
    anotar("tirada do livro", {"apagada": j.projeto.paginas[3].apagada, **resumo(j)})
    p(j, "tirada-do-livro")

    anotar("fim", resumo(j))
    base.fechar(j)


if __name__ == "__main__":
    main()
