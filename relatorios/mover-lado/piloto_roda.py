"""Piloto curto (D-612): Ctrl+roda nos pares, na janela de verdade, com a ferramenta Cortar
(como era antes) e com o Mover (a peça dele na página da vez). Anota a página da vez e o zoom
depois de cada volta, para comparar os dois. Usa as peças do piloto.py (sem rodar o main dele).

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_roda.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
_spec = importlib.util.spec_from_file_location("piloto_d612", AQUI / "piloto.py")
piloto = importlib.util.module_from_spec(_spec)
piloto.__dict__["__name__"] = "piloto_d612"
_spec.loader.exec_module(piloto)          # só define as funções (main fica de fora)
piloto.LOG = open(AQUI / "anotacoes-piloto-roda.txt", "w", encoding="utf-8")
base = piloto.base
piloto.N[0] = 100                          # os prints daqui: p101, p102 (não pisam nos do piloto)


def main():
    base.preparar(str(piloto.RAIZ), str(piloto.SCRATCH), limpar=False)
    import projetos
    pasta = piloto.preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(piloto.LARGURA, piloto.ALTURA)
    _p = piloto.Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    piloto.esperar_tela(j)
    t = j.tela_conferir
    pares = t.lado_a_lado
    original = pares.zoom_no_ponteiro

    def espiao(zoom, ponto):
        piloto.anotar("  zoom_no_ponteiro", {"ponto": [ponto.x(), ponto.y()], "atual": pares.atual,
                                             "barra": pares.verticalScrollBar().value()})
        original(zoom, ponto)
        piloto.anotar("  depois", {"atual": pares.atual, "barra": pares.verticalScrollBar().value()})
    pares.zoom_no_ponteiro = espiao
    from PySide6.QtCore import QEvent, QObject

    class Olho(QObject):
        def eventFilter(self, obj, ev):  # noqa: N802
            if ev.type() == QEvent.Wheel:
                piloto.anotar("  roda chegou", {"em": type(obj).__name__,
                                                "pos": [ev.position().x(), ev.position().y()],
                                                "global": [ev.globalPosition().x(), ev.globalPosition().y()],
                                                "obj_no_global": [obj.mapToGlobal(obj.rect().topLeft()).x(),
                                                                  obj.mapToGlobal(obj.rect().topLeft()).y()],
                                                "espontaneo": ev.spontaneous()})
            return False
    olho = Olho()
    t.visualizadores["mover"].installEventFilter(olho)
    pares.viewport().installEventFilter(olho)
    pares.pagina_da_vez_mudou.connect(lambda i: piloto.anotar("  pagina_da_vez_mudou", i + 1))
    for letra, nome in (("X", "cortar"), ("F", "mover")):
        piloto.ferramenta(j, letra)
        t.ir_para_pagina(38)
        piloto.mostrar(j, "duas")
        base.esperar(3)
        pares = t.lado_a_lado
        for volta in range(3):
            ret = next(r for i, r in pares.retangulos() if i == pares.atual)
            meio = pares.folhas.mapTo(pares, ret.center())
            piloto.roda_ctrl(j, pares, meio, 1)
            piloto.anotar(f"{nome}-volta-{volta + 1}", {"pagina": t.indice_pagina + 1,
                                                        "zoom": round(pares.zoom, 3),
                                                        "barra": pares.verticalScrollBar().value()})
        piloto.p(j, f"roda-{nome}")
        base.clique(j, t.botao_ajustar_a_tela); base.esperar(1)
        piloto.mostrar(j, "uma")
    base.fechar(j)


main()
