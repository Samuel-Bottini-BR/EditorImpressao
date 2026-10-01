r"""Monta as imagens do formulario relatorios/conferir-aqui-4.html (quarta conferencia, 01/10/2026).

Uso (no .venv do programa; nao muda o programa, nao processa pagina nenhuma, so desenha):
    .venv\Scripts\python.exe relatorios\conferencia-4-2026-10-01\scripts\montar_imagens.py
(rodar antes print_tela.py, que faz o print da tela "O que fazer").

Le (somente leitura):
- as paginas originais do gabarito (gabarito/paginas/*.png);
- os resultados prontos da rodada relatorios/conferir/pb-mp-decoracao-2026-10-01/
  (antes-pb, depois-pb, antes-mp, depois-mp: o programa antes e depois dos commits de 01/10);
- a medida do corte relatorios/corte-crista-2026-10-01/medida-corte-2026-10-01.json.

Grava em relatorios/conferencia-4-2026-10-01/:
- cartoes/  um JPG por cartao: em cima ORIGINAL, ANTES e AGORA da pagina inteira; embaixo,
            cada detalhe ampliado, o mesmo lugar nas tres;
- corte/    a pergunta do corte (Escola 7, "CRISTÃ"): como esta (~0,6 mm) e como ficaria com 1 mm;
- tela/     o print da tela com o lugar da caixinha nova marcado.

REGRA DO DESENHO (erro das conferencias anteriores: o retangulo rosa desenhado POR CIMA da
imagem escondeu a perna do "A" de "CRISTÃ"):
- o retangulo que mostra de onde vem o detalhe e desenhado COM FOLGA, por fora do lugar
  ampliado: nada do que esta ampliado fica embaixo da linha. A pagina inteira ganha uma
  margem branca antes, para o retangulo caber mesmo quando o detalhe encosta na beirada;
- o detalhe ampliado nao leva desenho nenhum por cima;
- nenhum texto e escrito em cima da imagem: os rotulos ficam em faixas acima de cada parte.

Seguro mudar: os recortes dos detalhes (fracoes da pagina do RESULTADO), textos dos rotulos,
tamanhos. Arriscado: nada (so leitura e desenho).
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "relatorios" / "conferencia-2-2026-09-30" / "scripts"))

import alinhar as A  # noqa: E402
import util_imagens as U  # noqa: E402  (rotulo, lado_a_lado, um_embaixo_do_outro, gravar)

SAIDA = AQUI.parent
RODADA = RAIZ / "relatorios" / "conferir" / "pb-mp-decoracao-2026-10-01"
PAGINAS = RAIZ / "gabarito" / "paginas"

COR_DETALHE = [(230, 0, 200), (0, 90, 220)]          # detalhe 1 rosa, detalhe 2 azul
NOME_COR = ["rosa", "azul"]
FUNDO = {"ORIGINAL": (90, 90, 90), "ANTES": (150, 60, 30), "AGORA": (0, 115, 0)}
NOME_FILTRO = {"pb": "Preto e branco", "mp": "Mágico pro"}
LARGURA = 1950


def resultado(pasta: str, pagina: str) -> np.ndarray:
    return A.ler_rgb(Path(glob.glob(str(RODADA / pasta / "*" / "resultado" / f"{pagina}.png"))[0]))


_ORIG: dict = {}


def original_alinhado(pagina: str) -> np.ndarray:
    """Original no enquadramento do resultado (alinhado pelo Magico pro de hoje, que tem cor)."""
    if pagina not in _ORIG:
        _ORIG[pagina] = A.original_no_quadro_do_resultado(A.ler_rgb(PAGINAS / f"{pagina}.png"),
                                                          resultado("depois-mp", pagina), pagina)
    return _ORIG[pagina]


def recorte(img: np.ndarray, ret) -> np.ndarray:
    h, w = img.shape[:2]
    return img[int(ret[1] * h):int(ret[3] * h), int(ret[0] * w):int(ret[2] * w)]


def pagina_com_folga_marcada(img: np.ndarray, detalhes: list, alt: int) -> np.ndarray:
    """Pagina inteira reduzida, com margem branca e o retangulo de cada detalhe POR FORA.

    O retangulo fica FOLGA pontos para fora do lugar ampliado (nada do detalhe fica embaixo
    da linha); a margem branca deixa o retangulo caber quando o detalhe encosta na beirada.
    """
    peq = U.na_altura(img, alt)
    folga, esp, margem = 7, 4, 14
    h, w = peq.shape[:2]
    out = np.full((h + 2 * margem, w + 2 * margem, 3), 255, np.uint8)
    out[margem:margem + h, margem:margem + w] = peq
    cv2.rectangle(out, (margem - 1, margem - 1), (margem + w, margem + h), (175, 175, 175), 1)
    for k, ret in enumerate(detalhes):
        x0 = margem + int(ret[0] * w) - folga - esp
        y0 = margem + int(ret[1] * h) - folga - esp
        x1 = margem + int(ret[2] * w) + folga + esp
        y1 = margem + int(ret[3] * h) + folga + esp
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(out.shape[1] - 1, x1), min(out.shape[0] - 1, y1)
        cv2.rectangle(out, (x0, y0), (x1, y1), COR_DETALHE[k], esp)
    return out


def contraste(img: np.ndarray) -> np.ndarray:
    """So para enxergar: estica os tons claros (200 a 255 viram 0 a 255). Papel branco fica branco."""
    return np.clip((img.astype(np.float32) - 200) * (255 / 55), 0, 255).astype(np.uint8)


def cartao(nome: str, pagina: str, filtro: str, detalhes: list, titulo: str,
           com_contraste: bool = False) -> Path:
    o = original_alinhado(pagina)
    a = resultado(f"antes-{filtro}", pagina)
    d = resultado(f"depois-{filtro}", pagina)
    f = NOME_FILTRO[filtro]
    rot = [("ORIGINAL", "a página como veio do livro"),
           ("ANTES", f"{f}, programa antes de 01/10"),
           ("AGORA", f"{f}, programa de hoje")]
    deitada = o.shape[1] > o.shape[0]
    alt = 560 if deitada else 880
    topo = U.lado_a_lado([U.rotulo(pagina_com_folga_marcada(im, detalhes, alt), r, fundo=FUNDO[r], sub=s, tam=38)
                          for im, (r, s) in zip((o, a, d), rot)], por_baixo=True)
    legenda = " · ".join(f"retângulo {NOME_COR[k]} = detalhe {k + 1}" for k in range(len(detalhes)))
    partes = [U.rotulo(topo, titulo, fundo=(30, 42, 54), sub=f"Página inteira: {legenda} "
                       "(o retângulo fica com folga, por fora do lugar ampliado; os detalhes não têm nada desenhado por cima)", tam=40)]
    nomes = [r for r, _ in rot]
    blocos_crus = [[recorte(im, ret) for im in (o, a, d)] for ret in detalhes]
    # largo = mais de 2,2 vezes mais largo que alto: as tres partes vao uma embaixo da outra
    largos = [c[2].shape[1] / c[2].shape[0] >= 2.2 for c in blocos_crus]
    # dois detalhes largos: um ao lado do outro (cada um com ORIGINAL/ANTES/AGORA empilhados),
    # senao a imagem fica comprida demais; nos outros casos, um detalhe embaixo do outro
    em_colunas = len(detalhes) == 2 and all(largos)
    larg_bloco = (LARGURA - 24) // 2 if em_colunas else LARGURA
    blocos = []
    for k, crs in enumerate(blocos_crus):
        if largos[k]:
            lb = (larg_bloco - 24) // 2 if com_contraste else larg_bloco - 10
            linhas = [U.rotulo(U.na_largura(c, lb), r, fundo=FUNDO[r], tam=34) for c, r in zip(crs, nomes)]
            corpo = U.um_embaixo_do_outro(linhas, espaco=14)
            if com_contraste:
                # ao lado: ANTES e AGORA com contraste aumentado (so para enxergar o cinza claro)
                extra = [U.rotulo(U.na_largura(contraste(c), lb), f"{r} com contraste aumentado",
                                  fundo=FUNDO[r], tam=30, sub="só para enxergar o cinza bem claro; não é como sai")
                         for c, r in zip(crs[1:], nomes[1:])]
                corpo = U.lado_a_lado([corpo, U.um_embaixo_do_outro(extra, espaco=14)], espaco=24)
        else:
            larg = (larg_bloco - 2 * 18) // 3
            corpo = U.lado_a_lado([U.rotulo(U.na_largura(c, larg), r, fundo=FUNDO[r], tam=34)
                                   for c, r in zip(crs, nomes)], por_baixo=True)
            if com_contraste:
                # embaixo de ANTES e AGORA, os mesmos com contraste aumentado; embaixo do ORIGINAL, o aviso
                cs = [U.na_largura(contraste(c), larg) for c in crs[1:]]
                aviso = U.rotulo(np.full_like(cs[0], 255), "CONTRASTE AUMENTADO →", fundo=(110, 110, 110), tam=30,
                                 sub="só para enxergar o cinza bem claro; não é como a página sai")
                linha = U.lado_a_lado([aviso] + [U.rotulo(c, f"{r} (contraste aumentado)", fundo=FUNDO[r], tam=30)
                                                 for c, r in zip(cs, nomes[1:])], por_baixo=True)
                corpo = U.um_embaixo_do_outro([corpo, linha], espaco=14)
        texto = (f"DETALHE {k + 1} (retângulo {NOME_COR[k]}), ampliado" if em_colunas else
                 f"DETALHE {k + 1} (retângulo {NOME_COR[k]}), ampliado, sem nada desenhado por cima")
        blocos.append(U.rotulo(corpo, texto, fundo=COR_DETALHE[k], tam=32))
    if em_colunas:
        partes.append(U.lado_a_lado(blocos, espaco=24))
    else:
        partes.extend(blocos)
    img = U.um_embaixo_do_outro(partes, espaco=26)
    return U.gravar(img, SAIDA / "cartoes" / f"{nome}.jpg", qualidade=88, largura_max=LARGURA)


# --------------------------------------------------------------------------- os cartoes
# (nome, pagina, filtro, [detalhes em fracao da pagina do RESULTADO], titulo, contraste)
CARTOES = [
    ("pb1-opus20-estatua", "opusmajus_p020", "pb", [(0.06, 0.04, 0.62, 0.50)],
     "Opus Majus 20: a foto da estátua no Preto e branco", False),
    ("pb2-escola35-anjo", "escola_p035", "pb", [(0.10, 0.0, 0.55, 0.42)],
     "Escola 35: a pintura do anjo no Preto e branco", False),
    ("pb3-horas13-vermelho", "horas_p013", "pb", [(0.08, 0.09, 0.80, 0.28)],
     "Horas 13: os títulos vermelhos no Preto e branco", False),
    ("pb4-horas27-letras-A", "horas_p027", "pb", [(0.06, 0.12, 0.45, 0.32), (0.06, 0.55, 0.45, 0.71)],
     "Horas 27: as letras 'A' douradas no Preto e branco", False),
    ("pb5-graduale223-vermelho", "graduale_p223", "pb", [(0.05, 0.55, 0.52, 0.68), (0.12, 0.20, 0.60, 0.32)],
     "Graduale 223: as palavras vermelhas no Preto e branco", False),
    ("pb6-horas13-moldura", "horas_p013", "pb", [(0.45, 0.76, 0.97, 0.875), (0.03, 0.07, 0.40, 0.19)],
     "Horas 13: a moldura dourada no Preto e branco", False),
    ("pb7-horas26-moldura", "horas_p026", "pb", [(0.0, 0.72, 0.40, 0.93), (0.0, 0.05, 0.50, 0.30)],
     "Horas 26: a moldura dourada no Preto e branco", False),
    ("pb8-horas27-moldura", "horas_p027", "pb", [(0.55, 0.72, 1.0, 0.93)],
     "Horas 27: a moldura dourada no Preto e branco", False),
    ("pb9-horas11-iluminura", "horas_p011", "pb", [(0.0, 0.60, 0.50, 0.86)],
     "Horas 11: a iluminura no Preto e branco", False),
    ("pb10-horas47-iluminura", "horas_p047", "pb", [(0.0, 0.38, 0.42, 0.63)],
     "Horas 47: a iluminura no Preto e branco", False),
    ("pb11-graduale222-pauta", "graduale_p222", "pb", [(0.30, 0.08, 0.85, 0.34)],
     "Graduale 222: a pauta e as notas no Preto e branco", False),
    ("mp1-horas13-dourado", "horas_p013", "mp", [(0.03, 0.06, 0.45, 0.22)],
     "Horas 13: a moldura dourada no Mágico pro", False),
    ("mp2-horas26-dourado", "horas_p026", "mp", [(0.0, 0.72, 0.40, 0.93)],
     "Horas 26: a moldura dourada no Mágico pro", False),
    ("mp3-horas47-faixa-cinza", "horas_p047", "mp", [(0.15, 0.47, 0.62, 0.60)],
     "Horas 47: a faixa cinza embaixo de 'pitié de nous' no Mágico pro", True),
    ("mp4-horas11-iluminura", "horas_p011", "mp", [(0.22, 0.78, 0.78, 0.99), (0.0, 0.30, 0.30, 0.75)],
     "Horas 11: a iluminura no Mágico pro", False),
]


# --------------------------------------------------------------------------- a tela
def tela() -> Path:
    """Print da tela com a caixinha nova; o lugar marcado por fora, com folga, e ampliado embaixo."""
    img = A.ler_rgb(SAIDA / "tela" / "o-que-fazer.png")
    info = json.loads((SAIDA / "tela" / "caixinha.json").read_text(encoding="utf-8"))
    x0, y0, x1, y1 = info["caixinha"]
    # a caixinha e a frase de baixo dela (a frase fica ~20 pontos abaixo)
    x0, y0, x1, y1 = x0 - 6, y0 - 4, x1 + 6, y1 + 26
    folga, esp = 6, 3
    marcado = img.copy()
    cv2.rectangle(marcado, (x0 - folga - esp, y0 - folga - esp), (x1 + folga + esp, y1 + folga + esp),
                  COR_DETALHE[0], esp)
    zoom = U.na_largura(img[max(0, y0 - 60):y1 + 12, max(0, x0 - 40):x1 + 20], LARGURA - 20)
    partes = [U.rotulo(marcado, "A tela \"O que fazer\" (filtro Preto e branco escolhido)", fundo=(30, 42, 54),
                       sub="retângulo rosa = a caixinha nova, ampliada embaixo (de fábrica ela vem desmarcada)", tam=36),
              U.rotulo(zoom, "A caixinha nova, ampliada", fundo=COR_DETALHE[0], tam=34)]
    return U.gravar(U.um_embaixo_do_outro(partes, espaco=24), SAIDA / "tela" / "tela-caixinha.jpg",
                    qualidade=90, largura_max=LARGURA)


# --------------------------------------------------------------------------- o corte (Escola 7)
def corte_crista() -> Path:
    """Canto de "CRISTÃ" (Escola 7): o corte de hoje (~0,6 mm depois da última letra) e o de 1 mm.

    Usa a medida do corte de 01/10 (borda direita do corte, a 300 DPI) e a pagina original
    ampliada para 300 DPI (o tamanho que o programa usa no corte). Nao roda o corte: so desenha
    a linha onde ele passa. A ultima tinta do titulo e medida aqui mesmo (cinza abaixo de 60%
    do papel, como o medidor de relatorios/corte-crista-2026-10-01).
    """
    med = json.loads((RAIZ / "relatorios" / "corte-crista-2026-10-01" / "medida-corte-2026-10-01.json")
                     .read_text(encoding="utf-8"))["escola_p007"]
    W, H = med["tamanho"]
    borda = med["px"][2]                                   # borda direita do corte de hoje
    pag = cv2.resize(A.ler_rgb(PAGINAS / "escola_p007.png"), (W, H), interpolation=cv2.INTER_CUBIC)
    cinza = cv2.cvtColor(pag, cv2.COLOR_RGB2GRAY)
    # faixa do titulo "... CRISTÃ" (linhas medidas na pagina a 300 DPI)
    t0, t1 = 230, 340
    papel = float(np.percentile(cinza[t0:t1, borda - 400:borda], 90))
    tinta = cinza[t0:t1, :borda] < 0.6 * papel
    colunas = np.nonzero(tinta.any(axis=0))[0]
    ultima = int(colunas.max())
    mm = 300 / 25.4                                        # pontos por milimetro a 300 DPI
    folga_hoje = (borda - ultima - 1) / mm
    borda_1mm = ultima + 1 + int(np.ceil(mm))
    print(f"  Escola 7: ultima tinta x={ultima}, borda do corte x={borda}: folga {borda - ultima - 1} pontos"
          f" = {folga_hoje:.2f} mm; com 1 mm a borda iria para x={borda_1mm}")

    esc = 6
    # recorte: o fim de "CRISTÃ" e papel a direita, com lugar para os textos da regua
    xa, xb, ya, yb = ultima - 150, borda_1mm + 75, t0, t1

    from PIL import Image, ImageDraw

    def painel(b: int, titulo: str, medida: str, fundo) -> np.ndarray:
        r = pag[ya:yb, xa:xb].copy()
        # o que o corte joga fora fica cinza liso (fora da pagina final)
        r[:, b - xa:] = (205, 205, 205)
        r = cv2.resize(r, None, fx=esc, fy=esc, interpolation=cv2.INTER_CUBIC)
        # regua EMBAIXO, numa faixa branca a parte (nada desenhado em cima da imagem)
        regua = np.full((130, r.shape[1], 3), 255, np.uint8)
        xu, xbb = (ultima + 1 - xa) * esc, (b - xa) * esc
        cv2.line(regua, (xu, 0), (xu, 60), (0, 0, 0), 3)
        cv2.line(regua, (xbb, 0), (xbb, 60), (200, 0, 0), 3)
        cv2.line(regua, (xu, 30), (xbb, 30), (200, 0, 0), 3)
        pil = Image.fromarray(np.vstack([r, regua]))
        dr = ImageDraw.Draw(pil)
        f, fg = U.fonte(28), U.fonte(36)
        y0 = r.shape[0]
        largura_txt = dr.textlength("fim da última letra", font=f)
        dr.text((xu - largura_txt - 10, y0 + 70), "fim da última letra", font=f, fill=(0, 0, 0))
        dr.text((xbb + 12, y0 + 6), medida, font=fg, fill=(200, 0, 0))
        dr.text((xbb + 12, y0 + 70), "onde o corte passa", font=f, fill=(200, 0, 0))
        return U.rotulo(np.asarray(pil).copy(), titulo, fundo=fundo, tam=34,
                        sub="cinza liso = o que o corte tira (fica fora da página no PDF)")

    hoje = painel(borda, f"COMO ESTÁ: {folga_hoje:.1f} mm de papel depois do 'Ã'".replace(".", ","),
                  f"{folga_hoje:.1f} mm".replace(".", ","), (0, 115, 0))
    um = painel(borda_1mm, "SE FOR 1 mm: a borda vai um pouco mais para fora", "1 mm", (21, 101, 192))
    # contexto: o alto da pagina, SEM nada desenhado por cima. Nas faixas brancas de cima e de
    # baixo: um triangulo rosa apontando o canto ampliado e um traco vermelho onde passa o corte.
    ctx_peq = U.na_largura(pag[0:700, :].copy(), 1200)
    e = 1200 / W
    faixa = 46
    base = np.full((ctx_peq.shape[0] + 2 * faixa, ctx_peq.shape[1] + 30, 3), 255, np.uint8)
    base[faixa:faixa + ctx_peq.shape[0], 15:15 + ctx_peq.shape[1]] = ctx_peq
    xc = 15 + int((xa + xb) / 2 * e)
    tri = np.array([[xc - 18, 4], [xc + 18, 4], [xc, faixa - 6]], np.int32)
    cv2.fillPoly(base, [tri], COR_DETALHE[0])
    xr = 15 + int(borda * e)
    hb = faixa + ctx_peq.shape[0]
    cv2.line(base, (xr, 2), (xr, faixa - 4), (200, 0, 0), 3)
    cv2.line(base, (xr, hb + 4), (xr, hb + faixa - 2), (200, 0, 0), 3)
    contexto = U.rotulo(base, "Escola 7, o alto da página (original)", fundo=(90, 90, 90), tam=32,
                        sub="triângulo rosa (em cima) = o canto ampliado embaixo; traço vermelho (em cima e embaixo) = "
                            "onde passa a borda direita do corte de hoje. Nada desenhado em cima da página.")
    img = U.um_embaixo_do_outro([contexto, U.rotulo(U.um_embaixo_do_outro([hoje, um], espaco=24),
                                                    "O canto de 'CRISTÃ' ampliado 6 vezes", fundo=COR_DETALHE[0], tam=34)],
                                espaco=24)
    return U.gravar(img, SAIDA / "corte" / "corte-crista.jpg", qualidade=90, largura_max=LARGURA)


def main() -> None:
    feitos = []
    for nome, pagina, filtro, detalhes, titulo, cont in CARTOES:
        feitos.append(cartao(nome, pagina, filtro, detalhes, titulo, cont))
        print("  gravado", feitos[-1].name)
    feitos.append(tela())
    feitos.append(corte_crista())
    print(f"{len(feitos)} imagens em {SAIDA}")


if __name__ == "__main__":
    main()
