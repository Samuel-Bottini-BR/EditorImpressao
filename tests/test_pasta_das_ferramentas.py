"""Testes da pasta das ferramentas do Samuel (core/pasta_das_ferramentas.py): o defeito 1 da prova à vista de 20/11/2026.

O DEFEITO (prova 6b; registro em C:\\EditorImpressaoProva\\prova6b.log)
    Seguida ao pé da letra a frase do próprio publicar (`publicar_versao_kaique.py --motor --pasta "..."`), rodada da
    cópia de trabalho `.claude\\worktrees\\passo2`, parou em "não achei um motor pronto do jeito novo", porque o motor
    foi procurado em `.claude\\worktrees\\EditorImpressao-arquivos\\ferramentas\\motor-kraken`, e não em
    `D:\\programas\\EditorImpressao-arquivos\\ferramentas\\motor-kraken`. A causa: seis lugares calculavam a pasta
    cada um por conta própria, a partir da pasta do código. A volta 9 passou a perguntar ao git; o relatório 8 de quem
    tentou quebrar mostrou que, sem resposta do git, a conta voltava calada à pasta errada.

O CONSERTO QUE VALE (D-820, Samuel, 21/11/2026: "não era melhor só ver se está instaldo no pc?" · "A")
    A pasta das ferramentas é um caminho escrito num lugar só (`core/pasta_das_ferramentas.PASTA_DAS_FERRAMENTAS`),
    sem perguntar ao git e sem depender de onde o código está. Os testes da volta 9 que provavam o jeito do git saíram
    (eram desta mesma tarefa, ainda não juntada; ordem da gerente, pela D-820): test_defeito1_a_pasta_principal_vem_do_git_de_verdade,
    test_falha_sem_git_vale_a_conta_de_antes, test_falha_copia_sem_repositorio_git_archive,
    test_falha_o_git_que_da_erro_e_o_que_demora e test_falha_as_variaveis_do_gancho_do_commit_nao_mudam_a_resposta.
    Dois mudaram de nome e passaram a cobrar a pasta escrita: test_defeito1_da_pasta_principal_nada_muda (agora
    test_d820_da_pasta_principal_os_seis_lugares_dao_a_mesma_pasta) e
    test_falha_a_pasta_principal_sem_a_pasta_do_samuel_ao_lado_nao_cria_nada (agora
    test_falha_sem_a_pasta_das_ferramentas_a_montagem_para_e_nao_cria_nada).

O QUE ESTES TESTES PROVAM (D-767: com o git de verdade, sem peça de mentira onde importa)
    Um repositório de prova de verdade (`regras_dos_agentes.repositorio_de_prova`), numa pasta com espaço no nome, com o
    código deste ramo copiado nele, e uma cópia de trabalho de verdade dele (`git worktree add`, em
    `.claude\\worktrees\\<nome>`, como no PC do Samuel), com a pasta errada de 19/11 imitada. O caminho da pasta das
    ferramentas é trocado NUM LUGAR SÓ: a linha de `PASTA_DAS_FERRAMENTAS` na cópia do código (no Windows do GitHub o D:
    é outro), para uma pasta de prova que fica de propósito LONGE do código (assim nada que dependa de onde o código
    está acerta por acaso). Um Python à parte roda de dentro da cópia e da pasta principal e diz onde cada um dos seis
    lugares procura.

Seguro mexer: acrescentar casos. Arriscado: trocar o repositório de prova por caminhos inventados (deixa de provar);
trocar o caminho em mais de um lugar.
"""

from __future__ import annotations

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

# A linha do caminho, como está em core/pasta_das_ferramentas.py (D-820). É a que a cópia do código troca.
LINHA_DO_CAMINHO = 'PASTA_DAS_FERRAMENTAS = Path(r"D:\\programas\\EditorImpressao-arquivos\\ferramentas")'

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
    "erros do empacotar": erros,
    "motor do programa": str(ocr_kraken.achar_pasta_do_motor() or ""),
}))
"""


def _copiar_o_codigo(destino: Path, ferramentas: Path) -> None:
    """O código deste ramo (o que roda: os .py da raiz, core/, regras_dos_agentes/ e as fontes do motor) no repositório
    de prova, com o caminho da pasta das ferramentas trocado na linha dele (o lugar único) para `ferramentas`. Só copia;
    nada do projeto é mexido. No código de antes da volta 10 (a prova de reversão) a linha não existe e nada é trocado:
    lá a pasta era calculada, e os testes mostram onde ela caía."""
    for arquivo in RAIZ.glob("*.py"):
        shutil.copy2(arquivo, destino / arquivo.name)
    for pasta in ("core", "regras_dos_agentes", "motor_kraken"):
        for arquivo in (RAIZ / pasta).rglob("*"):
            if arquivo.is_file() and "__pycache__" not in arquivo.parts and arquivo.suffix in (".py", ".txt"):
                alvo = destino / arquivo.relative_to(RAIZ)
                alvo.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(arquivo, alvo)
    regra = destino / "core" / "pasta_das_ferramentas.py"
    if regra.is_file():
        texto = regra.read_text(encoding="utf-8")
        if texto.count(LINHA_DO_CAMINHO) == 1:
            regra.write_text(texto.replace(LINHA_DO_CAMINHO, f"PASTA_DAS_FERRAMENTAS = Path({str(ferramentas)!r})"),
                             encoding="utf-8")


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
    """Todas as pastas que existem dentro de `base`, sem as do git e as do Python (para conferir que nada novo foi
    criado)."""
    return {str(p.relative_to(base)) for p in base.rglob("*")
            if p.is_dir() and ".git" not in p.parts and "__pycache__" not in p.parts}


@pytest.fixture
def projeto(tmp_path):
    """O PC do Samuel em miniatura, numa pasta com espaço no nome: a pasta principal (um repositório de verdade, com o
    código deste ramo), a pasta das ferramentas LONGE dela (com um motor e um Visual C++ de prova), uma cópia de
    trabalho em `.claude\\worktrees\\minha copia`, a pasta errada de 19/11 imitada em `.claude\\worktrees` e a que o
    jeito do git (voltas 9 e 10) acharia, ao lado da pasta principal, também imitada."""
    base = tmp_path / "programas do samuel"
    ferramentas = tmp_path / "outro disco" / "EditorImpressao-arquivos" / "ferramentas"
    r = RepositorioDeProva.novo(base)                       # base\copia (a principal) e base\github (o remoto)
    _copiar_o_codigo(r.raiz, ferramentas)
    r.commit("o codigo do ramo")
    motor = _motor_de_prova(ferramentas / "motor-kraken")
    (ferramentas / "downloads").mkdir()
    (ferramentas / "downloads" / "vc_redist.x64.exe").write_bytes(b"MZ o certo")
    errada = r.raiz / ".claude" / "worktrees" / "EditorImpressao-arquivos" / "ferramentas" / "downloads"
    errada.mkdir(parents=True)
    (errada / "vc_redist.x64.exe").write_bytes(b"MZ o do lugar errado")
    do_git = base / "EditorImpressao-arquivos" / "ferramentas" / "downloads"
    do_git.mkdir(parents=True)
    (do_git / "vc_redist.x64.exe").write_bytes(b"MZ o que o jeito do git acharia")
    copia = r.criar_copia_de_trabalho(r.raiz / ".claude" / "worktrees" / "minha copia", "copia-de-prova")
    return {"base": base, "principal": r.raiz, "copia": copia, "ferramentas": ferramentas, "motor": motor,
            "errada": errada.parent, "outro disco": tmp_path / "outro disco"}


def _rodar_python(pasta: Path, argumentos: list[str], ambiente: dict | None = None) -> subprocess.CompletedProcess:
    """Um Python à parte (o deste computador), rodando de dentro de `pasta` com o código que está lá, sem janela, com a
    internet trancada no processo (um proxy que não existe: nada é baixado, nem se uma proteção sumir), com a saída
    em UTF-8 e sem o PYTHONPATH. Devolve o resultado inteiro (código, saída, erros)."""
    env = dict(ambiente or os.environ)
    env.pop("PYTHONPATH", None)
    env.update(HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", NO_PROXY="",
               PYTHONUTF8="1")                  # a saída em UTF-8, como este lado lê
    return subprocess.run([sys.executable, *argumentos], cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=300,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _ler_os_seis(pasta: Path, ambiente: dict | None = None) -> dict:
    """Os seis lugares e o motor achado, lidos por um Python à parte de dentro de `pasta`."""
    r = _rodar_python(pasta, ["-c", LER_OS_SEIS_LUGARES], ambiente)
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def _ambiente_sem_git() -> dict:
    """O ambiente deste processo com o caminho do Windows sem nenhuma pasta que tenha o git (o git não está no
    caminho: o primeiro jeito do relatório 8)."""
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


def _mesma(a, b) -> bool:
    """O mesmo lugar no disco (o Windows não liga para maiúsculas)."""
    return a is not None and os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def _os_seis_na_pasta_certa(lido: dict, projeto: dict) -> None:
    """Os seis lugares apontam para a pasta das ferramentas de prova, e os dois motores achados são o dela."""
    errados = {k: v for k, v in lido.items() if k.startswith(("empacotar.", "ocr_kraken.", "montar", "compilar"))
               and not _mesma(v, projeto["ferramentas"])}
    assert errados == {}, f"procuram fora de {projeto['ferramentas']}: {errados}"
    assert _mesma(lido["motor do empacotar"], projeto["motor"]), lido
    assert _mesma(lido["motor do programa"], projeto["motor"]), lido


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_d820_a_pasta_das_ferramentas_esta_escrita_num_lugar_so():
    """D-820 ("A"): a pasta das ferramentas é `D:\\programas\\EditorImpressao-arquivos\\ferramentas`, escrita num lugar
    só (`PASTA_DAS_FERRAMENTAS`, a linha que os testes trocam); é ela que a regra devolve (sem estar empacotado), sem
    perguntar ao git (a peça do git, trocada aqui por uma que acusa se for chamada, não é chamada). Rodado em 6fa766c4:
    a linha não existe, e a regra pergunta ao git."""
    assert getattr(pf, "PASTA_DAS_FERRAMENTAS", None) == Path(r"D:\programas\EditorImpressao-arquivos\ferramentas")
    texto = (RAIZ / "core" / "pasta_das_ferramentas.py").read_text(encoding="utf-8")
    assert texto.count(LINHA_DO_CAMINHO) == 1, "a linha do caminho mudou: troque também LINHA_DO_CAMINHO neste teste"

    def nao_pode(*argumentos, **k):
        """A regra não pergunta ao git (D-820)."""
        raise AssertionError(f"a regra da pasta das ferramentas perguntou ao git: {argumentos}")

    original = git._rodar
    git._rodar = nao_pode
    try:
        assert pf.pasta_das_ferramentas() == pf.PASTA_DAS_FERRAMENTAS
    finally:
        git._rodar = original


def test_defeito1_de_uma_copia_de_trabalho_os_seis_lugares_acham_a_pasta_certa(projeto):
    """O defeito 1 da prova à vista de 20/11/2026 (prova 6b): rodando de uma cópia de trabalho de verdade, os seis lugares
    (`empacotar.DOWNLOADS`, `empacotar.LUGARES_DO_MOTOR`, `core/ocr_kraken.lugares_do_motor`,
    `montar_motor_kraken.PASTA_FERRAMENTAS`, `compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO` e
    `compilar_st_ferramentas.pasta_de_ferramentas_padrao`) procuram na pasta das ferramentas (D-820: a escrita num lugar
    só), e não na pasta errada de 19/11; o motor que o publicar --motor e o programa acham é o de lá. Numa pasta com
    espaço no nome, longe do código. Nada é criado."""
    antes = _pastas(projeto["base"])
    _os_seis_na_pasta_certa(_ler_os_seis(projeto["copia"]), projeto)
    assert _pastas(projeto["base"]) == antes, "rodar de dentro da cópia criou pasta"


def test_d820_da_pasta_principal_os_seis_lugares_dao_a_mesma_pasta(projeto):
    """D-605 e D-820: rodando da pasta principal, os seis lugares dão a mesma pasta das ferramentas que da cópia."""
    _os_seis_na_pasta_certa(_ler_os_seis(projeto["principal"]), projeto)


def test_achado1_sem_git_ou_com_o_git_recusando_os_seis_lugares_dao_a_mesma_pasta(projeto, tmp_path):
    """Achado 1 do relatório 8 de quem tentou quebrar (21/11/2026, médio): numa cópia de trabalho, sem o git no caminho
    do Windows ou com o git de verdade recusando a pasta por ser de outro dono ("detected dubious ownership", o HD
    levado a outro Windows), a regra da volta 9 voltava calada à pasta de cima do código, a pasta errada de 19/11, com o
    Visual C++ de lá. Com a pasta escrita num lugar só (D-820), o git não entra: da cópia e da pasta principal, os seis
    lugares dão a mesma pasta e acham o mesmo motor. Rodado em 6fa766c4: da cópia, sem git, apontam para
    `.claude\\worktrees\\EditorImpressao-arquivos`."""
    for ambiente in (_ambiente_sem_git(), _ambiente_dono_diferente(tmp_path)):
        for pasta in (projeto["copia"], projeto["principal"]):
            _os_seis_na_pasta_certa(_ler_os_seis(pasta, ambiente), projeto)


def test_falha_sem_a_pasta_das_ferramentas_a_montagem_para_e_nao_cria_nada(projeto):
    """Sem a pasta das ferramentas (o Windows do GitHub, um PC novo): a montagem do Visual C++
    (`empacotar.preparar_vc_redist`, que o publicar chama) para com a frase e não cria pasta nenhuma nem baixa nada
    (antes criava a pasta inteira onde a conta mandasse: foi assim que nasceu a pasta errada de 19/11). Da cópia de
    trabalho de verdade."""
    shutil.rmtree(projeto["outro disco"])
    antes = _pastas(projeto["base"])
    r = _rodar_python(projeto["copia"], ["-c", "import json, empacotar\n"
                                               "a, v, p = empacotar.preparar_vc_redist(baixar=True)\n"
                                               "print(json.dumps({'arquivo': str(a) if a else None, 'problemas': p}))"])
    assert r.returncode == 0, r.stderr[-3000:]
    lido = json.loads(r.stdout.strip().splitlines()[-1])
    assert lido["arquivo"] is None, lido
    assert any("não existe a pasta das ferramentas" in p and "nada foi criado" in p
               and str(projeto["ferramentas"]) in p for p in lido["problemas"]), lido
    assert _pastas(projeto["base"]) == antes and not projeto["outro disco"].exists()


def test_d820_sem_o_motor_a_frase_diz_onde_procurou_e_como_apontar_outro(projeto):
    """D-820: sem a peça (o motor) na pasta das ferramentas, a busca única do motor (`empacotar.achar_motor_kraken`, que
    o empacotar e o `publicar --motor` usam) não acha nada, e a frase diz onde procurou (a pasta das ferramentas) e como
    apontar outro lugar (`--motor-kraken`). Nada é criado. Rodado em 6fa766c4: a frase não diz como apontar outro."""
    shutil.rmtree(projeto["motor"])
    antes = _pastas(projeto["base"]) | _pastas(projeto["outro disco"])
    lido = _ler_os_seis(projeto["copia"])
    assert lido["motor do empacotar"] is None, lido
    frase = "; ".join(lido["erros do empacotar"])
    assert str(projeto["motor"]) in frase and "--motor-kraken" in frase, frase
    assert _pastas(projeto["base"]) | _pastas(projeto["outro disco"]) == antes


def test_b1_b3_os_tres_scripts_que_gravam_param_sem_a_pasta_das_ferramentas(projeto):
    """Achado 3 do relatório 8 (21/11/2026), mutações B1 a B3: o `montar_motor_kraken`, o `compilar_detector_gravura` e o
    `compilar_st_ferramentas`, rodados com o padrão de dentro de uma cópia de trabalho, sem a pasta das ferramentas,
    param com a frase (código 1) e não criam pasta nenhuma (eram os lugares que criaram a pasta errada de 19/11). A
    internet fica trancada no processo: sem a proteção, nada é baixado."""
    shutil.rmtree(projeto["outro disco"])
    antes = _pastas(projeto["base"])
    for script in ("montar_motor_kraken.py", "compilar_detector_gravura.py", "compilar_st_ferramentas.py"):
        r = _rodar_python(projeto["copia"], [script])
        saida = r.stdout + r.stderr
        assert r.returncode == 1, (script, r.returncode, saida[-2000:])
        assert "não existe a pasta das ferramentas" in saida and "nada foi criado" in saida, (script, saida[-2000:])
        assert _pastas(projeto["base"]) == antes and not projeto["outro disco"].exists(), script


def test_b4_o_montar_do_motor_para_se_um_dos_dois_lugares_e_o_de_fabrica(projeto, tmp_path):
    """Achado 3 do relatório 8 (21/11/2026), mutação B4: o `montar_motor_kraken` confere a pasta das ferramentas quando o
    destino OU a pasta dos downloads é o de fábrica (os dois moram nela). Com só o `--destino` passado, os downloads iriam
    para a pasta das ferramentas que não existe; com só o `--downloads`, o motor iria para lá: os dois param."""
    shutil.rmtree(projeto["outro disco"])
    antes = _pastas(projeto["base"])
    for argumentos in (["--destino", str(tmp_path / "outro destino" / "motor")],
                       ["--downloads", str(tmp_path / "outros downloads")]):
        r = _rodar_python(projeto["copia"], ["montar_motor_kraken.py", *argumentos])
        saida = r.stdout + r.stderr
        assert r.returncode == 1 and "não existe a pasta das ferramentas" in saida, (argumentos, saida[-2000:])
        assert not (tmp_path / "outro destino").exists() and not (tmp_path / "outros downloads").exists(), argumentos
        assert _pastas(projeto["base"]) == antes and not projeto["outro disco"].exists(), argumentos


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_b5_pode_gravar_olha_a_pasta_das_ferramentas_e_nao_a_de_cima(tmp_path, monkeypatch):
    """Achado 3 do relatório 8 (21/11/2026), mutação B5: `EditorImpressao-arquivos` existe, mas sem a `ferramentas`
    dentro: "pode gravar?" diz que não (a pasta das ferramentas não existe), e com ela existindo diz que pode. O caminho
    é trocado no lugar único (`PASTA_DAS_FERRAMENTAS`)."""
    ferramentas = tmp_path / "EditorImpressao-arquivos" / "ferramentas"
    ferramentas.parent.mkdir()
    monkeypatch.setattr(pf, "PASTA_DAS_FERRAMENTAS", ferramentas)
    frase = pf.problema_para_gravar()
    assert frase and "não existe a pasta das ferramentas" in frase and str(ferramentas) in frase, frase
    assert not ferramentas.exists(), "o pode gravar criou a pasta"
    ferramentas.mkdir()
    assert pf.problema_para_gravar() is None


@pytest.mark.skipif(pf is None, reason="core/pasta_das_ferramentas.py ainda não existe neste código")
def test_d788_o_programa_empacotado_acha_o_motor_ao_lado_dele_e_nunca_pergunta_ao_git(tmp_path, monkeypatch):
    """D-605 e D-788 ("1"): o programa do Kaique (empacotado) procura o motor primeiro ao lado do programa, como hoje, e
    acha o motor que está lá; não tem pasta das ferramentas (não a olha) e não pergunta nada ao git (a peça do git,
    trocada aqui por uma que acusa se for chamada, não é chamada)."""
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
def test_obs8_esta_empacotado_mora_num_lugar_so(tmp_path, monkeypatch):
    """Observação 8 do relatório 8 (21/11/2026): "está empacotado?" estava escrito em dois lugares. Agora o Kraken
    pergunta à regra (`pasta_das_ferramentas.empacotado`): com ela dizendo "empacotado", o primeiro lugar do motor é ao
    lado do programa, e a pasta das ferramentas não entra. (O "30 s" escrito em dois lugares saiu junto com a pergunta ao
    git, D-820.) Rodado em 6fa766c4: o Kraken olha o `sys.frozen` por conta própria."""
    programa = tmp_path / "programa"
    monkeypatch.setattr(pf, "empacotado", lambda: True)
    monkeypatch.setattr(sys, "executable", str(programa / "EditorImpressao.exe"))
    lugares = ocr_kraken.lugares_do_motor()
    assert _mesma(lugares[0], programa / ocr_kraken.NOME_DA_PASTA), lugares
    assert not any(pf.NOME_DA_PASTA_DO_SAMUEL in str(l) for l in lugares), lugares


def test_o_git_e_aberto_sem_janela_de_console(monkeypatch, tmp_path):
    """A peça do git abre o git sem janela de console (a bandeira do Windows que a peça do Windows também usa): sem
    ela, um git aberto por um programa sem console piscaria uma janela preta na tela do Samuel. Espia só a chamada (a
    lógica); a pergunta de verdade roda nos outros testes. (Volta 9; na volta 10 a pergunta da pasta principal saiu, e a
    espia usa outras duas funções da peça.)"""
    vistos = []
    rodar_de_verdade = git.subprocess.run

    def espia(*argumentos, **k):
        """Anota as bandeiras e roda de verdade."""
        vistos.append(k.get("creationflags"))
        return rodar_de_verdade(*argumentos, **k)

    monkeypatch.setattr(git.subprocess, "run", espia)
    r = RepositorioDeProva.novo(tmp_path / "sem janela")
    git.raiz_do_repositorio(r.raiz)
    git.arquivos_do_git(r.raiz)
    assert vistos and all(v == subprocess.CREATE_NO_WINDOW for v in vistos), vistos
