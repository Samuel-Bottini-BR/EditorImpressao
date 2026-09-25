"""Clica em TODOS os botões de TODAS as telas, de verdade.

Uso:
    python teste_botoes.py               # gera um PDF de teste sozinho (recomendado)
    python teste_botoes.py "livro.pdf"   # usa um PDF à sua escolha

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

Cobre: tela_inicio (busca, área de arrastar, cartão de projeto e seu menu de
contexto), tela_opcoes (checkboxes, filtros, combo de caderno), tela_conferir
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
abertura via área de arrastar); o aviso de "já existe arquivo com esse nome"
em `_perguntar_sobre_substituir` (só dispara se o destino escolhido já tiver
um arquivo com aquele nome - o destino de teste é sempre uma pasta nova);
`teste_ampliar.py` continua sendo o teste mais detalhado do zoom/arrasto.
"""

from __future__ import annotations

import shutil
import sys
import time
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
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

    QInputDialog.getText = staticmethod(
        lambda *a, **k: ("Projeto de teste (renomeado)", True))
    QInputDialog.getInt = staticmethod(
        lambda self, titulo, rotulo, valor=1, minimo=0, maximo=100, passo=1, *a, **k: (valor, True))

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
    from ui.janela_principal import OPCOES

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

    # a area de arrastar - abre o dialogo (mockado para devolver o PDF de teste)
    _contexto_atual = "clique na área de arrastar"
    antes = len(_falhas)
    QTest.mouseClick(inicio.area, Qt.LeftButton)
    if not esperar(20, lambda: janela.telas.currentIndex() == OPCOES):
        falhas += 1
        print("  FALHA área de arrastar não levou à tela de opções")
    elif len(_falhas) != antes:
        falhas += 1
    else:
        ok += 1
        print("  ok    área de arrastar abriu o PDF de teste")

    # menu, no estado "tela inicial" (so Arquivo/Ver/Ajuda valem)
    o, f = acionar_menu_habilitado(janela, excluir={"abrir", "sair"})
    ok += o
    falhas += f

    # redimensionar, so para confirmar que nao trava
    o, f = redimensionar_sem_quebrar(janela, TAMANHOS_PEQUENOS)
    ok += o
    falhas += f
    return ok, falhas


def testar_tela_opcoes(janela, caminho_pdf: str) -> tuple[int, int]:
    """Clica cada caixinha (e volta ao estado original, senao "Conferir" fica
    desabilitado com nenhuma função marcada), cada radio de filtro, troca o
    combo de páginas por caderno, redimensiona, e confere que "voltar" volta
    para a tela inicial (reabrindo o PDF depois, para os testes seguintes
    poderem continuar)."""
    from ui.janela_principal import INICIO, OPCOES

    print("\n--- tela de opções ---")
    ok = falhas = 0
    opcoes = janela.tela_opcoes

    for caixa in (opcoes.cx_dividir, opcoes.cx_limpar, opcoes.cx_endireitar,
                  opcoes.cx_cortar, opcoes.cx_cadernos):
        if acionar(caixa, caixa.text()):
            ok += 1
        else:
            falhas += 1
        # deixa como estava antes de seguir, senao desliga tudo e o botao
        # "Conferir" fica desabilitado (nenhuma funcao marcada)
        if acionar(caixa, caixa.text() + " (de volta)"):
            ok += 1
        else:
            falhas += 1

    for radio in opcoes.grupo_filtros.buttons():
        if acionar(radio, radio.text()):
            ok += 1
        else:
            falhas += 1

    global _contexto_atual
    _contexto_atual = "trocar o combo de páginas por caderno"
    antes = len(_falhas)
    indice_novo = (opcoes.combo_caderno.currentIndex() + 1) % opcoes.combo_caderno.count()
    opcoes.combo_caderno.setCurrentIndex(indice_novo)
    QApplication.processEvents()
    esperar(0.2)
    if len(_falhas) == antes:
        ok += 1
        print(f"  ok    {_contexto_atual}")
    else:
        falhas += 1

    o, f = redimensionar_sem_quebrar(janela, TAMANHOS_PEQUENOS)
    ok += o
    falhas += f

    # "voltar" - confere que volta para o inicio, e reabre para poder seguir
    achou_voltar = None
    for botao in botoes_de(opcoes):
        if botao is opcoes.botao_conferir:
            continue
        if "voltar" in (botao.text() or "").lower():
            achou_voltar = botao
            break
    if achou_voltar is not None:
        antes = len(_falhas)
        if acionar(achou_voltar, "voltar") and esperar(
                5, lambda: janela.telas.currentIndex() == INICIO):
            ok += 1
            QTest.mouseClick(janela.tela_inicio.area, Qt.LeftButton)
            if not esperar(20, lambda: janela.telas.currentIndex() == OPCOES):
                falhas += 1
                print("  FALHA reabrir o PDF depois de 'voltar'")
        else:
            falhas += 1
            print("  FALHA 'voltar' não retornou à tela inicial")

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

    print("\n--- cabecalho e rodape (conferir) ---")
    for botao in (conferir.botao_alertas, conferir.botao_desfazer, conferir.botao_refazer):
        if not botao.isEnabled():
            continue
        if acionar(botao, botao.text()):
            ok += 1
        else:
            falhas += 1

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
    o, f = acionar_menu_habilitado(janela, excluir={"processar", "sair", "voltar", "abrir"})
    ok += o
    falhas += f

    print("\n--- tela ampliada ---")
    o, f = testar_tela_ampliada(conferir)
    ok += o
    falhas += f

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

    print("\n--- tela final ---")
    final = janela.tela_final
    for botao in (final.botao_pasta, final.botao_imprimir):
        if acionar(botao, botao.text()):
            ok += 1
        else:
            falhas += 1

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
        # "continuar" pula direto para a analise (nao para de novo em OPCOES -
        # ver JanelaPrincipal._continuar_projeto), entao esperamos CONFERIR.
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
        ("tela de opções", testar_tela_opcoes, (janela, caminho_pdf)),
    ):
        ok, falhas = funcao(*args)
        total_ok += ok
        total_falhas += falhas

    print("\nAnalisando...")
    janela.analisar()
    from ui.janela_principal import CONFERIR
    if not esperar(180, lambda: janela.telas.currentIndex() == CONFERIR):
        print("a análise não terminou")
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
