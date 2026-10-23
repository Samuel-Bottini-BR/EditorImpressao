"""Prints e conferência da janela DE VERDADE para a etapa 5 do layout (miniaturas, 801 A, 808 A).

Montagem de prints_layout.py; cliques e arrasto por mensagens nativas do Windows (prints_etapa3).
Uso: python prints_etapa5.py <pasta>   (arquivo descartável do agente de layout)."""
import ctypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402
from prints_etapa3 import (RESULTADOS, _lparam, clicar_no_icone, clique_nativo,  # noqa: E402
                           conferir)
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint  # noqa: E402

user32 = ctypes.windll.user32


def foto(janela, nome, contornos=(), popup=None, onde=None):
    cena = r.Cena(janela)
    pix = janela.grab()
    r.ESC = pix.devicePixelRatio()
    cena.img = pix.toImage()
    cena.img.setDevicePixelRatio(1)
    if popup is not None:
        cena.colar(popup, onde)
    cena.inteira(nome, list(contornos))
    return cena


def principal(destino: Path) -> None:
    from ui.widgets.miniaturas import DIREITA, EMBAIXO, ESQUERDA

    r.SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    m = tela.miniaturas
    tela.ir_para_pagina(4)
    esperar(6)
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(3)
    no = r.no_janela
    conferir(m.lugar == EMBAIXO and m.aberta and tela.botao_processar.parent() is tela.lugar_embaixo,
             "de fábrica: miniaturas embaixo, abertas, e o 'Confirmar e processar' ao lado delas")
    foto(janela, "1-embaixo-abertas", [no(m.cabecalho, janela)])
    cena = r.Cena(janela)
    cena.ampliado("1-embaixo-abertas-ampliado", r.com_folga(no(m, janela), 4, janela),
                  "O cabeçalho PÁGINAS: alça, seta, três pontinhos e ver todas")

    clique_nativo(janela, m.seta)
    esperar(1.5)
    conferir(not m.aberta and tela.botao_processar.isVisible()
             and tela.lugar_embaixo.isAncestorOf(tela.botao_processar) is False,
             "clique nativo na seta fechou as miniaturas e o 'Confirmar e processar' desceu para a barra de baixo")
    conferir(not janela.menu.acoes["miniaturas"].isChecked(), "o menu Ver > Miniaturas acompanhou")
    foto(janela, "2-embaixo-fechadas", [no(tela.botao_processar, janela), no(m, janela)])
    clique_nativo(janela, m.seta)
    esperar(1.5)
    conferir(m.aberta and tela.lugar_embaixo.isAncestorOf(tela.botao_processar),
             "clique nativo na seta abriu de novo, e o botão voltou para o lado delas")

    # os três pontinhos
    clique_nativo(janela, m.pontos)
    esperar(0.8)
    conferir(m.menu.isVisible(), "clique nativo nos três pontinhos abriu o menu")
    onde = m.pontos.mapTo(janela, QPoint(0, m.pontos.height()))
    m.menu_lugar.popup(QPoint(-30000, -31000))
    esperar(0.4)
    cena = foto(janela, "3-menu-dos-tres-pontinhos", popup=m.menu, onde=onde)
    cena.colar(m.menu_lugar, QPoint(onde.x() + m.menu.width() - 4,
                                    onde.y() + m.menu.actionGeometry(m.menu_lugar.menuAction()).top()))
    cena.inteira("3-menu-dos-tres-pontinhos")
    m.menu_lugar.close()
    m.menu.close()
    esperar(0.4)
    print("     itens:", [a.text() for a in m.menu.actions() if not a.isSeparator()],
          [a.text() for a in m.menu_lugar.actions()])

    m.acao_em_pares.trigger()
    esperar(1.5)
    conferir(m.em_pares and tela.tira.em_pares, "'Ver em pares' juntou as miniaturas em pares")
    foto(janela, "4-embaixo-em-pares", [no(m, janela)])
    m.acao_em_pares.trigger()
    esperar(1)

    # de lado, pelo menu
    for lugar, nome in ((ESQUERDA, "5-a-esquerda"), (DIREITA, "5-a-direita")):
        m.acoes_de_lugar[lugar].trigger()
        esperar(2)
        conferir(m.lugar == lugar and not tela.lugar_embaixo.isVisible()
                 and not tela.lugar_embaixo.isAncestorOf(tela.botao_processar),
                 f"Lugar > {lugar}: a coluna de miniaturas, e o processar na barra de baixo")
        foto(janela, nome, [no(m, janela), no(tela.botao_processar, janela)])
    clicar_no_icone(janela, tela, "props")
    esperar(2)
    foto(janela, "5-a-direita-com-o-painel")
    m.acao_em_pares.trigger()
    esperar(1.5)
    foto(janela, "5-a-direita-em-pares", [no(m, janela)])
    m.acao_em_pares.trigger()
    clique_nativo(janela, m.seta)
    esperar(1.5)
    conferir(not m.aberta and m.width() <= 30, "de lado e fechadas: uma faixa fininha")
    foto(janela, "5-a-direita-fechada", [no(m, janela)])
    clique_nativo(janela, m.seta)
    esperar(1)
    tela.paineis.fechar()
    esperar(1)

    # arrasto nativo pela alça: da direita para embaixo
    print("\n6. arrastar pela alça")
    hwnd = int(janela.winId())
    inicio = m.alca.mapTo(janela, m.alca.rect().center())
    alvo_ret = tela._retangulos_de_encaixe()[EMBAIXO]
    fim = tela.mapTo(janela, alvo_ret.center())
    user32.PostMessageW(hwnd, 0x0200, 0, _lparam(janela, inicio))
    esperar(0.2)
    user32.PostMessageW(hwnd, 0x0201, 1, _lparam(janela, inicio))
    esperar(0.2)
    for passo in range(1, 13):
        meio = QPoint(round(inicio.x() + (fim.x() - inicio.x()) * passo / 12),
                      round(inicio.y() + (fim.y() - inicio.y()) * passo / 12))
        user32.PostMessageW(hwnd, 0x0200, 1, _lparam(janela, meio))
        esperar(0.08)
    esperar(0.5)
    conferir(tela.lugares_de_encaixe.isVisible() and tela.lugares_de_encaixe.aceso == EMBAIXO,
             "arrastando: os três lugares aparecem, e o de baixo acende")
    foto(janela, "6-arrastando-a-alca")
    user32.PostMessageW(hwnd, 0x0202, 0, _lparam(janela, fim))
    esperar(2)
    conferir(m.lugar == EMBAIXO and not tela.lugares_de_encaixe.isVisible(),
             "soltou no lugar de baixo: as miniaturas foram para baixo")

    # ver todas
    print("\n7. Todas as páginas")
    clique_nativo(janela, m.botao_ver_todas)
    esperar(12)
    todas = tela.todas
    conferir(tela.pilha_da_tela.currentWidget() is todas and todas.vista == "uma",
             "clique nativo em 'ver todas' abriu Todas as páginas, uma a uma (901 A)")
    foto(janela, "7-todas-uma-a-uma")
    clique_nativo(janela, todas.botao_pares)
    esperar(2)
    foto(janela, "7-todas-em-pares")
    clique_nativo(janela, todas.botao_atencao)
    esperar(2)
    foto(janela, "7-todas-so-atencao")
    clique_nativo(janela, todas.botao_todas)
    clique_nativo(janela, todas.botao_uma)
    esperar(2)
    quadro = todas.quadros[2]
    clique_nativo(janela, quadro)
    esperar(4)
    conferir(tela.pilha_da_tela.currentWidget() is tela.trabalho and tela.indice_pagina == 2,
             f"clique nativo na página 3 voltou ao trabalho nela (página {tela.indice_pagina + 1})")
    janela.menu.acoes["todas_as_paginas"].trigger()
    esperar(2)
    conferir(tela.pilha_da_tela.currentWidget() is todas, "menu Ver > Todas as páginas abriu a grade")
    clique_nativo(janela, todas.botao_voltar)
    esperar(2)

    # Dividir: FOLHAS
    tela.trilha.escolher("dividir")
    esperar(4)
    tela.paineis.fechar()
    esperar(1)
    conferir(m.titulo.text() == "FOLHAS", "com o Dividir o cabeçalho diz FOLHAS")
    foto(janela, "8-dividir-folhas", [no(m.cabecalho, janela)])
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(3)

    # tamanhos e temas
    janela.resize(1000, 600)
    janela.move(-32000, -32000)
    esperar(3)
    foto(janela, "9-minima")
    m.acoes_de_lugar[ESQUERDA].trigger()
    esperar(2)
    foto(janela, "9-minima-a-esquerda")
    m.acoes_de_lugar[EMBAIXO].trigger()
    janela.resize(1280, 657)
    janela.move(-32000, -32000)
    esperar(2)
    for tema in ("escuro", "claro"):
        janela._trocar_tema(tema)
        esperar(1.5)
        foto(janela, f"9-{tema}")
    janela._trocar_tema("cinza")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
