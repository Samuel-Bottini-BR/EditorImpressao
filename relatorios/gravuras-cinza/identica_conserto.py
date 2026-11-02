"""Conserto de 02/11/2026 (o cinza sem o "Respeitar"): prova entre commits, sem janela.

Desenha páginas do "Na escola de Jesus" com a marcação que o "Gravuras e fotos" deixou na pasta de
dados de teste dele (lida, nunca gravada: D:/programas/EditorImpressao-arquivos/dados-teste-
rodada-de-consertos), com o código da pasta que vem em argv[1], e imprime o md5 de cada desenho:
  - "Gravuras em tons de cinza" DESMARCADA, "Respeitar" ligada e desligada, nos quatro filtros
    (tem de dar o mesmo md5 antes e depois do conserto: "desmarcada, nada muda");
  - Preto e branco com a caixinha MARCADA, "Respeitar" ligada e desligada (depois do conserto os
    dois md5 têm de ser iguais; antes, o desligado era o preto e branco chapado).
Sem "Só as letras" na página (a pergunta 1 fica de fora). Cada página é desenhada uma vez antes
(a primeira guarda as medidas). Uso: python identica_conserto.py <pasta do código> > saída.txt
"""
import copy
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
CODIGO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(CODIGO))
PROJETO = Path(r"D:/programas/EditorImpressao-arquivos/dados-teste-rodada-de-consertos/EditorImpressao"
               r"/projetos/Na escola de Jesus - Catecismo explicado com imagens/projeto.json")
PAGINAS = (0, 8, 12, 18, 44)
FILTROS = ("original", "preto_e_branco", "melhorar", "magico_pro")


def main() -> int:
    import cv2

    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from modelos import Projeto

    projeto = Projeto.de_dicionario(json.loads(PROJETO.read_text(encoding="utf-8")))
    print("codigo:", CODIGO.name)
    doc = abrir_pdf(projeto.caminho_entrada)

    def md5(pagina, **campos):
        p = copy.deepcopy(pagina)
        for k, v in campos.items():
            setattr(p, k, v)
        img, _ = renderizar_pagina(doc, copy.deepcopy(projeto), p, dpi=110)
        cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        meio = float(((cinza > 10) & (cinza < 245)).mean())
        return hashlib.md5(img.tobytes()).hexdigest(), meio

    try:
        for indice in PAGINAS:
            pagina = copy.deepcopy(projeto.paginas[indice])
            pagina.misto_so_as_letras = False
            md5(pagina)
            for cinza in (False, True):
                for respeitar in (True, False):
                    for filtro in (FILTROS if not cinza else ("preto_e_branco",)):
                        valor, meio = md5(pagina, filtro=filtro, respeitar_gravuras_achadas=respeitar,
                                          gravuras_em_tons_de_cinza=cinza)
                        print(f"pagina {indice + 1:3d} cinza={'marcada  ' if cinza else 'desmarcada'} "
                              f"respeitar={'sim' if respeitar else 'nao'} {filtro:15s} "
                              f"md5={valor} tons_do_meio={meio:.1%}")
    finally:
        doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
