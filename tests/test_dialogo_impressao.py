"""Item 2.6 na tela (controle mínimo): a janela "Montar para imprimir".

- abre da tela "Ficou pronto!" pelo botão "montar para imprimir..." (que fica
  apagado quando o PDF já saiu em cadernos do jeito antigo);
- os controles começam nas opções de fábrica (as decisões do Samuel) e vão e
  voltam sem perder nada;
- gravar o arquivo roda num fio à parte, guarda as escolhas no
  configuracoes.json e mostra os avisos.
Nenhuma janela aparece na tela (tests/conftest.py); pasta de dados própria.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import impressao as imp  # noqa: E402
from tests.test_impressao import _livro  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import app, pasta  # noqa: F401, E402 - fixtures


def _dialogo(caminho):
    from ui.dialogo_impressao import DialogoImpressao

    return DialogoImpressao(str(caminho))


def test_comeca_nas_opcoes_de_fabrica(app, pasta):
    dialogo = _dialogo(_livro(pasta / "l.pdf", 4))
    assert dialogo.opcoes() == imp.OpcoesDeImpressao()
    assert dialogo.cx_imagem.isChecked()            # imp-6
    assert dialogo.cx_margens.isChecked()           # g11
    assert not dialogo.grupo_livreto.isHidden()
    assert dialogo.grupo_poster.isHidden()


def test_opcoes_vao_e_voltam_dos_controles(app, pasta):
    dialogo = _dialogo(_livro(pasta / "l.pdf", 4))
    opcoes = imp.OpcoesDeImpressao(formato=imp.MULTIPLO, papel="Carta", escala=imp.PERSONALIZADA,
                                   escala_percentual=83, escala_direita=90, excecoes={3: 80.0},
                                   paginas_por_caderno=16, lados=imp.SO_VERSO, reverter=True,
                                   cinza=True, como_imagem=False, multiplo_por_folha=9)
    dialogo.definir_opcoes(opcoes)
    assert dialogo.opcoes() == opcoes
    assert not dialogo.grupo_multiplo.isHidden() and dialogo.grupo_livreto.isHidden()


def test_ler_as_excecoes():
    from ui.dialogo_impressao import escrever_excecoes, ler_excecoes

    assert ler_excecoes("12=90; 15 = 85%, x=3; 0=50; 7") == {12: 90.0, 15: 85.0}
    assert escrever_excecoes({15: 85.0, 12: 90.0}) == "12=90; 15=85"


def test_gravar_monta_o_arquivo_e_guarda_as_escolhas(app, pasta):
    import configuracoes

    entrada = _livro(pasta / "l.pdf", 8)
    dialogo = _dialogo(entrada)
    dialogo.escala_direita.setValue(130)            # passa da margem: tem de avisar
    dialogo.cx_imagem.setChecked(False)
    destino = pasta / "s.pdf"
    dialogo.comecar(destino=str(destino))
    assert dialogo.tarefa.wait(60000)
    app.processEvents()
    assert destino.exists()
    assert dialogo.ultimo_resultado is not None
    assert dialogo.ultimo_resultado.avisos
    assert not dialogo.avisos.isHidden()
    assert "Pronto" in dialogo.estado.text()
    assert configuracoes.ler("impressao")["escala_direita"] == 130.0


def test_botao_da_tela_final(app, pasta):
    from modelos import Projeto
    from ui.tela_final import TelaFinal

    entrada = _livro(pasta / "l.pdf", 4)
    tela = TelaFinal()
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(entrada))
    tela.mostrar(projeto, str(entrada), 4)
    assert tela.botao_montar.isEnabled()
    tela.abrir_montar_para_imprimir()
    assert tela.dialogo_impressao.entrada == str(entrada)
    tela.dialogo_impressao.reject()
    projeto.montar_cadernos = True
    tela.mostrar(projeto, str(entrada), 4)
    assert not tela.botao_montar.isEnabled()
