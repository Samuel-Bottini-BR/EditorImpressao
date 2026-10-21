"""Verificador, 21/10/2026: o teste de reversao do implementador para o bug de 08/10 ("usar em todas apaga as
excecoes") importa a janela nova (ui.dialogo_escolher_paginas), entao no codigo antigo ele falha por
ImportError, nao pelo bug. Este e o mesmo caso SEM a janela nova: so chama _recorte_em_todas() e olha a
excecao. Copiar para tests/ da worktree e rodar com pytest. No codigo novo a janela "Em quais paginas?" e
respondida pelo padrao dela (as excecoes desmarcadas), como faz o teste do implementador."""
from __future__ import annotations

import pytest

pytest.importorskip("fitz")
from tests.test_mesmo_livro_outro_caminho import _analisar, _pdf, app, janela, pasta  # noqa: F401, E402


def test_usar_em_todas_guarda_a_excecao(janela, pasta, monkeypatch):
    janela.abrir_livro(str(_pdf(pasta)))
    _analisar(janela)
    tela, projeto = janela.tela_conferir, janela.projeto
    try:
        from ui import dialogo_escolher_paginas as dep
        monkeypatch.setattr(type(tela), "_escolher_paginas_do_corte",
                            lambda self: dep.paginas_de_fabrica(self.projeto, self.indice_pagina), raising=False)
    except ImportError:
        pass                                   # codigo antigo: nao ha janela
    excecao = [0.2, 0.2, 0.6, 0.6]
    projeto.paginas[2].recorte = excecao
    tela.ir_para_pagina(0)
    projeto.paginas[0].recorte = [0.05, 0.05, 0.9, 0.9]
    tela._recorte_em_todas()
    assert list(projeto.paginas[1].recorte) == [0.05, 0.05, 0.9, 0.9]
    assert list(projeto.paginas[2].recorte) == excecao, projeto.paginas[2].recorte
