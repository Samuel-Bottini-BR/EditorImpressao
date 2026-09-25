"""Fase 3b do plano "corrigir bugs do teste do Boécio": faltava granularidade
de aplicação para a marcação (aba Marcar) - existia "usar em todas" para
corte, recorte/bordas e filtro, mas não para o resultado da detecção
automática de regiões.

Interpretação adotada (documentada no relatório para o Samuel confirmar): o
"resultado" copiado é a MARCAÇÃO já computada na página atual (detectada +
qualquer correção manual), igual ao padrão já usado por
`_recorte_em_todas`/`_filtro_em_todas` - copia um VALOR já decidido, não roda
`detectar()` de novo em cada página (isso rasterizaria e processaria o livro
inteiro de forma síncrona na interface, o que a regra do projeto "nenhum
processamento pesado trava a interface" não permite sem uma tarefa em
segundo plano própria - fora do escopo desta entrega).

Roda com um PDF de verdade (fitz) e `GerenciadorPrevias` real, mesmo padrão
de `tests/test_salva_sozinho.py`, porque `_registrar` (o mecanismo que grava
no histórico) chama `atualizar()` no final, que depende da tela estar
carregada de verdade.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.selecao import GRAVURA, RETANGULO, Regiao, Selecao  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(5):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"pagina {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto(caminho, n: int = 5) -> Projeto:
    p = Projeto(caminho_entrada=str(caminho), nome="x")
    p.limpar = True
    p.detectar_regioes = True   # obrigatorio para a aba Marcar existir
    p.dividir_folhas = False
    p.endireitar = False
    p.cortar_bordas = False
    p.folhas = [ConfigFolha(indice=i) for i in range(n)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(n)]
    return p


@pytest.fixture
def conferir(app, livro):
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(livro)
    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    yield tela
    previas.parar()


def _selecao_com_uma_gravura() -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                         pontos=[(0.1, 0.1), (0.4, 0.4)]))
    return s


# --- usar em todas -----------------------------------------------------------

def test_usar_em_todas_copia_a_marcacao_para_as_outras_paginas(conferir):
    pagina0 = conferir.projeto.paginas[0]
    pagina0.guardar_selecao(_selecao_com_uma_gravura())

    conferir._marcacao_em_todas()

    for pagina in conferir.projeto.paginas:
        assert pagina.selecao == pagina0.selecao
        assert len(pagina.obter_selecao()) == 1


def test_usar_em_todas_e_uma_acao_so_no_desfazer(conferir):
    pagina0 = conferir.projeto.paginas[0]
    pagina2 = conferir.projeto.paginas[2]
    pagina2.guardar_selecao(_selecao_com_uma_gravura())  # valor diferente antes

    pagina0.guardar_selecao(_selecao_com_uma_gravura())
    conferir._marcacao_em_todas()
    assert all(p.selecao == pagina0.selecao for p in conferir.projeto.paginas)

    conferir.acoes.desfazer(conferir.projeto)
    assert conferir.projeto.paginas[2].selecao == pagina2.selecao, (
        "cada pagina tem que voltar para o SEU valor de antes")
    assert conferir.projeto.paginas[1].selecao == []


def test_usar_em_todas_sem_nada_marcado_nao_faz_nada(conferir):
    """Copiar uma marcacao VAZIA para todas apagaria o trabalho de outras
    paginas sem querer - guarda contra esse caso."""
    pagina1 = conferir.projeto.paginas[1]
    pagina1.guardar_selecao(_selecao_com_uma_gravura())

    assert conferir.projeto.paginas[0].selecao == []
    conferir._marcacao_em_todas()

    assert conferir.projeto.paginas[1].selecao != [], (
        "marcacao vazia da pagina atual nao pode apagar o que a pagina 1 tinha")


# --- só nas próximas ----------------------------------------------------------

def test_nas_proximas_nao_mexe_nas_paginas_anteriores(conferir):
    conferir.indice_pagina = 2
    pagina2 = conferir.projeto.paginas[2]
    pagina2.guardar_selecao(_selecao_com_uma_gravura())

    conferir._marcacao_nas_proximas()

    assert conferir.projeto.paginas[0].selecao == []
    assert conferir.projeto.paginas[1].selecao == []
    for pagina in conferir.projeto.paginas[2:]:
        assert pagina.selecao == pagina2.selecao
