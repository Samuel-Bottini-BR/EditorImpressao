"""Provas da volta 4 do atualizador (D-828, Samuel 22/11/2026: "foi eu, pode consertar essas coisas").

Os 3 defeitos da prova a vista de 22/11 (Lista de bugs de 22/11), um por conserto:
1. "Reiniciar agora" nao troca: o Velopack nao conseguiu renomear `current` ("O arquivo ja esta sendo usado por outro
   processo"), porque o PowerShell da troca nasceu com `current` como pasta de trabalho; e abrir o programa pelo atalho
   no meio da troca a estragava.
2. A pergunta do Windows da primeira abertura piscava na barra de tarefas (a janela do programa nao estava na frente).
3. A segunda preparacao falhava com a pasta dos testes a distancia trancada pelo `icacls ... /T`.

Plano, causas e experimentos: relatorios/atualizador-4/ONDE-PAREI.md (secao "Volta 4") e anexos/volta4-*.
Cada teste diz o defeito que pega e falha no codigo de antes do seu conserto (a prova de reversao fica nos anexos).

O QUE TOCA O WINDOWS DE VERDADE (D-767): so o que nao pede licenca nem abre janela: lancar um PowerShell escondido pela
peca, renomear uma pasta do teste, criar e ler uma marca (mutex) com nome proprio do teste, ler a lista de processos.
Nada pergunta "Deseja permitir...?" e nada aparece na tela.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

import atualizacao
from core import windows

RAIZ = Path(__file__).resolve().parent.parent
so_no_windows = pytest.mark.skipif(sys.platform != "win32", reason="so no Windows")


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (o estado, o registro e as pastas de troca da peca nascem limpos)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


def _registro() -> str:
    """O registro da atualizacao (o de mentira, desta pasta do teste)."""
    caminho = atualizacao.caminho_do_registro()
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1, parte a: o lancar solto nao prende a pasta de quem lancou
# ---------------------------------------------------------------------------------------------------------------------

_QUEM_LANCA = textwrap.dedent('''
    """Faz o papel do programa aberto pelo Velopack: a pasta de trabalho e `current`; lanca solto e sai dela."""
    import os, sys, time
    sys.path.insert(0, sys.argv[1])
    current = sys.argv[2]
    os.chdir(current)
    from core import windows
    r = windows.lancar_powershell_solto("Start-Sleep -Seconds 12")
    os.chdir(os.path.dirname(current))
    time.sleep(1.5)
    try:
        os.rename(current, current + "-velha")
        print("RENOMEOU" if r.deu_certo else "NAO LANCOU " + r.motivo)
    except OSError as erro:
        print("PRESA", erro.winerror)
''')


@so_no_windows
def test_conserto1_o_lancado_solto_nao_prende_a_pasta_de_trabalho_de_quem_lancou(tmp_path):
    """Defeito da prova a vista de 22/11 ("Reiniciar agora" ainda nao troca a versao): o PowerShell da troca nascia
    com a pasta de trabalho do programa (`current`) e o Velopack nao conseguia renomea-la (erro 32). Aqui, de verdade
    no Windows: um processo com a pasta de trabalho em `current` lanca solto pela peca e sai da pasta; a pasta tem de
    poder ser renomeada enquanto o lancado ainda roda. No codigo de antes: "PRESA 32"."""
    current = tmp_path / "current"
    current.mkdir()
    script = tmp_path / "quem_lanca.py"
    script.write_text(_QUEM_LANCA, encoding="utf-8")
    feito = subprocess.run([sys.executable, str(script), str(RAIZ), str(current)], capture_output=True, text=True,
                           timeout=90, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert feito.stdout.strip() == "RENOMEOU", (feito.stdout, feito.stderr)


def test_conserto1_o_programa_reaberto_pela_troca_nasce_na_pasta_dele():
    """Volta 4: o script da troca nasce na pasta do sistema; antes de reabrir o programa ele volta para a pasta do
    programa (o Start-Process abre na "localizacao" do PowerShell, volta4-exp3/exp4), para o programa reaberto ter a
    mesma pasta de trabalho de quando o Velopack o abre. A troca, a volta e a reabertura ficam iguais (D-742)."""
    exe = Path(r"C:\Arquivos de Programas\EditorImpressaoPrograma\current\EditorImpressao.exe")
    for janelinha in (False, True):
        script = atualizacao.script_de_trocar_e_reabrir(exe, 4321, Path("C:/x/estado.json"), janelinha=janelinha)
        linhas = script.split("\n")
        reabrir = next(i for i, linha in enumerate(linhas) if linha.startswith("Start-Process"))
        assert linhas[reabrir - 1] == f"Set-Location -LiteralPath '{exe.parent}'"


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1, parte b: o ajudante so troca com nada do programa rodando de `current`, conferido no Windows
# ---------------------------------------------------------------------------------------------------------------------

def _programa_de_verdade_numa_pasta(pasta: Path) -> subprocess.Popen:
    """Copia o ping.exe do Windows para `pasta` e o roda dali (uns segundos, sem janela): um processo de verdade cujo
    programa esta dentro da pasta, como o programa do Kaique em `current`."""
    pasta.mkdir(parents=True, exist_ok=True)
    copia = pasta / "EditorImpressao.exe"
    copia.write_bytes((Path(os.environ["SystemRoot"]) / "System32" / "PING.EXE").read_bytes())
    return subprocess.Popen([str(copia), "-n", "30", "127.0.0.1"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


@so_no_windows
def test_conserto1_a_peca_le_no_windows_o_que_roda_de_uma_pasta(tmp_path):
    """Volta 4 (D-828: "garante que o programa terminou de fechar antes de a troca comecar", conferido de verdade): a
    peca le na lista de processos do Windows o que roda de dentro de uma pasta, pelo caminho do programa; nada de fora
    da pasta conta; o processo que terminou sai da lista."""
    current = tmp_path / "EditorImpressaoPrograma" / "current"
    processo = _programa_de_verdade_numa_pasta(current)
    try:
        time.sleep(0.5)
        achados = windows.programas_rodando_de(current)
        assert [pid for pid, _ in achados] == [processo.pid]
        assert Path(achados[0][1]).name == "EditorImpressao.exe"
        assert windows.programas_rodando_de(tmp_path / "outra") == [], "uma pasta sem nada rodando"
    finally:
        processo.kill()
        processo.wait(10)
    assert windows.programas_rodando_de(current) == []


@pytest.fixture
def instalado_de_mentira(tmp_path, monkeypatch):
    """O programa "instalado" numa pasta do teste: a pasta do programa e <tmp>/EditorImpressaoPrograma/current; a
    marca da janela nao existe; a espera curta (o mesmo laco, menos tempo)."""
    current = tmp_path / "EditorImpressaoPrograma" / "current"
    current.mkdir(parents=True)
    monkeypatch.setattr(atualizacao, "pasta_do_programa", lambda: current)
    monkeypatch.setattr(atualizacao, "instalado_pelo_velopack", lambda: True)
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: False)
    monkeypatch.setattr(atualizacao, "ESPERA_O_PROGRAMA_FECHAR_S", 1.5, raising=False)
    return current


@so_no_windows
def test_conserto1_com_o_programa_ainda_rodando_de_current_o_ajudante_nao_troca(instalado_de_mentira, tmp_path):
    """Defeito da prova de 22/11: a troca comecou com algo ainda segurando `current`, e o Velopack desistiu (e a versao
    ficou como "ja falhou"). Agora o ajudante, antes de pedir a troca, le no Windows o que roda de `current`: com o
    programa ainda rodando (aqui um processo de verdade dali), nao troca (fica "pendente") e o registro diz o que roda.
    No codigo de antes: so a marca da janela contava, e trocava ("aplicando")."""
    from tests.test_decisoes_atualizacao import PUBLICA, GerenteFalso, _servidor

    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    processo = _programa_de_verdade_numa_pasta(instalado_de_mentira)
    try:
        time.sleep(0.5)
        resultado = atualizacao.procurar_e_preparar(gerente, fonte, atualizacao.ha_programa_aberto,
                                                    chave_publica=PUBLICA, motor_no_lugar=lambda: True)
    finally:
        processo.kill()
        processo.wait(10)
    assert resultado == "pendente" and gerente.trocou == []
    assert "ainda roda do programa (EditorImpressao.exe" in _registro()


def test_conserto1_o_que_termina_dentro_da_espera_deixa_trocar(instalado_de_mentira):
    """O programa terminando de fechar (some da lista dentro da espera): troca, sem esperar a mais; o registro diz que
    esperou."""
    vezes = iter([["EditorImpressao.exe (7)"], ["EditorImpressao.exe (7)"], []])
    assert atualizacao.ha_programa_aberto(roda=lambda: next(vezes), dormir=lambda s: None) is False
    assert "espero até" in _registro() and "terminou; pode trocar" in _registro()


@pytest.mark.parametrize("lido", [None, ["EditorImpressao.exe (7)"]])
def test_conserto1_lista_que_nao_deu_para_ler_ou_programa_que_nao_fecha_nao_troca(instalado_de_mentira, lido):
    """"Nada da como feito o que nao conferiu" (CLAUDE.md §11.12): a lista que o Windows nao deu, ou o programa que nao
    termina dentro da espera, contam como aberto."""
    assert atualizacao.ha_programa_aberto(roda=lambda: lido, dormir=lambda s: time.sleep(0.05)) is True
    assert "não troco agora" in _registro()


def test_conserto1_com_a_marca_da_janela_nao_espera_e_pelo_codigo_so_a_marca(monkeypatch):
    """A janela aberta (a marca) conta como aberto na hora, sem ler a lista; pelo codigo (nao instalado) so a marca,
    como antes."""
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: True)
    assert atualizacao.ha_programa_aberto(roda=lambda: pytest.fail("leu a lista"), instalado=lambda: True) is True
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: False)
    assert atualizacao.ha_programa_aberto(roda=lambda: pytest.fail("leu a lista"), instalado=lambda: False) is False


def test_conserto1_o_proprio_ajudante_nao_conta(instalado_de_mentira):
    """O ajudante roda de `current` (e ele que pede a troca e sai): ele mesmo nao entra na conta."""
    assert atualizacao.o_que_roda_do_programa(lambda pasta: [(os.getpid(), str(pasta / "EditorImpressao.exe"))]) == []
    assert atualizacao.o_que_roda_do_programa(lambda pasta: None) is None
