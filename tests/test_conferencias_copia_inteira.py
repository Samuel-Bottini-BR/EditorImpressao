"""Teste de reversão (CLAUDE.md §4.7): buscar a versão de teste nunca deixa rasa uma cópia inteira do repositório.

O defeito (19/11/2026, achado pela gerente): o repositório do Samuel no PC ficou RASO (`.git/shallow` com 746dbda6,
93ab77fb e 8a34960c), e o `git merge` do passo 0 na versão de teste recusou ("unrelated histories"). A gerente
restaurou com `git fetch --unshallow origin`.

A causa: o script do juiz do workflow (`anexos/juiz-no-workflow/porteiro_juiz.sh`) buscava a versão de teste sempre
com `git fetch --depth=1`. Ele foi rodado à mão na cópia do agente (uma worktree, que divide a pasta .git com o
repositório do PC), como "prova de verdade" da terceira volta: com a versão de teste `obra-2026-10-26` (a ponta era
746dbda6) e com o ramo do passo 0 no lugar dela (a ponta era 93ab77fb). Os dois são exatamente as duas primeiras linhas
do `.git/shallow`. O `--depth=1` deixa a cópia rasa mesmo quando o ramo buscado já estava em dia (por isso nenhum
registro de "fetch" no histórico dos ramos remotos). Depois de raso, `buscar_ramo` (que só usa `--depth=1` em cópia
rasa) continuou buscando raso e acrescentou 8a34960c (a terceira linha).

O conserto: o script segue a mesma regra de `conversa_com_o_git.buscar_ramo` (`--depth=1` só se a cópia já é rasa).
Esta prova roda os dois, de verdade (o git e o bash de verdade), numa cópia inteira num repositório de prova em pasta
temporária, com um "GitHub" que é outra pasta, e cobra que a cópia continua inteira. Falha no script antigo (o
`--depth=1` fixo) e passa no novo. Nada toca o repositório do projeto.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva
from tests.test_conferencias_juiz import DEFEITO, RAIZ, _rodar_o_script, escrever_o_minimo, lista


def _versao_de_teste_com_historia(pasta: Path) -> RepositorioDeProva:
    """A versão de teste no "GitHub" de prova, com dois commits (uma história para cortar) e o porteiro."""
    base = RepositorioDeProva.novo(pasta)
    base.escrever("LEIAME.md", "primeiro\n")
    base.commit("primeiro commit da versão de teste")
    shutil.copytree(RAIZ / "regras_dos_agentes", base.raiz / "regras_dos_agentes",
                    ignore=shutil.ignore_patterns("__pycache__"))
    base.escrever("tests/conferencias_excecoes.json", lista())
    base.escrever("atualizacao.py", DEFEITO)
    base.commit("segundo commit da versão de teste")
    base.enviar("obra-2026-10-26")
    return base


def _copia_inteira(pasta: Path, base: RepositorioDeProva) -> RepositorioDeProva:
    """A cópia do agente como a do PC: inteira, com a versão de teste já buscada (sem `--depth`) e um commit dele."""
    copia = RepositorioDeProva(pasta, base.remoto)
    git.criar_repositorio(copia.raiz)
    git.configurar(copia.raiz, "core.autocrlf", "false")
    git.configurar(copia.raiz, "remote.origin.url", str(base.remoto))
    escrever_o_minimo(copia, lista(), DEFEITO)
    copia.commit("o ramo do agente")
    git.buscar_ramo(copia.raiz, "obra-2026-10-26")
    assert not git.e_raso(copia.raiz), "a cópia de partida da prova tem de ser inteira"
    return copia


def test_o_script_do_juiz_numa_copia_inteira_deixa_a_copia_inteira(tmp_path):
    """Bug de 19/11/2026 (repositório do PC raso depois do juiz rodado à mão): o script do workflow, rodado numa cópia
    inteira, busca a versão de teste e julga, sem deixar a cópia rasa. Falha com o `--depth=1` fixo."""
    base = _versao_de_teste_com_historia(tmp_path / "base")
    copia = _copia_inteira(tmp_path / "copia_do_ramo", base)
    feito = _rodar_o_script(copia, tmp_path)
    assert "PORTEIRO: " in feito.stdout and "não deu para buscar" not in feito.stdout, feito.stdout + feito.stderr
    assert not git.e_raso(copia.raiz), "o script deixou a cópia inteira rasa (--depth=1 numa cópia inteira)"


def test_buscar_ramo_numa_copia_inteira_deixa_a_copia_inteira(tmp_path):
    """O mesmo cuidado na peça única do git (`buscar_ramo`, usada pela proteção e pelo Livro da versão de teste):
    buscar de novo, com a versão de teste já em dia e depois de ela andar, não deixa a cópia inteira rasa."""
    base = _versao_de_teste_com_historia(tmp_path / "base")
    copia = _copia_inteira(tmp_path / "copia_do_ramo", base)
    git.buscar_ramo(copia.raiz, "obra-2026-10-26")          # o ramo já em dia: o caso que não deixa registro
    assert not git.e_raso(copia.raiz)
    base.escrever("LEIAME.md", "terceiro\n")
    novo = base.commit("terceiro commit da versão de teste")
    base.enviar("obra-2026-10-26")
    assert git.buscar_ramo(copia.raiz, "obra-2026-10-26") == novo
    assert not git.e_raso(copia.raiz)
