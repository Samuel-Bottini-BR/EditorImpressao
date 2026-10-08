"""Rodada 4: o "texto falhado nos dois jeitos" (Camoes 27 e 104, Egenloff 3) se
conserta com a "Forca do preto" mais forte? Roda o Preto e branco do programa
(core.filtros.filtro_preto_e_branco, o mesmo que a aba Filtro usa) na pagina
preparada que o rodar.py gravou (original a 4000 px), com a forca de fabrica
(50) e mais forte (70 e 85), e grava <TRABALHO>/forca/<base>__f<forca>.png.
Ressalva: a pagina e o JPEG de 4000 px (qualidade 94), nao o PDF.
Uso: python forca_teste.py"""
import cv2

import comum
from sinais4 import pasta_de

BASES = ["camoes_p027__inteira", "camoes_p104__inteira", "egenloff_p003__inteira"]
FORCAS = [50, 70, 85]


def main() -> None:
    from core import filtros as F

    destino = comum.TRABALHO / "forca"
    destino.mkdir(parents=True, exist_ok=True)
    for b in BASES:
        img = cv2.imread(str(pasta_de(b) / f"{b}__original.jpg"))
        for f in FORCAS:
            pb = F.filtro_preto_e_branco(img, forca=f, despeckle="desligado")
            cv2.imwrite(str(destino / f"{b}__f{f}.png"), pb)
            print(b, f, round(float((pb < 128).mean()), 4), flush=True)


if __name__ == "__main__":
    main()
