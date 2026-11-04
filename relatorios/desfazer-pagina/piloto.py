"""D-621 na janela de VERDADE: "Desfazer nesta página" pelo botão direito, no Gradus Primus.

Como o piloto do mover-parou (relatorios/mover-parou/piloto.py, ramo mover-parou-2026-11-04): a
janela fora da tela, cliques e teclas por mensagens do Windows ao hwnd
(relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow. O botão direito é
WM_RBUTTONDOWN + WM_RBUTTONUP (o Qt faz dele o pedido de menu, como no mouse de verdade).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF aponta
para a cópia. Na cópia roda o Automático (Endireitar, Cortar, Limpar em Preto e branco, Gravuras)
antes, como o Samuel: "vamos supor que eu passei o automatico e só uma pagina veio com defeito".

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
               r"\scratchpad\desfazer-pagina-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
PRINTS = AQUI / "prints"
LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")
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


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=True)
    from PySide6.QtCore import QPoint
    from ui import desfazer_nesta_pagina as D
    from ui.tela_conferir import ABA_BORDAS, DUAS, UMA

    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    rodar_o_automatico(j)

    # 1. Cortar, Uma página, a página 14
    base.tecla(j, ord("X")); base.esperar(1.5)
    base.clique(j, t.botoes_mostrar[UMA]); base.esperar(1.0)
    ir_pagina(j, VIZINHA)
    print_como_sai(j, "pagina-13-antes")
    vizinha_antes = campos(j, VIZINHA)
    ir_pagina(j, PAGINA)
    anotar("página 14 antes", campos(j, PAGINA))
    anotar("página 14: etapas que mexeram", [D.NOMES[e] for e in D.etapas_que_mexeram(
        j.projeto, j.projeto.paginas[PAGINA - 1])])
    print_como_sai(j, "pagina-14-antes")
    feitas = len(t.acoes.feitas)

    # 2. botão direito na página, "Desfazer nesta página", marcar Corte e Filtro, desfazer
    botao_direito(j, t.visualizadores[ABA_BORDAS])
    abrir_o_submenu_e_marcar(j, ["cortar", "filtro"], "a-pagina-14")
    esperar_previa(j)
    anotar("página 14 depois", campos(j, PAGINA))
    anotar("ações no Histórico (antes, depois)", [feitas, len(t.acoes.feitas)])
    anotar("a última ação", t.acoes.feitas[-1].descricao if t.acoes.feitas else None)
    print_como_sai(j, "pagina-14-depois")
    ir_pagina(j, VIZINHA)
    vizinha_depois = campos(j, VIZINHA)
    anotar("página 13 igual", vizinha_antes == vizinha_depois)
    print_como_sai(j, "pagina-13-depois-igual")

    # 3. Ctrl+Z volta tudo, Ctrl+Y refaz
    ir_pagina(j, PAGINA)
    ctrl(j, ord("Z")); esperar_previa(j)
    anotar("página 14 depois do Ctrl+Z", campos(j, PAGINA))
    print_como_sai(j, "pagina-14-ctrl-z")
    ctrl(j, ord("Y")); esperar_previa(j)
    anotar("página 14 depois do Ctrl+Y", campos(j, PAGINA))
    print_como_sai(j, "pagina-14-ctrl-y")

    # 4. botão direito na miniatura da página 13 (com a 14 na tela): a lista da 13
    from ui.widgets.tira_miniaturas import Miniatura
    mini = next(m for m in t.tira.findChildren(Miniatura) if m.numero == VIZINHA)
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    botao_direito(j, mini)
    menu = getattr(t, "_menu_desfazer", None)
    anotar("miniatura 13: menu da página", getattr(menu.actions()[0].menu(), "indice", -1) + 1
           if menu is not None and menu.actions() else None)
    abrir_o_submenu_e_marcar(j, [], "miniatura-13", apertar=False)
    for m in menus_abertos():
        m.close()
    base.esperar(0.5)
    anotar("página 13 continua igual", campos(j, VIZINHA) == vizinha_depois)

    # 5. "Duas lado a lado": botão direito na página da direita do par
    base.clique(j, t.botoes_mostrar[DUAS]); base.esperar(4)
    lado = t.lado_a_lado
    # a página da vez é a 14 (esquerda do par 14-15); o botão direito vai na 15, a da direita
    alvo = next((ret for pos, ret in lado._ret if lado.indices[pos] == PAGINA), None)
    p(j, "duas-lado-a-lado")
    if alvo is not None:
        ponto = lado.folhas.mapTo(j, QPoint(int(alvo.center().x()), int(alvo.center().y())))
        botao_direito(j, j, ponto)
        menu = getattr(t, "_menu_desfazer", None)
        anotar("duas lado a lado: menu à vista logo depois", menu.isVisible() if menu is not None else None)
        anotar("duas lado a lado: página do menu", getattr(menu.actions()[0].menu(), "indice", -1) + 1
               if menu is not None and menu.actions() else None)
        abrir_o_submenu_e_marcar(j, [], "duas-lado-a-lado-pagina-15", apertar=False)
        for m in menus_abertos():
            m.close()
    else:
        anotar("duas lado a lado: a página 15 não está à vista", lado.indices[:20])
    base.clique(j, t.botoes_mostrar[UMA]); base.esperar(1.5)

    # 6. no Mover, o menu das linhas continua e ganha o "Desfazer nesta página" embaixo
    base.tecla(j, ord("F")); esperar_previa(j)
    from ui.tela_conferir import ABA_MOVER
    vis = t.visualizadores[ABA_MOVER]
    base.print_do_menu_que_abrir("mover-menu-das-linhas", PRINTS, AQUI / "menus.txt")
    botao_direito(j, vis, vis._area.center())
    base.esperar(2)

    anotar("fim", {"ações": len(t.acoes.feitas), "página 14": campos(j, PAGINA)})
    base.fechar(j)


if __name__ == "__main__":
    main()
