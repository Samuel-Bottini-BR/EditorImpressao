"""A barra de menu da janela: Arquivo · Editar · Ferramentas · Marcar · Filtro · Página · Ver · Painéis · Ajuda.

Etapa 2 da obra (26/10/2026):
  - menu novo "Ferramentas" (teste do Kaique, 26/10: "nenhum menu tem
    Endireitar, Cortar ou Dividir"; as ferramentas só tinham ícone): todas
    as da trilha, com o nome e a letra do atalho, a da vez marcada;
  - menu Página: "Deixar esta página em branco" (tecla Delete) e "Tirar esta
    página do livro" (Samuel, 07/10/2026: "Deixar em branco" (tecla Delete;
    página branca no lugar, encadernação não muda) e "Tirar do livro"). A
    Delete apagava a página;
  - menu Ver > "Lado direito": ícones na borda (de fábrica) ou a área de
    trabalho 1, em sanfona (R7 203 D: "Mas eu também quero ter a opção da
    area de trabalho 1"; R14 902 C: no menu Ver e nas Configurações);
  - com um livro aberto todos os menus ficam acesos (lista única 1.12; ver
    janela_principal._tela_mudou).

Rodada 14 do layout (Samuel, 20/10/2026): 903 "B — Um menu novo, “Painéis”"
(os cinco painéis da direita, "Fechar o painel" e os ícones da direita, como o
"Janela" do Photoshop; os quatro "Painel: ..." que o menu Ver tinha, e que
nunca fizeram nada, saíram) e 904 "A — Sim, no menu Ver" (as peças novas da
tela ganham item no menu Ver: por enquanto "Miniaturas" e "Ícones da
direita", "Todas as páginas" (etapa 5) e "Filtros em tela cheia" (etapa
6); "Ver lado a lado" entra quando essa tela existir - item que não
faz nada não entra).

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

import atalhos
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar

# Os menus que valem em cada tela. Fora da tela de trabalho, o resto fica
# apagado - e nao escondido.
MENUS_DA_TELA_INICIAL = ("Arquivo", "Ver", "Ajuda")


class BarraDeMenu(QMenuBar):
    """Monta os menus e guarda as acoes pelo nome, para a janela ligar depois."""

    # Emitido no fim de reaplicar_atalhos: quem mostra uma tecla fora do menu
    # (o balao dos botoes de girar, item 2.3) se acerta por aqui.
    atalhos_mudaram = Signal()

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
        self._montar_ferramentas()
        self._montar_marcar()
        self._montar_filtro()
        self._montar_pagina()
        self._montar_ver()
        self._montar_paineis()
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
        # Registrado no atalhos.py mesmo quando não tem tecla nenhuma (atalho
        # vazio) - assim toda ação de menu aparece na mesma tabela; só as que
        # já têm uma tecla de fábrica ficam editáveis na tela de
        # Configurações (ver TelaConfiguracoes).
        if atalho:
            atalhos.registrar(chave, texto.replace("&", ""), atalho)
        item = QAction(texto, self.janela)
        tecla = atalhos.tecla_atual(chave) if atalho else ""
        if tecla:
            item.setShortcut(QKeySequence(tecla))
        if acao is not None:
            item.triggered.connect(acao)
        menu.addAction(item)
        self.acoes[chave] = item
        return item

    def reaplicar_atalhos(self) -> None:
        """Copia o registro (atalhos.py) para os QAction de verdade.

        Chamado ao iniciar (depois de carregar o que o Samuel salvou) e toda
        vez que a tela de Configurações muda alguma tecla - sem isso o menu
        continuaria mostrando a tecla antiga até reabrir o programa.
        """
        for chave, item in self.acoes.items():
            tecla = atalhos.tecla_atual(chave)
            item.setShortcut(QKeySequence(tecla) if tecla else QKeySequence())
        # a letra mostrada no menu Ferramentas acompanha a troca
        for ferramenta in getattr(self, "ferramentas_do_menu", ()):
            self.acoes[f"usar_{ferramenta}"].setText(self._texto_da_ferramenta(ferramenta))
        self.atalhos_mudaram.emit()

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
        # Etapa 3 da obra (D-002): a tela "O que fazer" saiu do caminho. O
        # Automático (a janela grande) mora aqui e no painel da direita; o
        # "voltar" leva aos livros.
        self._acao(menu, "automatico", "Automático...")
        self._acao(menu, "voltar", "Voltar para os livros")
        menu.addSeparator()
        self._acao(menu, "configuracoes", "Configurações...")
        self._acao(menu, "sair", "Sair", "Ctrl+Q")

    def _montar_editar(self) -> None:
        menu = self._menu("Editar")
        self._acao(menu, "desfazer", "Desfazer", "Ctrl+Z")
        self._acao(menu, "refazer", "Refazer", "Ctrl+Shift+Z")
        menu.addSeparator()
        self._acao(menu, "historico", "Mostrar o histórico")

    def _montar_ferramentas(self) -> None:
        """Menu Ferramentas (etapa 2 da obra, 26/10/2026; teste do Kaique:
        nenhum menu tinha Endireitar, Cortar ou Dividir). As ferramentas da
        trilha, na ordem dela, com o nome escrito e a letra do atalho na coluna
        da direita (a letra é a de hoje: remapeada nas Configurações, muda aqui
        também, em reaplicar_atalhos). Marcada, a ferramenta da vez
        (marcar_ferramenta). A letra é só mostrada aqui: quem atende a tecla é
        a tela (TelaConferir.tratar_tecla), como sempre - um atalho de uma
        letra no menu roubaria a letra de quem digita num campo. Chaves
        "usar_<ferramenta>"."""
        from PySide6.QtGui import QActionGroup

        from ui.widgets.trilha_agrupada import GRUPOS

        menu = self._menu("Ferramentas")
        self.grupo_de_ferramentas = QActionGroup(self.janela)
        self.grupo_de_ferramentas.setExclusive(True)
        self.ferramentas_do_menu: list[str] = []
        for grupo in GRUPOS:
            if grupo == "-":
                menu.addSeparator()
                continue
            for ferramenta in grupo:
                item = self._acao(menu, f"usar_{ferramenta}", self._texto_da_ferramenta(ferramenta))
                item.setCheckable(True)
                self.grupo_de_ferramentas.addAction(item)
                self.ferramentas_do_menu.append(ferramenta)

    @staticmethod
    def _texto_da_ferramenta(ferramenta: str) -> str:
        """O nome da ferramenta e, depois de um tab (a coluna da direita do
        menu), a letra do atalho de hoje, se ela tiver uma."""
        from ui.widgets.trilha_agrupada import NOMES, tecla_de

        letra = tecla_de(ferramenta)
        return NOMES[ferramenta] + (("\t" + letra) if letra else "")

    def marcar_ferramenta(self, ferramenta: str | None) -> None:
        """Deixa marcada, no menu Ferramentas, a ferramenta da vez (sem
        virar clique)."""
        for nome in getattr(self, "ferramentas_do_menu", ()):
            item = self.acoes[f"usar_{nome}"]
            item.blockSignals(True)
            item.setChecked(nome == ferramenta)
            item.blockSignals(False)

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
        """Menu Pagina. Item 2.3 (girar, conferencia 14, G1 (c) "Os dois"): os
        tres giros, com tecla, e o "Aplicar o giro em", que e o MESMO da
        barrinha de girar em cima da pagina (ui/widgets/barra_girar.py; a
        janela mantem os dois iguais). "girar" continua sendo o 1/4 a direita
        de sempre (mesma chave, para nada que ja ligava nela quebrar).

        Teclas: Ctrl+Esquerda e Ctrl+Direita (sugeridas no formulario 14;
        livres - conferido contra todo o registro de atalhos.py e o
        tratar_tecla da tela de conferir). A meia volta fica sem tecla de
        fabrica (Ctrl+Direita duas vezes); o nome das teclas e o do Qt."""
        from core.girar import ALCANCES
        from PySide6.QtGui import QActionGroup

        from ui.widgets.barra_girar import nomes_dos_alcances

        # as mesmas palavras da lista "aplicar em" do girar (rodada 12 do
        # layout, 709 B: dizem "folha")
        nomes = nomes_dos_alcances("folha")

        menu = self._menu("Página")
        self._acao(menu, "ir_para_pagina", "Ir para a página...", "Ctrl+G")
        menu.addSeparator()
        self._acao(menu, "girar_esquerda", "Girar ¼ à esquerda", "Ctrl+Left")
        self._acao(menu, "girar", "Girar ¼ à direita", "Ctrl+Right")
        self._acao(menu, "girar_meia_volta", "Girar meia volta")
        alcance = menu.addMenu("Aplicar o giro em")
        self.menus_do_giro = alcance
        grupo = QActionGroup(self)
        grupo.setExclusive(True)
        for chave in ALCANCES:
            item = self._acao(alcance, f"giro_em_{chave}", nomes[chave])
            item.setCheckable(True)
            grupo.addAction(item)
        self.acoes[f"giro_em_{ALCANCES[0]}"].setChecked(True)
        menu.addSeparator()
        # Etapa 2 da obra (Samuel, 07/10/2026): os dois botões, e a Delete
        # deixa em branco (era "Apagar esta página", com a Delete).
        self._acao(menu, "deixar_em_branco", "Deixar esta página em branco", "Del")
        self._acao(menu, "tirar_do_livro", "Tirar esta página do livro", "Shift+Del")
        self._acao(menu, "restaurar", "Trazer de volta a página tirada")

    def _montar_ver(self) -> None:
        menu = self._menu("Ver")
        self._acao(menu, "mais_zoom", "Aproximar", "Ctrl++")
        self._acao(menu, "menos_zoom", "Afastar", "Ctrl+-")
        self._acao(menu, "ajustar", "Ajustar à tela", "Ctrl+0")
        menu.addSeparator()
        # rodada 14, 904 A: as peças da tela que se escondem e mostram
        for chave, texto in (("miniaturas", "Miniaturas"), ("icones", "Ícones da direita")):
            item = self._acao(menu, chave, texto)
            item.setCheckable(True)
            item.setChecked(True)
        self._acao(menu, "todas_as_paginas", "Todas as páginas")
        self._acao(menu, "filtros_tela_cheia", "Filtros em tela cheia")
        menu.addSeparator()
        item = self._acao(menu, "comparar", "Modo comparar")
        item.setCheckable(True)
        # Etapa 2 da obra: o jeito do lado direito (R7 203 D + R14 902 C).
        # Os nomes são os da rodada 14 (sugestão do agente, aceitos com a 902).
        # Só os dois que o Samuel pediu: os ícones na borda (de fábrica) e a
        # área de trabalho 1; "abas no alto" e "painel solto" não entram (não
        # foram pedidos e não existem no programa).
        from PySide6.QtGui import QActionGroup as _Grupo

        from ui.widgets.paineis import JEITOS_DO_LADO_DIREITO, NOMES_DOS_JEITOS
        lado = menu.addMenu("Lado direito")
        self.menu_do_lado_direito = lado
        self.grupo_do_lado_direito = _Grupo(self.janela)
        self.grupo_do_lado_direito.setExclusive(True)
        for jeito in JEITOS_DO_LADO_DIREITO:
            item = self._acao(lado, f"lado_{jeito}", NOMES_DOS_JEITOS[jeito])
            item.setCheckable(True)
            self.grupo_do_lado_direito.addAction(item)
        # Etapa 1 do layout (temas, rodada 7: os três ficam, cinza de
        # fábrica). Lugar provisório: onde a troca de tema mora ainda não foi
        # decidido (pode ir para as Configurações).
        from PySide6.QtGui import QActionGroup

        from ui.estilo import NOMES_DOS_TEMAS, TEMAS
        menu.addSeparator()
        submenu = menu.addMenu("Tema")
        self.grupo_de_temas = QActionGroup(self.janela)
        self.grupo_de_temas.setExclusive(True)
        for nome in TEMAS:
            item = self._acao(submenu, f"tema_{nome}", NOMES_DOS_TEMAS[nome])
            item.setCheckable(True)
            self.grupo_de_temas.addAction(item)

    # Os painéis do menu "Painéis" (rodada 14, 903 B): a chave da ação e a
    # chave do painel (ui/widgets/paineis.py), na ordem do desenho.
    PAINEIS_DO_MENU = (("painel_props", "props", "Propriedades"),
                       ("painel_filtro", "filtro", "Filtro da página"),
                       ("painel_revisar", "revisar", "Para revisar"),
                       ("painel_automatico", "automatico", "Automático"),
                       ("painel_historico", "historico", "Histórico"))

    def _montar_paineis(self) -> None:
        """Menu Painéis (rodada 14 do layout, 903 B): os cinco painéis da
        direita (marcado o aberto; abre um por vez), "Fechar o painel" e o
        "Ícones da direita" (a mesma ação do menu Ver)."""
        menu = self._menu("Painéis")
        for chave, _painel, texto in self.PAINEIS_DO_MENU:
            item = self._acao(menu, chave, texto)
            item.setCheckable(True)
        menu.addSeparator()
        self._acao(menu, "painel_fechar", "Fechar o painel")
        menu.addAction(self.acoes["icones"])

    def marcar_painel(self, aberto: str | None) -> None:
        """Deixa marcado, no menu Painéis, só o painel que está aberto."""
        for chave, painel, _texto in self.PAINEIS_DO_MENU:
            item = self.acoes[chave]
            item.blockSignals(True)
            item.setChecked(painel == aberto)
            item.blockSignals(False)

    def marcar_lado_direito(self, jeito: str) -> None:
        """Deixa marcado, no menu Ver > Lado direito, o jeito que vale."""
        item = self.acoes.get(f"lado_{jeito}")
        if item is not None:
            item.blockSignals(True)
            item.setChecked(True)
            item.blockSignals(False)

    def marcar_tema(self, nome: str) -> None:
        """Deixa marcado, no menu Ver > Tema, o tema que está valendo."""
        item = self.acoes.get(f"tema_{nome}")
        if item is not None:
            item.setChecked(True)

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
        for chave in ("pasta_de_saida", "nome_do_arquivo", "processar", "voltar", "automatico"):
            self.acoes[chave].setEnabled(False)

    def mostrar_tela_de_trabalho(self) -> None:
        """Reacende todos os menus, ao entrar na tela de trabalho."""
        for menu in self.menus.values():
            menu.menuAction().setEnabled(True)
        for chave in ("pasta_de_saida", "nome_do_arquivo", "processar", "voltar", "automatico"):
            self.acoes[chave].setEnabled(True)

    def mostrar_tela_das_opcoes(self) -> None:
        """A tela "O que fazer" de um livro aberto (lista única 1.12, etapa 2
        da obra): todos os menus acesos, como na tela de trabalho, menos
        "Confirmar e processar" (o livro ainda não passou pela conferência
        com as opções desta tela) e "Voltar para as opções" (já está nelas).
        O que mexe no trabalho passa pela janela (_no_trabalho)."""
        self.mostrar_tela_de_trabalho()
        for chave in ("processar", "voltar"):
            self.acoes[chave].setEnabled(False)

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
                f"    {a.text().replace('&', '').replace(chr(9), '  —  ')}"
                f"{'  —  ' + a.shortcut().toString() if not a.shortcut().isEmpty() else ''}"
                for a in menu.actions()
                if not a.isSeparator() and not a.menu()
            ]
            if do_menu:
                linhas.append(titulo)
                linhas.extend(do_menu)
                linhas.append("")
        return "\n".join(linhas).strip()
