"""O registro único de atalhos - sem Qt, puro Python."""

from __future__ import annotations

import pytest

import atalhos


@pytest.fixture(autouse=True)
def registro_limpo():
    """Cada teste daqui começa com o registro vazio e, no fim, o registro de
    antes VOLTA, exato (sem as teclas de mentira registradas aqui). Antes de
    21/10/2026 o registro ficava vazio depois deste arquivo e os testes de
    tela seguintes perdiam as teclas do Cortar (Lista de bugs, 20/10)."""
    import copy

    antes = copy.deepcopy(atalhos._registro)
    atalhos.limpar_registro_para_teste()
    yield
    atalhos.limpar_registro_para_teste()
    atalhos._registro.update(antes)        # sem as teclas de mentira daqui


def test_registrar_e_ler_a_tecla_atual():
    atalhos.registrar("desfazer", "Desfazer", "Ctrl+Z")
    assert atalhos.tecla_atual("desfazer") == "Ctrl+Z"
    assert atalhos.tecla_padrao("desfazer") == "Ctrl+Z"


def test_registrar_de_novo_nao_apaga_mudanca():
    atalhos.registrar("girar", "Girar", "R")
    atalhos.redefinir("girar", "G")
    atalhos.registrar("girar", "Girar", "R")  # tela recarregada, por exemplo
    assert atalhos.tecla_atual("girar") == "G"


def test_chave_nunca_registrada_devolve_vazio():
    assert atalhos.tecla_atual("nao_existe") == ""


def test_redefinir_muda_a_tecla():
    atalhos.registrar("zoom", "Zoom", "Z")
    assert atalhos.redefinir("zoom", "X")
    assert atalhos.tecla_atual("zoom") == "X"


def test_redefinir_recusa_conflito():
    atalhos.registrar("retangulo", "Retângulo", "R")
    atalhos.registrar("rodar", "Girar", "G")
    assert not atalhos.redefinir("rodar", "R")
    assert atalhos.tecla_atual("rodar") == "G", "não deve ter mudado"


def test_conflito_aponta_o_nome_da_outra_acao():
    atalhos.registrar("a", "Ação A", "M")
    atalhos.registrar("b", "Ação B", "T")
    assert atalhos.conflito("b", "M") == "Ação A"
    assert atalhos.conflito("a", "T") == "Ação B"


def test_tecla_vazia_nunca_conflita():
    atalhos.registrar("a", "Ação A", "")
    atalhos.registrar("b", "Ação B", "")
    assert atalhos.conflito("b", "") is None


def test_redefinir_chave_nao_registrada_falha():
    assert not atalhos.redefinir("fantasma", "Q")


def test_restaurar_padrao_de_uma_acao():
    atalhos.registrar("espelhado", "Espelhado", "M")
    atalhos.redefinir("espelhado", "X")
    atalhos.restaurar_padrao("espelhado")
    assert atalhos.tecla_atual("espelhado") == "M"


def test_restaurar_todos_os_padroes():
    atalhos.registrar("a", "A", "1")
    atalhos.registrar("b", "B", "2")
    atalhos.redefinir("a", "9")
    atalhos.redefinir("b", "8")
    atalhos.restaurar_todos_os_padroes()
    assert atalhos.tecla_atual("a") == "1"
    assert atalhos.tecla_atual("b") == "2"


def test_carregar_de_aplica_por_cima_dos_padroes():
    atalhos.registrar("proporcao", "Proporção travada", "T")
    atalhos.carregar_de({"proporcao": "P"})
    assert atalhos.tecla_atual("proporcao") == "P"


def test_carregar_de_ignora_chave_desconhecida():
    atalhos.carregar_de({"nao_existe_mais": "Z"})  # não deve levantar
    assert not atalhos.registrado("nao_existe_mais")


def test_carregar_de_ignora_conflito_salvo():
    """Se o arquivo salvo tiver duas ações com a mesma tecla (corrupção
    manual, por exemplo), ignora a segunda em vez de deixar duas ações com o
    mesmo atalho."""
    atalhos.registrar("a", "A", "1")
    atalhos.registrar("b", "B", "2")
    atalhos.carregar_de({"a": "9", "b": "9"})
    assert atalhos.tecla_atual("a") == "9"
    assert atalhos.tecla_atual("b") == "2"


def test_overrides_para_salvar_so_traz_o_que_mudou():
    atalhos.registrar("a", "A", "1")
    atalhos.registrar("b", "B", "2")
    atalhos.redefinir("b", "8")
    assert atalhos.overrides_para_salvar() == {"b": "8"}


def test_todas_devolve_na_ordem_de_registro():
    atalhos.registrar("primeiro", "Primeiro", "1")
    atalhos.registrar("segundo", "Segundo", "2")
    nomes = [a.nome for a in atalhos.todas()]
    assert nomes == ["Primeiro", "Segundo"]


def test_regressao_quem_vem_depois_ve_o_registro_de_antes():
    """Bug da Lista de bugs (20/10/2026): "teste que depende da ordem" -
    test_paineis_na_tela.py::test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem
    falhava na suíte inteira ("Espelhado   (tecla )") e passava sozinho,
    porque este arquivo esvaziava o registro global e não o devolvia. Roda,
    num processo à parte, este arquivo seguido de um que importa a tela na
    coleta e do teste que falhava: tem de passar."""
    import subprocess
    import sys
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "tests/test_atalhos.py::test_registrar_e_ler_a_tecla_atual", "tests/test_endireitar_na_tela.py",
         "tests/test_paineis_na_tela.py::test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem"],
        cwd=raiz, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    assert r.returncode == 0, r.stdout[-3000:]
