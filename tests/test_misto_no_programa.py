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
    - o aviso "Tinta forte fora do texto" entra acima do limite e sai quando
      a pagina deixa o Misto A/C;
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
    assert analise.TINTA_FORTE_FORA_DO_TEXTO not in p.paginas[0].alertas


# --- "Para revisar" sozinho ---------------------------------------------------

def test_muita_tinta_forte_fora_manda_para_revisar(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    pagina.revisada = True
    P._filtrar(p, pagina, img.copy())
    assert pagina.alertas[0] == analise.TINTA_FORTE_FORA_DO_TEXTO
    assert pagina.precisa_revisao and not pagina.revisada
    # "esta bom assim" vale: desenhar de novo nao volta a pedir
    pagina.revisada = True
    P._filtrar(p, pagina, img.copy())
    assert pagina.revisada and pagina.alertas.count(analise.TINTA_FORTE_FORA_DO_TEXTO) == 1


def test_pouca_tinta_forte_fora_nao_manda(leitor_falso):
    img, s = _pagina_sintetica()
    img[380:480, 280:400] = PAPEL                  # sem a nota
    p = _projeto(s, misto_so_as_letras=True)
    P._filtrar(p, p.paginas[0], img.copy())
    assert analise.TINTA_FORTE_FORA_DO_TEXTO not in p.paginas[0].alertas


def test_o_aviso_vale_tambem_no_c(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_APAGAR)
    P._filtrar(p, p.paginas[0], img.copy())
    assert analise.TINTA_FORTE_FORA_DO_TEXTO in p.paginas[0].alertas


@pytest.mark.parametrize("como_sair", ["b", "desligar", "outro_filtro"])
def test_o_aviso_sai_quando_a_pagina_deixa_o_misto_a(leitor_falso, como_sair):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert analise.TINTA_FORTE_FORA_DO_TEXTO in pagina.alertas
    if como_sair == "b":
        pagina.misto_fora_do_texto = misto.FORA_TUDO
    elif como_sair == "desligar":
        pagina.misto_so_as_letras = False
    else:
        pagina.filtro = MELHORAR
    # sem desenhar (o que a tela chama a cada atualizacao)...
    P.acertar_alertas_do_fundo(p, [pagina])
    assert analise.TINTA_FORTE_FORA_DO_TEXTO not in pagina.alertas
    # ...e desenhando
    pagina.alertas.insert(0, analise.TINTA_FORTE_FORA_DO_TEXTO)
    P._filtrar(p, pagina, img.copy())
    assert analise.TINTA_FORTE_FORA_DO_TEXTO not in pagina.alertas


def test_acertar_sem_desenhar_nao_tira_o_aviso_de_quem_continua_no_a(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    P._filtrar(p, p.paginas[0], img.copy())
    P.acertar_alertas_do_fundo(p)
    assert analise.TINTA_FORTE_FORA_DO_TEXTO in p.paginas[0].alertas


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
