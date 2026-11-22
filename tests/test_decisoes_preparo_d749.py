"""Provas da D-749 (Samuel, 17/11/2026), sem tocar o Windows.

Pergunta: "se o Kaique clicar "Sim" e a preparação der erro no meio, a pergunta volta na próxima abertura?
Sugiro que sim." Resposta: "Sim".

Na pratica: se o "Sim" da pergunta do Windows da primeira abertura (D-733) vem com a preparacao do computador
(--preparar-o-computador) parada no meio ou com erro, a preparacao conta como NAO feita: a pergunta volta na
proxima abertura, como depois de um "Nao" (D-741), e o programa nunca fica achando que esta preparado.

Teste de reversao: no codigo de antes (5a407a6f), qualquer "Sim" gravava "preparado" (deu certo ou nao), e o
--preparar-o-computador devolvia 0 mesmo com o Visual C++ ou o Inno falhando: as provas abaixo falham la.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import atualizacao
from core import testes_a_distancia as td

POWERSHELL = shutil.which("powershell")


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (as Configuracoes nascem limpas)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


# Desde os 4 consertos do atualizador (D-825, Samuel 21/11/2026: "ok"), os tres testes abaixo cobram a MESMA D-749
# pelo caminho novo: a pergunta pela peca unica do Windows e o "preparado" lido do Windows (o ajudante, a tarefa
# desfazer, o Visual C++, a instalacao antiga), sem o arquivo preparo.txt. O Windows de mentira e o de
# tests/test_atualizador_4.py.

import configuracoes  # noqa: E402
from tests.test_atualizador_4 import WindowsDeMentira  # noqa: E402


@pytest.fixture
def windows_de_mentira(tmp_path, monkeypatch):
    """O Windows de mentira do atualizador (cada pergunta: "sim", salvo `respostas`)."""
    return WindowsDeMentira().instalar(monkeypatch, tmp_path)


@pytest.mark.parametrize("como_parou", ["meio", "falhou"])
def test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta(windows_de_mentira, como_parou):
    """D-749: "Sim" + preparacao que parou no meio (ou deu erro) -> a pergunta volta na proxima abertura;
    "Sim" + preparacao que deu certo -> nunca mais. Antes (4a775ba8): o pedido antigo dava "Sim" e o preparo.txt
    decidia; com o "Nao" lido como 0, a anotacao de fora valia como feito."""
    windows_de_mentira.respostas = [como_parou, "sim"]
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True), "parou no meio e o programa achou que estava pronto"
    assert atualizacao.falta_a_pergunta_do_windows()
    assert "não ficou preparado" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=False) == []   # a proxima abertura: pergunta, da certo
    assert not atualizacao.falta_a_pergunta_do_windows()
    assert len(windows_de_mentira.pedidos) == 2


def test_d749_uma_anotacao_velha_nao_conta(windows_de_mentira):
    """D-749: so vale o que o Windows mostra agora. Uma anotacao velha de "preparado" (o preparo.txt com "0" e a marca
    antiga nas Configuracoes, de uma versao de antes) nao conta: sem o ajudante no Windows, falta."""
    arquivo = atualizacao.pasta_do_estado() / "preparo.txt"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("aaaa 0", encoding="ascii")
    configuracoes.escrever("atualizacao_computador_preparado", True)
    assert atualizacao.falta_a_pergunta_do_windows()
    assert any("ajudante" in f for f in atualizacao.o_que_falta_no_computador())


class _Gerente:
    def get_is_portable(self):
        return False


def test_d749_o_modo_preparar_devolve_erro_quando_algo_falha_no_meio():
    """D-749: o --preparar-o-computador so devolve 0 se tudo deu certo. Falha no codigo de antes: com o
    Visual C++ ou o Inno falhando ele devolvia 0, e um erro inesperado escapava sem codigo."""
    def quebra(_g):
        raise OSError("disco cheio")

    assert atualizacao.preparar_como_administrador(_Gerente(), criar=lambda: True, preparar=lambda g: True) == 0
    assert atualizacao.preparar_como_administrador(_Gerente(), criar=lambda: True, preparar=lambda g: False) == 1
    assert atualizacao.preparar_como_administrador(_Gerente(), criar=lambda: False, preparar=lambda g: True) == 1
    assert atualizacao.preparar_como_administrador(_Gerente(), criar=lambda: True, preparar=quebra) == 1
    assert "erro no meio" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


def test_d749_visual_c_ou_inno_que_falham_contam_como_erro(tmp_path, monkeypatch):
    """D-749: o Visual C++ que nao instalou e o Inno que nao saiu fazem a preparacao contar como nao feita;
    o Inno que nao se tira de proposito (caminho estranho) nao conta como erro (perguntar de novo nao mudaria nada)."""
    pasta = tmp_path / "programa"
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA).mkdir(parents=True)
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ")
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_VERSAO).write_text("14.44.1",
                                                                                               encoding="utf-8")
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: (1603, "")) is False
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: (0, "")) is True
    antiga = {"pasta": str(tmp_path / "antiga"), "desinstalador": str(tmp_path / "antiga" / "unins000.exe")}
    monkeypatch.setattr(atualizacao, "comando_para_tirar_o_inno", lambda a, p: ["unins000.exe", "/SILENT"])
    assert atualizacao.tirar_instalacao_antiga(pasta, achar=lambda: antiga, rodar=lambda c, t: (5, "")) is False
    assert atualizacao.tirar_instalacao_antiga(pasta, achar=lambda: antiga, rodar=lambda c, t: (0, "")) is True
    monkeypatch.setattr(atualizacao, "comando_para_tirar_o_inno", lambda a, p: None)
    assert atualizacao.tirar_instalacao_antiga(pasta, achar=lambda: antiga, rodar=lambda c, t: (5, "")) is True
    assert atualizacao.tirar_instalacao_antiga(pasta, achar=lambda: None) is True
    monkeypatch.setattr(atualizacao, "pasta_do_programa", lambda: pasta)
    monkeypatch.setattr(atualizacao, "e_portatil", lambda g=None: False)
    monkeypatch.setattr(atualizacao, "instalar_visual_c_se_faltar", lambda p: False)
    monkeypatch.setattr(atualizacao, "tirar_instalacao_antiga", lambda p: True)
    assert atualizacao.preparar_o_computador(_Gerente()) is False


@pytest.mark.skipif(sys.platform != "win32" or not POWERSHELL, reason="o passo e PowerShell")
@pytest.mark.parametrize("fim, esperado", [("[pscustomobject]@{ ExitCode = 0 }", "certo"),
                                           ("[pscustomobject]@{ ExitCode = 1 }", "falhou"),
                                           ("throw 'o exe sumiu'", "falhou"),
                                           ("$null", "falhou")])
def test_d749_o_passo_anota_como_o_preparo_terminou(tmp_path, fim, esperado):
    """D-749: o passo de verdade (o script do PowerShell, com o Start-Process trocado por um de mentira) termina bem
    SO quando o --preparar-o-computador terminou com 0; codigo 1, o .exe que nao abre ou nada devolvido fazem o passo
    falhar, e a peca unica devolve "falhou" (a preparacao conta como nao feita). Desde a D-825 nada e anotado num
    arquivo: quem le o desfecho e a peca. Antes (4a775ba8) o passo engolia o erro (try/catch) e anotava no preparo.txt."""
    exe = Path(r"D:\nao-existe\EditorImpressao.exe")
    passo = atualizacao.passo_de_preparar_o_computador(exe)
    texto = passo.dados["texto"]
    assert "C:\\" not in texto, "tudo na pasta de mentira"
    script = tmp_path / "passo.ps1"
    script.write_text("\n".join(["$ErrorActionPreference = 'Stop'",
                                 "function Start-Process { " + fim + " }",
                                 texto, "Write-Output 'SEGUIU'"]), encoding="utf-8-sig")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
                            str(script)], capture_output=True, text=True, timeout=120)
    if esperado == "certo":
        assert feito.returncode == 0 and "SEGUIU" in feito.stdout, feito.stderr
    else:
        assert feito.returncode != 0 and "SEGUIU" not in feito.stdout, "o preparo falhou e o passo seguiu"
    assert not (atualizacao.pasta_do_estado() / "preparo.txt").exists(), "nada anotado num arquivo"
