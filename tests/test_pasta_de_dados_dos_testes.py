"""Os testes nunca gravam na pasta de dados real do Samuel (tests/conftest.py).

Pedido da gerente em 29/09/2026: o erros.log real ganhava entradas de teste a
cada rodada, e pastas de projeto de teste ja nasceram na pasta real. O
conftest.py troca LOCALAPPDATA para uma pasta de saida_teste\\ antes de
qualquer teste; aqui se confere que tudo o que o programa grava cai nela.
"""

from __future__ import annotations

import os
from pathlib import Path

import configuracoes
import historico
import projetos
import registro
from tests.conftest import PASTA_DE_DADOS_DOS_TESTES


def _real() -> Path | None:
    valor = os.environ.get("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL")
    return Path(valor) if valor else None


def test_a_pasta_de_dados_e_a_dos_testes():
    assert historico.pasta_de_dados().is_relative_to(PASTA_DE_DADOS_DOS_TESTES)


def test_erros_log_projetos_historico_e_configuracoes_ficam_fora_da_pasta_real():
    caminhos = [registro.caminho_do_log(), projetos.pasta_dos_projetos(),
                historico._caminho_historico(), configuracoes._caminho()]
    for caminho in caminhos:
        assert caminho.is_relative_to(PASTA_DE_DADOS_DOS_TESTES), caminho
        if _real() is not None:
            assert not caminho.is_relative_to(_real() / "EditorImpressao"), caminho


def test_um_erro_registrado_vai_para_o_log_de_mentira():
    registro.registrar_erro("teste", "conferindo onde o erros.log mora")
    assert "conferindo onde o erros.log mora" in registro.caminho_do_log().read_text(
        encoding="utf-8")
