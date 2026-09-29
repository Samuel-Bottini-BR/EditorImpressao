"""Régua do item 1.2: a DLL do ScanTailor dá a mesma máscara que o ScanTailor?

    .venv\\Scripts\\python.exe conferir_gravura_scantailor.py

1. RÉGUA (teste de máquina). Em 24/09 o Samuel rodou o ScanTailor Advanced de
   verdade no modo Misto, e ele gravou a máscara de gravura de 7 páginas em
   gabarito/scantailor-24-09/out/cache/automask/. Para cada uma:
   - acha como a página de entrada virou a página de saída do ScanTailor
     (pontos SIFT do conferencia.py + ajuste fino por ECC; a escala é fixa em
     600 / DPI da entrada, porque a saída foi a 600 DPI);
   - acha o retângulo do conteúdo (onde a saída não é branco puro) e o
     retângulo de trabalho (conteúdo + 20 pontos a 300 DPI, como calcAreas());
   - roda a DLL com essa geometria (detectar_como_no_scantailor) e compara,
     ponto a ponto, dentro do conteúdo, com a máscara do ScanTailor;
   - roda também como o programa vai usar (a página inteira, sem geometria,
     no DPI dela e a 150 DPI) e compara do mesmo jeito.
   A geometria vai para tests/dados/gravura_scantailor_24_09.json (o teste
   automático usa a do Palatino 5).
2. PÁGINAS OBRIGATÓRIAS DA FASE 1 (teste de olho): a máscara por cima da
   página, ao lado do detector de hoje, e o tempo.
3. Relatório em relatorios/fase1-1.2-gravura-scantailor-<data>/ (md, html, pdf).

Não mexe em nada do programa. Lê o gabarito (fora do git) e grava só o
relatório e o .json.

Arriscado mudar: a escala fixa (600 / DPI) e a folga de 40 pontos (20 a 300
DPI, em 600 DPI): são as do ScanTailor para esta saída.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import conferencia as cf  # noqa: E402
from core import gravura_scantailor as gs  # noqa: E402

GABARITO = RAIZ / "gabarito"
TESTE_24_09 = GABARITO / "scantailor-24-09"
PAGINAS_24_09 = ["escola_p007", "horas_p011", "horas_p013", "horas_p047",
                 "palatino_p005", "palatino_p009", "rhetorica_p018"]
DPI_SAIDA = 600                   # a saída do teste de 24/09
FOLGA_DE_TRABALHO = DPI_SAIDA * 20 // 300   # calcAreas(): contentMargin
OBRIGATORIAS = ["palatino_p005", "escola_p035", "horas_p011", "horas_p013",
                "horas_p026", "horas_p027", "opusmajus_p020"]
ARQUIVO_GEOMETRIA = RAIZ / "tests" / "dados" / "gravura_scantailor_24_09.json"
# Páginas que o ScanTailor, sozinho, decidiu serem "claro no escuro" (a detecção
# automática de preto-no-branco dele) e por isso analisou INVERTIDAS. Achado em
# 28/09 na Horas 11: com a página invertida a concordância sobe de 0,39 para 0,81.
PAGINAS_VISTAS_INVERTIDAS = {"horas_p011"}


def dizer(texto: str) -> None:
    print(texto, flush=True)


# ------------------------------------------------------------------ geometria

def dpi_do_png(caminho: Path) -> int:
    """O DPI gravado no PNG, inteiro como o ScanTailor guarda (classe Dpi)."""
    from PIL import Image

    with Image.open(caminho) as im:
        return int(round(im.info["dpi"][0]))


def alinhar_com_a_saida(entrada: np.ndarray, saida: np.ndarray, dpi: int) -> tuple[np.ndarray, dict]:
    """Matriz 2x3 (convenção do OpenCV: centro do ponto) da entrada para a saída do ScanTailor.

    SIFT dá o giro e o deslocamento; a escala fica fixa em 600/DPI; o ECC, a
    300 DPI, acerta o que sobrou (fração de ponto)."""
    pontos_e = cf.achar_pontos(entrada)
    pontos_s = cf.achar_pontos(saida, recortar_conteudo=True)
    bruto = cf.alinhar(pontos_e, pontos_s)
    if not bruto.certo:
        raise RuntimeError("não alinhou a entrada com a saída do ScanTailor")
    m = bruto.matriz
    escala = DPI_SAIDA / dpi
    giro = math.atan2(m[1, 0], m[0, 0])
    a = np.array([[escala * math.cos(giro), -escala * math.sin(giro), m[0, 2]],
                  [escala * math.sin(giro), escala * math.cos(giro), m[1, 2]]])

    cinza_s = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(cinza_s < 250)
    x0, y0 = max(0, xs.min() - 100), max(0, ys.min() - 100)
    x1, y1 = min(cinza_s.shape[1], xs.max() + 100), min(cinza_s.shape[0], ys.max() + 100)
    f = 300.0 / DPI_SAIDA
    alvo = cv2.resize(cinza_s[y0:y1, x0:x1], None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    alvo = alvo.astype(np.float32)
    cinza_e = cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY)

    def levar(matriz):
        b = matriz.copy()
        b[:, 2] -= [x0, y0]
        b *= f
        return cv2.warpAffine(cinza_e, b, (alvo.shape[1], alvo.shape[0]), flags=cv2.INTER_LINEAR,
                              borderValue=255).astype(np.float32)

    w = np.eye(2, 3, dtype=np.float32)
    correlacao, w = cv2.findTransformECC(alvo, levar(a), w, cv2.MOTION_EUCLIDEAN,
                                         (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6),
                                         None, 5)
    # compõe a correção do ECC (no sistema reduzido e recortado) com a matriz
    a_inv = np.linalg.inv(np.vstack([a, [0, 0, 1]]))[:2]
    destino = np.array([[x0 + 100, y0 + 100], [x1 - 100, y0 + 100], [x0 + 100, y1 - 100]], np.float64)
    origem = []
    for p in destino:
        q = w.astype(np.float64) @ np.array([(p[0] - x0) * f, (p[1] - y0) * f, 1.0])
        pe = q / f + [x0, y0]
        origem.append(a_inv @ np.array([pe[0], pe[1], 1.0]))
    final = cv2.getAffineTransform(np.float32(origem), np.float32(destino)).astype(np.float64)
    qualidade = {"pontos_sift": int(bruto.pontos), "correlacao_ecc": round(float(correlacao), 4),
                 "giro_graus": round(math.degrees(math.atan2(final[1, 0], final[0, 0])), 4),
                 "escala": round(math.hypot(final[0, 0], final[1, 0]), 6)}
    return final, qualidade


def geometria(entrada: np.ndarray, saida: np.ndarray, matriz: np.ndarray) -> dict:
    """Transformação no formato do QTransform e os retângulos de conteúdo e de trabalho."""
    a, b, tx = matriz[0]
    c, d, ty = matriz[1]
    # centro do ponto (OpenCV) -> coordenada contínua (Qt): x_qt = x_cv + 0,5
    dx = tx + 0.5 - 0.5 * (a + b)
    dy = ty + 0.5 - 0.5 * (c + d)
    altura, largura = saida.shape[:2]
    # A página levada para a saída (caixa em volta; o giro é de fração de grau).
    cantos = np.array([[0, 0], [entrada.shape[1], 0], [0, entrada.shape[0]],
                       [entrada.shape[1], entrada.shape[0]]], float)
    levados = cantos @ np.array([[a, c], [b, d]]) + [dx, dy]
    (px0, py0), (px1, py1) = levados.min(0), levados.max(0)
    pag = (max(math.ceil(px0), 0), max(math.ceil(py0), 0),
           min(math.floor(px1), largura), min(math.floor(py1), altura))
    # Conteúdo: onde a saída não é branco puro, dentro da página. Fora da página
    # o ScanTailor pinta a "sobra" com a cor do fundo (Livro de Horas), que não é
    # conteúdo; e o conteúdo dele nunca passa da página (calcAreas()).
    ys, xs = np.nonzero((saida != 255).any(axis=2))
    x0, y0 = max(int(xs.min()), pag[0]), max(int(ys.min()), pag[1])
    x1, y1 = min(int(xs.max()) + 1, pag[2]), min(int(ys.max()) + 1, pag[3])
    conteudo = [x0, y0, x1 - x0, y1 - y0]
    cx, cy, cw, ch = conteudo
    wx0 = max(cx - FOLGA_DE_TRABALHO, pag[0])
    wy0 = max(cy - FOLGA_DE_TRABALHO, pag[1])
    wx1 = min(cx + cw + FOLGA_DE_TRABALHO, pag[2])
    wy1 = min(cy + ch + FOLGA_DE_TRABALHO, pag[3])
    return {"transformacao": [float(a), float(c), float(b), float(d), float(dx), float(dy)],
            "retangulo_conteudo": conteudo,
            "retangulo_trabalho": [int(wx0), int(wy0), int(wx1 - wx0), int(wy1 - wy0)],
            "dpi_saida": DPI_SAIDA, "tamanho_saida": [largura, altura]}


def comparar(nossa: np.ndarray, dele: np.ndarray) -> dict:
    """Concordância ponto a ponto entre duas máscaras do mesmo tamanho."""
    inter = int((nossa & dele).sum())
    uniao = int((nossa | dele).sum())
    return {"iou": inter / uniao if uniao else 1.0,
            "iguais": float((nossa == dele).mean()),
            "so_nossa": int((nossa & ~dele).sum()), "so_dele": int((~nossa & dele).sum()),
            "fracao_dele": float(dele.mean()), "fracao_nossa": float(nossa.mean())}


def imagem_de_diferenca(nossa: np.ndarray, dele: np.ndarray, lado: int = 1400) -> np.ndarray:
    """Cinza = os dois marcam; vermelho = só a DLL; azul = só o ScanTailor.
    As diferenças são engrossadas para aparecerem na imagem reduzida."""
    img = np.zeros(nossa.shape + (3,), np.uint8)
    img[nossa & dele] = (170, 170, 170)
    escala = min(1.0, lado / max(nossa.shape))
    pequena = cv2.resize(img, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    grossura = np.ones((5, 5), np.uint8)
    for mascara, cor in (((nossa & ~dele), (0, 0, 255)), ((~nossa & dele), (255, 0, 0))):
        m = cv2.resize(mascara.astype(np.uint8) * 255, (pequena.shape[1], pequena.shape[0]),
                       interpolation=cv2.INTER_AREA) > 0
        m = cv2.dilate(m.astype(np.uint8), grossura) > 0
        pequena[m] = cor
    return pequena


def regua(pasta: Path) -> list[dict]:
    resultados = []
    geometrias = {}
    for nome in PAGINAS_24_09:
        dizer(f"  {nome}")
        entrada = cv2.imread(str(TESTE_24_09 / f"{nome}.png"), cv2.IMREAD_COLOR)
        dpi = dpi_do_png(TESTE_24_09 / f"{nome}.png")
        saida = cv2.imread(str(TESTE_24_09 / "out" / f"{nome}.tif"), cv2.IMREAD_COLOR)
        matriz, qualidade = alinhar_com_a_saida(entrada, saida, dpi)
        geo = geometria(entrada, saida, matriz)
        geo["dpi_entrada"] = dpi
        geo["alinhamento"] = qualidade
        geometrias[nome] = geo
        del saida
        gc.collect()
        _, pilha = cv2.imreadmulti(str(TESTE_24_09 / "out" / "cache" / "automask" / f"{nome}.tif"),
                                   flags=cv2.IMREAD_GRAYSCALE)
        cx, cy, cw, ch = geo["retangulo_conteudo"]
        dele = pilha[0][cy:cy + ch, cx:cx + cw] > 0
        del pilha

        # (a) a conta do ScanTailor, com a geometria dele
        wx, wy, ww, wh = geo["retangulo_trabalho"]
        r = gs.detectar_como_no_scantailor(entrada, DPI_SAIDA, geo["transformacao"], geo["retangulo_trabalho"])
        if not r.disponivel:
            raise RuntimeError(f"DLL indisponível: {r.motivo} {r.detalhe_tecnico}")
        nossa = r.mascara[cy - wy:cy - wy + ch, cx - wx:cx - wx + cw]
        com_geometria = comparar(nossa, dele)
        com_geometria["segundos"] = r.segundos
        cv2.imwrite(str(pasta / f"regua_{nome}.jpg"), imagem_de_diferenca(nossa, dele),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        del r, nossa
        gc.collect()

        # (b) como o programa vai usar: a página inteira, no DPI dela e a 150 DPI
        como_programa = {}
        for rotulo, dpi_uso in (("dpi_da_pagina", dpi), ("150_dpi", 150)):
            fator = dpi_uso / dpi
            img = entrada if fator == 1 else cv2.resize(
                entrada, None, fx=fator, fy=fator, interpolation=cv2.INTER_AREA if fator < 1 else cv2.INTER_CUBIC)
            r = gs.detectar_gravura(img, dpi_uso)
            m = matriz.copy()
            m[:, :2] /= fator
            levada = cv2.warpAffine(r.mascara.astype(np.uint8), m, tuple(geo["tamanho_saida"]),
                                    flags=cv2.INTER_NEAREST, borderValue=0)[cy:cy + ch, cx:cx + cw] > 0
            como_programa[rotulo] = comparar(levada, dele) | {"segundos": r.segundos}
        invertida = None
        if nome in PAGINAS_VISTAS_INVERTIDAS:
            ri = gs.detectar_como_no_scantailor(255 - entrada, DPI_SAIDA, geo["transformacao"],
                                                geo["retangulo_trabalho"])
            nossa_inv = ri.mascara[cy - wy:cy - wy + ch, cx - wx:cx - wx + cw]
            invertida = comparar(nossa_inv, dele)
            cv2.imwrite(str(pasta / f"regua_{nome}_invertida.jpg"), imagem_de_diferenca(nossa_inv, dele),
                        [cv2.IMWRITE_JPEG_QUALITY, 88])
            del ri, nossa_inv
            gc.collect()
        resultados.append({"nome": nome, "dpi": dpi, "com_geometria": com_geometria, "invertida": invertida,
                           "como_programa": como_programa, "alinhamento": qualidade})
        del entrada, dele
        gc.collect()
    ARQUIVO_GEOMETRIA.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_GEOMETRIA.write_text(json.dumps(geometrias, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultados


# ------------------------------------------------------------------ páginas obrigatórias

def por_cima(img: np.ndarray, mascara: np.ndarray, cor: tuple[int, int, int]) -> np.ndarray:
    """A página com a máscara pintada por cima (meio a meio) e o contorno forte."""
    saida = img.copy()
    tinta = np.array(cor, np.float32)
    saida[mascara] = (0.55 * saida[mascara] + 0.45 * tinta).astype(np.uint8)
    borda = cv2.morphologyEx(mascara.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    saida[borda] = cor
    return saida


def detector_de_hoje(img: np.ndarray) -> tuple[np.ndarray | None, float]:
    """A zona "gravura" do detector que o programa usa hoje (core/detectar_regioes.py), e o tempo."""
    try:
        from core.detectar_regioes import detectar
        from core.selecao import GRAVURA

        inicio = time.perf_counter()
        mascara = detectar(img).mascara(img.shape[0], img.shape[1], GRAVURA) > 0
        return mascara, time.perf_counter() - inicio
    except Exception as erro:  # noqa: BLE001
        dizer(f"    detector de hoje falhou: {erro}")
        return None, 0.0


def paginas_obrigatorias(pasta: Path) -> list[dict]:
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))["paginas"]
    resultados = []
    for nome in OBRIGATORIAS:
        dizer(f"  {nome}")
        entrada = lista[nome]
        img = cv2.imread(str(GABARITO / entrada["png"]), cv2.IMREAD_COLOR)
        dpi = int(round(entrada["dpi_png"]))
        r = gs.detectar_gravura(img, dpi)
        hoje, tempo_hoje = detector_de_hoje(img)
        paineis = [img, por_cima(img, r.mascara, (0, 0, 230))]
        if hoje is not None:
            paineis.append(por_cima(img, hoje, (230, 90, 0)))
        lado = cf.juntar_lado_a_lado([cf.ajustar_lado_maior(p, 1100) for p in paineis])
        cv2.imwrite(str(pasta / f"obrigatoria_{nome}.jpg"), lado, [cv2.IMWRITE_JPEG_QUALITY, 85])
        # as duas opções do ScanTailor que mudam a forma: retangular e "maior sensibilidade"
        opcoes = {}
        paineis = [img]
        for rotulo, extra in (("retangular", {"forma": "retangular"}), ("mais_sensivel", {"mais_sensivel": True})):
            ro = gs.detectar_gravura(img, dpi, **extra)
            opcoes[rotulo] = float(ro.mascara.mean())
            paineis.append(por_cima(img, ro.mascara, (0, 0, 230)))
        lado = cf.juntar_lado_a_lado([cf.ajustar_lado_maior(p, 1100) for p in paineis])
        cv2.imwrite(str(pasta / f"obrigatoria_{nome}_opcoes.jpg"), lado, [cv2.IMWRITE_JPEG_QUALITY, 85])
        tempos = {"dpi_da_pagina": r.segundos, "detector_de_hoje": tempo_hoje}
        mascaras = {}
        for dpi_uso in (150, 300):
            fator = dpi_uso / dpi
            outra = cv2.resize(img, None, fx=fator, fy=fator,
                               interpolation=cv2.INTER_AREA if fator < 1 else cv2.INTER_CUBIC)
            ro = gs.detectar_gravura(outra, dpi_uso)
            tempos[f"{dpi_uso}_dpi"] = ro.segundos
            mascaras[dpi_uso] = cv2.resize(ro.mascara.astype(np.uint8), (img.shape[1], img.shape[0]),
                                           interpolation=cv2.INTER_NEAREST) > 0
        resultados.append({
            "nome": nome, "dpi": dpi, "tamanho": list(img.shape[:2]), "fracao": float(r.mascara.mean()),
            "fracao_hoje": None if hoje is None else float(hoje.mean()), "tempos": tempos,
            "fracao_opcoes": opcoes,
            "iou_150_x_pagina": comparar(mascaras[150], r.mascara)["iou"],
            "iou_300_x_pagina": comparar(mascaras[300], r.mascara)["iou"]})
        del img
        gc.collect()
    return resultados


# ------------------------------------------------------------------ relatório

def _pct(x: float) -> str:
    return f"{100 * x:.2f}%".replace(".", ",")


def _num(x: float, casas: int = 3) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def montar_relatorio(regua_r: list[dict], obrig_r: list[dict]) -> str:
    linhas = [
        "# Item 1.2: o seletor de gravura do ScanTailor, compilado (régua e páginas obrigatórias)",
        "",
        f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `conferir_gravura_scantailor.py`. "
        f"DLL: {gs.origem()}.",
        "",
        "## 1. Régua: a DLL contra as máscaras que o próprio ScanTailor gravou em 24/09 (teste de máquina)",
        "",
        "Com a mesma geometria do ScanTailor (giro, escala para 600 DPI e retângulo de trabalho), "
        "ponto a ponto, dentro do conteúdo. **IoU** = parte em comum / parte marcada por um ou pelo outro "
        "(1 = idênticas). **Iguais** = pontos com a mesma resposta.",
        "",
        "| Página | DPI | Gravura (ScanTailor) | Gravura (DLL) | IoU | Iguais | Só DLL | Só ScanTailor | Tempo |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in regua_r:
        g = r["com_geometria"]
        iou = "(as duas vazias)" if g["fracao_dele"] == 0 and g["fracao_nossa"] == 0 else _num(g["iou"], 4)
        linhas.append(f"| {r['nome']} | {r['dpi']} | {_pct(g['fracao_dele'])} | {_pct(g['fracao_nossa'])} | "
                      f"{iou} | {_pct(g['iguais'])} | {g['so_nossa']} | {g['so_dele']} | "
                      f"{_num(g['segundos'], 1)} s |")
    for r in regua_r:
        if r.get("invertida"):
            g = r["invertida"]
            linhas.append(f"| {r['nome']}, página invertida | {r['dpi']} | {_pct(g['fracao_dele'])} | "
                          f"{_pct(g['fracao_nossa'])} | {_num(g['iou'], 4)} | {_pct(g['iguais'])} | "
                          f"{g['so_nossa']} | {g['so_dele']} | - |")
    linhas += [
        "",
        "Imagens `regua_<página>.jpg`: cinza = os dois marcam; **vermelho = só a DLL**; "
        "**azul = só o ScanTailor** (engrossado para aparecer).",
        "",
        "## 2. Como o programa vai usar: a página inteira, sem a geometria do ScanTailor",
        "",
        "A mesma comparação, mas a DLL recebe a página como ela é (sem giro, sem o recorte do "
        "ScanTailor), no DPI dela e a 150 DPI (o DPI em que `core/camadas.py` chama o detector). "
        "A máscara é levada depois para o lugar da do ScanTailor.",
        "",
        "| Página | IoU no DPI da página | Iguais | IoU a 150 DPI | Iguais | Tempo (DPI da página / 150) |",
        "|---|---|---|---|---|---|",
    ]
    for r in regua_r:
        a, b = r["como_programa"]["dpi_da_pagina"], r["como_programa"]["150_dpi"]
        vazio = a["fracao_dele"] == 0 and a["fracao_nossa"] == 0
        linhas.append(f"| {r['nome']} | {'(vazias)' if vazio else _num(a['iou'], 4)} | {_pct(a['iguais'])} | "
                      f"{_num(b['iou'], 4)} | {_pct(b['iguais'])} | "
                      f"{_num(a['segundos'], 2)} s / {_num(b['segundos'], 2)} s |")
    linhas += [
        "",
        "## 3. Páginas obrigatórias da Fase 1 (teste de olho: o Samuel decide)",
        "",
        "Imagens `obrigatoria_<página>.jpg`: original | **DLL do ScanTailor (vermelho)** | "
        "detector de hoje, zona gravura (azul).",
        "",
        "| Página | DPI | Tamanho | Gravura (DLL) | Gravura (hoje) | Retangular | Mais sensível | "
        "Tempo DLL no DPI dela | a 150 DPI | a 300 DPI | Tempo do detector de hoje | "
        "IoU 150 x DPI dela | IoU 300 x DPI dela |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in obrig_r:
        t = r["tempos"]
        hoje = "-" if r["fracao_hoje"] is None else _pct(r["fracao_hoje"])
        linhas.append(f"| {r['nome']} | {r['dpi']} | {r['tamanho'][1]} x {r['tamanho'][0]} | "
                      f"{_pct(r['fracao'])} | {hoje} | {_pct(r['fracao_opcoes']['retangular'])} | "
                      f"{_pct(r['fracao_opcoes']['mais_sensivel'])} | {_num(t['dpi_da_pagina'], 2)} s | "
                      f"{_num(t['150_dpi'], 2)} s | {_num(t['300_dpi'], 2)} s | "
                      f"{_num(t['detector_de_hoje'], 2)} s | "
                      f"{_num(r['iou_150_x_pagina'], 3)} | {_num(r['iou_300_x_pagina'], 3)} |")
    linhas += ["", "Imagens `obrigatoria_<página>_opcoes.jpg`: original | forma retangular | "
               "\"maior sensibilidade de busca\" (as duas opções do ScanTailor que mudam a forma)."]
    linhas += ["", "**Aviso da Fase 1:** moldura e iluminura ainda são defeito conhecido até a Fase 1 "
               "ficar pronta.", ""]
    return "\n".join(linhas)


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--destino", type=Path, default=None)
    opcoes = analisador.parse_args(argumentos)
    if not gs.disponivel():
        dizer(f"A DLL não está disponível: {gs.motivo_indisponivel()}")
        return 1
    pasta = opcoes.destino or (RAIZ / "relatorios" / f"fase1-1.2-gravura-scantailor-{datetime.now():%Y-%m-%d}")
    pasta.mkdir(parents=True, exist_ok=True)
    dizer("1/3 régua (7 páginas de 24/09)")
    regua_r = regua(pasta)
    dizer("2/3 páginas obrigatórias")
    obrig_r = paginas_obrigatorias(pasta)
    dizer("3/3 relatório")
    (pasta / "numeros.json").write_text(json.dumps({"regua": regua_r, "obrigatorias": obrig_r},
                                                   indent=2, ensure_ascii=False), encoding="utf-8")
    import relatorio

    arquivos = relatorio.gravar(montar_relatorio(regua_r, obrig_r), pasta / "gravura-scantailor",
                                titulo="Item 1.2 - seletor de gravura do ScanTailor")
    dizer("Pronto: " + ", ".join(str(p) for p in arquivos.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
