"""Provas do juiz do porteiro (R2 e R3 da terceira volta de quem quebrou): o código e a lista da versão de teste
julgando o ramo do agente, de fora dele.

Palavras do Samuel (D-791, 18/11): "b" (o porteiro barra desde o primeiro dia); à pergunta "o que já está errado no
código fica numa lista, que só diminui e só ganha item com o seu "sim"?": "Sim".

Cada prova monta, numa pasta temporária: a "versão de teste" (uma cópia deste pacote e uma lista de confiança) e a
cópia de um ramo de agente (um repositório git de verdade). O juiz roda como a rodada do GitHub o rodará: de dentro da
pasta da versão de teste, `python -m regras_dos_agentes juiz --conferido <ramo>` (um Python de verdade, o código
copiado). A última prova roda o próprio script do workflow (`anexos/juiz-no-workflow/porteiro_juiz.sh`), com um
"GitHub" que é outra pasta. Nada toca o repositório do projeto.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "relatorios" / "passo0-2026-11-19" / "anexos" / "juiz-no-workflow" / "porteiro_juiz.sh"
DEFEITO = ('"""O atualizador."""\nimport subprocess\n\n\ndef lancar(c):\n    """Lança."""\n'
           '    subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)\n')
TEXTO = "subprocess.Popen(c, creationflags=subprocess.DETACHED_PROCESS)"
SIM = {"decisao": "D-900", "em": "20/11/2026", "palavras": "sim, pode ligar a lista"}


def lista(situacao: str = "valendo", itens: list | None = None) -> str:
    """Uma lista de exceções que deixa o defeito de `atualizacao.py` (K01 e K02)."""
    padrao = [{"arquivo": "atualizacao.py", "conferencia": k, "funcao": "lancar", "texto": TEXTO, "quantas": 1,
               "data": "2026-11-19", "passo": "3", "motivo": "prova"} for k in ("K01", "K02")]
    return json.dumps({"situacao": situacao, "sim_do_samuel": SIM if situacao == "valendo" else None,
                       "itens": padrao if itens is None else itens})


def versao_de_teste(pasta: Path, texto_da_lista: str) -> Path:
    """A pasta do juiz: uma cópia do pacote e a lista de confiança (o que a rodada tira da versão de teste)."""
    shutil.copytree(RAIZ / "regras_dos_agentes", pasta / "regras_dos_agentes",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (pasta / "tests").mkdir(parents=True)
    (pasta / "tests" / "conferencias_excecoes.json").write_text(texto_da_lista, encoding="utf-8")
    return pasta


# O mínimo que todo ramo tem e o porteiro cobra numa leitura completa: a folha de estilo (K22) e um agente (K23).
FOLHA = ('TEMAS = {"escuro": {"rolagem": "#4A4D54"}, "cinza": {"rolagem": "#6A6A6A"}, '
         '"claro": {"rolagem": "#B5B3AC"}}\n'
         '\n\ndef folha(c):\n    """A folha de estilo."""\n'
         '    return f"QScrollBar::handle:vertical {{ background: {c["rolagem"]}; }}"\n')
AGENTE = "---\nname: implementador\ntools: Read, Write\n---\n"


def escrever_o_minimo(r: RepositorioDeProva, texto_da_lista: str, atualizacao: str) -> None:
    """O programa do ramo: o atualizador, a folha de estilo, um agente e a lista."""
    r.escrever("atualizacao.py", atualizacao)
    r.escrever("ui/estilo.py", FOLHA)
    r.escrever(".claude/agents/implementador.md", AGENTE)
    r.escrever("tests/conferencias_excecoes.json", texto_da_lista)


def ramo(pasta: Path, texto_da_lista: str, atualizacao: str = DEFEITO) -> RepositorioDeProva:
    """A cópia do ramo do agente: o programa e a lista dele, num repositório git de verdade."""
    r = RepositorioDeProva.novo(pasta)
    escrever_o_minimo(r, texto_da_lista, atualizacao)
    r.commit("o ramo")
    return r


def julgar(juiz: Path, conferido: Path) -> subprocess.CompletedProcess:
    """Roda o juiz como a rodada do GitHub: de dentro da pasta do juiz, com o Python de verdade."""
    ambiente = dict(os.environ, PYTHONUTF8="1")
    ambiente.pop("GITHUB_ACTIONS", None)
    return subprocess.run([sys.executable, "-m", "regras_dos_agentes", "juiz", "--conferido", str(conferido)],
                          cwd=juiz, capture_output=True, text=True, encoding="utf-8", env=ambiente)


def test_lista_ainda_proposta_mostra_nao_conferido_e_nao_passa_calado(tmp_path):
    """Antes do "sim" (a lista da versão de teste é proposta): "PORTEIRO: NAO CONFERIDO", nunca "CONFERIDO"."""
    feito = julgar(versao_de_teste(tmp_path / "juiz", lista("proposta")), ramo(tmp_path / "r", lista("proposta")).raiz)
    assert feito.returncode == 0 and "PORTEIRO: NAO CONFERIDO" in feito.stdout, feito.stdout + feito.stderr


def test_item_novo_ou_ligar_no_ramo_barra_mesmo_antes_do_sim(tmp_path):
    """R1: item novo (com ou sem "sim") e trocar a situação no ramo do agente barram, mesmo com a lista proposta."""
    novo = json.loads(lista("proposta"))["itens"] + [{"arquivo": "main.py", "conferencia": "K01", "funcao": "",
                                                      "texto": "x", "quantas": 1, "data": "d", "passo": "3",
                                                      "motivo": "eu", "sim": SIM}]
    juiz = versao_de_teste(tmp_path / "juiz", lista("proposta"))
    feito = julgar(juiz, ramo(tmp_path / "r1", lista("proposta", novo)).raiz)
    assert feito.returncode == 1 and "PORTEIRO: BARROU" in feito.stdout and "item novo" in feito.stdout
    feito = julgar(juiz, ramo(tmp_path / "r2", lista("valendo")).raiz)
    assert feito.returncode == 1 and "situação" in feito.stdout


def test_com_a_lista_valendo_o_ramo_certo_e_conferido(tmp_path):
    """Com a lista valendo na versão de teste e o ramo sem erro novo: "PORTEIRO: CONFERIDO"."""
    feito = julgar(versao_de_teste(tmp_path / "juiz", lista()), ramo(tmp_path / "r", lista()).raiz)
    assert feito.returncode == 0 and "PORTEIRO: CONFERIDO" in feito.stdout, feito.stdout + feito.stderr


def test_erro_novo_no_ramo_barra(tmp_path):
    """Um erro novo no ramo (fora da lista) barra."""
    feito = julgar(versao_de_teste(tmp_path / "juiz", lista()),
                   ramo(tmp_path / "r", lista(), DEFEITO + '    return ["schtasks", "/Run"]\n').raiz)
    assert feito.returncode == 1 and "schtasks" in feito.stdout


def test_r3_afrouxar_o_porteiro_do_ramo_nao_tira_lugar_da_lista(tmp_path):
    """R3: o ramo afrouxa o próprio porteiro (aqui, troca o pacote inteiro por um que não acha nada) e tira os lugares
    da lista sem consertar. O juiz usa o porteiro da versão de teste: os lugares ainda estão no código, e ele barra."""
    r = ramo(tmp_path / "r", lista(itens=[]))
    r.escrever("regras_dos_agentes/porteiro.py", '"""Um porteiro frouxo."""\n\n\ndef conferir_codigo(*a):\n'
                                                 '    """Não acha nada."""\n    return []\n')
    r.commit("porteiro afrouxado")
    feito = julgar(versao_de_teste(tmp_path / "juiz", lista()), r.raiz)
    assert feito.returncode == 1 and "DETACHED_PROCESS" in feito.stdout, feito.stdout


def test_ramo_que_apagou_a_lista_barra(tmp_path):
    """O ramo sem a lista de exceções barra."""
    r = ramo(tmp_path / "r", lista())
    r.apagar("tests/conferencias_excecoes.json")
    r.commit("apaga a lista")
    feito = julgar(versao_de_teste(tmp_path / "juiz", lista()), r.raiz)
    assert feito.returncode == 1 and "apagou a lista" in feito.stdout


def _bash() -> str:
    """O bash do Git para Windows (o mesmo que a rodada do GitHub usa no passo "shell: bash")."""
    for candidato in (shutil.which("bash"), r"C:\Program Files\Git\bin\bash.exe"):
        if candidato and Path(candidato).exists():
            return candidato
    pytest.fail("não achei o bash do Git para Windows para rodar o script do workflow")


def _rodar_o_script(conferido: RepositorioDeProva, tmp_path: Path, ligado: str = "0") -> subprocess.CompletedProcess:
    """Roda o script do workflow como a rodada: na pasta do ramo, com a versão de teste no "GitHub" de prova."""
    ambiente = dict(os.environ, VERSAO_DE_TESTE="obra-2026-10-26", PORTEIRO_LIGADO=ligado, PYTHONUTF8="1",
                    GITHUB_WORKSPACE=str(conferido.raiz), RUNNER_TEMP=str(tmp_path / "runner"))
    ambiente["PATH"] = str(Path(sys.executable).parent) + os.pathsep + ambiente.get("PATH", "")
    ambiente.pop("GITHUB_ACTIONS", None)
    ambiente.pop("GITHUB_STEP_SUMMARY", None)
    (tmp_path / "runner").mkdir(exist_ok=True)
    return subprocess.run([_bash(), str(SCRIPT)], cwd=conferido.raiz, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=ambiente)


def test_o_script_do_workflow_busca_o_juiz_da_versao_de_teste_e_barra_o_erro_novo(tmp_path):
    """O script de verdade: busca a versão de teste no "GitHub", tira de lá o porteiro e a lista, e julga o ramo."""
    base = RepositorioDeProva.novo(tmp_path / "base")
    shutil.copytree(RAIZ / "regras_dos_agentes", base.raiz / "regras_dos_agentes",
                    ignore=shutil.ignore_patterns("__pycache__"))
    base.escrever("tests/conferencias_excecoes.json", lista())
    base.escrever("atualizacao.py", DEFEITO)
    base.commit("versão de teste")
    base.enviar("obra-2026-10-26")
    conferido = RepositorioDeProva(tmp_path / "copia_do_ramo", base.remoto)
    git.criar_repositorio(conferido.raiz)
    git.configurar(conferido.raiz, "core.autocrlf", "false")
    escrever_o_minimo(conferido, lista(), DEFEITO + '    return ["schtasks", "/Run"]\n')
    conferido.commit("o ramo do agente")
    git.configurar(conferido.raiz, "remote.origin.url", str(base.remoto))
    feito = _rodar_o_script(conferido, tmp_path)
    assert feito.returncode == 1 and "PORTEIRO: BARROU" in feito.stdout and "schtasks" in feito.stdout, \
        feito.stdout + feito.stderr


def test_o_script_sem_porteiro_na_versao_de_teste_avisa_e_ligado_falha(tmp_path):
    """Antes de juntar o passo 0, a versão de teste não tem o porteiro: "NAO CONFERIDO" visível; com PORTEIRO_LIGADO=1
    (a gerente liga ao juntar), isso faz a rodada falhar."""
    base = RepositorioDeProva.novo(tmp_path / "base")
    base.escrever("LEIAME.md", "versão antiga\n")
    base.commit("versão de teste sem porteiro")
    base.enviar("obra-2026-10-26")
    conferido = RepositorioDeProva(tmp_path / "copia", base.remoto)
    git.criar_repositorio(conferido.raiz)
    conferido.escrever("atualizacao.py", DEFEITO)
    conferido.commit("ramo")
    git.configurar(conferido.raiz, "remote.origin.url", str(base.remoto))
    feito = _rodar_o_script(conferido, tmp_path)
    assert feito.returncode == 0 and "PORTEIRO: NAO CONFERIDO" in feito.stdout, feito.stdout + feito.stderr
    feito = _rodar_o_script(conferido, tmp_path, ligado="1")
    assert feito.returncode == 1 and "PORTEIRO: NAO CONFERIDO" in feito.stdout


def test_q6_antes_do_sim_tirar_da_lista_sem_consertar_barra(tmp_path):
    """Achado Q6 (quarta volta de quem quebrou, 19/11/2026): com a lista ainda "proposta", o juiz não julgava o código,
    e o ramo podia tirar itens da lista sem consertar (a lista que vai ao "sim" encolhia de mentira). Agora o item
    tirado que o porteiro da versão de teste ainda acha no código do ramo barra; tirar o de um lugar consertado não."""
    juiz = versao_de_teste(tmp_path / "juiz", lista("proposta"))
    sem_um = json.loads(lista("proposta"))["itens"][:1]
    feito = julgar(juiz, ramo(tmp_path / "r1", lista("proposta", sem_um)).raiz)
    assert feito.returncode == 1 and "sem conserto" in feito.stdout, feito.stdout + feito.stderr
    consertado = DEFEITO.replace(", creationflags=subprocess.DETACHED_PROCESS", "")
    feito = julgar(juiz, ramo(tmp_path / "r2", lista("proposta", []), consertado).raiz)
    assert feito.returncode == 0 and "PORTEIRO: NAO CONFERIDO" in feito.stdout, feito.stdout + feito.stderr
