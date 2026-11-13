""""Desfazer nesta página": tirar só de UMA página as etapas que mexeram nela (D-621).

O QUE O SAMUEL PEDIU (docs/plano/DECISOES.md, D-621, 04/11/2026)
    "eu quero um botão para desfazer ajustes em uma pagina só, por exemplo, vamos supor que eu
    passei o automatico e só uma pagina veio com defeito, e eu gostaria de tirar algumas etapas que
    foram feitas somente com ela, eu quero poder clicar e falar quais coisas eu quero que sejam
    tirar, porque geralmnete quando a pagina já foi dividida, ela está certa e se eu juntar uma
    pagina na outra, a outra pagina que está certa vai voltar a ser uma junto com a que está errada
    e eu vou ter que refazer o processo em duas, e eu quero fazer só em uma." · o jeito escolhido:
    "A2" (botão direito na página, com caixinhas).

O QUE FAZ
    Botão direito na página (área de trabalho, em qualquer vista) ou na miniatura dela (tira de
    baixo) → menu com "Desfazer nesta página" → a lista das etapas (Endireitar, Corte das bordas,
    Mover e tamanho, Filtro, Gravuras e fotos), cada uma com caixinha; as que não mexeram na
    página ficam apagadas. Embaixo, o botão "desfazer". As caixinhas começam desmarcadas (o
    exemplo da D-621: "marcar Corte e Filtro → desfazer").

    Cada etapa marcada volta ao que veio do scan, SÓ nessa página, gravando o MESMO valor que o
    botão da ferramenta já grava:
        Endireitar        ângulo 0                       = "deixar como veio" (D-368)
        Corte das bordas  corte (0, 0, 1, 1)             = "não cortar esta"
        Mover e tamanho   tamanho 100%, sem mover        = "voltar como veio" do Mover
        Filtro            Original                       = escolher "Original" no painel
        Gravuras e fotos  marcação vazia e "Respeitar as gravuras achadas" desligada
                          = "Limpar tudo" do Marcar + a caixinha da D-586 (sem ela, a procura
                          automática poria as gravuras de volta na página no próximo desenho)
    A página fica "mexida à mão" (D-004) nas etapas desfeitas e "conferida", como fazem
    "deixar como veio" e "não cortar esta". A divisão não entra: a página continua separada e a
    outra página da folha não muda. Tudo é UMA ação do Histórico (Ctrl+Z volta tudo, Ctrl+Y refaz).

D-623 (04/11/2026, no mesmo menu): na MINIATURA da tira, embaixo do "Desfazer nesta página",
    "adicionar página em branco antes" e "adicionar página em branco depois"
    (TelaConferir.adicionar_pagina_em_branco; a conta em core/paginas_em_branco.py).

ONDE ESTÁ LIGADO
    TelaConferir.__init__ chama ligar(tela) (filtros do botão direito na área da página e na tira);
    TelaConferir._area_de_visualizador põe acrescentar_ao_menu no menu do botão direito do Mover
    (o das linhas de apoio, D-056, que continua igual; o "Desfazer nesta página" vem embaixo).

Seguro mudar: os textos. Arriscado: gravar outro valor que não o do botão da ferramenta (a página
sairia diferente do "deixar como veio"/"não cortar esta"); tocar em campo de FOLHA (a outra página
da folha mudaria); registrar mais de uma ação (o Ctrl+Z voltaria só uma parte).
"""

from __future__ import annotations

import copy
import traceback

from PySide6.QtCore import QEvent, QObject, QPointF, Qt, Signal
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QMenu, QPushButton, QVBoxLayout,
                               QWidget, QWidgetAction)

from core import etapas as etapas_core
from core.filtros import ORIGINAL
from registro import registrar_erro

# --- as etapas da lista, na ordem da tela ----------------------------------------------------

ENDIREITAR = etapas_core.ENDIREITAR
CORTAR = etapas_core.CORTAR
MOVER = etapas_core.MOVER
FILTRO = etapas_core.FILTRO
GRAVURAS = etapas_core.MARCAR

ETAPAS = (ENDIREITAR, CORTAR, MOVER, FILTRO, GRAVURAS)
NOMES = {
    ENDIREITAR: "Endireitar",
    CORTAR: "Corte das bordas",
    MOVER: "Mover e tamanho",
    FILTRO: "Filtro",
    GRAVURAS: "Gravuras e fotos",
}
TITULO = "Desfazer nesta página"
TEXTO_DO_BOTAO = "desfazer"

SEM_CORTE = (0.0, 0.0, 1.0, 1.0)        # o "não cortar esta" (TelaConferir._sem_recorte)
_TOLERANCIA = 1e-6


# --- a conta (só lê e monta campos; não muda nada) -------------------------------------------

def _sem_corte(recorte) -> bool:
    return recorte is not None and all(
        abs(float(a) - b) < _TOLERANCIA for a, b in zip(tuple(recorte), SEM_CORTE))


def _endireitar_mexeu(projeto, pagina) -> bool:
    """A página sai girada pelo ângulo (o automático ou o à mão)? Ângulo ainda não medido, com o
    automático ligado: conta como mexida (vai girar quando for medido)."""
    from core.pipeline import angulo_aplicado, angulo_da_pagina

    angulo = angulo_da_pagina(projeto, pagina)
    if angulo is None:
        return etapas_core.endireita_sozinho(projeto, pagina)
    return angulo_aplicado(angulo) != 0.0


def _corte_mexeu(projeto, pagina) -> bool:
    """A página sai cortada (o corte à mão, ou o automático sem corte à mão)? O "não cortar
    esta" não conta."""
    recorte = etapas_core.recorte_a_mao(projeto, pagina)
    if recorte is not None:
        return not _sem_corte(recorte)
    return etapas_core.corta_sozinho(projeto, pagina)


def _gravuras_mexeu(projeto, pagina) -> bool:
    """A página tem marcação que vale: feita à mão, ou achada pela máquina e respeitada pelo
    filtro (D-586)."""
    from core.selecao import MAO

    regioes = [r for r in (getattr(pagina, "selecao", None) or []) if isinstance(r, dict)]
    if any(str(r.get("origem", MAO)) == MAO for r in regioes):
        return True
    da_maquina = any(str(r.get("origem", MAO)) != MAO for r in regioes)
    return (da_maquina and bool(getattr(pagina, "respeitar_gravuras_achadas", True))
            and etapas_core.a_marcacao_da_maquina_vale(projeto, pagina))


def etapas_que_mexeram(projeto, pagina) -> list[str]:
    """As etapas da lista que mexeram nesta página, na ordem de ETAPAS. Só lê campos (e o ângulo
    já medido nesta sessão); nunca levanta."""
    contas = {
        ENDIREITAR: _endireitar_mexeu,
        CORTAR: _corte_mexeu,
        MOVER: lambda _p, pag: etapas_core.conteudo_fora_do_padrao(pag),
        FILTRO: lambda proj, pag: etapas_core.filtro_que_vale(proj, pag) != ORIGINAL,
        GRAVURAS: _gravuras_mexeu,
    }
    mexeram = []
    for etapa in ETAPAS:
        try:
            if contas[etapa](projeto, pagina):
                mexeram.append(etapa)
        except Exception:  # noqa: BLE001 - na dúvida a caixinha fica acesa
            registrar_erro("desfazer nesta página: etapas que mexeram", traceback.format_exc())
            mexeram.append(etapa)
    return mexeram


def campos_para_desfazer(projeto, pagina, etapas) -> dict:
    """Os campos da página que voltam ao que veio do scan, para as `etapas` (ver o começo do
    arquivo), com a marca "mexida à mão" de cada uma e "conferida", como os botões da
    ferramenta. Não mexe na página. Etapa desconhecida é ignorada."""
    etapas = [e for e in ETAPAS if e in set(etapas)]
    campos: dict = {}
    if ENDIREITAR in etapas:
        campos["angulo_manual"] = 0.0
    if CORTAR in etapas:
        campos["recorte"] = list(SEM_CORTE)
    if MOVER in etapas:
        campos["conteudo_escala"] = 1.0
        campos["conteudo_deslocamento"] = [0.0, 0.0]
    if FILTRO in etapas:
        campos["filtro"] = ORIGINAL
    if GRAVURAS in etapas:
        campos["selecao"] = []
        campos["marcacao_provisoria"] = False
        campos["geometria_das_zonas"] = None
        campos["respeitar_gravuras_achadas"] = False
    if not campos:
        return {}
    marcas = list(getattr(pagina, "mexida_a_mao", None) or [])
    for etapa in etapas:
        if etapa not in marcas:
            marcas.append(etapa)
    campos["mexida_a_mao"] = marcas
    campos["revisada"] = True
    return campos


def descricao(indice: int, etapas) -> str:
    """O texto do Histórico: "Desfazer na página 14: Corte das bordas e Filtro"."""
    nomes = [NOMES[e] for e in ETAPAS if e in set(etapas)]
    lista = nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]
    return f"Desfazer na página {indice + 1}: {lista}"


# --- a ação (uma só no Histórico) ------------------------------------------------------------

def desfazer(tela, indice: int, etapas) -> bool:
    """Desfaz as `etapas` na página `indice` do livro aberto na `tela` (TelaConferir), numa ação
    só do Histórico, e redesenha. Devolve True se mudou alguma coisa.

    É o caminho do TelaConferir._registrar, sem a marca automática dele (a marca daqui é a das
    etapas desfeitas: a caixinha "Respeitar as gravuras achadas" não pode virar "filtro escolhido
    à mão"). O Endireitar desfeito com o corte à mão ficando leva o corte junto quando a escolha
    é "acompanha o texto" (D-094), como o "deixar como veio" (_com_o_retangulo_do_corte)."""
    from historico_acoes import aplicar
    from modelos import Acao

    projeto = getattr(tela, "projeto", None)
    if projeto is None or getattr(tela, "acoes", None) is None:
        return False
    if not 0 <= indice < len(projeto.paginas):
        return False
    pagina = projeto.paginas[indice]
    campos = campos_para_desfazer(projeto, pagina, etapas)
    if not campos:
        return False
    if "angulo_manual" in campos and "recorte" not in campos:
        campos = tela._com_o_retangulo_do_corte([indice], campos)
        if "recorte" in campos and CORTAR not in campos["mexida_a_mao"]:
            campos["mexida_a_mao"] = [*campos["mexida_a_mao"], CORTAR]   # como o _registrar
    if tela._espera_pelas_marcacoes("pagina", [indice], campos):
        return False
    campos = tela._com_os_avisos_de_agora("pagina", [indice], campos)
    # D-646/D-699: o Filtro desfeito volta ao Original sem trazer o fundo de volta
    # (só o "Desfazer o tirar o fundo" traz): a MESMA regra das outras trocas de
    # filtro (core/fundo_tirado.com_o_fundo_que_fica, a de historico_acoes.montar_acao;
    # esta ação é montada aqui, sem passar por lá)
    from core.fundo_tirado import com_o_fundo_que_fica

    campos = com_o_fundo_que_fica(projeto, [indice], campos)
    chave = str(indice)
    antes = {campo: {chave: _como_no_arquivo(getattr(pagina, campo, None))} for campo in campos}
    depois = {campo: _como_no_arquivo(valor.get(chave) if isinstance(valor, dict) else valor)
              for campo, valor in campos.items()}
    if all(antes[c][chave] == depois[c] for c in campos
           if c not in ("revisada", "alertas", "alertas_aceitos", "mexida_a_mao")):
        return False                       # já estava assim: nada entra no Histórico
    acao = Acao.nova("desfazer_na_pagina", "pagina", [indice], antes, depois,
                     descricao(indice, etapas))
    aplicar(projeto, acao, acao.depois)
    tela.acoes.registrar(acao)
    if tela.previas is not None:
        tela.previas.invalidar(indice)
    tela.atualizar()
    return True


def _como_no_arquivo(valor):
    """O valor como o acoes.jsonl grava (tupla vira lista), numa cópia: o desfazer nunca devolve
    uma lista que mudou depois."""
    if isinstance(valor, (tuple, list)):
        return [_como_no_arquivo(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _como_no_arquivo(v) for k, v in valor.items()}
    return copy.deepcopy(valor)


# --- a lista com as caixinhas ----------------------------------------------------------------

class ListaDoDesfazer(QWidget):
    """As caixinhas das etapas e o botão "desfazer" (o que aparece dentro do menu). As etapas que
    não mexeram na página ficam apagadas; o botão só acende com alguma marcada."""

    desfazer_pedido = Signal(list)       # as etapas marcadas

    def __init__(self, mexeram: list[str], parent=None) -> None:
        super().__init__(parent)
        from ui import estilo
        from ui.estilo import estilo_da_caixinha_com_quadrado

        self.setObjectName("listaDoDesfazer")
        coluna = QVBoxLayout(self)
        coluna.setContentsMargins(14, 8, 14, 10)
        coluna.setSpacing(7)
        self.caixas: dict[str, QCheckBox] = {}
        for etapa in ETAPAS:
            caixa = QCheckBox(NOMES[etapa])
            estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(13))
            caixa.setEnabled(etapa in mexeram)
            if etapa not in mexeram:
                caixa.setToolTip("Esta etapa não mexeu nesta página.")
            caixa.toggled.connect(self._acertar_o_botao)
            coluna.addWidget(caixa)
            self.caixas[etapa] = caixa
        self.botao = QPushButton(TEXTO_DO_BOTAO)
        self.botao.setObjectName("acaoPrimaria")
        self.botao.setCursor(Qt.PointingHandCursor)
        self.botao.clicked.connect(self._pedir)
        coluna.addSpacing(2)
        coluna.addWidget(self.botao)
        self._acertar_o_botao()

    def marcadas(self) -> list[str]:
        return [e for e, caixa in self.caixas.items() if caixa.isChecked() and caixa.isEnabled()]

    def _acertar_o_botao(self, *_args) -> None:
        self.botao.setEnabled(bool(self.marcadas()))

    def _pedir(self) -> None:
        marcadas = self.marcadas()
        if marcadas:
            self.desfazer_pedido.emit(marcadas)


def acrescentar_ao_menu(tela, menu: QMenu, indice: int | None = None) -> QMenu | None:
    """Põe em `menu` o "Desfazer nesta página" (um submenu com a lista) da página `indice` (None =
    a página da vez da tela). Devolve o submenu, ou None se não há livro. O submenu guarda a
    lista em `.lista` (para os testes e o piloto)."""
    projeto = getattr(tela, "projeto", None)
    if projeto is None:
        return None
    if indice is None:
        indice = tela.indice_pagina
    if not 0 <= indice < len(projeto.paginas):
        return None
    # o submenu com dono (o menu) e guardado nele: o addMenu(texto) do PySide pode deixar o
    # Python apagar o submenu antes de ele abrir
    submenu = QMenu(TITULO, menu)
    submenu.setObjectName("menuDesfazerNestaPagina")
    menu.addMenu(submenu)
    menu._submenu_desfazer = submenu
    lista = ListaDoDesfazer(etapas_que_mexeram(projeto, projeto.paginas[indice]), submenu)
    acao = QWidgetAction(submenu)
    acao.setDefaultWidget(lista)
    submenu.addAction(acao)
    submenu._acao_da_lista = acao
    submenu.lista = lista
    submenu.indice = indice

    def pedido(etapas: list) -> None:
        # fecha o menu inteiro antes (a tela redesenha a página por baixo dele)
        submenu.hide()
        menu.hide()
        try:
            # o da tela tem o @protegido: um problema vira o aviso em português
            metodo = getattr(tela, "desfazer_nesta_pagina", None)
            if callable(metodo):
                metodo(indice, etapas)
            else:
                desfazer(tela, indice, etapas)
        except Exception:  # noqa: BLE001 - nenhuma exceção fecha a janela (CLAUDE.md §3)
            registrar_erro("desfazer nesta página", traceback.format_exc())

    lista.desfazer_pedido.connect(pedido)
    return submenu


# D-623 (Samuel, 04/11/2026, print a-80: "eu queria conseguir com botão direito apertando no meio
# das paginas aperece opção de adicionar folha em branco."): na miniatura da tira, o mesmo menu
# ganha estes dois (TelaConferir.adicionar_pagina_em_branco). Seguro mudar: os textos.
ANTES_EM_BRANCO = "adicionar página em branco antes"
DEPOIS_EM_BRANCO = "adicionar página em branco depois"


def acrescentar_pagina_em_branco(tela, menu: QMenu, indice: int) -> None:
    """Põe em `menu` "adicionar página em branco antes" e "... depois" da página `indice`
    (D-623; só no botão direito da miniatura)."""
    metodo = getattr(tela, "adicionar_pagina_em_branco", None)
    if not callable(metodo):
        return
    for texto, depois in ((ANTES_EM_BRANCO, False), (DEPOIS_EM_BRANCO, True)):
        acao = menu.addAction(texto)
        acao.triggered.connect(lambda _marcada=False, d=depois: metodo(indice, d))


def abrir_menu(tela, indice: int, posicao_global, da_tira: bool = False) -> QMenu | None:
    """Abre (sem esperar) o menu do botão direito da página `indice`, em `posicao_global`.
    Na miniatura da tira (`da_tira`), com o "adicionar página em branco" (D-623) embaixo.
    Guarda o menu em tela._menu_desfazer (o Qt não o apaga enquanto está aberto)."""
    menu = QMenu(tela)
    menu.setObjectName("menuDoBotaoDireitoDaPagina")
    if acrescentar_ao_menu(tela, menu, indice) is None:
        menu.deleteLater()
        return None
    if da_tira:
        menu.addSeparator()
        acrescentar_pagina_em_branco(tela, menu, indice)
    anterior = getattr(tela, "_menu_desfazer", None)
    if anterior is not None:
        try:
            anterior.close()
            anterior.deleteLater()
        except RuntimeError:
            pass
    tela._menu_desfazer = menu
    menu.popup(posicao_global)
    return menu


# --- qual página está debaixo do botão direito -----------------------------------------------

def pagina_no_ponto(tela, posicao_global) -> int | None:
    """A página do livro debaixo de `posicao_global` (um ponto da tela do Windows), na área de
    trabalho da `tela`: nos pares (Duas lado a lado), a página clicada; no Dividir com a folha
    inteira à vista, a metade do lado da linha em que se clicou; nas outras vistas, a página da
    vez. None = fora de qualquer página (nos pares) ou sem livro."""
    projeto = getattr(tela, "projeto", None)
    if projeto is None or not projeto.paginas:
        return None
    vista = getattr(tela, "vista_da_pagina", None)
    lado = getattr(tela, "lado_a_lado", None)
    if vista is not None and lado is not None and vista.currentWidget() is lado:
        # a peça da ferramenta (D-612) fica exatamente no lugar da página da vez: o lugar das
        # páginas arrumadas responde pelas duas
        from ui.widgets.paginas_rolando import MARGEM

        ponto = QPointF(lado.folhas.mapFromGlobal(posicao_global))
        for posicao, ret in getattr(lado, "_ret", []):
            if ret.adjusted(-MARGEM / 2, 0, MARGEM / 2, 0).contains(ponto):
                if 0 <= posicao < len(lado.indices):
                    return lado.indices[posicao]
        return None
    indice = tela.indice_pagina
    if getattr(tela, "trabalha_com_folhas", False):
        indice = _metade_clicada_no_dividir(tela, posicao_global, indice)
    return indice if 0 <= indice < len(projeto.paginas) else None


def _metade_clicada_no_dividir(tela, posicao_global, indice: int) -> int:
    """No Dividir com a folha dividida inteira à vista ("Duas lado a lado", com a linha azul): a
    página do lado da linha em que se clicou. Com "Uma página" (só a metade à vista) ou a folha
    inteira não dividida: a página da vez."""
    projeto = tela.projeto
    try:
        if tela._metade_no_dividir() is not None:
            return indice
        folha = projeto.folhas[tela.indice_folha]
        if not folha.dividir:
            return indice
        from ui.tela_conferir import ABA_CORTE

        vis = tela.visualizadores.get(ABA_CORTE)
        area = getattr(vis, "_area", None)
        if vis is None or area is None or area.width() <= 0:
            return indice
        x = (vis.mapFromGlobal(posicao_global).x() - area.left()) / area.width()
        metade = "esquerda" if x < float(vis.posicao_corte) else "direita"
        for pagina in projeto.paginas:
            if pagina.folha == tela.indice_folha and pagina.metade == metade:
                return pagina.indice
    except Exception:  # noqa: BLE001 - na dúvida, a página da vez
        registrar_erro("desfazer nesta página: metade clicada", traceback.format_exc())
    return indice


def pagina_da_miniatura(tela, widget) -> int | None:
    """A página do livro da miniatura `widget` (ou de um filho dela) da tira de baixo. No Dividir
    a tira mostra os passos das setas (D-601: uma metade ou a folha inteira): o passo vira a
    página (TelaConferir._passos_do_dividir). None fora de miniatura."""
    from ui.widgets.tira_miniaturas import Miniatura

    while widget is not None and not isinstance(widget, Miniatura):
        widget = widget.parentWidget()
    if widget is None or getattr(tela, "projeto", None) is None:
        return None
    quadro = int(widget.numero) - 1
    if getattr(tela, "trabalha_com_folhas", False):
        passos = tela._passos_do_dividir()
        if not 0 <= quadro < len(passos):
            return None
        quadro = passos[quadro]
    return quadro if 0 <= quadro < len(tela.projeto.paginas) else None


# --- a ligação na tela -----------------------------------------------------------------------

class _FiltroDoBotaoDireito(QObject):
    """Vigia o botão direito que chega à área da página (vista_da_pagina) e à tira (TiraMiniaturas)
    e abre o menu "Desfazer nesta página" da página certa. O botão direito chega aqui quando a
    peça de baixo não o usa (o visualizador só o usa no Mover, para as linhas de apoio)."""

    def __init__(self, tela) -> None:
        super().__init__(tela)
        self.tela = tela

    def eventFilter(self, vigiado, evento) -> bool:  # noqa: N802 - nome do Qt
        if evento.type() != QEvent.ContextMenu:
            return False
        tela = self.tela
        try:
            if getattr(tela, "projeto", None) is None or not tela._pronta():
                return False
            posicao = evento.globalPos()
            da_tira = vigiado is getattr(tela, "tira", None)
            if da_tira:
                debaixo = vigiado.childAt(vigiado.mapFromGlobal(posicao)) or QApplication.widgetAt(posicao)
                indice = pagina_da_miniatura(tela, debaixo)
            else:
                indice = pagina_no_ponto(tela, posicao)
            if indice is not None:
                abrir_menu(tela, indice, posicao, da_tira=da_tira)
        except Exception:  # noqa: BLE001 - o botão direito nunca fecha a janela
            registrar_erro("botão direito na página", traceback.format_exc())
        evento.accept()
        return True


def ligar(tela) -> None:
    """Liga o botão direito na área da página e na tira da `tela` (TelaConferir). Uma vez, no
    começo da tela."""
    filtro = _FiltroDoBotaoDireito(tela)
    tela._filtro_do_desfazer_na_pagina = filtro
    for peca in (getattr(tela, "vista_da_pagina", None), getattr(tela, "tira", None)):
        if peca is not None:
            peca.installEventFilter(filtro)
