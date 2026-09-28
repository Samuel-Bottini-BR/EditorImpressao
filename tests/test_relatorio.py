"""relatorio.py: a pasta de teste (uma por filtro, com data e hora, e nome que
o Windows aceita), o nome dos tres arquivos que gravar() escreve e o PDF."""

import pytest

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


def test_gravar_mantem_o_nome_inteiro_mesmo_com_ponto(tmp_path):
    """Bug de 25/09/2026: o destino "conferencia-6.7" gravava
    "conferencia-6.md" - o gravar tratava o ".7" como extensao e o cortava.
    O nome dado tem de ficar inteiro nos tres arquivos."""
    arquivos = relatorio.gravar("# Titulo\n\nTexto.", tmp_path / "conferencia-6.7")

    assert arquivos["md"] == tmp_path / "conferencia-6.7.md"
    assert arquivos["html"] == tmp_path / "conferencia-6.7.html"
    assert arquivos["pdf"] == tmp_path / "conferencia-6.7.pdf"
    assert {f.name for f in tmp_path.iterdir()} == {
        "conferencia-6.7.md", "conferencia-6.7.html", "conferencia-6.7.pdf"}


@pytest.mark.parametrize("extensao", [".md", ".html", ".pdf", ".MD"])
def test_gravar_aceita_destino_com_a_extensao_de_um_dos_tres(tmp_path, extensao):
    """Quem ja chama com extensao continua funcionando: o avaliar.py passa o
    proprio .md, e o `python relatorio.py x.md` tambem. So a extensao de um
    dos tres formatos sai; o resto do nome (inclusive o ".7") fica."""
    arquivos = relatorio.gravar("# Titulo", tmp_path / f"relatorio-6.7{extensao}")

    assert arquivos["md"] == tmp_path / "relatorio-6.7.md"
    assert arquivos["html"] == tmp_path / "relatorio-6.7.html"
    assert arquivos["pdf"] == tmp_path / "relatorio-6.7.pdf"


def test_gravar_pdf_mantem_o_nome_inteiro(tmp_path):
    """O gravar_pdf tem o mesmo cuidado: e chamado sozinho tambem (pelo
    converter_pasta, com o .md, e pelos testes)."""
    assert relatorio.gravar_pdf("# T", tmp_path / "velocidade-PC.local") == (
        tmp_path / "velocidade-PC.local.pdf")
    assert relatorio.gravar_pdf("# T", tmp_path / "outro.md") == tmp_path / "outro.pdf"


# O cinza do fundo do cabecalho da tabela no PDF (#f2f0ed), como o PyMuPDF o
# devolve em get_drawings (0 a 1, tres casas).
CINZA_DO_CABECALHO = (0.949, 0.941, 0.929)


def _fundos_cinza(pagina) -> list:
    return [d["rect"] for d in pagina.get_drawings()
            if d.get("fill") is not None
            and tuple(round(c, 3) for c in d["fill"]) == CINZA_DO_CABECALHO]


def test_fundo_do_cabecalho_da_tabela_nao_se_repete_nas_outras_paginas(tmp_path):
    """Bug de 25/09/2026: faixas cinzas atravessando o texto do PDF.

    Eram o fundo do cabecalho das tabelas (th) da PRIMEIRA pagina, redesenhado
    pelo Story do PyMuPDF em todas as paginas seguintes, na mesma altura, com
    a altura so do enchimento (6 pt). Acontece com 'border-collapse:
    collapse' na tabela, e so com ele (medido em 28/09). Aqui a tabela esta
    na primeira pagina e as seguintes nao tem tabela nem codigo: nenhum
    cinza pode aparecer nelas."""
    import fitz

    enchimento = "\n\n".join(f"Paragrafo {i} de enchimento, com texto comprido o "
                             f"bastante para ocupar a linha." for i in range(140))
    texto = ("# Com tabela\n\n| O que | Quanto |\n|---|---|\n| Abrir | 45 s |\n"
             "| Trocar | 2 s |\n\n" + enchimento)

    caminho = relatorio.gravar_pdf(texto, tmp_path / "tabela")

    with fitz.open(caminho) as doc:
        assert doc.page_count >= 3
        assert _fundos_cinza(doc[0]), "o cabecalho da tabela perdeu o fundo"
        for pagina in list(doc)[1:]:
            assert _fundos_cinza(pagina) == [], (
                f"faixa cinza na pagina {pagina.number + 1}, que nao tem tabela")


def test_rodape_nunca_fica_sozinho_numa_pagina(tmp_path):
    """Bug de 25/09/2026: uma ultima pagina so com o rodape ("Editor de
    Impressao - gerado em ...").

    O rodape era parte do texto corrido: quando o texto acabava perto do pe
    da folha, ele nao cabia e ia sozinho para uma folha nova (com o estilo
    antigo, aos 32 e aos 67 paragrafos deste teste). Agora ele vai na margem
    de baixo da ultima pagina, fora do texto. Varre os tamanhos em volta dos
    dois casos: toda pagina tem texto alem do rodape, e o rodape sai uma vez
    so, na ultima."""
    import fitz

    for n in range(25, 75):
        texto = "# Titulo\n\n" + "\n\n".join(
            f"Paragrafo {i} com um texto curto." for i in range(n))
        caminho = relatorio.gravar_pdf(texto, tmp_path / f"rodape-{n}")

        with fitz.open(caminho) as doc:
            paginas = [pagina.get_text() for pagina in doc]
        com_rodape = [i for i, t in enumerate(paginas) if "gerado em" in t]
        assert com_rodape == [len(paginas) - 1], f"{n} paragrafos: rodape em {com_rodape}"
        for i, t in enumerate(paginas):
            sem_rodape = "\n".join(linha for linha in t.splitlines() if "gerado em" not in linha)
            assert "Paragrafo" in sem_rodape or "Titulo" in sem_rodape, (
                f"{n} paragrafos: a pagina {i + 1} so tem o rodape")


def test_a_biblioteca_markdown_esta_no_requirements():
    """Bug de 25/09/2026: o relatorio.py usa a biblioteca markdown para o
    .html e o .pdf, e ela nao estava no requirements.txt. Numa instalacao do
    zero, o relatorio caia na conversao simples (_conversao_simples) e
    perdia as tabelas e as imagens, sem avisar."""
    from pathlib import Path

    requisitos = Path(relatorio.__file__).with_name("requirements.txt").read_text(
        encoding="utf-8")
    nomes = [linha.split(">=")[0].split("==")[0].strip().lower()
             for linha in requisitos.splitlines()
             if linha.strip() and not linha.lstrip().startswith("#")]

    assert "markdown" in nomes


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
