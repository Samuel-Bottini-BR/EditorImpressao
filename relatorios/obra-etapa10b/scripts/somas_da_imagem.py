"""Somas das páginas-gabarito ANTES de ir para o PDF (etapa 10b, 27/10/2026).

PARA QUÊ
    A etapa 10b passa a guardar as páginas de tons em JPEG (lista única 4.5):
    a soma dos pontos LIDOS do PDF muda em toda página de cor, mesmo quando o
    filtro não mudou nada. Para separar "o filtro mudou a página" de "o PDF
    guarda de outro jeito", aqui a soma é da imagem que o processar entrega ao
    escritor do PDF (core.pipeline._pagina_pronta), página-gabarito por
    página-gabarito, como livro novo de fábrica (dividir → endireitar → cortar
    → filtro), em Original, Preto e branco e Melhorar.

USO (da pasta da worktree):
    python relatorios/obra-etapa10b/scripts/somas_da_imagem.py --raiz <código> --saida s.json [--imagens pasta] [pid ...]
Sem pid: as 32 do gabarito. Com --imagens, grava cada página (PNG) para olhar
as que mudarem. A pasta de dados do programa vai para uma pasta temporária.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

_DADOS = Path(tempfile.gettempdir()) / "etapa10b_somas_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)
AQUI = Path(__file__).resolve()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--imagens", default="")
    ap.add_argument("pids", nargs="*")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.raiz).resolve()))
    import cv2

    from core import pipeline
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    raiz_gab = AQUI.parents[3] / "gabarito"
    pids = a.pids or sorted(json.loads((raiz_gab / "lista.json").read_text(encoding="utf-8"))["paginas"])
    saida = Path(a.saida)
    resultado = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    pasta = Path(a.imagens) if a.imagens else None
    if pasta:
        pasta.mkdir(parents=True, exist_ok=True)
    for pid in pids:
        entrada = raiz_gab / "paginas" / f"{pid}.pdf"
        for nome, codigo in (("original", ORIGINAL), ("preto_e_branco", PRETO_E_BRANCO),
                             ("melhorar", MELHORAR)):
            projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(_DADOS / "x.pdf"), nome=pid)
            projeto = pipeline.analisar_projeto(projeto)
            projeto.filtro_padrao = codigo
            doc = abrir_pdf(str(entrada))
            try:
                for i, pagina in enumerate(p for p in projeto.paginas if not p.apagada):
                    pagina.filtro = codigo
                    folha = projeto.folhas[pagina.folha]
                    img, mono = pipeline._pagina_pronta(projeto, doc, folha, pagina,
                                                        pipeline._FolhaDaVez(), 0)
                    h = hashlib.sha256(f"{img.shape}|{mono}".encode())
                    h.update(img.tobytes())
                    resultado[f"{pid}|{nome}|{i}"] = h.hexdigest()
                    if pasta:
                        cv2.imwrite(str(pasta / f"{pid}-{nome}-{i}.png"), img)
            finally:
                doc.close()
        saida.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
        print(pid, "ok", flush=True)


if __name__ == "__main__":
    main()
