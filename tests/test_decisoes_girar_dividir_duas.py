"""D-662 (Samuel, Central, 10/11/2026): no Dividir com "Duas lado a lado", "todas as folhas" gira página por página.

Pergunta (girar-capa-dividir-duas, refeita com provas em 09/11, Gradus folha 10, páginas 18 e 19): "No
Dividir, com "Duas lado a lado", "todas as folhas": gira a folha inteira ou página por página?" →
"Página por página também".
Livro: "No Dividir, com "Duas lado a lado", girar "todas as folhas" gira cada página sozinha e inteira, sem
pedaço da vizinha (como fora do Dividir). A capa gira inteira."

Antes (o defeito, print a-70): ali a tela mostra a FOLHA inteira com a linha, e "todas as folhas" girava
todas as folhas do scan inteiras; a linha da divisão ficava no mesmo lugar e cortava as duas páginas
deitadas ao meio: cada página saía no PDF como uma tira com metade de duas páginas.

Agora: o mesmo resultado de fora do Dividir (Cortar as bordas, "todas as páginas", D-636/D-640): cada
página das folhas divididas gira sozinha; a folha inteira (a capa aberta) gira inteira; nenhuma folha
dividida ganha rotação; a linha não muda. Uma ação só do desfazer.

Só o "todas as folhas": "só esta folha" (D-618, a folha inteira gira, como antes) e "daqui em diante",
"só as pares" e "só as ímpares" no Dividir com "Duas lado a lado" não mudam (D-662 não fala deles;
pergunta no relatório). O girar fora do Dividir e as D-638/D-640/D-645 também não.

Os testes test_reversao_d662_* falham no código de antes (girar-capa 269f05f3): saída em
relatorios/girar-capa/reversao-d662-no-codigo-antigo.txt.

O livro de teste é o das provas da D-638/D-640 (tests/test_decisoes_girar_capa.py): folha 1 inteira (a
capa aberta), folha 2 inteira (um encarte), folhas 3 e 4 divididas na dobra. Páginas: 1 (capa),
2 (encarte), 3 e 4 (folha 3), 5 e 6 (folha 4).
"""
from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from core import girar  # noqa: E402
from tests.test_decisoes_girar_capa import (  # noqa: E402,F401
    _confere_tudo_girado,
    _ctrl_y,
    _ctrl_z,
    _gerar,
    _girar,
    _giros,
    _livro_com_a_capa_inteira,
    _rotacoes,
    app,
    janela,
    pasta,
)


def _no_dividir_em_duas(janela, tmp_path, pagina: int = 2):
    """O livro da capa inteira, na ferramenta Dividir com "Duas lado a lado", na página `pagina`
    (de fábrica a 3: a esquerda da folha 3, dividida). A tela mostra a folha inteira com a linha."""
    from ui.tela_conferir import DUAS, FERRAMENTA_DIVIDIR

    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path, FERRAMENTA_DIVIDIR)
    tela.definir_mostrar(DUAS)
    tela.ir_para_pagina(pagina)
    assert tela.indice_folha == projeto.paginas[pagina].folha
    assert tela._pagina_que_gira_sozinha() is None          # a tela mostra a folha (D-618)
    return tela, projeto


def test_reversao_d662_todas_as_folhas_gira_cada_pagina_sozinha(janela, tmp_path):
    """No Dividir, "Duas lado a lado", folha 3 (dividida), "todas as folhas" + ¼ à direita: cada
    página das folhas divididas deita sozinha; a capa e o encarte (inteiros) giram inteiros; as
    folhas divididas não ganham rotação e a linha não muda. Uma ação só. REVERSÃO: antes as
    quatro folhas giravam (rotacao [90, 90, 90, 90]) e nenhuma página."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path)
    linhas = [f.posicao_corte for f in projeto.folhas]
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 90, 0, 0]
    assert _giros(projeto) == [0, 0, 90, 90, 90, 90]
    assert [f.posicao_corte for f in projeto.folhas] == linhas
    assert len(janela.acoes.feitas) == feitas + 1                     # uma ação só


def test_reversao_d662_igual_a_fora_do_dividir(janela, tmp_path):
    """"como fora do Dividir": o resultado é o MESMO do "todas as páginas" da ferramenta Cortar as
    bordas na mesma página (D-636/D-640, o caminho da simulação de 09/11). REVERSÃO: antes era
    outro (as folhas giravam inteiras)."""
    from ui.tela_conferir import FERRAMENTA_CORTAR, UMA

    tela, projeto = _no_dividir_em_duas(janela, tmp_path)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    no_dividir = (_rotacoes(projeto), _giros(projeto))
    _ctrl_z(tela)
    assert _rotacoes(projeto) == [0] * 4 and _giros(projeto) == [0] * 6
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.definir_mostrar(UMA)
    tela.ir_para_pagina(2)
    assert tela._pagina_que_gira_sozinha() == 2
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    assert (_rotacoes(projeto), _giros(projeto)) == no_dividir


def test_reversao_d662_viradas_como_a_pagina_da_vez_e_o_ctrl_z_e_o_ctrl_y(janela, tmp_path):
    """Todas ficam viradas como a página da vez (D-035): a página 3 já estava deitada (¼ à
    direita) e a 6 de cabeça para baixo; "todas as folhas" + ¼ à direita deixa todas em 180.
    O Ctrl+Z devolve a cada uma o giro que tinha, de uma vez; o Ctrl+Y refaz. REVERSÃO: antes
    as folhas giravam e as páginas ficavam como estavam."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path)
    projeto.paginas[2].giro_da_pagina = 90
    projeto.paginas[5].giro_da_pagina = 180
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    assert _giros(projeto) == [0, 0, 180, 180, 180, 180]
    assert _rotacoes(projeto) == [180, 180, 0, 0]
    _ctrl_z(tela)
    assert _giros(projeto) == [0, 0, 90, 0, 0, 180] and _rotacoes(projeto) == [0] * 4
    _ctrl_y(tela)
    assert _giros(projeto) == [0, 0, 180, 180, 180, 180]
    assert _rotacoes(projeto) == [180, 180, 0, 0]


@pytest.mark.parametrize("cortar", [False, True])
def test_reversao_d662_o_pdf_sai_com_cada_pagina_inteira(janela, tmp_path, cortar):
    """Medida de imagem (§4.7): o PDF (com e sem o corte das bordas) depois de "todas as folhas" +
    ¼ à esquerda no Dividir com "Duas lado a lado": cada página é a MESMA imagem de antes, girada
    (do tamanho dela, deitada, sem pedaço da vizinha); a capa e o encarte também, inteiros. O Ctrl+Z
    devolve o PDF de antes. REVERSÃO: antes cada página dividida saía como uma tira (outra forma,
    com metade de duas páginas)."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path)
    antes = _gerar(projeto, tmp_path, "antes", cortar)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    _confere_tudo_girado(antes, _gerar(projeto, tmp_path, "depois", cortar), girar.GIRO_ESQUERDA)
    _ctrl_z(tela)
    de_novo = _gerar(projeto, tmp_path, "de-novo", cortar)
    for a, b in zip(antes, de_novo):
        assert a.shape == b.shape and np.abs(a.astype(int) - b.astype(int)).mean() < 1


def test_reversao_d662_a_pagina_da_direita_tambem_serve_de_referencia(janela, tmp_path):
    """Na página da direita da folha (página 4), o mesmo: todas viradas como ela."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path, pagina=3)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_MEIA_VOLTA)
    assert _giros(projeto) == [0, 0, 180, 180, 180, 180]
    assert _rotacoes(projeto) == [180, 180, 0, 0]


def test_d662_as_palavras_do_dividir_nao_mudam(janela, tmp_path):
    """O quadro e a lista do Dividir com "Duas lado a lado" continuam dizendo "folha" (D-367): a
    tela mostra a folha. Só o resultado do "todas as folhas" mudou."""
    tela, _ = _no_dividir_em_duas(janela, tmp_path)
    combo = tela.barra_girar.combo_alcance
    itens = [combo.itemText(i) for i in range(combo.count())]
    assert "todas as folhas" in itens and "só esta folha" in itens


def test_d662_so_esta_folha_no_dividir_continua_girando_a_folha(janela, tmp_path):
    """D-618 (ressalva do Dividir) continua: "só esta folha" no Dividir com "Duas lado a lado" gira
    a folha da tela inteira, como antes; nenhuma página ganha giro."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [0, 0, 90, 0] and _giros(projeto) == [0] * 6


def test_d662_na_capa_no_dividir_continua_a_d638(janela, tmp_path):
    """Na capa (folha inteira) no Dividir com "Duas lado a lado", "todas as folhas" segue a D-638
    como antes: a capa e o encarte giram inteiros e as páginas das divididas cada uma sozinha."""
    tela, projeto = _no_dividir_em_duas(janela, tmp_path, pagina=0)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]


def test_d662_fora_do_dividir_nada_muda(janela, tmp_path):
    """O girar fora do Dividir não muda: na ferramenta Cortar as bordas, página 3, "todas as
    páginas" + ¼ à direita dá o mesmo de antes do conserto (D-636 com a D-640)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 90, 0, 0] and _giros(projeto) == [0, 0, 90, 90, 90, 90]
