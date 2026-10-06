r"""Imagens "como ficaria" da conferencia 11 (05/10/2026). PROTOTIPO: nada aqui muda o programa.

Usa o codigo do programa do ramo fase2-misto (core.filtros, core.misto, core.selecao) sobre as
paginas preparadas pelo caminho do programa (comum11.preparada) e faz as variacoes AQUI:

  Q1 (P5)  Horas 13: Original | Preto e branco com a caixinha das molduras marcada | Misto.
           Nada simulado: aplicar_filtro_com_selecao(decoracao_em_preto_e_branco=True) e
           core.misto.aplicar_misto, como estao.
  Q2 (P6)  Escola 7, um retangulo "gravura ou foto" a mao em volta da pintura com "so neste
           pedaco: Original" (Regiao.filtro = ORIGINAL, como a aba Marcar grava):
             - Preto e branco de hoje (aplicar_filtro_com_selecao: o pedaco e ignorado);
             - SIMULACAO do conserto: o mesmo resultado passado por core.filtros._filtro_so_no_pedaco
               (o que o Misto e os outros filtros ja fazem);
             - Melhorar com o mesmo pedaco (aplicar_filtro_com_selecao, como esta).
  Q3 (P11) Marial 7, a mancha que o detector tomou por foto (a regiao de gravura que ele mesmo
           marcou), no Misto (core.misto.aplicar_misto):
             - como sai hoje no Misto;
             - "isto nao e gravura": a mesma area com "gravura ou foto" + "tirar" (o que a aba
               Marcar ja faz);
             - "papel": a mesma area marcada como papel (o que a aba Marcar ja faz);
             - SIMULACAO de "pintar de branco por cima" (zona de preenchimento do ScanTailor):
               depois do Misto, a area vira branco puro.
           Os dois tipos novos do ScanTailor, SIMULADOS pelo que o codigo dele faz
           (OutputGenerator.cpp, modifyBinarizationMask; DEDUCAO, primeira vez que se ve):
             - "tinta com a cor original, papel branco" (Add to foreground): dentro da zona, onde o
               preto e branco da pagina diz tinta, o ponto do original; o resto, branco;
             - "tinta preta, fundo original" (Add to background): onde diz tinta, preto puro; o
               resto, o ponto do original.
           Mais o que ja existe e chega perto do primeiro: "so neste pedaco: Original".
           No titulo da Horas 13 e no retrato do Palatino 5.

Grava os .jpg em relatorios/conferencia-11-2026-10-05/ (reduzidos) e um simular.json com o que
foi medido. Uso: .venv\Scripts\python.exe relatorios\conferencia-11-2026-10-05\scripts\simular.py
"""
from __future__ import annotations

import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import comum11

from core import filtros as F                      # noqa: E402
from core.misto import aplicar_misto               # noqa: E402
from core.selecao import (GRAVURA, LETRA, MAO, PAPEL, POLIGONO, RETANGULO,  # noqa: E402
                          SUBTRAIR, Regiao, _desenhar)

FONTE = ImageFont.truetype(r"C:/Windows/Fonts/segoeuib.ttf", 30)
FONTE_P = ImageFont.truetype(r"C:/Windows/Fonts/segoeui.ttf", 24)
CINZA = (170, 170, 170)
MEDIDAS: dict = {}


# --- montagem das imagens ------------------------------------------------------------------

def _pil(img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def _recorte(img, caixa):
    a, l = img.shape[:2]
    x0, y0, x1, y1 = caixa
    return img[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)]


def _com_rotulo(p: Image.Image, rotulo: str, sub: str = "") -> Image.Image:
    faixa = 46 + (32 if sub else 0)
    tela = Image.new("RGB", (p.width, p.height + faixa), (255, 255, 255))
    d = ImageDraw.Draw(tela)
    d.text((8, 6), rotulo, font=FONTE, fill=(0, 0, 0))
    if sub:
        d.text((8, 44), sub, font=FONTE_P, fill=(70, 70, 70))
    tela.paste(p, (0, faixa))
    return tela


def painel(imagens, rotulos, altura=1000, subs=None, colunas=None):
    """Lado a lado (ou em grade de `colunas`), cada parte com o rotulo numa faixa ACIMA dela
    (nada escrito por cima da pagina)."""
    subs = subs or [""] * len(imagens)
    partes = []
    for img, rot, sub in zip(imagens, rotulos, subs):
        p = _pil(img)
        p = p.resize((max(1, round(p.width * altura / p.height)), altura), Image.LANCZOS)
        partes.append(_com_rotulo(p, rot, sub))
    colunas = colunas or len(partes)
    linhas = [partes[i:i + colunas] for i in range(0, len(partes), colunas)]
    folga = 12
    larg = max(sum(p.width for p in ln) + folga * (len(ln) - 1) for ln in linhas)
    alts = [max(p.height for p in ln) for ln in linhas]
    tela = Image.new("RGB", (larg, sum(alts) + folga * (len(linhas) - 1)), CINZA)
    y = 0
    for ln, alt in zip(linhas, alts):
        x = 0
        for p in ln:
            tela.paste(p, (x, y))
            x += p.width + folga
        y += alt + folga
    return tela


def gravar(img: Image.Image, nome: str, largura_max=1600, qualidade=82):
    img = img.convert("RGB")
    if img.width > largura_max:
        img = img.resize((largura_max, round(img.height * largura_max / img.width)), Image.LANCZOS)
    img.save(comum11.AQUI / nome, quality=qualidade, optimize=True)
    print(nome, img.size, (comum11.AQUI / nome).stat().st_size // 1024, "KB", flush=True)


def contorno(img, caixa, cor=(220, 90, 0), grossura=None):
    """Copia da pagina com o contorno do retangulo (fracoes) desenhado POR FORA do pedaco."""
    out = F._tres_canais(img).copy()
    a, l = out.shape[:2]
    g = grossura or max(4, l // 300)
    x0, y0, x1, y1 = caixa
    cv2.rectangle(out, (int(x0 * l) - g, int(y0 * a) - g), (int(x1 * l) + g, int(y1 * a) + g), cor, g)
    return out


# --- as contas -----------------------------------------------------------------------------

def _misto(img, sel, aj):
    return aplicar_misto(img, sel, aj["forca_preto"], aj["algoritmo_pb"], aj["despeckle"],
                         aj["clareza"], aj["intensidade"])[0]


def _pb(img, sel, aj, decoracao=False):
    return F.aplicar_filtro_com_selecao(img, F.PRETO_E_BRANCO, sel, aj["forca_preto"], aj["clareza"],
                                        aj["intensidade"], algoritmo_pb=aj["algoritmo_pb"],
                                        despeckle=aj["despeckle"],
                                        decoracao_em_preto_e_branco=decoracao)[0]


def _zona(img, regiao) -> np.ndarray:
    tela = np.zeros(img.shape[:2], np.uint8)
    _desenhar(tela, regiao)
    return tela > 0


def _tinta(img, aj) -> np.ndarray:
    """Onde o preto e branco da pagina diz "tinta" (o mesmo preto e branco do Misto)."""
    return F.filtro_preto_e_branco(img, forca=aj["forca_preto"], algoritmo=aj["algoritmo_pb"],
                                   despeckle=aj["despeckle"]) == 0


def tinta_com_a_cor(base, img, zona, tinta):
    """SIMULACAO do "Add to foreground" do ScanTailor: na zona, tinta = original, papel = branco."""
    out = F._tres_canais(base).copy()
    img3 = F._tres_canais(img)
    out[zona & tinta] = img3[zona & tinta]
    out[zona & ~tinta] = 255
    return out


def tinta_preta_fundo_original(base, img, zona, tinta):
    """SIMULACAO do "Add to background" do ScanTailor: na zona, tinta = preto, o resto = original."""
    out = F._tres_canais(base).copy()
    img3 = F._tres_canais(img)
    out[zona & tinta] = 0
    out[zona & ~tinta] = img3[zona & ~tinta]
    return out


# --- Q1 ------------------------------------------------------------------------------------

def q1():
    img, sel, aj = comum11.preparada("horas_p013")
    marcada = _pb(img, sel, aj, decoracao=True)
    desmarcada = _pb(img, sel, aj, decoracao=False)
    misto = _misto(img, sel, aj)
    MEDIDAS["q1_misto_igual_pb_desmarcada"] = bool(
        misto.shape == F._tres_canais(desmarcada).shape and np.array_equal(misto, F._tres_canais(desmarcada)))
    rot = ["Original", "Caixinha marcada", "Misto (\"Só as letras\")"]
    subs = ["a página como veio", "moldura só com o traço preto", "a moldura fica com a cor"]
    gravar(painel([img, marcada, misto], rot, 1000, subs), "q1-horas13-moldura.jpg")
    caixa = (0.04, 0.06, 0.50, 0.30)
    gravar(painel([_recorte(x, caixa) for x in (img, marcada, misto)], rot, 520, subs),
           "q1-horas13-moldura-detalhe.jpg")


# --- Q2 ------------------------------------------------------------------------------------

ESCOLA_PEDACO = (0.375, 0.378, 0.997, 0.932)


def q2():
    img, sel, aj = comum11.preparada("escola_p007")
    com = comum11.copia(sel)
    com.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                           pontos=[ESCOLA_PEDACO[:2], ESCOLA_PEDACO[2:]], origem=MAO,
                           filtro=F.ORIGINAL))
    hoje = _pb(img, com, aj)
    sem_pedaco = _pb(img, sel, aj)
    MEDIDAS["q2_pb_hoje_igual_sem_pedaco"] = bool(np.array_equal(hoje, sem_pedaco))
    consertado = F._filtro_so_no_pedaco(img, hoje, com, F.PRETO_E_BRANCO, aj["forca_preto"],
                                        aj["clareza"], aj["intensidade"])
    melhorar = F.aplicar_filtro_com_selecao(img, F.MELHORAR, com, aj["forca_preto"], aj["clareza"],
                                            aj["intensidade"])[0]
    rot = ["Original", "Preto e branco hoje", "Consertado (simulação)", "Melhorar hoje"]
    subs = ["laranja: o pedaço marcado", "o pedaço é ignorado", "o pedaço sai em Original",
            "o pedaço já vale"]
    gravar(painel([contorno(img, ESCOLA_PEDACO), hoje, consertado, melhorar], rot, 1000, subs),
           "q2-escola7-pedaco.jpg")
    caixa = (0.36, 0.36, 1.0, 0.96)
    gravar(painel([_recorte(x, caixa) for x in (hoje, consertado, melhorar)], rot[1:], 700, subs[1:]),
           "q2-escola7-pedaco-detalhe.jpg")


# --- Q3 ------------------------------------------------------------------------------------

def q3_marial():
    img, sel, aj = comum11.preparada("marial_p007")
    mancha = next(r for r in sel.regioes if r.tipo == GRAVURA and r.operacao != SUBTRAIR)
    hoje = _misto(img, sel, aj)

    tirar = comum11.copia(sel)
    tirar.acrescentar(Regiao(tipo=GRAVURA, forma=mancha.forma, pontos=list(mancha.pontos),
                             operacao=SUBTRAIR, origem=MAO))
    nao_e_gravura = _misto(img, tirar, aj)

    papel = comum11.copia(sel)
    papel.acrescentar(Regiao(tipo=PAPEL, forma=mancha.forma, pontos=list(mancha.pontos), origem=MAO))
    como_papel = _misto(img, papel, aj)

    zona = _zona(img, mancha)
    # a area do programa tem borda suave (a gravura se mistura alguns pontos para fora do
    # contorno): o branco cobre o contorno e mais essa borda, senao fica um risco creme em volta
    raio = max(3, int(2 * mancha.suavidade * min(img.shape[:2])) + 2)
    zona = cv2.dilate(zona.astype(np.uint8), cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))) > 0
    branco = F._tres_canais(hoje).copy()
    branco[zona] = 255
    # quanta tinta de letra cai dentro da area que o programa marcou (o que o branco apagaria)
    letra = sel.mascara(img.shape[0], img.shape[1], LETRA)
    tinta = _tinta(img, aj)
    MEDIDAS["q3_marial_pontos_de_tinta_de_letra_na_mancha"] = int(np.count_nonzero(zona & tinta & letra))

    rot = ["Original", "Misto hoje", "\"Não é gravura\"", "Marcar como papel", "Pintar de branco"]
    subs = ["a página como veio", "a mancha fica marrom", "já existe (gravura + tirar)", "já existe",
            "simulação"]
    caixa = (0.0, 0.0, 0.42, 0.30)
    gravar(painel([_recorte(x, caixa) for x in (img, hoje, nao_e_gravura, como_papel, branco)],
                  rot, 560, subs, colunas=3), "q3-marial7-mancha.jpg")
    # onde fica a area que o programa marcou (contorno laranja), na pagina inteira
    marca = F._tres_canais(img).copy()
    cnt, _h = cv2.findContours(zona.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(marca, cnt, -1, (0, 110, 255), max(4, img.shape[1] // 300))
    gravar(painel([marca, hoje, branco], ["A área que o programa marcou", "Misto hoje",
                                          "Pintar de branco (simulação)"], 900),
           "q3-marial7-pagina.jpg")


TITULO_H13 = (0.115, 0.118, 0.765, 0.272)


def q3_tipos_novos():
    # Horas 13: o titulo vermelho e azul
    img, sel, aj = comum11.preparada("horas_p013")
    hoje = _misto(img, sel, aj)
    reg = Regiao(tipo=LETRA, forma=RETANGULO, pontos=[TITULO_H13[:2], TITULO_H13[2:]], origem=MAO)
    zona = _zona(img, reg)
    tinta = _tinta(img, aj)
    ja = comum11.copia(sel)
    ja.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[TITULO_H13[:2], TITULO_H13[2:]],
                          origem=MAO, filtro=F.ORIGINAL))
    so_original = _misto(img, ja, aj)
    fg = tinta_com_a_cor(hoje, img, zona, tinta)
    bg = tinta_preta_fundo_original(hoje, img, zona, tinta)
    rot = ["Original", "Misto hoje", "Já existe: \"só neste pedaço: Original\"",
           "Novo: tinta com a cor, papel branco", "Novo: tinta preta, fundo original"]
    subs = ["a página como veio", "o título sai preto", "título marcado como letra, com Original",
            "simulação (dedução do ScanTailor)",
            "simulação (dedução do ScanTailor)"]
    caixa = (0.09, 0.10, 0.79, 0.29)
    gravar(painel([_recorte(x, caixa) for x in (img, hoje, so_original, fg, bg)], rot, 420, subs,
                  colunas=1), "q3-horas13-titulo-tipos.jpg", largura_max=1100)

    # Palatino 5: o retrato (a zona e a propria area de gravura que o programa achou)
    img, sel, aj = comum11.preparada("palatino_p005")
    retrato = next(r for r in sel.regioes if r.tipo == GRAVURA and r.operacao != SUBTRAIR)
    hoje = _misto(img, sel, aj)
    zona = _zona(img, retrato)
    tinta = _tinta(img, aj)
    ja = comum11.copia(sel)
    ja.acrescentar(Regiao(tipo=GRAVURA, forma=retrato.forma, pontos=list(retrato.pontos), origem=MAO,
                          filtro=F.ORIGINAL))
    so_original = _misto(img, ja, aj)
    fg = tinta_com_a_cor(hoje, img, zona, tinta)
    bg = tinta_preta_fundo_original(hoje, img, zona, tinta)
    rot = ["Original", "Misto hoje", "Já existe: \"só neste pedaço\"",
           "Novo: tinta com a cor", "Novo: tinta preta"]
    subs = ["a página como veio", "traço do original, papel branco", "Original",
            "papel branco (simulação)", "fundo original (simulação)"]
    caixa = (0.22, 0.36, 0.78, 0.66)
    gravar(painel([_recorte(x, caixa) for x in (img, hoje, so_original, fg, bg)], rot, 620, subs,
                  colunas=3), "q3-palatino5-retrato-tipos.jpg")


if __name__ == "__main__":
    import sys

    quais = sys.argv[1:] or ["q1", "q2", "q3_marial", "q3_tipos_novos"]
    for q in quais:
        globals()[q]()
    js = comum11.AQUI / "scripts" / "simular.json"
    antigo = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
    antigo.update(MEDIDAS)
    js.write_text(json.dumps(antigo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(MEDIDAS)
