"""O tamanho do livro no PDF GERADO, com o corte que segue o conteúdo (2.5),
sozinho e com a borda preta (2.13). Teste de reversão dos defeitos achados
pelo verificador gerando o Egenloff (folhas 1 a 14) em 21/10/2026
(ramo verif-caixa-2026-10-21, relatorios/conferir/caixa-conteudo-2026-10-21/):

1. só o 2.5: páginas de um mesmo livro saíam de tamanhos diferentes (3 e 4
   com 252 x 381 mm, as outras 255 x 363). Causa: o tamanho do livro era
   guardado em mm pelo DPI "dito" à conta do ScanTailor, que muda de página
   para página (o teto de pontos depende do tamanho de cada imagem); o mesmo
   tamanho em mm virava um número diferente de pontos em cada página.
2. com as duas opções: a página 6 saía uma tira de 253 x 139 mm. Causa: o
   bloco de texto dela é mais largo que os enfeites das outras, ela ficava
   fora da conta ("muito maior") e saía no tamanho DELA, baixinha.

O livro de mentira imita o Egenloff: PDF que diz 72 DPI (folhas de ~35 x 46
cm), imagens de alturas um pouco diferentes, e uma página com um bloco de
texto largo e baixo. Precisa da DLL do ScanTailor (pula sem ela).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import pipeline  # noqa: E402
from core import st_ferramentas  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from modelos import Projeto  # noqa: E402

pytestmark = pytest.mark.skipif(st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None,
                                reason="sem a DLL do ScanTailor")

# (altura da imagem em pontos, bloco de "enfeite" (x0, y0, x1, y1))
FOLHAS = [(1287, (330, 320, 670, 900)), (1317, (320, 330, 680, 910)), (1300, (335, 300, 665, 920)),
          (1317, (325, 340, 675, 905)), (1290, (330, 310, 670, 915)),
          (1317, (180, 560, 820, 700)),             # a "página 6": texto largo e baixo
          (1317, (330, 320, 670, 900)),
          (1300, None)]                              # verso em branco (21/10: saía maior)
LARGURA = 1000


@pytest.fixture(autouse=True)
def _limpo():
    for g in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()
    yield
    for g in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()


def _livro(pasta: Path) -> str:
    caminho = pasta / "livro.pdf"
    doc = fitz.open()
    for i, (altura, bloco) in enumerate(FOLHAS):
        img = np.full((altura, LARGURA, 3), 216, np.uint8)
        img[:, :20] = img[:, -20:] = 20                      # moldura preta do scanner
        img[:20, :] = img[-20:, :] = 20
        if bloco is None:
            cv2.imwrite(str(pasta / f"f{i}.png"), img)
            pg = doc.new_page(width=LARGURA, height=altura)
            pg.insert_image(pg.rect, filename=str(pasta / f"f{i}.png"))
            continue
        x0, y0, x1, y1 = bloco
        for y in range(y0, y1 - 8, 18):
            for x in range(x0, x1 - 20, 28):
                cv2.rectangle(img, (x, y), (x + 20, y + 8), (40, 40, 40), -1)
        png = pasta / f"f{i}.png"
        cv2.imwrite(str(png), img)
        pg = doc.new_page(width=LARGURA, height=altura)      # 72 DPI "do PDF"
        pg.insert_image(pg.rect, filename=str(png))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _tamanhos(pasta: Path, **campos) -> list[tuple[float, float]]:
    projeto = Projeto(caminho_entrada=_livro(pasta), nome="livro", **campos)
    projeto.filtro_padrao, projeto.limpar, projeto.qualidade_dpi = ORIGINAL, False, 150
    projeto.endireitar = False
    projeto = pipeline.analisar_projeto(projeto)
    projeto.caminho_saida = str(pasta / "saida.pdf")
    pipeline.processar(projeto)
    with fitz.open(projeto.caminho_saida) as d:
        return [(p.rect.width * 25.4 / 72, p.rect.height * 25.4 / 72) for p in d]


def test_regressao_so_o_25_todas_as_paginas_do_mesmo_tamanho(tmp_path):
    t = _tamanhos(tmp_path, cortar_pelo_conteudo=True)
    comuns = [t[i] for i in (0, 1, 2, 3, 4, 6, 7)]
    larguras, alturas = [w for w, _ in comuns], [h for _, h in comuns]
    assert max(larguras) - min(larguras) <= 1.0, t
    assert max(alturas) - min(alturas) <= 1.0, t


@pytest.mark.parametrize("jeito", ["ate_a_moldura", "so_o_preto"])
def test_regressao_as_duas_opcoes_sem_tira_e_do_mesmo_tamanho(tmp_path, jeito):
    t = _tamanhos(tmp_path, cortar_pelo_conteudo=True, borda_preta=True, borda_preta_ate=jeito)
    comuns = [t[i] for i in (0, 1, 2, 3, 4, 6, 7)]
    larguras, alturas = [w for w, _ in comuns], [h for _, h in comuns]
    assert max(larguras) - min(larguras) <= 1.0, t
    assert max(alturas) - min(alturas) <= 1.0, t
    # a "página 6" (texto largo e baixo) nunca sai menor que o livro
    assert t[5][1] >= min(alturas) - 1.0, t


def test_regressao_o_tamanho_do_livro_nao_muda_no_meio_da_geracao(monkeypatch):
    """Egenloff 1-14 de verdade, a 300 DPI (21/10/2026): a passada mede a 150
    DPI e cada página era medida de novo a 300 durante a geração; a medida nova
    sobrescrevia a da passada e o tamanho do livro mudava no meio (páginas 3 e
    4 com 382 mm, as outras 360). Uma vez medido, o tamanho de uma página não é
    trocado: o livro não muda depois da passada."""
    from core import corte_pelo_conteudo as cc

    chave = ("arquivo", 1)
    pipeline._TAMANHOS.clear()
    pipeline._TAMANHOS[chave] = (100.0, 380.0)                     # o da passada
    medida = cc.MedidaDoConteudo(1000, 1500, (0.0, 0.0, 900.0, 1300.0), (90.0, 358.0), (0.1, 0.1))
    pipeline._guardar_o_conteudo(chave, pipeline.ConteudoMedido(medida, None, ()))
    assert pipeline._TAMANHOS[chave] == (100.0, 380.0)
