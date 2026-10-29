"""D-586, prova "ligada = como hoje, byte a byte" entre commits (sem janela).

Desenha páginas do "Na escola de Jesus" (cópia do projeto de teste em <worktree>/_tmp/dados,
depois do Automático: endireitada, cortada, "Limpar a folha", "Gravuras e fotos" com a marcação
guardada) nos quatro filtros, com o código do commit cuja pasta vem em argv[1], e imprime o md5
de cada desenho. Rodado no 2db002e (antes da caixinha) e neste ramo (caixinha ligada, que é o
padrão de todo projeto antigo): os md5 têm de ser iguais. Cada página é desenhada duas vezes e
vale a segunda (a primeira guarda as medidas da página; ver as Ressalvas do ONDE-PAREI); a
primeira também sai, para mostrar que isso acontece igual nos dois commits.
Uso: python identica_entre_commits.py <pasta do código> > saída.txt
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
PROJETO = (Path(__file__).resolve().parents[2] / "_tmp" / "dados" / "EditorImpressao" / "projetos"
           / "Na escola de Jesus - Catecismo explicado com imagens" / "projeto.json")
PAGINAS = (0, 8, 18, 44)
FILTROS = ("original", "preto_e_branco", "melhorar", "magico_pro")


def main() -> int:
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from modelos import Projeto

    projeto = Projeto.de_dicionario(json.loads(PROJETO.read_text(encoding="utf-8")))
    print("codigo:", CODIGO.name, "| campo novo na pagina:",
          hasattr(projeto.paginas[0], "respeitar_gravuras_achadas"))
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for indice in PAGINAS:
            for filtro in FILTROS:
                pagina = copy.deepcopy(projeto.paginas[indice])
                pagina.filtro = filtro
                md5 = []
                for _vez in range(2):
                    img, _ = renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=110)
                    md5.append(hashlib.md5(img.tobytes()).hexdigest())
                print(f"pagina {indice + 1:3d} {filtro:15s} areas={len(pagina.selecao):2d} "
                      f"primeira={md5[0][:12]} segunda={md5[1][:12]}")
    finally:
        doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
