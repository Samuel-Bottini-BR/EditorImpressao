"""D-612, conserto do teste do Samuel (04/11/2026, prints a-77 e a-78, Mover em "Uma página" com o
"antes / depois"): "print 4 aparece uma mensagem pedindo para escolher filtro, esse era o objetivo?
print 5 - não mostra o depois mesmo movendo a pagina ou aumentando ela."

Pela D-612 ("Ok, pode ser assim o antes e depois"), com Mover, Cortar e Endireitar o "depois" é a
página como vai sair COM o que a ferramenta fez, mesmo com o filtro em Original, e o "antes" é a
página como veio. Antes, com a página em Original, o "antes / depois" não comparava nada: dizia
"Escolha outro filtro para comparar com o Original." (o aviso continua nas outras ferramentas, que
comparam só o filtro).

O que se mede: o que a VistaAntesDepois recebe (comparando, aviso, as duas imagens) e que o
"depois" muda com o Mover e o "antes" não. Em `d2567fab` os testes de reversão falham.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PySide6")

from tests.test_decisoes_mover import (  # noqa: E402,F401
    _assentar,
    _esperar,
    _pdf,
    app,
    janela,
    pasta,
)


def _imagem(pix) -> np.ndarray:
    img = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = img.width(), img.height()
    dados = np.frombuffer(img.constBits(), np.uint8).reshape(h, img.bytesPerLine())
    return dados[:, : w * 3].reshape(h, w, 3).copy()


def _ligado(janela, tmp_path, ferramenta: str):
    """Livro aberto (página em Original, como vem), a ferramenta e o "antes / depois" ligado."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta(ferramenta)
    tela.botao_antes_depois.click()
    _assentar()
    vista = tela.vista_antes_depois
    assert tela.comparando and tela.vista_da_pagina.currentWidget() is vista
    assert _esperar(lambda: vista.depois is not None and vista.antes is not None, 30), \
        (vista.depois is not None, vista.antes is not None, vista.aviso)
    return tela, vista


@pytest.mark.parametrize("ferramenta", ["mover", "cortar", "endireitar"])
def test_reversao_d612_com_a_ferramenta_compara_mesmo_em_original(janela, tmp_path, ferramenta):
    """Página em Original, ferramenta de página: o "antes / depois" compara (a linha, as duas
    imagens), sem o aviso de escolher outro filtro."""
    tela, vista = _ligado(janela, tmp_path, ferramenta)
    assert vista.comparando
    assert vista.aviso == ""


def test_reversao_d612_o_depois_do_mover_mostra_o_que_ele_fez(janela, tmp_path):
    """Mover a 131% (o print a-78): o "depois" passa a ser a página aumentada (o texto passa da
    beirada), o "antes" continua a página como veio."""
    tela, vista = _ligado(janela, tmp_path, "mover")
    antes_do_mover = (_imagem(vista.antes), _imagem(vista.depois))
    tela.campo_tamanho_do_conteudo.setValue(131)
    _assentar()
    assert _esperar(lambda: not np.array_equal(_imagem(vista.depois), antes_do_mover[1]), 30)
    assert np.array_equal(_imagem(vista.antes), antes_do_mover[0]), "o 'antes' mudou com o Mover"
    assert vista.comparando and vista.aviso == ""


def test_d612_nas_outras_ferramentas_o_aviso_do_filtro_continua(janela, tmp_path):
    """Guarda (D-605): na Mão (só olha), o "antes / depois" compara o filtro como antes; com a
    página em Original, o aviso "Escolha outro filtro para comparar com o Original." continua."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mao")
    tela.botao_antes_depois.click()
    vista = tela.vista_antes_depois
    assert _esperar(lambda: vista.depois is not None, 30)
    assert not vista.comparando
    assert vista.aviso == "Escolha outro filtro para comparar com o Original."
