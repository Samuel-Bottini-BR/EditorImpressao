"""Teste de reversão e prova da D-590 (03/11/2026): "Dividir" desmarcada e "Rodar" no Automático →
as folhas continuam divididas E a caixinha fica desmarcada.

O DEFEITO (achado pelo testador clicando em 02/11; prints
`.claude/worktrees/teste-cadernos/relatorios/teste-cadernos/36-d590-depois-de-rodar.png` e
`36b-d590-janela-reaberta.png`; relato "P1" no LEIA-ME.md da mesma pasta): num livro com folhas
divididas, na janela grande do Automático, desmarcar "1 Dividir folhas ao meio" e Rodar → as folhas
continuavam divididas (certo, D-590), mas a caixinha voltava MARCADA sozinha ("ligada no livro todo"
no painel e na janela reaberta) e a frase de baixo dizia "Vou dividir as folhas…". Kaique já tinha
contado o mesmo nos cadernos: "ele coloca de novo sozinho" (D-589).

Samuel, 03/11, à sugestão "a caixinha fica desmarcada como você deixou, e as folhas continuam
divididas. Pode ser?": "Sim a caixinha continua desmacada." (D-590, que também diz: "desmarcar
'Dividir' no Automático não junta nada").

A CAUSA: o "Rodar" deixava o Dividir fora do desligar das desmarcadas
(core/automatico._desligar_as_desmarcadas, DESLIGAM_DESMARCADAS só com Gravuras, Margens e
Cadernos): `Projeto.dividir_folhas` (o "ligado no livro todo" do Dividir) continuava True, e o
painel, relendo o livro (ui/automatico.EstadoDoAutomatico.do_projeto → core/automatico.
etapas_ligadas), voltava a marcar a caixinha. Junto com o conserto: com o Dividir desligado no livro,
o caminho rápido "só cadernos" (modelos.Projeto.so_cadernos, que monta os cadernos com as folhas
cruas do PDF) não pode valer num livro com folha dividida, senão os cadernos juntariam as folhas
(D-590: "não junta nada").

O que se mede: o projeto (o que vai para o projeto.json), a caixinha da lista no painel e na janela
grande aberta de novo, a frase de baixo, o trabalho fechado e reaberto e o PDF que o programa grava
(core.pipeline.processar, o mesmo do "Confirmar e processar"). Livro sintético de 3 folhas com o
livro aberto (duas páginas lado a lado), como tests/test_decisoes_juntar_todas.py.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core.pipeline import processar  # noqa: E402
from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixture app)
    _gerar,
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


def _nova_janela():
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    return janela


def _fechar(janela) -> None:
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


@pytest.fixture
def janela(app, pasta):
    janela = _nova_janela()
    yield janela
    _fechar(janela)


def _assentar(app, vezes: int = 30) -> None:
    for _ in range(vezes):
        app.processEvents()


def _marcada(lista, etapa: str) -> bool:
    from PySide6.QtCore import Qt

    return lista.item_da_etapa(etapa).checkState() == Qt.Checked


def _pela_janela(janela, app, marcar: bool) -> None:
    """Como o testador de 02/11: abre a janela grande, marca ou desmarca "1 Dividir folhas ao meio"
    e clica "Rodar"."""
    from PySide6.QtCore import Qt

    jan = janela.abrir_o_automatico()
    _assentar(app)
    jan.lista.item_da_etapa(A.DIVIDIR).setCheckState(Qt.Checked if marcar else Qt.Unchecked)
    _assentar(app)
    jan.botao_rodar.click()
    if janela.tarefa is not None:
        janela.tarefa.wait(60000)
    _assentar(app)


def _paginas_do_pdf(janela, tmp_path: Path, nome: str) -> list[tuple[float, float]]:
    """(largura, altura) de cada folha do PDF do livro aberto."""
    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    with fitz.open(processar(projeto)) as doc:
        return [(round(p.rect.width), round(p.rect.height)) for p in doc]


@precisa_da_dll
def test_d590_dividir_desmarcada_e_rodar_a_caixinha_fica_desmarcada_e_as_folhas_divididas(
        app, pasta, tmp_path):
    """D-590 (03/11: "Sim a caixinha continua desmacada."): livro dividido pelo Automático (3 folhas
    → 6 páginas) → na janela grande, desmarcar "Dividir" e Rodar → as folhas continuam divididas (6
    páginas no PDF), a etapa fica "desligada", a caixinha fica desmarcada no painel e na janela grande
    aberta de novo, a frase de baixo não diz "Vou dividir" — e continua assim depois de fechar e
    reabrir o trabalho. Marcar de novo e rodar → divide ("ligada no livro todo").
    No código de 8846017 falha: a caixinha voltava marcada ("ligada no livro todo")."""
    caminho = _livro_aberto(tmp_path)
    janela = _nova_janela()
    try:
        janela.show()
        janela.abrir_livro(caminho)
        _assentar(app)
        assert _rodar(janela, [A.DIVIDIR, A.LIMPAR])
        estado = janela.estado_do_automatico
        assert len(janela.projeto.paginas) == 6
        assert estado.situacoes[A.DIVIDIR] == "ligada no livro todo"

        _pela_janela(janela, app, marcar=False)

        projeto = janela.projeto
        # as folhas continuam divididas (D-590: "não junta nada")
        assert len(projeto.paginas) == 6 and all(f.dividir for f in projeto.folhas)
        assert len(_gerar(janela, tmp_path, "continua")) == 6
        # o que estava marcado continua (só a desmarcada saiu)
        assert projeto.limpar
        # e a caixinha fica desmarcada: no painel, na frase e na janela aberta de novo
        assert estado.situacoes[A.DIVIDIR] == "desligada"
        assert A.DIVIDIR not in estado.marcadas
        assert not _marcada(janela.tela_conferir.paineis.automatico.lista, A.DIVIDIR)
        assert "dividir" not in estado.frase().lower()
        jan = janela.abrir_o_automatico()
        _assentar(app)
        assert not _marcada(jan.lista, A.DIVIDIR)
        assert "dividir" not in jan.frase.text().lower()
        janela._fechar_a_janela_do_automatico()
        janela._salvar_agora()
    finally:
        _fechar(janela)

    # fechar e reabrir o trabalho: igual
    janela = _nova_janela()
    try:
        janela.show()
        janela.abrir_livro(caminho)
        _assentar(app)
        estado = janela.estado_do_automatico
        assert len(janela.projeto.paginas) == 6 and all(f.dividir for f in janela.projeto.folhas)
        assert estado.situacoes[A.DIVIDIR] == "desligada"
        assert A.DIVIDIR not in estado.marcadas
        jan = janela.abrir_o_automatico()
        _assentar(app)
        assert not _marcada(jan.lista, A.DIVIDIR)
        janela._fechar_a_janela_do_automatico()

        # marcar de novo e rodar: divide, e a etapa volta "ligada no livro todo"
        _pela_janela(janela, app, marcar=True)
        assert estado.situacoes[A.DIVIDIR] == "ligada no livro todo"
        assert A.DIVIDIR in estado.marcadas
        assert _marcada(janela.tela_conferir.paineis.automatico.lista, A.DIVIDIR)
        assert len(janela.projeto.paginas) == 6
        assert len(_gerar(janela, tmp_path, "de-novo")) == 6
    finally:
        _fechar(janela)


@precisa_da_dll
def test_d590_dividir_desmarcada_o_desfazer_volta_a_ligar(janela, app, tmp_path):
    """O desligar do Dividir desmarcado vai na mesma ação do Automático: o Ctrl+Z traz o Dividir
    "ligado no livro todo" de volta, e as folhas nunca deixam de estar divididas."""
    janela.show()
    janela.abrir_livro(_livro_aberto(tmp_path))
    _assentar(app)
    assert _rodar(janela, [A.DIVIDIR])
    _pela_janela(janela, app, marcar=False)
    assert not janela.projeto.dividir_folhas
    janela.tela_conferir.desfazer()
    assert janela.projeto.dividir_folhas
    assert len(janela.projeto.paginas) == 6 and all(f.dividir for f in janela.projeto.folhas)


@precisa_da_dll
def test_d590_dividir_desmarcada_e_so_cadernos_os_cadernos_continuam_com_as_folhas_divididas(
        janela, app, tmp_path):
    """D-590 ("não junta nada") com o caminho rápido "só cadernos" (modelos.Projeto.so_cadernos):
    livro dividido pelo Automático só com o Dividir → rodar só "Montar cadernos", com o Dividir
    desmarcado → os cadernos saem com as 6 páginas divididas, iguais aos cadernos com o Dividir
    ainda ligado (o caminho rápido monta com as folhas cruas do PDF e juntaria as folhas)."""
    janela.show()
    janela.abrir_livro(_livro_aberto(tmp_path))
    _assentar(app)
    assert _rodar(janela, [A.DIVIDIR, A.CADERNOS])
    assert janela.projeto.dividir_folhas and janela.projeto.montar_cadernos
    com_dividir = _paginas_do_pdf(janela, tmp_path, "com-dividir")

    estado = janela.estado_do_automatico
    estado.marcadas = {A.CADERNOS}
    assert A.DIVIDIR in estado.pedido().desmarcadas
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    projeto = janela.projeto
    assert not projeto.dividir_folhas and projeto.montar_cadernos
    assert len(projeto.paginas) == 6 and all(f.dividir for f in projeto.folhas)
    assert not projeto.so_cadernos
    assert _paginas_do_pdf(janela, tmp_path, "sem-dividir") == com_dividir
