"""Item 4 da etapa 9d: "Deixar a folha em branco" (e "pintar de branco") numa
página "Tirar o fundo" de que o fundo FOI tirado, pelo caminho inteiro do
programa, com o código de --raiz (o de antes ou o desta etapa).

Livro novo de fábrica com a página-gabarito pedida (PDF com camadas, do Internet
Archive; só lido), no filtro "Tirar o fundo" com "Limpar a folha"; a página
passa por core.pipeline.processar e a imagem é lida do PDF gravado.
USO (da pasta da worktree):
    python relatorios/obra-etapa9d/scripts/folha_em_branco_sem_fundo.py --raiz <código> --saida <pasta> pid [...]
Grava <pasta>/<pid>-{sem-marcar,folha-em-branco,pintar}.png e imprime o
mínimo (o ponto mais escuro) de cada uma.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

_DADOS = Path(tempfile.gettempdir()) / "etapa9d_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("pids", nargs="+")
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    sys.path.insert(0, str(raiz))
    import cv2
    import fitz
    import numpy as np

    from core import pipeline
    from core.filtros import TIRAR_FUNDO
    from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao
    from modelos import Projeto

    a.saida.mkdir(parents=True, exist_ok=True)
    gabarito = Path(__file__).resolve().parents[3] / "gabarito" / "paginas"
    for pid in a.pids:
        for nome, caixa in (("sem-marcar", None), ("folha-em-branco", (0.0, 0.0, 1.0, 1.0)),
                            ("pintar", (0.0, 0.0, 1.0, 0.5))):
            projeto = Projeto(caminho_entrada=str(gabarito / f"{pid}.pdf"), nome=pid,
                              caminho_saida=str(a.saida / f"{pid}-{nome}.pdf"))
            projeto.montar_cadernos = False
            projeto = pipeline.analisar_projeto(projeto)
            if not projeto.tem_camadas:
                print(pid, "sem camadas; pulei")
                break
            projeto.limpar = True
            pagina = projeto.paginas_ativas[0]
            pagina.filtro = TIRAR_FUNDO
            if caixa is not None:
                x0, y0, x1, y1 = caixa
                sel = Selecao()
                sel.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                                       origem=MAO))
                pagina.guardar_selecao(sel)
            pipeline.processar(projeto)
            with fitz.open(projeto.caminho_saida) as doc:
                pix = doc[0].get_pixmap(dpi=100, colorspace=fitz.csRGB)
                img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(a.saida / f"{pid}-{nome}.png"), img)
            print(f"{pid} {nome:16s} mínimo {int(img.min())}  tinta (<100): "
                  f"{float((img.min(axis=2) < 100).mean()):.2%}", flush=True)


if __name__ == "__main__":
    main()
