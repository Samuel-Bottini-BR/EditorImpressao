"""Teste de reversão da D-590 (defeito de 04/11/2026): a caixinha "1 Dividir folhas ao meio" que a
pessoa DESMARCOU no Automático continua desmarcada depois de usar a ferramenta Dividir, do Ctrl+Z e
do Ctrl+Y, do "Desligar as marcadas" e da caixinha "Margens iguais" do Cortar.

O DEFEITO: Samuel, 04/11, print a-67 (Gradus, 140 páginas, "1 Dividir" marcado, "ligada no livro
todo"): "depois de usar o dividir e voltar ao automatico ele está marcado de novo." D-590, 03/11: "Sim
a caixinha continua desmacada." Reproduzido pelo agente caixinha-volta (relatorios/caixinha-volta/):
com o Dividir desmarcado E "Rodar", nada voltava a marcar (conserto de 03/11,
tests/test_dividir_desmarcada_caixinha.py); com o Dividir desmarcado e AINDA SEM "Rodar" (o livro
continua com o Dividir ligado), voltava marcado:
  - qualquer Ctrl+Z ou Ctrl+Y (do "não dividir esta", "dividir esta", "juntar todas", "dividir
    todas", da linha arrastada, do motor de corte...);
  - o "Desligar as marcadas" (ele não mexe nas desmarcadas, D-068);
  - a caixinha "Margens iguais" do Cortar (D-554).

A CAUSA: esses caminhos releem o livro para o painel (ui/automatico.EstadoDoAutomatico.do_projeto,
chamado por ui/tela_conferir._reacertar_as_opcoes, ui/tela_conferir._mudar_margens_iguais e
ui/janela_principal._aplicar_o_automatico), e a releitura marca as etapas ligadas no livro
(core/automatico.etapas_ligadas): o Dividir ainda ligado (Projeto.dividir_folhas) voltava marcado.

O CONSERTO: nesses caminhos, a caixinha do Dividir desmarcada pela pessoa continua desmarcada
(do_projeto(manter_o_dividir_desmarcado=True)); no desfazer/refazer, só quando a ação não muda o
Dividir do livro ("livro.dividir_folhas"). Nada muda nas folhas: as ações da ferramenta fazem o mesmo.

Livro sintético de 4 folhas com o livro aberto (duas páginas lado a lado), dividido pelo Automático,
como tests/test_dividir_desmarcada_caixinha.py.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixture app)
    _livro_aberto,
    _rodar,
    app,
    precisa_da_dll,
)


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 760)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _assentar(app, vezes: int = 40) -> None:
    for _ in range(vezes):
        app.processEvents()


def _marcada_no_painel(janela) -> bool:
    from PySide6.QtCore import Qt

    lista = janela.tela_conferir.paineis.automatico.lista
    return lista.item_da_etapa(A.DIVIDIR).checkState() == Qt.Checked


def _marcada_na_janela_grande(janela, app) -> bool:
    from PySide6.QtCore import Qt

    jan = janela.abrir_o_automatico()
    _assentar(app)
    marcada = jan.lista.item_da_etapa(A.DIVIDIR).checkState() == Qt.Checked
    frase = jan.frase.text().lower()
    janela._fechar_a_janela_do_automatico()
    _assentar(app)
    assert ("dividir" in frase) == marcada, frase
    return marcada


def _desmarcada(janela, app, onde: str) -> None:
    """A caixinha do Dividir continua desmarcada: no estado, no painel e na janela grande."""
    assert A.DIVIDIR not in janela.estado_do_automatico.marcadas, onde
    assert not _marcada_no_painel(janela), onde
    assert not _marcada_na_janela_grande(janela, app), onde


def _dividido_e_desmarcado_sem_rodar(janela, app, tmp_path):
    """Livro dividido pelo Automático ("ligada no livro todo"); a pessoa DESMARCA o Dividir no
    painel (clicando na caixinha) e ainda não clica "Rodar"."""
    from PySide6.QtCore import Qt

    janela.show()
    janela.abrir_livro(_livro_aberto(tmp_path, folhas=4))
    _assentar(app)
    assert _rodar(janela, [A.DIVIDIR, A.LIMPAR])
    assert janela.projeto.dividir_folhas and len(janela.projeto.paginas) == 8
    assert _marcada_no_painel(janela)
    lista = janela.tela_conferir.paineis.automatico.lista
    lista.item_da_etapa(A.DIVIDIR).setCheckState(Qt.Unchecked)
    _assentar(app)
    _desmarcada(janela, app, "desmarcou no painel")
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    _assentar(app)
    return tela


def _nao_dividir_esta(tela, app):
    tela._ir_para(1)
    _assentar(app)
    tela._alternar_dividir()


def _dividir_esta(tela, app):
    tela._ir_para(1)
    _assentar(app)
    tela._alternar_dividir()          # junta
    _assentar(app)
    tela._alternar_dividir()          # e divide de novo ("dividir esta")


def _juntar_todas(tela, app):
    tela._juntar_todas()


def _dividir_todas(tela, app):
    tela._juntar_todas()
    _assentar(app)
    tela._dividir_todas()
    tarefa = getattr(tela, "_tarefa_de_dividir_todas", None)
    if tarefa is not None:
        tarefa.wait(60000)
    _assentar(app, 100)


def _arrastar_a_linha(tela, app):
    tela._ir_para(1)
    _assentar(app)
    tela._mover_corte(0.45)


def _trocar_o_motor(tela, app):
    tela._ir_para(1)
    _assentar(app)
    combo = tela.combo_jeito_da_folha
    combo.setCurrentIndex((combo.currentIndex() + 1) % combo.count())


CAMINHOS = {
    "nao_dividir_esta": _nao_dividir_esta,
    "dividir_esta": _dividir_esta,
    "juntar_todas": _juntar_todas,
    "dividir_todas": _dividir_todas,
    "arrastar_a_linha": _arrastar_a_linha,
    "motor_de_corte": _trocar_o_motor,
}


@precisa_da_dll
@pytest.mark.parametrize("caminho", list(CAMINHOS))
def test_d590_dividir_desmarcado_sem_rodar_a_ferramenta_e_o_ctrl_z_y_nao_o_marcam(
        janela, app, tmp_path, caminho):
    """D-590 (04/11, print a-67): Dividir desmarcado no painel, sem "Rodar" → um caminho da
    ferramenta Dividir, Ctrl+Z e Ctrl+Y → a caixinha continua desmarcada nos três momentos (no
    painel, na janela grande e na frase), e o Dividir do livro não muda (só o "Rodar" o muda).
    No código de 50b242c7 falha no Ctrl+Z: a caixinha voltava marcada."""
    tela = _dividido_e_desmarcado_sem_rodar(janela, app, tmp_path)
    feitas = len(janela.acoes.feitas)
    CAMINHOS[caminho](tela, app)
    _assentar(app)
    assert len(janela.acoes.feitas) > feitas, "o caminho não fez nada"
    _desmarcada(janela, app, caminho)
    tela.desfazer()
    _assentar(app)
    _desmarcada(janela, app, caminho + " + Ctrl+Z")
    tela.refazer()
    _assentar(app)
    _desmarcada(janela, app, caminho + " + Ctrl+Y")
    assert janela.projeto.dividir_folhas               # nada roda antes do "Rodar"
    # e o "Rodar" de depois desliga o Dividir no livro, sem juntar as folhas (D-590)
    divididas = [f.dividir for f in janela.projeto.folhas]
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar(app)
    assert not janela.projeto.dividir_folhas
    assert [f.dividir for f in janela.projeto.folhas] == divididas
    _desmarcada(janela, app, caminho + " + Rodar")


@precisa_da_dll
def test_d590_dividir_desmarcado_e_desligar_as_marcadas_nao_o_marca(janela, app, tmp_path):
    """Dividir desmarcado, Limpar marcado, "Desligar as marcadas": o Limpar desliga, o Dividir
    fica como está no livro (D-068: só as marcadas) e a caixinha dele continua desmarcada.
    No código de 50b242c7 falha: a caixinha voltava marcada."""
    _dividido_e_desmarcado_sem_rodar(janela, app, tmp_path)
    assert janela.rodar_o_automatico(desligar=True, esperar=True, perguntar=False)
    _assentar(app)
    assert not janela.projeto.limpar and janela.projeto.dividir_folhas
    _desmarcada(janela, app, "desligar as marcadas")


@precisa_da_dll
def test_d590_dividir_desmarcado_e_margens_iguais_do_cortar_nao_o_marcam(janela, app, tmp_path):
    """Dividir desmarcado, e a caixinha "Margens iguais" do Cortar (D-554) ligada: as margens
    ligam no livro, e a caixinha do Dividir continua desmarcada.
    No código de 50b242c7 falha: a caixinha voltava marcada."""
    tela = _dividido_e_desmarcado_sem_rodar(janela, app, tmp_path)
    tela._mudar_margens_iguais(True)
    _assentar(app)
    assert janela.projeto.margens_iguais
    _desmarcada(janela, app, "margens iguais")


@precisa_da_dll
def test_d590_o_que_ja_era_continua(janela, app, tmp_path):
    """O que já era continua (D-605): a caixinha MARCADA segue marcada depois do Ctrl+Z/Ctrl+Y de
    uma ação da ferramenta; o Ctrl+Z do "Rodar" que desligou o Dividir traz o Dividir ligado no
    livro E a caixinha marcada (o painel acompanha o desfazer do "Rodar", como antes)."""
    from PySide6.QtCore import Qt

    janela.show()
    janela.abrir_livro(_livro_aberto(tmp_path, folhas=4))
    _assentar(app)
    assert _rodar(janela, [A.DIVIDIR, A.LIMPAR])
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    _assentar(app)
    _nao_dividir_esta(tela, app)
    tela.desfazer()
    tela.refazer()
    _assentar(app)
    assert _marcada_no_painel(janela) and A.DIVIDIR in janela.estado_do_automatico.marcadas
    tela.desfazer()                                    # devolve a folha
    _assentar(app)
    # desmarcar e Rodar; o Ctrl+Z desse Rodar
    lista = janela.tela_conferir.paineis.automatico.lista
    lista.item_da_etapa(A.DIVIDIR).setCheckState(Qt.Unchecked)
    _assentar(app)
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar(app)
    assert not janela.projeto.dividir_folhas and not _marcada_no_painel(janela)
    tela.desfazer()
    _assentar(app)
    assert janela.projeto.dividir_folhas
    assert _marcada_no_painel(janela)
