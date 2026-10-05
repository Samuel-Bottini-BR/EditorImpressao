"""D3: ampliacao de onde o "uma pagina + sobra" do ScanTailor passa a tesoura.

Para as paginas em que o corte automatico do ScanTailor (page_split, modo
automatico) cai perto do conteudo, recorta a regiao em volta da linha de corte
(vermelha) na folha de 300 DPI e grava ampliado. Mostra se a linha passa por
cima de letra. Rodar da raiz do projeto, depois do comparar_d3.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparar_d3 as c  # noqa: E402

# (pagina, qual corte, faixa de altura a mostrar em fracao)
CASOS = [("escola_p007", -1, (0.05, 0.40)), ("escola_p035", 0, (0.50, 0.85)),
         ("escola_p035", -1, (0.50, 0.85)), ("graduale_p221", -1, (0.0, 0.35)),
         ("siebmacher_p009", 0, (0.05, 0.85)), ("opusmajus_p256", 0, (0.25, 0.55))]


def main() -> int:
    fator, _ = c.fator_do_sentido()
    lista = {}
    for nome, qual, (y0, y1) in CASOS:
        if nome not in lista:
            nosso = c.nossa_geometria(nome, {})
            c.TMP.mkdir(parents=True, exist_ok=True)
            arquivo = c.TMP / f"{nome}_300.png"
            cv2.imwrite(str(arquivo), nosso["img"])
            try:
                med = c.ler_saida(c.rodar_exe(str(arquivo), str(c.DPI)))[0]
            finally:
                arquivo.unlink(missing_ok=True)
            lista[nome] = (nosso["img"], med["cortes"])
        img, cortes = lista[nome]
        x1, ya, x2, yb = cortes[qual]
        h, w = img.shape[:2]
        desenho = img.copy()
        cv2.line(desenho, (int(x1), int(ya)), (int(x2), int(yb)), c.VERMELHO, 5, cv2.LINE_AA)
        meio = int((x1 + x2) / 2)
        largura = int(0.18 * w)
        recorte = desenho[int(y0 * h):int(y1 * h), max(0, meio - largura):min(w, meio + largura)]
        escala = 900 / recorte.shape[0]
        recorte = cv2.resize(recorte, (int(recorte.shape[1] * escala), 900), interpolation=cv2.INTER_AREA)
        rotulo = f"{nome}: corte do ScanTailor a {100 * meio / w:.1f}% da largura"
        cv2.imwrite(str(c.IMAGENS / f"corte_st_{nome}_{'esq' if qual == 0 else 'dir'}.jpg"),
                    c._titulo(recorte, rotulo, c.VERMELHO), [cv2.IMWRITE_JPEG_QUALITY, 85])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
