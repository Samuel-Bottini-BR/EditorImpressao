"""Provas da volta 4 do atualizador (D-828, Samuel 22/11/2026: "foi eu, pode consertar essas coisas").

Os 3 defeitos da prova a vista de 22/11 (Lista de bugs de 22/11), um por conserto:
1. "Reiniciar agora" nao troca: o Velopack nao conseguiu renomear `current` ("O arquivo ja esta sendo usado por outro
   processo"), porque o PowerShell da troca nasceu com `current` como pasta de trabalho; e abrir o programa pelo atalho
   no meio da troca a estragava.
2. A pergunta do Windows da primeira abertura piscava na barra de tarefas (a janela do programa nao estava na frente).
3. A segunda preparacao falhava com a pasta dos testes a distancia trancada pelo `icacls ... /T`.

Plano, causas e experimentos: relatorios/atualizador-4/ONDE-PAREI.md (secao "Volta 4") e anexos/volta4-*.
Cada teste diz o defeito que pega e falha no codigo de antes do seu conserto (a prova de reversao fica nos anexos).

O QUE TOCA O WINDOWS DE VERDADE (D-767): so o que nao pede licenca nem abre janela: lancar um PowerShell escondido pela
peca, renomear uma pasta do teste, criar e ler uma marca (mutex) com nome proprio do teste, ler a lista de processos.
Nada pergunta "Deseja permitir...?" e nada aparece na tela.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

import atualizacao
from core import windows

RAIZ = Path(__file__).resolve().parent.parent
so_no_windows = pytest.mark.skipif(sys.platform != "win32", reason="so no Windows")


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (o estado, o registro e as pastas de troca da peca nascem limpos)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


def _registro() -> str:
    """O registro da atualizacao (o de mentira, desta pasta do teste)."""
    caminho = atualizacao.caminho_do_registro()
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1, parte a: o lancar solto nao prende a pasta de quem lancou
# ---------------------------------------------------------------------------------------------------------------------

_QUEM_LANCA = textwrap.dedent('''
    """Faz o papel do programa aberto pelo Velopack: a pasta de trabalho e `current`; lanca solto e sai dela."""
    import os, sys, time
    sys.path.insert(0, sys.argv[1])
    current = sys.argv[2]
    os.chdir(current)
    from core import windows
    r = windows.lancar_powershell_solto("Start-Sleep -Seconds 12")
    os.chdir(os.path.dirname(current))
    time.sleep(1.5)
    try:
        os.rename(current, current + "-velha")
        print("RENOMEOU" if r.deu_certo else "NAO LANCOU " + r.motivo)
    except OSError as erro:
        print("PRESA", erro.winerror)
''')


@so_no_windows
def test_conserto1_o_lancado_solto_nao_prende_a_pasta_de_trabalho_de_quem_lancou(tmp_path):
    """Defeito da prova a vista de 22/11 ("Reiniciar agora" ainda nao troca a versao): o PowerShell da troca nascia
    com a pasta de trabalho do programa (`current`) e o Velopack nao conseguia renomea-la (erro 32). Aqui, de verdade
    no Windows: um processo com a pasta de trabalho em `current` lanca solto pela peca e sai da pasta; a pasta tem de
    poder ser renomeada enquanto o lancado ainda roda. No codigo de antes: "PRESA 32"."""
    current = tmp_path / "current"
    current.mkdir()
    script = tmp_path / "quem_lanca.py"
    script.write_text(_QUEM_LANCA, encoding="utf-8")
    feito = subprocess.run([sys.executable, str(script), str(RAIZ), str(current)], capture_output=True, text=True,
                           timeout=90, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert feito.stdout.strip() == "RENOMEOU", (feito.stdout, feito.stderr)


def test_conserto1_o_programa_reaberto_pela_troca_nasce_na_pasta_dele():
    """Volta 4: o script da troca nasce na pasta do sistema; antes de reabrir o programa ele volta para a pasta do
    programa (o Start-Process abre na "localizacao" do PowerShell, volta4-exp3/exp4), para o programa reaberto ter a
    mesma pasta de trabalho de quando o Velopack o abre. A troca, a volta e a reabertura ficam iguais (D-742)."""
    exe = Path(r"C:\Arquivos de Programas\EditorImpressaoPrograma\current\EditorImpressao.exe")
    for janelinha in (False, True):
        script = atualizacao.script_de_trocar_e_reabrir(exe, 4321, Path("C:/x/estado.json"), janelinha=janelinha)
        linhas = script.split("\n")
        reabrir = next(i for i, linha in enumerate(linhas) if "Start-Process -FilePath" in linha)
        assert linhas[reabrir - 1] == f"Set-Location -LiteralPath '{exe.parent}'"


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1, parte b: o ajudante so troca com nada do programa rodando de `current`, conferido no Windows
# ---------------------------------------------------------------------------------------------------------------------

def _programa_de_verdade_numa_pasta(pasta: Path) -> subprocess.Popen:
    """Copia o ping.exe do Windows para `pasta` e o roda dali (uns segundos, sem janela): um processo de verdade cujo
    programa esta dentro da pasta, como o programa do Kaique em `current`."""
    pasta.mkdir(parents=True, exist_ok=True)
    copia = pasta / "EditorImpressao.exe"
    copia.write_bytes((Path(os.environ["SystemRoot"]) / "System32" / "PING.EXE").read_bytes())
    return subprocess.Popen([str(copia), "-n", "30", "127.0.0.1"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


@so_no_windows
def test_conserto1_a_peca_le_no_windows_o_que_roda_de_uma_pasta(tmp_path):
    """Volta 4 (D-828: "garante que o programa terminou de fechar antes de a troca comecar", conferido de verdade): a
    peca le na lista de processos do Windows o que roda de dentro de uma pasta, pelo caminho do programa; nada de fora
    da pasta conta; o processo que terminou sai da lista."""
    current = tmp_path / "EditorImpressaoPrograma" / "current"
    processo = _programa_de_verdade_numa_pasta(current)
    try:
        time.sleep(0.5)
        achados = windows.programas_rodando_de(current)
        assert [pid for pid, _ in achados] == [processo.pid]
        assert Path(achados[0][1]).name == "EditorImpressao.exe"
        assert windows.programas_rodando_de(tmp_path / "outra") == [], "uma pasta sem nada rodando"
    finally:
        processo.kill()
        processo.wait(10)
    assert windows.programas_rodando_de(current) == []


@pytest.fixture
def instalado_de_mentira(tmp_path, monkeypatch):
    """O programa "instalado" numa pasta do teste: a pasta do programa e <tmp>/EditorImpressaoPrograma/current; a
    marca da janela nao existe; a espera curta (o mesmo laco, menos tempo)."""
    current = tmp_path / "EditorImpressaoPrograma" / "current"
    current.mkdir(parents=True)
    monkeypatch.setattr(atualizacao, "pasta_do_programa", lambda: current)
    monkeypatch.setattr(atualizacao, "instalado_pelo_velopack", lambda: True)
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: False)
    monkeypatch.setattr(atualizacao, "ESPERA_O_PROGRAMA_FECHAR_S", 1.5, raising=False)
    return current


@so_no_windows
def test_conserto1_com_o_programa_ainda_rodando_de_current_o_ajudante_nao_troca(instalado_de_mentira, tmp_path):
    """Defeito da prova de 22/11: a troca comecou com algo ainda segurando `current`, e o Velopack desistiu (e a versao
    ficou como "ja falhou"). Agora o ajudante, antes de pedir a troca, le no Windows o que roda de `current`: com o
    programa ainda rodando (aqui um processo de verdade dali), nao troca (fica "pendente") e o registro diz o que roda.
    No codigo de antes: so a marca da janela contava, e trocava ("aplicando")."""
    from tests.test_decisoes_atualizacao import PUBLICA, GerenteFalso, _servidor

    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    processo = _programa_de_verdade_numa_pasta(instalado_de_mentira)
    try:
        time.sleep(0.5)
        resultado = atualizacao.procurar_e_preparar(gerente, fonte, atualizacao.ha_programa_aberto,
                                                    chave_publica=PUBLICA, motor_no_lugar=lambda: True)
    finally:
        processo.kill()
        processo.wait(10)
    assert resultado == "pendente" and gerente.trocou == []
    assert "ainda roda do programa (EditorImpressao.exe" in _registro()


def test_conserto1_o_que_termina_dentro_da_espera_deixa_trocar(instalado_de_mentira):
    """O programa terminando de fechar (some da lista dentro da espera): troca, sem esperar a mais; o registro diz que
    esperou."""
    vezes = iter([["EditorImpressao.exe (7)"], ["EditorImpressao.exe (7)"], []])
    assert atualizacao.ha_programa_aberto(roda=lambda: next(vezes), dormir=lambda s: None) is False
    assert "espero até" in _registro() and "terminou; pode trocar" in _registro()


@pytest.mark.parametrize("lido", [None, ["EditorImpressao.exe (7)"]])
def test_conserto1_lista_que_nao_deu_para_ler_ou_programa_que_nao_fecha_nao_troca(instalado_de_mentira, lido):
    """"Nada da como feito o que nao conferiu" (CLAUDE.md §11.12): a lista que o Windows nao deu, ou o programa que nao
    termina dentro da espera, contam como aberto."""
    assert atualizacao.ha_programa_aberto(roda=lambda: lido, dormir=lambda s: time.sleep(0.05)) is True
    assert "não troco agora" in _registro()


def test_conserto1_com_a_marca_da_janela_nao_espera_e_pelo_codigo_so_a_marca(monkeypatch):
    """A janela aberta (a marca) conta como aberto na hora, sem ler a lista; pelo codigo (nao instalado) so a marca,
    como antes."""
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: True)
    assert atualizacao.ha_programa_aberto(roda=lambda: pytest.fail("leu a lista"), instalado=lambda: True) is True
    monkeypatch.setattr(atualizacao, "_marca_existe", lambda nome: False)
    assert atualizacao.ha_programa_aberto(roda=lambda: pytest.fail("leu a lista"), instalado=lambda: False) is False


def test_conserto1_o_proprio_ajudante_nao_conta(instalado_de_mentira):
    """O ajudante roda de `current` (e ele que pede a troca e sai): ele mesmo nao entra na conta."""
    assert atualizacao.o_que_roda_do_programa(lambda pasta: [(os.getpid(), str(pasta / "EditorImpressao.exe"))]) == []
    assert atualizacao.o_que_roda_do_programa(lambda pasta: None) is None


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1, parte c: a marca da troca (abrir pelo atalho no meio da troca nao a estraga)
# ---------------------------------------------------------------------------------------------------------------------

class _Marca:
    """Uma marca (mutex com nome) de verdade, segurada por este processo do teste enquanto existe este objeto."""

    def __init__(self, nome: str) -> None:
        """Cria a marca no Windows."""
        import ctypes

        self._k = ctypes.WinDLL("kernel32", use_last_error=True)
        self._k.CreateMutexW.restype = ctypes.c_void_p
        self._k.CloseHandle.argtypes = [ctypes.c_void_p]
        self.alca = self._k.CreateMutexW(None, False, nome)
        assert self.alca, "o Windows nao criou a marca do teste"

    def soltar(self) -> None:
        """Solta a marca (ela some do Windows)."""
        if self.alca:
            self._k.CloseHandle(self.alca)
            self.alca = None


@pytest.fixture
def marcas_do_teste(monkeypatch):
    """Nomes de marca so deste teste (nunca as do programa de verdade, que podem existir neste computador)."""
    sufixo = f"{os.getpid()}-{time.monotonic_ns()}"
    monkeypatch.setattr(atualizacao, "MARCA_DA_TROCA", f"Global\\EditorImpressaoTeste-trocando-{sufixo}",
                        raising=False)
    monkeypatch.setattr(atualizacao, "MARCA_DE_REABRIR", f"Local\\EditorImpressaoTeste-reabrir-{sufixo}",
                        raising=False)
    return atualizacao


def _esperar(condicao, limite: float = 15.0) -> bool:
    """Espera `condicao()` ficar verdadeira (ate `limite` segundos)."""
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        if condicao():
            return True
        time.sleep(0.2)
    return condicao()


def _abrir_o_programa(monkeypatch, *argumentos: str):
    """A abertura comum do programa instalado (atender_linha_de_comando), com o Velopack e a troca do "Depois" de
    mentira: devolve (o codigo, o que foi lancado pela peca)."""
    lancados: list[str] = []
    monkeypatch.setattr(atualizacao, "instalado_pelo_velopack", lambda: True)
    monkeypatch.setattr(atualizacao, "_rodar_o_velopack", lambda: None)
    monkeypatch.setattr(atualizacao, "trocar_antes_de_abrir", lambda argumentos: False)
    monkeypatch.setattr(atualizacao, "_lancar_pela_peca", lancados.append)
    return atualizacao.atender_linha_de_comando(["EditorImpressao.exe", *argumentos]), lancados


@so_no_windows
def test_conserto1_abrir_pelo_atalho_no_meio_da_troca_sai_em_silencio_e_abre_no_fim(marcas_do_teste, monkeypatch):
    """Defeito da prova de 22/11 (o Samuel abriu o programa pelo atalho as 14:34:58, no meio da troca): o programa
    abria de `current` e a troca nao conseguia renomear a pasta. Agora, com a marca da troca de pe (aqui, uma marca de
    verdade no Windows), a abertura comum sai antes do brasao e da janela (codigo 0) e deixa a reabertura pronta (o
    script so de reabrir). No codigo de antes: abria (None)."""
    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.1.1", "anterior": "1.1.0"})
    marca = _Marca(atualizacao.MARCA_DA_TROCA)
    try:
        codigo, lancados = _abrir_o_programa(monkeypatch)
    finally:
        marca.soltar()
    assert codigo == 0, "abriu no meio da troca"
    assert len(lancados) == 1 and "MarcaExiste" in lancados[0] and "Wait-Process" not in lancados[0]
    assert "o programa abre sozinho quando a troca acabar" in _registro()


@so_no_windows
@pytest.mark.parametrize("fase", ["pendente", "aplicando", "falhou", "ok"])
def test_conserto1_sem_a_marca_abre_normal_e_fora_das_fases_nem_le(marcas_do_teste, monkeypatch, fase):
    """Sem a marca (nenhuma troca acontecendo), o programa abre como sempre, em qualquer fase."""
    atualizacao.gravar_estado({"fase": fase, "nova": "1.1.1", "anterior": "1.1.0"})
    codigo, lancados = _abrir_o_programa(monkeypatch)
    assert codigo is None and lancados == []


@so_no_windows
@pytest.mark.parametrize("argumento", ["--depois-da-troca", "--veloapp-obsolete", "--procurar-atualizacao"])
def test_conserto1_o_reaberto_pela_troca_os_ganchos_e_os_modos_escondidos_nao_saem(marcas_do_teste, monkeypatch,
                                                                                   argumento):
    """O programa que o proprio script reabre, os ganchos do Velopack (que rodam DENTRO da troca) e os modos
    escondidos nunca saem pela marca."""
    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.1.1", "anterior": "1.1.0"})
    monkeypatch.setattr(atualizacao, "rodar_ao_ligar", lambda fonte: 7)
    marca = _Marca(atualizacao.MARCA_DA_TROCA)
    try:
        codigo, lancados = _abrir_o_programa(monkeypatch, argumento)
    finally:
        marca.soltar()
    assert lancados == [] and codigo != 0


def test_conserto1_quem_ja_vai_reabrir_nao_ganha_outro(monkeypatch):
    """Dois cliques no atalho no meio da troca: o segundo ve a marca de reabrir e nao lanca outro script."""
    lancados: list[str] = []
    assert atualizacao.abrir_quando_a_troca_acabar(lancar=lancados.append, ha_quem_reabra=lambda: True) is True
    assert lancados == []
    assert atualizacao.abrir_quando_a_troca_acabar(lancar=lancados.append, ha_quem_reabra=lambda: False) is True
    assert len(lancados) == 1


@pytest.mark.parametrize("lida", [False, None])
def test_conserto1_a_marca_que_nao_existe_ou_nao_deu_para_ler_nao_segura_a_abertura(lida):
    """A marca que nao existe, ou que o Windows nao deixou ler, nunca impede o programa de abrir (conta como NAO)."""
    assert atualizacao.troca_em_andamento(ler=lambda: {"fase": "aplicando"}, marca_existe=lambda nome: lida) is False
    assert atualizacao.troca_em_andamento(ler=lambda: {"fase": "aplicando"}, marca_existe=lambda nome: True) is True
    assert atualizacao.troca_em_andamento(ler=lambda: {"fase": "ok"},
                                          marca_existe=lambda nome: pytest.fail("leu fora das fases")) is False


def test_conserto1_o_script_da_troca_segura_as_duas_marcas_desde_a_primeira_linha():
    """O script da troca ("Reiniciar agora" e "Depois") pega a marca da troca e a de reabrir na PRIMEIRA linha (antes
    da janelinha e de esperar o programa sair), e reabre so com $reabrir verdadeiro."""
    for janelinha in (False, True):
        script = atualizacao.script_de_trocar_e_reabrir(Path(r"C:\p\current\E.exe"), 1, Path("C:/x/e.json"),
                                                        janelinha=janelinha)
        primeira = script.split("\n")[0]
        assert f"Mutex]::new($false, '{atualizacao.MARCA_DA_TROCA}')" in primeira
        assert f"Mutex]::new($false, '{atualizacao.MARCA_DE_REABRIR}')" in primeira
        assert "$reabrir = $true" in primeira
        assert "if ($reabrir) { Start-Process" in script


@so_no_windows
def test_conserto1_o_vigia_de_verdade_segura_a_marca_ate_a_troca_acabar(marcas_do_teste, tmp_path):
    """A troca que o ajudante faz sem o script (o Kaique fechou o programa durante o download): o vigia, lancado de
    verdade pela peca, segura a marca da troca enquanto o estado diz "aplicando", e a solta quando a troca acaba. No
    codigo de antes nao havia vigia: essa troca ficava sem nada que segurasse o clique no atalho."""
    from core import windows as peca

    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.1.1", "anterior": "1.1.0"})
    atualizacao._lancar_pela_peca(atualizacao.script_do_vigia_da_troca(atualizacao.pasta_do_estado() / "estado.json"))
    try:
        assert _esperar(lambda: peca.marca_existe(atualizacao.MARCA_DA_TROCA) is True), "o vigia nao pegou a marca"
        time.sleep(3)
        assert peca.marca_existe(atualizacao.MARCA_DA_TROCA) is True, "soltou a marca no meio da troca"
    finally:
        atualizacao.gravar_estado({"fase": "ok", "nova": "1.1.1", "anterior": "1.1.0"})
    assert _esperar(lambda: peca.marca_existe(atualizacao.MARCA_DA_TROCA) is False), "nao soltou a marca no fim"


@so_no_windows
def test_conserto1_o_script_so_de_reabrir_de_verdade_espera_a_troca_acabar(marcas_do_teste, tmp_path):
    """O script so de reabrir (o clique no atalho no meio da troca do vigia), de verdade: pega a marca de reabrir,
    espera enquanto a marca da troca existe e so depois reabre e termina (a marca de reabrir some). O programa que ele
    "reabre" aqui e o pythonw sem nada para fazer (nenhuma janela)."""
    exe = Path(sys.executable).with_name("pythonw.exe")
    if not exe.is_file():
        pytest.skip("sem o pythonw.exe")
    marca = _Marca(atualizacao.MARCA_DA_TROCA)
    try:
        atualizacao._lancar_pela_peca(atualizacao.script_de_trocar_e_reabrir(exe, os.getpid(), tmp_path / "e.json",
                                                                             so_reabrir=True))
        assert _esperar(lambda: atualizacao._marca_existe(atualizacao.MARCA_DE_REABRIR)), "nao pegou a marca"
        time.sleep(3)
        assert atualizacao._marca_existe(atualizacao.MARCA_DE_REABRIR), "reabriu no meio da troca"
    finally:
        marca.soltar()
    assert _esperar(lambda: not atualizacao._marca_existe(atualizacao.MARCA_DE_REABRIR)), "nao terminou no fim"


class _VelopackDeMentira:
    """O UpdateManager do Velopack, de mentira: so anota o pedido de troca e responde a versao."""

    def __init__(self) -> None:
        """Nada pedido ainda."""
        self.trocas: list = []

    def get_current_version(self) -> str:
        """A versao instalada."""
        return "1.1.0"

    def wait_exit_then_apply_updates(self, alvo, *args, **kwargs) -> None:
        """Anota o pedido de troca."""
        self.trocas.append(alvo)


def test_conserto1_sem_a_marca_segura_o_velopack_nem_e_chamado_e_a_versao_continua_esperando(tmp_path):
    """A regra num lugar so: o unico pedido de troca (GerenteComAMarcaDaTroca) so chama o Velopack com a marca da
    troca segura. Sem ela, a troca nao comeca e a versao fica "pendente" (entra na proxima abertura, pelo script)."""
    from tests.test_decisoes_atualizacao import PUBLICA, GerenteFalso, _servidor

    falso = GerenteFalso()
    fonte = _servidor(tmp_path, falso.alvo)
    gerente = atualizacao.GerenteComAMarcaDaTroca(falso, segurar=lambda: False)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA,
                                           motor_no_lugar=lambda: True) == "pendente"
    assert falso.trocou == [] and atualizacao.ler_estado()["fase"] == "pendente"
    assert "não troco agora (não deu para segurar a marca da troca)" in _registro()
    gerente = atualizacao.GerenteComAMarcaDaTroca(falso, segurar=lambda: True)
    assert gerente.get_current_version() == falso.get_current_version(), "o resto passa direto"
    atualizacao.gravar_estado({})
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA,
                                           motor_no_lugar=lambda: True) == "aplicando"
    assert len(falso.trocou) == 1


def test_conserto1_o_gerente_do_programa_e_sempre_o_que_segura_a_marca(monkeypatch):
    """criar_gerente (o unico jeito de o programa ter o Velopack) devolve sempre o gerente com a protecao da troca."""
    import types

    falso = types.SimpleNamespace(UpdateOptions=lambda **k: k, GithubSource=lambda endereco: endereco,
                                  UpdateManager=lambda fonte, opcoes: _VelopackDeMentira())
    monkeypatch.setitem(sys.modules, "velopack", falso)
    gerente = atualizacao.criar_gerente(atualizacao.Fonte.padrao())
    assert isinstance(gerente, atualizacao.GerenteComAMarcaDaTroca)


def test_conserto1_segurar_a_marca_usa_a_do_script_ou_lanca_o_vigia_e_confere(tmp_path):
    """Com o script da troca rodando (a marca ja existe), nao lanca vigia. Sem ele, lanca o vigia e so diz "segura"
    depois de ler a marca no Windows; vigia que nao lanca, ou marca que nao aparece: False."""
    lancados: list[str] = []
    assert atualizacao.segurar_a_marca_da_troca(marca_existe=lambda n: True, lancar=lancados.append) is True
    assert lancados == []
    vezes = iter([False, False, True])
    assert atualizacao.segurar_a_marca_da_troca(marca_existe=lambda n: next(vezes), lancar=lancados.append,
                                                dormir=lambda s: None) is True
    assert len(lancados) == 1 and "Mutex" in lancados[0]

    def nao_lanca(script):
        raise OSError("o processo lançado não deu sinal de vida")

    assert atualizacao.segurar_a_marca_da_troca(marca_existe=lambda n: False, lancar=nao_lanca) is False
    atualizacao.ESPERA_PELA_MARCA_S, antes = 0.3, atualizacao.ESPERA_PELA_MARCA_S
    try:
        assert atualizacao.segurar_a_marca_da_troca(marca_existe=lambda n: None, lancar=lambda s: None,
                                                    dormir=lambda s: time.sleep(0.05)) is False
    finally:
        atualizacao.ESPERA_PELA_MARCA_S = antes
    assert "a marca da troca não apareceu no Windows" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 2: a pergunta do Windows so sai com a janela do programa na frente
# ---------------------------------------------------------------------------------------------------------------------

class _TelaDeMentira:
    """A tela do Windows, de mentira, vista pela pergunta: qual janela esta na frente a cada leitura, se a janela do
    programa existe e se esta minimizada. `frentes`: a resposta de cada leitura, em ordem (a ultima se repete)."""

    def __init__(self, frentes: list, minimizada: bool = False, fecha_depois: int | None = None) -> None:
        """Comeca com as respostas dadas; nada trazido para a frente ainda."""
        self.frentes = list(frentes)
        self.minimizada = minimizada
        self.fecha_depois = fecha_depois
        self.leituras = 0
        self.trazidas: list[int] = []

    def na_frente(self, janela: int):
        """A janela da frente, se for a do programa (como core.windows.janela_do_programa_na_frente)."""
        self.leituras += 1
        return self.frentes.pop(0) if len(self.frentes) > 1 else self.frentes[0]

    def existe(self, janela: int) -> bool:
        """A janela do programa ainda existe?"""
        return self.fecha_depois is None or self.leituras < self.fecha_depois

    def trazer(self, janela: int) -> bool:
        """A tentativa de trazer a janela para a frente (anotada)."""
        self.trazidas.append(janela)
        return False


def test_conserto2_o_kaique_nao_saiu_da_janela_a_pergunta_vem_logo():
    """Caso 1 pedido pela gerente: o Kaique abre e nao sai da janela; a janela ja esta na frente na primeira leitura:
    a pergunta sai na hora, sem esperar e sem registrar espera, com a janela da frente como dona."""
    tela = _TelaDeMentira([0x77])
    dormiu: list[float] = []
    assert atualizacao.esperar_a_janela_na_frente(0x77, na_frente=tela.na_frente, existe=tela.existe,
                                                  trazer=tela.trazer, minimizada=lambda j: False,
                                                  dormir=dormiu.append) == 0x77
    assert dormiu == [] and tela.trazidas == [] and tela.leituras == 1
    assert "espera" not in _registro()


def test_conserto2_a_janela_minimizada_a_pergunta_espera_ela_voltar_sem_a_desminimizar():
    """Caso 2 pedido pela gerente: a janela do programa minimizada. A pergunta espera (le de tempos em tempos, nada
    trava: roda no fio de tras) ate a janela voltar; nao tenta trazer a janela minimizada (nao desfaz o que o Kaique
    fez); o registro diz que esperou e quanto. No codigo de antes: perguntava na hora (e a pergunta so piscava)."""
    tela = _TelaDeMentira([None, None, None, None, 0x77])
    dormiu: list[float] = []
    assert atualizacao.esperar_a_janela_na_frente(0x77, na_frente=tela.na_frente, existe=tela.existe,
                                                  trazer=tela.trazer, minimizada=lambda j: True,
                                                  dormir=dormiu.append) == 0x77
    assert len(dormiu) == 3 and tela.trazidas == []
    assert "espera ela voltar" in _registro() and "a pergunta esperou" in _registro()


def test_conserto2_noutra_janela_tenta_trazer_uma_vez_e_espera_o_kaique_voltar():
    """O Kaique estava noutra janela: uma tentativa de trazer a do programa (o Windows pode recusar) e a pergunta espera
    em silencio; quando ele volta (um aviso do programa na frente conta), a dona da pergunta e a janela da frente."""
    tela = _TelaDeMentira([None, None, 0x88])
    assert atualizacao.esperar_a_janela_na_frente(0x77, na_frente=tela.na_frente, existe=tela.existe,
                                                  trazer=tela.trazer, minimizada=lambda j: False,
                                                  dormir=lambda s: None) == 0x88
    assert tela.trazidas == [0x77]


def test_conserto2_a_janela_fechou_antes_nada_e_perguntado(windows_volta4):
    """A janela do programa fechou antes de vir para a frente: nada e perguntado (nunca uma pergunta para piscar); a
    leitura do Windows diz o que falta e a pergunta volta na proxima abertura (D-741)."""
    tela = _TelaDeMentira([None], fecha_depois=3)
    windows_volta4.tela(tela)
    falta = atualizacao.preparar_na_primeira_abertura(0x77)
    assert windows_volta4.pedidos == [] and falta
    assert "fechou antes de vir para a frente" in _registro()


def test_conserto2_a_pergunta_so_sai_depois_que_a_janela_vem_para_a_frente(windows_volta4):
    """Defeito da prova de 22/11 ("a pergunta do Windows da primeira abertura ainda pisca na barra de tarefas"): o
    pedido saia com a janela do programa fora da frente. Agora ele so sai depois que a janela esta na frente, e a dona
    e a janela da frente. No codigo de antes: o pedido saia na primeira leitura, com a janela fora da frente."""
    tela = _TelaDeMentira([None, None, 0x77])
    windows_volta4.tela(tela)
    atualizacao.preparar_na_primeira_abertura(0x77)
    assert windows_volta4.pedidos == [0x77]
    assert windows_volta4.leituras_antes_do_pedido == 3, "perguntou antes de a janela vir para a frente"


@pytest.fixture
def windows_volta4(monkeypatch):
    """A pergunta e a leitura do Windows de mentira, so para o conserto 2: anota as perguntas e quantas leituras da
    tela houve antes de cada uma; a leitura das tarefas diz que nada foi criado."""

    class _Windows:
        """O Windows de mentira do conserto 2."""

        def __init__(self) -> None:
            """Nada perguntado."""
            self.pedidos: list[int | None] = []
            self.leituras_antes_do_pedido = None
            self._tela = None

        def tela(self, tela: _TelaDeMentira) -> None:
            """Liga a tela de mentira na peca."""
            self._tela = tela
            monkeypatch.setattr(windows, "janela_do_programa_na_frente", tela.na_frente, raising=False)
            monkeypatch.setattr(windows, "janela_existe", tela.existe, raising=False)
            monkeypatch.setattr(windows, "janela_minimizada", lambda j: False, raising=False)
            monkeypatch.setattr(windows, "trazer_para_a_frente", tela.trazer)

        def pedir(self, passos, janela=None):
            """A pergunta de mentira: o Kaique diz "Nao"."""
            self.pedidos.append(janela)
            self.leituras_antes_do_pedido = self._tela.leituras
            return windows.Resposta(windows.DISSE_NAO, "você disse Não; nada mudou")

    w = _Windows()
    monkeypatch.setattr(atualizacao, "pedir_licenca_ao_windows", w.pedir)
    monkeypatch.setattr(atualizacao, "ler_tarefa_no_windows", lambda nome: windows.Tarefa(nome, False))
    monkeypatch.setattr(atualizacao, "INTERVALO_DA_JANELA_S", 0.0, raising=False)
    monkeypatch.setattr(atualizacao, "e_portatil", lambda gerente=None: False)
    return w


@so_no_windows
def test_conserto2_a_leitura_da_janela_da_frente_de_verdade():
    """A leitura da peca, de verdade, so lendo (nenhuma janela e aberta): uma janela que nao existe nunca esta "na
    frente" nem existe; a janela que esta na frente agora (a que o Windows disser) e reconhecida como a da frente."""
    import ctypes

    assert windows.janela_do_programa_na_frente(None) is None
    assert windows.janela_do_programa_na_frente(0x7FFFFFF0) is None
    assert windows.janela_existe(0x7FFFFFF0) is False and windows.janela_minimizada(0x7FFFFFF0) is False
    user32 = ctypes.WinDLL("user32")
    user32.GetForegroundWindow.restype = ctypes.c_void_p
    frente = user32.GetForegroundWindow()
    if not frente or windows.janela_minimizada(frente):
        pytest.skip("sem janela na frente neste Windows (o do GitHub roda sem tela)")
    assert windows.janela_do_programa_na_frente(frente) == frente
