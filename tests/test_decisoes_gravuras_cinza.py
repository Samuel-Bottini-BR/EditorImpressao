"""D-588 (Samuel, 01/11/2026): a caixinha "Gravuras em tons de cinza" no Preto e branco.

Palavras dele:
  - 29/10, na capa do *Na escola de Jesus* em Preto e branco: "onde está a opção que deixa só
    cinza e branco ,essa parece que está dando um negativo".
  - 01/11, depois de tentar o cinza que existe hoje: "está muito confuso e não deu certo,
    coloque um agente para fazer isso".
  - Pergunta da gerente → "ok": "Uma caixinha "Gravuras em tons de cinza" no Preto e branco.
    Ela fica no painel Filtro, na tela cheia dos filtros e no "Limpar a folha" do Automático.
    Marcada, toda gravura achada sai cinza, mesmo quando o programa acha que é um enfeite, como
    na capa do *Na escola de Jesus*. Ela segue o "Aplicar em" (só nesta, todas, daqui em
    diante), como as outras opções."

O que estas provas guardam:
  1. a caixinha, com esse nome, no painel Filtro (logo abaixo da "Respeitar as gravuras
     achadas"), só no Preto e branco, desmarcada de fábrica;
  2. marcada → a gravura que a conta toma por enfeite (a iluminura colorida do livro de teste,
     o caso da D-585) sai em TONS DE CINZA (nenhum ponto colorido, muitos tons do meio: nem cor
     nem 1 bit, D-147); o texto continua preto e branco; a tela mostra esse desenho (D-473);
  3. desmarcada → igual ao de antes, byte a byte (marcar e desmarcar volta ao mesmo desenho;
     a conta com a caixinha desmarcada é a de sempre; a prova entre commits, contra o
     `7fb6e19`, está em relatorios/gravuras-cinza/identica-ao-7fb6e19.txt);
  4. "Aplicar em: todas" e "daqui em diante" levam a caixinha às outras páginas;
  5. Ctrl+Z desfaz e Ctrl+Shift+Z refaz (D-020);
  6. tela = PDF (D-066/D-473), e o "antes / depois" segue a caixinha;
  7. a caixinha na tela cheia dos filtros (D-192), com o mesmo nome, e o "Usar" a grava;
  8. a caixinha no "Limpar a folha" do Automático (D-594), com o mesmo nome, só no Preto e
     branco; rodar com ela grava nas páginas e a gravura sai cinza;
  9. no padrão da D-168/D-587 (PERGUNTA ao Samuel no ONDE-PAREI): com "Só as letras" ou com
     "Respeitar as gravuras achadas" desligada, a caixinha fica cinza e volta como estava;
 10. projeto gravado antes abre desmarcado e sai idêntico.

Livro sintético e caminho inteiro: os de tests/test_decisoes_respeitar_gravuras.py (papel
amarelado, iluminura grande colorida achada pela máquina, origem "rede", texto embaixo; o
Automático roda com Endireitar, Cortar as bordas e Limpar a folha). Reversão (§4.7): no
`7fb6e19` (antes da caixinha) estas provas falham
(relatorios/gravuras-cinza/reversao-no-7fb6e19.txt).
"""

from __future__ import annotations

import copy
import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests import test_decisoes_respeitar_gravuras as R  # noqa: E402
from tests.test_decisoes_respeitar_gravuras import (  # noqa: E402,F401 - fixtures
    _assentar, _bgr, _colorido, _depois_do_automatico, _desenho, _diferenca, _esperar,
    _escolher, _gerar, _miolo_da_iluminura, _pixmap_bgr, app, janela, pasta)

NOME = "Gravuras em tons de cinza"


def _caixa(tela):
    return tela.caixa_gravuras_cinza


def _meio_tons(img: np.ndarray) -> float:
    """Fração dos pontos de tom do meio (nem preto nem branco): a pintura em tons de cinza tem
    muitos; o desenho em 1 bit (preto e branco) não tem nenhum."""
    cinza = cv2.cvtColor(_bgr(img), cv2.COLOR_BGR2GRAY)
    return float(((cinza > 10) & (cinza < 245)).mean())


def _texto(img: np.ndarray) -> np.ndarray:
    """As linhas de "texto" embaixo (pega pela fração: o Automático pode ter cortado)."""
    h, w = img.shape[:2]
    return img[int(h * 0.76):int(h * 0.9), int(w * 0.25):int(w * 0.75)]


def _e_tons_de_cinza(img: np.ndarray) -> bool:
    miolo = _miolo_da_iluminura(img)
    return _colorido(miolo) == 0.0 and _meio_tons(miolo) > 0.5


# --- 0. a conta, sem janela ---------------------------------------------------------------

def test_d588_a_conta_toda_gravura_em_tons_de_cinza_e_o_texto_preto_e_branco():
    """A conta do Preto e branco com a marcação da máquina: sem a escolha, a iluminura (que a
    conta toma por enfeite colorido: D-144/D-585) sai com a cor; com ela, em tons de cinza (o
    cinza da D-147: nenhum ponto colorido, muitos tons do meio, não 1 bit); o texto, preto e
    branco nos dois (só 0 e 255)."""
    from core.filtros import aplicar_filtro_com_selecao

    img = R._pagina()
    marcacao = R._marcacao_da_maquina()
    sem, mono_sem = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, marcacao)
    com, mono_com = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, marcacao, gravuras_em_cinza=True)
    assert _colorido(_miolo_da_iluminura(sem)) > 0.5, "sem a escolha, o enfeite perdeu a cor"
    assert com.ndim == 2 and not mono_com and not mono_sem
    assert _e_tons_de_cinza(com), "com a escolha, a gravura não saiu em tons de cinza"
    for saida in (sem, com):
        texto = cv2.cvtColor(_bgr(saida), cv2.COLOR_BGR2GRAY)[600:780, 110:490]
        assert set(np.unique(texto).tolist()) <= {0, 255}, "o texto deixou de ser preto e branco"
    # desligada, a conta é a de sempre (sem o argumento)
    sem2, _ = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, marcacao, gravuras_em_cinza=False)
    assert np.array_equal(sem, sem2)
    # só vale no Preto e branco
    a, _ = aplicar_filtro_com_selecao(img, MELHORAR, marcacao)
    b, _ = aplicar_filtro_com_selecao(img, MELHORAR, marcacao, gravuras_em_cinza=True)
    assert np.array_equal(a, b)


# --- 1 e 2. a caixinha no painel; marcada → tons de cinza; a tela mostra -----------------------

def test_d588_caixinha_no_painel_so_no_preto_e_branco_desmarcada_de_fabrica(janela, tmp_path):
    """"Uma caixinha "Gravuras em tons de cinza" no Preto e branco. Ela fica no painel
    Filtro": com esse nome, logo abaixo da "Respeitar as gravuras achadas", desmarcada em toda
    página; só aparece com o Preto e branco escolhido."""
    from PySide6.QtWidgets import QCheckBox

    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    painel = tela.paineis.filtro_da_pagina
    caixa = _caixa(tela)
    assert isinstance(caixa, QCheckBox) and caixa.text() == NOME and caixa.toolTip()
    itens = [painel.dentro.itemAt(i).widget() for i in range(painel.dentro.count())]
    assert itens.index(caixa) == itens.index(tela.caixa_respeitar_gravuras) + 1
    assert all(p.gravuras_em_tons_de_cinza is False for p in projeto.paginas)
    for filtro, visivel in ((ORIGINAL, False), (MELHORAR, False), (PRETO_E_BRANCO, True)):
        _escolher(tela, filtro)
        assert caixa.isVisibleTo(tela) is visivel, filtro
    assert not caixa.isChecked() and caixa.isEnabled()


def test_d588_marcada_a_gravura_achada_sai_cinza_desmarcada_volta_igual(janela, tmp_path):
    """"Marcada, toda gravura achada sai cinza, mesmo quando o programa acha que é um enfeite,
    como na capa do *Na escola de Jesus*." Página em Preto e branco depois do Automático, com a
    iluminura achada pela máquina (que a conta toma por enfeite e deixa com a cor):
      - desmarcada → a iluminura com a cor (como hoje);
      - marcada (clique de verdade) → a iluminura em tons de cinza, o texto preto e branco, e a
        tela mostra esse desenho (D-473); só esta página muda;
      - desmarcada de novo → o desenho da primeira vez, byte a byte."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    dpi = tela._dpi_atual
    editor = tela.editor_selecao
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia em Preto e branco")
    antes = _desenho(projeto, pagina, dpi)
    assert _colorido(_miolo_da_iluminura(antes)) > 0.5, "o enfeite já não tinha cor (a prova não vale)"

    _caixa(tela).click()
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is True and _caixa(tela).isChecked()
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia com a caixinha marcada")
    marcada = _desenho(projeto, pagina, dpi)
    assert _e_tons_de_cinza(marcada), "marcada, a gravura não saiu em tons de cinza"
    assert _colorido(marcada) == 0.0, "sobrou cor na página"
    assert _meio_tons(_texto(marcada)) < 0.02, "o texto deixou de ser preto e branco"
    assert _diferenca(_bgr(editor._img), marcada) < 0.5, "a tela não mostra o desenho"
    assert _e_tons_de_cinza(_bgr(editor._img))
    assert all(not p.gravuras_em_tons_de_cinza for p in projeto.paginas[1:]), "mudou outra página"

    _caixa(tela).click()
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is False
    assert np.array_equal(_desenho(projeto, pagina, dpi), antes), "desmarcada não voltou igual"
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia desmarcada")
    assert _diferenca(_bgr(editor._img), antes) < 0.5


def test_d588_desmarcada_e_a_conta_de_antes_byte_a_byte(janela, tmp_path, monkeypatch):
    """"Desmarcada: tudo como hoje". Nos quatro filtros, a página com a caixinha desmarcada sai
    igual ponto por ponto ao desenho em que a conta nem recebe a escolha (o filtro de antes,
    sem o argumento novo). A prova entre commits está em
    relatorios/gravuras-cinza/identica-ao-7fb6e19.txt."""
    from core import filtros, pipeline

    _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    original = filtros.aplicar_filtro_com_selecao

    def sem_a_escolha(*args, **kwargs):
        assert kwargs.pop("gravuras_em_cinza", False) is False
        return original(*args, **kwargs)

    for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR):
        pagina.filtro = filtro
        agora = _desenho(projeto, pagina, 110)
        with monkeypatch.context() as m:
            m.setattr(pipeline, "aplicar_filtro_com_selecao", sem_a_escolha)
            assert np.array_equal(agora, _desenho(projeto, pagina, 110)), filtro


def test_d588_reversao_pela_imagem_a_capa_com_a_escolha_gravada(janela, tmp_path):
    """Reversão pela IMAGEM (§4.7: "Bug de imagem usa uma medida que pega o defeito"): a
    escolha gravada direto na página (como o projeto.json a guarda), sem passar pela tela.
    Medida: no miolo da gravura que a conta toma por enfeite, a fração de pontos coloridos tem
    de ser 0 e a de tons do meio maior que 50%. No código de antes (`7fb6e19`) a escolha não
    existe e a gravura sai colorida (o defeito da D-585 sem saída: "está muito confuso e não
    deu certo"); a prova acusa ali (relatorios/gravuras-cinza/reversao-no-7fb6e19.txt)."""
    _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    pagina.filtro = PRETO_E_BRANCO
    assert _colorido(_miolo_da_iluminura(_desenho(projeto, pagina, 110))) > 0.5
    pagina.gravuras_em_tons_de_cinza = True
    img = _desenho(projeto, pagina, 110)
    miolo = _miolo_da_iluminura(img)
    assert _colorido(miolo) == 0.0, f"a gravura continua colorida ({_colorido(miolo):.0%} dos pontos)"
    assert _meio_tons(miolo) > 0.5, "a gravura não saiu em tons de cinza"


# --- 4. "Aplicar em" ------------------------------------------------------------------------

@pytest.mark.parametrize("alcance", ["todas", "daqui em diante"])
def test_d588_aplicar_em_leva_a_caixinha(janela, tmp_path, alcance):
    """"Ela segue o "Aplicar em" (só nesta, todas, daqui em diante)": na página 2 em Preto e
    branco, marcar a caixinha e apertar "todas" (ou "daqui em diante") → as páginas alcançadas
    ficam marcadas (as de antes, no "daqui em diante", não) e a gravura delas sai cinza."""
    from PySide6.QtWidgets import QPushButton

    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    assert [p.gravuras_em_tons_de_cinza for p in projeto.paginas] == [False, True, False]
    botao = next(b for b in tela.paineis.filtro_da_pagina.findChildren(QPushButton)
                 if b.text() == alcance)
    botao.click()
    _assentar()
    esperado = {"todas": [True, True, True], "daqui em diante": [False, True, True]}[alcance]
    assert [p.gravuras_em_tons_de_cinza for p in projeto.paginas] == esperado
    terceira = projeto.paginas[2]
    assert terceira.filtro == PRETO_E_BRANCO
    assert _e_tons_de_cinza(_desenho(projeto, terceira, 110))
    # "só nesta" não leva para as outras (é o "Marcar como revisada" da página)
    if alcance == "daqui em diante":
        assert projeto.paginas[0].gravuras_em_tons_de_cinza is False


# --- 5. Ctrl+Z / Ctrl+Shift+Z -----------------------------------------------------------------

def test_d588_ctrl_z_desfaz_e_ctrl_shift_z_refaz(janela, tmp_path):
    """D-020: marcar a caixinha é uma ação do Histórico; Ctrl+Z desfaz e Ctrl+Shift+Z refaz, e
    a caixinha na tela acompanha."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _depois_do_automatico(janela, tmp_path)
    pagina = janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is True
    assert NOME in janela.acoes.feitas[-1].descricao
    janela.show()
    janela.move(-3000, -3000)
    janela.activateWindow()
    _assentar()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier)
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is False and not _caixa(tela).isChecked()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier | Qt.ShiftModifier)
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is True and _caixa(tela).isChecked()


# --- 6. tela = PDF; "antes / depois" ------------------------------------------------------------

def test_d588_o_pdf_sai_como_a_tela(janela, tmp_path):
    """D-066/D-473: página 1 em Preto e branco com a caixinha marcada e página 2 em Preto e
    branco sem ela → no PDF a gravura da 1 sai em tons de cinza e a da 2 com a cor; cada página
    do PDF é o desenho do tamanho do PDF (o que a tela mostra, reduzido)."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    assert [p.gravuras_em_tons_de_cinza for p in projeto.paginas[:2]] == [True, False]
    dpi = int(projeto.qualidade_dpi)
    paginas = _gerar(projeto, tmp_path, "saida", dpi)
    miolo = _miolo_da_iluminura(paginas[0])
    assert _colorido(miolo) < 0.001 and _meio_tons(miolo) > 0.5, "no PDF a 1 não saiu em tons de cinza"
    assert _colorido(_miolo_da_iluminura(paginas[1])) > 0.5, "no PDF a página 2 perdeu a cor"
    for k in (0, 1):
        desenho = _desenho(projeto, projeto.paginas[k], dpi)
        no_pdf = paginas[k]
        if no_pdf.shape != desenho.shape:
            no_pdf = cv2.resize(no_pdf, (desenho.shape[1], desenho.shape[0]),
                                interpolation=cv2.INTER_AREA)
        assert _diferenca(no_pdf, desenho) < 3.0, f"a página {k + 1} do PDF não é a da tela"


def test_d588_antes_depois_segue_a_caixinha(janela, tmp_path):
    """O lado "depois" do "antes / depois" segue a caixinha: marcada, a gravura em tons de
    cinza; desmarcada, com a cor."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    vista = tela.vista_antes_depois
    tela.botao_antes_depois.click()
    dpi = tela._dpi_atual
    for marcada in (True, False):
        if _caixa(tela).isChecked() != marcada:
            _caixa(tela).click()
        _esperar(lambda: tela.previas.ja_pronta(0, dpi) is not None and vista.depois is not None
                 and vista.antes is not None, motivo="o antes e o depois")
        _assentar()
        depois = _pixmap_bgr(vista.depois)
        assert _diferenca(depois, _desenho(projeto, pagina, dpi)) < 0.5
        if marcada:
            assert _e_tons_de_cinza(depois)
        else:
            assert _colorido(_miolo_da_iluminura(depois)) > 0.5


# --- 7. tela cheia dos filtros ----------------------------------------------------------------

def test_d588_na_tela_cheia_dos_filtros(janela, tmp_path):
    """D-192 ("Tela cheia do Preto e branco → as mesmas opções do painel Filtro") e D-588 ("Ela
    fica [...] na tela cheia dos filtros"): a caixinha aparece com o mesmo nome no Preto e
    branco (não no Melhorar); marcá-la mostra a página grande com a gravura em tons de cinza
    sem mudar a página; "Usar" grava (uma ação do desfazer, como no painel)."""
    from ui.widgets.filtros_tela_cheia import DPI_DA_TELA_CHEIA, FiltrosEmTelaCheia

    tela = _depois_do_automatico(janela, tmp_path)
    pagina = janela.projeto.paginas[0]
    dialogo = FiltrosEmTelaCheia(tela)
    try:
        dialogo.escolher(MELHORAR)
        assert dialogo.caixa_gravuras_cinza.isHidden()
        dialogo.escolher(PRETO_E_BRANCO)
        caixa = dialogo.caixa_gravuras_cinza
        assert not caixa.isHidden() and caixa.text() == _caixa(tela).text() == NOME
        assert caixa.toolTip() == _caixa(tela).toolTip()
        assert not caixa.isChecked() and caixa.isEnabled()
        caixa.setChecked(True)
        assert dialogo.opcoes == {"gravuras_em_tons_de_cinza": True}
        assert pagina.gravuras_em_tons_de_cinza is False, "a página mudou antes do Usar"
        fim = time.monotonic() + 90
        vista = None
        while vista is None and time.monotonic() < fim:
            _assentar(2)
            vista = dialogo._imagem(PRETO_E_BRANCO)
        assert vista is not None, "a página grande não chegou"
        assert _e_tons_de_cinza(vista), "a tela cheia não mostra a gravura em tons de cinza"
        dialogo.usar()
    finally:
        if dialogo.isVisible():
            dialogo.reject()
    _assentar()
    assert pagina.filtro == PRETO_E_BRANCO and pagina.gravuras_em_tons_de_cinza is True
    assert _caixa(tela).isChecked()
    assert _e_tons_de_cinza(_desenho(janela.projeto, pagina, DPI_DA_TELA_CHEIA))
    tela.desfazer()
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is False


# --- 8. "Limpar a folha" do Automático ------------------------------------------------------

def test_d588_no_limpar_a_folha_do_automatico(janela, tmp_path):
    """D-594 ("todas as opções do Filtro, com os mesmos nomes") e D-588 ("Ela fica [...] no
    "Limpar a folha" do Automático"): na janela grande, a caixinha mora na página do "Limpar a
    folha", com o nome do painel, só no Preto e branco, desmarcada (receita "De fábrica");
    cinza com "Só as letras" ou com "Respeitar as gravuras achadas" desligada. Rodar o "Limpar
    a folha" no livro todo, em Preto e branco, com ela marcada → todas as páginas ficam
    marcadas e a gravura sai em tons de cinza; os dois lados do "comparar" usam o mesmo painel
    (PainelDeOpcoes), então têm a caixinha também."""
    from core import automatico as A
    from ui.automatico import EstadoDoAutomatico, PainelDeOpcoes

    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    grande = janela.abrir_o_automatico()
    assert grande is not None
    _assentar()
    caixa = grande.cx_gravuras_cinza
    assert caixa.text() == _caixa(tela).text() == NOME
    assert grande.paginas_das_etapas[A.LIMPAR].isAncestorOf(caixa)
    assert grande.controles["gravuras_em_tons_de_cinza"] is caixa
    assert grande.estado.opcoes["gravuras_em_tons_de_cinza"] is False
    e = grande.estado
    for filtro in (ORIGINAL, MELHORAR):
        e.definir_opcao("filtro_padrao", filtro)
        assert caixa.isHidden(), filtro
    e.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    assert not caixa.isHidden() and caixa.isEnabled()
    e.definir_opcao("misto_so_as_letras", True)
    assert not caixa.isEnabled()
    e.definir_opcao("misto_so_as_letras", False)
    e.definir_opcao("respeitar_gravuras_achadas", False)
    assert not caixa.isEnabled()
    e.definir_opcao("respeitar_gravuras_achadas", True)
    assert caixa.isEnabled()
    # o "comparar": o mesmo painel, com a caixinha
    lado = PainelDeOpcoes(EstadoDoAutomatico(), vertical=True)
    assert lado.controles["gravuras_em_tons_de_cinza"].text() == NOME
    # rodar
    e.marcadas = {A.LIMPAR}
    caixa.setChecked(True)
    assert e.opcoes["gravuras_em_tons_de_cinza"] is True
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar()
    assert all(p.filtro == PRETO_E_BRANCO for p in projeto.paginas)
    assert all(p.gravuras_em_tons_de_cinza is True for p in projeto.paginas)
    for pagina in projeto.paginas:
        pagina.guardar_selecao(R._marcacao_da_maquina(), provisoria=False)
        pagina.gravura_feita_com = ""
    assert _e_tons_de_cinza(_desenho(projeto, projeto.paginas[1], 110))


# --- 9. no padrão da D-168/D-587 (pergunta ao Samuel) ------------------------------------------

def test_d588_cinza_com_so_as_letras_e_com_respeitar_desligada_e_volta(janela, tmp_path):
    """No padrão da D-168 e da D-587 ("Fica apagada (cinza) enquanto 'Só as letras' estiver
    marcada, e volta como estava ao desligar"), à espera da resposta do Samuel (ONDE-PAREI):
      - com "Só as letras" ligada, a caixinha fica cinza, o valor guardado não muda e a
        iluminura guarda a cor (D-148);
      - com "Respeitar as gravuras achadas" desligada (D-586), não há gravura achada para
        pintar: a caixinha fica cinza e a página sai toda em preto e branco, como sem ela;
      - desfeito cada um, a caixinha volta clicável e marcada, e a gravura volta a sair cinza."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    caixa = _caixa(tela)
    caixa.click()
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is True
    # "Só as letras"
    R._caixa_so_as_letras(tela).click()
    _assentar()
    assert pagina.misto_so_as_letras is True
    assert not caixa.isEnabled() and caixa.isChecked()
    QTest.mouseClick(caixa, Qt.LeftButton)
    _assentar()
    assert pagina.gravuras_em_tons_de_cinza is True
    projeto.misto_fora_do_texto = "tudo"           # sem o leitor de texto (lento)
    pagina.misto_fora_do_texto = "tudo"
    assert _colorido(_miolo_da_iluminura(_desenho(projeto, pagina, 110))) > 0.5
    R._caixa_so_as_letras(tela).click()
    _assentar()
    assert pagina.misto_so_as_letras is False
    assert caixa.isEnabled() and caixa.isChecked()
    # "Respeitar as gravuras achadas" desligada
    tela.caixa_respeitar_gravuras.click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False
    assert not caixa.isEnabled() and caixa.isChecked()
    sem_achadas = _desenho(projeto, pagina, 110)
    assert _colorido(sem_achadas) == 0.0 and _meio_tons(_miolo_da_iluminura(sem_achadas)) < 0.05
    so_sem_achadas = copy.deepcopy(pagina)
    so_sem_achadas.gravuras_em_tons_de_cinza = False
    assert np.array_equal(sem_achadas, _desenho(projeto, so_sem_achadas, 110))
    tela.caixa_respeitar_gravuras.click()
    _assentar()
    assert caixa.isEnabled() and caixa.isChecked()
    assert _e_tons_de_cinza(_desenho(projeto, pagina, 110))


# --- 10. projeto antigo ---------------------------------------------------------------------

def test_d588_projeto_antigo_abre_desmarcado_e_sai_identico(janela, tmp_path):
    """"De fábrica: desmarcada": o projeto.json gravado antes da caixinha (sem a chave) abre com
    ela desmarcada e a página sai igual ponto por ponto; o projeto novo grava a chave."""
    from modelos import Projeto

    _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    dados = projeto.para_dicionario()
    assert all(p["gravuras_em_tons_de_cinza"] is False for p in dados["paginas"])
    for p in dados["paginas"]:
        del p["gravuras_em_tons_de_cinza"]
    antigo = Projeto.de_dicionario(copy.deepcopy(dados))
    assert all(p.gravuras_em_tons_de_cinza is False for p in antigo.paginas)
    assert np.array_equal(_desenho(antigo, antigo.paginas[0], 110),
                          _desenho(projeto, projeto.paginas[0], 110))
