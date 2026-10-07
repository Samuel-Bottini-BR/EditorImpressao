"""Os scripts de teste da raiz (teste_*.py) nunca gravam na pasta de dados
de verdade (regra de 29/09/2026; Lista de bugs de 06/10/2026: o
teste_velocidade gravava no erros.log do Samuel). Ver
pasta_de_dados_dos_scripts.py."""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

import pasta_de_dados_dos_scripts as pds

RAIZ = Path(__file__).resolve().parent.parent

# O que, importado por um script, pode gravar na pasta de dados: a janela
# (projetos, historico, configuracoes, erros.log), as configuracoes, e o
# processamento (o detector de gravura e o servidor de paginas anotam no
# erros.log quando falham).
_GRAVAM = ("ui", "projetos", "historico", "registro", "configuracoes", "main",
           "core.pipeline", "core.detectar_regioes", "core.paginas_em_outro_processo")

# Os que ja tinham pasta propria do seu jeito.
_COM_JEITO_PROPRIO = {
    "teste_botoes.py": 'os.environ["LOCALAPPDATA"] = str(_DADOS_DO_TESTE)',
    "teste_velocidade.py": "dados_de_verdade = pasta_de_dados_propria(temporaria)",
}


def _importa_algo_que_grava(caminho: Path) -> bool:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        nomes = []
        if isinstance(no, ast.Import):
            nomes = [a.name for a in no.names]
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            nomes = [no.module]
        for nome in nomes:
            if any(nome == g or nome.startswith(g + ".") for g in _GRAVAM):
                return True
    return False


def _scripts_que_gravam() -> list[Path]:
    return [c for c in sorted(RAIZ.glob("teste_*.py")) if _importa_algo_que_grava(c)]


def test_ha_scripts_para_conferir():
    nomes = {c.name for c in _scripts_que_gravam()}
    assert {"teste_interface.py", "teste_velocidade.py", "teste_pipeline.py"} <= nomes


@pytest.mark.parametrize("script", _scripts_que_gravam(), ids=lambda c: c.name)
def test_todo_script_que_pode_gravar_usa_pasta_de_dados_propria(script):
    texto = script.read_text(encoding="utf-8")
    if script.name in _COM_JEITO_PROPRIO:
        assert _COM_JEITO_PROPRIO[script.name] in texto
        return
    chamada = f'isolar_pasta_de_dados("{script.stem}")'
    assert chamada in texto, f"{script.name} grava na pasta de dados de verdade"
    # no bloco principal, antes do main()
    bloco = texto.split('if __name__ == "__main__":', 1)[1]
    assert bloco.index(chamada) < bloco.index("main(")


def test_isolar_troca_a_pasta_e_guarda_a_de_verdade(tmp_path, monkeypatch):
    import historico
    import registro

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "verdade"))
    monkeypatch.delenv("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL", raising=False)
    anotadas = []
    monkeypatch.setattr(pds.atexit, "register", lambda f, *a: anotadas.append((f, a)))

    pasta = pds.isolar_pasta_de_dados("teste_x", raiz=tmp_path / "scripts")

    assert pasta.is_dir() and pasta.parent == tmp_path / "scripts"
    assert pasta.name.startswith("teste_x-")
    assert os.environ["LOCALAPPDATA"] == str(pasta)
    assert os.environ["EDITOR_IMPRESSAO_LOCALAPPDATA_REAL"] == str(tmp_path / "verdade")
    assert historico.pasta_de_dados().is_relative_to(pasta)
    registro.registrar_erro("teste", "vai para a pasta propria")
    assert registro.caminho_do_log().is_relative_to(pasta)
    assert not (tmp_path / "verdade").exists()
    assert anotadas == [(pds.limpar_ao_terminar, (pasta,))], "limpa ao terminar"


def test_ao_terminar_apaga_a_pasta_sem_erros(tmp_path):
    pasta = tmp_path / "rodada"
    (pasta / "EditorImpressao" / "projetos").mkdir(parents=True)
    assert pds.limpar_ao_terminar(pasta) is True
    assert not pasta.exists()


def test_ao_terminar_guarda_a_pasta_com_erros_log(tmp_path, capsys):
    pasta = tmp_path / "rodada"
    log = pasta / "EditorImpressao" / "erros.log"
    log.parent.mkdir(parents=True)
    log.write_text("algo deu errado", encoding="utf-8")
    assert pds.limpar_ao_terminar(pasta) is False
    assert log.read_text(encoding="utf-8") == "algo deu errado"
    assert str(log) in capsys.readouterr().out
