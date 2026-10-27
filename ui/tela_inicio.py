"""TELA 1 - Inicio: os livros em cartões, e o livro aberto na tela inteira.

ETAPA 7 DO LAYOUT (21/10/2026). O que o Samuel decidiu (rodadas 4 a 6 e a página de escolhas de
06/10; prints `layout\\imagens\\12-rodada6-proposta-1-livros.png`, `-livro-aberto.png`, `-vazia.png`):

  A TELA DOS LIVROS: "Seus livros", a busca, "Configurações" e "Ajuda" no alto, SEM barra de menus
  (a janela esconde a linha dos menus nesta tela). Os cartões no tamanho, nas cores e com as
  informações da tela 1 (capa, nome, páginas e data, andamento); o primeiro lugar da grade é o
  cartão "+ Abrir um PDF novo" ("Como abrir um livro novo?": "Cartão '+' no começo da grade"); dá
  para arrastar o PDF em qualquer lugar da tela. Sem livro nenhum, a página vazia da tela 6 (o "+"
  grande e a explicação). Um clique no cartão abre o livro na tela inteira; duplo clique, ou o
  botão do cartão, continua direto.

  O LIVRO ABERTO, NA TELA INTEIRA (rodada 5: "queria que ele tomasse toda a tela e não ficasse com
  os outros livros do lado"): linha 1, "Voltar para os livros" (Esc), o nome, páginas e data, o
  andamento e "Mais..."; linha 2, Continuar, Rodar o automático..., Ver todas as páginas,
  Confirmar e processar... e, à direita, "Onde está". Embaixo, as páginas rolando com a coluna de
  miniaturas ("Sim, fica assim") e a pílula "página N de M · ir para".
  A BARRA DE BAIXO, COMO NO UPDF (conferência de 22/10/2026, quadro "O livro aberto na tela
  inteira", "Está pior": "Eu não consigo ver a página direito, e elas estão de maneira muito ruim,
  da uma na internet como o updf faz. Tem uma pagina maior que outra ali"): os jeitos de MOSTRAR
  ("Uma página" de fábrica, "Duas lado a lado", que é o "Ver lado a lado" de antes, e "Rolar sem
  parar", ligado de fábrica) e de CABER ("Caber a página" de fábrica, "Caber a altura", "Caber a
  largura", "Tamanho real"). A escolha fica em configuracoes.json ("livro_aberto") e vale para o
  próximo livro. As páginas de um par ficam sempre da mesma altura (ui/widgets/paginas_rolando.py).

O QUE CADA BOTÃO DO LIVRO ABERTO FAZ HOJE (sem inventar caminho novo):
  Continuar               o "continuar" do cartão (confere se o livro é o mesmo, abre o trabalho).
  Rodar o automático...   abre o livro na área de trabalho e a janela grande do Automático
                          (obra de 26/10/2026, etapa 3: a tela "O que fazer" saiu do caminho).
  Ver todas as páginas    a grade das folhas do PDF (ui/widgets/todas_as_paginas.py); clicar numa
                          folha leva a ela no folhear.
  Confirmar e processar   continua o trabalho e, quando ele abre, pede a confirmação de sempre.
  "Para revisar" e "Receita usada" (desenho da rodada 6, "Sim, fica assim"): desde a etapa 3 da
  obra o resumo do livro guarda quantas páginas pedem um olhar e a última receita do Automático
  (projetos.Resumo.para_revisar, receita_usada), e o livro aberto mostra os dois.

A miniatura da primeira pagina e o que distingue livros de nome igual. Nada de botao apagado sem
explicacao: quando o PDF sai do lugar, o cartao fica laranja e diz o que houve.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import historico
import projetos
from ui import perguntas
from ui import estilo
from ui.widgets.area_arrastar import AreaArrastar

# O cartão do desenho da rodada 6 (seis por linha em 1280 x 657). Antes: 304 x 220.
LARGURA_DO_CARTAO = 196
ALTURA_DO_CARTAO = 244
ALTURA_DA_CAPA = 150
ESPACO_ENTRE_CARTOES = 14

BOTAO_DO_CARTAO = """
QPushButton {{
    background: {fundo}; color: {cor}; border: {borda};
    border-radius: 5px; font-size: 12px; padding: 3px 10px;
}}
QPushButton:hover {{ background: {aceso}; }}
"""


def _botao_pequeno(texto: str, desenho: str, dica: str) -> QPushButton:
    """Botão leve do alto da tela ("Configurações", "Ajuda"), com o desenhinho ao lado."""
    botao = _BotaoComDesenho(texto, desenho)
    botao.setToolTip(dica)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setFocusPolicy(Qt.NoFocus)
    estilo.estilizar(botao, lambda: (
        f"QPushButton {{ background: transparent; border: none; color: {estilo.cor('texto')};"
        " padding: 4px 8px 4px 26px; font-size: 13px; }"
        f"QPushButton:hover {{ background: {estilo.cor('botao_h')}; border-radius: 5px; }}"))
    return botao


class _BotaoComDesenho(QPushButton):
    """Um botão com um desenho à esquerda do texto (engrenagem, ponto de interrogação, seta)."""

    def __init__(self, texto: str, desenho: str) -> None:
        super().__init__(texto)
        self.desenho = desenho

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().paintEvent(evento)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(QPen(QColor(estilo.cor("texto")), 1.4))
        cx, cy = 14, self.height() / 2
        if self.desenho == "engrenagem":
            pintor.drawEllipse(QPoint(int(cx), int(cy)), 3, 3)
            for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0), (4, 4), (-4, -4), (4, -4), (-4, 4)):
                pintor.drawLine(int(cx + dx * 0.7), int(cy + dy * 0.7), int(cx + dx), int(cy + dy))
        elif self.desenho == "ajuda":
            pintor.drawEllipse(QPoint(int(cx), int(cy)), 6, 6)
            pintor.drawText(int(cx - 3), int(cy - 6), 7, 12, Qt.AlignCenter, "?")
        elif self.desenho == "voltar":
            pintor.drawLine(int(cx - 6), int(cy), int(cx + 6), int(cy))
            pintor.drawLine(int(cx - 6), int(cy), int(cx - 2), int(cy - 4))
            pintor.drawLine(int(cx - 6), int(cy), int(cx - 2), int(cy + 4))
        pintor.end()


class TelaInicio(QWidget):
    abrir_pdf = Signal(str)
    continuar_projeto = Signal(object)      # projetos.Resumo
    recomecar_projeto = Signal(object)      # projetos.Resumo
    # Emitido depois do "Tirar da lista" confirmado e ANTES de apagar a pasta
    # (pedir_para_remover): a janela solta o livro, se for o aberto, para
    # nada mais grava-lo (R-B do verificador-3, 06/10/2026). Ligacao direta
    # (mesmo fio): quando o emit volta, a janela ja soltou.
    vai_tirar_da_lista = Signal(object)     # projetos.Resumo
    # Etapa 7 do layout: os botões do livro aberto e do alto da tela
    abrir_o_automatico = Signal(object)     # projetos.Resumo: o livro com o Automático aberto (etapa 3)
    processar_pedido = Signal(object)       # projetos.Resumo: continuar e confirmar
    configuracoes_pedidas = Signal()
    ajuda_pedida = Signal()

    # Mantido por compatibilidade com a janela, que ainda escuta o nome antigo.
    reabrir_projeto = Signal(object)

    def __init__(self, parent=None) -> None:
        """A pilha com as duas telas: os livros e o livro aberto. Preenche os
        cartões com o que já existe em disco (recarregar)."""
        super().__init__(parent)
        self._resumos: list[projetos.Resumo] = []
        self.ultimo_aberto: str = ""            # a pasta do último livro aberto (fica marcado)
        self.setAcceptDrops(True)

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        self.pilha = QStackedWidget()
        fora.addWidget(self.pilha)

        # --- a tela dos livros
        livros = QWidget()
        camadas = QVBoxLayout(livros)
        camadas.setContentsMargins(20, 14, 20, 14)
        camadas.setSpacing(12)
        alto = QHBoxLayout()
        alto.setSpacing(8)
        titulo = QLabel("Seus livros")
        titulo.setObjectName("tituloDosLivros")
        estilo.estilizar(titulo, lambda: f"color: {estilo.cor('forte')}; font-size: 18px; font-weight: 600;")
        alto.addWidget(titulo)
        self.contagem = QLabel("")
        estilo.estilizar(self.contagem, lambda: f"color: {estilo.cor('fraco')}; font-size: 13px;")
        alto.addWidget(self.contagem, 0, Qt.AlignBottom)
        alto.addStretch()
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("procurar pelo nome")
        self.busca.setFixedWidth(220)
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self._remontar)
        alto.addWidget(self.busca)
        alto.addSpacing(10)
        self.botao_configuracoes = _botao_pequeno("Configurações", "engrenagem",
                                                  "Tema, atalhos de teclado e outras escolhas")
        self.botao_configuracoes.clicked.connect(lambda: self.configuracoes_pedidas.emit())
        alto.addWidget(self.botao_configuracoes)
        self.botao_ajuda = _botao_pequeno("Ajuda", "ajuda", "A lista de atalhos de teclado (F1)")
        self.botao_ajuda.clicked.connect(lambda: self.ajuda_pedida.emit())
        alto.addWidget(self.botao_ajuda)
        camadas.addLayout(alto)

        # o cartão "+": a mesma AreaArrastar de antes (clique procura o PDF,
        # arrastar solta nele), agora no desenho de cartão
        self.area = AreaArrastar(cartao=True)
        self.area.setFixedSize(LARGURA_DO_CARTAO, ALTURA_DO_CARTAO)
        self.area.arquivo_escolhido.connect(self.abrir_pdf.emit)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        # Nunca rola de lado: os cartoes quebram linha sozinhos.
        self.rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        interno = QWidget()
        self.grade = QGridLayout(interno)
        self.grade.setContentsMargins(0, 0, 8, 0)
        self.grade.setSpacing(ESPACO_ENTRE_CARTOES)
        self.grade.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.rolagem.setWidget(interno)
        camadas.addWidget(self.rolagem, 1)
        self.pilha.addWidget(livros)

        # --- o livro aberto
        self.livro_aberto = LivroAberto(self)
        self.pilha.addWidget(self.livro_aberto)

        self.recarregar()

    # --- montagem ---------------------------------------------------------

    def recarregar(self) -> None:
        """Le os resumos do disco. Nao abre o historico de projeto nenhum.

        E o que mantem a tela rapida com cinquenta projetos e um livro de mil
        paginas na lista: cada cartao sai de um arquivo pequeno.
        """
        self._resumos = projetos.listar()
        self._remontar()

    def _remontar(self) -> None:
        """Refaz a grade: o cartão "+" primeiro e os cartões dos livros
        (filtrados pela busca), quantos couberem por linha. Sem livro nenhum,
        a página vazia (o "+" grande e a explicação)."""
        while self.grade.count():
            item = self.grade.takeAt(0)
            velho = item.widget()
            if velho is not None and velho is not self.area:
                # setParent(None) ANTES do deleteLater: so tirar do layout nao
                # tira da tela (aparecia um cartao fantasma).
                velho.setParent(None)
                velho.deleteLater()
        quantos = len(self._resumos)
        self.contagem.setText(f"{quantos} livro" + ("s" if quantos != 1 else "") if quantos else "")

        procurado = self.busca.text().strip().lower()
        mostrar = [r for r in self._resumos
                   if not procurado or procurado in r.nome.lower()]

        if not self._resumos:
            # a página vazia da tela 6: o "+" grande à esquerda, a explicação ao lado
            self.area.setFixedSize(530, 364)
            self.area.grande = True
            self.grade.addWidget(self.area, 0, 0)
            self.grade.addWidget(self._recado(""), 0, 1, Qt.AlignVCenter)
            return
        self.area.grande = False
        self.area.setFixedSize(LARGURA_DO_CARTAO, ALTURA_DO_CARTAO)
        largura = self.rolagem.viewport().width() + ESPACO_ENTRE_CARTOES
        por_linha = max(1, largura // (LARGURA_DO_CARTAO + ESPACO_ENTRE_CARTOES))
        self.grade.addWidget(self.area, 0, 0)
        if not mostrar:
            self.grade.addWidget(self._recado(procurado), 0, 1, 1, max(1, por_linha - 1))
            return
        for posicao, resumo in enumerate(mostrar, start=1):
            cartao = CartaoDeProjeto(resumo, self)
            cartao.definir_marcado(resumo.pasta == self.ultimo_aberto)
            self.grade.addWidget(cartao, posicao // por_linha, posicao % por_linha)

    def _recado(self, procurado: str) -> QLabel:
        """Texto para quando nao ha cartao a mostrar: muda conforme ha busca ou não."""
        texto = (f'Nenhum projeto com "{procurado}" no nome.' if procurado
                 else "<b style='font-size:16px'>Ainda não há nenhum livro aqui</b><br><br>"
                      "Cada livro que você abrir vira um cartão nesta tela.<br>"
                      "Um clique no cartão abre o livro na tela inteira, com as opções e as "
                      "páginas para folhear.<br><br>Para começar, clique no + ou arraste o PDF "
                      "de um livro para cá.")
        recado = QLabel(texto)
        recado.setWordWrap(True)
        estilo.estilizar(recado, lambda: f"color: {estilo.TEXTO_FRACO}; padding: 14px 24px;")
        return recado

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """A grade se refaz quando a janela muda de largura."""
        super().resizeEvent(evento)
        self._remontar()

    # --- arrastar em qualquer lugar ------------------------------------------

    def dragEnterEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if self.pilha.currentIndex() == 0 and AreaArrastar._pdf_de(evento):
            evento.acceptProposedAction()

    def dropEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        caminho = AreaArrastar._pdf_de(evento)
        if caminho and self.pilha.currentIndex() == 0:
            self.abrir_pdf.emit(caminho)

    # --- o livro aberto -------------------------------------------------------

    def abrir_o_livro(self, resumo: projetos.Resumo) -> None:
        """Um clique no cartão: o livro na tela inteira (rodada 6)."""
        self.ultimo_aberto = resumo.pasta
        self.livro_aberto.mostrar(resumo)
        self.pilha.setCurrentWidget(self.livro_aberto)

    def voltar_para_os_livros(self) -> None:
        """"Voltar para os livros" ou Esc: os cartões voltam, com o último marcado."""
        self.livro_aberto.fechar()
        self.pilha.setCurrentIndex(0)
        self._remontar()

    def mostrar_os_livros(self) -> None:
        """A janela trocou de tela: o livro aberto fecha (para de ler o PDF)
        e esta tela volta a começar pelos livros."""
        if self.pilha.currentIndex() != 0:
            self.voltar_para_os_livros()

    # --- acoes dos cartoes ------------------------------------------------

    def pedir_o_automatico(self, resumo: projetos.Resumo) -> None:
        """"Rodar o automático..." do livro aberto: o livro abre na área de
        trabalho com a janela grande do Automático (etapa 3 da obra), depois da
        mesma conferência do "continuar" (o PDF existe e é o mesmo livro)."""
        self.pedir_para_continuar(resumo, sinal=self.abrir_o_automatico)

    def pedir_para_processar(self, resumo: projetos.Resumo) -> None:
        """"Confirmar e processar..." do livro aberto: continua o trabalho e a
        janela pede a confirmação de sempre quando ele abrir."""
        self.pedir_para_continuar(resumo, sinal=self.processar_pedido)

    def pedir_para_continuar(self, resumo: projetos.Resumo, sinal=None) -> None:
        """Reabre o projeto - mas so depois de conferir que o PDF de entrada
        ainda existe e e o MESMO livro (nao um arquivo trocado no mesmo lugar).
        Aplicar ajustes salvos num livro diferente estragaria as páginas."""
        situacao, caminho = projetos.procurar_o_livro(resumo)

        if situacao == projetos.TROCADO:
            perguntas.avisar(
                self, "Este não é o mesmo livro",
                f"Existe um arquivo chamado {Path(caminho).name} nesse lugar, "
                "mas ele não é o livro deste projeto - alguém o substituiu.\n\n"
                "Não vou aplicar os ajustes deste projeto num livro diferente: "
                "isso estragaria o trabalho sem aparecer.\n\n"
                'Use "procurar de novo" e aponte onde está o livro certo.')
            return

        if situacao == projetos.SUMIU:
            self.procurar_o_livro_a_mao(resumo)
            return

        if situacao == projetos.RELIGADO:
            resumo.caminho_entrada = caminho
            projetos.gravar_resumo(resumo)

        (sinal or self.continuar_projeto).emit(resumo)

    def procurar_o_livro_a_mao(self, resumo: projetos.Resumo) -> None:
        """Pede pra pessoa apontar onde o PDF foi parar, e confere a assinatura
        antes de aceitar - mesma cautela de pedir_para_continuar."""
        # Obra 26/10 (etapa 9a): janela do Windows em portugues, caminho
        # conferido na volta (ui/dialogos_de_arquivo.py).
        from ui.dialogos_de_arquivo import escolher_pdf_para_abrir

        caminho = escolher_pdf_para_abrir(self, f"Onde está o livro de {resumo.nome}?")
        if not caminho:
            return

        if resumo.assinatura and projetos.assinatura_do_arquivo(caminho) != resumo.assinatura:
            perguntas.avisar(
                self, "Este não é o mesmo livro",
                "Esse arquivo não é o livro deste projeto. Os ajustes salvos "
                "aqui foram feitos em outro livro, e aplicá-los neste "
                "estragaria as páginas.")
            return

        resumo.caminho_entrada = caminho
        projetos.gravar_resumo(resumo)
        self.recarregar()
        self.continuar_projeto.emit(resumo)

    def pedir_para_recomecar(self, resumo: projetos.Resumo) -> None:
        """Confirma antes de jogar fora a conferência ja feita (o livro em si
        nunca e tocado - só o projeto salvo)."""
        # Botoes em portugues, com o "nao" no Enter (ui.perguntas; antes
        # saiam "Yes"/"No", print s25 do verificador, 30/09).
        if perguntas.perguntar(
                self, "Começar de novo?",
                f"Isto joga fora todos os ajustes de {resumo.nome} e abre o livro "
                "limpo.\n\nO livro em si não é tocado. O que se perde é a "
                "conferência já feita.",
                sim="Começar de novo", nao="Não, deixar"):
            self.recomecar_projeto.emit(resumo)

    def pedir_para_renomear(self, resumo: projetos.Resumo) -> None:
        """Renomeia so o projeto (para diferenciar livros de nome igual), nao o arquivo em disco."""
        novo, certo = perguntas.pedir_texto(
            self, "Renomear", "Nome deste projeto:", resumo.nome)
        if certo and novo.strip():
            projetos.renomear(resumo, novo)
            self.recarregar()

    def pedir_para_remover(self, resumo: projetos.Resumo) -> None:
        """Tira o projeto da lista (nao apaga o PDF, que nunca esteve guardado aqui).

        As copias de seguranca do trabalho (projeto.antigo-*) nao sao
        apagadas: vao para a pasta copias-de-seguranca, e a pergunta diz
        isso (decisao do Samuel, 29/09; projetos.remover_da_lista). Botoes
        em portugues, com o "nao" no Enter (ui.perguntas).

        Antes de apagar, avisa a janela (vai_tirar_da_lista): se o livro
        tirado e o que esta aberto, ela o solta e para a conversao das zonas
        dele, sem gravar. Sem isso, fechar o programa, o relogio de salvar ou
        o fim da conversao gravavam o livro de novo, a pasta voltava e o
        cartao tambem (R-B do verificador-3, 06/10/2026). Arriscado: emitir
        depois do remover_da_lista (uma gravacao poderia chegar no meio).
        """
        texto = (f"{resumo.nome} sai desta tela e a conferência feita nele se "
                 "perde.\n\nO livro em PDF continua onde está - ele nunca esteve "
                 "guardado aqui dentro.")
        quantas = len([c for c in projetos.copias_do_trabalho(resumo)
                       if c.name.startswith("projeto.")])
        if quantas:
            texto += (f"\n\nAs cópias de segurança do trabalho deste livro ({quantas}) "
                      "não são apagadas: ficam guardadas na pasta "
                      f"{projetos.pasta_das_copias_guardadas()}.")
        if perguntas.perguntar(self, "Tirar da lista?", texto,
                               sim="Tirar da lista", nao="Não, deixar"):
            self.vai_tirar_da_lista.emit(resumo)
            projetos.remover_da_lista(resumo)
            self.recarregar()


class CartaoDeProjeto(QFrame):
    """Um livro na tela dos livros: capa (com o botão por cima, no canto),
    nome, páginas e data, andamento. Um clique abre o livro na tela inteira;
    duplo clique ou o botão continua direto."""

    def __init__(self, resumo: projetos.Resumo, tela: TelaInicio) -> None:
        super().__init__()
        self.resumo = resumo
        self.tela = tela
        self.marcado = False
        self.setObjectName("cartao")
        self.setFixedSize(LARGURA_DO_CARTAO, ALTURA_DO_CARTAO)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Um clique abre o livro; duplo clique continua o trabalho")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._abrir_menu)

        situacao, _caminho = projetos.procurar_o_livro(resumo)
        self.perdido = situacao in (projetos.SUMIU, projetos.TROCADO)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(1, 1, 1, 1)
        camadas.setSpacing(0)
        camadas.addWidget(self._montar_capa())

        corpo = QVBoxLayout()
        corpo.setContentsMargins(12, 9, 12, 9)
        corpo.setSpacing(4)
        # O nome e cortado com reticencias em vez de vazar do cartao. O nome
        # inteiro fica na dica do mouse, junto com o caminho do livro.
        self.rotulo_nome = QLabel()
        self.rotulo_nome.setStyleSheet("font-size: 14px; font-weight: 600; background: transparent;")
        self.rotulo_nome.setToolTip(f"{resumo.nome}\n{resumo.caminho_entrada}")
        corpo.addWidget(self.rotulo_nome)
        detalhe = QLabel(f"{resumo.total_paginas} páginas · {resumo.data_amigavel}")
        estilo.estilizar(detalhe, lambda: (
            f"color: {estilo.TEXTO_FRACO}; font-size: 12px; background: transparent;"))
        corpo.addWidget(detalhe)
        if self.perdido:
            corpo.addWidget(self._montar_aviso_de_perdido())
        else:
            corpo.addWidget(self._montar_progresso())
            frase = QLabel(resumo.frase_do_progresso)
            gerado = resumo.pdf_gerado
            estilo.estilizar(frase, lambda: (
                f"color: {estilo.cor('ok') if gerado else (estilo.cor('link') if resumo.conferidas else estilo.cor('fraco'))}; "
                "font-size: 12px; background: transparent;"))
            corpo.addWidget(frase)
        corpo.addStretch()
        camadas.addLayout(corpo)
        self._aplicar_cor()

    # --- pedacos ----------------------------------------------------------

    def _montar_capa(self) -> QWidget:
        """A miniatura da primeira página (o que distingue livros de nome
        igual), com o botão do cartão no canto de baixo, por cima."""
        capa = QLabel()
        capa.setFixedHeight(ALTURA_DA_CAPA)
        capa.setAlignment(Qt.AlignCenter)
        perdido = self.perdido
        estilo.estilizar(capa, lambda: (
            f"background: {estilo.cor('aviso_f') if perdido else estilo.cor('fora')};"
            f" color: {estilo.TEXTO_FRACO}; border-top-left-radius: 9px; border-top-right-radius: 9px;"))
        caminho = projetos.garantir_miniatura(self.resumo)
        imagem = QPixmap(caminho) if caminho else QPixmap()
        if imagem.isNull():
            capa.setText("sem capa")
        else:
            razao = capa.devicePixelRatioF()       # nos pixels de verdade (escala do Windows)
            reduzida = imagem.scaled(
                QSize(round((LARGURA_DO_CARTAO - 40) * razao), round((ALTURA_DA_CAPA - 8) * razao)),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            reduzida.setDevicePixelRatio(razao)
            capa.setPixmap(reduzida)
        botao = self._botao_do_cartao()
        botao.setParent(capa)
        botao.adjustSize()
        botao.move(LARGURA_DO_CARTAO - botao.width() - 10, ALTURA_DA_CAPA - botao.height() - 8)
        return capa

    def _botao_do_cartao(self) -> QPushButton:
        """continuar (azul) · abrir a pasta (pronto) · procurar de novo (laranja, livro perdido)."""
        if self.perdido:
            botao = QPushButton("procurar de novo")
            estilo.estilizar(botao, lambda: BOTAO_DO_CARTAO.format(
                fundo=estilo.cor("aviso_f"), cor=estilo.cor("aviso"),
                borda=f"1px solid {estilo.cor('aviso')}", aceso=estilo.cor("aviso_b")))
            botao.clicked.connect(lambda: self.tela.procurar_o_livro_a_mao(self.resumo))
        elif self.resumo.pdf_gerado:
            botao = QPushButton("abrir a pasta")
            estilo.estilizar(botao, lambda: BOTAO_DO_CARTAO.format(
                fundo=estilo.cor("botao"), cor=estilo.cor("texto"),
                borda=f"1px solid {estilo.cor('sep')}", aceso=estilo.cor("botao_h")))
            botao.clicked.connect(lambda: historico.abrir_pasta(self.resumo.caminho_saida))
        else:
            botao = QPushButton("continuar")
            estilo.estilizar(botao, lambda: BOTAO_DO_CARTAO.format(
                fundo=estilo.cor("azul"), cor="#ffffff", borda="none", aceso=estilo.cor("azul_e")))
            botao.clicked.connect(lambda: self.tela.pedir_para_continuar(self.resumo))
        botao.setCursor(Qt.PointingHandCursor)
        return botao

    def _montar_progresso(self) -> QWidget:
        """Barra fina: verde e 100% se ja gerou PDF, azul com o progresso salvo senão."""
        pronto = self.resumo.pdf_gerado
        barra = QProgressBar()
        barra.setTextVisible(False)
        barra.setFixedHeight(5)
        barra.setRange(0, 100)
        barra.setValue(100 if pronto else int(self.resumo.progresso * 100))
        estilo.estilizar(barra, lambda: (
            f"QProgressBar {{ background: {estilo.cor('sep')}; border: none; border-radius: 2px; }}"
            f"QProgressBar::chunk {{ background: {estilo.cor('ok') if pronto else estilo.cor('azul')};"
            " border-radius: 2px; }"))
        return barra

    def _montar_aviso_de_perdido(self) -> QWidget:
        """Nunca um botao apagado sem explicacao - era a queixa do print."""
        aviso = QLabel("o PDF saiu do lugar")
        aviso.setObjectName("avisoFraco")   # cor do tema (ui/estilo.py)
        return aviso

    def definir_marcado(self, marcado: bool) -> None:
        """O último livro aberto fica com a borda azul ao voltar para os livros."""
        self.marcado = bool(marcado)
        self._aplicar_cor()

    def _aplicar_cor(self) -> None:
        """Laranja quando o PDF esta perdido/trocado; azul no último aberto."""
        perdido, marcado = self.perdido, self.marcado
        estilo.estilizar(self, lambda: (
            f"QFrame#cartao {{ border: {2 if (perdido or marcado) else 1}px solid "
            f"{estilo.cor('aviso') if perdido else (estilo.cor('azul') if marcado else estilo.cor('linha_b'))}; "
            f"background: {estilo.cor('aviso_f') if perdido else estilo.cor('painel')}; border-radius: 10px; }}"
            f"QFrame#cartao:hover {{ border-color: {estilo.cor('azul')}; }}"
            "QLabel { background: transparent; }"))

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        self._encurtar_o_nome()

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().showEvent(evento)
        self._encurtar_o_nome()

    def _encurtar_o_nome(self) -> None:
        """Nome comprido sai com reticencias, em vez de vazar do cartao."""
        from PySide6.QtGui import QFontMetrics

        largura = max(40, self.rotulo_nome.width())
        metrica = QFontMetrics(self.rotulo_nome.font())
        self.rotulo_nome.setText(
            metrica.elidedText(self.resumo.nome, Qt.ElideRight, largura))

    # --- menu do botao direito e cliques ------------------------------------

    def _abrir_menu(self, posicao) -> None:
        """Menu de contexto (botão direito) do cartão, com as mesmas ações do
        livro aberto, mais renomear e remover."""
        menu = _menu_do_livro(self, self.tela, self.resumo, self.perdido)
        menu.exec(self.mapToGlobal(posicao))

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Um clique abre o livro na tela inteira (rodada 6)."""
        if evento.button() == Qt.LeftButton and self.rect().contains(evento.position().toPoint()):
            self.tela.abrir_o_livro(self.resumo)

    def mouseDoubleClickEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Duplo clique no cartão continua o projeto (se o livro nao estiver perdido)."""
        if not self.perdido:
            self.tela.pedir_para_continuar(self.resumo)


def _menu_do_livro(pai, tela: TelaInicio, resumo: projetos.Resumo, perdido: bool) -> QMenu:
    """O menu de um livro: o do botão direito do cartão e o "Mais..." do livro aberto."""
    menu = QMenu(pai)
    if not perdido:
        menu.addAction("continuar", lambda: tela.pedir_para_continuar(resumo))
    else:
        menu.addAction("procurar o livro", lambda: tela.procurar_o_livro_a_mao(resumo))
    menu.addAction("começar de novo", lambda: tela.pedir_para_recomecar(resumo))
    menu.addSeparator()
    menu.addAction("renomear", lambda: tela.pedir_para_renomear(resumo))
    abrir = menu.addAction("abrir a pasta de saída", lambda: historico.abrir_pasta(resumo.caminho_saida))
    abrir.setEnabled(bool(resumo.caminho_saida) and Path(resumo.caminho_saida).exists())
    if not abrir.isEnabled():
        abrir.setToolTip("Este livro ainda não gerou PDF nenhum.")
    menu.addSeparator()
    menu.addAction("remover da lista", lambda: tela.pedir_para_remover(resumo))
    return menu


LARGURA_DA_PILULA_INTEIRA = 1180   # abaixo disto a pílula diz só "301 de 750" (ver _pagina_mudou)


class LivroAberto(QWidget):
    """O livro aberto, na tela inteira (rodada 6, proposta 1; ver o começo do arquivo)."""

    def __init__(self, tela: TelaInicio) -> None:
        super().__init__()
        from ui.widgets.paginas_rolando import PaginasRolando
        from ui.widgets.tira_miniaturas import TiraMiniaturas

        self.tela = tela
        self.resumo: projetos.Resumo | None = None
        self.perdido = False
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)

        alto = QFrame()
        alto.setObjectName("altoDoLivroAberto")
        estilo.estilizar(alto, lambda: (
            f"QFrame#altoDoLivroAberto {{ background: {estilo.cor('bar')};"
            f" border-bottom: 1px solid {estilo.cor('linha')}; }}"))
        caixa = QVBoxLayout(alto)
        caixa.setContentsMargins(20, 12, 20, 10)
        caixa.setSpacing(10)
        linha1 = QHBoxLayout()
        linha1.setSpacing(14)
        self.botao_voltar = _BotaoComDesenho("Voltar para os livros   Esc", "voltar")
        self.botao_voltar.setCursor(Qt.PointingHandCursor)
        self.botao_voltar.setFocusPolicy(Qt.NoFocus)
        self.botao_voltar.setToolTip("Volta para os cartões dos livros (tecla Esc)")
        estilo.estilizar(self.botao_voltar, lambda: (
            f"QPushButton {{ padding: 8px 14px 8px 30px; font-size: 14px; font-weight: 600; }}"))
        self.botao_voltar.clicked.connect(tela.voltar_para_os_livros)
        linha1.addWidget(self.botao_voltar)
        nomes = QVBoxLayout()
        nomes.setSpacing(0)
        self.nome = QLabel("")
        estilo.estilizar(self.nome, lambda: f"color: {estilo.cor('forte')}; font-size: 18px; font-weight: 600;")
        nomes.addWidget(self.nome)
        self.detalhe = QLabel("")
        estilo.estilizar(self.detalhe, lambda: f"color: {estilo.cor('fraco')}; font-size: 12px;")
        nomes.addWidget(self.detalhe)
        linha1.addLayout(nomes, 1)
        self.barra = QProgressBar()
        self.barra.setTextVisible(False)
        self.barra.setFixedSize(160, 5)
        self.barra.setRange(0, 100)
        estilo.estilizar(self.barra, lambda: (
            f"QProgressBar {{ background: {estilo.cor('sep')}; border: none; border-radius: 2px; }}"
            f"QProgressBar::chunk {{ background: {estilo.cor('azul')}; border-radius: 2px; }}"))
        linha1.addWidget(self.barra)
        self.andamento = QLabel("")
        estilo.estilizar(self.andamento, lambda: f"color: {estilo.cor('link')}; font-size: 13px;")
        linha1.addWidget(self.andamento)
        self.botao_mais = QPushButton("Mais...")
        self.botao_mais.setCursor(Qt.PointingHandCursor)
        self.botao_mais.setFocusPolicy(Qt.NoFocus)
        self.botao_mais.clicked.connect(self._abrir_o_mais)
        linha1.addWidget(self.botao_mais)
        caixa.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(8)
        self.botao_continuar = self._botao("Continuar", "Abre o trabalho deste livro onde parou",
                                           lambda: tela.pedir_para_continuar(self.resumo), primario=True)
        self.botao_automatico = self._botao(
            "Rodar o automático...", "Abre o livro e o Automático, para escolher as etapas e rodar",
            lambda: tela.pedir_o_automatico(self.resumo))
        self.botao_todas = self._botao("Ver todas as páginas", "Todas as folhas do livro, em grade",
                                       self._ver_todas)
        self.botao_processar = self._botao(
            "Confirmar e processar...", "Abre o trabalho e pede a confirmação para gerar o PDF",
            lambda: tela.pedir_para_processar(self.resumo))
        for botao in (self.botao_continuar, self.botao_automatico, self.botao_todas, self.botao_processar):
            linha2.addWidget(botao)
        linha2.addStretch()
        # etapa 3 da obra (R6): "Para revisar" e "Receita usada"
        self.para_revisar = QLabel("")
        self.receita_usada = QLabel("")
        for rotulo in (self.para_revisar, self.receita_usada):
            estilo.estilizar(rotulo, lambda: f"color: {estilo.cor('fraco')}; font-size: 12px;")
            linha2.addWidget(rotulo)
            linha2.addSpacing(10)
        # D-521 (27/10/2026, Central `pd-avisos-do-livro`: "No alto do painel
        # \"Para revisar\" e no livro aberto da tela inicial (recomendo)"): os
        # avisos que valem para o livro inteiro, numa linha (escondida sem
        # aviso). O mesmo texto do painel (paineis.frase_dos_avisos_do_livro).
        self.avisos_do_livro = QLabel("")
        self.avisos_do_livro.setWordWrap(True)
        self.avisos_do_livro.setVisible(False)
        estilo.estilizar(self.avisos_do_livro, lambda: f"color: {estilo.cor('aviso')}; font-size: 12px;")
        self.onde_esta = QLabel("")
        self.onde_esta.setTextFormat(Qt.RichText)
        estilo.estilizar(self.onde_esta, lambda: f"color: {estilo.cor('fraco')}; font-size: 12px;")
        linha2.addWidget(self.onde_esta)
        caixa.addLayout(linha2)
        caixa.addWidget(self.avisos_do_livro)
        fora.addWidget(alto)

        meio = QHBoxLayout()
        meio.setContentsMargins(0, 0, 0, 0)
        meio.setSpacing(0)
        self.miniaturas = TiraMiniaturas("Páginas")
        self.miniaturas.definir_arranjo(True, False)
        self.miniaturas.setFixedWidth(100)
        self.miniaturas.selecionada.connect(self.ir_para)
        meio.addWidget(self.miniaturas)
        self.pilha_do_meio = QStackedWidget()
        self.paginas = PaginasRolando()
        self.paginas.pagina_mudou.connect(self._pagina_mudou)
        self.pilha_do_meio.addWidget(self.paginas)
        from ui.widgets.todas_as_paginas import TodasAsPaginas
        self.todas = TodasAsPaginas()
        self.todas.ir_para.connect(self._voltar_da_grade)
        self.todas.voltar.connect(lambda: self._voltar_da_grade(None))
        self.todas.botao_voltar.setText("voltar ao livro")
        self.pilha_do_meio.addWidget(self.todas)
        self.perdido_aviso = QLabel("")
        self.perdido_aviso.setAlignment(Qt.AlignCenter)
        self.perdido_aviso.setWordWrap(True)
        self.pilha_do_meio.addWidget(self.perdido_aviso)
        meio.addWidget(self.pilha_do_meio, 1)
        fora.addLayout(meio, 1)

        # a pílula "página N de M · ir para": na barra de baixo, à direita, como o número
        # da página no UPDF (22/10/2026; antes ficava por cima das páginas e cobria o canto
        # da folha da direita)
        self.pilula = QFrame()
        self.pilula.setObjectName("pilulaDoLivro")
        estilo.estilizar(self.pilula, lambda: (
            f"QFrame#pilulaDoLivro {{ background: {estilo.cor('cabeca')}; border: 1px solid "
            f"{estilo.cor('sep')}; border-radius: 18px; }} QLabel {{ background: transparent; }}"))
        pl = QHBoxLayout(self.pilula)
        pl.setContentsMargins(12, 1, 4, 1)
        pl.setSpacing(8)
        self.rotulo_pagina = QLabel("")
        pl.addWidget(self.rotulo_pagina)
        self.rotulo_ir = QLabel("ir para")
        estilo.estilizar(self.rotulo_ir, lambda: f"color: {estilo.cor('fraco')}; font-size: 12px;")
        pl.addWidget(self.rotulo_ir)
        self.campo_ir = QSpinBox()
        self.campo_ir.setButtonSymbols(QSpinBox.NoButtons)
        self.campo_ir.setFixedWidth(64)          # "1000" cabe inteiro a 125% (com 52 o "304" cortava)
        self.campo_ir.editingFinished.connect(lambda: self.ir_para(self.campo_ir.value() - 1))
        pl.addWidget(self.campo_ir)
        for texto, passo, dica in (("‹", -1, "folha anterior"), ("›", 1, "próxima folha")):
            botao = QPushButton(texto)
            botao.setFixedSize(32, 28)
            botao.setStyleSheet("padding: 0px; font-size: 16px;")
            botao.setToolTip(dica)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            botao.clicked.connect(lambda _c=False, p=passo: self.ir_para(self.paginas.passo(p)))
            pl.addWidget(botao)

        # a barra de baixo: os jeitos de mostrar e de caber, como no UPDF (22/10/2026)
        fora.addWidget(self._montar_barra_de_baixo())

    # --- a barra de baixo (como no UPDF, 22/10/2026) ------------------------------

    # (jeito, texto do botão, balão do mouse)
    JEITOS_DE_MOSTRAR = (
        ("uma", "Uma página", "Uma página de cada vez"),
        ("duas", "Duas lado a lado", "As páginas em pares, como no livro aberto (a 1 sozinha, à direita)"),
    )
    JEITOS_DE_CABER = (
        ("pagina", "Caber a página", "A página inteira (ou o par) cabe na tela"),
        ("altura", "Caber a altura", "A página ocupa a altura toda da tela"),
        ("largura", "Caber a largura", "A página ocupa a largura toda da tela (rola para ver o resto)"),
        ("real", "Tamanho real", "A página no tamanho dela, a 100%"),
    )
    DE_FABRICA = {"mostrar": "uma", "rolar": True, "caber": "pagina"}

    def _montar_barra_de_baixo(self) -> QFrame:
        """A barra de baixo: "Uma página" / "Duas lado a lado", "Rolar sem
        parar" e os quatro jeitos de caber. Cada grupo é de escolha única."""
        from PySide6.QtWidgets import QButtonGroup

        barra = QFrame()
        barra.setObjectName("baixoDoLivroAberto")
        estilo.estilizar(barra, lambda: (
            f"QFrame#baixoDoLivroAberto {{ background: {estilo.cor('bar')};"
            f" border-top: 1px solid {estilo.cor('linha')}; }}"
            f"QPushButton#jeitoDoLivro {{ padding: 4px 8px; font-size: 12px; }}"
            f"QPushButton#jeitoDoLivro:checked {{ background: {estilo.cor('sel')};"
            f" border: 1px solid {estilo.cor('azul')}; color: {estilo.cor('forte')}; }}"
            f"QLabel#separadorDoLivro {{ background: {estilo.cor('sep')}; }}"))
        linha = QHBoxLayout(barra)
        linha.setContentsMargins(12, 5, 12, 5)
        linha.setSpacing(4)
        linha.addStretch()
        self.botoes_mostrar: dict[str, QPushButton] = {}
        self.botoes_caber: dict[str, QPushButton] = {}
        self._grupos = []
        for jeitos, botoes, acao in ((self.JEITOS_DE_MOSTRAR, self.botoes_mostrar, self._escolher_mostrar),
                                     (self.JEITOS_DE_CABER, self.botoes_caber, self._escolher_caber)):
            grupo = QButtonGroup(barra)
            grupo.setExclusive(True)
            self._grupos.append(grupo)
            for jeito, texto, dica in jeitos:
                botao = self._botao_de_jeito(texto, dica)
                botao.clicked.connect(lambda _c=False, j=jeito, a=acao: a(j))
                grupo.addButton(botao)
                botoes[jeito] = botao
                linha.addWidget(botao)
            if botoes is self.botoes_mostrar:
                self.botao_rolar = self._botao_de_jeito(
                    "Rolar sem parar", "Ligado: as páginas rolam uma atrás da outra.\n"
                    "Desligado: uma página (ou um par) de cada vez; a roda do mouse passa para a próxima.")
                self.botao_rolar.clicked.connect(lambda ligado: self._escolher_rolar(ligado))
                linha.addSpacing(4)
                linha.addWidget(self.botao_rolar)
                separador = QLabel()
                separador.setObjectName("separadorDoLivro")
                separador.setFixedSize(1, 20)
                linha.addSpacing(10)
                linha.addWidget(separador)
                linha.addSpacing(10)
        linha.addStretch()
        linha.addWidget(self.pilula)
        return barra

    def _botao_de_jeito(self, texto: str, dica: str) -> QPushButton:
        botao = QPushButton(texto)
        botao.setObjectName("jeitoDoLivro")
        botao.setCheckable(True)
        botao.setToolTip(dica)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setFocusPolicy(Qt.NoFocus)
        return botao

    def jeito_guardado(self) -> dict:
        """O jeito de mostrar e de caber escolhido da última vez (configuracoes.json,
        chave "livro_aberto"); o que faltar ou vier estranho volta ao de fábrica."""
        import configuracoes
        jeito = dict(self.DE_FABRICA)
        try:
            salvo = configuracoes.ler("livro_aberto")
        except Exception:  # noqa: BLE001 - configuração nunca impede a tela
            salvo = None
        if isinstance(salvo, dict):
            if salvo.get("mostrar") in {j for j, _t, _d in self.JEITOS_DE_MOSTRAR}:
                jeito["mostrar"] = salvo["mostrar"]
            if isinstance(salvo.get("rolar"), bool):
                jeito["rolar"] = salvo["rolar"]
            if salvo.get("caber") in {j for j, _t, _d in self.JEITOS_DE_CABER}:
                jeito["caber"] = salvo["caber"]
        return jeito

    def _aplicar_jeito(self, jeito: dict) -> None:
        """Mostra o jeito nos botões e nas páginas (sem gravar)."""
        self.botoes_mostrar[jeito["mostrar"]].setChecked(True)
        self.botao_rolar.setChecked(bool(jeito["rolar"]))
        self.botoes_caber[jeito["caber"]].setChecked(True)
        self.paginas.definir_jeito(mostrar=jeito["mostrar"], continuo=jeito["rolar"], caber=jeito["caber"])

    def _gravar_jeito(self) -> None:
        """Lembra a escolha para o próximo livro (configuracoes.json)."""
        import configuracoes
        configuracoes.escrever("livro_aberto", {
            "mostrar": self.paginas.mostrar, "rolar": self.paginas.continuo, "caber": self.paginas.caber})

    def _escolher_mostrar(self, jeito: str) -> None:
        self.paginas.definir_jeito(mostrar=jeito)
        self._pagina_mudou(self.paginas.atual)
        self._gravar_jeito()

    def _escolher_rolar(self, ligado: bool) -> None:
        self.paginas.definir_jeito(continuo=ligado)
        self._pagina_mudou(self.paginas.atual)
        self._gravar_jeito()

    def _escolher_caber(self, jeito: str) -> None:
        self.paginas.definir_jeito(caber=jeito)
        self._pagina_mudou(self.paginas.atual)
        self._gravar_jeito()

    def _botao(self, texto: str, dica: str, acao, primario: bool = False) -> QPushButton:
        botao = QPushButton(texto)
        botao.setToolTip(dica)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setFocusPolicy(Qt.NoFocus)
        if primario:
            botao.setObjectName("acaoPrimaria")
        botao.clicked.connect(lambda _c=False: acao())
        return botao

    # --- uso --------------------------------------------------------------------

    def mostrar(self, resumo: projetos.Resumo) -> None:
        """Mostra o livro `resumo` (o folhear lê o PDF como ele está)."""
        self.resumo = resumo
        situacao, caminho = projetos.procurar_o_livro(resumo)
        self.perdido = situacao in (projetos.SUMIU, projetos.TROCADO)
        self.nome.setText(resumo.nome)
        self.detalhe.setText(f"{resumo.total_paginas} páginas · aberto {resumo.data_amigavel}")
        self.barra.setValue(100 if resumo.pdf_gerado else int(resumo.progresso * 100))
        self.andamento.setText(resumo.frase_do_progresso)
        from PySide6.QtGui import QFontMetrics
        curto = QFontMetrics(self.onde_esta.font()).elidedText(
            resumo.caminho_entrada, Qt.ElideMiddle, 420)
        self.onde_esta.setText(f"Onde está: <b>{curto}</b>")
        self.onde_esta.setToolTip(resumo.caminho_entrada)
        # etapa 3 da obra (R6): o que o resumo guarda do trabalho
        revisar = int(getattr(resumo, "para_revisar", 0) or 0)
        self.para_revisar.setText(f"Para revisar: {revisar}")
        self.para_revisar.setToolTip("Páginas e folhas com um aviso que ainda pede um olhar.")
        receita = getattr(resumo, "receita_usada", "") or "nenhuma"
        self.receita_usada.setText(f"Receita usada: {receita}")
        self.receita_usada.setToolTip("A última receita com que o Automático rodou neste livro.")
        from ui.widgets.paineis import frase_dos_avisos_do_livro
        frase = frase_dos_avisos_do_livro(getattr(resumo, "avisos_do_livro", None) or [])
        self.avisos_do_livro.setText(frase)
        self.avisos_do_livro.setVisible(bool(frase))
        for botao in (self.botao_continuar, self.botao_automatico, self.botao_processar, self.botao_todas):
            botao.setVisible(not self.perdido)
        self.pilha_do_meio.setCurrentWidget(self.paginas)
        if self.perdido:
            self.perdido_aviso.setText(
                "O PDF deste livro saiu do lugar (ou foi trocado por outro).\n"
                "Use “Mais...” > “procurar o livro” e aponte onde ele está.")
            self.pilha_do_meio.setCurrentWidget(self.perdido_aviso)
            self.miniaturas.limpar()
            self.paginas.limpar()
            return
        self.paginas.abrir(resumo.caminho_entrada)
        self._aplicar_jeito(self.jeito_guardado())
        total = self.paginas.total()
        self.miniaturas.montar(total, resumo.caminho_entrada, {i: i for i in range(total)})
        self.campo_ir.setRange(1, max(1, total))
        self.ir_para(min(max(0, resumo.pagina_atual), max(0, total - 1)))
        self._acertar_pecas_soltas()

    def fechar(self) -> None:
        """Ao voltar para os livros: para de desenhar e solta o PDF."""
        self.paginas.parar()
        self.paginas.limpar()
        self.miniaturas.parar()
        self.todas.esquecer()

    def ir_para(self, indice: int) -> None:
        total = self.paginas.total()
        if not total:
            return
        indice = max(0, min(total - 1, int(indice)))
        self.paginas.ir_para(indice)
        self._pagina_mudou(indice)

    def _pagina_mudou(self, indice: int) -> None:
        total = self.paginas.total()
        # janela estreita (a mínima, 1000 x 600): "301 de 750", sem o "ir para",
        # para a pílula caber ao lado dos botões da barra de baixo
        estreita = self.width() < LARGURA_DA_PILULA_INTEIRA
        self.rotulo_pagina.setText(f"{indice + 1} de {total}" if estreita else f"página {indice + 1} de {total}")
        self.rotulo_ir.setVisible(not estreita)
        self.rotulo_pagina.setMinimumWidth(self.rotulo_pagina.sizeHint().width())   # nunca cortado
        self.campo_ir.blockSignals(True)
        self.campo_ir.setValue(indice + 1)
        self.campo_ir.blockSignals(False)
        self.miniaturas.selecionar(indice)

    def _ver_todas(self) -> None:
        """Ver todas as páginas: as folhas do PDF em grade (uma a uma, 901 A)."""
        from ui.widgets.todas_as_paginas import ItemDaGrade
        if self.resumo is None or self.perdido:
            return
        # etapa 7 da obra (lista única 5.5: aqui dava "(0)"): cada folha do PDF
        # leva o motivo e quantas páginas dela têm dúvida (projetos.Resumo)
        duvidas = getattr(self.resumo, "duvidas_por_folha", None) or {}
        itens = []
        for i in range(self.paginas.total()):
            motivo, quantas = (duvidas.get(str(i)) or ["", 0])[:2]
            itens.append(ItemDaGrade(indice=i, folha=i, motivo=str(motivo or ""),
                                     duvidas=int(quantas or 0)))
        self.todas.mostrar(itens, self.paginas.atual, self.resumo.caminho_entrada, None)
        self.pilha_do_meio.setCurrentWidget(self.todas)

    def _voltar_da_grade(self, indice) -> None:
        self.pilha_do_meio.setCurrentWidget(self.paginas)
        if indice is not None:
            self.ir_para(indice)

    def _abrir_o_mais(self) -> None:
        if self.resumo is None:
            return
        menu = _menu_do_livro(self, self.tela, self.resumo, self.perdido)
        menu.exec(self.botao_mais.mapToGlobal(QPoint(0, self.botao_mais.height())))

    def _acertar_pecas_soltas(self) -> None:
        """A pílula mora na barra de baixo desde 22/10/2026 (antes era posta por
        cima das páginas, aqui); só o texto dela muda com a largura da janela."""
        if self.paginas.total():
            self._pagina_mudou(self.paginas.atual)

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        self._acertar_pecas_soltas()

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().showEvent(evento)
        self._acertar_pecas_soltas()

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Esc volta para os livros; Page Up/Down e setas folheiam."""
        tecla = evento.key()
        if tecla == Qt.Key_Escape:
            if self.pilha_do_meio.currentWidget() is self.todas:
                self._voltar_da_grade(None)
            else:
                self.tela.voltar_para_os_livros()
        elif tecla in (Qt.Key_PageDown, Qt.Key_Down, Qt.Key_Right):
            self.ir_para(self.paginas.passo(1))         # no par, o par seguinte
        elif tecla in (Qt.Key_PageUp, Qt.Key_Up, Qt.Key_Left):
            self.ir_para(self.paginas.passo(-1))
        elif tecla == Qt.Key_Home:
            self.ir_para(0)
        elif tecla == Qt.Key_End:
            self.ir_para(self.paginas.total() - 1)
        else:
            super().keyPressEvent(evento)
