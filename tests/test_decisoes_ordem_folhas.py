"""Prova de comportamento da D-615 (04/11/2026): mudar folhas de lugar arrastando a miniatura.

Samuel (prints a-61 e a-62): "eu quero poder mover folhas para onde eu quiser dentro do app, quero
poder arrastar e mover folhas, caso eu precise resolver esse problema na mão" → proposta da gerente
(arrastar uma miniatura da tira de baixo e soltar onde quiser) → "ok".
Livro de decisões: "Mudar folhas de lugar à mão: arrastar uma miniatura da tira de baixo e soltar
onde quiser; a folha (ou a página, se já dividida) muda de lugar no livro, e o Ctrl+Z desfaz. A
nova ordem vale para a tela, o PDF e os cadernos."

O que se mede: a lista de páginas do projeto (o que vai para o projeto.json), a tira (os quadros e
o número de cada um), o Histórico (Ctrl+Z, Ctrl+Y), o PDF que o programa grava (core.pipeline.
processar, o do "Confirmar e processar"), a lista do caderno (core/automatico.paginas_do_pdf_depois,
D-603) e o livro reaberto. O arrastar é feito com o mouse de mentira do Qt (QTest: apertar, andar,
soltar) em cima das miniaturas, como a pessoa faz.

O ANTIGO NÃO TINHA: no código de antes (d66a588b) a miniatura não se arrasta (só o clique), e a
ação do desfazer não sabe mudar a ordem: os testes de arrastar e de desfazer falham lá.

Livro sintético: cada folha tem uma faixa preta numa altura diferente (a folha N na altura N), para
saber, no PDF, qual folha saiu em cada lugar.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, Qt  # noqa: E402

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _paginas_do_pdf,
    _pdf,
    app,
    janela,
    pasta,
)

ALTURAS = (60, 200, 340, 480, 620, 760)          # a faixa de cada folha (pontos, de 840)


def _folha(n: int) -> np.ndarray:
    """Uma página em pé com a faixa preta na altura da folha `n`."""
    img = np.full((840, 600, 3), 235, np.uint8)
    y = ALTURAS[n]
    img[y:y + 30, 60:540] = 0
    return img


def _aberta(n: int) -> np.ndarray:
    """Um livro aberto (duas páginas): a da esquerda com a faixa da folha `n`, a da direita
    com a faixa da folha `n` mais embaixo (para saber qual metade é qual)."""
    esquerda, direita = _folha(n), _folha(n)
    direita[ALTURAS[n] + 40:ALTURAS[n] + 60, 60:540] = 0
    return np.concatenate([esquerda, direita], axis=1)


def _livro(tmp_path: Path, folhas: int = 5) -> str:
    return _pdf(tmp_path / "livro.pdf", [_folha(n) for n in range(folhas)])


def _qual(img: np.ndarray) -> int:
    """Qual folha é esta página do PDF (a altura da faixa preta)."""
    cinza = img.mean(axis=2) if img.ndim == 3 else img
    linhas = np.where((cinza < 80).mean(axis=1) > 0.5)[0]
    assert linhas.size, "página sem a faixa"
    y = linhas[0] * 840 / cinza.shape[0]
    return int(np.argmin([abs(y - a) for a in ALTURAS]))


def _assentar(vezes: int = 4) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    import copy

    from core.pipeline import processar

    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


def _arrastar(tela, de: int, para_antes_de: int | None) -> None:
    """Arrasta, com o mouse, a miniatura `de` e solta no vão antes da miniatura
    `para_antes_de` (None = depois da última): aperta no meio dela, anda e solta um
    pouquinho à esquerda do meio do quadro de destino (ou à direita do último)."""
    from PySide6.QtTest import QTest

    tira = tela.tira
    tela.show()
    tela.window().show()
    _assentar()
    origem = tira._miniaturas[de]
    tira.rolagem.ensureWidgetVisible(origem)
    _assentar()
    QTest.mousePress(origem, Qt.LeftButton, Qt.NoModifier, origem.rect().center())
    _assentar()
    origem = tira._miniaturas[de]
    if para_antes_de is None:
        alvo = tira._miniaturas[-1]
        ponto = alvo.rect().center() + QPoint(alvo.width() // 3, 0)
    else:
        alvo = tira._miniaturas[para_antes_de]
        ponto = alvo.rect().center() - QPoint(alvo.width() // 3, 0)
    destino = origem.mapFromGlobal(alvo.mapToGlobal(ponto))
    # anda em passos (o primeiro passa da distância de arrastar)
    inicio = origem.rect().center()
    for t in (0.25, 0.5, 0.75, 1.0):
        meio = inicio + (destino - inicio) * t
        QTest.mouseMove(origem, meio)
        _assentar(1)
    assert tira.arrastando(), "a miniatura não começou a ser arrastada"
    assert tira.sinal_do_vao.isVisible(), "a linha azul de onde ela vai cair não apareceu"
    QTest.mouseRelease(origem, Qt.LeftButton, Qt.NoModifier, destino)
    _assentar()


def _folhas(projeto) -> list[int]:
    return [p.folha for p in projeto.paginas]


# --- o arrastar na tira -------------------------------------------------------------------------

def test_d615_arrastar_a_miniatura_muda_a_folha_de_lugar_e_o_ctrl_z_desfaz(janela, tmp_path):
    """D-615: arrastar a miniatura da folha 2 para depois da 4 (o exemplo do Livro: "arrastar a
    miniatura 2 para depois da 5") muda a ordem do livro, a tira e a página da vez; o Ctrl+Z volta,
    o Ctrl+Y refaz. Os quadros da tira só trocam de lugar (os MESMOS quadros, com a imagem já
    lida): num livro grande nada é lido do PDF de novo."""
    janela.abrir_livro(_livro(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    assert _folhas(projeto) == [0, 1, 2, 3, 4]
    quadros = list(tela.tira._miniaturas)
    feitas = len(janela.acoes.feitas)

    _arrastar(tela, 1, 4)                        # a 2ª miniatura para antes da 5ª

    assert _folhas(projeto) == [0, 2, 3, 1, 4]
    assert [p.indice for p in projeto.paginas] == [0, 1, 2, 3, 4]
    assert len(janela.acoes.feitas) == feitas + 1
    assert tela.indice_pagina == 3 and tela.indice_folha == 1      # a tela foi junto com a folha
    tira = tela.tira
    assert [m.numero for m in tira._miniaturas] == [1, 2, 3, 4, 5]
    assert tira._miniaturas == [quadros[i] for i in (0, 2, 3, 1, 4)], "a tira foi lida de novo"
    assert not tira.sinal_do_vao.isVisible() and not tira.arrastando()

    tela.desfazer()                              # Ctrl+Z
    assert _folhas(projeto) == [0, 1, 2, 3, 4]
    assert tira._miniaturas == quadros
    tela.refazer()                               # Ctrl+Y
    assert _folhas(projeto) == [0, 2, 3, 1, 4]


def test_d615_soltar_para_o_fim_e_para_o_comeco(janela, tmp_path):
    """Soltar depois da última miniatura leva a folha para o fim; antes da primeira, para o
    começo."""
    janela.abrir_livro(_livro(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    _arrastar(tela, 0, None)
    assert _folhas(projeto) == [1, 2, 3, 4, 0]
    _arrastar(tela, 3, 0)
    assert _folhas(projeto) == [4, 1, 2, 3, 0]


def test_d615_clique_simples_continua_indo_para_a_pagina_e_nao_muda_nada(janela, tmp_path):
    """"Um clique simples na miniatura continua indo para a folha, como hoje": apertar e soltar
    sem andar vai para a página e não muda a ordem nem o Histórico; soltar no mesmo lugar
    também não."""
    from PySide6.QtTest import QTest

    janela.abrir_livro(_livro(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela.show()
    _assentar()
    feitas = len(janela.acoes.feitas)
    quadro = tela.tira._miniaturas[3]
    QTest.mouseClick(quadro, Qt.LeftButton, Qt.NoModifier, quadro.rect().center())
    _assentar()
    assert tela.indice_atual == 3
    assert _folhas(projeto) == [0, 1, 2, 3, 4] and len(janela.acoes.feitas) == feitas
    _arrastar(tela, 2, 3)                        # soltou logo depois dela mesma: o mesmo lugar
    assert _folhas(projeto) == [0, 1, 2, 3, 4] and len(janela.acoes.feitas) == feitas


def test_d615_a_nova_ordem_vale_no_pdf(janela, tmp_path):
    """A nova ordem vale no PDF de saída (o mesmo processar do "Confirmar e processar")."""
    janela.abrir_livro(_livro(tmp_path))
    tela = janela.tela_conferir
    _arrastar(tela, 4, 0)                        # a última folha vira a primeira
    paginas = _gerar(janela, tmp_path, "saida")
    assert [_qual(p) for p in paginas] == [4, 0, 1, 2, 3]


def test_d615_a_nova_ordem_vale_nos_cadernos(janela, tmp_path):
    """A nova ordem vale nos cadernos: o caminho rápido "só cadernos" (que monta com as folhas
    na ordem do PDF) não é usado com a ordem mudada, e o PDF com cadernos sai com as páginas na
    ordem nova; a lista da etapa 7 (D-603) também segue."""
    from core import automatico as A

    janela.abrir_livro(_livro(tmp_path, folhas=4))
    tela, projeto = janela.tela_conferir, janela.projeto
    projeto.montar_cadernos, projeto.paginas_por_caderno = True, 4
    projeto.limpar = projeto.endireitar = projeto.cortar_bordas = False
    assert projeto.so_cadernos                    # livro sem ordem mudada: o caminho de sempre
    _arrastar(tela, 3, 0)
    assert _folhas(projeto) == [3, 0, 1, 2]
    assert not projeto.so_cadernos
    lista = A.paginas_do_pdf_depois(projeto, A.Pedido(etapas=[A.DIVIDIR]))
    assert [folha for _o, folha, _m in lista] == [3, 0, 1, 2]
    # o caderno de 4 páginas: frente = [4 | 1] (posições no PDF). A 1ª posição do livro agora
    # é a folha 3, e a 4ª é a folha 2.
    paginas = _gerar(janela, tmp_path, "cadernos")
    assert len(paginas) == 2                      # frente e verso de uma folha de caderno
    frente = paginas[0]
    metade = frente.shape[1] // 2
    assert _qual(frente[:, metade:]) == 3, "a página 1 do caderno não é a folha que foi para a frente"
    assert _qual(frente[:, :metade]) == 2


def test_d615_fechar_e_abrir_mantem_a_ordem(janela, tmp_path):
    """Fechar e abrir o projeto mantém a nova ordem (e o Ctrl+Z dela)."""
    caminho = _livro(tmp_path)
    janela.abrir_livro(caminho)
    _arrastar(janela.tela_conferir, 1, None)
    assert _folhas(janela.projeto) == [0, 2, 3, 4, 1]
    janela._salvar_agora()
    janela.abrir_livro(caminho)
    assert _folhas(janela.projeto) == [0, 2, 3, 4, 1]
    assert [p.indice for p in janela.projeto.paginas] == [0, 1, 2, 3, 4]
    janela.tela_conferir.desfazer()
    assert _folhas(janela.projeto) == [0, 1, 2, 3, 4]


def test_d615_projeto_antigo_abre_como_hoje(janela, tmp_path):
    """Projeto sem ordem mudada (todos os de antes): a lista na ordem das folhas, o caminho
    rápido dos cadernos como sempre, e o Histórico sem ação nova."""
    from core import ordem_das_paginas as O

    caminho = _livro(tmp_path)
    janela.abrir_livro(caminho)
    janela._salvar_agora()
    janela.abrir_livro(caminho)
    assert _folhas(janela.projeto) == [0, 1, 2, 3, 4]
    assert not O.fora_da_ordem_do_pdf(janela.projeto)
    assert not janela.acoes.feitas


def test_d615_passar_da_beirada_vale_como_a_beirada_e_longe_da_tira_nao_muda(janela, tmp_path):
    """Achado na janela de verdade (04/11): soltar um pouco à esquerda do começo da tira (o
    mouse passa da beirada) vale como o vão antes da primeira; bem acima da tira (longe dela),
    soltar não muda nada."""
    janela.abrir_livro(_livro(tmp_path))
    tela = janela.tela_conferir
    tela.show()
    _assentar()
    tira = tela.tira
    vp = tira.rolagem.viewport()
    assert tira.vao_do_ponto(vp.mapToGlobal(QPoint(-50, vp.height() // 2))) == 0
    assert tira.vao_do_ponto(vp.mapToGlobal(QPoint(vp.width() // 2, -200))) is None


# --- folha dividida: a página anda sozinha ------------------------------------------------------

def _dividir_a_mao(tela, projeto, folha: int) -> None:
    """"dividir esta" na folha, com a linha no meio (core/dividir_a_mao, a mesma ação da
    ferramenta)."""
    from core import dividir_a_mao

    tela._registrar("dividir_a_mao", "folha", [folha],
                    dividir_a_mao.campos_para_dividir(projeto, folha, 0.5), "dividir")


def test_d615_pagina_de_folha_dividida_anda_sozinha_e_juntar_e_desfazer_voltam_certo(janela, tmp_path):
    """"Se já estiver dividida, muda a página": a página da direita da folha 1 dividida vai para
    o fim, sem a da esquerda. Depois, "não dividir esta" junta a folha no lugar da primeira
    página dela (as duas guardadas na ordem esquerda, direita), e o Ctrl+Z devolve cada página
    ao lugar em que estava (a da direita, no fim)."""
    from core import dividir_a_mao

    janela.abrir_livro(_pdf(tmp_path / "abertas.pdf", [_aberta(n) for n in range(3)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    _dividir_a_mao(tela, projeto, 0)
    lugares = [(p.folha, p.metade) for p in projeto.paginas]
    assert lugares == [(0, "esquerda"), (0, "direita"), (1, "inteira"), (2, "inteira")]
    tela._montar_tira()
    _arrastar(tela, 1, None)                     # a direita da folha 1 para o fim
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "esquerda"), (1, "inteira"), (2, "inteira"), (0, "direita")]

    campos = dividir_a_mao.campos_para_juntar(projeto, 0)
    assert [m["metade"] for m in campos["metades_guardadas"]] == ["esquerda", "direita"]
    tela._registrar("nao_dividir", "folha", [0], campos, "juntar")
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "inteira"), (1, "inteira"), (2, "inteira")]
    tela.desfazer()
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "esquerda"), (1, "inteira"), (2, "inteira"), (0, "direita")]
    tela.refazer()
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "inteira"), (1, "inteira"), (2, "inteira")]


def test_d615_folha_nao_dividida_anda_inteira_e_dividir_depois_fica_no_lugar(janela, tmp_path):
    """A folha não dividida anda inteira; dividida depois, as duas páginas ficam no lugar novo
    dela (esquerda, direita)."""
    janela.abrir_livro(_pdf(tmp_path / "abertas.pdf", [_aberta(n) for n in range(3)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    _arrastar(tela, 0, None)
    assert _folhas(projeto) == [1, 2, 0]
    _dividir_a_mao(tela, projeto, 0)
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (1, "inteira"), (2, "inteira"), (0, "esquerda"), (0, "direita")]
    paginas = _gerar(janela, tmp_path, "dividida")
    assert [_qual(p) for p in paginas] == [1, 2, 0, 0]


def test_d615_no_dividir_a_tira_tambem_arrasta_e_as_setas_seguem_a_ordem(janela, tmp_path):
    """Na ferramenta Dividir (tira de folhas e páginas, D-601) o arrastar também vale, e as
    setas em "Duas lado a lado" andam na ordem do livro (a da tira)."""
    from ui.tela_conferir import DUAS

    janela.abrir_livro(_livro(tmp_path, folhas=4))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela.escolher_ferramenta("dividir")
    assert tela.trabalha_com_folhas
    _arrastar(tela, 0, 3)                        # a folha 1 para antes da 4
    assert _folhas(projeto) == [1, 2, 0, 3]
    tela.definir_mostrar(DUAS)
    tela._ir_para(2)
    tela._navegar(+1)
    assert tela.indice_folha == 0, "a seta não seguiu a ordem do livro"
    tela._navegar(+1)
    assert tela.indice_folha == 3


# --- livro grande ------------------------------------------------------------------------------

def test_d615_livro_de_1010_paginas_muda_de_lugar_depressa(app, monkeypatch):
    """Livro grande (1010 páginas) não pode ficar lento: mudar uma folha de lugar (a conta, a
    ação, o desfazer) e trocar os quadros da tira de lugar levam frações de segundo."""
    from historico_acoes import aplicar, montar_acao
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.widgets.tira_miniaturas import TiraMiniaturas
    from core import ordem_das_paginas as O

    n = 1010
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(n)]
    inicio = time.perf_counter()
    campos = O.campos_para_mover(projeto, O.bloco(projeto, 5), 900)
    acao = montar_acao(projeto, "mudar_de_lugar", "pagina", [], campos, "x")
    aplicar(projeto, acao, acao.depois)
    aplicar(projeto, acao, acao.antes)
    aplicar(projeto, acao, acao.depois)
    conta = time.perf_counter() - inicio
    assert [p.folha for p in projeto.paginas][895:901] == [896, 897, 898, 899, 5, 900]
    assert conta < 0.5, f"a conta levou {conta:.2f} s"

    from ui.widgets import tira_miniaturas

    lidas = []
    monkeypatch.setattr(tira_miniaturas._TarefaMiniaturas, "run", lambda self: lidas.append(1))
    tira = TiraMiniaturas("x")
    tira.montar(n, "nao-existe.pdf", {i: i for i in range(n)})
    quadros = list(tira._miniaturas)
    inicio = time.perf_counter()
    tira.montar(n, "nao-existe.pdf", {i: p.folha for i, p in enumerate(projeto.paginas)})
    reordenar = time.perf_counter() - inicio
    assert tira._miniaturas[899] is quadros[5]
    tira._pool.waitForDone(2000)
    assert len(lidas) == 1, "a tira foi lida do PDF de novo"
    assert reordenar < 1.0, f"trocar os quadros de lugar levou {reordenar:.2f} s"
    tira.parar()
