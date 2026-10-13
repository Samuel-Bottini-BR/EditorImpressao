"""SEGUNDA CONFERENCIA: o que o teste de velocidade nao mede.

Na JANELA DE VERDADE, com "So as letras" ligado, folheia o Antiphonal 1547 (298
folhas, livro novo, pasta de dados nova a cada rodada) clicando no botao ">" e
mede: (a) quanto a previa da pagina nova demora, parando 1,5 s em cada pagina;
(b) o mesmo sem parar; (c) quanto tempo o programa continua trabalhando por
tras depois de parar de folhear. Roda no codigo que VERIF_RAIZ apontar (o
programa de hoje ou o ramo). Grava trabalho/folhear/<rotulo>.json.

Uso: q4_folhear.py <rotulo>     (VERIF_RAIZ e VERIF_DADOS vem do ambiente)
A medida e por perguntas ao programa (uns 0,05 s cada): nao enxerga menos que isso.
"""
import json, statistics, sys, time
import v
from livros import LIVROS
P = v.P
rotulo = sys.argv[1]
v.fechar(); v.abrir()
abriu = v.novo_livro(LIVROS["antiphonal"])
v.esperar_medida(120) if "verif-para-revisar" in P.VERIF_RAIZ else time.sleep(8)
o0 = v.esperar_ocioso(300)
so_letras = v.s("tc.projeto.misto_so_as_letras")
com, resto_com = v.folhear(12, 1.5)
sem, resto_sem = v.folhear(12, 0)
pagina = v.s("tc.indice_pagina+1")
dados = {"rotulo": rotulo, "codigo": P.VERIF_RAIZ, "abriu_s": abriu, "so_as_letras": so_letras,
         "parando_1_5s": com, "resto_depois_de_parar_s": resto_com,
         "sem_parar": sem, "resto_depois_sem_parar_s": resto_sem, "pagina_final": pagina,
         "erros_log": v.erros_log()[-300:]}
pasta = P.BASE / "trabalho" / "folhear"; pasta.mkdir(parents=True, exist_ok=True)
(pasta / f"{rotulo}.json").write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
m = lambda xs: f"media {statistics.mean(xs):.2f} s, do meio {statistics.median(xs):.2f} s, pior {max(xs):.2f} s"
print(f"{rotulo} (So as letras: {so_letras}; abriu em {abriu} s; ocioso {o0} s depois)")
print("  parando 1,5 s:", m(com), "| por tras depois de parar:", resto_com, "s")
print("  sem parar:    ", m(sem), "| por tras depois de parar:", resto_sem, "s", "| pagina final", pagina)
v.fechar()
