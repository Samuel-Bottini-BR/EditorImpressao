"""Provas da D-574: ver o livreto pronto no "Montar para imprimir".

PALAVRAS DO SAMUEL (docs/plano/DECISOES.md, D-574)
    28/10/2026: "eu deveria conseguir ver o livreto pronto aqui nessa tela para
    que eu possa ver se ficou certo". 31/10/2026, na Central, ele escolheu a
    "Opção 1: as folhas como saem da impressora, frente e verso": "À direita, a
    folha A4 deitada como vai sair: "Folha 1 de 32 — frente" e embaixo o verso,
    com setas para passar as 32 folhas. [...] Caso real: Palatino, folha 1:
    frente com as páginas 20 e 1, verso com a 2 (em branco) e a 19."

O QUE SE PROVA (comportamento, não aparência)
    - a folha 1 da prévia: frente com as páginas 20 e 1, verso com a 2 e a 19
      (Livreto A4, 20 por caderno), IGUAL à folha 1 do PDF gravado (D-473: a
      prévia sai da mesma montagem);
    - a janela mostra isso sozinha, com "Folha 1 de N — frente/verso";
    - as setas passam as folhas;
    - trocar uma opção refaz a prévia;
    - a janela não congela enquanto monta (fio à parte, bolinha girando);
    - uma folha por vez na memória (CLAUDE.md §3);
    - fora do Livreto a janela fica como estava (só o texto).
Todas falham no código antigo (a janela só tinha o texto "O que vai sair" e o
core não tinha previa_da_folha).

O LIVRO DE TESTE: sintético, 40 páginas A5, cada página pintada com um cinza
próprio (página n = 5 * n), para saber pelo desenho qual página caiu em cada
metade da folha. A conferência com o Palatino de verdade fica nos prints
(relatorios/livreto-ver/), porque o PDF dele (172 MB) não vai para o git.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core import impressao as imp  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import app, pasta  # noqa: F401, E402 - fixtures

MM = 72 / 25.4
PASSO_DO_CINZA = 5


def _livro(caminho, n=40):
    """Livro de n páginas A5; a página k é toda pintada de cinza 5*k."""
    doc = fitz.open()
    for k in range(1, n + 1):
        pagina = doc.new_page(width=148 * MM, height=210 * MM)
        cor = PASSO_DO_CINZA * k / 255
        pagina.draw_rect(pagina.rect, color=(cor, cor, cor), fill=(cor, cor, cor))
    doc.save(str(caminho))
    doc.close()
    return caminho


def _qual_pagina(metade: np.ndarray) -> int | None:
    """A página pintada numa metade da folha (cinza), ou None se branca."""
    pintado = metade < 250
    if pintado.sum() < 20:
        return None
    return round(float(np.median(metade[pintado])) / PASSO_DO_CINZA)


def _paginas_da_face(cinza: np.ndarray) -> tuple:
    meio = cinza.shape[1] // 2
    return _qual_pagina(cinza[:, :meio]), _qual_pagina(cinza[:, meio:])


def _cinza_da_face(face: imp.FaceDaPrevia) -> np.ndarray:
    pontos = np.frombuffer(face.amostras, np.uint8).reshape(face.altura, face.largura, face.canais)
    return pontos.mean(axis=2) if face.canais == 3 else pontos[:, :, 0].astype(float)


def _cinza_do_rotulo(rotulo) -> np.ndarray:
    """O desenho que está de fato na tela (QLabel), em cinza."""
    imagem = rotulo.pixmap().toImage().convertToFormat(QImage.Format.Format_Grayscale8)
    largura, altura = imagem.width(), imagem.height()
    linha = imagem.bytesPerLine()
    dados = np.frombuffer(imagem.constBits(), np.uint8, count=linha * altura)
    return dados.reshape(altura, linha)[:, :largura].astype(float)


def _opcoes_livreto(**mudar) -> imp.OpcoesDeImpressao:
    o = imp.OpcoesDeImpressao()
    o.formato = imp.LIVRETO
    o.paginas_por_caderno = 20
    for nome, valor in mudar.items():
        setattr(o, nome, valor)
    return o


def _esperar(condicao, segundos=60.0) -> bool:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return False


def _dialogo(caminho, **mudar):
    """A janela com as opções escolhidas e a prévia da folha 1 já à vista."""
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(caminho))
    dialogo.definir_opcoes(_opcoes_livreto(**mudar))
    dialogo.show()
    assert _esperar(lambda: _previa_quieta(dialogo)), "a prévia não apareceu"
    return dialogo


def _previa_quieta(dialogo) -> bool:
    """A prévia terminou: nada agendado, nenhum fio montando, folha à vista."""
    return (not dialogo._relogio_da_previa.isActive()
            and not (dialogo.tarefa_previa is not None and dialogo.tarefa_previa.isRunning())
            and not dialogo._previa_pendente
            and not dialogo.bolinha_da_previa.carregando       # a resposta já chegou
            and dialogo.folha_na_tela is not None)


def _paginas_na_tela(dialogo) -> dict:
    return {lado: _paginas_da_face(_cinza_do_rotulo(dialogo.imagens_da_face[lado]))
            for lado in (imp.FRENTE, imp.VERSO) if dialogo.imagens_da_face[lado].isVisible()}


# --------------------------------------------------------------- o core: mesma montagem do PDF

def test_d574_folha_1_frente_20_e_1_verso_2_e_19_igual_ao_pdf(pasta):
    """D-574, "Caso real: Palatino, folha 1: frente com as páginas 20 e 1,
    verso com a 2 (em branco) e a 19". A prévia sai da mesma montagem do
    arquivo (D-473): os pontos da prévia e da folha 1 do PDF gravado batem."""
    entrada = _livro(pasta / "livro.pdf")
    opcoes = _opcoes_livreto()
    folha = imp.previa_da_folha(entrada, opcoes, 0, 300)
    assert (folha.numero, folha.total, folha.posicao, folha.quantas) == (1, 10, 0, 10)
    assert [f.lado for f in folha.faces] == [imp.FRENTE, imp.VERSO]
    assert _paginas_da_face(_cinza_da_face(folha.faces[0])) == (20, 1)
    assert _paginas_da_face(_cinza_da_face(folha.faces[1])) == (2, 19)

    # o PDF gravado de verdade (com "Imprimir como imagem", como sai de fábrica)
    saida = pasta / "para imprimir.pdf"
    imp.montar_para_impressao(entrada, saida, opcoes)
    with fitz.open(str(saida)) as pdf:
        for n, face in enumerate(folha.faces):
            zoom = face.largura / pdf[n].rect.width
            pix = pdf[n].get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB,
                                    alpha=False)
            assert (pix.width, pix.height) == (face.largura, face.altura)
            do_pdf = np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.stride)[:, :pix.width * 3].reshape(pix.height, pix.width, 3)
            da_previa = np.frombuffer(face.amostras, np.uint8).reshape(face.altura, face.largura, 3)
            diferenca = np.abs(do_pdf.astype(int) - da_previa.astype(int))
            assert diferenca.mean() < 2.0, f"face {n}: a prévia não é o PDF ({diferenca.mean():.2f})"


def test_d574_folhas_que_saem_seguem_de_ate_e_reverter():
    """As folhas da prévia são as que saem: "Folhas de/até" e "Reverter páginas"."""
    assert imp.folhas_que_saem(126, _opcoes_livreto()) == (list(range(1, 33)), 32)  # Palatino
    assert imp.folhas_que_saem(40, _opcoes_livreto(folhas_de=3, folhas_ate=5)) == ([3, 4, 5], 10)
    assert imp.folhas_que_saem(40, _opcoes_livreto(reverter=True))[0][:2] == [10, 9]


# --------------------------------------------------------------- a janela

def test_d574_janela_mostra_a_folha_1_frente_e_verso(app, pasta):
    """A janela mostra sozinha, à direita, "Folha 1 de 10 — frente" com as
    páginas 20 e 1 e embaixo "— verso" com a 2 e a 19 (o desenho na tela)."""
    dialogo = _dialogo(_livro(pasta / "livro.pdf"))
    assert dialogo.bloco_da_previa.isVisible()
    assert dialogo.rotulos_da_face[imp.FRENTE].text() == "Folha 1 de 10 — frente"
    assert dialogo.rotulos_da_face[imp.VERSO].text() == "Folha 1 de 10 — verso"
    assert _paginas_na_tela(dialogo) == {imp.FRENTE: (20, 1), imp.VERSO: (2, 19)}
    assert dialogo.rotulo_da_folha.text() == "folha 1"
    # o texto de antes continua embaixo (nada saiu, D-315)
    assert "Livreto (cadernos) em papel A4" in dialogo.resumo.text()
    dialogo.reject()


def test_d574_setas_passam_as_folhas(app, pasta):
    """As setas passam as folhas: ">" vai à folha 2 (frente 18 e 3, verso 4 e
    17); "<" volta à 1; na primeira a "<" fica apagada, na última a ">"."""
    dialogo = _dialogo(_livro(pasta / "livro.pdf"))
    assert not dialogo.botao_folha_anterior.isEnabled()
    dialogo.botao_folha_seguinte.click()
    assert _esperar(lambda: _previa_quieta(dialogo) and dialogo.folha_na_tela.numero == 2)
    assert dialogo.rotulos_da_face[imp.FRENTE].text() == "Folha 2 de 10 — frente"
    assert _paginas_na_tela(dialogo) == {imp.FRENTE: (18, 3), imp.VERSO: (4, 17)}
    assert dialogo.botao_folha_anterior.isEnabled()
    dialogo.botao_folha_anterior.click()
    assert _esperar(lambda: _previa_quieta(dialogo) and dialogo.folha_na_tela.numero == 1)
    assert _paginas_na_tela(dialogo) == {imp.FRENTE: (20, 1), imp.VERSO: (2, 19)}
    # até a última (folha 10, a do meio do segundo caderno)
    for numero in range(2, 11):
        dialogo.botao_folha_seguinte.click()
        assert _esperar(lambda: _previa_quieta(dialogo) and dialogo.folha_na_tela.numero == numero)
    assert dialogo.folha_na_tela.numero == 10
    assert not dialogo.botao_folha_seguinte.isEnabled()
    dialogo.reject()


def test_d574_trocar_a_opcao_refaz_a_previa(app, pasta):
    """Trocar "Páginas por caderno" de 20 para 8 refaz a folha 1: frente com
    a 8 e a 1. Trocar a encadernação para "Direita" troca os lados (1 e 8)."""
    dialogo = _dialogo(_livro(pasta / "livro.pdf"))
    dialogo.combo_caderno.setCurrentIndex(dialogo.combo_caderno.findData(8))
    assert _esperar(lambda: _previa_quieta(dialogo)
                    and _paginas_na_tela(dialogo).get(imp.FRENTE) == (8, 1))
    assert _paginas_na_tela(dialogo)[imp.VERSO] == (2, 7)
    dialogo.combo_encadernacao.setCurrentIndex(dialogo.combo_encadernacao.findData(imp.DIREITA))
    assert _esperar(lambda: _previa_quieta(dialogo)
                    and _paginas_na_tela(dialogo).get(imp.FRENTE) == (1, 8))
    # "Só a frente": só a frente aparece
    dialogo.combo_lados.setCurrentIndex(dialogo.combo_lados.findData(imp.SO_FRENTE))
    assert _esperar(lambda: _previa_quieta(dialogo)
                    and not dialogo.imagens_da_face[imp.VERSO].isVisible())
    assert list(_paginas_na_tela(dialogo)) == [imp.FRENTE]
    dialogo.reject()


def test_d574_janela_nao_congela_enquanto_monta(app, pasta, monkeypatch):
    """CLAUDE.md §3 ("Interface nunca congela"): a folha é montada num fio à
    parte. Com a montagem demorando 1,5 s, o relógio da tela continua batendo,
    a bolinha (D-064) gira e o pedido volta na hora."""
    entrada = _livro(pasta / "livro.pdf")
    original = imp.previa_da_folha

    def devagar(*a, **k):
        time.sleep(1.5)
        return original(*a, **k)

    monkeypatch.setattr(imp, "previa_da_folha", devagar)
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(entrada))
    dialogo.definir_opcoes(_opcoes_livreto())
    dialogo.show()
    batidas = []
    relogio = QTimer()
    relogio.timeout.connect(lambda: batidas.append(time.monotonic()))
    relogio.start(20)
    inicio = time.monotonic()
    dialogo.pedir_previa()
    assert time.monotonic() - inicio < 0.3, "pedir a folha parou a janela"
    assert dialogo.bolinha_da_previa.carregando
    assert _esperar(lambda: _previa_quieta(dialogo), 30)
    relogio.stop()
    assert not dialogo.bolinha_da_previa.carregando
    assert len(batidas) >= 30, f"a janela parou: só {len(batidas)} batidas em 1,5 s"
    assert max(np.diff(batidas)) < 0.5
    dialogo.reject()


def test_d574_uma_folha_por_vez_na_memoria(app, pasta, monkeypatch):
    """CLAUDE.md §3: cada pedido monta UMA folha, e a janela guarda só a que
    está à vista (passar as 10 folhas não junta nada)."""
    entrada = _livro(pasta / "livro.pdf")
    pedidos = []
    original = imp.previa_da_folha

    def contar(arquivo, opcoes, posicao, *a, **k):
        pedidos.append(posicao)
        return original(arquivo, opcoes, posicao, *a, **k)

    monkeypatch.setattr(imp, "previa_da_folha", contar)
    dialogo = _dialogo(entrada)
    for _ in range(9):
        dialogo.passar_folha(1)
        assert _esperar(lambda: _previa_quieta(dialogo))
    folha = dialogo.folha_na_tela
    assert folha.numero == 10 and len(folha.faces) == 2
    guardadas = [v for v in vars(dialogo).values()
                 if isinstance(v, imp.FolhaDaPrevia)
                 or (isinstance(v, (list, tuple, dict)) and any(
                     isinstance(x, imp.FolhaDaPrevia) for x in (v.values() if isinstance(v, dict) else v)))]
    assert guardadas == [folha]
    assert pedidos[-9:] == list(range(1, 10))
    dialogo.reject()


def test_d574_fora_do_livreto_fica_como_estava(app, pasta):
    """Só no Livreto (é o formato da D-574). "Página inteira": a parte da
    prévia some e o texto "O que vai sair" continua."""
    dialogo = _dialogo(_livro(pasta / "livro.pdf"))
    dialogo.combo_formato.setCurrentIndex(dialogo.combo_formato.findData(imp.PAGINA_INTEIRA))
    QApplication.processEvents()
    assert not dialogo.bloco_da_previa.isVisible()
    assert dialogo.folha_na_tela is None
    assert dialogo.resumo.isVisible()
    dialogo.combo_formato.setCurrentIndex(dialogo.combo_formato.findData(imp.LIVRETO))
    assert _esperar(lambda: _previa_quieta(dialogo))
    assert dialogo.bloco_da_previa.isVisible()
    dialogo.reject()


def test_d574_gravar_com_a_previa_montando_espera_e_grava(app, pasta):
    """Apertar "gravar" enquanto a folha ainda monta: a prévia para, o arquivo
    é gravado (um fio do MuPDF por vez) e a prévia volta depois."""
    entrada = _livro(pasta / "livro.pdf")
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(entrada))
    dialogo.definir_opcoes(_opcoes_livreto(como_imagem=False))
    dialogo.show()
    dialogo.pedir_previa()
    destino = pasta / "saida.pdf"
    dialogo.comecar(destino=str(destino))
    assert _esperar(lambda: dialogo.tarefa is not None and not dialogo.tarefa.isRunning()
                    and "Pronto" in dialogo.estado.text(), 60)
    assert destino.exists()
    # o resultado mora embaixo da folha: o cartão rola até ele (à vista)
    assert _esperar(lambda: not dialogo.estado.visibleRegion().isEmpty(), 5)
    assert _esperar(lambda: _previa_quieta(dialogo), 60)
    assert _paginas_na_tela(dialogo)[imp.FRENTE] == (20, 1)
    dialogo.reject()
