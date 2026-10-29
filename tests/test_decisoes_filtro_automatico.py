"""D-582 (Samuel, 29/10/2026): trocar o filtro de uma página depois do Automático.

Palavras dele: "depois de rodar o automatico, quando eu tento escolher outro filtro para uma
folha só, ele joga o filtro em cima do filtro que já tinha sido aplicado, e quando eu escolho
outro filtro ainda, ele nem mostra a mudança em tela mesmo eu estando na opção antes e depois."
Prova pedida no Livro de decisões: "rodar o Automático → trocar o filtro de uma página duas vezes
→ a tela mostra cada filtro escolhido, sozinho".

O que a investigação achou (relatorios/automatico-filtro/ONDE-PAREI.md):
  - a tela NÃO fica parada: a cada filtro escolhido ela recebe o desenho desse filtro, feito
    de novo a partir do scan (em 0,6 a 1,7 s no livro dele, "Na escola de Jesus", capa);
  - o filtro novo NÃO vai por cima do anterior: a página é sempre desenhada a partir do PDF;
  - o que "fica por cima" é a MARCAÇÃO que o "Gravuras e fotos" do Automático deixou (gravura,
    letra e papel). Na capa dele, a pintura inteira foi tomada por "enfeite colorido" (como
    moldura dourada ou iluminura), que fica com a cor em todos os filtros (D-144, D-127,
    D-128); por isso Preto e branco, Melhorar e Mágico pro saem quase iguais ali (diferença
    média de 0,2 a 2,2 tons em 255) e a troca parece não mudar nada. Isso é regra decidida, não
    defeito de tela: não foi mexido (vira a pergunta D-583).

Estas provas guardam o que a tela tem de fazer, para um defeito de tela (prévia velha, "antes /
depois" com outra imagem, clique que não grava) nunca aparecer escondido:
  1. "Uma página": depois do Automático, escolher um filtro e depois outro → a imagem que a
     vista da página recebe é, a cada vez, o desenho do filtro escolhido, e muda de uma vez para
     a outra.
  2. "antes / depois": o mesmo, com o lado "depois" (e o rótulo) do filtro escolhido e o
     "antes" no Original.
  3. Não é filtro em cima de filtro: Preto e branco e depois Mágico pro dá exatamente a página
     que o Mágico pro dá direto, sem ter passado pelo Preto e branco.

Livro sintético (papel amarelado, uma "pintura" colorida em cima e linhas de "texto" embaixo).
O Automático roda com "Limpar a folha" (o que liga o filtro); a marcação que o "Gravuras e fotos"
deixa é posta direto na página (a pintura como gravura e o texto como letra, origem "rede", como
no livro dele), sem rodar o detector, que é lento e não é o assunto aqui.
Nenhum destes testes mudou de resultado com o código: a tela já fazia isso no `dd13350` (ver o
ONDE-PAREI, "Ressalvas": sem conserto, não há teste de reversão).
"""

from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402

DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- o livro de teste -------------------------------------------------------------

def _pagina(largura: int = 600, altura: int = 840) -> np.ndarray:
    """Papel amarelado; em cima uma "pintura" de cores fortes (faixas que vão do vermelho ao
    azul e ao amarelo, com degradê, como a capa colorida); embaixo linhas de "texto"."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    y0, y1, x0, x1 = 90, 430, 90, largura - 90
    alt, larg = y1 - y0, x1 - x0
    yy, xx = np.mgrid[0:alt, 0:larg]
    img[y0:y1, x0:x1, 0] = (40 + 180 * xx / larg).astype(np.uint8)              # azul cresce
    img[y0:y1, x0:x1, 1] = (60 + 120 * yy / alt).astype(np.uint8)               # verde
    img[y0:y1, x0:x1, 2] = (220 - 160 * xx / larg).astype(np.uint8)             # vermelho cai
    for y in range(500, altura - 100, 36):
        img[y:y + 11, 110:largura - 110] = 25
    return img


def _pdf(caminho: Path, folhas: int = 2) -> str:
    """Um livro de `folhas` folhas de uma página só (sem dividir)."""
    doc = fitz.open()
    for _ in range(folhas):
        img = _pagina()
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


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


def _esperar(condicao, segundos: float = 60.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _depois_do_automatico(janela, tmp_path: Path):
    """O caminho do Kaique: abrir o livro, rodar o Automático com "Limpar a folha" (o filtro
    de fábrica do livro é o Original) e, na página 1, a marcação que o "Gravuras e fotos"
    deixa: a pintura como gravura e o bloco de texto como letra (origem "rede", definitiva,
    como no "Na escola de Jesus"). Devolve a tela, na página 1, com o Zoom (a página limpa,
    sem as cores das marcações: D-580)."""
    from core.selecao import GRAVURA, LETRA, REDE, RETANGULO, Regiao, Selecao
    from tests.ajudante_do_automatico import rodar_como_o_conferir

    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    assert rodar_como_o_conferir(janela, endireitar=False, cortar_bordas=False, limpar=True)
    projeto = janela.projeto
    assert projeto.limpar and projeto.passou_pelo_automatico
    projeto.detectar_regioes = True                # o "Gravuras e fotos" ligado no livro
    pagina = projeto.paginas[0]
    marcacao = Selecao()
    marcacao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, origem=REDE,
                                pontos=[(90 / 600, 90 / 840), (510 / 600, 430 / 840)]))
    marcacao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, origem=REDE,
                                pontos=[(100 / 600, 490 / 840), (500 / 600, 750 / 840)]))
    pagina.guardar_selecao(marcacao, provisoria=False)
    pagina.gravura_feita_com = ""                  # a marcação vale como está (não procura de novo)
    tela = janela.tela_conferir
    tela.previas.invalidar()
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(0)
    _assentar()
    assert pagina.filtro == ORIGINAL
    return tela


def _desenho(projeto, pagina, filtro: str, dpi: int) -> np.ndarray:
    """A página desenhada com `filtro`, do scan, numa cópia (core.pipeline.renderizar_com_filtro,
    o mesmo desenho da prévia), em 3 canais (BGR)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_com_filtro

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = renderizar_com_filtro(doc, copy.deepcopy(projeto), copy.deepcopy(pagina),
                                       filtro, dpi=dpi)
    finally:
        doc.close()
    return _bgr(img)


def _bgr(img: np.ndarray) -> np.ndarray:
    return np.repeat(img[..., None], 3, axis=2) if img.ndim == 2 else img


def _pixmap_bgr(pix) -> np.ndarray:
    """O QPixmap que a vista recebeu, de volta em BGR."""
    imagem = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(h, imagem.bytesPerLine())
    return dados[:, : w * 3].reshape(h, w, 3)[..., ::-1].copy()


def _diferenca(a: np.ndarray, b: np.ndarray) -> float:
    assert a.shape == b.shape, f"tamanhos diferentes: {a.shape} e {b.shape}"
    return float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())


def _escolher(tela, filtro: str) -> None:
    """O clique no filtro do painel "Filtro da página" (o mesmo sinal dos cartões; teclas 1 a 4
    e o menu chegam ao mesmo TelaConferir._escolher_filtro)."""
    tela.paineis.filtro_da_pagina.filtro_escolhido.emit(filtro)
    _assentar()


# --- 1. "Uma página" ----------------------------------------------------------------

def test_d582_uma_pagina_mostra_cada_filtro_escolhido_depois_do_automatico(janela, tmp_path):
    """D-582: depois do Automático, escolher Preto e branco e depois Mágico pro (o que ele quis
    no livro dele) numa página só → a vista da página ("Uma página") recebe, a cada vez, o
    desenho do filtro escolhido (diferença 0 com o desenho feito do scan) e a imagem muda de
    um filtro para o outro. Só a página 1 muda; a 2 continua no Original."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    editor = tela.editor_selecao
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    dpi = tela._dpi_atual
    _esperar(lambda: editor._img is not None, motivo="a página em Original")
    anterior = _bgr(editor._img).copy()
    for filtro in (PRETO_E_BRANCO, MAGICO_PRO):
        _escolher(tela, filtro)
        assert pagina.filtro == filtro, "o clique no filtro não gravou na página"
        _esperar(lambda: editor._img is not None
                 and editor._img is tela.previas.ja_pronta(0, dpi), motivo=f"a prévia em {filtro}")
        mostrada = _bgr(editor._img)
        assert _diferenca(mostrada, _desenho(projeto, pagina, filtro, dpi)) < 0.5, \
            f"a tela não mostra o {filtro} escolhido"
        assert _diferenca(mostrada, anterior) > 1.0, f"a tela não mudou ao escolher {filtro}"
        anterior = mostrada.copy()
    assert projeto.paginas[1].filtro == ORIGINAL


# --- 2. "antes / depois" ------------------------------------------------------------

def test_d582_antes_depois_mostra_cada_filtro_escolhido_depois_do_automatico(janela, tmp_path):
    """D-582 ("mesmo eu estando na opção antes e depois"): com o "antes / depois" ligado,
    escolher Preto e branco e depois Mágico pro → o lado "depois" recebe o desenho do filtro
    escolhido, com o nome dele no rótulo, e muda de um para o outro; o "antes" é sempre o
    Original."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    vista = tela.vista_antes_depois
    tela.botao_antes_depois.click()
    assert tela.vista_da_pagina.currentWidget() is vista
    dpi = tela._dpi_atual
    _esperar(lambda: vista.depois is not None, motivo="a página em Original")
    anterior = _pixmap_bgr(vista.depois)
    nomes = {PRETO_E_BRANCO: "Preto e branco", MAGICO_PRO: "Mágico pro"}
    for filtro in (PRETO_E_BRANCO, MAGICO_PRO):
        _escolher(tela, filtro)
        assert pagina.filtro == filtro
        _esperar(lambda: tela.previas.ja_pronta(0, dpi) is not None and vista.depois is not None
                 and vista.antes is not None, motivo=f"o antes e o depois em {filtro}")
        _assentar()
        assert vista.comparando and vista.rotulos == ("antes: Original", f"depois: {nomes[filtro]}")
        depois = _pixmap_bgr(vista.depois)
        assert _diferenca(depois, _desenho(projeto, pagina, filtro, dpi)) < 0.5, \
            f"o 'depois' não é o {filtro} escolhido"
        assert _diferenca(_pixmap_bgr(vista.antes), _desenho(projeto, pagina, ORIGINAL, dpi)) < 0.5, \
            "o 'antes' não é o Original"
        assert _diferenca(depois, anterior) > 1.0, f"o 'depois' não mudou ao escolher {filtro}"
        anterior = depois


# --- 3. não é filtro em cima de filtro -------------------------------------------------

def test_d582_o_filtro_novo_nao_vai_por_cima_do_anterior(janela, tmp_path):
    """D-582 ("ele joga o filtro em cima do filtro que já tinha sido aplicado"): a página é
    desenhada sempre a partir do scan. Escolher Preto e branco e depois Mágico pro dá
    exatamente a mesma imagem que o Mágico pro direto, numa cópia do livro que nunca passou
    pelo Preto e branco (e a mesma que a tela mostra). O que continua valendo de um filtro
    para o outro é a marcação do Automático (gravura, letra, papel), não o filtro de antes."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    dpi = tela._dpi_atual
    direto = _desenho(projeto, pagina, MAGICO_PRO, dpi)       # antes de qualquer escolha
    _escolher(tela, PRETO_E_BRANCO)
    _esperar(lambda: tela.previas.ja_pronta(0, dpi) is not None, motivo="o Preto e branco")
    _escolher(tela, MAGICO_PRO)
    _esperar(lambda: tela.previas.ja_pronta(0, dpi) is not None
             and tela.editor_selecao._img is tela.previas.ja_pronta(0, dpi), motivo="o Mágico pro")
    assert _diferenca(_bgr(tela.previas.ja_pronta(0, dpi)), direto) < 0.5
    assert _diferenca(_bgr(tela.editor_selecao._img), direto) < 0.5
    assert pagina.obter_selecao().regioes, "a marcação do Automático continua na página"


def test_d582_melhorar_tambem_aparece_na_tela(janela, tmp_path):
    """D-582, o terceiro filtro de cor: Mágico pro e depois Melhorar → a tela recebe o desenho
    do Melhorar. (Com a marcação do Automático, Melhorar e Mágico pro tratam a gravura e a
    letra do mesmo jeito suave, então a diferença entre os dois pode ser pequena: aqui só se
    exige que a tela mostre o desenho do filtro escolhido.)"""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    dpi = tela._dpi_atual
    for filtro in (MAGICO_PRO, MELHORAR):
        _escolher(tela, filtro)
        _esperar(lambda: tela.editor_selecao._img is not None
                 and tela.editor_selecao._img is tela.previas.ja_pronta(0, dpi),
                 motivo=f"a prévia em {filtro}")
        assert _diferenca(_bgr(tela.editor_selecao._img),
                          _desenho(projeto, pagina, filtro, dpi)) < 0.5
