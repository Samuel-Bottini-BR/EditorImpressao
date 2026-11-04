"""Prints na janela de VERDADE dos ajustes de 03/11/2026 (ramo dividir-ajustes-2026-11-03),
no Gradus Primus, como o verificador clicando de 03/11 (relatorios/verif-03-11/piloto.py).

Janela do Windows posta fora da tela; cliques e teclas por mensagens do Windows ao hwnd
(relatorios/obra-etapa3/roteiro/base.py); prints por PrintWindow. Dados, projetos e TEMP numa
pasta própria no scratchpad (nunca a pasta de dados do Samuel); o PDF do Gradus é COPIADO para
lá (o original só é lido). Janela principal 1536 x 824 (a do verificador e a do Samuel).

Rodar (na cópia dividir-ajustes):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\dividir-ajustes\\piloto.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\ajustes\dados-piloto")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / f"p{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: print, anota o texto e clica no botão pedido."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.responder = "cancelar"
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
                base.esperar(0.8)
                p(w, "caixa-por-cima")
                dados = {"titulo": w.windowTitle(), "texto": w.text(), "mais": w.informativeText(),
                         "botoes": [b.text() for b in w.buttons()]}
                self.vistas.append(dados)
                anotar("caixa", dados)
                escolha = next((b for b in w.buttons() if b.text().startswith(self.responder)),
                               w.buttons()[0])
                anotar("respondi", escolha.text())
                base.clique(w, escolha)
            finally:
                self.ocupado = False
            return


def esperar_tela(j, limite=300):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)


def esperar_linha(j, limite=120):
    from ui.tela_conferir import ABA_CORTE
    vis = j.tela_conferir.visualizadores[ABA_CORTE]
    t = time.time()
    base.esperar(0.5)
    while time.time() - t < limite and vis.lendo_a_linha:
        base.esperar(0.3)
    base.esperar(0.8)


def estado(j):
    from core import avisos
    from ui.tela_conferir import ABA_CORTE
    t, pr = j.tela_conferir, j.projeto
    vis = t.visualizadores[ABA_CORTE]
    folha = pr.folhas[t.indice_folha]
    return {"folha": t.indice_folha + 1, "pagina": t.indice_pagina + 1,
            "dividida": folha.dividir, "linha_da_folha": round(folha.posicao_corte, 4),
            "linha_visivel": vis.corte_visivel, "linha_na_tela": round(vis.posicao_corte, 4),
            "motor": t.combo_jeito_da_folha.currentText(), "botao": t.botao_nao_dividir.text(),
            "paginas": len(pr.paginas), "com_duvida": avisos.quantas_com_duvida(pr)}


def ferramenta_dividir(j):
    from ui.tela_conferir import ABA_CORTE
    t = j.tela_conferir
    tr = t.trilha
    r = tr.retangulos()
    base.clique(j, tr, ponto=r[min(r)].center()); base.esperar(2)
    if t.aba_atual != ABA_CORTE:
        base.tecla(j, ord("D")); base.esperar(2)
    anotar("ferramenta", t.aba_atual)


def indice_na_tira(j, folha_1):
    t = j.tela_conferir
    passos = t._passos_do_dividir() if t._dividir_por_paginas() else None
    if passos is not None:
        for i, pos in enumerate(passos):
            if j.projeto.paginas[pos].folha == folha_1 - 1:
                return i
    return folha_1 - 1


def ir_folha(j, folha_1):
    """Clique na miniatura da folha (a tira rolada até ela, como a mão faria com a barra)."""
    t = j.tela_conferir
    mini = t.tira._miniaturas[indice_na_tira(j, folha_1)]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini); base.esperar(1.0)
    esperar_linha(j)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    base.clique(j, j.tela_conferir.botoes_mostrar[UMA if qual == "uma" else DUAS])
    base.esperar(1.5); esperar_linha(j)


def trocar_motor(j):
    """Abre a lista "motor de corte" com um clique e escolhe a outra opção com outro clique."""
    t = j.tela_conferir
    combo = t.combo_jeito_da_folha
    antes = combo.currentText()
    base.clique(j, combo); base.esperar(0.8)
    view = combo.view()
    popup = view.window()
    alvo = next(i for i in range(combo.count()) if combo.itemText(i) != antes)
    r = view.visualRect(view.model().index(alvo, 0))
    base.clique(popup, view.viewport(), ponto=r.center()); base.esperar(0.8)
    if popup.isVisible():
        popup.hide()
    esperar_linha(j)
    return {"antes": antes, "depois": combo.currentText()}


def ctrl(j, vk):
    import ctypes
    h = int(j.winId())
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[0x11] = est[0xA2] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, 0x11, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, 0x11, 0xC0000001); base.esperar(0.3)
    est[0x11] = est[0xA2] = 0
    base.user32.SetKeyboardState(est); base.esperar(3)


def esperar_dividir_todas(j, limite=600):
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.5)
        if getattr(j.tela_conferir, "_caixa_de_dividir_todas", None) is None:
            break
    base.esperar(3)
    tarefa = getattr(j.tela_conferir, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(120000)
    base.esperar(3)


def tira_mostra_a_escolhida(j):
    tira = j.tela_conferir.tira
    mini = next(m for m in tira._miniaturas if m.selecionada)
    vista = tira.rolagem.viewport()
    canto = mini.mapTo(vista, mini.rect().topLeft())
    return {"numero_da_miniatura": mini.numero,
            "a_vista": 0 <= canto.x() and canto.x() + mini.width() <= vista.width()}


def main():
    base.preparar(str(RAIZ), str(SCRATCH))
    porteiro = Porteiro()
    destino = base.TRAB / "livros" / GRADUS.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GRADUS, destino)
    j = base.nova_janela(1536, 824)
    j.abrir_livro(str(destino))
    esperar_tela(j)
    t = j.tela_conferir
    ferramenta_dividir(j)

    # --- item 3: seta → depois da lista (antes de clicar em qualquer botão do painel) --------
    ir_folha(j, 6)
    base.tecla(j, 0x27); esperar_linha(j)
    anotar("seta direita antes de usar a lista", {"de": 6, "foi_para": t.indice_folha + 1})
    troca = trocar_motor(j)
    anotar("troquei o motor na folha 7", troca)
    base.tecla(j, 0x27); esperar_linha(j)
    anotar("seta direita depois da lista", {"de": 7, "foi_para": t.indice_folha + 1})
    p(j, "item3-seta-depois-da-lista-foi-para-a-folha-8")
    base.tecla(j, 0x25); esperar_linha(j)
    anotar("seta esquerda depois da lista", {"de": 8, "foi_para": t.indice_folha + 1})

    # --- item 1 (D-606): folha 5 dividida, linha acertada, juntada; trocar o motor -----------
    ir_folha(j, 5)
    anotar("folha 5 inteira", estado(j))
    base.clique(j, t.botao_nao_dividir); base.esperar(2)              # dividir esta
    mostrar(j, "duas")
    from ui.tela_conferir import ABA_CORTE
    # a linha acertada "à mão" em 0,44 (pelo programa, como o arrastar: o sinal da linha)
    t.visualizadores[ABA_CORTE].corte_movido.emit(0.44); base.esperar(1.5)
    anotar("folha 5 dividida, linha acertada", estado(j))
    base.clique(j, t.botao_nao_dividir); base.esperar(2)              # não dividir esta
    esperar_linha(j)
    anotar("folha 5 juntada (D-498: a linha de antes)", estado(j))
    p(j, "item1-folha5-juntada-linha-de-antes")
    troca = trocar_motor(j)
    anotar("troquei o motor", troca)
    anotar("folha 5 juntada, motor trocado (D-606)", estado(j))
    p(j, "item1-folha5-juntada-motor-trocado-linha-nova")

    mostrar(j, "uma")

    # --- item 5: "dividir todas" e as dúvidas ------------------------------------------------
    anotar("antes do dividir todas", estado(j))
    base.clique(j, t.botao_dividir_todas)
    esperar_dividir_todas(j)
    anotar("depois do dividir todas", estado(j))
    from core import avisos
    linhas = avisos.linhas_do_para_revisar(j.projeto)
    anotar("as com dúvida", [{"pagina": i + 1, "folha": j.projeto.paginas[i].folha + 1,
                              "metade": j.projeto.paginas[i].metade,
                              "avisos": [a.codigo for a in av]} for _alvo, i, av in linhas])
    ir_folha(j, 7)
    anotar("folha 7, metade esquerda", estado(j))
    p(j, "item5-folha7-metade-em-branco-com-duvida")

    # --- item 4: folha 60, Ctrl+Z, a tira ----------------------------------------------------
    ir_folha(j, 60)
    anotar("folha 60 antes do Ctrl+Z", {**estado(j), **tira_mostra_a_escolhida(j)})
    ctrl(j, ord("Z"))
    base.esperar(3)
    anotar("depois do Ctrl+Z", {**estado(j), **tira_mostra_a_escolhida(j)})
    p(j, "item4-tira-mostra-a-folha-60-depois-do-ctrl-z")
    ctrl(j, ord("Y"))
    base.esperar(3)
    anotar("depois do refazer", {**estado(j), **tira_mostra_a_escolhida(j)})
    p(j, "item4-tira-depois-do-refazer")

    # --- item 2 (D-607): "juntar todas" e o Automático com o Dividir --------------------------
    base.clique(j, t.botao_juntar_todas); base.esperar(3)
    anotar("depois do juntar todas", estado(j))
    from core import automatico as A
    jan = j.abrir_o_automatico(etapa=A.DIVIDIR)
    base.esperar(3)
    j.estado_do_automatico.marcadas = {A.DIVIDIR}
    j.estado_do_automatico.mudou.emit()
    base.esperar(2)
    anotar("frase da janela", jan.frase.text())
    porteiro.responder = "cancelar"
    base.clique(jan, jan.botao_rodar)
    base.esperar(4)
    anotar("depois de cancelar", estado(j))

    # --- item 6: a etapa 6 inteira, janela principal 1536 x 824 -------------------------------
    jan = j.abrir_o_automatico(etapa=A.MARGENS)
    base.esperar(3)
    if jan is not None:
        base.esperar(2)
        rol = jan.painel_de_opcoes.paginas_das_etapas[A.MARGENS]
        anotar("etapa 6", {"janela": [jan.width(), jan.height()],
                           "coluna_do_meio": rol.viewport().width(),
                           "rolagem_de_lado": rol.horizontalScrollBar().maximum()})
        p(jan, "item6-margens-iguais-inteira-1536x824")
        jan.reject(); base.esperar(1)
    j.close(); base.esperar(2)
    LOG.close()


if __name__ == "__main__":
    main()
