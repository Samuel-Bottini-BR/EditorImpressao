"""Monta as imagens das 6 perguntas (14/11/2026), no modelo do girar (CLAUDE.md §10), a partir do que
fundo_a.py, capa_b.py e girar_c.py gravaram em _cru/. Grava em imagens/ e imagens/legendas.json.

    python montar.py [a2] [a3] [a4] [b1] [b3] [c]      (sem nada: todas)

Faixas: azul = como é hoje; laranja = a outra opção; verde = a sugestão / a proposta. O que olhar fica
circulado em vermelho. O que é desenho (não existe no programa) diz "DESENHO" ou "PROPOSTA" no título.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pecas_imagem as P  # noqa: E402

R = AQUI.parent
CRU = R / "_cru"
SAIDA = R / "imagens"
LEG_ARQ = SAIDA / "legendas.json"
LEG: dict = json.loads(LEG_ARQ.read_text(encoding="utf-8")) if LEG_ARQ.exists() else {}
FUNDO_MENU = (69, 69, 69)


def guardar(img: Image.Image, nome: str, legenda: str) -> None:
    P.salvar(img, SAIDA / nome)
    LEG[nome] = legenda


def tracejar(img: Image.Image, caixa_frac, cor=P.VERMELHO, largura: int = 4, passo: int = 14) -> Image.Image:
    """Um retângulo tracejado (a borda do pedaço marcado), em frações da imagem."""
    saida = img.copy()
    d = ImageDraw.Draw(saida)
    x0, y0, x1, y1 = (round(caixa_frac[0] * img.width), round(caixa_frac[1] * img.height),
                      round(caixa_frac[2] * img.width), round(caixa_frac[3] * img.height))
    for a, b, fixo, horizontal in ((x0, x1, y0, True), (x0, x1, y1, True), (y0, y1, x0, False),
                                   (y0, y1, x1, False)):
        for t in range(a, b, passo * 2):
            fim = min(t + passo, b)
            if horizontal:
                d.line([(t, fixo), (fim, fixo)], fill=cor, width=largura)
            else:
                d.line([(fixo, t), (fixo, fim)], fill=cor, width=largura)
    return saida


def carimbo(img: Image.Image, texto: str = "PROPOSTA") -> Image.Image:
    """Um carimbo grande e inclinado por cima do desenho, para não ser confundido com o programa."""
    saida = img.convert("RGBA")
    f = P.fonte(max(40, img.width // 9), True)
    camada = Image.new("RGBA", saida.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    largura = f.getlength(texto)
    d.text(((saida.width - largura) / 2, saida.height * 0.40), texto, font=f, fill=(25, 130, 60, 110))
    camada = camada.rotate(18, center=(saida.width / 2, saida.height / 2))
    return Image.alpha_composite(saida, camada).convert("RGB")


# --------------------------------------------------------------------------- A3
def a3() -> None:
    hoje = P.abrir(CRU / "fundo" / "a3-janela-original.png")
    antes = P.abrir(CRU / "fundo" / "a3-janela-tirar-o-fundo.png")
    area = (44, 38, 1256, 852)                  # a página, a faixa azul e a faixa de baixo
    faixa = (44, 814, 1030, 852)                # a faixa de baixo (sem o botão "está certo")
    tela_hoje = hoje.crop(area)
    desenho = hoje.copy()
    desenho.paste(antes.crop(faixa), faixa[:2])  # a frase que o programa já mostra na página em "Tirar o fundo"
    tela_desenho = desenho.crop(area)
    alvo = ((faixa[0] - area[0]) / (area[2] - area[0]), (faixa[1] - area[1]) / (area[3] - area[1]),
            0.50, (faixa[3] - area[1]) / (area[3] - area[1]))

    def bloco(rotulo, cor, legenda, tela):
        t = P.circular(P.caber(tela, 1100, 740), alvo, folga=0.08, espessura=5)
        x0, y0 = faixa[0] - area[0], faixa[1] - area[1]
        perto = tela.crop((x0, y0, x0 + 560, y0 + (faixa[3] - faixa[1])))
        perto = P.caber(perto, 1400, 200)
        perto = P.circular(perto, (0.0, 0.0, 1.0, 1.0), folga=0.03, espessura=5)
        return P.empilhar([P.cabeca(rotulo, cor, legenda), P.com_titulo(t, "a tela"),
                           P.com_titulo(perto, "a faixa de baixo, ampliada", vermelho=True)], espaco=6)

    partes = [
        P.cabeca("A frase da faixa — resumo", P.CINZA,
                 "Siebmacher (cópia), página 4. O Kaique respondeu \"Sim, tirar o fundo\" e depois clicou na "
                 "figurinha \"Original\" do painel Filtro da página. Olhe a frase da faixa de baixo, circulada."),
        bloco("HOJE", P.AZUL,
              "A página continua sem o fundo (papel branco, como vai sair no PDF), mas a faixa diz \"Esta "
              "página vai sair em Original.\"", tela_hoje),
        bloco("SIM — DESENHO (ainda não existe)", P.VERDE,
              "A mesma página. A faixa diz a frase do fundo, a mesma que o programa já mostra numa página em "
              "\"Tirar o fundo\": \"Vou tirar o fundo desta página. Onde não der, ela sai como veio.\"",
              tela_desenho),
    ]
    guardar(P.empilhar(partes, espaco=10), "a3-frase-da-faixa.png",
            "A3: a página sem o fundo e a faixa dizendo \"vai sair em Original\" (hoje) e a frase do fundo "
            "(desenho da sugestão).")


# --------------------------------------------------------------------------- A4
def _linha_de_menu(menu: Image.Image, modelo: tuple[int, int], texto: str) -> Image.Image:
    """Uma linha nova do menu, com o mesmo fundo e a mesma letra do item "Desfazer o tirar o fundo"."""
    y0, y1 = modelo
    linha = Image.new("RGB", (menu.width, y1 - y0), FUNDO_MENU)
    d = ImageDraw.Draw(linha)
    f = P.fonte(15)
    d.text((41, (y1 - y0) / 2), texto, font=f, fill=(222, 222, 222), anchor="lm")
    return linha


def a4() -> None:
    menu = P.abrir(CRU / "fundo" / "a4-menu-filtro.png")
    corte = 137                                       # logo abaixo do risco que separa os filtros
    modelo = (139, 170)                               # a linha do "Desfazer o tirar o fundo"
    nova = _linha_de_menu(menu, modelo, "Tirar o fundo")
    proposta = Image.new("RGB", (menu.width, menu.height + nova.height), FUNDO_MENU)
    proposta.paste(menu.crop((0, 0, menu.width, corte)), (0, 0))
    proposta.paste(nova, (0, corte))
    proposta.paste(menu.crop((0, corte, menu.width, menu.height)), (0, corte + nova.height))
    escala = 2.4
    m_hoje = menu.resize((round(menu.width * escala), round(menu.height * escala)), Image.LANCZOS)
    m_prop = proposta.resize((round(proposta.width * escala), round(proposta.height * escala)), Image.LANCZOS)
    painel = P.abrir(CRU / "fundo" / "a2-painel-so-neste-pedaco.png").crop((0, 40, 300, 220))
    painel = painel.resize((round(painel.width * 1.7), round(painel.height * 1.7)), Image.LANCZOS)

    alvo_hoje = (0.05, (corte - 4) / menu.height, 0.95, (modelo[1] + 2) / menu.height)
    alvo_prop = (0.05, (corte - 2) / proposta.height, 0.95, (corte + nova.height + 2) / proposta.height)
    alvo_painel = (0.80, 0.0, 1.0, 1.0)

    linha_hoje = P.lado_a_lado([
        P.com_titulo(P.circular(m_hoje, alvo_hoje, folga=0.10, espessura=6), "menu Filtro", vermelho=True),
        P.com_titulo(P.circular(painel, (0.0, 0.84, 1.0, 1.0), folga=0.05, espessura=5),
                     "painel Filtro da página (já é assim)")], espaco=60)
    linha_prop = P.lado_a_lado([
        P.com_titulo(P.circular(m_prop, alvo_prop, folga=0.10, espessura=6), "menu Filtro (desenho)",
                     vermelho=True),
        P.com_titulo(painel, "painel Filtro da página (não muda)")], espaco=60)
    del alvo_painel
    partes = [
        P.cabeca("O \"Tirar o fundo\" no menu Filtro — resumo", P.CINZA,
                 "Siebmacher (cópia), página 4, depois do \"Sim, tirar o fundo\". Menu Filtro aberto, na barra "
                 "de cima. Ao lado, o painel Filtro da página, para comparar."),
        P.cabeca("HOJE", P.AZUL,
                 "O menu tem os quatro filtros e, depois do risco, \"Desfazer o tirar o fundo\". Não tem \"Tirar "
                 "o fundo\". No painel, o botão \"Desfazer\" já fica logo abaixo da figurinha \"Tirar o fundo\"."),
        linha_hoje,
        P.cabeca("SIM — DESENHO (ainda não existe)", P.VERDE,
                 "O menu ganha \"Tirar o fundo\" logo acima do \"Desfazer o tirar o fundo\", como no painel. "
                 "Só em livro que tem o fundo separado, como o \"Desfazer\". O painel não muda."),
        linha_prop,
    ]
    guardar(P.empilhar(partes, espaco=12), "a4-menu-filtro.png",
            "A4: o menu Filtro hoje (sem \"Tirar o fundo\") e o desenho com \"Tirar o fundo\" logo acima do "
            "\"Desfazer\".")


# --------------------------------------------------------------------------- A2
def a2() -> None:
    info = json.loads((CRU / "fundo2" / "info.json").read_text(encoding="utf-8"))
    pedaco = tuple(info["pedaco"])
    d = CRU / "fundo2"
    sem = P.abrir(d / "a2-0-tirar-o-fundo-sem-pedaco.png")
    hoje = P.abrir(d / "a2-1-tirar-o-fundo-com-pedaco.png")
    pb = P.abrir(d / "a2-3-preto-e-branco-com-pedaco.png")

    def pagina(img):
        return tracejar(P.caber(img, 900, 560), pedaco)

    def bloco(rotulo, cor, legenda, img, circular=True):
        p = pagina(img)            # o alvo é o próprio tracejado do pedaço (o círculo cobria as letras)
        return P.empilhar([P.cabeca(rotulo, cor, legenda), P.com_titulo(p, "página 5", vermelho=circular)],
                          espaco=6)

    partes = [
        P.cabeca("O \"Só neste pedaço\" em Original — resumo", P.CINZA,
                 "Siebmacher (cópia), página 5, como sai no PDF. \"Sim, tirar o fundo\"; depois, no painel Filtro "
                 "da página, \"Só neste pedaço\" > \"Original\" e um retângulo marcado no meio da página "
                 "(o pedaço é o tracejado vermelho)."),
        bloco("HOJE — página em \"Tirar o fundo\"", P.AZUL,
              "Dentro do pedaço volta o papel velho, amarelado, como foi escaneado. Fora dele, papel branco. "
              "Na página em \"Original\" depois do \"Sim\" sai igual a esta.",
              hoje),
        bloco("HOJE — a mesma página em \"Preto e branco\"", P.LARANJA,
              "O mesmo pedaço em \"Original\": aqui o papel velho NÃO volta (o pedaço sai da página já sem o "
              "fundo, sem filtro). Hoje o pedaço faz coisas diferentes conforme o filtro da página.", pb),
        bloco("SIM — DESENHO (o pedaço não traz o papel velho)", P.VERDE,
              "Dentro do pedaço, a página sem o fundo e sem filtro, como já acontece na faixa laranja. Na "
              "página em \"Tirar o fundo\" isso fica igual ao resto da página.", sem),
    ]
    guardar(P.empilhar(partes, espaco=10), "a2-so-neste-pedaco.png",
            "A2: o pedaço em Original traz o papel velho na página em \"Tirar o fundo\" (azul), não traz na "
            "página em Preto e branco (laranja), e o desenho da sugestão (verde).")


# --------------------------------------------------------------------------- B (capa do Gradus)
CAPA = CRU / "capa"
PRINT_13_01 = R.parents[1] / "relatorios" / "testes-guiados" / "2026-11-13-sessao-6" / "prints" / \
    "13-01-preto-e-branco-capa-preta.png"
if not PRINT_13_01.exists():                       # o print dele mora na pasta principal do projeto
    PRINT_13_01 = Path("D:/programas/EditorImpressao/relatorios/testes-guiados/2026-11-13-sessao-6/prints/"
                       "13-01-preto-e-branco-capa-preta.png")
ZOOM = (0.55, 0.0, 0.97, 0.30)             # o alto da capa azul (frações da página dupla)
ALVO_RETANGULOS = (0.64, 0.0, 0.90, 0.12)
ALVO_ONAI = (0.755, 0.0, 0.86, 0.085)
FRASE_DEFEITO = ("Os retângulos brancos são um defeito já anotado; o conserto está parado porque você "
                 "mandou não consertar agora.")


def no_zoom(caixa, zoom=ZOOM):
    zx0, zy0, zx1, zy1 = zoom
    x0, y0, x1, y1 = caixa
    return ((x0 - zx0) / (zx1 - zx0), (y0 - zy0) / (zy1 - zy0),
            (x1 - zx0) / (zx1 - zx0), (y1 - zy0) / (zy1 - zy0))


def capa(pasta: str, variante: str) -> Image.Image:
    return P.abrir(CAPA / pasta / variante / "pdf.png")


def linha_capa(img: Image.Image, alvo, circular: bool = True, titulo_zoom: str = "o alto da capa, ampliado"):
    inteira = P.caber(img, 640, 440)
    pedaco = P.caber(P.recorte(img, ZOOM), 780, 440)
    if circular:
        inteira = P.circular(inteira, alvo, folga=0.25, espessura=5)
        pedaco = P.circular(pedaco, no_zoom(alvo), folga=0.2)
    return P.lado_a_lado([P.com_titulo(inteira, "a capa aberta (página 1)"),
                          P.com_titulo(pedaco, titulo_zoom, vermelho=circular)])


def b1() -> None:
    partes = [
        P.cabeca("Capa do Gradus no Preto e branco — resumo", P.CINZA,
                 "Gradus Primus (cópia), página 1 (a capa aberta), como sai no PDF. Painel Filtro da página > "
                 "\"Preto e branco\" e a caixinha \"Respeitar as gravuras achadas\". Olhe a capa azul, à direita."),
        P.com_titulo(P.circular(P.caber(P.abrir(PRINT_13_01), 1300, 740), (0.785, 0.287, 0.935, 0.312),
                                folga=0.25, espessura=5),
                     "o seu print 13-01: a caixinha \"Respeitar as gravuras achadas\" desmarcada", vermelho=True),
        P.empilhar([P.cabeca("Como o livro foi escaneado", P.CINZA, ""),
                    linha_capa(capa("hoje", "original"), ALVO_RETANGULOS, circular=False)], espaco=6),
        P.empilhar([P.cabeca("HOJE — caixinha marcada (como vem)", P.AZUL,
                             "A capa fica em tons de cinza (é tratada como pintura)."),
                    linha_capa(capa("hoje", "pb+resp1"), ALVO_RETANGULOS, circular=False)], espaco=6),
        P.empilhar([P.cabeca("HOJE — caixinha desmarcada (seu print 13-01)", P.LARANJA,
                             "O Preto e branco vale na página inteira: a capa azul sai toda preta, com as letras "
                             "brancas. Circulados: os retângulos brancos. " + FRASE_DEFEITO),
                    linha_capa(capa("hoje", "pb+samuel+resp0"), ALVO_RETANGULOS)], espaco=6),
        P.empilhar([P.cabeca("SIM, ESTÁ CERTO — capa toda preta", P.VERDE,
                             "O mesmo caminho, sem os retângulos brancos (simulação: é como a capa saía antes de "
                             "27/10 e como fica quando o defeito for consertado). Capa preta e lisa, letras brancas."),
                    linha_capa(capa("sem_quadros", "pb+samuel+resp0"), ALVO_RETANGULOS)], espaco=6),
    ]
    guardar(P.empilhar(partes, espaco=10), "b1-capa-toda-preta.png",
            "B1: a capa do Gradus no Preto e branco com a caixinha marcada (tons de cinza) e desmarcada (toda "
            "preta, com os retângulos brancos do defeito parado); em verde, a capa preta lisa.")


def b3() -> None:
    def zoom(img, alvo, titulo):
        z = P.caber(P.recorte(img, ZOOM), 700, 380)
        return P.com_titulo(P.circular(z, no_zoom(alvo), folga=0.25, espessura=6), titulo, vermelho=True)

    def faixa(rotulo, cor, legenda, pasta):
        linha = P.lado_a_lado([
            zoom(capa(pasta, "pb+samuel+resp0+letras1"), ALVO_ONAI, "com \"Só as letras\" (13-02)"),
            zoom(capa(pasta, "pb+resp1"), ALVO_ONAI, "Preto e branco como vem")], espaco=40)
        return P.empilhar([P.cabeca(rotulo, cor, legenda), linha], espaco=6)

    original = capa("hoje", "original")
    resumo = P.lado_a_lado([
        P.com_titulo(P.circular(P.caber(original, 640, 420), ALVO_ONAI, folga=0.5, espessura=5),
                     "a capa aberta, como foi escaneada"),
        P.com_titulo(P.circular(P.caber(P.recorte(original, ZOOM), 760, 420), no_zoom(ALVO_ONAI), folga=0.25),
                     "o alto da capa: \"PAULO RÓNAI\"", vermelho=True)])
    partes = [
        P.cabeca("O nome escrito em cima da capa — resumo", P.CINZA,
                 "Gradus Primus (cópia), página 1. Preto e branco com \"Só as letras\" (como no seu print 13-02) "
                 "e Preto e branco como vem (caixinha \"Respeitar as gravuras achadas\" marcada). O programa acha "
                 "\"ÓNAI\" (de \"PAULO RÓNAI\") como letra, em cima da capa achada como pintura."),
        resumo,
        faixa("HOJE — uma caixa no lugar de \"ÓNAI\"", P.AZUL,
              "A letra é passada para preto e branco e abre uma caixa na capa. A caixa sai branca por causa do "
              "defeito dos retângulos (anotado, parado por ordem sua); sem ele, ela sai preta.", "hoje"),
        faixa("(b) CONTINUA PRETO E BRANCO — caixa preta", P.LARANJA,
              "Simulação de como fica depois do conserto parado: a caixa continua, preta, com \"ÓNAI\" "
              "em branco. Era assim antes de 27/10.", "sem_quadros"),
        faixa("(a) FICA COMO A CAPA — sem caixa (sugestão)", P.VERDE,
              "Simulação: o nome escrito em cima da capa fica com a cor da capa, como o resto do título. "
              "Nenhuma caixa.", "sem_letra"),
    ]
    guardar(P.empilhar(partes, espaco=10), "b3-nome-sobre-a-capa.png",
            "B3: \"ÓNAI\" sobre a capa azul: hoje uma caixa (branca pelo defeito parado), (b) caixa preta, (a) "
            "sem caixa, com a cor da capa.")


def main() -> None:
    pedidas = set(sys.argv[1:]) or {"a2", "a3", "a4", "b1", "b3", "c"}
    for nome, func in (("a2", a2), ("a3", a3), ("a4", a4)):
        if nome in pedidas:
            func()
            print("ok", nome)
    for nome in ("b1", "b3", "c"):
        if nome in pedidas and nome in globals():
            globals()[nome]()
            print("ok", nome)
    LEG_ARQ.write_text(json.dumps(LEG, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
