"""O dividir ligado ao programa (item 2.1, 06/10/2026).

Decisões do Samuel: G2 (a) "Só quando o Kaique pedir, livro a livro,
escolhendo 'o do programa' ou 'o do ScanTailor', e trocando numa folha se um
ficar ruim"; G3 (b) o "corte da sobra" do ScanTailor como opção, desligada;
e "o programa vai ter que ser capaz de abrir arquivos de versões anteriores".

Testes de máquina:
- livro novo não divide; o jeito de fábrica é o do programa; sobra desligada;
- projeto antigo (sem os campos novos) abre como estava: o que dividia
  continua dividindo, pelo jeito do programa;
- a análise pelo jeito do programa é a de sempre; pelo do ScanTailor divide
  onde a DLL diz; sem a DLL, cai no do programa;
- o corte da sobra: só com o livro marcado, só em folha não dividida e sem
  giro; a página sai mais estreita na medida certa; as zonas (D2) acompanham;
- conserto junto: "não dividir esta" não repete mais a folha no PDF;
- o trabalho salvo volta com o jeito novo do livro (trazer_divisao_da_analise),
  e não volta se as folhas divididas mudaram (projetos.combina_com).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from core import dividir_scantailor as ds  # noqa: E402
from core import pipeline  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from core import zonas_na_folha as zf  # noqa: E402
from core.dividir import detectar_lombada  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from modelos import METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigFolha, ConfigPagina, Projeto  # noqa: E402

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# ------------------------------------------------------------------ livros de mentira

def _pdf_deitado(pasta: Path, dobra: float = 0.6, folhas: int = 2) -> str:
    """Folhas deitadas com duas páginas de texto e a dobra (linha escura) em `dobra`."""
    caminho = pasta / "deitado.pdf"
    doc = fitz.open()
    largura, altura = 842, 595
    x = largura * dobra
    for _ in range(folhas):
        pagina = doc.new_page(width=largura, height=altura)
        for y in range(70, altura - 60, 16):
            pagina.insert_text((40, y), "texto da esquerda " * 2, fontsize=9)
            pagina.insert_text((x + 30, y), "direita " * 3, fontsize=9)
        pagina.draw_line((x, 0), (x, altura), width=4, color=(0.25, 0.25, 0.25))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _pdf_em_pe_com_sobra(pasta: Path) -> str:
    """Uma folha em pé com a beirada da página vizinha à direita (uma linha
    escura de cima a baixo e pedaços de texto depois dela)."""
    caminho = pasta / "em_pe.pdf"
    doc = fitz.open()
    largura, altura = 500, 700
    pagina = doc.new_page(width=largura, height=altura)
    for y in range(60, altura - 50, 14):
        pagina.insert_text((40, y), "linha de texto da pagina " * 2, fontsize=9)
        pagina.insert_text((462, y), "vi", fontsize=9)
    pagina.draw_line((450, 0), (450, altura), width=5, color=(0.15, 0.15, 0.15))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


# ------------------------------------------------------------------ o modelo

def test_livro_novo_nao_divide_e_o_jeito_e_o_do_programa():
    projeto = Projeto(caminho_entrada="x.pdf")
    assert projeto.dividir_folhas is False
    assert projeto.dividir_como == ds.JEITO_PROGRAMA
    assert projeto.cortar_sobra is False
    folha = ConfigFolha(indice=0)
    assert folha.dividir_como is None and folha.sobra is None


def test_projeto_antigo_abre_como_estava():
    """projeto.json gravado antes do item 2.1: sem dividir_como, cortar_sobra
    e os campos novos da folha."""
    antigo = {
        "caminho_entrada": "x.pdf", "dividir_folhas": True,
        "folhas": [{"indice": 0, "dividir": True, "posicao_corte": 0.53}],
        "paginas": [{"indice": 0, "folha": 0, "metade": "esquerda"},
                    {"indice": 1, "folha": 0, "metade": "direita"}],
    }
    projeto = Projeto.de_dicionario(json.loads(json.dumps(antigo)))
    assert projeto.dividir_folhas is True
    assert projeto.dividir_como == ds.JEITO_PROGRAMA
    assert projeto.cortar_sobra is False
    assert projeto.folhas[0].dividir and projeto.folhas[0].posicao_corte == 0.53
    assert projeto.folhas[0].dividir_como is None and projeto.folhas[0].sobra is None
    # sem o campo dividir_folhas (nao deveria existir, mas era o de fabrica)
    sem = Projeto.de_dicionario({"caminho_entrada": "x.pdf"})
    assert sem.dividir_folhas is True


def test_ida_e_volta_pelo_disco():
    projeto = Projeto(caminho_entrada="x.pdf", dividir_folhas=True,
                      dividir_como=ds.JEITO_SCANTAILOR, cortar_sobra=True)
    projeto.folhas = [ConfigFolha(indice=0, dividir=False, sobra=(0.05, 0.93),
                                  dividir_como=ds.JEITO_PROGRAMA)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    volta = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert volta.dividir_como == ds.JEITO_SCANTAILOR and volta.cortar_sobra
    assert volta.folhas[0].sobra == (0.05, 0.93)
    assert volta.folhas[0].dividir_como == ds.JEITO_PROGRAMA


# ------------------------------------------------------------------ a análise

def test_jeito_do_programa_e_o_de_sempre(tmp_path):
    caminho = _pdf_deitado(tmp_path, dobra=0.6)
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=True,
                      endireitar=False, cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    doc = abrir_pdf(caminho)
    img = pagina_para_array(doc, 0, dpi=pipeline.DPI_ANALISE)
    doc.close()
    esperado = detectar_lombada(img)
    assert projeto.folhas[0].dividir
    assert projeto.folhas[0].posicao_corte == esperado.posicao
    assert projeto.folhas[0].confianca_corte == esperado.confianca
    assert [p.metade for p in projeto.paginas] == [METADE_ESQUERDA, METADE_DIREITA] * 2


def test_sem_marcar_nao_divide(tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_deitado(tmp_path), endireitar=False,
                      cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    assert not any(f.dividir for f in projeto.folhas)
    assert [p.metade for p in projeto.paginas] == [METADE_INTEIRA] * 2


@precisa_da_dll
def test_jeito_do_scantailor_divide_onde_a_dll_diz(tmp_path):
    caminho = _pdf_deitado(tmp_path, dobra=0.6)
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=True,
                      dividir_como=ds.JEITO_SCANTAILOR, endireitar=False, cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    doc = abrir_pdf(caminho)
    img = pagina_para_array(doc, 0, dpi=pipeline.DPI_ANALISE)
    doc.close()
    esperado = ds.posicao_da_divisao(ds.achar(img, pipeline.DPI_ANALISE))
    assert projeto.folhas[0].dividir
    assert projeto.folhas[0].posicao_corte == pytest.approx(esperado)
    assert projeto.folhas[0].posicao_corte == pytest.approx(0.6, abs=0.02)
    assert len(projeto.paginas) == 4


def test_sem_a_dll_o_scantailor_cai_no_do_programa(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "achar", lambda *a, **k: ds.Resultado(None, (), "sem DLL"))
    caminho = _pdf_deitado(tmp_path, dobra=0.6)
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=True,
                      dividir_como=ds.JEITO_SCANTAILOR, endireitar=False, cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    doc = abrir_pdf(caminho)
    img = pagina_para_array(doc, 0, dpi=pipeline.DPI_ANALISE)
    doc.close()
    assert projeto.folhas[0].posicao_corte == detectar_lombada(img).posicao


@precisa_da_dll
def test_recalcular_divisao_de_uma_folha(tmp_path):
    caminho = _pdf_deitado(tmp_path, dobra=0.6)
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=True,
                      endireitar=False, cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    lombada = pipeline.recalcular_divisao(projeto, 1, ds.JEITO_SCANTAILOR)
    assert lombada.e_paisagem and lombada.posicao == pytest.approx(0.6, abs=0.02)
    assert pipeline.jeito_de_dividir(projeto, projeto.folhas[1]) == ds.JEITO_PROGRAMA
    projeto.folhas[1].dividir_como = ds.JEITO_SCANTAILOR
    assert pipeline.jeito_de_dividir(projeto, projeto.folhas[1]) == ds.JEITO_SCANTAILOR


# ------------------------------------------------------------------ o corte da sobra

def test_faixa_da_sobra_so_vale_nas_condicoes_certas():
    projeto = Projeto(caminho_entrada="x.pdf", cortar_sobra=True)
    folha = ConfigFolha(indice=0, dividir=False, sobra=(0.05, 0.9))
    inteira = ConfigPagina(indice=0, folha=0)
    assert pipeline.faixa_da_sobra(folha, inteira, projeto) == (0.05, 0.9)
    assert pipeline.faixa_da_sobra(folha, inteira, None) is None
    projeto.cortar_sobra = False
    assert pipeline.faixa_da_sobra(folha, inteira, projeto) is None
    projeto.cortar_sobra = True
    folha.rotacao = 90                      # girada: a sobra medida ja nao vale
    assert pipeline.faixa_da_sobra(folha, inteira, projeto) is None
    folha.rotacao = 0
    dividida = ConfigFolha(indice=0, dividir=True, sobra=(0.05, 0.9))
    assert pipeline.faixa_da_sobra(dividida, ConfigPagina(indice=0, folha=0, metade=METADE_ESQUERDA),
                                   projeto) is None
    folha.sobra = (0.5, 0.6)                # estreita demais: nao corta
    assert pipeline.faixa_da_sobra(folha, inteira, projeto) is None


@precisa_da_dll
def test_corte_da_sobra_estreita_a_pagina(tmp_path):
    caminho = _pdf_em_pe_com_sobra(tmp_path)
    sem = Projeto(caminho_entrada=caminho, endireitar=False, cortar_bordas=False)
    pipeline.analisar_projeto(sem)
    assert sem.folhas[0].sobra is None

    com = Projeto(caminho_entrada=caminho, endireitar=False, cortar_bordas=False, cortar_sobra=True)
    pipeline.analisar_projeto(com)
    sobra = com.folhas[0].sobra
    assert sobra is not None, "o ScanTailor nao achou a beirada da vizinha"
    a, b = sobra
    assert a < 0.05 and 0.85 < b < 0.93          # a linha esta a 90% da largura

    doc = abrir_pdf(caminho)
    img = pagina_para_array(doc, 0, dpi=100)
    doc.close()
    pagina = com.paginas[0]
    saida = pipeline.preparar_metade(img, com.folhas[0], pagina, com)
    largura = img.shape[1]
    esperado = int(round(b * largura)) - int(round(a * largura))
    assert saida.shape[1] == esperado
    inteira = pipeline.preparar_metade(img, sem.folhas[0], sem.paginas[0], sem)
    assert inteira.shape[1] == largura


def test_zonas_acompanham_o_corte_da_sobra():
    """Uma zona presa a folha original cai no mesmo pedaco com e sem a sobra."""
    sem = zf.geometria_do_desenho(0.7, 0, None, METADE_INTEIRA, None, 0.0)
    com = zf.geometria_do_desenho(0.7, 0, None, METADE_INTEIRA, None, 0.0, sobra=(0.1, 0.9))
    assert "sobra" not in sem                      # geometria de antes do 2.1: igual
    assert zf.geometria_valida(com) and not zf.mesma_geometria(sem, com)
    zona = [{"forma": "retangulo", "pontos": [[0.3, 0.2], [0.5, 0.4]], "filtro": "original"}]
    na_folha = zf.pagina_para_folha(zona, sem)
    na_pagina = zf.folha_para_pagina(na_folha, com)
    (x0, y0), (x1, y1) = na_pagina[0]["pontos"]
    assert x0 == pytest.approx((0.3 - 0.1) / 0.8) and x1 == pytest.approx((0.5 - 0.1) / 0.8)
    assert (y0, y1) == pytest.approx((0.2, 0.4))
    volta = zf.pagina_para_folha(na_pagina, com)
    assert np.allclose(np.asarray(volta[0]["pontos"], float), np.asarray(na_folha[0]["pontos"], float))


def test_chave_da_previa_muda_com_a_sobra(tmp_path):
    caminho = _pdf_em_pe_com_sobra(tmp_path)
    projeto = Projeto(caminho_entrada=caminho, cortar_sobra=True)
    folha = ConfigFolha(indice=0, dividir=False, sobra=(0.02, 0.9))
    pagina = ConfigPagina(indice=0, folha=0)
    com = pipeline._chave_da_geometria(folha, pagina, projeto)
    projeto.cortar_sobra = False
    assert pipeline._chave_da_geometria(folha, pagina, projeto) != com


# ------------------------------------------------------------------ "não dividir esta"

def test_nao_dividir_esta_nao_repete_a_folha_no_pdf(tmp_path):
    """Conserto junto do 2.1: antes saiam 4 paginas (a folha inteira duas vezes)."""
    caminho = _pdf_deitado(tmp_path, dobra=0.5)
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=True, endireitar=False,
                      cortar_bordas=False)
    pipeline.analisar_projeto(projeto)
    projeto.folhas[0].dividir = False
    assert [p.indice for p in projeto.paginas_ativas] == [0, 2, 3]
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    doc = fitz.open(pipeline.processar(projeto))
    larguras = [round(p.rect.width) for p in doc]
    doc.close()
    assert len(larguras) == 3
    assert larguras[0] > larguras[1]           # a primeira e a folha inteira


# ------------------------------------------------------------------ o trabalho salvo

def _projeto_com_folhas(jeito, divisoes, posicoes):
    projeto = Projeto(caminho_entrada="x.pdf", dividir_folhas=True, dividir_como=jeito)
    projeto.folhas = [ConfigFolha(indice=i, dividir=d, posicao_corte=p)
                      for i, (d, p) in enumerate(zip(divisoes, posicoes))]
    paginas = []
    for f in projeto.folhas:
        metades = [METADE_ESQUERDA, METADE_DIREITA] if f.dividir else [METADE_INTEIRA]
        for metade in metades:
            paginas.append(ConfigPagina(indice=len(paginas), folha=f.indice, metade=metade))
    projeto.paginas = paginas
    return projeto


def test_trabalho_salvo_volta_com_o_jeito_novo_do_livro():
    salvo = _projeto_com_folhas(ds.JEITO_PROGRAMA, [True, True, False], [0.5, 0.52, 0.5])
    salvo.folhas[1].dividir_como = ds.JEITO_PROGRAMA      # trocado a mao: fica
    fresco = _projeto_com_folhas(ds.JEITO_SCANTAILOR, [True, True, False], [0.61, 0.62, 0.5])
    fresco.cortar_sobra = True
    fresco.folhas[2].sobra = (0.03, 0.95)
    assert pipeline.trazer_divisao_da_analise(salvo, fresco) == 2
    assert salvo.dividir_como == ds.JEITO_SCANTAILOR and salvo.cortar_sobra
    assert [f.posicao_corte for f in salvo.folhas] == [0.61, 0.52, 0.5]
    assert salvo.folhas[2].sobra == (0.03, 0.95)
    # o mesmo jeito: as posicoes do salvo ficam (a pessoa pode ter arrastado a linha)
    salvo.folhas[0].posicao_corte = 0.4
    assert pipeline.trazer_divisao_da_analise(salvo, fresco) == 0
    assert salvo.folhas[0].posicao_corte == 0.4


def test_outras_folhas_divididas_nao_combinam():
    salvo = _projeto_com_folhas(ds.JEITO_PROGRAMA, [True, False], [0.5, 0.5])
    fresco = _projeto_com_folhas(ds.JEITO_SCANTAILOR, [False, True], [0.5, 0.5])
    assert len(salvo.paginas) == len(fresco.paginas)
    motivo = projetos.motivo_para_nao_combinar(salvo, fresco)
    assert "jeito de dividir" in motivo
    assert projetos.motivo_para_nao_combinar(salvo, _projeto_com_folhas(
        ds.JEITO_SCANTAILOR, [True, False], [0.6, 0.5])) == ""
