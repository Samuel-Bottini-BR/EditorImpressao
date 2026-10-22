"""Verificador 22/10/2026: leva páginas pelo caminho inteiro do programa.

Regra do Samuel (21/10/2026, CLAUDE.md §4.10): toda foto passa pela ordem do
livro novo (girar -> dividir -> endireitar -> cortar -> filtro), com os ajustes
de fábrica, até a ferramenta testada. Aqui: cada livro de teste vira um Projeto
novo (core.pipeline.analisar_projeto, a mesma análise do "abrir livro") e é
gerado pelo core.pipeline.processar (o mesmo do botão Processar).

USO (um processo por vez; --raiz escolhe qual código roda):
  python caminho.py --raiz <worktree> livro --saida X.pdf --campos '{"margens_iguais": true}' \
         [--pagina '{"luz_igualar": true}'] pid [pid ...]
  python caminho.py --raiz <worktree> somas --saida s.json --filtro preto_e_branco pid [pid ...]

`pid` é uma página do gabarito (gabarito/paginas/<pid>.pdf) ou "arquivo.pdf:N"
(página N, contando de 1, de um PDF do acervo, só lido). Escreve <saida>.json ao
lado do PDF com: por onde passou, tamanhos das páginas (cm), avisos e o tempo.
A pasta de dados do programa vai para uma pasta temporária.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_DADOS = Path(os.environ.get("VFR_DADOS") or (Path(tempfile.gettempdir()) / "vfr22_localappdata"))
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

FILTROS = {}


def _pagina_de(pid: str, raiz: Path):
    if ":" in pid and pid.lower().rsplit(":", 1)[0].endswith(".pdf"):
        arq, n = pid.rsplit(":", 1)
        return Path(arq), int(n) - 1
    return raiz / "gabarito" / "paginas" / f"{pid}.pdf", 0


def montar_entrada(pids: list[str], raiz: Path, destino: Path) -> Path:
    import fitz

    novo = fitz.open()
    for pid in pids:
        arq, i = _pagina_de(pid, raiz)
        with fitz.open(str(arq)) as um:
            novo.insert_pdf(um, from_page=i, to_page=i)
    novo.save(str(destino))
    novo.close()
    return destino


def frase(projeto) -> str:
    from core.filtros import NOMES_AMIGAVEIS

    p = projeto
    partes = ["girar (automático)",
              "dividir: " + ("sim" if p.dividir_folhas else "não (uma página por folha)"),
              "endireitada" if p.endireitar else "sem endireitar",
              "cortada (automático)" if p.cortar_bordas else "sem cortar",
              "filtro " + NOMES_AMIGAVEIS.get(p.filtro_padrao, p.filtro_padrao)]
    if getattr(p, "margens_iguais", False):
        partes.append("margens iguais {} mm, alinhamento {}".format(
            "/".join(f"{v:g}" for v in p.margens_mm), "/".join(p.margens_alinhamento)))
    if getattr(p, "pdf_em_duas_camadas", False):
        partes.append("PDF em duas camadas")
    if p.montar_cadernos:
        partes.append("montar cadernos no tamanho do scan")
    return " → ".join(partes)


def _trab():
    try:
        import core.nucleos as n
        return n.quantos_trabalhadores()
    except Exception:  # noqa: BLE001 - codigo antigo nao tem
        return "sem 2.16"


def processar_livro(raiz: Path, pids, saida: Path, campos: dict, campos_pagina: dict) -> dict:
    import fitz
    from core.pipeline import analisar_projeto, processar
    from modelos import Projeto

    saida.parent.mkdir(parents=True, exist_ok=True)
    entrada = montar_entrada(pids, raiz, saida.with_name(saida.stem + "-entrada.pdf"))
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome=saida.stem)
    t0 = time.perf_counter()
    projeto = analisar_projeto(projeto)
    t_analise = time.perf_counter() - t0
    for k, v in campos.items():
        setattr(projeto, k, v)
    if "filtro_padrao" in campos:
        for pg in projeto.paginas:
            pg.filtro = campos["filtro_padrao"]
    for pg in projeto.paginas:
        for k, v in campos_pagina.items():
            setattr(pg, k, v)
    t1 = time.perf_counter()
    processar(projeto)
    t_proc = time.perf_counter() - t1
    with fitz.open(str(saida)) as doc:
        tamanhos = [[round(pg.rect.width / 72 * 2.54, 2), round(pg.rect.height / 72 * 2.54, 2)] for pg in doc]
    info = {
        "pids": pids, "caminho": frase(projeto),
        "pagina": campos_pagina, "campos": campos,
        "tamanhos_cm": tamanhos,
        "avisos": {str(i + 1): list(pg.alertas) for i, pg in enumerate(projeto.paginas_ativas) if pg.alertas},
        "segundos_analise": round(t_analise, 2), "segundos_processar": round(t_proc, 2),
        "tamanho_arquivo_mb": round(saida.stat().st_size / 1e6, 3),
        "trabalhadores": _trab(),
    }
    saida.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def somas(raiz: Path, pids, saida: Path, filtro: str) -> None:
    import fitz
    from core import filtros as F

    codigo = {"original": F.ORIGINAL, "preto_e_branco": F.PRETO_E_BRANCO, "melhorar": F.MELHORAR,
              "magico_pro": getattr(F, "MAGICO_PRO", None)}[filtro]
    resultado = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    with tempfile.TemporaryDirectory(dir=str(_DADOS)) as tmp:
        for pid in pids:
            pdf = Path(tmp) / f"{pid.replace(':', '_').replace('/', '_')}.pdf"
            processar_livro(raiz, [pid], pdf, {"filtro_padrao": codigo}, {})
            with fitz.open(str(pdf)) as doc:
                for i, pg in enumerate(doc):
                    h = hashlib.sha256(f"{pg.rect.width:.3f}x{pg.rect.height:.3f}".encode())
                    for info in pg.get_images(full=True):
                        pix = fitz.Pixmap(doc, info[0])
                        h.update(f"{pix.width}x{pix.height}x{pix.n}".encode())
                        h.update(pix.samples)
                    resultado[f"{pid}|{filtro}|{i}"] = h.hexdigest()
            saida.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
            print(pid, filtro, "ok", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, required=True)
    sub = ap.add_subparsers(dest="modo", required=True)
    a = sub.add_parser("livro")
    a.add_argument("--saida", type=Path, required=True)
    a.add_argument("--campos", default="{}")
    a.add_argument("--pagina", default="{}")
    a.add_argument("pids", nargs="+")
    b = sub.add_parser("somas")
    b.add_argument("--saida", type=Path, required=True)
    b.add_argument("--filtro", required=True)
    b.add_argument("pids", nargs="+")
    o = ap.parse_args()
    raiz = o.raiz.resolve()
    o.saida = o.saida.resolve()
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)
    if os.environ.get("VFR_TRABALHADORES") and (raiz / "core" / "nucleos.py").is_file():
        # 2.16: forca N trabalhadores (o PC esta com pouca memoria livre e o
        # programa cairia sozinho para 1); so para comparar 1 x N
        import core.nucleos as _nuc
        _n = int(os.environ["VFR_TRABALHADORES"])
        _nuc.quantos_trabalhadores = lambda *a, **k: _n
    if o.modo == "livro":
        from core import filtros as F
        campos = json.loads(o.campos)
        if isinstance(campos.get("filtro_padrao"), str) and campos["filtro_padrao"].isupper():
            campos["filtro_padrao"] = getattr(F, campos["filtro_padrao"])
        info = processar_livro(raiz, o.pids, o.saida.resolve(), campos, json.loads(o.pagina))
        print(json.dumps({k: info[k] for k in ("caminho", "tamanhos_cm", "segundos_processar",
                                               "tamanho_arquivo_mb")}, ensure_ascii=False))
    else:
        somas(raiz, o.pids, o.saida.resolve(), o.filtro)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
