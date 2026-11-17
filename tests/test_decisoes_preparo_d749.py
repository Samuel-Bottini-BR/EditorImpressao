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


class WindowsQuePrepara(td.Executor):
    """A pergunta do Windows de mentira: o Kaique diz "Sim", e o passo de preparar anota no arquivo o que o
    --preparar-o-computador de verdade anotaria (`saidas`, uma por abertura: "0", "1" ou "comecou" = parou no
    meio). Nada do Windows e tocado."""

    def __init__(self, saidas: list[str]) -> None:
        self.saidas = list(saidas)
        self.chamadas = 0

    def aplicar(self, passos, senha):
        self.chamadas += 1
        saida = self.saidas.pop(0)
        preparo = [p for p in passos if atualizacao.ARG_PREPARAR in p.comando][0]
        achada = re.search(r"'([0-9a-f]{32}) comecou'", preparo.comando)
        if achada:
            arquivo = atualizacao.pasta_do_estado() / "preparo.txt"
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text(f"{achada.group(1)} {saida}", encoding="ascii")
        return td.Resultado(True, passos=passos)


@pytest.mark.parametrize("como_parou", ["comecou", "1"])
def test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta(monkeypatch, como_parou):
    """D-749: "Sim" + preparacao que parou no meio (ou deu erro) -> a pergunta volta na proxima abertura;
    "Sim" + preparacao que deu certo -> nunca mais. Falha no codigo de antes: o primeiro "Sim" ja gravava."""
    windows = WindowsQuePrepara([como_parou, "0"])
    monkeypatch.setattr(td, "_executor", windows)
    atualizacao.preparar_na_primeira_abertura("")
    assert atualizacao.falta_a_pergunta_do_windows(), "a preparação parou no meio e o programa achou que estava pronto"
    assert "D-749" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    atualizacao.preparar_na_primeira_abertura("")      # a proxima abertura: pergunta de novo, agora da certo
    assert not atualizacao.falta_a_pergunta_do_windows()
    assert windows.chamadas == 2


def test_d749_uma_anotacao_velha_nao_conta():
    """D-749: so vale o que o passo anotou NESTA pergunta (a marca dela); um "0" de outra vez nao conta."""
    arquivo = atualizacao.arquivo_do_preparo()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("aaaa 0", encoding="ascii")
    assert not atualizacao.preparo_deu_certo("bbbb", td.Resultado(False))
    arquivo.write_text("bbbb comecou", encoding="ascii")
    assert not atualizacao.preparo_deu_certo("bbbb", td.Resultado(True)), "parou no meio: não feito"
    arquivo.write_text("bbbb 0", encoding="ascii")
    assert atualizacao.preparo_deu_certo("bbbb", td.Resultado(True))


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
@pytest.mark.parametrize("fim, esperado", [("[pscustomobject]@{ ExitCode = 0 }", "0"),
                                           ("[pscustomobject]@{ ExitCode = 1 }", "1"),
                                           ("throw 'o exe sumiu'", "comecou")])
def test_d749_o_passo_anota_como_o_preparo_terminou(tmp_path, fim, esperado):
    """D-749: o passo de verdade (PowerShell), com o Start-Process trocado por um de mentira, anota "<marca>
    comecou" antes e "<marca> <codigo>" depois; se o preparo nem terminou, fica o "comecou" (= nao feito).
    E continua sem parar a pergunta (try/catch), como na D-733."""
    exe = Path(r"D:\nao-existe\EditorImpressao.exe")
    passo = atualizacao.passo_de_preparar_o_computador(exe, marca="abc123")
    assert "C:\\" not in passo.comando, "tudo na pasta de mentira"
    script = tmp_path / "passo.ps1"
    script.write_text("\n".join(["$ErrorActionPreference = 'Stop'",
                                 "function Start-Process { " + fim + " }",
                                 passo.comando, "Write-Output 'SEGUIU'"]), encoding="utf-8-sig")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
                            str(script)], capture_output=True, text=True, timeout=120)
    assert "SEGUIU" in feito.stdout, feito.stderr
    anotado = atualizacao.arquivo_do_preparo().read_text(encoding="utf-8-sig").strip()
    assert anotado == f"abc123 {esperado}"
    assert atualizacao.preparo_deu_certo("abc123", td.Resultado(True)) is (esperado == "0")
