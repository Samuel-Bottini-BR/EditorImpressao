"""O endireitar do ScanTailor na tela (item 2.2, 07/10/2026; aparência
provisória até o layout).

Decisão G4 (b) do Samuel (05/10/2026): "O do ScanTailor de fábrica [...] mas
eu vou ter a opção de escolher". Testes de máquina, sem janela na tela
(tests/conftest.py):
- tela "O que fazer": a lista "Conta do endireitar:" só aparece com
  "Endireitar folhas tortas" marcada, com "a do ScanTailor" escolhida no livro
  novo; a escolha vai para o projeto e volta ao reabrir; projeto antigo (sem o
  campo) reabre com "a do programa";
- aba "Endireitar": a lista "conta:" troca a conta SÓ desta página, numa ação
  do desfazer; com o ângulo a mão ela fica apagada; o texto dos dois ângulos.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

from core import endireitar_scantailor as es  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    app,
    janela,
    pasta,
)
from ui.tela_conferir import texto_dos_angulos_medidos  # noqa: E402


def _pdf(pasta, folhas=2):
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Texto.pdf"
    doc = fitz.open()
    for _ in range(folhas):
        pagina = doc.new_page(width=420, height=595)
        for y in range(70, 540, 16):
            pagina.insert_text((40, y), "texto corrido da pagina " * 2, fontsize=9)
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _aba_endireitar(janela, pasta):
    janela.abrir_livro(_pdf(pasta))
    _analisar(janela)
    tela = janela.tela_conferir
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("angulo"))
    return tela


# ------------------------------------------------------------------ "O que fazer"

def test_livro_novo_pela_conta_do_scantailor_e_a_lista_so_com_endireitar(janela, pasta):
    janela.abrir_livro(_pdf(pasta))
    opcoes = janela.tela_opcoes
    assert opcoes.cx_endireitar.isChecked()
    assert not opcoes.linha_conta_endireitar.isHidden()
    assert [opcoes.combo_conta_endireitar.itemText(i)
            for i in range(opcoes.combo_conta_endireitar.count())] \
        == ["a do ScanTailor", "a do programa"]
    assert opcoes.combo_conta_endireitar.currentData() == es.JEITO_SCANTAILOR
    assert janela.projeto.endireitar_como == es.JEITO_SCANTAILOR
    opcoes.combo_conta_endireitar.setCurrentIndex(
        opcoes.combo_conta_endireitar.findData(es.JEITO_PROGRAMA))
    assert janela.projeto.endireitar_como == es.JEITO_PROGRAMA
    opcoes.cx_endireitar.setChecked(False)
    assert opcoes.linha_conta_endireitar.isHidden()
    assert janela.projeto.endireitar_como == es.JEITO_PROGRAMA      # escondida, fica guardada


def test_a_escolha_volta_ao_reabrir_e_o_projeto_antigo_fica_com_a_do_programa(janela, pasta):
    import projetos

    janela.abrir_livro(_pdf(pasta))
    opcoes = janela.tela_opcoes
    opcoes.combo_conta_endireitar.setCurrentIndex(
        opcoes.combo_conta_endireitar.findData(es.JEITO_PROGRAMA))
    _analisar(janela)
    janela._salvar_agora()
    assert projetos.esperar_gravacoes(10)
    caminho = janela.projeto.caminho_entrada
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO

    def reabrir():
        if janela.previas is not None:          # reaberto sem conferir: nao ha previas
            janela.previas.parar()
            janela.previas = None
        janela.tela_opcoes.folhear.fechar()
        janela.abrir_livro(caminho)

    reabrir()
    assert janela.projeto.endireitar_como == es.JEITO_PROGRAMA
    assert janela.tela_opcoes.combo_conta_endireitar.currentData() == es.JEITO_PROGRAMA

    # o programa de antes do 2.2 grava sem o campo: volta "a do programa",
    # mesmo que o de fabrica agora seja a do ScanTailor
    dados = json.loads(estado.read_text(encoding="utf-8"))
    assert dados["endireitar_como"] == es.JEITO_PROGRAMA
    dados.pop("endireitar_como")
    for p in dados.get("paginas", []):
        p.pop("endireitar_como", None)
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    reabrir()
    assert janela.projeto.endireitar_como == es.JEITO_PROGRAMA
    assert janela.tela_opcoes.combo_conta_endireitar.currentData() == es.JEITO_PROGRAMA


# ------------------------------------------------------------------ "Endireitar"

def test_trocar_a_conta_so_desta_pagina_e_desfazer(janela, pasta):
    tela = _aba_endireitar(janela, pasta)
    projeto = janela.projeto
    assert tela.combo_conta_do_endireitar.isEnabled()
    assert tela.combo_conta_do_endireitar.currentData() == es.JEITO_SCANTAILOR
    tela.combo_conta_do_endireitar.setCurrentIndex(
        tela.combo_conta_do_endireitar.findData(es.JEITO_PROGRAMA))
    assert projeto.paginas[0].endireitar_como == es.JEITO_PROGRAMA
    assert projeto.paginas[0].revisada
    assert all(p.endireitar_como is None for p in projeto.paginas[1:])
    tela.desfazer()
    assert projeto.paginas[0].endireitar_como is None
    assert tela.combo_conta_do_endireitar.currentData() == es.JEITO_SCANTAILOR
    # escolher de novo a conta do livro nao grava nada (segue o livro)
    tela.combo_conta_do_endireitar.setCurrentIndex(
        tela.combo_conta_do_endireitar.findData(es.JEITO_SCANTAILOR))
    assert projeto.paginas[0].endireitar_como is None


def test_com_o_angulo_a_mao_a_lista_fica_apagada(janela, pasta):
    tela = _aba_endireitar(janela, pasta)
    tela._angulo_zero()
    assert janela.projeto.paginas[0].angulo_manual == 0.0
    assert not tela.combo_conta_do_endireitar.isEnabled()
    assert tela.rotulo_angulos_medidos.text() == ""
    tela._angulo_automatico()
    assert tela.combo_conta_do_endireitar.isEnabled()


def test_texto_dos_angulos():
    assert texto_dos_angulos_medidos(None) == "(medindo...)"
    assert texto_dos_angulos_medidos(
        {"programa": -1.46, "scantailor": -1.5, "jeito": "scantailor", "discordam": False}) \
        == "ScanTailor -1,5° · programa -1,5°"
    assert texto_dos_angulos_medidos(
        {"programa": 0.0, "scantailor": 0.8, "jeito": "scantailor", "discordam": True}) \
        == "ScanTailor +0,8° · programa +0,0°  (discordam)"
    # livro pela conta do programa, ScanTailor nao medido
    assert texto_dos_angulos_medidos(
        {"programa": 0.4, "scantailor": None, "jeito": "programa", "discordam": False}) \
        == "programa +0,4°"
