"""Verificador, 22/10/2026: o livro aberto "como o UPDF", na janela de verdade.

Caminho: livro novo (cópia do Graduale) aberto pelo programa -> tela "O que fazer" ->
"voltar" (clique nativo) -> cartão do livro (clique nativo) -> livro aberto. O livro aberto
mostra as folhas COMO ESTÃO NO PDF (sem dividir, endireitar, cortar nem filtro: é a vista do
livro, não a da página tratada). Folhas 301 a 305, do miolo.

Mede no PRINT (não nos números do programa): a altura pintada de cada página do par
(achada pela cor, comparando com o fundo) e a nitidez (pintado / o PDF desenhado 4x e reduzido).
Uso: python vlu_livro.py <pasta_de_saida> [--codigo <worktree>]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vlu_comum import (CODIGO, RESULTADOS, TRAB, app, clique_nativo, conferir, copiar, em_numpy,  # noqa: E402
                       esconder, esperar, esperar_ate, memoria_mb, nova_janela, roda_nativa,
                       tamanho_maximizada)

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtCore import QPoint, QPointF, QRect, Qt  # noqa: E402
from PySide6.QtGui import QWheelEvent  # noqa: E402

DESTINO = Path(sys.argv[1])
DESTINO.mkdir(parents=True, exist_ok=True)
GRADUALE = copiar("Graduale - Saeculum XIV.pdf", "Graduale (copia).pdf")
MEDIDAS: list[str] = []


def anotar(linha: str) -> None:
    MEDIDAS.append(linha)
    print("   ", linha, flush=True)


def foto(janela, nome):
    pix = janela.grab()
    pix.save(str(DESTINO / f"{nome}.png"))
    return em_numpy(pix), pix.devicePixelRatio()


def caixa_pintada(img, razao, ret_janela: QRect, fundo):
    """A caixa (x0, y0, x1, y1, em pixels do print) do que foi pintado perto de `ret_janela`,
    achada pela diferença para a cor do fundo."""
    m = 14
    x0 = max(0, round(ret_janela.left() * razao) - m)
    y0 = max(0, round(ret_janela.top() * razao) - m)
    x1 = min(img.shape[1], round((ret_janela.left() + ret_janela.width()) * razao) + m)
    y1 = min(img.shape[0], round((ret_janela.top() + ret_janela.height()) * razao) + m)
    corte = img[y0:y1, x0:x1].astype(int)
    dif = np.abs(corte - np.array(fundo, int)).max(axis=2) > 18
    linhas = np.where(dif.mean(axis=1) > 0.3)[0]
    colunas = np.where(dif.mean(axis=0) > 0.3)[0]
    if len(linhas) == 0 or len(colunas) == 0:
        return None
    return x0 + colunas[0], y0 + linhas[0], x0 + colunas[-1] + 1, y0 + linhas[-1] + 1


def nitidez(img, caixa, indice):
    x0, y0, x1, y1 = caixa
    w, h = x1 - x0, y1 - y0
    m = 6
    pintado = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(float)[m:-m, m:-m]
    doc = fitz.open(str(GRADUALE))
    p = doc[indice]
    px = p.get_pixmap(matrix=fitz.Matrix(4 * w / p.rect.width, 4 * h / p.rect.height),
                      colorspace=fitz.csGRAY, alpha=False)
    doc.close()
    ref = np.frombuffer(px.samples, np.uint8).reshape(px.height, px.width)
    ref = cv2.resize(ref, (w, h), interpolation=cv2.INTER_AREA).astype(float)[m:-m, m:-m]
    return cv2.Laplacian(pintado, cv2.CV_64F).std() / max(1e-6, cv2.Laplacian(ref, cv2.CV_64F).std())


def medir(janela, aberto, nome, img, razao):
    pg = aberto.paginas
    vis = pg.folhas.visibleRegion().boundingRect()
    vp = pg.viewport()
    canto = vp.mapTo(janela, QPoint(4, 4))
    fundo = img[round(canto.y() * razao), round(canto.x() * razao)]
    area = QRect(vp.mapTo(janela, QPoint(0, 0)), vp.size())
    pilula = QRect(aberto.pilula.mapTo(janela, QPoint(0, 0)), aberto.pilula.size())
    alturas = {}
    nit = None
    for i, r in pg.retangulos():
        if not r.intersects(vis):
            continue
        rj = QRect(pg.folhas.mapTo(janela, r.topLeft()), r.size()).intersected(area)
        if rj.height() < 60:
            continue
        cx = caixa_pintada(img, razao, rj, fundo)
        if cx is None:
            alturas[i + 1] = "cinza"
            continue
        inteira = r.intersected(vis) == r
        alturas[i + 1] = (cx[3] - cx[1]) if inteira else f"{cx[3] - cx[1]} (cortada pela tela)"
        if nit is None and i == pg.atual and inteira and not rj.intersects(pilula):
            nit = nitidez(img, cx, i)
    anotar(f"{nome}: alturas pintadas (pixels, achadas no print) {alturas}; "
           f"nitidez da folha {pg.atual + 1}: {('%.2f' % nit) if nit is not None else '-'}")
    return alturas, nit


def roda_simulada(widget, delta):
    """QWheelEvent do Qt (simulado): só quando a roda nativa não chega."""
    centro = QPointF(widget.rect().center())
    ev = QWheelEvent(centro, QPointF(widget.mapToGlobal(widget.rect().center())), QPoint(0, 0),
                     QPoint(0, delta), Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    app.sendEvent(widget, ev)
    esperar(0.5)


def principal():
    from ui.tela_inicio import CartaoDeProjeto

    janela = nova_janela()
    inicio = janela.tela_inicio
    janela.abrir_livro(str(GRADUALE))
    esperar(5)
    opcoes = janela.tela_opcoes
    voltar = next(b for b in opcoes.findChildren(type(opcoes.botao_conferir)) if b.text() == "voltar")
    clique_nativo(janela, voltar)
    esperar(4)
    cartoes = [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent() is not None and c.isVisible()]
    conferir(len(cartoes) >= 1, f"o cartão do livro na tela dos livros ({len(cartoes)})")
    clique_nativo(janela, cartoes[0], QPoint(cartoes[0].width() // 2, cartoes[0].height() // 2))
    esperar(5)
    aberto = inicio.livro_aberto
    conferir(inicio.pilha.currentWidget() is aberto, "um clique nativo no cartão abre o livro")
    novo = hasattr(aberto, "botoes_caber")
    if novo:
        conferir(aberto.botoes_mostrar["uma"].isChecked() and aberto.botao_rolar.isChecked()
                 and aberto.botoes_caber["pagina"].isChecked(),
                 "de fábrica: Uma página + Rolar sem parar + Caber a página")
    mem0 = memoria_mb()
    anotar(f"memória com o livro aberto (programa + processos filhos): {mem0:.0f} MB")
    tamanhos = (((1280, 657), "1600x821"), (tamanho_maximizada(janela), "maximizada"))
    for (w, h), sufixo in tamanhos:
        janela.resize(w, h)
        esconder(janela)
        esperar(2)
        anotar(f"--- {sufixo}: janela {janela.width()} x {janela.height()} pontos "
               f"({round(janela.width() * janela.devicePixelRatioF())} x "
               f"{round(janela.height() * janela.devicePixelRatioF())} pixels)")
        aberto.ir_para(300)
        esperar(6)
        img, razao = foto(janela, f"{sufixo}-1-uma-pagina")
        medir(janela, aberto, f"{sufixo} Uma página, Caber a página", img, razao)
        if novo:
            clique_nativo(janela, aberto.botoes_mostrar["duas"])
        else:
            clique_nativo(janela, aberto.botao_lado_a_lado)
        aberto.ir_para(301)
        esperar(8)
        conferir(aberto.paginas.lado_a_lado, f"{sufixo}: clique nativo em Duas lado a lado")
        img, razao = foto(janela, f"{sufixo}-2-duas")
        medir(janela, aberto, f"{sufixo} Duas lado a lado, Caber a página", img, razao)
        if not novo:
            clique_nativo(janela, aberto.botao_lado_a_lado)
            continue
        for jeito, n, texto in (("altura", 3, "Caber a altura"), ("largura", 4, "Caber a largura"),
                                ("real", 5, "Tamanho real")):
            clique_nativo(janela, aberto.botoes_caber[jeito])
            aberto.ir_para(301)
            esperar(8)
            conferir(aberto.paginas.caber == jeito, f"{sufixo}: clique nativo em {texto}")
            img, razao = foto(janela, f"{sufixo}-{n}-duas-{jeito}")
            medir(janela, aberto, f"{sufixo} Duas lado a lado, {texto}", img, razao)
        clique_nativo(janela, aberto.botoes_caber["pagina"])
        clique_nativo(janela, aberto.botao_rolar)
        esperar(6)
        conferir(not aberto.paginas.continuo, f"{sufixo}: clique nativo desliga Rolar sem parar")
        img, razao = foto(janela, f"{sufixo}-6-duas-sem-rolar")
        medir(janela, aberto, f"{sufixo} Duas lado a lado, sem rolar", img, razao)
        clique_nativo(janela, aberto.botoes_mostrar["uma"])
        esperar(4)
        img, razao = foto(janela, f"{sufixo}-7-uma-sem-rolar")
        medir(janela, aberto, f"{sufixo} Uma página, sem rolar", img, razao)
        clique_nativo(janela, aberto.botao_rolar)
        esperar(2)

    janela.resize(1280, 657)
    esconder(janela)
    esperar(2)
    if novo:
        # --- a roda do mouse ---
        pg = aberto.paginas
        clique_nativo(janela, aberto.botoes_mostrar["uma"])
        clique_nativo(janela, aberto.botao_rolar)          # desliga
        aberto.ir_para(300)
        esperar(4)
        antes = (pg.atual, pg.verticalScrollBar().value())
        for _ in range(3):
            roda_nativa(janela, pg.viewport(), -120)
        depois = (pg.atual, pg.verticalScrollBar().value())
        anotar(f"roda NATIVA (PostMessage WM_MOUSEWHEEL, janela sem foco), sem Rolar sem parar: "
               f"folha/rolagem {antes} -> {depois}")
        nativa_chegou = depois != antes
        conferir(True, f"roda nativa sem foco {'CHEGOU' if nativa_chegou else 'NÃO chegou'} ao programa")
        aberto.ir_para(300)
        esperar(3)
        passos = []
        for _ in range(4):
            roda_simulada(pg.viewport(), -120)
            passos.append(pg.atual + 1)
        anotar(f"roda SIMULADA do Qt (QWheelEvent), Uma página sem rolar, 4 voltinhas para baixo "
               f"a partir da folha 301: folhas {passos}")
        conferir(passos[-1] > 301, "sem Rolar sem parar a roda passa para a página seguinte (simulada)")
        for _ in range(2):
            roda_simulada(pg.viewport(), 120)
        anotar(f"  e 2 voltinhas para cima: folha {pg.atual + 1}, rolagem {pg.verticalScrollBar().value()}"
               f" de {pg.verticalScrollBar().maximum()}")
        clique_nativo(janela, aberto.botoes_mostrar["duas"])
        aberto.ir_para(301)
        esperar(3)
        passos = []
        for _ in range(3):
            roda_simulada(pg.viewport(), -120)
            passos.append(pg.atual + 1)
        anotar(f"roda SIMULADA, Duas lado a lado sem rolar, 3 voltinhas: folha da vez {passos}")
        img, razao = foto(janela, "1600x821-8-duas-sem-rolar-depois-da-roda")
        medir(janela, aberto, "1600x821 Duas sem rolar, depois da roda", img, razao)
        clique_nativo(janela, aberto.botao_rolar)          # liga de novo
        esperar(2)

        # --- memória no Tamanho real, num livro grande (750 folhas, 271 MB) ---
        clique_nativo(janela, aberto.botoes_caber["real"])
        esperar(2)
        pico = memoria_mb()
        inicio_t = time.time()
        for folha in list(range(0, 750, 25)) + list(range(300, 340, 2)):
            aberto.ir_para(folha)
            esperar(1.2)
            pico = max(pico, memoria_mb())
        esperar(5)
        pico = max(pico, memoria_mb())
        guardadas = len(pg.guardadas)
        bytes_g = sum(p.width() * p.height() * 4 for p in pg.guardadas.values()) / 2**20
        anotar(f"Tamanho real, Duas lado a lado, rolando por 50 lugares do livro ({time.time() - inicio_t:.0f} s):"
               f" memória {mem0:.0f} MB no começo, pico {pico:.0f} MB, no fim {memoria_mb():.0f} MB;"
               f" {guardadas} folhas guardadas, {bytes_g:.0f} MB nelas")
        conferir(pico - mem0 < 900, f"memória do Tamanho real não passa de +900 MB ({pico - mem0:.0f})")
        clique_nativo(janela, aberto.botoes_caber["pagina"])
        clique_nativo(janela, aberto.botoes_mostrar["duas"])
        esperar(2)

    # --- a grade "Todas as páginas" ---
    for (w, h), sufixo in tamanhos:
        janela.resize(w, h)
        esconder(janela)
        aberto.ir_para(300)
        esperar(3)
        clique_nativo(janela, aberto.botao_todas)
        q = None
        t = esperar_ate(lambda: next(qq for qq in aberto.todas.quadros if qq.itens[0].indice == 300), 10)
        q = next(qq for qq in aberto.todas.quadros if qq.itens[0].indice == 300)
        aberto.todas.rolagem.ensureWidgetVisible(q)
        t0 = time.time()
        desenhada = esperar_ate(lambda: getattr(q, "imagens", None) or getattr(q.desenho, "pixmap", None)
                                and False, 0.1)
        esperar(1)
        tempos = None
        for _ in range(60):
            img, razao = foto(janela, f"{sufixo}-9-todas-as-paginas")
            d = QRect(q.desenho.mapTo(janela, QPoint(0, 0)), q.desenho.size())
            x0, y0 = round(d.left() * razao), round(d.top() * razao)
            x1, y1 = round((d.left() + d.width()) * razao), round((d.top() + d.height()) * razao)
            cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)[y0:y1, x0:x1]
            masc = (cinza > 140).astype(np.uint8)
            n_c, _l, caixas, _c = cv2.connectedComponentsWithStats(masc)
            achadas = [tuple(int(v) for v in caixas[k][:4]) for k in range(1, n_c)]
            if achadas and max(c[2] * c[3] for c in achadas) > 5000:
                tempos = time.time() - t0
                break
            esperar(0.5)
        if tempos is None:
            anotar(f"{sufixo} grade: a folha 301 ainda cinza depois de 30 s")
        else:
            bx, by, bw, bh = max(achadas, key=lambda c: c[2] * c[3])
            nit = nitidez(img, (x0 + bx, y0 + by, x0 + bx + bw, y0 + by + bh), 300)
            anotar(f"{sufixo} grade Todas as páginas: folha 301 desenhada em {tempos:.1f} s, "
                   f"{bw} x {bh} pixels, nitidez {nit:.2f}")
        aberto._voltar_da_grade(None)
        esperar(2)

    # --- a escolha guardada ---
    if novo:
        clique_nativo(janela, aberto.botoes_mostrar["duas"])
        clique_nativo(janela, aberto.botoes_caber["largura"])
        esperar(1)
        arq = TRAB / "dados" / "EditorImpressao" / "configuracoes.json"
        salvo = json.loads(arq.read_text(encoding="utf-8")).get("livro_aberto") if arq.exists() else None
        anotar(f"configuracoes.json depois de Duas + Caber a largura: {salvo}")
        conferir(salvo == {"mostrar": "duas", "rolar": True, "caber": "largura"},
                 "a escolha foi gravada")
        clique_nativo(janela, aberto.botao_voltar)
        esperar(2)
        janela.close()
        esperar(2)
        janela2 = nova_janela()
        inicio2 = janela2.tela_inicio
        cartoes = [c for c in inicio2.findChildren(CartaoDeProjeto) if c.parent() is not None and c.isVisible()]
        clique_nativo(janela2, cartoes[0], QPoint(cartoes[0].width() // 2, cartoes[0].height() // 2))
        esperar(5)
        ab2 = inicio2.livro_aberto
        conferir(ab2.botoes_mostrar["duas"].isChecked() and ab2.botoes_caber["largura"].isChecked()
                 and ab2.paginas.mostrar == "duas" and ab2.paginas.caber == "largura",
                 "programa fechado e aberto de novo: o livro abre em Duas + Caber a largura")
        foto(janela2, "1600x821-10-reaberto-com-a-escolha")
        janela2.close()
    else:
        janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    (DESTINO / "medidas.txt").write_text(
        f"código: {CODIGO}\n" + "\n".join(MEDIDAS) + "\n\n" + "\n".join(
            ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


principal()
print("FIM", flush=True)
