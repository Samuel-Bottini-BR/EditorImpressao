"""Os tres filtros de limpeza + o Original.

Esta e a parte mais importante do programa. As versoes anteriores falharam aqui
por tentar inventar formula propria. Aqui usamos o que já e consagrado:

- Preto e branco: binarizacao local de Sauvola (via DoxaPy, licenca CC0).
  E o mesmo caminho do ScanTailor. Resolve amarelado E bleed-through (o texto
  do verso transparecendo) de uma vez só, porque o limiar e calculado numa
  janela ao redor de cada pixel: o texto do verso e sempre mais claro que o
  texto da frente na vizinhanca dele, entao cai para o branco.

- Melhorar: divisão pelo fundo estimado. Limpa a iluminacao sem tocar na cor.

- Mágico pro: Melhorar + CLAHE + saturacao + nitidez, no espirito do
  "magic color" do CamScanner.
"""

from __future__ import annotations

import cv2
import numpy as np

# --- nomes dos filtros (usados em ConfigPagina.filtro) -----------------------
ORIGINAL = "original"
PRETO_E_BRANCO = "preto_e_branco"
MELHORAR = "melhorar"
MAGICO_PRO = "magico_pro"

FILTROS = (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO)

NOMES_AMIGAVEIS = {
    ORIGINAL: "Original",
    PRETO_E_BRANCO: "Preto e branco",
    MELHORAR: "Melhorar",
    MAGICO_PRO: "Mágico pro",
}

# --- parametros de ajuste (mexer aqui para calibrar) -------------------------

# Janela do Sauvola, em fracao da altura da pagina. ~1/20 da altura pega algumas
# linhas de texto de cada vez, que e o tamanho certo para separar texto de fundo.
JANELA_FRACAO_ALTURA = 1 / 20
JANELA_MIN = 15
JANELA_MAX = 151

# Todos os ajustes de filtro sao um numero de 0 a 100, com 50 no meio. E o que
# o medidor deslizante da interface mostra: o usuario nunca ve k, clipLimit
# nem saturacao.
AJUSTE_MIN, AJUSTE_PADRAO, AJUSTE_MAX = 0, 50, 100

# k do Sauvola. Quanto MAIOR o k, MAIS ALTO fica o limiar de branco, ou seja,
# menos pixels viram preto. Por isso "mais fraco" tem k maior.
# 0 -> 0,40 (bem fraco)   50 -> 0,20 (normal)   100 -> 0,06 (bem escuro)
K_FRACO, K_NORMAL, K_ESCURO = 0.40, 0.20, 0.06

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


def binarizar(cinza: np.ndarray, janela: int | None = None, k: float = 0.20) -> np.ndarray:
    """Binarizacao local de Sauvola. Devolve imagem 0/255 de um canal."""
    if janela is None:
        janela = janela_para_altura(cinza.shape[0])

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


def k_do_sauvola(forca: int = AJUSTE_PADRAO) -> float:
    """Medidor de forca do preto -> k do Sauvola.

    Em duas retas para que a posicao do meio caia exatamente no k=0,20, que e
    o valor que funciona na maioria dos livros. Uma reta so entre 0,40 e 0,06
    deixaria o meio em 0,23 e o padrao ficaria diferente do recomendado.
    """
    forca = max(AJUSTE_MIN, min(AJUSTE_MAX, int(forca)))
    if forca <= AJUSTE_PADRAO:
        return K_FRACO + (K_NORMAL - K_FRACO) * (forca / AJUSTE_PADRAO)
    return K_NORMAL + (K_ESCURO - K_NORMAL) * ((forca - AJUSTE_PADRAO) / AJUSTE_PADRAO)


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


# Acima desta fracao de pixels coloridos a pagina nao e "texto com rubricacao":
# e iluminura ou estampa colorida de pagina cheia. Ali o Preto e branco ja e o
# filtro errado - o programa avisa "Tem cor" e sugere o Magico pro - e a
# conversao pelo maior canal so faz perder textura.
FRACAO_COLORIDA_DE_ILUMINURA = 0.25
SATURACAO_DE_RUBRICA = 60


def _cinza_para_binarizar(img: np.ndarray) -> np.ndarray:
    """Converte para cinza levando a COR em conta, so para o Preto e branco.

    A conversao comum pesa os canais pelo brilho que o olho percebe, e nela
    tinta vermelha fica tao escura quanto tinta preta. No Graduale, manuscrito
    do seculo XIV cujas pautas sao vermelhas, isso transformava as linhas em
    barras pretas grossas - e a rubricacao vermelha e parte do documento, nao
    sujeira. Medido no acervo, o vermelho saia em 130 numa escala de 0 a 255,
    quase colado nos 87 da tinta preta.

    Quando ha rubricacao, usamos o maior dos tres canais: tinta vermelha tem o
    vermelho alto, entao o maior e alto e ela le como CLARA; tinta preta tem os
    tres baixos e continua escura. No Graduale o vermelho sobe para 176, a
    distancia ate o preto quase dobra, e os vazios das letras TRIPLICAM porque
    as pautas param de engolir a notacao.

    Mas numa pagina inteiramente colorida - uma iluminura do Livro de Horas -
    a mesma conta so clareia tudo e a textura se perde. Medido: essas paginas
    perdiam ate 2.900 vazios cada. Por isso a conversao especial vale so quando
    a cor e MINORIA na pagina, que e o caso da rubricacao.
    """
    if img.ndim == 2:
        return img

    saturacao = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]
    fracao_colorida = float((saturacao > SATURACAO_DE_RUBRICA).mean())
    if fracao_colorida > FRACAO_COLORIDA_DE_ILUMINURA:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    try:
        import doxapy

        rgb = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), dtype=np.uint8)
        return doxapy.to_grayscale(doxapy.GrayscaleAlgorithms.VALUE, rgb)
    except Exception:  # noqa: BLE001 - o plano B da a mesma conta
        return img.max(axis=2)


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


def filtro_preto_e_branco(
    img: np.ndarray, forca: int = AJUSTE_PADRAO, despeckle: bool = True
) -> np.ndarray:
    """Preto e branco (Eco). Devolve imagem de 1 canal, só 0 e 255.

    forca vai de 0 (bem fraco, texto mais fino) a 100 (bem escuro, pega mais
    tinta e mais mancha junto).
    """
    cinza = _cinza_para_binarizar(img)
    janela = janela_para_altura(cinza.shape[0])
    binaria = binarizar(cinza, janela=janela, k=k_do_sauvola(forca))
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
    return float(np.percentile(_para_cinza(img), BRANCO_PERCENTIL))


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

    limiar_claro = float(np.percentile(cinza, BRANCO_PERCENTIL))
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
    nivel_papel = float(np.percentile(_para_cinza(saida)[papel], 50))
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

    preto = float(np.percentile(luz, percentil))
    papel = float(np.percentile(luz, BRANCO_PERCENTIL))
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

    preto_antes = float(np.percentile(cinza_antes, 2))
    papel_antes = float(np.percentile(cinza_antes, BRANCO_PERCENTIL))
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

    preto_depois = float(np.percentile(cinza_depois[tinta > 0], 20))
    papel_depois = float(np.percentile(cinza_depois[tinta == 0], 80)) \
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
    nivel_papel = float(np.percentile(cinza, BRANCO_PERCENTIL))
    if nivel_papel < 1:
        return True
    return float((cinza < nivel_papel * TINTA_PARA_ORLA).mean()) < TINTA_DE_FOLHA_ESCRITA


def _alisar_o_papel(img: np.ndarray) -> np.ndarray:
    """Tira o grao do papel sem encostar na tinta.

    As curvas que clareiam a folha multiplicam o que ja estava la: numa pagina
    de papel escuro e granulado, levar o papel de 159 para 255 leva junto o
    ruido de 11 para 18. Alisar SO o papel resolve sem tocar na letra - o
    alisamento fica de fora da tinta e da orla dela, que sao justamente o que
    precisa continuar nitido.
    """
    cinza = _para_cinza(img)
    nivel_papel = float(np.percentile(cinza, BRANCO_PERCENTIL))
    if nivel_papel < 1:
        return img

    tinta = (cinza < nivel_papel * TINTA_PARA_ORLA).astype(np.uint8)
    lado = max(3, int(min(img.shape[:2]) * ORLA_DA_TINTA_NO_PAPEL) | 1)
    perto_da_tinta = cv2.dilate(
        tinta, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    alisada = cv2.medianBlur(img, 3)
    saida = img.copy()
    saida[~perto_da_tinta] = alisada[~perto_da_tinta]
    return saida


def filtro_melhorar(img: np.ndarray, clareza: int = AJUSTE_PADRAO) -> np.ndarray:
    """Melhorar: fundo branco limpo, cores originais preservadas.

    clareza vai de 0 (fundo quase como veio) a 100 (fundo bem branco).
    """
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    saida = _achatar_iluminacao(img, _nivel_do_papel(img))
    saida = _balanco_de_branco(saida, clareza)
    if not _quase_sem_tinta(img):
        saida = _aprofundar_pretos(saida)
    saida = _alisar_o_papel(saida)
    return _recompor_a_rampa(img, saida)


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

    nivel_papel = float(np.percentile(luz, BRANCO_PERCENTIL))
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
    nivel_papel = float(np.percentile(cinza, BRANCO_PERCENTIL))

    claro = cinza > nivel_papel * CLARO_COMO_PAPEL
    tem_cor = np.clip(
        (saturacao - SATURACAO_DE_GRAO) / max(1.0, SATURACAO_DE_RUBRICA - SATURACAO_DE_GRAO),
        0.0, 1.0)
    peso = np.where(claro, tem_cor, 1.0).astype(np.float32)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1.0 + (ganho - 1.0) * peso), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


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
    nivel_papel = float(np.percentile(cinza, BRANCO_PERCENTIL))
    tinta = (cinza < nivel_papel * TINTA_PARA_ORLA).astype(np.uint8)

    lado = max(3, int(min(img.shape[:2]) / ORLA_DA_LETRA) | 1)
    orla = cv2.dilate(
        tinta, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))) > 0

    saida = img.copy()
    saida[quase_branco & ~orla] = 255

    # A orla fica, mas sem a cor do papel: mantida como veio, ela vira um halo
    # creme em volta de cada letra sobre o papel branco. Igualando os tres
    # canais ao brilho do pixel, a rampa continua existindo em tom de cinza e o
    # amarelado some junto com o resto do fundo.
    if saida.ndim == 3:
        de_fora = orla & quase_branco
        if de_fora.any():
            saida[de_fora] = cinza[de_fora][:, None]
    return saida


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

    # 3. cor mais viva
    #
    # ATENCAO, ja medido: este passo tambem realca a UNICA cor de uma folha
    # velha sem tinta, que e o amarelado do proprio papel. Olhadas as imagens, a
    # folha vazia do Boecio e a 446 da Rhetorica saem de um creme palido para um
    # amarelo forte - o oposto do que o filtro deveria fazer. Por o passo dentro
    # do guarda acima resolve quatro reprovacoes da regua e nao cria nenhuma,
    # mas tem um preco: numa pagina colorida SEM TINTA o medidor de intensidade
    # deixa de mexer na cor, e ha teste cobrando esse comportamento
    # (test_intensidade_do_magico_muda_a_saturacao). Fica como esta ate haver
    # decisao. Ver o cabecalho de _realcar_saturacao para as trocas de espaco de
    # cor ja tentadas e por que foram revertidas.
    saida = _realcar_saturacao(saida, _entre(intensidade, SATURACAO_MIN, SATURACAO_MAX))

    # 4. texto mais nitido
    saida = _nitidez(saida, _entre(intensidade, NITIDEZ_MIN, NITIDEZ_MAX))

    # 5. fundo branco de verdade, e sem o grao que as curvas amplificaram
    saida = _alisar_o_papel(saida)
    saida = _empurrar_branco(saida)

    # 6. e a borda da letra de volta ao que era, agora entre um preto mais fundo
    # e um papel mais claro
    return _recompor_a_rampa(img, saida)


# Area minima de uma gravura para valer a pena limpa-la pelo nivel dela, em
# fracao da pagina. Abaixo disso e respingo, e o recorte nem teria papel dentro
# para medir.
AREA_MINIMA_DE_GRAVURA = 0.002


def _limpar_cada_gravura(img: np.ndarray, gravura: np.ndarray,
                         clareza: int = AJUSTE_PADRAO) -> np.ndarray:
    """Limpa cada gravura ancorada no papel DELA, e nao no da folha.

    Sem isso o papel dentro do desenho nao chega a branco: medido na xilogravura
    da Rhetorica, ele parava em 214 numa escala em que 255 e branco, enquanto a
    margem da folha, essa sim, ia a 255. O papel dentro de um bloco gravado e
    mais escuro que a margem, e a curva de ombro calculada pela folha inteira
    nao alcanca ele.

    Uma iluminura de meio-tom, que quase nao tem papel a vista, passa por aqui
    sem mudanca: _balanco_de_branco desiste sozinho quando nao acha papel.
    """
    saida = filtro_melhorar(_tres_canais(img), clareza=clareza)

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
        pedaco = _tres_canais(img)[y:y + h, x:x + w]
        if pedaco.size:
            saida[y:y + h, x:x + w] = filtro_melhorar(pedaco, clareza=clareza)
    return saida


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


def _misturar(base: np.ndarray, tratada: np.ndarray, peso: np.ndarray) -> np.ndarray:
    """Mistura duas versoes da mesma imagem pelo peso, pixel a pixel."""
    if not peso.any():
        return base
    p = peso[:, :, None] if base.ndim == 3 else peso
    saida = base.astype(np.float32) * (1.0 - p) + tratada.astype(np.float32) * p
    return np.clip(saida, 0, 255).astype(base.dtype)


def _tres_canais(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def aplicar_filtro_com_selecao(
    img: np.ndarray,
    filtro: str,
    selecao,
    forca_preto: int = AJUSTE_PADRAO,
    clareza: int = AJUSTE_PADRAO,
    intensidade: int = AJUSTE_PADRAO,
) -> tuple[np.ndarray, bool]:
    """O filtro pedido, mas cada area da pagina tratada do seu jeito.

    Ate aqui os filtros olhavam a folha inteira igual, e daí vinham os defeitos
    que medimos: o realce que servia a gravura pegava o papel e virava grao; o
    empurrao para o branco que servia ao papel comia a borda da letra. Os
    remendos que ja estao no codigo - "nao realce onde estiver claro", "ancore
    no nivel do papel" - sao adivinhacao pela luminosidade. Com a selecao o
    filtro para de adivinhar: ele sabe o que esta olhando.

        gravura  ->  papel branco por curva, tom preservado; nunca binarizada
        letra    ->  contraste e nitidez, sem realce de fundo
        papel    ->  vai a branco, sem medo de estragar o que esta ao lado

    Dentro da gravura o papel tambem precisa ficar branco - o pedido do Samuel
    foi "quero que o papel saia branco, e o desenho tambem saia perfeito". Quem
    faz isso e a curva de ombro do filtro Melhorar, que leva o nivel do papel a
    255 e deixa o resto da escala onde esta. O que NAO pode acontecer ali dentro
    e binarizar ou pintar de branco chapado: a hachura da xilogravura vive nos
    tons intermediarios, e os dois caminhos a apagam.

    Selecao vazia devolve exatamente o comportamento de sempre. E o caso de
    todo projeto antigo e de toda pagina que ninguem marcou.
    """
    from core.selecao import GRAVURA, LETRA, PAPEL

    if selecao is None or getattr(selecao, "vazia", True):
        return aplicar_filtro(img, filtro, forca_preto, clareza, intensidade)

    if filtro == ORIGINAL:
        return img, False

    altura, largura = img.shape[:2]
    peso_gravura = selecao.peso(altura, largura, GRAVURA)
    peso_letra = selecao.peso(altura, largura, LETRA)
    peso_papel = selecao.peso(altura, largura, PAPEL)

    # A borda suave do papel nao pode passar por cima de letra: ver
    # _peso_do_papel_sem_tocar_a_tinta.
    if peso_papel.any() and filtro != ORIGINAL:
        peso_papel = _peso_do_papel_sem_tocar_a_tinta(img, peso_papel)

    try:
        # --- Preto e branco -------------------------------------------------
        # Binarizar uma gravura de meio-tom e joga-la fora. Onde ha gravura
        # marcada, a pagina deixa de ser monocromatica e o desenho fica em tom
        # continuo; o resto vira preto e branco como sempre.
        if filtro == PRETO_E_BRANCO:
            binaria = filtro_preto_e_branco(img, forca=forca_preto)
            if not peso_gravura.any():
                saida = binaria
                if peso_papel.any():
                    saida = _misturar(saida, np.full_like(saida, 255), peso_papel)
                return saida, True

            limpa = _limpar_cada_gravura(img, peso_gravura > 0.5, clareza)
            saida = _misturar(_tres_canais(binaria), limpa, peso_gravura)
            if peso_papel.any():
                saida = _misturar(saida, np.full_like(saida, 255), peso_papel)
            return saida, False   # tem gravura: nao cabe em 1 bit

        # --- Melhorar e Magico pro ------------------------------------------
        base = filtro_melhorar(img, clareza=clareza) if filtro == MELHORAR \
            else filtro_magico_pro(img, intensidade=intensidade)

        # Na gravura, o tratamento suave: papel a branco pela curva de ombro e
        # tom preservado. O Magico pro leva realce local e ganho de saturacao,
        # que numa xilogravura fecham a hachura e fabricam grao no papel de
        # dentro do desenho.
        if peso_gravura.any():
            base = _misturar(base, _limpar_cada_gravura(img, peso_gravura > 0.5, clareza),
                             peso_gravura)

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

        return base, False

    except cv2.error as exc:
        raise ErroFiltro("Não consegui limpar esta página.") from exc


def aplicar_filtro(
    img: np.ndarray,
    filtro: str,
    forca_preto: int = AJUSTE_PADRAO,
    clareza: int = AJUSTE_PADRAO,
    intensidade: int = AJUSTE_PADRAO,
) -> tuple[np.ndarray, bool]:
    """Aplica o filtro pedido na página inteira, do mesmo jeito.

    Cada filtro tem o seu ajuste de 0 a 100; os outros dois sao ignorados.
    Devolve (imagem, monocromatica). monocromatica=True avisa o EscritorPDF
    para salvar a página em 1 bit.

    Quando a página tem marcação, quem manda e aplicar_filtro_com_selecao.
    """
    try:
        if filtro == ORIGINAL:
            return img, False
        if filtro == PRETO_E_BRANCO:
            return filtro_preto_e_branco(img, forca=forca_preto), True
        if filtro == MELHORAR:
            return filtro_melhorar(img, clareza=clareza), False
        if filtro == MAGICO_PRO:
            return filtro_magico_pro(img, intensidade=intensidade), False
    except cv2.error as exc:
        raise ErroFiltro("Não consegui limpar esta página.") from exc

    # filtro desconhecido: nao mexer e melhor que quebrar
    return img, False
