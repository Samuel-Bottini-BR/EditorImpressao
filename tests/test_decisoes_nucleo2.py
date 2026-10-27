"""Obra de 26/10/2026, etapa 9d: consertos de núcleo que sobraram (provas das
decisões e testes de reversão; CLAUDE.md §4.7 e §11).

Cada teste diz a decisão ou o defeito (com a fonte) e uma MEDIDA que o pega.
Os de reversão falham no código de antes (`ad8df2b`, worktree
`obra-etapa9d-antes`) e passam no novo; a conta de cada um está no
`relatorios/obra-etapa9d/ONDE-PAREI.md`.

Dois tipos, como na etapa 10b:
  - páginas de verdade do acervo, pelo caminho inteiro do programa (livro NOVO
    de fábrica: core.pipeline.analisar_projeto e o mesmo corpo do processar,
    core.pipeline._pagina_pronta; regra de 21/10): só no PC do Samuel (o acervo
    fica fora do git; sem ele, pulam);
  - páginas e livros sintéticos, que rodam em qualquer lugar (GitHub).
Regra de 21/10: nenhuma página é lombada nem capa de couro.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVROS = {
    "antiphon": "Antiphon_25.pdf",
    "horas": "Livro de Horas - Luís XIV.pdf",
    "ljs47": "ljs47.pdf",
    "palatino": "Giovambattista Palatino cittadino romano.pdf",
    "righetti": "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf",
    "escola": "Na escola de Jesus - Catecismo explicado com imagens..pdf",
    "boecio": "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
}


# --- ajudantes ----------------------------------------------------------------

def _precisa(caminho: Path) -> None:
    if not caminho.exists():
        pytest.skip(f"sem {caminho} (só no PC do Samuel)")


def _pdf_sintetico(caminho: Path, paginas: list[np.ndarray], dpi: float = 150.0) -> Path:
    """Um PDF com uma imagem por página (cinza ou BGR), como um livro escaneado."""
    doc = fitz.open()
    for img in paginas:
        altura, largura = img.shape[:2]
        pagina = doc.new_page(width=largura / dpi * 72.0, height=altura / dpi * 72.0)
        ok, png = cv2.imencode(".png", img)
        assert ok
        pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


# =============================================================================
# Item 5 - o aviso de margem da impressão com número negativo
# =============================================================================

def test_reversao_aviso_de_margem_nunca_diz_numero_negativo(tmp_path):
    """Ressalva da etapa 10a (27/10/2026, "Bugs para a Lista de bugs"): "aviso
    de margem da impressão com número negativo ('em cima -2,2 cm (precisa de
    1,3 cm)') quando a página passa da folha: confuso" (core/impressao.py,
    _avisos_de_margem). Decisão do aviso (g11, 14/10): "o programa precisa
    avisar quando o corte deixar qualquer margem abaixo de 1 cm".

    Livreto em A4 com as duas páginas a 140% (o mesmo caso da 10a, numa página
    sintética com tinta até perto da beirada): o aviso de margem continua, sem
    nenhum número negativo, e diz que o impresso passa da beirada; o aviso
    "CORTADO" (D-017) continua dizendo quanto."""
    from core import impressao

    pagina = np.full((1500, 1000), 255, np.uint8)
    pagina[60:1440, 50:950] = 30                       # tinta quase até a beirada
    livro = _pdf_sintetico(tmp_path / "livro.pdf", [pagina] * 4)
    opcoes = impressao.OpcoesDeImpressao()
    opcoes.escala_esquerda = opcoes.escala_direita = 140.0
    r = impressao.montar_para_impressao(livro, tmp_path / "imprimir.pdf", opcoes)
    margem = [a.texto for a in r.avisos if "margem ficou abaixo" in a.texto]
    assert margem, [a.texto for a in r.avisos]
    textos = " ".join(margem)
    assert not re.search(r"-\s?\d", textos.replace(" - ", " ")), textos
    assert "nenhuma (o impresso passa da beirada do papel)" in textos, textos
    assert any("CORTADO" in a.texto for a in r.avisos)


def test_aviso_de_margem_pequena_continua_com_o_numero(tmp_path):
    """Guarda: a margem pequena mas positiva continua dita em cm (a 115%, o
    impresso não passa do papel, mas fica a menos de 1,3 cm da beirada)."""
    from core import impressao

    pagina = np.full((1500, 1000), 255, np.uint8)
    pagina[60:1440, 50:950] = 30
    livro = _pdf_sintetico(tmp_path / "livro.pdf", [pagina] * 4)
    opcoes = impressao.OpcoesDeImpressao()
    opcoes.escala_esquerda = opcoes.escala_direita = 115.0
    r = impressao.montar_para_impressao(livro, tmp_path / "imprimir.pdf", opcoes)
    textos = " ".join(a.texto for a in r.avisos if "margem ficou abaixo" in a.texto)
    assert re.search(r"\d,\d cm \(precisa de", textos), textos
    assert "nenhuma" not in textos, textos


# =============================================================================
# Item 4 - "Deixar a folha em branco" na página "Tirar o fundo" sem o fundo
# =============================================================================

@pytest.fixture
def _sem_figuras(monkeypatch):
    """O detector de figuras do core/camadas.py não acha nada (rápido, sem o
    modelo), como em tests/test_tirar_fundo_no_programa.py."""
    from core import camadas
    from tests.test_camadas import sem_figuras

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)


def _livro_sem_o_fundo(tmp_path, detectar: bool):
    """Livro de uma página com camadas (como os do Internet Archive), no
    filtro "Tirar o fundo", e a página de verdade sem o fundo (core/camadas)."""
    from core import pipeline
    from core.filtros import TIRAR_FUNDO
    from modelos import Projeto
    from tests.test_camadas import pdf_com_camadas

    doc = pdf_com_camadas()
    caminho = tmp_path / "camadas.pdf"
    doc.save(str(caminho))
    doc.close()
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste",
                      caminho_saida=str(tmp_path / "saida.pdf"))
    projeto.filtro_padrao = TIRAR_FUNDO
    projeto.detectar_regioes = detectar
    projeto.cortar_bordas = False
    projeto.endireitar = False
    projeto.montar_cadernos = False
    projeto.qualidade_dpi = 100
    projeto = pipeline.analisar_projeto(projeto)
    assert projeto.paginas[0].filtro == TIRAR_FUNDO
    return projeto


def _marcar_papel(pagina, x0, y0, x1, y1, origem=None):
    from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                               origem=origem or MAO))
    pagina.guardar_selecao(selecao)


def _pagina_do_pdf(caminho) -> np.ndarray:
    with fitz.open(str(caminho)) as doc:
        assert len(doc) == 1, "a página tem de continuar no livro (mesmo lugar)"
        pix = doc[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY)
        return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].copy()


@pytest.mark.parametrize("detectar", [True, False], ids=["procurar_gravura", "sem_procurar"])
def test_reversao_folha_em_branco_no_tirar_o_fundo_sem_o_fundo_sai_branca(tmp_path, _sem_figuras,
                                                                          detectar):
    """Bug achado na etapa 9c (27/10/2026, "Bugs para a Lista de bugs"):
    "'Deixar a folha em branco' numa página 'Tirar o fundo' de que o fundo FOI
    tirado: essa página vai por pipeline._pedacos_na_pagina_sem_fundo, que não
    passa pelo conserto do item 1; a tinta continua." Decisão D-027 (30/09):
    "essa é uma página que eu poderia simplesmente escolher a opção para virar
    uma folha branca". Medida: no PDF, a página inteira sai branca (antes, as
    letras pretas da camada de cima continuavam) - e a prévia igual."""
    from core import pipeline

    projeto = _livro_sem_o_fundo(tmp_path, detectar)
    pipeline.processar(projeto)
    antes = _pagina_do_pdf(projeto.caminho_saida)
    assert antes.min() < 80, "o livro de teste devia ter letra preta sem o fundo"
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, 1.0)      # "Deixar a folha em branco"
    pipeline.processar(projeto)
    img = _pagina_do_pdf(projeto.caminho_saida)
    assert img.min() >= 250, f"a folha devia sair toda branca no PDF (mínimo {img.min()})"
    doc = fitz.open(projeto.caminho_entrada)
    try:
        previa, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=100)
    finally:
        doc.close()
    assert previa.min() >= 250, "a prévia também (tela = PDF, D-473)"


def test_pintar_de_branco_no_tirar_o_fundo_so_na_area(tmp_path, _sem_figuras):
    """D-227 ("pintar de branco" → no PDF sai branca) na página sem o fundo:
    só a área marcada vai a branco; a letra de fora continua."""
    from core import pipeline

    projeto = _livro_sem_o_fundo(tmp_path, True)
    pipeline.processar(projeto)
    antes = _pagina_do_pdf(projeto.caminho_saida)
    altura, largura = antes.shape
    tinta = np.argwhere(antes < 80)
    meio = float(np.median(tinta[:, 0])) / altura          # onde está a letra (altura)
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, meio)  # a metade de cima da tinta
    pipeline.processar(projeto)
    img = _pagina_do_pdf(projeto.caminho_saida)
    corte = int(meio * altura)
    assert img[:max(1, corte - 2)].min() >= 250, "a área pintada não saiu branca"
    assert (img[corte + 2:] < 80).sum() > 0.3 * (antes[corte + 2:] < 80).sum(), \
        "a letra fora da área sumiu"


def test_papel_da_maquina_nao_branqueia_a_pagina_sem_o_fundo(tmp_path, _sem_figuras):
    """Guarda (D-134): o papel que a MÁQUINA marcou não muda a página sem o
    fundo; só o marcado à mão."""
    from core import pipeline
    from core.selecao import AUTOMATICO

    projeto = _livro_sem_o_fundo(tmp_path, True)
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, 1.0, origem=AUTOMATICO)
    pipeline.processar(projeto)
    assert _pagina_do_pdf(projeto.caminho_saida).min() < 80


# =============================================================================
# Item 3 - D-528: as marcações da folha inteira vão para a metade em que estão
# =============================================================================

def _folha_dupla() -> np.ndarray:
    """Uma folha de livro aberto (duas páginas, 150 DPI), papel branco, com
    três quadrados pretos: um na página da esquerda (A), dois na da direita (B,
    que vai ser "pintado de branco", e C, que fica)."""
    img = np.full((1400, 2000), 245, np.uint8)
    img[:, 995:1005] = 200                                # a lombada
    img[300:500, 300:500] = 10                            # A (esquerda)
    img[300:500, 1500:1700] = 10                          # B (direita, marcado)
    img[900:1100, 1300:1500] = 10                         # C (direita, não marcado)
    for y in range(650, 820, 40):                         # "linhas de texto"
        img[y:y + 12, 150:850] = 30
        img[y:y + 12, 1150:1850] = 30
    return img


def _livro_da_folha_dupla(tmp_path):
    """Livro novo de uma folha, sem dividir (livro novo não divide: D-080), sem
    corte nem endireitar (o papel fica onde o teste espera), em Original."""
    from core import pipeline
    from core.filtros import ORIGINAL
    from modelos import Projeto

    caminho = _pdf_sintetico(tmp_path / "dupla.pdf", [_folha_dupla()])
    projeto = Projeto(caminho_entrada=str(caminho), nome="dupla",
                      caminho_saida=str(tmp_path / "saida.pdf"))
    projeto.dividir_folhas = False
    projeto.cortar_bordas = False
    projeto.endireitar = False
    projeto.detectar_regioes = False
    projeto.montar_cadernos = False
    projeto.filtro_padrao = ORIGINAL
    projeto.qualidade_dpi = 150
    projeto = pipeline.analisar_projeto(projeto)
    assert len(projeto.paginas) == 1 and projeto.paginas[0].metade == "inteira"
    return projeto


def _desenhar(projeto, pagina, dpi=110):
    """A prévia da página (como a tela): anota a geometria das zonas."""
    from core import pipeline

    doc = fitz.open(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
    finally:
        doc.close()
    return img


def _pintar_de_branco_na_inteira(pagina, caixa, origem=None):
    """Uma marcação "pintar de branco" (papel à mão) na página, em fração dela,
    como a tela grava (core.editar_zonas.pintada_de_branco)."""
    from core import etapas
    from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

    x0, y0, x1, y1 = caixa
    selecao = Selecao.de_lista(pagina.selecao or [])
    selecao.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                               origem=origem or MAO))
    pagina.guardar_selecao(selecao)
    etapas.marcar_mexida_a_mao(pagina, etapas.MARCAR)


def _dividir_a_mao(projeto, posicao=0.5):
    """O que "dividir esta" faz (ui/tela_conferir._dividir_esta): UMA ação do
    desfazer com os campos de core/dividir_a_mao.campos_para_dividir."""
    from core import dividir_a_mao, etapas
    from historico_acoes import aplicar, montar_acao

    campos = dividir_a_mao.campos_para_dividir(projeto, 0, posicao=posicao)
    acao = montar_acao(projeto, "dividir", "folha", [0], campos, "dividir esta")
    aplicar(projeto, acao, acao.depois)
    etapas.marcar_mexida_a_mao(projeto.folhas[0], etapas.DIVIDIR)
    return acao


def _paginas_do_pdf_cinza(caminho) -> list[np.ndarray]:
    saida = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=150, colorspace=fitz.csGRAY)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.stride)[:, :pix.width].copy())
    return saida


def _escuro(img: np.ndarray, x0, y0, x1, y1) -> float:
    """Fração de pontos escuros (< 100) na caixa (fração da página)."""
    a, larg = img.shape
    trecho = img[int(y0 * a):int(y1 * a), int(x0 * larg):int(x1 * larg)]
    return float((trecho < 100).mean())


def test_reversao_d528_marcacao_a_mao_vai_para_a_metade_certa_ao_dividir_a_mao(tmp_path):
    """D-528 (escolha da gerente, 27/10/2026, apoiada na pergunta 1 da etapa
    4): "Ao dividir uma folha pela primeira vez, as marcações feitas na folha
    inteira vão para a metade em que estão (hoje se perdem, como no
    Automático)." Prova do Livro: "Marcar uma gravura na metade direita da
    folha inteira, dividir → a marcação aparece na página da direita, no lugar
    certo".

    Folha de livro aberto, inteira; "pintar de branco" no quadrado B (metade
    direita); "dividir esta" à mão. Medida no PDF: na página da DIREITA o
    quadrado B sai branco (era preto: no código antigo a marcação se perdia) e
    o C, fora da marcação, continua preto; a página da ESQUERDA não recebe
    marcação nenhuma e o quadrado A continua preto."""
    from core import pipeline

    projeto = _livro_da_folha_dupla(tmp_path)
    inteira = projeto.paginas[0]
    _desenhar(projeto, inteira)                          # a página foi vista na tela
    _pintar_de_branco_na_inteira(inteira, (0.73, 0.19, 0.87, 0.38))     # B
    _dividir_a_mao(projeto, 0.5)
    esquerda, direita = projeto.paginas
    assert (esquerda.metade, direita.metade) == ("esquerda", "direita")
    assert not esquerda.selecao, "a marcação da direita foi parar na esquerda"
    assert direita.selecao, "a marcação se perdeu ao dividir"
    pipeline.processar(projeto)
    pag_esq, pag_dir = _paginas_do_pdf_cinza(projeto.caminho_saida)
    # B na página da direita: x 1500..1700 da folha -> 0,5..0,7 da página
    assert _escuro(pag_dir, 0.52, 0.23, 0.68, 0.34) < 0.01, "o quadrado B devia sair branco"
    assert _escuro(pag_dir, 0.32, 0.66, 0.48, 0.77) > 0.9, "o quadrado C (fora) devia ficar"
    assert _escuro(pag_esq, 0.32, 0.23, 0.48, 0.34) > 0.9, "o quadrado A (esquerda) devia ficar"


def test_d528_a_marcacao_fica_no_lugar_na_previa_da_metade(tmp_path):
    """A prévia da página da direita (a que a tela mostra) recebe a marcação
    levada para a metade: o retângulo fica sobre o quadrado B (fração da
    página da direita ~0,46..0,74 × ~0,19..0,38), não no lugar que ele tinha
    na página inteira (0,73..0,87)."""
    projeto = _livro_da_folha_dupla(tmp_path)
    inteira = projeto.paginas[0]
    _desenhar(projeto, inteira)
    _pintar_de_branco_na_inteira(inteira, (0.73, 0.19, 0.87, 0.38))
    _dividir_a_mao(projeto, 0.5)
    direita = projeto.paginas[1]
    _desenhar(projeto, direita)                          # a tela mostra a página
    (x0, y0), (x1, y1) = [tuple(p) for p in direita.selecao[0]["pontos"]]
    assert abs(x0 - 0.46) < 0.02 and abs(x1 - 0.74) < 0.02, (x0, x1)
    assert abs(y0 - 0.19) < 0.02 and abs(y1 - 0.38) < 0.02, (y0, y1)


def test_d528_folha_inteira_em_branco_vai_para_as_duas_e_a_da_maquina_nao_passa(tmp_path):
    """"Deixar a folha em branco" na folha inteira vale nas duas metades; a
    marcação que a MÁQUINA achou na folha inteira não passa (a metade procura
    a dela de novo: marcação provisória)."""
    from core.selecao import AUTOMATICO

    projeto = _livro_da_folha_dupla(tmp_path)
    inteira = projeto.paginas[0]
    _desenhar(projeto, inteira)
    _pintar_de_branco_na_inteira(inteira, (0.0, 0.0, 1.0, 1.0))
    _pintar_de_branco_na_inteira(inteira, (0.1, 0.1, 0.2, 0.2), origem=AUTOMATICO)
    _dividir_a_mao(projeto, 0.5)
    for pagina in projeto.paginas:
        assert len(pagina.selecao) == 1, pagina.selecao
        assert [list(p) for p in pagina.selecao[0]["pontos"]] == [[0.0, 0.0], [1.0, 1.0]]
        assert pagina.marcacao_provisoria


def test_d528_sem_a_geometria_anotada_a_conta_aproximada_leva_para_a_metade():
    """Página nunca desenhada (sem geometria anotada): a zona vai para a metade
    pelo centro e a fração é levada para a metade (x da folha girada)."""
    from core import zonas_na_folha

    zona = {"tipo": "papel", "forma": "retangulo", "pontos": [[0.7, 0.2], [0.9, 0.4]],
            "origem": "mao"}
    esq, dir_, geo = zonas_na_folha.repartir_nas_metades([zona], None, 0.5)
    assert esq == [] and geo is None
    (x0, _), (x1, _) = dir_[0]["pontos"]
    assert abs(x0 - 0.4) < 1e-9 and abs(x1 - 0.8) < 1e-9


def test_reversao_d528_no_automatico_tambem(tmp_path):
    """D-528 vale "à mão ou no Automático" (pedido da gerente): o Automático
    com "Dividir" na folha inteira marcada leva a marcação à mão para a página
    da direita."""
    from core import automatico as A
    from core import pipeline, st_ferramentas

    if st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None:
        pytest.skip("sem a DLL do ScanTailor")
    projeto = _livro_da_folha_dupla(tmp_path)
    inteira = projeto.paginas[0]
    _desenhar(projeto, inteira)
    _pintar_de_branco_na_inteira(inteira, (0.73, 0.19, 0.87, 0.38))
    A.rodar(projeto, A.Pedido(etapas=[A.DIVIDIR], pular_mexidas=False))
    assert [p.metade for p in projeto.paginas] == ["esquerda", "direita"]
    esquerda, direita = projeto.paginas
    assert not esquerda.selecao and direita.selecao
    pipeline.processar(projeto)
    _pag_esq, pag_dir = _paginas_do_pdf_cinza(projeto.caminho_saida)
    corte = projeto.folhas[0].posicao_corte
    # B (x 0,75..0,85 da folha) na página da direita
    bx0, bx1 = (0.75 - corte) / (1 - corte), (0.85 - corte) / (1 - corte)
    assert _escuro(pag_dir, bx0 + 0.02, 0.23, bx1 - 0.02, 0.34) < 0.01
