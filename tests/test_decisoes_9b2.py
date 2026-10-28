"""As provas de comportamento da etapa 9b-2 da obra de 26/10/2026: a área de trabalho
(CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede é o projeto
gravado, a imagem que sai (no PDF ou na tela), a página da vez e o desfazer. Os que provam um
conserto de defeito (CLAUDE.md §4.7) falham no código antigo (`obra-2026-10-26` = 27b4c52): o
resultado está em relatorios/obra-etapa9b2/reversao-no-codigo-antigo.txt.

  D-558 (27/10, `ac-grade-inserir`): "quando falei dividir é dividir a pagina, usando a
      funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser feito."
  D-559 (27/10, `ac-tampa`): "Como eu decidi: sumir em todo o livro, e o Kaique escolhe por livro
      cortar ou pintar de branco" (D-097 "É para sumir totalmente."; D-092 "O Kaique escolhe por
      livro").
  D-547 / D-473 / D-066 / D-064: a tela mostra a página como sai no PDF ("precisamos que o pdf saia
      que nem está na tela"; "é só colocar uma bolinha de carregamento, pode ter uma pro livro
      inteiro e outra para a pagina que estamos").
  D-568 (`v-roda`): "sem zoom troca de página; Ctrl + roda dá zoom" + com zoom anda pela página.
  D-570 (`v-zoom-pares`): "Sim, zoom também no lado a lado".  D-571 (`v-100`): "A página inteira
      cabendo na tela".
  D-554 (`ac-margens-iguais`): "Também na tela do corte".
  D-563 (`ac-desentortar-texto`): "Tirar, voltar como era antes".  D-564 (`ac-gravura-cinza`):
      "Não fazer: gravura continua em preto e branco".
  D-020: "Ctrl+Z desfaz qualquer alteração" (lista única 1.3, 1.6, 1.7, 1.9, 4.6; promessa P-129).
  D-090 / D-091 (P-061): "usar em todas" com as exceções desmarcadas, que nunca apaga exceção.
"""

from __future__ import annotations

import copy
import inspect
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402

DPI = 100
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- os livros de teste -----------------------------------------------------------

def _pagina(largura: int = 600, altura: int = 840, marca: int = 0) -> np.ndarray:
    """Papel amarelado com margem larga, linhas de "texto" pretas e, no alto, `marca`
    quadradinhos (para saber qual página é qual)."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    for k in range(marca % 12):
        img[60:80, 110 + k * 24:126 + k * 24] = 0
    return img


def _aberto(marca: int = 0) -> np.ndarray:
    """Um livro aberto: duas páginas lado a lado (a dobra no meio)."""
    return np.concatenate([_pagina(marca=2 * marca), _pagina(marca=2 * marca + 1)], axis=1)


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava: as páginas desenhadas."""
    from core.pipeline import processar

    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


# --- D-563 e D-564: as contas que ele mandou tirar saíram -----------------------------------

def test_d563_a_conta_desentortar_so_o_bloco_do_texto_saiu():
    """D-563 (27/10/2026, Central `ac-desentortar-texto`: "Tirar, voltar como era antes
    (recomendo)"). A conta "desentortar seguindo só o bloco do texto" (D-493/D-530, etapa 10b,
    pronta e não ligada) saiu: a caixa do conteúdo do desentortar não tem mais o jeito "só o
    bloco" nem a conta das notas da margem. Falha no código antigo (a conta estava lá)."""
    from core import desentortar_scantailor as ds

    assert "so_o_bloco" not in inspect.signature(ds.caixa_do_conteudo).parameters
    assert not hasattr(ds, "_so_o_bloco_do_texto")
    assert not hasattr(ds, "BLOCO_PERCENTIL")


def test_d563_a_caixa_do_conteudo_continua_a_de_sempre():
    """D-563 ("voltar como era antes"): a caixa do conteúdo que vai ao desentortar é a de
    sempre, com o texto e as notas da margem dentro (nada ficou de fora)."""
    from core import desentortar_scantailor as ds

    img = np.full((1400, 1200, 3), 225, np.uint8)
    for y in range(160, 1260, 36):
        for x in range(260, 940, 22):
            img[y:y + 16, x:x + 14] = 30
    for y in (300, 336, 900):                           # notas da esquerda
        img[y:y + 12, 120:200] = 40
    x, _y, largura, _a = ds.caixa_do_conteudo(img, (0, 0, 1200, 1400), 300)
    assert x <= 125 and x + largura >= 930


def test_d564_a_chave_da_gravura_escura_em_cinza_saiu():
    """D-564 (27/10/2026, Central `ac-gravura-cinza`: "Não fazer: gravura continua em preto e
    branco (recomendo)"). A chave `GRAVURA_ESCURA_EM_CINZA` (D-532, etapa 9d, desligada) e a
    conta dela saíram. Falha no código antigo. A prova de que a gravura de fundo escuro do
    Palatino 74 sai em 1 bit pelo caminho inteiro é
    tests/test_decisoes_nucleo2.py::test_d564_palatino_74_continua_em_1_bit."""
    from core import filtros

    assert not hasattr(filtros, "GRAVURA_ESCURA_EM_CINZA")
    assert not hasattr(filtros, "_e_gravura_escura_ou_reticula")


# --- D-554: "Margens iguais" também na tela do Cortar ----------------------------------------

def test_d554_margens_iguais_na_tela_do_cortar_e_o_mesmo_valor_do_automatico(janela, tmp_path):
    """D-554 (27/10/2026, Central `ac-margens-iguais`: "Também na tela do corte"; confirma a
    D-494; D-075: "Mas eu vou conseguir alterar isso né?"). Na ferramenta Cortar há a caixinha
    "Margens iguais", desmarcada de fábrica; marcar liga as margens iguais DO LIVRO (o mesmo
    valor da etapa do Automático, que passa a mostrá-la marcada), numa ação do desfazer; o PDF
    sai com todas as páginas do mesmo tamanho. Falha no código antigo (não havia a caixinha)."""
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR

    imagens = [_pagina(600, 840), _pagina(520, 760), _pagina(640, 800)]
    janela.abrir_livro(_pdf(tmp_path / "tamanhos.pdf", imagens))
    tela = janela.tela_conferir
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    _assentar()
    caixa = tela.caixa_margens_iguais
    assert caixa.text() == "Margens iguais" and not caixa.isHidden()
    assert caixa.isChecked() is False and janela.projeto.margens_iguais is False

    caixa.click()
    _assentar()
    assert janela.projeto.margens_iguais is True
    assert A.MARGENS in tela.paineis.automatico.estado.marcadas      # o Automático mostra
    assert "Margens iguais" in janela.acoes.feitas[-1].descricao

    tela.desfazer()
    _assentar()
    assert janela.projeto.margens_iguais is False and not caixa.isChecked()
    tela.refazer()
    _assentar()
    assert janela.projeto.margens_iguais is True and caixa.isChecked()

    paginas = _gerar(janela, tmp_path, "margens")
    tamanhos = {p.shape[:2] for p in paginas}
    assert len(paginas) == 3 and len(tamanhos) == 1, tamanhos
