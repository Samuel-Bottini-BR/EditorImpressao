"""Prova de comportamento da D-590 (30/10/2026): "juntar todas" na ferramenta Dividir.

Samuel: "se quiser juntar as folhas de novo deveria ter uma opção mais clara né" · pergunta:
"na ferramenta Dividir, ao lado de \"não dividir esta\", um botão \"juntar todas\", que junta
todas as folhas do livro de uma vez (o Ctrl+Z desfaz). E desmarcar \"Dividir\" no Automático não
junta nada. Pode ser assim?" → "pode ser assim".
Livro de decisões: "Ferramenta Dividir: botão 'juntar todas' ao lado de 'não dividir esta', que
junta todas as folhas divididas do livro numa ação só do desfazer. 'Dividir' desmarcada no
Automático não junta nada (exceção à D-589)."

O que se mede: a lista de páginas do projeto, o Histórico (uma ação só) e o PDF que o programa
grava (core.pipeline.processar). Livro sintético de 3 folhas com o livro aberto (duas páginas
lado a lado), como tests/test_decisoes_dividir.py, de onde vêm os ajudantes.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _estado_das_outras,
    _gerar,
    _livro_aberto,
    _no_dividir,
    _rodar,
    app,
    janela,
    pasta,
    precisa_da_dll,
)


@precisa_da_dll
def test_d590_juntar_todas_junta_as_folhas_divididas_numa_acao_so(janela, tmp_path):
    """D-590: livro dividido pelo Automático (3 folhas → 6 páginas), com trabalho numa página
    (corte à mão) e a folha 3 já juntada à mão → "juntar todas" na ferramenta Dividir → todas as
    folhas viram uma página só (3 páginas, o PDF sai com 3 folhas deitadas), numa ação só do
    Histórico; Ctrl+Z → divididas de novo, com o corte à mão de volta; "dividir esta" numa
    folha devolve as duas páginas dela como estavam (as metades ficam guardadas)."""
    janela.show()
    janela.abrir_livro(_livro_aberto(tmp_path))
    _rodar(janela, [A.DIVIDIR])
    tela, projeto = janela.tela_conferir, janela.projeto
    assert len(projeto.paginas) == 6
    tela.ir_para_pagina(2)                                 # a esquerda da folha 2
    tela._mover_recorte((0.1, 0.1, 0.9, 0.9))
    _no_dividir(tela, 2)
    tela.botao_nao_dividir.click()                         # a folha 3 já juntada à mão
    assert len(projeto.paginas) == 5
    feitas = len(janela.acoes.feitas)

    _no_dividir(tela, 0)
    assert tela.botao_juntar_todas.text() == "juntar todas"
    assert tela.botao_juntar_todas.isVisible()
    tela.botao_juntar_todas.click()

    assert [p.metade for p in projeto.paginas] == ["inteira"] * 3
    assert [p.folha for p in projeto.paginas] == [0, 1, 2]
    assert [p.indice for p in projeto.paginas] == [0, 1, 2]
    assert not any(f.dividir for f in projeto.folhas)
    assert not projeto.folhas[0].revisada and not projeto.folhas[1].revisada   # não "conferidas"
    assert len(janela.acoes.feitas) == feitas + 1          # uma ação só
    paginas = _gerar(janela, tmp_path, "juntadas")
    assert len(paginas) == 3 and all(p.shape[1] > p.shape[0] for p in paginas)

    tela.desfazer()                                        # Ctrl+Z: divididas de novo
    assert len(projeto.paginas) == 5
    assert [p.metade for p in projeto.paginas if p.folha < 2] == ["esquerda", "direita"] * 2
    assert projeto.paginas[2].recorte == (0.1, 0.1, 0.9, 0.9)
    tela.refazer()
    assert len(projeto.paginas) == 3

    _no_dividir(tela, 1)
    tela.botao_nao_dividir.click()                         # "dividir esta" devolve as duas
    da_folha = [p for p in projeto.paginas if p.folha == 1]
    assert [p.metade for p in da_folha] == ["esquerda", "direita"]
    assert da_folha[0].recorte == (0.1, 0.1, 0.9, 0.9)


@precisa_da_dll
def test_d590_juntar_todas_sem_folha_dividida_nao_muda_nada(janela, tmp_path):
    """D-590: livro sem folha dividida → "juntar todas" não muda nada nem entra no
    Histórico."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    antes = _estado_das_outras(projeto, -1)
    feitas = len(janela.acoes.feitas)
    _no_dividir(tela, 0)
    tela.botao_juntar_todas.click()
    assert _estado_das_outras(projeto, -1) == antes
    assert len(janela.acoes.feitas) == feitas


@precisa_da_dll
def test_d590_dividir_desmarcada_no_automatico_nao_junta_nada(janela, tmp_path):
    """D-590 (exceção à D-589): livro dividido pelo Automático → desmarcar "Dividir" e rodar
    outra etapa → as folhas continuam divididas (6 páginas no PDF)."""
    janela.abrir_livro(_livro_aberto(tmp_path))
    _rodar(janela, [A.DIVIDIR])
    projeto = janela.projeto
    assert len(projeto.paginas) == 6
    estado = janela.estado_do_automatico
    estado.marcadas = {A.LIMPAR}
    assert A.DIVIDIR in estado.pedido().desmarcadas
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assert len(projeto.paginas) == 6 and all(f.dividir for f in projeto.folhas)
    assert len(_gerar(janela, tmp_path, "continua")) == 6
