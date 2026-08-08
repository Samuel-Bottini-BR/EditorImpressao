"""Os filtros lendo da selecao: cada area tratada do seu jeito."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
)
from core.selecao import GRAVURA, LETRA, PAPEL, Selecao, retangulo


def pagina_de_teste(altura=400, largura=300):
    """Meia pagina de gravura em degrade, meia de texto sobre papel amarelado."""
    img = np.zeros((altura, largura, 3), np.uint8)
    # papel amarelado
    img[:, :] = (190, 220, 235)
    # gravura na metade de cima: degrade cinza, tom continuo
    for y in range(altura // 2):
        img[y, :] = (60 + y // 2, 70 + y // 2, 90 + y // 2)
    # texto na metade de baixo
    for y in range(altura // 2 + 20, altura - 20, 24):
        img[y:y + 8, 30:largura - 30] = (25, 25, 25)
    return img


@pytest.fixture
def img():
    return pagina_de_teste()


# --- sem selecao nada muda --------------------------------------------------

@pytest.mark.parametrize("filtro", [ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_selecao_vazia_da_o_resultado_de_sempre(img, filtro):
    """Todo projeto antigo e toda pagina nao marcada caem aqui."""
    antes, mono_antes = aplicar_filtro(img.copy(), filtro)
    depois, mono_depois = aplicar_filtro_com_selecao(img.copy(), filtro, Selecao())
    assert mono_antes == mono_depois
    assert np.array_equal(antes, depois)


def test_selecao_none_tambem_e_aceita(img):
    antes, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    depois, _ = aplicar_filtro_com_selecao(img.copy(), MAGICO_PRO, None)
    assert np.array_equal(antes, depois)


# --- a gravura nao pode ser binarizada --------------------------------------

def test_preto_e_branco_preserva_tom_continuo_na_gravura(img):
    """Binarizar uma gravura de meio-tom e joga-la fora."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.5, tipo=GRAVURA))

    saida, mono = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, s)

    # a pagina deixa de caber em 1 bit, porque tem gravura em tom continuo
    assert mono is False

    metade = saida.shape[0] // 2
    gravura = saida[: metade - 10]
    tons = np.unique(cv2.cvtColor(gravura, cv2.COLOR_BGR2GRAY))
    assert len(tons) > 8, "a gravura foi binarizada"


def pagina_de_gravura_de_traco(altura=400, largura=300):
    """Uma xilogravura: hachura fina sobre papel amarelado, sem meio-tom."""
    # Papel amarelado, mas dentro da saturacao que o balanco de branco aceita
    # como papel - acima de BRANCO_SATURACAO_MAX ele desiste, por nao saber se
    # esta olhando papel ou uma capa colorida.
    img = np.full((altura, largura, 3), (196, 212, 226), np.uint8)
    for x in range(40, largura - 40, 6):       # hachura vertical
        img[60:340, x:x + 2] = (70, 75, 85)
    for y in range(150, 300, 6):               # hachura cruzada, mais fechada
        img[y:y + 2, 40:largura - 40] = (55, 60, 70)
    return img


def test_a_gravura_fica_com_o_papel_branco_sem_perder_o_traco():
    """O pedido do Samuel: papel branco E desenho perfeito.

    Antes desta correcao a gravura saia com o papel amarelado como veio, porque
    "nao binarizar" tinha virado "nao tocar". Medido na xilogravura da
    Rhetorica, o papel dentro do desenho parava em 214 numa escala em que 255 e
    branco, enquanto a margem da folha ia a 255.
    """
    img = pagina_de_gravura_de_traco()
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0, tipo=GRAVURA))

    saida, _ = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, s)
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)

    # O papel que interessa e o que fica ENTRE os tracos, e nao uma margem
    # limpa: e ele que dava a impressao de folha suja dentro do desenho.
    dentro = cinza[60:340, 40:260]
    claro = float(np.percentile(dentro, 85))
    assert claro >= 245, f"o papel entre os tracos nao clareou: {claro:.0f}"

    assert len(np.unique(dentro)) > 8, "a hachura foi binarizada"
    assert dentro.min() < 120, "a hachura sumiu no clareamento"


def test_preto_e_branco_sem_gravura_continua_em_um_bit(img):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.5, 1.0, 1.0, tipo=LETRA))
    _saida, mono = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, s)
    assert mono is True


# --- o papel vai a branco ---------------------------------------------------

@pytest.mark.parametrize("filtro", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_papel_marcado_fica_branco(img, filtro):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.3, 0.3, tipo=PAPEL))

    saida, _ = aplicar_filtro_com_selecao(img, filtro, s)
    canto = saida[5:100, 5:80]
    assert canto.min() >= 250, "o papel marcado nao ficou branco"


def test_o_que_esta_fora_do_papel_nao_e_afetado(img):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.3, 0.3, tipo=PAPEL))

    com, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    sem, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    # longe do canto marcado, o resultado e o mesmo
    assert np.array_equal(com[250:, 150:], sem[250:, 150:])


# --- a letra recebe so nitidez ----------------------------------------------

def test_letra_marcada_nao_recebe_realce_de_fundo(img):
    """Realce de fundo na letra e o que fabricava grao no papel em volta."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.5, 1.0, 1.0, tipo=LETRA))

    com, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    sem, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    metade = img.shape[0] // 2
    assert not np.array_equal(com[metade + 30:], sem[metade + 30:])


# --- a ordem e a mistura ----------------------------------------------------

def test_subtrair_devolve_a_area_ao_tratamento_comum(img):
    """O buraco tem de voltar a valer o tratamento comum, nao o do papel.

    A marcacao cobre a METADE DE CIMA, que na pagina de teste e a gravura
    escura: so ali a diferenca entre "virou branco" e "nao virou" aparece.
    """
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.5, tipo=PAPEL))
    s.acrescentar(retangulo(0.3, 0.1, 0.7, 0.4, tipo=PAPEL, operacao="subtrair"))

    saida, _ = aplicar_filtro_com_selecao(img, MELHORAR, s)
    assert saida[10, 10].min() >= 250        # fora do buraco: virou branco
    assert saida[100, 150].min() < 250       # dentro do buraco: continua gravura


def test_borda_suave_nao_deixa_degrau(img):
    """Corte seco entre area tratada e nao tratada aparece na impressao.

    A travessia tem de ser uma rampa com varios degraus intermediarios, e nao
    um salto de uma vez. Medido sobre a gravura, que e escura: sobre o papel
    claro os dois lados ja sao quase brancos e nao daria para ver diferenca.
    """
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 0.45, tipo=PAPEL, suavidade=0.08))

    saida, _ = aplicar_filtro_com_selecao(img, MELHORAR, s)
    linha = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)[100, :].astype(int)

    esquerda, direita = linha[20], linha[280]
    assert esquerda > direita + 40, "os dois lados deveriam ser bem diferentes"

    # na travessia ha varios valores entre um lado e o outro
    travessia = linha[110:190]
    intermediarios = ((travessia > direita + 10) & (travessia < esquerda - 10)).sum()
    assert intermediarios >= 10, "a borda saiu como degrau, nao como rampa"


# --- robustez ---------------------------------------------------------------

def test_pagina_em_cinza_tambem_funciona():
    cinza = np.full((200, 150), 200, np.uint8)
    cinza[80:120, 20:130] = 30
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.3, tipo=GRAVURA))
    saida, _ = aplicar_filtro_com_selecao(cinza, PRETO_E_BRANCO, s)
    assert saida.shape[:2] == cinza.shape[:2]


def test_selecao_so_de_tipo_ausente_nao_quebra(img):
    """Marcar so 'fora' nao muda o filtro, mas nao pode derrubar nada."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.2, 0.2, tipo="fora"))
    saida, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    assert saida.shape == img.shape


def test_filtro_so_no_pedaco_marcado():
    """Pedido: aplicar um filtro so numa parte, e o resto segue o da pagina.

    O caso concreto e a xilogravura da Rhetorica: a folha vai a Preto e branco,
    mas a gravura tem de ficar no Original, senao o meio-tom da hachura vira
    mancha preta.
    """
    import cv2
    import numpy as np

    from core.filtros import ORIGINAL, PRETO_E_BRANCO, aplicar_filtro_com_selecao
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

    pagina = np.full((400, 300, 3), 235, np.uint8)
    pagina[20:80, 20:280] = 40                       # uma linha de texto escura
    degrade = np.linspace(30, 220, 200).astype(np.uint8)
    pagina[180:380, 50:250] = degrade[None, :, None]  # a gravura, em meio-tom

    selecao = Selecao()
    selecao.acrescentar(Regiao(
        tipo=GRAVURA, forma=RETANGULO, pontos=[(0.16, 0.44), (0.84, 0.96)],
        origem=MAO, filtro=ORIGINAL))

    saida, mono = aplicar_filtro_com_selecao(
        pagina.copy(), PRETO_E_BRANCO, selecao)
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY) if saida.ndim == 3 else saida

    assert not mono, "com um pedaco em tom continuo a pagina nao cabe em 1 bit"

    tons_no_texto = len(np.unique(cinza[10:100, 10:290]))
    tons_na_gravura = len(np.unique(cinza[200:360, 70:230]))
    assert tons_no_texto <= 4, f"o texto tinha de sair binarizado: {tons_no_texto}"
    assert tons_na_gravura > 30, f"a gravura perdeu o meio-tom: {tons_na_gravura}"


def test_regiao_sem_filtro_proprio_segue_a_pagina():
    """Sem filtro na regiao, tudo continua como sempre foi."""
    import numpy as np

    from core.filtros import PRETO_E_BRANCO, aplicar_filtro_com_selecao
    from core.selecao import LETRA, MAO, RETANGULO, Regiao, Selecao

    pagina = np.full((300, 200, 3), 230, np.uint8)
    pagina[40:80, 20:180] = 40

    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO,
                               pontos=[(0.05, 0.10), (0.95, 0.30)], origem=MAO))
    saida, _mono = aplicar_filtro_com_selecao(pagina.copy(), PRETO_E_BRANCO, selecao)
    assert saida is not None and saida.size > 0


def test_o_amarelado_da_tinta_sai_e_a_cor_de_verdade_fica():
    """A tinta velha e marrom, e a impressora imprime isso como cor.

    O Samuel apontou: "melhorar e magico pro nao estao deixando a pagina
    totalmente branca... e isso e ruim porque a impressora vai entender como cor
    a ser impressa, mesmo em preto e branco". A cor nao estava no fundo, que ja
    saia em 250; estava na TINTA e na orla de cada letra.

    O que nao pode acontecer e a rubricacao vermelha desbotar junto.
    """
    import cv2
    import numpy as np

    from core.filtros import SATURACAO_DE_RUBRICA, tirar_o_amarelado_da_tinta

    pagina = np.full((200, 200, 3), 250, np.uint8)
    pagina[40:60, 20:180] = (170, 185, 200)     # tinta marrom, saturacao ~38
    pagina[120:140, 20:180] = (40, 40, 220)     # rubricacao vermelha forte

    saida = tirar_o_amarelado_da_tinta(pagina)
    sat = cv2.cvtColor(saida, cv2.COLOR_BGR2HSV)[:, :, 1]

    # a rampa e proporcional: quanto mais perto do grao, mais se tira.
    # A tinta do fixture tem saturacao 38 e cai para 15.
    assert sat[45:55, 30:170].mean() < 20, "o marrom da tinta tinha de sair"
    assert sat[125:135, 30:170].mean() > SATURACAO_DE_RUBRICA * 0.8, \
        "a rubricacao vermelha nao pode desbotar"


def test_o_papel_dentro_da_regiao_segue_a_pagina():
    """Marcar um retangulo em volta da gravura pega papel junto.

    Esse papel nao pode ficar no filtro da regiao: sai creme ao lado do branco
    do resto, e vira uma faixa cinza no pe da gravura. Foi o que o Samuel
    apontou circulando de vermelho.
    """
    import cv2
    import numpy as np

    from core.filtros import ORIGINAL, PRETO_E_BRANCO, aplicar_filtro_com_selecao
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

    pagina = np.full((400, 300, 3), 205, np.uint8)   # papel creme
    pagina[20:60, 20:280] = 40                        # texto
    degrade = np.linspace(30, 200, 160).astype(np.uint8)
    pagina[150:290, 60:220] = degrade[None, :, None]  # a gravura

    selecao = Selecao()
    selecao.acrescentar(Regiao(                        # o retangulo pega papel
        tipo=GRAVURA, forma=RETANGULO, pontos=[(0.10, 0.35), (0.90, 0.95)],
        origem=MAO, filtro=ORIGINAL))

    saida, _mono = aplicar_filtro_com_selecao(
        pagina.copy(), PRETO_E_BRANCO, selecao)
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY) if saida.ndim == 3 else saida

    # Antes do conserto o pe ficava no filtro da regiao - Original -, ou
    # seja, no creme de 205 em que a folha entrou. Agora ele e branqueado
    # como o resto do papel.
    no_pe = cinza[int(400 * 0.80):int(400 * 0.93), 80:200].mean()
    assert no_pe > 225, f"o pe da regiao ficou no creme: {no_pe:.0f}"
    assert no_pe > 205 + 20, "o pe nao foi branqueado"

    # e a gravura em si continua em tom continuo
    na_gravura = cinza[170:270, 70:210]
    assert len(np.unique(na_gravura)) > 30, "a gravura perdeu o meio-tom"
