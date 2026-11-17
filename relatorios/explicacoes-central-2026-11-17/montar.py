"""Monta as imagens das explicações (17/11/2026) no modelo do girar (docs/plano/central/modelo-de-print,
CLAUDE.md §10): imagem-resumo primeiro; uma faixa por situação, com cor e título grande (azul = como
é hoje / antes do clique; verde = depois do clique ou a opção recomendada; laranja = a outra opção);
uma frase embaixo de cada título; o que olhar circulado em vermelho, sem cobrir o conteúdo.

    python montar.py [item ...]        (sem item: todos os que têm os prints crus prontos)

Os prints crus ficam em crus/<piloto>/; as imagens prontas em prints/<item>/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
CRUS = AQUI / "crus"
SAIDA = AQUI / "prints"
FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL, LARANJA, VERDE, CINZA = (60, 90, 150), (190, 90, 10), (25, 130, 60), (40, 40, 40)
LEGENDAS: dict = {}


def fonte(t, negrito=False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, t)


def quebrar(texto, f, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if f.getlength(teste) > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def cabeca(rotulo, cor, legenda, largura=LARGURA):
    """A faixa colorida com o rótulo grande e, embaixo, a frase do que olhar."""
    f_rot, f_leg = fonte(44, True), fonte(26)
    linhas = quebrar(legenda, f_leg, largura - 40) if legenda else []
    img = Image.new("RGB", (largura, 84 + 14 + 36 * len(linhas) + 6), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 84], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, t in enumerate(linhas):
        d.text((20, 98 + 36 * n), t, fill=(30, 30, 30), font=f_leg)
    return img


def texto(t, tamanho=26, negrito=False, largura=LARGURA - 40, cor=(30, 30, 30)):
    f = fonte(tamanho, negrito)
    linhas = quebrar(t, f, largura)
    alt = int(tamanho * 1.4)
    img = Image.new("RGB", (largura, alt * len(linhas) + 6), FUNDO)
    d = ImageDraw.Draw(img)
    for n, l in enumerate(linhas):
        d.text((0, n * alt), l, fill=cor, font=f)
    return img


def empilhar(partes, espaco=16, largura=LARGURA):
    # nada passa da largura (senão a beirada da imagem cortaria um pedaço)
    partes = [p if p.width <= largura - 20 else caber(p, largura - 20, 100_000) for p in partes]
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def caber(img, cl, ca):
    e = min(cl / img.width, ca / img.height)
    return img.resize((max(1, round(img.width * e)), max(1, round(img.height * e))), Image.LANCZOS)


def circular(img, caixas, folga=14, largura=6):
    """Círculo (elipse) vermelho em volta de cada caixa (x0, y0, x1, y1), por fora dela."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in caixas:
        d.ellipse([x0 - folga, y0 - folga, x1 + folga, y1 + folga], outline=VERMELHO, width=largura)
    return img


def sublinhar(img, caixas, largura=6):
    """Retângulo vermelho de contorno (para caixas largas, onde a elipse ficaria enorme)."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in caixas:
        d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], radius=10, outline=VERMELHO, width=largura)
    return img


def lado_a_lado(imagens, titulos, caixa_l, caixa_a, cores_titulo=None, espaco=24):
    """Imagens lado a lado, cada uma com o título (negrito) em cima."""
    f = fonte(28, True)
    cel = [caber(i, caixa_l, caixa_a) for i in imagens]
    largura = sum(c.width for c in cel) + espaco * (len(cel) - 1)
    alt = max(c.height for c in cel) + 48
    img = Image.new("RGB", (largura, alt), FUNDO)
    d = ImageDraw.Draw(img)
    x = 0
    for n, (c, t) in enumerate(zip(cel, titulos)):
        cor = (cores_titulo or {}).get(n, (30, 30, 30))
        d.text((x + c.width / 2, 4), t, fill=cor, font=f, anchor="mt")
        img.paste(c, (x, 46))
        d.rectangle([x - 1, 45, x + c.width, 46 + c.height], outline=(150, 150, 150))
        x += c.width + espaco
    return img


def janela(nome_cru, recorte=None):
    """Um print da janela, sem a barra de título do Windows (e recortado, se pedido)."""
    img = Image.open(nome_cru).convert("RGB")
    if recorte is None:
        recorte = (0, 38, img.width, img.height)
    return img.crop(recorte)


def salvar(img, item, nome, legenda):
    pasta = SAIDA / item
    pasta.mkdir(parents=True, exist_ok=True)
    if img.width > 1600:
        img = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
    destino = pasta / nome
    img.save(destino, optimize=True)
    LEGENDAS.setdefault(item, {})[nome] = legenda
    print("ok", destino.relative_to(AQUI), img.size)
    return destino


def gravar_legendas():
    for item, leg in LEGENDAS.items():
        (SAIDA / item / "legendas.json").write_text(json.dumps(leg, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# coordenadas na janela de 1280 x 657 (print de 1618 x 868, já sem a barra de título: y - 38)
NOME_DA_FERRAMENTA = (728, 10, 870, 40)          # "Mão" / "Dividir a folha" no alto
CONTADOR = (74, 788, 236, 812)                   # "página 1 de 24" / "folha 4 de 12" embaixo
TIRA = (66, 668, 880, 770)
SEM_PAINEL = (0, 38, 1180, 868)                  # a janela sem o painel da direita


def item_501():
    d = CRUS / "dividir"
    reaberto = circular(janela(d / "09-reabriu.png"), [NOME_DA_FERRAMENTA, CONTADOR])
    antes = circular(janela(d / "02-no-dividir-antes.png"), [NOME_DA_FERRAMENTA, (596, 86, 672, 470)])
    depois = circular(janela(d / "04-depois-do-automatico.png"), [NOME_DA_FERRAMENTA, CONTADOR])
    # sem o painel da direita: nele os botões do cartão da página 2 ficaram por cima do cartão da
    # página 7 (defeito de desenho achado nestes prints; relatado à gerente)
    pag2 = circular(janela(d / "06-cartao-pagina-2.png", SEM_PAINEL), [NOME_DA_FERRAMENTA, CONTADOR])
    pag7 = circular(janela(d / "07-cartao-pagina-7.png", SEM_PAINEL), [NOME_DA_FERRAMENTA, CONTADOR])

    p1 = empilhar([cabeca("1. Abrir o livro", AZUL,
                          "La vida eterna (cópia), já dividido, fechado e aberto de novo. Ele abre na página "
                          "1, uma página por vez, na ferramenta Mão (nome no alto, em vermelho). Não abre "
                          "na folha inteira do Dividir."),
                   caber(reaberto, 1400, 760)])
    salvar(p1, "au-d-501", "501-1-abrir-o-livro.png",
           "Parte 1. Livro já dividido, aberto de novo: abre na página 1 (Mão), uma página por vez.")

    p2 = empilhar([cabeca("2. Automático com \"Dividir\", estando no Dividir", AZUL,
                          "ANTES (em cima): ferramenta Dividir, a folha 1 inteira com a linha azul. Painel "
                          "Automático, só \"Dividir folhas ao meio\" marcado, \"Rodar 1 etapa\"."),
                   caber(antes, 1400, 700),
                   cabeca("Depois do \"Rodar\"", VERDE,
                          "A tela sai sozinha do Dividir e mostra a página 1 de 24, uma por vez, na Mão. "
                          "A tira de baixo passa a ter uma miniatura por página."),
                   caber(depois, 1400, 700)])
    salvar(p2, "au-d-501", "501-2-automatico-no-dividir.png",
           "Parte 2. Antes: Dividir com a folha inteira. Depois do Automático \"Dividir\": a página, uma por vez.")

    p3 = empilhar([cabeca("3. Clicar num aviso do \"Para revisar\"", AZUL,
                          "Clique no cartão \"Página 2 · Parece em branco\" do painel Para revisar (aviso "
                          "que NÃO é da divisão): a tela vai à página 2, na Mão."),
                   caber(pag2, 1400, 700),
                   cabeca("Aviso da divisão", VERDE,
                          "Clique no cartão \"Página 7 · Lombada incerta\" (o programa não tem certeza de onde fica o meio "
                          "da folha 4): o clique leva ao Dividir, na folha 4, para conferir a linha. "
                          "\"Duas lado a lado\" mostra a folha inteira com a linha."),
                   caber(pag7, 1400, 700)])
    salvar(p3, "au-d-501", "501-3-clicar-no-aviso.png",
           "Parte 3. Aviso comum leva à página; aviso da divisão (\"Lombada incerta\") leva ao Dividir.")

    def peq(img):
        return caber(img, 700, 380)
    resumo = empilhar([
        cabeca("Dividir: para onde a tela vai — resumo", CINZA,
               "La vida eterna (cópia, 12 folhas), dividido pelo Automático. Três momentos, um em cada "
               "faixa. Em vermelho: o nome da ferramenta (no alto) e o contador (embaixo)."),
        cabeca("1. Abrir o livro", AZUL, "Abre na página, uma por vez (Mão)."),
        peq(reaberto),
        cabeca("2. Automático \"Dividir\" estando no Dividir", AZUL,
               "Antes: folha inteira com a linha (esquerda). Depois: a página, uma por vez (direita)."),
        lado_a_lado([antes, depois], ["antes do Rodar", "depois do Rodar"], 700, 380),
        cabeca("3. Clicar num aviso", AZUL,
               "\"Parece em branco\" leva à página (esquerda). \"Lombada incerta\" leva ao Dividir (direita)."),
        lado_a_lado([pag2, pag7], ["aviso comum: página 2", "aviso da divisão: Dividir"], 700, 380),
    ])
    salvar(resumo, "au-d-501", "501-0-resumo.png", "Resumo: os três momentos, um em cada faixa.")


def item_500():
    d = CRUS / "dividir"
    linhas = json.loads((d / "linhas.json").read_text(encoding="utf-8"))
    folha = Image.open(d / "folha-4.png").convert("RGB")
    w, h = folha.size

    def com_linha(pos, cor):
        img = folha.copy()
        dr = ImageDraw.Draw(img)
        x = round(pos * w)
        for k in range(-5, 6):
            dr.line([(x + k, 0), (x + k, h)], fill=cor)
        return img
    st = com_linha(linhas["4"]["scantailor"], LARANJA)
    pr = com_linha(linhas["4"]["programa"], VERDE)
    pdf_st = [Image.open(d / f"pdf-scantailor-{i}.png").convert("RGB") for i in (3, 4)]
    pdf_pr = [Image.open(d / f"pdf-programa-{i}.png").convert("RGB") for i in (3, 4)]

    def paginas(imgs, nomes, circular_estreita=False):
        f = fonte(28, True)
        alt = 420
        cel = [caber(i, 10_000, alt) for i in imgs]
        larg = [max(c.width, int(f.getlength(n)) + 20) for c, n in zip(cel, nomes)]
        largura = sum(larg) + 40 * (len(cel) - 1)
        img = Image.new("RGB", (max(largura, 300), alt + 64), FUNDO)
        dr = ImageDraw.Draw(img)
        x = 0
        for c, n, lc in zip(cel, nomes, larg):
            dr.text((x + lc / 2, 4), n, fill=VERMELHO, font=f, anchor="mt")
            px = x + (lc - c.width) // 2
            img.paste(c, (px, 52))
            dr.rectangle([px - 1, 51, px + c.width, 52 + c.height], outline=(120, 120, 120), width=2)
            if circular_estreita and c.width < 150:
                dr.ellipse([px - 60, 44, px + c.width + 60, 60 + c.height], outline=VERMELHO, width=6)
            x += lc + 40
        return img

    faixa_st = empilhar([
        cabeca("Se valesse a linha do ScanTailor (laranja)", LARANJA,
               f"A conta do ScanTailor põe a linha a {round(linhas['4']['scantailor'] * 100)}% da largura, "
               "na beirada do livro, antes da linha escura do canto. Resultado: a página 7 vira uma tira "
               "fina de margem e a página 8 sai com as DUAS páginas do livro (8 e 9) juntas."),
        lado_a_lado([st], ["folha 4 do scan, linha do ScanTailor"], 1300, 520),
        paginas(pdf_st, ["página 7 (tira)", "página 8 (8 e 9 juntas)"], circular_estreita=True)],
        espaco=8)
    faixa_pr = empilhar([
        cabeca("Como é hoje: vale a conta do Editor (verde)", VERDE,
               f"O programa vê que a linha do ScanTailor está na beirada (fora do meio da folha), não usa "
               f"essa linha e corta perto do meio, a {round(linhas['4']['programa'] * 100)}%. A página 7 sai "
               "com a página 8 do livro e a página 8 com a 9. A folha ganha o aviso \"Lombada incerta\" "
               "para alguém conferir."),
        lado_a_lado([pr], ["folha 4 do scan, linha do programa"], 1300, 520),
        paginas(pdf_pr, ["página 7", "página 8"])], espaco=8)
    resumo = empilhar([
        cabeca("Linha do Dividir na beirada — resumo", CINZA,
               "La vida eterna (cópia), folha 4 do scan (páginas 8 e 9 do livro). Automático só com "
               "\"Dividir\" (motor de corte: o do ScanTailor, de fábrica). Páginas como saem no PDF, sem "
               "outro ajuste. As folhas 1 a 3 e 6 a 12 o ScanTailor divide no meio e nada muda nelas."),
        faixa_st, faixa_pr])
    salvar(resumo, "au-d-500", "500-0-resumo.png",
           "Resumo: a mesma folha com a linha do ScanTailor (laranja: tira + duas páginas juntas) e com a "
           "do programa (verde: duas páginas certas + aviso).")
    salvar(faixa_st, "au-d-500", "500-1-linha-do-scantailor.png", "Se valesse a linha do ScanTailor.")
    salvar(faixa_pr, "au-d-500", "500-2-como-e-hoje.png", "Como é hoje: a linha perto do meio.")
    tela = sublinhar(janela(d / "07b-folha-4-duas-lado-a-lado.png", SEM_PAINEL), [(70, 592, 1172, 632)])
    tela = circular(tela, [(600, 86, 680, 540)])
    p3 = empilhar([cabeca("No programa: o aviso e a linha", AZUL,
                          "Ferramenta Dividir, \"Duas lado a lado\", folha 4: a linha azul perto do meio e, "
                          "embaixo, \"Não tenho certeza de onde cortar. Confira a linha.\" Dá para arrastar "
                          "a linha e \"aceitar o corte\"."),
                   caber(tela, 1400, 760)])
    salvar(p3, "au-d-500", "500-3-o-aviso-no-programa.png",
           "A folha 4 no Dividir: a linha perto do meio e o aviso \"Lombada incerta\".")


ITENS = {"au-d-501": item_501, "au-d-500": item_500}

if __name__ == "__main__":
    # tudo pelo módulo "montar" (o mesmo que montar_mais importa), para as legendas ficarem juntas
    sys.path.insert(0, str(AQUI))
    import montar as m
    import montar_mais                                    # os outros nove itens (mesmos ajudantes)
    m.ITENS.update(montar_mais.ITENS)
    for nome in sys.argv[1:] or list(m.ITENS):
        m.ITENS[nome]()
    m.gravar_legendas()
