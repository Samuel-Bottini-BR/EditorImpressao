"""D-648 (Samuel, 07/11/2026, Central `k0711-filtros-tela-cheia`): "Consertar" · "Esse é um grave."
Os cartões de "Filtros em tela cheia" mostram a página com cada filtro (D-184: "A — A “um grande”,
com a chave “Comparar com o Original”"; D-192: "faça o recomendado." / "Está bom").

O defeito (teste como o Kaique de 07/11/2026, versão 6904a634, Lusíadas, erro N9): ao abrir
"Filtros em tela cheia", os quatro cartões da esquerda ficavam cinza, vazios, mesmo depois de
20 segundos. Causa: os cartões não tinham conta própria; copiavam a figurinha do painel "Filtro da
página", que só é desenhada com esse painel aberto ou com a ferramenta Filtro. Aberta pelo menu Ver,
com outra ferramenta e o painel fechado, nada era desenhado. (E, com o painel aberto, mostravam a
conta mais simples das figurinhas, não a da página grande: revisão de código de 10/11, A2.)

Conserto (10/11/2026, ramo graves-2026-11-10): cada cartão é a MESMA imagem que a página grande
mostra quando ele é escolhido (o caminho do PDF, core.pipeline.renderizar_com_filtro), pequena.
Achado ao fazer esta prova: num livro com "Limpar a folha" desligado (o livro novo) essa conta
desenhava a cópia da página SEM a marca de "filtro escolhido à mão" que a tela grava ao escolher, e
o "Preto e branco" (o cartão e a página grande) saía em Original. Agora a cópia leva a marca: sai
como sairia se a pessoa escolhesse o filtro.

A medida (CLAUDE.md §4.7): cada cartão recebe uma página com a tinta do texto (a caixa do preto
achada) e, no Preto e branco, quase sem meios-tons (o papel amarelado do livro de teste vira
branco), enquanto no Original o papel continua amarelado. No código antigo nenhum cartão recebe
imagem: a prova falha ("não aconteceu a tempo").
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_decisoes_9b2 import (  # noqa: E402,F401 - as fixtures app, pasta e janela
    _assentar,
    _caixa_da_tinta,
    _esperar,
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)


def _meios_tons(img: np.ndarray) -> float:
    """A fração de pontos que não são nem quase brancos nem quase pretos."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return float(((cinza > 40) & (cinza < 225)).mean())


def test_d648_os_quatro_cartoes_mostram_a_pagina_com_o_filtro_de_cada_um(janela, tmp_path):
    """D-648, o caso do Lusíadas: livro aberto, ferramenta Cortar (não a Filtro), painel "Filtro
    da página" fechado; menu Ver > "Filtros em tela cheia". Os quatro cartões recebem a página,
    cada um no seu filtro: o Preto e branco sem meios-tons, o Original com o papel do livro."""
    from ui.tela_conferir import PAINEL_FILTRO
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_pagina(marca=k) for k in range(3)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("cortar")
    _assentar()
    assert tela.paineis.aberto != PAINEL_FILTRO           # o painel do Filtro está fechado
    cheia = FiltrosEmTelaCheia(tela, parent=janela)
    recebidas: dict = {}
    for chave, cartao in cheia.cartoes.items():
        original = cartao.definir_amostra

        def anotar(img, chave=chave, original=original):
            recebidas[chave] = img
            original(img)
        cartao.definir_amostra = anotar
    try:
        _esperar(lambda: (cheia.atualizar() or True)
                 and all(recebidas.get(c) is not None for c in cheia.cartoes),
                 segundos=60, motivo="os quatro cartões com a página")
        assert set(cheia.cartoes) >= {ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO}
        for chave, img in recebidas.items():
            _caixa_da_tinta(img)                           # a página está ali, com o texto
            assert cheia.cartoes[chave].desenho.pixmap is not None
        assert _meios_tons(recebidas[PRETO_E_BRANCO]) < 0.05
        assert _meios_tons(recebidas[ORIGINAL]) > 0.5      # o papel amarelado, como veio
    finally:
        cheia.done(0)


def test_d648_como_sai_com_o_filtro_no_livro_novo_e_como_ao_escolher(tmp_path):
    """D-648, o segundo defeito (achado ao fazer a prova acima): no livro novo ("Limpar a folha"
    desligado), "como esta página sai com o Preto e branco" (core.pipeline.renderizar_com_filtro,
    a conta da página grande da tela cheia e dos cartões) tem de ser a página que sai depois de
    ESCOLHER o Preto e branco (a tela grava o filtro e a marca de escolhido à mão). No código
    antigo saía em Original (o papel amarelado: meios-tons ~0,9)."""
    import copy as copia_

    from core import automatico, etapas
    from core.pdf_io import abrir_pdf, info_paginas
    from core.pipeline import renderizar_com_filtro, renderizar_pagina
    from modelos import Projeto

    caminho = _pdf(tmp_path / "livro.pdf", [_pagina(marca=1)])
    projeto = Projeto(caminho_entrada=caminho, nome="livro")
    doc = abrir_pdf(caminho)
    try:
        automatico.livro_leve(projeto, [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)])
        assert not projeto.limpar                          # o livro novo
        pagina = projeto.paginas[0]
        como_sairia, _ = renderizar_com_filtro(doc, projeto, pagina, PRETO_E_BRANCO, dpi=60)
        escolhida = copia_.deepcopy(pagina)                 # o que a tela faz ao escolher
        escolhida.filtro = PRETO_E_BRANCO
        etapas.marcar_mexida_a_mao(escolhida, etapas.FILTRO)
        sai, _ = renderizar_pagina(doc, projeto, escolhida, dpi=60)
    finally:
        doc.close()
    assert pagina.filtro == ORIGINAL                       # a página de verdade não mudou
    assert _meios_tons(como_sairia) < 0.05, _meios_tons(como_sairia)
    assert como_sairia.shape == sai.shape and np.abs(
        como_sairia.astype(int) - sai.astype(int)).mean() < 1.0
