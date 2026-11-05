"""Piloto da D-612, terceira parte ("Ok, pode ser assim o antes e depois": as ferramentas mexem no
"depois", o "antes" fica parado) e do bug de 04/11 (print a-65: o "tamanho" de cima acompanha o
pincel), na janela de verdade, Gradus (cópia dos dados de teste). Usa as peças do piloto.py.

Confere, com a mão (mensagens do Windows):
  1. Mover com "antes / depois": arrastar no "depois" (à esquerda da linha) move; no "antes" nada.
  2. A linha azul continua se arrastando; o pedaço da ferramenta acompanha.
  3. Cortar: puxar a beirada da esquerda (no "depois") muda o corte; Ctrl+Z volta.
  4. Endireitar: a linha torta no "depois" gira a página; Ctrl+Z volta.
  5. Retângulo: marcar no "depois"; Ctrl+Z tira.
  6. Desligar o "antes / depois": "Uma página" de sempre.
  7. Pincel: a roda muda o pincel e o "tamanho" de cima acompanha; o "tamanho" muda o pincel e o
     número do painel.

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_antes_depois.py
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
piloto.LOG = open(AQUI / "anotacoes-piloto-antes-depois.txt", "w", encoding="utf-8")
piloto.N[0] = 400                          # prints p401...
base = piloto.base


def esperar_vista(t, limite=60):
    vista = t.vista_antes_depois
    fim = time.time() + limite
    while time.time() < fim and (vista.depois is None or vista.antes is None):
        base.esperar(0.3)
    base.esperar(1.0)
    return vista


def ponto(vista, fx, fy=0.5):
    from PySide6.QtCore import QPoint
    a = vista._area(vista.depois)
    return QPoint(int(a.left() + fx * a.width()), int(a.top() + fy * a.height()))


def roda(j, widget, p, vezes=1):
    h = int(j.winId())
    alvo = widget.mapToGlobal(p)
    e = j.devicePixelRatioF()
    x, y = round(alvo.x() * e), round(alvo.y() * e)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    for _ in range(vezes):
        base.user32.PostMessageW(h, 0x020A, (120 & 0xFFFF) << 16, lp); base.esperar(0.2)
    base.esperar(0.8)


def main():
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QSlider

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
    t.ir_para_pagina(38)                       # página 39
    t._escolher_filtro("preto_e_branco")       # o "antes / depois" compara com o Original
    pg = pr.paginas[38]

    # 1. Mover
    piloto.ferramenta(j, "F"); piloto.esperar_previa(j)
    base.clique(j, t.botao_antes_depois); vista = esperar_vista(t)
    vis = t.visualizadores["mover"]
    base.conferir(t.comparando and t.vista_da_pagina.currentWidget() is vista and vista.isAncestorOf(vis),
                  "Mover com antes / depois: o Mover no lado do depois")
    piloto.p(j, "mover-antes-depois")
    antes = tuple(pg.conteudo_deslocamento)
    de = ponto(vista, 0.25)
    base.arrastar(j, vista, de, de + QPoint(-40, 0)); esperar_vista(t)
    base.conferir(pg.conteudo_deslocamento[0] < antes[0] - 0.02,
                  f"arrastar no depois move ({antes} -> {tuple(pg.conteudo_deslocamento)})")
    piloto.p(j, "mover-arrastou-no-depois")
    feito = tuple(pg.conteudo_deslocamento)
    de = ponto(vista, 0.8)
    base.arrastar(j, vista, de, de + QPoint(-40, 20)); esperar_vista(t)
    base.conferir(tuple(pg.conteudo_deslocamento) == feito, "arrastar no antes não mexe em nada")
    # 2. a linha
    de = ponto(vista, vista.posicao)
    base.arrastar(j, vista, de, de + QPoint(int(vista._area(vista.depois).width() * 0.25), 0))
    base.conferir(vista.posicao > 0.65, f"a linha continua se arrastando (posição {vista.posicao:.2f})")
    piloto.p(j, "linha-arrastada")
    piloto.ctrl(j, ord("Z")); esperar_vista(t)
    base.conferir(tuple(pg.conteudo_deslocamento) == antes, "Ctrl+Z desfaz o arrasto do Mover")

    # 3. Cortar
    piloto.na_trilha(j, "cortar"); esperar_vista(t)
    vis = t.visualizadores["bordas"]
    base.conferir(vista.isAncestorOf(vis), "Cortar com antes / depois: o Cortar no lado do depois")
    vis.grab()
    antes = tuple(pg.recorte or (0, 0, 1, 1))
    de = vis._alcas(vis._retangulo_recorte())["o"]
    base.arrastar(j, vis, de, de + QPoint(40, 0)); esperar_vista(t)
    depois = tuple(pg.recorte or (0, 0, 1, 1))
    base.conferir(depois[0] > antes[0] + 0.02, f"Cortar no depois: a beirada anda ({antes[0]:.3f} -> {depois[0]:.3f})")
    piloto.p(j, "cortar-no-depois")
    piloto.ctrl(j, ord("Z")); esperar_vista(t)
    base.conferir(tuple(pg.recorte or (0, 0, 1, 1)) == antes, "Ctrl+Z desfaz o corte")

    # 4. Endireitar
    piloto.na_trilha(j, "endireitar"); esperar_vista(t)
    vis = t.visualizadores["angulo"]
    base.conferir(vista.isAncestorOf(vis), "Endireitar com antes / depois: no lado do depois")
    antes = pg.angulo_manual
    de = ponto(vista, 0.05)
    largura = int(vista._area(vista.depois).width() * 0.4)
    base.arrastar(j, vista, de, de + QPoint(largura, -int(largura * 0.06))); esperar_vista(t)
    base.conferir(pg.angulo_manual is not None and pg.angulo_manual != antes,
                  f"Endireitar no depois: a linha torta gira ({antes} -> {pg.angulo_manual})")
    piloto.p(j, "endireitar-no-depois")
    piloto.ctrl(j, ord("Z")); esperar_vista(t)
    base.conferir(pg.angulo_manual == antes, "Ctrl+Z desfaz o giro")

    # 5. Retângulo
    t.escolher_ferramenta("retangulo"); esperar_vista(t)
    ed = t.editor_selecao
    base.conferir(vista.isAncestorOf(ed), "Retângulo com antes / depois: no lado do depois")
    antes = len(ed.selecao.regioes)
    de = ponto(vista, 0.1, 0.3)
    base.arrastar(j, vista, de, de + QPoint(60, 60)); base.esperar(1.5)
    base.conferir(len(ed.selecao.regioes) == antes + 1, "Retângulo no depois: marca uma região")
    piloto.p(j, "retangulo-no-depois")
    piloto.ctrl(j, ord("Z")); base.esperar(1.5)

    # 6. desligar
    base.clique(j, t.botao_antes_depois); base.esperar(1.5)
    base.conferir(t.vista_da_pagina.currentWidget() is t.area_imagem and t.paginas_de_imagem["marcar"].isAncestorOf(ed)
                  and ed.isVisible() and ed.mask().isEmpty(),
                  "antes / depois desligado: Uma página de sempre")

    # 7. Pincel
    t.escolher_ferramenta("pincel"); base.esperar(1.5)
    barra = t.barra_opcoes
    deslizante = next(s for s in barra.findChildren(QSlider) if s.isVisibleTo(barra))
    roda(j, ed, ed.rect().center(), 4)
    piloto.anotar("pincel-roda", {"espessura": ed.espessura, "tamanho_de_cima": deslizante.value(),
                                  "painel": t.aviso_marcacao.text()})
    base.conferir(deslizante.value() == round(ed.espessura * 1000) and ed.espessura > 0.025,
                  f"Pincel: a roda muda o pincel e o tamanho de cima acompanha ({deslizante.value()})")
    piloto.p(j, "pincel-roda-tamanho-de-cima")
    meio = deslizante.rect().center()
    base.clique(j, deslizante, QPoint(deslizante.width() - 6, meio.y())); base.esperar(1)
    piloto.anotar("pincel-tamanho", {"espessura": ed.espessura, "tamanho_de_cima": deslizante.value(),
                                     "painel": t.aviso_marcacao.text()})
    base.conferir(abs(ed.espessura - deslizante.value() / 1000) < 1e-9
                  and f"{ed.espessura * 100:.1f}%" in t.aviso_marcacao.text(),
                  "Pincel: mexer no tamanho de cima muda o pincel e o número do painel")
    piloto.p(j, "pincel-tamanho-de-cima")

    base.gravar_resultados(AQUI / "antes-depois")
    base.fechar(j)


main()
