"""Item 1.1 ligado ao programa: "tirar o fundo" de PDF com camadas.

Decisao do Samuel (29/09/2026): "automatico quando o programa detectar
camadas, com botao para desligar por livro; pagina duvidosa sai marcada
'conferir'." Decisao da gerente (a rever pelo Samuel): com o botao ligado, a
pagina que core/camadas.py deixa sem o fundo usa esse resultado NO LUGAR do
filtro; a pagina em "Original" fica como esta; a pagina deixada intacta segue
o filtro.

O que se cobra aqui (teste de maquina):

    - a deteccao ao abrir (analise e tela) e o campo novo do projeto, com o
      projeto antigo, salvo sem ele, abrindo normalmente;
    - a caixinha "Tirar o fundo sozinho" so aparece em PDF com camadas;
    - previa e PDF usam o "tirar o fundo" com o botao ligado, e nao usam com
      ele desligado, em "Original", em PDF sem camadas ou em pagina intacta;
    - a previa e o PDF saem iguais, ponto por ponto;
    - a pagina duvidosa ganha o alerta "conferir", e o perde quando deixa de
      usar o "tirar o fundo".

Os PDFs com camadas sao os de tests/test_camadas.py (montados na hora, como
os do Internet Archive). O detector de figuras e trocado por um que nao acha
nada (rapido, sem o modelo), como la.
"""

from __future__ import annotations

import json

import cv2
import fitz
import numpy as np
import pytest

from core import analise, camadas, pipeline
from core.filtros import MAGICO_PRO, ORIGINAL, PRETO_E_BRANCO
from modelos import Projeto
from tests.test_camadas import (
    ALTURA_CIMA,
    LARGURA_CIMA,
    PAPEL_RGB,
    fundo_com_escrita_fraca,
    pdf_com_camadas,
    pdf_comum,
    sem_figuras,
)


# --- montar -----------------------------------------------------------------


@pytest.fixture(autouse=True)
def detector_sem_figuras(monkeypatch):
    """O detector de figuras do core/camadas.py nao acha nada (rapido)."""
    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)


@pytest.fixture
def espiao(monkeypatch):
    """Conta as chamadas do "tirar o fundo" e do filtro, sem mudar o que fazem."""
    contagem = {"tirar_fundo": 0, "filtro": 0}
    original_tirar = camadas.tirar_fundo
    original_filtro = pipeline.aplicar_filtro_com_selecao

    def tirar(*args, **kwargs):
        contagem["tirar_fundo"] += 1
        return original_tirar(*args, **kwargs)

    def filtrar(*args, **kwargs):
        contagem["filtro"] += 1
        return original_filtro(*args, **kwargs)

    monkeypatch.setattr(camadas, "tirar_fundo", tirar)
    monkeypatch.setattr(pipeline, "aplicar_filtro_com_selecao", filtrar)
    return contagem


def _gravar(doc: fitz.Document, caminho) -> str:
    doc.save(caminho)
    doc.close()
    return str(caminho)


def _pdf_camadas(tmp_path, nome="camadas.pdf", **kw) -> str:
    return _gravar(pdf_com_camadas(**kw), tmp_path / nome)


def _pdf_sem_camadas(tmp_path) -> str:
    return _gravar(pdf_comum(), tmp_path / "comum.pdf")


def _projeto(caminho: str, filtro: str = MAGICO_PRO, geometria: bool = False) -> Projeto:
    """Projeto analisado como o programa faz. Sem corte e sem endireitar (a
    nao ser com geometria=True), para o papel ficar onde o teste espera; sem
    a marcacao de gravura e letra (o modelo e lento e nao e o assunto aqui)."""
    projeto = Projeto(caminho_entrada=caminho, nome="teste")
    projeto.filtro_padrao = filtro
    projeto.detectar_regioes = False
    if not geometria:
        projeto.cortar_bordas = False
        projeto.endireitar = False
    return pipeline.analisar_projeto(projeto)


def _previa(projeto: Projeto, indice: int = 0, dpi: int = 100) -> np.ndarray:
    doc = fitz.open(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[indice], dpi=dpi)
    finally:
        doc.close()
    return img


def _papel(img: np.ndarray) -> np.ndarray:
    """A cor media de um trecho que e so papel (a direita, no meio: longe das
    letras e da mancha d'agua do PDF de teste)."""
    altura, largura = img.shape[:2]
    return img[int(0.40 * altura):int(0.60 * altura),
               int(0.86 * largura):int(0.95 * largura)].reshape(-1, 3).mean(axis=0)


def _paginas_do_pdf(caminho) -> list[np.ndarray]:
    """As imagens gravadas no PDF de saida, ponto por ponto (o programa grava
    PNG, sem perda)."""
    saida = []
    with fitz.open(caminho) as doc:
        for pagina in doc:
            xref = pagina.get_images(full=True)[0][0]
            pix = fitz.Pixmap(doc, xref)
            dados = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
            saida.append(cv2.cvtColor(dados, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_GRAY2BGR))
    return saida


# --- o campo novo do projeto ----------------------------------------------------


def test_projeto_novo_nasce_com_a_caixinha_marcada_e_sem_camadas():
    projeto = Projeto(caminho_entrada="x.pdf")
    assert projeto.tirar_fundo_sozinho is True
    assert projeto.tem_camadas is False
    assert projeto.tirar_fundo_ligado is False     # sem camadas, nada liga


def test_tirar_fundo_ligado_precisa_das_camadas_e_da_caixinha():
    projeto = Projeto(caminho_entrada="x.pdf", tem_camadas=True)
    assert projeto.tirar_fundo_ligado
    projeto.tirar_fundo_sozinho = False
    assert not projeto.tirar_fundo_ligado


def test_projeto_antigo_salvo_sem_os_campos_abre_normalmente():
    """Projeto gravado antes de 29/09 (sem tem_camadas e tirar_fundo_sozinho)
    abre, com os padroes: caixinha marcada, camadas a detectar."""
    dados = Projeto(caminho_entrada="livro.pdf", nome="antigo").para_dicionario()
    del dados["tem_camadas"]
    del dados["tirar_fundo_sozinho"]
    dados["paginas"] = [{"indice": 0, "folha": 0, "filtro": PRETO_E_BRANCO}]
    dados["folhas"] = [{"indice": 0}]
    projeto = Projeto.de_dicionario(json.loads(json.dumps(dados)))
    assert projeto.nome == "antigo"
    assert projeto.tirar_fundo_sozinho is True
    assert projeto.tem_camadas is False
    assert projeto.paginas[0].filtro == PRETO_E_BRANCO


def test_projeto_antigo_abre_pelo_disco(tmp_path, monkeypatch):
    """O mesmo, pelo caminho de verdade (projetos.carregar_estado)."""
    import projetos

    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: tmp_path)
    projeto = Projeto(caminho_entrada=str(tmp_path / "livro.pdf"), nome="antigo")
    resumo = projetos.criar(projeto, 1)
    projetos.salvar_estado(resumo, projeto)
    arquivo = next(p for p in tmp_path.rglob("*.json") if p.name == projetos.ARQUIVO_ESTADO)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    dados.pop("tem_camadas")
    dados.pop("tirar_fundo_sozinho")
    arquivo.write_text(json.dumps(dados), encoding="utf-8")
    lido = projetos.carregar_estado(resumo)
    assert lido is not None and lido.tirar_fundo_sozinho is True


def test_caixinha_desmarcada_vai_e_volta_do_disco():
    projeto = Projeto(caminho_entrada="livro.pdf", tem_camadas=True, tirar_fundo_sozinho=False)
    volta = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert volta.tirar_fundo_sozinho is False
    assert volta.tem_camadas is True


# --- detectar ao abrir ------------------------------------------------------------


def test_analise_detecta_as_camadas(tmp_path):
    assert _projeto(_pdf_camadas(tmp_path)).tem_camadas is True


def test_analise_de_pdf_comum_nao_ve_camadas(tmp_path):
    projeto = _projeto(_pdf_sem_camadas(tmp_path))
    assert projeto.tem_camadas is False
    assert projeto.tirar_fundo_ligado is False


def test_deteccao_nao_desenha_pagina(tmp_path, monkeypatch):
    """Barata: so a estrutura do PDF (nenhum Pixmap, nenhum desenho)."""
    caminho = _pdf_camadas(tmp_path)

    def proibido(*_a, **_k):
        raise AssertionError("desenhou/decodificou imagem")

    monkeypatch.setattr(fitz, "Pixmap", proibido)
    monkeypatch.setattr(fitz.Page, "get_pixmap", proibido)
    with fitz.open(caminho) as doc:
        assert camadas.pdf_tem_camadas(doc)


# --- a tela: a caixinha so aparece com camadas ---------------------------------------


@pytest.fixture(scope="module")
def app():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _tela(app, projeto):
    from ui.tela_opcoes import TelaOpcoes

    tela = TelaOpcoes()
    tela.carregar(projeto, 1)
    return tela


def test_caixinha_aparece_com_camadas(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True)
    tela = _tela(app, projeto)
    try:
        assert not tela.painel_tirar_fundo.isHidden()
        assert tela.cx_tirar_fundo.isChecked()
        assert tela.cx_tirar_fundo.text() == "Tirar o fundo sozinho"
        assert "tirar o fundo" in tela.resumo.text()
    finally:
        tela.folhear.fechar()


def test_caixinha_nao_aparece_sem_camadas(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_sem_camadas(tmp_path), tem_camadas=False)
    tela = _tela(app, projeto)
    try:
        assert tela.painel_tirar_fundo.isHidden()
        assert "fundo" not in tela.resumo.text()
    finally:
        tela.folhear.fechar()


def test_caixinha_some_sem_limpar_a_folha(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True)
    tela = _tela(app, projeto)
    try:
        tela.cx_limpar.setChecked(False)
        assert tela.painel_tirar_fundo.isHidden()
    finally:
        tela.folhear.fechar()


def test_desmarcar_desliga_o_tirar_fundo_do_livro(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True)
    tela = _tela(app, projeto)
    try:
        tela.cx_tirar_fundo.click()
        assert projeto.tirar_fundo_sozinho is False
        assert not projeto.tirar_fundo_ligado
        assert "fundo" not in tela.resumo.text()
    finally:
        tela.folhear.fechar()


def test_carregar_devolve_a_caixinha_desmarcada(app, tmp_path):
    """O valor salvo volta a tela, mesmo que outra caixinha mude antes dele
    ao carregar (cada mudanca grava o estado de todas no projeto)."""
    tela = _tela(app, Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True))
    tela.folhear.fechar()
    outro = Projeto(caminho_entrada=_pdf_camadas(tmp_path, "b.pdf"), tem_camadas=True,
                    tirar_fundo_sozinho=False, dividir_folhas=False, endireitar=False)
    tela.carregar(outro, 1)
    try:
        assert not tela.cx_tirar_fundo.isChecked()
        assert outro.tirar_fundo_sozinho is False
    finally:
        tela.folhear.fechar()


def test_abrir_livro_detecta_e_mostra_a_caixinha(app, tmp_path, monkeypatch):
    """O caminho da janela: abrir o PDF ja decide se a caixinha aparece."""
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    try:
        janela.abrir_livro(_pdf_camadas(tmp_path))
        assert janela.projeto.tem_camadas is True
        assert not janela.tela_opcoes.painel_tirar_fundo.isHidden()
        janela.tela_opcoes.folhear.fechar()
        janela.abrir_livro(_pdf_sem_camadas(tmp_path))
        assert janela.projeto.tem_camadas is False
        assert janela.tela_opcoes.painel_tirar_fundo.isHidden()
    finally:
        janela.tela_opcoes.folhear.fechar()
        janela.close()


def test_desmarcar_depois_da_primeira_conferencia_vale(app, tmp_path, monkeypatch):
    """Achado ao ligar o 1.1: depois da primeira analise, o projeto salvo
    voltava por cima e a tela "O que fazer" mexia num objeto velho - a
    caixinha desmarcada na volta nao valia."""
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    try:
        janela.abrir_livro(_pdf_camadas(tmp_path))
        janela.projeto.detectar_regioes = False
        janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))
        assert janela.projeto.tirar_fundo_ligado

        # volta para "O que fazer", desmarca, confere de novo
        janela.tela_opcoes.cx_tirar_fundo.setChecked(False)
        janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))
        assert janela.projeto.tirar_fundo_sozinho is False
        assert projetos.carregar_estado(janela.resumo).tirar_fundo_sozinho is False
    finally:
        if janela.previas is not None:
            janela.previas.parar()
        janela.tela_opcoes.folhear.fechar()
        janela.close()


# --- o resumo em portugues ------------------------------------------------------------


def test_resumo_diz_que_tira_o_fundo():
    projeto = Projeto(caminho_entrada="x.pdf", tem_camadas=True, filtro_padrao=MAGICO_PRO)
    texto = pipeline.resumo_em_portugues(projeto, 10)
    assert "tirar o fundo sozinho" in texto
    assert "mágico pro" in texto            # onde nao der, o filtro


def test_resumo_em_original_avisa_que_precisa_de_filtro():
    projeto = Projeto(caminho_entrada="x.pdf", tem_camadas=True, filtro_padrao=ORIGINAL)
    assert "escolher um filtro" in pipeline.resumo_em_portugues(projeto, 10)


def test_resumo_nao_fala_do_fundo_desligado_ou_sem_camadas():
    desligado = Projeto(caminho_entrada="x.pdf", tem_camadas=True, tirar_fundo_sozinho=False,
                        filtro_padrao=MAGICO_PRO)
    sem = Projeto(caminho_entrada="x.pdf", filtro_padrao=MAGICO_PRO)
    for projeto in (desligado, sem):
        texto = pipeline.resumo_em_portugues(projeto, 10)
        assert "fundo" not in texto
        assert "deixar tudo em mágico pro" in texto


# --- previa e PDF -----------------------------------------------------------------------


def test_previa_usa_o_tirar_fundo_no_lugar_do_filtro(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    img = _previa(projeto)
    assert espiao["tirar_fundo"] == 1
    assert espiao["filtro"] == 0
    assert _papel(img).min() > 250               # papel branco (era amarelado)


def test_botao_desligado_segue_o_filtro(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.tirar_fundo_sozinho = False
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    assert espiao["filtro"] == 1


def test_original_nao_mexe_na_pagina(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path), filtro=ORIGINAL)
    img = _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    papel = _papel(img)[::-1]                    # BGR -> RGB
    assert np.abs(papel - np.array(PAPEL_RGB)).max() < 6   # continua amarelado


def test_sem_limpar_a_folha_nao_tira_o_fundo(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.limpar = False
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0


def test_pdf_sem_camadas_segue_o_filtro(tmp_path, espiao):
    projeto = _projeto(_pdf_sem_camadas(tmp_path))
    projeto.tirar_fundo_sozinho = True
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    assert espiao["filtro"] == 1


def test_pagina_deixada_intacta_segue_o_filtro(tmp_path, espiao, monkeypatch):
    """core/camadas.py deixa a pagina intacta (aqui: o detector falha, e ele
    nao arrisca a figura): o filtro escolhido vale, como antes."""
    def detector_quebrado(_img):
        raise RuntimeError("sem detector")

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", detector_quebrado)
    projeto = _projeto(_pdf_camadas(tmp_path))
    _previa(projeto)
    assert espiao["tirar_fundo"] == 1
    assert espiao["filtro"] == 1
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_pagina_intacta_nao_paga_de_novo(tmp_path, espiao, monkeypatch):
    """A decisao "fica como esta" vale para a sessao: a segunda previa (e o
    PDF) da mesma folha nao roda o "tirar o fundo" de novo."""
    def detector_quebrado(_img):
        raise RuntimeError("sem detector")

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", detector_quebrado)
    projeto = _projeto(_pdf_camadas(tmp_path, "intacta.pdf"))
    _previa(projeto)
    _previa(projeto, dpi=80)
    assert espiao["tirar_fundo"] == 1
    assert espiao["filtro"] == 2


def test_erro_no_tirar_fundo_nao_derruba_a_previa(tmp_path, monkeypatch, espiao):
    def quebra(*_a, **_k):
        raise MemoryError("sem memoria")

    monkeypatch.setattr(camadas, "tirar_fundo", quebra)
    projeto = _projeto(_pdf_camadas(tmp_path))
    img = _previa(projeto)
    assert img is not None
    assert espiao["filtro"] == 1


def test_pdf_final_usa_o_tirar_fundo_e_sai_igual_a_previa(tmp_path, espiao):
    """Prevla = PDF (conserto de 28/09): com corte e endireitar ligados, a
    previa na resolucao do PDF e a pagina gravada sao a mesma imagem."""
    projeto = _projeto(_pdf_camadas(tmp_path), geometria=True)
    projeto.qualidade_dpi = 150
    previa = _previa(projeto, dpi=150)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert espiao["filtro"] == 0
    gravada = _paginas_do_pdf(projeto.caminho_saida)
    assert len(gravada) == 1
    assert gravada[0].shape == previa.shape
    assert np.array_equal(gravada[0], previa)


def test_pdf_final_com_o_botao_desligado_usa_o_filtro(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.tirar_fundo_sozinho = False
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert espiao["tirar_fundo"] == 0
    assert espiao["filtro"] == 1


def test_folha_dividida_tira_o_fundo_uma_vez_so(tmp_path, espiao):
    """As duas metades vem da mesma folha: o "tirar o fundo" roda uma vez, na
    folha inteira, antes de dividir. Uma metade em Original fica como veio."""
    from modelos import METADE_DIREITA, METADE_ESQUERDA, ConfigPagina

    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.folhas[0].dividir = True
    projeto.folhas[0].posicao_corte = 0.5
    projeto.paginas = [
        ConfigPagina(indice=0, folha=0, metade=METADE_ESQUERDA, filtro=MAGICO_PRO),
        ConfigPagina(indice=1, folha=0, metade=METADE_DIREITA, filtro=ORIGINAL),
    ]
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert espiao["tirar_fundo"] == 1
    esquerda, direita = _paginas_do_pdf(projeto.caminho_saida)
    assert _papel(direita).min() < 230           # a metade em Original continua amarelada


# --- "conferir" -----------------------------------------------------------------------


def _pdf_duvidoso(tmp_path) -> str:
    """Pagina quase vazia com escrita fraca so no fundo: core/camadas.py tira
    o fundo e pede conferencia (tests/test_camadas.py)."""
    pouca = np.zeros((ALTURA_CIMA, LARGURA_CIMA), bool)
    pouca[600:640, 150:260] = True
    return _pdf_camadas(tmp_path, "duvidoso.pdf", fundo=fundo_com_escrita_fraca(), mascara=pouca)


def test_pagina_duvidosa_ganha_o_alerta_conferir(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    pagina = projeto.paginas[0]
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas   # a analise nao sabe
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in pagina.alertas
    assert pagina.precisa_revisao
    _previa(projeto)
    assert pagina.alertas.count(analise.CONFERIR_FUNDO_TIRADO) == 1


def test_pagina_sem_duvida_nao_ganha_o_alerta(tmp_path):
    projeto = _projeto(_pdf_camadas(tmp_path))
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_alerta_sai_quando_a_pagina_volta_a_original(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    pagina = projeto.paginas[0]
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in pagina.alertas
    pagina.filtro = ORIGINAL
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas


def test_processar_tambem_marca_conferir(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in projeto.paginas[0].alertas


def test_botao_desligado_tira_os_alertas_de_antes(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    _previa(projeto)
    projeto.tirar_fundo_sozinho = False
    pipeline.tirar_alertas_do_fundo_se_desligado(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_texto_do_alerta_em_portugues_sem_jargao():
    alerta = analise.descrever(analise.CONFERIR_FUNDO_TIRADO)
    assert alerta.titulo != analise.CONFERIR_FUNDO_TIRADO      # tem texto de verdade
    assert "confira" in alerta.mensagem
    assert "página" in alerta.mensagem                          # com acento
    assert alerta.mensagem.isprintable()
    assert all(ord(c) < 0x2000 for c in alerta.mensagem + alerta.titulo)   # sem emoji
    assert alerta.correcao == "revisar"
