"""Verificador 04/11: D-618 (girar so a pagina numa folha dividida; folha inteira gira como foto).
Livro do acervo: Siebmacher (folhas deitadas, abre sem dividir). Caminho do Samuel: Dividir a folha
3 ("dividir esta"), Cortar, pagina 3 (metade esquerda), "1/4 a esquerda" do Propriedades."""
import hashlib
import sys

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\girar-pagina"


def pix(j):
    v = C.visualizador(j)
    px = getattr(v, "_pixmap", None)
    if px is None:
        return None
    img = px.toImage()
    h = hashlib.md5(bytes(img.constBits())[: img.sizeInBytes()]).hexdigest()[:8]
    return {"larg": px.width(), "alt": px.height(), "prop": round(px.width() / max(1, px.height()), 3), "md5": h}


def campos(j, i):
    pg = j.projeto.paginas[i]
    f = j.projeto.folhas[pg.folha]
    return {"pagina": i + 1, "folha": pg.folha + 1, "metade": pg.metade, "giro_da_pagina": pg.giro_da_pagina,
            "rotacao_da_folha": f.rotacao, "dividir": f.dividir, "linha": f.posicao_corte, "recorte": pg.recorte}


def main():
    j, porteiro = C.abrir(WT, "1-girar", "Schön Neues Modell Buch - Johann Siebmacher.pdf")
    from core import girar
    t = j.tela_conferir
    p(j, "abriu")

    # 1. Dividir a folha 3 a mao ("dividir esta")
    C.ferramenta(j, "D")
    C.ir_pagina(j, 3)
    anotar("botao dividir/nao dividir", t.botao_nao_dividir.text())
    C.base.clique(j, t.botao_nao_dividir); C.base.esperar(3); C.esperar_previa(j)
    conferir(j.projeto.folhas[2].dividir, "a folha 3 ficou dividida pelo 'dividir esta'")
    anotar("depois de dividir", [campos(j, 2), campos(j, 3)])
    p(j, "dividir-folha-3")

    # 2. Cortar, Uma pagina, pagina 3 (metade esquerda da folha 3)
    C.ferramenta(j, "X"); C.mostrar(j, "uma")
    C.ir_pagina(j, 3)
    anotar("estado", C.estado(j))
    antes3, antes4c = pix(j), campos(j, 3)
    anotar("pagina 3 antes", {"tela": antes3, "campos": campos(j, 2)})
    p(j, "cortar-pagina-3-antes")
    C.ir_pagina(j, 4); antes4 = pix(j); anotar("pagina 4 antes", {"tela": antes4, "campos": antes4c})
    p(j, "cortar-pagina-4-antes")
    C.ir_pagina(j, 3)

    # 3. "1/4 a esquerda" do Propriedades (clique de verdade)
    b = t.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA]
    anotar("botao", b.text() or b.toolTip())
    C.base.clique(j, b); C.esperar_previa(j)
    d3 = pix(j)
    anotar("pagina 3 depois de 1/4 a esquerda", {"tela": d3, "campos": campos(j, 2), "estado": C.estado(j)})
    p(j, "pagina-3-um-quarto-esquerda")
    conferir(j.projeto.paginas[2].giro_da_pagina != 0, "a pagina 3 ficou girada (giro_da_pagina)")
    conferir(j.projeto.folhas[2].rotacao == 0, "a folha 3 NAO girou (rotacao 0)")
    conferir(antes3 and d3 and abs(d3["prop"] - 1 / antes3["prop"]) < 0.06,
             f"a pagina 3 so deitou (proporcao {antes3 and antes3['prop']} -> {d3 and d3['prop']}, esperado ~{antes3 and round(1/antes3['prop'],3)})")
    conferir(campos(j, 3)["giro_da_pagina"] == 0 and campos(j, 3)["linha"] == antes4c["linha"],
             "a pagina 4 e a linha da divisao nao mudaram (campos)")
    C.ir_pagina(j, 4); d4 = pix(j)
    conferir(d4 == antes4, f"a pagina 4 na tela igual a antes ({antes4} / {d4})")
    p(j, "pagina-4-depois")
    C.ir_pagina(j, 3)

    # 4. Duas vezes mais (o print a-70: 'cai na folha branca'), pelo canto e Ctrl+Seta
    C.base.clique(j, t.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA]); C.esperar_previa(j)
    p(j, "pagina-3-meia-volta-pelo-painel")
    anotar("pagina 3 depois de 2x esquerda", {"tela": pix(j), "campos": campos(j, 2)})
    C.base.clique(j, t.girar_do_canto.botoes_de_giro[girar.GIRO_DIREITA]); C.esperar_previa(j)
    anotar("pagina 3 depois do canto a direita", {"tela": pix(j), "campos": campos(j, 2)})
    p(j, "pagina-3-canto-direita")
    C.ctrl(j, C.VK_RIGHT); C.esperar_previa(j)
    anotar("pagina 3 depois de Ctrl+Seta direita", {"tela": pix(j), "campos": campos(j, 2), "estado": C.estado(j)})
    p(j, "pagina-3-ctrl-seta-direita")
    conferir(campos(j, 2)["giro_da_pagina"] == 0 and j.projeto.folhas[2].rotacao == 0,
             "esq+esq+dir+dir = volta a 0, folha sem giro")
    # Ctrl+Z ate voltar ao 1/4
    for _ in range(3):
        C.ctrl(j, ord("Z")); C.esperar_previa(j)
    anotar("depois de 3 Ctrl+Z", {"campos": campos(j, 2), "estado": C.estado(j)})
    conferir(campos(j, 2)["giro_da_pagina"] == girar.GIRO_ESQUERDA, "3 Ctrl+Z voltam ao 1/4 a esquerda")
    C.ctrl(j, ord("Z")); C.esperar_previa(j)
    conferir(campos(j, 2)["giro_da_pagina"] == 0, "mais um Ctrl+Z volta a pagina como veio")
    p(j, "ctrl-z-tudo")

    # 5. Folha inteira (nao dividida): pagina 6 (folha 5). Gira como foto, sem mudar a proporcao.
    C.ir_pagina(j, 6)
    anotar("pagina 6", campos(j, 5))
    a6 = pix(j); p(j, "folha-inteira-antes")
    C.base.clique(j, t.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA]); C.esperar_previa(j)
    d6 = pix(j); anotar("folha inteira girada", {"antes": a6, "depois": d6, "campos": campos(j, 5)})
    p(j, "folha-inteira-girada-cortar")
    conferir(j.projeto.folhas[4].rotacao != 0, "folha inteira: a folha girou")
    conferir(a6 and d6 and abs(d6["prop"] - 1 / a6["prop"]) < 0.06,
             f"folha inteira: so deitou, sem esticar (proporcao {a6 and a6['prop']} -> {d6 and d6['prop']})")
    # como sai (Filtros mostra a pagina pronta) e no Mover (a folha de papel)
    for letra, nome in (("F", "mover"), ("E", "endireitar")):
        C.ferramenta(j, letra)
        anotar(f"folha inteira girada no {nome}", {"tela": pix(j), "estado": C.estado(j)})
        p(j, f"folha-inteira-girada-{nome}")
    C.ferramenta(j, "X")
    C.ctrl(j, ord("Z")); C.esperar_previa(j)
    conferir(j.projeto.folhas[4].rotacao == 0, "Ctrl+Z desgira a folha inteira")

    # 6. Ao redor: Dividir em Duas lado a lado mostra a folha 3 inteira com a linha; Endireitar na pag 3
    C.ferramenta(j, "D"); C.ir_pagina(j, 3); C.mostrar(j, "duas")
    anotar("dividir duas lado a lado", C.estado(j)); p(j, "dividir-duas-lado-a-lado")
    C.mostrar(j, "uma"); p(j, "dividir-uma-pagina")
    C.ferramenta(j, "X"); C.ir_pagina(j, 3)
    C.base.clique(j, t.barra_girar.botoes_de_giro[girar.GIRO_DIREITA]); C.esperar_previa(j)
    C.ferramenta(j, "E")
    anotar("endireitar com a pagina 3 girada", {"tela": pix(j), "estado": C.estado(j), "campos": campos(j, 2)})
    p(j, "endireitar-pagina-3-girada")
    C.mostrar(j, "duas"); p(j, "endireitar-duas-lado-a-lado-pagina-3-girada"); C.mostrar(j, "uma")
    # o texto do bloco e da lista "aplicar em" (pergunta 1 do agente, ainda aberta)
    from PySide6.QtWidgets import QComboBox, QLabel
    anotar("bloco girar: textos", [w.text() for w in t.barra_girar.findChildren(QLabel)])
    anotar("bloco girar: listas", [[c.itemText(k) for k in range(c.count())] for c in t.barra_girar.findChildren(QComboBox)])
    C.fechar(j)


if __name__ == "__main__":
    main()
