"""A opcao "No Preto e branco, molduras e iluminuras tambem em preto e branco".

Emenda do Samuel a regra do Preto e branco (conferencia 3, 30/09/2026, cartao
N2): "Mantem a cor original (como o ANTES); traco preto so se eu escolher" - e
"gostaria de ter a opcao de fazer isso em outras ocasioes e em outros livros".

Testes de maquina:
- o campo do projeto (Projeto.pb_decoracao_em_preto_e_branco) nasce False, e
  projeto antigo, sem o campo, abre com False;
- a caixinha da tela "O que fazer" nasce desmarcada, grava no projeto, volta
  ao reabrir, e num livro com trabalho vale ao clicar "Conferir";
- o processamento (core.pipeline._filtrar) passa a opcao ao filtro;
- a caixinha nao fica espremida numa janela baixa.

A imagem (moldura em cor de fabrica, em desenho com a opcao) e testada em
tests/test_preto_e_branco_regra_30_09.py. Pasta de dados propria (as fixtures
de tests/test_mesmo_livro_outro_caminho.py); nenhuma janela aparece na tela
(tests/conftest.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from modelos import ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


def test_o_campo_nasce_desligado_e_projeto_antigo_abre_desligado():
    assert Projeto(caminho_entrada="x.pdf").pb_decoracao_em_preto_e_branco is False
    dados = Projeto(caminho_entrada="x.pdf").para_dicionario()
    dados.pop("pb_decoracao_em_preto_e_branco")          # projeto gravado antes do campo
    assert Projeto.de_dicionario(dados).pb_decoracao_em_preto_e_branco is False
    dados["pb_decoracao_em_preto_e_branco"] = True
    assert Projeto.de_dicionario(dados).pb_decoracao_em_preto_e_branco is True


@pytest.mark.parametrize("ligada", [False, True])
def test_o_processamento_passa_a_opcao_ao_filtro(monkeypatch, ligada):
    pedidos = {}

    def espiao(img, filtro, selecao, *a, **k):
        pedidos.update(k)
        return img, False

    monkeypatch.setattr(pipeline, "aplicar_filtro_com_selecao", espiao)
    monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, **k: None)
    projeto = Projeto(caminho_entrada="x.pdf", pb_decoracao_em_preto_e_branco=ligada)
    pagina = ConfigPagina(indice=0, folha=0, filtro="preto_e_branco")
    pipeline._filtrar(projeto, pagina, np.zeros((10, 10, 3), np.uint8))
    assert pedidos.get("decoracao_em_preto_e_branco") is ligada


def test_a_caixinha_nasce_desmarcada_e_grava_no_projeto(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    caixa = tela.cx_decoracao_pb
    assert not caixa.isChecked() and projeto.pb_decoracao_em_preto_e_branco is False
    assert caixa.text() == "No Preto e branco, molduras e iluminuras também em preto e branco"
    caixa.setChecked(True)
    assert projeto.pb_decoracao_em_preto_e_branco is True
    caixa.setChecked(False)
    assert projeto.pb_decoracao_em_preto_e_branco is False
    # so aparece com "Limpar a folha" (fica no grupo dos filtros)
    tela.cx_limpar.setChecked(False)
    assert caixa.isHidden() or not caixa.isVisibleTo(tela)
    tela.cx_limpar.setChecked(True)


def test_reabrir_traz_a_opcao_salva(janela, pasta):
    livro = _pdf(pasta)
    janela.abrir_livro(str(livro))
    janela.tela_opcoes.cx_decoracao_pb.setChecked(True)
    _analisar(janela)
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None
    janela.tela_opcoes.folhear.fechar()

    janela.abrir_livro(str(livro))
    assert janela.tela_opcoes.cx_decoracao_pb.isChecked()
    assert janela.projeto.pb_decoracao_em_preto_e_branco is True


def test_num_livro_com_trabalho_vale_ao_clicar_conferir(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO

    # mudar e sair sem "Conferir": nao vai para o disco (como as outras opcoes)
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_decoracao_pb.setChecked(True)
    janela._salvar_agora()
    assert json.loads(estado.read_text(encoding="utf-8"))["pb_decoracao_em_preto_e_branco"] is False

    # com "Conferir", vale - e o trabalho salvo volta por cima sem apagar a opcao
    _analisar(janela)
    assert janela.projeto.pb_decoracao_em_preto_e_branco is True
    janela._salvar_agora()
    assert json.loads(estado.read_text(encoding="utf-8"))["pb_decoracao_em_preto_e_branco"] is True


@pytest.mark.parametrize("largura, altura", [(1000, 600), (1152, 560), (1366, 600)])
def test_janela_baixa_nao_espreme_a_caixinha(janela, pasta, largura, altura):
    from PySide6.QtWidgets import QApplication

    janela.abrir_livro(str(_pdf(pasta)))
    tela = janela.tela_opcoes
    tela.escolher_filtro_do_livro("preto_e_branco")
    janela.resize(largura, altura)
    janela.show()
    for _ in range(5):
        QApplication.processEvents()
    caixa = tela.cx_decoracao_pb
    assert caixa.height() >= caixa.minimumSizeHint().height()
    janela.hide()
