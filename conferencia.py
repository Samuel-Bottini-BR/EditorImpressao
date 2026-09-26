"""Página de antes/depois de qualquer item do plano (item 0.4 do Plano Definitivo).

O verificador roda este script no fim de TODO item (regra 4 do plano). Ele pega
as páginas-gabarito daquele item (gabarito/lista.json, seção "itens"), produz o
"depois" de cada uma e monta a página de conferência que o Samuel olha em até
10 minutos: as colunas lado a lado (original, rodada anterior, resultado,
CamScanner, ScanTailor), a página inteira e, embaixo, o ponto que importa já
ampliado (o campo "detalhe" de cada página na lista).

Como usar (da pasta do projeto)::

    .venv\\Scripts\\python.exe conferencia.py 6.7
        o "depois" é o programa de hoje, no filtro Mágico pro (o padrão)
    .venv\\Scripts\\python.exe conferencia.py 6.7 --filtro "Preto e branco"
    .venv\\Scripts\\python.exe conferencia.py fase1 --funcao core.modulo:funcao
        o "depois" é uma função sozinha: funcao(caminho_do_pdf, imagem_antes)
    .venv\\Scripts\\python.exe conferencia.py 6.2 --pasta-depois PASTA
        o "depois" são imagens prontas: PASTA\\<id da página>.png (ou .jpg/.tif)
    .venv\\Scripts\\python.exe conferencia.py 6.7 --comparar-com relatorios\\conferir\\6.7-2026-09-25-1640
        acrescenta a coluna "Rodada anterior" (outra conferência, ou uma pasta de imagens)
    .venv\\Scripts\\python.exe conferencia.py 6.7 --opiniao opiniao.txt
        põe a opinião do verificador; só com ela a página diz PRONTO PARA CONFERIR
    .venv\\Scripts\\python.exe conferencia.py 6.7 --paginas horas_p026,escola_p035
        troca a lista de páginas do item

Para pôr a opinião sem processar tudo de novo: ``--pasta-depois`` aceita a pasta
de uma conferência já feita (usa as imagens de resultado\\ e os tempos dela).

Onde grava: relatorios\\conferir\\<item>-<AAAA-MM-DD-HHMM>\\
    conferencia-<item>.md/.html/.pdf   a página (relatorio.gravar: três formatos;
                                       o ponto do item vira hífen: conferencia-6-7)
    resultado\\<id>.png                o "depois" de cada página em tamanho cheio
                                       (é o que o --comparar-com lê depois)
    paineis\\                          as imagens reduzidas (JPG) da página
    dados.json                         os números crus (tempos, alinhamento...)
As referências recortadas (CamScanner, ScanTailor em formato que o navegador
abre) ficam uma vez só em relatorios\\conferir\\_referencias\\.

Como o detalhe é achado em cada coluna: o programa corta bordas e endireita, e
as referências têm outro enquadramento, então a mesma FRAÇÃO da página cairia
em outro lugar. Por isso cada imagem é alinhada com o original (pontos em comum
entre as duas: SIFT + RANSAC do OpenCV, algoritmo consagrado) e o retângulo do
detalhe é levado pelo alinhamento. Quando o alinhamento não dá certeza, o
recorte cai na mesma posição proporcional e a página AVISA.

Regras que valem aqui (CLAUDE.md): uma página por vez na memória (as do Opus
Majus e do Siebmacher têm 400 DPI; a saída do ScanTailor tem 94 megapixels);
os originais do gabarito e do acervo são só lidos, nunca gravados; o texto fixo
nunca diz "aprovado" - no máximo PRONTO PARA CONFERIR, e só com a opinião do
verificador.

Seguro mudar: textos, tamanhos dos painéis, qualidade dos JPG, cores. Arriscado
mudar: processar_pelo_programa (tem de ser o MESMO caminho do botão "Confirmar
e processar", senão a conferência mostra outro programa); o formato de
resultado\\<id>.png e do dados.json (conferências antigas são lidas pelo
--comparar-com e pelo --pasta-depois); os limites de alinhar() (afrouxar deixa
passar alinhamento errado sem aviso).
"""

from __future__ import annotations

import argparse
import gc
import html
import importlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import unicodedata
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# onde as coisas ficam
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent
GABARITO = RAIZ / "gabarito"
PASTA_CONFERIR = RAIZ / "relatorios" / "conferir"
# Referências preparadas uma vez só (recorte do CamScanner, ScanTailor em
# formato que o navegador abre), fora da pasta de cada rodada.
NOME_REFERENCIAS = "_referencias"

# O Mágico pro é o filtro mais parecido com o CamScanner, que é o
# resultado-alvo do plano (seção 2).
FILTRO_PADRAO = "magico_pro"

# ---------------------------------------------------------------------------
# as colunas, na ordem em que aparecem
# ---------------------------------------------------------------------------

ORIGINAL = "original"
ANTERIOR = "anterior"
RESULTADO = "resultado"
CAMSCANNER = "camscanner"
SCANTAILOR = "scantailor"

ROTULOS = {
    ORIGINAL: "Original",
    ANTERIOR: "Rodada anterior",
    RESULTADO: "Resultado",
    CAMSCANNER: "CamScanner Mágico Pro",
    SCANTAILOR: "ScanTailor 24/09",
}

# ---------------------------------------------------------------------------
# tamanhos das imagens da página (seguro mudar)
# ---------------------------------------------------------------------------

ALTURA_PAINEL = 1000         # página inteira reduzida: altura em pixels
LARGURA_MAX_PAINEL = 1600    # ... e largura máxima (folha deitada, folha dividida)
LADO_DETALHE = 1200          # detalhe ampliado: o lado maior, em pixels
QUALIDADE_PAINEL = 88        # JPG da página inteira
QUALIDADE_DETALHE = 90       # JPG do detalhe
QUALIDADE_REFERENCIA = 92    # JPG das referências coloridas em tamanho cheio
# Imagem maior que isto é reduzida logo depois de lida (a saída do ScanTailor
# tem 7925 x 11933 pixels): o detalhe continua com pixel de sobra e a memória
# não passa de uma página.
LADO_MAX_EM_MEMORIA = 6000
COR_DO_RETANGULO = (255, 0, 255)   # rosa (BGR): quase não existe em livro antigo
COR_DA_FAIXA = (128, 128, 128)     # a faixa entre as duas metades de uma folha dividida
LARGURA_DA_FAIXA = 24

# No PDF: largura útil da folha A4 (relatorio.gravar_pdf deixa 50 pt de cada
# lado) e a altura máxima de uma imagem, para uma linha de tabela nunca passar
# da folha - o Story do PyMuPDF entra em ciclo quando algo não cabe.
LARGURA_UTIL_PDF = 495
ALTURA_MAX_PDF = 600

# Quantos painéis cabem numa linha: a soma das larguras, medidas em alturas.
# 7,5 = cinco páginas em pé (0,7 cada), ou três detalhes de 2,4 lado a lado; um
# detalhe muito largo (uma faixa de 3,8) vai um embaixo do outro.
SOMA_DOS_ASPECTOS = 7.5

EXTENSOES = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

# ---------------------------------------------------------------------------
# alinhamento (arriscado mudar: ver alinhar)
# ---------------------------------------------------------------------------

LADO_ALINHAR = 2000   # as duas imagens são reduzidas a isto antes de achar pontos
PONTOS_SIFT = 6000


class ErroDeUso(Exception):
    """Algo no pedido não serve (item que não existe, pasta que falta...). A
    mensagem já vem em português, pronta para o terminal."""


# ---------------------------------------------------------------------------
# texto em português
# ---------------------------------------------------------------------------


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto)
                   if not unicodedata.combining(c))


def formatar_segundos(segundos: float | None) -> str:
    """Tempo em frase, com vírgula decimal: "0,4 segundo", "17,6 segundos",
    "2 minutos e 5 segundos". None vira "não medido", nunca 0."""
    if segundos is None or segundos < 0:
        return "não medido"
    if round(segundos, 1) < 60:
        numero = f"{segundos:.1f}".replace(".", ",")
        return f"{numero} {'segundo' if round(segundos, 1) < 2 else 'segundos'}"
    total = int(round(segundos))
    minutos, resto = divmod(total, 60)
    texto = f"{minutos} {'minuto' if minutos == 1 else 'minutos'}"
    if resto:
        texto += f" e {resto} {'segundo' if resto == 1 else 'segundos'}"
    return texto


def nome_seguro(texto: str) -> str:
    """Nome que o Windows aceita, sem acento: "6.7" fica "6.7", "Fase 1/ok"
    vira "Fase-1-ok". Caminho de disco sem acento é regra do projeto."""
    limpo = "".join(c if (c.isascii() and (c.isalnum() or c in ".-_")) else "-"
                    for c in _sem_acento(texto))
    while "--" in limpo:
        limpo = limpo.replace("--", "-")
    return limpo.strip("-_.") or "item"


def nome_da_pasta(item: str, quando: datetime) -> str:
    """<item>-<AAAA-MM-DD-HHMM>: "6.7-2026-09-25-1640". A data depois do item
    faz as rodadas do mesmo item ficarem juntas e em ordem."""
    return f"{nome_seguro(item)}-{quando:%Y-%m-%d-%H%M}"


def nome_do_relatorio(item: str) -> str:
    """ "conferencia-6-7" (sem extensão). Sem ponto de propósito: o
    relatorio.gravar tira a extensão do destino, e "conferencia-6.7" viraria
    "conferencia-6.md" - foi o que aconteceu na primeira rodada de verdade."""
    return f"conferencia-{nome_seguro(item).replace('.', '-')}"


def nome_do_livro(caminho_do_livro: str) -> str:
    """O nome do arquivo do livro, sem pasta nem extensão (nem o ponto que
    sobra em "...com imagens..pdf")."""
    if not caminho_do_livro:
        return "livro sem nome"
    return Path(caminho_do_livro.replace("\\", "/")).stem.strip(" .") or "livro sem nome"


def titulo_curto(nome_do_item: str) -> str:
    """O nome do item para o título: o de "fase1" é um parágrafo inteiro; o
    título fica com a primeira frase."""
    nome = " ".join((nome_do_item or "").split())
    if len(nome) > 70 and ". " in nome:
        nome = nome.split(". ")[0]
    return nome


# ---------------------------------------------------------------------------
# a lista do gabarito
# ---------------------------------------------------------------------------


def ler_lista(caminho: Path) -> dict:
    """Lê a gabarito/lista.json."""
    try:
        texto = Path(caminho).read_text(encoding="utf-8")
    except OSError as erro:
        raise ErroDeUso(f"Não consegui ler a lista do gabarito em {caminho}.") from erro
    try:
        return json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ErroDeUso(f"A lista do gabarito ({caminho}) está com defeito: {erro}.") from erro


def _itens_por_extenso(lista: dict) -> str:
    """Uma linha por item: "  6.7: Comparação final com o CamScanner"."""
    nomes = lista.get("nomes_dos_itens", {})
    linhas = []
    for chave in lista.get("itens", {}):
        nome = titulo_curto(nomes.get(chave, ""))
        linhas.append(f"  {chave}: {nome}" if nome else f"  {chave}")
    return "\n".join(linhas)


def separar_paginas(texto: str) -> list[str]:
    """ "a, b,,c,a" -> ["a", "b", "c"]: na ordem dada, sem repetir."""
    vistas: list[str] = []
    for parte in (texto or "").split(","):
        parte = parte.strip()
        if parte and parte not in vistas:
            vistas.append(parte)
    return vistas


def paginas_do_item(lista: dict, item: str | None, pedidas: list[str] | None = None) -> list[str]:
    """As páginas a conferir: as do item na lista, ou as de --paginas.

    Levanta ErroDeUso com a lista dos itens que existem quando o item não
    existe, e com o nome da página quando uma página pedida não existe.
    """
    itens = lista.get("itens", {})
    if not item:
        raise ErroDeUso("Diga qual item conferir. Os itens que existem são:\n"
                        + _itens_por_extenso(lista))
    if item not in itens:
        raise ErroDeUso(f"O item \"{item}\" não existe na lista do gabarito. "
                        "Os itens que existem são:\n" + _itens_por_extenso(lista))
    ids = list(itens[item]) if pedidas is None else list(pedidas)
    if not ids:
        raise ErroDeUso("Nenhuma página para conferir: a lista de páginas está vazia.")
    paginas = lista.get("paginas", {})
    faltam = [pid for pid in ids if pid not in paginas]
    if faltam:
        raise ErroDeUso(
            "Estas páginas não existem no gabarito: " + ", ".join(faltam) + ".\n"
            "As páginas que existem são: " + ", ".join(paginas) + ".")
    return ids


def ler_detalhe(entrada: dict) -> tuple[float, float, float, float] | None:
    """O campo "detalhe" de uma página: (x0, y0, x1, y1) em fração da página,
    de 0 a 1, a partir do canto de cima à esquerda. None se não houver."""
    valor = entrada.get("detalhe")
    if valor is None:
        return None
    if (not isinstance(valor, (list, tuple)) or len(valor) != 4
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in valor)):
        raise ErroDeUso(f"O \"detalhe\" {valor!r} não serve: são quatro números "
                        "de 0 a 1, [x0, y0, x1, y1].")
    x0, y0, x1, y1 = (float(v) for v in valor)
    if not (0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0):
        raise ErroDeUso(f"O \"detalhe\" {list(valor)} não serve: precisa de "
                        "0 <= x0 < x1 <= 1 e 0 <= y0 < y1 <= 1.")
    return x0, y0, x1, y1


def referencia_camscanner(lista: dict, pid: str) -> dict | None:
    """A entrada de "camscanner" cuja página do gabarito é pid (a chave da
    entrada é o nome das fotos, que pode ser outro: escola_p037 -> escola_p035)."""
    for chave, entrada in lista.get("camscanner", {}).items():
        if entrada.get("pagina_gabarito") == pid:
            return {"chave": chave, **entrada}
    return None


def referencia_scantailor(lista: dict, pid: str) -> dict | None:
    """A entrada de "scantailor_24_09" da página pid, só se ela tiver saída
    (duas páginas do teste de 24/09 não chegaram ao fim)."""
    for chave, entrada in lista.get("scantailor_24_09", {}).items():
        if entrada.get("pagina_gabarito") == pid and entrada.get("saida"):
            return {"chave": chave, **entrada}
    return None


def escolher_colunas(lista: dict, pid: str, com_anterior: bool) -> list[str]:
    """As colunas da página, na ordem: original, rodada anterior (se houver),
    resultado, e as referências que existem para aquela página."""
    colunas = [ORIGINAL]
    if com_anterior:
        colunas.append(ANTERIOR)
    colunas.append(RESULTADO)
    if referencia_camscanner(lista, pid) is not None:
        colunas.append(CAMSCANNER)
    if referencia_scantailor(lista, pid) is not None:
        colunas.append(SCANTAILOR)
    return colunas


def recorte_da_captura(entrada: dict, foto: str = "magico_pro") -> tuple[int, int, int, int] | None:
    """Onde está a página na captura de tela do celular: (x0, y0, x1, y1) em
    pixels da captura, x1/y1 = o primeiro pixel fora. None se a lista não disser."""
    valor = (entrada.get("recorte_da_pagina") or {}).get(foto)
    if valor is None:
        return None
    if (not isinstance(valor, (list, tuple)) or len(valor) != 4
            or not all(isinstance(v, int) and not isinstance(v, bool) for v in valor)):
        raise ErroDeUso(f"O \"recorte_da_pagina\" {valor!r} não serve: são quatro "
                        "números inteiros, [x0, y0, x1, y1], em pixels da captura.")
    x0, y0, x1, y1 = valor
    if not (0 <= x0 < x1 and 0 <= y0 < y1):
        raise ErroDeUso(f"O \"recorte_da_pagina\" {list(valor)} não serve: "
                        "precisa de x0 < x1 e y0 < y1.")
    return x0, y0, x1, y1


# ---------------------------------------------------------------------------
# imagens: ler, gravar, reduzir, recortar
# ---------------------------------------------------------------------------


def para_bgr(img: np.ndarray) -> np.ndarray:
    """uint8 BGR de 3 canais, venha a imagem como vier: cinza, 16 bits, com
    transparência (vira fundo branco) ou float de 0 a 1."""
    img = np.asarray(img)
    if img.dtype == bool:
        img = img.astype(np.uint8) * 255
    elif img.dtype == np.uint16:
        img = (img >> 8).astype(np.uint8)
    elif img.dtype.kind == "f":
        escala = 255.0 if float(np.nanmax(img)) <= 1.0 else 1.0
        img = np.clip(np.nan_to_num(img) * escala, 0, 255).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.ndim == 3 and img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2BGR)
    if img.ndim == 3 and img.shape[2] == 4:
        alfa = img[:, :, 3:4].astype(np.float32) / 255.0
        cor = img[:, :, :3].astype(np.float32)
        return np.clip(cor * alfa + 255.0 * (1.0 - alfa), 0, 255).astype(np.uint8)
    return np.ascontiguousarray(img[:, :, :3])


def ler_imagem(caminho: Path) -> np.ndarray:
    """PNG, JPG ou TIF em BGR uint8. Lê por np.fromfile, que aceita caminho com
    acento (o cv2.imread do Windows não aceita). Só lê: nunca grava no arquivo."""
    caminho = Path(caminho)
    dados = np.fromfile(str(caminho), dtype=np.uint8)
    img = cv2.imdecode(dados, cv2.IMREAD_UNCHANGED)
    del dados
    if img is None:
        # Plano B para o que o OpenCV não abre (TIF com compressão rara...).
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None   # a saída do ScanTailor tem 94 megapixels
        with Image.open(caminho) as aberta:
            img = np.array(aberta.convert("RGB"))[:, :, ::-1]
    return para_bgr(img)


def gravar_imagem(caminho: Path, img: np.ndarray, qualidade: int = 90) -> Path:
    """Grava PNG (sem perda) ou JPG, pela extensão. Aceita caminho com acento."""
    caminho = Path(caminho)
    extensao = caminho.suffix.lower()
    if extensao in (".jpg", ".jpeg"):
        parametros = [cv2.IMWRITE_JPEG_QUALITY, int(qualidade)]
    elif extensao == ".png":
        parametros = [cv2.IMWRITE_PNG_COMPRESSION, 3]
    else:
        parametros = []
    ok, codificada = cv2.imencode(extensao, img, parametros)
    if not ok:
        raise OSError(f"não consegui codificar {caminho.name}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    codificada.tofile(str(caminho))
    return caminho


def reduzir_para_caber(img: np.ndarray, altura_max: int, largura_max: int) -> np.ndarray:
    """Reduz (nunca amplia) até caber em altura_max x largura_max."""
    altura, largura = img.shape[:2]
    escala = min(1.0, altura_max / altura, largura_max / largura)
    if escala >= 1.0:
        return img
    tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))
    return cv2.resize(img, tamanho, interpolation=cv2.INTER_AREA)


def limitar_lado(img: np.ndarray, lado_max: int = LADO_MAX_EM_MEMORIA) -> np.ndarray:
    """Reduz só o que passar de lado_max no lado maior."""
    return reduzir_para_caber(img, lado_max, lado_max)


def ajustar_para_caber(img: np.ndarray, altura_max: int, largura_max: int) -> np.ndarray:
    """Reduz OU amplia até encostar em altura_max x largura_max. Os painéis da
    página inteira saem todos da mesma altura (a foto do CamScanner, pequena,
    é ampliada), e no navegador as colunas ficam do mesmo tamanho."""
    altura, largura = img.shape[:2]
    escala = min(altura_max / altura, largura_max / largura)
    if abs(escala - 1.0) < 1e-3:
        return img.copy()
    tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))
    metodo = cv2.INTER_AREA if escala < 1.0 else cv2.INTER_CUBIC
    return cv2.resize(img, tamanho, interpolation=metodo)


def ajustar_lado_maior(img: np.ndarray, lado: int) -> np.ndarray:
    """Reduz ou amplia até o lado maior ter `lado` pixels. Ampliar usa
    interpolação cúbica (a foto do CamScanner, pequena, fica borrada - é a
    verdade dela); reduzir usa média de área."""
    altura, largura = img.shape[:2]
    escala = lado / max(altura, largura)
    if abs(escala - 1.0) < 1e-3:
        return img.copy()
    tamanho = (max(1, round(largura * escala)), max(1, round(altura * escala)))
    metodo = cv2.INTER_AREA if escala < 1.0 else cv2.INTER_CUBIC
    return cv2.resize(img, tamanho, interpolation=metodo)


def caixa_em_pixels(detalhe: tuple[float, float, float, float], largura: int,
                    altura: int) -> tuple[int, int, int, int]:
    """O detalhe (fração da página) em pixels daquela imagem, com pelo menos
    1 pixel de cada lado e sem sair dela."""
    x0, y0, x1, y1 = detalhe
    a = min(max(int(round(x0 * largura)), 0), largura - 1)
    b = min(max(int(round(y0 * altura)), 0), altura - 1)
    c = min(max(int(round(x1 * largura)), a + 1), largura)
    d = min(max(int(round(y1 * altura)), b + 1), altura)
    return a, b, c, d


def xadrez(altura: int, largura: int, lado: int = 12) -> np.ndarray:
    """Quadriculado cinza-claro: "aqui a imagem não tem nada" (como os
    programas de imagem mostram a transparência)."""
    ys, xs = np.indices((altura, largura))
    claro = ((ys // lado + xs // lado) % 2 == 0)
    saida = np.where(claro, 236, 206).astype(np.uint8)
    return cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)


def recortar(img: np.ndarray, caixa: tuple[int, int, int, int]) -> np.ndarray:
    """Recorta a caixa (x0, y0, x1, y1) em pixels. O que cair fora da imagem
    vira xadrez - a margem que o programa cortou aparece como "não tem", e o
    recorte fica do mesmo tamanho nas colunas todas."""
    x0, y0, x1, y1 = (int(v) for v in caixa)
    x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)
    altura, largura = img.shape[:2]
    saida = xadrez(y1 - y0, x1 - x0)
    a, b = max(0, x0), max(0, y0)
    c, d = min(largura, x1), min(altura, y1)
    if c > a and d > b:
        saida[b - y0:d - y0, a - x0:c - x0] = img[b:d, a:c]
    return saida


def juntar_lado_a_lado(partes: list[np.ndarray]) -> np.ndarray:
    """Folha que o programa dividiu em duas páginas: as duas lado a lado, com
    uma faixa cinza entre elas (o que sobra embaixo da mais baixa fica branco)."""
    altura = max(p.shape[0] for p in partes)
    blocos: list[np.ndarray] = []
    for numero, parte in enumerate(partes):
        if numero:
            blocos.append(np.full((altura, LARGURA_DA_FAIXA, 3), COR_DA_FAIXA, np.uint8))
        if parte.shape[0] < altura:
            sobra = np.full((altura - parte.shape[0], parte.shape[1], 3), 255, np.uint8)
            parte = np.vstack([parte, sobra])
        blocos.append(parte)
    return np.hstack(blocos)


def quase_cinza(img: np.ndarray) -> bool:
    """A imagem é preto, branco e cinza (as três cores quase iguais)? Serve
    para escolher PNG (sem perda, e pequeno nesse caso) ou JPG."""
    amostra = reduzir_para_caber(img, 800, 800).astype(np.int16)
    return bool(np.abs(amostra[:, :, 0] - amostra[:, :, 1]).max() < 12
                and np.abs(amostra[:, :, 1] - amostra[:, :, 2]).max() < 12)


# ---------------------------------------------------------------------------
# alinhamento: achar o mesmo ponto do livro em cada coluna
# ---------------------------------------------------------------------------


@dataclass
class Pontos:
    """Pontos marcantes de uma imagem (SIFT), já na escala da imagem inteira."""

    xy: np.ndarray                   # (N, 2), em pixels da imagem inteira
    descritores: np.ndarray | None   # (N, 128)
    escala: float                    # pixels de trabalho por pixel da imagem


@dataclass
class Alinhamento:
    """Como levar um ponto do original para a outra imagem."""

    matriz: np.ndarray | None   # 2x3: giro + escala + deslocamento
    pontos: int                 # quantos pontos concordaram com a matriz
    certo: bool                 # a matriz passou nas conferências de alinhar


def caixa_do_conteudo(cinza: np.ndarray) -> tuple[int, int, int, int]:
    """Onde está a tinta na imagem. Serve para a saída do ScanTailor, que é
    uma folha grande e branca com o conteúdo pequeno no meio: sem recortar, o
    texto fica miúdo demais para achar pontos em comum com o original. Se a
    tinta ocupa quase tudo (o caso comum), devolve a imagem inteira."""
    altura, largura = cinza.shape[:2]
    inteira = (0, 0, largura, altura)
    escala = min(1.0, 1000 / max(altura, largura))
    pequena = cinza if escala >= 1.0 else cv2.resize(
        cinza, (max(1, round(largura * escala)), max(1, round(altura * escala))),
        interpolation=cv2.INTER_AREA)
    papel = float(np.median(pequena))
    tinta = pequena < min(papel - 50.0, 200.0)
    ys, xs = np.nonzero(tinta)
    if len(xs) < 50:
        return inteira
    x0, x1 = np.percentile(xs, [0.5, 99.5])
    y0, y1 = np.percentile(ys, [0.5, 99.5])
    folga = 0.03 * max(pequena.shape[:2])
    a = max(0, int((x0 - folga) / escala))
    b = max(0, int((y0 - folga) / escala))
    c = min(largura, int(math.ceil((x1 + folga) / escala)))
    d = min(altura, int(math.ceil((y1 + folga) / escala)))
    if c <= a or d <= b or (c - a) * (d - b) > 0.6 * largura * altura:
        return inteira
    return a, b, c, d


def achar_pontos(img: np.ndarray, recortar_conteudo: bool = False,
                 largura_da_pagina: float | None = None) -> Pontos:
    """Os pontos SIFT da imagem.

    Sem largura_da_pagina, a imagem é reduzida a LADO_ALINHAR no lado maior
    (é o que se faz com o original). Com ela, a imagem é reduzida OU ampliada
    (até 3 vezes) para a página ficar com essa largura - a mesma do original
    reduzido. Medido em 25/09/2026: com a foto do CamScanner da "Escola" (426
    pixels de largura) contra o original reduzido (1446), 3,4 vezes maior, o
    alinhamento falhava; com as duas do mesmo tamanho, acertou.
    """
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dx = dy = 0
    if recortar_conteudo:
        a, b, c, d = caixa_do_conteudo(cinza)
        cinza, dx, dy = cinza[b:d, a:c], a, b
    altura, largura = cinza.shape[:2]
    if largura_da_pagina:
        escala = min(3.0, max(0.05, largura_da_pagina / largura))
        # teto de trabalho: uma imagem muito alta não passa de 1,5 x LADO_ALINHAR
        escala = min(escala, 1.5 * LADO_ALINHAR / max(altura, largura))
    else:
        escala = min(1.0, LADO_ALINHAR / max(altura, largura))
    if abs(escala - 1.0) > 1e-3:
        metodo = cv2.INTER_AREA if escala < 1.0 else cv2.INTER_CUBIC
        cinza = cv2.resize(cinza, (max(1, round(largura * escala)), max(1, round(altura * escala))),
                           interpolation=metodo)
    else:
        escala = 1.0
    sift = cv2.SIFT_create(nfeatures=PONTOS_SIFT)
    chaves, descritores = sift.detectAndCompute(cinza, None)
    if not chaves or descritores is None:
        return Pontos(np.zeros((0, 2), np.float32), None, escala)
    xy = np.float32([k.pt for k in chaves]) / escala + np.float32([dx, dy])
    return Pontos(xy, descritores, escala)


def _estimar(origem: np.ndarray, destino: np.ndarray, limiar: float,
             minimo: int, fracao: float) -> Alinhamento:
    """Giro + escala + deslocamento que mais pontos aceitam (RANSAC), e as
    conferências: pontos suficientes, escala possível e giro pequeno (o
    programa só endireita alguns graus; uma matriz girada 40 graus é
    alinhamento errado, não página girada)."""
    matriz, aceitos = cv2.estimateAffinePartial2D(
        origem, destino, method=cv2.RANSAC, ransacReprojThreshold=limiar,
        maxIters=5000, confidence=0.995)
    if matriz is None:
        return Alinhamento(None, 0, False)
    pontos = int(aceitos.sum()) if aceitos is not None else 0
    escala = math.hypot(matriz[0, 0], matriz[1, 0])
    giro = math.degrees(math.atan2(matriz[1, 0], matriz[0, 0]))
    certo = (pontos >= minimo and pontos >= fracao * len(origem)
             and 0.05 <= escala <= 20.0 and abs(giro) <= 10.0)
    return Alinhamento(matriz, pontos, certo)


def alinhar(original: Pontos, outra: Pontos,
            regiao: tuple[float, float, float, float] | None = None) -> Alinhamento:
    """Como o original vira a outra imagem, pelos pontos em comum.

    Primeiro tenta só com os pontos perto do detalhe (`regiao`, em pixels do
    original): assim uma folha que o programa dividiu em duas, ou uma página
    que o ScanTailor desentortou, ainda acerta o ponto certo. Sem pontos
    suficientes ali, vale o alinhamento da página inteira.

    Arriscado mudar: a razão de Lowe (0,75), o limiar do RANSAC e os mínimos
    de pontos. Afrouxar deixa passar alinhamento errado sem aviso; apertar faz
    mais colunas caírem na posição proporcional.
    """
    if (original.descritores is None or outra.descritores is None
            or len(original.xy) < 8 or len(outra.xy) < 8):
        return Alinhamento(None, 0, False)
    pares = cv2.BFMatcher(cv2.NORM_L2).knnMatch(original.descritores, outra.descritores, k=2)
    bons = [p[0] for p in pares if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
    if len(bons) < 8:
        return Alinhamento(None, len(bons), False)
    origem = original.xy[[m.queryIdx for m in bons]].astype(np.float32)
    destino = outra.xy[[m.trainIdx for m in bons]].astype(np.float32)
    limiar = 3.0 / outra.escala   # 3 pixels na imagem reduzida
    if regiao is not None:
        x0, y0, x1, y1 = regiao
        perto = ((origem[:, 0] >= x0) & (origem[:, 0] <= x1)
                 & (origem[:, 1] >= y0) & (origem[:, 1] <= y1))
        if int(perto.sum()) >= 10:
            local = _estimar(origem[perto], destino[perto], limiar, minimo=10, fracao=0.25)
            if local.certo:
                return local
    return _estimar(origem, destino, limiar, minimo=15, fracao=0.15)


def regiao_de_busca(caixa: tuple[int, int, int, int], largura: int,
                    altura: int) -> tuple[float, float, float, float]:
    """O detalhe com folga (metade do tamanho dele, e pelo menos 10% da
    página de cada lado): os pontos que decidem o alinhamento local."""
    x0, y0, x1, y1 = caixa
    folga_x = max(0.5 * (x1 - x0), 0.1 * largura)
    folga_y = max(0.5 * (y1 - y0), 0.1 * altura)
    return (max(0.0, x0 - folga_x), max(0.0, y0 - folga_y),
            min(float(largura), x1 + folga_x), min(float(altura), y1 + folga_y))


def levar_detalhe(caixa_original: tuple[int, int, int, int],
                  detalhe: tuple[float, float, float, float],
                  alinhamento: Alinhamento, forma: tuple[int, ...]
                  ) -> tuple[np.ndarray, tuple[int, int, int, int], bool]:
    """O detalhe na outra imagem: (os 4 cantos, para desenhar; a caixa, para
    recortar; se veio do alinhamento). Sem alinhamento certo, o detalhe cai na
    mesma fração da página (False: a página avisa que pode estar deslocado).

    Com alinhamento certo, a caixa pode sair em parte da imagem - é a margem
    que o programa cortou, por exemplo: recortar() mostra essa parte em
    xadrez, e a página avisa quando é muita (fracao_dentro)."""
    altura, largura = forma[:2]
    x0, y0, x1, y1 = caixa_original
    cantos = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float64)
    if alinhamento.certo and alinhamento.matriz is not None:
        matriz = alinhamento.matriz.astype(np.float64)
        levados = cantos @ matriz[:, :2].T + matriz[:, 2]
        a, b = np.floor(levados.min(axis=0)).astype(int)
        c, d = np.ceil(levados.max(axis=0)).astype(int)
        return levados, (int(a), int(b), max(int(c), int(a) + 1), max(int(d), int(b) + 1)), True
    caixa = caixa_em_pixels(detalhe, largura, altura)
    a, b, c, d = caixa
    return np.array([[a, b], [c, b], [c, d], [a, d]], dtype=np.float64), caixa, False


def fracao_dentro(caixa: tuple[int, int, int, int], forma: tuple[int, ...]) -> float:
    """Quanto da caixa (0 a 1) cai dentro da imagem."""
    altura, largura = forma[:2]
    x0, y0, x1, y1 = caixa
    area = max(1, (x1 - x0) * (y1 - y0))
    dentro = max(0, min(x1, largura) - max(x0, 0)) * max(0, min(y1, altura) - max(y0, 0))
    return dentro / area


# ---------------------------------------------------------------------------
# de onde vem o "depois"
# ---------------------------------------------------------------------------


@dataclass
class Depois:
    """O "depois" de uma página, do jeito que a fonte entregou."""

    imagem: np.ndarray | None
    segundos: float | None = None           # o processamento daquela página
    segundos_analise: float | None = None   # só no programa: a análise automática
    partes: int = 1                         # quantas páginas saíram da folha
    aviso: str | None = None                # por que não há imagem, se não houver
    arquivo: Path | None = None             # a imagem pronta de onde veio (--pasta-depois)


# A aplicação Qt fica viva até o fim do processo (mesma ideia do
# teste_velocidade.py): não abre janela, só dá casa às tarefas do programa.
_APLICACAO_QT = None


def _garantir_aplicacao_qt():
    global _APLICACAO_QT
    from PySide6.QtCore import QCoreApplication

    if _APLICACAO_QT is None:
        _APLICACAO_QT = QCoreApplication.instance() or QCoreApplication(["conferencia"])
    return _APLICACAO_QT


def paginas_do_pdf(caminho: Path, dpi: int) -> list[np.ndarray]:
    """As páginas do PDF de saída do programa, como imagem BGR.

    O programa grava cada página como UMA imagem (core.pdf_io.EscritorPDF):
    ela é tirada do PDF tal como foi gravada, pixel por pixel, sem desenhar de
    novo. Se a página não tiver exatamente uma imagem, ela é desenhada no DPI
    de saída do programa.
    """
    import fitz

    partes: list[np.ndarray] = []
    with fitz.open(caminho) as documento:
        for pagina in documento:
            img = None
            imagens = pagina.get_images(full=True)
            if len(imagens) == 1:
                try:
                    pix = fitz.Pixmap(documento, imagens[0][0])
                    if pix.alpha or pix.n not in (1, 3):
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    dados = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
                    img = cv2.cvtColor(dados, cv2.COLOR_GRAY2BGR if pix.n == 1 else cv2.COLOR_RGB2BGR)
                    del pix
                except Exception:  # noqa: BLE001 - desenhar a página é o plano B
                    img = None
            if img is None:
                pix = pagina.get_pixmap(dpi=dpi, alpha=False)
                dados = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
                img = cv2.cvtColor(dados, cv2.COLOR_GRAY2BGR if pix.n == 1 else cv2.COLOR_RGB2BGR)
                del pix
            partes.append(np.ascontiguousarray(img))
    return partes


def processar_pelo_programa(pdf: Path, filtro: str, pasta: Path) -> Depois:
    """O "depois" do programa de hoje, pelo MESMO caminho do programa de verdade.

    Faz o que o programa faz com um livro de uma página só (o PDF do gabarito,
    com as camadas originais), sem a tela - o mesmo que o teste_velocidade.py
    faz (medir_abrir e medir_processar):

    1. ui/tarefas.py, TarefaAnalise.run -> core.pipeline.analisar_projeto: a
       análise automática (dividir, ângulo, bordas, cor), com as caixas da tela
       "O que fazer" como o programa traz (modelos.Projeto) e o filtro pedido;
    2. ui/tarefas.py, TarefaProcessar.run -> core.pipeline.processar: o botão
       "Confirmar e processar" (dividir, cortar, endireitar, achar gravura e
       letra, filtro, gravar o PDF, a Projeto.qualidade_dpi);
    3. as páginas do PDF gravado viram a imagem do resultado (paginas_do_pdf).

    Os run() são os mesmos que as QThreads do programa executam; aqui rodam
    direto, sem thread, porque não há tela para manter viva. Arriscado mudar:
    qualquer atalho aqui faria a conferência mostrar outro programa.
    """
    from modelos import Projeto
    from ui.tarefas import TarefaAnalise, TarefaProcessar

    projeto = Projeto(caminho_entrada=str(pdf), nome=Path(pdf).stem)
    projeto.filtro_padrao = filtro

    analisado: dict = {}
    analise = TarefaAnalise(projeto)
    analise.concluida.connect(lambda resultado: analisado.setdefault("projeto", resultado))
    analise.falhou.connect(lambda mensagem: analisado.setdefault("erro", mensagem))
    inicio = time.perf_counter()
    analise.run()
    segundos_analise = time.perf_counter() - inicio
    if "projeto" not in analisado:
        return Depois(None, segundos_analise=segundos_analise,
                      aviso="a análise automática do programa não terminou: "
                            f"{analisado.get('erro', 'o programa não disse por quê')}")

    projeto = analisado["projeto"]
    pasta.mkdir(parents=True, exist_ok=True)
    projeto.caminho_saida = str(pasta / "saida.pdf")
    feito: dict = {}
    tarefa = TarefaProcessar(projeto)
    tarefa.concluida.connect(lambda caminho: feito.setdefault("caminho", caminho))
    tarefa.falhou.connect(lambda mensagem: feito.setdefault("erro", mensagem))
    tarefa.cancelada.connect(lambda: feito.setdefault("erro", "o processamento foi cancelado"))
    inicio = time.perf_counter()
    tarefa.run()
    segundos = time.perf_counter() - inicio
    if "caminho" not in feito:
        return Depois(None, segundos=segundos, segundos_analise=segundos_analise,
                      aviso="o programa não terminou de processar: "
                            f"{feito.get('erro', 'o programa não disse por quê')} "
                            "(o detalhe técnico fica no erros.log do programa)")

    caminho = Path(feito["caminho"])
    partes = paginas_do_pdf(caminho, projeto.qualidade_dpi)
    caminho.unlink(missing_ok=True)
    imagem = partes[0] if len(partes) == 1 else juntar_lado_a_lado(partes)
    return Depois(imagem, segundos, segundos_analise, len(partes))


class FonteDoPrograma:
    """O "depois" é o programa de hoje (ver processar_pelo_programa)."""

    tipo = "programa"

    def __init__(self, filtro: str) -> None:
        from core.filtros import NOMES_AMIGAVEIS

        self.filtro = filtro
        self.nome_do_filtro = NOMES_AMIGAVEIS.get(filtro, filtro)
        self.aquecimento_s: float | None = None
        self.detector: bool | None = None
        self.dpi: int | None = None
        self._temporaria: Path | None = None

    def preparar(self, dizer: Callable[[str], None]) -> None:
        """O mesmo aquecimento que o programa faz ao ligar (sem ele, a primeira
        página levaria junto o tempo de carregar o detector de gravura e letra)."""
        _garantir_aplicacao_qt()
        from core.aquecimento import aquecer_dependencias_pesadas
        from core.detectar_regioes import _detector
        from modelos import Projeto

        dizer("Preparando: o mesmo aquecimento que o programa faz ao ligar...")
        inicio = time.perf_counter()
        aquecer_dependencias_pesadas()
        self.aquecimento_s = time.perf_counter() - inicio
        self.detector = bool(_detector.disponivel)
        self.dpi = Projeto(caminho_entrada="").qualidade_dpi
        dizer(f"  levou {formatar_segundos(self.aquecimento_s)}; detector de gravura e letra: "
              + ("carregado" if self.detector else "NÃO CARREGOU"))
        self._temporaria = Path(tempfile.mkdtemp(prefix="conferencia_"))

    def obter(self, pid: str, pdf: Path, antes: np.ndarray) -> Depois:
        if not Path(pdf).is_file():
            return Depois(None, aviso=f"não achei o PDF da página: {pdf}")
        return processar_pelo_programa(Path(pdf), self.filtro, self._temporaria / pid)

    def encerrar(self) -> None:
        if self._temporaria is not None:
            shutil.rmtree(self._temporaria, ignore_errors=True)

    def rotulo(self) -> str:
        return f"Resultado: {self.nome_do_filtro}"

    def descrever(self) -> dict:
        return {"tipo": self.tipo, "filtro": self.filtro, "nome_do_filtro": self.nome_do_filtro,
                "detector": self.detector, "aquecimento_s": self.aquecimento_s, "dpi": self.dpi}


def carregar_funcao(especificacao: str) -> Callable:
    """ "modulo:funcao" -> a função. O módulo pode ser um nome com pontos
    (core.meu_modulo) ou o caminho de um arquivo .py."""
    modulo, _, nome = (especificacao or "").rpartition(":")
    if not modulo or not nome:
        raise ErroDeUso("Use --funcao modulo:funcao, por exemplo "
                        "--funcao core.meu_modulo:tirar_fundo.")
    try:
        if modulo.lower().endswith(".py") or "/" in modulo or "\\" in modulo:
            arquivo = Path(modulo)
            if not arquivo.is_file():
                raise ErroDeUso(f"Não achei o arquivo {arquivo}.")
            spec = importlib.util.spec_from_file_location(f"_conferencia_{arquivo.stem}", arquivo)
            carregado = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(carregado)
        else:
            carregado = importlib.import_module(modulo)
    except ErroDeUso:
        raise
    except Exception as erro:  # noqa: BLE001 - vira mensagem em português
        raise ErroDeUso(f"Não consegui carregar o módulo {modulo}: "
                        f"{type(erro).__name__}: {erro}") from erro
    funcao = getattr(carregado, nome, None)
    if not callable(funcao):
        raise ErroDeUso(f"O módulo {modulo} não tem a função {nome}.")
    return funcao


def _imagem_da_saida(saida) -> np.ndarray | None:
    """O que a função devolveu, como imagem. Aceita também (imagem, algo), que
    é o formato dos filtros de core/filtros.py."""
    if isinstance(saida, np.ndarray):
        return saida
    if isinstance(saida, (tuple, list)):
        for valor in saida:
            if isinstance(valor, np.ndarray):
                return valor
    return None


class FonteFuncao:
    """O "depois" é uma função sozinha: funcao(caminho_do_pdf, imagem_antes),
    em que caminho_do_pdf é o PDF de uma página do gabarito (com as camadas
    originais, para a Fase 1.1) e imagem_antes é o PNG do gabarito em BGR
    uint8 (o padrão do OpenCV). Ela devolve a imagem "depois"."""

    tipo = "funcao"

    def __init__(self, especificacao: str) -> None:
        self.especificacao = especificacao
        self.funcao = carregar_funcao(especificacao)

    def preparar(self, dizer: Callable[[str], None]) -> None:
        dizer(f"O depois: a função {self.especificacao}")

    def obter(self, pid: str, pdf: Path, antes: np.ndarray) -> Depois:
        inicio = time.perf_counter()
        try:
            saida = self.funcao(Path(pdf), antes.copy())
        except Exception as erro:  # noqa: BLE001 - a página vira aviso; as outras seguem
            traceback.print_exc()
            return Depois(None, segundos=time.perf_counter() - inicio,
                          aviso=f"a função deu erro: {type(erro).__name__}: {erro}")
        segundos = time.perf_counter() - inicio
        img = _imagem_da_saida(saida)
        if img is None:
            return Depois(None, segundos=segundos, aviso="a função não devolveu uma imagem")
        return Depois(para_bgr(img), segundos=segundos)

    def encerrar(self) -> None:
        pass

    def rotulo(self) -> str:
        return f"Resultado: {self.especificacao}"

    def descrever(self) -> dict:
        return {"tipo": self.tipo, "funcao": self.especificacao}


def _ler_dados(caminho: Path) -> dict | None:
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def resolver_pasta_de_imagens(pasta: Path) -> tuple[Path, dict | None]:
    """A pasta onde estão as imagens, e o dados.json quando ela é de uma
    conferência. Aceita a pasta de uma conferência (usa resultado\\), a
    própria resultado\\ de uma conferência, ou uma pasta qualquer."""
    pasta = Path(pasta)
    if (pasta / "dados.json").is_file() and (pasta / "resultado").is_dir():
        return pasta / "resultado", _ler_dados(pasta / "dados.json")
    if pasta.name == "resultado" and (pasta.parent / "dados.json").is_file():
        return pasta, _ler_dados(pasta.parent / "dados.json")
    return pasta, None


def achar_imagem(pasta: Path, pid: str) -> Path | None:
    """<pasta>\\<id>.png (ou .jpg, .jpeg, .tif, .tiff)."""
    for extensao in EXTENSOES:
        candidato = Path(pasta) / f"{pid}{extensao}"
        if candidato.is_file():
            return candidato
    return None


def descrever_rodada(dados: dict | None) -> str:
    """ "rodada de 25/09/2026 às 16:40, do programa no filtro Mágico pro"
    (sem parênteses: a frase entra dentro de outros parênteses no texto)."""
    if not dados:
        return ""
    try:
        quando = datetime.fromisoformat(dados.get("quando", ""))
        texto = f"rodada de {quando:%d/%m/%Y} às {quando:%H:%M}"
    except (TypeError, ValueError):
        texto = "rodada anterior"
    origem = dados.get("origem") or {}
    if origem.get("tipo") == "programa":
        filtro = origem.get("nome_do_filtro", origem.get("filtro", "?"))
        return f"{texto}, do programa no filtro {filtro}"
    if origem.get("tipo") == "funcao":
        return f"{texto}, da função {origem.get('funcao', '?')}"
    if origem.get("tipo") == "pasta":
        return f"{texto}, com imagens prontas"
    return texto


class FontePasta:
    """O "depois" são imagens prontas: <pasta>\\<id>.png (ou .jpg/.tif). Se a
    pasta for de outra conferência, os tempos e a descrição vêm do dados.json
    dela - é o jeito de pôr a opinião sem processar tudo de novo."""

    tipo = "pasta"

    def __init__(self, pasta: Path) -> None:
        self.pasta_pedida = Path(pasta)
        self.pasta, self.dados = resolver_pasta_de_imagens(self.pasta_pedida)
        if not self.pasta.is_dir():
            raise ErroDeUso(f"A pasta das imagens prontas não existe: {self.pasta_pedida}")
        self._paginas_antes = {p.get("id"): p for p in (self.dados or {}).get("paginas", [])}

    def preparar(self, dizer: Callable[[str], None]) -> None:
        dizer(f"O depois: as imagens de {self.pasta}")

    def obter(self, pid: str, pdf: Path, antes: np.ndarray) -> Depois:
        arquivo = achar_imagem(self.pasta, pid)
        if arquivo is None:
            return Depois(None, aviso=f"não achei {pid}.png (nem .jpg ou .tif) em {self.pasta}")
        anterior = self._paginas_antes.get(pid) or {}
        return Depois(ler_imagem(arquivo), segundos=anterior.get("tempo_s"),
                      segundos_analise=anterior.get("tempo_analise_s"),
                      partes=int(anterior.get("partes") or 1), arquivo=arquivo)

    def encerrar(self) -> None:
        pass

    def rotulo(self) -> str:
        origem = (self.dados or {}).get("origem") or {}
        if origem.get("tipo") == "programa":
            return f"Resultado: {origem.get('nome_do_filtro', 'o programa')}"
        if origem.get("tipo") == "funcao":
            return f"Resultado: {origem.get('funcao', 'a função')}"
        return "Resultado"

    def descrever(self) -> dict:
        return {"tipo": self.tipo, "pasta": str(self.pasta_pedida),
                "reaproveitada": descrever_rodada(self.dados) or None,
                "origem_reaproveitada": (self.dados or {}).get("origem")}


class RodadaAnterior:
    """A coluna "Rodada anterior": as imagens de outra conferência (ou de uma
    pasta qualquer), para ver o que uma mudança de código mudou."""

    def __init__(self, pasta: Path) -> None:
        self.pasta_pedida = Path(pasta)
        self.pasta, self.dados = resolver_pasta_de_imagens(self.pasta_pedida)
        if not self.pasta.is_dir():
            raise ErroDeUso(f"A pasta da rodada anterior não existe: {self.pasta_pedida}")

    def imagem(self, pid: str) -> Path | None:
        return achar_imagem(self.pasta, pid)

    def descrever(self) -> dict:
        return {"pasta": str(self.pasta_pedida), "rodada": descrever_rodada(self.dados) or None}


# ---------------------------------------------------------------------------
# as referências (CamScanner, ScanTailor), preparadas uma vez só
# ---------------------------------------------------------------------------


def pagina_do_camscanner(gabarito: Path, entrada: dict,
                         referencias: Path) -> tuple[np.ndarray | None, Path | None, str | None]:
    """A foto Mágico Pro recortada só na página (o campo recorte_da_pagina).
    Devolve (imagem, arquivo do recorte em tamanho cheio, aviso)."""
    foto = gabarito / entrada.get("magico_pro", "")
    if not entrada.get("magico_pro") or not foto.is_file():
        return None, None, f"não achei a foto do CamScanner ({foto})"
    captura = ler_imagem(foto)
    caixa = recorte_da_captura(entrada, "magico_pro")
    aviso = None
    if caixa is None:
        pagina = captura
        nome = f"{nome_seguro(entrada.get('chave', foto.stem))}-captura-inteira.png"
        aviso = ("a lista não diz onde está a página na captura (recorte_da_pagina): "
                 "a coluna mostra a captura inteira, com o aplicativo em volta")
    else:
        x0, y0, x1, y1 = caixa
        pagina = captura[y0:y1, x0:x1].copy()
        nome = f"{nome_seguro(entrada.get('chave', foto.stem))}-{x0}-{y0}-{x1}-{y1}.png"
    arquivo = referencias / "camscanner" / nome
    if not arquivo.is_file():
        gravar_imagem(arquivo, pagina)
    return pagina, arquivo, aviso


def saida_do_scantailor(gabarito: Path, entrada: dict, pid: str,
                        referencias: Path) -> tuple[np.ndarray | None, Path | None, str | None]:
    """A saída do ScanTailor de 24/09 (TIF de 600 DPI, que o navegador não
    abre). Na primeira vez, grava uma cópia em tamanho cheio que o navegador
    abre (PNG se for preto e branco, JPG se tiver cor). Devolve (imagem já
    reduzida a LADO_MAX_EM_MEMORIA, arquivo em tamanho cheio, aviso)."""
    origem = gabarito / entrada.get("saida", "")
    if not entrada.get("saida") or not origem.is_file():
        return None, None, f"não achei a saída do ScanTailor ({origem})"
    pasta = referencias / "scantailor-24-09"
    feitos = [pasta / f"{pid}{ext}" for ext in (".png", ".jpg")]
    pronto = next((f for f in feitos if f.is_file()
                   and f.stat().st_mtime >= origem.stat().st_mtime), None)
    img = ler_imagem(origem)
    if pronto is None:
        pronto = feitos[0] if quase_cinza(img) else feitos[1]
        gravar_imagem(pronto, img, QUALIDADE_REFERENCIA)
    return limitar_lado(img), pronto, None


# ---------------------------------------------------------------------------
# uma página: as colunas, os painéis
# ---------------------------------------------------------------------------


def endereco(alvo: Path | None, pasta: Path) -> str | None:
    """O endereço do arquivo para o link do HTML, relativo à pasta da
    conferência (funciona sem internet, e com a pasta do projeto em qualquer
    disco). Em outro disco, vira file:///."""
    if alvo is None:
        return None
    alvo = Path(alvo).resolve()
    try:
        relativo = os.path.relpath(alvo, Path(pasta).resolve())
    except ValueError:
        return alvo.as_uri()
    return urllib.parse.quote(relativo.replace("\\", "/"))


def guardar_resultado(depois: Depois, pasta: Path, pid: str) -> Path:
    """Guarda o "depois" em tamanho cheio: resultado\\<id>.png (ou .jpg).

    Imagem pronta em PNG ou JPG (--pasta-depois) é copiada byte a byte: sem
    gravar de novo, sem mudar nada e sem gastar tempo. O resto (o programa, a
    função, um TIF, que o navegador não abre) é gravado em PNG, sem perda.
    """
    pasta.mkdir(parents=True, exist_ok=True)
    origem = depois.arquivo
    if origem is not None and Path(origem).suffix.lower() in (".png", ".jpg", ".jpeg"):
        destino = pasta / f"{pid}{Path(origem).suffix.lower()}"
        shutil.copyfile(origem, destino)
        return destino
    return gravar_imagem(pasta / f"{pid}.png", depois.imagem)


def gravar_paineis(img: np.ndarray, poligono: np.ndarray, caixa: tuple[int, int, int, int],
                   pasta_paineis: Path, nome: str) -> tuple[str, str]:
    """Os dois JPG de uma coluna: a página inteira reduzida, com o retângulo
    do detalhe desenhado, e o detalhe ampliado. Devolve os endereços relativos
    à pasta da conferência (paineis/...)."""
    painel = ajustar_para_caber(img, ALTURA_PAINEL, LARGURA_MAX_PAINEL)
    escala = painel.shape[1] / img.shape[1]
    cantos = np.round(np.asarray(poligono, np.float64) * escala).astype(np.int32)
    espessura = max(3, round(max(painel.shape[:2]) / 200))
    cv2.polylines(painel, [cantos.reshape(-1, 1, 2)], True, COR_DO_RETANGULO, espessura, cv2.LINE_AA)
    gravar_imagem(pasta_paineis / f"{nome}.jpg", painel, QUALIDADE_PAINEL)
    del painel
    detalhe = ajustar_lado_maior(recortar(img, caixa), LADO_DETALHE)
    gravar_imagem(pasta_paineis / f"{nome}-detalhe.jpg", detalhe, QUALIDADE_DETALHE)
    return f"paineis/{nome}.jpg", f"paineis/{nome}-detalhe.jpg"


def _registro_da_pagina(numero: int, pid: str, entrada: dict) -> dict:
    return {
        "numero": numero,
        "id": pid,
        "livro": entrada.get("livro", ""),
        "livro_nome": nome_do_livro(entrada.get("livro", "")),
        "pagina": entrada.get("pagina"),
        "para_que": entrada.get("para_que", ""),
        "a_confirmar": bool(entrada.get("a_confirmar")),
        "observacao": entrada.get("observacao", ""),
        "detalhe": None,
        "aspecto_detalhe": 1.0,
        "tempo_s": None,
        "tempo_analise_s": None,
        "partes": 1,
        "avisos": [],
        "colunas": [],
        "falhou": False,
    }


def conferir_pagina(numero: int, pid: str, lista: dict, gabarito: Path, fonte, anterior,
                    pasta: Path, referencias: Path, dizer: Callable[[str], None]) -> dict:
    """Uma página inteira: o "depois", as colunas, os painéis. Devolve o
    registro da página (o que vai para o dados.json e para o texto).

    Uma página por vez na memória: só o original fica aberto a página toda;
    cada coluna é lida, alinhada, vira painel e é solta antes da próxima.
    """
    entrada = lista["paginas"][pid]
    registro = _registro_da_pagina(numero, pid, entrada)
    detalhe = ler_detalhe(entrada)
    if detalhe is None:
        registro["avisos"].append("Esta página ainda não tem \"detalhe\" na lista do gabarito: "
                                  "o detalhe ampliado mostra a página inteira.")
        detalhe = (0.0, 0.0, 1.0, 1.0)
    registro["detalhe"] = list(detalhe)

    png = gabarito / entrada.get("png", "")
    pdf = gabarito / entrada.get("pdf", "")
    if not png.is_file():
        registro["falhou"] = True
        registro["avisos"].append(f"Não achei a imagem do gabarito ({png}): a página ficou sem painéis.")
        return registro
    original = ler_imagem(png)
    altura, largura = original.shape[:2]
    caixa_original = caixa_em_pixels(detalhe, largura, altura)
    registro["aspecto_detalhe"] = ((caixa_original[2] - caixa_original[0])
                                   / (caixa_original[3] - caixa_original[1]))
    regiao = regiao_de_busca(caixa_original, largura, altura)
    pontos_do_original: Pontos | None = None

    for posicao, chave in enumerate(escolher_colunas(lista, pid, anterior is not None), start=1):
        rotulo = fonte.rotulo() if chave == RESULTADO else ROTULOS[chave]
        coluna = {"chave": chave, "posicao": posicao, "rotulo": rotulo,
                  "titulo": f"{posicao}. {rotulo}", "painel": None, "detalhe": None,
                  "cheia": None, "alinhamento": None, "aviso": None, "aspecto": None}
        registro["colunas"].append(coluna)
        img, cheia, aviso = None, None, None
        try:
            if chave == ORIGINAL:
                img, cheia = original, png
            elif chave == ANTERIOR:
                arquivo = anterior.imagem(pid)
                if arquivo is None:
                    aviso = f"a rodada anterior não tem {pid}"
                else:
                    img, cheia = limitar_lado(ler_imagem(arquivo)), arquivo
            elif chave == RESULTADO:
                dizer(f"    o depois ({fonte.rotulo().lower()})...")
                depois = fonte.obter(pid, pdf, original)
                registro["tempo_s"] = depois.segundos
                registro["tempo_analise_s"] = depois.segundos_analise
                registro["partes"] = depois.partes
                if depois.imagem is None:
                    aviso = depois.aviso or "sem imagem"
                    registro["falhou"] = True
                else:
                    cheia = guardar_resultado(depois, pasta / "resultado", pid)
                    img = limitar_lado(depois.imagem)
                del depois
            elif chave == CAMSCANNER:
                img, cheia, aviso = pagina_do_camscanner(
                    gabarito, referencia_camscanner(lista, pid), referencias)
            elif chave == SCANTAILOR:
                img, cheia, aviso = saida_do_scantailor(
                    gabarito, referencia_scantailor(lista, pid), pid, referencias)
        except Exception as erro:  # noqa: BLE001 - a coluna vira aviso; as outras seguem
            traceback.print_exc()
            img, aviso = None, f"deu erro ao preparar esta coluna: {type(erro).__name__}: {erro}"
            if chave == RESULTADO:
                registro["falhou"] = True
        if img is None:
            coluna["aviso"] = aviso or "sem imagem"
            continue
        if aviso:   # a coluna tem imagem, mas com ressalva (ex.: sem recorte_da_pagina)
            registro["avisos"].append(f"Coluna {posicao} ({rotulo}): {aviso}.")

        if chave == ORIGINAL:
            x0, y0, x1, y1 = caixa_original
            poligono = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float64)
            caixa = caixa_original
        else:
            if pontos_do_original is None:
                pontos_do_original = achar_pontos(original)
            # A página do mesmo tamanho nas duas imagens; se não der certo, uma
            # segunda tentativa só reduzindo (o jeito do original).
            alinhamento = alinhar(pontos_do_original, achar_pontos(
                img, recortar_conteudo=True,
                largura_da_pagina=pontos_do_original.escala * largura), regiao)
            if not alinhamento.certo:
                segunda = alinhar(pontos_do_original, achar_pontos(img, recortar_conteudo=True), regiao)
                if segunda.certo:
                    alinhamento = segunda
            poligono, caixa, certo = levar_detalhe(caixa_original, detalhe, alinhamento, img.shape)
            coluna["alinhamento"] = {"certo": certo, "pontos": alinhamento.pontos}
            if not certo:
                registro["avisos"].append(
                    f"No detalhe da coluna {posicao} ({rotulo}), não consegui achar o mesmo ponto "
                    "com certeza: o recorte está na mesma posição proporcional da página e pode "
                    "estar deslocado.")
            elif fracao_dentro(caixa, img.shape) < 0.5:
                registro["avisos"].append(
                    f"No detalhe da coluna {posicao} ({rotulo}), boa parte do ponto do detalhe não "
                    "existe nesta imagem (aparece quadriculado): ela foi cortada ali.")
        coluna["painel"], coluna["detalhe"] = gravar_paineis(
            img, poligono, caixa, pasta / "paineis", f"{numero:02d}-{pid}-{posicao}-{chave}")
        coluna["aspecto"] = img.shape[1] / img.shape[0]
        coluna["cheia"] = endereco(cheia, pasta)
        coluna["caixa"] = [int(v) for v in caixa]
        del img
    return registro


# ---------------------------------------------------------------------------
# o texto da página de conferência
# ---------------------------------------------------------------------------

# Vai dentro do .md como bloco HTML: o navegador aplica (páginas largas, painéis
# ocupando a largura toda); o PDF (Story do PyMuPDF) ignora e usa as larguras
# escritas em cada <img>. Seguro mudar.
ESTILO_DA_CONFERENCIA = """<style>
body { max-width: 120rem; }
body > p, body > ul, body > ol, body > blockquote, body > pre, body > h1,
body > h2, body > h3, body > .faixa { max-width: 58rem; }
table.paineis { display: table; width: 100%; table-layout: fixed; border-collapse: separate;
  border-spacing: 10px 0; margin: .3em 0 1.3em; font-size: .92rem; }
table.paineis td { border: none; padding: 0 0 .9em; vertical-align: top; }
table.paineis td b { display: block; font-weight: 620; padding: .2em 0 .3em; }
table.paineis img { display: block; width: auto; height: auto; max-width: 100%;
  max-height: 82vh; margin: 0; }
table.paineis .falta { display: block; padding: 2.5em 1em; background: #f1efec; color: #55524d;
  border-radius: 6px; }
.faixa { padding: .8em 1.1em; border-radius: 8px; margin: 1em 0 1.4em; }
.faixa p { margin: 0; }
.faixa.falta { background: #fff1c2; border: 1px solid #e0b400; color: #3d3000; }
.faixa.pronta { background: #dff3e2; border: 1px solid #5aa469; color: #123d1c; }
@media (prefers-color-scheme: dark) {
  table.paineis .falta { background: #262421; color: #b0aca6; }
  .faixa.falta { background: #3d3200; border-color: #8a6d00; color: #fff1c2; }
  .faixa.pronta { background: #173d20; border-color: #3f7a4c; color: #dff3e2; }
}
</style>"""


def paineis_por_linha(aspecto: float, quantos: int) -> int:
    """Quantos painéis lado a lado: o máximo que cabe em SOMA_DOS_ASPECTOS,
    dividindo as linhas por igual (4 painéis largos saem 2 + 2, não 3 + 1)."""
    if quantos <= 1:
        return max(quantos, 1)
    maximo = quantos
    while maximo > 1 and maximo * max(aspecto, 0.05) > SOMA_DOS_ASPECTOS:
        maximo -= 1
    linhas = math.ceil(quantos / maximo)
    return math.ceil(quantos / linhas)


def _atributo(texto: str) -> str:
    return html.escape(str(texto), quote=True)


def tabela_de_paineis(colunas: list[dict], campo: str, aspecto: float) -> str:
    """As imagens de um campo ("painel" ou "detalhe") lado a lado, cada uma
    com o título da coluna em cima e o link para a imagem em tamanho cheio.

    O título vai DENTRO da mesma célula da imagem, e não numa linha de
    cabeçalho: no PDF, a quebra de página separava o título da imagem. A
    largura escrita em cada <img> é a do PDF; no navegador o estilo manda.
    """
    quantos = len(colunas)
    por_linha = paineis_por_linha(aspecto, quantos)
    largura = int((LARGURA_UTIL_PDF - 8 * por_linha) / por_linha)
    largura = max(40, min(largura, int(ALTURA_MAX_PDF * max(aspecto, 0.05))))
    linhas = ['<table class="paineis">']
    for inicio in range(0, quantos, por_linha):
        grupo = colunas[inicio:inicio + por_linha]
        celulas = []
        for coluna in grupo:
            titulo = f"<b>{html.escape(coluna['titulo'])}</b>"
            arquivo = coluna.get(campo)
            if arquivo:
                imagem = (f'<img src="{_atributo(arquivo)}" width="{largura}" '
                          f'alt="{_atributo(coluna["titulo"])}">')
                if coluna.get("cheia"):
                    imagem = f'<a href="{_atributo(coluna["cheia"])}" target="_blank">{imagem}</a>'
                celulas.append(f"<td>{titulo}{imagem}</td>")
            else:
                motivo = coluna.get("aviso") or "sem imagem"
                celulas.append(f'<td>{titulo}<span class="falta">Sem imagem: '
                               f"{html.escape(motivo)}.</span></td>")
        celulas += ["<td></td>"] * (por_linha - len(grupo))
        linhas.append("<tr>" + "".join(celulas) + "</tr>")
    linhas.append("</table>")
    return "\n".join(linhas)


def _quando(dados: dict) -> str:
    try:
        quando = datetime.fromisoformat(dados["quando"])
        return f"{quando:%d/%m/%Y} às {quando:%H:%M}"
    except (KeyError, TypeError, ValueError):
        return "?"


def _frase_do_depois(dados: dict) -> str:
    """De onde veio o "depois", em uma ou duas frases."""
    origem = dados.get("origem") or {}
    if origem.get("tipo") == "programa":
        frase = ("O **depois** é o programa de hoje: cada página foi aberta sozinha (o PDF de "
                 "uma página do gabarito, com as camadas originais) e passou pelo mesmo caminho "
                 "do botão \"Confirmar e processar\", com o que a análise automática do programa "
                 f"decidiu, no filtro **{origem.get('nome_do_filtro', '?')}**.")
        if origem.get("filtro") == FILTRO_PADRAO:
            frase += (" O Mágico pro é o filtro mais parecido com o CamScanner, que é o "
                      "resultado-alvo do plano.")
        return frase
    if origem.get("tipo") == "funcao":
        return (f"O **depois** é a função `{origem.get('funcao', '?')}`, rodada sozinha em cada "
                "página: ela recebe o PDF de uma página do gabarito e a imagem original, e "
                "devolve a imagem pronta.")
    frase = f"O **depois** são imagens já prontas, da pasta `{origem.get('pasta', '?')}`."
    if origem.get("reaproveitada"):
        frase += (f" São as imagens da {origem['reaproveitada']}, reaproveitadas sem processar "
                  "de novo.")
    return frase


def _frase_do_tempo(pagina: dict, dados: dict) -> str:
    """O tempo daquela página, em frase."""
    origem = dados.get("origem") or {}
    tempo, analise = pagina.get("tempo_s"), pagina.get("tempo_analise_s")
    if origem.get("tipo") == "funcao":
        return f"A função levou {formatar_segundos(tempo)}." if tempo is not None else ""
    if tempo is None:
        if origem.get("tipo") == "pasta":
            return "Tempo de processamento: não medido (as imagens já vieram prontas)."
        return "Tempo de processamento: não medido."
    frase = f"Processada em {formatar_segundos(tempo)}"
    if analise is not None:
        frase += f" (a análise automática levou mais {formatar_segundos(analise)})"
    if origem.get("tipo") == "pasta" and origem.get("reaproveitada"):
        frase += f", na {origem['reaproveitada']}"
    return frase + "."


def _bloco_da_pagina(pagina: dict, dados: dict) -> list[str]:
    """O bloco de uma página: título, o que olhar, tempo, avisos e os painéis."""
    t: list[str] = []
    numero_pdf = pagina.get("pagina")
    t += [f"## {pagina['numero']}. {pagina['livro_nome']}, página {numero_pdf} do PDF", ""]
    t += [f"**O que olhar:** {pagina.get('para_que') or '(a lista do gabarito não diz)'}", ""]
    t += [f"`{pagina['id']}`. {_frase_do_tempo(pagina, dados)}".strip(), ""]
    if pagina.get("a_confirmar"):
        aviso = ("> **Atenção:** esta página ainda está *a confirmar*: o Samuel precisa dizer se "
                 "ela é a página certa antes de ela virar gabarito fixo.")
        if pagina.get("observacao"):
            aviso += f" Observação do gabarito: {pagina['observacao']}"
        t += [aviso, ""]
    if (pagina.get("partes") or 1) > 1:
        t += [f"> **Atenção:** o programa dividiu esta folha em {pagina['partes']} páginas. No "
              "Resultado elas aparecem lado a lado, separadas por uma faixa cinza.", ""]
    for aviso in pagina.get("avisos", []):
        t += [f"> **Atenção:** {aviso}", ""]
    colunas = pagina.get("colunas") or []
    if not colunas:
        return t
    aspecto_pagina = max([c["aspecto"] for c in colunas if c.get("aspecto")] or [0.7])
    t += ["**A página inteira** (o retângulo rosa é de onde vem o detalhe):", ""]
    t += [tabela_de_paineis(colunas, "painel", aspecto_pagina), ""]
    t += ["**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:", ""]
    t += [tabela_de_paineis(colunas, "detalhe", pagina.get("aspecto_detalhe") or 1.0), ""]
    return t


def montar_texto(dados: dict) -> str:
    """A página de conferência em Markdown (com os painéis em blocos HTML),
    montada só a partir do dados.json - pode ser refeita sem processar nada.

    O texto fixo diz PRONTO PARA CONFERIR só quando há opinião do verificador,
    e nunca diz que o item foi aceito: quem marca o item no plano é o Samuel.
    """
    paginas = dados.get("paginas") or []
    nome = titulo_curto(dados.get("nome_do_item", ""))
    titulo = f"# Conferência do item {dados['item']}" + (f": {nome}" if nome else "")
    t: list[str] = [titulo, "", ESTILO_DA_CONFERENCIA, ""]

    opiniao = (dados.get("opiniao") or "").strip()
    if opiniao:
        t += ['<div class="faixa pronta"><p><strong>PRONTO PARA CONFERIR.</strong> O verificador '
              "olhou as imagens e escreveu a opinião dele logo abaixo, com as ressalvas. Quem "
              "marca o item no plano é o Samuel.</p></div>", ""]
    else:
        t += ['<div class="faixa falta"><p><strong>Falta a opinião do verificador.</strong> As '
              "imagens abaixo ainda não foram conferidas por ele: esta página ainda não está "
              "pronta para o Samuel.</p></div>", ""]

    quantas = len(paginas)
    resumo = (f"Gerada em {_quando(dados)}, com {quantas} "
              f"{'página-gabarito' if quantas == 1 else 'páginas-gabarito'} do item "
              f"{dados['item']}. " + _frase_do_depois(dados))
    anterior = dados.get("anterior")
    if anterior:
        resumo += (f" A coluna **Rodada anterior** mostra as imagens de `{anterior.get('pasta')}`"
                   + (f" ({anterior['rodada']})" if anterior.get("rodada") else "")
                   + ", para ver o que a mudança de código mudou.")
    t += [resumo, ""]
    t += ["Teste **de olho**: quem decide é o Samuel, olhando.", ""]
    origem = dados.get("origem") or {}
    if origem.get("tipo") == "programa" and origem.get("detector") is False:
        t += ["> **Atenção:** o detector de gravura e letra do programa (modelos\\doclayout.onnx) "
              "NÃO carregou. Sem ele o programa trata a página inteira do mesmo jeito: este "
              "resultado não é o do programa de verdade.", ""]
    falharam = [p["id"] for p in paginas if p.get("falhou")]
    if falharam:
        t += ["> **Atenção:** " + ("a página " if len(falharam) == 1 else "as páginas ")
              + ", ".join(f"`{p}`" for p in falharam)
              + " ficaram sem resultado (o motivo está no bloco de cada uma).", ""]

    t += ["Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que "
          "importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A "
          "explicação completa está no fim, em \"Como ler esta página\".", ""]

    if opiniao:
        t += ["## Opinião do verificador", "", opiniao, ""]

    for pagina in paginas:
        t += _bloco_da_pagina(pagina, dados)

    tem_camscanner = any(c.get("chave") == CAMSCANNER for p in paginas for c in p.get("colunas", []))
    t += ["## Como ler esta página", "",
          "- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe "
          "ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira "
          "mostra de onde o detalhe saiu, em cada coluna.",
          "- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi "
          "escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que "
          "existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.",
          "- **Clique** em qualquer imagem para abrir em tamanho cheio.",
          "- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, "
          "a margem que o programa cortou)."]
    if tem_camscanner:
        t += ["- A foto do CamScanner é uma captura da tela do celular: a página tem só uns 520 "
              "pontos de largura. Serve para comparar a cor e o branco do papel, não o detalhe "
              "(ampliada, ela fica borrada)."]
    t += [""]

    t += ["## Como esta página foi feita", ""]
    if dados.get("comando"):
        t += [f"- **Comando:** `{dados['comando']}`"]
    t += [f"- **Pasta:** `{dados.get('pasta', '')}`. Nela, `resultado\\` tem o resultado de cada "
          "página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), "
          "`paineis\\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. "
          "O original fica no gabarito (`gabarito\\paginas\\`); as referências recortadas, em "
          "`relatorios\\conferir\\_referencias\\`."]
    if origem.get("tipo") == "programa":
        t += ["- **O caminho do programa:** `TarefaAnalise.run` (a análise automática: dividir, "
              "ângulo, bordas, cor) e depois `TarefaProcessar.run`, que chama `processar`, o "
              "mesmo que o botão \"Confirmar e processar\" dispara. As caixas da tela \"O que "
              "fazer\" ficaram como o programa traz (dividir, limpar, endireitar, cortar as "
              f"bordas, achar gravura e letra), a {origem.get('dpi') or '?'} DPI. O resultado é "
              "a imagem que o programa gravou no PDF de saída, sem desenhar de novo.",
              "- **Antes das páginas**, o mesmo aquecimento que o programa faz ao ligar: levou "
              f"{formatar_segundos(origem.get('aquecimento_s'))}, fora dos tempos de cada página. "
              "Detector de gravura e letra: "
              + ("carregado." if origem.get("detector") else "**NÃO carregou.**")]
    t += ["- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita "
          "a página, e as referências têm outro enquadramento; por isso o detalhe não sai da "
          "mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada "
          "imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o "
          "alinhamento não dá certeza, o bloco da página avisa.",
          f"- **Levou** {formatar_segundos(dados.get('duracao_s'))} no total.",
          f"- **Versões:** {dados.get('versoes', '')}", ""]
    return "\n".join(t)


# ---------------------------------------------------------------------------
# o comando
# ---------------------------------------------------------------------------


def achar_filtro(texto: str) -> str:
    """ "Mágico pro", "magico_pro", "mágico-pro" -> "magico_pro"."""
    from core.filtros import FILTROS, NOMES_AMIGAVEIS

    def normal(valor: str) -> str:
        valor = _sem_acento(valor).lower().replace("_", " ").replace("-", " ")
        return " ".join(valor.split())

    procurado = normal(texto or "")
    for chave in FILTROS:
        if procurado in (normal(chave), normal(NOMES_AMIGAVEIS.get(chave, chave))):
            return chave
    nomes = ", ".join(NOMES_AMIGAVEIS.get(f, f) for f in FILTROS)
    raise ErroDeUso(f"Não conheço o filtro \"{texto}\". Os filtros são: {nomes}.")


def ler_opiniao(caminho: str) -> str | None:
    """O texto do verificador (Markdown). Vazio conta como sem opinião."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ErroDeUso(f"Não achei o arquivo da opinião: {arquivo}")
    try:
        texto = arquivo.read_text(encoding="utf-8-sig").strip()
    except (OSError, UnicodeDecodeError) as erro:
        raise ErroDeUso(f"Não consegui ler a opinião em {arquivo} (tem de ser texto UTF-8).") from erro
    return texto or None


def criar_pasta(destino: Path, item: str, quando: datetime) -> Path:
    """relatorios\\conferir\\<item>-<AAAA-MM-DD-HHMM>; se já existir (duas
    rodadas no mesmo minuto), ganha -2, -3..."""
    base = Path(destino) / nome_da_pasta(item, quando)
    pasta, numero = base, 1
    while pasta.exists():
        numero += 1
        pasta = base.with_name(f"{base.name}-{numero}")
    pasta.mkdir(parents=True)
    return pasta


class _Analisador(argparse.ArgumentParser):
    """argparse com o erro em português (o detalhe do argparse vem junto)."""

    def error(self, message: str) -> None:  # noqa: D401 - nome do argparse
        self.print_usage(sys.stderr)
        self.exit(2, f"Não entendi o pedido ({message}). Veja: conferencia.py --help\n")


def _ler_argumentos(argv: list[str] | None) -> argparse.Namespace:
    analisador = _Analisador(
        prog="conferencia.py",
        description="Gera a página de antes/depois de um item do plano, com as "
                    "páginas-gabarito dele (gabarito\\lista.json).")
    analisador.add_argument("item", nargs="?",
                            help="o item do plano, como está em \"itens\" na lista (ex.: 6.7, fase1)")
    analisador.add_argument("--paginas",
                            help="troca a lista de páginas do item: id1,id2 (ex.: horas_p026,escola_p035)")
    de_onde = analisador.add_mutually_exclusive_group()
    de_onde.add_argument("--funcao", metavar="MODULO:FUNCAO",
                         help="o depois é uma função: funcao(caminho_do_pdf, imagem_antes) -> imagem")
    de_onde.add_argument("--pasta-depois", metavar="PASTA",
                         help="o depois são imagens prontas: PASTA\\<id>.png (ou .jpg/.tif), ou a "
                              "pasta de uma conferência já feita")
    analisador.add_argument("--filtro",
                            help="o filtro do programa (padrão: Mágico pro, o mais parecido com o "
                                 "CamScanner). Só vale quando o depois é o programa de hoje")
    analisador.add_argument("--comparar-com", metavar="PASTA",
                            help="acrescenta a coluna \"Rodada anterior\", com as imagens de uma "
                                 "conferência feita antes (ou de uma pasta de imagens)")
    analisador.add_argument("--opiniao", metavar="ARQUIVO",
                            help="o texto do verificador (opinião e ressalvas), em UTF-8")
    argumentos = analisador.parse_args(argv)
    if argumentos.filtro and (argumentos.funcao or argumentos.pasta_depois):
        analisador.error("--filtro só vale quando o depois é o programa de hoje, "
                         "sem --funcao nem --pasta-depois")
    return argumentos


def _acertar_o_terminal() -> None:
    """Acento que o terminal não sabe mostrar vira "?", em vez de derrubar a
    conferência no meio (mesma ideia do teste_velocidade.py)."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            if fluxo is None or not hasattr(fluxo, "reconfigure"):
                continue
            if fluxo.isatty():
                fluxo.reconfigure(errors="replace")
            else:
                fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


def _dizer(texto: str) -> None:
    try:
        print(texto, flush=True)
    except Exception:  # noqa: BLE001 - terminal que falha não para a conferência
        pass


def _versoes() -> str:
    import platform

    partes = [f"Python {platform.python_version()}"]
    try:
        import fitz

        partes.append(f"PyMuPDF {getattr(fitz, 'VersionBind', '?')}")
    except Exception:  # noqa: BLE001
        pass
    partes.append(f"OpenCV {cv2.__version__}")
    partes.append(f"numpy {np.__version__}")
    return " · ".join(partes)


def pico_de_memoria_mb() -> float | None:
    """O maior uso de memória deste processo até agora, em MB (o "pico do
    conjunto de trabalho" do Windows). Serve para conferir a regra "uma página
    por vez na memória": o pico não pode crescer com o número de páginas.
    None se não der para medir."""
    try:
        import psutil

        pico = getattr(psutil.Process().memory_info(), "peak_wset", None)
        return pico / 1024 / 1024 if pico else None
    except Exception:  # noqa: BLE001 - sem a medida a conferência segue
        return None


def _comando(argv: list[str]) -> str:
    return (".venv\\Scripts\\python.exe conferencia.py " + subprocess.list2cmdline(argv)).strip()


def main(argv: list[str] | None = None, *, gabarito: Path | None = None,
         destino: Path | None = None, referencias: Path | None = None) -> int:
    """Um comando, sem perguntar nada. Sai com 0 (deu certo), 1 (alguma página
    ficou sem resultado; a página de conferência sai mesmo assim) ou 2 (o
    pedido não serve: item que não existe, pasta que falta...).

    gabarito, destino e referencias existem para o teste automático; o uso
    normal é sem nenhum (gabarito\\, relatorios\\conferir\\ e
    relatorios\\conferir\\_referencias\\).
    """
    _acertar_o_terminal()
    argv = list(sys.argv[1:] if argv is None else argv)
    argumentos = _ler_argumentos(argv)
    gabarito = Path(gabarito or GABARITO)
    destino = Path(destino or PASTA_CONFERIR)
    referencias = Path(referencias or destino / NOME_REFERENCIAS)

    try:
        lista = ler_lista(gabarito / "lista.json")
        pedidas = separar_paginas(argumentos.paginas) if argumentos.paginas is not None else None
        ids = paginas_do_item(lista, argumentos.item, pedidas)
        opiniao = ler_opiniao(argumentos.opiniao) if argumentos.opiniao else None
        if argumentos.funcao:
            fonte = FonteFuncao(argumentos.funcao)
        elif argumentos.pasta_depois:
            fonte = FontePasta(Path(argumentos.pasta_depois))
        else:
            fonte = FonteDoPrograma(achar_filtro(argumentos.filtro) if argumentos.filtro
                                    else FILTRO_PADRAO)
        anterior = RodadaAnterior(Path(argumentos.comparar_com)) if argumentos.comparar_com else None
        for pid in ids:   # confere o "detalhe" de todas antes de gastar tempo processando
            ler_detalhe(lista["paginas"][pid])
    except ErroDeUso as erro:
        _dizer(str(erro))
        return 2

    try:
        import markdown  # noqa: F401 - só confere que existe
    except ImportError:
        _dizer("Atenção: a biblioteca markdown não está instalada; o .html vai mostrar os "
               "painéis como texto. Instale com: .venv\\Scripts\\python.exe -m pip install markdown")

    quando = datetime.now()
    comeco = time.perf_counter()
    item = argumentos.item
    nome_do_item = lista.get("nomes_dos_itens", {}).get(item, "")
    pasta = criar_pasta(destino, item, quando)
    _dizer(f"Conferência do item {item}" + (f" ({titulo_curto(nome_do_item)})" if nome_do_item else "")
           + f": {len(ids)} {'página' if len(ids) == 1 else 'páginas'}.")
    _dizer(f"Pasta: {pasta}")

    paginas: list[dict] = []
    fonte.preparar(_dizer)
    try:
        for numero, pid in enumerate(ids, start=1):
            _dizer(f"[{numero}/{len(ids)}] {pid}")
            try:
                registro = conferir_pagina(numero, pid, lista, gabarito, fonte, anterior,
                                           pasta, referencias, _dizer)
            except Exception as erro:  # noqa: BLE001 - uma página que falha não derruba as outras
                traceback.print_exc()
                registro = _registro_da_pagina(numero, pid, lista["paginas"][pid])
                registro["falhou"] = True
                registro["avisos"].append(f"A conferência desta página deu erro: "
                                          f"{type(erro).__name__}: {erro}")
            if registro.get("tempo_s") is not None:
                _dizer(f"    {formatar_segundos(registro['tempo_s'])}")
            for aviso in registro.get("avisos", []):
                _dizer(f"    atenção: {aviso}")
            paginas.append(registro)
            gc.collect()
    finally:
        fonte.encerrar()

    dados = {
        "versao": 1,
        "item": item,
        "nome_do_item": nome_do_item,
        "quando": quando.isoformat(timespec="seconds"),
        "comando": _comando(argv),
        "pasta": str(pasta),
        "origem": fonte.descrever(),
        "anterior": anterior.descrever() if anterior else None,
        "opiniao": opiniao,
        "paginas": paginas,
        "duracao_s": time.perf_counter() - comeco,
        "memoria_pico_mb": pico_de_memoria_mb(),
        "versoes": _versoes(),
    }
    (pasta / "dados.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    import relatorio

    # Sem ponto no nome: relatorio.gravar tira a "extensão" do destino, e
    # "conferencia-6.7" viraria "conferencia-6.md".
    arquivos = relatorio.gravar(montar_texto(dados), pasta / nome_do_relatorio(item))
    _dizer("")
    _dizer("Página de conferência gravada em:")
    for formato in ("html", "pdf", "md"):
        if formato in arquivos:
            _dizer(f"  {arquivos[formato]}")
    if "pdf" not in arquivos:
        _dizer("  (o PDF não saiu; o .md e o .html saíram)")
    if dados["memoria_pico_mb"] is not None:
        _dizer(f"Memória máxima usada: {dados['memoria_pico_mb']:.0f} MB.")
    if not opiniao:
        _dizer("Falta a opinião do verificador: rode de novo com --opiniao ARQUIVO "
               f"(e --pasta-depois \"{pasta}\" para não processar tudo de novo).")
    return 1 if any(p.get("falhou") for p in paginas) else 0


if __name__ == "__main__":
    raise SystemExit(main())
