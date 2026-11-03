"""Teste de reversão: o Automático pulava as folhas ERRADAS depois de dividir (03/11/2026).

O defeito (Gradus Primus, achado pela gerente em 03/11/2026). Samuel: "fui testar o margens
iguais e o dividir e acho que deu algum erro. envestiga isso para mim" · "teve até uma folha
que ficou colocada uma na outra." Ele tinha dividido à mão as folhas 1, 2 e 9 e rodou o
Automático só com "Dividir" no livro todo, pulando as mexidas (D-004). Saíram 138 páginas: as
folhas 6 e 7 do scan ficaram inteiras, embora o motor ache duas páginas nelas.

Causa: `core/automatico.aplicar` guardava as páginas a pular pelo NÚMERO da página
(`pagina.indice`), contado antes de dividir. Cada folha de uma página que o laço do
`_dividir` parte em duas renumera as páginas seguintes; o número guardado da folha 9 (dividida
à mão) passava a apontar para as páginas das folhas 6 e 7, que eram puladas no lugar dela. A
mesma lista velha valia depois no Endireitar/Cortar/Limpar da mesma rodada
(`_ligar_na_pagina`): a página mexida à mão perdia o valor dela e outra era pulada.

D-004 (28/09/2026): "Automático em livro já mexido à mão: o programa pergunta se quer pular as
páginas mexidas." — com "pular", a página mexida fica igual; as outras são feitas.

Sem DLL e sem PDF: o projeto é montado à mão e as medidas (o que o motor acharia) são
passadas prontas a `aplicar`, como a janela faz depois de medir num fio de fundo.
"""

from __future__ import annotations

from core import automatico as A
from core import etapas as E
from modelos import (METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigFolha,
                     ConfigPagina, Projeto)

LINHA_A_MAO = 0.47          # a linha que a pessoa pôs (o motor acharia 0.5)


def _livro(divididas_a_mao: set[int], folhas: int = 10) -> Projeto:
    """Livro de `folhas` folhas de duas páginas; as de `divididas_a_mao` já divididas à mão
    (com a marca "mexida à mão" do Dividir, na linha LINHA_A_MAO), as outras ainda inteiras."""
    projeto = Projeto(caminho_entrada="sintetico.pdf")
    paginas = []
    for f in range(folhas):
        if f in divididas_a_mao:
            projeto.folhas.append(ConfigFolha(indice=f, dividir=True, posicao_corte=LINHA_A_MAO,
                                              mexida_a_mao=[E.DIVIDIR]))
            paginas += [ConfigPagina(indice=0, folha=f, metade=METADE_ESQUERDA),
                        ConfigPagina(indice=0, folha=f, metade=METADE_DIREITA)]
        else:
            projeto.folhas.append(ConfigFolha(indice=f, dividir=False))
            paginas.append(ConfigPagina(indice=0, folha=f, metade=METADE_INTEIRA))
    for n, pagina in enumerate(paginas):
        pagina.indice = n
    projeto.paginas = paginas
    return projeto


def _medidas(projeto: Projeto) -> dict[int, A.MedidaDaFolha]:
    """O que o motor acha em cada folha: duas páginas, a linha no meio."""
    return {f.indice: A.MedidaDaFolha(
        indice=f.indice, dividir=True, posicao_corte=0.5, confianca_corte=0.9, e_paisagem=True,
        sobra=None, angulo_detectado=0.0, confianca_angulo=0.0, alertas=[], partes=[])
        for f in projeto.folhas}


def _metades(projeto: Projeto, folha: int) -> list[str]:
    return [p.metade for p in projeto.paginas if p.folha == folha]


def test_dividir_pula_so_as_folhas_divididas_a_mao_mesmo_com_as_paginas_renumeradas():
    """Como no Gradus: folhas 1, 2 e 9 (índices 0, 1, 8) divididas à mão, as outras inteiras.
    Rodar só "Dividir" no livro todo, pulando as mexidas: TODAS as folhas inteiras são
    divididas (20 páginas) e as três divididas à mão ficam como estavam (a linha delas e a
    marca). No código antigo as folhas 6 e 7 (índices 5 e 6) ficavam inteiras (18 páginas) e a
    folha 9 perdia a linha à mão."""
    projeto = _livro({0, 1, 8})
    assert len(projeto.paginas) == 13
    A.aplicar(projeto, A.Pedido(etapas=[A.DIVIDIR]), _medidas(projeto))

    assert len(projeto.paginas) == 20
    for folha in projeto.folhas:
        assert folha.dividir, f"folha {folha.indice + 1} ficou inteira"
        assert _metades(projeto, folha.indice) == [METADE_ESQUERDA, METADE_DIREITA]
    for f in (0, 1, 8):                       # as mexidas à mão ficam iguais (D-004)
        assert projeto.folhas[f].posicao_corte == LINHA_A_MAO
        assert E.DIVIDIR in projeto.folhas[f].mexida_a_mao
    for f in (2, 3, 4, 5, 6, 7, 9):           # as outras ganham a linha achada
        assert projeto.folhas[f].posicao_corte == 0.5
    assert [p.indice for p in projeto.paginas] == list(range(20))


def test_dividir_em_qualquer_ordem_de_folhas_mexidas():
    """Qualquer ordem: folha dividida à mão no fim, no meio e várias seguidas depois de
    folhas inteiras. Toda folha não mexida é dividida; as mexidas ficam."""
    for mexidas in ({9}, {4}, {3, 7, 8}, {0, 5, 9}, {6, 7}, set()):
        projeto = _livro(mexidas)
        A.aplicar(projeto, A.Pedido(etapas=[A.DIVIDIR]), _medidas(projeto))
        assert len(projeto.paginas) == 20, mexidas
        for folha in projeto.folhas:
            esperada = LINHA_A_MAO if folha.indice in mexidas else 0.5
            assert folha.dividir and folha.posicao_corte == esperada, (mexidas, folha.indice)


def test_endireitar_na_mesma_rodada_pula_a_pagina_certa_depois_de_dividir():
    """A mesma lista valia no Endireitar da mesma rodada (`_ligar_na_pagina`). Folhas 1 e 2
    divididas à mão; a página da folha 10 (inteira) com o ângulo à mão. "Dividir" e
    "Endireitar" no livro todo, pulando as mexidas: a página da folha 10 fica igual (o ângulo
    dela, a marca, e a folha sem dividir, como o pular sempre fez com a folha da página
    mexida); as folhas 3 a 9 são divididas. No código antigo a folha 10 era dividida e perdia
    o ângulo à mão."""
    projeto = _livro({0, 1})
    mexida = projeto.paginas[-1]
    assert mexida.folha == 9
    mexida.angulo_manual = 2.0
    mexida.mexida_a_mao = [E.ENDIREITAR]
    A.aplicar(projeto, A.Pedido(etapas=[A.DIVIDIR, A.ENDIREITAR]), _medidas(projeto))

    assert projeto.endireitar
    assert _metades(projeto, 9) == [METADE_INTEIRA]
    pagina = next(p for p in projeto.paginas if p.folha == 9)
    assert pagina.angulo_manual == 2.0 and E.ENDIREITAR in pagina.mexida_a_mao
    for f in range(0, 9):
        assert _metades(projeto, f) == [METADE_ESQUERDA, METADE_DIREITA], f
    assert len(projeto.paginas) == 19


def test_rodar_nelas_tambem_divide_todas_as_folhas():
    """O outro botão da pergunta D-004 ("Rodar nelas também", pular_mexidas=False) não muda:
    todas as folhas ganham a linha achada, também as divididas à mão."""
    projeto = _livro({0, 1, 8})
    A.aplicar(projeto, A.Pedido(etapas=[A.DIVIDIR], pular_mexidas=False), _medidas(projeto))
    assert len(projeto.paginas) == 20
    assert all(f.dividir and f.posicao_corte == 0.5 for f in projeto.folhas)
