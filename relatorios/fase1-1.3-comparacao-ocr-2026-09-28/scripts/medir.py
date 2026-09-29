"""Passo final do 1.3: mede cada detector em cada pagina e monta as folhas de contato.

Uso (ambiente de teste, depois de preparar.py e dos rodar_*.py):
    .venv-ocr\\Scripts\\python.exe medir.py

Le saida_teste\\ocr-1.3\\linhas\\<detector>\\<pagina>.json e grava:
- relatorios\\...\\resultados.json  -- todas as medidas;
- relatorios\\...\\folhas\\<pagina>.jpg -- as caixas de cada detector por cima da pagina.

Detectores (nomes da pesquisa, secao 5.4):
R0 linhas do texto invisivel do Internet Archive (so livros do IA)
T1 Tesseract, modelo do idioma | T2 = T1 com o filtro do IA (confianca < 20 sai)
T3a Tesseract frak2021 + filtro | T3b Tesseract GT4HistOCR + filtro
D1 OnnxTR db_resnet50 | D2 OnnxTR fast_base
P1 PP-OCRv5 servidor | P2 PP-OCRv5 movel | P3 PP-OCRv6 pequeno (extra)
K1 Kraken blla (WSL)

Seguro mudar: tamanho e cores das folhas. Arriscado: o limiar 20 do filtro
(e o do Internet Archive) e a lista de detectores (a tabela do relatorio le daqui).
"""

from __future__ import annotations

import json

import cv2
import numpy as np

import comum as C

LIMIAR_IA = 20.0

# nome -> (pasta das linhas, filtrar pela confianca?)
DETECTORES = {
    "R0": ("R0", False),
    "T1": ("T1", False),
    "T2": ("T1", True),
    "T3a": ("T3a", True),
    "T3b": ("T3b", True),
    "D1": ("D1", False),
    "D2": ("D2", False),
    "P1": ("P1", False),
    "P2": ("P2", False),
    "P3": ("P3", False),
    "K1": ("K1", False),
}
# So para conferir a deducao da pesquisa (o modelo do Tesseract nao muda as linhas):
EXTRAS = {"T3a sem filtro": ("T3a", False), "T3b sem filtro": ("T3b", False),
          "K1w": ("K1w", False)}  # Kraken no Windows (Python 3.12), so 6 paginas

NOMES = {
    "R0": "Linhas do Internet Archive (ja no PDF)",
    "T1": "Tesseract, modelo do idioma",
    "T2": "Tesseract, idioma + filtro do IA",
    "T3a": "Tesseract frak2021 + filtro",
    "T3b": "Tesseract GT4HistOCR + filtro",
    "D1": "docTR/OnnxTR db_resnet50",
    "D2": "docTR/OnnxTR fast_base",
    "P1": "PP-OCRv5 servidor (RapidOCR)",
    "P2": "PP-OCRv5 movel (RapidOCR)",
    "P3": "PP-OCRv6 pequeno (RapidOCR, extra)",
    "K1": "Kraken blla (WSL)",
}


def linhas_de(detector: str, pagina: str, todos: dict) -> tuple[list[dict] | None, list[dict], dict | None]:
    """(linhas usadas, linhas descartadas pelo filtro, dados brutos) ou (None, [], None)."""
    pasta, filtrar = todos[detector]
    dados = C.ler_linhas(pasta, pagina)
    if dados is None:
        return None, [], None
    linhas = dados["linhas"]
    if filtrar:
        usadas = [ln for ln in linhas if ln.get("conf", 100) >= LIMIAR_IA]
        fora = [ln for ln in linhas if ln.get("conf", 100) < LIMIAR_IA]
        return usadas, fora, dados
    return linhas, [], dados


def painel(img: np.ndarray, zm: dict, linhas, fora, titulo: str, sub: str, altura: int = 760) -> np.ndarray:
    """Um quadro da folha de contato: pagina, figura (contorno vermelho), caixas (azul)."""
    h, w = img.shape[:2]
    esc = altura / h
    base = cv2.resize(img, (int(w * esc), altura), interpolation=cv2.INTER_AREA)
    base = cv2.cvtColor(base, cv2.COLOR_RGB2BGR)
    if linhas is None:
        cinza = (0.35 * base + 0.65 * 235).astype(np.uint8)
        cv2.putText(cinza, "nao se aplica", (10, altura // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 60), 2)
        base = cinza
    else:
        cobre = base.copy()
        for ln in linhas:
            pts = np.round(np.asarray(ln["poligono"]) * esc).astype(np.int32)
            cv2.fillPoly(cobre, [pts], (255, 120, 0))
        base = cv2.addWeighted(cobre, 0.35, base, 0.65, 0)
        for ln in linhas:
            pts = np.round(np.asarray(ln["poligono"]) * esc).astype(np.int32)
            cv2.polylines(base, [pts], True, (200, 60, 0), 1)
        for ln in fora:
            pts = np.round(np.asarray(ln["poligono"]) * esc).astype(np.int32)
            cv2.polylines(base, [pts], True, (0, 140, 255), 2)
    fig = cv2.resize(zm["figura"].astype(np.uint8), (base.shape[1], altura), interpolation=cv2.INTER_NEAREST)
    cont, _ = cv2.findContours(fig, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(base, cont, -1, (0, 0, 220), 2)
    faixa = np.full((56, base.shape[1], 3), 255, np.uint8)
    cv2.putText(faixa, titulo, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2)
    cv2.putText(faixa, sub, (6, 47), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1)
    return np.vstack([faixa, base])


def folha(paineis: list[np.ndarray], colunas: int = 4) -> np.ndarray:
    alt = max(p.shape[0] for p in paineis)
    larg = max(p.shape[1] for p in paineis)
    linhas_img = []
    for i in range(0, len(paineis), colunas):
        grupo = []
        for p in paineis[i:i + colunas]:
            q = np.full((alt, larg, 3), 255, np.uint8)
            q[:p.shape[0], :p.shape[1]] = p
            grupo.append(q)
        while len(grupo) < colunas:
            grupo.append(np.full((alt, larg, 3), 255, np.uint8))
        linhas_img.append(np.hstack([np.pad(g, ((6, 6), (6, 6), (0, 0)), constant_values=255) for g in grupo]))
    return np.vstack(linhas_img)


def pct(v) -> str:
    return "-" if v is None else f"{100 * v:.1f}%"


def main() -> None:
    zonas = C.carregar_zonas()
    todos = {**DETECTORES, **EXTRAS}
    resultados: dict = {"detectores": NOMES, "paginas": {}}
    (C.RELATORIO / "folhas").mkdir(parents=True, exist_ok=True)
    for pagina in C.PAGINAS:
        img = C.ler_imagem(pagina)
        h, w = img.shape[:2]
        zm = C.mascaras_zonas(zonas[pagina], (h, w))
        tinta = C.tinta(img, C.dpi_trabalho(pagina))
        res_pag = {}
        paineis = []
        for det in todos:
            linhas, fora, dados = linhas_de(det, pagina, todos)
            if linhas is None:
                res_pag[det] = None
                if det in DETECTORES:
                    paineis.append(painel(img, zm, None, [], det, "sem dados"))
                continue
            m = C.mascara_linhas(linhas, (h, w))
            m_cru = C.mascara_linhas(linhas, (h, w), alargar=0.0)
            med = C.medir(tinta, zm, m, m_cru)
            med.update(C.linhas_falsas(linhas, zm))
            med["linhas"] = len(linhas)
            med["linhas_descartadas_pelo_filtro"] = len(fora)
            med["tempo_s"] = dados.get("tempo_mediana_s")
            med["tempos_s"] = dados.get("tempos_s")
            res_pag[det] = med
            if det in DETECTORES:
                sub = f"texto {pct(med['texto_achado'])}  figura {pct(med['figura_tomada'])}"
                if med["figura_area"] is not None:
                    sub += f" (area {pct(med['figura_area'])})"
                if med["tempo_s"] is not None and det != "R0":
                    sub += f"  {med['tempo_s']:.1f}s"
                # No T1, as linhas que o filtro do IA jogaria fora aparecem em laranja.
                if det == "T1":
                    _, fora_t2, _ = linhas_de("T2", pagina, todos)
                    fora = fora_t2
                paineis.append(painel(img, zm, linhas, fora, f"{det}  {len(linhas)} linhas", sub))
        resultados["paginas"][pagina] = res_pag
        cv2.imwrite(str(C.RELATORIO / "folhas" / f"{pagina}.jpg"), folha(paineis),
                    [cv2.IMWRITE_JPEG_QUALITY, 80])
        print(pagina, " ".join(f"{d}:{pct(r['texto_achado'])}/{pct(r['figura_tomada'])}"
                               for d, r in res_pag.items() if r and d in DETECTORES), flush=True)
    (C.RELATORIO / "resultados.json").write_text(json.dumps(resultados, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
