"""MAQUINA: a mesma pagina medida a 300 DPI de dois jeitos - (a) direto, como o
implementador conferiu as 89 paginas; (b) depois de a previa de 110 DPI ter sido
desenhada no MESMO projeto, como acontece na janela. Diz se os avisos mudam."""
import sys, json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parents[2]
sys.path.insert(0, str(RAIZ)); sys.path.insert(0, str(RAIZ / "relatorios" / "para-revisar-impl"))
from pasta_de_dados_dos_scripts import isolar_pasta_de_dados
isolar_pasta_de_dados("verif-para-revisar-ordem")
import conferir_89
from core import misto, pipeline as P
from core.filtros import PRETO_E_BRANCO
from core.pdf_io import abrir_pdf
from modelos import Projeto
sys.stdout.reconfigure(encoding="utf-8")
def projeto_de(caminho):
    pr = Projeto(caminho_entrada=caminho, nome="x"); pr.filtro_padrao = PRETO_E_BRANCO
    pr = P.analisar_projeto(pr); pr.misto_so_as_letras = True; pr.misto_fora_do_texto = misto.FORA_REDE
    pr.reforcar_texto_falhado = False
    for p in pr.paginas: p.filtro = PRETO_E_BRANCO
    return pr
for alvo in sys.argv[1:]:
    n = 0
    if ".pdf:" in alvo:
        alvo, k = alvo.rsplit(":", 1); n = int(k) - 1
    caminho = alvo if alvo.endswith(".pdf") else str(conferir_89._pdf_da_pagina(alvo))
    pr = projeto_de(caminho); doc = abrir_pdf(caminho)
    P.renderizar_pagina(doc, pr, pr.paginas[n], dpi=300); direto = sorted(pr.paginas[n].alertas)
    pr = projeto_de(caminho)
    P.renderizar_pagina(doc, pr, pr.paginas[n], dpi=110); na_previa = sorted(pr.paginas[n].alertas)
    P.renderizar_pagina(doc, pr, pr.paginas[n], dpi=300); depois = sorted(pr.paginas[n].alertas)
    doc.close()
    print(f"{Path(caminho).stem[:26]:26s} p{n+1}  direto a 300: {direto} | so a previa 110: {na_previa} | 300 depois da previa: {depois}", flush=True)
