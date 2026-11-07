"""Monta os quadros de antes/depois (relatorios/girar-capa) com o que gerar_antes_depois.py gravou.

    python montar_quadros.py <pasta do código de antes> <pasta do código novo> <pasta de saída> <título do livro>

Um quadro por situação: em cima, o PDF que sai antes do clique; no meio, o PDF que sai depois do
clique com o código de ANTES do conserto; embaixo, com o código NOVO. Cada linha diz por onde a
página passou e com quais opções (CLAUDE.md §4.10). E as fotos da janela (desenhada na memória).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
ALTURA = 260
NUMEROS = [1, 2, 3, 14, 15]


def _fonte(tamanho: int, negrito: bool = False):
    try:
        return ImageFont.truetype(FONTE_N if negrito else FONTE, tamanho)
    except OSError:
        return ImageFont.load_default()


def _linha(pasta: Path, nome: str) -> Image.Image:
    imagens = []
    for n in range(1, 6):
        img = Image.open(pasta / f"pdf-{nome}-{n}.png").convert("RGB")
        escala = ALTURA / img.height
        imagens.append(img.resize((max(1, round(img.width * escala)), ALTURA)))
    largura = sum(i.width for i in imagens) + 24 * (len(imagens) + 1)
    linha = Image.new("RGB", (largura, ALTURA + 44), "white")
    d = ImageDraw.Draw(linha)
    x = 24
    for numero, img in zip(NUMEROS, imagens):
        linha.paste(img, (x, 36))
        d.rectangle([x - 1, 35, x + img.width, 36 + img.height], outline=(150, 150, 150))
        d.text((x, 6), f"página {numero}", fill=(40, 40, 40), font=_fonte(20, True))
        x += img.width + 24
    return linha


def _quebrar(texto: str, fonte, largura: int) -> list[str]:
    """Quebra a legenda em linhas que cabem na largura do quadro."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.getlength(teste) > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def _quadro(titulo: str, linhas: list[tuple[str, Image.Image]], destino: Path) -> None:
    largura = max(max(img.width for _, img in linhas) + 40, 1400)
    fonte = _fonte(19)
    legendas = [_quebrar(legenda, fonte, largura - 40) for legenda, _ in linhas]
    altura = 90 + sum(img.height + 40 + 28 * len(leg) for (_, img), leg in zip(linhas, legendas))
    quadro = Image.new("RGB", (largura, altura), (245, 243, 238))
    d = ImageDraw.Draw(quadro)
    d.text((20, 18), titulo, fill=(20, 20, 20), font=_fonte(26, True))
    y = 80
    for (_, img), leg in zip(linhas, legendas):
        for n, texto in enumerate(leg):
            d.text((20, y + 28 * n), texto, fill=(60, 60, 60), font=fonte)
        y += 28 * len(leg) + 6
        quadro.paste(img, (20, y))
        y += img.height + 34
    quadro.save(destino)


def _tela(pasta: Path, nome: str) -> Image.Image:
    """A foto da janela (desenhada na memória, sem aparecer na tela), reduzida."""
    img = Image.open(pasta / nome).convert("RGB")
    return img.resize((img.width * 3 // 4, img.height * 3 // 4))


def main() -> None:
    antes, depois, saida, livro = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
    saida.mkdir(parents=True, exist_ok=True)
    estado = json.loads((depois / "estado.json").read_text(encoding="utf-8"))
    l = estado["livro"]
    caminho = (f"{livro}, livro novo (ajustes de fábrica: dividir as folhas 2 a 70 pela lombada, "
               f"endireitar {'ligado' if l.get('endireitar') else 'desligado'}, "
               f"cortar as bordas {'ligado' if l.get('cortar_bordas') else 'desligado'}, "
               f"filtro {l.get('filtro_padrao')}); folha 1 (capa e contracapa abertas) inteira; "
               f"ferramenta Cortar as bordas")
    for situacao, titulo, onde in (
            ("s1", "Situação 1 (D-638): na capa inteira, \"todas as folhas\" + ¼ à esquerda",
             "na página 1 (capa inteira), quadro \"Girar a folha\", lista \"todas as folhas\""),
            ("s2", "Situação 2 (D-640): no miolo, \"todas as páginas\" + ¼ à esquerda",
             "na página 14 (folha dividida), quadro \"Girar a página\", lista \"todas as páginas\""),
            ("s3", "Situação 3 (resposta \"Giram também\", 07/11): na página 3, \"só as ímpares\" + ¼ à esquerda",
             "na página 3 (folha dividida, ímpar), quadro \"Girar a página\", lista \"só as ímpares\"")):
        _quadro(titulo, [
            (f"PDF que sai ANTES do clique. {caminho}.", _linha(depois, "original")),
            (f"PDF que sai DEPOIS do clique, com o código de ANTES do conserto: {onde}.",
             _linha(antes, situacao)),
            (f"PDF que sai DEPOIS do clique, com o código NOVO (girar-capa): {onde}.",
             _linha(depois, situacao)),
        ], saida / f"{situacao}-pdf-antes-e-depois.png")
    # a janela: na situação 1, a página 14 depois do giro na capa; na 2, a capa depois do giro no miolo
    for situacao, titulo, foto, onde in (
            ("s1", "Situação 1 (D-638) na janela: a página 14 depois de girar \"todas as folhas\" na capa",
             "tela-s1-pagina14.png", "girou na página 1 (capa) com \"todas as folhas\" + ¼ à esquerda e foi à página 14"),
            ("s2", "Situação 2 (D-640) na janela: a capa depois de girar \"todas as páginas\" no miolo",
             "tela-s2-pagina1.png", "girou na página 14 com \"todas as páginas\" + ¼ à esquerda e foi à página 1 (capa)"),
            ("s3", "Situação 3 (\"Giram também\") na janela: a capa depois de girar \"só as ímpares\" na página 3",
             "tela-s3-pagina1.png", "girou na página 3 com \"só as ímpares\" + ¼ à esquerda e foi à página 1 (capa)")):
        _quadro(titulo, [
            (f"Código de ANTES do conserto: {onde}. {caminho}. Janela desenhada na memória "
             f"(nada abriu na tela).", _tela(antes, foto)),
            (f"Código NOVO (girar-capa): o mesmo caminho.", _tela(depois, foto)),
        ], saida / f"{situacao}-janela-antes-e-depois.png")
    print("ok", saida)


if __name__ == "__main__":
    main()
