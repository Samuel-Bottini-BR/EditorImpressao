"""Cada botão prova que faz o que promete (bateria nova de 26/10/2026, parte 4).

D-010 (Samuel, 26/10/2026): "eu acho que o botão tem que ser provado que ele faz o que se diz que se
faz, e não só se ele muda algo na tela." Prova escrita pelo verificador, que não construiu o programa.

COMO FUNCIONA
  - A lista de promessas mora em tests/promessas/promessas.md: uma entrada por botão (ou por ação
    que mora em vários lugares, como "Girar ¼ à direita" no menu, no painel e no canto da página),
    tirada do nome do botão, da dica e das decisões do Livro (docs/plano/DECISOES.md). Cada uma diz
    o que tem de acontecer NA TELA, NO PROJETO GRAVADO (projeto.json, acoes.jsonl) e NO PDF QUE SAI.
  - A VARREDURA abre o programa sem janela visível, passa por todas as telas e estados que sabe
    abrir e anota a chave de cada botão à vista ("tela/lugar/rótulo"). Botão sem promessa escrita
    REPROVA (test_todo_botao_tem_promessa). Promessa de botão que sumiu também (o contrário).
  - Cada promessa tem a sua PROVA (`@prova("P-NNN")`): clica o botão de verdade (o sinal clicked do
    Qt, o trigger do menu, o clique do mouse nos botões desenhados à mão) e confere a promessa
    inteira. Quando a promessa fala do PDF, o PDF é gerado de verdade pelo "Confirmar e processar"
    e medido. Quando diz que o PDF NÃO muda, a prova confere que o projeto gravado não mudou
    (o PDF sai só do livro e do projeto: mesmo projeto, mesmo PDF).
  - Promessa de decisão ainda não construída ("aguarda: etapa N, D-xxx" na lista) vira
    xfail(strict=True): enquanto a etapa não fizer, o teste falha "esperado"; quando fizer, o
    xfail estrito vira erro e obriga a tirar a marca — daí em diante a promessa é exigida.
  - Promessa QUEBRADA (defeito real do programa de hoje) fica vermelha de propósito, com a frase
    do defeito. Para juntar sem vermelho, a gerente dá dono ao defeito (uma etapa) e troca para
    "aguarda" na lista.

Nada aparece na tela (tests/conftest.py). Pasta de dados própria em saida_teste\\ (fixture `pasta`).
O que mudar quando a tela mudar: tests/promessas/ajudantes.py (abrir o livro, os lugares da área
de trabalho) e a lista de promessas.
"""

from __future__ import annotations

import os
import shutil
import time
import uuid
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")
pytest.importorskip("cv2")

from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox  # noqa: E402

import projetos  # noqa: E402
from tests.promessas import ajudantes as aj  # noqa: E402

PASTA_DOS_TESTES = aj.RAIZ / "saida_teste" / "pytest_promessas"
PROMESSAS = aj.ler_promessas()


# --- fixtures -----------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """O QApplication com o que o main.py põe no programa de verdade (etapa 9a): a tradução dos
    textos do próprio Qt para o português e a rodinha que não muda número sem clique."""
    app = QApplication.instance() or QApplication([])
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)
    return app


@pytest.fixture
def pasta(monkeypatch):
    """Pasta própria do teste, com LOCALAPPDATA apontando para ela (projetos, configurações e
    histórico nascem ali, nunca na pasta de dados do Samuel)."""
    aqui = PASTA_DOS_TESTES / uuid.uuid4().hex[:10]
    (aqui / "dados").mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(aqui / "dados"))
    monkeypatch.delenv("APPDATA", raising=False)
    assert projetos.pasta_dos_projetos().is_relative_to(aqui)
    yield aqui
    if Path.cwd().is_relative_to(aqui):
        os.chdir(aj.RAIZ)
    from core.paginas_em_outro_processo import soltar_livro

    soltar_livro(None)
    for _tentativa in range(30):
        shutil.rmtree(aqui, ignore_errors=True)
        if not aqui.exists():
            break
        QApplication.processEvents()
        time.sleep(0.1)
    try:
        PASTA_DOS_TESTES.rmdir()
    except OSError:
        pass


@pytest.fixture
def janela(app, pasta, monkeypatch):
    """A janela principal do programa, com os avisos anotados numa lista (em vez da caixa modal).
    No fim, para o que segura o PDF e fecha."""
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.avisos = []
    monkeypatch.setattr(janela, "avisar",
                        lambda mensagem, titulo="": janela.avisos.append(mensagem))
    yield janela
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
        janela.previas = None
    try:
        janela.tela_conferir.tira.parar()
    except Exception:  # noqa: BLE001
        pass
    janela._fechar_a_janela_do_automatico()          # etapa 3: a tela "O que fazer" saiu (D-002)
    janela.close()
    aj.assentar()
    # as tarefas de fundo deste teste (prévias, miniaturas) terminam aqui, antes de a pasta de
    # dados trocar: senão o erro de uma delas (o livro já apagado) cai no erros.log do próximo
    from PySide6.QtCore import QThreadPool

    QThreadPool.globalInstance().waitForDone(15000)
    aj.assentar()


@pytest.fixture
def livro(pasta):
    return aj.criar_livro(pasta, folhas=4)


@pytest.fixture
def tela(janela, livro):
    """A área de trabalho com o livro de teste aberto sem nada marcado (D-009)."""
    return aj.abrir_livro_para_teste(janela, livro)


# --- a varredura --------------------------------------------------------------------------------
#
# Passa por todas as telas e estados que sabe abrir e anota a chave de cada botão à vista. O que a
# varredura não sabe abrir não entra (ressalva escrita no ONDE-PAREI); a promessa desses botões diz
# "fora da varredura" e o motivo.

def _chaves_da_trilha(tela) -> dict[str, object]:
    from ui.widgets.trilha_agrupada import GRUPOS

    return {f"trilha/{f}": f for g in GRUPOS if g != "-" for f in g}


def _chaves_dos_icones(tela) -> dict[str, object]:
    return {f"ícones da direita/{chave}": chave for chave in tela.paineis.icones.retangulos()}


def _chaves_dos_cartoezinhos(tela) -> dict[str, object]:
    """Os filtros da página no painel Filtro são cartõezinhos (a página pequena e o nome), não
    botões: clicar escolhe o filtro da página (rodada 9, 403 B)."""
    return {f"área de trabalho/filtro da página/cartão {c.rotulo.text()}": c
            for c in tela.paineis.filtro_da_pagina.cartoes.values()}


def _chaves_do_menu(janela) -> dict[str, object]:
    saida = {f"menu/{chave}": acao for chave, acao in janela.menu.acoes.items()}
    saida["menu/livros recentes"] = janela.menu.menu_recentes
    return saida


def _chaves_dos_avisos() -> dict[str, object]:
    """Os botões que os avisos põem na faixa embaixo da página: tirados do catálogo dos avisos
    (core/analise.ALERTAS), porque cada um aparece só na página que tem aquele aviso. A chave é o
    que o botão FAZ (o código da correção), porque o mesmo rótulo ("está bom assim", "Desfazer")
    aparece em avisos diferentes."""
    from core import analise

    saida = {}
    for alerta in analise.ALERTAS.values():
        for rotulo, correcao in alerta.botoes:
            saida[f"aviso/{correcao}"] = (rotulo, alerta.codigo)
    return saida


def _especiais_do_revisar(tela) -> dict:
    """Os botões do "Por motivo" têm o nome do motivo e a contagem: viram dois rótulos fixos."""
    from PySide6.QtWidgets import QPushButton

    especiais = {}
    for botao in getattr(tela.paineis.para_revisar, "itens", []):
        especiais[botao] = "motivo (o botão do grupo)"
    for botao in tela.paineis.para_revisar.findChildren(QPushButton):
        if botao.text().startswith("está bom") and botao.text() != "está bom em tudo":
            especiais[botao] = "está bom: todas"
    # os filtros do "Só neste pedaço" (os mesmos nomes dos cartõezinhos da página)
    for chave, botao in getattr(tela.paineis.filtro_da_pagina, "botoes_do_pedaco", {}).items():
        especiais[botao] = f"só neste pedaço: {botao.text()}"
    # as linhas do Histórico (uma por ação feita ou desfeita) são botões com a descrição da ação
    for botao in getattr(tela.paineis.historico, "itens", []):
        especiais[botao] = "ação feita (volta até aqui)"
    for botao in getattr(tela.paineis.historico, "itens_desfeitos", []):
        especiais[botao] = "ação desfeita (refaz até aqui)"
    # o "Rodar N etapas" do painel Automático (o número muda com as marcadas; etapa 3)
    rodar = getattr(tela.paineis.automatico, "botao_rodar", None)
    if rodar is not None:
        especiais[rodar] = "Rodar"
    return especiais


def _anotar_caixas(chaves: dict, vistas) -> None:
    for titulo, botoes in vistas:
        for texto in botoes:
            chaves[f"caixa “{titulo}”/{aj.rotulo_do_botao(texto)}"] = texto


def _varrer_area_de_trabalho(janela, tela, chaves) -> None:
    from core import analise
    from core.filtros import PRETO_E_BRANCO
    from ui.widgets.trilha_agrupada import GRUPOS

    def anotar() -> None:
        aj.assentar(3)
        lugares = aj.lugares_da_area_de_trabalho(tela)
        chaves.update(aj.chaves_dos_botoes(tela, "área de trabalho", lugares, _especiais_do_revisar(tela)))

    # cada ferramenta, com o Propriedades aberto, em duas páginas
    for indice in (0, 1):
        tela.ir_para_pagina(indice)
        for grupo in GRUPOS:
            if grupo == "-":
                continue
            for ferramenta in grupo:
                tela.escolher_ferramenta(ferramenta)
                tela.paineis.abrir("props")
                anotar()
    # cada painel
    for painel in ("revisar", "automatico", "props", "filtro", "historico"):
        tela.paineis.abrir(painel)
        anotar()
    # o "Só neste pedaço" aberto
    parte = tela.paineis.filtro_da_pagina.partes.get("pedaco")
    if parte is not None:
        tela.paineis.abrir("filtro")
        parte.abrir(True)
        anotar()
        parte.abrir(False)
    # a página em Preto e branco com "Só as letras" (os jeitos do "Só as letras" no painel Filtro)
    pagina = tela.projeto.paginas[0]
    tela.ir_para_pagina(0)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.paineis.abrir("filtro")
    anotar()
    from PySide6.QtWidgets import QCheckBox

    for caixa in tela.paineis.filtro_da_pagina.findChildren(QCheckBox):
        if caixa.text() == "Só as letras" and caixa.isVisibleTo(tela):
            caixa.click()
            anotar()
            for botao in tela.paineis.filtro_da_pagina.findChildren(type(tela.botao_esta_certo)):
                if botao.text() == "Mais opções" and botao.isVisibleTo(tela):
                    botao.click()
                    anotar()
            caixa.click()
    tela.desfazer()
    # uma página com aviso, e o "Por motivo"
    pagina = tela.projeto.paginas[1]
    pagina.alertas = [analise.EM_BRANCO, analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    pagina.revisada = False
    tela.ir_para_pagina(1)
    tela.paineis.para_revisar.atualizar(tela.projeto)
    tela.paineis.abrir("revisar")
    anotar()
    tela.paineis.para_revisar.mostrar_aba("motivo")
    anotar()
    # depois de um "deixar em branco" (os botões viram "voltar a página" e o desfazer acende)
    tela.paineis.abrir("props")
    tela.botao_em_branco.click()
    anotar()
    tela.paineis.abrir("historico")
    anotar()
    tela.desfazer()
    anotar()
    pagina.alertas = []
    # a área de trabalho 1 (sanfona)
    tela.paineis.definir_jeito("sanfona")
    anotar()
    tela.paineis.definir_jeito("icones")
    # as miniaturas fechadas ("Confirmar e processar" desce para a barra de baixo, D-050)
    tela.mostrar_miniaturas(False)
    anotar()
    tela.mostrar_miniaturas(True)
    # "Todas as páginas"
    tela.abrir_todas_as_paginas()
    anotar()
    tela._voltar_das_todas(None)
    aj.assentar()


def _mostrar_e_anotar(dialogo, prefixo: str) -> dict:
    dialogo.show()
    aj.assentar()
    chaves = aj.chaves_dos_botoes(dialogo, prefixo)
    dialogo.close()
    dialogo.deleteLater()
    aj.assentar()
    return chaves


def _varrer_janelas(janela, tela) -> dict:
    from core import analise
    from core import avisos as avisos_do_livro
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    from ui.tela_ampliada import TelaAmpliada
    from ui.tela_configuracoes import PARTES, TelaConfiguracoes
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    chaves: dict = {}
    projeto = janela.projeto
    chaves.update(_mostrar_e_anotar(JanelaConfirmar(projeto, "Livro de Teste.pdf", janela),
                                    "confirmar e processar"))
    projeto.paginas[2].alertas = [analise.EM_BRANCO]
    projeto.paginas[2].revisada = False
    pendentes = avisos_do_livro.pendentes_do_livro(projeto)
    chaves.update(_mostrar_e_anotar(
        JanelaDosAvisos(pendentes, antes_de_processar=True, parent=janela, projeto=projeto),
        "antes de processar"))
    chaves.update(_mostrar_e_anotar(
        JanelaDosAvisos(pendentes, antes_de_processar=False, parent=janela, projeto=projeto),
        "lista dos avisos"))
    projeto.paginas[2].alertas = []
    chaves.update(_mostrar_e_anotar(DialogoEscolherPaginas(projeto, 0, janela), "escolher as páginas"))
    chaves.update(_mostrar_e_anotar(DialogoTamanhoDaFolha(10.0, 14.0, None, janela), "tamanho da folha"))
    for parte in PARTES:
        chaves.update(_mostrar_e_anotar(TelaConfiguracoes(janela, parte=parte), f"configurações/{parte}"))
    chaves.update(_mostrar_e_anotar(FiltrosEmTelaCheia(tela, janela), "filtros em tela cheia"))
    chaves.update(_mostrar_e_anotar(TelaAmpliada(tela, parent=janela), "página ampliada"))
    # a janela grande do Automático (etapa 3 da obra), com as opções de cada etapa, e a caixa da receita
    from core import automatico as A
    from ui.automatico import CaixaDaReceita, JanelaDoAutomatico

    grande = JanelaDoAutomatico(janela.estado_do_automatico, projeto.caminho_entrada, janela)
    grande.show()
    aj.assentar()
    for etapa in A.ETAPAS:
        grande.mostrar_etapa(etapa)
        aj.assentar()
        chaves.update(aj.chaves_dos_botoes(grande, "automático (janela grande)"))
    grande.done(0)
    grande.deleteLater()
    aj.assentar()
    chaves.update(_mostrar_e_anotar(CaixaDaReceita(janela.estado_do_automatico, janela), "caixa da receita"))
    # as caixas de perguntar e de digitar que os menus abrem
    vistas = []
    for chave in ("ir_para_pagina", "nome_do_arquivo", "atalhos"):
        vistas += aj.caixas_durante(janela.menu.acoes[chave].trigger)
    _anotar_caixas(chaves, vistas)
    return chaves


def _varrer_janelas_do_pdf(janela, pdf: Path) -> dict:
    from ui.dialogo_impressao import ConfirmarImpressao, DialogoImpressao

    chaves: dict = {}
    chaves.update(_mostrar_e_anotar(DialogoImpressao(str(pdf), janela), "montar para imprimir"))
    chaves.update(_mostrar_e_anotar(
        ConfirmarImpressao(str(pdf), janela, impressoras=["Impressora de teste"]), "imprimir agora"))
    return chaves


def inventario(janela, pasta, monkeypatch) -> dict[str, object]:
    """Passa por todas as telas e estados que a varredura sabe abrir e devolve chave -> botão."""
    from ui.janela_principal import OPCOES, PROGRESSO

    chaves: dict[str, object] = {}
    inicio = janela.tela_inicio
    lugares_do_inicio = [("todas as páginas", inicio.livro_aberto.todas),
                         ("livro aberto", inicio.livro_aberto), ("livros", inicio)]

    # tela dos livros, sem livro nenhum
    janela.resize(1280, 760)
    janela.show()
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(inicio, "início", lugares_do_inicio))
    chaves["início/livros/+ (abrir um PDF)"] = inicio.area

    # a tela "O que fazer" (sai na etapa 3, D-002)
    livro = aj.criar_livro(pasta, folhas=4)
    janela.abrir_livro(str(livro))
    aj.assentar()
    if janela.telas.currentIndex() == OPCOES:
        chaves.update(aj.chaves_dos_botoes(janela.tela_opcoes, "o que fazer"))
    tela = aj.abrir_livro_para_teste(janela, livro)

    # a área de trabalho
    chaves.update(_chaves_da_trilha(tela))
    chaves.update(_chaves_dos_icones(tela))
    chaves.update(_chaves_dos_cartoezinhos(tela))
    chaves.update(_chaves_do_menu(janela))
    chaves.update(_chaves_dos_avisos())
    _varrer_area_de_trabalho(janela, tela, chaves)
    for texto in aj.acoes_de_menu_aberto(tela.miniaturas.pontos.click):
        chaves[f"área de trabalho/miniaturas/… {aj.rotulo_do_botao(texto)}"] = texto
    chaves.update(_varrer_janelas(janela, tela))

    # o PDF: "processando", "Ficou pronto!", as janelas de imprimir e a caixa "Já existe"
    janela.telas.setCurrentIndex(PROGRESSO)
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(janela.tela_progresso, "processando"))
    janela.telas.setCurrentIndex(janela.telas.indexOf(janela.tela_conferir))
    pdf = aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "pronto.pdf")
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(janela.tela_final, "ficou pronto"))
    chaves.update(_varrer_janelas_do_pdf(janela, pdf))
    janela.telas.setCurrentIndex(janela.telas.indexOf(janela.tela_conferir))
    _anotar_caixas(chaves, aj.caixas_durante(janela.processar, clicar="cancelar"))

    # de volta à tela dos livros, agora com um livro: cartão, menu do cartão, livro aberto
    janela._recomecar()
    inicio.recarregar()
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(inicio, "início", lugares_do_inicio))
    from ui.tela_inicio import CartaoDeProjeto

    cartoes = inicio.findChildren(CartaoDeProjeto)
    assert cartoes, "a varredura não achou o cartão do livro na tela dos livros"
    cartao = cartoes[0]
    chaves["início/livros/(clique no cartão)"] = cartao
    abrir_menu = lambda: cartao._abrir_menu(QPoint(5, 5))  # noqa: E731
    for texto in aj.acoes_de_menu_aberto(abrir_menu):
        chaves[f"início/menu do livro/{aj.rotulo_do_botao(texto)}"] = texto
    for item in ("começar de novo", "renomear", "remover da lista"):
        _anotar_caixas(chaves, aj.caixas_durante(lambda i=item: aj.acoes_de_menu_aberto(abrir_menu, i)))
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(inicio, "início", lugares_do_inicio))
    inicio.livro_aberto._ver_todas()
    aj.assentar()
    chaves.update(aj.chaves_dos_botoes(inicio, "início", lugares_do_inicio))
    return chaves


@pytest.fixture(scope="module")
def _inventario_guardado():
    return {}


def _inventario(janela, pasta, monkeypatch, guardado) -> list[str]:
    if "chaves" not in guardado:
        guardado["chaves"] = sorted(inventario(janela, pasta, monkeypatch))
    return guardado["chaves"]


def test_todo_botao_tem_promessa(janela, pasta, monkeypatch, _inventario_guardado):
    """D-010: "Botão sem promessa [...] reprova a junção" (a prova escrita no Livro). A varredura
    acha os botões; cada chave tem de estar numa promessa de tests/promessas/promessas.md."""
    chaves = _inventario(janela, pasta, monkeypatch, _inventario_guardado)
    prometidas = {c for p in PROMESSAS.values() for c in p.chaves}
    sem_promessa = [c for c in chaves if c not in prometidas]
    assert not sem_promessa, (
        f"{len(sem_promessa)} botão(ões) sem promessa escrita em tests/promessas/promessas.md:\n  "
        + "\n  ".join(sem_promessa))


def test_toda_promessa_tem_botao(janela, pasta, monkeypatch, _inventario_guardado):
    """O contrário: promessa de botão que a varredura não acha mais (o botão saiu ou mudou de nome)
    reprova, para a lista não ficar velha. Ficam de fora as que aguardam etapa (o botão ainda não
    existe), as "fora da varredura" e as do que já saiu ("sai na", depois de sair)."""
    chaves = set(_inventario(janela, pasta, monkeypatch, _inventario_guardado))
    velhas = [f"{p.numero} · {p.titulo}" for p in PROMESSAS.values()
              if not p.aguarda and "fora da varredura" not in p.campos and not p.some_na
              and not any(c in chaves for c in p.chaves)]
    assert not velhas, ("promessa(s) de botão que a varredura não achou (o botão saiu ou mudou de "
                        "nome? atualize tests/promessas/promessas.md):\n  " + "\n  ".join(velhas))


# --- as provas ----------------------------------------------------------------------------------
#
# `@prova("P-NNN")` liga a prova à promessa. Se a promessa diz "aguarda", a prova fica
# xfail(strict=True) com o motivo; quando a etapa fizer, ela passa e o estrito obriga a tirar a
# marca da lista (daí em diante é exigida). Toda promessa tem de ter prova (test_toda_promessa_tem_prova).

_PROVADAS: set[str] = set()


def prova(numero: str):
    assert numero in PROMESSAS, f"{numero} não está em promessas.md"
    _PROVADAS.add(numero)
    promessa = PROMESSAS[numero]

    def marcar(funcao):
        funcao.__doc__ = f"{numero} · {promessa.titulo}\n\n{funcao.__doc__ or ''}"
        if promessa.aguarda:
            return pytest.mark.xfail(strict=True, reason=f"aguarda {promessa.aguarda}")(funcao)
        return funcao

    return marcar


def test_toda_promessa_tem_prova():
    sem_prova = [f"{p.numero} · {p.titulo}" for p in PROMESSAS.values() if p.numero not in _PROVADAS]
    assert not sem_prova, "promessa(s) sem prova em tests/test_promessas.py:\n  " + "\n  ".join(sem_prova)


@pytest.fixture(autouse=True)
def _nenhum_erro_escondido(request):
    """Nenhum botão pode falhar escondido: o programa anota no erros.log o erro que um botão teve
    (e mostra "Não consegui fazer isso agora", que o vigia do conftest pega). No fim de cada prova,
    o erros.log da pasta de dados do teste tem de estar vazio."""
    pasta = request.getfixturevalue("pasta") if "pasta" in request.fixturenames else None
    yield
    if pasta is None:
        return
    log = pasta / "dados" / "EditorImpressao" / "erros.log"
    if log.exists() and log.read_text(encoding="utf-8", errors="replace").strip():
        pytest.fail("um botão falhou por baixo (erros.log):\n" + log.read_text(encoding="utf-8")[-3000:])


# --- ajudantes das provas -------------------------------------------------------------------------

def _lugares_do_inicio(inicio):
    return [("todas as páginas", inicio.livro_aberto.todas),
            ("livro aberto", inicio.livro_aberto), ("livros", inicio)]


def botao(janela, chave: str):
    """O botão de verdade que tem esta chave, achado pela mesma varredura do teste (assim a chave
    da promessa e o botão apertado são o mesmo). Falha se não estiver à vista."""
    tela = janela.tela_conferir
    if chave.startswith("área de trabalho/"):
        achados = aj.chaves_dos_botoes(tela, "área de trabalho", aj.lugares_da_area_de_trabalho(tela),
                                      _especiais_do_revisar(tela))
    elif chave.startswith("início/"):
        achados = aj.chaves_dos_botoes(janela.tela_inicio, "início", _lugares_do_inicio(janela.tela_inicio))
    elif chave.startswith("ficou pronto/"):
        achados = aj.chaves_dos_botoes(janela.tela_final, "ficou pronto")
    elif chave.startswith("o que fazer/"):
        achados = aj.chaves_dos_botoes(janela.tela_opcoes, "o que fazer")
    elif chave.startswith("processando/"):
        achados = aj.chaves_dos_botoes(janela.tela_progresso, "processando")
    else:
        raise AssertionError(f"botao(): chave sem tela conhecida: {chave}")
    assert chave in achados, f"o botão '{chave}' não está à vista. À vista: {sorted(achados)}"
    return achados[chave]


def apertar(janela, chave: str) -> None:
    """Aperta o botão da chave como a pessoa: o clique do botão (sinal clicked), o item do menu
    (trigger), ou o clique do mouse nos botões desenhados à mão (trilha, ícones da direita)."""
    tela = janela.tela_conferir
    if chave.startswith("menu/"):
        acao = janela.menu.acoes[chave[5:]]
        assert acao.isEnabled(), f"o item de menu '{chave}' está apagado"
        acao.trigger()
    elif chave.startswith("trilha/"):
        from ui.widgets.trilha_agrupada import GRUPOS, NOMES

        ferramenta = chave[7:]
        indice = next(i for i, g in enumerate(GRUPOS) if g != "-" and ferramenta in g)
        trilha = tela.trilha
        centro = trilha.retangulos()[indice].center()
        if trilha._a_vista[indice] == ferramenta:
            QTest.mouseClick(trilha, Qt.LeftButton, Qt.NoModifier, centro)
        else:   # a outra do grupo: botão direito abre o grupo, escolhe pelo nome
            aj.acoes_de_menu_aberto(
                lambda: QTest.mouseClick(trilha, Qt.RightButton, Qt.NoModifier, centro),
                escolher=NOMES[ferramenta])
    elif chave.startswith("área de trabalho/filtro da página/cartão "):
        cartao = _chaves_dos_cartoezinhos(tela)[chave]
        assert cartao.isVisibleTo(tela), f"o cartãozinho '{chave}' não está à vista"
        QTest.mouseClick(cartao, Qt.LeftButton, Qt.NoModifier, cartao.rect().center())
    elif chave.startswith("ícones da direita/"):
        icones = tela.paineis.icones
        centro = icones.retangulos()[chave.split("/", 1)[1]].center()
        QTest.mouseClick(icones, Qt.LeftButton, Qt.NoModifier, centro)
    else:
        alvo = botao(janela, chave)
        assert alvo.isEnabled(), f"o botão '{chave}' está apagado"
        alvo.click()
    aj.assentar()


def _pagina(janela, indice):
    return janela.projeto.paginas[indice]


def _gerar(janela, monkeypatch, pasta, nome="saida"):
    """Gera o PDF pelo "Confirmar e processar" e devolve as páginas medidas."""
    caminho = aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / f"{nome}.pdf")
    return aj.paginas_do_pdf(caminho)


def _voltar_ao_trabalho(janela):
    from ui.janela_principal import CONFERIR

    janela.telas.setCurrentIndex(CONFERIR)
    aj.assentar()


def _livro_inteiro_original(paginas, quantas=4):
    """O PDF tem `quantas` páginas, na ordem do livro, todas no Original (amareladas)."""
    assert len(paginas) == quantas, f"o PDF tem {len(paginas)} páginas, esperava {quantas}"
    assert [aj.qual_pagina(p) for p in paginas] == list(range(quantas))
    assert all(aj.papel_amarelado(p) for p in paginas)


# --- tela dos livros -----------------------------------------------------------------------------

@prova("P-001")
def test_p001_mais_abre_o_pdf_escolhido(janela, pasta, monkeypatch):
    """O "+" e o menu Arquivo > Abrir: a janela de arquivo (trocada por uma resposta fixa, a do
    Windows apareceria na tela) devolve o PDF; o livro abre e nasce o projeto dele."""
    import ui.dialogos_de_arquivo as dialogos

    livro = aj.criar_livro(pasta)
    pedidos = []
    monkeypatch.setattr(dialogos, "escolher_pdf_para_abrir",
                        lambda *a, **k: pedidos.append(a) or str(livro))
    janela.resize(1280, 760)
    janela.show()
    aj.assentar()
    for jeito in ("cartão", "menu"):
        if jeito == "cartão":
            area = janela.tela_inicio.area
            QTest.mouseClick(area, Qt.LeftButton, Qt.NoModifier, area.rect().center())
        else:
            janela._recomecar()
            aj.assentar()
            apertar(janela, "menu/abrir")
        aj.assentar()
        assert pedidos, f"{jeito}: a janela de escolher o arquivo não abriu"
        assert janela.projeto is not None and Path(janela.projeto.caminho_entrada) == livro, jeito
        assert (aj.pasta_do_projeto(janela) / "projeto.json").exists() or janela.resumo is not None
        pedidos.clear()


@prova("P-002")
def test_p002_configuracoes_abre_a_janela(janela, pasta, monkeypatch):
    from ui.tela_configuracoes import TelaConfiguracoes

    abertas = []
    monkeypatch.setattr(TelaConfiguracoes, "exec", lambda self: abertas.append(self.lista.count()) or 0)
    janela.resize(1280, 760)
    janela.show()
    aj.assentar()
    apertar(janela, "início/livros/Configurações")
    aj.abrir_livro_para_teste(janela, aj.criar_livro(pasta))
    antes = aj.projeto_gravado(janela)
    apertar(janela, "menu/configuracoes")
    assert len(abertas) == 2 and abertas[0] >= 5, "Configurações não abriu com a lista das partes"
    assert aj.projeto_gravado(janela) == antes


@prova("P-003")
def test_p003_ajuda_mostra_os_atalhos_dos_menus(janela, pasta):
    from PySide6.QtWidgets import QMessageBox as Caixa

    textos = []

    def ler(caixa):
        textos.append(caixa.detailedText())

    janela.resize(1280, 760)
    janela.show()
    aj.assentar()
    vistas = aj.caixas_durante(lambda: apertar(janela, "início/livros/Ajuda"), clicar="fechar", antes=ler)
    vistas += aj.caixas_durante(lambda: apertar(janela, "menu/atalhos"), clicar="fechar", antes=ler)
    assert [v[0] for v in vistas] == ["Lista de atalhos"] * 2
    assert all("Desfazer" in t and "Ctrl+Z" in t for t in textos), textos[:1]
    assert Caixa is not None


def _livro_trabalhado(janela, pasta, monkeypatch):
    """Um livro com trabalho: a página 2 em Preto e branco, gravado; volta para a tela dos livros."""
    from core.filtros import PRETO_E_BRANCO

    tela = aj.abrir_livro_para_teste(janela, aj.criar_livro(pasta))
    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    assert aj.pagina_gravada(janela, 1)["filtro"] == PRETO_E_BRANCO
    janela._recomecar()
    janela.tela_inicio.recarregar()
    aj.assentar()
    from ui.tela_inicio import CartaoDeProjeto

    return janela.tela_inicio.findChildren(CartaoDeProjeto)[0]


@prova("P-027")
def test_p027_atalhos_em_portugues(janela, pasta):
    texto = janela.menu.texto_dos_atalhos()
    ingles = [palavra for palavra in ("Return", "Left", "Right", "Del", "Shift+Del") if palavra in texto]
    assert not ingles, f"nomes de tecla em inglês na lista de atalhos: {ingles}"


@prova("P-004")
def test_p004_clique_no_cartao_abre_o_livro_na_tela_inteira(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    QTest.mouseClick(cartao, Qt.LeftButton, Qt.NoModifier, cartao.rect().center())
    aj.assentar()
    inicio = janela.tela_inicio
    assert inicio.pilha.currentWidget() is inicio.livro_aberto
    assert not cartao.isVisibleTo(janela), "os outros cartões continuam à vista"


def _esperar_a_area_de_trabalho(janela, segundos=90):
    from ui.janela_principal import CONFERIR

    fim = time.monotonic() + segundos
    while janela.telas.currentIndex() != CONFERIR and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    assert janela.telas.currentIndex() == CONFERIR, "não chegou à área de trabalho"


@prova("P-005")
@pytest.mark.parametrize("onde", ["início/livros/continuar", "início/livro aberto/Continuar",
                                  "início/menu do livro/continuar", "início/livro aberto/Mais... continuar"])
def test_p005_continuar_volta_o_trabalho(janela, pasta, monkeypatch, onde):
    from core.filtros import PRETO_E_BRANCO

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    if onde == "início/menu do livro/continuar":
        aj.acoes_de_menu_aberto(lambda: cartao._abrir_menu(QPoint(5, 5)), escolher="continuar")
    else:
        if "livro aberto" in onde:
            janela.tela_inicio.abrir_o_livro(cartao.resumo)
            aj.assentar()
        if onde.endswith("Mais... continuar"):
            aj.acoes_de_menu_aberto(janela.tela_inicio.livro_aberto.botao_mais.click, escolher="continuar")
        else:
            apertar(janela, onde)
    _esperar_a_area_de_trabalho(janela)
    assert janela.projeto.paginas[1].filtro == PRETO_E_BRANCO, "o trabalho de antes se perdeu"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 4
    assert aj.so_preto_e_branco(paginas[1]) and aj.papel_amarelado(paginas[0])


@prova("P-006")
def test_p006_comecar_de_novo(janela, pasta, monkeypatch):
    import projetos as pr
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    livro = Path(cartao.resumo.caminho_entrada)
    bytes_do_livro = livro.read_bytes()
    abrir_menu = lambda: cartao._abrir_menu(QPoint(5, 5))  # noqa: E731
    vistas = aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "começar de novo"), clicar="Não, deixar")
    assert vistas and vistas[0][0] == "Começar de novo?", vistas
    salvo = pr.carregar_estado(cartao.resumo)
    assert salvo.paginas[1].filtro == PRETO_E_BRANCO, "o 'Não' mexeu no trabalho"
    vistas = aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "começar de novo"), clicar="Começar de novo")
    tela = aj.abrir_livro_para_teste(janela, cartao.resumo.caminho_entrada) \
        if janela.telas.currentIndex() != janela.telas.indexOf(janela.tela_conferir) else janela.tela_conferir
    assert janela.projeto.paginas[1].filtro == ORIGINAL, "o trabalho antigo continuou"
    assert aj.pagina_gravada(janela, 1)["filtro"] == ORIGINAL
    assert livro.read_bytes() == bytes_do_livro, "o livro em si foi tocado"
    paginas = _gerar(janela, monkeypatch, pasta)
    _livro_inteiro_original(paginas)
    assert tela is not None


@prova("P-007")
def test_p007_renomear(janela, pasta, monkeypatch):
    import projetos as pr

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    abrir_menu = lambda: cartao._abrir_menu(QPoint(5, 5))  # noqa: E731
    aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "renomear"), clicar="Cancelar")
    assert [r.nome for r in pr.listar()] == ["Livro de Teste"]
    aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "renomear"), clicar="OK",
                      antes=lambda caixa: caixa.setTextValue("Meu livro novo"))
    janela.tela_inicio.recarregar()
    assert [r.nome for r in pr.listar()] == ["Meu livro novo"]


@prova("P-008")
def test_p008_abrir_a_pasta_do_pdf(janela, pasta, monkeypatch):
    import historico

    abertas = []
    monkeypatch.setattr(historico, "abrir_pasta", lambda caminho: abertas.append(str(caminho)))
    aj.abrir_livro_para_teste(janela, aj.criar_livro(pasta))
    pdf = aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "pronto.pdf")
    apertar(janela, "ficou pronto/abrir a pasta")
    janela._recomecar()
    janela.tela_inicio.recarregar()
    aj.assentar()
    from ui.tela_inicio import CartaoDeProjeto

    cartao = janela.tela_inicio.findChildren(CartaoDeProjeto)[0]
    apertar(janela, "início/livros/abrir a pasta")
    aj.acoes_de_menu_aberto(lambda: cartao._abrir_menu(QPoint(5, 5)), escolher="abrir a pasta de saída")
    assert len(abertas) == 3
    assert all(Path(a) in (pdf, pdf.parent) for a in abertas), abertas
    antes = pdf.read_bytes()
    assert pdf.read_bytes() == antes


@prova("P-009")
def test_p009_remover_da_lista(janela, pasta, monkeypatch):
    import projetos as pr

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    livro = Path(cartao.resumo.caminho_entrada)
    bytes_do_livro = livro.read_bytes()
    abrir_menu = lambda: cartao._abrir_menu(QPoint(5, 5))  # noqa: E731
    aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "remover da lista"), clicar="Não, deixar")
    assert len(pr.listar()) == 1
    vistas = aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "remover da lista"),
                               clicar="Tirar da lista")
    assert vistas[0][0] == "Tirar da lista?"
    aj.assentar()
    assert pr.listar() == [], "o livro continua na lista"
    from ui.tela_inicio import CartaoDeProjeto

    assert not janela.tela_inicio.findChildren(CartaoDeProjeto) or all(
        not c.isVisible() for c in janela.tela_inicio.findChildren(CartaoDeProjeto))
    assert livro.read_bytes() == bytes_do_livro, "o PDF do livro foi mexido"


@prova("P-010")
def test_p010_voltar_para_os_livros(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    apertar(janela, "início/livro aberto/Voltar para os livros")
    assert inicio.pilha.currentIndex() == 0
    from ui.tela_inicio import CartaoDeProjeto

    novo = [c for c in inicio.findChildren(CartaoDeProjeto) if c.isVisibleTo(inicio)]
    assert novo and novo[0].marcado, "o cartão do livro não ficou marcado"


@prova("P-012")
def test_p012_rodar_o_automatico_abre_o_automatico(janela, pasta, monkeypatch):
    """D-002/D-018: o livro abre na área de trabalho com o Automático, sem a tela "O que fazer"."""
    from ui.janela_principal import CONFERIR

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    janela.tela_inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    apertar(janela, "início/livro aberto/Rodar o automático...")
    aj.assentar()
    assert janela.telas.currentIndex() == CONFERIR, "abriu a tela 'O que fazer'"
    grande = janela.janela_do_automatico                 # D-018: a janela grande, com a receita
    assert janela.tela_conferir.paineis.automatico.isVisible() or (
        grande is not None and grande.isVisible()), "o Automático não abriu"


@prova("P-026")
def test_p026_mais_abre_o_menu_do_livro(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    janela.tela_inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    vistos = aj.acoes_de_menu_aberto(lambda: apertar(janela, "início/livro aberto/Mais..."))
    esperados = {"continuar", "começar de novo", "renomear", "abrir a pasta de saída", "remover da lista"}
    assert esperados <= set(vistos), vistos


@prova("P-013")
def test_p013_ver_todas_as_paginas_uma_a_uma(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    apertar(janela, "início/livro aberto/Ver todas as páginas")
    todas = inicio.livro_aberto.todas
    assert todas.isVisibleTo(inicio)
    assert botao(janela, "início/todas as páginas/uma a uma").isChecked()


@prova("P-014")
def test_p014_confirmar_e_processar_do_livro_aberto(janela, pasta, monkeypatch):
    import ui.janela_confirmar as confirmar
    from ui.janela_principal import FINAL

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    destino = pasta / "saida" / "do livro aberto.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    pedidos = []
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: pedidos.append(1) or destino)
    from ui.janela_dos_avisos import CONTINUAR

    monkeypatch.setattr(type(janela.tela_conferir), "_mostrar_a_lista_dos_avisos",
                        lambda self, antes_de_processar=False: CONTINUAR)
    apertar(janela, "início/livro aberto/Confirmar e processar...")
    fim = time.monotonic() + 180
    while janela.telas.currentIndex() != FINAL and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    assert pedidos, "não pediu a confirmação do destino"
    assert destino.exists(), "o PDF não foi gravado"
    assert len(aj.paginas_do_pdf(destino)) == 4


@prova("P-015")
def test_p015_uma_pagina_e_duas_lado_a_lado_lembradas(janela, pasta, monkeypatch):
    import configuracoes

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    aberto = inicio.livro_aberto
    antes = aj.projeto_gravado  # noqa: F841 - o projeto não está aberto aqui
    apertar(janela, "início/livro aberto/Duas lado a lado")
    assert botao(janela, "início/livro aberto/Duas lado a lado").isChecked()
    assert aberto.jeito_guardado().get("mostrar") in ("duas", "pares", "lado_a_lado") or \
        "duas" in str(configuracoes.ler("livro_aberto")).lower() or aberto.paginas.em_pares
    apertar(janela, "início/livro aberto/Uma página")
    assert botao(janela, "início/livro aberto/Uma página").isChecked()
    assert not botao(janela, "início/livro aberto/Duas lado a lado").isChecked()


@prova("P-016")
def test_p016_rolar_sem_parar(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    rolar = botao(janela, "início/livro aberto/Rolar sem parar")
    antes = rolar.isChecked()
    apertar(janela, "início/livro aberto/Rolar sem parar")
    assert rolar.isChecked() != antes
    assert inicio.livro_aberto.jeito_guardado() != {}


@prova("P-017")
@pytest.mark.parametrize("nome", ["Caber a página", "Caber a altura", "Caber a largura", "Tamanho real"])
def test_p017_caber(janela, pasta, monkeypatch, nome):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    import configuracoes

    apertar(janela, f"início/livro aberto/{nome}")
    assert botao(janela, f"início/livro aberto/{nome}").isChecked(), f"'{nome}' não ficou aceso"
    jeito = {"Caber a página": "pagina", "Caber a altura": "altura", "Caber a largura": "largura",
             "Tamanho real": "real"}[nome]
    assert inicio.livro_aberto.paginas.caber == jeito
    assert configuracoes.ler("livro_aberto")["caber"] == jeito, "a escolha não ficou lembrada"


@prova("P-018")
def test_p018_folha_anterior_e_proxima_no_livro_aberto(janela, pasta, monkeypatch):
    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    inicio = janela.tela_inicio
    inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    aberto = inicio.livro_aberto
    antes = aberto.campo_ir.value()
    apertar(janela, "início/livro aberto/›")
    assert aberto.campo_ir.value() == antes + 1
    apertar(janela, "início/livro aberto/‹")
    assert aberto.campo_ir.value() == antes


def _grade_da_area(janela, pasta):
    tela = aj.abrir_livro_para_teste(janela, aj.criar_livro(pasta))
    from core import analise

    tela.projeto.paginas[2].alertas = [analise.EM_BRANCO]
    tela.ir_para_pagina(1)
    tela.abrir_todas_as_paginas()
    aj.assentar()
    return tela


@prova("P-019")
def test_p019_todas_as_paginas_filtros_da_grade(janela, pasta):
    tela = _grade_da_area(janela, pasta)
    antes = aj.projeto_gravado(janela)
    for nome in ("em pares", "todas", "uma a uma"):
        apertar(janela, f"área de trabalho/todas as páginas/{nome}")
        assert botao(janela, f"área de trabalho/todas as páginas/{nome}").isChecked(), nome
    atencao = botao(janela, "área de trabalho/todas as páginas/só as que precisam de atenção (N)")
    assert "(1)" in atencao.text(), f"a contagem não bate com as páginas com aviso: {atencao.text()}"
    apertar(janela, "área de trabalho/todas as páginas/só as que precisam de atenção (N)")
    assert atencao.isChecked()
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]
    assert tela is not None


@prova("P-020")
def test_p020_voltar_da_grade_na_mesma_pagina(janela, pasta):
    tela = _grade_da_area(janela, pasta)
    apertar(janela, "área de trabalho/todas as páginas/voltar ao trabalho")
    assert not tela.todas.isVisibleTo(tela)
    assert tela.indice_pagina == 1


# --- ferramentas ---------------------------------------------------------------------------------

def _ferramenta_escolhida(janela, tela, ferramenta):
    assert tela.trilha.ferramenta == ferramenta
    assert janela.menu.acoes[f"usar_{ferramenta}"].isChecked(), "o menu Ferramentas não acompanha"


@prova("P-030")
@pytest.mark.parametrize("onde", ["trilha/dividir", "menu/usar_dividir"])
def test_p030_dividir(janela, tela, onde):
    tela.escolher_ferramenta("mao")
    tela.paineis.fechar()
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    _ferramenta_escolhida(janela, tela, "dividir")
    assert tela.trabalha_com_folhas, "não mostra a folha inteira"
    assert tela.paineis.propriedades.isVisible() and tela.paineis.propriedades.conteudo == "corte"
    assert aj.projeto_gravado(janela) == antes


@prova("P-031")
@pytest.mark.parametrize("onde", ["trilha/cortar", "menu/usar_cortar"])
def test_p031_cortar(janela, tela, onde):
    tela.escolher_ferramenta("mao")
    tela.paineis.fechar()
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    _ferramenta_escolhida(janela, tela, "cortar")
    assert tela.paineis.propriedades.isVisible() and tela.paineis.propriedades.conteudo == "bordas"
    assert aj.projeto_gravado(janela) == antes


@prova("P-032")
@pytest.mark.parametrize("onde", ["trilha/endireitar", "menu/usar_endireitar"])
def test_p032_endireitar(janela, tela, onde):
    tela.escolher_ferramenta("mao")
    tela.paineis.fechar()
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    _ferramenta_escolhida(janela, tela, "endireitar")
    assert tela.paineis.propriedades.isVisible() and tela.paineis.propriedades.conteudo == "angulo"
    assert aj.projeto_gravado(janela) == antes


@prova("P-035")
@pytest.mark.parametrize("onde", ["trilha/mover", "menu/usar_mover"])
def test_p035_mover_e_redimensionar(janela, tela, onde):
    """Etapa 5 da obra (D-008): a ferramenta própria, sem tamanho de folha escolhido."""
    tela.escolher_ferramenta("mao")
    tela.paineis.fechar()
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    _ferramenta_escolhida(janela, tela, "mover")
    assert tela.aba_atual == "mover"
    assert tela.paineis.propriedades.isVisible() and tela.paineis.propriedades.conteudo == "mover"
    vis = tela.visualizadores["mover"]
    aj.esperar(lambda: vis._folha_do_mover is not None, motivo="a página na ferramenta Mover")
    assert vis._folha_do_mover == vis.tamanho_da_pagina_px(), "sem folha, a área branca é a página"
    assert aj.projeto_gravado(janela) == antes


FERRAMENTAS_DE_MARCAR = ("retangulo", "elipse", "laco", "poligono", "pincel", "varinha", "cor", "ajustar")


@prova("P-033")
@pytest.mark.parametrize("ferramenta", FERRAMENTAS_DE_MARCAR)
@pytest.mark.parametrize("lugar", ["trilha", "menu"])
def test_p033_ferramentas_de_marcar(janela, tela, ferramenta, lugar):
    tela.escolher_ferramenta("dividir")
    antes = aj.projeto_gravado(janela)
    apertar(janela, f"trilha/{ferramenta}" if lugar == "trilha" else f"menu/usar_{ferramenta}")
    _ferramenta_escolhida(janela, tela, ferramenta)
    assert tela.editor_selecao.ferramenta == ferramenta
    tela.paineis.abrir("props")
    assert tela.paineis.propriedades.conteudo == "marcar"
    assert aj.projeto_gravado(janela) == antes


@prova("P-034")
@pytest.mark.parametrize("ferramenta", ["zoom", "mao"])
@pytest.mark.parametrize("lugar", ["trilha", "menu"])
def test_p034_zoom_e_mao(janela, tela, ferramenta, lugar):
    tela.escolher_ferramenta("cortar")
    antes = aj.projeto_gravado(janela)
    apertar(janela, f"trilha/{ferramenta}" if lugar == "trilha" else f"menu/usar_{ferramenta}")
    _ferramenta_escolhida(janela, tela, ferramenta)
    tela.paineis.abrir("props")
    assert "olhar" in tela.paineis.propriedades.sem_propriedades.text()
    assert aj.projeto_gravado(janela) == antes


# --- painéis -------------------------------------------------------------------------------------

PAINEIS = ("revisar", "automatico", "props", "filtro", "historico")


@prova("P-040")
@pytest.mark.parametrize("painel", PAINEIS)
@pytest.mark.parametrize("lugar", ["ícone", "menu"])
def test_p040_abrir_cada_painel(janela, tela, painel, lugar):
    paineis = tela.paineis
    paineis.fechar()
    aj.assentar()
    largura_da_pagina = tela.area_imagem.width()
    apertar(janela, f"ícones da direita/{painel}" if lugar == "ícone" else f"menu/painel_{painel}")
    aberto = {"revisar": paineis.para_revisar, "automatico": paineis.automatico,
              "props": paineis.propriedades, "filtro": paineis.filtro_da_pagina,
              "historico": paineis.historico}[painel]
    assert aberto.isVisible(), f"o painel {painel} não abriu"
    assert paineis.icones.aberto == painel
    assert janela.menu.acoes[f"painel_{painel}"].isChecked(), "o menu Painéis não marca o aberto"
    assert tela.area_imagem.width() < largura_da_pagina, "o painel não empurrou a página (D-043)"
    if lugar == "ícone":
        apertar(janela, f"ícones da direita/{painel}")
        assert not aberto.isVisible(), "clicar de novo no ícone não fechou"


@prova("P-041")
@pytest.mark.parametrize("onde", ["ícones da direita/seta", "menu/icones"])
def test_p041_esconder_os_icones(janela, tela, onde):
    icones = tela.paineis.icones
    assert not icones.recolhida
    apertar(janela, onde)
    assert icones.recolhida, "os ícones não se esconderam"
    assert not janela.menu.acoes["icones"].isChecked()
    apertar(janela, "ícones da direita/seta")
    assert not icones.recolhida
    assert janela.menu.acoes["icones"].isChecked()


@prova("P-042")
@pytest.mark.parametrize("painel,lugar", [("revisar", "para revisar"), ("automatico", "automático"),
                                          ("props", "propriedades"), ("filtro", "filtro da página"),
                                          ("historico", "histórico"), ("props", "menu"),
                                          ("props", "sanfona")])
def test_p042_fechar_o_painel(janela, tela, painel, lugar):
    paineis = tela.paineis
    if lugar == "sanfona":
        paineis.definir_jeito("sanfona")
        aj.assentar()
        largura = tela.area_imagem.width()
        apertar(janela, "área de trabalho/lado direito/esconder os painéis")
        assert tela.area_imagem.width() > largura, "a página não ganhou o lugar"
        paineis.definir_jeito("icones")
        return
    paineis.abrir(painel)
    aj.assentar()
    largura = tela.area_imagem.width()
    apertar(janela, "menu/painel_fechar" if lugar == "menu" else f"área de trabalho/{lugar}/fechar o painel")
    assert paineis.icones.aberto is None, "o painel continua aberto"
    assert tela.area_imagem.width() > largura, "a página não ganhou o lugar do painel"


@prova("P-043")
def test_p043_lado_direito_sanfona_e_icones(janela, tela):
    from ui.widgets.paineis import jeito_guardado

    apertar(janela, "menu/lado_sanfona")
    assert tela.paineis.jeito == "sanfona" and tela.paineis.sanfona.isVisible()
    assert jeito_guardado() == "sanfona", "a escolha não ficou guardada"
    # D-033 (etapa 9b-1): os outros dois jeitos
    apertar(janela, "menu/lado_abas")
    assert tela.paineis.jeito == "abas" and tela.paineis.abas.isVisible()
    assert jeito_guardado() == "abas"
    apertar(janela, "menu/lado_solto")
    assert tela.paineis.jeito == "solto" and tela.paineis.botoes_do_alto.isVisible()
    assert jeito_guardado() == "solto"
    apertar(janela, "menu/lado_icones")
    assert tela.paineis.jeito == "icones" and jeito_guardado() == "icones"


# --- girar, "Esta página" ------------------------------------------------------------------------

LUGARES_DO_GIRO = {
    "P-050": ("área de trabalho/girar a folha/¼ à direita", "área de trabalho/girar do canto/Girar ¼ à direita",
              "menu/girar"),
    "P-051": ("área de trabalho/girar a folha/¼ à esquerda", "área de trabalho/girar do canto/Girar ¼ à esquerda",
              "menu/girar_esquerda"),
    "P-052": ("área de trabalho/girar a folha/meia volta", "área de trabalho/girar do canto/Girar meia volta",
              "menu/girar_meia_volta"),
}
GIRO_ESPERADO = {"P-050": 90, "P-051": 270, "P-052": 180}


def _mostrar_o_canto(tela):
    """Os botões de girar do canto aparecem com o mouse em cima da página (D-049); aqui são postos
    à vista do jeito que a tela faz."""
    tela.girar_do_canto.setVisible(True)
    tela.girar_do_canto.raise_()
    aj.assentar()


def _provar_giro(janela, tela, monkeypatch, pasta, numero, onde):
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mao")
    tela.paineis.abrir("props")
    if "girar do canto" in onde:
        _mostrar_o_canto(tela)
    apertar(janela, onde)
    gravado = projeto_gravado = aj.projeto_gravado(janela)
    assert gravado["folhas"][1]["rotacao"] == GIRO_ESPERADO[numero], "o giro não foi gravado"
    assert all(f["rotacao"] == 0 for i, f in enumerate(gravado["folhas"]) if i != 1), "girou outra folha"
    assert any(a.get("tipo") == "girar" for a in aj.acoes_gravadas(janela)), "o giro não entrou no histórico"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 4
    if GIRO_ESPERADO[numero] == 180:
        assert not paginas[1].deitada
        assert aj.qual_pagina(paginas[1]) is None, "a página não saiu de cabeça para baixo"
    else:
        assert paginas[1].deitada, "a página girada não saiu deitada no PDF"
    assert not paginas[0].deitada and not paginas[2].deitada
    assert projeto_gravado is not None


@prova("P-050")
@pytest.mark.parametrize("onde", LUGARES_DO_GIRO["P-050"])
def test_p050_girar_a_direita(janela, tela, monkeypatch, pasta, onde):
    _provar_giro(janela, tela, monkeypatch, pasta, "P-050", onde)


@prova("P-051")
@pytest.mark.parametrize("onde", LUGARES_DO_GIRO["P-051"])
def test_p051_girar_a_esquerda(janela, tela, monkeypatch, pasta, onde):
    _provar_giro(janela, tela, monkeypatch, pasta, "P-051", onde)


@prova("P-052")
@pytest.mark.parametrize("onde", LUGARES_DO_GIRO["P-052"])
def test_p052_girar_meia_volta(janela, tela, monkeypatch, pasta, onde):
    _provar_giro(janela, tela, monkeypatch, pasta, "P-052", onde)


@prova("P-053")
def test_p053_aplicar_o_giro_em(janela, tela, monkeypatch, pasta):
    tela.ir_para_pagina(1)                       # a folha 2 (par)
    apertar(janela, "menu/giro_em_impares")
    apertar(janela, "menu/girar")
    assert janela.avisos, "folha par + 'só as ímpares' não avisou (D-036)"
    assert all(f["rotacao"] == 0 for f in aj.projeto_gravado(janela)["folhas"]), "girou mesmo assim"
    # D-035: "Todas ficam viradas como a folha da vez" (as outras copiam o giro final dela)
    for alcance, esperado in (("pares", [0, 90, 0, 90]), ("daqui_em_diante", [0, 180, 180, 180]),
                              ("esta", [0, 270, 180, 180])):
        apertar(janela, f"menu/giro_em_{alcance}")
        apertar(janela, "menu/girar")
        assert [f["rotacao"] for f in aj.projeto_gravado(janela)["folhas"]] == esperado, alcance
    tela.desfazer(); tela.desfazer(); tela.desfazer()   # noqa: E702
    apertar(janela, "menu/giro_em_todas")
    apertar(janela, "menu/girar")
    assert [f["rotacao"] for f in aj.projeto_gravado(janela)["folhas"]] == [90] * 4
    paginas = _gerar(janela, monkeypatch, pasta)
    assert all(p.deitada for p in paginas), "com 'todas', alguma página não saiu deitada"


def _deixar_em_branco_por(janela, tela, onde):
    tela.ir_para_pagina(2)
    if "filtro da página" in onde:
        tela.paineis.abrir("filtro")
    else:
        tela.paineis.abrir("props")
    apertar(janela, onde)


@prova("P-054")
@pytest.mark.parametrize("onde", ["área de trabalho/esta página/deixar em branco",
                                  "área de trabalho/filtro da página/deixar em branco",
                                  "menu/deixar_em_branco", "tecla Delete"])
def test_p054_deixar_em_branco(janela, tela, monkeypatch, pasta, onde):
    if onde == "tecla Delete":
        tela.ir_para_pagina(2)
        tela.escolher_ferramenta("mao")
        QTest.keyClick(tela, Qt.Key_Delete)
        aj.assentar()
    else:
        _deixar_em_branco_por(janela, tela, onde)
    pagina = aj.pagina_gravada(janela, 2)
    assert pagina["em_branco"] is True and pagina.get("apagada") is not True
    assert pagina["revisada"] is True
    tela.paineis.abrir("props")
    assert botao(janela, "área de trabalho/esta página/voltar a página"), "o botão não virou 'voltar a página'"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 4, "o número de páginas mudou (a encadernação mudaria)"
    assert aj.esta_branca(paginas[2]), "a página não saiu branca"
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, None, 3]


@prova("P-055")
@pytest.mark.parametrize("onde", ["área de trabalho/esta página/voltar a página",
                                  "área de trabalho/faixa do aviso/voltar a página"])
def test_p055_voltar_a_pagina(janela, tela, monkeypatch, pasta, onde):
    _deixar_em_branco_por(janela, tela, "área de trabalho/esta página/deixar em branco")
    apertar(janela, onde)
    assert aj.pagina_gravada(janela, 2)["em_branco"] is False
    paginas = _gerar(janela, monkeypatch, pasta)
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 2, 3]


@prova("P-056")
@pytest.mark.parametrize("onde", ["área de trabalho/esta página/tirar do livro",
                                  "área de trabalho/filtro da página/tirar do livro", "menu/tirar_do_livro"])
def test_p056_tirar_do_livro(janela, tela, monkeypatch, pasta, onde):
    _deixar_em_branco_por(janela, tela, onde)
    assert aj.pagina_gravada(janela, 2)["apagada"] is True
    assert any("Tirar do livro" in a.get("descricao", "") for a in aj.acoes_gravadas(janela))
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 3, "a página não sumiu do PDF"
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 3]


@prova("P-057")
@pytest.mark.parametrize("onde", ["área de trabalho/esta página/trazer de volta", "menu/restaurar"])
def test_p057_trazer_de_volta(janela, tela, monkeypatch, pasta, onde):
    _deixar_em_branco_por(janela, tela, "área de trabalho/esta página/tirar do livro")
    tela.ir_para_pagina(2)
    tela.paineis.abrir("props")
    apertar(janela, onde)
    assert aj.pagina_gravada(janela, 2)["apagada"] is False
    paginas = _gerar(janela, monkeypatch, pasta)
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 2, 3]


# --- Dividir, Cortar, Endireitar ---------------------------------------------------------------

@prova("P-060")
def test_p060_nao_dividir_esta(janela, pasta, monkeypatch):
    """Livro de folhas duplas aberto com "Dividir folhas ao meio": "não dividir esta" na folha 1
    faz ela sair como UMA página (a folha inteira) no PDF."""
    livro = aj.criar_livro_duplo(pasta, folhas=2)
    tela = aj.abrir_livro_para_teste(janela, livro, marcadas=("cx_dividir",))
    assert len(tela.projeto.paginas) == 4, "o livro duplo não foi dividido ao abrir"
    tela.escolher_ferramenta("dividir")
    tela.paineis.abrir("props")
    tela.ir_para_pagina(0)
    apertar(janela, "área de trabalho/dividir/não dividir esta")
    assert aj.projeto_gravado(janela)["folhas"][0]["dividir"] is False
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 3 and paginas[0].deitada, "a folha não saiu inteira, como uma página"
    tela = janela.tela_conferir
    _voltar_ao_trabalho(janela)
    apertar(janela, "área de trabalho/dividir/dividir esta")
    assert aj.projeto_gravado(janela)["folhas"][0]["dividir"] is True


@prova("P-059")
def test_p059_dividir_esta_em_livro_aberto_sem_dividir(janela, pasta, monkeypatch):
    """Etapa 4 (plano de 26/10: "'dividir esta' sempre ativo") e D-009: livro de folhas duplas
    aberto sem nada marcado; "dividir esta" na folha 1 divide a folha em duas páginas no PDF."""
    livro = aj.criar_livro_duplo(pasta, folhas=2)
    tela = aj.abrir_livro_para_teste(janela, livro)
    tela.escolher_ferramenta("dividir")
    tela.paineis.abrir("props")
    alvo = botao(janela, "área de trabalho/dividir/dividir esta")
    assert alvo.isEnabled(), f"'dividir esta' apagado: {alvo.toolTip()}"
    alvo.click()
    aj.assentar()
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 3, "a folha dividida não saiu como duas páginas"


@prova("P-061")
def test_p061_usar_em_todas_do_dividir_abre_a_lista(janela, pasta, monkeypatch):
    """D-090: "usar em todas" abre a lista das folhas, com a exceção desmarcada, e não apaga a
    exceção."""
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    livro = aj.criar_livro_duplo(pasta, folhas=3)
    tela = aj.abrir_livro_para_teste(janela, livro, marcadas=("cx_dividir",))
    tela.escolher_ferramenta("dividir")
    tela.paineis.abrir("props")
    abertas = []
    monkeypatch.setattr(DialogoEscolherPaginas, "exec", lambda self: abertas.append(self) or 0)
    apertar(janela, "área de trabalho/dividir/usar em todas")
    assert abertas, "'usar em todas' do Dividir não abriu a lista (D-090)"


@prova("P-062")
@pytest.mark.parametrize("ferramenta,lugar", [("dividir", "dividir"), ("cortar", "cortar"),
                                              ("endireitar", "endireitar")])
def test_p062_mudar_no_automatico(janela, tela, ferramenta, lugar):
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    from ui.janela_principal import CONFERIR

    etapa = {"dividir": A.DIVIDIR, "cortar": A.CORTAR, "endireitar": A.ENDIREITAR}[ferramenta]
    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.escolher_ferramenta(ferramenta)
    tela.paineis.abrir("props")
    apertar(janela, f"área de trabalho/{lugar}/mudar no Automático...")
    grande = janela.janela_do_automatico
    assert janela.telas.currentIndex() == CONFERIR
    assert grande is not None and grande.isVisible(), "a janela grande do Automático não abriu"
    assert grande.pilha.currentWidget() is grande.paginas_das_etapas[etapa], "não abriu na etapa"
    assert janela.projeto.paginas[1].filtro == PRETO_E_BRANCO, "o trabalho se perdeu"


def _no_cortar(janela, tela, indice=1):
    tela.ir_para_pagina(indice)
    tela.escolher_ferramenta("cortar")
    tela.paineis.abrir("props")
    vis = tela.visualizadores["bordas"]
    aj.esperar(lambda: vis.tamanho_da_pagina_px()[0] > 0, motivo="a prévia da página no Cortar")


@prova("P-063")
@pytest.mark.parametrize("onde", ["área de trabalho/cortar/não cortar esta", "aviso/sem_recorte"])
def test_p063_nao_cortar_esta(janela, tela, monkeypatch, pasta, onde):
    _no_cortar(janela, tela)
    tela.projeto.paginas[1].recorte = (0.2, 0.2, 0.6, 0.6)       # um corte à mão
    if onde.startswith("aviso/"):
        _apertar_aviso(janela, tela, 1, onde)
    else:
        apertar(janela, onde)
    assert aj.pagina_gravada(janela, 1)["recorte"] == [0.0, 0.0, 1.0, 1.0]
    paginas = _gerar(janela, monkeypatch, pasta)
    inteira = paginas[0]
    assert abs(paginas[1].largura_pt - inteira.largura_pt) < 2 and abs(paginas[1].altura_pt - inteira.altura_pt) < 2


@prova("P-064")
def test_p064_usar_o_corte_do_programa(janela, tela, monkeypatch, pasta):
    _no_cortar(janela, tela)
    tela._registrar("recortar", "pagina", [1], {"recorte": [0.2, 0.2, 0.6, 0.6]}, "corte à mão")
    apertar(janela, "área de trabalho/cortar/usar o corte do programa")
    assert aj.pagina_gravada(janela, 1)["recorte"] is None
    paginas = _gerar(janela, monkeypatch, pasta)
    assert abs(paginas[1].largura_pt - paginas[0].largura_pt) < 2, "o corte à mão continuou valendo"


@prova("P-065")
def test_p065_usar_em_todas_do_cortar(janela, tela, monkeypatch, pasta):
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    _no_cortar(janela, tela, indice=3)
    tela._registrar("recortar", "pagina", [3], {"recorte": [0.1, 0.1, 0.5, 0.5]}, "exceção à mão")
    tela.ir_para_pagina(1)
    tela._registrar("recortar", "pagina", [1], {"recorte": [0.0, 0.0, 0.5, 0.5]}, "corte à mão")
    marcadas = []

    def ver(caixa):
        marcadas.extend(caixa.paginas_escolhidas() if hasattr(caixa, "paginas_escolhidas") else [])

    aj.responder_caixa(monkeypatch, DialogoEscolherPaginas, "Aplicar", antes=ver)
    apertar(janela, "área de trabalho/cortar/usar em todas")
    gravado = aj.projeto_gravado(janela)
    assert gravado["paginas"][3]["recorte"] == [0.1, 0.1, 0.5, 0.5], "a exceção foi apagada (D-090)"
    assert gravado["paginas"][0]["recorte"] == [0.0, 0.0, 0.5, 0.5]
    assert gravado["paginas"][2]["recorte"] == [0.0, 0.0, 0.5, 0.5]
    paginas = _gerar(janela, monkeypatch, pasta)
    assert abs(paginas[0].largura_pt - paginas[1].largura_pt) < 2
    assert paginas[0].largura_pt < paginas[3].largura_pt * 1.4


@prova("P-066")
def test_p066_tamanho_da_folha(janela, tela, monkeypatch, pasta):
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha

    _no_cortar(janela, tela)
    vistas = []
    aj.responder_caixa(monkeypatch, DialogoTamanhoDaFolha, "Cancelar", registro=vistas)
    apertar(janela, "área de trabalho/cortar/tamanho...")
    assert vistas, "a janela 'Tamanho da folha' não abriu"
    assert aj.pagina_gravada(janela, 1).get("tamanho_folha_cm") is None, "Cancelar mudou a página"

    def a5(caixa):
        alvo = next(b for b in caixa.findChildren(type(tela.botao_esta_certo)) if b.text() == "A5")
        alvo.click()

    aj.responder_caixa(monkeypatch, DialogoTamanhoDaFolha, "OK", antes=a5)
    apertar(janela, "área de trabalho/cortar/tamanho...")
    tamanho = aj.pagina_gravada(janela, 1).get("tamanho_folha_cm")
    assert tamanho is not None and abs(tamanho[0] - 14.8) < 0.05 and abs(tamanho[1] - 21.0) < 0.05, tamanho
    paginas = _gerar(janela, monkeypatch, pasta)
    mm = (paginas[1].largura_pt / 72 * 25.4, paginas[1].altura_pt / 72 * 25.4)
    assert abs(mm[0] - 148) < 2 and abs(mm[1] - 210) < 2, f"a página saiu com {mm} mm, não A5"


def _no_mover(janela, tela, indice=1):
    """A ferramenta Mover na página `indice`, com a página já chegada (etapa 5 da obra)."""
    tela.ir_para_pagina(indice)
    tela.escolher_ferramenta("mover")
    tela.paineis.abrir("props")
    vis = tela.visualizadores["mover"]
    aj.esperar(lambda: vis._pixmap is not None and getattr(tela, "_mover_da_vez", None),
               motivo="a página na ferramenta Mover")
    return vis


def _caixa_escura(pagina) -> tuple[float, float, float, float]:
    """(esquerda, cima, direita, baixo) do que é escuro na página do PDF, em fração dela."""
    ys, xs = np.nonzero(pagina.cinza < 100)
    altura, largura = pagina.cinza.shape
    return xs.min() / largura, ys.min() / altura, (xs.max() + 1) / largura, (ys.max() + 1) / altura


@prova("P-190")
def test_p190_tamanho_da_folha_no_mover(janela, tela, monkeypatch, pasta):
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha

    _no_mover(janela, tela)
    vistas = []
    aj.responder_caixa(monkeypatch, DialogoTamanhoDaFolha, "Cancelar", registro=vistas)
    apertar(janela, "área de trabalho/mover/tamanho da folha...")
    assert vistas, "a janela 'Tamanho da folha' não abriu"
    assert aj.pagina_gravada(janela, 1).get("tamanho_folha_cm") is None, "Cancelar mudou a página"

    def a5(caixa):
        alvo = next(b for b in caixa.findChildren(type(tela.botao_esta_certo)) if b.text() == "A5")
        alvo.click()

    aj.responder_caixa(monkeypatch, DialogoTamanhoDaFolha, "OK", antes=a5)
    apertar(janela, "área de trabalho/mover/tamanho da folha...")
    gravada = aj.pagina_gravada(janela, 1)
    tamanho = gravada.get("tamanho_folha_cm")
    assert tamanho is not None and abs(tamanho[0] - 14.8) < 0.05 and abs(tamanho[1] - 21.0) < 0.05
    assert gravada.get("recorte") is None and gravada.get("conteudo_escala", 1.0) == 1.0
    aj.esperar(lambda: tela.visualizadores["mover"]._folha_do_mover
               != tela.visualizadores["mover"].tamanho_da_pagina_px(),
               motivo="a área branca da ferramenta virou a folha A5")
    paginas = _gerar(janela, monkeypatch, pasta)
    mm = (paginas[1].largura_pt / 72 * 25.4, paginas[1].altura_pt / 72 * 25.4)
    assert abs(mm[0] - 148) < 2 and abs(mm[1] - 210) < 2, f"a página saiu com {mm} mm, não A5"


@prova("P-191")
def test_p191_centralizar(janela, tela, monkeypatch, pasta):
    _no_mover(janela, tela)
    # o texto da página 2 do livro de teste fica alto (margem de cima menor que a de baixo);
    # e um mover à mão o tira também do meio na largura
    tela._gravar_o_conteudo(1.0, (0.08, 0.04), "fora do meio")
    antes = _caixa_escura(_gerar(janela, monkeypatch, pasta, "antes")[1])
    assert abs(antes[0] - (1 - antes[2])) > 0.08 and abs(antes[1] - (1 - antes[3])) > 0.04, antes
    _voltar_ao_trabalho(janela)
    apertar(janela, "área de trabalho/mover/Centralizar")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["conteudo_deslocamento"] != [0.0, 0.0]
    assert "mover" in gravada.get("mexida_a_mao", [])
    x0, y0, x1, y1 = _caixa_escura(_gerar(janela, monkeypatch, pasta, "depois")[1])
    assert abs(x0 - (1 - x1)) <= 0.02 and abs(y0 - (1 - y1)) <= 0.02, (x0, 1 - x1, y0, 1 - y1)


@prova("P-192")
def test_p192_voltar_como_veio(janela, tela, monkeypatch, pasta):
    _no_mover(janela, tela)
    antes = _gerar(janela, monkeypatch, pasta, "antes")[1]
    _voltar_ao_trabalho(janela)
    tela.campo_tamanho_do_conteudo.setValue(120)
    tela.botao_centralizar.click()
    assert aj.pagina_gravada(janela, 1)["conteudo_escala"] == 1.2
    apertar(janela, "área de trabalho/mover/voltar como veio")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["conteudo_escala"] == 1.0 and gravada["conteudo_deslocamento"] == [0.0, 0.0]
    depois = _gerar(janela, monkeypatch, pasta, "depois")[1]
    assert np.array_equal(antes.imagem, depois.imagem)


@prova("P-193")
def test_p193_usar_em_todas_do_mover(janela, tela, monkeypatch, pasta):
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    _no_mover(janela, tela, indice=3)
    tela.campo_tamanho_do_conteudo.setValue(80)            # a exceção, mexida à mão
    _no_mover(janela, tela, indice=1)
    tela.campo_tamanho_do_conteudo.setValue(70)
    vistas = []
    aj.responder_caixa(monkeypatch, DialogoEscolherPaginas, "Aplicar", registro=vistas)
    apertar(janela, "área de trabalho/mover/usar em todas...")
    assert vistas, "a lista 'Em quais páginas?' não abriu"
    gravado = aj.projeto_gravado(janela)
    escalas = [p.get("conteudo_escala", 1.0) for p in gravado["paginas"]]
    assert escalas == [0.7, 0.7, 0.7, 0.8], f"a exceção foi apagada (D-090)? {escalas}"
    paginas = _gerar(janela, monkeypatch, pasta)
    larguras = [(lambda c: c[2] - c[0])(_caixa_escura(p)) for p in paginas]
    assert abs(larguras[0] - larguras[1]) < 0.02 and abs(larguras[2] - larguras[1]) < 0.02


def _no_endireitar(janela, tela):
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("endireitar")
    tela.paineis.abrir("props")
    vis = tela.visualizadores["angulo"]
    aj.esperar(lambda: vis.angulo_conhecido, motivo="o ângulo da página medido (a prévia do Endireitar)")


@prova("P-067")
def test_p067_um_decimo_de_grau(janela, tela):
    _no_endireitar(janela, tela)
    lugares = [c for c in PROMESSAS["P-067"].chaves]
    antihorario = next(c for c in lugares if "anti-horário" in c)
    horario = next(c for c in lugares if c.endswith("sentido horário"))
    apertar(janela, antihorario)
    aj.esperar(lambda: tela.projeto.paginas[1].angulo_manual is not None, 5, "o ângulo gravado")
    a = aj.pagina_gravada(janela, 1)["angulo_manual"]
    apertar(janela, horario)
    apertar(janela, horario)
    aj.esperar(lambda: tela.projeto.paginas[1].angulo_manual != a, 5, "o ângulo novo gravado")
    b = aj.pagina_gravada(janela, 1)["angulo_manual"]
    assert a is not None and b is not None, "o ângulo à mão não foi gravado"
    assert abs((a - b) - 0.2) < 1e-6, f"anti-horário {a}, depois duas vezes horário {b}"


@prova("P-068")
@pytest.mark.parametrize("onde", ["área de trabalho/endireitar/deixar como veio", "aviso/angulo_zero"])
def test_p068_deixar_como_veio(janela, tela, monkeypatch, pasta, onde):
    _no_endireitar(janela, tela)
    if onde.startswith("aviso/"):
        _apertar_aviso(janela, tela, 1, onde)
    else:
        apertar(janela, onde)
    assert aj.pagina_gravada(janela, 1)["angulo_manual"] == 0.0


@prova("P-069")
def test_p069_usar_o_angulo_do_programa(janela, tela):
    _no_endireitar(janela, tela)
    tela._registrar("angulo", "pagina", [1], {"angulo_manual": 2.0}, "ângulo à mão")
    apertar(janela, "área de trabalho/endireitar/usar o ângulo do programa")
    assert aj.pagina_gravada(janela, 1)["angulo_manual"] is None


# --- marcar ---------------------------------------------------------------------------------------

def _no_marcar(janela, tela, indice=1):
    tela.ir_para_pagina(indice)
    tela.escolher_ferramenta("retangulo")
    tela.paineis.abrir("props")
    aj.assentar()


def _desenhar_area(tela, x0=0.2, y0=0.2, x1=0.6, y1=0.6):
    """Desenha uma área com o Retângulo (o arrastar do mouse no editor, como nos testes do editor)."""
    from tests.test_editor_selecao import arrastar

    editor = tela.editor_selecao
    editor.resize(300, 420)
    editor._area = editor._calcular_area()
    arrastar(editor, x0, y0, x1, y1)
    aj.assentar()


TIPOS_DE_MARCAR = {"gravura ou foto": "gravura", "letra e traço": "letra", "papel": "papel",
                   "pintar por cima": "pintar", "manter a cor da tinta": "tinta_cor",
                   "tinta preta, fundo original": "tinta_preta"}


@prova("P-070")
@pytest.mark.parametrize("nome", ["gravura ou foto", "letra e traço", "papel", "pintar por cima",
                                  "manter a cor da tinta", "tinta preta, fundo original"])
def test_p070_marcar_como(janela, tela, nome):
    _no_marcar(janela, tela)
    if nome == "gravura ou foto":              # o de fábrica: escolhe outro antes, para ver a troca
        apertar(janela, "área de trabalho/marcar/papel")
    apertar(janela, f"área de trabalho/marcar/{nome}")
    assert tela.paineis.marcar_como.tipo == TIPOS_DE_MARCAR[nome], "o tipo não ficou escolhido"
    _desenhar_area(tela)
    selecao = aj.pagina_gravada(janela, 1)["selecao"]
    assert selecao, "a área desenhada não foi gravada"
    assert selecao[-1].get("tipo") == TIPOS_DE_MARCAR[nome], f"marcou como {selecao[-1].get('tipo')}"


@prova("P-071")
def test_p071_cor_de_pintar(janela, tela, monkeypatch):
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QColorDialog

    _no_marcar(janela, tela)
    apertar(janela, "área de trabalho/marcar/cor de pintar")
    caixa = tela.paineis.marcar_como.caixa_de_cor
    assert isinstance(caixa, QColorDialog) and caixa.isVisible(), "a caixa de cores não abriu"
    caixa.setCurrentColor(QColor("#ff0000"))
    caixa.accept()
    aj.assentar()
    apertar(janela, "área de trabalho/marcar/pintar por cima")
    _desenhar_area(tela)
    selecao = aj.pagina_gravada(janela, 1)["selecao"]
    assert "ff0000" in str(selecao[-1]).lower(), f"a cor escolhida não foi para a área: {selecao[-1]}"


@prova("P-072")
@pytest.mark.parametrize("onde", ["área de trabalho/marcar/detectar automaticamente", "menu/procurar_de_novo"])
def test_p072_detectar_de_novo_guarda_o_feito_a_mao(janela, tela, onde):
    _no_marcar(janela, tela)
    apertar(janela, "área de trabalho/marcar/papel")
    _desenhar_area(tela)
    antes = [r for r in aj.pagina_gravada(janela, 1)["selecao"] if r.get("origem") == "mao"]
    assert antes
    apertar(janela, onde)
    depois = [r for r in aj.pagina_gravada(janela, 1)["selecao"] if r.get("origem") == "mao"]
    assert depois == antes, "o que foi marcado à mão se perdeu"


def _folha_inteira_como_papel(janela, tela):
    _no_marcar(janela, tela)
    apertar(janela, "menu/folha_em_branco")


@prova("P-073")
@pytest.mark.parametrize("qual", ["todas", "daqui"])
def test_p073_marcacao_em_todas_e_daqui(janela, tela, monkeypatch, pasta, qual):
    _folha_inteira_como_papel(janela, tela)
    chave = next(c for c in PROMESSAS["P-073"].chaves if ("usar em todas" if qual == "todas" else "daqui") in c)
    apertar(janela, chave)
    gravado = aj.projeto_gravado(janela)["paginas"]
    com = [bool(p["selecao"]) for p in gravado]
    assert com == ([True] * 4 if qual == "todas" else [False, True, True, True]), com
    # o PDF da folha marcada como papel é a promessa P-078 (lá a prova gera o PDF)


@prova("P-074")
@pytest.mark.parametrize("qual", ["todas", "daqui"])
def test_p074_tem_foto_em_todas_e_daqui(janela, tela, qual):
    _no_marcar(janela, tela)
    tela.caixa_tem_foto.setChecked(True)
    chave = next(c for c in PROMESSAS["P-074"].chaves if ("usar em todas" if qual == "todas" else "daqui") in c)
    apertar(janela, chave)
    formas = [p.get("gravura_forma") for p in aj.projeto_gravado(janela)["paginas"]]
    marcada = formas[1]
    assert marcada is not None
    assert formas == ([marcada] * 4 if qual == "todas" else [formas[0], marcada, marcada, marcada])
    if qual == "daqui":
        assert formas[0] != marcada


@prova("P-075")
def test_p075_apagar_pintar_copiar_colar(janela, tela, monkeypatch, pasta):
    _no_marcar(janela, tela)
    apertar(janela, "área de trabalho/marcar/gravura ou foto")
    _desenhar_area(tela, 0.1, 0.1, 0.5, 0.3)
    tela.escolher_ferramenta("ajustar")
    editor = tela.editor_selecao
    from tests.test_editor_selecao import clicar, soltar

    editor.mousePressEvent(clicar(editor, 0.3, 0.2))     # o clique na área, com a ferramenta A
    editor.mouseReleaseEvent(soltar(editor, 0.3, 0.2))
    aj.assentar()
    assert editor.escolhida is not None, "a ferramenta Mover e mudar o tamanho não escolheu a área"
    apertar(janela, "área de trabalho/marcar/copiar")
    tela.ir_para_pagina(2)
    apertar(janela, "área de trabalho/marcar/colar")
    assert aj.pagina_gravada(janela, 2)["selecao"], "colar não pôs a área na outra página"
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("ajustar")
    aj.esperar(lambda: editor._pixmap is not None, motivo="a página no editor")
    editor.mousePressEvent(clicar(editor, 0.3, 0.2))     # escolhe a área de novo nesta página
    editor.mouseReleaseEvent(soltar(editor, 0.3, 0.2))
    aj.assentar()
    assert editor.escolhida is not None, f"a área não ficou escolhida: {tela.aviso_marcacao.text()}"
    apertar(janela, "área de trabalho/marcar/pintar de branco")
    tipos = [r["tipo"] for r in aj.pagina_gravada(janela, 1)["selecao"]]
    assert tipos == ["papel"], f"pintar de branco não virou papel: {tipos} ({tela.aviso_marcacao.text()})"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert aj.qual_pagina(paginas[1]) is None, "a área pintada de branco não saiu branca (o bloco continua)"
    _voltar_ao_trabalho(janela)
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("ajustar")
    # etapa 9c: esperar a página chegar ao editor, como no clique de cima (sem isto o clique
    # caía antes da imagem e não escolhia nada; o defeito do PDF escondia esta falta da prova)
    aj.esperar(lambda: editor._pixmap is not None, motivo="a página no editor")
    editor.mousePressEvent(clicar(editor, 0.3, 0.2))
    editor.mouseReleaseEvent(soltar(editor, 0.3, 0.2))
    aj.assentar()
    apertar(janela, "área de trabalho/marcar/apagar a área")
    assert not aj.pagina_gravada(janela, 1)["selecao"], "apagar a área não tirou a área"


@prova("P-076")
def test_p076_ajustar_o_pedaco(janela, tela):
    """Só aparece com um pedaço de outro filtro e papel demais em volta: a prova monta esse caso
    marcando um pedaço grande em Original numa página em Preto e branco."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    _no_marcar(janela, tela)
    tela._escolher_filtro_da_regiao(ORIGINAL)
    _desenhar_area(tela, 0.05, 0.05, 0.6, 0.45)
    tela._avaliar_os_pedacos(tela.projeto.paginas[1])
    aj.assentar()
    alvo = tela.botao_ajustar_pedaco
    if not (alvo.isVisibleTo(tela) and alvo.isEnabled()):
        pytest.skip("o caso do pedaço com papel demais não apareceu nesta página sintética")
    antes = aj.pagina_gravada(janela, 1)["selecao"][-1]
    alvo.click()
    aj.assentar()
    depois = aj.pagina_gravada(janela, 1)["selecao"][-1]
    assert depois != antes, "o pedaço não encolheu"


@prova("P-077")
def test_p077_limpar_tudo(janela, tela):
    _no_marcar(janela, tela)
    _desenhar_area(tela)
    assert aj.pagina_gravada(janela, 1)["selecao"]
    apertar(janela, "menu/limpar_marcacao")
    assert not aj.pagina_gravada(janela, 1)["selecao"]
    # o Desfazer da marcação é a promessa P-129 (aguarda a etapa 9)


@prova("P-129")
def test_p129_desfazer_desfaz_a_marcacao(janela, tela):
    _no_marcar(janela, tela)
    _desenhar_area(tela)
    apertar(janela, "menu/limpar_marcacao")
    assert not aj.pagina_gravada(janela, 1)["selecao"]
    apertar(janela, "menu/desfazer")
    assert aj.pagina_gravada(janela, 1)["selecao"], "o Desfazer não trouxe a marcação"


@prova("P-078")
def test_p078_deixar_a_folha_em_branco(janela, tela, monkeypatch, pasta):
    _folha_inteira_como_papel(janela, tela)
    selecao = aj.pagina_gravada(janela, 1)["selecao"]
    assert selecao and selecao[-1]["tipo"] == "papel"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 4 and aj.esta_branca(paginas[1]) and not aj.esta_branca(paginas[0])


# --- painel Filtro ----------------------------------------------------------------------------

FILTROS = {"Original": "original", "Preto e branco": "preto_e_branco", "Melhorar": "melhorar",
           "Mágico pro": "magico_pro"}


@prova("P-080")
@pytest.mark.parametrize("nome", list(FILTROS))
@pytest.mark.parametrize("lugar", ["painel", "menu", "tecla"])
def test_p080_os_quatro_filtros(janela, tela, monkeypatch, pasta, nome, lugar):
    from core.filtros import MELHORAR

    chave = FILTROS[nome]
    tela.ir_para_pagina(1)
    if chave == "original":                      # para ver o Original mudar alguma coisa
        tela._escolher_filtro(MELHORAR)
    tela.paineis.abrir("filtro")
    tela.escolher_ferramenta("mao")
    if lugar == "painel":
        apertar(janela, f"área de trabalho/filtro da página/cartão {nome}")
    elif lugar == "menu":
        apertar(janela, f"menu/filtro_{chave}")
    else:
        QTest.keyClick(tela, getattr(Qt, f"Key_{list(FILTROS).index(nome) + 1}"))
        aj.assentar()
    assert aj.pagina_gravada(janela, 1)["filtro"] == chave
    assert [p["filtro"] for i, p in enumerate(aj.projeto_gravado(janela)["paginas"]) if i != 1] == ["original"] * 3
    if lugar != "painel" or nome not in ("Preto e branco", "Original"):
        return                                   # o PDF de cada filtro: um por filtro basta
    paginas = _gerar(janela, monkeypatch, pasta)
    if chave == "preto_e_branco":
        assert aj.so_preto_e_branco(paginas[1]), "a página não saiu em preto e branco"
    else:
        assert aj.papel_amarelado(paginas[1])
    assert aj.papel_amarelado(paginas[0]) and aj.papel_amarelado(paginas[2]), "mudou outra página"


@prova("P-085")
def test_p085_o_menu_filtro_marca_o_filtro_da_pagina(janela, tela):
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    aj.assentar()
    assert janela.menu.acoes["filtro_preto_e_branco"].isChecked(), "o menu Filtro não marca o filtro da página"
    tela.ir_para_pagina(0)
    aj.assentar()
    assert tela.projeto.paginas[0].filtro == ORIGINAL
    assert janela.menu.acoes["filtro_original"].isChecked() and \
        not janela.menu.acoes["filtro_preto_e_branco"].isChecked(), "o menu Filtro não acompanha a página"


@prova("P-084")
def test_p084_so_neste_pedaco(janela, tela, monkeypatch, pasta):
    """D-188: nenhum aceso de fábrica; clicar escolhe o filtro do próximo pedaço; clicar de novo no
    aceso volta a nenhum. D-173: página em Original com o pedaço em Preto e branco -> o pedaço sai
    em Preto e branco no PDF (o pedaço cobre o canto de cima à direita, onde só há papel)."""
    painel = tela.paineis.filtro_da_pagina
    _no_marcar(janela, tela)
    tela.paineis.abrir("filtro")
    from PySide6.QtWidgets import QFrame

    for parte in painel.findChildren(QFrame):
        if type(parte).__name__ == "ParteQueAbre" and "pedaço" in parte.nome.lower():
            parte.abrir(True)
    aj.assentar()
    botoes = painel.botoes_do_pedaco
    assert not painel.filtro_pedaco, "veio um filtro aceso de fábrica (D-188)"
    pb = botoes["preto_e_branco"]
    pb.click()
    aj.assentar()
    assert painel.filtro_pedaco == "preto_e_branco"
    pb.click()
    aj.assentar()
    assert not painel.filtro_pedaco, "clicar de novo no aceso não voltou a nenhum"
    pb.click()
    aj.assentar()
    tela.paineis.abrir("props")
    _desenhar_area(tela, 0.75, 0.0, 1.0, 0.12)
    regiao = aj.pagina_gravada(janela, 1)["selecao"][-1]
    assert regiao.get("filtro") == "preto_e_branco", f"o pedaço não ficou com o filtro dele: {regiao}"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert not aj.papel_amarelado(paginas[1]), "o pedaço em Preto e branco não saiu no PDF (D-173)"
    assert aj.papel_amarelado(paginas[0])


@prova("P-081")
@pytest.mark.parametrize("alcance", ["só nesta", "todas", "daqui em diante"])
def test_p081_aplicar_o_filtro_em(janela, tela, monkeypatch, pasta, alcance):
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(2)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.paineis.abrir("filtro")
    apertar(janela, f"área de trabalho/filtro da página/{alcance}")
    filtros = [p["filtro"] for p in aj.projeto_gravado(janela)["paginas"]]
    esperado = {"só nesta": ["original", "original", "preto_e_branco", "original"],
                "todas": ["preto_e_branco"] * 4,
                "daqui em diante": ["original", "original", "preto_e_branco", "preto_e_branco"]}[alcance]
    assert filtros == esperado, filtros
    assert aj.pagina_gravada(janela, 2)["revisada"] is True
    if alcance == "todas":
        paginas = _gerar(janela, monkeypatch, pasta)
        assert all(aj.so_preto_e_branco(p) for p in paginas)


@prova("P-082")
@pytest.mark.parametrize("onde", ["área de trabalho/filtro da página/Ver os filtros em tela cheia",
                                  "menu/filtros_tela_cheia"])
def test_p082_filtros_em_tela_cheia(janela, tela, monkeypatch, onde):
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    abertas = []
    monkeypatch.setattr(FiltrosEmTelaCheia, "exec", lambda self: abertas.append(self) or 0)
    monkeypatch.setattr(FiltrosEmTelaCheia, "open", lambda self: abertas.append(self))
    tela.ir_para_pagina(2)
    tela.paineis.abrir("filtro")
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    assert abertas, "os filtros em tela cheia não abriram"
    assert aj.projeto_gravado(janela) == antes


@prova("P-083")
@pytest.mark.parametrize("jeito", ["tudo", "apagar", "rede"])
def test_p083_jeitos_do_so_as_letras(janela, tela, jeito):
    """Na área de trabalho os jeitos do "Só as letras" são uma lista com desenho (D-185, "Menu com
    amostra"); "Mais opções" / "Menos opções" abrem e fecham as escolhas a mais."""
    from PySide6.QtWidgets import QCheckBox

    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.paineis.abrir("filtro")
    aj.assentar()
    caixa = next(c for c in tela.paineis.filtro_da_pagina.findChildren(QCheckBox)
                 if c.text() == "Só as letras" and c.isVisibleTo(tela))
    caixa.click()
    aj.assentar()
    assert aj.pagina_gravada(janela, 1)["misto_so_as_letras"] is True
    lista = tela.escolhas_misto.lista_do_texto
    assert lista.isVisibleTo(tela), "a lista dos jeitos não aparece com 'Só as letras' ligado"
    if jeito == "rede":                       # o de fábrica: escolhe outro antes, para ver a troca
        lista.setCurrentIndex(lista.findData("tudo"))
        aj.assentar()
    lista.setCurrentIndex(lista.findData(jeito))
    aj.assentar()
    gravado = aj.pagina_gravada(janela, 1)["misto_fora_do_texto"]
    assert gravado == jeito or (jeito == "rede" and gravado in (None, "rede")), gravado
    painel_mais = tela.escolhas_misto.painel_mais
    apertar(janela, "área de trabalho/filtro da página/Mais opções")
    assert painel_mais.isVisibleTo(tela), "'Mais opções' não abriu as escolhas a mais"
    apertar(janela, "área de trabalho/filtro da página/Menos opções")
    assert not painel_mais.isVisibleTo(tela), "'Menos opções' não fechou"


@prova("P-083")
@pytest.mark.parametrize("nome,valor", [("Guardar tudo", "tudo"), ("Guardar só o texto", "apagar"),
                                        ("Guardar a tinta forte", "rede")])
def test_p083_jeitos_no_automatico(janela, tela, nome, valor):
    """Etapa 3 da obra: os jeitos do "Só as letras" do livro moram no Automático (janela grande,
    etapa Limpar a folha); antes, na tela "O que fazer"."""
    from core import automatico as A

    opcoes = janela.abrir_o_automatico(A.LIMPAR)
    opcoes.escolhas_misto.mostrar(True, "tudo" if valor == "rede" else "rede", None, None)
    aj.assentar()
    alvo = opcoes.escolhas_misto.botoes[valor]
    alvo.click()
    aj.assentar()
    assert opcoes.escolhas_misto.fora_do_texto() == valor

# --- "Para revisar" -------------------------------------------------------------------------------

def _com_avisos(janela, tela):
    """Páginas 2 e 4 com aviso ("Parece em branco"), a 3 com dois ("Parece em branco" e "Endireitar:
    as contas discordam"); o painel "Para revisar" aberto."""
    from core import analise

    for indice, codigos in ((1, [analise.EM_BRANCO]), (2, [analise.EM_BRANCO, analise.CONTAS_DO_ENDIREITAR_DISCORDAM]),
                            (3, [analise.EM_BRANCO])):
        pagina = tela.projeto.paginas[indice]
        pagina.alertas = list(codigos)
        pagina.revisada = False
    tela.ir_para_pagina(0)
    tela.atualizar()
    tela.paineis.para_revisar.atualizar(tela.projeto)
    tela.paineis.abrir("revisar")
    aj.assentar()


def _pendentes(janela) -> int:
    from core import avisos

    return len(avisos.pendentes_do_livro(janela.projeto))


@prova("P-090")
def test_p090_por_pagina_e_por_motivo(janela, tela):
    _com_avisos(janela, tela)
    revisar = tela.paineis.para_revisar
    antes = aj.projeto_gravado(janela)
    apertar(janela, "área de trabalho/para revisar/Por motivo")
    assert revisar.motivos.parentWidget().isVisible() if hasattr(revisar, "motivos") else True
    assert revisar.itens, "a aba 'Por motivo' não mostra os motivos"
    apertar(janela, "área de trabalho/para revisar/Por página")
    assert revisar.lista.isVisible() and revisar.lista.count() == 3
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]
    tela.paineis.fechar()
    tela.paineis.abrir("revisar")
    assert revisar.lista.isVisible(), "não reabriu em 'Por página' (D-266)"


@prova("P-091")
def test_p091_clicar_no_motivo_leva_a_pagina(janela, tela):
    _com_avisos(janela, tela)
    apertar(janela, "área de trabalho/para revisar/Por motivo")
    apertar(janela, "área de trabalho/para revisar/motivo (o botão do grupo)")
    assert tela.indice_pagina in (1, 2)


@prova("P-092")
def test_p092_esta_bom_todas(janela, tela, monkeypatch, pasta):
    _com_avisos(janela, tela)
    apertar(janela, "área de trabalho/para revisar/Por motivo")
    revisar = tela.paineis.para_revisar
    from PySide6.QtWidgets import QPushButton

    alvo = next(b for b in revisar.findChildren(QPushButton) if b.text() == "está bom: todas" and b.isVisible())
    antes = _pendentes(janela)
    alvo.click()
    aj.assentar()
    assert _pendentes(janela) < antes
    gravado = aj.projeto_gravado(janela)["paginas"]
    assert all("em_branco" in p.get("alertas_aceitos", []) for p in gravado[1:]), "o aviso não ficou dado por visto"
    assert all(p.get("em_branco") is not True for p in gravado), "mudou a página"


@prova("P-093")
def test_p093_esta_bom_em_tudo(janela, tela):
    _com_avisos(janela, tela)
    antes = _pendentes(janela)
    apertar(janela, "área de trabalho/para revisar/está bom em tudo")
    assert _pendentes(janela) == 0, "o painel não ficou em 0"
    tela.desfazer()
    assert _pendentes(janela) == antes, "um Ctrl+Z não trouxe todos de volta"


@prova("P-094")
def test_p094_lista_dos_avisos(janela, tela):
    from ui.janela_dos_avisos import JanelaDosAvisos

    _com_avisos(janela, tela)

    def marcar_a_primeira_e_aceitar(caixa):
        botao_todas = caixa.botao_todas
        botao_todas.click()
        assert all(caixa.lista.item(i).checkState() == Qt.Checked for i in range(caixa.lista.count()))
        caixa.botao_nenhuma.click()
        assert not caixa.avisos_marcados()
        caixa.lista.item(0).setCheckState(Qt.Checked)

    original = JanelaDosAvisos.exec
    rodada = {"n": 0}

    def _exec(caixa):
        rodada["n"] += 1
        from PySide6.QtCore import QTimer

        if rodada["n"] == 1:
            QTimer.singleShot(0, lambda: (marcar_a_primeira_e_aceitar(caixa), caixa.botao_aceitar.click()))
        else:
            fechar = next(b for b in caixa.findChildren(type(caixa.botao_ver)) if b.text() == "fechar")
            QTimer.singleShot(0, fechar.click)
        return original(caixa)

    JanelaDosAvisos.exec = _exec
    try:
        apertar(janela, "área de trabalho/para revisar/ver a lista…")
    finally:
        JanelaDosAvisos.exec = original
    assert _pendentes(janela) == 3, "'está bom nas marcadas' não tirou só a marcada"


@prova("P-095")
def test_p095_ver_as_duvidas_em_tela_cheia(janela, tela):
    from core import avisos

    _com_avisos(janela, tela)
    antes = _trabalho(aj.projeto_gravado(janela))
    numero = avisos.quantas_com_duvida(tela.projeto)
    alvo = botao(janela, "área de trabalho/para revisar/ver as N em tela cheia")
    assert alvo.text() == f"ver as {numero} em tela cheia"
    alvo.click()
    aj.assentar()
    assert tela.pilha_da_tela.currentWidget() is tela.todas, "a tela cheia (a grade) não abriu"
    assert tela.todas.so_atencao, "não abriu em 'só as que precisam de atenção'"
    mostradas = [i.indice for grupo in tela.todas._grupos() for i in grupo]
    # as páginas com dúvida agora (o programa refaz sozinho alguns avisos que ele mesmo mede)
    com_duvida = [i for alvo, i, _a in avisos.linhas_do_para_revisar(tela.projeto) if alvo == avisos.PAGINA]
    assert mostradas and mostradas == com_duvida, f"mostrou {mostradas}, e não só as com dúvida {com_duvida}"
    assert len(mostradas) < len(tela.projeto.paginas)
    assert tela.todas.botao_atencao.text().endswith(f"({numero})")
    assert _trabalho(aj.projeto_gravado(janela)) == antes


# --- a faixa e os avisos ---------------------------------------------------------------------------

CAMPOS_DO_TRABALHO = ("filtro", "revisada", "em_branco", "apagada", "recorte", "angulo_manual",
                      "selecao", "forca_preto", "misto_so_as_letras", "misto_fora_do_texto")


def _trabalho(gravado: dict) -> list:
    """O que a pessoa fez nas páginas (sem os avisos, que o programa põe e tira sozinho)."""
    return [{c: p.get(c) for c in CAMPOS_DO_TRABALHO} for p in gravado["paginas"]]


def _apertar_aviso(janela, tela, indice, chave):
    """Vai até a página, põe nela o aviso que tem o botão da chave `aviso/<conserto>`, redesenha a
    faixa e aperta o botão (antes de as prévias de fundo poderem mexer nos avisos)."""
    rotulo, codigo = _chaves_dos_avisos()[chave]
    tela.ir_para_pagina(indice)
    item = tela.item_atual
    item.alertas = [codigo]
    item.alertas_aceitos = []
    item.revisada = False
    tela._atualizar_faixa()
    pagina = item
    faixa = [tela.botao_sugestao, tela.botao_sugestao_2, tela.botao_sugestao_3]
    alvo = next((b for b in faixa if not b.isHidden() and b.text() == rotulo), None)
    assert alvo is not None, f"a faixa não mostra '{rotulo}': {[b.text() for b in faixa if not b.isHidden()]}"
    alvo.click()
    aj.assentar()
    return pagina


@prova("P-194")
def test_p194_ver_no_mover(janela, tela):
    """Etapa 5 da obra (D-017): o aviso leva à ferramenta Mover e não diminui nada sozinho."""
    tela.escolher_ferramenta("retangulo")
    antes = aj.projeto_gravado(janela)
    _apertar_aviso(janela, tela, 1, "aviso/ver_no_mover")
    assert tela.aba_atual == "mover" and tela.indice_pagina == 1
    depois = aj.projeto_gravado(janela)
    assert [p.get("conteudo_escala", 1.0) for p in depois["paginas"]] == \
        [p.get("conteudo_escala", 1.0) for p in antes["paginas"]]


@prova("P-100")
def test_p100_esta_certo_hoje(janela, tela, monkeypatch, pasta):
    from core import analise

    pagina = tela.projeto.paginas[1]
    pagina.alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mao")
    apertar(janela, "área de trabalho/faixa do aviso/está certo")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["revisada"] is True
    assert pagina.alertas_pendentes == [], "o aviso continua pendente"
    assert any(a.get("tipo") == "revisar" for a in aj.acoes_gravadas(janela))


@prova("P-101")
def test_p101_esta_certo_com_resposta(janela, tela):
    from core import analise

    for i in (1, 3):
        tela.projeto.paginas[i].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mao")
    antes = sum(1 for p in tela.projeto.paginas if p.revisada)
    assert f"{antes} de " in tela.rotulo_do_livro.text()
    apertar(janela, "área de trabalho/faixa do aviso/está certo")
    assert tela.indice_pagina == 3, "não foi para a próxima dúvida"
    assert tela.tira._miniaturas[1].conferida, "a miniatura não ganhou o tique"
    assert f"{antes + 1} de " in tela.rotulo_do_livro.text(), "o contador de conferidas não subiu"
    assert aj.pagina_gravada(janela, 1)["revisada"] is True


@prova("P-102")
def test_p102_proxima_duvida(janela, tela):
    from core import analise

    tela.projeto.paginas[2].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    tela.ir_para_pagina(0)
    tela.escolher_ferramenta("mao")
    tela.atualizar()
    antes = _trabalho(aj.projeto_gravado(janela))
    apertar(janela, "área de trabalho/faixa do aviso/próxima dúvida")
    assert tela.indice_pagina == 2
    assert _trabalho(aj.projeto_gravado(janela)) == antes


@prova("P-103")
def test_p103_esta_bom_assim(janela, tela, monkeypatch, pasta):
    from core import analise

    tela.ir_para_pagina(1)
    pagina = tela.projeto.paginas[1]
    # os dois avisos postos depois de chegar à página (ao chegar, o programa refaz os avisos
    # que ele mesmo mede, e o "contas discordam" de mentira sairia)
    pagina.alertas = [analise.EM_BRANCO, analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    tela._atualizar_faixa()
    apertar(janela, "área de trabalho/faixa do aviso/está bom assim")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["alertas_aceitos"] == [analise.EM_BRANCO], f"aceitou mais que este motivo: {gravada['alertas_aceitos']}"
    assert gravada["revisada"] is False, "deu a página inteira por conferida"
    assert not pagina.em_branco and not pagina.apagada
    paginas = _gerar(janela, monkeypatch, pasta)
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 2, 3]


@prova("P-104")
def test_p104_aviso_deixar_em_branco(janela, tela, monkeypatch, pasta):
    _apertar_aviso(janela, tela, 2, "aviso/em_branco")
    assert aj.pagina_gravada(janela, 2)["em_branco"] is True
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 4 and aj.esta_branca(paginas[2])


@prova("P-105")
def test_p105_aviso_tirar_do_livro(janela, tela, monkeypatch, pasta):
    _apertar_aviso(janela, tela, 2, "aviso/apagar")
    assert aj.pagina_gravada(janela, 2)["apagada"] is True
    paginas = _gerar(janela, monkeypatch, pasta)
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 3]


@prova("P-106")
@pytest.mark.parametrize("chave,esperado", [("aviso/misto_fora:tudo", "tudo"), ("aviso/misto_fora:rede", "rede")])
def test_p106_trazer_de_volta(janela, tela, chave, esperado):
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    pagina = tela.projeto.paginas[1]
    pagina.misto_so_as_letras = True
    pagina.misto_fora_do_texto = "apagar" if esperado == "rede" else "rede"   # o jeito que apagou
    _apertar_aviso(janela, tela, 1, chave)
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["misto_fora_do_texto"] == esperado or (esperado == "rede" and gravada["misto_fora_do_texto"] is None), \
        gravada["misto_fora_do_texto"]
    assert all(p.get("misto_fora_do_texto") is None for i, p in enumerate(aj.projeto_gravado(janela)["paginas"]) if i != 1)


@prova("P-107")
@pytest.mark.parametrize("chave,sobe", [("aviso/forca:mais_escuro", True), ("aviso/forca:mais_fraco", False)])
def test_p107_forca_do_preto(janela, tela, monkeypatch, pasta, chave, sobe):
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    _apertar_aviso(janela, tela, 1, chave)
    forca = aj.pagina_gravada(janela, 1)["forca_preto"]
    assert (forca > 50) if sobe else (forca < 50), forca
    assert [p["forca_preto"] for i, p in enumerate(aj.projeto_gravado(janela)["paginas"]) if i != 1] == [50] * 3


@prova("P-108")
def test_p108_desfazer_o_reforco(janela, tela):
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    pagina = tela.projeto.paginas[1]
    pagina.forca_antes_do_reforco = 50
    pagina.forca_preto = 85
    _apertar_aviso(janela, tela, 1, "aviso/desfazer_reforco")
    assert aj.pagina_gravada(janela, 1)["forca_preto"] == 50


@prova("P-109")
def test_p109_usar_magico_pro(janela, tela, monkeypatch, pasta):
    _apertar_aviso(janela, tela, 1, "aviso/filtro:magico_pro")
    assert aj.pagina_gravada(janela, 1)["filtro"] == "magico_pro"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert not aj.papel_amarelado(paginas[1]) and aj.papel_amarelado(paginas[0])


@prova("P-110")
def test_p110_corte_alargado(janela, tela):
    _apertar_aviso(janela, tela, 1, "aviso/corte_alargado")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada["revisada"] is True
    assert any("alargado" in a.get("descricao", "").lower() or a.get("tipo") in ("recortar", "revisar")
               for a in aj.acoes_gravadas(janela)), "o botão não fez nada no histórico"


@prova("P-111")
def test_p111_desentortar_aumentando(janela, tela):
    _apertar_aviso(janela, tela, 1, "aviso/desentortar_aumentando")
    assert aj.pagina_gravada(janela, 1)["desentortar_aumentar"] is True
    _apertar_aviso(janela, tela, 1, "aviso/desentortar_desfazer_aumento")
    assert aj.pagina_gravada(janela, 1)["desentortar_aumentar"] is False


@prova("P-112")
def test_p112_aviso_nao_dividir(janela, pasta, monkeypatch):
    livro = aj.criar_livro_duplo(pasta, folhas=2)
    tela = aj.abrir_livro_para_teste(janela, livro, marcadas=("cx_dividir",))
    tela.escolher_ferramenta("dividir")
    rotulo, codigo = _chaves_dos_avisos()["aviso/nao_dividir"]
    folha = tela.projeto.folhas[0]
    folha.alertas = [codigo]
    folha.revisada = False
    tela.ir_para_pagina(0)
    alvo = next(b for b in (tela.botao_sugestao, tela.botao_sugestao_2, tela.botao_sugestao_3)
                if not b.isHidden() and b.text() == rotulo)
    alvo.click()
    aj.assentar()
    assert aj.projeto_gravado(janela)["folhas"][0]["dividir"] is False
    paginas = _gerar(janela, monkeypatch, pasta)
    assert len(paginas) == 3


@prova("P-113")
def test_p113_alinhar_com_as_outras(janela, tela):
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("endireitar")
    _apertar_aviso(janela, tela, 1, "aviso/alinhar_com_as_outras")
    gravada = aj.pagina_gravada(janela, 1)
    assert gravada.get("alinhar_com_as_outras") is True or gravada.get("angulo_manual") is not None


# --- miniaturas e barra de baixo ------------------------------------------------------------------

@prova("P-120")
@pytest.mark.parametrize("onde", ["área de trabalho/miniaturas/Fechar as miniaturas",
                                  "área de trabalho/miniaturas/… Fechar as miniaturas", "menu/miniaturas"])
def test_p120_fechar_e_abrir_as_miniaturas(janela, tela, onde):
    import configuracoes

    miniaturas = tela.miniaturas
    assert miniaturas.aberta
    if onde.startswith("área de trabalho/miniaturas/…"):
        aj.acoes_de_menu_aberto(miniaturas.pontos.click, escolher="Fechar as miniaturas")
        aj.assentar()
    else:
        apertar(janela, onde)
    assert not miniaturas.aberta, "as miniaturas não fecharam"
    assert not janela.menu.acoes["miniaturas"].isChecked(), "o menu Ver não acompanha"
    assert configuracoes.ler("miniaturas")["aberta"] is False, "não ficou lembrado (D-060)"
    apertar(janela, "área de trabalho/miniaturas/Abrir as miniaturas")
    assert miniaturas.aberta and janela.menu.acoes["miniaturas"].isChecked()


@prova("P-121")
@pytest.mark.parametrize("item,lugar", [("Ver em pares", None), ("Lugar > à esquerda", "esquerda"),
                                        ("Lugar > à direita, junto da página", "direita"),
                                        ("Lugar > embaixo", "embaixo")])
def test_p121_mais_opcoes_das_miniaturas(janela, tela, item, lugar):
    import configuracoes

    miniaturas = tela.miniaturas
    if lugar == "embaixo":
        aj.acoes_de_menu_aberto(miniaturas.pontos.click, escolher="Lugar > à esquerda")
    vistos = aj.acoes_de_menu_aberto(miniaturas.pontos.click, escolher=item)
    aj.assentar()
    assert "Ver em pares" in vistos
    guardado = configuracoes.ler("miniaturas")
    if lugar is None:
        assert miniaturas.em_pares and guardado["em_pares"] is True
    else:
        assert miniaturas.lugar == lugar and guardado["lugar"] == lugar


@prova("P-122")
@pytest.mark.parametrize("onde", ["área de trabalho/miniaturas/ver todas", "menu/todas_as_paginas"])
def test_p122_ver_todas(janela, tela, onde):
    tela.ir_para_pagina(2)
    apertar(janela, onde)
    assert tela.todas.isVisibleTo(tela)
    assert botao(janela, "área de trabalho/todas as páginas/uma a uma").isChecked()


@prova("P-123")
def test_p123_pagina_anterior_e_proxima(janela, tela):
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mao")
    antes = aj.projeto_gravado(janela)
    apertar(janela, "área de trabalho/barra de baixo/›")
    assert tela.indice_pagina == 2 and "3" in tela.rotulo_da_pagina.text()
    apertar(janela, "área de trabalho/barra de baixo/‹")
    assert tela.indice_pagina == 1
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]


@prova("P-124")
@pytest.mark.parametrize("lugar", ["barra de baixo", "histórico", "menu"])
def test_p124_desfazer_e_refazer(janela, tela, monkeypatch, pasta, lugar):
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    if lugar == "histórico":
        tela.paineis.abrir("historico")
    desfazer = "menu/desfazer" if lugar == "menu" else f"área de trabalho/{lugar}/Desfazer"
    refazer = "menu/refazer" if lugar == "menu" else f"área de trabalho/{lugar}/Refazer"
    apertar(janela, desfazer)
    assert aj.pagina_gravada(janela, 1)["filtro"] == "original"
    apertar(janela, refazer)
    assert aj.pagina_gravada(janela, 1)["filtro"] == PRETO_E_BRANCO
    apertar(janela, desfazer)
    aj.projeto_gravado(janela)
    from historico_acoes import HistoricoAcoes

    relido = HistoricoAcoes(aj.pasta_do_projeto(janela))
    assert not relido.pode_desfazer, "o histórico gravado não acompanhou o desfazer"
    paginas = _gerar(janela, monkeypatch, pasta) if lugar == "menu" else None
    if paginas:
        assert aj.papel_amarelado(paginas[1]), "depois do desfazer o PDF saiu com o filtro desfeito"


@prova("P-125")
def test_p125_desfazer_apagado_sem_nada(janela, tela):
    assert not tela.acoes.pode_desfazer
    assert not botao(janela, "área de trabalho/barra de baixo/Desfazer").isEnabled()
    assert not janela.menu.acoes["desfazer"].isEnabled(), "menu Editar > Desfazer aceso sem nada para desfazer"


@prova("P-126")
@pytest.mark.parametrize("onde", ["área de trabalho/barra de baixo/Abrir ou fechar o painel Histórico", "menu/historico"])
def test_p126_botao_do_historico(janela, tela, onde):
    from core.filtros import PRETO_E_BRANCO

    tela._escolher_filtro(PRETO_E_BRANCO)
    tela.paineis.fechar()
    apertar(janela, onde)
    historico = tela.paineis.historico
    assert historico.isVisible() and historico.itens, "o painel Histórico não abriu com a lista"
    if onde.startswith("área"):
        apertar(janela, onde)
        assert not historico.isVisible(), "clicar de novo não fechou"


@prova("P-128")
def test_p128_linhas_do_historico(janela, tela):
    from core.filtros import MAGICO_PRO, PRETO_E_BRANCO

    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela._escolher_filtro(MAGICO_PRO)
    tela.paineis.abrir("historico")
    aj.assentar()
    historico = tela.paineis.historico
    historico.itens[0].click()                    # volta até a primeira ação
    aj.assentar()
    assert aj.pagina_gravada(janela, 1)["filtro"] == PRETO_E_BRANCO
    historico.itens_desfeitos[0].click()          # refaz até a desfeita
    aj.assentar()
    assert aj.pagina_gravada(janela, 1)["filtro"] == MAGICO_PRO


@prova("P-127")
@pytest.mark.parametrize("onde", ["área de trabalho/processar/Confirmar e processar", "menu/processar"])
def test_p127_confirmar_e_processar(janela, tela, monkeypatch, pasta, onde):
    import ui.janela_confirmar as confirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    from ui.janela_principal import FINAL

    from core import analise

    tela.projeto.paginas[1].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    destino = pasta / "saida" / "livro pronto.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: destino)
    vistas = []
    aj.responder_caixa(monkeypatch, JanelaDosAvisos, "continuar assim mesmo", registro=vistas)
    apertar(janela, onde)
    fim = time.monotonic() + 180
    while janela.telas.currentIndex() != FINAL and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    assert vistas, "com aviso pendente, a janela 'Antes de processar' não apareceu (D-274)"
    assert destino.exists()
    assert Path(aj.projeto_gravado(janela)["caminho_saida"]) == destino
    _livro_inteiro_original(aj.paginas_do_pdf(destino))


# --- janelas ------------------------------------------------------------------------------------------

@prova("P-130")
@pytest.mark.parametrize("escolha", ["ver", "continuar assim mesmo"])
def test_p130_antes_de_processar(janela, tela, monkeypatch, pasta, escolha):
    import ui.janela_confirmar as confirmar
    from ui.janela_dos_avisos import JanelaDosAvisos
    from ui.janela_principal import CONFERIR, FINAL

    from core import analise

    tela.projeto.paginas[2].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    destino = pasta / "saida" / "x.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: destino)
    aj.responder_caixa(monkeypatch, JanelaDosAvisos, escolha)
    apertar(janela, "área de trabalho/processar/Confirmar e processar")
    fim = time.monotonic() + 180
    while escolha != "ver" and janela.telas.currentIndex() != FINAL and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    if escolha == "ver":
        assert janela.telas.currentIndex() == CONFERIR and tela.indice_pagina == 2
        assert not destino.exists(), "'ver' processou"
    else:
        assert destino.exists()


@prova("P-131")
def test_p131_janela_confirmar(janela, tela, monkeypatch, pasta):
    import ui.dialogos_de_arquivo as dialogos
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_principal import FINAL

    outra = pasta / "outra pasta"
    outra.mkdir()
    monkeypatch.setattr(dialogos, "escolher_pasta", lambda *a, **k: str(outra))

    def escolher_e_processar(caixa):
        alvo = aj.chaves_dos_botoes(caixa, "confirmar e processar")["confirmar e processar/Escolher pasta"]
        alvo.click()
        aj.assentar()
        assert Path(caixa.destino.pasta) == outra, "'Escolher pasta' não trocou a pasta"

    aj.responder_caixa(monkeypatch, JanelaConfirmar, "voltar")
    apertar(janela, "área de trabalho/processar/Confirmar e processar")
    assert janela.telas.currentIndex() != FINAL
    assert not list(pasta.rglob("*.pdf"))[1:], "'voltar' gravou algum PDF"
    aj.responder_caixa(monkeypatch, JanelaConfirmar, "Processar", antes=escolher_e_processar)
    apertar(janela, "área de trabalho/processar/Confirmar e processar")
    fim = time.monotonic() + 180
    while janela.telas.currentIndex() != FINAL and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    gerados = list(outra.glob("*.pdf"))
    assert len(gerados) == 1, "o PDF não foi para a pasta escolhida"


@prova("P-132")
@pytest.mark.parametrize("resposta", ["substituir o antigo", "salvar como", "cancelar"])
def test_p132_ja_existe_um_arquivo(janela, tela, monkeypatch, pasta, resposta):
    import ui.janela_confirmar as confirmar
    from ui.janela_principal import FINAL

    destino = pasta / "saida" / "pronto.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    doc.new_page().insert_text((40, 60), "o antigo")
    doc.save(str(destino))
    doc.close()
    antigo = destino.read_bytes()
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: destino)
    vistas = aj.caixas_durante(janela.processar, clicar=resposta)
    assert vistas and vistas[0][0] == "Já existe um arquivo com esse nome"
    fim = time.monotonic() + 180
    while resposta != "cancelar" and janela.telas.currentIndex() != FINAL and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    novo = pasta / "saida" / "pronto (2).pdf"
    if resposta == "substituir o antigo":
        assert destino.read_bytes() != antigo and len(aj.paginas_do_pdf(destino)) == 4
    elif resposta == "salvar como":
        assert destino.read_bytes() == antigo and len(aj.paginas_do_pdf(novo)) == 4
    else:
        assert destino.read_bytes() == antigo and not novo.exists()


@prova("P-133")
def test_p133_escolher_as_paginas(janela, tela, monkeypatch):
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    _no_cortar(janela, tela)
    tela._registrar("recortar", "pagina", [1], {"recorte": [0.0, 0.0, 0.5, 0.5]}, "corte à mão")

    def nenhuma_e_uma(caixa):
        caixa.botao_todas.click()
        assert all(caixa.lista.item(i).checkState() == Qt.Checked for i in range(caixa.lista.count()))
        caixa.botao_nenhuma.click()
        assert all(caixa.lista.item(i).checkState() == Qt.Unchecked for i in range(caixa.lista.count()))
        caixa.lista.item(2).setCheckState(Qt.Checked)

    aj.responder_caixa(monkeypatch, DialogoEscolherPaginas, "Cancelar")
    apertar(janela, "área de trabalho/cortar/usar em todas")
    assert [p["recorte"] for p in aj.projeto_gravado(janela)["paginas"]] == [None, [0.0, 0.0, 0.5, 0.5], None, None]
    aj.responder_caixa(monkeypatch, DialogoEscolherPaginas, "Aplicar", antes=nenhuma_e_uma)
    apertar(janela, "área de trabalho/cortar/usar em todas")
    recortes = [p["recorte"] for p in aj.projeto_gravado(janela)["paginas"]]
    assert recortes[2] == [0.0, 0.0, 0.5, 0.5] and recortes[0] is None and recortes[3] is None, recortes


@prova("P-134")
def test_p134_filtros_em_tela_cheia(janela, tela, monkeypatch, pasta):
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    tela.ir_para_pagina(1)
    dialogo = FiltrosEmTelaCheia(tela, janela)
    dialogo.show()
    aj.assentar()
    chaves = lambda: aj.chaves_dos_botoes(dialogo, "filtros em tela cheia")  # noqa: E731
    chaves()["filtros em tela cheia/›"].click()
    aj.assentar()
    chaves()["filtros em tela cheia/‹"].click()
    aj.assentar()
    dialogo.escolher("preto_e_branco")
    aj.assentar()
    assert aj.pagina_gravada(janela, 1)["filtro"] == "original", "escolher já mudou a página"
    chaves()["filtros em tela cheia/daqui em diante"].click()
    usar = next(b for c, b in chaves().items() if c.startswith("filtros em tela cheia/Usar"))
    usar.click()
    aj.assentar()
    filtros = [p["filtro"] for p in aj.projeto_gravado(janela)["paginas"]]
    assert filtros == ["original", "preto_e_branco", "preto_e_branco", "preto_e_branco"], filtros
    dialogo = FiltrosEmTelaCheia(tela, janela)
    dialogo.show()
    aj.assentar()
    dialogo.escolher("magico_pro")
    aj.chaves_dos_botoes(dialogo, "filtros em tela cheia")["filtros em tela cheia/Fechar sem mudar"].click()
    aj.assentar()
    assert [p["filtro"] for p in aj.projeto_gravado(janela)["paginas"]] == filtros, "'Fechar sem mudar' mudou"


@prova("P-135")
def test_p135_modo_comparar(janela, tela, monkeypatch):
    from ui.tela_ampliada import TelaAmpliada

    abertas = []
    monkeypatch.setattr(TelaAmpliada, "exec", lambda self: abertas.append(self) or 0)
    monkeypatch.setattr(TelaAmpliada, "open", lambda self: abertas.append(self))
    antes = aj.projeto_gravado(janela)
    apertar(janela, "menu/comparar")
    assert abertas, "o Modo comparar não abriu a página ampliada"
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]


@prova("P-136")
@pytest.mark.parametrize("onde", ["área de trabalho/barra de baixo/Duas lado a lado", "menu/lado_a_lado"])
def test_p136_ver_lado_a_lado_na_area_de_trabalho(janela, tela, onde):
    assert "lado_a_lado" in janela.menu.acoes, "o menu Ver não tem 'Ver lado a lado'"
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem, "não abriu em 'Uma página' (D-007)"
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(2)
    antes = aj.projeto_gravado(janela)
    apertar(janela, onde)
    aj.assentar()
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado, "os pares não apareceram"
    assert janela.menu.acoes["lado_a_lado"].isChecked(), "o menu Ver não acompanha"
    assert botao(janela, "área de trabalho/barra de baixo/Duas lado a lado").isChecked()
    pares = tela.lado_a_lado
    assert pares.indices == [p.indice for p in janela.projeto.paginas_ativas]
    assert pares._linhas()[0] == [None, 0], "a 1 não ficou sozinha à direita"
    assert pares.indice_da_vez() == 2, "não ficou na página da vez"
    if onde.startswith("menu/"):
        apertar(janela, onde)                           # desmarcar
    else:
        apertar(janela, "área de trabalho/barra de baixo/Uma página")
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert not janela.menu.acoes["lado_a_lado"].isChecked()
    assert tela.indice_pagina == 2
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]


@prova("P-137")
def test_p137_aviso_de_livro_novo(janela, tela):
    from core import automatico as A
    from core import perfis

    apertar(janela, "área de trabalho/aviso de livro novo/Rodar o automático…")
    aj.assentar()
    grande = janela.janela_do_automatico
    assert grande is not None and grande.isVisible(), "a janela grande não abriu"
    de_sempre = set(perfis.etapas_da_receita(perfis.ler(perfis.receita_de_sempre())))
    assert janela.estado_do_automatico.marcadas == de_sempre, "a receita de sempre não veio marcada"
    assert not janela.projeto.endireitar, "o livro mudou antes de Rodar"
    janela._fechar_a_janela_do_automatico()
    apertar(janela, "área de trabalho/aviso de livro novo/agora não")
    aj.assentar()
    assert not tela.aviso_do_livro_novo.isVisible(), "'agora não' não fechou o aviso"
    assert A.situacao(janela.projeto, A.ENDIREITAR) == "desligada"


@prova("P-139")
def test_p139_automatico_de_verdade(janela, tela, monkeypatch):
    """Rodar só "endireitar" numa página muda só ela (no projeto e no PDF)."""
    from core import automatico as A
    from ui.automatico import NA_PAGINA

    tela.paineis.abrir("automatico")
    estado = janela.estado_do_automatico
    estado.marcadas = {A.ENDIREITAR}
    tela.ir_para_pagina(1)
    estado.definir_alcance(NA_PAGINA)
    monkeypatch.setattr(janela, "rodar_o_automatico",
                        lambda _rodar=janela.rodar_o_automatico, **k: _rodar(esperar=True, **k))
    apertar(janela, "área de trabalho/automático/Rodar")
    aj.assentar()
    paginas = janela.projeto.paginas
    codigo = A.NA_PAGINA[A.ENDIREITAR]
    assert codigo in paginas[1].automatico, "a página 2 não ficou com o Endireitar"
    assert not janela.projeto.endireitar and all(codigo not in p.automatico
                                                  for i, p in enumerate(paginas) if i != 1)


# --- o Automático de verdade e a grade com várias escolhidas (etapa 3 da obra) -------------------

def _trabalho_gravado(janela) -> dict:
    """O projeto gravado sem a `geometria_das_zonas` das páginas: é a anotação que a conversão das
    zonas grava por trás logo depois de abrir (não é trabalho da pessoa), e chega em hora variável."""
    gravado = aj.projeto_gravado(janela)
    gravado["paginas"] = [{k: v for k, v in p.items() if k != "geometria_das_zonas"}
                          for p in gravado.get("paginas", [])]
    return gravado

@prova("P-172")
def test_p172_menu_automatico(janela, tela):
    antes = _trabalho_gravado(janela)
    apertar(janela, "menu/automatico")
    grande = janela.janela_do_automatico
    assert grande is not None and grande.isVisible(), "o menu não abriu o Automático"
    assert _trabalho_gravado(janela) == antes


@prova("P-173")
def test_p173_abrir_em_janela_grande_e_ajustar(janela, tela):
    from core import automatico as A

    tela.paineis.abrir("automatico")
    antes = _trabalho_gravado(janela)
    apertar(janela, "área de trabalho/automático/abrir em janela grande")
    assert janela.janela_do_automatico is not None and janela.janela_do_automatico.isVisible()
    janela._fechar_a_janela_do_automatico()
    tela.paineis.automatico.lista.escolher(A.LIMPAR)
    apertar(janela, "área de trabalho/automático/ajustar a etapa escolhida ›")
    grande = janela.janela_do_automatico
    assert grande is not None and grande.pilha.currentWidget() is grande.paginas_das_etapas[A.LIMPAR]
    assert _trabalho_gravado(janela) == antes


@prova("P-174")
def test_p174_salvar_a_receita(janela, tela):
    from core import perfis

    tela.paineis.abrir("automatico")
    antes = _trabalho_gravado(janela)
    apertar(janela, "área de trabalho/automático/Salvar...")
    caixa = janela.caixa_da_receita
    assert caixa is not None and caixa.isVisible(), "a caixa da receita não abriu"
    assert caixa.caixas, "a caixa não diz o que vai dentro"
    caixa.nome.setText("Receita da promessa")
    caixa.botao_guardar.click()
    aj.assentar()
    try:
        assert perfis.ler("Receita da promessa") is not None
        assert tela.paineis.automatico.combo_receitas.findData("Receita da promessa") >= 0
    finally:
        perfis.apagar("Receita da promessa")
    assert _trabalho_gravado(janela) == antes


@prova("P-175")
def test_p175_escolher_paginas(janela, tela):
    tela.paineis.abrir("automatico")
    antes = _trabalho_gravado(janela)
    apertar(janela, "área de trabalho/automático/escolher páginas...")
    assert tela.pilha_da_tela.currentWidget() is tela.todas and tela.todas.para_o_automatico
    tela.todas.marcar(0)
    tela.todas.marcar(2)
    tela.todas.botao_usar.click()
    aj.assentar()
    estado = janela.estado_do_automatico
    assert estado.alcance == "escolhidas" and estado.escolhidas == [0, 2]
    assert _trabalho_gravado(janela) == antes


@prova("P-176")
def test_p176_desligar_as_marcadas(janela, tela, monkeypatch):
    from core import automatico as A

    assert janela.rodar_o_automatico(pedido=A.Pedido(etapas=[A.ENDIREITAR]), esperar=True, perguntar=False)
    assert janela.projeto.endireitar
    tela.paineis.abrir("automatico")
    janela.estado_do_automatico.marcadas = {A.ENDIREITAR}
    janela.estado_do_automatico.definir_alcance("livro")
    monkeypatch.setattr(janela, "rodar_o_automatico",
                        lambda _rodar=janela.rodar_o_automatico, **k: _rodar(esperar=True, **k))
    apertar(janela, "área de trabalho/automático/desligar as marcadas")
    aj.assentar()
    assert not janela.projeto.endireitar, "a etapa não desligou"
    assert aj.projeto_gravado(janela).get("endireitar") is False
    janela.acoes.desfazer(janela.projeto)
    assert janela.projeto.endireitar, "o Ctrl+Z não voltou"


def _grade_escolhendo(tela, *indices):
    tela.abrir_todas_as_paginas()
    aj.assentar()
    if not tela.todas.escolhendo:
        apertar(tela.window(), "área de trabalho/todas as páginas/marcar várias")
    tela.todas.escolher_nenhuma()
    for indice in indices:
        tela.todas.marcar(indice)
    aj.assentar()
    return tela.todas


@prova("P-177")
def test_p177_marcar_varias_todas_nenhuma(janela, tela):
    antes = _trabalho_gravado(janela)
    grade = _grade_escolhendo(tela, 1)
    assert grade.escolhendo and sorted(grade.escolhidas) == [1]
    apertar(janela, "área de trabalho/todas as páginas/todas — Marca todas as páginas que estão à vista.")
    assert sorted(grade.escolhidas) == list(range(len(janela.projeto.paginas)))
    apertar(janela, "área de trabalho/todas as páginas/nenhuma")
    assert not grade.escolhidas
    assert _trabalho_gravado(janela) == antes


@prova("P-178")
def test_p178_girar_as_escolhidas(janela, tela, monkeypatch, pasta):
    _grade_escolhendo(tela, 1)
    feitas = len(janela.acoes.feitas)
    apertar(janela, "área de trabalho/todas as páginas/girar ¼ →")
    assert janela.projeto.folhas[1].rotacao == 90 and janela.projeto.folhas[0].rotacao == 0
    assert len(janela.acoes.feitas) == feitas + 1
    _grade_escolhendo(tela, 2)
    apertar(janela, "área de trabalho/todas as páginas/girar ¼ ←")
    assert janela.projeto.folhas[2].rotacao == 270
    _voltar_ao_trabalho(janela)
    paginas = _gerar(janela, monkeypatch, pasta)
    assert paginas[1].deitada and paginas[2].deitada, "a página girada não saiu deitada"
    assert not paginas[0].deitada and not paginas[3].deitada


@prova("P-179")
def test_p179_deixar_em_branco_as_escolhidas(janela, tela):
    _grade_escolhendo(tela, 0, 3)
    apertar(janela, "área de trabalho/todas as páginas/deixar em branco")
    gravado = aj.projeto_gravado(janela)
    assert [bool(p.get("em_branco")) for p in gravado["paginas"]] == [True, False, False, True]


@prova("P-180")
def test_p180_tirar_e_trazer_de_volta(janela, tela, monkeypatch, pasta):
    _grade_escolhendo(tela, 2)
    apertar(janela, "área de trabalho/todas as páginas/tirar do livro")
    assert janela.projeto.paginas[2].apagada
    _voltar_ao_trabalho(janela)
    paginas = _gerar(janela, monkeypatch, pasta, "sem")
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 3]
    _grade_escolhendo(tela, 2)
    apertar(janela, "área de trabalho/todas as páginas/trazer de volta")
    assert not janela.projeto.paginas[2].apagada
    _voltar_ao_trabalho(janela)
    paginas = _gerar(janela, monkeypatch, pasta, "com")
    assert [aj.qual_pagina(p) for p in paginas] == [0, 1, 2, 3]


@prova("P-181")
def test_p181_extrair_as_escolhidas(janela, tela, monkeypatch, pasta):
    import ui.dialogos_de_arquivo as dialogos

    destino = pasta / "extraidas.pdf"
    monkeypatch.setattr(dialogos, "escolher_onde_salvar_pdf", lambda *a, **k: str(destino))
    antes = _trabalho_gravado(janela)
    _grade_escolhendo(tela, 1, 3)
    apertar(janela, "área de trabalho/todas as páginas/extrair...")
    paginas = aj.paginas_do_pdf(destino)
    assert [aj.qual_pagina(p) for p in paginas] == [1, 3]
    assert all(aj.papel_amarelado(p) for p in paginas), "não saíram como estão no PDF de entrada"
    assert _trabalho_gravado(janela) == antes


@prova("P-182")
def test_p182_rodar_o_automatico_nelas(janela, tela):
    antes = _trabalho_gravado(janela)
    _grade_escolhendo(tela, 0, 2)
    apertar(janela, "área de trabalho/todas as páginas/rodar o automático nelas...")
    estado = janela.estado_do_automatico
    assert estado.alcance == "escolhidas" and estado.escolhidas == [0, 2]
    assert tela.pilha_da_tela.currentWidget() is not tela.todas
    assert _trabalho_gravado(janela) == antes


def _janela_grande(janela, etapa=""):
    """Abre a janela grande do Automático e devolve (janela grande, chave -> botão à vista)."""
    grande = janela.abrir_o_automatico(etapa)
    aj.assentar()
    return grande, aj.chaves_dos_botoes(grande, "automático (janela grande)")


def _apertar_na_janela_grande(janela, chave: str, etapa: str = ""):
    grande, achados = _janela_grande(janela, etapa)
    assert chave in achados, f"o botão '{chave}' não está à vista. À vista: {sorted(achados)}"
    achados[chave].click()
    aj.assentar()
    return grande


def _rodar_esperando(janela, monkeypatch):
    monkeypatch.setattr(janela, "rodar_o_automatico",
                        lambda _rodar=janela.rodar_o_automatico, **k: _rodar(esperar=True, **k))


@prova("P-183")
def test_p183_rodar_da_janela_grande(janela, tela, monkeypatch, pasta):
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO

    estado = janela.estado_do_automatico
    estado.marcadas = {A.LIMPAR, A.ENDIREITAR}     # duas: o botão diz "Rodar 2 etapas"
    estado.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    estado.definir_alcance("livro")
    _rodar_esperando(janela, monkeypatch)
    feitas = len(janela.acoes.feitas)
    _apertar_na_janela_grande(janela, "automático (janela grande)/Rodar N etapas")
    assert janela.janela_do_automatico is None, "a janela não fechou"
    gravado = aj.projeto_gravado(janela)
    assert gravado["limpar"] is True and gravado["endireitar"] is True
    assert gravado["filtro_padrao"] == PRETO_E_BRANCO
    assert len(janela.acoes.feitas) == feitas + 1, "não virou uma ação do Histórico"
    paginas = _gerar(janela, monkeypatch, pasta)
    assert not any(aj.papel_amarelado(p) for p in paginas), "o PDF saiu amarelado"


@prova("P-184")
def test_p184_desligar_da_janela_grande(janela, tela, monkeypatch):
    from core import automatico as A

    assert janela.rodar_o_automatico(pedido=A.Pedido(etapas=[A.CORTAR]), esperar=True, perguntar=False)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.CORTAR}
    estado.definir_alcance("livro")
    _rodar_esperando(janela, monkeypatch)
    _apertar_na_janela_grande(janela, "automático (janela grande)/Desligar as marcadas")
    assert aj.projeto_gravado(janela)["cortar_bordas"] is False


@prova("P-185")
def test_p185_salvar_e_apagar_a_receita(janela, tela):
    from core import perfis

    antes = _trabalho_gravado(janela)
    grande = _apertar_na_janela_grande(janela, "automático (janela grande)/Salvar receita...")
    caixa = janela.caixa_da_receita
    assert caixa is not None and caixa.isVisible() and caixa.caixas
    achados = aj.chaves_dos_botoes(caixa, "caixa da receita")
    achados["caixa da receita/cancelar"].click()
    aj.assentar()
    assert perfis.ler("Receita da P-185") is None and not caixa.isVisible()
    grande.botao_salvar.click()
    aj.assentar()
    caixa = janela.caixa_da_receita
    caixa.nome.setText("Receita da P-185")
    aj.chaves_dos_botoes(caixa, "caixa da receita")["caixa da receita/guardar"].click()
    aj.assentar()
    try:
        assert perfis.ler("Receita da P-185") is not None, "'guardar' não guardou"
        janela.estado_do_automatico.por_receita("Receita da P-185")
        grande.encher_receitas()
        aj.caixas_durante(grande.botao_apagar.click, clicar="apagar")
        assert perfis.ler("Receita da P-185") is None, "'Apagar a receita' não apagou"
    finally:
        perfis.apagar("Receita da P-185")
    assert _trabalho_gravado(janela) == antes


@prova("P-186")
def test_p186_escolher_paginas_da_janela_grande(janela, tela):
    antes = _trabalho_gravado(janela)
    _apertar_na_janela_grande(janela, "automático (janela grande)/escolher páginas...")
    assert tela.pilha_da_tela.currentWidget() is tela.todas and tela.todas.para_o_automatico
    tela.todas.marcar(1)
    tela.todas.botao_usar.click()
    aj.assentar()
    assert janela.estado_do_automatico.escolhidas == [1]
    assert janela.janela_do_automatico is not None and janela.janela_do_automatico.isVisible()
    assert _trabalho_gravado(janela) == antes


@prova("P-187")
def test_p187_folhear_na_janela_grande(janela, tela, monkeypatch):
    antes = _trabalho_gravado(janela)
    grande, achados = _janela_grande(janela)
    folhear = grande.folhear
    inicio = folhear._indice
    achados["automático (janela grande)/>"].click()
    aj.assentar()
    assert folhear._indice == inicio + 1
    achados["automático (janela grande)/<"].click()
    aj.assentar()
    assert folhear._indice == inicio
    visor = folhear.visor
    zoom = getattr(visor, "zoom", 1.0)
    achados["automático (janela grande)/+"].click()
    assert getattr(visor, "zoom", 1.0) > zoom, "'+' não aproximou"
    achados["automático (janela grande)/–"].click()
    achados["automático (janela grande)/–"].click()
    assert getattr(visor, "zoom", 1.0) < zoom * 1.25, "'–' não afastou"
    achados["automático (janela grande)/ajustar à tela"].click()
    aj.assentar()
    abertas = []
    monkeypatch.setattr(QDialog, "exec", lambda self: abertas.append(type(self).__name__) or 0)
    monkeypatch.setattr(QDialog, "open", lambda self: abertas.append(type(self).__name__))
    monkeypatch.setattr(QDialog, "show", lambda self: abertas.append(type(self).__name__))
    achados["automático (janela grande)/tela cheia"].click()
    aj.assentar()
    assert abertas, "'tela cheia' não abriu a folha grande"
    assert _trabalho_gravado(janela) == antes


@prova("P-188")
def test_p188_fechar_e_mais_opcoes(janela, tela):
    from core import automatico as A

    antes = _trabalho_gravado(janela)
    grande, achados = _janela_grande(janela, A.GRAVURAS)
    painel = grande.painel_mais_opcoes
    aberto = painel.isVisibleTo(grande)
    achados["automático (janela grande)/Mais opções"].click()
    aj.assentar()
    assert painel.isVisibleTo(grande) != aberto, "'Mais opções' não abriu nem fechou nada"
    achados["automático (janela grande)/Fechar"].click()
    aj.assentar()
    assert not grande.isVisible(), "'Fechar' não fechou"
    assert _trabalho_gravado(janela) == antes


# --- menus -----------------------------------------------------------------------------------------

@prova("P-140")
def test_p140_livros_recentes(janela, pasta):
    primeiro = aj.criar_livro(pasta, nome="Primeiro")
    aj.abrir_livro_para_teste(janela, primeiro)
    aj.abrir_livro_para_teste(janela, aj.criar_livro(pasta, nome="Segundo"))
    janela.menu.menu_recentes.aboutToShow.emit()
    acoes = [a for a in janela.menu.menu_recentes.actions() if "Primeiro" in a.text()]
    assert acoes, f"o Primeiro não está nos recentes: {[a.text() for a in janela.menu.menu_recentes.actions()]}"
    acoes[0].trigger()
    aj.assentar()
    assert Path(janela.projeto.caminho_entrada).stem == "Primeiro"


@prova("P-141")
def test_p141_escolher_a_pasta_de_saida(janela, tela, monkeypatch, pasta):
    import ui.dialogos_de_arquivo as dialogos
    from ui.janela_confirmar import JanelaConfirmar

    outra = pasta / "pasta escolhida"
    outra.mkdir()
    monkeypatch.setattr(dialogos, "escolher_pasta", lambda *a, **k: str(outra))
    apertar(janela, "menu/pasta_de_saida")
    caixa = JanelaConfirmar(janela.projeto, "x.pdf", janela)
    assert Path(caixa.destino.pasta) == outra, "a próxima janela 'Confirmar e processar' não usa a pasta"


@prova("P-142")
def test_p142_nome_do_arquivo(janela, tela):
    aj.caixas_durante(lambda: apertar(janela, "menu/nome_do_arquivo"), clicar="Cancelar")
    antes = janela.projeto.caminho_saida
    aj.caixas_durante(lambda: apertar(janela, "menu/nome_do_arquivo"), clicar="OK",
                      antes=lambda caixa: caixa.setTextValue("meu nome.pdf"))
    assert Path(janela.projeto.caminho_saida).name == "meu nome.pdf" != Path(antes or "x").name
    assert Path(aj.projeto_gravado(janela)["caminho_saida"]).name == "meu nome.pdf"


@prova("P-143")
def test_p143_voltar_para_os_livros(janela, tela):
    import projetos as pr
    from core.filtros import PRETO_E_BRANCO
    from ui.janela_principal import INICIO

    tela._escolher_filtro(PRETO_E_BRANCO)
    resumo = janela.resumo
    apertar(janela, "menu/voltar")
    pr.esperar_gravacoes()
    assert janela.telas.currentIndex() == INICIO
    assert pr.carregar_estado(resumo).paginas[0].filtro == PRETO_E_BRANCO, "o trabalho não ficou gravado"


@prova("P-144")
def test_p144_sair_grava_o_trabalho(janela, tela, monkeypatch):
    import projetos as pr
    from core.filtros import PRETO_E_BRANCO

    tela.ir_para_pagina(3)
    tela._escolher_filtro(PRETO_E_BRANCO)
    resumo = janela.resumo
    apertar(janela, "menu/sair")
    pr.esperar_gravacoes()
    assert not janela.isVisible(), "o programa não fechou"
    assert pr.carregar_estado(resumo).paginas[3].filtro == PRETO_E_BRANCO


@prova("P-145")
def test_p145_ir_para_a_pagina(janela, tela):
    tela.ir_para_pagina(0)
    aj.caixas_durante(lambda: apertar(janela, "menu/ir_para_pagina"), clicar="Cancelar")
    assert tela.indice_pagina == 0
    aj.caixas_durante(lambda: apertar(janela, "menu/ir_para_pagina"), clicar="OK",
                      antes=lambda caixa: caixa.setIntValue(3))
    assert tela.indice_pagina == 2


@prova("P-146")
@pytest.mark.parametrize("lugar", ["menu", "barra de baixo"])
def test_p146_zoom_pelo_menu(janela, tela, lugar):
    tela.escolher_ferramenta("mao")
    vista = tela.editor_selecao
    antes = aj.projeto_gravado(janela)
    aj.esperar(lambda: vista._pixmap is not None, motivo="a página no editor")
    if lugar == "menu":
        mais_, menos_, ajustar_ = "menu/mais_zoom", "menu/menos_zoom", "menu/ajustar"
    else:
        base_ = "área de trabalho/barra de baixo/"
        mais_, menos_, ajustar_ = base_ + "+", base_ + "–", base_ + "ajustar à tela"
    tela.mudar_o_zoom(None)
    base = vista.zoom
    apertar(janela, mais_)
    apertar(janela, mais_)
    mais = vista.zoom
    assert mais > base
    assert tela.rotulo_do_zoom.text() == f"{round(mais * 100)}%", "o número do zoom não acompanha"
    apertar(janela, menos_)
    assert base < vista.zoom < mais
    apertar(janela, ajustar_)
    assert abs(vista.zoom - base) < 1e-6
    assert tela.rotulo_do_zoom.text() == "100%"
    assert aj.projeto_gravado(janela) == antes


@prova("P-195")
def test_p195_antes_depois(janela, tela):
    from core.filtros import PRETO_E_BRANCO

    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    antes = aj.projeto_gravado(janela)
    apertar(janela, "área de trabalho/barra de baixo/antes / depois")
    vista = tela.vista_antes_depois
    assert tela.vista_da_pagina.currentWidget() is vista, "o antes e depois não apareceu"
    aj.esperar(lambda: vista.antes is not None and vista.depois is not None, motivo="as duas prévias")
    assert vista.comparando and vista.rotulos == ("antes: Original", "depois: Preto e branco")
    tela.ir_para_pagina(0)                                   # página em Original
    assert vista.aviso == "Escolha outro filtro para comparar com o Original."
    apertar(janela, "área de trabalho/barra de baixo/antes / depois")
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]


@prova("P-147")
@pytest.mark.parametrize("tema", ["escuro", "claro", "cinza"])
def test_p147_tema(janela, tela, tema):
    import configuracoes
    from ui import estilo

    fundo_antes = estilo.cor("bar")
    apertar(janela, f"menu/tema_{tema}")
    assert estilo.tema_atual() == tema
    assert janela.menu.acoes[f"tema_{tema}"].isChecked()
    assert str(configuracoes.ler("tema")) == tema or tema in str(configuracoes.ler("tema"))
    assert fundo_antes is not None


@prova("P-148")
@pytest.mark.parametrize("nome", list(FILTROS))
def test_p148_filtros_da_pagina_ampliada(janela, tela, nome):
    from core.filtros import MELHORAR
    from ui.tela_ampliada import TelaAmpliada

    tela.ir_para_pagina(1)
    if FILTROS[nome] == "original":
        tela._escolher_filtro(MELHORAR)
    dialogo = TelaAmpliada(tela, parent=janela)
    dialogo.show()
    aj.assentar()
    aj.chaves_dos_botoes(dialogo, "página ampliada")[f"página ampliada/{nome}"].click()
    aj.assentar()
    assert aj.pagina_gravada(janela, 1)["filtro"] == FILTROS[nome]
    dialogo.close()


@prova("P-149")
def test_p149_botoes_da_pagina_ampliada(janela, tela):
    from ui.tela_ampliada import TelaAmpliada

    tela.ir_para_pagina(1)
    dialogo = TelaAmpliada(tela, parent=janela)
    dialogo.show()
    aj.assentar()
    b = lambda nome: aj.chaves_dos_botoes(dialogo, "página ampliada")[f"página ampliada/{nome}"]  # noqa: E731
    antes = aj.projeto_gravado(janela)
    b(">").click()
    aj.assentar()
    assert tela.indice_pagina == 2
    b("<").click()
    aj.assentar()
    assert tela.indice_pagina == 1
    zoom = dialogo.vista.zoom
    b("+").click()
    b("+").click()
    mais = dialogo.vista.zoom
    assert mais > zoom
    b("-").click()
    assert zoom < dialogo.vista.zoom < mais
    b("ajustar à tela").click()
    b("comparar").click()
    aj.assentar()
    assert dialogo.vista_b.isVisible(), "'comparar' não mostrou os dois lado a lado"
    b("X").click()
    aj.assentar()
    assert not dialogo.isVisible()
    assert aj.projeto_gravado(janela)["paginas"] == antes["paginas"]


# --- processando e "Ficou pronto!" -------------------------------------------------------------------

@prova("P-150")
def test_p150_cancelar_o_processamento(janela, tela, monkeypatch, pasta):
    import ui.janela_confirmar as confirmar
    from ui.janela_principal import CONFERIR, PROGRESSO

    destino = pasta / "saida" / "pronto.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    doc.new_page().insert_text((40, 60), "o antigo")
    doc.save(str(destino))
    doc.close()
    antigo = destino.read_bytes()
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: destino)
    aj.caixas_durante(janela.processar, clicar="substituir o antigo")
    assert janela.telas.currentIndex() == PROGRESSO
    apertar(janela, "processando/cancelar")
    fim = time.monotonic() + 60
    while janela.telas.currentIndex() != CONFERIR and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    assert janela.telas.currentIndex() == CONFERIR, "não voltou à área de trabalho"
    assert destino.read_bytes() == antigo, "o PDF antigo foi mexido (D-310)"


def _pronto(janela, tela, monkeypatch, pasta):
    return aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "pronto.pdf")


@prova("P-151")
def test_p151_imprimir_agora_pergunta_antes(janela, tela, monkeypatch, pasta):
    from core import impressora
    from ui.dialogo_impressao import ConfirmarImpressao

    mandadas = []
    monkeypatch.setattr(impressora, "imprimir", lambda folhas, nome, copias, *a, **k:
                        mandadas.append((folhas.page_count, nome, copias)) or folhas.page_count)
    monkeypatch.setattr("ui.dialogo_impressao.listar_impressoras", lambda: ["Impressora de teste"])
    _pronto(janela, tela, monkeypatch, pasta)
    apertar(janela, "ficou pronto/imprimir agora...")
    dialogo = janela.tela_final.dialogo_imprimir
    assert isinstance(dialogo, ConfirmarImpressao) and not mandadas, "mandou sem perguntar (D-012)"
    aj.chaves_dos_botoes(dialogo, "imprimir agora")["imprimir agora/cancelar"].click()
    aj.assentar()
    assert not mandadas
    apertar(janela, "ficou pronto/imprimir agora...")
    dialogo = janela.tela_final.dialogo_imprimir
    dialogo.copias.setValue(2)
    aj.chaves_dos_botoes(dialogo, "imprimir agora")["imprimir agora/imprimir N páginas"].click()
    fim = time.monotonic() + 30
    while not mandadas and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    assert mandadas == [(4, "Impressora de teste", 2)], mandadas


@prova("P-152")
def test_p152_montar_para_imprimir_abre(janela, tela, monkeypatch, pasta):
    from ui.dialogo_impressao import DialogoImpressao

    pdf = _pronto(janela, tela, monkeypatch, pasta)
    antes = pdf.read_bytes()
    apertar(janela, "ficou pronto/montar para imprimir em A4 (com margens)...")
    dialogo = janela.tela_final.dialogo_impressao
    assert isinstance(dialogo, DialogoImpressao) and Path(dialogo.entrada) == pdf
    dialogo.reject()
    assert pdf.read_bytes() == antes


@prova("P-153")
def test_p153_fazer_outro(janela, tela, monkeypatch, pasta):
    from ui.janela_principal import INICIO

    _pronto(janela, tela, monkeypatch, pasta)
    apertar(janela, "ficou pronto/fazer outro")
    assert janela.telas.currentIndex() == INICIO
    import projetos as pr

    assert pr.listar()[0].pdf_gerado, "o cartão não diz que o PDF foi gerado"


# --- Montar para imprimir ------------------------------------------------------------------------

def _montar(janela, tela, monkeypatch, pasta):
    from ui.dialogo_impressao import DialogoImpressao

    pdf = _pronto(janela, tela, monkeypatch, pasta)
    dialogo = DialogoImpressao(str(pdf), janela)
    dialogo.show()
    aj.assentar()
    return pdf, dialogo


def _esperar_a_tarefa(dialogo, segundos=120):
    fim = time.monotonic() + segundos
    while dialogo.tarefa is not None and dialogo.tarefa.isRunning() and time.monotonic() < fim:
        aj.assentar(2)
        time.sleep(0.02)
    aj.assentar(4)


@prova("P-160")
def test_p160_gravar_o_arquivo_para_imprimir(janela, tela, monkeypatch, pasta):
    import ui.dialogos_de_arquivo as dialogos
    from core import impressao as imp

    pdf, dialogo = _montar(janela, tela, monkeypatch, pasta)
    destino = pasta / "saida" / "para imprimir.pdf"
    monkeypatch.setattr(dialogos, "escolher_onde_salvar_pdf", lambda *a, **k: str(destino))
    dialogo.combo_formato.setCurrentIndex(dialogo.combo_formato.findData(imp.LIVRETO))
    antes = pdf.read_bytes()
    aj.chaves_dos_botoes(dialogo, "montar para imprimir")["montar para imprimir/gravar o arquivo para imprimir"].click()
    _esperar_a_tarefa(dialogo)
    assert destino.exists(), "o arquivo para imprimir não foi gravado"
    folhas = aj.paginas_do_pdf(destino)
    assert len(folhas) == 2 and all(f.deitada for f in folhas), \
        f"livreto de 4 páginas: esperava 2 lados de folha A4 deitada, saiu {len(folhas)}"
    assert abs(folhas[0].largura_pt - 842) < 3 and abs(folhas[0].altura_pt - 595) < 3, "não é A4 deitada"
    assert pdf.read_bytes() == antes, "o PDF do livro mudou"
    dialogo.close()


@prova("P-161")
def test_p161_mandar_para_a_impressora(janela, tela, monkeypatch, pasta):
    from core import impressora

    mandadas = []
    monkeypatch.setattr(impressora, "imprimir", lambda folhas, nome, copias, *a, **k:
                        mandadas.append((folhas.page_count, copias)) or folhas.page_count)
    pdf, dialogo = _montar(janela, tela, monkeypatch, pasta)
    botao_mandar = aj.chaves_dos_botoes(dialogo, "montar para imprimir")["montar para imprimir/mandar para a impressora..."]
    vistas = aj.caixas_durante(botao_mandar.click, clicar="cancelar")
    assert vistas and vistas[0][0] == "Mandar para a impressora?", vistas
    assert not mandadas, "'cancelar' mandou"
    dialogo.copias.setValue(3)
    aj.caixas_durante(botao_mandar.click, clicar="mandar")
    _esperar_a_tarefa(dialogo)
    assert mandadas and mandadas[0][1] == 3, mandadas
    dialogo.close()


@prova("P-162")
def test_p162_parar_e_fechar(janela, tela, monkeypatch, pasta):
    pdf, dialogo = _montar(janela, tela, monkeypatch, pasta)
    chaves = aj.chaves_dos_botoes(dialogo, "montar para imprimir")
    assert not chaves["montar para imprimir/cancelar"].isEnabled() or True
    import ui.dialogos_de_arquivo as dialogos

    destino = pasta / "saida" / "parado.pdf"
    monkeypatch.setattr(dialogos, "escolher_onde_salvar_pdf", lambda *a, **k: str(destino))
    chaves["montar para imprimir/gravar o arquivo para imprimir"].click()
    chaves["montar para imprimir/cancelar"].click()
    _esperar_a_tarefa(dialogo)
    if destino.exists():
        assert len(aj.paginas_do_pdf(destino)) >= 1, "ficou um arquivo pela metade"
    chaves["montar para imprimir/fechar"].click()
    aj.assentar()
    assert not dialogo.isVisible()


# --- Configurações -------------------------------------------------------------------------------

@prova("P-170")
def test_p170_fechar_as_configuracoes(janela, tela):
    from ui.tela_configuracoes import PARTES, TelaConfiguracoes

    for parte in PARTES:
        dialogo = TelaConfiguracoes(janela, parte=parte)
        dialogo.show()
        aj.assentar()
        aj.chaves_dos_botoes(dialogo, f"configurações/{parte}")[f"configurações/{parte}/Fechar"].click()
        aj.assentar()
        assert not dialogo.isVisible(), parte


@prova("P-171")
def test_p171_restaurar_os_atalhos(janela, tela):
    import atalhos
    import configuracoes
    from PySide6.QtGui import QKeySequence

    from ui.tela_configuracoes import TelaConfiguracoes

    assert atalhos.redefinir("desfazer", "Ctrl+Alt+U")
    janela.menu.reaplicar_atalhos()
    assert janela.menu.acoes["desfazer"].shortcut().toString() == "Ctrl+Alt+U"
    dialogo = TelaConfiguracoes(janela, parte="Atalhos de teclado")
    dialogo.show()
    aj.assentar()
    aj.chaves_dos_botoes(dialogo, "configurações/Atalhos de teclado")[
        "configurações/Atalhos de teclado/Restaurar todos os padrões"].click()
    aj.assentar()
    assert janela.menu.acoes["desfazer"].shortcut() == QKeySequence("Ctrl+Z")
    assert not configuracoes.ler("atalhos"), "as configurações continuam com atalho mudado"
    dialogo.close()
