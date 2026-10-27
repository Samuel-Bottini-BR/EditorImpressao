"""Desenha dois cortes (antes em azul, depois em vermelho) na página reta do gabarito.
USO: python desenhar_cortes.py antes.json depois.json pasta_saida chave [chave ...]
(chave = 'pid|metade'; só para olhar a diferença, não é a imagem do PDF)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import cv2  # noqa: E402

from core.endireitar import rotacionar  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402

a, b = (json.loads(Path(p).read_text()) for p in sys.argv[1:3])
saida = Path(sys.argv[3])
saida.mkdir(parents=True, exist_ok=True)
for chave in sys.argv[4:]:
    pid = chave.split("|")[0]
    doc = abrir_pdf(rf"D:\programas\EditorImpressao\gabarito\paginas\{pid}.pdf")
    img = rotacionar(pagina_para_array(doc, 0, dpi=150), a[chave][1])
    doc.close()
    h, w = img.shape[:2]
    for (rec, _ang), cor, e in ((a[chave], (255, 0, 0), 5), (b[chave], (0, 0, 255), 2)):
        x, y, rw, rh = rec
        cv2.rectangle(img, (int(x * w), int(y * h)), (int((x + rw) * w), int((y + rh) * h)), cor, e)
    cv2.imwrite(str(saida / (chave.replace("|", "-") + ".jpg")), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
