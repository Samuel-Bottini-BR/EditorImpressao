"""Item 1.1 no programa: o filtro "Tirar o fundo" de PDF com camadas.

Decisao do Samuel (29/09/2026, depois de ver a primeira ligacao, commit
bb54b7d): "Pagina sempre abre em 'Original', sem mexer. Em PDF com camadas,
'Tirar o fundo' vira mais uma opcao na lista de filtros (ao lado de Original,
Preto e branco, Melhorar e Magico pro), com botao para aplicar no livro
inteiro. [...] Ao abrir um livro com camadas, o programa pode avisar: 'Este
livro tem fundo separado. Quer tirar o fundo?'. A caixinha 'Tirar o fundo
sozinho' nao e mais necessaria." E: "eu quero poder escolher tirar o fundo
sem colocar nenhum filtro." E: "nenhum livro vem marcado, nem novo, nem
velho." Decisao da gerente (a rever pelo Samuel): o aviso so aparece quando o
livro e aberto pela primeira vez (projeto novo).

O que se cobra aqui (teste de maquina):

    - o filtro novo so aparece em livro com camadas (tela "O que fazer",
      cartoes da aba Filtro, tela ampliada e "comparar");
    - por pagina e para o livro inteiro (filtro do livro, "todas"), com
      desfazer e refazer;
    - pagina que core/camadas.py deixa "intacta" sai como veio (igual ao
      Original), sem filtro por cima; Original nao mexe; PDF sem camadas com
      o filtro salvo sai como Original, sem erro;
    - projeto antigo (sem o campo, ou com a caixinha da rodada anterior)
      abre normalmente e nao vem com o fundo tirado;
    - o aviso so na primeira abertura de livro com camadas; "Sim" poe o livro
      inteiro no filtro, "Nao" nao muda nada;
    - o alerta "conferir" aparece na pagina em que se escolhe o filtro
      (defeito 2 do verificador) e some quando ela sai dele;
    - previa igual ao PDF ponto a ponto; o cartao e o "comparar" mostram o
      resultado de verdade.

Os PDFs com camadas sao os de tests/test_camadas.py (montados na hora, como
os do Internet Archive). O detector de figuras do core/camadas.py e trocado
por um que nao acha nada (rapido, sem o modelo), como la.
"""

from __future__ import annotations

import json
import time

import cv2
import fitz
import numpy as np
import pytest

from core import analise, camadas, pipeline
from core.filtros import (
    FILTROS,
    FILTROS_COMUNS,
    MAGICO_PRO,
    NOMES_AMIGAVEIS,
    ORIGINAL,
    PRETO_E_BRANCO,
    TIRAR_FUNDO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
    filtros_do_livro,
)
from modelos import ConfigPagina, Projeto
from tests.test_camadas import (
    ALTURA_CIMA,
    LARGURA_CIMA,
    PAPEL_RGB,
    acrescentar_pagina_com_camadas,
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


@pytest.fixture
def detector_quebrado(monkeypatch):
    """O detector falha: core/camadas.py nao arrisca a figura e deixa a
    pagina INTACTA (o caso do Palatino 5)."""
    def quebrado(_img):
        raise RuntimeError("sem detector")

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", quebrado)


def _gravar(doc: fitz.Document, caminho) -> str:
    doc.save(caminho)
    doc.close()
    return str(caminho)


def _pdf_camadas(tmp_path, nome="camadas.pdf", paginas: int = 1, **kw) -> str:
    doc = pdf_com_camadas(**kw)
    for _ in range(paginas - 1):
        acrescentar_pagina_com_camadas(doc, **kw)
    return _gravar(doc, tmp_path / nome)


def _pdf_sem_camadas(tmp_path) -> str:
    return _gravar(pdf_comum(), tmp_path / "comum.pdf")


def _pdf_duvidoso(tmp_path, nome="duvidoso.pdf", paginas: int = 1) -> str:
    """Pagina quase vazia com escrita fraca so no fundo: core/camadas.py tira
    o fundo e pede conferencia (tests/test_camadas.py)."""
    pouca = np.zeros((ALTURA_CIMA, LARGURA_CIMA), bool)
    pouca[600:640, 150:260] = True
    return _pdf_camadas(tmp_path, nome, paginas=paginas,
                        fundo=fundo_com_escrita_fraca(), mascara=pouca)


def _projeto(caminho: str, filtro: str = TIRAR_FUNDO, geometria: bool = False,
             dividir: bool = True) -> Projeto:
    """Projeto analisado como o programa faz. Sem corte e sem endireitar (a
    nao ser com geometria=True), para o papel ficar onde o teste espera; sem
    a marcacao de gravura e letra (o modelo e lento e nao e o assunto aqui)."""
    projeto = Projeto(caminho_entrada=caminho, nome="teste")
    projeto.filtro_padrao = filtro
    projeto.detectar_regioes = False
    projeto.dividir_folhas = dividir
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


def _esperar(condicao, segundos: float = 30.0) -> bool:
    """Deixa a fila do Qt andar ate `condicao()` ou o tempo acabar (as previas
    chegam de tarefas em segundo plano)."""
    from PySide6.QtWidgets import QApplication

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    QApplication.processEvents()
    return bool(condicao())


# --- o filtro na lista ----------------------------------------------------------


def test_filtro_novo_esta_na_lista_com_nome_em_portugues():
    assert TIRAR_FUNDO in FILTROS
    assert TIRAR_FUNDO not in FILTROS_COMUNS
    assert NOMES_AMIGAVEIS[TIRAR_FUNDO] == "Tirar o fundo"


def test_filtro_so_aparece_em_livro_com_camadas():
    assert TIRAR_FUNDO in filtros_do_livro(Projeto(caminho_entrada="x.pdf", tem_camadas=True))
    assert filtros_do_livro(Projeto(caminho_entrada="x.pdf")) == FILTROS_COMUNS


def test_filtro_salvo_sem_camadas_continua_na_lista_para_poder_sair_dele():
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=TIRAR_FUNDO)]
    assert TIRAR_FUNDO in filtros_do_livro(projeto)


def test_aplicar_o_filtro_na_imagem_nao_mexe():
    """Nas funcoes de filtro o "Tirar o fundo" e o Original (so chega ali a
    pagina que fica como veio): nunca outro filtro por cima."""
    from core.selecao import GRAVURA, RETANGULO, Regiao, Selecao

    img = np.full((60, 40, 3), (160, 200, 215), np.uint8)
    img[20:30, 10:30] = 30
    saida, mono = aplicar_filtro(img, TIRAR_FUNDO)
    assert np.array_equal(saida, img) and not mono
    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.5, 0.5)]))
    saida, mono = aplicar_filtro_com_selecao(img, TIRAR_FUNDO, selecao)
    assert np.array_equal(saida, img) and not mono


# --- o projeto: a caixinha saiu, os projetos antigos abrem ---------------------------


def test_projeto_nao_tem_mais_a_caixinha():
    projeto = Projeto(caminho_entrada="x.pdf")
    assert not hasattr(projeto, "tirar_fundo_sozinho")
    assert not hasattr(projeto, "tirar_fundo_ligado")
    assert projeto.tem_camadas is False
    assert projeto.filtro_padrao == ORIGINAL


def test_projeto_antigo_sem_o_campo_abre_normalmente():
    """Projeto gravado antes de 29/09 (sem tem_camadas): abre, com o padrao."""
    dados = Projeto(caminho_entrada="livro.pdf", nome="antigo").para_dicionario()
    del dados["tem_camadas"]
    dados["paginas"] = [{"indice": 0, "folha": 0, "filtro": PRETO_E_BRANCO}]
    dados["folhas"] = [{"indice": 0}]
    projeto = Projeto.de_dicionario(json.loads(json.dumps(dados)))
    assert projeto.nome == "antigo"
    assert projeto.tem_camadas is False
    assert projeto.paginas[0].filtro == PRETO_E_BRANCO


def test_projeto_da_rodada_anterior_com_a_caixinha_abre_e_nao_tira_o_fundo(tmp_path, espiao):
    """Projeto salvo na primeira ligacao (commit bb54b7d), com a caixinha
    "tirar_fundo_sozinho" marcada, num PDF com camadas: abre, o campo e
    ignorado, e a pagina em Preto e branco sai no Preto e branco - o fundo
    nao sai sem ninguem escolher ("nenhum livro vem marcado")."""
    caminho = _pdf_camadas(tmp_path)
    analisado = _projeto(caminho, filtro=PRETO_E_BRANCO)
    dados = analisado.para_dicionario()
    dados["tirar_fundo_sozinho"] = True
    projeto = Projeto.de_dicionario(json.loads(json.dumps(dados)))
    assert projeto.tem_camadas is True
    assert all(p.filtro == PRETO_E_BRANCO for p in projeto.paginas)
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    assert espiao["filtro"] == 1


def test_projeto_antigo_abre_pelo_disco(tmp_path, monkeypatch):
    """O mesmo, pelo caminho de verdade (projetos.carregar_estado), com o
    campo da caixinha sobrando e o tem_camadas faltando."""
    import projetos

    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: tmp_path)
    projeto = Projeto(caminho_entrada=str(tmp_path / "livro.pdf"), nome="antigo")
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=MAGICO_PRO)]
    resumo = projetos.criar(projeto, 1)
    projetos.salvar_estado(resumo, projeto)
    arquivo = next(p for p in tmp_path.rglob("*.json") if p.name == projetos.ARQUIVO_ESTADO)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    dados.pop("tem_camadas")
    dados["tirar_fundo_sozinho"] = True
    arquivo.write_text(json.dumps(dados), encoding="utf-8")
    lido = projetos.carregar_estado(resumo)
    assert lido is not None
    assert lido.paginas[0].filtro == MAGICO_PRO
    assert not hasattr(lido, "tirar_fundo_sozinho")


def test_filtro_tirar_o_fundo_vai_e_volta_do_disco():
    projeto = Projeto(caminho_entrada="livro.pdf", tem_camadas=True, filtro_padrao=TIRAR_FUNDO)
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=TIRAR_FUNDO)]
    volta = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert volta.filtro_padrao == TIRAR_FUNDO
    assert volta.paginas[0].filtro == TIRAR_FUNDO


def test_nome_do_arquivo_de_saida():
    from modelos import nome_de_saida_sugerido

    projeto = Projeto(caminho_entrada="x.pdf", nome="Palatino", filtro_padrao=TIRAR_FUNDO)
    assert nome_de_saida_sugerido(projeto) == "Palatino - sem fundo.pdf"


# --- detectar ao abrir ------------------------------------------------------------


def test_analise_detecta_as_camadas(tmp_path):
    assert _projeto(_pdf_camadas(tmp_path)).tem_camadas is True


def test_analise_de_pdf_comum_nao_ve_camadas(tmp_path):
    assert _projeto(_pdf_sem_camadas(tmp_path)).tem_camadas is False


def test_deteccao_nao_desenha_pagina(tmp_path, monkeypatch):
    """Barata: so a estrutura do PDF (nenhum Pixmap, nenhum desenho)."""
    caminho = _pdf_camadas(tmp_path)

    def proibido(*_a, **_k):
        raise AssertionError("desenhou/decodificou imagem")

    monkeypatch.setattr(fitz, "Pixmap", proibido)
    monkeypatch.setattr(fitz.Page, "get_pixmap", proibido)
    with fitz.open(caminho) as doc:
        assert camadas.pdf_tem_camadas(doc)


# --- a tela "O que fazer" -------------------------------------------------------------


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


def test_filtro_do_livro_aparece_com_camadas(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True)
    tela = _tela(app, projeto)
    try:
        radio = tela.radios_de_filtro[TIRAR_FUNDO]
        assert not radio.isHidden()
        assert radio.text() == "Tirar o fundo"
        assert not radio.isChecked()                        # nunca vem marcado
        assert tela.radios_de_filtro[ORIGINAL].isChecked()
        assert "fundo" not in tela.resumo.text()
        assert not hasattr(tela, "cx_tirar_fundo")          # a caixinha saiu
    finally:
        tela.folhear.fechar()


def test_filtro_do_livro_nao_aparece_sem_camadas(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_sem_camadas(tmp_path), tem_camadas=False)
    tela = _tela(app, projeto)
    try:
        assert tela.radios_de_filtro[TIRAR_FUNDO].isHidden()
        assert not tela.radios_de_filtro[MAGICO_PRO].isHidden()
    finally:
        tela.folhear.fechar()


def test_clicar_o_filtro_do_livro_vale_para_o_livro(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True)
    tela = _tela(app, projeto)
    try:
        tela.radios_de_filtro[TIRAR_FUNDO].click()
        assert projeto.filtro_padrao == TIRAR_FUNDO
        assert "tirar o fundo de todas as páginas" in tela.resumo.text()
        assert "como veio" in tela.resumo.text()
    finally:
        tela.folhear.fechar()


def test_escolher_filtro_do_livro_marca_limpar(app, tmp_path):
    projeto = Projeto(caminho_entrada=_pdf_camadas(tmp_path), tem_camadas=True, limpar=False)
    tela = _tela(app, projeto)
    try:
        tela.escolher_filtro_do_livro(TIRAR_FUNDO)
        assert projeto.limpar is True
        assert projeto.filtro_padrao == TIRAR_FUNDO
        assert tela.radios_de_filtro[TIRAR_FUNDO].isChecked()
    finally:
        tela.folhear.fechar()


def test_resumo_sem_camadas_nao_fala_do_fundo():
    projeto = Projeto(caminho_entrada="x.pdf", filtro_padrao=TIRAR_FUNDO)
    assert "fundo" not in pipeline.resumo_em_portugues(projeto, 10)
    projeto = Projeto(caminho_entrada="x.pdf", tem_camadas=True, filtro_padrao=MAGICO_PRO)
    texto = pipeline.resumo_em_portugues(projeto, 10)
    assert "fundo" not in texto and "deixar tudo em mágico pro" in texto


# --- o aviso ao abrir ------------------------------------------------------------------


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    yield janela
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.tela_opcoes.folhear.fechar()
    janela.close()


def _botao_do_aviso(janela, texto: str):
    from PySide6.QtWidgets import QAbstractButton

    caixa = janela.aviso_do_fundo
    assert caixa is not None
    return next(b for b in caixa.findChildren(QAbstractButton) if b.text() == texto)


def _analisar(janela) -> None:
    """O que o "Conferir" faz, sem a tarefa em segundo plano."""
    janela.projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))


def test_aviso_aparece_ao_abrir_livro_com_camadas_pela_primeira_vez(janela, tmp_path):
    janela.abrir_livro(_pdf_camadas(tmp_path))
    caixa = janela.aviso_do_fundo
    assert caixa is not None
    assert caixa.text() == "Este livro tem fundo separado. Quer tirar o fundo?"
    textos = {b.text() for b in caixa.buttons()}
    assert {"Sim, tirar o fundo", "Não, deixar como está"} <= textos
    assert all(ord(c) < 0x2000 for t in textos for c in t)          # sem emoji
    assert janela.projeto.filtro_padrao == ORIGINAL                  # nada muda antes da resposta


def test_sim_poe_o_livro_inteiro_no_filtro(janela, tmp_path):
    janela.abrir_livro(_pdf_camadas(tmp_path, paginas=2))
    _botao_do_aviso(janela, "Sim, tirar o fundo").click()
    assert janela.aviso_do_fundo is None
    assert janela.projeto.filtro_padrao == TIRAR_FUNDO
    assert janela.tela_opcoes.radios_de_filtro[TIRAR_FUNDO].isChecked()
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [TIRAR_FUNDO, TIRAR_FUNDO]


def test_nao_deixa_tudo_como_esta(janela, tmp_path):
    janela.abrir_livro(_pdf_camadas(tmp_path, paginas=2))
    _botao_do_aviso(janela, "Não, deixar como está").click()
    assert janela.aviso_do_fundo is None
    assert janela.projeto.filtro_padrao == ORIGINAL
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [ORIGINAL, ORIGINAL]


def test_fechar_o_aviso_vale_como_nao(janela, tmp_path):
    janela.abrir_livro(_pdf_camadas(tmp_path))
    janela.aviso_do_fundo.reject()                  # Esc / X
    assert janela.aviso_do_fundo is None
    assert janela.projeto.filtro_padrao == ORIGINAL


def test_livro_sem_camadas_nunca_pergunta(janela, tmp_path):
    janela.abrir_livro(_pdf_sem_camadas(tmp_path))
    assert janela.aviso_do_fundo is None
    assert janela.tela_opcoes.radios_de_filtro[TIRAR_FUNDO].isHidden()


def test_reabrir_livro_que_ja_tem_projeto_nao_pergunta(janela, tmp_path):
    caminho = _pdf_camadas(tmp_path)
    janela.abrir_livro(caminho)
    _botao_do_aviso(janela, "Não, deixar como está").click()
    janela.tela_opcoes.folhear.fechar()
    janela.abrir_livro(caminho)                     # o mesmo PDF, pelo "Abrir"
    assert janela.aviso_do_fundo is None
    assert not janela.tela_opcoes.radios_de_filtro[TIRAR_FUNDO].isHidden()


def test_abrir_e_continuar_mantem_o_filtro_escolhido(janela, tmp_path, monkeypatch):
    """Defeito 1 do verificador (a caixinha voltava marcada pelo "Abrir"):
    com o filtro, abrir o mesmo PDF pelo "Abrir" e pelo "continuar" mantem o
    que foi escolhido em cada pagina."""
    import projetos

    caminho = _pdf_camadas(tmp_path, paginas=2)
    janela.abrir_livro(caminho)
    _botao_do_aviso(janela, "Não, deixar como está").click()
    _analisar(janela)
    janela.projeto.paginas[1].filtro = TIRAR_FUNDO     # so a segunda pagina
    janela._salvar_agora()

    janela.tela_opcoes.folhear.fechar()
    janela.abrir_livro(caminho)                         # pelo "Abrir"
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [ORIGINAL, TIRAR_FUNDO]

    janela.tela_opcoes.folhear.fechar()
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.achar_por_assinatura(caminho))   # pelo "continuar"
    assert janela.aviso_do_fundo is None
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [ORIGINAL, TIRAR_FUNDO]


# --- previa e PDF -----------------------------------------------------------------------


def test_previa_tira_o_fundo_sem_filtro_por_cima(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    img = _previa(projeto)
    assert espiao["tirar_fundo"] == 1
    assert espiao["filtro"] == 0
    assert _papel(img).min() > 250               # papel branco (era amarelado)


def test_original_nao_mexe_na_pagina(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path), filtro=ORIGINAL)
    img = _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    papel = _papel(img)[::-1]                    # BGR -> RGB
    assert np.abs(papel - np.array(PAPEL_RGB)).max() < 6   # continua amarelado


def test_outro_filtro_nao_tira_o_fundo(tmp_path, espiao):
    """Magico pro num livro com camadas e so o Magico pro ("sem mudanca
    escondida")."""
    projeto = _projeto(_pdf_camadas(tmp_path), filtro=MAGICO_PRO)
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0
    assert espiao["filtro"] == 1


def test_pagina_intacta_sai_como_veio(tmp_path, espiao, detector_quebrado):
    """core/camadas.py deixa a pagina intacta: ela sai igual ao Original,
    ponto por ponto - nada de Magico pro nem de outro filtro."""
    projeto = _projeto(_pdf_camadas(tmp_path))
    com_filtro = _previa(projeto)
    assert espiao["tirar_fundo"] == 1
    assert espiao["filtro"] == 0
    projeto.paginas[0].filtro = ORIGINAL
    como_veio = _previa(projeto)
    assert np.array_equal(com_filtro, como_veio)
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_pagina_intacta_nao_paga_de_novo(tmp_path, espiao, detector_quebrado):
    """A decisao "fica como esta" vale para a sessao: a segunda previa (e o
    PDF) da mesma folha nao roda o "tirar o fundo" de novo."""
    projeto = _projeto(_pdf_camadas(tmp_path, "intacta.pdf"))
    _previa(projeto)
    _previa(projeto, dpi=80)
    assert espiao["tirar_fundo"] == 1


def test_erro_no_tirar_fundo_sai_como_veio(tmp_path, monkeypatch):
    def quebra(*_a, **_k):
        raise MemoryError("sem memoria")

    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.paginas[0].filtro = ORIGINAL
    como_veio = _previa(projeto)
    monkeypatch.setattr(camadas, "tirar_fundo", quebra)
    projeto.paginas[0].filtro = TIRAR_FUNDO
    assert np.array_equal(_previa(projeto), como_veio)


def test_filtro_salvo_em_pdf_sem_camadas_sai_como_original(tmp_path, espiao):
    """Projeto com "Tirar o fundo" salvo e um PDF sem camadas: a pagina sai
    como Original, sem erro (com tem_camadas errado tambem)."""
    projeto = _projeto(_pdf_sem_camadas(tmp_path))
    como_veio = _previa(projeto)                 # o filtro ja e TIRAR_FUNDO
    assert espiao["tirar_fundo"] == 0 and espiao["filtro"] == 0
    projeto.paginas[0].filtro = ORIGINAL
    assert np.array_equal(_previa(projeto), como_veio)
    projeto.paginas[0].filtro = TIRAR_FUNDO
    projeto.tem_camadas = True                   # engano: o PDF diz que nao tem
    assert np.array_equal(_previa(projeto), como_veio)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    projeto.qualidade_dpi = 100
    assert pipeline.processar(projeto)


def test_sem_limpar_a_folha_nao_tira_o_fundo(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.limpar = False
    _previa(projeto)
    assert espiao["tirar_fundo"] == 0


def test_pdf_final_sai_igual_a_previa(tmp_path, espiao):
    """Previa = PDF (conserto de 28/09): com corte e endireitar ligados, a
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


def test_livro_inteiro_no_filtro_sai_todo_sem_fundo(tmp_path, espiao):
    projeto = _projeto(_pdf_camadas(tmp_path, paginas=2))
    assert [p.filtro for p in projeto.paginas] == [TIRAR_FUNDO, TIRAR_FUNDO]
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert espiao["tirar_fundo"] == 2
    assert espiao["filtro"] == 0
    for pagina in _paginas_do_pdf(projeto.caminho_saida):
        assert _papel(pagina).min() > 250


def test_folha_dividida_tira_o_fundo_uma_vez_so(tmp_path, espiao):
    """As duas metades vem da mesma folha: o "tirar o fundo" roda uma vez, na
    folha inteira, antes de dividir. Uma metade em Original fica como veio."""
    from modelos import METADE_DIREITA, METADE_ESQUERDA

    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.folhas[0].dividir = True
    projeto.folhas[0].posicao_corte = 0.5
    projeto.paginas = [
        ConfigPagina(indice=0, folha=0, metade=METADE_ESQUERDA, filtro=TIRAR_FUNDO),
        ConfigPagina(indice=1, folha=0, metade=METADE_DIREITA, filtro=ORIGINAL),
    ]
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert espiao["tirar_fundo"] == 1
    _esquerda, direita = _paginas_do_pdf(projeto.caminho_saida)
    assert _papel(direita).min() < 230           # a metade em Original continua amarelada


def test_desenho_com_outro_filtro_e_o_de_verdade_e_nao_muda_a_pagina(tmp_path):
    """O cartao e o "comparar" (renderizar_com_filtro): a mesma imagem que a
    pagina teria no filtro, sem mudar o filtro nem os alertas dela."""
    projeto = _projeto(_pdf_duvidoso(tmp_path), filtro=ORIGINAL)
    pagina = projeto.paginas[0]
    with fitz.open(projeto.caminho_entrada) as doc:
        cartao, _ = pipeline.renderizar_com_filtro(doc, projeto, pagina, TIRAR_FUNDO, dpi=90)
    assert pagina.filtro == ORIGINAL
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas
    pagina.filtro = TIRAR_FUNDO
    assert np.array_equal(cartao, _previa(projeto, dpi=90))


# --- "conferir" -----------------------------------------------------------------------


def test_pagina_duvidosa_ganha_o_alerta_conferir(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    pagina = projeto.paginas[0]
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas   # a analise nao sabe
    _previa(projeto)
    assert pagina.alertas[0] == analise.CONFERIR_FUNDO_TIRADO    # e o que a faixa mostra
    assert pagina.precisa_revisao
    _previa(projeto)
    assert pagina.alertas.count(analise.CONFERIR_FUNDO_TIRADO) == 1


def test_alerta_aparece_mesmo_com_a_pagina_ja_conferida(tmp_path):
    """Defeito 2 do verificador: escolher o filtro marca a pagina como
    conferida, e o alerta, que so vem depois, nascia escondido."""
    projeto = _projeto(_pdf_duvidoso(tmp_path), filtro=ORIGINAL)
    pagina = projeto.paginas[0]
    pagina.filtro, pagina.revisada = TIRAR_FUNDO, True   # o que _escolher_filtro faz
    _previa(projeto)
    assert pagina.precisa_revisao


def test_esta_bom_assim_continua_valendo(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    pagina = projeto.paginas[0]
    _previa(projeto)
    pagina.revisada = True                        # "esta bom assim"
    _previa(projeto)
    pipeline.acertar_alertas_do_fundo(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in pagina.alertas
    assert not pagina.precisa_revisao


def test_pagina_sem_duvida_nao_ganha_o_alerta(tmp_path):
    projeto = _projeto(_pdf_camadas(tmp_path))
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_alerta_sai_quando_a_pagina_sai_do_filtro(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    pagina = projeto.paginas[0]
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in pagina.alertas
    pagina.filtro = MAGICO_PRO
    pipeline.acertar_alertas_do_fundo(projeto)    # sem desenhar
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas
    pagina.filtro = TIRAR_FUNDO
    pipeline.acertar_alertas_do_fundo(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in pagina.alertas      # volta, sem desenhar
    pagina.filtro = ORIGINAL
    _previa(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas


def test_alerta_na_hora_de_escolher_se_o_cartao_ja_desenhou(tmp_path, espiao):
    """O cartao "Tirar o fundo" (numa copia da pagina) ja descobriu a
    decisao: ao escolher o filtro, o alerta aparece sem desenhar de novo."""
    projeto = _projeto(_pdf_duvidoso(tmp_path), filtro=ORIGINAL)
    pagina = projeto.paginas[0]
    with fitz.open(projeto.caminho_entrada) as doc:
        pipeline.renderizar_com_filtro(doc, projeto, pagina, TIRAR_FUNDO, dpi=70)
    vezes = espiao["tirar_fundo"]
    pagina.filtro, pagina.revisada = TIRAR_FUNDO, True
    pipeline.acertar_alertas_do_fundo(projeto, [pagina])
    assert espiao["tirar_fundo"] == vezes
    assert pagina.precisa_revisao


def test_processar_tambem_marca_conferir(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    projeto.qualidade_dpi = 100
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO in projeto.paginas[0].alertas


def test_ao_abrir_o_alerta_sai_das_paginas_fora_do_filtro(tmp_path):
    projeto = _projeto(_pdf_duvidoso(tmp_path))
    _previa(projeto)
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    projeto.tem_camadas = True
    pipeline.acertar_alertas_do_fundo(projeto)
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas


def test_texto_do_alerta_em_portugues_sem_jargao():
    alerta = analise.descrever(analise.CONFERIR_FUNDO_TIRADO)
    assert alerta.titulo != analise.CONFERIR_FUNDO_TIRADO      # tem texto de verdade
    assert "confira" in alerta.mensagem
    assert "página" in alerta.mensagem                          # com acento
    assert alerta.mensagem.isprintable()
    assert all(ord(c) < 0x2000 for c in alerta.mensagem + alerta.titulo)   # sem emoji
    assert alerta.correcao == "revisar"


# --- a tela de conferir: cartoes, "todas", desfazer, alerta ------------------------------


@pytest.fixture
def conferir(app, tmp_path):
    """TelaConferir de verdade, com GerenciadorPrevias de verdade, num livro
    de 2 paginas com camadas (duvidosas), em Original."""
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(_pdf_duvidoso(tmp_path, paginas=2), filtro=ORIGINAL, dividir=False)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    yield tela
    previas.parar()


def test_cartoes_com_camadas_tem_o_tirar_o_fundo(conferir):
    assert list(conferir.cartoes) == list(FILTROS)
    assert conferir.cartoes[TIRAR_FUNDO].rotulo_nome.text() == "Tirar o fundo"


def test_cartoes_sem_camadas_sao_os_quatro(app, tmp_path):
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(_pdf_sem_camadas(tmp_path), filtro=ORIGINAL, dividir=False)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    try:
        tela.carregar(projeto, HistoricoAcoes(), previas)
        assert list(tela.cartoes) == list(FILTROS_COMUNS)
    finally:
        previas.parar()


def test_cartao_mostra_o_fundo_tirado_de_verdade(conferir):
    """Ressalva (c) do verificador: o cartao mostra o resultado do
    core/camadas.py, e nao um filtro comum."""
    from ui.tela_conferir import DPI_CARTAO_SEM_FUNDO

    cartao = conferir.cartoes[TIRAR_FUNDO]
    assert _esperar(lambda: cartao.amostra._pixmap is not None)
    projeto = conferir.projeto
    esperado = conferir.previas.pegar_com_filtro(0, DPI_CARTAO_SEM_FUNDO, TIRAR_FUNDO)
    with fitz.open(projeto.caminho_entrada) as doc:
        direto, _ = pipeline.renderizar_com_filtro(doc, projeto, projeto.paginas[0],
                                                   TIRAR_FUNDO, dpi=DPI_CARTAO_SEM_FUNDO)
    assert np.array_equal(esperado, direto)
    assert _papel(esperado).min() > 250           # branco: nao e o Original
    assert projeto.paginas[0].filtro == ORIGINAL  # o cartao nao muda a pagina


def test_escolher_o_filtro_na_pagina_mostra_o_alerta(conferir):
    """Defeito 2 do verificador, pela tela: escolher "Tirar o fundo" na pagina
    faz o alerta aparecer (faixa, miniatura, contador), e sair dele o tira."""
    projeto = conferir.projeto
    conferir._escolher_filtro(TIRAR_FUNDO)
    pagina = projeto.paginas[0]
    assert pagina.filtro == TIRAR_FUNDO
    assert _esperar(lambda: pagina.precisa_revisao)
    mensagem = analise.descrever(analise.CONFERIR_FUNDO_TIRADO).mensagem
    assert _esperar(lambda: conferir.texto_faixa.text() == mensagem)
    assert projeto.pendentes_de_revisao() >= 1
    conferir._escolher_filtro(ORIGINAL)
    assert analise.CONFERIR_FUNDO_TIRADO not in pagina.alertas
    assert conferir.texto_faixa.text() != mensagem


def test_alerta_que_chega_pela_previa_entra_no_para_revisar(app, tmp_path):
    """Bug pequeno do item 1.1 (verificador, 29/09; print
    t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg): quando o alerta
    "conferir o fundo tirado" chegava com a previa, a faixa e a miniatura o
    mostravam, mas o quadro "Para revisar" ficava "nada pendente" ate virar a
    pagina. A pagina ja nasce no filtro: na hora de abrir a decisao do
    core/camadas.py ainda nao e conhecida, e o alerta so vem com a previa."""
    from historico_acoes import HistoricoAcoes
    from PySide6.QtWidgets import QPushButton
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(_pdf_duvidoso(tmp_path, paginas=2), filtro=TIRAR_FUNDO, dividir=False)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    try:
        tela.carregar(projeto, HistoricoAcoes(), previas)
        painel = tela.paineis.para_revisar

        def textos() -> list[str]:
            return [b.text() for b in painel.findChildren(QPushButton)
                    if b is not painel.cabecalho]

        assert _esperar(lambda: projeto.paginas[0].precisa_revisao), "o alerta nao chegou"
        titulo = analise.descrever(analise.CONFERIR_FUNDO_TIRADO).titulo
        assert _esperar(lambda: any(titulo in t for t in textos()), segundos=5), (
            f"'Para revisar' nao contou o alerta que chegou pela previa: {textos()}")
        assert painel.cabecalho.text() != "Para revisar"      # com o numero
    finally:
        previas.parar()


def test_todas_poe_o_livro_inteiro_no_filtro_e_desfazer_volta(conferir):
    projeto = conferir.projeto
    conferir._escolher_filtro(TIRAR_FUNDO)
    conferir._filtro_em_todas()
    assert [p.filtro for p in projeto.paginas] == [TIRAR_FUNDO, TIRAR_FUNDO]
    conferir.desfazer()
    assert [p.filtro for p in projeto.paginas] == [TIRAR_FUNDO, ORIGINAL]
    conferir.desfazer()
    assert [p.filtro for p in projeto.paginas] == [ORIGINAL, ORIGINAL]
    assert analise.CONFERIR_FUNDO_TIRADO not in projeto.paginas[0].alertas
    conferir.refazer()
    conferir.refazer()
    assert [p.filtro for p in projeto.paginas] == [TIRAR_FUNDO, TIRAR_FUNDO]


def test_ampliada_tem_o_filtro_e_o_comparar_de_verdade(conferir):
    from ui.tela_ampliada import DPI_AMPLIADA, TelaAmpliada

    ampliada = TelaAmpliada(conferir)
    try:
        assert TIRAR_FUNDO in ampliada.botoes_de_filtro
        assert ampliada.botoes_de_filtro[TIRAR_FUNDO].text() == "Tirar o fundo"
        assert ampliada.combo_comparar.findData(TIRAR_FUNDO) >= 0
        ampliada.botao_comparar.setChecked(True)
        ampliada._alternar_comparar()
        ampliada.combo_comparar.setCurrentIndex(ampliada.combo_comparar.findData(TIRAR_FUNDO))
        assert _esperar(lambda: ampliada._imagem_do_outro_filtro() is not None)
        projeto = conferir.projeto
        with fitz.open(projeto.caminho_entrada) as doc:
            direto, _ = pipeline.renderizar_com_filtro(doc, projeto, projeto.paginas[0],
                                                       TIRAR_FUNDO, dpi=DPI_AMPLIADA)
        assert np.array_equal(ampliada._imagem_do_outro_filtro(), direto)
        ampliada.botoes_de_filtro[TIRAR_FUNDO].click()
        assert projeto.paginas[0].filtro == TIRAR_FUNDO
    finally:
        ampliada.close()


def test_ampliada_sem_camadas_nao_tem_o_filtro(app, tmp_path):
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_ampliada import TelaAmpliada
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(_pdf_sem_camadas(tmp_path), filtro=ORIGINAL, dividir=False)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    try:
        tela.carregar(projeto, HistoricoAcoes(), previas)
        ampliada = TelaAmpliada(tela)
        assert TIRAR_FUNDO not in ampliada.botoes_de_filtro
        assert ampliada.combo_comparar.findData(TIRAR_FUNDO) < 0
        ampliada.close()
    finally:
        previas.parar()
