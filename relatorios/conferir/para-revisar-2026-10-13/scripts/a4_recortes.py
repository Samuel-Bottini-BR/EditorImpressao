"""20/10/2026: recortes "so a parte que muda, ampliada" para a aba 4 da pagina de conferencia.

Cada recorte sai de uma imagem que ja esta em img/ (nada e medido de novo): junta, uma embaixo
da outra, as faixas que importam (o aviso, os botoes, os cartoes) e amplia. Grava img/a4-*.jpg.
As coordenadas sao em pontos da imagem de origem (x0, y0, x1, y1). So le as imagens de origem."""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
IMG = BASE / "img"
DES = BASE / "trabalho" / "desenhos"
FUNDO = (43, 43, 43)
LARGURA = 1600


def pedaco(origem, caixa):
    im = Image.open(origem).convert("RGB")
    return im.crop(caixa)


def empilhar(nome, pedacos, largura=LARGURA, lado_a_lado=False, espaco=14, centro=()):
    """Junta os pedacos (um embaixo do outro, ou lado a lado) e amplia ate `largura`."""
    if lado_a_lado:
        h = max(p.height for p in pedacos)
        pedacos = [p.resize((round(p.width * h / p.height), h), Image.LANCZOS) for p in pedacos]
        w = sum(p.width for p in pedacos) + espaco * (len(pedacos) - 1)
        tela = Image.new("RGB", (w, h), FUNDO)
        x = 0
        for p in pedacos:
            tela.paste(p, (x, 0)); x += p.width + espaco
    else:
        w = max(p.width for p in pedacos)
        h = sum(p.height for p in pedacos) + espaco * (len(pedacos) - 1)
        tela = Image.new("RGB", (w, h), FUNDO)
        y = 0
        for i, p in enumerate(pedacos):
            x = (w - p.width) // 2 if i in centro else w - p.width       # os botoes ficam a direita, como na tela
            tela.paste(p, (x, y)); y += p.height + espaco
    if tela.width != largura:
        tela = tela.resize((largura, round(tela.height * largura / tela.width)), Image.LANCZOS)
    destino = IMG / f"a4-{nome}.jpg"
    tela.save(destino, quality=90)
    return destino


R = 2184 / 2000          # os recortes de 2184 pontos foram vistos a 2000


def c(x0, y0, x1, y1, k=R):
    return (round(x0 * k), round(y0 * k), round(x1 * k), round(y1 * k))


feitos = []
# 1. letra T: o Original (T vermelho) e o Preto e branco (T que vai sumir no PDF), com a marca laranja
feitos.append(empilhar("letra-t", [pedaco(IMG / "letra-t-0-marca-recorte.jpg", (55, 15, 400, 260)),
                                   pedaco(IMG / "letra-t-0-marca-recorte.jpg", (535, 20, 875, 265))], lado_a_lado=True))
# 2. Graduale 222: o cartao Original e o do Preto e branco sem a musica, a marca laranja e o aviso com os botoes
cartoes = Image.open(empilhar("tmp", [pedaco(IMG / "so-o-texto-1-aviso-recorte.jpg", c(255, 50, 405, 297)),
                                      pedaco(IMG / "so-o-texto-1-aviso-recorte.jpg", c(635, 55, 780, 297))],
                                largura=900, lado_a_lado=True)).copy()
feitos.append(empilhar("so-o-texto", [
    cartoes,
    pedaco(IMG / "so-o-texto-1-aviso-recorte.jpg", c(0, 305, 2000, 372)),
    pedaco(IMG / "so-o-texto-1-aviso-recorte.jpg", c(1420, 620, 2000, 690))], centro=(0,)))
# 3. sem conteudo (Egenloff 12) e Rariora 8: o aviso e os tres botoes
feitos.append(empilhar("sem-conteudo", [pedaco(IMG / "sem-conteudo-1-egenloff-recorte.jpg", c(0, 305, 2000, 372)),
                                        pedaco(IMG / "sem-conteudo-1-egenloff-recorte.jpg", c(1330, 620, 2000, 690))]))
# 4. Gladstone 18: o aviso "Parece em branco" e os tres botoes
feitos.append(empilhar("parece-em-branco", [pedaco(IMG / "parece-em-branco-1-recorte.jpg", c(0, 305, 2000, 372)),
                                            pedaco(IMG / "parece-em-branco-1-recorte.jpg", c(1330, 620, 2000, 690))]))
# 5. forca sozinha (Camoes 27): o aviso, o medidor em "bem forte" e os botoes
feitos.append(empilhar("forca-sozinha", [pedaco(IMG / "forca-1-camoes-recorte.jpg", c(0, 0, 2000, 70)),
                                         pedaco(IMG / "forca-1-camoes-recorte.jpg", c(0, 110, 2000, 162)),
                                         pedaco(IMG / "forca-1-camoes-recorte.jpg", c(1620, 318, 2000, 388))]))
# 6. Palatino 66: o aviso "Texto falhado", a forca em "normal" e os botoes
feitos.append(empilhar("palatino-66", [pedaco(IMG / "palatino-66-2-aviso-recorte.jpg", c(0, 290, 2000, 385)),
                                       pedaco(IMG / "palatino-66-2-aviso-recorte.jpg", c(0, 428, 2000, 475)),
                                       pedaco(IMG / "palatino-66-2-aviso-recorte.jpg", c(1540, 635, 2000, 692))]))
# 7. a lista "Antes de processar" (Camoes): a frase e as primeiras linhas
feitos.append(empilhar("antes-de-processar", [pedaco(IMG / "antes-3-lista-camoes.jpg", (0, 40, 702, 450)),
                                              pedaco(IMG / "antes-3-lista-camoes.jpg", (0, 560, 702, 689))], largura=1100))
# 8. Graduale 221: os cartoes e a faixa sem aviso
feitos.append(empilhar("janela-diferente", [pedaco(IMG / "janela-diferente-1-graduale-221-recorte.jpg", c(140, 40, 1990, 297)),
                                            pedaco(IMG / "janela-diferente-1-graduale-221-recorte.jpg", c(0, 305, 2000, 372))]))
# 9. projeto antigo no ramo: "Texto falhado", forca normal, botoes
feitos.append(empilhar("projeto-antigo", [pedaco(IMG / "antigo-2-no-ramo-recorte.jpg", c(0, 290, 2000, 385)),
                                          pedaco(IMG / "antigo-2-no-ramo-recorte.jpg", c(1540, 635, 2000, 692))]))
# 10. dois cliques: o aviso e os botoes continuam
feitos.append(empilhar("duplo-clique", [pedaco(IMG / "duplo-clique-1-aviso-continua-recorte.jpg", c(0, 305, 2000, 372)),
                                        pedaco(IMG / "duplo-clique-1-aviso-continua-recorte.jpg", c(1420, 620, 2000, 690))]))
# 11. teclado: a tira com a pagina 13 escolhida depois da barra de espaco
feitos.append(empilhar("teclado", [pedaco(IMG / "teclado-1-recorte.jpg", c(0, 305, 2000, 372)),
                                   pedaco(IMG / "teclado-1-recorte.jpg", c(0, 688, 1540, 775))]))
(IMG / "a4-tmp.jpg").unlink(missing_ok=True)
for f in feitos:
    print(Path(f).name, Image.open(f).size)
