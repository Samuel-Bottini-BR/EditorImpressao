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
