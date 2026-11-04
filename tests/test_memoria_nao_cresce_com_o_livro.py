"""A memória do programa não cresce com o tamanho do livro ao gerar o PDF.

Bug (Central, pergunta 2-12, 28/10/2026; D-591 de 31/10/2026; pedido do
Samuel de 04/11/2026: "aquele problema de quando o pdf era grande demais, ou
faltava memoria e ele cancelava a geração do pdf ou o processamento foi
resolvido?"): processando o Rhetorica (446 folhas) o programa caiu com
"Este livro ficou grande demais para a memória do computador".

A causa, medida em 04/11/2026 (relatorios/memoria-pdf/): o PDF novo era
montado INTEIRO na memória (`fitz.open()` guarda cada imagem até o `save` do
fim). No Rhetorica, de fábrica e uma página por vez, o pico subiu de 1.665 MB
(30 folhas) para 1.891 MB (90 folhas), junto com o PDF (87 -> 301 MB); com
270 folhas a medida caiu por falta de memória. O mesmo nos cadernos
(core/cadernos.impor_pdf) e no livreto (core/impressao.montar_para_impressao,
que guardava as folhas montadas E as desenhadas como imagem).

O conserto (core/pdf_io.PDFQueVaiParaODisco): as páginas prontas vão para o
disco de tempos em tempos. O que se cobra aqui (CLAUDE.md §3: "O pico não
pode crescer com o tamanho do livro"):

    - livro sintético de N e de 3N páginas: o pico de memória do processo
      quase não muda (no código antigo, cresce com as páginas a mais) - no
      EscritorPDF, no processar, nos cadernos e no livreto;
    - o PDF que sai é o mesmo indo ou não ao disco no meio: mesmas páginas,
      mesmo tamanho de página, as imagens byte a byte e o desenho ponto a
      ponto (D-304: sem perda);
    - cancelar ou dar erro depois de ter ido ao disco: o PDF antigo de mesmo
      nome fica idêntico e nada sobra na pasta (bug de 05/10).

Os limites do teste são pequenos (alguns MB) para o livro sintético caber em
segundos; o de fábrica é core.pdf_io.LIMITE_DO_PDF_NA_MEMORIA.
"""

from __future__ import annotations

import gc
import hashlib
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
psutil = pytest.importorskip("psutil")

from core import cadernos, impressao, pdf_io, pipeline  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import EscritorPDF  # noqa: E402
from core.pipeline import Cancelou, processar  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

MB = 1024 * 1024
LIMITE_DO_TESTE = 4 * MB
# Cada página sintética pesa ~2,4 MB no PDF (ruído não se comprime): 2N
# páginas a mais no código antigo são ~48 MB a mais na memória. A folga
# cobre o vai-e-vem do Windows e do Python.
FOLGA_MB = 16


def _privado_mb() -> float:
    """A memória que o processo reservou para si (no Windows, "bytes
    privados"; fora dele, a residente)."""
    info = psutil.Process().memory_info()
    return getattr(info, "private", info.rss) / MB


def _ruido(semente: int, altura: int = 1000, largura: int = 800) -> np.ndarray:
    return np.random.default_rng(semente).integers(0, 256, (altura, largura, 3), dtype=np.uint8)


def _livro_de_ruido(caminho: Path, paginas: int) -> None:
    """Um PDF de `paginas` páginas de 800 x 1000 pt, cada uma uma imagem de
    ruído de 800 x 1000 pontos (a 72 DPI sai do mesmo tamanho)."""
    doc = fitz.open()
    for i in range(paginas):
        img = _ruido(1000 + i)
        dicionario, dados = pdf_io._imagem_comprimida(img)
        xref = doc.get_new_xref()
        doc.update_object(xref, dicionario)
        doc.update_stream(xref, dados, compress=0)
        doc.xref_set_key(xref, "Filter", "/FlateDecode")
        pagina = doc.new_page(width=800, height=1000)
        pagina.insert_image(fitz.Rect(0, 0, 800, 1000), xref=xref)
    doc.save(str(caminho))
    doc.close()


def _sem_paralelo(monkeypatch) -> None:
    """Uma página por vez (o pico com vários trabalhadores depende da
    memória livre na hora, não só do livro)."""
    monkeypatch.setattr(pipeline.nucleos, "quantos_trabalhadores", lambda *a, **k: 1)


def _limite(monkeypatch, valor: int) -> None:
    # raising=False: no código antigo o limite não existe (o teste roda lá
    # também, para provar que acusa o defeito - CLAUDE.md §4.7)
    monkeypatch.setattr(pdf_io, "LIMITE_DO_PDF_NA_MEMORIA", valor, raising=False)


def _crescimento(fazer) -> float:
    """Quanto o pico passa do começo, em MB. `fazer(anotar)` chama
    `anotar()` a cada página; uma linha de fundo também anota a cada 20 ms
    (pega a gravação do fim, que não chama ninguém)."""
    import threading

    gc.collect()
    base = _privado_mb()
    pico = [base]
    parar = threading.Event()

    def anotar(*_a, **_k) -> None:
        pico[0] = max(pico[0], _privado_mb())

    def vigiar() -> None:
        while not parar.wait(0.02):
            anotar()

    vigia = threading.Thread(target=vigiar, daemon=True)
    vigia.start()
    try:
        fazer(anotar)
    finally:
        parar.set()
        vigia.join()
    anotar()
    return pico[0] - base


# --- o pico não cresce com o livro ---------------------------------------------

def test_escritor_pdf_n_e_3n_paginas_mesmo_pico(tmp_path, monkeypatch):
    """EscritorPDF (o PDF do processar): 10 e 30 páginas, o mesmo pico."""
    _limite(monkeypatch, LIMITE_DO_TESTE)

    def escrever(n):
        def fazer(anotar):
            with EscritorPDF(tmp_path / f"e{n}.pdf") as escritor:
                for i in range(n):
                    escritor.escrever_imagem(_ruido(i), dpi=72)
                    anotar()
        return _crescimento(fazer)

    escrever(3)                                   # aquece (bibliotecas, caches)
    pequeno, grande = escrever(10), escrever(30)
    with fitz.open(str(tmp_path / "e30.pdf")) as doc:
        assert doc.page_count == 30
    assert grande - pequeno < FOLGA_MB, (
        f"o pico cresceu {grande - pequeno:.0f} MB com 20 páginas a mais "
        f"(10 páginas: +{pequeno:.0f} MB; 30: +{grande:.0f} MB)")


def _projeto(entrada: Path, saida: Path, paginas: int, montar_cadernos: bool = False) -> Projeto:
    """O livro de ruído pelo processar de verdade, com o filtro Original (a
    imagem passa como veio) - o jeito de tests/test_substituir_e_cancelar.py."""
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome="livro")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = False
    projeto.limpar = montar_cadernos      # sem isto + cadernos = "só cadernos"
    projeto.detectar_regioes = False
    projeto.montar_cadernos = montar_cadernos
    projeto.qualidade_dpi = 72
    projeto.filtro_padrao = ORIGINAL
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(paginas)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(paginas)]
    return projeto


def test_processar_n_e_3n_folhas_mesmo_pico(tmp_path, monkeypatch):
    """O "Confirmar e processar" (core/pipeline.processar): 10 e 30 folhas."""
    _limite(monkeypatch, LIMITE_DO_TESTE)
    _sem_paralelo(monkeypatch)

    def rodar(n):
        entrada = tmp_path / f"livro{n}.pdf"
        _livro_de_ruido(entrada, n)
        saida = tmp_path / f"saida{n}" / "pronto.pdf"

        def fazer(anotar):
            processar(_projeto(entrada, saida, n), progresso=anotar)
        cresceu = _crescimento(fazer)
        with fitz.open(str(saida)) as doc:
            assert doc.page_count == n
        return cresceu

    rodar(3)
    pequeno, grande = rodar(10), rodar(30)
    assert grande - pequeno < FOLGA_MB, (
        f"processar: o pico cresceu {grande - pequeno:.0f} MB com 20 folhas a mais")


def test_montar_cadernos_n_e_3n_paginas_mesmo_pico(tmp_path, monkeypatch):
    """"Montar cadernos" (core/cadernos.impor_pdf): 10 e 30 páginas."""
    _limite(monkeypatch, LIMITE_DO_TESTE)

    def rodar(n):
        entrada = tmp_path / f"livro{n}.pdf"
        _livro_de_ruido(entrada, n)

        def fazer(anotar):
            cadernos.impor_pdf(entrada, tmp_path / f"cadernos{n}.pdf", 8,
                               progresso=lambda *_a: anotar())
        return _crescimento(fazer)

    rodar(3)
    pequeno, grande = rodar(10), rodar(30)
    assert grande - pequeno < FOLGA_MB, (
        f"cadernos: o pico cresceu {grande - pequeno:.0f} MB com 20 páginas a mais")


def _opcoes_do_livreto() -> "impressao.OpcoesDeImpressao":
    """As opções de fábrica (livreto, "Imprimir como imagem"), com a imagem a
    72 DPI para o teste caber em segundos."""
    opcoes = impressao.OpcoesDeImpressao()
    opcoes.dpi_da_imagem = 72
    return opcoes


def test_livreto_n_e_3n_paginas_mesmo_pico(tmp_path, monkeypatch):
    """O livreto ("Montar para imprimir", core/impressao.montar_para_impressao,
    de fábrica com "Imprimir como imagem"): 16 e 48 páginas."""
    _limite(monkeypatch, LIMITE_DO_TESTE)

    def rodar(n):
        entrada = tmp_path / f"livro{n}.pdf"
        _livro_de_ruido(entrada, n)

        def fazer(anotar):
            impressao.montar_para_impressao(entrada, tmp_path / f"livreto{n}.pdf",
                                            _opcoes_do_livreto(),
                                            progresso=lambda *_a: anotar())
        return _crescimento(fazer)

    rodar(4)
    pequeno, grande = rodar(16), rodar(48)
    assert grande - pequeno < FOLGA_MB, (
        f"livreto: o pico cresceu {grande - pequeno:.0f} MB com 32 páginas a mais")


# --- o PDF é o mesmo, indo ou não ao disco no meio (D-304) -------------------------

def _retrato(caminho: Path) -> list:
    """Página por página: o tamanho, as imagens (bytes guardados) e o desenho
    a 36 DPI."""
    saida = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            imagens = [doc.xref_stream_raw(info[0]) for info in pagina.get_images(full=True)]
            desenho = pagina.get_pixmap(dpi=36).samples
            saida.append((tuple(pagina.rect), [hashlib.sha256(i).hexdigest() for i in imagens],
                          hashlib.sha256(desenho).hexdigest()))
    return saida


def test_escritor_o_pdf_e_o_mesmo_indo_ao_disco(tmp_path, monkeypatch):
    imagens = [_ruido(i, 300, 200) for i in range(5)] + [np.full((300, 200, 3), 255, np.uint8)]

    def gravar(nome, limite):
        _limite(monkeypatch, limite)
        with EscritorPDF(tmp_path / nome) as escritor:
            for i, img in enumerate(imagens):
                escritor.escrever_imagem(img, dpi=150, monocromatico=(i == 2))
            idas = escritor._montagem.idas_ao_disco
        return idas

    assert gravar("sem.pdf", 10**12) == 0
    assert gravar("com.pdf", 1) >= 5               # vai ao disco a cada página
    assert _retrato(tmp_path / "sem.pdf") == _retrato(tmp_path / "com.pdf")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["com.pdf", "sem.pdf"]


def test_cadernos_e_livreto_o_pdf_e_o_mesmo_indo_ao_disco(tmp_path, monkeypatch):
    entrada = tmp_path / "livro.pdf"
    _livro_de_ruido(entrada, 10)
    for limite, nome in ((10**12, "sem"), (1, "com")):
        _limite(monkeypatch, limite)
        cadernos.impor_pdf(entrada, tmp_path / f"cadernos-{nome}.pdf", 8)
        impressao.montar_para_impressao(entrada, tmp_path / f"livreto-{nome}.pdf",
                                        _opcoes_do_livreto())
        sem_imagem = _opcoes_do_livreto()
        sem_imagem.como_imagem = False
        impressao.montar_para_impressao(entrada, tmp_path / f"montado-{nome}.pdf", sem_imagem)
    for tipo in ("cadernos", "livreto", "montado"):
        assert _retrato(tmp_path / f"{tipo}-sem.pdf") == _retrato(tmp_path / f"{tipo}-com.pdf"), tipo
    assert not [p.name for p in tmp_path.iterdir() if p.name.startswith("~")]


# --- cancelar e erro depois de ir ao disco: o antigo fica (bug de 05/10) -----------

@pytest.fixture
def livro_e_antigo(tmp_path, monkeypatch):
    _limite(monkeypatch, 1)                      # vai ao disco a cada página
    _sem_paralelo(monkeypatch)
    entrada = tmp_path / "livro.pdf"
    _livro_de_ruido(entrada, 6)
    pasta = tmp_path / "saida"
    pasta.mkdir()
    saida = pasta / "pronto.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((40, 60), "o antigo")
    doc.save(str(saida))
    doc.close()
    return entrada, pasta, saida, saida.read_bytes()


@pytest.mark.parametrize("montar_cadernos", [False, True])
def test_cancelar_depois_de_ir_ao_disco_mantem_o_antigo(livro_e_antigo, montar_cadernos):
    entrada, pasta, saida, antigo = livro_e_antigo
    perguntas = {"n": 0}

    def cancelado():
        perguntas["n"] += 1
        return perguntas["n"] > 4

    with pytest.raises(Cancelou):
        processar(_projeto(entrada, saida, 6, montar_cadernos), cancelado=cancelado)
    assert saida.read_bytes() == antigo
    assert sorted(p.name for p in pasta.iterdir()) == ["pronto.pdf"]


def test_falta_de_memoria_depois_de_ir_ao_disco_mantem_o_antigo(livro_e_antigo, monkeypatch):
    entrada, pasta, saida, antigo = livro_e_antigo
    original = pipeline.compor_na_folha
    vezes = {"n": 0}

    def falha_na_quinta(*a, **k):
        vezes["n"] += 1
        if vezes["n"] == 5:
            raise MemoryError("de mentira")
        return original(*a, **k)

    monkeypatch.setattr(pipeline, "compor_na_folha", falha_na_quinta)
    with pytest.raises(MemoryError):
        processar(_projeto(entrada, saida, 6))
    assert saida.read_bytes() == antigo
    assert sorted(p.name for p in pasta.iterdir()) == ["pronto.pdf"]


def test_terminar_depois_de_ir_ao_disco_troca_e_nao_sobra_nada(livro_e_antigo):
    entrada, pasta, saida, antigo = livro_e_antigo
    processar(_projeto(entrada, saida, 6))
    with fitz.open(str(saida)) as doc:
        assert doc.page_count == 6
    assert sorted(p.name for p in pasta.iterdir()) == ["pronto.pdf"]


def test_sobra_de_queda_do_arquivo_ao_lado_e_apagada(tmp_path):
    """O arquivo ao lado de uma queda anterior (mesmo nome exato) sai ao
    começar; um parecido de outro livro fica."""
    destino = tmp_path / "~pronto.pdf.parcial"
    sobra = tmp_path / "~pronto.pdf.parcial.paginas"
    outro = tmp_path / "~outro.pdf.parcial.paginas"
    sobra.write_bytes(b"%PDF-1.7 de uma queda")
    outro.write_bytes(b"%PDF-1.7 de outro livro")
    with EscritorPDF(destino) as escritor:
        escritor.escrever_imagem(_ruido(1, 100, 80), dpi=72)
    assert not sobra.exists()
    assert outro.exists()
