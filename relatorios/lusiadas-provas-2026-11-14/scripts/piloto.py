"""Verificador, 14/11/2026: o caminho do Kaique no Lusíadas, na versão de teste de hoje (c7e34fd8),
para reproduzir os erros D-678 a D-690. Só estudo: nada do programa muda.

Janela de VERDADE (plataforma Windows), posta fora da tela (-32000); cliques, teclas e arrastos por
mensagens do Windows ao hwnd; prints por PrintWindow (relatorios/obra-etapa3/roteiro/base.py).
Dados do programa, projetos e TEMP em relatorios/lusiadas-provas-2026-11-14/_dados (fora do git).
O livro é uma CÓPIA (de _livro/lusiadas.pdf para _dados/livros/).

Uso (na cópia lusiadas-provas):
    .venv\\Scripts\\python.exe relatorios\\lusiadas-provas-2026-11-14\\scripts\\piloto.py <fase>
Fases: a (abrir, Automático como a rodada 1 do Kaique, olhar a tela, tirar/branco/propriedades,
processar duas vezes), b (o Automático de novo: lista e Margens iguais), ...
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent                      # relatorios/lusiadas-provas-2026-11-14
RAIZ = PASTA.parents[1]                  # a cópia (worktree)
import os  # noqa: E402
# CODIGO=<pasta de outra cópia>: roda o MESMO caminho no código de outra versão (ex.: a do teste do
# Kaique, 51bdcb0b), com outra pasta de dados (_dados-<nome da cópia>)
if os.environ.get("CODIGO"):
    RAIZ = Path(os.environ["CODIGO"]).resolve()
sys.path.insert(0, str(PASTA.parents[1] / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

TRAB = PASTA / ("_dados" if not os.environ.get("CODIGO") else f"_dados-{RAIZ.name}")
LIVRO = PASTA / "_livro" / "lusiadas.pdf"
CRUS = PASTA / "prints" / "crus"
FASE = sys.argv[1] if len(sys.argv) > 1 else "a"
LARGURA, ALTURA = 1582, 860
LOG = None
N = [0]


def anotar(chave, valor=None):
    linha = f"{time.strftime('%H:%M:%S')} {chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, CRUS / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas QMessageBox que abrem por cima: print, texto anotado, e o botão preferido."""

    def __init__(self, preferidos=("Pular", "entendi", "Não, deixar como está", "OK", "Ok")):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.n = 0
        self.preferidos = preferidos
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
                self.n += 1
                base.print_window(w, CRUS / f"{FASE}-caixa-{self.n:02d}.png", so_cliente=False)
                anotar(f"caixa-{self.n}", {"titulo": w.windowTitle(), "texto": w.text(),
                                           "mais": w.informativeText(), "botoes": [b.text() for b in w.buttons()]})
                escolha = None
                for pref in self.preferidos:
                    escolha = next((b for b in w.buttons() if b.text().startswith(pref)), None)
                    if escolha:
                        break
                escolha = escolha or w.defaultButton() or w.buttons()[0]
                anotar(f"caixa-{self.n}-respondi", escolha.text())
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
    return round(time.time() - t, 1)


def abrir(j):
    destino = TRAB / "livros" / "lusiadas.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copy2(LIVRO, destino)
    j.abrir_livro(str(destino))
    anotar("abriu-em-s", esperar_tela(j))
    return destino


# --- o que a tela mostra -------------------------------------------------------------------------

def sino(j):
    t = j.tela_conferir
    from core import avisos as avisos_do_livro
    pr = j.projeto
    return {"sino": getattr(t.paineis.icones, "contagem", None),
            "quantas_com_duvida": avisos_do_livro.quantas_com_duvida(pr),
            "botao_alertas": t.botao_alertas.text(),
            "rodape": t.rotulo_da_pagina.text() if hasattr(t, "rotulo_da_pagina") else None}


def estado(j):
    t = j.tela_conferir
    pr = j.projeto
    ed = t.editor_selecao
    return {"pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1, "aba": t.aba_atual,
            "ferramenta_trilha": t.trilha.ferramenta, "ferramenta_editor": getattr(ed, "ferramenta", None),
            "mostrar": t.mostrar, "comparando": t.comparando,
            "marcacoes_botao": t.botao_marcacoes.isChecked(),
            "editor_mostra_marcacao": getattr(ed, "mostrar_marcacao", None),
            "editor_mostra_achadas": getattr(ed, "mostrar_achadas", None),
            "faixa": t.texto_faixa.text(),
            "paginas": len(pr.paginas), "vao_ao_pdf": len(pr.paginas_ativas),
            "folhas_divididas": sum(1 for f in pr.folhas if f.dividir),
            "pixmap_editor": (None if ed._pixmap is None else [ed._pixmap.width(), ed._pixmap.height()]),
            "area_editor": (None if getattr(ed, "_area", None) is None else
                            [ed._area.width(), ed._area.height()]),
            **sino(j)}


def ferramenta(j, nome):
    """Clique no botão da trilha da esquerda cujo ícone à vista é `nome` (mensagem do Windows)."""
    t = j.tela_conferir
    tr = t.trilha
    for indice, ret in tr.retangulos().items():
        if tr._a_vista.get(indice) == nome:
            base.clique(j, tr, ponto=ret.center())
            base.esperar(1.5)
            return True
    anotar("AVISO-ferramenta-nao-achada-na-trilha", nome)
    return False


def mostrar(j, qual):
    from ui.widgets.paginas_rolando import DUAS, UMA
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(2.0)


def ir_pagina(j, n1):
    """Clique na miniatura da página n1 (1 = a primeira) na tira de baixo."""
    t = j.tela_conferir
    i = n1 - 1
    mini = t.tira._miniaturas[i]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini)
    base.esperar(2.5)
    if t.indice_pagina != i:
        anotar(f"AVISO-ir-pagina-{n1}", {"cheguei_em": t.indice_pagina + 1})


# --- Automático ---------------------------------------------------------------------------------

def abrir_janela_grande(j, pelo_aviso=False):
    t = j.tela_conferir
    if pelo_aviso and t.aviso_do_livro_novo.isVisible():
        base.clique(j, t.botao_rodar_do_aviso)
        anotar("abri-pelo-aviso-do-livro-novo", True)
    else:
        from ui.widgets.paineis import PAINEL_AUTOMATICO
        pa = t.paineis
        if not pa.automatico.isVisible():
            ic = pa.icones
            base.clique(j, ic, ponto=ic.retangulos()[PAINEL_AUTOMATICO].center())
            base.esperar(0.8)
        base.clique(j, pa.automatico.botao_janela)
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


def marcar_etapa(jan, etapa, querer: bool, rolar=True):
    from PySide6.QtCore import QPoint, Qt
    lista = jan.painel_de_opcoes.lista
    item = lista.item_da_etapa(etapa)
    if (item.checkState() == Qt.Checked) == querer:
        return querer
    if rolar:
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


def estado_da_lista(jan):
    from PySide6.QtCore import Qt
    from core import automatico as A
    lista = jan.painel_de_opcoes.lista
    return {e: ("MARCADA" if lista.item_da_etapa(e).checkState() == Qt.Checked else "desmarcada")
            + " | " + lista.item_da_etapa(e).text().replace("\n", " / ") for e in A.ETAPAS}


def rodar(j, jan):
    from ui.janela_principal import CONFERIR
    from ui.tarefas import TarefaAutomatico
    base.clique(jan, jan.botao_rodar)
    base.esperar(1.0)
    t = time.time()
    viu = False
    while time.time() - t < 2400:
        base.esperar(0.3)
        rodando = isinstance(j.tarefa, TarefaAutomatico) and j.tarefa.isRunning()
        viu = viu or rodando
        pronta = j.telas.currentIndex() == CONFERIR and not rodando
        try:
            aberta = jan.isVisible()
        except RuntimeError:
            aberta = False
        if pronta and (viu or (time.time() - t > 30 and not aberta)):
            break
    anotar("rodar-viu-a-tarefa", viu)
    return round(time.time() - t, 1)


# --- processar ----------------------------------------------------------------------------------

def processar(j, nome_novo=None, prints=""):
    """Clica "Confirmar e processar"; na "Antes de processar", "continuar assim mesmo"; na janela
    "Confirmar e processar" tira o print, e se `nome_novo`, apaga o nome e digita o novo (teclas do
    Windows no campo), tira outro print e clica Processar. Espera o PDF ficar pronto."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    feito = {"antes": False, "confirmar": False}

    def olhar():
        for w in QApplication.topLevelWidgets():
            try:
                vis = w.isVisible()
            except RuntimeError:
                continue
            if not vis or w.property("_visto"):
                continue
            if isinstance(w, JanelaDosAvisos):
                w.setProperty("_visto", True)
                base.esperar(1.0)
                p(w, f"{prints}antes-de-processar")
                anotar("antes-de-processar", [x for x in base.textos(w) if "aviso" in x.lower() or "página" in x.lower()][:12])
                base.clique(w, w.botao_continuar)
                feito["antes"] = True
                return
            if isinstance(w, JanelaConfirmar):
                w.setProperty("_visto", True)
                base.esperar(1.2)
                p(w, f"{prints}confirmar-como-abriu")
                anotar("confirmar-abriu", {"nome": w.destino.campo_nome.text(), "pasta": str(w.destino.pasta),
                                           "faixa_existe_visivel": w.aviso_existe.isVisibleTo(w),
                                           "faixa_existe": w.aviso_existe.rotulo.text(),
                                           "aviso_do_seletor": w.destino.aviso.text()})
                if nome_novo:
                    campo = w.destino.campo_nome
                    base.clique(w, campo)
                    # Ctrl+A pelo teclado não passa por mensagem; End + Backspaces apagam o nome
                    base.tecla(w, 0x23)                         # End
                    base.tecla(w, 0x08, vezes=len(campo.text()) + 2)   # Backspace
                    base.digitar(w, nome_novo, enter=False)
                    base.esperar(1.0)
                    p(w, f"{prints}confirmar-depois-de-trocar-o-nome")
                    anotar("confirmar-depois-de-trocar-o-nome", {
                        "nome": campo.text(), "caminho": str(w.caminho), "existe": w.caminho.exists(),
                        "faixa_existe_visivel": w.aviso_existe.isVisibleTo(w),
                        "faixa_existe": w.aviso_existe.rotulo.text(),
                        "aviso_do_seletor": w.destino.aviso.text(),
                        "aviso_do_seletor_visivel": w.destino.aviso.isVisibleTo(w)})
                base.clique(w, w.botao_processar)
                feito["confirmar"] = True
                return

    relogio = QTimer(); relogio.setInterval(300); relogio.timeout.connect(olhar); relogio.start()
    t = j.tela_conferir
    base.clique(j, t.botao_processar)
    comeco = time.time()
    from ui.janela_principal import CONFERIR, PROGRESSO
    while time.time() - comeco < 3600:
        base.esperar(1.0)
        if feito["confirmar"] and j.telas.currentIndex() not in (PROGRESSO, CONFERIR):
            break
    relogio.stop()
    base.esperar(3)
    anotar("processar", {"s": round(time.time() - comeco), "tela": j.telas.currentIndex(),
                         "saida": getattr(j.projeto, "caminho_saida", "")})
    p(j, f"{prints}pronto")


# --- fases ---------------------------------------------------------------------------------------

def fase_a():
    from PySide6.QtCore import Qt
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    from ui.widgets.editor_selecao import FERRAMENTA_MAO
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    abrir(j)
    anotar("abriu", estado(j))
    p(j, "abriu-livro-novo")

    # 1. o Automático pelo aviso do livro novo, como a rodada 1 do Kaique
    jan = abrir_janela_grande(j, pelo_aviso=True)
    jan.resize(1456, 784)
    base.esperar(1.0)
    anotar("automatico-abriu", estado_da_lista(jan))
    mostrar_etapa(jan, A.DIVIDIR)
    p(jan, "automatico-dividir-g2")                                   # D-687
    marcar_etapa(jan, A.DIVIDIR, True)
    caixa_capa = jan.painel_de_opcoes.controles["capa_aberta"]
    from PySide6.QtCore import QPoint
    for x in (10, 30, 60):                  # o quadradinho e o começo do texto (a caixinha é larga)
        base.clique(jan, caixa_capa, QPoint(x, caixa_capa.height() // 2)); base.esperar(0.8)
        if caixa_capa.isChecked():
            break
    anotar("capa-aberta-marcada", caixa_capa.isChecked())
    marcar_etapa(jan, A.CORTAR, False)
    mostrar_etapa(jan, A.LIMPAR)
    base.clique(jan, jan.painel_de_opcoes.radios_de_filtro[PRETO_E_BRANCO]); base.esperar(1.0)
    anotar("antes-de-rodar", {"lista": estado_da_lista(jan), "botao": jan.botao_rodar.text(),
                              "resumo": [x for x in base.textos(jan) if "Vou " in x]})
    base.esperar(4)
    p(jan, "automatico-pronto-para-rodar")
    anotar("rodou-em-s", rodar(j, jan))

    # 2. logo depois de rodar: a ferramenta que ficou, a vista, o sino
    t = j.tela_conferir
    base.esperar(2)
    anotar("depois-de-rodar", estado(j))
    p(j, "depois-de-rodar")
    # o sino sem ninguém mexer: 60 s parado
    for s in (10, 20, 30, 60):
        base.esperar(10 if s != 60 else 30)
        anotar(f"sino-parado-{s}s", sino(j))
    # 3. a Mão escolhida na trilha, "Uma página" (D-683, D-684)
    ferramenta(j, FERRAMENTA_MAO)
    mostrar(j, "uma")
    anotar("mao-uma-pagina-p1", estado(j))
    p(j, "mao-uma-pagina-p1")
    for n1 in (2, 5, 8, 14):
        ir_pagina(j, n1)
        anotar(f"mao-uma-pagina-p{n1}", estado(j))
        p(j, f"mao-uma-pagina-p{n1}")
    # o mesmo com o Dividir escolhido (a página certa?) e de volta à Mão
    ir_pagina(j, 1)
    base.tecla(j, ord("D")); base.esperar(2.5)
    anotar("dividir-p1", estado(j))
    p(j, "dividir-p1")
    ferramenta(j, FERRAMENTA_MAO)
    anotar("mao-de-novo-p1", estado(j))
    p(j, "mao-de-novo-p1")
    anotar("sino-depois-de-andar", sino(j))
    if FASE == "a":
        resto_da_fase_a(j)


def abrir_painel(j, qual, aberto=True):
    """Clique no ícone do painel na coluna da direita; se o clique por mensagem não mudar nada
    (visto na fase a), o mesmo que o clique faz: paineis.alternar(qual). Anota qual valeu."""
    pa = j.tela_conferir.paineis
    if (pa.aberto == qual) == aberto:
        return
    ic = pa.icones
    base.clique(j, ic, ponto=ic.retangulos()[qual].center())
    base.esperar(1.5)
    if (pa.aberto == qual) != aberto:
        anotar("painel-pelo-alternar", {"qual": qual, "aberto_antes": pa.aberto})
        pa.alternar(qual)
        base.esperar(1.5)
    anotar("painel", {"qual": qual, "aberto": pa.aberto})


def fase_b():
    """Reabre o livro já rodado e processado na fase a: "deixar em branco" (D-680), "tirar do
    livro" (D-686), o Propriedades aberto na janela grande e na pequena (D-681), o sino depois de
    reabrir (D-679), e o Automático de novo: a contagem com a página tirada (D-679) e a lista que
    sobe ao marcar "Margens iguais" (D-688)."""
    from core import automatico as A
    from ui.widgets.paineis import PAINEL_PROPRIEDADES
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    abrir(j)
    t = j.tela_conferir
    anotar("reabriu", estado(j))
    for s in (5, 15, 30):
        base.esperar(5 if s == 5 else (10 if s == 15 else 15))
        anotar(f"sino-reaberto-{s}s", sino(j))
    sino_que_muda(j)
    ir_pagina(j, 3)
    abrir_painel(j, PAINEL_PROPRIEDADES)
    anotar("propriedades", {"em_branco_visivel": t.botao_em_branco.isVisible(),
                            "tirar_visivel": t.botao_tirar_do_livro.isVisible()})
    p(j, "p3-propriedades-aberto")                                       # D-681
    base.clique(j, t.botao_em_branco); base.esperar(4)
    anotar("p3-em-branco", estado(j))
    p(j, "p3-em-branco")                                                 # D-680
    ir_pagina(j, 4); base.esperar(2)
    p(j, "p4-depois-do-branco-na-3")
    ir_pagina(j, 133)
    anotar("p133-antes", estado(j))
    p(j, "p133-antes-de-tirar")
    base.clique(j, t.botao_tirar_do_livro); base.esperar(3)
    anotar("p133-tirada", estado(j))
    p(j, "p133-tirada")                                                  # D-686
    j.resize(1280, 657); base.esperar(3)
    p(j, "pequena-propriedades-aberto")                                  # D-681
    j.resize(LARGURA, ALTURA); base.esperar(3)
    abrir_painel(j, PAINEL_PROPRIEDADES, aberto=False)
    p(j, "grande-propriedades-fechado")
    anotar("sino-depois-de-tirar", sino(j))
    # o Automático de novo, com a página tirada
    ir_pagina(j, 132)
    jan = abrir_janela_grande(j)
    jan.resize(1456, 784)
    base.esperar(3)
    painel = jan.antes_e_depois
    anotar("automatico-2", {"contador": painel.contador.text() if hasattr(painel.contador, "text") else None,
                            "campo": painel.campo_pagina.text(),
                            "resumo": [x for x in base.textos(jan) if "Vou " in x or "páginas" in x][:6],
                            "lista": estado_da_lista(jan)})
    p(jan, "automatico-2-contagem")                                      # D-679
    # a lista: rolar até o fim e marcar "Margens iguais" (D-688)
    lista = jan.painel_de_opcoes.lista
    barra = lista.verticalScrollBar()
    item = lista.item_da_etapa(A.MARGENS)
    lista.scrollToItem(item); base.esperar(0.8)
    antes = barra.value()
    anotar("lista-rolada", {"barra": antes, "max": barra.maximum()})
    p(jan, "lista-rolada-ate-margens")
    marcar_etapa(jan, A.MARGENS, True, rolar=False)
    base.esperar(1.5)
    anotar("lista-depois-de-marcar-margens", {"barra": barra.value(), "max": barra.maximum(),
                                               "atual": lista.currentItem().data(0x0100) if lista.currentItem() else None})
    p(jan, "lista-depois-de-marcar-margens")
    # outro caminho: uma opção qualquer da etapa (capa aberta) com a lista rolada
    lista.scrollToItem(lista.item_da_etapa(A.CADERNOS)); base.esperar(0.8)
    antes2 = barra.value()
    marcar_etapa(jan, A.CADERNOS, True, rolar=False); base.esperar(1.5)
    anotar("lista-depois-de-marcar-cadernos", {"antes": antes2, "depois": barra.value()})
    p(jan, "lista-depois-de-marcar-cadernos")
    base.clique(jan, [b for b in jan.findChildren(__import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton)
                      if b.text() == "Fechar"][0])
    base.esperar(2)
    # a janela de salvar (D-685): o livro "já foi processado" para _dados/saida (o PDF da fase a,
    # copiado para lá); a janela abre com esse nome, que existe; troca-se o nome pelo teclado e
    # depois "voltar" (não processa de novo: nada é gravado)
    saida = TRAB / "saida" / "lusiadas - preto e branco.pdf"
    j.projeto.caminho_saida = str(saida)
    confirmar_e_trocar_o_nome(j, "rodada-2.pdf")
    base.fechar(j)


def sino_que_muda(j):
    """D-679, o caminho do Kaique: na "Antes de processar", "Mostrar: Qualidade baixa" +
    "Selecionar todas" + "está bom nas marcadas"; a janela volta com o que sobrou: print e fechar no
    X (não processa). Depois, sem mexer em nada, esperar; e depois só andar pelas páginas (setas).
    Anota o sino a cada passo."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    feito = {"vezes": 0, "fim": False}

    def olhar():
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto"):
                    continue
            except RuntimeError:
                continue
            if isinstance(w, JanelaConfirmar):          # não era para chegar aqui: "voltar"
                w.setProperty("_visto", True)
                anotar("AVISO-confirmar-abriu-no-teste-do-sino", True)
                w.reject()
                return
            if not isinstance(w, JanelaDosAvisos):
                continue
            w.setProperty("_visto", True)
            feito["vezes"] += 1
            base.esperar(1.0)
            if feito["vezes"] == 1:
                anotar("avisos-1", {"frase": w.rotulo.text(),
                                    "motivos": [w.combo_motivo.itemText(i) for i in range(w.combo_motivo.count())]})
                qual = next((i for i in range(w.combo_motivo.count())
                             if "ualidade" in w.combo_motivo.itemText(i)), 0)
                w.combo_motivo.setCurrentIndex(qual); base.esperar(0.8)
                base.clique(w, w.botao_todas); base.esperar(0.8)
                anotar("avisos-1-marcadas", len(w.avisos_marcados()))
                p(w, "avisos-qualidade-baixa-todas-marcadas")
                base.clique(w, w.botao_aceitar); base.esperar(1.5)
            else:
                p(w, "avisos-o-que-sobrou")
                anotar("avisos-2", {"frase": w.rotulo.text()})
                base.user32.PostMessageW(int(w.winId()), base.WM_CLOSE, 0, 0)
                feito["fim"] = True
            return

    relogio = QTimer(); relogio.setInterval(300); relogio.timeout.connect(olhar); relogio.start()
    anotar("sino-antes-do-esta-bom", sino(j))
    base.clique(j, j.tela_conferir.botao_processar)
    comeco = time.time()
    while time.time() - comeco < 90 and not feito["fim"]:
        base.esperar(0.5)
    base.esperar(2)
    relogio.stop()
    anotar("sino-logo-depois-do-esta-bom", sino(j))
    p(j, "sino-logo-depois-do-esta-bom")
    for s in (10, 30, 60):
        base.esperar(10 if s == 10 else (20 if s == 30 else 30))
        anotar(f"sino-parado-{s}s-depois-do-esta-bom", sino(j))
    ir_pagina(j, 1)
    for n in range(1, 41):
        base.tecla(j, 0x27); base.esperar(0.8)
        if n % 10 == 0:
            anotar(f"sino-depois-de-{n}-setas", {**sino(j), "pagina": j.tela_conferir.indice_pagina + 1})
    base.esperar(20)
    anotar("sino-20s-depois-das-setas", sino(j))
    p(j, "sino-depois-de-andar")


def confirmar_e_trocar_o_nome(j, nome_novo):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    feito = {"fim": False}

    def olhar():
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto"):
                    continue
            except RuntimeError:
                continue
            if isinstance(w, JanelaDosAvisos):
                w.setProperty("_visto", True)
                base.esperar(1.0)
                base.clique(w, w.botao_continuar)
                return
            if isinstance(w, JanelaConfirmar):
                w.setProperty("_visto", True)
                base.esperar(1.2)
                p(w, "salvar-como-abriu")
                anotar("salvar-abriu", {"nome": w.destino.campo_nome.text(), "pasta": str(w.destino.pasta),
                                        "faixa_existe_visivel": w.aviso_existe.isVisibleTo(w),
                                        "faixa_existe": w.aviso_existe.rotulo.text(),
                                        "aviso_do_seletor": w.destino.aviso.text()})
                campo = w.destino.campo_nome
                base.clique(w, campo)
                base.tecla(w, 0x23)
                base.tecla(w, 0x08, vezes=len(campo.text()) + 2)
                base.digitar(w, nome_novo, enter=False)
                base.esperar(1.0)
                p(w, "salvar-depois-de-trocar-o-nome")
                anotar("salvar-depois-de-trocar-o-nome", {
                    "nome": campo.text(), "caminho": str(w.caminho), "existe": w.caminho.exists(),
                    "faixa_existe_visivel": w.aviso_existe.isVisibleTo(w),
                    "faixa_existe": w.aviso_existe.rotulo.text(),
                    "aviso_do_seletor": w.destino.aviso.text(),
                    "aviso_do_seletor_visivel": w.destino.aviso.isVisibleTo(w)})
                base.clique(w, [b for b in w.findChildren(__import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton)
                                if b.text() == "voltar"][0])
                feito["fim"] = True
                return

    relogio = QTimer(); relogio.setInterval(300); relogio.timeout.connect(olhar); relogio.start()
    base.clique(j, j.tela_conferir.botao_processar)
    comeco = time.time()
    while time.time() - comeco < 120 and not feito["fim"]:
        base.esperar(0.5)
    base.esperar(2)
    relogio.stop()


def resto_da_fase_a(j):
    from ui.widgets.paineis import PAINEL_PROPRIEDADES
    t = j.tela_conferir
    # 4. "deixar em branco" na página 3 (D-680): a página grande e a miniatura
    ir_pagina(j, 3)
    abrir_painel(j, PAINEL_PROPRIEDADES)
    anotar("propriedades-aberto", {"visivel_em_branco": t.botao_em_branco.isVisible(),
                                   "visivel_tirar": t.botao_tirar_do_livro.isVisible()})
    p(j, "p3-antes-do-branco-propriedades-aberto")                     # D-681 também
    base.clique(j, t.botao_em_branco); base.esperar(4)
    anotar("p3-em-branco", estado(j))
    p(j, "p3-em-branco")
    # 5. "tirar do livro" na página 133 (a contracapa repetida do scan; D-686)
    ir_pagina(j, 133)
    anotar("p133-antes-de-tirar", estado(j))
    p(j, "p133-antes-de-tirar")
    base.clique(j, t.botao_tirar_do_livro); base.esperar(3)
    anotar("p133-tirada", estado(j))
    p(j, "p133-tirada")
    # 6. a janela pequena (1280 x 657) com o Propriedades aberto (D-681)
    j.resize(1280, 657); base.esperar(2.5)
    p(j, "pequena-propriedades-aberto")
    j.resize(LARGURA, ALTURA); base.esperar(2.5)
    # o "voltar a página" na 3, para o PDF sair com ela
    ir_pagina(j, 3)
    base.clique(j, t.botao_em_branco); base.esperar(3)
    anotar("p3-voltou", estado(j))
    abrir_painel(j, PAINEL_PROPRIEDADES)                               # fecha
    anotar("sino-antes-de-processar", sino(j))
    # 7. processar (o nome que o programa sugere)
    processar(j, prints="proc1-")
    # 8. montar para imprimir (Livreto, de fábrica), sobre o PDF que saiu (D-682)
    tf = j.tela_final
    base.clique(j, tf.botao_montar); base.esperar(4)
    d = tf.dialogo_impressao
    d.resize(1250, 800); base.esperar(6)
    p(d, "montar-como-abriu")
    destino = TRAB / "saida" / "lusiadas - para imprimir.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    # o "gravar" abriria a janela de arquivo do Windows (fora do nosso alcance): o mesmo
    # que ela faz depois de escolher o lugar é d.comecar(destino)
    d.comecar(destino=str(destino))
    comeco = time.time()
    while time.time() - comeco < 1800 and d.tarefa is not None and d.tarefa.isRunning():
        base.esperar(1.0)
    base.esperar(3)
    anotar("montar-gravou", {"s": round(time.time() - comeco), "avisos_visiveis": d.avisos.isVisible(),
                             "avisos": d.avisos.text(), "estado": d.estado.text()})
    p(d, "montar-depois-de-gravar")
    d.close(); base.esperar(1)
    # 9. de volta ao livro e processar de novo, trocando o nome (D-685)
    base.clique(j, [b for b in tf.findChildren(__import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton)
                    if b.text() == "fazer outro"][0])
    base.esperar(3)
    j.abrir_livro(str(TRAB / "livros" / "lusiadas.pdf"))
    anotar("reabriu-em-s", esperar_tela(j))
    anotar("reabriu", estado(j))
    processar(j, nome_novo="rodada-2.pdf", prints="proc2-")


def fase_c():
    """D-686 com a Mão (o caso do Kaique): reabre, escolhe a Mão na trilha, vai à página 133 (já
    tirada do livro na fase b) e à 132 (no livro), e fotografa a faixa das duas."""
    from ui.widgets.editor_selecao import FERRAMENTA_MAO
    j = base.nova_janela(LARGURA, ALTURA)
    _porteiro = Porteiro()
    abrir(j)
    ferramenta(j, FERRAMENTA_MAO)
    for n1 in (132, 133):
        ir_pagina(j, n1)
        base.esperar(2)
        anotar(f"mao-p{n1}", estado(j))
        p(j, f"mao-p{n1}")
    # D-688: a janela do Automático do tamanho da tela do notebook do Kaique (1280 x 657), onde
    # a lista das etapas não cabe; rolar a lista até o fim (a roda do mouse não chega fora da
    # tela: a barra é posta no fim, como a roda faria) e marcar "6 Margens iguais" com o clique
    from core import automatico as A
    jan = abrir_janela_grande(j)
    jan.resize(1280, 657); base.esperar(3)
    lista = jan.painel_de_opcoes.lista
    barra = lista.verticalScrollBar()
    for etapa in (A.MARGENS, A.CADERNOS):
        barra.setValue(barra.maximum()); base.esperar(1.0)
        antes = barra.value()
        anotar(f"lista-{etapa}-rolada", {"barra": antes, "max": barra.maximum()})
        p(jan, f"lista-rolada-antes-de-marcar-{etapa}")
        item = lista.item_da_etapa(etapa)
        marcado_antes = item.checkState()
        marcar_etapa(jan, etapa, item.checkState() != 2, rolar=False)
        base.esperar(1.5)
        anotar(f"lista-depois-de-marcar-{etapa}", {"antes": antes, "depois": barra.value(),
                                                     "max": barra.maximum(), "estado_antes": int(marcado_antes.value) if hasattr(marcado_antes, "value") else int(marcado_antes)})
        p(jan, f"lista-depois-de-marcar-{etapa}")
    jan.reject(); base.esperar(1.5)
    base.fechar(j)


def main():
    global LOG
    base.preparar(str(RAIZ), str(TRAB), limpar=False)
    LOG = open(PASTA / "scripts" / f"anotacoes-{FASE}.txt", "a", encoding="utf-8")
    anotar("comeco", {"fase": FASE, "raiz": str(RAIZ)})
    {"a": fase_a, "mao": fase_a, "b": fase_b, "c": fase_c}[FASE]()
    anotar("fim", FASE)
    LOG.close()


if __name__ == "__main__":
    main()
