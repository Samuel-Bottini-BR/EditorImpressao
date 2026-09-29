"""Pecas comuns da medicao do item 1.3 (comparar OCRs so para ACHAR o texto).

Nao faz parte do programa: e so a regua desta comparacao. Roda no ambiente de
teste separado (.venv-ocr, Python 3.14), nunca no .venv do programa.

O que tem aqui:
- PAGINAS: as 19 paginas da pesquisa + Graduale 221 a 223 (manuscrito);
- render_pagina: a imagem de trabalho que TODOS os detectores recebem;
- tinta: binarizacao Sauvola igual a do Internet Archive (janela DPI/4, k 0,34);
- mascaras_zonas: as zonas de gabarito/ocr-zonas.json em pixels;
- mascara_linhas: as caixas de linha de um detector, alargadas 15% da altura;
- medir: as tres medidas (texto achado, figura tomada por texto, itens
  pequenos perdidos).

Seguro mudar: a lista de paginas, as cores dos desenhos.
Arriscado mudar: a janela e o k da Sauvola, o alargamento de 15% e a
prioridade das zonas (neutro > texto > nao_pode) -- mudar qualquer um deles
muda todos os numeros e deixa de ser comparavel com o relatorio de 28/09/2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np
from skimage.filters import threshold_sauvola

RAIZ = Path(__file__).resolve().parents[3]          # D:\programas\EditorImpressao
GABARITO = RAIZ / "gabarito"
TRABALHO = RAIZ / "saida_teste" / "ocr-1.3"         # fora do git (saida_teste/)
RELATORIO = Path(__file__).resolve().parents[1]
MODELOS_TESS = RAIZ / "modelos" / "tessdata"        # fora do git (modelos/)

# As 16 do item fase1 da lista.json + Rhetorica 18, Siebmacher 9, Palatino 57
# (as 19 da pesquisa), + Graduale 221-223 para ver manuscrito.
PAGINAS_19 = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
]
PAGINAS_MANUSCRITO_EXTRA = ["graduale_p221", "graduale_p222", "graduale_p223"]
PAGINAS = PAGINAS_19 + PAGINAS_MANUSCRITO_EXTRA

# Paginas obrigatorias da Fase 1 (plano, 28/09): passar de 1% de figura
# tomada por texto nelas REPROVA.
OBRIGATORIAS = {"palatino_p005", "escola_p035", "horas_p011", "horas_p013",
                "horas_p026", "horas_p027", "opusmajus_p020"}

# Idioma do modelo "normal" (tessdata_best) de cada livro.
IDIOMA_LIVRO = {
    "palatino": "ita", "escola": "por", "horas": "fra", "opusmajus": "eng",
    "rhetorica": "lat", "siebmacher": "script/Fraktur", "graduale": "lat",
}

# Livros cujo PDF ja vem com o texto invisivel do Internet Archive (R0).
LIVROS_IA = {"palatino", "opusmajus", "rhetorica", "siebmacher"}

DPI_MAXIMO = 300  # a pesquisa manda medir a 300 DPI; scan menor fica como esta


def livro(pagina: str) -> str:
    return pagina.split("_")[0]


def info_lista(pagina: str) -> dict:
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
    return lista["paginas"][pagina]


def dpi_trabalho(pagina: str) -> float:
    """DPI da imagem de trabalho: o do scan, com teto de 300."""
    return min(float(info_lista(pagina)["dpi_scan"]), DPI_MAXIMO)


def render_pagina(pagina: str) -> tuple[np.ndarray, float]:
    """Imagem de trabalho (RGB) e o zoom usado (pixels por ponto de PDF).

    E a mesma imagem para todos os detectores, e e nela que as zonas e a
    tinta sao medidas. Sem corte nem endireitamento do programa: as paginas
    do gabarito ja estao direitas o bastante (ver Ressalvas do relatorio).
    """
    doc = fitz.open(GABARITO / "paginas" / f"{pagina}.pdf")
    zoom = dpi_trabalho(pagina) / 72.0
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, 3).copy()
    return img, zoom


def caminho_imagem(pagina: str) -> Path:
    return TRABALHO / "imagens" / f"{pagina}.png"


def ler_imagem(pagina: str) -> np.ndarray:
    """RGB da imagem de trabalho ja gravada por preparar.py."""
    bgr = cv2.imread(str(caminho_imagem(pagina)), cv2.IMREAD_COLOR)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def tinta(img_rgb: np.ndarray, dpi: float) -> np.ndarray:
    """Mascara booleana da tinta: Sauvola como o Internet Archive.

    Janela = DPI/4 (impar), k = 0,34 (archive-pdf-tools). Sobre o cinza da
    pagina; tinta colorida (rubrica, iluminura) tambem sai como tinta.
    """
    cinza = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float64)
    janela = int(round(dpi / 4)) | 1
    janela = max(janela, 15)
    # r = 128 (faixa dinamica de 8 bits, o valor classico da Sauvola). Sem ele,
    # o scikit-image usa a faixa do tipo float e a pagina inteira vira "tinta"
    # (medido em 28/09: 88% da Horas 13). Arriscado: tirar o r.
    limiar = threshold_sauvola(cinza, window_size=janela, k=0.34, r=128)
    return cinza < limiar


def _desenhar_forma(mascara: np.ndarray, ret, forma: str, valor: bool) -> None:
    h, w = mascara.shape
    x0, y0, x1, y1 = ret
    px0, py0 = int(round(x0 * w)), int(round(y0 * h))
    px1, py1 = int(round(x1 * w)), int(round(y1 * h))
    tmp = np.zeros_like(mascara, dtype=np.uint8)
    if forma == "elipse":
        centro = ((px0 + px1) // 2, (py0 + py1) // 2)
        eixos = (max(1, (px1 - px0) // 2), max(1, (py1 - py0) // 2))
        cv2.ellipse(tmp, centro, eixos, 0, 0, 360, 1, -1)
    else:
        tmp[py0:py1, px0:px1] = 1
    mascara[tmp.astype(bool)] = valor


def _zona_para_mascara(forma_zona: dict, shape) -> np.ndarray:
    m = np.zeros(shape, dtype=bool)
    _desenhar_forma(m, forma_zona["ret"], forma_zona.get("forma", "ret"), True)
    buraco = forma_zona.get("buraco")
    if buraco:
        _desenhar_forma(m, buraco["ret"], buraco.get("forma", "ret"), False)
    return m


def carregar_zonas() -> dict:
    return json.loads((GABARITO / "ocr-zonas.json").read_text(encoding="utf-8"))["paginas"]


def mascaras_zonas(zonas_pagina: dict, shape) -> dict:
    """Mascaras de texto, nao_pode e neutro, com a prioridade neutro > texto > nao_pode.

    Devolve tambem a lista de (zona, mascara) de cada item de texto, para
    contar os pequenos perdidos, e a mascara 'tabela' (onde a grade nao conta).
    """
    neutro = np.zeros(shape, bool)
    for z in zonas_pagina.get("neutro", []):
        neutro |= _zona_para_mascara(z, shape)
    texto = np.zeros(shape, bool)
    tabela = np.zeros(shape, bool)
    itens = []
    for z in zonas_pagina.get("texto", []):
        m = _zona_para_mascara(z, shape)
        texto |= m
        if z.get("tabela"):
            tabela |= m
        itens.append((z, m & ~neutro))
    figura = np.zeros(shape, bool)
    for z in zonas_pagina.get("nao_pode", []):
        figura |= _zona_para_mascara(z, shape)
    texto &= ~neutro
    figura &= ~(neutro | texto)
    return {"texto": texto, "figura": figura, "neutro": neutro,
            "tabela": tabela & ~neutro, "itens": itens}


def tirar_grade(tinta_m: np.ndarray, onde: np.ndarray) -> np.ndarray:
    """Tira da tinta as linhas retas compridas (grade de tabela) dentro de 'onde'."""
    if not onde.any():
        return tinta_m
    h, w = tinta_m.shape
    t = (tinta_m & onde).astype(np.uint8)
    horiz = cv2.morphologyEx(t, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_RECT, (max(15, w // 50), 1)))
    vert = cv2.morphologyEx(t, cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, h // 25))))
    grade = cv2.dilate((horiz | vert), np.ones((3, 3), np.uint8)).astype(bool)
    return tinta_m & ~(grade & onde)


ALARGAR = 0.15  # 15% da altura da linha, para pegar hastes e pernas


def _altura_poligono(pts: np.ndarray) -> float:
    (_, _), (a, b), _ = cv2.minAreaRect(pts.astype(np.float32))
    return float(min(a, b))


def mascara_linhas(linhas: list[dict], shape, alargar: float = ALARGAR) -> np.ndarray:
    """Une as linhas de um detector numa mascara, cada uma alargada 15% da altura.

    Cada linha e {"poligono": [[x, y], ...]} em pixels da imagem de trabalho
    (retangulo = 4 pontos).
    """
    h, w = shape
    m = np.zeros(shape, np.uint8)
    for ln in linhas:
        pts = np.asarray(ln["poligono"], dtype=np.float64)
        if len(pts) < 3:
            continue
        alt = _altura_poligono(pts)
        r = int(round(alargar * alt))
        x0 = max(0, int(np.floor(pts[:, 0].min())) - r - 1)
        y0 = max(0, int(np.floor(pts[:, 1].min())) - r - 1)
        x1 = min(w, int(np.ceil(pts[:, 0].max())) + r + 2)
        y1 = min(h, int(np.ceil(pts[:, 1].max())) + r + 2)
        if x1 <= x0 or y1 <= y0:
            continue
        local = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillPoly(local, [np.round(pts - [x0, y0]).astype(np.int32)], 1)
        if r > 0:
            local = cv2.dilate(local, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * r + 1, 2 * r + 1)))
        m[y0:y1, x0:x1] |= local
    return m.astype(bool)


def linhas_falsas(linhas: list[dict], zm: dict) -> dict:
    """Conta as linhas que quase nao tocam texto (medida extra, nao estava na pesquisa).

    Uma linha e "falsa" quando menos de 30% da sua area (sem alargar) cai em
    zona de texto ou neutra. Se metade ou mais cai em figura, conta como
    "falsa na figura"; senao, "falsa fora" (papel, mancha do verso, borda do
    scan, pauta de musica no Graduale). As "falsas fora" importam para o 1.4:
    dentro de uma caixa, a tinta fica com a cor -- uma caixa em cima da
    mancha do verso guardaria a mancha.
    """
    h, w = zm["texto"].shape
    ok = zm["texto"] | zm["neutro"]
    na_figura = fora = 0
    for ln in linhas:
        pts = np.asarray(ln["poligono"], dtype=np.float64)
        if len(pts) < 3:
            continue
        x0 = max(0, int(np.floor(pts[:, 0].min())))
        y0 = max(0, int(np.floor(pts[:, 1].min())))
        x1 = min(w, int(np.ceil(pts[:, 0].max())) + 1)
        y1 = min(h, int(np.ceil(pts[:, 1].max())) + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        local = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillPoly(local, [np.round(pts - [x0, y0]).astype(np.int32)], 1)
        local = local.astype(bool)
        area = local.sum()
        if area == 0:
            continue
        if (local & ok[y0:y1, x0:x1]).sum() / area >= 0.3:
            continue
        if (local & zm["figura"][y0:y1, x0:x1]).sum() / area >= 0.5:
            na_figura += 1
        else:
            fora += 1
    return {"falsas_na_figura": na_figura, "falsas_fora": fora}


def medir(tinta_m: np.ndarray, zm: dict, linhas_m: np.ndarray,
          linhas_m_cruas: np.ndarray | None = None) -> dict:
    """As medidas do 1.3 para uma pagina e um detector."""
    tinta_texto = tirar_grade(tinta_m, zm["tabela"]) & zm["texto"]
    tinta_fig = tinta_m & zm["figura"]
    n_texto = int(tinta_texto.sum())
    n_fig = int(tinta_fig.sum())
    achado = float((tinta_texto & linhas_m).sum()) / n_texto if n_texto else None
    tomada = float((tinta_fig & linhas_m).sum()) / n_fig if n_fig else None
    # Medida extra (nao estava na pesquisa): quanto da AREA da figura cai em
    # caixa. Na moldura dourada e na pintura quase nada e "tinta" pela Sauvola
    # (a faixa de ouro e lisa), mas no 1.4 tudo o que nao e tinta dentro de
    # uma caixa vira papel branco -- entao a area coberta e o estrago real.
    n_area = int(zm["figura"].sum())
    area = float((zm["figura"] & linhas_m).sum()) / n_area if n_area else None
    # Medida extra: a mesma "figura tomada", mas com as caixas SEM o alargamento
    # de 15%. Separa "a caixa encosta na figura" (texto colado na moldura,
    # como na Horas 13) de "a caixa cobre a figura".
    cru = None
    if linhas_m_cruas is not None and n_fig:
        cru = float((tinta_fig & linhas_m_cruas).sum()) / n_fig
    perdidos, pequenos = [], 0
    for z, m in zm["itens"]:
        if not z.get("pequeno"):
            continue
        pequenos += 1
        tz = tinta_m & m
        if tz.sum() == 0:
            continue
        if (tz & linhas_m).sum() / tz.sum() < 0.5:
            perdidos.append(z["o_que"])
    return {"texto_achado": achado, "figura_tomada": tomada, "figura_area": area,
            "figura_tomada_sem_alargar": cru,
            "tinta_texto_px": n_texto, "tinta_figura_px": n_fig,
            "pequenos": pequenos, "pequenos_perdidos": perdidos}


def gravar_linhas(detector: str, pagina: str, linhas: list[dict], tempos: list[float],
                  extra: dict | None = None) -> None:
    """Formato unico de saida de todos os detectores."""
    pasta = TRABALHO / "linhas" / detector
    pasta.mkdir(parents=True, exist_ok=True)
    dados = {"detector": detector, "pagina": pagina, "linhas": linhas,
             "tempos_s": tempos, "tempo_mediana_s": float(np.median(tempos)) if tempos else None}
    if extra:
        dados.update(extra)
    (pasta / f"{pagina}.json").write_text(json.dumps(dados), encoding="utf-8")


def ler_linhas(detector: str, pagina: str) -> dict | None:
    arq = TRABALHO / "linhas" / detector / f"{pagina}.json"
    if not arq.exists():
        return None
    return json.loads(arq.read_text(encoding="utf-8"))
