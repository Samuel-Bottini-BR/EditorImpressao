"""A selecao: onde cada tratamento vale dentro da pagina."""

from __future__ import annotations

import numpy as np
import pytest

from core.selecao import (
    AUTOMATICO,
    GRAVURA,
    LETRA,
    MAO,
    POLIGONO,
    REDE,
    RETANGULO,
    SUBTRAIR,
    Regiao,
    Selecao,
    de_mascara,
    poligono,
    retangulo,
    traco,
)
from modelos import ConfigPagina, Projeto


# --- o basico ---------------------------------------------------------------

def test_selecao_vazia_nao_marca_nada():
    s = Selecao()
    assert s.vazia
    assert not s.mascara(100, 100, GRAVURA).any()


def test_retangulo_marca_a_area_certa():
    s = Selecao()
    s.acrescentar(retangulo(0.25, 0.25, 0.75, 0.75))
    m = s.mascara(200, 200, GRAVURA)
    # o miolo esta dentro, os cantos estao fora
    assert m[100, 100]
    assert not m[10, 10]
    assert not m[190, 190]
    # metade do lado ao quadrado = um quarto da area
    assert 0.20 < m.mean() < 0.30


def test_poligono_marca_o_interior():
    s = Selecao()
    s.acrescentar(poligono([(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]))
    m = s.mascara(100, 100, GRAVURA)
    assert m[50, 50]
    assert not m[2, 2]


def test_traco_marca_uma_linha_com_espessura():
    s = Selecao()
    s.acrescentar(traco([(0.1, 0.5), (0.9, 0.5)], espessura=0.1))
    m = s.mascara(200, 200, GRAVURA)
    assert m[100, 100]      # em cima da linha
    assert not m[20, 100]   # bem acima dela
    assert not m[180, 100]  # bem abaixo


# --- somar e subtrair -------------------------------------------------------

def test_subtrair_apaga_o_que_veio_antes():
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0))
    s.acrescentar(retangulo(0.25, 0.25, 0.75, 0.75, operacao=SUBTRAIR))
    m = s.mascara(200, 200, GRAVURA)
    assert m[10, 10]          # a borda ficou
    assert not m[100, 100]    # o meio foi tirado


def test_a_ordem_importa():
    """Subtrair antes de somar nao apaga nada: a ordem e a regra."""
    s = Selecao()
    s.acrescentar(retangulo(0.25, 0.25, 0.75, 0.75, operacao=SUBTRAIR))
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0))
    assert s.mascara(200, 200, GRAVURA)[100, 100]


def test_tipos_nao_se_misturam():
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.48, 1.0, tipo=GRAVURA))
    s.acrescentar(retangulo(0.52, 0.0, 1.0, 1.0, tipo=LETRA))
    g = s.mascara(100, 100, GRAVURA)
    ll = s.mascara(100, 100, LETRA)
    assert g[50, 20] and not g[50, 80]
    assert ll[50, 80] and not ll[50, 20]
    assert not (g & ll).any()


def test_regioes_encostadas_dividem_so_a_linha_da_divisa():
    """Duas areas coladas compartilham a coluna da divisa, e so ela.

    E consequencia de o retangulo preenchido incluir as duas pontas. Uma
    emenda de um pixel nao atrapalha: os filtros se aplicam em ordem, e nessa
    linha um deles simplesmente vence. Fica registrado para nao virar susto.
    """
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 1.0, tipo=GRAVURA))
    s.acrescentar(retangulo(0.5, 0.0, 1.0, 1.0, tipo=LETRA))
    juntos = s.mascara(100, 100, GRAVURA) & s.mascara(100, 100, LETRA)
    assert juntos.mean() < 0.02


# --- independencia de resolucao --------------------------------------------

@pytest.mark.parametrize("lado", [64, 200, 1000])
def test_a_mesma_selecao_vale_em_qualquer_tamanho(lado):
    """E o motivo de guardar fracao e nao pixel: previa e exportacao batem."""
    s = Selecao()
    s.acrescentar(retangulo(0.2, 0.2, 0.8, 0.8))
    fracao = s.mascara(lado, lado, GRAVURA).mean()
    assert 0.33 < fracao < 0.39   # 0,6 x 0,6 = 0,36


# --- limpar por origem ------------------------------------------------------

def test_limpar_a_maquina_preserva_a_mao():
    """Rodar a deteccao de novo nao pode apagar o trabalho manual."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 0.5, origem=REDE))
    s.acrescentar(retangulo(0.5, 0.5, 1.0, 1.0, origem=MAO))
    s.acrescentar(retangulo(0.0, 0.5, 0.5, 1.0, origem=AUTOMATICO))

    assert s.limpar_origem(REDE) == 1
    assert s.limpar_origem(AUTOMATICO) == 1
    assert len(s) == 1
    assert s.regioes[0].origem == MAO


# --- borda suave ------------------------------------------------------------

def test_peso_sem_suavidade_e_igual_a_mascara():
    s = Selecao()
    s.acrescentar(retangulo(0.25, 0.25, 0.75, 0.75))
    p = s.peso(100, 100, GRAVURA)
    assert set(np.unique(p)).issubset({0.0, 1.0})


def test_peso_com_suavidade_tem_meio_termo():
    """Sem borda suave a emenda entre tratado e nao tratado vira degrau."""
    s = Selecao()
    s.acrescentar(retangulo(0.25, 0.25, 0.75, 0.75, suavidade=0.05))
    p = s.peso(200, 200, GRAVURA)
    assert p.max() > 0.9
    assert ((p > 0.1) & (p < 0.9)).any()


# --- a ponte com a rede neural ---------------------------------------------

def test_de_mascara_vira_forma_editavel():
    """A saida da rede tem de virar forma, senao nao da para corrigir a mao."""
    m = np.zeros((200, 200), np.uint8)
    m[50:150, 60:140] = 1

    regioes = de_mascara(m, tipo=GRAVURA, origem=REDE)
    assert regioes and all(r.forma == POLIGONO for r in regioes)
    assert all(r.origem == REDE for r in regioes)

    s = Selecao(regioes=regioes)
    refeita = s.mascara(200, 200, GRAVURA)
    # o poligono simplificado cobre a area original quase inteira
    original = m.astype(bool)
    interseccao = (refeita & original).sum() / original.sum()
    assert interseccao > 0.9


def test_de_mascara_descarta_cisco():
    m = np.zeros((200, 200), np.uint8)
    m[100:103, 100:103] = 1     # tres por tres pixels
    assert de_mascara(m, area_minima=0.01) == []


def test_de_mascara_preserva_o_buraco_de_um_anel():
    """Uma moldura e um anel. Se o buraco sumir, ela engole o texto do meio.

    Foi o que aconteceu na iluminura do Livro de Horas: a orla era detectada
    certo e a mancha de texto no centro dela desaparecia junto.
    """
    m = np.zeros((300, 300), np.uint8)
    m[40:260, 40:260] = 1      # a moldura
    m[90:210, 90:210] = 0      # o vao onde mora o texto

    regioes = de_mascara(m, tipo=GRAVURA, origem=REDE, area_minima=0.001)
    assert any(r.operacao == SUBTRAIR for r in regioes), "o buraco nao virou subtracao"

    refeita = Selecao(regioes=regioes).mascara(300, 300, GRAVURA)
    assert refeita[50, 150], "a moldura sumiu"
    assert not refeita[150, 150], "o buraco foi tapado"


# --- serializacao -----------------------------------------------------------

def test_ida_e_volta_preserva_tudo():
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.2, 0.3, 0.4, tipo=LETRA, origem=REDE,
                            confianca=0.87, rotulo="figure"))
    s.acrescentar(traco([(0.1, 0.1), (0.5, 0.5)], espessura=0.03))

    volta = Selecao.de_lista(s.para_lista())
    assert len(volta) == 2
    assert volta.regioes[0].confianca == pytest.approx(0.87)
    assert volta.regioes[0].rotulo == "figure"
    assert volta.regioes[1].espessura == pytest.approx(0.03)
    assert np.array_equal(s.mascara(80, 80, LETRA), volta.mascara(80, 80, LETRA))


def test_lista_estragada_nao_derruba():
    """Arquivo de versao anterior ou mexido a mao nao pode quebrar o programa."""
    assert Selecao.de_lista(None).vazia
    assert Selecao.de_lista("nao e lista").vazia
    assert Selecao.de_lista([{"tipo": "inventado"}, {"lixo": 1}, 42]).vazia

    boa = Selecao.de_lista([
        {"tipo": GRAVURA, "forma": RETANGULO, "pontos": [[0, 0], [1, 1]]},
        {"tipo": GRAVURA, "forma": POLIGONO, "pontos": [[0, 0]]},   # pontos de menos
    ])
    assert len(boa) == 1


def test_projeto_antigo_sem_selecao_continua_abrindo():
    dados = {
        "caminho_entrada": "x.pdf",
        "paginas": [{"indice": 0, "folha": 0}],   # sem o campo selecao
    }
    projeto = Projeto.de_dicionario(dados)
    assert projeto.paginas[0].selecao == []
    assert projeto.paginas[0].obter_selecao().vazia


def test_selecao_sobrevive_ao_projeto():
    pagina = ConfigPagina(indice=0, folha=0)
    s = Selecao()
    s.acrescentar(retangulo(0.2, 0.2, 0.6, 0.6, tipo=GRAVURA))
    pagina.guardar_selecao(s)

    projeto = Projeto(caminho_entrada="x.pdf", paginas=[pagina])
    volta = Projeto.de_dicionario(projeto.para_dicionario())
    assert len(volta.paginas[0].obter_selecao()) == 1


# --- frases para a tela -----------------------------------------------------

def test_resumo_e_frase_em_portugues():
    s = Selecao()
    assert "Nada marcado" in s.resumo_em_portugues()
    s.acrescentar(retangulo(0, 0, 1, 1, tipo=GRAVURA))
    texto = s.resumo_em_portugues()
    assert "gravura" in texto.lower()
    assert "mask" not in texto.lower() and "None" not in texto


def test_regiao_invalida_nao_entra():
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=POLIGONO, pontos=[(0.1, 0.1)]))
    s.acrescentar(Regiao(tipo="inventado", forma=RETANGULO,
                         pontos=[(0, 0), (1, 1)]))
    assert s.vazia
