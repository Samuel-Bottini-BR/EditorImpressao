"""D-636 (Samuel, 05/11/2026): numa folha dividida, o "aplicar em" do girar gira PÁGINAS.

Pergunta (agente girar-pagina): "nessa lista, cada página gira sozinha, igual à da tela. O quadro passaria a
se chamar "Girar a página", e a lista diria "só esta página / todas as páginas / daqui em diante / pares /
ímpares". O mesmo valeria na tela "ver todas". Pode ser assim?" → "1- pode ser, só garanta que não crie mais
problemas fazendo isso, você tem que pensar na experiencia do usario e no resultado final do livro dentro do
programa, quando vai mudar algo, deixe isso anotado."

Livro de decisões (D-636): numa folha dividida, o quadro do girar se chama "Girar a página" e o "aplicar em"
diz "só esta página / todas as páginas / daqui em diante / pares / ímpares"; cada página gira sozinha, como a
da tela (D-618), também na tela "ver todas". As outras ficam viradas igual à da vez (D-035). Folha inteira
(não dividida): fica como está.

Como fica para quem usa e no livro (D-637): relatorios/girar-pagina/ONDE-PAREI.md.

Os testes de reversão (test_reversao_d636_*) falham no código de antes (girar-pagina 10f74f65): lá
"todas as folhas" numa folha dividida gira as FOLHAS (folha.rotacao muda) e cada página vira meia folha
deitada com pedaços das duas (a confusão do a-70); a grade "ver todas" também girava a folha inteira.
"""
from __future__ import annotations

import copy

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import girar, pipeline  # noqa: E402
from core.dividir_a_mao import campos_para_dividir  # noqa: E402
from core.endireitar import girar_90  # noqa: E402
# o livro de teste e a janela, os mesmos das provas da D-618
from tests.test_decisoes_girar_pagina import (  # noqa: E402,F401
    _folha_aberta,
    _paginas_do_pdf,
    _pdf,
    app,
    janela,
    pasta,
)


def _livro_com_duas_folhas_divididas(janela, tmp_path):
    """Três folhas abertas: a 1 e a 2 divididas na dobra (páginas 1 a 4), a 3 inteira (página 5,
    como uma capa aberta que ninguém dividiu). Ferramenta Cortar as bordas, na página 2."""
    from ui.tela_conferir import FERRAMENTA_CORTAR

    janela.abrir_livro(_pdf(tmp_path / "aberto.pdf", [_folha_aberta()] * 3))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("dividir", "folha", [0], campos_para_dividir(projeto, 0, 0.5), "Dividir")
    tela._registrar("dividir", "folha", [1], campos_para_dividir(projeto, 1, 0.5), "Dividir")
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "esquerda"), (0, "direita"), (1, "esquerda"), (1, "direita"), (2, "inteira")]
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(1)
    assert tela._pagina_que_gira_sozinha() == 1
    return tela, projeto


def _giros(projeto) -> list[int]:
    return [p.giro_da_pagina for p in projeto.paginas]


def _rotacoes(projeto) -> list[int]:
    return [f.rotacao for f in projeto.folhas]


def _itens(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


# --- reversão: "todas as páginas" gira cada página sozinha ---------------------------------------

def test_reversao_d636_todas_as_paginas_gira_cada_pagina_sozinha(janela, tmp_path):
    """Na página 2 (folha dividida), "todas" + ¼ à esquerda: as quatro páginas das folhas
    divididas ficam deitadas, cada uma sozinha; nenhuma folha do scan gira (a linha da divisão
    não muda) e a folha inteira (página 5) fica como está. REVERSÃO: antes as três folhas giravam
    (rotacao 270) e as páginas não."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    linhas = [f.posicao_corte for f in projeto.folhas]
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert _rotacoes(projeto) == [0, 0, 270]      # D-640 (06/11; troca autorizada pelo Samuel, Central girar-capa-testes-antigos, 07/11): a folha inteira também gira
    assert _giros(projeto) == [270, 270, 270, 270, 0]
    assert [f.posicao_corte for f in projeto.folhas] == linhas
    assert len([a for a in janela.acoes.feitas if a.tipo == "girar"]) == 1   # uma ação só


def test_reversao_d636_o_quadro_e_a_lista_dizem_pagina_na_folha_dividida(janela, tmp_path):
    """O quadro "Girar a página" e a lista "só esta página / todas as páginas / ..." numa folha
    dividida; o menu Página e o balão do canto dizem o mesmo. Na folha inteira, "folha", como
    sempre (D-367). REVERSÃO: antes dizia "folha" em todo lugar."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    barra, menu = tela.barra_girar, janela.menu.acoes
    assert barra.rotulo.text() == "Girar a página"
    assert _itens(barra.combo_alcance) == ["só esta página", "todas as páginas", "daqui em diante",
                                           "só as pares", "só as ímpares"]
    assert menu["giro_em_esta"].text() == "só esta página"
    assert menu["giro_em_todas"].text() == "todas as páginas"
    assert all("só esta página" in b.toolTip() for b in tela.girar_do_canto.botoes_de_giro.values())
    assert "página" in barra.combo_alcance.toolTip()

    tela.ir_para_pagina(4)                       # a folha inteira: fica como está
    assert barra.rotulo.text() == "Girar a folha"
    assert _itens(barra.combo_alcance)[:2] == ["só esta folha", "todas as folhas"]
    assert menu["giro_em_esta"].text() == "só esta folha"
    assert all("só esta folha" in b.toolTip() for b in tela.girar_do_canto.botoes_de_giro.values())

    barra.definir_alcance(girar.ALCANCE_TODAS)   # a escolha da lista não se perde na troca
    tela.ir_para_pagina(2)
    assert barra.rotulo.text() == "Girar a página"
    assert barra.alcance() == girar.ALCANCE_TODAS
    assert barra.combo_alcance.currentText() == "todas as páginas"


def test_reversao_d636_ver_todas_gira_so_as_paginas_escolhidas(janela, tmp_path):
    """Na tela "ver todas": escolher a página 2 (folha dividida) e a 5 (folha inteira) e "girar
    ¼ →": a 2 gira sozinha (a 1 não muda, a folha 1 não gira); a 5 gira a folha dela, como
    sempre. Um Ctrl+Z devolve tudo. REVERSÃO: antes girava a folha 1 inteira (a 1 junto)."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela._acao_nas_escolhidas("girar_direita", [1, 4])
    assert _giros(projeto) == [0, 90, 0, 0, 0]
    assert _rotacoes(projeto) == [0, 0, 90]
    tela._acao_nas_escolhidas("girar_esquerda", [0, 1])     # cada uma a partir de onde está
    assert _giros(projeto) == [270, 0, 0, 0, 0]
    tela.desfazer()
    assert _giros(projeto) == [0, 90, 0, 0, 0]
    tela.desfazer()
    assert _giros(projeto) == [0, 0, 0, 0, 0] and _rotacoes(projeto) == [0, 0, 0]


def test_d636_ver_todas_so_folhas_inteiras_gira_as_folhas_como_antes(janela, tmp_path):
    """D-487 / D-334: escolhidas só de folhas inteiras, a grade gira as folhas delas, como antes."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela._acao_nas_escolhidas("girar_direita", [4])
    assert _rotacoes(projeto) == [0, 0, 90] and _giros(projeto) == [0] * 5
    assert janela.acoes.feitas[-1].alvo == "folha"


# --- as outras escolhas da lista, com "página" --------------------------------------------------

def test_d636_daqui_em_diante_conta_paginas(janela, tmp_path):
    """"daqui em diante" na página 3: a 3 e a 4 deitam; a 1 e a 2 não mudam."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela.ir_para_pagina(2)
    tela.barra_girar.definir_alcance(girar.ALCANCE_DAQUI)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    # resposta do Samuel "Giram também" (Central, 07/11/2026): a folha inteira (página 5) está no
    # "daqui em diante" da página 3 e gira também, inteira
    assert _giros(projeto) == [0, 0, 90, 90, 0] and _rotacoes(projeto) == [0, 0, 90]
    assert "da página 3 em diante" in janela.acoes.feitas[-1].descricao


def test_d636_pares_e_impares_contam_o_numero_da_pagina_e_avisam(janela, tmp_path):
    """"só as pares" na página 2: a 2 e a 4. Na página 1 (ímpar): avisa e não gira (D-036, com
    página no lugar de folha)."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela.barra_girar.definir_alcance(girar.ALCANCE_PARES)
    tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    assert _giros(projeto) == [0, 180, 0, 180, 0]
    tela.ir_para_pagina(0)
    feitas = len(janela.acoes.feitas)
    tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    assert janela.avisos[-1] == ("Você está numa página ímpar. Para girar só as pares, "
                                 "vá a uma página par e gire de lá.")
    assert len(janela.acoes.feitas) == feitas and _giros(projeto) == [0, 180, 0, 180, 0]
    tela.barra_girar.definir_alcance(girar.ALCANCE_IMPARES)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _giros(projeto) == [90, 180, 90, 180, 0]


def test_d636_todas_ficam_viradas_como_a_da_vez_e_o_ctrl_z_devolve_cada_uma(janela, tmp_path):
    """D-035 com páginas: a 1 já estava ¼ à direita; na 2, "todas" + ¼ à esquerda → todas ficam
    em 270, como a 2. Um Ctrl+Z devolve a cada uma o giro que tinha."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela.ir_para_pagina(0)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()     # só esta página
    assert _giros(projeto) == [90, 0, 0, 0, 0]
    tela.ir_para_pagina(1)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert _giros(projeto) == [270, 270, 270, 270, 0]
    # D-640 (06/11; troca autorizada pelo Samuel, Central girar-capa-testes-antigos, 07/11): a folha inteira gira junto e conta na frase
    assert "todas as 5 páginas, viradas como a página 2" in janela.acoes.feitas[-1].descricao
    tela.desfazer()
    assert _giros(projeto) == [90, 0, 0, 0, 0]
    janela.menu.acoes["refazer"].trigger()
    assert _giros(projeto) == [270, 270, 270, 270, 0]


def test_d636_o_corte_a_mao_de_cada_pagina_gira_junto(janela, tmp_path):
    """O corte à mão de cada página girada continua sobre o mesmo pedaço do papel (cada uma
    pelo quanto ela girou); o Ctrl+Z devolve o corte de antes."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    projeto.paginas[0].giro_da_pagina = 90                  # a 1 já deitada: gira 180 até 270
    projeto.paginas[0].recorte = (0.1, 0.2, 0.5, 0.6)
    projeto.paginas[3].recorte = (0.05, 0.1, 0.8, 0.7)      # a 4 em pé: gira 270
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert list(projeto.paginas[0].recorte) == girar.recorte_girado((0.1, 0.2, 0.5, 0.6), 180)
    assert list(projeto.paginas[3].recorte) == girar.recorte_girado((0.05, 0.1, 0.8, 0.7), 270)
    tela.desfazer()
    assert tuple(projeto.paginas[0].recorte) == (0.1, 0.2, 0.5, 0.6)
    assert tuple(projeto.paginas[3].recorte) == (0.05, 0.1, 0.8, 0.7)
    assert _giros(projeto) == [90, 0, 0, 0, 0]


def test_d636_folha_inteira_fica_como_esta(janela, tmp_path):
    """Na folha inteira (página 5), "todas as folhas" gira as folhas, como hoje (D-636: "Folha
    inteira (não dividida): fica como está"; o que isso faz nas folhas divididas é a pergunta 3
    do ONDE-PAREI)."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela.ir_para_pagina(4)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    # D-638 (06/11; troca autorizada pelo Samuel, Central girar-capa-testes-antigos, 07/11): as folhas divididas giram página por página; a inteira gira inteira
    assert _rotacoes(projeto) == [0, 0, 90] and _giros(projeto) == [90, 90, 90, 90, 0]


# --- o PDF que sai ------------------------------------------------------------------------------

def test_d636_o_pdf_sai_com_cada_pagina_deitada_inteira(janela, tmp_path):
    """O PDF: com "todas as páginas" + ¼ à esquerda, as páginas 1 a 4 saem deitadas, cada uma a
    MESMA imagem que sairia sem o giro, girada (nenhuma com pedaço da vizinha); a 5 sai igual."""
    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)

    def gerar(nome):
        copia = copy.copy(projeto)
        copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
        return _paginas_do_pdf(pipeline.processar(copia))

    antes = gerar("antes")
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    depois = gerar("depois")
    assert len(antes) == len(depois) == 5
    for i in range(4):
        girada = girar_90(antes[i], girar.GIRO_ESQUERDA)
        assert girada.shape == depois[i].shape, i
        diferenca = np.abs(girada.astype(int) - depois[i].astype(int)).mean()
        assert diferenca < 3, (i, diferenca)
    # D-640 (06/11; troca autorizada pelo Samuel, Central girar-capa-testes-antigos, 07/11): a folha inteira (página 5) também sai girada, inteira
    girada = girar_90(antes[4], girar.GIRO_ESQUERDA)
    assert girada.shape == depois[4].shape
    assert np.abs(girada.astype(int) - depois[4].astype(int)).mean() < 3
