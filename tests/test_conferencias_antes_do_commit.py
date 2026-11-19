"""Provas da conferência antes do commit (`ganchos/pre-commit`, D-791), com o git de verdade e um Python de verdade.

Palavras do Samuel (D-791): "b" (o porteiro barra desde o primeiro dia). O porteiro roda nos testes do GitHub e "a mesma
busca roda numa conferência do git antes do commit, só nos arquivos mudados" (plano-v3, passo 0).

Cada prova monta, numa pasta temporária, um repositório com uma cópia do pacote `regras_dos_agentes/` e do gancho,
liga o gancho só ali (`core.hooksPath ganchos`, nunca no repositório do projeto) e faz commits de verdade. O Python do
gancho é um ambiente de verdade criado na hora (`python -m venv`, sem bibliotecas: o pacote só usa o Python puro), no
mesmo lugar onde o gancho procura o `.venv` do projeto.

O que fica provado, além de barrar o erro: o gancho lê o que vai no commit (o índice), não a pasta; sem o Python, o
commit é barrado (nada passa sem conferir); e sem o gancho ligado o git não avisa nada (por isso quem garante é o
teste no GitHub).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva

RAIZ = Path(__file__).resolve().parent.parent
DEFEITO_1 = ('"""O atualizador."""\nimport subprocess\n\n\ndef lancar(c):\n    """Lança."""\n'
             '    subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)\n')
CERTO = '"""Um arquivo certo."""\n\n\ndef f():\n    """Nada de errado."""\n    return 1\n'


LIVRO = ('| D-791 | 18/11/2026 | Chat: "o que já está errado no código fica numa lista" · "sim" | a lista de '
         'exceções do porteiro | x | x | x | x | x |\n')
SIM = {"decisao": "D-791", "em": "19/11/2026", "palavras": "o que já está errado no código"}
FORJADO = {"decisao": "D-791", "em": "19/11/2026", "palavras": "sim"}     # o ataque de quem quebrou (achado N1)


def _lista(r: RepositorioDeProva, situacao: str = "valendo", mais: list | None = None, sim: dict | None = None) -> None:
    """A lista de exceções do repositório de prova: deixa o defeito 1 em atualizacao.py (K01 e K02, uma vez)."""
    texto = "subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)"
    itens = [{"arquivo": "atualizacao.py", "conferencia": k, "texto": texto, "quantas": 1, "data": "2026-11-19",
              "passo": "3", "motivo": "prova"} for k in ("K01", "K02")] + (mais or [])
    r.escrever("tests/conferencias_excecoes.json", json.dumps({
        "situacao": situacao, "sim_do_samuel": (sim or SIM) if situacao == "valendo" else None, "itens": itens}))


@pytest.fixture
def repo(tmp_path) -> RepositorioDeProva:
    """Repositório de prova com o pacote, o gancho ligado, o Python do .venv e a partida já no commit."""
    r = RepositorioDeProva.novo(tmp_path)
    shutil.copytree(RAIZ / "regras_dos_agentes", r.raiz / "regras_dos_agentes",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (r.raiz / "ganchos").mkdir()
    shutil.copy2(RAIZ / "ganchos" / "pre-commit", r.raiz / "ganchos" / "pre-commit")
    feito = subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(r.raiz / ".venv")],
                           capture_output=True, text=True)
    assert feito.returncode == 0, feito.stderr
    r.escrever(".gitignore", ".venv/\n__pycache__/\n")
    r.escrever("atualizacao.py", DEFEITO_1)
    r.escrever("docs/plano/DECISOES.md", LIVRO)
    _lista(r)
    r.commit("partida")
    # A versão de teste no "GitHub" de prova: é dela que o gancho lê o Livro que vale (achado N1).
    r.enviar("obra-2026-10-26")
    git.configurar(r.raiz, "core.hooksPath", "ganchos")
    r.escrever("LEIAME.md", "x\n")
    r.commit("o primeiro commit com o gancho ligado")
    return r


def test_o_gancho_barra_o_erro_novo_e_diz_onde(repo):
    """Um DETACHED_PROCESS novo num arquivo do programa: o commit é barrado, com a conferência e o arquivo."""
    repo.escrever("core/novo.py", DEFEITO_1)
    feito = repo.tentar_commit("erro novo")
    saida = feito.stdout + feito.stderr
    assert feito.returncode != 0, saida
    assert "K02" in saida and "core/novo.py" in saida
    assert git.mudancas_sem_commit(repo.raiz), "o commit não pode ter acontecido"


def test_o_gancho_barra_o_mesmo_erro_uma_vez_a_mais_no_arquivo_que_tem_excecao(repo):
    """A exceção é por lugar: o mesmo texto uma segunda vez no arquivo que tem exceção é barrado."""
    repo.escrever("atualizacao.py", DEFEITO_1 + "    subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)\n")
    feito = repo.tentar_commit("o mesmo erro de novo")
    assert feito.returncode != 0 and "K02" in feito.stdout + feito.stderr


def test_o_gancho_deixa_passar_o_commit_certo(repo):
    """Arquivo certo: o commit acontece."""
    repo.escrever("core/certo.py", CERTO)
    feito = repo.tentar_commit("certo")
    assert feito.returncode == 0, feito.stdout + feito.stderr


def test_o_gancho_le_o_que_vai_no_commit_e_nao_a_pasta(repo):
    """O que conta é o índice: o erro só na pasta (fora do commit) não barra; o erro no commit barra."""
    repo.escrever("core/a.py", CERTO)
    repo.adicionar("core/a.py")
    repo.escrever("core/a.py", DEFEITO_1)              # mudou a pasta depois do add: não vai no commit
    feito = repo.commit_do_indice("só o certo")
    assert feito.returncode == 0, feito.stdout + feito.stderr
    feito = repo.tentar_commit("agora o erro vai junto")
    assert feito.returncode != 0


def test_sem_o_python_o_gancho_barra_em_vez_de_passar_calado(repo):
    """Sem o Python do projeto, nada foi conferido: o commit é barrado e a mensagem diz por quê."""
    shutil.rmtree(repo.raiz / ".venv")
    repo.escrever("core/certo.py", CERTO)
    feito = repo.tentar_commit("sem python")
    assert feito.returncode != 0 and "não achei o Python" in feito.stdout + feito.stderr


def test_sem_o_gancho_ligado_o_git_nao_avisa_nada(repo):
    """O que a documentação diz (hook.c, find_hook): sem o gancho, o git faz o commit sem aviso. Quem garante é o GitHub."""
    git.configurar(repo.raiz, "core.hooksPath", "pasta_que_nao_existe")
    repo.escrever("core/novo.py", DEFEITO_1)
    feito = repo.tentar_commit("sem gancho")
    assert feito.returncode == 0 and "K02" not in feito.stdout + feito.stderr


def test_com_a_lista_ainda_proposta_o_gancho_nao_barra_e_diz_isso(repo):
    """Enquanto o Samuel não disser "sim", a lista não vale: o gancho avisa o que barraria e deixa passar."""
    _lista(repo, "proposta")
    repo.commit("a lista volta a proposta")
    repo.escrever("core/novo.py", DEFEITO_1)
    feito = repo.tentar_commit("erro com a lista proposta")
    assert feito.returncode == 0
    assert "proposta" in feito.stdout + feito.stderr and "K02" in feito.stdout + feito.stderr


def test_o_gancho_e_o_github_acham_o_mesmo_no_mesmo_arquivo(repo):
    """Caminho → função: o GitHub (o repositório inteiro, da pasta) e o gancho (o índice) chamam a mesma conferência
    (`porteiro.conferir_codigo`) e acham os mesmos lugares no mesmo arquivo."""
    from regras_dos_agentes import porteiro

    repo.escrever("core/novo.py", DEFEITO_1)
    repo.adicionar("core/novo.py")
    _, do_commit = porteiro.achados_do_proximo_commit(repo.raiz)
    _, do_repositorio = porteiro.achados_do_repositorio(repo.raiz)
    chave = lambda a: (a.conferencia, a.arquivo, a.linha, a.texto)  # noqa: E731
    assert sorted(map(chave, do_commit)) == sorted(chave(a) for a in do_repositorio if a.arquivo == "core/novo.py")
    assert {a.conferencia for a in do_commit} == {"K01", "K02"}


def test_o_gancho_barra_o_agente_que_poe_o_proprio_erro_na_lista_no_mesmo_commit(repo):
    """Achado 7 de quem tentou quebrar (19/11): o erro novo e o item dele na lista, no mesmo commit, passavam no gancho.
    Agora a lista do commit é comparada com a do último commit: item novo sem o "sim" próprio barra."""
    repo.escrever("core/novo.py", DEFEITO_1)
    texto = "subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)"
    _lista(repo, mais=[{"arquivo": "core/novo.py", "conferencia": k, "texto": texto, "quantas": 1,
                        "data": "2026-11-19", "passo": "3", "motivo": "eu mesmo"} for k in ("K01", "K02")])
    feito = repo.tentar_commit("erro novo e o item dele")
    assert feito.returncode != 0 and "item novo na lista" in feito.stdout + feito.stderr


def test_o_gancho_barra_o_sim_forjado_num_item_novo(repo):
    """Achado N1 da segunda volta de quem quebrou (19/11): o erro novo e o item dele na lista, com o "sim"
    `{"decisao": "D-791", "palavras": "sim"}`, passavam no gancho (código 0). Agora barram: o "sim" é conferido no
    Livro da versão de teste e tem de trazer um trecho das palavras do Samuel."""
    repo.escrever("atualizacao.py", DEFEITO_1 + '    return ["schtasks", "/Run", "/TN", "nova"]\n')
    texto = 'return ["schtasks", "/Run", "/TN", "nova"]'
    _lista(repo, mais=[{"arquivo": "atualizacao.py", "conferencia": "K01", "texto": texto, "quantas": 1,
                        "data": "2026-11-19", "passo": "3", "motivo": "eu mesmo", "sim": FORJADO}])
    feito = repo.tentar_commit("erro novo com o sim forjado")
    assert feito.returncode != 0 and "item novo na lista" in feito.stdout + feito.stderr


def test_o_gancho_barra_a_lista_valendo_com_o_sim_forjado(repo):
    """A lista inteira "valendo" com o "sim" forjado: barrada (o Livro da versão de teste não confirma)."""
    _lista(repo, sim=FORJADO)
    repo.escrever("core/certo.py", CERTO)
    feito = repo.tentar_commit("sim forjado")
    assert feito.returncode != 0 and "não confirma" in feito.stdout + feito.stderr


def test_sem_internet_o_gancho_barra_em_vez_de_passar(repo):
    """Sem o GitHub (aqui, o "GitHub" de prova sumiu), o gancho não consegue ler o Livro da versão de teste: barra
    (código 3), nunca passa calado."""
    git.configurar(repo.raiz, "remote.origin.url", str(repo.remoto.parent / "github_que_nao_existe"))
    repo.escrever("core/certo.py", CERTO)
    feito = repo.tentar_commit("sem internet")
    assert feito.returncode != 0 and "Não deu para conferir" in feito.stdout + feito.stderr
