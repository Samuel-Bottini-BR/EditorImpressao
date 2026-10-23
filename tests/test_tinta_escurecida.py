"""Item 2.18: as duas opções da "Tinta com a cor original, papel branco".

Resposta do Samuel de 22/10/2026 à pergunta b-8-tinta-com-cor (Central):
"As duas: A e B como opções separadas".
- A, "cor como no livro": a tinta com a cor que tem no original (o que o
  programa sempre fez). É o de fábrica.
- B, "cor escurecida": a mesma tinta, mais escura e com a cor um pouco mais
  forte (core/editar_zonas.escurecida; Regiao.tinta_escurecida = True).

O que estes testes guardam:
1. Livro novo e livro já começado (projeto gravado antes, sem a chave nova)
   saem IDÊNTICOS, ponto por ponto, ao que o programa fazia antes de
   22/10/2026 (a conta antiga está copiada aqui, em `_a_de_antes`).
2. A opção B escurece só a tinta de dentro da área B; o papel fica branco e o
   resto da página não muda.
3. A tela: os dois botões só aparecem com a "tinta com a cor" escolhida, e a
   área marcada leva o jeito escolhido.
Testes de máquina; nenhuma janela aparece na tela.
"""

from __future__ import annotations

import cv2
import numpy as np

from core import editar_zonas as ez
from core.selecao import MAO, SUBTRAIR, TINTA_COR, Regiao, Selecao


def _pagina():
    """Papel amarelado com duas linhas de tinta: uma vermelha e uma azul."""
    img = np.full((240, 240, 3), (180, 200, 220), np.uint8)
    img[50:62, 20:220] = (40, 40, 170)        # vermelho (BGR)
    img[150:162, 20:220] = (160, 70, 40)      # azul (BGR)
    return img


AREA_DE_CIMA = [(0.0, 0.15), (1.0, 0.32)]      # cobre a linha vermelha
AREA_DE_BAIXO = [(0.0, 0.57), (1.0, 0.73)]     # cobre a linha azul


def _a_de_antes(original, saida, selecao):
    """A conta da "tinta com a cor" como era em f26407c (antes de 22/10/2026),
    copiada linha por linha, para comparar com a de hoje."""
    altura, largura = saida.shape[:2]
    resultado = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    resultado = resultado.copy()
    mascara = selecao.mascara(altura, largura, TINTA_COR)
    tinta = ez._tinta_na_area(original, mascara, 50, "auto")
    resultado[mascara & tinta] = original[mascara & tinta]
    resultado[mascara & ~tinta] = 255
    return resultado


def test_de_fabrica_e_a_cor_como_no_livro():
    assert Regiao(tipo=TINTA_COR).tinta_escurecida is False


def test_livro_novo_e_livro_ja_comecado_saem_identicos_ponto_por_ponto():
    """O de fábrica continua A: uma área nova, uma área de projeto gravado
    antes (sem a chave `tinta_escurecida`) e a conta antiga dão a MESMA
    imagem, ponto por ponto."""
    img = _pagina()
    saida = np.full((240, 240), 255, np.uint8)
    nova = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO)
    gravada_antes = nova.para_dicionario()
    del gravada_antes["tinta_escurecida"]                 # como no projeto.json de antes
    de_antes = Regiao.de_dicionario(gravada_antes)
    assert de_antes.tinta_escurecida is False

    esperado = _a_de_antes(img, saida, Selecao([nova]))
    livro_novo, mono_novo = ez.aplicar_por_cima(img, saida, True, Selecao([nova]))
    ja_comecado, mono_antes = ez.aplicar_por_cima(img, saida, True, Selecao([de_antes]))
    assert mono_novo is False and mono_antes is False
    assert np.array_equal(livro_novo, esperado)
    assert np.array_equal(ja_comecado, esperado)


def test_no_pipeline_livro_novo_e_ja_comecado_iguais(tmp_path):
    """O mesmo, pelo fim do caminho de verdade (core.pipeline._filtrar, o
    filtro Preto e branco da página com a marcação por cima)."""
    from core import pipeline
    from core.filtros import PRETO_E_BRANCO
    from modelos import ConfigPagina, Projeto

    resultados = []
    for regiao in (Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO),
                   Regiao.de_dicionario({"tipo": TINTA_COR, "forma": "retangulo",
                                         "pontos": [list(p) for p in AREA_DE_CIMA],
                                         "origem": MAO})):
        projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), detectar_regioes=True)
        pagina = ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO)
        pagina.guardar_selecao(Selecao([regiao]))
        resultados.append(pipeline._filtrar(projeto, pagina, _pagina())[0])
    assert np.array_equal(resultados[0], resultados[1])


def test_b_escurece_so_a_tinta_da_area_b():
    img = _pagina()
    saida = np.full((240, 240), 255, np.uint8)
    a = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO)
    b = Regiao(tipo=TINTA_COR, pontos=AREA_DE_BAIXO, origem=MAO, tinta_escurecida=True)
    so_a, _ = ez.aplicar_por_cima(img, saida, True, Selecao([a]))
    as_duas, mono = ez.aplicar_por_cima(img, saida, True, Selecao([a, b]))
    assert mono is False

    # a área A não mudou com a B do lado; fora das áreas, o filtro (branco)
    assert np.array_equal(as_duas[:120], so_a[:120])
    assert tuple(as_duas[200, 100]) == (255, 255, 255)
    # na área B: o papel branco, a tinta azul mais escura e ainda azul
    assert tuple(as_duas[145, 100]) == (255, 255, 255)
    azul = as_duas[155, 100].astype(int)
    lab_antes = cv2.cvtColor(img[155:156, 100:101], cv2.COLOR_BGR2LAB)[0, 0].astype(int)
    lab_depois = cv2.cvtColor(as_duas[155:156, 100:101], cv2.COLOR_BGR2LAB)[0, 0].astype(int)
    assert lab_depois[0] < lab_antes[0] * 0.7                 # mais escura (brilho ~metade; a cor mais forte sobe um pouco)
    assert azul[0] > azul[1] and azul[0] > azul[2]           # continua azul (B de BGR maior)
    assert abs(lab_depois[2] - 128) >= abs(lab_antes[2] - 128)   # cor não mais fraca


def test_b_a_ultima_area_manda_onde_se_cruzam_e_o_tirar_vale():
    img = _pagina()
    saida = np.full((240, 240), 255, np.uint8)
    b = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, origem=MAO, tinta_escurecida=True)
    a_por_cima = Regiao(tipo=TINTA_COR, pontos=[(0.5, 0.15), (1.0, 0.32)], origem=MAO)
    res, _ = ez.aplicar_por_cima(img, saida, True, Selecao([b, a_por_cima]))
    assert tuple(res[55, 60]) != tuple(img[55, 60])           # metade da esquerda: B
    assert tuple(res[55, 180]) == tuple(img[55, 180])         # metade da direita: A (por cima)

    tirada = Selecao([b, Regiao(tipo=TINTA_COR, pontos=[(0.0, 0.0), (0.5, 1.0)],
                                operacao=SUBTRAIR)])
    res, _ = ez.aplicar_por_cima(img, saida, True, tirada)
    assert tuple(res[55, 60]) == (255, 255, 255)               # tirada: volta o filtro
    assert tuple(res[55, 180]) != tuple(img[55, 180])          # o que sobrou: B


def test_a_escolha_fica_gravada_no_projeto():
    b = Regiao(tipo=TINTA_COR, pontos=AREA_DE_CIMA, tinta_escurecida=True)
    assert Regiao.de_dicionario(b.para_dicionario()).tinta_escurecida is True


# --------------------------------------------------------------- a tela

from tests.test_mesmo_livro_outro_caminho import app  # noqa: E402,F401 - fixture


def test_os_dois_jeitos_so_aparecem_com_a_tinta_com_a_cor(app):
    from ui.widgets.paineis import PainelMarcarComo

    painel = PainelMarcarComo()
    assert painel.dentro.count() == 7                           # como antes
    escolhas = []
    painel.escurecer_escolhido.connect(escolhas.append)
    painel.definir_tipo(TINTA_COR)
    assert painel.dentro.count() == 8                           # a linha dos dois jeitos
    assert [b.text() for b in painel.botoes_da_cor.values()] == ["cor como no livro",
                                                                 "cor escurecida"]
    painel.botoes_da_cor[True].click()
    assert escolhas == [True] and painel.escurecer is True
    painel.definir_tipo("letra")
    assert painel.dentro.count() == 7


def test_a_area_marcada_leva_o_jeito_escolhido(app):
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO, EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 400)
    editor.definir_imagem(np.full((400, 400, 3), 230, np.uint8))
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(TINTA_COR)
    editor._acrescentar(editor._nova("retangulo", [(0.1, 0.1), (0.4, 0.4)]))
    assert editor.selecao.regioes[-1].tinta_escurecida is False   # de fábrica, A
    editor.definir_tinta_escurecida(True)
    editor._acrescentar(editor._nova("retangulo", [(0.5, 0.5), (0.8, 0.8)]))
    assert editor.selecao.regioes[-1].tinta_escurecida is True
