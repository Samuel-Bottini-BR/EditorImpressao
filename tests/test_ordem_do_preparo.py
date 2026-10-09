"""A ordem do preparo: endireitar antes de cortar no livro novo (item 2.2, G6).

Decisão do Samuel (09/10/2026, página de escolhas, pergunta
g6-endireitar-antes): "Endireitar antes de cortar (como o ScanTailor): pode
começar?" -> "Pode começar". O que ele leu: "Livro começado antes desta
mudança continua saindo exatamente igual, ponto por ponto; só os livros
novos mudam."

Testes de máquina (rodam no Linux da nuvem e no Windows do GitHub; nada aqui
depende das DLLs do ScanTailor, do gabarito nem dos modelos - a conta do
ScanTailor, quando entra, é trocada por um número fixo):
- o campo: livro novo "endireitar_antes"; projeto sem o campo "cortar_antes";
  vai e volta do arquivo; valor estranho = a de sempre;
- PROJETO ANTIGO IDÊNTICO PONTO POR PONTO: uma cópia congelada da conta de
  antes do G6 (_preparo_de_antes, abaixo) contra o programa, em vários casos
  (corte e ângulo automáticos e à mão, folha dividida, giro de 90, sobra,
  endireitar ou cortar desligados); a imagem, a geometria das zonas e a
  imagem da aba Bordas;
- ordem nova: o ângulo é o mesmo da ordem antiga; o corte é achado na página
  reta e deixa pelo menos 1 mm de papel em volta da tinta nos quatro lados
  (o bug dos cantos); o corte à mão está em fração da página reta; a aba
  Bordas mostra a página reta; a análise (aviso C1) mede o mesmo ângulo;
- zonas (core/zonas_na_folha): a conta com a ordem como dado acerta o pixel
  de verdade nas duas ordens; geometria sem a chave "ordem" continua a de
  sempre; zonas de projeto antigo não andam;
- a janela: livro novo nasce "endireitar_antes", a ordem volta ao reabrir, e
  projeto sem o campo reabre "cortar_antes".

- g6-retangulo (Samuel, 09/10/2026, "Fica no mesmo lugar da página (como no
  ScanTailor)"): mudar o ângulo depois não mexe no corte à mão (de fábrica);
  a outra opção, "acompanha o texto", está pronta sem tela
  (pipeline.recorte_depois_de_mudar_o_angulo) e é conferida no pixel.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import endireitar_scantailor as es  # noqa: E402
from core import ordem_do_preparo as op  # noqa: E402
from core import pipeline  # noqa: E402
from core import zonas_na_folha as zf  # noqa: E402
from core.endireitar import ANGULO_MINIMO, detectar_angulo, rotacionar  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from core.recortar import (alargar_para_o_giro, aplicar_recorte, detectar_bordas,  # noqa: E402
                           fatiar)
from modelos import (METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigFolha,  # noqa: E402
                     ConfigPagina, Projeto)

DPI = 300


# ------------------------------------------------------------------ livro de mentira

def _pdf(pasta: Path, nome: str, graus: float, duas: bool = False, ponto=None) -> str:
    """Uma folha de "texto" (A5, ou duas A5 lado a lado) girada `graus`
    (sentido do OpenCV), embutida a 200 DPI. `ponto` (u, v): um quadradinho
    vermelho nesse lugar da folha (fração), para achar na página preparada."""
    largura, altura = (2330 if duas else 1165), 1654
    img = np.full((altura, largura, 3), 255, np.uint8)
    blocos = [(70, largura // 2 - 60), (largura // 2 + 60, largura - 70)] if duas else [(130, largura - 170)]
    for x0, x1 in blocos:
        for y in range(180, altura - 180, 34):
            for x in range(x0, x1 - 40, 52):
                cv2.rectangle(img, (x, y), (x + 38, y + 14), (0, 0, 0), -1)
    m = cv2.getRotationMatrix2D((largura / 2, altura / 2), graus, 1.0)
    img = cv2.warpAffine(img, m, (largura, altura), borderValue=(255, 255, 255))
    if ponto is not None:
        cx, cy = int(ponto[0] * largura), int(ponto[1] * altura)
        img[cy - 4:cy + 5, cx - 4:cx + 5] = (0, 0, 255)            # vermelho (BGR)
    png = pasta / f"{nome}.png"
    cv2.imwrite(str(png), img)
    caminho = pasta / f"{nome}.pdf"
    doc = fitz.open()
    pagina = doc.new_page(width=largura * 72 / 200, height=altura * 72 / 200)
    pagina.insert_image(pagina.rect, filename=str(png))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _antigo(caminho: str, **campos) -> Projeto:
    """Um projeto como o programa de antes do G6 grava: sem o campo da ordem."""
    dados = Projeto(caminho_entrada=caminho, qualidade_dpi=DPI, **campos).para_dicionario()
    dados.pop("ordem_do_preparo")
    return Projeto.de_dicionario(dados)


def _novo(caminho: str, **campos) -> Projeto:
    return Projeto(caminho_entrada=caminho, qualidade_dpi=DPI, **campos)


def _com_folha(projeto: Projeto, folha: dict, pagina: dict):
    f = ConfigFolha(indice=0, **folha)
    p = ConfigPagina(indice=0, folha=0, **pagina)
    projeto.folhas, projeto.paginas = [f], [p]
    return f, p


def _desenhar(caminho: str, dpi: int = DPI) -> np.ndarray:
    doc = abrir_pdf(caminho)
    try:
        return pagina_para_array(doc, 0, dpi=dpi)
    finally:
        doc.close()


@pytest.fixture(autouse=True)
def _sem_geometrias_guardadas():
    pipeline._GEOMETRIAS.clear()
    pipeline._ANGULOS_MEDIDOS.clear()
    yield
    pipeline._GEOMETRIAS.clear()
    pipeline._ANGULOS_MEDIDOS.clear()


@pytest.fixture
def scantailor_fixo(monkeypatch):
    """A conta do ScanTailor trocada por um ângulo fixo (-1,3°): o teste não
    depende da DLL (que só existe no Windows) e dá o mesmo nos dois."""
    monkeypatch.setattr(es, "medir_na_pagina",
                        lambda *_a, **_k: es.Medida(-1.3, -1.3, 5.0, True, 300.0))


# ------------------------------------------------------------------ o campo

def test_livro_novo_endireita_antes():
    assert Projeto(caminho_entrada="x.pdf").ordem_do_preparo == op.ENDIREITAR_ANTES
    assert op.ORDEM_DO_LIVRO_NOVO == op.ENDIREITAR_ANTES


def test_projeto_sem_o_campo_corta_antes():
    dados = Projeto(caminho_entrada="x.pdf").para_dicionario()
    dados.pop("ordem_do_preparo")
    assert Projeto.de_dicionario(dados).ordem_do_preparo == op.CORTAR_ANTES


def test_o_campo_vai_e_volta_do_arquivo():
    for ordem in op.ORDENS:
        projeto = Projeto(caminho_entrada="x.pdf", ordem_do_preparo=ordem)
        assert Projeto.de_dicionario(projeto.para_dicionario()).ordem_do_preparo == ordem


def test_valor_estranho_e_a_ordem_de_sempre():
    assert op.ordem_valida("qualquer coisa") == op.CORTAR_ANTES
    assert op.ordem_valida(None) == op.CORTAR_ANTES
    assert op.ordem_do_livro(object()) == op.CORTAR_ANTES
    assert not op.endireita_antes(Projeto(caminho_entrada="x.pdf", ordem_do_preparo="xx"))


# ------------------------------------------------------------------ projeto antigo: identico

def _preparo_de_antes(img_folha, folha, pagina, projeto, dpi):
    """CÓPIA CONGELADA da conta de antes do G6 (core/pipeline de 08/10/2026,
    _geometria + _preparar_metade_e_geometria, sem nada guardado), só para
    este teste. Não mudar: é a régua do "idêntico ponto por ponto"."""
    inteira = pipeline.preparar_para_recorte(img_folha, folha, pagina, projeto)
    recorte, automatico = None, None
    if projeto.cortar_bordas:
        if pagina.recorte is None:
            automatico = detectar_bordas(inteira, dpi=dpi)
            recorte = automatico.tupla
        else:
            recorte = tuple(pagina.recorte)
    angulo = 0.0
    if projeto.endireitar:
        angulo = pagina.angulo_manual
        if angulo is None:
            cortada = inteira if recorte is None else fatiar(inteira, recorte)
            if es.jeito_da_pagina(projeto, pagina) == es.JEITO_SCANTAILOR:
                angulo = es.medir_na_pagina(inteira, dpi, None).angulo
            else:
                angulo = detectar_angulo(cortada).angulo
        angulo = float(angulo or 0.0)
        if automatico is not None and abs(angulo) >= ANGULO_MINIMO:
            recorte = alargar_para_o_giro(automatico, angulo, inteira).tupla
    img = inteira
    girar = projeto.endireitar and abs(angulo) >= ANGULO_MINIMO
    if recorte is not None:
        img = fatiar(inteira, recorte) if girar else aplicar_recorte(inteira, recorte)
    cortou = recorte is not None and (img is not inteira)
    if girar:
        img = rotacionar(img, angulo)
    dividida = bool(folha.dividir) and pagina.metade != METADE_INTEIRA
    desenho = zf.geometria_do_desenho(
        img_folha.shape[1] / max(1, img_folha.shape[0]), folha.rotacao,
        folha.posicao_corte if dividida else None,
        pagina.metade if dividida else METADE_INTEIRA,
        tuple(recorte) if cortou else None, float(angulo) if girar else 0.0,
        sobra=pipeline.faixa_da_sobra(folha, pagina, projeto))
    return img, desenho


CASOS_ANTIGOS = [
    # (nome, duas paginas, campos do projeto, da folha, da pagina)
    ("automatico", False, {}, {"dividir": False}, {}),
    ("automatico-scantailor", False, {"endireitar_como": es.JEITO_SCANTAILOR},
     {"dividir": False}, {}),
    ("giro-90", False, {}, {"dividir": False, "rotacao": 90}, {}),
    ("giro-180", False, {}, {"dividir": False, "rotacao": 180}, {}),
    ("corte-a-mao", False, {}, {"dividir": False}, {"recorte": (0.05, 0.06, 0.88, 0.9)}),
    ("angulo-a-mao", False, {}, {"dividir": False}, {"angulo_manual": -2.2}),
    ("os-dois-a-mao", False, {}, {"dividir": False},
     {"recorte": (0.1, 0.1, 0.8, 0.8), "angulo_manual": 0.8}),
    ("sem-cortar", False, {"cortar_bordas": False}, {"dividir": False}, {}),
    ("sem-endireitar", False, {"endireitar": False}, {"dividir": False}, {}),
    ("sobra", False, {"cortar_sobra": True}, {"dividir": False, "sobra": (0.03, 0.97)}, {}),
    ("esquerda", True, {}, {"dividir": True, "posicao_corte": 0.5}, {"metade": METADE_ESQUERDA}),
    ("direita", True, {}, {"dividir": True, "posicao_corte": 0.52}, {"metade": METADE_DIREITA}),
]


@pytest.mark.parametrize("nome,duas,campos,folha,pagina", CASOS_ANTIGOS,
                         ids=[c[0] for c in CASOS_ANTIGOS])
def test_projeto_antigo_sai_identico_ponto_por_ponto(tmp_path, scantailor_fixo,
                                                     nome, duas, campos, folha, pagina):
    caminho = _pdf(tmp_path, nome, -1.4 if not duas else 0.9, duas=duas)
    campos = {"endireitar_como": es.JEITO_PROGRAMA, **campos}
    projeto = _antigo(caminho, **campos)
    assert projeto.ordem_do_preparo == op.CORTAR_ANTES
    f, p = _com_folha(projeto, folha, pagina)
    img_folha = _desenhar(caminho)

    esperada, desenho_esperado = _preparo_de_antes(img_folha, f, p, projeto, DPI)
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, projeto, dpi=DPI)
    assert saida.shape == esperada.shape and np.array_equal(saida, esperada)
    assert desenho == desenho_esperado
    assert "ordem" not in desenho                 # a geometria gravada e a de sempre

    # a previa na resolucao do PDF (com a geometria guardada) e a mesma
    doc = abrir_pdf(caminho)
    try:
        previa, _ = pipeline.renderizar_pagina(doc, projeto, p, dpi=DPI)
        # a aba Bordas: girada e dividida, nunca cortada nem endireitada
        bordas = pipeline.renderizar_pagina_para_recorte(doc, projeto, p, dpi=DPI)
    finally:
        doc.close()
    assert np.array_equal(bordas, pipeline.preparar_para_recorte(img_folha, f, p, projeto))
    assert previa.shape[:2] == esperada.shape[:2]


# ------------------------------------------------------------------ a ordem nova

def _quase_igual(a: np.ndarray, b: np.ndarray) -> bool:
    """Mesma forma, e no maximo 1 nivel de cinza de diferenca em menos de 1%
    dos pontos: girar so a parte cortada (core/endireitar.rotacionar_e_cortar)
    contra girar a pagina inteira e depois cortar (arredondamento do
    warpAffine; medido em 09/10/2026)."""
    if a.shape != b.shape:
        return False
    diferenca = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return int(diferenca.max(initial=0)) <= 1 and float((diferenca > 0).mean()) < 0.01


def _corte_na_reta(base: np.ndarray, angulo: float):
    """O corte automatico do livro novo: detectar_bordas na pagina em cinza
    endireitada (pipeline._geometria_endireitando_antes)."""
    cinza = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    return detectar_bordas(rotacionar(cinza, angulo), dpi=DPI).tupla


def _margens_da_tinta(img: np.ndarray) -> tuple[int, int, int, int]:
    """Pontos de papel entre a tinta e cada borda (esquerda, cima, direita, baixo)."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(cinza < 128)
    return (int(xs.min()), int(ys.min()),
            int(cinza.shape[1] - 1 - xs.max()), int(cinza.shape[0] - 1 - ys.max()))


@pytest.mark.parametrize("graus", [-1.4, 0.9, 2.5])
def test_ordem_nova_mesmo_angulo_e_cantos_com_folga(tmp_path, graus):
    """O ângulo do livro novo é o mesmo da ordem antiga (só o corte muda), e
    o corte achado na página reta deixa ~1 mm de papel nos quatro lados - o
    bug "páginas endireitadas ficam com menos de 1 mm nos cantos"."""
    caminho = _pdf(tmp_path, "torto", graus)
    img_folha = _desenhar(caminho)
    antigo = _antigo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    fa, pa = _com_folha(antigo, {"dividir": False}, {})
    _, desenho_antigo = pipeline.preparar_metade_e_geometria(img_folha, fa, pa, antigo, dpi=DPI)

    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    fn, pn = _com_folha(novo, {"dividir": False}, {})
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, fn, pn, novo, dpi=DPI)

    assert desenho["ordem"] == op.ENDIREITAR_ANTES
    assert desenho["angulo"] == desenho_antigo["angulo"]
    assert abs(desenho["angulo"] + graus) < 0.3            # endireitou de verdade
    um_mm = DPI / 25.4
    assert min(_margens_da_tinta(saida)) >= um_mm - 3, _margens_da_tinta(saida)


def test_ordem_nova_corta_a_pagina_reta(tmp_path):
    """A imagem do livro novo é: girar a página inteira, achar o corte nela,
    cortar. E o corte à mão está em fração da página RETA."""
    caminho = _pdf(tmp_path, "torto", -1.4)
    img_folha = _desenhar(caminho)
    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    f, p = _com_folha(novo, {"dividir": False}, {})
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, novo, dpi=DPI)
    base = pipeline.preparar_para_recorte(img_folha, f, p, novo)
    reta = rotacionar(base, desenho["angulo"])
    corte = _corte_na_reta(base, desenho["angulo"])
    assert tuple(desenho["recorte"]) == corte
    # o mesmo corte achado na pagina colorida endireitada (o que a simulacao
    # mostrou ao Samuel) - o cinza e so para pesar menos
    assert np.allclose(corte, detectar_bordas(reta, dpi=DPI).tupla, atol=2e-3)
    assert _quase_igual(saida, aplicar_recorte(reta, corte))

    pipeline._GEOMETRIAS.clear()
    p.recorte = (0.1, 0.1, 0.8, 0.8)
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, novo, dpi=DPI)
    assert desenho["recorte"] == [0.1, 0.1, 0.8, 0.8]
    assert _quase_igual(saida, aplicar_recorte(reta, (0.1, 0.1, 0.8, 0.8)))


def test_ordem_nova_angulo_a_mao_e_endireitar_desligado(tmp_path):
    caminho = _pdf(tmp_path, "torto", -1.4)
    img_folha = _desenhar(caminho)
    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    f, p = _com_folha(novo, {"dividir": False}, {"angulo_manual": 2.0})
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, novo, dpi=DPI)
    base = pipeline.preparar_para_recorte(img_folha, f, p, novo)
    reta = rotacionar(base, 2.0)
    assert desenho["angulo"] == 2.0
    assert _quase_igual(saida, aplicar_recorte(reta, _corte_na_reta(base, 2.0)))

    sem = _novo(caminho, endireitar=False)
    f, p = _com_folha(sem, {"dividir": False}, {})
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, sem, dpi=DPI)
    assert desenho["angulo"] == 0.0
    assert np.array_equal(saida, aplicar_recorte(base, detectar_bordas(base, dpi=DPI)))


def test_aba_bordas_mostra_a_pagina_reta(tmp_path):
    caminho = _pdf(tmp_path, "torto", -1.4)
    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    f, p = _com_folha(novo, {"dividir": False}, {})
    doc = abrir_pdf(caminho)
    try:
        bordas = pipeline.renderizar_pagina_para_recorte(doc, novo, p, dpi=DPI)
    finally:
        doc.close()
    angulo = pipeline.angulo_da_pagina(novo, p)          # medido e guardado
    assert angulo is not None and abs(angulo) >= ANGULO_MINIMO
    base = pipeline.preparar_para_recorte(_desenhar(caminho), f, p, novo)
    assert np.array_equal(bordas, rotacionar(base, angulo))
    # nunca cortada: o retangulo da aba vale 1:1 na pagina reta
    assert bordas.shape == base.shape


def test_ordem_nova_na_previa_e_na_chave(tmp_path):
    """A previa da tela (outra resolucao) usa a geometria guardada na
    resolucao do PDF; trocar a ordem muda a chave (nada guardado e reusado
    entre as duas)."""
    caminho = _pdf(tmp_path, "torto", -1.4)
    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    f, p = _com_folha(novo, {"dividir": False}, {})
    chave = pipeline._chave_da_geometria(f, p, novo)
    novo.ordem_do_preparo = op.CORTAR_ANTES
    assert pipeline._chave_da_geometria(f, p, novo) != chave
    novo.ordem_do_preparo = op.ENDIREITAR_ANTES
    doc = abrir_pdf(caminho)
    try:
        previa, _ = pipeline.renderizar_pagina(doc, novo, p, dpi=110)
    finally:
        doc.close()
    assert pipeline._geometria_guardada(f, p, novo) is not None
    assert p.geometria_das_zonas["ordem"] == op.ENDIREITAR_ANTES
    assert previa.ndim >= 2


def test_analise_mede_o_mesmo_angulo_nas_duas_ordens(tmp_path, scantailor_fixo):
    """O aviso C1 (as duas contas discordam) sai igual: a análise só quer o
    ângulo, e o ângulo não depende da ordem."""
    caminho = _pdf(tmp_path, "torto", -1.4)
    resultados = []
    for projeto in (_antigo(caminho), _novo(caminho)):
        projeto.endireitar_como = es.JEITO_SCANTAILOR
        pipeline.analisar_projeto(projeto)
        medidas: dict = {}
        base = pipeline.preparar_para_recorte(_desenhar(caminho, 150), projeto.folhas[0],
                                              projeto.paginas[0], projeto)
        _, angulo = pipeline._geometria(base, projeto.paginas[0], projeto, dpi=150,
                                        medidas=medidas)
        resultados.append((angulo, medidas, list(projeto.paginas[0].alertas)))
    assert resultados[0] == resultados[1]


def test_retangulo_a_mao_fica_no_mesmo_lugar_de_fabrica():
    """g6-retangulo, decisão do Samuel (09/10/2026): "Fica no mesmo lugar da
    página (como no ScanTailor)" é o de fábrica - mudar o ângulo depois não
    mexe nos números do corte à mão (nos dois tipos de projeto)."""
    assert pipeline.RETANGULO_PADRAO == pipeline.RETANGULO_FICA
    for projeto in (_novo("x.pdf"), _antigo("x.pdf")):
        _, p = _com_folha(projeto, {"dividir": False}, {"recorte": (0.1, 0.2, 0.7, 0.6)})
        assert pipeline.recorte_depois_de_mudar_o_angulo(
            projeto, p, 0.5, -1.0, proporcao=0.7) == (0.1, 0.2, 0.7, 0.6)
        p.recorte = None
        assert pipeline.recorte_depois_de_mudar_o_angulo(projeto, p, 0.5, -1.0) is None


def test_retangulo_a_mao_acompanha_o_texto_a_outra_opcao(tmp_path):
    """A outra opção pedida pelo Samuel ("Acompanha o texto"; onde trocar
    ainda vai ser perguntado, sem tela): o retângulo cresce para o mesmo
    pedaço do papel continuar dentro. Conferido no pixel: um ponto vermelho
    perto do canto do corte à mão continua na página depois de mudar o
    ângulo. Na ordem antiga, e sem a proporção, fica como está."""
    caminho = _pdf(tmp_path, "ponto", 0.0, ponto=(0.232, 0.262))
    img_folha = _desenhar(caminho)
    novo = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    recorte = (0.22, 0.25, 0.5, 0.5)                   # o ponto bem no canto de cima, a esquerda
    f, p = _com_folha(novo, {"dividir": False}, {"recorte": recorte, "angulo_manual": 0.0})
    base = pipeline.preparar_para_recorte(img_folha, f, p, novo)
    proporcao = base.shape[1] / base.shape[0]
    assert _onde_esta_o_vermelho(pipeline.preparar_metade(img_folha, f, p, novo, dpi=DPI))

    acompanha = pipeline.recorte_depois_de_mudar_o_angulo(
        novo, p, 0.0, 4.0, jeito=pipeline.RETANGULO_ACOMPANHA, proporcao=proporcao)
    x, y, w, h = acompanha
    assert x <= recorte[0] and y <= recorte[1]
    assert x + w >= recorte[0] + recorte[2] and y + h >= recorte[1] + recorte[3]
    assert w * h < recorte[2] * recorte[3] * 1.25           # cresce so um pouco

    pipeline._GEOMETRIAS.clear()
    p.angulo_manual = 4.0
    p.recorte = acompanha
    _onde_esta_o_vermelho(pipeline.preparar_metade(img_folha, f, p, novo, dpi=DPI))
    # o de fabrica (fica): com o mesmo giro, o ponto do canto sai do corte
    pipeline._GEOMETRIAS.clear()
    p.recorte = recorte
    with pytest.raises(AssertionError):
        _onde_esta_o_vermelho(pipeline.preparar_metade(img_folha, f, p, novo, dpi=DPI))

    antigo = _antigo(caminho)
    _, pa = _com_folha(antigo, {"dividir": False}, {"recorte": recorte})
    assert pipeline.recorte_depois_de_mudar_o_angulo(
        antigo, pa, 0.0, 4.0, jeito=pipeline.RETANGULO_ACOMPANHA, proporcao=proporcao) == recorte
    assert pipeline.recorte_depois_de_mudar_o_angulo(
        novo, pa, 0.0, 4.0, jeito=pipeline.RETANGULO_ACOMPANHA) == recorte


# ------------------------------------------------------------------ as zonas

def _onde_esta_o_vermelho(img: np.ndarray) -> tuple[float, float]:
    """Centro do quadradinho vermelho, em fração da imagem."""
    b, g, r = (img[..., i].astype(int) for i in range(3))
    ys, xs = np.where((r > 150) & (g < 110) & (b < 110))
    assert len(xs), "o ponto vermelho sumiu da página"
    return (xs.mean() + 0.5) / img.shape[1], (ys.mean() + 0.5) / img.shape[0]


@pytest.mark.parametrize("ordem", op.ORDENS)
@pytest.mark.parametrize("folha,pagina,duas,ponto", [
    ({"dividir": False}, {}, False, (0.55, 0.62)),
    ({"dividir": False}, {"recorte": (0.08, 0.05, 0.85, 0.9), "angulo_manual": 2.4}, False,
     (0.55, 0.62)),
    # corte a mao bem fora do centro: o centro do giro das duas ordens fica
    # longe (centenas de pontos), e a conta da ordem errada erra o pixel
    ({"dividir": False}, {"recorte": (0.02, 0.03, 0.55, 0.5), "angulo_manual": 3.0}, False,
     (0.3, 0.3)),
    ({"dividir": False, "rotacao": 90}, {"angulo_manual": -1.7}, False, (0.55, 0.62)),
    ({"dividir": False, "rotacao": 270}, {"recorte": (0.4, 0.45, 0.58, 0.52),
                                          "angulo_manual": -2.6}, False, (0.3, 0.6)),
    ({"dividir": True, "posicao_corte": 0.5}, {"metade": METADE_DIREITA, "angulo_manual": 1.9},
     True, (0.78, 0.6)),
])
def test_conta_das_zonas_acerta_o_pixel_nas_duas_ordens(tmp_path, ordem, folha, pagina, duas,
                                                        ponto):
    """Um ponto marcado na folha original cai, pela conta de
    core/zonas_na_folha (com a ordem como dado), no mesmo lugar em que o
    pipeline o desenha - a zona fica sobre o mesmo pedaço do papel."""
    caminho = _pdf(tmp_path, "ponto", -1.2, duas=duas, ponto=ponto)
    projeto = _novo(caminho, endireitar_como=es.JEITO_PROGRAMA, ordem_do_preparo=ordem)
    f, p = _com_folha(projeto, folha, pagina)
    img_folha = _desenhar(caminho)
    saida, desenho = pipeline.preparar_metade_e_geometria(img_folha, f, p, projeto, dpi=DPI)
    assert ("ordem" in desenho) == (ordem == op.ENDIREITAR_ANTES)
    assert desenho["angulo"] != 0.0
    zona = [{"forma": "poligono", "tipo": "gravura", "operacao": "somar",
             "pontos": [list(ponto)]}]
    (u, v), = zf.folha_para_pagina(zona, desenho)[0]["pontos"]
    x, y = _onde_esta_o_vermelho(saida)
    altura, largura = saida.shape[:2]
    assert abs(u - x) * largura < 3 and abs(v - y) * altura < 3, (u * largura, x * largura,
                                                                  v * altura, y * altura)


def test_zonas_ida_e_volta_na_ordem_nova():
    g = zf.geometria_do_desenho(0.7, 90, None, "inteira", (0.05, 0.04, 0.9, 0.91), 1.7,
                                ordem=op.ENDIREITAR_ANTES)
    assert zf.geometria_valida(g)
    zona = [{"forma": "retangulo", "tipo": "gravura", "operacao": "somar",
             "pontos": [[0.2, 0.3], [0.6, 0.7]], "espessura": 0.01}]
    volta = zf.folha_para_pagina(zf.pagina_para_folha(zona, g), g)[0]
    assert np.allclose(volta["pontos"], zona[0]["pontos"], atol=1e-9)
    assert abs(volta["espessura"] - 0.01) < 1e-12


def test_geometria_sem_a_chave_e_a_de_sempre_e_as_ordens_nao_se_confundem():
    sem = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 1.2)
    corta = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 1.2,
                                    ordem=op.CORTAR_ANTES)
    endireita = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 1.2,
                                        ordem=op.ENDIREITAR_ANTES)
    assert sem == corta and "ordem" not in sem
    assert zf.mesma_geometria(sem, corta)
    assert not zf.mesma_geometria(sem, endireita)
    assert not zf.geometria_valida({**endireita, "ordem": "outra"})
    # sem angulo as duas ordens poem a zona no mesmo lugar (so o giro muda)
    zona = [{"forma": "poligono", "tipo": "papel", "operacao": "somar", "pontos": [[0.3, 0.4]]}]
    sem_giro = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 0.0)
    sem_giro_nova = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 0.0,
                                            ordem=op.ENDIREITAR_ANTES)
    # e a geometria e a mesma: sem giro a zona nao tem por que andar
    assert sem_giro == sem_giro_nova and zf.mesma_geometria(sem_giro, sem_giro_nova)
    assert np.allclose(zf.folha_para_pagina(zona, sem_giro)[0]["pontos"],
                       zf.folha_para_pagina(zona, sem_giro_nova)[0]["pontos"])


def test_zonas_de_projeto_antigo_nao_andam(tmp_path):
    """Página de projeto antigo com zonas e a geometria anotada antes do G6
    (sem a chave "ordem"): desenhar de novo não leva as zonas a lugar
    nenhum (a pendência D2/Z1)."""
    caminho = _pdf(tmp_path, "torto", -1.4)
    projeto = _antigo(caminho, endireitar_como=es.JEITO_PROGRAMA)
    f, p = _com_folha(projeto, {"dividir": False}, {})
    _, desenho = _preparo_de_antes(_desenhar(caminho), f, p, projeto, DPI)
    zona = [{"forma": "retangulo", "tipo": "gravura", "operacao": "somar",
             "pontos": [[0.2, 0.3], [0.6, 0.7]]}]
    p.selecao = [dict(z) for z in zona]
    p.geometria_das_zonas = dict(desenho)
    # vai ao disco e volta, como no programa
    projeto = Projeto.de_dicionario(projeto.para_dicionario())
    p = projeto.paginas[0]
    doc = abrir_pdf(caminho)
    try:
        pipeline.renderizar_pagina(doc, projeto, p, dpi=110)
        pipeline.renderizar_pagina(doc, projeto, p, dpi=DPI)
    finally:
        doc.close()
    assert p.selecao == zona
    assert p.geometria_das_zonas == desenho


# ------------------------------------------------------------------ a janela

from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    app,
    janela,
    pasta,
)


def _pdf_texto(pasta):
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Texto.pdf"
    doc = fitz.open()
    for _ in range(2):
        pagina = doc.new_page(width=420, height=595)
        for y in range(70, 540, 16):
            pagina.insert_text((40, y), "texto corrido da pagina " * 2, fontsize=9)
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def test_janela_livro_novo_e_reabrir(janela, pasta):
    import projetos

    janela.abrir_livro(_pdf_texto(pasta))
    assert janela.projeto.ordem_do_preparo == op.ENDIREITAR_ANTES
    _analisar(janela)
    janela._salvar_agora()
    assert projetos.esperar_gravacoes(10)
    caminho = janela.projeto.caminho_entrada
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO

    def reabrir():
        if janela.previas is not None:
            janela.previas.parar()
            janela.previas = None
        janela.tela_opcoes.folhear.fechar()
        janela.abrir_livro(caminho)

    reabrir()
    assert janela.projeto.ordem_do_preparo == op.ENDIREITAR_ANTES

    # o programa de antes do G6 grava sem o campo: reabre cortando antes
    dados = json.loads(estado.read_text(encoding="utf-8"))
    assert dados["ordem_do_preparo"] == op.ENDIREITAR_ANTES
    dados.pop("ordem_do_preparo")
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    reabrir()
    assert janela.projeto.ordem_do_preparo == op.CORTAR_ANTES


# ------------------------------------------------------------------ a velocidade

def test_girar_so_a_parte_cortada_e_o_mesmo_que_girar_tudo_e_cortar():
    """core/endireitar.rotacionar_e_cortar (regra 6: o livro novo nao gira a
    pagina inteira a toa) = rotacionar + fatiar, a menos do arredondamento;
    e a caixa e a mesma conta de pontos do fatiar (recortar.caixa_em_pontos)."""
    from core.endireitar import rotacionar_e_cortar
    from core.recortar import caixa_em_pontos

    rng = np.random.default_rng(7)
    img = cv2.GaussianBlur((rng.random((900, 640, 3)) * 255).astype(np.uint8), (5, 5), 0)
    recorte = (0.07, 0.11, 0.81, 0.77)
    caixa = caixa_em_pontos(img.shape, recorte)
    x0, y0, x1, y1 = caixa
    assert np.shares_memory(fatiar(img, recorte), img)
    assert fatiar(img, recorte).shape[:2] == (y1 - y0, x1 - x0)
    for angulo in (-2.7, -0.4, 0.0, 0.05, 1.3):
        assert _quase_igual(rotacionar_e_cortar(img, angulo, caixa),
                            fatiar(rotacionar(img, angulo), recorte))
    assert caixa_em_pontos(img.shape, (0.5, 0.5, 0.001, 0.4)) is None     # absurdo: nao corta
