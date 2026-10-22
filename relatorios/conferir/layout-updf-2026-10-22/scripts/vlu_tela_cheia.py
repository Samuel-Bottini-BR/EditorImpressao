"""Verificador, 22/10/2026: os filtros em tela cheia com todas as opções, na janela de verdade.

Caminho inteiro do livro novo: cópia do Boécio aberta pelo programa -> tela "O que fazer" com os
ajustes de fábrica -> "Conferir" (clique nativo) -> análise (dividir/endireitar/cortar de fábrica)
-> página 7 do PDF (miolo) -> painel Filtro -> ícone da tela cheia (clique nativo).
O "exec" da tela cheia é trocado por um "show" fora da tela (senão o roteiro fica parado dentro
dela); todo o resto é o programa de verdade.
Mede: as opções de cada filtro; quanto cada opção muda a página grande; e se a página grande é
igual à do PDF gerado de verdade (core.pipeline.processar, o mesmo do botão Processar).
Uso: python vlu_tela_cheia.py <pasta_de_saida> [--codigo <worktree>]"""
import copy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vlu_comum import (CODIGO, RESULTADOS, TRAB, app, clique_nativo, conferir, copiar, em_numpy,  # noqa: E402
                       esconder, esperar, esperar_ate, nova_janela, tamanho_maximizada)

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtCore import QPoint, Qt  # noqa: E402

DESTINO = Path(sys.argv[1])
DESTINO.mkdir(parents=True, exist_ok=True)
BOECIO = copiar("Sobre a Consolação da Filosofia - Severino Boécio.pdf", "Boecio (copia).pdf")
MEDIDAS: list[str] = []
ABERTAS = []
PAGINA = 6          # a página 7 do PDF (miolo, página-gabarito boecio-007)


def anotar(linha: str) -> None:
    MEDIDAS.append(linha)
    print("   ", linha, flush=True)


def foto(widget, nome):
    pix = widget.grab()
    pix.save(str(DESTINO / f"{nome}.png"))
    return em_numpy(pix)


def mudou(a, b) -> float:
    """% dos pontos que mudaram de verdade (mais de 40 níveis em algum canal)."""
    if a is None or b is None:
        return float("nan")
    if a.shape != b.shape:
        return 100.0
    dif = np.abs(a.astype(int) - b.astype(int))
    if dif.ndim == 3:
        dif = dif.max(axis=2)
    return 100.0 * (dif > 40).mean()


def principal():
    from core import preto_e_branco_scantailor as pbst
    from core import pontinhos_scantailor as pontinhos
    from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    def exec_sem_travar(self):
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        esconder(self)
        self.show()
        esconder(self)
        ABERTAS.append(self)
        return 0

    FiltrosEmTelaCheia.exec = exec_sem_travar
    janela = nova_janela()
    janela.abrir_livro(str(BOECIO))
    esperar(4)
    opcoes = janela.tela_opcoes
    foto(janela, "0-o-que-fazer-de-fabrica")
    clique_nativo(janela, opcoes.botao_conferir)
    t = esperar_ate(lambda: janela.trabalho_carregado and janela.tela_conferir.isVisible(), 240, 0.5)
    conferir(t >= 0, f"clique nativo em Conferir: análise do livro novo terminou ({t:.0f} s)")
    esperar(3)
    projeto = janela.projeto
    tela = janela.tela_conferir
    pag = projeto.paginas[PAGINA]
    from core.pipeline import angulo_da_pagina
    try:
        ang = angulo_da_pagina(projeto, pag)
    except Exception:  # noqa: BLE001
        ang = "?"
    caminho = (f"livro novo, ajustes de fábrica: dividir={projeto.dividir_folhas}, "
               f"endireitar={projeto.endireitar}, cortar={projeto.cortar_bordas}, "
               f"ordem={projeto.ordem_do_preparo}; {len(projeto.paginas)} páginas; página 7: ângulo "
               f"{ang}, recorte {pag.recorte}, filtro de fábrica {pag.filtro}")
    anotar(caminho)
    tela.ir_para_pagina(PAGINA)
    esperar(6)
    icones = tela.paineis.icones
    clique_nativo(janela, icones, icones.retangulos()["filtro"].center())
    esperar(3)
    painel = tela.paineis.filtro_da_pagina
    clique_nativo(janela, painel.cartoes[PRETO_E_BRANCO])
    esperar(6)
    conferir(pag.filtro == PRETO_E_BRANCO, "clique nativo no cartão Preto e branco do painel")
    parte = painel.partes["mais"]
    if not parte.corpo.isVisible():
        parte.alternar()
    esperar(2)
    foto(janela, "1-painel-filtro-preto-e-branco-mais-ajustes")
    # --- a tela cheia ---
    clique_nativo(janela, painel.botao_tela_cheia)
    esperar(4)
    conferir(len(ABERTAS) == 1, "clique nativo no ícone do título do painel abre a tela cheia")
    d = ABERTAS[0]
    d.resize(1280, 657)
    esconder(d)
    esperar_ate(lambda: d._imagem(PRETO_E_BRANCO) is not None, 60)
    esperar(2)
    # as opções de cada filtro
    jeitos = [d.seletor_algoritmo_pb.itemText(i) for i in range(d.seletor_algoritmo_pb.count())
              if d.seletor_algoritmo_pb.itemData(i) is not None]
    dados = [d.seletor_algoritmo_pb.itemData(i) for i in range(d.seletor_algoritmo_pb.count())]
    do_st = [x for x in dados if x in pbst.CODIGOS]
    anotar(f"Jeito do preto e branco: {len(jeitos)} itens: {jeitos}")
    conferir(len(do_st) == 10, f"os 10 jeitos do ScanTailor na lista ({len(do_st)})")
    limpezas = [d.seletor_pontinhos.itemText(i) for i in range(d.seletor_pontinhos.count())]
    anotar(f"Limpar a sujeira: {limpezas}")
    for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
        clique_nativo(d, d.cartoes[filtro])
        esperar_ate(lambda f=filtro: d._imagem(f) is not None, 60)
        esperar(1.5)
        vis = [t for t, w in d.partes_das_opcoes.items() if not w.isHidden()]
        caixas = [c.text() for k, c in d.caixas.items() if not c.isHidden()]
        jeito_vis = not d.seletor_algoritmo_pb.isHidden()
        anotar(f"tela cheia, {filtro}: partes {vis}; caixinhas {caixas}; "
               f"jeito do preto e branco {'aparece' if jeito_vis else 'não aparece'}; "
               f"ajuste {'aparece' if d.medidor.isVisible() else 'não aparece'}")
        conferir(d.escolhido == filtro, f"clique nativo no cartão {filtro} da tela cheia")
        foto(d, f"2-tela-cheia-{filtro}-1600x821")
    # --- quanto cada opção muda a página grande ---
    clique_nativo(d, d.cartoes[PRETO_E_BRANCO])
    base = None
    esperar_ate(lambda: d._imagem(PRETO_E_BRANCO) is not None, 60)
    base = d._imagem(PRETO_E_BRANCO).copy()

    def com(filtro, mexer, desfazer, nome):
        mexer()
        t0 = time.time()
        esperar_ate(lambda: d._imagem(filtro) is not None, 90)
        img = d._imagem(filtro)
        img = None if img is None else img.copy()
        pct = mudou(base_de[filtro], img)
        anotar(f"  {filtro} + {nome}: {pct:.2f}% dos pontos mudam ({time.time() - t0:.1f} s)")
        desfazer()
        esperar(0.3)
        return img, pct

    base_de = {PRETO_E_BRANCO: base}
    efeitos = {}
    cx = d.caixas
    efeitos["só as letras"] = com(PRETO_E_BRANCO, lambda: d.escolhas_misto.caixa.setChecked(True),
                                  lambda: d.escolhas_misto.caixa.setChecked(False), "Só as letras")
    for chave in pontinhos.ESCOLHAS:
        if chave == pontinhos.escolha_da_pagina(projeto, pag):
            continue
        i = d.seletor_pontinhos.findData(chave)
        efeitos[f"limpar {chave}"] = com(
            PRETO_E_BRANCO, lambda i=i: d.seletor_pontinhos.setCurrentIndex(i),
            lambda: d.seletor_pontinhos.setCurrentIndex(d.seletor_pontinhos.findData(
                pontinhos.escolha_da_pagina(projeto, pag))), f"Limpar a sujeira: {d.seletor_pontinhos.itemText(i)}")
    volta_jeito = d.seletor_algoritmo_pb.currentIndex()
    for codigo in pbst.CODIGOS:
        i = d.seletor_algoritmo_pb.findData(codigo)
        efeitos[codigo] = com(PRETO_E_BRANCO, lambda i=i: d.seletor_algoritmo_pb.setCurrentIndex(i),
                              lambda: d.seletor_algoritmo_pb.setCurrentIndex(volta_jeito),
                              f"jeito {pbst.NOMES_NA_TELA[codigo]}")
    for campo in ("claro_no_escuro", "letras_com_a_cor", "reduzir_cores"):
        efeitos[campo] = com(PRETO_E_BRANCO, lambda c=campo: cx[c].setChecked(True),
                             lambda c=campo: cx[c].setChecked(False), cx[campo].text())
    efeitos["letras+reduzir"] = com(
        PRETO_E_BRANCO, lambda: (cx["letras_com_a_cor"].setChecked(True), cx["reduzir_cores"].setChecked(True)),
        lambda: (cx["reduzir_cores"].setChecked(False), cx["letras_com_a_cor"].setChecked(False)),
        "Letras com a cor delas + Reduzir cores")
    for filtro in (MELHORAR, MAGICO_PRO):
        clique_nativo(d, d.cartoes[filtro])
        esperar_ate(lambda f=filtro: d._imagem(f) is not None, 90)
        base_de[filtro] = d._imagem(filtro).copy()
        for campo in ("claro_no_escuro", "reduzir_cores"):
            efeitos[f"{filtro} {campo}"] = com(filtro, lambda c=campo: cx[c].setChecked(True),
                                               lambda c=campo: cx[c].setChecked(False), cx[campo].text())
    conferir(not d.opcoes, f"depois de desmarcar tudo, nada fica mexido ({d.opcoes})")
    # --- prints com opções mexidas, nas duas janelas ---
    clique_nativo(d, d.cartoes[PRETO_E_BRANCO])
    esperar(2)
    clique_nativo(d, d.escolhas_misto.caixa, QPoint(8, d.escolhas_misto.caixa.height() // 2))
    i_normal = d.seletor_pontinhos.findData(pontinhos.NORMAL)
    d.seletor_pontinhos.setCurrentIndex(i_normal)
    d.seletor_algoritmo_pb.setCurrentIndex(d.seletor_algoritmo_pb.findData("st_wolf"))
    esperar_ate(lambda: d._imagem(PRETO_E_BRANCO) is not None, 90)
    esperar(2)
    conferir(d.opcoes.get("misto_so_as_letras") is True, "clique nativo em Só as letras na tela cheia")
    mexidas = dict(d.opcoes)
    anotar(f"mexido na tela cheia: {mexidas}")
    vista = d._imagem(PRETO_E_BRANCO).copy()
    foto(d, "3-tela-cheia-pb-opcoes-mexidas-1600x821")
    w, h = tamanho_maximizada(janela)
    d.resize(w, h)
    esconder(d)
    esperar(3)
    foto(d, "3-tela-cheia-pb-opcoes-mexidas-maximizada")
    # a lista dos jeitos aberta
    d.seletor_algoritmo_pb.showPopup()
    esperar(1)
    try:
        d.seletor_algoritmo_pb.view().window().grab().save(str(DESTINO / "4-lista-dos-jeitos.png"))
    finally:
        d.seletor_algoritmo_pb.hidePopup()
    esperar(0.5)
    # --- Usar: grava; e o PDF gerado de verdade ---
    clique_nativo(d, d.botao_usar)
    esperar(3)
    conferir(pag.filtro == PRETO_E_BRANCO and pag.algoritmo_preto_branco == "st_wolf",
             "clique nativo em Usar: as opções gravadas na página")
    esperar(2)
    foto(janela, "5-depois-de-usar-a-pagina-no-programa")
    from core.pipeline import processar
    copia = copy.deepcopy(projeto)
    copia.caminho_saida = str(TRAB / "saida-boecio.pdf")
    copia.montar_cadernos = False
    t0 = time.time()
    saida = processar(copia)
    anotar(f"PDF gerado por core.pipeline.processar (o do botão Processar) em {time.time() - t0:.0f} s: {saida}")
    doc = fitz.open(saida)
    # a página 7 do livro é a 7ª do PDF de saída se nada foi apagado nem dividido antes dela
    antes_dela = [p for p in copia.paginas[:PAGINA] if not getattr(p, "apagada", False)]
    n_saida = len(antes_dela)
    pg = doc[n_saida]
    hv, wv = vista.shape[:2]
    pix = pg.get_pixmap(matrix=fitz.Matrix(4 * wv / pg.rect.width, 4 * hv / pg.rect.height),
                        colorspace=fitz.csRGB, alpha=False)
    ref = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    ref = cv2.resize(ref, (wv, hv), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(DESTINO / "6-pdf-gerado-pagina-7.png"), cv2.cvtColor(ref, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(DESTINO / "6-tela-cheia-pagina-7.png"), cv2.cvtColor(
        vista if vista.ndim == 3 else cv2.cvtColor(vista, cv2.COLOR_GRAY2RGB), cv2.COLOR_RGB2BGR))
    v = vista if vista.ndim == 2 else cv2.cvtColor(vista, cv2.COLOR_RGB2GRAY)
    r = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
    tinta_v, tinta_r = (v < 128), (r < 128)
    so_tela = (tinta_v & ~cv2.dilate(tinta_r.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)).sum()
    so_pdf = (tinta_r & ~cv2.dilate(tinta_v.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)).sum()
    anotar(f"tela cheia ({wv} x {hv}, {pg.rect.width:.0f} x {pg.rect.height:.0f} pt no PDF) x PDF gerado no mesmo "
           f"tamanho: tinta na tela {tinta_v.mean() * 100:.2f}%, no PDF {tinta_r.mean() * 100:.2f}%; "
           f"tinta só na tela (longe de tinta do PDF) {so_tela} pontos = {100 * so_tela / max(1, tinta_v.sum()):.1f}% "
           f"da tinta; só no PDF {so_pdf} pontos = {100 * so_pdf / max(1, tinta_r.sum()):.1f}%")
    dif = np.zeros((hv, wv, 3), np.uint8) + 255
    dif[tinta_v & tinta_r] = (0, 0, 0)
    dif[tinta_v & ~tinta_r] = (220, 0, 0)      # vermelho: só na tela
    dif[~tinta_v & tinta_r] = (0, 90, 255)     # azul: só no PDF
    cv2.imwrite(str(DESTINO / "6-diferenca-tela-x-pdf.png"), cv2.cvtColor(dif, cv2.COLOR_RGB2BGR))
    doc.close()
    # --- achado do core (só registrar): a primeira vez que uma página é desenhada ---
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    fresco = copy.deepcopy(projeto)
    p20 = fresco.paginas[20]
    doc = abrir_pdf(str(BOECIO))
    try:
        a, _ = renderizar_pagina(doc, fresco, p20, dpi=100)
        b, _ = renderizar_pagina(doc, fresco, p20, dpi=100)
    finally:
        doc.close()
    igual = a.shape == b.shape and np.array_equal(a, b)
    anotar(f"página 21 desenhada duas vezes seguidas (cópia do livro): "
           f"{'iguais' if igual else ('tamanhos ' + str(a.shape) + ' e ' + str(b.shape)) if a.shape != b.shape else 'diferentes em ' + str(int((a != b).any(axis=-1).sum() if a.ndim == 3 else (a != b).sum())) + ' pontos'}")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    (DESTINO / "medidas.txt").write_text(
        f"código: {CODIGO}\n" + "\n".join(MEDIDAS) + "\n\n" + "\n".join(
            ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


principal()
print("FIM", flush=True)
