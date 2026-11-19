"""Testes da peça única do Windows (`core/windows.py`; plano da parte do Windows, passo 1, peças 1 e 2).

O QUE ESTES TESTES PROVAM, E O QUE NÃO PROVAM (D-767, D-785)
    Só rodam coisas que NÃO mudam o Windows: leem licenças de pasta, leem tarefas, rodam o PowerShell e programas
    comuns, lançam processos, cifram e decifram, criam pastas na pasta de dados dos testes. Nada aqui pede a licença
    de administrador, cria tarefa ou mexe em Arquivos de Programas: isso só conta rodando de verdade e à vista, na
    janela de prova (`janela_de_prova.py`), na sessão A do plano. Onde um teste troca uma função por uma de mentira, é
    só para garantir que a pergunta do Windows NÃO aparece (o pedido errado para antes), nunca para provar que o
    Windows fez algo.

    No GitHub, o Windows da nuvem roda como administrador sem a pergunta: o teste do trabalho com licença
    (`test_o_trabalho_com_licenca_faz_so_o_aviso`) então roda o script de verdade ali; no PC do Samuel, sem a licença,
    ele confere a recusa. Os dois desfechos são cobrados.

Seguro mexer: acrescentar casos. Arriscado: trocar uma leitura de verdade por uma de mentira (deixa de provar).
"""

from __future__ import annotations

import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core import windows  # noqa: E402

PY = sys.executable


def _pasta_local_da_conta() -> Path:
    """A pasta local da conta (a %LOCALAPPDATA% de verdade), perguntada ao Windows: o GitHub e o conftest desviam as
    variáveis de ambiente (a pasta temporária do GitHub fica no D: da máquina da nuvem, sem as licenças da conta)."""
    import uuid
    from ctypes import wintypes

    guid = windows._GUID.from_buffer_copy(uuid.UUID("f1b32785-6fba-4fcf-9d55-7b8e7f157091").bytes_le)
    saida = wintypes.LPWSTR()
    shell32 = ctypes.WinDLL("shell32")
    shell32.SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE,
                                             ctypes.POINTER(wintypes.LPWSTR)]
    assert shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(saida)) == 0
    caminho = Path(saida.value)
    ctypes.WinDLL("ole32").CoTaskMemFree(ctypes.cast(saida, ctypes.c_void_p))
    return caminho


@pytest.fixture(autouse=True)
def _pasta_da_conta_no_disco_do_sistema(monkeypatch):
    """A pasta de troca tem de nascer onde nasce no programa de verdade: dentro da pasta local da conta, onde só a
    conta, o sistema e os administradores gravam. A pasta de dados dos testes (`saida_teste`, no D: do Samuel) deixa
    "Todos" gravarem, e a pasta temporária do GitHub fica no D: da máquina da nuvem: a peça recusa a pasta de troca
    nos dois (com razão). Então, nestes testes, a pasta de dados fica numa pasta própria do teste dentro da pasta local
    da conta (perguntada ao Windows), criada com `os.mkdir` comum (herda as licenças da conta) e apagada no fim. Só a
    pasta que o próprio teste criou é apagada."""
    pasta = _pasta_local_da_conta() / f"EditorImpressaoTestesPecaWindows-{os.getpid()}-{time.time_ns()}"
    os.mkdir(pasta)
    monkeypatch.setenv("LOCALAPPDATA", str(pasta))
    yield pasta
    shutil.rmtree(pasta, ignore_errors=True)


def _troca_com_aviso(passos: list[dict], com_segredo: bool = False) -> Path:
    """Uma pasta de troca de verdade (na pasta de dados dos testes) com um aviso de trabalho dentro."""
    pasta = windows.criar_pasta_de_troca()
    aviso = {"formato": windows.FORMATO_DO_AVISO, "pedido_por": windows.sid_desta_conta(), "criado_em": "agora",
             "com_segredo": com_segredo, "passos": passos}
    (pasta / windows.NOME_DO_AVISO).write_text(json.dumps(aviso, ensure_ascii=False), encoding="utf-8")
    return pasta


# ---------------------------------------------------------------------------------------------------------------------
# A entrada no começo do programa
# ---------------------------------------------------------------------------------------------------------------------

def test_o_main_atende_o_argumento_da_peca_antes_de_tudo():
    """O texto do argumento no main.py é o mesmo da peça (lugar único: core.windows), e é atendido antes dos outros
    modos e antes do brasão (que só abre dentro de main())."""
    texto = (RAIZ / "main.py").read_text(encoding="utf-8")
    assert windows.ARG_TRABALHO_DE_ADMINISTRADOR == "--trabalho-de-administrador"
    assert f'sys.argv[1] == "{windows.ARG_TRABALHO_DE_ADMINISTRADOR}"' in texto
    bloco = texto[texto.index('if __name__ == "__main__":'):]
    assert bloco.index(windows.ARG_TRABALHO_DE_ADMINISTRADOR) < bloco.index("--servidor-de-paginas")
    assert bloco.index(windows.ARG_TRABALHO_DE_ADMINISTRADOR) < bloco.index("raise SystemExit(main())")


def test_o_trabalho_de_administrador_nao_abre_janela_nem_brasao():
    """Aberto com o argumento, o programa não carrega o Qt nem o brasão: atende e sai (aqui com uma pasta que não é
    de troca, então recusa com o código de pasta recusada)."""
    codigo = ("import runpy, sys\n"
              "sys.argv = ['main.py', '--trabalho-de-administrador', r'C:\\nao\\troca\\troca-x']\n"
              "try:\n    runpy.run_path('main.py', run_name='__main__')\n"
              "except SystemExit as e:\n"
              "    print('SAIDA', e.code, 'QT', 'PySide6' in sys.modules, 'BRASAO', "
              "'ui.tela_de_carregamento' in sys.modules)\n")
    feito = subprocess.run([PY, "-c", codigo], cwd=RAIZ, capture_output=True, text=True, timeout=120)
    assert f"SAIDA {windows.SAIDA_PASTA_RECUSADA} QT False BRASAO False" in feito.stdout, feito.stdout + feito.stderr


# ---------------------------------------------------------------------------------------------------------------------
# O lado com licença: o que ele aceita e o que recusa
# ---------------------------------------------------------------------------------------------------------------------

def test_o_trabalho_recusa_argumentos_e_pastas_que_nao_sao_de_troca():
    """Sem o caminho, com caminho a mais, ou com uma pasta que não é de troca: recusa e não faz nada."""
    assert windows.atender_trabalho_de_administrador([]) == windows.SAIDA_ARGUMENTOS_ERRADOS
    assert windows.atender_trabalho_de_administrador(["a", "b"]) == windows.SAIDA_ARGUMENTOS_ERRADOS
    assert windows.atender_trabalho_de_administrador([os.environ["SystemRoot"]]) == windows.SAIDA_PASTA_RECUSADA
    falsa = Path(tempfile.gettempdir()) / "troca" / "troca-nao-e-nossa"
    assert windows.atender_trabalho_de_administrador([str(falsa)]) == windows.SAIDA_PASTA_RECUSADA


def test_o_trabalho_recusa_a_pasta_de_troca_que_e_um_atalho(tmp_path):
    """Uma junção (atalho do Windows para outra pasta) com nome de pasta de troca é recusada, mesmo apontando para uma
    pasta de troca de verdade."""
    import _winapi

    verdadeira = _troca_com_aviso([{"tipo": "script", "descricao": "x", "dados": {"texto": "", "com_segredo": False,
                                                                                  "limite_s": 10}}])
    atalho = verdadeira.parent / (windows.PREFIXO_DA_TROCA + "atalho-do-teste")
    _winapi.CreateJunction(str(verdadeira), str(atalho))
    try:
        assert windows._e_atalho(atalho)
        assert windows.atender_trabalho_de_administrador([str(atalho)]) == windows.SAIDA_PASTA_RECUSADA
        assert not (verdadeira / windows.NOME_DO_RELATORIO).exists()
    finally:
        os.rmdir(atalho)                     # tira só a junção; a pasta de verdade continua
        assert verdadeira.is_dir()
        windows.apagar_pasta_de_troca(verdadeira)


def test_o_trabalho_recusa_aviso_que_nao_e_do_programa():
    """Aviso de outro formato, sem a conta que pediu, ou que não é JSON: recusa sem escrever relatório."""
    pasta = windows.criar_pasta_de_troca()
    try:
        for conteudo in ("isto não é json", json.dumps({"formato": 99, "passos": []}),
                         json.dumps({"formato": windows.FORMATO_DO_AVISO, "pedido_por": "eu", "passos": []})):
            (pasta / windows.NOME_DO_AVISO).write_text(conteudo, encoding="utf-8")
            assert windows.atender_trabalho_de_administrador([str(pasta)]) == windows.SAIDA_PASTA_RECUSADA
            assert not (pasta / windows.NOME_DO_RELATORIO).exists()
    finally:
        windows.apagar_pasta_de_troca(pasta)


def test_o_trabalho_com_licenca_faz_so_o_aviso():
    """O lado com licença, de verdade: sem a licença (o PC do Samuel), recusa e não roda o script; com a licença (o
    Windows do GitHub, que roda como administrador sem pergunta), roda o script do aviso e o relatório diz "deu
    certo". Nos dois casos o relatório existe e diz o que aconteceu."""
    pasta = windows.criar_pasta_de_troca()
    marca = pasta / "o-script-rodou.txt"
    texto = f"[System.IO.File]::WriteAllText('{marca}', 'Ação')\n[Console]::Out.Write('ÊXITO')"
    aviso = {"formato": windows.FORMATO_DO_AVISO, "pedido_por": windows.sid_desta_conta(), "criado_em": "agora",
             "com_segredo": False,
             "passos": [{"tipo": "script", "descricao": "escrever a marca", "dados": {"texto": texto,
                                                                                    "com_segredo": False,
                                                                                    "limite_s": 120}}]}
    (pasta / windows.NOME_DO_AVISO).write_text(json.dumps(aviso, ensure_ascii=False), encoding="utf-8")
    try:
        codigo = windows.atender_trabalho_de_administrador([str(pasta)])
        relatorio = json.loads((pasta / windows.NOME_DO_RELATORIO).read_text(encoding="utf-8"))
        resposta = windows._desfecho_do_trabalho(codigo, relatorio)
        if windows.tem_licenca_de_administrador():
            assert codigo == windows.SAIDA_TUDO_CERTO and resposta.deu_certo
            assert marca.read_text(encoding="utf-8") == "Ação"
            assert relatorio["passos"][0]["saida"] == "ÊXITO"
        else:
            assert codigo == windows.SAIDA_SEM_LICENCA and resposta.desfecho == windows.FALHOU
            assert "licença de administrador" in resposta.motivo
            assert not marca.exists()
            assert relatorio["passos"][0]["resultado"] == "não tentado"
    finally:
        windows.apagar_pasta_de_troca(pasta)


def test_o_aviso_so_aceita_a_lista_fechada():
    """Tipo de passo desconhecido, pasta segura fora da lista, tarefa fora da pasta do programa, arquivo com "..",
    script sem limite aceito: tudo recusado. Os passos montados pelas funções da peça são aceitos."""
    def problemas(passo) -> list[str]:
        """Os problemas de um passo, como o lado com licença confere."""
        return windows._problemas_do_passo(passo)

    assert problemas({"tipo": "formatar_o_disco", "descricao": "x", "dados": {}})
    assert problemas({"tipo": "criar_pasta_segura", "descricao": "x", "dados": {"nome": "Windows"}})
    assert problemas({"tipo": "apagar_pasta_segura", "descricao": "x", "dados": {"nome": "..\\Windows"}})
    assert problemas({"tipo": "apagar_tarefa", "descricao": "x", "dados": {"nome": "\\Microsoft\\Windows\\Defrag"}})
    assert problemas({"tipo": "criar_tarefa", "descricao": "x", "dados": {"nome": "EditorImpressao\\a\\b", "xml": ""}})
    assert problemas({"tipo": "gravar_na_pasta_segura", "descricao": "x",
                      "dados": {"nome": windows.NOME_DA_PASTA_SEGURA, "arquivo": "..\\x.ps1", "texto": ""}})
    assert problemas({"tipo": "script", "descricao": "x", "dados": {"texto": "", "com_segredo": False,
                                                                   "limite_s": 99999}})
    assert problemas("não é passo")
    from dataclasses import asdict

    xml = windows.xml_da_tarefa_do_sistema("C:\\a.exe", "", "d", "D:(A;;FA;;;SY)")
    for passo in (windows.passo_criar_pasta_segura(), windows.passo_apagar_pasta_segura(windows.NOME_DA_PASTA_SEGURA),
                  windows.passo_gravar_na_pasta_segura(windows.NOME_DA_PASTA_SEGURA, "a.ps1", "x"),
                  windows.passo_criar_tarefa("EditorImpressao\\Prova", xml),
                  windows.passo_apagar_tarefa("EditorImpressao\\Prova"), windows.passo_script("s", "x", True, 60)):
        assert problemas(asdict(passo)) == [], passo


# ---------------------------------------------------------------------------------------------------------------------
# O lado que pede
# ---------------------------------------------------------------------------------------------------------------------

def test_pedir_licenca_errado_para_antes_da_pergunta(monkeypatch):
    """Pedido sem passos, com passo fora da lista ou com um programa que não existe: "falhou" em português, e a
    pergunta do Windows nem chega a ser feita (a função que abre com licença não é chamada)."""
    def nao_pode(*_a, **_k):
        """Se chegasse aqui, o Windows faria a pergunta: o teste falha."""
        raise AssertionError("a pergunta do Windows não podia ter sido feita")

    monkeypatch.setattr(windows, "_abrir_com_licenca", nao_pode)
    r = windows.pedir_licenca([])
    assert r.desfecho == windows.FALHOU and "pedido" in r.motivo
    r = windows.pedir_licenca([windows.Passo("formatar_o_disco", "x", {})])
    assert r.desfecho == windows.FALHOU
    r = windows.pedir_licenca([windows.passo_script("s", "x")], programa=["C:\\nao\\existe\\EditorImpressao.exe"])
    assert r.desfecho == windows.FALHOU and "não achei o programa" in r.motivo


def test_o_desfecho_vem_do_relatorio_nunca_so_do_codigo():
    """Sem relatório, nunca "deu certo" (nem com o código 0); relatório recusado, pela metade ou com um passo que
    falhou: "falhou", com o passo; só tudo feito e o código 0 dão "deu certo"."""
    ok = {"passos": [{"descricao": "a", "resultado": windows.DEU_CERTO}], "terminou": True, "recusado": ""}
    assert windows._desfecho_do_trabalho(0, None).desfecho == windows.FALHOU
    assert "não é só desta conta" in windows._desfecho_do_trabalho(windows.SAIDA_PASTA_RECUSADA, None).motivo
    assert windows._desfecho_do_trabalho(0, {**ok, "recusado": "sem licença"}).desfecho == windows.FALHOU
    assert windows._desfecho_do_trabalho(0, {**ok, "terminou": False}).desfecho == windows.FALHOU
    falhou = {**ok, "passos": [{"descricao": "criar a tarefa", "resultado": windows.FALHOU, "motivo": "m"}]}
    r = windows._desfecho_do_trabalho(1, falhou)
    assert r.desfecho == windows.FALHOU and r.motivo.startswith("criar a tarefa")
    assert windows._desfecho_do_trabalho(1, ok).desfecho == windows.FALHOU
    assert windows._desfecho_do_trabalho(0, {**ok, "passos": []}).desfecho == windows.FALHOU
    assert windows._desfecho_do_trabalho(0, ok).deu_certo


def test_o_nao_e_lido_pelo_erro_guardado_daquela_chamada():
    """Etapa 5, defeito 2 (18/11): o "Não" na pergunta do Windows virava "deu certo" porque o erro era lido sem
    guardar o último erro da chamada (`ctypes.windll`, sem `use_last_error`). Todas as bibliotecas da peça guardam o
    erro; a do jeito antigo não guarda (este teste acusaria o jeito antigo)."""
    guarda = ctypes._FUNCFLAG_USE_LASTERROR
    w = windows._win()
    for biblioteca in (w.kernel32, w.advapi32, w.shell32, w.user32, w.ole32, w.crypt32):
        assert biblioteca._FuncPtr._flags_ & guarda, biblioteca
    assert not ctypes.windll.shell32._FuncPtr._flags_ & guarda      # o jeito de core/_testes_a_distancia_windows.py
    assert windows.ERRO_CANCELADO == 1223
    assert "não achei" in windows._motivo_do_erro_ao_abrir(windows.ERRO_ARQUIVO_NAO_ACHADO)


# ---------------------------------------------------------------------------------------------------------------------
# A pasta de troca
# ---------------------------------------------------------------------------------------------------------------------

def test_a_pasta_de_troca_herda_as_licencas_da_conta():
    """Etapa 5, defeito 3 (18/11): a pasta temporária do Python 3.14 (`mkdtemp`) nasce com a lista protegida e a
    licença "do dono"; o arquivo que o programa com licença cria tem outro dono, e a conta comum não lia o
    relatório. A pasta de troca nasce do jeito comum: herda, e a conta aparece pelo nome dela."""
    sid = windows.sid_desta_conta()
    pasta = windows.criar_pasta_de_troca()
    try:
        lic = windows.ler_licencas(pasta)
        assert not lic.protegida
        assert any(li.sid == sid and li.herdada and li.grava for li in lic.lista)
        assert not any(li.sid == windows.SID_DIREITOS_DO_DONO for li in lic.lista)
        assert lic.dono == sid
        assert windows._problemas_da_pasta_de_troca(lic, sid) == []
    finally:
        assert windows.apagar_pasta_de_troca(pasta)
        assert not pasta.exists()
    antiga = Path(tempfile.mkdtemp())                       # o jeito antigo, para mostrar a diferença
    try:
        lic = windows.ler_licencas(antiga)
        assert lic.protegida and any(li.sid == windows.SID_DIREITOS_DO_DONO for li in lic.lista)
    finally:
        os.rmdir(antiga)


def test_a_regra_da_pasta_de_troca_recusa_outra_conta():
    """A regra (lugar único dos dois lados): dono de outra conta, ou outra conta que pode gravar, é problema."""
    sid = "S-1-5-21-1-2-3-1001"

    def lic(dono: str, *linhas) -> windows.Licencas:
        """Licenças montadas para o teste da regra."""
        return windows.Licencas("x", dono, "", False, False, tuple(linhas))

    def linha(quem: str, mascara: int, tipo: str = "permite") -> windows.Licenca:
        """Uma linha de licença montada."""
        return windows.Licenca(quem, "", tipo, mascara, True, False)

    assert windows._problemas_da_pasta_de_troca(lic(sid, linha(sid, 0x1F01FF)), sid) == []
    assert windows._problemas_da_pasta_de_troca(lic(sid, linha("S-1-1-0", 0x2)), sid)          # Todos gravam
    assert windows._problemas_da_pasta_de_troca(lic(sid, linha(windows.SID_USUARIOS, 0x1301BF)), sid)
    assert windows._problemas_da_pasta_de_troca(lic("S-1-5-21-9-9-9-1002", linha(sid, 0x1F01FF)), sid)
    assert windows._problemas_da_pasta_de_troca(windows.Licencas("x", sid, "", False, True, ()), sid)  # sem lista
    assert windows._problemas_da_pasta_de_troca(lic(sid, linha(windows.SID_USUARIOS, 0x1200A9)), sid) == []


def test_apagar_pasta_de_troca_so_apaga_pasta_de_troca(tmp_path):
    """Uma pasta que não é de troca (nome ou lugar errado) não é apagada."""
    outra = tmp_path / "troca-mas-fora-do-lugar"
    outra.mkdir()
    assert windows.apagar_pasta_de_troca(outra) is False and outra.is_dir()
    assert windows.apagar_pasta_de_troca(Path(os.environ["SystemRoot"])) is False


# ---------------------------------------------------------------------------------------------------------------------
# Rodar e esperar: as letras certas
# ---------------------------------------------------------------------------------------------------------------------

def test_a_resposta_das_ferramentas_do_windows_e_lida_na_tabela_do_console():
    """Etapa 5, revisão do atualizador 1.3: a resposta do Windows era lida na tabela errada ("ÒXITO" no registro).
    Um programa de console escreve na tabela OEM; lida como OEM, volta igual; lida como ANSI (o jeito antigo), não."""
    r = windows.rodar_e_esperar(["cmd", "/c", "echo", "çéü"])
    assert r.deu_certo and r.dados["saida"] == "çéü"
    cru = subprocess.run(["cmd", "/c", "echo", "çéü"], capture_output=True,
                         creationflags=windows.CREATE_NO_WINDOW).stdout.strip()
    assert cru.decode("cp1252", "replace") != "çéü"


def test_rodar_e_esperar_diz_cada_falha():
    """Programa que não existe, código de erro e tempo esgotado: "falhou", com a frase certa."""
    assert "não achei" in windows.rodar_e_esperar(["C:\\nao\\existe.exe"]).motivo
    r = windows.rodar_e_esperar([PY, "-c", "raise SystemExit(3)"], letras="utf-8")
    assert r.desfecho == windows.FALHOU and r.dados["codigo"] == 3
    r = windows.rodar_e_esperar([PY, "-c", "import time; time.sleep(20)"], limite_s=1, letras="utf-8")
    assert r.desfecho == windows.FALHOU and "não terminou" in r.motivo


def test_o_script_vai_com_a_marca_de_utf8_e_acento_e_segredo_chegam_iguais(tmp_path):
    """O script é gravado com a marca de UTF-8 (sem ela o PowerShell 5.1 lê como ANSI) e o texto com acento dentro do
    script e o segredo com acento (pela entrada, nunca pela linha de comando) chegam iguais."""
    arquivo = tmp_path / "s.ps1"
    windows._gravar_script(arquivo, "Write-Output 'ç'")
    assert arquivo.read_bytes().startswith(b"\xef\xbb\xbf")
    segredo = "Senha de prova: çÃõ€ ção"
    r = windows.rodar_powershell("$s = [Console]::In.ReadLine()\n"
                                 "$h = [System.Security.Cryptography.SHA256]::Create().ComputeHash($__utf8.GetBytes($s))\n"
                                 "[Console]::Out.Write('Ação ÊXITO|' + (($h | ForEach-Object { $_.ToString('x2') }) "
                                 "-join ''))", segredo=segredo)
    assert r.deu_certo, r.detalhe
    texto, soma = r.dados["saida"].split("|")
    import hashlib

    assert texto == "Ação ÊXITO"
    assert soma == hashlib.sha256(segredo.encode("utf-8")).hexdigest()


def test_o_script_que_da_erro_volta_falhou():
    """Um erro dentro do script (o script para no primeiro erro) vira "falhou", com o código de saída."""
    r = windows.rodar_powershell("throw 'erro de propósito'")
    assert r.desfecho == windows.FALHOU and r.dados["codigo"] != 0


# ---------------------------------------------------------------------------------------------------------------------
# Lançar solto
# ---------------------------------------------------------------------------------------------------------------------

_NETO = r"""
import ctypes, sys, time
sinal, depois, pai = sys.argv[1], sys.argv[2], int(sys.argv[3])
open(sinal, "w", encoding="utf-8").write("comecei")
k = ctypes.WinDLL("kernel32")
k.OpenProcess.restype = ctypes.c_void_p
h = k.OpenProcess(0x00100000, False, pai)
if h:
    k.WaitForSingleObject(ctypes.c_void_p(h), 30000)
open(depois, "w", encoding="utf-8").write("rodei depois de quem lançou fechar")
"""

_FILHO = r"""
import sys
sys.path.insert(0, sys.argv[1])
import os
from core import windows
sinal, depois, neto = sys.argv[2], sys.argv[3], sys.argv[4]
r = windows.lancar_solto([sys.executable, neto, sinal, depois, str(os.getpid())], sinal, 30)
print(r.desfecho, r.dados.get("grupo"))
"""


def test_lancar_solto_continua_depois_de_quem_lancou_fechar(tmp_path):
    """Etapa 5, defeito 1 (18/11): o processo lançado solto saía sem rodar. Aqui um processo lança outro e fecha; o
    lançado dá o sinal de vida, espera quem o lançou fechar e só então escreve que rodou."""
    neto = tmp_path / "neto.py"
    neto.write_text(_NETO, encoding="utf-8")
    sinal, depois = tmp_path / "sinal.txt", tmp_path / "depois.txt"
    feito = subprocess.run([PY, "-c", _FILHO, str(RAIZ), str(sinal), str(depois), str(neto)], capture_output=True,
                           text=True, timeout=120, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert feito.stdout.startswith(windows.DEU_CERTO), feito.stdout + feito.stderr
    fim = time.monotonic() + 30
    while not depois.exists() and time.monotonic() < fim:
        time.sleep(0.2)
    assert depois.read_text(encoding="utf-8") == "rodei depois de quem lançou fechar"


def test_lancar_solto_sem_sinal_de_vida_fecha_o_lancado(tmp_path):
    """O lançado que não dá sinal de vida no tempo é fechado (nada fica rodando pela metade) e a resposta é
    "falhou"; o que sai sem dar sinal também é "falhou", com o código."""
    atrasado = tmp_path / "atrasado.txt"
    r = windows.lancar_solto([PY, "-c", f"import time; time.sleep(4); open(r'{atrasado}', 'w').write('x')"],
                             tmp_path / "nunca.txt", espera_s=1)
    assert r.desfecho == windows.FALHOU and "fechado" in r.motivo
    time.sleep(6)
    assert not atrasado.exists()
    r = windows.lancar_solto([PY, "-c", "raise SystemExit(7)"], tmp_path / "nunca.txt", espera_s=10)
    assert r.desfecho == windows.FALHOU and "código 7" in r.motivo


def test_lancar_powershell_solto_roda_e_apaga_a_propria_pasta(tmp_path):
    """O script lançado solto dá o sinal, roda (com acento) e apaga a própria pasta de troca no fim."""
    saida = tmp_path / "saida.txt"

    def trocas() -> set:
        """As pastas de troca que existem agora."""
        mae = windows._pasta_mae_da_troca()
        return set(mae.iterdir()) if mae.is_dir() else set()

    antes = trocas()
    r = windows.lancar_powershell_solto(f"Start-Sleep -Milliseconds 300\n"
                                        f"[System.IO.File]::WriteAllText('{saida}', 'Ação ÊXITO')")
    assert r.deu_certo, r.detalhe
    fim = time.monotonic() + 30
    while time.monotonic() < fim and (not saida.exists() or trocas() - antes):
        time.sleep(0.2)
    assert saida.read_text(encoding="utf-8-sig") == "Ação ÊXITO"
    assert not trocas() - antes


# ---------------------------------------------------------------------------------------------------------------------
# Ler sem licença: marcas, tarefas, licenças, a pasta segura
# ---------------------------------------------------------------------------------------------------------------------

def test_marca_existe_le_o_windows():
    """Uma marca criada agora existe; depois de solta, não existe."""
    nome = f"Local\\EditorImpressao-teste-{os.getpid()}-{time.time_ns()}"
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateMutexW.restype = ctypes.c_void_p
    alca = k.CreateMutexW(None, False, nome)
    try:
        assert windows.marca_existe(nome) is True
    finally:
        k.CloseHandle(ctypes.c_void_p(alca))
    assert windows.marca_existe(nome) is False


def test_ler_tarefa_que_nao_existe_e_nome_fora_da_pasta():
    """Tarefa do programa que não existe: existe=False. Nome fora da pasta do programa: nem pergunta (None)."""
    assert windows.ler_tarefa("EditorImpressao\\Tarefa que nao existe do teste").existe is False
    fora = windows.ler_tarefa("\\Microsoft\\Windows\\Defrag\\ScheduledDefrag")
    assert fora.existe is None and "fora da pasta" in fora.motivo


def test_o_xml_da_tarefa_ida_e_volta():
    """O XML que a peça escreve é lido de volta pelo mesmo leitor que lê o que o Windows devolve: comando com espaço,
    argumentos com aspas, descrição com acento, quem roda (o sistema) e quem pode mandar rodar."""
    xml = windows.xml_da_tarefa_do_sistema("C:\\Program Files\\Editor X\\a.exe", '-File "C:\\a b\\c.ps1"',
                                           "Prova da peça: ção & <coisa>", "D:(A;;FA;;;BA)(A;;GRGX;;;AU)")
    lido = windows.ler_xml_da_tarefa(xml)
    assert lido == {"comando": "C:\\Program Files\\Editor X\\a.exe", "argumentos": '-File "C:\\a b\\c.ps1"',
                    "usuario": windows.SID_SISTEMA, "quem_pode": "D:(A;;FA;;;BA)(A;;GRGX;;;AU)"}


def test_o_leitor_de_tarefa_le_o_que_o_windows_devolve():
    """Uma tarefa do próprio Windows (a de desfragmentar), lida pelo mesmo leitor: roda como o sistema."""
    texto = windows.rodar_powershell("$s = New-Object -ComObject Schedule.Service\n$s.Connect()\n"
                                     "[Console]::Out.Write($s.GetFolder('\\Microsoft\\Windows\\Defrag')"
                                     ".GetTask('ScheduledDefrag').Xml)")
    if not texto.deu_certo:
        pytest.skip("este Windows não tem a tarefa de desfragmentar para ler")
    lido = windows.ler_xml_da_tarefa(texto.dados["saida"])
    assert lido["usuario"] == windows.SID_SISTEMA and lido["comando"].lower().endswith("defrag.exe")


def test_a_regra_da_pasta_segura_com_pastas_de_verdade():
    """Uma pasta que o Windows fez em Arquivos de Programas (Common Files) tem só as licenças de fábrica: passa. A
    pasta de troca (a conta grava e é dona) não passa. As linhas montadas: conta comum que grava, ou ninguém comum que
    lê, não passam."""
    comuns = windows.pasta_de_programas() / "Common Files"
    assert windows._problemas_da_pasta_segura(windows.ler_licencas(comuns)) == []
    pasta = windows.criar_pasta_de_troca()
    try:
        assert windows._problemas_da_pasta_segura(windows.ler_licencas(pasta))
    finally:
        windows.apagar_pasta_de_troca(pasta)
    le = windows.Licenca(windows.SID_USUARIOS, "", "permite", 0x1200A9, True, False)
    grava = windows.Licenca(windows.SID_USUARIOS, "", "permite", 0x1301BF, True, False)
    adm = windows.Licenca(windows.SID_ADMINISTRADORES, "", "permite", 0x1F01FF, True, False)
    base = windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False, (adm, le))
    assert windows._problemas_da_pasta_segura(base) == []
    assert windows._problemas_da_pasta_segura(windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False,
                                                               (adm, le, grava)))
    assert windows._problemas_da_pasta_segura(windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False,
                                                               (adm,)))


def test_a_pasta_segura_fica_ao_lado_do_programa_e_so_com_nome_da_lista():
    """A pasta segura fica em Arquivos de Programas, com nome próprio (não o da pasta do programa, que o Velopack
    troca e apaga); nome fora da lista fechada é recusado."""
    import versao

    caminho = windows.pasta_segura()
    assert caminho.parent == windows.pasta_de_programas()
    assert caminho.name not in (versao.ID_DO_PACOTE, "EditorImpressao")
    with pytest.raises(ValueError):
        windows.pasta_segura("Windows")


def test_conferir_pasta_segura_que_nao_existe():
    """A pasta segura de prova não existe fora da sessão de prova: a leitura diz "não existe" (sem licença)."""
    r = windows.conferir_pasta_segura(windows.NOME_DA_PASTA_SEGURA_DE_PROVA)
    assert r.desfecho == windows.FALHOU and r.dados.get("existe") is False


def test_o_segredo_ida_e_volta():
    """O segredo cifrado pelo Windows volta igual, com acento, e não fica legível no arquivo."""
    segredo = "Senha de prova: çÃõ€"
    cifrado = windows.cifrar_segredo(segredo)
    assert segredo.encode("utf-8") not in cifrado
    assert windows.decifrar_segredo(cifrado) == segredo


def test_trazer_para_a_frente_sem_janela_diz_que_nao():
    """Sem janela, ou com um número que não é janela: False (nunca finge que veio para a frente)."""
    assert windows.trazer_para_a_frente(None) is False
    assert windows.trazer_para_a_frente(0) is False
    assert windows.trazer_para_a_frente(0x7FFFFFF0) is False


def test_a_peca_nao_importa_a_tela():
    """A peça é do processamento: não importa Qt nem ui/ (roda por linha de comando e no programa com licença)."""
    texto = (RAIZ / "core" / "windows.py").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from|import)\s+(PySide6|ui)\b", texto, re.M)


def test_o_programa_deste_processo_existe():
    """Pelo código, o programa a abrir com licença é o pythonw (sem console) com o main.py; os dois existem."""
    programa = windows.programa_deste_processo()
    assert all(Path(p).is_file() for p in programa)
    assert programa[-1].endswith("main.py")
