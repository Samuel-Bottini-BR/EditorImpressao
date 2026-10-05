"""O modo Misto na tela (ligar o Misto ao programa, passo 3; provisorio ate o layout).

Pedidos do Samuel: a caixinha "So as letras" no Preto e branco, na tela "O
que fazer" (livro) e na aba Filtro (pagina) (conferencia 10, P1 (a));
escolher A/B/C "bem visivel" (conferencia 8); a caixinha das molduras
"apagada (cinza) enquanto 'So as letras' estiver marcada, e volta como estava
ao desligar" (conferencia 11, P5 (a)); as outras escolhas do papel da gravura
(P2) e das letras da moldura (P4) disponiveis (conferencia 12).

Testes de maquina (sem janela na tela, tests/conftest.py):
    - livro: cada controle grava no projeto; os tres botoes so com a caixinha
      marcada; a caixinha das molduras apaga e volta como estava; projeto
      salvo volta para a tela; textos sem jargao e sem emoji;
    - pagina: so no Preto e branco; mostra o que vale (do livro ou dela);
      cada mudanca e uma acao do desfazer; "todas" leva as escolhas junto;
      a previa e refeita (a chave muda).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import misto  # noqa: E402
from core.filtros import MELHORAR, PRETO_E_BRANCO  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)


@pytest.fixture(autouse=True)
def leitor_rapido(monkeypatch):
    """As previas de fundo nao chamam o leitor de texto de verdade (o modelo
    leva segundos e nao e o que se testa aqui)."""
    from core import pipeline

    monkeypatch.setattr(pipeline.linhas_do_texto, "linhas_da_pagina", lambda *a, **k: [])
    aquecidas = []
    monkeypatch.setattr(pipeline.linhas_do_texto, "aquecer_em_segundo_plano",
                        lambda: aquecidas.append(1))
    return aquecidas


# --- a tela "O que fazer" (o livro) ------------------------------------------

def test_o_livro_comeca_sem_so_as_letras_e_com_a_de_fabrica(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = janela.tela_opcoes
    e = tela.escolhas_misto
    assert not e.caixa.isChecked()
    assert e.painel.isHidden(), "os botoes so aparecem com a caixinha marcada"
    assert e.fora_do_texto() == misto.FORA_REDE
    assert e.botoes[misto.FORA_REDE].isChecked()
    assert e.painel_mais.isHidden(), "o 'Mais opcoes' comeca recolhido"
    assert tela.cx_decoracao_pb.isEnabled()
    assert janela.projeto.misto_so_as_letras is False


def test_cada_controle_do_livro_grava_no_projeto(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    e = tela.escolhas_misto
    e.caixa.setChecked(True)
    assert projeto.misto_so_as_letras is True
    assert not e.painel.isHidden()
    e.botoes[misto.FORA_APAGAR].click()
    assert projeto.misto_fora_do_texto == misto.FORA_APAGAR
    assert e.botoes[misto.FORA_APAGAR].isChecked() and not e.botoes[misto.FORA_REDE].isChecked()
    e.botoes[misto.FORA_TUDO].click()
    assert projeto.misto_fora_do_texto == misto.FORA_TUDO
    e.botao_mais.click()
    assert not e.painel_mais.isHidden()
    e.combo_papel.setCurrentIndex(e.combo_papel.findData(misto.PAPEL_COMO_ESCANEADO))
    assert projeto.misto_papel_da_gravura == misto.PAPEL_COMO_ESCANEADO
    e.combo_letras.setCurrentIndex(e.combo_letras.findData(misto.LETRAS_PRETAS))
    assert projeto.misto_letras_na_moldura == misto.LETRAS_PRETAS
    e.caixa.setChecked(False)
    assert projeto.misto_so_as_letras is False
    assert e.painel.isHidden()
    assert projeto.misto_fora_do_texto == misto.FORA_TUDO, "desligar nao esquece a escolha"


@pytest.mark.parametrize("molduras_antes", [False, True])
def test_a_caixinha_das_molduras_apaga_e_volta_como_estava(janela, pasta, molduras_antes):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    tela.cx_decoracao_pb.setChecked(molduras_antes)
    tela.escolhas_misto.caixa.setChecked(True)
    assert not tela.cx_decoracao_pb.isEnabled(), "tinha de ficar apagada (cinza)"
    assert tela.cx_decoracao_pb.isChecked() == molduras_antes
    tela.escolhas_misto.caixa.setChecked(False)
    assert tela.cx_decoracao_pb.isEnabled()
    assert tela.cx_decoracao_pb.isChecked() == molduras_antes
    assert projeto.pb_decoracao_em_preto_e_branco == molduras_antes


def test_projeto_salvo_volta_para_a_tela(janela, pasta):
    caminho = str(_pdf(pasta))
    janela.abrir_livro(caminho)
    salvo = Projeto(caminho_entrada=caminho, misto_so_as_letras=True,
                    misto_fora_do_texto=misto.FORA_APAGAR,
                    misto_letras_na_moldura=misto.LETRAS_COR_FUNDO_ORIGINAL)
    janela._trazer_opcoes_salvas(salvo)
    e = janela.tela_opcoes.escolhas_misto
    assert e.caixa.isChecked() and e.botoes[misto.FORA_APAGAR].isChecked()
    assert e.combo_letras.currentData() == misto.LETRAS_COR_FUNDO_ORIGINAL
    assert not e.painel_mais.isHidden(), "escolha fora do padrao abre o 'Mais opcoes'"
    assert janela.projeto.misto_fora_do_texto == misto.FORA_APAGAR


def test_projeto_antigo_volta_com_o_misto_desligado(janela, pasta):
    """Objeto salvo por uma versao anterior, sem os campos (regra do Samuel,
    conferencia 14: abrir arquivos de versoes anteriores)."""
    caminho = str(_pdf(pasta))
    janela.abrir_livro(caminho)
    janela.tela_opcoes.escolhas_misto.caixa.setChecked(True)
    salvo = Projeto(caminho_entrada=caminho)
    for campo in misto.CAMPOS_DO_MISTO:
        delattr(salvo, campo)            # sem o campo no objeto: vale o da classe
    janela._trazer_opcoes_salvas(salvo)
    assert janela.projeto.misto_so_as_letras is False
    assert not janela.tela_opcoes.escolhas_misto.caixa.isChecked()


def test_textos_sem_jargao_e_sem_emoji(janela, pasta):
    e = janela.tela_opcoes.escolhas_misto
    textos = [e.caixa.text(), e.caixa.toolTip(), e.botao_mais.text(), e.frase_do_escolhido.text()]
    textos += [b.text() for b in e.botoes.values()] + [b.toolTip() for b in e.botoes.values()]
    textos += [e.combo_papel.itemText(i) for i in range(e.combo_papel.count())]
    textos += [e.combo_letras.itemText(i) for i in range(e.combo_letras.count())]
    junto = " ".join(textos)
    for jargao in ("ocr", "doctr", "kraken", "sauvola", "misto", "máscara", "binari"):
        assert jargao not in junto.lower(), jargao
    assert all(ord(c) < 0x2000 for c in junto), "emoji ou simbolo estranho"
    assert [b.text() for b in e.botoes.values()] == [
        "Guardar a tinta forte", "Tudo em preto e branco", "Só o texto achado"]
    assert e.caixa.text() == "Só as letras"


def test_a_caixinha_tem_o_quadrado_a_vista(janela, pasta):
    """Regra O1: caixinha com o quadrado visivel (ui/estilo)."""
    assert "QCheckBox::indicator" in janela.tela_opcoes.escolhas_misto.caixa.styleSheet()


# --- a aba Filtro (a pagina) ---------------------------------------------------

@pytest.fixture
def conferir(app, pasta):
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=3)
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste", dividir_folhas=False,
                      detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(3)]
    projeto.paginas[2].filtro = MELHORAR
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    yield tela
    previas.parar()


def test_so_aparece_no_preto_e_branco(conferir):
    assert not conferir.escolhas_misto.isHidden()
    conferir.ir_para_pagina(2)                    # Melhorar
    assert conferir.escolhas_misto.isHidden()
    conferir.ir_para_pagina(0)
    assert not conferir.escolhas_misto.isHidden()


def test_a_pagina_mostra_o_que_vem_do_livro(conferir):
    projeto = conferir.projeto
    projeto.misto_so_as_letras = True
    projeto.misto_fora_do_texto = misto.FORA_TUDO
    conferir.atualizar()
    e = conferir.escolhas_misto
    assert e.caixa.isChecked() and e.botoes[misto.FORA_TUDO].isChecked()
    assert projeto.paginas[0].misto_so_as_letras is None, "mostrar nao pode gravar na pagina"
    assert not conferir.acoes.pode_desfazer, "mostrar nao pode virar acao"


def test_mudar_na_pagina_e_acao_do_desfazer(conferir):
    projeto, e = conferir.projeto, conferir.escolhas_misto
    pagina, outra = projeto.paginas[0], projeto.paginas[1]
    chave_antes = conferir.previas.chave(0, 110)
    e.caixa.setChecked(True)
    assert pagina.misto_so_as_letras is True and outra.misto_so_as_letras is None
    assert conferir.previas.chave(0, 110) != chave_antes, "a previa tinha de ser refeita"
    assert "Só as letras" in conferir.acoes.descricao_desfazer()
    e.botoes[misto.FORA_APAGAR].click()
    assert pagina.misto_fora_do_texto == misto.FORA_APAGAR
    assert "Só o texto achado" in conferir.acoes.descricao_desfazer()
    e.combo_letras.setCurrentIndex(e.combo_letras.findData(misto.LETRAS_PRETAS))
    assert pagina.misto_letras_na_moldura == misto.LETRAS_PRETAS
    e.combo_papel.setCurrentIndex(e.combo_papel.findData(misto.PAPEL_COMO_ESCANEADO))
    assert pagina.misto_papel_da_gravura == misto.PAPEL_COMO_ESCANEADO

    conferir.desfazer()
    assert pagina.misto_papel_da_gravura is None
    conferir.desfazer()
    conferir.desfazer()
    assert pagina.misto_fora_do_texto is None
    assert e.botoes[misto.FORA_REDE].isChecked(), "a tela volta junto com o desfazer"
    conferir.desfazer()
    assert pagina.misto_so_as_letras is None and not e.caixa.isChecked()
    conferir.refazer()
    assert pagina.misto_so_as_letras is True and e.caixa.isChecked()


def test_clicar_no_que_ja_vale_nao_vira_acao(conferir):
    conferir.escolhas_misto.botoes[misto.FORA_REDE].click()
    assert not conferir.acoes.pode_desfazer


def test_todas_leva_as_escolhas_do_misto(conferir):
    projeto, e = conferir.projeto, conferir.escolhas_misto
    e.caixa.setChecked(True)
    e.botoes[misto.FORA_TUDO].click()
    conferir._filtro_em_todas()
    for pagina in projeto.paginas:
        assert pagina.misto_so_as_letras is True
        assert pagina.misto_fora_do_texto == misto.FORA_TUDO
    conferir.desfazer()
    assert projeto.paginas[1].misto_so_as_letras is None


def test_ligar_o_a_aquece_o_leitor_antes_da_previa(conferir, leitor_rapido):
    """A primeira previa no Misto A nao espera abrir o leitor de texto
    (~7 a 20 s medidos): ele abre numa thread a parte quando o A passa a valer."""
    assert leitor_rapido == [], "sem o Misto, nada de abrir o leitor"
    conferir.escolhas_misto.caixa.setChecked(True)
    assert leitor_rapido, "ligar o A tinha de aquecer o leitor"
    leitor_rapido.clear()
    conferir.escolhas_misto.botoes[misto.FORA_TUDO].click()
    assert leitor_rapido == [], "a B nao usa o leitor"
