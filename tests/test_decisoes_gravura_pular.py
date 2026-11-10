"""D-661 (Samuel, 09/11/2026): o "Pular" guarda a gravura achada no Preto e branco à mão.

O defeito (prova da pergunta 2 da D-659, 09/11/2026, relatorios/gravura-a-mao/imagens/q2-*.jpg):
página 8 do *Na escola de Jesus* em Preto e branco escolhido à mão, com "Respeitar as gravuras
achadas": a gravura sai certa (q2-a). Depois o Automático só com "Limpar a folha" e, no aviso das
páginas mexidas (D-004), "Pular": a gravura voltava a manchas pretas (q2-d), porque a procura da
D-659 só valia com "Limpar a folha" desligado.

Palavras dele: pergunta "Posso fazer esse conserto do 'Pular'?" (o programa guarda no arquivo do
livro que a gravura daquela página foi achada no Preto e branco à mão; livros antigos abrem
igual) → "1- pode". Na prática: com "Pular", a página sai como ele deixou, usando a gravura já
achada, sem procurar de novo e sem procurar nas outras; "Rodar nelas também" passa por cima.

O que estas provas guardam (sem janela; a mesma conta do "Rodar", core.automatico.rodar, e do
desenho da tela e do PDF, core.pipeline.renderizar_pagina):
  1. "Pular": a página sai igual, byte a byte, à de antes do Automático; nenhuma procura nova
     (nem nela, nem nas outras, nem no PDF);
  2. "Rodar nelas também": passa por cima (sai toda em preto e branco, como antes) e o campo
     novo volta a falso;
  3. o campo novo vai para o projeto.json e volta; projeto antigo (sem o campo) abre com ele
     falso e sai igual ao código de antes;
  4. o campo não passa para a página posta à mão nem para as metades de uma folha partida.

O detector é trocado por um que devolve a marcação do livro de teste e anota a página procurada
(como em tests/test_decisoes_gravura_a_mao.py). A prova no livro dele (q2-d igual à q2-a, ponto
por ponto) está em relatorios/gravura-a-mao/ (prova_pergunta2.py). Reversão (§4.7): no código de
antes deste conserto as provas 1, 2 (o campo) e 3 falham
(relatorios/gravura-a-mao/reversao-d661.txt).
"""

from __future__ import annotations

import copy
import threading

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests import test_decisoes_respeitar_gravuras as R  # noqa: E402

DPI_DA_PROVA = 110


@pytest.fixture
def procuradas(monkeypatch):
    """O detector de mentira: devolve a marcação do livro de teste e anota a página procurada."""
    from core import detectar_regioes, pipeline

    lista: list = []
    local = threading.local()
    original = pipeline.garantir_selecao

    def garantir(projeto, pagina, *args, **kwargs):
        pilha = getattr(local, "pilha", None)
        if pilha is None:
            pilha = local.pilha = []
        pilha.append(pagina.indice)
        try:
            return original(projeto, pagina, *args, **kwargs)
        finally:
            pilha.pop()

    def detectar(img, **kwargs):
        pilha = getattr(local, "pilha", None) or [None]
        lista.append(pilha[-1])
        return R._marcacao_da_maquina()

    monkeypatch.setattr(pipeline, "garantir_selecao", garantir)
    monkeypatch.setattr(detectar_regioes, "detectar", detectar)
    return lista


class _Livro:
    """Um livro novo (core.automatico.livro_leve, como a janela abre), com o documento aberto."""

    def __init__(self, tmp_path, folhas: int = 3):
        from core import automatico
        from core.pdf_io import abrir_pdf, info_paginas
        from modelos import Projeto

        caminho = R._pdf(tmp_path / "livro.pdf", folhas)
        self.projeto = Projeto(caminho_entrada=caminho, nome="livro",
                               caminho_saida=str(tmp_path / "saida.pdf"))
        self.doc = abrir_pdf(caminho)
        automatico.livro_leve(self.projeto,
                              [(i.largura_pt, i.altura_pt) for i in info_paginas(self.doc)])

    def a_mao(self, indice: int = 0):
        """O clique no Preto e branco do painel (o filtro e a marca FILTRO), "Respeitar" de
        fábrica."""
        from core import etapas

        pagina = self.projeto.paginas[indice]
        pagina.filtro = PRETO_E_BRANCO
        etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)
        return pagina

    def desenho(self, indice: int, dpi: int = DPI_DA_PROVA, projeto=None) -> np.ndarray:
        from core.pipeline import renderizar_pagina

        projeto = projeto or self.projeto
        img, _ = renderizar_pagina(self.doc, projeto, projeto.paginas[indice], dpi=dpi)
        return R._bgr(img)

    def automatico(self, pular: bool):
        """O Automático do print 02: só "Limpar a folha" (Preto e branco), as outras etapas
        desmarcadas; `pular` é a resposta à pergunta das páginas mexidas (D-004)."""
        from core import automatico as A

        pedido = A.Pedido(etapas=[A.LIMPAR], opcoes={"filtro_padrao": PRETO_E_BRANCO},
                          pular_mexidas=pular,
                          desmarcadas=[e for e in A.ETAPAS if e != A.LIMPAR])
        assert [p + 1 for p in A.paginas_mexidas(self.projeto, pedido)] == [1], \
            "o Automático devia perguntar pela página mexida"
        return A.rodar(self.projeto, pedido)

    def fechar(self):
        self.doc.close()


@pytest.fixture
def livro(tmp_path):
    livro = _Livro(tmp_path)
    yield livro
    livro.fechar()


def _gravura_respeitada(img: np.ndarray) -> bool:
    return R._colorido(R._miolo_da_iluminura(img)) > 0.5


# --- 1. "Pular" ------------------------------------------------------------------------------

def test_d661_pular_a_pagina_sai_como_ele_deixou_sem_procurar_de_novo(livro, procuradas):
    """D-661: "Pular" → a página em Preto e branco à mão sai igual, byte a byte, à de antes do
    Automático (a gravura achada vale), na prévia e no tamanho do PDF; nenhuma procura nova, nem
    nela nem nas outras páginas (que também são desenhadas). Defeito de 09/11: a gravura voltava a
    manchas (q2-d)."""
    from core import etapas

    pagina = livro.a_mao(0)
    antes = livro.desenho(0)
    antes_pdf = livro.desenho(0, dpi=int(livro.projeto.qualidade_dpi))
    assert _gravura_respeitada(antes), "a prova não vale: a gravura não foi respeitada à mão"
    assert procuradas and set(procuradas) == {0}

    livro.automatico(pular=True)
    assert livro.projeto.limpar and etapas.filtro_a_mao(livro.projeto, pagina)
    procuradas.clear()
    depois = livro.desenho(0)
    depois_pdf = livro.desenho(0, dpi=int(livro.projeto.qualidade_dpi))
    for indice in (1, 2):
        livro.desenho(indice)
    assert np.array_equal(depois, antes), "com 'Pular' a página mudou (a gravura voltou a manchas)"
    assert np.array_equal(depois_pdf, antes_pdf)
    assert procuradas == [], f"procurou de novo: {procuradas}"
    assert getattr(pagina, "gravura_achada_a_mao", None) is True, "o campo novo não foi gravado"


def test_d661_pular_o_pdf_sai_como_a_tela_e_nao_procura(livro, procuradas, tmp_path):
    """D-473: com "Pular", o PDF gerado (core.pipeline.processar) traz a página com a gravura
    respeitada, e gerar o PDF não procura em página nenhuma."""
    livro.a_mao(0)
    livro.desenho(0, dpi=int(livro.projeto.qualidade_dpi))     # a definitiva, como o acerto por trás
    livro.automatico(pular=True)
    procuradas.clear()
    paginas = R._gerar(livro.projeto, tmp_path, "pulou", 72)
    assert _gravura_respeitada(paginas[0]), "no PDF a gravura voltou a manchas"
    assert procuradas == [], f"o PDF procurou: {procuradas}"


# --- 2. "Rodar nelas também" ---------------------------------------------------------------------

def test_d661_rodar_nelas_tambem_passa_por_cima(livro, procuradas):
    """"Rodar nelas também" passa por cima, como o aviso diz: a página sai toda em preto e branco
    (sem "Gravuras e fotos", D-589), o campo novo volta a falso e nada é procurado."""
    pagina = livro.a_mao(0)
    livro.desenho(0)
    resultado = livro.automatico(pular=False)
    procuradas.clear()
    depois = livro.desenho(0)
    assert R._colorido(depois) == 0.0, "a página devia sair toda em preto e branco"
    assert procuradas == []
    assert getattr(pagina, "gravura_achada_a_mao", None) is False,         "o 'Rodar nelas também' não passou por cima do campo"
    assert resultado is not None


# --- 3. o campo no projeto.json; projeto antigo ---------------------------------------------------

def test_d661_o_campo_vai_e_volta_do_projeto_json(livro, procuradas):
    """O campo novo vai para o projeto.json e volta (o "Pular" continua valendo ao abrir de
    novo)."""
    from modelos import Projeto

    livro.a_mao(0)
    livro.desenho(0)
    livro.automatico(pular=True)
    antes = livro.desenho(0)
    dados = livro.projeto.para_dicionario()
    assert dados["paginas"][0]["gravura_achada_a_mao"] is True
    assert dados["paginas"][1]["gravura_achada_a_mao"] is False
    aberto = Projeto.de_dicionario(copy.deepcopy(dados))
    assert aberto.paginas[0].gravura_achada_a_mao is True
    procuradas.clear()
    assert np.array_equal(livro.desenho(0, projeto=aberto), antes)
    assert procuradas == []


def test_d661_projeto_antigo_abre_sem_o_campo_e_sai_igual(livro, procuradas, monkeypatch):
    """Projeto gravado antes do campo (a chave não existe): abre com ele falso e cada página sai
    igual, byte a byte, ao código de antes (core/etapas.respeitar_procura sem a D-661)."""
    from core import etapas
    from modelos import Projeto

    livro.a_mao(0)
    livro.desenho(0)
    livro.automatico(pular=True)
    dados = livro.projeto.para_dicionario()
    for pagina in dados["paginas"]:
        pagina.pop("gravura_achada_a_mao")
    antigo = Projeto.de_dicionario(dados)
    assert all(p.gravura_achada_a_mao is False for p in antigo.paginas)
    agora = [livro.desenho(i, projeto=antigo) for i in range(3)]

    def respeitar_de_antes(projeto, pagina=None):
        """core/etapas.respeitar_procura antes da D-661 (só sem "Limpar a folha")."""
        if pagina is None or etapas.limpa_sozinho(projeto, pagina) \
                or not etapas.filtro_a_mao(projeto, pagina):
            return False
        if not bool(getattr(pagina, "respeitar_gravuras_achadas", True)):
            return False
        return getattr(pagina, "filtro", None) == PRETO_E_BRANCO

    monkeypatch.setattr(etapas, "respeitar_procura", respeitar_de_antes)
    for i in range(3):
        assert np.array_equal(livro.desenho(i, projeto=antigo), agora[i]), f"página {i + 1}"


# --- 4. não passa para a página posta nem para as metades ---------------------------------------

def test_d661_o_campo_nao_passa_para_a_pagina_posta_nem_para_as_metades():
    """Como gravura_feita_com: o campo é da marcação daquela página. A página posta à mão (core/
    paginas_em_branco._NAO_HERDA) e as metades de uma folha partida (core/dividir_a_mao.
    LIMPAR_AO_PARTIR) nascem com ele falso."""
    from core import dividir_a_mao, paginas_em_branco
    from modelos import ConfigPagina

    assert "gravura_achada_a_mao" in paginas_em_branco._NAO_HERDA
    assert dividir_a_mao.LIMPAR_AO_PARTIR["gravura_achada_a_mao"] is False
    assert ConfigPagina(indice=0, folha=0).gravura_achada_a_mao is False


def test_d661_sem_o_pular_nada_muda_na_conta_de_quem_procura(livro):
    """Com "Limpar a folha" ligado, a página sem o campo (ou sem a marca FILTRO) responde como
    antes; e sem "Limpar a folha" nada muda (a D-659)."""
    from core import etapas

    pagina = livro.a_mao(0)
    assert etapas.respeitar_procura(livro.projeto, pagina)            # D-659, sem o Limpar
    livro.projeto.limpar = True
    assert not etapas.respeitar_procura(livro.projeto, pagina), "sem o campo, como antes"
    pagina.gravura_achada_a_mao = True
    assert etapas.respeitar_procura(livro.projeto, pagina)            # D-661
    pagina.mexida_a_mao = [m for m in pagina.mexida_a_mao if m != etapas.FILTRO]
    assert not etapas.respeitar_procura(livro.projeto, pagina), "sem a marca FILTRO, não vale"
    pagina.mexida_a_mao = [etapas.FILTRO]
    pagina.respeitar_gravuras_achadas = False
    assert not etapas.respeitar_procura(livro.projeto, pagina), "com a 'Respeitar' desmarcada, não"
    pagina.respeitar_gravuras_achadas = True
    pagina.filtro = ORIGINAL
    assert not etapas.respeitar_procura(livro.projeto, pagina), "fora do Preto e branco, não"
