"""Monta as imagens das 4 perguntas (modelo de print do Samuel, 10/11/2026: CLAUDE.md §10,
docs/plano/central/modelo-de-print/) com as fotos cruas que gerar_p1..gerar_p4 gravaram.

    python montar.py <pasta crua (com p1/ p2/ p3/ p4/)> <pasta de saída>

Cada pergunta: pN-resumo.png (título, uma linha com livro/páginas/clique, e as faixas uma
embaixo da outra) e pN-passo-*.png (cada faixa grande e as telas dos cliques). Cores: azul =
ANTES do clique; laranja = DEPOIS pelo caminho que fica como hoje (opção "não"); verde = DEPOIS
pelo outro caminho (o jeito que a opção "sim" copiaria). O que olhar: círculo vermelho e o nome
da página em vermelho. Também grava legendas.json (nome da imagem → legenda).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
CINZA_ESCURO = (40, 40, 40)
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


def _cabeca(rotulo: str, cor, legenda: str, largura: int = LARGURA) -> Image.Image:
    """A faixa colorida com o rótulo grande e, embaixo, a frase do que acontece."""
    f_rot, f_leg = _fonte(46, True), _fonte(26)
    linhas = _quebrar(legenda, f_leg, largura - 40)
    img = Image.new("RGB", (largura, 86 + 14 + 36 * len(linhas) + 10), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 86], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 100 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def _titulo(texto: str, largura: int = LARGURA - 40) -> Image.Image:
    f = _fonte(28, True)
    linhas = _quebrar(texto, f, largura)
    t = Image.new("RGB", (largura, 8 + 38 * len(linhas)), FUNDO)
    for n, linha in enumerate(linhas):
        ImageDraw.Draw(t).text((0, 4 + 38 * n), linha, fill=(30, 30, 30), font=f)
    return t


def _empilhar(partes: list[Image.Image], espaco: int = 16, largura: int = LARGURA) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def _caber(img: Image.Image, caixa_l: int, caixa_a: int) -> Image.Image:
    escala = min(caixa_l / img.width, caixa_a / img.height)
    return img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))),
                      Image.LANCZOS)


def _grade(imagens: list[Image.Image | None], nomes: list[str], por_linha: int, caixa: int,
           circular: set[int], moldura: bool = True, embaixo: list | None = None,
           caixa_a: int | None = None) -> Image.Image:
    """Páginas em quadros iguais, com o nome grande em cima de cada uma (vermelho nas de
    `circular`, que ganham um círculo vermelho em volta) e, se houver, uma linha embaixo
    (`embaixo`: lista de (texto, cor) ou None). Imagem None = quadro vazio com "—"."""
    f_num, f_baixo = _fonte(28, True), _fonte(22, True)
    caixa_a = caixa_a or caixa
    topo, margem = 46, 14
    rodape = 34 if embaixo else 0
    cel_l, cel_a = caixa + 2 * margem, caixa_a + topo + 2 * margem + rodape
    linhas = (len(imagens) + por_linha - 1) // por_linha
    img = Image.new("RGB", (cel_l * por_linha, cel_a * linhas), FUNDO)
    d = ImageDraw.Draw(img)
    for n, (pagina, nome) in enumerate(zip(imagens, nomes)):
        x0, y0 = (n % por_linha) * cel_l, (n // por_linha) * cel_a
        cor = VERMELHO if n in circular else (30, 30, 30)
        d.text((x0 + cel_l / 2, y0 + 6), nome, fill=cor, font=f_num, anchor="mt")
        if pagina is None:
            d.text((x0 + cel_l / 2, y0 + topo + margem + caixa_a / 2), "(ainda não existe)",
                   fill=(120, 120, 120), font=_fonte(22), anchor="mm")
        else:
            p = _caber(pagina, caixa, caixa_a)
            px, py = x0 + (cel_l - p.width) // 2, y0 + topo + margem + (caixa_a - p.height) // 2
            img.paste(p, (px, py))
            if moldura:
                d.rectangle([px - 1, py - 1, px + p.width, py + p.height], outline=(150, 150, 150))
        if embaixo and embaixo[n]:
            texto, cor_b = embaixo[n]
            d.text((x0 + cel_l / 2, y0 + cel_a - rodape + 4), texto, fill=cor_b, font=f_baixo,
                   anchor="mt")
        if n in circular:
            d.ellipse([x0 + 2, y0 + topo - 6, x0 + cel_l - 3, y0 + cel_a - rodape - 3], outline=VERMELHO,
                      width=7)
    return img


def _recortar_a_pagina(img: Image.Image, limiar: int = 70, folga: int = 10) -> Image.Image:
    """Tira o fundo escuro da área de trabalho em volta da página (a foto do widget)."""
    a = np.asarray(img.convert("RGB")).astype(int)
    claro = a.max(axis=2) > limiar
    ys, xs = np.where(claro)
    if len(xs) == 0:
        return img
    x0, x1 = max(0, xs.min() - folga), min(img.width, xs.max() + folga + 1)
    y0, y1 = max(0, ys.min() - folga), min(img.height, ys.max() + folga + 1)
    return img.crop((x0, y0, x1, y1))


def _abrir(pasta: Path, nome: str) -> Image.Image:
    return Image.open(pasta / nome).convert("RGB")


def _tela(img: Image.Image, circulos=(), caixa=None, largura: int = LARGURA - 40) -> Image.Image:
    """Uma foto da tela (inteira ou um pedaço, `caixa`), com círculos vermelhos em `circulos`
    (retângulos em pontos da foto original) e na largura pedida."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    for c in circulos:
        d.ellipse(c, outline=VERMELHO, width=5)
    if caixa:
        img = img.crop(caixa)
    return img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)


def _salvar(img: Image.Image, destino: Path, legendas: dict, legenda: str) -> None:
    assert 900 <= img.width <= 1600, (destino, img.width)
    img.save(destino, optimize=True)
    legendas[destino.name] = legenda


# ---------------------------------------------------------------------------------------------
# Pergunta 1 — "usar em todas": Cortar e Marcar
# ---------------------------------------------------------------------------------------------

def pergunta_1(cru: Path, saida: Path, legendas: dict) -> None:
    pasta = cru / "p1"
    numeros = [15, 16, 17, 18]
    nomes = ["página 15", "página 16", "página 17 (onde apertei)", "página 18"]
    situacoes = (
        ("antes", "ANTES do clique", AZUL,
         "A página 15 foi mexida à mão nas duas ferramentas: no Cortar, o corte só em volta do "
         "título e da águia; no Marcar, a águia marcada como gravura (vermelho). A página 17 "
         "também: outro corte e o texto marcado como letra (azul). As páginas 16 e 18 estão como "
         "vieram.",
         "Página 15 mexida à mão: corte só na águia e a águia marcada (vermelho)."),
        ("marcar", "DEPOIS — pelo Marcar (como é hoje)", LARANJA,
         "Na página 17, botão \"usar em todas\" do Marcar. A águia que você marcou à mão na página "
         "15 SOME, e no lugar dela vem o retângulo azul da página 17 (no texto). As páginas 16 e "
         "18 também ganham o retângulo azul. O corte não muda.",
         "\"usar em todas\" do Marcar na 17: a águia marcada à mão na 15 SOME; vem o azul da 17."),
        ("cortar", "DEPOIS — pelo Cortar", VERDE,
         "Na página 17, botão \"usar em todas\" do Cortar. A janela \"Em quais páginas?\" já vem "
         "com a página 15 desmarcada (\"corte próprio\"); com \"Aplicar\", a 15 FICA como você "
         "deixou e as páginas 16 e 18 ganham o corte da 17. É o que a opção \"Sim\" faria também "
         "no Marcar.",
         "\"usar em todas\" do Cortar na 17: a página 15 FICA como você deixou; 16 e 18 mudam."),
    )
    resumo = []
    for n, (chave, rotulo, cor, legenda, curta) in enumerate(situacoes, start=1):
        cortar = [_recortar_a_pagina(_abrir(pasta, f"p1-{chave}-cortar-{i}.png")) for i in numeros]
        marcar = [_recortar_a_pagina(_abrir(pasta, f"p1-{chave}-marcar-{i}.png")) for i in numeros]
        img = _empilhar([
            _cabeca(rotulo, cor, legenda),
            _titulo("1) Na ferramenta Cortar as bordas (o retângulo verde é o corte):"),
            _grade(cortar, nomes, 4, 330, {0}),
            _titulo("2) Na ferramenta Marcar (vermelho = gravura, azul = letra; o Marcar mostra a "
                    "página já cortada):"),
            _grade(marcar, nomes, 4, 330, {0}),
        ])
        _salvar(img, saida / f"p1-passo-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        curtos = [f"página {i}" for i in numeros]
        resumo.append(_empilhar([
            _cabeca(rotulo, cor, curta),
            _lado_a_lado([_grade(cortar, curtos, 4, 150, {0}), _grade(marcar, curtos, 4, 150, {0})],
                         ["No Cortar (o corte é o retângulo verde)",
                          "No Marcar (vermelho = gravura, azul = letra)"], tamanho=24)],
            espaco=6))
    img = _empilhar([_cabeca("Pergunta 1 — resumo", CINZA_ESCURO,
                             "Gradus Primus (cópia), páginas 15 a 18. A página 15 foi mexida à mão. "
                             "Na página 17: \"usar em todas\" do Marcar e, separado, \"usar em "
                             "todas\" do Cortar. Em cada parte, as 4 páginas no Cortar e depois no "
                             "Marcar."), *resumo])
    _salvar(img, saida / "p1-resumo.png", legendas,
            "Resumo da pergunta 1: antes, depois pelo Marcar (laranja, como é hoje) e depois pelo "
            "Cortar (verde), um embaixo do outro.")
    # as telas dos cliques
    tela = _abrir(pasta, "p1-tela-marcar-17.png")
    img = _empilhar([_cabeca("O clique no Marcar", LARANJA,
                             "Página 17, ferramenta Marcar (Retângulo): o botão \"usar em todas\" "
                             "de \"Marcação desta página\" (em vermelho). Ele não pergunta nada: "
                             "copia a marcação da 17 para as 139 páginas."),
                     _tela(tela, [(1058, 630, 1210, 676)])])
    _salvar(img, saida / "p1-passo-4-clique-no-marcar.png", legendas,
            "O clique no Marcar: página 17, \"usar em todas\" de \"Marcação desta página\". Não abre "
            "lista; vale para todas as 139 páginas.")
    tela = _abrir(pasta, "p1-tela-cortar-17.png")
    janela = _abrir(pasta, "p1-janela-em-quais-paginas.png")
    d = ImageDraw.Draw(janela)
    d.ellipse((2, 334, 230, 368), outline=VERMELHO, width=4)
    janela = janela.resize((janela.width * 2, janela.height * 2), Image.LANCZOS)
    img = _empilhar([_cabeca("O clique no Cortar", VERDE,
                             "Página 17, ferramenta Cortar as bordas: o botão \"usar em todas\" (em "
                             "vermelho) abre a janela \"Em quais páginas?\". A página 15 já vem "
                             "DESMARCADA, com \"(corte próprio)\" (em vermelho). Apertei \"Aplicar\" "
                             "sem mudar nada."),
                     _tela(tela, [(1058, 428, 1210, 474)]), janela])
    _salvar(img, saida / "p1-passo-5-clique-no-cortar.png", legendas,
            "O clique no Cortar: página 17, \"usar em todas\" abre \"Em quais páginas?\", com a página "
            "15 desmarcada (\"corte próprio\"); \"Aplicar\" sem mudar nada.")


# ---------------------------------------------------------------------------------------------
# Pergunta 2 — "Letra clara em fundo escuro" no "todas" do painel Filtro e no Automático
# ---------------------------------------------------------------------------------------------

def pergunta_2(cru: Path, saida: Path, legendas: dict) -> None:
    pasta = cru / "p2"
    estado = json.loads((pasta / "estado-p2.json").read_text(encoding="utf-8"))
    numeros = ["11", "13", "15", "17"]
    nomes = ["página 11", "página 13 (onde apertei)", "página 15", "página 17"]
    situacoes = (
        ("antes", "ANTES do clique", AZUL, "antes",
         "Siebmacher: as páginas 11, 13, 15 e 17 são desenhos de bordado claros em fundo escuro. "
         "O livro já passou pelo Automático em Preto e branco, com a caixinha \"Letra clara em "
         "fundo escuro\" desmarcada em todas. É o ponto de partida dos dois caminhos.",
         "Preto e branco em todas; caixinha \"Letra clara em fundo escuro\" desmarcada em todas."),
        ("painel", "DEPOIS — pelo painel Filtro (como é hoje)", LARANJA, "painel",
         "Na página 13, painel \"Filtro da página\": marquei \"Letra clara em fundo escuro\" e "
         "apertei \"Aplicar em: todas\". Só a 13 fica com a caixinha (e com o fundo escuro). Nas "
         "páginas 11, 15 e 17 a caixinha continua DESMARCADA e elas não mudam.",
         "Página 13: caixinha + \"todas\". A caixinha NÃO vai: 11, 15 e 17 ficam sem ela."),
        ("automatico", "DEPOIS — pelo Automático", VERDE, "automatico",
         "O mesmo Automático do ANTES (Limpar a folha, Preto e branco), agora com a caixinha "
         "\"Letra clara em fundo escuro\" marcada, no livro todo: as quatro páginas ficam com a "
         "caixinha MARCADA e saem com o fundo escuro. É o que a opção \"Sim\" faria também no "
         "\"todas\" do painel.",
         "Automático com a caixinha: ela VAI para todas; as quatro saem com o fundo escuro."),
    )
    resumo = []
    for n, (chave, rotulo, cor, pdf, legenda, curta) in enumerate(situacoes, start=1):
        paginas = [_abrir(pasta, f"pdf-p2-{pdf}-{i}.png") for i in range(1, 5)]
        valores = estado[{"antes": "antes", "painel": "depois_painel",
                          "automatico": "depois_automatico"}[chave]]
        embaixo = [("caixinha marcada", VERDE) if valores[x]["claro_no_escuro"]
                   else ("caixinha desmarcada", (120, 120, 120)) for x in numeros]
        circular = {0, 2, 3} if chave != "antes" else set()
        img = _empilhar([
            _cabeca(rotulo, cor, legenda),
            _titulo("As páginas como saem no PDF (embaixo de cada uma, a caixinha \"Letra clara em "
                    "fundo escuro\" dela):"),
            _grade(paginas, nomes, 2, 640, circular, embaixo=embaixo, caixa_a=500)])
        _salvar(img, saida / f"p2-passo-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        resumo.append(_empilhar([_cabeca(rotulo, cor, curta),
                                 _grade(paginas, nomes, 4, 330, circular, embaixo=embaixo,
                                        caixa_a=260)], espaco=6))
    img = _empilhar([_cabeca("Pergunta 2 — resumo", CINZA_ESCURO,
                             "Siebmacher (cópia), páginas 11, 13, 15 e 17. Na página 13: caixinha "
                             "\"Letra clara em fundo escuro\" + \"todas\" no painel Filtro; e, "
                             "separado, o Automático com a caixinha. Páginas como saem no PDF."),
                     *resumo])
    _salvar(img, saida / "p2-resumo.png", legendas,
            "Resumo da pergunta 2: antes, depois pelo painel Filtro (laranja, como é hoje) e depois "
            "pelo Automático (verde), um embaixo do outro.")
    # as telas
    p13, p15 = _abrir(pasta, "p2-painel-pagina-13.png"), _abrir(pasta, "p2-painel-pagina-15.png")
    caixa = CAIXA_DO_PAINEL
    onde = {k: _folga(v) for k, v in estado["onde_a_caixinha"].items()}
    img = _empilhar([
        _cabeca("O painel Filtro, pelo caminho do painel", LARANJA,
                "À esquerda, a página 13, onde marquei \"Letra clara em fundo escuro\" (em vermelho) e "
                "apertei \"todas\". À direita, a página 15 depois do \"todas\": o filtro é o "
                "mesmo, mas a caixinha está desmarcada (em vermelho)."),
        _lado_a_lado([_tela(p13, [onde["painel-13"]], caixa, 420),
                      _tela(p15, [onde["painel-15"]], caixa, 420)],
                     ["página 13 (onde apertei)", "página 15, depois do \"todas\""])])
    _salvar(img, saida / "p2-passo-4-painel.png", legendas,
            "O painel \"Filtro da página\": na página 13 a caixinha marcada; na página 15, depois do "
            "\"todas\", desmarcada.")
    auto = _abrir(pasta, "p2-janela-do-automatico.png")
    p15a = _abrir(pasta, "p2-automatico-painel-pagina-15.png")
    img = _empilhar([
        _cabeca("O Automático, pelo caminho do Automático", VERDE,
                "A janela do Automático: a etapa \"4 Limpar a folha\" (Preto e branco, \"Letra "
                "clara em fundo escuro\"), a caixinha marcada e o \"Rodar\" (em vermelho). Depois do \"Rodar\", o painel Filtro da "
                "página 15 mostra a caixinha marcada (embaixo, em vermelho)."),
        _tela(auto, [onde["janela-do-automatico"], *CIRCULOS_DO_AUTOMATICO]),
        _lado_a_lado([_tela(p15a, [onde["automatico-15"]], caixa, 420)],
                     ["página 15, depois do Automático"])])
    _salvar(img, saida / "p2-passo-5-automatico.png", legendas,
            "A janela do Automático com a caixinha marcada, e o painel da página 15 depois do "
            "\"Rodar\" (caixinha marcada).")


# ajustados olhando as fotos cruas (janela de 1400 x 820)
CAIXA_DO_PAINEL = (1056, 38, 1400, 820)
CIRCULOS_DO_AUTOMATICO = [(8, 280, 284, 358), (1122, 758, 1292, 814)]   # etapa 4 e "Rodar"


def _folga(r, x: int = 34, y: int = 12) -> tuple:
    return (r[0] - x, r[1] - y, r[2] + x, r[3] + y)


def _lado_a_lado(imagens: list[Image.Image], nomes: list[str], tamanho: int = 28) -> Image.Image:
    f = _fonte(tamanho, True)
    vagas = [max(i.width, round(f.getlength(nome)) + 20) for i, nome in zip(imagens, nomes)]
    largura = sum(vagas) + 30 * (len(imagens) - 1)
    altura = max(i.height for i in imagens) + 46
    img = Image.new("RGB", (largura, altura), FUNDO)
    d = ImageDraw.Draw(img)
    x = 0
    for i, nome, vaga in zip(imagens, nomes, vagas):
        d.text((x + vaga / 2, 4), nome, fill=(30, 30, 30), font=f, anchor="mt")
        img.paste(i, (x + (vaga - i.width) // 2, 46))
        x += vaga + 30
    return img


# ---------------------------------------------------------------------------------------------
# Pergunta 3 — Dividir: a linha arrastada, "dividir esta" e o "dividir" da grade
# ---------------------------------------------------------------------------------------------

CAIXA_DA_FOLHA = (44, 38, 1056, 582)     # a área da página na tela (sem os painéis)


def pergunta_3(cru: Path, saida: Path, legendas: dict) -> None:
    pasta = cru / "p3"
    estado = json.loads((pasta / "estado-p3.json").read_text(encoding="utf-8"))
    arrastada = estado["antes"]["posicao_corte"]
    motor = estado["motor"]["linha_do_motor"]
    situacoes = (
        ("antes", "ANTES do clique", AZUL, "p3-antes.png", ["pdf-p3-antes-1.png", None],
         f"Gradus, ferramenta Dividir, \"Duas lado a lado\", folha 10 ainda inteira (páginas 18 e "
         f"19). Arrastei a linha azul para a esquerda, para longe do meio de propósito (para ficar "
         f"fácil de ver): ela está em {round(arrastada * 100)}% da largura; a do motor estava em "
         f"{round(motor * 100)}%.",
         "Folha 10 inteira; a linha azul arrastada para a esquerda do meio (em vermelho)."),
        ("grade", "DEPOIS — pelo \"dividir\" da grade (como é hoje)", LARANJA, "p3-grade.png",
         ["pdf-p3-grade-1.png", "pdf-p3-grade-2.png"],
         "Grade \"Todas as páginas\": escolhi a página 18 e apertei \"dividir\". A folha é cortada "
         "na linha do MOTOR, não onde você deixou a linha: a linha arrastada é esquecida.",
         "Grade, \"dividir\": corta na linha do motor (no meio); a linha que você arrastou é "
                "esquecida."),
        ("esta", "DEPOIS — pelo \"dividir esta\"", VERDE, "p3-esta.png",
         ["pdf-p3-esta-1.png", "pdf-p3-esta-2.png"],
         "Ferramenta Dividir, botão \"dividir esta\": a folha é cortada ONDE VOCÊ DEIXOU a linha "
         "(D-609). É o que a opção \"Sim\" faria também na grade.",
         "\"dividir esta\": corta onde você deixou a linha (D-609): a 18 sai sem a beirada da direita e "
                "a 19 leva um pedaço da 18."),
    )
    nomes = ["tela do Dividir, folha 10", "página 18", "página 19"]
    resumo = []
    for n, (chave, rotulo, cor, tela, pdfs, legenda, curta) in enumerate(situacoes, start=1):
        folha = _recortar_a_pagina(_abrir(pasta, tela).crop(CAIXA_DA_FOLHA), limiar=70)
        paginas = [_abrir(pasta, p) if p else None for p in pdfs]
        circular = {0} if chave == "antes" else {1, 2}     # antes: a linha; depois: as páginas
        nomes_n = nomes if chave != "antes" else ["tela do Dividir, folha 10",
                                                  "página 18 (folha inteira)", "página 19"]
        img = _empilhar([
            _cabeca(rotulo, cor, legenda),
            _titulo("A tela do Dividir (\"Duas lado a lado\") e as páginas como saem no PDF:"),
            _grade([folha, *paginas], nomes_n, 3, 440, circular, caixa_a=440)])
        _salvar(img, saida / f"p3-passo-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        resumo.append(_empilhar([_cabeca(rotulo, cor, curta),
                                 _grade([folha, *paginas], nomes_n, 3, 400, circular, caixa_a=290)],
                                espaco=6))
    img = _empilhar([_cabeca("Pergunta 3 — resumo", CINZA_ESCURO,
                             "Gradus Primus (cópia), folha 10 (páginas 18 e 19), linha azul "
                             "arrastada à mão. Caminhos: \"dividir\" da grade \"Todas as páginas\" e "
                             "\"dividir esta\" do Dividir. Em cada parte: a tela do Dividir e as "
                             "páginas do PDF."), *resumo])
    _salvar(img, saida / "p3-resumo.png", legendas,
            "Resumo da pergunta 3: antes, depois pela grade (laranja, como é hoje) e depois pelo "
            "\"dividir esta\" (verde), um embaixo do outro.")
    motor_img = _abrir(pasta, "p3-linha-do-motor.png")
    antes = _abrir(pasta, "p3-antes.png")
    img = _empilhar([
        _cabeca("A linha antes e depois de arrastar", AZUL,
                f"Em cima: a folha 10 com a linha do motor ({round(motor * 100)}% da largura). "
                f"Embaixo: a mesma folha com a linha arrastada à mão ({round(arrastada * 100)}%)."),
        _tela(motor_img, caixa=CAIXA_DA_FOLHA, largura=1100),
        _tela(antes, caixa=CAIXA_DA_FOLHA, largura=1100)])
    _salvar(img, saida / "p3-passo-4-linha-arrastada.png", legendas,
            "A linha da folha 10: a do motor (em cima) e a arrastada à mão (embaixo).")
    grade = _abrir(pasta, "p3-grade-escolhida.png")
    img = _empilhar([
        _cabeca("O clique na grade \"Todas as páginas\"", LARANJA,
                "\"marcar várias\" ligado, a página 18 escolhida (a folha 10 inteira) e o botão "
                "\"dividir\" da faixa de cima (em vermelho)."),
        _tela(grade, CIRCULOS_DA_GRADE_DIVIDIR)])
    _salvar(img, saida / "p3-passo-5-clique-na-grade.png", legendas,
            "O clique na grade: página 18 escolhida e o botão \"dividir\".")


CIRCULOS_DA_GRADE_DIVIDIR = [(184, 526, 316, 714), (518, 92, 594, 144)]   # página 18 e "dividir"


# ---------------------------------------------------------------------------------------------
# Pergunta 4 — o girar da grade e o do painel
# ---------------------------------------------------------------------------------------------

def pergunta_4(cru: Path, saida: Path, legendas: dict) -> None:
    pasta = cru / "p4"
    estado = json.loads((pasta / "estado-p4.json").read_text(encoding="utf-8"))
    nomes = ["página 17", "página 18 (a da vez)", "página 19", "página 20"]
    situacoes = (
        ("antes", "ANTES do clique", AZUL, "antes",
         "Gradus, folhas divididas. A página 19 foi virada ¼ à direita à mão (\"só esta página\"). "
         "As outras estão em pé.",
         "A página 19 virada ¼ à direita à mão; as outras em pé."),
        ("grade", "DEPOIS — pela grade \"Todas as páginas\" (como é hoje)", LARANJA, "grade",
         "Na grade, todas as páginas escolhidas e \"girar ¼ →\". Cada página gira ¼ A PARTIR DE "
         "ONDE ESTÁ: as que estavam em pé deitam, e a 19, que já estava deitada, fica DE CABEÇA "
         "PARA BAIXO.",
         "Grade, todas + \"girar ¼ →\": cada uma gira a partir de onde está; a 19 fica de cabeça "
         "para baixo."),
        ("painel", "DEPOIS — pelo painel", VERDE, "painel",
         "Na página 18, \"aplicar em: todas as páginas\" + \"¼ à direita\". Todas ficam VIRADAS "
         "COMO A PÁGINA 18 (D-035): a 19, que já estava deitada, continua deitada, igual às "
         "outras. É o que a opção \"Sim\" faria também na grade.",
         "Painel, \"todas as páginas\" + ¼: todas ficam como a 18; a 19 fica deitada como as "
         "outras."),
    )
    resumo = []
    for n, (chave, rotulo, cor, pdf, legenda, curta) in enumerate(situacoes, start=1):
        paginas = [_abrir(pasta, f"pdf-p4-{pdf}-{i}.png") for i in range(1, 5)]
        img = _empilhar([_cabeca(rotulo, cor, legenda),
                         _titulo("As páginas como saem no PDF:"),
                         _grade(paginas, nomes, 4, 330, {2})])
        _salvar(img, saida / f"p4-passo-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        resumo.append(_empilhar([_cabeca(rotulo, cor, curta), _grade(paginas, nomes, 4, 250, {2})],
                                espaco=6))
    img = _empilhar([_cabeca("Pergunta 4 — resumo", CINZA_ESCURO,
                             "Gradus Primus (cópia), páginas 17 a 20; a 19 já virada à mão. "
                             "Caminhos: grade \"Todas as páginas\" (todas + \"girar ¼ →\") e painel "
                             "(página 18, \"todas as páginas\" + ¼ à direita). Páginas do PDF."),
                     *resumo])
    _salvar(img, saida / "p4-resumo.png", legendas,
            "Resumo da pergunta 4: antes, depois pela grade (laranja, como é hoje) e depois pelo "
            "painel (verde), um embaixo do outro.")
    painel = _abrir(pasta, "p4-painel-antes-do-clique.png")
    grade = _abrir(pasta, "p4-grade-escolhidas.png")
    img = _empilhar([
        _cabeca("Os dois cliques", CINZA_ESCURO,
                "Em cima, o painel (página 18): \"aplicar em: todas as páginas\" e \"¼ à direita\" "
                "(em vermelho). Embaixo, a grade \"Todas as páginas\": todas escolhidas e \"girar "
                "¼ →\" (em vermelho)."),
        _tela(painel, CIRCULOS_DO_PAINEL_GIRAR), _tela(grade, CIRCULOS_DA_GRADE_GIRAR)])
    _salvar(img, saida / "p4-passo-4-cliques.png", legendas,
            "Os dois cliques: o painel da página 18 (\"todas as páginas\" + ¼ à direita) e a grade "
            "com todas escolhidas (\"girar ¼ →\").")


CIRCULOS_DO_PAINEL_GIRAR = [(1058, 176, 1354, 212), (1204, 106, 1352, 148)]   # "todas as páginas" e "¼ à direita"
CIRCULOS_DA_GRADE_GIRAR = [(454, 92, 550, 144), (12, 92, 222, 144)]   # "girar ¼ →" e "139 escolhidas"


def main() -> None:
    cru, saida = Path(sys.argv[1]), Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    so = sys.argv[3:] or ["1", "2", "3", "4"]
    caminho = saida / "legendas.json"
    legendas: dict = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
    for n in so:
        {"1": pergunta_1, "2": pergunta_2, "3": pergunta_3, "4": pergunta_4}[n](cru, saida, legendas)
        estado = cru / f"p{n}" / f"estado-p{n}.json"
        if estado.exists():
            (saida / f"estado-p{n}.json").write_bytes(estado.read_bytes())
    caminho.write_text(json.dumps(legendas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    main()
