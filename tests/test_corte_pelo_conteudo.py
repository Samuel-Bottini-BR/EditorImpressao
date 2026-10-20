"""O corte que segue o conteúdo (item 2.5): as contas de core/corte_pelo_conteudo.py.

Testes de máquina. As contas de soma e máximo (tamanho do livro, alargar até
ele, caber na imagem, o que ficou de fora) não precisam da DLL; os que medem
uma página de verdade pulam sem a DLL do ScanTailor.

Decisões cobertas (literais no topo do módulo): G8 e G9 (05/10/2026),
g8-moldura-tinta-fora, g9-pagina-muito-maior (13/10/2026) e a explicação da
impressão (14/10/2026: na edição não há margem; só a folga de 1 mm).
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core import corte_pelo_conteudo as cc
from core import st_ferramentas

MM = 0.1      # 0,1 mm por ponto nos casos de mentira (254 DPI)


def _medida(caixa, largura=2000, altura=3000, mm=MM):
    x0, y0, x1, y1 = caixa
    return cc.MedidaDoConteudo(largura, altura, caixa, ((x1 - x0) * mm, (y1 - y0) * mm), (mm, mm))


# ------------------------------------------------------------ tamanho do livro (G9)

def test_tamanho_do_livro_e_a_maior_largura_e_a_maior_altura_com_a_margem():
    """ScanTailor (computeAggregateHardSizeMMLocked): a maior largura e a maior
    altura podem vir de páginas diferentes; cada uma com 1 mm de cada lado."""
    livro = cc.tamanho_do_livro({1: (100.0, 150.0), 2: (110.0, 140.0), 3: (105.0, 160.0)})
    assert livro.como_tupla() == pytest.approx((110.0 + 2 * cc.MARGEM_MM, 160.0 + 2 * cc.MARGEM_MM))
    assert livro.muito_maiores == frozenset()
    assert livro.paginas == 3


def test_pagina_sem_conteudo_nao_entra_na_conta():
    livro = cc.tamanho_do_livro({1: (100.0, 150.0), 2: None, 3: (100.0, 150.0)})
    assert livro.paginas == 2
    assert cc.tamanho_do_livro({1: None}) is None
    assert cc.tamanho_do_livro({}) is None


def test_g9_folha_muito_maior_fica_de_fora_sozinha():
    """g9-pagina-muito-maior: "O programa deixa essa folha de fora sozinho, e
    avisa". A tabela dobrável (bem mais larga) não muda o tamanho do livro."""
    tamanhos = {i: (100.0 + i, 150.0) for i in range(1, 9)}
    tamanhos[9] = (190.0, 150.0)                     # a tabela dobrável
    livro = cc.tamanho_do_livro(tamanhos)
    assert livro.muito_maiores == frozenset({9})
    assert livro.largura_mm == pytest.approx(108.0 + 2 * cc.MARGEM_MM)
    # mais alta que o limite também fica de fora
    tamanhos[9] = (100.0, 150.0 * cc.LIMITE_DA_MUITO_MAIOR + 1)
    assert cc.tamanho_do_livro(tamanhos).muito_maiores == frozenset({9})


def test_g9_um_pouco_maior_continua_na_conta():
    tamanhos = {i: (100.0, 150.0) for i in range(1, 9)}
    tamanhos[9] = (100.0 * cc.LIMITE_DA_MUITO_MAIOR - 1, 150.0)
    livro = cc.tamanho_do_livro(tamanhos)
    assert livro.muito_maiores == frozenset()
    assert livro.largura_mm == pytest.approx(100.0 * cc.LIMITE_DA_MUITO_MAIOR - 1 + 2 * cc.MARGEM_MM)


def test_g9_o_kaique_poe_de_volta_ou_tira():
    """O aviso deixa desfazer: a página posta de volta entra na conta; a que
    ele tira não entra (o "não alinhar com as outras" do ScanTailor)."""
    tamanhos = {i: (100.0, 150.0) for i in range(1, 9)}
    tamanhos[9] = (190.0, 150.0)
    de_volta = cc.tamanho_do_livro(tamanhos, sempre_dentro=[9])
    assert de_volta.muito_maiores == frozenset()
    assert de_volta.largura_mm == pytest.approx(190.0 + 2 * cc.MARGEM_MM)
    tirada = cc.tamanho_do_livro({1: (100.0, 150.0), 2: (120.0, 150.0)}, sempre_fora=[2])
    assert tirada.largura_mm == pytest.approx(100.0 + 2 * cc.MARGEM_MM)


def test_g9_com_poucas_paginas_ninguem_fica_de_fora():
    assert cc.muito_maiores({1: (100.0, 150.0), 2: (300.0, 150.0)}) == frozenset()


# ------------------------------------------------------- o corte de cada página

def test_corte_sem_o_livro_e_o_conteudo_com_1_mm():
    """Sem o tamanho do livro: a caixa mais 1 mm de cada lado (a folga já
    aprovada; na edição não há margem, explicação de 14/10)."""
    m = _medida((500.0, 600.0, 1500.0, 2400.0))
    folga = cc.MARGEM_MM / MM                                 # 10 pontos
    assert cc.caixa_do_corte(m) == pytest.approx((500 - folga, 600 - folga, 1500 + folga, 2400 + folga))


def test_corte_alarga_ate_o_tamanho_do_livro_metade_para_cada_lado():
    """ScanTailor (calcSoftMarginsMM com HCENTER e VCENTER, o de fábrica): a
    página menor fica do tamanho do livro, com o conteúdo no meio."""
    m = _medida((800.0, 1000.0, 1200.0, 1500.0))              # 40 x 50 mm
    livro = cc.TamanhoDoLivro(102.0, 152.0)                   # 100 x 150 + 1 mm de cada lado
    x0, y0, x1, y1 = cc.caixa_do_corte(m, livro)
    assert ((x1 - x0) * MM, (y1 - y0) * MM) == pytest.approx((102.0, 152.0))
    assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx((1000.0, 1250.0))   # o meio do conteúdo


def test_a_maior_pagina_nao_alarga():
    m = _medida((500.0, 600.0, 1500.0, 2100.0))               # 100 x 150 mm
    livro = cc.tamanho_do_livro({1: m.tamanho_mm, 2: (90.0, 140.0), 3: (95.0, 145.0)})
    assert cc.caixa_do_corte(m, livro) == pytest.approx(cc.caixa_do_corte(m))


def test_corte_anda_para_dentro_da_imagem_guardando_o_tamanho():
    """O corte não sai da imagem (pintar o que sobra de branco é o 2.14): anda
    para dentro, do mesmo tamanho."""
    m = _medida((20.0, 30.0, 420.0, 530.0))                   # colado no canto
    livro = cc.TamanhoDoLivro(102.0, 152.0)
    x0, y0, x1, y1 = cc.caixa_do_corte(m, livro)
    assert (x0, y0) == pytest.approx((0.0, 0.0))
    assert ((x1 - x0) * MM, (y1 - y0) * MM) == pytest.approx((102.0, 152.0))


def test_imagem_menor_que_o_livro_fica_a_imagem_inteira():
    m = _medida((100.0, 100.0, 500.0, 600.0), largura=700, altura=900)
    livro = cc.TamanhoDoLivro(102.0, 152.0)                   # 1020 x 1520 pontos > a imagem
    assert cc.caixa_do_corte(m, livro) == pytest.approx((0.0, 0.0, 700.0, 900.0))


def test_regressao_egenloff_12_pagina_quase_vazia_nao_vira_tira():
    """Bug achado olhando o Egenloff 12 (20/10/2026, relatorios/caixa-conteudo-
    impl/img/folha-grande/egenloff_p012.jpg): verso quase em branco, só um
    carimbo; a caixa do conteúdo vira uma tira de 231 x 22 pontos. Com o
    tamanho do livro, o corte fica do tamanho das outras páginas, não uma tira.
    (Bug de antes de existir a ligação: não há código antigo a reverter; a
    medida que pega o defeito é a altura do corte.)"""
    mm = 25.4 / 271.3                                          # o DPI dito no Egenloff 12
    tira = cc.MedidaDoConteudo(2084, 2746, (805.8, 1322.5, 1037.0, 1344.2),
                               (231.2 * mm, 21.7 * mm), (mm, mm))
    livro = cc.tamanho_do_livro({1: (140.0, 190.0), 2: (138.0, 185.0), 3: (141.0, 192.0),
                                 12: tira.tamanho_mm})
    x0, y0, x1, y1 = cc.caixa_do_corte(tira, livro)
    assert (y1 - y0) * mm == pytest.approx(livro.altura_mm, rel=1e-6)
    assert (x1 - x0) * mm == pytest.approx(livro.largura_mm, rel=1e-6)


def test_sem_caixa_nao_ha_corte():
    sem = cc.MedidaDoConteudo(100, 100, None, None, (0.1, 0.1), "a página não tem conteúdo")
    assert cc.caixa_do_corte(sem) is None
    indisponivel = cc.MedidaDoConteudo(100, 100, None, None, None, "sem DLL")
    assert not indisponivel.disponivel
    assert cc.caixa_do_corte(indisponivel) is None


def test_fracao_vai_e_volta():
    caixa = (100.0, 200.0, 900.0, 1500.0)
    recorte = cc.em_fracao(caixa, 1000, 2000)
    assert recorte == pytest.approx((0.1, 0.1, 0.8, 0.65))
    assert cc.de_fracao(recorte, 1000, 2000) == pytest.approx(caixa)


# ------------------------------------------------ o que ficou de fora (g8)

def _pagina_com_numero_e_moldura():
    """Uma página de mentira (0,1 mm por ponto): bloco de texto, um número de
    página sozinho no pé, a barra de uma moldura que o corte atravessa, uma
    mancha clara e um cisco."""
    cinza = np.full((3000, 2000), 235, np.uint8)
    cinza[600:2000, 500:1500] = 30                          # o texto
    cinza[2300:2340, 980:1020] = 20                         # o número da página, no pé
    cinza[400:2200, 1550:1600] = 25                         # a barra da moldura
    cinza[2500:2600, 300:400] = 200                         # mancha clara, fora da coluna
    cinza[2450:2455, 1000:1003] = 10                        # cisco (menor que 1 mm)
    pecas = np.array([
        [500 / 2000, 600 / 3000, 1500 / 2000, 2000 / 3000, 0],
        [980 / 2000, 2300 / 3000, 1020 / 2000, 2340 / 3000, 0],
        [1550 / 2000, 400 / 3000, 1600 / 2000, 2200 / 3000, 0],
        [300 / 2000, 2500 / 3000, 400 / 2000, 2600 / 3000, 0],
        [1000 / 2000, 2450 / 3000, 1003 / 2000, 2455 / 3000, 0],
        [100 / 2000, 100 / 3000, 1900 / 2000, 104 / 3000, 1],     # risco comprido e fino
    ])
    return cinza, pecas


def test_g8_avisa_o_numero_da_pagina_e_a_moldura_partida():
    """g8-moldura-tinta-fora: o corte que segue o conteúdo deixou de fora a
    barra da moldura (atravessada) e o número da página (sozinho no pé, na
    coluna); a mancha clara, o cisco e o risco fino não contam."""
    cinza, pecas = _pagina_com_numero_e_moldura()
    corte = (490.0, 590.0, 1560.0, 2010.0)                  # atravessa a barra
    tiradas = cc.tinta_tirada(corte, pecas, cinza, (MM, MM))
    assert sorted(tiradas) == sorted([(980.0, 2300.0, 1020.0, 2340.0), (1550.0, 400.0, 1600.0, 2200.0)])


def test_g8_nada_de_fora_nada_a_avisar():
    cinza, pecas = _pagina_com_numero_e_moldura()
    assert cc.tinta_tirada((290.0, 390.0, 1610.0, 2610.0), pecas, cinza, (MM, MM)) == []
    assert cc.tinta_tirada((0.0, 0.0, 10.0, 10.0), None, cinza, (MM, MM)) == []


def test_g8_corte_alargado_pega_o_que_foi_tirado():
    """A opção da g8, "mostrar ele alargado com o que foi tirado": o corte
    alargado contém as peças tiradas, com 1 mm em volta, sem sair da imagem."""
    cinza, pecas = _pagina_com_numero_e_moldura()
    corte = (490.0, 590.0, 1560.0, 2010.0)
    tiradas = cc.tinta_tirada(corte, pecas, cinza, (MM, MM))
    x0, y0, x1, y1 = cc.alargar(corte, tiradas, (MM, MM), 2000, 3000)
    folga = cc.MARGEM_MM / MM
    assert (x0, y0) == pytest.approx((490.0, 400.0 - folga))
    assert (x1, y1) == pytest.approx((1600.0 + folga, 2340.0 + folga))
    assert cc.alargar(corte, [], (MM, MM), 2000, 3000) == corte
    assert cc.alargar(corte, [(-50.0, -50.0, 10.0, 10.0)], (MM, MM), 2000, 3000)[:2] == (0.0, 0.0)


# -------------------------------------------------------------- com a DLL

precisa_da_dll = pytest.mark.skipif(
    st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None,
    reason="sem a DLL do ScanTailor (st_ferramentas)")


@precisa_da_dll
def test_medir_uma_pagina_de_mentira():
    """A caixa do conteúdo de uma página de texto de mentira (A5 a 200 DPI)
    abraça o texto, com a busca da página desligada (o de fábrica do
    ScanTailor; a busca da página é o 2.13)."""
    img = np.full((1654, 1165, 3), 255, np.uint8)
    for y in range(300, 1350, 34):
        for x in range(200, 960, 52):
            cv2.rectangle(img, (x, y), (x + 38, y + 14), (0, 0, 0), -1)
    m = cc.medir(img, 200.0, 200.0)
    assert m.disponivel and m.tem_conteudo
    x0, y0, x1, y1 = m.caixa
    assert x0 == pytest.approx(200, abs=4) and y0 == pytest.approx(300, abs=4)
    assert x1 == pytest.approx(967, abs=4) and y1 == pytest.approx(1335, abs=4)
    assert m.mm_por_ponto == pytest.approx((25.4 / 200, 25.4 / 200))
    assert m.tamanho_mm[0] == pytest.approx((x1 - x0) * 25.4 / 200, abs=0.2)


@precisa_da_dll
def test_medir_pagina_em_branco_nao_tem_conteudo():
    m = cc.medir(np.full((1654, 1165, 3), 255, np.uint8), 200.0, 200.0)
    assert m.disponivel and not m.tem_conteudo
    assert cc.caixa_do_corte(m) is None


def test_medir_sem_dll_volta_sem_caixa(monkeypatch):
    """Sem a DLL: sem caixa e com o motivo; nada levanta exceção."""
    class SemDLL:
        motivo_indisponivel = "A DLL não abriu."
        detalhe_indisponivel = "teste"

        def funcao(self, nome):
            return None

    m = cc.medir(np.full((300, 200), 255, np.uint8), 150.0, 150.0, biblioteca=SemDLL())
    assert not m.disponivel and not m.tem_conteudo
    assert m.motivo


def test_g8_corte_maior_so_tira_menos():
    """As candidatas são medidas uma vez, no corte da própria página; quando o
    corte cresce até o tamanho do livro, a conta barata dá o mesmo que medir de
    novo (o número da página entra; a barra, atravessada, continua)."""
    cinza, pecas = _pagina_com_numero_e_moldura()
    pequeno = (490.0, 590.0, 1510.0, 2010.0)
    grande = (300.0, 500.0, 1560.0, 2400.0)
    guardadas = cc.candidatas(pequeno, pecas, cinza, (MM, MM))
    assert cc.tiradas_do_corte(grande, guardadas) == cc.tinta_tirada(grande, pecas, cinza, (MM, MM))
    assert cc.tiradas_do_corte(grande, guardadas) == [(1550.0, 400.0, 1600.0, 2200.0)]
