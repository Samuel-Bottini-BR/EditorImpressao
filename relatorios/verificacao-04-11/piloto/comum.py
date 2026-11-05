"""Ajudantes do verificador de 04/11/2026 (verificacao-04-11). Janela de verdade fora da tela,
cliques e teclas por mensagens do Windows (base.py), prints por PrintWindow.

Uso: python comum_<x>.py  -> cada piloto chama abrir(worktree, nome, livro).
"""
from __future__ import annotations

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import base  # noqa: E402

SAIDA = Path(r"D:\programas\EditorImpressao\relatorios\verificacao-04-11")
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LARGURA, ALTURA = 1536, 824
VK_LEFT, VK_RIGHT = 0x25, 0x27
WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON = 0x0204, 0x0205, 0x0002

NOME = ["x"]
LOG = [None]
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG[0].write(linha + "\n"); LOG[0].flush()


def conferir(ok, frase):
    base.conferir(ok, frase)
    LOG[0].write(("OK      " if ok else "FALHOU  ") + frase + "\n"); LOG[0].flush()
    return ok


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, SAIDA / "prints" / NOME[0] / f"{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """Caixas de aviso que abrem por cima: anota o texto, tira print e aperta o botao padrao
    (ou o de `escolher`, se o texto do botao estiver la)."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.escolher = None
        self.vistas = []
        self.t = QTimer(); self.t.setInterval(250); self.t.timeout.connect(self.olhar); self.t.start()

    def olhar(self):
        if self.ocupado:
            return
        from PySide6.QtWidgets import QApplication, QMessageBox
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto") or not isinstance(w, QMessageBox):
                    continue
            except RuntimeError:
                continue
            w.setProperty("_visto", True)
            self.ocupado = True
            try:
                base.esperar(0.6)
                info = {"titulo": w.windowTitle(), "texto": w.text(),
                        "botoes": [b.text() for b in w.buttons()]}
                self.vistas.append(info)
                anotar("caixa", info)
                p(w, "caixa")
                alvo = None
                if self.escolher:
                    lista = self.escolher if isinstance(self.escolher, (list, tuple)) else [self.escolher]
                    for texto in lista:
                        alvo = next((b for b in w.buttons() if b.text() == texto), None)
                        if alvo is not None:
                            break
                b = alvo or w.defaultButton() or w.buttons()[0]
                base.clique(w, b)
            finally:
                self.ocupado = False
            return


def abrir(worktree: str, nome: str, livro: str, limpar=True):
    """Abre o programa da worktree com uma COPIA do livro do acervo, do zero (sem projeto)."""
    NOME[0] = nome
    (SAIDA / "prints" / nome).mkdir(parents=True, exist_ok=True)
    LOG[0] = open(SAIDA / "prints" / nome / "anotacoes.txt", "w", encoding="utf-8")
    trab = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\trab") / nome
    base.preparar(worktree, str(trab), limpar=limpar)
    import configuracoes
    configuracoes.escrever("qualidade_previa", "rapida")
    livros = trab / "livros"; livros.mkdir(exist_ok=True)
    nome_seguro = "".join(c for c in livro if c.isascii() and (c.isalnum() or c in "._- "))
    pdf = livros / nome_seguro.replace(" ", "_")
    if not pdf.exists():
        shutil.copy2(ACERVO / livro, pdf)       # o acervo so e lido
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    t0 = time.time()
    j.abrir_livro(str(pdf))
    anotar("abriu-em-s", esperar_tela(j))
    anotar("livro", {"pdf": pdf.name, "paginas": len(j.projeto.paginas), "folhas": len(j.projeto.folhas),
                     "worktree": worktree})
    return j, porteiro


def esperar_tela(j, limite=300):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)
    return round(time.time() - t, 1)


def esperar_previa(j, limite=60):
    t0 = time.time()
    base.esperar(0.5)
    while time.time() - t0 < limite:
        t = j.tela_conferir
        vis = getattr(t, "visualizadores", {}).get(t.aba_atual) or t.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        base.esperar(0.2)
    base.esperar(1.0)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5); esperar_previa(j)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5); esperar_previa(j)


def ir_pagina(j, numero):
    """Vai a pagina `numero` (1...) clicando a miniatura da tira."""
    t = j.tela_conferir
    i = numero - 1
    mapa = getattr(t.tira, "_miniaturas", [])
    if 0 <= i < len(mapa):
        mini = mapa[i]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(1.0)
    if t.indice_pagina != i:
        anotar("tira-nao-levou; vou pelo programa", {"queria": numero, "estou": t.indice_pagina + 1})
        t.ir_para_pagina(i); base.esperar(1.0)
    esperar_previa(j)


def ctrl(j, tecla_vk, shift=False):
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL, VK_SHIFT = 0x11, 0xA2, 0x10
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    if shift:
        est[VK_SHIFT] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, 0x0100, VK_CONTROL, 1); base.esperar(0.05)
    ext = 0x01000000 if tecla_vk in (VK_LEFT, VK_RIGHT) else 0
    base.user32.PostMessageW(h, 0x0100, tecla_vk, 1 | ext); base.esperar(0.05)
    base.user32.PostMessageW(h, 0x0101, tecla_vk, 0xC0000001 | ext); base.esperar(0.05)
    base.user32.PostMessageW(h, 0x0101, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    est[VK_SHIFT] = 0
    base.user32.SetKeyboardState(est); base.esperar(1.5)


def botao_direito(janela, widget, ponto=None):
    alvo = widget.mapTo(janela, ponto if ponto is not None else widget.rect().center())
    h, lp = int(janela.winId()), base._lp(janela, alvo)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.15)
    base.user32.PostMessageW(h, WM_RBUTTONDOWN, MK_RBUTTON, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, WM_RBUTTONUP, 0, lp); base.esperar(1.0)


def clique_no_menu(menu, ponto):
    h = int(menu.winId())
    lp = base._lp(menu, ponto)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.3)
    base.user32.PostMessageW(h, base.WM_LBUTTONDOWN, base.MK_LBUTTON, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, base.WM_LBUTTONUP, 0, lp); base.esperar(0.8)


def menus_abertos():
    from PySide6.QtWidgets import QApplication, QMenu
    return [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu) and w.isVisible()]


def visualizador(j):
    t = j.tela_conferir
    return getattr(t, "visualizadores", {}).get(t.aba_atual) or t.area_imagem.currentWidget()


def estado(j) -> dict:
    t = j.tela_conferir
    return {"aba": t.aba_atual, "pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1,
            "mostrar": t.mostrar, "feitas": len(t.acoes.feitas) if t.acoes else None,
            "desfazer": t.acoes.descricao_desfazer() if t.acoes else None}


def fechar(j):
    base.fechar(j)
    falhas = [f for ok, f in base.RES if not ok]
    anotar("resultado", f"{len(base.RES) - len(falhas)} de {len(base.RES)} certas; falhas: {falhas}")
    LOG[0].close()


def processar(j, destino: Path, limite=900, nome_print="confirmar"):
    """Aperta "Confirmar e processar" (clique), e na janela "Processar" (JanelaConfirmar) aperta
    "Processar" (clique). O destino fica no projeto antes (a janela abre nele). Espera a tela final
    ou a volta para a area de trabalho. Devolve o indice da tela no fim."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_principal import CONFERIR, FINAL, PROGRESSO
    destino.parent.mkdir(parents=True, exist_ok=True)
    j.projeto.caminho_saida = str(destino)
    feito = {"ok": False}

    def olhar():
        from ui.janela_dos_avisos import JanelaDosAvisos
        for w in QApplication.topLevelWidgets():
            if isinstance(w, JanelaDosAvisos) and w.isVisible() and not w.property("_visto"):
                w.setProperty("_visto", True)
                base.esperar(0.8)
                anotar("janela 'Antes de processar'", {"titulo": w.windowTitle(), "botao": w.botao_continuar.text()})
                p(w, "antes-de-processar")
                base.clique(w, w.botao_continuar)
                return
            if isinstance(w, JanelaConfirmar) and w.isVisible() and not feito["ok"]:
                feito["ok"] = True
                base.esperar(0.8)
                anotar("janela Processar", {"caminho": str(w.caminho)})
                p(w, nome_print)
                base.clique(w, w.botao_processar)
                return
    relogio = QTimer(); relogio.setInterval(300); relogio.timeout.connect(olhar); relogio.start()
    t = j.tela_conferir
    botao = getattr(t, "botao_confirmar", None) or getattr(t, "botao_processar", None)
    if botao is not None and botao.isVisible():
        QTimer.singleShot(50, lambda: base.clique(j, botao))
    else:
        QTimer.singleShot(50, j.processar)
    t0 = time.time()
    viu_progresso = False
    while time.time() - t0 < limite:
        base.esperar(0.5)
        i = j.telas.currentIndex()
        viu_progresso |= i == PROGRESSO
        if feito["ok"] and i in (FINAL,) and time.time() - t0 > 2:
            break
        if feito["ok"] and viu_progresso and i == CONFERIR:
            break
    relogio.stop()
    base.esperar(2)
    anotar("processar terminou", {"tela": j.telas.currentIndex(), "s": round(time.time() - t0, 1)})
    return j.telas.currentIndex()
