"""Livro de teste do verificador (05/10/2026): copia de paginas do gabarito (so lidas)."""
import fitz
from pathlib import Path

G = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
D = Path(__file__).parent / "dados" / "livros" / "livro-teste.pdf"
NOMES = ("escola_p007", "boecio_p003", "boecio_p007", "boecio_p008", "boecio_p022",
         "escola_p035", "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010")
saida = fitz.open()
for nome in NOMES:
    with fitz.open(G / f"{nome}.pdf") as doc:
        saida.insert_pdf(doc)
saida.save(D)
print(D, saida.page_count, [tuple(round(x) for x in p.rect[2:]) for p in saida])
