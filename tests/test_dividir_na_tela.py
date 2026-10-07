"""O dividir na tela (item 2.1, 06/10/2026; aparência provisória até o layout).

Decisões do Samuel G2 (a) e G3 (b) (05/10/2026). Testes de máquina, sem
janela na tela (tests/conftest.py):
- tela "O que fazer": livro novo com "Dividir folhas ao meio" desmarcada; a
  lista "Jeito de dividir:" só aparece com ela marcada; a escolha e a caixinha
  "Cortar a beirada da folha vizinha" vão para o projeto e voltam ao reabrir;
- aba "Onde cortar": a lista "jeito:" troca o jeito SÓ desta folha, numa ação
  do desfazer; "não dividir esta" apaga a metade da direita junto (o PDF não
  repete a folha) e o desfazer devolve as duas coisas; folha de uma página só
  não oferece "dividir esta".
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import dividir_scantailor as ds  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    app,
    janela,
    pasta,
)

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _pdf_deitado(pasta, dobra=0.6, folhas=3):
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Aberto.pdf"
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


def _conferir_dividido(janela, pasta, jeito=ds.JEITO_PROGRAMA):
    janela.abrir_livro(_pdf_deitado(pasta))
    opcoes = janela.tela_opcoes
    opcoes.cx_dividir.setChecked(True)
    opcoes.combo_jeito_dividir.setCurrentIndex(opcoes.combo_jeito_dividir.findData(jeito))
    _analisar(janela)
    tela = janela.tela_conferir
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("corte"))
    return tela


# ------------------------------------------------------------------ "O que fazer"

def test_livro_novo_nao_divide_e_o_jeito_so_aparece_marcado(janela, pasta):
    janela.abrir_livro(_pdf_deitado(pasta))
    opcoes = janela.tela_opcoes
    assert not opcoes.cx_dividir.isChecked() and not janela.projeto.dividir_folhas
    assert opcoes.linha_jeito_dividir.isHidden()
    assert not opcoes.cx_cortar_sobra.isChecked() and not janela.projeto.cortar_sobra
    opcoes.cx_dividir.setChecked(True)
    assert not opcoes.linha_jeito_dividir.isHidden()
    assert [opcoes.combo_jeito_dividir.itemText(i) for i in range(opcoes.combo_jeito_dividir.count())] \
        == ["o do programa", "o do ScanTailor"]
    opcoes.combo_jeito_dividir.setCurrentIndex(opcoes.combo_jeito_dividir.findData(ds.JEITO_SCANTAILOR))
    opcoes.cx_cortar_sobra.setChecked(True)
    assert janela.projeto.dividir_como == ds.JEITO_SCANTAILOR
    assert janela.projeto.cortar_sobra
    assert "ScanTailor" in opcoes.resumo.text()


@precisa_da_dll
def test_as_escolhas_voltam_ao_reabrir(janela, pasta):
    tela = _conferir_dividido(janela, pasta, ds.JEITO_SCANTAILOR)
    assert tela is not None
    janela._salvar_agora()
    caminho = janela.projeto.caminho_entrada
    janela.previas.parar()
    janela.previas = None
    janela.tela_opcoes.folhear.fechar()
    janela.abrir_livro(caminho)
    assert janela.projeto.dividir_folhas
    assert janela.projeto.dividir_como == ds.JEITO_SCANTAILOR
    assert janela.tela_opcoes.combo_jeito_dividir.currentData() == ds.JEITO_SCANTAILOR


# ------------------------------------------------------------------ "Onde cortar"

@precisa_da_dll
def test_trocar_o_jeito_so_desta_folha_e_desfazer(janela, pasta):
    tela = _conferir_dividido(janela, pasta, ds.JEITO_PROGRAMA)
    projeto = janela.projeto
    antes = [f.posicao_corte for f in projeto.folhas]
    assert tela.combo_jeito_da_folha.isEnabled()
    assert tela.combo_jeito_da_folha.currentData() == ds.JEITO_PROGRAMA
    tela.combo_jeito_da_folha.setCurrentIndex(tela.combo_jeito_da_folha.findData(ds.JEITO_SCANTAILOR))
    assert projeto.folhas[0].dividir_como == ds.JEITO_SCANTAILOR
    assert projeto.folhas[0].posicao_corte == pytest.approx(0.6, abs=0.02)
    assert [f.posicao_corte for f in projeto.folhas[1:]] == antes[1:]
    tela.desfazer()
    assert projeto.folhas[0].dividir_como is None
    assert projeto.folhas[0].posicao_corte == antes[0]
    assert tela.combo_jeito_da_folha.currentData() == ds.JEITO_PROGRAMA


def test_nao_dividir_esta_apaga_a_direita_e_o_desfazer_devolve(janela, pasta):
    tela = _conferir_dividido(janela, pasta)
    projeto = janela.projeto
    assert len(projeto.paginas_ativas) == 6
    tela._alternar_dividir()
    assert not projeto.folhas[0].dividir
    assert projeto.paginas[1].apagada and not projeto.paginas[0].apagada
    assert len(projeto.paginas_ativas) == 5
    assert tela.botao_nao_dividir.text() == "dividir esta"
    assert not tela.combo_jeito_da_folha.isEnabled()
    tela.desfazer()
    assert projeto.folhas[0].dividir and not projeto.paginas[1].apagada
    assert len(projeto.paginas_ativas) == 6
    tela._alternar_dividir()
    tela._alternar_dividir()              # "dividir esta": a direita volta
    assert projeto.folhas[0].dividir and not projeto.paginas[1].apagada


def test_folha_de_uma_pagina_nao_oferece_dividir(janela, pasta):
    tela = _conferir_dividido(janela, pasta)
    projeto = janela.projeto
    # uma folha que entrou como pagina inteira (como uma capa em pe)
    projeto.folhas[0].dividir = False
    projeto.paginas = [p for p in projeto.paginas if not (p.folha == 0 and p.metade == "direita")]
    projeto.paginas[0].metade = "inteira"
    for i, p in enumerate(projeto.paginas):
        p.indice = i
    tela.indice_folha = 0
    tela.atualizar()
    assert not tela.botao_nao_dividir.isEnabled()
    tela._alternar_dividir()              # a sugestao do alerta: so confere
    assert not projeto.folhas[0].dividir and projeto.folhas[0].revisada
    assert len(projeto.paginas) == 5


def test_nao_dividir_espera_as_zonas_antigas(janela, pasta, monkeypatch):
    """A pendencia da D2 (ver tests/test_girar_cartoes_e_previas.py): mudar a
    divisao de uma folha com zonas ainda no formato antigo espera a conversao."""
    from core import zonas_na_folha as zf
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao

    monkeypatch.setattr(zf, "acompanhar", lambda pagina, geometria: False)
    tela = _conferir_dividido(janela, pasta)
    janela.avisos = []
    monkeypatch.setattr(janela, "avisar", lambda mensagem, titulo="": janela.avisos.append(mensagem))
    pagina = janela.projeto.paginas[0]
    pagina.selecao = [Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.4, 0.3)],
                             origem=MAO).para_dicionario()]
    pagina.geometria_das_zonas = None
    monkeypatch.setattr(janela, "_comecar_a_converter_as_zonas", lambda: None)
    feitas = len(janela.acoes.feitas)
    tela._alternar_dividir()
    assert janela.projeto.folhas[0].dividir and not janela.projeto.paginas[1].apagada
    assert len(janela.acoes.feitas) == feitas
    assert janela.avisos and "preparando as marcações" in janela.avisos[-1]
