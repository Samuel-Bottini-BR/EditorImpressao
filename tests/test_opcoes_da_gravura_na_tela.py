"""As opções do detector de gravuras na tela (item 1.2; decisão do Samuel, 30/09/2026).

"o programa tem que ter essas opções para o usuário conseguir usar" e
"Todo livro começa no contorno 'livre', com a caixinha 'Este livro tem fotos'
para trocar para 'retangular'. Quero poder trocar também só numa página".

Desde a etapa 3 da obra (26/10/2026) o grupo mora na janela do Automático,
etapa "Gravuras e fotos" (a tela "O que fazer" saiu do caminho); o livro só
muda ao rodar.

Testes de máquina:
- a janela do Automático tem o grupo "Gravuras e fotos" e cada escolha vale ao
  rodar; o livro começa com as opções de fábrica; a sensibilidade só fica
  habilitada com "Este livro tem fotos"; o grupo some sem "Limpar a folha";
- reabrir o livro traz as opções salvas para a tela;
- mudar as opções num livro com trabalho só vale ao clicar "Conferir": aí a
  gravura achada sozinha é marcada para refazer, a marcação à mão fica, uma
  cópia do trabalho é guardada antes e o aviso aparece;
- mudar e sair sem "Conferir" não grava a opção nova (como as outras).

Pasta de dados própria (as fixtures de tests/test_mesmo_livro_outro_caminho.py);
nenhuma janela aparece na tela (tests/conftest.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from core.selecao import MAO, Selecao, retangulo  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


class _Escolhas:
    """As escolhas do Automático lidas como os campos do livro."""

    def __init__(self, janela):
        self._estado = janela.estado_do_automatico

    def __getattr__(self, nome):
        return self._estado.opcoes.get(nome)


def _tela(janela):
    """A janela do Automático na etapa "Gravuras e fotos" (era a tela "O que fazer")."""
    jan = janela.janela_do_automatico
    if jan is None:
        jan = janela.abrir_o_automatico("gravuras")
    return jan


def _rodar_gravuras(janela) -> None:
    """Marca só "Gravuras e fotos" e roda no livro todo (o antigo "Conferir")."""
    from core import automatico as A

    janela.estado_do_automatico.marcadas = {A.GRAVURAS}
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)


def test_o_livro_comeca_com_as_opcoes_de_fabrica(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = _tela(janela), janela.projeto
    assert tela.cx_achar_gravuras.isChecked()
    assert not tela.cx_tem_fotos.isChecked()
    assert tela.deslizante.value() == 100
    assert not tela.controles["gravura_mais_sensivel"].isChecked()
    assert tela.controles["gravura_normalizar"].isChecked()
    assert (projeto.gravura_forma, projeto.gravura_sensibilidade,
            projeto.gravura_mais_sensivel, projeto.gravura_normalizar) == ("livre", 100, False, True)
    assert not tela.deslizante.isEnabled(), "sensibilidade só vale com fotos"


def test_cada_controle_grava_no_projeto(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, escolhas = _tela(janela), _Escolhas(janela)
    tela.cx_tem_fotos.setChecked(True)
    assert escolhas.gravura_forma == "retangular"
    assert tela.deslizante.isEnabled()
    tela.deslizante.setValue(70)
    assert escolhas.gravura_sensibilidade == 70 and tela.valor_sensibilidade.text() == "70"
    tela.controles["gravura_mais_sensivel"].setChecked(True)
    tela.controles["gravura_normalizar"].setChecked(False)
    assert escolhas.gravura_mais_sensivel and not escolhas.gravura_normalizar
    tela.cx_achar_gravuras.setChecked(False)
    assert escolhas.gravura_forma == "desligada"
    assert tela.painel_opcoes_gravura.isHidden()
    tela.cx_achar_gravuras.setChecked(True)
    assert escolhas.gravura_forma == "retangular"
    _rodar_gravuras(janela)
    projeto = janela.projeto
    assert (projeto.gravura_forma, projeto.gravura_sensibilidade,
            projeto.gravura_mais_sensivel, projeto.gravura_normalizar) == ("retangular", 70, True, False)


def test_o_grupo_mora_na_etapa_gravuras_e_fotos(janela, pasta):
    """Rascunho do layout ("O painel Automático vai crescer"): o grupo "Gravuras e
    fotos" é uma etapa própria (antes sumia sem "Limpar a folha", na tela antiga)."""
    from core import automatico as A

    assert ("Gravuras e fotos", (A.GRAVURAS,)) in A.GRUPOS
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    assert tela.pilha.currentWidget() is tela.paginas_das_etapas[A.GRAVURAS]


def test_o_resumo_fala_das_gravuras(janela, pasta):
    from core import automatico as A

    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)

    def linha():
        return tela.lista.item_da_etapa(A.GRAVURAS).text()

    assert "seguindo o desenho" in linha()
    tela.cx_tem_fotos.setChecked(True)
    assert "fotos em retângulo" in linha()
    tela.cx_achar_gravuras.setChecked(False)
    assert "não procurar gravuras" in linha()


def test_textos_sem_jargao_e_com_acento(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    textos = [tela.cx_achar_gravuras.text(), tela.cx_tem_fotos.text(),
              tela.controles["gravura_mais_sensivel"].text(), tela.controles["gravura_normalizar"].text()]
    junto = " ".join(textos).lower()
    for jargao in ("scantailor", "retangular", "normaliz", "dpi", "máscara"):
        assert jargao not in junto
    assert "página" in tela.controles["gravura_normalizar"].text()
    assert "também" in tela.controles["gravura_mais_sensivel"].text()


def _marcar_paginas(janela):
    """Duas páginas com marcação: a 0 com uma região da máquina e uma à mão
    (assinatura das opções de fábrica); a 1 só à mão."""
    from core.detectar_regioes import GRAVURA_SCANTAILOR, OpcoesDaGravura, assinatura_da_gravura

    paginas = janela.projeto.paginas
    s0 = Selecao()
    s0.acrescentar(retangulo(0.1, 0.1, 0.5, 0.5, origem="rede"))
    s0.acrescentar(retangulo(0.6, 0.6, 0.8, 0.8, origem=MAO, filtro="original"))
    paginas[0].guardar_selecao(s0)
    paginas[0].gravura_feita_com = assinatura_da_gravura(GRAVURA_SCANTAILOR, OpcoesDaGravura())
    s1 = Selecao()
    s1.acrescentar(retangulo(0.2, 0.2, 0.3, 0.3, origem=MAO))
    paginas[1].guardar_selecao(s1)
    janela._salvar_agora()
    return s0.para_lista(), s1.para_lista()


@pytest.mark.usefixtures("livro_novo_divide")
def test_mudar_as_opcoes_num_livro_com_trabalho_refaz_so_a_gravura_automatica(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    antes_0, antes_1 = _marcar_paginas(janela)
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    gravado_antes = estado.read_bytes()
    janela.avisos.clear()

    # no Automático, marca "Este livro tem fotos" e roda (antes: "O que fazer" e "Conferir")
    _tela(janela).cx_tem_fotos.setChecked(True)
    _rodar_gravuras(janela)

    projeto = janela.projeto
    assert projeto.gravura_forma == "retangular", "a opção nova não valeu"
    # a marcação continua lá (é refeita na hora de desenhar a página)
    assert projeto.paginas[0].selecao == antes_0 and projeto.paginas[1].selecao == antes_1
    assert pipeline._gravura_a_refazer(projeto, projeto.paginas[0])
    assert not pipeline._gravura_a_refazer(projeto, projeto.paginas[1]), \
        "página só com marcação à mão não é refeita"
    # cópia do trabalho de antes, e o aviso
    copias = sorted(estado.parent.glob("projeto.antigo-*.json"))
    assert len(copias) == 1 and copias[0].read_bytes() == gravado_antes
    assert janela.avisos and "procuradas de novo" in janela.avisos[-1]
    assert "à mão fica" in janela.avisos[-1] and str(copias[0].parent)[2:] in janela.avisos[-1]
    # e a opção nova foi para o disco
    assert json.loads(estado.read_text(encoding="utf-8"))["gravura_forma"] == "retangular"


def test_reabrir_traz_as_opcoes_salvas(janela, pasta):
    livro = _pdf(pasta)
    janela.abrir_livro(str(livro))
    _tela(janela).cx_tem_fotos.setChecked(True)
    _tela(janela).deslizante.setValue(40)
    _rodar_gravuras(janela)
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None

    janela.abrir_livro(str(livro))
    assert _tela(janela).cx_tem_fotos.isChecked()
    assert _tela(janela).deslizante.value() == 40
    assert janela.projeto.gravura_forma == "retangular"


def test_mudar_sem_rodar_nao_grava_a_opcao_nova(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _tela(janela).cx_achar_gravuras.setChecked(False)
    janela._fechar_a_janela_do_automatico()
    janela._salvar_agora()
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    assert json.loads(estado.read_text(encoding="utf-8"))["gravura_forma"] == "livre"


def test_rodar_sem_mudar_nada_nao_avisa_nem_copia(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _marcar_paginas(janela)
    janela.avisos.clear()
    _rodar_gravuras(janela)
    assert not janela.avisos
    assert not list(Path(janela.resumo.pasta).glob("projeto.antigo-*.json"))


# ---------------------------------------------------------------------------
# a janela nao espreme o grupo (parecer do verificador de 30/09, r01-r04)
# ---------------------------------------------------------------------------

def test_mais_opcoes_comeca_fechado_e_abre(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    assert tela.painel_mais_opcoes.isHidden() and tela.botao_mais_opcoes.text() == "Mais opções"
    tela.botao_mais_opcoes.click()
    assert not tela.painel_mais_opcoes.isHidden()
    assert tela.botao_mais_opcoes.text() == "Menos opções"


def test_mais_opcoes_abre_sozinho_quando_algo_avancado_mudou(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    janela.projeto.gravura_mais_sensivel = True
    janela.estado_do_automatico.do_projeto(janela.projeto)
    tela = _tela(janela)
    assert tela.botao_mais_opcoes.isChecked() and not tela.painel_mais_opcoes.isHidden()


@pytest.mark.parametrize("largura, altura", [(1152, 560), (1280, 520), (1366, 600)])
def test_janela_baixa_nao_espreme_as_linhas(janela, pasta, largura, altura):
    """Numa janela baixa nenhuma linha fica mais baixa que precisa (a 1440 x 880 com
    125%, as linhas ficavam com 2 pontos: r01); a página das opções tem rolagem."""
    from PySide6.QtWidgets import QApplication

    janela.abrir_livro(str(_pdf(pasta)))
    janela.resize(largura, altura)
    janela.show()
    tela = _tela(janela)
    tela.resize(largura, altura)
    tela.cx_tem_fotos.setChecked(True)
    tela.botao_mais_opcoes.setChecked(True)
    for _ in range(5):
        QApplication.processEvents()
    controles = [tela.cx_achar_gravuras, tela.cx_tem_fotos, tela.deslizante,
                 tela.controles["gravura_mais_sensivel"], tela.controles["gravura_normalizar"]]
    for controle in controles:
        assert controle.height() >= controle.minimumSizeHint().height(), controle
    janela._fechar_a_janela_do_automatico()
    janela.hide()


# ---------------------------------------------------------------------------
# o Automático acompanha o desfazer e o refazer (parecer do verificador, 30/09, r15)
# ---------------------------------------------------------------------------

def test_o_automatico_acompanha_o_desfazer(janela, pasta):
    """Desfeita uma ação que muda o filtro do livro ("livro.filtro_padrao"), o
    Automático mostra o filtro de antes (como a tela "O que fazer" mostrava)."""
    from PySide6.QtWidgets import QApplication

    from historico_acoes import aplicar
    from modelos import Acao

    janela.abrir_livro(str(_pdf(pasta)))
    projeto = janela.projeto
    acao = Acao.nova("tirar_o_fundo_do_livro", "pagina", [0],
                     {"livro.filtro_padrao": projeto.filtro_padrao},
                     {"livro.filtro_padrao": "magico_pro"}, "Filtro do livro")
    aplicar(projeto, acao, acao.depois)
    janela.acoes.registrar(acao)
    janela.estado_do_automatico.do_projeto(projeto)
    assert _Escolhas(janela).filtro_padrao == "magico_pro"

    janela.tela_conferir.desfazer()
    QApplication.processEvents()
    assert projeto.filtro_padrao == "original"
    assert _Escolhas(janela).filtro_padrao == "original", "o Automático ficou com o filtro desfeito"
    jan = janela.abrir_o_automatico("limpar")
    assert jan.radios_de_filtro["original"].isChecked()
    janela._fechar_a_janela_do_automatico()
    janela.tela_conferir.refazer()
    assert _Escolhas(janela).filtro_padrao == "magico_pro"
