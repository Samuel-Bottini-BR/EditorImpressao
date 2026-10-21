"""Testes de reversão do "Para revisar" (regra do Samuel de 19/10/2026,
CLAUDE.md §4.7: todo bug consertado ganha um teste que FALHA no código antigo
e PASSA no novo).

Os bugs são os da segunda conferência do verificador (ramo
`verif-para-revisar-2026-10-13`, `2920f21`, relatorios/conferir/
para-revisar-2026-10-13/conferencia.md, "Bugs para a Lista de bugs"):

  20/10/2026 - "a lista 'Antes de processar' mistura 'Folha N' e 'Página N'":
      o aviso de uma FOLHA (qualidade baixa, muito torta, tamanho) aparecia
      como "Folha 2 - ..." no meio das linhas "Página N - ...", e a folha 2
      nem sempre é a página 2 do livro (depois de uma folha dividida, não é).
  20/10/2026 - "os textos novos dos avisos ainda dizem 'aba Marcar' e 'aba
      Bordas'": o layout aprovado (no fase-1 desde 14/10) não tem abas.

Código antigo = o ramo `fase2-para-revisar` em `ce2b835` (antes da junção com
o fase-1). Testes de máquina; a janela é montada sem aparecer.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from core import analise, avisos
from core.filtros import PRETO_E_BRANCO
from modelos import ConfigFolha, ConfigPagina, Projeto

RAIZ = Path(__file__).resolve().parent.parent


def _livro_com_uma_folha_dividida() -> Projeto:
    """3 folhas; a primeira dividida em duas páginas. Folha 2 = página 3,
    folha 3 = página 4: o número da folha NÃO é o da página."""
    p = Projeto(caminho_entrada=str(RAIZ / "nao-existe.pdf"))
    p.folhas = [ConfigFolha(indice=0, dividir=True), ConfigFolha(indice=1, dividir=False),
                ConfigFolha(indice=2, dividir=False)]
    p.paginas = [ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO),
                 ConfigPagina(indice=1, folha=0, filtro=PRETO_E_BRANCO),
                 ConfigPagina(indice=2, folha=1, filtro=PRETO_E_BRANCO),
                 ConfigPagina(indice=3, folha=2, filtro=PRETO_E_BRANCO)]
    p.folhas[0].alertas = [analise.RESOLUCAO_BAIXA]       # folha 1 = páginas 1 e 2
    p.folhas[1].alertas = [analise.MUITO_TORTA]           # folha 2 = página 3
    p.paginas[3].alertas = [analise.DESENHO_APAGADO]      # página 4
    return p


def test_bug_20_10_a_lista_antes_de_processar_so_fala_em_pagina():
    """Bug de 20/10/2026 (verificador): a lista "Antes de processar" misturava
    "Folha N" e "Página N". Agora toda linha diz a(s) PÁGINA(S) do livro, e o
    aviso da folha leva o número das páginas que saíram dela."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from ui.janela_dos_avisos import JanelaDosAvisos

    QApplication.instance() or QApplication([])
    p = _livro_com_uma_folha_dividida()
    janela = JanelaDosAvisos(avisos.pendentes_do_livro(p), antes_de_processar=True, projeto=p)
    linhas = janela.linhas()
    assert linhas == [
        "Páginas 1 e 2  -  " + analise.descrever(analise.RESOLUCAO_BAIXA).titulo,
        "Página 3  -  " + analise.descrever(analise.MUITO_TORTA).titulo,
        "Página 4  -  " + analise.descrever(analise.DESENHO_APAGADO).titulo,
    ], linhas
    assert not any(linha.startswith("Folha") for linha in linhas)
    janela.deleteLater()


def test_bug_20_10_o_aviso_da_folha_diz_as_paginas_dela():
    """A conta por trás da linha (core.avisos.onde_no_livro): folha com uma
    página, com duas, e folha sem página nenhuma no livro (todas tiradas):
    só então sobra "Folha N", porque não há página para nomear."""
    p = _livro_com_uma_folha_dividida()
    folha = avisos.FOLHA
    assert avisos.onde_no_livro(avisos.Aviso(folha, 0, analise.RESOLUCAO_BAIXA), p) == "Páginas 1 e 2"
    assert avisos.onde_no_livro(avisos.Aviso(folha, 1, analise.MUITO_TORTA), p) == "Página 3"
    assert avisos.onde_no_livro(avisos.Aviso(avisos.PAGINA, 3, analise.COR), p) == "Página 4"
    p.paginas[3].apagada = True
    assert avisos.onde_no_livro(avisos.Aviso(folha, 2, analise.MUITO_TORTA), p) == "Folha 3"


def test_bug_20_10_os_textos_dos_avisos_nao_falam_de_aba():
    """Bug de 20/10/2026 (verificador): os textos dos avisos diziam "Confira na
    aba Marcar" e "Confira o corte na aba Bordas", e o layout aprovado não tem
    abas. Nenhum aviso pode mandar a pessoa a uma aba."""
    for codigo, alerta in analise.ALERTAS.items():
        texto = f"{alerta.titulo} {alerta.mensagem}".lower()
        assert not re.search(r"\baba\b", texto), (codigo, alerta.mensagem)


# --- 21/10/2026: a terceira conferência do verificador (aba 4 na tela nova) -----
#
# Código antigo destes = o ramo em `de5b84e` (antes deste conserto).

def test_aviso_desenho_ou_escrita_diz_onde_fica_o_letra_e_traco():
    """Decisão do Samuel na `r14-aviso-marcar` (rodada 14 do layout): "C — Diz
    onde fica o “letra e traço”". Até 20/10 a frase era neutra (não dizia
    onde)."""
    assert analise.descrever(analise.DESENHO_OU_ESCRITA).mensagem == (
        "Não tenho certeza se esta página é desenho ou escrita. Confira: se for "
        "escrita, marque a área e escolha “letra e traço” no painel Propriedades.")
    # as outras frases de marcar dizem onde fica o que usar
    assert "painel Filtro da página" in analise.descrever(analise.TEXTO_FALHADO).mensagem
    assert "painel Propriedades" in analise.descrever(analise.FIGURA_ALEM_DA_GRAVURA).mensagem


# A tela de conferir do tests/test_para_revisar_na_tela.py (o mesmo livro de 4
# páginas em Preto e branco com "Só as letras"), com as fixtures que ela usa.
pytest.importorskip("PySide6")
from tests.test_para_revisar_na_tela import app, leitor_rapido, pasta, tela  # noqa: F401, E402


def test_bug_esta_bom_em_tudo_se_desfaz_com_um_ctrl_z(tela):
    """Bug do verificador (20/10/2026, aba 4): "está bom em tudo" com avisos de
    folha E de página gravava duas ações, e o Ctrl+Z precisava de dois toques."""
    projeto = tela.projeto
    projeto.folhas[0].alertas = [analise.RESOLUCAO_BAIXA]
    projeto.folhas[0].revisada = False
    projeto.paginas[1].alertas = [analise.DESENHO_APAGADO]
    projeto.paginas[1].revisada = False
    tela.atualizar()
    assert len(avisos.pendentes_do_livro(projeto)) >= 2
    tela._aceitar_tudo()
    assert avisos.pendentes_do_livro(projeto) == []
    tela.desfazer()                                   # UM Ctrl+Z
    pendentes = {(a.alvo, a.indice, a.codigo) for a in avisos.pendentes_do_livro(projeto)}
    assert (avisos.FOLHA, 0, analise.RESOLUCAO_BAIXA) in pendentes
    assert (avisos.PAGINA, 1, analise.DESENHO_APAGADO) in pendentes


def test_bug_rodape_com_duvida_acerta_quando_o_aviso_chega(tela):
    """Bug do verificador (20/10/2026, aba 4): o rodapé "N com dúvida" ficava um
    passo atrasado - o aviso que chegava com a medida por trás mudava o
    contador de cima, e o rodapé só acertava ao trocar de página."""
    projeto = tela.projeto
    for pagina in projeto.paginas:
        pagina.alertas, pagina.revisada = [], False
    tela.ir_para_pagina(0)
    tela.atualizar()
    assert "0 com dúvida" in tela.rotulo_do_livro.text()
    # chega um aviso na página da vez (o que _previa_chegou faz com a medida)
    projeto.paginas[0].alertas = [analise.DESENHO_APAGADO]
    tela._alertas_da_previa()
    assert "1 com dúvida" in tela.rotulo_do_livro.text(), tela.rotulo_do_livro.text()
