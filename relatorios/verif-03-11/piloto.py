"""Verificador clicando (03/11/2026): os três consertos de hoje (D-602, D-004 no Gradus, D-590),
na janela de VERDADE (plataforma Windows, letras de verdade), posta fora da tela.

Cliques e teclas por mensagens do Windows mandadas ao hwnd da janela (relatorios/obra-etapa3/
roteiro/base.py: PostMessage de WM_LBUTTONDOWN/UP, WM_KEYDOWN/UP); prints por PrintWindow.
Dados, projetos e TEMP numa pasta própria no scratchpad (nunca a pasta de dados do Samuel).
O PDF do Gradus é COPIADO para essa pasta (o original só é lido).

Rodar (na cópia verif-03-11):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\verif-03-11\\piloto.py t1
    (fases: t1, boecio, t2, t3, t3b)
"""
from __future__ import annotations

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\verif-03-11-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
BOECIO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE"
              r"\Sobre a Consolação da Filosofia - Severino Boécio.pdf")
LARGURA, ALTURA = 1536, 824          # o tamanho da janela do Samuel (prints a-51/a-53)
MED: dict = {}
PORTEIROS: list = []
LOG = None
FASE = ""
N = [0]


def anotar(chave, valor=None):
    MED[chave] = valor
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


# --- o porteiro: as janelas que abrem por cima (exec) -------------------------------------

class Porteiro:
    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.n = 0
        self.preferidos = ("entendi", "Pular", "Não, deixar como está", "OK", "Ok")
        self.t = QTimer(); self.t.setInterval(250); self.t.timeout.connect(self.olhar); self.t.start()

    def olhar(self):
        if self.ocupado:
            return
        from PySide6.QtWidgets import QApplication, QMessageBox
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto_pelo_porteiro"):
                    continue
            except RuntimeError:
                continue
            if isinstance(w, QMessageBox):
                w.setProperty("_visto_pelo_porteiro", True)
                self.ocupado = True
                try:
                    base.esperar(0.8)
                    self.n += 1
                    nome = f"{FASE}-por-cima-{self.n:02d}"
                    base.print_window(w, AQUI / "por-cima" / f"{nome}.png", so_cliente=False)
                    textos = [b.text() for b in w.buttons()]
                    anotar(nome, {"titulo": w.windowTitle(), "texto": w.text(),
                                  "mais": w.informativeText(), "botoes": textos})
                    escolha = None
                    for preferido in self.preferidos:
                        escolha = next((b for b in w.buttons() if b.text().startswith(preferido)), None)
                        if escolha:
                            break
                    escolha = escolha or w.defaultButton() or w.buttons()[0]
                    anotar(nome + "-respondi", escolha.text())
                    base.clique(w, escolha)
                finally:
                    self.ocupado = False
                return


# --- abrir e esperar ---------------------------------------------------------------------------

def esperar_tela(j, limite=240):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)
    return round(time.time() - t, 1)


def abrir_pdf(j, origem: Path, nome=None) -> Path:
    destino = base.TRAB / "livros" / (nome or origem.name)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copy2(origem, destino)
    j.abrir_livro(str(destino))
    anotar("abriu-em-s", esperar_tela(j))
    return destino


def ferramenta_dividir(j):
    from ui.tela_conferir import ABA_CORTE
    t = j.tela_conferir
    if t.aba_atual != ABA_CORTE:
        tr = t.trilha
        r = tr.retangulos()
        base.clique(j, tr, ponto=r[min(r)].center()); base.esperar(2)   # 1º botão da trilha: Dividir
        if t.aba_atual != ABA_CORTE:
            anotar("AVISO-trilha-nao-abriu-o-dividir-uso-a-tecla-D", t.aba_atual)
            base.tecla(j, ord("D")); base.esperar(2)
    anotar("ferramenta", t.aba_atual)
    return t.aba_atual == ABA_CORTE


def esperar_linha(j, limite=120):
    from ui.tela_conferir import ABA_CORTE
    vis = j.tela_conferir.visualizadores[ABA_CORTE]
    t = time.time()
    base.esperar(0.5)
    while time.time() - t < limite and vis.lendo_a_linha:
        base.esperar(0.3)
    base.esperar(0.8)
    return round(time.time() - t, 1)


def estado(j):
    from ui.tela_conferir import ABA_CORTE
    t = j.tela_conferir
    pr = j.projeto
    vis = t.visualizadores[ABA_CORTE]
    folha = pr.folhas[t.indice_folha]
    return {
        "folha": t.indice_folha + 1, "pagina": t.indice_pagina + 1, "mostrar": t.mostrar,
        "folha_dividida": folha.dividir, "posicao_corte_da_folha": round(folha.posicao_corte, 4),
        "linha_visivel": vis.corte_visivel, "linha_em": round(vis.posicao_corte, 4),
        "linha_arrastavel": vis.corte_arrastavel, "atualizando": vis.lendo_a_linha,
        "motor": t.combo_jeito_da_folha.currentText(), "lista_motor_ativa": t.combo_jeito_da_folha.isEnabled(),
        "botao": t.botao_nao_dividir.text(),
        "paginas": len(pr.paginas), "vao_ao_pdf": len(pr.paginas_ativas),
        "folhas_divididas": sum(1 for f in pr.folhas if f.dividir),
    }


def indice_na_tira(j, folha_1: int) -> int:
    t = j.tela_conferir
    passos = t._passos_do_dividir() if t._dividir_por_paginas() else None
    if passos is not None:
        for i, pos in enumerate(passos):
            if j.projeto.paginas[pos].folha == folha_1 - 1:
                return i
    mapa = t.tira._mapa_folha
    return min(mapa.get(folha_1 - 1, [folha_1 - 1]))


def ir_folha(j, folha_1: int):
    """Clique na miniatura da folha na tira de baixo (rola a tira até ela, como a mão faria
    com a barra de rolagem)."""
    t = j.tela_conferir
    i = indice_na_tira(j, folha_1)
    mini = t.tira._miniaturas[i]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini)
    base.esperar(1.0)
    if t.indice_folha != folha_1 - 1:
        anotar(f"AVISO-ir-folha-{folha_1}", {"cheguei_em": t.indice_folha + 1, "tira": i})
    return esperar_linha(j)


def seta(j, passo):
    """Seta da barra de baixo (› / ‹)? usamos a tecla de seta do teclado."""
    base.tecla(j, 0x27 if passo > 0 else 0x25); base.esperar(1.0)
    esperar_linha(j)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    t = j.tela_conferir
    b = t.botoes_mostrar[UMA if qual == "uma" else DUAS]
    base.clique(j, b); base.esperar(1.5)
    esperar_linha(j)


def trocar_motor(j, nome_parcial=None):
    """Abre a lista "motor de corte" com um clique e escolhe a outra opção (ou a que tem
    `nome_parcial`) com outro clique no item da lista aberta. Devolve o que aconteceu."""
    from PySide6.QtWidgets import QApplication
    t = j.tela_conferir
    combo = t.combo_jeito_da_folha
    antes = combo.currentText()
    ativa = combo.isEnabled()
    base.clique(j, combo); base.esperar(0.8)
    view = combo.view()
    popup = view.window()
    abriu = popup.isVisible() and popup is not j
    res = {"antes": antes, "lista_ativa": ativa, "abriu": abriu}
    if not abriu:
        res["depois"] = combo.currentText()
        res["trocou"] = False
        return res
    alvo = None
    for i in range(combo.count()):
        txt = combo.itemText(i)
        if (nome_parcial and nome_parcial in txt) or (not nome_parcial and txt != antes):
            alvo = i
            break
    r = view.visualRect(view.model().index(alvo, 0))
    base.clique(popup, view.viewport(), ponto=r.center()); base.esperar(0.8)
    if popup.isVisible():
        popup.hide()
    res["depois"] = combo.currentText()
    res["trocou"] = res["depois"] != antes
    res["espera_linha_s"] = esperar_linha(j)
    return res


def ctrl(j, tecla_vk):
    """Ctrl+tecla: o Ctrl fica "apertado" no estado do teclado deste fio (SetKeyboardState: só
    este programa) e a tecla vai por mensagem do Windows."""
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL = 0x11, 0xA2
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, VK_CONTROL, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, tecla_vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, tecla_vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    base.user32.SetKeyboardState(est); base.esperar(3)


def palavra_jeito(raiz, onde):
    """Procura "jeito" em todo texto e balão dentro de `raiz` (visíveis ou não)."""
    from PySide6.QtWidgets import (QAbstractButton, QComboBox, QLabel, QListWidget, QWidget)
    achados = []
    for w in [raiz] + raiz.findChildren(QWidget):
        textos = [w.toolTip()]
        if isinstance(w, (QAbstractButton, QLabel)):
            textos.append(w.text())
        if isinstance(w, QComboBox):
            textos += [w.itemText(i) for i in range(w.count())]
        if isinstance(w, QListWidget):
            textos += [w.item(i).text() for i in range(w.count())]
        for tx in textos:
            if tx and "jeito" in tx.lower():
                achados.append({"onde": onde, "tipo": type(w).__name__, "visivel": w.isVisible(), "texto": tx})
    return achados


# --- Automático --------------------------------------------------------------------------------

def abrir_painel_automatico(j):
    from ui.widgets.paineis import PAINEL_AUTOMATICO
    pa = j.tela_conferir.paineis
    if not pa.automatico.isVisible():
        ic = pa.icones
        base.clique(j, ic, ponto=ic.retangulos()[PAINEL_AUTOMATICO].center())
        base.esperar(0.8)
    return pa.automatico


def abrir_janela_grande(j, pelo_aviso=False):
    t = j.tela_conferir
    if pelo_aviso and t.aviso_do_livro_novo.isVisible():
        base.clique(j, t.botao_rodar_do_aviso)
        anotar("abri-pelo-aviso-do-livro-novo", True)
    else:
        painel = abrir_painel_automatico(j)
        base.clique(j, painel.botao_janela)
        anotar("abri-pelo-painel", True)
    base.esperar(3)
    jan = j.janela_do_automatico
    assert jan is not None and jan.isVisible(), "a janela grande do Automático não abriu"
    return jan


def _ponto_da_caixinha(lista, item):
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QStyle, QStyleOptionViewItem
    r = lista.visualItemRect(item)
    opt = QStyleOptionViewItem()
    lista.initViewItemOption(opt)
    opt.rect = r
    opt.features |= QStyleOptionViewItem.HasCheckIndicator
    ci = lista.style().subElementRect(QStyle.SE_ItemViewItemCheckIndicator, opt, lista)
    if ci.isValid() and r.contains(ci.center()):
        return ci.center()
    return QPoint(r.left() + 16, r.center().y())


def marcar_etapa(jan, etapa, querer: bool, lista=None):
    from PySide6.QtCore import QPoint, Qt
    lista = lista or jan.painel_de_opcoes.lista
    item = lista.item_da_etapa(etapa)
    if (item.checkState() == Qt.Checked) == querer:
        return querer
    lista.scrollToItem(item); base.esperar(0.2)
    item = lista.item_da_etapa(etapa)
    pontos = [_ponto_da_caixinha(lista, item)]
    r = lista.visualItemRect(item)
    pontos += [QPoint(r.left() + dx, r.top() + 14) for dx in (14, 20, 26)]
    for pt in pontos:
        base.clique(jan, lista.viewport(), ponto=pt)
        item = lista.item_da_etapa(etapa)
        if (item.checkState() == Qt.Checked) == querer:
            return querer
    raise RuntimeError(f"o clique na caixinha de {etapa} não mudou nada")


def mostrar_etapa(jan, etapa):
    from PySide6.QtCore import QPoint
    lista = jan.painel_de_opcoes.lista
    item = lista.item_da_etapa(etapa)
    lista.scrollToItem(item); base.esperar(0.2)
    item = lista.item_da_etapa(etapa)
    r = lista.visualItemRect(item)
    base.clique(jan, lista.viewport(), ponto=QPoint(r.left() + 120, r.top() + 14))
    base.esperar(1.0)


def estado_da_lista(lista):
    from PySide6.QtCore import Qt
    from core import automatico as A
    return {e: ("MARCADA" if lista.item_da_etapa(e).checkState() == Qt.Checked else "desmarcada")
            + " | " + lista.item_da_etapa(e).text().replace("\n", " / ") for e in A.ETAPAS}


def rodar(j, jan):
    from ui.janela_principal import CONFERIR
    from ui.tarefas import TarefaAutomatico
    base.clique(jan, jan.botao_rodar)
    base.esperar(1.0)
    t = time.time()
    viu = False
    while time.time() - t < 1800:
        base.esperar(0.3)
        rodando = isinstance(j.tarefa, TarefaAutomatico) and j.tarefa.isRunning()
        viu = viu or rodando
        pronta = j.telas.currentIndex() == CONFERIR and not rodando
        try:
            janela_aberta = jan.isVisible()
        except RuntimeError:            # a janela grande já foi fechada e apagada
            janela_aberta = False
        if pronta and (viu or (time.time() - t > 30 and not janela_aberta)):
            break
    anotar("rodar-viu-a-tarefa", viu)
    base.esperar(4.0)
    return round(time.time() - t, 1)


def contar(j):
    pr = j.projeto
    from collections import Counter
    por_folha = Counter(pg.folha for pg in pr.paginas)
    metades = Counter((pg.folha, pg.metade) for pg in pr.paginas)
    return {"paginas": len(pr.paginas), "vao_ao_pdf": len(pr.paginas_ativas),
            "folhas_divididas": sum(1 for f in pr.folhas if f.dividir), "folhas": len(pr.folhas),
            "folhas_nao_divididas": [f.indice + 1 for f in pr.folhas if not f.dividir],
            "folhas_com_paginas_diferente_de_2": {k + 1: v for k, v in por_folha.items() if v != 2},
            "metade_repetida": [f"{k[0] + 1}:{k[1]}" for k, v in metades.items() if v > 1]}


# --- Teste 1: D-602 ----------------------------------------------------------------------------

def t1():
    from ui.tela_conferir import ABA_CORTE
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())     # guardado: sem referência o relógio dele some
    abrir_pdf(j, GRADUS)
    t = j.tela_conferir
    p(j, "gradus-aberto-novo")
    anotar("ao-abrir", contar(j))
    if t.aviso_do_livro_novo.isVisible():
        base.clique(j, t.botao_agora_nao); base.esperar(1)
    ferramenta_dividir(j)
    esperar_linha(j)
    anotar("01-folha1", estado(j))
    p(j, "dividir-folha-1-uma-pagina")

    # folha 5 inteira, Uma página
    ir_folha(j, 5)
    anotar("02-folha5-uma", estado(j))
    p(j, "folha-5-inteira-uma-pagina-linha")
    mostrar(j, "duas")
    anotar("03-folha5-duas", estado(j))
    p(j, "folha-5-inteira-duas-lado-a-lado-linha")
    mostrar(j, "uma")
    linha_antes = estado(j)["linha_em"]
    # dividir esta
    base.clique(j, t.botao_nao_dividir); base.esperar(2); esperar_linha(j)
    e = estado(j)
    anotar("04-folha5-depois-de-dividir-esta", {**e, "linha_mostrada_antes": linha_antes,
                                                "cortou_na_linha": abs(e["posicao_corte_da_folha"] - linha_antes) < 0.002})
    p(j, "folha-5-dividir-esta-uma-pagina")
    mostrar(j, "duas")
    anotar("05-folha5-dividida-duas", estado(j))
    p(j, "folha-5-dividida-duas-lado-a-lado")
    mostrar(j, "uma")

    # trocar o motor várias vezes
    trocas = []

    def troca(rotulo):
        r = trocar_motor(j)
        e = estado(j)
        r.update({"rotulo": rotulo, "folha": e["folha"], "dividida": e["folha_dividida"],
                  "linha_visivel": e["linha_visivel"], "linha_em": e["linha_em"],
                  "corte_da_folha": e["posicao_corte_da_folha"], "mostrar": e["mostrar"]})
        trocas.append(r)
        anotar(f"troca-{len(trocas):02d}", r)
        return r

    troca("folha 5 dividida (Uma página)")
    p(j, "motor-trocado-folha-5-dividida")
    troca("folha 5 dividida, de volta")
    mostrar(j, "duas")
    troca("folha 5 dividida (Duas lado a lado)")
    p(j, "motor-trocado-folha-5-dividida-duas")
    troca("folha 5 dividida (Duas), de volta")
    mostrar(j, "uma")
    ir_folha(j, 6)
    troca("folha 6 inteira")
    p(j, "motor-trocado-folha-6-inteira")
    troca("folha 6 inteira, de volta")
    troca("folha 6 inteira, outra vez")
    p(j, "motor-trocado-folha-6-inteira-3a")
    troca("folha 6 inteira, de volta 2")
    # não dividir esta na folha 5 e trocar
    ir_folha(j, 5)
    base.clique(j, t.botao_nao_dividir); base.esperar(2); esperar_linha(j)
    anotar("06-folha5-depois-de-nao-dividir-esta", estado(j))
    p(j, "folha-5-nao-dividir-esta")
    troca("folha 5 depois de 'não dividir esta'")
    troca("folha 5 depois de 'não dividir esta', de volta")
    # dividir de novo e juntar todas
    base.clique(j, t.botao_nao_dividir); base.esperar(2); esperar_linha(j)
    anotar("07-folha5-dividir-esta-de-novo", estado(j))
    ir_folha(j, 7)
    base.clique(j, t.botao_nao_dividir); base.esperar(2); esperar_linha(j)
    anotar("08-folha7-dividir-esta", estado(j))
    base.clique(j, t.botao_juntar_todas); base.esperar(3); esperar_linha(j)
    anotar("09-depois-de-juntar-todas", {**estado(j), **contar(j)})
    p(j, "depois-de-juntar-todas")
    troca("folha 7 depois de 'juntar todas'")
    troca("folha 7 depois de 'juntar todas', de volta")
    ir_folha(j, 8)
    troca("trocou de folha (8)")
    seta(j, +1)
    troca("seta para a folha seguinte")
    p(j, "motor-trocado-depois-da-seta")
    troca("seta, de volta")
    anotar("10-trocas-resumo", {"total": len(trocas), "nao_abriu": [x["rotulo"] for x in trocas if not x["abriu"]],
                                "nao_trocou": [x["rotulo"] for x in trocas if not x["trocou"]],
                                "lista_cinza": [x["rotulo"] for x in trocas if not x["lista_ativa"]]})

    # dividir todas, com "parar" no meio
    ir_folha(j, 1)
    antes_parar = contar(j)
    base.clique(j, t.botao_dividir_todas); base.esperar(1.5)
    caixa = getattr(t, "_caixa_de_dividir_todas", None)
    anotar("11-dividir-todas-caixa", {"abriu": caixa is not None and caixa.isVisible(),
                                     "texto": caixa.labelText() if caixa else None})
    if caixa is not None:
        tt = time.time()
        while time.time() - tt < 120 and caixa.value() < 6:
            base.esperar(0.3)
        p(caixa, "dividir-todas-andamento-antes-de-parar")
        anotar("12-andamento-antes-de-parar", caixa.labelText())
        from PySide6.QtWidgets import QPushButton
        botao_parar = caixa.findChild(QPushButton)
        anotar("12b-botao-parar", botao_parar.text() if botao_parar else None)
        base.clique(caixa, botao_parar); base.esperar(4)
    depois_parar = contar(j)
    anotar("13-depois-de-parar", {"antes": antes_parar, "depois": depois_parar,
                                  "nada_mudou": antes_parar == depois_parar,
                                  "desfazer": j.acoes.feitas[-1].descricao if j.acoes.feitas else ""})
    p(j, "depois-de-parar")
    # dividir todas até o fim
    tt = time.time()
    base.clique(j, t.botao_dividir_todas); base.esperar(1.5)
    caixa = getattr(t, "_caixa_de_dividir_todas", None)
    meio = False
    while time.time() - tt < 1500:
        base.esperar(0.5)
        caixa = getattr(t, "_caixa_de_dividir_todas", None)
        if caixa is None:
            break
        if not meio and caixa.value() >= max(1, caixa.maximum() // 2):
            p(caixa, "dividir-todas-andamento-no-meio")
            anotar("14-andamento-no-meio", caixa.labelText())
            meio = True
    base.esperar(4)
    fim = contar(j)
    anotar("15-dividir-todas-fim", {"segundos": round(time.time() - tt, 1), **fim,
                                    "desfazer": j.acoes.feitas[-1].descricao if j.acoes.feitas else ""})
    p(j, "depois-de-dividir-todas")
    # cada dupla na sua linha: comparar o corte com a leitura do motor
    difs = []
    for f in j.projeto.folhas:
        lida = t._linha_do_motor(f.indice)
        if f.dividir and lida is not None:
            difs.append((f.indice + 1, round(f.posicao_corte, 4), round(lida[0].posicao, 4)))
    fora = [d for d in difs if abs(d[1] - d[2]) > 0.002]
    anotar("16-linhas", {"conferidas": len(difs), "fora_da_linha_lida": fora,
                         "amostra": difs[:12], "posicoes_distintas": len({d[1] for d in difs})})
    mostrar(j, "duas")
    for f in (5, 9, 30, 60):
        ir_folha(j, f)
        anotar(f"17-folha{f}-duas", estado(j))
        p(j, f"dividida-folha-{f}-duas-lado-a-lado")
    mostrar(j, "uma")
    # Ctrl+Z
    ctrl(j, ord("Z"))
    anotar("18-depois-do-ctrl-z", {**contar(j), "ferramenta": t.aba_atual})
    p(j, "depois-do-ctrl-z")
    # "jeito" no Dividir e no Automático
    achados = palavra_jeito(t.paineis if hasattr(t, "paineis") else t, "painel/tela")
    achados += palavra_jeito(t, "tela do conferir")
    jan = abrir_janela_grande(j)
    mostrar_etapa(jan, "dividir")
    p(jan, "automatico-etapa-1")
    achados += palavra_jeito(jan, "janela grande do Automático")
    anotar("19-palavra-jeito", achados)
    base.gravar_textos(jan, AQUI / f"{FASE}-textos.txt", "janela grande, etapa 1")
    base.clique(jan, jan.botao_fechar); base.esperar(1)
    base.gravar_textos(t, AQUI / f"{FASE}-textos.txt", "tela do Dividir")
    base.fechar(j)


def boecio():
    import fitz
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())     # guardado: sem referência o relógio dele some
    livro = base.TRAB / "livros" / "boecio-6-paginas.pdf"
    livro.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(str(BOECIO)) as doc:
        anotar("boecio-original", {"paginas": doc.page_count, "tamanho_p1": [round(doc[0].rect.width), round(doc[0].rect.height)],
                                   "tamanho_p10": [round(doc[min(9, doc.page_count - 1)].rect.width),
                                                   round(doc[min(9, doc.page_count - 1)].rect.height)]})
        novo = fitz.open()
        novo.insert_pdf(doc, from_page=8, to_page=13)
        novo.save(str(livro)); novo.close()
    j.abrir_livro(str(livro))
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    if t.aviso_do_livro_novo.isVisible():
        base.clique(j, t.botao_agora_nao); base.esperar(1)
    ferramenta_dividir(j)
    for f in (1, 3):
        ir_folha(j, f)
        anotar(f"boecio-folha{f}-uma", estado(j))
        p(j, f"boecio-folha-{f}-uma-pagina")
    mostrar(j, "duas")
    anotar("boecio-folha3-duas", estado(j))
    p(j, "boecio-folha-3-duas-lado-a-lado")
    base.fechar(j)


# --- Teste 2: D-004 (defeito do Gradus) --------------------------------------------------------

def t2():
    from core import automatico as A
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())     # guardado: sem referência o relógio dele some
    abrir_pdf(j, GRADUS)
    t = j.tela_conferir
    anotar("aviso-do-livro-novo-visivel", t.aviso_do_livro_novo.isVisible())
    ferramenta_dividir(j)
    for f in (1, 2, 9):
        ir_folha(j, f)
        base.clique(j, t.botao_nao_dividir); base.esperar(2); esperar_linha(j)
        anotar(f"01-dividir-esta-folha-{f}", estado(j))
    anotar("02-depois-de-dividir-a-mao", contar(j))
    p(j, "dividiu-a-mao-1-2-9")
    jan = abrir_janela_grande(j, pelo_aviso=True)
    anotar("03-janela-ao-abrir", estado_da_lista(jan.painel_de_opcoes.lista))
    p(jan, "janela-grande-ao-abrir")
    for e in A.ETAPAS:
        marcar_etapa(jan, e, e == A.DIVIDIR)
    anotar("04-so-dividir", estado_da_lista(jan.painel_de_opcoes.lista))
    anotar("04b-rodar-em", jan.findChild(__import__("ui.automatico", fromlist=["_ComboDoAlcance"])._ComboDoAlcance).currentText())
    anotar("04c-frase", jan.frase.text())
    p(jan, "so-dividir-marcada")
    anotar("05-rodar-s", rodar(j, jan))
    c = contar(j)
    anotar("06-depois-de-rodar-dividir", c)
    ferramenta_dividir(j)
    mostrar(j, "uma")
    for f in range(5, 11):
        ir_folha(j, f)
        anotar(f"07-folha{f}-uma-esq", estado(j))
        p(j, f"rodou-folha-{f}-uma-pagina-esq")
        seta(j, +1)
        anotar(f"07-folha{f}-uma-dir", estado(j))
        p(j, f"rodou-folha-{f}-uma-pagina-dir")
    mostrar(j, "duas")
    for f in range(5, 11):
        ir_folha(j, f)
        anotar(f"08-folha{f}-duas", estado(j))
        p(j, f"rodou-folha-{f}-duas")
    mostrar(j, "uma")
    # a vista normal (Filtro / Mão) com as páginas, em Uma e em Duas
    tr = t.trilha
    r = tr.retangulos()
    base.clique(j, tr, ponto=r[max(r)].center()); base.esperar(2)      # último botão: Mão
    anotar("09-ferramenta-fora-do-dividir", t.aba_atual)
    # ir por clique na tira de páginas
    for numero in (9, 12, 18):
        mini = t.tira._miniaturas[numero - 1]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(2.5)
        p(j, f"rodou-pagina-{numero}-vista-normal-uma")
    mostrar(j, "duas"); base.esperar(2)
    p(j, "rodou-pagina-18-vista-normal-duas")
    mostrar(j, "uma")

    # Margens iguais
    jan = abrir_janela_grande(j)
    anotar("10-janela-reaberta", estado_da_lista(jan.painel_de_opcoes.lista))
    marcar_etapa(jan, A.MARGENS, True)
    mostrar_etapa(jan, A.MARGENS)
    base.esperar(3)
    ad = jan.antes_e_depois
    for _ in range(10):
        base.clique(jan, ad.botao_proxima); base.esperar(0.4)
    tt = time.time()
    while time.time() - tt < 120 and ad.bolinha.isVisible():
        base.esperar(0.5)
    base.esperar(2)
    anotar("11-previa", {"contador": ad.contador.text(), "frase": jan.frase.text(),
                         "lista": estado_da_lista(jan.painel_de_opcoes.lista)})
    p(jan, "margens-marcada-previa-pagina-11")
    anotar("12-rodar-margens-s", rodar(j, jan))
    anotar("13-depois-de-margens", contar(j))
    tamanhos = []
    for pg in j.projeto.paginas[:30]:
        tamanhos.append((pg.folha + 1, pg.metade))
    anotar("13b-primeiras-paginas", tamanhos)
    for numero in (9, 11, 12, 13, 20):
        mini = t.tira._miniaturas[numero - 1]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(2.5)
        p(j, f"margens-pagina-{numero}-uma")
    mostrar(j, "duas"); base.esperar(3)
    p(j, "margens-pagina-20-duas")
    mostrar(j, "uma")
    base.fechar(j)


# --- Teste 3: D-590 (caixinha do Dividir) ------------------------------------------------------

def t3():
    """Continua do t2 (mesma pasta de dados): reabre o livro pela tela inicial."""
    from core import automatico as A
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())     # guardado: sem referência o relógio dele some
    reabrir_pela_tela_inicial(j)
    anotar("00-ao-reabrir", contar(j))
    jan = abrir_janela_grande(j)
    anotar("01-janela-ao-abrir", estado_da_lista(jan.painel_de_opcoes.lista))
    marcar_etapa(jan, A.DIVIDIR, False)
    for e in A.ETAPAS:
        if e != A.MARGENS:
            marcar_etapa(jan, e, False)
    marcar_etapa(jan, A.MARGENS, True)       # algo para rodar
    anotar("02-dividir-desmarcada", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "dividir-desmarcada-antes-de-rodar")
    anotar("03-rodar-s", rodar(j, jan))
    anotar("04-depois-de-rodar", contar(j))
    painel = abrir_painel_automatico(j)
    base.esperar(1)
    anotar("05-painel", {"lista": estado_da_lista(painel.lista)})
    p(j, "painel-depois-de-rodar")
    jan = abrir_janela_grande(j)
    anotar("06-janela-reaberta", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "janela-grande-reaberta")
    base.clique(jan, jan.botao_fechar); base.esperar(1)
    base.fechar(j)


def t3b():
    """Fecha e reabre (processo novo, mesma pasta de dados): continua desmarcada? Depois marca
    de novo e roda."""
    from core import automatico as A
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())     # guardado: sem referência o relógio dele some
    reabrir_pela_tela_inicial(j)
    anotar("00-ao-reabrir", contar(j))
    painel = abrir_painel_automatico(j)
    base.esperar(1)
    anotar("01-painel-ao-reabrir", estado_da_lista(painel.lista))
    p(j, "painel-trabalho-reaberto")
    jan = abrir_janela_grande(j)
    anotar("02-janela-ao-reabrir", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "janela-grande-trabalho-reaberto")
    # juntar todas, para ver o Dividir marcado de novo dividir
    base.clique(jan, jan.botao_fechar); base.esperar(1)
    ferramenta_dividir(j)
    base.clique(j, j.tela_conferir.botao_juntar_todas); base.esperar(3)
    anotar("03-depois-de-juntar-todas", contar(j))
    jan = abrir_janela_grande(j)
    for e in A.ETAPAS:
        marcar_etapa(jan, e, e == A.DIVIDIR)
    anotar("04-dividir-marcada-de-novo", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "dividir-marcada-de-novo")
    anotar("05-rodar-s", rodar(j, jan))
    anotar("06-depois-de-rodar", contar(j))
    painel = abrir_painel_automatico(j)
    base.esperar(1)
    anotar("07-painel", estado_da_lista(painel.lista))
    p(j, "painel-depois-de-rodar-dividir-marcada")
    jan = abrir_janela_grande(j)
    anotar("08-janela-reaberta", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "janela-reaberta-dividir-marcada")
    base.clique(jan, jan.botao_fechar); base.esperar(1)
    base.fechar(j)


def t2m():
    """Retomada (o Samuel parou a rodada no meio): reabre o Gradus do teste 2 pela tela inicial,
    roda Dividir + Margens iguais no livro todo (se a rodada interrompida não ficou gravada) e
    olha as páginas na vista normal e na prévia."""
    from core import automatico as A
    j = base.nova_janela(LARGURA, ALTURA)
    PORTEIROS.append(Porteiro())
    reabrir_pela_tela_inicial(j)
    t = j.tela_conferir
    pr = j.projeto
    anotar("00-ao-reabrir", {**contar(j), "margens_iguais_no_livro": pr.margens_iguais})
    jan = abrir_janela_grande(j)
    anotar("01-janela-ao-abrir", estado_da_lista(jan.painel_de_opcoes.lista))
    for e in A.ETAPAS:
        marcar_etapa(jan, e, e in (A.DIVIDIR, A.MARGENS))
    mostrar_etapa(jan, A.MARGENS)
    ad = jan.antes_e_depois
    # a prévia na página 11 (como no a-51): volta ao começo e anda com ">"
    for _ in range(40):
        if not ad.botao_anterior.isEnabled():
            break
        base.clique(jan, ad.botao_anterior); base.esperar(0.15)
    for _ in range(10):
        base.clique(jan, ad.botao_proxima); base.esperar(0.3)
    tt = time.time()
    base.esperar(2)
    while time.time() - tt < 120 and ad.bolinha.isVisible():
        base.esperar(0.5)
    base.esperar(2)
    anotar("02-previa", {"contador": ad.contador.text(), "frase": jan.frase.text(),
                         "lista": estado_da_lista(jan.painel_de_opcoes.lista)})
    p(jan, "previa-margens-pagina-11")
    for _ in range(6):
        base.clique(jan, ad.botao_anterior); base.esperar(0.3)
    base.esperar(4)
    anotar("02b-previa", ad.contador.text())
    p(jan, "previa-margens-pagina-5")
    anotar("03-rodar-margens-s", rodar(j, jan))
    anotar("04-depois-de-margens", {**contar(j), "margens_iguais_no_livro": j.projeto.margens_iguais})
    tr = t.trilha
    r = tr.retangulos()
    base.clique(j, tr, ponto=r[max(r)].center()); base.esperar(2)      # Mão (vista normal)
    anotar("05-ferramenta", t.aba_atual)
    mostrar(j, "uma") if t.mostrar != "uma" else None
    for numero in (1, 3, 9, 11, 12, 13, 17, 18, 20, 60):
        mini = t.tira._miniaturas[numero - 1]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(3)
        p(j, f"margens-pagina-{numero}-uma")
    mostrar(j, "duas"); base.esperar(3)
    for numero in (12, 18):
        mini = t.tira._miniaturas[numero - 1]
        t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
        base.clique(j, mini); base.esperar(4)
        p(j, f"margens-pagina-{numero}-duas")
    mostrar(j, "uma")
    # o tamanho de cada página como vai sair (para achar folha deitada)
    try:
        from core import margens_iguais as M  # noqa: F401
    except Exception:
        pass
    base.fechar(j)


def t3c():
    """Depois do t3b (folhas juntadas, "Pular as 70" deixou tudo inteiro): Dividir marcada e
    Rodar, respondendo "Rodar nelas também" na pergunta das mexidas."""
    from core import automatico as A
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    porteiro.preferidos = ("Rodar nelas", "entendi", "OK")
    PORTEIROS.append(porteiro)
    reabrir_pela_tela_inicial(j)
    anotar("00-ao-reabrir", contar(j))
    jan = abrir_janela_grande(j)
    for e in A.ETAPAS:
        marcar_etapa(jan, e, e == A.DIVIDIR)
    anotar("01-so-dividir", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "dividir-marcada")
    anotar("02-rodar-s", rodar(j, jan))
    anotar("03-depois-de-rodar", contar(j))
    painel = abrir_painel_automatico(j)
    base.esperar(1)
    anotar("04-painel", {"lista": estado_da_lista(painel.lista)})
    p(j, "painel-depois-de-rodar")
    jan = abrir_janela_grande(j)
    anotar("05-janela-reaberta", {"lista": estado_da_lista(jan.painel_de_opcoes.lista), "frase": jan.frase.text()})
    p(jan, "janela-reaberta")
    base.clique(jan, jan.botao_fechar); base.esperar(1)
    base.fechar(j)


def reabrir_pela_tela_inicial(j):
    from PySide6.QtCore import QPoint
    from ui.janela_principal import CONFERIR
    from ui.tela_inicio import CartaoDeProjeto
    base.esperar(2)
    cartoes = [c for c in j.tela_inicio.findChildren(CartaoDeProjeto) if c.isVisible()]
    anotar("cartoes", [c.resumo.nome for c in cartoes])
    alvo = next(c for c in cartoes if "gradus" in c.resumo.nome.lower())
    base.clique(j, alvo, ponto=QPoint(alvo.width() // 2, 40)); base.esperar(1.5)
    p(j, "tela-inicial-livro-escolhido")
    base.clique(j, j.tela_inicio.livro_aberto.botao_continuar)
    tt = time.time()
    while time.time() - tt < 120 and j.telas.currentIndex() != CONFERIR:
        base.esperar(0.3)
    anotar("reabriu-em-s", esperar_tela(j))


def main():
    global LOG, FASE
    FASE = sys.argv[1] if len(sys.argv) > 1 else "t1"
    pasta = {"t1": "t1", "boecio": "boecio", "t2": "t2b", "t2m": "t2b", "t3": "t2b", "t3b": "t2b", "t3c": "t2b"}[FASE]
    (AQUI / "por-cima").mkdir(parents=True, exist_ok=True)
    LOG = open(AQUI / f"anotacoes-{FASE}.txt", "w", encoding="utf-8")
    trab = SCRATCH / pasta
    base.preparar(str(RAIZ), str(trab), limpar=False)
    try:
        {"t1": t1, "boecio": boecio, "t2": t2, "t2m": t2m, "t3": t3, "t3b": t3b, "t3c": t3c}[FASE]()
    except Exception:
        import traceback
        anotar("ERRO", traceback.format_exc())
        try:
            from PySide6.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                if w.isVisible():
                    base.print_window(w, AQUI / "por-cima" / f"{FASE}-erro-{type(w).__name__}.png", so_cliente=False)
            for w in QApplication.topLevelWidgets():
                if w.isVisible() and w.isWindow():
                    base.user32.PostMessageW(int(w.winId()), base.WM_CLOSE, 0, 0)
            base.esperar(2)
        except Exception:
            pass
        raise
    finally:
        (AQUI / f"anotacoes-{FASE}.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1, default=str),
                                                     encoding="utf-8")
    print("fim", flush=True)


if __name__ == "__main__":
    main()
