"""Pasta de dados propria para os scripts de teste da raiz (teste_*.py).

Regra de 29/09/2026 (Lista de bugs): teste nunca grava na pasta de dados de
verdade do Samuel, %LOCALAPPDATA%\\EditorImpressao (erros.log, projetos,
historico dos livros abertos, configuracoes). O pytest ja cuida disso
(tests/conftest.py); os scripts da raiz nao passam pelo conftest. Achado em
06/10/2026: o teste_velocidade gravava no erros.log de verdade (ele tem o
jeito dele, que funciona tambem empacotado: teste_velocidade.
pasta_de_dados_propria). Os outros scripts que abrem a janela do programa
(teste_interface, teste_medidor, teste_ampliar) criavam projetos na lista de
verdade; os que rodam o processamento (core.pipeline, core.detectar_regioes)
anotam no erros.log quando o detector de gravura ou o servidor de paginas
falha.

Como funciona: o mesmo jeito do conftest - trocar a variavel LOCALAPPDATA,
que o programa le na hora de gravar (historico.pasta_de_dados). Os processos
filhos herdam a troca. A pasta e uma por rodada, em
saida_teste\\dados_dos_scripts\\<script>-<data e hora>-<processo> (o
saida_teste e ignorado pelo git), e e apagada quando o script termina - a
nao ser que o programa tenha anotado algo no erros.log: ai ela fica, e o
caminho e escrito no terminal, para quem for ver o que deu errado.

Uso, no bloco `if __name__ == "__main__":` do script, antes do main():

    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados
    isolar_pasta_de_dados("teste_interface")

Seguro mudar: onde fica a pasta. Arriscado: chamar depois de o script abrir a
janela ou o servidor de paginas (ja teriam gravado, ou nascido, com a pasta
de verdade); apagar a pasta com erros.log dentro (o detalhe se perderia).
"""

from __future__ import annotations

import atexit
import os
import shutil
import time
from pathlib import Path

PASTA_DOS_SCRIPTS = Path(__file__).resolve().parent / "saida_teste" / "dados_dos_scripts"


def isolar_pasta_de_dados(nome: str, raiz: Path | None = None) -> Path:
    """Troca LOCALAPPDATA por uma pasta so desta rodada e devolve a pasta.

    O valor de verdade fica em EDITOR_IMPRESSAO_LOCALAPPDATA_REAL (o mesmo
    nome do tests/conftest.py), para quem precisar. `raiz`: onde criar (os
    testes passam uma pasta temporaria); de fabrica, PASTA_DOS_SCRIPTS.
    """
    if os.environ.get("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL") is None:
        os.environ["EDITOR_IMPRESSAO_LOCALAPPDATA_REAL"] = os.environ.get("LOCALAPPDATA", "")
    base = Path(raiz) if raiz is not None else PASTA_DOS_SCRIPTS
    pasta = base / f"{nome}-{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    pasta.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(pasta)
    atexit.register(limpar_ao_terminar, pasta)
    return pasta


def limpar_ao_terminar(pasta: Path) -> bool:
    """Apaga a pasta desta rodada (criada por isolar_pasta_de_dados), a nao
    ser que o programa tenha anotado algo no erros.log: ai ela fica e o
    caminho do erros.log e escrito no terminal. Devolve True se apagou.
    Nunca levanta (roda na saida do script)."""
    log = Path(pasta) / "EditorImpressao" / "erros.log"
    try:
        if log.is_file() and log.stat().st_size > 0:
            print(f"O programa anotou erros técnicos durante o teste: {log}")
            return False
        shutil.rmtree(pasta, ignore_errors=True)
        return True
    except Exception:  # noqa: BLE001 - na saida do script, nada pode quebrar
        return False
