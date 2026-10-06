"""COPIA do figuras.py da rodada 1, com os quadros lado a lado da rodada 2.

As imagens da rodada 1 das decisoes do "Para revisar" (06/10/2026).

Base: relatorios/revisar-criterios-2026-10-06/scripts/figuras.py (copiado e
mudado aqui; o do estudo nao foi tocado).

Cada imagem tem duas fileiras:
  1a: tres quadros grandes, recortados e ampliados na regiao que importa:
      Original | Resultado (o jeito de fabrica, ou o "So o texto achado") |
      Preto e branco de sempre (so nas paginas; no fechamento entra o "onde olhar")
  2a: a pagina inteira pequena, com a parte ampliada pintada de amarelo
      transparente (para se localizar), e o quadro "onde olhar": uma COPIA do
      original recortado, com o que importa pintado em cor transparente.
Nunca se desenha nada por cima do Original, do Resultado nem do Preto e branco.

Uso: python figuras.py [nome,nome,...]   (grava ../img/*.jpg)
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import comum
import medir

DESTINO = comum.PASTA / "img"
LARGURA = 1800
VAO = 24
CORES = {"sumiu": (225, 20, 20), "contou": (255, 130, 0), "gravura": (30, 160, 50),
         "caixa": (255, 200, 0), "olhar": (40, 110, 230), "beirada": (255, 130, 0)}
NOMES = {"a": "Resultado (jeito de fábrica)", "c": "Resultado (Só o texto achado)",
         "pb": "Preto e branco de sempre"}


def _fonte(tamanho: int, negrito: bool = False):
    nomes = ("arialbd.ttf", "segoeuib.ttf") if negrito else ("arial.ttf", "segoeui.ttf")
    for nome in nomes + ("DejaVuSans.ttf",):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def _com_titulo(img_rgb: np.ndarray, texto: str, largura: int | None = None) -> Image.Image:
    """O quadro com uma borda cinza fina e o titulo em cima (fora da imagem)."""
    alto = 46
    q = cv2.copyMakeBorder(img_rgb, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(150, 150, 150))
    larg = largura or q.shape[1]
    tela = Image.new("RGB", (larg, q.shape[0] + alto), (255, 255, 255))
    tela.paste(Image.fromarray(q), ((larg - q.shape[1]) // 2, alto))
    d = ImageDraw.Draw(tela)
    fonte = _fonte(28, True)
    while d.textlength(texto, font=fonte) > larg - 8 and fonte.size > 14:
        fonte = _fonte(fonte.size - 1, True)
    d.text(((larg - d.textlength(texto, font=fonte)) / 2, 8), texto, fill=(25, 25, 25), font=fonte)
    return tela


def _ler(base: str, nome: str, forma) -> np.ndarray:
    img = cv2.imread(str(comum.DADOS / f"{base}__{nome}.jpg"))
    if img.shape[:2] != tuple(forma):
        img = cv2.resize(img, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    return img


def _tingir(img_bgr: np.ndarray, mascara: np.ndarray, cor_rgb, clarear: bool = True,
            forca: float = 0.55) -> np.ndarray:
    x = img_bgr.astype(np.float32)
    if clarear:
        x = x * 0.6 + 255 * 0.4
    bgr = np.array(cor_rgb[::-1], np.float32)
    x[mascara] = x[mascara] * (1 - forca) + bgr * forca
    return x.astype(np.uint8)


def _escala(img: np.ndarray, larg: int, alt: int, ampliar_ate: float = 2.5) -> np.ndarray:
    f = min(larg / img.shape[1], alt / img.shape[0], ampliar_ate)
    nova = (max(1, round(img.shape[1] * f)), max(1, round(img.shape[0] * f)))
    interp = cv2.INTER_CUBIC if f > 1 else cv2.INTER_AREA
    return cv2.resize(img, nova, interpolation=interp)


def figura(arquivo: str, base: str, jeito: str, caixa, camadas, legenda: str,
           caixas_olhar=(), cor_caixas: str = "sumiu", alto_max: int = 900) -> None:
    """caixa = (x0, y0, x1, y1) em fracao da pagina: a parte ampliada.
    camadas = mascaras pintadas no "onde olhar" (sumiu, contou, gravura).
    caixas_olhar = retangulos (fracao DA PAGINA) pintados no "onde olhar"
    quando o que importa nao e uma mascara (ex.: a faixa do scanner)."""
    dados = json.loads((comum.DADOS / f"{base}.json").read_text(encoding="utf-8"))
    z = dict(np.load(comum.DADOS / f"{base}.npz"))
    alt, larg = z["base_tinta"].shape
    f = min(1.0, 4000 / max(alt, larg))
    forma = (round(alt * f), round(larg * f))
    ori = _ler(base, "original", forma)
    res = _ler(base, jeito, forma)
    pb = _ler(base, "pb", forma)

    def peq(m):
        return cv2.resize(m.astype(np.uint8) * 255, (forma[1], forma[0]),
                          interpolation=cv2.INTER_AREA) > 40

    mascaras = {}
    if camadas:
        s, m = medir.sinais(dados, z)
        res_tinta = z["a_tinta"] if jeito == "a" else z["c_tinta"]
        sumiu = z["pb_tinta"] & ~res_tinta & ~z["imagem"]
        raio = max(2, int(round(dados["altura_linha"] * 0.06)))
        el = np.ones((raio, raio), np.uint8)
        from sinais import beirada_escura
        _f, beir = beirada_escura(z["a_tinta"] & ~z["imagem"])
        beir = cv2.resize(beir.astype(np.uint8) * 255, (forma[1], forma[0]),
                          interpolation=cv2.INTER_NEAREST) > 0
        mascaras = {"beirada": beir,
                    "sumiu": peq(cv2.dilate(sumiu.astype(np.uint8), el) > 0),
                    "contou": peq(cv2.dilate(m["forte"].astype(np.uint8), el) > 0),
                    "gravura": peq(z["imagem"])}
    onde = ori.astype(np.float32) * 0.6 + 255 * 0.4
    onde = onde.astype(np.uint8)
    for c in camadas:
        onde = _tingir(onde, mascaras[c], CORES[c], clarear=False,
                       forca=0.55 if c == "sumiu" else 0.35)
    for (bx0, by0, bx1, by1) in caixas_olhar:
        mm = np.zeros(forma, bool)
        mm[int(by0 * forma[0]):int(by1 * forma[0]), int(bx0 * forma[1]):int(bx1 * forma[1])] = True
        onde = _tingir(onde, mm, CORES[cor_caixas], clarear=False, forca=0.3)

    x0, y0, x1, y1 = caixa
    ya, yb, xa, xb = int(y0 * forma[0]), int(y1 * forma[0]), int(x0 * forma[1]), int(x1 * forma[1])

    def rec(img):
        return cv2.cvtColor(img[ya:yb, xa:xb], cv2.COLOR_BGR2RGB)

    # 1a fileira: tres quadros grandes
    w3 = (LARGURA - 2 * VAO) // 3 - 4
    if jeito == "a":
        trio = [(rec(ori), "Original"), (rec(res), NOMES["a"]), (rec(pb), NOMES["pb"])]
    else:
        trio = [(rec(ori), "Original"), (rec(res), NOMES["c"]), (rec(onde), "Onde olhar")]
    quadros = [_com_titulo(_escala(q, w3, alto_max), t, w3 + 4) for q, t in trio]
    h1 = max(q.height for q in quadros)

    # 2a fileira: pagina inteira pequena + onde olhar (so nas paginas)
    alto2 = 600
    pagina = ori.copy()
    mm = np.zeros(forma, bool)
    mm[ya:yb, xa:xb] = True
    pagina = cv2.cvtColor(_tingir(pagina, mm, CORES["caixa"], clarear=False, forca=0.4), cv2.COLOR_BGR2RGB)
    q_pag = _com_titulo(_escala(pagina, 560, alto2, 1.0), "Página inteira")
    segunda = [q_pag]
    resto = LARGURA - q_pag.width - VAO - 4
    if jeito == "a":
        segunda.append(_com_titulo(_escala(rec(onde), resto, alto2), "Onde olhar"))
    else:
        fab = _ler(base, "a", forma)
        segunda.append(_com_titulo(_escala(rec(fab), resto, alto2),
                                   "Para comparar: o jeito de fábrica"))
    h2 = max(q.height for q in segunda) + 90

    tela = Image.new("RGB", (LARGURA, h1 + VAO + h2), (255, 255, 255))
    x = 0
    for q in quadros:
        tela.paste(q, (x, 0))
        x += q.width + VAO
    x = 0
    for q in segunda:
        tela.paste(q, (x, h1 + VAO))
        x += q.width + VAO
    d = ImageDraw.Draw(tela)
    linhas = ["Na página inteira, em amarelo, a parte ampliada.", "Onde olhar: " + legenda]
    for i, texto in enumerate(linhas):
        fonte = _fonte(26)
        while d.textlength(texto, font=fonte) > LARGURA - 10 and fonte.size > 16:
            fonte = _fonte(fonte.size - 1)
        d.text((6, h1 + VAO + h2 - 82 + 38 * i), texto, fill=(40, 40, 40), font=fonte)
    DESTINO.mkdir(parents=True, exist_ok=True)
    destino = DESTINO / f"{arquivo}.jpg"
    qualidade = 88
    while True:
        tela.save(destino, quality=qualidade)
        if destino.stat().st_size < 590_000 or qualidade <= 70:
            break
        qualidade -= 4
    print(arquivo, tela.size, qualidade, destino.stat().st_size // 1024, "KB", flush=True)






# ---------------------------------------------------------------------------
# Rodada 2: quadros soltos lado a lado (para os cartoes de resposta).
# Cada quadro: (base, nome da imagem: original|a|pb|c|<caminho jpg>, caixa,
#               camadas pintadas por cima de uma COPIA clareada do original
#               ([] = a imagem como esta), titulo)
# ---------------------------------------------------------------------------

def _quadro(base, nome, caixa, camadas, alvo_larg, alvo_alt):
    from pathlib import Path

    dados = json.loads((comum.DADOS / f"{base}.json").read_text(encoding="utf-8"))
    alt, larg = dados["tamanho"][1], dados["tamanho"][0]
    f = min(1.0, 4000 / max(alt, larg))
    forma = (round(alt * f), round(larg * f))
    if nome in ("original", "a", "pb", "c"):
        img = _ler(base, nome, forma)
    else:
        img = cv2.imread(str(Path(nome)))
        img = cv2.resize(img, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    if camadas:
        z = dict(np.load(comum.DADOS / f"{base}.npz"))
        img = (img.astype(np.float32) * 0.6 + 255 * 0.4).astype(np.uint8)
        raio = max(2, int(round(dados["altura_linha"] * 0.06)))
        el = np.ones((raio, raio), np.uint8)
        for c in camadas:
            if c in ("sumiu", "sumiu_c"):
                res = z["a_tinta"] if c == "sumiu" else z["c_tinta"]
                m = z["pb_tinta"] & ~res & ~z["imagem"]
            elif c == "gravura":
                m = z["imagem"]
            elif c == "contou":
                s, mm = medir.sinais(dados, z)
                m = mm["forte"]
            m = cv2.dilate(m.astype(np.uint8), el) > 0
            m = cv2.resize(m.astype(np.uint8) * 255, (forma[1], forma[0]),
                           interpolation=cv2.INTER_AREA) > 40
            cor = CORES["sumiu" if c == "sumiu_c" else c]
            img = _tingir(img, m, cor, clarear=False, forca=0.55 if "sumiu" in c else 0.35)
    x0, y0, x1, y1 = caixa
    q = img[int(y0 * forma[0]):int(y1 * forma[0]), int(x0 * forma[1]):int(x1 * forma[1])]
    return _escala(cv2.cvtColor(q, cv2.COLOR_BGR2RGB), alvo_larg, alvo_alt)


def lado_a_lado(arquivo: str, quadros: list, legendas: list[str], alto_max: int = 900) -> None:
    n = len(quadros)
    w = (LARGURA - (n - 1) * VAO) // n - 4
    prontos = [_com_titulo(_quadro(b, nm, cx, cam, w, alto_max), t, w + 4)
               for (b, nm, cx, cam, t) in quadros]
    h1 = max(p.height for p in prontos)
    tela = Image.new("RGB", (LARGURA, h1 + 16 + 38 * len(legendas)), (255, 255, 255))
    x = 0
    for p in prontos:
        tela.paste(p, (x, 0))
        x += p.width + VAO
    d = ImageDraw.Draw(tela)
    for i, texto in enumerate(legendas):
        fonte = _fonte(26)
        while d.textlength(texto, font=fonte) > LARGURA - 10 and fonte.size > 16:
            fonte = _fonte(fonte.size - 1)
        d.text((6, h1 + 10 + 38 * i), texto, fill=(40, 40, 40), font=fonte)
    destino = DESTINO / f"{arquivo}.jpg"
    DESTINO.mkdir(parents=True, exist_ok=True)
    qualidade = 88
    while True:
        tela.save(destino, quality=qualidade)
        if destino.stat().st_size < 590_000 or qualidade <= 70:
            break
        qualidade -= 4
    print(arquivo, tela.size, qualidade, destino.stat().st_size // 1024, "KB", flush=True)


def main() -> None:
    from figuras_lista import FIGURAS as LISTA

    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for fig in LISTA:
        if so and fig["arquivo"] not in so:
            continue
        fig = dict(fig)
        if fig.pop("tipo", "") == "lado":
            lado_a_lado(**fig)
        else:
            figura(**fig)


if __name__ == "__main__":
    main()
