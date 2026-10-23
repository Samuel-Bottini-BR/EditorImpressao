"""Item 2.18: o papel da "Tinta com a cor original" em dois jeitos.

Resposta do Samuel de 22/10/2026 à pergunta tc23-1 da Central (o retângulo
branco no meio do papel creme, no Original): ele perguntou "eu posso ter as
duas opções?" e escolheu "As duas: escolher o papel em cada área ('papel
branco' ou 'papel como o resto da página')".
- "papel branco": o papel dentro da área sai branco (o que o programa sempre
  fez). É o de fábrica.
- "papel como o resto da página": o papel dentro da área fica igual ao de
  fora, no filtro da página; só a tinta segue o A ou o B
  (Regiao.papel_da_pagina = True).

O que estes testes guardam:
1. De fábrica, livro novo e livro já começado (projeto gravado antes, sem a
   chave nova) saem IDÊNTICOS, ponto por ponto, ao de antes desta mudança, com
   A e com B (a conta de antes está copiada aqui, em `_de_antes`).
2. "papel como o resto da página": o papel da área é o do filtro (o creme do
   Original); a tinta é a mesma do "papel branco" (A ou B).
3. A última área manda onde duas se cruzam; o "tirar" vale.
4. A tela: os dois botões do papel aparecem com a "tinta com a cor", e a área
   marcada leva o jeito escolhido.
Testes de máquina; nenhuma janela aparece na tela.
"""

from __future__ import annotations

import cv2
import numpy as np

from core import editar_zonas as ez
from core.selecao import MAO, SUBTRAIR, TINTA_COR, Regiao, Selecao

CREME = (180, 200, 220)          # BGR: o papel amarelado


def _pagina():
    """Papel creme com duas linhas de tinta: uma vermelha e uma azul."""
    img = np.full((240, 240, 3), CREME, np.uint8)
    img[50:62, 20:220] = (40, 40, 170)        # vermelho (BGR)
    img[150:162, 20:220] = (160, 70, 40)      # azul (BGR)
    return img


AREA_DE_CIMA = [(0.0, 0.15), (1.0, 0.32)]      # cobre a linha vermelha
AREA_DE_BAIXO = [(0.0, 0.57), (1.0, 0.73)]     # cobre a linha azul


def _de_antes(original, saida, selecao):
    """A conta da "tinta com a cor" como era em 639136a (antes desta mudança),
    copiada linha por linha: A em toda a área, depois a B por cima onde a área
    é B (a última área manda)."""
    altura, largura = saida.shape[:2]
    resultado = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    resultado = resultado.copy()
    mascara = selecao.mascara(altura, largura, TINTA_COR)
    tinta = ez._tinta_na_area(original, mascara, 50, "auto")
    resultado[mascara & tinta] = original[mascara & tinta]
    resultado[mascara & ~tinta] = 255
    escura = np.zeros((altura, largura), bool)
    for r in selecao.regioes:
        if r.tipo == TINTA_COR and r.operacao != SUBTRAIR:
            escura[Selecao([r]).mascara(altura, largura, TINTA_COR)] = r.tinta_escurecida
    escura &= mascara & tinta
    if escura.any():
        resultado[escura] = ez.escurecida(original, escura)[escura]
    return resultado


def _sem_a_chave(regiao):
    """A área como um projeto gravado antes desta mudança a guardava."""
    dados = regiao.para_dicionario()
    del dados["papel_da_pagina"]
    return Regiao.de_dicionario(dados)


def test_de_fabrica_e_papel_branco():
    assert Regiao(tipo=TINTA_COR).papel_da_pagina is False


def test_de_fabrica_igual_ao_de_antes_com_a_e_com_b():
    """Papel branco (de fábrica): livro novo e livro já começado dão a MESMA
    imagem da conta de antes, ponto por ponto, nos dois filtros (saída cinza do
    Preto e branco e saída colorida do Original) e com A e B juntas."""
    img = _pagina()
    a = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO)
    b = Regiao(tipo=TINTA_COR, pontos=AREA_DE_BAIXO, origem=MAO, tinta_escurecida=True)
    for saida in (np.full((240, 240), 255, np.uint8), img.copy()):
        for regioes in ([a], [b], [a, b]):
            esperado = _de_antes(img, saida, Selecao(regioes))
            novo, mono = ez.aplicar_por_cima(img, saida, True, Selecao(regioes))
            antigo, _ = ez.aplicar_por_cima(img, saida, True,
                                            Selecao([_sem_a_chave(r) for r in regioes]))
            assert mono is False
            assert np.array_equal(novo, esperado)
            assert np.array_equal(antigo, esperado)


def test_papel_como_a_pagina_no_original_sem_retangulo_branco():
    """No Original (a saída do filtro é a própria página creme), o papel da
    área fica creme como em volta; com A, a página sai igual a sem área."""
    img = _pagina()
    saida = img.copy()                                   # o Original
    area = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, papel_da_pagina=True)
    res, _ = ez.aplicar_por_cima(img, saida, False, Selecao([area]))
    assert tuple(res[45, 100]) == CREME                  # papel dentro da área: creme
    assert tuple(res[55, 100]) == tuple(img[55, 100])    # tinta: como no livro (A)
    assert np.array_equal(res, saida)                    # nenhum retângulo branco

    branca, _ = ez.aplicar_por_cima(img, saida, False,
                                    Selecao([Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO)]))
    assert tuple(branca[45, 100]) == (255, 255, 255)     # o de fábrica: papel branco


def test_papel_como_a_pagina_com_b_so_a_tinta_escurece():
    img = _pagina()
    saida = img.copy()
    area = dict(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, tinta_escurecida=True)
    res, _ = ez.aplicar_por_cima(img, saida, False, Selecao([Regiao(**area, papel_da_pagina=True)]))
    branca, _ = ez.aplicar_por_cima(img, saida, False, Selecao([Regiao(**area)]))
    tinta = ez._tinta_na_area(img, Selecao([Regiao(**area)]).mascara(240, 240, TINTA_COR), 50, "auto")
    assert np.array_equal(res[tinta], branca[tinta])      # a tinta B é a mesma nos dois papéis
    assert tuple(res[45, 100]) == CREME                   # o papel, o da página
    assert tuple(res[55, 100]) != tuple(img[55, 100])     # a tinta escureceu


def test_papel_como_a_pagina_no_preto_e_branco_fica_branco():
    """No Preto e branco o papel da página já é branco: o papel da área também."""
    img = _pagina()
    saida = np.full((240, 240), 255, np.uint8)
    area = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, papel_da_pagina=True)
    res, _ = ez.aplicar_por_cima(img, saida, True, Selecao([area]))
    assert tuple(res[45, 100]) == (255, 255, 255)
    assert tuple(res[55, 100]) == tuple(img[55, 100])


def test_a_ultima_area_manda_e_o_tirar_vale():
    img = _pagina()
    saida = img.copy()
    da_pagina = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, papel_da_pagina=True)
    branca_por_cima = Regiao(tipo=TINTA_COR, pontos=[(0.5, 0.15), (1.0, 0.32)], origem=MAO)
    res, _ = ez.aplicar_por_cima(img, saida, False, Selecao([da_pagina, branca_por_cima]))
    assert tuple(res[45, 60]) == CREME                    # esquerda: papel da página
    assert tuple(res[45, 180]) == (255, 255, 255)         # direita: papel branco (por cima)

    tirada = Selecao([Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO),
                      Regiao(tipo=TINTA_COR, pontos=[(0.0, 0.0), (0.5, 1.0)], operacao=SUBTRAIR)])
    res, _ = ez.aplicar_por_cima(img, saida, False, tirada)
    assert tuple(res[45, 60]) == CREME                    # tirada: volta o filtro
    assert tuple(res[45, 180]) == (255, 255, 255)         # o que sobrou: papel branco


def test_a_escolha_fica_gravada_no_projeto():
    area = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, papel_da_pagina=True)
    assert Regiao.de_dicionario(area.para_dicionario()).papel_da_pagina is True


def test_no_pipeline_original_sem_retangulo_branco(tmp_path):
    """Pelo fim do caminho de verdade (core.pipeline._filtrar), no Original:
    com "papel como o resto da página" e A, sai igual a sem área nenhuma."""
    from core import pipeline
    from core.filtros import ORIGINAL
    from modelos import ConfigPagina, Projeto

    def filtrar(regioes):
        projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), detectar_regioes=False)
        pagina = ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)
        pagina.guardar_selecao(Selecao(regioes))
        return pipeline._filtrar(projeto, pagina, _pagina())[0]

    sem_area = filtrar([])
    com_area = filtrar([Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, papel_da_pagina=True)])
    sem3 = sem_area if sem_area.ndim == 3 else cv2.cvtColor(sem_area, cv2.COLOR_GRAY2BGR)
    assert np.array_equal(com_area, sem3)


# --------------------------------------------------------------- a tela

from tests.test_mesmo_livro_outro_caminho import app  # noqa: E402,F401 - fixture


def test_os_dois_papeis_aparecem_com_a_tinta_com_a_cor(app):
    from ui.widgets.paineis import PainelMarcarComo

    painel = PainelMarcarComo()
    assert not hasattr(painel, "botoes_do_papel") or not painel.botoes_do_papel
    escolhas = []
    painel.papel_escolhido.connect(escolhas.append)
    painel.definir_tipo(TINTA_COR)
    assert [b.text() for b in painel.botoes_do_papel.values()] == [
        "papel branco", "papel como o resto da página"]
    assert painel.papel_da_pagina is False                      # de fábrica
    painel.botoes_do_papel[True].click()
    assert escolhas == [True] and painel.papel_da_pagina is True
    assert painel.escurecer is False                            # a cor não mudou
    painel.definir_tipo("letra")
    assert not painel.botoes_do_papel


def test_a_area_marcada_leva_o_papel_escolhido(app):
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO, EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 400)
    editor.definir_imagem(np.full((400, 400, 3), 230, np.uint8))
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(TINTA_COR)
    editor._acrescentar(editor._nova("retangulo", [(0.1, 0.1), (0.4, 0.4)]))
    assert editor.selecao.regioes[-1].papel_da_pagina is False   # de fábrica
    editor.definir_papel_da_pagina(True)
    editor._acrescentar(editor._nova("retangulo", [(0.5, 0.5), (0.8, 0.8)]))
    assert editor.selecao.regioes[-1].papel_da_pagina is True
    assert editor.selecao.regioes[-1].tinta_escurecida is False
