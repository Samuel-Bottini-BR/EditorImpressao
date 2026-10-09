"""O endireitar do ScanTailor ligado ao programa (item 2.2, 07/10/2026).

Decisões do Samuel (conferência 9, 05/10/2026, literais em
relatorios/conferencia-samuel-2026-10-05-g.md):
  G4 (b) "O do ScanTailor de fábrica; quando os dois discordarem mais de 0,3
     grau, a página fica marcada 'conferir' - mas eu vou ter a opção de
     escolher."
  C1 "Aviso 'conferir' quando as duas contas de endireitar discordam: Sim"
e a regra da conferência 14: "o programa quando estiver pronto, ele vai ter
que ser capaz de abrir arquivos de versões anteriores".

Testes de máquina:
- livro novo endireita pela conta do ScanTailor; projeto antigo (sem o campo)
  continua pela do programa, e a página sai IDÊNTICA à de antes;
- cada página pode trocar de conta só nela; trocar refaz a geometria;
- sem a DLL, cai na conta do programa (nada quebra);
- C1: discordância de mais de 0,3° põe a página em "Para revisar" (na
  análise e ao desenhar), com a escolha da conta; concordância tira.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import analise  # noqa: E402
from core import endireitar_scantailor as es  # noqa: E402
from core import pipeline  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from core.endireitar import detectar_angulo  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.recortar import detectar_bordas, fatiar  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# ------------------------------------------------------------------ livro de mentira

def _pdf_torto(pasta: Path, graus: float = 1.5, nome: str = "torto.pdf") -> str:
    """Uma folha A5 de "texto" girada `graus` (sentido do OpenCV), como imagem
    embutida de 200 DPI (um escaneamento)."""
    largura, altura = 1165, 1654                      # A5 a 200 DPI
    img = np.full((altura, largura), 255, np.uint8)
    for y in range(180, altura - 180, 34):
        for x in range(130, largura - 170, 52):
            cv2.rectangle(img, (x, y), (x + 38, y + 14), 0, -1)
    m = cv2.getRotationMatrix2D((largura / 2, altura / 2), graus, 1.0)
    img = cv2.warpAffine(img, m, (largura, altura), borderValue=255)
    png = pasta / (nome + ".png")
    cv2.imwrite(str(png), img)
    caminho = pasta / nome
    doc = fitz.open()
    pagina = doc.new_page(width=largura * 72 / 200, height=altura * 72 / 200)
    pagina.insert_image(pagina.rect, filename=str(png))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _projeto(caminho: str, **campos) -> Projeto:
    projeto = Projeto(caminho_entrada=caminho, qualidade_dpi=300, **campos)
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    return projeto


def _base(caminho: str, projeto: Projeto) -> np.ndarray:
    from core.pdf_io import pagina_para_array

    doc = abrir_pdf(caminho)
    try:
        img = pagina_para_array(doc, 0, dpi=300)
    finally:
        doc.close()
    return pipeline.preparar_para_recorte(img, projeto.folhas[0], projeto.paginas[0], projeto)


@pytest.fixture(autouse=True)
def _sem_geometrias_guardadas():
    pipeline._GEOMETRIAS.clear()
    pipeline._ANGULOS_MEDIDOS.clear()
    yield
    pipeline._GEOMETRIAS.clear()
    pipeline._ANGULOS_MEDIDOS.clear()


def _medida_fixa(angulo):
    def medir(*_args, **_kwargs):
        return es.Medida(angulo, angulo, 5.0, True, 300.0)
    return medir


# ------------------------------------------------------------------ o modelo

def test_livro_novo_pela_conta_do_scantailor():
    projeto = Projeto(caminho_entrada="x.pdf")
    assert projeto.endireitar_como == es.JEITO_SCANTAILOR == es.PADRAO
    assert ConfigPagina(indice=0, folha=0).endireitar_como is None


def test_projeto_antigo_sem_o_campo_fica_com_a_conta_do_programa():
    dados = Projeto(caminho_entrada="x.pdf").para_dicionario()
    dados.pop("endireitar_como")
    for p in dados["paginas"]:
        p.pop("endireitar_como", None)
    assert Projeto.de_dicionario(dados).endireitar_como == es.JEITO_PROGRAMA


def test_campos_vao_e_voltam_do_arquivo():
    projeto = Projeto(caminho_entrada="x.pdf", endireitar_como=es.JEITO_PROGRAMA)
    projeto.paginas = [ConfigPagina(indice=0, folha=0, endireitar_como=es.JEITO_SCANTAILOR)]
    volta = Projeto.de_dicionario(projeto.para_dicionario())
    assert volta.endireitar_como == es.JEITO_PROGRAMA
    assert volta.paginas[0].endireitar_como == es.JEITO_SCANTAILOR


# ------------------------------------------------------------------ a conta que vale

def _angulo_do_programa(base: np.ndarray) -> float:
    """A conta de sempre: detectar_angulo na página já cortada pelo automático."""
    return detectar_angulo(fatiar(base, detectar_bordas(base, dpi=300).tupla)).angulo


def test_conta_do_programa_e_a_de_sempre(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path)
    projeto = _projeto(caminho, endireitar_como=es.JEITO_PROGRAMA)
    base = _base(caminho, projeto)
    # o ScanTailor nem é chamado num livro antigo (sai idêntico e não fica mais lento)
    monkeypatch.setattr(es, "medir_na_pagina", lambda *a, **k: pytest.fail("chamou o ScanTailor"))
    _, angulo = pipeline._geometria(base, projeto.paginas[0], projeto, dpi=300)
    assert angulo == _angulo_do_programa(base)


def test_conta_do_scantailor_vale_no_livro_novo(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path)
    projeto = _projeto(caminho)
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.7))
    _, angulo = pipeline._geometria(_base(caminho, projeto), projeto.paginas[0], projeto, dpi=300)
    assert angulo == pytest.approx(0.7)


def test_a_pagina_troca_de_conta_so_nela(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path)
    projeto = _projeto(caminho)
    projeto.paginas[0].endireitar_como = es.JEITO_PROGRAMA
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.7))
    base = _base(caminho, projeto)
    _, angulo = pipeline._geometria(base, projeto.paginas[0], projeto, dpi=300)
    assert angulo == _angulo_do_programa(base)


def test_sem_a_dll_cai_na_conta_do_programa(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path)
    projeto = _projeto(caminho)
    monkeypatch.setattr(es, "medir_na_pagina",
                        lambda *a, **k: es.Medida(None, motivo="sem a DLL"))
    base = _base(caminho, projeto)
    _, angulo = pipeline._geometria(base, projeto.paginas[0], projeto, dpi=300)
    assert angulo == _angulo_do_programa(base)


def test_trocar_de_conta_muda_a_chave_da_geometria(tmp_path):
    caminho = _pdf_torto(tmp_path)
    projeto = _projeto(caminho)
    folha, pagina = projeto.folhas[0], projeto.paginas[0]
    antes = pipeline._chave_da_geometria(folha, pagina, projeto)
    pagina.endireitar_como = es.JEITO_PROGRAMA
    assert pipeline._chave_da_geometria(folha, pagina, projeto) != antes


@precisa_da_dll
def test_scantailor_de_verdade_endireita_a_folha(tmp_path):
    """A folha está girada +1,5° (OpenCV): a conta do ScanTailor manda girar
    -1,5° (o sentido do programa), como a do programa."""
    caminho = _pdf_torto(tmp_path, 1.5)
    projeto = _projeto(caminho)
    _, angulo = pipeline._geometria(_base(caminho, projeto), projeto.paginas[0], projeto, dpi=300)
    assert angulo == pytest.approx(-1.5, abs=0.15)


def test_projeto_antigo_sai_identico(tmp_path, monkeypatch):
    """Projeto gravado antes do item 2.2 (sem endireitar_como): a página
    desenhada é a mesma, ponto por ponto, que a da conta do programa."""
    caminho = _pdf_torto(tmp_path)
    novo = _projeto(caminho, endireitar_como=es.JEITO_PROGRAMA)
    dados = novo.para_dicionario()
    dados.pop("endireitar_como")
    antigo = Projeto.de_dicionario(dados)
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(3.0))   # se fosse chamado, mudaria tudo
    doc = abrir_pdf(caminho)
    try:
        img_antigo, _ = pipeline.renderizar_pagina(doc, antigo, antigo.paginas[0], dpi=300)
        pipeline._GEOMETRIAS.clear()
        img_novo, _ = pipeline.renderizar_pagina(doc, novo, novo.paginas[0], dpi=300)
    finally:
        doc.close()
    assert np.array_equal(img_antigo, img_novo)


# ------------------------------------------------------------------ C1

def test_alerta_existe_com_texto_em_portugues():
    alerta = analise.descrever(analise.CONTAS_DO_ENDIREITAR_DISCORDAM)
    assert "endireitar" in alerta.mensagem.lower()
    assert alerta.acao and alerta.correcao


def test_discordancia_ao_desenhar_poe_e_concordancia_tira(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path, 1.5)              # o programa acha ~ -1,5
    projeto = _projeto(caminho)
    pagina = projeto.paginas[0]
    pagina.revisada = True
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.0))
    doc = abrir_pdf(caminho)
    try:
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=100)
        assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM in pagina.alertas
        assert pagina.revisada is False                 # volta para "Para revisar"
        medidos = pipeline.angulos_medidos(projeto, pagina)
        assert medidos["scantailor"] == pytest.approx(0.0)
        assert medidos["programa"] == pytest.approx(-1.5, abs=0.2)
        # as duas concordam: o alerta sai
        pipeline._GEOMETRIAS.clear()
        pipeline._ANGULOS_MEDIDOS.clear()
        monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(medidos["programa"]))
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=100)
        assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM not in pagina.alertas
    finally:
        doc.close()


def test_angulo_a_mao_nao_pede_conferir(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path, 1.5)
    projeto = _projeto(caminho)
    pagina = projeto.paginas[0]
    pagina.angulo_manual = -1.0
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.0))
    doc = abrir_pdf(caminho)
    try:
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=100)
    finally:
        doc.close()
    assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM not in pagina.alertas


def test_livro_antigo_nao_ganha_o_alerta(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path, 1.5)
    projeto = _projeto(caminho, endireitar_como=es.JEITO_PROGRAMA)
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.0))
    doc = abrir_pdf(caminho)
    try:
        pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=100)
    finally:
        doc.close()
    assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM not in projeto.paginas[0].alertas


def test_discordancia_na_analise(tmp_path, monkeypatch):
    caminho = _pdf_torto(tmp_path, 1.5)
    projeto = Projeto(caminho_entrada=caminho)
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(0.0))
    pipeline.analisar_projeto(projeto)
    assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM in projeto.paginas[0].alertas
    projeto = Projeto(caminho_entrada=caminho)
    monkeypatch.setattr(es, "medir_na_pagina", _medida_fixa(-1.5))
    pipeline.analisar_projeto(projeto)
    assert analise.CONTAS_DO_ENDIREITAR_DISCORDAM not in projeto.paginas[0].alertas
