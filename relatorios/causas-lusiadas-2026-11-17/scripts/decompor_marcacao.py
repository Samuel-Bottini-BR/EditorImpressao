"""Implementador, 17/11/2026 (causas do Lusíadas, lu-1 e lu-7): de onde vem cada pedaço da marcação.

Lê uma CÓPIA do projeto do Lusíadas gravado pelo verificador em 14/11 (ramo lusiadas-provas, fase a:
Automático com Dividir + capa aberta, Endireitar, Limpar em Preto e branco, Gravuras e fotos) e, para as
páginas pedidas (de fábrica 14 e 8):

  1. prepara a página pelo caminho inteiro (dividir -> endireitar; sem Cortar, como na rodada) no DPI do PDF;
  2. procura a marcação DE NOVO, do zero, pela função do programa (core.detectar_regioes.detectar, com o
     detector e as opções que o programa usa: pipeline.escolha_da_gravura), espiando por dentro:
       - a gravura que o ScanTailor achou (antes de qualquer regra);
       - as caixas do leitor de texto (o modelo de layout) e quais viraram "escrita certa";
     e mede, dentro da área que é pintura no ScanTailor, quanto virou LETRA e PAPEL, e por quê;
  3. desenha a página como sai (pipeline.renderizar_pagina, no DPI do PDF) em Preto e branco, Melhorar e
     Mágico pro (só muda o filtro da página, numa cópia na memória).

Nada é gravado no projeto. Imagens em ../prints/decompor/ (fora do git: Lusíadas tem direito autoral).
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe decompor_marcacao.py [14 8]
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
ESTUDO = RAIZ.parent / "lusiadas-provas" / "relatorios" / "lusiadas-provas-2026-11-14" / "_dados"
TRAB = PASTA / "_dados"
os.environ["LOCALAPPDATA"] = str(TRAB / "localappdata")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import projetos  # noqa: E402

if not (TRAB / "projetos").exists():
    shutil.copytree(ESTUDO / "projetos", TRAB / "projetos")
projetos.pasta_dos_projetos = lambda: TRAB / "projetos"

from core import detectar_regioes as dr  # noqa: E402
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, dpi_real_da_pagina, pagina_para_array  # noqa: E402
from core.selecao import GRAVURA, LETRA, PAPEL, Selecao  # noqa: E402

SAI = PASTA / "prints" / "decompor"
SAI.mkdir(parents=True, exist_ok=True)

ESPIA: dict = {}
_achar_original = dr.DetectorDeLayout.achar
_resultado_original = dr._ProcuraNoScanTailor.resultado


def _achar_espiado(self, img):
    achados = _achar_original(self, img)
    ESPIA["achados"] = achados
    return achados


def _resultado_espiado(self):
    r = _resultado_original(self)
    ESPIA["gravura_st"] = None if r[0] is None else r[0].copy()
    return r


dr.DetectorDeLayout.achar = _achar_espiado
dr._ProcuraNoScanTailor.resultado = _resultado_espiado


def bgr(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def pintar(img, camadas):
    base = bgr(img).astype(np.float32)
    w = img.shape[1]
    for m, cor in camadas:
        if m is None or not m.any():
            continue
        base[m] = base[m] * 0.5 + np.array(cor, np.float32) * 0.5
        cont, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(base, cont, -1, cor, max(2, w // 400))
    return base.clip(0, 255).astype(np.uint8)


def caixas(achados, classes, h, w, so_escrita=False, tinta=None):
    m = np.zeros((h, w), bool)
    for a in achados:
        if a.classe not in classes:
            continue
        x0, y0, x1, y1 = a.caixa
        f = (slice(int(y0 * h), int(y1 * h)), slice(int(x0 * w), int(x1 * w)))
        if so_escrita and dr._tinta_em_pedacos_de_glifo(tinta[f]) < dr.PEDACOS_DE_GLIFO_DE_ESCRITA:
            continue
        m[f] = True
    return m


def main(numeros):
    pasta = next(p for p in (TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
    projeto = projetos.carregar_estado(projetos.ler_resumo(pasta))
    dpi = int(getattr(projeto, "qualidade_dpi", 300) or 300)
    doc = abrir_pdf(projeto.caminho_entrada)
    res = {"dpi": dpi}
    for n in numeros:
        pg = projeto.paginas[n - 1]
        folha = projeto.folhas[pg.folha]
        prep = pipeline.preparar_metade(pagina_para_array(doc, folha.indice, dpi), folha, pg, projeto, dpi=dpi)
        h, w = prep.shape[:2]
        detector, opcoes = pipeline.escolha_da_gravura(projeto, pg)
        ESPIA.clear()
        sel = dr.detectar(prep, detector_de_gravura=detector, opcoes_da_gravura=opcoes, dpi=dpi,
                          dpi_do_scan=dpi_real_da_pagina(doc, folha.indice))
        g_st = ESPIA.get("gravura_st")
        achados = ESPIA.get("achados") or []
        cor = dr._tres_canais_ou_cinza(prep)
        tinta = dr.mascara_de_tinta(cor)
        texto = caixas(achados, dr.CLASSES_DE_LETRA, h, w)
        escrita = caixas(achados, dr.CLASSES_DE_LETRA, h, w, so_escrita=True, tinta=tinta)
        g = sel.mascara(h, w, GRAVURA)
        le = sel.mascara(h, w, LETRA)
        pa = sel.mascara(h, w, PAPEL)
        guardada = pg.obter_selecao()
        gg = guardada.mascara(h, w, GRAVURA)
        lg = guardada.mascara(h, w, LETRA)
        st = g_st if g_st is not None else np.zeros((h, w), bool)
        dentro = st.sum() or 1
        info = {
            "folha": folha.indice + 1, "metade": pg.metade, "tamanho": [w, h], "detector": detector,
            "caixas_do_leitor": [{"classe": a.classe, "caixa": [round(c, 3) for c in a.caixa],
                                  "certeza": round(float(getattr(a, "confianca", 0) or 0), 2)} for a in achados],
            "fracao_da_pagina": {"gravura_scantailor": round(float(st.mean()), 4),
                                 "gravura_final": round(float(g.mean()), 4),
                                 "letra_final": round(float(le.mean()), 4),
                                 "papel_final": round(float(pa.mean()), 4),
                                 "caixas_de_texto": round(float(texto.mean()), 4),
                                 "escrita_certa": round(float(escrita.mean()), 4)},
            "dentro_da_pintura_do_scantailor": {
                "virou_letra": round(float((st & le).sum() / dentro), 4),
                "virou_letra_por_escrita_certa": round(float((st & le & escrita).sum() / dentro), 4),
                "virou_papel": round(float((st & pa).sum() / dentro), 4)},
            "letra_fora_da_pintura_mas_dentro_do_contorno": None,
            "igual_a_guardada": {"gravura": round(float((g == gg).mean()), 4),
                                 "letra": round(float((le == lg).mean()), 4)},
        }
        res[f"p{n}"] = info
        cv2.imwrite(str(SAI / f"p{n}-a-preparada.jpg"), prep, [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(str(SAI / f"p{n}-b-scantailor.jpg"), pintar(prep, [(st, (60, 200, 60))]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(str(SAI / f"p{n}-c-caixas-de-texto.jpg"),
                    pintar(prep, [(texto & ~escrita, (0, 200, 255)), (escrita, (40, 40, 230))]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(str(SAI / f"p{n}-d-marcacao-final.jpg"),
                    pintar(prep, [(g, (60, 200, 60)), (le, (230, 120, 30)), (pa, (40, 220, 240))]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        for filtro in ("preto_e_branco", "melhorar", "magico_pro"):
            pg2 = copy.deepcopy(pg)
            pg2.filtro = filtro
            final, _mono = pipeline.renderizar_pagina(doc, projeto, pg2, dpi=dpi)
            cv2.imwrite(str(SAI / f"p{n}-e-{filtro}.png"), final)
    (AQUI / "decompor_marcacao.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [14, 8])
