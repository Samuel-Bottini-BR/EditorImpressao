"""Piloto curto (D-612): a frase "Área branca" do Mover na "Uma página" (sem passar pelos pares),
no Gradus, página 39: arrastar, Ctrl+Z, Ctrl+Y, puxar o canto. No piloto.py, nos pares, a frase
passou de 29,7 x 21,0 cm para 31,7 x 22,0 cm depois do Ctrl+Z/Ctrl+Y; aqui se vê se na "Uma
página" (o caminho que o conserto não mexe) é igual: se for, já era assim antes.

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_area.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
_spec = importlib.util.spec_from_file_location("piloto_d612", AQUI / "piloto.py")
piloto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(piloto)          # só define as funções (main fica de fora)
piloto.LOG = open(AQUI / "anotacoes-piloto-area.txt", "w", encoding="utf-8")
base = piloto.base


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
    piloto.ferramenta(j, "F")
    t.ir_para_pagina(38)
    piloto.esperar_previa(j)
    vis = piloto.vis_mover(j)

    def frase(nome):
        pg = j.projeto.paginas[t.indice_pagina]
        ultima = t.acoes.feitas[-1] if t.acoes and t.acoes.feitas else None
        piloto.anotar(nome, {"area": t.rotulo_area_branca.text(), "mostrar": t.mostrar,
                             "pagina": t.indice_pagina + 1, "paginas": len(j.projeto.paginas),
                             "desloc": [round(v, 4) for v in pg.conteudo_deslocamento],
                             "escala": round(pg.conteudo_escala, 3),
                             "feitas": len(t.acoes.feitas) if t.acoes else None,
                             "ultima": getattr(ultima, "descricao", str(ultima))[:90]})

    vis.conteudo_movido.connect(lambda r: piloto.anotar("  conteudo_movido", [round(v, 4) for v in r]))
    piloto.anotar("vis", {"visivel": vis.isVisible(), "pixmap": vis._pixmap is not None,
                          "carregando": vis.carregando, "modo": vis.modo,
                          "folha_do_mover": vis._folha_do_mover, "aba": t.aba_atual,
                          "pronta": t._pronta(), "foco": type(j.focusWidget()).__name__})
    frase("inicio")
    vis.grab()
    piloto.anotar("area-do-vis", [vis._area.x(), vis._area.y(), vis._area.width(), vis._area.height(),
                                  vis.width(), vis.height()])
    c = vis._area.center()
    base.arrastar(j, vis, c, c + QPoint(-int(vis._area.width() * 0.12), 0)); piloto.esperar_previa(j)
    frase("arrastou")
    piloto.ctrl(j, ord("Z")); piloto.esperar_previa(j); frase("ctrl-z")
    piloto.ctrl(j, ord("Y")); piloto.esperar_previa(j); frase("ctrl-y")
    vis.grab()
    canto = vis._alcas(vis._area_do_conteudo())["se"]
    base.arrastar(j, vis, canto, canto + QPoint(-30, -30)); piloto.esperar_previa(j)
    frase("canto")
    piloto.N[0] = 200
    piloto.p(j, "uma-pagina-area-branca")
    base.fechar(j)


main()
