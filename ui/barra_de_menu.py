"""A barra de menu da janela: Arquivo · Editar · Marcar · Filtro · Página · Ver · Ajuda.

Ela existe para tirar botao solto da tela. Antes, "limpar tudo", "procurar de
novo" e "deixar a folha em branco" eram tres botoes largos atravessando a
janela, roubando altura da pagina - que e o que a pessoa precisa olhar.

Cada acao aparece em UM lugar so, e o atalho vem escrito ao lado. E a lista de
atalhos de Ajuda sai desta mesma tabela: um menu que promete um atalho e uma
ajuda que promete outro e pior do que nao ter nenhum dos dois.

Na tela inicial so tres menus ficam de pe - Arquivo, Ver e Ajuda -, como no
desenho aprovado. Os outros ficam apagados: sumir e voltar faria a barra pular
de largura ao trocar de tela.
"""

from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar

# Os menus que valem em cada tela. Fora da tela de trabalho, o resto fica
# apagado - e nao escondido.
MENUS_DA_TELA_INICIAL = ("Arquivo", "Ver", "Ajuda")


class BarraDeMenu(QMenuBar):
    """Monta os menus e guarda as acoes pelo nome, para a janela ligar depois."""

    def __init__(self, janela) -> None:
        """Monta os sete menus de uma vez. Ligar cada acao a um metodo de
        verdade e trabalho de quem cria a janela - ver `ligar`."""
        super().__init__(janela)
        self.janela = janela
        self.acoes: dict[str, QAction] = {}
        self.menus: dict[str, object] = {}
        # Quais acoes ja foram ligadas a alguma coisa. Serve para a bateria
        # cobrar a lista de conferencia: item de menu que nao faz nada e pior
        # do que item que nao existe.
        self.ligadas: set[str] = set()

        self._montar_arquivo()
        self._montar_editar()
        self._montar_marcar()
        self._montar_filtro()
        self._montar_pagina()
        self._montar_ver()
        self._montar_ajuda()

    # --- montagem ---------------------------------------------------------

    def _menu(self, titulo: str):
        """Cria um menu de topo e guarda pelo titulo, para mostrar/esconder depois."""
        menu = self.addMenu(titulo)
        self.menus[titulo] = menu
        return menu

    def _acao(self, menu, chave: str, texto: str, atalho: str = "",
              acao=None) -> QAction:
        """Cria um item de menu, guarda em self.acoes[chave] para `ligar` achar
        depois, e opcionalmente ja conecta a uma funcao (`acao`)."""
        item = QAction(texto, self.janela)
        if atalho:
            item.setShortcut(QKeySequence(atalho))
        if acao is not None:
            item.triggered.connect(acao)
        menu.addAction(item)
        self.acoes[chave] = item
        return item

    def _montar_arquivo(self) -> None:
        menu = self._menu("Arquivo")
        self._acao(menu, "abrir", "Abrir um livro...", "Ctrl+O")
        self.menu_recentes = menu.addMenu("Livros recentes")
        menu.addSeparator()
        self._acao(menu, "pasta_de_saida", "Escolher a pasta de saída...")
        self._acao(menu, "nome_do_arquivo", "Nome do arquivo...")
        menu.addSeparator()
        self._acao(menu, "processar", "Confirmar e processar", "Ctrl+Return")
        menu.addSeparator()
        self._acao(menu, "voltar", "Voltar para as opções")
        self._acao(menu, "sair", "Sair", "Ctrl+Q")

    def _montar_editar(self) -> None:
        menu = self._menu("Editar")
        self._acao(menu, "desfazer", "Desfazer", "Ctrl+Z")
        self._acao(menu, "refazer", "Refazer", "Ctrl+Shift+Z")
        menu.addSeparator()
        self._acao(menu, "historico", "Mostrar o histórico")

    def _montar_marcar(self) -> None:
        menu = self._menu("Marcar")
        self._acao(menu, "procurar_de_novo", "Procurar de novo")
        self._acao(menu, "limpar_marcacao", "Limpar tudo")
        menu.addSeparator()
        self._acao(menu, "folha_em_branco", "Deixar a folha em branco")

    def _montar_filtro(self) -> None:
        menu = self._menu("Filtro")
        from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO

        for numero, (chave, nome) in enumerate(
            ((ORIGINAL, "Original"), (PRETO_E_BRANCO, "Preto e branco"),
             (MELHORAR, "Melhorar"), (MAGICO_PRO, "Mágico pro")), start=1
        ):
            item = self._acao(menu, f"filtro_{chave}", nome, str(numero))
            item.setCheckable(True)

    def _montar_pagina(self) -> None:
        menu = self._menu("Página")
        self._acao(menu, "ir_para_pagina", "Ir para a página...", "Ctrl+G")
        menu.addSeparator()
        self._acao(menu, "girar", "Girar")
        self._acao(menu, "apagar", "Apagar esta página", "Del")
        self._acao(menu, "restaurar", "Restaurar página apagada")

    def _montar_ver(self) -> None:
        menu = self._menu("Ver")
        self._acao(menu, "mais_zoom", "Aproximar", "Ctrl++")
        self._acao(menu, "menos_zoom", "Afastar", "Ctrl+-")
        self._acao(menu, "ajustar", "Ajustar à tela", "Ctrl+0")
        menu.addSeparator()
        for chave, texto in (("painel_revisar", "Painel: Para revisar"),
                             ("painel_marcar", "Painel: Marcar como"),
                             ("painel_filtro", "Painel: Filtro da página"),
                             ("painel_historico", "Painel: Histórico")):
            item = self._acao(menu, chave, texto)
            item.setCheckable(True)
            item.setChecked(True)
        menu.addSeparator()
        item = self._acao(menu, "comparar", "Modo comparar")
        item.setCheckable(True)

    def _montar_ajuda(self) -> None:
        menu = self._menu("Ajuda")
        self._acao(menu, "atalhos", "Lista de atalhos", "F1")

    # --- estado por tela --------------------------------------------------

    def mostrar_tela_inicial(self) -> None:
        """Apaga (nao esconde) os menus que so fazem sentido na tela de trabalho.

        Esconder e reaparecer mudaria a largura da barra ao trocar de tela -
        ver o comentario do modulo.
        """
        for titulo, menu in self.menus.items():
            menu.menuAction().setEnabled(titulo in MENUS_DA_TELA_INICIAL)
        for chave in ("pasta_de_saida", "nome_do_arquivo", "processar", "voltar"):
            self.acoes[chave].setEnabled(False)

    def mostrar_tela_de_trabalho(self) -> None:
        """Reacende todos os menus, ao entrar na tela de trabalho."""
        for menu in self.menus.values():
            menu.menuAction().setEnabled(True)
        for chave in ("pasta_de_saida", "nome_do_arquivo", "processar", "voltar"):
            self.acoes[chave].setEnabled(True)

    def ligar(self, chave: str, acao) -> None:
        """Liga uma acao ja montada. Levanta se o nome nao existir.

        De proposito: um menu que aponta para o vazio e pior do que um menu que
        nao existe - a pessoa clica, nada acontece, e ela acha que o programa
        travou.
        """
        if chave not in self.acoes:
            raise KeyError(f"não existe ação de menu chamada {chave!r}")
        self.acoes[chave].triggered.connect(acao)
        self.ligadas.add(chave)

    # --- a lista de atalhos, tirada dos proprios menus --------------------

    def texto_dos_atalhos(self) -> str:
        """A lista de Ajuda sai DAQUI, e nao de uma segunda lista escrita a mao.

        Duas listas separadas divergem na primeira mudanca, e a ajuda passa a
        mentir sobre o programa.
        """
        linhas = []
        for titulo, menu in self.menus.items():
            do_menu = [
                f"    {a.text().replace('&', '')}"
                f"{'  —  ' + a.shortcut().toString() if not a.shortcut().isEmpty() else ''}"
                for a in menu.actions()
                if not a.isSeparator() and not a.menu()
            ]
            if do_menu:
                linhas.append(titulo)
                linhas.extend(do_menu)
                linhas.append("")
        return "\n".join(linhas).strip()
