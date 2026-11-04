"""Piloto dos consertos do teste do Samuel de 04/11/2026 (prints a-74 a a-78), na janela de verdade,
Gradus (cópia dos dados de teste). Usa as peças do piloto.py (sem rodar o main dele).

  A. Dividir em "Duas lado a lado": clicar na miniatura de uma metade → a folha na tela e as DUAS
     miniaturas dela marcadas (a-75/a-76).
  (a) Mover nos pares: o mesmo aperto na outra página a escolhe e já arrasta.
  C. D-622: clicar no cinza larga a escolha (cantos e quadro somem); clicar na página volta. Nos
     pares e em "Uma página".
  B. "antes / depois" com o Mover numa página em Original, a 131% (a-77/a-78): compara, sem o aviso;
     o "depois" com o Mover, o "antes" como veio. E o Cortar.

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_consertos.py
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
_spec = importlib.util.spec_from_file_location("piloto_d612", AQUI / "piloto.py")
piloto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(piloto)          # só define as funções (main fica de fora)
piloto.LOG = open(AQUI / "anotacoes-piloto-consertos.txt", "w", encoding="utf-8")
piloto.N[0] = 500                          # prints p501...
base = piloto.base


def marcadas(t):
    return [i for i, m in enumerate(t.tira._miniaturas) if m.selecionada]


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
    piloto.anotar("livro", {"folhas": len(pr.folhas), "paginas": len(pr.paginas),
                            "divididas": sum(1 for f in pr.folhas if f.dividir)})

    # A. Dividir em Duas lado a lado (o livro dividido, como nos prints a-75/a-76)
    piloto.ferramenta(j, "D")
    if not any(f.dividir for f in pr.folhas):
        base.clique(j, t.botao_dividir_todas)
        fim = time.time() + 600
        while time.time() < fim and not all(f.dividir for f in pr.folhas[1:]):
            base.esperar(0.5)
        base.esperar(3)
        piloto.anotar("dividiu", {"divididas": sum(1 for f in pr.folhas if f.dividir),
                                  "paginas": len(pr.paginas)})
    piloto.mostrar(j, "duas"); base.esperar(2)
    grupos = {}
    for i in range(len(t.tira._miniaturas)):
        linha, coluna = t.tira.posicao(i)
        grupos.setdefault((linha, coluna // 3), []).append(i)
    pares_da_tira = sorted(grupos.values())[:8]
    piloto.anotar("A-pares-da-tira", [[i + 1 for i in g] for g in pares_da_tira])
    passos = t._passos_do_dividir()
    pela_folha = all(len({pr.paginas[passos[i]].folha for i in g}) == 1 for g in pares_da_tira)
    base.conferir(pela_folha, "Dividir/Duas lado a lado: a tira junta as duas páginas da mesma folha")
    for item in (10, 9):                      # as miniaturas "11" e "10" dos prints a-75/a-76
        mini = t.tira._miniaturas[item]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(2)
        folha = t.indice_folha
        da_folha = [i for i, p in enumerate(t._passos_do_dividir()) if pr.paginas[p].folha == folha]
        piloto.anotar(f"A-miniatura-{item + 1}", {"folha": folha + 1, "marcadas": [i + 1 for i in marcadas(t)],
                                                  "da_folha": [i + 1 for i in da_folha]})
        base.conferir(marcadas(t) == [item] and item in da_folha,
                      f"Dividir/Duas lado a lado: clique na miniatura {item + 1} → folha {folha + 1}, "
                      f"marcada {[i + 1 for i in marcadas(t)]} (a folha: {[i + 1 for i in da_folha]})")
        piloto.p(j, f"A-dividir-miniatura-{item + 1}")

    # (a) Mover nos pares: o mesmo aperto escolhe e arrasta
    piloto.ferramenta(j, "F"); piloto.esperar_previa(j); base.esperar(1)
    pares = t.lado_a_lado
    vis = piloto.vis_mover(j)
    da_vez = pares.atual
    outra = next(i for i, r in pares.retangulos() if i != da_vez and pares._linha_de(i) == pares._linha_de(da_vez))
    ret = next(r for i, r in pares.retangulos() if i == outra)
    indice_outra = pares.indices[outra]
    pg = pr.paginas[indice_outra]
    antes = tuple(pg.conteudo_deslocamento)
    centro = pares.folhas.mapTo(pares, ret.center())
    base.arrastar(j, pares, centro, centro + QPoint(40, 0)); piloto.esperar_previa(j)
    piloto.anotar("a-outra-pagina", {"pagina": t.indice_pagina + 1, "esperada": indice_outra + 1,
                                     "antes": antes, "depois": tuple(pg.conteudo_deslocamento)})
    base.conferir(t.indice_pagina == indice_outra and pg.conteudo_deslocamento[0] > antes[0] + 0.02,
                  "pares: o mesmo aperto na outra página escolhe e já arrasta")
    piloto.p(j, "a-outra-pagina-escolhe-e-arrasta")
    piloto.ctrl(j, ord("Z")); piloto.esperar_previa(j)

    # C. clicar no cinza dos pares
    lugar = next(r for i, r in pares.retangulos() if i == pares.atual)
    lugar = lugar.translated(pares.folhas.mapTo(pares, QPoint(0, 0)))
    fora = QPoint(max(4, min(lugar.left(), pares.width() - lugar.right()) // 2) if lugar.left() > 20
                  else pares.width() - 10, lugar.center().y())
    base.clique(j, pares, fora); base.esperar(1)
    base.conferir(pares.sem_escolha and not vis.conteudo_escolhido,
                  "pares: clique no cinza larga a escolha (sem quadro, sem cantos)")
    piloto.p(j, "C-pares-clique-fora")
    base.clique(j, pares, lugar.center() + QPoint(0, -lugar.height() // 4)); base.esperar(1)
    base.conferir(not pares.sem_escolha and vis.conteudo_escolhido, "pares: clique na página escolhe de novo")
    piloto.p(j, "C-pares-clique-na-pagina")

    # C. Uma página
    piloto.mostrar(j, "uma"); piloto.esperar_previa(j)
    vis.grab()
    fora = QPoint(max(4, vis._area.left() // 2), vis._area.center().y())
    base.clique(j, vis, fora); base.esperar(1)
    base.conferir(not vis.conteudo_escolhido, "Uma página: clique no cinza larga (sem cantos)")
    piloto.p(j, "C-uma-pagina-clique-fora")
    base.clique(j, vis, vis._area.center()); base.esperar(1)
    base.conferir(vis.conteudo_escolhido, "Uma página: clique na página escolhe de novo")

    # B. antes / depois com o Mover, página em Original, a 131%
    pagina = pr.paginas[t.indice_pagina]
    piloto.anotar("B-filtro", pagina.filtro)
    base.clique(j, t.campo_tamanho_do_conteudo)
    base.tecla(j, 0x23); base.tecla(j, 0x08, vezes=4); base.digitar(j, "131"); piloto.esperar_previa(j)
    foco = j.focusWidget()
    if foco is t.campo_tamanho_do_conteudo:
        foco.clearFocus()
    base.clique(j, t.botao_antes_depois); base.esperar(1)
    vista = t.vista_antes_depois
    fim = time.time() + 60
    while time.time() < fim and (vista.depois is None or vista.antes is None):
        base.esperar(0.3)
    base.esperar(1.5)
    piloto.anotar("B-antes-depois", {"comparando": vista.comparando, "aviso": vista.aviso,
                                     "antes": vista.antes is not None, "depois": vista.depois is not None,
                                     "rotulos": vista.rotulos})
    base.conferir(vista.comparando and vista.aviso == "" and vista.antes is not None,
                  "antes / depois do Mover em Original: compara, sem o aviso")
    piloto.p(j, "B-mover-131-antes-depois")
    piloto.na_trilha(j, "cortar"); base.esperar(3)
    base.conferir(vista.comparando and vista.aviso == "", "antes / depois do Cortar: compara")
    piloto.p(j, "B-cortar-antes-depois")
    base.clique(j, t.botao_antes_depois); base.esperar(1)

    base.gravar_resultados(AQUI / "consertos")
    base.fechar(j)


main()
