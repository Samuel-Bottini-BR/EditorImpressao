"""D-618 (Samuel, 04/11/2026): numa folha já dividida, girar gira só a página da tela.

Palavras dele (prints a-70 a a-73, Gradus Primus página 14, ferramenta Cortar as bordas): "quando ele
gira a pagina ele faz ela caber no A4, ele deveria girar o conteudo só que é da pagina cortada, mas ele
gira a pagina verdadeira do scan. tanto que quando você vai girando ele cai na folha branca. Ele gira as
duas folhas ao mesmo tempo, faz uma confusão com as paginas."

Livro de decisões: "Numa folha já dividida, o giro de ¼ e a meia volta ("Girar a folha", botões do
canto, Ctrl+Seta) giram só o conteúdo da página que está na tela, já cortada; a outra página da folha
e a linha da divisão não mudam." Folha inteira (não dividida): como antes (D-035, D-367).

A causa (relatorios/girar-pagina/): o giro morava só na folha (o scan inteiro) e vinha antes de
dividir; a folha girada era dividida de novo pela mesma linha, e cada "página" virava meia folha
deitada, com pedaços das duas (a-70); com meia volta, a página 14 mostrava a 13, branca (a-71).

Os testes de reversão (test_reversao_d618_*) falham no código de antes (obra-2026-10-26, ce086bb6):
lá o botão gira a FOLHA (folha.rotacao muda) e a outra página muda junto.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import girar, pipeline  # noqa: E402
from core.endireitar import girar_90  # noqa: E402
from core.dividir_a_mao import campos_para_dividir  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402

DPI = 150
DPI_MEDIDA = 60


# --- o livro de teste: duas folhas abertas, cada página com uma marca diferente -----------------

def _pagina_com_marca(lado: str, largura: int = 600, altura: int = 840) -> np.ndarray:
    """Uma página branca com uma marca preta que diz qual página é e para que lado está:
    a esquerda tem um quadrado no canto de cima à esquerda; a direita, uma barra em pé perto
    da beirada esquerda dela, do alto até a metade."""
    img = np.full((altura, largura, 3), 245, np.uint8)
    if lado == "esquerda":
        img[60:200, 60:200] = 20
    else:
        img[60:altura // 2, 80:130] = 20
    return img


def _folha_aberta() -> np.ndarray:
    return np.concatenate([_pagina_com_marca("esquerda"), _pagina_com_marca("direita")], axis=1)


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI_MEDIDA, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


# --- a janela ---------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.avisos = []
    janela.avisar = lambda mensagem, titulo="": janela.avisos.append(mensagem)
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _livro_com_a_folha_1_dividida(janela, tmp_path):
    """Abre o livro (duas folhas abertas), divide a folha 1 na dobra (o "dividir esta", sem
    a DLL), escolhe Cortar as bordas e vai à página 2 (a da direita da folha 1)."""
    from ui.tela_conferir import FERRAMENTA_CORTAR

    janela.abrir_livro(_pdf(tmp_path / "aberto.pdf", [_folha_aberta(), _folha_aberta()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("dividir", "folha", [0], campos_para_dividir(projeto, 0, 0.5), "Dividir")
    assert projeto.folhas[0].dividir and len(projeto.paginas) == 3
    assert [p.metade for p in projeto.paginas] == ["esquerda", "direita", "inteira"]
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(1)
    assert tela.indice_pagina == 1 and tela.indice_folha == 0
    return tela, projeto


def _como_o_cortar_mostra(projeto, indice: int) -> np.ndarray:
    """A página como a ferramenta Cortar a mostra (girada e dividida, sem cortar), pela conta do
    programa (core/pipeline.preparar_para_recorte)."""
    pagina = projeto.paginas[indice]
    folha = projeto.folhas[pagina.folha]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img = pagina_para_array(doc, folha.indice, DPI_MEDIDA)
    finally:
        doc.close()
    return pipeline.preparar_para_recorte(img, folha, pagina, projeto)


def _marca_em_pe_perto_da_esquerda(img: np.ndarray) -> bool:
    """A marca da página da direita, como ela é: barra em pé (mais alta que larga), no lado
    esquerdo da página e na metade de cima."""
    cinza = img.mean(axis=2)
    ys, xs = np.nonzero(cinza < 100)
    if len(xs) == 0:
        return False
    alta = (ys.max() - ys.min()) > 2 * (xs.max() - xs.min())
    return bool(alta and xs.mean() < img.shape[1] * 0.4 and ys.mean() < img.shape[0] * 0.5)


# --- reversão: o caminho do Samuel (Propriedades, ¼ à esquerda) ---------------------------------

def test_reversao_d618_quarto_a_esquerda_gira_so_a_pagina_da_tela(janela, tmp_path):
    """D-618 / prints a-70 e a-71: na página da direita de uma folha dividida, "¼ à esquerda" do
    Propriedades ("só esta folha") deixa SÓ esta página deitada, inteira (a mesma imagem, girada);
    a página da esquerda, a linha da divisão e o giro da folha não mudam; é uma ação só, e o
    Ctrl+Z volta. No código de antes a folha inteira girava (folha.rotacao 270) e a página virava
    meia folha deitada com pedaços das duas (a outra página mudava junto): falha lá."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    esquerda_antes = _como_o_cortar_mostra(projeto, 0)
    direita_antes = _como_o_cortar_mostra(projeto, 1)
    assert _marca_em_pe_perto_da_esquerda(direita_antes)
    feitas = len(tela.acoes.feitas)
    assert tela.barra_girar.alcance() == girar.ALCANCE_ESTA

    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()

    assert projeto.folhas[0].rotacao == 0, "a folha (o scan inteiro) não gira"
    assert projeto.folhas[0].posicao_corte == pytest.approx(0.5), "a linha não muda"
    assert len(tela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"
    assert tela.acoes.feitas[-1].descricao == "Girar ¼ à esquerda: a página 2"
    direita = _como_o_cortar_mostra(projeto, 1)
    assert direita.shape[:2] == direita_antes.shape[1::-1], "a página inteira, deitada"
    assert np.array_equal(direita, girar_90(direita_antes, girar.GIRO_ESQUERDA)), \
        "o conteúdo DESTA página, girado ¼ à esquerda"
    assert np.array_equal(_como_o_cortar_mostra(projeto, 0), esquerda_antes), \
        "a outra página da folha fica igual"

    tela.desfazer()
    assert projeto.paginas[1].giro_da_pagina == 0
    assert np.array_equal(_como_o_cortar_mostra(projeto, 1), direita_antes), "o Ctrl+Z volta"
    tela.refazer()
    assert np.array_equal(_como_o_cortar_mostra(projeto, 1),
                          girar_90(direita_antes, girar.GIRO_ESQUERDA))


def test_reversao_d618_girar_duas_vezes_nao_cai_na_pagina_branca(janela, tmp_path):
    """Print a-71/a-72 ("quando você vai girando ele cai na folha branca"): duas vezes "¼ à
    esquerda" = a MESMA página de cabeça para baixo, nunca a outra página da folha. No código de
    antes a página da direita mostrava a da esquerda (a folha de cabeça para baixo, dividida pela
    mesma linha): falha lá."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    direita_antes = _como_o_cortar_mostra(projeto, 1)
    for _ in range(2):
        tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    depois = _como_o_cortar_mostra(projeto, 1)
    assert _marca_em_pe_perto_da_esquerda(girar_90(depois, 180)), \
        "é a página da direita (a marca dela), de cabeça para baixo - não a outra página"
    assert np.array_equal(depois, girar_90(direita_antes, 180))


@pytest.mark.parametrize("como", ["canto", "tecla", "meia_volta"])
def test_d618_canto_ctrl_seta_e_meia_volta_tambem_giram_so_a_pagina(janela, tmp_path, como):
    """D-618: os botões do canto (D-053), o Ctrl+Seta do menu Página (D-361) e a meia volta giram
    só a página da tela, numa folha dividida."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    esquerda_antes = _como_o_cortar_mostra(projeto, 0)
    direita_antes = _como_o_cortar_mostra(projeto, 1)
    if como == "canto":
        tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)     # o canto gira só esta (D-053)
        tela.girar_do_canto.botoes_de_giro[girar.GIRO_DIREITA].click()
        giro = girar.GIRO_DIREITA
    elif como == "tecla":
        janela.menu.acoes["girar_esquerda"].trigger()
        giro = girar.GIRO_ESQUERDA
    else:
        tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
        giro = girar.GIRO_MEIA_VOLTA
    assert projeto.folhas[0].rotacao == 0
    assert np.array_equal(_como_o_cortar_mostra(projeto, 1), girar_90(direita_antes, giro))
    assert np.array_equal(_como_o_cortar_mostra(projeto, 0), esquerda_antes)


# --- o que já era escolhido e testado continua (D-605) ------------------------------------------

def test_d618_folha_inteira_continua_girando_a_folha(janela, tmp_path):
    """Folha NÃO dividida (a folha 2 do livro): "¼ à esquerda" gira a folha, como antes (D-035,
    tests/test_girar_na_tela.py); como uma foto ("girar - sim", 04/11: os testes abaixo)."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.ir_para_pagina(2)
    assert tela.indice_folha == 1
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert projeto.folhas[1].rotacao == girar.GIRO_ESQUERDA
    assert projeto.paginas[2].giro_da_pagina == 0
    assert projeto.folhas[0].rotacao == 0 and projeto.paginas[1].giro_da_pagina == 0


def test_d618_folha_inteira_girada_mede_a_proporcao_na_previa_e_no_pdf(janela, tmp_path):
    """Correção do Samuel na D-618 (04/11, recado da gerente): "hoje quando gira a folha altera a
    proporção dela para girar ela". Medida, sem mudar nada: a folha inteira (larga, 29,7 x 21)
    girada ¼ fica 21 x 29,7 - a proporção exatamente invertida, sem esticar nem apertar - na
    imagem da ferramenta Cortar e na página do PDF gravado; e o conteúdo é a mesma imagem,
    girada. Ele confirmou a proposta ("girar - sim": "como girar uma foto [...] A proporção não
    muda"); sem corte nem tamanho escolhido isto já valia antes (os casos com corte e tamanho são
    os testes de reversão abaixo)."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.ir_para_pagina(2)

    def gerar(nome):
        copia = copy.copy(projeto)
        copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
        return _paginas_do_pdf(pipeline.processar(copia))[2]

    base_antes, pdf_antes = _como_o_cortar_mostra(projeto, 2), gerar("inteira_antes")
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    base_depois, pdf_depois = _como_o_cortar_mostra(projeto, 2), gerar("inteira_depois")

    def proporcao(img):
        return img.shape[1] / img.shape[0]

    assert proporcao(base_depois) == pytest.approx(1 / proporcao(base_antes), rel=0.01)
    assert proporcao(pdf_depois) == pytest.approx(1 / proporcao(pdf_antes), rel=0.01)
    assert np.array_equal(base_depois, girar_90(base_antes, girar.GIRO_ESQUERDA))


def _gerar_pagina(projeto, tmp_path, nome, indice):
    copia = copy.copy(projeto)
    copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(pipeline.processar(copia))[indice]


def _parecidas(a: np.ndarray, b: np.ndarray, tolerancia: float = 4.0) -> bool:
    """Mesma imagem (a mesma folha desenhada duas vezes muda um ponto ou dois de tamanho)."""
    if abs(a.shape[0] - b.shape[0]) > 2 or abs(a.shape[1] - b.shape[1]) > 2:
        return False
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    return float(np.abs(a[:h, :w].astype(int) - b[:h, :w].astype(int)).mean()) < tolerancia


def test_reversao_d618_folha_inteira_com_corte_a_mao_gira_como_foto(janela, tmp_path):
    """"girar - sim" (Samuel, 04/11/2026: "girar a folha inteira é como girar uma foto. A folha
    larga, com as duas páginas, fica em pé, inteira, sem esticar, sem apertar e sem cortar nada").
    Folha inteira com um corte à mão (só a página da esquerda dela): girar ¼ à esquerda deixa no
    PDF o MESMO pedaço do papel, girado - a proporção exatamente invertida. No código de antes o
    corte ficava com as mesmas frações e cortava outro pedaço da folha deitada (a metade de cima
    dela, com pedaços das duas páginas): falha lá. O Ctrl+Z devolve o corte."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.ir_para_pagina(2)
    corte = [0.02, 0.05, 0.46, 0.9]
    tela._registrar("recortar", "pagina", [2], {"recorte": corte}, "Corte")
    antes = _gerar_pagina(projeto, tmp_path, "corte_antes", 2)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert projeto.folhas[1].rotacao == girar.GIRO_ESQUERDA
    depois = _gerar_pagina(projeto, tmp_path, "corte_depois", 2)
    assert depois.shape[1] / depois.shape[0] == pytest.approx(antes.shape[0] / antes.shape[1], rel=0.02)
    assert _parecidas(depois, girar_90(antes, girar.GIRO_ESQUERDA)), "o mesmo pedaço, girado"
    tela.desfazer()
    assert list(projeto.paginas[2].recorte) == pytest.approx(corte)
    assert projeto.folhas[1].rotacao == 0


def test_reversao_d618_folha_inteira_com_tamanho_escolhido_nao_aperta(janela, tmp_path):
    """"girar - sim": "sem apertar". Folha inteira (larga) com o tamanho de folha escolhido no
    "tamanho..." (29,7 x 21 cm, deitada como ela): girar ¼ deixa a folha em pé, 21 x 29,7, com o
    conteúdo do mesmo tamanho, girado. No código de antes o tamanho escolhido ficava deitado e a
    folha em pé era apertada dentro dele (a proporção da página do PDF não mudava): falha lá."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.ir_para_pagina(2)
    tela._registrar("tamanho", "pagina", [2], {"tamanho_folha_cm": [29.7, 21.0]}, "Tamanho")
    antes = _gerar_pagina(projeto, tmp_path, "tamanho_antes", 2)
    assert antes.shape[1] > antes.shape[0]
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    depois = _gerar_pagina(projeto, tmp_path, "tamanho_depois", 2)
    assert depois.shape[1] / depois.shape[0] == pytest.approx(antes.shape[0] / antes.shape[1], rel=0.02)
    assert tuple(projeto.paginas[2].tamanho_folha_cm) == pytest.approx((21.0, 29.7))
    assert _parecidas(depois, girar_90(antes, girar.GIRO_ESQUERDA))


def test_d618_conta_do_que_gira_junto_com_a_pagina():
    """core/girar.campos_da_pagina_que_giram_junto: o corte, o tamanho escolhido e o lugar do
    conteúdo giram como numa foto; página sem nada disso não leva campo nenhum."""
    from modelos import ConfigPagina

    vazia = ConfigPagina(indice=0, folha=0)
    assert girar.campos_da_pagina_que_giram_junto(vazia, girar.GIRO_DIREITA) == {}
    p = ConfigPagina(indice=0, folha=0, recorte=(0.1, 0.2, 0.3, 0.4), tamanho_folha_cm=(21.0, 29.7),
                     conteudo_deslocamento=(0.1, -0.05))
    c = girar.campos_da_pagina_que_giram_junto(p, girar.GIRO_DIREITA)
    assert c["recorte"] == pytest.approx([1 - 0.6, 0.1, 0.4, 0.3])
    assert c["tamanho_folha_cm"] == [29.7, 21.0]
    assert c["conteudo_deslocamento"] == pytest.approx([0.05, 0.1])
    meia = girar.campos_da_pagina_que_giram_junto(p, girar.GIRO_MEIA_VOLTA)
    assert "tamanho_folha_cm" not in meia
    assert meia["conteudo_deslocamento"] == pytest.approx([-0.1, 0.05])


def test_d618_juntar_e_dividir_noutra_linha_nao_herda_o_giro_da_metade(janela, tmp_path):
    """Achado no teste antigo do recomeço (04/11): girar a página da esquerda, "não dividir esta"
    e dividir de novo NOUTRA linha fazia as duas metades novas nascerem giradas (a página inteira
    herdava o giro da metade, e as metades novas o da inteira). Agora o giro só fica na metade que
    a pessoa girou: juntar e "dividir esta" na mesma linha devolve as metades como estavam (a da
    esquerda girada); partir noutra linha dá metades sem giro."""
    from core.dividir_a_mao import campos_para_juntar

    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.ir_para_pagina(0)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert [p.giro_da_pagina for p in projeto.paginas if p.folha == 0] == [270, 0]
    tela._registrar("dividir", "folha", [0], campos_para_juntar(projeto, 0), "Juntar")
    assert projeto.paginas[0].giro_da_pagina == 0, "a página inteira não herda o giro da metade"
    tela._registrar("dividir", "folha", [0], campos_para_dividir(projeto, 0), "Dividir de novo")
    assert [p.giro_da_pagina for p in projeto.paginas if p.folha == 0] == [270, 0]
    tela._registrar("dividir", "folha", [0], campos_para_juntar(projeto, 0), "Juntar")
    tela._registrar("dividir", "folha", [0], campos_para_dividir(projeto, 0, 0.45), "Noutra linha")
    assert [p.giro_da_pagina for p in projeto.paginas if p.folha == 0] == [0, 0]


def test_d618_no_dividir_em_duas_lado_a_lado_a_folha_inteira_gira(janela, tmp_path):
    """No Dividir com "Duas lado a lado" a tela mostra a FOLHA inteira com a linha (D-601): ali o
    giro continua sendo o da folha, como antes (o que aparece na tela é a folha). Ressalva escrita
    no relatório."""
    from ui.tela_conferir import DUAS, FERRAMENTA_DIVIDIR

    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
    tela.definir_mostrar(DUAS)
    assert tela._pagina_que_gira_sozinha() is None
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert projeto.folhas[0].rotacao == girar.GIRO_ESQUERDA


def test_d618_no_dividir_em_uma_pagina_gira_so_a_metade_da_tela(janela, tmp_path):
    """No Dividir com "Uma página" (D-601) a tela mostra só a metade: o giro é só dela."""
    from ui.tela_conferir import FERRAMENTA_DIVIDIR, UMA

    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
    tela.definir_mostrar(UMA)
    tela.ir_para_pagina(1)
    assert tela._pagina_que_gira_sozinha() == 1
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert projeto.folhas[0].rotacao == 0
    assert projeto.paginas[1].giro_da_pagina == girar.GIRO_ESQUERDA


def test_d618_d636_aplicar_em_todas_numa_folha_dividida_gira_as_paginas(janela, tmp_path):
    """Até 05/11 esta prova dizia "continua como antes até o Samuel responder" (pergunta 1 do
    ONDE-PAREI; escrita nesta mesma tarefa, provisória). Ele respondeu (D-636, 05/11/2026: "1- pode
    ser [...]"): numa folha dividida o "aplicar em" com mais de uma página gira PÁGINAS, cada uma
    sozinha; nenhuma folha gira. A folha 2 (inteira) fica como está. Mais provas em
    tests/test_decisoes_girar_paginas_aplicar_em.py."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    # D-640 (06/11; troca autorizada pelo Samuel, Central girar-capa-testes-antigos, 07/11): "todas as páginas" gira também a folha 2 (inteira), como a página da vez
    assert [f.rotacao for f in projeto.folhas] == [0, 90]
    assert [p.giro_da_pagina for p in projeto.paginas] == [90, 90, 0]


# --- o PDF de saída ----------------------------------------------------------------------------

def test_d618_o_pdf_sai_com_so_a_pagina_girada(janela, tmp_path):
    """O PDF gravado sai com a página 2 deitada (a mesma imagem que sairia sem o giro, girada) e
    as páginas 1 e 3 iguais às de antes do giro."""
    tela, projeto = _livro_com_a_folha_1_dividida(janela, tmp_path)

    def gerar(nome):
        copia = copy.copy(projeto)
        copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
        return _paginas_do_pdf(pipeline.processar(copia))

    antes = gerar("antes")
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    depois = gerar("depois")
    assert len(antes) == len(depois) == 3
    assert antes[1].shape[0] > antes[1].shape[1] and depois[1].shape[1] > depois[1].shape[0]
    girada = girar_90(antes[1], girar.GIRO_ESQUERDA)
    assert girada.shape == depois[1].shape
    assert np.abs(girada.astype(int) - depois[1].astype(int)).mean() < 3
    for i in (0, 2):
        assert antes[i].shape == depois[i].shape
        assert np.abs(antes[i].astype(int) - depois[i].astype(int)).mean() < 1


# --- as contas (core/girar) e o projeto antigo --------------------------------------------------

@pytest.mark.parametrize("giro", [girar.GIRO_DIREITA, girar.GIRO_ESQUERDA, girar.GIRO_MEIA_VOLTA])
def test_d618_o_corte_a_mao_gira_junto_e_fica_no_mesmo_pedaco(giro):
    """O corte a mão (fração da página) depois do giro corta o MESMO pedaço do papel na página
    girada; quatro quartos voltam ao corte de antes."""
    img = np.zeros((80, 60), np.uint8)
    img[10:30, 5:25] = 255
    recorte = (5 / 60, 10 / 80, 20 / 60, 20 / 80)

    def cortar(imagem, r):
        h, w = imagem.shape[:2]
        x, y, cw, ch = r
        return imagem[round(y * h):round((y + ch) * h), round(x * w):round((x + cw) * w)]

    novo = girar.recorte_girado(recorte, giro)
    assert np.array_equal(cortar(girar_90(img, giro), novo), girar_90(cortar(img, recorte), giro))
    volta = recorte
    for _ in range(4):
        volta = girar.recorte_girado(volta, girar.GIRO_DIREITA)
    assert volta == pytest.approx(list(recorte), abs=1e-5)     # guardado com 6 casas
    assert girar.recorte_girado(None, giro) is None


def test_d618_projeto_antigo_sem_o_campo_abre_igual():
    """Projeto gravado antes da D-618 (página sem "giro_da_pagina") abre com 0: a página sai
    igual. A página inteira nunca usa o giro da página (quem gira é a folha)."""
    from modelos import ConfigFolha, ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=0, dividir=True)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, metade="esquerda"),
                       ConfigPagina(indice=1, folha=0, metade="direita")]
    dados = projeto.para_dicionario()
    for p in dados["paginas"]:
        p.pop("giro_da_pagina")
    aberto = Projeto.de_dicionario(dados)
    assert [p.giro_da_pagina for p in aberto.paginas] == [0, 0]
    inteira = ConfigPagina(indice=0, folha=0, metade="inteira", giro_da_pagina=90)
    assert girar.giro_da_pagina(ConfigFolha(indice=0, dividir=False), inteira) == 0


def test_d618_a_geometria_das_zonas_de_antes_continua_igual():
    """A geometria anotada das zonas (core/zonas_na_folha) só ganha a chave nova com o giro da
    página: a de uma página sem giro é a mesma de antes da D-618 (as zonas não andam ao abrir)."""
    from core.zonas_na_folha import _matriz_folha_para_pagina, geometria_do_desenho, mesma_geometria

    sem = geometria_do_desenho(1.4, 0, 0.5, "direita", None, 0.0)
    assert "giro_pagina" not in sem
    com = geometria_do_desenho(1.4, 0, 0.5, "direita", None, 0.0, giro_pagina=270)
    assert com["giro_pagina"] == 270 and not mesma_geometria(sem, com)
    # um ponto da folha vai para o mesmo lugar que a imagem girada leva: (u, v) -> (v, 1 - u)
    ponto = np.array([0.8, 0.25, 1.0])
    u, v, _ = _matriz_folha_para_pagina(sem) @ ponto
    u2, v2, _ = _matriz_folha_para_pagina(com) @ ponto
    assert (u2, v2) == pytest.approx((v, 1 - u))
