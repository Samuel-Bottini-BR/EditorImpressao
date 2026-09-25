"""Os quatro painéis da direita, na coluna de 172 px do desenho aprovado.

Eles recebem o que eram linhas de botões atravessando a tela. Cada linha dessas
custava altura da página - que é o que a pessoa precisa olhar -, e largura
sobra.

De cima para baixo, e a ordem importa:

  Para revisar        o que exige atenção vem primeiro, e AGRUPADO POR TIPO.
                      Uma lista solta de "página 3, página 17, página 40" não
                      diz o que há de errado; "ângulo suspeito: 2" diz.
  Marcar como         gravura · letra · papel, um embaixo do outro
  Filtro da página    qual filtro, o deslizante dele, e "só neste pedaço"
  Histórico           as ações da sessão; clicar volta o trabalho até ali

Cada um recolhe com um clique no título. Recolhido, sobra só a barra de título -
e quem não usa um painel recupera a altura dele para os outros.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.estilo import TEXTO_FRACO

LARGURA = 172          # do desenho aprovado
LARANJA, LARANJA_FUNDO = "#ef9f27", "#faeeda"
FUNDO = "#f7f5f2"
BORDA = "#e6e4e0"
AZUL, AZUL_FUNDO = "#378add", "#e6f1fb"

BOTAO_DO_PAINEL = """
QPushButton {{
    border: 1px solid {borda}; background: {fundo}; color: {cor};
    border-radius: 4px; padding: 3px 8px; font-size: 12px; text-align: left;
}}
QPushButton:hover {{ border-color: {azul}; }}
"""


class _BotaoDoPainel(QPushButton):
    """Um botão da coluna de 172px que corta o próprio texto, em vez de
    empurrar a coluna inteira para o dobro da largura do desenho.

    Achado ao vivo: o `QPushButton` não encolhe abaixo do que precisa para
    mostrar o texto inteiro sem quebrar. Um item de histórico como "Filtro da
    página 12: Preto e branco para Melhorar" pedia ~350px, e como os quatro
    painéis dividem a MESMA coluna, isso alargava a coluna toda - inclusive
    "Marcar como" e "Filtro da página" - bem além dos 172px, cortando o
    resultado pela metade sem aviso nenhum.
    """

    def __init__(self, texto: str, parent=None) -> None:
        super().__init__(texto, parent)
        self._texto_completo = ""
        self.setText(texto)

    def setText(self, texto: str) -> None:  # noqa: N802
        # Alguns paineis trocam o texto depois (o contador de "Para revisar",
        # por exemplo) - guardar aqui de novo garante que o elidir usa sempre
        # o texto atual, nao o do momento em que o botao foi criado.
        self._texto_completo = texto
        self.setToolTip(texto)
        self._reelidir()

    def minimumSizeHint(self) -> QSize:
        # Nao depender do tamanho do texto: e exatamente essa dependencia que
        # forcava a coluna a crescer para caber o texto inteiro sem cortar.
        cheio = super().minimumSizeHint()
        return QSize(0, cheio.height())

    def resizeEvent(self, evento) -> None:  # noqa: N802
        """Reelide o texto quando o botão muda de tamanho."""
        super().resizeEvent(evento)
        self._reelidir()

    def _reelidir(self) -> None:
        """Corta o texto completo com reticencias para caber na largura atual."""
        disponivel = self.width() - 20  # o padding de "3px 8px" + a borda
        elidido = self.fontMetrics().elidedText(
            self._texto_completo, Qt.ElideRight, max(0, disponivel))
        QPushButton.setText(self, elidido)


class Painel(QFrame):
    """Um painel com título clicável e um corpo que recolhe."""

    recolheu = Signal(bool)

    def __init__(self, titulo: str, parent=None) -> None:
        """Monta o cabeçalho clicável (que recolhe/expande) e o corpo vazio -
        cada subclasse preenche o corpo em `atualizar` ou `_montar`."""
        super().__init__(parent)
        # Trava a largura nos 172px do desenho de verdade: sem isto, um botao
        # ou rotulo comprido (achado ao vivo: um item de historico como
        # "Filtro da pagina 12: Preto e branco para Melhorar") empurra a
        # coluna inteira para o dobro da largura, cortando os OUTROS paineis
        # pela metade sem aviso nenhum.
        self.setMaximumWidth(LARGURA)
        self.setStyleSheet(
            f"QFrame {{ background: {FUNDO}; border: none; "
            f"border-bottom: 1px solid {BORDA}; }}")

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(0)

        self.cabecalho = _BotaoDoPainel(titulo)
        self.cabecalho.setCursor(Qt.PointingHandCursor)
        self.cabecalho.setStyleSheet(
            "QPushButton { border: none; background: transparent; "
            "text-align: left; padding: 7px 12px; font-size: 13px; }")
        self.cabecalho.clicked.connect(self.alternar)
        camadas.addWidget(self.cabecalho)

        self.corpo = QWidget()
        self.corpo.setStyleSheet("background: transparent; border: none;")
        self.dentro = QVBoxLayout(self.corpo)
        self.dentro.setContentsMargins(12, 0, 12, 10)
        self.dentro.setSpacing(5)
        camadas.addWidget(self.corpo)

        self._titulo = titulo
        self.recolhido = False

    def alternar(self) -> None:
        """Clique no cabeçalho: recolhe se estava aberto, abre se estava recolhido."""
        self.definir_recolhido(not self.recolhido)

    def definir_recolhido(self, recolhido: bool) -> None:
        """Mostra/esconde o corpo do painel (só a barra de título fica, se recolhido)."""
        self.recolhido = bool(recolhido)
        self.corpo.setVisible(not self.recolhido)
        self.recolheu.emit(self.recolhido)

    def limpar(self) -> None:
        """Remove todo o conteudo do corpo, antes de `atualizar`/`_montar` repovoar."""
        while self.dentro.count():
            item = self.dentro.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _texto(self, texto: str, cor: str = "", tamanho: int = 12) -> QLabel:
        """Rotulo simples de texto fraco, ja adicionado ao corpo do painel."""
        rotulo = QLabel(texto)
        rotulo.setWordWrap(True)
        rotulo.setStyleSheet(
            f"color: {cor or TEXTO_FRACO}; font-size: {tamanho}px; "
            "background: transparent; border: none;")
        self.dentro.addWidget(rotulo)
        return rotulo

    def _botao(self, texto: str, acao, escolhido: bool = False) -> QPushButton:
        """Botão de acao do painel, ja adicionado ao corpo e ligado a `acao`.
        escolhido=True destaca em azul (usado para o item atualmente selecionado)."""
        botao = _BotaoDoPainel(texto)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(BOTAO_DO_PAINEL.format(
            borda=AZUL if escolhido else "#d3d1c7",
            fundo=AZUL_FUNDO if escolhido else "#ffffff",
            cor="#185fa5" if escolhido else "#5f5e5a",
            azul=AZUL))
        botao.clicked.connect(acao)
        self.dentro.addWidget(botao)
        return botao


class PainelParaRevisar(Painel):
    """O que exige atenção, agrupado POR TIPO de alerta.

    A especificação original pedia este painel e ele nunca tinha sido feito. E
    pedia agrupado: uma lista de "página 3, página 17, página 40" não diz o que
    há de errado com elas.
    """

    ir_para = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__("Para revisar", parent)
        self.cabecalho.setStyleSheet(
            "QPushButton { border: none; text-align: left; padding: 7px 12px; "
            f"font-size: 13px; background: {LARANJA_FUNDO}; "
            f"border-bottom: 1px solid {LARANJA}; }}")

    def atualizar(self, projeto) -> None:
        """Reconstroi a lista agrupada por tipo de alerta, dos maiores grupos
        para os menores, e o contador no cabeçalho."""
        self.limpar()
        if projeto is None:
            return

        from core import analise

        por_tipo: dict[str, list[int]] = {}
        for pagina in projeto.paginas:
            if pagina.revisada or pagina.apagada:
                continue
            for alerta in pagina.alertas:
                por_tipo.setdefault(alerta, []).append(pagina.indice)

        total = sum(len(p) for p in por_tipo.values())
        self.cabecalho.setText(f"Para revisar          {total}" if total
                               else "Para revisar")

        if not por_tipo:
            self._texto("nada pendente")
            return

        for alerta, indices in sorted(por_tipo.items(),
                                      key=lambda p: -len(p[1])):
            # descrever devolve um Alerta, e nao um texto: sem o .titulo o
            # painel mostrava "Alerta(codigo='cor', titulo=..." na cara do
            # usuario.
            nome = getattr(analise.descrever(alerta), "titulo", None) or alerta
            botao = self._botao(f"{nome}   ({len(indices)})",
                                lambda _c=False, i=indices[0]: self.ir_para.emit(i))
            botao.setToolTip(
                "páginas: " + ", ".join(str(i + 1) for i in indices[:20]))

        self._texto("clicar leva à primeira", tamanho=11)


class PainelMarcarComo(Painel):
    """Gravura · letra · papel, um embaixo do outro - e não em linha."""

    escolheu = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("Marcar como", parent)
        self.tipo = ""
        self._montar()

    def _montar(self) -> None:
        """(Re)desenha os três botões de tipo, destacando o escolhido."""
        from core.selecao import GRAVURA, LETRA, PAPEL

        self.limpar()
        self.botoes = {}
        for tipo, texto in ((GRAVURA, "gravura ou foto"),
                            (LETRA, "letra e traço"),
                            (PAPEL, "papel")):
            self.botoes[tipo] = self._botao(
                texto, lambda _c=False, t=tipo: self.definir_tipo(t),
                escolhido=(tipo == (self.tipo or GRAVURA)))
        self.tipo = self.tipo or GRAVURA

    def definir_tipo(self, tipo: str) -> None:
        """Troca o tipo escolhido (gravura/letra/papel) e emite `escolheu`."""
        if tipo == self.tipo:
            return
        self.tipo = tipo
        self._montar()
        self.escolheu.emit(tipo)


class PainelFiltroDaPagina(Painel):
    """Qual filtro está valendo, o deslizante dele, e "só neste pedaço"."""

    filtro_escolhido = Signal(str)
    filtro_do_pedaco = Signal(str)
    medidor_mudou = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__("Filtro da página", parent)
        self.filtro = ""
        self.filtro_pedaco = ""

    def atualizar(self, pagina) -> None:
        """Reconstroi o painel para a página atual: nome do filtro + tecla, o
        medidor do ajuste daquele filtro (cada filtro guarda o seu - ver o
        comentario abaixo) e os botões de "só neste pedaço"."""
        from core.filtros import (
            MAGICO_PRO,
            MELHORAR,
            NOMES_AMIGAVEIS,
            ORIGINAL,
            PRETO_E_BRANCO,
        )
        from PySide6.QtWidgets import QSlider

        self.limpar()
        if pagina is None:
            return

        self.filtro = pagina.filtro
        teclas = {ORIGINAL: 1, PRETO_E_BRANCO: 2, MELHORAR: 3, MAGICO_PRO: 4}

        linha = QWidget()
        linha.setStyleSheet("background: transparent; border: none;")
        dentro = QHBoxLayout(linha)
        dentro.setContentsMargins(0, 0, 0, 2)
        nome = QLabel(NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro))
        nome.setWordWrap(True)
        nome.setStyleSheet("font-size: 13px; background: transparent; border: none;")
        dentro.addWidget(nome)
        dentro.addStretch()
        tecla = QLabel(f"tecla {teclas.get(pagina.filtro, '')}")
        tecla.setWordWrap(True)
        tecla.setStyleSheet(
            f"color: {TEXTO_FRACO}; font-size: 11px; background: transparent; "
            "border: none;")
        dentro.addWidget(tecla)
        self.dentro.addWidget(linha)

        # O deslizante daquele filtro. Cada um tem o seu, e trocar de filtro e
        # voltar devolve o ajuste que AQUELE filtro tinha.
        campos = {
            PRETO_E_BRANCO: ("forca_preto", "força do preto"),
            MELHORAR: ("clareza_melhorar", "clareza do fundo"),
            MAGICO_PRO: ("intensidade_magico", "intensidade"),
        }
        if pagina.filtro in campos:
            campo, rotulo = campos[pagina.filtro]
            self._texto(rotulo, tamanho=11)
            barra = QSlider(Qt.Horizontal)
            barra.setRange(0, 100)
            barra.setValue(getattr(pagina, campo))
            barra.valueChanged.connect(self.medidor_mudou.emit)
            barra.setStyleSheet("border: none;")
            self.dentro.addWidget(barra)

        self._texto("só neste pedaço", tamanho=11)
        for chave, texto in (("", "o mesmo da página"),
                             (ORIGINAL, NOMES_AMIGAVEIS[ORIGINAL]),
                             (PRETO_E_BRANCO, NOMES_AMIGAVEIS[PRETO_E_BRANCO]),
                             (MELHORAR, NOMES_AMIGAVEIS[MELHORAR]),
                             (MAGICO_PRO, NOMES_AMIGAVEIS[MAGICO_PRO])):
            self._botao(texto,
                        lambda _c=False, k=chave: self._escolher_pedaco(k),
                        escolhido=(chave == self.filtro_pedaco))

    def _escolher_pedaco(self, chave: str) -> None:
        """Marca qual filtro vale "só neste pedaço" (chave vazia = o mesmo da página)."""
        self.filtro_pedaco = chave
        self.filtro_do_pedaco.emit(chave)


class PainelHistorico(Painel):
    """As ações da sessão, a mais recente embaixo. Clicar volta até ali.

    Usa o arquivo de desfazer que já existe - o mesmo JSON Lines que sobrevive
    a fechar o programa. Um segundo mecanismo de histórico ao lado do que já
    funciona seria duas verdades sobre o mesmo trabalho.
    """

    voltar_para = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__("Histórico", parent)

    def atualizar(self, acoes) -> None:
        """Mostra as últimas 12 ações (de acoes.feitas) na ordem do tempo, a
        mais recente embaixo e destacada."""
        self.limpar()
        if acoes is None or not acoes.feitas:
            self._texto("nada ainda")
            return

        # As ultimas primeiro na leitura, mas na ordem do tempo: a mais recente
        # fica embaixo, como no desenho.
        for posicao, acao in enumerate(acoes.feitas[-12:], start=max(
                0, len(acoes.feitas) - 12)):
            ultima = posicao == len(acoes.feitas) - 1
            botao = self._botao(
                acao.descricao,
                lambda _c=False, p=posicao: self.voltar_para.emit(p + 1),
                escolhido=ultima)
            botao.setToolTip("clicar volta o trabalho até aqui")

        self._texto("clicar volta até a ação", tamanho=11)


class ColunaDePaineis(QScrollArea):
    """Os quatro empilhados, na largura do desenho."""

    def __init__(self, parent=None) -> None:
        """Cria os quatro painéis (na ordem fixa comentada no topo do arquivo)
        dentro de uma area de rolagem vertical."""
        super().__init__(parent)
        self.setFixedWidth(LARGURA)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        dentro = QWidget()
        dentro.setStyleSheet(f"background: {FUNDO};")
        self.camadas = QVBoxLayout(dentro)
        self.camadas.setContentsMargins(0, 0, 0, 0)
        self.camadas.setSpacing(0)

        self.para_revisar = PainelParaRevisar()
        self.marcar_como = PainelMarcarComo()
        self.filtro_da_pagina = PainelFiltroDaPagina()
        self.historico = PainelHistorico()

        self.paineis = {
            "revisar": self.para_revisar,
            "marcar": self.marcar_como,
            "filtro": self.filtro_da_pagina,
            "historico": self.historico,
        }
        for painel in self.paineis.values():
            painel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            self.camadas.addWidget(painel)
        self.camadas.addStretch()

        self.setWidget(dentro)

    def mostrar_painel(self, chave: str, visivel: bool) -> None:
        """Do menu Ver: mostrar ou esconder cada painel."""
        painel = self.paineis.get(chave)
        if painel is not None:
            painel.setVisible(bool(visivel))
