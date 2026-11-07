"""D-638 e D-640 (Samuel, 06/11/2026): girar num livro dividido que tem uma folha inteira (a capa aberta).

D-638, pergunta B do agente girar-pagina: "Agora você está na capa inteira e escolhe girar "todas as
folhas". Hoje, as outras folhas do livro giram inteiras, e volta a confusão do seu print: cada página com
um pedaço da vizinha. Sugestão: elas giram página por página, sem confusão. Pode ser assim?" → "Pode ser,
mas isso vai acontecer se elas estiverem cortadas e se não estiverem cortadas né?"
Livro: "Estando numa folha inteira (ex.: a capa aberta), "todas as folhas", "daqui em diante", "só as
pares" e "só as ímpares" giram as folhas divididas página por página (cada página sozinha, como na
D-636), e as folhas não divididas giram inteiras, como hoje. Nenhuma página fica com pedaço da vizinha.
Vale com ou sem o corte das bordas."

D-640, pergunta A: "Você está numa página do miolo e escolhe girar "todas as páginas". Todas as páginas
do livro giram, menos a capa inteira, que fica como está. Pode ser assim?" → "Todas giram, mas porque a
capa inteira não gira?" → "Não sei o que responder - vamos deixar como gira todas as paginas".
Livro: "Numa folha dividida, "todas as páginas" gira também as folhas que não foram divididas, como a
capa aberta (inteira): todas giram."

Resposta do Samuel à pergunta 1 deste trabalho (Central, 07/11/2026): "No miolo, "daqui em diante",
"só as pares" e "só as ímpares" giram também a capa aberta?" → "Giram também": a folha inteira que fizer
parte do grupo escolhido gira também, inteira, como no "todas as páginas" (provas test_*_d640_* no
bloco "resposta do Samuel"; falham no código de 16e752e7).

Não podem mudar: D-618 / D-636 (numa folha dividida o girar vira só a página; cada página gira sozinha)
e o "girar - sim" (a folha inteira gira como uma foto, levando o corte à mão). Regra D-605: "coisas
novas não podem criar novos problemas".

Como fica para quem usa e no livro (D-637): relatorios/girar-capa/ONDE-PAREI.md.

Os testes de reversão (test_reversao_d638_*, test_reversao_d640_*) falham no código de antes
(obra-2026-10-26, 6904a634): lá, na capa, "todas as folhas" girava as FOLHAS divididas inteiras
(folha.rotacao muda e cada página vira meia folha deitada com pedaço da vizinha, a confusão do a-70); e
no miolo, "todas as páginas" deixava a capa sem girar.

O livro de teste: quatro folhas abertas. Folha 1 inteira (a capa aberta) e folha 2 inteira (um encarte,
para ter uma folha inteira par); folhas 3 e 4 divididas na dobra. Páginas: 1 (capa), 2 (encarte), 3 e 4
(folha 3), 5 e 6 (folha 4).
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
# o livro de teste e a janela, os mesmos das provas da D-618 / D-636
from tests.test_decisoes_girar_pagina import (  # noqa: E402,F401
    _folha_aberta,
    _paginas_do_pdf,
    _pdf,
    app,
    janela,
    pasta,
)

CAPA, ENCARTE = 0, 1                       # indices das paginas das folhas inteiras
METADES = [2, 3, 4, 5]                     # as paginas das folhas divididas


def _livro_com_a_capa_inteira(janela, tmp_path, ferramenta: str | None = None):
    """Abre o livro de quatro folhas abertas, divide as folhas 3 e 4 na dobra (o "dividir esta",
    sem a DLL) e escolhe a ferramenta (de fábrica: Cortar as bordas). Fica na página 1 (a capa)."""
    from ui.tela_conferir import FERRAMENTA_CORTAR

    janela.abrir_livro(_pdf(tmp_path / "aberto.pdf", [_folha_aberta()] * 4))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("dividir", "folha", [2], campos_para_dividir(projeto, 2, 0.5), "Dividir")
    tela._registrar("dividir", "folha", [3], campos_para_dividir(projeto, 3, 0.5), "Dividir")
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "inteira"), (1, "inteira"), (2, "esquerda"), (2, "direita"), (3, "esquerda"),
        (3, "direita")]
    tela.escolher_ferramenta(ferramenta or FERRAMENTA_CORTAR)
    tela.ir_para_pagina(CAPA)
    assert tela.indice_folha == 0 and tela._pagina_que_gira_sozinha() is None
    return tela, projeto


def _giros(projeto) -> list[int]:
    return [p.giro_da_pagina for p in projeto.paginas]


def _rotacoes(projeto) -> list[int]:
    return [f.rotacao for f in projeto.folhas]


def _girar(tela, alcance: str, giro: int) -> None:
    """O clique no Propriedades: escolhe o "aplicar em" e aperta o botão do giro."""
    tela.barra_girar.definir_alcance(alcance)
    tela.barra_girar.botoes_de_giro[giro].click()


def _tecla(tela, tecla) -> None:
    """Ctrl+<tecla> pela mesma porta das teclas da janela (TelaConferir.tratar_tecla)."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, tecla, Qt.ControlModifier))


def _ctrl_z(tela) -> None:
    from PySide6.QtCore import Qt

    _tecla(tela, Qt.Key_Z)


def _ctrl_y(tela) -> None:
    from PySide6.QtCore import Qt

    _tecla(tela, Qt.Key_Y)


# --- D-638: na capa (folha inteira), o "aplicar em" gira as folhas divididas página por página ----

def test_reversao_d638_na_capa_todas_as_folhas_gira_as_divididas_pagina_por_pagina(janela, tmp_path):
    """Na capa, "todas as folhas" + ¼ à esquerda: a capa e o encarte giram inteiros (como hoje); as
    folhas divididas NÃO giram como folha (a linha da divisão não muda) e cada página delas deita
    sozinha. Uma ação só. REVERSÃO: antes as quatro folhas giravam (rotacao 270) e as páginas não."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    linhas = [f.posicao_corte for f in projeto.folhas]
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]
    assert [f.posicao_corte for f in projeto.folhas] == linhas
    assert len(janela.acoes.feitas) == feitas + 1                     # uma ação só
    assert janela.acoes.feitas[-1].descricao == (
        "Girar ¼ à esquerda: todas as 4 folhas, viradas como a folha 1")


def test_reversao_d638_daqui_em_diante_na_folha_inteira(janela, tmp_path):
    """No encarte (folha 2, inteira), "daqui em diante" + ¼ à direita: o encarte gira inteiro; as
    folhas 3 e 4 (divididas) giram página por página; a capa (antes) não muda."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(ENCARTE)
    _girar(tela, girar.ALCANCE_DAQUI, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [0, 90, 0, 0]
    assert _giros(projeto) == [0, 0, 90, 90, 90, 90]


def test_reversao_d638_so_as_pares_na_folha_inteira(janela, tmp_path):
    """No encarte (folha 2, par), "só as pares" + meia volta: as folhas 2 e 4. O encarte gira
    inteiro; as duas páginas da folha 4 (dividida) giram cada uma sozinha; a folha 3 não muda."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(ENCARTE)
    _girar(tela, girar.ALCANCE_PARES, girar.GIRO_MEIA_VOLTA)
    assert _rotacoes(projeto) == [0, 180, 0, 0]
    assert _giros(projeto) == [0, 0, 0, 0, 180, 180]


def test_reversao_d638_so_as_impares_na_capa(janela, tmp_path):
    """Na capa (folha 1, ímpar), "só as ímpares" + ¼ à direita: as folhas 1 e 3. A capa gira
    inteira; as páginas da folha 3 giram cada uma sozinha; o encarte e a folha 4 não mudam."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    _girar(tela, girar.ALCANCE_IMPARES, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 0, 0, 0]
    assert _giros(projeto) == [0, 0, 90, 90, 0, 0]


def test_d638_so_as_pares_na_capa_avisa_e_nao_gira(janela, tmp_path):
    """D-036 continua: na capa (folha 1, ímpar), "só as pares" avisa "vá a uma folha par" e não
    gira nada (nem entra no histórico)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_PARES, girar.GIRO_DIREITA)
    assert janela.avisos[-1] == girar.AVISO_PARES_NA_IMPAR
    assert len(janela.acoes.feitas) == feitas
    assert _rotacoes(projeto) == [0] * 4 and _giros(projeto) == [0] * 6


def test_d638_todas_ficam_viradas_como_a_capa_e_o_ctrl_z_e_o_ctrl_y(janela, tmp_path):
    """D-035: a página 3 já estava ¼ à direita e a folha 2 meia volta; na capa, "todas as folhas"
    + ¼ à esquerda → todas ficam em 270, como a capa (as folhas inteiras na rotação, as páginas
    das divididas no giro delas). Ctrl+Z devolve a cada uma o que tinha; Ctrl+Y refaz."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)              # só esta página (D-618)
    tela.ir_para_pagina(ENCARTE)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_MEIA_VOLTA)           # só esta folha
    assert _giros(projeto) == [0, 0, 90, 0, 0, 0] and _rotacoes(projeto) == [0, 180, 0, 0]
    tela.ir_para_pagina(CAPA)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]
    _ctrl_z(tela)
    assert _giros(projeto) == [0, 0, 90, 0, 0, 0] and _rotacoes(projeto) == [0, 180, 0, 0]
    _ctrl_y(tela)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]


def test_d638_o_corte_a_mao_gira_junto_e_o_ctrl_z_devolve(janela, tmp_path):
    """O corte à mão continua sobre o mesmo pedaço do papel: o da capa gira com a folha ("girar -
    sim"), o de cada página dividida pelo quanto ELA girou. Ctrl+Z devolve os cortes."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    projeto.paginas[CAPA].recorte = (0.55, 0.1, 0.4, 0.8)
    projeto.paginas[2].giro_da_pagina = 90                  # a 3 já deitada: gira 180 até 270
    projeto.paginas[2].recorte = (0.1, 0.2, 0.5, 0.6)
    projeto.paginas[5].recorte = (0.05, 0.1, 0.8, 0.7)      # a 6 em pé: gira 270
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert list(projeto.paginas[CAPA].recorte) == girar.recorte_girado((0.55, 0.1, 0.4, 0.8), 270)
    assert list(projeto.paginas[2].recorte) == girar.recorte_girado((0.1, 0.2, 0.5, 0.6), 180)
    assert list(projeto.paginas[5].recorte) == girar.recorte_girado((0.05, 0.1, 0.8, 0.7), 270)
    _ctrl_z(tela)
    assert tuple(projeto.paginas[CAPA].recorte) == (0.55, 0.1, 0.4, 0.8)
    assert tuple(projeto.paginas[2].recorte) == (0.1, 0.2, 0.5, 0.6)
    assert tuple(projeto.paginas[5].recorte) == (0.05, 0.1, 0.8, 0.7)
    assert _giros(projeto) == [0, 0, 90, 0, 0, 0] and _rotacoes(projeto) == [0] * 4


@pytest.mark.parametrize("ferramenta", ["cortar", "endireitar"])
def test_d638_vale_com_e_sem_o_corte_das_bordas_na_tela(janela, tmp_path, ferramenta):
    """"Vale com ou sem o corte das bordas": na ferramenta Cortar as bordas e na Endireitar (onde a
    página não aparece cortada), o mesmo resultado."""
    from ui import tela_conferir

    nome = {"cortar": tela_conferir.FERRAMENTA_CORTAR,
            "endireitar": tela_conferir.FERRAMENTA_ENDIREITAR}[ferramenta]
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path, nome)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 90, 0, 0]
    assert _giros(projeto) == [0, 0, 90, 90, 90, 90]


def test_d638_so_esta_folha_na_capa_continua_girando_so_a_capa(janela, tmp_path):
    """O que já funcionava (D-053 / "girar - sim"): na capa, "só esta folha" e os botões do canto
    giram só a capa; nenhuma página dividida muda."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 0, 0, 0] and _giros(projeto) == [0] * 6
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.girar_do_canto.botoes_de_giro[girar.GIRO_DIREITA].click()   # o canto: só esta
    assert _rotacoes(projeto) == [180, 0, 0, 0] and _giros(projeto) == [0] * 6


# --- D-640: no miolo (folha dividida), "todas as páginas" gira também a capa inteira -------------

def test_reversao_d640_todas_as_paginas_gira_tambem_a_capa(janela, tmp_path):
    """Na página 3 (folha dividida), "todas as páginas" + ¼ à esquerda: cada página das folhas
    divididas deita sozinha (D-636) e a capa e o encarte (inteiros) giram a folha deles, como uma
    foto. Nenhuma folha dividida gira como folha; a capa não ganha giro de página. Uma ação só.
    REVERSÃO: antes a capa e o encarte ficavam como estavam (rotacao 0)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    assert tela._pagina_que_gira_sozinha() == 2
    linhas = [f.posicao_corte for f in projeto.folhas]
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]
    assert [f.posicao_corte for f in projeto.folhas] == linhas
    assert len(janela.acoes.feitas) == feitas + 1
    assert janela.acoes.feitas[-1].descricao == (
        "Girar ¼ à esquerda: todas as 6 páginas, viradas como a página 3")


def test_d640_ctrl_z_e_ctrl_y_devolvem_a_capa_e_as_paginas(janela, tmp_path):
    """Ctrl+Z devolve a capa, o encarte e cada página ao giro (e ao corte à mão) que tinham;
    Ctrl+Y refaz. A capa já estava ¼ à direita: termina virada como a página da vez (270)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)              # a capa: só esta folha
    projeto.paginas[CAPA].recorte = (0.1, 0.55, 0.8, 0.4)
    tela.ir_para_pagina(4)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]
    # a capa girou 180 (de 90 a 270): o corte à mão foi junto, sobre o mesmo pedaço do papel
    assert list(projeto.paginas[CAPA].recorte) == girar.recorte_girado((0.1, 0.55, 0.8, 0.4), 180)
    _ctrl_z(tela)
    assert _rotacoes(projeto) == [90, 0, 0, 0] and _giros(projeto) == [0] * 6
    assert tuple(projeto.paginas[CAPA].recorte) == (0.1, 0.55, 0.8, 0.4)
    _ctrl_y(tela)
    assert _rotacoes(projeto) == [270, 270, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 270, 270, 270]


# --- resposta do Samuel à pergunta 1 (Central, 07/11/2026): "Giram também" ----------------------
# Pergunta: "No miolo, "daqui em diante", "só as pares" e "só as ímpares" giram também a capa aberta?"
# → "Giram também". Estando numa página de folha dividida, a folha inteira que fizer parte do grupo
# escolhido gira também, inteira, como no "todas as páginas" (D-640). Par/ímpar: a mesma conta de
# páginas da D-636 (o número que a tela mostra, "página 1 de N"): a capa aberta é a página 1, ímpar.
# (Até 07/11 aqui havia a prova provisória "test_d640_as_outras_escolhas_do_miolo_continuam_como_antes",
# escrita nesta tarefa enquanto a pergunta estava aberta; trocada por estas.)

def test_reversao_d640_so_as_impares_no_miolo_gira_tambem_a_capa(janela, tmp_path):
    """Na página 3 (ímpar, folha dividida), "só as ímpares" + ¼ à direita: as páginas 1, 3 e 5. A
    capa (página 1) gira inteira; as páginas 3 e 5 giram sozinhas; o encarte (página 2, par) e as
    páginas 4 e 6 não mudam. Uma ação só. REVERSÃO: antes a capa ficava sem girar."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_IMPARES, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [90, 0, 0, 0]
    assert _giros(projeto) == [0, 0, 90, 0, 90, 0]
    assert len(janela.acoes.feitas) == feitas + 1
    assert janela.acoes.feitas[-1].descricao == (
        "Girar ¼ à direita: as 3 páginas ímpares, viradas como a página 3")


def test_reversao_d640_so_as_pares_no_miolo_gira_tambem_a_folha_inteira_par(janela, tmp_path):
    """Na página 4 (par), "só as pares" + meia volta: as páginas 2, 4 e 6. O encarte (página 2,
    folha inteira) gira inteiro; as páginas 4 e 6 sozinhas; a capa (página 1) não muda.
    REVERSÃO: antes o encarte ficava sem girar."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(3)
    _girar(tela, girar.ALCANCE_PARES, girar.GIRO_MEIA_VOLTA)
    assert _rotacoes(projeto) == [0, 180, 0, 0]
    assert _giros(projeto) == [0, 0, 0, 180, 0, 180]


def test_reversao_d640_daqui_em_diante_gira_a_folha_inteira_que_vem_depois(janela, tmp_path):
    """Livro com a folha inteira no FIM (folhas 1 e 2 divididas, folha 3 inteira, página 5): na
    página 3, "daqui em diante" + ¼ à direita → as páginas 3 e 4 sozinhas e a folha 3 inteira.
    As páginas 1 e 2 (antes) não mudam. REVERSÃO: antes a folha 3 ficava sem girar."""
    from tests.test_decisoes_girar_paginas_aplicar_em import _livro_com_duas_folhas_divididas

    tela, projeto = _livro_com_duas_folhas_divididas(janela, tmp_path)
    tela.ir_para_pagina(2)
    _girar(tela, girar.ALCANCE_DAQUI, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [0, 0, 90]
    assert _giros(projeto) == [0, 0, 90, 90, 0]
    assert janela.acoes.feitas[-1].descricao == (
        "Girar ¼ à direita: da página 3 em diante (3 páginas), viradas como a página 3")


def test_d640_daqui_em_diante_nao_volta_para_a_capa_que_ficou_antes(janela, tmp_path):
    """"daqui em diante" começa onde se está: na página 3, a capa e o encarte (páginas 1 e 2, antes)
    não giram; as páginas 3 a 6 giram sozinhas."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    _girar(tela, girar.ALCANCE_DAQUI, girar.GIRO_DIREITA)
    assert _rotacoes(projeto) == [0] * 4
    assert _giros(projeto) == [0, 0, 90, 90, 90, 90]


def test_d640_so_as_pares_na_pagina_impar_avisa_e_nao_gira_nada(janela, tmp_path):
    """D-036 continua: na página 3 (ímpar), "só as pares" avisa ("Você está numa página ímpar") e
    não gira nada, nem a folha inteira."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    feitas = len(janela.acoes.feitas)
    _girar(tela, girar.ALCANCE_PARES, girar.GIRO_DIREITA)
    assert janela.avisos[-1] == girar.AVISO_PARES_NA_IMPAR_GIRAR_PAGINA
    assert len(janela.acoes.feitas) == feitas
    assert _rotacoes(projeto) == [0] * 4 and _giros(projeto) == [0] * 6


def test_d640_impares_no_miolo_ctrl_z_e_ctrl_y_de_uma_vez(janela, tmp_path):
    """A capa tinha um corte à mão e já estava ¼ à direita; na página 5, "só as ímpares" + ¼ à
    esquerda → a capa fica virada como a página 5 (270), levando o corte; Ctrl+Z devolve tudo de
    uma vez (a capa, o corte e as páginas); Ctrl+Y refaz tudo."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)              # a capa: só esta folha
    projeto.paginas[CAPA].recorte = (0.1, 0.55, 0.8, 0.4)
    tela.ir_para_pagina(4)                                            # página 5, ímpar
    _girar(tela, girar.ALCANCE_IMPARES, girar.GIRO_ESQUERDA)
    assert _rotacoes(projeto) == [270, 0, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 0, 270, 0]
    assert list(projeto.paginas[CAPA].recorte) == girar.recorte_girado((0.1, 0.55, 0.8, 0.4), 180)
    _ctrl_z(tela)
    assert _rotacoes(projeto) == [90, 0, 0, 0] and _giros(projeto) == [0] * 6
    assert tuple(projeto.paginas[CAPA].recorte) == (0.1, 0.55, 0.8, 0.4)
    _ctrl_y(tela)
    assert _rotacoes(projeto) == [270, 0, 0, 0]
    assert _giros(projeto) == [0, 0, 270, 0, 270, 0]


def test_d640_so_esta_pagina_no_miolo_continua_girando_so_ela(janela, tmp_path):
    """D-618 continua: na página 4, "só esta página" gira só ela; a capa não muda."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(3)
    _girar(tela, girar.ALCANCE_ESTA, girar.GIRO_DIREITA)
    assert _giros(projeto) == [0, 0, 0, 90, 0, 0] and _rotacoes(projeto) == [0] * 4


# --- o PDF que sai: a capa e as páginas giradas como na tela ------------------------------------

def _gerar(projeto, tmp_path, nome: str, cortar: bool) -> list[np.ndarray]:
    copia = copy.copy(projeto)
    copia.cortar_bordas = cortar
    copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(pipeline.processar(copia))


def _confere_tudo_girado(antes, depois, giro: int) -> None:
    """Cada página do PDF de depois é a MESMA imagem de antes, girada (nenhuma com pedaço da
    vizinha)."""
    assert len(antes) == len(depois) == 6
    for i in range(6):
        girada = girar_90(antes[i], giro)
        assert girada.shape == depois[i].shape, i
        diferenca = np.abs(girada.astype(int) - depois[i].astype(int)).mean()
        assert diferenca < 3, (i, diferenca)


@pytest.mark.parametrize("cortar", [False, True])
def test_reversao_d638_o_pdf_sai_com_a_capa_e_cada_pagina_girada(janela, tmp_path, cortar):
    """O PDF (com e sem o corte das bordas): na capa, "todas as folhas" + ¼ à esquerda → a capa e
    o encarte saem girados, inteiros, e cada página das folhas divididas sai deitada, inteira, a
    mesma imagem de antes girada. REVERSÃO: antes as páginas divididas saíam como meia folha
    deitada (outra forma, com pedaço da vizinha)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    antes = _gerar(projeto, tmp_path, "antes", cortar)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    _confere_tudo_girado(antes, _gerar(projeto, tmp_path, "depois", cortar), girar.GIRO_ESQUERDA)
    _ctrl_z(tela)                                   # e o Ctrl+Z devolve o PDF de antes
    de_novo = _gerar(projeto, tmp_path, "de-novo", cortar)
    for a, b in zip(antes, de_novo):
        assert a.shape == b.shape and np.abs(a.astype(int) - b.astype(int)).mean() < 1


@pytest.mark.parametrize("cortar", [False, True])
def test_reversao_d640_o_pdf_sai_com_a_capa_girada(janela, tmp_path, cortar):
    """O PDF (com e sem o corte das bordas): na página 3, "todas as páginas" + ¼ à esquerda → a
    capa e o encarte saem girados, inteiros, e as páginas divididas deitadas, como na tela.
    REVERSÃO: antes a capa e o encarte saíam iguais (em pé, sem girar)."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    antes = _gerar(projeto, tmp_path, "antes", cortar)
    _girar(tela, girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA)
    _confere_tudo_girado(antes, _gerar(projeto, tmp_path, "depois", cortar), girar.GIRO_ESQUERDA)
    _ctrl_z(tela)
    _ctrl_y(tela)                                   # o Ctrl+Y refaz o mesmo PDF
    _confere_tudo_girado(antes, _gerar(projeto, tmp_path, "refeito", cortar), girar.GIRO_ESQUERDA)


@pytest.mark.parametrize("cortar", [False, True])
def test_reversao_d640_impares_o_pdf_sai_com_a_capa_girada(janela, tmp_path, cortar):
    """O PDF (com e sem o corte das bordas): na página 3, "só as ímpares" + ¼ à esquerda → a capa
    (página 1) e as páginas 3 e 5 saem giradas, cada uma a mesma imagem de antes girada; as páginas
    2, 4 e 6 saem iguais. Ctrl+Z e Ctrl+Y: o PDF volta e depois sai girado de novo. REVERSÃO: antes
    a capa saía sem girar."""
    tela, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    tela.ir_para_pagina(2)
    antes = _gerar(projeto, tmp_path, "antes", cortar)

    def confere(depois):
        assert len(depois) == 6
        for i in range(6):
            esperado = girar_90(antes[i], girar.GIRO_ESQUERDA) if i in (0, 2, 4) else antes[i]
            assert esperado.shape == depois[i].shape, i
            assert np.abs(esperado.astype(int) - depois[i].astype(int)).mean() < 3, i

    _girar(tela, girar.ALCANCE_IMPARES, girar.GIRO_ESQUERDA)
    confere(_gerar(projeto, tmp_path, "depois", cortar))
    _ctrl_z(tela)
    de_novo = _gerar(projeto, tmp_path, "de-novo", cortar)
    for a, b in zip(antes, de_novo):
        assert a.shape == b.shape and np.abs(a.astype(int) - b.astype(int)).mean() < 1
    _ctrl_y(tela)
    confere(_gerar(projeto, tmp_path, "refeito", cortar))


# --- as contas (core/girar.py), sem janela ------------------------------------------------------

def test_d638_as_contas_separam_folhas_inteiras_e_paginas_divididas(janela, tmp_path):
    """core/girar.campos_do_giro_numa_folha_inteira: as folhas inteiras do alcance ficam com a
    rotação final da folha da vez; as páginas das divididas, com o mesmo giro, cada uma sozinha."""
    _, projeto = _livro_com_a_capa_inteira(janela, tmp_path)
    rotacao, paginas = girar.campos_do_giro_numa_folha_inteira(
        projeto.folhas, projeto.paginas, [0, 1, 2, 3], girar.GIRO_DIREITA, 0)
    assert rotacao == {"0": 90, "1": 90}
    assert sorted(paginas) == METADES
    assert all(paginas[i]["giro_da_pagina"] == 90 for i in METADES)
