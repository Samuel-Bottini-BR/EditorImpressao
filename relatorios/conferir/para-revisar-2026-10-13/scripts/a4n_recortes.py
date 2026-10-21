"""21/10/2026: recortes da aba 4 na TELA NOVA (layout aprovado; codigo adf4e69, e 8cb84b8 nas fotos m*), a partir dos prints
trabalho/prints/n*.png (janela de 1600 x 821 pontos, com a barra de titulo). So le os prints.
Grava img/a4n-*.jpg: so a parte que muda, ampliada."""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
PR = BASE / "trabalho" / "prints"
IMG = BASE / "img"
FUNDO = (43, 43, 43)

CARTOES_E_FAIXA = (56, 116, 1544, 468)       # os cartoes de filtro e a faixa do aviso (painel fechado)
CARTOES_E_FAIXA_P = (56, 116, 1168, 468)     # com o painel da direita aberto
FAIXA = (56, 402, 1544, 468)
TIRA_E_RODAPE = (56, 700, 1544, 821)


def p(nome, caixa=None):
    im = Image.open(PR / f"{nome}.png").convert("RGB")
    return im.crop(caixa) if caixa else im


def junta(nome, pedacos, largura=1600, lado=False, espaco=14):
    if lado:
        h = max(x.height for x in pedacos)
        pedacos = [x.resize((round(x.width * h / x.height), h), Image.LANCZOS) for x in pedacos]
        t = Image.new("RGB", (sum(x.width for x in pedacos) + espaco * (len(pedacos) - 1), h), FUNDO)
        pos = 0
        for x in pedacos:
            t.paste(x, (pos, 0)); pos += x.width + espaco
    else:
        w = max(x.width for x in pedacos)
        t = Image.new("RGB", (w, sum(x.height for x in pedacos) + espaco * (len(pedacos) - 1)), FUNDO)
        pos = 0
        for x in pedacos:
            t.paste(x, (0, pos)); pos += x.height + espaco
    if t.width != largura:
        t = t.resize((largura, round(t.height * largura / t.width)), Image.LANCZOS)
    t.save(IMG / f"a4n-{nome}.jpg", quality=90)
    return f"img/a4n-{nome}.jpg"


FEITOS = {
    "letra-t": junta("letra-t", [p("n04-ant46-ferramenta-filtro", CARTOES_E_FAIXA)]),
    "letra-t-marcar": junta("letra-t-marcar", [p("n10-ant46-marcar", (470, 86, 752, 300))], largura=900),
    "letra-t-depois": junta("letra-t-depois", [p("n09-ant46-trazer-de-volta", (56, 86, 1545, 468))]),
    "painel": junta("painel", [p("n08-ant46-painel-para-revisar", (1170, 86, 1545, 345))], largura=900),
    "duplo-clique": junta("duplo-clique", [p("n07-ant46-depois-do-duplo-clique", CARTOES_E_FAIXA)]),
    "ver-de-perto": junta("ver-de-perto", [p("n06-ant46-ver-de-perto")], largura=1200),
    "marcar-sozinha": junta("marcar-sozinha", [p("n13-grad223-marcar-previa", (560, 86, 1040, 540)),
                                               p("n14-grad223-marcar-depois", (560, 86, 1040, 540))], lado=True, largura=1200),
    "marcar-a-mao": junta("marcar-a-mao", [p("n15-grad224-a-mao-depois", (630, 86, 970, 535))], largura=700),
    "janela-diferente": junta("janela-diferente", [p("n12-grad221-marcar-depois", (56, 86, 1544, 590))]),
    "so-o-texto": junta("so-o-texto", [p("n18-grad222-so-o-texto", CARTOES_E_FAIXA)]),
    "so-o-texto-depois": junta("so-o-texto-depois", [p("n19-grad222-trazer-de-volta", (56, 116, 1544, 468))]),
    "sem-conteudo": junta("sem-conteudo", [p("n20-egenloff12-sem-conteudo", CARTOES_E_FAIXA)]),
    "deixar-em-branco": junta("deixar-em-branco", [p("n21-egenloff12-deixar-em-branco", (56, 116, 1544, 468))]),
    "tirar-do-livro": junta("tirar-do-livro", [p("n22-egenloff12-tirar-do-livro", (56, 655, 1544, 821))]),
    "teclado": junta("teclado", [p("n23-egenloff-espaco", (56, 402, 1544, 821))]),
    "egenloff-3": junta("egenloff-3", [p("m01-egenloff3-texto-falhado", CARTOES_E_FAIXA)]),
    "egenloff-3-escuro": junta("egenloff-3-escuro", [p("m08-egenloff3-escuro", (56, 402, 1544, 545))]),
    "caixinha": junta("caixinha", [p("n28-o-que-fazer-caixinha-rolado", (60, 212, 910, 600))], largura=1100),
    "forca-sozinha": junta("forca-sozinha", [p("n29-camoes27-forca-sozinha", (56, 402, 1544, 545))]),
    "forca-desfazer": junta("forca-desfazer", [p("m07-camoes27-desfazer", (56, 402, 1544, 545))]),
    "antes-de-processar": junta("antes-de-processar", [p("n31-antes-de-processar-camoes")], largura=900),
    "antes-varios": junta("antes-varios", [p("n46-antes-de-processar-varios")], largura=900),
    "confirmar": junta("confirmar", [p("n47-confirmar")], largura=1000),
    "ficou-pronto": junta("ficou-pronto", [p("n48-ficou-pronto", (100, 250, 1500, 580))]),
    "painel-por-pagina": junta("painel-por-pagina", [p("n32-camoes-painel-por-pagina", (1170, 86, 1545, 821))], largura=700),
    "painel-por-motivo": junta("painel-por-motivo", [p("n33-camoes-painel-por-motivo", (1170, 86, 1545, 821))], largura=700),
    "esta-bom-todas": junta("esta-bom-todas", [p("n34-camoes-esta-bom-todas", (1170, 86, 1545, 821))], largura=700),
    "esta-bom-em-tudo": junta("esta-bom-em-tudo", [p("n35-camoes-esta-bom-em-tudo", (1170, 86, 1545, 400))], largura=700),
    "seletor": junta("seletor", [p("n36-camoes-seletor")], largura=900),
    "camoes-66": junta("camoes-66", [p("n37-camoes66", (56, 86, 1600, 470))]),
    "rariora-8": junta("rariora-8", [p("n41-rariora8", CARTOES_E_FAIXA)]),
    "gladstone-18": junta("gladstone-18", [p("n45-gladstone18-parece-em-branco", CARTOES_E_FAIXA)]),
    "palatino-66": junta("palatino-66", [p("m03-palatino66", CARTOES_E_FAIXA)]),
    "opus-20": junta("opus-20", [p("m04-opus20", CARTOES_E_FAIXA)]),
    "cursus-3": junta("cursus-3", [p("m05-cursus3", CARTOES_E_FAIXA)]),
    "antiphon-260": junta("antiphon-260", [p("m06-antiphon260", CARTOES_E_FAIXA)]),
    "antigo-no-fase1": junta("antigo-no-fase1", [p("n50-antigo-no-fase1-p12", CARTOES_E_FAIXA)]),
    "antigo-no-ramo": junta("antigo-no-ramo", [p("n52-antigo-no-ramo-p12", CARTOES_E_FAIXA)]),
}

if __name__ == "__main__":
    for k, v in FEITOS.items():
        print(k, v, Image.open(BASE / v).size)
