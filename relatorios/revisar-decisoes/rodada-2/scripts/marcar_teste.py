"""Rodada 2: o que acontece quando a pessoa marca uma area a mao na aba Marcar
(retangulo de "gravura ou foto" ou de "papel"), pelo caminho do programa.

Como: a pagina e aberta e desenhada por core.pipeline.renderizar_pagina, como
no rodar.py; so a marcacao que o programa usa (core.pipeline.garantir_selecao)
ganha, por cima da achada sozinha, um retangulo feito "a mao" (origem MAO), do
mesmo jeito que a aba Marcar acrescenta. Nada do programa e mudado (a troca e
so dentro deste processo).

Uso: python marcar_teste.py [nome,nome]   (grava <TRABALHO>/marcar/<nome>__<jeito>.jpg)
"""

from __future__ import annotations

import copy

import cv2

import comum

# nome: (pagina, tipo, operacao, retangulo em fracao da pagina preparada)
# operacao: "somar" (o normal) ou "subtrair" (o botao "tirar" da barra)
TESTES = {
    "graduale588-S-gravura": ("graduale_p588", "gravura", "somar", (0.07, 0.285, 0.34, 0.475)),
    "marial454-remendo-papel": ("marial_p454", "papel", "somar", (0.0, 0.25, 0.20, 0.62)),
    "marial454-remendo-tirar": ("marial_p454", "gravura", "subtrair", (0.0, 0.17, 0.21, 0.63)),
    "marial454-remendo-letra": ("marial_p454", "letra", "somar", (0.0, 0.25, 0.20, 0.62)),
}


def main() -> None:
    from core import misto
    from core import pipeline as P
    from core import selecao as S
    from core.filtros import PRETO_E_BRANCO

    destino = comum.TRABALHO / "marcar"
    destino.mkdir(parents=True, exist_ok=True)
    original = P.garantir_selecao
    extra: list = []

    def com_marca(*a, **k):
        sel = original(*a, **k)
        if not extra:
            return sel
        sel2 = copy.deepcopy(sel) if sel is not None else S.Selecao()
        for r in extra:
            sel2.acrescentar(r)
        return sel2

    P.garantir_selecao = com_marca
    import sys
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for nome, (pid, tipo, operacao, (x0, y0, x1, y1)) in TESTES.items():
        if so and nome not in so:
            continue
        doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
        try:
            pagina = projeto.paginas[0]
            for marcado in (False, True):
                extra.clear()
                if marcado:
                    extra.append(S.retangulo(x0, y0, x1, y1, tipo=tipo, origem=S.MAO))
                    extra[-1].operacao = operacao
                for jeito, so_letras in (("pb", False), ("a", True)):
                    projeto.misto_so_as_letras = so_letras
                    projeto.misto_fora_do_texto = misto.FORA_REDE
                    img, _m = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                    sufixo = "marcado" if marcado else "sem"
                    comum.gravar_jpg(destino / f"{nome}__{jeito}__{sufixo}.jpg", img, lado=4000,
                                     qualidade=94)
                    print(nome, jeito, sufixo, img.shape, flush=True)
        finally:
            doc.close()


if __name__ == "__main__":
    main()
