"""Monta as imagens antes × depois da conferência da etapa 10a.

Cada caso: a página pelo caminho inteiro do programa (core.pipeline._pagina_pronta,
o corpo do processar), uma vez com o código de antes (worktree obra-etapa10a-antes,
11f9ed3) e outra com o de agora, lado a lado na mesma escala, com o original ao
lado. Grava JPG de até ~300 KB em relatorios/obra-etapa10a/conferencia/img/.

USO (da pasta da worktree): python relatorios/obra-etapa10a/scripts/fazer_conferencia.py [id ...]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
ANTES = RAIZ.parent / "obra-etapa10a-antes"
PY = Path(r"D:\programas\EditorImpressao\.venv\Scripts\python.exe")
TMP = RAIZ / "relatorios" / "conferir" / "obra-etapa10a" / "conf"
IMG = RAIZ / "relatorios" / "obra-etapa10a" / "conferencia" / "img"

# id: (alvo, campos, filtro (None = o do livro), refazer a sobra, recortes extras)
CASOS = {
    "cursus3": ("cursus:3", {}, "original", True),
    "siebmacher74": ("siebmacher:74", {}, None, False),
    "ljs47-2": ("ljs47:2", {}, "original", False),
    "antiphon2": ("antiphon:2", {}, "original", False),
    "boecio2": ("boecio:2", {}, None, False),
    "escola197": ("fab-escola:197", {}, "original", False),
    "boecio8": ("fab-boecio:8", {}, "original", False),
    "graduale221": ("fab-graduale:221", {}, "original", False),
    "marial7": ("fab-marial:7", {}, "original", False),
    "siebmacher7": ("fab-siebmacher:7", {}, "original", False),
    "horas18": ("horas:18", {}, "melhorar", False),
    "righetti96": ("fab-righetti:96", {"_girar_e_dividir": 270}, "original", False),
}


def _rodar(raiz: Path, alvo: str, campos: dict, filtro: str | None, refazer: bool, rotulo: str) -> Path:
    args = [str(PY), str(AQUI / "reproduzir.py"), "--raiz", str(raiz), "--saida", str(TMP),
            "--sem-mao", "--rotulo", rotulo, "--campos", json.dumps(campos)]
    if filtro == "original":
        args.append("--so-original")
    if refazer:
        args.append("--refazer-sobra")
    env = dict(os.environ, TEMP=str(TMP / "tmp"), TMP=str(TMP / "tmp"))
    (TMP / "tmp").mkdir(parents=True, exist_ok=True)
    r = subprocess.run(args + [alvo], cwd=str(RAIZ), env=env, capture_output=True, text=True)
    print(r.stdout.strip()[-400:], r.returncode, flush=True)
    livro, n = alvo.split(":")
    candidatos = sorted(TMP.glob(f"{livro}-p{int(n):03d}-*-{rotulo}.png"))
    if filtro and filtro != "original":
        candidatos = [c for c in candidatos if f"-{filtro}-" in c.name] or candidatos
    elif not filtro:
        candidatos = [c for c in candidatos if "-original-" not in c.name] or candidatos
    return candidatos[-1]


def _jpg_pequeno(origem, destino: Path, limite_kb: int = 300) -> None:
    import cv2

    img = origem
    for largura in (2000, 1800, 1600, 1400, 1200, 1000):
        if img.shape[1] > largura:
            img = cv2.resize(origem, (largura, int(origem.shape[0] * largura / origem.shape[1])),
                             interpolation=cv2.INTER_AREA)
        for q in (85, 78, 70):
            ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, q])
            if len(buf) <= limite_kb * 1024:
                destino.write_bytes(buf.tobytes())
                return
    destino.write_bytes(buf.tobytes())


def montar(id_: str) -> None:
    import cv2
    import numpy as np

    sys.path.insert(0, str(AQUI))
    from lado_a_lado import juntar

    alvo, campos, filtro, refazer = CASOS[id_]
    antes = _rodar(ANTES, alvo, campos, filtro, False, "antes")
    depois = _rodar(RAIZ, alvo, campos, filtro, refazer, "depois")
    livro, n = alvo.split(":")
    original = TMP / f"{livro}-p{int(n):03d}-original.png"
    # mesma escala (pontos por cm) para antes e depois: altura pela maior
    a, d = cv2.imread(str(antes)), cv2.imread(str(depois))
    o = cv2.imread(str(original))
    altura = 1100
    escala = altura / max(a.shape[0], d.shape[0])

    def na_escala(img, s):
        return cv2.resize(img, (max(1, int(img.shape[1] * s)), max(1, int(img.shape[0] * s))),
                          interpolation=cv2.INTER_AREA)

    pa, pd = na_escala(a, escala), na_escala(d, escala)
    po = na_escala(o, altura / o.shape[0])
    for nome, img in (("o", po), ("a", pa), ("d", pd)):
        fundo = np.full((altura, img.shape[1], 3), 255, np.uint8)
        fundo[: img.shape[0]] = img
        cv2.imwrite(str(TMP / f"_{id_}_{nome}.png"), fundo)
    junto = TMP / f"_{id_}.jpg"
    juntar(str(junto), altura, [("original (o scan)", str(TMP / f"_{id_}_o.png")),
                                ("ANTES (código de 26/10, 11f9ed3)", str(TMP / f"_{id_}_a.png")),
                                ("DEPOIS (etapa 10a)", str(TMP / f"_{id_}_d.png"))], 92)
    IMG.mkdir(parents=True, exist_ok=True)
    _jpg_pequeno(cv2.imread(str(junto)), IMG / f"{id_}.jpg")
    dpi = 300
    info = {"antes_cm": [round(a.shape[1] / dpi * 2.54, 2), round(a.shape[0] / dpi * 2.54, 2)],
            "depois_cm": [round(d.shape[1] / dpi * 2.54, 2), round(d.shape[0] / dpi * 2.54, 2)]}
    (IMG / f"{id_}.json").write_text(json.dumps(info), encoding="utf-8")
    print(id_, info, flush=True)


if __name__ == "__main__":
    for i in (sys.argv[1:] or list(CASOS)):
        montar(i)
