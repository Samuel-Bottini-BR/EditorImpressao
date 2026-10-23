"""Antes/depois do papel da "Tinta com a cor original" (2.18), 22/10/2026.

Resposta do Samuel à pergunta tc23-1 (o retângulo branco no papel creme do
Original): "As duas: escolher o papel em cada área ('papel branco' ou 'papel
como o resto da página')". "papel branco" é o de fábrica (o de sempre); "papel
como o resto da página" (Regiao.papel_da_pagina) deixa o papel da área como o
filtro da página o deixou, e só a tinta segue o A ou o B.

Cada página passa pelo caminho inteiro de livro novo, com os ajustes de
fábrica (o mesmo de tinta_a_e_b.py): girar → dividir → endireitar → cortar →
filtro; a área marcada à mão vai por cima da marcação que o programa acha
sozinho. Páginas: Livro de Horas 13, Escola de Jesus 7, Opus Majus 3.

USO (um modo por processo):
    python relatorios\fase2-novas\scripts\tinta_papel.py fotos [--raiz <worktree>]
    python relatorios\fase2-novas\scripts\tinta_papel.py somas <saida.json> [--raiz <worktree>]
"fotos" grava em relatorios/conferir/fase2-novas/tinta-papel/ (fora do git).
"somas": a soma de cada PDF com a área de fábrica ("papel branco"), A e B, em
Original, Preto e branco e Melhorar; rodar no código antigo (639136a, sem o
campo novo) e no novo: têm de dar iguais.

Desde 23/10/2026 (respostas do Samuel às perguntas 10 e 11):
    python ...	inta_papel.py somas23 <saida.json> [--raiz <worktree>]
    python ...	inta_papel.py pb23 <pasta> [--raiz <worktree>]
    python ...	inta_papel.py juntar23 <pasta-antes> <pasta-depois>
"somas23": as somas sem área, com "papel branco" e com "papel como o resto da
página", A e B, nos três filtros (45 PDFs); rodar no antigo (0acf2c7) e no
novo. "pb23": a Escola 7 em Preto e branco com "papel como o resto da página"
(A), a página do PDF gravada em PNG na <pasta>; "juntar23": o antes/depois em
relatorios/conferir/fase2-novas/pergunta-10/ (fora do git).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve()
sys.path.insert(0, str(AQUI.parent))
import antes_depois as ad  # noqa: E402
import rodada_processar as rp  # noqa: E402
from tinta_a_e_b import CASOS, _processar  # noqa: E402

SAIDA = AQUI.parents[3] / "relatorios" / "conferir" / "fase2-novas" / "tinta-papel"


def _regiao(area, escurecida, papel_da_pagina):
    """A área "tinta com a cor". Os campos só são postos quando ligados: o
    código antigo (sem `papel_da_pagina`) roda o mesmo caso de fábrica."""
    from core.selecao import MAO, TINTA_COR, Regiao

    regiao = Regiao(tipo=TINTA_COR, pontos=[area[:2], area[2:]], origem=MAO)
    if escurecida:
        regiao.tinta_escurecida = True
    if papel_da_pagina:
        regiao.papel_da_pagina = True
    return regiao


def _nome_do_filtro(filtro):
    return {"original": "Original", "preto_e_branco": "Preto e branco",
            "melhorar": "Melhorar"}[filtro]


def fotos(raiz: Path) -> int:
    import cv2
    import numpy as np
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    SAIDA.mkdir(parents=True, exist_ok=True)
    tmp = SAIDA / "_pdfs"
    tmp.mkdir(exist_ok=True)
    jeitos = [("sem área", None),
              ("A + \"papel branco\" (de fábrica, igual ao de antes)", (False, False)),
              ("A + \"papel como o resto da página\" (novo)", (False, True)),
              ("B + \"papel branco\" (de fábrica, igual ao de antes)", (True, False)),
              ("B + \"papel como o resto da página\" (novo)", (True, True))]
    for pid, nome, area in CASOS:
        for filtro in (ORIGINAL, PRETO_E_BRANCO):
            paineis = []
            for i, (titulo, jeito) in enumerate(jeitos):
                regiao = None if jeito is None else _regiao(area, *jeito)
                img, frase, _ = _processar(raiz, pid, tmp, f"{filtro}-{i}", filtro, regiao)
                if jeito is not None:
                    frase += (f" + área marcada à mão \"manter a cor da tinta\" {area}, "
                              f"{'cor escurecida' if jeito[0] else 'cor como no livro'}, "
                              f"{'papel como o resto da página' if jeito[1] else 'papel branco'}")
                paineis.append((f"{nome}, {_nome_do_filtro(filtro)}: {titulo}", img, frase))
            cv2.imwrite(str(SAIDA / f"{pid}-{filtro}-pagina.jpg"),
                        ad._lado_a_lado(paineis, altura=1000), [cv2.IMWRITE_JPEG_QUALITY, 85])
            h, w = paineis[0][1].shape[:2]
            x0, y0 = int(area[0] * w), int(area[1] * h)
            x1, y1 = int(area[2] * w), int(area[3] * h)
            # o título ampliado, com uma folga em volta para ver a beirada da área
            fx, fy = int(0.04 * w), int(0.03 * h)
            x0, y0, x1, y1 = max(0, x0 - fx), max(0, y0 - fy), min(w, x1 + fx), min(h, y1 + fy)
            tiras = []
            for titulo, im, frase in paineis:
                pedaco = im[y0:y1, x0:x1]
                largura = min(1400, pedaco.shape[1])
                pedaco = cv2.resize(pedaco, (largura, int(pedaco.shape[0] * largura / pedaco.shape[1])))
                tiras.append(ad._faixa(pedaco, [titulo] + ad._quebrar(frase, largura)))
            largura = max(t.shape[1] for t in tiras)
            tiras = [cv2.copyMakeBorder(t, 0, 8, 0, largura - t.shape[1], cv2.BORDER_CONSTANT,
                                        value=(255, 255, 255)) for t in tiras]
            cv2.imwrite(str(SAIDA / f"{pid}-{filtro}-titulo-ampliado.jpg"), np.vstack(tiras),
                        [cv2.IMWRITE_JPEG_QUALITY, 88])
            # números: quantos pontos diferem de "sem área" (o retângulo branco some?)
            sem = paineis[0][1]
            dif = {t.split(": ", 1)[1][:40]: int(np.count_nonzero(np.any(
                cv2.absdiff(sem, im) > 12, axis=2))) for t, im, _ in paineis[1:]}
            print(json.dumps({"pagina": pid, "filtro": filtro,
                              "pontos_diferentes_de_sem_area": dif}, ensure_ascii=False), flush=True)
    return 0


def somas(raiz: Path, destino: Path) -> int:
    """As somas dos PDFs com a área de fábrica (papel branco), A e B."""
    import tempfile
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO

    resultado = {}
    with tempfile.TemporaryDirectory() as tmp:
        for pid, _nome, area in CASOS:
            for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR):
                for escura in (False, True):
                    _img, _f, pdf = _processar(raiz, pid, Path(tmp), f"{filtro}-{escura}", filtro,
                                               _regiao(area, escura, False))
                    for i, soma in enumerate(rp._somas_do_pdf(pdf)):
                        resultado[f"{pid}|{filtro}|{'B' if escura else 'A'}|{i}"] = soma
                    print(pid, filtro, "B" if escura else "A", "ok", flush=True)
    destino.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
    return 0


def somas23(raiz: Path, destino: Path) -> int:
    """As somas de 23/10/2026: sem área, e a área com os dois papéis, A e B,
    em Original, Preto e branco e Melhorar. Chave pagina|filtro|jeito|página."""
    import tempfile
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO

    jeitos = [("sem-area", None), ("A-branco", (False, False)), ("A-da-pagina", (False, True)),
              ("B-branco", (True, False)), ("B-da-pagina", (True, True))]
    resultado = {}
    with tempfile.TemporaryDirectory() as tmp:
        for pid, _nome, area in CASOS:
            for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR):
                for nome, jeito in jeitos:
                    regiao = None if jeito is None else _regiao(area, *jeito)
                    _img, _f, pdf = _processar(raiz, pid, Path(tmp), f"{filtro}-{nome}", filtro, regiao)
                    for i, soma in enumerate(rp._somas_do_pdf(pdf)):
                        resultado[f"{pid}|{filtro}|{nome}|{i}"] = soma
                    pdf.unlink(missing_ok=True)
                    print(pid, filtro, nome, "ok", flush=True)
    destino.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
    return 0


def pb23(raiz: Path, pasta: Path) -> int:
    """A Escola 7 em Preto e branco com "papel como o resto da página" (A):
    a página do PDF em PNG e a frase do caminho em texto."""
    import cv2
    from core.filtros import PRETO_E_BRANCO

    pasta.mkdir(parents=True, exist_ok=True)
    pid, _nome, area = CASOS[1]
    img, frase, _pdf = _processar(raiz, pid, pasta, "pb-papel-da-pagina", PRETO_E_BRANCO,
                                  _regiao(area, False, True))
    cv2.imwrite(str(pasta / f"{pid}-pb-papel-da-pagina.png"), img)
    (pasta / f"{pid}-pb-papel-da-pagina.txt").write_text(
        frase + f" + área marcada à mão \"manter a cor da tinta\" {area}, cor como no livro, "
        "papel como o resto da página", encoding="utf-8")
    return 0


def juntar23(antes: Path, depois: Path) -> int:
    """Antes (0acf2c7) e depois, um sob o outro: a página inteira e o título
    ampliado 3 vezes. Grava em relatorios/conferir/fase2-novas/pergunta-10/."""
    import cv2
    import numpy as np

    pid, _nome, area = CASOS[1]
    destino = SAIDA.parent / "pergunta-10"
    destino.mkdir(parents=True, exist_ok=True)
    nome = f"{pid}-pb-papel-da-pagina"
    a = cv2.imread(str(antes / f"{nome}.png"))
    d = cv2.imread(str(depois / f"{nome}.png"))
    frase = (depois / f"{nome}.txt").read_text(encoding="utf-8")
    titulos = ["ANTES (hoje, 0acf2c7): contorno preto em volta da letra",
               "DEPOIS: igual a \"papel branco\", letra limpa"]
    cv2.imwrite(str(destino / f"{pid}-preto_e_branco-pagina.jpg"),
                ad._lado_a_lado([(titulos[0], a, frase), (titulos[1], d, frase)], altura=1000),
                [cv2.IMWRITE_JPEG_QUALITY, 85])
    h, w = d.shape[:2]
    x0, y0, x1, y1 = 0, 0, int(0.5 * w), int(min(1.0, area[3] + 0.02) * h)
    tiras = []
    for titulo, im in zip(titulos, (a, d)):
        pedaco = cv2.resize(im[y0:y1, x0:x1], None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        pedaco = pedaco[:, :min(1800, pedaco.shape[1])]
        tiras.append(ad._faixa(pedaco, [titulo + " (metade esquerda do título, ampliada 3 vezes)"]
                               + ad._quebrar(frase, pedaco.shape[1])))
    largura = max(t.shape[1] for t in tiras)
    tiras = [cv2.copyMakeBorder(t, 0, 8, 0, largura - t.shape[1], cv2.BORDER_CONSTANT,
                                value=(255, 255, 255)) for t in tiras]
    cv2.imwrite(str(destino / f"{pid}-preto_e_branco-letra-de-perto.jpg"), np.vstack(tiras),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    mudou = int(np.count_nonzero(np.any(a != d, axis=2))) if a.shape == d.shape else -1
    print(json.dumps({"pontos_diferentes_antes_depois": mudou}), flush=True)
    return 0


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("modo", choices=("fotos", "somas", "somas23", "pb23", "juntar23"))
    analisador.add_argument("saida", nargs="?", type=Path)
    analisador.add_argument("depois", nargs="?", type=Path)
    analisador.add_argument("--raiz", type=Path, default=rp.RAIZ_PADRAO)
    args = analisador.parse_args()
    if args.modo == "juntar23":
        return juntar23(args.saida, args.depois)
    raiz = args.raiz.resolve()
    rp._preparar(raiz)
    if args.modo == "fotos":
        return fotos(raiz)
    if args.modo == "somas23":
        return somas23(raiz, args.saida)
    if args.modo == "pb23":
        return pb23(raiz, args.saida)
    return somas(raiz, args.saida)


if __name__ == "__main__":
    raise SystemExit(main())
