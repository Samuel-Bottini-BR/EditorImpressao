"""Prints do estudo D-701, no modelo do girar (faixa com nome: azul = como é hoje, verde = opção
recomendada, laranja = a outra opção, cinza-escuro = o scan; o que olhar em vermelho; uma frase em
cada imagem). Lê as imagens do m4 (o programa de hoje, caminho inteiro) e do m5 (a simulação do
conserto, fora do programa). Grava em prints/.

    python m6_prints.py <pasta do m5 a usar, ex.: m5-v3>
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
os.environ.setdefault("M5_PESO_L", "0.15")
os.environ.setdefault("M5_LIMIAR", "10")
from m5_prototipo import cor_por_palavra  # noqa: E402

DADOS = AQUI.parent / "_dados"
M1, M4 = DADOS / "m1", DADOS / "m4"
M5 = DADOS / (sys.argv[1] if len(sys.argv) > 1 else "m5-v3")
PRINTS = AQUI.parent / "prints"
PRINTS.mkdir(exist_ok=True)
LARG = 1500
CORES = {"azul": (59, 91, 151), "verde": (27, 130, 59), "laranja": (204, 102, 0), "escuro": (40, 40, 40)}
FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
# trecho "S. Leonard" a "S. Theodore" (pontos da página a 300 DPI)
TRECHO = (1530, 2010, 560, 2400)


def fonte(t, negrito=False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, t)


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=f) > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = teste
    linhas.append(atual)
    return linhas


def faixa(titulo, frase, cor):
    f_t, f_f = fonte(40, True), fonte(26)
    rasc = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    linhas = quebrar(frase, f_f, LARG - 40, rasc) if frase else []
    alt = 80 + 36 * len(linhas) + (16 if linhas else 0)
    im = Image.new("RGB", (LARG, alt), (250, 248, 243))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, LARG, 72], fill=CORES[cor])
    d.text((20, 12), titulo, font=f_t, fill="white")
    for i, l in enumerate(linhas):
        d.text((20, 84 + 36 * i), l, font=f_f, fill=(30, 30, 30))
    return im


def quadro(img_bgr, alvos=(), largura=1200):
    """A imagem com borda cinza, centralizada, com elipses vermelhas em `alvos` (frações x0,y0,x1,y1)."""
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    esc = largura / rgb.shape[1]
    rgb = cv2.resize(rgb, (largura, int(rgb.shape[0] * esc)), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(rgb)
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in alvos:
        W, H = im.size
        d.ellipse([x0 * W, y0 * H, x1 * W, y1 * H], outline=(220, 0, 0), width=5)
    fundo = Image.new("RGB", (LARG, im.size[1] + 40), (250, 248, 243))
    x = (LARG - im.size[0]) // 2
    ImageDraw.Draw(fundo).rectangle([x - 2, 18, x + im.size[0] + 1, 20 + im.size[1] + 1], outline=(180, 180, 180))
    fundo.paste(im, (x, 20))
    return fundo


def lado_a_lado(esq, dir_, rot_e, rot_d, alvos=()):
    """Duas imagens BGR do mesmo tamanho, lado a lado, com um rótulo em cima de cada."""
    h = max(esq.shape[0], dir_.shape[0])
    esp = np.full((h, 30, 3), 255, np.uint8)
    junto = np.hstack([esq, esp, dir_])
    im = quadro(junto, alvos, largura=1440)
    d = ImageDraw.Draw(im)
    f = fonte(24, True)
    d.text((40, 0), rot_e, font=f, fill=(30, 30, 30))
    d.text((LARG // 2 + 10, 0), rot_d, font=f, fill=(30, 30, 30))
    return im


def empilhar(partes, nome):
    alt = sum(p.size[1] for p in partes)
    im = Image.new("RGB", (LARG, alt), (250, 248, 243))
    y = 0
    for p in partes:
        im.paste(p, (0, y))
        y += p.size[1]
    im.save(PRINTS / nome)
    print("gravado", nome, im.size)


def trecho(img, fator=None, trecho=TRECHO, largura_px=900):
    f = img.shape[0] / 5709 if fator is None else fator
    y0, y1, x0, x1 = (int(v * f) for v in trecho)
    c = img[y0:y1, x0:x1]
    return cv2.resize(c, (largura_px, int(largura_px * c.shape[0] / c.shape[1])),
                      interpolation=cv2.INTER_AREA if c.shape[1] > largura_px else cv2.INTER_CUBIC)


def ler(p):
    im = cv2.imread(str(p))
    if im is None:
        raise FileNotFoundError(p)
    return im


def main():
    scan = ler(M1 / "original.png")
    hoje300, hoje110 = ler(M4 / "horas_p026_300_reduzir.png"), ler(M4 / "horas_p026_110_reduzir.png")
    letras300 = ler(M4 / "horas_p026_300_letras.png")
    caminho = ("Livro de Horas, página 26, livro novo de fábrica: endireitada, cortada, Preto e branco + "
               "\"Letras com a cor delas\" + \"Reduzir cores\".")
    # 1) por que: cada letra com a média dela; a divisa no meio; as cores emprestadas
    alvos = [(0.0, 0.0, 0.33, 0.25), (0.0, 0.73, 0.40, 1.0)]
    titulo = scan[700:930, 600:2900]
    beirada = hoje300[2000:2600, 3120:3277]
    tit_hoje = hoje300[700:930, 600:2900]
    p = [faixa("O SCAN (filtro Original)", "Cada palavra é de uma tinta só, cinza-escura.", "escuro"),
         quadro(trecho(scan)),
         faixa("SÓ \"LETRAS COM A COR DELAS\" (hoje)",
               "Cada letra sai com a cor média DELA. Letra de traço grosso dá média mais escura; letra fina, "
               "mais clara. A diferença é pequena: ainda parece uma tinta só.", "azul"),
         quadro(trecho(letras300)),
         faixa("+ \"REDUZIR CORES\" (hoje, no PDF)",
               caminho + " A redução corta as cores em caixas fixas, e a divisa cai no meio das letras: as "
               "escuras vão para uma caixa, as claras para outra. Em vermelho, \"S. Leonard\" e \"S. Theodore\".",
               "azul"),
         quadro(trecho(hoje300), alvos),
         faixa("DE ONDE VÊM O AZUL E O BEGE",
               "Cada caixa sai com a cor que mais aparece dentro dela, venha de onde vier. A caixa das letras "
               "escuras pega o azul do título \"NOVEMBRE.\" (à esquerda); a das letras claras pega o bege da "
               "beirada da folha (à direita).", "azul"),
         lado_a_lado(cv2.resize(tit_hoje, (700, 70)),
                     np.hstack([np.full((70, 320, 3), 255, np.uint8), cv2.resize(beirada, (60, 70)),
                                np.full((70, 320, 3), 255, np.uint8)]),
                     "o título, no PDF de hoje", "a beirada da folha")]
    empilhar(p, "1-por-que-duas-cores.png")

    # 2) a prévia não mostra o mesmo que o PDF (hoje)
    e = trecho(hoje110, largura_px=700)
    d_ = trecho(hoje300, largura_px=700)
    p = [faixa("HOJE: A TELA E O PDF NÃO MOSTRAM AS MESMAS CORES",
               caminho + " À esquerda, a página na tela (prévia); à direita, a mesma página no PDF. As "
               "letras que saem azuis não são as mesmas nas duas. Em vermelho: \"Martyr\" sai todo azul na tela; "
               "no PDF, só o \"M\" sai azul e o resto bege.", "azul"),
         lado_a_lado(e, d_, "na tela (prévia)", "no PDF", [(0.18, 0.70, 0.33, 1.0), (0.69, 0.70, 0.84, 1.0)])]
    empilhar(p, "2-hoje-tela-diferente-do-pdf.png")

    # 3) as duas opções (simulação, fora do programa)
    b110, b300 = ler(M5 / "horas_p026_110_B.png"), ler(M5 / "horas_p026_300_B.png")
    a110, a300 = ler(M5 / "horas_p026_110_A.png"), ler(M5 / "horas_p026_300_A.png")
    p = [faixa("COMO É HOJE", "Na mesma palavra, letras azuis e letras bege; e a tela mostra outras cores "
               "que o PDF.", "azul"),
         lado_a_lado(trecho(hoje110, largura_px=700), trecho(hoje300, largura_px=700), "na tela", "no PDF"),
         faixa("OPÇÃO 1 (recomendo): A MESMA TINTA, A MESMA COR",
               "Simulação do conserto (fora do programa). Cada palavra sai numa cor só, e as palavras da "
               "mesma tinta saem todas iguais, como no scan. A tela e o PDF mostram a mesma cor.", "verde"),
         lado_a_lado(trecho(b110, largura_px=700), trecho(b300, largura_px=700), "na tela", "no PDF"),
         faixa("OPÇÃO 2: CADA PALAVRA NUMA COR, COM A CONTA DO SCANTAILOR",
               "Simulação. Cada palavra sai numa cor só, mas uma palavra pode sair azul e a vizinha bege, e a "
               "tela continua mostrando outras cores que o PDF.", "laranja"),
         lado_a_lado(trecho(a110, largura_px=700), trecho(a300, largura_px=700), "na tela", "no PDF"),
         faixa("O SCAN", "", "escuro"),
         lado_a_lado(trecho(scan, largura_px=700), trecho(scan, largura_px=700), "", "")]
    empilhar(p, "3-opcoes-horas-26-antigo.png")

    # 4) o que já funciona continua: título vermelho e azul (Horas 13), pauta e rubrica vermelhas (Graduale)
    h13h, h13b = ler(M4 / "horas_p013_300_reduzir.png"), ler(M5 / "horas_p013_300_B.png")
    grh, grb = ler(M4 / "graduale_p223_300_reduzir.png"), ler(M5 / "graduale_p223_300_B.png")

    def meio(img, y0, y1, x0, x1):
        H, W = img.shape[:2]
        c = img[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
        return cv2.resize(c, (700, int(700 * c.shape[0] / c.shape[1])), interpolation=cv2.INTER_AREA)

    p = [faixa("LIVRO DE HORAS, PÁGINA 13: TÍTULO VERMELHO E AZUL",
               "Livro novo de fábrica, Preto e branco + \"Letras com a cor delas\" + \"Reduzir cores\". O "
               "vermelho continua vermelho e o azul continua azul; o texto passa a sair numa cor só.", "verde"),
         lado_a_lado(meio(h13h, 0.12, 0.45, 0.1, 0.9), meio(h13b, 0.12, 0.45, 0.1, 0.9), "hoje, no PDF",
                     "opção 1 (simulação), no PDF"),
         faixa("GRADUALE, PÁGINA 223: PAUTA E PALAVRA VERMELHAS",
               "O mesmo caminho. A pauta vermelha e a palavra vermelha \"com.\" continuam vermelhas, separadas "
               "das notas e das letras pretas que encostam nelas.", "verde"),
         lado_a_lado(meio(grh, 0.50, 0.72, 0.05, 0.9), meio(grb, 0.50, 0.72, 0.05, 0.9), "hoje, no PDF",
                     "opção 1 (simulação), no PDF")]
    empilhar(p, "4-o-que-funciona-continua.png")

    # 5) pergunta 2: só "Letras com a cor delas", sem "Reduzir cores"
    tinta = cv2.cvtColor(ler(M4 / "horas_p026_300_pb.png"), cv2.COLOR_BGR2GRAY) == 0
    so_palavra, _, _ = cor_por_palavra(letras300, tinta)
    cv2.imwrite(str(M5 / "horas_p026_300_letras_palavra.png"), so_palavra)
    p = [faixa("SÓ \"LETRAS COM A COR DELAS\", COMO É HOJE",
               "Livro de Horas, página 26, Preto e branco + \"Letras com a cor delas\" (sem \"Reduzir cores\"). "
               "Cada letra com a cor média dela: em \"Godefroy\", o \"Go\" sai mais escuro que o \"defroy\".",
               "azul"),
         quadro(trecho(letras300), [(0.0, 0.47, 0.43, 0.75)]),
         faixa("SE TAMBÉM VALER \"CADA PALAVRA NUMA COR\"",
               "Simulação. A palavra inteira com a cor média dela; uma palavra pode ser um pouco mais clara "
               "que a outra, como no scan.", "verde"),
         quadro(trecho(so_palavra), [(0.0, 0.47, 0.43, 0.75)])]
    empilhar(p, "5-so-letras-com-a-cor.png")




# --- Print 3, refeito em 14/11 a pedido da gerente (§11.13 regra 3: a imagem prova o que o texto diz) ---
# Medida em m8_vizinhas.py: no PDF a diferença entre as opções é de no máximo 4,5 (LAB) entre palavras
# vizinhas - pequena demais para se ver; na tela (prévia, 110) a opção 2 deixa a letra grande do começo
# ("N" de "Neocefarée", "M" de "Martyr") mais escura que o resto (diferença 10 a 13), e a opção 1 não.
RECORTES = {  # frações da página (y0, y1, x0, x1): "de Neocefarée." e "& Martyr."
    "neocefaree": (0.4847, 0.5180, 0.682, 0.925),
    "martyr": (0.6065, 0.6400, 0.430, 0.680),
}
ALVO = {"neocefaree": (0.22, 0.02, 1.0, 1.0), "martyr": (0.27, 0.02, 1.0, 1.0)}


def recorte(img, nome, largura=700):
    y0, y1, x0, x1 = RECORTES[nome]
    H, W = img.shape[:2]
    c = img[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    return cv2.resize(c, (largura, int(largura * c.shape[0] / c.shape[1])), interpolation=cv2.INTER_CUBIC)


def par(img, rot_e="", rot_d=""):
    e, d = recorte(img, "neocefaree"), recorte(img, "martyr")
    h = max(e.shape[0], d.shape[0])
    e = cv2.copyMakeBorder(e, 0, h - e.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    d = cv2.copyMakeBorder(d, 0, h - d.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    # elipses: a palavra em cada recorte (o lado esquerdo vai de 0 a 0,489 da largura junta)
    a1, a2 = ALVO["neocefaree"], ALVO["martyr"]
    alvos = [(a1[0] * 0.489, a1[1], a1[2] * 0.489, a1[3]),
             (0.511 + a2[0] * 0.489, a2[1], 0.511 + a2[2] * 0.489, a2[3])]
    return lado_a_lado(e, d, rot_e, rot_d, alvos)


def resumo(scan, hoje, op1, op2):
    """A imagem-resumo: título, a linha do caminho e as três saídas no PDF, pequenas, lado a lado."""
    f_t, f_f, f_r = fonte(40, True), fonte(26), fonte(24, True)
    topo = Image.new("RGB", (LARG, 170), (250, 248, 243))
    d = ImageDraw.Draw(topo)
    d.rectangle([0, 0, LARG, 72], fill=CORES["escuro"])
    d.text((20, 12), "CADA PALAVRA NUMA COR SÓ: AS DUAS OPÇÕES", font=f_t, fill="white")
    for i, l in enumerate(quebrar("Livro de Horas, página 26, livro novo de fábrica (endireitada, cortada) · Preto e "
                                  "branco + \"Letras com a cor delas\" + \"Reduzir cores\" · as opções 1 e 2 são "
                                  "simulação do conserto, fora do programa.", f_f, LARG - 40, d)):
        d.text((20, 84 + 36 * i), l, font=f_f, fill=(30, 30, 30))
    cols = []
    for img in (hoje, op1, op2):
        c = trecho(img, largura_px=470)
        cols.append(cv2.copyMakeBorder(c, 0, 0, 10, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255)))
    junto = np.hstack(cols)
    meio = quadro(junto, largura=1460)
    dm = ImageDraw.Draw(meio)
    for i, (t, cor) in enumerate((("hoje", CORES["azul"]), ("opção 1", CORES["verde"]), ("opção 2", CORES["laranja"]))):
        dm.text((30 + i * 487, 0), t + " (no PDF)", font=f_r, fill=cor)
    frase = faixa("O QUE O RESUMO MOSTRA",
                  "Hoje a mesma palavra sai azul e bege. Nas duas opções cada palavra sai numa cor só. No PDF as "
                  "opções 1 e 2 ficam quase iguais: a diferença entre elas é pequena demais para se ver. Ela "
                  "aparece na tela (a prévia), ampliada abaixo.", "escuro")
    return [topo, meio, frase]


def print3_novo():
    scan = ler(M1 / "original.png")
    hoje300, hoje110 = ler(M4 / "horas_p026_300_reduzir.png"), ler(M4 / "horas_p026_110_reduzir.png")
    b110, b300 = ler(M5 / "horas_p026_110_B.png"), ler(M5 / "horas_p026_300_B.png")
    a110, a300 = ler(M5 / "horas_p026_110_A.png"), ler(M5 / "horas_p026_300_A.png")
    p = resumo(scan, hoje300, b300, a300)
    p += [faixa("NA TELA, COMO É HOJE",
                "\"de Neocefarée.\" e \"& Martyr.\", ampliados. Letras azuis e letras bege na mesma palavra.", "azul"),
          par(hoje110),
          faixa("NA TELA, OPÇÃO 1 (recomendo): A MESMA TINTA, A MESMA COR",
                "As mesmas palavras: \"Neocefarée\" e \"Martyr\" saem inteiras numa cor só, a mesma das palavras "
                "vizinhas \"de\" e \"&\". O \"N\" e o \"M\", de traço grosso, parecem um pouco mais "
                "escuros só por serem grossos: a cor é a mesma (medida).", "verde"),
          par(b110),
          faixa("NA TELA, OPÇÃO 2: CADA PALAVRA, COM A CONTA DO SCANTAILOR",
                "As mesmas palavras: a letra grande do começo (o \"N\" e o \"M\") ainda sai mais escura que o resto "
                "da palavra e que as vizinhas \"de\" e \"&\". A diferença é pequena, mas se vê ampliada.", "laranja"),
          par(a110),
          faixa("NO PDF: OPÇÃO 1 (esquerda) E OPÇÃO 2 (direita)",
                "\"Neocefarée\" no PDF. Aqui a diferença entre as duas opções é pequena demais para se ver: as "
                "duas saem numa cor só.", "escuro"),
          lado_a_lado(recorte(b300, "neocefaree"), recorte(a300, "neocefaree"), "opção 1", "opção 2",
                      [(0.11, 0.02, 0.49, 1.0), (0.62, 0.02, 1.0, 1.0)]),
          faixa("O SCAN", "As mesmas palavras no scan (filtro Original): uma tinta só.", "escuro"),
          par(scan)]
    empilhar(p, "3-opcoes-horas-26.png")


if __name__ == "__main__":
    main()
    print3_novo()
