"""As provas da D-646 e da D-699: nenhum filtro traz o fundo de volta; só o "Desfazer o tirar o fundo".

O defeito (achado no teste como o Kaique de 07/11/2026; Central `k0711-auto-tira-fundo`;
print `relatorios/graves-2026-11-10/prints/d646-pergunta.png` do ramo graves-2026-11-10):
Siebmacher, "Sim, tirar o fundo" na pergunta do livro, o papel fica branco; rodando o
Automático (que abre com "Limpar a folha" em Original), o papel velho volta em todas as
páginas, sem aviso. A causa: o fundo tirado era guardado SÓ no filtro da página
("tirar_fundo"); trocar de filtro apagava a marca, e o fundo voltava.

  D-646 (07/11): "Consertar" · "É só criar uma opção para desfazer o tirar fundo, e só vai
      desfazer o tirar fundo quando apertar ela. E via de regra, nenhum filtro deve fazer o
      fundo voltar."
  D-699 (13/11, "Ok"): o botão "Desfazer o tirar o fundo" fica logo abaixo do "Tirar o
      fundo" no menu Filtro e no painel "Filtro da página" (embaixo das figurinhas), com o
      "Aplicar em" de sempre. Depois do "Tirar o fundo", o Preto e branco, o Melhorar, o
      Mágico pro, o Original e o Automático trabalham em cima da página já sem o fundo.
      Projetos salvos com "Tirar o fundo" abrem com o fundo tirado e o filtro Original.
  D-134 (29/09): "eu quero poder escolher tirar o fundo sem colocar nenhum filtro."
  D-667 (10/11) e CLAUDE.md §11.12: a regra vale em todos os caminhos, escrita num lugar
      só (core/fundo_tirado.py). Por isso a prova principal passa pelos caminhos que trocam
      filtro e cobra o MESMO resultado (a mesma imagem) em todos.

A medida do fundo: a cor do papel num trecho sem letra (tests/test_tirar_fundo_no_programa
._papel): com o fundo tirado o papel é branco (> 250 nos três canais); com o fundo, o
amarelado do PDF de teste (tests/test_camadas.PAPEL_RGB). PDFs com camadas montados na hora
(como os do Internet Archive), o detector de figuras trocado por um que não acha nada.
"""

from __future__ import annotations

import json

import fitz
import numpy as np
import pytest

from core import camadas, pipeline
from core.filtros import (FILTROS, MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO,
                          TIRAR_FUNDO)
from modelos import Projeto
from tests.test_camadas import PAPEL_RGB, sem_figuras
from tests.test_tirar_fundo_no_programa import _papel, _pdf_camadas, _projeto


@pytest.fixture(autouse=True)
def detector_sem_figuras(monkeypatch):
    """O detector de figuras do core/camadas.py não acha nada (rápido, sem o modelo)."""
    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)


@pytest.fixture(scope="module")
def app():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    """A janela de verdade, com os projetos numa pasta à parte."""
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    yield janela
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela._fechar_a_janela_do_automatico()
    janela.close()


def _desenho(projeto: Projeto, indice: int = 0, dpi: int = 60) -> np.ndarray:
    """A página como sai (core.pipeline.renderizar_pagina: o mesmo da prévia e do PDF)."""
    with fitz.open(projeto.caminho_entrada) as doc:
        img, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[indice], dpi=dpi)
    return img


def _sem_fundo(img: np.ndarray) -> bool:
    """O papel saiu branco (o fundo tirado)?"""
    return bool(_papel(img).min() > 250)


def _com_fundo(img: np.ndarray) -> bool:
    """O papel saiu com o amarelado do PDF (o fundo de volta)?"""
    return bool(np.abs(_papel(img)[::-1] - np.array(PAPEL_RGB)).max() < 6)


def _abrir_com_o_fundo_tirado(janela, tmp_path, paginas: int = 2):
    """Abre um livro com camadas e responde "Sim, tirar o fundo", como o Kaique."""
    from PySide6.QtWidgets import QAbstractButton

    janela.abrir_livro(_pdf_camadas(tmp_path, paginas=paginas))
    caixa = janela.aviso_do_fundo
    assert caixa is not None
    next(b for b in caixa.findChildren(QAbstractButton)
         if b.text() == "Sim, tirar o fundo").click()
    janela.projeto.detectar_regioes = False       # o modelo é lento e não é o assunto
    return janela.tela_conferir


def _rodar_o_automatico(janela, filtro: str) -> None:
    """O Automático do jeito que ele abre: "Limpar a folha" no livro todo com `filtro`."""
    from core import automatico as A

    pedido = A.Pedido(etapas=[A.LIMPAR], opcoes={"filtro_padrao": filtro}, pular_mexidas=True)
    janela.rodar_o_automatico(pedido=pedido, esperar=True, perguntar=False)


# --- a reversão: o defeito de 07/11 -------------------------------------------------------


def test_d646_sim_tirar_o_fundo_e_o_automatico_nao_traz_o_fundo_de_volta(janela, tmp_path):
    """REVERSÃO (falha no 863cdde3): "Sim, tirar o fundo" e depois o Automático do jeito
    que ele abre ("Limpar a folha" em Original). Antes: as páginas voltavam com o papel
    velho, sem aviso. Agora: o filtro vira Original e o papel continua branco."""
    _abrir_com_o_fundo_tirado(janela, tmp_path)
    projeto = janela.projeto
    assert all(_sem_fundo(_desenho(projeto, i)) for i in range(2))
    _rodar_o_automatico(janela, ORIGINAL)
    assert [p.filtro for p in projeto.paginas] == [ORIGINAL, ORIGINAL]
    for i in range(2):
        assert _sem_fundo(_desenho(projeto, i)), f"o fundo voltou na página {i + 1}"


# --- a mesma regra em todos os caminhos (CLAUDE.md §11.12) ---------------------------------


def _por_tecla(conferir, tecla) -> None:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert conferir.tratar_tecla(QKeyEvent(QEvent.KeyPress, tecla, Qt.NoModifier))


def _caminho(janela, conferir, nome: str) -> None:
    """Põe a página 1 em Original pelo caminho `nome` (a página 2 também, nos que valem
    para várias)."""
    from PySide6.QtCore import Qt

    if nome == "figurinha":
        conferir.cartoes[ORIGINAL].escolhido.emit(ORIGINAL)
    elif nome == "figurinha_do_painel":
        conferir.paineis.filtro_da_pagina.filtro_escolhido.emit(ORIGINAL)
    elif nome == "tecla_1":
        _por_tecla(conferir, Qt.Key_1)
    elif nome == "menu_filtro":
        janela.menu.acoes[f"filtro_{ORIGINAL}"].trigger()
    elif nome == "tela_cheia":
        conferir.usar_da_tela_cheia(ORIGINAL, None, "esta")
    elif nome == "aplicar_em_todas":
        conferir._escolher_filtro(ORIGINAL)
        conferir._filtro_em_todas()
    elif nome == "aplicar_daqui_em_diante":
        conferir._escolher_filtro(ORIGINAL)
        conferir._filtro_nas_proximas()
    elif nome == "automatico":
        _rodar_o_automatico(janela, ORIGINAL)
    else:
        raise AssertionError(nome)


CAMINHOS = ("figurinha", "figurinha_do_painel", "tecla_1", "menu_filtro", "tela_cheia",
            "aplicar_em_todas", "aplicar_daqui_em_diante", "automatico")


@pytest.mark.parametrize("nome", CAMINHOS)
def test_d699_o_original_nao_traz_o_fundo_em_nenhum_caminho(janela, tmp_path, nome):
    """D-646/D-699/D-667: pelo cartão, pela figurinha do painel, pela tecla 1, pelo menu
    Filtro, pela tela cheia, pelo "Aplicar em" (todas, daqui em diante) e pelo
    Automático: a página vai para o Original e sai EXATAMENTE como no "Tirar o fundo"
    (a mesma imagem, ponto por ponto: a mesma regra, core/fundo_tirado), com o papel
    branco. O fundo tirado fica gravado na página, separado do filtro."""
    conferir = _abrir_com_o_fundo_tirado(janela, tmp_path)
    projeto = janela.projeto
    antes = [_desenho(projeto, i) for i in range(2)]
    assert all(_sem_fundo(img) for img in antes)
    _caminho(janela, conferir, nome)
    assert projeto.paginas[0].filtro == ORIGINAL
    for i in range(2):
        depois = _desenho(projeto, i)
        assert _sem_fundo(depois), f"{nome}: o fundo voltou na página {i + 1}"
        assert np.array_equal(depois, antes[i]), f"{nome}: a página {i + 1} mudou"
    from core import fundo_tirado

    assert fundo_tirado.valor(projeto.paginas[0]) is True


def test_d699_o_desfazer_e_o_refazer_devolvem_o_fundo_tirado_junto(janela, tmp_path):
    """Ctrl+Z / Ctrl+Shift+Z: a troca de filtro e o fundo tirado vão na mesma ação. O
    Ctrl+Z do "Original" volta ao "Tirar o fundo" (sem fundo); o Ctrl+Z do "Sim" traz o
    fundo de volta (desfaz o que foi feito); o refazer refaz os dois."""
    from core import fundo_tirado

    conferir = _abrir_com_o_fundo_tirado(janela, tmp_path)
    projeto = janela.projeto
    conferir._escolher_filtro(ORIGINAL)
    conferir.desfazer()
    assert projeto.paginas[0].filtro == TIRAR_FUNDO
    assert _sem_fundo(_desenho(projeto))
    conferir.desfazer()                                  # o "Sim" da pergunta
    assert projeto.paginas[0].filtro == ORIGINAL
    assert not fundo_tirado.esta_sem_o_fundo(projeto, projeto.paginas[0])
    assert _com_fundo(_desenho(projeto))
    conferir.refazer()
    conferir.refazer()
    assert projeto.paginas[0].filtro == ORIGINAL
    assert fundo_tirado.valor(projeto.paginas[0]) is True
    assert _sem_fundo(_desenho(projeto))


# --- os filtros por cima da página sem o fundo ---------------------------------------------


@pytest.mark.parametrize("filtro", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_d699_o_filtro_trabalha_em_cima_da_pagina_sem_o_fundo(tmp_path, filtro, monkeypatch):
    """D-699: depois do "Tirar o fundo", o Preto e branco, o Melhorar e o Mágico pro são
    feitos em cima da página SEM o fundo: o "tirar o fundo" roda e o filtro também, e a
    imagem é a do filtro sobre a página sem o fundo. A figurinha (renderizar_com_filtro)
    mostra a mesma imagem que a página tem depois de escolhida, e o PDF sai igual à
    prévia (D-473)."""
    from core import fundo_tirado

    from core.filtros import aplicar_filtro_com_selecao

    chamadas = {"fundo": 0, "filtro": 0}
    original_tirar = camadas.tirar_fundo

    def tirar(*a, **k):
        chamadas["fundo"] += 1
        return original_tirar(*a, **k)

    def filtrar(*a, **k):
        chamadas["filtro"] += 1
        return aplicar_filtro_com_selecao(*a, **k)

    monkeypatch.setattr(camadas, "tirar_fundo", tirar)
    monkeypatch.setattr(pipeline, "aplicar_filtro_com_selecao", filtrar)
    projeto = _projeto(_pdf_camadas(tmp_path))            # página em "Tirar o fundo"
    pagina = projeto.paginas[0]
    with fitz.open(projeto.caminho_entrada) as doc:
        figurinha, _ = pipeline.renderizar_com_filtro(doc, projeto, pagina, filtro, dpi=100)
    pagina.fundo_tirado = fundo_tirado.depois_da_troca(projeto, pagina, filtro)
    pagina.filtro = filtro
    assert pagina.fundo_tirado is True
    chamadas.update(fundo=0, filtro=0)
    pipeline._DECISOES_DO_FUNDO.clear()
    previa = _desenho(projeto, dpi=100)
    assert chamadas["fundo"] == 1 and chamadas["filtro"] == 1
    assert np.array_equal(previa, figurinha)
    # a mesma página com o fundo (sem o "tirar o fundo") sai diferente
    pagina.fundo_tirado = None
    assert not np.array_equal(_desenho(projeto, dpi=100), previa)
    pagina.fundo_tirado = True
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    from tests.test_tirar_fundo_no_programa import _paginas_do_pdf

    gravada = _paginas_do_pdf(projeto.caminho_saida)[0]
    if previa.ndim == 2:
        gravada = gravada[:, :, 0]
    assert gravada.shape[:2] == previa.shape[:2]
    assert np.array_equal(gravada, previa)


def test_d646_a_regra_nenhum_filtro_traz_o_fundo():
    """A regra, sozinha (core/fundo_tirado.depois_da_troca): com o fundo tirado, todo
    filtro mantém o fundo tirado; "Tirar o fundo" tira; sem o fundo tirado, os outros
    filtros não tiram (D-134: "sem mudança escondida")."""
    from core import fundo_tirado

    from modelos import ConfigPagina

    projeto = Projeto(caminho_entrada="x.pdf", tem_camadas=True, limpar=True)
    sem = ConfigPagina(indice=0, folha=0, filtro=TIRAR_FUNDO)
    com = ConfigPagina(indice=1, folha=0, filtro=ORIGINAL)
    desfeita = ConfigPagina(indice=2, folha=0, filtro=ORIGINAL, fundo_tirado=False)
    for filtro in FILTROS:
        assert fundo_tirado.depois_da_troca(projeto, sem, filtro) is True
    for pagina in (com, desfeita):
        assert fundo_tirado.depois_da_troca(projeto, pagina, TIRAR_FUNDO) is True
        for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            assert fundo_tirado.depois_da_troca(projeto, pagina, filtro) is not True


# --- o "Desfazer o tirar o fundo" (o único que traz o fundo de volta) ---------------------


def test_d699_desfazer_pelo_menu_e_pelo_painel_e_a_mesma_acao(janela, tmp_path):
    """D-699: o item do menu Filtro e o botão do painel (embaixo das figurinhas) fazem o
    mesmo: o fundo volta na página da vez (papel amarelado), a página no "Tirar o fundo"
    fica no Original, numa ação do desfazer (Ctrl+Z tira o fundo de novo). Depois, o
    "Aplicar em" leva o fundo de volta às outras páginas."""
    from core import fundo_tirado

    conferir = _abrir_com_o_fundo_tirado(janela, tmp_path, paginas=3)
    projeto = janela.projeto
    janela._marcar_o_filtro_no_menu()
    item = janela.menu.acoes["desfazer_tirar_fundo"]
    botao = conferir.botao_desfazer_fundo
    assert item.text() == botao.text() == "Desfazer o tirar o fundo"
    assert item.isVisible() and item.isEnabled() and botao.isEnabled()
    # o botão fica logo abaixo das figurinhas, no painel
    dentro = conferir.paineis.filtro_da_pagina.dentro
    posicoes = [dentro.itemAt(i).widget() for i in range(dentro.count())]
    assert posicoes.index(botao) == posicoes.index(conferir.paineis.filtro_da_pagina._fila) + 1

    item.trigger()                                     # menu, página 1
    assert projeto.paginas[0].filtro == ORIGINAL
    assert fundo_tirado.valor(projeto.paginas[0]) is False
    assert _com_fundo(_desenho(projeto, 0))
    assert _sem_fundo(_desenho(projeto, 1))           # só nesta
    janela._marcar_o_filtro_no_menu()
    assert not item.isEnabled()                        # nada mais a desfazer aqui
    conferir.desfazer()
    assert _sem_fundo(_desenho(projeto, 0))
    conferir.refazer()
    assert _com_fundo(_desenho(projeto, 0))

    conferir.ir_para_pagina(1)
    assert conferir.indice_pagina == 1
    botao.click()                                      # painel, página 2
    assert projeto.paginas[1].filtro == ORIGINAL
    assert fundo_tirado.valor(projeto.paginas[1]) is False
    assert _com_fundo(_desenho(projeto, 1))
    assert _sem_fundo(_desenho(projeto, 2))
    conferir._filtro_nas_proximas()                    # "Aplicar em": daqui em diante
    assert _com_fundo(_desenho(projeto, 2))


def test_d699_aplicar_em_de_pagina_que_nunca_teve_o_fundo_tirado_nao_traz_o_fundo(janela,
                                                                                 tmp_path):
    """O "Aplicar em" leva o fundo só da página que o tem tirado ou desfeito: de uma
    página que nunca teve o fundo tirado (Original de fábrica), levar o filtro às outras
    não traz o fundo de volta nelas (só o "Desfazer o tirar o fundo" traz)."""
    from historico_acoes import aplicar, montar_acao

    conferir = _abrir_com_o_fundo_tirado(janela, tmp_path, paginas=2)
    projeto = janela.projeto
    # a página 1 volta ao de fábrica (nunca tirado), sem passar pela regra
    acao = montar_acao(projeto, "teste", "pagina", [0],
                       {"filtro": ORIGINAL, "fundo_tirado": None}, "teste")
    aplicar(projeto, acao, acao.depois)
    assert _com_fundo(_desenho(projeto, 0))
    conferir._filtro_em_todas()
    assert _sem_fundo(_desenho(projeto, 1))


def test_d699_livro_sem_camadas_nao_tem_o_desfazer(janela, tmp_path):
    """Como a figurinha "Tirar o fundo": livro sem camadas não mostra o botão nem o item."""
    from tests.test_tirar_fundo_no_programa import _pdf_sem_camadas

    janela.abrir_livro(_pdf_sem_camadas(tmp_path))
    janela._marcar_o_filtro_no_menu()
    assert janela.tela_conferir.botao_desfazer_fundo is None
    assert not janela.menu.acoes["desfazer_tirar_fundo"].isVisible()


# --- o projeto: o campo novo e os projetos antigos ------------------------------------------


def test_d699_o_fundo_tirado_vai_e_volta_do_disco_separado_do_filtro():
    from modelos import ConfigPagina

    projeto = Projeto(caminho_entrada="livro.pdf", tem_camadas=True)
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO, fundo_tirado=True),
                       ConfigPagina(indice=1, folha=0, filtro=ORIGINAL, fundo_tirado=False),
                       ConfigPagina(indice=2, folha=0, filtro=ORIGINAL)]
    dados = json.loads(json.dumps(projeto.para_dicionario()))
    assert [p["fundo_tirado"] for p in dados["paginas"]] == [True, False, None]
    volta = Projeto.de_dicionario(dados)
    assert [(p.filtro, p.fundo_tirado) for p in volta.paginas] == [
        (PRETO_E_BRANCO, True), (ORIGINAL, False), (ORIGINAL, None)]


def test_d699_projeto_antigo_em_tirar_o_fundo_abre_com_o_fundo_tirado_e_o_original(tmp_path):
    """Projeto gravado antes do conserto (a página sem a chave "fundo_tirado"): a página em
    "Tirar o fundo" abre com o fundo tirado e o filtro Original (palavras da pergunta
    aprovada), sem erro, e sai IGUAL, ponto por ponto; a página em outro filtro não muda."""
    projeto = _projeto(_pdf_camadas(tmp_path, paginas=2))
    projeto.paginas[1].filtro = PRETO_E_BRANCO
    como_era = _desenho(projeto, 0)
    dados = json.loads(json.dumps(projeto.para_dicionario()))
    for p in dados["paginas"]:
        del p["fundo_tirado"]
    aberto = Projeto.de_dicionario(dados)
    assert aberto.paginas[0].filtro == ORIGINAL
    assert aberto.paginas[0].fundo_tirado is True
    assert aberto.paginas[1].filtro == PRETO_E_BRANCO
    assert aberto.paginas[1].fundo_tirado is None
    assert np.array_equal(_desenho(aberto, 0), como_era)


def test_d699_projeto_antigo_abre_pelo_disco(tmp_path, monkeypatch):
    """O mesmo, pelo caminho de verdade (projetos.carregar_estado)."""
    import projetos

    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: tmp_path / "projetos")
    projeto = _projeto(_pdf_camadas(tmp_path))
    resumo = projetos.criar(projeto, 1)
    projetos.salvar_estado(resumo, projeto)
    arquivo = next(p for p in (tmp_path / "projetos").rglob("*.json")
                   if p.name == projetos.ARQUIVO_ESTADO)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    for p in dados["paginas"]:
        p.pop("fundo_tirado", None)
    arquivo.write_text(json.dumps(dados), encoding="utf-8")
    lido = projetos.carregar_estado(resumo)
    assert lido is not None
    assert (lido.paginas[0].filtro, lido.paginas[0].fundo_tirado) == (ORIGINAL, True)
    assert _sem_fundo(_desenho(lido))
