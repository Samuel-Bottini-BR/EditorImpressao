"""Provas do porteiro das mudanças (K09 a K15, K17, K18), num repositório git de verdade numa pasta temporária.

Palavras do Samuel: D-791 ("b": barram desde o primeiro dia); D-796 ("1, mas tem que ser explissito o pedido né" e,
logo depois, "o porteiro tem que bloquear"); D-798 ("fechou": só quem confere escreve o rótulo de pronto para
conferir, nunca quem construiu).

Cada conferência acusa um exemplo errado feito de propósito e não acusa o certo. O git é o de verdade (D-767), com um
"GitHub" que é outra pasta; nada toca o repositório do projeto.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes import porteiro_mudancas as pm
from regras_dos_agentes.livro import Livro
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva

LIVRO = ("| D-605 | 03/11/2026 | \"A partir de agora, nenhuma função nova\" | o novo não estraga | x | x | x | x | x |\n"
         "| D-774 | 18/11/2026 | \"ok\" | os testes antigos que cobram o jeito errado mudam | x | x | x | x | x |\n"
         "| D-900 | 19/11/2026 | \"pode pôr a biblioteca\" | entra a biblioteca nova no requirements | x | x | x | x | x |\n")
TESTE_VELHO = ('"""Teste antigo."""\n\n\ndef test_um():\n    """Um."""\n    assert 1 == 1\n\n\n'
               'def test_dois():\n    """Dois."""\n    assert 2 == 2\n')
LISTA = {"situacao": "valendo", "sim_do_samuel": {"em": "19/11/2026", "palavras": "sim"},
         "itens": [{"arquivo": "atualizacao.py", "conferencia": "K02", "texto": "x", "quantas": 1, "data": "2026-11-19",
                    "passo": "3", "motivo": "prova"}]}


@pytest.fixture
def repo(tmp_path) -> tuple[RepositorioDeProva, str]:
    """Um repositório com o commit de partida: Livro, um teste antigo, core/, ui/, a lista e o requirements."""
    r = RepositorioDeProva.novo(tmp_path)
    r.escrever("docs/plano/DECISOES.md", LIVRO)
    r.escrever("tests/test_velho.py", TESTE_VELHO)
    r.escrever("core/a.py", '"""Processamento."""\n')
    r.escrever("ui/b.py", '"""Tela."""\n')
    r.escrever("requirements.txt", "numpy>=2.0\n")
    r.escrever("tests/conferencias_excecoes.json", json.dumps(LISTA))
    base = r.commit("partida")
    return r, base


def livro(r: RepositorioDeProva) -> Livro:
    """O Livro da cópia de prova."""
    return Livro.do_repositorio(r.raiz)


def conferencias(achados) -> list[str]:
    """Os códigos dos achados, em ordem."""
    return sorted(a.conferencia for a in achados)


# ---------------------------------------------------------------- K10 (com a D-798)

def test_k10_barra_o_rotulo_de_pronto_no_ramo_de_quem_construiu(repo):
    """D-798: o rótulo de pronto para conferir escrito pelo implementador (ou layout) é barrado; o do verificador não."""
    r, base = repo
    r.escrever("relatorios/x/ONDE-PAREI.md", "# Entrega\n\nPRONTO PARA CONFERIR\n")
    r.commit("entrega")
    assert conferencias(pm.k10(r.raiz, base, "implementador")) == ["K10"]
    assert conferencias(pm.k10(r.raiz, base, "layout")) == ["K10"]
    assert pm.k10(r.raiz, base, "verificador") == [] and pm.k10(r.raiz, base, "quebrador") == []


def test_k10_barra_aprovado_e_x_no_plano_e_aceita_a_citacao_entre_aspas(repo):
    """APROVADO escrito por agente e [x] no plano são barrados; a regra citada entre aspas, não."""
    r, base = repo
    r.escrever("relatorios/x/ONDE-PAREI.md", 'Nunca escrevo "APROVADO" nem `PRONTO PARA CONFERIR`.\n')
    r.commit("citação")
    assert pm.k10(r.raiz, base, "implementador") == []
    r.escrever("relatorios/x/ONDE-PAREI.md", "Item APROVADO.\n")
    r.escrever("docs/plano/PLANO-DEFINITIVO.md", "- [x] 2.13 cortar\n")
    r.commit("aprovou")
    assert conferencias(pm.k10(r.raiz, base, "verificador")) == ["K10", "K10"]


# ---------------------------------------------------------------- K11

def test_k11_barra_teste_antigo_mudado_ou_apagado(repo):
    """D-605: teste antigo mudado (ou apagado) sem o commit citar o nome dele e a decisão é barrado."""
    r, base = repo
    r.escrever("tests/test_velho.py", TESTE_VELHO.replace("assert 2 == 2", "assert True"))
    r.commit("enfraquece o teste")
    achados = pm.k11(r.raiz, base, livro(r))
    assert [(a.conferencia, a.texto) for a in achados] == [("K11", "test_dois")]
    r.apagar("tests/test_velho.py")
    r.commit("apaga")
    assert sorted(a.texto for a in pm.k11(r.raiz, base, livro(r))) == ["test_dois", "test_um"]


def test_k11_aceita_a_mudanca_autorizada_e_o_teste_novo(repo):
    """O commit que cita o nome do teste e a decisão do Livro (a D-774) passa; teste novo e espaço no fim, também."""
    r, base = repo
    r.escrever("tests/test_velho.py", TESTE_VELHO.replace("assert 2 == 2", "assert 2 == 2 + 0  ") +
               '\n\ndef test_novo():\n    """Novo."""\n    assert 3\n')
    r.commit("test_dois passa a cobrar o jeito certo (D-774)")
    assert pm.k11(r.raiz, base, livro(r)) == []
    r.escrever("tests/test_velho.py", TESTE_VELHO.replace("assert 1 == 1", "assert 0 == 0"))
    r.commit("muda test_um (D-999, que não existe no Livro)")
    assert [a.texto for a in pm.k11(r.raiz, base, livro(r))] == ["test_um"]


# ---------------------------------------------------------------- K12

def test_k12_barra_funcao_mexida_sem_docstring_e_arquivo_sem_docstring(repo):
    """Função mexida sem docstring e arquivo novo sem docstring são barrados; a de 2 linhas dentro de outra, não."""
    r, base = repo
    r.escrever("core/a.py", '"""Processamento."""\n\n\ndef f(x):\n    return x\n\n\ndef g():\n    """Com doc."""\n'
                            "    def h():\n        return 1\n    return h\n")
    r.escrever("core/novo.py", "X = 1\n")
    r.commit("mexe")
    achados = pm.k12(r.raiz, base)
    assert sorted((a.arquivo, a.texto) for a in achados) == [("core/a.py", "f"), ("core/novo.py", "core/novo.py")]


# ---------------------------------------------------------------- K13 e K14 (com a D-796)

def test_k13_barra_o_agente_de_tela_em_core_fora_da_lista_do_pedido(repo):
    """D-796: agente de tela mexeu em core/ sem o pedido nomear: barrado; com o arquivo nomeado, passa."""
    r, base = repo
    r.escrever("core/a.py", '"""Processamento mudado."""\n')
    r.escrever("ui/b.py", '"""Tela mudada."""\n')
    r.commit("mexe")
    mudados = git.arquivos_mudados(r.raiz, base)
    assert [(a.conferencia, a.arquivo) for a in pm.k13(mudados, "layout", ["ui/"])] == [("K13", "core/a.py")]
    assert pm.k13(mudados, "layout", ["ui/", "core/a.py"]) == []


def test_k13_barra_implementador_em_ui_e_verificador_no_programa(repo):
    """O implementador em ui/ sem pedido e o verificador no programa são barrados."""
    r, base = repo
    r.escrever("core/a.py", '"""Mudado."""\n')
    r.escrever("ui/b.py", '"""Mudado."""\n')
    r.commit("mexe")
    mudados = git.arquivos_mudados(r.raiz, base)
    assert [a.arquivo for a in pm.k13(mudados, "implementador", ["core/a.py"])] == ["ui/b.py"]
    assert sorted(a.arquivo for a in pm.k13(mudados, "verificador", ["relatorios/"])) == ["core/a.py", "ui/b.py"]


def test_k14_so_avisa_arquivo_fora_da_lista(repo):
    """K14 não barra: avisa que o pacote pode estar incompleto. A pasta do relatório não conta."""
    r, base = repo
    r.escrever("core/a.py", '"""Mudado."""\n')
    r.escrever("relatorios/x/ONDE-PAREI.md", "# x\n")
    r.commit("mexe")
    avisos = pm.k14(git.arquivos_mudados(r.raiz, base), ["ui/"], "relatorios/x/")
    assert [(a.arquivo, a.barra) for a in avisos] == [("core/a.py", False)]


# ---------------------------------------------------------------- K15 e K17

def test_k15_requirements_so_muda_com_o_sim_citado_no_commit(repo):
    """Trocar biblioteca sem citar a decisão do Livro que fala dela é barrado; citando, passa."""
    r, base = repo
    r.escrever("requirements.txt", "numpy>=2.0\nrequests\n")
    r.commit("acrescenta requests (D-605)")
    mudados = git.arquivos_mudados(r.raiz, base)
    assert conferencias(pm.k15(r.raiz, base, mudados, livro(r))) == ["K15"]
    r.escrever("requirements.txt", "numpy>=2.0\nrequests>=2\n")
    r.commit("biblioteca nova com o sim do Samuel (D-900)")
    assert pm.k15(r.raiz, base, mudados, livro(r)) == []


def test_k17_barra_mexer_nas_regras_e_acrescentar_item_na_lista(repo):
    """O Livro mexido sem pedido, e um item novo na lista de exceções, são barrados; tirar item, não."""
    r, base = repo
    lista = dict(LISTA, itens=LISTA["itens"] + [dict(LISTA["itens"][0], arquivo="main.py")])
    r.escrever("tests/conferencias_excecoes.json", json.dumps(lista))
    r.escrever("docs/plano/DECISOES.md", LIVRO + "| D-901 | x | x | x |\n")
    r.commit("mexe")
    mudados = git.arquivos_mudados(r.raiz, base)
    achados = pm.k17(r.raiz, base, mudados, ["core/"])
    assert sorted(a.arquivo for a in achados) == ["docs/plano/DECISOES.md", "tests/conferencias_excecoes.json"]
    r.escrever("tests/conferencias_excecoes.json", json.dumps(dict(LISTA, itens=[])))
    r.escrever("docs/plano/DECISOES.md", LIVRO)
    r.commit("só tira")
    assert pm.k17(r.raiz, base, git.arquivos_mudados(r.raiz, base), ["core/"]) == []


# ---------------------------------------------------------------- K09 e K18

def test_k09_relatorio_so_em_md_e_barrado(repo):
    """Relatório da pasta do trabalho sem o .html e o .pdf é barrado; o ONDE-PAREI e os anexos não contam."""
    r, _ = repo
    pasta = r.raiz / "relatorios" / "x"
    r.escrever("relatorios/x/ONDE-PAREI.md", "# x\n")
    r.escrever("relatorios/x/anexos/pacote.md", "# x\n")
    r.escrever("relatorios/x/relatorio.md", "# x\n")
    assert [a.arquivo for a in pm.k09(pasta, r.raiz)] == ["relatorios/x/relatorio.md"]
    r.escrever("relatorios/x/relatorio.html", "<p>x</p>")
    (pasta / "relatorio.pdf").write_bytes(b"%PDF-1.4")
    assert pm.k09(pasta, r.raiz) == []


def test_k18_barra_mudanca_fora_de_commit_e_sem_push(repo):
    """Mudança fora de commit e commit que não foi ao "GitHub" são barrados; depois do push, passa."""
    r, _ = repo
    assert "o ramo não acompanha" in pm.k18(r.raiz)[0].porque
    r.enviar()
    assert pm.k18(r.raiz) == []
    r.escrever("core/a.py", '"""Mudado e sem commit."""\n')
    assert conferencias(pm.k18(r.raiz)) == ["K18"]
    r.commit("agora com commit")
    assert "ainda não está no GitHub" in pm.k18(r.raiz)[0].porque
    r.enviar()
    assert pm.k18(r.raiz) == []


def test_git_que_nao_responde_nunca_vira_passou(repo):
    """Commit de partida que não existe: a conferência não passa calada, levanta o motivo (GitFalhou)."""
    r, _ = repo
    with pytest.raises(git.GitFalhou):
        pm.conferir_mudancas(r.raiz, "0" * 40, "implementador", [], r.raiz / "relatorios", livro(r), False)
