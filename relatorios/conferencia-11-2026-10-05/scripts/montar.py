r"""Junta e reduz imagens prontas para o formulario conferir-aqui-11.html (05/10/2026).
Nenhuma pagina e processada; o programa nao e tocado. Fontes (somente leitura):
  - q1-caixinha-hoje.png e q1-caixinha-simulacao.png (feitas por tela.py);
  - prints da janela real do verificador, 05/10:
    D:\programas\EditorImpressao\relatorios\conferir\consertos-janela-2026-10-05\verificador\prints\
    (16-caixa-antes-de-substituir.png, 17-depois-de-cancelar.png);
  - print da aba Marcar de 02/10: D:\programas\EditorImpressao\relatorios\prints-telas-2026-10-02\
    conferir-marcar-1280x657.png;
  - imagens do formulario 10 (P2, P3, P4): relatorios/conferencia-10-2026-10-05/ (ramo fase2-misto).
Uso: .venv\Scripts\python.exe relatorios\conferencia-11-2026-10-05\scripts\montar.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parents[1]
CONF10 = AQUI.parent / "conferencia-10-2026-10-05"
VERIF = Path(r"D:\programas\EditorImpressao\relatorios\conferir\consertos-janela-2026-10-05\verificador\prints")
PRINTS = Path(r"D:\programas\EditorImpressao\relatorios\prints-telas-2026-10-02")
FONTE = ImageFont.truetype(r"C:/Windows/Fonts/segoeuib.ttf", 26)
CINZA = (170, 170, 170)


def rotulo(p: Image.Image, texto: str) -> Image.Image:
    tela = Image.new("RGB", (p.width, p.height + 44), (255, 255, 255))
    ImageDraw.Draw(tela).text((8, 6), texto, font=FONTE, fill=(0, 0, 0))
    tela.paste(p.convert("RGB"), (0, 44))
    return tela


def empilhar(partes, folga=12):
    larg = max(p.width for p in partes)
    tela = Image.new("RGB", (larg, sum(p.height for p in partes) + folga * (len(partes) - 1)), CINZA)
    y = 0
    for p in partes:
        tela.paste(p, (0, y))
        y += p.height + folga
    return tela


def gravar(img, nome, largura_max=1600, qualidade=85):
    img = img.convert("RGB")
    if img.width > largura_max:
        img = img.resize((largura_max, round(img.height * largura_max / img.width)), Image.LANCZOS)
    img.save(AQUI / nome, quality=qualidade, optimize=True)
    print(nome, img.size, (AQUI / nome).stat().st_size // 1024, "KB")


def dobro(p):
    return p.resize((p.width * 2, p.height * 2), Image.LANCZOS)


# Q1: a caixinha hoje e como ficaria
hoje = Image.open(AQUI / "q1-caixinha-hoje.png")
sim = Image.open(AQUI / "q1-caixinha-simulacao.png")
gravar(empilhar([rotulo(dobro(hoje), "Hoje (tela \"O que fazer\", Preto e branco escolhido)"),
                 rotulo(dobro(sim), "Como ficaria na opção (a): SIMULAÇÃO")]), "q1-caixinha.jpg", 1100)

# Q2: a aba Marcar e o "só neste pedaço" (painel da direita do print 17)
marcar = Image.open(PRINTS / "conferir-marcar-1280x657.png")
gravar(marcar, "q2-aba-marcar.jpg", 1600)
p17 = Image.open(VERIF / "17-depois-de-cancelar.png")
gravar(p17.crop((1355, 285, 1560, 615)), "q2-so-neste-pedaco.jpg", 400)

# Q4: a caixa "substituir o antigo" e a tela depois de cancelar
gravar(Image.open(VERIF / "16-caixa-antes-de-substituir.png"), "q4-caixa-substituir.jpg", 700)
gravar(p17, "q4-depois-de-cancelar.jpg", 1600)

# Q6 a Q8: as imagens do formulario 10, como estavam
for nome in ("p2-palatino_p005.jpg", "p2-palatino_p005-detalhe.jpg", "p3-escola_p007.jpg",
             "p3-opusmajus_p020.jpg", "p4-horas_p011-detalhe.jpg"):
    shutil.copyfile(CONF10 / nome, AQUI / nome)
    print("copiada", nome)
