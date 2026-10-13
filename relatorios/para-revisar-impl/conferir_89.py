"""Confere a regra ajustada do "Para revisar" nas 89 paginas do estudo.

O criterio de aceite (Samuel, rodada 4, `rv4-resumo`: "Fica assim"): nas 89
paginas, o aviso de antes mandava 55 e acertava 52; a regra ajustada tem de
mandar 21 e acertar 78. O gabarito (o que deveria acontecer em cada pagina) e
o do estudo: <TRABALHO>/regra4.json, gravado por
relatorios/revisar-decisoes/rodada-4/scripts/regra4.py.

Dois jeitos de conferir, do mais leve para o mais pesado:

  python conferir_89.py
      SEM rodar o programa: le as mascaras que o estudo gravou de cada pagina
      (<TRABALHO>/dados4/*.npz: o cinza, a tinta de base, as linhas, a gravura,
      o resultado) e passa pela conta do programa (core.revisar.medir). Prova
      que a conta do programa e a do estudo. Uns minutos; uma pagina por vez
      na memoria (ate ~600 MB na maior, de 38 milhoes de pontos).

  python conferir_89.py --programa [--dpi 300] [pid,pid,...]
      Roda o PROGRAMA de verdade (analise + desenho da pagina no "Só as
      letras" de fabrica, como a previa e o PDF fazem) e le os avisos que ele
      pos. --dpi 300 e a resolucao do PDF (a do estudo); --dpi 110 e a da
      previa da tela. Pesado (o leitor de texto roda em cada pagina): uma
      rodada por vez, com pelo menos 3 GB livres. Pula as paginas ja feitas
      (apague o conferir-89-programa-dpiN.json para refazer). A "forca do
      preto sozinha" fica desligada (a regra pura, como no estudo).
      --preparo-do-estudo: prepara a pagina como o programa de 07/10 (corta
      antes de endireitar, conta do endireitar do programa).
      --completo: mede sem os atalhos de tempo e guarda tambem as "guardas" de
      cada linha (para reacertar_limites.py); grava em ...-completo.json.

      ACHADO de 12/10/2026: a 110 DPI a regra NAO vale (24 vao, 67 certas, 13
      paginas decidem diferente do estudo; o texto falhado da falso em varias
      paginas e a letra T do Antiphonal 46 nao e vista - a pagina tem 396
      pontos de altura na previa). Por isso o programa so mede no desenho
      feito na resolucao do PDF (core.pipeline._da_para_medir).

Nada aqui muda o programa, o acervo, o gabarito nem a pasta do estudo (tudo
so e lido). A pasta de dados do programa e isolada
(pasta_de_dados_dos_scripts): nada vai para a pasta de verdade do Samuel.
Os resultados ficam ao lado deste arquivo (conferir-89-*.json).

Faixa na beirada: como no estudo, o "livro" de cada pagina sao as paginas
do mesmo livro entre as 89; a faixa em 70% ou mais delas vira aviso do livro
e nao manda a pagina.
"""

from __future__ import annotations

import gc
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]                      # a copia do projeto em que este arquivo esta
TRABALHO = Path(os.environ.get(
    "REVISAR_TRABALHO", r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho"))
DADOS = TRABALHO / "dados4"
PAGINAS = TRABALHO / "paginas"

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

ESPERADO_HOJE = (55, 52)        # (vao, acertam) do aviso de antes
ESPERADO_AJUSTADA = (21, 78)    # (vao, acertam) da regra ajustada


def _gabarito() -> dict:
    return json.loads((TRABALHO / "regra4.json").read_text(encoding="utf-8"))


def _livro(base: str) -> str:
    return base.split("_p")[0]


def _contas(nome: str, vai: dict[str, bool], gab: dict) -> tuple[int, int]:
    bases = sorted(gab)
    vao = sum(1 for b in bases if vai[b])
    certas = sum(1 for b in bases if vai[b] == gab[b]["gabarito"])
    escapam = [b for b in bases if gab[b]["gabarito"] and not vai[b]]
    sobram = [b for b in bases if vai[b] and not gab[b]["gabarito"]]
    print(f"{nome}: vao {vao} de {len(bases)}; acertam {certas}; escapam {len(escapam)} "
          f"{escapam}; vao sem precisar {len(sobram)} {sobram}", flush=True)
    return vao, certas


def _motivos_com_a_faixa_do_livro(sinais_por_base: dict) -> tuple[dict, dict]:
    """(motivos por pagina, faixa do livro por livro), com a faixa contada por
    livro como no estudo."""
    from core import revisar

    por_livro: dict[str, list[bool]] = {}
    for base, s in sinais_por_base.items():
        por_livro.setdefault(_livro(base), []).append(s.faixa_na_beirada)
    faixa = {livro: revisar.faixa_no_livro(v) for livro, v in por_livro.items()}
    motivos = {base: revisar.motivos(s, True, 0.0, faixa[_livro(base)])
               for base, s in sinais_por_base.items()}
    return motivos, faixa


def _resumo(s) -> dict:
    return {"apagado_a": round(s.apagado_a, 4), "apagado_junto": round(s.apagado_junto, 4),
            "maior_pedaco": round(s.maior_pedaco, 4),
            "vazou_da_gravura": round(s.vazou_da_gravura, 4), "beirada_a": round(s.beirada_a, 4),
            "falhadas": s.falhadas, "linhas_contadas": s.linhas_contadas,
            "sem_conteudo": round(s.sem_conteudo, 4), "linhas_fortes": s.linhas_fortes,
            "linhas_fracas": s.linhas_fracas, "caixas": len(s.onde_sumiu),
            "guardas": [round(g, 4) for g in s.guardas]}


def sem_rodar_o_programa() -> int:
    """A conta do programa sobre as mascaras gravadas pelo estudo."""
    import numpy as np

    from core import revisar

    gab = _gabarito()
    do_estudo = json.loads((TRABALHO / "sinais-rodada4.json").read_text(encoding="utf-8"))
    sinais, tempos, diferencas, falhadas_pela_base, atalho_mudou = {}, [], [], [], []
    for base in sorted(gab):
        dados = json.loads((DADOS / f"{base}.json").read_text(encoding="utf-8"))
        with np.load(DADOS / f"{base}.npz") as z:
            cinza, base_tinta, linhas = z["cinza"], z["base_tinta"], z["linhas"]
            imagem, a_tinta, pb_tinta = z["imagem"], z["a_tinta"], z["pb_tinta"]
        # 1) como o PROGRAMA mede (com os atalhos de tempo): as decisoes e o tempo
        t0 = time.perf_counter()
        rapido = revisar.medir(cinza, base_tinta, linhas, imagem, a_tinta, dados["poligonos"],
                               dados["altura_linha"], tinta_pb=pb_tinta)
        tempos.append((time.perf_counter() - t0, cinza.size / 1e6))
        # 2) sem os atalhos: os NUMEROS, para comparar um a um com os do estudo
        s = revisar.medir(cinza, base_tinta, linhas, imagem, a_tinta, dados["poligonos"],
                          dados["altura_linha"], tinta_pb=pb_tinta, completo=True)
        if revisar.motivos(rapido, True, 0.0, False) != revisar.motivos(s, True, 0.0, False):
            atalho_mudou.append((base, revisar.motivos(rapido, True, 0.0, False),
                                 revisar.motivos(s, True, 0.0, False)))
        # a conta do texto falhado com a tinta de base (o que o programa usa)
        # no lugar do Preto e branco inteiro (o que o estudo usou)
        pela_base = revisar._letra_falhada(cinza, dados["poligonos"], base_tinta)[:2]
        if pela_base != (s.falhadas, s.linhas_contadas):
            falhadas_pela_base.append((base, (s.falhadas, s.linhas_contadas), pela_base))
        sinais[base] = s
        e = do_estudo[base]
        for campo, meu in (("apagado_a", s.apagado_a), ("apagado_junto", s.apagado_junto),
                           ("maior_pedaco", s.maior_pedaco),
                           ("vazou_da_gravura", s.vazou_da_gravura), ("beirada_a", s.beirada_a),
                           ("falhadas_pb", s.falhadas), ("linhas_contadas", s.linhas_contadas),
                           ("sem_conteudo", s.sem_conteudo), ("linhas_fortes", s.linhas_fortes),
                           ("linhas_fracas", s.linhas_fracas)):
            if abs(float(meu) - float(e[campo])) > 0.00006:
                diferencas.append((base, campo, round(float(meu), 5), e[campo]))
        print(f"{base:32s} {tempos[-1][0]:5.2f}s {tempos[-1][1]:5.1f} MP  {_resumo(s)}", flush=True)
        del cinza, base_tinta, linhas, imagem, a_tinta, pb_tinta, s
        gc.collect()

    motivos, faixa = _motivos_com_a_faixa_do_livro(sinais)
    print()
    hoje = _contas("aviso de antes", {b: gab[b]["hoje"] for b in gab}, gab)
    nova = _contas("regra ajustada (conta do programa)", {b: bool(motivos[b]) for b in gab}, gab)
    print("faixa vira aviso do livro:", sorted(l for l, v in faixa.items() if v))
    outras = [(b, motivos[b], gab[b]["motivos4"]) for b in sorted(gab)
              if bool(motivos[b]) != gab[b]["regra4"]]
    print("paginas em que a conta do programa decide diferente do estudo:", outras)
    print("sinais diferentes dos do estudo (pagina, sinal, programa, estudo):", diferencas)
    print("texto falhado medido na tinta de base da resultado diferente em:", falhadas_pela_base)
    print("paginas em que os atalhos de tempo mudam a decisao (tem de ser nenhuma):", atalho_mudou)
    seg = sum(t for t, _ in tempos)
    mp = sum(m for _, m in tempos)
    print(f"tempo da conta: {seg:.1f}s nas 89 ({1000 * seg / len(tempos):.0f} ms por pagina em "
          f"media; {1000 * seg / mp:.0f} ms por milhao de pontos; a mais lenta "
          f"{max(tempos)[0]:.2f}s)")
    (AQUI / "conferir-89-sem-o-programa.json").write_text(json.dumps({
        "aviso_de_antes": hoje, "regra_ajustada": nova, "esperado": [ESPERADO_HOJE, ESPERADO_AJUSTADA],
        "faixa_do_livro": sorted(l for l, v in faixa.items() if v),
        "decide_diferente_do_estudo": outras, "sinais_diferentes": diferencas,
        "falhadas_pela_base": falhadas_pela_base, "atalho_mudou": atalho_mudou,
        "segundos": round(seg, 1),
        "paginas": {b: {"motivos": motivos[b], "gabarito": gab[b]["gabarito"],
                        "sinais": _resumo(sinais[b])} for b in sorted(gab)},
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    bateu = (hoje == ESPERADO_HOJE and nova == ESPERADO_AJUSTADA and not outras
             and not atalho_mudou)
    print("BATEU com o criterio de aceite" if bateu else "NAO BATEU com o criterio de aceite")
    return 0 if bateu else 1


def _pdf_da_pagina(pid: str) -> Path:
    do_acervo = PAGINAS / f"{pid}.pdf"
    return do_acervo if do_acervo.exists() else RAIZ / "gabarito" / "paginas" / f"{pid}.pdf"


def _dividir_a_mao(doc, projeto, filtro) -> None:
    """A folha dupla do Siebmacher 7 e 9, dividida como a pessoa faria na aba
    "Onde cortar" (copia de comum._dividir do estudo: as respostas do Samuel
    foram dadas nas metades)."""
    from core.dividir import detectar_lombada
    from core.pdf_io import pagina_para_array
    from core.pipeline import DPI_ANALISE
    from modelos import ConfigPagina

    folha = projeto.folhas[0]
    lombada = detectar_lombada(pagina_para_array(doc, 0, dpi=DPI_ANALISE))
    folha.dividir = True
    folha.posicao_corte = lombada.posicao
    folha.confianca_corte = lombada.confianca
    projeto.paginas = [ConfigPagina(indice=i, folha=0, metade=m, filtro=filtro)
                       for i, m in enumerate(("esquerda", "direita"))]


def com_o_programa(dpi: int, so: list[str] | None, como_no_estudo: bool = False,
                   completo: bool = False) -> int:
    """O programa de verdade, pagina por pagina, no "Só as letras" de fabrica.

    como_no_estudo: prepara a pagina como o programa de 07/10/2026 (o do
    estudo) preparava - corta antes de endireitar e endireita pela conta do
    programa - em vez do jeito do livro novo de hoje (endireita antes de
    cortar, G6, e a conta do ScanTailor). Serve para separar o que mudou na
    REGRA do que mudou no PREPARO da pagina depois do estudo.

    completo: mede sem os atalhos de tempo (core.revisar.medir, completo=True),
    para os NUMEROS de cada sinal sairem inteiros mesmo abaixo dos limites - e o
    que reacertar_limites.py le. As decisoes sao as mesmas."""
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("conferir-89")

    from core import analise, misto
    from core import pipeline as P
    from core.filtros import PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    gab = _gabarito()
    saida = AQUI / (f"conferir-89-programa-dpi{dpi}{'-preparo-do-estudo' if como_no_estudo else ''}"
                    f"{'-completo' if completo else ''}.json")
    feitas = json.loads(saida.read_text(encoding="utf-8")) if saida.exists() else {}

    vistos: list = []
    original = P.medir_para_revisar

    def espiao(*args, **kwargs):
        s = original(*args, **kwargs)
        vistos.append(s)
        return s

    P.medir_para_revisar = espiao
    # este script mede em qualquer resolucao pedida (e assim que se viu que a
    # 110 DPI a regra nao vale); o programa so mede na resolucao do PDF
    P.MEDIR_SO_NA_RESOLUCAO_DO_PDF = False
    if completo:
        medir_de_sempre = P.revisar.medir

        def medir_completo(*args, **kwargs):
            kwargs["completo"] = True
            return medir_de_sempre(*args, **kwargs)

        P.revisar.medir = medir_completo

    pids = sorted({b.split("__")[0] for b in gab})
    for pid in pids:
        if so and pid not in so:
            continue
        if any(b.split("__")[0] == pid for b in feitas):
            continue
        t0 = time.perf_counter()
        projeto = Projeto(caminho_entrada=str(_pdf_da_pagina(pid)), nome=pid)
        projeto.filtro_padrao = PRETO_E_BRANCO
        if como_no_estudo:
            from modelos import ENDIREITAR_DO_PROJETO_ANTIGO, ORDEM_DO_PROJETO_ANTIGO

            projeto.ordem_do_preparo = ORDEM_DO_PROJETO_ANTIGO
            projeto.endireitar_como = ENDIREITAR_DO_PROJETO_ANTIGO
        projeto = analisar_projeto(projeto)
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            if pid.startswith("siebmacher") and not projeto.folhas[0].dividir:
                _dividir_a_mao(doc, projeto, PRETO_E_BRANCO)
            projeto.misto_so_as_letras = True
            projeto.misto_fora_do_texto = misto.FORA_REDE
            # a regra pura, como no estudo: sem a "forca do preto sozinha" (com
            # ela ligada, a pagina de texto falhado e filtrada de novo com a
            # forca mais escura, e os avisos passam a ser os DEPOIS do reforco)
            projeto.reforcar_texto_falhado = False
            for pagina in projeto.paginas:
                pagina.filtro = PRETO_E_BRANCO
                vistos.clear()
                t1 = time.perf_counter()
                P.renderizar_pagina(doc, projeto, pagina, dpi=dpi if dpi else projeto.qualidade_dpi)
                base = f"{pid}__{pagina.metade}"
                s = vistos[-1] if vistos else None
                feitas[base] = {
                    "alertas": list(pagina.alertas),
                    "faixa_na_beirada": pagina.faixa_na_beirada,
                    "sinais": _resumo(s) if s is not None else None,
                    "marcas": P.marcas_do_aviso(pagina),
                    "segundos_do_desenho": round(time.perf_counter() - t1, 1),
                }
                print(f"{base:32s} {time.perf_counter() - t0:5.1f}s {feitas[base]['alertas']} "
                      f"{feitas[base]['sinais']}", flush=True)
        finally:
            doc.close()
            del projeto
            gc.collect()
        saida.write_text(json.dumps(feitas, indent=1, ensure_ascii=False), encoding="utf-8")

    faltam = [b for b in gab if b not in feitas]
    if faltam:
        print("ainda faltam", len(faltam), "paginas:", faltam)
        return 2
    # a faixa por livro, como no estudo: sai das paginas dos livros em que
    # esta em 70% ou mais
    from core import revisar

    por_livro: dict[str, list[bool]] = {}
    for base in gab:
        por_livro.setdefault(_livro(base), []).append(bool(feitas[base]["faixa_na_beirada"]))
    faixa = {livro: revisar.faixa_no_livro(v) for livro, v in por_livro.items()}
    vai = {}
    for base in gab:
        avisos = [a for a in feitas[base]["alertas"] if a in analise.AVISOS_DO_SO_AS_LETRAS]
        if faixa[_livro(base)]:
            avisos = [a for a in avisos if a != analise.FAIXA_NA_BEIRADA]
        vai[base] = bool(avisos)
    print()
    hoje = _contas("aviso de antes", {b: gab[b]["hoje"] for b in gab}, gab)
    nova = _contas(f"regra ajustada (o programa, {dpi} DPI)", vai, gab)
    print("faixa vira aviso do livro:", sorted(l for l, v in faixa.items() if v))
    outras = [(b, [a for a in feitas[b]["alertas"] if a in analise.AVISOS_DO_SO_AS_LETRAS],
               gab[b]["motivos4"]) for b in sorted(gab) if vai[b] != gab[b]["regra4"]]
    print("paginas em que o programa decide diferente do estudo:", outras)
    bateu = nova == ESPERADO_AJUSTADA
    print("BATEU com o criterio de aceite" if bateu else "NAO BATEU com o criterio de aceite")
    return 0 if bateu else 1


def main() -> int:
    args = sys.argv[1:]
    if "--programa" not in args:
        return sem_rodar_o_programa()
    dpi = 300
    if "--dpi" in args:
        dpi = int(args[args.index("--dpi") + 1])
    so = [a for a in args if not a.startswith("--") and not a.isdigit()]
    return com_o_programa(dpi, so[0].split(",") if so else None,
                          como_no_estudo="--preparo-do-estudo" in args,
                          completo="--completo" in args)


if __name__ == "__main__":
    sys.exit(main())
