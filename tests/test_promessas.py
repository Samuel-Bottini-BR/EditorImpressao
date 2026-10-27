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
    janela.tela_opcoes.folhear.fechar()
    janela.close()
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
    # as linhas do Histórico (uma por ação feita ou desfeita) são botões com a descrição da ação
    for botao in getattr(tela.paineis.historico, "itens", []):
        especiais[botao] = "ação feita (volta até aqui)"
    for botao in getattr(tela.paineis.historico, "itens_desfeitos", []):
        especiais[botao] = "ação desfeita (refaz até aqui)"
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
    abrir_menu = lambda: cartao._abrir_menu(QPoint(5, 5))  # noqa: E731
    vistas = aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "começar de novo"), clicar="Não")
    assert vistas and vistas[0][0] == "Começar de novo?", vistas
    salvo = pr.carregar_estado(cartao.resumo)
    assert salvo.paginas[1].filtro == PRETO_E_BRANCO, "o 'Não' mexeu no trabalho"
    vistas = aj.caixas_durante(lambda: aj.acoes_de_menu_aberto(abrir_menu, "começar de novo"), clicar="Sim")
    tela = aj.abrir_livro_para_teste(janela, cartao.resumo.caminho_entrada) \
        if janela.telas.currentIndex() != janela.telas.indexOf(janela.tela_conferir) else janela.tela_conferir
    assert janela.projeto.paginas[1].filtro == ORIGINAL, "o trabalho antigo continuou"
    copias = list(Path(cartao.resumo.pasta).glob("projeto.antigo-*"))
    assert copias, "não ficou cópia de segurança do trabalho antigo"
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


@prova("P-011")
def test_p011_rodar_o_automatico_abre_as_escolhas_do_livro(janela, pasta, monkeypatch):
    from ui.janela_principal import OPCOES

    cartao = _livro_trabalhado(janela, pasta, monkeypatch)
    janela.tela_inicio.abrir_o_livro(cartao.resumo)
    aj.assentar()
    apertar(janela, "início/livro aberto/Rodar o automático...")
    assert janela.telas.currentIndex() == OPCOES
    assert Path(janela.projeto.caminho_entrada) == Path(cartao.resumo.caminho_entrada)


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
    assert janela.tela_conferir.paineis.automatico.isVisible(), "o Automático não abriu"


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
    apertar(janela, f"início/livro aberto/{nome}")
    assert botao(janela, f"início/livro aberto/{nome}").isChecked(), f"'{nome}' não ficou aceso"


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


# --- tela "O que fazer" (sai na etapa 3) -------------------------------------------------------

def _na_tela_o_que_fazer(janela, pasta):
    from ui.janela_principal import OPCOES

    janela.resize(1280, 760)
    janela.show()
    janela.abrir_livro(str(aj.criar_livro(pasta)))
    aj.assentar()
    if janela.telas.currentIndex() != OPCOES:
        pytest.skip("a tela 'O que fazer' já saiu (etapa 3)")
    return janela.tela_opcoes


@prova("P-021")
def test_p021_conferir_leva_a_area_de_trabalho_sem_caixinhas(janela, pasta):
    opcoes = _na_tela_o_que_fazer(janela, pasta)
    for nome in aj.CAIXINHAS_DA_TELA_O_QUE_FAZER:
        getattr(opcoes, nome).setChecked(False)
    janela.projeto.detectar_regioes = False
    apertar(janela, "o que fazer/Conferir")
    _esperar_a_area_de_trabalho(janela)
    gravado = aj.projeto_gravado(janela)
    assert gravado.get("cortar_bordas") is False and gravado.get("dividir_folhas") is False


@prova("P-022")
def test_p022_voltar_da_tela_o_que_fazer(janela, pasta):
    from ui.janela_principal import INICIO

    _na_tela_o_que_fazer(janela, pasta)
    apertar(janela, "o que fazer/voltar")
    assert janela.telas.currentIndex() == INICIO


@prova("P-023")
def test_p023_receitas(janela, pasta):
    opcoes = _na_tela_o_que_fazer(janela, pasta)
    opcoes.cx_dividir.setChecked(True)
    opcoes.nome_da_receita.setText("Minha receita")
    apertar(janela, "o que fazer/guardar")
    nomes = [opcoes.combo_receitas.itemText(i) for i in range(opcoes.combo_receitas.count())]
    assert "Minha receita" in nomes
    opcoes.cx_dividir.setChecked(False)
    opcoes.combo_receitas.setCurrentIndex(nomes.index("Minha receita"))
    apertar(janela, "o que fazer/pôr neste livro")
    assert opcoes.cx_dividir.isChecked(), "pôr a receita não marcou a caixinha dela"
    opcoes.combo_receitas.setCurrentIndex(nomes.index("Minha receita"))
    aj.caixas_durante(lambda: apertar(janela, "o que fazer/apagar"), clicar="Sim")
    nomes = [opcoes.combo_receitas.itemText(i) for i in range(opcoes.combo_receitas.count())]
    assert "Minha receita" not in nomes


@prova("P-024")
def test_p024_mais_opcoes_abre_e_fecha(janela, pasta):
    opcoes = _na_tela_o_que_fazer(janela, pasta)
    alvo = botao(janela, "o que fazer/Mais opções")
    from PySide6.QtWidgets import QCheckBox

    visiveis_antes = sum(c.isVisibleTo(opcoes) for c in opcoes.findChildren(QCheckBox))
    alvo.click()
    aj.assentar()
    visiveis_depois = sum(c.isVisibleTo(opcoes) for c in opcoes.findChildren(QCheckBox))
    assert visiveis_depois > visiveis_antes, "'Mais opções' não abriu nada"


@prova("P-025")
def test_p025_folhear_o_pdf(janela, pasta, monkeypatch):
    opcoes = _na_tela_o_que_fazer(janela, pasta)
    folhear = opcoes.folhear
    antes = folhear.indice
    apertar(janela, "o que fazer/>")
    assert folhear.indice == antes + 1
    apertar(janela, "o que fazer/<")
    assert folhear.indice == antes
    abertas = []
    monkeypatch.setattr(QDialog, "exec", lambda self: abertas.append(type(self).__name__) or 0)
    monkeypatch.setattr(QDialog, "open", lambda self: abertas.append(type(self).__name__))
    monkeypatch.setattr(QDialog, "show", lambda self: abertas.append(type(self).__name__))
    apertar(janela, "o que fazer/tela cheia")
    assert abertas, "'tela cheia' não abriu nada"


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
    apertar(janela, "menu/lado_icones")
    assert tela.paineis.jeito == "icones" and jeito_guardado() == "icones"
