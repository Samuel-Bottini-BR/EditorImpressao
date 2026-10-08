"""As imagens da rodada 5 (../img/*.jpg).

Duas familias:
  - paginas de verdade (o que o programa de hoje faz), lidas dos dados da rodada 4
    (<TRABALHO>/dados4) e, para o "So o texto achado" do Graduale 222, da rodada 3
    (<TRABALHO>/dados; esse jeito nao rodou de novo: o conserto nao mexe nele);
  - DESENHOS DA PROPOSTA (o aviso do "Para revisar" com botoes, o seletor de
    paginas, a janela "Antes de processar"): nao sao a tela de verdade; a aparencia
    fica com o agente de layout. Toda imagem com desenho diz isso na legenda.
Simulacoes ("como ficaria") sao feitas numa COPIA, colando o resultado de outro
jeito dentro de um retangulo, ou cortando a imagem: estao escritas como simulacao.

Uso: python figuras5.py [nome,nome,...]
"""
from __future__ import annotations

import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

import comum
import desenho as D

DESTINO = comum.PASTA / "img"
AZUL, LARANJA, VERDE, CINZA, VERMELHO = (40, 110, 230), (240, 130, 0), (20, 150, 40), (120, 120, 120), (210, 30, 30)
AVISO_DESENHO = "DESENHO DA PROPOSTA (não é a tela de verdade; a aparência fica com o agente de layout)."


def ler(base: str, nome: str, pasta=None) -> np.ndarray:
    return cv2.imread(str((pasta or comum.DADOS) / f"{base}__{nome}.jpg"))


def mesmo_tamanho(img, ref):
    return cv2.resize(img, (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_AREA)


def colar(base_img, outro, caixa):
    """COPIA de base_img com o retangulo `caixa` (fracao) tirado de `outro`."""
    x = base_img.copy()
    a, l = x.shape[:2]
    x0, y0, x1, y1 = caixa
    sl = (slice(int(y0 * a), int(y1 * a)), slice(int(x0 * l), int(x1 * l)))
    x[sl] = outro[sl]
    return x


def retangulo(img, caixa, cor, esp=None, texto=None, tam=None):
    """COPIA com um retangulo tracejado (o que o Kaique desenha na aba Marcar)."""
    x = img.copy()
    a, l = x.shape[:2]
    x0, y0, x1, y1 = caixa
    m = np.zeros((a, l), np.uint8)
    cv2.rectangle(m, (int(x0 * l), int(y0 * a)), (int(x1 * l), int(y1 * a)), 255, -1)
    x = D.contorno(x, m > 0, cor, espessura=esp or max(6, l // 200))
    if texto:
        tam = tam or max(34, l // 40)
        x = D.rotulo(x, texto, (int(x0 * l) + 8, max(4, int(y0 * a) - tam - 16)), cor_rgb=cor, tamanho=tam)
    return x


def painel(titulo: str, frase: str, botoes: list[str], largura=820, destaque=0, alto=None) -> np.ndarray:
    """Desenho do aviso do "Para revisar" (a caixa laranja da direita, aberta numa
    pagina), com os botoes. `destaque`: indice do botao em que o Kaique clica
    (desenhado com o ponteiro do mouse); None = nenhum."""
    f, fb, fp = D.fonte(30), D.fonte(32, True), D.fonte(28, True)
    im = Image.new("RGB", (largura, 10), "white")
    d = ImageDraw.Draw(im)
    linhas, atual = [], ""
    for palavra in frase.split():
        teste = (atual + " " + palavra).strip()
        if d.textlength(teste, font=f) > largura - 60:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    linhas.append(atual)
    h = 90 + 42 * len(linhas) + 30 + 80 * len(botoes) + 30
    h = max(h, alto or 0)
    im = Image.new("RGB", (largura, h), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, largura - 1, h - 1], outline=(200, 160, 110), width=4)
    d.rectangle([2, 2, largura - 3, 70], fill=(255, 236, 210))
    d.text((24, 18), titulo, font=fb, fill=(60, 40, 20))
    y = 90
    for t in linhas:
        d.text((28, y), t, font=f, fill=(30, 30, 30))
        y += 42
    y += 24
    for i, b in enumerate(botoes):
        cor = (40, 110, 230) if i == destaque else (110, 110, 110)
        d.rounded_rectangle([28, y, largura - 28, y + 62], 12, outline=cor, width=4,
                            fill=(225, 236, 255) if i == destaque else (245, 245, 245))
        d.text((48, y + 14), b, font=fp, fill=cor)
        if i == destaque:
            px, py = largura - 90, y + 40
            d.polygon([(px, py), (px, py + 46), (px + 12, py + 34), (px + 22, py + 56), (px + 30, py + 52),
                       (px + 20, py + 31), (px + 36, py + 30)], fill=(20, 20, 20))
        y += 80
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


def tres(arquivo, quadros, legendas, titulo=None, alto=760, ampliar=3.0):
    w = D.largura_de(len(quadros))
    q = [D.quadro(img, t, w, alto, ampliar) for img, t in quadros]
    D.montar([q], legendas, DESTINO / f"{arquivo}.jpg", titulo)


# ---------------------------------------------------------------------------
# Erro 1: a letra grande que some (Antiphonal 46)
# ---------------------------------------------------------------------------
A46 = "antiphonal1547_p046__inteira"
CX46 = (0.0, 0.14, 0.62, 0.42)          # a parte ampliada
T46 = (0.078, 0.245, 0.17, 0.35)       # em volta da letra T


def _rec(img, caixa=CX46):
    return D.recortar(img, caixa)


def f_desenho():
    ori, a, t, pb = ler(A46, "original"), ler(A46, "a"), ler(A46, "t"), ler(A46, "pb")
    a, t, pb = mesmo_tamanho(a, ori), mesmo_tamanho(t, ori), mesmo_tamanho(pb, ori)
    w = D.largura_de(3)
    cima = [D.quadro(D.amarelo(ori, CX46), "A página (amarelo = ampliada)", w, 620, 1.0),
            D.quadro(_rec(ori), "Original: a letra T vermelha", w, 620),
            D.quadro(_rec(a), "Como sai: a letra T sumiu", w, 620)]
    D.montar([cima], ["Antiphonal 46. A letra T vermelha grande (à esquerda de 'Tunc invoca') some no Preto e branco",
                      "com 'Só as letras' de fábrica. É isso que manda a página para 'Para revisar'."],
             DESTINO / "r5-desenho-o-que-acontece.jpg")
    # opcao 1: botao no aviso
    tres("r5-desenho-op-botao",
         [(_rec(a), "1. O Kaique vê: a letra sumiu"),
          (painel("Para revisar · página 46", "Sumiu uma letra grande ou um desenho que eu não reconheci.",
                  ["Trazer de volta nesta página", "Está bom assim"]), "2. No aviso, ele clica no botão"),
          (_rec(t), "3. A letra volta")],
         ["Opção 'Botão no aviso'. O botão troca só esta página para 'Guardar tudo' (o que não é texto sai como no Preto",
          "e branco de sempre). " + AVISO_DESENHO])
    # opcao 2: marcar a mao
    marcado = retangulo(a, T46, AZUL, texto="letra e traço")
    depois = colar(a, pb, T46)
    tres("r5-desenho-op-mao",
         [(_rec(a), "1. O Kaique vê: a letra sumiu"),
          (_rec(marcado), "2. Aba Marcar: 'letra e traço' e um retângulo"),
          (_rec(depois), "3. A letra volta (simulação)")],
         ["Opção 'Marcar à mão' (já existe hoje, na aba Marcar). Só o que está dentro do retângulo volta.",
          "O quadro 3 é uma simulação: colei ali o Preto e branco de sempre, que é o que a marcação faz."])
    # opcao 3: sozinho
    tres("r5-desenho-op-sozinho",
         [(_rec(t), "1. A página já sai com a letra"),
          (painel("Para revisar · página 46", "Eu tinha apagado uma letra grande e a trouxe de volta.",
                  ["Desfazer (apagar de novo)", "Está bom assim"], destaque=None), "2. O aviso diz o que foi feito")],
         ["Opção 'O programa traz sozinho'. Ele mesmo troca a página para 'Guardar tudo' e avisa; o Kaique só desfaz se quiser.",
          AVISO_DESENHO])


# ---------------------------------------------------------------------------
# Erro 5: pagina sem conteudo (Egenloff 12)
# ---------------------------------------------------------------------------
def _fila(paginas: list[tuple[str, np.ndarray | None]], largura=820) -> np.ndarray:
    """Desenho: as paginas em fila, como vao para a encadernacao (frente/verso)."""
    n = len(paginas)
    w = (largura - 20 * (n + 1)) // n
    h = int(w * 1.35)
    tela = np.full((h + 110, largura, 3), 255, np.uint8)
    for i, (rot, img) in enumerate(paginas):
        x = 20 + i * (w + 20)
        if img is None:
            cv2.rectangle(tela, (x, 20), (x + w, 20 + h), (255, 255, 255), -1)
        else:
            tela[20:20 + h, x:x + w] = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        cv2.rectangle(tela, (x, 20), (x + w, 20 + h), (120, 120, 120), 3)
        pil = Image.fromarray(cv2.cvtColor(tela, cv2.COLOR_BGR2RGB))
        dd = ImageDraw.Draw(pil)
        dd.text((x + 6, 30 + h), rot, font=D.fonte(26, True), fill=(30, 30, 30))
        tela = cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
    return tela


def f_sem_conteudo():
    b = "egenloff_p012__inteira"
    ori, a = ler(b, "original"), ler(b, "a")
    a = mesmo_tamanho(a, ori)
    vizinha = ler("egenloff_p047__inteira", "a")
    vizinha2 = ler("egenloff_p121__inteira", "a")
    tres("r5-vazia-o-que-acontece",
         [(ori, "Original: o verso em branco de uma prancha"), (a, "Como sai")],
         ["Egenloff 12: a página não tem nada do livro (só o carimbo da biblioteca e a moldura do scanner).",
          "A Rariora 8 é igual: só a mancha da página de trás. O programa avisa: 'página sem conteúdo'."], ampliar=1.0)
    branco = np.full_like(a, 255)
    tres("r5-vazia-op-branco",
         [(painel("Para revisar · página 12", "Esta página não tem conteúdo (em branco, ou só a mancha da página de trás).",
                  ["Deixar em branco", "Tirar do livro", "Está bom assim"]), "1. O Kaique clica em 'Deixar em branco'"),
          (_fila([("11", vizinha), ("12", None), ("13", vizinha2)]), "2. Fica uma folha branca no lugar")],
         ["'Deixar em branco': a página 12 sai branca, no mesmo lugar. A frente e o verso das páginas seguintes não mudam.",
          AVISO_DESENHO], ampliar=1.0)
    tres("r5-vazia-op-tirar",
         [(painel("Para revisar · página 12", "Esta página não tem conteúdo (em branco, ou só a mancha da página de trás).",
                  ["Deixar em branco", "Tirar do livro", "Está bom assim"], destaque=1), "1. O Kaique clica em 'Tirar do livro'"),
          (_fila([("11", vizinha), ("13", vizinha2), ("14", vizinha)]), "2. A página some e as outras andam uma casa")],
         ["'Tirar do livro': a página sai de vez. As seguintes andam uma casa: o que era frente vira verso.",
          "Serve para o que não é página do livro (folha de proteção, régua de cor). " + AVISO_DESENHO], ampliar=1.0)


# ---------------------------------------------------------------------------
# Erro 6: "Guardar so o texto" (Graduale 222)
# ---------------------------------------------------------------------------
G222 = "graduale_p222__inteira"
CXG = (0.0, 0.0, 1.0, 0.42)
PAUTA = (0.03, 0.125, 0.97, 0.215)


def f_so_texto():
    R3 = comum.DADOS_R3
    ori, c, a = ler(G222, "original", R3), ler(G222, "c", R3), ler(G222, "a", R3)
    c, a = mesmo_tamanho(c, ori), mesmo_tamanho(a, ori)
    w = D.largura_de(3)
    cima = [D.quadro(D.amarelo(ori, CXG), "A página (amarelo = ampliada)", w, 640, 1.0),
            D.quadro(D.recortar(ori, CXG), "Original: texto e música", w, 640),
            D.quadro(D.recortar(c, CXG), "Como sai: a música sumiu", w, 640)]
    D.montar([cima], ["Graduale 222. Com 'Guardar só o texto' (antes 'Só o texto achado') o programa apaga tudo que não é",
                      "linha de texto: aqui, a música inteira. Essa página vai para 'Para revisar'."],
             DESTINO / "r5-sotexto-o-que-acontece.jpg")
    tres("r5-sotexto-op-botao",
         [(D.recortar(c, CXG), "1. O Kaique vê: a música sumiu"),
          (painel("Para revisar · página 222", "Sumiu música, letra grande ou desenho (você escolheu 'Guardar só o texto').",
                  ["Trazer de volta nesta página", "Está bom assim"]), "2. No aviso, ele clica no botão"),
          (D.recortar(a, CXG), "3. A música volta")],
         ["Opção 'Botão no aviso'. O botão troca só esta página para 'Guardar a tinta forte'; as outras continuam só com o texto.",
          AVISO_DESENHO])
    marcado = retangulo(c, PAUTA, AZUL, esp=14, texto="letra e traço", tam=130)
    depois = colar(c, a, PAUTA)
    tres("r5-sotexto-op-mao",
         [(D.recortar(c, CXG), "1. O Kaique vê: a música sumiu"),
          (D.recortar(marcado, CXG), "2. Aba Marcar: retângulo na pauta"),
          (D.recortar(depois, CXG), "3. Só essa pauta volta (simulação)")],
         ["Opção 'Marcar à mão' (já existe hoje). Volta só o que ele marcou; o resto continua apagado.",
          "O quadro 3 é uma simulação: colei ali o resultado de 'Guardar a tinta forte'."])


# ---------------------------------------------------------------------------
# Respostas aos comentarios
# ---------------------------------------------------------------------------
def f_delineado():
    b = "camoes_p104__inteira"
    ori = ler(b, "original")
    z = np.load(comum.DADOS / f"{b}.npz")
    m = cv2.resize(z["imagem"].astype(np.uint8) * 255, (ori.shape[1], ori.shape[0])) > 0
    n, rot, st, _c = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    maior = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    zona = rot == maior
    clara = (ori.astype(np.float32) * 0.75 + 255 * 0.25).astype(np.uint8)
    x, y, w, h = st[maior, :4]
    # (a) alcas: o retangulo da area com quadradinhos nos cantos e no meio dos lados
    alca = D.contorno(clara, zona, LARANJA, espessura=8)
    lado = max(40, ori.shape[1] // 22)
    for px, py in [(x, y), (x + w, y), (x, y + h), (x + w, y + h), (x + w // 2, y), (x + w // 2, y + h),
                   (x, y + h // 2), (x + w, y + h // 2)]:
        cv2.rectangle(alca, (px - lado // 2, py - lado // 2), (px + lado // 2, py + lado // 2), (255, 255, 255), -1)
        cv2.rectangle(alca, (px - lado // 2, py - lado // 2), (px + lado // 2, py + lado // 2), (0, 130, 240), 5)
    cv2.arrowedLine(alca, (x + w - int(0.02 * ori.shape[1]), y + h - int(0.02 * ori.shape[0])),
                    (x + w - int(0.12 * ori.shape[1]), y + h - int(0.09 * ori.shape[0])),
                    (230, 110, 40), max(8, ori.shape[1] // 120), tipLength=0.35)
    # (b) pincel: um circulo "somar" e um "tirar"
    pincel = D.contorno(clara, zona, LARANJA, espessura=8)
    r = max(40, ori.shape[1] // 14)
    for (cx, cy, txt, cor) in [(x + int(w * 0.15), y + h + r // 2, "+ somar", (40, 160, 40)),
                               (x + int(w * 0.85), y + int(h * 0.1), "- tirar", (40, 40, 210))]:
        cv2.circle(pincel, (cx, cy), r, cor, 6)
        pincel = D.rotulo(pincel, txt, (cx - r, cy + r + 10), cor_rgb=cor[::-1], tamanho=max(30, ori.shape[1] // 35))
    tres("r5-delineado-ajustar", [(alca, "A: puxar pelos quadradinhos"), (pincel, "B: pincel 'somar' / 'tirar'")],
         ["Duas formas de aumentar ou diminuir a área achada (Camões 104). A: puxar os quadradinhos dos cantos e dos lados",
          "(a seta mostra o canto sendo puxado para dentro). B: passar um pincel redondo: 'somar' (verde) aumenta, 'tirar' (vermelho)",
          "diminui. " + AVISO_DESENHO], ampliar=1.0, alto=900)


def f_seletor():
    _seletor("r5-seletor", ["Selecionar todas", "Nenhuma", "Só as pares", "Só as ímpares"])
    _seletor("r5-seletor-2", ["Selecionar todas", "Nenhuma"])


def _seletor(arquivo, botoes):
    """Desenho do seletor grande de paginas (para o corte e para os avisos)."""
    pids = ["egenloff_p003", "egenloff_p007", "egenloff_p012", "egenloff_p047", "egenloff_p121", "egenloff_p131"]
    W, H = 1800, 980
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(160, 160, 160), width=3)
    d.text((24, 18), "Escolher as páginas", font=D.fonte(36, True), fill=(20, 20, 20))
    bx = 24
    for nome in botoes:
        wbt = int(d.textlength(nome, font=D.fonte(28, True))) + 40
        d.rounded_rectangle([bx, 80, bx + wbt, 136], 10, outline=(40, 110, 230), width=3, fill=(225, 236, 255))
        d.text((bx + 20, 92), nome, font=D.fonte(28, True), fill=(30, 60, 150))
        bx += wbt + 20
    marcadas = [True, True, False, True, True, True]
    tw, th = 250, 330
    for i, pid in enumerate(pids):
        x = 24 + i * (tw + 40)
        y = 170
        th_img = cv2.imread(str(comum.DADOS / f"{pid}__inteira__a.jpg"))
        th_img = cv2.cvtColor(cv2.resize(th_img, (tw, th), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        im.paste(Image.fromarray(th_img), (x, y))
        d.rectangle([x, y, x + tw, y + th], outline=(40, 110, 230) if marcadas[i] else (170, 170, 170),
                    width=6 if marcadas[i] else 2)
        cx, cy = x + 14, y + th + 18
        d.rectangle([cx, cy, cx + 36, cy + 36], outline=(40, 40, 40), width=3, fill=(40, 110, 230) if marcadas[i] else "white")
        if marcadas[i]:
            d.line([cx + 7, cy + 18, cx + 15, cy + 28, cx + 30, cy + 8], fill="white", width=5)
        d.text((cx + 50, cy + 2), f"página {pid.split('_p')[1].lstrip('0')}", font=D.fonte(28), fill=(30, 30, 30))
        if i == 2:
            d.text((x, cy + 48), "(exceção: corte próprio)", font=D.fonte(24), fill=(200, 90, 20))
    d.rounded_rectangle([24, 640, 700, 710], 12, outline=(20, 130, 60), width=4, fill=(225, 245, 230))
    d.text((44, 655), "Aplicar o corte nas 5 marcadas", font=D.fonte(32, True), fill=(20, 100, 40))
    for i, t in enumerate(["A mesma janela serve para o corte (em que páginas vale) e para os avisos (quais marcar como vistos).",
                           "Mudar o corte de uma página depois vira exceção só dela: as outras não mudam.",
                           AVISO_DESENHO]):
        d.text((24, 760 + 52 * i), t, font=D.fonte(28), fill=(50, 50, 50))
    destino = DESTINO / f"{arquivo}.jpg"
    im.save(destino, quality=88)
    print(destino.name, im.size)


def f_antes_de_processar():
    W = 1800
    im = Image.new("RGB", (W, 700), "white")
    d = ImageDraw.Draw(im)
    x0, y0 = 300, 30
    d.rectangle([x0, y0, x0 + 1200, y0 + 430], outline=(120, 120, 120), width=3, fill=(250, 250, 250))
    d.rectangle([x0, y0, x0 + 1200, y0 + 60], fill=(230, 230, 230))
    d.text((x0 + 20, y0 + 14), "Antes de processar", font=D.fonte(30, True), fill=(30, 30, 30))
    d.text((x0 + 40, y0 + 100), "Ainda tem 12 páginas que eu não tive certeza.", font=D.fonte(34, True), fill=(20, 20, 20))
    d.text((x0 + 40, y0 + 160), "Quer conferir antes ou processar assim mesmo?", font=D.fonte(30), fill=(40, 40, 40))
    for i, (nome, cor) in enumerate([("conferir", (40, 110, 230)), ("processar assim mesmo", (110, 110, 110))]):
        bx = x0 + 40 + i * 330
        wbt = int(d.textlength(nome, font=D.fonte(30, True))) + 50
        d.rounded_rectangle([bx, y0 + 300, bx + wbt, y0 + 370], 10, outline=cor, width=4, fill=(240, 244, 252))
        d.text((bx + 25, y0 + 316), nome, font=D.fonte(30, True), fill=cor)
    for i, t in enumerate(["Esta janela JÁ EXISTE no programa (desenho com os textos de verdade): ao clicar em 'Confirmar e processar' com",
                           "páginas do 'Para revisar' ainda não conferidas, ele para e pergunta. 'conferir' leva à primeira página com aviso."]):
        d.text((24, 500 + 50 * i), t, font=D.fonte(28), fill=(50, 50, 50))
    destino = DESTINO / "r5-antes-de-processar.jpg"
    im = im.crop((0, 0, W, 610))
    im.save(destino, quality=88)
    print(destino.name, im.size)


def f_avisos_separados():
    p1 = painel("Para revisar · página 18", "Esta página parece estar em branco.",
                ["Deixar em branco", "Tirar do livro", "Está bom assim"], destaque=None, largura=860)
    p2 = painel("Para revisar · página 8", "Esta página não tem conteúdo: só a mancha da página de trás.",
                ["Deixar em branco", "Tirar do livro", "Está bom assim"], destaque=None, largura=860)
    tres("r5-avisos-separados", [(p1, "Aviso 'Parece em branco'"), (p2, "Aviso 'Página sem conteúdo'")],
         ["Um aviso para cada coisa, cada um com os dois botões separados: 'Deixar em branco' (folha branca no lugar)",
          "e 'Tirar do livro' (a página sai de vez). " + AVISO_DESENHO], ampliar=1.0)


def caixa_do_papel(ori):
    """A pagina dentro da moldura do scanner e acima da tarja: o maior pedaco de
    'papel claro' (cinza > 150). So para a simulacao."""
    g = cv2.cvtColor(ori, cv2.COLOR_BGR2GRAY)
    m = (g > 150).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
    n, rot, st, _c = cv2.connectedComponentsWithStats(m, connectivity=8)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = st[i, :4]
    a, l = g.shape
    return (x / l, y / a, (x + w) / l, (y + h) / a)


def f_egenloff047():
    b = "egenloff_p047__inteira"
    ori, a = ler(b, "original"), ler(b, "a")
    a = mesmo_tamanho(a, ori)
    cx = caixa_do_papel(ori)
    cortado = D.recortar(a, cx)
    pintado = np.full_like(a, 255)
    al, ll = a.shape[:2]
    x0, y0, x1, y1 = cx
    pintado[int(y0 * al):int(y1 * al), int(x0 * ll):int(x1 * ll)] = a[int(y0 * al):int(y1 * al), int(x0 * ll):int(x1 * ll)]
    olhar = ori.copy()
    m = np.ones(ori.shape[:2], bool)
    m[int(y0 * al):int(y1 * al), int(x0 * ll):int(x1 * ll)] = False
    olhar = D.tingir(olhar, m, LARANJA, 0.55)
    tres("r5-egenloff047-tarja",
         [(olhar, "Onde olhar: em laranja, moldura e tarja"), (a, "Como sai hoje"),
          (cortado, "Simulação: cortado fora"), (pintado, "Simulação: pintado de branco")],
         ["Egenloff 47. Em laranja (cópia do original), o que não é do livro: a moldura preta do scanner e a tarja 'SLUB' da biblioteca.",
          "Os dois quadros da direita são SIMULAÇÕES (cortei pela beirada do papel claro): cortar fora deixa a página menor;",
          "pintar de branco mantém o tamanho da folha."], ampliar=1.0)


TODAS = {"desenho": f_desenho, "sem-conteudo": f_sem_conteudo, "so-texto": f_so_texto, "delineado": f_delineado,
         "seletor": f_seletor, "antes-de-processar": f_antes_de_processar, "avisos-separados": f_avisos_separados,
         "egenloff047": f_egenloff047}


def main() -> None:
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else list(TODAS)
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome in so:
        TODAS[nome]()


if __name__ == "__main__":
    main()
