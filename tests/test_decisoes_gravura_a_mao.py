"""D-659 (Samuel, 09/11/2026): a gravura é procurada no Preto e branco escolhido À MÃO.

O defeito (teste do Samuel, 09/11/2026, sessão 4, página 8 do livro de 199 páginas): livro novo,
que nunca passou pelo Automático ("Livro novo: ainda não passou pelo automático"); na área de
trabalho, painel "Filtro da página", ele escolhe Preto e branco com "Respeitar as gravuras
achadas" e "Gravuras em tons de cinza" marcadas, e a gravura sai em manchas pretas (a página
inteira vira preto e branco). Na janela do Automático a mesma página sai certa. Palavras dele:
"isso é um grande erro". Causa: core/etapas.marca_sozinho devolvia False logo na primeira linha
com "Limpar a folha" desligado, antes de olhar a "procura por dentro"; nenhuma gravura era
procurada. As provas de antes começavam todas depois do Automático.

Palavras dele (D-659): "1- ele vai procurar a gravura quando eu selecionar a opção ali no filtro
né? e ai se eu selecionar para o livro todo ou para varias paginas, ele vai procurar nas paginas
especificas, não precisa procurar em todas." e "2- No caso de a opção ter sido selecionada sim,
vai procuar na pagina que está ou nas paginas que foram selecionadas entendeu?". Esclarecimento
(09/11): "se estamos no manual e eu estou fazendo ajustes em uma pagina, ele vai procurar só
naquela pagina se eu optar para que ele faça aquele ajuste em varias paginas ai sim o programa vai
ler as outras paginas, entendeu? isso para as duas opções."

O que estas provas guardam (todas num livro NOVO, sem o Automático, com o filtro escolhido pelo
painel, clique de verdade):
  0. a conta (core/etapas): quem procura e quem não procura, sem janela;
  a. "só nesta" com "Respeitar" (de fábrica, marcada) → a gravura achada é respeitada, igual ao
     filtro depois do Automático; só esta página é procurada (contadas);
  b. "Gravuras em tons de cinza" → a gravura em tons de cinza; só esta página;
  c. "Só as letras" → a gravura como no original; só esta página;
  d. "Aplicar em: todas" / "daqui em diante" → procura só nas páginas alcançadas (contadas);
  e. várias páginas escolhidas, uma a uma → só nelas (o filtro não tem "pares/ímpares" nem
     "pôr filtro" na grade: ver o ONDE-PAREI, ressalva 1);
  f. as três desmarcadas → nenhuma procura e a página igual à do código de antes, byte a byte;
  g. Melhorar / Mágico pro / Original à mão → nenhuma procura, igual ao de antes, byte a byte;
  h. a tela e o PDF saem iguais (D-473); Ctrl+Z / Ctrl+Shift+Z (D-020);
  i. depois, rodar o Automático no mesmo livro → a conta é a de antes em todas as páginas, a
     etapa 5 continua desmarcada.

"Igual ao de antes": o desenho com core/etapas.marca_sozinho e procura_por_dentro trocados pelas
do `a0c99cc7` (_DE_ANTES, abaixo), o código de antes do conserto.

O detector é trocado por um que devolve a marcação do livro de teste (a iluminura como gravura,
o texto como letra, origem "rede": tests/test_decisoes_respeitar_gravuras._marcacao_da_maquina) e
ANOTA a página procurada: o detector de verdade é lento e não é o assunto; a imagem do livro dele
(com o detector de verdade) está em relatorios/gravura-a-mao/. Reversão (§4.7): no `a0c99cc7`
estas provas falham (relatorios/gravura-a-mao/reversao-no-a0c99cc7.txt).
"""

from __future__ import annotations

import copy
import threading

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests import test_decisoes_respeitar_gravuras as R  # noqa: E402
from tests.test_decisoes_respeitar_gravuras import (  # noqa: E402,F401 - fixtures
    _assentar, _bgr, _colorido, _desenho, _diferenca, _esperar, _escolher, _gerar,
    _miolo_da_iluminura, app, janela, pasta)


# --- o código de antes (a0c99cc7), para as comparações "igual a hoje" ----------------------

def _marca_sozinho_de_antes(projeto, pagina=None) -> bool:
    """core/etapas.marca_sozinho como era no `a0c99cc7` (antes da D-659)."""
    from core import etapas as E

    if not E.limpa_sozinho(projeto, pagina):
        return False
    return bool(getattr(projeto, "detectar_regioes", False)) or _procura_por_dentro_de_antes(
        projeto, pagina)


def _procura_por_dentro_de_antes(projeto, pagina=None) -> bool:
    """core/etapas.procura_por_dentro como era no `a0c99cc7`."""
    from core import etapas as E

    return E.so_as_letras_procura(projeto, pagina) or E.cinza_procura(projeto, pagina)


def _com_o_codigo_de_antes(monkeypatch):
    """Um contexto em que core/etapas responde como no `a0c99cc7`."""
    from core import etapas as E

    contexto = monkeypatch.context()
    m = contexto.__enter__()
    m.setattr(E, "marca_sozinho", _marca_sozinho_de_antes)
    m.setattr(E, "procura_por_dentro", _procura_por_dentro_de_antes)
    return contexto


# --- o detector que anota quem foi procurado ---------------------------------------------------

@pytest.fixture
def procuradas(monkeypatch):
    """Troca o detector de gravura (core.detectar_regioes.detectar) por um que devolve a
    marcação do livro de teste e ANOTA o número da página procurada (o índice da página, de 0),
    em todos os fios (a prévia e o acerto por trás rodam em QThread). Devolve a lista."""
    from core import detectar_regioes, pipeline

    lista: list = []
    local = threading.local()
    original = pipeline.garantir_selecao

    def garantir(projeto, pagina, *args, **kwargs):
        pilha = getattr(local, "pilha", None)
        if pilha is None:
            pilha = local.pilha = []
        pilha.append(pagina.indice)
        try:
            return original(projeto, pagina, *args, **kwargs)
        finally:
            pilha.pop()

    def detectar(img, **kwargs):
        pilha = getattr(local, "pilha", None) or [None]
        lista.append(pilha[-1])
        return R._marcacao_da_maquina()

    monkeypatch.setattr(pipeline, "garantir_selecao", garantir)
    monkeypatch.setattr(detectar_regioes, "detectar", detectar)
    return lista


# --- o livro novo --------------------------------------------------------------------------

def _livro_novo(janela, tmp_path, folhas: int = 3):
    """O caminho do Samuel: abrir o livro e NÃO rodar o Automático (faixa "Livro novo: ainda não
    passou pelo automático"); Zoom, página 1, painel "Filtro da página" aberto."""
    from ui.tela_conferir import PAINEL_FILTRO

    janela.abrir_livro(R._pdf(tmp_path / "livro.pdf", folhas))
    projeto = janela.projeto
    assert not projeto.passou_pelo_automatico, "o livro já passou pelo Automático"
    assert not projeto.limpar, "o livro novo veio com o Limpar a folha ligado"
    assert not _etapa_5_ligada(projeto)
    tela = janela.tela_conferir
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(0)
    tela.paineis.abrir(PAINEL_FILTRO)
    _assentar()
    _esperar(lambda: tela.previas.ja_pronta(0, tela._dpi_atual) is not None, motivo="a prévia")
    return tela


def _etapa_5_ligada(projeto) -> bool:
    """A etapa 5 do Automático ("Gravuras e fotos") está ligada no livro? (core/automatico.
    ligada_no_livro: o "Procurar gravura e letra" com o "Limpar a folha"; no livro novo o
    detectar_regioes vem True de fábrica e o Limpar desligado: desligada)."""
    from core import automatico as A

    return A.ligada_no_livro(projeto, A.GRAVURAS)


def _previa_pronta(tela, indice: int, motivo: str) -> None:
    editor = tela.editor_selecao
    dpi = tela._dpi_atual
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(indice, dpi),
             motivo=motivo)


def _definitiva(pagina) -> bool:
    """A marcação da página já é a definitiva (achada no tamanho do PDF, por trás)."""
    return bool(pagina.selecao) and not getattr(pagina, "marcacao_provisoria", False)


def _caixa_respeitar(tela):
    return tela.caixa_respeitar_gravuras


def _caixa_cinza(tela):
    return tela.caixa_gravuras_cinza


def _caixa_so_as_letras(tela):
    from PySide6.QtWidgets import QCheckBox

    return next(c for c in tela.paineis.filtro_da_pagina.findChildren(QCheckBox)
                if c.text() == "Só as letras" and c.isVisibleTo(tela))


def _botao(tela, texto: str):
    from PySide6.QtWidgets import QPushButton

    return next(b for b in tela.paineis.filtro_da_pagina.findChildren(QPushButton)
                if b.text() == texto)


def _meio_tons(img: np.ndarray) -> float:
    cinza = cv2.cvtColor(_bgr(img), cv2.COLOR_BGR2GRAY)
    return float(((cinza > 10) & (cinza < 245)).mean())


def _como_no_automatico(projeto, pagina, dpi: int) -> np.ndarray:
    """A mesma página com o filtro do Automático: "Limpar a folha" e "Gravuras e fotos" ligados
    no livro, a mesma marcação (a que a página guarda). É o print 02 do Samuel."""
    copia = copy.deepcopy(projeto)
    copia.limpar = True
    copia.detectar_regioes = True
    return _desenho(copia, copia.paginas[pagina.indice], dpi)


def _procurar_no_pdf(projeto, tmp_path, procuradas, nome: str) -> set:
    """Gera o PDF (o "Confirmar e processar") e devolve as páginas procuradas nele."""
    antes = len(procuradas)
    _gerar(projeto, tmp_path, nome, 72)
    return set(procuradas[antes:])


# --- 0. a conta --------------------------------------------------------------------------------

def test_d659_a_conta_quem_procura_com_limpar_desligado():
    """A conta de core/etapas, sem janela, com "Limpar a folha" desligado (livro novo):
    procura só a página em Preto e branco ESCOLHIDO À MÃO (marca FILTRO) com uma das três
    caixinhas; a etapa 5 não é tocada. Com "Limpar a folha" ligado, a resposta é a de antes."""
    from core import etapas as E
    from modelos import ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.limpar = False
    projeto.detectar_regioes = False

    def pagina(filtro=PRETO_E_BRANCO, a_mao=True, **campos):
        p = ConfigPagina(indice=0, folha=0, filtro=filtro)
        if a_mao:
            E.marcar_mexida_a_mao(p, E.FILTRO)
        for campo, valor in campos.items():
            setattr(p, campo, valor)
        return p

    # procuram (D-659)
    assert E.marca_sozinho(projeto, pagina())                          # "Respeitar" de fábrica
    assert E.marca_sozinho(projeto, pagina(respeitar_gravuras_achadas=False,
                                           gravuras_em_tons_de_cinza=True))
    assert E.marca_sozinho(projeto, pagina(respeitar_gravuras_achadas=False,
                                           misto_so_as_letras=True))
    # não procuram
    assert not E.marca_sozinho(projeto, pagina(respeitar_gravuras_achadas=False))
    for filtro in (ORIGINAL, MELHORAR, MAGICO_PRO):
        assert not E.marca_sozinho(projeto, pagina(filtro=filtro)), filtro
        assert not E.marca_sozinho(projeto, pagina(filtro=filtro, gravuras_em_tons_de_cinza=True))
    assert not E.marca_sozinho(projeto, pagina(a_mao=False)), "Preto e branco sem a marca (D-009)"
    assert not E.marca_sozinho(projeto, None), "sem a página, nada"
    projeto.detectar_regioes = True                   # o de fábrica do livro novo
    assert E.marca_sozinho(projeto, pagina())
    assert not E.marca_sozinho(projeto, pagina(respeitar_gravuras_achadas=False))
    assert not E.marca_sozinho(projeto, pagina(filtro=MELHORAR))
    assert not _etapa_5_ligada(projeto), "a etapa 5 foi remarcada"

    # com "Limpar a folha" ligado: a conta de antes, em todos os casos
    projeto.limpar = True
    for detectar in (False, True):
        projeto.detectar_regioes = detectar
        for p in (pagina(), pagina(respeitar_gravuras_achadas=False),
                  pagina(respeitar_gravuras_achadas=False, gravuras_em_tons_de_cinza=True),
                  pagina(filtro=MELHORAR), pagina(a_mao=False)):
            assert E.marca_sozinho(projeto, p) == _marca_sozinho_de_antes(projeto, p)
            assert E.a_marcacao_da_maquina_vale(projeto, p) == (
                detectar or _procura_por_dentro_de_antes(projeto, p))


# --- a. "só nesta" com "Respeitar" ----------------------------------------------------------------

def test_d659_a_so_nesta_com_respeitar_a_gravura_e_respeitada_e_so_ela_e_procurada(
        janela, tmp_path, procuradas):
    """Livro novo, página 1, clique em Preto e branco ("Respeitar as gravuras achadas" já vem
    marcada, D-586): a gravura é procurada SÓ nesta página (na prévia e no acerto por trás), e
    sai respeitada (a iluminura com a cor, D-144), igual ao filtro do Automático (print 02);
    a tela mostra esse desenho. Andar pelas outras páginas não procura nelas, e o PDF também não
    ("vai procurar só naquela pagina"). A etapa 5 continua desmarcada."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    assert _caixa_respeitar(tela).isChecked() and pagina.respeitar_gravuras_achadas
    assert procuradas == [], "procurou antes de escolher o filtro"

    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: _definitiva(pagina), motivo="a gravura achada no tamanho do PDF")
    _previa_pronta(tela, 0, "a prévia em Preto e branco")
    assert set(procuradas) == {0}, f"procurou em outras páginas: {procuradas}"

    dpi = tela._dpi_atual
    agora = _desenho(projeto, pagina, dpi)
    assert _colorido(_miolo_da_iluminura(agora)) > 0.5, "a gravura não foi respeitada (manchas)"
    assert np.array_equal(agora, _como_no_automatico(projeto, pagina, dpi)), \
        "não saiu igual ao filtro do Automático"
    _esperar(lambda: tela.editor_selecao._img is not None
             and _diferenca(_bgr(tela.editor_selecao._img), agora) < 0.5,
             motivo="a tela mostrar o desenho com a gravura respeitada")

    procuradas.clear()
    for indice in (1, 2, 0):
        tela.ir_para_pagina(indice)
        _assentar()
        _esperar(lambda i=indice: tela.previas.ja_pronta(i, tela._dpi_atual) is not None,
                 motivo=f"a prévia da página {indice + 1}")
    assert procuradas == [], f"andar pelas páginas procurou: {procuradas}"
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "a") <= {0}
    assert not any(p.selecao for p in projeto.paginas[1:]), "outra página ganhou marcação"
    assert not _etapa_5_ligada(projeto), "a etapa 5 foi remarcada"


# --- b. "Gravuras em tons de cinza" -------------------------------------------------------------

def test_d659_b_so_nesta_com_o_cinza_a_gravura_sai_em_tons_de_cinza(janela, tmp_path, procuradas):
    """Preto e branco e "Gravuras em tons de cinza" (com "Respeitar" desmarcada, o caso do
    conserto de 02/11: "por gravuras em tons de cinza sozinho já deveria resolver o problema"):
    a gravura sai em tons de cinza, igual ao Automático; só esta página é procurada."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    _caixa_respeitar(tela).click()
    _assentar()
    _caixa_cinza(tela).click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False and pagina.gravuras_em_tons_de_cinza is True
    _esperar(lambda: _definitiva(pagina), motivo="a gravura achada no tamanho do PDF")
    _previa_pronta(tela, 0, "a prévia com o cinza")
    assert set(procuradas) == {0}, f"procurou em outras páginas: {procuradas}"
    dpi = tela._dpi_atual
    agora = _desenho(projeto, pagina, dpi)
    miolo = _miolo_da_iluminura(agora)
    assert _colorido(miolo) == 0.0 and _meio_tons(miolo) > 0.5, "a gravura não saiu em tons de cinza"
    assert np.array_equal(agora, _como_no_automatico(projeto, pagina, dpi))
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "b") <= {0}


# --- c. "Só as letras" -----------------------------------------------------------------------------

def test_d659_c_so_nesta_com_so_as_letras_a_gravura_sai_como_no_original(
        janela, tmp_path, procuradas):
    """Preto e branco e "Só as letras" (D-148: gravura como no original; D-589: "procura as
    figuras por dentro"), com "Respeitar" desmarcada antes (para a procura vir só do "Só as
    letras"): a gravura sai colorida, igual ao Automático; só esta página é procurada."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    _caixa_respeitar(tela).click()
    _assentar()
    # sem o leitor de texto (lento, não é o assunto): como em test_decisoes_respeitar_gravuras
    projeto.misto_fora_do_texto = "tudo"
    pagina.misto_fora_do_texto = "tudo"
    _caixa_so_as_letras(tela).click()
    _assentar()
    assert pagina.misto_so_as_letras is True and pagina.respeitar_gravuras_achadas is False
    _esperar(lambda: _definitiva(pagina), motivo="a gravura achada no tamanho do PDF")
    assert set(procuradas) == {0}, f"procurou em outras páginas: {procuradas}"
    dpi = tela._dpi_atual
    agora = _desenho(projeto, pagina, dpi)
    assert _colorido(_miolo_da_iluminura(agora)) > 0.5, "a gravura não saiu como no original"
    assert np.array_equal(agora, _como_no_automatico(projeto, pagina, dpi))
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "c") <= {0}


# --- d. "Aplicar em" ---------------------------------------------------------------------------------

@pytest.mark.parametrize("alcance, esperado", [("todas", {0, 1, 2, 3}),
                                               ("daqui em diante", {1, 2, 3})])
def test_d659_d_aplicar_em_procura_so_nas_paginas_alcancadas(
        janela, tmp_path, procuradas, alcance, esperado):
    """"se eu selecionar para o livro todo ou para varias paginas, ele vai procurar nas paginas
    especificas": na página 2 de 4, Preto e branco ("só nesta": só a 2 é procurada), depois
    "todas" ou "daqui em diante" → no PDF, as páginas procuradas são exatamente as alcançadas
    (no "daqui em diante" a página 1 nunca é procurada) e todas elas saem com a gravura
    respeitada."""
    tela = _livro_novo(janela, tmp_path, folhas=4)
    projeto = janela.projeto
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: _definitiva(projeto.paginas[1]), motivo="a página 2 procurada")
    assert set(procuradas) == {1}, f"só nesta: procurou em {procuradas}"

    _botao(tela, alcance).click()
    _assentar()
    assert {p.indice for p in projeto.paginas if p.filtro == PRETO_E_BRANCO} == esperado
    no_pdf = _procurar_no_pdf(projeto, tmp_path, procuradas, "d")
    assert set(procuradas) <= esperado, f"procurou fora do alcance: {procuradas}"
    assert no_pdf | {1} == esperado, f"no PDF, procuradas {no_pdf}; esperado {esperado}"
    paginas = _gerar(projeto, tmp_path, "d2", 72)
    for indice in range(4):
        colorida = _colorido(_miolo_da_iluminura(paginas[indice])) > 0.5
        assert colorida, f"página {indice + 1}"     # fora do alcance é o Original (colorido)
    for indice in esperado:
        assert _colorido(_miolo_da_iluminura(_desenho(projeto, projeto.paginas[indice], 72))) > 0.5
    if 0 not in esperado:
        assert projeto.paginas[0].filtro == ORIGINAL and not projeto.paginas[0].selecao


# --- e. várias escolhidas ----------------------------------------------------------------------------

def test_d659_e_varias_paginas_escolhidas_procura_so_nelas(janela, tmp_path, procuradas):
    """"vai procuar na pagina que está ou nas paginas que foram selecionadas": Preto e branco
    escolhido na página 1 e na 3 de 4 (o filtro não tem "pares/ímpares" nem "pôr filtro" na grade
    "ver todas": cada página escolhida no painel). Na tela e no PDF, só a 1 e a 3 são
    procuradas; a 2 e a 4 ficam no Original, sem marcação."""
    tela = _livro_novo(janela, tmp_path, folhas=4)
    projeto = janela.projeto
    for indice in (0, 2):
        tela.ir_para_pagina(indice)
        _assentar()
        _escolher(tela, PRETO_E_BRANCO)
        _esperar(lambda i=indice: _definitiva(projeto.paginas[i]), motivo=f"página {indice + 1}")
    assert set(procuradas) == {0, 2}, f"procurou {procuradas}"
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "e") <= {0, 2}
    assert not projeto.paginas[1].selecao and not projeto.paginas[3].selecao


# --- f e g. desmarcadas, outros filtros: igual ao de antes ------------------------------------------

def test_d659_f_as_tres_desmarcadas_nada_e_procurado_e_sai_igual_ao_de_antes(
        janela, tmp_path, procuradas, monkeypatch):
    """D-586: "Desligada, o filtro vale na página inteira". Preto e branco com "Respeitar",
    "Gravuras em tons de cinza" e "Só as letras" desmarcadas → nenhuma procura (nem na tela, nem
    no PDF) e a página igual, byte a byte, à do código de antes; toda em preto e branco."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    _caixa_respeitar(tela).click()
    _assentar()
    assert not pagina.respeitar_gravuras_achadas and not pagina.gravuras_em_tons_de_cinza
    assert not pagina.misto_so_as_letras and not projeto.misto_so_as_letras
    _previa_pronta(tela, 0, "a prévia sem as caixinhas")
    # a prévia do clique no Preto e branco (com a "Respeitar" ainda marcada) pode ter procurado;
    # o que vale é: depois de desmarcar, nada mais é procurado
    procuradas.clear()
    pagina.selecao = []                   # como a página estava antes do conserto
    pagina.marcacao_provisoria = False
    agora = _desenho(projeto, pagina, 110)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes = _desenho(projeto, pagina, 110)
    finally:
        contexto.__exit__(None, None, None)
    assert np.array_equal(agora, antes), "não saiu igual ao código de antes"
    assert _colorido(agora) == 0.0, "sobrou cor: a página devia sair toda em preto e branco"
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "f") == set()
    assert procuradas == []


@pytest.mark.parametrize("filtro", [MELHORAR, MAGICO_PRO, ORIGINAL])
def test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes(
        janela, tmp_path, procuradas, monkeypatch, filtro):
    """Melhorar, Mágico pro e Original escolhidos à mão (com as caixinhas de fábrica, "Respeitar"
    marcada, e até "Gravuras em tons de cinza" gravada na página): nenhuma procura, e a página
    igual, byte a byte, à do código de antes."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    if filtro == ORIGINAL:
        _escolher(tela, MELHORAR)
    _escolher(tela, filtro)
    pagina.gravuras_em_tons_de_cinza = True
    _assentar()
    _esperar(lambda: tela.previas.ja_pronta(0, tela._dpi_atual) is not None, motivo="a prévia")
    agora = _desenho(projeto, pagina, 110)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes = _desenho(projeto, pagina, 110)
    finally:
        contexto.__exit__(None, None, None)
    assert np.array_equal(agora, antes), "não saiu igual ao código de antes"
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "g") == set()
    assert procuradas == [], f"procurou: {procuradas}"


# --- h. tela = PDF; Ctrl+Z / Ctrl+Shift+Z ----------------------------------------------------------

def test_d659_h_o_pdf_sai_como_a_tela(janela, tmp_path, procuradas):
    """D-066/D-473: página 1 em Preto e branco com "Respeitar" (gravura colorida) e página 2 com
    "Gravuras em tons de cinza" (gravura cinza), no livro novo → no PDF cada uma sai como a
    tela, e a página 3 (Original) sem procura."""
    tela = _livro_novo(janela, tmp_path)
    projeto = janela.projeto
    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: _definitiva(projeto.paginas[0]), motivo="a página 1 procurada")
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    _caixa_cinza(tela).click()
    _assentar()
    _esperar(lambda: _definitiva(projeto.paginas[1]), motivo="a página 2 procurada")
    dpi = int(projeto.qualidade_dpi)
    paginas = _gerar(projeto, tmp_path, "saida", dpi)
    assert _colorido(_miolo_da_iluminura(paginas[0])) > 0.5, "no PDF a página 1 perdeu a gravura"
    miolo = _miolo_da_iluminura(paginas[1])
    assert _colorido(miolo) < 0.001 and _meio_tons(miolo) > 0.5, "no PDF a 2 não saiu cinza"
    for k in (0, 1):
        desenho = _desenho(projeto, projeto.paginas[k], dpi)
        no_pdf = paginas[k]
        if no_pdf.shape != desenho.shape:
            no_pdf = cv2.resize(no_pdf, (desenho.shape[1], desenho.shape[0]),
                                interpolation=cv2.INTER_AREA)
        assert _diferenca(no_pdf, desenho) < 3.0, f"a página {k + 1} do PDF não é a da tela"
    assert 2 not in procuradas


def test_d659_h_ctrl_z_desfaz_e_ctrl_shift_z_refaz(janela, tmp_path, procuradas):
    """D-020: o Preto e branco escolhido à mão (que procurou a gravura) é uma ação do Histórico:
    Ctrl+Z volta a página ao Original, igual byte a byte ao de antes de escolher; Ctrl+Shift+Z
    refaz e a gravura volta respeitada, igual à primeira vez (sem procurar de novo)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    original = _desenho(projeto, pagina, 110)
    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: _definitiva(pagina), motivo="a gravura achada")
    feito = _desenho(projeto, pagina, 110)
    assert _colorido(_miolo_da_iluminura(feito)) > 0.5
    janela.show()
    janela.move(-3000, -3000)
    janela.activateWindow()
    _assentar()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier)
    _assentar()
    assert pagina.filtro == ORIGINAL
    assert np.array_equal(_desenho(projeto, pagina, 110), original), "o Ctrl+Z não voltou igual"
    procuradas.clear()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier | Qt.ShiftModifier)
    _assentar()
    assert pagina.filtro == PRETO_E_BRANCO
    assert np.array_equal(_desenho(projeto, pagina, 110), feito), "o Ctrl+Shift+Z não refez igual"
    _previa_pronta(tela, 0, "a prévia refeita")
    assert procuradas == [], "refazer procurou de novo"


# --- i. o Automático depois -----------------------------------------------------------------------

def test_d659_i_depois_o_automatico_a_conta_e_a_de_antes(janela, tmp_path, procuradas, monkeypatch):
    """Depois do Preto e branco à mão na página 1 (procurada), rodar o Automático no livro
    (Endireitar, Cortar as bordas, Limpar a folha: o de fábrica; "Gravuras e fotos" desmarcada):
    com "Limpar a folha" ligado, a conta de quem procura é a de antes em todas as páginas
    (marca_sozinho e a marcação da máquina valem como no `a0c99cc7`), cada página do PDF sai
    igual, byte a byte, ao desenho com o código de antes, e a etapa 5 continua desmarcada.
    (A página 1 guarda a gravura achada antes, que acompanha o papel no corte, como toda
    página já procurada: ONDE-PAREI, ressalva 3.)"""
    from core import etapas as E
    from tests.ajudante_do_automatico import rodar_como_o_conferir

    tela = _livro_novo(janela, tmp_path)
    projeto = janela.projeto
    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: _definitiva(projeto.paginas[0]), motivo="a gravura achada")
    assert rodar_como_o_conferir(janela, limpar=True)
    assert projeto.limpar and projeto.passou_pelo_automatico and not _etapa_5_ligada(projeto)
    for p in projeto.paginas:
        assert E.marca_sozinho(projeto, p) == _marca_sozinho_de_antes(projeto, p)
        assert E.a_marcacao_da_maquina_vale(projeto, p) == (
            projeto.detectar_regioes or _procura_por_dentro_de_antes(projeto, p))
    # o primeiro desenho de cada página depois do Automático guarda as medidas dela (a
    # geometria, em core/pipeline); as comparações começam depois, como em
    # tests/test_decisoes_respeitar_gravuras._depois_do_automatico
    for p in projeto.paginas:
        _desenho(projeto, p, 110)
    agora = [_desenho(projeto, p, 110) for p in projeto.paginas]
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes = [_desenho(projeto, p, 110) for p in projeto.paginas]
    finally:
        contexto.__exit__(None, None, None)
    for k, (a, b) in enumerate(zip(agora, antes)):
        assert np.array_equal(a, b), f"a página {k + 1} mudou depois do Automático"


# --- o defeito da tela achado no caminho (core/pipeline.acertar_no_tamanho_do_pdf) -------------

def test_d659_a_tela_nao_troca_a_previa_pela_folha_crua(tmp_path, procuradas):
    """Defeito achado em 09/11/2026 ao fazer a D-659 (o clique no Preto e branco não mudava a
    tela): no acerto por trás de uma página com a marcação provisória (a da prévia) e sem a regra
    do "Para revisar", core/pipeline.acertar_no_tamanho_do_pdf(com_a_imagem=True) devolvia a
    FOLHA CRUA (sem corte e sem filtro) como "a imagem do PDF", e a tela (ui/tarefas.
    _por_a_imagem_do_pdf) trocava a prévia certa por ela. A docstring sempre disse "ou None nas
    outras (nada foi desenhado com o filtro)"; o nome `grande` tinha sido usado duas vezes desde
    o `4f881001`. Agora: a marcação é trocada pela do tamanho do PDF e nenhuma imagem volta."""
    from core import automatico, etapas
    from core.pdf_io import abrir_pdf, info_paginas
    from core.pipeline import acertar_no_tamanho_do_pdf, renderizar_pagina
    from modelos import Projeto

    caminho = R._pdf(tmp_path / "livro.pdf", 1)
    projeto = Projeto(caminho_entrada=caminho, nome="livro")
    doc = abrir_pdf(caminho)
    try:
        automatico.livro_leve(projeto, [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)])
        pagina = projeto.paginas[0]
        pagina.filtro = PRETO_E_BRANCO
        etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)
        pagina.gravuras_em_tons_de_cinza = True           # procura também no código de antes
        projeto.limpar = True                             # (o Automático rodado: o caminho de antes)
        renderizar_pagina(doc, projeto, pagina, dpi=55)   # a prévia: marcação provisória
        assert pagina.marcacao_provisoria and pagina.selecao
        mudou, imagem = acertar_no_tamanho_do_pdf(doc, projeto, pagina, com_a_imagem=True)
    finally:
        doc.close()
    assert not pagina.marcacao_provisoria, "a marcação não virou a definitiva"
    assert imagem is None, "devolveu a folha crua como se fosse o desenho do PDF"
