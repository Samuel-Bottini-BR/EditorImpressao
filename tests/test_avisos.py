"""O "Para revisar" depois das decisoes do Samuel (rodadas 4 e 5, 07 a 09/10/2026):
um aviso para cada coisa, cada um com os seus botoes; "esta bom" por motivo;
"Deixar em branco"; a forca do preto sozinha. Testes de maquina, sem janela.

    `rv4-em-branco`: "Tem que ter um tipo de aviso para cada coisa, e um botão de
        apagar folha e outro realmente de só mudar para um folha branca."
    `rv4-conserto-desenho`: "(a) Botão no aviso"
    `rv4-erro-4-texto-falhado`: "Força sozinha"
    `rv4-aviso-so-texto`: "Eu tenho que conseguir fazer isso com uma pagina
        individual, com um motivo individual de uma pagina e com todas as paginas
        ou com todos os motivos de todas as paginas [...]"
A parte da tela esta em tests/test_para_revisar_na_tela.py.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core import analise, avisos, misto, revisar
from core import pipeline as P
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import ConfigFolha, ConfigPagina, Projeto
from tests.test_misto_no_programa import (  # noqa: F401 - fixtures e paginas sinteticas
    _pagina_sintetica,
    _projeto,
    leitor_falso,
    linhas_limpas,
)

RAIZ = Path(__file__).resolve().parent.parent


def _livro(n: int = 5) -> Projeto:
    p = Projeto(caminho_entrada=str(RAIZ / "nao-existe.pdf"))
    p.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    p.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(n)]
    return p


# --- um aviso para cada coisa, cada um com os seus botoes ----------------------

@pytest.mark.parametrize("codigo", [analise.EM_BRANCO, analise.PAGINA_SEM_CONTEUDO])
def test_em_branco_e_sem_conteudo_tem_os_dois_botoes_separados(codigo):
    botoes = analise.descrever(codigo).botoes
    assert botoes == [("Deixar em branco", "em_branco"), ("Tirar do livro", "apagar")]


def test_parece_em_branco_e_pagina_sem_conteudo_sao_dois_avisos():
    a, b = analise.descrever(analise.EM_BRANCO), analise.descrever(analise.PAGINA_SEM_CONTEUDO)
    assert a.titulo == "Parece em branco" and b.titulo == "Página sem conteúdo"
    assert a.mensagem != b.mensagem
    assert "apagar" not in a.mensagem.lower(), "o aviso nao oferece mais so apagar"


def test_os_consertos_rapidos_sao_botoes_do_aviso():
    desenho = analise.descrever(analise.DESENHO_APAGADO).botoes
    assert desenho[0] == ("Trazer de volta nesta página", "misto_fora:" + misto.FORA_TUDO)
    so_texto = analise.descrever(analise.SO_O_TEXTO_APAGOU).botoes
    assert so_texto[0] == ("Trazer de volta nesta página", "misto_fora:" + misto.FORA_REDE)
    reforco = analise.descrever(analise.FORCA_REFORCADA).botoes
    assert reforco[0] == ("Desfazer", "desfazer_reforco")
    # todos os tres deixam dar "esta bom" so naquele motivo
    for botoes in (desenho, so_texto, reforco):
        assert botoes[1] == ("está bom assim", "revisar")


def test_aviso_de_um_botao_so_continua_com_um():
    cor = analise.descrever(analise.COR).botoes
    assert len(cor) == 1 and cor[0][0] == "usar Mágico pro nesta"
    assert analise.descrever(analise.DESENHO_OU_ESCRITA).botoes == []
    assert analise.descrever("codigo-que-nao-existe").botoes == []


# --- "esta bom" por motivo, por pagina, por motivo em todas e em tudo ----------

def test_esta_bom_num_motivo_so_deixa_os_outros_na_lista():
    pagina = ConfigPagina(indice=0, folha=0,
                          alertas=[analise.DESENHO_APAGADO, analise.TEXTO_FALHADO])
    assert pagina.alertas_pendentes == [analise.DESENHO_APAGADO, analise.TEXTO_FALHADO]
    pagina.alertas_aceitos = [analise.DESENHO_APAGADO]
    assert pagina.alertas_pendentes == [analise.TEXTO_FALHADO] and pagina.precisa_revisao
    pagina.alertas_aceitos = [analise.DESENHO_APAGADO, analise.TEXTO_FALHADO]
    assert pagina.alertas_pendentes == [] and not pagina.precisa_revisao
    # a pagina inteira dada como boa: nada pendente, qualquer que seja o motivo
    outra = ConfigPagina(indice=1, folha=1, alertas=[analise.COR], revisada=True)
    assert outra.alertas_pendentes == []
    # a folha tem a mesma conta
    folha = ConfigFolha(indice=0, alertas=[analise.MUITO_TORTA, analise.RESOLUCAO_BAIXA],
                        alertas_aceitos=[analise.MUITO_TORTA])
    assert folha.alertas_pendentes == [analise.RESOLUCAO_BAIXA]


def test_a_lista_do_livro_vem_na_ordem_e_sem_as_apagadas():
    p = _livro(4)
    p.folhas[1].alertas = [analise.MUITO_TORTA]
    p.paginas[0].alertas = [analise.COR]
    p.paginas[1].alertas = [analise.DESENHO_APAGADO, analise.TEXTO_FALHADO]
    p.paginas[2].alertas = [analise.COR]
    p.paginas[2].apagada = True
    p.paginas[3].alertas = [analise.COR]
    p.paginas[3].revisada = True
    lista = avisos.pendentes_do_livro(p)
    assert [(a.alvo, a.indice, a.codigo) for a in lista] == [
        ("pagina", 0, analise.COR),
        ("folha", 1, analise.MUITO_TORTA),
        ("pagina", 1, analise.DESENHO_APAGADO),
        ("pagina", 1, analise.TEXTO_FALHADO),
    ]
    assert lista[0].onde == "Página 1" and lista[1].onde == "Folha 2"
    assert lista[2].titulo == "Desenho apagado"
    assert avisos.frase_de_quantos(lista) == "Ainda tem 3 páginas que eu não tive certeza."
    assert avisos.frase_de_quantos(lista[:1]) == "Ainda tem 1 página que eu não tive certeza."


def test_por_motivo_poe_primeiro_o_motivo_com_mais_paginas():
    p = _livro(4)
    p.paginas[0].alertas = [analise.TEXTO_FALHADO]
    for i in (1, 2, 3):
        p.paginas[i].alertas = [analise.COR]
    grupos = avisos.por_motivo(avisos.pendentes_do_livro(p))
    assert list(grupos) == [analise.COR, analise.TEXTO_FALHADO]
    assert [a.indice for a in grupos[analise.COR]] == [1, 2, 3]


def _aceitar(projeto, lista, historico=None):
    """O que a tela faz: uma acao do desfazer por alvo."""
    acoes = []
    for alvo, (indices, campos) in avisos.campos_para_aceitar(projeto, lista).items():
        acao = montar_acao(projeto, "aceitar_avisos", alvo, indices, campos, "está bom")
        aplicar(projeto, acao, acao.depois)
        if historico is not None:
            historico.registrar(acao)
        acoes.append(acao)
    return acoes


def test_esta_bom_em_todas_as_paginas_de_um_motivo_e_o_desfazer():
    p = _livro(4)
    for i in (0, 2, 3):
        p.paginas[i].alertas = [analise.FAIXA_NA_BEIRADA, analise.COR]
    lista = [a for a in avisos.pendentes_do_livro(p) if a.codigo == analise.FAIXA_NA_BEIRADA]
    historico = HistoricoAcoes()
    acoes = _aceitar(p, lista, historico)
    assert len(acoes) == 1 and acoes[0].indices == [0, 2, 3]
    for i in (0, 2, 3):
        assert p.paginas[i].alertas_pendentes == [analise.COR]
        assert p.paginas[i].alertas == [analise.FAIXA_NA_BEIRADA, analise.COR], "a pagina nao muda"
    assert p.pendentes_de_revisao() == 3
    # o Ctrl+Z traz os avisos de volta
    historico.desfazer(p)
    assert all(p.paginas[i].alertas_aceitos == [] for i in (0, 2, 3))
    historico.refazer(p)
    assert p.paginas[2].alertas_aceitos == [analise.FAIXA_NA_BEIRADA]


def test_esta_bom_em_tudo_pega_folhas_e_paginas():
    p = _livro(3)
    p.folhas[0].alertas = [analise.MUITO_TORTA]
    p.paginas[1].alertas = [analise.COR, analise.TEXTO_FALHADO]
    p.paginas[2].alertas = [analise.COR]
    p.paginas[2].alertas_aceitos = [analise.COR]             # este ja estava aceito
    acoes = _aceitar(p, avisos.pendentes_do_livro(p))
    assert sorted(a.alvo for a in acoes) == ["folha", "pagina"]
    assert p.pendentes_de_revisao() == 0 and avisos.pendentes_do_livro(p) == []
    assert p.paginas[1].alertas_aceitos == [analise.COR, analise.TEXTO_FALHADO]
    assert p.paginas[2].alertas_aceitos == [analise.COR], "o que ja estava aceito nao duplica"
    # aviso que ja nao esta pendente e pulado sem erro
    assert avisos.campos_para_aceitar(p, [avisos.Aviso("pagina", 1, analise.COR),
                                           avisos.Aviso("pagina", 99, analise.COR)]) == {}


def test_o_aviso_que_some_sozinho_esquece_o_esta_bom(leitor_falso):
    """Se o problema for resolvido e voltar depois, o aviso pede um olhar de
    novo (o "esta bom" era para aquela vez)."""
    from tests.test_misto_no_programa import _com_letra_clara

    img, s = _pagina_sintetica()
    com_letra = _com_letra_clara(img)
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, com_letra.copy())
    assert pagina.alertas_pendentes == [analise.DESENHO_APAGADO]
    pagina.alertas_aceitos = [analise.DESENHO_APAGADO]
    P._filtrar(p, pagina, com_letra.copy())
    assert pagina.alertas_pendentes == [], "o esta bom vale enquanto o aviso estiver la"
    P._filtrar(p, pagina, img.copy())                        # o problema sumiu
    assert pagina.alertas == [] and pagina.alertas_aceitos == []
    P._filtrar(p, pagina, com_letra.copy())                  # e voltou
    assert pagina.alertas_pendentes == [analise.DESENHO_APAGADO]


# --- "Deixar em branco" ---------------------------------------------------------

@pytest.mark.parametrize("filtro", [ORIGINAL, PRETO_E_BRANCO, MELHORAR, TIRAR_FUNDO])
def test_deixar_em_branco_sai_uma_folha_branca_do_mesmo_tamanho(leitor_falso, filtro):
    img, s = _pagina_sintetica()
    p = _projeto(s, filtro=filtro, misto_so_as_letras=True)
    pagina = p.paginas[0]
    pagina.em_branco = True
    saida, mono = P._filtrar(p, pagina, img.copy())
    assert mono is True and saida.shape == img.shape[:2]
    assert int(saida.min()) == 255
    assert leitor_falso == [], "a folha branca nao passa pelo leitor de texto"
    assert pagina.alertas == []


def test_em_branco_nao_tira_o_fundo_e_volta_ao_desmarcar(leitor_falso):
    img, s = _pagina_sintetica()
    p = _projeto(s, filtro=TIRAR_FUNDO)
    p.tem_camadas = True
    pagina = p.paginas[0]
    assert P.usa_tirar_fundo(p, pagina)
    pagina.em_branco = True
    assert not P.usa_tirar_fundo(p, pagina)
    pagina.em_branco = False
    pagina.filtro = ORIGINAL
    saida, _ = P._filtrar(p, pagina, img.copy())
    assert np.array_equal(saida, img), "desmarcado, a pagina sai como sempre"


def test_os_campos_novos_vao_e_voltam_do_projeto_salvo():
    p = _livro(2)
    p.reforcar_texto_falhado = True
    p.paginas[0].em_branco = True
    p.paginas[0].alertas_aceitos = [analise.COR]
    p.paginas[0].forca_antes_do_reforco = 40
    p.paginas[0].reforco_desfeito = True
    p.folhas[1].alertas_aceitos = [analise.MUITO_TORTA]
    de_volta = Projeto.de_dicionario(p.para_dicionario())
    assert de_volta.reforcar_texto_falhado is True
    assert de_volta.paginas[0].em_branco is True
    assert de_volta.paginas[0].alertas_aceitos == [analise.COR]
    assert de_volta.paginas[0].forca_antes_do_reforco == 40 and de_volta.paginas[0].reforco_desfeito
    assert de_volta.folhas[1].alertas_aceitos == [analise.MUITO_TORTA]
    # projeto de versao anterior, sem os campos: abre, com tudo desligado
    antigo = p.para_dicionario()
    antigo.pop("reforcar_texto_falhado")
    for item in antigo["paginas"]:
        for campo in ("em_branco", "alertas_aceitos", "forca_antes_do_reforco", "reforco_desfeito",
                      "faixa_na_beirada"):
            item.pop(campo)
    for item in antigo["folhas"]:
        item.pop("alertas_aceitos")
    velho = Projeto.de_dicionario(antigo)
    assert velho.reforcar_texto_falhado is False, "livro ja conferido nao ganha o reforco sozinho"
    assert velho.paginas[0].em_branco is False and velho.paginas[0].alertas_aceitos == []
    assert velho.paginas[0].forca_antes_do_reforco is None
    assert Projeto(caminho_entrada="x.pdf").reforcar_texto_falhado is True, "livro novo: ligado"


# --- a forca do preto sozinha ---------------------------------------------------

@pytest.fixture
def texto_falhado(monkeypatch):
    """Troca a conta da regra por uma que diz "texto falhado" enquanto a forca
    do preto esta abaixo de `ate` (como o Camoes 27: 85 fecha as letras)."""
    estado = {"ate": P.FORCA_DO_REFORCO, "forcas": []}
    original = P.misto.aplicar_misto

    def espiao(img, selecao, forca_preto, *args, **kwargs):
        estado["forcas"].append(forca_preto)
        return original(img, selecao, forca_preto, *args, **kwargs)

    def medir(*args, **kwargs):
        falhou = estado["forcas"][-1] < estado["ate"]
        return revisar.Sinais(falhadas=3 if falhou else 0, linhas_contadas=5, sem_conteudo=0.2,
                              linhas_fortes=5)

    monkeypatch.setattr(P.misto, "aplicar_misto", espiao)
    monkeypatch.setattr(P.revisar, "medir", medir)
    return estado


def test_texto_falhado_escurece_a_forca_so_nessa_pagina_e_avisa(leitor_falso, texto_falhado):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    assert p.reforcar_texto_falhado is True
    pagina = p.paginas[0]
    pagina.revisada = True
    saida, _ = P._filtrar(p, pagina, img.copy())
    assert texto_falhado["forcas"] == [50, P.FORCA_DO_REFORCO], "filtrou de novo com a forca nova"
    assert pagina.forca_preto == P.FORCA_DO_REFORCO and pagina.forca_antes_do_reforco == 50
    assert pagina.alertas == [analise.FORCA_REFORCADA], "o reforco fechou as letras: so o aviso dele"
    assert not pagina.revisada
    assert saida.shape[:2] == img.shape[:2]
    # desenhar de novo nao reforca de novo nem repete o aviso
    P._filtrar(p, pagina, img.copy())
    assert texto_falhado["forcas"][2:] == [P.FORCA_DO_REFORCO]
    assert pagina.alertas.count(analise.FORCA_REFORCADA) == 1


def test_se_o_reforco_nao_resolve_o_aviso_de_texto_falhado_fica_junto(leitor_falso, texto_falhado):
    """O texto vermelho do Egenloff 3: nem a 85 fecha."""
    texto_falhado["ate"] = 101
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert pagina.forca_preto == P.FORCA_DO_REFORCO
    assert pagina.alertas == [analise.FORCA_REFORCADA, analise.TEXTO_FALHADO]


def test_com_o_reforco_desligado_no_livro_so_avisa(leitor_falso, texto_falhado):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True, reforcar_texto_falhado=False)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert pagina.forca_preto == 50 and pagina.forca_antes_do_reforco is None
    assert pagina.alertas == [analise.TEXTO_FALHADO]
    assert texto_falhado["forcas"] == [50]


def test_projeto_antigo_sai_igual_ponto_por_ponto_mesmo_com_texto_falhado(leitor_falso,
                                                                         texto_falhado):
    """O projeto gravado antes de 12/10/2026 (sem nenhum dos campos novos)
    abre e a pagina sai IGUAL, ponto por ponto, ao "So as letras" de sempre -
    mesmo quando a regra acha o texto falhado: a forca nao muda sozinha, a
    pagina so ganha o aviso. ("o programa vai ter que ser capaz de abrir
    arquivos de versoes anteriores", Samuel, 05/10.)"""
    from tests.test_misto_no_programa import _resultado_falso

    img, s = _pagina_sintetica()
    dados = _projeto(s, misto_so_as_letras=True).para_dicionario()
    dados.pop("reforcar_texto_falhado")
    for pagina in dados["paginas"]:
        for campo in ("em_branco", "alertas_aceitos", "forca_antes_do_reforco", "reforco_desfeito",
                      "faixa_na_beirada"):
            pagina.pop(campo)
    for folha in dados["folhas"]:
        folha.pop("alertas_aceitos")
    antigo = Projeto.de_dicionario(dados)
    pagina = antigo.paginas[0]

    saida, mono = P._filtrar(antigo, pagina, img.copy())

    linhas, altura = misto.mascara_das_linhas([_resultado_falso()], img.shape)
    esperado, mono_esperado = misto.aplicar_misto(
        img.copy(), pagina.obter_selecao(), 50, fora_do_texto=misto.FORA_REDE,
        linhas=linhas, altura_linha=altura)
    assert mono == mono_esperado and np.array_equal(saida, esperado)
    assert pagina.forca_preto == 50 and pagina.forca_antes_do_reforco is None
    assert pagina.alertas == [analise.TEXTO_FALHADO], "so o aviso; nada mexe na imagem"
    assert texto_falhado["forcas"] == [50, 50], "filtrou uma vez so (a segunda e a do teste)"


def test_o_desfazer_do_reforco_volta_a_forca_e_nao_reforca_de_novo(leitor_falso, texto_falhado):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    pagina.forca_preto = 40
    P._filtrar(p, pagina, img.copy())
    assert pagina.forca_antes_do_reforco == 40
    # o que o botao "Desfazer" do aviso grava (ui/tela_conferir._desfazer_o_reforco)
    pagina.forca_preto, pagina.forca_antes_do_reforco, pagina.reforco_desfeito = 40, None, True
    P._filtrar(p, pagina, img.copy())
    assert pagina.forca_preto == 40
    assert pagina.alertas == [analise.TEXTO_FALHADO], "sem o reforco, o aviso do texto falhado"


def test_mexer_na_forca_depois_do_reforco_tira_o_aviso_sem_desenhar(leitor_falso, texto_falhado):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    assert analise.FORCA_REFORCADA in pagina.alertas
    pagina.alertas_aceitos = [analise.FORCA_REFORCADA]
    pagina.forca_preto = 70                                  # a pessoa puxou o medidor
    P.acertar_alertas_do_fundo(p, [pagina])
    assert analise.FORCA_REFORCADA not in pagina.alertas
    assert pagina.forca_antes_do_reforco is None and pagina.reforco_desfeito is True
    assert pagina.alertas_aceitos == []


def test_o_aviso_do_reforco_segue_o_filtro(leitor_falso, texto_falhado):
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    P._filtrar(p, pagina, img.copy())
    pagina.filtro = MELHORAR
    P.acertar_alertas_do_fundo(p, [pagina])
    assert analise.FORCA_REFORCADA not in pagina.alertas
    pagina.filtro = PRETO_E_BRANCO
    P.acertar_alertas_do_fundo(p, [pagina])
    assert analise.FORCA_REFORCADA in pagina.alertas, "o reforco continua valendo: o aviso volta"


def test_quem_ja_esta_na_forca_do_reforco_nao_e_reforcado(leitor_falso, texto_falhado):
    texto_falhado["ate"] = 101
    img, s = _pagina_sintetica()
    p = _projeto(s, misto_so_as_letras=True)
    pagina = p.paginas[0]
    pagina.forca_preto = 90
    P._filtrar(p, pagina, img.copy())
    assert pagina.forca_preto == 90 and pagina.forca_antes_do_reforco is None
    assert pagina.alertas == [analise.TEXTO_FALHADO]
