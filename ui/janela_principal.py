"""A janela e o fluxo entre as telas.

Inicio -> Opcoes -> (análise) -> Conferir -> (processamento) -> Pronto
"""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

import configuracoes
import historico
import projetos
from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
from historico_acoes import HistoricoAcoes
from modelos import Projeto
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
        self.setWindowTitle("Editor de Impressão")
        self.setMinimumSize(1000, 680)
        self.resize(1220, 800)
        self.setStyleSheet(FOLHA_DE_ESTILO)

        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None
        self.tarefa = None
        self.total_folhas = 0
        self.resumo: projetos.Resumo | None = None

        # Salvar sozinho, com um respiro. Gravar a cada mudanca travaria a tela
        # ao arrastar o medidor - sao dezenas de mudancas por segundo, e o
        # projeto de um livro de mil paginas nao e um arquivo pequeno. O relogio
        # junta a rajada e grava uma vez depois que a mao para.
        #
        # NAO existe botao de salvar e nunca se pergunta "quer salvar?". Essa
        # pergunta e uma armadilha para quem nao e tecnico: um "nao" por engano
        # apaga um dia de trabalho.
        self._relogio_de_salvar = QTimer(self)
        self._relogio_de_salvar.setSingleShot(True)
        self._relogio_de_salvar.setInterval(600)
        self._relogio_de_salvar.timeout.connect(self._salvar_agora)

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
        self.tela_conferir.voltar.connect(self._sair_da_conferencia)
        self.tela_conferir.processar.connect(self.processar)
        self.tela_conferir.trabalho_mudou.connect(self._marcar_para_salvar)
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
            self.avisar("Não consegui abrir esse arquivo. Ele pode não ser um PDF.")
            return

        nome = Path(caminho).stem
        self.projeto = Projeto(caminho_entrada=caminho, nome=nome)

        # Abrir o MESMO livro de novo continua o projeto de antes, em vez de
        # criar um ao lado: quem for reabrir de propósito passa pela tela
        # inicial, que tem "começar de novo" no menu do cartão.
        self.resumo = projetos.achar_por_assinatura(caminho)
        if self.resumo is None:
            self.resumo = projetos.criar(self.projeto, self.total_folhas)
        else:
            self.resumo.caminho_entrada = caminho   # pode ter mudado de pasta
        self.acoes = HistoricoAcoes(Path(self.resumo.pasta))

        self.tela_opcoes.carregar(self.projeto, self.total_folhas)
        self.telas.setCurrentIndex(OPCOES)

    def _reabrir(self, entrada: historico.Entrada) -> None:
        """Reabre um projeto do histórico, com as mesmas configuracoes."""
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
        assert self.acoes is not None

        # O trabalho da sessao passada volta AQUI, depois da analise: filtro de
        # cada pagina, corte, angulo, marcacao, apagadas, conferidas. Sem isto,
        # quem conferiu 80 paginas e fechou o programa reabria do zero.
        #
        # So volta se combinar com o livro recem-analisado - mesmo arquivo,
        # mesma contagem de folhas e de paginas. Se a pessoa mudou "dividir
        # folhas ao meio" entre uma sessao e outra, a pagina 40 salva nao e a
        # pagina 40 de agora, e devolver o corte de uma na outra estragaria o
        # trabalho em silencio. Ver projetos.combina_com.
        paginas_perdidas = 0
        if self.resumo is not None:
            salvo = projetos.carregar_estado(self.resumo)
            if projetos.combina_com(salvo, projeto):
                projeto = salvo
            elif salvo is not None:
                paginas_perdidas = len(salvo.paginas)

        self.projeto = projeto

        # O desfazer de um projeto ja trabalhado tambem volta do disco.
        self.acoes.carregar()

        if self.previas is not None:
            self.previas.parar()
        self.previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, self)

        self.tela_conferir.carregar(projeto, self.acoes, self.previas)
        if self.resumo is not None:
            self.tela_conferir.ir_para_pagina(self.resumo.pagina_atual)
        self.telas.setCurrentIndex(CONFERIR)
        self._salvar_agora()

        if self.acoes.linhas_perdidas:
            self.avisar(
                f"O computador foi desligado no meio da última gravação, e "
                f"{self.acoes.linhas_perdidas} ação(ões) do fim se perderam. "
                "O resto do trabalho está aqui.")
        elif paginas_perdidas:
            self.avisar(
                "Você mudou as opções desde a última vez, e o livro ficou com "
                "outro número de páginas. Comecei a conferência de novo - o "
                "trabalho antigo não serve para páginas diferentes.")

    # --- salvar sozinho ---------------------------------------------------

    def _marcar_para_salvar(self) -> None:
        """Alguma coisa mudou. Grava daqui a pouco, quando a mao parar."""
        if self.resumo is not None and self.projeto is not None:
            self._relogio_de_salvar.start()

    def _salvar_agora(self) -> None:
        """Grava de verdade. Chamado pelo relogio e ao sair da tela."""
        self._relogio_de_salvar.stop()
        if self.resumo is None or self.projeto is None:
            return
        projetos.salvar_estado(self.resumo, self.projeto)
        projetos.atualizar(self.resumo, self.projeto,
                           pagina_atual=self.tela_conferir.indice_pagina)

    def _sair_da_conferencia(self) -> None:
        """Voltar para as opcoes grava antes: sair nao pode custar trabalho."""
        self._salvar_agora()
        self.telas.setCurrentIndex(OPCOES)

    def _falhou_na_analise(self, mensagem: str) -> None:
        self.telas.setCurrentIndex(OPCOES)
        self.avisar(mensagem)

    # --- processamento ----------------------------------------------------

    def processar(self) -> None:
        if self.projeto is None:
            return

        caminho = self._resolver_destino()
        if caminho is None:
            return  # o usuario desistiu ou a pasta nao serve

        self.projeto.caminho_saida = str(caminho)
        configuracoes.lembrar_pasta_de_saida(caminho.parent)
        historico.salvar_projeto(self.projeto)

        self.tela_progresso.comecar("Processando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        self.tarefa = TarefaProcessar(self.projeto)
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._processamento_pronto)
        self.tarefa.falhou.connect(self._falhou_no_processamento)
        self.tarefa.cancelada.connect(lambda: self.telas.setCurrentIndex(CONFERIR))
        self.tarefa.start()

    def _resolver_destino(self) -> Path | None:
        """Confere a pasta e o nome escolhidos. Devolve None se não der para seguir.

        Duas perguntas, nesta ordem: da para gravar nessa pasta? e o arquivo já
        existe? Nenhuma das duas pode virar um erro técnico na cara do usuario.
        """
        destino = self.tela_conferir.destino
        caminho = destino.caminho

        pode, motivo = destino.pronto_para_gravar()
        if not pode:
            self.avisar(
                f"{motivo}\n\nA pasta era:\n{destino.pasta}",
                titulo="Não consigo salvar ai",
            )
            destino.escolher_pasta()
            return None

        if caminho.exists():
            return self._perguntar_sobre_substituir(caminho)

        return caminho

    def _perguntar_sobre_substituir(self, caminho: Path) -> Path | None:
        """Já existe arquivo com esse nome: substituir, renomear ou desistir."""
        alternativo = configuracoes.caminho_sem_repetir(caminho.parent, caminho.name)

        caixa = QMessageBox(self)
        caixa.setWindowTitle("Já existe um arquivo com esse nome")
        caixa.setIcon(QMessageBox.Question)
        caixa.setText(f"Já existe um arquivo chamado:\n{caminho.name}")
        caixa.setInformativeText(
            f"Posso substituir o antigo ou salvar como:\n{alternativo.name}"
        )
        botao_substituir = caixa.addButton("substituir o antigo", QMessageBox.DestructiveRole)
        botao_renomear = caixa.addButton(
            f"salvar como {alternativo.name}", QMessageBox.AcceptRole
        )
        caixa.addButton("cancelar", QMessageBox.RejectRole)
        caixa.setDefaultButton(botao_renomear)
        caixa.exec()

        escolhido = caixa.clickedButton()
        if escolhido is botao_substituir:
            return caminho
        if escolhido is botao_renomear:
            self.tela_conferir.destino.definir(alternativo.parent, alternativo.name)
            return alternativo
        return None

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
        """Sair no meio de um trabalho não pode deixar thread solta nem perder
        o que foi feito.

        Grava ANTES de encerrar as threads: a prévia que ainda vier não muda o
        trabalho, e esperar por ela só atrasaria o fechamento.

        E não pergunta nada. A pergunta "quer salvar?" é o que este programa
        não faz - um "não" por engano apagaria um dia de trabalho do Kaique.
        """
        self._salvar_agora()

        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(3000)
        if self.previas is not None:
            self.previas.parar()
        self.tela_conferir.tira.parar()
        if self.projeto is not None:
            historico.salvar_projeto(self.projeto)
        evento.accept()
