"""Configuracao comum de TODOS os testes: pasta de dados de mentira e nenhuma
janela na tela.

PARTE 1 - SEM JANELA NA TELA (pedido da gerente, 30/09/2026)
------------------------------------------------------------
Rodadas de pytest abriam janelas na tela do Samuel (uma caixa "Tirar da
lista?" ficou minutos esperando clique, em 30/09). Aqui, antes de qualquer
teste:
  - QT_QPA_PLATFORM=offscreen: o Qt desenha tudo na memoria, nada aparece.
    Vale tambem para os processos filhos (herdam o ambiente). Quem precisar
    ver as janelas (depurar um teste de tela) roda com
    EDITOR_TESTES_COM_TELA=1 - de proposito, nunca por padrao.
  - Caixas modais nunca ficam esperando clique: QDialog.exec,
    QMessageBox.exec e QMenu.exec ganham um vigia que fecha a caixa depois
    de LIMITE_DA_CAIXA_S segundos e faz o teste FALHAR, dizendo qual caixa
    ficou sem resposta (em vez de travar a bateria para sempre). Teste que
    responde a caixa sozinho (QTimer, clique) antes disso nao e afetado.
  - As funcoes prontas do Qt que abrem caixa por dentro do C++ (sem passar
    pelo exec do Python) - QMessageBox.question/warning/..., QInputDialog.
    getText/getInt/..., QFileDialog.getOpenFileName/... - levantam erro
    na hora se um teste as chamar sem troca-las por uma resposta
    (monkeypatch). A caixa de arquivo do Windows ("nativa") apareceria na
    tela mesmo com o offscreen.
Nenhum teste precisa de fontes de verdade: a bateria inteira ja passava com
o offscreen (conferido em 30/09, 1207 testes).

PARTE 2 - PASTA DE DADOS DE MENTIRA
-----------------------------------

O programa guarda o que e dele em %LOCALAPPDATA%\\EditorImpressao
(historico.pasta_de_dados): projetos, historico.json, configuracoes.json e o
erros.log (registro.caminho_do_log). Rodar os testes com a pasta de verdade
enchia a pasta de dados real do Samuel: o erros.log ganhava entradas de
teste a cada rodada (tests/test_folhear_pdf.py) e ja nasceram la pastas de
projeto de teste ("camadas", "comum", "fixture_gerado"...). Pedido da gerente
em 29/09/2026 (Lista de bugs, parecer do verificador, 2a rodada).

Aqui, antes de qualquer teste, LOCALAPPDATA passa a apontar para uma pasta
nova dentro de saida_teste\\ (ignorada pelo git), so desta rodada, apagada no
fim. Todo o resto le a variavel na hora (historico.pasta_de_dados), entao
nada precisa ser trocado modulo por modulo. Os testes que ja trocam a pasta
por conta propria (monkeypatch.setenv, ou pasta_dos_projetos trocada)
continuam funcionando: trocam por cima desta, e o monkeypatch devolve esta
no fim de cada teste.

O valor verdadeiro fica em EDITOR_IMPRESSAO_LOCALAPPDATA_REAL, para quem
precisar (nenhum teste precisa hoje; o Tesseract e procurado primeiro em
%ProgramFiles%). O APPDATA so e usado se LOCALAPPDATA nao existir, e fica.

Seguro mudar: onde fica a pasta de mentira. Arriscado: tirar isto (os testes
voltam a gravar na pasta real), ou trocar a variavel so dentro de uma fixture
que nao seja de sessao (import feito antes dela ja teria lido a pasta real -
hoje nenhum modulo guarda a pasta na importacao, mas nada garante).
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import pytest

# Quanto uma caixa modal pode ficar aberta num teste antes de ser fechada
# pelo vigia (e o teste falhar). Folgado para teste que responde a caixa com
# um QTimer; curto o bastante para a bateria nao ficar parada.
LIMITE_DA_CAIXA_S = 20.0

# Caixas que o vigia teve de fechar no teste da vez (ver _caixas_sem_resposta).
_CAIXAS_SEM_RESPOSTA: list[str] = []

PASTA_DE_DADOS_DOS_TESTES = (Path(__file__).resolve().parent.parent / "saida_teste"
                             / "pytest_dados")
_ESTA_RODADA: Path | None = None


def _sem_janela_na_tela() -> None:
    """Parte 1 do docstring: offscreen, vigia nas caixas modais e as funcoes
    prontas de caixa do Qt proibidas sem resposta."""
    if os.environ.get("EDITOR_TESTES_COM_TELA") != "1":
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import (
            QDialog, QFileDialog, QInputDialog, QMenu, QMessageBox)
    except ImportError:                  # sem PySide6, os testes de tela pulam sozinhos
        return

    def vigiar(classe) -> None:
        original = classe.exec

        def exec_vigiado(self, *args, **kwargs):
            def fechar_se_ainda_aberta() -> None:
                if self.isVisible():
                    titulo = self.windowTitle() if hasattr(self, "windowTitle") else ""
                    _CAIXAS_SEM_RESPOSTA.append(f"{type(self).__name__} '{titulo}'")
                    if hasattr(self, "reject"):
                        self.reject()
                    else:
                        self.close()

            vigia = QTimer(self)
            vigia.setSingleShot(True)
            vigia.timeout.connect(fechar_se_ainda_aberta)
            vigia.start(int(LIMITE_DA_CAIXA_S * 1000))
            return original(self, *args, **kwargs)

        exec_vigiado.__doc__ = f"{classe.__name__}.exec com vigia (tests/conftest.py)"
        classe.exec = exec_vigiado

    for classe in (QDialog, QMessageBox, QMenu):
        vigiar(classe)

    def proibida(nome: str):
        def chamada(*_args, **_kwargs):
            raise RuntimeError(
                f"{nome} abriu uma caixa num teste sem resposta. Troque-a por uma "
                "resposta fixa (monkeypatch) - ver tests/conftest.py.")
        return staticmethod(chamada)

    for classe, nomes in (
            (QMessageBox, ("question", "warning", "information", "critical", "about")),
            (QInputDialog, ("getText", "getInt", "getDouble", "getItem", "getMultiLineText")),
            (QFileDialog, ("getOpenFileName", "getOpenFileNames", "getSaveFileName",
                           "getExistingDirectory", "getOpenFileUrl", "getSaveFileUrl",
                           "getExistingDirectoryUrl"))):
        for nome in nomes:
            setattr(classe, nome, proibida(f"{classe.__name__}.{nome}"))


@pytest.fixture(autouse=True)
def _caixas_sem_resposta():
    """Falha o teste em que o vigia teve de fechar uma caixa modal."""
    _CAIXAS_SEM_RESPOSTA.clear()
    yield
    if _CAIXAS_SEM_RESPOSTA:
        caixas = ", ".join(_CAIXAS_SEM_RESPOSTA)
        _CAIXAS_SEM_RESPOSTA.clear()
        pytest.fail(f"caixa modal ficou sem resposta e foi fechada pelo vigia: {caixas}")


def pytest_configure(config) -> None:
    """Antes de coletar os testes: nenhuma janela na tela, e LOCALAPPDATA vai
    para a pasta desta rodada."""
    global _ESTA_RODADA
    _sem_janela_na_tela()
    if os.environ.get("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL") is None:
        os.environ["EDITOR_IMPRESSAO_LOCALAPPDATA_REAL"] = os.environ.get("LOCALAPPDATA", "")
    _ESTA_RODADA = PASTA_DE_DADOS_DOS_TESTES / f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    _ESTA_RODADA.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(_ESTA_RODADA)


def pytest_unconfigure(config) -> None:
    """No fim: a variavel volta, e a pasta desta rodada (criada aqui) e apagada."""
    real = os.environ.get("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL")
    if real:
        os.environ["LOCALAPPDATA"] = real
    if _ESTA_RODADA is not None:
        shutil.rmtree(_ESTA_RODADA, ignore_errors=True)
        try:
            PASTA_DE_DADOS_DOS_TESTES.rmdir()          # so se ficou vazia
        except OSError:
            pass
