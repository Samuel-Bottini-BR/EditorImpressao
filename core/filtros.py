"""Os tres filtros de limpeza + o Original.

Esta e a parte mais importante do programa. As versoes anteriores falharam aqui
por tentar inventar formula propria. Aqui usamos o que ja e consagrado:

- Preto e branco: binarizacao local de Sauvola (via DoxaPy, licenca CC0).
  E o mesmo caminho do ScanTailor. Resolve amarelado E bleed-through (o texto
  do verso transparecendo) de uma vez so, porque o limiar e calculado numa
  janela ao redor de cada pixel: o texto do verso e sempre mais claro que o
  texto da frente na vizinhanca dele, entao cai para o branco.

- Melhorar: divisao pelo fundo estimado. Limpa a iluminacao sem tocar na cor.

- Magico pro: Melhorar + CLAHE + saturacao + nitidez, no espirito do
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
    MAGICO_PRO: "Magico pro",
}

# --- parametros de ajuste (mexer aqui para calibrar) -------------------------

# Janela do Sauvola, em fracao da altura da pagina. ~1/20 da altura pega algumas
# linhas de texto de cada vez, que e o tamanho certo para separar texto de fundo.
JANELA_FRACAO_ALTURA = 1 / 20
JANELA_MIN = 15
JANELA_MAX = 151

# k do Sauvola. Quanto MAIOR o k, MAIS ALTO fica o limiar de branco, ou seja,
# menos pixels viram preto. Por isso "mais fraco" tem k maior.
K_POR_FORCA = {
    "mais_fraco": 0.34,
    "normal": 0.20,
    "mais_escuro": 0.10,
}
FORCAS = tuple(K_POR_FORCA)

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

# Magico pro
CLAHE_CLIP = 2.0
CLAHE_GRADE = (8, 8)
SATURACAO_GANHO = 1.35
NITIDEZ_PESO = 0.6
BRANCO_LIMIAR = 235


class ErroFiltro(Exception):
    """Falha ao aplicar um filtro, ja com mensagem para o usuario."""


# --- binarizacao: DoxaPy com queda automatica para scikit-image --------------

def _sauvola_doxapy(cinza: np.ndarray, janela: int, k: float) -> np.ndarray | None:
    """Sauvola pelo DoxaPy. Devolve None se a biblioteca nao estiver disponivel."""
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
    """Tamanho da janela do Sauvola proporcional a pagina, sempre impar."""
    janela = int(altura * JANELA_FRACAO_ALTURA)
    janela = max(JANELA_MIN, min(JANELA_MAX, janela))
    if janela % 2 == 0:
        janela += 1
    return janela


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


def _despeckle(binaria: np.ndarray, altura: int) -> np.ndarray:
    """Remove manchinhas isoladas de preto (poeira do scanner).

    A area minima acompanha a resolucao: a 600 DPI a mesma sujeira ocupa
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
    img: np.ndarray, forca: str = "normal", despeckle: bool = True
) -> np.ndarray:
    """Preto e branco (Eco). Devolve imagem de 1 canal, so 0 e 255."""
    if forca not in K_POR_FORCA:
        forca = "normal"
    cinza = _para_cinza(img)
    janela = janela_para_altura(cinza.shape[0])
    binaria = binarizar(cinza, janela=janela, k=K_POR_FORCA[forca])
    if despeckle:
        binaria = _despeckle(binaria, cinza.shape[0])
    return binaria


def _estimar_fundo_cinza(cinza: np.ndarray) -> np.ndarray:
    """Estima a iluminacao da folha: a variacao lenta de claro e escuro.

    Sao a sombra da lombada, a luz torta do scanner e o amarelado irregular.
    O desfoque forte apaga o texto e deixa so isso.

    Truque de desempenho: como o resultado e liso por definicao, o desfoque e
    feito numa miniatura e depois esticado de volta. Desfocar a pagina inteira
    a 300 DPI levava quase 5 segundos por pagina - inviavel para 500 paginas.
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

    Duas diferencas para a divisao ingenua (img / fundo * 255), que foi onde a
    versao anterior estragava as capas:

    1. Dividimos pelo fundo *relativo ao nivel do papel*, nao pelo branco
       absoluto. So a desigualdade e corrigida, o tom geral fica.

    2. A correcao so vale onde o fundo local ainda parece papel. Numa capa
       azul, o fundo local e escuro porque ali o conteudo E escuro - nao e
       sombra. Tratar aquilo como sombra era o que lavava a capa. O peso cai a
       zero conforme o fundo se afasta do nivel do papel.

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


def _balanco_de_branco(img: np.ndarray) -> np.ndarray:
    """Faz o papel virar branco de verdade, tirando o amarelado.

    Olha SO para os pixels que parecem papel: claros e pouco coloridos. Calcula
    a media de cada canal neles e estica para o branco. Como a mesma logica
    ignora tinta e ilustracao, a cor do conteudo nao e afetada.

    Se a pagina quase nao tem papel branco a vista (uma capa colorida inteira,
    uma foto de pagina cheia), nao ha o que balancear e a imagem sai como veio.
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
    return _curva_de_ombro(saida, nivel_papel)


def _curva_de_ombro(img: np.ndarray, nivel_papel: float) -> np.ndarray:
    """Mapeia nivel_papel -> 255 mexendo so na parte clara da escala."""
    inicio = max(1.0, nivel_papel * OMBRO_INICIO)
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
    """Puxa o ponto de preto para baixo, so na luminosidade.

    Trabalhar no canal L do LAB (e nao nos tres canais BGR) evita o desvio de
    matiz que aparecia quando cada canal era esticado por conta propria.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    luz = lab[:, :, 0].astype(np.float32)
    preto = float(np.percentile(luz, percentil))
    if preto < 1:
        return img
    luz = (luz - preto) * (255.0 / max(1.0, 255.0 - preto))
    lab[:, :, 0] = np.clip(luz, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def filtro_melhorar(img: np.ndarray) -> np.ndarray:
    """Melhorar: fundo branco limpo, cores originais preservadas."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    saida = _achatar_iluminacao(img, _nivel_do_papel(img))
    saida = _balanco_de_branco(saida)
    return _aprofundar_pretos(saida)


def _realcar_saturacao(img: np.ndarray, ganho: float = SATURACAO_GANHO) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * ganho, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _nitidez(img: np.ndarray, peso: float = NITIDEZ_PESO) -> np.ndarray:
    """Unsharp mask: soma a propria imagem menos a versao borrada dela."""
    sigma = max(1.0, img.shape[0] / 1000.0)
    borrada = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.addWeighted(img, 1.0 + peso, borrada, -peso, 0)


def _empurrar_branco(img: np.ndarray, limiar: int = BRANCO_LIMIAR) -> np.ndarray:
    """Pixels quase brancos viram branco puro: acaba com o cinza de fundo."""
    cinza = _para_cinza(img)
    mascara = cinza >= limiar
    saida = img.copy()
    saida[mascara] = 255
    return saida


def filtro_magico_pro(img: np.ndarray) -> np.ndarray:
    """Magico pro: cor viva, texto nitido, fundo branco. Para capas e gravuras."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 1. mesma limpeza de iluminacao do Melhorar
    saida = _achatar_iluminacao(img, _nivel_do_papel(img))
    saida = _balanco_de_branco(saida)

    # 2. CLAHE so no canal de luminosidade (L do LAB), para nao mexer no matiz
    lab = cv2.cvtColor(saida, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=CLAHE_GRADE)
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    saida = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # 3. cor mais viva
    saida = _realcar_saturacao(saida)

    # 4. texto mais nitido
    saida = _nitidez(saida)

    # 5. fundo branco de verdade
    return _empurrar_branco(saida)


def aplicar_filtro(
    img: np.ndarray, filtro: str, forca_preto: str = "normal"
) -> tuple[np.ndarray, bool]:
    """Aplica o filtro pedido.

    Devolve (imagem, monocromatica). monocromatica=True avisa o EscritorPDF
    para salvar a pagina em 1 bit.
    """
    try:
        if filtro == ORIGINAL:
            return img, False
        if filtro == PRETO_E_BRANCO:
            return filtro_preto_e_branco(img, forca=forca_preto), True
        if filtro == MELHORAR:
            return filtro_melhorar(img), False
        if filtro == MAGICO_PRO:
            return filtro_magico_pro(img), False
    except cv2.error as exc:
        raise ErroFiltro("Nao consegui limpar esta pagina.") from exc

    # filtro desconhecido: nao mexer e melhor que quebrar
    return img, False
