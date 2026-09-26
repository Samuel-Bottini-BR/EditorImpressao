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


def test_pdf_leva_as_imagens_que_estao_ao_lado_do_relatorio(tmp_path):
    """Imagem citada no relatorio tem de sair DENTRO do PDF.

    Ate 25/09/2026 o Story do PyMuPDF nao sabia onde procurar os arquivos, e
    cada imagem virava o texto "[image]" no PDF (conferido no relatorio de
    17/09). A pagina de conferencia do item 0.4 depende disso: o PDF leva os
    paineis de antes/depois.
    """
    import cv2
    import fitz
    import numpy as np

    (tmp_path / "paineis").mkdir()
    cv2.imwrite(str(tmp_path / "paineis" / "a.jpg"), np.full((300, 200, 3), (40, 90, 200), np.uint8))
    texto = ("# Com imagem\n\n![o painel](paineis/a.jpg)\n\n"
             '<table><tr><td><img src="paineis/a.jpg" width="120"></td></tr></table>\n')

    arquivos = relatorio.gravar(texto, tmp_path / "com-imagem")

    with fitz.open(arquivos["pdf"]) as doc:
        assert sum(len(pagina.get_images()) for pagina in doc) >= 1
        assert "[image]" not in "".join(pagina.get_text() for pagina in doc)


def test_conferencia_grava_o_que_a_pessoa_disse(tmp_path, monkeypatch):
    """A tela de conferir tem de guardar o veredito de quem olhou.

    O gargalo do projeto nao e medir, e olhar - e ate aqui o que a pessoa dizia
    olhando a amostra se perdia, porque era anotado fora do projeto.
    """
    import numpy as np
    import cv2
    import relatorio
    import conferir

    amostras = tmp_path / "amostras"
    amostras.mkdir()
    for nome in ("uma.png", "outra.png"):
        cv2.imwrite(str(amostras / nome), np.full((40, 40, 3), 200, np.uint8))

    saida = tmp_path / "testes"
    monkeypatch.setattr(
        relatorio, "pasta_de_teste",
        lambda assunto, filtro="", raiz=None: _pasta(saida, assunto))

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    tela = conferir.Conferencia(
        sorted(amostras.iterdir()), "conferencia de teste")

    tela.caixa.setPlainText("o titulo saiu vermelho")
    tela.responder(False)
    tela.responder(True)          # a segunda fecha e grava

    assert len(tela.vereditos) == 2
    assert tela.vereditos[0]["veredito"] == "ERRADA"
    assert tela.vereditos[0]["o_que_disse"] == "o titulo saiu vermelho"
    assert tela.vereditos[1]["veredito"] == "certa"

    escrito = next(saida.rglob("o que foi conferido.md"))
    texto = escrito.read_text(encoding="utf-8")
    assert "o titulo saiu vermelho" in texto
    assert "1 certas, 1 erradas" in texto


def _pasta(raiz, assunto):
    destino = raiz / assunto
    destino.mkdir(parents=True, exist_ok=True)
    return destino
