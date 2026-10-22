"""Item 2.18: mudar à mão as áreas de gravura (core/editar_zonas.py e o editor).

Decisões do Samuel testadas (ficha memoria/itens/2.18.md):
- P11b "Clicar numa área que o programa já marcou e apagar ou pintar de branco";
- P11 (a) "'Pintar por cima' e 'Tinta com a cor original, papel branco', mais
  copiar, colar e mover zona"; TINTA3 "Tinta preta, fundo original";
- rodadas 4 e 5: as áreas achadas delineadas e mudar o tamanho ("Os dois":
  quadradinhos e pincel somar/tirar).
Testes de máquina; nenhuma janela aparece na tela.
"""

from __future__ import annotations

import numpy as np
import pytest

from core import editar_zonas as ez
from core.selecao import (AUTOMATICO, GRAVURA, MAO, PAPEL, PINTAR, SUBTRAIR, TINTA_COR,
                          TINTA_PRETA, Regiao, Selecao, retangulo, traco)


def test_escolher_a_area_no_ponto_a_de_cima_primeiro():
    sel = Selecao([retangulo(0.1, 0.1, 0.5, 0.5, origem=AUTOMATICO),
                   retangulo(0.3, 0.3, 0.7, 0.7, tipo=PAPEL)])
    assert ez.area_no_ponto(sel, (0.4, 0.4)) == 1
    assert ez.area_no_ponto(sel, (0.2, 0.2)) == 0
    assert ez.area_no_ponto(sel, (0.9, 0.9)) is None


def test_mover_e_mudar_o_tamanho_sao_copias_e_nao_saem_da_pagina():
    original = retangulo(0.1, 0.1, 0.3, 0.2, origem=AUTOMATICO)
    andou = ez.movida(original, 0.1, 0.05)
    assert original.pontos == [(0.1, 0.1), (0.3, 0.2)]          # nao mexeu na de antes
    assert [v for ponto in andou.pontos for v in ponto] == pytest.approx([0.2, 0.15, 0.4, 0.25])
    assert andou.origem == MAO                                    # mexida pela pessoa
    assert ez.caixa_da_area(ez.movida(original, 5, 5)) == pytest.approx((0.8, 0.9, 1.0, 1.0))
    maior = ez.redimensionada(original, (0.1, 0.1, 0.5, 0.4))
    assert ez.caixa_da_area(maior) == pytest.approx((0.1, 0.1, 0.5, 0.4))
    risco = ez.redimensionada(traco([(0.2, 0.2), (0.4, 0.2)], espessura=0.02), (0.1, 0.1, 0.7, 0.4))
    assert risco.espessura > 0.02


def test_apagar_pintar_de_branco_e_copiar():
    sel = Selecao([retangulo(0.1, 0.1, 0.5, 0.5, origem=AUTOMATICO)])
    assert ez.sem_a_area(sel, 0).vazia and len(sel) == 1
    branca = ez.pintada_de_branco(sel.regioes[0])
    assert branca.tipo == PAPEL and branca.origem == MAO
    copia = ez.copia(sel.regioes[0])
    assert copia.pontos[0][0] > 0.1 and copia.origem == MAO


def test_contornos_so_das_achadas_pela_maquina():
    sel = Selecao([retangulo(0.1, 0.1, 0.5, 0.5, origem=AUTOMATICO),
                   retangulo(0.6, 0.6, 0.9, 0.9, origem=MAO)])
    assert len(ez.contornos(sel, 100, 100)) == 1
    assert len(ez.contornos(sel, 100, 100, so_da_maquina=False)) == 2


def _pagina():
    img = np.full((200, 200, 3), (180, 200, 220), np.uint8)       # papel amarelado
    img[50:60, 20:180] = (40, 30, 120)                              # uma linha de tinta marrom-avermelhada
    return img


def test_tres_jeitos_novos_por_cima_do_filtro():
    img = _pagina()
    saida = np.full((200, 200), 255, np.uint8)                      # o filtro deixou tudo branco
    area = [(0.0, 0.2), (1.0, 0.35)]                                # cobre a linha de tinta

    so = lambda tipo, **k: Selecao([Regiao(tipo=tipo, pontos=area, **k)])   # noqa: E731
    sem, mono = ez.aplicar_por_cima(img, saida, True, Selecao([retangulo(0, 0, 1, 1, tipo=GRAVURA)]))
    assert sem is saida and mono is True                            # sem os novos: o mesmo objeto

    cor, mono = ez.aplicar_por_cima(img, saida, True, so(TINTA_COR))
    assert mono is False
    assert tuple(cor[55, 100]) == (40, 30, 120)                     # a tinta com a cor dela
    assert tuple(cor[45, 100]) == (255, 255, 255)                   # o papel em branco

    preta, _ = ez.aplicar_por_cima(img, saida, True, so(TINTA_PRETA))
    assert tuple(preta[55, 100]) == (0, 0, 0)                       # a tinta em preto
    assert tuple(preta[45, 100]) == (180, 200, 220)                 # o fundo como no original

    pintada, _ = ez.aplicar_por_cima(img, saida, True, so(PINTAR, cor="#ff0000"))
    assert tuple(pintada[55, 100]) == (0, 0, 255)                   # BGR do vermelho
    assert tuple(pintada[150, 100]) == (255, 255, 255)              # fora da área, o filtro

    tirada = Selecao([Regiao(tipo=PINTAR, pontos=area, cor="#ff0000"),
                      Regiao(tipo=PINTAR, pontos=[(0.0, 0.0), (0.5, 1.0)], operacao=SUBTRAIR)])
    meio, _ = ez.aplicar_por_cima(img, saida, True, tirada)
    assert tuple(meio[55, 50]) == (255, 255, 255) and tuple(meio[55, 150]) == (0, 0, 255)


def test_no_pipeline_a_area_nova_muda_so_ela(tmp_path):
    from core import pipeline
    from core.filtros import PRETO_E_BRANCO
    from modelos import ConfigPagina, Projeto

    # (com detectar_regioes desligado o programa ignora a marcacao inteira;
    # ligado, a marcacao a mao que ja existe vale e nada e procurado)
    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), detectar_regioes=False)
    pagina = ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO)
    antes, mono_antes = pipeline._filtrar(projeto, pagina, _pagina())
    projeto.detectar_regioes = True
    pagina.guardar_selecao(Selecao([Regiao(tipo=PINTAR, pontos=[(0.0, 0.0), (0.2, 0.2)],
                                           cor="#0000ff", origem=MAO)]))
    depois, mono = pipeline._filtrar(projeto, pagina, _pagina())
    assert mono_antes is True and mono is False
    assert tuple(depois[10, 10]) == (255, 0, 0)
    assert (depois[100:, 100:, 0] == antes[100:, 100:]).all()


# --------------------------------------------------------------- o editor

from tests.test_mesmo_livro_outro_caminho import app  # noqa: E402,F401 - fixture


def _editor(app):
    from ui.widgets.editor_selecao import FERRAMENTA_AJUSTAR, EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 400)
    editor.definir_imagem(np.full((400, 400, 3), 230, np.uint8))
    editor.definir_selecao(Selecao([retangulo(0.1, 0.1, 0.4, 0.4, origem=AUTOMATICO)]))
    editor.definir_ferramenta(FERRAMENTA_AJUSTAR)
    editor._area = editor._calcular_area()
    return editor


def test_editor_escolhe_apaga_e_desfaz(app):
    editor = _editor(app)
    mudou = []
    editor.selecao_mudou.connect(lambda: mudou.append(1))
    assert editor.escolher_area((0.2, 0.2)) == 0
    assert editor.apagar_area_escolhida()
    assert editor.selecao.vazia and mudou
    editor.desfazer()
    assert len(editor.selecao) == 1 and editor.selecao.regioes[0].origem == AUTOMATICO


def test_editor_pinta_de_branco_copia_e_cola(app):
    editor = _editor(app)
    editor.escolher_area((0.2, 0.2))
    assert editor.pintar_de_branco_area_escolhida()
    assert editor.selecao.regioes[0].tipo == PAPEL
    assert editor.copiar_area_escolhida() and editor.colar()
    assert len(editor.selecao) == 2 and editor.escolhida == 1
    editor.desfazer()
    editor.desfazer()
    assert editor.selecao.regioes[0].tipo == GRAVURA


def test_editor_arrasta_para_mover_e_pelos_quadradinhos(app):
    from PySide6.QtCore import QPoint

    editor = _editor(app)
    a = editor._area
    meio = QPoint(a.left() + int(0.25 * a.width()), a.top() + int(0.25 * a.height()))
    editor._comecar_a_ajustar(meio)
    editor._arrastar_a_area(meio + QPoint(int(0.1 * a.width()), 0), soltou=True)
    x0, _y0, x1, _y1 = ez.caixa_da_area(editor.selecao.regioes[0])
    assert x0 == pytest.approx(0.2, abs=0.01) and x1 == pytest.approx(0.5, abs=0.01)
    # o quadradinho de baixo-direita aumenta
    canto = editor._alcas(editor._caixa_na_tela(editor.selecao.regioes[0]))["bd"].center()
    editor._comecar_a_ajustar(canto)
    editor._arrastar_a_area(canto + QPoint(int(0.1 * a.width()), int(0.1 * a.height())), soltou=True)
    x0, y0, x1, y1 = ez.caixa_da_area(editor.selecao.regioes[0])
    assert x1 == pytest.approx(0.6, abs=0.015) and y1 == pytest.approx(0.5, abs=0.015)
    editor.desfazer()
    editor.desfazer()
    assert ez.caixa_da_area(editor.selecao.regioes[0]) == pytest.approx((0.1, 0.1, 0.4, 0.4))


def test_pintar_por_cima_leva_a_cor_escolhida(app):
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO

    editor = _editor(app)
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(PINTAR)
    editor.definir_cor_de_pintar("#00ff00")
    editor._acrescentar(editor._nova("retangulo", [(0.5, 0.5), (0.8, 0.8)]))
    assert editor.selecao.regioes[-1].tipo == PINTAR
    assert editor.selecao.regioes[-1].cor == "#00ff00"
