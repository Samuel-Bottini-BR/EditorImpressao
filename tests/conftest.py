"""Configuracao comum de TODOS os testes: a pasta de dados do programa e de mentira.

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

PASTA_DE_DADOS_DOS_TESTES = (Path(__file__).resolve().parent.parent / "saida_teste"
                             / "pytest_dados")
_ESTA_RODADA: Path | None = None


def pytest_configure(config) -> None:
    """Antes de coletar os testes: LOCALAPPDATA vai para a pasta desta rodada."""
    global _ESTA_RODADA
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
