"""Verificador 04/11, complemento do mover-lado: no "antes / depois", qual lado mostra o antes e qual
o depois, e onde o Mover age. Palatino, pagina 9 em Preto e branco (para ver os lados)."""
import numpy as np

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\mover-lado"


def lados(j):
    """Cor media da metade esquerda e da direita da pagina desenhada (saturacao ~ 0 = P&B)."""
    from PySide6.QtCore import QPoint
    t = j.tela_conferir
    vista = t.vista_antes_depois
    img = vista.grab().toImage()
    e = img.width() / max(1, vista.width())
    area = vista._area(vista.depois)
    saida = {}
    for nome, fx in (("esquerda", 0.15), ("direita", 0.85)):
        cores = []
        for fy in (0.2, 0.4, 0.6, 0.8):
            for dx in (-0.05, 0, 0.05):
                x = int((area.left() + (fx + dx) * area.width()) * e); y = int((area.top() + fy * area.height()) * e)
                c = img.pixelColor(x, y); cores.append((c.red(), c.green(), c.blue()))
        a = np.array(cores, float)
        saida[nome] = round(float((a.max(axis=1) - a.min(axis=1)).mean()), 1)   # quanto colorido
    saida["linha"] = round(vista.posicao, 2)
    return saida


def main():
    j, porteiro = C.abrir(WT, "2b-antes-depois", "Giovambattista Palatino cittadino romano.pdf")
    t = j.tela_conferir
    C.ir_pagina(j, 9)
    t._escolher_filtro("preto_e_branco"); C.esperar_previa(j)
    t.escolher_ferramenta("filtros"); C.esperar_previa(j)
    C.base.clique(j, t.botao_antes_depois); C.base.esperar(5)
    anotar("Filtro com antes/depois: cor de cada lado (0 = preto e branco)", lados(j))
    p(j, "filtro-antes-depois")
    C.ferramenta(j, "F"); C.base.esperar(4)
    anotar("Mover com antes/depois: cor de cada lado", lados(j))
    p(j, "mover-antes-depois")
    vista = t.vista_da_pagina.currentWidget()
    av = t.vista_antes_depois
    area = av._area(av.depois)
    from PySide6.QtCore import QPoint
    pg = j.projeto.paginas[8]
    # arrasto do lado DIREITO (rotulo "depois")
    de = av.mapTo(vista, QPoint(int(area.left() + 0.8 * area.width()), int(area.center().y())))
    C.base.arrastar(j, vista, de, QPoint(de.x() - 60, de.y())); C.base.esperar(3)
    anotar("arrasto do lado direito (rotulo 'depois')", {"desloc": pg.conteudo_deslocamento})
    d_dir = tuple(pg.conteudo_deslocamento)
    # arrasto do lado ESQUERDO (rotulo "antes")
    de = av.mapTo(vista, QPoint(int(area.left() + 0.2 * area.width()), int(area.center().y())))
    C.base.arrastar(j, vista, de, QPoint(de.x() - 60, de.y())); C.base.esperar(4)
    anotar("arrasto do lado esquerdo (rotulo 'antes')", {"desloc": pg.conteudo_deslocamento})
    p(j, "mover-depois-de-arrastar-a-esquerda")
    conferir(d_dir == (0.0, 0.0), "arrastar do lado com o rotulo 'depois' nao move nada")
    conferir(pg.conteudo_deslocamento[0] < -0.02, "arrastar do lado com o rotulo 'antes' move a pagina")
    anotar("rotulos", {"esquerda": getattr(av, "rotulo_esquerda", None), "textos": [w.text() for w in av.findChildren(type(t.rotulo_da_pagina))]})
    C.fechar(j)


if __name__ == "__main__":
    main()
