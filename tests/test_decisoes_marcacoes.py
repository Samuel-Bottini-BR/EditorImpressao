"""Provas de comportamento do botão "marcações" da barra de baixo (D-578 e D-580, 29/10/2026).

D-578 (Samuel, 29/10/2026, testando o Automático): "um bug que acontece quando nós usamos o
automatico, de vez as paginas mudarem, elas continuam iguais, mas o que aparece são as marcações
feitas no pdf, de gravura e de letras, tem que ter um jeito de aparecer e desaparecer essas
marcações nas paginas." · "não tem nenhuma opção de marcação escolhida, está o zoom escolhido".
Prints: relatorios/testes-guiados/2026-10-29-automatico/a-01, a-02, a-03 (pasta principal).

D-580 (Samuel, 29/10/2026, "A"): "A — Na barra de baixo, começando escondido. O botão "marcações"
fica ao lado de "Uma página / Duas lado a lado / antes / depois". Com qualquer ferramenta, até com o
Zoom, a página aparece limpa, como vai sair. Um clique mostra as cores e outro esconde."

O DEFEITO: a vista da página (ui/widgets/editor_selecao.EditorSelecao, a mesma do Zoom, da Mão e das
ferramentas de marcar) pintava SEMPRE o colorido de toda a marcação (letra azul, gravura salmão,
papel verde) e o contorno das feitas à mão. Depois do Automático a página inteira fica marcada, e a
imagem sumia debaixo das cores.

COMO SE PROVA: pelos PIXELS que o widget pinta (grab() sem janela na tela, tests/conftest.py), não
por um atributo. "Pixel colorido" = um pixel em que os três canais diferem (a página do teste é
cinza ou branca com letra preta; as cores das marcações não são cinza).

REVERSÃO (CLAUDE.md §4.7): no código antigo (commit ac0b9ec) os testes deste arquivo FALHAM na
primeira conferência ("com o Zoom, nada do colorido"), porque o colorido era sempre pintado; a
saída da rodada no código antigo está em relatorios/automatico-marcacoes/ONDE-PAREI.md.

Também conferido aqui, porque não pode quebrar: D-237 ("mas quando eu quiser ver as areas achadas,
deve ter um botão ou aba para eu fazer isso [...] no para revisar, elas já vão aparecer laranjas"):
o contorno laranja da caixinha "Mostrar as áreas achadas" continua aparecendo com "marcações"
desligado; e o traço que está sendo desenhado continua aparecendo enquanto se desenha.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core.selecao import (  # noqa: E402
    AUTOMATICO,
    GRAVURA,
    LETRA,
    MAO,
    PAPEL,
    RETANGULO,
    Regiao,
    Selecao,
)
from tests.ajudante_do_automatico import rodar_como_o_conferir  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    app,
    janela,
    pasta,
)


# --- ajudantes ------------------------------------------------------------------------------------

def _assentar(vezes: int = 6) -> None:
    for _ in range(vezes):
        QApplication.processEvents()


def _rgb(widget) -> np.ndarray:
    """O que o widget pinta agora, como matriz RGB (altura x largura x 3)."""
    imagem = widget.grab().toImage().convertToFormat(QImage.Format_RGB888)
    largura, altura = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(altura, imagem.bytesPerLine())
    return dados[:, :largura * 3].reshape(altura, largura, 3).copy()


def _coloridos_na_pagina(editor) -> int:
    """Quantos pixels DENTRO da página (editor._area) têm cor (canais diferentes). A página do
    teste é cinza/branca com letra preta: sem as marcações, quase nenhum."""
    rgb = _rgb(editor).astype(np.int16)
    area = editor._area
    pedaco = rgb[area.top():area.bottom(), area.left():area.right()]
    diferenca = pedaco.max(axis=2) - pedaco.min(axis=2)
    return int((diferenca > 25).sum())


def _laranja_das_achadas(editor) -> int:
    """Pixels do contorno laranja das áreas achadas (COR_DAS_ACHADAS = 255, 140, 0)."""
    rgb = _rgb(editor).astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return int(((r > 220) & (g > 100) & (g < 180) & (b < 60)).sum())


def _marcacao_da_maquina() -> Selecao:
    """Como fica uma página depois do Automático: gravura, letra e papel achados pela máquina."""
    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(0.02, 0.02), (0.98, 0.98)],
                               origem=AUTOMATICO))
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.9, 0.5)],
                               origem=AUTOMATICO))
    selecao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[(0.1, 0.6), (0.9, 0.9)],
                               origem=AUTOMATICO))
    return selecao


# --- no editor da página, sozinho -----------------------------------------------------------------

def test_d578_d580_com_o_zoom_a_pagina_aparece_limpa_e_marcacoes_mostra_e_esconde(app):
    """D-578 + D-580, no próprio editor da página: página marcada pela máquina, ferramenta Zoom →
    nenhum pixel colorido (de fábrica escondido). Ligar "marcações" → o colorido aparece.
    Desligar → some de novo. FALHA no código antigo (ac0b9ec): lá o colorido era sempre pintado."""
    from ui.widgets.editor_selecao import FERRAMENTA_ZOOM, EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 560)
    editor.definir_imagem(np.full((560, 400, 3), 230, np.uint8))
    editor.definir_selecao(_marcacao_da_maquina())
    editor.definir_ferramenta(FERRAMENTA_ZOOM)

    limpa = _coloridos_na_pagina(editor)
    assert limpa < 50, f"com o Zoom a página ainda aparece pintada ({limpa} pixels coloridos)"

    editor.definir_mostrar_marcacao(True)
    com_cores = _coloridos_na_pagina(editor)
    assert com_cores > 20000, f"ligado, o colorido não apareceu ({com_cores} pixels)"

    editor.definir_mostrar_marcacao(False)
    de_novo = _coloridos_na_pagina(editor)
    assert de_novo < 50, f"desligado de novo, o colorido não sumiu ({de_novo} pixels)"


@pytest.mark.parametrize("ferramenta", ["mao", "pincel", "retangulo", "varinha", "ajustar"])
def test_d580_com_qualquer_ferramenta_a_pagina_aparece_limpa(app, ferramenta):
    """D-580: "Com qualquer ferramenta, até com o Zoom, a página aparece limpa". Também o contorno
    das feitas à mão (etapa 9b-2, lista 1.9) fica escondido."""
    from ui.widgets.editor_selecao import EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 560)
    editor.definir_imagem(np.full((560, 400, 3), 230, np.uint8))
    selecao = _marcacao_da_maquina()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.3, 0.3), (0.7, 0.45)],
                               origem=MAO))
    editor.definir_selecao(selecao)
    editor.definir_ferramenta(ferramenta)
    assert _coloridos_na_pagina(editor) < 50, ferramenta
    editor.definir_mostrar_marcacao(True)
    assert _coloridos_na_pagina(editor) > 20000, ferramenta


def test_d580_o_traco_em_andamento_e_o_laranja_das_achadas_continuam(app):
    """Detalhes fixados pela gerente para a D-580, e a D-237: com "marcações" desligado, (1) o
    contorno laranja de "Mostrar as áreas achadas" continua aparecendo (D-237: "apertar nele e
    mostrar as areas achadas delineadas"); (2) o traço que a pessoa está desenhando continua
    aparecendo enquanto desenha (a pista visual da ferramenta)."""
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO, EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 560)
    editor.definir_imagem(np.full((560, 400, 3), 230, np.uint8))
    editor.definir_selecao(_marcacao_da_maquina())
    assert not editor.mostrar_marcacao
    assert _laranja_das_achadas(editor) == 0
    editor.definir_mostrar_achadas(True)
    assert _laranja_das_achadas(editor) > 200, "o laranja das áreas achadas sumiu (D-237)"
    editor.definir_mostrar_achadas(False)

    # o traço em andamento (o retângulo sendo arrastado), sem soltar o mouse
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.grab()                                   # calcula a área da página na tela
    editor._desenhando = True
    editor._pontos = [(0.2, 0.2), (0.8, 0.4)]
    assert _coloridos_na_pagina(editor) > 100, "o traço em andamento não aparece"
    editor._desenhando = False
    editor._pontos = []
    assert _coloridos_na_pagina(editor) < 50


# --- na janela de verdade, pelo botão da barra de baixo -------------------------------------------

def _abrir_marcado(janela, pasta):
    """Abre um livro, roda o Automático (rápido) e põe na página 2 a marcação que a máquina
    deixa (gravura, letra, papel), como se a etapa de gravuras e fotos tivesse rodado."""
    janela.abrir_livro(str(_pdf(pasta, folhas=3)))
    rodar_como_o_conferir(janela, sempre=True, detectar_regioes=False, dividir_folhas=False,
                          cortar_bordas=False, endireitar=False, limpar=False)
    janela.resize(1280, 657)
    janela.show()
    _assentar()
    tela = janela.tela_conferir
    for pagina in janela.projeto.paginas:
        pagina.guardar_selecao(_marcacao_da_maquina(), provisoria=False)
    return tela


def _esperar_a_pagina(tela, segundos: float = 30.0) -> None:
    """Espera a prévia da página chegar ao editor (sem ela não há o que pintar)."""
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar()
        editor = tela.editor_selecao
        if editor._pixmap is not None and not editor._pixmap.isNull() and editor.isVisible():
            return
        time.sleep(0.05)
    raise AssertionError("a página não apareceu no editor")


def test_d578_d580_o_botao_marcacoes_da_barra_de_baixo(janela, pasta):
    """D-578 + D-580 na janela de verdade: livro marcado pela máquina, ferramenta Zoom → a página
    aparece sem cores (de fábrica escondido); o botão "marcações" da barra de baixo, ao lado de
    "antes / depois", liga (cores) e desliga (some). O estado vale para as outras páginas e não é
    gravado no projeto. FALHA no código antigo (ac0b9ec) já na primeira conferência."""
    tela = _abrir_marcado(janela, pasta)
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(1)
    _esperar_a_pagina(tela)
    editor = tela.editor_selecao
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem      # "Uma página"

    limpa = _coloridos_na_pagina(editor)
    assert limpa < 300, f"com o Zoom a página aparece pintada ({limpa} pixels coloridos; D-578)"

    botao = tela.botao_marcacoes
    assert botao.text() == "marcações"
    assert botao.isCheckable() and not botao.isChecked(), "de fábrica tem de vir desligado"
    assert botao.objectName() == tela.botao_antes_depois.objectName(), "estilo diferente dos vizinhos"
    assert botao.parentWidget() is tela.botao_antes_depois.parentWidget(), "fora da barra de baixo"
    assert botao.isEnabled()
    antes = [list(p.selecao) for p in janela.projeto.paginas]

    botao.click()
    _assentar()
    com_cores = _coloridos_na_pagina(editor)
    assert botao.isChecked()
    assert com_cores > 20000, f"ligado, o colorido não apareceu ({com_cores} pixels)"

    # vale para as outras páginas
    tela.ir_para_pagina(2)
    _esperar_a_pagina(tela)
    assert _coloridos_na_pagina(editor) > 20000, "na página seguinte as cores voltaram a sumir"

    botao.click()
    _assentar()
    assert not botao.isChecked()
    assert _coloridos_na_pagina(editor) < 300, "desligado, o colorido não sumiu"
    tela.ir_para_pagina(1)
    _esperar_a_pagina(tela)
    assert _coloridos_na_pagina(editor) < 300

    # nada muda na marcação das páginas (nada gravado no projeto, nada muda no PDF)
    assert [list(p.selecao) for p in janela.projeto.paginas] == antes


def test_d237_com_marcacoes_desligado_a_caixinha_ainda_mostra_o_laranja(janela, pasta):
    """D-237 não pode quebrar: com "marcações" desligado, a caixinha "Mostrar as áreas achadas"
    continua desenhando o contorno laranja das áreas da máquina, sem o colorido."""
    tela = _abrir_marcado(janela, pasta)
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(1)
    _esperar_a_pagina(tela)
    editor = tela.editor_selecao
    assert not tela.botao_marcacoes.isChecked()
    assert _laranja_das_achadas(editor) == 0
    tela.caixa_mostrar_achadas.setChecked(True)
    _assentar()
    assert _laranja_das_achadas(editor) > 200, "o laranja das áreas achadas sumiu (D-237)"
    tela.caixa_mostrar_achadas.setChecked(False)
    _assentar()
    assert _laranja_das_achadas(editor) == 0


# --- D-584: as ferramentas de marcar ligam as marcações sozinhas -------------------------------------
#
# D-584 (Samuel, 29/10/2026, "a"): "A — O botão liga sozinho ao escolher uma ferramenta de marcar
# (Retângulo, Laço, Pincel, Varinha...) e desliga sozinho ao voltar para o Zoom ou a Mão. Quem marca
# sempre vê o que está marcando; quem só olha a página vê ela limpa."
# REVERSÃO: no commit abbb0d3 (D-580 sem a D-584) estes testes FALHAM: escolher o Pincel não liga.

FERRAMENTAS_DE_MARCAR = ["retangulo", "elipse", "laco", "poligono", "pincel", "varinha", "cor",
                         "ajustar"]


def test_d584_pincel_liga_zoom_desliga_e_o_clique_ainda_esconde(janela, pasta):
    """D-584 na janela de verdade, pelos pixels: Pincel → colorido pintado e botão aceso; Zoom →
    nada pintado e botão apagado; de novo o Pincel e um clique no botão → some, e fica desligado
    até trocar de ferramenta (outra de marcar liga de novo)."""
    tela = _abrir_marcado(janela, pasta)
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(1)
    _esperar_a_pagina(tela)
    editor, botao = tela.editor_selecao, tela.botao_marcacoes
    assert not botao.isChecked() and _coloridos_na_pagina(editor) < 300

    tela.escolher_ferramenta("pincel")
    _assentar()
    assert botao.isChecked(), "escolher o Pincel não acendeu o botão (D-584)"
    assert _coloridos_na_pagina(editor) > 20000, "com o Pincel as marcações não aparecem (D-584)"

    tela.escolher_ferramenta("zoom")
    _assentar()
    assert not botao.isChecked(), "voltar ao Zoom não apagou o botão (D-584)"
    assert _coloridos_na_pagina(editor) < 300

    tela.escolher_ferramenta("pincel")
    _assentar()
    botao.click()                                   # a pessoa esconde com o Pincel na mão
    _assentar()
    assert not botao.isChecked() and _coloridos_na_pagina(editor) < 300
    tela.ir_para_pagina(2)                          # fica desligado (não é troca de ferramenta)
    _esperar_a_pagina(tela)
    assert not botao.isChecked() and _coloridos_na_pagina(editor) < 300
    tela.escolher_ferramenta("laco")                # trocar de ferramenta de marcar liga de novo
    _assentar()
    assert botao.isChecked() and _coloridos_na_pagina(editor) > 20000


@pytest.mark.parametrize("ferramenta", FERRAMENTAS_DE_MARCAR)
def test_d584_toda_ferramenta_de_marcar_liga_e_a_mao_desliga(janela, pasta, ferramenta):
    """D-584: todas as ferramentas que pintam ou mexem na marcação (a lista FERRAMENTAS do editor
    menos o Zoom e a Mão) acendem "marcações"; a Mão apaga."""
    from ui.widgets.editor_selecao import FERRAMENTAS, FERRAMENTAS_DE_NAVEGACAO

    assert sorted(FERRAMENTAS_DE_MARCAR) == sorted(
        f for f in FERRAMENTAS if f not in FERRAMENTAS_DE_NAVEGACAO), "a lista do editor mudou"
    tela = _abrir_marcado(janela, pasta)
    tela.escolher_ferramenta("mao")
    assert not tela.botao_marcacoes.isChecked()
    tela.escolher_ferramenta(ferramenta)
    assert tela.botao_marcacoes.isChecked(), ferramenta
    assert tela.editor_selecao.mostrar_marcacao, ferramenta
    tela.escolher_ferramenta("mao")
    assert not tela.botao_marcacoes.isChecked() and not tela.editor_selecao.mostrar_marcacao


def test_d580_d584_abrir_outro_livro_o_editor_novo_segue_o_botao(janela, pasta):
    """D-580 ("vale para todas as páginas e livros"): o editor da página nasce de novo a cada livro
    aberto (_montar_aba_marcar). O editor novo tem de seguir o botão (antes ficava com as cores
    escondidas embaixo de um botão aceso). Abrir um livro não é "escolher" ferramenta (D-584):
    o botão fica como estava."""
    tela = _abrir_marcado(janela, pasta)
    tela.escolher_ferramenta("zoom")
    tela.botao_marcacoes.click()                    # ligado à mão (não depende da D-584)
    assert tela.botao_marcacoes.isChecked() and tela.editor_selecao.mostrar_marcacao
    outro = pasta / "livros" / "Outro Livro.pdf"      # outro arquivo de verdade (outra assinatura)
    doc = fitz.open()
    for i in range(2):
        doc.new_page(width=400, height=560).insert_text((40, 60), f"outro livro {i}", fontsize=14)
    doc.save(str(outro))
    doc.close()
    janela.abrir_livro(str(outro))
    _assentar()
    tela = janela.tela_conferir
    assert tela.botao_marcacoes.isChecked()
    assert tela.editor_selecao.mostrar_marcacao == tela.botao_marcacoes.isChecked(), \
        "o editor do livro novo não segue o botão"
