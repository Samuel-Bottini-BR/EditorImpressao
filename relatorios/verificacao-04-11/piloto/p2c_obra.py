"""Mesmo teste do lado do antes/depois, no codigo da OBRA (sem o mover-lado), so com o Filtro."""
import comum as C
from comum import anotar, p
import p2b_antes_depois as B
WT = r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\obra"
j, porteiro = C.abrir(WT, "2c-antes-depois-na-obra", "Giovambattista Palatino cittadino romano.pdf")
t = j.tela_conferir
C.ir_pagina(j, 9)
t._escolher_filtro("preto_e_branco"); C.esperar_previa(j)
t.escolher_ferramenta("filtros"); C.esperar_previa(j)
C.base.clique(j, t.botao_antes_depois); C.base.esperar(3)
import time
v = t.vista_antes_depois; t0 = time.time()
while time.time() - t0 < 60 and (v.antes is None or v.depois is None):
    C.base.esperar(0.5)
C.base.esperar(3)
anotar("estado", {"comparando": t.comparando, "antes": v.antes is not None, "depois": v.depois is not None, "aviso": getattr(v, "aviso", None), "na tela": type(t.vista_da_pagina.currentWidget()).__name__})
anotar("OBRA, Filtro com antes/depois: cor de cada lado (0 = preto e branco)", B.lados(j))
p(j, "obra-filtro-antes-depois")
C.fechar(j)
