"""A janela e o fluxo entre as telas.

Inicio -> Opcoes -> (analise) -> Conferir -> (processamento) -> Pronto
"""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

import historico
from core.filtros import NOMES_AMIGAVEIS
from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
from historico_acoes import HistoricoAcoes
from modelos import Projeto, nome_de_arquivo_seguro
from registro import registrar_erro
from ui.estilo import FOLHA_DE_ESTILO
from ui.tarefas import GerenciadorPrevias, TarefaAnalise, TarefaProcessar
from ui.tela_conferir import TelaConferir
from ui.tela_final import TelaFinal, TelaProgresso
from ui.tela_inicio import TelaInicio
from ui.tela_opcoes import TelaOpcoes

INICIO, OPCOES, PROGRESSO, CONFERIR, FINAL = range(5)


class JanelaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Editor de Impressao")
        self.setMinimumSize(1000, 680)
        self.resize(1220, 800)
        self.setStyleSheet(FOLHA_DE_ESTILO)

        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None
        self.tarefa = None
        self.total_folhas = 0

        self.telas = QStackedWidget()
        self.setCentralWidget(self.telas)

        self.tela_inicio = TelaInicio()
        self.tela_inicio.abrir_pdf.connect(self.abrir_livro)
        self.tela_inicio.reabrir_projeto.connect(self._reabrir)
        self.telas.addWidget(self.tela_inicio)

        self.tela_opcoes = TelaOpcoes()
        self.tela_opcoes.voltar.connect(lambda: self.telas.setCurrentIndex(INICIO))
        self.tela_opcoes.conferir.connect(self.analisar)
        self.telas.addWidget(self.tela_opcoes)

        self.tela_progresso = TelaProgresso()
        self.tela_progresso.cancelar.connect(self.cancelar)
        self.telas.addWidget(self.tela_progresso)

        self.tela_conferir = TelaConferir()
        self.tela_conferir.voltar.connect(lambda: self.telas.setCurrentIndex(OPCOES))
        self.tela_conferir.processar.connect(self.processar)
        self.telas.addWidget(self.tela_conferir)

        self.tela_final = TelaFinal()
        self.tela_final.fazer_outro.connect(self._recomecar)
        self.telas.addWidget(self.tela_final)

        self.telas.setCurrentIndex(INICIO)

    # ------------------------------------------------------------------
    # avisos
    # ------------------------------------------------------------------

    def avisar(self, mensagem: str, titulo: str = "Um momento") -> None:
        """Regra 3.3: erro vira aviso gentil e o programa continua aberto."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle(titulo)
        caixa.setIcon(QMessageBox.Information)
        caixa.setText(mensagem)
        caixa.addButton("entendi", QMessageBox.AcceptRole)
        caixa.exec()

    # ------------------------------------------------------------------
    # fluxo
    # ------------------------------------------------------------------

    def abrir_livro(self, caminho: str) -> None:
        try:
            doc = abrir_pdf(caminho)
            try:
                self.total_folhas = doc.page_count
                info_paginas(doc)
            finally:
                doc.close()
        except ErroPDF as erro:
            self.avisar(str(erro))
            return
        except Exception:  # noqa: BLE001
            registrar_erro("abrir", traceback.format_exc())
            self.avisar("Nao consegui abrir esse arquivo. Ele pode nao ser um PDF.")
            return

        nome = Path(caminho).stem
        self.projeto = Projeto(caminho_entrada=caminho, nome=nome)
        self.acoes = HistoricoAcoes(historico.pasta_do_projeto(nome))

        self.tela_opcoes.carregar(self.projeto, self.total_folhas)
        self.telas.setCurrentIndex(OPCOES)

    def _reabrir(self, entrada: historico.Entrada) -> None:
        """Reabre um projeto do historico, com as mesmas configuracoes."""
        salvo = historico.carregar_projeto(entrada.nome)
        self.abrir_livro(entrada.caminho_entrada)
        if salvo is not None and self.projeto is not None:
            self.projeto.dividir_folhas = salvo.dividir_folhas
            self.projeto.limpar = salvo.limpar
            self.projeto.filtro_padrao = salvo.filtro_padrao
            self.projeto.endireitar = salvo.endireitar
            self.projeto.cortar_bordas = salvo.cortar_bordas
            self.projeto.montar_cadernos = salvo.montar_cadernos
            self.projeto.paginas_por_caderno = salvo.paginas_por_caderno
            self.tela_opcoes.carregar(self.projeto, self.total_folhas)

    # --- analise ----------------------------------------------------------

    def analisar(self) -> None:
        if self.projeto is None:
            return
        self.tela_progresso.comecar("Olhando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        self.tarefa = TarefaAnalise(self.projeto)
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._analise_pronta)
        self.tarefa.falhou.connect(self._falhou_na_analise)
        self.tarefa.start()

    def _analise_pronta(self, projeto: Projeto) -> None:
        self.projeto = projeto
        assert self.acoes is not None

        # O historico de acoes de um projeto ja trabalhado antes volta do disco:
        # fechar e reabrir o programa nao apaga o desfazer (criterio 14).
        self.acoes.carregar()

        if self.previas is not None:
            self.previas.parar()
        self.previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, self)

        self.tela_conferir.carregar(projeto, self.acoes, self.previas)
        self.telas.setCurrentIndex(CONFERIR)
        historico.salvar_projeto(projeto)

    def _falhou_na_analise(self, mensagem: str) -> None:
        self.telas.setCurrentIndex(OPCOES)
        self.avisar(mensagem)

    # --- processamento ----------------------------------------------------

    def processar(self) -> None:
        if self.projeto is None:
            return

        self.projeto.caminho_saida = self._caminho_de_saida()
        historico.salvar_projeto(self.projeto)

        self.tela_progresso.comecar("Processando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        self.tarefa = TarefaProcessar(self.projeto)
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._processamento_pronto)
        self.tarefa.falhou.connect(self._falhou_no_processamento)
        self.tarefa.cancelada.connect(lambda: self.telas.setCurrentIndex(CONFERIR))
        self.tarefa.start()

    def _caminho_de_saida(self) -> str:
        """Monta o nome do arquivo final, sem o usuario precisar escolher."""
        assert self.projeto is not None
        pasta = historico.pasta_de_saida_padrao()
        nome = nome_de_arquivo_seguro(self.projeto.nome)

        if self.projeto.montar_cadernos:
            sufixo = "cadernos"
        elif self.projeto.limpar:
            sufixo = NOMES_AMIGAVEIS.get(
                self.projeto.filtro_padrao, self.projeto.filtro_padrao
            ).lower()
        else:
            sufixo = "arrumado"

        caminho = pasta / f"{nome} - {sufixo}.pdf"
        # nunca sobrescrever um trabalho anterior sem avisar
        contador = 2
        while caminho.exists():
            caminho = pasta / f"{nome} - {sufixo} ({contador}).pdf"
            contador += 1
        return str(caminho)

    def _processamento_pronto(self, caminho: str) -> None:
        assert self.projeto is not None
        try:
            import fitz

            with fitz.open(caminho) as doc:
                folhas_de_saida = doc.page_count
        except Exception:  # noqa: BLE001
            folhas_de_saida = 0

        # Paginas DO LIVRO: com cadernos, o arquivo tem metade das paginas,
        # porque cada folha leva duas. Quem conta caderno e a pagina do livro.
        if self.projeto.montar_cadernos:
            paginas = len(self.projeto.paginas_ativas) if self.projeto.paginas else folhas_de_saida * 2
        else:
            paginas = folhas_de_saida or len(self.projeto.paginas_ativas)

        historico.registrar(self.projeto, paginas)
        historico.salvar_projeto(self.projeto)
        self.tela_inicio.recarregar()

        self.tela_final.mostrar(self.projeto, caminho, paginas, folhas_de_saida)
        self.telas.setCurrentIndex(FINAL)

    def _falhou_no_processamento(self, mensagem: str) -> None:
        self.telas.setCurrentIndex(CONFERIR)
        self.avisar(mensagem)

    def cancelar(self) -> None:
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
        destino = CONFERIR if self.projeto and self.projeto.paginas else OPCOES
        self.telas.setCurrentIndex(destino)

    def _recomecar(self) -> None:
        self.tela_inicio.recarregar()
        self.telas.setCurrentIndex(INICIO)

    # ------------------------------------------------------------------
    # teclado e fechamento
    # ------------------------------------------------------------------

    def keyPressEvent(self, evento) -> None:  # noqa: N802
        if self.telas.currentIndex() == CONFERIR:
            if self.tela_conferir.tratar_tecla(evento):
                evento.accept()
                return
        super().keyPressEvent(evento)

    def closeEvent(self, evento) -> None:  # noqa: N802
        """Sair no meio de um trabalho nao pode deixar thread solta."""
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(3000)
        if self.previas is not None:
            self.previas.parar()
        self.tela_conferir.tira.parar()
        if self.projeto is not None:
            historico.salvar_projeto(self.projeto)
        evento.accept()
