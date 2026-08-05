"""Regua do Editor de Impressao: mede o programa em numeros, sem opiniao.

Roda sozinho sobre o acervo e grava relatorios/linha-de-base.json e .md.

Para que serve
--------------
Antes de mexer em qualquer filtro precisamos saber como o programa esta HOJE.
Sem isso, toda mudanca parece boa: quem mexeu acha que melhorou. Aqui cada
pagina vira um punhado de numeros, e a comparacao entre o antes e o depois
deixa de ser conversa.

Como usar
---------
    .venv\\Scripts\\python.exe avaliar.py
    .venv\\Scripts\\python.exe avaliar.py --paginas 6 --saida relatorios
    .venv\\Scripts\\python.exe avaliar.py --rotulo depois-do-ajuste
    .venv\\Scripts\\python.exe avaliar.py --comparar relatorios/linha-de-base.json

Os PDFs de entrada sao abertos SO PARA LEITURA. Nada e gravado dentro da pasta
do acervo.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import statistics
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# O projeto importa a si mesmo por caminho relativo a raiz.
RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core import analise  # noqa: E402
from core.endireitar import detectar_angulo  # noqa: E402
from core.filtros import (  # noqa: E402
    FILTROS,
    MAGICO_PRO,
    MELHORAR,
    NOMES_AMIGAVEIS,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
    doxapy_disponivel,
)
from core.pdf_io import (  # noqa: E402
    EscritorPDF,
    ErroPDF,
    abrir_pdf,
    info_paginas,
    pagina_para_array,
)
from core.pipeline import DPI_ANALISE, analisar_projeto, preparar_metade  # noqa: E402
from modelos import Projeto  # noqa: E402

# ---------------------------------------------------------------------------
# Onde ficam as coisas. Caminhos de disco sem acento, de proposito.
# ---------------------------------------------------------------------------

NOME_DO_ACERVO = "BIBLIOTECA DO FIM DOS TEMPOS"
PASTA_RELATORIOS = RAIZ / "relatorios"
PASTA_SAIDA = RAIZ / "saida-avaliacao"

# Quantas paginas de cada livro entram na medida de qualidade. Poucas paginas
# medidas a fundo valem mais que o livro inteiro medido por cima, e o conjunto
# e sempre o MESMO entre uma rodada e outra - senao a comparacao nao vale.
PAGINAS_POR_LIVRO = 7

# DPI da medicao. 300 e o que o Kaique usa para imprimir; medir em outro valor
# mediria um programa que ninguem usa.
DPI_MEDIDA = 300

# Filtros que entram na medida de qualidade.
FILTROS_MEDIDOS = (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO)

# --- limites usados para dizer "esta pagina saiu pior que o original" -------
#
# Cada um responde a uma queixa concreta do Kaique, anotada nos .txt do acervo.
# Sao propositalmente tolerantes: a ideia e pegar estrago de verdade, nao
# variacao de medida.

# Perder mais que isto dos vazios internos das letras significa que o "o" e o
# "e" entupiram. E o defeito mais grave que existe aqui: letra entupida e
# letra perdida, e nao ha ajuste de impressora que traga de volta.
QUEDA_VAZIOS_MAXIMA = 0.25

# O fundo nao pode escurecer. A queixa do amarelado virando cinza e exatamente
# isto: o papel sai mais escuro do que entrou.
QUEDA_FUNDO_MAXIMA = 2.0

# O fundo nao pode ficar mais sujo do que entrou.
AUMENTO_RUIDO_MAXIMO = 1.5

# Faixa saudavel da transicao na borda da letra, em pixels.
#   abaixo de 0,7  -> escada (o serrilhado que o Kaique chama de "pixelado")
#   acima de 3,0   -> borrado
TRANSICAO_BOA_MIN, TRANSICAO_BOA_MAX = 0.7, 3.0

# O traco nao pode sumir: perder mais de um terco da espessura e texto fino
# demais para imprimir.
QUEDA_ESPESSURA_MAXIMA = 0.34

# Metas da Etapa 5, para o relatorio ja dizer se passou ou nao.
METAS = {
    "abrir_programa_s": 10.0,
    "primeiras_miniaturas_s": 5.0,
    "analise_500_paginas_s": 180.0,
    "exportar_500_paginas_300dpi_s": 1200.0,
    "pico_memoria_mb": 2048.0,
}


class Cronometro:
    """Mede tempo de parede de um trecho."""

    def __init__(self) -> None:
        self.segundos = 0.0

    def __enter__(self) -> "Cronometro":
        self._inicio = time.perf_counter()
        return self

    def __exit__(self, *_exc) -> None:
        self.segundos = time.perf_counter() - self._inicio


class VigiaDeMemoria:
    """Acompanha o pico de memoria do processo enquanto algo roda.

    O pico e o numero que importa: a maquina do Kaique tem 8 GB e o programa
    nao pode crescer junto com o tamanho do livro.
    """

    def __init__(self, intervalo: float = 0.05) -> None:
        self.intervalo = intervalo
        self.pico_mb = 0.0
        self._rodando = False
        self._thread: threading.Thread | None = None
        try:
            import psutil

            self._proc = psutil.Process(os.getpid())
        except Exception:  # noqa: BLE001 - sem psutil a medida some, o resto continua
            self._proc = None

    def _laco(self) -> None:
        while self._rodando and self._proc is not None:
            try:
                mb = self._proc.memory_info().rss / (1024 * 1024)
            except Exception:  # noqa: BLE001
                break
            self.pico_mb = max(self.pico_mb, mb)
            time.sleep(self.intervalo)

    def __enter__(self) -> "VigiaDeMemoria":
        if self._proc is not None:
            self._rodando = True
            self._thread = threading.Thread(target=self._laco, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, *_exc) -> None:
        self._rodando = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)


# ---------------------------------------------------------------------------
# As medidas de qualidade de imagem
# ---------------------------------------------------------------------------

# Contraste minimo, do percentil 1 ao 99, para haver tinta a separar. Medido no
# acervo: folha em branco fica entre 14 e 55, pagina com conteudo entre 167 e
# 193. O corte em 80 fica no vao.
CONTRASTE_DE_FOLHA_ESCRITA = 80


def _cinza(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _mascara_de_tinta(cinza: np.ndarray) -> np.ndarray:
    """Separa tinta de papel so para MEDIR (nunca para produzir imagem).

    Otsu global e proposital: e a mesma regra para todos os filtros, entao a
    comparacao entre eles e justa. Um separador esperto por filtro mediria
    coisas diferentes em cada um.

    Mas Otsu SEMPRE parte a imagem em dois, mesmo quando nao ha nada para
    partir: numa folha em branco ele corta o proprio grao do scanner ao meio e
    declara 38% de tinta. A pagina virava "ilustracao" no relatorio, e limpar
    aquele grao - que e o certo - aparecia como "a borda das letras virou
    degrau", com uma rampa de 4,59 pixels que nunca existiu. Antes de separar,
    portanto, ha uma pergunta mais simples: existe contraste aqui?
    """
    espalhamento = float(np.percentile(cinza, 99) - np.percentile(cinza, 1))
    if espalhamento < CONTRASTE_DE_FOLHA_ESCRITA:
        return np.zeros_like(cinza)

    _, mascara = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mascara


def espessura_do_traco(tinta: np.ndarray) -> float:
    """Espessura media do traco da tinta, em pixels.

    Mede a distancia do meio do traco ate a borda dele e dobra. Traco que
    afina demais desaparece na impressao; traco que engorda entope as letras.
    """
    if not tinta.any():
        return 0.0
    try:
        from skimage.morphology import skeletonize
    except Exception:  # noqa: BLE001
        return 0.0

    distancia = cv2.distanceTransform(tinta, cv2.DIST_L2, 5)
    esqueleto = skeletonize(tinta > 0)
    if not esqueleto.any():
        return 0.0
    return float(2.0 * distancia[esqueleto].mean())


# Faixa de tamanho, em pixels a 300 DPI, do que pode ser o miolo de uma letra.
# O contra-forma de um "o" de corpo 10 a 300 DPI tem por volta de 20 a 200 px.
# A folga e generosa para caber capitular grande e nota de rodape miuda, mas
# fecha a porta para a textura de uma xilogravura, que gera milhares de vaos
# minusculos e nao tem nada a ver com letra entupida.
VAZIO_AREA_MIN_300DPI = 4
VAZIO_AREA_MAX_300DPI = 900


def vazios_internos(tinta: np.ndarray, dpi: int = 300) -> tuple[int, float]:
    """Conta os buracos fechados dentro das letras: o miolo do "o", do "e", do "a".

    Quando um filtro engrossa demais o traco, esses buracos entopem e a letra
    vira uma bolha. Contar quantos sobraram e a forma mais direta de flagrar
    isso. Devolve (quantidade, quantidade por mil pixels de tinta).

    So conta vao de tamanho compativel com letra: sem esse limite, uma pagina
    de gravura devolvia milhares de "vazios" que eram textura do desenho, e o
    numero perdia o sentido.
    """
    if not tinta.any():
        return 0, 0.0

    papel = cv2.bitwise_not(tinta)
    num, _rotulos, stats, _ = cv2.connectedComponentsWithStats(papel, connectivity=4)
    if num <= 1:
        return 0, 0.0

    escala = (dpi / 300.0) ** 2
    area_min = max(3, int(VAZIO_AREA_MIN_300DPI * escala))
    area_max = int(VAZIO_AREA_MAX_300DPI * escala)

    altura, largura = tinta.shape[:2]
    buracos = 0
    for i in range(1, num):
        x, y, w, h, area = (
            stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP],
            stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT],
            stats[i, cv2.CC_STAT_AREA],
        )
        # encostou na moldura => e o papel de fora, nao um buraco de letra
        if x == 0 or y == 0 or x + w >= largura or y + h >= altura:
            continue
        if not (area_min <= area <= area_max):
            continue
        buracos += 1

    tinta_px = int((tinta > 0).sum())
    por_mil = (buracos * 1000.0 / tinta_px) if tinta_px else 0.0
    return buracos, float(por_mil)


def regiao_de_papel(tinta: np.ndarray) -> np.ndarray:
    """Onde e papel de verdade: longe de qualquer tinta.

    Calculada UMA VEZ sobre o original e reaproveitada em todos os filtros da
    mesma pagina. Foi o conserto mais importante desta regua: recalculando a
    regiao em cada filtro, "fundo" e "ruido" eram medidos em pedacos
    diferentes da folha e a comparacao entre filtros nao queria dizer nada.
    """
    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    return cv2.dilate(tinta, nucleo, iterations=1) == 0


def nivel_do_fundo(cinza: np.ndarray, papel: np.ndarray) -> float:
    """Quao claro esta o papel, de 0 a 255. O alvo e 255: branco de verdade."""
    valores = cinza[papel]
    if valores.size == 0:
        return 0.0
    return float(valores.mean())


def ruido_do_fundo(cinza: np.ndarray, papel: np.ndarray) -> float:
    """Sujeira do papel: o quanto o fundo varia onde ele deveria ser liso.

    Olha so as regioes longe da tinta, para nao medir a borda das letras como
    se fosse sujeira.
    """
    so_papel = papel
    if so_papel.sum() < 100:
        return 0.0

    f = cinza.astype(np.float32)
    media = cv2.boxFilter(f, -1, (7, 7), normalize=True)
    media_quadrados = cv2.boxFilter(f * f, -1, (7, 7), normalize=True)
    variancia = np.clip(media_quadrados - media * media, 0, None)
    desvio_local = np.sqrt(variancia)
    return float(np.median(desvio_local[so_papel]))


# Ate onde da borda da letra ainda pode ser rampa. Alem disto e papel, e papel
# sujo nao e rampa de letra.
RAIO_DA_RAMPA = 4


def largura_da_transicao(cinza: np.ndarray, tinta: np.ndarray) -> float:
    """Largura da rampa entre a tinta e o papel, em pixels.

    E o numero por tras da queixa de "letra pixelada". Uma borda saudavel tem
    de 1 a 2 pixels de rampa: de longe a letra parece lisa. Perto de zero a
    borda vira degrau de escada (o serrilhado). Acima de 3 a letra borra.

    Conta os pixels que estao no meio do caminho entre o preto e o branco e
    divide pelo comprimento do contorno das letras.

    So conta perto do contorno. A primeira versao contava em toda a pagina, e
    papel ruidoso - cheio de pixels de tom intermediario - inflava o numero:
    uma folha suja aparecia com a borda mais suave que uma folha limpa. Isso
    contaminava exatamente a comparacao que este numero existe para fazer.
    """
    if not tinta.any():
        return 0.0

    escuro = float(np.percentile(cinza[tinta > 0], 50))
    claro = float(np.percentile(cinza[tinta == 0], 50)) if (tinta == 0).any() else 255.0
    faixa = claro - escuro
    if faixa < 10:
        return 0.0

    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    contorno = cv2.morphologyEx(tinta, cv2.MORPH_GRADIENT, nucleo)
    comprimento = int((contorno > 0).sum())
    if comprimento == 0:
        return 0.0

    lado = 2 * RAIO_DA_RAMPA + 1
    perto_da_letra = cv2.dilate(
        contorno, cv2.getStructuringElement(cv2.MORPH_RECT, (lado, lado))
    ) > 0

    baixo = escuro + 0.2 * faixa
    alto = escuro + 0.8 * faixa
    meio_do_caminho = int(
        ((cinza > baixo) & (cinza < alto) & perto_da_letra).sum()
    )
    return float(meio_do_caminho / comprimento)


def nitidez(cinza: np.ndarray) -> float:
    """Nitidez geral: variancia do laplaciano. Quanto maior, mais definido."""
    return float(cv2.Laplacian(cinza, cv2.CV_64F).var())


def medir_imagem(
    img: np.ndarray, papel_ref: np.ndarray | None = None, dpi: int = 300
) -> dict[str, float]:
    """Todas as medidas de qualidade de uma imagem so.

    papel_ref e a regiao de papel tirada do ORIGINAL desta mesma pagina. Passar
    sempre a mesma regiao e o que torna o "antes e depois" comparavel.
    """
    cinza = _cinza(img)
    tinta = _mascara_de_tinta(cinza)
    papel = papel_ref if papel_ref is not None else regiao_de_papel(tinta)
    buracos, buracos_por_mil = vazios_internos(tinta, dpi=dpi)
    return {
        "espessura_traco_px": round(espessura_do_traco(tinta), 3),
        "vazios_internos": buracos,
        "vazios_por_mil_tinta": round(buracos_por_mil, 4),
        "nivel_fundo": round(nivel_do_fundo(cinza, papel), 2),
        "ruido_fundo": round(ruido_do_fundo(cinza, papel), 3),
        "transicao_borda_px": round(largura_da_transicao(cinza, tinta), 3),
        "nitidez": round(nitidez(cinza), 1),
        "fracao_tinta": round(float((tinta > 0).mean()), 5),
    }


# ---------------------------------------------------------------------------
# "Esta pagina saiu pior que o original?"
# ---------------------------------------------------------------------------

# Acima desta fracao de tinta a pagina nao e texto: e gravura, iluminura ou
# mancha de pagina cheia. Cobrar dela os mesmos numeros que se cobra de uma
# pagina de texto nao faz sentido - o Preto e branco JOGA FORA o meio-tom de
# uma xilogravura de proposito, e isso nao e defeito.
FRACAO_TINTA_DE_ILUSTRACAO = 0.25

# Abaixo desta fracao de tinta nao ha letra nenhuma na pagina: e folha em
# branco, guarda ou verso limpo. Cobrar dela "borda de letra" mede ficcao - a
# mascara de tinta pega grao de scanner, e a rampa medida na pagina 446 da
# Rhetorica dava 4,59 pixels de "borda" que nao existe. Limpar esse grao, que e
# o certo, aparecia como defeito.
FRACAO_TINTA_DE_FOLHA_VAZIA = 0.01

TEXTO, ILUSTRACAO, COLORIDA, VAZIA = "texto", "ilustracao", "colorida", "vazia"


# Quanto da folha o detector precisa marcar como gravura, e quao pouco como
# letra, para a pagina contar como desenho de ponta a ponta.
SO_DESENHO_GRAVURA_MIN = 0.98
SO_DESENHO_LETRA_MAX = 0.01


def e_so_desenho(selecao, altura: int, largura: int) -> bool:
    """A pagina inteira e desenho, sem uma linha de texto?

    A classificacao por fracao de tinta e cor tem um buraco: a pagina 199 do
    Catecismo e uma estampa colorida de pagina inteira, sem uma letra, e caia
    como TEXTO. A tinta dela e so 7% - a estampa e clara - e o "tem cor" saiu
    falso porque a analise roda a 150 DPI e ali a fracao de pixels coloridos
    da 0,0499 contra o limiar de 0,05; medida a 300 DPI a mesma pagina da
    0,0500 e sai como colorida. Decisao na navalha.

    O resultado era a regua cobrar dela os vazios internos das letras e reprovar
    os tres filtros por "as letras entupiram" - numa pagina onde nao ha letra
    nenhuma. Os filtros estavam certos: o Preto e branco preservou a estampa,
    que e o que se espera.

    O detector de regioes ja sabia a resposta, e a regua ja o tinha em maos:
    marcou 100% da pagina como gravura e 0% como letra. Aqui isso passa a valer
    mais que a conta de tinta e cor.

    O limite e proposital de apertado - a folha INTEIRA marcada como desenho e
    nada como letra. Se o detector errar e marcar uma pagina de texto assim, a
    regua deixa de cobrar letra onde deveria; por isso as paginas reclassificadas
    saem nomeadas no relatorio, e nao caladas.
    """
    from core.selecao import GRAVURA, LETRA

    if selecao is None or len(selecao) == 0:
        return False
    gravura = float(selecao.mascara(altura, largura, GRAVURA).mean())
    letra = float(selecao.mascara(altura, largura, LETRA).mean())
    return gravura >= SO_DESENHO_GRAVURA_MIN and letra <= SO_DESENHO_LETRA_MAX


def classificar_pagina(fracao_tinta: float, tem_cor: bool) -> str:
    """Que tipo de pagina e esta, para saber o que cobrar dela.

    A classificacao sai sempre do ORIGINAL, nunca do resultado filtrado: e o
    conteudo que decide o que se pode exigir, nao o efeito aplicado.
    """
    if fracao_tinta < FRACAO_TINTA_DE_FOLHA_VAZIA:
        return VAZIA
    if fracao_tinta > FRACAO_TINTA_DE_ILUSTRACAO:
        return ILUSTRACAO
    if tem_cor:
        return COLORIDA
    return TEXTO


def comparar_com_original(
    medidas: dict[str, float], base: dict[str, float], filtro: str,
    classe: str = TEXTO,
) -> list[str]:
    """Lista, em portugues, o que piorou nesta pagina em relacao ao original.

    Lista vazia = a pagina nao piorou. O criterio de aceitacao do projeto exige
    que essa lista esteja vazia em TODAS as paginas de TODOS os livros.

    O que se cobra depende do tipo de pagina. Numa pagina de TEXTO cobramos
    tudo: letra nao pode entupir, traco nao pode sumir, borda nao pode
    serrilhar. Numa GRAVURA nao cobramos espessura nem vazio, porque reduzir
    uma gravura a preto e branco puro descarta meio-tom por definicao - e o que
    o filtro existe para fazer. Em toda pagina, de qualquer tipo, o fundo nunca
    pode escurecer nem sujar: isso e estrago em qualquer conteudo.
    """
    motivos: list[str] = []
    pagina_de_texto = classe == TEXTO
    # Numa folha vazia nao ha letra a medir. O que se cobra dela e so nao
    # escurecer e nao sujar - ver FRACAO_TINTA_DE_FOLHA_VAZIA.
    tem_letra = classe != VAZIA

    # 1. letras entupidas (so em pagina de texto)
    antes = base.get("vazios_internos", 0)
    depois = medidas.get("vazios_internos", 0)
    if pagina_de_texto and antes >= 20:  # so vale comparar se havia o que perder
        queda = (antes - depois) / antes
        if queda > QUEDA_VAZIOS_MAXIMA:
            motivos.append(
                f"as letras entupiram: sobraram {depois} vazios internos de {antes} "
                f"({queda * 100:.0f}% a menos)"
            )

    # 2. fundo escureceu
    if medidas.get("nivel_fundo", 0) < base.get("nivel_fundo", 0) - QUEDA_FUNDO_MAXIMA:
        motivos.append(
            f"o fundo escureceu: passou de {base['nivel_fundo']:.0f} para "
            f"{medidas['nivel_fundo']:.0f} numa escala em que 255 e branco"
        )

    # 3. fundo mais sujo
    if medidas.get("ruido_fundo", 0) > base.get("ruido_fundo", 0) + AUMENTO_RUIDO_MAXIMO:
        motivos.append(
            f"o fundo ficou mais sujo: ruido subiu de {base['ruido_fundo']:.1f} "
            f"para {medidas['ruido_fundo']:.1f}"
        )

    # 4. traco sumindo (so em pagina de texto)
    esp_antes = base.get("espessura_traco_px", 0.0)
    esp_depois = medidas.get("espessura_traco_px", 0.0)
    if pagina_de_texto and esp_antes > 0.5:
        queda = (esp_antes - esp_depois) / esp_antes
        if queda > QUEDA_ESPESSURA_MAXIMA:
            motivos.append(
                f"o traco afinou demais: de {esp_antes:.2f} para {esp_depois:.2f} pixels "
                f"({queda * 100:.0f}% a menos)"
            )

    # 5. borda serrilhada ou borrada
    # O Preto e branco e 1 bit por definicao: cobrar rampa dele nao faz sentido.
    if filtro != PRETO_E_BRANCO and tem_letra:
        t = medidas.get("transicao_borda_px", 0.0)
        t_base = base.get("transicao_borda_px", 0.0)
        if t < TRANSICAO_BOA_MIN <= t_base:
            motivos.append(
                f"a borda das letras virou degrau (serrilhado): a rampa caiu de "
                f"{t_base:.2f} para {t:.2f} pixels"
            )
        elif t > TRANSICAO_BOA_MAX and t > t_base * 1.3:
            motivos.append(
                f"a borda das letras borrou: a rampa subiu de {t_base:.2f} para "
                f"{t:.2f} pixels"
            )

    return motivos


# ---------------------------------------------------------------------------
# Escolha das paginas medidas
# ---------------------------------------------------------------------------

def escolher_paginas(projeto: Projeto, quantas: int) -> list[int]:
    """Escolhe quais paginas do livro entram na medida.

    Precisa ser DETERMINISTICO: a mesma escolha em toda rodada, senao o
    "antes" e o "depois" mediriam paginas diferentes e a comparacao nao valeria
    nada. Pega o comeco, o meio e o fim, e reserva vagas para os casos dificeis
    que o Kaique reclamou: pagina colorida, pagina em branco e pagina com
    mancha do verso.
    """
    ativas = [p for p in projeto.paginas if not p.apagada]
    if not ativas:
        return []
    total = len(ativas)

    escolhidas: list[int] = []

    def juntar(indice: int) -> None:
        if 0 <= indice < total and ativas[indice].indice not in escolhidas:
            escolhidas.append(ativas[indice].indice)

    # casos dificeis primeiro, para nao ficarem de fora quando quantas e pequeno
    coloridas = [p.indice for p in ativas if p.tem_cor]
    em_branco = [p.indice for p in ativas if analise.EM_BRANCO in p.alertas]
    if coloridas:
        escolhidas.append(coloridas[0])
    if em_branco and em_branco[0] not in escolhidas:
        escolhidas.append(em_branco[0])

    # primeira, ultima e um leque no meio
    juntar(0)
    juntar(total - 1)
    faltam = max(0, quantas - len(escolhidas))
    if faltam:
        passo = max(1, total // (faltam + 1))
        for n in range(1, faltam + 1):
            juntar(min(total - 1, n * passo))

    return sorted(escolhidas)[:quantas]


# ---------------------------------------------------------------------------
# Medicao de um livro
# ---------------------------------------------------------------------------

@dataclass
class ResultadoLivro:
    arquivo: str
    nome: str
    tamanho_mb: float
    folhas: int = 0
    paginas: int = 0
    erro: str = ""
    tempo_analise_s: float = 0.0
    tempo_por_folha_analise_s: float = 0.0
    tempo_export_s: float = 0.0
    tempo_por_pagina_export_s: float = 0.0
    pico_memoria_mb: float = 0.0
    pdf_saida_mb: float = 0.0
    pdf_saida_kb_por_pagina: float = 0.0
    paginas_medidas: list[int] = field(default_factory=list)
    alertas: dict[str, int] = field(default_factory=dict)
    observacoes: list[str] = field(default_factory=list)
    medidas: list[dict[str, Any]] = field(default_factory=list)
    geometria: dict[str, Any] = field(default_factory=dict)
    piores_que_original: list[dict[str, Any]] = field(default_factory=list)
    # Paginas que a classificacao chamou de texto e o detector mostrou serem
    # desenho de ponta a ponta. Saem nomeadas no relatorio de proposito: e onde
    # a regua deixa de cobrar letra, e um erro do detector tem de aparecer.
    reclassificadas: list[int] = field(default_factory=list)


def avaliar_livro(caminho: Path, quantas_paginas: int, dpi: int) -> ResultadoLivro:
    """Mede um livro inteiro. Nunca escreve nada dentro da pasta do acervo."""
    resultado = ResultadoLivro(
        arquivo=caminho.name,
        nome=caminho.stem,
        tamanho_mb=round(caminho.stat().st_size / (1024 * 1024), 2),
    )

    projeto = Projeto(
        caminho_entrada=str(caminho),
        nome=caminho.stem,
        caminho_saida=str(PASTA_SAIDA / f"{_sem_acento(caminho.stem)}.pdf"),
        qualidade_dpi=dpi,
    )

    # --- fase 1: analisar o livro inteiro ---------------------------------
    try:
        with VigiaDeMemoria() as vigia, Cronometro() as relogio:
            analisar_projeto(projeto)
        resultado.tempo_analise_s = round(relogio.segundos, 2)
        resultado.pico_memoria_mb = round(vigia.pico_mb, 1)
    except ErroPDF as exc:
        resultado.erro = str(exc)
        return resultado
    except Exception as exc:  # noqa: BLE001 - um livro quebrado nao derruba a bateria
        resultado.erro = f"{type(exc).__name__}: {exc}"
        return resultado

    resultado.folhas = len(projeto.folhas)
    resultado.paginas = len(projeto.paginas)
    if resultado.folhas:
        resultado.tempo_por_folha_analise_s = round(
            resultado.tempo_analise_s / resultado.folhas, 4
        )
    resultado.observacoes = list(projeto.observacoes)

    # quantas paginas ficaram laranja, e por que
    contagem: dict[str, int] = {}
    for item in list(projeto.folhas) + list(projeto.paginas):
        for codigo in item.alertas:
            contagem[codigo] = contagem.get(codigo, 0) + 1
    resultado.alertas = dict(sorted(contagem.items(), key=lambda kv: -kv[1]))

    # --- fase 2: qualidade de imagem, pagina a pagina, filtro a filtro ----
    indices = escolher_paginas(projeto, quantas_paginas)
    resultado.paginas_medidas = indices
    por_indice = {p.indice: p for p in projeto.paginas}

    tamanhos: list[tuple[int, int]] = []
    angulos_residuais: list[float] = []

    doc = abrir_pdf(str(caminho))
    try:
        for indice in indices:
            pagina = por_indice.get(indice)
            if pagina is None:
                continue
            folha = projeto.folhas[pagina.folha]
            try:
                img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
                base_img = preparar_metade(img_folha, folha, pagina, projeto)
                del img_folha
            except Exception as exc:  # noqa: BLE001
                resultado.medidas.append(
                    {"pagina": indice + 1, "erro": f"{type(exc).__name__}: {exc}"}
                )
                continue

            altura, largura = base_img.shape[:2]
            tamanhos.append((largura, altura))
            try:
                angulos_residuais.append(abs(detectar_angulo(base_img).angulo))
            except Exception:  # noqa: BLE001
                pass

            # A regiao de papel e a classe da pagina saem do ORIGINAL, uma vez
            # so, e valem para todos os filtros desta pagina.
            cinza_original = _cinza(base_img)
            tinta_original = _mascara_de_tinta(cinza_original)
            papel_ref = regiao_de_papel(tinta_original)
            classe = classificar_pagina(
                float((tinta_original > 0).mean()), bool(pagina.tem_cor)
            )

            registro: dict[str, Any] = {
                "pagina": indice + 1,
                "folha": folha.indice + 1,
                "metade": pagina.metade,
                "tem_cor": bool(pagina.tem_cor),
                "classe": classe,
                "largura_px": largura,
                "altura_px": altura,
                "largura_mm": round(largura / dpi * 25.4, 1),
                "altura_mm": round(altura / dpi * 25.4, 1),
                "filtros": {},
            }

            # A selecao e descoberta uma vez por pagina e serve os quatro
            # filtros, como acontece no programa de verdade.
            from core.pipeline import garantir_selecao

            selecao = garantir_selecao(projeto, pagina, base_img)
            registro["regioes_achadas"] = len(selecao)

            # Pagina que o detector diz ser desenho de ponta a ponta nao tem
            # letra para medir, mesmo que a classificacao por tinta e cor diga
            # que tem. Ver e_so_desenho.
            if classe == TEXTO and e_so_desenho(selecao, altura, largura):
                classe = ILUSTRACAO
                registro["classe"] = classe
                registro["reclassificada_por_desenho"] = True
                resultado.reclassificadas.append(indice + 1)

            medidas_base: dict[str, float] = {}
            for filtro in FILTROS_MEDIDOS:
                try:
                    with Cronometro() as relogio:
                        saida, _mono = aplicar_filtro_com_selecao(
                            base_img.copy(), filtro, selecao)
                    m = medir_imagem(saida, papel_ref=papel_ref, dpi=dpi)
                    m["tempo_s"] = round(relogio.segundos, 3)
                    del saida
                except Exception as exc:  # noqa: BLE001
                    registro["filtros"][filtro] = {
                        "erro": f"{type(exc).__name__}: {exc}"
                    }
                    continue

                if filtro == ORIGINAL:
                    medidas_base = dict(m)
                else:
                    motivos = comparar_com_original(m, medidas_base, filtro, classe)
                    m["pior_que_original"] = bool(motivos)
                    m["motivos"] = motivos
                    if motivos:
                        resultado.piores_que_original.append(
                            {
                                "pagina": indice + 1,
                                "filtro": NOMES_AMIGAVEIS.get(filtro, filtro),
                                "classe": classe,
                                "motivos": motivos,
                            }
                        )
                registro["filtros"][filtro] = m

            resultado.medidas.append(registro)
            del base_img
    finally:
        doc.close()

    # --- geometria -------------------------------------------------------
    if tamanhos:
        larguras = [t[0] for t in tamanhos]
        alturas = [t[1] for t in tamanhos]
        resultado.geometria = {
            "largura_px_min": min(larguras),
            "largura_px_max": max(larguras),
            "altura_px_min": min(alturas),
            "altura_px_max": max(alturas),
            "variacao_largura_px": max(larguras) - min(larguras),
            "variacao_altura_px": max(alturas) - min(alturas),
            "variacao_largura_mm": round((max(larguras) - min(larguras)) / dpi * 25.4, 2),
            "variacao_altura_mm": round((max(alturas) - min(alturas)) / dpi * 25.4, 2),
            "angulo_residual_medio_graus": (
                round(statistics.fmean(angulos_residuais), 4) if angulos_residuais else 0.0
            ),
            "angulo_residual_maximo_graus": (
                round(max(angulos_residuais), 4) if angulos_residuais else 0.0
            ),
        }

    # --- fase 3: exportar de verdade, para ter tempo, memoria e tamanho ---
    _exportar_amostra(projeto, indices, dpi, resultado)
    return resultado


def _exportar_amostra(
    projeto: Projeto, indices: list[int], dpi: int, resultado: ResultadoLivro
) -> None:
    """Exporta so as paginas medidas, no caminho de verdade do programa.

    Exportar os nove livros inteiros a 300 DPI levaria horas e mediria sempre a
    mesma coisa. Medimos o custo POR PAGINA e o relatorio projeta dai o livro
    de 500 paginas que a meta cobra - dizendo com todas as letras que e
    projecao.
    """
    if not indices:
        return

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    destino = Path(projeto.caminho_saida)

    # Cinto de seguranca: jamais gravar dentro do acervo.
    if NOME_DO_ACERVO.lower() in str(destino).lower():
        raise RuntimeError("A saida nao pode ficar dentro da pasta do acervo.")

    escolhidas = set(indices)
    por_indice = {p.indice: p for p in projeto.paginas}
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        with VigiaDeMemoria() as vigia, Cronometro() as relogio:
            with EscritorPDF(destino) as escritor:
                folha_atual: int | None = None
                img_folha: np.ndarray | None = None
                for indice in sorted(escolhidas):
                    pagina = por_indice.get(indice)
                    if pagina is None:
                        continue
                    folha = projeto.folhas[pagina.folha]
                    if folha_atual != folha.indice:
                        img_folha = pagina_para_array(doc, folha.indice, dpi=dpi)
                        folha_atual = folha.indice
                    img = preparar_metade(img_folha, folha, pagina, projeto)
                    img, mono = aplicar_filtro(
                        img, pagina.filtro, pagina.forca_preto,
                        pagina.clareza_melhorar, pagina.intensidade_magico,
                    )
                    escritor.escrever_imagem(img, dpi=dpi, monocromatico=mono)
                    del img
    finally:
        doc.close()

    resultado.tempo_export_s = round(relogio.segundos, 2)
    resultado.pico_memoria_mb = round(max(resultado.pico_memoria_mb, vigia.pico_mb), 1)
    if escolhidas:
        resultado.tempo_por_pagina_export_s = round(relogio.segundos / len(escolhidas), 3)
    if destino.exists():
        tamanho = destino.stat().st_size
        resultado.pdf_saida_mb = round(tamanho / (1024 * 1024), 2)
        resultado.pdf_saida_kb_por_pagina = round(tamanho / 1024 / len(escolhidas), 1)


# ---------------------------------------------------------------------------
# Tempo de abertura do programa e das primeiras miniaturas
# ---------------------------------------------------------------------------

def medir_abertura_do_programa() -> dict[str, float]:
    """Quanto tempo o programa leva para aparecer na tela.

    Roda num processo separado e sem tela (offscreen) porque e a unica forma
    de medir isso sozinho, sem alguem olhando o relogio.
    """
    codigo = (
        "import time,os,sys;"
        "os.environ['QT_QPA_PLATFORM']='offscreen';"
        f"sys.path.insert(0, r'{RAIZ}');"
        "t=time.perf_counter();"
        "from PySide6.QtWidgets import QApplication;"
        "app=QApplication([]);"
        "from ui.janela_principal import JanelaPrincipal;"
        "j=JanelaPrincipal();j.show();"
        "app.processEvents();"
        "print(round(time.perf_counter()-t,3))"
    )
    try:
        saida = subprocess.run(
            [sys.executable, "-c", codigo],
            capture_output=True, text=True, timeout=180, cwd=str(RAIZ),
        )
        linha = (saida.stdout or "").strip().splitlines()
        if linha:
            return {"abrir_programa_s": float(linha[-1])}
        return {"abrir_programa_s": -1.0, "erro": (saida.stderr or "")[-400:]}
    except Exception as exc:  # noqa: BLE001
        return {"abrir_programa_s": -1.0, "erro": f"{type(exc).__name__}: {exc}"}


def medir_primeiras_miniaturas(caminho: Path, quantas: int = 12) -> float:
    """Tempo ate as primeiras miniaturas de um livro estarem prontas.

    E o que o Kaique enxerga como "abriu": o momento em que a tira de baixo
    para de estar vazia.
    """
    from core.pdf_io import DPI_MINIATURA

    try:
        doc = abrir_pdf(str(caminho))
    except ErroPDF:
        return -1.0
    try:
        with Cronometro() as relogio:
            total = min(quantas, doc.page_count)
            for i in range(total):
                img = pagina_para_array(doc, i, dpi=DPI_MINIATURA)
                del img
        return round(relogio.segundos, 3)
    except Exception:  # noqa: BLE001
        return -1.0
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Relatorios
# ---------------------------------------------------------------------------

def _sem_acento(texto: str) -> str:
    """Caminhos de disco sem acento: e regra do projeto, e ja custou um bug."""
    import unicodedata

    normal = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normal if not unicodedata.combining(c))


def _ambiente() -> dict[str, Any]:
    memoria_mb = 0.0
    try:
        import psutil

        memoria_mb = round(psutil.virtual_memory().total / (1024 * 1024), 0)
    except Exception:  # noqa: BLE001
        pass
    return {
        "python": platform.python_version(),
        "sistema": f"{platform.system()} {platform.release()}",
        "processador": platform.processor(),
        "nucleos": os.cpu_count(),
        "memoria_total_mb": memoria_mb,
        "opencv": cv2.__version__,
        "doxapy_disponivel": doxapy_disponivel(),
        "dpi_da_medida": DPI_MEDIDA,
    }


def _media(valores: list[float]) -> float:
    return round(statistics.fmean(valores), 3) if valores else 0.0


def montar_resumo(livros: list[ResultadoLivro]) -> dict[str, Any]:
    """Junta os numeros de todos os livros num punhado de medias."""
    ok = [r for r in livros if not r.erro]
    por_filtro: dict[str, dict[str, list[float]]] = {f: {} for f in FILTROS_MEDIDOS}

    for livro in ok:
        for registro in livro.medidas:
            for filtro, m in registro.get("filtros", {}).items():
                if "erro" in m:
                    continue
                for chave, valor in m.items():
                    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                        por_filtro.setdefault(filtro, {}).setdefault(chave, []).append(
                            float(valor)
                        )

    medias = {
        filtro: {chave: _media(vals) for chave, vals in campos.items()}
        for filtro, campos in por_filtro.items()
    }

    total_piores = sum(len(r.piores_que_original) for r in ok)
    tempos_folha = [r.tempo_por_folha_analise_s for r in ok if r.tempo_por_folha_analise_s]
    tempos_pagina = [r.tempo_por_pagina_export_s for r in ok if r.tempo_por_pagina_export_s]

    return {
        "livros_avaliados": len(ok),
        "livros_com_erro": len(livros) - len(ok),
        "total_folhas": sum(r.folhas for r in ok),
        "total_paginas": sum(r.paginas for r in ok),
        "paginas_medidas": sum(len(r.paginas_medidas) for r in ok),
        "paginas_piores_que_original": total_piores,
        "medias_por_filtro": medias,
        "tempo_analise_por_folha_s": _media(tempos_folha),
        "tempo_export_por_pagina_s": _media(tempos_pagina),
        "projecao_analise_500_folhas_s": round(_media(tempos_folha) * 500, 1),
        "projecao_export_500_paginas_s": round(_media(tempos_pagina) * 500, 1),
        "pico_memoria_mb": round(max((r.pico_memoria_mb for r in ok), default=0.0), 1),
    }


def _tabela(linhas: list[list[str]], cabecalho: list[str]) -> str:
    partes = ["| " + " | ".join(cabecalho) + " |",
              "|" + "|".join(["---"] * len(cabecalho)) + "|"]
    for linha in linhas:
        partes.append("| " + " | ".join(linha) + " |")
    return "\n".join(partes)


def escrever_markdown(dados: dict[str, Any], destino: Path) -> None:
    """O relatorio que o Samuel le. Sem jargao, numero sempre explicado."""
    resumo = dados["resumo"]
    amb = dados["ambiente"]
    desem = dados["desempenho"]
    L: list[str] = []

    L.append(f"# {dados['titulo']}")
    L.append("")
    L.append(f"Medido em {dados['quando']}.")
    L.append("")
    L.append(
        "Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, "
        "diz em numeros como ele esta hoje. Serve para que, depois de qualquer "
        "mudanca, se possa medir de novo e saber se melhorou de verdade ou se "
        "foi so impressao."
    )
    L.append("")

    # --- o que importa primeiro ---
    L.append("## O essencial, em quatro linhas")
    L.append("")
    piores = resumo["paginas_piores_que_original"]
    L.append(
        f"- Foram medidos **{resumo['livros_avaliados']} livros**, "
        f"{resumo['total_folhas']} folhas, {resumo['total_paginas']} paginas de saida."
    )
    L.append(
        f"- A qualidade de imagem foi medida a fundo em **{resumo['paginas_medidas']} paginas**, "
        f"as mesmas em toda rodada."
    )
    if piores:
        L.append(
            f"- **{piores} vezes um filtro deixou a pagina pior do que ela era.** "
            f"Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer "
            f"mais de uma vez, uma por filtro que a estragou. O criterio de "
            f"aceitacao do projeto exige que esse numero seja zero."
        )
    else:
        L.append("- **Nenhuma pagina saiu pior que o original.** E o que se espera.")
    L.append(
        f"- O programa nunca passou de **{resumo['pico_memoria_mb']:.0f} MB** de memoria, "
        f"contra o teto de {METAS['pico_memoria_mb']:.0f} MB."
    )
    L.append("")

    # --- o que cada numero quer dizer ---
    L.append("## O que cada numero quer dizer")
    L.append("")
    L.append(_tabela(
        [
            ["Espessura do traco", "Grossura media da linha da letra, em pontinhos de tela (pixels). Se afina demais, some na impressao."],
            ["Vazios internos", "Buraquinhos fechados dentro das letras: o miolo do **o**, do **e**, do **a**. Se o filtro engrossa demais, eles entopem e a letra vira bolha. Quanto mais sobrarem, melhor."],
            ["Nivel do fundo", "Quao claro esta o papel, de 0 (preto) a 255 (branco). O alvo e 255: papel branco de verdade, sem o amarelado."],
            ["Ruido do fundo", "O quanto o papel varia onde deveria ser liso. Quanto menor, mais limpo."],
            ["Transicao da borda", "Largura da rampa entre a tinta e o papel, em pixels. **Este e o numero da queixa de letra pixelada.** De 1 a 2 e o certo; perto de zero a borda vira degrau de escada; acima de 3 a letra borra."],
            ["Nitidez", "O quanto a imagem tem detalhe definido. Maior e mais nitido, mas exagero vira ruido."],
        ],
        ["Numero", "O que e, na pratica"],
    ))
    L.append("")

    # --- media por filtro ---
    L.append("## Como cada filtro se comporta, na media do acervo")
    L.append("")
    linhas = []
    for filtro in FILTROS_MEDIDOS:
        m = resumo["medias_por_filtro"].get(filtro, {})
        if not m:
            continue
        linhas.append([
            NOMES_AMIGAVEIS.get(filtro, filtro),
            f"{m.get('espessura_traco_px', 0):.2f}",
            f"{m.get('vazios_internos', 0):.0f}",
            f"{m.get('nivel_fundo', 0):.1f}",
            f"{m.get('ruido_fundo', 0):.2f}",
            f"{m.get('transicao_borda_px', 0):.2f}",
            f"{m.get('nitidez', 0):.0f}",
            f"{m.get('tempo_s', 0):.2f}s",
        ])
    L.append(_tabela(linhas, [
        "Filtro", "Espessura", "Vazios", "Fundo (255=branco)", "Ruido",
        "Transicao (px)", "Nitidez", "Tempo/pagina",
    ]))
    L.append("")
    L.append(
        "> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - "
        "e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; "
        "valor muito baixo e o serrilhado que aparece nas letras."
    )
    L.append("")

    # --- desempenho ---
    L.append("## Velocidade e memoria")
    L.append("")
    linhas = [
        ["Abrir o programa", f"{desem.get('abrir_programa_s', 0):.2f} s",
         f"{METAS['abrir_programa_s']:.0f} s",
         _passou(desem.get("abrir_programa_s", 0), METAS["abrir_programa_s"])],
        ["Primeiras miniaturas", f"{desem.get('primeiras_miniaturas_s', 0):.2f} s",
         f"{METAS['primeiras_miniaturas_s']:.0f} s",
         _passou(desem.get("primeiras_miniaturas_s", 0), METAS["primeiras_miniaturas_s"])],
        ["Analisar 500 folhas (projecao)",
         f"{resumo['projecao_analise_500_folhas_s']:.0f} s",
         f"{METAS['analise_500_paginas_s']:.0f} s",
         _passou(resumo["projecao_analise_500_folhas_s"], METAS["analise_500_paginas_s"])],
        ["Exportar 500 paginas a 300 DPI (projecao)",
         f"{resumo['projecao_export_500_paginas_s']:.0f} s",
         f"{METAS['exportar_500_paginas_300dpi_s']:.0f} s",
         _passou(resumo["projecao_export_500_paginas_s"],
                 METAS["exportar_500_paginas_300dpi_s"])],
        ["Pico de memoria", f"{resumo['pico_memoria_mb']:.0f} MB",
         f"{METAS['pico_memoria_mb']:.0f} MB",
         _passou(resumo["pico_memoria_mb"], METAS["pico_memoria_mb"])],
    ]
    L.append(_tabela(linhas, ["O que", "Medido", "Meta", "Passou?"]))
    L.append("")
    L.append(
        "> As duas linhas marcadas como **projecao** foram calculadas a partir do "
        "custo real por folha e por pagina medido nos nove livros, multiplicado "
        "por 500. Nenhum livro do acervo tem 500 paginas."
    )
    L.append("")

    # --- livro a livro ---
    L.append("## Livro a livro")
    L.append("")
    linhas = []
    for livro in dados["livros"]:
        if livro.get("erro"):
            linhas.append([livro["nome"][:44], "-", "-", "-", "-",
                           f"ERRO: {livro['erro'][:60]}"])
            continue
        linhas.append([
            livro["nome"][:44],
            f"{livro['tamanho_mb']:.0f} MB",
            f"{livro['folhas']}",
            f"{livro['paginas']}",
            f"{livro['tempo_analise_s']:.1f}s",
            f"{len(livro['piores_que_original'])}",
        ])
    L.append(_tabela(linhas, [
        "Livro", "Tamanho", "Folhas", "Paginas", "Analise", "Paginas piores",
    ]))
    L.append("")

    # --- paginas piores que o original ---
    L.append("## Paginas que sairam piores que o original")
    L.append("")
    if not piores:
        L.append("Nenhuma. E o resultado esperado.")
    else:
        L.append(
            f"Sao **{piores}** ocorrencias. Cada linha e uma pagina com um filtro "
            f"que a deixou pior do que ela era antes de qualquer tratamento."
        )
        L.append("")
        linhas = []
        for livro in dados["livros"]:
            for caso in livro.get("piores_que_original", []):
                linhas.append([
                    livro["nome"][:34],
                    f"{caso['pagina']}",
                    caso["filtro"],
                    "; ".join(caso["motivos"])[:150],
                ])
        L.append(_tabela(linhas, ["Livro", "Pagina", "Filtro", "O que piorou"]))
    L.append("")

    # --- paginas em que a regua deixou de cobrar letra ---
    reclassificadas = [
        (livro["nome"], pagina)
        for livro in dados["livros"]
        for pagina in livro.get("reclassificadas", [])
    ]
    if reclassificadas:
        L.append("## Paginas em que a regua nao cobrou letra")
        L.append("")
        L.append(
            "A conta de tinta e cor chamou estas paginas de texto, mas o detector "
            "de regioes marcou a folha INTEIRA como desenho e nada como letra. "
            "Numa pagina assim nao ha letra para medir, entao os criterios de "
            "letra - vazios internos, espessura e borda - ficam de fora. Os de "
            "fundo continuam valendo."
        )
        L.append("")
        L.append(
            "**Elas saem nomeadas aqui de proposito.** E onde a regua afrouxa, e "
            "se o detector errar - marcar como desenho uma pagina que tem texto - "
            "o erro tem de estar a vista, e nao escondido num numero menor."
        )
        L.append("")
        L.append(_tabela(
            [[nome[:44], str(pagina)] for nome, pagina in reclassificadas],
            ["Livro", "Pagina"],
        ))
        L.append("")

    # --- alertas ---
    L.append("## Paginas marcadas em laranja, e por que")
    L.append("")
    L.append(
        "Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um "
        "pedido de conferida."
    )
    L.append("")
    total_alertas: dict[str, int] = {}
    for livro in dados["livros"]:
        for codigo, quantas in livro.get("alertas", {}).items():
            total_alertas[codigo] = total_alertas.get(codigo, 0) + quantas
    if not total_alertas:
        L.append("Nenhuma pagina ficou laranja.")
    else:
        linhas = []
        for codigo, quantas in sorted(total_alertas.items(), key=lambda kv: -kv[1]):
            try:
                d = analise.descrever(codigo)
                titulo, mensagem = d.titulo, d.mensagem
            except Exception:  # noqa: BLE001
                titulo, mensagem = codigo, ""
            linhas.append([titulo, f"{quantas}", mensagem])
        L.append(_tabela(linhas, ["Aviso", "Quantas paginas", "O que o programa diz"]))
    L.append("")

    # --- geometria ---
    L.append("## Geometria: as paginas saem todas do mesmo tamanho?")
    L.append("")
    L.append(
        "Paginas do mesmo livro precisam sair identicas, senao o caderno nao "
        "fecha direito na hora de imprimir. A coluna de variacao deveria ser zero."
    )
    L.append("")
    linhas = []
    for livro in dados["livros"]:
        g = livro.get("geometria") or {}
        if not g:
            continue
        linhas.append([
            livro["nome"][:38],
            f"{g.get('largura_px_min', 0)}x{g.get('altura_px_min', 0)}",
            f"{g.get('variacao_largura_mm', 0):.1f} mm",
            f"{g.get('variacao_altura_mm', 0):.1f} mm",
            f"{g.get('angulo_residual_medio_graus', 0):.3f}",
            f"{g.get('angulo_residual_maximo_graus', 0):.3f}",
        ])
    L.append(_tabela(linhas, [
        "Livro", "Menor pagina (px)", "Variacao largura", "Variacao altura",
        "Inclinacao media", "Inclinacao maxima",
    ]))
    L.append("")

    # --- ambiente ---
    L.append("## Em que maquina isto foi medido")
    L.append("")
    L.append(
        f"- {amb['sistema']}, Python {amb['python']}, {amb['nucleos']} nucleos, "
        f"{amb['memoria_total_mb'] / 1024:.0f} GB de memoria"
    )
    L.append(f"- OpenCV {amb['opencv']}, DoxaPy disponivel: "
             f"{'sim' if amb['doxapy_disponivel'] else 'nao (usando o plano B)'}")
    L.append(f"- Todas as imagens medidas a {amb['dpi_da_medida']} DPI")
    L.append("")
    L.append(
        "> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos "
        "numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num "
        "computador de verdade."
    )
    L.append("")

    destino.write_text("\n".join(L), encoding="utf-8")


def _passou(valor: float, meta: float) -> str:
    if valor <= 0:
        return "nao medido"
    return "sim" if valor <= meta else "NAO"


def escrever_por_livro(dados: dict[str, Any], pasta: Path) -> list[Path]:
    """Um relatorio por livro, como a Etapa 6 do protocolo pede.

    O agregado esconde o livro: uma media boa pode ter dentro dela um livro
    inteiro saindo mal. Aqui cada um responde por si.
    """
    from relatorio import gravar

    escritos: list[Path] = []
    for livro in dados["livros"]:
        nome = _sem_acento(livro["nome"])[:56]
        L = [f"# {livro['nome']}", ""]

        if livro.get("erro"):
            L += [f"**Nao consegui abrir este livro.** {livro['erro']}", ""]
            escritos.append(gravar("\n".join(L), pasta / nome)["md"])
            continue

        L += [
            f"- Arquivo de {livro['tamanho_mb']:.0f} MB",
            f"- {livro['folhas']} folhas no PDF, que viram {livro['paginas']} "
            f"paginas de saida",
            f"- {len(livro['paginas_medidas'])} paginas medidas a fundo",
            f"- {livro['tempo_analise_s']:.0f} segundos para analisar o livro "
            f"inteiro ({livro['tempo_por_folha_analise_s'] * 1000:.0f} "
            f"milissegundos por folha)",
            "",
        ]

        piores = livro.get("piores_que_original", [])
        L.append("## Paginas que sairam piores que o original")
        L.append("")
        if not piores:
            L.append("Nenhuma. E o resultado esperado.")
        else:
            L.append(f"Sao {len(piores)} ocorrencias. Cada linha e uma pagina com um "
                     f"filtro que a deixou pior do que ela era.")
            L.append("")
            L.append("| Pagina | Filtro | O que piorou |")
            L.append("|---|---|---|")
            for caso in piores:
                L.append(f"| {caso['pagina']} | {caso['filtro']} | "
                         f"{'; '.join(caso['motivos'])[:150]} |")
        L.append("")

        alertas = livro.get("alertas") or {}
        L.append("## Paginas marcadas em laranja")
        L.append("")
        if not alertas:
            L.append("Nenhuma.")
        else:
            L.append("Laranja quer dizer *o programa nao teve certeza*. Nao e erro:")
            L.append("e um pedido de conferida.")
            L.append("")
            L.append("| Aviso | Quantas | O que significa |")
            L.append("|---|---|---|")
            for codigo, quantas in alertas.items():
                try:
                    d = analise.descrever(codigo)
                    L.append(f"| {d.titulo} | {quantas} | {d.mensagem} |")
                except Exception:  # noqa: BLE001
                    L.append(f"| {codigo} | {quantas} | |")
        L.append("")

        if livro.get("observacoes"):
            L.append("## Observacoes do livro inteiro")
            L.append("")
            for obs in livro["observacoes"]:
                L.append(f"- {obs}")
            L.append("")

        g = livro.get("geometria") or {}
        if g:
            L += [
                "## As paginas saem todas do mesmo tamanho?",
                "",
                "Paginas do mesmo livro precisam sair identicas, senao o caderno",
                "nao fecha direito na impressao.",
                "",
                f"- Menor pagina: {g.get('largura_px_min')} x "
                f"{g.get('altura_px_min')} pontinhos",
                f"- Variacao de largura: {g.get('variacao_largura_mm', 0):.1f} mm",
                f"- Variacao de altura: {g.get('variacao_altura_mm', 0):.1f} mm",
                f"- Inclinacao que sobrou depois de endireitar: "
                f"{g.get('angulo_residual_medio_graus', 0):.3f} grau na media, "
                f"{g.get('angulo_residual_maximo_graus', 0):.3f} no pior caso",
                "",
            ]

        L += [
            "## Como cada filtro se comportou",
            "",
            "| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |",
            "|---|---|---|---|---|---|",
        ]
        por_filtro: dict[str, dict[str, list[float]]] = {}
        for registro in livro.get("medidas", []):
            for filtro, m in registro.get("filtros", {}).items():
                if "erro" in m:
                    continue
                for chave, valor in m.items():
                    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                        por_filtro.setdefault(filtro, {}).setdefault(
                            chave, []).append(float(valor))
        for filtro in FILTROS_MEDIDOS:
            campos = por_filtro.get(filtro)
            if not campos:
                continue
            L.append(
                f"| {NOMES_AMIGAVEIS.get(filtro, filtro)} "
                f"| {_media(campos.get('espessura_traco_px', [])):.2f} "
                f"| {_media(campos.get('vazios_internos', [])):.0f} "
                f"| {_media(campos.get('nivel_fundo', [])):.1f} "
                f"| {_media(campos.get('ruido_fundo', [])):.2f} "
                f"| {_media(campos.get('transicao_borda_px', [])):.2f} |")
        L += [
            "",
            "> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os",
            "> buraquinhos dentro das letras: quanto mais sobrarem, melhor.",
            "> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e",
            "> serrilhado.",
            "",
        ]
        escritos.append(gravar("\n".join(L), pasta / nome)["md"])
    return escritos


def escrever_desempenho(dados: dict[str, Any], pasta: Path) -> Path:
    """A tabela da Etapa 5: as metas, o medido, e passou ou nao."""
    from relatorio import gravar

    r, d = dados["resumo"], dados["desempenho"]
    amb = dados["ambiente"]

    linhas = [
        ("Abrir o programa", d.get("abrir_programa_s", 0), METAS["abrir_programa_s"], "s"),
        ("Primeiras miniaturas na tela", d.get("primeiras_miniaturas_s", 0),
         METAS["primeiras_miniaturas_s"], "s"),
        ("Analisar 500 folhas", r["projecao_analise_500_folhas_s"],
         METAS["analise_500_paginas_s"], "s"),
        ("Exportar 500 paginas a 300 DPI", r["projecao_export_500_paginas_s"],
         METAS["exportar_500_paginas_300dpi_s"], "s"),
        ("Pico de memoria", r["pico_memoria_mb"], METAS["pico_memoria_mb"], "MB"),
    ]

    L = [
        "# Desempenho",
        "",
        f"Medido em {dados['quando']}.",
        "",
        "As metas sao as da Etapa 5 do protocolo. Onde houver projecao, ela sai",
        "do custo real por folha medido nos nove livros, multiplicado por 500 -",
        "nenhum livro do acervo tem 500 paginas.",
        "",
        "| O que | Medido | Meta | Passou? |",
        "|---|---|---|---|",
    ]
    for nome, valor, meta, unidade in linhas:
        L.append(f"| {nome} | {valor:.1f} {unidade} | {meta:.0f} {unidade} "
                 f"| {_passou(valor, meta)} |")

    L += [
        "",
        "## Custo por pagina, que e de onde as projecoes saem",
        "",
        f"- Analisar uma folha: {r['tempo_analise_por_folha_s'] * 1000:.0f} "
        f"milissegundos",
        f"- Exportar uma pagina a 300 DPI: "
        f"{r['tempo_export_por_pagina_s'] * 1000:.0f} milissegundos",
        "",
        "## Quanto tempo cada filtro leva por pagina",
        "",
        "| Filtro | Tempo |",
        "|---|---|",
    ]
    for filtro in FILTROS_MEDIDOS:
        m = r["medias_por_filtro"].get(filtro, {})
        if m:
            L.append(f"| {NOMES_AMIGAVEIS.get(filtro, filtro)} | "
                     f"{m.get('tempo_s', 0) * 1000:.0f} ms |")

    L += [
        "",
        "## Memoria, livro a livro",
        "",
        "O que importa aqui e o pico **nao acompanhar** o tamanho do livro. Se",
        "acompanhasse, um livro grande estouraria a memoria da maquina do",
        "Kaique.",
        "",
        "| Livro | Folhas | Pico |",
        "|---|---|---|",
    ]
    for livro in sorted(dados["livros"], key=lambda x: -(x.get("folhas") or 0)):
        if livro.get("erro"):
            continue
        L.append(f"| {livro['nome'][:40]} | {livro['folhas']} | "
                 f"{livro['pico_memoria_mb']:.0f} MB |")

    L += [
        "",
        "## Em que maquina isto foi medido",
        "",
        f"- {amb['sistema']}, {amb['nucleos']} nucleos, "
        f"{amb['memoria_total_mb'] / 1024:.0f} GB de memoria",
        "",
        "> Esta maquina e mais forte que a do Kaique. Os tempos la serao",
        "> maiores. A conferencia num computador de verdade esta em",
        "> `conferencia-outro-computador.pdf`.",
        "",
    ]
    return gravar("\n".join(L), pasta / "desempenho")["md"]


# ---------------------------------------------------------------------------
# Comparacao entre duas rodadas
# ---------------------------------------------------------------------------

def comparar_rodadas(antes: dict[str, Any], depois: dict[str, Any]) -> str:
    """Diz, em portugues, o que mudou de uma medicao para outra."""
    L = ["# Comparacao entre duas medicoes", ""]
    L.append(f"- Antes: {antes.get('titulo', '?')} ({antes.get('quando', '?')})")
    L.append(f"- Depois: {depois.get('titulo', '?')} ({depois.get('quando', '?')})")
    L.append("")

    ra, rd = antes["resumo"], depois["resumo"]
    # Para cada numero: se "maior e melhor" ou nao.
    direcao = {
        "espessura_traco_px": 0,      # nem maior nem menor: so nao pode despencar
        "vazios_internos": +1,
        "nivel_fundo": +1,
        "ruido_fundo": -1,
        "transicao_borda_px": 0,
        "nitidez": +1,
    }

    for filtro in FILTROS_MEDIDOS:
        ma = ra["medias_por_filtro"].get(filtro, {})
        md = rd["medias_por_filtro"].get(filtro, {})
        if not ma or not md:
            continue
        L.append(f"## {NOMES_AMIGAVEIS.get(filtro, filtro)}")
        L.append("")
        linhas = []
        for chave, sinal in direcao.items():
            a, d = ma.get(chave, 0.0), md.get(chave, 0.0)
            delta = d - a
            if abs(delta) < 1e-9:
                veredito = "igual"
            elif sinal == 0:
                veredito = "mudou"
            elif (delta > 0) == (sinal > 0):
                veredito = "melhorou"
            else:
                veredito = "PIOROU"
            linhas.append([chave, f"{a:.3f}", f"{d:.3f}", f"{delta:+.3f}", veredito])
        L.append(_tabela(linhas, ["Numero", "Antes", "Depois", "Diferenca", "Veredito"]))
        L.append("")

    pa, pd = ra["paginas_piores_que_original"], rd["paginas_piores_que_original"]
    L.append("## Paginas piores que o original")
    L.append("")
    L.append(f"Antes: {pa}. Depois: {pd}. "
             + ("Melhorou." if pd < pa else "Igual." if pd == pa else "PIOROU."))
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Programa
# ---------------------------------------------------------------------------

def achar_acervo(indicado: str | None) -> Path:
    """Acha a pasta do acervo sem chutar o nome do usuario nem da Area de Trabalho.

    A Area de Trabalho pode estar redirecionada para o OneDrive - e o padrao em
    muito Windows novo. Perguntar ao proprio Windows onde ela esta e a unica
    forma que nao quebra na maquina do Kaique.
    """
    if indicado:
        caminho = Path(indicado)
        if caminho.is_dir():
            return caminho
        raise SystemExit(f"Nao achei a pasta indicada: {indicado}")

    candidatas: list[Path] = []
    try:  # a forma certa: perguntar ao Windows
        from ctypes import windll, wintypes  # noqa: F401

        buffer = ctypes.create_unicode_buffer(260)
        # CSIDL_DESKTOPDIRECTORY = 0x10
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buffer)
        if buffer.value:
            candidatas.append(Path(buffer.value))
    except Exception:  # noqa: BLE001 - fora do Windows, ou API indisponivel
        pass

    candidatas.append(Path.home() / "Desktop")
    candidatas.append(Path.home() / "OneDrive" / "Desktop")
    candidatas.append(Path.home() / "OneDrive" / "Area de Trabalho")

    # O acervo ja mudou de lugar uma vez, entao olhamos varios lugares
    # conhecidos - mas em ORDEM DE PREFERENCIA, e nao pelo que tiver mais PDF.
    # Contar arquivos escolhia errado: a pasta antiga tem uma subpasta de
    # RESULTADOS, e os PDFs que nos mesmos geramos entravam na conta.
    nomes = [
        Path("TESTES EDITOR DE IMPRESSAO") / "LIVROS PARA TESTE",
        Path(NOME_DO_ACERVO),
        Path("LIVROS PARA FAZER TESTE"),
    ]
    for nome in nomes:
        for base in candidatas:
            alvo = base / nome
            if alvo.is_dir() and any(alvo.rglob("*.pdf")):
                return alvo

    raise SystemExit(
        "Nao achei a pasta dos livros de teste na Area de Trabalho. "
        "Passe o caminho com --acervo."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Mede o Editor de Impressao em numeros e grava os relatorios."
    )
    p.add_argument("--acervo", default=None, help="pasta com os PDFs de teste")
    p.add_argument("--paginas", type=int, default=PAGINAS_POR_LIVRO,
                   help="quantas paginas de cada livro entram na medida de qualidade")
    p.add_argument("--dpi", type=int, default=DPI_MEDIDA, help="DPI da medida")
    p.add_argument("--saida", default=str(PASTA_RELATORIOS), help="pasta dos relatorios")
    p.add_argument("--rotulo", default="linha-de-base",
                   help="nome dos arquivos gerados, sem extensao")
    p.add_argument("--titulo", default=None, help="titulo do relatorio")
    p.add_argument("--comparar", default=None,
                   help="caminho de um .json anterior, para gerar a comparacao")
    p.add_argument("--livro", default=None,
                   help="mede so os livros cujo nome contenha este texto")
    p.add_argument("--por-livro", action="store_true",
                   help="grava tambem um relatorio por livro e o de desempenho")
    p.add_argument("--refazer-md", default=None, metavar="ARQUIVO.json",
                   help="so reescreve o .md a partir de um .json ja medido, "
                        "sem medir nada de novo")
    args = p.parse_args(argv)

    # Reescrever o texto do relatorio nao exige remedir o acervo. Sem isto,
    # trocar uma frase custaria os 33 minutos da bateria inteira.
    if args.refazer_md:
        origem = Path(args.refazer_md)
        dados_md = json.loads(origem.read_text(encoding="utf-8"))
        destino_md = origem.with_suffix(".md")
        escrever_markdown(dados_md, destino_md)
        print(f"Relatorio reescrito: {destino_md}")
        return 0

    acervo = achar_acervo(args.acervo)
    pdfs = sorted(acervo.rglob("*.pdf"))
    if args.livro:
        # sem acento dos dois lados: procurar por "Boecio" tem que achar "Boécio"
        alvo = _sem_acento(args.livro).lower()
        pdfs = [c for c in pdfs if alvo in _sem_acento(c.name).lower()]
    if not pdfs:
        raise SystemExit(f"Nenhum PDF encontrado em {acervo}")

    pasta_relatorios = Path(args.saida)
    pasta_relatorios.mkdir(parents=True, exist_ok=True)

    print(f"Acervo: {acervo}")
    print(f"Livros: {len(pdfs)}   Paginas medidas por livro: {args.paginas}   "
          f"DPI: {args.dpi}")
    print("-" * 72)

    print("Medindo o tempo de abertura do programa...", flush=True)
    desempenho = medir_abertura_do_programa()

    livros: list[ResultadoLivro] = []
    for n, caminho in enumerate(pdfs, 1):
        print(f"[{n}/{len(pdfs)}] {caminho.name} ...", end=" ", flush=True)
        inicio = time.perf_counter()
        try:
            resultado = avaliar_livro(caminho, args.paginas, args.dpi)
        except Exception as exc:  # noqa: BLE001 - um livro nao derruba a bateria
            resultado = ResultadoLivro(
                arquivo=caminho.name, nome=caminho.stem,
                tamanho_mb=round(caminho.stat().st_size / (1024 * 1024), 2),
                erro=f"{type(exc).__name__}: {exc}",
            )
            traceback.print_exc()
        livros.append(resultado)
        gasto = time.perf_counter() - inicio
        if resultado.erro:
            print(f"ERRO ({gasto:.0f}s): {resultado.erro[:70]}")
        else:
            print(f"{resultado.folhas} folhas, {resultado.paginas} paginas, "
                  f"{len(resultado.piores_que_original)} piores ({gasto:.0f}s)")

    # primeiras miniaturas: medido no maior livro, que e o pior caso
    maior = max(pdfs, key=lambda c: c.stat().st_size)
    desempenho["primeiras_miniaturas_s"] = medir_primeiras_miniaturas(maior)
    desempenho["livro_das_miniaturas"] = maior.name

    from datetime import datetime

    dados: dict[str, Any] = {
        "titulo": args.titulo or "Linha de base do Editor de Impressao",
        "quando": datetime.now().strftime("%d/%m/%Y as %H:%M"),
        "acervo": str(acervo),
        "ambiente": _ambiente(),
        "desempenho": desempenho,
        "resumo": montar_resumo(livros),
        "livros": [vars(r) for r in livros],
    }

    destino_json = pasta_relatorios / f"{args.rotulo}.json"
    destino_md = pasta_relatorios / f"{args.rotulo}.md"
    destino_json.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    escrever_markdown(dados, destino_md)

    # Os tres formatos, porque o Samuel nao abre .md
    try:
        from relatorio import gravar

        gravar(destino_md.read_text(encoding="utf-8"), destino_md)
    except Exception:  # noqa: BLE001 - o .md sozinho ainda serve para mim
        pass

    # A Etapa 6 pede um relatorio por livro e um de desempenho. O agregado
    # esconde o livro: uma media boa pode ter dentro dela um livro saindo mal.
    if args.rotulo == "linha-de-base" or args.por_livro:
        pasta_livros = pasta_relatorios / "por-livro"
        pasta_livros.mkdir(exist_ok=True)
        escritos = escrever_por_livro(dados, pasta_livros)
        print(f"Relatorios por livro: {len(escritos)} em {pasta_livros}")
        escrever_desempenho(dados, pasta_relatorios)
        print(f"Desempenho: {pasta_relatorios / 'desempenho.pdf'}")

    print("-" * 72)
    r = dados["resumo"]
    print(f"Livros medidos ......... {r['livros_avaliados']} "
          f"(com erro: {r['livros_com_erro']})")
    print(f"Paginas medidas ........ {r['paginas_medidas']}")
    print(f"Piores que o original .. {r['paginas_piores_que_original']}  (tem que ser 0)")
    print(f"Pico de memoria ........ {r['pico_memoria_mb']:.0f} MB "
          f"(teto {METAS['pico_memoria_mb']:.0f})")
    print(f"Abrir o programa ....... {desempenho.get('abrir_programa_s', -1):.2f} s "
          f"(meta {METAS['abrir_programa_s']:.0f})")
    print(f"Gravado em: {destino_md}")

    if args.comparar:
        anterior = json.loads(Path(args.comparar).read_text(encoding="utf-8"))
        texto = comparar_rodadas(anterior, dados)
        destino_cmp = pasta_relatorios / f"comparacao-{args.rotulo}.md"
        destino_cmp.write_text(texto, encoding="utf-8")
        print(f"Comparacao em: {destino_cmp}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
