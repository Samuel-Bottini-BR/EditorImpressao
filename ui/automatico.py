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
        return A.Pedido(etapas=self.etapas_marcadas(), opcoes=copy.deepcopy(self.opcoes),
                        paginas=self.paginas(), pular_mexidas=pular_mexidas,
                        receita=self.receita, desligar=desligar, ordem=list(self.ordem))

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
# a janela grande
# ---------------------------------------------------------------------------

class JanelaDoAutomatico(QDialog):
    """A janela grande do Automático ("O que o automático vai fazer"): as
    etapas à esquerda, as opções da etapa escolhida no meio, a página ao lado
    (folhear e zoom) e, embaixo, a frase do que vai acontecer.

    `controles`: campo do Projeto -> o controle que o muda (a prova de que
    nenhuma opção da tela "O que fazer" se perdeu)."""

    rodar_pedido = Signal()
    desligar_pedido = Signal()
    escolher_pedido = Signal()
    receita_guardar_pedida = Signal()

    def __init__(self, estado: EstadoDoAutomatico, caminho_pdf: str = "", parent=None) -> None:
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
        # direita: a página ao lado, para folhear e dar zoom
        from ui.widgets.folhear_pdf import FolhearPDF

        direita = QWidget()
        direita.setObjectName("paginaAoLado")
        direita.setMinimumWidth(320)
        cold = QVBoxLayout(direita)
        cold.setContentsMargins(10, 10, 12, 10)
        cold.addWidget(QLabel("O livro, como está agora"))
        self.folhear = FolhearPDF()
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
        if caminho_pdf:
            self.folhear.abrir(caminho_pdf, max(0, estado.pagina_atual))
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
        self._combo("borda_preta_fazer", [(f, borda_preta.NOMES_DO_FAZER[f]) for f in borda_preta.FAZERES],
                    col, "O que fica fora da página:",
                    "Cortar fora: a página fica menor. Pintar de branco: a página fica do tamanho "
                    "de sempre e o que está fora vira branco.")

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
            self.cx_forca_sozinha.setEnabled(so_letras)
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
            # a lista da borda preta so aparece com a caixinha marcada (D-101)
            self.linhas["borda_preta_ate"].setVisible(bool(o.get("borda_preta")))
            self.linhas["borda_preta_fazer"].setVisible(bool(o.get("borda_preta")))
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
        visor = self.folhear.visor
        if fator is None:
            visor.ajustar_a_tela()
        else:
            visor.definir_zoom(max(0.1, min(8.0, getattr(visor, "zoom", 1.0) * fator)))

    def done(self, resultado: int) -> None:  # noqa: D401 - nome do Qt
        """Ao fechar, solta o PDF do folhear (ver FolhearPDF.fechar)."""
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
