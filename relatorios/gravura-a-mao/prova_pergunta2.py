"""Prova da pergunta 2 da D-659 (ressalva 4): o Automático DEPOIS do Preto e branco à mão.

O que faz, sem janela e pela mesma conta do programa: abre uma CÓPIA do PDF do *Na escola de
Jesus* como livro novo (core/automatico.livro_leve, como a janela abre) e, na página 8:
  (A) Preto e branco escolhido à mão (o filtro e a marca FILTRO, o que o clique no painel grava),
      "Respeitar as gravuras achadas" marcada (de fábrica): desenha no tamanho do PDF;
  (B) em seguida roda o Automático no livro como no print 02 do Samuel: só "Limpar a folha"
      marcada (Preto e branco), todas as outras etapas desmarcadas, incluindo "Gravuras e fotos"
      (core/automatico.rodar, a mesma conta do "Rodar"), respondendo "Rodar nelas também" à
      pergunta das páginas mexidas à mão (D-004): desenha a página 8 de novo;
  (C) o mesmo de B, com "Gravuras em tons de cinza" marcada na página 8;
  (D) o mesmo de B, respondendo "Pular" (a página 8 mexida fica como está).
Cada cenário começa de um livro novo, com a (A) feita.
Grava cada uma com a página inteira e um recorte da gravura (o mesmo enquadramento nas três).

Também mede quanto a procura da gravura leva por página (o detector de verdade, no tamanho do
PDF), em páginas espalhadas do livro, para estimar o tempo a mais em 199 páginas se a
"Respeitar" sozinha também procurasse depois do Automático.

Nunca abre janela, nunca abre nem grava o projeto do Samuel (o projeto aqui é só na memória).
Uso: .venv\\Scripts\\python.exe relatorios\\gravura-a-mao\\prova_pergunta2.py <pdf> <pasta>
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")      # nada de janela (ordem do Samuel)
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import automatico as A  # noqa: E402
from core import detectar_regioes, etapas, pipeline  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf, info_paginas  # noqa: E402
from modelos import Projeto  # noqa: E402

PAGINA = 7                       # a página 8
RECORTE = (0.0, 0.45)            # a gravura: do alto até 45% da altura (o mesmo nas três)


def _livro_novo(pdf: str):
    projeto = Projeto(caminho_entrada=pdf, nome="copia")
    doc = abrir_pdf(pdf)
    A.livro_leve(projeto, [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)])
    return projeto, doc


def _desenho(doc, projeto, indice: int) -> np.ndarray:
    img, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[indice],
                                        dpi=projeto.qualidade_dpi)
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _quadro(img: np.ndarray, titulo: str, cor) -> np.ndarray:
    """A página inteira à esquerda e a gravura de perto à direita, com o título em cima."""
    h = 1300
    inteira = cv2.resize(img, (int(img.shape[1] * h / img.shape[0]), h), interpolation=cv2.INTER_AREA)
    y0, y1 = int(img.shape[0] * RECORTE[0]), int(img.shape[0] * RECORTE[1])
    perto = img[y0:y1]
    perto = cv2.resize(perto, (int(perto.shape[1] * h / perto.shape[0]), h), interpolation=cv2.INTER_AREA)
    corpo = np.hstack([inteira, np.full((h, 24, 3), 255, np.uint8), perto])
    faixa = np.full((80, corpo.shape[1], 3), cor, np.uint8)
    cv2.putText(faixa, titulo, (20, 56), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 4, cv2.LINE_AA)
    return np.vstack([faixa, corpo])


def main(pdf: str, pasta: str) -> None:
    saida = Path(pasta)
    saida.mkdir(parents=True, exist_ok=True)
    tempos_da_procura: list[tuple[int, float]] = []
    procurando = {"pagina": None}
    detectar_de_verdade = detectar_regioes.detectar

    def detectar(*args, **kwargs):
        inicio = time.perf_counter()
        try:
            return detectar_de_verdade(*args, **kwargs)
        finally:
            tempos_da_procura.append((procurando["pagina"], time.perf_counter() - inicio))

    detectar_regioes.detectar = detectar
    relato = {}
    imagens = {}

    def cenario(nome: str, automatico: bool, pular: bool = False, cinza: bool = False):
        """Livro novo, (A) na página 8 e, se `automatico`, o Automático do print 02 (só
        "Limpar a folha", Preto e branco), com a resposta `pular` à pergunta das páginas
        mexidas à mão (D-004: "Pular" = True, "Rodar nelas também" = False)."""
        projeto, doc = _livro_novo(pdf)
        try:
            pagina = projeto.paginas[PAGINA]
            pagina.filtro = PRETO_E_BRANCO                      # o clique no painel
            etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)
            assert pagina.respeitar_gravuras_achadas and not pagina.gravuras_em_tons_de_cinza
            procurando["pagina"] = PAGINA
            antes = len(tempos_da_procura)
            img = _desenho(doc, projeto, PAGINA)               # (A): a tela/PDF da página 8
            info = {"A_procurou": len(tempos_da_procura) - antes,
                    "A_areas_achadas": len(pagina.selecao or [])}
            if automatico:
                desmarcadas = [e for e in A.ETAPAS if e != A.LIMPAR]
                pedido = A.Pedido(etapas=[A.LIMPAR], opcoes={"filtro_padrao": PRETO_E_BRANCO},
                                  pular_mexidas=pular, desmarcadas=desmarcadas)
                info["mexidas_que_o_automatico_pergunta"] = [
                    i + 1 for i in A.paginas_mexidas(projeto, pedido)]
                inicio = time.perf_counter()
                A.rodar(projeto, pedido)
                info["rodar_segundos"] = round(time.perf_counter() - inicio, 2)
                if cinza:
                    pagina.gravuras_em_tons_de_cinza = True
                antes = len(tempos_da_procura)
                img = _desenho(doc, projeto, PAGINA)
                info.update({
                    "procurou_depois": len(tempos_da_procura) - antes,
                    "limpar_no_livro": projeto.limpar,
                    "gravuras_e_fotos_ligada": A.ligada_no_livro(projeto, A.GRAVURAS),
                    "pagina_no_automatico": list(getattr(pagina, "automatico", []) or []),
                    "filtro_da_pagina": pagina.filtro,
                    "respeitar": pagina.respeitar_gravuras_achadas,
                    "cinza": pagina.gravuras_em_tons_de_cinza,
                    "a_marcacao_da_maquina_vale": etapas.a_marcacao_da_maquina_vale(projeto, pagina),
                    "areas_guardadas_na_pagina": len(pagina.selecao or []),
                    "mexida_a_mao": list(getattr(pagina, "mexida_a_mao", []) or []),
                    "gravura_feita_com": bool(getattr(pagina, "gravura_feita_com", "")),
                    "gravura_achada_a_mao": bool(getattr(pagina, "gravura_achada_a_mao", False))})
        finally:
            doc.close()
        imagens[nome] = img
        relato[nome] = info

    cenario("A", automatico=False)
    cenario("B", automatico=True, pular=False)
    cenario("C", automatico=True, pular=False, cinza=True)
    cenario("D", automatico=True, pular=True)
    a, b, c, d = (imagens[k] for k in "ABCD")

    for nome, img, titulo, cor in (
            ("q2-a-a-mao", a, "A - Preto e branco a mao, Respeitar marcada", (40, 140, 40)),
            ("q2-b-depois-do-automatico", b,
             "B - depois do Automatico, 'Rodar nelas tambem' (Gravuras e fotos desmarcada)",
             (40, 40, 180)),
            ("q2-c-com-cinza", c, "C - como B, com Gravuras em tons de cinza marcada", (140, 90, 30)),
            ("q2-d-pulou", d, "D - depois do Automatico, 'Pular' a pagina mexida (D-661)", (110, 60, 110))):
        cv2.imwrite(str(saida / f"{nome}.jpg"), _quadro(img, titulo, cor), [cv2.IMWRITE_JPEG_QUALITY, 84])

    def igual(x, y):
        return bool(x.shape == y.shape and np.array_equal(x, y))

    def pontos_diferentes(x, y):
        if x.shape != y.shape:
            return "tamanhos diferentes"
        return int(np.any(x != y, axis=2).sum())

    relato["D_igual_A"] = igual(d, a)
    relato["D_pontos_diferentes_de_A"] = pontos_diferentes(d, a)
    relato["C_igual_A"] = igual(c, a)
    relato["C_pontos_diferentes_de_A"] = pontos_diferentes(c, a)
    relato["B_colorido_ou_cinza_na_gravura"] = float(
        ((lambda g: ((g > 10) & (g < 245)).mean())(cv2.cvtColor(
            b[: int(b.shape[0] * RECORTE[1])], cv2.COLOR_BGR2GRAY))))

    # o tempo da procura por página, em páginas espalhadas (livro novo, Preto e branco à mão)
    projeto, doc = _livro_novo(pdf)
    try:
        amostra = [12, 30, 55, 80, 105, 130, 155, 180, 195]
        tempos_da_procura.clear()
        for indice in amostra:
            p = projeto.paginas[indice]
            p.filtro = PRETO_E_BRANCO
            etapas.marcar_mexida_a_mao(p, etapas.FILTRO)
            procurando["pagina"] = indice
            _desenho(doc, projeto, indice)
    finally:
        doc.close()
    so = [t for _i, t in tempos_da_procura]
    relato["procura_por_pagina_segundos"] = [round(t, 2) for t in so]
    media = float(np.mean(so)) if so else 0.0
    relato["procura_media_segundos"] = round(media, 2)
    relato["a_mais_em_199_paginas_segundos"] = round(media * 199, 0)
    (saida / "q2-medidas.json").write_text(json.dumps(relato, indent=1, ensure_ascii=False),
                                          encoding="utf-8")
    print(json.dumps(relato, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
