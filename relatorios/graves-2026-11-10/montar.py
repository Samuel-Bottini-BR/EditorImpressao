"""Monta os prints dos três defeitos no modelo do girar (docs/plano/central/modelo-de-print/):
imagem-resumo, faixa azul "ANTES do conserto" e verde "DEPOIS do conserto" (na pergunta do
fundo: azul "Com o fundo tirado" e laranja "Depois do Automático"), as mesmas páginas no mesmo
enquadramento, o que olhar em vermelho e circulado.

    python montar.py <capturas do código antigo> <capturas do novo> <capturas do fundo> <saída>

As capturas vêm de capturar.py (antigo e novo) e capturar_fundo.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL, LARANJA, VERDE = (60, 90, 150), (190, 90, 10), (25, 130, 60)


def _fonte(tamanho: int, negrito: bool = False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, tamanho)


def _quebrar(texto: str, fonte, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.getlength(teste) > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def _cabeca(rotulo: str, cor, legenda: str) -> Image.Image:
    f_rot, f_leg = _fonte(46, True), _fonte(26)
    linhas = _quebrar(legenda, f_leg, LARGURA - 40)
    img = Image.new("RGB", (LARGURA, 86 + 14 + 36 * len(linhas) + 10), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, LARGURA, 86], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 100 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def _empilhar(partes: list[Image.Image], espaco: int = 16) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (LARGURA, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((LARGURA - p.width) // 2, y))
        y += p.height + espaco
    return img


def _caber(img: Image.Image, caixa_l: int, caixa_a: int) -> Image.Image:
    escala = min(caixa_l / img.width, caixa_a / img.height)
    return img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))),
                      Image.LANCZOS)


def _grade(imagens: list[Image.Image], rotulos: list[str], caixa: int,
           circular: set[int]) -> Image.Image:
    """Quadros iguais lado a lado, com o nome grande em cima de cada um; os de `circular`
    (posições) com o nome em vermelho e um círculo vermelho em volta."""
    f_num = _fonte(28, True)
    topo, margem = 46, 14
    cel_l, cel_a = caixa + 2 * margem, caixa + topo + 2 * margem
    img = Image.new("RGB", (cel_l * len(imagens), cel_a), FUNDO)
    d = ImageDraw.Draw(img)
    for n, (pagina, rotulo) in enumerate(zip(imagens, rotulos)):
        x0 = n * cel_l
        cor = VERMELHO if n in circular else (30, 30, 30)
        d.text((x0 + cel_l / 2, 6), rotulo, fill=cor, font=f_num, anchor="mt")
        p = _caber(pagina, caixa, caixa)
        px, py = x0 + (cel_l - p.width) // 2, topo + margem + (caixa - p.height) // 2
        img.paste(p, (px, py))
        d.rectangle([px - 1, py - 1, px + p.width, py + p.height], outline=(150, 150, 150))
        if n in circular:
            d.ellipse([x0 + 2, topo - 4, x0 + cel_l - 3, cel_a - 3], outline=VERMELHO, width=7)
    if img.width > LARGURA - 20:
        img = _caber(img, LARGURA - 20, 10_000)
    return img


def _abrir(pasta: Path, nome: str) -> Image.Image:
    img = Image.open(pasta / nome).convert("RGB")
    if nome.startswith(("tira-", "grade-")):
        # só o desenho da página: o número e o aviso miúdos de baixo saem (o nome vai em cima)
        img = img.crop((0, 0, img.width, round(img.height * 0.78)))
    return img


def _salvar(img: Image.Image, destino: Path) -> None:
    assert 900 <= img.width <= 1600, (destino, img.width)
    img.save(destino, optimize=True)
    print("gravei", destino)


def d649(antigo: Path, novo: Path, saida: Path) -> list[Image.Image]:
    paginas = [7, 8, 9, 10]
    faixas = []
    for pasta, rotulo, cor, frase in (
            (antigo, "ANTES do conserto", AZUL,
             "Palatino (cópia), filtro Original. A página 9 teve o conteúdo movido 17% para cima "
             "na ferramenta Mover; o livro foi fechado e aberto de novo, na página 1. A miniatura "
             "da página 9 (em vermelho), na tira de baixo e em \"ver todas\", mostra a página como "
             "veio, com o alto da página no lugar. O PDF sai com o alto cortado."),
            (novo, "DEPOIS do conserto", VERDE,
             "O mesmo caminho. A miniatura da página 9 (em vermelho), na tira e em \"ver todas\", "
             "mostra o conteúdo subido e o alto cortado, igual ao PDF. As páginas 7, 8 e 10, que "
             "ninguém moveu, ficam como sempre.")):
        tira = _grade([_abrir(pasta, f"tira-{p}.png") for p in paginas],
                      [f"tira: pág. {p}" for p in paginas], 170, {2})
        grade = _grade([_abrir(pasta, f"grade-{p}.png") for p in paginas],
                       [f"ver todas: pág. {p}" for p in paginas], 230, {2})
        pdf = _grade([_abrir(pasta, "pdf-pagina-9.png")], ["PDF: página 9"], 300, {0})
        faixa = _empilhar([_cabeca(rotulo, cor, frase), tira, grade, pdf])
        _salvar(faixa, saida / f"d649-{'1-antes' if pasta == antigo else '2-depois'}.png")
        faixas.append((rotulo, cor, pasta))
    resumo = _empilhar([
        _cabeca("Miniatura e PDF (D-649)", (40, 40, 40),
                "Página 9 do Palatino com o conteúdo movido 17% para cima, depois de reabrir o "
                "livro. Em cima, ANTES (azul): a miniatura mostra o alto da página; o PDF não. "
                "Embaixo, DEPOIS (verde): a miniatura sai igual ao PDF."),
        _grade([_abrir(antigo, "tira-9.png"), _abrir(antigo, "grade-9.png"),
                _abrir(novo, "tira-9.png"), _abrir(novo, "grade-9.png"),
                _abrir(novo, "pdf-pagina-9.png")],
               ["ANTES: tira", "ANTES: ver todas", "DEPOIS: tira", "DEPOIS: ver todas", "PDF"],
               230, {0, 1})])
    _salvar(resumo, saida / "d649-0-resumo.png")
    return [resumo]


def d648(antigo: Path, novo: Path, saida: Path) -> None:
    def fila(pasta: Path) -> Image.Image:
        img = _abrir(pasta, "tela-cheia.png")
        return img

    for pasta, rotulo, cor, frase, nome in (
            (antigo, "ANTES do conserto", AZUL,
             "Palatino (cópia), página 9, ferramenta Cortar, painel do Filtro fechado; menu Ver > "
             "\"Filtros em tela cheia\", depois de 30 segundos. Os cartões da esquerda (em "
             "vermelho) não mostram a página 9: mostram a última figurinha do painel Filtro (aqui, "
             "a capa de couro da página 1, vista ao abrir). No Lusíadas, de 07/11, ficaram vazios.",
             "d648-1-antes.png"),
            (novo, "DEPOIS do conserto", VERDE,
             "O mesmo caminho. Cada cartão da esquerda (em vermelho) mostra a página 9 com o seu "
             "filtro (Original, Preto e branco, Melhorar, Mágico pro e Tirar o fundo), como sai no "
             "PDF (com o conteúdo movido do Mover).", "d648-2-depois.png")):
        img = fila(pasta)
        tela = _caber(img, LARGURA - 40, 10_000)
        d = ImageDraw.Draw(tela)
        escala = tela.width / img.width
        # os cartões ficam na coluna da esquerda (130 pontos de largura na tela cheia)
        d.ellipse([2, 40 * escala, 125 * escala, min(tela.height - 4, 745 * escala)],
                  outline=VERMELHO, width=7)
        _salvar(_empilhar([_cabeca(rotulo, cor, frase), tela]), saida / nome)
    a = _abrir(antigo, "tela-cheia.png").crop((0, 45, 110, 735))
    b = _abrir(novo, "tela-cheia.png").crop((0, 45, 110, 735))
    _salvar(_empilhar([
        _cabeca("Filtros em tela cheia (D-648)", (40, 40, 40),
                "Os cartões da esquerda da tela cheia, na página 9 do Palatino. ANTES (azul): "
                "outra página (ou vazios, no Lusíadas). DEPOIS (verde): a página 9 em cada filtro."),
        _grade([a, b], ["ANTES", "DEPOIS"], 560, {0, 1})]), saida / "d648-0-resumo.png")


def d646(fundo: Path, saida: Path) -> None:
    paginas = [3, 4, 5, 6]
    partes = [_cabeca("O Automático traz o fundo de volta (D-646)", (40, 40, 40),
                      "Siebmacher (cópia). Em cima: depois do \"Sim, tirar o fundo\". Embaixo: "
                      "depois de rodar o Automático do jeito que ele abre (\"Limpar a folha\" em "
                      "Original). O papel velho volta em todas, sem aviso.")]
    for prefixo, rotulo, cor, frase in (
            ("com-o-fundo-tirado", "Com o fundo tirado", AZUL,
             "Páginas 3 a 6 em \"Tirar o fundo\": papel branco, só o que está impresso."),
            ("depois-do-automatico", "Depois do Automático (hoje)", LARANJA,
             "As mesmas páginas: o filtro virou Original e o fundo (o papel velho) voltou nas "
             "quatro, em vermelho.")):
        imagens = [_abrir(fundo, f"{prefixo}-{p}.png") for p in paginas]
        circular = set(range(len(paginas))) if prefixo.startswith("depois") else set()
        partes += [_cabeca(rotulo, cor, frase),
                   _grade(imagens, [f"página {p}" for p in paginas], 300, circular)]
    _salvar(_empilhar(partes), saida / "d646-pergunta.png")


if __name__ == "__main__":
    ANTIGO, NOVO, FUNDO_, SAIDA = (Path(a) for a in sys.argv[1:5])
    SAIDA.mkdir(parents=True, exist_ok=True)
    d649(ANTIGO, NOVO, SAIDA)
    d648(ANTIGO, NOVO, SAIDA)
    d646(FUNDO_, SAIDA)
