"""As imagens da rodada 4 (../img/*.jpg). Formato que o Samuel entende: a folha
inteira em cima, com a parte ampliada em amarelo transparente; os quadros lado a
lado embaixo, cada um com o titulo; a legenda fixa no pe. Nada e desenhado por
cima do Original, do Resultado nem do Preto e branco: o que e marcado (contorno,
cor) vai sempre numa COPIA, com titulo proprio ("Onde olhar", "Como ficaria").

Os dados vem do rodar.py (dados4, fase-1 de hoje) e, para as paginas que nao
rodaram na rodada 4, da rodada 3 (sinais4.pasta_de).

Uso: python figuras4.py [nome,nome,...]
"""
from __future__ import annotations

import json
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

import comum
import desenho as D
from sinais4 import pasta_de

DESTINO = comum.PASTA / "img"
S = json.loads((comum.TRABALHO / "sinais-rodada4.json").read_text(encoding="utf-8"))
NOMES = {"original": "Original", "a": "Jeito de fábrica (Guardar a tinta forte)",
         "t": "Guardar tudo", "pb": "Preto e branco de sempre"}
VERMELHO, LARANJA, VERDE, AZUL, ROXO = (225, 20, 20), (255, 130, 0), (20, 150, 40), (40, 110, 230), (150, 40, 200)


def ler(base: str, nome: str) -> np.ndarray:
    return cv2.imread(str(pasta_de(base) / f"{base}__{nome}.jpg"))


def mascara(base: str, chave: str, forma) -> np.ndarray:
    z = np.load(pasta_de(base) / f"{base}.npz")
    m = z[chave]
    return cv2.resize(m.astype(np.uint8) * 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA) > 40


def apagado(base: str, forma) -> np.ndarray:
    from sinais4 import apagado_real
    d = json.loads((pasta_de(base) / f"{base}.json").read_text(encoding="utf-8"))
    z = dict(np.load(pasta_de(base) / f"{base}.npz"))
    _a, _j, m = apagado_real(d, z)
    r = max(2, int(round(d["altura_linha"] * 0.08)))
    m = cv2.dilate(m.astype(np.uint8), np.ones((r, r), np.uint8))
    return cv2.resize(m * 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA) > 40


def escala_z(base: str, forma) -> float:
    d = json.loads((pasta_de(base) / f"{base}.json").read_text(encoding="utf-8"))
    return forma[1] / d["tamanho"][0]


def onde_olhar(img: np.ndarray, camadas) -> np.ndarray:
    """Copia clareada do original com as camadas [(mascara, cor, forca)]."""
    x = (img.astype(np.float32) * 0.6 + 255 * 0.4).astype(np.uint8)
    for m, cor, f in camadas:
        x = D.tingir(x, m, cor, f)
    return x


def caixas_desenhadas(img, caixas, cor, esp=6):
    x = img.copy()
    for (x0, y0, x1, y1) in caixas:
        cv2.rectangle(x, (int(x0), int(y0)), (int(x1), int(y1)), tuple(int(c) for c in cor[::-1]), esp)
    return x


def pagina_em_cima(arquivo, base, caixa, quadros, legendas, titulo=None, extras_em_cima=(),
                   alto_cima=620, alto_baixo=820, ampliar=3.0):
    """Em cima: a folha inteira (original) com a caixa em amarelo, e ao lado as
    `extras_em_cima` [(img, titulo)] tambem inteiras. Embaixo: os `quadros`
    [(img inteira, titulo)] recortados na caixa e ampliados, lado a lado."""
    ori = ler(base, "original")
    if tuple(caixa) == (0.0, 0.0, 1.0, 1.0) and not extras_em_cima:
        # a pagina inteira ja e o que se amplia: so a fileira de quadros
        n2 = len(quadros)
        baixo = [D.quadro(im, t, D.largura_de(n2), alto_baixo, ampliar) for im, t in quadros]
        D.montar([baixo], legendas, DESTINO / f"{arquivo}.jpg", titulo)
        return
    cima_imgs = [(D.amarelo(ori, caixa), "Página inteira (em amarelo, a parte ampliada)")] + list(extras_em_cima)
    n1 = len(cima_imgs)
    w1 = min(D.largura_de(n1), 900) if n1 > 1 else 900
    cima = [D.quadro(im if im.shape[:2] == ori.shape[:2] else im, t, w1, alto_cima, 1.0) for im, t in cima_imgs]
    n2 = len(quadros)
    w2 = D.largura_de(n2)
    baixo = [D.quadro(D.recortar(im, caixa), t, w2, alto_baixo, ampliar) for im, t in quadros]
    D.montar([cima, baixo], legendas, DESTINO / f"{arquivo}.jpg", titulo)


# ---------------------------------------------------------------------------
# cada imagem
# ---------------------------------------------------------------------------

def f_resumo():
    """A tabela da regra ajustada (texto desenhado)."""
    linhas = [
        ("O que manda a página para 'Para revisar'", "Exemplo", "Novo?"),
        ("1. O jeito de fábrica apagou parte de um desenho", "Antiphonal 46 (a letra T vermelha some)", "ajustado"),
        ("2. Uma figura passou da gravura achada, ou uma mancha virou 'gravura'", "Marial 454, Camões 104", "igual"),
        ("3. Faixa escura na beirada (em 70% das páginas: um aviso só, no livro)", "Matemática 32; Egenloff (livro)", "igual"),
        ("4. Texto que sai falhado nos DOIS jeitos (letra clara ou vermelha)", "Camões 27, Camões 104, Egenloff 3", "NOVO"),
        ("5. Página sem conteúdo (em branco, ou só mancha do verso)", "Egenloff 12, Rariora 8", "NOVO"),
    ]
    contas = [
        ("Nas 89 páginas (59 do estudo + 30 da rodada 3)", "Vão", "Acertam"),
        ("Hoje (o aviso do programa)", "55", "52 de 89"),
        ("Regra da rodada 3 (no programa de hoje)", "15", "72 de 89"),
        ("Regra ajustada (rodada 4)", "21", "78 de 89"),
    ]
    W = D.LARGURA
    im = Image.new("RGB", (W, 900), "white")
    d = ImageDraw.Draw(im)
    y = 10
    d.text((10, y), "A regra ajustada, com o programa de hoje (com o conserto do desenho claro)", font=D.fonte(34, True), fill=(10, 10, 10))
    y += 64
    cols = [10, 1000, 1640]
    for i, row in enumerate(linhas):
        f = D.fonte(26, i == 0)
        if i:
            d.rectangle([4, y - 6, W - 4, y + 40], fill=(255, 245, 210) if row[2] == "NOVO" else (245, 245, 245))
        for c, t in zip(cols, row):
            d.text((c, y), t, font=f, fill=(20, 20, 20))
        y += 52
    y += 30
    cols = [10, 1000, 1300]
    for i, row in enumerate(contas):
        f = D.fonte(28, i == 0 or i == 3)
        for c, t in zip(cols, row):
            d.text((c, y), t, font=f, fill=(20, 20, 20))
        y += 50
    y += 20
    for t in ["'Acertam' = a página vai quando deveria ir e não vai quando não deveria (pelas suas respostas das",
              "rodadas 1 e 3; nas páginas que você não viu, pelo meu olho). Escapam 5 (Antiphonal 6 e 31, Camões 9 e 66,",
              "Egenloff 47); vão sem precisar 6 (beiradas e figuras que passam da gravura, de leve)."]:
        d.text((10, y), t, font=D.fonte(25), fill=(50, 50, 50))
        y += 38
    im = im.crop((0, 0, W, y + 10))
    destino = DESTINO / "resumo-regra4.jpg"
    im.save(destino, quality=90)
    print(destino.name, im.size)


def f_desenho():
    b = "antiphonal1547_p046__inteira"
    cx = (0.0, 0.12, 0.62, 0.42)
    pagina_em_cima("c1-desenho-antiphonal046", b, cx,
                   [(ler(b, "original"), "Original"), (ler(b, "a"), NOMES["a"]),
                    (ler(b, "t"), "Um clique: 'Guardar tudo'"), (ler(b, "pb"), NOMES["pb"])],
                   ["Antiphonal 46 (programa de hoje, com o conserto). A letra T vermelha some no jeito de fábrica.",
                    "O jeito mais rápido: trocar a página para 'Guardar tudo' (aba Filtro). A letra volta, como no Preto e branco."])


def f_texto_camoes027():
    b = "camoes_p027__inteira"
    cx = (0.05, 0.16, 0.62, 0.33)
    ori = ler(b, "original")
    f85 = cv2.imread(str(comum.TRABALHO / "forca" / f"{b}__f85.png"))
    f85 = cv2.resize(f85, (ori.shape[1], ori.shape[0]), interpolation=cv2.INTER_AREA)
    pagina_em_cima("c4-texto-camoes027", b, cx,
                   [(ori, "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), "Preto e branco (força de fábrica)"),
                    (f85, "Um clique: força do preto mais forte")],
                   ["Camões 27. As letras claras perdem os traços finos nos dois jeitos ('que' vira 'qne', 'e' vira 'c').",
                    "O jeito mais rápido: puxar a 'Força do preto' para o lado do escuro (aqui, 85 em vez de 50): as letras se fecham."])


def f_egenloff003():
    b = "egenloff_p003__inteira"
    cx = (0.12, 0.76, 0.88, 0.92)
    pagina_em_cima("p-egenloff-003", b, cx,
                   [(ler(b, "original"), "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"])],
                   ["Egenloff 3. As duas linhas vermelhas do pé ('1880 neu aufgelegt von / George Gilbers...') saem falhadas",
                    "nos dois jeitos. A força do preto mais forte NÃO conserta (testei 70 e 85): o vermelho fica claro demais.",
                    "Ressalva: das duas linhas que a regra conta aqui, uma é a vermelha do pé; a outra é o carimbo da biblioteca no alto."])


def f_sem_conteudo():
    trios = [("egenloff_p012__inteira", "Egenloff 12", "hoje: vai, pela moldura preta", "regra ajustada: VAI"),
             ("rariora_p008__inteira", "Rariora 8", "hoje: não avisa", "regra ajustada: VAI"),
             ("gladstone_p018__inteira", "Gladstone 18", "hoje: 'Parece em branco. Quer apagar?'", "regra ajustada: não vai")]
    w = D.largura_de(3)
    cima = [D.quadro(ler(b, "original"), f"{n}: original", w, 700, 1.0) for b, n, _h, _r in trios]
    baixo = [D.quadro(ler(b, "a"), f"{h} / {r}", w, 700, 1.0) for b, n, h, r in trios]
    D.montar([cima, baixo],
             ["Em cima, o original; embaixo, como sai hoje (jeito de fábrica), com o que o programa faz hoje e a regra ajustada.",
              "Hoje o Egenloff 12 vai para 'Para revisar' só porque a moldura preta conta como 'tinta forte fora do texto'.",
              "Egenloff 12 é o verso em branco de uma prancha; a Rariora 8 só tem a mancha do verso e um selo escuro.",
              "A Gladstone 18 tem um título ('DA ORAÇÃO'): hoje o programa diz 'Parece em branco' e oferece APAGAR. A regra nova não a pega."],
             DESTINO / "c5-sem-conteudo.jpg")


def f_rariora169():
    b = "rariora_p169__inteira"
    cx = (0.55, 0.3, 1.0, 0.65)
    antes = cv2.imread(str(comum.DADOS_R3 / f"{b}__a.jpg"))
    ori = ler(b, "original")
    antes = cv2.resize(antes, (ori.shape[1], ori.shape[0]), interpolation=cv2.INTER_AREA)
    pagina_em_cima("p-rariora-169", b, cx,
                   [(ori, "Original"), (antes, "Rodada 3: jeito de fábrica SEM o conserto"),
                    (ler(b, "a"), "Hoje: jeito de fábrica COM o conserto"), (ler(b, "pb"), NOMES["pb"])],
                   ["Rariora 169, a concha oval (Fig. 8). Na rodada 3 o pontilhado de dentro sumia.",
                    "Com o conserto do desenho claro (entrou no programa em 06/10), a concha sai inteira."])


def f_camoes104():
    b = "camoes_p104__inteira"
    cx = (0.25, 0.74, 0.8, 0.9)
    ori = ler(b, "original")
    forma = ori.shape[:2]
    f85 = cv2.imread(str(comum.TRABALHO / "forca" / f"{b}__f85.png"))
    f85 = cv2.resize(f85, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    olhar = onde_olhar(ori, [(mascara(b, "imagem", forma), VERDE, 0.35)])
    pagina_em_cima("p-camoes-104", b, cx,
                   [(ori, "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"]),
                    (f85, "Força do preto mais forte (85)")],
                   ["Camões 104 (contracapa). O título 'LUIZ DE CAMÕES' sai 'LUIZ DI CAMÕUS' nos dois jeitos;",
                    "com a força do preto mais forte, o 'DE' volta. Em cima, à direita: em verde, a gravura achada, que escorre pela beirada."],
                   extras_em_cima=[(olhar, "Onde olhar: em verde, a gravura achada")])


def f_camoes027():
    b = "camoes_p027__inteira"
    cx = (0.0, 0.5, 1.0, 0.85)
    ori = ler(b, "original")
    f = escala_z(b, ori.shape[:2])
    m = np.zeros(ori.shape[:2], bool)
    for (x0, y0, x1, y1, _g) in S[b]["falhadas_lista"]:
        m[int(y0 * f):int(y1 * f), int(x0 * f):int(x1 * f)] = True
    olhar = onde_olhar(ori, [(m, VERMELHO, 0.35)])
    pagina_em_cima("p-camoes-027", b, cx,
                   [(ori, "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"]),
                    (olhar, "Onde olhar: linhas mais falhadas")],
                   ["Camões 27, a nota de rodapé (letra miúda e clara). As letras perdem os traços finos nos dois jeitos.",
                    "Em vermelho (cópia do original), as linhas em que o preto e branco guardou menos da tinta clara: são elas",
                    "que mandam a página pela regra ajustada. No texto de cima a falha é a mesma, um pouco menor (ver o cartão do erro 4)."])


def f_camoes066():
    b = "camoes_p066__inteira"
    cx = (0.0, 0.0, 1.0, 1.0)
    pagina_em_cima("p-camoes-066", b, cx,
                   [(ler(b, "original"), "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"])],
                   ["Camões 66, página inteira. O texto sai legível; o que destoa são as linhas pretas na beirada (direita, alto e",
                    "cantos de baixo) e o borrão no canto de baixo à esquerda. Essas linhas aparecem nas 6 páginas do Camões."],
                   alto_baixo=900, ampliar=1.0)


def f_egenloff012():
    b = "egenloff_p012__inteira"
    pagina_em_cima("p-egenloff-012", b, (0.0, 0.0, 1.0, 1.0),
                   [(ler(b, "original"), "Original"), (ler(b, "a"), NOMES["a"])],
                   ["Egenloff 12: o verso em branco de uma prancha (só o carimbo da biblioteca e a moldura do scanner).",
                    "Pela regra ajustada ela vai, com o motivo 'página sem conteúdo', para o Kaique trocar por página branca."],
                   alto_baixo=900, ampliar=1.0)


def f_egenloff047():
    b = "egenloff_p047__inteira"
    cxs = (0.25, 0.15, 0.6, 0.45)
    ori = ler(b, "original")
    forma = ori.shape[:2]
    olhar = onde_olhar(ori, [(apagado(b, forma), VERMELHO, 0.6)])
    pagina_em_cima("p-egenloff-047", b, cxs,
                   [(ori, "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"]),
                    (olhar, "Onde olhar: em vermelho, o que o jeito de fábrica apagou")],
                   ["Egenloff 47 (programa de hoje). Em cima, a página inteira como sai no jeito de fábrica: a moldura preta do scanner",
                    "e a tarja da biblioteca ficam. Embaixo, o ornamento ampliado: o jeito de fábrica apaga só pontinhos."],
                   extras_em_cima=[(ler(b, "a"), "Como sai, inteira (jeito de fábrica)")])


def f_rariora008():
    b = "rariora_p008__inteira"
    ori = ler(b, "original")
    pagina_em_cima("p-rariora-008", b, (0.0, 0.0, 1.0, 1.0),
                   [(ori, "Original"), (ler(b, "a"), NOMES["a"]), (ler(b, "pb"), NOMES["pb"])],
                   ["Rariora 8: só a mancha do verso (a folha de rosto vista por trás, ao contrário) e um selo escuro.",
                    "O programa achou a página inteira como 'gravura' e ela sai como o original. A regra ajustada a reconhece como 'sem conteúdo'."],
                   alto_baixo=800, ampliar=1.0)


def f_antiphonal006():
    b = "antiphonal1547_p006__inteira"
    cx = (0.08, 0.30, 0.95, 0.50)
    ori = ler(b, "original")
    forma = ori.shape[:2]
    z = np.load(pasta_de(b) / f"{b}.npz")
    cinza = cv2.resize(z["cinza"], (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    olhar = onde_olhar(ori, [(apagado(b, forma), VERMELHO, 0.7)])
    pagina_em_cima("p-antiphonal1547-006", b, cx,
                   [(ori, "Original"), (cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR), "Como o programa vê (cinza)"),
                    (ler(b, "a"), NOMES["a"]), (ler(b, "t"), "Um clique: 'Guardar tudo'")],
                   ["Antiphonal 6. O programa decide no cinza: o vermelho vira um cinza CLARO, mais claro que as letras pretas.",
                    "O jeito de fábrica só guarda, fora das linhas de texto, o que é tão escuro quanto as letras (ou está colado nelas).",
                    "Os pedaços de pauta vermelha soltos entre as notas não são: vão para o branco. Em cima, em vermelho, o que foi apagado."],
                   extras_em_cima=[(olhar, "Onde olhar: em vermelho, o que o jeito de fábrica apagou")])


def f_gravura():
    """O delineado: o contorno tracejado de cada area achada como gravura, numa
    COPIA do original, com um numero; laranja = area suspeita (contraste dentro
    dela menor que 60 niveis de cinza entre o claro e o escuro - remendo, mancha
    do verso - ou tiras finas na beirada), verde = parece gravura."""
    grupos = [("gravura-delineado-1", ["marial_p454__inteira", "camoes_p104__inteira", "antiphon_p260__inteira",
                                       "rariora_p008__inteira"]),
              ("gravura-delineado-2", ["pesel_p021__inteira", "graduale_p269__inteira", "rariora_p155__inteira",
                                       "opusmajus_p020__inteira"])]
    nomes = {"marial_p454__inteira": "Marial 454", "camoes_p104__inteira": "Camões 104",
             "antiphon_p260__inteira": "Antiphon 260", "rariora_p008__inteira": "Rariora 8",
             "pesel_p021__inteira": "Pesel 21", "graduale_p269__inteira": "Graduale 269",
             "rariora_p155__inteira": "Rariora 155", "opusmajus_p020__inteira": "Opus Majus 20"}
    for arq, bases in grupos:
        w = D.largura_de(len(bases))
        cima, baixo = [], []
        for b in bases:
            ori = ler(b, "original")
            forma = ori.shape[:2]
            z = np.load(pasta_de(b) / f"{b}.npz")
            cinza = cv2.resize(z["cinza"], (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
            m = mascara(b, "imagem", forma)
            n, rot, st, _c = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
            x = (ori.astype(np.float32) * 0.75 + 255 * 0.25).astype(np.uint8)
            k = 0
            area_pag = forma[0] * forma[1]
            beir = int(0.01 * min(forma))
            for i in range(1, n):
                if st[i, cv2.CC_STAT_AREA] < 0.004 * area_pag:
                    continue
                k += 1
                xx, yy, ww, hh = st[i, :4]
                zona = rot == i
                g = cinza[zona]
                contraste = float(np.percentile(g, 95) - np.percentile(g, 5))
                toca = xx <= beir or yy <= beir or xx + ww >= forma[1] - beir or yy + hh >= forma[0] - beir
                cheia = st[i, cv2.CC_STAT_AREA] / max(1, ww * hh)
                # suspeita: so mancha (pouca diferenca entre claro e escuro dentro
                # dela: remendo, mancha do verso) ou tiras finas na beirada
                suspeita = contraste < 60 or (toca and cheia < 0.3)
                cor = LARANJA if suspeita else VERDE
                x = D.contorno(x, zona, cor, espessura=max(6, forma[1] // 250))
                x = D.rotulo(x, str(k), (int(xx + ww * 0.05) + 10, int(yy + hh * 0.05) + 10),
                             cor_rgb=cor, tamanho=max(60, forma[1] // 14))
            cima.append(D.quadro(x, f"{nomes[b]}: como ficaria", w, 760, 1.0))
            baixo.append(D.quadro(ler(b, "a"), "como sai hoje", w, 420, 1.0))
        D.montar([cima, baixo],
                 ["Em cima, uma COPIA do original com o contorno tracejado em volta de cada área que o programa achou como gravura.",
                  "Laranja = área suspeita (só mancha, sem desenho dentro; ou tiras finas na beirada); verde = parece gravura de verdade.",
                  "Clicando no número, o Kaique escolheria: manter, apagar (deixar branco) ou tratar como texto. Embaixo, como sai hoje."],
                 DESTINO / f"{arq}.jpg")


def f_faixa():
    pids = [("egenloff_p003", "Egenloff 3"), ("matematica_p032", "Matemática 32"), ("camoes_p066", "Camões 66")]
    w = D.largura_de(3)
    cima, baixo = [], []
    for pid, nome in pids:
        im = cv2.imread(str(comum.TRABALHO / "faixa" / f"{pid}.png"))
        d = json.loads((comum.TRABALHO / "faixa" / f"{pid}.json").read_text(encoding="utf-8"))
        a, l = im.shape[:2]
        x = (im.astype(np.float32) * 0.8 + 255 * 0.2).astype(np.uint8)
        for cx, cor, esp in ((d["nosso"], LARANJA, max(5, l // 120)), (d["scantailor"], AZUL, max(3, l // 220))):
            if cx:
                x0, y0, x1, y1 = cx
                cv2.rectangle(x, (int(x0 * l), int(y0 * a)), (int(x1 * l) - 1, int(y1 * a) - 1),
                              tuple(int(c) for c in cor[::-1]), esp)
        cima.append(D.quadro(x, f"{nome}: onde cada um corta", w, 760, 1.0))
        base = f"{pid}__inteira"
        baixo.append(D.quadro(ler(base, "a"), f"{nome}: como sai hoje", w, 640, 1.0))
    D.montar([cima, baixo],
             ["Em cima, a folha como veio do scanner (cópia). Laranja = o corte de bordas do NOSSO programa (já ligado de fábrica);",
              "azul = a 'caixa da página' do ScanTailor (item 2.13; ainda não está no programa). Egenloff e Camões: nenhum dos dois",
              "tira a moldura escura. Matemática: o nosso tira só o lado direito; o do ScanTailor tira também a faixa de baixo.",
              "Embaixo, como a página sai hoje (com o nosso corte)."],
             DESTINO / "faixa-cortes.jpg")


def f_aviso_todos():
    """Desenho da proposta (nao e a tela real): o painel 'Para revisar' na aba
    'Por motivo' (decidida na rodada 10 do layout), com o botao por motivo."""
    W, H = 1800, 760
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f, fb = D.fonte(28), D.fonte(28, True)

    def painel(x0, titulo_extra, botoes):
        d.rectangle([x0, 20, x0 + 820, 640], outline=(160, 160, 160), width=3)
        d.rectangle([x0, 20, x0 + 820, 80], fill=(255, 236, 210))
        d.text((x0 + 16, 34), "Para revisar        12", font=fb, fill=(40, 40, 40))
        d.text((x0 + 16, 96), "Por página  |  Por motivo", font=f, fill=(60, 60, 60))
        d.line([x0 + 190, 132, x0 + 360, 132], fill=(230, 120, 0), width=4)
        y = 160
        for nome, n, bot in botoes:
            if nome:
                d.text((x0 + 20, y), f"{nome}   ({n})", font=f, fill=(30, 30, 30))
            else:
                y -= 50
            if bot:
                d.rounded_rectangle([x0 + 40, y + 44, x0 + 520, y + 94], 10, outline=(40, 110, 230), width=3,
                                    fill=(225, 236, 255))
                d.text((x0 + 56, y + 54), bot, font=D.fonte(25), fill=(30, 60, 150))
                y += 120
            else:
                y += 70
        d.text((x0 + 16, 660), titulo_extra, font=D.fonte(26, True), fill=(20, 20, 20))

    painel(20, "A: um botão por motivo", [("Some algo no 'Só o texto achado'", 9, "está bom assim: todas as 9"),
                                         ("Desenho apagado", 2, "está bom assim: todas as 2"),
                                         ("Página sem conteúdo", 1, None)])
    painel(960, "B: um botão para tudo", [("Some algo no 'Só o texto achado'", 9, None),
                                          ("Desenho apagado", 2, None), ("Página sem conteúdo", 1, None),
                                          ("", "", "está bom assim: todas as 12")])
    d.text((20, 710), "DESENHO DA PROPOSTA (não é a tela de verdade). O botão só marca como 'visto'; nada é mudado na página.",
           font=D.fonte(25), fill=(80, 80, 80))
    destino = DESTINO / "aviso-todos.jpg"
    im.save(destino, quality=90)
    print(destino.name, im.size)


TODAS = {"resumo-regra4": f_resumo, "c1-desenho-antiphonal046": f_desenho, "c4-texto-camoes027": f_texto_camoes027,
         "c5-sem-conteudo": f_sem_conteudo, "p-rariora-169": f_rariora169, "p-camoes-104": f_camoes104,
         "p-camoes-027": f_camoes027, "p-camoes-066": f_camoes066, "p-egenloff-003": f_egenloff003,
         "p-egenloff-012": f_egenloff012, "p-egenloff-047": f_egenloff047, "p-rariora-008": f_rariora008,
         "p-antiphonal1547-006": f_antiphonal006, "gravura-delineado": f_gravura, "faixa-cortes": f_faixa,
         "aviso-todos": f_aviso_todos}


def main() -> None:
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else list(TODAS)
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome in so:
        TODAS[nome]()


if __name__ == "__main__":
    main()
