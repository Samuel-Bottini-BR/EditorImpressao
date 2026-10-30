"""O painel Automático e a janela grande do Automático (obra de 26/10/2026, etapa 3).

AS DECISÕES DO SAMUEL QUE ESTA TELA CUMPRE
  D-002 (25/09): "Trabalho automático = painel 'Automático' que abre e fecha (substitui a tela
      7). [...] Funciona antes/ao abrir o livro e depois, na área de trabalho (ex.: abrir o PDF
      sem mexer e rodar as etapas depois)." · rodada 2 nº 5 ("Aprovado"): "Ter as duas: painel
      (opção 1) com botão que abre a janela (opção 2). Escolher folhas abrindo a tela de todas as
      páginas (marcar/desmarcar). Na janela, ver a página ao lado, folhear e dar zoom." · 26/10:
      "eu quero poder sim fazer automatico para todo livro, mas também quero pode fazer uma a uma."
  D-003 (28/09) + D-016: a ordem das etapas muda arrastando (a ordem em que RODAM; a montagem da
      página segue a ordem obrigatória).
  D-068 (24/09): "Toda função automática tem botão de ligar e desligar." (a caixinha de cada
      etapa e "Desligar as marcadas").
  D-071 (`fr-219`, 22/10): "Mas ainda pode melhorar a caixa de como escolhemos o que vai dentro
      da receita." (CaixaDaReceita: o que vai, escrito por extenso, etapa por etapa).
  D-577 (29/10/2026): "eu queria poder nessa etapa do automatico poder ver como iria ficar
      conforme as opções que eu fosse escolhendo." → a página da direita da janela grande mostra
      o antes e depois da página da vez, com a linha que se arrasta, e a bolinha de carregamento
      enquanto calcula ("sim, mas coloca uma bolinha de carregamento como fez na area de
      trabalho"). Substitui a D-486 (a página original). PaginaAntesEDepois.
  Tudo o que morava na tela "O que fazer" (ui/tela_opcoes.py, que saiu do caminho) mora aqui,
  em grupos: Página (Dividir, Endireitar, Cortar), Limpeza (Limpar a folha: filtros, "Só as
  letras", força sozinha, molduras no Preto e branco, limpar a sujeira), Gravuras e fotos,
  Saída (Margens iguais, Montar cadernos). E a troca do retângulo do corte "do livro" (D-094).

O DESENHO (rodada 12b, `layout\\imagens\\19-rodada12b-automatico-painel.png` e
  `-automatico-janela.png`; rodada 2, `8-novo-automatico.png`)
  Painel: Receita (lista + "Salvar..."), "Etapas, na ordem em que rodam" (arraste para mudar),
  cada etapa com a caixinha e a frase; no pé, "Rodar N etapas", "abrir em janela grande" e
  "escolher páginas...". Janela: "O que o automático vai fazer", a receita no alto, as etapas
  à esquerda, as opções da etapa escolhida no meio, a página ao lado (folhear e zoom) e, embaixo,
  a frase do que vai acontecer, "escolher páginas...", "Fechar" e "Rodar N etapas".

COMO FUNCIONA
  EstadoDoAutomatico guarda o que está escolhido (as etapas marcadas, a ordem, as opções, a
  receita e onde rodar) e é o MESMO para o painel e a janela. Nada muda no livro até "Rodar": aí
  a janela principal (ui/janela_principal.rodar_o_automatico) monta o pedido
  (core/automatico.Pedido), pergunta das páginas mexidas à mão (D-004), mede por trás e grava no
  projeto aberto, numa ação do Histórico.

Seguro mudar: textos, tamanhos. Arriscado: gravar no projeto daqui (quem grava é a janela, com
o desfazer); tirar um controle (a prova "nenhuma opção da tela 'O que fazer' se perdeu",
tests/test_decisoes_automatico.py, confere `JanelaDoAutomatico.controles`).
"""

from __future__ import annotations

import copy

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core import automatico as A
from core import borda_preta, dividir_scantailor, endireitar_scantailor, margens_scantailor, misto
from core import perfis
from core import pontinhos_scantailor as pontinhos
from core.filtros import (MAGICO_PRO, MELHORAR, NOMES_AMIGAVEIS, ORIGINAL, PRETO_E_BRANCO,
                          TIRAR_FUNDO)
from ui import estilo
from ui.estilo import estilo_da_caixinha_com_quadrado

# Onde rodar (codigos internos)
NO_LIVRO, NA_PAGINA, NAS_ESCOLHIDAS = "livro", "pagina", "escolhidas"

FILTROS_DA_LIMPEZA = (
    (ORIGINAL, "Original", "não mexe na página"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado, arquivo pequeno"),
    (MELHORAR, "Melhorar", "limpa o fundo e mantém as cores"),
    (MAGICO_PRO, "Mágico pro", "cor viva e texto nítido"),
    (TIRAR_FUNDO, "Tirar o fundo", "tira o papel e deixa só o que está impresso"),
)
PAGINAS_POR_CADERNO = (8, 12, 16, 20, 24, 32, 40)

# D-093/D-094: o retângulo do corte quando o ângulo muda (códigos de core/pipeline)
RETANGULO_SEGUE = None
NOMES_DO_RETANGULO = (
    (None, "o das Configurações"),
    ("fica", "fica no mesmo lugar (como o ScanTailor)"),
    ("acompanha", "acompanha o texto"),
)


def _nome_do_jeito(jeito: str) -> str:
    from ui.widgets.paineis import nome_do_jeito_de_dividir

    return nome_do_jeito_de_dividir(jeito)


def _nome_da_conta(jeito: str) -> str:
    from ui.widgets.paineis import nome_da_conta

    return nome_da_conta(jeito)


def texto_das_opcoes(etapa: str, opcoes: dict) -> str:
    """O que a etapa vai fazer com as opções escolhidas, em português (a
    segunda linha da etapa no painel e a caixa da receita: D-071 quer ver "o
    que vai dentro")."""
    o = opcoes
    if etapa == A.DIVIDIR:
        return "jeito: " + _nome_do_jeito(dividir_scantailor.jeito_valido(o.get("dividir_como")))
    if etapa == A.ENDIREITAR:
        conta = _nome_da_conta(endireitar_scantailor.jeito_valido(o.get("endireitar_como")))
        return f"conta: {conta}"
    if etapa == A.CORTAR:
        partes = []
        if o.get("cortar_sobra"):
            partes.append("beirada da folha vizinha")
        if o.get("cortar_pelo_conteudo"):
            partes.append("seguindo o conteúdo")
        if o.get("borda_preta"):
            partes.append("borda preta: " + borda_preta.NOMES[borda_preta.jeito_valido(o.get("borda_preta_ate"))]
                          + ", " + borda_preta.NOMES_DO_FAZER[borda_preta.fazer_valido(o.get("borda_preta_fazer"))])
        return "; ".join(partes) if partes else "o corte de sempre"
    if etapa == A.LIMPAR:
        filtro = o.get("filtro_padrao", ORIGINAL)
        texto = NOMES_AMIGAVEIS.get(filtro, filtro)
        if filtro == PRETO_E_BRANCO:
            if o.get("misto_so_as_letras"):
                texto += ", só as letras"
            limpeza = pontinhos.escolha_valida(o.get("limpar_pontinhos", pontinhos.PADRAO))
            if limpeza != pontinhos.DESLIGADO:
                texto += ", " + pontinhos.NOMES_NA_TELA[limpeza].lower()
            if o.get("pb_decoracao_em_preto_e_branco") and not o.get("misto_so_as_letras"):
                texto += ", molduras em preto e branco"
        return texto
    if etapa == A.GRAVURAS:
        forma = o.get("gravura_forma", "livre")
        if forma == "desligada":
            return "não procurar gravuras"
        texto = "fotos em retângulo" if forma == "retangular" else "seguindo o desenho"
        if o.get("gravura_mais_sensivel"):
            texto += ", também imagens claras"
        return texto
    if etapa == A.MARGENS:
        mm = margens_scantailor.Margens.de(o.get("margens_mm")).como_lista()
        return "margens " + " / ".join(f"{v:g}" for v in mm) + " mm"
    if etapa == A.CADERNOS:
        return f"{o.get('paginas_por_caderno', 20)} páginas por caderno"
    return ""


# ---------------------------------------------------------------------------
# o estado (o mesmo para o painel e para a janela)
# ---------------------------------------------------------------------------

class EstadoDoAutomatico(QObject):
    """O que está escolhido no Automático: as etapas marcadas, a ordem, as
    opções, a receita e onde rodar. Não grava nada no livro: só monta o
    pedido (core/automatico.Pedido) quando a pessoa clica "Rodar"."""

    mudou = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.marcadas: set[str] = set()
        self.ordem: list[str] = list(A.ORDEM_DE_FABRICA)
        self.opcoes: dict = {}
        self.receita = ""
        self.alcance = NO_LIVRO
        self.escolhidas: list[int] = []
        self.pagina_atual = 0
        self.total_paginas = 0
        self.tem_camadas = False
        self.situacoes: dict[str, str] = {}

    # --- de onde vem ---------------------------------------------------------

    def do_projeto(self, projeto, receita: str | None = None) -> None:
        """Começa do livro: as opções e a ordem dele, e as etapas que já estão
        ligadas (no livro ou em alguma página). Com `receita`, a receita por
        cima (o aviso do livro novo marca a receita de sempre, D-018)."""
        self.opcoes = A.opcoes_do_livro(projeto)
        self.ordem = A.ordem(projeto)
        self.marcadas = set(A.etapas_ligadas(projeto))
        self.receita = getattr(projeto, "receita_usada", "") or ""
        self.total_paginas = len(getattr(projeto, "paginas", []))
        self.tem_camadas = bool(getattr(projeto, "tem_camadas", False))
        self.acertar_situacoes(projeto)
        if receita:
            self.por_receita(receita, avisar=False)
        self.mudou.emit()

    def acertar_situacoes(self, projeto) -> None:
        """Onde cada etapa está ligada hoje ("ligada no livro todo",
        "ligada em 3 páginas", "desligada"), para o painel mostrar."""
        self.situacoes = {e: A.situacao(projeto, e) for e in A.ETAPAS}
        self.total_paginas = len(getattr(projeto, "paginas", []))

    def por_receita(self, nome: str, avisar: bool = True) -> bool:
        """Põe a receita guardada: marca as etapas dela e as opções dela.
        Não muda o livro (só quando "Rodar")."""
        dados = perfis.ler(nome)
        if dados is None:
            return False
        for campo, valor in dados.items():
            if campo in perfis.CAMPOS:
                self.opcoes[campo] = copy.deepcopy(valor)
        self.marcadas = set(perfis.etapas_da_receita(dados))
        self.receita = nome
        if avisar:
            self.mudou.emit()
        return True

    # --- mexer -----------------------------------------------------------------

    def marcar(self, etapa: str, sim: bool) -> None:
        antes = set(self.marcadas)
        (self.marcadas.add if sim else self.marcadas.discard)(etapa)
        if self.marcadas != antes:
            self.mudou.emit()

    def definir_ordem(self, ordem: list[str]) -> None:
        nova = [e for e in ordem if e in A.ETAPAS]
        nova += [e for e in self.ordem if e not in nova]
        if nova != self.ordem:
            self.ordem = nova
            self.mudou.emit()

    def mover(self, de: int, para: int) -> None:
        """Muda a ordem como o arrastar faz (D-003): a etapa da posição `de`
        vai para a posição `para`."""
        ordem = list(self.ordem)
        if not (0 <= de < len(ordem)) or not (0 <= para < len(ordem)):
            return
        ordem.insert(para, ordem.pop(de))
        self.definir_ordem(ordem)

    def definir_opcao(self, campo: str, valor) -> None:
        if self.opcoes.get(campo) != valor:
            self.opcoes[campo] = copy.deepcopy(valor)
            self.mudou.emit()

    def definir_alcance(self, alcance: str, escolhidas: list[int] | None = None) -> None:
        self.alcance = alcance
        if escolhidas is not None:
            self.escolhidas = sorted(set(int(i) for i in escolhidas))
        self.mudou.emit()

    # --- o pedido --------------------------------------------------------------

    def etapas_marcadas(self) -> list[str]:
        """As marcadas, na ordem em que rodam."""
        return [e for e in self.ordem if e in self.marcadas]

    def paginas(self) -> list[int] | None:
        """As páginas em que rodar (None = o livro todo)."""
        if self.alcance == NA_PAGINA:
            return [self.pagina_atual]
        if self.alcance == NAS_ESCOLHIDAS:
            return list(self.escolhidas)
        return None

    def pedido(self, pular_mexidas: bool = True, desligar: bool = False) -> A.Pedido:
        """O pedido do "Rodar" (ou do "Desligar as marcadas"). Leva também as
        etapas desmarcadas (D-589: "Montar cadernos" desmarcada desliga no
        "Rodar"; core/automatico.Pedido.desmarcadas)."""
        return A.Pedido(etapas=self.etapas_marcadas(), opcoes=copy.deepcopy(self.opcoes),
                        paginas=self.paginas(), pular_mexidas=pular_mexidas,
                        receita=self.receita, desligar=desligar, ordem=list(self.ordem),
                        desmarcadas=[e for e in self.ordem if e not in self.marcadas])

    def frase(self) -> str:
        """A frase de baixo da janela (como no desenho aprovado)."""
        filtro = self.opcoes.get("filtro_padrao", ORIGINAL)
        frase = A.resumo(self.pedido(), self.total_paginas, NOMES_AMIGAVEIS.get(filtro, ""))
        if A.LIMPAR in self.marcadas and filtro == PRETO_E_BRANCO:
            # o que o Preto e branco vai fazer de verdade (ressalva 4 do
            # verificador do Misto, 05/10: com "Só as letras" a frase não pode
            # dizer "deixar tudo em preto e branco"); o texto e o de sempre,
            # core/pipeline._frase_do_so_as_letras
            from core.pipeline import _frase_do_so_as_letras
            from modelos import Projeto

            if self.opcoes.get("misto_so_as_letras"):
                livro = Projeto(caminho_entrada="")
                for campo, valor in self.opcoes.items():
                    if hasattr(livro, campo):
                        setattr(livro, campo, valor)
                livro.limpar = True
                frase += " No Preto e branco: " + _frase_do_so_as_letras(livro) + "."
            else:
                frase += " No Preto e branco: deixar tudo em preto e branco."
        return frase


# ---------------------------------------------------------------------------
# a lista das etapas (arrastar muda a ordem; a caixinha marca)
# ---------------------------------------------------------------------------

class ListaDeEtapas(QListWidget):
    """As etapas, na ordem em que rodam, com a caixinha de cada uma. Arrastar
    com o mouse muda a ordem (D-003: "muda arrastando com o mouse. Sem
    cadeados."). Mostra a pista de que se arrasta (o cursor de mão aberta e a
    frase de cima). Duplo clique numa etapa pede para ajustar (abre a janela
    grande nela)."""

    etapa_escolhida = Signal(str)
    ajustar_pedido = Signal(str)

    def __init__(self, estado: EstadoDoAutomatico, compacta: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.estado = estado
        self.compacta = compacta
        self.setObjectName("listaDeEtapas")
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setWordWrap(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   # o texto quebra; nada de rolar de lado
        self.setSpacing(2)
        self.viewport().setCursor(Qt.OpenHandCursor)
        self.setToolTip("Arraste uma etapa para mudar a ordem em que elas rodam. "
                        "A caixinha liga ou desliga a etapa.")
        # a ordem nova e lida NA HORA do movimento (uma atualizacao da tela antes
        # do relogio remontaria a lista com a ordem velha) e entra no estado
        # logo depois (remontar a lista dentro do proprio sinal do Qt nao pode)
        self.model().rowsMoved.connect(lambda *_: self._arrastou())
        self.itemChanged.connect(self._marcou)
        self.currentItemChanged.connect(self._escolheu)
        self.itemDoubleClicked.connect(lambda item: self.ajustar_pedido.emit(item.data(Qt.UserRole)))
        estado.mudou.connect(self.refazer)
        estilo.estilizar(self, lambda: (
            f"QListWidget#listaDeEtapas {{ background: transparent; border: none; }}"
            f"QListWidget#listaDeEtapas::item {{ background: {estilo.cor('botao')};"
            f" border: 1px solid {estilo.cor('sep')}; border-radius: 6px; padding: 6px 6px;"
            f" color: {estilo.cor('texto')}; }}"
            f"QListWidget#listaDeEtapas::item:selected {{ border: 1px solid {estilo.cor('azul')};"
            f" background: {estilo.cor('sel')}; color: {estilo.cor('forte')}; }}"))
        self.refazer()

    def refazer(self) -> None:
        """Remonta as linhas a partir do estado (sem avisar ninguém)."""
        atual = self.currentItem().data(Qt.UserRole) if self.currentItem() else None
        self.blockSignals(True)
        try:
            self.clear()
            for n, etapa in enumerate(self.estado.ordem, start=1):
                detalhe = texto_das_opcoes(etapa, self.estado.opcoes)
                situacao = self.estado.situacoes.get(etapa, "")
                # o painel e estreito: so o nome e onde esta ligada; a janela
                # mostra tambem o jeito escolhido
                segunda = situacao if self.compacta else (
                    detalhe + (f" · {situacao}" if situacao else ""))
                item = QListWidgetItem(f"{n}  {A.NOMES[etapa]}\n{segunda}")
                item.setData(Qt.UserRole, etapa)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
                              | Qt.ItemIsDragEnabled)
                item.setCheckState(Qt.Checked if etapa in self.estado.marcadas else Qt.Unchecked)
                item.setToolTip(f"{A.NOMES[etapa]}: {A.EXPLICACOES[etapa]}. {detalhe}."
                                + (f" Hoje: {situacao}." if situacao else "")
                                + " Arraste para mudar a ordem; duplo clique para ajustar.")
                self.addItem(item)
                if etapa == atual:
                    self.setCurrentItem(item)
        finally:
            self.blockSignals(False)

    def etapas_na_lista(self) -> list[str]:
        return [self.item(i).data(Qt.UserRole) for i in range(self.count())]

    def _arrastou(self) -> None:
        ordem = self.etapas_na_lista()
        QTimer.singleShot(0, lambda: self.estado.definir_ordem(ordem))

    def _marcou(self, item: QListWidgetItem) -> None:
        self.estado.marcar(item.data(Qt.UserRole), item.checkState() == Qt.Checked)

    def _escolheu(self, item, _antes) -> None:
        if item is not None:
            self.etapa_escolhida.emit(item.data(Qt.UserRole))

    def item_da_etapa(self, etapa: str) -> QListWidgetItem | None:
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == etapa:
                return self.item(i)
        return None

    def escolher(self, etapa: str) -> None:
        item = self.item_da_etapa(etapa)
        if item is not None:
            self.setCurrentItem(item)


class _ComboDoAlcance(QComboBox):
    """A lista "Rodar em:" (o livro todo / só esta página / as escolhidas).

    E uma classe (e nao uma funcao solta ligada ao `estado.mudou`) de proposito:
    o Qt desliga sozinho o sinal de um METODO de um objeto que foi apagado. Com
    uma funcao solta, fechar a janela grande deixava o sinal apontando para a
    lista apagada, e o Desfazer seguinte dava "already deleted" (achado pelo
    teste_botoes.py na etapa 3 da obra)."""

    def __init__(self, estado: EstadoDoAutomatico) -> None:
        super().__init__()
        self.estado = estado
        self.setObjectName("comboDoAlcance")
        self.setToolTip("Onde o automático vai rodar: no livro todo, só na página que está "
                        "na tela, ou nas páginas escolhidas em \"escolher páginas...\".")
        self.currentIndexChanged.connect(self._escolheu)
        estado.mudou.connect(self.encher)
        self.encher()

    def _escolheu(self, _indice: int) -> None:
        self.estado.definir_alcance(self.currentData())

    def encher(self) -> None:
        estado = self.estado
        self.blockSignals(True)
        self.clear()
        self.addItem("no livro todo", NO_LIVRO)
        self.addItem(f"só nesta página ({estado.pagina_atual + 1})", NA_PAGINA)
        quantas = len(estado.escolhidas)
        self.addItem(f"nas páginas escolhidas ({quantas})", NAS_ESCOLHIDAS)
        self.setCurrentIndex(max(0, self.findData(estado.alcance)))
        self.blockSignals(False)


def _combo_do_alcance(estado: EstadoDoAutomatico) -> QComboBox:
    """A lista "Rodar em:" (ver _ComboDoAlcance)."""
    return _ComboDoAlcance(estado)


def _texto_do_rodar(estado: EstadoDoAutomatico) -> str:
    n = len(estado.marcadas)
    return f"Rodar {n} etapa" + ("" if n == 1 else "s")


# ---------------------------------------------------------------------------
# o painel (a coluna da direita)
# ---------------------------------------------------------------------------

def _classe_do_painel():
    """A classe Painel de ui/widgets/paineis.py. Este arquivo importa o de lá;
    o de lá importa este só quando monta a coluna (ColunaDePaineis), para os
    dois nunca se importarem na volta."""
    from ui.widgets.paineis import Painel

    return Painel


class PainelAutomatico(_classe_do_painel()):
    """O painel "Automático" (desenho da rodada 12b): receita, as etapas na
    ordem em que rodam (arrastar, marcar), onde rodar e "Rodar N etapas",
    "abrir em janela grande", "escolher páginas..." e "Desligar as marcadas".
    Os botões só PEDEM (sinais): quem roda é a janela principal."""

    rodar_pedido = Signal()
    desligar_pedido = Signal()
    janela_pedida = Signal(str)         # a etapa a ajustar ("" = a primeira)
    escolher_pedido = Signal()
    receita_guardar_pedida = Signal()

    def __init__(self, titulo: str = "Automático", parent=None) -> None:
        super().__init__(titulo, parent)
        from ui.widgets.paineis import frase_do_painel, risco_do_painel

        self.estado = EstadoDoAutomatico(self)
        linha = QHBoxLayout()
        linha.setSpacing(6)
        self.combo_receitas = QComboBox()
        self.combo_receitas.setToolTip("Um jeito de trabalhar guardado com um nome: as etapas "
                                       "marcadas e as opções delas. Escolher põe a receita aqui "
                                       "(o livro só muda ao rodar).")
        self.combo_receitas.activated.connect(lambda _i: self._escolheu_receita())
        linha.addWidget(self.combo_receitas, 1)
        self.botao_salvar = QPushButton("Salvar...")
        self.botao_salvar.setToolTip("Guarda as etapas marcadas e as opções delas como receita.")
        self.botao_salvar.clicked.connect(lambda: self.receita_guardar_pedida.emit())
        linha.addWidget(self.botao_salvar)
        self.dentro.addWidget(QLabel("Receita"))
        self.dentro.addLayout(linha)
        self.dentro.addWidget(risco_do_painel())
        self.dentro.addWidget(QLabel("Etapas, na ordem em que rodam"))
        self.dentro.addWidget(frase_do_painel("arraste para mudar a ordem; a caixinha liga e desliga"))
        self.lista = ListaDeEtapas(self.estado, compacta=True)
        self.lista.setMinimumHeight(7 * 46)
        # Etapa 9b-1 (achado das etapas 5 e 6: "com o foco na lista do
        # Automático, as letras vão para a lista"): a lista do painel não
        # pega o teclado, como os botões dele (NoFocus, mais abaixo). O mouse
        # continua igual: clicar escolhe a etapa, a caixinha liga e desliga,
        # arrastar muda a ordem, duplo clique ajusta. As teclas (D, X, I, F,
        # 1-4, Page Down...) continuam indo para a página. A lista da janela
        # grande (JanelaDoAutomatico) não muda: lá não há página atrás.
        # Arriscado: devolver o foco à lista do painel.
        self.lista.setFocusPolicy(Qt.NoFocus)
        self.lista.ajustar_pedido.connect(self.janela_pedida.emit)
        self.dentro.addWidget(self.lista)
        self.botao_ajustar = QPushButton("ajustar a etapa escolhida ›")
        self.botao_ajustar.setObjectName("plano")
        self.botao_ajustar.setCursor(Qt.PointingHandCursor)
        self.botao_ajustar.clicked.connect(self._ajustar)
        self.dentro.addWidget(self.botao_ajustar)

        # o pé, sempre à vista (o desenho: o "Rodar" preso no pé)
        onde = QHBoxLayout()
        onde.addWidget(QLabel("Rodar"))
        self.combo_alcance = _combo_do_alcance(self.estado)
        onde.addWidget(self.combo_alcance, 1)
        self.no_pe.addLayout(onde)
        self.botao_rodar = QPushButton(_texto_do_rodar(self.estado))
        self.botao_rodar.setObjectName("primario")
        self.botao_rodar.setCursor(Qt.PointingHandCursor)
        self.botao_rodar.clicked.connect(lambda: self.rodar_pedido.emit())
        self.no_pe.addWidget(self.botao_rodar)
        linha2 = QHBoxLayout()
        self.botao_janela = QPushButton("abrir em janela grande")
        self.botao_janela.clicked.connect(lambda: self.janela_pedida.emit(""))
        self.botao_escolher = QPushButton("escolher páginas...")
        self.botao_escolher.setToolTip("Abre todas as páginas do livro para marcar em quais o "
                                       "automático vai rodar.")
        self.botao_escolher.clicked.connect(lambda: self.escolher_pedido.emit())
        linha2.addWidget(self.botao_janela)
        linha2.addWidget(self.botao_escolher)
        self.no_pe.addLayout(linha2)
        self.botao_desligar = QPushButton("desligar as marcadas")
        self.botao_desligar.setObjectName("plano")
        self.botao_desligar.setToolTip("Tira o automático das etapas marcadas, onde está "
                                       "escolhido em \"Rodar\" (D-068: toda função automática "
                                       "liga e desliga). O Desfazer traz de volta.")
        self.botao_desligar.clicked.connect(lambda: self.desligar_pedido.emit())
        self.no_pe.addWidget(self.botao_desligar)
        self.pe.setVisible(True)
        for botao in (self.botao_salvar, self.botao_rodar, self.botao_janela, self.botao_escolher,
                      self.botao_desligar, self.botao_ajustar):
            botao.setFocusPolicy(Qt.NoFocus)
        self.estado.mudou.connect(self._estado_mudou)
        self.encher_receitas()

    def encher_receitas(self) -> None:
        """A lista das receitas guardadas (a escolhida fica à vista)."""
        self.combo_receitas.blockSignals(True)
        self.combo_receitas.clear()
        self.combo_receitas.addItem("(nenhuma)", "")
        for nome in perfis.nomes():
            self.combo_receitas.addItem(nome, nome)
        self.combo_receitas.setCurrentIndex(max(0, self.combo_receitas.findData(self.estado.receita)))
        self.combo_receitas.blockSignals(False)

    def _escolheu_receita(self) -> None:
        nome = self.combo_receitas.currentData()
        if nome:
            self.estado.por_receita(nome)

    def _ajustar(self) -> None:
        item = self.lista.currentItem()
        self.janela_pedida.emit(item.data(Qt.UserRole) if item else "")

    def _estado_mudou(self) -> None:
        self.botao_rodar.setText(_texto_do_rodar(self.estado))
        self.botao_rodar.setEnabled(bool(self.estado.marcadas))
        self.botao_desligar.setEnabled(bool(self.estado.marcadas))
        indice = self.combo_receitas.findData(self.estado.receita)
        if indice >= 0 and indice != self.combo_receitas.currentIndex():
            self.combo_receitas.blockSignals(True)
            self.combo_receitas.setCurrentIndex(indice)
            self.combo_receitas.blockSignals(False)

    def atualizar(self, projeto) -> None:
        """A tela chama a cada atualização: acerta a situação de cada etapa
        (ligada no livro, em N páginas) e a página da vez. Não mexe no que a
        pessoa marcou."""
        if projeto is None:
            return
        self.estado.acertar_situacoes(projeto)
        self.estado.tem_camadas = bool(getattr(projeto, "tem_camadas", False))
        self.lista.refazer()
        self.combo_alcance.encher()
        self._estado_mudou()


# ---------------------------------------------------------------------------
# a página da direita da janela grande: antes e depois (D-577)
# ---------------------------------------------------------------------------

# A resolução em que a prévia desenha a página. Escolha técnica (pedido da
# gerente, item 6): o PDF é de 300 DPI, e desenhar a página inteira nele a cada
# opção trocada levaria vários segundos por página. Só o desenho é nesta
# resolução: o corte e o ângulo continuam medidos na resolução do PDF
# (core/pipeline.renderizar_pagina já faz assim, e guarda a medida para o rodar
# de verdade).
# Era 110 (a prévia "Rápida" da área de trabalho). Subiu para 180 (decisão da
# gerente, 30/10/2026, defeito D2 do verificador da D-577): no Mágico pro, a
# 110 DPI a prévia estragava letras que o PDF não estraga ("Nihil" virava
# "N h", "1955" virava "19 5", "vês" virava "ves"). Medido pelo verificador no
# *Na escola de Jesus*, Mágico pro, diferença da prévia para o PDF: página 5,
# 2,10% a 110 DPI e 1,02% a 180; página 41, 5,22% e 2,82%; uns 0,6 s a mais
# por conta. Seguro mudar: o número (mais alto = mais perto do PDF e mais
# lento); arriscado: descer de novo para 110 (as letras falham no Mágico pro).
DPI_DA_PREVIA = 180
# Quanto esperar depois da última troca antes de começar a conta (várias trocas
# seguidas, como as setinhas das margens, viram um pedido só). Seguro mudar.
ESPERA_ANTES_DE_CALCULAR_MS = 200
# Entre as duas páginas que uma folha dividida vira, no "depois" (pontos da
# imagem, na resolução da prévia).
VAO_ENTRE_AS_METADES = 12


class _Guardiao(QObject):
    """Segura as tarefas da prévia até elas terminarem, mesmo depois de a
    janela grande fechar (uma QThread apagada no meio da conta derruba o
    programa). Vive no fio da janela; um só para o programa (_guardiao())."""

    def __init__(self) -> None:
        super().__init__()
        self.tarefas: set = set()

    def segurar(self, tarefa) -> None:
        self.tarefas.add(tarefa)
        tarefa.terminou.connect(self.soltar)

    def soltar(self, tarefa) -> None:
        self.tarefas.discard(tarefa)
        tarefa.deleteLater()


_O_GUARDIAO: _Guardiao | None = None


def _guardiao() -> _Guardiao:
    global _O_GUARDIAO
    if _O_GUARDIAO is None:
        _O_GUARDIAO = _Guardiao()
    return _O_GUARDIAO


# Quanto esperar, ao fechar o programa, a conta da prévia que estiver rodando.
# Ela só para entre a medida, o aplicar e o desenho: o desenho de uma página já
# começado termina (alguns segundos no pior caso). Seguro mudar: para mais.
ESPERA_AO_SAIR_MS = 60000


def parar_as_previas(espera_ms: int = ESPERA_AO_SAIR_MS) -> None:
    """Ao fechar o programa (ui/janela_principal.closeEvent): pede a toda conta
    da prévia do antes e depois (D-577) que pare, e espera cada uma terminar.
    Defeito achado pelo verificador da D-577 (30/10/2026): fechar o programa
    com uma conta rodando deixava a QThread viva no _Guardiao, e o processo
    saía quebrado (código 127), como já acontecia com as outras tarefas
    antes de o closeEvent esperar por elas. Arriscado: não esperar."""
    if _O_GUARDIAO is None:
        return
    tarefas = list(_O_GUARDIAO.tarefas)
    for tarefa in tarefas:
        tarefa.cancelar()
    for tarefa in tarefas:
        tarefa.wait(espera_ms)


def _classe_da_vista():
    """VistaAntesDepois (ui/widgets/filtros_tela_cheia.py), importada só aqui
    (o mesmo jeito de _classe_do_painel)."""
    from ui.widgets.filtros_tela_cheia import VistaAntesDepois

    return VistaAntesDepois


class VistaAntesDepoisComZoom(_classe_da_vista()):
    """O "antes / depois" que já existe na área de trabalho (VistaAntesDepois:
    o antes à esquerda da linha, o depois à direita, a linha se arrasta), com
    duas coisas a mais que a janela grande do Automático precisa:

      - antes e depois de tamanhos diferentes (cortar, endireitar e dividir
        mudam o tamanho da página): os dois vão para uma tela do mesmo tamanho
        (o maior dos dois), cada um no meio dela, na MESMA escala (a mesma
        resolução de desenho). Assim a linha não estica nenhum dos dois, e a
        página cortada aparece menor, como vai sair. O que sobra em volta tem
        a cor do fundo da janela.
      - o zoom (−, +, ajustar à tela), como o folhear tinha (D-002, rodada 2
        nº 5: "Na janela, ver a página ao lado, folhear e dar zoom."): ela
        fica dentro de uma área de rolar, e o zoom muda o tamanho dela (1 =
        cabendo na área).

    `zoom`, definir_zoom e ajustar_a_tela têm os nomes do Visualizador do
    folhear (a janela grande e a prova P-187 usam esses nomes).
    Seguro mudar: os limites do zoom. Arriscado: desenhar o antes esticado no
    tamanho do depois (a página cortada pareceria do tamanho da inteira)."""

    def __init__(self, rolagem: QScrollArea, parent=None) -> None:
        super().__init__(parent)
        self.rolagem = rolagem
        self.zoom = 1.0
        self._crus: tuple = (None, None)         # (antes, depois) como chegaram (numpy)
        self._fundo_usado = ""

    def mostrar(self, antes, depois, rotulos=("antes", "depois"), aviso: str = "") -> None:
        """Põe o antes e o depois (numpy, ou None enquanto não chegam)."""
        self._crus = (antes, depois)
        self._fundo_usado = ""
        self.rotulos, self.aviso = rotulos, aviso
        self._montar()

    def _montar(self) -> None:
        from ui.widgets.visualizador import numpy_para_qimage

        antes, depois = self._crus
        fundo = estilo.cor("tela")
        self._fundo_usado = fundo
        pix = [None if img is None else QPixmap.fromImage(numpy_para_qimage(img))
               for img in (antes, depois)]
        if pix[0] is not None and pix[1] is not None and pix[0].size() != pix[1].size():
            largura = max(pix[0].width(), pix[1].width())
            altura = max(pix[0].height(), pix[1].height())
            pix = [_no_meio(p, largura, altura, fundo) for p in pix]
        self.antes, self.depois = pix
        self.comparando = self.antes is not None and self.depois is not None
        if self.depois is None and self.antes is not None:
            # o depois ainda não chegou: o antes sozinho (a bolinha gira ao lado)
            self.depois, self.antes, self.comparando = self.antes, None, False
        self.update()

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if self._fundo_usado and self._fundo_usado != estilo.cor("tela"):
            self._montar()                 # o tema mudou: o que sobra em volta acompanha
        super().paintEvent(evento)

    def definir_zoom(self, zoom: float) -> None:
        self.zoom = max(0.2, min(8.0, float(zoom)))
        if abs(self.zoom - 1.0) < 1e-6:
            self.ajustar_a_tela()
            return
        area = self.rolagem.viewport().size()
        self.rolagem.setWidgetResizable(False)
        self.resize(max(50, int(area.width() * self.zoom)), max(50, int(area.height() * self.zoom)))

    def ajustar_a_tela(self) -> None:
        self.zoom = 1.0
        self.rolagem.setWidgetResizable(True)


def _no_meio(pix: QPixmap, largura: int, altura: int, fundo: str) -> QPixmap:
    """`pix` no meio de uma tela largura x altura da cor `fundo`."""
    tela = QPixmap(largura, altura)
    tela.fill(QColor(fundo))
    pintor = QPainter(tela)
    pintor.drawPixmap((largura - pix.width()) // 2, (altura - pix.height()) // 2, pix)
    pintor.end()
    return tela


def _lado_a_lado(imagens: list):
    """As páginas que uma folha vira (o "depois" de uma folha inteira que vai
    ser dividida), uma ao lado da outra, na ordem do PDF, com um vão branco
    entre elas. Uma só: ela mesma. Nenhuma: None."""
    import numpy as np

    imagens = [img for img in imagens if img is not None]
    if not imagens:
        return None
    if len(imagens) == 1:
        return imagens[0]
    cores = 3 if any(img.ndim == 3 for img in imagens) else 1
    altura = max(img.shape[0] for img in imagens)
    pedacos = []
    for n, img in enumerate(imagens):
        if cores == 3 and img.ndim == 2:
            img = np.repeat(img[:, :, None], 3, axis=2)
        if img.shape[0] < altura:
            resto = np.full((altura - img.shape[0],) + img.shape[1:], 255, img.dtype)
            img = np.concatenate([img, resto], axis=0)
        if n:
            pedacos.append(np.full((altura, VAO_ENTRE_AS_METADES) + img.shape[2:], 255, img.dtype))
        pedacos.append(img)
    return np.concatenate(pedacos, axis=1)


class TelaCheiaDoAntesEDepois(QDialog):
    """O "tela cheia" da página da direita da janela grande do Automático (D-577, 30/10/2026).

    Samuel, depois do teste de 30/10 (print a-08: o "tela cheia" mostrava a folha crua do PDF):
    "tem que dar para ver na previa em tela grande e poder dar zoom na previa em tela grande".

    O QUE MOSTRA: o MESMO antes e depois da PaginaAntesEDepois que a abriu (as mesmas imagens,
    nada é calculado de novo), grande, com a linha que se arrasta, e:
      - o zoom: –, + e "ajustar à tela", os mesmos da janela grande (VistaAntesDepoisComZoom
        numa área de rolar, a vista que a página da direita já usa);
      - o folhear: "<" e ">" e as setas do teclado (como a TelaCheiaDoPDF de antes já
        folheava). Folhear aqui é folhear a página da direita (PaginaAntesEDepois.virar): a
        conta do antes e depois da página nova é a dela, e a bolinha gira aqui também;
      - "fechar" (e Esc) volta para a janela grande, na página em que parou;
      - "comparar" (D-577, 30/10, depois do 2º teste: "na tela cheia vai ter um botão de
        comparação , ai vão aparecer duas telas para comparar" · "nessa vai ter o filtro que
        estava antes, seja ele original ou que foi aplicado e o filtro que está selecionado
        no momento"): duas telas lado a lado, à esquerda a página como está agora no livro
        (com o filtro que ela já tem) e à direita o "depois" (o que está escolhido na
        janela), cada uma com o rótulo dela. O jeito é o do "comparar" do "Ver de perto"
        (ui/tela_ampliada.py): dois Visualizador, o zoom e a posição andam juntos (a roda
        do mouse e o arrastar também). Apertar de novo volta ao antes e depois com a linha.
    Quem põe as imagens, o "página N de M", os botões e a bolinha é a PaginaAntesEDepois
    (_acertar_tela_cheia): esta janela só mostra. Abre maximizada, como a TelaCheiaDoPDF.
    A página como está no livro só é desenhada com o "comparar" ligado (custa um desenho a
    mais por página).

    Seguro mudar: tamanhos e margens. Arriscado: calcular aqui uma prévia própria (duas
    contas da mesma página, e a tela cheia poderia mostrar outra coisa que a janela)."""

    def __init__(self, painel: "PaginaAntesEDepois") -> None:
        super().__init__(painel)
        from PySide6.QtGui import QGuiApplication

        from ui.widgets.bolinha import BolinhaDeCarregamento

        self.painel = painel
        self.setWindowTitle("A página, antes e depois")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO)
        self.setSizeGripEnabled(True)
        self._mostrado: tuple = (None, None, None)      # (antes, depois, aviso) já postos na vista

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(14, 14, 14, 12)
        camadas.setSpacing(8)
        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        self.rolagem.setAlignment(Qt.AlignCenter)
        self.visor = VistaAntesDepoisComZoom(self.rolagem)
        self.visor.setToolTip(painel.visor.toolTip())
        self.visor.posicao = painel.visor.posicao        # a linha onde estava na janela
        self.rolagem.setWidget(self.visor)
        camadas.addWidget(self.rolagem, 1)

        # o "comparar": duas telas lado a lado, como no "Ver de perto" (ui/tela_ampliada.py)
        from ui.widgets.visualizador import MODO_NENHUM, Visualizador

        self.comparando = False
        self.duas = QWidget()
        lado = QHBoxLayout(self.duas)
        lado.setContentsMargins(0, 0, 0, 0)
        lado.setSpacing(10)
        self.rotulo_a, self.rotulo_b = QLabel(""), QLabel("")
        self.vista_a, self.vista_b = Visualizador(), Visualizador()
        for rotulo, vista in ((self.rotulo_a, self.vista_a), (self.rotulo_b, self.vista_b)):
            coluna = QVBoxLayout()
            coluna.setSpacing(4)
            rotulo.setAlignment(Qt.AlignCenter)
            coluna.addWidget(rotulo)
            vista.definir_modo(MODO_NENHUM)
            coluna.addWidget(vista, 1)
            lado.addLayout(coluna, 1)
        self.vista_a.vista_mudou.connect(self._vista_a_mudou)
        self.vista_b.vista_mudou.connect(self._vista_b_mudou)
        self.duas.setVisible(False)
        camadas.addWidget(self.duas, 1)

        barra = QHBoxLayout()
        barra.setSpacing(8)
        self.botao_anterior = QPushButton("<")
        self.botao_anterior.setFixedWidth(44)
        self.botao_anterior.clicked.connect(lambda: painel.virar(-1))
        barra.addWidget(self.botao_anterior)
        self.contador = QLabel("")
        self.contador.setAlignment(Qt.AlignCenter)
        barra.addWidget(self.contador, 1)
        self.bolinha = BolinhaDeCarregamento()
        barra.addWidget(self.bolinha)
        self.botao_proxima = QPushButton(">")
        self.botao_proxima.setFixedWidth(44)
        self.botao_proxima.clicked.connect(lambda: painel.virar(1))
        barra.addWidget(self.botao_proxima)
        # o zoom: os mesmos botões, dicas e passos da janela grande (JanelaDoAutomatico._zoom)
        self.botao_menos = QPushButton("–")
        self.botao_menos.setToolTip("afastar")
        self.botao_menos.clicked.connect(lambda: self._zoom(0.8))
        self.botao_mais = QPushButton("+")
        self.botao_mais.setToolTip("aproximar")
        self.botao_mais.clicked.connect(lambda: self._zoom(1.25))
        for botao in (self.botao_menos, self.botao_mais):
            botao.setMinimumWidth(44)
            barra.addWidget(botao)
        self.botao_caber = QPushButton("ajustar à tela")
        self.botao_caber.clicked.connect(lambda: self._zoom(None))
        barra.addWidget(self.botao_caber)
        self.botao_comparar = QPushButton("comparar")
        self.botao_comparar.setCheckable(True)
        self.botao_comparar.clicked.connect(lambda *_: self._alternar_comparar())
        barra.addWidget(self.botao_comparar)
        fechar = QPushButton("fechar")
        fechar.setObjectName("primario")
        fechar.clicked.connect(self.accept)
        barra.addWidget(fechar)
        camadas.addLayout(barra)

        # o tamanho da tela pedido ANTES de maximizar (o mesmo cuidado da TelaCheiaDoPDF: se o
        # Windows ignorar o maximizar, o pior caso ainda é uma janela grande)
        tela = self.screen() or QGuiApplication.primaryScreen()
        if tela is not None:
            self.setGeometry(tela.availableGeometry())
        self.setWindowState(Qt.WindowMaximized)

    def acertar(self, antes, depois, aviso: str, contador: str, anterior: bool, proxima: bool,
                calculando: bool, indice: int = -1, do_livro=None, nome_do_livro: str = "",
                nome_depois: str = "") -> None:
        """Põe o que a página da direita mostra agora (só refaz a imagem quando ela mudou) e,
        no "comparar", as duas telas: a página como está no livro (`do_livro`, None enquanto
        não chega) e o depois, com os nomes dos filtros nos rótulos."""
        if (self._mostrado[0] is not antes or self._mostrado[1] is not depois
                or self._mostrado[2] != aviso):
            self._mostrado = (antes, depois, aviso)
            self.visor.mostrar(antes, depois, aviso=aviso)
        if self.comparando:
            # depois de _lado_a_lado: o mesmo "depois" do antes e depois (as duas metades,
            # quando a folha é dividida)
            depois_cru = self.visor._crus[1]
            self.vista_a.definir_imagem(do_livro, dono=("pagina", indice))
            self.vista_b.definir_imagem(depois_cru, dono=("pagina", indice))
            self.rotulo_a.setText(f"como está no livro: {nome_do_livro}" if nome_do_livro
                                  else "como está no livro")
            self.rotulo_b.setText(f"depois: {nome_depois}" if nome_depois else "depois")
        self.contador.setText(contador)
        self.botao_anterior.setEnabled(anterior)
        self.botao_proxima.setEnabled(proxima)
        self.bolinha.definir(calculando, "Calculando como a página vai ficar..." if calculando else "")

    def _zoom(self, fator: float | None) -> None:
        """–, + e "ajustar à tela" (a mesma conta de JanelaDoAutomatico._zoom). No "comparar",
        nas duas telas juntas (a da direita copia a da esquerda, como no "Ver de perto")."""
        if self.comparando:
            if fator is None:
                self.vista_a.ajustar_a_tela()
                self.vista_b.ajustar_a_tela()
            else:
                self.vista_a.definir_zoom(self.vista_a.zoom * fator)
            return
        if fator is None:
            self.visor.ajustar_a_tela()
        else:
            self.visor.definir_zoom(max(0.1, min(8.0, self.visor.zoom * fator)))

    def _vista_a_mudou(self, zoom: float, deslocamento) -> None:
        if self.comparando:
            self.vista_b.aplicar_vista(zoom, deslocamento)

    def _vista_b_mudou(self, zoom: float, deslocamento) -> None:
        if self.comparando:
            self.vista_a.aplicar_vista(zoom, deslocamento)

    def _alternar_comparar(self) -> None:
        """O botão "comparar": liga as duas telas (e pede a página como está no livro, se
        ela ainda não foi desenhada) ou volta ao antes e depois com a linha."""
        self.comparando = self.botao_comparar.isChecked()
        self.rolagem.setVisible(not self.comparando)
        self.duas.setVisible(self.comparando)
        if self.comparando:
            self.vista_b.aplicar_vista(self.vista_a.zoom, self.vista_a.deslocamento)
            self.painel.pedir(agora=True)
        else:
            self.vista_a.definir_imagem(None, dono=("nada",))   # solta as imagens
            self.vista_b.definir_imagem(None, dono=("nada",))
        self.painel._acertar_tela_cheia()

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Setas e Page Up/Down viram a página (como na TelaCheiaDoPDF); Esc fecha."""
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.painel.virar(-1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.painel.virar(1)
        else:
            super().keyPressEvent(evento)

    def done(self, resultado: int) -> None:  # noqa: D401 - nome do Qt
        """Ao fechar: a linha volta para a janela onde ficou aqui, e a página da direita
        esquece esta janela (não manda mais nada para ela)."""
        self.painel.visor.posicao = self.visor.posicao
        self.painel.visor.update()
        if self.painel.tela_cheia is self:
            self.painel.tela_cheia = None
        self._mostrado = (None, None, None)
        self.visor.mostrar(None, None)              # solta as imagens (uma página por vez)
        self.vista_a.definir_imagem(None, dono=("nada",))
        self.vista_b.definir_imagem(None, dono=("nada",))
        super().done(resultado)


class PaginaAntesEDepois(QWidget):
    """A página da direita da janela grande do Automático (D-577, 29/10/2026).

    Samuel: "eu queria poder nessa etapa do automatico poder ver como iria
    ficar conforme as opções que eu fosse escolhendo." Pergunta: "A página da
    direita passa a mostrar o antes e depois, com a linha que você arrasta. O
    lado do "depois" muda a cada opção que você marca ou desmarca." → "sim,
    mas coloca uma bolinha de carregamento como fez na area de trabalho,
    porque as vezes vai demorar para processar né?" (substitui a D-486, em que
    a página da direita era a original).

    O QUE MOSTRA: a página da vez, com o "antes" (a folha CRUA, como veio do
    PDF: sem filtro, sem cortar, sem endireitar, sem nada: core/automatico.
    antes_da_pagina; D-577, 30/10, depois do 2º teste: "o antes é sem filtro e
    sem cortar sem nada, o depois na tela de atualizar que aplica os filtros de
    endireitar cortar ou fazer qualquer outra coisa para ver como iria
    ficar."; até 30/10 era a página como está no livro, com o filtro dela) à
    esquerda da linha e o
    "depois" (como ela sai se rodar o Automático com as etapas marcadas e as opções escolhidas na janela) à
    direita. Folheia as páginas do livro ("<" e ">", as setas do teclado) e dá
    zoom (a janela grande liga os botões −, + e "ajustar à tela" ao `visor`).
    "tela cheia" abre o MESMO antes e depois, grande, com zoom e folhear
    (TelaCheiaDoAntesEDepois; D-577, 30/10: "tem que dar para ver na previa em
    tela grande e poder dar zoom na previa em tela grande"). Antes abria a
    folha crua do PDF (TelaCheiaDoPDF), que saiu.

    COMO CALCULA: cada troca no EstadoDoAutomatico (marcar, opção, receita,
    ordem, onde rodar) pede um "depois" novo. A conta vai para um fio de fundo
    (ui/tarefas.TarefaPreviaDoAutomatico) numa CÓPIA do projeto, pelo mesmo
    caminho do "Rodar" (core/automatico.depois_da_pagina). Enquanto calcula, a
    BolinhaDeCarregamento (a mesma da barra de baixo) gira ao lado do título.
    Trocas rápidas: espera ESPERA_ANTES_DE_CALCULAR_MS depois da última; só
    uma conta por vez; a que está rodando é cancelada e a última troca espera
    a vez; o resultado de um pedido velho (chave diferente da `_querida`, ou
    outra página) é jogado fora. O "antes" não muda com as opções: é calculado uma vez por
    página. Uma página por vez na memória (o antes e o depois da página da
    vez; ao folhear, os da anterior saem).

    NÃO MUDA NADA: nem o projeto, nem o Histórico, nem o disco. Fechar a
    janela sem rodar deixa o livro como estava.

    Arriscado: calcular no projeto aberto em vez da cópia; mostrar o que
    chegar sem conferir a geração (o depois velho cobriria o novo)."""

    def __init__(self, estado: EstadoDoAutomatico, projeto=None, parent=None) -> None:
        super().__init__(parent)
        from ui.widgets.bolinha import BolinhaDeCarregamento

        self.estado = estado
        self.projeto = projeto
        self._indice = 0                      # a página da vez (índice em projeto.paginas)
        self._querida = None                  # a chave do último pedido (_chave): só ela vale
        self._tarefa = None                   # a conta que está rodando
        self._na_espera: tuple | None = None  # a última troca, esperando a vez
        self._feito = None                    # a chave a que o "depois" mostrado responde
        self._antes = None                    # (índice, imagem) do antes da página da vez
        self._depois = None                   # (índice, imagem) do depois
        self._do_livro = None                 # (índice, imagem) da página como está no livro
        self._filtro_depois = ""              # o filtro do depois (o rótulo do "comparar")
        self._fechada = False                 # fechar(): nada mais é pedido
        self.tela_cheia: TelaCheiaDoAntesEDepois | None = None   # aberta pelo "tela cheia"

        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)
        topo = QHBoxLayout()
        topo.addWidget(QLabel("A página, antes e depois"))
        self.bolinha = BolinhaDeCarregamento()
        topo.addWidget(self.bolinha)
        topo.addStretch()
        col.addLayout(topo)
        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        self.rolagem.setAlignment(Qt.AlignCenter)
        self.visor = VistaAntesDepoisComZoom(self.rolagem)
        # D-577, 30/10: o antes é a folha crua (antes dizia "a página como está agora")
        self.visor.setToolTip("À esquerda da linha, a página como veio, sem nada; à direita, como "
                              "ela vai sair com as etapas marcadas. Arraste a linha para comparar.")
        self.rolagem.setWidget(self.visor)
        col.addWidget(self.rolagem, 1)

        barra = QHBoxLayout()
        barra.setSpacing(8)
        self.botao_anterior = QPushButton("<")
        self.botao_anterior.setFixedWidth(40)
        self.botao_anterior.clicked.connect(lambda: self.virar(-1))
        barra.addWidget(self.botao_anterior)
        self.contador = QLabel("")
        self.contador.setAlignment(Qt.AlignCenter)
        barra.addWidget(self.contador, 1)
        self.botao_proxima = QPushButton(">")
        self.botao_proxima.setFixedWidth(40)
        self.botao_proxima.clicked.connect(lambda: self.virar(1))
        barra.addWidget(self.botao_proxima)
        self.botao_tela_cheia = QPushButton("tela cheia")
        self.botao_tela_cheia.clicked.connect(self.abrir_em_tela_cheia)
        barra.addWidget(self.botao_tela_cheia)
        col.addLayout(barra)

        self._relogio = QTimer(self)
        self._relogio.setSingleShot(True)
        self._relogio.setInterval(ESPERA_ANTES_DE_CALCULAR_MS)
        self._relogio.timeout.connect(self._calcular_agora)
        estado.mudou.connect(self.pedir)
        self.ir_para(estado.pagina_atual)

    # --- folhear ------------------------------------------------------------

    def _ativas(self) -> list[int]:
        """As páginas que vão para o PDF (as que se folheiam)."""
        if self.projeto is None:
            return []
        return [p.indice for p in self.projeto.paginas_ativas]

    def ir_para(self, indice: int) -> None:
        """Vai para a página `indice` (a ativa mais perto, se ela não vai para
        o PDF) e pede o antes e o depois dela."""
        ativas = self._ativas()
        if not ativas:
            self.contador.setText("")
            self._acertar_botoes(ativas)
            self.visor.mostrar(None, None)
            return
        depois_dela = [i for i in ativas if i >= int(indice)]
        indice = depois_dela[0] if depois_dela else ativas[-1]
        if indice != self._indice or self._antes is None:
            self._antes = self._depois = None     # uma página por vez na memória
            self._do_livro = None
            self._feito = None
        self._indice = indice
        self.contador.setText(f"página {indice + 1} de {len(self.projeto.paginas)}")
        self._acertar_botoes(ativas)
        self._mostrar()
        self.pedir(agora=True)
        self._acertar_tela_cheia()

    def virar(self, passo: int) -> None:
        ativas = self._ativas()
        if self._indice not in ativas:
            return
        lugar = max(0, min(len(ativas) - 1, ativas.index(self._indice) + passo))
        self.ir_para(ativas[lugar])

    def _acertar_botoes(self, ativas: list[int]) -> None:
        tem = bool(ativas) and self._indice in ativas
        self.botao_anterior.setEnabled(tem and ativas.index(self._indice) > 0)
        self.botao_proxima.setEnabled(tem and ativas.index(self._indice) < len(ativas) - 1)
        self.botao_tela_cheia.setEnabled(tem)

    def abrir_em_tela_cheia(self) -> None:
        """O "tela cheia": o antes e depois da página da vez, grande, com zoom e folhear
        (TelaCheiaDoAntesEDepois; D-577, 30/10). Não bloqueia (open): a conta do antes e
        depois continua chegando e aparece lá. Ao fechar, a página da vez é a da página em
        que a pessoa parou (o folhear de lá é o daqui). Antes abria a folha crua do PDF
        (ui/widgets/folhear_pdf.TelaCheiaDoPDF; print a-08 do teste de 30/10)."""
        if self.projeto is None or self._indice not in self._ativas():
            return
        if self.tela_cheia is None:
            self.tela_cheia = TelaCheiaDoAntesEDepois(self)
        self._acertar_tela_cheia()
        self.tela_cheia.open()
        self.tela_cheia.raise_()
        self.tela_cheia.activateWindow()

    def _acertar_tela_cheia(self) -> None:
        """Manda para o tela cheia aberto o que a página da direita mostra agora: o antes e o
        depois (os mesmos da vista daqui), o "página N de M", os botões e a bolinha."""
        if self.tela_cheia is None:
            return
        from core import etapas
        from core.filtros import NOMES_AMIGAVEIS as NOMES

        antes, depois = self.visor._crus
        do_livro = self._do_livro[1] if self._do_livro and self._do_livro[0] == self._indice else None
        nome_do_livro = nome_depois = ""
        if self.projeto is not None and 0 <= self._indice < len(self.projeto.paginas):
            filtro = etapas.filtro_que_vale(self.projeto, self.projeto.paginas[self._indice])
            nome_do_livro = NOMES.get(filtro, filtro)
        if self._feito is not None and self._filtro_depois:
            nome_depois = NOMES.get(self._filtro_depois, self._filtro_depois)
        self.tela_cheia.acertar(antes, depois, self.visor.aviso, self.contador.text(),
                                self.botao_anterior.isEnabled(), self.botao_proxima.isEnabled(),
                                self.calculando(), self._indice, do_livro, nome_do_livro,
                                nome_depois)

    def _precisa_do_livro(self) -> bool:
        """O "comparar" da tela cheia está ligado e a página como está no livro desta página
        ainda não foi desenhada."""
        return bool(self.tela_cheia is not None and self.tela_cheia.comparando
                    and (self._do_livro is None or self._do_livro[0] != self._indice))

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Setas e Page Up/Down viram a página, como no folhear."""
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.virar(-1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.virar(1)
        else:
            super().keyPressEvent(evento)

    # --- o cálculo -----------------------------------------------------------

    def _chave(self, pedido) -> str:
        """Tudo o que muda o depois, em texto: a página e o pedido inteiro."""
        import json

        return json.dumps([self._indice, pedido.etapas, pedido.opcoes, pedido.paginas,
                           pedido.pular_mexidas, pedido.ordem, pedido.desligar],
                          sort_keys=True, default=str)

    def calculando(self) -> bool:
        """Há conta pedida ou rodando (a bolinha gira)?"""
        return bool(self._relogio.isActive() or self._tarefa is not None or self._na_espera)

    def pedir(self, agora: bool = False) -> None:
        """Uma troca na janela: pede o depois de novo (depois de uma espera
        curta, para trocas seguidas virarem uma só). `agora`: sem a espera
        (abrir a janela, folhear)."""
        if self._fechada or self.projeto is None or self._indice not in self._ativas():
            return
        if agora:
            self._relogio.stop()
            self._calcular_agora()
        else:
            self._relogio.start()
        self._acertar_bolinha()

    def _calcular_agora(self) -> None:
        """Começa a conta do pedido de agora (ou a põe na espera, se outra roda).
        `_querida` passa a ser a chave dele: só o resultado dela é mostrado."""
        from core.automatico import copia_para_a_previa

        if self._fechada or self.projeto is None or self._indice not in self._ativas():
            return
        # a prévia NUNCA pula as páginas mexidas à mão (D-577, 30/10: "na previa ali, ele
        # mostra a mudança em todas as paginas mas só muda as que nós autorizarmos ( no caso
        # as que foram mexidas a mão)"). Quem decide pular é a pergunta da D-004 ao "Rodar",
        # que usa o pedido de fábrica do estado (pular_mexidas=True), não este. Arriscado:
        # voltar a pular aqui (a capa mexida do teste de 30/10 não mudava com o filtro).
        pedido = self.estado.pedido(pular_mexidas=False)
        chave = self._chave(pedido)
        self._querida = chave
        precisa_do_antes = self._antes is None or self._antes[0] != self._indice
        precisa_do_livro = self._precisa_do_livro()
        rodando = self._tarefa
        if chave == self._feito and not precisa_do_antes and not precisa_do_livro:
            # o depois mostrado já é este: nada a calcular (e o que roda ficou velho)
            self._na_espera = None
            if rodando is not None:
                rodando.cancelar()
        elif (rodando is not None and rodando.chave == chave and not rodando.foi_cancelada
              and (rodando.com_o_do_livro or not precisa_do_livro)):
            self._na_espera = None                    # a que roda já é esta: esperar por ela
        else:
            # a cópia é feita AQUI, no fio da janela (o projeto aberto só muda nele)
            pedido_da_vez = (chave, self._indice, copia_para_a_previa(self.projeto), pedido,
                             precisa_do_antes, precisa_do_livro)
            if rodando is not None:
                # só uma conta por vez: a que roda para no próximo ponto de
                # parada, e esta espera a vez (no lugar da que esperava antes)
                rodando.cancelar()
                self._na_espera = pedido_da_vez
            else:
                self._comecar(pedido_da_vez)
        self._acertar_bolinha()

    def _comecar(self, pedido_da_vez: tuple) -> None:
        from ui.tarefas import TarefaPreviaDoAutomatico

        chave, indice, copia, pedido, com_o_antes, com_o_do_livro = pedido_da_vez
        tarefa = TarefaPreviaDoAutomatico(copia, pedido, indice, DPI_DA_PREVIA, com_o_antes, chave,
                                          com_o_do_livro)
        tarefa.pronta.connect(self._chegou)
        tarefa.falhou.connect(self._falhou)
        tarefa.terminou.connect(self._terminou)
        _guardiao().segurar(tarefa)
        self._tarefa = tarefa
        tarefa.start()

    def _chegou(self, chave: str, indice: int, antes, depois, extra=None) -> None:
        """O antes e o depois chegaram. O depois só vale se é do ÚLTIMO pedido
        (`_querida`) e da página da vez: resultado velho nunca cobre o novo.
        O antes (e a página como está no livro, do "comparar") vale para a
        página dele (não muda com as opções). `extra`: {"do_livro", "filtro_depois"}."""
        if indice != self._indice:
            return
        extra = extra or {}
        if antes is not None:
            self._antes = (indice, antes)
        if extra.get("do_livro") is not None:
            self._do_livro = (indice, extra["do_livro"])
        if chave == self._querida:
            self._depois = (indice, _lado_a_lado(depois or []))
            self._feito = chave
            self._filtro_depois = extra.get("filtro_depois", "")
        self._mostrar()

    def _falhou(self, chave: str, _mensagem: str) -> None:
        """A conta deu erro (já está no erros.log): a página da vez mostra o
        antes e uma frase, e a janela continua (regra 3: nenhuma exceção fecha
        a janela)."""
        if chave != self._querida:
            return
        antes = self._antes[1] if self._antes and self._antes[0] == self._indice else None
        self._depois = None
        self.visor.mostrar(antes, None, aviso="Não foi possível mostrar como esta página vai ficar.")
        self._acertar_tela_cheia()

    def _terminou(self, tarefa) -> None:
        """Uma conta terminou (pronta, falha ou cancelada): começa a que estava
        esperando, se ela ainda é a última pedida."""
        if tarefa is self._tarefa:
            self._tarefa = None
        espera, self._na_espera = self._na_espera, None
        if espera is not None and self._tarefa is None:
            if espera[0] == self._querida and espera[1] == self._indice:
                self._comecar(espera)
            elif not self._relogio.isActive():
                self._calcular_agora()
        self._acertar_bolinha()

    def _acertar_bolinha(self) -> None:
        calculando = self.calculando()
        self.bolinha.definir(calculando, "Calculando como a página vai ficar..." if calculando else "")
        self._acertar_tela_cheia()

    def _mostrar(self) -> None:
        antes = self._antes[1] if self._antes and self._antes[0] == self._indice else None
        depois = self._depois[1] if self._depois and self._depois[0] == self._indice else None
        self.visor.mostrar(antes, depois)
        self._acertar_tela_cheia()

    def fechar(self) -> None:
        """Ao fechar a janela: para a conta (o que estiver rodando termina
        sozinho, e nada chega mais aqui) e solta as imagens. Depois disto,
        nenhuma troca no estado pede conta nova (a janela fechada pode
        demorar um instante para sumir, e o "Rodar" troca o estado)."""
        if not self._fechada:            # a janela pode chamar duas vezes (Fechar e depois done)
            self._fechada = True
            try:
                self.estado.mudou.disconnect(self.pedir)
            except (RuntimeError, TypeError):
                pass
        self._relogio.stop()
        self._na_espera = None
        if self._tarefa is not None:
            self._tarefa.cancelar()
            for sinal, alvo in ((self._tarefa.pronta, self._chegou), (self._tarefa.falhou, self._falhou),
                                (self._tarefa.terminou, self._terminou)):
                try:
                    sinal.disconnect(alvo)
                except (RuntimeError, TypeError):
                    pass
            self._tarefa = None
        if self.tela_cheia is not None:
            self.tela_cheia.reject()            # a tela cheia fecha junto com a janela grande
        self._antes = self._depois = self._do_livro = None
        self._acertar_bolinha()


# ---------------------------------------------------------------------------
# a janela grande
# ---------------------------------------------------------------------------

class JanelaDoAutomatico(QDialog):
    """A janela grande do Automático ("O que o automático vai fazer"): as
    etapas à esquerda, as opções da etapa escolhida no meio, a página ao lado
    (antes e depois, D-577; folhear e zoom) e, embaixo, a frase do que vai
    acontecer.

    `controles`: campo do Projeto -> o controle que o muda (a prova de que
    nenhuma opção da tela "O que fazer" se perdeu)."""

    rodar_pedido = Signal()
    desligar_pedido = Signal()
    escolher_pedido = Signal()
    receita_guardar_pedida = Signal()

    def __init__(self, estado: EstadoDoAutomatico, caminho_pdf: str = "", parent=None,
                 projeto=None) -> None:
        """`projeto`: o livro aberto, só para LER (a prévia do antes e depois
        trabalha numa cópia dele, D-577). Sem ele, a página da direita fica
        vazia. `caminho_pdf` ficou só para quem já chamava assim (a página da
        direita lê o PDF do projeto)."""
        super().__init__(parent)
        self.setWindowTitle("Automático")
        self.setObjectName("janelaDoAutomatico")
        self.estado = estado
        self.controles: dict[str, QWidget] = {}
        self.linhas: dict[str, QWidget] = {}
        self._enchendo = False
        if parent is not None:
            area = parent.geometry()
            self.resize(max(900, int(area.width() * 0.92)), max(560, int(area.height() * 0.92)))
        else:
            self.resize(1180, 620)

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)

        # o alto: título, a receita e "Salvar receita..."
        alto = QFrame()
        alto.setObjectName("altoDaJanelaAuto")
        linha = QHBoxLayout(alto)
        linha.setContentsMargins(18, 10, 14, 10)
        titulo = QLabel("O que o automático vai fazer")
        titulo.setObjectName("tituloDaJanelaAuto")
        linha.addWidget(titulo)
        linha.addStretch()
        linha.addWidget(QLabel("Receita:"))
        self.combo_receitas = QComboBox()
        self.combo_receitas.setMinimumWidth(200)
        self.combo_receitas.activated.connect(lambda _i: self._escolheu_receita())
        linha.addWidget(self.combo_receitas)
        self.botao_salvar = QPushButton("Salvar receita...")
        self.botao_salvar.clicked.connect(lambda: self.receita_guardar_pedida.emit())
        linha.addWidget(self.botao_salvar)
        self.botao_apagar = QPushButton("Apagar a receita")
        self.botao_apagar.setObjectName("plano")
        self.botao_apagar.clicked.connect(self._apagar_receita)
        linha.addWidget(self.botao_apagar)
        fora.addWidget(alto)

        meio = QHBoxLayout()
        meio.setContentsMargins(0, 0, 0, 0)
        meio.setSpacing(0)
        # esquerda: as etapas
        esquerda = QWidget()
        esquerda.setObjectName("colunaDasEtapas")
        esquerda.setFixedWidth(290)
        col = QVBoxLayout(esquerda)
        col.setContentsMargins(12, 10, 10, 10)
        col.addWidget(QLabel("Etapas, na ordem · arraste para mudar"))
        self.lista = ListaDeEtapas(estado, compacta=False)
        self.lista.etapa_escolhida.connect(self.mostrar_etapa)
        col.addWidget(self.lista, 1)
        meio.addWidget(esquerda)
        # meio: as opções da etapa escolhida
        self.pilha = QStackedWidget()
        self.pilha.setObjectName("opcoesDaEtapa")
        self.paginas_das_etapas: dict[str, QWidget] = {}
        for etapa in A.ETAPAS:
            pagina = self._pagina_da_etapa(etapa)
            self.paginas_das_etapas[etapa] = pagina
            self.pilha.addWidget(pagina)
        meio.addWidget(self.pilha, 3)     # as opções ganham mais largura que a página ao lado
        # direita: a página da vez, antes e depois (D-577, no lugar da página
        # original da D-486), para folhear e dar zoom. `folhear` é o nome de
        # sempre (a prova P-187 e o _zoom usam: .visor, ._indice)
        direita = QWidget()
        direita.setObjectName("paginaAoLado")
        direita.setMinimumWidth(320)
        cold = QVBoxLayout(direita)
        cold.setContentsMargins(10, 10, 12, 10)
        self.folhear = self.antes_e_depois = PaginaAntesEDepois(estado, projeto)
        cold.addWidget(self.folhear, 1)
        zoom = QHBoxLayout()
        for texto, dica, fator in (("–", "afastar", 0.8), ("+", "aproximar", 1.25)):
            botao = QPushButton(texto)
            botao.setMinimumWidth(44)          # largura fixa de 34 escondia o sinal (o enchimento do estilo)
            botao.setToolTip(dica)
            botao.clicked.connect(lambda _c=False, f=fator: self._zoom(f))
            zoom.addWidget(botao)
        caber = QPushButton("ajustar à tela")
        caber.clicked.connect(lambda: self._zoom(None))
        zoom.addWidget(caber)
        zoom.addStretch()
        cold.addLayout(zoom)
        meio.addWidget(direita, 2)
        fora.addLayout(meio, 1)

        # embaixo: a frase, onde rodar, escolher páginas, fechar, desligar, rodar
        baixo = QFrame()
        baixo.setObjectName("baixoDaJanelaAuto")
        duas = QVBoxLayout(baixo)
        duas.setContentsMargins(14, 8, 14, 10)
        duas.setSpacing(6)
        self.frase = QLabel("")
        self.frase.setObjectName("fraseDaJanelaAuto")
        self.frase.setWordWrap(True)
        duas.addWidget(self.frase)
        lb = QHBoxLayout()
        duas.addLayout(lb)
        lb.addWidget(QLabel("Rodar"))
        self.combo_alcance = _combo_do_alcance(estado)
        lb.addWidget(self.combo_alcance)
        lb.addStretch()
        self.botao_escolher = QPushButton("escolher páginas...")
        self.botao_escolher.clicked.connect(lambda: self.escolher_pedido.emit())
        lb.addWidget(self.botao_escolher)
        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.clicked.connect(self.reject)
        lb.addWidget(self.botao_fechar)
        self.botao_desligar = QPushButton("Desligar as marcadas")
        self.botao_desligar.setToolTip("Tira o automático das etapas marcadas (o Desfazer traz de volta).")
        self.botao_desligar.clicked.connect(lambda: self.desligar_pedido.emit())
        lb.addWidget(self.botao_desligar)
        self.botao_rodar = QPushButton(_texto_do_rodar(estado))
        self.botao_rodar.setObjectName("primario")
        self.botao_rodar.setDefault(True)
        self.botao_rodar.clicked.connect(lambda: self.rodar_pedido.emit())
        lb.addWidget(self.botao_rodar)
        fora.addWidget(baixo)

        estilo.estilizar(self, lambda: (
            f"QDialog#janelaDoAutomatico {{ background: {estilo.cor('tela')}; }}"
            f"QFrame#altoDaJanelaAuto, QFrame#baixoDaJanelaAuto {{ background: {estilo.cor('bar')}; }}"
            f"QLabel#tituloDaJanelaAuto {{ color: {estilo.cor('forte')}; font-size: 16px; font-weight: 600; }}"
            f"QWidget#colunaDasEtapas {{ background: {estilo.cor('bar')}; }}"
            f"QLabel#fraseDaJanelaAuto {{ background: {estilo.cor('sel')}; border-radius: 6px;"
            f" padding: 7px 10px; color: {estilo.cor('forte')}; }}"))
        estado.mudou.connect(self._estado_mudou)
        self.encher_receitas()
        self._mostrar_opcoes()
        self._estado_mudou()
        primeira = next(iter(estado.etapas_marcadas()), estado.ordem[0])
        self.lista.escolher(primeira)
        self.mostrar_etapa(primeira)

    # --- as opções de cada etapa ---------------------------------------------

    def _pagina_da_etapa(self, etapa: str) -> QWidget:
        """As opções de uma etapa, com o nome e o que faz no alto."""
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QFrame.NoFrame)
        dentro = QWidget()
        col = QVBoxLayout(dentro)
        col.setContentsMargins(18, 14, 18, 14)
        col.setSpacing(6)
        nome = QLabel(A.NOMES[etapa])
        nome.setStyleSheet("font-size: 15px; font-weight: 600;")
        col.addWidget(nome)
        col.addWidget(self._fraco(A.EXPLICACOES[etapa][0].upper() + A.EXPLICACOES[etapa][1:] + "."))
        if etapa in A.DO_LIVRO_TODO:
            col.addWidget(self._fraco("Esta etapa vale sempre no livro todo."))
        col.addSpacing(6)
        getattr(self, f"_opcoes_{etapa}")(col)
        col.addStretch()
        rolagem.setWidget(dentro)
        return rolagem

    @staticmethod
    def _fraco(texto: str) -> QLabel:
        rotulo = QLabel(texto)
        rotulo.setWordWrap(True)
        estilo.estilizar(rotulo, lambda: f"color: {estilo.TEXTO_FRACO}; font-size: 12px;")
        return rotulo

    def _combo(self, campo: str, escolhas, col: QVBoxLayout, rotulo: str, dica: str = "") -> QComboBox:
        """Uma lista com o rotulo na frente, numa linha propria (self.linhas[campo]:
        a linha inteira some quando a opcao nao vale, como na tela de antes)."""
        caixa_da_linha = QWidget()
        linha = QHBoxLayout(caixa_da_linha)
        linha.setContentsMargins(0, 0, 0, 0)
        nome_da_linha = QLabel(rotulo)
        nome_da_linha.setWordWrap(True)        # rótulo longo quebra a linha em vez de rolar de lado
        linha.addWidget(nome_da_linha, 1)
        combo = QComboBox()
        for valor, nome in escolhas:
            combo.addItem(nome, valor)
        if dica:
            combo.setToolTip(dica)
        combo.currentIndexChanged.connect(
            lambda _i, c=campo, w=combo: self._mudou(c, w.currentData()))
        linha.addWidget(combo)
        linha.addStretch(1)
        col.addWidget(caixa_da_linha)
        self.controles[campo] = combo
        self.linhas[campo] = caixa_da_linha
        return combo

    def _caixa(self, campo: str, texto: str, explicacao: str, col: QVBoxLayout) -> QCheckBox:
        caixa = QCheckBox(texto)
        estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(14)
                         + f" QCheckBox:disabled {{ color: {estilo.cor('desligado')}; }}")
        caixa.toggled.connect(lambda v, c=campo: self._mudou(c, bool(v)))
        col.addWidget(caixa)
        if explicacao:
            frase = self._fraco(explicacao)
            frase.setContentsMargins(26, 0, 0, 4)
            col.addWidget(frase)
        self.controles[campo] = caixa
        return caixa

    def _opcoes_dividir(self, col) -> None:
        self._combo("dividir_como", [(j, _nome_do_jeito(j)) for j in dividir_scantailor.JEITOS], col,
                    "Jeito de dividir:",
                    "O do Editor procura a lombada no meio das folhas deitadas; o do ScanTailor "
                    "divide toda folha mais larga que alta, na dobra que ele acha.")
        col.addWidget(self._fraco("Livro novo não divide sozinho: só quando esta etapa roda (G2). "
                                  "Dá para trocar numa folha só, com a ferramenta Dividir a folha."))

    def _opcoes_endireitar(self, col) -> None:
        self._combo("endireitar_como", [(j, _nome_da_conta(j)) for j in endireitar_scantailor.JEITOS],
                    col, "Conta do endireitar:",
                    "Como a inclinação é medida. Quando as duas contas discordam mais de 0,3 grau, "
                    "a página vai para \"Para revisar\".")
        col.addSpacing(8)
        self._combo("retangulo_do_corte", list(NOMES_DO_RETANGULO), col,
                    "Quando o ângulo muda depois do corte à mão, o corte:",
                    "D-094: a mesma escolha existe nas Configurações (para todos os livros) e na "
                    "ferramenta Endireitar (só uma página).")

    def _opcoes_cortar(self, col) -> None:
        self._caixa("cortar_sobra", "Cortar a beirada da folha vizinha",
                    "o corte da sobra do ScanTailor, nas folhas que não forem divididas", col)
        self._caixa("cortar_pelo_conteudo", "Cortar seguindo o conteúdo (como o ScanTailor)",
                    "o corte abraça o que está impresso, e todas as páginas ficam do tamanho da maior",
                    col)
        self._caixa("borda_preta", "Achar a página dentro da borda preta do scanner",
                    "o programa sugere o corte; dá para mudar o corte numa página só", col)
        self._combo("borda_preta_ate", [(j, borda_preta.NOMES[j]) for j in borda_preta.JEITOS], col,
                    "Cortar:", "Até a moldura: o corte vai até o que está impresso. Só o preto: "
                    "tira só a faixa preta do scanner.")
        # Etapa 9b-2 (D-559: a faixa preta da tampa do scanner some em todo o
        # livro, "e o Kaique escolhe por livro cortar ou pintar de branco"): a
        # MESMA escolha do livro da D-092 ("O Kaique escolhe por livro") vale
        # para a borda preta e para a tampa; por isso fica à vista também com
        # a borda preta desmarcada (_mostrar_opcoes).
        self._combo("borda_preta_fazer", [(f, borda_preta.NOMES_DO_FAZER[f]) for f in borda_preta.FAZERES],
                    col, "O que fica fora da página:",
                    "Cortar fora: a página fica menor. Pintar de branco: a página fica do tamanho "
                    "de sempre e o que está fora vira branco. Vale para a borda preta e para a "
                    "faixa preta da tampa do scanner.")

    def _opcoes_limpar(self, col) -> None:
        from ui.widgets.escolhas_do_misto import EscolhasDoMisto

        col.addWidget(QLabel("Jeito de limpar"))
        self.grupo_filtros = QButtonGroup(self)
        self.radios_de_filtro: dict[str, QRadioButton] = {}
        self.explicacoes_dos_filtros: dict[str, QLabel] = {}   # somem junto com o radio (Tirar o fundo)
        grade = QGridLayout()
        for n, (chave, nome, explicacao) in enumerate(FILTROS_DA_LIMPEZA):
            radio = QRadioButton(nome)
            radio.setProperty("filtro", chave)
            radio.toggled.connect(lambda v, k=chave: v and self._mudou("filtro_padrao", k))
            self.grupo_filtros.addButton(radio)
            self.radios_de_filtro[chave] = radio
            grade.addWidget(radio, n, 0)
            fraco = self._fraco(explicacao)
            self.explicacoes_dos_filtros[chave] = fraco
            grade.addWidget(fraco, n, 1)
        col.addLayout(grade)
        self.controles["filtro_padrao"] = self.radios_de_filtro[PRETO_E_BRANCO]
        self.escolhas_misto = EscolhasDoMisto()
        self.escolhas_misto.so_as_letras_mudou.connect(lambda v: self._mudou("misto_so_as_letras", bool(v)))
        self.escolhas_misto.fora_do_texto_escolhido.connect(lambda v: self._mudou("misto_fora_do_texto", v))
        self.escolhas_misto.papel_escolhido.connect(lambda v: self._mudou("misto_papel_da_gravura", v))
        self.escolhas_misto.letras_escolhidas.connect(lambda v: self._mudou("misto_letras_na_moldura", v))
        col.addWidget(self.escolhas_misto)
        for campo in misto.CAMPOS_DO_MISTO:
            self.controles[campo] = self.escolhas_misto
        self.cx_forca_sozinha = self._caixa(
            "reforcar_texto_falhado", "Escurecer sozinho a força do preto quando o texto sair falhado",
            "com \"Só as letras\": escurece só na página falhada e avisa, com \"Desfazer\"", col)
        self.cx_decoracao_pb = self._caixa(
            "pb_decoracao_em_preto_e_branco",
            "No Preto e branco, molduras e iluminuras também em preto e branco",
            "desmarcada, a moldura dourada e a iluminura ficam com a cor do original", col)
        self.combo_pontinhos = self._combo(
            "limpar_pontinhos", [(c, pontinhos.NOMES_NA_TELA[c]) for c in pontinhos.ESCOLHAS], col,
            pontinhos.ROTULO_NA_TELA, pontinhos.EXPLICACAO_NA_TELA)

    def _opcoes_gravuras(self, col) -> None:
        """O grupo "Gravuras e fotos" (item 1.2, D-212 e D-213), como era na tela
        "O que fazer": "Achar gravuras e fotos" (desmarcada = não procurar: o
        desligar da regra 8), "Este livro tem fotos" e, atrás de "Mais opções",
        a sensibilidade, as imagens claras e o igualar a luz."""
        self.cx_achar_gravuras = QCheckBox("Achar gravuras e fotos")
        estilo.estilizar(self.cx_achar_gravuras, lambda: estilo_da_caixinha_com_quadrado(14))
        self.cx_achar_gravuras.toggled.connect(lambda _v: self._forma_mudou())
        col.addWidget(self.cx_achar_gravuras)
        col.addWidget(self._fraco("separa desenho, foto e moldura do texto, para cada um ser "
                                  "tratado do seu jeito"))
        self.painel_opcoes_gravura = QWidget()
        dentro = QVBoxLayout(self.painel_opcoes_gravura)
        dentro.setContentsMargins(22, 4, 0, 0)
        self.cx_tem_fotos = QCheckBox("Este livro tem fotos")
        estilo.estilizar(self.cx_tem_fotos, lambda: estilo_da_caixinha_com_quadrado(14))
        self.cx_tem_fotos.toggled.connect(lambda _v: self._forma_mudou())
        dentro.addWidget(self.cx_tem_fotos)
        dentro.addWidget(self._fraco("procura em retângulo, que pega a foto inteira; desmarcada, "
                                     "segue o contorno do desenho"))
        self.controles["gravura_forma"] = self.cx_tem_fotos
        self.botao_mais_opcoes = QPushButton("Mais opções")
        self.botao_mais_opcoes.setObjectName("plano")
        self.botao_mais_opcoes.setCheckable(True)
        self.botao_mais_opcoes.toggled.connect(self._abrir_mais_opcoes)
        dentro.addWidget(self.botao_mais_opcoes, 0, Qt.AlignLeft)
        self.painel_mais_opcoes = QWidget()
        mais = QVBoxLayout(self.painel_mais_opcoes)
        mais.setContentsMargins(0, 0, 0, 0)
        dentro.addWidget(self.painel_mais_opcoes)
        self.painel_mais_opcoes.setVisible(False)
        col.addWidget(self.painel_opcoes_gravura)
        col = mais
        linha = QHBoxLayout()
        linha.addWidget(QLabel("Sensibilidade"))
        self.deslizante = QSlider(Qt.Horizontal)
        self.deslizante.setRange(0, 100)
        self.deslizante.setSingleStep(10)
        self.deslizante.setPageStep(10)
        self.deslizante.valueChanged.connect(lambda v: self._mudou("gravura_sensibilidade", int(v)))
        linha.addWidget(self.deslizante, 1)
        self.valor_sensibilidade = QLabel("")
        linha.addWidget(self.valor_sensibilidade)
        col.addLayout(linha)
        col.addWidget(self._fraco("só com fotos: no máximo, o retângulo pega a foto inteira"))
        self.controles["gravura_sensibilidade"] = self.deslizante
        self._caixa("gravura_mais_sensivel", "Procurar também imagens claras",
                    "acha desenho e foto bem apagados; pode pegar mancha junto", col)
        self._caixa("gravura_normalizar", "Igualar a luz da página antes",
                    "acerta a página mais escura de um lado antes de procurar", col)
        col.addWidget(self._fraco("Estas opções valem no livro todo, nas páginas com "
                                  "\"Limpar a folha\"."))

    def _opcoes_margens(self, col) -> None:
        grade = QGridLayout()
        self.margens_mm: dict[str, QDoubleSpinBox] = {}
        for i, (chave, rotulo) in enumerate((("esquerda", "esquerda"), ("cima", "em cima"),
                                             ("direita", "direita"), ("baixo", "embaixo"))):
            caixa = QDoubleSpinBox()
            caixa.setRange(0.0, 100.0)
            caixa.setDecimals(1)
            caixa.setSuffix(" mm")
            caixa.valueChanged.connect(lambda _v: self._margens_mudaram())
            self.margens_mm[chave] = caixa
            grade.addWidget(QLabel(f"margem {rotulo}:"), i // 2, (i % 2) * 2)
            grade.addWidget(caixa, i // 2, (i % 2) * 2 + 1)
        col.addLayout(grade)
        self.controles["margens_mm"] = self.margens_mm["esquerda"]
        self.combo_vertical = QComboBox()
        for codigo in margens_scantailor.VERTICAIS:
            self.combo_vertical.addItem(margens_scantailor.NOMES_VERTICAIS[codigo], codigo)
        self.combo_horizontal = QComboBox()
        for codigo in margens_scantailor.HORIZONTAIS:
            self.combo_horizontal.addItem(margens_scantailor.NOMES_HORIZONTAIS[codigo], codigo)
        for combo in (self.combo_vertical, self.combo_horizontal):
            combo.currentIndexChanged.connect(lambda _i: self._alinhamento_mudou())
        linha = QHBoxLayout()
        linha.addWidget(QLabel("página menor, de cima a baixo:"))
        linha.addWidget(self.combo_vertical)
        linha.addWidget(QLabel("de um lado ao outro:"))
        linha.addWidget(self.combo_horizontal)
        linha.addStretch()
        col.addLayout(linha)
        self.controles["margens_alinhamento"] = self.combo_vertical

    def _opcoes_cadernos(self, col) -> None:
        self._combo("paginas_por_caderno", [(n, str(n)) for n in PAGINAS_POR_CADERNO], col,
                    "páginas por caderno:")
        col.addWidget(self._fraco("Monta os cadernos no tamanho do scan (sem A4, sem margem). "
                                  "A montagem em A4 fica em \"Ficou pronto!\"."))

    def _forma_mudou(self) -> None:
        """"Achar gravuras e fotos" e "Este livro tem fotos" viram a forma do
        contorno do livro (Projeto.gravura_forma)."""
        if not self.cx_achar_gravuras.isChecked():
            forma = "desligada"
        else:
            forma = "retangular" if self.cx_tem_fotos.isChecked() else "livre"
        self._mudou("gravura_forma", forma)

    def _abrir_mais_opcoes(self, aberto: bool) -> None:
        self.painel_mais_opcoes.setVisible(aberto)
        self.botao_mais_opcoes.setText("Menos opções" if aberto else "Mais opções")

    def _margens_mudaram(self) -> None:
        self._mudou("margens_mm", [float(self.margens_mm[c].value())
                                   for c in ("esquerda", "cima", "direita", "baixo")])

    def _alinhamento_mudou(self) -> None:
        self._mudou("margens_alinhamento", list(margens_scantailor.alinhamento_valido(
            (self.combo_vertical.currentData(), self.combo_horizontal.currentData()))))

    # --- ida e volta com o estado ----------------------------------------------

    def _mudou(self, campo: str, valor) -> None:
        if self._enchendo:
            return
        self.estado.definir_opcao(campo, valor)

    def _mostrar_opcoes(self) -> None:
        """Acerta os controles pelas opções do estado (sem avisar ninguém)."""
        o = self.estado.opcoes
        self._enchendo = True
        try:
            for campo in ("dividir_como", "endireitar_como", "retangulo_do_corte", "borda_preta_ate",
                          "borda_preta_fazer", "limpar_pontinhos", "paginas_por_caderno"):
                combo = self.controles.get(campo)
                if isinstance(combo, QComboBox):
                    indice = combo.findData(o.get(campo))
                    combo.setCurrentIndex(max(0, indice))
            for campo in ("cortar_sobra", "cortar_pelo_conteudo", "borda_preta", "reforcar_texto_falhado",
                          "pb_decoracao_em_preto_e_branco", "gravura_mais_sensivel", "gravura_normalizar"):
                caixa = self.controles.get(campo)
                if isinstance(caixa, QCheckBox):
                    caixa.setChecked(bool(o.get(campo, False)))
            filtro = o.get("filtro_padrao", ORIGINAL)
            if filtro in self.radios_de_filtro:
                self.radios_de_filtro[filtro].setChecked(True)
            com_fundo = self.estado.tem_camadas or filtro == TIRAR_FUNDO
            self.radios_de_filtro[TIRAR_FUNDO].setVisible(com_fundo)
            self.explicacoes_dos_filtros[TIRAR_FUNDO].setVisible(com_fundo)
            self.escolhas_misto.mostrar(
                bool(o.get("misto_so_as_letras", False)),
                o.get("misto_fora_do_texto", misto.FORA_DO_TEXTO_PADRAO),
                o.get("misto_papel_da_gravura", misto.PAPEL_DA_GRAVURA_PADRAO),
                o.get("misto_letras_na_moldura", misto.LETRAS_NA_MOLDURA_PADRAO))
            no_pb = filtro == PRETO_E_BRANCO
            so_letras = bool(o.get("misto_so_as_letras", False))
            self.escolhas_misto.setVisible(no_pb)
            self.cx_forca_sozinha.setVisible(no_pb)
            # etapa 9b-2 (lista única 23/10, 5.3, Samuel: "Essa opção não dá
            # para desativar" - ela ficava marcada e CINZA sem "Só as letras"):
            # a caixinha fica sempre acesa, para ligar e desligar quando quiser
            # (regra 8 do plano); a frase embaixo diz que ela age com "Só as letras"
            self.cx_forca_sozinha.setEnabled(True)
            # "Limpar a sujeira" so aparece com o Preto e branco (escondida, a
            # escolha fica guardada: como a tela "O que fazer" fazia)
            self.linhas["limpar_pontinhos"].setVisible(no_pb)
            # D-168: a caixinha das molduras fica cinza com "Só as letras" e volta como estava
            self.cx_decoracao_pb.setEnabled(not (so_letras and no_pb))
            forma = o.get("gravura_forma", "livre")
            self.cx_achar_gravuras.setChecked(forma != "desligada")
            self.painel_opcoes_gravura.setVisible(forma != "desligada")
            if forma != "desligada":          # desligada, "tem fotos" fica como estava
                self.cx_tem_fotos.setChecked(forma == "retangular")
            # "Mais opções" abre sozinho quando alguma avançada não está no padrão
            avancada = (int(o.get("gravura_sensibilidade", 100) or 100) != 100
                        or bool(o.get("gravura_mais_sensivel")) or not o.get("gravura_normalizar", True))
            if avancada and not self.botao_mais_opcoes.isChecked():
                self.botao_mais_opcoes.setChecked(True)
            try:
                sens = max(0, min(100, int(o.get("gravura_sensibilidade", 100))))
            except (TypeError, ValueError):
                sens = 100
            self.deslizante.setValue(sens)
            self.deslizante.setEnabled(forma == "retangular")
            self.valor_sensibilidade.setText(str(sens))
            mm = margens_scantailor.Margens.de(o.get("margens_mm")).como_lista()
            for chave, valor in zip(("esquerda", "cima", "direita", "baixo"), mm):
                self.margens_mm[chave].setValue(valor)
            vertical, horizontal = margens_scantailor.alinhamento_valido(o.get("margens_alinhamento"))
            self.combo_vertical.setCurrentIndex(max(0, self.combo_vertical.findData(vertical)))
            self.combo_horizontal.setCurrentIndex(max(0, self.combo_horizontal.findData(horizontal)))
            # a lista da borda preta so aparece com a caixinha marcada (D-101);
            # o "O que fica fora da pagina" fica sempre: vale tambem para a
            # tampa do scanner, que some em todo livro (D-559, etapa 9b-2)
            self.linhas["borda_preta_ate"].setVisible(bool(o.get("borda_preta")))
            self.linhas["borda_preta_fazer"].setVisible(True)
        finally:
            self._enchendo = False

    def _estado_mudou(self) -> None:
        self._mostrar_opcoes()
        self.frase.setText(self.estado.frase())
        self.botao_rodar.setText(_texto_do_rodar(self.estado))
        self.botao_rodar.setEnabled(bool(self.estado.marcadas))
        self.botao_desligar.setEnabled(bool(self.estado.marcadas))
        indice = self.combo_receitas.findData(self.estado.receita)
        self.combo_receitas.blockSignals(True)
        self.combo_receitas.setCurrentIndex(max(0, indice))
        self.combo_receitas.blockSignals(False)
        self.botao_apagar.setEnabled(bool(self.estado.receita)
                                     and self.estado.receita != perfis.NOME_DE_FABRICA)

    def mostrar_etapa(self, etapa: str) -> None:
        """Mostra no meio as opções da etapa (o "ajustar ›")."""
        if etapa in self.paginas_das_etapas:
            self.pilha.setCurrentWidget(self.paginas_das_etapas[etapa])
            self.lista.escolher(etapa)

    def encher_receitas(self) -> None:
        self.combo_receitas.blockSignals(True)
        self.combo_receitas.clear()
        self.combo_receitas.addItem("(nenhuma)", "")
        for nome in perfis.nomes():
            self.combo_receitas.addItem(nome, nome)
        self.combo_receitas.setCurrentIndex(max(0, self.combo_receitas.findData(self.estado.receita)))
        self.combo_receitas.blockSignals(False)

    def _escolheu_receita(self) -> None:
        nome = self.combo_receitas.currentData()
        if nome:
            self.estado.por_receita(nome)

    def _apagar_receita(self) -> None:
        nome = self.estado.receita
        if not nome or nome == perfis.NOME_DE_FABRICA:
            return
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Apagar a receita")
        caixa.setText(f"Apagar a receita \"{nome}\"? Os livros que já rodaram com ela não mudam.")
        sim = caixa.addButton("apagar", QMessageBox.DestructiveRole)
        caixa.addButton("cancelar", QMessageBox.RejectRole)
        caixa.exec()
        if caixa.clickedButton() is sim and perfis.apagar(nome):
            self.estado.receita = ""
            self.encher_receitas()
            self.estado.mudou.emit()

    def _zoom(self, fator: float | None) -> None:
        """−, + e "ajustar à tela" da página da direita (D-002: "folhear e dar zoom")."""
        visor = self.folhear.visor
        if fator is None:
            visor.ajustar_a_tela()
        else:
            visor.definir_zoom(max(0.1, min(8.0, getattr(visor, "zoom", 1.0) * fator)))

    def done(self, resultado: int) -> None:  # noqa: D401 - nome do Qt
        """Ao fechar, para a conta do antes e depois e solta as imagens
        (PaginaAntesEDepois.fechar). Nada muda no livro (D-577: só mostra)."""
        self.folhear.fechar()
        super().done(resultado)


# ---------------------------------------------------------------------------
# a caixa da receita (D-071: mais clara sobre o que vai dentro)
# ---------------------------------------------------------------------------

class CaixaDaReceita(QDialog):
    """"Guardar como receita": o nome, e O QUE VAI DENTRO, etapa por etapa,
    escrito por extenso (com as opções dela), cada uma com a caixinha de
    levar ou não. Embaixo, "usar em todo livro novo". Pedido do Samuel
    (`fr-219`, 22/10): "Mas ainda pode melhorar a caixa de como escolhemos o
    que vai dentro da receita." (antes: um campo de nome e "guardar", que
    levava todas as caixinhas da tela sem dizer quais)."""

    def __init__(self, estado: EstadoDoAutomatico, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Guardar como receita")
        self.estado = estado
        col = QVBoxLayout(self)
        col.addWidget(QLabel("Nome da receita:"))
        self.nome = QLineEdit(estado.receita if estado.receita != perfis.NOME_DE_FABRICA else "")
        self.nome.setPlaceholderText("ex.: Livro amarelado")
        col.addWidget(self.nome)
        col.addSpacing(6)
        col.addWidget(QLabel("O que vai dentro desta receita (desmarque o que não quer levar):"))
        self.caixas: dict[str, QCheckBox] = {}
        for etapa in estado.ordem:
            caixa = QCheckBox(f"{A.NOMES[etapa]} — {texto_das_opcoes(etapa, estado.opcoes)}")
            estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(14))
            caixa.setChecked(etapa in estado.marcadas)
            self.caixas[etapa] = caixa
            col.addWidget(caixa)
        col.addWidget(QLabel("As etapas desmarcadas ficam desligadas quando a receita for posta."))
        self.cx_livro_novo = QCheckBox("Usar esta receita no aviso de todo livro novo")
        estilo.estilizar(self.cx_livro_novo, lambda: estilo_da_caixinha_com_quadrado(14))
        col.addWidget(self.cx_livro_novo)
        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("cancelar")
        cancelar.clicked.connect(self.reject)
        self.botao_guardar = QPushButton("guardar")
        self.botao_guardar.setObjectName("primario")
        self.botao_guardar.clicked.connect(self.guardar)
        botoes.addWidget(cancelar)
        botoes.addWidget(self.botao_guardar)
        col.addLayout(botoes)
        self.guardada = ""

    def etapas_escolhidas(self) -> list[str]:
        return [e for e in self.estado.ordem if self.caixas[e].isChecked()]

    def guardar(self) -> None:
        """Guarda e fecha (o nome usado fica em self.guardada)."""
        self.guardada = perfis.guardar_receita(self.nome.text(), self.estado.opcoes,
                                               self.etapas_escolhidas())
        if self.cx_livro_novo.isChecked():
            perfis.definir_do_livro_novo(self.guardada)
        self.estado.receita = self.guardada
        self.accept()
