"""O programa nao some ao clicar "Conferir" logo depois do "cancelar".

Bug antigo achado pelo verificador (30/09/2026, print s33, sonda
reproducoes/sonda3_thread.py): "cancelar" em "Olhando o livro..." pede para a
analise parar, mas ela ainda roda por uma fracao de segundo (termina a pagina
em que esta). Se nesse intervalo comecava outra analise, a janela trocava
`self.tarefa` e a analise antiga perdia a ultima referencia do Python; o Qt
destruia o QThread ainda rodando e derrubava o processo inteiro, sem
mensagem e sem nada no erros.log (queda nativa: nenhuma excecao Python).
Contra a regra "nenhuma excecao fecha a janela".

A queda mata o processo, entao o cenario roda num processo a parte e o teste
confere que ele terminou normalmente. Pasta de dados: a do conftest.py
(LOCALAPPDATA de mentira), herdada pelo processo filho.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CENARIO = textwrap.dedent(r'''
    import os, sys, time
    from pathlib import Path
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    sys.path.insert(0, sys.argv[1])
    import fitz
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    from core import pipeline
    from ui.janela_principal import JanelaPrincipal

    livro = Path(sys.argv[2])
    doc = fitz.open()
    for i in range(int(sys.argv[3])):
        pagina = doc.new_page(width=1200, height=1700)
        for linha in range(40):
            pagina.insert_text((60, 60 + linha * 40), f"folha {i} linha {linha} " * 6, fontsize=12)
    doc.save(str(livro))
    doc.close()

    j = JanelaPrincipal()
    j.avisar = lambda *a, **k: None
    j.abrir_livro(str(livro))
    if j.aviso_do_fundo is not None:
        j.aviso_do_fundo.done(0)
    j.projeto.detectar_regioes = False
    j._analise_pronta(pipeline.analisar_projeto(j.projeto))

    for vez in range(int(sys.argv[4])):
        j._sair_da_conferencia()
        j.analisar()
        time.sleep(0.25)
        app.processEvents()
        j.cancelar()
        j.analisar()                  # "Conferir" logo depois do "cancelar"
        j.cancelar()
        import gc; gc.collect()
    for _ in range(300):
        app.processEvents()
        time.sleep(0.01)
    j.close()
    for _ in range(50):
        app.processEvents()
        time.sleep(0.01)
    print("FIM sem cair", flush=True)
''')


def _rodar(tmp_path: Path, folhas: int = 12, vezes: int = 3) -> subprocess.CompletedProcess:
    script = tmp_path / "cenario.py"
    script.write_text(CENARIO, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(script), str(RAIZ), str(tmp_path / "livro.pdf"), str(folhas), str(vezes)],
        capture_output=True, text=True, timeout=300, env=dict(os.environ), cwd=str(RAIZ))


def test_conferir_logo_depois_do_cancelar_nao_derruba_o_programa(tmp_path):
    resultado = _rodar(tmp_path)
    assert resultado.returncode == 0, (
        f"o programa caiu (codigo {resultado.returncode}):\n{resultado.stdout}\n{resultado.stderr[-2000:]}")
    assert "FIM sem cair" in resultado.stdout
