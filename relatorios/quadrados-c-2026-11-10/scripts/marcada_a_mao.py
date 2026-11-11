"""Pagina com a gravura marcada A MAO (aba Marcar) antes de escolher o filtro: o que sai com o codigo
desta copia. Pedido da gerente: "Nao mude o que sai [...] nas que ja tem gravura marcada a mao".
Uso: python marcada_a_mao.py <saida> <livro.pdf> <pagina> <x0,y0,x1,y1> [filtros...]"""
import sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reproduzir as R  # noqa
import cv2  # noqa
from core import etapas, pipeline  # noqa
from core.pdf_io import abrir_pdf  # noqa
from core.selecao import GRAVURA, Selecao, retangulo  # noqa

saida = Path(sys.argv[1]); saida.mkdir(parents=True, exist_ok=True)
pdf, numero = sys.argv[2], int(sys.argv[3])
caixa = [float(v) for v in sys.argv[4].split(",")]
for v in sys.argv[5:] or ["melhorar_forte_respeitar", "magico_fraco_respeitar"]:
    projeto = R.livro_novo(pdf)
    p, pag = R.preparar(projeto, numero - 1, v)
    sel = Selecao(); sel.acrescentar(retangulo(*caixa, tipo=GRAVURA))
    pag.guardar_selecao(sel)
    etapas.marcar_mexida_a_mao(pag, etapas.MARCAR)
    doc = abrir_pdf(pdf)
    try:
        img, _ = pipeline._pagina_pronta(p, doc, p.folhas[pag.folha], pag, pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    cv2.imwrite(str(saida / f"mao_{v}.png"), img)
    print(v, [(r.get("tipo"), r.get("origem")) for r in (pag.selecao or [])], flush=True)
