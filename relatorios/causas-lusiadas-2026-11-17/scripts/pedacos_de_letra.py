"""Implementador, 17/11/2026 (lu-1): cada pedaço que a procura marcou como LETRA na página, medido com as
réguas que o próprio detector já tem (core.detectar_regioes._parece_escrita e _tinta_em_pedacos_de_glifo), e
se ele encosta na gravura. Serve para ver se "pedaço que não parece escrita e encosta na pintura" separa os
remendos (p. 14, p. 8 do Lusíadas) das letras de verdade (p. 2, folha de rosto; p. 12, título).
Só leitura (usa a cópia do projeto de decompor_marcacao.py).
"""
from __future__ import annotations

import json
import sys

import decompor_marcacao as dm  # prepara o ambiente (cópia do projeto, pasta de dados própria)

cv2, np = dm.cv2, dm.np
dr, pipeline = dm.dr, dm.pipeline


def main(numeros):
    pasta = next(p for p in (dm.TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
    projeto = dm.projetos.carregar_estado(dm.projetos.ler_resumo(pasta))
    dpi = 300
    doc = dm.abrir_pdf(projeto.caminho_entrada)
    res = {}
    for n in numeros:
        pg = projeto.paginas[n - 1]
        folha = projeto.folhas[pg.folha]
        prep = pipeline.preparar_metade(dm.pagina_para_array(doc, folha.indice, dpi), folha, pg, projeto, dpi=dpi)
        h, w = prep.shape[:2]
        sel = pg.obter_selecao()
        g = sel.mascara(h, w, dm.GRAVURA)
        le = sel.mascara(h, w, dm.LETRA)
        tinta = dr.mascara_de_tinta(dr._tres_canais_ou_cinza(prep))
        perto = cv2.dilate(g.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
        num, rot, stats, _ = cv2.connectedComponentsWithStats(le.astype(np.uint8), connectivity=8)
        pecas = []
        for i in range(1, num):
            x, y, ww, hh, area = stats[i]
            if area < 0.001 * h * w:
                continue
            f = (slice(y, y + hh), slice(x, x + ww))
            t = tinta[f] & (rot[f] == i)
            pecas.append({"caixa": [round(x / w, 2), round(y / h, 2), round((x + ww) / w, 2), round((y + hh) / h, 2)],
                          "area": round(area / (h * w), 4),
                          "parece_escrita": bool(dr._parece_escrita(t)),
                          "glifos": round(dr._tinta_em_pedacos_de_glifo(t), 2),
                          "linhas_vazias": round(dr._fracao_de_linhas_vazias(t), 2),
                          "tinta": round(float(t.mean()), 2),
                          "encosta_na_gravura": bool((perto & (rot == i)).any())})
        res[f"p{n}"] = pecas
    (dm.AQUI / "pedacos_de_letra.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [14, 8, 2, 12])
