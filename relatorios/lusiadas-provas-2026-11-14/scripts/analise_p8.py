"""Verificador, 14/11/2026 (D-690): a página 8 do projeto da fase a: como o Preto e branco
classificou cada zona de gravura (_tipos_das_zonas: foto/pintura, decoração ou desenho), e a
mesma página com a caixinha "Gravuras em tons de cinza" (D-588) marcada, numa CÓPIA da página.
Também a página 14 com a caixinha, para ver se os remendos somem."""
import copy, json, os, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent; PASTA = AQUI.parent; RAIZ = PASTA.parents[1]; TRAB = PASTA / "_dados"
os.environ["LOCALAPPDATA"] = str(TRAB / "dados-analise"); os.chdir(RAIZ); sys.path.insert(0, str(RAIZ))
import cv2, numpy as np  # noqa
import projetos  # noqa
projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
from core import pipeline, filtros  # noqa
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa
from core.selecao import GRAVURA  # noqa
SAI = PASTA / "prints" / "analise"
pasta = next(p for p in (TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
projeto = projetos.carregar_estado(projetos.ler_resumo(pasta))
doc = abrir_pdf(projeto.caminho_entrada)
res = {}
for n in (8, 14):
    pg = projeto.paginas[n - 1]
    folha = projeto.folhas[pg.folha]
    prep = pipeline.preparar_metade(pagina_para_array(doc, folha.indice, 300), folha, pg, projeto, dpi=300)
    sel = pg.obter_selecao()
    h, w = prep.shape[:2]
    peso = sel.peso(h, w, GRAVURA)
    rot, foto, deco, _ref = filtros._tipos_das_zonas(filtros._tres_canais(prep), peso,
                                                     com_decoracao=True)
    areas = np.bincount(rot.ravel(), minlength=len(foto))
    zonas = sorted(((int(areas[i]), "pintura/foto" if foto[i] else ("enfeite" if deco[i] else "desenho de traço"))
                    for i in range(1, len(foto))), reverse=True)[:6]
    res[f"p{n}-zonas-maiores"] = zonas
    pg2 = copy.deepcopy(pg)
    pg2.gravuras_em_tons_de_cinza = True
    img, _m = pipeline.renderizar_pagina(doc, projeto, pg2, dpi=300)
    cv2.imwrite(str(SAI / f"p{n}-5-com-gravuras-em-cinza.png"), img)
(AQUI / "analise_p8.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
