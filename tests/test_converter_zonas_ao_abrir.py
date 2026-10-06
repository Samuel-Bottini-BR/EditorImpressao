"""Converter as zonas do livro inteiro, por tras, ao abrir (decisao Z1 (b) do
Samuel, conferencia 9, 05/10/2026).

Pedido literal: "O livro inteiro, por tras, ao abrir - ele poderia fazer isso
quando abre o livro e fica carregando dai né?". Antes (D2, commit 7cb56c1),
cada pagina de projeto antigo so era convertida (ganhava a geometria das
zonas, e no disco as zonas na folha original) quando era DESENHADA. Agora o
livro inteiro e convertido numa tarefa de fundo assim que o trabalho salvo
volta (ui/janela_principal._analise_pronta), uma folha por vez na memoria.
Pagina que o Kaique abrir antes da tarefa chegar nela continua sendo
convertida na hora, como antes.

O que estes testes prendem (pedido da gerente, 05/10/2026):
1. projeto antigo com zonas em varias paginas: todas convertidas ao abrir;
2. as zonas ficam iguais na tela e o PDF sai identico ao do programa antigo;
3. fechar no meio e reabrir: continua de onde parou (e a copia de seguranca
   do projeto.json antigo continua sendo feita, uma vez);
4. a janela nao congela enquanto converte, e o andamento aparece na faixa da
   tela de conferir;
mais: pagina mexida no meio da conversao nao e anotada com o preparo velho, e
pagina ja convertida pela previa nao e tocada.

Paginas sinteticas (PDF de verdade gravado na hora), para nao depender do
gabarito, que fica fora do git.
"""

from __future__ import annotations

import copy
import json
import time

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import pipeline  # noqa: E402
from core import zonas_na_folha as zf  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.selecao import GRAVURA, MAO, PAPEL, POLIGONO, RETANGULO, SUBTRAIR, Regiao  # noqa: E402
from modelos import (METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA,  # noqa: E402
                     ConfigFolha, ConfigPagina, Projeto)


# ---------------------------------------------------------------------------
# O livro de teste: 4 folhas, 6 paginas, 5 delas com zonas
# ---------------------------------------------------------------------------

def _folha_sintetica(semente: int) -> np.ndarray:
    """Folha de 1400 x 1000 pontos (200 DPI) com linhas de texto giradas 1,5
    grau (o endireitar automatico acha um angulo) e um quadrado vermelho."""
    img = np.full((1400, 1000, 3), 236, np.uint8)
    for y in range(160, 1250, 34):
        for x in range(110, 880, 70):
            cv2.rectangle(img, (x, y), (x + 52, y + 14), (45, 45, 45), -1)
    dx = 40 * (semente % 3)
    cv2.rectangle(img, (520 + dx, 520), (720 + dx, 700), (40, 40, 210), -1)
    m = cv2.getRotationMatrix2D((500, 700), 1.5, 1.0)
    return cv2.warpAffine(img, m, (1000, 1400), borderValue=(236, 236, 236))


def _gravar_pdf(caminho) -> None:
    folhas = [
        _folha_sintetica(0),                                           # 0: inteira, automatica
        np.hstack([_folha_sintetica(1), _folha_sintetica(2)]),         # 1: dividida em duas
        _folha_sintetica(3),                                           # 2: girada 90, angulo a mao
        _folha_sintetica(4),                                           # 3: corte a mao
    ]
    doc = fitz.open()
    for img in folhas:
        ok, png = cv2.imencode(".png", img)
        assert ok
        pagina = doc.new_page(width=img.shape[1] * 72 / 200, height=img.shape[0] * 72 / 200)
        pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()


def _zonas(k: int) -> list[dict]:
    return [
        Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.3 + 0.02 * k, 0.32), (0.62, 0.5)],
               origem=MAO, filtro=ORIGINAL).para_dicionario(),
        Regiao(tipo=PAPEL, forma=POLIGONO, pontos=[(0.1, 0.7), (0.4, 0.75), (0.25, 0.92)],
               operacao=SUBTRAIR, origem=MAO, suavidade=0.01).para_dicionario(),
    ]


def _projeto(caminho) -> Projeto:
    projeto = Projeto(caminho_entrada=str(caminho), nome="livro")
    projeto.dividir_folhas = True
    projeto.endireitar = True
    projeto.cortar_bordas = True
    projeto.limpar = True
    projeto.montar_cadernos = False
    projeto.detectar_regioes = False          # nada de procurar gravura: so as zonas a mao
    projeto.qualidade_dpi = 150               # rapido; a conta e a mesma em qualquer DPI
    projeto.folhas = [
        ConfigFolha(indice=0, dividir=False, e_paisagem=False),
        ConfigFolha(indice=1, dividir=True, posicao_corte=0.5, e_paisagem=True),
        ConfigFolha(indice=2, dividir=False, rotacao=90, e_paisagem=False),
        ConfigFolha(indice=3, dividir=False, e_paisagem=False),
    ]
    projeto.paginas = [
        ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO),
        ConfigPagina(indice=1, folha=1, metade=METADE_ESQUERDA, filtro=PRETO_E_BRANCO),
        ConfigPagina(indice=2, folha=1, metade=METADE_DIREITA, filtro=PRETO_E_BRANCO),
        ConfigPagina(indice=3, folha=2, filtro=PRETO_E_BRANCO, angulo_manual=-0.8),
        ConfigPagina(indice=4, folha=3, filtro=PRETO_E_BRANCO, recorte=(0.05, 0.06, 0.88, 0.86)),
        ConfigPagina(indice=5, folha=3, metade=METADE_INTEIRA, filtro=PRETO_E_BRANCO),  # sem zonas
    ]
    for k, pagina in enumerate(projeto.paginas[:5]):
        pagina.selecao = _zonas(k)
    return projeto


COM_ZONAS = 5


def _dicionario_antigo(caminho) -> dict:
    """O projeto.json como o programa gravava antes de 05/10: so "selecao", em
    fracao da pagina, sem os campos novos."""
    dados = _projeto(caminho).para_dicionario()
    for pagina in dados["paginas"]:
        pagina.pop("geometria_das_zonas", None)
        pagina.pop(zf.CAMPO_NA_FOLHA, None)
    return json.loads(json.dumps(dados))


@pytest.fixture
def pdf(tmp_path):
    caminho = tmp_path / "livro.pdf"
    _gravar_pdf(caminho)
    pipeline._GEOMETRIAS.clear()
    return caminho


def _imagens_do_pdf(caminho) -> list[bytes]:
    doc = fitz.open(str(caminho))
    try:
        return [doc.extract_image(info[0])["image"]
                for pagina in doc for info in pagina.get_images(full=True)]
    finally:
        doc.close()


def _selecoes(projeto) -> list[list[dict]]:
    return [copy.deepcopy(p.selecao) for p in projeto.paginas]


# ---------------------------------------------------------------------------
# 1. Todas as paginas com zonas sao convertidas
# ---------------------------------------------------------------------------

def test_paginas_por_converter_sao_as_antigas_com_zonas(pdf):
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    pendentes = zf.paginas_por_converter(projeto)
    assert [p.indice for p in pendentes] == [0, 1, 2, 3, 4]      # a 5 nao tem zonas


def test_converte_todas_as_paginas_com_zonas(pdf):
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    antes = _selecoes(projeto)
    andamento = []
    convertidas = pipeline.converter_zonas_do_livro(
        projeto, progresso=lambda feitas, total: andamento.append((feitas, total)))
    assert convertidas == COM_ZONAS
    assert andamento[-1] == (COM_ZONAS, COM_ZONAS)
    assert [f for f, _ in andamento] == sorted(f for f, _ in andamento)
    assert not zf.paginas_por_converter(projeto)
    for pagina in projeto.paginas[:5]:
        assert zf.geometria_valida(pagina.geometria_das_zonas)
    assert projeto.paginas[5].geometria_das_zonas is None        # sem zonas: nada
    assert _selecoes(projeto) == antes                           # nada andou
    gravado = projeto.para_dicionario()
    assert all(p.get(zf.CAMPO_NA_FOLHA) for p in gravado["paginas"][:5])
    # de novo: nada a fazer
    assert pipeline.converter_zonas_do_livro(projeto) == 0


def test_a_geometria_anotada_e_a_mesma_da_previa_e_do_pdf(pdf):
    """A conversao anota o preparo que a previa (outro DPI) e o PDF dariam:
    desenhar depois nao leva zona nenhuma."""
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    antes = _selecoes(projeto)
    pipeline.converter_zonas_do_livro(projeto)
    anotadas = [copy.deepcopy(p.geometria_das_zonas) for p in projeto.paginas]
    doc = abrir_pdf(str(pdf))
    try:
        for pagina in projeto.paginas:
            for dpi in (pipeline.DPI_PREVIA, projeto.qualidade_dpi):
                levou = []
                original = zf.acompanhar

                def espiao(p, g, _orig=original):
                    r = _orig(p, g)
                    levou.append(r)
                    return r

                zf.acompanhar = espiao
                try:
                    pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                finally:
                    zf.acompanhar = original
                assert levou == [False], (pagina.indice, dpi)
    finally:
        doc.close()
    assert _selecoes(projeto) == antes
    for a, pagina in zip(anotadas[:5], projeto.paginas[:5]):
        assert zf.mesma_geometria(a, pagina.geometria_das_zonas)


# ---------------------------------------------------------------------------
# 2. Zonas iguais na tela e PDF identico
# ---------------------------------------------------------------------------

def test_zonas_iguais_e_pdf_identico_ao_do_programa_antigo(pdf, tmp_path, monkeypatch):
    antigo = _dicionario_antigo(pdf)

    # ANTES: o programa de antes (sem acompanhar a geometria)
    with monkeypatch.context() as m:
        m.setattr(zf, "acompanhar", lambda pagina, geometria: False)
        pipeline._GEOMETRIAS.clear()
        projeto_a = Projeto.de_dicionario(copy.deepcopy(antigo))
        projeto_a.caminho_saida = str(tmp_path / "antes.pdf")
        pipeline.processar(projeto_a)

    # DEPOIS: abre, converte o livro inteiro por tras, grava, reabre, gera
    pipeline._GEOMETRIAS.clear()
    projeto_b = Projeto.de_dicionario(copy.deepcopy(antigo))
    zonas = _selecoes(projeto_b)
    assert pipeline.converter_zonas_do_livro(projeto_b) == COM_ZONAS
    assert _selecoes(projeto_b) == zonas                      # na tela: as mesmas
    gravado = json.loads(json.dumps(projeto_b.para_dicionario()))
    for pagina, original in zip(gravado["paginas"], zonas):
        assert pagina["selecao"] == original                   # copia p/ o programa antigo
    projeto_c = Projeto.de_dicionario(gravado)
    assert _selecoes(projeto_c) == zonas                       # reaberto: bit a bit
    projeto_c.caminho_saida = str(tmp_path / "depois.pdf")
    pipeline.processar(projeto_c)
    assert _selecoes(projeto_c) == zonas

    antes, depois = _imagens_do_pdf(tmp_path / "antes.pdf"), _imagens_do_pdf(tmp_path / "depois.pdf")
    assert len(antes) == 6 and antes == depois


def test_depois_de_converter_mudar_o_corte_leva_a_zona_junto(pdf):
    """O motivo de converter antes: pagina convertida e depois mexida no
    corte (sem nunca ter sido desenhada) leva as zonas para o mesmo pedaco
    do papel; sem a conversao, a zona ficava nas mesmas fracoes (andava)."""
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    pipeline.converter_zonas_do_livro(projeto)
    pagina = projeto.paginas[0]
    antes = copy.deepcopy(pagina.selecao)
    pagina.recorte = (0.15, 0.2, 0.8, 0.7)
    doc = abrir_pdf(str(pdf))
    try:
        pipeline.renderizar_pagina(doc, projeto, pagina, dpi=pipeline.DPI_PREVIA)
    finally:
        doc.close()
    assert pagina.selecao != antes


# ---------------------------------------------------------------------------
# 3. Fechar no meio e reabrir: continua de onde parou
# ---------------------------------------------------------------------------

def _resumo(pasta):
    import projetos

    return projetos.Resumo(pasta=str(pasta), nome="livro", caminho_entrada="x.pdf")


def test_fechar_no_meio_e_reabrir_continua_de_onde_parou(pdf, tmp_path):
    import projetos

    pasta = tmp_path / "projeto"
    pasta.mkdir()
    antigo = _dicionario_antigo(pdf)
    arquivo = pasta / projetos.ARQUIVO_ESTADO
    arquivo.write_text(json.dumps(antigo, ensure_ascii=False, indent=1), encoding="utf-8")
    bytes_antigos = arquivo.read_bytes()
    resumo = _resumo(pasta)

    projeto = projetos.carregar_estado(resumo)
    zonas = _selecoes(projeto)
    andamento = []
    convertidas = pipeline.converter_zonas_do_livro(
        projeto, progresso=lambda f, t: andamento.append(f),
        cancelado=lambda: len(andamento) >= 2)            # "fechou" depois de 2
    assert convertidas == 2
    projetos.salvar_estado(resumo, projeto)                # o closeEvent grava

    # o arquivo e um projeto valido, com 2 paginas no formato novo
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert sum(1 for p in dados["paginas"] if p.get(zf.CAMPO_NA_FOLHA)) == 2
    copias = list(pasta.glob("projeto.antigo-zonas-na-folha-*.json"))
    assert len(copias) == 1 and copias[0].read_bytes() == bytes_antigos

    # reabre: so as 3 que faltam
    pipeline._GEOMETRIAS.clear()
    reaberto = projetos.carregar_estado(resumo)
    assert _selecoes(reaberto) == zonas
    assert len(zf.paginas_por_converter(reaberto)) == COM_ZONAS - 2
    assert pipeline.converter_zonas_do_livro(reaberto) == COM_ZONAS - 2
    assert _selecoes(reaberto) == zonas
    projetos.salvar_estado(resumo, reaberto)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert sum(1 for p in dados["paginas"] if p.get(zf.CAMPO_NA_FOLHA)) == COM_ZONAS
    assert len(list(pasta.glob("projeto.antigo-zonas-na-folha-*"))) == 1   # nenhuma outra copia
    assert _selecoes(projetos.carregar_estado(resumo)) == zonas


def test_cancelar_antes_de_comecar_nao_converte_nada(pdf):
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    assert pipeline.converter_zonas_do_livro(projeto, cancelado=lambda: True) == 0
    assert len(zf.paginas_por_converter(projeto)) == COM_ZONAS


# ---------------------------------------------------------------------------
# A pessoa trabalhando enquanto converte
# ---------------------------------------------------------------------------

def test_pagina_ja_convertida_pela_previa_nao_e_tocada(pdf):
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    doc = abrir_pdf(str(pdf))
    try:
        pipeline.renderizar_pagina(doc, projeto, projeto.paginas[1], dpi=pipeline.DPI_PREVIA)
    finally:
        doc.close()
    da_previa = projeto.paginas[1].geometria_das_zonas
    assert zf.geometria_valida(da_previa)
    assert pipeline.converter_zonas_do_livro(projeto) == COM_ZONAS - 1
    assert projeto.paginas[1].geometria_das_zonas is da_previa


def test_pagina_mexida_no_meio_nao_e_anotada_com_o_preparo_velho(pdf, monkeypatch):
    """O Kaique muda o corte de uma pagina enquanto a tarefa calcula o
    preparo dela: a tarefa nao anota o preparo de antes (a previa anota o de
    agora quando desenhar, como antes da Z1)."""
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    alvo = projeto.paginas[0]
    original = pipeline._guardar_geometria

    def no_meio(folha, pagina, projeto_, img):
        original(folha, pagina, projeto_, img)
        if pagina is alvo:
            alvo.recorte = (0.1, 0.1, 0.8, 0.8)        # a mao da pessoa, no meio

    monkeypatch.setattr(pipeline, "_guardar_geometria", no_meio)
    pipeline.converter_zonas_do_livro(projeto)
    assert alvo.geometria_das_zonas is None
    assert [p.indice for p in zf.paginas_por_converter(projeto)] == [0]


def test_pdf_que_sumiu_nao_derruba(pdf, tmp_path):
    projeto = Projeto.de_dicionario(_dicionario_antigo(pdf))
    projeto.caminho_entrada = str(tmp_path / "nao-existe.pdf")
    assert pipeline.converter_zonas_do_livro(projeto) == 0
    assert len(zf.paginas_por_converter(projeto)) == COM_ZONAS


# ---------------------------------------------------------------------------
# 4. Na janela: por tras, sem congelar, com o andamento na faixa
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


@pytest.fixture
def janela(app, raiz, monkeypatch):
    from ui import tarefas
    from ui.janela_principal import JanelaPrincipal

    # As previas da tela convertem as paginas que desenham (como antes da
    # Z1): aqui elas devolvem uma folha branca sem desenhar, para a conta do
    # teste ser so a da tarefa de fundo. (A previa que chega antes da tarefa
    # e testada acima, em test_pagina_ja_convertida_pela_previa_nao_e_tocada.)
    monkeypatch.setattr(tarefas, "renderizar_pagina",
                        lambda doc, projeto, pagina, dpi=0: (np.full((90, 64, 3), 255, np.uint8), False))
    janela = JanelaPrincipal()
    janela.avisos = []
    monkeypatch.setattr(janela, "avisar",
                        lambda mensagem, titulo="": janela.avisos.append(mensagem))
    yield janela
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _abrir_projeto_antigo(janela, pdf):
    """Grava o projeto antigo como trabalho salvo do livro e o abre pela
    janela, como o Kaique: abrir o livro e "Conferir" (sem a tarefa da
    analise, que so propoe o que o salvo vai substituir)."""
    import projetos

    janela.abrir_livro(str(pdf))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    arquivo = __import__("pathlib").Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    antigo = _dicionario_antigo(pdf)
    antigo["caminho_entrada"] = str(pdf)
    arquivo.write_text(json.dumps(antigo, ensure_ascii=False, indent=1), encoding="utf-8")
    analisado = Projeto.de_dicionario(copy.deepcopy(antigo))
    for pagina in analisado.paginas:
        pagina.selecao = []
    janela._analise_pronta(analisado)
    return arquivo


def _esperar(app, condicao, limite_s=60.0) -> float:
    """Roda o laco de eventos ate `condicao()`; devolve o maior intervalo
    (s) em que um relogio de 20 ms ficou sem tocar."""
    from PySide6.QtCore import QTimer

    toques = [time.perf_counter()]
    relogio = QTimer()
    relogio.setInterval(20)
    relogio.timeout.connect(lambda: toques.append(time.perf_counter()))
    relogio.start()
    fim = time.perf_counter() + limite_s
    try:
        while not condicao() and time.perf_counter() < fim:
            app.processEvents()
            time.sleep(0.005)
    finally:
        relogio.stop()
    toques.append(time.perf_counter())
    return max(b - a for a, b in zip(toques, toques[1:]))


def test_janela_converte_por_tras_sem_congelar_e_mostra_o_andamento(janela, app, pdf,
                                                                   monkeypatch):
    import projetos

    textos = set()
    original = janela.tela_conferir.mostrar_andamento_das_marcacoes

    def anotar(feitas, total):
        original(feitas, total)
        textos.add(janela.tela_conferir.texto_faixa.text())

    monkeypatch.setattr(janela.tela_conferir, "mostrar_andamento_das_marcacoes", anotar)
    # Cada folha leva 0,4 s a mais (sem segurar o Python): se a conversao
    # rodasse no fio da janela, ela ficaria parada 2 s ou mais.
    original_guardar = pipeline._guardar_geometria

    def devagar(*args, **kwargs):
        time.sleep(0.4)
        return original_guardar(*args, **kwargs)

    monkeypatch.setattr(pipeline, "_guardar_geometria", devagar)
    arquivo = _abrir_projeto_antigo(janela, pdf)
    tarefa = janela.conversao_das_zonas
    assert tarefa is not None, "a conversao nao comecou ao abrir"
    # a janela ja esta na conferencia, e o livro ainda nao foi convertido:
    # o trabalho e por tras
    assert zf.paginas_por_converter(janela.projeto)
    zonas = _selecoes(janela.projeto)

    pior = _esperar(app, lambda: not tarefa.isRunning() and janela.conversao_das_zonas is None)
    for _ in range(20):
        app.processEvents()

    assert not zf.paginas_por_converter(janela.projeto)
    assert _selecoes(janela.projeto) == zonas
    assert any("Preparando as marcações do livro..." in t and f"de {COM_ZONAS}" in t
               for t in textos), textos
    assert "Preparando as marcações" not in janela.tela_conferir.texto_faixa.text()
    assert pior < 1.0, f"a janela ficou {pior:.2f} s sem responder"

    janela._salvar_agora()
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert sum(1 for p in dados["paginas"] if p.get(zf.CAMPO_NA_FOLHA)) == COM_ZONAS
    assert len(list(arquivo.parent.glob("projeto.antigo-zonas-na-folha-*.json"))) == 1
    assert projetos.carregar_estado(janela.resumo) is not None


def test_a_copia_e_o_projeto_de_antes_byte_a_byte(janela, app, pdf):
    """R2 do verificador (05/10/2026): abrir um projeto antigo pela janela
    grava logo (no formato antigo, acrescentando "geometria_das_zonas":
    null) e so depois converte. A copia de seguranca tem de ser o arquivo
    como estava antes de o programa novo tocar nele, byte a byte."""
    import projetos

    original = projetos.salvar_estado
    lidos = []

    def anotar_antes(resumo, projeto):
        caminho = __import__("pathlib").Path(resumo.pasta) / projetos.ARQUIVO_ESTADO
        if caminho.is_file() and not lidos:
            lidos.append(caminho.read_bytes())         # o arquivo antes da 1a gravacao
        original(resumo, projeto)

    projetos.salvar_estado = anotar_antes
    try:
        arquivo = _abrir_projeto_antigo(janela, pdf)
        tarefa = janela.conversao_das_zonas
        _esperar(app, lambda: not tarefa.isRunning() and janela.conversao_das_zonas is None)
        janela._salvar_agora()
    finally:
        projetos.salvar_estado = original
    copias = list(arquivo.parent.glob("projeto.antigo-zonas-na-folha-*.json"))
    assert len(copias) == 1
    assert lidos and copias[0].read_bytes() == lidos[0]
    assert b"geometria_das_zonas" not in copias[0].read_bytes()
    assert zf.tem_formato_novo(json.loads(arquivo.read_text(encoding="utf-8")))


def test_fechar_a_janela_no_meio_nao_estraga_e_continua(janela, app, pdf, monkeypatch):
    import projetos

    # cada folha demora um pouco mais, para dar tempo de fechar no meio
    original = pipeline._guardar_geometria

    def devagar(*args, **kwargs):
        time.sleep(0.3)
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline, "_guardar_geometria", devagar)
    arquivo = _abrir_projeto_antigo(janela, pdf)
    tarefa = janela.conversao_das_zonas
    assert tarefa is not None
    _esperar(app, lambda: tarefa.feitas >= 1, limite_s=30)
    janela.close()                                   # fecha no meio
    assert not tarefa.isRunning()
    dados = json.loads(arquivo.read_text(encoding="utf-8"))   # JSON inteiro
    feitas = sum(1 for p in dados["paginas"] if p.get(zf.CAMPO_NA_FOLHA))
    assert 1 <= feitas < COM_ZONAS
    reaberto = projetos.carregar_estado(janela.resumo)
    assert len(zf.paginas_por_converter(reaberto)) == COM_ZONAS - feitas


def test_trocar_de_livro_no_meio_para_a_conversao_e_grava_o_feito(janela, app, pdf, monkeypatch):
    original = pipeline._guardar_geometria

    def devagar(*args, **kwargs):
        time.sleep(0.3)
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline, "_guardar_geometria", devagar)
    arquivo = _abrir_projeto_antigo(janela, pdf)
    tarefa = janela.conversao_das_zonas
    _esperar(app, lambda: tarefa.feitas >= 1, limite_s=30)
    janela.abrir_livro(str(pdf))                     # outro livro (aqui, o mesmo de novo)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    assert janela.conversao_das_zonas is None
    assert tarefa.foi_cancelada
    _esperar(app, lambda: not tarefa.isRunning(), limite_s=30)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    feitas = sum(1 for p in dados["paginas"] if p.get(zf.CAMPO_NA_FOLHA))
    assert 1 <= feitas < COM_ZONAS
    assert "Preparando as marcações" not in janela.tela_conferir.texto_faixa.text()
