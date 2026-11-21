"""Testes da pasta das ferramentas do Samuel (core/pasta_das_ferramentas.py): o defeito 1 da prova à vista de 20/11/2026.

O DEFEITO (prova 6b; registro em C:\\EditorImpressaoProva\\prova6b.log)
    Seguida ao pé da letra a frase do próprio publicar (`publicar_versao_kaique.py --motor --pasta "..."`), rodada da
    cópia de trabalho `.claude\\worktrees\\passo2`, parou em "não achei um motor pronto do jeito novo", porque o motor
    foi procurado em `.claude\\worktrees\\EditorImpressao-arquivos\\ferramentas\\motor-kraken`, e não em
    `D:\\programas\\EditorImpressao-arquivos\\ferramentas\\motor-kraken`. O Visual C++ só foi achado porque uma montagem
    de 19/11 tinha criado uma pasta no lugar errado e baixado o arquivo para lá. A causa: seis lugares calculavam a pasta
    cada um por conta própria, a partir da pasta do código.

O QUE ESTES TESTES PROVAM (D-767: com o git de verdade, sem peça de mentira)
    Um repositório de prova de verdade (`regras_dos_agentes.repositorio_de_prova`), numa pasta com espaço no nome, com o
    código deste ramo copiado nele, e uma cópia de trabalho de verdade dele (`git worktree add`, em
    `.claude\\worktrees\\<nome>`, como no PC do Samuel), com a pasta errada de 19/11 imitada ao lado. Um Python à parte
    roda de dentro da cópia e diz onde cada um dos seis lugares procura. Os casos que podem falhar (sem git, cópia sem
    repositório, pasta principal sem a pasta do Samuel ao lado, o git que demora ou dá erro, o programa empacotado)
    rodam com o git de verdade; só o "empacotado" e a espia da bandeira sem janela trocam uma peça, para a lógica.

Seguro mexer: acrescentar casos. Arriscado: trocar o repositório de prova por caminhos inventados (deixa de provar).
"""

from __future__ import annotations

import functools
import inspect
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core import ocr_kraken  # noqa: E402
from regras_dos_agentes import conversa_com_o_git as git  # noqa: E402
from regras_dos_agentes.repositorio_de_prova import RepositorioDeProva  # noqa: E402

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="as ferramentas e o publicar são do Windows")

try:
    from core import pasta_das_ferramentas as pf  # noqa: E402
except ImportError:                                # no código de antes da volta 9 (a prova de reversão)
    pf = None


class _NuncaLevantada(Exception):
    """No lugar de `pf.SemPastaPrincipal` no código de antes da volta 10 (a prova de reversão): ninguém a levanta, então
    o `pytest.raises` dela falha, que é o que a reversão tem de mostrar."""

# O que o Python à parte lê de dentro da cópia: os seis lugares e o motor que o empacotar e o programa acham.
LER_OS_SEIS_LUGARES = r"""
import json
import compilar_detector_gravura, compilar_st_ferramentas, empacotar, montar_motor_kraken
from core import ocr_kraken
motor, erros = empacotar.achar_motor_kraken()
print(json.dumps({
    "empacotar.DOWNLOADS": str(empacotar.DOWNLOADS.parent),
    "empacotar.LUGARES_DO_MOTOR": str(empacotar.LUGARES_DO_MOTOR[1].parent),
    "ocr_kraken.lugares_do_motor": str(ocr_kraken.lugares_do_motor()[-1].parent),
    "montar_motor_kraken.PASTA_FERRAMENTAS": str(montar_motor_kraken.PASTA_FERRAMENTAS),
    "compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO": str(compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO),
    "compilar_st_ferramentas.pasta_de_ferramentas_padrao": str(compilar_st_ferramentas.pasta_de_ferramentas_padrao()),
    "motor do empacotar": str(motor) if motor else None,
    "motor do programa": str(ocr_kraken.achar_pasta_do_motor() or ""),
}))
"""


def _copiar_o_codigo(destino: Path) -> None:
    """O código deste ramo (o que roda: os .py da raiz, core/, regras_dos_agentes/ e as fontes do motor) no repositório
    de prova. Só copia; nada do projeto é mexido."""
    for arquivo in RAIZ.glob("*.py"):
        shutil.copy2(arquivo, destino / arquivo.name)
    for pasta in ("core", "regras_dos_agentes", "motor_kraken"):
        for arquivo in (RAIZ / pasta).rglob("*"):
            if arquivo.is_file() and "__pycache__" not in arquivo.parts and arquivo.suffix in (".py", ".txt"):
                alvo = destino / arquivo.relative_to(RAIZ)
                alvo.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(arquivo, alvo)


def _motor_de_prova(pasta: Path) -> Path:
    """Um motor com a forma do jeito novo e a ficha gravada pela função de verdade (como em test_publicar_versao)."""
    import montar_motor_kraken

    kraken = pasta / "python" / "Lib" / "site-packages" / "kraken"
    kraken.mkdir(parents=True)
    (pasta / "python" / "python.exe").write_bytes(b"MZ python")
    (kraken / "blla.mlmodel").write_bytes(b"modelo" * 100)
    (pasta / ocr_kraken.NOME_DO_SERVIDOR).write_text(f"VERSAO_PROTOCOLO = {ocr_kraken.VERSAO_PROTOCOLO}\n",
                                                     encoding="utf-8")
    montar_motor_kraken.gravar_ficha_do_motor(pasta)
    return pasta


def _pastas(base: Path) -> set[str]:
    """Todas as pastas que existem dentro de `base` (para conferir que nada novo foi criado)."""
    return {str(p.relative_to(base)) for p in base.rglob("*") if p.is_dir() and ".git" not in p.parts}


@pytest.fixture
def projeto(tmp_path):
    """O PC do Samuel em miniatura, numa pasta com espaço no nome: a pasta principal (um repositório de verdade, com o
    código deste ramo), a pasta das ferramentas ao lado dela (com um motor e um Visual C++ de prova), uma cópia de
    trabalho em `.claude\\worktrees\\minha copia` e a pasta errada de 19/11 imitada em `.claude\\worktrees`."""
    base = tmp_path / "programas do samuel"
    r = RepositorioDeProva.novo(base)                       # base\copia (a principal) e base\github (o remoto)
    _copiar_o_codigo(r.raiz)
    r.commit("o codigo do ramo")
    ferramentas = base / "EditorImpressao-arquivos" / "ferramentas"
    motor = _motor_de_prova(ferramentas / "motor-kraken")
    (ferramentas / "downloads").mkdir()
    (ferramentas / "downloads" / "vc_redist.x64.exe").write_bytes(b"MZ o certo")
    errada = r.raiz / ".claude" / "worktrees" / "EditorImpressao-arquivos" / "ferramentas" / "downloads"
    errada.mkdir(parents=True)
    (errada / "vc_redist.x64.exe").write_bytes(b"MZ o do lugar errado")
    copia = r.criar_copia_de_trabalho(r.raiz / ".claude" / "worktrees" / "minha copia", "copia-de-prova")
    return {"base": base, "principal": r.raiz, "copia": copia, "ferramentas": ferramentas, "motor": motor,
            "errada": errada.parent}


def _rodar_de_dentro(pasta: Path, script: str, ambiente: dict | None = None) -> dict:
    """Um Python à parte (o deste computador), rodando de dentro de `pasta` com o código que está lá (nada do projeto
    no caminho). Devolve o que ele imprimiu, lido como JSON."""
    env = dict(ambiente or os.environ)
    env.pop("PYTHONPATH", None)
    r = subprocess.run([sys.executable, "-c", script], cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=300, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def _mesma(a, b) -> bool:
    """O mesmo lugar no disco (o Windows não liga para maiúsculas)."""
    return a is not None and os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def test_defeito1_de_uma_copia_de_trabalho_os_seis_lugares_acham_a_pasta_certa(projeto):
    """O defeito 1 da prova à vista de 20/11/2026 (prova 6b): rodando de uma cópia de trabalho de verdade, os seis lugares
    (`empacotar.DOWNLOADS`, `empacotar.LUGARES_DO_MOTOR`, `core/ocr_kraken.lugares_do_motor`,
    `montar_motor_kraken.PASTA_FERRAMENTAS`, `compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO` e
    `compilar_st_ferramentas.pasta_de_ferramentas_padrao`) procuram na pasta das ferramentas AO LADO DA PASTA PRINCIPAL,
    e não na pasta errada de 19/11 (em `.claude\\worktrees`); o motor que o publicar --motor e o programa acham é o de
    lá. Numa pasta com espaço no nome. Rodado em 5c22a12d: os lugares apontam para `.claude\\worktrees\\EditorImpressao-arquivos`
    e o motor não é achado (o defeito antigo nº 330, para o programa)."""
    antes = _pastas(projeto["base"])
    lido = _rodar_de_dentro(projeto["copia"], LER_OS_SEIS_LUGARES)
    errados = {k: v for k, v in lido.items() if k.startswith(("empacotar.", "ocr_kraken.", "montar", "compilar"))
               and not _mesma(v, projeto["ferramentas"])}
    assert errados == {}, f"procuram fora de {projeto['ferramentas']}: {errados}"
    assert _mesma(lido["motor do empacotar"], projeto["motor"]), lido
    assert _mesma(lido["motor do programa"], projeto["motor"]), lido
    assert _pastas(projeto["base"]) - antes <= {p for p in _pastas(projeto["base"]) if "__pycache__" in p}, \
        "rodar de dentro da cópia criou pasta"


def test_defeito1_da_pasta_principal_nada_muda(projeto):
    """D-605: rodando da pasta principal, os seis lugares dão o mesmo caminho de antes (a pasta de cima do código), que é
    a pasta das ferramentas ao lado dela."""
    lido = _rodar_de_dentro(projeto["principal"], LER_OS_SEIS_LUGARES)
    for nome, valor in lido.items():
        if nome.startswith(("empacotar.", "ocr_kraken.", "montar", "compilar")):
            assert _mesma(valor, projeto["principal"].parent / "EditorImpressao-arquivos" / "ferramentas"), (nome, valor)
    assert _mesma(lido["motor do empacotar"], projeto["motor"]), lido


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_defeito1_a_pasta_principal_vem_do_git_de_verdade(projeto):
    """A peça única do git diz a pasta principal: da cópia de trabalho, a principal; da principal, ela mesma (com espaço
    no nome). E a regra única diz a pasta das ferramentas ao lado dela."""
    assert _mesma(git.pasta_principal(projeto["copia"]), projeto["principal"])
    assert _mesma(git.pasta_principal(projeto["principal"]), projeto["principal"])
    assert _mesma(pf.pasta_das_ferramentas(projeto["copia"]), projeto["ferramentas"])
    assert pf.problema_para_gravar(projeto["copia"]) is None


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_falha_sem_git_vale_a_conta_de_antes(tmp_path, monkeypatch):
    """Sem git (o git não está no caminho do Windows): a peça do git levanta "não está instalado", e a pasta do próprio
    código faz o papel da principal (a conta de antes). Nada é criado."""
    codigo = tmp_path / "sem git" / "codigo"
    codigo.mkdir(parents=True)
    monkeypatch.setenv("PATH", str(Path(sys.executable).parent))
    with pytest.raises(git.GitFalhou, match="não está instalado"):
        git.pasta_principal(codigo)
    assert _mesma(pf.pasta_principal(codigo), codigo)
    assert _mesma(pf.pasta_das_ferramentas(codigo), codigo.parent / "EditorImpressao-arquivos" / "ferramentas")
    assert "nada foi criado" in pf.problema_para_gravar(codigo)
    assert _pastas(tmp_path / "sem git") == {"codigo"}


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_falha_copia_sem_repositorio_git_archive(tmp_path, monkeypatch):
    """Uma cópia feita com `git archive` (sem `.git`), como as das provas de reversão: o git de verdade diz "not a git
    repository", e vale a pasta do próprio código. A pasta das ferramentas ao lado dela não existe: quem grava ouve a
    frase, e nada é criado. O git não pode subir além da pasta do teste (GIT_CEILING_DIRECTORIES, documentação do git):
    no Windows do GitHub a pasta temporária fica dentro do repositório baixado, e o git acharia ele (rodada 44857903442;
    família F4 do catálogo: o teste supunha a pasta temporária do PC)."""
    codigo = tmp_path / "copia sem git" / "codigo"
    codigo.mkdir(parents=True)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    with pytest.raises(git.GitFalhou):
        git.pasta_principal(codigo)
    assert _mesma(pf.pasta_principal(codigo), codigo)
    frase = pf.problema_para_gravar(codigo)
    assert frase and "não existe a pasta das ferramentas" in frase and "nada foi criado" in frase, frase
    assert _pastas(tmp_path / "copia sem git") == {"codigo"}


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_falha_o_git_que_da_erro_e_o_que_demora(tmp_path, monkeypatch):
    """O git que dá erro (um `.git` que aponta para um lugar que não existe) e o que demora (o limite de tempo, com o git
    de verdade, fechado ao passar dele): os dois viram `GitFalhou`; nada é criado.

    Volta 10 (achado 1 do relatório 8 de quem tentou quebrar, 21/11/2026): as duas pastas têm o `.git` em arquivo (são
    cópias de trabalho), e a pasta do próprio código ali é a conta errada do defeito 1. Antes estas duas linhas cobravam
    "vale a pasta do próprio código" (o defeito); agora cobram que a regra para com a frase (`SemPastaPrincipal`). O
    limite passou a ser o da peça do git (observação 8): o git que demora é o de verdade, com o limite apertado nela."""
    estragado = tmp_path / "git estragado"
    estragado.mkdir()
    (estragado / ".git").write_text("gitdir: X:/nao/existe/.git/worktrees/x\n", encoding="utf-8")
    with pytest.raises(git.GitFalhou):
        git.pasta_principal(estragado)
    with pytest.raises(getattr(pf, "SemPastaPrincipal", _NuncaLevantada), match="não sei onde fica"):
        pf.pasta_principal(estragado)
    r = RepositorioDeProva.novo(tmp_path / "git que demora")
    r.escrever("a.txt", "a")
    r.commit("a")
    copia = r.criar_copia_de_trabalho(tmp_path / "git que demora" / "a copia", "copia-lenta")
    assert _mesma(pf.pasta_principal(copia), r.raiz), "sem limite apertado, a principal"
    with pytest.raises(git.GitFalhou, match="não respondeu"):
        git.pasta_principal(copia, limite_s=0.000001)
    monkeypatch.setattr(git, "pasta_principal", functools.partial(git.pasta_principal, limite_s=0.000001))
    with pytest.raises(getattr(pf, "SemPastaPrincipal", _NuncaLevantada), match="não respondeu"):
        pf.pasta_principal(copia)


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_falha_as_variaveis_do_gancho_do_commit_nao_mudam_a_resposta(projeto, tmp_path, monkeypatch):
    """Dentro do gancho do commit, o git põe GIT_DIR e GIT_INDEX_FILE no ambiente, apontando para o repositório que está
    fazendo o commit. A pergunta "onde está este código" não pode herdá-las: com elas apontando para outro repositório,
    a pasta principal da cópia continua sendo a dela."""
    outro = RepositorioDeProva.novo(tmp_path / "outro repositorio")
    monkeypatch.setenv("GIT_DIR", str(outro.raiz / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(outro.raiz / ".git" / "index"))
    assert _mesma(git.pasta_principal(projeto["copia"]), projeto["principal"])


def test_falha_a_pasta_principal_sem_a_pasta_do_samuel_ao_lado_nao_cria_nada(projeto):
    """A pasta principal sem `EditorImpressao-arquivos` ao lado (o Windows do GitHub, um PC novo): a montagem do Visual
    C++ (`empacotar.preparar_vc_redist`, que o publicar chama) para com a frase e não cria pasta nenhuma nem baixa nada
    (antes criava a pasta inteira onde a conta mandasse: foi assim que nasceu a pasta errada de 19/11). Da cópia de
    trabalho de verdade. Rodado em 5c22a12d: a pasta errada de dentro de `.claude\\worktrees` é usada."""
    shutil.rmtree(projeto["ferramentas"].parent)
    antes = _pastas(projeto["base"])
    lido = _rodar_de_dentro(projeto["copia"], "import json, empacotar\n"
                                              "a, v, p = empacotar.preparar_vc_redist(baixar=True)\n"
                                              "print(json.dumps({'arquivo': str(a) if a else None, 'problemas': p}))")
    assert lido["arquivo"] is None, lido
    assert any("não existe a pasta das ferramentas" in p and "nada foi criado" in p for p in lido["problemas"]), lido
    depois = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
    assert depois == {p for p in antes if "__pycache__" not in p}, depois - antes


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_d788_o_programa_empacotado_acha_o_motor_ao_lado_dele_e_nunca_pergunta_ao_git(tmp_path, monkeypatch):
    """D-605 e D-788 ("1"): o programa do Kaique (empacotado) procura o motor primeiro ao lado do programa, como hoje, e
    acha o motor que está lá; não tem pasta das ferramentas e não pergunta nada ao git (a peça do git, trocada aqui por
    uma que acusa se for chamada, não é chamada)."""
    programa = tmp_path / "Program Files" / "EditorImpressaoPrograma" / "current"
    motor = programa / ocr_kraken.NOME_DA_PASTA
    (motor / "python").mkdir(parents=True)
    (motor / "python" / "python.exe").write_bytes(b"MZ")
    (motor / ocr_kraken.NOME_DO_SERVIDOR).write_text("x", encoding="utf-8")

    def nao_pode(*argumentos, **k):
        """O programa empacotado nunca pergunta ao git."""
        raise AssertionError(f"o programa empacotado perguntou ao git: {argumentos}")

    monkeypatch.setattr(git, "_rodar", nao_pode)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(programa / "EditorImpressao.exe"))
    assert pf.pasta_das_ferramentas() is None
    lugares = ocr_kraken.lugares_do_motor()
    assert _mesma(lugares[0], motor), lugares
    assert _mesma(ocr_kraken.achar_pasta_do_motor(), motor)
    assert not any(pf.NOME_DA_PASTA_DO_SAMUEL in str(l) for l in lugares), lugares


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_o_git_e_aberto_sem_janela_de_console(monkeypatch, tmp_path):
    """A peça do git abre o git sem janela de console (a bandeira do Windows que a peça do Windows também usa): sem
    ela, perguntar a pasta principal de dentro da janela do programa, rodando pelas fontes, piscaria uma janela preta na
    tela do Samuel. Espia só a chamada (a lógica); a pergunta de verdade roda nos outros testes."""
    vistos = []
    rodar_de_verdade = git.subprocess.run

    def espia(*argumentos, **k):
        """Anota as bandeiras e roda de verdade."""
        vistos.append(k.get("creationflags"))
        return rodar_de_verdade(*argumentos, **k)

    monkeypatch.setattr(git.subprocess, "run", espia)
    r = RepositorioDeProva.novo(tmp_path / "sem janela")
    git.pasta_principal(r.raiz)
    git.raiz_do_repositorio(r.raiz)
    assert vistos and all(v == subprocess.CREATE_NO_WINDOW for v in vistos), vistos


# ---------------------------------------------------------------------------------------------------------------------
# Volta 10 (relatório 8 de quem tentou quebrar, 21/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

# A frase da regra quando ela não sabe a pasta (o começo dela, em core/pasta_das_ferramentas.SemPastaPrincipal).
FRASE_NAO_SEI = "não sei onde fica a pasta das ferramentas"

# Os seis lugares, cada um num Python à parte (o primeiro que parar não pode esconder os outros). Os quatro scripts
# guardam a pasta ao carregar: param ao importar. O Kraken (o programa pelas fontes) recebe a falha da regra e fica
# "indisponível" com a frase. "Pode gravar?" devolve a frase.
IMPORTAR_OS_SCRIPTS = ("empacotar", "montar_motor_kraken", "compilar_detector_gravura", "compilar_st_ferramentas")
LER_O_KRAKEN = r"""
import json
from core import ocr_kraken, pasta_das_ferramentas as pf
Erro = getattr(pf, "SemPastaPrincipal", None) or type("NuncaLevantada", (Exception,), {})
try:
    lugares = "devolveu: " + ", ".join(str(p) for p in ocr_kraken.lugares_do_motor())
except Erro as erro:
    lugares = "parou: " + str(erro)
_, _, falha = ocr_kraken.MotorKraken()._comando()
print(json.dumps({"lugares": lugares,
                  "kraken": None if falha is None else f"{falha.motivo} | {falha.detalhe_tecnico}",
                  "pode gravar": pf.problema_para_gravar()}))
"""


def _rodar_python(pasta: Path, argumentos: list[str], ambiente: dict) -> subprocess.CompletedProcess:
    """Um Python à parte (o deste computador), rodando de dentro de `pasta` com o código que está lá, sem janela, com a
    internet trancada no processo (um proxy que não existe: nada é baixado, nem se uma proteção sumir), com a saída
    em UTF-8 e sem o PYTHONPATH. Devolve o resultado inteiro (código, saída, erros)."""
    env = dict(ambiente)
    env.pop("PYTHONPATH", None)
    env.update(HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", NO_PROXY="",
               PYTHONUTF8="1")                  # a saida em UTF-8, como este lado le
    return subprocess.run([sys.executable, *argumentos], cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=300,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _ambiente_sem_git() -> dict:
    """O ambiente deste processo com o caminho do Windows sem nenhuma pasta que tenha o git (o git não está no caminho:
    o primeiro jeito do relatório 8)."""
    caminho = [p for p in os.environ.get("PATH", "").split(os.pathsep)
               if p and not (Path(p) / "git.exe").exists() and not (Path(p) / "git").is_file()]
    return dict(os.environ, PATH=os.pathsep.join(caminho))


def _ambiente_dono_diferente(tmp_path: Path) -> dict:
    """O git de verdade recusando a pasta por ser de outro dono (o segundo jeito do relatório 8: o HD externo levado a
    outro Windows). Lido no código do git (setup.c, ensure_valid_ownership): com GIT_TEST_ASSUME_DIFFERENT_OWNER ligado,
    só o safe.directory da configuração protegida aceita a pasta; sem a configuração global (um arquivo vazio) e sem a
    do sistema, nenhum safe.directory da máquina muda o resultado."""
    vazia = tmp_path / "configuracao global vazia"
    vazia.write_text("", encoding="utf-8")
    return dict(os.environ, GIT_TEST_ASSUME_DIFFERENT_OWNER="1", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(vazia))


def _os_seis_param(projeto: dict, ambiente: dict, o_que_o_git_disse: str) -> None:
    """De dentro da cópia de trabalho de verdade, com o git sem responder: os seis lugares param com a frase (e o que o
    git disse), sem o rastro técnico nos scripts, sem criar pasta, e a pasta errada imitada não é usada."""
    antes = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
    for script in IMPORTAR_OS_SCRIPTS:
        r = _rodar_python(projeto["copia"], ["-c", f"import {script}; print('carregou')"], ambiente)
        saida = r.stdout + r.stderr
        assert r.returncode == 1 and "carregou" not in r.stdout, (script, r.returncode, saida[-2000:])
        assert FRASE_NAO_SEI in r.stderr and o_que_o_git_disse in r.stderr, (script, saida[-2000:])
        assert "Traceback" not in saida, (script, saida[-2000:])
        assert str(projeto["errada"]) not in saida, (script, "falou da pasta errada", saida[-2000:])
    r = _rodar_python(projeto["copia"], ["-c", LER_O_KRAKEN], ambiente)
    assert r.returncode == 0, r.stderr[-3000:]
    lido = json.loads(r.stdout.strip().splitlines()[-1])
    assert lido["lugares"].startswith("parou: ") and FRASE_NAO_SEI in lido["lugares"], lido
    assert lido["kraken"] and FRASE_NAO_SEI in lido["kraken"] and o_que_o_git_disse in lido["kraken"], lido
    assert lido["pode gravar"] and FRASE_NAO_SEI in lido["pode gravar"], lido
    depois = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
    assert depois == antes, depois - antes


def test_achado1_sem_git_no_caminho_numa_copia_de_trabalho_os_seis_lugares_param(projeto):
    """Achado 1 do relatório 8 de quem tentou quebrar (21/11/2026, médio): numa cópia de trabalho, sem o git no caminho
    do Windows, a regra voltava calada à pasta de cima do código (`.claude\\worktrees`), que no PC do Samuel é a pasta
    errada de 19/11, com o Visual C++ de lá. Agora os seis lugares param com a frase do porquê (o git não está no
    caminho) e do que fazer. Com o git de verdade, de dentro de uma cópia de trabalho de verdade. Rodado em 6fa766c4: os
    scripts carregam e apontam para `.claude\\worktrees\\EditorImpressao-arquivos`."""
    _os_seis_param(projeto, _ambiente_sem_git(), "não está no caminho do Windows")


def test_achado1_o_git_recusando_o_dono_numa_copia_de_trabalho_os_seis_lugares_param(projeto, tmp_path):
    """Achado 1 do relatório 8 (21/11/2026): o git de verdade recusando a cópia por ser de outro dono ("detected dubious
    ownership", o HD externo levado a outro Windows): os seis lugares param com a frase, que traz o que o git disse (ele
    mesmo escreve o comando do safe.directory). Rodado em 6fa766c4: carregam calados com a pasta errada."""
    _os_seis_param(projeto, _ambiente_dono_diferente(tmp_path), "dubious ownership")


def test_achado1_da_pasta_principal_sem_git_nada_muda(projeto):
    """D-605: da pasta principal (o `.git` é uma pasta), sem o git no caminho, os seis lugares continuam dando a pasta das
    ferramentas ao lado dela (a conta de antes, que lá é a certa), e o motor é achado."""
    r = _rodar_python(projeto["principal"], ["-c", LER_OS_SEIS_LUGARES], _ambiente_sem_git())
    assert r.returncode == 0, r.stderr[-3000:]
    lido = json.loads(r.stdout.strip().splitlines()[-1])
    for nome, valor in lido.items():
        if nome.startswith(("empacotar.", "ocr_kraken.", "montar", "compilar")):
            assert _mesma(valor, projeto["ferramentas"]), (nome, valor)
    assert _mesma(lido["motor do empacotar"], projeto["motor"]), lido


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_achado1_a_regra_diz_que_nao_sabe_e_a_falha_nao_fica_guardada(projeto, monkeypatch):
    """Achado 1 do relatório 8 (21/11/2026), na regra: da cópia de trabalho, sem git, `pasta_das_ferramentas` levanta
    `SemPastaPrincipal` (nunca devolve a pasta de cima do código); com o git de volta no caminho, a mesma pergunta acha a
    pasta certa (a falha não ficou guardada). A peça do git diz se a pasta é uma cópia (o `.git` é um arquivo) sem rodar
    o git. Rodado em 6fa766c4: devolve `.claude\\worktrees\\EditorImpressao-arquivos\\ferramentas`."""
    assert getattr(git, "e_copia_de_trabalho", lambda p: None)(projeto["copia"]) is True
    assert git.e_copia_de_trabalho(projeto["principal"]) is False
    assert git.e_copia_de_trabalho(projeto["base"]) is False
    caminho_de_antes = os.environ["PATH"]
    monkeypatch.setenv("PATH", _ambiente_sem_git()["PATH"])
    with pytest.raises(getattr(pf, "SemPastaPrincipal", _NuncaLevantada), match=FRASE_NAO_SEI):
        pf.pasta_das_ferramentas(projeto["copia"])
    assert FRASE_NAO_SEI in (pf.problema_para_gravar(projeto["copia"]) or "")
    monkeypatch.setenv("PATH", caminho_de_antes)
    assert _mesma(pf.pasta_das_ferramentas(projeto["copia"]), projeto["ferramentas"])


def test_b1_b3_os_tres_scripts_que_gravam_param_sem_a_pasta_das_ferramentas(projeto):
    """Achado 3 do relatório 8 (21/11/2026), mutações B1 a B3: o `montar_motor_kraken`, o `compilar_detector_gravura` e o
    `compilar_st_ferramentas`, rodados com o padrão de dentro de uma cópia de trabalho cuja pasta principal não tem a
    pasta das ferramentas ao lado, param com a frase (código 1) e não criam pasta nenhuma (eram os lugares que criaram a
    pasta errada de 19/11). A internet fica trancada no processo: sem a proteção, nada é baixado."""
    shutil.rmtree(projeto["ferramentas"].parent)
    antes = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
    for script in ("montar_motor_kraken.py", "compilar_detector_gravura.py", "compilar_st_ferramentas.py"):
        r = _rodar_python(projeto["copia"], [script], dict(os.environ))
        saida = r.stdout + r.stderr
        assert r.returncode == 1, (script, r.returncode, saida[-2000:])
        assert "não existe a pasta das ferramentas" in saida and "nada foi criado" in saida, (script, saida[-2000:])
        depois = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
        assert depois == antes, (script, depois - antes)


def test_b4_o_montar_do_motor_para_se_um_dos_dois_lugares_e_o_de_fabrica(projeto, tmp_path):
    """Achado 3 do relatório 8 (21/11/2026), mutação B4: o `montar_motor_kraken` confere a pasta das ferramentas quando o
    destino OU a pasta dos downloads é o de fábrica (os dois moram nela). Com só o `--destino` passado, os downloads iriam
    para a pasta das ferramentas que não existe; com só o `--downloads`, o motor iria para lá: os dois param."""
    shutil.rmtree(projeto["ferramentas"].parent)
    antes = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
    for argumentos in (["--destino", str(tmp_path / "outro destino" / "motor")],
                       ["--downloads", str(tmp_path / "outros downloads")]):
        r = _rodar_python(projeto["copia"], ["montar_motor_kraken.py", *argumentos], dict(os.environ))
        saida = r.stdout + r.stderr
        assert r.returncode == 1 and "não existe a pasta das ferramentas" in saida, (argumentos, saida[-2000:])
        assert not (tmp_path / "outro destino").exists() and not (tmp_path / "outros downloads").exists(), argumentos
        depois = {p for p in _pastas(projeto["base"]) if "__pycache__" not in p}
        assert depois == antes, (argumentos, depois - antes)


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_b5_pode_gravar_olha_a_pasta_das_ferramentas_e_nao_a_de_cima(projeto):
    """Achado 3 do relatório 8 (21/11/2026), mutação B5: `EditorImpressao-arquivos` existe ao lado da pasta principal, mas
    sem a `ferramentas` dentro: "pode gravar?" diz que não (a pasta das ferramentas não existe), da cópia e da principal."""
    shutil.rmtree(projeto["ferramentas"])
    assert projeto["ferramentas"].parent.is_dir()
    for codigo in (projeto["copia"], projeto["principal"]):
        frase = pf.problema_para_gravar(codigo)
        assert frase and "não existe a pasta das ferramentas" in frase, (codigo, frase)


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_obs8_esta_empacotado_e_o_limite_do_git_moram_num_lugar_so(projeto, tmp_path, monkeypatch):
    """Observação 8 do relatório 8 (21/11/2026): "está empacotado?" e o limite de tempo do git estavam escritos em dois
    lugares. Agora o Kraken pergunta à regra (`pasta_das_ferramentas.empacotado`): com ela dizendo "empacotado", o
    primeiro lugar do motor é ao lado do programa, e a pasta das ferramentas não entra. E a regra pergunta ao git com o
    limite da peça do git (não passa um seu). Rodado em 6fa766c4: o Kraken olha o `sys.frozen` por conta própria, e a
    regra passa o próprio limite."""
    programa = tmp_path / "programa"
    monkeypatch.setattr(pf, "empacotado", lambda: True)
    monkeypatch.setattr(sys, "executable", str(programa / "EditorImpressao.exe"))
    lugares = ocr_kraken.lugares_do_motor()
    assert _mesma(lugares[0], programa / ocr_kraken.NOME_DA_PASTA), lugares
    assert not any(pf.NOME_DA_PASTA_DO_SAMUEL in str(l) for l in lugares), lugares
    monkeypatch.undo()
    pedidos = []
    de_verdade = git.pasta_principal

    def espia(pasta, **k):
        """Anota o que a regra pede e pergunta ao git de verdade."""
        pedidos.append(k)
        return de_verdade(pasta, **k)

    monkeypatch.setattr(git, "pasta_principal", espia)
    assert _mesma(pf.pasta_das_ferramentas(projeto["copia"]), projeto["ferramentas"])
    assert pedidos == [{}], pedidos
    assert inspect.signature(de_verdade).parameters["limite_s"].default == 30
    assert not hasattr(pf, "LIMITE_DO_GIT_S")
