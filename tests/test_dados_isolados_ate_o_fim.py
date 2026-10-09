"""Nenhum teste escreve na pasta de dados de verdade, nem depois do fim da sessão.

O defeito (achado em 07 e 08/10/2026): o erros.log de verdade do Samuel
(%LOCALAPPDATA%\\EditorImpressao\\erros.log) ganhava entradas de teste ("o
servidor de paginas caiu", "miniaturas: Signal source has been deleted"),
vindas das worktrees. O tests/conftest.py trocava LOCALAPPDATA por uma pasta
da rodada, mas no pytest_unconfigure devolvia o valor verdadeiro - e o que
ainda escrevia depois disso (o fio que lê o servidor de páginas quando ele
fecha, o fio das miniaturas, rotinas de saída do Python) ia parar na pasta
do Samuel.

Como se prova sem tocar na pasta do Samuel: um pytest à parte, com o
conftest do projeto e um LOCALAPPDATA "verdadeiro" de mentira (uma pasta
temporária), roda um teste que deixa uma anotação para DEPOIS do fim da
sessão (atexit: roda depois do pytest_unconfigure, como os fios que ainda
estão vivos). A pasta "verdadeira" tem de continuar sem erros.log.
Teste de máquina.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

TESTE_QUE_ESCREVE_DEPOIS = textwrap.dedent('''
    import atexit
    import threading


    def test_deixa_anotacoes_para_depois_do_fim():
        from registro import registrar_erro

        # como o fio que le o servidor de paginas: escreve quando o programa
        # ja esta fechando, depois de o pytest terminar
        atexit.register(registrar_erro, "teste", "escrito depois do fim da sessao (atexit)")

        # como o fio das miniaturas: um fio vivo que escreve um pouco depois
        def tarde():
            import time
            time.sleep(1.0)
            registrar_erro("teste", "escrito depois do fim da sessao (fio)")
        threading.Thread(target=tarde, daemon=False).start()
''')


def test_nada_vai_para_a_pasta_de_dados_verdadeira_nem_no_fim(tmp_path):
    verdadeira = tmp_path / "localappdata-verdadeira"
    verdadeira.mkdir()
    arquivo = tmp_path / "caso" / "test_escreve_depois.py"
    arquivo.parent.mkdir()
    arquivo.write_text(TESTE_QUE_ESCREVE_DEPOIS, encoding="utf-8")

    ambiente = dict(os.environ)
    ambiente["LOCALAPPDATA"] = str(verdadeira)
    ambiente.pop("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL", None)   # o pytest de fora poe
    ambiente["PYTHONPATH"] = str(RAIZ)
    processo = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "tests.conftest", "-p", "no:cacheprovider",
         f"--basetemp={tmp_path / 'base'}", f"--rootdir={arquivo.parent}", str(arquivo)],
        cwd=RAIZ, env=ambiente, capture_output=True, text=True, timeout=180)
    assert processo.returncode == 0, processo.stdout + processo.stderr

    escritos = sorted(str(p.relative_to(verdadeira)) for p in verdadeira.rglob("*"))
    assert escritos == [], (
        "o teste escreveu na pasta de dados de verdade depois do fim da sessao: "
        f"{escritos}")
