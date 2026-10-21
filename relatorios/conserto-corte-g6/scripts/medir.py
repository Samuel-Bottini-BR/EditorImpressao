"""COPIA do medir.py do verificador (ramo verif-corte-g6-2026-10-13,
relatorios/conferir/corte-g6-2026-10-13/scripts/medir.py), para o conserto do
corte do G6 (implementador, 13/10/2026). Mudou SO: os caminhos (esta pasta),
e duas variaveis de ambiente - MEDIR_CONFIGS ("C" mede so o livro novo) e
MEDIR_SAIDA (o nome do .json gravado nesta pasta). As contas sao as dele,
ponto por ponto, para as tres colunas (antiga, nova de hoje, consertada)
serem comparaveis.

Mede o CORTE das paginas nas duas ordens do preparo (G6, commit 4a7f288).

Conferencia de 13/10/2026 (verificador). Nada aqui muda o programa, o acervo,
o gabarito nem a pasta do estudo: tudo so e lido. A pasta de dados do programa
e isolada (pasta_de_dados_dos_scripts).

O QUE COMPARA
    Para cada uma das 87 folhas (89 paginas) do estudo do "Para revisar" - as
    32 do gabarito estao todas dentro delas - a pagina e preparada pelo
    PROGRAMA (core.pipeline.renderizar_pagina, 300 DPI, sem filtro nenhum:
    "Limpar a folha" desligado, para ver so o corte e o giro) de tres jeitos:

      A  "antigo"      cortar antes + endireitar pela conta do programa
                       (o projeto gravado antes de 05/10: o livro antigo de
                       verdade; e o "--preparo-do-estudo" do conferir_89.py)
      B  "so a ordem"  cortar antes + endireitar pela conta do ScanTailor
                       (mesmo angulo do livro novo: a diferenca B -> C e SO a
                       ordem, que e o que o G6 mudou)
      C  "novo"        endireitar antes + conta do ScanTailor (livro novo)

O QUE MEDE EM CADA UM (dados.json)
    - recorte e angulo guardados pelo programa; tamanho da pagina final;
    - faixa escura encostada na beirada: a conta de core/revisar.py
      (_beirada_escura, ramo fase2-para-revisar), copiada aqui porque o
      arquivo ainda nao esta no fase-1. Em duas mascaras: "escuro" (mais
      escuro que 60% do papel: fundo do scanner, sombra da lombada) e "pb"
      (a tinta do Preto e branco de fabrica: e a mascara em que o aviso do
      programa conta). Por lado: a largura da faixa em mm;
    - cunha branca do giro que entrou na pagina;
    - conteudo impresso: a tinta da pagina inteira (pecas que nao encostam na
      beirada) e levada pelo MESMO corte e giro; conta-se quanta tinta fica
      de fora, quantas pecas saem partidas e a folga ate a beirada.

USO
    python medir.py [pid,pid,...]     (sem nada: todas; pula as ja medidas)
    Uma pagina por vez na memoria. Grava dados.json a cada pagina.
"""

from __future__ import annotations

import gc
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent                                   # relatorios/conserto-corte-g6
RAIZ = PASTA.parents[1]                               # a copia do projeto
TRABALHO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho")
PAGINAS = TRABALHO / "paginas"
FINAIS = RAIZ / "_tmp" / "finais"                     # as paginas prontas (fora do git)
SUFIXO = os.environ.get("MEDIR_SUFIXO", "")           # no nome das paginas prontas
DADOS = PASTA / os.environ.get("MEDIR_SAIDA", "dados.json")
DPI = 300

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

CONFIGS = tuple(os.environ.get("MEDIR_CONFIGS", "A,B,C").split(","))
NOMES = {"A": "antigo (corta antes, conta do programa)",
         "B": "so a ordem antiga (corta antes, conta do ScanTailor)",
         "C": "novo (endireita antes, conta do ScanTailor)"}


def _pdf_da_pagina(pid: str) -> Path:
    do_estudo = PAGINAS / f"{pid}.pdf"
    return do_estudo if do_estudo.exists() else RAIZ / "gabarito" / "paginas" / f"{pid}.pdf"


def _projeto(pid: str, cfg: str):
    """O projeto de uma pagina, analisado, no jeito `cfg` (A, B ou C)."""
    from core.dividir import detectar_lombada
    from core.filtros import ORIGINAL
    from core.pdf_io import abrir_pdf, pagina_para_array
    from core.pipeline import DPI_ANALISE, analisar_projeto
    from modelos import (ENDIREITAR_DO_LIVRO_NOVO, ENDIREITAR_DO_PROJETO_ANTIGO,
                         ORDEM_DO_LIVRO_NOVO, ORDEM_DO_PROJETO_ANTIGO, ConfigPagina, Projeto)

    projeto = Projeto(caminho_entrada=str(_pdf_da_pagina(pid)), nome=pid)
    projeto.filtro_padrao = ORIGINAL
    projeto.limpar = False            # nenhum filtro: so o corte e o giro
    projeto.qualidade_dpi = DPI
    projeto.ordem_do_preparo = ORDEM_DO_LIVRO_NOVO if cfg == "C" else ORDEM_DO_PROJETO_ANTIGO
    projeto.endireitar_como = (ENDIREITAR_DO_PROJETO_ANTIGO if cfg == "A"
                               else ENDIREITAR_DO_LIVRO_NOVO)
    projeto = analisar_projeto(projeto)
    if pid.startswith("siebmacher") and not projeto.folhas[0].dividir:
        # a folha dupla do Siebmacher 7 e 9, dividida como a pessoa faria (o
        # mesmo de conferir_89._dividir_a_mao, do implementador)
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            lombada = detectar_lombada(pagina_para_array(doc, 0, dpi=DPI_ANALISE))
        finally:
            doc.close()
        folha = projeto.folhas[0]
        folha.dividir = True
        folha.posicao_corte = lombada.posicao
        folha.confianca_corte = lombada.confianca
        projeto.paginas = [ConfigPagina(indice=i, folha=0, metade=m, filtro=ORIGINAL)
                           for i, m in enumerate(("esquerda", "direita"))]
    return projeto


# ---------------------------------------------------------------------------
# As medidas
# ---------------------------------------------------------------------------

def _cinza(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _nivel_do_papel(cinza: np.ndarray) -> float:
    """O percentil 90 do miolo da pagina (60% x 60% do meio)."""
    a, l = cinza.shape
    miolo = cinza[int(a * 0.2):int(a * 0.8):4, int(l * 0.2):int(l * 0.8):4]
    return float(np.percentile(miolo, 90)) if miolo.size else 255.0


def _beirada(tinta: np.ndarray):
    """A conta de core/revisar._beirada_escura (ramo fase2-para-revisar),
    COPIADA ponto por ponto: fracao da pagina coberta por mancha cheia de
    tinta (sobra de uma abertura com um quadrado de 1,5% do lado menor)
    encostada na beirada (ate 1% dela), na pagina reduzida a 1000 pontos.
    Devolve (fracao, mascara das manchas que encostam, fator da reducao)."""
    alt, larg = tinta.shape
    f = 1000 / max(alt, larg)
    peq = cv2.resize(tinta.astype(np.uint8) * 255, (max(1, round(larg * f)), max(1, round(alt * f))),
                     interpolation=cv2.INTER_AREA) > 127
    a, l = peq.shape
    lado = max(3, int(round(0.015 * min(a, l))))
    cheia = cv2.morphologyEx(peq.astype(np.uint8), cv2.MORPH_OPEN,
                             np.ones((lado, lado), np.uint8)) > 0
    _n, rot, _st, _c = cv2.connectedComponentsWithStats(cheia.astype(np.uint8), connectivity=8)
    m = max(1, int(round(0.01 * min(a, l))))
    borda = np.zeros_like(cheia)
    borda[:m, :] = borda[-m:, :] = True
    borda[:, :m] = borda[:, -m:] = True
    ids = np.unique(rot[cheia & borda])
    ids = ids[ids > 0]
    if not len(ids):
        return 0.0, np.zeros_like(cheia), f
    encosta = np.isin(rot, ids)
    return float(np.count_nonzero(encosta)) / (a * l), encosta, f


def _por_lado(encosta: np.ndarray, f: float) -> dict:
    """De cada lado, a largura da faixa que encosta na beirada, em mm: em cada
    linha (ou coluna) contam-se os pontos da faixa na metade daquele lado;
    "mm" e o percentil 90 dessas contagens (a faixa que pega quase o lado
    todo), "mm_max" o maior, "cobre" a fracao do lado que tem faixa."""
    a, l = encosta.shape
    mm_por_ponto = 25.4 / (DPI * f)
    lados = {"esq": encosta[:, :l // 2].sum(axis=1), "dir": encosta[:, l // 2:].sum(axis=1),
             "topo": encosta[:a // 2, :].sum(axis=0), "pe": encosta[a // 2:, :].sum(axis=0)}
    return {k: {"mm": round(float(np.percentile(v, 90)) * mm_por_ponto, 2),
                "mm_max": round(float(v.max()) * mm_por_ponto, 2),
                "cobre": round(float(np.count_nonzero(v)) / max(1, v.size), 3)}
            for k, v in lados.items()}


def _medir_a_beirada(final: np.ndarray) -> dict:
    from core.filtros import filtro_preto_e_branco

    cinza = _cinza(final)
    papel = _nivel_do_papel(cinza)
    fr_e, enc_e, f = _beirada(cinza < 0.6 * papel)
    try:
        pb = filtro_preto_e_branco(final)
        fr_p, enc_p, f2 = _beirada(_cinza(pb) < 128)
        lados_pb = _por_lado(enc_p, f2)
    except Exception as erro:  # noqa: BLE001 - a medida "escuro" basta
        fr_p, lados_pb = None, {"erro": str(erro)}
    return {"papel": round(papel, 1),
            "beirada_escuro": round(fr_e, 5), "lados_escuro": _por_lado(enc_e, f),
            "beirada_pb": None if fr_p is None else round(fr_p, 5), "lados_pb": lados_pb}


# --- o conteudo impresso, levado pelo mesmo corte e giro ---------------------

LADO_DO_CONTEUDO = 2000       # a mascara do conteudo e feita na pagina reduzida a isto


def _pecas_do_conteudo(inteira: np.ndarray):
    """As pecas de tinta da pagina INTEIRA (girada de 90 e dividida, sem corte
    nem endireitar), reduzida a LADO_DO_CONTEUDO: tinta pelo limiar local do
    programa (core.filtros.binarizar, o mesmo do corte) OU mais escura que 60%
    do papel; o que esta ligado a beirada da imagem (borda do scanner, sombra
    da lombada, folha vizinha) fica de fora. Devolve (rotulos, areas, quais
    tem tamanho de letra, fator)."""
    from core.filtros import binarizar, janela_para_altura

    cinza = _cinza(inteira)
    alt, larg = cinza.shape
    f = min(1.0, LADO_DO_CONTEUDO / max(alt, larg))
    if f < 1.0:
        cinza = cv2.resize(cinza, (max(8, round(larg * f)), max(8, round(alt * f))),
                           interpolation=cv2.INTER_AREA)
    papel = _nivel_do_papel(cinza)
    tinta = (binarizar(cinza, janela=janela_para_altura(cinza.shape[0]), k=0.20) == 0)
    tudo = (tinta | (cinza < 0.6 * papel)).astype(np.uint8)
    n, rot, st, _c = cv2.connectedComponentsWithStats(tudo, connectivity=8)
    a, l = tudo.shape
    x, y, w, h, area = (st[:, i] for i in range(5))
    encosta = (x <= 1) | (y <= 1) | (x + w >= l - 1) | (y + h >= a - 1)
    fica = ~encosta & (area >= 6)
    fica[0] = False
    de_letra = fica & (np.maximum(w, h) >= 8) & (np.minimum(w, h) >= 3)
    rot = np.where(fica[rot], rot, 0).astype(np.float32)
    return rot, area.astype(np.int64), de_letra, f


def _levar(mapa: np.ndarray, recorte, angulo: float, endireitar: bool, endireita_antes: bool):
    """Leva um mapa (do tamanho da pagina inteira, reduzido ou nao) pelo mesmo
    corte e giro do programa, ponto mais proximo, fundo 0. Replica de
    core.pipeline._preparar_metade_e_geometria nas duas ordens; para a imagem
    de verdade a replica e conferida contra o programa (ver `confere`)."""
    from core.endireitar import ANGULO_MINIMO
    from core.recortar import caixa_em_pontos

    girar = endireitar and abs(angulo) >= ANGULO_MINIMO
    alt, larg = mapa.shape[:2]
    caixa = None if recorte is None else caixa_em_pontos(mapa.shape, recorte)
    if endireita_antes:
        if not girar:
            return mapa if caixa is None else mapa[caixa[1]:caixa[3], caixa[0]:caixa[2]]
        matriz = cv2.getRotationMatrix2D((larg / 2.0, alt / 2.0), angulo, 1.0)
        tamanho = (larg, alt)
        if caixa is not None:
            matriz[0, 2] -= caixa[0]
            matriz[1, 2] -= caixa[1]
            tamanho = (caixa[2] - caixa[0], caixa[3] - caixa[1])
        return cv2.warpAffine(mapa, matriz, tamanho, flags=cv2.INTER_NEAREST,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    img = mapa if caixa is None else mapa[caixa[1]:caixa[3], caixa[0]:caixa[2]]
    if not girar:
        return img
    a2, l2 = img.shape[:2]
    matriz = cv2.getRotationMatrix2D((l2 / 2.0, a2 / 2.0), angulo, 1.0)
    return cv2.warpAffine(img, matriz, (l2, a2), flags=cv2.INTER_NEAREST,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def _medir_o_conteudo(pecas, recorte, angulo, endireitar, endireita_antes) -> dict:
    rot, area, de_letra, f = pecas
    levado = _levar(rot, recorte, angulo, endireitar, endireita_antes)
    ids = levado.astype(np.int64).ravel()
    depois = np.bincount(ids, minlength=len(area))[:len(area)]
    antes = np.bincount(rot.astype(np.int64).ravel(), minlength=len(area))[:len(area)]
    quais = np.flatnonzero(de_letra)
    total = int(antes[quais].sum())
    ficou = int(np.minimum(depois[quais], antes[quais]).sum())
    razao = depois[quais] / np.maximum(1, antes[quais])
    fora = int(np.count_nonzero(razao < 0.05))
    partidas = int(np.count_nonzero((razao >= 0.05) & (razao < 0.90)))
    # a folga: da caixa de toda a tinta de letra que ficou ate cada beirada
    mm_por_ponto = 25.4 / (DPI * f)
    tem = np.isin(levado.astype(np.int64), quais)
    a, l = tem.shape
    folga = None
    if tem.any():
        ys, xs = np.flatnonzero(tem.any(axis=1)), np.flatnonzero(tem.any(axis=0))
        folga = {"esq": round(float(xs[0]) * mm_por_ponto, 2),
                 "dir": round(float(l - 1 - xs[-1]) * mm_por_ponto, 2),
                 "topo": round(float(ys[0]) * mm_por_ponto, 2),
                 "pe": round(float(a - 1 - ys[-1]) * mm_por_ponto, 2)}
    return {"pecas": int(len(quais)), "pecas_fora": fora, "pecas_partidas": partidas,
            "tinta_perdida": round(1.0 - ficou / total, 5) if total else 0.0, "folga_mm": folga}


def _cunha_branca(forma, recorte, angulo, endireitar, endireita_antes) -> float:
    """Fracao da pagina final que e o branco posto pelo giro (ponto de fora
    da pagina de origem)."""
    alt, larg = forma[:2]
    f = min(1.0, 1000 / max(alt, larg))
    uns = np.ones((max(8, round(alt * f)), max(8, round(larg * f))), np.uint8)
    levado = _levar(uns, recorte, angulo, endireitar, endireita_antes)
    return round(1.0 - float(levado.mean()), 5)


# ---------------------------------------------------------------------------

def medir_pagina(pid: str) -> dict:
    """As medidas de todas as paginas (metades) de uma folha, nos tres jeitos."""
    from core import pipeline as P
    from core.ordem_do_preparo import endireita_antes
    from core.pdf_io import abrir_pdf, pagina_para_array

    saida: dict = {}
    pecas_por_base: dict = {}
    for cfg in CONFIGS:
        projeto = _projeto(pid, cfg)
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            for pagina in projeto.paginas:
                base = f"{pid}__{pagina.metade}"
                folha = projeto.folhas[pagina.folha]
                t0 = time.perf_counter()
                final, _mono = P.renderizar_pagina(doc, projeto, pagina, dpi=DPI)
                segundos = time.perf_counter() - t0
                geometria = P._geometria_guardada(folha, pagina, projeto)
                recorte, angulo = geometria if geometria is not None else (None, 0.0)
                medidas = P.angulos_medidos(projeto, pagina) or {}
                img_folha = pagina_para_array(doc, folha.indice, dpi=DPI)
                inteira = P.preparar_para_recorte(img_folha, folha, pagina, projeto)
                antes = endireita_antes(projeto)
                if base not in pecas_por_base:
                    pecas_por_base[base] = _pecas_do_conteudo(inteira)
                # a replica do corte e do giro tem de dar a imagem do programa
                replica = _levar(_cinza(inteira), recorte, float(angulo), projeto.endireitar, antes)
                confere = replica.shape[:2] == final.shape[:2]
                diferenca = (float(np.abs(replica[::4, ::4].astype(np.int16)
                                          - _cinza(final)[::4, ::4].astype(np.int16)).mean())
                             if confere else None)
                r = {"replica_diferenca_media": None if diferenca is None else round(diferenca, 2),"nome": NOMES[cfg], "ordem": projeto.ordem_do_preparo,
                     "endireitar_como": projeto.endireitar_como,
                     "conta_que_valeu": medidas.get("jeito"),
                     "angulo": round(float(angulo), 3),
                     "angulo_programa": medidas.get("programa"),
                     "angulo_scantailor": medidas.get("scantailor"),
                     "recorte": None if recorte is None else [round(float(v), 5) for v in recorte],
                     "pagina_inteira_px": [int(inteira.shape[1]), int(inteira.shape[0])],
                     "tamanho_px": [int(final.shape[1]), int(final.shape[0])],
                     "tamanho_mm": [round(final.shape[1] * 25.4 / DPI, 1),
                                    round(final.shape[0] * 25.4 / DPI, 1)],
                     "replica_do_tamanho_confere": bool(confere),
                     "segundos": round(segundos, 2)}
                r.update(_medir_a_beirada(final))
                r["cunha_branca"] = _cunha_branca(inteira.shape, recorte, float(angulo),
                                                  projeto.endireitar, antes)
                r.update(_medir_o_conteudo(pecas_por_base[base], recorte, float(angulo),
                                           projeto.endireitar, antes))
                FINAIS.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(FINAIS / f"{base}__{cfg}{SUFIXO}.jpg"), final,
                            [cv2.IMWRITE_JPEG_QUALITY, 90])
                if cfg == "C" and not SUFIXO:
                    cv2.imwrite(str(FINAIS / f"{base}__inteira.jpg"), inteira,
                                [cv2.IMWRITE_JPEG_QUALITY, 90])
                # o md5 da pagina pronta: para dizer "identica ponto por ponto"
                import hashlib
                r["md5"] = hashlib.md5(np.ascontiguousarray(final).tobytes()).hexdigest()
                saida.setdefault(base, {"pid": pid, "metade": pagina.metade})[cfg] = r
                del final, img_folha, inteira, replica
        finally:
            doc.close()
            del projeto
            gc.collect()
    return saida


def _gb_livres() -> float:
    """Memoria fisica livre, em GB (Windows)."""
    import ctypes

    class Estado(ctypes.Structure):
        _fields_ = [("tamanho", ctypes.c_ulong), ("carga", ctypes.c_ulong),
                    ("total", ctypes.c_ulonglong), ("livre", ctypes.c_ulonglong),
                    ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                    ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong),
                    ("e", ctypes.c_ulonglong)]

    estado = Estado()
    estado.tamanho = ctypes.sizeof(Estado)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado))
    return estado.livre / 2 ** 30


def _esperar_memoria(minimo: float = 3.0, no_maximo: float = 600.0) -> None:
    """Espera ter `minimo` GB livres (ha outro agente rodando testes no PC);
    depois de `no_maximo` segundos segue assim mesmo, avisando."""
    t0 = time.perf_counter()
    while _gb_livres() < minimo:
        if time.perf_counter() - t0 > no_maximo:
            print(f"  (segui com {_gb_livres():.1f} GB livres depois de esperar)", flush=True)
            return
        time.sleep(10)


def _pids() -> list[str]:
    gab = json.loads((TRABALHO / "regra4.json").read_text(encoding="utf-8"))
    return sorted({b.split("__")[0] for b in gab})


def main() -> int:
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("corte-g6")
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    dados = json.loads(DADOS.read_text(encoding="utf-8")) if DADOS.exists() else {}
    do_gabarito = set(json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"])
    for pid in _pids():
        if so and pid not in so:
            continue
        if any(v.get("pid") == pid and all(c in v for c in CONFIGS) for v in dados.values()):
            continue
        _esperar_memoria()
        t0 = time.perf_counter()
        try:
            novas = medir_pagina(pid)
        except Exception as erro:  # noqa: BLE001 - uma pagina com erro nao para as outras
            import traceback

            traceback.print_exc()
            novas = {f"{pid}__erro": {"pid": pid, "erro": repr(erro)}}
        for base, v in novas.items():
            v["no_gabarito"] = pid in do_gabarito
            dados[base] = v
            if "C" in v:
                print(f"{base:32s} {time.perf_counter() - t0:5.1f}s  "
                      + "  ".join(f"{c}: {v[c]['tamanho_px']} ang {v[c]['angulo']:+.2f} "
                                  f"escuro {100 * v[c]['beirada_escuro']:.2f}% "
                                  f"pb {100 * (v[c]['beirada_pb'] or 0):.2f}% "
                                  f"partidas {v[c]['pecas_partidas']} fora {v[c]['pecas_fora']}"
                                  for c in CONFIGS), flush=True)
        DADOS.write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
        gc.collect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
