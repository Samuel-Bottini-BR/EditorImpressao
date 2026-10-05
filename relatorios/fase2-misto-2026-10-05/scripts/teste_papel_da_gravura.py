"""Teste de bancada: o papel de dentro da gravura de traco no Misto.

Compara, nas paginas pedidas, duas contas para a gravura de traco: (A) a da
decoracao (core.filtros._com_a_decoracao, papel pela cor do papel da PAGINA)
e (B) a da propria gravura (core.filtros._so_o_papel_da_gravura, papel pela
cor do papel ENTRE OS TRACOS, a conta feita para o retrato do Palatino 5).
Grava teste-papel/<pagina>.jpg (A | B, inteira e ampliada). So para decidir;
nada aqui vai para o programa.
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

import comum


def main() -> None:
    sys.path.insert(0, str(comum.RAIZ))
    from core import filtros as F
    from core.filtros import PRETO_E_BRANCO
    from core.selecao import GRAVURA

    for pid in sys.argv[1].split(","):
        doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
        try:
            img, sel = comum.imagem_preparada(doc, projeto, projeto.paginas[0])
        finally:
            doc.close()
        img3 = F._tres_canais(img)
        a, l = img3.shape[:2]
        peso = sel.peso(a, l, GRAVURA)
        base = F._tres_canais(F.filtro_preto_e_branco(img)).copy()
        rot, foto, dec, ref = F._tipos_das_zonas(img3, peso)
        print(pid, "zonas", len(foto) - 1, "foto", int(foto[1:].sum()), "decoracao", int(dec[1:].sum()))
        A = F._com_a_decoracao(base.copy(), img3, peso, ref or F._referencia_do_papel(img3, peso > 0))
        tratada = img3.copy()
        n, r2, st, _ = cv2.connectedComponentsWithStats((peso > 0).astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, w, h = st[i, :4]
            pedaco = np.ascontiguousarray(img3[y:y + h, x:x + w])
            tratada[y:y + h, x:x + w] = F._so_o_papel_da_gravura(pedaco, pedaco.copy())
        B = F._misturar(base.copy(), tratada, peso)
        partes = [comum.reduzir(A, 1100), comum.reduzir(B, 1100)]
        comum.gravar_jpg(comum.PASTA / "teste-papel" / f"{pid}.jpg", np.hstack(partes), lado=2200)
        y0, x0 = int(a * 0.35), int(l * 0.3)
        recortes = [x[y0:y0 + a // 4, x0:x0 + l // 3] for x in (img3, A, B)]
        comum.gravar_jpg(comum.PASTA / "teste-papel" / f"{pid}-detalhe.jpg", np.hstack(recortes), lado=2400)


if __name__ == "__main__":
    main()
