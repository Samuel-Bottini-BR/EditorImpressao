"""Antes/depois da "Tinta com a cor original" com os dois jeitos (2.18), 22/10/2026.

Resposta do Samuel à pergunta b-8-tinta-com-cor: "As duas: A e B como opções
separadas". A = "cor como no livro" (de fábrica, o de sempre); B = "cor
escurecida" (agora de verdade no programa, não mais simulada).

Cada página passa pelo caminho inteiro de livro novo, com os ajustes de
fábrica (core.pipeline.analisar_projeto + processar): girar (de 90 em 90, o que
a análise achar) → dividir → endireitar → cortar → filtro Preto e branco; a
área marcada à mão vai POR CIMA da marcação que o programa acha sozinho, como
na tela. Páginas: Livro de Horas 13 (título vermelho e azul), Escola de Jesus 7
(título em tinta cinza-marrom) e Opus Majus 3 (folha de rosto com o título em
vermelho). Só páginas que vão ser impressas.

USO (da worktree que se quer provar; um modo por processo):
    python relatorios\\fase2-novas\\scripts\\tinta_a_e_b.py fotos [--raiz <worktree>]
    python relatorios\\fase2-novas\\scripts\\tinta_a_e_b.py somas-a <saida.json> [--raiz <worktree>]
"fotos" grava em relatorios/conferir/fase2-novas/tinta-a-e-b/ (fora do git).
"somas-a" grava a soma de cada PDF com a área A (para comparar a worktree
antiga, f26407c, com a nova: têm de dar iguais).
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

SAIDA = AQUI.parents[3] / "relatorios" / "conferir" / "fase2-novas" / "tinta-a-e-b"

# (página, nome, área marcada à mão em fração da página pronta)
CASOS = [
    ("horas_p013", "Livro de Horas 13 (título vermelho e azul)", (0.10, 0.11, 0.80, 0.27)),
    ("escola_p007", "Na Escola de Jesus 7 (título em tinta cinza-marrom)", (0.0, 0.0, 1.0, 0.065)),
    ("opusmajus_p003", "Opus Majus 3 (folha de rosto, título em vermelho)", (0.08, 0.08, 0.80, 0.27)),
]


def _caminho(projeto) -> str:
    """A frase de cada foto: por onde a página passou (o girar primeiro)."""
    giros = sorted({int(f.rotacao) % 360 for f in projeto.folhas})
    girar = "girar: " + (", ".join(f"{g}°" for g in giros) if any(giros)
                         else "0° (a análise não precisou girar)")
    return girar + " → " + rp._por_onde_passou(projeto)


def _processar(raiz, pid, pasta, rotulo, filtro, regiao=None):
    """Uma página pelo caminho inteiro; devolve (imagem, frase, pdf)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import processar, renderizar_pagina

    pdf = pasta / f"{pid}-{rotulo}.pdf"
    projeto = rp._projeto_de_fabrica(rp._gabarito(raiz, pid), pdf)
    projeto.filtro_padrao = filtro
    for pagina in projeto.paginas:
        pagina.filtro = filtro
    if regiao is not None:
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            for pagina in projeto.paginas_ativas:
                renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                marcacao = pagina.obter_selecao()
                marcacao.acrescentar(regiao)
                pagina.guardar_selecao(marcacao)
        finally:
            doc.close()
    processar(projeto)
    return ad._paginas_do_pdf(pdf, dpi=300)[0], _caminho(projeto), pdf


def _regiao(area, escurecida):
    from core.selecao import MAO, TINTA_COR, Regiao

    regiao = Regiao(tipo=TINTA_COR, pontos=[area[:2], area[2:]], origem=MAO)
    if escurecida:
        regiao.tinta_escurecida = True
    return regiao


def fotos(raiz: Path) -> int:
    import cv2
    import numpy as np
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    SAIDA.mkdir(parents=True, exist_ok=True)
    tmp = SAIDA / "_pdfs"
    tmp.mkdir(exist_ok=True)
    for pid, nome, area in CASOS:
        orig, f_o, _ = _processar(raiz, pid, tmp, "original", ORIGINAL)
        pb, f_p, _ = _processar(raiz, pid, tmp, "pb", PRETO_E_BRANCO)
        a, f_a, _ = _processar(raiz, pid, tmp, "a", PRETO_E_BRANCO, _regiao(area, False))
        b, f_b, _ = _processar(raiz, pid, tmp, "b", PRETO_E_BRANCO, _regiao(area, True))
        marcada = f" + área marcada à mão como \"Tinta com a cor original, papel branco\" {area}"
        paineis = [
            (f"{nome}: Original", orig, f_o),
            ("Preto e branco (sem área): a cor vira preto", pb, f_p),
            ("A: \"cor como no livro\" (de fábrica)", a, f_a + marcada + ", jeito A"),
            ("B: \"cor escurecida\" (novo)", b, f_b + marcada + ", jeito B"),
        ]
        cv2.imwrite(str(SAIDA / f"{pid}-pagina.jpg"), ad._lado_a_lado(paineis, altura=1000),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        h, w = orig.shape[:2]
        x0, y0, x1, y1 = int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h)
        tiras = []
        for titulo, im, frase in paineis:
            pedaco = im[y0:y1, x0:x1]
            largura = min(1400, pedaco.shape[1])
            pedaco = cv2.resize(pedaco, (largura, int(pedaco.shape[0] * largura / pedaco.shape[1])))
            tiras.append(ad._faixa(pedaco, [titulo] + ad._quebrar(frase, largura)))
        largura = max(t.shape[1] for t in tiras)
        tiras = [cv2.copyMakeBorder(t, 0, 8, 0, largura - t.shape[1], cv2.BORDER_CONSTANT,
                                    value=(255, 255, 255)) for t in tiras]
        cv2.imwrite(str(SAIDA / f"{pid}-titulo-ampliado.jpg"), np.vstack(tiras),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        # números: quanto a tinta de dentro da área escureceu (brilho médio)
        dentro_a = cv2.cvtColor(a[y0:y1, x0:x1], cv2.COLOR_BGR2LAB)[..., 0]
        dentro_b = cv2.cvtColor(b[y0:y1, x0:x1], cv2.COLOR_BGR2LAB)[..., 0]
        tinta = dentro_a < 200
        fora_igual = int(np.count_nonzero(np.any(a != b, axis=2)) -
                         np.count_nonzero(np.any(a[y0:y1, x0:x1] != b[y0:y1, x0:x1], axis=2)))
        print(json.dumps({"pagina": pid, "brilho_da_tinta_A": round(float(dentro_a[tinta].mean()), 1),
                          "brilho_da_tinta_B": round(float(dentro_b[tinta].mean()), 1),
                          "pontos_diferentes_fora_da_area": fora_igual}, ensure_ascii=False), flush=True)
    return 0


def somas_a(raiz: Path, destino: Path) -> int:
    """As somas dos PDFs com a área A, para comparar o código antigo e o novo."""
    import tempfile
    from core.filtros import PRETO_E_BRANCO

    resultado = {}
    with tempfile.TemporaryDirectory() as tmp:
        for pid, _nome, area in CASOS:
            _img, _f, pdf = _processar(raiz, pid, Path(tmp), "a", PRETO_E_BRANCO, _regiao(area, False))
            for i, soma in enumerate(rp._somas_do_pdf(pdf)):
                resultado[f"{pid}|A|{i}"] = soma
            print(pid, "ok", flush=True)
    destino.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
    return 0


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("modo", choices=("fotos", "somas-a"))
    analisador.add_argument("saida", nargs="?", type=Path)
    analisador.add_argument("--raiz", type=Path, default=rp.RAIZ_PADRAO)
    args = analisador.parse_args()
    raiz = args.raiz.resolve()
    rp._preparar(raiz)
    if args.modo == "fotos":
        return fotos(raiz)
    return somas_a(raiz, args.saida)


if __name__ == "__main__":
    raise SystemExit(main())
