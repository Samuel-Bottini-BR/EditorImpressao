"""Os alertas: onde o programa avisa que pode ter errado.

E o coracao da ideia do aplicativo. O ScanTailor deixa tudo manual e cansa; o
CamScanner faz tudo sozinho e não avisa nada. Aqui o programa faz sozinho E diz
onde teve dúvida, para o usuario conferir 7 páginas em vez de 500.

Regra de calibragem: num livro bem escaneado, menos de 10% das páginas devem
ser marcadas. Se marcar tudo, o alerta vira ruido e o usuario para de olhar.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from core.dividir import Lombada
from core.endireitar import ANGULO_SUSPEITO, Inclinacao
from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO
from core.recortar import Recorte

# --- codigos dos alertas ----------------------------------------------------
COR = "cor"
LOMBADA_INCERTA = "lombada_incerta"
NAO_PARECE_DUPLA = "nao_parece_dupla"
MUITO_TORTA = "muito_torta"
ANGULO_SUSPEITO_ = "angulo_suspeito"
EM_BRANCO = "em_branco"
ESCURA_DEMAIS = "escura_demais"
APAGADA_DEMAIS = "apagada_demais"
CORTE_PEGOU_CONTEUDO = "corte_pegou_conteudo"
RESOLUCAO_BAIXA = "resolucao_baixa"
TAMANHO_DIFERENTE = "tamanho_diferente"


@dataclass(frozen=True)
class Alerta:
    """O texto que o usuario le e o atalho de correcao que oferecemos."""

    codigo: str
    titulo: str          # nome curto, para agrupar no painel
    mensagem: str        # frase completa, na faixa da pagina
    acao: str | None     # rotulo do botao de sugestao
    correcao: str | None # o que o botao faz (lido pela interface)


ALERTAS: dict[str, Alerta] = {
    COR: Alerta(
        COR, "Tem cor",
        "Esta página tem cor - o preto e branco vai perder a ilustração.",
        "usar Mágico pro nesta", "filtro:" + MAGICO_PRO,
    ),
    LOMBADA_INCERTA: Alerta(
        LOMBADA_INCERTA, "Lombada incerta",
        "Não tenho certeza de onde cortar. Confira a linha.",
        "aceitar o corte", "revisar",
    ),
    NAO_PARECE_DUPLA: Alerta(
        NAO_PARECE_DUPLA, "Não parece dupla",
        "Esta folha parece ter uma página só. Confirme se devo dividir.",
        "não dividir esta", "nao_dividir",
    ),
    MUITO_TORTA: Alerta(
        MUITO_TORTA, "Muito torta",
        "Esta página estava bem torta. Veja se ficou certa.",
        "está bom assim", "revisar",
    ),
    ANGULO_SUSPEITO_: Alerta(
        ANGULO_SUSPEITO_, "Alinhamento duvidoso",
        "Não consegui achar o alinhamento do texto direito.",
        "não endireitar esta", "angulo_zero",
    ),
    EM_BRANCO: Alerta(
        EM_BRANCO, "Parece em branco",
        "Esta página parece estar em branco. Quer apagar?",
        "apagar esta página", "apagar",
    ),
    ESCURA_DEMAIS: Alerta(
        ESCURA_DEMAIS, "Ficou escura",
        "Ficou muito escura. Tente mais fraco na força do preto.",
        "usar mais fraco", "forca:mais_fraco",
    ),
    APAGADA_DEMAIS: Alerta(
        APAGADA_DEMAIS, "Texto quase sumiu",
        "O texto quase sumiu. Tente mais escuro.",
        "usar mais escuro", "forca:mais_escuro",
    ),
    CORTE_PEGOU_CONTEUDO: Alerta(
        CORTE_PEGOU_CONTEUDO, "Corte encostou no texto",
        "O corte da borda pode ter pegado parte do texto.",
        "não cortar esta", "sem_recorte",
    ),
    RESOLUCAO_BAIXA: Alerta(
        RESOLUCAO_BAIXA, "Qualidade baixa",
        "Esta página foi escaneada em qualidade baixa. O resultado pode não ficar bom.",
        "está bom assim", "revisar",
    ),
    TAMANHO_DIFERENTE: Alerta(
        TAMANHO_DIFERENTE, "Tamanho diferente",
        "Esta folha tem tamanho diferente das outras.",
        "está bom assim", "revisar",
    ),
}


def descrever(codigo: str) -> Alerta:
    return ALERTAS.get(
        codigo, Alerta(codigo, codigo, "Confira esta página.", None, None)
    )


# --- limiares (calibrados no livro de teste) --------------------------------

# Cor - todos os valores abaixo saem de medição nos nove livros do acervo,
# não de chute. Ver detectar_cor.
PERCENTIL_DO_PAPEL = 85     # a partir de que brilho um pixel conta como papel
CORRECAO_MAXIMA = 2.5       # teto do desconto da dominante, por canal
SATURACAO_DE_TINTA = 90     # acima disso o pixel e tinta colorida, não mancha
FRACAO_COLORIDA_MIN = 0.05  # 5% dos pixels: separa xilogravura de iluminura
SATURACAO_MEDIA_MIN = 28.0  # rede de segurança para página colorida por inteiro

CONFIANCA_LOMBADA_MIN = 0.5
CONFIANCA_ANGULO_MIN = 0.35

# Pagina em branco: quase nada de tinta depois de binarizar.
FRACAO_TINTA_BRANCA = 0.002

FRACAO_PRETO_ESCURA = 0.40
FRACAO_PRETO_APAGADA = 0.01

DPI_BAIXO = 150
TAMANHO_DIFERENTE_TOLERANCIA = 0.10


def _neutralizar_o_papel(img: np.ndarray) -> np.ndarray:
    """Tira do quadro a cor do PROPRIO papel, antes de procurar cor de tinta.

    Papel envelhecido e amarelo, e amarelo tem saturação alta. Sem tirar isso,
    qualquer livro velho de texto preto e lido como colorido - foi o que
    aconteceu com os nove livros do acervo, inclusive os de texto puro.

    A dominante e medida nos pixels claros (o papel) e descontada dos tres
    canais. O que sobrar de cor depois disso e tinta de verdade.
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    papel = cinza >= np.percentile(cinza, PERCENTIL_DO_PAPEL)
    if papel.sum() < 100:
        return img

    medias = [float(img[:, :, c][papel].mean()) for c in range(3)]
    geral = sum(medias) / 3.0
    if geral < 1:
        return img

    saida = img.astype(np.float32)
    for canal in range(3):
        if medias[canal] >= 1:
            fator = geral / medias[canal]
            saida[:, :, canal] *= min(max(fator, 1 / CORRECAO_MAXIMA), CORRECAO_MAXIMA)
    return np.clip(saida, 0, 255).astype(np.uint8)


def detectar_cor(img: np.ndarray) -> tuple[bool, float]:
    """Diz se a página tem TINTA colorida e devolve a saturação corrigida.

    Duas decisões, as duas tiradas de medição no acervo do instituto:

    1. medir depois de neutralizar o papel (ver acima);
    2. contar a FRAÇÃO de pixels fortemente coloridos, não a média. Uma
       iluminura e cor concentrada numa mancha; papel manchado e cor fraca
       espalhada pela folha inteira. A média confunde as duas, a fração não.

    Nos livros medidos: texto puro fica em ~1% de pixels coloridos, xilogravura
    em papel manchado 2-4%, página com rubrica vermelha 3-7%, iluminura 25-36%.
    O limiar fica baixo de proposito: perder a cor de uma miniatura estraga a
    página, enquanto um alerta a mais só custa um olhar.
    """
    if img.ndim == 2:
        return False, 0.0

    limpa = _neutralizar_o_papel(img)
    saturacao = cv2.cvtColor(limpa, cv2.COLOR_BGR2HSV)[:, :, 1]

    media = float(saturacao.mean())
    fracao_forte = float((saturacao > SATURACAO_DE_TINTA).mean())

    tem_cor = fracao_forte >= FRACAO_COLORIDA_MIN or media >= SATURACAO_MEDIA_MIN
    return tem_cor, media


def fracao_de_tinta(img: np.ndarray) -> float:
    """Fracao de pixels escuros. Serve para 'em branco' e 'escura demais'."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return float((binaria > 0).mean())


def dpi_estimado(largura_px: int, largura_pt: float) -> float:
    """Quantos pontos por polegada essa página realmente tem."""
    if largura_pt <= 0:
        return 0.0
    return largura_px / (largura_pt / 72.0)


def analisar_folha(
    img: np.ndarray,
    lombada: Lombada,
    inclinacao: Inclinacao,
    recorte: Recorte,
    vai_dividir: bool,
    vai_endireitar: bool,
    vai_cortar: bool,
    dpi_real: float | None = None,
    tamanho_fora_do_padrao: bool = False,
) -> list[str]:
    """Alertas da FOLHA de entrada: corte, ângulo, recorte, tamanho."""
    alertas: list[str] = []

    if vai_dividir:
        if not lombada.e_paisagem:
            alertas.append(NAO_PARECE_DUPLA)
        elif lombada.confianca < CONFIANCA_LOMBADA_MIN or not lombada.centralizada:
            alertas.append(LOMBADA_INCERTA)

    if vai_endireitar:
        if inclinacao.muito_torta:
            alertas.append(MUITO_TORTA)
        elif inclinacao.vale_a_pena and inclinacao.confianca < CONFIANCA_ANGULO_MIN:
            alertas.append(ANGULO_SUSPEITO_)

    if vai_cortar and recorte.encostou_no_conteudo:
        alertas.append(CORTE_PEGOU_CONTEUDO)

    if dpi_real is not None and 0 < dpi_real < DPI_BAIXO:
        alertas.append(RESOLUCAO_BAIXA)

    if tamanho_fora_do_padrao:
        alertas.append(TAMANHO_DIFERENTE)

    return alertas


def analisar_pagina(img: np.ndarray, filtro: str) -> tuple[list[str], bool]:
    """Alertas da PAGINA de saida: cor, em branco, escura ou apagada demais.

    Devolve (alertas, tem_cor).
    """
    alertas: list[str] = []
    tem_cor, _ = detectar_cor(img)

    tinta = fracao_de_tinta(img)
    if tinta < FRACAO_TINTA_BRANCA:
        alertas.append(EM_BRANCO)
        return alertas, tem_cor  # numa pagina em branco os outros nao fazem sentido

    if tem_cor and filtro == PRETO_E_BRANCO:
        alertas.append(COR)

    return alertas, tem_cor


def analisar_resultado(img_filtrada: np.ndarray, filtro: str) -> list[str]:
    """Alertas que só aparecem DEPOIS de aplicar o filtro.

    Só valem para o preto e branco: e o único filtro em que o texto pode
    literalmente sumir ou a página virar uma mancha preta.
    """
    if filtro != PRETO_E_BRANCO:
        return []

    cinza = img_filtrada if img_filtrada.ndim == 2 else cv2.cvtColor(
        img_filtrada, cv2.COLOR_BGR2GRAY
    )
    fracao_preta = float((cinza < 128).mean())

    if fracao_preta > FRACAO_PRETO_ESCURA:
        return [ESCURA_DEMAIS]
    if fracao_preta < FRACAO_PRETO_APAGADA:
        return [APAGADA_DEMAIS]
    return []


def sugerir_filtro(tem_cor: bool, filtro_padrao: str) -> str:
    """Qual filtro faz sentido para esta página, dado o padrão escolhido."""
    if tem_cor and filtro_padrao == PRETO_E_BRANCO:
        return MAGICO_PRO
    return filtro_padrao


def tamanhos_fora_do_padrao(tamanhos: list[tuple[float, float]]) -> list[bool]:
    """Marca as folhas cujo tamanho destoa das demais.

    Compara com a mediana, não com a média: uma única folha gigante não pode
    arrastar a referência e fazer todo o resto parecer diferente.
    """
    if len(tamanhos) < 3:
        return [False] * len(tamanhos)

    larguras = np.array([t[0] for t in tamanhos], dtype=np.float32)
    alturas = np.array([t[1] for t in tamanhos], dtype=np.float32)
    ref_l, ref_a = float(np.median(larguras)), float(np.median(alturas))
    if ref_l <= 0 or ref_a <= 0:
        return [False] * len(tamanhos)

    fora = (np.abs(larguras - ref_l) / ref_l > TAMANHO_DIFERENTE_TOLERANCIA) | (
        np.abs(alturas - ref_a) / ref_a > TAMANHO_DIFERENTE_TOLERANCIA
    )
    return [bool(v) for v in fora]


# A partir de que fração de páginas um alerta deixa de ser exceção e vira
# característica do livro. Acima disso ele sai das páginas e vira observação.
FRACAO_VIRA_OBSERVACAO = 0.7

# Como cada alerta se lê quando vale para o livro todo, e não para uma página.
OBSERVACOES = {
    NAO_PARECE_DUPLA: "este livro tem uma página por folha, não duas",
    RESOLUCAO_BAIXA: "o livro inteiro foi escaneado em qualidade baixa",
    COR: "o livro inteiro é colorido",
    TAMANHO_DIFERENTE: "as folhas deste livro têm tamanhos variados",
    LOMBADA_INCERTA: "a lombada é difícil de achar neste livro",
    EM_BRANCO: "quase todas as páginas parecem estar em branco",
}


def separar_observacoes(
    listas_de_alertas: list[list[str]], limiar: float = FRACAO_VIRA_OBSERVACAO
) -> tuple[list[str], set[str]]:
    """Tira das páginas os alertas que valem para o livro inteiro.

    Marcar 500 páginas porque TODAS são coloridas não ajuda ninguém: o usuário
    não vai conferir uma a uma, e o contador perde o sentido justamente onde
    deveria servir. Um fato do livro inteiro se diz uma vez só.

    Devolve (observações em português, códigos que devem sair das páginas).
    """
    total = len(listas_de_alertas)
    if total < 4:      # livro curto demais para tirar conclusão
        return [], set()

    contagem: dict[str, int] = {}
    for alertas in listas_de_alertas:
        for codigo in set(alertas):
            contagem[codigo] = contagem.get(codigo, 0) + 1

    observacoes: list[str] = []
    para_remover: set[str] = set()
    for codigo, quantas in sorted(contagem.items(), key=lambda kv: -kv[1]):
        if quantas / total < limiar or codigo not in OBSERVACOES:
            continue
        para_remover.add(codigo)
        observacoes.append(OBSERVACOES[codigo])

    return observacoes, para_remover


def agrupar_por_tipo(
    itens: list[tuple[int, list[str]]]
) -> dict[str, list[int]]:
    """Monta o painel 'Páginas para revisar', agrupado por tipo de alerta.

    itens e uma lista de (numero_da_pagina, codigos_de_alerta).
    """
    grupos: dict[str, list[int]] = {}
    for numero, codigos in itens:
        for codigo in codigos:
            grupos.setdefault(codigo, []).append(numero)
    return grupos
