"""Prints e medidas da janela DE VERDADE: o livro aberto "como o UPDF" (22/10/2026).
Abre uma CÓPIA do Graduale (folhas de alturas diferentes: 960 x 1396 e 960 x 1351), clica no
cartão com mensagens do Windows, fotografa os jeitos de mostrar e de caber em 1280 x 657 (print
de 1600 x 821 a 125%) e maximizada (1536 x 816), e mede no print: a altura pintada das duas
folhas do par e a nitidez (pintado / o PDF desenhado direto no mesmo tamanho).
Serve para o código antigo e o novo. Uso: python prints_livro_updf.py <pasta>
(arquivo descartável do agente de layout, em saida_teste/, que o git ignora)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_etapa3 import RESULTADOS, clique_nativo, conferir  # noqa: E402
from prints_layout import ACERVO, TRAB, esperar, nova_janela  # noqa: E402

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtCore import QPoint, QRect  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402

GRADUALE = TRAB / "Graduale (copia).pdf"
shutil.copy2(ACERVO / "Graduale - Saeculum XIV.pdf", GRADUALE)   # o original nunca é aberto
DESTINO = Path(".")
MEDIDAS = []


def em_numpy(pix):
    img = pix.toImage().convertToFormat(QImage.Format_RGB888)
    d = np.frombuffer(img.constBits(), np.uint8, count=img.bytesPerLine() * img.height())
    return d.reshape(img.height(), img.bytesPerLine())[:, :img.width() * 3].reshape(
        img.height(), img.width(), 3).copy()


def foto(janela, nome):
    pix = janela.grab()
    pix.save(str(DESTINO / f"{nome}.png"))
    print(f"  {nome}.png ({pix.width()} x {pix.height()})", flush=True)
    return em_numpy(pix), pix.devicePixelRatio()


def nitidez(img, razao, ret: QRect, indice, margem=6, visivel: QRect | None = None):
    """Laplaciano do pintado / do MuPDF direto no tamanho pintado. `ret` é a página
    inteira (pontos da janela); só a parte `visivel` dela (menos a margem) é comparada,
    a mesma parte nos dois."""
    x0, y0 = round(ret.left() * razao), round(ret.top() * razao)
    w = round((ret.left() + ret.width()) * razao) - x0
    h = round((ret.top() + ret.height()) * razao) - y0
    v = visivel if visivel is not None else ret
    vx0, vy0 = round(v.left() * razao), round(v.top() * razao)
    vx1, vy1 = round((v.left() + v.width()) * razao), round((v.top() + v.height()) * razao)
    m = round(margem * razao)
    vx0, vy0, vx1, vy1 = vx0 + m, vy0 + m, vx1 - m, vy1 - m
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    pintado = cinza[vy0:vy1, vx0:vx1]
    doc = fitz.open(str(GRADUALE))
    p = doc[indice]
    # a referência: o PDF desenhado 4 vezes maior e reduzido por área para o tamanho pintado
    # (o "ideal"; o MuPDF direto, numa folha pequena, serrilha e parece mais nítido do que é)
    px = p.get_pixmap(matrix=fitz.Matrix(4 * w / p.rect.width, 4 * h / p.rect.height),
                      colorspace=fitz.csGRAY, alpha=False)
    ref = np.frombuffer(px.samples, np.uint8).reshape(px.height, px.width)
    ref = cv2.resize(ref, (w, h), interpolation=cv2.INTER_AREA).astype(float)
    doc.close()
    ref = ref[vy0 - y0:vy1 - y0, vx0 - x0:vx1 - x0]
    return cv2.Laplacian(pintado, cv2.CV_64F).std() / cv2.Laplacian(ref, cv2.CV_64F).std()


def na_janela(janela, widget, ret: QRect) -> QRect:
    return QRect(widget.mapTo(janela, ret.topLeft()), ret.size())


def medir_livro(janela, aberto, nome, img, razao):
    """A altura de cada folha na tela e a nitidez da folha da vez."""
    folhas = aberto.paginas.folhas
    vis = folhas.visibleRegion().boundingRect()
    rets = [(i, r) for i, r in aberto.paginas.retangulos() if r.intersects(vis)]
    alturas = {i + 1: round(r.height() * razao) for i, r in rets}
    i, r = next(((i, r) for i, r in rets if i == aberto.paginas.atual), rets[0])
    area = aberto.paginas.viewport().geometry()
    vis_r = r.intersected(vis)
    vis_j = na_janela(janela, folhas, vis_r).intersected(QRect(aberto.paginas.mapTo(janela, area.topLeft()),
                                                              area.size()))
    pilula = QRect(aberto.pilula.mapTo(janela, QPoint(0, 0)), aberto.pilula.size())
    if vis_j.intersects(pilula):             # a pílula fica por cima do canto de baixo
        vis_j.setBottom(pilula.top() - 1)
    n = nitidez(img, razao, na_janela(janela, folhas, r), i, visivel=vis_j)
    linha = f"{nome}: folhas na tela (altura em pixels) {alturas}; nitidez da folha {i + 1}: {n:.2f}"
    MEDIDAS.append(linha)
    print("   ", linha, flush=True)


def principal() -> None:
    from ui.tela_inicio import CartaoDeProjeto

    janela = nova_janela()
    inicio = janela.tela_inicio
    janela.abrir_livro(str(GRADUALE))
    esperar(6)
    janela._voltar_das_opcoes()
    esperar(4)
    cartoes = [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent() is not None]
    clique_nativo(janela, cartoes[0], QPoint(20, 200))
    esperar(5)
    aberto = inicio.livro_aberto
    conferir(inicio.pilha.currentWidget() is aberto, "clique nativo no cartão: o livro aberto")
    novo = hasattr(aberto, "botoes_caber")
    for tamanho, sufixo in (((1280, 657), "1600x821"), ((1536, 816), "maximizada")):
        janela.resize(*tamanho)
        janela.move(-32000, -32000)
        esperar(2)
        aberto.ir_para(300)                    # a folha 301, do miolo
        esperar(8)
        img, razao = foto(janela, f"{sufixo}-1-uma-pagina")
        medir_livro(janela, aberto, f"{sufixo} uma página", img, razao)
        if novo:
            clique_nativo(janela, aberto.botoes_mostrar["duas"])
        else:
            clique_nativo(janela, aberto.botao_lado_a_lado)
        aberto.ir_para(301)                    # o par 302 e 303 (alturas 1396 e 1351 no scan)
        esperar(10)
        conferir(aberto.paginas.lado_a_lado, f"{sufixo}: clique nativo em lado a lado")
        img, razao = foto(janela, f"{sufixo}-2-duas-lado-a-lado")
        medir_livro(janela, aberto, f"{sufixo} lado a lado", img, razao)
        if novo:
            for jeito, n in (("largura", 3), ("altura", 4), ("real", 5)):
                clique_nativo(janela, aberto.botoes_caber[jeito])
                aberto.ir_para(301)
                esperar(10)
                conferir(aberto.paginas.caber == jeito, f"{sufixo}: clique nativo em caber {jeito}")
                img, razao = foto(janela, f"{sufixo}-{n}-duas-caber-{jeito}")
                medir_livro(janela, aberto, f"{sufixo} lado a lado, caber {jeito}", img, razao)
            clique_nativo(janela, aberto.botoes_caber["pagina"])
            clique_nativo(janela, aberto.botao_rolar)
            esperar(8)
            conferir(not aberto.paginas.continuo, f"{sufixo}: clique nativo desliga o rolar sem parar")
            img, razao = foto(janela, f"{sufixo}-6-duas-sem-rolar")
            medir_livro(janela, aberto, f"{sufixo} lado a lado sem rolar", img, razao)
            clique_nativo(janela, aberto.pilula.findChildren(type(aberto.botao_mais))[-1])
            esperar(8)
            conferir(aberto.paginas.atual == 303, f"{sufixo}: a seta da pílula vai ao par seguinte "
                     f"(folha {aberto.paginas.atual + 1})")
            clique_nativo(janela, aberto.botao_rolar)
            clique_nativo(janela, aberto.botoes_mostrar["uma"])
            esperar(2)
        else:
            clique_nativo(janela, aberto.botao_lado_a_lado)
        # a grade "Todas as páginas"
        clique_nativo(janela, aberto.botao_todas)
        esperar(25)
        img, razao = foto(janela, f"{sufixo}-7-todas-as-paginas")
        q = next(q for q in aberto.todas.quadros if q.itens[0].indice == 300)
        aberto.todas.rolagem.ensureWidgetVisible(q)
        esperar(3)
        img, razao = foto(janela, f"{sufixo}-7-todas-as-paginas")
        # a folha pintada, achada no print dentro do quadro (o pergaminho é claro)
        d = na_janela(janela, q.desenho, q.desenho.rect())
        dx0, dy0 = round(d.left() * razao), round(d.top() * razao)
        dx1, dy1 = round((d.left() + d.width()) * razao), round((d.top() + d.height()) * razao)
        cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)[dy0:dy1, dx0:dx1]
        mascara = (cinza > 140).astype(np.uint8)
        n_c, _l, caixas, _c = cv2.connectedComponentsWithStats(mascara)
        achadas = [tuple(int(v) for v in caixas[k][:4]) for k in range(1, n_c)]
        if not achadas or max(c[2] * c[3] for c in achadas) < 5000:
            MEDIDAS.append(f"{sufixo} grade: a folha 301 ainda cinza (não desenhada) depois de 28 s")
            print("   ", MEDIDAS[-1], flush=True)
            aberto._voltar_da_grade(None)
            esperar(2)
            continue
        bx, by, bw, bh = max(achadas, key=lambda c: c[2] * c[3])
        doc = fitz.open(str(GRADUALE))
        pg = doc[300]
        px = pg.get_pixmap(matrix=fitz.Matrix(4 * bh / pg.rect.height, 4 * bh / pg.rect.height),
                           colorspace=fitz.csGRAY, alpha=False)
        doc.close()
        ref = np.frombuffer(px.samples, np.uint8).reshape(px.height, px.width)
        ref = cv2.resize(ref, (bw, bh), interpolation=cv2.INTER_AREA).astype(float)[4:-4, 4:-4]
        pintado = cinza[by:by + bh, bx:bx + bw].astype(float)[4:-4, 4:-4]
        n = cv2.Laplacian(pintado, cv2.CV_64F).std() / cv2.Laplacian(ref, cv2.CV_64F).std()
        MEDIDAS.append(f"{sufixo} grade: folha 301 pintada com {bw} x {bh} pixels; nitidez {n:.2f}")
        print("   ", MEDIDAS[-1], flush=True)
        vis = na_janela(janela, q.desenho, q.desenho.visibleRegion().boundingRect())
        conferir(vis.height() > 100, f"{sufixo}: a folha 301 aparece na grade ({vis.height()} pontos)")
        aberto._voltar_da_grade(None)
        esperar(2)
    janela.resize(1000, 600)                 # a janela mínima
    janela.move(-32000, -32000)
    aberto.ir_para(300)
    esperar(6)
    foto(janela, "minima-1000x600")
    if hasattr(aberto, "botoes_caber"):
        barra = aberto.botoes_caber["real"].parentWidget()
        dentro = all(b.geometry().right() < aberto.pilula.geometry().left()
                     for b in list(aberto.botoes_caber.values()))
        conferir(dentro and aberto.pilula.geometry().right() <= barra.width(),
                 "na janela mínima os botões da barra de baixo e a pílula cabem sem se cobrir")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)
    (DESTINO / "medidas.txt").write_text("\n".join(MEDIDAS) + "\n" + "\n".join(
        ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


if __name__ == "__main__":
    DESTINO = Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    principal()
    print("FIM", flush=True)
