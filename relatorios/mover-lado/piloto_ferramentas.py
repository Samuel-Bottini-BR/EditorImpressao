"""Piloto da D-612, segunda parte (Samuel, 04/11/2026: "1- sim" para Cortar, Endireitar e marcar),
na janela de verdade, Gradus (cópia dos dados de teste), vista "Duas lado a lado". Mesmo jeito do
piloto.py (usa as peças dele, sem rodar o main dele).

Confere, com a mão (mensagens do Windows):
  1. Cortar nos pares: puxar a beirada da direita muda o corte; Ctrl+Z volta.
  2. Endireitar nos pares: desenhar a linha torta gira a página; Ctrl+Z volta.
  3. Retângulo nos pares: desenhar marca uma região; Ctrl+Z tira.
  4. Pincel nos pares: a roda muda a espessura; Ctrl+roda dá zoom no par.
  5. Mão nos pares: os pares de sempre (sem o editor por cima).
  6. "Uma página": cada ferramenta no lugar de sempre.

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_ferramentas.py
"""
from __future__ import annotations

import ctypes
import importlib.util
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
_spec = importlib.util.spec_from_file_location("piloto_d612", AQUI / "piloto.py")
piloto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(piloto)          # só define as funções (main fica de fora)
piloto.LOG = open(AQUI / "anotacoes-piloto-ferramentas.txt", "w", encoding="utf-8")
piloto.N[0] = 300                          # prints p301...
base = piloto.base


def esperar_pixmap(peca, limite=60):
    t = time.time()
    base.esperar(0.5)
    while time.time() - t < limite and (peca._pixmap is None or getattr(peca, "carregando", False)):
        base.esperar(0.2)
    base.esperar(0.8)
    peca.grab()


def roda(j, widget, ponto, ctrl=False):
    h = int(j.winId())
    alvo = widget.mapToGlobal(ponto)
    e = j.devicePixelRatioF()
    x, y = round(alvo.x() * e), round(alvo.y() * e)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[0x11] = 0x80 if ctrl else 0
    base.user32.SetKeyboardState(est)
    wp = ((120 & 0xFFFF) << 16) | (0x0008 if ctrl else 0)
    base.user32.PostMessageW(h, 0x020A, wp, lp); base.esperar(0.4)
    est[0x11] = 0
    base.user32.SetKeyboardState(est)
    base.esperar(0.8)


def main():
    from PySide6.QtCore import QPoint

    base.preparar(str(piloto.RAIZ), str(piloto.SCRATCH), limpar=False)
    import projetos
    pasta = piloto.preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(piloto.LARGURA, piloto.ALTURA)
    _p = piloto.Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    piloto.esperar_tela(j)
    t = j.tela_conferir
    pr = j.projeto
    pares = t.lado_a_lado
    t.ir_para_pagina(38)                  # página 39 (a da direita do par 38-39)

    def nos_pares(peca):
        return pares.isAncestorOf(peca) and peca.isVisible()

    # 1. Cortar
    piloto.na_trilha(j, "cortar"); piloto.mostrar(j, "duas")
    vis = t.visualizadores["bordas"]
    esperar_pixmap(vis)
    pg = pr.paginas[t.indice_pagina]
    base.conferir(t.vista_da_pagina.currentWidget() is pares and nos_pares(vis),
                  "Cortar em Duas lado a lado: a página da vez é o Cortar, a vista nos pares")
    piloto.p(j, "cortar-nos-pares")
    antes = tuple(pg.recorte or (0, 0, 1, 1))
    de = vis._alcas(vis._retangulo_recorte())["l"]
    base.arrastar(j, vis, de, de + QPoint(-40, 0)); esperar_pixmap(vis)
    depois = tuple(pg.recorte or (0, 0, 1, 1))
    piloto.anotar("cortar", {"antes": antes, "depois": depois})
    base.conferir(depois[2] < antes[2] - 0.02, f"Cortar nos pares: puxar a beirada muda o corte "
                  f"({antes[2]:.3f} -> {depois[2]:.3f})")
    piloto.p(j, "cortar-puxou-a-beirada")
    piloto.ctrl(j, ord("Z")); esperar_pixmap(vis)
    base.conferir(tuple(pg.recorte or (0, 0, 1, 1)) == antes, "Ctrl+Z desfaz o corte nos pares")

    # 2. Endireitar
    piloto.na_trilha(j, "endireitar")
    vis = t.visualizadores["angulo"]
    esperar_pixmap(vis)
    base.conferir(t.vista_da_pagina.currentWidget() is pares and nos_pares(vis),
                  "Endireitar em Duas lado a lado: a página da vez é o Endireitar")
    antes = pg.angulo_manual
    a = vis._area
    de = QPoint(a.left() + int(a.width() * 0.2), a.center().y())
    base.arrastar(j, vis, de, de + QPoint(int(a.width() * 0.6), -int(a.width() * 0.6 * 0.05)))
    esperar_pixmap(vis)
    piloto.anotar("endireitar", {"antes": antes, "depois": pg.angulo_manual})
    base.conferir(pg.angulo_manual is not None and pg.angulo_manual != antes,
                  f"Endireitar nos pares: a linha torta gira a página ({antes} -> {pg.angulo_manual})")
    piloto.p(j, "endireitar-nos-pares")
    piloto.ctrl(j, ord("Z")); esperar_pixmap(vis)
    base.conferir(pg.angulo_manual == antes, "Ctrl+Z desfaz o giro nos pares")

    # 3. Retângulo
    t.escolher_ferramenta("retangulo")     # (o mesmo da trilha e da letra)
    base.esperar(1.5)
    ed = t.editor_selecao
    esperar_pixmap(ed)
    base.conferir(t.vista_da_pagina.currentWidget() is pares and nos_pares(ed),
                  "Retângulo em Duas lado a lado: a página da vez é o editor de marcar")
    antes = len(ed.selecao.regioes)
    a = ed._calcular_area()
    de = QPoint(a.left() + int(a.width() * 0.3), a.top() + int(a.height() * 0.3))
    base.arrastar(j, ed, de, de + QPoint(80, 80)); base.esperar(1.5)
    piloto.anotar("retangulo", {"antes": antes, "depois": len(ed.selecao.regioes)})
    base.conferir(len(ed.selecao.regioes) == antes + 1, "Retângulo nos pares: marca uma região")
    piloto.p(j, "retangulo-nos-pares")
    piloto.ctrl(j, ord("Z")); base.esperar(1.5)
    base.conferir(len(ed.selecao.regioes) == antes, "Ctrl+Z tira a marcação nos pares")

    # 4. Pincel: a roda é dele; Ctrl+roda é do par
    t.escolher_ferramenta("pincel"); base.esperar(1.5)
    ed.grab()
    espessura = ed.espessura
    roda(j, ed, ed._calcular_area().center())
    base.conferir(ed.espessura > espessura and abs(pares.zoom - 1.0) < 1e-6,
                  "Pincel nos pares: a roda muda a espessura")
    roda(j, ed, ed._calcular_area().center(), ctrl=True)
    base.conferir(pares.zoom > 1.1 and abs(ed.zoom - 1.0) < 1e-6 and t.indice_pagina == 38,
                  "Pincel nos pares: Ctrl+roda dá zoom no par, na mesma página")
    piloto.p(j, "pincel-ctrl-roda-nos-pares")
    base.clique(j, t.botao_ajustar_a_tela); base.esperar(1)

    # 5. Mão: os pares de sempre
    t.escolher_ferramenta("mao"); base.esperar(1.5)
    base.conferir(t.vista_da_pagina.currentWidget() is pares and not pares.isAncestorOf(ed),
                  "Mão em Duas lado a lado: os pares de sempre (sem o editor por cima)")
    piloto.p(j, "mao-nos-pares")

    # 6. Uma página
    piloto.mostrar(j, "uma")
    for ferr, peca in (("retangulo", ed), ("cortar", t.visualizadores["bordas"]),
                       ("endireitar", t.visualizadores["angulo"])):
        t.escolher_ferramenta(ferr); base.esperar(1.5)
        base.conferir(t.vista_da_pagina.currentWidget() is t.area_imagem and not pares.isAncestorOf(peca)
                      and peca.isVisible(), f"Uma página: {ferr} no lugar de sempre")
    piloto.p(j, "uma-pagina-endireitar")

    base.gravar_resultados(AQUI / "ferramentas")
    base.fechar(j)


main()
