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

A aparência é provisória (fica com o agente de layout): lista simples e
botões como os das outras janelas. Seguro mudar: textos, tamanhos, a ordem
dos botões. Arriscado: fazer a janela mudar o projeto direto (o desfazer
não saberia).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
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

# o que a pessoa escolheu ao sair da janela
VER = "ver"                    # ir para a página de `aviso_para_ver`
CONTINUAR = "continuar"        # processar assim mesmo
ACEITAR = "aceitar"            # dar "está bom" nos `marcados`
FECHAR = ""                    # fechou sem escolher (não processa)

TODOS_OS_MOTIVOS = ""


class JanelaDosAvisos(QDialog):
    """A lista das páginas com aviso e os motivos (ver o topo do arquivo)."""

    def __init__(self, avisos: list, antes_de_processar: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.avisos = list(avisos)
        self.antes_de_processar = bool(antes_de_processar)
        self.escolha = FECHAR
        self.aviso_para_ver = None
        self.marcados: list = []

        self.setWindowTitle("Antes de processar" if antes_de_processar else "Para revisar")
        self.setModal(True)
        self.resize(560, 520)

        camadas = QVBoxLayout(self)
        self.rotulo = QLabel(self._frase())
        self.rotulo.setWordWrap(True)
        camadas.addWidget(self.rotulo)

        # mostrar só um motivo ("todas as páginas com aquele problema")
        linha_filtro = QHBoxLayout()
        linha_filtro.addWidget(QLabel("Mostrar:"))
        self.combo_motivo = QComboBox()
        self.combo_motivo.addItem(f"todos os motivos ({len(self.avisos)})", TODOS_OS_MOTIVOS)
        for codigo, do_motivo in avisos_do_livro.por_motivo(self.avisos).items():
            self.combo_motivo.addItem(f"{do_motivo[0].titulo} ({len(do_motivo)})", codigo)
        self.combo_motivo.currentIndexChanged.connect(lambda _i: self._encher_a_lista())
        linha_filtro.addWidget(self.combo_motivo, 1)
        camadas.addLayout(linha_filtro)

        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(lambda _item: self._ver())
        camadas.addWidget(self.lista, 1)

        linha_marcar = QHBoxLayout()
        self.botao_todas = QPushButton("Selecionar todas")
        self.botao_todas.clicked.connect(lambda *_: self._marcar_todas(True))
        linha_marcar.addWidget(self.botao_todas)
        self.botao_nenhuma = QPushButton("Nenhuma")
        self.botao_nenhuma.clicked.connect(lambda *_: self._marcar_todas(False))
        linha_marcar.addWidget(self.botao_nenhuma)
        linha_marcar.addStretch()
        self.botao_aceitar = QPushButton("está bom nas marcadas")
        self.botao_aceitar.setToolTip(
            "Tira da lista as linhas marcadas. Não muda nada nas páginas; "
            "o Desfazer traz de volta.")
        self.botao_aceitar.clicked.connect(lambda *_: self._aceitar())
        linha_marcar.addWidget(self.botao_aceitar)
        camadas.addLayout(linha_marcar)

        linha_sair = QHBoxLayout()
        linha_sair.addStretch()
        self.botao_ver = QPushButton("ver")
        self.botao_ver.setToolTip("Vai para a página da linha escolhida (ou a primeira da lista).")
        self.botao_ver.clicked.connect(lambda *_: self._ver())
        linha_sair.addWidget(self.botao_ver)
        self.botao_continuar = QPushButton(
            "continuar assim mesmo" if antes_de_processar else "fechar")
        self.botao_continuar.clicked.connect(lambda *_: self._continuar())
        linha_sair.addWidget(self.botao_continuar)
        camadas.addLayout(linha_sair)

        self._encher_a_lista()
        self.botao_ver.setDefault(True)

    # --- montagem ---------------------------------------------------------

    def _frase(self) -> str:
        if self.antes_de_processar:
            return (avisos_do_livro.frase_de_quantos(self.avisos)
                    + " Quer ver antes ou continuar assim mesmo?")
        return ("As páginas com aviso e o motivo de cada uma. Marque as que estão boas "
                "e clique em \"está bom nas marcadas\", ou escolha uma e clique em \"ver\".")

    def _visiveis(self) -> list:
        """Os avisos do motivo escolhido na lista "Mostrar" (ou todos)."""
        codigo = self.combo_motivo.currentData()
        if not codigo:
            return list(self.avisos)
        return [a for a in self.avisos if a.codigo == codigo]

    def _encher_a_lista(self) -> None:
        """Uma linha por motivo de cada página: "Página 12 - Desenho apagado",
        com a caixinha desmarcada."""
        self.lista.clear()
        for aviso in self._visiveis():
            item = QListWidgetItem(f"{aviso.onde}  -  {aviso.titulo}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, aviso)
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
