"""Imagens do conserto C (D-668) no modelo de print do girar (CLAUDE.md §10): resumo primeiro; faixa
azul "ANTES do conserto (hoje)" e verde "DEPOIS do conserto C" (e uma cinza com o original, de
referencia); as MESMAS paginas e o MESMO recorte ampliado em todas as faixas; o que olhar circulado
em vermelho.

    python montar_c.py <pasta antes> <pasta depois> <pasta de saida>

As pastas sao as de paginas_soltas.py (o corpo do PDF, 300 DPI, livro novo, filtro escolhido a mao):
<nome>_original.jpg e <nome>_<variante>.png. "Antes" = o codigo do obra-2026-10-26 (58806f81);
"depois" = o ramo quadrados-c-2026-11-10."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, r"D:\programas\EditorImpressao\docs\plano\central\modelo-de-print")
import montar_provas_exemplo as M  # noqa: E402

AZUL, VERDE, CINZA, PRETO = (60, 90, 150), (25, 130, 60), (110, 110, 110), (40, 40, 40)

# (nome, rotulo, recorte em fracao da pagina, alvos [(x0, y0, x1, y1) em fracao do recorte])
AGUA = ("escola_p013", "Escola 13 · água", (0.12, 0.13, 0.62, 0.36), [(0.08, 0.30, 0.95, 0.95)])
CEU = ("escola_p097", "Escola 97 · céu", (0.47, 0.06, 0.97, 0.30), [(0.0, 0.0, 0.45, 0.75)])
VIVIA = ("escola_p013", "Escola 13 · \"Vivia\"", (0.075, 0.529, 0.215, 0.566),
         [(0.47, 0.02, 0.56, 0.50), (0.61, 0.02, 0.70, 0.50), (0.78, 0.52, 0.87, 1.0)])
HORAS = ("horas_p047", "Horas 47 · prédio", (0.30, 0.04, 0.72, 0.22), [(0.30, 0.05, 0.85, 0.75)])
CELULAS = (AGUA, CEU, VIVIA, HORAS)


def _abrir(pasta: Path, nome: str, variante: str | None) -> Image.Image:
    arq = pasta / (f"{nome}_original.jpg" if variante is None else f"{nome}_{variante}.png")
    return Image.open(arq).convert("RGB")


def _recorte(img: Image.Image, c) -> Image.Image:
    w, h = img.size
    return img.crop((round(c[0] * w), round(c[1] * h), round(c[2] * w), round(c[3] * h)))


def _linha(imgs, celulas, circular: bool, caixa_l: int | None = None,
           caixa_a: int | None = None) -> Image.Image:
    """Uma linha de recortes ampliados, com o nome em vermelho em cima; com `circular`, o alvo de
    cada recorte (o que olhar) num circulo vermelho."""
    caixa_l = caixa_l or min(440, 1480 // len(imgs) - 40)
    caixa_a = caixa_a or round(caixa_l * 0.76)
    f = M._fonte(24, True)
    topo, margem = 40, 20
    cel_l, cel_a = caixa_l + 2 * margem, caixa_a + topo + 2 * margem
    img = Image.new("RGB", (cel_l * len(imgs), cel_a), M.FUNDO)
    d = ImageDraw.Draw(img)
    for n, (r, cel) in enumerate(zip(imgs, celulas)):
        x0 = n * cel_l
        d.text((x0 + cel_l / 2, 6), cel[1], fill=M.VERMELHO, font=f, anchor="mt")
        p = M._caber(r, caixa_l, caixa_a)
        px, py = x0 + (cel_l - p.width) // 2, topo + margem + (caixa_a - p.height) // 2
        img.paste(p, (px, py))
        d.rectangle([px - 1, py - 1, px + p.width, py + p.height], outline=(150, 150, 150), width=1)
        if circular:
            for a in cel[3]:
                d.ellipse([px + a[0] * p.width - 6, py + a[1] * p.height - 6,
                           px + a[2] * p.width + 6, py + a[3] * p.height + 6],
                          outline=M.VERMELHO, width=5)
    return img


def _faixas(antes: Path, depois: Path, variante: str, celulas, legenda_antes: str,
            legenda_depois: str) -> list[Image.Image]:
    def linha(pasta, var, circular):
        return _linha([_recorte(_abrir(pasta, c[0], var), c[2]) for c in celulas], celulas, circular)

    return [
        M._empilhar([M._cabeca("Original (como veio no PDF)", CINZA, "Para comparar."),
                     linha(antes, None, False)], espaco=4),
        M._empilhar([M._cabeca("ANTES do conserto (hoje)", AZUL, legenda_antes),
                     linha(antes, variante, True)], espaco=4),
        M._empilhar([M._cabeca("DEPOIS do conserto C", VERDE, legenda_depois),
                     linha(depois, variante, True)], espaco=4),
    ]


def _pagina_inteira_e_recortes(pasta: Path, variante: str | None, alvos: bool) -> Image.Image:
    """[página 13 inteira | água | "Vivia"], com o circulo vermelho no lugar a olhar."""
    pag = _abrir(pasta, "escola_p013", variante)
    w, h = pag.size
    inteira = pag.copy()
    d = ImageDraw.Draw(inteira)
    for c in (AGUA[2], VIVIA[2]):
        d.rectangle([c[0] * w, c[1] * h, c[2] * w, c[3] * h], outline=M.VERMELHO, width=8)
    celulas = (("escola_p013", "página 13", (0, 0, 1, 1), []), AGUA, VIVIA)
    imgs = [inteira, _recorte(pag, AGUA[2]), _recorte(pag, VIVIA[2])]
    return _linha(imgs, celulas, alvos, caixa_l=440, caixa_a=330)


def resumo(antes: Path, depois: Path, saida: Path, legendas: dict) -> None:
    partes = [
        M._cabeca("Quadrados brancos — resumo", PRETO,
                  "Na escola de Jesus, página 13. Livro novo; dividida, endireitada e cortada como o "
                  "programa faz; Melhorar \"bem forte\" escolhido à mão, \"Respeitar as gravuras "
                  "achadas\" marcada. Como sai no PDF."),
        M._empilhar([M._cabeca("ANTES do conserto (hoje)", AZUL,
                               "Buracos brancos em quadrados na água; o \"i\" e o \"t\" quebrados."),
                     _pagina_inteira_e_recortes(antes, "melhorar_forte_respeitar", True)], espaco=4),
        M._empilhar([M._cabeca("DEPOIS do conserto C", VERDE,
                               "A água inteira; \"Vivia\" com o \"i\" inteiro."),
                     _pagina_inteira_e_recortes(depois, "melhorar_forte_respeitar", True)], espaco=4),
    ]
    M._salvar(M._empilhar(partes, espaco=10), saida / "1-resumo-pagina-13.png", legendas,
              "Resumo: página 13, Melhorar, antes e depois do conserto C.")


def filtro(antes: Path, depois: Path, saida: Path, legendas: dict, variante: str, nome: str,
           arquivo: str) -> None:
    partes = [M._cabeca(f"{nome} — antes e depois do conserto C", PRETO,
                        f"Livro novo; dividida, endireitada e cortada; {nome} escolhido à mão, "
                        "\"Respeitar as gravuras achadas\" marcada. Como sai no PDF (300 DPI). Os "
                        "mesmos quatro pedaços ampliados em todas as faixas.")]
    partes += _faixas(antes, depois, variante, CELULAS,
                      "Buracos brancos na água, no céu e no prédio; o \"i\" e o \"t\" quebrados.",
                      "Água, céu, prédio e letras inteiros.")
    M._salvar(M._empilhar(partes, espaco=10), saida / arquivo, legendas,
              f"{nome}: Escola 13, Escola 97, \"Vivia\" e Horas 47, antes e depois.")


def print_10(antes: Path, depois: Path, saida: Path, legendas: dict) -> None:
    celulas = (AGUA, VIVIA)
    partes = [M._cabeca("Print 10 — \"Respeitar\" desmarcada", PRETO,
                        "Na escola de Jesus, página 13; livro novo; Mágico pro \"bem fraco\" escolhido "
                        "à mão, \"Respeitar as gravuras achadas\" DESMARCADA (nada é procurado). Como "
                        "sai no PDF.")]
    partes += _faixas(antes, depois, "magico_fraco_sem_respeitar", celulas,
                      "Buracos brancos em quadrados na água.",
                      "A água sem os buracos. As letras: como hoje (sem a gravura achada, a letra "
                      "continua com o tratamento da página inteira).")
    M._salvar(M._empilhar(partes, espaco=10), saida / "4-print-10-respeitar-desmarcada.png", legendas,
              "Print 10: Mágico pro com \"Respeitar\" desmarcada, antes e depois.")


def mancha(antes: Path, depois: Path, saida: Path, legendas: dict) -> None:
    celulas = (("boecio_p033", "Boécio 33 · mancha do verso", (0.10, 0.10, 0.90, 0.45), []),
               ("boecio_p003", "Boécio 3 · xilogravura", (0.10, 0.10, 0.90, 0.60), []),
               ("palatino_p005", "Palatino 5 · retrato", (0.33, 0.40, 0.63, 0.60), []),
               ("escola_p035", "Escola 35 · anjo", (0.15, 0.10, 0.85, 0.50), []))
    partes = [M._cabeca("O que já estava bom continua — Melhorar", PRETO,
                        "Páginas do gabarito (mancha do verso, xilogravura, retrato, pintura do anjo). "
                        "Livro novo; dividida, endireitada e cortada; Melhorar \"bem forte\" escolhido à "
                        "mão, \"Respeitar\" marcada. Como sai no PDF.")]
    partes += _faixas(antes, depois, "melhorar_forte_respeitar", celulas, "Como sai hoje.",
                      "Depois do conserto: a mancha do verso some igual; com a gravura achada, o "
                      "retrato e a xilogravura recebem o tratamento de gravura.")
    M._salvar(M._empilhar(partes, espaco=10), saida / "5-o-que-ja-estava-bom.png", legendas,
              "Mancha do verso, xilogravura, retrato e anjo: antes e depois.")


def main() -> None:
    antes, depois, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    saida.mkdir(parents=True, exist_ok=True)
    legendas: dict = {}
    resumo(antes, depois, saida, legendas)
    filtro(antes, depois, saida, legendas, "melhorar_forte_respeitar", "Melhorar \"bem forte\"",
           "2-melhorar.png")
    filtro(antes, depois, saida, legendas, "magico_fraco_respeitar", "Mágico pro \"bem fraco\"",
           "3-magico-pro.png")
    print_10(antes, depois, saida, legendas)
    mancha(antes, depois, saida, legendas)
    (saida / "legendas.json").write_text(json.dumps(legendas, indent=1, ensure_ascii=False),
                                         encoding="utf-8")


if __name__ == "__main__":
    main()
