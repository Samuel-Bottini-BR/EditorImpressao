"""Passo 2: as imagens das seis perguntas G7 a G10 (12/10/2026).

Le dados/caixas.json (passo 1) e as paginas, e grava img/g7g10/*.jpg. Cada funcao
`pergunta_...` faz as imagens de uma pergunta; os nomes dos arquivos sao os que o
escolhas-g7-g10.json usa (montar_json.py).

O QUE E DE VERDADE E O QUE E SIMULACAO (esta escrito tambem nas legendas):
  - "corte de hoje": core.recortar.detectar_bordas, o corte do programa (de verdade);
  - caixas do ScanTailor: codigo original v1.2.1, pela funcao do programa
    (core.caixas_scantailor.achar_na_pagina) com o DPI que o programa diz (passo 1b,
    13/10/2026; em 12/10 eram do caixas.exe com o DPI que o PDF diz) (de verdade);
  - "so o preto" (pergunta da borda preta) e "alargar ate a moldura" (pergunta do
    seguir a moldura): contas simples MINHAS, so para mostrar como ficaria;
  - margens, alinhamento e "tamanho da maior": as contas do ScanTailor
    (page_layout/Utils.cpp) refeitas aqui em Python, com as caixas de verdade;
  - folhas impressas e guias: desenhos em escala, nao a tela do programa.

Nada aqui muda o programa nem as paginas. Uso: python passo2_imagens.py [g7 g8 ...]
"""
from __future__ import annotations

import json
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

import comum
from comum import AZUL, CINZA, LARANJA, ROSA, VERDE, VERMELHO, com_borda, com_titulo, fonte, gravar, lado_a_lado

D = json.loads((comum.DADOS / "caixas.json").read_text(encoding="utf-8"))
FUNDO = (232, 232, 232)
COR_HOJE = (150, 75, 10)
COR_ST = (20, 80, 170)
COR_OPCAO = (15, 110, 55)
COR_NEUTRA = (60, 64, 72)


# ----------------------------------------------------------------------------
# ajudantes
# ----------------------------------------------------------------------------

def pagina(nome: str) -> tuple[Image.Image, float]:
    d = D[nome]
    return comum.para_pil(cv2.imread(d["png"], cv2.IMREAD_COLOR)), float(d["dpi"])


def nosso(nome: str) -> list[float]:
    return D[nome]["nosso"]["caixa"]


def st(nome: str, chave: str = "conteudo_na_pagina") -> list[float]:
    """Uma caixa do ScanTailor. A do conteudo e cortada pela caixa da pagina, como o
    ScanTailor faz depois de achar as duas (select_content/Task.cpp: contentRect &= pageRect)."""
    caixa = D[nome]["scantailor"][chave]
    if chave == "conteudo_na_pagina":
        p = D[nome]["scantailor"]["pagina"]
        caixa = [max(caixa[0], p[0]), max(caixa[1], p[1]), min(caixa[2], p[2]), min(caixa[3], p[3])]
    return caixa


def filtrada(nome: str, filtro: str = "magico_pro") -> Image.Image:
    """A pagina inteira depois do filtro do programa (guardada em saida_teste, para nao refazer).
    Serve para as folhas com margem branca: o papel sai branco e a margem nao destoa."""
    pasta = comum.RASCUNHO / "filtradas"
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"{nome}-{filtro}.png"
    if arquivo.exists():
        return Image.open(arquivo).convert("RGB")
    from core.filtros import aplicar_filtro

    bgr = cv2.imread(D[nome]["png"], cv2.IMREAD_COLOR)
    saida, _mono = aplicar_filtro(bgr, filtro)
    if saida.ndim == 2:
        saida = cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(str(arquivo), saida)
    print("filtrou", nome, filtro, flush=True)
    return comum.para_pil(saida)


def cortar(img: Image.Image, caixa) -> Image.Image:
    x0, y0, x1, y1 = (int(round(v)) for v in caixa)
    return img.crop((max(0, x0), max(0, y0), min(img.width, x1), min(img.height, y1)))


def redimensionar(img: Image.Image, largura: int | None = None, altura: int | None = None) -> Image.Image:
    if largura is None:
        largura = round(img.width * altura / img.height)
    if altura is None:
        altura = round(img.height * largura / img.width)
    return img.resize((max(1, largura), max(1, altura)), Image.LANCZOS)


def com_corte(img: Image.Image, caixa, cor, espessura: int | None = None) -> Image.Image:
    """A folha com o que sai escurecido e o corte desenhado."""
    q = comum.escurecer_fora(img, caixa)
    comum.retangulo(q, caixa, cor, espessura or max(4, img.width // 260))
    return q


def regiao(img: Image.Image, fx0: float, fy0: float, fx1: float, fy1: float) -> Image.Image:
    return img.crop((int(img.width * fx0), int(img.height * fy0), int(img.width * fx1), int(img.height * fy1)))


def uniao(a, b) -> list[float]:
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def rotulo(img: Image.Image, xy, texto: str, cor=(0, 0, 0), tamanho: int = 26, fundo=(255, 255, 255)) -> None:
    d = ImageDraw.Draw(img)
    f = fonte(tamanho, negrito=True)
    x, y = xy
    caixa = d.textbbox((x, y), texto, font=f)
    d.rectangle([caixa[0] - 6, caixa[1] - 4, caixa[2] + 6, caixa[3] + 4], fill=fundo)
    d.text((x, y), texto, font=f, fill=cor)


def painel(quadros: list[tuple[str, Image.Image, tuple]], altura: int = 900) -> Image.Image:
    """Quadros (titulo, imagem, cor da faixa) lado a lado, com a mesma altura de imagem."""
    prontos = [com_titulo(redimensionar(im, altura=altura), t, cor, tamanho=28) for t, im, cor in quadros]
    return lado_a_lado(prontos, fundo=FUNDO)


# ----------------------------------------------------------------------------
# G7: a borda preta (item 2.13)
# ----------------------------------------------------------------------------

def so_o_preto(img: Image.Image) -> list[float]:
    """CONTA MINHA (simulacao): anda de cada beirada para dentro enquanto a linha for
    quase toda escura (fundo do scanner), e para na primeira linha clara. Olha so o
    meio de cada lado. Nao e do ScanTailor nem do programa."""
    g = np.asarray(img.convert("L"), np.float32)
    alt, larg = g.shape
    papel = float(np.percentile(g[alt // 4: 3 * alt // 4, larg // 4: 3 * larg // 4], 60))
    escuro = g < papel * 0.45
    meio_x = slice(int(larg * 0.25), int(larg * 0.75))
    meio_y = slice(int(alt * 0.25), int(alt * 0.75))

    def anda(perfil: np.ndarray) -> int:
        i = 0
        limite = int(len(perfil) * 0.3)
        while i < limite and perfil[i:i + 4].mean() > 0.5:
            i += 1
        return i

    x0 = anda(escuro[meio_y, :].mean(axis=0))
    x1 = larg - anda(escuro[meio_y, ::-1].mean(axis=0))
    y0 = anda(escuro[:, meio_x].mean(axis=1))
    y1 = alt - anda(escuro[::-1, meio_x].mean(axis=1))
    return [float(x0), float(y0), float(x1), float(y1)]


CANTO = (0.60, 0.52, 1.0, 1.0)     # o canto de baixo a direita do Siebmacher (onde esta o preto)


def trio(nome: str, caixa, cor, titulo_do_corte: str, altura: int = 760) -> Image.Image:
    """[a folha com o corte] [como fica] [o canto ampliado]."""
    img, _ = pagina(nome)
    marcada = com_corte(img, caixa, cor)
    resultado = cortar(img, caixa)
    canto = regiao(marcada, *CANTO)
    return painel([
        (titulo_do_corte, marcada, COR_NEUTRA),
        ("Como fica a página", com_borda(resultado), COR_NEUTRA),
        ("O canto de baixo, ampliado", canto, COR_NEUTRA),
    ], altura)


def opcao_do_corte(nome: str, caixa, cor, prefixo: str) -> None:
    img, _ = pagina(nome)
    marcada = com_corte(img, caixa, cor)
    canto = regiao(marcada, *CANTO)
    gravar(redimensionar(canto, largura=1300), f"{prefixo}-canto")
    antes = com_titulo(redimensionar(img, altura=820), "Antes: a folha como veio", COR_NEUTRA, 28)
    onde = com_titulo(redimensionar(marcada, altura=820), "O corte sugerido (o escuro sai)", COR_OPCAO, 28)
    res = cortar(img, caixa)
    depois = com_titulo(redimensionar(com_borda(res), altura=820), "Depois", COR_OPCAO, 28)
    gravar(lado_a_lado([antes, onde, depois], fundo=FUNDO), f"{prefixo}-inteira", 2000)


def pergunta_g7() -> None:
    principal, outra = "siebmacher_p007", "siebmacher_p009"
    for nome, curto in ((principal, "siebmacher7"), (outra, "siebmacher9")):
        gravar(trio(nome, nosso(nome), LARANJA, "Hoje: o corte do programa (laranja)"), f"g7-hoje-{curto}", 2000)
    gravar(trio(principal, st(principal, "pagina"), AZUL, "A busca de página do ScanTailor (azul)"),
           "g7-scantailor-siebmacher7", 2000)
    # a opcao "ajustar os cantos" do ScanTailor: anda em diagonal enquanto o canto esta no preto
    gravar(trio(principal, st(principal, "pagina_cantos"), AZUL, "ScanTailor com \"ajustar os cantos\" (azul)"),
           "g7-scantailor-cantos-siebmacher7", 2000)
    if "ljs47_p046" in D:
        img, _ = pagina("ljs47_p046")
        cx = st("ljs47_p046", "pagina")
        gravar(painel([("Livro com preto em volta toda", img, COR_NEUTRA),
                       ("A busca de página do ScanTailor (azul)", com_corte(img, cx, AZUL), COR_ST),
                       ("Como fica", com_borda(cortar(img, cx)), COR_ST)], 760), "g7-scantailor-borda-larga", 2000)
    pretos = {n: so_o_preto(pagina(n)[0]) for n in (principal, outra)}
    print("so o preto:", {n: [round(v) for v in c] for n, c in pretos.items()}, flush=True)
    (comum.DADOS / "so-o-preto.json").write_text(json.dumps(pretos, indent=1), encoding="utf-8")
    opcao_do_corte(principal, pretos[principal], VERDE, "g7-a-so-o-preto")
    opcao_do_corte(principal, st(principal), VERDE, "g7-b-ate-a-moldura")
    # as duas opcoes na outra pagina (aqui a caixa do ScanTailor para nos pontinhos de sujeira)
    img, _ = pagina(outra)
    gravar(painel([("Tira só o preto", com_corte(img, pretos[outra], VERDE), COR_OPCAO),
                   ("Como fica", com_borda(cortar(img, pretos[outra])), COR_OPCAO),
                   ("Vai até a moldura", com_corte(img, st(outra), VERDE), COR_OPCAO),
                   ("Como fica", com_borda(cortar(img, st(outra))), COR_OPCAO)], 640), "g7-as-duas-na-outra-pagina", 2200)


# ----------------------------------------------------------------------------
# G8: seguir a moldura (item 2.5)
# ----------------------------------------------------------------------------

def alargar_ate_a_tinta(nome: str, caixa) -> list[float]:
    """SIMULACAO (conta minha por cima de contas de verdade): alarga a caixa do
    ScanTailor usando as pecas de tinta que o corte do PROGRAMA ja conhece
    (core.recortar: Recorte.pecas; nao entram cisco, risco fino comprido nem o que
    encosta na beirada da folha). Entram: (a) a peca que a caixa atravessa (a barra
    de uma moldura); (b) a peca do tamanho de uma letra ou maior que esta logo acima
    ou abaixo da caixa, na mesma coluna (o numero da pagina no pe, o reclamo): tem de
    ter 1 mm ou mais nos dois sentidos e ser escura como tinta (metade do tom do papel),
    para mancha clara e risquinho nao puxarem a caixa.
    Depois da 1 mm de folga, como o corte de hoje."""
    from core.recortar import detectar_bordas

    bgr = cv2.imread(D[nome]["png"], cv2.IMREAD_COLOR)
    cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    papel = float(np.percentile(cinza, 60))
    dpi = float(D[nome]["dpi"])
    alt, larg = bgr.shape[:2]
    pecas = detectar_bordas(bgr, dpi=dpi).pecas
    mm = dpi / 25.4
    x0, y0, x1, y1 = caixa
    nova = list(caixa)
    quantas = 0
    for p in (np.asarray(pecas) if pecas is not None else []):
        if p[4] > 0:
            continue                                   # risco comprido e fino
        px0, py0, px1, py1 = p[0] * larg, p[1] * alt, p[2] * larg, p[3] * alt
        if px0 >= x0 and py0 >= y0 and px1 <= x1 and py1 <= y1:
            continue                                   # ja esta inteira dentro
        toca = not (px1 < x0 or px0 > x1 or py1 < y0 or py0 > y1)
        na_coluna = x0 <= (px0 + px1) / 2 <= x1 and min(px1 - px0, py1 - py0) >= 1.0 * mm
        if na_coluna and not toca:
            pedaco = cinza[int(py0):int(py1) + 1, int(px0):int(px1) + 1]
            na_coluna = float(np.percentile(pedaco, 5)) < 0.5 * papel
        if not (toca or na_coluna):
            continue
        nova = uniao(nova, [px0, py0, px1, py1])
        quantas += 1
    print(f"{nome}: {quantas} pecas puxaram a caixa", flush=True)
    return [max(0, nova[0] - mm), max(0, nova[1] - mm), min(larg, nova[2] + mm), min(alt, nova[3] + mm)]


def opcao_da_moldura(nome: str, caixa, cor, prefixo: str, zona: tuple, titulo: str) -> None:
    img, _ = pagina(nome)
    res = cortar(img, caixa)
    marcada = com_corte(img, caixa, cor)
    gravar(redimensionar(regiao(marcada, *zona), largura=1300), f"{prefixo}-canto")
    antes = com_titulo(redimensionar(img, altura=900), "Antes: a folha como veio", COR_NEUTRA, 28)
    onde = com_titulo(redimensionar(marcada, altura=900), titulo, COR_OPCAO, 28)
    depois = com_titulo(redimensionar(com_borda(res), altura=900), "Depois", COR_OPCAO, 28)
    gravar(lado_a_lado([antes, onde, depois], fundo=FUNDO), f"{prefixo}-inteira", 2000)


def pergunta_g8_moldura() -> None:
    nome = "horas_p014"
    do_st = st(nome)
    alargada = alargar_ate_a_tinta(nome, do_st)
    registro = {nome: {"scantailor": do_st, "alargada": alargada, "nosso": nosso(nome)}}
    print("horas 14: scantailor", [round(v) for v in do_st], "alargada", [round(v) for v in alargada],
          "nosso", [round(v) for v in nosso(nome)], flush=True)
    zona = (0.10, 0.05, 0.62, 0.36)                    # o canto de cima a esquerda da moldura
    opcao_da_moldura(nome, do_st, VERMELHO, "g8-a-avisa", zona, "O corte do ScanTailor (o escuro sai)")
    opcao_da_moldura(nome, alargada, VERDE, "g8-b-alarga", zona, "O corte alargado (o escuro sai)")
    opcao_da_moldura(nome, nosso(nome), LARANJA, "g8-c-volta", zona, "O corte comum do programa")
    # exemplo: uma pagina em que o corte do ScanTailor acerta
    outra, _ = pagina("horas_p026")
    gravar(painel([("ScanTailor (azul): abraça a moldura", com_corte(outra, st("horas_p026"), AZUL), COR_ST),
                   ("Como fica", com_borda(cortar(outra, st("horas_p026"))), COR_ST),
                   ("O corte comum do programa (laranja)", com_corte(outra, nosso("horas_p026"), LARANJA), COR_HOJE)],
                  820), "g8-exemplo-acerta", 2000)
    # exemplo: pagina que termina no meio; o numero da pagina, sozinho no pe, fica de fora
    num = "opusmajus_p137"
    if num in D:
        img, _ = pagina(num)
        do_st2 = st(num)
        alargada2 = alargar_ate_a_tinta(num, do_st2)
        registro[num] = {"scantailor": do_st2, "alargada": alargada2, "nosso": nosso(num)}
        pe = (0.20, 0.78, 0.80, 0.95)
        gravar(painel([("ScanTailor: o número fica fora", com_corte(img, do_st2, VERMELHO), COR_ST),
                       ("O número que ficou de fora", regiao(img, *pe), COR_ST),
                       ("Alargado: o número entra", com_corte(img, alargada2, VERDE), COR_OPCAO),
                       ("Como fica, alargado", com_borda(cortar(img, alargada2)), COR_OPCAO)],
                      820), "g8-exemplo-numero-da-pagina", 2200)
    (comum.DADOS / "moldura.json").write_text(json.dumps(registro, indent=1), encoding="utf-8")


# ----------------------------------------------------------------------------
# margens do ScanTailor, refeitas em Python (page_layout/Utils.cpp)
# ----------------------------------------------------------------------------

MARGENS_MM = (10.0, 5.0, 10.0, 5.0)        # esquerda, cima, direita, baixo: as de fabrica do ScanTailor


def tamanho_com_margens(caixa, dpi: float, margens=MARGENS_MM) -> tuple[float, float]:
    """Largura e altura (em pontos da pagina) do conteudo mais as margens fixas."""
    mm = dpi / 25.4
    return (caixa[2] - caixa[0] + (margens[0] + margens[2]) * mm, caixa[3] - caixa[1] + (margens[1] + margens[3]) * mm)


def folha_com_margens(conteudo: Image.Image, caixa, tamanho_da_folha, dpi: float, alvo: tuple[float, float],
                      vertical: str = "meio", horizontal: str = "meio", margens=MARGENS_MM) -> Image.Image:
    """A folha branca do tamanho `alvo` com o conteudo (recorte ja filtrado) dentro.

    Igual ao ScanTailor: margens fixas em volta do conteudo; o que falta para chegar
    ao tamanho `alvo` (o da maior pagina) vai para cima/baixo e esquerda/direita
    conforme o alinhamento. "original" = a mesma posicao relativa que o conteudo
    tinha na folha escaneada (calcSoftMarginsMM, ramo "default")."""
    mm = dpi / 25.4
    w, h = tamanho_com_margens(caixa, dpi, margens)
    sobra_x, sobra_y = max(0.0, alvo[0] - w), max(0.0, alvo[1] - h)
    larg_folha, alt_folha = tamanho_da_folha
    cx = (caixa[0] + caixa[2]) / 2 / larg_folha
    cy = (caixa[1] + caixa[3]) / 2 / alt_folha
    if horizontal == "original":
        esq = min(max(cx * alvo[0] - w / 2, 0.0), sobra_x)
    else:
        esq = sobra_x / 2
    if vertical == "original":
        cima = min(max(cy * alvo[1] - h / 2, 0.0), sobra_y)
    elif vertical == "cima":
        cima = 0.0
    else:
        cima = sobra_y / 2
    folha = Image.new("RGB", (int(round(max(alvo[0], w))), int(round(max(alvo[1], h)))), (255, 255, 255))
    folha.paste(conteudo, (int(round(esq + margens[0] * mm)), int(round(cima + margens[1] * mm))))
    return folha


def conteudo_filtrado(nome: str, caixa) -> Image.Image:
    return cortar(filtrada(nome), caixa)


# ----------------------------------------------------------------------------
# G9: uma folha muito maior que as outras (item 2.4)
# ----------------------------------------------------------------------------

LIVRO_OPUS = ["opusmajus_p003", "opusmajus_p011", "opusmajus_p020", "opusmajus_p165"]
DOBRAVEL = "opusmajus_p256"

CAIXAS_BOAS: dict[str, list[float]] = {}


def caixa_boa(nome: str) -> list[float]:
    """A caixa do conteudo usada nas folhas com margem: a do ScanTailor dentro da pagina,
    menos nas duas paginas do Livro de Horas em que ela sai errada (ver preparar_caixas_boas)."""
    return CAIXAS_BOAS.get(nome) or st(nome)


def preparar_caixas_boas() -> None:
    """Nas folhas com margem (tamanho final) a caixa precisa estar certa, senao a
    imagem mostraria o erro do corte e nao o assunto da pergunta. No Livro de Horas:
    pagina cheia = o corte do programa (abraca a iluminura); pagina da tabela pequena =
    a caixa do ScanTailor (que fica por dentro da moldura) alargada ate a moldura.
    Conferidas a olho; gravadas em dados/caixas-boas.json."""
    CAIXAS_BOAS["horas_p047"] = nosso("horas_p047")
    CAIXAS_BOAS["horas_p013"] = alargar_ate_a_tinta("horas_p013", st("horas_p013"))
    (comum.DADOS / "caixas-boas.json").write_text(json.dumps(CAIXAS_BOAS, indent=1), encoding="utf-8")


def maior_do_livro(nomes: list[str]) -> tuple[float, float]:
    tamanhos = [tamanho_com_margens(caixa_boa(n), D[n]["dpi"]) for n in nomes]
    return max(t[0] for t in tamanhos), max(t[1] for t in tamanhos)


def folha_de(nome: str, alvo, vertical="meio", horizontal="meio") -> Image.Image:
    img, dpi = pagina(nome)
    return folha_com_margens(conteudo_filtrado(nome, caixa_boa(nome)), caixa_boa(nome), img.size, dpi, alvo,
                             vertical, horizontal)


def pergunta_g9_maior() -> None:
    normais = LIVRO_OPUS
    alvo_sem = maior_do_livro(normais)
    alvo_com = maior_do_livro(normais + [DOBRAVEL])
    alvo_dobravel = tamanho_com_margens(caixa_boa(DOBRAVEL), D[DOBRAVEL]["dpi"])
    print("opus: maior sem a dobravel", [round(v) for v in alvo_sem], "com", [round(v) for v in alvo_com], flush=True)
    escala = 760 / alvo_com[1]                       # as tres folhas na mesma escala

    def na_escala(folha: Image.Image) -> Image.Image:
        return redimensionar(com_borda(folha, espessura=4), largura=round(folha.width * escala))

    # as duas folhas como vieram, na MESMA escala (as duas sao PNG de 400 DPI)
    a, b = pagina("opusmajus_p011")[0], pagina(DOBRAVEL)[0]
    e = 760 / max(a.height, b.height)
    gravar(lado_a_lado([com_titulo(redimensionar(a, largura=round(a.width * e)), "Página comum (em pé)", COR_NEUTRA, 26),
                        com_titulo(redimensionar(b, largura=round(b.width * e)), "A tabela dobrável (deitada, bem mais larga)",
                                   COR_NEUTRA, 26)], fundo=FUNDO, mesma_altura=False), "g9-maior-as-duas-paginas", 1800)
    for prefixo, alvo, alvo_da_dobravel in (("g9-maior-a-fica-de-fora", alvo_sem, alvo_dobravel),
                                            ("g9-maior-b-entra-na-conta", alvo_com, alvo_com)):
        comum_ = folha_de("opusmajus_p011", alvo)
        gravar(redimensionar(com_borda(comum_, espessura=4), altura=1000), f"{prefixo}-pagina-comum", 1700)
        tres = [na_escala(folha_de("opusmajus_p011", alvo)), na_escala(folha_de("opusmajus_p165", alvo)),
                na_escala(folha_de(DOBRAVEL, alvo_da_dobravel))]
        alt = max(t.height for t in tres)
        tela = Image.new("RGB", (sum(t.width for t in tres) + 40 * 4, alt + 80), FUNDO)
        x = 40
        for t in tres:
            tela.paste(t, (x, 40 + (alt - t.height) // 2))
            x += t.width + 40
        gravar(tela, f"{prefixo}-o-livro", 2000)


# ----------------------------------------------------------------------------
# G10: tamanho final (item 2.6). Desenhos em escala.
# ----------------------------------------------------------------------------

A4 = (21.0, 29.7)
A5 = (14.85, 21.0)
PX_POR_CM = 44          # escala dos desenhos das folhas impressas


def folha_branca(tamanho_cm, px_por_cm: float = PX_POR_CM) -> Image.Image:
    return Image.new("RGB", (round(tamanho_cm[0] * px_por_cm), round(tamanho_cm[1] * px_por_cm)), (255, 255, 255))


def colar_no_meio(folha: Image.Image, conteudo: Image.Image) -> None:
    folha.paste(conteudo, ((folha.width - conteudo.width) // 2, (folha.height - conteudo.height) // 2))


def pagina_impressa(nome: str, tamanho_cm, fator: float, px_por_cm: float = PX_POR_CM) -> Image.Image:
    """A pagina de `tamanho_cm` com o conteudo de `nome` no meio, ampliado ou reduzido
    por `fator` em relacao ao tamanho que o arquivo diz ter."""
    _img, dpi = pagina(nome)
    cx = caixa_boa(nome)
    conteudo = conteudo_filtrado(nome, cx)
    larg_cm = (cx[2] - cx[0]) / dpi * 2.54 * fator
    conteudo = redimensionar(conteudo, largura=round(larg_cm * px_por_cm))
    folha = folha_branca(tamanho_cm, px_por_cm)
    colar_no_meio(folha, conteudo)
    return folha


def cota(img: Image.Image, texto: str, embaixo: bool = True, tamanho: int = 30) -> Image.Image:
    """Um texto curto (medida) em baixo ou em cima de um desenho; quebra em linhas se nao couber."""
    f = fonte(tamanho, negrito=True)
    regua = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    linhas, atual = [], ""
    for palavra in texto.split():
        tentativa = (atual + " " + palavra).strip()
        if regua.textlength(tentativa, font=f) <= img.width - 24 or not atual:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra
    linhas.append(atual)
    faixa = Image.new("RGB", (img.width, int(tamanho * 1.45 * len(linhas) + tamanho * 0.5)), FUNDO)
    d = ImageDraw.Draw(faixa)
    for n, linha in enumerate(linhas):
        w = d.textlength(linha, font=f)
        d.text(((img.width - w) / 2, tamanho * 0.25 + n * tamanho * 1.45), linha, font=f, fill=(30, 30, 30))
    tela = Image.new("RGB", (img.width, img.height + faixa.height), FUNDO)
    if embaixo:
        tela.paste(img, (0, 0)); tela.paste(faixa, (0, img.height))
    else:
        tela.paste(faixa, (0, 0)); tela.paste(img, (0, faixa.height))
    return tela


def tamanho_real_cm(nome: str) -> tuple[float, float]:
    cx, dpi = caixa_boa(nome), D[nome]["dpi"]
    return ((cx[2] - cx[0]) / dpi * 2.54, (cx[3] - cx[1]) / dpi * 2.54)


def pergunta_g10_papel() -> None:
    esq, dir_ = "palatino_p010", "palatino_p009"       # duas paginas do mesmo livro
    # (a) A4 = o papel da impressora: cada pagina do livro e meia folha (A5), no tamanho real
    pa, pb = pagina_impressa(esq, A5, 1.0), pagina_impressa(dir_, A5, 1.0)
    folha_a = Image.new("RGB", (pa.width * 2, pa.height), (255, 255, 255))
    folha_a.paste(pa, (0, 0)); folha_a.paste(pb, (pa.width, 0))
    d = ImageDraw.Draw(folha_a)
    for y in range(0, folha_a.height, 24):
        d.line([pa.width, y, pa.width, y + 12], fill=(150, 150, 150), width=3)        # a dobra
    folha_a = com_borda(folha_a, (40, 40, 40), 5)
    # (b) A4 = a pagina do livro: a folha do caderno e o dobro (A3); numa impressora A4 sai a 71%
    pa2, pb2 = pagina_impressa(esq, A4, 1.0), pagina_impressa(dir_, A4, 1.0)
    folha_b = Image.new("RGB", (pa2.width * 2, pa2.height), (255, 255, 255))
    folha_b.paste(pa2, (0, 0)); folha_b.paste(pb2, (pa2.width, 0))
    d = ImageDraw.Draw(folha_b)
    for y in range(0, folha_b.height, 24):
        d.line([pa2.width, y, pa2.width, y + 12], fill=(150, 150, 150), width=3)
    folha_b = com_borda(folha_b, (40, 40, 40), 5)
    reduzida = redimensionar(folha_b, largura=folha_a.width)     # A3 reduzida para caber no A4: 71%

    # opcao A
    gravar(cota(com_borda(pa, (40, 40, 40), 4), "uma página do livro: 14,8 × 21 cm (meia folha A4)"), "g10-papel-a-pagina", 1300)
    gravar(cota(folha_a, "folha A4 deitada, impressa: duas páginas lado a lado, no tamanho de verdade"),
           "g10-papel-a-folha", 1700)
    # opcao B
    meia = reduzida.crop((0, 0, reduzida.width // 2, reduzida.height))
    gravar(cota(com_borda(meia, (40, 40, 40), 4), "a mesma página depois de reduzida para caber no A4: 71% do tamanho"),
           "g10-papel-b-pagina", 1300)
    tela = Image.new("RGB", (folha_b.width + 80, folha_b.height + 80), FUNDO)
    tela.paste(folha_b, (40, 40))
    d = ImageDraw.Draw(tela)
    comum.retangulo(tela, (40, 40, 40 + folha_a.width, 40 + folha_a.height), ROSA, 8, tracejado=True)
    rotulo(tela, (60, 60), "tracejado rosa: o tamanho do papel A4", ROSA, 34)
    gravar(cota(tela, "duas páginas A4 lado a lado dão uma folha A3 (42 × 29,7 cm): não cabe no papel A4"),
           "g10-papel-b-folha", 1700)


def pergunta_g10_ajustar() -> None:
    cheia, pequena = "horas_p047", "horas_p013"
    tam_cheia, tam_pequena = tamanho_real_cm(cheia), tamanho_real_cm(pequena)
    margem = (2.0, 1.0)                                  # 10 + 10 mm e 5 + 5 mm
    def fator_para_caber(tam):
        return min(A4[0] / (tam[0] + margem[0]), A4[1] / (tam[1] + margem[1]))
    f_livro = min(fator_para_caber(tam_cheia), fator_para_caber(tam_pequena))
    f_pequena = fator_para_caber(tam_pequena)
    print(f"horas: cheia {tam_cheia}, pequena {tam_pequena}; fator do livro {f_livro:.3f}; "
          f"fator so da pequena {f_pequena:.3f}", flush=True)
    (comum.DADOS / "ajustar-horas.json").write_text(json.dumps(
        {"cheia_cm": tam_cheia, "pequena_cm": tam_pequena, "fator_do_livro": f_livro,
         "fator_so_da_pequena": f_pequena}, indent=1), encoding="utf-8")
    folha_cheia = com_borda(pagina_impressa(cheia, A4, f_livro), (40, 40, 40), 4)
    for prefixo, fator, titulo in (("g10-ajustar-a-mesma-medida", f_livro, "A página pequena, na mesma medida"),
                                   ("g10-ajustar-b-cada-uma", f_pequena, "A página pequena, enchendo a folha")):
        folha_pequena = com_borda(pagina_impressa(pequena, A4, fator), (40, 40, 40), 4)
        # o mesmo pedaco de papel (10 x 5 cm, no meio da folha) da pagina pequena nas duas
        # opcoes: mostra o quanto a pagina foi ampliada (as duas paginas tem letras de
        # tamanhos diferentes no proprio livro, por isso a comparacao e da mesma pagina)
        w, h = round(10 * PX_POR_CM), round(5 * PX_POR_CM)
        x, y = (folha_pequena.width - w) // 2, int(folha_pequena.height * 0.42)
        pedaco = folha_pequena.crop((x, y, x + w, y + h))
        gravar(cota(redimensionar(pedaco, largura=1300), "um pedaço de 10 × 5 cm da folha impressa (página pequena)", tamanho=34),
               f"{prefixo}-letra", 1300)
        gravar(lado_a_lado([com_titulo(redimensionar(folha_cheia, altura=900), "A página cheia", COR_NEUTRA, 28),
                            com_titulo(redimensionar(folha_pequena, altura=900), titulo, COR_OPCAO, 28)], fundo=FUNDO),
               f"{prefixo}-folhas", 1700)
    antes = painel([("A página cheia, como veio", pagina(cheia)[0], COR_NEUTRA),
                    ("A página pequena, como veio", pagina(pequena)[0], COR_NEUTRA)], 800)
    gravar(antes, "g10-ajustar-as-duas-paginas", 1500)


# ----------------------------------------------------------------------------
# G8: guias (desenho)
# ----------------------------------------------------------------------------

def pergunta_g8_guias() -> None:
    nomes = ["palatino_p010", "palatino_p057"]
    alvo = maior_do_livro(nomes + ["palatino_p009", "palatino_p007"])
    ciano = (0, 170, 200)
    # (a) guias postas pelo Kaique: as mesmas linhas em todas as paginas; o conteudo gruda nelas
    # a guia vertical fica na margem esquerda e a horizontal na margem de cima; cada pagina
    # e colada encostada nas duas (e o que o "grudar na guia" do ScanTailor faz)
    prontos = []
    for nome in nomes:
        img, dpi = pagina(nome)
        mm = dpi / 25.4
        cx = caixa_boa(nome)
        folha = Image.new("RGB", (int(alvo[0]), int(alvo[1])), (255, 255, 255))
        folha.paste(conteudo_filtrado(nome, cx), (int(MARGENS_MM[0] * mm), int(MARGENS_MM[1] * mm)))
        d = ImageDraw.Draw(folha)
        e = max(5, folha.width // 220)
        d.line([int(MARGENS_MM[0] * mm), 0, int(MARGENS_MM[0] * mm), folha.height], fill=ciano, width=e)
        d.line([0, int(MARGENS_MM[1] * mm), folha.width, int(MARGENS_MM[1] * mm)], fill=ciano, width=e)
        prontos.append(com_borda(folha, (40, 40, 40), 4))
    canto = prontos[0].crop((0, 0, int(prontos[0].width * 0.55), int(prontos[0].height * 0.30)))
    gravar(redimensionar(canto, largura=1300), "g8-guias-a-canto")
    gravar(lado_a_lado([com_titulo(redimensionar(p, altura=900), t, COR_OPCAO, 28) for p, t in
                        zip(prontos, ("Uma página: encostada nas duas linhas", "Outra página: as mesmas linhas"))],
                       fundo=FUNDO), "g8-guias-a-paginas", 1700)
    # (b) so as automaticas de hoje: o meio e as beiradas da folha
    nome = nomes[0]
    folha = folha_de(nome, alvo)
    d = ImageDraw.Draw(folha)
    e = max(5, folha.width // 220)
    d.line([folha.width // 2, 0, folha.width // 2, folha.height], fill=ciano, width=e)
    d.line([0, folha.height // 2, folha.width, folha.height // 2], fill=ciano, width=e)
    folha = com_borda(folha, ciano, e * 2)
    meio = folha.crop((int(folha.width * 0.2), int(folha.height * 0.36), int(folha.width * 0.8), int(folha.height * 0.64)))
    gravar(redimensionar(meio, largura=1300), "g8-guias-b-meio")
    gravar(lado_a_lado([com_titulo(redimensionar(folha, altura=900), "Linhas automáticas: o meio e as beiradas da folha",
                                   COR_HOJE, 28)], fundo=FUNDO), "g8-guias-b-pagina", 1300)


PERGUNTAS = {"g7": pergunta_g7, "g8m": pergunta_g8_moldura, "g8g": pergunta_g8_guias,
             "g9m": pergunta_g9_maior, "g10p": pergunta_g10_papel, "g10a": pergunta_g10_ajustar}

if __name__ == "__main__":
    preparar_caixas_boas()
    for chave in (sys.argv[1:] or list(PERGUNTAS)):
        print("==", chave, flush=True)
        PERGUNTAS[chave]()
