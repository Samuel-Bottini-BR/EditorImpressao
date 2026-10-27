"""Lista única 4.5 (PDF gigante): quanto cada página ocupa no PDF, sem perda
(o jeito de antes, zlib) e em JPEG 92 (etapa 10b), e quanto a imagem muda.

Usa o projeto salvo do teste dos 14 livros (23/10/2026), as páginas pedidas,
com o filtro que o livro usou, pelo corpo do processar (_pagina_pronta).
USO: python tamanho_do_pdf.py livro:pagina [...]   (saída: tabela no terminal)
"""
from __future__ import annotations

import importlib.util
import sys
import zlib
from pathlib import Path

AQUI = Path(__file__).resolve()
sys.path.insert(0, str(AQUI.parents[3]))
spec = importlib.util.spec_from_file_location("rep", AQUI.parent / "reproduzir.py")
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core.pdf_io import _imagem_comprimida  # noqa: E402


def main() -> None:
    for alvo in sys.argv[1:]:
        livro, n = alvo.split(":")
        projeto = rep.carregar(livro)
        for pagina in rep.paginas_da_folha(projeto, int(n)):
            img = rep.pronta(projeto, pagina)
            if img.ndim == 3:
                sem_perda = len(zlib.compress(cv2.cvtColor(img, cv2.COLOR_BGR2RGB).tobytes(), 9))
            else:
                sem_perda = len(zlib.compress(img.tobytes(), 9))
            _d, dados, filtro = _imagem_comprimida(img)
            lida = cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_UNCHANGED)
            dif = np.abs(lida.astype(np.int16) - img.astype(np.int16))
            print(f"{alvo:16s} {pagina.filtro:15s} {img.shape[1]}x{img.shape[0]}  sem perda "
                  f"{sem_perda / 1e6:6.2f} MB  JPEG {len(dados) / 1e6:5.2f} MB  "
                  f"({len(dados) / sem_perda:.0%})  diferença média {dif.mean():.2f}, "
                  f"99,9% até {np.percentile(dif, 99.9):.0f}", flush=True)


if __name__ == "__main__":
    main()
