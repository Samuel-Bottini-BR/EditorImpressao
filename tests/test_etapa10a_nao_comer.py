"""Obra de 26/10/2026, etapa 10a: o corte não come a página (testes de reversão
nas páginas de verdade; CLAUDE.md §4.7).

Cada teste: o defeito com a data e as palavras de onde veio, a página do acervo
(somente leitura; copiada para uma pasta temporária), o caminho inteiro do
programa (core.pipeline.analisar_projeto + processar, livro NOVO, filtro
Original) e uma MEDIDA que pega o defeito. Falham no código de antes (11f9ed3)
e passam no novo. Sem o acervo ou sem a DLL do ScanTailor (GitHub), pulam.

Defeitos (Livro de decisões D-104 / D-466, lista única 4.2, 4.10, 1.4; Lista de
bugs de 13/10, Escola 197; ressalvas do G6, D-095):
  - Cursus 3 com "Cortar a beirada da folha vizinha": "o corte da esquerda
    comeu a primeira letra ou duas das linhas do bloco de baixo";
  - folha quase em branco com a borda preta "até a moldura" virava uma tira
    (Siebmacher 74: 2,6 x 8,6 cm; Antiphon 2, guarda manchada);
  - Boécio 2: "um risco preto fino em toda a beirada esquerda";
  - Escola 197: "o corte come os números 1, 2 e 3 dos itens, na margem
    esquerda";
  - Boécio 8: cunhas brancas do giro com o corte até a beirada.
Regra de 21/10: nenhuma página é lombada nem capa.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVROS = {
    "cursus": "Cursus philosophicus. Tomo.2.pdf",
    "siebmacher": "Schön Neues Modell Buch - Johann Siebmacher.pdf",
    "antiphon": "Antiphon_25.pdf",
    "boecio": "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
    "escola": "Na escola de Jesus - Catecismo explicado com imagens..pdf",
}
DPI = 300

pytestmark = pytest.mark.skipif(not ACERVO.is_dir(), reason="sem o acervo (só no PC do Samuel)")


def _precisa_da_dll():
    from core import st_ferramentas

    if st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None:
        pytest.skip("sem a DLL do ScanTailor")


def _uma_pagina(tmp_path: Path, livro: str, numero: int) -> Path:
    destino = tmp_path / f"{livro}_p{numero:03d}.pdf"
    with fitz.open(str(ACERVO / LIVROS[livro])) as doc:
        um = fitz.open()
        um.insert_pdf(doc, from_page=numero - 1, to_page=numero - 1)
        um.save(str(destino))
        um.close()
    return destino


def _pronta(tmp_path: Path, livro: str, numero: int, **campos):
    """(imagem da página do PDF gerado, projeto): livro novo de fábrica com as
    opções `campos`, filtro Original, pelo processar."""
    from core import pipeline
    from core.filtros import ORIGINAL
    from modelos import Projeto

    for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()
    entrada = _uma_pagina(tmp_path, livro, numero)
    saida = tmp_path / "saida.pdf"
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome=entrada.stem)
    for chave, valor in campos.items():
        setattr(projeto, chave, valor)
    projeto = pipeline.analisar_projeto(projeto)
    projeto.filtro_padrao = ORIGINAL
    for pagina in projeto.paginas:
        pagina.filtro = ORIGINAL
    pipeline.processar(projeto)
    with fitz.open(str(saida)) as doc:
        pix = doc[0].get_pixmap(dpi=DPI)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img, projeto


def _folha_cm(livro: str, numero: int) -> tuple[float, float]:
    with fitz.open(str(ACERVO / LIVROS[livro])) as doc:
        r = doc[numero - 1].rect
    return r.width / 72 * 2.54, r.height / 72 * 2.54


def _cm(img) -> tuple[float, float]:
    return img.shape[1] / DPI * 2.54, img.shape[0] / DPI * 2.54


def _letras_na_beirada(img, lado: str, de: float = 0.4, ate: float = 0.95) -> int:
    """Quantos pedaços de tinta do tamanho de letra (1 a 8 mm de altura)
    encostam na beirada `lado` ("esq") da página pronta, entre `de` e `ate` da
    altura: letra cortada pela beirada."""
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, tinta = cv2.threshold(cinza, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h = tinta.shape[0]
    tinta[: int(h * de)] = 0
    tinta[int(h * ate):] = 0
    n, _, caixas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    mm = DPI / 25.4
    conta = 0
    for x, y, w, hh, _a in caixas[1:]:
        if x <= 1 and mm <= hh <= 8 * mm and w < 15 * mm:
            conta += 1
    return conta


def test_reversao_cursus_3_a_sobra_nao_leva_as_primeiras_letras(tmp_path):
    """Lista única 4.2 / C-1 (23/10/2026), Cursus 3 com "Cortar a beirada da
    folha vizinha": "o corte da esquerda comeu a primeira letra ou duas das
    linhas do bloco de baixo". Causa (etapa 10a): o corte da sobra era feito
    colado no texto e o endireitar empurrava o canto do bloco para fora da
    imagem. Medida: letras cortadas pela beirada esquerda na metade de baixo."""
    _precisa_da_dll()
    img, _ = _pronta(tmp_path, "cursus", 3, cortar_sobra=True)
    assert _letras_na_beirada(img, "esq") <= 1


@pytest.mark.parametrize("livro, numero", [("siebmacher", 74), ("antiphon", 2)])
def test_reversao_folha_quase_em_branco_nao_vira_tira(tmp_path, livro, numero):
    """Lista única 4.8/4.10 e 1.4 (23/10/2026): com a borda preta "até a
    moldura", a folha quase em branco virava uma tira (Siebmacher 74: 2,6 x
    8,6 cm, "faixa preta grossa"; Antiphon 2, guarda manchada: só o meio
    para a direita). Medida: a página pronta tem pelo menos 70% da largura e
    da altura da folha escaneada."""
    _precisa_da_dll()
    img, _ = _pronta(tmp_path, livro, numero, borda_preta=True, borda_preta_ate="ate_a_moldura")
    largura, altura = _cm(img)
    folha_l, folha_a = _folha_cm(livro, numero)
    assert largura >= 0.7 * folha_l and altura >= 0.7 * folha_a, (largura, altura, folha_l, folha_a)


def test_reversao_boecio_2_sem_o_fio_preto_na_beirada(tmp_path):
    """Lista única 4.10 / B-6 (23/10/2026), Boécio 2 (guarda com carimbo), de
    fábrica: "Ficou um risco preto fino em toda a beirada esquerda". Medida:
    a coluna da beirada esquerda (mediana do meio da altura) não é escura."""
    img, _ = _pronta(tmp_path, "boecio", 2)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h = cinza.shape[0]
    papel = float(np.percentile(cinza[h // 4: 3 * h // 4], 60))
    beirada = np.median(cinza[h // 4: 3 * h // 4, :3], axis=0)
    assert float(beirada.min()) > 0.65 * papel, (beirada, papel)


def test_reversao_escola_197_os_numeros_da_margem_ficam(tmp_path):
    """Lista de bugs, 13/10/2026 (verificador do corte): "Escola 197: na ordem
    nova o corte come os números 1, 2 e 3 dos itens, na margem esquerda".
    Medida: pedaços de tinta do tamanho de letra na faixa esquerda da página
    pronta, antes do travessão de cada item (os três números)."""
    img, _ = _pronta(tmp_path, "escola", 197)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, tinta = cv2.threshold(cinza, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    mm = DPI / 25.4
    faixa = tinta[:, : int(4 * mm)]                  # os 4 mm da esquerda
    n, _, caixas, _ = cv2.connectedComponentsWithStats(faixa, connectivity=8)
    numeros = [c for c in caixas[1:] if 2 * mm <= c[3] <= 6 * mm]
    assert len(numeros) >= 3, len(numeros)


def test_reversao_boecio_8_sem_cunha_branca_na_beirada(tmp_path):
    """Ressalva do G6 (12/10/2026, D-095): "cunhas brancas com corte até a
    beirada" (Boécio 8). A página é girada 1,1 grau e o corte vai até a
    beirada; a cunha do giro saía branca puro ao lado do papel amarelado.
    Medida: pontos brancos puros (os três canais >= 254) na faixa de 2 mm das
    beiradas da esquerda e da direita."""
    img, _ = _pronta(tmp_path, "boecio", 8)
    mm = int(round(2 * DPI / 25.4))
    faixas = np.concatenate([img[:, :mm].reshape(-1, 3), img[:, -mm:].reshape(-1, 3)])
    brancos = float((faixas.min(axis=1) >= 254).mean())
    assert brancos < 0.005, brancos


def test_reversao_corte_alargado_nunca_fica_menor_que_o_corte_de_agora(monkeypatch):
    """Lista única 1.4 (23/10/2026), Antiphon 2: "usar o corte alargado" deixou a
    página MENOR ("a página virou uma tira estreita e perdeu a metade
    esquerda"). O alargado sempre contém o corte que a página tem agora."""
    from core import corte_pelo_conteudo as cc
    from core import pipeline
    from modelos import ConfigFolha, ConfigPagina, Projeto

    medida = cc.MedidaDoConteudo(1000, 1000, (600, 100, 900, 900), (25.4, 67.7), (0.0847, 0.0847))
    medido = pipeline.ConteudoMedido(medida, None, (((580.0, 400.0, 620.0, 450.0), True),))
    monkeypatch.setattr(pipeline, "_caixa_do_livro", lambda f, p, pr: (medido, (600, 100, 900, 900), None))
    monkeypatch.setattr(pipeline, "_geometria_guardada", lambda f, p, pr: ((0.1, 0.05, 0.85, 0.9), 0.0))
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=0)]
    pagina = ConfigPagina(indice=0, folha=0)
    x, y, w, h = pipeline.corte_alargado(projeto, pagina)
    assert x <= 0.1 + 1e-9 and y <= 0.05 + 1e-9
    assert x + w >= 0.95 - 1e-9 and y + h >= 0.95 - 1e-9
