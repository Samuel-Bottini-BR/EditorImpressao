"""A regra ajustada do "Para revisar" no "Só as letras" (Fase 2, 12/10/2026).

O PEDIDO
    Samuel, rodada 4 do "Para revisar" (08/10/2026, `rv4-resumo`): "Fica assim"
    para a regra ajustada (relatorios/revisar-decisoes/rodada-4/LEIA-ME.md).
    Nas 89 paginas do estudo, o aviso de antes ("Tinta forte fora do texto",
    mais de 10% da tinta) mandava 55 paginas e acertava 52; a regra ajustada
    manda 21 e acerta 78. E `rv4-pag-antiphonal1547-006`: "Entendi; a página
    não precisa ir" (a pauta com pouca falha nao vai para a lista).

O QUE FAZ
    medir() olha a pagina JA FILTRADA pelo "Só as letras" e devolve os sinais
    (Sinais); motivos() diz, a partir deles, por quais motivos a pagina vai
    para "Para revisar" (os codigos de core/analise.py):

    1. DESENHO APAGADO (so no jeito de fabrica, "Guardar a tinta forte"):
       tinta que o Preto e branco de sempre imprime, fora das linhas de texto e
       das gravuras, e que NAO esta no resultado. Vai quando essa tinta e 2,5%
       ou mais de toda a tinta, ou 2% amontoada, ou quando um pedaco cheio e
       grande (1,5 altura de linha ao quadrado ou mais) colado no texto sumiu
       (a letra T vermelha do Antiphonal 46). O que fica so na faixa da
       beirada (tarja da biblioteca, fundo do scanner) nao conta.
    2. FIGURA ALEM DA GRAVURA ACHADA: pedacos grandes de tinta encostados por
       fora na gravura achada somam 10% ou mais da tinta.
    3. FAIXA ESCURA NA BEIRADA: mancha cheia de tinta encostada na beirada do
       resultado, 3% ou mais da pagina. Em 70% ou mais das paginas do livro,
       vira um aviso so, do livro (faixa_no_livro; quem junta e core.pipeline).
    4. TEXTO FALHADO NOS DOIS JEITOS: 2 ou mais linhas compridas em que o preto
       e branco guarda entre 20% e 62% da tinta clara da letra, ou todas as
       linhas contadas. Abaixo de 20% a linha sumiu inteira: no acervo isso e
       carimbo e anotacao a lapis, que se quer tirar.
    5. PAGINA SEM CONTEUDO: quase nenhuma tinta forte no miolo (menos de 0,5%),
       no maximo 1 linha forte e (3 ou mais linhas fracas, ou nenhuma forte).
    E, so no "Guardar só o texto" (que apaga de proposito tudo o que nao e
    linha): SUMIU ALGO, quando a tinta forte apagada passa de 10% da tinta (a
    conta do aviso antigo, que ali continua valendo: a musica do Graduale 222).

    As contas sao as dos scripts do estudo, copiadas sem mudar limite nenhum
    (relatorios/revisar-decisoes/rodada-4/scripts: sinais4.py, sinais.py,
    medir.py, criterio.py, regra4.py). A prova de que dao o mesmo esta em
    relatorios/para-revisar-impl/conferir_89.py.

    medir() tambem devolve ONDE SUMIU (caixas em fracao da pagina), para o
    aviso mostrar o lugar marcado (Samuel, rodada 5, `rv5-erro-1-desenho`:
    "onde sumiu, tem que aparecer selecionado automaticamente").

O QUE E SEGURO MUDAR
    Os textos; MAXIMO_DE_CAIXAS e a folga das caixas (so mudam o desenho da
    marca, nunca quem vai para a lista).

O QUE E ARRISCADO MUDAR
    Qualquer limite (os numeros 21 e 78 foram aprovados com estes); a ordem das
    contas dentro de _apagado (a peca da beirada sai ANTES de medir o
    amontoado); trocar o elemento redondo de _maior_pedaco por quadrado (a
    letra T do Antiphonal 46 da 1,6, colada no limite de 1,5).

Nao importa ui/. Uma pagina por vez. Custa umas rotulacoes de pedacos da
pagina (tempo medido em relatorios/para-revisar-impl/ONDE-PAREI.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from core import analise

# --- os limites aprovados (rodada 4; ver o topo) ----------------------------
LIMITE_JUNTO = 0.02             # desenho apagado: tinta apagada amontoada
LIMITE_APAGADO = 0.025          # desenho apagado: tinta apagada ao todo
PEDACO_GRANDE = 1.5             # desenho apagado: o maior pedaco, em alturas de linha ao quadrado
LIMITE_VAZOU = 0.10             # figura alem da gravura achada
LIMITE_BEIRADA = 0.03           # faixa escura na beirada (fracao da pagina)
FRACAO_VIRA_AVISO_DO_LIVRO = 0.7
LIMITE_SEM_CONTEUDO = 0.005     # pagina sem conteudo: tinta forte no miolo
LIMITE_GUARDA = 0.62            # texto falhado: guarda menos que isto...
GUARDA_MINIMA = 0.20            # ...e pelo menos isto (abaixo, a linha sumiu inteira)
LIMITE_JUNTO_DENS = 0.04        # o que e "amontoado": mais de 4% apagado na janela
# "Guardar só o texto": a tinta forte que ele apaga, em fracao de toda a tinta.
# E o limite do aviso antigo (core.pipeline.LIMITE_DA_TINTA_FORTE_FORA ate
# 12/10/2026), medido na conferencia 8: Graduale 222 76%, texto corrido < 4%.
LIMITE_SO_O_TEXTO = 0.10

# Quantas caixas de "onde sumiu" o aviso mostra, no maximo (as maiores).
MAXIMO_DE_CAIXAS = 6

Caixa = tuple[float, float, float, float]       # x0, y0, x1, y1 em fracao da pagina


@dataclass
class Sinais:
    """O que medir() achou numa pagina (ver o topo para o que cada um e)."""

    apagado_a: float = 0.0
    apagado_junto: float = 0.0
    maior_pedaco: float = 0.0
    vazou_da_gravura: float = 0.0
    beirada_a: float = 0.0
    falhadas: int = 0
    linhas_contadas: int = 0
    sem_conteudo: float = 1.0
    linhas_fortes: int = 0
    linhas_fracas: int = 0
    # onde o desenho sumiu (jeito de fabrica) e onde a tinta forte sumiu
    # ("Guardar só o texto"): caixas em fracao da pagina, as maiores primeiro
    onde_sumiu: list[Caixa] = field(default_factory=list)
    onde_sumiu_a_tinta_forte: list[Caixa] = field(default_factory=list)
    # as linhas falhadas: (x0, y0, x1, y1) em fracao da pagina
    linhas_falhadas: list[Caixa] = field(default_factory=list)

    @property
    def desenho_apagado(self) -> bool:
        return (self.apagado_junto >= LIMITE_JUNTO or self.apagado_a >= LIMITE_APAGADO
                or self.maior_pedaco >= PEDACO_GRANDE)

    @property
    def figura_alem_da_gravura(self) -> bool:
        return self.vazou_da_gravura >= LIMITE_VAZOU

    @property
    def faixa_na_beirada(self) -> bool:
        return self.beirada_a >= LIMITE_BEIRADA

    @property
    def texto_falhado(self) -> bool:
        return self.falhadas >= 2 or (self.linhas_contadas > 0
                                      and self.falhadas == self.linhas_contadas)

    @property
    def pagina_sem_conteudo(self) -> bool:
        return (self.sem_conteudo < LIMITE_SEM_CONTEUDO and self.linhas_fortes <= 1
                and (self.linhas_fracas >= 3 or self.linhas_fortes == 0))


def motivos(sinais: Sinais, desenho_apagado_vale: bool = True, tinta_forte_apagada: float = 0.0,
            faixa_do_livro: bool = False) -> list[str]:
    """Os codigos de alerta (core/analise.py) que a pagina ganha, na ordem em
    que aparecem na tela (o primeiro e o que a faixa mostra).

    desenho_apagado_vale: True no jeito de fabrica ("Guardar a tinta forte").
        No "Guardar só o texto" tudo o que nao e linha vai a branco de
        proposito, e a conta do desenho apagado diria "sim" em toda pagina; ali
        vale tinta_forte_apagada (a fracao da tinta que e tinta forte apagada,
        `forte_fora` de core.misto), contra LIMITE_SO_O_TEXTO.
    faixa_do_livro: a faixa na beirada ja e aviso do livro inteiro (nao volta
        para as paginas).
    """
    m: list[str] = []
    if desenho_apagado_vale:
        if sinais.desenho_apagado:
            m.append(analise.DESENHO_APAGADO)
    elif tinta_forte_apagada > LIMITE_SO_O_TEXTO:
        m.append(analise.SO_O_TEXTO_APAGOU)
    if sinais.texto_falhado:
        m.append(analise.TEXTO_FALHADO)
    if sinais.pagina_sem_conteudo:
        m.append(analise.PAGINA_SEM_CONTEUDO)
    if sinais.figura_alem_da_gravura:
        m.append(analise.FIGURA_ALEM_DA_GRAVURA)
    if sinais.faixa_na_beirada and not faixa_do_livro:
        m.append(analise.FAIXA_NA_BEIRADA)
    return m


def faixa_no_livro(com_faixa: list[bool]) -> bool:
    """A faixa na beirada esta em 70% ou mais das paginas medidas do livro?
    (ai ela e do livro, nao da pagina: Samuel, rodada 1, "avisar uma vez no
    livro"; rodada 4, Camoes 66: "aviso no livro basta"). Lista vazia: nao."""
    if not com_faixa:
        return False
    return sum(1 for v in com_faixa if v) / len(com_faixa) >= FRACAO_VIRA_AVISO_DO_LIVRO


# ---------------------------------------------------------------------------
# as contas (copias dos scripts do estudo; ver o topo)
# ---------------------------------------------------------------------------

def _percentil(a: np.ndarray, q: float) -> float:
    """np.percentile(a, q), igual ate o ultimo bit, mais rapido em imagem de
    8 bits (pela contagem dos 256 valores em vez de ordenar a pagina)."""
    if a.dtype != np.uint8 or a.size == 0:
        return float(np.percentile(a, q))
    contagem = np.bincount(a.reshape(-1), minlength=256)
    acumulado = np.cumsum(contagem)
    posicao = (a.size - 1) * q / 100.0
    baixo, alto = int(np.floor(posicao)), int(np.ceil(posicao))
    v_baixo = int(np.searchsorted(acumulado, baixo + 1))
    v_alto = int(np.searchsorted(acumulado, alto + 1))
    return float(v_baixo + (v_alto - v_baixo) * (posicao - baixo))


def _apagado(base_tinta: np.ndarray, linhas: np.ndarray, imagem: np.ndarray,
             tinta_do_resultado: np.ndarray, h: float, completo: bool = False):
    """(apagado_a, apagado_junto, mascara apagada, mascara amontoada): a tinta
    do Preto e branco de base, fora das linhas e das gravuras, que nao esta no
    resultado (sinais4.apagado_real). As pecas que encostam na beirada (1% da
    pagina) e ficam inteiras na faixa de fora (6% de um lado) nao contam: sao a
    tarja da biblioteca e o fundo do scanner, que ir para o branco e o certo.

    Atalho (so muda o tempo, nunca a decisao): o amontoado e parte do apagado;
    se o apagado todo nao chega a LIMITE_JUNTO, o amontoado tambem nao chega,
    e a conta dele (um filtro na pagina inteira) e pulada - devolve 0.
    completo=True faz a conta sempre (para comparar os numeros com o estudo)."""
    total = max(int(np.count_nonzero(base_tinta)), 1)
    apag = base_tinta & ~linhas & ~imagem & ~tinta_do_resultado
    if not apag.any():
        return 0.0, 0.0, apag, apag
    alt, larg = apag.shape
    m = max(2, int(round(0.01 * min(alt, larg))))
    n, rot, st, _c = cv2.connectedComponentsWithStats(apag.view(np.uint8), connectivity=8)
    if n > 1:
        borda = np.zeros_like(apag)
        borda[:m, :] = borda[-m:, :] = True
        borda[:, :m] = borda[:, -m:] = True
        tira = np.zeros(n, bool)
        tira[np.unique(rot[apag & borda])] = True
        # ...mas so a peca que fica toda na faixa de fora: a pauta vermelha que
        # vai da beirada ate o meio (Antiphonal 46) conta
        x, y = st[:, cv2.CC_STAT_LEFT], st[:, cv2.CC_STAT_TOP]
        x1, y1 = x + st[:, cv2.CC_STAT_WIDTH], y + st[:, cv2.CC_STAT_HEIGHT]
        fx, fy = 0.06 * larg, 0.06 * alt
        so_na_faixa = (y1 <= fy) | (y >= alt - fy) | (x1 <= fx) | (x >= larg - fx)
        tira &= so_na_faixa
        tira[0] = False
        if tira.any():
            apag = apag & ~tira[rot]
    apagado_a = float(np.count_nonzero(apag)) / total
    if apagado_a < LIMITE_JUNTO and not completo:
        return apagado_a, 0.0, apag, np.zeros_like(apag)
    k = max(3, int(round(2 * h)))
    dens = cv2.boxFilter(apag.astype(np.float32), -1, (k, k), normalize=True)
    junto = apag & (dens > LIMITE_JUNTO_DENS)
    return apagado_a, float(np.count_nonzero(junto)) / total, apag, junto


def _maior_pedaco(apag: np.ndarray, h: float, linhas: np.ndarray, completo: bool = False):
    """(tinta do maior pedaco apagado em alturas de linha ao quadrado, mascara
    dos pedacos grandes): pontos apagados a menos de h/4 um do outro contam
    como um pedaco; so pedaco CHEIO (tinta >= 15% da caixa dele: a letra T da
    0,20; a mancha pontilhada do canto do Cursus 3, 0,06) e que encosta (a
    menos de uma altura de linha) numa linha de texto - a letra grande fica
    sempre colada no texto (sinais4.maior_pedaco).

    Dois atalhos (so mudam o tempo, nunca a decisao): se TODA a tinta apagada
    nao chega ao tamanho de um pedaco grande, nenhum pedaco chega (devolve 0
    sem alargar nada); e a conta e feita so no retangulo que contem a tinta
    apagada (mais o raio), nao na pagina inteira - alargar com o elemento
    redondo custa mais quanto maior a altura da linha (segundos na pagina de
    musica de linha alta). completo=True desliga o primeiro atalho (para
    comparar os numeros com o estudo)."""
    vazio = np.zeros_like(apag)
    quanto = int(np.count_nonzero(apag))
    if quanto == 0 or (quanto < PEDACO_GRANDE * h * h and not completo):
        return 0.0, vazio
    rad = max(1, int(round(h / 4)))
    # o retangulo da tinta apagada, com folga do raio (fora dele nada muda)
    ys, xs = np.flatnonzero(apag.any(axis=1)), np.flatnonzero(apag.any(axis=0))
    alt, larg = apag.shape
    y0, y1 = max(0, int(ys[0]) - rad - 1), min(alt, int(ys[-1]) + rad + 2)
    x0, x1 = max(0, int(xs[0]) - rad - 1), min(larg, int(xs[-1]) + rad + 2)
    pedaco = np.ascontiguousarray(apag[y0:y1, x0:x1])
    junto = cv2.dilate(pedaco.view(np.uint8),
                       cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rad + 1, 2 * rad + 1)))
    n, rot, st, _c = cv2.connectedComponentsWithStats(junto, connectivity=8)
    if n <= 1:
        return 0.0, vazio
    tinta = np.bincount(rot[pedaco], minlength=n)
    tinta[0] = 0
    caixa = np.maximum(st[:, cv2.CC_STAT_WIDTH] * st[:, cv2.CC_STAT_HEIGHT], 1)
    tinta[tinta < 0.15 * caixa] = 0
    if linhas is not None and linhas.any():
        r = max(1, int(round(h)))
        # as linhas alargadas uma altura de linha, vistas so dentro do retangulo
        # (com a folga para o alargamento alcancar as linhas de fora dele)
        ya, yb = max(0, y0 - r), min(alt, y1 + r)
        xa, xb = max(0, x0 - r), min(larg, x1 + r)
        perto = cv2.dilate(np.ascontiguousarray(linhas[ya:yb, xa:xb]).view(np.uint8),
                           np.ones((2 * r + 1, 2 * r + 1), np.uint8))
        perto = perto[y0 - ya:y0 - ya + (y1 - y0), x0 - xa:x0 - xa + (x1 - x0)] > 0
        encosta = np.zeros(n, bool)
        encosta[np.unique(rot[perto & (junto > 0)])] = True
        tinta[~encosta] = 0
    maior = float(tinta.max()) / (h * h)
    grandes = tinta >= PEDACO_GRANDE * h * h
    grandes[0] = False
    if not grandes.any():
        return maior, vazio
    marca = vazio
    marca[y0:y1, x0:x1] = pedaco & grandes[rot]
    return maior, marca


def _vazou_da_gravura(base_tinta: np.ndarray, imagem: np.ndarray, h: float) -> float:
    """Tinta de pedacos grandes (1,5 altura de linha ou mais) encostados por
    fora na gravura achada / toda a tinta (medir.sinais, "vazou_da_gravura")."""
    if not imagem.any():
        return 0.0
    total = max(int(np.count_nonzero(base_tinta)), 1)
    inteiro = base_tinta & ~imagem
    n, rot, st, _c = cv2.connectedComponentsWithStats(inteiro.view(np.uint8), connectivity=8)
    if n <= 1:
        return 0.0
    borda = cv2.dilate(imagem.view(np.uint8), np.ones((5, 5), np.uint8)) > 0
    toca = np.zeros(n, bool)
    toca[np.unique(rot[inteiro & borda])] = True
    tamanho = np.maximum(st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT])
    toca &= tamanho >= 1.5 * h
    toca[0] = False
    return float(st[toca, cv2.CC_STAT_AREA].sum()) / total


def _beirada_escura(tinta: np.ndarray) -> float:
    """Fracao da pagina coberta por mancha CHEIA de tinta (sobra de uma
    abertura com um quadrado de 1,5% do lado menor: letra, fio e moldura
    somem; tarja e faixa ficam) encostada na beirada (ate 1% dela). Trabalha
    na pagina reduzida a 1000 pontos (sinais.beirada_escura)."""
    alt, larg = tinta.shape
    f = 1000 / max(alt, larg)
    peq = cv2.resize(tinta.astype(np.uint8) * 255, (max(1, round(larg * f)), max(1, round(alt * f))),
                     interpolation=cv2.INTER_AREA) > 127
    a, l = peq.shape
    lado = max(3, int(round(0.015 * min(a, l))))
    cheia = cv2.morphologyEx(peq.astype(np.uint8), cv2.MORPH_OPEN,
                             np.ones((lado, lado), np.uint8)) > 0
    n, rot, _st, _c = cv2.connectedComponentsWithStats(cheia.astype(np.uint8), connectivity=8)
    m = max(1, int(round(0.01 * min(a, l))))
    borda = np.zeros_like(cheia)
    borda[:m, :] = borda[-m:, :] = True
    borda[:, :m] = borda[:, -m:] = True
    ids = np.unique(rot[cheia & borda])
    ids = ids[ids > 0]
    if not len(ids):
        return 0.0
    return float(np.count_nonzero(np.isin(rot, ids))) / (a * l)


def _caixa_da_linha(poligono, larg: int, alt: int):
    pts = np.asarray(poligono)
    x0, y0 = max(0, int(pts[:, 0].min())), max(0, int(pts[:, 1].min()))
    x1, y1 = min(larg, int(pts[:, 0].max()) + 1), min(alt, int(pts[:, 1].max()) + 1)
    return x0, y0, x1, y1


def _letra_falhada(cinza: np.ndarray, poligonos, tinta_pb: np.ndarray):
    """(quantas falhadas, quantas contadas, as caixas das falhadas): texto que
    o preto e branco deixa PELA METADE (sinais4.letra_falhada). So linhas
    compridas (15% da largura ou mais) e longe do alto e do pe (6%): carimbo,
    numero de estante e tarja ficam de fora. Em cada uma: papel = percentil 90
    do cinza da linha, tinta = percentil 2; "tinta da letra" = pontos mais
    escuros que papel - 30% do contraste. guarda = quanto dessa tinta o preto e
    branco guarda. Linha de contraste baixo (papel - tinta < 25) nao conta: e a
    mancha do verso que o leitor leu."""
    alt, larg = cinza.shape
    contadas, falhadas = 0, []
    for p in poligonos:
        x0, y0, x1, y1 = _caixa_da_linha(p, larg, alt)
        if (x1 - x0) < 0.15 * larg or y0 < 0.06 * alt or y1 > 0.94 * alt:
            continue
        g = cinza[y0:y1, x0:x1]
        if g.size == 0:
            continue
        papel, tinta = _percentil(g, 90), _percentil(g, 2)
        if papel - tinta < 25:
            continue
        m = g < papel - 0.3 * (papel - tinta)
        guarda = float(np.count_nonzero(tinta_pb[y0:y1, x0:x1] & m)) / max(1, int(np.count_nonzero(m)))
        contadas += 1
        if GUARDA_MINIMA <= guarda < LIMITE_GUARDA:
            falhadas.append((x0 / larg, y0 / alt, x1 / larg, y1 / alt))
    return len(falhadas), contadas, falhadas


def _linhas_por_contraste(cinza: np.ndarray, poligonos) -> tuple[int, int]:
    """(linhas fortes, linhas fracas): contraste da linha contra o papel da
    pagina (percentil 60 do miolo); forte = a tinta (percentil 2) 50% mais
    escura que o papel. A mancha do verso que o leitor le como texto e fraca
    (sinais4.linhas_por_contraste)."""
    alt, larg = cinza.shape
    papel = _percentil(cinza[int(.1 * alt):int(.9 * alt), int(.1 * larg):int(.9 * larg)], 60)
    fortes = fracas = 0
    for p in poligonos:
        x0, y0, x1, y1 = _caixa_da_linha(p, larg, alt)
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        c = (papel - _percentil(cinza[y0:y1, x0:x1], 2)) / max(papel, 1.0)
        if c >= 0.5:
            fortes += 1
        else:
            fracas += 1
    return fortes, fracas


def _sem_conteudo(cinza: np.ndarray) -> float:
    """Fracao do miolo (8% de margem de cada lado) com tinta forte: pontos com
    o cinza abaixo de 55% do papel (percentil 60 do miolo). Pagina em branco ou
    so com a mancha do verso da quase zero (sinais4.sem_conteudo)."""
    alt, larg = cinza.shape
    my, mx = int(0.08 * alt), int(0.08 * larg)
    g = cinza[my:alt - my, mx:larg - mx]
    if g.size == 0:
        return 1.0
    papel = _percentil(g, 60)
    return float(np.count_nonzero(g < 0.55 * papel)) / g.size


def caixas_de(mascara: np.ndarray, h: float, maximo: int = MAXIMO_DE_CAIXAS) -> list[Caixa]:
    """As caixas (x0, y0, x1, y1 em fracao da pagina) em volta dos amontoados
    de `mascara` (booleana), as de mais tinta primeiro. Pontos a menos de uma
    altura de linha um do outro ficam na mesma caixa; cada caixa ganha meia
    altura de linha de folga. Trabalha na pagina reduzida a 1000 pontos. So
    serve para o desenho da marca do aviso: seguro mudar."""
    if mascara is None or not mascara.any():
        return []
    alt, larg = mascara.shape
    f = min(1.0, 1000 / max(alt, larg))
    peq = cv2.resize(mascara.astype(np.uint8) * 255,
                     (max(1, round(larg * f)), max(1, round(alt * f))),
                     interpolation=cv2.INTER_AREA) > 0
    a, l = peq.shape
    raio = max(1, int(round(h * f)))
    junto = cv2.dilate(peq.astype(np.uint8), np.ones((2 * raio + 1, 2 * raio + 1), np.uint8))
    n, rot, st, _c = cv2.connectedComponentsWithStats(junto, connectivity=8)
    if n <= 1:
        return []
    tinta = np.bincount(rot[peq], minlength=n)
    tinta[0] = 0
    folga = raio // 2
    caixas: list[Caixa] = []
    for i in np.argsort(-tinta)[:maximo]:
        if tinta[i] <= 0:
            break
        # a caixa da tinta de verdade (a do amontoado alargado menos o raio)
        x0 = st[i, cv2.CC_STAT_LEFT] + raio - folga
        y0 = st[i, cv2.CC_STAT_TOP] + raio - folga
        x1 = st[i, cv2.CC_STAT_LEFT] + st[i, cv2.CC_STAT_WIDTH] - raio + folga
        y1 = st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] - raio + folga
        caixas.append((float(max(0.0, x0 / l)), float(max(0.0, y0 / a)),
                       float(min(1.0, x1 / l)), float(min(1.0, y1 / a))))
    return caixas


def medir(cinza: np.ndarray, base_tinta: np.ndarray, linhas: np.ndarray, imagem: np.ndarray,
          tinta_do_resultado: np.ndarray, poligonos, altura_linha: float,
          tinta_pb: np.ndarray | None = None, tinta_forte_apagada: np.ndarray | None = None,
          com_o_desenho_apagado: bool = True, completo: bool = False) -> Sinais:
    """Os sinais do "Para revisar" de uma pagina (ver o topo).

    cinza: o cinza usado para binarizar (core.filtros._cinza_para_binarizar).
    base_tinta: a tinta do Preto e branco de base da pagina, ANTES de o "Só as
        letras" apagar o que esta fora das linhas (booleano).
    linhas: a mascara das linhas de texto (core.misto.mascara_das_linhas).
    imagem: onde a pagina fica como imagem (gravura achada ou marcada).
    tinta_do_resultado: a tinta da pagina como saiu (cinza < 128).
    poligonos: as linhas do leitor, ja no tamanho da pagina (listas de pontos).
    altura_linha: a altura mediana das linhas, em pontos da pagina.
    tinta_pb: a tinta do Preto e branco de sempre (sem "Só as letras"); None =
        usa base_tinta (so diferem dentro das gravuras e no papel marcado).
    tinta_forte_apagada: no "Guardar só o texto", a tinta forte que ele apagou
        (para marcar onde sumiu); None = nao marca.
    com_o_desenho_apagado: False pula a conta do desenho apagado (no "Guardar
        só o texto" ela nao vale; ver motivos).
    completo: True desliga os atalhos de tempo de _apagado e _maior_pedaco,
        para os NUMEROS sairem iguais aos do estudo mesmo abaixo dos limites
        (so o script conferir_89.py usa). As decisoes sao as mesmas dos dois
        jeitos.

    Todas as mascaras tem o tamanho da pagina. Nao muda nenhuma delas.
    """
    h = max(float(altura_linha), 1.0)
    s = Sinais()
    if com_o_desenho_apagado:
        s.apagado_a, s.apagado_junto, apag, junto = _apagado(
            base_tinta, linhas, imagem, tinta_do_resultado, h, completo)
        s.maior_pedaco, grandes = _maior_pedaco(apag, h, linhas, completo)
        if s.desenho_apagado:
            marca = junto | grandes
            s.onde_sumiu = caixas_de(marca if marca.any() else apag, h)
    elif tinta_forte_apagada is not None:
        s.onde_sumiu_a_tinta_forte = caixas_de(tinta_forte_apagada, h)
    s.vazou_da_gravura = _vazou_da_gravura(base_tinta, imagem, h)
    s.beirada_a = _beirada_escura(tinta_do_resultado & ~imagem)
    s.falhadas, s.linhas_contadas, s.linhas_falhadas = _letra_falhada(
        cinza, poligonos, base_tinta if tinta_pb is None else tinta_pb)
    s.sem_conteudo = _sem_conteudo(cinza)
    s.linhas_fortes, s.linhas_fracas = _linhas_por_contraste(cinza, poligonos)
    return s


def poligonos_das_linhas(resultados, forma: tuple[int, int]) -> list[list[list[int]]]:
    """As linhas dos leitores de texto (core.ocr_comum.ResultadoOCR) como
    listas de pontos inteiros no tamanho `forma` (altura, largura) da pagina -
    a mesma conta de core.misto.mascara_das_linhas, sem alargar."""
    altura, largura = forma[:2]
    poligonos = []
    for r in resultados or []:
        if r is None or not r.disponivel:
            continue
        fx = largura / r.largura if r.largura else 1.0
        fy = altura / r.altura if r.altura else 1.0
        for linha in r.linhas:
            pts = np.asarray(linha.poligono, np.float64) * (fx, fy)
            if len(pts) >= 3 and np.isfinite(pts).all():
                poligonos.append(np.round(pts).astype(int).tolist())
    return poligonos
