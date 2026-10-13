"""Por que o corte muda quando a pagina e endireitada ANTES (G6)?

Refaz, passo a passo, a conta de core/recortar.detectar_bordas na pagina
como veio (o que a ordem antiga mede) e na pagina ja endireitada (o que a
ordem nova mede), e diz em que passo as duas se separam. So le; nao muda
nada do programa. Usa as funcoes do proprio programa (as de nome com "_"
sao as internas do corte).

USO
    python causa.py base[,base...]      base = cursus_p003__inteira, por exemplo
    (precisa de _tmp/finais/<base>__inteira.jpg e do dados.json, do medir.py)
Grava causa.json ao lado do dados.json e, por pagina, img/causa-<base>.jpg
(a mascara de tinta do corte nas duas paginas, com o corte achado).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[2]
FINAIS = RAIZ / "_tmp" / "finais"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import recortar as R  # noqa: E402
from core.endireitar import rotacionar  # noqa: E402


def passos(cinza_cheio: np.ndarray, dpi: float = 300.0) -> dict:
    """Os passos de detectar_bordas, um por um, na imagem em cinza."""
    alt0, larg0 = cinza_cheio.shape
    escala = R.ALTURA_ANALISE / alt0
    cinza = cv2.resize(cinza_cheio, (max(8, int(larg0 * escala)), R.ALTURA_ANALISE),
                       interpolation=cv2.INTER_AREA) if alt0 > R.ALTURA_ANALISE else cinza_cheio
    alt, larg = cinza.shape
    tinta = R._mascara_de_tinta_local(cinza)
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    # cobertura de tinta das colunas e linhas da ponta (o que _apagar_bordas_solidas olha)
    col, lin = tinta.mean(axis=0), tinta.mean(axis=1)
    sem_borda = R._apagar_bordas_solidas(tinta)

    def apagadas(antes, depois):
        """Quantas colunas (linhas) inteiras sumiram de cada ponta."""
        c = (antes.sum(axis=0) > 0) & (depois.sum(axis=0) == 0)
        l = (antes.sum(axis=1) > 0) & (depois.sum(axis=1) == 0)
        meio_c, meio_l = len(c) // 2, len(l) // 2
        return {"esq": int(c[:meio_c].sum()), "dir": int(c[meio_c:].sum()),
                "topo": int(l[:meio_l].sum()), "pe": int(l[meio_l:].sum())}

    borda = apagadas(tinta, sem_borda)
    sem_risca = R._apagar_riscas_de_dobra(sem_borda)
    risca = apagadas(sem_borda, sem_risca)
    fy = R._faixa_com_a_tinta(sem_risca.sum(axis=1))
    fx = R._faixa_com_a_tinta(sem_risca.sum(axis=0))
    final = R.detectar_bordas(cinza_cheio, dpi=dpi).tupla

    def maior_seguida(v, limite):
        """A maior fileira seguida de colunas com cobertura >= limite, em cada metade."""
        res = {}
        for nome, trecho in (("primeira_metade", v[:len(v) // 2]), ("segunda_metade", v[len(v) // 2:])):
            melhor = atual = 0
            for x in trecho >= limite:
                atual = atual + 1 if x else 0
                melhor = max(melhor, atual)
            res[nome] = melhor
        return res

    return {
        "mascara_px": [larg, alt],
        "cobertura_da_coluna_0_e_da_ultima": [round(float(col[0]), 3), round(float(col[-1]), 3)],
        "cobertura_das_8_colunas_da_esquerda": [round(float(v), 2) for v in col[:8]],
        "cobertura_das_8_colunas_da_direita": [round(float(v), 2) for v in col[-8:]],
        "cobertura_da_linha_0_e_da_ultima": [round(float(lin[0]), 3), round(float(lin[-1]), 3)],
        "cobertura_das_8_linhas_de_cima": [round(float(v), 2) for v in lin[:8]],
        "cobertura_das_8_linhas_de_baixo": [round(float(v), 2) for v in lin[-8:]],
        "colunas_com_80_por_cento_ou_mais_seguidas": maior_seguida(col, R.FRACAO_BORDA_SOLIDA),
        "linhas_com_80_por_cento_ou_mais_seguidas": maior_seguida(lin, R.FRACAO_BORDA_SOLIDA),
        "apagou_como_borda_solida": borda,
        "apagou_como_risca_de_dobra": risca,
        "faixa_da_tinta_x": None if fx is None else [round(fx[0] / larg, 4), round(fx[1] / larg, 4)],
        "faixa_da_tinta_y": None if fy is None else [round(fy[0] / alt, 4), round(fy[1] / alt, 4)],
        "corte_final": [round(float(v), 4) for v in final],
        "_mascara": sem_risca, "_mascara_bruta": tinta,
    }


def desenhar(base: str, como_veio: dict, reta: dict) -> None:
    """As duas mascaras lado a lado: em preto a tinta que o corte considera,
    em cinza a que ele jogou fora (borda solida, risca), em vermelho o corte."""
    quadros = []
    for nome, p in (("como veio (ordem antiga mede aqui)", como_veio),
                    ("ja endireitada (ordem nova mede aqui)", reta)):
        bruta, limpa = p["_mascara_bruta"], p["_mascara"]
        img = np.full(bruta.shape + (3,), 255, np.uint8)
        img[bruta > 0] = (170, 170, 170)
        img[limpa > 0] = (0, 0, 0)
        a, l = bruta.shape
        x, y, w, h = p["corte_final"]
        cv2.rectangle(img, (int(x * l), int(y * a)), (int((x + w) * l) - 1, int((y + h) * a) - 1),
                      (0, 0, 255), 2)
        img = cv2.copyMakeBorder(img, 34, 6, 6, 6, cv2.BORDER_CONSTANT, value=(235, 235, 235))
        cv2.putText(img, nome, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
        quadros.append(img)
    alt = max(q.shape[0] for q in quadros)
    quadros = [cv2.copyMakeBorder(q, 0, alt - q.shape[0], 0, 0, cv2.BORDER_CONSTANT,
                                  value=(235, 235, 235)) for q in quadros]
    (PASTA / "img").mkdir(exist_ok=True)
    cv2.imwrite(str(PASTA / "img" / f"causa-{base}.jpg"), np.hstack(quadros),
                [cv2.IMWRITE_JPEG_QUALITY, 88])


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    destino = PASTA / "causa.json"
    saida = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for base in sys.argv[1].split(","):
        inteira = cv2.imread(str(FINAIS / f"{base}__inteira.jpg"), cv2.IMREAD_GRAYSCALE)
        angulo = dados[base]["C"]["angulo"]
        como_veio = passos(inteira)
        reta = passos(rotacionar(inteira, angulo))
        desenhar(base, como_veio, reta)
        for p in (como_veio, reta):
            p.pop("_mascara"), p.pop("_mascara_bruta")
        saida[base] = {"angulo": angulo, "pagina_como_veio": como_veio, "pagina_ja_endireitada": reta,
                       "corte_do_programa_na_ordem_antiga_B": dados[base]["B"]["recorte"],
                       "corte_do_programa_na_ordem_nova_C": dados[base]["C"]["recorte"]}
        print(base, "angulo", angulo)
        for nome, p in (("como veio", como_veio), ("ja endireitada", reta)):
            print("  ", nome)
            for k, v in p.items():
                print("      ", k, v)
    destino.write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
