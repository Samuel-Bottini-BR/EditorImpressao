"""Prova de comportamento da D-613 (04/11/2026): o "dividir todas" pergunta sobre as folhas
juntadas à mão.

Pergunta (Central `d602-juntada`, repetida no chat): "O "dividir todas" pula as folhas que você
juntou à mão? Sugiro que sim." → Samuel: "2- ele dá um aviso perguntando ."
Livro de decisões: "Quando há folhas juntadas à mão, o "dividir todas" dá um aviso perguntando se
divide também essas ou se pula. As outras folhas são divididas como hoje."

O aviso segue o jeito do aviso da D-004 (o das páginas mexidas à mão do Automático: "Pular as N"
/ "Rodar nelas também" / "cancelar"). Cada escolha é UMA ação do desfazer (ou nenhuma, no
cancelar). Sem folha juntada à mão, nada muda: sem aviso (D-605).

Pergunta ainda aberta (da gerente ao Samuel): as folhas juntadas pelo "juntar todas" (D-590)
contam como "juntadas à mão"? Até a resposta, NÃO contam (core/dividir_a_mao.JUNTAR_TODAS_CONTA
= False); os dois jeitos são provados aqui.

O que se mede: o projeto (folhas divididas ou não, quantas páginas), o Histórico (quantas ações)
e o aviso de verdade (título, texto, botões). No código de antes (dd7a648c) o "dividir todas"
dividia as juntadas sem perguntar: os testes "reversao" falham lá.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import app, janela, pasta  # noqa: E402,F401  (fixtures)
from tests.test_decisoes_dividir_linha import (  # noqa: E402
    _aberto_torto,
    _assentar,
    _esperar,
    _linha_lida,
    _no_dividir,
)


def _paginas_da(projeto, folha: int) -> int:
    return len([p for p in projeto.paginas if p.folha == folha])


def _juntar_a_mao(janela, tela, indice: int) -> None:
    """O que o Samuel faz: na folha, "dividir esta" e depois "não dividir esta"."""
    projeto = janela.projeto
    tela._ir_para(indice)
    _linha_lida(tela)
    if not projeto.folhas[indice].dividir:
        tela.botao_nao_dividir.click()                   # dividir esta
    assert projeto.folhas[indice].dividir
    tela.botao_nao_dividir.click()                       # não dividir esta
    assert not projeto.folhas[indice].dividir and projeto.folhas[indice].metades_guardadas


def _responder(monkeypatch, tela, resposta):
    """Troca o aviso por uma resposta pronta e guarda quantas folhas ele contou."""
    perguntas: list[int] = []

    def perguntar(quantas):
        perguntas.append(quantas)
        return resposta

    monkeypatch.setattr(tela, "_perguntar_as_juntadas", perguntar, raising=False)
    return perguntas


def _sem_aviso(monkeypatch, tela):
    def nao_pode(quantas):
        raise AssertionError("o aviso não podia aparecer")

    monkeypatch.setattr(tela, "_perguntar_as_juntadas", nao_pode, raising=False)


def _dividir_todas_e_esperar(janela, tela, condicao, motivo="dividir todas") -> None:
    tela.botao_dividir_todas.click()
    _esperar(condicao, motivo=motivo)
    _assentar(5)


# --- 1. pular: as juntadas ficam inteiras, as outras divididas, uma ação só ---------------------

def test_reversao_d613_pular_deixa_a_juntada_inteira(janela, tmp_path, monkeypatch):
    """D-613: folha 2 juntada à mão → "dividir todas" pergunta (1 folha); "Pular" → a folha 2
    fica inteira e as outras são divididas, numa ação só; Ctrl+Z volta tudo (a folha 2 continua
    juntada); Ctrl+Y faz de novo. No código de antes não perguntava e dividia a folha 2."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _juntar_a_mao(janela, tela, 1)
    perguntas = _responder(monkeypatch, tela, True)
    feitas = len(janela.acoes.feitas)

    _dividir_todas_e_esperar(janela, tela, lambda: projeto.folhas[0].dividir
                             and projeto.folhas[2].dividir)
    f = projeto.folhas
    assert perguntas == [1], "o aviso aparece e conta a folha juntada à mão"
    assert not f[1].dividir and _paginas_da(projeto, 1) == 1, "pular: a juntada fica inteira"
    assert f[1].metades_guardadas, "e continua guardando as duas páginas (D-498)"
    assert len(projeto.paginas) == 2 + 1 + 2
    assert len(janela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"

    tela.desfazer()                                       # Ctrl+Z
    _assentar(5)
    assert not any(x.dividir for x in f) and len(projeto.paginas) == 3
    assert f[1].metades_guardadas, "a folha juntada continua juntada"
    tela.refazer()                                        # Ctrl+Y
    _assentar(5)
    assert f[0].dividir and not f[1].dividir and f[2].dividir
    assert len(projeto.paginas) == 5


# --- 2. dividir também: todas divididas, como hoje ---------------------------------------------

def test_reversao_d613_dividir_tambem_divide_todas(janela, tmp_path, monkeypatch):
    """D-613: "Dividir também" → todas divididas (a juntada volta como estava, na linha de antes,
    D-498), numa ação só; Ctrl+Z volta tudo; Ctrl+Y de novo."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _juntar_a_mao(janela, tela, 1)
    linha_de_antes = projeto.folhas[1].posicao_corte
    perguntas = _responder(monkeypatch, tela, False)
    feitas = len(janela.acoes.feitas)

    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas))
    f = projeto.folhas
    assert perguntas == [1]
    assert len(projeto.paginas) == 6
    assert f[1].posicao_corte == pytest.approx(linha_de_antes), "na linha de antes"
    assert len(janela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"
    tela.desfazer()
    _assentar(5)
    assert not any(x.dividir for x in f) and f[1].metades_guardadas
    tela.refazer()
    _assentar(5)
    assert all(x.dividir for x in f) and len(projeto.paginas) == 6


# --- 3. cancelar: nada muda --------------------------------------------------------------------

def test_reversao_d613_cancelar_nao_muda_nada(janela, tmp_path, monkeypatch):
    """D-613: "cancelar" → nada é lido nem dividido e nada vai para o desfazer."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _juntar_a_mao(janela, tela, 1)
    perguntas = _responder(monkeypatch, tela, None)
    feitas = len(janela.acoes.feitas)
    paginas = len(projeto.paginas)
    tela._linhas_do_motor.clear()                          # nada lido: a leitura teria de começar

    tela.botao_dividir_todas.click()
    _assentar(10)
    assert perguntas == [1]
    assert getattr(tela, "_caixa_de_dividir_todas", None) is None, "nenhuma leitura começou"
    assert not any(x.dividir for x in projeto.folhas)
    assert len(projeto.paginas) == paginas
    assert len(janela.acoes.feitas) == feitas, "nada vai para o desfazer"


# --- 4. sem folha juntada à mão: sem aviso, como hoje (D-605) -----------------------------------

def test_d613_sem_juntada_nao_pergunta(janela, tmp_path, monkeypatch):
    """Livro sem nada juntado (uma folha já dividida à mão, as outras inteiras): o "dividir
    todas" não mostra aviso e divide como sempre (D-602), numa ação só."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    tela._ir_para(2)
    _linha_lida(tela)
    tela.botao_nao_dividir.click()                       # dividir esta: dividida, não juntada
    _sem_aviso(monkeypatch, tela)
    feitas = len(janela.acoes.feitas)
    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas))
    assert len(projeto.paginas) == 6
    assert len(janela.acoes.feitas) == feitas + 1


# --- 5. as juntadas pelo "juntar todas" (pergunta aberta) ----------------------------------------

def test_d613_juntar_todas_nao_conta_enquanto_a_pergunta_esta_aberta(janela, tmp_path, monkeypatch):
    """Até o Samuel responder, as folhas juntadas pelo "juntar todas" NÃO contam: "dividir todas"
    depois do "juntar todas" divide tudo sem aviso, como hoje."""
    from core import dividir_a_mao

    assert dividir_a_mao.JUNTAR_TODAS_CONTA is False
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _linha_lida(tela)
    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas))
    tela.botao_juntar_todas.click()
    assert not any(x.dividir for x in projeto.folhas)
    _sem_aviso(monkeypatch, tela)
    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas),
                             "dividir todas depois do juntar todas")
    assert len(projeto.paginas) == 6


def test_d613_juntar_todas_conta_com_a_chave_ligada(janela, tmp_path, monkeypatch):
    """Com a chave ligada (se o Samuel disser que contam), as do "juntar todas" entram no aviso:
    as 3 folhas; "Pular" → nada é dividido e nada vai para o desfazer."""
    from core import dividir_a_mao

    monkeypatch.setattr(dividir_a_mao, "JUNTAR_TODAS_CONTA", True)
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _linha_lida(tela)
    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas))
    tela.botao_juntar_todas.click()
    perguntas = _responder(monkeypatch, tela, True)
    feitas = len(janela.acoes.feitas)
    tela.botao_dividir_todas.click()
    _assentar(10)
    assert perguntas == [3]
    assert not any(x.dividir for x in projeto.folhas)
    assert len(janela.acoes.feitas) == feitas


def test_d613_mistura_conta_so_a_juntada_uma_por_uma(janela, tmp_path, monkeypatch):
    """"juntar todas" e depois a folha 1 dividida e juntada de novo à mão: só ela conta (1);
    "Pular" → a folha 1 fica inteira, as outras (do "juntar todas") são divididas."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(3)])
    projeto = janela.projeto
    _linha_lida(tela)
    _dividir_todas_e_esperar(janela, tela, lambda: all(x.dividir for x in projeto.folhas))
    tela.botao_juntar_todas.click()
    _juntar_a_mao(janela, tela, 0)
    perguntas = _responder(monkeypatch, tela, True)
    _dividir_todas_e_esperar(janela, tela, lambda: projeto.folhas[1].dividir
                             and projeto.folhas[2].dividir)
    assert perguntas == [1]
    assert not projeto.folhas[0].dividir and len(projeto.paginas) == 1 + 2 + 2


def test_d613_juntar_todas_de_uma_folha_so_tambem_e_do_juntar_todas(janela, tmp_path):
    """O "juntar todas" com UMA folha dividida é do "juntar todas" (não da mão), mesmo sendo
    uma folha só; e a conta é a mesma lendo o histórico gravado no disco (reabrir o livro)."""
    from core import dividir_a_mao
    from historico_acoes import HistoricoAcoes

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _linha_lida(tela)
    tela.botao_nao_dividir.click()                       # dividir esta (folha 1)
    tela.botao_juntar_todas.click()                      # junta só a folha 1
    _juntar_a_mao(janela, tela, 1)                       # folha 2: à mão
    feitas = janela.acoes.feitas
    assert dividir_a_mao.folhas_juntadas_a_mao(projeto, feitas) == [1]
    assert dividir_a_mao.folhas_juntadas_a_mao(projeto, feitas, contar_o_juntar_todas=True) \
        == [0, 1]
    if janela.acoes.pasta is not None:
        do_disco = HistoricoAcoes(janela.acoes.pasta)
        do_disco.carregar()
        assert dividir_a_mao.folhas_juntadas_a_mao(projeto, do_disco.feitas) == [1]


# --- 6. o aviso de verdade --------------------------------------------------------------------

def _clicar_no_aviso(texto_do_botao: str, visto: dict) -> None:
    """Quando o aviso abrir, guarda o que ele mostra e clica no botão."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox

    def clicar():
        caixa = QApplication.activeModalWidget()
        if not isinstance(caixa, QMessageBox):
            QTimer.singleShot(20, clicar)
            return
        visto["titulo"] = caixa.windowTitle()
        visto["texto"] = caixa.text()
        visto["explicacao"] = caixa.informativeText()
        visto["botoes"] = [b.text() for b in caixa.buttons()]
        visto["padrao"] = caixa.defaultButton().text() if caixa.defaultButton() else None
        botao = next(b for b in caixa.buttons() if b.text() == texto_do_botao)
        botao.click()

    QTimer.singleShot(20, clicar)


@pytest.mark.parametrize("quantas,pular,frase,explicacao", [
    (1, "Pular esta", "1 folha foi juntada à mão no Dividir. Pular essa folha?",
     "Pular: ela fica inteira, como você deixou. Dividir também: ela é dividida junto com as "
     "outras (o Desfazer traz de volta). As outras folhas são divididas nos dois casos."),
    (2, "Pular as 2", "2 folhas foram juntadas à mão no Dividir. Pular essas folhas?",
     "Pular: elas ficam inteiras, como você deixou. Dividir também: elas são divididas junto "
     "com as outras (o Desfazer traz de volta). As outras folhas são divididas nos dois casos."),
])
def test_d613_o_aviso_como_o_da_d004(janela, tmp_path, quantas, pular, frase, explicacao):
    """O aviso no jeito da D-004: título, a frase com quantas folhas, a explicação, os botões
    "Pular as N"/"Pular esta", "Dividir também" e "cancelar"; o de fábrica é o "Pular"."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    for botao, esperado in ((pular, True), ("Dividir também", False), ("cancelar", None)):
        visto: dict = {}
        _clicar_no_aviso(botao, visto)
        assert tela._perguntar_as_juntadas(quantas) is esperado
        assert visto["titulo"] == "Folhas juntadas à mão"
        assert visto["texto"] == frase
        assert visto["explicacao"] == explicacao
        # a ordem na tela é a do Qt (pelo papel de cada botão), a mesma do aviso da D-004
        assert sorted(visto["botoes"]) == sorted([pular, "Dividir também", "cancelar"])
        assert visto["padrao"] == pular


def test_d613_clicando_no_aviso_de_verdade(janela, tmp_path):
    """O caminho inteiro com o aviso de verdade: folha 1 juntada à mão, "dividir todas",
    clicar "Pular esta" → a folha 1 inteira, a 2 dividida."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _juntar_a_mao(janela, tela, 0)
    visto: dict = {}
    _clicar_no_aviso("Pular esta", visto)
    _dividir_todas_e_esperar(janela, tela, lambda: projeto.folhas[1].dividir)
    assert visto["texto"] == "1 folha foi juntada à mão no Dividir. Pular essa folha?"
    assert not projeto.folhas[0].dividir and len(projeto.paginas) == 3
