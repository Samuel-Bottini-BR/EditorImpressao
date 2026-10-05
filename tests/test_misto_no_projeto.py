"""Os campos do modo Misto no projeto salvo (ligar o Misto ao programa, passo 1).

Pedido do Samuel (conferencia 10, P1 (a)): a caixinha "So as letras" dentro do
Preto e branco, "para o livro (tela 'O que fazer') e para a pagina (aba
Filtro)" - autoriza os campos novos no projeto. As escolhas e os padroes de
fabrica: conferencia 14 (PADRAO: A, "Guardar a tinta forte"), conferencia 12
(P2 (a) papel da gravura branco; P4 (a) letras da moldura com a cor delas e o
papel branco atras, com (b) e (c) disponiveis), e a regra geral "esse
programa deve presar por dar opcoes".

E a regra da conferencia 14 (Z2): "o programa quando estiver pronto, ele vai
ter que ser capaz de abrir arquivos de versoes anteriores." O arquivo
tests/dados/projeto_ace15b2.json foi gravado pelo programa de ANTES destes
campos (commit ace15b2, para_dicionario de verdade): ele tem de abrir igual,
com o Misto desligado.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import projetos
from core import misto
from modelos import ConfigFolha, ConfigPagina, Projeto

ANTIGO = Path(__file__).parent / "dados" / "projeto_ace15b2.json"


# --- os padroes -------------------------------------------------------------

def test_livro_novo_comeca_com_o_misto_desligado_e_as_escolhas_de_fabrica():
    p = Projeto(caminho_entrada="x.pdf")
    assert p.misto_so_as_letras is False
    assert p.misto_fora_do_texto == misto.FORA_REDE            # A, conferencia 14
    assert p.misto_papel_da_gravura == misto.PAPEL_BRANCO      # P2 (a)
    assert p.misto_letras_na_moldura == misto.LETRAS_COR_PAPEL_BRANCO   # P4 (a)


def test_pagina_nova_segue_o_livro_em_tudo():
    pagina = ConfigPagina(indice=0, folha=0)
    for campo in misto.CAMPOS_DO_MISTO:
        assert getattr(pagina, campo) is None, campo


# --- a pagina herda do livro e pode trocar so nela --------------------------

def _livro(**opcoes):
    p = Projeto(caminho_entrada="x.pdf", **opcoes)
    p.folhas = [ConfigFolha(indice=0)]
    p.paginas = [ConfigPagina(indice=0, folha=0, filtro="preto_e_branco"),
                 ConfigPagina(indice=1, folha=0, filtro="preto_e_branco")]
    return p


def test_sem_so_as_letras_nao_ha_misto():
    p = _livro()
    assert misto.opcoes_da_pagina(p, p.paginas[0]) is None


def test_o_livro_liga_e_a_pagina_herda_as_escolhas_dele():
    p = _livro(misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_TUDO)
    opcoes = misto.opcoes_da_pagina(p, p.paginas[0])
    assert opcoes is not None
    assert opcoes.fora_do_texto == misto.FORA_TUDO
    assert opcoes.papel_da_gravura == misto.PAPEL_BRANCO
    assert opcoes.letras_na_moldura == misto.LETRAS_COR_PAPEL_BRANCO


def test_a_pagina_troca_so_nela():
    p = _livro(misto_so_as_letras=True)
    p.paginas[1].misto_fora_do_texto = misto.FORA_APAGAR
    p.paginas[1].misto_letras_na_moldura = misto.LETRAS_PRETAS
    assert misto.opcoes_da_pagina(p, p.paginas[0]).fora_do_texto == misto.FORA_REDE
    assert misto.opcoes_da_pagina(p, p.paginas[1]).fora_do_texto == misto.FORA_APAGAR
    assert misto.opcoes_da_pagina(p, p.paginas[1]).letras_na_moldura == misto.LETRAS_PRETAS


def test_a_pagina_desliga_o_misto_do_livro_ou_liga_sem_o_livro():
    p = _livro(misto_so_as_letras=True)
    p.paginas[0].misto_so_as_letras = False
    assert misto.opcoes_da_pagina(p, p.paginas[0]) is None
    assert misto.opcoes_da_pagina(p, p.paginas[1]) is not None
    q = _livro()
    q.paginas[1].misto_so_as_letras = True
    assert misto.opcoes_da_pagina(q, q.paginas[0]) is None
    assert misto.opcoes_da_pagina(q, q.paginas[1]) is not None


def test_valor_estranho_vindo_do_arquivo_vira_o_padrao():
    """Um projeto mexido a mao (ou de uma versao futura) nao derruba nada."""
    p = _livro(misto_so_as_letras=True, misto_fora_do_texto="xyz",
               misto_papel_da_gravura=3, misto_letras_na_moldura=None)
    opcoes = misto.opcoes_da_pagina(p, p.paginas[0])
    assert opcoes == misto.OpcoesDoMisto()
    p.paginas[0].misto_fora_do_texto = "tambem nao"
    assert misto.opcoes_da_pagina(p, p.paginas[0]).fora_do_texto == misto.FORA_REDE


def test_objeto_sem_os_campos_e_misto_desligado():
    """Projeto de outra versao em memoria (sem os atributos): desligado."""
    class Velho:
        pass

    assert misto.opcoes_da_pagina(Velho(), Velho()) is None


# --- gravar e abrir ---------------------------------------------------------

def test_ida_e_volta_pelo_json_guarda_livro_e_pagina():
    p = _livro(misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_APAGAR,
               misto_papel_da_gravura=misto.PAPEL_COMO_ESCANEADO,
               misto_letras_na_moldura=misto.LETRAS_COR_FUNDO_ORIGINAL)
    p.paginas[1].misto_so_as_letras = False
    p.paginas[1].misto_fora_do_texto = misto.FORA_TUDO
    volta = Projeto.de_dicionario(json.loads(json.dumps(p.para_dicionario())))
    for campo in misto.CAMPOS_DO_MISTO:
        assert getattr(volta, campo) == getattr(p, campo), campo
        for a, b in zip(volta.paginas, p.paginas):
            assert getattr(a, campo) == getattr(b, campo), campo
    assert misto.opcoes_da_pagina(volta, volta.paginas[1]) is None
    assert misto.opcoes_da_pagina(volta, volta.paginas[0]).papel_da_gravura == \
        misto.PAPEL_COMO_ESCANEADO


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


def test_ida_e_volta_pelo_disco(raiz, tmp_path):
    livro = tmp_path / "livro.pdf"
    livro.write_bytes(b"A" * 300_000)
    p = _livro(misto_so_as_letras=True)
    p.caminho_entrada = str(livro)
    p.paginas[0].misto_letras_na_moldura = misto.LETRAS_PRETAS
    resumo = projetos.criar(p, total_paginas=2)
    projetos.salvar_estado(resumo, p)
    volta = projetos.carregar_estado(resumo)
    assert volta.misto_so_as_letras is True
    assert volta.paginas[0].misto_letras_na_moldura == misto.LETRAS_PRETAS
    assert volta.paginas[1].misto_letras_na_moldura is None


# --- o projeto de antes destes campos --------------------------------------

def test_o_arquivo_de_antes_nao_tem_os_campos():
    """Garante que o teste de baixo testa mesmo um arquivo antigo."""
    dados = json.loads(ANTIGO.read_text(encoding="utf-8"))
    assert not [k for k in dados if k.startswith("misto")]
    assert not [k for p in dados["paginas"] for k in p if k.startswith("misto")]


def test_projeto_de_antes_abre_igual_com_o_misto_desligado():
    dados = json.loads(ANTIGO.read_text(encoding="utf-8"))
    volta = Projeto.de_dicionario(json.loads(json.dumps(dados)))
    # o que ja existia volta como estava
    assert volta.filtro_padrao == "preto_e_branco"
    assert volta.pb_decoracao_em_preto_e_branco is True
    assert [p.filtro for p in volta.paginas] == ["preto_e_branco", "preto_e_branco", "original"]
    assert volta.paginas[0].forca_preto == 60
    assert volta.paginas[0].recorte == (0.01, 0.02, 0.98, 0.97)
    assert volta.paginas[1].gravura_forma == "retangular"
    assert not volta.paginas[1].obter_selecao().vazia
    assert volta.paginas[2].alertas == ["cor"] and volta.paginas[2].revisada
    # e o Misto desligado em todas as paginas
    assert volta.misto_so_as_letras is False
    for pagina in volta.paginas:
        assert misto.opcoes_da_pagina(volta, pagina) is None
    # regravado, continua abrindo (agora com os campos novos)
    de_novo = Projeto.de_dicionario(json.loads(json.dumps(volta.para_dicionario())))
    assert de_novo.para_dicionario() == volta.para_dicionario()
