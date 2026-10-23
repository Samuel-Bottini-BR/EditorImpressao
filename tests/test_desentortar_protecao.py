"""A proteção do desentortar e o "Desentortar aumentando a página" (item 2.12, 22/10/2026).

Respostas do Samuel (22/10/2026, perguntas a-212-p1 e a-212-p2):
  P1 "B — Proteção: se a tinta passar a encostar na beirada, a página sai sem
     desentortar e vai para o 'Para revisar'" (+ "Ainda vou poder selecionar a
     opção c para as paginas que entrarem para revisão?" - sim: o botão
     "Desentortar aumentando a página" no aviso, a opção C só naquela página);
  P2 "B — A mesma proteção da pergunta anterior" (o "pelas margens" que entorta
     a página e traz fundo escuro para dentro).

Os testes de REVERSÃO (§4.7) usam o acervo (só no PC do Samuel) e falham no
código de antes (177f711): Righetti 96 no automático (a tinta saía da página)
e Cursus 176 no "pelas margens" (a página era entortada).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from core import analise
from core import desentortar_scantailor as ds
from core import st_ferramentas as st
from modelos import ConfigFolha, ConfigPagina, Projeto
from tests.test_desentortar_scantailor import (
    _caixa_rente,
    pagina_curva,
    tinta_que_ficou_no_lugar,
)

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _pagina_com_papel(curva=60):
    """A página de mentira com 120 pontos de papel em volta e o corte rente."""
    img = cv2.copyMakeBorder(pagina_curva(curva=curva), 120, 120, 120, 120,
                             cv2.BORDER_CONSTANT, value=(235, 235, 235))
    return img, _caixa_rente(img)


# ------------------------------------------------------------- a DLL (versão 9)

@precisa_da_dll
@pytest.mark.parametrize("modo", [ds.AUTOMATICO, ds.PELAS_MARGENS])
def test_crescer_nao_muda_a_pagina_dentro_do_corte(modo):
    """O `crescer` é a MESMA página desentortada, só maior: dentro do corte,
    ponto por ponto igual (a medida da proteção não muda a imagem)."""
    img, (x0, y0, x1, y1) = _pagina_com_papel()
    corte = (x0, y0, x1 - x0, y1 - y0)
    conteudo = ds.caixa_do_conteudo(img, (x0, y0, x1, y1), 300)
    sem = ds.desentortar(img, 300, modo, lado=2, corte=corte, conteudo=conteudo)
    com = ds.desentortar(img, 300, modo, lado=2, corte=corte, conteudo=conteudo, crescer=50,
                         marca=ds.marca_da_pagina(img, (x0, y0, x1, y1), conteudo))
    assert sem.disponivel and com.disponivel
    h, w = sem.imagem.shape[:2]
    assert com.imagem.shape[:2] == (h + 100, w + 100)
    assert com.marca.shape == com.imagem.shape[:2]
    assert np.array_equal(com.imagem[50:50 + h, 50:50 + w], sem.imagem)


@precisa_da_dll
def test_marca_ruim_nao_chega_a_dll():
    img, (x0, y0, x1, y1) = _pagina_com_papel()
    r = ds.desentortar(img, 300, ds.AUTOMATICO, corte=(x0, y0, x1 - x0, y1 - y0),
                       marca=np.zeros((10, 10), np.uint8))
    assert not r.disponivel and r.motivo


# ------------------------------------------------------------- as medidas

def test_medir_o_estrago_conta_tinta_para_fora_e_fundo_para_dentro():
    c = 20
    marca = np.full((200 + 2 * c, 100 + 2 * c), ds.MARCA_PAPEL, np.uint8)
    assert ds.medir_o_estrago(marca, c, 300) == (0, 0.0)
    for k in range(4):  # quatro letras de 2 mm para fora, à esquerda
        marca[c + 20 + 40 * k:c + 44 + 40 * k, 0:c + 5] = ds.MARCA_TINTA
    marca[c:c + 20, c:c + 100] = ds.MARCA_FORA  # 10% da página veio de fora
    pecas, fundo = ds.medir_o_estrago(marca, c, 300)
    assert pecas == 4 and abs(fundo - 0.10) < 1e-6
    assert ds.recusar(pecas, 0.0) and ds.recusar(0, fundo)
    assert not ds.recusar(ds.PECAS_PARA_FORA - 1, ds.FUNDO_DENTRO_MAXIMO)


def test_pontinho_para_fora_nao_conta():
    c = 20
    marca = np.full((200 + 2 * c, 100 + 2 * c), ds.MARCA_PAPEL, np.uint8)
    for k in range(5):
        marca[5 + 30 * k:8 + 30 * k, 5:8] = ds.MARCA_TINTA  # 3 pontos: menos de 1 mm
    assert ds.medir_o_estrago(marca, c, 300)[0] == 0


def test_a_marca_tem_tinta_papel_e_fora():
    img, (x0, y0, x1, y1) = _pagina_com_papel()
    conteudo = ds.caixa_do_conteudo(img, (x0, y0, x1, y1), 300)
    marca = ds.marca_da_pagina(img, (x0, y0, x1, y1), conteudo)
    assert marca[0, 0] == ds.MARCA_FORA
    assert marca[y0 + 1, x0 + 1] == ds.MARCA_PAPEL
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    assert (marca[cinza < 128] == ds.MARCA_TINTA).mean() > 0.99


# ------------------------------------------------------------- o passo do preparo

@precisa_da_dll
def test_pagina_curva_com_corte_rente_vai_para_revisar_e_o_botao_desentorta():
    """A página curva de mentira (60 pontos perto da lombada) com o corte rente
    de 1 mm: o desentortar do ScanTailor estica o texto além do corte (medido
    em 22/10/2026: mais de 100 pedaços de tinta para fora), então a proteção
    recusa (regra P1-B do Samuel). Com "Desentortar aumentando a página" a
    página sai desentortada e maior, com toda a tinta dentro."""
    img, caixa = _pagina_com_papel()
    x0, y0, x1, y1 = caixa
    pagina = ConfigPagina(indice=0, folha=0, metade="direita", desentortar=ds.AUTOMATICO)
    preparo = ds.preparar_no_corte(img, caixa, pagina, 300)
    assert preparo.saiu_sem and preparo.pecas_para_fora >= ds.PECAS_PARA_FORA
    assert np.array_equal(preparo.imagem, img[y0:y1, x0:x1])
    pagina.desentortar_aumentar = True
    maior = ds.preparar_no_corte(img, caixa, pagina, 300)
    assert not maior.saiu_sem
    assert maior.imagem.shape[0] > y1 - y0


@precisa_da_dll
def test_quando_recusa_sai_o_corte_sem_desentortar(monkeypatch):
    img, caixa = _pagina_com_papel()
    monkeypatch.setattr(ds, "recusar", lambda pecas, fundo: True)
    pagina = ConfigPagina(indice=0, folha=0, metade="direita", desentortar=ds.AUTOMATICO)
    preparo = ds.preparar_no_corte(img, caixa, pagina, 300)
    x0, y0, x1, y1 = caixa
    assert preparo.saiu_sem
    assert np.array_equal(preparo.imagem, img[y0:y1, x0:x1])


def test_recorte_aumentado_cresce_ate_caber_a_tinta():
    c = 40
    imagem = np.full((100 + 2 * c, 80 + 2 * c), 200, np.uint8)
    marca = np.full(imagem.shape, ds.MARCA_PAPEL, np.uint8)
    assert ds._recorte_aumentado(imagem, marca, c, 300).shape == (100, 80)
    marca[c + 40:c + 60, 20:c + 10] = ds.MARCA_TINTA  # uma letra que saiu 20 pontos à esquerda
    saida = ds._recorte_aumentado(imagem, marca, c, 300)
    folga = round(ds.FOLGA_DO_AUMENTO_MM * 300 / 25.4)
    assert saida.shape == (100, 80 + (c - 20) + folga)


def test_aumentar_no_arquivo_vai_e_volta_e_o_antigo_abre_falso():
    projeto = Projeto(caminho_entrada="x.pdf")
    pagina = ConfigPagina(indice=0, folha=0, desentortar=ds.AUTOMATICO, desentortar_aumentar=True)
    projeto.folhas, projeto.paginas = [ConfigFolha(indice=0)], [pagina]
    assert Projeto.de_dicionario(projeto.para_dicionario()).paginas[0].desentortar_aumentar is True
    dados = projeto.para_dicionario()
    for p in dados["paginas"]:
        p.pop("desentortar_aumentar")
    assert Projeto.de_dicionario(dados).paginas[0].desentortar_aumentar is False
    assert ConfigPagina(indice=0, folha=0).desentortar_aumentar is False


def test_o_aviso_tem_o_botao_da_opcao_c():
    alerta = analise.descrever(analise.DESENTORTAR_SAIU_SEM)
    assert alerta.acao == "Desentortar aumentando a página"
    assert alerta.correcao == "desentortar_aumentando"


# ------------------------------------------------------------- o aviso no pipeline

def _livro(modo):
    from core import pipeline

    pipeline._GEOMETRIAS.clear()
    projeto = Projeto(caminho_entrada="x.pdf", qualidade_dpi=300, cortar_bordas=True, endireitar=False,
                      ordem_do_preparo="endireitar_antes")
    folha = ConfigFolha(indice=0)
    pagina = ConfigPagina(indice=0, folha=0, metade="direita", desentortar=modo)
    pagina.recorte = (0.04, 0.04, 0.92, 0.92)
    projeto.folhas, projeto.paginas = [folha], [pagina]
    return projeto, folha, pagina


def test_o_aviso_entra_quando_recusa_e_sai_quando_desliga(monkeypatch):
    from core import pipeline

    img = pagina_curva(curva=0)
    projeto, folha, pagina = _livro(ds.AUTOMATICO)
    pagina.revisada = True

    def recusou(reta, caixa, pag, dpi=None, **k):
        x0, y0, x1, y1 = caixa
        return ds.Preparo(reta[y0:y1, x0:x1].copy(), True, 9, 0.0)

    monkeypatch.setattr(ds, "preparar_no_corte", recusou)
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert pagina.alertas[0] == analise.DESENTORTAR_SAIU_SEM
    assert pagina.revisada is False and pagina.precisa_revisao
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert pagina.alertas.count(analise.DESENTORTAR_SAIU_SEM) == 1
    pagina.desentortar = ds.DESLIGADO
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas


def test_o_aviso_sai_quando_a_pagina_desentorta(monkeypatch):
    from core import pipeline

    img = pagina_curva(curva=0)
    projeto, folha, pagina = _livro(ds.AUTOMATICO)
    pagina.alertas = [analise.DESENTORTAR_SAIU_SEM]
    monkeypatch.setattr(ds, "preparar_no_corte",
                        lambda reta, caixa, pag, dpi=None, **k: ds.Preparo(reta.copy(), False, 0, 0.0))
    pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas


# ------------------------------------------------------------- REVERSÃO no acervo

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
RIGHETTI = ACERVO / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf"
CURSUS = ACERVO / "Cursus philosophicus. Tomo.2.pdf"


def _pagina_do_acervo(tmp_path, livro, indice, giro, dividir, metade):
    """A página do acervo (só lida) num PDF de rascunho, pelo caminho inteiro do
    programa (livro novo, de fábrica): devolve (img da folha, folha, página, projeto)."""
    import fitz
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array

    pdf = tmp_path / "pagina.pdf"
    origem, novo = fitz.open(livro), fitz.open()
    novo.insert_pdf(origem, from_page=indice, to_page=indice)
    if giro:
        novo[0].set_rotation((novo[0].rotation + giro) % 360)
    novo.save(pdf)
    novo.close()
    origem.close()
    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome="t", dividir_folhas=dividir))
    doc = abrir_pdf(str(pdf))
    try:
        pagina = [p for p in projeto.paginas_ativas if p.metade == metade][0]
        img = pagina_para_array(doc, 0, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    return img, projeto.folhas[pagina.folha], pagina, projeto


def _margem_esquerda_do_texto(img: np.ndarray) -> int:
    """Onde começa o bloco de texto (a primeira coluna com tinta em mais de 1%
    das linhas), sem a faixa preta do scanner e sem os 15 pontos da beirada."""
    t = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < 128
    t[t.mean(axis=1) > 0.5] = False
    t[:, :15] = False
    t[:, -15:] = False
    return int(np.where(t.mean(axis=0) > 0.01)[0].min())


@precisa_da_dll
@pytest.mark.skipif(not RIGHETTI.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_reversao_righetti_96_a_tinta_nao_sai_mais_da_pagina(tmp_path):
    """REVERSÃO (§4.7) do defeito da pergunta P1 de 22/10/2026: Righetti, folha
    96 (girada 270°, "Dividir" ligado), página da direita, livro novo de
    fábrica, desentortar automático. No código de antes (177f711) o automático
    ampliava o texto e o começo das linhas sumia ("mente" -> "te"): a margem
    esquerda do texto caía de 173 para ~15 pontos. Agora a proteção recusa: a
    página sai como hoje (a margem fica) e entra o aviso "Desentortar não
    usado". Com o botão (opção C), a página cresce e o texto continua inteiro."""
    from core import pipeline

    img, folha, pagina, projeto = _pagina_do_acervo(tmp_path, RIGHETTI, 95, 270, True, "direita")
    dpi = projeto.qualidade_dpi
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    pagina.desentortar = ds.AUTOMATICO
    saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert saida.shape == hoje.shape
    assert _margem_esquerda_do_texto(hoje) > 100
    assert _margem_esquerda_do_texto(saida) >= 0.8 * _margem_esquerda_do_texto(hoje)
    assert analise.DESENTORTAR_SAIU_SEM in getattr(pagina, "alertas", [])
    pagina.desentortar_aumentar = True
    maior = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert maior.shape[1] > hoje.shape[1] and maior.shape[0] >= hoje.shape[0]
    assert _margem_esquerda_do_texto(maior) > 15
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas


@precisa_da_dll
@pytest.mark.skipif(not CURSUS.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_reversao_cursus_176_pelas_margens_nao_entorta_mais_a_pagina(tmp_path):
    """REVERSÃO (§4.7) do defeito da pergunta P2 de 22/10/2026: Cursus
    philosophicus, página 176 do PDF, livro novo de fábrica, desentortar "pelas
    margens". No código de antes (177f711) a página inteira saía entortada,
    com cunha preta (pouca tinta no lugar); agora a proteção recusa e a página
    sai como hoje (a tinta toda no lugar), com o aviso."""
    from core import pipeline

    img, folha, pagina, projeto = _pagina_do_acervo(tmp_path, CURSUS, 175, 0, False, "inteira")
    dpi = projeto.qualidade_dpi
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    pagina.desentortar = ds.PELAS_MARGENS
    saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=dpi)
    assert saida.shape == hoje.shape
    assert tinta_que_ficou_no_lugar(hoje, saida, tolerancia=6) > 0.95
    assert analise.DESENTORTAR_SAIU_SEM in getattr(pagina, "alertas", [])
