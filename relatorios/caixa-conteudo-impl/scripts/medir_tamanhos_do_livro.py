"""Mede o tamanho do conteúdo (ScanTailor) numa amostra de páginas de vários
livros, para conferir a regra da folha "muito maior" (g9, core/
corte_pelo_conteudo.LIMITE_DA_MUITO_MAIOR) contra páginas de verdade.

Para cada livro: até N páginas espalhadas (mais as páginas pedidas à mão,
como a tabela dobrável do Opus Majus, p. 256), desenhadas a 150 DPI, sem
dividir nem endireitar (só livros de uma página por folha). Grava
dados/tamanhos-do-livro.json com o tamanho de cada página, a razão contra a
mediana do livro e quem ficou de fora com o limite de hoje.

Somente leitura do acervo. Uso: python medir_tamanhos_do_livro.py [N]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from statistics import median

import cv2
import fitz
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from core import corte_pelo_conteudo as cc  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
L = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVROS = {
    "opusmajus": (Path(r"C:\Users\fotog\Desktop\opusmajustransla01baco.pdf"), [256, 255, 257]),
    "palatino": (L / "Giovambattista Palatino cittadino romano.pdf", []),
    "escola": (L / "Na escola de Jesus - Catecismo explicado com imagens..pdf", []),
    "marial": (L / "Marial de sermoens - Frei Balthasar Paez. (1).pdf", []),
    "horas": (L / "Livro de Horas - Luís XIV.pdf", []),
    "graduale": (L / "Graduale - Saeculum XIV.pdf", []),
    "righetti": (L / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf", []),
    "camoes": (Path(r"D:\Livros para editar\HISTÓRIA\Luiz de Camões levantando o seu monumento ou A Historia de Portugal justificada pelos Lusiadas.pdf"), []),
    "antiphon": (L / "Antiphon_25.pdf", []),
    "ljs47": (L / "ljs47.pdf", []),
}


def desenhar(doc, i: int):
    p = doc[i]
    pix = p.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    maior = max((int(x[2]) for x in p.get_images()), default=0)
    scan = maior / (p.rect.width / 72.0) if maior else None
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR), scan


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    so = sys.argv[2:] or list(LIVROS)
    destino = PASTA / "dados" / "tamanhos-do-livro.json"
    resultado = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for nome in so:
        pdf, extras = LIVROS[nome]
        if not pdf.exists():
            print(nome, "sem o PDF", flush=True)
            continue
        inicio = time.time()
        with fitz.open(pdf) as doc:
            total = doc.page_count
            paginas = sorted(set(np.linspace(1, total, num=min(n, total), dtype=int).tolist()) | set(extras))
            tamanhos = {}
            for numero in paginas:
                img, scan = desenhar(doc, numero - 1)
                m = cc.medir(img, 150.0, scan)
                tamanhos[numero] = None if not m.tem_conteudo else [round(v, 1) for v in m.tamanho_mm]
        com = {k: v for k, v in tamanhos.items() if v}
        ml = median(v[0] for v in com.values()) if com else 0
        ma = median(v[1] for v in com.values()) if com else 0
        fora = sorted(cc.muito_maiores({k: tuple(v) for k, v in com.items()}))
        resultado[nome] = {
            "paginas": len(paginas), "total_do_livro": total,
            "mediana_mm": [round(ml, 1), round(ma, 1)],
            "razoes": {str(k): [round(v[0] / ml, 2), round(v[1] / ma, 2)] for k, v in com.items()},
            "tamanhos_mm": {str(k): v for k, v in tamanhos.items()},
            "muito_maiores_com_o_limite": fora,
            "limite": cc.LIMITE_DA_MUITO_MAIOR,
            "segundos": round(time.time() - inicio, 1),
        }
        maiores = sorted(((max(r), k) for k, r in resultado[nome]["razoes"].items()), reverse=True)[:5]
        print(nome, "mediana", resultado[nome]["mediana_mm"], "fora", fora, "maiores razoes", maiores,
              f"{resultado[nome]['segundos']} s", flush=True)
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
