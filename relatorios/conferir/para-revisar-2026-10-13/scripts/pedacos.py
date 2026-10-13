"""Tira pedacos pequenos dos livros (so leitura nos originais) para os testes de processar ate o fim."""
import sys, fitz
from pathlib import Path
from livros import LIVROS
DEST = Path(__file__).resolve().parent.parent / "trabalho" / "livros"
PEDACOS = {"antiphonal_44a49": ("antiphonal", 44, 49), "graduale_219a225": ("graduale", 219, 225),
           "egenloff_1a14": ("egenloff", 1, 14)}
for nome, (livro, de, ate) in PEDACOS.items():
    destino = DEST / f"{nome}.pdf"
    if destino.exists():
        continue
    with fitz.open(LIVROS[livro]) as origem, fitz.open() as novo:
        novo.insert_pdf(origem, from_page=de - 1, to_page=ate - 1)
        novo.save(destino)
    print(destino.name, destino.stat().st_size)
