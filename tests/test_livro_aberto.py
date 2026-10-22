"""O livro aberto na tela inteira (etapa 7 do layout; rodada 6 e escolhas de 06/10; rodada 7, 201 B e
202 A): as folhas rolando, "Ver lado a lado" em pares com a 1 sozinha, e o folhear que só desenha
o que aparece (nunca o livro inteiro na memória)."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

fitz = pytest.importorskip("fitz")

from tests.test_gravura_na_aba_marcar import app  # noqa: F401, E402 - fixture


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(30):
        pagina = doc.new_page(width=400, height=600)
        pagina.insert_text((50, 80), f"folha {i + 1}", fontsize=30)
    doc.save(str(caminho))
    doc.close()
    return caminho


def test_folhas_rolando_e_lado_a_lado(app, livro):  # noqa: F811
    from ui.widgets.paginas_rolando import PaginasRolando

    vista = PaginasRolando()
    vista.resize(900, 600)
    vista.abrir(str(livro))
    assert vista.total() == 30
    ret = dict(vista.retangulos())
    assert ret[0].top() < ret[1].top(), "uma embaixo da outra"
    vista.definir_lado_a_lado(True)
    ret = dict(vista.retangulos())
    assert ret[1].top() == ret[2].top() and ret[1].left() < ret[2].left(), "2 e 3 lado a lado"
    assert ret[0].top() < ret[1].top() and ret[0].left() >= ret[1].right() - 1, \
        "a folha 1 sozinha, à direita, como num livro"
    vista.ir_para(20)
    assert vista.atual == 20
    vista.parar()


def test_so_guarda_algumas_folhas(app, livro):  # noqa: F811
    from ui.widgets import paginas_rolando as pr
    import numpy as np

    vista = pr.PaginasRolando()
    vista.abrir(str(livro))
    for i in range(30):
        vista._chegou(i, np.zeros((20, 14, 3), dtype=np.uint8))
    assert len(vista.guardadas) <= pr.MAXIMO_GUARDADAS
    vista.parar()


def test_a_folha_e_desenhada_na_resolucao_da_tela(app, livro):  # noqa: F811
    """Verificador, 21/10/2026: no livro aberto, uma página por vez, a página
    saía borrada (desenhada a 70 DPI fixo e aumentada na tela). A folha
    desenhada tem de ter pelo menos a largura, em pixels, que ocupa na tela."""
    import time

    from PySide6.QtWidgets import QApplication

    from ui.widgets.paginas_rolando import PaginasRolando

    vista = PaginasRolando()
    vista.resize(900, 600)
    vista.abrir(str(livro))
    vista.ir_para(0)
    fim = time.time() + 15
    while 0 not in vista.guardadas and time.time() < fim:
        QApplication.processEvents()
        time.sleep(0.02)
    assert 0 in vista.guardadas
    assert vista.guardadas[0].width() >= vista.pixels_necessarios(0) * 0.95, \
        f"{vista.guardadas[0].width()} pixels para {vista.pixels_necessarios(0)} na tela"
    vista.parar()


def test_a_grade_desenha_na_altura_do_quadro(app, livro):  # noqa: F811
    """Verificador, 21/10/2026: a grade "Todas as páginas" saía mole (DPI fixo).
    Cada folha sai com a altura, em pixels, que o quadro precisa."""
    from ui.widgets import todas_as_paginas as tp

    recebidas = []
    sinais = tp._Sinais()
    sinais.pronta.connect(lambda folha, img: recebidas.append(img))
    tp._TarefaDasFolhas(str(livro), [0], sinais, altura_px=420).run()
    assert recebidas and recebidas[0].shape[0] >= 400


def _pintado_com_razao(widget, razao: float):
    """O widget pintado numa imagem com `razao` pixels por ponto (como numa tela
    a 125% ou 200%), em numpy cinza."""
    import numpy as np
    from PySide6.QtGui import QImage, QPixmap

    pix = QPixmap(round(widget.width() * razao), round(widget.height() * razao))
    pix.setDevicePixelRatio(razao)
    pix.fill()
    widget.render(pix)
    img = pix.toImage().convertToFormat(QImage.Format_Grayscale8)
    largura, altura = img.width(), img.height()
    dados = np.frombuffer(img.constBits(), dtype=np.uint8, count=img.bytesPerLine() * altura)
    return dados.reshape(altura, img.bytesPerLine())[:, :largura].astype(float)


def test_a_grade_pinta_nitida_na_escala_do_windows(app):  # noqa: F811
    """Verificador, 21/10/2026: a grade "Todas as páginas" continuava mole na
    janela. A imagem guardada tinha o tamanho certo em pixels, mas era reduzida
    ao tamanho em PONTOS e o Qt aumentava de novo pela escala do Windows.
    Mede o que é PINTADO: listras de 1 pixel guardadas no tamanho da tela têm de
    continuar listras (contraste alto entre pixels vizinhos) depois de pintadas
    a 2 pixels por ponto. No jeito antigo viram cinza (falha no f963cfd)."""
    import numpy as np
    from PySide6.QtGui import QImage, QPixmap

    from ui.widgets.todas_as_paginas import ALTURA_DA_PAGINA, ItemDaGrade, _Quadro

    quadro = _Quadro([ItemDaGrade(indice=0, folha=0)], atual=False)
    razao = 2.0
    alt = int(ALTURA_DA_PAGINA * razao)
    larg = int(alt * 0.7)
    listras = np.zeros((alt, larg), dtype=np.uint8)
    listras[:, ::2] = 255                                   # uma coluna branca, uma preta
    imagem = QImage(listras.data, larg, alt, larg, QImage.Format_Grayscale8).copy()
    quadro.definir_pixmap(0, QPixmap.fromImage(imagem))
    quadro.resize(quadro.sizeHint())
    pintado = _pintado_com_razao(quadro.desenho, razao)
    meio = pintado[pintado.shape[0] // 2, pintado.shape[1] // 2 - 40: pintado.shape[1] // 2 + 40]
    contraste = float(np.mean(np.abs(np.diff(meio))))
    assert contraste > 100, f"a página foi pintada mole (contraste entre vizinhos {contraste:.0f})"


# --- O livro aberto "como o UPDF" (22/10/2026) ---------------------------------------
# Conferência de 22/10/2026, quadro "O livro aberto na tela inteira", "Está pior": "Eu não
# consigo ver a página direito, e elas estão de maneira muito ruim, da uma na internet como o
# updf faz. Tem uma pagina maior que outra ali".

RAZAO_DO_WINDOWS = 1.25          # a escala do PC do Samuel


def _pdf_de_ruido(caminho, tamanhos):
    """Um PDF de "scan": cada página coberta por pontinhos cinza (detalhe fino
    que borra se a página for reamostrada) nos tamanhos dados (pontos)."""
    import cv2
    import numpy as np

    rng = np.random.default_rng(7)
    doc = fitz.open()
    for largura, altura in tamanhos:
        pagina = doc.new_page(width=largura, height=altura)
        img = (rng.random((altura * 2, largura * 2)) > 0.5).astype(np.uint8) * 175 + 40
        pagina.insert_image(pagina.rect, stream=cv2.imencode(".png", img)[1].tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


def _esperar_e_pintar(vista, folhas, vezes=40):
    """Pinta o folhear a 125% até as folhas pedidas chegarem (a pintura pede
    as folhas no tamanho de que precisa) e devolve o pintado (cinza)."""
    import time

    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        _pintado_com_razao(vista.viewport(), RAZAO_DO_WINDOWS)
        QApplication.processEvents()
        if all(f in vista.guardadas for f in folhas) and not getattr(vista, "_pedidas", None):
            break
        time.sleep(0.1)
    for _ in range(3):
        _pintado_com_razao(vista.viewport(), RAZAO_DO_WINDOWS)
        QApplication.processEvents()
        time.sleep(0.2)
    QApplication.processEvents()
    return _pintado_com_razao(vista.viewport(), RAZAO_DO_WINDOWS)


def _nitidez(pintado, caminho, indice):
    """A nitidez da página pintada: quanto detalhe fino ela tem (desvio do
    Laplaciano) comparado com a mesma página desenhada pelo MuPDF direto no
    tamanho pintado. 1,0 = tão nítida quanto dá; página reamostrada fica abaixo."""
    import cv2
    import numpy as np

    mascara = ((pintado > 20) & (pintado < 235)).astype(np.uint8)
    n, _r, caixas, _c = cv2.connectedComponentsWithStats(mascara)
    x, y, w, h = max((tuple(caixas[i][:4]) for i in range(1, n)), key=lambda c: c[2] * c[3])
    regiao = pintado[y + 2:y + h - 2, x + 2:x + w - 2]
    doc = fitz.open(str(caminho))
    pagina = doc[indice]
    pix = pagina.get_pixmap(matrix=fitz.Matrix(w / pagina.rect.width, h / pagina.rect.height),
                            colorspace=fitz.csGRAY, alpha=False)
    ref = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)[:h, :w].astype(float)
    doc.close()
    ref = ref[2:h - 2, 2:w - 2]
    return cv2.Laplacian(regiao, cv2.CV_64F).std() / cv2.Laplacian(ref, cv2.CV_64F).std()


def test_o_par_fica_da_mesma_altura_na_tela(app, tmp_path):  # noqa: F811
    """22/10/2026, "Tem uma pagina maior que outra ali": lado a lado, as duas
    páginas do par têm de ser PINTADAS da mesma altura, mesmo com o scan de uma
    maior (antes as duas tinham a mesma largura e a maior saía mais alta).
    Falha no 2eeec20 (562 e 510 pixels)."""
    import numpy as np

    from ui.widgets.paginas_rolando import PaginasRolando

    caminho = _pdf_de_ruido(tmp_path / "par.pdf", [(400, 600), (400, 600), (470, 640), (400, 600)])
    vista = PaginasRolando()
    vista.resize(1100, 700)
    vista.abrir(str(caminho))
    vista.definir_lado_a_lado(True)
    vista.ir_para(1)
    pintado = _esperar_e_pintar(vista, [1, 2])
    vista.parar()
    escuro = (pintado > 20) & (pintado < 235)
    topo = int(np.where(escuro.any(axis=1))[0][0])
    faixa = escuro[topo:]
    colunas = np.where(faixa[:40].any(axis=0))[0]
    esquerda, direita = int(colunas[0]) + 15, int(colunas[-1]) - 15

    def altura(coluna):
        """A maior faixa seguida de página na coluna (o contorno azul da folha
        da vez, a 1 pixel de distância, não entra)."""
        col = np.concatenate([[False], faixa[:, coluna], [False]]).astype(np.int8)
        mudancas = np.flatnonzero(np.diff(col))
        return int(max(mudancas[1::2] - mudancas[0::2]))

    a2, a3 = altura(esquerda), altura(direita)
    assert abs(a2 - a3) <= 1, f"as duas páginas do par pintadas com alturas diferentes: {a2} e {a3} pixels"


def test_o_livro_aberto_pinta_nitido_na_escala_do_windows(app, tmp_path):  # noqa: F811
    """22/10/2026, "Eu não consigo ver a página direito": a página do livro
    aberto tem de ser pintada tão nítida quanto o PDF desenhado direto naquele
    tamanho (nada de desenhar num tamanho e reduzir ou aumentar ao pintar).
    Mede o PINTADO a 125%. Falha no 2eeec20 (0,41; o novo, 0,99)."""
    from ui.widgets.paginas_rolando import PaginasRolando

    caminho = _pdf_de_ruido(tmp_path / "uma.pdf", [(400, 600)] * 3)
    vista = PaginasRolando()
    vista.resize(1100, 700)
    vista.abrir(str(caminho))
    vista.ir_para(0)
    nitidez = _nitidez(_esperar_e_pintar(vista, [0]), caminho, 0)
    vista.parar()
    assert nitidez > 0.9, f"a página do livro aberto foi pintada mole (nitidez {nitidez:.2f})"


def test_a_grade_pinta_nitida_a_125(app, tmp_path):  # noqa: F811
    """Ressalva do verificador (21/10/2026), medida em 22/10: a grade "Todas as
    páginas" a 125% ainda saía mole (a folha guardada 5% maior e reduzida ao
    pintar, e posta meio pixel fora do lugar, o Qt reamostrando). Agora ela é
    guardada na altura exata do quadro e pintada 1 para 1 num pixel inteiro.
    Falha no 2eeec20 (0,89; o novo, 1,18: o MuPDF mais a redução por área
    saem um pouco mais marcados que o MuPDF sozinho)."""
    from PySide6.QtGui import QPixmap

    from ui.widgets import todas_as_paginas as tp
    from ui.widgets.visualizador import numpy_para_qimage

    caminho = _pdf_de_ruido(tmp_path / "grade.pdf", [(400, 600)])
    recebidas = []
    sinais = tp._Sinais()
    sinais.pronta.connect(lambda folha, img: recebidas.append(img))
    grade = tp.TodasAsPaginas()
    # a altura que a grade pede numa tela a 125% (a deste teste não tem escala)
    altura = int(round(grade.altura_necessaria() * RAZAO_DO_WINDOWS / grade.devicePixelRatioF()))
    tp._TarefaDasFolhas(str(caminho), [0], sinais, altura_px=altura).run()
    quadro = tp._Quadro([tp.ItemDaGrade(indice=0, folha=0)], atual=False)
    quadro.definir_pixmap(0, QPixmap.fromImage(numpy_para_qimage(recebidas[0])))
    quadro.resize(quadro.sizeHint())
    nitidez = _nitidez(_pintado_com_razao(quadro.desenho, RAZAO_DO_WINDOWS), caminho, 0)
    assert nitidez > 0.97, f"a grade foi pintada mole (nitidez {nitidez:.2f})"


def test_os_jeitos_de_caber_e_de_mostrar(app, tmp_path):  # noqa: F811
    """Os quatro jeitos de caber e o rolar sem parar (como no UPDF, 22/10/2026)."""
    from ui.widgets import paginas_rolando as pr

    caminho = _pdf_de_ruido(tmp_path / "jeitos.pdf", [(400, 600)] * 6)
    vista = pr.PaginasRolando()
    vista.resize(1000, 700)
    vista.abrir(str(caminho))
    livre = vista.maximumViewportSize()
    barra = vista.style().pixelMetric(vista.style().PixelMetric.PM_ScrollBarExtent)

    vista.definir_jeito(caber=pr.CABER_PAGINA)
    r = dict(vista.retangulos_exatos())[0]
    assert abs(r.height() - (livre.height() - 2 * pr.MARGEM)) < 1 and r.width() < livre.width(), \
        "Caber a página: a página inteira na tela"
    vista.definir_jeito(caber=pr.CABER_LARGURA)
    r = dict(vista.retangulos_exatos())[0]
    assert abs(r.width() - (livre.width() - barra - 2 * pr.MARGEM)) < 1, "Caber a largura"
    vista.definir_jeito(caber=pr.CABER_ALTURA)
    r = dict(vista.retangulos_exatos())[0]
    assert abs(r.height() - (livre.height() - barra - 2 * pr.MARGEM)) < 1, "Caber a altura"
    vista.definir_jeito(caber=pr.TAMANHO_REAL)
    r = dict(vista.retangulos_exatos())[0]
    assert abs(r.height() - 600 * vista.logicalDpiY() / 72) < 1, "Tamanho real: 100%"

    # sem rolar: só a página da vez; o passo pula de par em par
    vista.definir_jeito(continuo=False, caber=pr.CABER_PAGINA)
    vista.ir_para(3)
    assert [i for i, _r in vista.retangulos()] == [3]
    vista.definir_jeito(mostrar=pr.DUAS)
    assert sorted(i for i, _r in vista.retangulos()) == [3, 4]
    assert vista.passo(1) == 5 and vista.passo(-1) == 1
    vista.ir_para(0)
    assert [i for i, _r in vista.retangulos()] == [0], "a 1 sozinha"
    vista.parar()


def test_a_escolha_fica_para_o_proximo_livro(app, monkeypatch):  # noqa: F811
    """A barra de baixo do livro aberto lembra o jeito escolhido
    (configuracoes.json, "livro_aberto"), e valor estranho volta ao de fábrica."""
    import configuracoes
    from ui.tela_inicio import LivroAberto

    guardado = {}
    monkeypatch.setattr(configuracoes, "ler", lambda chave: guardado.get(chave))
    monkeypatch.setattr(configuracoes, "escrever", lambda chave, valor: guardado.__setitem__(chave, valor))

    class _Tela:
        def __getattr__(self, _nome):
            return lambda *a, **k: None

    livro = LivroAberto(_Tela())
    assert livro.jeito_guardado() == {"mostrar": "uma", "rolar": True, "caber": "pagina"}, "de fábrica"
    livro._aplicar_jeito(livro.jeito_guardado())
    livro.botoes_mostrar["duas"].click()
    livro.botoes_caber["largura"].click()
    livro.botao_rolar.click()
    assert guardado["livro_aberto"] == {"mostrar": "duas", "rolar": False, "caber": "largura"}
    outro = LivroAberto(_Tela())
    assert outro.jeito_guardado() == guardado["livro_aberto"]
    guardado["livro_aberto"] = {"mostrar": "tres", "rolar": "sim", "caber": 7}
    assert outro.jeito_guardado() == {"mostrar": "uma", "rolar": True, "caber": "pagina"}
    assert configuracoes.PADROES["livro_aberto"] == LivroAberto.DE_FABRICA
