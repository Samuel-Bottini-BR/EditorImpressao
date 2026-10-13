"""Monta as imagens da conferencia (img/*.jpg) a partir dos prints da janela
(trabalho/prints/*.png) e das paginas tiradas do PDF gerado (trabalho/desenhos).

Para cada quadro: primeiro o RECORTE da parte da tela que importa, ampliado;
depois a TELA INTEIRA. JPG qualidade 90, nomes sem acento. Nao muda print nenhum.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
PR = BASE / "trabalho" / "prints"
DE = BASE / "trabalho" / "desenhos"
IMG = BASE / "img"
IMG.mkdir(exist_ok=True)

FAIXA = (20, 205, 1580, 745)        # cartoes + aviso + ajuste + botoes do aviso (janela 1600 x 821)
SO_AVISO = (20, 440, 1580, 762)     # aviso + ajuste + botoes
PERTO = (480, 140, 1125, 990)       # a pagina dentro do "Ver de perto"


def fonte(tam):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def abrir(nome):
    p = PR / f"{nome}.png"
    if not p.exists():
        p = DE / f"{nome}.png"
    return Image.open(p).convert("RGB")


def salvar(img, nome):
    destino = IMG / f"{nome}.jpg"
    img.save(destino, "JPEG", quality=90)
    return destino


def recorte(origem, nome, caixa, escala=1.4):
    img = abrir(origem).crop(caixa)
    if escala != 1:
        img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
    return salvar(img, nome)


def inteira(origem, nome):
    return salvar(abrir(origem), nome)


def lado_a_lado(partes, nome, altura=560, titulo_px=30):
    """partes = [(origem, caixa, legenda)]: poe os recortes lado a lado, na mesma altura, com a legenda em cima."""
    imgs = []
    for origem, caixa, legenda in partes:
        im = abrir(origem)
        if caixa:
            im = im.crop(caixa)
        im = im.resize((round(im.width * altura / im.height), altura), Image.LANCZOS)
        imgs.append((im, legenda))
    largura = sum(i.width for i, _ in imgs) + 20 * (len(imgs) + 1)
    tela = Image.new("RGB", (largura, altura + titulo_px + 50), "white")
    d = ImageDraw.Draw(tela)
    x = 20
    for im, legenda in imgs:
        d.text((x, 12), legenda, fill=(170, 60, 0), font=fonte(titulo_px - 6))
        tela.paste(im, (x, titulo_px + 30))
        d.rectangle([x - 1, titulo_px + 29, x + im.width, titulo_px + 30 + im.height], outline=(120, 120, 120))
        x += im.width + 20
    return salvar(tela, nome)


def main():
    feitos = []
    f = feitos.append
    # 1 letra T
    f(recorte("70d-antiphonal-46-maximizada", "letra-t-0-marca-recorte", (140, 235, 1030, 630), 1.6))
    f(recorte("70d-antiphonal-46-maximizada", "letra-t-1-aviso-recorte", (20, 205, 1900, 935), 1.0))
    f(inteira("70d-antiphonal-46-maximizada", "letra-t-2-aviso-tela"))
    f(inteira("70d-antiphonal-46", "letra-t-5-aviso-tela-1280x657"))
    f(recorte("04b-antiphonal-46-depois-do-trazer-de-volta", "letra-t-3-trazer-de-volta-recorte", FAIXA))
    f(inteira("04c-antiphonal-46-ctrlz", "letra-t-4-ctrlz-tela"))
    # 2 a tela mostra a letra, o PDF sai sem ela
    f(lado_a_lado([("03g-antiphonal-46-ver-de-perto-com-aviso", (560, 299, 1097, 470), "Na tela (Ver de perto): a letra T aparece"),
                   ("pdf-A-pagina3", (30, 194, 726, 415), "No PDF que saiu: a letra T sumiu")],
                  "tela-engana-1-comparacao", altura=300))
    f(inteira("03g-antiphonal-46-ver-de-perto-com-aviso", "tela-engana-2-ver-de-perto-tela"))
    f(inteira("pdf-A-pagina3", "tela-engana-3-pagina-do-pdf"))
    # 3 guardar so o texto
    f(recorte("40b-graduale-222-so-o-texto", "so-o-texto-1-aviso-recorte", FAIXA))
    f(inteira("40b-graduale-222-so-o-texto", "so-o-texto-2-aviso-tela"))
    f(recorte("40c-graduale-222-trazer-de-volta", "so-o-texto-3-trazer-de-volta-recorte", FAIXA))
    # 4 pagina sem conteudo
    f(recorte("20b-egenloff-12-pagina-sem-conteudo", "sem-conteudo-1-egenloff-recorte", FAIXA))
    f(inteira("20b-egenloff-12-pagina-sem-conteudo", "sem-conteudo-2-egenloff-tela"))
    f(recorte("21a-egenloff-12-deixar-em-branco", "sem-conteudo-3-deixar-em-branco-recorte", FAIXA))
    f(recorte("21c-egenloff-12-tirar-do-livro", "sem-conteudo-4-tirar-do-livro-recorte", (20, 205, 1580, 815)))
    f(recorte("51-rariora-p8-tela", "sem-conteudo-5-rariora-recorte", FAIXA))
    # 5 parece em branco
    f(recorte("50-gladstone-p18-parece-em-branco", "parece-em-branco-1-recorte", FAIXA))
    f(inteira("50-gladstone-p18-parece-em-branco", "parece-em-branco-2-tela"))
    f(recorte("50-gladstone-p18-perto", "parece-em-branco-3-a-pagina", PERTO, 0.8))
    # 6 forca do preto sozinha
    f(recorte("30a-camoes-27-forca-sozinha", "forca-1-camoes-recorte", SO_AVISO))
    f(inteira("30a-camoes-27-forca-sozinha", "forca-2-camoes-tela"))
    f(recorte("30c-camoes-27-desfazer", "forca-3-desfazer-recorte", SO_AVISO))
    f(recorte("22a-egenloff-3-forca-sozinha", "forca-4-egenloff-3-recorte", FAIXA))
    f(recorte("01-o-que-fazer-caixinha-forca", "forca-5-caixinha-recorte", (55, 270, 935, 625)))
    f(inteira("01-o-que-fazer-caixinha-forca", "forca-6-caixinha-tela"))
    # 7 antes de processar
    f(inteira("25a-antes-de-processar-egenloff", "antes-1-lista-egenloff"))
    f(inteira("10c-depois-do-ver-pagina3", "antes-2-depois-do-ver-tela"))
    f(inteira("32a-antes-de-processar-camoes", "antes-3-lista-camoes"))
    f(inteira("10d-janela-confirmar", "antes-4-confirmar"))
    f(inteira("10f-ficou-pronto", "antes-5-ficou-pronto-tela"))
    # 8 esta bom
    f(recorte("23a-esta-bom-um-motivo-da-pagina", "esta-bom-1-um-motivo-recorte", (20, 205, 1580, 815)))
    f(inteira("23b-esta-bom-um-motivo-em-todas", "esta-bom-2-motivo-em-todas-tela"))
    f(inteira("23d-esta-bom-em-tudo", "esta-bom-3-em-tudo-tela"))
    f(inteira("24b-seletor-duas-marcadas", "esta-bom-4-seletor"))
    # 9 a janela mede diferente da conferencia do implementador
    f(recorte("40x-graduale-pagina3", "janela-diferente-1-graduale-221-recorte", FAIXA))
    f(inteira("40x-graduale-pagina3", "janela-diferente-2-graduale-221-tela"))
    # 10 a 13: as quatro paginas
    for origem, nome in (("62-cursus-p3", "cursus-3"), ("61-opusmajus-p1", "opus-majus-20"),
                         ("60-palatino-p66", "palatino-66"), ("63-antiphon-p260", "antiphon-260")):
        f(recorte(f"{origem}-perto", f"{nome}-1-pagina-recorte", PERTO, 0.9))
        f(recorte(f"{origem}-tela", f"{nome}-2-aviso-recorte", SO_AVISO, 1.0))
        f(inteira(f"{origem}-tela", f"{nome}-3-tela"))
    # 14 camoes 66
    f(recorte("31a-camoes-66", "camoes-66-1-recorte", FAIXA))
    f(inteira("31a-camoes-66", "camoes-66-2-tela"))
    # 15 projeto antigo
    f(recorte("80a-antigo-no-fase1-p12", "antigo-1-no-programa-de-hoje-recorte", FAIXA))
    f(recorte("80c-antigo-no-ramo-p12", "antigo-4-no-ramo-p12-recorte", FAIXA))
    f(recorte("80c-antigo-no-ramo-p3", "antigo-2-no-ramo-recorte", FAIXA))
    f(inteira("80c-antigo-no-ramo-p3", "antigo-3-no-ramo-tela"))
    # a pergunta da medida
    f(lado_a_lado([("70b-lista-poucas-visitadas-desenho-apagado", None, "Visitei 2 páginas: a lista mostra 2"),
                   ("70c-lista-mais-visitadas-desenho-apagado", None, "Visitei mais 4: a lista mostra 4")],
                  "medir-1-listas", altura=620))
    f(inteira("70b-lista-poucas-visitadas-todos", "medir-2-lista-inteira"))
    # bugs
    f(inteira("03e-antiphonal-46-filtro-depois-do-marcar", "bug-duplo-clique-tira-o-aviso-tela"))
    for d in feitos:
        im = Image.open(d)
        print(f"{d.name:52s} {im.width}x{im.height} {d.stat().st_size // 1024} KB")
    print(len(feitos), "imagens")


if __name__ == "__main__":
    sys.exit(main())
