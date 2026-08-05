"""A pasta de teste: uma por filtro, com data e hora, e nome que o Windows aceita."""

import relatorio


def test_pasta_por_filtro_com_data_e_hora(tmp_path):
    pasta = relatorio.pasta_de_teste("orla do branco", "magico pro", raiz=tmp_path)

    assert pasta.parent.name == "MAGICO PRO"
    assert pasta.name.endswith(" - orla do branco")
    assert pasta.is_dir()


def test_pontuacao_no_assunto_nao_derruba_o_teste():
    """Um assunto com dois pontos estourava o mkdir no fim de uma bateria.

    O assunto e escrito a mao a cada teste, entao a pontuacao aparece; o estrago
    vinha depois de todo o trabalho pesado ja feito.
    """
    assert relatorio._nome_de_pasta("letra arredondada: raio da nitidez") == (
        "letra arredondada raio da nitidez")
    assert relatorio._nome_de_pasta('recorte "novo" / antigo') == "recorte novo antigo"
    assert relatorio._nome_de_pasta("   ") == "sem assunto"


def test_filtro_desconhecido_vai_para_outros(tmp_path):
    pasta = relatorio.pasta_de_teste("qualquer coisa", raiz=tmp_path)

    assert pasta.parent.name == "OUTROS"


def test_tabela_longa_nao_trava_o_pdf(tmp_path):
    """Relatorio com tabela longa tem de sair, e sair rapido.

    O laco de paginacao nao tinha teto. O Story do PyMuPDF devolve "ainda tem
    mais" sem consumir nada quando um elemento nao cabe, e a linha de base de
    04/08/2026 entrava num ciclo de tres paginas que se repetia sem fim: o
    programa ficava escrevendo paginas para sempre e deixava um .pdf de zero
    byte. Travar e pior que falhar.
    """
    linhas = "\n".join(
        f"| Livro de nome comprido numero {i} | {i} | Mágico pro | "
        f"o fundo escureceu: passou de {200 - i % 50} para {190 - i % 50} numa "
        f"escala em que 255 e branco |"
        for i in range(120)
    )
    texto = (
        "# Relatorio de teste\n\nUm paragrafo de abertura.\n\n"
        "## Paginas que sairam piores\n\n"
        "| Livro | Pagina | Filtro | O que piorou |\n|---|---|---|---|\n"
        + linhas + "\n"
    )

    caminho = relatorio.gravar_pdf(texto, tmp_path / "longo")

    assert caminho is not None and caminho.exists()
    assert caminho.stat().st_size > 0, "PDF de zero byte: a paginacao nao fechou"

    import fitz

    with fitz.open(caminho) as doc:
        assert 0 < doc.page_count <= relatorio.PAGINAS_MAXIMAS
        assert "Relatorio de teste" in doc[0].get_text()
