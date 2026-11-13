"""Monta os prints do conserto do fundo tirado (D-646/D-699) no modelo do girar
(docs/plano/central/modelo-de-print/): faixa azul = antes, verde = depois, as mesmas páginas no
mesmo enquadramento, o que olhar circulado em vermelho, uma frase em cada imagem. Os ajudantes
de desenho são os do relatorios/graves-2026-11-10/montar.py (ramo graves-2026-11-10).

    python montar.py <capturas do código antigo> <capturas do novo> <capturas da tela> <saída>

As capturas vêm de capturar.py (antigo e novo) e capturar_tela.py (novo).
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




def _linha(pasta: Path, prefixo: str, circular: set[int]) -> Image.Image:
    paginas = [3, 4, 5, 6]
    return _grade([_abrir(pasta, f"{prefixo}-{p}.png") for p in paginas],
                  [f"página {p}" for p in paginas], 300, circular)


def automatico(antigo: Path, novo: Path, saida: Path) -> None:
    _salvar(_empilhar([
        _cabeca("O Automático não traz mais o fundo de volta (D-646)", (40, 40, 40),
                "Siebmacher (cópia), páginas 3 a 6: \"Sim, tirar o fundo\" e depois o Automático "
                "do jeito que ele abre (Endireitar, Cortar as bordas e \"Limpar a folha\" em "
                "Original)."),
        _cabeca("ANTES do conserto", AZUL,
                "Depois do Automático, o filtro virou Original e o papel velho voltou nas quatro "
                "páginas (em vermelho), sem aviso."),
        _linha(antigo, "2-depois-do-automatico-original", {0, 1, 2, 3}),
        _cabeca("DEPOIS do conserto", VERDE,
                "O mesmo caminho: o filtro vira Original e o papel continua branco nas quatro "
                "(em vermelho), igual a antes do Automático."),
        _linha(novo, "2-depois-do-automatico-original", {0, 1, 2, 3})]),
        saida / "fundo-1-automatico.png")


def desfazer(novo: Path, saida: Path) -> None:
    _salvar(_empilhar([
        _cabeca("Desfazer o tirar o fundo (D-699)", (40, 40, 40),
                "Siebmacher (cópia), páginas 3 a 6, filtro Original com o fundo tirado. Menu "
                "Filtro > \"Desfazer o tirar o fundo\" na página 3 (o botão do painel faz o mesmo)."),
        _cabeca("ANTES do botão", AZUL, "As quatro páginas sem o fundo (papel branco)."),
        _linha(novo, "2-depois-do-automatico-original", set()),
        _cabeca("DEPOIS do botão", VERDE,
                "Só a página 3 (em vermelho) volta com o papel como foi escaneado; as outras "
                "continuam sem o fundo. Para levar às outras: \"Aplicar em\"."),
        _linha(novo, "3-desfazer-o-tirar-o-fundo-na-pagina-3", {0})]),
        saida / "fundo-2-desfazer.png")


def preto_e_branco(novo: Path, saida: Path) -> None:
    _salvar(_empilhar([
        _cabeca("Preto e branco em cima da página sem o fundo (D-699)", (40, 40, 40),
                "Siebmacher (cópia), páginas 3 a 6, depois do \"Desfazer o tirar o fundo\" só na "
                "página 3. Automático com \"Limpar a folha\" em Preto e branco."),
        _cabeca("ANTES: Original", AZUL,
                "Página 3 com o fundo de volta; páginas 4 a 6 sem o fundo."),
        _linha(novo, "3-desfazer-o-tirar-o-fundo-na-pagina-3", set()),
        _cabeca("DEPOIS: Preto e branco", VERDE,
                "As páginas 4 a 6 (em vermelho) ficam em preto e branco feito em cima da página "
                "sem o fundo; a página 3, sobre a página como foi escaneada."),
        _linha(novo, "4-depois-do-automatico-preto-e-branco", {1, 2, 3})]),
        saida / "fundo-3-preto-e-branco.png")


def botao_e_menu(tela: Path, saida: Path) -> None:
    janela = Image.open(tela / "janela.png").convert("RGB")
    painel = janela.crop((1258, 40, 1556, 420))
    painel = painel.resize((painel.width * 2, painel.height * 2), Image.LANCZOS)
    d = ImageDraw.Draw(painel)
    # o botão fica logo abaixo das figurinhas (y 226-254 na janela)
    d.ellipse([4, (222 - 40) * 2, painel.width - 4, (258 - 40) * 2], outline=VERMELHO, width=6)
    menu = Image.open(tela / "menu-filtro.png").convert("RGB")
    menu = menu.resize((menu.width * 2, menu.height * 2), Image.LANCZOS)
    d = ImageDraw.Draw(menu)
    d.ellipse([4, menu.height - 62, menu.width - 4, menu.height - 2], outline=VERMELHO, width=6)
    _salvar(_empilhar([
        _cabeca("Onde fica o botão (D-699)", (40, 40, 40),
                "Siebmacher (cópia), página 3. À esquerda, o painel \"Filtro da página\": o botão "
                "\"Desfazer o tirar o fundo\" logo abaixo das figurinhas. À direita, o menu Filtro, "
                "com o mesmo item embaixo dos filtros (os dois em vermelho)."),
        _cabeca("DEPOIS do conserto", VERDE,
                "Os dois só aparecem em livro com o \"Tirar o fundo\" e só ficam acesos na "
                "página sem o fundo."),
        _grade([painel, menu], ["painel Filtro da página", "menu Filtro"], 620, set())]),
        saida / "fundo-4-botao-e-menu.png")


if __name__ == "__main__":
    ANTIGO, NOVO, TELA, SAIDA = (Path(a) for a in sys.argv[1:5])
    SAIDA.mkdir(parents=True, exist_ok=True)
    automatico(ANTIGO, NOVO, SAIDA)
    desfazer(NOVO, SAIDA)
    preto_e_branco(NOVO, SAIDA)
    botao_e_menu(TELA, SAIDA)
