"""A lista grande dos avisos: as páginas e os motivos (12/10/2026).

O PEDIDO
    Samuel, rodada 4 do "Para revisar" (08/10/2026, `rv4-aviso-so-texto`): "eu
    devo conseguir abrir um selecionador em aba grande mostrando todas as
    paginas com aquele problema e deselecionar ou dar ok em todas [...] quando
    alguém tentar imprimir sem ver os alertas o programa para e mostra os
    alertas e a pessoa diz se quer ver ou continuar". Rodada 5
    (`rv5-aviso-so-texto`): a janela "Antes de processar" "Lista as páginas e
    os motivos", com "ver" e "continuar assim mesmo" (antes ela só dizia
    quantas páginas). Botões rápidos do seletor (`rv5-conserto-faixa`): só
    "Selecionar todas" e "Nenhuma".

O QUE É
    Uma janela só, usada de dois jeitos (ui/tela_conferir.py):
      - "Antes de processar" (antes_de_processar=True): aparece quando a
        pessoa pede para processar com avisos sem olhar. Tem "ver" e
        "continuar assim mesmo".
      - o seletor do painel "Para revisar" ("ver a lista…"): a mesma lista,
        com "ver" e "fechar".
    Nos dois, cada linha é um motivo de uma página, com uma caixinha; "está
    bom nas marcadas" tira da lista as linhas marcadas.

    A janela NÃO mexe no projeto: ela só devolve o que a pessoa escolheu
    (`escolha`, `aviso_para_ver`, `marcados`); quem aplica é a tela de
    conferir, pelo histórico (o Ctrl+Z desfaz).

A aparência foi arrumada pelo agente de layout em 22/10/2026 (Samuel, 21/10,
`pr-antes-de-processar`: "ficou meio embolado, deve ficar mais claro e não
tão grande."): janela menor (500 x 400 em vez de 560 x 520), a frase de cima
em duas linhas (o que aconteceu, forte; o que fazer, fraco), "Selecionar
todas" e "Nenhuma" pequenos na linha de cima da lista, junto do "Mostrar", e
uma fila só embaixo ("está bom nas marcadas" à esquerda; "ver", em azul, e
"continuar assim mesmo" à direita). Nenhum controle saiu nem mudou de nome.
Seguro mudar: tamanhos, cores, a ordem dos botões. Arriscado: fazer a janela mudar o projeto direto (o desfazer
não saberia).
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from core import avisos as avisos_do_livro
from ui import estilo

# o tamanho com que a janela abre, em pontos (antes 560 x 520; ver __init__)
TAMANHO_DA_JANELA = (500, 400)


def _folha() -> str:
    """O estilo próprio da janela, com as cores do tema da vez (estilo.estilizar):
    a frase de cima forte, a pergunta mais fraca, as linhas da lista mais
    baixas (cabem mais sem a janela crescer), "Selecionar todas" e "Nenhuma"
    pequenos (são ajuda para marcar, não saídas) e o "ver" em azul. Seguro
    mudar: tamanhos e cores. Os nomes (#...) são os dos objectName do __init__."""
    c = estilo.cor
    return (f"QLabel#fraseDosAvisos {{ color: {c('forte')}; font-size: 15px; font-weight: 600; }}"
            f"QLabel#perguntaDosAvisos {{ color: {c('fraco')}; }}"
            f"QListWidget#listaDosAvisos {{ background: {c('painel')}; border: 1px solid {c('sep')};"
            f" border-radius: 6px; padding: 2px; }}"
            f"QListWidget#listaDosAvisos::item {{ padding: 0px 4px; }}"
            f"QPushButton#marcarDosAvisos {{ padding: 4px 10px; font-size: 13px; }}"
            f"QPushButton#verDosAvisos {{ background: {c('azul')}; color: white; border: none;"
            f" font-weight: 600; padding: 9px 22px; }}"
            f"QPushButton#verDosAvisos:hover {{ background: {c('azul_e')}; }}")


# o que a pessoa escolheu ao sair da janela
VER = "ver"                    # ir para a página de `aviso_para_ver`
CONTINUAR = "continuar"        # processar assim mesmo
ACEITAR = "aceitar"            # dar "está bom" nos `marcados`
FECHAR = ""                    # fechou sem escolher (não processa)

TODOS_OS_MOTIVOS = ""


class JanelaDosAvisos(QDialog):
    """A lista das páginas com aviso e os motivos (ver o topo do arquivo)."""

    def __init__(self, avisos: list, antes_de_processar: bool = False, parent=None,
                 projeto=None) -> None:
        """projeto: o livro, so para a frase de cima contar as PAGINAS certo
        (o aviso de uma folha e o da pagina dela sao a mesma pagina:
        core.avisos.paginas_com_aviso). Sem ele, cada folha conta como uma."""
        super().__init__(parent)
        self.avisos = list(avisos)
        self.projeto = projeto
        self.antes_de_processar = bool(antes_de_processar)
        self.escolha = FECHAR
        self.aviso_para_ver = None
        self.marcados: list = []

        self.setWindowTitle("Antes de processar" if antes_de_processar else "Para revisar")
        self.setObjectName("janelaDosAvisos")
        self.setModal(True)
        # menor que antes (560 x 520): Samuel, 21/10/2026, `pr-antes-de-processar`:
        # "ficou meio embolado, deve ficar mais claro e não tão grande." Cabe
        # folgada no notebook do Kaique (1280 x 657); dá para aumentar puxando.
        self.resize(TAMANHO_DA_JANELA[0], TAMANHO_DA_JANELA[1])

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(18, 16, 18, 14)
        camadas.setSpacing(8)
        # em cima, em duas linhas: o que aconteceu (forte) e o que fazer (fraco)
        frase, pergunta = self._frases()
        self.rotulo = QLabel(frase)
        self.rotulo.setObjectName("fraseDosAvisos")
        self.rotulo.setWordWrap(True)
        camadas.addWidget(self.rotulo)
        self.pergunta = QLabel(pergunta)
        self.pergunta.setObjectName("perguntaDosAvisos")
        self.pergunta.setWordWrap(True)
        camadas.addWidget(self.pergunta)
        camadas.addSpacing(4)

        # a linha de cima da lista: mostrar só um motivo ("todas as páginas
        # com aquele problema") e, do outro lado, marcar todas ou nenhuma
        linha_filtro = QHBoxLayout()
        linha_filtro.setSpacing(6)
        linha_filtro.addWidget(QLabel("Mostrar:"))
        self.combo_motivo = QComboBox()
        self.combo_motivo.addItem(f"todos os motivos ({len(self.avisos)})", TODOS_OS_MOTIVOS)
        for codigo, do_motivo in avisos_do_livro.por_motivo(self.avisos).items():
            self.combo_motivo.addItem(f"{do_motivo[0].titulo} ({len(do_motivo)})", codigo)
        self.combo_motivo.currentIndexChanged.connect(lambda _i: self._encher_a_lista())
        # a lista não cresce até o motivo mais comprido (a janela ficava larga)
        self.combo_motivo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.combo_motivo.setMinimumContentsLength(20)
        linha_filtro.addWidget(self.combo_motivo)
        linha_filtro.addStretch(1)
        self.botao_todas = QPushButton("Selecionar todas")
        self.botao_todas.setObjectName("marcarDosAvisos")
        self.botao_todas.setCursor(Qt.PointingHandCursor)
        self.botao_todas.clicked.connect(lambda *_: self._marcar_todas(True))
        linha_filtro.addWidget(self.botao_todas)
        self.botao_nenhuma = QPushButton("Nenhuma")
        self.botao_nenhuma.setObjectName("marcarDosAvisos")
        self.botao_nenhuma.setCursor(Qt.PointingHandCursor)
        self.botao_nenhuma.clicked.connect(lambda *_: self._marcar_todas(False))
        linha_filtro.addWidget(self.botao_nenhuma)
        camadas.addLayout(linha_filtro)

        self.lista = QListWidget()
        self.lista.setObjectName("listaDosAvisos")
        self.lista.itemDoubleClicked.connect(lambda _item: self._ver())
        camadas.addWidget(self.lista, 1)

        # embaixo, uma fila só: à esquerda o que vale para as marcadas, à
        # direita as duas saídas (a de fábrica, "ver", em azul: não processa)
        linha_sair = QHBoxLayout()
        linha_sair.setSpacing(8)
        self.botao_aceitar = QPushButton("está bom nas marcadas")
        self.botao_aceitar.setToolTip(
            "Tira da lista as linhas marcadas. Não muda nada nas páginas; "
            "o Desfazer traz de volta.")
        self.botao_aceitar.clicked.connect(lambda *_: self._aceitar())
        linha_sair.addWidget(self.botao_aceitar)
        linha_sair.addStretch(1)
        self.botao_ver = QPushButton("ver")
        self.botao_ver.setObjectName("verDosAvisos")
        self.botao_ver.setToolTip("Vai para a página da linha escolhida (ou a primeira da lista).")
        self.botao_ver.clicked.connect(lambda *_: self._ver())
        linha_sair.addWidget(self.botao_ver)
        self.botao_continuar = QPushButton(
            "continuar assim mesmo" if antes_de_processar else "fechar")
        if antes_de_processar:
            self.botao_continuar.setToolTip("Processa o livro como está, com os avisos.")
        self.botao_continuar.clicked.connect(lambda *_: self._continuar())
        linha_sair.addWidget(self.botao_continuar)
        camadas.addSpacing(2)
        camadas.addLayout(linha_sair)

        estilo.estilizar(self, _folha)
        self._encher_a_lista()
        self.botao_ver.setDefault(True)

    # --- montagem ---------------------------------------------------------

    def _frases(self) -> tuple[str, str]:
        """(o que aconteceu, o que fazer): as duas linhas de cima. Antes era
        uma frase só, comprida (22/10/2026: separada para ficar mais clara)."""
        if self.antes_de_processar:
            return (avisos_do_livro.frase_de_quantos(self.avisos, self.projeto),
                    "Quer ver antes ou continuar assim mesmo?")
        return ("As páginas com aviso e o motivo de cada uma.",
                "Marque as que estão boas e clique em \"está bom nas marcadas\", "
                "ou escolha uma e clique em \"ver\".")

    def _visiveis(self) -> list:
        """Os avisos do motivo escolhido na lista "Mostrar" (ou todos)."""
        codigo = self.combo_motivo.currentData()
        if not codigo:
            return list(self.avisos)
        return [a for a in self.avisos if a.codigo == codigo]

    def _encher_a_lista(self) -> None:
        """Uma linha por motivo de cada página: "Página 12 - Desenho apagado",
        com a caixinha desmarcada. O aviso de uma folha diz as páginas dela
        ("Páginas 3 e 4 - Qualidade baixa"; core.avisos.onde_no_livro), para a
        lista não misturar folha e página (verificador, 20/10/2026)."""
        self.lista.clear()
        altura = self.lista.fontMetrics().height() + 10
        for aviso in self._visiveis():
            onde = avisos_do_livro.onde_no_livro(aviso, self.projeto)
            item = QListWidgetItem(f"{onde}  -  {aviso.titulo}")
            if aviso.alvo == avisos_do_livro.FOLHA:
                item.setToolTip(f"Aviso da folha {aviso.indice + 1} do PDF de entrada.")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, aviso)
            item.setSizeHint(QSize(0, altura))     # linhas mais baixas: cabem mais
            self.lista.addItem(item)
        if self.lista.count():
            self.lista.setCurrentRow(0)

    # --- consulta (também para os testes) ---------------------------------

    def linhas(self) -> list[str]:
        """Os textos das linhas que estão na lista agora."""
        return [self.lista.item(i).text() for i in range(self.lista.count())]

    def avisos_marcados(self) -> list:
        return [self.lista.item(i).data(Qt.UserRole) for i in range(self.lista.count())
                if self.lista.item(i).checkState() == Qt.Checked]

    # --- ações ------------------------------------------------------------

    def _marcar_todas(self, marcar: bool) -> None:
        estado = Qt.Checked if marcar else Qt.Unchecked
        for i in range(self.lista.count()):
            self.lista.item(i).setCheckState(estado)

    def _aceitar(self) -> None:
        """"está bom nas marcadas": sai dizendo quais. Sem nenhuma marcada,
        não faz nada (a janela continua aberta)."""
        marcados = self.avisos_marcados()
        if not marcados:
            return
        self.marcados = marcados
        self.escolha = ACEITAR
        self.accept()

    def _ver(self) -> None:
        """"ver": a página da linha escolhida; sem linha escolhida, a primeira."""
        item = self.lista.currentItem() or (self.lista.item(0) if self.lista.count() else None)
        if item is None:
            return
        self.aviso_para_ver = item.data(Qt.UserRole)
        self.escolha = VER
        self.accept()

    def _continuar(self) -> None:
        """"continuar assim mesmo" (ou "fechar", no seletor do painel)."""
        self.escolha = CONTINUAR if self.antes_de_processar else FECHAR
        self.accept()
