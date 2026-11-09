"""Gera as imagens da prova da D-659 para o Samuel (relatorios/gravura-a-mao/).

O que faz: abre uma CÓPIA do PDF do *Na escola de Jesus* (199 páginas, rodapé
alexandriacatolica.blogspot.com.br) como LIVRO NOVO, do mesmo jeito que a janela abre
(core/automatico.livro_leve: nada do Automático ligado), e desenha a página 8 em Preto e
branco escolhido À MÃO (o que o painel "Filtro da página" grava: o filtro e a marca FILTRO),
no tamanho do PDF, com cada combinação das três caixinhas; e uma página sem gravura. Mede o
tempo do desenho e quantas vezes o detector de gravura rodou em cada caso.

Nunca abre nem grava o projeto do Samuel: o projeto aqui é só na memória, e o PDF é a cópia.

Uso: .venv\\Scripts\\python.exe relatorios\\gravura-a-mao\\gerar_imagens.py <pdf> <pasta> <rotulo>
  rotulo: "antes" (rodar no código de antes do conserto) ou "depois".
Escreve <pasta>/<rotulo>-<caso>.png e <pasta>/<rotulo>-tempos.json.
Seguro mudar: as páginas e os casos. Arriscado: gravar o projeto (não grava).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402

from core import automatico, detectar_regioes, etapas, pipeline  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf, info_paginas  # noqa: E402
from modelos import Projeto  # noqa: E402

CASOS = {
    # caso: (pagina, respeitar, cinza, so_as_letras)
    "p8-respeitar": (7, True, False, False),
    "p8-cinza": (7, False, True, False),
    "p8-respeitar-e-cinza": (7, True, True, False),
    "p8-so-as-letras": (7, False, False, True),
    "p8-tres-desmarcadas": (7, False, False, False),
    "p6-sem-gravura-respeitar": (5, True, False, False),
}


def _livro_novo(pdf: str):
    projeto = Projeto(caminho_entrada=pdf, nome="copia")
    doc = abrir_pdf(pdf)
    automatico.livro_leve(projeto, [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)])
    return projeto, doc


def main(pdf: str, pasta: str, rotulo: str) -> None:
    saida = Path(pasta)
    saida.mkdir(parents=True, exist_ok=True)
    chamadas = []
    detectar_de_verdade = detectar_regioes.detectar

    def detectar(*args, **kwargs):
        inicio = time.perf_counter()
        try:
            return detectar_de_verdade(*args, **kwargs)
        finally:
            chamadas.append(time.perf_counter() - inicio)

    detectar_regioes.detectar = detectar
    tempos = {}
    for caso, (indice, respeitar, cinza, letras) in CASOS.items():
        projeto, doc = _livro_novo(pdf)
        try:
            pagina = projeto.paginas[indice]
            # o que o painel grava ao clicar em Preto e branco e nas caixinhas
            pagina.filtro = PRETO_E_BRANCO
            etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)
            pagina.respeitar_gravuras_achadas = respeitar
            pagina.gravuras_em_tons_de_cinza = cinza
            pagina.misto_so_as_letras = letras
            antes = len(chamadas)
            inicio = time.perf_counter()
            img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
            total = time.perf_counter() - inicio
            procuras = chamadas[antes:]
            cv2.imwrite(str(saida / f"{rotulo}-{caso}.png"), img)
            outras = [p.indice for p in projeto.paginas if p.selecao and p is not pagina]
            tempos[caso] = {"pagina": indice + 1, "segundos_do_desenho": round(total, 2),
                            "vezes_que_procurou": len(procuras),
                            "segundos_da_procura": round(sum(procuras), 2),
                            "outras_paginas_com_marcacao": outras,
                            "dpi": projeto.qualidade_dpi}
            print(caso, tempos[caso], flush=True)
        finally:
            doc.close()
    (saida / f"{rotulo}-tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                 encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
