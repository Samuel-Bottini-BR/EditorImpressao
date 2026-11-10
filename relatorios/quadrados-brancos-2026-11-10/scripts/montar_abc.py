"""Imagens da comparacao A, B e C (pedido do Samuel, 10/11: "faça um teste com os dois para ver
qual se sai melhor"), no modelo de print: resumo primeiro; uma faixa por situacao (azul Original,
laranja hoje, verde A, roxo B, azul-esverdeado C); as MESMAS quatro paginas e o MESMO recorte
ampliado em todas as faixas; contorno vermelho por fora do recorte.

    python montar_abc.py <pasta com as paginas prontas (comparar_paginas.py)> <pasta de saida>

Arquivos esperados: <nome>_original.jpg e <nome>_<variante>_<hoje|A|B|C>.jpg."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, r"D:\programas\EditorImpressao\docs\plano\central\modelo-de-print")
import montar_provas_exemplo as M  # noqa: E402

AZUL, LARANJA, VERDE, ROXO, TEAL, CINZA = ((60, 90, 150), (190, 90, 10), (25, 130, 60),
                                           (110, 60, 150), (20, 120, 130), (40, 40, 40))
# (nome do arquivo, rotulo, recorte em fracao da pagina)
CELULAS = (
    ("escola_p013", "Escola 13 · água", (0.12, 0.13, 0.62, 0.36)),
    ("escola_p097", "Escola 97 · céu", (0.47, 0.06, 0.97, 0.30)),
    ("escola_p013", "Escola 13 · letras", (0.075, 0.529, 0.215, 0.566)),
    ("palatino_p005", "Palatino 5 · retrato", (0.33, 0.40, 0.63, 0.60)),
)


def _abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def _recorte(img: Image.Image, c) -> Image.Image:
    w, h = img.size
    return img.crop((round(c[0] * w), round(c[1] * h), round(c[2] * w), round(c[3] * h)))


def _linha(imgs: list[Image.Image], rotulos: list[str], caixa_l: int = 330, caixa_a: int = 260) -> Image.Image:
    f = M._fonte(26, True)
    topo, margem = 44, 20
    cel_l, cel_a = caixa_l + 2 * margem, caixa_a + topo + 2 * margem
    img = Image.new("RGB", (cel_l * len(imgs), cel_a), M.FUNDO)
    d = ImageDraw.Draw(img)
    for n, (r, rot) in enumerate(zip(imgs, rotulos)):
        x0 = n * cel_l
        d.text((x0 + cel_l / 2, 6), rot, fill=M.VERMELHO, font=f, anchor="mt")
        p = M._caber(r, caixa_l, caixa_a)
        px, py = x0 + (cel_l - p.width) // 2, topo + margem + (caixa_a - p.height) // 2
        img.paste(p, (px, py))
        d.rounded_rectangle([px - 10, py - 10, px + p.width + 9, py + p.height + 9], radius=16,
                            outline=M.VERMELHO, width=5)
    return img


def figura(pasta: Path, saida: Path, variante: str, nome_filtro: str, arquivo: str, legendas: dict) -> None:
    faixas = (
        ("ORIGINAL", AZUL, "original", "Como veio no PDF."),
        (f"HOJE — {nome_filtro}", LARANJA, "hoje",
         "Buracos brancos na água e no céu; o \"i\" e o \"t\" quebrados; pontinhos brancos no retrato."),
        ("A — a regra \"em volta é papel\"", VERDE, "A",
         "A água volta; o céu claro perto da margem ainda fura; as letras continuam quebradas; o retrato igual a hoje."),
        ("B — procurar a gravura (como a D-659)", ROXO, "B",
         "Água, céu e letras inteiros; o papel entre os traços do retrato fica branco. Só com \"Respeitar\" marcada."),
        ("C — os dois juntos", TEAL, "C",
         "Igual ao B nestas páginas. Com \"Respeitar\" desmarcada (print 10), fica como o A."),
    )
    partes = [M._cabeca(f"Comparação A, B e C — {nome_filtro}", CINZA,
                        "Livro novo, filtro escolhido à mão, como sai no PDF (300 DPI). Os mesmos quatro "
                        "pedaços ampliados em todas as faixas. A, B e C são SIMULAÇÃO: não estão no programa.")]
    for rotulo, cor, s, legenda in faixas:
        imgs = []
        for nome, _rot, rec in CELULAS:
            arq = pasta / (f"{nome}_original.jpg" if s == "original" else f"{nome}_{variante}_{s}.jpg")
            imgs.append(_recorte(_abrir(arq), rec))
        partes.append(M._empilhar([M._cabeca(rotulo, cor, legenda),
                                   _linha(imgs, [c[1] for c in CELULAS])], espaco=4))
    img = M._empilhar(partes, espaco=10)
    M._salvar(img, saida / arquivo, legendas,
              f"Comparação A, B e C no {nome_filtro}: água, céu, letras e retrato, nas cinco situações.")


def main() -> None:
    pasta, saida = Path(sys.argv[1]), Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    arq_leg = saida / "legendas.json"
    legendas = json.loads(arq_leg.read_text(encoding="utf-8")) if arq_leg.is_file() else {}
    figura(pasta, saida, "melhorar_forte_respeitar", "Melhorar \"bem forte\"", "6-comparacao-abc-melhorar.png", legendas)
    figura(pasta, saida, "magico_fraco_respeitar", "Mágico pro \"bem fraco\"", "7-comparacao-abc-magico-pro.png", legendas)
    arq_leg.write_text(json.dumps(legendas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
