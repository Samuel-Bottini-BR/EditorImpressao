"""Teste de reversão do bug "teste que depende da ordem" (Lista de bugs,
20/10/2026), num arquivo SÓ dele, sem nada do conserto: o conserto mora em
tests/conftest.py (_atalhos_isolados) e em tests/test_atalhos.py; para provar
no código antigo, troca-se aqueles dois pelo antigo e este fica (pedido do
verificador, 21/10/2026)."""

from __future__ import annotations


def test_regressao_quem_vem_depois_ve_o_registro_de_antes():
    """Bug da Lista de bugs (20/10/2026): "teste que depende da ordem" -
    test_paineis_na_tela.py::test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem
    falhava na suíte inteira ("Espelhado   (tecla )") e passava sozinho,
    porque o test_atalhos.py esvaziava o registro global e não o devolvia. Roda,
    num processo à parte, o test_atalhos.py seguido de um que importa a tela na
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
