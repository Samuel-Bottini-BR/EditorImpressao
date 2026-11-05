"""Verificador 04/11, D-623: pagina em branco posta pelo botao direito, e depois "voltar a pagina"
(o botao que aparece nela). O que sai no PDF? Boecio do acervo (50 paginas)."""
import numpy as np

import comum as C
import p4b_desfazer as B
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\desfazer-pagina"


def main():
    j, porteiro = C.abrir(WT, "5c-pagina-em-branco-voltar", "Sobre a Consolação da Filosofia - Severino Boécio.pdf")
    from ui import desfazer_nesta_pagina as D
    from PySide6.QtWidgets import QPushButton
    t = j.tela_conferir
    C.ferramenta(j, "X"); C.mostrar(j, "uma"); C.ir_pagina(j, 5)
    mini = t.tira._miniaturas[4]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); C.base.esperar(0.4)
    C.botao_direito(j, mini)
    conferir(B.escolher_item(t._menu_desfazer, D.DEPOIS_EM_BRANCO), "pagina em branco depois da 5")
    C.ir_pagina(j, 6)
    pg = j.projeto.paginas[5]
    anotar("pagina 6 posta", {"inserida": pg.inserida, "em_branco": getattr(pg, "em_branco", None),
                              "folha": pg.folha + 1, "metade": pg.metade})
    p(j, "pagina-6-em-branco-no-cortar")
    botoes = [b for b in t.findChildren(QPushButton) if b.text() == "voltar a página" and b.isVisible()]
    anotar("botoes 'voltar a pagina' a vista", len(botoes))
    if botoes:
        C.base.clique(j, botoes[0]); C.base.esperar(2.5); C.esperar_previa(j)
    pg = j.projeto.paginas[5]
    anotar("depois do 'voltar a pagina'", {"inserida": pg.inserida, "em_branco": getattr(pg, "em_branco", None),
                                          "apagada": pg.apagada, "folha": pg.folha + 1,
                                          "paginas": len([q for q in j.projeto.paginas if not q.apagada]),
                                          "ultima": t.acoes.feitas[-1].descricao if t.acoes.feitas else None})
    p(j, "pagina-6-depois-do-voltar")
    t.escolher_ferramenta("filtros"); C.esperar_previa(j); C.base.esperar(2)
    p(j, "pagina-6-como-sai")
    C.ir_pagina(j, 5); p(j, "pagina-5-como-sai")
    # processar e comparar a pagina 6 do PDF com a 5
    destino = C.base.TRAB / "saida" / "Boecio-voltar.pdf"
    C.processar(j, destino)
    import fitz
    with fitz.open(destino) as d:
        anotar("PDF", {"paginas": d.page_count})
        imgs = []
        for i in (4, 5):
            pix = d[i].get_pixmap(dpi=40, colorspace=fitz.csGRAY)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).astype(float)
            imgs.append(a)
            pix.save(str(C.SAIDA / "prints" / C.NOME[0] / f"pdf-pagina-{i + 1}.png"))
        h = min(imgs[0].shape[0], imgs[1].shape[0]); w = min(imgs[0].shape[1], imgs[1].shape[1])
        dif = float(np.abs(imgs[0][:h, :w] - imgs[1][:h, :w]).mean())
        tinta6 = float((imgs[1] < 128).mean() * 100)
        anotar("pagina 6 do PDF", {"diferenca media para a 5": round(dif, 1), "tinta % na 6": round(tinta6, 2)})
        conferir(tinta6 < 0.5, f"a pagina 6 do PDF e branca (tinta {tinta6:.2f}%)")
    C.fechar(j)


if __name__ == "__main__":
    main()
