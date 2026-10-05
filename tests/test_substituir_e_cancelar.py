"""Substituir o PDF antigo e depois cancelar (ou dar erro) nao pode apagar o antigo.

Bug GRAVE da Lista de bugs do plano (05/10/2026, confirmado na janela real
pelo verificador, relatorios/conferir/consertos-janela-2026-10-05/verificador/;
o Samuel mandou consertar na conferencia 11: "CANCELAR (a) Consertar ja").

O defeito: sem "Montar cadernos" (o normal), core/pipeline.py::processar
gravava direto no arquivo final. Se o Kaique escolhia "substituir o antigo" e
depois apertava "cancelar", o EscritorPDF gravava por cima do antigo as
paginas feitas ate ali e o cancelamento apagava esse arquivo: o PDF antigo
sumia, sem aviso. Erro no meio (disco cheio, por exemplo) deixava no lugar do
antigo um PDF pela metade.

O conserto: o PDF novo e gravado num arquivo a parte, na MESMA pasta
(`~<nome>.parcial`), e so troca de lugar com o antigo quando tudo terminou
(os.replace, que no mesmo disco e uma troca so). Cancelou ou deu erro: apaga
so o arquivo a parte. O que se cobra aqui, com o conteudo do antigo conferido
por sha256:

    - cancelar com "substituir": o antigo fica identico; nada sobra na pasta;
    - terminar: o antigo e trocado pelo novo; nada sobra na pasta;
    - erro no meio (uma pagina que falha; disco cheio na hora de gravar): o
      antigo fica identico; nada sobra;
    - o mesmo com "Montar cadernos" (e o temporario da imposicao some);
    - o mesmo no caminho rapido "so cadernos";
    - sobra de arquivo a parte de uma vez que o programa caiu: e apagada;
    - o antigo aberto em outro programa (no Windows a troca falha): aviso em
      portugues, o antigo fica, e o PDF novo NAO se perde (vai para
      "<nome> (2).pdf", e o aviso diz o nome).

Tudo em pasta temporaria do pytest; nada de gabarito nem da pasta real.
"""

from __future__ import annotations

import errno
import hashlib
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import ErroPDF  # noqa: E402
from core.pipeline import Cancelou, processar  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

PAGINAS = 4


def _sha(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def _pdf_de_entrada(caminho: Path, paginas: int = PAGINAS) -> None:
    """Um livro pequeno: `paginas` folhas de cor solida (desenho, nao texto)."""
    import cv2

    doc = fitz.open()
    for i in range(paginas):
        arte = np.full((300, 200, 3), (40 + 40 * i, 120, 200), np.uint8)
        ok, buffer = cv2.imencode(".png", arte)
        assert ok
        pagina = doc.new_page(width=200, height=300)
        pagina.insert_image(fitz.Rect(0, 0, 200, 300), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()


def _pdf_antigo(caminho: Path) -> str:
    """O PDF "antigo" que o Kaique escolheu substituir: 7 paginas, para nao
    se confundir com o novo (4). Devolve o sha256."""
    doc = fitz.open()
    for _ in range(7):
        doc.new_page(width=100, height=100).insert_text((10, 50), "antigo")
    doc.save(str(caminho))
    doc.close()
    return _sha(caminho)


def _projeto(entrada: Path, saida: Path, montar_cadernos: bool = False) -> Projeto:
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome="livro")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = False
    # "Limpar" ligado (com o filtro Original, que nao mexe na imagem) so com
    # cadernos: tudo desligado + cadernos e o caminho rapido "so cadernos"
    # (Projeto.so_cadernos), que tem teste proprio abaixo.
    projeto.limpar = montar_cadernos
    projeto.detectar_regioes = False
    projeto.montar_cadernos = montar_cadernos
    projeto.qualidade_dpi = 72
    projeto.filtro_padrao = ORIGINAL
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(PAGINAS)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(PAGINAS)]
    return projeto


def _cancela_depois_de(n: int):
    """O "cancelar" apertado depois de `n` perguntas (uma por pagina)."""
    perguntas = {"n": 0}

    def cancelado() -> bool:
        perguntas["n"] += 1
        return perguntas["n"] > n
    return cancelado


@pytest.fixture
def livro(tmp_path):
    """(pasta de saida, entrada, saida com o PDF antigo, sha do antigo)."""
    entrada = tmp_path / "entrada" / "livro.pdf"
    entrada.parent.mkdir()
    _pdf_de_entrada(entrada)
    pasta = tmp_path / "saida"
    pasta.mkdir()
    saida = pasta / "pronto.pdf"
    return pasta, entrada, saida, _pdf_antigo(saida)


def _so_o_antigo_na_pasta(pasta: Path, saida: Path) -> None:
    sobra = sorted(p.name for p in pasta.iterdir())
    assert sobra == [saida.name], f"sobrou arquivo na pasta: {sobra}"


def _paginas(caminho: Path) -> int:
    with fitz.open(str(caminho)) as doc:
        return doc.page_count


# --- sem "Montar cadernos" (o normal) -------------------------------------------

@pytest.mark.parametrize("depois_de", [1, 2, PAGINAS])
def test_cancelar_ao_substituir_mantem_o_antigo_identico(livro, depois_de):
    """O defeito grave: "substituir o antigo" + "cancelar" apagava o antigo.
    depois_de=PAGINAS e o cancelar apertado depois da ultima pagina (o
    _checar do fim), o ponto mais perto de gravar."""
    pasta, entrada, saida, sha_antigo = livro
    with pytest.raises(Cancelou):
        processar(_projeto(entrada, saida), cancelado=_cancela_depois_de(depois_de))
    assert saida.exists(), "o PDF antigo foi apagado pelo cancelar"
    assert _sha(saida) == sha_antigo, "o PDF antigo mudou"
    _so_o_antigo_na_pasta(pasta, saida)


def test_terminar_troca_o_antigo_pelo_novo(livro):
    pasta, entrada, saida, sha_antigo = livro
    devolvido = processar(_projeto(entrada, saida))
    assert Path(devolvido) == saida
    assert _sha(saida) != sha_antigo
    assert _paginas(saida) == PAGINAS
    _so_o_antigo_na_pasta(pasta, saida)


def test_sem_pdf_antigo_continua_gravando_normal(tmp_path):
    entrada = tmp_path / "livro.pdf"
    _pdf_de_entrada(entrada)
    saida = tmp_path / "nova" / "pronto.pdf"
    processar(_projeto(entrada, saida))
    assert _paginas(saida) == PAGINAS
    assert sorted(p.name for p in saida.parent.iterdir()) == ["pronto.pdf"]


def test_erro_numa_pagina_mantem_o_antigo(livro, monkeypatch):
    """Uma pagina que falha no meio (qualquer erro do filtro, memoria...)."""
    pasta, entrada, saida, sha_antigo = livro
    original = pipeline.compor_na_folha
    vezes = {"n": 0}

    def falha_na_terceira(*a, **k):
        vezes["n"] += 1
        if vezes["n"] == 3:
            raise MemoryError("de mentira")
        return original(*a, **k)

    monkeypatch.setattr(pipeline, "compor_na_folha", falha_na_terceira)
    with pytest.raises(MemoryError):
        processar(_projeto(entrada, saida))
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def _disco_cheio_ao_gravar(monkeypatch):
    """fitz.Document.save que escreve um pedaco e para com "disco cheio"."""
    def save(self, nome, *a, **k):
        Path(nome).write_bytes(b"%PDF-1.7 pela metade")
        raise OSError(errno.ENOSPC, "No space left on device")
    monkeypatch.setattr(fitz.Document, "save", save)


def test_disco_cheio_ao_gravar_mantem_o_antigo(livro, monkeypatch):
    pasta, entrada, saida, sha_antigo = livro
    _disco_cheio_ao_gravar(monkeypatch)
    with pytest.raises(ErroPDF):
        processar(_projeto(entrada, saida))
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def test_o_arquivo_a_parte_fica_na_mesma_pasta_e_nao_parece_pdf(livro, monkeypatch):
    """O arquivo a parte e gravado ao lado do destino (para a troca ser uma
    so, no mesmo disco), com nome que o Kaique nao confunde com o PDF: comeca
    com "~" e nao termina em .pdf."""
    pasta, entrada, saida, _sha_antigo = livro
    gravados: list[Path] = []
    original = fitz.Document.save

    def save(self, nome, *a, **k):
        gravados.append(Path(nome))
        return original(self, nome, *a, **k)

    monkeypatch.setattr(fitz.Document, "save", save)
    processar(_projeto(entrada, saida))
    assert len(gravados) == 1
    assert gravados[0].parent == pasta
    assert gravados[0].name.startswith("~")
    assert gravados[0].suffix.lower() != ".pdf"


# --- com "Montar cadernos" -------------------------------------------------------

@pytest.mark.parametrize("depois_de", [1, PAGINAS])
def test_cadernos_cancelar_mantem_o_antigo(livro, depois_de):
    pasta, entrada, saida, sha_antigo = livro
    projeto = _projeto(entrada, saida, montar_cadernos=True)
    with pytest.raises(Cancelou):
        processar(projeto, cancelado=_cancela_depois_de(depois_de))
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def test_cadernos_terminar_troca_e_apaga_o_temporario(livro):
    import tempfile

    pasta, entrada, saida, sha_antigo = livro
    processar(_projeto(entrada, saida, montar_cadernos=True))
    assert _sha(saida) != sha_antigo
    assert _paginas(saida) > 0
    _so_o_antigo_na_pasta(pasta, saida)
    assert not (Path(tempfile.gettempdir()) / "_editor_impressao_pronto.pdf").exists()


def test_cadernos_erro_ao_montar_mantem_o_antigo(livro, monkeypatch):
    """A imposicao falha no meio da gravacao (disco cheio): antes ela gravava
    direto no arquivo final."""
    import tempfile

    pasta, entrada, saida, sha_antigo = livro

    def impor_que_falha(entrada_, saida_, *a, **k):
        Path(saida_).write_bytes(b"%PDF-1.7 pela metade")
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(pipeline, "impor_pdf", impor_que_falha)
    with pytest.raises(OSError):
        processar(_projeto(entrada, saida, montar_cadernos=True))
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)
    assert not (Path(tempfile.gettempdir()) / "_editor_impressao_pronto.pdf").exists()


def test_so_cadernos_erro_mantem_o_antigo(livro, monkeypatch):
    pasta, entrada, saida, sha_antigo = livro
    projeto = _projeto(entrada, saida)
    projeto.montar_cadernos = True          # tudo o mais desligado: so cadernos
    assert projeto.so_cadernos

    def impor_que_falha(entrada_, saida_, *a, **k):
        Path(saida_).write_bytes(b"%PDF-1.7 pela metade")
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(pipeline, "impor_pdf", impor_que_falha)
    with pytest.raises(OSError):
        processar(projeto)
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def test_so_cadernos_terminar_troca(livro):
    pasta, entrada, saida, sha_antigo = livro
    projeto = _projeto(entrada, saida)
    projeto.montar_cadernos = True          # tudo o mais desligado: so cadernos
    assert projeto.so_cadernos
    processar(projeto)
    assert _sha(saida) != sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


# --- sobra de uma vez que o programa caiu ------------------------------------------

def test_sobra_de_queda_anterior_e_apagada(livro):
    """O programa caiu (ou faltou luz) no meio da gravacao: ficou o arquivo a
    parte. Na proxima vez que o mesmo PDF for gerado, ele some."""
    pasta, entrada, saida, _sha_antigo = livro
    sobra = pasta / f"~{saida.name}.parcial"
    sobra.write_bytes(b"%PDF-1.7 de uma queda")
    processar(_projeto(entrada, saida))
    _so_o_antigo_na_pasta(pasta, saida)


def test_sobra_de_queda_some_tambem_ao_cancelar(livro):
    pasta, entrada, saida, sha_antigo = livro
    (pasta / f"~{saida.name}.parcial").write_bytes(b"%PDF-1.7 de uma queda")
    with pytest.raises(Cancelou):
        processar(_projeto(entrada, saida), cancelado=_cancela_depois_de(1))
    assert _sha(saida) == sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def test_arquivo_parecido_de_outro_livro_nao_e_apagado(livro):
    """So a sobra DESTE destino e apagada; nada mais da pasta."""
    pasta, entrada, saida, _sha_antigo = livro
    outro = pasta / "~outro.pdf.parcial"
    outro.write_bytes(b"de outro livro")
    processar(_projeto(entrada, saida))
    assert outro.read_bytes() == b"de outro livro"


# --- o PDF antigo aberto em outro programa --------------------------------------

def test_antigo_aberto_em_outro_programa_nao_perde_o_novo(livro, monkeypatch):
    """No Windows, os.replace falha quando o destino esta aberto (no leitor de
    PDF, por exemplo). O aviso e em portugues, o antigo fica, e o PDF novo
    vai para "pronto (2).pdf" - o aviso diz o nome."""
    pasta, entrada, saida, sha_antigo = livro
    replace_de_verdade = pipeline.os.replace

    def replace(origem, destino):
        if Path(destino) == saida:
            raise PermissionError(errno.EACCES, "Acesso negado", str(destino))
        return replace_de_verdade(origem, destino)

    monkeypatch.setattr(pipeline.os, "replace", replace)
    monkeypatch.setattr(pipeline, "ESPERA_DA_TROCA_S", 0.0, raising=False)
    with pytest.raises(ErroPDF) as erro:
        processar(_projeto(entrada, saida))

    novo = pasta / "pronto (2).pdf"
    assert _sha(saida) == sha_antigo
    assert novo.exists(), "o PDF novo se perdeu"
    assert _paginas(novo) == PAGINAS
    texto = str(erro.value)
    assert "pronto (2).pdf" in texto
    assert "aberto" in texto
    assert "Traceback" not in texto and "Errno" not in texto
    assert sorted(p.name for p in pasta.iterdir()) == ["pronto (2).pdf", "pronto.pdf"]


def test_antigo_aberto_mas_solta_logo_a_troca_acontece(livro, monkeypatch):
    """O antivirus ou o indexador do Windows seguram o arquivo por um
    instante: a troca tenta de novo antes de desistir."""
    pasta, entrada, saida, sha_antigo = livro
    replace_de_verdade = pipeline.os.replace
    falhas = {"n": 0}

    def replace(origem, destino):
        if Path(destino) == saida and falhas["n"] < 2:
            falhas["n"] += 1
            raise PermissionError(errno.EACCES, "Acesso negado", str(destino))
        return replace_de_verdade(origem, destino)

    monkeypatch.setattr(pipeline.os, "replace", replace)
    monkeypatch.setattr(pipeline, "ESPERA_DA_TROCA_S", 0.0, raising=False)
    processar(_projeto(entrada, saida))
    assert _sha(saida) != sha_antigo
    _so_o_antigo_na_pasta(pasta, saida)


def test_na_tela_o_aviso_do_antigo_aberto_sai_como_esta(livro, monkeypatch):
    """O aviso chega a tela pelo ui/tarefas.py::_mensagem_amigavel, que
    mostra o ErroPDF como ele e (sem trocar por "problema inesperado")."""
    pytest.importorskip("PySide6")
    from ui.tarefas import _mensagem_amigavel

    pasta, entrada, saida, _sha_antigo = livro
    monkeypatch.setattr(pipeline.os, "replace", _sempre_aberto(saida, pipeline.os.replace))
    monkeypatch.setattr(pipeline, "ESPERA_DA_TROCA_S", 0.0, raising=False)
    with pytest.raises(ErroPDF) as erro:
        processar(_projeto(entrada, saida))
    assert _mensagem_amigavel(erro.value) == str(erro.value)


def _sempre_aberto(saida: Path, replace_de_verdade):
    def replace(origem, destino):
        if Path(destino) == saida:
            raise PermissionError(errno.EACCES, "Acesso negado", str(destino))
        return replace_de_verdade(origem, destino)
    return replace


@pytest.mark.skipif(__import__("sys").platform != "win32", reason="so o Windows prende o arquivo aberto")
def test_antigo_aberto_de_verdade_no_windows(livro, monkeypatch):
    """Sem simulacao: o PDF antigo fica aberto (como num leitor de PDF)
    enquanto o programa processa. No Windows a troca falha de verdade
    (PermissionError, "Acesso negado"); o antigo fica e o novo vai para (2)."""
    pasta, entrada, saida, sha_antigo = livro
    monkeypatch.setattr(pipeline, "ESPERA_DA_TROCA_S", 0.0, raising=False)
    with open(saida, "rb"):
        with pytest.raises(ErroPDF) as erro:
            processar(_projeto(entrada, saida))
    assert _sha(saida) == sha_antigo
    assert _paginas(pasta / "pronto (2).pdf") == PAGINAS
    assert "pronto (2).pdf" in str(erro.value)
    assert sorted(p.name for p in pasta.iterdir()) == ["pronto (2).pdf", "pronto.pdf"]
