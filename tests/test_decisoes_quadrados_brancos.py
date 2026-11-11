"""D-668 (Samuel, 10/11/2026): os quadrados brancos do Melhorar e do Mágico pro (o conserto C).

O defeito (Lista de bugs, 10/11/2026, prints 09 e 10 da sessão 5): livro novo, que nunca passou
pelo Automático, Melhorar ou Mágico pro escolhido à mão no painel "Filtro da página": a água, o céu
e as roupas claras das pinturas saem com buracos brancos em quadrados, na tela e no PDF, e o "i" e
o "t" finos se quebram ("Vivia" vira "V via"). Palavras dele: "anotar erro do filtro melhorar, ele
deixa a imagem pixelada, olha esses quadrados brancos. também acontece no automatico e no magico
pro" e "o erro não aparece só na pagina 13, aparece em varias." Causa (relatorios/quadrados-brancos-
2026-11-10, ramo obra-2026-10-26): (1) sem a gravura achada, a limpeza do papel do Melhorar e do
Mágico pro (core/filtros._limpar_o_papel_de_verdade) toma a pintura por papel; a pergunta da cor é
feita sobre a cor crua do JPEG, guardada em blocos de 16x16, e o branco sai em quadrados; (2) a
"Respeitar as gravuras achadas" só procurava a gravura no Preto e branco (D-659).

Decisão (Central `quadrados-qual`: "Roxo: o conserto C (recomendo)"; chat: "c"): "Melhorar e Mágico
pro voltam a proteger as pinturas: nas páginas com Melhorar ou Mágico pro e "Respeitar as gravuras
achadas" marcada, o programa procura a gravura (como o Preto e branco, D-659) e não pinta de branco
dentro dela; e a limpeza do papel só pinta de branco onde em volta também é papel (vale também com
"Respeitar" desmarcada, print 10)." Pela D-667 ("se mudou a ferramenta, muda em todos os lugares"),
a procura vale nos três filtros por UMA regra (core.filtros.FILTROS_QUE_RESPEITAM_AS_GRAVURAS).

O que estas provas guardam:
  1. a conta (core/etapas, sem janela): quem procura com "Limpar a folha" desligado; a lista é a
     mesma da caixinha desmarcada; com "Limpar a folha" ligado, a conta de antes;
  2. a quarta pergunta da limpeza, numa página sintética (roda em qualquer máquina): a pintura em
     tom médio com a cor em blocos de 16x16 não vai mais a branco; a mancha do verso no papel
     continua indo; a página sem pintura sai igual à de antes;
  3. na tela, no livro novo (clique de verdade): Melhorar e Mágico pro com "Respeitar" procuram
     só a página da opção (ou as que o "Aplicar em" alcançou), a gravura é respeitada como depois
     do Automático; com "Respeitar" desmarcada, nada é procurado;
  4. no livro dele (só no PC do Samuel; pula sem o PDF): página 13 do *Na escola de Jesus*, como
     sai no PDF: a pintura sem buracos, o "i" de "Vivia" inteiro, o print 10 (Mágico pro com
     "Respeitar" desmarcada) e o Preto e branco à mão igual, ponto por ponto, ao de antes.

"O código de antes" (o `58806f81`, ponta do obra-2026-10-26 antes do conserto) é imitado por
_com_o_codigo_de_antes: a procura só no Preto e branco e a quarta pergunta sempre "sim". A reversão
de verdade (estas provas rodadas no `58806f81`) está em relatorios/quadrados-c-2026-11-10/.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import filtros as F  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO  # noqa: E402
from tests.test_decisoes_gravura_a_mao import (  # noqa: E402,F401 - fixtures e ajudantes
    _botao, _caixa_respeitar, _como_no_automatico, _definitiva, _etapa_5_ligada, _livro_novo,
    _previa_pronta, _procurar_no_pdf, procuradas)
from tests.test_decisoes_respeitar_gravuras import (  # noqa: E402,F401 - fixtures
    _assentar, _colorido, _desenho, _escolher, _esperar, _gerar, _miolo_da_iluminura, app,
    janela, pasta)

OS_DOIS = [MELHORAR, MAGICO_PRO]


# --- o código de antes (58806f81) ---------------------------------------------------------------

def _com_o_codigo_de_antes(monkeypatch):
    """Um contexto em que o programa responde como no `58806f81`: a "Respeitar" só procura no
    Preto e branco (core/etapas.respeitar_procura le a lista de core.filtros) e a limpeza do papel
    não faz a quarta pergunta (core.filtros._em_volta_e_papel sempre "sim")."""
    contexto = monkeypatch.context()
    m = contexto.__enter__()
    # raising=False: no proprio 58806f81 (a prova da reversao, §4.7) os dois nomes nao existem e
    # o codigo ja e o de antes
    m.setattr(F, "FILTROS_QUE_RESPEITAM_AS_GRAVURAS", (PRETO_E_BRANCO,), raising=False)
    m.setattr(F, "_em_volta_e_papel", lambda original, cinza, nivel: np.ones(cinza.shape, bool),
              raising=False)
    return contexto


# --- 1. a conta -----------------------------------------------------------------------------------

def test_d668_a_conta_os_tres_filtros_procuram_pela_mesma_regra():
    """Sem "Limpar a folha" (livro novo): Preto e branco, Melhorar e Mágico pro escolhidos À MÃO
    com "Respeitar" (de fábrica) procuram a gravura; Original e "Tirar o fundo" não; sem a marca
    FILTRO (D-009) ou com "Respeitar" desmarcada, nenhum. A lista é a MESMA que diz quais filtros
    obedecem a caixinha desmarcada (D-667: uma regra só). Com "Limpar a folha" ligado, a conta de
    antes (só a página pulada com a gravura achada à mão, D-661)."""
    from core import etapas as E
    from core import pipeline
    from modelos import ConfigPagina, Projeto

    assert set(F.FILTROS_QUE_RESPEITAM_AS_GRAVURAS) == {PRETO_E_BRANCO, MELHORAR, MAGICO_PRO}
    assert pipeline.FILTROS_QUE_RESPEITAM_AS_GRAVURAS is F.FILTROS_QUE_RESPEITAM_AS_GRAVURAS

    projeto = Projeto(caminho_entrada="x.pdf", nome="x")
    projeto.limpar = False                      # o livro novo (core.automatico.livro_leve)
    projeto.detectar_regioes = True             # o de fábrica do livro novo: não conta sem o Limpar

    def pagina(filtro, a_mao=True, **campos):
        p = ConfigPagina(indice=0, folha=0, filtro=filtro)
        if a_mao:
            E.marcar_mexida_a_mao(p, E.FILTRO)
        for campo, valor in campos.items():
            setattr(p, campo, valor)
        return p

    for filtro in (PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
        assert E.respeitar_procura(projeto, pagina(filtro)), filtro
        assert E.marca_sozinho(projeto, pagina(filtro)), filtro
        assert E.a_marcacao_da_maquina_vale(projeto, pagina(filtro)), filtro
        assert not E.marca_sozinho(projeto, pagina(filtro, respeitar_gravuras_achadas=False)), filtro
        assert not E.marca_sozinho(projeto, pagina(filtro, a_mao=False)), f"{filtro} sem a marca"
    for filtro in (ORIGINAL, TIRAR_FUNDO):
        assert not E.marca_sozinho(projeto, pagina(filtro)), filtro
    # o cinza e o "Só as letras" continuam só do Preto e branco
    assert not E.marca_sozinho(projeto, pagina(MELHORAR, respeitar_gravuras_achadas=False,
                                               gravuras_em_tons_de_cinza=True))

    projeto.limpar = True                       # depois do Automático: a conta de antes
    for filtro in (MELHORAR, MAGICO_PRO):
        assert not E.respeitar_procura(projeto, pagina(filtro))
        assert E.respeitar_procura(projeto, pagina(filtro, gravura_achada_a_mao=True))   # D-661


# --- 2. a quarta pergunta da limpeza (página sintética) -----------------------------------------

def _cor(h: int, s: int, v: int) -> tuple[int, int, int]:
    bgr = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0, 0]
    return tuple(int(x) for x in bgr)


PINTURA = (slice(40, 500), slice(60, 640))
MANCHA = (slice(520, 547), slice(20, 682))


def _pagina_com_agua(com_pintura: bool = True) -> np.ndarray:
    """Papel âmbar, texto no pé (a limpeza do papel liga: mais de 200 peças de letra), uma faixa
    de mancha do verso (pontinhos pardos claros longe da letra) e, no alto, a "água" de uma
    pintura: cinza-azulado de tom médio, com a cor em blocos de 16x16 como a do JPEG, uns blocos
    com pouca cor ("cor de papel") e outros com mais. É a página 13 do *Na escola de Jesus* em
    miniatura."""
    rng = np.random.default_rng(5)
    img = np.full((900, 700, 3), (205, 228, 245), np.uint8)
    for y in range(560, 870, 18):
        for x in range(30, 670, 12):
            img[y:y + 6, x:x + 6] = 30
    if com_pintura:
        for by in range(40, 500, 16):
            for bx in range(60, 640, 16):
                saturacao = 12 if (by // 16 + bx // 16) % 2 == 0 else 34
                img[by:by + 16, bx:bx + 16] = _cor(105, saturacao, 150 + int(rng.integers(-6, 7)))
    for _ in range(400):
        y, x = int(rng.integers(520, 545)), int(rng.integers(20, 680))
        img[y:y + 2, x:x + 2] = _cor(18, 40, 215)
    return img


def _branco_puro(img: np.ndarray, area) -> float:
    return float((img[area] >= 250).all(axis=2).mean())


@pytest.mark.parametrize("filtro", OS_DOIS)
def test_d668_a_agua_da_pintura_nao_vai_mais_a_branco_em_quadrados(filtro, monkeypatch):
    """REVERSÃO (§4.7, medida): sem a gravura achada (aplicar_filtro, o caminho da página sem
    marcação: o print 10, "Respeitar" desmarcada), a água da pintura sintética ia a branco em
    quadrados no código de antes (48% dela) e agora fica com o tom do filtro (0%). A mancha do
    verso no papel continua indo a branco (o motivo de a limpeza existir: "não tirou a mancha do
    verso"), igual ao de antes."""
    img = _pagina_com_agua()
    agora, _ = F.aplicar_filtro(img.copy(), filtro, clareza=100, intensidade=0)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes, _ = F.aplicar_filtro(img.copy(), filtro, clareza=100, intensidade=0)
    finally:
        contexto.__exit__(None, None, None)
    assert _branco_puro(antes, PINTURA) > 0.30, "a página de teste não mostra mais o defeito"
    assert _branco_puro(agora, PINTURA) < 0.01, (
        f"a água ainda vai a branco: {_branco_puro(agora, PINTURA):.1%}")
    assert _branco_puro(agora, MANCHA) > 0.99, "a mancha do verso deixou de sair"
    assert _branco_puro(agora, MANCHA) == _branco_puro(antes, MANCHA)


@pytest.mark.parametrize("filtro", OS_DOIS)
def test_d668_pagina_de_texto_sem_pintura_sai_igual_a_de_antes(filtro, monkeypatch):
    """Página de texto com a mancha do verso e sem pintura: a quarta pergunta responde "papel"
    em toda parte e a página sai IGUAL, ponto por ponto, à do código de antes (D-605: a limpeza
    da mancha do verso e do papel amarelado não muda)."""
    img = _pagina_com_agua(com_pintura=False)
    agora, _ = F.aplicar_filtro(img.copy(), filtro, clareza=100, intensidade=0)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes, _ = F.aplicar_filtro(img.copy(), filtro, clareza=100, intensidade=0)
    finally:
        contexto.__exit__(None, None, None)
    assert np.array_equal(agora, antes)


# --- 3. na tela, no livro novo ------------------------------------------------------------------

@pytest.mark.parametrize("filtro", OS_DOIS)
def test_d668_so_nesta_com_respeitar_procura_so_esta_pagina_e_respeita_a_gravura(
        janela, tmp_path, procuradas, filtro):
    """REVERSÃO: livro novo, página 1, clique em Melhorar ou Mágico pro ("Respeitar" já vem
    marcada, D-586): a gravura é procurada SÓ nesta página, como a D-659 faz no Preto e branco,
    e sai respeitada, IGUAL ao filtro depois do Automático (no código de antes nada era
    procurado). Andar pelas outras páginas não procura nelas, nem o PDF. A etapa 5 continua
    desmarcada. A tela mostra o mesmo desenho do PDF (D-473: _previa_pronta e _como_no_automatico
    usam a mesma conta, core.pipeline.renderizar_pagina)."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    assert _caixa_respeitar(tela).isChecked() and pagina.respeitar_gravuras_achadas
    _escolher(tela, filtro)
    _esperar(lambda: _definitiva(pagina), motivo="a gravura achada no tamanho do PDF")
    _previa_pronta(tela, 0, f"a prévia em {filtro}")
    assert set(procuradas) == {0}, f"procurou em outras páginas: {procuradas}"
    assert pagina.gravura_achada_a_mao, "a D-661 (Pular) não vale para esta página"

    dpi = tela._dpi_atual
    agora = _desenho(projeto, pagina, dpi)
    assert _colorido(_miolo_da_iluminura(agora)) > 0.5, "a gravura não saiu com a cor"
    assert np.array_equal(agora, _como_no_automatico(projeto, pagina, dpi)), \
        "não saiu igual ao filtro do Automático"

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


@pytest.mark.parametrize("filtro", OS_DOIS)
@pytest.mark.parametrize("alcance, esperado", [("todas", {0, 1, 2, 3}),
                                               ("daqui em diante", {1, 2, 3})])
def test_d668_aplicar_em_procura_so_nas_paginas_alcancadas(
        janela, tmp_path, procuradas, filtro, alcance, esperado):
    """D-667 (todos os lugares da ferramenta): o "Aplicar em" do Melhorar e do Mágico pro procura
    só nas páginas alcançadas, como o do Preto e branco (D-659: "se eu selecionar para o livro
    todo ou para varias paginas, ele vai procurar nas paginas especificas")."""
    tela = _livro_novo(janela, tmp_path, folhas=4)
    projeto = janela.projeto
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, filtro)
    _esperar(lambda: _definitiva(projeto.paginas[1]), motivo="a página 2 procurada")
    assert set(procuradas) == {1}, f"só nesta: procurou em {procuradas}"
    _botao(tela, alcance).click()
    _assentar()
    assert {p.indice for p in projeto.paginas if p.filtro == filtro} == esperado
    no_pdf = _procurar_no_pdf(projeto, tmp_path, procuradas, "d")
    assert set(procuradas) <= esperado, f"procurou fora do alcance: {procuradas}"
    assert no_pdf | {1} == esperado, f"no PDF, procuradas {no_pdf}; esperado {esperado}"
    for indice in esperado:
        assert _colorido(_miolo_da_iluminura(_desenho(projeto, projeto.paginas[indice], 72))) > 0.5


@pytest.mark.parametrize("filtro", OS_DOIS)
def test_d668_respeitar_desmarcada_nada_e_procurado(janela, tmp_path, procuradas, filtro):
    """D-586 ("Desligada, o filtro vale na página inteira"): Melhorar ou Mágico pro com
    "Respeitar" desmarcada → nenhuma procura, nem na tela nem no PDF (o print 10 fica só com a
    quarta pergunta da limpeza)."""
    tela = _livro_novo(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, filtro)
    _caixa_respeitar(tela).click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False
    procuradas.clear()
    pagina.selecao = None
    _assentar()
    assert _procurar_no_pdf(projeto, tmp_path, procuradas, "f") == set()
    assert procuradas == []


# --- 4. no livro dele (Na escola de Jesus, página 13) --------------------------------------------

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
NA_ESCOLA = ACERVO / "Na escola de Jesus - Catecismo explicado com imagens..pdf"
# frações da página 13 pronta (como sai no PDF, 300 DPI): a água da pintura (Jonas e a baleia) e
# as palavras "Vivia em" / "Um dia" (os mesmos recortes da imagem 6 da investigação)
AGUA_13 = (0.12, 0.13, 0.62, 0.36)
VIVIA_13 = (0.075, 0.529, 0.215, 0.566)


def _livro_novo_sem_janela():
    """O livro como a tela abre (core.automatico.livro_leve, sem o Automático)."""
    from core import automatico
    from core.pdf_io import abrir_pdf, info_paginas
    from modelos import Projeto

    if not NA_ESCOLA.exists():
        pytest.skip("sem o Na escola de Jesus (só no PC do Samuel)")
    projeto = Projeto(caminho_entrada=str(NA_ESCOLA), nome=NA_ESCOLA.stem)
    doc = abrir_pdf(str(NA_ESCOLA))
    try:
        tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
    finally:
        doc.close()
    automatico.livro_leve(projeto, tamanhos)
    return projeto


def _como_no_pdf(projeto, numero: int, filtro: str, respeitar: bool = True):
    """A página `numero` (de 1) escolhida À MÃO no painel com `filtro` ("bem forte" no Melhorar,
    "bem fraco" no Mágico pro, os do print 09 e do print 10), desenhada pelo corpo do PDF
    (core.pipeline._pagina_pronta): dividir, endireitar, cortar e filtro, na ordem do livro
    novo. Devolve (a página pronta, o original no mesmo tamanho)."""
    from core import etapas, pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array

    p = copy.deepcopy(projeto)
    pagina = p.paginas[numero - 1]
    pagina.filtro = filtro
    pagina.clareza_melhorar = 100
    pagina.intensidade_magico = 0
    pagina.respeitar_gravuras_achadas = respeitar
    etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)
    doc = abrir_pdf(p.caminho_entrada)
    try:
        folha = p.folhas[pagina.folha]
        pronta, _ = pipeline._pagina_pronta(p, doc, folha, pagina, pipeline._FolhaDaVez(), 0)
        original = pagina_para_array(doc, folha.indice, dpi=p.qualidade_dpi)
    finally:
        doc.close()
    if original.shape[:2] != pronta.shape[:2]:
        original = cv2.resize(original, (pronta.shape[1], pronta.shape[0]),
                              interpolation=cv2.INTER_AREA)
    return pronta, original


def _recorte(img: np.ndarray, fr) -> np.ndarray:
    h, w = img.shape[:2]
    return img[round(fr[1] * h):round(fr[3] * h), round(fr[0] * w):round(fr[2] * w)]


def _pintura_em_branco(pronta: np.ndarray, original: np.ndarray, fr) -> float:
    """Dos pontos da pintura de tom médio (luz entre 45% e 80% do papel no original: nem tinta
    escura, nem papel), quantos saíram branco puro. A medida 1 da investigação."""
    o, s = _recorte(original, fr), _recorte(pronta, fr)
    cinza = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(np.float32)
    nivel = float(np.percentile(cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)[::4, ::4], 85))
    pintura = (cinza < 0.80 * nivel) & (cinza > 0.45 * nivel)
    branco = (s >= 255).all(axis=2) if s.ndim == 3 else s >= 255
    return float((branco & pintura).sum()) / max(1, int(pintura.sum()))


def _letra_apagada(pronta: np.ndarray, original: np.ndarray, fr) -> float:
    """Da tinta das letras no original (luz abaixo de 50% do papel), quanto saiu quase branco
    (>= 230): o "i" e o "t" quebrados."""
    o, s = _recorte(original, fr), _recorte(pronta, fr)
    cinza = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(np.float32)
    tinta = cinza < 0.50 * float(np.percentile(cinza, 85))
    claro = (s >= 230).all(axis=2) if s.ndim == 3 else s >= 230
    return float((claro & tinta).sum()) / max(1, int(tinta.sum()))


@pytest.mark.parametrize("filtro", OS_DOIS)
def test_d668_pagina_13_sem_buracos_e_vivia_com_o_i_inteiro(filtro, monkeypatch):
    """REVERSÃO no livro dele (prints 09 e 10 da sessão 5): página 13 do *Na escola de Jesus*,
    livro novo, filtro escolhido à mão com "Respeitar" marcada, como sai no PDF. No código de
    antes a água da baleia tinha 25% de buracos brancos e o "i" de "Vivia" quebrava; agora,
    quase nada (o que sobra é a espuma, que já é branca no original) e o "i" inteiro."""
    projeto = _livro_novo_sem_janela()
    agora, original = _como_no_pdf(projeto, 13, filtro)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes, _ = _como_no_pdf(projeto, 13, filtro)
    finally:
        contexto.__exit__(None, None, None)
    assert _pintura_em_branco(antes, original, AGUA_13) > 0.10, "o livro não mostra mais o defeito"
    assert _pintura_em_branco(agora, original, AGUA_13) < 0.02, (
        f"buracos na água: {_pintura_em_branco(agora, original, AGUA_13):.1%}")
    assert _letra_apagada(antes, original, VIVIA_13) > 0.01, "o código de antes não quebrava a letra"
    assert _letra_apagada(agora, original, VIVIA_13) < 0.002, (
        f"letra quebrada: {_letra_apagada(agora, original, VIVIA_13):.2%}")


def test_d668_print_10_magico_pro_com_respeitar_desmarcada(monkeypatch):
    """REVERSÃO, print 10 (Mágico pro "bem fraco", "Respeitar" desmarcada): nada é procurado
    (D-586), e mesmo assim a água deixa de virar buraco branco, pela quarta pergunta da limpeza."""
    projeto = _livro_novo_sem_janela()
    agora, original = _como_no_pdf(projeto, 13, MAGICO_PRO, respeitar=False)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes, _ = _como_no_pdf(projeto, 13, MAGICO_PRO, respeitar=False)
    finally:
        contexto.__exit__(None, None, None)
    assert _pintura_em_branco(antes, original, AGUA_13) > 0.10
    assert _pintura_em_branco(agora, original, AGUA_13) < 0.02


def test_d668_preto_e_branco_a_mao_igual_ponto_por_ponto(monkeypatch):
    """D-659/D-661 testadas pelo Samuel em 10/11 ("fiz os dois testes que você pediu e estão
    funcionando."): a página 13 em Preto e branco escolhido à mão, com "Respeitar", sai IGUAL,
    ponto por ponto, à do código de antes."""
    projeto = _livro_novo_sem_janela()
    agora, _ = _como_no_pdf(projeto, 13, PRETO_E_BRANCO)
    contexto = _com_o_codigo_de_antes(monkeypatch)
    try:
        antes, _ = _como_no_pdf(projeto, 13, PRETO_E_BRANCO)
    finally:
        contexto.__exit__(None, None, None)
    assert np.array_equal(agora, antes)
