"""A medida do desentortar na resolução do livro, por trás (item 2.12, 23/10/2026).

Resposta do Samuel à P6 (23/10/2026), opção (b): "Como o ScanTailor: o
desentortar sempre é medido na resolução do livro (300 DPI), numa tarefa por
trás (uns 3 a 8 s por página, só nas páginas com ele ligado), e a prévia
rápida e os cartões (Preto e branco, Melhorar, Mágico pro, Original) usam essa
medida, só reduzida. A página na tela fica igual à do PDF, e os avisos
('Desentortar não usado' com o botão, e 'A página ainda saiu deformada')
aparecem na hora." E: a tela não trava enquanto mede (tarefa por trás; até
terminar, a página sem desentortar e um sinal discreto); a medida é
reaproveitada (não mede de novo a mesma página com os mesmos ajustes).

O que se confere aqui (testes de máquina):
  1. antes da medida, o desenho pequeno NÃO chama o desentortar e não mexe nos
     avisos (a página sai sem desentortar);
  2. medir_o_desentortar faz UMA conta na resolução do livro; depois disso o
     desenho pequeno usa essa página reduzida, com os avisos, sem conta nova;
     trocar o filtro não mede de novo; trocar o modo mede de novo;
  3. desligado (o de fábrica): nada disto roda;
  4. na tela: o sinal "Desentortando esta página" aparece, a medida vem por
     trás e o sinal some;
  5. REVERSÃO na página de verdade (Righetti 96 com o botão "Desentortar
     aumentando a página"): a prévia rápida mostra a página aumentada, como o
     PDF (no 2a42cfb ela saía do tamanho de antes: o desentortar não acha a
     curva a 110 DPI).
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from core import analise
from core import desentortar_scantailor as ds
from core import st_ferramentas as st
from modelos import ConfigFolha, ConfigPagina, Projeto
from tests.test_desentortar_protecao import RIGHETTI, _pagina_do_acervo
from tests.test_desentortar_scantailor import pagina_curva

fitz = pytest.importorskip("fitz")

from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _livro_em_pdf(tmp_path, modo=ds.AUTOMATICO):
    """Um PDF de verdade (a medida precisa do arquivo no disco: a chave leva o
    caminho, a data e o tamanho) com a página de mentira a 300 DPI."""
    import cv2

    from core import pipeline

    pipeline._GEOMETRIAS.clear()
    pipeline._DESENTORTADAS.clear()
    img = pagina_curva(curva=0)
    png = tmp_path / "pagina.png"
    cv2.imwrite(str(png), img)
    pdf = tmp_path / "livro.pdf"
    doc = fitz.open()
    altura, largura = img.shape[:2]
    pag = doc.new_page(width=largura * 72 / 300, height=altura * 72 / 300)
    pag.insert_image(pag.rect, filename=str(png))
    doc.save(str(pdf))
    doc.close()
    projeto = Projeto(caminho_entrada=str(pdf), qualidade_dpi=300, cortar_bordas=True,
                      endireitar=False, ordem_do_preparo="endireitar_antes")
    folha = ConfigFolha(indice=0)
    pagina = ConfigPagina(indice=0, folha=0, desentortar=modo)
    pagina.recorte = (0.04, 0.04, 0.92, 0.92)
    projeto.folhas, projeto.paginas = [folha], [pagina]
    return projeto, folha, pagina


def _desentortar_de_mentira(monkeypatch, contas):
    """No lugar do desentortar de verdade: conta as chamadas e devolve o corte
    pintado de preto, com a proteção recusando (saiu_sem) - fácil de ver."""
    def falso(reta, caixa, pag, dpi=None, **k):
        contas.append(dpi)
        x0, y0, x1, y1 = caixa
        return ds.Preparo(np.zeros_like(reta[y0:y1, x0:x1]), True, 9, 0.0)

    monkeypatch.setattr(ds, "preparar_no_corte", falso)


def test_antes_da_medida_o_desenho_pequeno_sai_sem_desentortar(tmp_path, monkeypatch):
    from core import pipeline
    from core.pdf_io import abrir_pdf

    projeto, _, pagina = _livro_em_pdf(tmp_path)
    contas = []
    _desentortar_de_mentira(monkeypatch, contas)
    assert pipeline.desentortar_por_medir(projeto, pagina)
    assert pipeline.estado_do_desentortar(projeto, pagina) == "por_medir"
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
    finally:
        doc.close()
    assert contas == [], "o desenho pequeno não pode desentortar (não acha a curva)"
    assert img.mean() > 100, "antes da medida a página sai sem desentortar"
    assert analise.DESENTORTAR_SAIU_SEM not in pagina.alertas


def test_medida_uma_vez_e_o_desenho_pequeno_usa_ela_reduzida(tmp_path, monkeypatch):
    from core import pipeline
    from core.pdf_io import abrir_pdf

    projeto, folha, pagina = _livro_em_pdf(tmp_path)
    contas = []
    _desentortar_de_mentira(monkeypatch, contas)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        assert pipeline.medir_o_desentortar(doc, projeto, pagina) is True
        assert contas == [300]
        assert pagina.alertas[0] == analise.DESENTORTAR_SAIU_SEM, "o aviso vem com a medida"
        assert pipeline.estado_do_desentortar(projeto, pagina) == "medido"
        assert pipeline.medir_o_desentortar(doc, projeto, pagina) is False, "não mede de novo"
        pequena, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
        # trocar o filtro não mede de novo (o desentortar vem antes do filtro)
        pagina.filtro = "preto_e_branco" if pagina.filtro != "preto_e_branco" else "original"
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
        grande, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=300)
        assert contas == [300], "a medida tinha de ser reaproveitada"
        # o tamanho do desenho pequeno é o mesmo do desligado (o corte dele)
        pagina.desentortar = ds.DESLIGADO
        desligada, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
        assert pequena.shape[:2] == desligada.shape[:2]
        # trocar o modo: outra medida
        pagina.desentortar = ds.PELAS_MARGENS
        assert pipeline.desentortar_por_medir(projeto, pagina)
    finally:
        doc.close()
    assert pequena.mean() < 20, "a prévia rápida tinha de mostrar a página medida"
    assert grande.mean() < 20


def test_desligado_de_fabrica_nada_roda(tmp_path, monkeypatch):
    from core import pipeline
    from core.pdf_io import abrir_pdf

    projeto, _, pagina = _livro_em_pdf(tmp_path, ds.DESLIGADO)
    contas = []
    _desentortar_de_mentira(monkeypatch, contas)
    assert pipeline.estado_do_desentortar(projeto, pagina) == ""
    assert not pipeline.desentortar_por_medir(projeto, pagina)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        assert pipeline.medir_o_desentortar(doc, projeto, pagina) is False
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=300)
    finally:
        doc.close()
    assert contas == [] and not pipeline._DESENTORTADAS


def test_a_medida_guardada_tem_limite_de_tamanho(monkeypatch):
    from core import pipeline

    pipeline._DESENTORTADAS.clear()
    monkeypatch.setattr(pipeline, "MAX_BYTES_DESENTORTADAS", 3 * 1000)
    for i in range(5):
        pipeline._guardar_desentortada(("k", i), ds.Preparo(np.zeros((10, 100), np.uint8)), (20, 200))
    assert list(pipeline._DESENTORTADAS) == [("k", 2), ("k", 3), ("k", 4)]
    pipeline._DESENTORTADAS.clear()


def _esperar(condicao, segundos=30.0):
    from PySide6.QtWidgets import QApplication

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    return False


def test_na_tela_o_sinal_aparece_a_medida_vem_por_tras_e_o_sinal_some(conferir, monkeypatch):
    from core import pipeline

    pipeline._DESENTORTADAS.clear()
    contas = []
    _desentortar_de_mentira(monkeypatch, contas)
    assert conferir.sinal_desentortando.isHidden(), "desligado: sem sinal"
    assert conferir.sinal_desentortando.text() == "Desentortando esta página, um momento..."
    combo = conferir.combo_desentortar
    combo.setCurrentIndex(combo.findData(ds.AUTOMATICO))
    pagina = conferir.projeto.paginas[0]
    assert not conferir.sinal_desentortando.isHidden() or contas, "o sinal tinha de aparecer"
    assert _esperar(lambda: not pipeline.desentortar_por_medir(conferir.projeto, pagina))
    assert _esperar(lambda: conferir.sinal_desentortando.isHidden()), "o sinal tinha de sumir"
    assert contas and all(d == conferir.projeto.qualidade_dpi for d in contas)
    assert analise.DESENTORTAR_SAIU_SEM in pagina.alertas, "o aviso vem com a medida"
    # voltar à página não mede de novo
    n = len(contas)
    conferir.ir_para_pagina(1)
    conferir.ir_para_pagina(0)
    _esperar(lambda: False, 0.5)
    assert len(contas) == n and conferir.sinal_desentortando.isHidden()


@precisa_da_dll
@pytest.mark.skipif(not RIGHETTI.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_reversao_righetti_96_a_previa_rapida_mostra_a_pagina_aumentada(tmp_path):
    """REVERSÃO (§4.7) da P6 (23/10/2026): na prévia "Rápida" (110 DPI) o
    desentortar não aparecia - o do ScanTailor não acha a curva nessa
    resolução. Righetti 96, direita, automático, com o botão "Desentortar
    aumentando a página": no PDF (300 DPI) a página cresce (1385 -> 1600
    pontos de largura); na prévia rápida ela saía do tamanho de antes (no
    2a42cfb: a proporção das larguras 110/300 dava ~0,32 em vez de ~0,37).
    Agora a prévia é a página do PDF reduzida."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    getattr(pipeline, "_DESENTORTADAS", {}).clear()     # (no codigo antigo nao existe)
    _, _, pagina, projeto = _pagina_do_acervo(tmp_path, RIGHETTI, 95, 270, True, "direita")
    pagina.desentortar = ds.AUTOMATICO
    pagina.desentortar_aumentar = True
    doc = abrir_pdf(str(tmp_path / "pagina.pdf"))
    try:
        grande, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
        pequena, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
    finally:
        doc.close()
    proporcao = pequena.shape[1] / grande.shape[1]
    assert abs(proporcao - 110 / projeto.qualidade_dpi) < 0.01, (
        f"a prévia rápida não mostra a página do PDF (proporção {proporcao:.3f})")
