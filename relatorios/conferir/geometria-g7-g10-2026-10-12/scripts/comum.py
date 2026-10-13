"""Caminhos e ajudantes dos scripts das perguntas G7 a G10 (12/10/2026).

O QUE E
    Scripts do pesquisador para preparar as imagens das perguntas ao Samuel sobre
    os itens 2.13 (borda preta), 2.5 (caixa do conteudo e guias), 2.4 (margens)
    e 2.6 (tamanho final). NAO fazem parte do programa: so LEEM as paginas do
    gabarito e o codigo de core/ (o corte de hoje), e gravam imagens na pasta
    relatorios/conferir/geometria-g7-g10-2026-10-12/.

COMO RODAR (da raiz da worktree, com a .venv da pasta principal)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\conferir\\geometria-g7-g10-2026-10-12\\scripts\\passo1_dados.py
    ...\\python.exe ...\\scripts\\passo2_imagens.py

SEGURO MUDAR: cores, tamanhos, textos. ARRISCADO: os caminhos de leitura (as
pastas de fora do projeto sao somente leitura; nada e gravado nelas).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent                                   # .../geometria-g7-g10-2026-10-12
RAIZ = PASTA.parents[2]                               # a raiz da worktree
IMG = PASTA / "img" / "g7g10"                         # na pagina: img/g7g10/<nome>.jpg
DADOS = PASTA / "dados"
RASCUNHO = RAIZ / "saida_teste" / "geometria-perguntas"   # fora do git (saida_teste/ e ignorada)
GABARITO = RAIZ / "gabarito"

# Somente leitura (fora do projeto).
ARQUIVOS = Path(r"D:\programas\EditorImpressao-arquivos")
FAIXA = ARQUIVOS / "revisar-decisoes-trabalho" / "faixa"          # folhas cruas a 150 DPI (rodada 4)
LIVROS = ARQUIVOS / "TESTES EDITOR DE IMPRESSAO" / "LIVROS PARA TESTE"
QT_BIN = ARQUIVOS / "ferramentas" / "qt" / "6.11.1" / "msvc2022_64" / "bin"
CAIXAS_EXE = RASCUNHO / "build-caixas" / "Release" / "caixas.exe"

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# TEMP e TMP dentro da worktree (regra da gerente, 12/10).
_tmp = RASCUNHO / "tmp"
_tmp.mkdir(parents=True, exist_ok=True)
os.environ["TEMP"] = os.environ["TMP"] = str(_tmp)

# Cores (R, G, B) usadas nos desenhos por cima das paginas.
LARANJA = (240, 120, 20)      # o corte do nosso programa hoje
AZUL = (30, 110, 230)         # o ScanTailor
VERDE = (20, 150, 70)         # a opcao mostrada
VERMELHO = (215, 40, 40)      # o que se perde / o que sobra
CINZA = (110, 110, 110)
ROSA = (225, 30, 150)         # o retangulo "olhe aqui"


def fonte(tamanho: int, negrito: bool = False) -> ImageFont.FreeTypeFont:
    nome = "segoeuib.ttf" if negrito else "segoeui.ttf"
    try:
        return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / nome), tamanho)
    except OSError:
        return ImageFont.load_default()


def lista_do_gabarito() -> dict:
    return json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))


def pagina_do_gabarito(nome: str) -> tuple[np.ndarray, float]:
    """(imagem BGR, DPI) de uma pagina do gabarito. O DPI e o do PNG (lista.json):
    nas paginas do Graduale, Horas e Marial o PDF diz 72 (o tamanho da pagina em
    pontos e o da imagem), e e esse o tamanho fisico que o programa enxerga."""
    dados = lista_do_gabarito()["paginas"][nome]
    img = cv2.imread(str(GABARITO / dados["png"]), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(nome)
    return img, float(dados["dpi_png"])


def para_pil(bgr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def gravar(img: Image.Image, nome: str, largura_maxima: int = 1600, qualidade: int = 86) -> Path:
    """Grava img/<nome>.jpg, reduzindo se passar de `largura_maxima`."""
    IMG.mkdir(parents=True, exist_ok=True)
    if img.width > largura_maxima:
        img = img.resize((largura_maxima, round(img.height * largura_maxima / img.width)), Image.LANCZOS)
    destino = IMG / f"{nome}.jpg"
    img.convert("RGB").save(destino, quality=qualidade, optimize=True)
    print("gravou", destino.name, img.size, flush=True)
    return destino


def retangulo(img: Image.Image, caixa, cor, espessura: int = 6, tracejado: bool = False) -> None:
    """Desenha a caixa (x0, y0, x1, y1), em pontos, por cima de `img`."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = (int(round(v)) for v in caixa)
    if not tracejado:
        d.rectangle([x0, y0, x1, y1], outline=cor, width=espessura)
        return
    passo = espessura * 5
    for x in range(x0, x1, passo * 2):
        d.line([x, y0, min(x + passo, x1), y0], fill=cor, width=espessura)
        d.line([x, y1, min(x + passo, x1), y1], fill=cor, width=espessura)
    for y in range(y0, y1, passo * 2):
        d.line([x0, y, x0, min(y + passo, y1)], fill=cor, width=espessura)
        d.line([x1, y, x1, min(y + passo, y1)], fill=cor, width=espessura)


def escurecer_fora(img: Image.Image, caixa, quanto: float = 0.55) -> Image.Image:
    """A pagina com tudo o que fica FORA da caixa escurecido (o que o corte tira)."""
    x0, y0, x1, y1 = (int(round(v)) for v in caixa)
    fora = Image.blend(img, Image.new("RGB", img.size, (90, 20, 20)), quanto)
    fora.paste(img.crop((x0, y0, x1, y1)), (x0, y0))
    return fora


def faixa_de_titulo(largura: int, texto: str, cor=(40, 44, 52), altura: int = 0, tamanho: int = 30,
                    cor_do_texto=(255, 255, 255)) -> Image.Image:
    """Uma faixa colorida com um titulo curto, para por em cima de um quadro."""
    f = fonte(tamanho, negrito=True)
    altura = altura or int(tamanho * 1.9)
    faixa = Image.new("RGB", (largura, altura), cor)
    d = ImageDraw.Draw(faixa)
    d.text((14, (altura - tamanho) // 2 - 3), texto, font=f, fill=cor_do_texto)
    return faixa


def com_titulo(img: Image.Image, texto: str, cor=(40, 44, 52), tamanho: int = 30) -> Image.Image:
    faixa = faixa_de_titulo(img.width, texto, cor, tamanho=tamanho)
    quadro = Image.new("RGB", (img.width, img.height + faixa.height), (255, 255, 255))
    quadro.paste(faixa, (0, 0))
    quadro.paste(img, (0, faixa.height))
    return quadro


def lado_a_lado(quadros: list[Image.Image], vao: int = 24, fundo=(235, 235, 235),
                altura: int | None = None, mesma_altura: bool = True) -> Image.Image:
    """Poe os quadros um ao lado do outro. Com `mesma_altura` (o padrao) todos sao
    levados a mesma altura; sem ela ficam do tamanho que vieram (para mostrar duas
    folhas na MESMA escala), alinhados por cima."""
    altura = altura or max(q.height for q in quadros)
    prontos = []
    for q in quadros:
        if mesma_altura and q.height != altura:
            q = q.resize((round(q.width * altura / q.height), altura), Image.LANCZOS)
        prontos.append(q)
    largura = sum(q.width for q in prontos) + vao * (len(prontos) + 1)
    painel = Image.new("RGB", (largura, altura + 2 * vao), fundo)
    x = vao
    for q in prontos:
        painel.paste(q, (x, vao))
        x += q.width + vao
    return painel


def com_borda(img: Image.Image, cor=(150, 150, 150), espessura: int = 2) -> Image.Image:
    """Um fio em volta da folha, para a folha branca nao sumir no fundo claro."""
    q = img.copy()
    ImageDraw.Draw(q).rectangle([0, 0, q.width - 1, q.height - 1], outline=cor, width=espessura)
    return q
