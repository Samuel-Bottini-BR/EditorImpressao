"""As provas da D-614: na janela grande do Automático, com "Dividir" marcado, o "depois" mostra a
folha como se a divisão já tivesse sido feita (CLAUDE.md §11, regra 4; docs/plano/DECISOES.md).

  D-614 (04/11/2026). Samuel, print a-60: "o dividir folha está escolhido era para aparecer uma
      folha divida ali né, e não duas folhas coladas, está errado" · "era para eu ter um preview
      de como vai ficar a folha separada" · "não gostei de nenhuma alternativa é para aparecer
      como se já tivesse sido feita a separação." · "você já sabe como é, porque eu preciso
      mandar um print". No Livro: "o "depois" mostra a folha como se a divisão já tivesse sido
      feita, igual à área de trabalho depois de dividir (D-601, "Uma página"): uma página por
      vez, a metade cortada na linha, e as setas andam pelas páginas." Muda só a parte da D-577
      sobre o Dividir ("o depois mostra as duas metades lado a lado"); o resto da D-577 fica.
  D-601 (02/11/2026), a área de trabalho que a D-614 manda seguir: as setas andam pelas páginas
      (a esquerda, depois a direita, depois a próxima folha; a folha não dividida é um passo
      só) e o rótulo não muda ("folha N de M" nas duas metades).

Teste de reversão (§4.7): no código de antes (`ad563c35`), o "depois" da folha dupla com
"Dividir" marcado eram as duas metades lado a lado, com um vão branco no meio
(VAO_ENTRE_AS_METADES), e o ">" ia direto para a folha seguinte.

Livro sintético do tests/test_decisoes_automatico.py: folha 0 dupla (duas páginas lado a lado),
folha 1 torta, folha 2 reta.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico import _livro  # noqa: E402
from tests.test_decisoes_automatico_ver_como_fica import (  # noqa: E402,F401
    _abrir, _assentar, _esperar, _folha_crua, _imagens, _marcar, app, janela, pasta)


def _metades_do_rodar(janela) -> list[np.ndarray]:
    """As duas páginas da folha 0 como o "Rodar" de verdade as desenha (já rodado), na
    resolução da prévia e como saem na tela (a mesma conta da prévia)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from ui.automatico import DPI_DA_PREVIA

    projeto = janela.projeto
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        saida = []
        for pagina in [p for p in projeto.paginas_ativas if p.folha == 0]:
            img, _ = renderizar_pagina(doc, projeto, pagina, dpi=DPI_DA_PREVIA)
            saida.append(A.como_sai_na_tela(img, projeto, pagina, DPI_DA_PREVIA))
        return saida
    finally:
        doc.close()


def test_d614_com_dividir_o_depois_e_uma_pagina_e_as_setas_andam_pelas_paginas(janela, app,
                                                                                  tmp_path):
    """Folha dupla ainda inteira, "Dividir" marcado: o depois é UMA página (a metade da
    esquerda, cortada na linha, igual ao "Rodar" de verdade, ponto por ponto); ">" mostra a
    outra metade (a da direita, sem conta nova); ">" de novo vai para a folha seguinte; "<"
    volta para a metade da direita. O contador não muda nas duas metades ("página 1 de 3"),
    como o rodapé da área de trabalho no Dividir (D-601). O antes continua a folha inteira
    crua (D-577)."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    crua = _folha_crua(janela, 0)
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    antes, esquerda = _imagens(painel)
    assert np.array_equal(antes, crua), "o antes não é mais a folha inteira crua"
    assert esquerda.shape[1] < crua.shape[1] * 0.6, (
        f"o depois não é uma página só: {esquerda.shape} (folha {crua.shape})")
    assert painel.visor._crus[1] is esquerda, "a vista não mostra a metade"
    assert painel.contador.text() == "página 1 de 3"
    assert painel.botao_proxima.isEnabled() and not painel.botao_anterior.isEnabled()
    painel.botao_proxima.click()
    assert painel._indice == 0, "o > pulou a outra metade da folha"
    _esperar(app, painel)
    antes2, direita = _imagens(painel)
    assert np.array_equal(antes2, crua)
    assert direita.shape[1] < crua.shape[1] * 0.6 and not np.array_equal(direita, esquerda)
    assert painel.contador.text() == "página 1 de 3"
    assert painel.botao_anterior.isEnabled()
    painel.botao_proxima.click()
    assert painel._indice == 1, "o > não foi para a folha seguinte"
    _esperar(app, painel)
    assert painel.contador.text() == "página 2 de 3"
    painel.botao_anterior.click()
    assert painel._indice == 0
    _esperar(app, painel)
    assert np.array_equal(_imagens(painel)[1], direita), "o < não voltou para a metade da direita"
    # a metade é a do "Rodar" de verdade (o mesmo caminho: a prévia não mente)
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    de_verdade = _metades_do_rodar(janela)
    assert len(de_verdade) == 2
    assert np.array_equal(esquerda, de_verdade[0]), "a metade da esquerda não é a do Rodar"
    assert np.array_equal(direita, de_verdade[1]), "a metade da direita não é a do Rodar"


def test_d614_desmarcar_dividir_volta_a_folha_inteira_e_um_passo_por_folha(janela, app, tmp_path):
    """Sem "Dividir" marcado nada muda: o depois é a folha inteira e o ">" vai para a folha
    seguinte. Desmarcar estando na metade da direita volta à folha inteira (a mesma página)."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    crua = _folha_crua(janela, 0)
    _, inteira = _imagens(painel)
    assert inteira.shape[:2] == crua.shape[:2]
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    painel.botao_proxima.click()                    # a metade da direita
    _esperar(app, painel)
    _marcar(grande, set())
    _esperar(app, painel)
    assert painel._indice == 0
    _, depois = _imagens(painel)
    assert depois.shape[:2] == crua.shape[:2], "desmarcar não voltou a folha inteira"
    assert np.array_equal(depois, inteira)
    painel.botao_proxima.click()
    assert painel._indice == 1, "sem Dividir, o > tinha de ir para a folha seguinte"


def test_d614_tela_cheia_e_comparar_mostram_a_mesma_metade(janela, app, tmp_path):
    """O "tela cheia" e o "comparar" mostram o mesmo depois novo (D-614: "O "tela cheia" e o
    "comparar" mostram o mesmo "depois" novo"): a metade, e o ">" de lá anda pelas páginas."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    painel.botao_tela_cheia.click()
    _assentar(app)
    tela = painel.tela_cheia
    _, esquerda = _imagens(painel)
    assert tela.visor._crus[1] is esquerda, "a tela cheia não mostra a metade"
    assert tela.contador.text() == "página 1 de 3"
    tela.botao_comparar.click()
    _esperar(app, painel)
    _assentar(app)
    assert tela.vista_b._pixmap is not None
    assert (tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()) == esquerda.shape[:2]
    tela.botao_proxima.click()
    _esperar(app, painel)
    _assentar(app)
    assert painel._indice == 0
    _, direita = _imagens(painel)
    assert not np.array_equal(direita, esquerda)
    assert (tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()) == direita.shape[:2]
    tela.botao_comparar.click()
    _assentar(app)
    assert tela.visor._crus[1] is direita


def test_d614_folha_ja_dividida_nao_muda(janela, app, tmp_path):
    """Folha já dividida no livro (o "Rodar" de verdade com "Dividir"): com "Dividir" marcado
    ou não, cada metade é uma página do livro, o ">" anda de uma para a outra como antes, e
    o depois de cada uma é ela mesma."""
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    janela.estado_do_automatico.marcadas = {A.DIVIDIR}
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar(app)
    assert [p.metade for p in janela.projeto.paginas if p.folha == 0] == ["esquerda", "direita"]
    janela.tela_conferir.ir_para_pagina(0)
    grande = janela.abrir_o_automatico()
    painel = grande.antes_e_depois
    _esperar(app, painel)
    for marcadas in ({A.DIVIDIR}, set()):
        _marcar(grande, marcadas)
        _esperar(app, painel)
        painel.ir_para(0)
        _esperar(app, painel)
        antes, depois = _imagens(painel)
        assert depois.shape[:2] == antes.shape[:2], "o depois não é a mesma metade"
        assert painel.contador.text() == "página 1 de 4"
        painel.botao_proxima.click()
        assert painel._indice == 1, "o > não foi para a outra metade (outra página do livro)"
        _esperar(app, painel)
        assert painel.contador.text() == "página 2 de 4"
