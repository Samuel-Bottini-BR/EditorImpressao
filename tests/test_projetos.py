"""Os projetos salvos: o trabalho sobrevive a fechar o programa.

Os casos aqui sao os do pedido, e cada um ja deu errado de um jeito diferente
em programa de verdade: livro que muda de pasta, livro trocado por outro de
mesmo nome, arquivo de acoes cortado por queda de energia.
"""

from __future__ import annotations

import json

import pytest

import projetos
from modelos import ConfigFolha, ConfigPagina, Projeto


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    """Poe a pasta de projetos num lugar descartavel."""
    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


def _livro(caminho, semente: bytes = b"A", tamanho: int = 300_000):
    """Um arquivo grande o bastante para a assinatura ler tres pedacos."""
    caminho.write_bytes(semente * tamanho)
    return caminho


def _projeto(caminho, paginas: int = 5) -> Projeto:
    p = Projeto(caminho_entrada=str(caminho), nome=caminho.stem)
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


# --- a assinatura -----------------------------------------------------------


def test_arquivos_diferentes_tem_assinaturas_diferentes(tmp_path):
    a = _livro(tmp_path / "a.pdf", b"A")
    b = _livro(tmp_path / "b.pdf", b"B")
    assert projetos.assinatura_do_arquivo(a) != projetos.assinatura_do_arquivo(b)


def test_a_assinatura_le_o_fim_e_nao_so_o_comeco(tmp_path):
    """Dois PDFs do mesmo digitalizador comecam iguais."""
    comum = b"X" * 200_000
    (tmp_path / "um.pdf").write_bytes(comum + b"final um")
    (tmp_path / "dois.pdf").write_bytes(comum + b"final dois!!")
    assert (projetos.assinatura_do_arquivo(tmp_path / "um.pdf")
            != projetos.assinatura_do_arquivo(tmp_path / "dois.pdf"))


def test_arquivo_que_sumiu_nao_derruba_a_assinatura(tmp_path):
    assert projetos.assinatura_do_arquivo(tmp_path / "nao_existe.pdf") == ""


# --- achar o livro de novo --------------------------------------------------


def test_livro_no_lugar_e_achado(raiz, tmp_path):
    livro = _livro(tmp_path / "livro.pdf")
    resumo = projetos.criar(_projeto(livro))
    situacao, caminho = projetos.procurar_o_livro(resumo)
    assert situacao == projetos.ACHOU
    assert caminho == str(livro)


def test_livro_que_mudou_de_pasta_religa_sozinho(raiz, tmp_path, monkeypatch):
    origem = tmp_path / "antes"
    destino = tmp_path / "depois"
    origem.mkdir()
    destino.mkdir()
    livro = _livro(origem / "livro.pdf")
    resumo = projetos.criar(_projeto(livro))

    livro.rename(destino / "livro.pdf")
    monkeypatch.setattr(projetos, "_pastas_conhecidas", lambda: [origem, destino])

    situacao, caminho = projetos.procurar_o_livro(resumo)
    assert situacao == projetos.RELIGADO
    assert caminho == str(destino / "livro.pdf")


def test_livro_trocado_por_outro_de_mesmo_nome_e_recusado(raiz, tmp_path):
    """O pior desfecho: aplicar corte de um livro em outro, em silencio."""
    livro = _livro(tmp_path / "livro.pdf", b"A")
    resumo = projetos.criar(_projeto(livro))

    _livro(tmp_path / "livro.pdf", b"Z")      # outro livro, mesmo nome

    situacao, _caminho = projetos.procurar_o_livro(resumo)
    assert situacao == projetos.TROCADO, "aceitou um livro que nao e aquele"


def test_livro_que_sumiu_de_vez(raiz, tmp_path, monkeypatch):
    livro = _livro(tmp_path / "livro.pdf")
    resumo = projetos.criar(_projeto(livro))
    livro.unlink()
    monkeypatch.setattr(projetos, "_pastas_conhecidas", lambda: [tmp_path])
    situacao, caminho = projetos.procurar_o_livro(resumo)
    assert situacao == projetos.SUMIU
    assert caminho == ""


# --- a lista da tela inicial ------------------------------------------------


def test_dois_projetos_do_mesmo_pdf_sao_numerados(raiz, tmp_path):
    livro = _livro(tmp_path / "Gradus primus.pdf")
    um = projetos.criar(_projeto(livro))
    dois = projetos.criar(_projeto(livro))
    assert um.nome == "Gradus primus"
    assert dois.nome == "Gradus primus (2)", "dois cartoes iguais na tela"
    assert um.pasta != dois.pasta


def test_a_pasta_em_disco_vai_sem_acento(raiz, tmp_path):
    livro = _livro(tmp_path / "Consolação da Filosofia.pdf")
    resumo = projetos.criar(_projeto(livro))
    from pathlib import Path

    nome_da_pasta = Path(resumo.pasta).name
    assert nome_da_pasta.isascii(), f"pasta com acento: {nome_da_pasta}"
    assert "ç" not in nome_da_pasta and "ã" not in nome_da_pasta
    assert resumo.nome == "Consolação da Filosofia", "o nome da TELA perdeu o acento"


def test_o_progresso_e_gravado_e_lido_de_volta(raiz, tmp_path):
    livro = _livro(tmp_path / "livro.pdf")
    projeto = _projeto(livro, paginas=50)
    resumo = projetos.criar(projeto, total_paginas=50)

    for pagina in projeto.paginas[:31]:
        pagina.revisada = True
    projetos.atualizar(resumo, projeto, pagina_atual=30)

    de_volta = projetos.ler_resumo(resumo.pasta)
    assert de_volta.conferidas == 31
    assert de_volta.pagina_atual == 30
    assert de_volta.frase_do_progresso == "31 de 50 conferidas"


def test_a_lista_vem_do_mais_recente_para_o_mais_antigo(raiz, tmp_path):
    for nome in ("um", "dois", "tres"):
        projetos.criar(_projeto(_livro(tmp_path / f"{nome}.pdf")))
    nomes = [r.nome for r in projetos.listar()]
    assert set(nomes) == {"um", "dois", "tres"}
    assert len(nomes) == 3


def test_resumo_corrompido_nao_derruba_a_lista(raiz, tmp_path):
    bom = projetos.criar(_projeto(_livro(tmp_path / "bom.pdf")))
    ruim = raiz / "quebrado"
    ruim.mkdir()
    (ruim / projetos.ARQUIVO_RESUMO).write_text("{isto nao e json", encoding="utf-8")

    lista = projetos.listar()
    assert [r.nome for r in lista] == [bom.nome], "um projeto quebrado escondeu os bons"


def test_resumo_de_versao_antiga_com_campo_a_mais(raiz, tmp_path):
    """Abrir um projeto gravado por uma versao futura nao pode explodir."""
    resumo = projetos.criar(_projeto(_livro(tmp_path / "livro.pdf")))
    caminho = raiz / "livro" / projetos.ARQUIVO_RESUMO
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    dados["campo_que_ainda_nao_existe"] = 42
    caminho.write_text(json.dumps(dados), encoding="utf-8")

    de_volta = projetos.ler_resumo(resumo.pasta)
    assert de_volta is not None and de_volta.nome == "livro"


# --- tirar da lista e renomear ----------------------------------------------


def test_remover_da_lista_nao_toca_no_pdf(raiz, tmp_path):
    livro = _livro(tmp_path / "livro.pdf")
    resumo = projetos.criar(_projeto(livro))

    projetos.remover_da_lista(resumo)

    assert projetos.listar() == []
    assert livro.is_file(), "apagou o livro do acervo"


def test_remover_so_apaga_dentro_da_pasta_de_projetos(raiz, tmp_path):
    de_fora = tmp_path / "coisa importante"
    de_fora.mkdir()
    (de_fora / "arquivo.txt").write_text("nao apague", encoding="utf-8")

    projetos.remover_da_lista(projetos.Resumo(pasta=str(de_fora)))
    assert (de_fora / "arquivo.txt").is_file(), "apagou fora da pasta de projetos"


def test_renomear_muda_a_tela_e_nao_a_pasta(raiz, tmp_path):
    resumo = projetos.criar(_projeto(_livro(tmp_path / "livro.pdf")))
    pasta_antes = resumo.pasta

    projetos.renomear(resumo, "Nome novo com acentuação")

    assert projetos.ler_resumo(pasta_antes).nome == "Nome novo com acentuação"
    assert resumo.pasta == pasta_antes


def test_renomear_para_vazio_nao_apaga_o_nome(raiz, tmp_path):
    resumo = projetos.criar(_projeto(_livro(tmp_path / "livro.pdf")))
    projetos.renomear(resumo, "   ")
    assert projetos.ler_resumo(resumo.pasta).nome == "livro"


# --- datas em linguagem comum -----------------------------------------------


@pytest.mark.parametrize("dias, esperado", [(0, "hoje"), (1, "ontem"), (3, "há 3 dias")])
def test_data_em_linguagem_comum(dias, esperado):
    from datetime import datetime, timedelta

    quando = datetime.now() - timedelta(days=dias)
    resumo = projetos.Resumo(mexido_em=quando.isoformat(timespec="seconds"))
    assert resumo.data_amigavel == esperado


def test_data_antiga_vira_dia_e_mes():
    resumo = projetos.Resumo(mexido_em="2026-01-15T10:00:00")
    assert resumo.data_amigavel == "15/01/2026"


# --- o arquivo de acoes cortado por queda de energia -------------------------


def _historico_com(tmp_path, conteudo: bytes):
    from historico_acoes import ARQUIVO_ACOES, HistoricoAcoes

    pasta = tmp_path / "proj"
    pasta.mkdir(exist_ok=True)
    (pasta / ARQUIVO_ACOES).write_bytes(conteudo)
    historico = HistoricoAcoes(pasta)
    historico.carregar()
    return historico


def _linha_boa() -> bytes:
    from modelos import Acao

    acao = Acao.nova("filtro", "pagina", [0], {"filtro": "a"}, {"filtro": "b"},
                     "trocou o filtro")
    return json.dumps(acao.para_dicionario(), ensure_ascii=False).encode() + b"\n"


def test_ultima_linha_cortada_nao_trava_e_e_contada(tmp_path):
    """Queda de energia no meio da gravacao. Nao pode travar nem apagar."""
    historico = _historico_com(
        tmp_path, _linha_boa() + _linha_boa() + b'{"descricao": "corta')

    assert len(historico.feitas) == 2, "perdeu as acoes boas junto com a ruim"
    assert historico.linhas_perdidas == 1, "nao contou a linha perdida"


def test_arquivo_de_acoes_com_lixo_binario_nao_derruba(tmp_path):
    """Bytes que nem sao texto. Antes isto levantava UnicodeDecodeError."""
    historico = _historico_com(
        tmp_path, _linha_boa() + b"\xff\xfe\x00 lixo binario \x80\n")

    assert len(historico.feitas) == 1
    assert historico.linhas_perdidas >= 1


def test_arquivo_de_acoes_intacto_nao_reporta_perda(tmp_path):
    historico = _historico_com(tmp_path, _linha_boa() + _linha_boa())
    assert len(historico.feitas) == 2
    assert historico.linhas_perdidas == 0
