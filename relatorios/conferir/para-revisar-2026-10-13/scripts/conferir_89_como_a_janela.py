"""MAQUINA: as 89 paginas do estudo medidas COMO A JANELA MEDE.

O implementador conferiu a regra desenhando cada pagina direto na resolucao do
PDF (300 DPI). Na janela nunca e assim: a previa da tela (110 DPI) e desenhada
ANTES, no mesmo projeto, e so depois vem a medida a 300 DPI. Na conferencia vi
que isso muda o aviso em algumas paginas (Graduale 221: direto nao tem aviso;
depois da previa, "Desenho apagado"). Este script repete as 89 paginas na ordem
da janela (previa 110, depois 300) e compara com o gabarito do estudo e com o
resultado do implementador (conferir-89-programa-dpi300.json).

Igual ao conferir_89.py --programa: livro novo (endireitar antes de cortar),
"So as letras" de fabrica, forca do preto sozinha DESLIGADA (a regra pura), a
faixa contada por livro entre as 89. Nao muda o programa; pasta de dados isolada.
Grava conferir-89-como-a-janela.json ao lado dos outros resultados desta conferencia.
"""
import gc
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
RAIZ = BASE.parents[2]
IMPL = RAIZ / "relatorios" / "para-revisar-impl"
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(IMPL))

from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

isolar_pasta_de_dados("verif-para-revisar-89")

import conferir_89  # noqa: E402
from core import analise, misto, revisar  # noqa: E402
from core import pipeline as P  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

SAIDA = BASE / "conferir-89-como-a-janela.json"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gab = conferir_89._gabarito()
    feitas = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {}
    pids = sorted({b.split("__")[0] for b in gab})
    t_total = time.perf_counter()
    for pid in pids:
        if any(b.split("__")[0] == pid for b in feitas):
            continue
        projeto = Projeto(caminho_entrada=str(conferir_89._pdf_da_pagina(pid)), nome=pid)
        projeto.filtro_padrao = PRETO_E_BRANCO
        projeto = P.analisar_projeto(projeto)
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            if pid.startswith("siebmacher") and not projeto.folhas[0].dividir:
                conferir_89._dividir_a_mao(doc, projeto, PRETO_E_BRANCO)
            projeto.misto_so_as_letras = True
            projeto.misto_fora_do_texto = misto.FORA_REDE
            projeto.reforcar_texto_falhado = False
            for pagina in projeto.paginas:
                pagina.filtro = PRETO_E_BRANCO
                P.renderizar_pagina(doc, projeto, pagina, dpi=110)       # a previa da tela, primeiro
                t1 = time.perf_counter()
                P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)   # a medida, depois
                feitas[f"{pid}__{pagina.metade}"] = {
                    "alertas": list(pagina.alertas), "faixa_na_beirada": pagina.faixa_na_beirada,
                    "segundos_da_medida": round(time.perf_counter() - t1, 1)}
        finally:
            doc.close()
            del projeto
            gc.collect()
        SAIDA.write_text(json.dumps(feitas, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"medi em {time.perf_counter() - t_total:.0f} s", flush=True)

    def decide(resultados):
        por_livro = {}
        for base in gab:
            por_livro.setdefault(conferir_89._livro(base), []).append(bool(resultados[base]["faixa_na_beirada"]))
        faixa = {livro: revisar.faixa_no_livro(v) for livro, v in por_livro.items()}
        vai, motivos = {}, {}
        for base in gab:
            avisos = [a for a in resultados[base]["alertas"] if a in analise.AVISOS_DO_SO_AS_LETRAS]
            if faixa[conferir_89._livro(base)]:
                avisos = [a for a in avisos if a != analise.FAIXA_NA_BEIRADA]
            vai[base], motivos[base] = bool(avisos), avisos
        return vai, motivos, sorted(l for l, v in faixa.items() if v)

    falta = [b for b in gab if b not in feitas]
    if falta:
        print("faltam", falta)
        return 2
    vai_j, mot_j, faixa_j = decide(feitas)
    do_impl = json.loads((IMPL / "conferir-89-programa-dpi300.json").read_text(encoding="utf-8"))
    vai_i, mot_i, faixa_i = decide(do_impl)
    for nome, vai in (("implementador (direto a 300)", vai_i), ("como a janela (previa 110, depois 300)", vai_j)):
        vao = sum(vai.values())
        certas = sum(1 for b in gab if vai[b] == gab[b]["gabarito"])
        escapam = [b for b in sorted(gab) if gab[b]["gabarito"] and not vai[b]]
        sobram = [b for b in sorted(gab) if vai[b] and not gab[b]["gabarito"]]
        print(f"{nome}: vao {vao}; certas {certas} de {len(gab)}; escapam {len(escapam)}; vao sem precisar {len(sobram)}")
        print("   escapam:", escapam)
        print("   vao sem precisar:", sobram)
    print("faixa do livro (implementador):", faixa_i, "| (como a janela):", faixa_j)
    print("PAGINAS EM QUE A DECISAO OU O MOTIVO MUDA:")
    for b in sorted(gab):
        if vai_i[b] != vai_j[b] or sorted(mot_i[b]) != sorted(mot_j[b]):
            print(f"   {b}: gabarito {'vai' if gab[b]['gabarito'] else 'nao vai'} | direto: {mot_i[b] or '-'} | como a janela: {mot_j[b] or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
