"""Endireitar folhas tortas (deskew).

Metodo do perfil de projecao: giramos a pagina em varios angulos e ficamos com
o que deixa as somas por linha mais "picudas". Quando o texto esta alinhado com
a horizontal, cada linha de texto vira um pico e cada entrelinha vira um vale,
o que da variancia alta. Torto, tudo borra e a variancia cai.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Limite de correcao. Acima disso quase sempre e erro de deteccao (uma
# ilustracao, uma tabela), nao pagina torta - e girar estragaria.
ANGULO_MAXIMO = 5.0

# Abaixo disso nao compensa girar: a interpolacao custaria mais qualidade do
# que o endireitamento traria.
ANGULO_MINIMO = 0.1

# Angulo acima do qual avisamos "esta pagina estava bem torta" (secao 4.3).
ANGULO_SUSPEITO = 3.0

# Altura de trabalho da deteccao. Nao precisa de resolucao: o que importa e o
# ritmo das linhas de texto, que sobrevive de sobra a 700 px.
ALTURA_ANALISE = 700

PASSO_GROSSO = 0.5
PASSO_FINO = 0.1

# Razao entre a melhor variancia e a mediana das variancias a partir da qual
# consideramos que achamos mesmo o alinhamento.
RAZAO_CONFIANTE = 1.6


@dataclass(frozen=True)
class Inclinacao:
    angulo: float       # graus; positivo = girar no sentido anti-horario
    confianca: float    # 0.0 a 1.0

    @property
    def vale_a_pena(self) -> bool:
        return abs(self.angulo) >= ANGULO_MINIMO

    @property
    def muito_torta(self) -> bool:
        return abs(self.angulo) >= ANGULO_SUSPEITO


def _preparar(img: np.ndarray) -> np.ndarray:
    """Reduz e binariza: pixels de texto viram 1, papel vira 0."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    altura = cinza.shape[0]
    if altura > ALTURA_ANALISE:
        escala = ALTURA_ANALISE / altura
        cinza = cv2.resize(
            cinza, (max(8, int(cinza.shape[1] * escala)), ALTURA_ANALISE),
            interpolation=cv2.INTER_AREA,
        )
    # Otsu global basta aqui: nao queremos qualidade, queremos onde ha tinta.
    _, binaria = cv2.threshold(cinza, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binaria.astype(np.float32)


def _pontuacao(binaria: np.ndarray, angulo: float) -> float:
    """Variancia das somas por linha depois de girar o angulo dado."""
    altura, largura = binaria.shape
    centro = (largura / 2.0, altura / 2.0)
    matriz = cv2.getRotationMatrix2D(centro, angulo, 1.0)
    girada = cv2.warpAffine(
        binaria, matriz, (largura, altura),
        flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0,
    )
    somas = girada.sum(axis=1)
    return float(somas.var())


def detectar_angulo(img: np.ndarray) -> Inclinacao:
    """Descobre o quanto a pagina esta torta.

    Vai em duas passadas (grossa e fina) para nao testar 101 angulos na mao.
    """
    binaria = _preparar(img)
    if binaria.sum() < 50:  # pagina praticamente em branco: nada para alinhar
        return Inclinacao(angulo=0.0, confianca=0.0)

    grossos = np.arange(-ANGULO_MAXIMO, ANGULO_MAXIMO + PASSO_GROSSO, PASSO_GROSSO)
    notas = np.array([_pontuacao(binaria, a) for a in grossos])
    melhor_grosso = float(grossos[int(np.argmax(notas))])

    finos = np.arange(
        max(-ANGULO_MAXIMO, melhor_grosso - PASSO_GROSSO),
        min(ANGULO_MAXIMO, melhor_grosso + PASSO_GROSSO) + PASSO_FINO,
        PASSO_FINO,
    )
    notas_finas = np.array([_pontuacao(binaria, a) for a in finos])
    angulo = float(finos[int(np.argmax(notas_finas))])

    # Confianca: um alinhamento real cria um pico bem destacado. Se todas as
    # rotacoes pontuam parecido, nao achamos alinhamento nenhum.
    mediana = float(np.median(notas))
    razao = (float(notas.max()) / mediana) if mediana > 0 else 1.0
    confianca = float(np.clip((razao - 1.0) / (RAZAO_CONFIANTE - 1.0), 0.0, 1.0))

    # Se o melhor angulo caiu na ponta da busca, a curva ainda estava subindo:
    # o alinhamento de verdade esta fora do que podemos corrigir. Acontece em
    # capa e pagina de ilustracao, que nao tem linha de texto nenhuma. Melhor
    # nao girar do que girar 5 graus a toa.
    if abs(abs(angulo) - ANGULO_MAXIMO) < PASSO_FINO / 2:
        return Inclinacao(angulo=0.0, confianca=0.0)

    if abs(angulo) > ANGULO_MAXIMO:
        return Inclinacao(angulo=0.0, confianca=0.0)
    return Inclinacao(angulo=angulo, confianca=confianca)


def rotacionar(img: np.ndarray, angulo: float, fundo: int = 255) -> np.ndarray:
    """Gira a imagem preenchendo o que sobra com branco.

    Mantem o mesmo tamanho de folha: o objetivo e reimprimir, entao todas as
    paginas precisam sair iguais.
    """
    if abs(angulo) < ANGULO_MINIMO:
        return img
    altura, largura = img.shape[:2]
    matriz = cv2.getRotationMatrix2D((largura / 2.0, altura / 2.0), angulo, 1.0)
    borda = fundo if img.ndim == 2 else (fundo, fundo, fundo)
    return cv2.warpAffine(
        img, matriz, (largura, altura),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=borda,
    )


def endireitar(img: np.ndarray) -> tuple[np.ndarray, Inclinacao]:
    """Detecta e corrige de uma vez. Devolve a imagem e o que foi detectado."""
    inclinacao = detectar_angulo(img)
    if not inclinacao.vale_a_pena:
        return img, inclinacao
    return rotacionar(img, inclinacao.angulo), inclinacao


def girar_90(img: np.ndarray, rotacao: int) -> np.ndarray:
    """Giro de 90 em 90 graus, pedido pelo usuario no botao 'girar'."""
    rotacao = rotacao % 360
    if rotacao == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if rotacao == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if rotacao == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img
