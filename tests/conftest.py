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
nova dentro de saida_teste\\ (ignorada pelo git), so desta rodada, apagada na
saida do processo - e NUNCA volta ao valor verdadeiro, nem no fim da sessao
(conserto de 08/10/2026: o que ainda escrevia depois do fim ia para o
erros.log do Samuel; ver pytest_unconfigure). Todo o resto le a variavel na hora (historico.pasta_de_dados), entao
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

import atexit
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
    # Registrada PRIMEIRO, roda por ULTIMO na saida (o atexit roda do ultimo
    # registrado para o primeiro): depois das rotinas de saida dos testes.
    atexit.register(_apagar_a_pasta_da_rodada)


def pytest_unconfigure(config) -> None:
    """No fim da sessao: LOCALAPPDATA NAO volta ao valor verdadeiro.

    Conserto de 08/10/2026 (Lista de bugs): antes a variavel voltava aqui, e
    o que ainda escrevia depois - o fio que le o servidor de paginas quando
    ele fecha ("o servidor de paginas caiu"), o fio das miniaturas ("Signal
    source has been deleted"), rotinas de saida do Python (atexit) - ia para
    o erros.log de verdade do Samuel (31 linhas numa rodada de 08/10). Voltar
    a variavel nao servia para nada: ela so vale dentro deste processo, que
    esta terminando (o terminal de quem chamou o pytest nao muda).

    A pasta desta rodada e apagada so na saida do processo
    (_apagar_a_pasta_da_rodada, registrada no atexit em pytest_configure:
    roda DEPOIS dos fios normais terminarem e das rotinas de saida
    registradas pelos testes). Se um fio "daemon" ainda escrever depois
    disso, a pasta renasce dentro de saida_teste\\ (ignorada pelo git), nunca
    na pasta do Samuel. Teste: tests/test_dados_isolados_ate_o_fim.py.
    Arriscado: voltar a devolver a variavel aqui, ou apagar a pasta aqui.
    """


def _apagar_a_pasta_da_rodada() -> None:
    """Na saida do processo: apaga a pasta desta rodada (criada em
    pytest_configure) e a pasta-mae, se ficou vazia. Nunca levanta erro."""
    if _ESTA_RODADA is not None:
        shutil.rmtree(_ESTA_RODADA, ignore_errors=True)
        try:
            PASTA_DE_DADOS_DOS_TESTES.rmdir()          # so se ficou vazia
        except OSError:
            pass


@pytest.fixture
def livro_novo_divide(monkeypatch):
    """O livro novo abre com "Dividir folhas ao meio" marcada, como era ate o
    item 2.1. Desde a decisao G2 (a) do Samuel (05/10/2026) o livro novo NAO
    divide; os testes marcados com esta fixture foram escritos com o livro
    deitado dividido (6 paginas) e mudam a opcao a partir dali - o cenario
    deles continua o mesmo, so o ponto de partida e posto a mao."""
    from dataclasses import dataclass

    import ui.janela_principal as jp
    from modelos import Projeto

    @dataclass
    class ProjetoQueDivide(Projeto):
        dividir_folhas: bool = True

    monkeypatch.setattr(jp, "Projeto", ProjetoQueDivide)
