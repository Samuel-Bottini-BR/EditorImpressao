"""O "Limpar pontinhos" ligado ao programa (decisão do Samuel, 06/10/2026, P7).

O pedido: "Limpar pontinhos: desligado · o nosso · pouco · normal · muito",
por livro e por página, valendo no Preto e branco e no "Só as letras". De
fábrica, em 06/10, o do ScanTailor "pouco"; desde 07/10 ele só vale quando
escolhido ("só deve ser usado se for selecionado junto, e não como automatico
junto do preto e branco", Samuel), e o de fábrica é "o nosso" ou "desligado"
(core/pontinhos_scantailor.PADRAO; os testes valem para os dois). "Eu vou poder ligar e desligar esse apagador de
pingos? e selecionar o pouco, normal ou muito, ou selecionar o nosso" - "o
nosso muitas vezes acaba comendo muito as letras". E a regra de sempre: o
programa abre os arquivos de versões anteriores; o livro já conferido com a
caixinha "limpar poeirinha" ligada vira "o nosso" e sai igual ponto a ponto.

Testes de máquina (o "ficou melhor" é teste de olho, do Samuel):
    - os padrões: livro novo no de fábrica (nunca o do ScanTailor), página
      nova segue o livro;
    - a página troca só nela; valor estranho não derruba nada;
    - ida e volta pelo projeto.json;
    - projeto antigo (tests/dados/projeto_ace15b2.json, gravado pelo programa
      de antes): o livro abre "o nosso"; a página com a caixinha desligada
      abre "desligado"; e a página sai idêntica à de antes;
    - cada um dos cinco valores chega ao filtro, no Preto e branco (com e sem
      marcação) e no "Só as letras", com a força certa;
    - o DPI de verdade nos PDFs de "72 DPI" (passo 1 da ligação);
    - sem a DLL, cai no nosso (nunca sai sem limpar);
    - o desfazer de uma ação antiga da caixinha ainda funciona.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import filtros as F
from core import misto, pipeline
from core import pontinhos_scantailor as ps
from core import st_ferramentas as st
from core.selecao import LETRA, PAPEL, Selecao, retangulo
from historico_acoes import aplicar
from modelos import Acao, ConfigFolha, ConfigPagina, Projeto

ANTIGO = Path(__file__).parent / "dados" / "projeto_ace15b2.json"
precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# --- os padrões e o projeto ----------------------------------------------------

def test_as_cinco_escolhas_na_ordem_da_tela():
    assert ps.ESCOLHAS == ("desligado", "nosso", "st_pouco", "st_normal", "st_muito")
    # nomes da Rodada 10 do layout (07/10/2026); antes "Limpar pontinhos:"
    # desligado · o nosso · pouco · normal · muito
    assert [ps.NOMES_NA_TELA[e] for e in ps.ESCOLHAS] == [
        "Sem limpeza", "Limpeza bruta", "Limpeza cuidadosa (leve)",
        "Limpeza cuidadosa (média)", "Limpeza cuidadosa (forte)"]
    assert ps.ROTULO_NA_TELA == "Limpar a sujeira:"


def test_o_projeto_grava_o_codigo_e_nunca_o_texto_da_tela():
    """Pedido da gerente (06/10): os nomes da tela são provisórios (o Samuel
    vai escolher outros); o projeto.json guarda só o código interno."""
    assert set(ps.NOMES_NA_TELA) == set(ps.ESCOLHAS)
    projeto = Projeto(caminho_entrada="x.pdf", limpar_pontinhos=ps.NOSSO)
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, limpar_pontinhos=ps.MUITO)]
    texto = json.dumps(projeto.para_dicionario(), ensure_ascii=False)
    assert '"limpar_pontinhos": "nosso"' in texto and '"limpar_pontinhos": "st_muito"' in texto
    assert "o nosso" not in texto
    for nome in ps.NOMES_NA_TELA.values():          # os nomes de 07/10 também
        assert nome not in texto, nome
    # e o texto da tela (o de hoje e o de antes de 07/10) não vale como escolha
    for nome in ["o nosso", "pouco", *ps.NOMES_NA_TELA.values()]:
        assert ps.escolha_valida(nome) == ps.PADRAO, nome


def test_o_do_scantailor_nunca_vem_de_fabrica():
    """Decisão do Samuel, 07/10/2026 (página de escolhas, "Limpar pontinhos do
    ScanTailor: aceita o Preto e branco um pouco mais lento?" -> "Aceito, pode
    entrar"): "o limpar pontinhos, só deve ser usado se for selecionado junto,
    e não como automatico junto do preto e branco [...] eu quero poder usar o
    pouco o o medio e muito". O de fábrica é "o nosso" ou "desligado" (falta
    ele dizer qual; a troca é uma linha em core/pontinhos_scantailor.PADRAO),
    e as três forças do ScanTailor continuam como escolha."""
    assert ps.PADRAO in (ps.NOSSO, ps.DESLIGADO)
    assert ps.PADRAO not in ps.DO_SCANTAILOR
    assert Projeto(caminho_entrada="x.pdf").limpar_pontinhos not in ps.DO_SCANTAILOR
    assert set(ps.DO_SCANTAILOR) <= set(ps.ESCOLHAS)
    assert [ps.FORCA_DA_ESCOLHA[e] for e in ps.DO_SCANTAILOR] == ["pouco", "normal", "muito"]


def test_livro_novo_comeca_no_de_fabrica_e_a_pagina_segue_o_livro():
    projeto = Projeto(caminho_entrada="x.pdf")
    pagina = ConfigPagina(indice=0, folha=0)
    assert projeto.limpar_pontinhos == ps.PADRAO
    assert pagina.limpar_pontinhos is None
    assert ps.escolha_da_pagina(projeto, pagina) == ps.PADRAO
    assert not hasattr(pagina, "despeckle"), "a caixinha antiga saiu do modelo"


def test_a_pagina_troca_so_nela():
    projeto = Projeto(caminho_entrada="x.pdf", limpar_pontinhos=ps.NORMAL)
    a, b = ConfigPagina(indice=0, folha=0), ConfigPagina(indice=1, folha=0)
    b.limpar_pontinhos = "desligado"
    assert ps.escolha_da_pagina(projeto, a) == ps.NORMAL
    assert ps.escolha_da_pagina(projeto, b) == "desligado"


def test_valor_estranho_nao_derruba_nada():
    projeto = Projeto(caminho_entrada="x.pdf", limpar_pontinhos="forte")
    pagina = ConfigPagina(indice=0, folha=0, limpar_pontinhos="enorme")
    assert ps.escolha_da_pagina(projeto, pagina) == ps.PADRAO
    projeto.limpar_pontinhos = ps.MUITO
    assert ps.escolha_da_pagina(projeto, pagina) == ps.MUITO
    # objeto sem os campos (projeto em memória de antes): o de fábrica
    assert ps.escolha_da_pagina(object(), object()) == ps.PADRAO


def test_ida_e_volta_pelo_json():
    projeto = Projeto(caminho_entrada="x.pdf", limpar_pontinhos=ps.NORMAL)
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0),
                       ConfigPagina(indice=1, folha=0, limpar_pontinhos="desligado")]
    volta = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert volta.limpar_pontinhos == ps.NORMAL
    assert [p.limpar_pontinhos for p in volta.paginas] == [None, "desligado"]
    assert "despeckle" not in json.dumps(projeto.para_dicionario())


def _antigo() -> dict:
    return json.loads(ANTIGO.read_text(encoding="utf-8"))


def test_o_arquivo_de_antes_tem_a_caixinha_e_nao_a_escolha():
    dados = _antigo()
    assert "limpar_pontinhos" not in dados
    assert all("limpar_pontinhos" not in p and p["despeckle"] is True for p in dados["paginas"])


def test_projeto_antigo_abre_com_o_nosso():
    projeto = Projeto.de_dicionario(_antigo())
    assert projeto.limpar_pontinhos == "nosso"
    assert all(p.limpar_pontinhos is None for p in projeto.paginas)
    assert {ps.escolha_da_pagina(projeto, p) for p in projeto.paginas} == {"nosso"}


def test_pagina_antiga_com_a_caixinha_desligada_abre_desligado():
    dados = _antigo()
    dados["paginas"][1]["despeckle"] = False
    projeto = Projeto.de_dicionario(dados)
    assert projeto.paginas[1].limpar_pontinhos == "desligado"
    assert projeto.paginas[0].limpar_pontinhos is None
    assert ps.escolha_da_pagina(projeto, projeto.paginas[1]) == "desligado"
    assert ps.escolha_da_pagina(projeto, projeto.paginas[0]) == "nosso"


# --- a página de teste ---------------------------------------------------------

def _pagina_com_poeira() -> np.ndarray:
    """Papel creme, linhas de "letras", pingos de "i" perto delas, poeira
    solta (pequena e média) e poeira colada numa letra: os jeitos de limpar
    discordam aqui."""
    gerador = np.random.default_rng(7)
    img = np.full((900, 700, 3), (200, 220, 230), np.uint8)
    for linha in range(8):
        y = 80 + linha * 90
        for letra in range(18):
            x = 40 + letra * 34
            img[y:y + 32, x:x + 6] = 40
            img[y:y + 6, x:x + 18] = 40
            if letra % 3 == 0:
                img[y - 9:y - 5, x:x + 4] = 45        # o pingo do "i"
        img[y + 34:y + 36, 41:43] = 60                  # poeira colada na letra
    for _ in range(120):                                # poeira solta
        y, x = gerador.integers(20, 880), gerador.integers(20, 680)
        lado = int(gerador.integers(1, 7))
        img[y:y + lado, x:x + lado] = 50
    return cv2.GaussianBlur(img, (3, 3), 0)


def _livro(escolha_do_livro=ps.POUCO, escolha_da_pagina=None, **opcoes):
    projeto = Projeto(caminho_entrada="x.pdf", detectar_regioes=False,
                      limpar_pontinhos=escolha_do_livro, **opcoes)
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=F.PRETO_E_BRANCO,
                                    limpar_pontinhos=escolha_da_pagina)]
    return projeto


@pytest.fixture
def espiao(monkeypatch):
    """Anota cada chamada ao limpar do ScanTailor (força e DPI) e ao nosso,
    deixando as duas contas de verdade rodarem."""
    chamadas = []
    original_st, original_nosso = ps.limpar_pontinhos, F._despeckle

    def do_scantailor(binaria, dpi, forca="normal", **k):
        chamadas.append(("scantailor", forca, dpi))
        return original_st(binaria, dpi, forca, **k)

    def nosso(binaria, altura):
        chamadas.append(("nosso", None, None))
        return original_nosso(binaria, altura)

    monkeypatch.setattr(ps, "limpar_pontinhos", do_scantailor)
    monkeypatch.setattr(F, "_despeckle", nosso)
    return chamadas


def _esperado(img, escolha, dpi=300):
    """A conta à mão: o Preto e branco sem limpar e depois o limpar escolhido."""
    sem = F.filtro_preto_e_branco(img, despeckle=False)
    if escolha == "desligado":
        return sem
    if escolha == "nosso":
        return F._despeckle(sem, sem.shape[0])
    return ps.limpar_pontinhos(sem, dpi, ps.FORCA_DA_ESCOLHA[escolha]).imagem


# --- cada valor chega ao filtro ------------------------------------------------

@precisa_da_dll
@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_cada_escolha_do_livro_chega_ao_preto_e_branco(escolha, espiao):
    img = _pagina_com_poeira()
    projeto = _livro(escolha)
    saida, mono = pipeline._filtrar(projeto, projeto.paginas[0], img, 300.0, 300.0)
    assert mono
    usadas = [c for c in espiao if c[0] == "scantailor"]
    if escolha in ps.DO_SCANTAILOR:
        assert usadas and {c[1] for c in usadas} == {ps.FORCA_DA_ESCOLHA[escolha]}
        assert {round(c[2]) for c in usadas} == {300}
    else:
        assert not usadas
    assert (("nosso", None, None) in espiao) == (escolha == "nosso")
    espiao.clear()
    assert np.array_equal(saida, _esperado(img, escolha))


@precisa_da_dll
def test_as_cinco_saem_diferentes_nesta_pagina():
    """Sem isto o teste de cima passaria com o filtro ignorando a escolha."""
    img = _pagina_com_poeira()
    saidas = {e: pipeline._filtrar(_livro(e), _livro(e).paginas[0], img, 300.0, 300.0)[0]
              for e in ps.ESCOLHAS}
    for i, a in enumerate(ps.ESCOLHAS):
        for b in ps.ESCOLHAS[i + 1:]:
            assert not np.array_equal(saidas[a], saidas[b]), (a, b)
    # e o desligado é o que tem mais preto; o do ScanTailor só tira, nunca põe
    pretos = {e: int((s == 0).sum()) for e, s in saidas.items()}
    assert pretos["desligado"] == max(pretos.values())
    assert pretos[ps.POUCO] >= pretos[ps.NORMAL] >= pretos[ps.MUITO]


@precisa_da_dll
@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_a_escolha_da_pagina_vale_por_cima_do_livro(escolha, espiao):
    img = _pagina_com_poeira()
    outra = "desligado" if escolha != "desligado" else ps.MUITO
    projeto = _livro(outra, escolha)
    saida, _ = pipeline._filtrar(projeto, projeto.paginas[0], img, 300.0, 300.0)
    assert np.array_equal(saida, _esperado(img, escolha))


@precisa_da_dll
@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_cada_escolha_chega_com_marcacao(escolha, espiao, monkeypatch):
    """Página com marcação de letra e papel (o caminho de quase toda página)."""
    selecao = Selecao()
    selecao.acrescentar(retangulo(0.0, 0.0, 1.0, 0.6, tipo=LETRA))
    selecao.acrescentar(retangulo(0.0, 0.9, 1.0, 1.0, tipo=PAPEL))
    monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, **k: selecao)
    img = _pagina_com_poeira()
    projeto = _livro(escolha)
    projeto.detectar_regioes = True
    saida, _ = pipeline._filtrar(projeto, projeto.paginas[0], img, 300.0, 300.0)
    esperado, _ = F.aplicar_filtro_com_selecao(
        img, F.PRETO_E_BRANCO, selecao,
        despeckle=ps.Pontinhos(escolha, 300.0) if escolha in ps.DO_SCANTAILOR else
        {"desligado": False, "nosso": True}[escolha])
    assert np.array_equal(saida, esperado)
    usadas = {c[1] for c in espiao if c[0] == "scantailor"}
    assert usadas == ({ps.FORCA_DA_ESCOLHA[escolha]} if escolha in ps.DO_SCANTAILOR else set())


@precisa_da_dll
@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_cada_escolha_chega_ao_so_as_letras(escolha, espiao, monkeypatch):
    selecao = Selecao()
    selecao.acrescentar(retangulo(0.0, 0.0, 1.0, 0.6, tipo=LETRA))
    monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, **k: selecao)
    img = _pagina_com_poeira()
    projeto = _livro(escolha, misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_TUDO)
    projeto.detectar_regioes = True
    saida, _ = pipeline._filtrar(projeto, projeto.paginas[0], img, 300.0, 300.0)
    esperado, _ = misto.aplicar_misto(
        img, selecao, despeckle=ps.Pontinhos(escolha, 300.0) if escolha in ps.DO_SCANTAILOR
        else {"desligado": False, "nosso": True}[escolha], fora_do_texto=misto.FORA_TUDO)
    assert np.array_equal(saida, esperado)
    usadas = {c[1] for c in espiao if c[0] == "scantailor"}
    assert usadas == ({ps.FORCA_DA_ESCOLHA[escolha]} if escolha in ps.DO_SCANTAILOR else set())


def test_nos_outros_filtros_nao_muda_nada():
    img = _pagina_com_poeira()
    for filtro in (F.MELHORAR, F.ORIGINAL):
        saidas = []
        for escolha in ("desligado", ps.MUITO):
            projeto = _livro(escolha)
            projeto.paginas[0].filtro = filtro
            saidas.append(pipeline._filtrar(projeto, projeto.paginas[0], img, 300.0, 300.0)[0])
        assert np.array_equal(saidas[0], saidas[1]), filtro


# --- projeto antigo sai idêntico ------------------------------------------------

@pytest.mark.parametrize("caixinha", [True, False])
def test_projeto_antigo_sai_identico_ao_de_antes(caixinha, monkeypatch):
    """O projeto gravado pelo programa de antes (ace15b2), com a caixinha
    "limpar poeirinha" ligada ou desligada na página: a página sai igual,
    ponto a ponto, à conta que o programa de antes fazia
    (aplicar_filtro_com_selecao(..., despeckle=<a caixinha>)). Com e sem
    marcação, e no "Só as letras"."""
    dados = _antigo()
    for pagina in dados["paginas"]:
        pagina["despeckle"] = caixinha
        pagina["filtro"] = F.PRETO_E_BRANCO
    img = _pagina_com_poeira()
    selecao = Selecao()
    selecao.acrescentar(retangulo(0.0, 0.0, 1.0, 0.6, tipo=LETRA))
    for marcada in (True, False):
        projeto = Projeto.de_dicionario(json.loads(json.dumps(dados)))
        pagina = projeto.paginas[0]
        usada = selecao if marcada else Selecao()
        monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, _s=usada, **k: _s)
        novo, _ = pipeline._filtrar(projeto, pagina, img, 300.0, 72.0)
        antes, _ = F.aplicar_filtro_com_selecao(
            img, F.PRETO_E_BRANCO, usada, pagina.forca_preto, pagina.clareza_melhorar,
            pagina.intensidade_magico, algoritmo_pb=pagina.algoritmo_preto_branco,
            despeckle=caixinha)
        if not marcada and not caixinha:
            # a página sem marcação ficava SEMPRE com o nosso, sem ver a
            # caixinha (conserto desta ligação, ver core.filtros
            # .aplicar_filtro_com_selecao): aqui a caixinha desligada passa a valer
            antes = F.filtro_preto_e_branco(img, forca=pagina.forca_preto, despeckle=False)
        assert np.array_equal(novo, antes), (caixinha, marcada)
        # e no "Só as letras", a conta de antes com a caixinha
        projeto.misto_so_as_letras = True
        projeto.misto_fora_do_texto = misto.FORA_TUDO
        novo, _ = pipeline._filtrar(projeto, pagina, img, 300.0, 72.0)
        antes, _ = misto.aplicar_misto(
            img, usada, pagina.forca_preto, pagina.algoritmo_preto_branco, caixinha,
            pagina.clareza_melhorar, pagina.intensidade_magico, fora_do_texto=misto.FORA_TUDO)
        assert np.array_equal(novo, antes), ("só as letras", caixinha, marcada)


def test_true_e_false_continuam_fazendo_o_de_antes():
    """Os scripts e testes antigos passam despeckle=True/False: o nosso e nada."""
    img = _pagina_com_poeira()
    sem = F.filtro_preto_e_branco(img, despeckle=False)
    assert np.array_equal(F.filtro_preto_e_branco(img), F._despeckle(sem, sem.shape[0]))
    assert np.array_equal(F.filtro_preto_e_branco(img, despeckle=True),
                          F.filtro_preto_e_branco(img, despeckle="nosso"))
    assert np.array_equal(F.filtro_preto_e_branco(img, despeckle=ps.Pontinhos("desligado")), sem)


# --- o DPI de verdade (passo 1) --------------------------------------------------

def test_o_dpi_dos_pdfs_de_72():
    """Horas 11 desenhada a 300 DPI (3684 x 5633 pontos; o PDF diz 72): a
    mesma conta do detector de gravura dá uns 517 DPI - papel de 18 x 28 cm,
    e não de 31 x 48 cm."""
    from core.detectar_regioes import _dpi_declarado_a_dll

    dpi = ps.dpi_para_os_pontinhos(3684, 5633, 300.0, 72.0)
    assert dpi == pytest.approx(_dpi_declarado_a_dll(3684, 5633, 300.0))
    assert 510 < dpi < 525
    # o Graduale diz 112: tambem e acertado (abaixo de DPI_CONFIAVEL)
    assert ps.dpi_para_os_pontinhos(3219, 5264, 300.0, 112.4) == pytest.approx(466.8, abs=1)
    # sem saber o do scan: a mesma conta
    assert ps.dpi_para_os_pontinhos(3684, 5633, 300.0, None) == pytest.approx(dpi)
    # a previa (desenhada menor) ve o mesmo papel: o DPI acompanha o desenho
    assert ps.dpi_para_os_pontinhos(1351, 2066, 110.0, 72.0) == pytest.approx(dpi * 110 / 300, rel=0.01)


def test_o_dpi_dos_pdfs_de_verdade_nao_muda():
    # Palatino (o PDF diz 400): a pagina cabe, e o numero e de verdade
    assert ps.dpi_para_os_pontinhos(1176, 2073, 300.1, 400.0) == pytest.approx(300.1)
    # uma pagina GRANDE de um PDF que diz 300 DPI (fólio bem escaneado) fica como esta
    assert ps.dpi_para_os_pontinhos(5000, 7000, 300.0, 300.0) == pytest.approx(300.0)
    # Boécio (150) e Escola (199,9) estão acima da trava
    assert ps.DPI_CONFIAVEL < 149.9
    assert ps.dpi_para_os_pontinhos(1000, 1500, 300.0, 149.9) == pytest.approx(300.0)


def test_sem_dpi_o_filtro_estima_pela_altura():
    assert ps.dpi_para_os_pontinhos(100, 100, None) is None
    assert ps.dpi_para_os_pontinhos(100, 100, 0) is None
    assert ps.dpi_pela_altura(3000) == 300.0
    assert ps.dpi_pela_altura(10) == st.DPI_MINIMO


def test_o_pipeline_passa_o_dpi_certo():
    projeto = _livro(ps.POUCO)
    pagina = projeto.paginas[0]
    grande = np.zeros((5633, 3684), np.uint8)
    pontinhos = pipeline.pontinhos_da_pagina(projeto, pagina, grande, 300.0, 72.0)
    assert pontinhos.escolha == ps.POUCO and 510 < pontinhos.dpi < 525
    # o nosso e o desligado nao precisam de DPI
    pagina.limpar_pontinhos = "nosso"
    assert pipeline.pontinhos_da_pagina(projeto, pagina, grande, 300.0, 72.0) == ps.Pontinhos("nosso")
    # sem DPI (quem chama nao sabe): fica para o filtro estimar
    pagina.limpar_pontinhos = None
    assert pipeline.pontinhos_da_pagina(projeto, pagina, grande).dpi is None


def test_so_mede_o_dpi_quando_o_scantailor_vai_limpar():
    projeto = _livro(ps.POUCO)
    pagina = projeto.paginas[0]
    assert pipeline._vai_limpar_pelo_scantailor(projeto, pagina)
    for escolha in ("nosso", "desligado"):
        pagina.limpar_pontinhos = escolha
        assert not pipeline._vai_limpar_pelo_scantailor(projeto, pagina)
    pagina.limpar_pontinhos = ps.MUITO
    pagina.filtro = F.MELHORAR
    assert not pipeline._vai_limpar_pelo_scantailor(projeto, pagina)
    pagina.filtro = F.PRETO_E_BRANCO
    projeto.limpar = False
    assert not pipeline._vai_limpar_pelo_scantailor(projeto, pagina)


# --- sem a DLL ---------------------------------------------------------------------

def test_sem_a_dll_cai_no_nosso(tmp_path):
    sem_dll = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    img = _pagina_com_poeira()
    binaria = F.filtro_preto_e_branco(img, despeckle=False)
    saida = ps.limpar_conforme_a_escolha(binaria, ps.Pontinhos(ps.POUCO, 300.0), biblioteca=sem_dll)
    assert np.array_equal(saida, F._despeckle(binaria, binaria.shape[0]))


# --- o desfazer de uma ação antiga ------------------------------------------------

def test_desfazer_acao_antiga_da_caixinha():
    """acoes.jsonl gravado antes: "mudar_despeckle" (True -> False). O Ctrl+Z
    e o refazer dela continuam mudando a página."""
    projeto = _livro("nosso")
    acao = Acao.nova("mudar_despeckle", "pagina", [0], {"despeckle": {"0": True}},
                     {"despeckle": False}, "Limpar poeirinha na página 1: desligado")
    aplicar(projeto, acao, acao.depois)
    assert projeto.paginas[0].limpar_pontinhos == "desligado"
    aplicar(projeto, acao, acao.antes)
    assert projeto.paginas[0].limpar_pontinhos == "nosso"
    assert not hasattr(projeto.paginas[0], "despeckle")
