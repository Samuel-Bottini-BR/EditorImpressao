"""Provas da D-749 (Samuel, 17/11/2026), sem tocar o Windows.

Pergunta: "se o Kaique clicar "Sim" e a preparação der erro no meio, a pergunta volta na próxima abertura?
Sugiro que sim." Resposta: "Sim".

Na prática: se o "Sim" da pergunta do Windows da primeira abertura vem com a preparação do computador parada no meio
ou com erro, a preparação conta como NÃO feita: a pergunta volta na próxima abertura, como depois de um "Não" (D-741),
e o programa nunca fica achando que está preparado.

ATUALIZADOR NOVO (23/11/2026, D-830; D-836 para os testes): o `--preparar-o-computador`, o `preparo.txt` e a marca
nas Configurações SAÍRAM. "Preparado?" passou a ser o que o Windows responde agora: a conta que abriu consegue gravar
na pasta do programa? (`atualizacao.pasta_aceita_gravacao`). E a licença da pasta é o ÚLTIMO passo da pergunta: a
peça do Windows para no primeiro passo que falha, então a pasta só aceita gravação se o Visual C++ e a retirada do
Inno deram certo antes. As provas de baixo cobram isso pelo caminho novo; as três que cobravam o `preparo.txt` e o
modo escondido saíram com eles (a lista teste por teste: relatorios/atualizador-novo/lista-dos-testes-d836.md).
"""

from __future__ import annotations

import pytest

import atualizacao
from core import fases_da_atualizacao as fases
from core import windows
from tests.ajudante_do_atualizador import Prova, programdata_de_prova  # noqa: F401


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado e o registro numa pasta de prova."""


@pytest.mark.parametrize("o_trabalho_disse", ["deu certo", "falhou"])
def test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta(tmp_path, o_trabalho_disse):
    """D-749 (adaptado pela D-836): "Sim", o trabalho com licença terminou (dizendo que deu certo, ou que falhou), mas a
    pasta continua sem aceitar gravação → conta como NÃO feita (o que vale é o teste de gravar feito de novo, nunca o
    que o trabalho anotou): nada é procurado, e a próxima abertura pergunta de novo."""
    p = Prova(tmp_path, grava=False, licenca="comecou")
    p.win.depois_do_sim = None
    if o_trabalho_disse == "falhou":
        class Falhou:
            comecou, resposta_da_pergunta = True, None

            def esperar(self):
                return windows.Resposta(windows.FALHOU, "o Visual C++ não foi instalado")

        p.win.comecar_pedido_de_licenca = lambda passos: p.win.pedidos.append([x.tipo for x in passos]) or Falhou()
    p.abrir()
    assert p.vp.chamadas == [] and p.atual.estado.fase is fases.Fase.PARADO
    seguinte = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz, fonte=p.atual.fonte,
                                       por_tras=lambda t: t(), pasta_grava=lambda r: False, chave_publica=None)
    seguinte.abrir([])
    assert len(p.win.pedidos) == 2, "a pergunta volta na próxima abertura"


def test_d749_visual_c_ou_inno_que_falham_contam_como_erro(tmp_path, monkeypatch):
    """D-749 (adaptado pela D-836): o Visual C++ que o Windows não instala (código de erro, ou terminou sem a versão no
    registro) e o Inno que não sai (a chave continua) são FALHA do passo; e a licença da pasta é o último passo, então
    nenhum dos dois deixa a pasta aceitando gravação."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    pasta = tmp_path / "current"
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA).mkdir(parents=True)
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ")
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: (1603, "")) is False
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: (0, "")) is False
    antiga = tmp_path / "Antiga"
    chave = {"UninstallString": str(antiga / "unins000.exe"), "InstallLocation": str(antiga)}
    assert windows.tirar_instalacao_do_inno(tmp_path / "nova", ler=lambda: chave, esperar_s=0).desfecho == windows.FALHOU
    tipos = [p.tipo for p in atualizacao.passos_do_preparo()]
    assert tipos[-1] == "dar_licenca_aos_usuarios" and tipos.index("instalar_visual_c") < len(tipos) - 1
