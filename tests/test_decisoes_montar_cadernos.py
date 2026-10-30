"""Prova de comportamento da D-589 (30/10/2026): desmarcar "Montar cadernos" no Automático vale.

O DEFEITO (relato do Kaique, áudios de 30/10; prints k-01 e k-02 em
relatorios/testes-guiados/2026-10-29-automatico/):
  "ela não tá selecionada, nem ela e nem a opção de dividir [...] aí aplicou o filtro branco,
  letra preta. Aí só que ele forma os cadernos do mesmo jeito." · "depois de rodar a etapa, aí
  ele volta a marcar." · "tiro, é, a opção de montar os cadernos, aí depois ele coloca de novo
  sozinho."
Livro de decisões, D-589: "Desmarcar 'Montar cadernos' no Automático tem que valer: o livro sai
sem cadernos, e a etapa não volta marcada sozinha."

A CAUSA (achada em 30/10): o "Rodar" só ligava as etapas marcadas (core/automatico.aplicar); a
caixinha desmarcada deixava a etapa de fora da rodada, mas "Montar cadernos" continuava ligada no
livro todo (Projeto.montar_cadernos, de uma rodada anterior). O PDF saía em cadernos
(core/pipeline.processar lê esse campo) e, depois do "Rodar", o painel relia o livro
(EstadoDoAutomatico.do_projeto: as etapas ligadas voltam marcadas) e a caixinha voltava marcada.

O que se mede aqui não é aparência: o campo do livro, o PDF que o programa grava (o mesmo do
"Confirmar e processar") e a caixinha da lista depois do "Rodar". Páginas sintéticas de propósito
(a medida é o número e a forma das folhas do PDF), como tests/test_decisoes_automatico.py.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core.pipeline import processar  # noqa: E402

DPI = 100


def _livro(tmp_path: Path) -> str:
    """4 páginas em pé (papel amarelado com linhas de "texto")."""
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for _ in range(4):
        img = np.full((560, 400, 3), (170, 215, 235), np.uint8)
        for y in range(90, 460, 30):
            img[y:y + 8, 70:330] = 25
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = 400 / DPI * 72, 560 / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _folhas_do_pdf(janela, tmp_path: Path, nome: str) -> list[tuple[float, float]]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava: (largura, altura) de cada
    folha. Sem cadernos: uma folha em pé por página. Em cadernos: folhas deitadas, duas
    páginas lado a lado."""
    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    with fitz.open(processar(projeto)) as doc:
        return [(p.rect.width, p.rect.height) for p in doc]


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos
    from ui.janela_principal import JanelaPrincipal

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _assentar(app, vezes: int = 10) -> None:
    for _ in range(vezes):
        app.processEvents()


def _caixinha(lista, etapa: str):
    from PySide6.QtCore import Qt

    return lista.item_da_etapa(etapa).checkState() == Qt.Checked


def test_d589_desmarcar_montar_cadernos_e_rodar_sai_sem_cadernos_e_nao_volta_marcada(janela, app, tmp_path):
    """D-589: livro com "Montar cadernos" ligada no livro todo → na janela grande do
    Automático, desmarcar "Montar cadernos" e rodar o resto (como o Kaique, print k-01) → o
    PDF sai sem cadernos, a etapa fica "desligada" e a caixinha não volta marcada sozinha
    (nem no painel, nem ao abrir a janela de novo). O Desfazer traz os cadernos de volta."""
    from PySide6.QtCore import Qt

    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    estado = janela.estado_do_automatico

    # 1) uma rodada anterior ligou "Montar cadernos" no livro todo (e o Limpar)
    estado.marcadas = {A.LIMPAR, A.CADERNOS}
    assert janela.rodar_o_automatico(esperar=True)
    projeto = janela.projeto
    assert projeto.montar_cadernos
    assert estado.situacoes[A.CADERNOS] == "ligada no livro todo"
    assert A.CADERNOS in estado.marcadas
    com_cadernos = _folhas_do_pdf(janela, tmp_path, "com-cadernos")
    assert all(largura > altura for largura, altura in com_cadernos)    # folhas deitadas

    # 2) o Kaique abre a janela grande, tira "Montar cadernos" e roda o resto
    jan = janela.abrir_o_automatico()
    _assentar(app)
    assert _caixinha(jan.lista, A.CADERNOS)              # vem marcada: está ligada no livro
    jan.lista.item_da_etapa(A.CADERNOS).setCheckState(Qt.Unchecked)
    _assentar(app)
    assert A.CADERNOS not in estado.marcadas
    jan.botao_rodar.click()
    if janela.tarefa is not None:
        janela.tarefa.wait(60000)
    _assentar(app, 30)

    # o livro sai sem cadernos: uma folha em pé por página
    assert not janela.projeto.montar_cadernos
    sem_cadernos = _folhas_do_pdf(janela, tmp_path, "sem-cadernos")
    assert len(sem_cadernos) == 4
    assert all(largura < altura for largura, altura in sem_cadernos)
    # o que estava marcado continua ligado (só a desmarcada saiu)
    assert janela.projeto.limpar
    # e a etapa não volta marcada sozinha: nem no painel, nem na janela aberta de novo
    painel = janela.tela_conferir.paineis.automatico
    assert estado.situacoes[A.CADERNOS] == "desligada"
    assert A.CADERNOS not in estado.marcadas
    assert not _caixinha(painel.lista, A.CADERNOS)
    jan = janela.abrir_o_automatico()
    _assentar(app)
    assert not _caixinha(jan.lista, A.CADERNOS)
    janela._fechar_a_janela_do_automatico()

    # o Desfazer traz de volta (está na mesma ação do Automático)
    janela.tela_conferir.desfazer()
    assert janela.projeto.montar_cadernos


def test_d589_so_a_janela_desliga_quem_monta_o_pedido_sem_ela_nao_mexe(tmp_path):
    """O desligar da D-589 vale para a caixinha DESMARCADA na janela (Pedido.desmarcadas), não
    para qualquer pedido sem "Montar cadernos": um pedido montado por outro caminho (testes,
    linha de comando) com só "Limpar" deixa os cadernos como estão. E "Desligar as marcadas"
    continua como era (D-068)."""
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=_livro(tmp_path))
    projeto.montar_cadernos = True
    A.aplicar(projeto, A.Pedido(etapas=[A.LIMPAR]))
    assert projeto.montar_cadernos
    # "Desligar as marcadas" com só o Limpar marcado: os cadernos ficam
    A.aplicar(projeto, A.Pedido(etapas=[A.LIMPAR], desligar=True, desmarcadas=[A.CADERNOS]))
    assert projeto.montar_cadernos and not projeto.limpar
    # "Rodar" com a caixinha dos cadernos desmarcada na janela: desliga
    A.aplicar(projeto, A.Pedido(etapas=[A.LIMPAR], desmarcadas=[A.CADERNOS]))
    assert not projeto.montar_cadernos and projeto.limpar
