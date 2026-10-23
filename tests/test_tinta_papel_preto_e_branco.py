"""Item 2.18: respostas do Samuel às perguntas 10 e 11 (Central, 23/10/2026).

Pergunta 10 (a linha preta em volta da letra no Preto e branco): "No Preto e
branco, tirar a linha preta: as duas opções de papel saem iguais, com a letra
limpa". Ele perguntou "Isso vai alterar alguma coisa, tirar essa linha
preta?" e a resposta dada foi: só muda a página em Preto e branco com uma área
"papel como o resto da página"; nela a letra sai igual a "papel branco". Nada
mais muda. O que estes testes guardam:
1. No Preto e branco, "papel como o resto da página" sai IDÊNTICO, ponto por
   ponto, a "papel branco" (com A e com B), pelo caminho de verdade
   (core.pipeline._filtrar). O teste com o contorno preto
   (`test_preto_e_branco_sem_o_contorno_preto`) FALHA no código de antes
   (0acf2c7), que deixava o contorno do filtro em volta da letra.
2. No Original e no Melhorar, "papel como o resto da página" sai igual ao de
   hoje (a conta de 0acf2c7 copiada aqui em `_de_hoje`), sem mudança.

Pergunta 11 (o nome do botão): "manter a cor da tinta". Só o rótulo da tela
mudou; o código gravado no projeto.json continua "tinta_cor" (projeto antigo
abre igual).
Testes de máquina; nenhuma janela aparece na tela.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core import editar_zonas as ez
from core.selecao import MAO, SUBTRAIR, TINTA_COR, Regiao, Selecao

CREME = (180, 200, 220)          # BGR: o papel amarelado
AREA = [(0.0, 0.1), (1.0, 0.4)]  # cobre as duas linhas de cima


def _pagina():
    """Papel creme com letras de beirada macia (vermelho e azul), como num
    scan: a beirada borrada é onde o filtro Preto e branco pinta um pouco além
    da "tinta" medida na área."""
    img = np.full((300, 300, 3), CREME, np.uint8)
    for y in (40, 80):
        for x in range(20, 280, 24):
            cv2.putText(img, "A", (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (40, 40, 170) if y == 40 else (160, 70, 40), 3)
    img[200:212, 20:280] = (30, 30, 30)        # uma linha preta fora da área
    return cv2.GaussianBlur(img, (5, 5), 1.5)


def _de_hoje(original, saida, selecao, forca_preto=50, algoritmo="auto"):
    """A conta da "tinta com a cor" como era em 0acf2c7 (antes desta mudança),
    copiada linha por linha: A em toda a área, a B por cima onde a área é B,
    e o papel da página onde a área pede (a última área manda)."""
    altura, largura = saida.shape[:2]
    filtrada = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    resultado = filtrada.copy()
    original3 = original if original.ndim == 3 else cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    mascara = selecao.mascara(altura, largura, TINTA_COR)
    tinta = ez._tinta_na_area(original, mascara, forca_preto, algoritmo)
    resultado[mascara & tinta] = original3[mascara & tinta]
    resultado[mascara & ~tinta] = 255
    escura = np.zeros((altura, largura), bool)
    papel = np.zeros((altura, largura), bool)
    for r in selecao.regioes:
        if r.tipo == TINTA_COR and r.operacao != SUBTRAIR:
            dela = Selecao([r]).mascara(altura, largura, TINTA_COR)
            escura[dela] = r.tinta_escurecida
            papel[dela] = r.papel_da_pagina
    escura &= mascara & tinta
    if escura.any():
        resultado[escura] = ez.escurecida(original3, escura)[escura]
    papel &= mascara & ~tinta
    resultado[papel] = filtrada[papel]
    return resultado


def _filtrar(tmp_path, filtro, regioes, monkeypatch=None, guardar=None):
    """O fim do caminho de verdade (core.pipeline._filtrar), com
    detectar_regioes=True: com ele desligado o pipeline não usa marcação
    nenhuma, nem a feita à mão (core.pipeline.garantir_selecao). `guardar`
    (lista) recebe a imagem que entra no filtro e a saída do filtro, antes das
    áreas por cima."""
    from core import pipeline
    from modelos import ConfigPagina, Projeto

    if guardar is not None:
        filtro_de_verdade = pipeline._filtro_da_pagina

        def espiao(projeto, pagina, img, selecao, dpi, dpi_do_scan):
            saida = filtro_de_verdade(projeto, pagina, img, selecao, dpi, dpi_do_scan)
            guardar.append((img, saida[0]))
            return saida
        monkeypatch.setattr(pipeline, "_filtro_da_pagina", espiao)
    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), detectar_regioes=True)
    pagina = ConfigPagina(indice=0, folha=0, filtro=filtro)
    pagina.guardar_selecao(Selecao(regioes))
    return pipeline._filtrar(projeto, pagina, _pagina())[0]


def _area(escurecida=False, papel_da_pagina=False):
    return Regiao(tipo=TINTA_COR, pontos=AREA, origem=MAO,
                  tinta_escurecida=escurecida, papel_da_pagina=papel_da_pagina)


# --------------------------------------------------------------- pergunta 10

@pytest.mark.parametrize("escurecida", [False, True])
def test_preto_e_branco_os_dois_papeis_saem_iguais(tmp_path, escurecida):
    """No Preto e branco (filtro de verdade), "papel como o resto da página"
    sai idêntico, ponto por ponto, a "papel branco", com A e com B."""
    from core.filtros import PRETO_E_BRANCO

    branco = _filtrar(tmp_path, PRETO_E_BRANCO, [_area(escurecida, False)])
    da_pagina = _filtrar(tmp_path, PRETO_E_BRANCO, [_area(escurecida, True)])
    sem_area = _filtrar(tmp_path, PRETO_E_BRANCO, [])
    sem3 = sem_area if sem_area.ndim == 3 else cv2.cvtColor(sem_area, cv2.COLOR_GRAY2BGR)
    assert not np.array_equal(branco, sem3), "a área tem de valer (a tinta volta com cor)"
    assert np.array_equal(branco, da_pagina)


def test_preto_e_branco_sem_o_contorno_preto(tmp_path, monkeypatch):
    """Reversão da pergunta 10 (23/10/2026, "tirar a linha preta"): o filtro
    Preto e branco pinta de preto a beirada da letra um pouco além da "tinta"
    da área. Aqui a saída do filtro é forçada a ter esse contorno (a tinta da
    área engordada 2 pontos, em preto), para o teste não depender de quanto o
    binarizador engorda nesta página. No código de antes (0acf2c7) o contorno
    ficava com "papel como o resto da página" e este teste FALHA; agora sai
    igual a "papel branco"."""
    from core import pipeline
    from core.filtros import PRETO_E_BRANCO

    def filtro_com_contorno(projeto, pagina, img, selecao, dpi, dpi_do_scan):
        altura, largura = img.shape[:2]
        tudo = np.ones((altura, largura), bool)
        tinta = ez._tinta_na_area(img, tudo, pagina.forca_preto, pagina.algoritmo_preto_branco)
        gorda = cv2.dilate(tinta.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        saida = np.full((altura, largura), 255, np.uint8)
        saida[gorda] = 0
        return saida, True
    monkeypatch.setattr(pipeline, "_filtro_da_pagina", filtro_com_contorno)

    branco = _filtrar(tmp_path, PRETO_E_BRANCO, [_area(False, False)])
    da_pagina = _filtrar(tmp_path, PRETO_E_BRANCO, [_area(False, True)])
    altura, largura = branco.shape[:2]
    dentro = Selecao([_area()]).mascara(altura, largura, TINTA_COR)
    pretos_branco = int(np.count_nonzero(np.all(branco[dentro] == 0, axis=-1)))
    pretos_da_pagina = int(np.count_nonzero(np.all(da_pagina[dentro] == 0, axis=-1)))
    assert pretos_da_pagina == pretos_branco, (
        f"contorno preto em volta da letra: {pretos_da_pagina - pretos_branco} pontos a mais")
    assert np.array_equal(branco, da_pagina)
    # fora da área a página continua a do filtro (a linha preta de baixo)
    assert np.all(da_pagina[206, 100] == 0)


def test_preto_e_branco_chamada_direta(tmp_path):
    """A mesma regra chamando core.editar_zonas direto: com
    preto_e_branco=True o papel da área é branco mesmo onde o filtro deixou
    preto; sem dizer o filtro (de fábrica False), o de antes."""
    img = _pagina()
    saida = np.zeros((300, 300), np.uint8)            # um filtro todo preto
    sel_pagina = Selecao([_area(False, True)])
    sel_branco = Selecao([_area(False, False)])
    pb, _ = ez.aplicar_por_cima(img, saida, True, sel_pagina, preto_e_branco=True)
    branco, _ = ez.aplicar_por_cima(img, saida, True, sel_branco, preto_e_branco=True)
    assert np.array_equal(pb, branco)
    antes, _ = ez.aplicar_por_cima(img, saida, True, sel_pagina)
    assert np.array_equal(antes, _de_hoje(img, saida, sel_pagina))


@pytest.mark.parametrize("filtro_nome", ["ORIGINAL", "MELHORAR"])
@pytest.mark.parametrize("escurecida", [False, True])
def test_original_e_melhorar_como_hoje(tmp_path, monkeypatch, filtro_nome, escurecida):
    """No Original e no Melhorar, "papel como o resto da página" (e "papel
    branco") saem iguais ao de hoje, ponto por ponto (conta de 0acf2c7)."""
    from core import filtros
    from modelos import ConfigPagina

    filtro = getattr(filtros, filtro_nome)
    de_fabrica = ConfigPagina(indice=0, folha=0, filtro=filtro)
    for papel in (False, True):
        guardado = []
        regioes = [_area(escurecida, papel)]
        res = _filtrar(tmp_path, filtro, regioes, monkeypatch, guardado)
        img, saida = guardado[-1]
        assert not np.array_equal(res, saida if saida.ndim == 3 else
                                  cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)) or (papel and not escurecida),             "a área tem de valer"
        assert np.array_equal(res, _de_hoje(img, saida, Selecao(regioes), de_fabrica.forca_preto,
                                            de_fabrica.algoritmo_preto_branco))
    # no Original, com A e papel da página, continua sem o retângulo branco
    if filtro_nome == "ORIGINAL" and not escurecida:
        sem_area = _filtrar(tmp_path, filtro, [])
        sem3 = sem_area if sem_area.ndim == 3 else cv2.cvtColor(sem_area, cv2.COLOR_GRAY2BGR)
        assert np.array_equal(_filtrar(tmp_path, filtro, [_area(False, True)]), sem3)


# --------------------------------------------------------------- pergunta 11

from tests.test_mesmo_livro_outro_caminho import app  # noqa: E402,F401 - fixture


def test_o_botao_se_chama_manter_a_cor_da_tinta(app):
    from core.selecao import NOMES_AMIGAVEIS
    from ui.widgets.paineis import PainelMarcarComo

    painel = PainelMarcarComo()
    painel.definir_tipo(TINTA_COR)
    assert painel.botoes[TINTA_COR].text() == "manter a cor da tinta"
    assert NOMES_AMIGAVEIS[TINTA_COR] == "Manter a cor da tinta"
    textos = [b.text() for b in painel.botoes.values()]
    assert not any("papel branco" in t for t in textos), "o nome antigo saiu do tipo"
    # os jeitos da cor e do papel continuam com os mesmos nomes
    assert [b.text() for b in painel.botoes_do_papel.values()] == [
        "papel branco", "papel como o resto da página"]


def test_o_codigo_gravado_nao_mudou():
    """Só o rótulo mudou: a área grava "tinta_cor" como antes, e um projeto
    gravado antes (com "tinta_cor") abre como a mesma área."""
    assert TINTA_COR == "tinta_cor"
    dados = _area().para_dicionario()
    assert dados["tipo"] == "tinta_cor"
    antigo = {"tipo": "tinta_cor", "pontos": [[0.0, 0.1], [1.0, 0.4]], "origem": "mao"}
    assert Regiao.de_dicionario(antigo).tipo == TINTA_COR
