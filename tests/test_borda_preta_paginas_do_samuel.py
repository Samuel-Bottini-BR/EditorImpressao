"""A borda preta (item 2.13) nas páginas que o Samuel escolheu como alvo, com
a MEDIDA em mm de preto que sobra em cada beirada (pedido da gerente, 21/10).

Palavras dele (20/10/2026): Antiphon 260 "tem que cortar a faixa inteira.";
Antiphon 88 "Tem que cortar em cima e embaixo e dos lados ainda tem um fio
preto."; Camões 104 "É para sumir totalmente."; Cursus 3 "tem que ficar
rente a folha de papel, não pode ter preto ali."; Matemática 32 "ainda estou
vendo a faixa preta.". Pesel 21: tem de continuar inteiro (conserto do corte,
aprovado em 20/10).

Regra dele para os testes (20/10): "deveriamos ter indireitado a folha antes
de cortar [...]": a página passa pelo programa inteiro (analisar_projeto e
renderizar_pagina: dividir, endireitar e cortar, livro novo), não a crua.

A medida é a do verificador do corte (relatorios/conserto-corte-g6/scripts/
medir.py, _beirada e _por_lado): faixa mais escura que 60% do papel encostada
na beirada, em mm, percentil 90 ao longo de cada lado. Precisa das páginas do
estudo (fora do git): sem elas, pula (no GitHub, pula).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

RAIZ = Path(__file__).resolve().parents[1]
PAGINAS = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
MEDIDA = RAIZ / "relatorios" / "conserto-corte-g6" / "scripts"
DPI = 150

pytestmark = pytest.mark.skipif(not PAGINAS.is_dir() or not (MEDIDA / "medir.py").is_file(),
                                reason="sem as páginas do estudo (fora do git)")


def _pronta(pid: str, **campos):
    from core import pipeline as P
    from core import st_ferramentas
    from core.filtros import ORIGINAL
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    if st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None:
        pytest.skip("sem a DLL do ScanTailor")
    projeto = Projeto(caminho_entrada=str(PAGINAS / f"{pid}.pdf"), nome=pid, **campos)
    projeto.filtro_padrao, projeto.limpar, projeto.qualidade_dpi = ORIGINAL, False, DPI
    projeto = P.analisar_projeto(projeto)
    for g in (P._GEOMETRIAS, P._CONTEUDOS, P._TAMANHOS):
        g.clear()
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        final, _ = P.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=DPI)
    finally:
        doc.close()
    return final


def _preto_mm(final) -> dict:
    sys.path.insert(0, str(MEDIDA))
    import medir as verif

    cinza = verif._cinza(final)
    _fr, encosta, f = verif._beirada(cinza < 0.6 * verif._nivel_do_papel(cinza))
    verif.DPI = DPI
    return {k: v["mm"] for k, v in verif._por_lado(encosta, f).items()}


TOLERANCIA_MM = 1.0     # arredondamento a 150 DPI (um ponto = 0,17 mm) e papel rasgado


@pytest.mark.parametrize("pid", ["antiphon_p260", "antiphon_p088", "camoes_p104"])
def test_ate_a_moldura_nao_sobra_preto(pid):
    """"Até a moldura" (o que vem escolhido): nenhuma faixa preta nas quatro
    beiradas."""
    lados = _preto_mm(_pronta(pid, borda_preta=True, borda_preta_ate="ate_a_moldura"))
    assert max(lados.values()) <= TOLERANCIA_MM, lados


def _faixa_escura_na_beirada(final, lado: str, de: float, ate: float, mm: float = 2.0) -> float:
    """Fração escura (mais que 55% abaixo do papel) numa tira de `mm` junto da
    beirada `lado`, só entre as frações `de` e `ate` do comprimento do lado."""
    import cv2
    import numpy as np

    cinza = final if final.ndim == 2 else cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
    a, l = cinza.shape
    papel = float(np.percentile(cinza[a // 4:3 * a // 4, l // 4:3 * l // 4], 90))
    n = max(1, int(round(mm * DPI / 25.4)))
    faixas = {"dir": cinza[int(a * de):int(a * ate), l - n:], "pe": cinza[a - n:, int(l * de):int(l * ate)],
              "esq": cinza[int(a * de):int(a * ate), :n], "topo": cinza[:n, int(l * de):int(l * ate)]}
    return float((faixas[lado] < 0.45 * papel).mean())


def test_matematica_32_ate_a_moldura_sem_a_faixa_do_scanner():
    """Matemática 32: a faixa preta do scanner (embaixo e à direita) some. A
    medida do verificador não serve aqui: o bloco escuro impresso do
    "Capítulo 2" encosta na beirada quando o corte é rente ao impresso; por
    isso a tira é medida embaixo e no lado, abaixo do título."""
    final = _pronta("matematica_p032", borda_preta=True, borda_preta_ate="ate_a_moldura")
    for lado in ("pe", "dir", "esq"):
        assert _faixa_escura_na_beirada(final, lado, 0.25, 1.0) <= 0.05, lado


def test_cursus_3_ate_a_moldura_rente_sem_o_preto_de_fora():
    """Cursus 3: não sobra preto de fora do papel à direita nem embaixo nem em
    cima. RESSALVA (20/10): à esquerda sobra um traço preto vertical que está
    DENTRO do papel, ao lado do título (o ScanTailor o conta como conteúdo);
    a medida dá ~3 mm desse lado, e este teste prende que não piore."""
    lados = _preto_mm(_pronta("cursus_p003", borda_preta=True, borda_preta_ate="ate_a_moldura"))
    assert max(lados["dir"], lados["pe"], lados["topo"]) <= TOLERANCIA_MM, lados
    assert lados["esq"] <= 3.5, lados


@pytest.mark.parametrize("pid", ["antiphon_p260", "antiphon_p088", "camoes_p104", "matematica_p032"])
def test_so_o_preto_tira_a_faixa_do_meio_dos_lados(pid):
    """"Só o preto": no meio dos lados não sobra faixa (percentil 90).
    As pontas dos cantos de folha torta ficam, como a pergunta dizia."""
    lados = _preto_mm(_pronta(pid, borda_preta=True, borda_preta_ate="so_o_preto"))
    assert max(lados.values()) <= TOLERANCIA_MM, lados


def test_pesel_21_so_o_preto_continua_inteiro():
    """Pesel 21 (cartão marrom escuro): "só o preto" sai igual ao de hoje (o
    cartão não é fundo de scanner: não é cinza). Reversão do defeito achado em
    20/10: antes da regra da cor neutra, cortava o título e o número 3
    (157 x 241 mm -> 138 x 223 mm)."""
    hoje = _pronta("pesel_p021")
    so = _pronta("pesel_p021", borda_preta=True, borda_preta_ate="so_o_preto")
    assert abs(so.shape[0] - hoje.shape[0]) <= 3 and abs(so.shape[1] - hoje.shape[1]) <= 3


# ------------------------------------------- item 2.14: pintar de branco

@pytest.mark.parametrize("pid", ["antiphon_p260", "antiphon_p088", "camoes_p104", "cursus_p003",
                                 "egenloff_p047"])
def test_2_14_ate_a_moldura_pintando_nao_sobra_preto_e_o_tamanho_fica(pid):
    """Item 2.14 (rodada 5, rv5-pag-egenloff-047: "O Kaique escolhe por
    livro" entre cortar fora e pintar de branco). Pintando, a página fica do
    tamanho de hoje e não sobra faixa preta em beirada nenhuma (no Egenloff
    47, a tarja da biblioteca também some)."""
    hoje = _pronta(pid)
    pintada = _pronta(pid, borda_preta=True, borda_preta_ate="ate_a_moldura", borda_preta_fazer="pintar")
    assert pintada.shape == hoje.shape
    lados = _preto_mm(pintada)
    assert max(lados.values()) <= TOLERANCIA_MM, lados


def test_2_14_matematica_32_pintando_a_faixa_some():
    hoje = _pronta("matematica_p032")
    pintada = _pronta("matematica_p032", borda_preta=True, borda_preta_ate="so_o_preto",
                      borda_preta_fazer="pintar")
    assert pintada.shape == hoje.shape
    assert _faixa_escura_na_beirada(hoje, "pe", 0.25, 1.0) > 0.5          # hoje a faixa está lá
    assert _faixa_escura_na_beirada(pintada, "pe", 0.25, 1.0) <= 0.05


def test_2_14_pesel_21_so_o_preto_pintando_fica_igual():
    """Pesel 21: "só o preto" pintando não toca no cartão (não é cinza)."""
    import numpy as np

    hoje = _pronta("pesel_p021")
    pintada = _pronta("pesel_p021", borda_preta=True, borda_preta_ate="so_o_preto", borda_preta_fazer="pintar")
    assert pintada.shape == hoje.shape
    assert float(np.abs(pintada.astype(int) - hoje.astype(int)).mean()) < 1.0
