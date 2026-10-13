"""Setas do teclado: trocam de pagina ou ficam presas no que esta com o foco? (janela de teste, nunca ativa)"""
import time, v
P = v.P
QUEM = ("(lambda w: 'tira' if w is tc.tira.rolagem else ('coluna dos paineis' if type(w).__name__ == 'ColunaDePaineis' else "
        "(type(w).__name__ + ':' + (w.text() if hasattr(w, 'text') else ''))[:40]) if w is not None else None)(jp.focusWidget())")
ROL = "tc.tira.rolagem.horizontalScrollBar().value()"
def seta(nome):
    p0, r0 = v.s("tc.indice_pagina+1"), v.s(ROL)
    P.tecla(0x27); time.sleep(1.5)
    print(f"  {nome}: foco em [{v.s(QUEM)}]; seta direita: pagina {p0} -> {v.s('tc.indice_pagina+1')}; rolagem da tira {r0} -> {v.s(ROL)}")
print("codigo:", P.VERIF_RAIZ[-22:])
v.ir_pagina(5); time.sleep(1.5); seta("depois de clicar numa miniatura da tira")
v.aba("Filtro", espera=1.0); seta("depois de clicar na aba Filtro")
v.clicar(">", classe="QPushButton", espera=1.5); seta("depois de clicar no botao >")
x, y, vis, ativo = v.g.geo("tc.cartoes['original']"); P.clicar_em(P.principal(), int(x), int(y) + 60); time.sleep(1.5); seta("depois de clicar no cartao Original")
v.ctrl_z()
