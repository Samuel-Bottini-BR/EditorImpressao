"""D-649 (Samuel, 07/11/2026, Central `k0711-miniatura-pdf`): "Consertar" · "Isso é um erro grave.
O preview as miniaturas tem que estar sincronizada e o resultado final tem que sair como a edição
foi mostrada no preview ." Reforça a D-547 (a miniatura mostra a página movida como sai no PDF) e a
D-473 ("Tela e PDF diferentes é defeito, nunca escolha").

O defeito (teste como o Kaique de 07/11/2026, versão 6904a634, Lusíadas, página 5, erros N2, N3 e
N8 do relatório `teste-kaique-funcoes`): depois do Mover, o PDF saiu com o conteúdo subido e sem o
título "PREFÁCIO", mas a miniatura da tira e a da grade "Todas as páginas" mostravam a página com o
título no lugar.

Duas causas, as duas provadas aqui:
  a. a folha espremida no Mover e na Mão (N2): a tela trocava a prévia da página pela folha CRUA
     reduzida à forma da página, e o "Centralizar" foi feito nessa imagem. Consertado na origem em
     09/11/2026 (`88731637`, core/pipeline.acertar_no_tamanho_do_pdf; prova
     tests/test_decisoes_gravura_a_mao.py::test_d659_a_tela_nao_troca_a_previa_pela_folha_crua).
     A prova (a) abaixo é uma GUARDA (passa também no código de 07/11, porque o livro de teste não
     tem a marcação provisória): confere que a imagem do Mover tem a forma da página. A reversão
     dessa causa é a do D-659, que falha no 6904a634 ("devolveu a folha crua como se fosse o
     desenho do PDF"; relatorios/graves-2026-11-10/reversao.txt).
  b. a miniatura (N8): só era composta como no PDF se a prévia da página ainda estivesse guardada
     (as últimas 30); depois de reabrir o livro ela ficava com a página como veio, e a grade nunca
     compunha. Consertado em 10/11/2026 (ramo graves-2026-11-10): a prévia que falta é pedida por
     trás e a miniatura sai pela conta única da composição (core.pipeline.compor_como_no_pdf), a
     mesma do PDF, na tira e na grade.

A medida (CLAUDE.md §4.7, defeito de imagem): a linha mais alta com tinta, em fração da altura da
página. No livro de teste a página tem, no alto, uns quadradinhos pretos (o "título"); movida
17% para cima (o deslocamento do Lusíadas, -0,17), eles saem da folha no PDF. A miniatura tem de
começar a tinta no mesmo lugar do PDF (até 3% da altura). No código antigo a miniatura da página
movida, depois de reabrir o livro, fica com o título (a tinta começa em ~7% da altura, e o PDF em
0%): a prova (b) falha ("não aconteceu a tempo").
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_9b2 import (  # noqa: E402,F401 - as fixtures app, pasta e janela
    _assentar,
    _caixa_da_tinta,
    _esperar,
    _gerar,
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)

DESLOCAMENTO_DO_LUSIADAS = (0.0, -0.17)     # o "Centralizar" gravado na tela espremida (notas.md)
MOVIDA = 5                                  # a página 6 do livro de teste


def _livro_com_a_pagina_2_movida(janela, tmp_path):
    """Um livro de 8 páginas; a página 6 (longe da 1: fora das 3 que a tela adianta) com o
    conteúdo movido 17% para cima (ferramenta Mover). Devolve o caminho do PDF de entrada."""
    caminho = _pdf(tmp_path / "livro.pdf", [_pagina(marca=k + 3) for k in range(8)])
    janela.abrir_livro(caminho)
    tela = janela.tela_conferir
    tela.ir_para_pagina(MOVIDA)
    tela.escolher_ferramenta("mover")
    _esperar(lambda: tela.previas.ja_pronta(MOVIDA, tela._dpi_atual) is not None, motivo="a prévia")
    assert tela._gravar_o_conteudo(1.0, DESLOCAMENTO_DO_LUSIADAS, "mover para cima")
    _assentar()
    return caminho


def test_d649_a_o_mover_mostra_a_pagina_e_nao_a_folha_espremida(janela, tmp_path):
    """D-649 (a), guarda: na ferramenta Mover, a imagem em que o "Centralizar" mede é a da
    página (a mesma forma da prévia da página), nunca a folha inteira reduzida (N2 de 07/11)."""
    _livro_com_a_pagina_2_movida(janela, tmp_path)
    tela = janela.tela_conferir
    previa = tela.previas.ja_pronta(MOVIDA, tela._dpi_atual)
    da_vez = tela._mover_da_vez
    assert da_vez["conteudo"] == (previa.shape[1], previa.shape[0])
    altura_pt, largura_pt = 840, 600                      # a página do livro de teste
    assert abs(previa.shape[1] / previa.shape[0] - largura_pt / altura_pt) < 0.02


def test_d649_b_a_miniatura_da_pagina_movida_sai_como_o_pdf_depois_de_reabrir(janela, tmp_path):
    """D-649 (b), o caso do Lusíadas: depois de reabrir o livro (nenhuma prévia guardada), a
    miniatura da página movida na tira e na grade "Todas as páginas" começa a tinta no mesmo
    lugar do PDF (o título saiu da folha nos três), sem visitar a página."""
    caminho = _livro_com_a_pagina_2_movida(janela, tmp_path)
    no_pdf = _caixa_da_tinta(_gerar(janela, tmp_path, "saida")[MOVIDA])
    assert no_pdf[1] < 0.02                               # no PDF o "título" saiu da folha

    tela = janela.tela_conferir
    tela.ir_para_pagina(0)
    janela._salvar_agora()
    janela.abrir_livro(caminho)                           # reabrir: nada guardado
    tela = janela.tela_conferir
    tela.ir_para_pagina(0)
    tela.escolher_ferramenta("filtros")
    assert tela.indice_pagina == 0

    _esperar(lambda: MOVIDA in tela.tira._como_sai, segundos=40,
             motivo="a miniatura da página movida composta como no PDF")
    _chave, mini = tela.tira._como_sai[MOVIDA]
    na_tira = _caixa_da_tinta(mini, rgb=False)
    assert abs(na_tira[1] - no_pdf[1]) <= 0.03, (na_tira, no_pdf)

    tela.abrir_todas_as_paginas()                         # a grade usa a mesma miniatura
    na_grade = tela._pagina_dentro_da_folha(MOVIDA, np.full((84, 60, 3), 255, np.uint8))
    assert abs(_caixa_da_tinta(na_grade, rgb=False)[1] - no_pdf[1]) <= 0.03
    # as páginas que não foram movidas continuam como sempre (a folha como veio, D-547)
    assert set(tela.tira._como_sai) == {MOVIDA}
