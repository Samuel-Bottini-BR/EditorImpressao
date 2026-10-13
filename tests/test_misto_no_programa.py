"""O modo Misto ligado ao processamento (ligar o Misto ao programa, passo 2).

Pedidos do Samuel: a caixinha "So as letras" no Preto e branco, por livro e
por pagina (conferencia 10, P1 (a)); A "Guardar a tinta forte" de fabrica,
achando as linhas so com o docTR, o Kraken como segunda opiniao desligada
(conferencia 14); "Para revisar" sozinho quando sobra muita tinta forte fora
das linhas (conferencia 8, REVISAR: "Sim").

O que se cobra (testes de maquina, paginas sinteticas; o leitor de texto e
trocado por um falso, para nao depender do modelo nem do tempo dele):
    - sem "So as letras", core.pipeline._filtrar da exatamente o de antes;
    - com ela, a pagina em Preto e branco passa por core.misto.aplicar_misto
      com as escolhas da pagina; nos outros filtros nada muda;
    - a B nao chama o leitor; a A e a C chamam, uma vez por pagina (a previa
      e o PDF usam as mesmas linhas);
    - os avisos da regra ajustada do "Para revisar" (12/10/2026; trocaram o
      "Tinta forte fora do texto") entram quando algo some do resultado e
      saem sozinhos quando o problema e resolvido ou a pagina deixa o Misto
      A/C; a faixa na beirada em quase todas as paginas vira aviso do livro;
    - core.linhas_do_texto guarda as linhas por pagina, nao guarda a de
      imagem pequena nem a que falhou, e o gancho do Kraken soma as linhas.
A prova nas 32 paginas do gabarito (sem Misto, identicas ao ace15b2) esta em
relatorios/conferir/misto-no-programa-2026-10-05/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core import analise, linhas_do_texto, misto
from core import pipeline as P
from core.filtros import MELHORAR, PRETO_E_BRANCO, aplicar_filtro_com_selecao
from core.ocr_comum import LinhaOCR, ResultadoOCR, retangulo as caixa
from core.selecao import GRAVURA, Selecao, retangulo
from modelos import ConfigFolha, ConfigPagina, Projeto

RAIZ = Path(__file__).resolve().parent.parent
PAPEL = (200, 222, 232)


@pytest.fixture(autouse=True)
def linhas_limpas():
    linhas_do_texto.esquecer()
    yield
    linhas_do_texto.esquecer()


def _pagina_sintetica():
    """Duas linhas de texto, uma "nota" escura grande fora delas e uma
    gravura marcada (para o Misto ter o que fazer)."""
    img = np.full((900, 700, 3), PAPEL, np.uint8)
    for y in (100, 140):
        for x in range(100, 600, 16):
            img[y:y + 12, x:x + 4] = 30
    img[380:480, 280:400] = 20                    # a "nota": tinta forte fora do texto
    yy, xx = np.mgrid[600:850, 150:550]
    img[600:850, 150:550] = (90 + 60 * np.sin(xx / 4.0) * np.cos(yy / 6.0)).astype(np.uint8)[..., None]
    s = Selecao()
    s.acrescentar(retangulo(150 / 700, 600 / 900, 550 / 700, 850 / 900, tipo=GRAVURA))
    return img, s


def _resultado_falso(largura=700, altura=900):
    """O que o docTR diria: as duas linhas de texto."""
    return ResultadoOCR("doctr", [LinhaOCR(caixa(95, 98, 605, 114)),
                                  LinhaOCR(caixa(95, 138, 605, 154))],
                        largura=largura, altura=altura)


def _projeto(selecao, filtro=PRETO_E_BRANCO, **opcoes) -> Projeto:
    p = Projeto(caminho_entrada=str(RAIZ / "nao-existe.pdf"), **opcoes)
    p.folhas = [ConfigFolha(indice=0, dividir=False)]
    pagina = ConfigPagina(indice=0, folha=0, filtro=filtro)
    pagina.guardar_selecao(selecao)        # ja marcada: garantir_selecao devolve esta
    p.paginas = [pagina]
    return p


@pytest.fixture
def leitor_falso(monkeypatch):
    """Troca o leitor de texto por um falso que conta as chamadas."""
    chamadas = []

    def falso(img, chave=None, cancelar=None):
        chamadas.append(img.shape)
        return [_resultado_falso(img.shape[1], img.shape[0])]

    monkeypatch.setattr(P.linhas_do_texto, "linhas_da_pagina", falso)
    return chamadas


# --- sem "So as letras": o caminho de sempre --------------------------------

def test_sem_so_as_letras_e_o_preto_e_branco_de_sempre(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s)
    saida, mono = P._filtrar(p, p.paginas[0], img.copy())
    esperado, mono_e = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert mono == mono_e and np.array_equal(saida, esperado)
    assert leitor_falso == [], "sem o Misto, o leitor de texto nao pode rodar"


def test_so_as_letras_nao_vale_em_outro_filtro(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, filtro=MELHORAR, misto_so_as_letras=True)
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    esperado, _ = aplicar_filtro_com_selecao(img.copy(), MELHORAR, s)
    assert np.array_equal(saida, esperado)
    assert leitor_falso == []


# --- com "So as letras" --------------------------------------------------------

def test_b_e_o_misto_sem_o_leitor(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_TUDO)
    saida, mono = P._filtrar(p, p.paginas[0], img.copy())
    esperado, mono_e = misto.aplicar_misto(img.copy(), s)
    assert mono == mono_e and np.array_equal(saida, esperado)
    assert leitor_falso == []
    assert not np.array_equal(saida, aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)[0])


def test_a_de_fabrica_usa_as_linhas_e_guarda_a_nota(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    linhas, altura = misto.mascara_das_linhas([_resultado_falso()], img.shape)
    esperado, _ = misto.aplicar_misto(img.copy(), s, fora_do_texto=misto.FORA_REDE,
                                      linhas=linhas, altura_linha=altura)
    assert np.array_equal(saida, esperado)
    assert leitor_falso == [img.shape]
    nota = saida[410:460, 310:370]
    assert float((nota == 0).mean()) > 0.5, "a nota escura tinha de ficar (A)"


def test_c_apaga_o_que_esta_fora_das_linhas(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_APAGAR)
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    assert int(saida[410:460, 310:370].min()) == 255


def test_a_pagina_troca_so_nela(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    p.paginas[0].misto_so_as_letras = False
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    assert np.array_equal(saida, aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)[0])


def test_as_escolhas_da_pagina_chegam_ao_misto(monkeypatch, leitor_falso):
    vistos = {}

    def espiao(img, selecao, *args, **kwargs):
        vistos.update(kwargs)
        return img, False

    monkeypatch.setattr(P.misto, "aplicar_misto", espiao)
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, pb_decoracao_em_preto_e_branco=True)
    p.paginas[0].misto_papel_da_gravura = misto.PAPEL_COMO_ESCANEADO
    p.paginas[0].misto_letras_na_moldura = misto.LETRAS_PRETAS
    P._filtrar(p, p.paginas[0], img.copy())
    assert vistos["papel_da_gravura_branco"] is False
    assert vistos["letras_na_moldura"] == misto.LETRAS_PRETAS
    assert vistos["fora_do_texto"] == misto.FORA_REDE
    # P5: a caixinha das molduras nao vale no Misto
    assert "decoracao_em_preto_e_branco" not in vistos


def test_leitor_indisponivel_vira_o_misto_b(monkeypatch):
    monkeypatch.setattr(P.linhas_do_texto, "linhas_da_pagina", lambda *a, **k: [])
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    assert np.array_equal(saida, misto.aplicar_misto(img.copy(), s)[0])
    # sem o leitor nao ha o que medir: nenhum aviso entra
    assert p.paginas[0].alertas == []


# --- "Para revisar" sozinho: a regra ajustada (12/10/2026) --------------------
#
# Ate 12/10 a pagina ia para "Para revisar" quando a tinta forte fora das
# linhas passava de 10% da tinta (o aviso "Tinta forte fora do texto"): nas 89
# paginas do estudo, 55 iam e 52 estavam certas. A regra ajustada (Samuel,
# rodada 4, `rv4-resumo`: "Fica assim"; core/revisar.py) olha o que SUMIU do
# resultado. As contas uma a uma estao em tests/test_revisar.py; aqui, a
# ligacao ao processamento.

def _com_letra_clara(img):
    """A pagina sintetica com uma letra "T" grande e clara colada embaixo do
    texto (a T vermelha do Antiphonal 46): mais clara que as letras, o jeito de
    fabrica a manda para o branco inteira."""
    img = img.copy()
    img[165:177, 100:180] = 110
    img[177:245, 134:146] = 110
    return img


def _tem(caixas, x, y, largura=700, altura=900) -> bool:
    """Alguma caixa (em fracao da pagina) cobre o ponto (x, y)?"""
    return any(x0 * largura <= x <= x1 * largura and y0 * altura <= y <= y1 * altura
               for x0, y0, x1, y1 in caixas)


def test_a_tinta_forte_guardada_nao_manda_mais_para_revisar(leitor_falso):
    """O defeito do aviso antigo: a nota escura fora do texto, que o jeito de
    fabrica GUARDA, mandava a pagina para a lista sem nada estar errado."""
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    P._filtrar(p, p.paginas[0], img.copy())
    assert p.paginas[0].alertas == []
    assert p.paginas[0].faixa_na_beirada is False, "a pagina foi medida"


def test_letra_grande_que_some_manda_para_revisar(leitor_falso):
    img, s = _pagina_sintetica()
    img = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    pagina.revisada = True
    saida, _ = P._filtrar(p, pagina, img.copy())
    assert int(saida[165:245, 100:180].min()) == 255, "a letra clara tinha de sumir (A)"
    assert pagina.alertas[0] == analise.DESENHO_APAGADO
    assert pagina.precisa_revisao and not pagina.revisada
    # o lugar onde sumiu ja vem marcado
    assert _tem(P.marcas_do_aviso(pagina, analise.DESENHO_APAGADO), 140, 200)
    assert P.marcas_do_aviso(pagina) == P.marcas_do_aviso(pagina, analise.DESENHO_APAGADO)
    # "esta bom assim" vale: desenhar de novo nao volta a pedir
    pagina.revisada = True
    P._filtrar(p, pagina, img.copy())
    assert pagina.revisada and pagina.alertas.count(analise.DESENHO_APAGADO) == 1


@pytest.mark.parametrize("como_resolver", ["guardar_tudo", "desligar", "outro_filtro"])
def test_o_aviso_some_sozinho_quando_o_problema_e_resolvido(leitor_falso, como_resolver):
    """Samuel, rodada 4: "quando eu resolver aquele problema, o programa já
    vai automaticamente ver que eu resolvi?" """
    img, s = _pagina_sintetica()
    img = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert analise.DESENHO_APAGADO in pagina.alertas
    if como_resolver == "guardar_tudo":
        pagina.misto_fora_do_texto = misto.FORA_TUDO
    elif como_resolver == "desligar":
        pagina.misto_so_as_letras = False
    else:
        pagina.filtro = MELHORAR
    # sem desenhar (o que a tela chama a cada atualizacao)...
    P.acertar_alertas_do_fundo(p, [pagina])
    assert analise.DESENHO_APAGADO not in pagina.alertas
    assert P.marcas_do_aviso(pagina) == [] and pagina.faixa_na_beirada is None
    # ...e desenhando
    pagina.alertas.insert(0, analise.DESENHO_APAGADO)
    P._filtrar(p, pagina, img.copy())
    assert analise.DESENHO_APAGADO not in pagina.alertas


def test_acertar_sem_desenhar_nao_tira_o_aviso_de_quem_continua_no_a(leitor_falso):
    img, s = _pagina_sintetica()
    img = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    P._filtrar(p, p.paginas[0], img.copy())
    P.acertar_alertas_do_fundo(p)
    assert analise.DESENHO_APAGADO in p.paginas[0].alertas
    assert P.marcas_do_aviso(p.paginas[0])


def test_guardar_so_o_texto_que_apaga_tinta_forte(leitor_falso):
    """O "Guardar só o texto" apaga de proposito o que nao e linha; o aviso
    vale quando some bastante tinta forte (a musica do Graduale 222), e a
    conta do desenho apagado nao entra."""
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_APAGAR)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert pagina.alertas == [analise.SO_O_TEXTO_APAGOU]
    assert _tem(P.marcas_do_aviso(pagina, analise.SO_O_TEXTO_APAGOU), 340, 430)
    # trocar a pagina para "Guardar a tinta forte" traz a nota de volta: o aviso some
    pagina.misto_fora_do_texto = misto.FORA_REDE
    P._filtrar(p, pagina, img.copy())
    assert pagina.alertas == []


def test_o_aviso_antigo_sai_do_projeto_salvo_antes(leitor_falso):
    """Projeto gravado antes de 12/10/2026 pode ter o "Tinta forte fora do
    texto": ele sai ao abrir a conferencia, com ou sem "So as letras"."""
    for ligado in (True, False):
        _img, s = _pagina_sintetica()
        p = _projeto(s, misto_so_as_letras=ligado)
        p.paginas[0].alertas = [analise.TINTA_FORTE_FORA_DO_TEXTO, analise.RESOLUCAO_BAIXA]
        P.acertar_alertas_do_fundo(p)
        assert p.paginas[0].alertas == [analise.RESOLUCAO_BAIXA]


def test_a_regra_so_e_medida_no_desenho_da_resolucao_do_pdf(leitor_falso):
    """A regra foi acertada e aprovada a 300 DPI; a 110 DPI (a previa) 13 das
    89 paginas do estudo decidem diferente (medido em 12/10/2026). A previa e
    o arrasto do medidor (55 DPI) nao medem: os avisos ficam como estavam (nem
    entram nem saem). O PDF e a medida que a tela pede por tras medem."""
    img, s = _pagina_sintetica()
    img = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    assert p.qualidade_dpi == 300
    pagina = p.paginas[0]
    for dpi in (55, 110):
        P._filtrar(p, pagina, img.copy(), dpi_pedido=dpi)
        assert pagina.alertas == [] and pagina.faixa_na_beirada is None, dpi
    pagina.alertas = [analise.COR]
    P._filtrar(p, pagina, img.copy(), dpi_pedido=300)
    assert pagina.alertas == [analise.DESENHO_APAGADO, analise.COR]
    # a previa de depois, de uma pagina que nem teria o problema, nao tira o aviso
    P._filtrar(p, pagina, _pagina_sintetica()[0], dpi_pedido=110)
    assert pagina.alertas == [analise.DESENHO_APAGADO, analise.COR]
    assert P._da_para_medir(img, None, p) and P._da_para_medir(img, 300, p)
    assert not P._da_para_medir(img, 299, p)
    assert not P._da_para_medir(img[:300, :300], None, p), "imagem minuscula nunca e medida"
    # livro de 200 DPI: a resolucao do PDF dele e 200
    p.qualidade_dpi = 200
    assert P._da_para_medir(img, 200, p) and not P._da_para_medir(img, 110, p)


def test_quem_precisa_da_medida_por_tras(leitor_falso):
    _img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    assert P.precisa_medir_para_revisar(p, pagina)
    for mudar, valor in (("misto_fora_do_texto", misto.FORA_TUDO), ("misto_so_as_letras", False),
                         ("filtro", MELHORAR), ("em_branco", True), ("apagada", True)):
        antes = getattr(pagina, mudar)
        setattr(pagina, mudar, valor)
        assert not P.precisa_medir_para_revisar(p, pagina), mudar
        setattr(pagina, mudar, antes)
    p.limpar = False
    assert not P.precisa_medir_para_revisar(p, pagina)


def test_a_copia_do_cartao_nao_mexe_nas_marcas_da_pagina(leitor_falso):
    """Os cartoes de filtro desenham uma COPIA da pagina com outro filtro
    (renderizar_com_filtro): ela nao pode apagar as marcas da pagina de verdade."""
    from dataclasses import replace

    img, s = _pagina_sintetica()
    img = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    antes = P.marcas_do_aviso(pagina)
    assert antes
    copia = replace(pagina, filtro=MELHORAR, alertas=list(pagina.alertas))
    P._filtrar(p, copia, img.copy())
    assert P.marcas_do_aviso(pagina) == antes
    assert analise.DESENHO_APAGADO in pagina.alertas


def test_a_medida_que_falha_nao_derruba_o_desenho(leitor_falso, monkeypatch):
    def quebrada(*args, **kwargs):
        raise RuntimeError("de proposito")

    monkeypatch.setattr(P.revisar, "medir", quebrada)
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    p.paginas[0].alertas = [analise.DESENHO_APAGADO]
    saida, _ = P._filtrar(p, p.paginas[0], img.copy())
    assert saida.shape[:2] == img.shape[:2]
    assert p.paginas[0].alertas == [analise.DESENHO_APAGADO], "sem medir, fica como estava"


def _livro_de(n: int) -> Projeto:
    p = Projeto(caminho_entrada=str(RAIZ / "nao-existe.pdf"))
    p.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    p.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(n)]
    return p


def test_faixa_em_quase_todas_as_paginas_vira_um_aviso_do_livro():
    """Samuel, rodada 4 (Camoes 66): "São as linhas pretas: aviso no livro basta"."""
    p = _livro_de(6)
    frase = analise.OBSERVACOES[analise.FAIXA_NA_BEIRADA]
    for pagina in p.paginas[:4]:
        pagina.faixa_na_beirada = True
        pagina.alertas = [analise.FAIXA_NA_BEIRADA, analise.RESOLUCAO_BAIXA]
    p.paginas[4].faixa_na_beirada = False          # a quinta foi medida e nao tem
    assert P.acertar_faixa_do_livro(p) is True     # 4 de 5 medidas = 80%
    assert frase in p.observacoes
    assert all(pg.alertas == [analise.RESOLUCAO_BAIXA] for pg in p.paginas[:4])
    assert P.acertar_faixa_do_livro(p) is False, "sem mudanca, nao pede redesenho"
    # a faixa do livro nao volta para a pagina desenhada depois
    assert P._faixa_e_do_livro(p)
    # duas paginas deixam de ter a faixa (o corte foi consertado): 2 de 5 = 40%
    p.paginas[0].faixa_na_beirada = p.paginas[1].faixa_na_beirada = False
    p.paginas[2].revisada = True
    assert P.acertar_faixa_do_livro(p) is True
    assert frase not in p.observacoes
    assert analise.FAIXA_NA_BEIRADA in p.paginas[2].alertas and p.paginas[2].revisada
    assert analise.FAIXA_NA_BEIRADA in p.paginas[3].alertas
    assert analise.FAIXA_NA_BEIRADA not in p.paginas[0].alertas


def test_com_poucas_paginas_medidas_a_faixa_fica_nas_paginas():
    p = _livro_de(6)
    for pagina in p.paginas[:3]:
        pagina.faixa_na_beirada = True
        pagina.alertas = [analise.FAIXA_NA_BEIRADA]
    assert P.acertar_faixa_do_livro(p) is False
    assert p.observacoes == []
    assert all(analise.FAIXA_NA_BEIRADA in pg.alertas for pg in p.paginas[:3])


def test_o_campo_da_faixa_vai_e_volta_do_projeto_salvo():
    p = _livro_de(2)
    p.paginas[0].faixa_na_beirada = True
    de_volta = Projeto.de_dicionario(p.para_dicionario())
    assert de_volta.paginas[0].faixa_na_beirada is True
    assert de_volta.paginas[1].faixa_na_beirada is None
    # projeto antigo, sem o campo: None
    dados = p.para_dicionario()
    for pagina in dados["paginas"]:
        pagina.pop("faixa_na_beirada")
    assert Projeto.de_dicionario(dados).paginas[0].faixa_na_beirada is None


# --- a previa e o PDF pelo mesmo caminho --------------------------------------

def _pdf(caminho: Path, img: np.ndarray) -> Path:
    import cv2
    import fitz

    ok, png = cv2.imencode(".png", img)
    assert ok
    doc = fitz.open()
    pagina = doc.new_page(width=img.shape[1] * 72 / 150, height=img.shape[0] * 72 / 150)
    pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


def test_previa_e_pdf_passam_pelo_misto_e_o_leitor_roda_uma_vez(tmp_path, monkeypatch):
    from core.pdf_io import abrir_pdf

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    contagem = []

    class Falso:
        def segmentar(self, img, cancelar=None):
            contagem.append(img.shape)
            return _resultado_falso(img.shape[1], img.shape[0])

    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: Falso())
    usados = []
    original = misto.aplicar_misto

    def espiao(img, selecao, *args, **kwargs):
        usados.append(kwargs["fora_do_texto"])
        return original(img, selecao, *args, **kwargs)

    monkeypatch.setattr(P.misto, "aplicar_misto", espiao)

    img, s = _pagina_sintetica()
    pdf = _pdf(tmp_path / "livro.pdf", img)
    p = _projeto(s, misto_so_as_letras=True, endireitar=False, cortar_bordas=False,
                 dividir_folhas=False)
    p.caminho_entrada = str(pdf)
    p.caminho_saida = str(tmp_path / "saida.pdf")
    p.qualidade_dpi = 300            # o PDF: 1800 pontos de altura
    p.paginas[0].recorte = (0.0, 0.0, 1.0, 1.0)
    p.paginas[0].angulo_manual = 0.0

    doc = abrir_pdf(str(pdf))
    try:
        previa, _ = P.renderizar_pagina(doc, p, p.paginas[0], dpi=180)   # 1080 pontos
    finally:
        doc.close()
    assert usados == [misto.FORA_REDE]
    P.processar(p)
    assert usados == [misto.FORA_REDE, misto.FORA_REDE], "o PDF nao passou pelo Misto"
    assert len(contagem) == 1, "o PDF tinha de usar as linhas que a previa achou"
    assert Path(p.caminho_saida).is_file()


# --- a marcacao automatica nao depende de a previa ter sido desenhada antes ----
#
# O defeito (verificador, 13/10/2026): a marcacao de gravura, letra e papel e
# procurada no PRIMEIRO desenho da pagina e fica guardada. Na janela o
# primeiro desenho e a previa (110 DPI); gerando o PDF direto, e o de 300. O
# detector acha areas diferentes nas duas resolucoes, e a mesma pagina saia
# (e era medida pela regra do "Para revisar") diferente conforme a ordem: nas
# 89 paginas do estudo, 24 iam e 73 certas na ordem da janela, contra 22 e 75
# direto. Agora a marcacao e sempre procurada na resolucao do PDF.

@pytest.fixture
def detector_que_depende_do_tamanho(monkeypatch):
    """Troca o detector por um falso cuja resposta DEPENDE do tamanho da
    imagem (como o de verdade): pagina grande, gravura ate o meio; pagina
    pequena, gravura ate 60%. Anota o tamanho de cada imagem que recebeu."""
    import core.detectar_regioes as D

    vistas = []

    def falso(img, **_opcoes):
        vistas.append(img.shape[:2])
        s = Selecao()
        fim = 0.5 if img.shape[0] > 1500 else 0.6
        s.acrescentar(retangulo(0.2, 0.65, fim, 0.95, tipo=GRAVURA))
        return s

    monkeypatch.setattr(D, "detectar", falso)
    return vistas


def _livro_sem_marcacao(tmp_path) -> Projeto:
    """Um livro de uma pagina, ainda sem marcacao nenhuma. O PDF e gravado so
    na primeira vez (o Windows nao deixa gravar por cima de um PDF aberto)."""
    pdf = tmp_path / "livro.pdf"
    if not pdf.exists():
        _pdf(pdf, _pagina_sintetica()[0])
    p = _projeto(Selecao(), misto_so_as_letras=True, endireitar=False, cortar_bordas=False,
                 dividir_folhas=False)
    p.caminho_entrada = str(pdf)
    p.qualidade_dpi = 300                      # o PDF: 1800 pontos de altura
    p.paginas[0].recorte = (0.0, 0.0, 1.0, 1.0)
    p.paginas[0].angulo_manual = 0.0
    assert p.paginas[0].selecao == []
    return p


def test_a_previa_procura_a_marcacao_na_resolucao_do_pdf(tmp_path, monkeypatch, leitor_falso,
                                                        detector_que_depende_do_tamanho):
    from core.pdf_io import abrir_pdf

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    vistas = detector_que_depende_do_tamanho

    # direto na resolucao do PDF (como o PDF de uma pagina nunca vista na tela)
    direto = _livro_sem_marcacao(tmp_path)
    doc = abrir_pdf(direto.caminho_entrada)
    try:
        P.renderizar_pagina(doc, direto, direto.paginas[0], dpi=300)
        assert vistas == [(1800, 1400)]

        # na ordem da janela: a previa primeiro, depois o desenho do tamanho do PDF
        janela = _livro_sem_marcacao(tmp_path)
        vistas.clear()
        previa, _ = P.renderizar_pagina(doc, janela, janela.paginas[0], dpi=110)
        assert vistas == [(1800, 1400)], "a previa tinha de procurar na pagina do tamanho do PDF"
        assert max(previa.shape[:2]) < 800, "e a previa continua pequena"
        P.renderizar_pagina(doc, janela, janela.paginas[0], dpi=300)
        assert vistas == [(1800, 1400)], "com a marcacao guardada, nao procura de novo"
    finally:
        doc.close()
    assert janela.paginas[0].selecao == direto.paginas[0].selecao
    assert janela.paginas[0].gravura_feita_com == direto.paginas[0].gravura_feita_com != ""
    # e a regra mediu a mesma coisa nos dois caminhos
    assert janela.paginas[0].alertas == direto.paginas[0].alertas
    assert janela.paginas[0].faixa_na_beirada == direto.paginas[0].faixa_na_beirada is not None


def test_a_copia_dos_cartoes_nao_procura_na_resolucao_do_pdf(tmp_path, monkeypatch, leitor_falso,
                                                            detector_que_depende_do_tamanho):
    """Os cartoes de filtro desenham uma copia da pagina e jogam a marcacao
    dela fora: procurar na pagina grande ali seria tempo perdido."""
    from core.pdf_io import abrir_pdf

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    p = _livro_sem_marcacao(tmp_path)
    doc = abrir_pdf(p.caminho_entrada)
    try:
        P.renderizar_com_filtro(doc, p, p.paginas[0], MELHORAR, dpi=110)
    finally:
        doc.close()
    assert all(max(forma) < 800 for forma in detector_que_depende_do_tamanho)
    assert p.paginas[0].selecao == [], "a pagina de verdade nao muda"


def test_se_a_procura_grande_falha_a_previa_procura_como_antes(tmp_path, monkeypatch, leitor_falso,
                                                             detector_que_depende_do_tamanho):
    from core.pdf_io import abrir_pdf

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))

    def quebrada(*args, **kwargs):
        raise RuntimeError("de proposito")

    de_verdade = P._preparar_metade_e_geometria
    chamadas = []

    def preparar(img, *args, **kwargs):
        chamadas.append(img.shape[:2])
        if len(chamadas) == 1:                 # a primeira e a da pagina grande
            return quebrada()
        return de_verdade(img, *args, **kwargs)

    monkeypatch.setattr(P, "_preparar_metade_e_geometria", preparar)
    p = _livro_sem_marcacao(tmp_path)
    doc = abrir_pdf(p.caminho_entrada)
    try:
        previa, _ = P.renderizar_pagina(doc, p, p.paginas[0], dpi=110)
    finally:
        doc.close()
    assert previa is not None and p.paginas[0].selecao != [], "a previa saiu e a marcacao existe"
    assert max(detector_que_depende_do_tamanho[-1]) < 800


# --- core.linhas_do_texto ------------------------------------------------------

class _LeitorContador:
    def __init__(self, resultado=None):
        self.vezes = 0
        self.tamanhos = []
        self.resultado = resultado

    def segmentar(self, img, cancelar=None):
        self.vezes += 1
        self.tamanhos.append(img.shape[:2])
        if self.resultado is not None:
            return self.resultado
        return _resultado_falso(img.shape[1], img.shape[0])


def test_as_linhas_ficam_guardadas_por_pagina(monkeypatch):
    leitor = _LeitorContador()
    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: leitor)
    grande = np.full((3000, 2000, 3), 230, np.uint8)
    a = linhas_do_texto.linhas_da_pagina(grande, chave="p1")
    b = linhas_do_texto.linhas_da_pagina(grande, chave="p1")
    assert leitor.vezes == 1 and len(a) == len(b) == 1
    linhas_do_texto.linhas_da_pagina(grande, chave="p2")
    assert leitor.vezes == 2
    linhas_do_texto.linhas_da_pagina(grande, chave=None)
    assert leitor.vezes == 3, "sem chave, nao guarda"
    # a pagina vai ao leitor com o lado maior em LADO_DO_LEITOR
    assert max(leitor.tamanhos[0]) == linhas_do_texto.LADO_DO_LEITOR


def test_imagem_mais_nitida_acha_de_novo_e_a_menos_nitida_usa_a_guardada(monkeypatch):
    leitor = _LeitorContador()
    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: leitor)
    arrasto = np.full((340, 240, 3), 230, np.uint8)       # o arrasto do medidor, 55 DPI
    previa = np.full((680, 480, 3), 230, np.uint8)        # pagina pequena, 110 DPI
    pdf = np.full((1852, 1331, 3), 230, np.uint8)         # a mesma, 300 DPI
    linhas_do_texto.linhas_da_pagina(previa, chave="p1")
    linhas_do_texto.linhas_da_pagina(arrasto, chave="p1")
    linhas_do_texto.linhas_da_pagina(previa, chave="p1")
    assert leitor.vezes == 1, "a previa de novo e o arrasto usam a guardada"
    linhas_do_texto.linhas_da_pagina(pdf, chave="p1")
    assert leitor.vezes == 2, "o PDF de pagina pequena acha de novo, mais nitido"
    linhas_do_texto.linhas_da_pagina(previa, chave="p1")
    linhas_do_texto.linhas_da_pagina(pdf, chave="p1")
    assert leitor.vezes == 2, "e depois a mais nitida serve para todas"
    # a do arrasto, achada primeiro, nao serve para a previa
    linhas_do_texto.linhas_da_pagina(arrasto, chave="p2")
    linhas_do_texto.linhas_da_pagina(previa, chave="p2")
    assert leitor.vezes == 4


def test_leitor_que_falha_da_lista_vazia_e_nao_guarda(monkeypatch):
    leitor = _LeitorContador(ResultadoOCR("doctr", None, motivo="sem modelo"))
    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: leitor)
    grande = np.full((3000, 2000, 3), 230, np.uint8)
    assert linhas_do_texto.linhas_da_pagina(grande, chave="p1") == []
    assert linhas_do_texto.linhas_da_pagina(grande, chave="p1") == []
    assert leitor.vezes == 2

    def quebra():
        raise RuntimeError("caiu")

    monkeypatch.setattr(linhas_do_texto, "_detector", quebra)
    assert linhas_do_texto.linhas_da_pagina(grande, chave="p2") == []


def test_gancho_do_kraken_desligado_de_fabrica_e_soma_quando_ligado(monkeypatch):
    assert linhas_do_texto.SEGUNDA_OPINIAO_DO_KRAKEN is False
    doctr, kraken = _LeitorContador(), _LeitorContador(
        ResultadoOCR("kraken", [LinhaOCR(caixa(10, 500, 300, 520))], largura=2000, altura=3000))
    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: doctr)
    monkeypatch.setattr(linhas_do_texto, "_kraken", lambda: kraken)
    grande = np.full((3000, 2000, 3), 230, np.uint8)
    assert len(linhas_do_texto.linhas_da_pagina(grande)) == 1 and kraken.vezes == 0
    monkeypatch.setattr(linhas_do_texto, "SEGUNDA_OPINIAO_DO_KRAKEN", True)
    resultados = linhas_do_texto.linhas_da_pagina(grande)
    assert [r.motor for r in resultados] == ["doctr", "kraken"]
    assert kraken.tamanhos == [(3000, 2000)], "o Kraken recebe a pagina inteira"


def test_a_chave_das_linhas_muda_com_o_corte_e_nao_com_o_filtro(tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4 teste")
    p = _projeto(Selecao())
    p.caminho_entrada = str(pdf)
    pagina = p.paginas[0]
    antes = P._chave_das_linhas(p, pagina)
    pagina.forca_preto = 90
    pagina.filtro = MELHORAR
    assert P._chave_das_linhas(p, pagina) == antes
    pagina.recorte = (0.1, 0.1, 0.9, 0.9)
    assert P._chave_das_linhas(p, pagina) != antes
    pagina.recorte = None
    pagina.angulo_manual = 1.5
    assert P._chave_das_linhas(p, pagina) != antes
    p.caminho_entrada = str(tmp_path / "nao-existe.pdf")
    assert P._chave_das_linhas(p, pagina) is None


def test_alguma_precisa_das_linhas():
    img, s = _pagina_sintetica()
    p = _projeto(s)
    assert not misto.alguma_precisa_das_linhas(p)
    p.misto_so_as_letras = True
    assert misto.alguma_precisa_das_linhas(p)
    p.misto_fora_do_texto = misto.FORA_TUDO
    assert not misto.alguma_precisa_das_linhas(p), "a B nao usa o leitor"
    p.paginas[0].misto_fora_do_texto = misto.FORA_APAGAR
    assert misto.alguma_precisa_das_linhas(p)
    p.limpar = False
    assert not misto.alguma_precisa_das_linhas(p)


def test_aquecer_abre_o_leitor_uma_vez_numa_thread(monkeypatch):
    import threading
    import time

    class Falso:
        def __init__(self):
            self.aberto = False
            self.vezes = 0
            self._tranca = threading.RLock()
            self.thread = None

        def _abrir(self):
            self.vezes += 1
            self.thread = threading.current_thread().name
            time.sleep(0.05)
            self.aberto = True

    falso = Falso()
    monkeypatch.setattr(linhas_do_texto, "_DETECTOR", falso)
    monkeypatch.setattr(linhas_do_texto, "_detector", lambda: falso)
    linhas_do_texto.aquecer_em_segundo_plano()
    linhas_do_texto.aquecer_em_segundo_plano()          # ja abrindo: nada
    for _ in range(100):
        if falso.aberto and not linhas_do_texto._AQUECENDO:
            break
        time.sleep(0.02)
    assert falso.vezes == 1 and falso.thread == "aquecer-leitor-de-texto"
    linhas_do_texto.aquecer_em_segundo_plano()          # ja aberto: nada
    time.sleep(0.05)
    assert falso.vezes == 1
