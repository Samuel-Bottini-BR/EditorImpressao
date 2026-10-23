"""A regra ajustada do "Para revisar" (core/revisar.py), em paginas sinteticas.

Pedido do Samuel (rodada 4 do "Para revisar", 08/10/2026, `rv4-resumo`): "Fica
assim" para a regra ajustada. A prova nas 89 paginas do estudo (21 vao, 78
certas) e do script relatorios/para-revisar-impl/conferir_89.py; aqui se cobra,
em paginas pequenas feitas a mao, que cada conta diz "sim" e "nao" onde deve.
Testes de maquina: nenhum abre janela nem le PDF.
"""

from __future__ import annotations

import numpy as np
import pytest

from core import analise, revisar

ALT, LARG = 1000, 800
H = 20.0                     # altura de linha das paginas sinteticas


def _pagina():
    """Pagina vazia: (cinza claro, tinta de base, linhas, imagem, poligonos)."""
    cinza = np.full((ALT, LARG), 220, np.uint8)
    vazio = np.zeros((ALT, LARG), bool)
    return cinza, vazio.copy(), vazio.copy(), vazio.copy(), []


def _linha(cinza, base, linhas, poligonos, y, x0=100, x1=700, tom=30):
    """Uma linha de texto de 20 pontos de altura, feita de tracinhos."""
    for x in range(x0, x1, 12):
        cinza[y:y + 20, x:x + 5] = tom
        base[y:y + 20, x:x + 5] = True
    linhas[y - 3:y + 23, x0 - 3:x1 + 3] = True
    poligonos.append([[x0, y], [x1, y], [x1, y + 20], [x0, y + 20]])


def _texto(n=6):
    cinza, base, linhas, imagem, pol = _pagina()
    for i in range(n):
        _linha(cinza, base, linhas, pol, 200 + 40 * i)
    return cinza, base, linhas, imagem, pol


@pytest.mark.parametrize("q", [2, 60, 90, 50, 0, 100])
def test_o_percentil_rapido_e_o_do_numpy(q):
    rng = np.random.default_rng(q)
    for forma in ((37, 53), (1, 1), (200, 3)):
        a = rng.integers(0, 256, forma, dtype=np.uint8)
        assert revisar._percentil(a, q) == pytest.approx(float(np.percentile(a, q)), abs=1e-9)
        recorte = a[::2, ::1]                       # pedaco nao contiguo
        assert revisar._percentil(recorte, q) == pytest.approx(float(np.percentile(recorte, q)),
                                                             abs=1e-9)


def test_texto_corrido_inteiro_nao_vai():
    cinza, base, linhas, imagem, pol = _texto()
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H)
    assert revisar.motivos(s) == []
    assert s.linhas_fortes == 6 and s.falhadas == 0


def test_letra_grande_que_some_e_desenho_apagado():
    """A letra T do Antiphonal 46: pouca tinta perto da pagina, mas um pedaco
    cheio e grande, colado no texto, sumiu inteiro."""
    cinza, base, linhas, imagem, pol = _texto()
    base[445:475, 100:160] = True              # 1800 pontos = 4,5 alturas de linha ao quadrado
    cinza[445:475, 100:160] = 120
    resultado = base.copy()
    resultado[445:475, 100:160] = False        # o jeito de fabrica apagou
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.maior_pedaco >= revisar.PEDACO_GRANDE
    assert revisar.motivos(s) == [analise.DESENHO_APAGADO]
    # onde sumiu: uma caixa em volta da letra
    assert s.onde_sumiu
    x0, y0, x1, y1 = s.onde_sumiu[0]
    assert x0 * LARG <= 105 and x1 * LARG >= 155 and y0 * ALT <= 450 and y1 * ALT >= 470
    # no "Guardar só o texto" a conta do desenho nao vale
    assert revisar.motivos(s, desenho_apagado_vale=False) == []


def test_os_dois_limites_reacertados_para_o_preparo_do_livro_novo():
    """Reacerto de 13/10/2026 (relatorios/para-revisar-impl/reacerto-dos-limites.md):
    com o preparo do livro novo (endireitar antes de cortar), a letra T do
    Antiphonal 46 mede 1,43 alturas de linha ao quadrado (no dia do estudo,
    1,57) e a linha vermelha do Egenloff 3 guarda 0,148 da tinta. Os limites
    de antes (1,5 e 0,20) deixavam as duas paginas de fora. Quem mudar estes
    numeros tem de rodar reacertar_limites.py e ver as 89 paginas de novo."""
    assert revisar.PEDACO_GRANDE == 1.2
    assert revisar.GUARDA_MINIMA == 0.13
    # os outros continuam os da rodada 4
    assert (revisar.LIMITE_JUNTO, revisar.LIMITE_APAGADO, revisar.LIMITE_VAZOU,
            revisar.LIMITE_BEIRADA, revisar.LIMITE_SEM_CONTEUDO, revisar.LIMITE_GUARDA,
            revisar.FRACAO_VIRA_AVISO_DO_LIVRO) == (0.02, 0.025, 0.10, 0.03, 0.005, 0.62, 0.7)


def test_letra_grande_do_tamanho_da_t_do_antiphonal_46_no_preparo_novo():
    """Um pedaco cheio de 1,4 altura de linha ao quadrado, colado no texto,
    numa pagina com muita tinta (as outras duas contas do desenho apagado nao
    chegam): com o limite de antes (1,5) nao ia; com 1,2 vai."""
    cinza, base, linhas, imagem, pol = _texto(n=18)
    # 20 x 28 = 560 pontos = 1,4 altura de linha ao quadrado (altura 20)
    base[925:945, 100:128] = True
    resultado = base.copy()
    resultado[925:945, 100:128] = False
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.apagado_a < revisar.LIMITE_JUNTO, "so a conta do pedaco grande pode pegar"
    assert 1.3 < s.maior_pedaco < 1.5
    assert revisar.motivos(s) == [analise.DESENHO_APAGADO]
    # um pedaco de 1,0 (20 x 20) continua sem ir
    base[925:945, 120:128] = False
    resultado[925:945, 120:128] = False
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert analise.DESENHO_APAGADO not in revisar.motivos(s)


def test_a_linha_que_guarda_15_por_cento_conta_como_falhada():
    """A linha vermelha do Egenloff 3 no preparo novo guarda 0,148 da tinta;
    com o minimo de antes (0,20) ela era dada como "sumiu inteira"."""
    cinza, base, linhas, imagem, pol = _texto()
    pb = base.copy()
    pb[200:220:2, :] = False                       # uma linha pela metade (0,5)
    pb[240:260, :] = False
    pb[240:243, :] = base[240:243, :]              # outra guarda 3 fileiras de 20: 0,15
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H, tinta_pb=pb)
    assert sorted(round(g, 2) for g in s.guardas)[:2] == [0.15, 0.5]
    assert s.falhadas == 2 and s.texto_falhado
    # com 2 fileiras de 20 (0,10) a linha sumiu inteira: nao conta
    pb[242, :] = False
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H, tinta_pb=pb)
    assert s.falhadas == 1 and not s.texto_falhado


def test_pedaco_apagado_longe_do_texto_nao_e_letra_grande():
    cinza, base, linhas, imagem, pol = _texto()
    base[800:830, 400:460] = True
    resultado = base.copy()
    resultado[800:830, 400:460] = False
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    # (a pagina ainda pode ir pelas outras duas contas do desenho apagado, que
    # olham quanta tinta sumiu; aqui se cobra so a conta do pedaco grande)
    assert s.maior_pedaco == 0.0


def test_o_que_some_so_na_faixa_da_beirada_nao_conta():
    """A tarja da biblioteca e o fundo do scanner: ir para o branco e o certo."""
    cinza, base, linhas, imagem, pol = _texto()
    base[ALT - 30:ALT, 50:750] = True          # barra colada no pe, toda na faixa de fora
    resultado = base.copy()
    resultado[ALT - 30:ALT, 50:750] = False
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.apagado_a == 0.0 and not s.desenho_apagado


def test_muita_tinta_apagada_amontoada_e_desenho_apagado():
    cinza, base, linhas, imagem, pol = _texto()
    yy, xx = np.mgrid[600:800, 200:600]
    hachura = ((xx + yy) % 6 == 0)             # tracinhos finos, espalhados
    base[600:800, 200:600] |= hachura
    resultado = base.copy()
    resultado[600:800, 200:600] = False
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.apagado_junto >= revisar.LIMITE_JUNTO
    assert analise.DESENHO_APAGADO in revisar.motivos(s)
    assert s.onde_sumiu


def test_texto_falhado_nos_dois_jeitos():
    """Letra clara: o preto e branco guarda so metade da tinta da linha."""
    cinza, base, linhas, imagem, pol = _texto()
    pb = base.copy()
    for y in (200, 240, 280):                  # tres linhas saem pela metade
        pb[y:y + 20:2, :] = False
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H, tinta_pb=pb)
    assert s.falhadas == 3 and s.linhas_contadas == 6
    assert revisar.motivos(s) == [analise.TEXTO_FALHADO]
    assert len(s.linhas_falhadas) == 3


def test_linha_que_some_inteira_nao_e_texto_falhado():
    """Abaixo de 20% a linha sumiu inteira: e carimbo ou lapis, que se quer tirar."""
    cinza, base, linhas, imagem, pol = _texto()
    pb = base.copy()
    for y in (200, 240, 280):
        pb[y:y + 20, :] = False
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H, tinta_pb=pb)
    assert s.falhadas == 0 and not s.texto_falhado


def test_uma_linha_falhada_so_nao_basta():
    cinza, base, linhas, imagem, pol = _texto()
    pb = base.copy()
    pb[200:220:2, :] = False
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H, tinta_pb=pb)
    assert s.falhadas == 1 and not s.texto_falhado


def test_pagina_em_branco_e_sem_conteudo():
    cinza, base, linhas, imagem, pol = _pagina()
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, 0.0)
    assert revisar.motivos(s) == [analise.PAGINA_SEM_CONTEUDO]


def test_so_a_mancha_do_verso_e_sem_conteudo():
    """Tres linhas fracas (o leitor leu a mancha da pagina de tras) e nada forte."""
    cinza, base, linhas, imagem, pol = _pagina()
    for y in (300, 340, 380):
        _linha(cinza, np.zeros_like(base), linhas, pol, y, tom=190)
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H)
    assert s.linhas_fracas == 3 and s.linhas_fortes == 0
    assert analise.PAGINA_SEM_CONTEUDO in revisar.motivos(s)


def test_pagina_com_titulo_tem_conteudo():
    """A Gladstone 18 (so o titulo "DA ORAÇÃO"): tem uma linha forte, e tinta
    forte no miolo acima do limite - nao e pagina sem conteudo."""
    cinza, base, linhas, imagem, pol = _pagina()
    cinza[400:440, 200:600] = 20               # um titulo cheio
    base[400:440, 200:600] = True
    pol.append([[200, 400], [600, 400], [600, 440], [200, 440]])
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, 40.0)
    assert not s.pagina_sem_conteudo


def test_faixa_escura_na_beirada():
    cinza, base, linhas, imagem, pol = _texto()
    resultado = base.copy()
    resultado[:, :60] = True                   # o fundo do scanner sobrou a esquerda (7,5%)
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.beirada_a >= revisar.LIMITE_BEIRADA
    assert revisar.motivos(s) == [analise.FAIXA_NA_BEIRADA]
    # quando a faixa ja e aviso do livro, a pagina nao vai por ela
    assert revisar.motivos(s, faixa_do_livro=True) == []


def test_fio_fino_na_beirada_nao_e_faixa():
    cinza, base, linhas, imagem, pol = _texto()
    resultado = base.copy()
    resultado[:, 2:5] = True
    s = revisar.medir(cinza, base, linhas, imagem, resultado, pol, H)
    assert s.beirada_a == 0.0


def test_figura_que_passa_da_gravura_achada():
    cinza, base, linhas, imagem, pol = _texto()
    imagem[600:800, 200:500] = True
    base[610:790, 210:490] = True              # a gravura (dentro da area achada)
    base[650:750, 498:700] = True              # ...e o pedaco que passou para fora
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H)
    assert s.vazou_da_gravura >= revisar.LIMITE_VAZOU
    assert revisar.motivos(s) == [analise.FIGURA_ALEM_DA_GRAVURA]


def test_no_guardar_so_o_texto_vale_a_tinta_forte_apagada():
    cinza, base, linhas, imagem, pol = _texto()
    forte = np.zeros_like(base)
    forte[600:700, 200:600] = True             # a "musica" que o jeito apagou
    s = revisar.medir(cinza, base, linhas, imagem, base.copy(), pol, H,
                      tinta_forte_apagada=forte, com_o_desenho_apagado=False)
    assert s.onde_sumiu == [] and s.onde_sumiu_a_tinta_forte
    assert revisar.motivos(s, desenho_apagado_vale=False, tinta_forte_apagada=0.30) == [
        analise.SO_O_TEXTO_APAGOU]
    assert revisar.motivos(s, desenho_apagado_vale=False, tinta_forte_apagada=0.05) == []


def test_a_ordem_dos_motivos():
    s = revisar.Sinais(apagado_a=0.5, vazou_da_gravura=0.5, beirada_a=0.5, falhadas=2,
                       linhas_contadas=5, sem_conteudo=0.0, linhas_fortes=0)
    assert revisar.motivos(s) == [
        analise.DESENHO_APAGADO, analise.TEXTO_FALHADO, analise.PAGINA_SEM_CONTEUDO,
        analise.FIGURA_ALEM_DA_GRAVURA, analise.FAIXA_NA_BEIRADA]
    for codigo in revisar.motivos(s):
        assert codigo in analise.AVISOS_DO_SO_AS_LETRAS
        assert analise.descrever(codigo).titulo != codigo, "todo motivo tem nome na tela"


def test_faixa_no_livro_e_em_70_por_cento():
    assert revisar.faixa_no_livro([True] * 7 + [False] * 3)
    assert not revisar.faixa_no_livro([True] * 6 + [False] * 4)
    assert not revisar.faixa_no_livro([])


def test_as_caixas_cabem_na_pagina_e_sao_poucas():
    mascara = np.zeros((ALT, LARG), bool)
    for i in range(10):
        mascara[50 + 90 * i:70 + 90 * i, 100:130 + 10 * i] = True
    caixas = revisar.caixas_de(mascara, H)
    assert 0 < len(caixas) <= revisar.MAXIMO_DE_CAIXAS
    for x0, y0, x1, y1 in caixas:
        assert 0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0
    assert revisar.caixas_de(np.zeros((ALT, LARG), bool), H) == []


def test_os_textos_dos_avisos_tem_acento_e_nao_tem_jargao():
    for codigo in analise.AVISOS_DO_SO_AS_LETRAS:
        alerta = analise.descrever(codigo)
        texto = (alerta.titulo + " " + alerta.mensagem).lower()
        for palavra in ("ocr", "máscara", "mascara", "misto", "binariz", "pixel"):
            assert palavra not in texto, (codigo, palavra)
    assert "página" in analise.descrever(analise.PAGINA_SEM_CONTEUDO).mensagem
