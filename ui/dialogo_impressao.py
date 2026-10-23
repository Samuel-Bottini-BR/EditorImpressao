"""Item 2.6: a janela "Montar para imprimir" (CONTROLE MÍNIMO, PROVISÓRIO).

É a janela de imprimir do UPDF dentro do programa, como o Samuel pediu em
14/10/2026 ("Quero TODAS essas opções dentro do programa, para ter bastante
escolha"). Abre da tela "Ficou pronto!" (botão "montar para imprimir...") e
trabalha sobre o PDF que acabou de ser gerado: grava um arquivo à parte com as
folhas prontas para a impressora, ou manda direto para ela (imp-5).

Tudo o que é conta mora em core/impressao.py e core/impressora.py; aqui só
os controles, um fio (QThread) para a janela não parar e os avisos em
português. A aparência e o lugar são do agente de layout: as escolhas feitas
aqui estão anotadas em relatorios/fase2-novas/ONDE-PAREI.md.

As escolhas ficam guardadas no configuracoes.json (chave "impressao"), como a
"Predefinição: Última configuração" do UPDF. Seguro mudar: os textos.
Arriscado: montar no fio da tela (a janela pararia num livro grande).
"""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import configuracoes
from core import impressao as imp
from registro import registrar_erro
from ui import estilo

CHAVE_DAS_CONFIGURACOES = "impressao"
OPCOES_CADERNO = [8, 12, 16, 20, 24, 32, 40]


def ler_excecoes(texto: str) -> dict[int, float]:
    """"12=90; 15=85" -> {12: 90.0, 15: 85.0}. O que não se entende é ignorado."""
    excecoes: dict[int, float] = {}
    for pedaco in texto.replace(",", ";").split(";"):
        if "=" not in pedaco:
            continue
        pagina, _, valor = pedaco.partition("=")
        try:
            numero, por_cento = int(pagina.strip()), float(valor.strip().rstrip("%"))
        except ValueError:
            continue
        if numero > 0 and por_cento > 0:
            excecoes[numero] = por_cento
    return excecoes


def escrever_excecoes(excecoes: dict) -> str:
    return "; ".join(f"{n}={v:g}" for n, v in sorted(excecoes.items()))


class _Tarefa(QThread):
    """Monta o arquivo (ou imprime) fora do fio da tela."""

    progresso = Signal(int, int, str)
    concluida = Signal(object)
    falhou = Signal(str)

    def __init__(self, entrada: str, opcoes: imp.OpcoesDeImpressao, destino: str = "",
                 impressora: str = "", copias: int = 1, agrupar: bool = True) -> None:
        super().__init__()
        self.entrada, self.opcoes, self.destino = entrada, opcoes, destino
        self.impressora, self.copias, self.agrupar = impressora, copias, agrupar
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            avisar = lambda f, t, txt: self.progresso.emit(f, t, txt)  # noqa: E731
            if self.destino:
                resultado = imp.montar_para_impressao(self.entrada, self.destino, self.opcoes,
                                                      progresso=avisar,
                                                      cancelado=lambda: self._cancelar)
            else:
                from core import impressora

                self.progresso.emit(0, 1, "Falando com a impressora (pode demorar um pouco)")
                folhas, resultado = imp.montar_em_memoria(self.entrada, self.opcoes)
                try:
                    lado = (impressora.BORDA_CURTA if self.opcoes.formato == imp.LIVRETO
                            else impressora.BORDA_COMPRIDA)
                    if self.opcoes.lados != imp.AMBOS:
                        lado = impressora.SO_UM_LADO
                    impressora.imprimir(folhas, self.impressora, self.copias, self.agrupar, lado,
                                        progresso=avisar, cancelado=lambda: self._cancelar)
                finally:
                    folhas.close()
            self.concluida.emit(resultado)
        except imp.Cancelou:
            self.falhou.emit("Cancelado: nada foi gravado.")
        except Exception:  # noqa: BLE001 - nunca fecha a janela (CLAUDE.md §3)
            registrar_erro("montar para imprimir", traceback.format_exc())
            self.falhou.emit("Não consegui montar o arquivo para imprimir. "
                             "O livro continua salvo como estava.")


class DialogoImpressao(QDialog):
    """A janela de imprimir. `entrada` é o PDF do livro (as páginas em ordem)."""

    def __init__(self, entrada: str, parent=None) -> None:
        super().__init__(parent)
        self.entrada = entrada
        self.tarefa: _Tarefa | None = None
        self.ultimo_resultado: imp.Resultado | None = None
        self.setWindowTitle("Montar para imprimir")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO)
        self.setMinimumSize(620, 560)

        externo = QVBoxLayout(self)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        dentro = QWidget()
        coluna = QVBoxLayout(dentro)
        rolagem.setWidget(dentro)
        externo.addWidget(rolagem, 1)

        # --- formato e papel
        geral = QGroupBox("Como vai sair")
        form = QFormLayout(geral)
        self.combo_formato = self._combo(imp.FORMATOS, imp.NOMES_DOS_FORMATOS)
        form.addRow("Formato:", self.combo_formato)
        self.combo_papel = self._combo(tuple(imp.PAPEIS_MM), {p: p for p in imp.PAPEIS_MM})
        form.addRow("Papel:", self.combo_papel)
        self.combo_orientacao = self._combo(("", imp.RETRATO, imp.PAISAGEM),
                                            {"": "a do formato", imp.RETRATO: "em pé (retrato)",
                                             imp.PAISAGEM: "deitada (paisagem)"})
        form.addRow("Folha:", self.combo_orientacao)
        self.combo_escala = self._combo(imp.ESCALAS, imp.NOMES_DAS_ESCALAS)
        form.addRow("Tamanho:", self.combo_escala)
        self.escala_percentual = self._por_cento()
        form.addRow("Escala personalizada:", self.escala_percentual)
        self.cx_girar = QCheckBox("Rotação automática (página deitada gira de pé)")
        self.cx_centralizar = QCheckBox("Centralizar automático")
        self.cx_margens = QCheckBox("Margens da encadernação: 1,3 cm da beirada do papel e 1 cm na costura")
        for caixa in (self.cx_girar, self.cx_centralizar, self.cx_margens):
            form.addRow(caixa)
        coluna.addWidget(geral)

        # --- escala por lado (g12, imp-1)
        lados = QGroupBox("Escala de cada lado (sobre o tamanho escolhido)")
        form = QFormLayout(lados)
        self.escala_esquerda = self._por_cento()
        self.escala_direita = self._por_cento()
        form.addRow("Páginas da esquerda (pares):", self.escala_esquerda)
        form.addRow("Páginas da direita (ímpares):", self.escala_direita)
        self.excecoes = QLineEdit()
        self.excecoes.setPlaceholderText("ex.: 12=90; 15=85")
        self.excecoes.setToolTip("Uma página só, com outra escala: número da página do livro = %.")
        form.addRow("Só uma página:", self.excecoes)
        coluna.addWidget(lados)

        # --- livreto
        self.grupo_livreto = QGroupBox("Livreto")
        form = QFormLayout(self.grupo_livreto)
        self.combo_caderno = QComboBox()
        for valor in OPCOES_CADERNO:
            self.combo_caderno.addItem(str(valor), valor)
        form.addRow("Páginas por caderno:", self.combo_caderno)
        self.combo_encadernacao = self._combo((imp.ESQUERDA, imp.DIREITA),
                                              {imp.ESQUERDA: "Esquerda", imp.DIREITA: "Direita"})
        form.addRow("Encadernação:", self.combo_encadernacao)
        self.combo_lados = self._combo((imp.AMBOS, imp.SO_FRENTE, imp.SO_VERSO),
                                       {imp.AMBOS: "Frente e verso", imp.SO_FRENTE: "Só a frente",
                                        imp.SO_VERSO: "Só o verso"})
        form.addRow("Ordem de páginas:", self.combo_lados)
        self.folhas_de, self.folhas_ate = self._numero(), self._numero()
        form.addRow("Folhas de (0 = todas):", self._linha(self.folhas_de, "até", self.folhas_ate))
        coluna.addWidget(self.grupo_livreto)

        # --- várias por folha e pôster
        self.grupo_multiplo = QGroupBox("Várias páginas por folha")
        form = QFormLayout(self.grupo_multiplo)
        self.combo_por_folha = self._combo(imp.POR_FOLHA, {n: str(n) for n in imp.POR_FOLHA})
        form.addRow("Páginas por folha:", self.combo_por_folha)
        self.combo_ordem = self._combo((imp.HORIZONTAL, imp.VERTICAL),
                                       {imp.HORIZONTAL: "Horizontal", imp.VERTICAL: "Vertical"})
        form.addRow("Ordem:", self.combo_ordem)
        self.cx_moldura = QCheckBox("Moldura em volta de cada página")
        form.addRow(self.cx_moldura)
        coluna.addWidget(self.grupo_multiplo)

        self.grupo_poster = QGroupBox("Pôster")
        form = QFormLayout(self.grupo_poster)
        self.poster_escala = self._por_cento()
        form.addRow("Escala do pedaço:", self.poster_escala)
        self.poster_sobra = QDoubleSpinBox()
        self.poster_sobra.setRange(0, 50)
        self.poster_sobra.setSuffix(" mm")
        form.addRow("Sobreposição:", self.poster_sobra)
        self.cx_marcas = QCheckBox("Marcas de corte e o nome de cada pedaço")
        self.cx_so_grandes = QCheckBox("Só as páginas grandes (as que cabem saem inteiras)")
        form.addRow(self.cx_marcas)
        form.addRow(self.cx_so_grandes)
        coluna.addWidget(self.grupo_poster)

        # --- o resto da janela do UPDF
        outros = QGroupBox("Outras opções")
        form = QFormLayout(outros)
        self.paginas_de, self.paginas_ate = self._numero(), self._numero()
        form.addRow("Páginas do livro de (0 = todas):", self._linha(self.paginas_de, "até", self.paginas_ate))
        self.cx_cinza = QCheckBox("Imprimir em escala de cinza")
        self.cx_imagem = QCheckBox("Imprimir como imagem")
        self.cx_reverter = QCheckBox("Reverter páginas (da última folha para a primeira)")
        for caixa in (self.cx_cinza, self.cx_imagem, self.cx_reverter):
            form.addRow(caixa)
        coluna.addWidget(outros)

        # --- impressora
        grupo_impressora = QGroupBox("Impressora (para mandar direto)")
        form = QFormLayout(grupo_impressora)
        self.combo_impressora = QComboBox()
        self.combo_impressora.addItem("(a de sempre do Windows)", "")
        form.addRow("Impressora:", self.combo_impressora)
        self.copias = QSpinBox()
        self.copias.setRange(1, 99)
        form.addRow("Cópias:", self.copias)
        self.cx_agrupar = QCheckBox("Agrupar")
        self.cx_agrupar.setChecked(True)
        form.addRow(self.cx_agrupar)
        coluna.addWidget(grupo_impressora)
        coluna.addStretch()

        # --- o que aconteceu
        self.estado = QLabel("")
        self.estado.setWordWrap(True)
        externo.addWidget(self.estado)
        self.avisos = QPlainTextEdit()
        self.avisos.setReadOnly(True)
        self.avisos.setMaximumHeight(120)
        self.avisos.setVisible(False)
        externo.addWidget(self.avisos)

        botoes = QHBoxLayout()
        self.botao_gravar = QPushButton("gravar o arquivo para imprimir")
        self.botao_gravar.setObjectName("primario")
        self.botao_gravar.clicked.connect(self._gravar)
        self.botao_imprimir = QPushButton("mandar para a impressora")
        self.botao_imprimir.clicked.connect(self._imprimir)
        self.botao_cancelar = QPushButton("cancelar")
        self.botao_cancelar.clicked.connect(self._cancelar)
        self.botao_cancelar.setEnabled(False)
        fechar = QPushButton("fechar")
        fechar.clicked.connect(self.reject)
        for botao in (self.botao_gravar, self.botao_imprimir, self.botao_cancelar):
            botoes.addWidget(botao)
        botoes.addStretch()
        botoes.addWidget(fechar)
        externo.addLayout(botoes)

        self.combo_formato.currentIndexChanged.connect(lambda _i: self._acertar_grupos())
        self.combo_escala.currentIndexChanged.connect(lambda _i: self._acertar_grupos())
        self.definir_opcoes(imp.OpcoesDeImpressao.de_dicionario(
            configuracoes.ler(CHAVE_DAS_CONFIGURACOES)))

    # --- peças

    def _combo(self, codigos, nomes) -> QComboBox:
        combo = QComboBox()
        for codigo in codigos:
            combo.addItem(nomes.get(codigo, str(codigo)), codigo)
        return combo

    def _por_cento(self) -> QDoubleSpinBox:
        caixa = QDoubleSpinBox()
        caixa.setRange(10.0, 400.0)
        caixa.setDecimals(0)
        caixa.setSingleStep(5.0)
        caixa.setSuffix(" %")
        return caixa

    def _numero(self) -> QSpinBox:
        caixa = QSpinBox()
        caixa.setRange(0, 99999)
        return caixa

    def _linha(self, a, texto, b) -> QWidget:
        caixa = QWidget()
        linha = QHBoxLayout(caixa)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.addWidget(a)
        linha.addWidget(QLabel(texto))
        linha.addWidget(b)
        linha.addStretch()
        return caixa

    def _acertar_grupos(self) -> None:
        formato = self.combo_formato.currentData()
        self.grupo_livreto.setVisible(formato == imp.LIVRETO)
        self.grupo_multiplo.setVisible(formato == imp.MULTIPLO)
        self.grupo_poster.setVisible(formato == imp.POSTER)
        self.escala_percentual.setEnabled(self.combo_escala.currentData() == imp.PERSONALIZADA)

    # --- as opções

    def definir_opcoes(self, o: imp.OpcoesDeImpressao) -> None:
        """Põe as opções nos controles."""
        def escolher(combo, valor):
            i = combo.findData(valor)
            combo.setCurrentIndex(i if i >= 0 else 0)

        escolher(self.combo_formato, o.formato)
        escolher(self.combo_papel, o.papel)
        escolher(self.combo_orientacao, o.orientacao)
        escolher(self.combo_escala, o.escala)
        self.escala_percentual.setValue(o.escala_percentual)
        self.cx_girar.setChecked(o.rotacao_automatica)
        self.cx_centralizar.setChecked(o.centralizar)
        self.cx_margens.setChecked(o.margens)
        self.escala_esquerda.setValue(o.escala_esquerda)
        self.escala_direita.setValue(o.escala_direita)
        self.excecoes.setText(escrever_excecoes(o.excecoes))
        escolher(self.combo_caderno, o.paginas_por_caderno)
        escolher(self.combo_encadernacao, o.encadernacao)
        escolher(self.combo_lados, o.lados)
        self.folhas_de.setValue(o.folhas_de)
        self.folhas_ate.setValue(o.folhas_ate)
        escolher(self.combo_por_folha, o.multiplo_por_folha)
        escolher(self.combo_ordem, o.multiplo_ordem)
        self.cx_moldura.setChecked(o.multiplo_moldura)
        self.poster_escala.setValue(o.poster_escala)
        self.poster_sobra.setValue(o.poster_sobreposicao_mm)
        self.cx_marcas.setChecked(o.poster_marcas)
        self.cx_so_grandes.setChecked(o.poster_so_grandes)
        self.paginas_de.setValue(o.paginas_de)
        self.paginas_ate.setValue(o.paginas_ate)
        self.cx_cinza.setChecked(o.cinza)
        self.cx_imagem.setChecked(o.como_imagem)
        self.cx_reverter.setChecked(o.reverter)
        self._acertar_grupos()

    def opcoes(self) -> imp.OpcoesDeImpressao:
        """As opções que estão nos controles."""
        o = imp.OpcoesDeImpressao()
        o.formato = self.combo_formato.currentData()
        o.papel = self.combo_papel.currentData()
        o.orientacao = self.combo_orientacao.currentData()
        o.escala = self.combo_escala.currentData()
        o.escala_percentual = self.escala_percentual.value()
        o.rotacao_automatica = self.cx_girar.isChecked()
        o.centralizar = self.cx_centralizar.isChecked()
        o.margens = self.cx_margens.isChecked()
        o.escala_esquerda = self.escala_esquerda.value()
        o.escala_direita = self.escala_direita.value()
        o.excecoes = ler_excecoes(self.excecoes.text())
        o.paginas_por_caderno = int(self.combo_caderno.currentData())
        o.encadernacao = self.combo_encadernacao.currentData()
        o.lados = self.combo_lados.currentData()
        o.folhas_de, o.folhas_ate = self.folhas_de.value(), self.folhas_ate.value()
        o.multiplo_por_folha = int(self.combo_por_folha.currentData())
        o.multiplo_ordem = self.combo_ordem.currentData()
        o.multiplo_moldura = self.cx_moldura.isChecked()
        o.poster_escala = self.poster_escala.value()
        o.poster_sobreposicao_mm = self.poster_sobra.value()
        o.poster_marcas = self.cx_marcas.isChecked()
        o.poster_so_grandes = self.cx_so_grandes.isChecked()
        o.paginas_de, o.paginas_ate = self.paginas_de.value(), self.paginas_ate.value()
        o.cinza = self.cx_cinza.isChecked()
        o.como_imagem = self.cx_imagem.isChecked()
        o.reverter = self.cx_reverter.isChecked()
        return o

    def _guardar(self) -> imp.OpcoesDeImpressao:
        opcoes = self.opcoes()
        configuracoes.escrever(CHAVE_DAS_CONFIGURACOES, opcoes.para_dicionario())
        return opcoes

    # --- as ações

    def destino_sugerido(self) -> Path:
        entrada = Path(self.entrada)
        return entrada.with_name(f"{entrada.stem} - para imprimir.pdf")

    def _gravar(self) -> None:
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Gravar o arquivo para imprimir", str(self.destino_sugerido()), "PDF (*.pdf)")
        if caminho:
            self.comecar(destino=caminho)

    def _imprimir(self) -> None:
        if self.combo_impressora.count() == 1:
            try:
                from core import impressora

                for nome in impressora.listar_impressoras():
                    self.combo_impressora.addItem(nome, nome)
            except Exception:  # noqa: BLE001
                registrar_erro("listar impressoras", traceback.format_exc())
        self.comecar(impressora=self.combo_impressora.currentData() or "")

    def comecar(self, destino: str = "", impressora: str = "") -> None:
        """Começa a montar (destino) ou a imprimir, num fio à parte."""
        if self.tarefa is not None and self.tarefa.isRunning():
            return
        opcoes = self._guardar()
        self.tarefa = _Tarefa(self.entrada, opcoes, destino, impressora,
                              self.copias.value(), self.cx_agrupar.isChecked())
        self.tarefa.progresso.connect(lambda f, t, txt: self.estado.setText(txt))
        self.tarefa.concluida.connect(lambda r, d=destino: self._pronto(r, d))
        self.tarefa.falhou.connect(self._falhou)
        for botao in (self.botao_gravar, self.botao_imprimir):
            botao.setEnabled(False)
        self.botao_cancelar.setEnabled(True)
        self.tarefa.start()

    def _cancelar(self) -> None:
        if self.tarefa is not None:
            self.tarefa.cancelar()

    def _terminou(self) -> None:
        for botao in (self.botao_gravar, self.botao_imprimir):
            botao.setEnabled(True)
        self.botao_cancelar.setEnabled(False)

    def _pronto(self, resultado: imp.Resultado, destino: str) -> None:
        self._terminou()
        self.ultimo_resultado = resultado
        partes = [f"Pronto: {resultado.paginas_do_arquivo} páginas no arquivo"
                  + (f", {resultado.folhas_de_papel} folhas de papel" if resultado.folhas_de_papel else "")
                  + (f", {resultado.cadernos} cadernos" if resultado.cadernos else "") + "."]
        if destino:
            partes.append(f"Gravado em: {destino}")
        partes += resultado.instrucoes
        if resultado.conferencia is not None:
            partes.append(resultado.conferencia[1])
        self.estado.setText("\n".join(partes))
        self.avisos.setPlainText("\n".join(a.texto for a in resultado.avisos))
        self.avisos.setVisible(bool(resultado.avisos))

    def _falhou(self, texto: str) -> None:
        self._terminou()
        self.estado.setText(texto)

    def closeEvent(self, evento) -> None:  # noqa: N802
        """Fechar no meio cancela e espera o fio terminar (nada fica pela metade)."""
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(30000)
        super().closeEvent(evento)

    def reject(self) -> None:
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(30000)
        super().reject()
