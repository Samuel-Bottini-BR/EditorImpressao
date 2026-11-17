"""Ajudantes dos pilotos das explicações da Central (17/11/2026). Só LÊ o programa: abre a janela de
VERDADE (JanelaPrincipal) desta worktree fora da tela (-32000), com dados, projetos e TEMP numa pasta
de trabalho no scratchpad; cliques e teclas por mensagens do Windows; prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py, do verificador de 22-23/10). Os livros são CÓPIAS (o
original só é lido). Nenhuma linha do programa muda.
"""
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd"
               r"\fa022b8a-5c74-4934-803d-d9544e30a47d\scratchpad\explicacoes")
VIDA = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf")
CRUS = AQUI / "crus"
LOG = None


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    if LOG is not None:
        LOG.write(linha + "\n")
        LOG.flush()


def preparar(nome: str):
    """Pasta de trabalho própria (no scratchpad) e o caminho do Python na worktree."""
    global LOG
    (CRUS / nome).mkdir(parents=True, exist_ok=True)
    LOG = open(CRUS / nome / "anotacoes.txt", "w", encoding="utf-8")
    base.preparar(str(RAIZ), str(SCRATCH / nome))
    return CRUS / nome


def copia_da_vida(folhas: int = 12, nome: str = "La vida eterna.pdf") -> Path:
    """As primeiras `folhas` folhas do "La vida eterna" numa CÓPIA (o original só é lido)."""
    import fitz
    destino = base.TRAB / "livros" / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        with fitz.open(str(VIDA)) as livro, fitz.open() as novo:
            novo.insert_pdf(livro, from_page=0, to_page=folhas - 1)
            novo.save(str(destino))
    return destino


def esperar_ate(condicao, segundos=120.0) -> bool:
    fim = time.time() + segundos
    while time.time() < fim:
        try:
            if condicao():
                return True
        except Exception:  # noqa: BLE001
            pass
        base.esperar(0.2)
    return bool(condicao())


def abrir(j, pdf: Path, resumo=None):
    j.abrir_livro(str(pdf), resumo=resumo) if resumo is not None else j.abrir_livro(str(pdf))
    base.esperar(2.0)
    esperar_ate(lambda: getattr(j, "medida_ao_abrir", None) is None or not j.medida_ao_abrir.isRunning(), 240)
    base.esperar(1.5)
    responder_caixa(j, "Não")
    return j.tela_conferir


def responder_caixa(j, comeco_do_botao: str):
    """Se uma caixa de pergunta está aberta (ex.: "Este livro tem fundo separado. Quer tirar o
    fundo?" do Palatino), anota o texto e clica no botão que começa com `comeco_do_botao`."""
    from PySide6.QtWidgets import QApplication, QMessageBox
    m = QApplication.activeModalWidget()
    if isinstance(m, QMessageBox):
        anotar("caixa-ao-abrir", {"titulo": m.windowTitle(), "texto": m.text(),
                                  "botoes": [b.text() for b in m.buttons()]})
        b = next((b for b in m.buttons() if b.text().startswith(comeco_do_botao)), m.buttons()[0])
        base.clique(m, b)
        base.esperar(2.0)


def esperar_previa(tela, limite=60.0):
    base.esperar(0.5)
    t0 = time.time()
    while time.time() - t0 < limite:
        vis = getattr(tela, "visualizadores", {}).get(tela.aba_atual) or tela.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        base.esperar(0.2)
    base.esperar(1.5)


def letra(j, l: str):
    vk = base.user32.VkKeyScanW(ord(l.lower())) & 0xFF
    base.tecla(j, vk)
    base.esperar(1.5)


def rodar_automatico(j, etapas: set, esperar_fim=True):
    """Painel Automático: marca SÓ `etapas` (clique na caixinha de cada uma que precisa mudar) e
    clica "Rodar". Espera o fim."""
    from PySide6.QtCore import QPoint

    from core import automatico as A
    tela = j.tela_conferir
    tela.paineis.abrir("automatico")
    base.esperar(0.8)
    painel = tela.paineis.automatico
    lista = painel.lista
    for i in range(lista.count()):
        item = lista.item(i)
        etapa = item.data(0x0100)
        if etapa not in A.ETAPAS:
            etapa = next((e for e in A.ETAPAS if item.text().startswith(A.NOMES[e])), None)
        if etapa is None:
            continue
        quer = etapa in etapas
        if (etapa in painel.estado.marcadas) != quer:
            ret = lista.visualItemRect(item)
            base.clique(j, lista.viewport(), QPoint(ret.left() + 14, ret.center().y()))
            base.esperar(0.4)
    anotar("automatico-marcadas", sorted(painel.estado.marcadas))
    return painel


def clicar_rodar(j, painel, limite=400):
    feitas = len(j.acoes.feitas) if j.acoes else 0
    base.clique(j, painel.botao_rodar)
    esperar_ate(lambda: j.acoes is not None and len(j.acoes.feitas) > feitas
                and j.telas.currentIndex() != 1 and j.tela_conferir._pronta(), limite)
    base.esperar(3.0)


def pdf_das_paginas(projeto, paginas, saida: Path, nome: str, dpi=60) -> list[Path]:
    """As páginas como saem no PDF (core/pipeline.processar numa CÓPIA do projeto, só com
    `paginas`; as outras tiradas na cópia); cada página vira um PNG."""
    import fitz

    from core import pipeline
    c = copy.deepcopy(projeto)
    for pg in c.paginas:
        if pg.indice not in paginas:
            pg.apagada = True
    c.caminho_saida = str(base.TRAB / f"_{nome}.pdf")
    caminho = pipeline.processar(c)
    pngs = []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            png = saida / f"pdf-{nome}-{n + 1}.png"
            pagina.get_pixmap(dpi=dpi).save(str(png))
            pngs.append(png)
    Path(caminho).unlink(missing_ok=True)
    return pngs


def normal(widget):
    """Se o Windows minimizou a janela (o print sai 199x34 e o clique não chega), volta ao normal
    FORA da tela (SW_SHOWNOACTIVATE, depois -32000). Nunca aparece na tela do Samuel."""
    from PySide6.QtCore import Qt
    h = int(widget.window().winId())
    w = widget.window()
    for _ in range(3):
        if not base.user32.IsIconic(h) and not (w.windowState() & Qt.WindowMinimized):
            return
        anotar("janela-minimizada-voltei", type(w).__name__)
        w.setWindowState(w.windowState() & ~Qt.WindowMinimized)
        base.user32.ShowWindow(h, 4)                  # SW_SHOWNOACTIVATE
        w.move(-32000, -32000)
        base.esperar(1.5)


_clique, _arrastar, _tecla = base.clique, base.arrastar, base.tecla


def _clique_normal(janela, widget, ponto=None, duplo=False):
    normal(janela)
    return _clique(janela, widget, ponto, duplo)


def _arrastar_normal(janela, widget, de, para, passos=12):
    normal(janela)
    return _arrastar(janela, widget, de, para, passos)


def _tecla_normal(janela, vk, char=None, vezes=1):
    normal(janela)
    return _tecla(janela, vk, char, vezes)


base.clique, base.arrastar, base.tecla = _clique_normal, _arrastar_normal, _tecla_normal


def p(widget, pasta: Path, nome: str, so_cliente=False):
    """Print da janela (volta ao normal fora da tela antes, se o Windows a minimizou)."""
    normal(widget)
    img = base.print_window(widget, pasta / f"{nome}.png", so_cliente=so_cliente)
    if img is not None and img.width < 400:
        anotar("PRINT-PEQUENO", [nome, img.size])
    return img
