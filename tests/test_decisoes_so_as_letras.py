"""O "Só as letras" ligado na janela do Automático (pedido do Samuel, 29/10/2026).

Palavras dele: "eu usei no painel automatico, mas não foi agora na ultima sessão e não lembro que
ssessão foi, mas cofira se isso está funcionando".

Decisões (docs/plano/DECISOES.md):
  D-148 (30/09 e 05/10/2026): "(a) Uma caixinha 'Só as letras' dentro do Preto e branco, para o
      livro (tela 'O que fazer') e para a página (aba Filtro) (recomendado)" - marcada, só as
      letras viram preto e branco; gravura, foto, moldura e iluminura ficam como no original.
      A do livro mora hoje na janela do Automático (etapa "Limpar a folha"; D-002).
  D-168 (05/10/2026): "(a) Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta
      como estava ao desligar (recomendado)".

O que se prova, pelo caminho do Kaique (abrir o livro → Automático → "Jeito de limpar: Preto e
branco" + "Só as letras" → Rodar), medindo o estado gravado e os pontos da página:
  a) o livro fica com "Só as letras" (no projeto aberto e no projeto.json) e a página em Preto e
     branco sai com as letras em preto e branco e a gravura com a cor, na tela ("Uma página" e
     "antes / depois") e no PDF;
  b) o painel "Filtro da página" mostra o que vale na página: a caixinha marcada (herdada do
     livro) e o resumo da parte com o jeito escolhido, não "desligado";
  c) desfazer o Automático devolve o "Só as letras" do livro como estava; refazer põe de volta.
  D-168 na janela do Automático: a caixinha das molduras fica cinza e volta como estava.

Achado da conferência (relatorios/automatico-pintura/ONDE-PAREI.md): funciona, também no livro
dele ("Na escola de Jesus", página 9; medida-so-as-letras.txt). Estas provas guardam o caminho
para um defeito futuro nunca aparecer escondido; elas já passavam no 226536c (não houve conserto,
então não há teste de reversão para elas).

Livro sintético: papel amarelado, uma "pintura" colorida em cima e linhas de "texto" pretas
embaixo. A marcação que o "Gravuras e fotos" deixa é posta direto na página (como em
tests/test_decisoes_filtro_automatico.py, do D-582), sem rodar o detector; o leitor de texto não
roda (devolve "nenhuma linha": o jeito de fábrica, "Guardar a tinta forte", guarda a tinta preta).
"""

from __future__ import annotations

import copy
import json
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import misto  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402

DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho
PINTURA = (90, 90, 510, 430)           # x0, y0, x1, y1 na página de 600 x 840
TEXTO = (100, 490, 500, 750)


def _pagina(largura: int = 600, altura: int = 840) -> np.ndarray:
    """Papel amarelado; em cima uma "pintura" de cores fortes em degradê; embaixo linhas de
    "texto" pretas."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    x0, y0, x1, y1 = PINTURA
    yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]
    img[y0:y1, x0:x1, 0] = (40 + 180 * xx / (x1 - x0)).astype(np.uint8)
    img[y0:y1, x0:x1, 1] = (60 + 120 * yy / (y1 - y0)).astype(np.uint8)
    img[y0:y1, x0:x1, 2] = (220 - 160 * xx / (x1 - x0)).astype(np.uint8)
    for y in range(500, altura - 100, 36):
        img[y:y + 11, 110:largura - 110] = 25
    return img


def _pdf(caminho: Path, folhas: int = 2) -> str:
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


@pytest.fixture(autouse=True)
def leitor_rapido(monkeypatch):
    """O leitor de texto (docTR) não roda: leva segundos e não é o assunto."""
    from core import pipeline

    monkeypatch.setattr(pipeline.linhas_do_texto, "linhas_da_pagina", lambda *a, **k: [])
    monkeypatch.setattr(pipeline.linhas_do_texto, "aquecer_em_segundo_plano", lambda: None)


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


def _livro_com_a_marcacao(janela, tmp_path: Path):
    """Abre o livro, roda o Automático de fábrica (Limpar a folha, no Original) e põe na
    página 1 a marcação do "Gravuras e fotos" (a pintura como gravura, o texto como letra)."""
    from core.selecao import GRAVURA, LETRA, REDE, RETANGULO, Regiao, Selecao
    from tests.ajudante_do_automatico import rodar_como_o_conferir

    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    assert rodar_como_o_conferir(janela, endireitar=False, cortar_bordas=False, limpar=True)
    projeto = janela.projeto
    projeto.detectar_regioes = True
    pagina = projeto.paginas[0]
    marcacao = Selecao()
    x0, y0, x1, y1 = PINTURA
    marcacao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, origem=REDE,
                                pontos=[(x0 / 600, y0 / 840), (x1 / 600, y1 / 840)]))
    x0, y0, x1, y1 = TEXTO
    marcacao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, origem=REDE,
                                pontos=[(x0 / 600, y0 / 840), (x1 / 600, y1 / 840)]))
    pagina.guardar_selecao(marcacao, provisoria=False)
    pagina.gravura_feita_com = ""
    tela = janela.tela_conferir
    tela.previas.invalidar()
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(0)
    _assentar()
    assert projeto.misto_so_as_letras is False and pagina.filtro == ORIGINAL
    return tela


def _rodar_com_so_as_letras(janela) -> None:
    """O clique do Kaique: na janela do Automático, "Preto e branco" + "Só as letras", só a
    etapa "Limpar a folha", no livro todo, e Rodar."""
    jan = janela.abrir_o_automatico("limpar")
    jan.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    jan.escolhas_misto.caixa.setChecked(True)
    _assentar()
    estado = janela.estado_do_automatico
    estado.marcadas = {A.LIMPAR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    _assentar()


def _bgr(img) -> np.ndarray:
    img = np.asarray(img)
    return np.repeat(img[..., None], 3, axis=2) if img.ndim == 2 else img


def _pixmap_bgr(pix) -> np.ndarray:
    imagem = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(h, imagem.bytesPerLine())
    return dados[:, : w * 3].reshape(h, w, 3)[..., ::-1].copy()


def _cor(img: np.ndarray, caixa) -> float:
    """Fração dos pontos com cor (diferença entre os canais acima de 30) dentro da `caixa`
    (em pontos da página de 600 x 840, reescalada para o tamanho de `img`)."""
    img = _bgr(img).astype(int)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = caixa
    pedaco = img[int(y0 / 840 * h) + 4:int(y1 / 840 * h) - 4, int(x0 / 600 * w) + 4:int(x1 / 600 * w) - 4]
    croma = (np.abs(pedaco[..., 0] - pedaco[..., 2]) + np.abs(pedaco[..., 1] - pedaco[..., 2]))
    return float((croma > 30).mean())


def _confere_letras_pb_e_pintura_com_cor(img: np.ndarray, onde: str) -> None:
    assert _cor(img, TEXTO) < 0.01, f"{onde}: as letras não saíram em preto e branco"
    assert _cor(img, PINTURA) > 0.80, f"{onde}: a gravura perdeu a cor (o 'Só as letras' não valeu)"


def test_d148_so_as_letras_do_automatico_grava_no_livro_e_vale_na_tela_e_no_pdf(janela, tmp_path):
    """(a) "Só as letras" ligado na janela do Automático → o livro grava (projeto aberto e
    projeto.json), a página fica em Preto e branco com "Só as letras" herdado do livro, e a
    tela ("Uma página" e "antes / depois") e o PDF saem com as letras em preto e branco e a
    gravura com a cor (D-148)."""
    from core.pipeline import processar

    tela = _livro_com_a_marcacao(janela, tmp_path)
    _rodar_com_so_as_letras(janela)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    assert projeto.misto_so_as_letras is True
    assert pagina.filtro == PRETO_E_BRANCO and pagina.misto_so_as_letras is None   # herda do livro
    assert misto.escolhas_da_pagina(projeto, pagina)[0] is True
    gravado = json.loads((Path(janela.resumo.pasta) / "projeto.json").read_text(encoding="utf-8"))
    assert gravado["misto_so_as_letras"] is True and gravado["filtro_padrao"] == PRETO_E_BRANCO

    dpi = tela._dpi_atual
    editor = tela.editor_selecao
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia em Preto e branco")
    _confere_letras_pb_e_pintura_com_cor(editor._img, "tela, 'Uma página'")
    tela.botao_antes_depois.click()
    vista = tela.vista_antes_depois
    _esperar(lambda: vista.depois is not None and tela.previas.ja_pronta(0, dpi) is not None,
             motivo="o antes / depois")
    _assentar()
    _confere_letras_pb_e_pintura_com_cor(_pixmap_bgr(vista.depois), "tela, 'antes / depois'")

    copia = copy.copy(projeto)
    copia.caminho_saida = str(tmp_path / "saida.pdf")
    with fitz.open(processar(copia)) as doc:
        pix = doc[0].get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
        no_pdf = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].copy()
    _confere_letras_pb_e_pintura_com_cor(no_pdf, "PDF")


def test_d148_o_painel_filtro_da_pagina_mostra_o_so_as_letras_herdado_do_livro(janela, tmp_path):
    """(b) Depois de rodar, o painel "Filtro da página" mostra o que vale na página: a caixinha
    "Só as letras" marcada (vinda do livro) e, à direita da parte, o jeito escolhido ("Guardar a
    tinta forte"), não "desligado". E continua assim ao sair da página e voltar."""
    from ui.tela_conferir import PAINEL_FILTRO

    tela = _livro_com_a_marcacao(janela, tmp_path)
    tela.paineis.abrir(PAINEL_FILTRO)
    _assentar()
    parte = tela.paineis.filtro_da_pagina.partes["letras"]
    assert not tela.escolhas_misto.caixa.isChecked()
    _rodar_com_so_as_letras(janela)
    for _vez in range(2):
        assert tela.escolhas_misto.caixa.isChecked(), "o painel mostra 'Só as letras' desligado"
        assert parte.cabeca.resumo.text() not in ("", "desligado"), parte.cabeca.resumo.text()
        assert tela.escolhas_misto.isVisibleTo(tela.escolhas_misto.parentWidget())
        tela.ir_para_pagina(1)
        _assentar()
        tela.ir_para_pagina(0)
        _assentar()


def test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro(janela, tmp_path):
    """(c) Ctrl+Z no Automático: o "Só as letras" do livro volta a desligado (e o filtro ao
    Original), também no projeto.json e no painel; Ctrl+Y põe de volta."""
    from ui.tela_conferir import PAINEL_FILTRO

    tela = _livro_com_a_marcacao(janela, tmp_path)
    tela.paineis.abrir(PAINEL_FILTRO)
    _rodar_com_so_as_letras(janela)
    projeto = janela.projeto
    assert projeto.misto_so_as_letras is True
    tela.desfazer()
    _assentar()
    assert projeto.misto_so_as_letras is False
    assert projeto.paginas[0].filtro == ORIGINAL
    arquivo = Path(janela.resumo.pasta) / "projeto.json"
    # o desfazer grava pelo salvar de sempre (com um pequeno atraso, como toda mudança)
    _esperar(lambda: json.loads(arquivo.read_text(encoding="utf-8"))["misto_so_as_letras"] is False,
             segundos=15, motivo="o projeto.json com o 'Só as letras' desfeito")
    assert not misto.escolhas_da_pagina(projeto, projeto.paginas[0])[0]
    tela.refazer()
    _assentar()
    assert projeto.misto_so_as_letras is True and projeto.paginas[0].filtro == PRETO_E_BRANCO
    assert tela.escolhas_misto.caixa.isChecked()


@pytest.mark.parametrize("molduras_antes", [False, True])
def test_d168_na_janela_do_automatico_a_caixinha_das_molduras_apaga_e_volta(janela, tmp_path,
                                                                              molduras_antes):
    """D-168: na janela do Automático, com o Preto e branco, marcar "Só as letras" deixa a
    caixinha das molduras cinza; desmarcar devolve como estava (marcada ou não)."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    jan = janela.abrir_o_automatico("limpar")
    jan.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    jan.cx_decoracao_pb.setChecked(molduras_antes)
    _assentar()
    assert jan.cx_decoracao_pb.isEnabled()
    jan.escolhas_misto.caixa.setChecked(True)
    _assentar()
    assert not jan.cx_decoracao_pb.isEnabled()
    jan.escolhas_misto.caixa.setChecked(False)
    _assentar()
    assert jan.cx_decoracao_pb.isEnabled() and jan.cx_decoracao_pb.isChecked() is molduras_antes
