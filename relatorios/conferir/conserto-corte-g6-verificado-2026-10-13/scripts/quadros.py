"""As imagens da conferencia do conserto: as TRES versoes de cada pagina lado a
lado, alinhadas pelo conteudo.

    "Antes do endireitar novo"  ordem antiga (corta e depois endireita), mesmo
                                angulo do livro novo (o preparo B da conferencia
                                de antes: _tmp/finais/<base>__B.jpg)
    "Hoje no programa"          livro novo no fase-1 de hoje (_tmp/finais-hoje)
    "Com o conserto"            livro novo no ramo do conserto, d97b937
                                (_tmp/finais-conserto)

As tres sao postas no MESMO lugar da pagina inteira (cada uma e um corte dela:
a posicao vem do recorte que o programa guardou), entao o mesmo pedaco do
papel aparece na mesma altura nas tres, e o que fica de fora de cada corte
aparece em azul claro ("fora da folha"). Erro do alinhamento: 1 ou 2 pontos
(a ordem antiga gira em volta do centro do corte, as outras do centro da
pagina).

Para cada pagina:
    img/cg6-<pagina>-perto.jpg    so a parte que mudou, ampliada (REGIOES)
    img/cg6-<pagina>-pagina.jpg   a pagina inteira nas tres versoes
E, para as paginas que saem identicas com o conserto, folhas de contato:
    img/cg6-identicas-NN.jpg

USO   python quadros.py [base,base,...]     (sem nada: todas as de PAGINAS)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[2]
TMP = RAIZ / "_tmp"
ANTES = PASTA.parent / "corte-g6-2026-10-13"
DPI = 300
FORA = (236, 205, 170)          # azul claro (BGR): fora da folha
FUNDO = (245, 243, 240)
TITULOS = ("Antes do endireitar novo", "Hoje no programa", "Com o conserto")
CORES = ((90, 90, 90), (40, 40, 190), (40, 130, 40))        # BGR da tarja de cada titulo

# A parte que mudou, em fracao da pagina INTEIRA (x0, y0, x1, y1). Escolhidas
# a mao, olhando as paginas inteiras (ver tambem `mudou_em`, impresso ao rodar).
REGIOES: dict[str, tuple[float, float, float, float]] = {}


def _fonte(tamanho: int, negrito: bool = True):
    for nome in (("segoeuib.ttf", "arialbd.ttf") if negrito else ("segoeui.ttf", "arial.ttf")):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def slug(base: str) -> str:
    livro, resto = base.split("_p")
    pagina, metade = resto.split("__")
    return f"{livro}-{int(pagina)}" + ("" if metade == "inteira" else f"-{metade}")


def carregar() -> tuple[dict, dict, dict]:
    antes = json.loads((ANTES / "dados.json").read_text(encoding="utf-8"))
    hoje = json.loads((PASTA / "dados-hoje.json").read_text(encoding="utf-8"))
    conserto = json.loads((PASTA / "dados-conserto.json").read_text(encoding="utf-8"))
    return antes, hoje, conserto


def versoes(base: str, dados) -> list[dict]:
    """As tres versoes: imagem e onde ela fica na pagina inteira (x0, y0 em pontos)."""
    antes, hoje, conserto = dados
    fontes = ((antes[base]["B"], TMP / "finais" / f"{base}__B.jpg"),
              (hoje[base]["C"], TMP / "finais-hoje" / f"{base}__C.jpg"),
              (conserto[base]["C"], TMP / "finais-conserto" / f"{base}__C.jpg"))
    larg, alt = antes[base]["B"]["pagina_inteira_px"]
    saida = []
    for r, caminho in fontes:
        img = cv2.imread(str(caminho))
        x, y = (0.0, 0.0) if r["recorte"] is None else r["recorte"][:2]
        saida.append({"img": img, "x0": int(x * larg), "y0": int(y * alt), "r": r, "pagina": (larg, alt)})
    return saida


def na_pagina(v: dict, caixa: tuple[int, int, int, int]) -> np.ndarray:
    """O pedaco `caixa` (x0, y0, x1, y1, em pontos da pagina inteira) como esta
    versao o mostra: a imagem dela onde ha, azul claro onde ela nao chega."""
    x0, y0, x1, y1 = caixa
    tela = np.full((y1 - y0, x1 - x0, 3), FORA, np.uint8)
    img = v["img"]
    a, l = img.shape[:2]
    # a parte da versao que cai dentro da caixa
    ix0, iy0 = max(x0, v["x0"]), max(y0, v["y0"])
    ix1, iy1 = min(x1, v["x0"] + l), min(y1, v["y0"] + a)
    if ix1 > ix0 and iy1 > iy0:
        tela[iy0 - y0:iy1 - y0, ix0 - x0:ix1 - x0] = img[iy0 - v["y0"]:iy1 - v["y0"], ix0 - v["x0"]:ix1 - v["x0"]]
    return tela


def montar(pedacos: list[np.ndarray], legendas: list[str], rodape: str, largura_alvo: int) -> np.ndarray:
    """Tres pedacos lado a lado, com a tarja do titulo em cima de cada um."""
    a, l = pedacos[0].shape[:2]
    cada = (largura_alvo - 4 * 14) // 3
    fator = min(cada / l, 1250 / a, 1.0 if l >= cada else cada / l)
    novo = (max(1, round(l * fator)), max(1, round(a * fator)))
    inter = cv2.INTER_AREA if fator < 1 else cv2.INTER_CUBIC
    pedacos = [cv2.resize(p, novo, interpolation=inter) for p in pedacos]
    cada = max(cada, novo[0])
    alt_titulo, alt_leg, alt_rodape = 46, 30, 34
    tela = np.full((alt_titulo + alt_leg + novo[1] + alt_rodape + 14, 3 * cada + 4 * 14, 3), FUNDO, np.uint8)
    for i, p in enumerate(pedacos):
        x = 14 + i * (cada + 14)
        cv2.rectangle(tela, (x, 8), (x + cada - 1, 8 + alt_titulo - 8), CORES[i], -1)
        px = x + (cada - novo[0]) // 2
        tela[alt_titulo + alt_leg:alt_titulo + alt_leg + novo[1], px:px + novo[0]] = p
        cv2.rectangle(tela, (px - 1, alt_titulo + alt_leg - 1), (px + novo[0], alt_titulo + alt_leg + novo[1]),
                      (120, 120, 120), 1)
    pil = Image.fromarray(cv2.cvtColor(tela, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    for i in range(3):
        x = 14 + i * (cada + 14)
        d.text((x + 12, 11), TITULOS[i], font=_fonte(24), fill=(255, 255, 255))
        d.text((x + 2, alt_titulo + 4), legendas[i], font=_fonte(17, False), fill=(40, 40, 40))
    d.rectangle((16, tela.shape[0] - alt_rodape - 2, 44, tela.shape[0] - 18), fill=FORA[::-1], outline=(120, 120, 120))
    d.text((52, tela.shape[0] - alt_rodape - 5), rodape, font=_fonte(17, False), fill=(40, 40, 40))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def cm(mm: float) -> str:
    return f"{mm / 10:.1f}".replace(".", ",")


def legenda(v: dict) -> str:
    return f"folha de {cm(v['r']['tamanho_mm'][0])} x {cm(v['r']['tamanho_mm'][1])} cm"


def mudou_em(vs: list[dict]) -> dict:
    """Quanto cada beirada do corte andou, em mm (positivo = a folha cresceu
    daquele lado), de hoje para o conserto e da antiga para o conserto."""
    def beiradas(v):
        a, l = v["img"].shape[:2]
        return {"esq": -v["x0"], "topo": -v["y0"], "dir": v["x0"] + l, "pe": v["y0"] + a}
    b = [beiradas(v) for v in vs]
    mm = 25.4 / DPI
    return {"hoje_para_conserto": {k: round((b[2][k] - b[1][k]) * mm, 1) for k in b[0]},
            "antiga_para_conserto": {k: round((b[2][k] - b[0][k]) * mm, 1) for k in b[0]}}


def pagina_inteira(base: str, dados, destino: Path) -> None:
    vs = versoes(base, dados)
    x0 = min(v["x0"] for v in vs)
    y0 = min(v["y0"] for v in vs)
    x1 = max(v["x0"] + v["img"].shape[1] for v in vs)
    y1 = max(v["y0"] + v["img"].shape[0] for v in vs)
    folga = int(4 / 25.4 * DPI)
    caixa = (x0 - folga, y0 - folga, x1 + folga, y1 + folga)
    img = montar([na_pagina(v, caixa) for v in vs], [legenda(v) for v in vs],
                 "azul claro = fora da folha (o que o corte tirou)", 1800)
    cv2.imwrite(str(destino), img, [cv2.IMWRITE_JPEG_QUALITY, 84])


def de_perto(base: str, regiao, dados, destino: Path) -> None:
    vs = versoes(base, dados)
    larg, alt = vs[0]["pagina"]
    caixa = (int(regiao[0] * larg), int(regiao[1] * alt), int(regiao[2] * larg), int(regiao[3] * alt))
    lado_cm = f"{cm((caixa[2] - caixa[0]) * 25.4 / DPI)} x {cm((caixa[3] - caixa[1]) * 25.4 / DPI)} cm"
    img = montar([na_pagina(v, caixa) for v in vs], [legenda(v) for v in vs],
                 f"azul claro = fora da folha.  O pedaco mostrado tem {lado_cm} da pagina.", 1800)
    cv2.imwrite(str(destino), img, [cv2.IMWRITE_JPEG_QUALITY, 88])


def folhas_identicas(bases: list[str], dados, prefixo: str = "cg6-identicas") -> None:
    """Folhas de contato das paginas que saem identicas com o conserto: 3
    paginas por folha, as tres versoes de cada."""
    for n in range(0, len(bases), 3):
        linhas = []
        for base in bases[n:n + 3]:
            vs = versoes(base, dados)
            x0 = min(v["x0"] for v in vs); y0 = min(v["y0"] for v in vs)
            x1 = max(v["x0"] + v["img"].shape[1] for v in vs); y1 = max(v["y0"] + v["img"].shape[0] for v in vs)
            pedacos = [na_pagina(v, (x0, y0, x1, y1)) for v in vs]
            f = min(600 / pedacos[0].shape[0], 420 / pedacos[0].shape[1])
            pedacos = [cv2.resize(p, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) for p in pedacos]
            linha = np.full((640, 3 * 440 + 20, 3), FUNDO, np.uint8)
            for i, p in enumerate(pedacos):
                x = 10 + i * 440 + (430 - p.shape[1]) // 2
                linha[36:36 + p.shape[0], x:x + p.shape[1]] = p
            pil = Image.fromarray(cv2.cvtColor(linha, cv2.COLOR_BGR2RGB))
            d = ImageDraw.Draw(pil)
            for i in range(3):
                d.text((14 + i * 440, 6), f"{slug(base)}: {TITULOS[i]}", font=_fonte(17), fill=CORES[i][::-1])
            linhas.append(cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR))
        destino = PASTA / "img" / f"{prefixo}-{n // 3 + 1:02d}.jpg"
        cv2.imwrite(str(destino), np.vstack(linhas), [cv2.IMWRITE_JPEG_QUALITY, 82])
        print(destino.name, [slug(b) for b in bases[n:n + 3]])


def main() -> int:
    dados = carregar()
    regioes = json.loads((AQUI / "regioes.json").read_text(encoding="utf-8")) if (AQUI / "regioes.json").exists() else {}
    hoje, conserto = dados[1], dados[2]
    mudam = [b for b in sorted(hoje) if hoje[b]["C"]["md5"] != conserto[b]["C"]["md5"]]
    bases = sys.argv[1].split(",") if len(sys.argv) > 1 else mudam
    (PASTA / "img").mkdir(exist_ok=True)
    for base in bases:
        vs = versoes(base, dados)
        print(slug(base), mudou_em(vs), flush=True)
        pagina_inteira(base, dados, PASTA / "img" / f"cg6-{slug(base)}-pagina.jpg")
        for i, regiao in enumerate(regioes.get(base, [])):
            de_perto(base, regiao, dados, PASTA / "img" / f"cg6-{slug(base)}-perto{'' if i == 0 else i + 1}.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
