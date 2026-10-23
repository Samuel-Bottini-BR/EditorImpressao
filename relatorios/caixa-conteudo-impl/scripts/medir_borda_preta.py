"""Mede quanto preto de scanner sobra em cada beirada da página que o
PROGRAMA entrega (item 2.13), nas páginas que o Samuel escolheu em 20/10/2026
como alvo da borda preta, mais o Pesel 21 (que tem de continuar inteiro).

As palavras dele (20/10): Antiphon 260 "tem que cortar a faixa inteira.";
Antiphon 88 "Tem que cortar em cima e embaixo e dos lados ainda tem um fio
preto."; Camões 104 "É para sumir totalmente."; Cursus 3 "tem que ficar
rente a folha de papel, não pode ter preto ali."; Matemática 32 "ainda estou
vendo a faixa preta.".

Regra dele para os testes (20/10): "deveriamos ter indireitado a folha antes
de cortar [...]" - por isso a página passa pelo programa inteiro
(analisar_projeto e renderizar_pagina: girar, dividir, endireitar, cortar),
livro novo, conta do ScanTailor, sem filtro.

A medida é a do verificador do corte (relatorios/conserto-corte-g6/scripts/
medir.py, _beirada e _por_lado, importadas daqui sem cópia): a faixa "escura"
(mais escura que 60% do papel) encostada na beirada, em mm por lado
("mm" = percentil 90 ao longo do lado; "mm_max" = o pior ponto).

Jeitos: hoje (desligado), só o preto, até a moldura, e os dois pintando de
branco (item 2.14) em vez de cortar. Grava
dados/borda-preta-mm.json e as páginas prontas reduzidas em
img/borda-preta-mm/. Uso: python medir_borda_preta.py [pid ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "relatorios" / "conserto-corte-g6" / "scripts"))

import medir as verif  # noqa: E402  (a medida do verificador)

PAGINAS = ["antiphon_p260", "antiphon_p088", "camoes_p104", "cursus_p003", "matematica_p032",
           "pesel_p021", "egenloff_p047"]
TRABALHO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
DPI = 200
JEITOS = {"hoje": {}, "so_o_preto": {"borda_preta": True, "borda_preta_ate": "so_o_preto"},
          "ate_a_moldura": {"borda_preta": True, "borda_preta_ate": "ate_a_moldura"},
          # item 2.14: pintar de branco em vez de cortar fora
          "so_o_preto_pinta": {"borda_preta": True, "borda_preta_ate": "so_o_preto",
                               "borda_preta_fazer": "pintar"},
          "ate_a_moldura_pinta": {"borda_preta": True, "borda_preta_ate": "ate_a_moldura",
                                  "borda_preta_fazer": "pintar"}}


def medir(pid: str, jeito: str) -> dict:
    from core import pipeline as P
    from core.filtros import ORIGINAL
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(TRABALHO / f"{pid}.pdf"), nome=pid, **JEITOS[jeito])
    projeto.filtro_padrao = ORIGINAL
    projeto.limpar = False
    projeto.qualidade_dpi = DPI
    projeto = P.analisar_projeto(projeto)
    for g in (P._GEOMETRIAS, P._CONTEUDOS, P._TAMANHOS):
        g.clear()
    doc = abrir_pdf(projeto.caminho_entrada)
    saida = {}
    try:
        for pagina in projeto.paginas:
            final, _ = P.renderizar_pagina(doc, projeto, pagina, dpi=DPI)
            cinza = verif._cinza(final)
            papel = verif._nivel_do_papel(cinza)
            _fr, encosta, f = verif._beirada(cinza < 0.6 * papel)
            verif.DPI = DPI
            lados = verif._por_lado(encosta, f)
            geo = P._geometria_guardada(projeto.folhas[pagina.folha], pagina, projeto)
            saida[pagina.metade] = {
                "lados_mm": {k: v["mm"] for k, v in lados.items()},
                "lados_mm_max": {k: v["mm_max"] for k, v in lados.items()},
                "tamanho_mm": [round(final.shape[1] * 25.4 / DPI, 1), round(final.shape[0] * 25.4 / DPI, 1)],
                "recorte": None if geo is None or geo[0] is None else [round(float(v), 4) for v in geo[0]],
                "angulo": None if geo is None else round(float(geo[1]), 2)}
            pasta = PASTA / "img" / "borda-preta-mm"
            pasta.mkdir(parents=True, exist_ok=True)
            pequena = cv2.resize(final, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(pasta / f"{pid}__{pagina.metade}__{jeito}.jpg"), pequena,
                        [cv2.IMWRITE_JPEG_QUALITY, 80])
    finally:
        doc.close()
    return saida


def main() -> None:
    destino = PASTA / "dados" / "borda-preta-mm.json"
    dados = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for pid in (sys.argv[1:] or PAGINAS):
        dados[pid] = {j: medir(pid, j) for j in JEITOS}
        for j, porpag in dados[pid].items():
            for metade, r in porpag.items():
                print(pid, metade, j, r["lados_mm"], "max", r["lados_mm_max"], r["tamanho_mm"], flush=True)
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
