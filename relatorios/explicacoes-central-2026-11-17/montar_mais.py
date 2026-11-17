"""Os outros nove itens das explicações (17/11/2026), com os ajudantes de montar.py (modelo do girar).
Rodar pelo montar.py: python montar.py [item ...]."""
from __future__ import annotations

from PIL import Image, ImageDraw

from montar import (AZUL, CINZA, CRUS, FUNDO, LARANJA, VERDE, VERMELHO, cabeca, caber, circular,
                    empilhar, fonte, janela, lado_a_lado, salvar, sublinhar)


# --- ajudantes das faixas -----------------------------------------------------------------------

def abrir(caminho):
    return Image.open(caminho).convert("RGB")


def paginas_numeradas(imgs, numeros, circular_em=(), alt=330, legendas=None):
    """Páginas do PDF lado a lado, com "página N" em cima (vermelho e circulada as de circular_em)."""
    f = fonte(28, True)
    cel = [caber(i, 10_000, alt) for i in imgs]
    larg = [max(c.width, 170) + 20 for c in cel]
    img = Image.new("RGB", (sum(larg), alt + 70), FUNDO)
    d = ImageDraw.Draw(img)
    x = 0
    for c_, n, lc in zip(cel, numeros, larg):
        nome = (legendas or {}).get(n, f"página {n}")
        cor = VERMELHO if n in circular_em else (30, 30, 30)
        d.text((x + lc / 2, 4), nome, fill=cor, font=f, anchor="mt")
        px = x + (lc - c_.width) // 2
        img.paste(c_, (px, 50))
        d.rectangle([px - 1, 49, px + c_.width, 50 + c_.height], outline=(150, 150, 150))
        if n in circular_em:
            d.ellipse([x + 2, 40, x + lc - 2, 66 + c_.height], outline=VERMELHO, width=6)
        x += lc
    return img


def faixa(rotulo, cor, frase, *conteudo, espaco=8):
    return empilhar([cabeca(rotulo, cor, frase), *conteudo], espaco=espaco)


def resumo_de(titulo, linha, faixas_pequenas):
    return empilhar([cabeca(titulo, CINZA, linha), *faixas_pequenas])


def simulacao(img, texto="SIMULAÇÃO: texto trocado só para este print", embaixo=False):
    """Carimbo amarelo num canto (de cima, ou de baixo com `embaixo`), para ninguém achar que já
    está assim no programa. Não pode cobrir o texto que se quer mostrar."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    f = fonte(26, True)
    w = int(f.getlength(texto)) + 24
    y0 = img.height - 48 if embaixo else 6
    d.rectangle([img.width - w - 10, y0, img.width - 10, y0 + 40], fill=(255, 214, 0))
    d.text((img.width - w + 2, y0 + 4), texto, fill=(20, 20, 20), font=f)
    return img


# --- au-d-541: a ferramenta Mover -----------------------------------------------------------------

def item_541():
    d = CRUS / "trabalho"
    campo = (1195, 582, 1525, 630)
    m0 = circular(janela(d / "M0-mover-antes.png"), [(730, 10, 925, 40), (443, 77, 463, 97),
                                                     (777, 77, 797, 97), (443, 534, 463, 554),
                                                     (777, 534, 797, 554), campo])
    m1 = circular(janela(d / "M1-mover-arrastou.png"), [(427, 87, 480, 545)])
    m2 = circular(janela(d / "M2-mover-canto.png"), [campo, (64, 576, 600, 632)])
    m3 = circular(janela(d / "M3-mover-numero-80.png"), [campo])
    m4 = circular(janela(d / "M4-mover-passou-da-beirada.png"), [(700, 87, 865, 535)])
    pdf = {k: abrir(d / f"pdf-{k}-1.png") for k in ("M0", "M1", "M2", "M3", "M4")}

    def par(tela, chave, alt=560):
        return lado_a_lado([tela, pdf[chave]], ["na tela", "no PDF que sai"], 1050, alt)

    partes = [
        ("0. A ferramenta, como é hoje", AZUL,
         "La vida eterna (cópia, dividido), página 3. Ícone da cruz na barra da esquerda, ou tecla F: o "
         "nome \"Mover e redimensionar\" aparece no alto. A borda azul com 4 quadradinhos nos cantos é o "
         "conteúdo da página. À direita, \"Tamanho do conteúdo\" = 100 %.", m0, "M0", "A ferramenta"),
        ("1. Arrastar", AZUL,
         "Clicar em cima da página e arrastar para a esquerda: a página anda junto com o mouse. A faixa "
         "riscada de vermelho (circulada) é o pedaço que passou da beirada: ele fica de fora no PDF.", m1, "M1",
         "A página anda com o mouse"),
        ("2. Puxar um canto", AZUL,
         "Puxar o quadradinho de baixo, à direita, para fora: o conteúdo cresce por igual (126 %). O que "
         "passa da beirada fica riscado de vermelho e a página ganha um aviso (circulado). O programa não "
         "diminui sozinho.", m2, "M2", "Cresce por igual; o que passa fica riscado"),
        ("3. Digitar o tamanho", AZUL,
         "Escrever 80 no \"Tamanho do conteúdo\": o conteúdo fica menor, no meio da página, com margem "
         "branca em volta.", m3, "M3", "80 %: menor, no meio"),
        ("4. Arrastar até passar da beirada", AZUL,
         "Arrastar muito para a direita: o programa para quando o MEIO do conteúdo chega na beirada "
         "(circulado), para a página nunca sumir da vista. A metade de fora fica riscada.", m4, "M4",
         "Para no meio; não some"),
    ]
    resumo = [cabeca("Ferramenta Mover — resumo", CINZA,
                     "La vida eterna (cópia), página 3, dividido pelo Automático, filtro Original. Em cada "
                     "faixa: a tela (esquerda) e a página como sai no PDF (direita). Entre uma faixa e outra, "
                     "Ctrl+Z voltou a página ao normal.")]
    for n, (rot, cor, frase, tela, chave, curta) in enumerate(partes):
        salvar(faixa(rot, cor, frase, par(tela, chave)), "au-d-541", f"541-{n + 1}-{chave}.png",
               f"{rot}. {frase}")
        resumo.append(faixa(rot, cor, curta + ".",
                            lado_a_lado([tela, pdf[chave]], ["na tela", "no PDF"], 700, 300)))
    salvar(empilhar(resumo), "au-d-541", "541-0-resumo.png", "Resumo: as quatro mexidas do Mover, tela e PDF.")


# --- au-d-487 e au-d-484: a grade "Todas as páginas" e o Automático nas escolhidas -----------------

def item_487():
    d = CRUS / "grade"
    c1 = sublinhar(janela(d / "C1-grade-paginas-9-e-11.png"), [(14, 120, 1546, 172)])
    c1 = circular(c1, [(251, 432, 390, 627), (649, 432, 788, 627)])
    c2 = circular(janela(d / "C2-depois-do-botao-direito.png"), [(251, 432, 390, 627)])
    menu = abrir(CRUS / "extra" / "X2-botao-direito-na-miniatura.png")
    menu = menu.resize((menu.width * 3 // 2, menu.height * 3 // 2), Image.LANCZOS)
    x2 = Image.new("RGB", (620, 560), FUNDO)             # o menu num quadro, sem crescer demais
    x2.paste(menu, ((620 - menu.width) // 2, 40))
    f1 = faixa("1. Onde ficam os botões da grade", AZUL,
               "Palatino (cópia). \"ver todas\" abre a grade; \"marcar várias\" e um clique nas páginas 9 e 11 "
               "(circuladas). Os botões ficam na FAIXA DE CIMA (contorno vermelho): girar ¼ ←, girar ¼ →, "
               "dividir, deixar em branco, tirar do livro, trazer de volta, extrair..., rodar o automático "
               "nelas... (O \"tem cor\" nas páginas 5 e 7 vem de outro teste feito antes nesta mesma cópia.)",
               caber(c1, 1450, 800))
    f2 = faixa("2. Botão direito numa página da grade", AZUL,
               "Botão direito na página 9 da grade: nada abre (esquerda). A grade não tem menu de botão "
               "direito. O menu de botão direito que existe é o das miniaturas de baixo e o da página grande "
               "(direita: \"Desfazer nesta página\" e \"adicionar página em branco\").",
               lado_a_lado([c2, x2], ["grade: nada abre", "miniatura de baixo: o menu"], 1000, 560))
    salvar(f1, "au-d-487", "487-1-botoes-da-grade.png", "A grade com 2 escolhidas e a faixa de botões.")
    salvar(f2, "au-d-487", "487-2-botao-direito.png",
           "Botão direito na grade: nada abre. O menu de botão direito é o da miniatura de baixo.")
    salvar(resumo_de("Grade \"Todas as páginas\" — resumo",
                     "Palatino (cópia, 12 páginas de texto). Onde ficam os botões e o que o botão direito faz.",
                     [f1, f2]), "au-d-487", "487-0-resumo.png",
           "Resumo: botões na faixa de cima; botão direito não abre nada.")


def item_484():
    d = CRUS / "grade"
    b1 = circular(janela(d / "B1-janela-grande.png"), [(80, 692, 330, 734), (748, 689, 932, 736)])
    b2 = circular(janela(d / "B2-grade-paginas-5-e-7.png"),
                  [(848, 210, 986, 404), (1245, 210, 1383, 404), (1236, 124, 1492, 182)])
    b3 = circular(janela(d / "B3-janela-nas-escolhidas.png"), [(80, 692, 330, 734), (28, 406, 340, 488)])
    pdf_b = [abrir(d / f"pdf-B-{i}.png") for i in range(1, 6)]
    c1 = circular(janela(d / "C1-grade-paginas-9-e-11.png"),
                  [(1308, 124, 1538, 172), (251, 432, 390, 627), (649, 432, 788, 627)])
    c3 = circular(janela(d / "C3-automatico-com-as-escolhidas.png"), [(1250, 637, 1538, 679),
                                                                      (1198, 542, 1508, 622)])
    pdf_c = [abrir(d / f"pdf-C-{i}.png") for i in range(1, 6)]
    fa1 = faixa("Caminho 1 — pelo Automático (janela grande)", AZUL,
                "Palatino (cópia). Painel Automático > \"abrir em janela grande\". Embaixo: \"Rodar: no livro "
                "todo\" e o botão \"escolher páginas...\" (circulados).", caber(b1, 1400, 700))
    fa2 = faixa("\"escolher páginas...\" abre a grade", AZUL,
                "A grade abre no jeito de escolher: um clique marca. Marquei as páginas 5 e 7 (circuladas) e "
                "cliquei \"usar estas 2 páginas\".", caber(b2, 1400, 760))
    fa3 = faixa("De volta à janela do Automático", AZUL,
                "Agora diz \"Rodar: nas páginas escolhidas (2)\". Marquei só \"Limpar a folha\" com Preto e "
                "branco (circulado) e cliquei \"Rodar 1 etapa\".", caber(b3, 1400, 700))
    fa4 = faixa("Resultado: só as páginas 5 e 7 mudaram", VERDE,
                "Páginas 4 a 8 como saem no PDF: a 5 e a 7 em Preto e branco; a 4, a 6 e a 8 continuam como "
                "estavam (amareladas, Original).", paginas_numeradas(pdf_b, [4, 5, 6, 7, 8], {5, 7}))
    fc1 = faixa("Caminho 2 — pela grade \"Todas as páginas\"", AZUL,
                "\"ver todas\" > \"marcar várias\" > páginas 9 e 11 > botão \"rodar o automático nelas...\" "
                "(circulado), na faixa de cima.", caber(c1, 1400, 760))
    fc2 = faixa("O Automático abre com as 2 páginas", AZUL,
                "O painel Automático abre com \"Rodar: nas páginas escolhidas (2)\" (circulado). Cliquei "
                "\"Rodar 1 etapa\".", caber(c3, 1400, 760))
    fc3 = faixa("Resultado: só as páginas 9 e 11 mudaram", VERDE,
                "Páginas 8 a 12 como saem no PDF: a 9 e a 11 em Preto e branco; as outras como estavam.",
                paginas_numeradas(pdf_c, [8, 9, 10, 11, 12], {9, 11}))
    for n, (f, nome, leg) in enumerate([
            (fa1, "janela-grande", "Caminho 1: a janela grande do Automático, \"escolher páginas...\"."),
            (fa2, "grade-marcar", "A grade no jeito de escolher, páginas 5 e 7."),
            (fa3, "janela-nas-escolhidas", "A janela diz \"nas páginas escolhidas (2)\"."),
            (fa4, "resultado-5-e-7", "Só as páginas 5 e 7 saem em Preto e branco."),
            (fc1, "grade-rodar-nelas", "Caminho 2: na grade, \"rodar o automático nelas...\"."),
            (fc2, "painel-nas-escolhidas", "O painel abre com as 2 páginas."),
            (fc3, "resultado-9-e-11", "Só as páginas 9 e 11 saem em Preto e branco.")], start=1):
        salvar(f, "au-d-484", f"484-{n}-{nome}.png", leg)
    pequeno = [
        cabeca("Caminho 1 — Automático > escolher páginas...", AZUL,
               "janela grande (1) → grade com 5 e 7 (2) → \"nas páginas escolhidas (2)\" (3) → PDF."),
        lado_a_lado([b1, b2, b3], ["1", "2", "3"], 470, 300),
        paginas_numeradas(pdf_b, [4, 5, 6, 7, 8], {5, 7}, alt=240),
        cabeca("Caminho 2 — grade > rodar o automático nelas...", AZUL,
               "grade com 9 e 11 (1) → painel com as 2 (2) → PDF."),
        lado_a_lado([c1, c3], ["1", "2"], 700, 380),
        paginas_numeradas(pdf_c, [8, 9, 10, 11, 12], {9, 11}, alt=240)]
    salvar(resumo_de("Automático só nas páginas escolhidas — resumo",
                     "Palatino (cópia). Dois caminhos, os dois testados na janela de verdade. Etapa usada: "
                     "\"Limpar a folha\" em Preto e branco (dá para ver no PDF quais páginas mudaram).",
                     pequeno), "au-d-484", "484-0-resumo.png",
           "Resumo: pelo Automático e pela grade, só as páginas escolhidas mudam.")


# --- au-d-492: o tique do menu Filtro -------------------------------------------------------------

def item_492():
    d = CRUS / "grade"
    m1 = circular(abrir(d / "A1-menu-filtro-pagina-1.png"), [(8, 14, 130, 40)], folga=8, largura=4)
    m3 = circular(abrir(d / "A3-menu-filtro-pagina-2.png"), [(8, 54, 180, 80)], folga=8, largura=4)
    m5 = circular(abrir(d / "A5-menu-filtro-pagina-3.png"), [(8, 14, 130, 40)], folga=8, largura=4)
    a2 = circular(janela(d / "A2-pagina-2-preto-e-branco-no-painel.png"),
                  [(1265, 114, 1330, 270), (66, 594, 900, 632)])
    a2 = circular(a2, [(172, 676, 192, 696)], folga=10, largura=4)
    menus = lado_a_lado([m1, m3, m5], ["página 1 (Original)", "página 2 (Preto e branco)",
                                       "página 3 (Original)"], 420, 300)
    f1 = faixa("O tique só existe no menu Filtro (no alto)", AZUL,
               "Palatino (cópia). Menu Filtro aberto (clique em \"Filtro\", na barra do alto) em três páginas. "
               "O tique (a marquinha à esquerda do nome, circulada) fica no filtro da página que está na tela.", menus)
    f2 = faixa("Fora do menu, o filtro aparece de outro jeito", VERDE,
               "Página 2: o painel \"Filtro da página\" (à direita) mostra o filtro escolhido com a borda "
               "azul (circulado), e a faixa de baixo diz \"Esta página vai sair em Preto e branco\". Não há "
               "tique nesses lugares. A marquinha verde na miniatura 2, embaixo (circulada), é outra coisa: quer dizer "
               "\"página conferida\".", caber(a2, 1400, 760))
    salvar(f1, "au-d-492", "492-1-menu-filtro.png", "O menu Filtro em três páginas: o tique acompanha a página.")
    salvar(f2, "au-d-492", "492-2-fora-do-menu.png",
           "Fora do menu: borda azul no painel e a frase de baixo; sem tique.")
    salvar(resumo_de("Tique do menu Filtro — resumo",
                     "Palatino (cópia). Páginas 1 e 3 em Original, página 2 em Preto e branco (escolhido no "
                     "painel Filtro da página).", [f1, f2]), "au-d-492", "492-0-resumo.png",
           "Resumo: o tique só aparece com o menu Filtro aberto.")


# --- nm-folha-pagina -----------------------------------------------------------------------------

def item_folha_pagina():
    dv, dl, dt = CRUS / "dividir", CRUS / "livros", CRUS / "trabalho"
    folha = abrir(dv / "folha-4.png")
    pags = [abrir(dv / f"pdf-programa-{i}.png") for i in (3, 4)]
    f0 = faixa("O que é folha e o que é página", AZUL,
               "Folha = a foto que o scanner tirou (aqui, o livro aberto: duas páginas numa foto). Página = "
               "cada página do livro que sai no PDF. La vida eterna: a folha 4 do scan vira as páginas 7 e 8 "
               "do PDF. No livro inteiro: 180 folhas viram 360 páginas.",
               lado_a_lado([folha], ["folha 4 (a foto do scan)"], 1100, 420),
               paginas_numeradas(pags, [7, 8], {7, 8}, alt=380))
    l6 = circular(janela(dl / "L6-livro-aberto.png"), [(300, 46, 470, 66), (1222, 776, 1355, 804)])
    l7 = simulacao(circular(janela(dl / "L7-livro-aberto-SIMULACAO.png"),
                            [(300, 46, 540, 66), (1222, 776, 1355, 804)]))
    f1 = faixa("Hoje: o livro aberto (tela dos livros)", AZUL,
               "Um clique no cartão do livro. Em cima diz \"24 páginas\"; embaixo diz \"página 3 de 12\" e "
               "mostra a FOLHA 3 inteira (duas páginas). O número de baixo conta folhas, mas a palavra é "
               "\"página\" (circulados).", caber(l6, 1400, 760))
    f2 = faixa("Com a segunda opção (simulação)", VERDE,
               "Em cima: \"12 folhas, 24 páginas\". Embaixo: \"folha 3 de 12\". Só as palavras mudam; a tela "
               "mostra a mesma coisa.", caber(l7, 1400, 760))
    fr = abrir(dt / "F0-para-revisar.png")
    rev = fr.crop((1182, 86, 1550, 700))
    sim = rev.copy()
    dr = ImageDraw.Draw(sim)
    fte = fonte(16, True)
    for y, texto in ((174, "Página 2 (folha 1)"), (271, "Página 7 (folha 4)"), (369, "Página 8 (folha 4)"),
                     (466, "Página 9 (folha 5)")):
        dr.rectangle([22, y - 2, 250, y + 18], fill=(78, 78, 78))
        dr.text((26, y - 2), texto, fill=(255, 255, 255), font=fte)
    rev = circular(rev, [(22, 268, 100, 290)], folga=8, largura=4)
    sim = simulacao(circular(sim, [(22, 268, 175, 290)], folga=8, largura=4), "SIMULAÇÃO")
    f3 = faixa("O \"Para revisar\": hoje e com a segunda opção", AZUL,
               "Hoje o cartão diz \"Página 7\" e não diz de que folha ela é (o Kaique, 26/10: \"A conta folha "
               "↔ página não é mostrada\"). Com a segunda opção: \"Página 7 (folha 4)\". (Simulação: o texto "
               "foi escrito por cima do print.)",
               lado_a_lado([rev, sim], ["hoje", "segunda opção (simulação)"], 520, 640,
                           cores_titulo={0: AZUL, 1: VERDE}))
    f2b = janela(dt / "F2-mover-tamanho-da-folha.png").crop((1180, 440, 1550, 540))
    f3b = janela(dt / "F3-automatico-endireitar-folhas.png").crop((1180, 360, 1550, 460))
    f4 = faixa("O que NÃO muda na segunda opção", LARANJA,
               "O botão \"tamanho da folha...\" do Mover e a etapa \"Endireitar folhas tortas\" do "
               "Automático ficam com o nome de hoje (só a primeira opção mudaria estes).",
               lado_a_lado([f2b, f3b], ["Mover", "Automático"], 600, 200))
    for n, (f, nome, leg) in enumerate([
            (f0, "folha-e-pagina", "Folha = a foto do scan; página = o que sai no PDF."),
            (f1, "livro-aberto-hoje", "Hoje: \"24 páginas\" em cima e \"página 3 de 12\" embaixo."),
            (f2, "livro-aberto-segunda-opcao",
             "Segunda opção (simulação): \"12 folhas, 24 páginas\", \"folha 3 de 12\"."),
            (f3, "para-revisar", "Para revisar: hoje \"Página 7\"; segunda opção \"Página 7 (folha 4)\"."),
            (f4, "o-que-nao-muda", "Na segunda opção estes nomes ficam.")], start=1):
        salvar(f, "nm-folha-pagina", f"folha-{n}-{nome}.png", leg)
    pequeno = [f0,
               cabeca("Livro aberto: hoje (esquerda) e com a segunda opção (direita)", AZUL,
                      "\"24 páginas\" + \"página 3 de 12\" vira \"12 folhas, 24 páginas\" + \"folha 3 de 12\"."),
               lado_a_lado([l6, l7], ["hoje", "segunda opção (simulação)"], 700, 380,
                           cores_titulo={0: AZUL, 1: VERDE}),
               cabeca("Para revisar: hoje e com a segunda opção", AZUL, "\"Página 7\" vira \"Página 7 (folha 4)\"."),
               lado_a_lado([rev, sim], ["hoje", "segunda opção"], 420, 500, cores_titulo={0: AZUL, 1: VERDE})]
    salvar(resumo_de("Folha e página — resumo",
                     "La vida eterna (cópia, 12 folhas = 24 páginas), dividido pelo Automático.", pequeno),
           "nm-folha-pagina", "folha-0-resumo.png",
           "Resumo: o que é folha, o que é página e o que a segunda opção muda.")


# --- nm-jeito-pb ---------------------------------------------------------------------------------

def item_jeito_pb():
    d = CRUS / "trabalho"
    p0 = circular(janela(d / "P0-painel-filtro-jeito.png"), [(1205, 532, 1515, 594), (1265, 114, 1330, 270)])
    hoje = sublinhar(abrir(d / "P1-lista-hoje.png"), [(6, 6, 284, 156)])
    op1 = simulacao(sublinhar(abrir(d / "P2-lista-SIMULACAO-pelo-uso.png"), [(6, 6, 284, 156)]), "SIMULAÇÃO", embaixo=True)
    op2 = simulacao(sublinhar(abrir(d / "P2-lista-SIMULACAO-so-padrao.png"), [(6, 6, 284, 156)]), "SIMULAÇÃO", embaixo=True)
    f0 = faixa("Onde fica", AZUL,
               "La vida eterna (cópia), página 3. Painel \"Filtro da página\" (à direita) > cartão \"Preto e "
               "branco\" > parte \"Mais ajustes\" > lista \"Jeito do preto e branco\" (circulada). A mesma lista "
               "existe no Automático (etapa \"Limpar a folha\") e em \"Filtros em tela cheia\".",
               caber(p0, 1400, 760))
    f1 = faixa("Você escolhe só as PALAVRAS dos 4 primeiros itens", AZUL,
               "A lista aberta: hoje (esquerda), a primeira opção (meio) e a segunda opção (direita). O que "
               "cada item faz com a página não muda em nenhuma opção. Os dez \"do ScanTailor\" ficam como "
               "estão (você mandou pôr assim em 21/10).",
               lado_a_lado([hoje, op1, op2], ["hoje", "opção 1: pelo uso", "opção 2: só tira \"(padrão)\""],
                           420, 500, cores_titulo={0: AZUL, 1: VERDE, 2: LARANJA}))
    salvar(f0, "nm-jeito-pb", "jeito-1-onde-fica.png", "Onde fica a lista \"Jeito do preto e branco\".")
    salvar(f1, "nm-jeito-pb", "jeito-2-os-nomes.png", "A lista hoje e com cada opção de nome (simulação).")
    salvar(resumo_de("Jeito do preto e branco — resumo",
                     "O que muda é só o texto da lista. Hoje, opção 1 e opção 2, lado a lado.", [f1, f0]),
           "nm-jeito-pb", "jeito-0-resumo.png", "Resumo: você escolhe as palavras da lista.")


# --- nm-tela-livros ------------------------------------------------------------------------------

def item_tela_livros():
    dl, dx = CRUS / "livros", CRUS / "extra"
    l3 = circular(abrir(dl / "L3-menu-do-livro.png"), [(30, 191, 160, 216)], folga=6, largura=4)
    l4 = circular(abrir(dl / "L4-janela-tirar-da-lista.png"), [(346, 173, 482, 221)], folga=6, largura=4)
    f1 = faixa("1. Tirar o livro da lista: MESMA coisa, dois nomes", AZUL,
               "Botão direito no cartão do livro (ou \"Mais...\"): o item se chama \"remover da lista\". Ele "
               "abre a janela \"Tirar da lista?\", com o botão \"Tirar da lista\". É um caminho só: o primeiro "
               "nome leva ao segundo. O PDF não é apagado.",
               lado_a_lado([l3, l4], ["menu: \"remover da lista\"", "janela: \"Tirar da lista\""], 640, 330))
    l0 = circular(janela(dl / "L0-tela-dos-livros.png").crop((280, 60, 560, 390)), [(110, 168, 253, 197)],
                  folga=8, largura=4)
    l2 = circular(abrir(dl / "L2-menu-do-livro-perdido.png"), [(30, 16, 155, 38)], folga=6, largura=4)
    r1 = circular(abrir(dl / "R1-pdf-trocado.png"), [(86, 196, 522, 218)], folga=6, largura=4)
    f2 = faixa("2. Achar o PDF que mudou de lugar: MESMA coisa, dois nomes", AZUL,
               "Palatino (cópia, arquivo mudado de nome). O cartão diz \"o PDF saiu do lugar\" e o botão "
               "\"procurar de novo\"; o menu do mesmo cartão diz \"procurar o livro\". Os dois abrem a mesma "
               "janela do Windows para apontar o PDF. O aviso de PDF trocado (embaixo) usa \"procurar de novo\".",
               lado_a_lado([l0, l2], ["o cartão", "o menu do cartão"], 560, 330),
               lado_a_lado([r1], ["o aviso de quando o PDF foi trocado: \"procurar de novo\""], 800, 330))
    x1 = circular(abrir(dx / "X1-menu-marcar.png"), [(20, 10, 160, 38)], folga=6, largura=4)
    f2b = faixa("Cuidado: \"Procurar de novo\" também é outra coisa", LARANJA,
                "Na área de trabalho, menu Marcar > \"Procurar de novo\" procura as GRAVURAS de novo. Mesmo "
                "nome, coisa diferente.", lado_a_lado([x1], ["menu Marcar"], 500, 220))
    l1 = circular(janela(dl / "L1-busca-horas.png").crop((0, 0, 1610, 400)),
                  [(325, 205, 590, 254), (1045, 18, 1320, 60)], folga=8, largura=4)
    l5 = circular(abrir(dl / "L5-janela-renomear.png"), [(22, 54, 182, 74)], folga=6, largura=4)
    f3 = faixa("3. \"Livro\" ou \"projeto\": MESMA coisa, duas palavras", AZUL,
               "O programa todo diz \"livro\" (\"Seus livros\"), mas a busca diz \"Nenhum projeto com "
               "'horas' no nome.\" e o \"renomear\" diz \"Nome deste projeto:\".",
               lado_a_lado([l1], ["busca \"horas\""], 1400, 380),
               lado_a_lado([l5], ["renomear"], 400, 260))
    for n, (f, nome, leg) in enumerate([
            (f1, "tirar-da-lista", "\"remover da lista\" e \"Tirar da lista\": o mesmo caminho."),
            (f2, "procurar-o-livro", "\"procurar de novo\" e \"procurar o livro\": a mesma janela."),
            (f2b, "procurar-de-novo-do-marcar", "No menu Marcar, \"Procurar de novo\" é outra coisa (gravuras)."),
            (f3, "livro-ou-projeto", "\"livro\" e \"projeto\": a mesma coisa.")], start=1):
        salvar(f, "nm-tela-livros", f"livros-{n}-{nome}.png", leg)
    salvar(resumo_de("Tela dos livros — resumo",
                     "Cópias do La vida eterna e do Palatino. Em cada faixa, o mesmo caminho com dois nomes "
                     "(circulados).", [f1, f2, f3]), "nm-tela-livros", "livros-0-resumo.png",
           "Resumo: três coisas, cada uma com dois nomes.")


# --- nm-antes-de-processar -----------------------------------------------------------------------

def item_antes_de_processar():
    d = CRUS / "trabalho"
    hoje = circular(abrir(d / "A0-antes-de-processar-hoje.png"), [(295, 473, 375, 519), (386, 473, 611, 519)],
                    folga=6, largura=4)
    sims = {nome: simulacao(sublinhar(abrir(d / f"A1-SIMULACAO-{nome}.png"), [(282, 472, 690, 522)]),
                            "SIMULAÇÃO")
            for nome in ("segunda", "nova-1", "nova-2", "nova-3")}
    textos = {
        "segunda": ("A segunda opção (a que você gostou)", LARANJA,
                    "\"ver\" vira \"ir para a página\"; \"continuar assim mesmo\" vira \"processar com os avisos\"."),
        "nova-1": ("Nova A", VERDE, "\"ver a página\" · \"processar mesmo assim\"."),
        "nova-2": ("Nova B", VERDE, "\"abrir esta página\" · \"processar sem olhar\"."),
        "nova-3": ("Nova C", VERDE, "\"conferir a página\" · \"processar agora\"."),
    }
    f0 = faixa("Como é hoje", AZUL,
               "La vida eterna (cópia), 5 páginas com aviso. Clique em \"Confirmar e processar\": abre \"Antes de "
               "processar\". Os dois botões de baixo à direita (circulados) são os que mudam nestas opções; "
               "\"Selecionar todas\", \"Nenhuma\" e \"está bom nas marcadas\" ficam.", caber(hoje, 900, 640))
    salvar(f0, "nm-antes-de-processar", "antes-1-hoje.png", "A janela hoje.")
    for n, nome in enumerate(("segunda", "nova-1", "nova-2", "nova-3"), start=2):
        rot, cor, frase = textos[nome]
        f = faixa(rot, cor, frase + " O que cada botão faz não muda.", caber(sims[nome], 900, 640))
        salvar(f, "nm-antes-de-processar", f"antes-{n}-{nome}.png", f"{rot} (simulação): {frase}")
    resumo = [cabeca("Antes de processar — resumo", CINZA,
                     "Hoje (azul), a segunda opção que você gostou (laranja) e três nomes novos na mesma linha "
                     "(verde). Só os dois botões de baixo à direita mudam."),
              lado_a_lado([hoje, sims["segunda"]], ["hoje", "segunda opção"], 700, 520,
                          cores_titulo={0: AZUL, 1: LARANJA}),
              lado_a_lado([sims["nova-1"], sims["nova-2"], sims["nova-3"]], ["nova A", "nova B", "nova C"],
                          470, 380, cores_titulo={0: VERDE, 1: VERDE, 2: VERDE})]
    salvar(empilhar(resumo), "nm-antes-de-processar", "antes-0-resumo.png",
           "Resumo: hoje, a segunda opção e três nomes novos.")


# --- au-d-489: quando a conferência começa de novo -----------------------------------------------

def item_489():
    dl = CRUS / "livros"
    h1 = circular(janela(dl / "H1-mudou-a-etapa-o-trabalho-ficou.png"), [(1195, 198, 1542, 330),
                                                                         (66, 594, 600, 632)])
    r1 = circular(abrir(dl / "R1-pdf-trocado.png"), [(86, 50, 620, 170)], folga=8, largura=4)
    r2a = circular(abrir(dl / "L3-menu-do-livro.png"), [(30, 54, 170, 78)], folga=6, largura=4)
    r2 = abrir(dl / "R2-comecar-de-novo.png")
    r2b = circular(janela(dl / "R2b-depois-de-comecar-de-novo.png"), [(1195, 198, 1542, 330),
                                                                       (66, 594, 600, 632)])
    r3 = circular(abrir(dl / "R3-trabalho-estragado.png"), [(86, 54, 690, 76)], folga=6, largura=4)
    f1 = faixa("1. Mudar uma etapa no Automático: o trabalho FICA", AZUL,
               "La vida eterna (cópia): dividido, página 3 posta em Preto e branco à mão, depois o Automático "
               "com \"Endireitar\". A página 3 continua em Preto e branco (embaixo) e o Histórico (direita) "
               "mostra as três coisas, uma depois da outra. Ctrl+Z desfaz só o Automático.",
               caber(h1, 1400, 760))
    f2 = faixa("2. O PDF trocado por outro no mesmo lugar: o programa NÃO abre", AZUL,
               "Troquei o arquivo da cópia por outro PDF com o mesmo nome e cliquei \"continuar\". O programa "
               "avisa \"Este não é o mesmo livro\" e não abre, para não pôr o trabalho num livro diferente. O "
               "trabalho continua guardado.", caber(r1, 900, 400))
    f3 = faixa("3. \"começar de novo\" do cartão: só quando você pede", AZUL,
               "Botão direito no cartão > \"começar de novo\" > a janela pergunta > \"Começar de novo\": o livro "
               "abre como novo: sem dividir (12 páginas de novo), sem o Preto e branco da página 3, Histórico "
               "vazio (\"nada ainda\") e o aviso \"Livro novo: ainda não passou pelo automático\".",
               lado_a_lado([r2a, r2], ["menu do cartão", "a pergunta"], 640, 300), caber(r2b, 1400, 700))
    f4 = faixa("4. O trabalho salvo estragado: começa de novo e GUARDA uma cópia", AZUL,
               "Estraguei de propósito o arquivo do trabalho da cópia (como se o computador desligasse no meio "
               "de uma gravação). Ao continuar, o programa avisa que começou de novo e diz onde guardou a "
               "cópia do trabalho antigo.", caber(r3, 1000, 400))
    for n, (f, nome, leg) in enumerate([
            (f1, "mudar-etapa", "Mudar uma etapa no Automático: o trabalho fica."),
            (f2, "pdf-trocado", "PDF trocado: o programa avisa e não abre."),
            (f3, "comecar-de-novo", "\"começar de novo\": só quando você pede, e pergunta antes."),
            (f4, "trabalho-estragado", "Trabalho estragado: começa de novo e guarda cópia.")], start=1):
        salvar(f, "au-d-489", f"489-{n}-{nome}.png", leg)
    pequeno = [
        cabeca("1. Mudar uma etapa no Automático", AZUL, "O trabalho fica (Histórico à direita)."),
        caber(h1, 900, 480),
        cabeca("2. PDF trocado  ·  3. \"começar de novo\"  ·  4. trabalho estragado", AZUL,
               "Não abre e avisa · pergunta antes e abre limpo · começa de novo e guarda cópia."),
        lado_a_lado([r1, r2, r3], ["2", "3", "4"], 470, 260)]
    salvar(resumo_de("Quando a conferência começa de novo — resumo",
                     "La vida eterna (cópia), testado na janela de verdade.", pequeno), "au-d-489",
           "489-0-resumo.png", "Resumo: só recomeça quando você pede ou quando o trabalho salvo estragou.")


ITENS = {"au-d-541": item_541, "au-d-487": item_487, "au-d-484": item_484, "au-d-492": item_492,
         "nm-folha-pagina": item_folha_pagina, "nm-jeito-pb": item_jeito_pb,
         "nm-tela-livros": item_tela_livros, "nm-antes-de-processar": item_antes_de_processar,
         "au-d-489": item_489}
