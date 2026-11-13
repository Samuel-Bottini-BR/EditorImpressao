"""Paginas soltas (gabarito do assunto, Horas 47, Escola 13 e 97/119), livro novo, filtro escolhido a
mao, "Respeitar" marcada, pelo corpo do PDF (core.pipeline._pagina_pronta, 300 DPI), com o codigo da
copia em que este arquivo esta (reproduzir.RAIZ). Grava a pagina pronta (JPG 92) e quatro medidas.
Uso: python paginas_soltas.py <saida> <lista.json: [[pdf, pagina, nome], ...]> [variantes...]"""
import json, sys, time
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reproduzir as R  # noqa
import cv2, numpy as np  # noqa
from core import pipeline  # noqa
from core import filtros as F  # noqa
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa
import varrer  # noqa


def medidas(orig, img):
    pct, blocos, _ = varrer.medir(orig, img)
    cinza = F._para_cinza(orig).astype(np.float32)
    nivel = float(np.percentile(cinza[::4, ::4], F.BRANCO_PERCENTIL))
    s = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    branco = (s >= 250).all(axis=2)
    h, w = cinza.shape; mh, mw = int(0.06 * h), int(0.06 * w)
    miolo = np.zeros_like(branco); miolo[mh:-mh, mw:-mw] = True
    papel = (cinza >= 0.80 * nivel) & miolo          # papel e mancha do verso clara
    tinta = (cinza < 0.50 * nivel) & miolo           # a tinta das letras e tracos
    hsv = cv2.cvtColor(s, cv2.COLOR_BGR2HSV)
    return {"branco_em_pintura_pct": pct, "blocos": blocos,
            "papel_branco_pct": round(100 * float(branco[papel].mean()), 2) if papel.any() else None,
            "papel_saturacao_media": round(float(hsv[:, :, 1][papel].mean()), 2) if papel.any() else None,
            "tinta_apagada_pct": round(100 * float((s.min(axis=2) >= 230)[tinta].mean()), 3) if tinta.any() else None}


saida = Path(sys.argv[1]); saida.mkdir(parents=True, exist_ok=True)
lista = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
variantes = sys.argv[3:] or ["melhorar_forte_respeitar", "magico_fraco_respeitar"]
arq = saida / "medidas.json"
res = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
for pdf, numero, nome in lista:
    projeto = R.livro_novo(pdf)
    doc = abrir_pdf(pdf)
    try:
        for v in variantes:
            if f"{nome}|{v}" in res:
                continue
            t = time.monotonic()
            p, pag = R.preparar(projeto, numero - 1, v)
            img, _ = pipeline._pagina_pronta(p, doc, p.folhas[pag.folha], pag, pipeline._FolhaDaVez(), 0)
            seg = round(time.monotonic() - t, 1)
            orig = pagina_para_array(doc, p.folhas[pag.folha].indice, dpi=p.qualidade_dpi)
            if orig.shape[:2] != img.shape[:2]:
                orig = cv2.resize(orig, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
            if not (saida / f"{nome}_original.jpg").exists():
                cv2.imwrite(str(saida / f"{nome}_original.jpg"), orig, [cv2.IMWRITE_JPEG_QUALITY, 92])
            cv2.imwrite(str(saida / f"{nome}_{v}.png"), img)
            m = medidas(orig, img); m["segundos"] = seg
            m["gravuras"] = sum(1 for r in (pag.selecao or []) if isinstance(r, dict) and r.get("tipo") == "gravura")
            res[f"{nome}|{v}"] = m
            print(nome, v, m, flush=True)
            arq.write_text(json.dumps(res, indent=1), encoding="utf-8")
    finally:
        doc.close()
