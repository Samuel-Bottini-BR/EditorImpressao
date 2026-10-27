"""Clica em TODOS os botões de TODAS as telas, de verdade.

Uso:
    python teste_botoes.py               # gera um PDF de teste sozinho (recomendado)
    python teste_botoes.py "livro.pdf"   # usa um PDF à sua escolha
    python teste_botoes.py --com-tela    # mostra as janelas (só para depurar)

**Por padrão, nenhuma janela aparece na tela** (pedido da gerente, 30/09/2026:
rodadas de teste abriam janelas na tela do Samuel): o Qt desenha fora da tela
(`QT_QPA_PLATFORM=offscreen`), a menos que se passe `--com-tela`. E a pasta de
dados do programa é uma pasta própria, `saida_teste/botoes/dados` (apagada e
recriada a cada rodada), para o script não criar projetos na pasta de dados
real (%LOCALAPPDATA%\\EditorImpressao).

**Nunca aponte para um livro do acervo real** (`TESTES EDITOR DE
IMPRESSAO\\LIVROS PARA TESTE`): este script cria, mexe e no fim **apaga** o
projeto correspondente ao PDF usado (é a limpeza do que ele mesmo criou). Os
nove livros do acervo já têm projetos reais de rodadas de teste anteriores -
usar um deles aqui apagaria esse histórico. Foi assim que este script quase
apagou um projeto de 05/08 na primeira tentativa de expandir este arquivo;
por isso, sem argumento, ele gera um PDF sintético de duas páginas, isolado.

Aqui os controles são acionados por `botao.click()` / `acao.trigger()`,
passando pelo sinal `clicked`/`triggered` do Qt, e não chamando o método
Python direto. Um erro que só aparece na ligação do sinal - por exemplo o
argumento `checked` que o `clicked` manda junto - escapa do `teste_interface.py`
(que chama métodos internos direto, para validar resultado de ação, não a
fiação do botão) e é pego aqui.

Cobre (desde 06/10/2026 também as escolhas do dividir, item 2.1: "Dividir folhas
ao meio" marcada para a aba Onde cortar aparecer, a lista "Jeito de dividir:",
a caixinha do corte da sobra e a lista "jeito:" da aba Onde cortar):
tela_inicio (busca, área de arrastar, cartão de projeto e seu menu de
contexto), o Automatico (painel e janela grande - desde a etapa 3 da obra,
26/10/2026, no lugar da tela_opcoes, que saiu do caminho), tela_conferir
(como antes: layout e botões de cada aba, cabeçalho/rodapé, redimensionar),
tela_ampliada (zoom, navegação, comparar, filtros), janela_confirmar (escolher
pasta, nome, processar), tela_final (abrir pasta, imprimir, fazer outro), e o
menu (Arquivo/Editar/Marcar/Filtro/Página/Ver/Ajuda).

**Diálogos nativos são substituídos por respostas fixas** (ver `_MONKEYPATCHES`
mais abaixo) para o script não travar esperando alguém clicar num `QFileDialog`
de verdade, e para não mandar nada para a impressora física nem abrir o
Explorer de verdade. Isso é intencional: o que se testa aqui é a ligação do
programa com esses diálogos, não os diálogos do próprio Windows.

**Diferença importante para quem for expandir:** `botao.click()` dispara o
slot conectado, mas se esse slot levantar uma exceção, ela NÃO propaga para um
`try/except` em volta do `.click()` - vai direto para `sys.excepthook`, e o
processo continua como se nada tivesse acontecido. Por isso as falhas aqui são
detectadas por um `sys.excepthook` global (grava em `saida_teste/botoes/falhas.log`
e conta), não por `try/except` ao redor do clique.

**Não coberto de propósito, por enquanto:** "continuar" e "começar de novo" no
cartão de projeto (reentram no fluxo principal, que já é testado pela
abertura via área de arrastar); `teste_ampliar.py` continua sendo o teste
mais detalhado do zoom/arrasto.

**Coberto desde 02/10/2026:** a caixa "Já existe um arquivo com esse nome"
(`_perguntar_sobre_substituir`). Antes de processar, o script deixa na pasta
de destino um PDF com o mesmo nome; a resposta automática às caixas clica a
opção de AcceptRole, que ali é "salvar como ... (2).pdf". Confere que o
`(2)` foi gerado e o antigo ficou intacto. Bug que isso pega: esse botão
chamava um seletor de destino que não existe mais na tela Conferir, e o PDF
não era gerado (Lista de bugs, 02/10/2026).
"""

from __future__ import annotations

import os
import shutil
import sys
import time
import traceback
from pathlib import Path

# Antes de importar o Qt e o programa: sem janela na tela e pasta de dados
# propria (ver o topo). O Qt le QT_QPA_PLATFORM ao criar a QApplication; o
# programa le LOCALAPPDATA a cada gravacao (historico.pasta_de_dados).
if "--com-tela" in sys.argv:
    sys.argv.remove("--com-tela")
else:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
_DADOS_DO_TESTE = Path(__file__).resolve().parent / "saida_teste" / "botoes" / "dados"
shutil.rmtree(_DADOS_DO_TESTE, ignore_errors=True)       # criada por este script
_DADOS_DO_TESTE.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS_DO_TESTE)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QInputDialog,
    QLayout,
    QMessageBox,
    QPushButton,
    QWidget,
)

import historico

try:  # saida sem buffer: sem isso, um travamento nao mostra nada ate matar o processo
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

PASTA_DE_SAIDA_DO_TESTE = Path(__file__).resolve().parent / "saida_teste" / "botoes"
CAMINHO_DO_LOG = PASTA_DE_SAIDA_DO_TESTE / "falhas.log"


# ---------------------------------------------------------------------------
# excepthook global: pega exceção de dentro de um slot que .click()/.trigger()
# não propaga (ver docstring do módulo).
# ---------------------------------------------------------------------------

_falhas: list[str] = []
_contexto_atual = "(antes de qualquer ação)"


def _excepthook(tipo, valor, tb) -> None:
    linha = f"{_contexto_atual}: {tipo.__name__}: {valor}"
    _falhas.append(linha)
    print(f"  FALHA (exceção) em {_contexto_atual}")
    print(f"        {tipo.__name__}: {valor}")
    PASTA_DE_SAIDA_DO_TESTE.mkdir(parents=True, exist_ok=True)
    with CAMINHO_DO_LOG.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"=== {_contexto_atual} ===\n")
        arquivo.write("".join(traceback.format_exception(tipo, valor, tb)))
        arquivo.write("\n")


sys.excepthook = _excepthook


def esperar(segundos: float, condicao=None) -> bool:
    """Bombeia o loop de eventos do Qt ate `segundos` passarem ou `condicao`
    ficar verdadeira (o que vier primeiro). Devolve se a condicao foi atendida."""
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao is not None and condicao():
            return True
        time.sleep(0.02)
    return condicao() if condicao else True


def acionar(controle, rotulo: str) -> bool:
    """Clica (QPushButton) ou aciona (QAction) de verdade, e diz se passou.

    "Passou" aqui quer dizer "não apareceu nenhuma exceção nova no
    sys.excepthook" - um `.click()`/`.trigger()` sempre "funciona" do ponto
    de vista do Qt mesmo quando o slot conectado quebra por dentro.
    """
    global _contexto_atual
    _contexto_atual = f"clique em '{rotulo}'"
    antes = len(_falhas)
    if hasattr(controle, "trigger"):
        controle.trigger()
    else:
        controle.click()
    QApplication.processEvents()
    esperar(0.3)
    ok = len(_falhas) == antes
    if ok:
        print(f"  ok    {_contexto_atual}")
    return ok


def trocar_combo(combo, rotulo: str) -> bool:
    """Escolhe o proximo item de uma lista (QComboBox), como a pessoa faria,
    e diz se passou (nenhuma excecao nova no sys.excepthook). Item 2.1
    (06/10/2026): as listas do dividir."""
    global _contexto_atual
    _contexto_atual = f"trocar a lista '{rotulo}'"
    antes = len(_falhas)
    combo.setCurrentIndex((combo.currentIndex() + 1) % combo.count())
    QApplication.processEvents()
    esperar(0.3)
    ok = len(_falhas) == antes
    if ok:
        print(f"  ok    {_contexto_atual} -> '{combo.currentText()}'")
    return ok


def botoes_de(widget: QWidget) -> list[QPushButton]:
    """Todos os QPushButton visíveis e habilitados dentro de `widget` (recursivo)."""
    return [b for b in widget.findChildren(QPushButton) if b.isVisible() and b.isEnabled()]


def clicar_todos_os_botoes_de(widget: QWidget) -> tuple[int, int]:
    """Clica em cada QPushButton visível/habilitado de `widget`. Devolve (ok, falhas)."""
    ok = falhas = 0
    for botao in botoes_de(widget):
        rotulo = botao.text() or botao.toolTip() or botao.objectName() or "(sem texto)"
        if acionar(botao, rotulo):
            ok += 1
        else:
            falhas += 1
    return ok, falhas


# ---------------------------------------------------------------------------
# checagem de layout - só a tela de conferir tem o empilhamento complexo que
# já causou sobreposição de verdade; as outras telas usam grade/coluna simples.
# ---------------------------------------------------------------------------


def faixas_da_tela(conferir: QWidget) -> list[tuple[str, QWidget]]:
    """As linhas do empilhamento principal, de cima para baixo."""
    camada = conferir.layout()
    linhas: list[tuple[str, QWidget]] = []
    if camada is None:
        return linhas

    for i in range(camada.count()):
        item = camada.itemAt(i)
        if item.widget() is not None:
            widget = item.widget()
            nome = widget.objectName() or type(widget).__name__
            linhas.append((nome, widget))
        elif item.layout() is not None:
            # cabecalho e rodape sao layouts; conferimos os widgets deles
            for j in range(item.layout().count()):
                sub = item.layout().itemAt(j)
                if sub.widget() is not None:
                    w = sub.widget()
                    linhas.append((w.objectName() or w.text() if isinstance(w, QPushButton)
                                   else type(w).__name__, w))
    return linhas


def sobreposicoes(conferir: QWidget) -> list[str]:
    """Acha linhas do empilhamento cujos retangulos se cruzam.

    Num QVBoxLayout isso nunca deveria acontecer: cada faixa fica na sua
    altura. Se acontecer, alguma coisa esta desenhada por cima do conteúdo.
    """
    problemas: list[str] = []
    linhas = faixas_da_tela(conferir)

    for i, (nome_a, a) in enumerate(linhas):
        for nome_b, b in linhas[i + 1:]:
            if a.parent() is not b.parent() or not (a.isVisible() and b.isVisible()):
                continue
            cruz = a.geometry().intersected(b.geometry())
            if cruz.width() > 2 and cruz.height() > 2:
                problemas.append(
                    f"{nome_a} {a.geometry().getRect()} cruza "
                    f"{nome_b} {b.geometry().getRect()} em {cruz.getRect()}"
                )
    return problemas


def ordem_correta(conferir: QWidget) -> list[str]:
    """Confere se as linhas aparecem na ordem pedida, de cima para baixo."""
    problemas: list[str] = []
    alvos = []
    for nome, widget in faixas_da_tela(conferir):
        if nome in ("QStackedWidget", "TiraMiniaturas", "QFrame", "cartao") or \
                nome.startswith("faixa"):
            alvos.append((nome, widget.geometry().top(), widget.geometry().bottom()))

    for i in range(len(alvos) - 1):
        nome_a, _, base_a = alvos[i]
        nome_b, topo_b, _ = alvos[i + 1]
        if topo_b < base_a:
            problemas.append(f"{nome_b} comeca antes de {nome_a} terminar")
    return problemas


# ---------------------------------------------------------------------------
# monkeypatches: nenhum diálogo nativo do SO abre de verdade neste teste, e
# nada é mandado para a impressora física nem para o Explorer de verdade.
# ---------------------------------------------------------------------------


def _instalar_monkeypatches(caminho_pdf: str) -> None:
    """Troca os diálogos nativos do Qt (arquivo, pasta, mensagem, entrada) e
    as ações de abrir_pasta/imprimir por versões falsas, para o teste
    conseguir clicar em tudo sem travar esperando um clique humano de
    verdade e sem mandar nada para o Explorer/impressora reais. Ver a
    ressalva no docstring do módulo sobre QMessageBox.exec() precisar de
    tratamento especial."""
    pasta_destino = PASTA_DE_SAIDA_DO_TESTE / "destino_escolhido"
    if pasta_destino.exists():
        shutil.rmtree(pasta_destino)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (caminho_pdf, "Arquivos PDF (*.pdf)"))
    QFileDialog.getExistingDirectory = staticmethod(
        lambda *a, **k: str(pasta_destino))
    QMessageBox.question = staticmethod(
        lambda *a, **k: QMessageBox.Yes)
    QMessageBox.warning = staticmethod(lambda *a, **k: QMessageBox.Ok)
    QMessageBox.information = staticmethod(lambda *a, **k: QMessageBox.Ok)

    # Qualquer QMessageBox construído na mão (self.avisar(), _mostrar_atalhos,
    # "ainda há páginas não conferidas", etc.) chama .exec() na instância, não
    # a função estática acima - sem isso, a primeira caixa desse tipo trava o
    # script para sempre.
    #
    # Fechar com .close() (sem clicar em nada) NÃO equivale a "cancelar": o Qt
    # trata como se o botão de RejectRole tivesse sido clicado. Numa caixa
    # tipo "conferir" / "processar assim mesmo", isso escolhe sempre
    # "conferir" e o fluxo nunca avança - por isso aqui se clica de propósito
    # no botão de AcceptRole quando ele existir (a opção que segue em frente),
    # e só fecha sem clicar quando a caixa só tem um botão informativo.
    _exec_original_caixa = QMessageBox.exec

    def _resolver_caixa(self) -> None:
        aceitar = next(
            (b for b in self.buttons() if self.buttonRole(b) == QMessageBox.AcceptRole),
            None)
        if aceitar is not None:
            aceitar.click()
        else:
            self.close()

    def _exec_caixa_sem_travar(self):
        QTimer.singleShot(0, lambda: _resolver_caixa(self))
        return _exec_original_caixa(self)

    QMessageBox.exec = _exec_caixa_sem_travar

    # A tela de Configurações também é modal (.exec()) - mesma técnica das
    # duas acima, senão o clique em "menu: configuracoes" trava o script.
    from ui.tela_configuracoes import TelaConfiguracoes

    _exec_original_configuracoes = TelaConfiguracoes.exec

    def _interagir_com_configuracoes(dialogo) -> None:
        restaurar = next(
            (b for b in dialogo.findChildren(QPushButton)
             if "restaurar" in b.text().lower()), None)
        if restaurar is not None:
            restaurar.click()
        fechar = next(
            (b for b in dialogo.findChildren(QPushButton)
             if b.text().lower() == "fechar"), None)
        if fechar is not None:
            fechar.click()
        else:
            dialogo.close()

    def _exec_configuracoes_sem_travar(self):
        QTimer.singleShot(0, lambda: _interagir_com_configuracoes(self))
        return _exec_original_configuracoes(self)

    TelaConfiguracoes.exec = _exec_configuracoes_sem_travar

    # A lista dos avisos ("Antes de processar" e o seletor do painel "Para
    # revisar", 12/10/2026) também é modal: antes era um QMessageBox, que a
    # técnica de cima já resolvia. Aqui se clica no botão que segue em frente
    # ("continuar assim mesmo", ou "fechar" no seletor).
    from ui.janela_dos_avisos import JanelaDosAvisos

    _exec_original_avisos = JanelaDosAvisos.exec

    def _exec_avisos_sem_travar(self):
        QTimer.singleShot(0, self.botao_continuar.click)
        return _exec_original_avisos(self)

    JanelaDosAvisos.exec = _exec_avisos_sem_travar

    # O diálogo "tamanho..." (Problema 1, opção A) também é modal.
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha

    _exec_original_tamanho = DialogoTamanhoDaFolha.exec

    def _interagir_com_tamanho(dialogo) -> None:
        botao_a5 = next(
            (b for b in dialogo.findChildren(QPushButton) if b.text() == "A5"), None)
        if botao_a5 is not None:
            botao_a5.click()
        dialogo.accept()

    def _exec_tamanho_sem_travar(self):
        QTimer.singleShot(0, lambda: _interagir_com_tamanho(self))
        return _exec_original_tamanho(self)

    DialogoTamanhoDaFolha.exec = _exec_tamanho_sem_travar

    # A tela cheia dos filtros (etapa 6 do layout) tambem e modal: clica nos
    # filtros da fila, liga e desliga o "Comparar com o Original" e fecha sem
    # mudar (o "Usar" e conferido em tests/test_filtros_tela_cheia.py).
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    _exec_original_tela_cheia = FiltrosEmTelaCheia.exec

    def _interagir_com_a_tela_cheia(dialogo) -> None:
        for cartao in list(dialogo.cartoes.values()):
            dialogo.escolher(cartao.chave)
        dialogo.chave_comparar.click()
        dialogo.chave_comparar.click()
        dialogo.botao_sem_mudar.click()

    def _exec_tela_cheia_sem_travar(self):
        QTimer.singleShot(0, lambda: _interagir_com_a_tela_cheia(self))
        return _exec_original_tela_cheia(self)

    FiltrosEmTelaCheia.exec = _exec_tela_cheia_sem_travar
    # A janela "Em quais páginas?" do "usar em todas" do Cortar (item 2.13)
    # também é modal: clica "Nenhuma", "Selecionar todas" e aplica.
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    _exec_original_paginas = DialogoEscolherPaginas.exec

    def _interagir_com_paginas(dialogo) -> None:
        dialogo.botao_nenhuma.click()
        dialogo.botao_todas.click()
        dialogo.accept()

    def _exec_paginas_sem_travar(self):
        QTimer.singleShot(0, lambda: _interagir_com_paginas(self))
        return _exec_original_paginas(self)

    DialogoEscolherPaginas.exec = _exec_paginas_sem_travar

    QInputDialog.getText = staticmethod(
        lambda *a, **k: ("Projeto de teste (renomeado)", True))
    QInputDialog.getInt = staticmethod(
        lambda self, titulo, rotulo, valor=1, minimo=0, maximo=100, passo=1, *a, **k: (valor, True))
    # Desde 30/09 o programa pede texto e numero por ui/perguntas.py (botoes
    # em portugues), que abre um QInputDialog modal: respostas fixas aqui
    # tambem, senao o script trava esperando alguem digitar.
    import ui.perguntas as perguntas_da_interface

    perguntas_da_interface.pedir_texto = (
        lambda *a, **k: ("Projeto de teste (renomeado)", True))
    perguntas_da_interface.pedir_numero = (
        lambda pai, titulo, rotulo, valor, minimo, maximo: (valor, True))

    def _abrir_pasta_falso(caminho) -> None:
        print(f"  (interceptado: abrir_pasta não abriu o Explorer de verdade - {caminho})")

    def _imprimir_falso(caminho) -> bool:
        print(f"  (interceptado: imprimir não mandou nada para a impressora - {caminho})")
        return True

    historico.abrir_pasta = _abrir_pasta_falso
    historico.imprimir = _imprimir_falso


# ---------------------------------------------------------------------------
# telas
# ---------------------------------------------------------------------------


def testar_tela_inicial(janela, caminho_pdf: str) -> tuple[int, int]:
    """Testa a busca, o clique na área de arrastar (abre o PDF de teste via
    o QFileDialog mockado), o menu no estado "tela inicial" e o
    redimensionamento. Devolve (quantos passaram, quantos falharam)."""
    from ui.janela_principal import CONFERIR

    print("\n--- tela inicial ---")
    ok = falhas = 0
    inicio = janela.tela_inicio

    # a busca
    global _contexto_atual
    _contexto_atual = "digitar na busca"
    QTest.keyClicks(inicio.busca, "nenhum-projeto-deveria-ter-este-nome")
    esperar(0.2)
    inicio.busca.clear()
    esperar(0.2)
    print("  ok    busca (digitar e limpar)")
    ok += 1

    # menu, no estado "tela inicial" (so Arquivo/Ver/Ajuda valem), ANTES de
    # abrir o livro: desde a etapa 3 da obra o livro abre direto na area de
    # trabalho, e os menus de la sao conferidos em testar_conferir_e_ampliada.
    # "miniaturas" e "icones" (menu Ver, rodada 14 do layout) escondem a tira
    # e os icones da direita: acionados aqui, os passos seguintes nao os
    # achariam. Sao conferidos em tests/test_menu_paineis.py.
    o, f = acionar_menu_habilitado(janela, excluir={"abrir", "sair", "miniaturas", "icones",
                                                    "filtros_tela_cheia", "lado_icones",
                                                    "lado_sanfona", "automatico"})
    ok += o
    falhas += f

    # a area de arrastar - abre o dialogo (mockado para devolver o PDF de teste).
    # Etapa 3 da obra (D-002, Kaique 22/09: "nós tínhamos que abrir direto na
    # área de trabalho"): a promessa e o livro ir DIRETO para a area de trabalho.
    _contexto_atual = "clique na área de arrastar"
    antes = len(_falhas)
    QTest.mouseClick(inicio.area, Qt.LeftButton)
    if not esperar(20, lambda: janela.telas.currentIndex() == CONFERIR):
        falhas += 1
        print("  FALHA área de arrastar não levou o livro à área de trabalho")
    elif len(_falhas) != antes:
        falhas += 1
    else:
        ok += 1
        print("  ok    área de arrastar abriu o PDF de teste direto na área de trabalho")

    # Item 1.1: livro com camadas aberto pela primeira vez -> o aviso "Este
    # livro tem fundo separado. Quer tirar o fundo?". Responde "Sim" clicando
    # o botao de verdade, e confere que o filtro do livro virou "Tirar o
    # fundo" (o resto do teste, entao, confere com o filtro novo).
    o, f = responder_aviso_do_fundo(janela)
    ok += o
    falhas += f

    # redimensionar, so para confirmar que nao trava
    o, f = redimensionar_sem_quebrar(janela, TAMANHOS_PEQUENOS)
    ok += o
    falhas += f
    return ok, falhas


def responder_aviso_do_fundo(janela) -> tuple[int, int]:
    """Item 1.1: se a janela abriu o aviso de livro com camadas
    (janela.aviso_do_fundo), clica "Sim, tirar o fundo" e confere que o
    filtro do livro virou "Tirar o fundo". Sem camadas, confere que o aviso
    NAO apareceu (nunca pergunta em livro sem camadas)."""
    from core.filtros import TIRAR_FUNDO
    from PySide6.QtWidgets import QAbstractButton

    global _contexto_atual
    esperar(0.3)
    caixa = janela.aviso_do_fundo
    tem_camadas = bool(janela.projeto is not None and janela.projeto.tem_camadas)
    if caixa is None:
        if tem_camadas:
            _contexto_atual = "aviso de livro com camadas"
            print("  FALHA livro com camadas aberto pela primeira vez e o aviso não apareceu"
                  " (se o projeto de teste já existia de uma rodada anterior, é esperado)")
            return 0, 1
        print("  ok    sem camadas: o aviso 'Quer tirar o fundo?' não apareceu")
        return 1, 0
    if not tem_camadas:
        print("  FALHA o aviso 'Quer tirar o fundo?' apareceu num livro sem camadas")
        return 0, 1
    print(f"  (aviso: {caixa.text()})")
    sim = next((b for b in caixa.findChildren(QAbstractButton)
                if b.text() == "Sim, tirar o fundo"), None)
    if sim is None:
        print("  FALHA o aviso não tem o botão 'Sim, tirar o fundo'")
        return 0, 1
    if not acionar(sim, "Sim, tirar o fundo"):
        return 0, 1
    # etapa 3 da obra: o livro ja esta na area de trabalho; o "Sim" vale na hora
    certo = (janela.aviso_do_fundo is None
             and janela.projeto.filtro_padrao == TIRAR_FUNDO and janela.projeto.limpar
             and any(p.filtro == TIRAR_FUNDO for p in janela.projeto.paginas))
    if certo:
        print("  ok    'Sim' deixou o livro inteiro em 'Tirar o fundo'")
        return 2, 0
    print(f"  FALHA depois do 'Sim' o filtro do livro ficou {janela.projeto.filtro_padrao}")
    return 1, 1


def testar_automatico(janela, caminho_pdf: str) -> tuple[int, int]:
    """Etapa 3 da obra (26/10/2026; D-002, D-003, D-005, D-018, D-068, D-071, D-334): o
    livro abriu direto na area de trabalho; aqui o painel Automatico e a janela grande,
    clicados de verdade, com a PROMESSA de cada coisa conferida (D-010: "o botão tem que
    ser provado que ele faz o que se diz que se faz"): a caixinha marca a etapa, o
    arrastar muda a ordem, cada opcao muda a escolha, "escolher páginas..." escolhe na
    grade, "Salvar receita..." guarda, e "Rodar" liga as etapas no livro (numa acao do
    desfazer). O "Rodar" e o antigo "Conferir" da bateria."""
    from core import automatico as A
    from core import perfis
    from PySide6.QtCore import QModelIndex
    from PySide6.QtWidgets import QCheckBox, QComboBox, QRadioButton
    from ui.janela_principal import CONFERIR

    global _contexto_atual
    print("\n--- Automático (painel e janela grande) ---")
    ok = falhas = 0

    def promessa(certo: bool, texto: str) -> None:
        nonlocal ok, falhas
        if certo:
            ok += 1
            print(f"  ok    {texto}")
        else:
            falhas += 1
            print(f"  FALHA {texto}")
            _falhas.append(f"promessa: {texto}")

    tela = janela.tela_conferir
    promessa(janela.telas.currentIndex() == CONFERIR, "o livro está na área de trabalho")
    promessa(not hasattr(janela, "tela_opcoes"), "a tela 'O que fazer' não existe mais")
    promessa(tela.aviso_do_livro_novo.isVisible(), "aviso 'Livro novo: ainda não passou pelo automático'")

    # o painel
    tela.paineis.mostrar_painel("automatico", True)
    esperar(0.3)
    painel = tela.paineis.automatico
    estado = painel.estado
    lista = painel.lista
    for linha in range(lista.count()):
        item = lista.item(linha)
        etapa = item.data(Qt.UserRole)
        for vez in range(2):
            _contexto_atual = f"caixinha da etapa '{A.NOMES[etapa]}' ({vez + 1}a vez)"
            antes = etapa in estado.marcadas
            item = lista.item_da_etapa(etapa)
            item.setCheckState(Qt.Unchecked if antes else Qt.Checked)
            esperar(0.1)
            promessa((etapa in estado.marcadas) != antes, f"a caixinha liga e desliga '{A.NOMES[etapa]}'")
    _contexto_atual = "arrastar a etapa 3 para o primeiro lugar"
    antes = list(estado.ordem)
    lista.model().moveRow(QModelIndex(), 2, QModelIndex(), 0)
    esperar(0.3)
    promessa(estado.ordem[0] == antes[2], "arrastar muda a ordem em que as etapas rodam (D-003)")
    lista.model().moveRow(QModelIndex(), 0, QModelIndex(), 3)
    esperar(0.3)
    promessa(estado.ordem == antes, "arrastar de volta devolve a ordem")
    for _ in range(painel.combo_alcance.count()):
        if trocar_combo(painel.combo_alcance, "Rodar em"):
            ok += 1
        else:
            falhas += 1
    estado.definir_alcance("livro")

    # o aviso do livro novo abre a janela grande com a receita de sempre (D-018)
    if acionar(tela.botao_rodar_do_aviso, "Rodar o automático… (aviso do livro novo)"):
        ok += 1
    else:
        falhas += 1
    jan = janela.janela_do_automatico
    promessa(jan is not None and jan.isVisible(), "o aviso abriu a janela grande do Automático")
    if jan is None:
        return ok, falhas
    de_sempre = set(perfis.etapas_da_receita(perfis.ler(perfis.receita_de_sempre())))
    promessa(estado.marcadas == de_sempre, "a receita de sempre veio marcada (D-018)")
    promessa(not janela.projeto.endireitar, "nada mudou no livro antes de Rodar")

    # cada etapa e cada opção da janela
    for etapa in A.ETAPAS:
        jan.mostrar_etapa(etapa)
        esperar(0.1)
        promessa(jan.pilha.currentWidget() is jan.paginas_das_etapas[etapa],
                 f"'{A.NOMES[etapa]}' mostra as opções dela")
    for campo, controle in sorted(jan.controles.items()):
        if campo.startswith("misto_") or campo == "filtro_padrao":
            continue
        if isinstance(controle, QCheckBox):
            for vez in range(2):
                if acionar(controle, f"{controle.text()} ({vez + 1}a vez)"):
                    ok += 1
                else:
                    falhas += 1
        elif isinstance(controle, QComboBox):
            for _ in range(controle.count()):
                if trocar_combo(controle, campo):
                    ok += 1
                else:
                    falhas += 1
    for chave, radio in jan.radios_de_filtro.items():
        if radio.isHidden():
            continue
        if acionar(radio, f"filtro do livro: {radio.text()}"):
            ok += 1
        else:
            falhas += 1
        promessa(estado.opcoes.get("filtro_padrao") == chave, f"o filtro do livro vira {radio.text()}")
    jan.radios_de_filtro["preto_e_branco"].setChecked(True)
    if acionar(jan.escolhas_misto.caixa, "Só as letras"):
        ok += 1
    promessa("só as letras" in jan.frase.text() or "Só as letras" in jan.frase.text()
             or "letras" in jan.frase.text(), "a frase de baixo diz o que o 'Só as letras' faz")
    jan.escolhas_misto.caixa.setChecked(False)

    # "escolher páginas..." -> a grade escolhe -> a janela volta (rodada 2, D-334)
    if acionar(jan.botao_escolher, "escolher páginas..."):
        ok += 1
    grade = tela.todas
    promessa(tela.pilha_da_tela.currentWidget() is grade and grade.para_o_automatico,
             "'escolher páginas...' abriu a grade no jeito de escolher")
    grade.marcar(0)
    if acionar(grade.botao_usar, "usar esta página (grade)"):
        ok += 1
    promessa(estado.alcance == "escolhidas" and estado.escolhidas == [0],
             "a grade devolveu a página escolhida ao Automático")
    jan = janela.janela_do_automatico
    promessa(jan is not None and jan.isVisible(), "a janela grande voltou")
    estado.definir_alcance("livro")

    # "Salvar receita..." (D-071): a caixa diz o que vai dentro e guarda
    if acionar(jan.botao_salvar, "Salvar receita..."):
        ok += 1
    caixa = getattr(janela, "caixa_da_receita", None)
    promessa(caixa is not None and caixa.isVisible(), "a caixa da receita abriu")
    if caixa is not None:
        caixa.nome.setText("Receita do teste de botões")
        if acionar(caixa.botao_guardar, "guardar (caixa da receita)"):
            ok += 1
        promessa(perfis.ler("Receita do teste de botões") is not None, "a receita foi guardada")
        perfis.apagar("Receita do teste de botões")

    # Rodar: Endireitar, Cortar e Limpar em Mágico pro, no livro todo
    estado.marcadas = {A.ENDIREITAR, A.CORTAR, A.LIMPAR}
    jan.radios_de_filtro["magico_pro"].setChecked(True)
    feitas = len(janela.acoes.feitas)
    if acionar(jan.botao_rodar, jan.botao_rodar.text()):
        ok += 1
    else:
        falhas += 1
    esperar(180, lambda: janela.telas.currentIndex() == CONFERIR and (
        janela.tarefa is None or not janela.tarefa.isRunning()))
    esperar(0.5)
    p = janela.projeto
    promessa(p.endireitar and p.cortar_bordas and p.limpar and p.filtro_padrao == "magico_pro",
             "Rodar ligou as etapas marcadas no livro (Mágico pro)")
    promessa(len(janela.acoes.feitas) == feitas + 1, "o Automático virou uma ação do desfazer")
    promessa(not tela.aviso_do_livro_novo.isVisible(), "o aviso do livro novo sumiu depois de rodar")
    return ok, falhas


def testar_conferir_e_ampliada(janela) -> tuple[int, int]:
    """Para cada aba ativa da tela de conferir: confere que o layout não tem
    sobreposição nem ordem trocada, e clica em todos os botões da area de
    imagem e da barra de botões daquela aba. Depois clica cabeçalho/rodapé,
    redimensiona em vários tamanhos grandes conferindo layout em cada aba, o
    menu, e por fim a tela ampliada (`testar_tela_ampliada`)."""
    ok = falhas = 0
    conferir = janela.tela_conferir
    esperar(2.0)

    for indice, aba in enumerate(conferir._abas_ativas):
        conferir.barra_abas.setCurrentIndex(indice)
        esperar(1.5)

        print(f"\n--- aba '{aba}' ---")
        dizer_as_paginas(conferir, "ao entrar")

        problemas = sobreposicoes(conferir) + ordem_correta(conferir)
        if problemas:
            falhas += 1
            print("  LAYOUT SOBREPOSTO:")
            for p in problemas:
                print(f"    {p}")
        else:
            ok += 1
            print("  layout: sem sobreposicao, ordem correta")

        alvos = list(botoes_de(conferir.area_imagem.currentWidget()))
        alvos += list(botoes_de(conferir.barra_botoes.currentWidget()))
        # Etapa 3 do layout (12/10/2026): os botoes de Dividir, Cortar e
        # Endireitar sairam da fila embaixo da pagina e moram no painel
        # Propriedades: abre o painel e clica nos botoes e nas caixinhas dele
        # (Espelhado, Proporcao travada). Fica de fora so o "mudar nas opções
        # do livro...", que sai desta tela (o "voltar" ja e conferido na tela
        # "O que fazer").
        if hasattr(conferir, "paineis") and hasattr(conferir.paineis, "abrir"):
            conferir.paineis.abrir("props")
            esperar(0.4)
            corpo = conferir.paineis.propriedades.corpo
            # Etapa 2 da obra: os dois botoes de "Esta pagina" (no alto do
            # Propriedades, em toda ferramenta) ficam de fora daqui - clicados
            # em cada ferramenta, a pagina sumiria do livro de duas paginas.
            # Sao conferidos uma vez, com a promessa, em
            # testar_os_dois_botoes_da_pagina.
            da_pagina = {getattr(conferir, "botao_em_branco", None),
                         getattr(conferir, "botao_tirar_do_livro", None)}
            alvos += [b for b in botoes_de(corpo)
                      if not (b.text() or "").startswith("mudar nas opções")
                      and b not in da_pagina]
            alvos += [c for c in corpo.findChildren(QCheckBox)
                      if c.isVisible() and c.isEnabled()]
        # O "está certo" e a sugestao laranja, que cada fila tinha, sao agora
        # os da faixa do conferir. Sao clicados NAS MESMAS ferramentas e NA
        # MESMA ORDEM de quando moravam nas filas ("está certo" primeiro, em
        # Dividir, Cortar e Endireitar; a sugestao por ultimo, menos no
        # Marcar, que nunca teve): a bateria conta com isso. A sugestao
        # "apagar esta página" de uma ferramenta e desfeita pelo "restaurar
        # página" de outra, e um clique a mais ou a menos deixa o livro de
        # teste (duas paginas) sem nenhuma para processar. O "próxima dúvida"
        # (que troca de pagina) e clicado em testar_paineis_da_direita.
        if hasattr(conferir, "faixa"):
            if aba in ("corte", "bordas", "angulo") and conferir.botao_esta_certo.isVisible():
                alvos.insert(0, conferir.botao_esta_certo)
            sugestao = conferir.botao_sugestao
            if aba != "marcar" and sugestao.isVisible() and sugestao.isEnabled():
                alvos.append(sugestao)
            # O segundo e o terceiro botao do aviso ("Para revisar", junção
            # com o layout em 20/10/2026: moram na faixa, ao lado do primeiro).
            # O que eles apagam ou deixam em branco volta antes de processar
            # (_devolver_as_paginas_apagadas).
            for extra in (getattr(conferir, "botao_sugestao_2", None),
                          getattr(conferir, "botao_sugestao_3", None)):
                if (aba != "marcar" and extra is not None and extra.isVisible()
                        and extra.isEnabled()):
                    alvos.append(extra)
        # Item 2.3 (06/10/2026): os tres botoes de girar, na linha das abas
        # (ui/widgets/barra_girar.py), valem em todas as abas.
        if hasattr(conferir, "barra_girar"):
            alvos += list(botoes_de(conferir.barra_girar))
        # Etapa 3 do layout: os tres botoes pequenos de girar do canto da
        # area da pagina (giram so esta folha).
        if hasattr(conferir, "girar_do_canto"):
            alvos += list(botoes_de(conferir.girar_do_canto))
        # Item 2.1: a lista "jeito:" da aba Onde cortar (ida e volta; numa
        # folha em pe ela fica apagada e trocar nao faz nada - so nao pode quebrar)
        if aba == "corte" and hasattr(conferir, "combo_jeito_da_folha"):
            for _ in range(conferir.combo_jeito_da_folha.count()):
                if trocar_combo(conferir.combo_jeito_da_folha, "jeito (desta folha)"):
                    ok += 1
                else:
                    falhas += 1
        for botao in alvos:
            rotulo = botao.text() or "(sem texto)"

            # Item 2/4 do teste do Boecio (secao 3a do plano): o botao
            # "tamanho..." (aba Bordas) NAO PODE mais mexer no recorte que o
            # usuario ja fez - so no tamanho de folha. Este e o unico jeito de
            # pegar o bug de verdade: `.click()` passa pelo sinal `clicked` do
            # Qt de ponta a ponta, dialogo modal incluido (ver
            # _instalar_monkeypatches / DialogoTamanhoDaFolha.exec acima).
            confere_recorte = aba == "bordas" and rotulo == "tamanho..."
            if confere_recorte:
                pagina_antes = conferir.projeto.paginas[conferir.indice_pagina]
                recorte_antes = pagina_antes.recorte

            if acionar(botao, rotulo):
                ok += 1
            else:
                falhas += 1

            if confere_recorte:
                pagina_depois = conferir.projeto.paginas[conferir.indice_pagina]
                if pagina_depois.recorte == recorte_antes:
                    ok += 1
                    print(f"  ok    'tamanho...' nao mexeu no recorte do usuario "
                          f"(continua {recorte_antes})")
                else:
                    falhas += 1
                    print(f"  REGRESSAO: 'tamanho...' mudou o recorte do usuario "
                          f"({recorte_antes} -> {pagina_depois.recorte})")
                if pagina_depois.tamanho_folha_cm is None:
                    falhas += 1
                    print("  REGRESSAO: 'tamanho...' nao registrou tamanho_folha_cm")
                else:
                    ok += 1
                    print(f"  ok    tamanho_folha_cm registrado: "
                          f"{pagina_depois.tamanho_folha_cm}")

    # O "apagar página" da fila dos filtros deixou a pagina da vez apagada:
    # o mesmo botao, que agora diz "restaurar página", e clicado de volta.
    # Antes do layout sem abas quem equilibrava isso era a ordem dos cliques
    # (as setas "<" e ">" dos lados da pagina, hoje escondidas, levavam a
    # bateria para a segunda pagina, que a sugestao "apagar esta página"
    # apagava e este botao restaurava). Sem isto o livro de teste, de duas
    # paginas, chegava ao "Processar" sem nenhuma: o menu Pagina > Apagar,
    # mais adiante, apaga a outra.
    # Etapa 2 da obra: o botao virou "tirar do livro" / "trazer de volta".
    if (hasattr(conferir, "botao_apagar") and conferir.projeto is not None
            and conferir.projeto.paginas[conferir.indice_pagina].apagada):
        if acionar(conferir.botao_apagar, "trazer de volta (desfaz o tirar do livro da fila)"):
            ok += 1
        else:
            falhas += 1

    o, f = testar_os_dois_botoes_da_pagina(conferir)
    ok += o
    falhas += f

    o, f = testar_cartao_tirar_fundo(conferir)
    ok += o
    falhas += f

    dizer_as_paginas(conferir, "depois das ferramentas")
    print("\n--- cabecalho e rodape (conferir) ---")
    for botao in (conferir.botao_alertas, conferir.botao_desfazer, conferir.botao_refazer):
        if not botao.isEnabled():
            continue
        if acionar(botao, botao.text()):
            ok += 1
        else:
            falhas += 1

    dizer_as_paginas(conferir, "depois do cabecalho")
    o, f = testar_paineis_da_direita(conferir)
    ok += o
    falhas += f
    dizer_as_paginas(conferir, "depois dos paineis")

    print("\n--- redimensionando (conferir) ---")
    for largura, altura in TAMANHOS_GRANDES:
        janela.resize(largura, altura)
        esperar(0.4)
        quebrou = False
        for indice in range(len(conferir._abas_ativas)):
            conferir.barra_abas.setCurrentIndex(indice)
            esperar(0.25)
            problemas = sobreposicoes(conferir) + ordem_correta(conferir)
            if problemas:
                falhas += 1
                print(f"  {largura}x{altura} aba '{conferir.aba_atual}': "
                      f"SOBREPOSTO - {problemas[0]}")
                quebrou = True
                break
        if not quebrou:
            ok += 1
            print(f"  {largura}x{altura}: ok em todas as abas")

    print("\n--- menu (conferir) ---")
    # "comparar" (Ver > "Modo comparar", ligado na etapa 4 do layout) abre a
    # tela grande, que é modal: ela é conferida em testar_tela_ampliada, com
    # o .exec() interceptado; aqui travaria a bateria.
    # Etapa 2 da obra: o "Lado direito" do menu Ver troca o jeito dos paineis
    # e o guarda; e conferido a parte (testar_o_lado_direito), ida e volta.
    o, f = acionar_menu_habilitado(janela, excluir={"processar", "sair", "voltar", "abrir",
                                                    "comparar", "miniaturas", "icones",
                                                    "filtros_tela_cheia", "lado_icones",
                                                    "lado_sanfona", "automatico"})
    ok += o
    falhas += f
    o, f = testar_o_lado_direito(janela)
    ok += o
    falhas += f
    o, f = testar_o_ver_da_barra_de_baixo(conferir)       # etapa 6 da obra
    ok += o
    falhas += f

    dizer_as_paginas(conferir, "depois do menu")
    print("\n--- tela ampliada ---")
    o, f = testar_tela_ampliada(conferir)
    ok += o
    falhas += f

    return ok, falhas


def testar_os_dois_botoes_da_pagina(conferir) -> tuple[int, int]:
    """Etapa 2 da obra (26/10/2026; Samuel, 09/10: "Essa opção de tirar do
    livro ou deixar folha em branco eu quero ter em outras paginas"): os dois
    botoes de "Esta pagina", no alto do painel Propriedades. Clica cada um e
    confere a PROMESSA (a pagina fica em branco / sai do livro), e clica de
    volta ("voltar a página" / "trazer de volta"), para o livro de teste nao
    perder paginas."""
    branco = getattr(conferir, "botao_em_branco", None)
    tirar = getattr(conferir, "botao_tirar_do_livro", None)
    if branco is None or tirar is None or conferir.projeto is None:
        return 0, 0
    print("\n--- os dois botoes de 'Esta pagina' ---")
    ok = falhas = 0
    conferir.trilha.escolher("mao")             # uma ferramenta de pagina (nao o Dividir)
    conferir.paineis.abrir("props")
    esperar(0.4)
    pagina = conferir.projeto.paginas[conferir.indice_pagina]
    for botao, campo, rotulo in ((branco, "em_branco", "deixar em branco"),
                                 (branco, "em_branco", "voltar a página"),
                                 (tirar, "apagada", "tirar do livro"),
                                 (tirar, "apagada", "trazer de volta")):
        antes = bool(getattr(pagina, campo))
        if acionar(botao, rotulo) and bool(getattr(pagina, campo)) != antes:
            ok += 1
            print(f"  ok    '{rotulo}' fez o que diz ({campo}: {antes} -> {not antes})")
        else:
            falhas += 1
            print(f"  FALHA '{rotulo}' nao mudou {campo}")
    return ok, falhas


def testar_o_ver_da_barra_de_baixo(conferir) -> tuple[int, int]:
    """Obra 26/10/2026, etapa 6 (D-015: "Uma página / Duas lado a lado" na
    barra de baixo; desenho decidido: "antes / depois", "– N% +", "ajustar à
    tela"). Clica cada botão e confere a PROMESSA: o que fica no lugar da
    página e o número do zoom. Volta como estava ("Uma página", sem zoom)."""
    if not hasattr(conferir, "botoes_mostrar") or conferir.projeto is None:
        return 0, 0
    print("
--- o ver da barra de baixo (etapa 6) ---")
    from ui.widgets.paginas_rolando import DUAS, UMA

    ok = falhas = 0
    conferir.trilha.escolher("mao")             # uma ferramenta de pagina (nao o Dividir)
    esperar(0.4)

    def conferir_promessa(botao, rotulo, condicao, frase) -> None:
        nonlocal ok, falhas
        if acionar(botao, rotulo) and condicao():
            ok += 1
            print(f"  ok    '{rotulo}': {frase}")
        else:
            falhas += 1
            print(f"  FALHA '{rotulo}' nao fez: {frase}")

    vista = conferir.vista_da_pagina
    conferir_promessa(conferir.botoes_mostrar[DUAS], "Duas lado a lado",
                      lambda: vista.currentWidget() is conferir.lado_a_lado, "os pares no lugar da pagina")
    conferir_promessa(conferir.botoes_mostrar[UMA], "Uma página",
                      lambda: vista.currentWidget() is conferir.area_imagem, "a pagina da ferramenta volta")
    conferir_promessa(conferir.botao_antes_depois, "antes / depois",
                      lambda: vista.currentWidget() is conferir.vista_antes_depois, "o antes e depois")
    conferir_promessa(conferir.botao_antes_depois, "antes / depois (desligar)",
                      lambda: vista.currentWidget() is conferir.area_imagem, "a pagina da ferramenta volta")
    conferir_promessa(conferir.botao_mais_zoom, "+",
                      lambda: conferir.rotulo_do_zoom.text() == "125%", "zoom 125%")
    conferir_promessa(conferir.botao_menos_zoom, "–",
                      lambda: conferir.rotulo_do_zoom.text() == "100%", "zoom 100%")
    conferir_promessa(conferir.botao_mais_zoom, "+ (de novo)",
                      lambda: conferir.rotulo_do_zoom.text() == "125%", "zoom 125%")
    conferir_promessa(conferir.botao_ajustar_a_tela, "ajustar à tela",
                      lambda: conferir.rotulo_do_zoom.text() == "100%", "a pagina inteira (100%)")
    return ok, falhas


def testar_o_lado_direito(janela) -> tuple[int, int]:
    """Etapa 2 da obra (R7 203 D: "Mas eu também quero ter a opção da area de
    trabalho 1"; R14 902 C: menu Ver e Configuracoes): Ver > Lado direito >
    Sanfona poe os paineis em sanfona; Icones na borda volta ao de fabrica."""
    acoes = janela.menu.acoes
    if "lado_sanfona" not in acoes:
        return 0, 0
    paineis = janela.tela_conferir.paineis
    ok = falhas = 0
    for chave, jeito in (("lado_sanfona", "sanfona"), ("lado_icones", "icones")):
        if acionar(acoes[chave], f"menu: {chave}") and paineis.jeito == jeito:
            ok += 1
        else:
            falhas += 1
            print(f"  FALHA menu {chave} nao pos o lado direito em {jeito}")
    return ok, falhas


def dizer_as_paginas(conferir, quando: str) -> None:
    """Escreve quais paginas estao apagadas e quantas vao sair no PDF. A
    bateria clica em "apagar" e "restaurar" em varios lugares, e o livro de
    teste tem poucas paginas: quando ele chega ao "Processar" sem nenhuma,
    estas linhas dizem em que parte isso aconteceu."""
    projeto = conferir.projeto
    if projeto is None:
        return
    apagadas = [p.indice + 1 for p in projeto.paginas if p.apagada]
    print(f"  (paginas {quando}: {len(projeto.paginas)} no livro, apagadas {apagadas}, "
          f"vao sair {len(projeto.paginas_ativas)}; na tela a pagina "
          f"{conferir.indice_pagina + 1})")


def testar_paineis_da_direita(conferir) -> tuple[int, int]:
    """Etapa 3 do layout (12/10/2026): a coluna de icones da direita e os
    paineis que ela abre. Clica de verdade (mouse do Qt em cima do desenho) em
    cada icone, confere que o painel dele abriu ao lado da pagina, clica nos
    botoes do painel (as abas do "Para revisar", desfazer e refazer do
    Historico, o "x") e, por fim, na seta que esconde e mostra os icones.
    Ficam de fora os dois botoes que saem desta tela ("Voltar para as opções"
    e "mudar nas opções do livro...") e as acoes da lista do Historico (cada
    uma desfaria o trabalho ate ali, mudando o que o resto da bateria ve)."""
    global _contexto_atual
    if not hasattr(conferir, "paineis") or not hasattr(conferir.paineis, "icones"):
        return 0, 0
    print("\n--- paineis da direita (conferir) ---")
    ok = falhas = 0
    paineis, icones = conferir.paineis, conferir.paineis.icones
    # Alguns cliques daqui andam de pagina ("próxima dúvida", um motivo do
    # "Para revisar"). No fim a tela volta para a pagina em que estava: o
    # resto da bateria conta com isso (o "apagar" do menu desfaz o "apagar
    # página" clicado antes NA MESMA pagina; em outra, o livro de teste, de
    # duas paginas, ficaria sem nenhuma para processar).
    pagina_de_antes = conferir.indice_pagina
    paineis.fechar()
    esperar(0.2)

    def clicar_no_icone(item: str) -> bool:
        global _contexto_atual
        _contexto_atual = f"clique no icone '{item}' da coluna da direita"
        antes = len(_falhas)
        QTest.mouseClick(icones, Qt.LeftButton, Qt.NoModifier,
                         icones.retangulos()[item].center())
        QApplication.processEvents()
        esperar(0.3)
        return len(_falhas) == antes

    for chave, painel in list(paineis.paineis.items()):
        largura_antes = conferir.area_imagem.width()
        if not clicar_no_icone(chave) or paineis.aberto != chave or not painel.isVisible():
            falhas += 1
            print(f"  FALHA o icone '{chave}' nao abriu o painel dele")
            continue
        if conferir.area_imagem.width() >= largura_antes:
            falhas += 1
            print(f"  FALHA o painel '{chave}' nao empurrou a pagina "
                  f"({largura_antes} -> {conferir.area_imagem.width()})")
            continue
        ok += 1
        print(f"  ok    icone '{chave}': painel aberto ao lado da pagina "
              f"({largura_antes} -> {conferir.area_imagem.width()} de largura)")
        itens_do_historico = set(getattr(painel, "itens", [])) | set(
            getattr(painel, "itens_desfeitos", [])) if chave == "historico" else set()
        fechar = painel.cabecalho.botao_fechar
        feitas_antes = len(conferir.acoes.feitas) if conferir.acoes is not None else 0
        for botao in botoes_de(painel):
            texto = botao.text() or botao.toolTip() or "(sem texto)"
            if botao is fechar or botao in itens_do_historico:
                continue
            # etapa 3 da obra: os botoes do painel Automatico que rodam, abrem a
            # janela grande ou a grade sao conferidos com a promessa em
            # testar_automatico (aqui mudariam o que o resto da bateria ve)
            if texto.startswith(("Voltar para as opções", "mudar nas opções", "mudar no Automático",
                                 "Rodar", "abrir em janela grande", "escolher páginas",
                                 "desligar as marcadas", "Salvar", "ajustar a etapa")):
                continue
            if acionar(botao, f"{texto} (painel {chave})"):
                ok += 1
            else:
                falhas += 1
        # No Historico, "Desfazer" e "Refazer" sao clicados em PAR e
        # conferidos (o laco acima so clica no que estava aceso ao abrir o
        # painel: so o "Desfazer", e a ultima acao da bateria ficava
        # desfeita - era o "restaurar página", e o livro de teste chegava ao
        # "Processar" sem pagina nenhuma).
        if chave == "historico" and conferir.acoes is not None:
            if len(conferir.acoes.feitas) < feitas_antes:
                acionar(painel.botao_refazer, "Refazer (painel historico)")
            if len(conferir.acoes.feitas) == feitas_antes:
                ok += 1
                print("  ok    Desfazer e Refazer do painel: o trabalho ficou como estava")
            else:
                falhas += 1
                print("  FALHA o Refazer do painel Historico nao refez a acao desfeita")
        if acionar(fechar, f"x do painel {chave}") and paineis.aberto is None:
            ok += 1
        else:
            falhas += 1
            print(f"  FALHA o 'x' nao fechou o painel '{chave}'")

    # o "próxima dúvida" da faixa (so anda de pagina; nao muda o trabalho)
    if conferir.botao_proxima_duvida.isEnabled():
        if acionar(conferir.botao_proxima_duvida, "próxima dúvida (faixa)"):
            ok += 1
        else:
            falhas += 1

    # a seta: esconde os icones, e mostra de novo
    for esperado in (False, True):
        if clicar_no_icone("seta") and paineis.icones_a_vista is esperado:
            ok += 1
            print(f"  ok    seta: icones {'a vista' if esperado else 'escondidos'}")
        else:
            falhas += 1
            print(f"  FALHA a seta nao {'mostrou' if esperado else 'escondeu'} os icones")
    conferir.ir_para_pagina(pagina_de_antes)
    esperar(0.3)
    return ok, falhas


def testar_cartao_tirar_fundo(conferir) -> tuple[int, int]:
    """Item 1.1: na aba Filtro de um livro com camadas, espera o cartão
    "Tirar o fundo" mostrar a página de verdade (desenhada em segundo plano) e
    clica nele com o mouse (escolhe o filtro e abre a tela ampliada, que aqui
    fecha sozinha). Confere que a página ficou em "Tirar o fundo". Sem o
    cartão (livro sem camadas), só avisa."""
    from core.filtros import ORIGINAL, TIRAR_FUNDO
    from ui.tela_ampliada import TelaAmpliada

    global _contexto_atual
    cartao = conferir.cartoes.get(TIRAR_FUNDO)
    if cartao is None:
        print("  (sem o cartão 'Tirar o fundo': este livro não tem camadas)")
        return 0, 0
    print("\n--- cartão 'Tirar o fundo' ---")
    ok = falhas = 0
    if "filtro" in conferir._abas_ativas:
        conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("filtro"))
    pagina = conferir.projeto.paginas[conferir.indice_pagina]
    if pagina.filtro == TIRAR_FUNDO:
        # para o cartão ser o desenhado em segundo plano, a página sai do filtro
        conferir._escolher_filtro(ORIGINAL)
    if esperar(60, lambda: cartao.amostra._pixmap is not None):
        ok += 1
        print("  ok    o cartão 'Tirar o fundo' mostrou a página")
    else:
        falhas += 1
        _contexto_atual = "cartão 'Tirar o fundo'"
        print("  FALHA o cartão 'Tirar o fundo' ficou em 'preparando...' por 60 s")

    exec_original = TelaAmpliada.exec

    def exec_fechando(self):
        QTimer.singleShot(200, self.close)
        return exec_original(self)

    TelaAmpliada.exec = exec_fechando
    try:
        _contexto_atual = "clique no cartão 'Tirar o fundo'"
        antes = len(_falhas)
        QTest.mouseClick(cartao, Qt.LeftButton)
        esperar(1.0)
    finally:
        TelaAmpliada.exec = exec_original
    pagina = conferir.projeto.paginas[conferir.indice_pagina]
    if len(_falhas) == antes and pagina.filtro == TIRAR_FUNDO:
        ok += 1
        print("  ok    clique no cartão 'Tirar o fundo' (a página ficou nele)")
    else:
        falhas += 1
        print(f"  FALHA clique no cartão 'Tirar o fundo' (filtro: {pagina.filtro})")
    return ok, falhas


def testar_tela_ampliada(conferir) -> tuple[int, int]:
    """Intercepta o próprio TelaAmpliada.exec() em vez de usar
    QApplication.activeModalWidget() - esse não é confiável sob
    QT_QPA_PLATFORM=offscreen (o diálogo nunca vira "ativo" de verdade, e o
    .exec() trava para sempre esperando um clique que nunca chega)."""
    from ui.tela_ampliada import TelaAmpliada

    resultado = {"ok": 0, "falhas": 0}
    global _contexto_atual

    def _interagir(ampliada) -> None:
        for atributo, rotulo in (("anterior", "<"), ("proxima", ">")):
            botao = getattr(ampliada, atributo, None)
            if botao is not None and botao.isEnabled():
                if acionar(botao, rotulo):
                    resultado["ok"] += 1
                else:
                    resultado["falhas"] += 1

        for botao in botoes_de(ampliada):
            rotulo = botao.text() or botao.toolTip() or "(sem texto)"
            if rotulo == "X":
                continue  # fecha por último
            if acionar(botao, rotulo):
                resultado["ok"] += 1
            else:
                resultado["falhas"] += 1

        fechar = next((b for b in ampliada.findChildren(QPushButton) if b.text() == "X"), None)
        if fechar is not None:
            acionar(fechar, "X (fechar ampliada)")

    exec_original = TelaAmpliada.exec

    def exec_com_clique(self):
        QTimer.singleShot(0, lambda: _interagir(self))
        return exec_original(self)

    TelaAmpliada.exec = exec_com_clique
    try:
        conferir.ampliar()
        esperar(2.0)
    finally:
        TelaAmpliada.exec = exec_original

    if resultado["ok"] == 0 and resultado["falhas"] == 0:
        _contexto_atual = "achar a tela ampliada aberta"
        print("  FALHA a tela ampliada não abriu ou não deu tempo de clicar")
        return 0, 1
    return resultado["ok"], resultado["falhas"]


def _devolver_as_paginas_apagadas(conferir) -> tuple[int, int]:
    """Antes de processar, devolve ao livro (pelo proprio "apagar/restaurar"
    do programa) as paginas que este roteiro apagou ou deixou em branco.

    Por que (13/10/2026): o roteiro clica em TODOS os botoes, inclusive os que
    apagam e restauram a pagina da vez (o botao do aviso, "apagar página" da
    aba Filtro, "Apagar esta página" e "Restaurar página apagada" do menu). Se
    a pagina termina apagada ou nao depende de QUANTOS desses botoes existem.
    Ate 12/10 o botao do aviso "Parece em branco" era "apagar esta página";
    com a decisao do Samuel ele virou "Deixar em branco" (que nao apaga), a
    conta mudou de par para impar, as paginas do livro de teste terminavam
    todas apagadas e o programa, CERTO, recusava gerar um PDF sem pagina
    nenhuma ("Não sobrou nenhuma página para gerar"). O teste dizia "o
    processamento não chegou à tela final". Agora o estado antes de processar
    nao depende mais da conta de cliques. Devolve (ok, falhas)."""
    projeto = conferir.projeto
    apagadas = [p.indice + 1 for p in projeto.paginas if p.apagada]
    em_branco = [p.indice + 1 for p in projeto.paginas if getattr(p, "em_branco", False)]
    print("\n--- antes de processar: o que o roteiro deixou nas páginas ---")
    print(f"  páginas apagadas: {apagadas or 'nenhuma'}; em branco: {em_branco or 'nenhuma'}; "
          f"de {len(projeto.paginas)}")
    if "filtro" in conferir._abas_ativas:
        conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("filtro"))
    for pagina in list(projeto.paginas):
        if pagina.apagada:
            conferir.ir_para_pagina(pagina.indice)
            conferir.apagar_pagina()                     # o mesmo metodo do botao: restaura
        if getattr(pagina, "em_branco", False):
            conferir.ir_para_pagina(pagina.indice)
            conferir._deixar_em_branco(False)            # o "voltar a página" do aviso
    QApplication.processEvents()
    if any(p.apagada or getattr(p, "em_branco", False) for p in projeto.paginas):
        print("  FALHA não consegui devolver as páginas apagadas ou em branco")
        return 0, 1
    print(f"  ok    as {len(projeto.paginas)} páginas estão no livro")
    return 1, 0


def _testar_o_ver_da_lista_dos_avisos(janela, JanelaConfirmar) -> tuple[int, int]:
    """A janela "Antes de processar" (a lista das paginas e dos motivos,
    12/10/2026; Samuel, rodada 5 do "Para revisar": "Lista as páginas e os
    motivos", com "ver" e "continuar assim mesmo"). Aqui o "ver": tem de levar
    a pagina escolhida e NAO processar (a janela de confirmar nem abre). O
    "continuar assim mesmo" e exercitado logo depois, no processar de
    verdade (a resposta automatica de sempre, ver o comeco de main).

    Para a lista ter o que mostrar sempre, a ultima pagina ganha um aviso que
    o programa nao tira sozinho ("Qualidade baixa")."""
    from PySide6.QtWidgets import QDialog

    from core import analise
    from core import avisos as avisos_do_livro
    from ui.janela_dos_avisos import JanelaDosAvisos
    from ui.janela_principal import CONFERIR

    conferir = janela.tela_conferir
    projeto = conferir.projeto
    ultima = projeto.paginas[-1]
    if analise.RESOLUCAO_BAIXA not in ultima.alertas:
        ultima.alertas = list(ultima.alertas) + [analise.RESOLUCAO_BAIXA]
    ultima.revisada = False
    ultima.alertas_aceitos = [a for a in ultima.alertas_aceitos if a != analise.RESOLUCAO_BAIXA]
    conferir.ir_para_pagina(0)
    pendentes = avisos_do_livro.pendentes_do_livro(projeto)

    print("\n--- antes de processar: a lista dos avisos ('ver') ---")
    visto = {"linhas": [], "confirmar_abriu": False}
    exec_dos_avisos = JanelaDosAvisos.exec
    exec_do_confirmar = JanelaConfirmar.exec

    def escolher_ver(dialogo) -> None:
        visto["linhas"] = dialogo.linhas()
        for linha in range(dialogo.lista.count()):
            aviso = dialogo.lista.item(linha).data(Qt.UserRole)
            if aviso.alvo == avisos_do_livro.PAGINA and aviso.indice == ultima.indice:
                dialogo.lista.setCurrentRow(linha)
        dialogo.botao_ver.click()

    def exec_dos_avisos_com_ver(self):
        QTimer.singleShot(0, lambda: escolher_ver(self))
        return QDialog.exec(self)

    def exec_do_confirmar_que_nao_devia_abrir(self):
        visto["confirmar_abriu"] = True
        QTimer.singleShot(0, self.reject)
        return QDialog.exec(self)

    JanelaDosAvisos.exec = exec_dos_avisos_com_ver
    JanelaConfirmar.exec = exec_do_confirmar_que_nao_devia_abrir
    try:
        conferir.botao_processar.click()
        esperar(0.5)
    finally:
        JanelaDosAvisos.exec = exec_dos_avisos
        JanelaConfirmar.exec = exec_do_confirmar

    ok = falhas = 0
    esperada = f"Página {ultima.indice + 1}  -  {analise.descrever(analise.RESOLUCAO_BAIXA).titulo}"
    for certo, frase in (
        (len(visto["linhas"]) == len(pendentes) and esperada in visto["linhas"],
         f"a janela listou as páginas e os motivos ({len(visto['linhas'])} linhas, entre elas '{esperada}')"),
        (not visto["confirmar_abriu"] and janela.telas.currentIndex() == CONFERIR,
         "'ver' não processou (a janela de confirmar não abriu)"),
        (conferir.indice_pagina == ultima.indice,
         f"'ver' levou à página {ultima.indice + 1} (está na {conferir.indice_pagina + 1})"),
    ):
        print(("  ok    " if certo else "  FALHA ") + frase)
        ok += int(certo)
        falhas += int(not certo)
    return ok, falhas


def testar_processar_e_final(janela) -> tuple[int, int]:
    """Clica "Processar", interage com a janela de confirmação (escolher
    pasta, digitar nome, confirmar), espera o processamento terminar e
    depois clica os botões da tela final (abrir pasta, imprimir, fazer
    outro). Mesma técnica de `testar_tela_ampliada`: intercepta o `.exec()` da
    própria `JanelaConfirmar`, em vez de `QApplication.activeModalWidget()`."""
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_principal import FINAL

    resultado = {"ok": 0, "falhas": 0}
    global _contexto_atual
    conferir = janela.tela_conferir

    def _interagir_com_confirmar(dialogo) -> None:
        botao_pasta = next(
            (b for b in dialogo.findChildren(QPushButton) if "escolher pasta" in b.text().lower()),
            None)
        if botao_pasta is not None:
            if acionar(botao_pasta, "Escolher pasta"):
                resultado["ok"] += 1
            else:
                resultado["falhas"] += 1

        campo_nome = dialogo.destino.campo_nome
        _contexto_atual = "digitar o nome do arquivo"
        campo_nome.selectAll()
        QTest.keyClicks(campo_nome, "teste_botoes_saida.pdf")
        QApplication.processEvents()
        esperar(0.2)

        if acionar(dialogo.botao_processar, "Processar"):
            resultado["ok"] += 1
        else:
            resultado["falhas"] += 1

    exec_original = JanelaConfirmar.exec

    def exec_com_clique(self):
        QTimer.singleShot(0, lambda: _interagir_com_confirmar(self))
        return exec_original(self)

    # Ja existe um PDF com o nome que vai ser digitado: a caixa "Ja existe um
    # arquivo com esse nome" aparece, e a resposta automatica (AcceptRole)
    # escolhe "salvar como teste_botoes_saida (2).pdf". Ver o docstring.
    import fitz

    pasta_destino = PASTA_DE_SAIDA_DO_TESTE / "destino_escolhido"
    antigo = pasta_destino / "teste_botoes_saida.pdf"
    novo = pasta_destino / "teste_botoes_saida (2).pdf"
    pasta_destino.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    doc.new_page().insert_text((40, 60), "PDF antigo, nao pode ser mexido")
    doc.save(str(antigo))
    doc.close()
    bytes_do_antigo = antigo.read_bytes()

    ok_antes, falhas_antes = _devolver_as_paginas_apagadas(conferir)
    resultado["ok"] += ok_antes
    resultado["falhas"] += falhas_antes
    ok_lista, falhas_lista = _testar_o_ver_da_lista_dos_avisos(janela, JanelaConfirmar)
    resultado["ok"] += ok_lista
    resultado["falhas"] += falhas_lista

    print("\n--- confirmar e processar ---")
    JanelaConfirmar.exec = exec_com_clique
    try:
        conferir.botao_processar.click()
    finally:
        JanelaConfirmar.exec = exec_original

    ok, falhas = resultado["ok"], resultado["falhas"]
    if ok == 0 and falhas == 0:
        print("  FALHA a janela de confirmar não abriu ou não deu tempo de clicar")
        falhas = 1

    if not esperar(600, lambda: janela.telas.currentIndex() == FINAL):
        falhas += 1
        print("  FALHA o processamento não chegou à tela final")
        return ok, falhas

    if novo.exists() and antigo.read_bytes() == bytes_do_antigo:
        ok += 1
        print(f"  ok    já existia: salvou como '{novo.name}' sem mexer no antigo")
    else:
        falhas += 1
        print(f"  FALHA já existia: '{novo.name}' não foi gerado ou o antigo mudou")

    print("\n--- tela final ---")
    final = janela.tela_final
    for botao in (final.botao_pasta, final.botao_imprimir):
        if acionar(botao, botao.text()):
            ok += 1
        else:
            falhas += 1
    # D-012 (etapa 9a, 26/10/2026): o "imprimir agora..." abre a confirmação
    # (sem bloquear) e nada vai para a impressora; fecha sem imprimir
    confirmar = getattr(final, "dialogo_imprimir", None)
    if confirmar is not None:
        if confirmar.isVisible() and confirmar.tarefa is None:
            ok += 1
            print("  ok    imprimir agora: abriu a confirmação, nada foi impresso")
        else:
            falhas += 1
            print("  FALHA imprimir agora: a confirmação não abriu ou já mandou imprimir")
        confirmar.reject()
    # item 2.6: a janela "Montar para imprimir" abre (sem bloquear) e fecha
    if final.botao_montar.isEnabled():
        if acionar(final.botao_montar, final.botao_montar.text()):
            ok += 1
        else:
            falhas += 1
        dialogo = getattr(final, "dialogo_impressao", None)
        if dialogo is not None:
            dialogo.reject()

    outro = next((b for b in botoes_de(final) if "fazer outro" in b.text().lower()), None)
    if outro is not None:
        if acionar(outro, "fazer outro"):
            ok += 1
        else:
            falhas += 1

    return ok, falhas


def testar_cartao_e_limpar(janela, caminho_pdf: str) -> tuple[int, int]:
    """Acha o cartão do projeto de teste na tela inicial e testa o menu dele.

    "Remover da lista" acontece por último, de propósito: é a limpeza do
    projeto que este script criou, não deve sobrar na sua lista de verdade.
    """
    from ui.tela_inicio import CartaoDeProjeto

    ok = falhas = 0
    inicio = janela.tela_inicio
    esperar(0.5)

    cartao = None
    for candidato in inicio.findChildren(CartaoDeProjeto):
        if Path(candidato.resumo.caminho_entrada).name == Path(caminho_pdf).name:
            cartao = candidato
            break

    if cartao is None:
        print("\n--- cartão do projeto de teste: não encontrado (não é falha crítica) ---")
        return ok, falhas

    print("\n--- cartão do projeto de teste ---")
    global _contexto_atual

    for rotulo in ("abrir a pasta de saída", "renomear"):
        _contexto_atual = f"menu do cartão: '{rotulo}'"
        acao = _acao_do_menu_do_cartao(cartao, rotulo)
        if acao is None:
            continue
        if not acao.isEnabled():
            print(f"  (pulado, desabilitado: '{rotulo}')")
            continue
        if acionar(acao, f"menu do cartão: {rotulo}"):
            ok += 1
        else:
            falhas += 1

    # duplo clique no cartao, so se ele nao estiver "perdido"
    if not cartao.perdido:
        _contexto_atual = "duplo clique no cartão"
        # "continuar" abre o trabalho salvo direto na area de trabalho (etapa 3
        # da obra - ver JanelaPrincipal._continuar_projeto), entao esperamos CONFERIR.
        from ui.janela_principal import CONFERIR
        antes = len(_falhas)
        QTest.mouseDClick(cartao, Qt.LeftButton)
        if esperar(60, lambda: janela.telas.currentIndex() == CONFERIR) and len(_falhas) == antes:
            ok += 1
            print("  ok    duplo clique no cartão")
            acao_voltar = janela.menu.acoes.get("voltar")
            if acao_voltar is not None and acao_voltar.isEnabled():
                acionar(acao_voltar, "voltar (depois do duplo clique)")
                esperar(1.0)
        else:
            falhas += 1
            print("  FALHA duplo clique no cartão")

    _contexto_atual = "menu do cartão: 'remover da lista' (limpeza)"
    acao_remover = _acao_do_menu_do_cartao(cartao, "remover da lista")
    if acao_remover is not None and acionar(acao_remover, "remover da lista (limpeza)"):
        ok += 1
    else:
        falhas += 1
        print("  FALHA ao remover o projeto de teste - remova à mão em 'Continuar de onde parou'")

    return ok, falhas


def _acao_do_menu_do_cartao(cartao, texto_procurado: str):
    """Abre o menu de contexto do cartão (sem clique de mouse: QMenu.exec()
    bloquearia) e devolve a QAction cujo texto contém `texto_procurado`."""
    from PySide6.QtWidgets import QMenu

    menu = QMenu(cartao)
    if not cartao.perdido:
        menu.addAction("continuar", lambda: cartao.tela.pedir_para_continuar(cartao.resumo))
    else:
        menu.addAction("procurar o livro",
                        lambda: cartao.tela.procurar_o_livro_a_mao(cartao.resumo))
    menu.addAction("começar de novo", lambda: cartao.tela.pedir_para_recomecar(cartao.resumo))
    menu.addAction("renomear", lambda: cartao.tela.pedir_para_renomear(cartao.resumo))
    abrir = menu.addAction(
        "abrir a pasta de saída",
        lambda: historico.abrir_pasta(cartao.resumo.caminho_saida))
    abrir.setEnabled(bool(cartao.resumo.caminho_saida)
                     and Path(cartao.resumo.caminho_saida).exists())
    menu.addAction("remover da lista", lambda: cartao.tela.pedir_para_remover(cartao.resumo))

    for acao in menu.actions():
        if texto_procurado in acao.text().lower():
            return acao
    return None


def acionar_menu_habilitado(janela, excluir: set[str]) -> tuple[int, int]:
    """Só aciona o que um clique de mouse de verdade alcançaria.

    `acao.isEnabled()` não basta: um QAction continua "habilitado" mesmo
    dentro de um menu cujo dropdown inteiro está apagado (Editar/Marcar/etc.
    ficam assim fora da tela de trabalho, via `mostrar_tela_inicial`) - só o
    `menuAction()` do menu em si é desabilitado. Sem essa checagem, o
    varrimento aciona ações de página/seleção com o projeto ainda pela
    metade e trava numa delas.
    """
    menu_de: dict[object, object] = {}
    for menu in janela.menu.menus.values():
        for acao_do_menu in menu.actions():
            menu_de[acao_do_menu] = menu

    ok = falhas = 0
    for chave, acao in janela.menu.acoes.items():
        if chave in excluir or not acao.isEnabled():
            continue
        menu_pai = menu_de.get(acao)
        if menu_pai is not None and not menu_pai.menuAction().isEnabled():
            continue
        if acionar(acao, f"menu: {chave}"):
            ok += 1
        else:
            falhas += 1
    return ok, falhas


TAMANHOS_GRANDES = ((1000, 680), (1000, 700), (1100, 720), (1280, 800),
                    (1400, 900), (1600, 1000), (1024, 690), (1920, 1050))
TAMANHOS_PEQUENOS = ((1000, 680), (1400, 900))  # so para as telas mais simples


def redimensionar_sem_quebrar(janela, tamanhos) -> tuple[int, int]:
    """Redimensiona a janela para cada (largura, altura) da lista e confere
    que nenhuma exceção nova apareceu (o teste de "botao_botoes.py" clica em
    botões de verdade, mas aqui só se checa que o resize em si não derruba nada -
    ver CLAUDE.md secao 4.5)."""
    global _contexto_atual
    ok = falhas = 0
    for largura, altura in tamanhos:
        _contexto_atual = f"redimensionar para {largura}x{altura}"
        antes = len(_falhas)
        janela.resize(largura, altura)
        esperar(0.3)
        if len(_falhas) == antes:
            ok += 1
        else:
            falhas += 1
    return ok, falhas


# ---------------------------------------------------------------------------


def main(caminho_pdf: str) -> int:
    """Instala os monkeypatches, abre a janela de verdade e roda, em ordem,
    todos os testes de tela (inicial, opções, análise, conferir+ampliada,
    processar+final, cartão+limpeza). Devolve 1 se qualquer clique ou
    checagem de layout falhou em algum lugar."""
    _instalar_monkeypatches(caminho_pdf)
    if CAMINHO_DO_LOG.exists():
        CAMINHO_DO_LOG.unlink()

    app = QApplication(sys.argv)

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.show()
    esperar(0.3)

    total_ok = total_falhas = 0

    for nome, funcao, args in (
        ("tela inicial", testar_tela_inicial, (janela, caminho_pdf)),
        # etapa 3 da obra: a tela "O que fazer" saiu do caminho; o Automatico
        # (painel e janela grande) roda no lugar do antigo "Conferir"
        ("Automático", testar_automatico, (janela, caminho_pdf)),
    ):
        ok, falhas = funcao(*args)
        total_ok += ok
        total_falhas += falhas

    from ui.janela_principal import CONFERIR
    if not esperar(180, lambda: janela.telas.currentIndex() == CONFERIR):
        print("o Automático não terminou")
        return 1

    ok, falhas = testar_conferir_e_ampliada(janela)
    total_ok += ok
    total_falhas += falhas

    ok, falhas = testar_processar_e_final(janela)
    total_ok += ok
    total_falhas += falhas

    ok, falhas = testar_cartao_e_limpar(janela, caminho_pdf)
    total_ok += ok
    total_falhas += falhas

    print(f"\n{total_ok} ações realizadas, {total_falhas} falhas")
    if _falhas:
        print(f"Detalhe das falhas em: {CAMINHO_DO_LOG}")
    janela.close()
    esperar(0.4)
    return 1 if total_falhas else 0


def _gerar_pdf_de_teste() -> str:
    """PDF sintético de duas páginas, isolado de qualquer projeto real."""
    import fitz

    caminho = PASTA_DE_SAIDA_DO_TESTE / "fixture_gerado.pdf"
    PASTA_DE_SAIDA_DO_TESTE.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for i in range(2):
        pagina = doc.new_page(width=595, height=842)
        pagina.insert_text((100, 100), f"Página de teste {i + 1}", fontsize=24)
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        caminho_pdf = sys.argv[1]
    else:
        caminho_pdf = _gerar_pdf_de_teste()
        print(f"Nenhum PDF indicado - gerado um PDF de teste em: {caminho_pdf}")
    raise SystemExit(main(caminho_pdf))
