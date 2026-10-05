"""Monta o livro de teste (copia de 4 paginas do gabarito, somente leitura)."""
import fitz
from pathlib import Path

G = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
D = Path(__file__).parent / "dados" / "livros" / "livro-teste.pdf"
saida = fitz.open()
for nome in ("boecio_p003", "boecio_p007", "boecio_p008", "boecio_p022"):
    with fitz.open(G / f"{nome}.pdf") as doc:
        saida.insert_pdf(doc)
saida.save(D)
print(D, saida.page_count, [tuple(round(x) for x in p.rect[2:]) for p in saida])
