"""Consertos da conferencia 6 do Samuel (02/10/2026), testes de maquina.

Respostas literais em relatorios/conferencia-samuel-2026-10-02.md. Cada teste
diz o cartao que ele protege. As imagens sao sinteticas (pequenas e rapidas);
o teste de olho e a rodada de antes/depois nas paginas-gabarito
(relatorios/conferir/conferencia-6-consertos-2026-10-02/).
"""

from __future__ import annotations

import cv2
import numpy as np

from core import filtros as F

PAPEL = 225


def _pagina_com_moldura_escura_e_letra_clara():
    """Uma folha como a Horas 47 no cinza: uma moldura larga e escura (que puxa
    o limiar do Otsu para baixo) e, no meio, linhas de "letras" de traco fino,
    mais claras que a moldura e com a beirada macia (scan de baixa resolucao
    ampliado). Devolve (cinza, mascara do traco desenhado)."""
    cinza = np.full((1400, 1000), PAPEL, np.uint8)
    cv2.rectangle(cinza, (0, 0), (999, 1399), 55, 230)            # a moldura
    traco = np.zeros(cinza.shape, np.uint8)
    for y in range(330, 1050, 70):
        for x in range(300, 680, 38):
            cv2.ellipse(traco, (x, y), (13, 20), 0, 0, 360, 255, 6)   # um "o"
            cv2.line(traco, (x + 15, y - 20), (x + 15, y + 20), 255, 6)
    letra = np.where(traco > 0, 110, PAPEL).astype(np.uint8)
    letra = cv2.GaussianBlur(letra, (0, 0), 2.5)                  # beirada macia
    dentro = np.zeros(cinza.shape, bool)
    dentro[260:1140, 260:740] = True
    cinza[dentro] = letra[dentro]
    return cinza, traco > 0


# --- A1: "Ainda esta apagando as letras, o original esta muito melhor para ler"


def test_a_folha_com_moldura_escura_vai_para_o_otsu():
    """O caso da Horas 47: a escolha automatica poe o Otsu (o traco medido e
    grosso por causa da moldura)."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    assert F.escolher_algoritmo_automatico(cinza) == F.ALGORITMO_OTSU


def test_a_letra_clara_nao_sai_picotada():
    """Com o Otsu sozinho a letra clara sai fina e falhada; com a borda do
    Sauvola ela sai com o traco que foi desenhado."""
    cinza, traco = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    so_otsu = F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU) == 0
    agora = F.filtro_preto_e_branco(img) == 0
    cheio_otsu = float(so_otsu[traco].mean())
    cheio_agora = float(agora[traco].mean())
    # medido: Otsu sozinho 61% do traco desenhado (a beirada macia some),
    # com a borda do Sauvola 91%
    assert cheio_agora >= 0.85, f"a letra saiu falhada: so {cheio_agora:.0%} do traco"
    assert cheio_agora > cheio_otsu + 0.2


def test_a_escolha_a_mao_do_otsu_continua_o_otsu():
    """Quem escolhe "Otsu" a mao recebe o Otsu, sem a borda do Sauvola."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    a_mao = F.filtro_preto_e_branco(img, algoritmo=F.ALGORITMO_OTSU, despeckle=False)
    otsu = F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU)
    assert np.array_equal(a_mao, otsu)


def test_risco_fraco_solto_nao_vira_preto():
    """O risco fraco que nao encosta em letra (a pauta a ponta seca do
    Graduale, a mancha) nao entra: o Sauvola sozinho o marcaria."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    cinza[1080:1084, 300:700] = 185                   # um risco fraco, solto
    janela = F.janela_para_altura(cinza.shape[0])
    otsu = F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU)
    sauvola = F.binarizar(cinza, janela=janela, k=0.12)
    assert (sauvola[1080:1084, 300:700] == 0).mean() > 0.5, "o teste perdeu o sentido"
    junto = F._otsu_com_a_borda_do_sauvola(cinza, otsu, janela, 0.12)
    assert (junto[1080:1084, 300:700] == 0).mean() < 0.05


def test_nada_do_otsu_sai():
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    janela = F.janela_para_altura(cinza.shape[0])
    otsu = F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU)
    junto = F._otsu_com_a_borda_do_sauvola(cinza, otsu, janela, 0.12)
    assert not ((otsu == 0) & (junto == 255)).any()
    assert set(np.unique(junto)) <= {0, 255}


def test_a_escolha_automatica_numa_folha_grande_e_a_mesma():
    """Regra 6: na folha grande a medida reduzida decide sozinha so com folga
    (FOLGA_DA_MEDIDA_REDUZIDA); a resposta e a da medida cheia."""
    for grossura, esperado in ((60, F.ALGORITMO_OTSU), (3, F.ALGORITMO_SAUVOLA)):
        cinza = np.full((3200, 2200), PAPEL, np.uint8)
        for y in range(200, 3000, 160):
            cv2.line(cinza, (200, y), (2000, y), 40, grossura)
        F._KS_GUARDADOS.clear()
        assert F.escolher_algoritmo_automatico(cinza) == esperado


def test_o_k_continua_o_mesmo_com_a_espessura_guardada():
    """A espessura passou a ser guardada no lugar do k: o k sai igual ao da
    medida sem o cache."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    F._KS_GUARDADOS.clear()
    assert F.k_para_a_letra(cinza) == F._medir_k_para_a_letra(cinza)


# --- X2: "nao consigo ver o rosto mais, esses pontos estao horriveis" --------


def _foto_com_contorno_livre():
    """Uma foto de tom continuo (sem traco) ocupando quase a folha toda, e uma
    marcacao como a do contorno livre do Opus 20: a gravura com um buraco em
    cima a direita (~10% do fecho), e no buraco um pedaco de meio-tom (o
    rosto, marcado PAPEL) e um escuro (o vao da porta, marcado LETRA).
    Devolve (img, selecao)."""
    from core.selecao import GRAVURA, LETRA, Selecao, retangulo
    from core.selecao import PAPEL as PAPEL_

    altura, largura = 1500, 1000
    yy, xx = np.mgrid[0:altura, 0:largura]
    tom = (150 + 60 * np.sin(xx / 90.0) * np.cos(yy / 120.0)).astype(np.float32)
    ruido = np.random.default_rng(3).normal(0, 4, tom.shape).astype(np.float32)
    cinza = np.clip(tom + ruido, 0, 255).astype(np.uint8)
    cinza[200:500, 600:780] = 175                 # o "rosto", meio-tom
    cinza[200:500, 800:880] = 45                  # o "vao da porta", escuro
    img = cv2.merge([cinza, cinza, cinza])
    s = Selecao()
    # a foto toda menos um buraco em cima a direita (x 0,57-0,90, y 0,10-0,36)
    s.acrescentar(retangulo(0.05, 0.05, 0.95, 0.10, tipo=GRAVURA))
    s.acrescentar(retangulo(0.05, 0.10, 0.57, 0.36, tipo=GRAVURA))
    s.acrescentar(retangulo(0.90, 0.10, 0.95, 0.36, tipo=GRAVURA))
    s.acrescentar(retangulo(0.05, 0.36, 0.95, 0.95, tipo=GRAVURA))
    s.acrescentar(retangulo(0.58, 0.12, 0.79, 0.35, tipo=PAPEL_))
    s.acrescentar(retangulo(0.79, 0.12, 0.89, 0.35, tipo=LETRA))
    return img, s


def test_a_foto_do_contorno_livre_sai_como_a_foto_inteira_no_magico_pro():
    """O rosto (marcado papel) e o vao escuro (marcado letra) saem como com a
    foto marcada inteira ("Este livro tem fotos"): sem ir a branco e sem
    virar papel branco com pontinhos. Medido no exemplo: antes do conserto a
    diferenca media no buraco era ~50 tons (rosto e vao brancos)."""
    from core.filtros import aplicar_filtro_com_selecao
    from core.selecao import GRAVURA, Selecao, retangulo

    img, livre = _foto_com_contorno_livre()
    inteira = Selecao()
    inteira.acrescentar(retangulo(0.05, 0.05, 0.95, 0.95, tipo=GRAVURA))
    a, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", livre)
    b, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", inteira)
    buraco = (slice(200, 500), slice(600, 880))
    diferenca = cv2.absdiff(a[buraco], b[buraco])
    assert float(diferenca.mean()) < 3.0
    vao = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)[260:440, 815:865]
    assert float((vao > 200).mean()) < 0.05, "o vao escuro virou papel branco"


def test_a_foto_inteira_nao_mexe_na_foto_retangular():
    """Com a foto marcada inteira ("Este livro tem fotos"), nada muda."""
    from core.selecao import GRAVURA, Selecao, retangulo

    img, _s = _foto_com_contorno_livre()
    s = Selecao()
    s.acrescentar(retangulo(0.05, 0.05, 0.95, 0.95, tipo=GRAVURA))
    altura, largura = img.shape[:2]
    pg = s.peso(altura, largura, GRAVURA)
    zero = np.zeros_like(pg)
    assert F._a_foto_inteira(img, pg, zero, zero) is None
