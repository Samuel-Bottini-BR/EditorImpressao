"""Depois do botão "Desentortar aumentando a página", o programa confere de novo (item 2.12, 23/10/2026).

Resposta P5 do Samuel (Central, 23/10/2026): "C — Aparece sempre, mas depois do
clique o programa confere de novo...", com o ajuste dele: "Mas o programa vai
saber sempre que estiver deformada, o aviso deve perguntar e não fazer
automaticamente." Então:
  1. o botão aparece em toda página que a proteção segurou (já era assim);
  2. depois do clique, as mesmas medidas da proteção na página aumentada:
     tinta saindo da página e fundo de fora entrando;
  3. ainda deformada: a página NÃO volta sozinha; entra o aviso "A página ainda
     saiu deformada", com "Desfazer" (volta sem desentortar, como antes do
     clique) e "Manter assim";
  4. saiu boa: fica, sem aviso;
  5. o Ctrl+Z continua desfazendo.

Os dois casos de verdade (só lidos; pulam fora do PC do Samuel): Destino do
socialismo, p. 18, de "Livros para editar" (o botão traz a deformação: aparece
a pergunta) e Righetti 96, do acervo (o botão dá certo: não aparece pergunta).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core import analise
from core import desentortar_scantailor as ds
from core import st_ferramentas as st
from modelos import ConfigPagina
from tests.test_desentortar_protecao import RIGHETTI, _livro, _pagina_com_papel, _pagina_do_acervo
from tests.test_desentortar_scantailor import pagina_curva

fitz = pytest.importorskip("fitz")

from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# ------------------------------------------------------------- as medidas

def test_tinta_cortada_pela_beirada_da_pagina_aumentada():
    """Só conta o pedaço de tinta (de 1 mm ou mais) que encosta na beirada da
    página aumentada; pontinho e tinta longe da beirada não contam."""
    marca = np.full((300, 200), ds.MARCA_PAPEL, np.uint8)
    marca[100:130, 50:80] = ds.MARCA_TINTA            # longe da beirada
    assert ds.pecas_cortadas_pela_beirada(marca, 300) == 0
    marca[0:3, 10:13] = ds.MARCA_TINTA                # pontinho na beirada
    assert ds.pecas_cortadas_pela_beirada(marca, 300) == 0
    for k in range(3):                                # três letras cortadas embaixo
        marca[280:300, 20 + 50 * k:40 + 50 * k] = ds.MARCA_TINTA
    assert ds.pecas_cortadas_pela_beirada(marca, 300) == 3


def test_a_regra_de_ainda_deformada():
    assert not ds.ainda_deformada(0, 0.0)
    assert not ds.ainda_deformada(ds.PECAS_PARA_FORA - 1, ds.FUNDO_DENTRO_MAXIMO_AUMENTANDO)
    assert ds.ainda_deformada(ds.PECAS_PARA_FORA, 0.0)
    assert ds.ainda_deformada(0, ds.FUNDO_DENTRO_MAXIMO_AUMENTANDO + 0.001)
    # Righetti 96 com o botão: 5,7% de papel de fora (medido em 23/10) - fica
    assert not ds.ainda_deformada(0, 0.0574)


@precisa_da_dll
def test_a_pagina_aumentada_nunca_volta_sozinha(monkeypatch):
    """Mesmo deformada, a imagem que sai é a AUMENTADA (quem decide é a
    pessoa, pelo aviso); só a marca ainda_deformada diz que precisa perguntar."""
    img, caixa = _pagina_com_papel()
    pagina = ConfigPagina(indice=0, folha=0, metade="direita", desentortar=ds.AUTOMATICO,
                          desentortar_aumentar=True)
    boa = ds.preparar_no_corte(img, caixa, pagina, 300)
    assert not boa.ainda_deformada and boa.pecas_cortadas is not None
    monkeypatch.setattr(ds, "ainda_deformada", lambda pecas, fundo: True)
    ruim = ds.preparar_no_corte(img, caixa, pagina, 300)
    assert ruim.ainda_deformada and not ruim.saiu_sem
    assert np.array_equal(ruim.imagem, boa.imagem)


@precisa_da_dll
def test_sem_o_botao_nao_ha_a_conferencia_nova():
    img, caixa = _pagina_com_papel()
    pagina = ConfigPagina(indice=0, folha=0, metade="direita", desentortar=ds.AUTOMATICO)
    preparo = ds.preparar_no_corte(img, caixa, pagina, 300)
    assert not preparo.ainda_deformada and preparo.pecas_cortadas is None


# ------------------------------------------------------------- o aviso

def test_o_aviso_pergunta_desfazer_ou_manter_assim():
    alerta = analise.descrever(analise.DESENTORTAR_AINDA_DEFORMADA)
    assert alerta.titulo == "A página ainda saiu deformada"
    assert alerta.acao == "Desfazer"
    assert alerta.correcao == "desentortar_desfazer_aumento"
    assert alerta.confirmar == "Manter assim"
    assert alerta.mensagem.endswith("?"), "o aviso pergunta"
    for texto in (alerta.titulo, alerta.mensagem, alerta.acao, alerta.confirmar):
        assert all(ord(c) < 0x2000 for c in texto), "sem emoji"
    # os outros avisos continuam com o "está certo" de sempre
    assert analise.descrever(analise.DESENTORTAR_SAIU_SEM).confirmar is None


def test_o_aviso_entra_quando_ainda_deformada_e_sai_quando_fica_boa(monkeypatch):
    from core import pipeline

    img = pagina_curva(curva=0)
    projeto, folha, pagina = _livro(ds.AUTOMATICO)
    pagina.desentortar_aumentar = True
    pagina.alertas = [analise.DESENTORTAR_SAIU_SEM]
    pagina.revisada = True
    deformada = {"sim": True}

    def aumentada(reta, caixa, pag, dpi=None, **k):
        return ds.Preparo(reta.copy(), False, 20, 0.4, deformada["sim"], 22)

    monkeypatch.setattr(ds, "preparar_no_corte", aumentada)
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert pagina.alertas == [analise.DESENTORTAR_AINDA_DEFORMADA]
    assert pagina.revisada is False and pagina.precisa_revisao
    # "Manter assim" marca como conferida: desenhar de novo não traz o aviso de volta à vista
    pagina.revisada = True
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert pagina.alertas.count(analise.DESENTORTAR_AINDA_DEFORMADA) == 1 and pagina.revisada
    deformada["sim"] = False
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas


def test_desligar_o_desentortar_tira_o_aviso_novo():
    from core import pipeline

    img = pagina_curva(curva=0)
    projeto, folha, pagina = _livro(ds.DESLIGADO)
    pagina.alertas = [analise.DESENTORTAR_AINDA_DEFORMADA]
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas


# ------------------------------------------------------------- na tela

def _com_o_aviso(conferir, codigo):
    pagina = conferir.projeto.paginas[0]
    pagina.desentortar = ds.AUTOMATICO
    pagina.alertas = [codigo]
    pagina.revisada = False
    conferir.ir_para_pagina(0)
    conferir.atualizar()
    return pagina


def test_na_faixa_os_dois_botoes_desfazer_e_manter_assim(conferir):
    _com_o_aviso(conferir, analise.DESENTORTAR_AINDA_DEFORMADA)
    assert conferir.texto_faixa.text().startswith("Mesmo aumentando a página")
    assert conferir.botao_sugestao.text() == "Desfazer"
    assert conferir.botao_esta_certo.text() == "Manter assim"
    # outro aviso: o "está certo" de sempre volta
    _com_o_aviso(conferir, analise.DESENTORTAR_SAIU_SEM)
    assert conferir.botao_sugestao.text() == "Desentortar aumentando a página"
    assert conferir.botao_esta_certo.text() == "está certo"


def test_o_caminho_inteiro_na_tela_com_o_ctrl_z(conferir):
    """Clique no botão -> aviso novo -> "Desfazer" volta sem desentortar ->
    Ctrl+Z traz o aumento de volta -> desfazer de novo tira o aumento (como
    antes do clique)."""
    pagina = _com_o_aviso(conferir, analise.DESENTORTAR_SAIU_SEM)
    conferir.botao_sugestao.click()
    assert pagina.desentortar_aumentar is True
    pagina.alertas = [analise.DESENTORTAR_AINDA_DEFORMADA]   # o que a prévia nova põe
    pagina.revisada = False
    conferir.atualizar()
    conferir.botao_sugestao.click()                          # "Desfazer"
    assert pagina.desentortar_aumentar is False
    assert pagina.desentortar == ds.AUTOMATICO, "o desentortar do livro fica como estava"
    assert conferir.acoes.descricao_desfazer().endswith("Voltar a página 1 sem desentortar")
    conferir.desfazer()                                      # Ctrl+Z
    assert pagina.desentortar_aumentar is True
    conferir.desfazer()
    assert pagina.desentortar_aumentar is False


def test_manter_assim_marca_a_pagina_como_conferida(conferir):
    pagina = _com_o_aviso(conferir, analise.DESENTORTAR_AINDA_DEFORMADA)
    pagina.desentortar_aumentar = True
    conferir.botao_esta_certo.click()                        # "Manter assim"
    assert pagina.revisada is True and pagina.desentortar_aumentar is True
    assert conferir.botao_esta_certo.text() == "está certo"


# ------------------------------------------------------------- os dois casos de verdade

DESTINO = Path(r"D:\Livros para editar\2 - TEOLOGIA\Doutrina Social da Igreja"
               r"\Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI"
               r"\9 - Octávio de Faria\Destino do socialismo - Octavio de faria.pdf")


@precisa_da_dll
@pytest.mark.skipif(not DESTINO.is_file(), reason="sem 'Livros para editar' (só no PC do Samuel)")
def test_destino_do_socialismo_18_o_botao_traz_a_deformacao_e_aparece_a_pergunta(tmp_path):
    """Destino do socialismo (Octávio de Faria), p. 18 do PDF, página da direita
    ("Dividir" ligado), livro novo de fábrica, desentortar automático: a
    proteção segura (sai como hoje, aviso "Desentortar não usado"); com o
    botão a página volta monstruosa (medido em 23/10: 22 pedaços de tinta
    cortados pela beirada da página aumentada, 39,6% de fundo de fora) -> o
    aviso "A página ainda saiu deformada" pergunta, e a página fica aumentada
    (não volta sozinha). "Desfazer" traz de volta a página de antes do clique."""
    from core import pipeline

    img, folha, pagina, projeto = _pagina_do_acervo(tmp_path, DESTINO, 17, 0, True, "direita")
    dpi = projeto.qualidade_dpi
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    pagina.desentortar = ds.AUTOMATICO
    segurada = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    # "como hoje": o mesmo tamanho e nenhum ponto mudado de verdade (a página
    # segurada vem pelo caminho do "papel em volta"; arredondamento de 1 ou 2
    # tons pode mudar, como no antes/depois de 22/10)
    assert segurada.shape == hoje.shape
    assert int((np.abs(segurada.astype(int) - hoje.astype(int)) > 64).sum()) == 0
    assert pagina.alertas[0] == analise.DESENTORTAR_SAIU_SEM
    pagina.desentortar_aumentar = True
    aumentada = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert aumentada.shape != hoje.shape, "a página não volta sozinha"
    assert pagina.alertas[0] == analise.DESENTORTAR_AINDA_DEFORMADA
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas
    assert pagina.precisa_revisao
    pagina.desentortar_aumentar = False                       # "Desfazer"
    de_volta = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert np.array_equal(de_volta, segurada)
    assert pagina.alertas[0] == analise.DESENTORTAR_SAIU_SEM
    assert analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas


@precisa_da_dll
@pytest.mark.skipif(not RIGHETTI.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_righetti_96_o_botao_da_certo_e_nao_aparece_pergunta(tmp_path):
    """Righetti, folha 96 (girada 270°, "Dividir" ligado), página da direita,
    livro novo de fábrica, automático: com o botão a página cresce e o texto
    fica inteiro (medido em 23/10: 0 pedaços cortados, 5,7% de papel de fora)
    -> nenhuma pergunta, e o aviso "Desentortar não usado" sai."""
    from core import pipeline

    img, folha, pagina, projeto = _pagina_do_acervo(tmp_path, RIGHETTI, 95, 270, True, "direita")
    dpi = projeto.qualidade_dpi
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    pagina.desentortar = ds.AUTOMATICO
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert analise.DESENTORTAR_SAIU_SEM in pagina.alertas
    pagina.desentortar_aumentar = True
    maior = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert maior.shape[1] > hoje.shape[1]
    assert analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas


# ------------------------------------------------------------- REVERSÃO: o aviso que sumia

def test_reversao_previa_em_resolucao_baixa_nao_tira_os_avisos(monkeypatch):
    """REVERSÃO (§4.7) do bug de 23/10/2026 (achado nos prints da janela da
    resposta P5): o desentortar não acha as curvas em resolução baixa, então a
    prévia rápida (110 DPI), as miniaturas e os cartões desenhavam a página
    "sem estrago" e TIRAVAM o aviso que o desenho na resolução do livro tinha
    posto: o "Desentortar não usado" sumia da faixa antes do clique (no código
    de antes, a220c2d, o aviso sai aqui). Agora só o desenho na resolução do
    livro (projeto.qualidade_dpi) põe ou tira os avisos do desentortar."""
    from core import pipeline

    img = pagina_curva(curva=0)
    projeto, folha, pagina = _livro(ds.AUTOMATICO)
    pagina.alertas = [analise.DESENTORTAR_SAIU_SEM]
    monkeypatch.setattr(ds, "preparar_no_corte",
                        lambda reta, caixa, pag, dpi=None, **k: ds.Preparo(reta.copy(), False, 0, 0.0))
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=110)
    assert analise.DESENTORTAR_SAIU_SEM in pagina.alertas, "a prévia rápida tirou o aviso"
    pagina.alertas = [analise.DESENTORTAR_AINDA_DEFORMADA]
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=110)
    assert analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
    assert analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas


@precisa_da_dll
@pytest.mark.skipif(not DESTINO.is_file(), reason="sem 'Livros para editar' (só no PC do Samuel)")
def test_reversao_destino_18_o_aviso_fica_depois_da_previa_rapida(tmp_path):
    """REVERSÃO (§4.7), o mesmo bug na página de verdade: Destino do socialismo
    18, direita, automático. O desenho na resolução do livro põe o aviso; o
    desenho a 110 DPI (a prévia rápida) não o tira mais (no a220c2d tirava)."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    _, _, pagina, projeto = _pagina_do_acervo(tmp_path, DESTINO, 17, 0, True, "direita")
    pagina.desentortar = ds.AUTOMATICO
    doc = abrir_pdf(str(tmp_path / "pagina.pdf"))
    try:
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
        assert analise.DESENTORTAR_SAIU_SEM in pagina.alertas
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
        assert analise.DESENTORTAR_SAIU_SEM in pagina.alertas, "a prévia rápida tirou o aviso"
    finally:
        doc.close()
