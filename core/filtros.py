"""Os tres filtros de limpeza + o Original.

Esta e a parte mais importante do programa. As versoes anteriores falharam aqui
por tentar inventar formula propria. Aqui usamos o que já e consagrado:

- Preto e branco: binarizacao local de Sauvola (via DoxaPy, licenca CC0).
  Na gravura marcada (moldura, iluminura, titulo colorido, gravura de traco),
  o desenho em preto e branco de _preto_e_branco_com_gravura (regra do
  Samuel de 30/09/2026: no Preto e branco tudo sai em preto e branco).
  E o mesmo caminho do ScanTailor. Resolve amarelado E bleed-through (o texto
  do verso transparecendo) de uma vez só, porque o limiar e calculado numa
  janela ao redor de cada pixel: o texto do verso e sempre mais claro que o
  texto da frente na vizinhanca dele, entao cai para o branco.

- Melhorar: divisão pelo fundo estimado. Limpa a iluminacao sem tocar na cor.

- Mágico pro: Melhorar + CLAHE + saturacao + nitidez, no espirito do
  "magic color" do CamScanner.

- Tirar o fundo (item 1.1, 29/09/2026): NAO e calculado aqui. So existe em
  PDF com camadas (Internet Archive: fundo embaixo, texto recortado por cima)
  e quem faz e core/camadas.py, chamado por core/pipeline.py na folha inteira,
  antes de dividir (ver pipeline.usa_tirar_fundo). Aqui ele e so um nome na
  lista, e as funcoes deste arquivo o tratam como o Original (devolvem a
  imagem como veio): e assim que sai a pagina que core/camadas.py deixa
  intacta, ou um projeto com o filtro salvo num PDF sem camadas.
"""

from __future__ import annotations

import cv2
import numpy as np

# --- nomes dos filtros (usados em ConfigPagina.filtro) -----------------------
ORIGINAL = "original"
PRETO_E_BRANCO = "preto_e_branco"
MELHORAR = "melhorar"
MAGICO_PRO = "magico_pro"

# Item 1.1 do Plano Definitivo. Decisao do Samuel (29/09/2026): "Em PDF com
# camadas, 'Tirar o fundo' vira mais uma opcao na lista de filtros (ao lado de
# Original, Preto e branco, Melhorar e Magico pro), com botao para aplicar no
# livro inteiro." E "eu quero poder escolher tirar o fundo sem colocar nenhum
# filtro": nenhum outro filtro vai por cima dele. Quem desenha a pagina e
# core/camadas.py (via core/pipeline.py); ver o topo deste arquivo.
# Arriscado mudar o valor: e o que fica gravado em ConfigPagina.filtro nos
# projetos salvos.
TIRAR_FUNDO = "tirar_fundo"

# Os quatro filtros de sempre, que valem em qualquer livro.
FILTROS_COMUNS = (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO)

# Todos os nomes que ConfigPagina.filtro aceita. O "Tirar o fundo" so aparece
# na tela em livro com camadas: ver filtros_do_livro.
FILTROS = FILTROS_COMUNS + (TIRAR_FUNDO,)

NOMES_AMIGAVEIS = {
    ORIGINAL: "Original",
    PRETO_E_BRANCO: "Preto e branco",
    MELHORAR: "Melhorar",
    MAGICO_PRO: "Mágico pro",
    TIRAR_FUNDO: "Tirar o fundo",
}


def filtros_do_livro(projeto) -> tuple[str, ...]:
    """Os filtros que a tela oferece para este livro, na ordem da tela.

    "Tirar o fundo" so entra quando o PDF tem camadas (projeto.tem_camadas,
    detectado ao abrir). Tambem entra, para a pessoa poder sair dele, quando o
    livro ja tem esse filtro escolhido (salvo antes) mesmo sem camadas - ai a
    pagina sai como veio, sem erro (ver core/pipeline.py). `projeto` e um
    modelos.Projeto; lido so por atributo, para este arquivo nao importar
    modelos (que importa este).
    """
    mostrar = bool(getattr(projeto, "tem_camadas", False)) or (
        getattr(projeto, "filtro_padrao", None) == TIRAR_FUNDO
        or any(getattr(p, "filtro", None) == TIRAR_FUNDO
               for p in getattr(projeto, "paginas", ())))
    return FILTROS if mostrar else FILTROS_COMUNS

# --- parametros de ajuste (mexer aqui para calibrar) -------------------------

# Janela do Sauvola, em fracao da altura da pagina. Era 1/20 - algumas linhas de
# texto de cada vez -, e isso e grande demais para separar a mancha do verso.
#
# O Sauvola compara cada pixel com a vizinhanca dele. Numa janela larga, a
# vizinhanca de uma marca do verso inclui o texto da frente, que e bem mais
# escuro; a media desce, o limiar desce junto, e a marca do verso passa por
# tinta. Numa janela do tamanho de UMA linha, a marca do verso e comparada com
# o papel ao redor dela, e cai para o branco - que e para isto que o Sauvola
# serve.
#
# Medido na pagina 33 do Boecio, quanto da mancha do verso sobrevive:
#
#   janela 139 (1/20)   64%      <- saia legivel, da para ler espelhado
#   janela  56 (1/50)   30%
#   janela  46 (1/60)   24%
#
# A tinta de verdade fica em 100% em todas elas - nao ha texto a perder aqui.
JANELA_FRACAO_ALTURA = 1 / 50
JANELA_MIN = 15
JANELA_MAX = 151

# Todos os ajustes de filtro sao um numero de 0 a 100, com 50 no meio. E o que
# o medidor deslizante da interface mostra: o usuario nunca ve k, clipLimit
# nem saturacao.
AJUSTE_MIN, AJUSTE_PADRAO, AJUSTE_MAX = 0, 50, 100

# k do Sauvola. Quanto MAIOR o k, MAIS ALTO fica o limiar de branco, ou seja,
# menos pixels viram preto. Por isso "mais fraco" tem k maior.
# 0 -> 0,40 (bem fraco)   50 -> 0,30 (normal)   100 -> 0,06 (bem escuro)
#
# O normal era 0,20, e 0,20 engordava a letra: ampliada, ela saia mais grossa
# que no original, e o vao entre as linhas ficava salpicado da mancha do verso.
# Em 0,30 a letra volta ao peso do original e o fundo limpa.
K_FRACO, K_NORMAL, K_ESCURO = 0.40, 0.30, 0.06

# Palavras que aparecem ao lado do medidor. O usuario le isto, nao o numero.
PALAVRAS_DA_FORCA = (
    (20, "bem fraco"),
    (40, "leve"),
    (60, "normal"),
    (80, "forte"),
    (101, "bem forte"),
)

# Ruido: componentes conectados menores que isso (em px, medido a 300 DPI)
# viram branco. Tira a poeira do scanner sem comer pingo de "i" nem acento.
AREA_MINIMA_RUIDO_300DPI = 8

# Fundo: sigma do desfoque que estima a iluminacao, em fracao da altura.
# Precisa ser bem maior que uma letra e bem menor que a pagina.
SIGMA_FUNDO_FRACAO = 1 / 20

# O fundo e uma variacao lenta, entao pode ser estimado numa imagem pequena e
# esticado de volta. Da o mesmo resultado ~60x mais rapido que desfocar a
# pagina inteira a 300 DPI.
LARGURA_ESTIMATIVA_FUNDO = 400

# Quanto a correcao de iluminacao pode clarear ou escurecer um ponto.
# Limitar evita que uma area escura grande (uma foto, uma capa colorida) seja
# tratada como sombra e lavada ate o branco.
GANHO_MIN, GANHO_MAX = 0.6, 2.2

# Faixa em que a correcao de iluminacao vai perdendo forca, medida como
# fundo_local / nivel_do_papel. Acima de MAX e papel (corrige tudo); abaixo de
# MIN e conteudo escuro de verdade (nao corrige nada).
PESO_RAZAO_MIN, PESO_RAZAO_MAX = 0.62, 0.85

# Ponto de branco: so pixels claros e pouco coloridos contam como "papel".
BRANCO_PERCENTIL = 85
BRANCO_SATURACAO_MAX = 60
BRANCO_FRACAO_MINIMA = 0.02  # abaixo disso a pagina nao tem papel branco visivel
BRANCO_ESCALA_MAX = 2.5
# Onde comeca o "ombro" da curva de branco, em fracao do nivel do papel.
# Tudo mais escuro que isso fica exatamente como estava.
OMBRO_INICIO = 0.75

# Melhorar: a "clareza do fundo" mexe em onde comeca o ombro. Quanto mais cedo
# comeca, mais tons sobem para o branco - o fundo fica mais limpo, com o risco
# de achatar o que era quase branco.
OMBRO_SUAVE, OMBRO_FORTE = 0.88, 0.55

# Magico pro: a "intensidade" move os tres de uma vez.
CLAHE_GRADE = (8, 8)
CLAHE_CLIP_MIN, CLAHE_CLIP_MAX = 1.0, 3.5

# Onde comeca a valer o realce de contraste local, em fracao do nivel do papel,
# e em quantos tons ele chega a valer inteiro. Ancorar o inicio ABAIXO do nivel
# do papel e o que fecha o vazamento: o nivel do papel e o percentil 85, entao
# a metade mais escura do proprio papel ainda receberia realce se a rampa
# comecasse nele. Medido no acervo, descer o inicio de 1,00 para 0,80 leva o
# ruido de 7,2 para 5,1; abaixo de 0,80 nao ha mais ganho, so perda de
# contraste nas gravuras.
CLAHE_INICIO_CONTEUDO = 0.80
CLAHE_FAIXA_CONTEUDO = 0.35
SATURACAO_MIN, SATURACAO_MAX = 1.0, 2.2
NITIDEZ_MIN, NITIDEZ_MAX = 0.15, 1.10

CLAHE_CLIP = 2.0
SATURACAO_GANHO = 1.35

# Onde o realce de cor NAO deve pegar: claro como papel e sem cor de verdade.
# Medido no acervo, o grao do papel ja limpo fica entre 13 e 16 de saturacao; a
# rubricacao comeca em 60 (SATURACAO_DE_RUBRICA).
CLARO_COMO_PAPEL = 0.80
SATURACAO_DE_GRAO = 25
NITIDEZ_PESO = 0.6
BRANCO_LIMIAR = 235

# Largura da orla que o empurrao para o branco NAO toca, como fracao do menor
# lado da pagina. Da uns dois pixels a 300 DPI - a espessura da rampa de
# antisserrilhamento de uma letra impressa.
ORLA_DA_LETRA = 400

# Abaixo desta fracao do nivel do papel o pixel conta como tinta, so para saber
# onde fica a orla a preservar. Nao e limiar de binarizacao.
TINTA_PARA_ORLA = 0.60

# Orla em volta da tinta onde o branco do papel marcado nao entra, em fracao do
# menor lado da pagina. Ver _peso_do_papel_sem_tocar_a_tinta.
ORLA_DA_TINTA_NO_PAPEL = 1 / 250

# Abaixo desta fracao de tinta a folha esta em branco: nao ha preto a aprofundar
# nem contraste a realcar, so grao de scanner a nao amplificar.
TINTA_DE_FOLHA_ESCRITA = 0.01

# A partir desta fracao da folha marcada como papel, entende-se que a pessoa
# quer a FOLHA EM BRANCO, e nao "aqui e fundo". Ver aplicar_filtro_com_selecao.
FOLHA_INTEIRA_EM_BRANCO = 0.95

# Acima desta fracao de tinta, o Sauvola nao esta vendo LETRA e sim hachura de
# gravura ou pergaminho escuro inteiro. Ali o branco a limpo nao entra: apagar
# "o que nao e tinta" numa gravura arranca o meio-tom. Medido no acervo: pagina
# de texto fica entre 3% e 12%; as pranchas do Siebmacher passam de 25%.
TINTA_DEMAIS_PARA_LIMPAR = 0.22

# Tamanho minimo de uma peca de tinta para valer como letra, em fracao da area
# da pagina. Medido na pagina 33 do Boecio, a mais manchada do acervo: as pecas
# do texto tem area mediana de 66 pixels e as da mancha do verso, 4. O corte em
# 30 pixels - 2,5 centesimos de milesimo da folha - separa os dois lados sem
# depender do DPI. As pecas menores nao se perdem: sobrevivem se encostarem numa
# peca grande, que e o caso de acento, pingo e serifa solta.
PECA_DE_LETRA_MINIMA = 0.000025

# Abaixo desta fracao do nivel do papel o pixel e escuro demais para ser mancha,
# e fica como esta mesmo longe de qualquer letra. Rede de seguranca: e melhor
# deixar uma sujeira escura do que apagar tinta fraca que o Sauvola nao viu.
ESCURO_DEMAIS_PARA_SER_MANCHA = 0.45

# Quantas pecas de letra a pagina precisa ter para valer como pagina de TEXTO.
# A limpeza do papel so faz sentido entre letras; numa estampa ou numa prancha o
# que esta entre os tracos e a obra, e branquear aquilo a arruina - a estampa do
# Catecismo perdia o ceu azul. Contado no acervo: pagina de texto vai de 264
# (Graduale) a 2405 (Rhetorica) pecas; estampa e prancha ficam entre 6 e 83.
# Entre os dois grupos ha um vao de tres vezes, e o corte cai no meio dele.
PECAS_DE_TEXTO_MINIMAS = 200

# Raio do borrao da nitidez, em fracao da altura. Era 1/1000, tres pixels numa
# pagina de 300 DPI: largo demais para letra, e o que sobrava era um halo claro
# em volta de cada traco em vez de nitidez. Ver _nitidez.
RAIO_DA_NITIDEZ = 2500


class ErroFiltro(Exception):
    """Falha ao aplicar um filtro, já com mensagem para o usuario."""


# --- binarizacao: DoxaPy com queda automatica para scikit-image --------------

def _sauvola_doxapy(cinza: np.ndarray, janela: int, k: float) -> np.ndarray | None:
    """Sauvola pelo DoxaPy. Devolve None se a biblioteca não estiver disponível."""
    try:
        import doxapy
    except Exception:  # noqa: BLE001 - biblioteca nativa pode faltar no Windows
        return None

    try:
        entrada = np.ascontiguousarray(cinza, dtype=np.uint8)
        saida = np.empty_like(entrada)
        bin_ = doxapy.Binarization(doxapy.Binarization.Algorithms.SAUVOLA)
        bin_.initialize(entrada)
        bin_.to_binary(saida, {"window": int(janela), "k": float(k)})
        return saida
    except Exception:  # noqa: BLE001 - se o nativo falhar, usamos o plano B
        return None


def _sauvola_skimage(cinza: np.ndarray, janela: int, k: float) -> np.ndarray:
    """Plano B: Sauvola do scikit-image (BSD). Mais lento, mesmo resultado."""
    from skimage.filters import threshold_sauvola

    limiar = threshold_sauvola(cinza, window_size=int(janela), k=float(k))
    return np.where(cinza > limiar, 255, 0).astype(np.uint8)


def _wolf_doxapy(cinza: np.ndarray, janela: int, k: float) -> np.ndarray | None:
    """Wolf pelo DoxaPy - mesma biblioteca do Sauvola, só troca o algoritmo.

    Achado em `relatorios/melhorias.md`: a literatura indica Wolf melhor que
    Sauvola em scan de baixo contraste. Devolve None se a biblioteca não
    estiver disponível (mesma regra do `_sauvola_doxapy`) - quem chama cai
    para Sauvola em vez de travar.
    """
    try:
        import doxapy
    except Exception:  # noqa: BLE001 - biblioteca nativa pode faltar no Windows
        return None

    try:
        entrada = np.ascontiguousarray(cinza, dtype=np.uint8)
        saida = np.empty_like(entrada)
        bin_ = doxapy.Binarization(doxapy.Binarization.Algorithms.WOLF)
        bin_.initialize(entrada)
        bin_.to_binary(saida, {"window": int(janela), "k": float(k)})
        return saida
    except Exception:  # noqa: BLE001 - se o nativo falhar, usamos o plano B
        return None


def _otsu_binario(cinza: np.ndarray) -> np.ndarray:
    """Otsu (cv2) - um limiar só para a página inteira, sem janela nem k.

    Achado em `relatorios/melhorias.md` (30/07/2026): sai sólido em letra
    gótica pesada (Palatino), onde o Sauvola quebra o traço - mas guarda o
    dobro de "tinta" que o Sauvola, risco de manter mancha do verso como se
    fosse letra. Por isso não é o padrão, só uma opção.
    """
    _limiar, saida = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return saida


ALGORITMO_SAUVOLA = "sauvola"
ALGORITMO_OTSU = "otsu"
ALGORITMO_WOLF = "wolf"
ALGORITMOS_PB = (ALGORITMO_SAUVOLA, ALGORITMO_OTSU, ALGORITMO_WOLF)
NOMES_DOS_ALGORITMOS_PB = {
    ALGORITMO_SAUVOLA: "Sauvola (padrão)",
    ALGORITMO_OTSU: "Otsu (letra grossa/gótica)",
    ALGORITMO_WOLF: "Wolf (scan de baixo contraste)",
}


# --- esqueleto do traco, em partes (regra 6, 30/09/2026) ---------------------
#
# O skeletonize (Zhang-Suen, scikit-image) e a conta mais cara do Preto e
# branco: ~0,6 s na pagina a 300 DPI (escolher_algoritmo_automatico) e ~0,15 s
# em cada medida do k (k_para_a_letra), so numa linha da maquina. Ele decide
# cada ponto olhando so os 8 vizinhos, e repete ate nada mudar; duas pecas de
# tinta que nao se encostam (nem na diagonal) nunca se influenciam. Entao a
# pagina e dividida em grupos de pecas inteiras, cada grupo e esqueletizado
# sozinho (no recorte dele, com as pecas dos outros grupos apagadas) e os
# pedacos voltam para o lugar: o MESMO esqueleto, ponto por ponto, feito em
# varias linhas ao mesmo tempo (o skeletonize solta o GIL). Pagina pequena, ou
# com uma peca so, vai inteira, como antes.
# Seguro mudar: PARTES_DO_ESQUELETO e o tamanho minimo. Arriscado: cortar uma
# peca entre dois grupos (o esqueleto dela mudaria) - por isso o grupo e feito
# de pecas inteiras (rotulos do connectedComponents com vizinhanca 8).
PARTES_DO_ESQUELETO = 4
PONTOS_PARA_DIVIDIR_O_ESQUELETO = 1_500_000


def _esqueleto(tinta: np.ndarray) -> np.ndarray:
    """skimage.morphology.skeletonize(tinta), identico, em partes paralelas."""
    from skimage.morphology import skeletonize

    tinta = np.asarray(tinta, dtype=bool)
    if tinta.ndim != 2 or tinta.size < PONTOS_PARA_DIVIDIR_O_ESQUELETO:
        return skeletonize(tinta)
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(
        tinta.view(np.uint8), connectivity=8)
    if quantas <= 2:
        return skeletonize(tinta)
    # Grupos de pecas inteiras. A peca alta ou larga (faixa da beirada, fio
    # de moldura) fica num grupo so dela, no recorte justo dela: junto das
    # outras, o recorte do grupo viraria a pagina inteira. As demais vao em
    # faixas de cima para baixo, com area parecida.
    pecas = np.arange(1, quantas)
    altura, largura = tinta.shape
    grande = ((medidas[1:, cv2.CC_STAT_HEIGHT] > altura // 4)
              | (medidas[1:, cv2.CC_STAT_WIDTH] > largura // 2))
    grupo = np.zeros(quantas, np.int64)
    comuns = pecas[~grande]
    if comuns.size:
        ordem = comuns[np.argsort(medidas[comuns, cv2.CC_STAT_TOP], kind="stable")]
        acumulada = np.cumsum(medidas[ordem, cv2.CC_STAT_AREA])
        total = float(acumulada[-1])
        grupo[ordem] = np.minimum((acumulada - 1) * PARTES_DO_ESQUELETO // max(1.0, total),
                                  PARTES_DO_ESQUELETO - 1).astype(np.int64)
    grupo[pecas[grande]] = PARTES_DO_ESQUELETO + np.arange(int(grande.sum()))
    tarefas = []
    for g in range(PARTES_DO_ESQUELETO + int(grande.sum())):
        membros = pecas[grupo[1:] == g]
        if membros.size == 0:
            continue
        x0 = int(medidas[membros, cv2.CC_STAT_LEFT].min())
        y0 = int(medidas[membros, cv2.CC_STAT_TOP].min())
        x1 = int((medidas[membros, cv2.CC_STAT_LEFT] + medidas[membros, cv2.CC_STAT_WIDTH]).max())
        y1 = int((medidas[membros, cv2.CC_STAT_TOP] + medidas[membros, cv2.CC_STAT_HEIGHT]).max())
        do_grupo = np.zeros(quantas, bool)
        do_grupo[membros] = True
        tarefas.append((y0, y1, x0, x1, do_grupo))
    if len(tarefas) <= 1:
        return skeletonize(tinta)

    def esqueletizar(tarefa):
        y0, y1, x0, x1, do_grupo = tarefa
        return skeletonize(do_grupo[rotulos[y0:y1, x0:x1]])

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=min(len(tarefas), PARTES_DO_ESQUELETO)) as linhas:
        pedacos = list(linhas.map(esqueletizar, tarefas))
    saida = np.zeros(tinta.shape, bool)
    for (y0, y1, x0, x1, _g), pedaco in zip(tarefas, pedacos):
        saida[y0:y1, x0:x1] |= pedaco
    return saida


# Regra 6 (02/10/2026): a escolha automatica media a espessura na pagina
# INTEIRA (o esqueleto de 20 a 25 milhoes de pontos nas Horas e no Graduale a
# 300 DPI): medido, 6,2 s na Horas 47 e 9,5 s na Horas 11 (a moldura enche
# metade da folha), so para responder "passa de 10 pontos?". A medida reduzida
# (a do k, ALTURA_PARA_MEDIR_TRACO, ja paga e guardada) sai sempre um pouco
# MAIS grossa que a de tamanho cheio - medido nas 32 paginas do gabarito, de
# 1,00 a 1,56 vez (Opus 20: 31,3 contra 20,1). Quando ela passa de
# FOLGA_DA_MEDIDA_REDUZIDA vezes o limite, a resposta de tamanho cheio e Otsu
# com certeza, e a medida cheia nao e feita: as mesmas escolhas nas 32 paginas.
# Abaixo disso, a medida cheia continua decidindo (no Marial 7, 9,6 cheia e
# 10,4 reduzida: a reduzida trocaria a escolha). As paginas perto do limite
# medem de 1,00 a 1,25 vez (Marial 7 1,08; Horas 26 1,19; Horas 27 1,25); o
# 1,56 do Opus 20 e de uma pagina de traco 20, longe dele. Com 1,6 a Horas 13
# (16,9 reduzida) e o Graduale 222 (19,9) deixam de pagar a medida cheia
# (1,5 s e 0,6 s). Arriscado: baixar de 1,6 (uma pagina perto do limite
# poderia trocar de Sauvola para Otsu).
FOLGA_DA_MEDIDA_REDUZIDA = 1.6


def escolher_algoritmo_automatico(cinza: np.ndarray) -> str:
    """Tenta adivinhar qual dos 3 fica melhor nesta página, pela espessura
    do traço - a mesma medida que `k_para_a_letra` já faz.

    Critério único por enquanto: traço muito grosso (letra gótica pesada,
    tipo Graduale) tende a ir melhor com Otsu, que não quebra o traço como o
    Sauvola. Sem uma medida de contraste local barata o bastante para rodar
    em toda página, o Wolf fica de fora da escolha automática por ora -
    continua disponível como escolha manual ou "usar em todas".

    A medida reduzida (a do k, guardada) decide sozinha quando a pagina nao
    foi reduzida para medir, ou quando o traco e grosso com folga - ver
    FOLGA_DA_MEDIDA_REDUZIDA. Senao, a medida de tamanho cheio, como sempre.
    Quem escolhe Otsu aqui ganha a borda do Sauvola (ver
    _otsu_com_a_borda_do_sauvola, em filtro_preto_e_branco).
    """
    try:
        reduzida = _espessura_do_traco(cinza)
        if reduzida is not None:
            if cinza.shape[0] <= ALTURA_PARA_MEDIR_TRACO:
                # nao reduziu: e a propria medida de tamanho cheio
                return (ALGORITMO_OTSU if reduzida >= ESPESSURA_DE_LETRA_GROSSA
                        else ALGORITMO_SAUVOLA)
            if reduzida >= ESPESSURA_DE_LETRA_GROSSA * FOLGA_DA_MEDIDA_REDUZIDA:
                return ALGORITMO_OTSU
    except Exception:  # noqa: BLE001 - a medida cheia, abaixo, decide
        pass
    try:
        _lim, tinta = cv2.threshold(
            cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        tinta = (tinta > 0).astype(np.uint8)
        if not (0.002 <= tinta.mean() <= 0.6):
            return ALGORITMO_SAUVOLA
        distancia = cv2.distanceTransform(tinta, cv2.DIST_L2, 5)
        esqueleto = _esqueleto(tinta > 0)     # = skeletonize, em partes
        if not esqueleto.any():
            return ALGORITMO_SAUVOLA
        espessura = float(2.0 * distancia[esqueleto].mean())
    except Exception:  # noqa: BLE001 - medicao falhou, fica no padrao seguro
        return ALGORITMO_SAUVOLA

    if espessura >= ESPESSURA_DE_LETRA_GROSSA:
        return ALGORITMO_OTSU
    return ALGORITMO_SAUVOLA


def binarizar(
    cinza: np.ndarray, janela: int | None = None, k: float = 0.20,
    algoritmo: str = ALGORITMO_SAUVOLA,
) -> np.ndarray:
    """Binarizacao local. Devolve imagem 0/255 de um canal.

    `algoritmo` escolhe entre os 3 candidatos já medidos no acervo (ver
    ALGORITMOS_PB) - Otsu não usa janela/k (é um limiar só pra página
    inteira), os outros dois usam.
    """
    if janela is None:
        janela = janela_para_altura(cinza.shape[0])

    if algoritmo == ALGORITMO_OTSU:
        return _otsu_binario(cinza)

    if algoritmo == ALGORITMO_WOLF:
        resultado = _wolf_doxapy(cinza, janela, k)
        if resultado is not None:
            return resultado
        # Sem Wolf disponível (biblioteca faltando) cai para Sauvola em vez
        # de travar - mesma filosofia do _sauvola_doxapy/_sauvola_skimage.

    resultado = _sauvola_doxapy(cinza, janela, k)
    if resultado is None:
        resultado = _sauvola_skimage(cinza, janela, k)
    return resultado


def janela_para_altura(altura: int) -> int:
    """Tamanho da janela do Sauvola proporcional a página, sempre impar."""
    janela = int(altura * JANELA_FRACAO_ALTURA)
    janela = max(JANELA_MIN, min(JANELA_MAX, janela))
    if janela % 2 == 0:
        janela += 1
    return janela


# --- traducao do medidor (0 a 100) para os parametros de verdade ------------

def _entre(valor: int, minimo: float, maximo: float) -> float:
    """Interpola o valor do medidor dentro da faixa dada."""
    v = max(AJUSTE_MIN, min(AJUSTE_MAX, int(valor))) / 100.0
    return minimo + (maximo - minimo) * v


def k_do_sauvola(forca: int = AJUSTE_PADRAO,
                 k_do_meio: float | None = None) -> float:
    """Medidor de forca do preto -> k do Sauvola.

    Em duas retas para que a posicao do meio caia exatamente no k=0,20, que e
    o valor que funciona na maioria dos livros. Uma reta so entre 0,40 e 0,06
    deixaria o meio em 0,23 e o padrao ficaria diferente do recomendado.
    """
    forca = max(AJUSTE_MIN, min(AJUSTE_MAX, int(forca)))
    meio = K_NORMAL if k_do_meio is None else float(k_do_meio)
    if forca <= AJUSTE_PADRAO:
        return K_FRACO + (meio - K_FRACO) * (forca / AJUSTE_PADRAO)
    return meio + (K_ESCURO - meio) * ((forca - AJUSTE_PADRAO) / AJUSTE_PADRAO)


# O k que a LETRA daquela pagina pede, e nao um numero fixo para o acervo todo.
#
# Foi medido pagina a pagina, e a espessura do traco separa os casos sozinha:
#
#              espessura   k=0,20 (o antigo)        k=0,30
#   Boecio 33      4,3     mancha do verso 49%   mancha 31%, letra intacta
#   Rhetorica     5,4      mancha 61%            mancha 51%, letra intacta
#   Marial 454     8,6     vazios -20%           vazios -26%  REPROVA
#   Marial 756    10,3     vazios -26% ja no li- vazios -37%  REPROVA
#
# Letra fina aguenta k alto, e k alto e o que mata a mancha do verso. Letra
# grossa nao aguenta: o Sauvola come a barriga do traco e o "o" entope. O
# Marial 756 ja vivia na beirada com o valor antigo - traco afinando 34% contra
# o limite de 34% - e qualquer aperto o derrubava.
ESPESSURA_DE_LETRA_FINA, ESPESSURA_DE_LETRA_GROSSA = 5.0, 10.0
K_PARA_LETRA_FINA, K_PARA_LETRA_GROSSA = 0.30, 0.12


# Altura em que a espessura do traco e medida. A medicao usa esqueletizacao,
# que e a conta mais cara do programa: numa pagina de 300 DPI ela sozinha levava
# 1,9 s, contra 59 ms do proprio Sauvola. Medida num reduzido e reconvertida
# pela escala, cai para pouco mais de 100 ms sem mudar a resposta - a espessura
# e uma media sobre milhares de tracos, e reduzir nao a enviesa.
#
# A altura saiu de comparar com a medicao nativa nas 14 paginas do acervo:
#
#   altura   paginas com k fora de 0,01 do nativo   custo por pagina
#    1500                 4 de 14                       105 ms
#    2000                 2 de 14                       207 ms
#    2500                 1 de 14                       319 ms
#    3000                 1 de 14                       435 ms
#   nativo                  -                          1900 ms
#
# Em 2500 a resposta empata com a nativa em 13 das 14 e o custo cai seis vezes.
# Acima disso so se paga mais caro pela mesma resposta. A que sobra e a pagina
# 454 do Marial, que cai bem no meio da rampa entre traco fino e grosso, onde
# qualquer decimo de pixel move o k.
ALTURA_PARA_MEDIR_TRACO = 2500


# A mesma pagina pergunta o k tres vezes: o detector, ao marcar; o filtro, ao
# binarizar; e a limpeza do papel. Guardar as ultimas respostas corta duas
# medicoes de cada tres. A chave e o conteudo da imagem, e nao o objeto: o
# programa copia a pagina entre um passo e outro, e por objeto o cache nunca
# acertaria. Somar o hash custa uns 10 ms contra os 319 ms da medicao.
# Sao quatro entradas porque uma pagina passa por no maximo quatro versoes
# diferentes de si mesma dentro de um filtro.
# (02/10/2026) O que fica guardado e a ESPESSURA medida (ou None, quando a
# pagina nao tem traco que se meca), e nao mais o k: a escolha automatica do
# binarizador (escolher_algoritmo_automatico) usa a mesma medida, e assim a
# pagina e medida uma vez so para as duas perguntas. O k sai igual.
_KS_GUARDADOS: dict[tuple, float | None] = {}
_KS_GUARDADOS_MAX = 4


def _espessura_do_traco(cinza: np.ndarray) -> float | None:
    """A espessura do traco desta pagina, em pontos do tamanho de verdade,
    medida na copia reduzida (ALTURA_PARA_MEDIR_TRACO); None quando nao ha
    traco que se meca (tinta de menos ou de mais, esqueleto vazio). Guardada
    por conteudo (_KS_GUARDADOS). Ver k_para_a_letra."""
    from hashlib import blake2b

    chave = (cinza.shape, cinza.dtype.str,
             blake2b(np.ascontiguousarray(cinza), digest_size=16).digest())
    if chave in _KS_GUARDADOS:
        return _KS_GUARDADOS[chave]

    espessura = _medir_espessura_do_traco(cinza)
    if len(_KS_GUARDADOS) >= _KS_GUARDADOS_MAX:
        _KS_GUARDADOS.pop(next(iter(_KS_GUARDADOS)))
    _KS_GUARDADOS[chave] = espessura
    return espessura


def k_para_a_letra(cinza: np.ndarray) -> float:
    """O k que a letra desta pagina pede. Ver o comentario acima."""
    return _k_da_espessura(_espessura_do_traco(cinza))


def _medir_k_para_a_letra(cinza: np.ndarray) -> float:
    """O k medido de verdade, sem o cache (core/aquecimento.py o chama para
    carregar o skimage antes da primeira pagina). Ver k_para_a_letra."""
    return _k_da_espessura(_medir_espessura_do_traco(cinza))


def _k_da_espessura(espessura: float | None) -> float:
    """A rampa do k entre letra fina e grossa (ver o comentario de
    ESPESSURA_DE_LETRA_FINA); sem medida, K_NORMAL."""
    if espessura is None:
        return K_NORMAL
    fatia = np.clip(
        (espessura - ESPESSURA_DE_LETRA_FINA)
        / (ESPESSURA_DE_LETRA_GROSSA - ESPESSURA_DE_LETRA_FINA), 0.0, 1.0)
    return K_PARA_LETRA_FINA + (K_PARA_LETRA_GROSSA - K_PARA_LETRA_FINA) * fatia


def _medir_espessura_do_traco(cinza: np.ndarray) -> float | None:
    """A medicao de verdade, sem o cache. Ver _espessura_do_traco."""
    escala = min(1.0, ALTURA_PARA_MEDIR_TRACO / max(1, cinza.shape[0]))
    if escala < 1.0:
        cinza = cv2.resize(cinza, (max(8, int(cinza.shape[1] * escala)),
                                   max(8, int(cinza.shape[0] * escala))),
                           interpolation=cv2.INTER_AREA)

    # A mesma mascara que a regua usa para medir espessura - Otsu -, para o
    # filtro e a regua nao discordarem sobre a grossura da mesma letra.
    _lim, tinta = cv2.threshold(
        cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    tinta = (tinta > 0).astype(np.uint8)
    if tinta.mean() < 0.002 or tinta.mean() > 0.6:
        return None

    distancia = cv2.distanceTransform(tinta, cv2.DIST_L2, 5)
    esqueleto = _esqueleto(tinta > 0)     # = skeletonize, em partes
    if not esqueleto.any():
        return None
    # De volta a escala da pagina: os limites de 5 e 10 pixels estao escritos
    # no tamanho de verdade, e nao no reduzido.
    return float(2.0 * distancia[esqueleto].mean()) / escala


def palavra_do_ajuste(valor: int) -> str:
    """O ajuste em palavras, para o usuario nao precisar ler numero."""
    for limite, palavra in PALAVRAS_DA_FORCA:
        if int(valor) < limite:
            return palavra
    return PALAVRAS_DA_FORCA[-1][1]


def doxapy_disponivel() -> bool:
    """Informa se estamos no caminho rapido (DoxaPy) ou no plano B (skimage)."""
    try:
        import doxapy  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


# --- filtros ----------------------------------------------------------------

def _para_cinza(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# Saturacao (HSV, 0 a 255) a partir da qual a tinta e "colorida de proposito"
# (rubricacao, iluminura), e nao o marrom da tinta velha. Usada pelo Melhorar e
# pelo Magico pro (tirar_o_amarelado_da_tinta, _realcar_saturacao).
SATURACAO_DE_RUBRICA = 60


def _cinza_para_binarizar(img: np.ndarray) -> np.ndarray:
    """O cinza que o Preto e branco binariza: o BRILHO comum (BT.601, o
    cv2.COLOR_BGR2GRAY), em que a tinta colorida fica escura como a preta.

    Decisao do Samuel (conferencia 2 de 30/09/2026, cartao V1: "No Preto e
    branco, o que e vermelho (titulos, rubrica) sai preto?" - "BOM"): no Preto
    e branco o vermelho, e qualquer letra colorida, sai PRETO.

    Historia: ate 30/09 esta funcao usava o MAIOR dos tres canais quando a cor
    era minoria na pagina, escolhido em 2026 para a pauta vermelha do Graduale
    nao virar barras pretas. Com isso a tinta vermelha lia como clara e sumia:
    "TABLE" e "CONTENU EN CE LIVRE." da Horas 13 e as letras "A" douradas da
    Horas 27 nao saiam (Lista de bugs, 30/09). Medido em 30/09 pelo caminho
    inteiro do programa: a pauta do Graduale 222 ja saia preta (a pagina passa
    de 25% de pontos coloridos, e ali ja valia o brilho comum); com o brilho
    em toda pagina, o Graduale 221 e o 222 saem identicos ponto a ponto, e os
    titulos vermelhos e as letras douradas voltam.

    Arriscado mudar: voltar ao maior canal (os titulos vermelhos somem de novo).
    Fica numa funcao so para o Preto e branco ter um lugar unico onde o cinza e
    escolhido.
    """
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _despeckle(binaria: np.ndarray, altura: int) -> np.ndarray:
    """Remove manchinhas isoladas de preto (poeira do scanner).

    A área minima acompanha a resolução: a 600 DPI a mesma sujeira ocupa
    4x mais pixels que a 300 DPI.
    """
    escala = max(1.0, altura / 3000.0) ** 2
    area_min = max(4, int(AREA_MINIMA_RUIDO_300DPI * escala))

    # Componentes de PRETO, entao invertemos antes de contar.
    invertida = cv2.bitwise_not(binaria)
    num, rotulos, stats, _ = cv2.connectedComponentsWithStats(invertida, connectivity=8)
    if num <= 1:
        return binaria

    areas = stats[:, cv2.CC_STAT_AREA]
    pequenos = np.zeros(num, dtype=bool)
    pequenos[1:] = areas[1:] < area_min  # o rotulo 0 e o fundo
    if not pequenos.any():
        return binaria

    limpa = binaria.copy()
    limpa[pequenos[rotulos]] = 255
    return limpa


# --- a letra colorida no Preto e branco (conferencia 5, A1/I2) --------------
#
# Samuel, conferencia 5 (01/10/2026), Horas 47: "o 'JESUS' e o 'C' dourados
# quase somem" - "Eu preciso conseguir enchergar todas as letras da folha";
# "tem que reconhecer as letras mesmo em outras cores". O brilho comum
# (_cinza_para_binarizar) ve o dourado quase da cor do papel (cinza 160 contra
# 225, e o brilho do ouro varia dentro da letra): o binarizador o parte em
# pedacos. A decisao V1 ("letra colorida sai preta") vale para o dourado.
#
# O ponto cuja COR fica longe da cor do papel (a distancia em a e b do LAB, a
# mesma medida da decoracao, DECORACAO_CROMA) passa a preto, somado ao preto
# do binarizador: e o limiar fixo sobre a distancia de cor ao fundo. Nada que
# o binarizador ja punha preto sai. Medido: o dourado de JESUS fica a 33 do
# papel; manchas e o papel ambar do retrato do Palatino 5, abaixo de 20.
# Mudou 0 a 0,05% dos pontos nas paginas sem cor do gabarito (Palatino 9, 10,
# 67, Marial 7, Graduale 222, Opus 20) - no Palatino 67, os numeros escritos a
# mao em vermelho ("8", "28") saem mais cheios.
# Arriscado: baixar COR_DE_TINTA (a mancha amarelada vira preto) ou tirar a
# porta (a pagina sem cor pagaria a conta da cor: ~40 ms a 300 DPI).
COR_DE_TINTA = 21.0
# A porta: so faz a conta se pelo menos esta fracao da pagina (contada de 8
# em 8 pontos: a porta custa ~4 ms, e de 4 em 4 custava ~15) tem cor de
# tinta. Medido de 4 em 4: Marial 7 0,003%, Palatino 10 0,002%, as paginas do
# meio do marial_300 (o livro do teste de velocidade) 0,006% a 0,013% (ficam
# de fora); Palatino 67 0,04%, Horas 47 38%.
COR_DE_TINTA_NA_PAGINA = 0.0002


def _com_a_tinta_colorida(img: np.ndarray, binaria: np.ndarray) -> np.ndarray:
    """binaria (0 = preto) com os pontos de cor de tinta tambem pretos - ver
    COR_DE_TINTA. img: a pagina (BGR; em cinza, nada muda)."""
    if img.ndim != 3:
        return binaria
    pequena = cv2.cvtColor(np.ascontiguousarray(img[::8, ::8]), cv2.COLOR_BGR2LAB)
    luz = pequena[:, :, 0]
    papel = luz >= _percentil(luz, BRANCO_PERCENTIL)
    if not papel.any():
        return binaria
    a_papel = float(np.median(pequena[:, :, 1][papel]))
    b_papel = float(np.median(pequena[:, :, 2][papel]))
    longe = np.hypot(pequena[:, :, 1].astype(np.float32) - a_papel,
                     pequena[:, :, 2].astype(np.float32) - b_papel) >= COR_DE_TINTA
    if float(longe.mean()) < COR_DE_TINTA_NA_PAGINA:
        return binaria
    # a pagina inteira, em contas de 8 bits: |a - a do papel|^2/4 +
    # |b - b do papel|^2/4 por tabela, contra COR_DE_TINTA^2/4
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    quarto = np.minimum(255, np.arange(256, dtype=np.float32) ** 2 / 4.0).astype(np.uint8)
    da = cv2.absdiff(cv2.extractChannel(lab, 1), int(round(a_papel)))
    db = cv2.absdiff(cv2.extractChannel(lab, 2), int(round(b_papel)))
    soma = cv2.add(cv2.LUT(da, quarto), cv2.LUT(db, quarto))
    tinta = cv2.compare(soma, COR_DE_TINTA * COR_DE_TINTA / 4.0, cv2.CMP_GE)
    tinta = _so_a_tinta_de_borda_nitida(tinta, soma)
    return cv2.bitwise_and(binaria, cv2.bitwise_not(tinta))


# Letra colorida ou mancha colorida? (verificador, 01/10/2026: no Palatino 66 a
# mancha cor de ferrugem entre "D." e "Xlv" virava um borrao preto, e outra um
# ponto preto no alto do "P" de "Palatinus"; antes sumiam - regra R4, "tirar
# manchas sem mexer no titulo".) A tinta da letra (impressa ou pintada) tem a
# BORDA NITIDA: a cor muda de uma vez entre a letra e o papel. A mancha de
# ferrugem ou de umidade se espalha pela fibra do papel e a borda dela e
# esmaecida. A medida e a nitidez da borda (a acutancia): a media do
# gradiente de Sobel da distancia de cor ao papel nos pontos da beirada de
# cada peca. Medido (Sobel 3x3, distancia de cor em unidades de a e b do LAB):
# letras douradas da Horas 47 47 a 80; titulos vermelhos da Horas 13 52 a 64;
# "A" dourados da Horas 27 36 a 48; douradas da Horas 14 61 a 71; numeros
# vermelhos a mao do Palatino 67 29 a 50 (um pedaco, 13); pauta vermelha do
# Graduale 223 20 a 30. Manchas: Palatino 66 5,9 e 6,2; Pesel 2 4,9 a 9,7;
# pontos do papel ambar do Palatino 5 4,6 a 12. A peca abaixo de
# BORDA_DE_TINTA nao entra (fica so o preto do binarizador, como antes da
# regra da cor). Arriscado: subir (a pauta vermelha e a letra a mao clara
# saem da regra) ou descer (a mancha volta a virar borrao). A letra colorida
# grudada numa mancha fica com a borda media da mancha e tambem nao entra.
BORDA_DE_TINTA = 16.0


def _so_a_tinta_de_borda_nitida(tinta: np.ndarray, soma: np.ndarray) -> np.ndarray:
    """tinta (uint8, 255 = cor de tinta) so com as pecas de borda nitida - ver
    BORDA_DE_TINTA. soma: o quadrado/4 da distancia de cor ao papel, ponto a
    ponto (8 bits, como em _com_a_tinta_colorida)."""
    if not cv2.countNonZero(tinta):
        return tinta
    # so na caixa da tinta, com 1 ponto de folga para o Sobel
    x, y, w, h = cv2.boundingRect(tinta)
    y0, y1 = max(0, y - 1), min(tinta.shape[0], y + h + 1)
    x0, x1 = max(0, x - 1), min(tinta.shape[1], x + w + 1)
    pedaco, s = tinta[y0:y1, x0:x1], soma[y0:y1, x0:x1]
    # a distancia de cor (a raiz de 4 x soma), em 8 bits
    raiz = np.minimum(255.0, np.sqrt(4.0 * np.arange(256, dtype=np.float32)))
    distancia = cv2.LUT(s, (raiz + 0.5).astype(np.uint8))
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(pedaco, connectivity=8)
    beirada = cv2.subtract(pedaco, cv2.erode(pedaco, np.ones((3, 3), np.uint8)))
    pontos_xy = cv2.findNonZero(beirada)          # bem mais rapido que np.flatnonzero
    if pontos_xy is None:
        return tinta
    pontos_xy = pontos_xy.reshape(-1, 2)
    onde = pontos_xy[:, 1].astype(np.int64) * beirada.shape[1] + pontos_xy[:, 0]
    # o gradiente so nos pontos da beirada (na folha inteira, o dobro do tempo)
    gx = cv2.Sobel(distancia, cv2.CV_16S, 1, 0).ravel()[onde].astype(np.float32)
    gy = cv2.Sobel(distancia, cv2.CV_16S, 0, 1).ravel()[onde].astype(np.float32)
    r = rotulos.ravel()[onde]
    total = np.bincount(r, weights=np.hypot(gx, gy), minlength=quantas)
    pontos = np.maximum(np.bincount(r, minlength=quantas), 1)
    sai = np.flatnonzero((total / pontos) < BORDA_DE_TINTA)
    sai = sai[sai > 0]
    saida = tinta.copy()
    # so as pecas de borda esmaecida saem, cada uma na caixa dela
    for k in sai:
        x, y, w, h = (int(v) for v in medidas[k, :4])
        caixa = (slice(y0 + y, y0 + y + h), slice(x0 + x, x0 + x + w))
        saida[caixa][rotulos[y:y + h, x:x + w] == k] = 0
    return saida


# --- a letra fina no Otsu (conferencia 6, A1, 02/10/2026) -------------------
#
# Samuel, Horas 47 no Preto e branco: "Ainda esta apagando as letras, o
# original esta muito melhor para ler" - as letras da pagina inteira saiam
# finas, falhadas e picotadas ("Changeant", "ayez pitie de nous"). Causa: a
# escolha automatica poe o OTSU nas paginas de traco grosso (as Horas, o
# Graduale, a Escola, o Opus 20 a 300 DPI); o Otsu e UM limiar para a folha
# toda, e numa folha com moldura e iluminura ele cai no meio do tom da letra
# (161, com papel em 224 e o miolo da letra azul ou parda entre 90 e 140): a
# beirada da letra, macia porque o scan e de baixa resolucao, vira papel, e o
# traco fino some aos pedacos. O Sauvola na mesma letra sai cheio, mas sozinho
# ele quebra a letra gotica pesada (o motivo do Otsu, ver ESPESSURA_DE_LETRA_
# GROSSA) e marca de preto o que o Otsu deixa de fora de proposito: os riscos
# de pauta a ponta seca do Graduale, a mancha fraca.
#
# A juncao e por HISTERESE (a mesma ideia consagrada do limiar duplo do
# Canny): o Otsu diz ONDE ha letra, o Sauvola diz ATE ONDE ela vai. Entra a
# peca de tinta do Sauvola que o Otsu ja tem em parte (OTSU_NA_PECA_MINIMO) -
# a letra inteira, com a beirada que o Otsu perdeu; a peca do Sauvola sem
# ponto do Otsu (o risco de pauta solto, a mancha) fica de fora. Nada do Otsu sai. A peca
# enorme ou encostada na beirada da imagem (a faixa escura do scan, a pauta
# com as notas), do Otsu ou do Sauvola, nao cresce nem faz crescer (ver
# dentro da funcao).
# A semente e vista de 2 em 2 pontos (como em _so_o_papel_da_gravura): a peca
# que so tem 1 ou 2 pontos de Otsu pode ficar de fora, e ai fica so o Otsu.
# Vale so na escolha automatica (quem escolhe "Otsu" a mao recebe o Otsu). O k
# do Sauvola e o do medidor (k_do_sauvola): nas paginas Otsu, o medidor de
# forca passa a mexer na beirada da letra.
# Arriscado: juntar sem a histerese (o Sauvola inteiro somado traz os riscos
# de pauta do Graduale 221 e a mancha); tirar a semente de 2 em 2 (custa ~0,1 s
# por pagina grande a mais).


# A peca do Sauvola entra so se o Otsu ja tem pelo menos isto dela: a letra
# falhada tem a maior parte no Otsu, e o Sauvola so completa a beirada e o
# pedaco que faltou. Medido (fracao do Otsu em cada peca do Sauvola): letras
# das Horas 47 e 13, 0,63 e 0,76 no percentil 10 (as abaixo de 0,5 na Horas 47
# sao o "JESUS" e o "C" dourados, que a regra da cor ja enche, e acentos); os
# riscos da pauta a ponta seca do Graduale 222 e 223, mediana 0,24 a 0,32; a
# sombra da beirada da folha da Horas 13 (canto de cima a direita, um fio de
# 238 pontos), 0,07. Com 0,10 os riscos do Graduale ainda ficavam mais
# compridos. Arriscado: subir (a letra muito falhada no Otsu deixa de ser
# completada) ou descer (os riscos e a sombra voltam).
OTSU_NA_PECA_MINIMO = 0.50


def _otsu_com_a_borda_do_sauvola(cinza: np.ndarray, otsu: np.ndarray,
                                 janela: int, k: float) -> np.ndarray:
    """otsu (0 = tinta: o Otsu, ja com a letra colorida de
    _com_a_tinta_colorida) mais as pecas de tinta do Sauvola (janela, k) que
    ele ja tem em boa parte - ver o comentario acima. Devolve 0/255 de um
    canal."""
    sauvola = binarizar(cinza, janela=janela, k=k, algoritmo=ALGORITMO_SAUVOLA)
    tinta_s = cv2.bitwise_not(sauvola)
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(tinta_s, connectivity=8)
    if quantas <= 1:
        return otsu
    # A peca ENORME (mais alta que 1/4 da folha ou mais larga que metade, a
    # mesma medida de _esqueleto: a pauta inteira com as notas) e a que
    # ENCOSTA NA BEIRADA da imagem (a faixa escura do scan, a lombada) nao
    # crescem nem fazem crescer: medido, na Horas 13 a faixa do scan puxava o
    # fio da beirada da folha (uma sombra) e no Graduale 222 um borrao do
    # canto da lombada. Ali vale so o Otsu.
    altura, largura = cinza.shape[:2]

    def enormes(medidas_: np.ndarray) -> np.ndarray:
        x, y = medidas_[:, cv2.CC_STAT_LEFT], medidas_[:, cv2.CC_STAT_TOP]
        w, h = medidas_[:, cv2.CC_STAT_WIDTH], medidas_[:, cv2.CC_STAT_HEIGHT]
        e = ((h > altura // 4) | (w > largura // 2)
             | (x <= 0) | (y <= 0) | (x + w >= largura) | (y + h >= altura))
        e[0] = False
        return e

    _q, rotulos_o, medidas_o, _c = cv2.connectedComponentsWithStats(
        cv2.bitwise_not(otsu), connectivity=8)
    otsu_enorme = enormes(medidas_o)
    nas_duas = cv2.bitwise_and(tinta_s[::2, ::2], cv2.bitwise_not(otsu[::2, ::2]))
    ligada = np.zeros(quantas, bool)
    pontos = cv2.findNonZero(nas_duas)
    if pontos is not None:
        pontos = pontos.reshape(-1, 2)
        ys, xs = 2 * pontos[:, 1], 2 * pontos[:, 0]
        semente = ~otsu_enorme[rotulos_o[ys, xs]]
        # quanto da peca do Sauvola o Otsu ja tem (a semente de 2 em 2
        # pontos vale 4): a peca em que o Otsu e so um cisco (menos de
        # OTSU_NA_PECA_MINIMO) nao entra - ver o comentario dela
        cheio = 4 * np.bincount(rotulos[ys[semente], xs[semente]], minlength=quantas)
        ligada = cheio >= OTSU_NA_PECA_MINIMO * medidas[:, cv2.CC_STAT_AREA]
    ligada[enormes(medidas)] = False
    ligada[0] = False                      # o papel
    # entra so a tinta do Sauvola que o Otsu nao tem, das pecas ligadas (os
    # pontos sao poucos: contar so neles e ~3 vezes mais rapido que pintar
    # peca por peca); nada do Otsu sai
    saida = otsu.copy()
    novos = cv2.findNonZero(cv2.bitwise_and(tinta_s, otsu))
    if novos is not None:
        novos = novos.reshape(-1, 2)
        entra = ligada[rotulos[novos[:, 1], novos[:, 0]]]
        saida[novos[entra, 1], novos[entra, 0]] = 0
    return saida


def filtro_preto_e_branco(
    img: np.ndarray, forca: int = AJUSTE_PADRAO, despeckle: bool = True,
    algoritmo: str = "auto",
) -> np.ndarray:
    """Preto e branco (Eco). Devolve imagem de 1 canal, só 0 e 255.

    forca vai de 0 (bem fraco, texto mais fino) a 100 (bem escuro, pega mais
    tinta e mais mancha junto).

    `algoritmo`: "auto" (o programa escolhe pela espessura do traço desta
    página, ver `escolher_algoritmo_automatico`), ou um de `ALGORITMOS_PB`
    escolhido à mão / vindo de "usar em todas" (Problema 5 do plano).
    """
    cinza = _cinza_para_binarizar(img)
    janela = janela_para_altura(cinza.shape[0])
    algoritmo_de_verdade = (
        escolher_algoritmo_automatico(cinza) if algoritmo == "auto" else algoritmo
    )
    # O meio do medidor passa a ser o k que a LETRA desta pagina pede; o
    # medidor continua andando em volta dele, para mais fraco ou mais
    # escuro. Ver k_para_a_letra. So vale para Sauvola/Wolf - o Otsu nao usa k
    # (menos na borda do Sauvola, abaixo).
    k = k_do_sauvola(forca, k_para_a_letra(cinza))
    binaria = binarizar(cinza, janela=janela, k=k, algoritmo=algoritmo_de_verdade)
    binaria = _com_a_tinta_colorida(img, binaria)
    # a borda do Sauvola depois da letra colorida: o "JESUS" dourado da Horas
    # 47, que o Otsu quase nao ve, entra como semente pela cor
    if algoritmo == "auto" and algoritmo_de_verdade == ALGORITMO_OTSU:
        binaria = _otsu_com_a_borda_do_sauvola(cinza, binaria, janela, k)
    if despeckle:
        binaria = _despeckle(binaria, cinza.shape[0])
    return binaria


def _estimar_fundo_cinza(cinza: np.ndarray) -> np.ndarray:
    """Estima a iluminacao da folha: a variacao lenta de claro e escuro.

    Sao a sombra da lombada, a luz torta do scanner e o amarelado irregular.
    O desfoque forte apaga o texto e deixa só isso.

    Truque de desempenho: como o resultado e liso por definicao, o desfoque e
    feito numa miniatura e depois esticado de volta. Desfocar a página inteira
    a 300 DPI levava quase 5 segundos por página - inviavel para 500 páginas.
    """
    altura, largura = cinza.shape[:2]
    escala = min(1.0, LARGURA_ESTIMATIVA_FUNDO / max(1, largura))
    pequena = cv2.resize(
        cinza, (max(8, int(largura * escala)), max(8, int(altura * escala))),
        interpolation=cv2.INTER_AREA,
    )
    sigma = max(2.0, pequena.shape[0] * SIGMA_FUNDO_FRACAO)
    fundo_pequeno = cv2.GaussianBlur(pequena, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.resize(fundo_pequeno, (largura, altura), interpolation=cv2.INTER_LINEAR)


def _nivel_do_papel(img: np.ndarray) -> float:
    """Quao claro esta o papel desta folha, em cinza de 0 a 255."""
    return _percentil(_para_cinza(img), BRANCO_PERCENTIL)


def _achatar_iluminacao(img: np.ndarray, nivel_papel: float) -> np.ndarray:
    """Tira a variacao de luz da folha SEM mexer na cor nem no tom geral.

    Duas diferencas para a divisão ingenua (img / fundo * 255), que foi onde a
    versão anterior estragava as capas:

    1. Dividimos pelo fundo *relativo ao nível do papel*, não pelo branco
       absoluto. Só a desigualdade e corrigida, o tom geral fica.

    2. A correcao só vale onde o fundo local ainda parece papel. Numa capa
       azul, o fundo local e escuro porque ali o conteúdo E escuro - não e
       sombra. Tratar aquilo como sombra era o que lavava a capa. O peso cai a
       zero conforme o fundo se afasta do nível do papel.

    O ganho e igual nos tres canais, o que preserva o matiz.
    """
    if nivel_papel < 1:
        return img

    fundo = _estimar_fundo_cinza(_para_cinza(img)).astype(np.float32)

    ganho = nivel_papel / (fundo + 1.0)
    np.clip(ganho, GANHO_MIN, GANHO_MAX, out=ganho)

    # peso: 1 onde o fundo esta perto do papel, 0 onde esta claramente abaixo
    razao = fundo / nivel_papel
    peso = np.clip((razao - PESO_RAZAO_MIN) / (PESO_RAZAO_MAX - PESO_RAZAO_MIN), 0.0, 1.0)
    ganho = 1.0 + (ganho - 1.0) * peso

    if ganho.dtype == np.float32 and img.ndim == 3:
        # Regra 6 (30/09/2026): a mesma conta, no mesmo array (sem as copias
        # intermediarias de 130 MB a 300 DPI). Em float32 o resultado de cada
        # ponto e o mesmo.
        saida = img.astype(np.float32)
        saida *= ganho[:, :, None]
        np.clip(saida, 0, 255, out=saida)
        return saida.astype(np.uint8)
    saida = img.astype(np.float32) * ganho[:, :, None]
    return np.clip(saida, 0, 255).astype(np.uint8)


def _balanco_de_branco(img: np.ndarray, clareza: int = AJUSTE_PADRAO) -> np.ndarray:
    """Faz o papel virar branco de verdade, tirando o amarelado.

    Olha SO para os pixels que parecem papel: claros e pouco coloridos. Calcula
    a média de cada canal neles e estica para o branco. Como a mesma logica
    ignora tinta e ilustração, a cor do conteúdo não e afetada.

    Se a página quase não tem papel branco a vista (uma capa colorida inteira,
    uma foto de página cheia), não ha o que balancear e a imagem sai como veio.
    """
    cinza = _para_cinza(img)
    hsv_s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]

    limiar_claro = _percentil(cinza, BRANCO_PERCENTIL)
    papel = (cinza >= limiar_claro) & (hsv_s <= BRANCO_SATURACAO_MAX)

    if papel.mean() < BRANCO_FRACAO_MINIMA:
        return img

    # Passo 1 - tirar so a DOMINANTE de cor (o amarelado), sem clarear nada.
    # Cada canal e puxado para a media dos tres, entao o brilho total nao muda.
    medias = [float(img[:, :, c][papel].mean()) for c in range(3)]
    media_geral = sum(medias) / 3.0
    saida = img.astype(np.float32)
    if media_geral >= 1:
        for canal in range(3):
            if medias[canal] >= 1:
                fator = media_geral / medias[canal]
                saida[:, :, canal] *= min(max(fator, 1 / BRANCO_ESCALA_MAX), BRANCO_ESCALA_MAX)
    saida = np.clip(saida, 0, 255).astype(np.uint8)

    # Passo 2 - levar o papel ao branco com uma curva de ombro, nao com uma
    # multiplicacao. So os tons a partir de OMBRO_INICIO x o nivel do papel sao
    # empurrados; abaixo disso nada muda. E o que mantem uma capa azul escura
    # com a mesma cor de sempre enquanto o papel amarelado vira branco.
    nivel_papel = _percentil(_para_cinza(saida)[papel], 50)
    if nivel_papel < 1:
        return saida
    return _curva_de_ombro(saida, nivel_papel, clareza)


def _curva_de_ombro(
    img: np.ndarray, nivel_papel: float, clareza: int = AJUSTE_PADRAO
) -> np.ndarray:
    """Mapeia nivel_papel -> 255 mexendo só na parte clara da escala.

    clareza decide ONDE o ombro comeca. Quanto mais cedo, mais tons sobem para
    o branco: o fundo fica mais limpo, ao custo de achatar o que ja era quase
    branco. E o medidor "Clareza do fundo" do filtro Melhorar.
    """
    fracao = _entre(clareza, OMBRO_SUAVE, OMBRO_FORTE)
    inicio = max(1.0, nivel_papel * fracao)
    if nivel_papel <= inicio:
        return img

    escala = np.arange(256, dtype=np.float32)
    acima = escala >= inicio
    escala[acima] = inicio + (escala[acima] - inicio) * (255.0 - inicio) / (nivel_papel - inicio)
    tabela = np.clip(escala, 0, 255).astype(np.uint8)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = cv2.LUT(lab[:, :, 0], tabela)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _aprofundar_pretos(img: np.ndarray, percentil: float = 0.5) -> np.ndarray:
    """Puxa o ponto de preto para baixo SEM mexer no nivel do papel.

    Trabalhar no canal L do LAB (e não nos tres canais BGR) evita o desvio de
    matiz que aparecia quando cada canal era esticado por conta propria.

    A ancora e o papel, e nao o branco absoluto. A versao anterior mapeava o
    ponto de preto para 0 e o 255 para 255, o que arrasta TODO o meio da escala
    para baixo junto. Numa pagina de gravura, onde o papel ja e escuro, o
    estrago era enorme: na Rhetorica p446 o papel caia de 208 para 64 - o
    filtro que existe para clarear escurecia a folha inteira. Medido no acervo,
    era ele sozinho o responsavel, e nao o balanco de branco, que nessas
    paginas nem chega a rodar por nao achar papel branco.

    Agora o preto vai para 0 e o papel fica onde estava; so a parte de baixo da
    escala e esticada.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    luz = lab[:, :, 0].astype(np.float32)

    preto = _percentil(luz, percentil)
    papel = _percentil(luz, BRANCO_PERCENTIL)
    if preto < 1 or papel - preto < 10:
        return img

    escala = np.arange(256, dtype=np.float32)
    abaixo = escala <= papel
    escala[abaixo] = (escala[abaixo] - preto) * (papel / (papel - preto))
    tabela = np.clip(escala, 0, 255).astype(np.uint8)

    lab[:, :, 0] = cv2.LUT(lab[:, :, 0], tabela)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _recompor_a_rampa(original: np.ndarray, saida: np.ndarray) -> np.ndarray:
    """Devolve a borda da letra o meio-tom que as curvas de contraste comem.

    As curvas que limpam a pagina - o ombro que leva o papel a branco e o
    esticao do ponto de preto - deixam o salto entre tinta e papel mais
    ingreme. Isso e bom no meio da letra e ruim na borda dela: os poucos pixels
    de tom intermediario que a arredondam caem para um lado ou para o outro, e a
    borda vira degrau. Medido pela regua do projeto, a rampa do Graduale caia de
    2,38 para 0,68 pixels; era o defeito mais frequente do acervo, 35 das 53
    paginas que sairam piores que o original.

    Aqui a rampa e reconstruida: para cada pixel da orla, olha-se ONDE ele
    estava entre o preto e o papel na imagem original, e ele e recolocado na
    mesma posicao relativa entre o preto e o papel da imagem tratada. A forma da
    borda volta a ser a do original, agora entre um preto mais fundo e um papel
    mais claro.

    So a orla e mexida. O miolo da letra e o papel aberto ficam como o filtro os
    deixou.
    """
    cinza_antes = _para_cinza(original)
    cinza_depois = _para_cinza(saida)

    preto_antes = _percentil(cinza_antes, 2)
    papel_antes = _percentil(cinza_antes, BRANCO_PERCENTIL)
    if papel_antes - preto_antes < 20:
        return saida

    tinta = (cinza_antes < papel_antes * TINTA_PARA_ORLA).astype(np.uint8)
    if not tinta.any():
        return saida

    lado = max(3, int(min(saida.shape[:2]) / ORLA_DA_LETRA) | 1)
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))
    orla = (cv2.dilate(tinta, nucleo) > 0) & (cv2.erode(tinta, nucleo) == 0)
    if not orla.any():
        return saida

    preto_depois = _percentil(cinza_depois[tinta > 0], 20)
    papel_depois = _percentil(cinza_depois[tinta == 0], 80) \
        if (tinta == 0).any() else 255.0
    if papel_depois - preto_depois < 20:
        return saida

    onde = np.clip((cinza_antes.astype(np.float32) - preto_antes)
                   / (papel_antes - preto_antes), 0.0, 1.0)
    rampa = preto_depois + onde * (papel_depois - preto_depois)

    lab = cv2.cvtColor(saida, cv2.COLOR_BGR2LAB)
    luz = lab[:, :, 0].astype(np.float32)
    # A conta e feita em cinza; o canal L do LAB segue a mesma escala de 0 a 255
    # e mexer so nele preserva o matiz da tinta colorida.
    luz[orla] = np.clip(rampa[orla], 0, 255)
    lab[:, :, 0] = luz.astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _quase_sem_tinta(img: np.ndarray) -> bool:
    """Folha em branco, guarda, verso limpo: nao ha preto a aprofundar.

    Numa folha assim o ponto de preto cai em cima do proprio ruido do scanner, e
    estica-lo e amplificar grao: medido, a pagina 446 da Rhetorica saia com o
    ruido de fundo subindo de 1,8 para 7,6.
    """
    cinza = _para_cinza(img)
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)
    if nivel_papel < 1:
        return True
    return float((cinza < nivel_papel * TINTA_PARA_ORLA).mean()) < TINTA_DE_FOLHA_ESCRITA


# Matiz do papel envelhecido, na escala do OpenCV (0 a 180, nao 0 a 360).
# Medido nas folhas sem tinta do acervo: 19,6 e 20,1 no BRODERIES, 20,5 no
# Boecio, 23,0 na Rhetorica. Todas no ambar, e bem juntas. A faixa e larga o
# bastante para caber pergaminho mais rosado ou mais esverdeado.
MATIZ_DE_PAPEL_MIN, MATIZ_DE_PAPEL_MAX = 12.0, 32.0


def _so_o_amarelado_do_papel(img: np.ndarray) -> bool:
    """A unica cor desta folha e o amarelado do proprio papel?

    Serve para decidir se ha cor a avivar. Numa folha velha sem tinta a resposta
    e nao: a unica cor ali e o amarelado, e realca-lo e o oposto do pedido - a
    folha vazia do Boecio saia de um creme palido para um amarelo forte.

    Nao basta perguntar "tem tinta?". Uma capa colorida lisa tambem nao tem
    tinta, e ali a cor E o conteudo - deixar de avivar seria tirar do Magico pro
    justamente aquilo para que ele existe, e o medidor de intensidade pararia de
    fazer efeito. Tentei separar os dois casos pela saturacao e nao da: medida
    no acervo, uma folha velha amarelada marca 0,99 de fracao colorida, MAIS que
    uma capa lisa.

    O que separa e o MATIZ. Papel envelhecido e ambar, sempre; uma capa pode ser
    de qualquer cor. Por isso a pergunta aqui e dupla: sem tinta E da cor do
    papel.
    """
    if not _quase_sem_tinta(img) or img.ndim != 3:
        return False

    cinza = _para_cinza(img)
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)
    claro = cinza >= nivel_papel * 0.95
    if claro.sum() < 100:
        return False

    # Media circular: matiz e um angulo, e a media comum erra na volta do zero.
    matiz = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 0][claro].astype(np.float32)
    angulo = matiz * 2.0 * np.pi / 180.0
    medio = np.arctan2(float(np.sin(angulo).mean()),
                       float(np.cos(angulo).mean())) * 180.0 / np.pi / 2.0
    medio = (medio + 180.0) % 180.0
    return MATIZ_DE_PAPEL_MIN <= medio <= MATIZ_DE_PAPEL_MAX


def _alisar_o_papel(img: np.ndarray) -> np.ndarray:
    """Tira o grao do papel sem encostar na tinta.

    As curvas que clareiam a folha multiplicam o que ja estava la: numa pagina
    de papel escuro e granulado, levar o papel de 159 para 255 leva junto o
    ruido de 11 para 18. Alisar SO o papel resolve sem tocar na letra - o
    alisamento fica de fora da tinta e da orla dela, que sao justamente o que
    precisa continuar nitido.
    """
    cinza = _para_cinza(img)
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)
    if nivel_papel < 1:
        return img

    tinta = (cinza < nivel_papel * TINTA_PARA_ORLA).astype(np.uint8)
    lado = max(3, int(min(img.shape[:2]) * ORLA_DA_TINTA_NO_PAPEL) | 1)
    perto_da_tinta = cv2.dilate(
        tinta, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    alisada = cv2.medianBlur(img, 3)
    saida = img.copy()
    # copyto com "where" = saida[~perto] = alisada[~perto], sem montar as duas
    # listas de pontos no meio (regra 6, 30/09/2026)
    longe = ~perto_da_tinta
    np.copyto(saida, alisada, where=longe[:, :, None] if saida.ndim == 3 else longe)
    return saida


def _e_capa_e_nao_papel(img: np.ndarray) -> bool:
    """Isto e a encadernacao do livro, ou uma folha de papel?

    A diferenca decide se ha papel a branquear. Numa capa nao ha: o que parece
    papel e o couro. Numa folha de guarda em branco ha, e ela tem de ir a
    branco - foi o pedido do Kaique.

    Pergunta emprestada do detector de regioes, que decide a mesma coisa para
    marcar ou nao a pagina como gravura. Manter a resposta num lugar so evita
    que o filtro e o detector discordem sobre a mesma folha.
    """
    try:
        from core.detectar_regioes import _e_objeto_e_nao_folha, _pagina_sem_conteudo

        colorida = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return bool(_pagina_sem_conteudo(colorida)
                    and _e_objeto_e_nao_folha(colorida))
    except Exception:  # noqa: BLE001 - na duvida, limpa como sempre limpou
        return False


def filtro_melhorar(img: np.ndarray, clareza: int = AJUSTE_PADRAO,
                    dentro_da_gravura: bool = False) -> np.ndarray:
    """Melhorar: fundo branco limpo, cores originais preservadas.

    clareza vai de 0 (fundo quase como veio) a 100 (fundo bem branco).

    dentro_da_gravura=True so e usado por _limpar_cada_gravura, que roda este
    filtro no recorte de cada gravura: ai a limpeza final do papel so branqueia
    o papel de verdade, e nao a pintura clara (ver _limpar_o_papel_de_verdade).
    """
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Numa CAPA nao ha papel a branquear: o que ali parece papel e o couro, a
    # madeira ou o pergaminho da encadernacao, e branquear aquilo estica o
    # mosqueado dele. Medido na capa do Boecio, passo a passo: o balanco de
    # branco leva o ruido de 5,9 para 13,3 e o ponto de preto de 13,3 para 17,5.
    # A folha de guarda EM BRANCO nao entra aqui - ela e papel, e tem de
    # branquear mesmo. Ver _e_capa_e_nao_papel.
    # Numa capa nem o achatamento de iluminacao serve: nao ha luz torta de
    # scanner a corrigir, o que varia e o relevo do proprio objeto, e achatar
    # aquilo o escurece. Medido na capa de couro verde do Livro de Horas, o
    # achatamento sozinho levava o fundo de 219 para 194. Fica so o alisamento,
    # que tira grao sem mexer no tom: nas tres capas medidas o fundo nao se move
    # um decimo, e o ruido cai.
    # Nem a recomposicao da rampa entra: ela existe para devolver a borda da
    # LETRA ao lugar, e numa capa nao ha letra. Medido na capa de couro vermelho
    # do Graduale, ela sozinha levava o fundo de 47,4 para 43,9. Sobra o
    # alisamento, que tira grao sem mexer no tom: nas tres capas medidas o fundo
    # nao anda um decimo, e o ruido do Boecio cai de 5,52 para 4,48.
    if _e_capa_e_nao_papel(img):
        return _alisar_o_papel(img.copy())

    saida = _achatar_iluminacao(img, _nivel_do_papel(img))
    saida = _balanco_de_branco(saida, clareza)
    if not _quase_sem_tinta(img):
        saida = _aprofundar_pretos(saida)
    saida = _alisar_o_papel(saida)
    saida = _recompor_a_rampa(img, saida)
    return _limpar_o_papel_de_verdade(img, saida, dentro_da_gravura=dentro_da_gravura)


def _contraste_local_no_conteudo(img: np.ndarray, intensidade: int) -> np.ndarray:
    """Realce de contraste local (CLAHE) so onde ha conteudo.

    O CLAHE aplicado na folha inteira estica o histograma tambem dos ladrilhos
    que sao so papel. Como ali nao ha o que realcar, ele faz duas coisas ruins
    de uma vez: amplia o grao do scanner - que e o que o Kaique enxerga como
    "pixelado" - e ainda puxa o papel para baixo, deixando o fundo mais escuro
    justamente no filtro que deveria embranquece-lo.

    Medido nos nove livros do acervo, so desligar este passo levava o ruido de
    fundo de 13,6 para 6,4 e o papel de 197 para 219. Em vez de desligar - o
    que apagaria o realce das gravuras, que e a razao de existir deste filtro -
    o efeito passa a ser pesado: cheio no conteudo escuro, nulo no papel.

    O peso trabalha no canal de luminosidade do LAB, entao o matiz nao muda.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    luz = lab[:, :, 0]

    nivel_papel = _percentil(luz, BRANCO_PERCENTIL)
    if nivel_papel < 1:
        return img

    clahe = cv2.createCLAHE(
        clipLimit=_entre(intensidade, CLAHE_CLIP_MIN, CLAHE_CLIP_MAX),
        tileGridSize=CLAHE_GRADE,
    )
    realcada = clahe.apply(luz).astype(np.float32)

    original = luz.astype(np.float32)
    peso = _peso_do_conteudo(original, nivel_papel)

    lab[:, :, 0] = np.clip(
        original * (1.0 - peso) + realcada * peso, 0, 255
    ).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _peso_do_conteudo(luz: np.ndarray, nivel_papel: float) -> np.ndarray:
    """0 no papel, subindo ate 1 no conteudo bem mais escuro que ele.

    A rampa comeca abaixo do nivel do papel para que o papel inteiro - e nao so
    a metade mais clara dele - fique de fora do realce.
    """
    inicio = nivel_papel * CLAHE_INICIO_CONTEUDO
    faixa = max(1.0, inicio * CLAHE_FAIXA_CONTEUDO)
    return np.clip((inicio - luz) / faixa, 0.0, 1.0)


def _realcar_saturacao(img: np.ndarray, ganho: float = SATURACAO_GANHO) -> np.ndarray:
    """Cor mais viva NO CONTEUDO. No papel, cor nenhuma a avivar.

    Aplicado na folha inteira, este passo pinta o grao do papel: medido no
    acervo, a cor do papel subia de 14,9 para 24,6 no Boecio e de 13,7 para 20,6
    no Marial, e o que se ve na pagina limpa e um chuvisco de pontinhos rosa e
    verde onde deveria haver so branco.

    O peso NAO pode ser o do contraste local, que olha so o brilho: numa capa
    colorida de pagina inteira a propria capa vira "o papel" daquela folha, e a
    capa deixaria de ganhar cor - que e para o que este filtro existe. O que
    separa papel de conteudo aqui e a dupla claro E sem cor: grao de papel e
    claro e quase cinza; tinta colorida, mesmo clara, tem cor de verdade.

    Este passo continua em HSV, e nao e por falta de tentativa. Subir o S do HSV
    mantem o V, mas nao mantem a luminancia (0,299 R + 0,587 G + 0,114 B): numa
    cor quente o verde cai, e o verde carrega quase seis decimos do peso. Por
    isso o passo escurecia o papel velho, que e sempre amarelo-pardo.

    A troca obvia - subir a cor em LAB, que preserva o L - foi medida e
    REVERTIDA. Ela conserta o papel, mas faz o mesmo estrago do outro lado: L*
    nao e a luminancia do cinza, e num vermelho saturado manter L* enquanto se
    afasta do eixo cinza tambem derruba o verde. Na pagina 376 do Graduale, de
    rubricacao vermelha, a letra engrossou e os vazios internos cairam de 18%
    para 30% abaixo do original - entupimento de letra, que e o defeito mais
    grave que existe aqui. Trocava um problema por outro pior.

    O YCrCb, que preserva exatamente a luminancia do cinza, foi medido tambem:
    conserta o papel em TODAS as paginas - inclusive as duas que o guarda de
    folha vazia nao alcanca, a capa do Palatino e a folha 1 do Graduale - mas
    engrossa a mesma rubricacao do Graduale 376, de 18% para 28%. Preservar a
    luminancia nao basta: o que binariza a letra e a conversao para cinza por
    VALUE (o maior canal), e essa nao ve o Y.

    O caminho que sobra, para quem pegar isto depois: deixar a TINTA de fora do
    realce, e nao so o papel claro. O peso abaixo separa papel de conteudo pelo
    par claro-e-sem-cor; falta uma terceira condicao que reconheca tinta
    colorida - a rubricacao - e a preserve. Ai da para trocar o espaco de cor
    sem engrossar letra nenhuma.
    """
    cinza = _para_cinza(img)
    saturacao = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1].astype(np.float32)
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)

    claro = cinza > nivel_papel * CLARO_COMO_PAPEL
    tem_cor = np.clip(
        (saturacao - SATURACAO_DE_GRAO) / max(1.0, SATURACAO_DE_RUBRICA - SATURACAO_DE_GRAO),
        0.0, 1.0)
    peso = np.where(claro, tem_cor, 1.0).astype(np.float32)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1.0 + (ganho - 1.0) * peso), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def tirar_o_amarelado_da_tinta(img: np.ndarray,
                               fora_da_gravura: np.ndarray | None = None) -> np.ndarray:
    """Deixa neutro o que nao e cor de verdade - papel velho e tinta marrom.

    O Samuel olhou a saida do Melhorar e disse que a pagina continuava
    amarelada, "e isso e ruim porque a impressora vai entender como cor a ser
    impressa, mesmo em preto e branco". Ele estava certo, e eu tinha
    diagnosticado errado: o FUNDO ja sai entre 250 e 255. A cor esta na TINTA.

    Tinta impressa de 1579 e marrom, nao preta, e a orla de cada letra carrega
    esse marrom. Mapeados os pixels claros que ainda tem cor, eles desenham o
    texto - nao o papel. Uma pagina inteira disso o olho le como amarelada, e a
    impressora gasta tinta colorida em cada letra.

    O que fica: cor de VERDADE. A conta e a mesma que o resto do arquivo usa -
    abaixo de SATURACAO_DE_GRAO e grao de papel, acima de SATURACAO_DE_RUBRICA e
    tinta colorida de propósito. A rubricacao vermelha e a iluminura passam
    inteiras; o marrom da tinta velha, nao.

    E dentro da gravura nao se mexe em nada: ali a cor e o conteudo. Quem diz
    onde e a gravura e a selecao, por isso o peso vem de fora.

    Medido no acervo, na saida do Melhorar - fracao de pixel claro que ainda tem
    cor, contra a fracao de cor forte que TEM de sobreviver:

        Rhetorica 223, texto        7,7% -> 2,7%     18,40% -> 18,38%
        Boecio 33, texto            2,1% -> 0,4%      7,66% ->  7,69%
        Graduale 376, rubricacao    7,5% -> 2,4%     17,32% -> 17,31%
        Catecismo 199, estampa     39,6% -> 39,5%     intacta
    """
    if img.ndim != 3:
        return img

    saturacao = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1].astype(np.float32)
    guardar = np.clip(
        (saturacao - SATURACAO_DE_GRAO)
        / max(1.0, SATURACAO_DE_RUBRICA - SATURACAO_DE_GRAO), 0.0, 1.0)
    peso = 1.0 - guardar
    if fora_da_gravura is not None:
        peso = peso * np.clip(fora_da_gravura, 0.0, 1.0)
    if not peso.any():
        return img

    # Regra 6 (30/09/2026): so os canais de cor (Cr e Cb) vao para float; o
    # brilho (Y) passava por float e voltava igual (inteiro de 0 a 255). A
    # conta de cada canal e a mesma de antes, ponto por ponto.
    ycc = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    fator = 1.0 - peso
    for canal in (1, 2):
        cor = 128.0 + (ycc[:, :, canal].astype(np.float32) - 128.0) * fator
        # antes a conta ia para um array float32: o mesmo arredondamento aqui
        cor = cor.astype(np.float32, copy=False)
        ycc[:, :, canal] = np.clip(cor, 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)


def _nitidez(img: np.ndarray, peso: float = NITIDEZ_PESO) -> np.ndarray:
    """Unsharp mask: soma a propria imagem menos a versão borrada dela.

    O raio manda no resultado mais que o peso. Com raio largo, o unsharp nao
    afia o traco: ele desenha um halo claro de tres pixels em volta da letra e
    achata a rampa dela, que e o oposto do pedido - letra "arredondada e
    nitida". Medido no acervo, este passo sozinho levava a rampa de 2,71 para
    1,95 no Marial e de 1,80 para 1,32 no Boecio.

    Com raio da ordem de um pixel, o realce cai em cima da propria borda: a
    letra ganha contraste sem ganhar contorno.
    """
    sigma = max(0.8, img.shape[0] / RAIO_DA_NITIDEZ)
    borrada = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.addWeighted(img, 1.0 + peso, borrada, -peso, 0)


def _empurrar_branco(img: np.ndarray, limiar: int = BRANCO_LIMIAR) -> np.ndarray:
    """Pixels quase brancos viram branco puro: acaba com o cinza de fundo.

    Menos a ORLA COLADA NA TINTA. Ali mora a rampa de antisserrilhamento, os
    poucos pixels de tom intermediario que arredondam a letra; jogados a branco,
    a letra vira escada - e a queixa do Kaique de "letras pixeladas". Medido no
    acervo, so este corte levava a rampa de 1,32 para 1,03 no Boecio e de 1,95
    para 1,58 no Marial.

    O miolo do papel continua indo a branco puro: o ruido de fundo medido
    continua zero. O que sobra fora do branco e uma orla de dois pixels em volta
    das letras, que e justamente o que faz a letra parecer redonda.
    """
    cinza = _para_cinza(img)
    quase_branco = cinza >= limiar

    # A orla e medida a partir da TINTA, e nao do proprio branco. Encolher a
    # mascara de branco nao serve: onde o papel tem grao ela fica furada, e cada
    # furo abriria um anel cinza no meio do papel aberto - medido, 80% do papel
    # do Boecio deixava de ir a branco.
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)
    tinta = (cinza < nivel_papel * TINTA_PARA_ORLA).astype(np.uint8)

    lado = max(3, int(min(img.shape[:2]) / ORLA_DA_LETRA) | 1)
    orla = cv2.dilate(
        tinta, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    saida = img.copy()
    _pintar_de_branco(saida, quase_branco & ~orla)     # saida[...] = 255

    # A orla fica, mas sem a cor do papel: mantida como veio, ela vira um halo
    # creme em volta de cada letra sobre o papel branco. Igualando os tres
    # canais ao brilho do pixel, a rampa continua existindo em tom de cinza e o
    # amarelado some junto com o resto do fundo.
    if saida.ndim == 3:
        de_fora = orla & quase_branco
        if de_fora.any():
            _copiar_o_cinza(saida, de_fora, cinza)     # saida[de_fora] = cinza
    return saida


def _limpar_o_papel_de_verdade(original: np.ndarray, saida: np.ndarray,
                               dentro_da_gravura: bool = False) -> np.ndarray:
    """O que nao e tinta vira papel branco puro - inclusive a mancha do verso.

    O empurrao de branco antigo usava um limiar fixo (235). Numa folha amarelada
    o papel tratado fica em 225 e a mancha do verso em 210: nenhum dos dois
    passa do limiar, entao o fundo continuava creme e a mancha continuava
    legivel. Foram as duas queixas do Samuel sobre o Melhorar e o Magico pro:
    "nao tirou a mancha do verso" e "ainda deixa o fundo meio amarelado (e isso
    e ruim porque a impressora vai entender como cor a ser impressa)".

    O limiar fixo e o erro. Quem sabe separar a tinta da mancha nao e um numero
    e sim o SAUVOLA - ele compara cada pixel com a vizinhanca dele, e a mancha
    do verso perde justamente por ser mais fraca que a vizinhanca. E a mesma
    conta que o Preto e branco ja faz, e ali a mancha some. Entao a pergunta
    passa a ser feita a ele: o que o Preto e branco chamaria de papel, aqui vira
    branco puro; o resto fica com o tom que o filtro deu.

    A orla colada na tinta continua de fora, pelo mesmo motivo de sempre: ali
    mora a rampa de antisserrilhamento, e joga-la a branco serrilha a letra.

    Nao entra em capa nem em folha sem tinta - em nenhuma dessas o "fundo" e
    papel, e branquear objeto e o oposto do pedido.

    Dentro da gravura (dentro_da_gravura=True, chamado por _limpar_cada_gravura)
    a pergunta final muda. Numa pagina de texto, tudo o que nao e letra e papel;
    numa gravura, nao: o pano quase branco da roupa do anjo e o cinza claro da
    foto da estatua sao PINTURA, e iam a branco por aqui - era o bug dos
    quadradinhos de 28/09/2026. Ali quem decide e _so_o_papel_da_gravura, que so
    branqueia o papel de gravura de TRACO (xilogravura, tabela) e deixa a de tom
    continuo (pintura, foto) como o Melhorar a deixou. As travas de cima (capa,
    tinta de menos ou de mais, poucas pecas de letra) e o "nao escuro" valem
    igual nos dois casos; o "longe da letra" e a trava de cor fixa, nao - la o
    papel e o ponto no nivel do fundo em volta, com a cor do papel DELA.
    """
    if _e_capa_e_nao_papel(original) or _quase_sem_tinta(original):
        return saida

    cinza = _para_cinza(original)
    tinta = binarizar(cinza, k=k_para_a_letra(cinza)) == 0
    fracao = float(tinta.mean())
    # Sem tinta nenhuma nao ha o que preservar; com tinta demais nao e letra, e
    # hachura de gravura - e ali limpar arranca o meio-tom.
    if fracao < 0.0005 or fracao > TINTA_DEMAIS_PARA_LIMPAR:
        return saida

    # O Sauvola sozinho nao basta: ele tambem pega a parte mais forte da mancha
    # do verso, e ali ela vira um fantasma cinza. O que separa os dois nao e o
    # tom e sim o TAMANHO DA PECA - a mancha e um chuvisco de pontinhos, a letra
    # e um traco inteiro. Medido na pagina 33 do Boecio: 66 pixels de area
    # mediana no texto contra 4 na mancha. Ver PECA_DE_LETRA_MINIMA.
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(
        tinta.astype(np.uint8), 8)
    corte = max(4.0, PECA_DE_LETRA_MINIMA * original.shape[0] * original.shape[1])
    grandes = np.zeros(quantas, bool)
    grandes[1:] = medidas[1:, cv2.CC_STAT_AREA] >= corte
    if int(grandes.sum()) < PECAS_DE_TEXTO_MINIMAS:
        return saida

    # Dentro da gravura, daqui em diante a pergunta e outra (ver a docstring e
    # _so_o_papel_da_gravura): o "longe da letra" de baixo nao e usado la, e
    # pula-lo poupa a conta mais cara desta funcao (o np.isin da pagina toda).
    if dentro_da_gravura:
        return _so_o_papel_da_gravura(original, saida)

    semente = grandes[rotulos]

    lado = max(3, int(min(original.shape[:2]) / ORLA_DA_LETRA) | 1)
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))
    perto = cv2.dilate(semente.astype(np.uint8), nucleo) > 0

    # Acento, pingo do i e serifa solta sao pecas pequenas, mas encostadas numa
    # grande. Elas voltam: peca pequena que toca a orla de uma grande conta como
    # letra. Peca pequena isolada no meio do papel e a mancha, e sai.
    # (regra 6, 30/09/2026: uma tabela por rotulo no lugar do np.isin da
    # pagina inteira - a mesma resposta, ponto por ponto, umas 10x mais rapida)
    encostadas = np.zeros(quantas, bool)
    encostadas[rotulos[perto & tinta]] = True
    encostadas[0] = False
    de_letra = encostadas[rotulos] if encostadas.any() else semente

    perto_da_tinta = cv2.dilate(de_letra.astype(np.uint8), nucleo) > 0

    # Rede de seguranca: pixel muito escuro fica onde esta, mesmo longe de
    # letra. E melhor deixar uma sujeira escura do que apagar tinta fraca.
    #
    # A pergunta e feita ao ORIGINAL, e nao a saida. O Magico pro realca
    # contraste local, e o realce escurece a mancha do verso junto com o resto -
    # perguntado a saida dele, o proprio realce promovia a mancha a "escura
    # demais para ser mancha" e a protegia. Medido nesta pagina, era a unica
    # diferenca entre o Melhorar sair limpo e o Magico pro sair com fantasma.
    escuro = cinza < _percentil(cinza, BRANCO_PERCENTIL) \
        * ESCURO_DEMAIS_PARA_SER_MANCHA

    # E so entra onde a cor e a do PAPEL. A mancha do verso e amarelo-pardo,
    # do mesmo tom do resto da folha; ceu de estampa, rubricacao vermelha,
    # couro verde e madeira nao sao. Sem esta trava, a estampa colorida do
    # Catecismo perdia o ceu azul inteiro - o fundo dela e claro e tem pouca
    # tinta escura, entao passava por "papel sujo" e ia a branco.
    hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV) if original.ndim == 3 else None
    if hsv is not None:
        matiz = hsv[:, :, 0].astype(np.float32)  # mesma escala 0..179 do resto
        cor_de_papel = (hsv[:, :, 1] <= SATURACAO_DE_GRAO) | (
            (matiz >= MATIZ_DE_PAPEL_MIN) & (matiz <= MATIZ_DE_PAPEL_MAX)
            & (hsv[:, :, 1] < SATURACAO_DE_RUBRICA))
    else:
        cor_de_papel = np.ones(cinza.shape, bool)

    papel_limpo = ~perto_da_tinta & ~escuro & cor_de_papel

    limpa = saida.copy()
    _pintar_de_branco(limpa, papel_limpo)               # limpa[papel_limpo] = 255
    return limpa


# --- o papel DENTRO da gravura (bug dos quadradinhos no anjo, 28/09/2026) ----
#
# Regra do resultado da Fase 1 (Samuel, 28/09): "todo o papel totalmente
# branco, inclusive o papel dentro da gravura" (o fundo do retrato do Palatino
# 5), e "so pintura de verdade mantem a cor" (a roupa do anjo da Escola 35, o
# ceu, a foto da estatua do Opus Majus 20), sem quadradinhos.
#
# Pela COR nao da para separar: medido, o pano do anjo (luz 222 a 233, pouca
# cor) e MAIS parecido com o papel da pagina (250) do que o papel de dentro do
# retrato do Palatino 5 e parecido com o da margem dele (183 contra 213, e bem
# mais amarelado); e a estatua do Opus 20 tem a cor exata do papel, so 14 tons
# mais escura. O que separa e a ESTRUTURA: xilogravura e tabela sao traco fino
# e escuro sobre papel liso; pintura e foto sao tom continuo, sem traco.
#
# O traco fino e achado pelo "top-hat preto" (fechamento menos a imagem), a
# operacao consagrada de morfologia para tirar letra e traco escuro de cima de
# um fundo irregular: o fechamento apaga o que e mais fino que o elemento e
# deixa o fundo; a diferenca e o traco.

# Elemento do fechamento, em fracao do menor lado do recorte: bem mais largo
# que um traco de xilogravura ou de letra (3 a 8 pontos a 300 DPI), bem mais
# estreito que uma area de tinta de verdade (o escuro de uma porta na foto).
TRACO_FECHAMENTO = 1 / 90

# Um ponto e traco quando fica abaixo de 60% do fundo em volta (o mesmo
# TINTA_PARA_ORLA do resto do arquivo) e o fundo em volta e claro, perto do
# papel: tinta sobre papel, e nao a textura de uma area escura de foto.
TRACO_CONTRASTE = 0.40
TRACO_SOBRE_PAPEL = 0.80

# Densidade do traco: media numa vizinhanca de 1/25 do menor lado. Medido no
# gabarito (densidade media): pintura do anjo e da Escola 7 = 0,000; foto do
# Opus 20 = 0,001 (com um pico de 0,15 so no livro da mao da estatua); retrato
# do Palatino 5 = 0,09 a 0,13; tabela do Opus 256 = 0,06; Rhetorica 73 = 0,10.
# Abaixo de MIN nao e traco, acima de MAX e; no meio, a rampa.
TRACO_ESPALHAMENTO = 1 / 25
TRACO_DENSIDADE_MIN, TRACO_DENSIDADE_MAX = 0.02, 0.06

# "Tamanho da regiao": a gravura so e tratada como gravura de traco se o traco
# cobrir pelo menos esta fracao dela. Medido: foto do Opus 20 = 0,9% (so o
# livro da mao), pinturas da Escola = 0%; as de traco = 24% (tabela das Horas
# 14) a 88% (Rhetorica 73). E o que impede o livro da mao de abrir uma mancha
# branca na estatua.
GRAVURA_DE_TRACO_MINIMA = 0.05

# Qual ponto e PAPEL dentro da gravura de traco: o que esta no nivel do fundo
# (o fechamento) em volta dele, e nao "o que esta longe de letra", que e a
# pergunta da pagina de texto. Tentado primeiro com a pergunta da pagina de
# texto: no retrato do Palatino 5 a hachura fraca, que o Sauvola regulado para
# letra nao ve, ia a branco, e o traco se partia. Medido no fundo do retrato
# (luz do ponto / fundo em volta): o papel entre as linhas fica em 0,90 (a
# digitalizacao borra), a borda das linhas de 0,5 a 0,8. Abaixo de MIN o ponto
# fica como esta; acima de MAX vai a branco; no meio, a rampa - que tambem
# clareia aos poucos a orla da letra, em vez de deixar um contorno creme.
PAPEL_NO_FUNDO_MIN, PAPEL_NO_FUNDO_MAX = 0.78, 0.90

# E o fundo em volta tem de ser claro, perto do nivel do papel da gravura: numa
# mancha de tinta mais larga que o fechamento, o ponto tambem esta "no nivel do
# fundo", mas o fundo ali e a propria tinta. Medido no Palatino 5: o fundo do
# papel escurecido do retrato fica em 0,79 a 0,93 do papel da margem.
FUNDO_CLARO_MIN, FUNDO_CLARO_MAX = 0.65, 0.80

# A cor do papel de cada gravura e medida nela mesma, no papel entre os tracos
# (o papel do Palatino 5 e ambar forte, o das Horas quase cinza). Um ponto tem
# cor de papel se a distancia dele (em a,b do LAB) a mediana desse papel cabe em
# CHEIO vezes o percentil 99 das distancias do proprio papel; de CHEIO a ZERO
# vezes, a rampa. CHEIO passa de 1 de proposito: por definicao 1% do papel fica
# alem do percentil 99, e com o corte nele esse papel saia 248 em vez de 255.
# Medido: papel das Horas 13 ate 7, a moldura dourada dela a partir de 25; papel
# do Palatino 5 ate 13 (o fundo do retrato fica em 10). Arriscado subir ZERO: e
# ele que segura o dourado das molduras.
COR_DO_PAPEL_PERCENTIL = 99
COR_DO_PAPEL_RAIO_MIN = 6.0
COR_DO_PAPEL_CHEIO = 1.2
COR_DO_PAPEL_ZERO = 1.6

# A cor e medida alisada, para nao herdar a grade do JPEG: a imagem dentro do
# PDF guarda a cor em quadrados de 16x16 pontos (24x24 depois de ampliar), e
# decidir ponto a ponto sobre a cor crua era o que fazia os quadradinhos.
COR_DO_PAPEL_ALISAMENTO = 1 / 150

# Os mapas lisos (densidade do traco e cor alisada) sao calculados numa copia
# reduzida a este menor lado e esticados de volta, como o fundo em
# _estimar_fundo_cinza: o resultado e liso por definicao. Medido: a primeira
# versao deste conserto, em tamanho cheio e em ponto flutuante, deixava o filtro
# da pagina 13 das Horas (4150 x 5800) um segundo mais lento; assim, e em 8
# bits, antes e depois empatam (diferenca dentro do ruido da medida).
LADO_DOS_MAPAS_LISOS = 400


def _escala_dos_mapas(forma: tuple[int, ...]) -> float:
    """Quanto reduzir a imagem para os mapas lisos (1.0 = nao reduz)."""
    return min(1.0, LADO_DOS_MAPAS_LISOS / max(1, min(forma[:2])))


def _reduzir(mapa: np.ndarray, escala: float) -> np.ndarray:
    """Copia reduzida (media por area) de um mapa, em float32."""
    altura, largura = mapa.shape[:2]
    tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))
    return cv2.resize(mapa, tamanho, interpolation=cv2.INTER_AREA).astype(np.float32)


def _voltar(pequeno: np.ndarray, forma: tuple[int, ...]) -> np.ndarray:
    """Estica um mapa reduzido de volta ao tamanho da imagem."""
    return cv2.resize(pequeno, (forma[1], forma[0]), interpolation=cv2.INTER_LINEAR)


def _desfocar(pequeno: np.ndarray, forma: tuple[int, ...], escala: float,
              sigma_fracao: float) -> np.ndarray:
    """Desfoque gaussiano de sigma_fracao do menor lado da imagem ORIGINAL,
    feito na copia reduzida."""
    sigma = max(0.8, min(forma[:2]) * escala * sigma_fracao)
    return cv2.GaussianBlur(pequeno, (0, 0), sigmaX=sigma, sigmaY=sigma)


def _fundo_e_nivel(lab: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """A luz da gravura, o fundo dela sem os tracos finos e o nivel do papel.

    O fundo e o fechamento (TRACO_FECHAMENTO): em cada ponto, o nivel do papel
    em volta, com a letra e a hachura apagadas. O nivel do papel e o percentil
    85 da gravura, o mesmo BRANCO_PERCENTIL do resto do arquivo. Tudo em 8 bits.
    """
    luz = np.ascontiguousarray(lab[:, :, 0])
    lado = max(9, int(min(luz.shape) * TRACO_FECHAMENTO) | 1)
    fundo = cv2.morphologyEx(
        luz, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
    nivel = _percentil(luz[::4, ::4], BRANCO_PERCENTIL)
    return luz, fundo, nivel


def _peso_de_traco(luz: np.ndarray, fundo: np.ndarray, nivel: float) -> np.ndarray:
    """0 a 255: quanto cada ponto esta numa area de TRACO SOBRE PAPEL.

    255 na xilogravura, na tabela e no texto; 0 na pintura e na foto. E a pista
    "textura e sombreado": traco fino e escuro sobre fundo claro e liso so
    existe em gravura de traco. Ver TRACO_FECHAMENTO e os numeros medidos em
    TRACO_ESPALHAMENTO.

    Arriscado mudar: TRACO_SOBRE_PAPEL (baixar deixa a textura das areas
    escuras de uma foto contar como traco) e TRACO_FECHAMENTO (pequeno demais
    deixa de apagar o traco grosso; grande demais passa a contar as sombras
    da pintura como traco).
    """
    # luz <= (1 - TRACO_CONTRASTE) * fundo, e fundo claro; em 8 bits, que e a
    # conta que roda em toda a gravura
    limite = cv2.convertScaleAbs(fundo, alpha=1.0 - TRACO_CONTRASTE)
    escuro = cv2.compare(luz, limite, cv2.CMP_LE)
    _t, claro = cv2.threshold(fundo, TRACO_SOBRE_PAPEL * nivel - 1e-3, 255, cv2.THRESH_BINARY)
    traco = cv2.bitwise_and(escuro, claro)
    escala = _escala_dos_mapas(luz.shape)
    densidade = _desfocar(_reduzir(traco, escala) / 255.0, luz.shape, escala,
                          TRACO_ESPALHAMENTO)
    peso = np.clip((densidade - TRACO_DENSIDADE_MIN)
                   / (TRACO_DENSIDADE_MAX - TRACO_DENSIDADE_MIN), 0.0, 1.0)
    return _voltar((peso * 255.0 + 0.5).astype(np.uint8), luz.shape)


def _rampa_8_bits(inicio: float, fim: float, divisor: float) -> np.ndarray:
    """Tabela de 256 valores: 0 ate inicio, 255 a partir de fim (em v/divisor)."""
    v = np.arange(256, dtype=np.float32) / max(divisor, 1.0)
    return (np.clip((v - inicio) / (fim - inicio), 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def _no_nivel_do_papel(luz: np.ndarray, fundo: np.ndarray, nivel: float) -> np.ndarray:
    """0 a 255: quanto cada ponto e o proprio papel, e nao traco nem orla.

    255 onde o ponto esta no nivel do fundo em volta e esse fundo e claro; 0 no
    traco (mesmo o fraco, que fica abaixo do fundo) e na mancha larga de tinta
    (onde o fundo e escuro). Ver PAPEL_NO_FUNDO_MIN e FUNDO_CLARO_MIN. Em 8 bits,
    com tabelas: e a conta que roda em toda a gravura.
    """
    razao = cv2.divide(luz, fundo, scale=255)   # luz / fundo, 0 a 255
    no_fundo = cv2.LUT(razao, _rampa_8_bits(PAPEL_NO_FUNDO_MIN, PAPEL_NO_FUNDO_MAX, 255.0))
    claro = cv2.LUT(fundo, _rampa_8_bits(FUNDO_CLARO_MIN, FUNDO_CLARO_MAX, nivel))
    return cv2.multiply(no_fundo, claro, scale=1.0 / 255.0)


def _cor_parecida_com_o_papel(lab: np.ndarray, papel_certo: np.ndarray) -> np.ndarray | None:
    """0 a 255: quanto a cor de cada ponto e a do papel desta gravura.

    A referencia e o papel_certo (papel entre os tracos), medido na propria
    gravura: e a pista "cor igual a do papel da propria pagina", mas com o papel
    DELA, porque o papel de dentro de um retrato escurece e amarela mais que o
    da margem. A comparacao e so na cor (a e b do LAB), nao na luz: papel
    escurecido continua papel. A cor vem alisada (COR_DO_PAPEL_ALISAMENTO), e a
    decisao sai em rampa - as duas coisas juntas impedem os quadrados do JPEG.
    Calculada na copia reduzida: e lisa de qualquer jeito.

    None quando nao ha papel certo que chegue para medir.
    """
    forma = lab.shape
    escala = _escala_dos_mapas(forma)
    pequeno = _desfocar(_reduzir(lab, escala), forma, escala, COR_DO_PAPEL_ALISAMENTO)
    a = pequeno[:, :, 1] - 128.0
    b = pequeno[:, :, 2] - 128.0
    certo = _reduzir(np.multiply(papel_certo, 255, dtype=np.uint8), escala) >= 128.0
    if int(certo.sum()) < 10:
        return None
    a_papel = float(np.median(a[certo]))
    b_papel = float(np.median(b[certo]))
    distancia = np.hypot(a - a_papel, b - b_papel)
    raio = max(COR_DO_PAPEL_RAIO_MIN,
               _percentil(distancia[certo], COR_DO_PAPEL_PERCENTIL))
    cheio, zero = raio * COR_DO_PAPEL_CHEIO, raio * COR_DO_PAPEL_ZERO
    cor = np.clip((zero - distancia) / (zero - cheio), 0.0, 1.0)
    return _voltar((cor * 255.0 + 0.5).astype(np.uint8), forma)


def _so_o_papel_da_gravura(original: np.ndarray, saida: np.ndarray) -> np.ndarray:
    """Dentro de uma gravura, vai a branco o papel e so o papel.

    Chamada por _limpar_o_papel_de_verdade depois das travas dela (capa, tinta
    de menos ou de mais, poucas pecas de letra). A decisao passa por quatro
    perguntas, uma para cada pista:

    1. A gravura e de TRACO? (_peso_de_traco: textura). Se o traco cobre menos
       que GRAVURA_DE_TRACO_MINIMA dela, e pintura ou foto: nada vai a branco
       por aqui, e o tom fica como o Melhorar deixou (a curva de ombro ja leva
       o papel dela a branco). E o que devolve a roupa do anjo, o ceu e a
       estatua.
    2. O ponto esta no NIVEL DO PAPEL em volta? (_no_nivel_do_papel). O traco,
       ate o fraco da hachura, fica abaixo dele e nao e tocado.
    3. A cor e a do papel DESTA gravura? (_cor_parecida_com_o_papel). Protege a
       moldura dourada, a iluminura e a cor pintada a mao numa xilogravura.
    4. Esta LIGADO ao papel entre os tracos? (tamanho e ligacao). O papel certo
       - onde ha traco em volta - e a semente; vai a branco o que passa em 2 e 3
       e se liga a ela sem atravessar traco. Assim o rosto liso de um retrato,
       longe da hachura, vai junto; uma area da mesma cor que nao encosta no
       papel de traco, nao.

    O branco entra em rampa (pelo nivel e pela cor) e e decidido ponto a ponto,
    nunca por bloco.

    Arriscado mudar: tirar a pergunta 1 traz de volta o bug do anjo; trocar a 2
    pela pergunta da pagina de texto ("longe de letra") parte a hachura do
    Palatino 5; tirar a 3 apaga a moldura dourada das Horas 13; tirar a 4 deixa
    o rosto do retrato creme.
    """
    if original.ndim != 3 or saida.ndim != 3:
        return saida
    lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB)
    luz, fundo, nivel = _fundo_e_nivel(lab)
    traco_certo = _peso_de_traco(luz, fundo, nivel) >= 128
    if float(traco_certo.mean()) < GRAVURA_DE_TRACO_MINIMA:
        return saida

    no_papel = _no_nivel_do_papel(luz, fundo, nivel)
    # o papel certo, de onde se mede a cor: no nivel do fundo, com traco em
    # volta e nao escuro demais (a rede de seguranca ESCURO_DEMAIS_PARA_SER_MANCHA
    # da limpeza da pagina)
    papel_certo = traco_certo & (no_papel == 255) & (
        luz >= nivel * ESCURO_DEMAIS_PARA_SER_MANCHA)
    if int(papel_certo.sum()) < 100:
        return saida

    cor = _cor_parecida_com_o_papel(lab, papel_certo)
    if cor is None:
        return saida
    peso = cv2.multiply(no_papel, cor, scale=1.0 / 255.0)
    semente = papel_certo & (cor == 255)

    _n, rotulos = cv2.connectedComponents((peso > 0).astype(np.uint8), connectivity=8)
    ligados = np.zeros(int(rotulos.max()) + 1, np.uint8)
    # a semente vista de 2 em 2 pontos: basta um ponto dela para ligar a regiao
    # inteira, e a conta cai a um quarto
    ligados[rotulos[::2, ::2][semente[::2, ::2]]] = 255
    ligados[0] = 0
    peso = cv2.bitwise_and(peso, ligados[rotulos])
    if not peso.any():
        return saida

    # saida + (255 - saida) * peso, em 8 bits
    return cv2.add(saida, cv2.multiply(cv2.bitwise_not(saida), cv2.merge([peso, peso, peso]),
                                       scale=1.0 / 255.0))


def filtro_magico_pro(img: np.ndarray, intensidade: int = AJUSTE_PADRAO) -> np.ndarray:
    """Mágico pro: cor viva, texto nítido, fundo branco. Para capas e gravuras.

    intensidade move os tres realces de uma vez - saturação, contraste local e
    nitidez. Um controle só, porque mexer nos tres separado nao faz sentido
    para quem nao e da area.
    """
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 1. mesma limpeza de iluminacao do Melhorar
    saida = _achatar_iluminacao(img, _nivel_do_papel(img))
    saida = _balanco_de_branco(saida)

    # 2. contraste local so onde ha conteudo; o papel fica como estava. Em folha
    # em branco nao ha conteudo nenhum, e realcar so amplifica grao.
    if not _quase_sem_tinta(img):
        saida = _contraste_local_no_conteudo(saida, intensidade)

    # 3. cor mais viva - onde houver cor que nao seja a do proprio papel.
    # Numa folha velha sem tinta a unica cor e o amarelado, e avivar aquilo e o
    # oposto do pedido: a folha vazia do Boecio saia de um creme palido para um
    # amarelo forte. Numa capa colorida, que tambem nao tem tinta, a cor E o
    # conteudo e o realce tem de valer. Ver _so_o_amarelado_do_papel.
    if not _so_o_amarelado_do_papel(img):
        saida = _realcar_saturacao(saida, _entre(intensidade, SATURACAO_MIN, SATURACAO_MAX))

    # 4. texto mais nitido
    saida = _nitidez(saida, _entre(intensidade, NITIDEZ_MIN, NITIDEZ_MAX))

    # 5. fundo branco de verdade, e sem o grao que as curvas amplificaram
    saida = _alisar_o_papel(saida)
    saida = _empurrar_branco(saida)

    # 6. e a borda da letra de volta ao que era, agora entre um preto mais fundo
    # e um papel mais claro
    saida = _recompor_a_rampa(img, saida)

    # 7. o que sobrou de creme e de mancha do verso sai agora, perguntando ao
    # Sauvola o que e tinta de verdade. O limiar fixo do passo 5 nao alcanca
    # papel amarelado - ver _limpar_o_papel_de_verdade.
    return _limpar_o_papel_de_verdade(img, saida)


# Area minima de uma gravura para valer a pena limpa-la pelo nivel dela, em
# fracao da pagina. Abaixo disso e respingo, e o recorte nem teria papel dentro
# para medir.
AREA_MINIMA_DE_GRAVURA = 0.002

# Ate que tamanho a gravura conta como "pequena" para _limpar_cada_gravura, em
# fracao da folha: a caixa em volta de onde o peso dela passa de zero. Ver o
# comentario "Gravura pequena" dentro da funcao.
#
# Historia (29/09/2026, regra 6 do plano): o Preto e branco ficou 8% mais lento
# no teste de velocidade. O detector passou a marcar como gravura o titulo
# corrido "de Maria." do Marial 153 (0,4% da folha), e qualquer gravura, por
# menor que fosse, fazia rodar o Melhorar na FOLHA INTEIRA - quase 3 segundos a
# 300 DPI - so para usar o resultado numa borda de uns 15 pontos em volta dela.
#
# Tentado primeiro (decisao da gerente): rodar esse Melhorar so numa area em
# volta da gravura. Ficou rapido, mas numa area pequena a limpeza do papel nao
# reconhece mais "pagina de texto" (75 letras no Marial 153, e ela pede 200) e o
# papel da borda parava em 220 a 229 em vez de 255: um halo cinza em volta da
# caixa, visivel, em 11 a 28 mil pontos por pagina. Descartado.
#
# Seguro mudar: o numero (mais alto poe mais paginas no caminho rapido e muda
# mais bordas; medido nas 32 do gabarito, com 0,25 as 5 paginas em destaque do
# Samuel ficam de fora, identicas).
GRAVURA_PEQUENA_ATE = 0.25


def _gravura_pequena_sem_pedacinhos(gravura: np.ndarray, onde_vale: np.ndarray) -> bool:
    """True quando o caminho rapido de _limpar_cada_gravura vale: a caixa em
    volta de onde o peso passa de zero cabe em GRAVURA_PEQUENA_ATE da folha, e
    nenhum pedaco de gravura e menor que AREA_MINIMA_DE_GRAVURA (pedacinho nao
    tem recorte proprio e depende do Melhorar da folha inteira)."""
    x, y, largura, altura = cv2.boundingRect(onde_vale.astype(np.uint8))
    if largura * altura == 0 or largura * altura > GRAVURA_PEQUENA_ATE * onde_vale.size:
        return False
    num, _, stats, _ = cv2.connectedComponentsWithStats(
        (gravura > 0).astype(np.uint8), connectivity=8)
    minimo = AREA_MINIMA_DE_GRAVURA * gravura.size
    return bool(num > 1 and (stats[1:, cv2.CC_STAT_AREA] >= minimo).all())


def _limpar_cada_gravura(img: np.ndarray, gravura: np.ndarray,
                         clareza: int = AJUSTE_PADRAO,
                         onde_vale: np.ndarray | None = None,
                         fundo: np.ndarray | None = None) -> np.ndarray:
    """Limpa cada gravura ancorada no papel DELA, e nao no da folha.

    Sem isso o papel dentro do desenho nao chega a branco: medido na xilogravura
    da Rhetorica, ele parava em 214 numa escala em que 255 e branco, enquanto a
    margem da folha, essa sim, ia a 255. O papel dentro de um bloco gravado e
    mais escuro que a margem, e a curva de ombro calculada pela folha inteira
    nao alcanca ele.

    Uma iluminura de meio-tom, que quase nao tem papel a vista, passa por aqui
    sem mudanca: _balanco_de_branco desiste sozinho quando nao acha papel.

    Cada recorte vai com dentro_da_gravura=True: a limpeza final do papel so
    branqueia o papel de verdade (o fundo do retrato do Palatino 5), nunca a
    pintura clara (a roupa do anjo) nem a foto (a estatua do Opus 20). Era o
    bug dos quadradinhos de 28/09/2026 - ver _so_o_papel_da_gravura. Arriscado
    mudar: tirar isso traz os quadradinhos de volta nos tres filtros (Magico
    pro e Melhorar passam por aqui; no Preto e branco, desde 30/09/2026, so a
    foto ou pintura de tom continuo - ver _preto_e_branco_com_gravura).

    onde_vale e fundo (os dois juntos, ou nenhum): onde o resultado desta funcao
    vai entrar na pagina (o peso da gravura maior que zero) e o resultado do
    filtro da pagina sem a gravura (o "base" de aplicar_filtro_com_selecao).
    Servem ao caminho rapido da gravura pequena, abaixo. Sem eles, a folha
    inteira, como sempre.
    """
    img3 = _tres_canais(img)

    # Gravura pequena (29/09/2026, ver GRAVURA_PEQUENA_ATE): fora dos recortes o
    # resultado desta funcao so entra na borda suave, misturado com o filtro da
    # pagina pelo peso. Ali vai o PROPRIO filtro da pagina (fundo), e nao um
    # Melhorar da folha inteira: a borda fica igual a pagina em volta, e a conta
    # mais cara desta funcao some. No filtro Melhorar o resultado e identico
    # ponto a ponto (o fundo ja e o Melhorar da folha). No Magico pro e no Preto
    # e branco, muda so a letra que cai na borda suave: sai com o tratamento da
    # pagina (no Preto e branco, preto e branco) em vez de meio a meio com o
    # Melhorar.
    # Arriscado mudar: o fundo tem de ser o filtro da pagina de verdade - fundo
    # errado aparece como moldura em volta de toda gravura pequena; e so vale sem
    # pedacinhos (ver _gravura_pequena_sem_pedacinhos): pedacinho de gravura
    # usaria o fundo e sairia binarizado no Preto e branco.
    if (onde_vale is not None and fundo is not None
            and _gravura_pequena_sem_pedacinhos(gravura, onde_vale)):
        saida = _tres_canais(fundo).copy()
    else:
        saida = filtro_melhorar(img3, clareza=clareza)

    num, _, stats, _ = cv2.connectedComponentsWithStats(
        (gravura > 0).astype(np.uint8), connectivity=8)
    minimo = AREA_MINIMA_DE_GRAVURA * gravura.size
    for i in range(1, num):
        if stats[i, cv2.CC_STAT_AREA] < minimo:
            continue
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        pedaco = img3[y:y + h, x:x + w]
        if pedaco.size:
            saida[y:y + h, x:x + w] = filtro_melhorar(pedaco, clareza=clareza,
                                                      dentro_da_gravura=True)
    return saida


# --- Preto e branco: a gravura vira desenho (regra do Samuel, 30/09/2026) ----
#
# "No Preto e branco, tudo sai em preto e branco, inclusive moldura dourada,
# titulo colorido e iluminura. A moldura nao deve sair dourada (como no
# detector antigo) nem preta chapada (como no novo): deve sair como desenho em
# preto e branco, com os tracos e detalhes em preto e o fundo da faixa em
# branco, sem perder o desenho. O titulo 'NOVEMBRE.' da Horas 26 sai preto no
# Preto e branco. Nos outros filtros (Magico pro, Melhorar, Original), sai com
# a cor original."
#
# Por que nao o Sauvola da pagina dentro da gravura: ele compara cada ponto com
# a vizinhanca, e uma faixa dourada mais estreita que a janela dele e mais
# escura que o papel em volta - sai inteira preta (a moldura preta da Horas 13,
# print v04 do verificador). Numa iluminura, tudo o que e mais escuro que o
# papel vira um borrao preto (Horas 11 no detector antigo).
#
# O desenho usa o "fundo" de cada ponto pelo FECHAMENTO morfologico (a mesma
# operacao consagrada de _peso_de_traco: o fechamento apaga o que e mais fino
# que o elemento e deixa o fundo). Preto e o que fica bem mais escuro que o
# fundo em volta: traco, contorno, detalhe, letra. Uma area pintada mais larga
# que o elemento (a faixa dourada, o verde de fundo de uma iluminura) e fundo
# dela mesma e sai branca. E a normalizacao pelo fundo seguida de um limiar
# fixo, como o top-hat preto; nao e fotografia de nada, so decide preto ou
# branco ponto a ponto a partir do proprio original.
#
# Medido nas paginas-gabarito (saida_teste/pb_30_09, prototipos v2 a v8):
# elemento 1/200 da pagina deixava oco o titulo "NOVEMBRE."; 1/120 deixa a
# letra cheia e ainda cabe dentro das faixas das molduras (39 a 44 pontos de
# largura mediana nas Horas 13, 26 e 27, contra 27 a 35 do elemento). Contraste
# 0,15 enchia a faixa da Horas 13 de pontinhos; 0,30 apagava a hachura do
# retrato do Palatino 5; 0,20 fica no meio. O canal verde no lugar do brilho
# nao mudou nada a vista; os tres canais juntos enchiam a faixa de ruido.
DESENHO_FECHAMENTO = 1 / 120        # elemento, em fracao do menor lado da PAGINA
DESENHO_CONTRASTE = 0.20            # preto se o ponto < (1 - isto) x fundo em volta

# A letra ou nota MAIS LARGA que o elemento ficaria oca (so o contorno): as
# notas quadradas do Graduale 222 saiam vazadas. Ela volta cheia quando e uma
# mancha escura (fundo abaixo de DESENHO_AREA_ESCURA do papel), pequena (maior
# lado abaixo de DESENHO_MANCHA_PEQUENA do menor lado da pagina) e SEM COR
# (croma media, em a e b do LAB, abaixo de DESENHO_CROMA_DE_TINTA): tinta.
# Medido: notas do Graduale 17 de croma; faixa dourada da Horas 13 de 29 para
# cima. Arriscado tirar a trava da cor: pedacos da moldura dourada viravam
# blocos pretos (prototipo v6). Arriscado trocar o "pequena" por "lisa": a
# hachura fechada do retrato do Palatino 5 virava manchas pretas.
DESENHO_AREA_ESCURA = 0.80
DESENHO_MANCHA_PEQUENA = 1 / 12
DESENHO_CROMA_DE_TINTA = 22.0

# Foto e pintura de tom continuo (a estatua do Opus Majus 20, o anjo da Escola
# 35): no Preto e branco saem em TONS DE CINZA (decisao do Samuel, conferencia
# 2 de 30/09, cartao P1a "Cinza (tons de cinza): BOM"; os tres pontilhados,
# RUIM) - ver _foto_em_tons_de_cinza. E foto quem tem pouco
# traco (_peso_de_traco abaixo de GRAVURA_DE_TRACO_MINIMA, a mesma medida do
# Magico pro) E e "grossa": cabe dentro dela um circulo de FOTO_ESPESSURA_MINIMA
# do menor lado da pagina. A espessura e o que separa uma foto de um pedaco
# fino de moldura, que tambem quase nao tem traco no recorte dele. Medido
# (espessura / menor lado): fotos e pinturas 34% a 65%; pedacos de moldura das
# Horas 0,7% a 4%; pedacos de pauta do Graduale 4,5%; iluminura da Horas 11
# 89%, mas com 22% de traco (sai desenho, como pede a regra).
FOTO_ESPESSURA_MINIMA = 0.12

# A foto em tons de cinza (decisao P1 do Samuel, 30/09/2026) e feita como no
# exemplo que ele aprovou (relatorios/conferir/fotos-no-preto-e-branco-2026-
# 09-30, versao "3-tons-de-cinza", script saida_teste/pb_30_09/fotos_exemplo.py):
#   1. o cinza do ORIGINAL - nao o do Melhorar, que levava a estatua do Opus 20
#      (da cor do papel, so 14 tons mais escura) quase a branco;
#   2. um desfoque gaussiano leve (FOTO_DESFOQUE pontos), que tira a reticula
#      da impressao antiga (o "descreen" consagrado; sem ele os pontinhos da
#      reticula aparecem como chuvisco);
#   3. os niveis esticados em linha reta pela pagina inteira: o FOTO_PRETO% mais
#      escuro vira preto e o FOTO_BRANCO% mais claro vira branco.
# Uma mudanca sobre o exemplo: o branco nunca fica acima do nivel do PAPEL da
# pagina (o percentil BRANCO_PERCENTIL do cinza fora das gravuras). O Samuel
# pediu "papel em volta branco": no Marial 7 o detector marca como foto um
# canto de papel, e a pagina tem pontos brancos puros (o preenchimento do
# corte), entao o percentil 99,5 dava 255 e o papel desse canto ficava cinza
# 214. Nas fotos de verdade quase nao muda (Opus 20: 215 -> 210; Escola 35:
# 255 -> 252).
# Seguro mudar: os numeros, olhando o Opus 20 e a Escola 35. Arriscado: trocar
# o original pelo Melhorar (a estatua some) ou tirar o desfoque (chuvisco).
FOTO_DESFOQUE = 1.0
FOTO_PRETO, FOTO_BRANCO = 0.5, 99.5


def _niveis_da_foto(img3: np.ndarray, gravura: np.ndarray | None = None) -> tuple[float, float]:
    """(preto, branco) do esticao da foto em cinza: os percentis FOTO_PRETO e
    FOTO_BRANCO do cinza da PAGINA inteira (como no exemplo aprovado), com o
    branco limitado ao nivel do papel fora das gravuras (gravura: mascara
    booleana; None = sem esse limite). Ver FOTO_DESFOQUE."""
    cinza = _para_cinza(img3)
    preto, branco = _percentil(cinza, FOTO_PRETO), _percentil(cinza, FOTO_BRANCO)
    if gravura is not None:
        fora = cinza[::2, ::2][~gravura[::2, ::2]]
        if fora.size >= 0.05 * cinza[::2, ::2].size:
            branco = min(branco, _percentil(fora, BRANCO_PERCENTIL))
    return preto, max(branco, preto + 1.0)


def _foto_em_tons_de_cinza(recorte: np.ndarray, niveis: tuple[float, float]) -> np.ndarray:
    """A foto (ou pintura) em tons de cinza, 1 canal: cinza do original, com o
    desfoque que tira a reticula e os niveis esticados (ver FOTO_DESFOQUE).
    recorte: BGR do pedaco da pagina; niveis: _niveis_da_foto da pagina."""
    cinza = cv2.GaussianBlur(_para_cinza(recorte), (0, 0), FOTO_DESFOQUE)
    preto, branco = niveis
    escala = np.arange(256, dtype=np.float32)
    tabela = np.clip((escala - preto) * 255.0 / max(1.0, branco - preto), 0, 255)
    return cv2.LUT(cinza, tabela.astype(np.uint8))


def _e_foto_ou_pintura(img3: np.ndarray, zona: np.ndarray, caixa: tuple[int, int, int, int],
                       menor_lado: int) -> bool:
    """Esta zona de gravura e foto/pintura de tom continuo (fica como esta)?

    zona: mascara booleana da zona, do tamanho da caixa (x, y, largura,
    altura) na pagina. Ver FOTO_ESPESSURA_MINIMA. A espessura vem primeiro
    porque e barata: zona fina (moldura, titulo) nem chega a medir o traco.
    Arriscado mudar: e esta resposta que decide se a zona sai em cor ou em
    preto e branco.
    """
    distancia = cv2.distanceTransform(
        np.pad(zona.astype(np.uint8), 1), cv2.DIST_L2, 5)
    if 2.0 * float(distancia.max()) < FOTO_ESPESSURA_MINIMA * menor_lado:
        return False
    x, y, largura, altura = caixa
    lab = cv2.cvtColor(img3[y:y + altura, x:x + largura], cv2.COLOR_BGR2LAB)
    luz, fundo, nivel = _fundo_e_nivel(lab)
    traco = _peso_de_traco(luz, fundo, nivel) >= 128
    return float(traco.mean()) < GRAVURA_DE_TRACO_MINIMA


# Opus Majus 20 no Preto e branco, contorno "livre" (conferencia 5 do Samuel,
# F1/A3): "nao gostei de como ficou esbranquicada, nao da mais para ver o rosto
# direito da imagem" ("'Este livro tem fotos' e a melhor escolha ate agora").
# O contorno livre do ScanTailor deixa de fora da foto o rosto e o lado da
# estatua (claros, da cor do papel); ali o detector marca PAPEL, que vai a
# branco. A foto (_e_foto_ou_pintura) que cobre pelo menos FOTO_CAIXA_CHEIA do
# seu FECHO CONVEXO (o menor poligono convexo em volta dela) vale o fecho
# inteiro: o buraco e a reentrancia dentro da foto voltam a ser foto, e o papel
# marcado ali nao vai a branco. O fecho, e nao a caixa: a caixa levava junto a
# margem de papel em volta do anjo da Escola 35 (a zona tem borda suave), que
# ficava cinza. Medido: a zona do Opus 20 enche 81% do fecho (o rosto e o
# lado da estatua voltam); o anjo da Escola 35, 100% (nada muda). Arriscado:
# baixar muito (uma foto recortada em L levaria junto o texto do canto vazio,
# que sairia em tons de cinza).
FOTO_CAIXA_CHEIA = 0.75
# Abaixo disto (fracao do fecho que falta na zona) a foto ja esta inteira.
# Medido: anjo da Escola 35, 0%; Opus 20, 19%.
FOTO_FALTA_MINIMA = 0.03


def _fechos_de_foto(rotulos: np.ndarray, foto: np.ndarray,
                    peso_gravura: np.ndarray) -> np.ndarray | None:
    """A mascara (uint8, 255) dos fechos convexos das zonas de foto que enchem
    o fecho delas (FOTO_CAIXA_CHEIA), ou None. rotulos e foto: os de
    _tipos_das_zonas; a zona conta onde o peso passa de 0,5 (sem a borda
    suave)."""
    fechos = None
    for i in np.flatnonzero(foto):
        zona = ((rotulos == i) & (peso_gravura > 0.5)).astype(np.uint8)
        contornos, _h = cv2.findContours(zona, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contornos:
            continue
        fecho = cv2.convexHull(np.vstack(contornos))
        area = cv2.contourArea(fecho)
        cheia = cv2.countNonZero(zona)
        # o fecho tem de encher a foto (FOTO_CAIXA_CHEIA) e faltar alguma
        # coisa de verdade (FOTO_FALTA_MINIMA): a foto inteira (o anjo da
        # Escola 35) fica como estava, borda suave e tudo
        if area <= 0 or not FOTO_FALTA_MINIMA * area <= area - cheia <= (1 - FOTO_CAIXA_CHEIA) * area:
            continue
        if fechos is None:
            fechos = np.zeros(zona.shape, np.uint8)
        cv2.fillConvexPoly(fechos, fecho, 255)
    return fechos


# Opus Majus 20 no Magico pro, contorno "livre" (conferencia 6 do Samuel, X2,
# 02/10/2026): "nao sei porque, agora ficou muito ruim, nao consigo ver o rosto
# mais, esses pontos estao horriveis atras da estatua." O contorno livre do
# ScanTailor deixa de fora da foto o rosto e o lado da estatua (claros, da cor
# do papel: o detector marca PAPEL, que vai a branco) e o vao escuro da porta
# atras dela (o detector marca LETRA, porque e tinta: o traco vira a reticula
# da foto em pontinhos pretos, e o papel entre eles vai a branco). No AGORA da
# conferencia 6 apareceu ainda um retangulo branco no vao: a emenda das barras
# da moldura (commit 358d27e, conferencia 5) passou a ligar a gravura do lado
# direito do vao, e o pedaco que sobrou entre ela e a letra virou PAPEL.
# O mesmo conserto do Preto e branco (_fechos_de_foto, conferencia 5, F1): a
# foto (_e_foto_ou_pintura) que enche o FECHO CONVEXO dela (FOTO_CAIXA_CHEIA)
# vale o fecho inteiro, aqui no Magico pro e no Melhorar - dentro dele e
# gravura (peso 1), sem papel nem letra: sai como a foto com "Este livro tem
# fotos". A forma de fabrica ("livre") e a marcacao guardada nao mudam; so o
# filtro le a foto inteira.
# Regra 6: a pergunta cara (_e_foto_ou_pintura) so e feita na zona larga o
# bastante para ser foto (a caixa passa de FOTO_ESPESSURA_MINIMA do menor lado)
# e que enche o fecho dela - a pagina de texto com titulo marcado (o Marial)
# nem chega a ela.
# Arriscado: o mesmo de FOTO_CAIXA_CHEIA (baixar muito leva junto o texto do
# canto vazio de uma foto em L).


def _a_foto_inteira(img3: np.ndarray, peso_gravura: np.ndarray, peso_letra: np.ndarray,
                    peso_papel: np.ndarray, decoracao: np.ndarray | None = None
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """(peso_gravura, peso_letra, peso_papel) com o fecho de cada foto do
    contorno livre dentro da gravura - ver o comentario acima -, ou None
    quando nao ha foto assim (nada muda).

    decoracao: a resposta de _tipos_das_zonas(so_a_decoracao=True) para estes
    mesmos pesos (os rotulos sao os mesmos: o mesmo connectedComponents), ou
    None. A zona de decoracao colorida nao e foto e nem e perguntada (regra 6:
    a pergunta da foto custava ~0,5 s na iluminura da Horas 11)."""
    if decoracao is not None and decoracao.size > 1 and decoracao[1:].all():
        return None
    altura, largura = img3.shape[:2]
    menor_lado = min(altura, largura)
    minimo = FOTO_ESPESSURA_MINIMA * menor_lado
    area_minima = AREA_MINIMA_DE_GRAVURA * altura * largura
    # porta barata (regra 6): numa copia 4 vezes menor, alguma zona e larga,
    # grande e enche o fecho como uma foto do contorno livre? (o Marial, com
    # titulos e o canto de papel marcados, para aqui; a conta de verdade, em
    # tamanho cheio, vem depois so se passar)
    peso_p = np.ascontiguousarray(peso_gravura[::4, ::4])
    pequena = (peso_p > 0).view(np.uint8)
    quantas_p, rotulos_p, medidas_p, _c = cv2.connectedComponentsWithStats(pequena, connectivity=8)
    talvez = False
    for i in range(1, quantas_p):
        x, y, w, h = (int(v) for v in medidas_p[i, :4])
        if min(w, h) < minimo / 4 - 1 or medidas_p[i, cv2.CC_STAT_AREA] * 16 < area_minima:
            continue
        zona = ((rotulos_p[y:y + h, x:x + w] == i) & (peso_p[y:y + h, x:x + w] > 0.5)
                ).astype(np.uint8)
        contornos, _h = cv2.findContours(zona, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = cv2.contourArea(cv2.convexHull(np.vstack(contornos))) if contornos else 0.0
        # com folga (a copia pequena arredonda a beirada)
        falta = area - cv2.countNonZero(zona)
        if area > 0 and (0.5 * FOTO_FALTA_MINIMA * area <= falta
                         <= 1.2 * (1 - FOTO_CAIXA_CHEIA) * area):
            talvez = True
            break
    if not talvez:
        return None
    onde = (peso_gravura > 0).astype(np.uint8)
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(onde, connectivity=8)
    fechos = None
    for i in range(1, quantas):
        if decoracao is not None and i < decoracao.size and decoracao[i]:
            continue
        x, y, w, h = (int(v) for v in medidas[i, :4])
        if min(w, h) < minimo or medidas[i, cv2.CC_STAT_AREA] < area_minima:
            continue
        zona = ((rotulos[y:y + h, x:x + w] == i) & (peso_gravura[y:y + h, x:x + w] > 0.5))
        contornos, _h = cv2.findContours(zona.astype(np.uint8), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)
        if not contornos:
            continue
        fecho = cv2.convexHull(np.vstack(contornos))
        area = cv2.contourArea(fecho)
        falta = area - cv2.countNonZero(zona.view(np.uint8))
        # as mesmas condicoes de _fechos_de_foto: enche o fecho e falta algo
        if area <= 0 or not FOTO_FALTA_MINIMA * area <= falta <= (1 - FOTO_CAIXA_CHEIA) * area:
            continue
        if not _e_foto_ou_pintura(img3, rotulos[y:y + h, x:x + w] == i, (x, y, w, h), menor_lado):
            continue
        if fechos is None:
            fechos = np.zeros((altura, largura), np.uint8)
        cv2.fillConvexPoly(fechos, fecho + np.array([x, y], np.int32), 255)
    if fechos is None:
        return None
    dentro = fechos > 0
    return (np.where(dentro, 1.0, peso_gravura).astype(np.float32),
            np.where(dentro, 0.0, peso_letra).astype(np.float32),
            np.where(dentro, 0.0, peso_papel).astype(np.float32))


def _desenho_em_preto_e_branco(img3: np.ndarray, nivel_papel: float,
                               menor_lado: int) -> np.ndarray:
    """A gravura como desenho de 1 bit: 0 no traco e no detalhe, 255 no resto.

    img3 e o recorte (BGR) com uma folga em volta; nivel_papel e menor_lado
    sao os da PAGINA inteira, para o desenho sair igual em qualquer recorte.
    Ver o comentario de DESENHO_FECHAMENTO e de DESENHO_AREA_ESCURA.
    """
    cinza = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
    lado = max(5, int(menor_lado * DESENHO_FECHAMENTO) | 1)
    fundo = cv2.morphologyEx(
        cinza, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
    # cinza < (1 - contraste) x fundo, em 8 bits
    limite = cv2.convertScaleAbs(fundo, alpha=1.0 - DESENHO_CONTRASTE)
    preto = cv2.compare(cinza, limite, cv2.CMP_LT) > 0

    # a letra e a nota mais largas que o elemento: de volta cheias (tinta)
    _t, escura = cv2.threshold(fundo, DESENHO_AREA_ESCURA * nivel_papel, 255,
                               cv2.THRESH_BINARY_INV)
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(escura, connectivity=8)
    if quantas > 1:
        pequenas = np.zeros(quantas, bool)
        pequenas[1:] = (np.maximum(medidas[1:, cv2.CC_STAT_WIDTH], medidas[1:, cv2.CC_STAT_HEIGHT])
                        < DESENHO_MANCHA_PEQUENA * menor_lado)
        if pequenas.any():
            # a cor media so das manchas pequenas (contar a pagina toda custava
            # o dobro)
            nas_pequenas = pequenas[rotulos]
            lab = cv2.cvtColor(img3, cv2.COLOR_BGR2LAB)
            a_ = lab[:, :, 1][nas_pequenas].astype(np.float32) - 128.0
            b_ = lab[:, :, 2][nas_pequenas].astype(np.float32) - 128.0
            media = (np.bincount(rotulos[nas_pequenas], weights=np.hypot(a_, b_),
                                 minlength=quantas)
                     / np.maximum(medidas[:, cv2.CC_STAT_AREA], 1))
            tinta = pequenas & (media < DESENHO_CROMA_DE_TINTA)
            if tinta.any():
                preto |= tinta[rotulos]
    saida = np.full(cinza.shape, 255, np.uint8)
    saida[preto] = 0
    return saida


# --- decoracao colorida: moldura dourada e iluminura com a cor original ------
#
# Emenda do Samuel a regra do Preto e branco (conferencia 3, 30/09/2026, cartao
# N2): "Mantem a cor original (como o ANTES); traco preto so se eu escolher". A
# gerente estendeu a decisao a iluminura colorida (a Horas 11: "perde um monte
# de detalhes" no Preto e branco). E a regra da Fase 1 para os outros filtros:
# "moldura dourada ... mantida sem mudar a cor"; "iluminura sai intacta ... so
# o papel em volta do texto que fica dentro dela e branqueado".
#
# O que e decoracao colorida: zona de gravura que nao e foto e tem AREAS
# coloridas largas - a faixa dourada (39 a 44 pontos de largura nas Horas 13,
# 26 e 27), o fundo verde e o ouro de uma iluminura. A medida: o ponto e
# colorido quando a cor dele (a e b do LAB) fica a mais de DECORACAO_CROMA do
# papel da pagina; "largo" e o que sobra de colorido depois de uma ABERTURA
# morfologica com o mesmo elemento do desenho (DESENHO_FECHAMENTO): a letra
# colorida fina (o titulo vermelho, a pauta) nao sobra, a faixa dourada sobra.
# A zona e decoracao quando o colorido largo cobre DECORACAO_MINIMA dela.
# Medido (30/09, despejo do programa): Horas 11 = 34%, Horas 13 = 45%, Horas
# 26 = 22%, Horas 27 = 54%, Horas 47 = 49%; retrato do Palatino 5 (traco sobre
# papel ambar) = 0,7%. A moldura e a iluminura nao sao separadas uma da outra:
# as duas sao "decoracao colorida" (a gerente autorizou tratar juntas).
#
# A decoracao sai com os pontos do ORIGINAL, sem curva nenhuma - so o papel
# vai a branco (_decoracao_com_a_cor_original). Era o Melhorar que rodava ali
# (no Preto e branco antes de decca4a, e no Magico pro): o esticao do preto
# escurecia o dourado ("a borda dourada ... saindo meio escurecida", Horas 13
# e 26), a curva de ombro lavava o ouro e o anjinho da Horas 11
# ("esbranquicando algumas partes"), e o papel dentro da zona, medido pela
# zona, parava em 233 a 244 (a faixa cinza da Horas 47).
DECORACAO_CROMA = 18.0
DECORACAO_MINIMA = 0.08
# A medida e feita numa copia reduzida a 1/DECORACAO_REDUCAO (so pergunta "tem
# area colorida larga?").
DECORACAO_REDUCAO = 4

# Qual ponto da decoracao e PAPEL (vai a branco): a cor perto da do papel da
# pagina (a mesma rampa de COR_DO_PAPEL_CHEIO a COR_DO_PAPEL_ZERO vezes o raio
# do papel) E a luz perto da do papel (de DECORACAO_LUZ_MIN a DECORACAO_LUZ_MAX
# do nivel dele, em rampa). A cor e alisada (DECORACAO_ALISAMENTO do menor
# lado), para a grade do JPEG nao virar quadradinho; bem menos que o
# COR_DO_PAPEL_ALISAMENTO da gravura de traco, porque o alisamento largo
# espalhava a cor da letra dourada no papel em volta e deixava um halo creme
# de uns 10 pontos em volta de cada letra (Horas 11, medido 1/150 contra
# 1/600). Arriscado: alisamento maior (halo), DECORACAO_LUZ_MIN mais baixo
# (clareia o ouro e a pele clara pintada), a cor fora da rampa (o dourado
# claro vai a branco).
DECORACAO_ALISAMENTO = 1 / 600
DECORACAO_LUZ_MIN, DECORACAO_LUZ_MAX = 0.80, 0.92
# E so vai a branco o papel ligado ao papel de fora da zona, ou o pedaco de
# papel com pelo menos esta fracao da folha (o centro da Horas 11, cercado
# pela iluminura, tem ~10%; o horizonte creme das paisagens da Horas 47, que
# tem cor e luz de papel mas e pintura, fica bem abaixo). Arriscado: baixar
# demais (o ceu palido vai a branco) ou tirar a ligacao.
DECORACAO_PAPEL_GRANDE = 0.01


def _referencia_do_papel(img3: np.ndarray, gravura: np.ndarray) -> tuple[float, float, float, float]:
    """(nivel da luz, a, b, raio) do papel da PAGINA, para a decoracao.

    Medido fora das gravuras (gravura: mascara booleana), quando sobra pagina
    que chegue (5%); senao, na pagina inteira. O nivel e o percentil
    BRANCO_PERCENTIL da luz (L do LAB); a e b sao a mediana da cor dos pontos
    no nivel do papel ou acima; o raio, o percentil COR_DO_PAPEL_PERCENTIL da
    distancia deles a essa mediana (no minimo COR_DO_PAPEL_RAIO_MIN). Feito de
    4 em 4 pontos: e uma medida da pagina, nao do ponto.
    """
    lab = cv2.cvtColor(np.ascontiguousarray(img3[::4, ::4]), cv2.COLOR_BGR2LAB)
    g = gravura[::4, ::4]
    usar = ~g if float((~g).mean()) >= 0.05 else np.ones(g.shape, bool)
    luz = lab[:, :, 0]
    nivel = _percentil(luz[usar], BRANCO_PERCENTIL)
    papel = usar & (luz >= nivel)
    a = lab[:, :, 1][papel].astype(np.float32) - 128.0
    b = lab[:, :, 2][papel].astype(np.float32) - 128.0
    if a.size == 0:
        return nivel, 0.0, 0.0, COR_DO_PAPEL_RAIO_MIN
    a_papel, b_papel = float(np.median(a)), float(np.median(b))
    raio = max(COR_DO_PAPEL_RAIO_MIN,
               float(np.percentile(np.hypot(a - a_papel, b - b_papel), COR_DO_PAPEL_PERCENTIL)))
    return nivel, a_papel, b_papel, raio


def _e_decoracao_colorida(img3: np.ndarray, zona: np.ndarray, caixa: tuple[int, int, int, int],
                          menor_lado: int, referencia: tuple[float, float, float, float]) -> bool:
    """Esta zona (que nao e foto) e decoracao colorida - moldura dourada ou
    iluminura? Ver DECORACAO_CROMA. zona: mascara booleana do tamanho da caixa
    (x, y, largura, altura). Arriscado mudar: e esta resposta que decide se a
    zona mantem a cor no Preto e branco e sai sem curva no Magico pro."""
    x, y, largura, altura = caixa
    fator = 1.0 / DECORACAO_REDUCAO
    tamanho = (max(1, round(largura * fator)), max(1, round(altura * fator)))
    pequeno = cv2.resize(img3[y:y + altura, x:x + largura], tamanho, interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(pequeno, cv2.COLOR_BGR2LAB).astype(np.float32)
    _nivel, a_papel, b_papel, _raio = referencia
    distancia = np.hypot(lab[:, :, 1] - 128.0 - a_papel, lab[:, :, 2] - 128.0 - b_papel)
    colorido = (distancia > DECORACAO_CROMA).astype(np.uint8)
    # o elemento do desenho na copia reduzida, arredondado (com int, numa
    # pagina pequena ele caia para 3 pontos e a letra vermelha de 7 pontos
    # sobrava como "larga")
    lado = max(3, int(round(menor_lado * DESENHO_FECHAMENTO * fator)) | 1)
    largo = cv2.morphologyEx(colorido, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
    dentro = cv2.resize(zona.astype(np.uint8), tamanho, interpolation=cv2.INTER_NEAREST) > 0
    if not dentro.any():
        return False
    return float(largo[dentro].mean()) >= DECORACAO_MINIMA


def _decoracao_com_a_cor_original(recorte: np.ndarray,
                                  referencia: tuple[float, float, float, float],
                                  fora: np.ndarray | None = None,
                                  area_grande: int = 0,
                                  letra_max: int = 0,
                                  letras_pretas: bool = False,
                                  altura_da_pagina: int = 0,
                                  lado_largo: int = 0) -> np.ndarray:
    """A decoracao com os pontos do original; so o papel vai a branco.

    letras_pretas (so o Preto e branco, com letra_max): a letra solta no papel
    da decoracao sai PRETA e cheia (decisao P4 do Samuel, conferencia 5:
    titulos dentro da iluminura ou da moldura "saem pretos, como o resto do
    texto"; M2, Horas 26: "as letras ainda estao saindo com alguns pedacos
    cinzas dentro delas"). Letra = o que nao e papel num pedaco solto
    (_pedacos_soltos; lado_largo: o da linha de letras presas por um fio),
    contado depois da beirada; a sujeira menor que a letra (o tamanho do
    _despeckle da pagina, pela altura_da_pagina) e a mancha clara
    (_so_a_tinta_forte) nao entram.

    letra_max (pontos; 0 = nao procurar): o papel dentro de uma letra solta
    no papel branco (o miolo do "O") tambem vai a branco - ver
    _miolos_das_letras e LETRA_NA_DECORACAO_MAX.

    recorte: BGR do pedaco da pagina. Papel e o ponto com a cor e a luz do
    papel da pagina (ver DECORACAO_ALISAMENTO); o branco entra em rampa,
    ponto a ponto, nunca por bloco: saida = original + (255 - original) x peso.
    O ouro, o verde, o azul, a pele pintada e o contorno ficam como no
    original - nem mais escuros, nem lavados.
    """
    nivel, a_papel, b_papel, raio = referencia
    lab = cv2.cvtColor(recorte, cv2.COLOR_BGR2LAB)
    forma = lab.shape
    escala = _escala_dos_mapas(forma)
    pequeno = _desfocar(_reduzir(lab, escala), forma, escala, DECORACAO_ALISAMENTO)
    distancia = np.hypot(pequeno[:, :, 1] - 128.0 - a_papel, pequeno[:, :, 2] - 128.0 - b_papel)
    cheio, zero = raio * COR_DO_PAPEL_CHEIO, raio * COR_DO_PAPEL_ZERO
    cor = np.clip((zero - distancia) / (zero - cheio), 0.0, 1.0)
    cor = _voltar((cor * 255.0 + 0.5).astype(np.uint8), forma)
    luz = cv2.LUT(np.ascontiguousarray(lab[:, :, 0]),
                  _rampa_8_bits(DECORACAO_LUZ_MIN, DECORACAO_LUZ_MAX, nivel))
    peso = cv2.multiply(cor, luz, scale=1.0 / 255.0)

    # So vai a branco o papel que esta LIGADO ao papel de fora da decoracao
    # (fora: mascara booleana dos pontos do recorte fora da zona), ou que e
    # grande (area_grande pontos): o centro claro da Horas 11, cercado pela
    # iluminura, tem ~10% da folha. Sem isso, o ceu palido e o horizonte creme
    # das paisagens pintadas da Horas 47 (cor e luz de papel, mas pintura)
    # iam a branco. Mesma ideia da pergunta 4 de _so_o_papel_da_gravura.
    if fora is not None or area_grande:
        quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(
            (peso > 0).astype(np.uint8), connectivity=8)
        if quantas > 1:
            ligados = np.zeros(quantas, np.uint8)
            if area_grande:
                ligados[medidas[:, cv2.CC_STAT_AREA] >= area_grande] = 255
            if fora is not None and fora.any():
                ligados[rotulos[fora]] = 255
            ligados[0] = 0
            ligado = cv2.bitwise_and(peso, ligados[rotulos])
            if letra_max:
                _miolos_das_letras(ligado, peso, letra_max)
            peso = ligado
            if letra_max:
                peso = _beirada_do_papel(peso, lab, (a_papel, b_papel), (cheio, zero), luz,
                                         faixa=max(2, int(np.ceil(1.5 / escala))))
            # a letra solta: contada depois da beirada, que solta do festao a
            # letra que so encostava nele pelo fio creme (o "H" de HEURES)
            tinta = (_pedacos_soltos(cv2.compare(peso, 128, cv2.CMP_LT), letra_max,
                                     lado_largo=lado_largo)
                     if letras_pretas and letra_max else None)
            if tinta is not None:
                saida = cv2.add(recorte, cv2.multiply(cv2.bitwise_not(recorte),
                                                      cv2.merge([peso, peso, peso]),
                                                      scale=1.0 / 255.0))
                # a tinta da letra (o que nao vai a branco), menos a sujeira
                # miuda e a mancha clara
                # (so na caixa das letras: a folha inteira custava o dobro)
                bx, by, bw, bh = cv2.boundingRect(tinta)
                caixa = (slice(by, by + bh), slice(bx, bx + bw))
                pedaco = cv2.bitwise_not(_despeckle(cv2.bitwise_not(tinta[caixa]),
                                                    altura_da_pagina or tinta.shape[0]))
                pedaco = _so_a_tinta_forte(pedaco, lab[caixa], nivel, a_papel, b_papel)
                saida[caixa][pedaco > 0] = 0
                return saida
    return cv2.add(recorte, cv2.multiply(cv2.bitwise_not(recorte), cv2.merge([peso, peso, peso]),
                                         scale=1.0 / 255.0))


# O miolo de uma letra pintada dentro da decoracao (o "O" dourado de LOUIS da
# Horas 11) e papel cercado pela letra: nao esta ligado ao papel de fora nem e
# grande, e ficava creme. Conferencia 5 do Samuel (01/10/2026, A2): "eu nao
# quero esses miolos de letras com a cor da pagina de tras, queremos a pagina
# inteiramente branca". Ver _miolos_das_letras. O tamanho maximo da letra, em
# fracao do menor lado da PAGINA: as letras grandes de LOUIS tem 230 a 240
# pontos de altura numa pagina de 3684 (1/15); o miolo de uma pintura (o ceu
# das paisagens da Horas 47) fica dentro de um pedaco pintado bem maior.
# Arriscado: subir muito (o ceu palido de uma pintura pequena, cercada de
# papel, iria a branco).
LETRA_NA_DECORACAO_MAX = 1 / 10


def _pedacos_soltos(resto: np.ndarray, letra_max: int, lado_largo: int = 0) -> np.ndarray | None:
    """Os pedacos pequenos de `resto` (uint8, 255 = o que nao vai a branco):
    os dois lados da caixa ate letra_max pontos, sem encostar na beirada do
    recorte - uma letra (ou um enfeite pequeno) solta no papel branco da
    decoracao. Devolve a mascara (uint8, 255) deles, ou None se nao ha.

    lado_largo (pontos; 0 = nao usar): tambem entra a LINHA de letras presas
    umas as outras por um fio impresso (o "LXXXVIII" da Horas 11, ligado pelo
    risco de pauta embaixo): um lado ate letra_max e o outro maior, desde que
    quase nada dela (ate LINHA_DE_LETRAS_LARGA) sobre de uma abertura com um
    circulo de lado_largo pontos - o traco da letra e o fio sao finos; a
    faixa dourada de uma moldura e larga e sobra inteira (fica de fora).

    Os pedacos sao contados com o resto afinado de 1 ponto: a letra que so
    encosta na decoracao por um fio se solta; depois cada pedaco volta 1
    ponto, dentro do resto. Feito so na caixa de cada pedaco (a conta pela
    folha inteira, rotulo a rotulo, custava ~0,2 s numa pagina das Horas).
    """
    nucleo = np.ones((3, 3), np.uint8)
    quantos, marcas, medidas, _c = cv2.connectedComponentsWithStats(
        cv2.erode(resto, nucleo), connectivity=8)
    altura, largura = resto.shape
    circulo = (cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado_largo, lado_largo))
               if lado_largo >= 3 else None)
    soltos = None
    for i in range(1, quantos):
        x, y, w, h = (int(v) for v in medidas[i, :4])
        if x <= 1 or y <= 1 or x + w >= largura - 1 or y + h >= altura - 1:
            continue
        caixa = (slice(y, y + h), slice(x, x + w))
        if max(w, h) > letra_max:
            if circulo is None or min(w, h) > letra_max:
                continue
            pedaco = (marcas[caixa] == i).astype(np.uint8)
            largo = cv2.morphologyEx(pedaco, cv2.MORPH_OPEN, circulo)
            if cv2.countNonZero(largo) > LINHA_DE_LETRAS_LARGA * medidas[i, cv2.CC_STAT_AREA]:
                continue
        if soltos is None:
            soltos = np.zeros(resto.shape, np.uint8)
        soltos[caixa][marcas[caixa] == i] = 255
    if soltos is None:
        return None
    return cv2.bitwise_and(cv2.dilate(soltos, nucleo), resto)


# Ate que fracao uma linha de letras presas por um fio pode sobrar da
# abertura (ver _pedacos_soltos). Letra fina: quase nada sobra; faixa de
# moldura: quase tudo. Arriscado subir: um pedaco de moldura solto vira preto.
LINHA_DE_LETRAS_LARGA = 0.25


def _miolos_das_letras(ligado: np.ndarray, peso: np.ndarray, letra_max: int) -> None:
    """Devolve ao papel que vai a branco (`ligado`, peso 0 a 255 depois da
    regra da ligacao) o papel que fica DENTRO de uma letra cercada de papel
    branco. `peso`: o peso do papel antes da regra da ligacao.

    O que nao vai a branco (a letra, a pintura e o papel recusado) forma
    pedacos; o pedaco pequeno e solto (_pedacos_soltos) e uma letra (ou um
    enfeite pequeno) no papel branco - e o papel recusado dentro dele e o
    miolo da letra: volta com o peso que tinha. Uma pintura e grande e o ceu
    dela continua como esta. Muda `ligado` no lugar.
    """
    soltos = _pedacos_soltos(cv2.compare(ligado, 0, cv2.CMP_EQ), letra_max)
    if soltos is None:
        return
    miolo = (soltos > 0) & (peso > 0)
    if miolo.any():
        ligado[miolo] = peso[miolo]


# A mancha clara e o respingo cor-de-rosa no papel da decoracao (o oval da
# Horas 11) tambem sao "pedacos pequenos" e virariam pontos pretos. Fica preto
# so o pedaco cuja tinta se afasta do papel: a media da distancia de cor (a e
# b do LAB) mais a media de quanto e mais escura que o papel (L do LAB, 0 a
# 255), pelo menos LETRA_FORCA_MINIMA. Medido nas Horas 11 e 26: letras
# vermelhas, azuis e douradas, e os pontos finais, de 86 a 125; manchas e
# respingos de 46 a 64. Arriscado: subir (a letra dourada clara, ~95, fica em
# cor) ou descer (a mancha vira ponto preto).
LETRA_FORCA_MINIMA = 75.0


def _so_a_tinta_forte(tinta: np.ndarray, lab: np.ndarray, nivel: float,
                      a_papel: float, b_papel: float) -> np.ndarray:
    """A mascara `tinta` (uint8, 255) so com os pedacos fortes - ver
    LETRA_FORCA_MINIMA. lab: o mesmo pedaco em LAB (8 bits); nivel, a_papel
    e b_papel: o papel da pagina (_referencia_do_papel). A cor de cada pedaco
    e a media dele (cv2.mean na caixa do pedaco: barato, e a letra tem uma
    cor so ou quase)."""
    quantos, marcas, medidas, _c = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    if quantos <= 1:
        return tinta
    fica = np.zeros(tinta.shape, np.uint8)
    for i in range(1, quantos):
        x, y, w, h = (int(v) for v in medidas[i, :4])
        caixa = (slice(y, y + h), slice(x, x + w))
        dentro = (marcas[caixa] == i).astype(np.uint8)
        luz, a, b, _ = cv2.mean(lab[caixa], mask=dentro)
        forca = float(np.hypot(a - 128.0 - a_papel, b - 128.0 - b_papel)) + (nivel - luz)
        if forca >= LETRA_FORCA_MINIMA:
            fica[caixa][dentro > 0] = 255
    return fica


def _beirada_do_papel(peso: np.ndarray, lab: np.ndarray, papel_ab: tuple[float, float],
                      rampa: tuple[float, float], luz: np.ndarray, faixa: int) -> np.ndarray:
    """O fio creme em volta da letra dourada (Horas 11, conferencia 5 do
    Samuel, A2: "queremos a pagina inteiramente branca") vai a branco.

    A cor do papel e medida num mapa alisado e reduzido (ver
    DECORACAO_ALISAMENTO): perto da letra, a cor dela se espalha no mapa, e
    uma faixa de uns 10 pontos de papel de verdade (luz e cor de papel, ponto
    a ponto: medido na Horas 11, luz 224 contra 228 do papel, distancia de cor
    3 a 4) ficava creme. Aqui, SO nos pontos a ate `faixa` pontos do papel que
    ja vai a branco, a cor e medida no proprio ponto, sem alisar, com a mesma
    rampa (rampa = (cheio, zero), papel_ab = a e b do papel) e a mesma luz
    (luz: a rampa de luz, 0 a 255); o peso so sobe, nunca desce.

    Por que so na beirada: a cor ponto a ponto no papel inteiro traria de
    volta os quadradinhos da grade do JPEG (o motivo do alisamento), e longe
    do papel branco ligaria o ceu palido de uma pintura ao papel de fora.
    Arriscado: faixa larga (clareia a beirada clara de um dourado).
    """
    # elemento quadrado: o OpenCV dilata em duas passadas (linha e coluna),
    # bem mais barato que o redondo nesta folha inteira
    elemento = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * faixa + 1, 2 * faixa + 1))
    perto = cv2.dilate(cv2.compare(peso, 128, cv2.CMP_GE), elemento)
    perto = cv2.bitwise_and(perto, cv2.compare(peso, 255, cv2.CMP_LT))
    if not cv2.countNonZero(perto):
        return peso
    # a distancia de cor ao papel, ponto a ponto, em contas de 8 bits do
    # OpenCV na folha inteira (indexar so a faixa custava o dobro: ela tem
    # milhoes de pontos; em float, o triplo): |a - a do papel| e |b - b do
    # papel|, o quadrado de cada um por tabela (dividido por `escala_q` para
    # caber em 8 bits ate o fim da rampa), somados, e a rampa por tabela.
    cheio, zero = rampa
    escala_q = max(1.0, zero * zero / 250.0)
    quadrado = np.minimum(255.0, np.round(np.arange(256, dtype=np.float32) ** 2 / escala_q))
    quadrado = quadrado.astype(np.uint8)
    da = cv2.absdiff(cv2.extractChannel(lab, 1), int(round(128.0 + papel_ab[0])))
    db = cv2.absdiff(cv2.extractChannel(lab, 2), int(round(128.0 + papel_ab[1])))
    soma = cv2.add(cv2.LUT(da, quadrado), cv2.LUT(db, quadrado))
    distancia = np.sqrt(np.arange(256, dtype=np.float32) * escala_q)
    tabela = np.clip((zero - distancia) / max(zero - cheio, 1e-3), 0.0, 1.0)
    tabela[255] = 0.0                                   # saturou: longe do papel
    cor = cv2.LUT(soma, (tabela * 255.0 + 0.5).astype(np.uint8))
    novo = cv2.bitwise_and(cv2.multiply(cor, luz, scale=1.0 / 255.0), perto)
    return cv2.max(peso, novo)
    a = lab[ys, xs, 1].astype(np.float32) - 128.0 - papel_ab[0]
    b = lab[ys, xs, 2].astype(np.float32) - 128.0 - papel_ab[1]
    cheio, zero = rampa
    cor = np.clip((zero - np.hypot(a, b)) / (zero - cheio), 0.0, 1.0)
    novo = (cor * luz[ys, xs].astype(np.float32) + 0.5).astype(np.uint8)
    peso = peso.copy()
    peso[ys, xs] = np.maximum(peso[ys, xs], novo)
    return peso


def _pode_ter_decoracao(img3: np.ndarray, peso_gravura: np.ndarray, menor_lado: int) -> bool:
    """A gravura desta pagina pode ter decoracao colorida? Pergunta rapida, de
    8 em 8 pontos, antes das contas da pagina inteira (regra 6, 01/10/2026):
    na pagina de texto com um titulo marcado (o Marial) a resposta e nao, e o
    Magico pro nao paga as zonas nem a medida do papel (~55 ms por pagina).
    E a mesma pergunta de _e_decoracao_colorida (colorido largo dentro da
    gravura), mais grosseira; ela so serve de porta: quem decide, zona a zona,
    continua sendo _e_decoracao_colorida. Arriscado: deixa-la mais exigente
    que a de verdade (decoracao de verdade passaria pelo Melhorar)."""
    passo = 2 * DECORACAO_REDUCAO
    g = peso_gravura[::passo, ::passo] > 0
    if not g.any():
        return False
    lab = cv2.cvtColor(np.ascontiguousarray(img3[::passo, ::passo]),
                       cv2.COLOR_BGR2LAB)
    usar = ~g if float((~g).mean()) >= 0.05 else np.ones(g.shape, bool)
    luz = lab[:, :, 0]
    papel = usar & (luz >= _percentil(luz[usar], BRANCO_PERCENTIL))
    if not papel.any():
        return True
    a = lab[:, :, 1].astype(np.float32) - 128.0
    b = lab[:, :, 2].astype(np.float32) - 128.0
    a_papel, b_papel = float(np.median(a[papel])), float(np.median(b[papel]))
    colorido = (np.hypot(a - a_papel, b - b_papel) > DECORACAO_CROMA).astype(np.uint8)
    lado = max(3, int(round(menor_lado * DESENHO_FECHAMENTO / passo)) | 1)
    largo = cv2.morphologyEx(colorido, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
    return bool((largo.astype(bool) & g).any())


def _tipos_das_zonas(img3: np.ndarray, peso_gravura: np.ndarray, com_decoracao: bool = True,
                     so_a_decoracao: bool = False):
    """Separa as zonas de gravura (pedacos ligados de peso_gravura > 0).

    Devolve (rotulos, foto, decoracao, referencia): rotulos de cada ponto; foto
    e decoracao sao listas booleanas por rotulo (o 0 e o fundo); o que nao e
    nenhum dos dois e gravura de traco (desenho). A foto vem primeiro
    (_e_foto_ou_pintura); decoracao so e perguntada se com_decoracao
    (_e_decoracao_colorida). referencia: _referencia_do_papel, ou None quando
    nao foi preciso medir.

    so_a_decoracao (Magico pro e Melhorar, que so precisam saber o que e
    decoracao): a pergunta da cor vem antes, e a da foto so e feita na zona
    colorida (a pintura colorida, como o anjo da Escola 35, e foto e nao
    decoracao). A resposta e a mesma; o que muda e a ordem - a pergunta da
    foto e a cara (~35 ms por pagina com titulo marcado, no Marial), e a zona
    sem cor nem chega a ela (regra 6, 01/10/2026). Nesse modo, foto so vem
    marcada nas zonas coloridas.
    """
    altura, largura = img3.shape[:2]
    menor_lado = min(altura, largura)
    if so_a_decoracao and not _pode_ter_decoracao(img3, peso_gravura, menor_lado):
        vazio = np.zeros(1, bool)
        return None, vazio, vazio.copy(), None
    onde = (peso_gravura > 0).astype(np.uint8)
    quantas, rotulos, medidas, _c = cv2.connectedComponentsWithStats(onde, connectivity=8)
    foto = np.zeros(quantas, bool)
    decoracao = np.zeros(quantas, bool)
    referencia = None
    for i in range(1, quantas):
        x, y, w, h = (int(v) for v in medidas[i, :4])
        zona = rotulos[y:y + h, x:x + w] == i
        if so_a_decoracao:
            if referencia is None:
                referencia = _referencia_do_papel(img3, onde > 0)
            if _e_decoracao_colorida(img3, zona, (x, y, w, h), menor_lado, referencia):
                if _e_foto_ou_pintura(img3, zona, (x, y, w, h), menor_lado):
                    foto[i] = True
                else:
                    decoracao[i] = True
            continue
        if _e_foto_ou_pintura(img3, zona, (x, y, w, h), menor_lado):
            foto[i] = True
        elif com_decoracao:
            if referencia is None:
                referencia = _referencia_do_papel(img3, onde > 0)
            decoracao[i] = _e_decoracao_colorida(img3, zona, (x, y, w, h), menor_lado, referencia)
    return rotulos, foto, decoracao, referencia


def _com_a_decoracao(base: np.ndarray, img3: np.ndarray, peso_decoracao: np.ndarray,
                     referencia, letras_pretas: bool = False) -> np.ndarray:
    """base (BGR) com a decoracao de cor original por cima, pelo peso. O
    recorte e so a caixa das zonas de decoracao. O papel que vai a branco e o
    ligado ao papel de fora da zona, ou o grande (DECORACAO_PAPEL_GRANDE da
    folha) - ver _decoracao_com_a_cor_original. letras_pretas: so no Preto e
    branco (a letra solta no papel da decoracao sai preta, decisao P4)."""
    bx, by, bw, bh = cv2.boundingRect((peso_decoracao > 0).astype(np.uint8))
    tratada = base.copy()
    fora = peso_decoracao[by:by + bh, bx:bx + bw] <= 0
    tratada[by:by + bh, bx:bx + bw] = _decoracao_com_a_cor_original(
        np.ascontiguousarray(img3[by:by + bh, bx:bx + bw]), referencia, fora=fora,
        area_grande=max(1, int(DECORACAO_PAPEL_GRANDE * img3.shape[0] * img3.shape[1])),
        letra_max=max(1, int(LETRA_NA_DECORACAO_MAX * min(img3.shape[:2]))),
        letras_pretas=letras_pretas, altura_da_pagina=img3.shape[0],
        lado_largo=max(5, int(min(img3.shape[:2]) * DESENHO_FECHAMENTO) | 1))
    return _misturar(base, tratada, peso_decoracao)


def _preto_e_branco_com_gravura(img: np.ndarray, binaria: np.ndarray,
                                peso_gravura: np.ndarray, peso_papel: np.ndarray,
                                clareza: int = AJUSTE_PADRAO,
                                decoracao_em_preto_e_branco: bool = False
                                ) -> tuple[np.ndarray, bool]:
    """O Preto e branco de uma pagina com gravura marcada (regra de 30/09/2026,
    com a emenda da conferencia 3).

    binaria e o Preto e branco da pagina inteira (filtro_preto_e_branco). Cada
    zona de gravura (pedaco ligado de peso_gravura > 0) vira:

    - TONS DE CINZA, se for foto ou pintura de tom continuo
      (_e_foto_ou_pintura; decisao P1 do Samuel, 30/09/2026): o cinza do
      original sem a reticula (_foto_em_tons_de_cinza);
    - COR ORIGINAL, se for decoracao colorida - moldura dourada, iluminura
      (_e_decoracao_colorida; emenda N2 do Samuel, conferencia 3: "Mantem a cor
      original (como o ANTES); traco preto so se eu escolher"): os pontos do
      original, com o papel a branco (_decoracao_com_a_cor_original);
    - DESENHO em preto e branco (_desenho_em_preto_e_branco): a gravura de
      traco sem cor, e a decoracao colorida quando a pessoa marcou
      decoracao_em_preto_e_branco (a caixinha da tela "O que fazer";
      Projeto.pb_decoracao_em_preto_e_branco).

    Misturadas pela borda suave do peso. Devolve (imagem, monocromatica):
    so desenho -> 1 canal, so 0 e 255, monocromatica=True; com foto e sem
    decoracao colorida -> cinza (1 canal), False; com decoracao colorida ->
    cor (3 canais), False. Dentro da zona de desenho vale o desenho onde o peso
    passa de 0,5; na borda suave, a pagina.

    clareza: nao e mais usado (era o do Melhorar na foto); fica na assinatura
    para quem chama.

    Arriscado mudar: nao misturar desenho e pagina pelo peso (sairia cinza, e
    a pagina deixaria de caber em 1 bit); rodar o Melhorar na decoracao (era o
    que a escurecia e lavava, e custava ~3 s por pagina).
    """
    img3 = _tres_canais(img)
    altura, largura = img3.shape[:2]
    menor_lado = min(altura, largura)
    saida = binaria if binaria.ndim == 2 else _para_cinza(binaria)
    saida = saida.copy()

    rotulos, foto, decoracao, referencia = _tipos_das_zonas(
        img3, peso_gravura, com_decoracao=not decoracao_em_preto_e_branco)
    desenho = ~(foto | decoracao)
    desenho[0] = False

    if desenho.any():
        nivel_papel = _percentil(_para_cinza(img3)[::4, ::4], BRANCO_PERCENTIL)
        vale = desenho[rotulos] & (peso_gravura > 0.5)
        if vale.any():
            # o desenho e feito so na caixa das zonas, com folga para o
            # fechamento nao ver a beirada do recorte como fundo
            bx, by, bw, bh = cv2.boundingRect(vale.astype(np.uint8))
            folga = max(5, int(menor_lado * DESENHO_FECHAMENTO) | 1) * 2
            y0, y1 = max(0, by - folga), min(altura, by + bh + folga)
            x0, x1 = max(0, bx - folga), min(largura, bx + bw + folga)
            feito = _desenho_em_preto_e_branco(img3[y0:y1, x0:x1], nivel_papel, menor_lado)
            feito = _despeckle(feito, altura)
            pedaco = saida[y0:y1, x0:x1]
            dentro = vale[y0:y1, x0:x1]
            pedaco[dentro] = feito[dentro]

    if peso_papel.any():
        _pintar_de_branco(saida, peso_papel >= 0.5)     # saida[...] = 255

    if not (foto.any() or decoracao.any()):
        return saida, True

    def so_das(zonas: np.ndarray) -> np.ndarray:
        # o peso so das zonas pedidas; se sao todas, o da gravura inteira,
        # sem a conta ponto a ponto (o caso do Opus Majus 20, so foto)
        if zonas[1:].all():
            return peso_gravura
        return np.where(zonas[rotulos], peso_gravura, 0.0).astype(np.float32)

    if foto.any():
        # Foto e pintura: em tons de cinza (decisao P1; ver FOTO_DESFOQUE). So
        # na caixa das fotos, com folga para o desfoque; a borda suave mistura
        # o cinza com o preto e branco da pagina.
        peso_foto = so_das(foto)
        # a foto que quase enche o fecho convexo dela vale o fecho inteiro
        # (ver FOTO_CAIXA_CHEIA): o pedaco que o contorno livre deixou de fora
        # (o rosto da estatua do Opus 20) nao vira papel branco
        fechos = _fechos_de_foto(rotulos, foto, peso_gravura)
        if fechos is not None:
            # so o que falta dentro do fecho (a borda suave da zona fica)
            dentro = (fechos > 0) & (peso_foto < 1.0)
            peso_foto = np.where(dentro, 1.0, peso_foto).astype(np.float32)
            peso_papel = np.where(dentro, 0.0, peso_papel).astype(np.float32)
        bx, by, bw, bh = cv2.boundingRect((peso_foto > 0).astype(np.uint8))
        folga = 4
        y0, y1 = max(0, by - folga), min(altura, by + bh + folga)
        x0, x1 = max(0, bx - folga), min(largura, bx + bw + folga)
        tons = saida.copy()
        tons[y0:y1, x0:x1] = _foto_em_tons_de_cinza(
            img3[y0:y1, x0:x1], _niveis_da_foto(img3, peso_gravura > 0))
        saida = _misturar(saida, tons, peso_foto)

    if decoracao.any():
        # Moldura e iluminura com a cor original (emenda N2): a pagina passa
        # a ter cor, e a decoracao entra pela borda suave.
        # (a letra solta no papel da decoracao sai preta: decisao P4 do
        # Samuel, conferencia 5 - ver _decoracao_com_a_cor_original)
        saida = _com_a_decoracao(_tres_canais(saida).copy(), img3, so_das(decoracao),
                                 referencia, letras_pretas=True)

    if peso_papel.any():
        saida = _misturar(saida, np.full_like(saida, 255), peso_papel)
    # tem foto em cinza ou decoracao em cor: nao cabe em 1 bit
    return saida, False


def _peso_do_papel_sem_tocar_a_tinta(img: np.ndarray, peso: np.ndarray) -> np.ndarray:
    """Zera o peso do papel em cima da tinta e da orla dela.

    A regiao de papel tem borda suave, de proposito, para nao deixar degrau na
    impressao. So que essa borda passa por cima das letras da beirada do bloco:
    medido no Boecio, de 16% a 26% da tinta da pagina cai dentro da rampa do
    papel, e o branco por cima dela come a borda da letra. Era o ultimo lugar
    onde a queixa de "letra pixelada" ainda acontecia - a rampa caia de 0,84
    para 0,58 justamente neste passo.

    A mancha do verso continua indo a branco: ela e clara demais para o limiar
    local de Sauvola chamar de tinta, que e a razao de o limiar ser local.
    """
    if not peso.any():
        return peso
    from core.detectar_regioes import mascara_de_tinta

    tinta = mascara_de_tinta(_tres_canais(img)).astype(np.uint8)
    if not tinta.any():
        return peso

    lado = max(3, int(min(img.shape[:2]) * ORLA_DA_TINTA_NO_PAPEL) | 1)
    com_a_orla = cv2.dilate(
        tinta, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    limpo = peso.copy()
    limpo[com_a_orla] = 0.0
    return limpo


def _percentil(valores: np.ndarray, q: float) -> float:
    """float(np.percentile(valores, q)), identico ate o ultimo bit, mais rapido
    em imagem uint8 (regra 6, 30/09/2026).

    O np.percentile ordena parcialmente a pagina inteira (~35 ms a 300 DPI, e
    o Magico pro pede uns 15 por pagina). Em uint8 so ha 256 valores: o
    histograma (cv2.calcHist, ~3 ms) diz qual valor esta em cada posicao da
    fila ordenada, e a interpolacao e a MESMA do numpy (metodo "linear": indice
    virtual (n - 1) x q / 100; a + (b - a) x g, ou b - (b - a) x (1 - g) quando
    g >= 0,5 - numpy/lib/_function_base_impl.py, _quantile e _lerp), em
    float64. Outro tipo, ou imagem vazia: o proprio np.percentile.
    Arriscado: mudar a conta da interpolacao (o resultado deixaria de ser o do
    numpy); tests/test_percentil_rapido.py compara com o numpy.
    """
    if not isinstance(valores, np.ndarray) or valores.dtype != np.uint8 or valores.size == 0:
        return float(np.percentile(valores, q))
    n = int(valores.size)
    if n < (1 << 24):
        # calcHist conta em float32: exato ate 2^24 pontos (16 milhoes)
        plano = valores.reshape(-1, 1) if valores.ndim != 2 else valores
        if not plano.flags.c_contiguous and plano.ndim == 2 and plano.strides[1] != 1:
            plano = np.ascontiguousarray(plano)
        contagem = cv2.calcHist([plano], [0], None, [256], [0, 256]).ravel().astype(np.int64)
    else:
        contagem = np.bincount(valores.ravel(), minlength=256)
    acumulado = np.cumsum(contagem)
    virtual = (n - 1) * (q / 100)
    if virtual >= n - 1:
        anterior = proximo = n - 1
    elif virtual < 0:
        anterior = proximo = 0
    else:
        anterior = int(np.floor(virtual))
        proximo = anterior + 1
    a = int(np.searchsorted(acumulado, anterior, side="right"))
    b = int(np.searchsorted(acumulado, proximo, side="right"))
    # Nas pontas a == b: a conta abaixo da o proprio valor, qualquer que seja g.
    g = virtual - float(anterior)
    d = float(b - a)
    if g >= 0.5:
        return float(b) - d * (1 - g)
    return float(a) + d * g


# O mesmo _percentil, com nome publico, para os outros arquivos do core
# (analise, dividir, detectar_regioes) - regra 6, 30/09/2026.
percentil_rapido = _percentil


def _misturar(base: np.ndarray, tratada: np.ndarray, peso: np.ndarray) -> np.ndarray:
    """Mistura duas versoes da mesma imagem pelo peso, pixel a pixel.

    A conta e base x (1 - peso) + tratada x peso, em float32, cortada em 0..255.
    Regra 6 (30/09/2026): quase todo peso e 0 ou 1 (a marcacao so tem borda
    suave numa faixa estreita), e fazer a conta em float na pagina inteira
    custava ~0,4 s por chamada a 300 DPI - tres ou quatro por pagina no Magico
    pro. _misturar_por_partes da o MESMO resultado, ponto por ponto, fazendo a
    conta so onde o peso fica entre 0 e 1. Arriscado mudar: a conta abaixo
    (ordem e tipo das operacoes) e a referencia do caminho rapido.
    """
    if not peso.any():
        return base
    rapido = _misturar_por_partes(base, tratada, peso)
    if rapido is not None:
        return rapido
    p = peso[:, :, None] if base.ndim == 3 else peso
    saida = base.astype(np.float32) * (1.0 - p) + tratada.astype(np.float32) * p
    return np.clip(saida, 0, 255).astype(base.dtype)


def _mascara_0_255(mascara: np.ndarray, canais: int) -> np.ndarray:
    """A mascara booleana como uint8 (0 ou 255), repetida em `canais` canais."""
    k = mascara.view(np.uint8) * np.uint8(255)
    return cv2.merge([k] * canais) if canais > 1 else k


def _pode_no_lugar(img: np.ndarray, mascara: np.ndarray) -> bool:
    """img e mascara servem para as contas no lugar de _pintar_de_branco e
    _copiar_o_cinza (uint8 contigua, mascara booleana do mesmo tamanho)?"""
    return (img.dtype == np.uint8 and img.flags.c_contiguous and img.ndim in (2, 3)
            and mascara.dtype == np.bool_ and mascara.shape == img.shape[:2]
            and (img.ndim == 2 or img.shape[2] in (3, 4)))


def _pintar_de_branco(img: np.ndarray, mascara: np.ndarray) -> None:
    """img[mascara] = 255, no lugar, ponto por ponto igual.

    Regra 6 (30/09/2026): a atribuicao por mascara booleana numa imagem de tres
    canais custa ~0,2 s a 300 DPI; o OU bit a bit com a mascara em 0/255 da o
    mesmo (x | 255 = 255; x | 0 = x) em ~0,02 s."""
    if not _pode_no_lugar(img, mascara):
        img[mascara] = 255
        return
    canais = img.shape[2] if img.ndim == 3 else 1
    cv2.bitwise_or(img, _mascara_0_255(mascara, canais), dst=img)


def _copiar_o_cinza(img: np.ndarray, mascara: np.ndarray, cinza: np.ndarray) -> None:
    """img[mascara] = cinza[mascara][:, None] (os canais iguais ao cinza), no
    lugar, ponto por ponto igual: img ^ ((img ^ cinza) & mascara) troca so os
    pontos da mascara. Regra 6 (30/09/2026): ~7x mais rapido que a mascara
    booleana em tres canais."""
    if (not _pode_no_lugar(img, mascara) or img.ndim != 3 or cinza.dtype != np.uint8
            or cinza.shape != img.shape[:2]):
        img[mascara] = cinza[mascara][:, None]
        return
    canais = img.shape[2]
    diferenca = cv2.bitwise_and(cv2.bitwise_xor(img, cv2.merge([cinza] * canais)),
                                _mascara_0_255(mascara, canais))
    cv2.bitwise_xor(img, diferenca, dst=img)


def _misturar_por_partes(base: np.ndarray, tratada: np.ndarray,
                         peso: np.ndarray) -> np.ndarray | None:
    """A mesma mistura de _misturar, identica ponto por ponto, mais rapida.

    Onde o peso e exatamente 0 a conta de _misturar da a propria base (x 1,0
    mais 0,0 e exato em ponto flutuante); onde e exatamente 1, da a tratada
    (que, em uint8, ja esta dentro de 0..255). So os pontos com peso entre os
    dois passam pela conta em float32 - a MESMA expressao, com os mesmos tipos,
    so que num pedaco da imagem (a conta e ponto a ponto, entao o resultado de
    cada ponto nao muda). Devolve None quando o caso foge do comum (tipos ou
    formas diferentes, peso que nao e float): ai vale a conta inteira.
    Arriscado: mudar a expressao do meio sem mudar a de _misturar (as duas
    precisam dar o mesmo numero); tests/test_misturar_por_partes.py confere.
    """
    if (base.dtype != np.uint8 or tratada.dtype != np.uint8 or base.shape != tratada.shape
            or peso.shape != base.shape[:2] or peso.dtype.kind != "f"):
        return None
    canais = base.shape[2] if base.ndim == 3 else 1
    # Cada ponto (os canais juntos) vira um "item" de `canais` bytes: pegar e
    # pôr pontos por posição na lista assim é bem mais rápido que a máscara
    # booleana em três canais (medido: 0,49 s -> 0,19 s numa página a 300 DPI).
    ponto = np.dtype((np.void, canais))
    pf = peso.ravel()
    um = pf == 1
    no_um = np.flatnonzero(um)
    no_meio = np.flatnonzero(~((pf == 0) | um))
    saida = base.copy()                       # C-contígua
    s = saida.view(ponto).reshape(-1)
    b = np.ascontiguousarray(base).view(ponto).reshape(-1)
    t = np.ascontiguousarray(tratada).view(ponto).reshape(-1)
    s[no_um] = t[no_um]
    if no_meio.size:
        p = pf[no_meio]
        bm = b[no_meio].view(np.uint8).reshape(-1, canais)
        tm = t[no_meio].view(np.uint8).reshape(-1, canais)
        if base.ndim == 3:
            p = p[:, None]
        else:
            bm, tm = bm[:, 0], tm[:, 0]
        conta = bm.astype(np.float32) * (1.0 - p) + tm.astype(np.float32) * p
        pronto = np.ascontiguousarray(np.clip(conta, 0, 255).astype(base.dtype))
        s[no_meio] = pronto.view(ponto).reshape(-1)
    return saida


def _tres_canais(img: np.ndarray) -> np.ndarray:
    """Garante BGR de 3 canais - a mistura por peso (_misturar) e as demais
    contas deste arquivo assumem imagem colorida mesmo quando a entrada e cinza."""
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def _filtro_so_no_pedaco(
    img: np.ndarray, base: np.ndarray, selecao, filtro: str,
    forca_preto: int, clareza: int, intensidade: int,
) -> np.ndarray:
    """Aplica, por cima do resultado, o filtro que a pessoa pediu para um pedaco.

    E o pedido do Samuel: "aplicar filtro so em uma parte selecionada". A
    marcacao ja dizia o que cada area E - gravura, letra, papel -, e isso decide
    COMO o filtro da pagina trata cada uma. O que faltava era dizer QUAL filtro
    vale num pedaco: deixar uma gravura no Original enquanto a folha inteira vai
    a Preto e branco, por exemplo.

    Cada filtro pedido e calculado UMA vez na pagina inteira e colado so onde
    foi pedido. Calcular no recorte sairia diferente: todos os filtros aqui se
    ancoram no nivel do papel da folha, e um recorte de gravura escura teria
    outro nivel de papel - a mesma armadilha que ja custou as capas lavadas.
    """
    pedidos = [f for f in getattr(selecao, "filtros_pedidos", lambda: [])()
               if f in FILTROS_COMUNS and f != filtro]   # "Tirar o fundo" nao vale por pedaco
    if not pedidos:
        return base

    altura, largura = img.shape[:2]

    # O PAPEL de dentro da regiao nao segue o filtro da regiao: segue a pagina.
    # Quem marca um retangulo em volta de uma gravura pega papel junto, e se
    # esse papel ficar no Original ele sai creme ao lado do branco do resto -
    # uma faixa cinza no pe da gravura, que foi o que o Samuel apontou. Papel e
    # papel em qualquer regiao; o filtro do pedaco vale para o CONTEUDO dele.
    cinza = _para_cinza(img)
    nivel_papel = _percentil(cinza, BRANCO_PERCENTIL)
    e_papel = cinza > nivel_papel * TINTA_PARA_ORLA
    lado = max(3, int(min(altura, largura) * ORLA_DA_TINTA_NO_PAPEL) | 1)
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))
    # a orla em volta do conteudo continua sendo do pedaco, para nao serrilhar
    e_papel = cv2.erode(e_papel.astype(np.uint8), nucleo) > 0
    so_conteudo = 1.0 - e_papel.astype(np.float32)

    saida = base
    for pedido in pedidos:
        peso = selecao.peso_do_filtro(altura, largura, pedido) * so_conteudo
        if not peso.any():
            continue
        if pedido == ORIGINAL:
            pedaco = _tres_canais(img)
        else:
            pedaco, _mono = aplicar_filtro(
                img.copy(), pedido, forca_preto, clareza, intensidade)
            pedaco = _tres_canais(pedaco)
        saida = _misturar(_tres_canais(saida), pedaco, peso)
    return saida


def aplicar_filtro_com_selecao(
    img: np.ndarray,
    filtro: str,
    selecao,
    forca_preto: int = AJUSTE_PADRAO,
    clareza: int = AJUSTE_PADRAO,
    intensidade: int = AJUSTE_PADRAO,
    algoritmo_pb: str = "auto",
    despeckle: bool = True,
    decoracao_em_preto_e_branco: bool = False,
) -> tuple[np.ndarray, bool]:
    """O filtro pedido, mas cada area da pagina tratada do seu jeito.

    decoracao_em_preto_e_branco (so vale no Preto e branco): a moldura dourada
    e a iluminura saem como desenho em preto e branco, em vez de manter a cor
    original (o de fabrica). E a opcao do livro
    Projeto.pb_decoracao_em_preto_e_branco (emenda N2 do Samuel, 30/09/2026:
    "traco preto so se eu escolher"); ver _preto_e_branco_com_gravura.

    Ate aqui os filtros olhavam a folha inteira igual, e daí vinham os defeitos
    que medimos: o realce que servia a gravura pegava o papel e virava grao; o
    empurrao para o branco que servia ao papel comia a borda da letra. Os
    remendos que ja estao no codigo - "nao realce onde estiver claro", "ancore
    no nivel do papel" - sao adivinhacao pela luminosidade. Com a selecao o
    filtro para de adivinhar: ele sabe o que esta olhando.

        gravura  ->  papel branco por curva, tom preservado (Melhorar e
                     Magico pro); no Preto e branco vira desenho em 1 bit,
                     menos foto/pintura (regra de 30/09/2026)
        letra    ->  contraste e nitidez, sem realce de fundo
        papel    ->  vai a branco, sem medo de estragar o que esta ao lado

    Dentro da gravura o papel tambem precisa ficar branco - o pedido do Samuel
    foi "quero que o papel saia branco, e o desenho tambem saia perfeito". Quem
    faz isso e a curva de ombro do filtro Melhorar, que leva o nivel do papel a
    255 e deixa o resto da escala onde esta. O que NAO pode acontecer ali dentro
    e binarizar ou pintar de branco chapado: a hachura da xilogravura vive nos
    tons intermediarios, e os dois caminhos a apagam. (Isso vale para o
    Melhorar e o Magico pro. No Preto e branco o Samuel pediu, em 30/09/2026,
    tudo em preto e branco: a gravura sai como desenho, e o que protege a
    hachura ali e o limiar pelo fundo em volta de cada ponto - ver
    _preto_e_branco_com_gravura.)

    Selecao vazia devolve exatamente o comportamento de sempre. E o caso de
    todo projeto antigo e de toda pagina que ninguem marcou.
    """
    from core.selecao import GRAVURA, LETRA, PAPEL

    if selecao is None or getattr(selecao, "vazia", True):
        return aplicar_filtro(img, filtro, forca_preto, clareza, intensidade)

    # Tirar o fundo (item 1.1) chega aqui so quando core/camadas.py deixou a
    # pagina intacta, ou o PDF nao tem camadas: sai como veio, igual ao
    # Original - nunca com outro filtro por cima (decisao do Samuel, 29/09).
    if filtro in (ORIGINAL, TIRAR_FUNDO):
        return img, False

    altura, largura = img.shape[:2]
    peso_gravura = selecao.peso(altura, largura, GRAVURA)
    peso_letra = selecao.peso(altura, largura, LETRA)
    peso_papel = selecao.peso(altura, largura, PAPEL)

    # A borda suave do papel nao pode passar por cima de letra: ver
    # _peso_do_papel_sem_tocar_a_tinta.
    #
    # Menos quando a pessoa marcou a FOLHA INTEIRA como papel. Ai ela nao esta
    # dizendo "aqui e fundo", esta dizendo "quero esta folha em branco" - uma
    # capa que nao se quer no livro reimpresso, por exemplo. Proteger a tinta
    # nesse caso deixa a etiqueta da biblioteca e a sujeira da borda no meio da
    # folha branca, que e o oposto do pedido.
    if peso_papel.any() and filtro != ORIGINAL:
        if float((peso_papel > 0.5).mean()) < FOLHA_INTEIRA_EM_BRANCO:
            peso_papel = _peso_do_papel_sem_tocar_a_tinta(img, peso_papel)

    try:
        # --- Preto e branco -------------------------------------------------
        # Regra do Samuel (30/09/2026), com a emenda da conferencia 3: titulo
        # colorido e gravura de traco viram desenho (traco em preto, fundo em
        # branco); moldura dourada e iluminura mantem a cor original (traco
        # preto so com decoracao_em_preto_e_branco); a foto ou pintura de tom
        # continuo sai em tons de cinza (decisao P1). Ver
        # _preto_e_branco_com_gravura. Antes daqui, toda gravura ficava em
        # cor (o Melhorar rodava dentro dela).
        if filtro == PRETO_E_BRANCO:
            binaria = filtro_preto_e_branco(img, forca=forca_preto, algoritmo=algoritmo_pb,
                                            despeckle=despeckle)
            if not peso_gravura.any():
                saida = binaria
                if peso_papel.any():
                    saida = _misturar(saida, np.full_like(saida, 255), peso_papel)
                return saida, True

            return _preto_e_branco_com_gravura(
                img, binaria, peso_gravura, peso_papel, clareza,
                decoracao_em_preto_e_branco=decoracao_em_preto_e_branco)

        # --- Melhorar e Magico pro ------------------------------------------
        base = filtro_melhorar(img, clareza=clareza) if filtro == MELHORAR \
            else filtro_magico_pro(img, intensidade=intensidade)

        # Na gravura, o tratamento suave: papel a branco pela curva de ombro e
        # tom preservado. O Magico pro leva realce local e ganho de saturacao,
        # que numa xilogravura fecham a hachura e fabricam grao no papel de
        # dentro do desenho.
        #
        # Menos na DECORACAO COLORIDA - moldura dourada, iluminura (ver
        # DECORACAO_CROMA): ali vale a regra da Fase 1, "moldura dourada ...
        # mantida sem mudar a cor" e "iluminura sai intacta", e sai o original
        # com so o papel a branco (_decoracao_com_a_cor_original). O Melhorar
        # do recorte escurecia o dourado (Horas 13 e 26: "a borda dourada
        # deveria sair sem alteracao"), lavava o ouro e o anjinho da Horas 11
        # e deixava o papel da zona cinza (faixa embaixo de "pitie de nous" da
        # Horas 47). Foto, pintura e gravura de traco: como sempre.
        if peso_gravura.any():
            img3 = _tres_canais(img)
            rotulos, _foto, decoracao, referencia = _tipos_das_zonas(
                img3, peso_gravura, so_a_decoracao=True)
            # a foto do contorno livre vale o fecho inteiro (conferencia 6,
            # X2, Opus 20): sem papel nem letra dentro - ver _a_foto_inteira.
            # Se mudou, as zonas sao separadas de novo (os rotulos mudam).
            inteira = _a_foto_inteira(img3, peso_gravura, peso_letra, peso_papel,
                                      decoracao if rotulos is not None else None)
            if inteira is not None:
                peso_gravura, peso_letra, peso_papel = inteira
                rotulos, _foto, decoracao, referencia = _tipos_das_zonas(
                    img3, peso_gravura, so_a_decoracao=True)
            if decoracao.any():
                peso_decoracao = peso_gravura if decoracao[1:].all() else np.where(
                    decoracao[rotulos], peso_gravura, 0.0).astype(np.float32)
                peso_resto = np.where(decoracao[rotulos], 0.0, peso_gravura).astype(np.float32)
            else:
                peso_decoracao, peso_resto = None, peso_gravura
            if peso_resto.any():
                base = _misturar(base, _limpar_cada_gravura(img, peso_resto > 0.5, clareza,
                                                            onde_vale=peso_resto > 0,
                                                            fundo=base),
                                 peso_resto)
            if peso_decoracao is not None:
                base = _com_a_decoracao(_tres_canais(base), img3, peso_decoracao, referencia)

        # Na letra, so nitidez - E SO EM CIMA DO TRACO. Um bloco de texto e
        # metade papel: as entrelinhas e as margens dentro do bloco. Tratar o
        # bloco inteiro como letra impede o papel de branquear justamente onde
        # ele mais aparece, que foi o que deixava a folha amarelada.
        if peso_letra.any():
            from core.detectar_regioes import refinar_para_tinta

            traco, papel_do_bloco = refinar_para_tinta(img, peso_letra > 0.5)
            if traco.any():
                so_nitidez = _nitidez(
                    _tres_canais(img), _entre(intensidade, NITIDEZ_MIN, NITIDEZ_MAX)
                )
                base = _misturar(base, so_nitidez, traco.astype(np.float32))
            if papel_do_bloco.any():
                base = _misturar(base, np.full_like(base, 255),
                                 papel_do_bloco.astype(np.float32))

        # No papel marcado, branco de verdade.
        if peso_papel.any():
            base = _misturar(base, np.full_like(base, 255), peso_papel)

        # A tinta velha e marrom, e a impressora imprime isso como cor.
        # Dentro da gravura nao se toca. Ver tirar_o_amarelado_da_tinta.
        if filtro in (MELHORAR, MAGICO_PRO):
            base = tirar_o_amarelado_da_tinta(
                _tres_canais(base), 1.0 - np.clip(peso_gravura, 0.0, 1.0))

        return _filtro_so_no_pedaco(img, base, selecao, filtro,
                                    forca_preto, clareza, intensidade), False

    except cv2.error as exc:
        raise ErroFiltro("Não consegui limpar esta página.") from exc


def aplicar_filtro(
    img: np.ndarray,
    filtro: str,
    forca_preto: int = AJUSTE_PADRAO,
    clareza: int = AJUSTE_PADRAO,
    intensidade: int = AJUSTE_PADRAO,
    algoritmo_pb: str = "auto",
    despeckle: bool = True,
) -> tuple[np.ndarray, bool]:
    """Aplica o filtro pedido na página inteira, do mesmo jeito.

    Cada filtro tem o seu ajuste de 0 a 100; os outros dois sao ignorados.
    Devolve (imagem, monocromatica). monocromatica=True avisa o EscritorPDF
    para salvar a página em 1 bit.

    `algoritmo_pb` e `despeckle` só valem para o Preto e branco.

    Quando a página tem marcação, quem manda e aplicar_filtro_com_selecao.
    """
    try:
        # Tirar o fundo (item 1.1): ver aplicar_filtro_com_selecao - aqui so
        # chega a pagina que fica como veio.
        if filtro in (ORIGINAL, TIRAR_FUNDO):
            return img, False
        if filtro == PRETO_E_BRANCO:
            return filtro_preto_e_branco(
                img, forca=forca_preto, algoritmo=algoritmo_pb,
                despeckle=despeckle), True
        # Sem selecao nao ha mascara de gravura, entao a protecao vem so da
        # forca da cor: o que passa de SATURACAO_DE_RUBRICA fica.
        if filtro == MELHORAR:
            return tirar_o_amarelado_da_tinta(
                filtro_melhorar(img, clareza=clareza)), False
        if filtro == MAGICO_PRO:
            return tirar_o_amarelado_da_tinta(
                filtro_magico_pro(img, intensidade=intensidade)), False
    except cv2.error as exc:
        raise ErroFiltro("Não consegui limpar esta página.") from exc

    # filtro desconhecido: nao mexer e melhor que quebrar
    return img, False
