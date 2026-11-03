"""Prova de comportamento da D-602 (03/11/2026): no Dividir, a linha do motor de corte aparece
antes de cortar, "dividir todas" e o nome "motor de corte".

Samuel, testando o Dividir no Gradus Primus (prints a-45 a a-47): "quando eu entro no dividir
não aparece a linha azul, então eu aperto dividir folha, ele já dividi automaticamente sem mostrar
a linha azul, ela não aparece mais em nenhuma folha, só aparece quando eu aperto duas lado a lado.
Quando eu estiver na ferramenta de dividir, o programa deveria carregar com a conta que está
escolhida, e dai eu conseguir ver a linha e dai eu clicar e dividir esta, dai ele reparte, se eu
apertasse para todas as folhas ele carregaria para todas as folhas, faria a leitura em todas as
folhas. teve um momento também que o botão do jeito ( que eu acho um nome bem ruim, acho que o
nome poderia ser motor de corte) ficou travado e não dava para mudar." · "quando a folha for
dupla, ela vai aparecer a linha de divisão ou até quando for só uma folha vai aparecer?" → só nas
duplas → "pode ser assim na questão do divisor."
Livro de decisões: "Na ferramenta Dividir, a folha dupla ainda inteira já mostra a linha azul onde
o motor escolhido cortaria, antes de cortar (também em "Uma página"); a folha que o motor acha de
uma página só não mostra linha. "dividir esta" corta nessa linha. Botão novo "dividir todas": o
motor faz a conta em cada folha do livro e corta cada folha dupla na sua própria linha (as de uma
página ficam inteiras). O "usar em todas" (D-090, copia a linha desta folha) fica como está.
"jeito" vira "motor de corte" no Dividir e no Automático [...]; os nomes das opções ("o do
ScanTailor", "o do Editor", D-373) não mudam. Defeito: a lista do jeito ficou travada, sem deixar
trocar (causa a achar)."

O que se mede: a linha que a vista do Dividir desenha (visível ou não, onde, se arrasta), o
projeto (folhas divididas, onde, quantas páginas), o Histórico (uma ação do desfazer) e os textos
dos rótulos. O ANTIGO SAIU: no código de antes (8846017) a folha inteira nunca mostrava a linha, a
lista do motor ficava cinza (travada) em toda folha não dividida, e não havia "dividir todas".

Livros sintéticos: o livro aberto com a dobra FORA do meio (página da esquerda mais estreita: a
dobra fica a 44% da largura, para a linha do motor não se confundir com o meio de fábrica, 0,5) e
uma folha em pé (uma página só).
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)

DOBRA = 600 / (600 + 760)            # onde fica a dobra do livro aberto sintético (0,441)


def _aberto_torto() -> np.ndarray:
    """O livro aberto com a página da esquerda mais estreita: a dobra a 44% da largura."""
    return np.concatenate([_pagina(600), _pagina(760)], axis=1)


def _em_pe() -> np.ndarray:
    """Uma folha em pé: uma página só (a capa, a folha de rosto)."""
    return _pagina(600, 840)


def _assentar(vezes: int = 3) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _no_dividir(janela, tmp_path: Path, folhas) -> object:
    """O caminho do Samuel no Gradus Primus: abrir o livro (nada dividido), escolher a
    ferramenta Dividir (de fábrica, "Uma página") na folha 1."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import UMA

    janela.show()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", folhas))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assert tela.aba_atual == ABA_CORTE and tela.mostrar == UMA
    assert not any(f.dividir for f in janela.projeto.folhas), "ao abrir, nada dividido"
    return tela


def _linha_lida(tela) -> None:
    """Espera a conta do motor na folha da vez acabar (ela roda por trás). No código de
    antes não havia conta nenhuma: volta na hora."""
    from ui.tela_conferir import ABA_CORTE

    vista = tela.visualizadores[ABA_CORTE]
    _assentar(5)
    _esperar(lambda: not getattr(vista, "lendo_a_linha", False), motivo="a conta do motor")
    tela.atualizar()


# --- 1. a folha dupla inteira mostra a linha do motor, em "Uma página" -----------------------

def test_reversao_d602_linha_azul_na_folha_dupla_inteira_em_uma_pagina(janela, tmp_path):
    """D-602, defeito de 03/11 (a-45: "quando eu entro no dividir não aparece a linha azul"):
    folha dupla ainda inteira, no Dividir com "Uma página" → a linha azul aparece onde o
    motor cortaria (na dobra, a 44%), e NADA é cortado (a folha continua uma página só).
    No código de antes (8846017) a linha só aparecia em folha dividida: este teste falha lá."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    _linha_lida(tela)
    assert vista.corte_visivel, "a folha dupla inteira mostra a linha azul"
    assert vista.posicao_corte == pytest.approx(DOBRA, abs=0.03)
    assert not projeto.folhas[0].dividir and len(projeto.paginas) == 2, "nada foi cortado"
    assert not janela.acoes.pode_desfazer, "abrir o Dividir não grava nada"
    # a linha da folha inteira é só para ver: arrastar não muda nada (pergunta ao Samuel)
    assert not vista.corte_arrastavel


def test_d602_folha_de_uma_pagina_nao_mostra_linha(janela, tmp_path):
    """D-602 ("só nas duplas" → "pode ser assim na questão do divisor"): a folha em pé, que o
    motor acha de uma página só, não mostra linha; a dupla, ao lado, mostra."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_em_pe(), _aberto_torto()])
    vista = tela.visualizadores[ABA_CORTE]
    _linha_lida(tela)
    assert not vista.corte_visivel, "folha de uma página só: sem linha"
    tela._navegar(1)
    _linha_lida(tela)
    assert tela.indice_folha == 1 and vista.corte_visivel


def test_d602_linha_tambem_em_duas_lado_a_lado(janela, tmp_path):
    """D-602 ("também em "Uma página"", ou seja, nos dois): em "Duas lado a lado" a folha
    dupla inteira mostra a mesma linha."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    vista = tela.visualizadores[ABA_CORTE]
    tela.botoes_mostrar[DUAS].click()
    _linha_lida(tela)
    assert vista.corte_visivel
    assert vista.posicao_corte == pytest.approx(DOBRA, abs=0.03)


# --- 2. "dividir esta" corta nessa linha ------------------------------------------------------

def test_d602_dividir_esta_corta_na_linha_mostrada(janela, tmp_path):
    """D-602 ("e dai eu clicar e dividir esta, dai ele reparte"): "dividir esta" corta
    exatamente onde a linha estava, numa ação do desfazer; com "Uma página" aparece a metade
    (D-601, sem a linha)."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    _linha_lida(tela)
    mostrada = vista.posicao_corte
    assert tela.botao_nao_dividir.text() == "dividir esta"
    tela.botao_nao_dividir.click()
    folha = projeto.folhas[0]
    assert folha.dividir and folha.posicao_corte == pytest.approx(mostrada, abs=1e-3)
    assert [p.metade for p in projeto.paginas if p.folha == 0] == ["esquerda", "direita"]
    assert not projeto.folhas[1].dividir, "só esta folha"
    tela.desfazer()
    assert not projeto.folhas[0].dividir and len(projeto.paginas) == 2


def test_d602_folha_juntada_mostra_a_linha_de_antes(janela, tmp_path):
    """D-602 com a D-498: depois de "não dividir esta", a folha (dupla) mostra a linha onde o
    "dividir esta" a corta de novo - a linha de antes, mesmo arrastada à mão."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    _linha_lida(tela)
    tela.botao_nao_dividir.click()                       # dividir esta
    tela.botoes_mostrar[DUAS].click()
    vista.corte_movido.emit(0.47)                        # a linha acertada à mão
    tela.botoes_mostrar[UMA].click()
    tela.botao_nao_dividir.click()                       # não dividir esta
    _linha_lida(tela)
    assert not projeto.folhas[0].dividir
    assert vista.corte_visivel and vista.posicao_corte == pytest.approx(0.47)
    tela.botao_nao_dividir.click()                       # dividir esta: na linha de antes
    assert projeto.folhas[0].dividir and projeto.folhas[0].posicao_corte == pytest.approx(0.47)


# --- 3. a lista do motor não trava ---------------------------------------------------------------

def test_reversao_d602_lista_do_motor_nao_trava_na_folha_inteira(janela, tmp_path):
    """D-602, defeito ("teve um momento também que o botão do jeito [...] ficou travado e não
    dava para mudar"). CAUSA: a lista só ficava acesa em folha DIVIDIDA
    (_atualizar_botoes: setEnabled(folha.dividir)); toda folha ainda inteira - todas, ao
    abrir o livro - a deixava cinza, e trocar não fazia nada (_trocar_jeito_da_folha voltava
    sem mudar). Agora: acesa na folha inteira; trocar grava o motor desta folha (uma ação do
    desfazer) e a linha é lida de novo pelo motor novo. No código de antes falha."""
    from core import dividir_scantailor as ds

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    combo = tela.combo_jeito_da_folha
    assert combo.isEnabled() and tela.rotulo_jeito_da_folha.isEnabled(), "a lista não trava"
    agora = combo.currentData()
    outro = next(j for j in ds.JEITOS if j != agora)
    combo.setCurrentIndex(combo.findData(outro))
    assert projeto.folhas[0].dividir_como == outro, "trocar vale nesta folha"
    assert projeto.folhas[1].dividir_como is None, "só nesta folha"
    assert not projeto.folhas[0].dividir, "trocar o motor não corta"
    _linha_lida(tela)
    assert combo.currentData() == outro and combo.isEnabled()
    tela.desfazer()
    assert projeto.folhas[0].dividir_como is None
    assert combo.currentData() == agora and combo.isEnabled()


def test_d602_lista_do_motor_acesa_depois_de_dividir_e_juntar(janela, tmp_path):
    """O caminho do Samuel (cortar, juntar, voltar): a lista continua acesa em todos os
    passos (antes ficava cinza depois do "não dividir esta")."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    combo = tela.combo_jeito_da_folha
    _linha_lida(tela)
    tela.botao_nao_dividir.click()                       # dividir esta
    assert combo.isEnabled()
    tela.botao_nao_dividir.click()                       # não dividir esta
    assert combo.isEnabled()
    tela.botao_juntar_todas.click()
    assert combo.isEnabled()
    tela.desfazer()
    tela._navegar(1)
    assert combo.isEnabled()


# --- 4. "dividir todas" --------------------------------------------------------------------------

def test_d602_dividir_todas_corta_as_duplas_cada_uma_na_sua_linha(janela, tmp_path):
    """D-602 ("se eu apertasse para todas as folhas ele carregaria para todas as folhas, faria
    a leitura em todas as folhas"): "dividir todas" lê cada folha pelo motor (por trás, com
    andamento) e corta cada dupla na SUA linha; a de uma página só fica inteira; a folha já
    dividida não é dividida de novo (a linha dela fica). Uma ação só do desfazer."""
    from ui.tela_conferir import ABA_CORTE

    simetrico = np.concatenate([_pagina(), _pagina()], axis=1)       # a dobra no meio
    tela = _no_dividir(janela, tmp_path, [_em_pe(), _aberto_torto(), simetrico, _aberto_torto()])
    projeto = janela.projeto
    # a folha 4 já dividida, com a linha arrastada à mão (não pode mudar)
    tela._ir_para(3)
    _linha_lida(tela)
    tela.botao_nao_dividir.click()
    from ui.widgets.paginas_rolando import DUAS

    tela.botoes_mostrar[DUAS].click()
    tela.visualizadores[ABA_CORTE].corte_movido.emit(0.47)
    assert projeto.folhas[3].posicao_corte == pytest.approx(0.47)
    feitas_antes = len(janela.acoes.feitas)

    assert tela.botao_dividir_todas.text() == "dividir todas"
    tela.botao_dividir_todas.click()
    _esperar(lambda: projeto.folhas[1].dividir, motivo="dividir todas")
    _assentar(5)
    f = projeto.folhas
    assert not f[0].dividir and len([p for p in projeto.paginas if p.folha == 0]) == 1, \
        "a folha de uma página fica inteira"
    assert f[1].dividir and f[1].posicao_corte == pytest.approx(DOBRA, abs=0.03)
    assert f[2].dividir and f[2].posicao_corte == pytest.approx(0.5, abs=0.03)
    assert f[3].dividir and f[3].posicao_corte == pytest.approx(0.47), "a já dividida fica"
    assert len(projeto.paginas) == 1 + 2 + 2 + 2
    # como o "juntar todas" (D-590): a pessoa não olhou cada uma, nada fica "conferida"
    assert not f[1].revisada and not f[2].revisada
    assert len(janela.acoes.feitas) == feitas_antes + 1, "uma ação só do desfazer"
    tela.desfazer()                                       # uma ação só: volta tudo
    assert not f[1].dividir and not f[2].dividir and f[3].dividir
    assert len(projeto.paginas) == 1 + 1 + 1 + 2


def test_d602_dividir_todas_usa_a_linha_ja_mostrada(janela, tmp_path):
    """A folha cuja linha já foi lida (mostrada) é cortada nessa mesma linha pelo "dividir
    todas" (o motor não muda de ideia entre o que mostrou e o que corta)."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    _linha_lida(tela)
    mostrada = vista.posicao_corte
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    assert projeto.folhas[0].posicao_corte == pytest.approx(mostrada, abs=1e-3)


def test_d602_dividir_todas_parar_nao_muda_nada(janela, tmp_path, monkeypatch):
    """CLAUDE.md §3 ("botão de cancelar que funciona"): "parar" no meio da leitura → nenhuma
    folha é cortada e nada vai para o desfazer."""
    from core import dividir_a_mao

    tela = _no_dividir(janela, tmp_path, [_aberto_torto() for _ in range(4)])
    projeto = janela.projeto
    lida = dividir_a_mao.ler_a_linha

    def devagar(*args, **kwargs):
        time.sleep(0.3)
        return lida(*args, **kwargs)

    monkeypatch.setattr(dividir_a_mao, "ler_a_linha", devagar)
    tela._linhas_do_motor.clear()
    tela.botao_dividir_todas.click()
    caixa = tela._caixa_de_dividir_todas
    assert caixa is not None, "aparece a caixa do andamento, com o parar"
    from PySide6.QtWidgets import QPushButton

    parar = next(b for b in caixa.findChildren(QPushButton) if b.text() == "parar")
    parar.click()                                         # o que a pessoa faz
    tarefa = tela._tarefa_de_dividir_todas
    tarefa.wait(10000)
    _assentar(10)
    assert not any(f.dividir for f in projeto.folhas)
    assert not janela.acoes.pode_desfazer


# --- 5. "usar em todas" fica como está (D-090) ---------------------------------------------------

def test_d602_usar_em_todas_continua_copiando_a_linha_desta_folha(janela, tmp_path, monkeypatch):
    """D-090: "usar em todas" copia a linha DESTA folha para as folhas escolhidas (não lê o
    motor em cada uma: isso é o "dividir todas")."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _linha_lida(tela)
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    tela.botoes_mostrar[DUAS].click()
    tela._ir_para(0)
    tela.visualizadores[ABA_CORTE].corte_movido.emit(0.52)
    monkeypatch.setattr(tela, "_escolher_folhas_da_linha", lambda: [0, 1, 2])
    tela._corte_em_todas()
    assert [round(f.posicao_corte, 4) for f in projeto.folhas] == [0.52, 0.52, 0.52]


# --- 6. "motor de corte" no lugar de "jeito" -----------------------------------------------------

def _textos(widget) -> list[str]:
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel

    textos = []
    for w in widget.findChildren(QLabel) + widget.findChildren(QAbstractButton):
        textos.append(w.text())
        textos.append(w.toolTip())
    for c in widget.findChildren(QComboBox):
        textos.append(c.toolTip())
        textos.extend(c.itemText(i) for i in range(c.count()))
    return [t for t in textos if t]


def test_d602_jeito_vira_motor_de_corte_no_dividir(janela, tmp_path):
    """D-602: o rótulo da lista e a linha do "Para o livro todo" do Dividir dizem "motor de
    corte"; a palavra "jeito" não aparece em nenhum rótulo, botão ou dica do Dividir; os nomes
    das opções continuam "o do Editor" e "o do ScanTailor" (D-373)."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    painel = tela.propriedades_das_abas[ABA_CORTE]
    textos = _textos(painel)
    assert tela.rotulo_jeito_da_folha.text() == "motor de corte:"
    assert any(t.startswith("Motor de corte: ") for t in textos), "Para o livro todo"
    assert not [t for t in textos if "jeito" in t.lower()], "jeito não aparece no Dividir"
    combo = tela.combo_jeito_da_folha
    assert sorted(combo.itemText(i) for i in range(combo.count())) == ["o do Editor", "o do ScanTailor"]


def test_d602_jeito_vira_motor_de_corte_no_automatico(app):
    """D-602: no Automático, a etapa 1 ("Dividir folhas ao meio") diz "motor de corte" - a
    lista das opções e a segunda linha da etapa ("Para o livro todo" do painel) -, e não
    "jeito"; as opções continuam com os nomes da D-373."""
    from core import automatico as A
    from core import dividir_scantailor as ds
    from ui.automatico import EstadoDoAutomatico, PainelDeOpcoes, texto_das_opcoes

    for jeito in ds.JEITOS:
        texto = texto_das_opcoes(A.DIVIDIR, {"dividir_como": jeito})
        assert texto == "motor de corte: " + ds.NOMES_DOS_JEITOS[jeito]
    painel = PainelDeOpcoes(EstadoDoAutomatico())
    pagina = painel.paginas_das_etapas[A.DIVIDIR]
    textos = _textos(pagina)
    assert "Motor de corte:" in textos
    assert not [t for t in textos if "jeito" in t.lower()], "jeito não aparece na etapa 1"
    combo = painel.controles["dividir_como"]
    assert sorted(combo.itemText(i) for i in range(combo.count())) == ["o do Editor", "o do ScanTailor"]
