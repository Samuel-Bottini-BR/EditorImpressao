"""Testes do core que nao dependem de nenhum PDF real."""

from __future__ import annotations

import numpy as np
import pytest

from core.analise import detectar_cor, fracao_de_tinta, tamanhos_fora_do_padrao
from core.dividir import detectar_lombada, dividir_imagem
from core.endireitar import ANGULO_MAXIMO, detectar_angulo, rotacionar
from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    janela_para_altura,
)
from core.recortar import aplicar_recorte, detectar_bordas
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import ConfigFolha, ConfigPagina, Projeto


def folha_dupla(com_sombra: bool = True) -> np.ndarray:
    """Uma folha branca com duas colunas de texto e uma lombada no meio."""
    img = np.full((600, 1000, 3), 235, dtype=np.uint8)
    for bloco_x in (120, 620):
        for linha in range(12):
            y = 100 + linha * 30
            img[y : y + 10, bloco_x : bloco_x + 260] = 30
    if com_sombra:
        img[:, 490:510] = 150
    return img


# --- filtros ---------------------------------------------------------------

def test_preto_e_branco_devolve_um_canal_so_com_preto_e_branco():
    saida, mono = aplicar_filtro(folha_dupla(), PRETO_E_BRANCO)
    assert mono is True
    assert saida.ndim == 2
    assert set(np.unique(saida)).issubset({0, 255})


def test_preto_e_branco_preserva_o_texto():
    saida, _ = aplicar_filtro(folha_dupla(), PRETO_E_BRANCO)
    tinta = (saida == 0).mean()
    assert 0.01 < tinta < 0.40, f"tinta fora do esperado: {tinta:.3f}"


def test_forcas_do_preto_sao_ordenadas():
    """Mais escuro tem que deixar mais preto que normal, que deixa mais que fraco."""
    img = folha_dupla()
    pretos = []
    for forca in ("mais_fraco", "normal", "mais_escuro"):
        saida, _ = aplicar_filtro(img, PRETO_E_BRANCO, forca_preto=forca)
        pretos.append((saida == 0).mean())
    assert pretos[0] <= pretos[1] <= pretos[2], pretos


@pytest.mark.parametrize("filtro", [ORIGINAL, MELHORAR, MAGICO_PRO])
def test_filtros_coloridos_mantem_tres_canais(filtro):
    saida, mono = aplicar_filtro(folha_dupla(), filtro)
    assert mono is False
    assert saida.ndim == 3


def test_melhorar_nao_lava_uma_area_colorida_uniforme():
    """A capa azul: o Melhorar tem que devolver azul, nao um borrao claro.

    E a regressao que motivou trocar a divisao pelo fundo por uma correcao
    com peso - a versao ingenua lavava a capa e trocava as cores.
    """
    img = np.full((600, 400, 3), 235, dtype=np.uint8)
    img[:, 200:] = (150, 70, 20)   # metade direita azul escuro (BGR)

    saida, _ = aplicar_filtro(img, MELHORAR)
    azul = saida[300, 300].astype(int)

    assert azul[0] > azul[2] + 40, f"o azul deixou de ser azul: {azul}"
    assert azul[0] < 235, f"o azul foi lavado ate o branco: {azul}"


def test_janela_do_sauvola_e_sempre_impar():
    for altura in (300, 1000, 2480, 5000):
        assert janela_para_altura(altura) % 2 == 1


# --- dividir ---------------------------------------------------------------

def test_acha_a_lombada_no_meio():
    lombada = detectar_lombada(folha_dupla())
    assert lombada.e_paisagem
    assert abs(lombada.posicao - 0.5) < 0.05
    assert lombada.confianca > 0.5


def test_acha_a_lombada_mesmo_sem_sombra():
    """Scan limpo: sobra so a ausencia de texto para nos guiar."""
    lombada = detectar_lombada(folha_dupla(com_sombra=False))
    assert abs(lombada.posicao - 0.5) < 0.06


def test_pagina_em_retrato_nao_e_dupla():
    retrato = np.full((900, 600, 3), 240, dtype=np.uint8)
    lombada = detectar_lombada(retrato)
    assert lombada.e_paisagem is False
    assert lombada.confianca == 0.0


def test_dividir_devolve_esquerda_e_direita():
    esq, dir_ = dividir_imagem(folha_dupla(), 0.5)
    assert esq.shape[1] == 500 and dir_.shape[1] == 500


# --- endireitar ------------------------------------------------------------

def test_detecta_a_inclinacao_que_aplicamos():
    img = rotacionar(folha_dupla(), -2.0)
    detectado = detectar_angulo(img)
    assert abs(detectado.angulo - 2.0) < 0.6, detectado.angulo


def test_nao_gira_quando_o_angulo_e_minimo():
    img = folha_dupla()
    assert rotacionar(img, 0.05) is img


def test_pagina_em_branco_nao_tem_angulo():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    assert detectar_angulo(branca).angulo == 0.0


def test_nunca_passa_do_limite():
    for _ in range(3):
        assert abs(detectar_angulo(folha_dupla()).angulo) <= ANGULO_MAXIMO


# --- recortar --------------------------------------------------------------

def test_recorte_tira_a_borda_preta_do_scanner():
    img = folha_dupla()
    img[:, :40] = 0        # borda preta na esquerda
    recorte = detectar_bordas(img)
    cortada = aplicar_recorte(img, recorte)
    assert cortada.shape[1] < img.shape[1]
    assert cortada[:, :5].mean() > 100, "sobrou borda preta depois do corte"


def test_pagina_em_branco_nao_e_recortada():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    recorte = detectar_bordas(branca)
    assert recorte.tupla == (0.0, 0.0, 1.0, 1.0)


# --- analise ---------------------------------------------------------------

def test_texto_preto_no_branco_nao_conta_como_colorido():
    tem_cor, _ = detectar_cor(folha_dupla())
    assert tem_cor is False


def test_capa_colorida_conta_como_colorida():
    capa = np.full((600, 400, 3), (170, 90, 30), dtype=np.uint8)
    tem_cor, _ = detectar_cor(capa)
    assert tem_cor is True


def test_pagina_em_branco_quase_nao_tem_tinta():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    assert fracao_de_tinta(branca) < 0.01


def test_marca_a_folha_de_tamanho_diferente():
    tamanhos = [(842.0, 595.0)] * 9 + [(595.0, 842.0)]
    fora = tamanhos_fora_do_padrao(tamanhos)
    assert fora[-1] is True
    assert not any(fora[:-1])


# --- desfazer / refazer ----------------------------------------------------

def projeto_de_teste() -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(3)]
    projeto.paginas = [
        ConfigPagina(indice=i, folha=i // 2, filtro=PRETO_E_BRANCO) for i in range(6)
    ]
    return projeto


def test_desfazer_e_refazer_uma_alteracao():
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes()

    acao = montar_acao(projeto, "mudar_filtro", "pagina", [2],
                       {"filtro": MAGICO_PRO}, "Filtro da pagina 3")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert projeto.paginas[2].filtro == MAGICO_PRO

    acoes.desfazer(projeto)
    assert projeto.paginas[2].filtro == PRETO_E_BRANCO
    acoes.refazer(projeto)
    assert projeto.paginas[2].filtro == MAGICO_PRO


def test_um_ctrl_z_desfaz_o_lote_inteiro():
    """'Usar em todas' e UMA acao, mesmo mexendo em 6 paginas."""
    projeto = projeto_de_teste()
    projeto.paginas[0].filtro = MELHORAR   # valor diferente, para conferir a volta
    acoes = HistoricoAcoes()

    indices = [p.indice for p in projeto.paginas]
    acao = montar_acao(projeto, "aplicar_em_todas", "pagina", indices,
                       {"filtro": MAGICO_PRO}, "Magico pro em todas")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert all(p.filtro == MAGICO_PRO for p in projeto.paginas)

    acoes.desfazer(projeto)
    assert projeto.paginas[0].filtro == MELHORAR, "cada pagina volta ao SEU valor"
    assert all(p.filtro == PRETO_E_BRANCO for p in projeto.paginas[1:])


def test_acao_nova_limpa_a_pilha_de_refazer():
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes()

    for filtro in (MAGICO_PRO, MELHORAR):
        acao = montar_acao(projeto, "mudar_filtro", "pagina", [0], {"filtro": filtro}, "x")
        aplicar(projeto, acao, acao.depois)
        acoes.registrar(acao)

    acoes.desfazer(projeto)
    assert acoes.pode_refazer

    acao = montar_acao(projeto, "mudar_filtro", "pagina", [1], {"filtro": ORIGINAL}, "y")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert not acoes.pode_refazer


def test_historico_sobrevive_a_fechar_o_programa(tmp_path):
    """Criterio 14: reabrir o programa mantem o desfazer E o refazer."""
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes(tmp_path)

    for filtro in (MAGICO_PRO, MELHORAR):
        acao = montar_acao(projeto, "mudar_filtro", "pagina", [0], {"filtro": filtro}, "x")
        aplicar(projeto, acao, acao.depois)
        acoes.registrar(acao)
    acoes.desfazer(projeto)   # sobra 1 aplicada e 1 para refazer

    # "fecha e reabre"
    outro = HistoricoAcoes(tmp_path)
    outro.carregar()
    assert len(outro.feitas) == 1
    assert outro.pode_desfazer and outro.pode_refazer


def test_apagar_paginas_nao_quebra_a_contagem():
    projeto = projeto_de_teste()
    projeto.paginas[1].apagada = True
    projeto.paginas[4].apagada = True
    assert projeto.total_apagadas == 2
    assert len(projeto.paginas_ativas) == 4


def test_caminho_rapido_so_com_cadernos():
    projeto = projeto_de_teste()
    projeto.montar_cadernos = True
    projeto.dividir_folhas = projeto.limpar = False
    projeto.endireitar = projeto.cortar_bordas = False
    assert projeto.so_cadernos is True

    projeto.paginas[0].apagada = True
    assert projeto.so_cadernos is False, "apagar pagina exige regravar o PDF"
