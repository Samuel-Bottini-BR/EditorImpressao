"""D-113 (d212-1): a página curva com a moldura escura do scanner desentorta?

Usa a página de teste do verificador do 2.12 (Marial 41 encurvada por ele, com a
moldura do scanner: sint/curvada2.png, copiada para relatorios/conferir/
obra-etapa10a/sint/, fora do git). Livro novo de fábrica, desentortar automático,
filtro Original; mede a "nitidez das linhas" (a conta do verificador do 2.12:
desvio da projeção da tinta / média; quanto maior, mais retas) no terço da
lombada e na página toda, desligado e ligado. Grava as imagens.
USO: python curvada_com_moldura.py <raiz do código> <saida.png>
"""
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RAIZ))
import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402

AQUI = Path(__file__).resolve().parents[3] / "relatorios" / "conferir" / "obra-etapa10a"


def nitidez(img, faixa):
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, m = cv2.threshold(cv2.GaussianBlur(cinza, (3, 3), 0), 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    h, w = m.shape
    proj = (m[int(h * .06):int(h * .94), int(w * faixa[0]):int(w * faixa[1])] > 0).sum(axis=1).astype(float)
    return float(proj.std() / max(1e-6, proj.mean()))


def main():
    from core import desentortar_scantailor as ds
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import Projeto

    png = AQUI / "sint" / "curvada2.png"
    img = cv2.imread(str(png))
    pdf = AQUI / "tmp" / "curvada2.pdf"
    ok, jpg = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    doc = fitz.open()
    pg = doc.new_page(width=img.shape[1] * 72 / 300, height=img.shape[0] * 72 / 300)
    pg.insert_image(pg.rect, stream=jpg.tobytes())
    doc.save(str(pdf))
    doc.close()
    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome="curvada2"))
    doc = abrir_pdf(str(pdf))
    pagina = projeto.paginas_ativas[0]
    folha = projeto.folhas[pagina.folha]
    folha_img = pagina_para_array(doc, 0, dpi=300)
    doc.close()
    hoje = pipeline.preparar_metade(folha_img, folha, pagina, projeto, dpi=300)
    pagina.desentortar = ds.AUTOMATICO
    ligado = pipeline.preparar_metade(folha_img, folha, pagina, projeto, dpi=300)
    for nome, im in (("desligado", hoje), ("ligado", ligado)):
        print(nome, "esq", round(nitidez(im, (0, .33)), 3), "dir", round(nitidez(im, (.67, 1)), 3),
              "toda", round(nitidez(im, (0, 1)), 3), "aviso saiu sem:", pagina.alertas)
    a = cv2.resize(hoje, None, fx=.3, fy=.3)
    b = cv2.resize(ligado, (a.shape[1], a.shape[0]))
    cv2.imwrite(sys.argv[2], np.hstack([a, np.full((a.shape[0], 10, 3), 128, np.uint8), b]))


main()
