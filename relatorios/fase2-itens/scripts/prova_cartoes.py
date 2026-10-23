"""Prova do conserto dos cartões (bug do verificador do 2.9, 21/10/2026), em páginas de verdade.

Para cada página: a amostra dos cartões (70 DPI, como a tela) com "Letra clara
em fundo escuro" marcada; em cada filtro, três imagens lado a lado:
  o cartão ANTES do conserto (aplicar_filtro direto),
  o cartão DEPOIS (core.pipeline.filtro_com_as_caixinhas),
  a página como sai ao escolher o filtro (core.pipeline._filtrar).
E grava se o cartão de depois é igual, ponto por ponto, à página escolhida.

Uso: python prova_cartoes.py <pasta_saida> <pdf>:<pagina> [...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))


def rotulo(img: np.ndarray, texto: str) -> np.ndarray:
    faixa = np.full((28, img.shape[1], 3), 255, np.uint8)
    cv2.putText(faixa, texto, (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([faixa, img])


def main() -> None:
    from core import pipeline as P
    from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO, aplicar_filtro
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import ConfigFolha, ConfigPagina, Projeto

    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    resumo = []
    for item in sys.argv[2:]:
        caminho, numero = item.rsplit(":", 1)
        doc = abrir_pdf(caminho)
        try:
            base = pagina_para_array(doc, int(numero) - 1, dpi=70)
        finally:
            doc.close()
        if base.ndim == 2:
            base = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
        linhas = []
        for filtro in (PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            projeto = Projeto(caminho_entrada=caminho, detectar_regioes=False)
            projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
            pagina = ConfigPagina(indice=0, folha=0, filtro=filtro)
            pagina.claro_no_escuro = True
            projeto.paginas = [pagina]
            antes = aplicar_filtro(base, filtro, 50, 50, 50)[0]
            depois = P.filtro_com_as_caixinhas(
                base, pagina, filtro, 70, 50, 50, 50, algoritmo_pb=pagina.algoritmo_preto_branco,
                despeckle=P.pontinhos_da_pagina(projeto, pagina, base, 70))  # como ui/tarefas.pedir_cartoes
            escolhida = P._filtrar(projeto, pagina, base)[0]
            como3 = [x if x.ndim == 3 else cv2.cvtColor(x, cv2.COLOR_GRAY2BGR)
                     for x in (antes, depois, escolhida)]
            igual = bool(np.array_equal(como3[1], como3[2]))
            resumo.append({"pagina": f"{Path(caminho).name} p. {numero}", "filtro": filtro,
                           "cartao_depois_igual_a_pagina": igual,
                           "cartao_antes_igual_a_pagina": bool(np.array_equal(como3[0], como3[2]))})
            linhas.append(np.hstack([rotulo(como3[0], f"{filtro}: cartao antes"),
                                     rotulo(como3[1], "cartao depois"),
                                     rotulo(como3[2], "escolhendo o filtro")]))
        largura = max(x.shape[1] for x in linhas)
        linhas = [np.pad(x, ((0, 0), (0, largura - x.shape[1]), (0, 0)), constant_values=255) for x in linhas]
        nome = f"{Path(caminho).stem[:30]}-p{numero}.jpg".replace(" ", "_")
        cv2.imwrite(str(saida / nome), np.vstack(linhas), [cv2.IMWRITE_JPEG_QUALITY, 88])
    (saida / "prova.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in resumo:
        print(r)


if __name__ == "__main__":
    main()
