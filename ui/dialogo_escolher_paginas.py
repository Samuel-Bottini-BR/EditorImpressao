"""Janela "Em quais páginas?" do "usar em todas" do Cortar (item 2.13).

PEDIDO DO SAMUEL ("Para revisar", rodada 4, 08/10/2026): "nós podemos alterar
o corte sugerido, ou fazer um corte e mandar para todas as paginas e alterar
em algumas paginas só o corte quando cortamos alguma, assim quando mudar de um
não muda de todas, eu devo conseguir abrir uma aba para selecionar as que eu
quero ( as paginas) ou também simplismente apertar num botão e selecionar
todas." Rodada 5 (09/10, rv5-conserto-faixa): seletor só com "Selecionar
todas" e "Nenhuma".

Conserta o bug da Lista de bugs de 08/10/2026: "O 'usar em todas' da aba Bordas
apaga as exceções por página". De fábrica a lista vem marcada nas páginas que
NÃO têm corte próprio (as exceções ficam desmarcadas e não mudam), e a página
da vez sempre marcada. O Kaique muda o que quiser e confirma.

paginas_de_fabrica() é a regra (sem tela, testada); a janela só mostra.
Controle mínimo: o desenho é do agente de layout.

Etapa 5 da obra de 26/10/2026: a mesma janela serve ao "usar em todas..." da
ferramenta Mover (G10 do Samuel, 05/10/2026: "ter uma opção para passar isso
para todas as folhas"), com a mesma regra de D-090 ("nunca apaga exceção"): as
páginas que já têm tamanho ou lugar próprio do conteúdo vêm desmarcadas. Quem
chama passa `tem_proprio` (a regra da exceção), a `explicacao` e a `marca` que
aparece ao lado da página. Sem eles, é a janela do Cortar, como sempre.

Etapa 9b-2 da obra (promessa P-061; D-090: "usar em todas" abre a lista das
páginas com as exceções desmarcadas e nunca apaga exceção; o Livro dizia "no
Dividir ainda aplica em todas sem seletor"): a mesma janela serve ao "usar em
todas" do Dividir, com as FOLHAS (`itens=projeto.folhas`, `nome="Folha"`): as
folhas em que a pessoa já acertou a linha à mão vêm desmarcadas.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QPushButton, QVBoxLayout)


def _corte_proprio(pagina) -> bool:
    """A exceção do Cortar: a página tem corte próprio."""
    return pagina.recorte is not None


def paginas_de_fabrica(projeto, indice_da_vez: int, tem_proprio=None, itens=None) -> list[int]:
    """As páginas que vêm marcadas: a da vez e todas as que não têm o seu
    próprio (`tem_proprio`; de fábrica, o corte próprio: recorte não None).
    As que têm o seu (exceções) e as apagadas ficam desmarcadas.
    itens: a lista (de fábrica, projeto.paginas; o Dividir passa as folhas)."""
    tem_proprio = tem_proprio or _corte_proprio
    marcadas = []
    for p in (projeto.paginas if itens is None else itens):
        if p.indice == indice_da_vez or (not tem_proprio(p) and not getattr(p, "apagada", False)):
            marcadas.append(p.indice)
    return marcadas


class DialogoEscolherPaginas(QDialog):
    """A lista das páginas com caixinha, "Selecionar todas", "Nenhuma",
    "Aplicar" e "Cancelar". escolhidas() devolve os índices marcados."""

    def __init__(self, projeto, indice_da_vez: int, parent=None, *, tem_proprio=None,
                 explicacao: str | None = None, marca: str = "corte próprio",
                 itens=None, nome: str = "Página") -> None:
        super().__init__(parent)
        self.setWindowTitle("Em quais páginas?")
        coluna = QVBoxLayout(self)
        explicacao = QLabel(explicacao or (
            "O corte desta página vai para as páginas marcadas. As páginas em que você "
            "já mudou o corte vêm desmarcadas, para não perder o que fez nelas."))
        explicacao.setWordWrap(True)
        coluna.addWidget(explicacao)
        self.lista = QListWidget()
        tem_proprio = tem_proprio or _corte_proprio
        marcadas = set(paginas_de_fabrica(projeto, indice_da_vez, tem_proprio, itens))
        for p in (projeto.paginas if itens is None else itens):
            texto = f"{nome} {p.indice + 1}"
            if tem_proprio(p) and p.indice != indice_da_vez:
                texto += f"  ({marca})"
            if getattr(p, "apagada", False):
                texto += "  (apagada)"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, p.indice)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if p.indice in marcadas else Qt.Unchecked)
            self.lista.addItem(item)
        coluna.addWidget(self.lista, 1)
        linha = QHBoxLayout()
        self.botao_todas = QPushButton("Selecionar todas")
        self.botao_todas.clicked.connect(lambda: self._marcar_todas(True))
        self.botao_nenhuma = QPushButton("Nenhuma")
        self.botao_nenhuma.clicked.connect(lambda: self._marcar_todas(False))
        linha.addWidget(self.botao_todas)
        linha.addWidget(self.botao_nenhuma)
        linha.addStretch()
        coluna.addLayout(linha)
        botoes = QDialogButtonBox()
        botoes.addButton("Aplicar", QDialogButtonBox.AcceptRole)
        botoes.addButton("Cancelar", QDialogButtonBox.RejectRole)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        coluna.addWidget(botoes)
        self.resize(360, 480)

    def _marcar_todas(self, marcar: bool) -> None:
        for i in range(self.lista.count()):
            self.lista.item(i).setCheckState(Qt.Checked if marcar else Qt.Unchecked)

    def escolhidas(self) -> list[int]:
        return [int(self.lista.item(i).data(Qt.UserRole)) for i in range(self.lista.count())
                if self.lista.item(i).checkState() == Qt.Checked]
