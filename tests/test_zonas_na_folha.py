"""Zonas da aba Marcar guardadas na FOLHA ORIGINAL (decisao D2 do Samuel, 02/10/2026).

Pedido: "Sim, pode mudar (com copia de seguranca dos projetos)". Antes, as
zonas eram guardadas em fracao da pagina ja dividida, cortada e endireitada;
mudar o corte ou o angulo depois deixava a zona sobre outro pedaco do papel.
Agora a verdade no projeto.json e a folha original (core/zonas_na_folha.py),
e a forma como a tela e o pipeline recebem as zonas na memoria nao muda.

O que estes testes prendem (pedido da gerente, 05/10/2026):
1. projeto antigo convertido da EXATAMENTE as mesmas zonas na tela e o mesmo
   PDF que antes;
2. mudar corte/angulo depois mantem a zona sobre o mesmo pedaco da folha;
3. desfazer/refazer continua funcionando;
mais: a conta folha <-> pagina vai e volta sem perder nada, o programa
antigo (que nao conhece os campos novos) continua lendo a copia certa, e a
copia de seguranca do projeto.json antigo e feita uma vez e nunca apagada.

As paginas sao sinteticas (gravadas num PDF de verdade, como o acervo), para
nao depender do gabarito, que fica fora do git.
"""

from __future__ import annotations

import copy
import json

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import pipeline
from core import zonas_na_folha as zf
from core.filtros import ORIGINAL, PRETO_E_BRANCO
from core.pdf_io import abrir_pdf
from core.selecao import (ELIPSE, GRAVURA, MAO, PAPEL, POLIGONO, RETANGULO, SUBTRAIR, TRACO,
                          Regiao, Selecao)
from modelos import ConfigFolha, ConfigPagina, Projeto


# ---------------------------------------------------------------------------
# 0. A conta pura: folha <-> pagina
# ---------------------------------------------------------------------------

def _regioes_de_exemplo() -> list[dict]:
    return [
        Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.2, 0.3), (0.55, 0.62)], origem=MAO,
               filtro=ORIGINAL).para_dicionario(),
        Regiao(tipo=GRAVURA, forma=ELIPSE, pontos=[(0.61, 0.1), (0.9, 0.33)], origem=MAO).para_dicionario(),
        Regiao(tipo=PAPEL, forma=POLIGONO, pontos=[(0.1, 0.7), (0.4, 0.75), (0.25, 0.95)],
               operacao=SUBTRAIR, origem=MAO, suavidade=0.01).para_dicionario(),
        Regiao(tipo=GRAVURA, forma=TRACO, pontos=[(0.3, 0.4), (0.5, 0.45), (0.7, 0.41)],
               espessura=0.03, origem=MAO).para_dicionario(),
    ]


GEOMETRIAS = [
    zf.geometria_do_desenho(0.7, 0, None, "inteira", None, 0.0),
    zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.05, 0.04, 0.9, 0.91), 1.7),
    zf.geometria_do_desenho(1.45, 0, 0.57, "esquerda", (0.1, 0.02, 0.8, 0.95), -2.3),
    zf.geometria_do_desenho(1.45, 0, 0.57, "direita", (0.0, 0.1, 0.92, 0.85), 0.6),
    zf.geometria_do_desenho(0.7, 90, None, "inteira", (0.03, 0.03, 0.94, 0.9), -0.4),
    zf.geometria_do_desenho(0.66, 180, None, "inteira", None, 3.0),
    zf.geometria_do_desenho(1.3, 270, 0.5, "direita", (0.02, 0.05, 0.9, 0.9), 0.0),
]


@pytest.mark.parametrize("g", GEOMETRIAS)
def test_folha_e_volta_devolve_as_mesmas_zonas(g):
    regioes = _regioes_de_exemplo()
    na_folha = zf.pagina_para_folha(regioes, g)
    de_volta = zf.folha_para_pagina(na_folha, g)
    assert len(de_volta) == len(regioes)
    for a, b in zip(regioes, de_volta):
        assert a["forma"] == b["forma"] and a["tipo"] == b["tipo"] and a["filtro"] == b["filtro"]
        assert len(a["pontos"]) == len(b["pontos"])
        for p, q in zip(a["pontos"], b["pontos"]):
            assert abs(p[0] - q[0]) < 1e-12 and abs(p[1] - q[1]) < 1e-12
        assert abs(a["espessura"] - b["espessura"]) < 1e-12
        assert abs(a["suavidade"] - b["suavidade"]) < 1e-12
    # nada de entrada foi mexido (o desfazer guarda essas listas)
    assert regioes == _regioes_de_exemplo()


def test_retangulo_girado_vira_quadrilatero_e_desenha_no_lugar():
    """Mudar so o angulo: o retangulo nao fica mais alinhado com a pagina e
    passa a ter 4 pontos; desenhado, cobre o mesmo lugar que a conta diz."""
    antes = zf.geometria_do_desenho(0.7, 0, None, "inteira", None, 0.0)
    depois = zf.geometria_do_desenho(0.7, 0, None, "inteira", None, 2.0)
    regiao = Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.3, 0.3), (0.6, 0.5)]).para_dicionario()
    levada = zf.trocar_de_geometria([regiao], antes, depois)[0]
    assert len(levada["pontos"]) == 4
    sel = Selecao.de_lista([levada])
    assert len(sel.regioes) == 1
    mascara = sel.mascara(1000, 700, GRAVURA)
    # o centro do retangulo continua dentro (giro em volta do centro da pagina)
    assert mascara[400, int(0.45 * 700)]
    area = mascara.mean()
    assert abs(area - 0.3 * 0.2) < 0.01
    # e volta a ter 2 pontos quando a geometria volta
    de_volta = zf.trocar_de_geometria([levada], depois, antes)[0]
    assert len(de_volta["pontos"]) == 2
    assert np.allclose(de_volta["pontos"], regiao["pontos"], atol=1e-12)


def test_folha_inteira_em_branco_continua_a_pagina_inteira():
    """O retangulo (0,0)-(1,1) de PAPEL da aba Marcar quer dizer 'a folha toda
    em branco', qualquer que seja o corte (filtros.FOLHA_INTEIRA_EM_BRANCO)."""
    a = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 0.0)
    b = zf.geometria_do_desenho(0.7, 0, None, "inteira", (0.0, 0.0, 1.0, 1.0), 1.5)
    folha = Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(0.0, 0.0), (1.0, 1.0)], origem=MAO).para_dicionario()
    levada = zf.trocar_de_geometria([folha], a, b)[0]
    assert levada["pontos"] == [[0.0, 0.0], [1.0, 1.0]]
    assert "pagina_inteira" not in levada


def test_mesma_geometria_ignora_o_arredondamento_da_proporcao():
    a = zf.geometria_do_desenho(0.7081, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 1.2)
    b = zf.geometria_do_desenho(0.7085, 0, None, "inteira", (0.1, 0.1, 0.8, 0.8), 1.2)
    c = zf.geometria_do_desenho(0.7085, 0, None, "inteira", (0.1, 0.1, 0.8, 0.81), 1.2)
    assert zf.mesma_geometria(a, b)
    assert not zf.mesma_geometria(a, c)


# ---------------------------------------------------------------------------
# PDF sintetico: texto torto e um quadrado vermelho num lugar conhecido
# ---------------------------------------------------------------------------

def _folha_sintetica() -> np.ndarray:
    """Folha de 1400 x 1000 pontos (a 200 DPI), com linhas de texto giradas
    1,5 grau (o endireitar automatico acha um angulo), margem de papel, e um
    quadrado vermelho (a "gravura") que serve de marco no papel."""
    img = np.full((1400, 1000, 3), 236, np.uint8)
    for y in range(160, 1250, 34):
        for x in range(110, 880, 70):
            cv2.rectangle(img, (x, y), (x + 52, y + 14), (45, 45, 45), -1)
    cv2.rectangle(img, (560, 520), (760, 700), (40, 40, 210), -1)
    m = cv2.getRotationMatrix2D((500, 700), 1.5, 1.0)
    return cv2.warpAffine(img, m, (1000, 1400), borderValue=(236, 236, 236))


def _gravar_pdf(caminho, img: np.ndarray) -> None:
    ok, png = cv2.imencode(".png", img)
    assert ok
    doc = fitz.open()
    pagina = doc.new_page(width=img.shape[1] * 72 / 200, height=img.shape[0] * 72 / 200)
    pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()


def _projeto(caminho, filtro=PRETO_E_BRANCO, limpar=True) -> Projeto:
    projeto = Projeto(caminho_entrada=str(caminho), nome="zonas")
    projeto.dividir_folhas = False
    projeto.endireitar = True
    projeto.cortar_bordas = True
    projeto.limpar = limpar
    projeto.montar_cadernos = False
    projeto.detectar_regioes = True
    projeto.folhas = [ConfigFolha(indice=0, dividir=False, e_paisagem=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=filtro)]
    return projeto


def _vermelho(img: np.ndarray) -> np.ndarray:
    b, g, r = (img[..., k].astype(int) for k in range(3))
    return (r > 150) & (g < 110) & (b < 110)


def _caixa(mascara: np.ndarray) -> tuple[float, float, float, float]:
    ys, xs = np.nonzero(mascara)
    h, w = mascara.shape
    return xs.min() / w, ys.min() / h, (xs.max() + 1) / w, (ys.max() + 1) / h


def _desenhar(caminho, projeto, dpi=100) -> np.ndarray:
    doc = abrir_pdf(str(caminho))
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=dpi)
    finally:
        doc.close()
    return img


@pytest.fixture
def pdf(tmp_path):
    caminho = tmp_path / "folha.pdf"
    _gravar_pdf(caminho, _folha_sintetica())
    pipeline._GEOMETRIAS.clear()
    return caminho


def _zona_sobre_o_vermelho(caminho) -> list[dict]:
    """A zona que a pessoa desenharia em volta do quadrado vermelho, na pagina
    como o programa mostra hoje (cortada e endireitada sozinho)."""
    projeto = _projeto(caminho, limpar=False)
    img = _desenhar(caminho, projeto)
    x0, y0, x1, y1 = _caixa(_vermelho(img))
    return [Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)], origem=MAO,
                   filtro=ORIGINAL).para_dicionario()]


# ---------------------------------------------------------------------------
# 1. Projeto antigo: mesmas zonas na tela, mesmo PDF
# ---------------------------------------------------------------------------

def _dicionario_antigo(caminho, zonas) -> dict:
    """O projeto.json como o programa gravava antes de 05/10: so "selecao", em
    fracao da pagina, sem os campos novos."""
    projeto = _projeto(caminho)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    dados = projeto.para_dicionario()
    for pagina in dados["paginas"]:
        pagina.pop("geometria_das_zonas", None)
        pagina.pop(zf.CAMPO_NA_FOLHA, None)
    return json.loads(json.dumps(dados))


def _imagens_do_pdf(caminho) -> list[bytes]:
    doc = fitz.open(str(caminho))
    try:
        saida = []
        for pagina in doc:
            for info in pagina.get_images(full=True):
                saida.append(doc.extract_image(info[0])["image"])
        return saida
    finally:
        doc.close()


def test_projeto_antigo_da_as_mesmas_zonas_e_o_mesmo_pdf(pdf, tmp_path, monkeypatch):
    zonas = _zona_sobre_o_vermelho(pdf)
    antigo = _dicionario_antigo(pdf, zonas)

    # ANTES: o programa de antes (sem acompanhar a geometria)
    with monkeypatch.context() as m:
        m.setattr(zf, "acompanhar", lambda pagina, geometria: False)
        pipeline._GEOMETRIAS.clear()
        projeto_a = Projeto.de_dicionario(copy.deepcopy(antigo))
        projeto_a.caminho_saida = str(tmp_path / "antes.pdf")
        pipeline.processar(projeto_a)

    # DEPOIS: abre o antigo, a previa converte, grava no formato novo, reabre
    pipeline._GEOMETRIAS.clear()
    projeto_b = Projeto.de_dicionario(copy.deepcopy(antigo))
    assert projeto_b.paginas[0].selecao == zonas            # abre igual
    assert projeto_b.paginas[0].geometria_das_zonas is None
    _desenhar(pdf, projeto_b)
    assert projeto_b.paginas[0].selecao == zonas            # na tela: as mesmas zonas
    assert zf.geometria_valida(projeto_b.paginas[0].geometria_das_zonas)
    gravado = json.loads(json.dumps(projeto_b.para_dicionario()))
    assert gravado["paginas"][0][zf.CAMPO_NA_FOLHA]          # a verdade na folha
    assert gravado["paginas"][0]["selecao"] == zonas         # copia p/ o programa antigo
    projeto_c = Projeto.de_dicionario(gravado)
    assert projeto_c.paginas[0].selecao == zonas             # reaberto: bit a bit igual
    _desenhar(pdf, projeto_c)
    assert projeto_c.paginas[0].selecao == zonas
    projeto_c.caminho_saida = str(tmp_path / "depois.pdf")
    pipeline.processar(projeto_c)

    antes, depois = _imagens_do_pdf(tmp_path / "antes.pdf"), _imagens_do_pdf(tmp_path / "depois.pdf")
    assert antes and antes == depois


def test_programa_antigo_le_a_copia_certa(pdf):
    """Quem abre o projeto novo com o programa instalado de antes (que descarta
    campos que nao conhece) recebe as zonas certas em fracao da pagina."""
    zonas = _zona_sobre_o_vermelho(pdf)
    projeto = _projeto(pdf)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    _desenhar(pdf, projeto)
    gravado = json.loads(json.dumps(projeto.para_dicionario()))
    pagina = gravado["paginas"][0]
    conhecidos_antes = {"indice", "folha", "metade", "recorte", "angulo_manual", "filtro", "selecao"}
    assert {k: v for k, v in pagina.items() if k in conhecidos_antes}["selecao"] == zonas


def test_na_folha_manda_quando_a_copia_nao_bate(pdf):
    zonas = _zona_sobre_o_vermelho(pdf)
    projeto = _projeto(pdf)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    _desenhar(pdf, projeto)
    gravado = json.loads(json.dumps(projeto.para_dicionario()))
    gravado["paginas"][0]["selecao"][0]["pontos"] = [[0.0, 0.0], [0.1, 0.1]]   # copia estragada
    reaberto = Projeto.de_dicionario(gravado)
    assert np.allclose(reaberto.paginas[0].selecao[0]["pontos"], zonas[0]["pontos"], atol=1e-9)


def test_campo_estranho_no_disco_nao_derruba(pdf):
    zonas = _zona_sobre_o_vermelho(pdf)
    dados = _dicionario_antigo(pdf, zonas)
    dados["paginas"][0]["geometria_das_zonas"] = {"isto": "nao e geometria"}
    dados["paginas"][0][zf.CAMPO_NA_FOLHA] = "lixo"
    projeto = Projeto.de_dicionario(dados)
    assert projeto.paginas[0].selecao == zonas
    assert projeto.paginas[0].geometria_das_zonas is None


# ---------------------------------------------------------------------------
# 2. Mudar o corte e o angulo depois: a zona fica no mesmo pedaco do papel
# ---------------------------------------------------------------------------

def _cobertura(caminho, projeto) -> float:
    """Que parte do quadrado vermelho a zona cobre, na pagina desenhada agora."""
    img = _desenhar(caminho, projeto)
    vermelho = _vermelho(img)
    zona = projeto.paginas[0].obter_selecao().mascara(img.shape[0], img.shape[1], GRAVURA)
    uniao = (vermelho | zona).sum()
    return float((vermelho & zona).sum() / uniao)


@pytest.mark.parametrize("recorte, angulo", [
    ((0.02, 0.03, 0.9, 0.85), None),        # so o corte, a mao
    (None, -1.0),                            # so o angulo, a mao (o certo era +1,5)
    ((0.15, 0.2, 0.8, 0.7), 2.5),            # os dois
])
def test_mudar_corte_e_angulo_mantem_a_zona_no_lugar(pdf, recorte, angulo):
    projeto = _projeto(pdf, limpar=False)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    assert _cobertura(pdf, projeto) > 0.9                 # comeca sobre o vermelho
    projeto.paginas[0].recorte = recorte
    projeto.paginas[0].angulo_manual = angulo
    assert _cobertura(pdf, projeto) > 0.85                # continua sobre ele


def test_sem_isto_a_zona_andava(pdf, monkeypatch):
    """Prova de que o teste acima pega o defeito: com o programa de antes, a
    zona sai de cima do vermelho quando o corte muda."""
    monkeypatch.setattr(zf, "acompanhar", lambda pagina, geometria: False)
    projeto = _projeto(pdf, limpar=False)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    projeto.paginas[0].recorte = (0.15, 0.2, 0.8, 0.7)
    projeto.paginas[0].angulo_manual = 2.5
    assert _cobertura(pdf, projeto) < 0.6


def test_a_zona_vale_no_pdf_depois_de_mudar_o_corte(pdf, tmp_path, monkeypatch):
    """No PDF final (300 DPI) o filtro recebe a zona sobre o vermelho, na
    pagina com o corte e o angulo novos (a pagina que o filtro recebe ainda
    esta sem filtro: da para achar o vermelho nela)."""
    vistos = []
    original = pipeline.aplicar_filtro_com_selecao

    def espiao(img, filtro, selecao, *args, **kwargs):
        vistos.append((img.copy(), selecao))
        return original(img, filtro, selecao, *args, **kwargs)

    monkeypatch.setattr(pipeline, "aplicar_filtro_com_selecao", espiao)
    projeto = _projeto(pdf)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    _desenhar(pdf, projeto)
    projeto.paginas[0].recorte = (0.15, 0.2, 0.8, 0.7)
    projeto.paginas[0].angulo_manual = 2.5
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    vistos.clear()
    pipeline.processar(projeto)
    assert len(vistos) == 1
    img, selecao = vistos[0]
    vermelho = _vermelho(img)
    zona = selecao.mascara(img.shape[0], img.shape[1], GRAVURA)
    assert vermelho.sum() > 0
    assert (vermelho & zona).sum() / (vermelho | zona).sum() > 0.85


# ---------------------------------------------------------------------------
# 3. Desfazer e refazer
# ---------------------------------------------------------------------------

def test_desfazer_e_refazer_a_marcacao_continuam(pdf, tmp_path):
    from historico_acoes import HistoricoAcoes, montar_acao

    projeto = _projeto(pdf, limpar=False)
    zonas = _zona_sobre_o_vermelho(pdf)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    _desenhar(pdf, projeto)
    historico = HistoricoAcoes(tmp_path / "proj")
    nova = [Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(0.1, 0.1), (0.3, 0.2)], origem=MAO).para_dicionario()]
    acao = montar_acao(projeto, "aplicar_em_todas", "pagina", [0], {"selecao": nova}, "marcar")
    projeto.paginas[0].selecao = copy.deepcopy(nova)
    historico.registrar(acao)

    # grava e reabre (o projeto.json no formato novo, o historico do disco)
    projeto = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    historico = HistoricoAcoes(tmp_path / "proj")
    historico.carregar()
    assert projeto.paginas[0].selecao == nova
    historico.desfazer(projeto)
    assert projeto.paginas[0].selecao == zonas
    historico.refazer(projeto)
    assert projeto.paginas[0].selecao == nova


def test_desfazer_o_corte_devolve_as_zonas(pdf, tmp_path):
    from historico_acoes import HistoricoAcoes, montar_acao

    projeto = _projeto(pdf, limpar=False)
    zonas = _zona_sobre_o_vermelho(pdf)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    _desenhar(pdf, projeto)
    historico = HistoricoAcoes(tmp_path / "proj")
    acao = montar_acao(projeto, "recorte", "pagina", [0], {"recorte": (0.15, 0.2, 0.8, 0.7)}, "cortar")
    projeto.paginas[0].recorte = (0.15, 0.2, 0.8, 0.7)
    historico.registrar(acao)
    _desenhar(pdf, projeto)
    assert projeto.paginas[0].selecao != zonas            # a zona foi levada
    historico.desfazer(projeto)
    _desenhar(pdf, projeto)
    assert np.allclose(projeto.paginas[0].selecao[0]["pontos"], zonas[0]["pontos"], atol=1e-9)
    historico.refazer(projeto)
    assert _cobertura(pdf, projeto) > 0.85


# ---------------------------------------------------------------------------
# Copia de seguranca do projeto.json antigo
# ---------------------------------------------------------------------------

def _resumo(pasta):
    import projetos

    return projetos.Resumo(pasta=str(pasta), nome="zonas", caminho_entrada="x.pdf")


def test_copia_de_seguranca_antes_de_converter(pdf, tmp_path):
    import projetos

    pasta = tmp_path / "projeto"
    pasta.mkdir()
    zonas = _zona_sobre_o_vermelho(pdf)
    antigo = _dicionario_antigo(pdf, zonas)
    arquivo = pasta / projetos.ARQUIVO_ESTADO
    arquivo.write_text(json.dumps(antigo, ensure_ascii=False, indent=1), encoding="utf-8")
    bytes_antigos = arquivo.read_bytes()

    projeto = Projeto.de_dicionario(copy.deepcopy(antigo))
    resumo = _resumo(pasta)
    # R2 (05/10/2026): a copia vem antes de QUALQUER gravacao do programa
    # novo, mesmo a que ainda sai no formato antigo (a que a janela faz ao
    # abrir), e e o arquivo de antes byte a byte.
    projetos.salvar_estado(resumo, projeto)          # ainda nada convertido
    copias = list(pasta.glob("projeto.antigo-zonas-na-folha-*.json"))
    assert len(copias) == 1 and copias[0].read_bytes() == bytes_antigos
    assert not zf.tem_formato_novo(json.loads(arquivo.read_text(encoding="utf-8")))
    assert json.loads(arquivo.read_text(encoding="utf-8"))["paginas"][0]["selecao"] == zonas
    assert arquivo.read_bytes() != bytes_antigos     # o programa novo ja mexeu no arquivo

    _desenhar(pdf, projeto)                           # a previa converte a pagina
    projetos.salvar_estado(resumo, projeto)
    copias = list(pasta.glob("projeto.antigo-zonas-na-folha-*.json"))
    assert len(copias) == 1
    assert copias[0].read_bytes() == bytes_antigos   # o antigo, intacto
    assert zf.tem_formato_novo(json.loads(arquivo.read_text(encoding="utf-8")))
    assert copias[0] in projetos.copias_do_trabalho(resumo)   # "Tirar da lista" guarda

    projetos.salvar_estado(resumo, projeto)          # gravar de novo nao faz outra
    assert len(list(pasta.glob("projeto.antigo-zonas-na-folha-*"))) == 1
    assert copias[0].read_bytes() == bytes_antigos


def test_anotar_no_estado_tambem_copia_antes(pdf, tmp_path):
    """R2: a gravacao de so alguns campos (a pergunta do fundo, antes de o
    trabalho carregar) tambem e do programa novo: a copia vem antes, igual
    ao arquivo de antes, e uma vez so."""
    import projetos

    pasta = tmp_path / "projeto"
    pasta.mkdir()
    antigo = _dicionario_antigo(pdf, _zona_sobre_o_vermelho(pdf))
    arquivo = pasta / projetos.ARQUIVO_ESTADO
    arquivo.write_text(json.dumps(antigo, ensure_ascii=False, indent=2), encoding="utf-8")
    bytes_antigos = arquivo.read_bytes()
    resumo = _resumo(pasta)
    assert projetos.anotar_no_estado(resumo, perguntou_fundo=True)
    copias = list(pasta.glob("projeto.antigo-zonas-na-folha-*.json"))
    assert len(copias) == 1 and copias[0].read_bytes() == bytes_antigos
    projetos.salvar_estado(resumo, Projeto.de_dicionario(copy.deepcopy(antigo)))
    assert len(list(pasta.glob("projeto.antigo-zonas-na-folha-*"))) == 1


def test_sem_zonas_nao_ha_copia(pdf, tmp_path):
    import projetos

    pasta = tmp_path / "projeto"
    pasta.mkdir()
    antigo = _dicionario_antigo(pdf, [])
    (pasta / projetos.ARQUIVO_ESTADO).write_text(json.dumps(antigo), encoding="utf-8")
    projeto = Projeto.de_dicionario(copy.deepcopy(antigo))
    _desenhar(pdf, projeto)
    projetos.salvar_estado(_resumo(pasta), projeto)
    assert not list(pasta.glob("projeto.antigo-*"))


def test_sem_conseguir_a_copia_grava_no_formato_de_antes(pdf, tmp_path, monkeypatch):
    """Disco cheio na hora da copia: o trabalho continua sendo gravado (no
    formato de antes, que vale com a geometria anotada) e nada se perde."""
    import projetos

    pasta = tmp_path / "projeto"
    pasta.mkdir()
    zonas = _zona_sobre_o_vermelho(pdf)
    antigo = _dicionario_antigo(pdf, zonas)
    arquivo = pasta / projetos.ARQUIVO_ESTADO
    arquivo.write_text(json.dumps(antigo), encoding="utf-8")
    projeto = Projeto.de_dicionario(copy.deepcopy(antigo))
    _desenhar(pdf, projeto)
    projeto.paginas[0].filtro = ORIGINAL            # uma mexida nova
    monkeypatch.setattr(projetos, "_copia_antes_das_zonas_na_folha", lambda *a, **k: False)
    projetos.salvar_estado(_resumo(pasta), projeto)
    gravado = json.loads(arquivo.read_text(encoding="utf-8"))
    assert gravado["paginas"][0]["filtro"] == ORIGINAL          # a mexida foi gravada
    assert not zf.tem_formato_novo(gravado)                      # sem converter
    reaberto = Projeto.de_dicionario(gravado)
    assert reaberto.paginas[0].selecao == zonas
    assert zf.mesma_geometria(reaberto.paginas[0].geometria_das_zonas,
                              projeto.paginas[0].geometria_das_zonas)
