"""Simula, SEM mudar o programa, como ficaria o Preto e branco se o vermelho saisse preto.

Uso (no .venv do programa):
    .venv\\Scripts\\python.exe relatorios\\conferencia-2-2026-09-30\\scripts\\simular_vermelho.py

O que faz: passa a pagina do gabarito pelo MESMO caminho do programa de verdade
(conferencia.processar_pelo_programa: analise automatica + "Confirmar e processar",
corte, endireitar, gravura, filtro Preto e branco), duas vezes:
  1. como esta hoje;
  2. trocando, so dentro deste processo e com unittest.mock, a conversao para cinza
     do Preto e branco (core.filtros._cinza_para_binarizar) pela conversao comum
     (a do brilho), na qual o vermelho fica escuro como a tinta preta.
Nenhum arquivo do programa e alterado; o PDF de trabalho vai para uma pasta
temporaria e e apagado pelo proprio conferencia.py.

Por que o caminho inteiro e nao so o filtro: a conversao especial (vermelho claro)
so vale quando a cor e minoria na pagina (menos de 25% de pontos coloridos,
core/filtros.py). O Graduale 222 fica perto desse limite (21% na pagina inteira,
~25% depois do corte), entao rodar so o filtro na pagina sem corte daria outro
resultado que o programa. Medido em 30/09: no programa de hoje a pauta do
Graduale 222 JA sai preta; so os titulos vermelhos da Horas 13 somem.
Grava em relatorios/conferencia-2-2026-09-30/vermelho/simulacao/.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest import mock

import cv2

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
import conferencia  # noqa: E402
import core.filtros as F  # noqa: E402

SAIDA = Path(__file__).resolve().parents[1] / "vermelho" / "simulacao"


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    conferencia._garantir_aplicacao_qt()
    trabalho = Path(tempfile.mkdtemp(prefix="simular_vermelho_"))
    for pg in ("horas_p013", "graduale_p222", "graduale_p221", "graduale_p223"):
        pdf = RAIZ / "gabarito" / "paginas" / f"{pg}.pdf"
        hoje = conferencia.processar_pelo_programa(pdf, F.PRETO_E_BRANCO, trabalho)
        cv2.imwrite(str(SAIDA / f"{pg}-hoje.png"), hoje.imagem)
        with mock.patch.object(F, "_cinza_para_binarizar", lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)):
            muda = conferencia.processar_pelo_programa(pdf, F.PRETO_E_BRANCO, trabalho)
        cv2.imwrite(str(SAIDA / f"{pg}-vermelho-preto.png"), muda.imagem)
        print("feito", pg, hoje.imagem.shape, flush=True)
    try:
        trabalho.rmdir()
    except OSError:
        pass


if __name__ == "__main__":
    main()
