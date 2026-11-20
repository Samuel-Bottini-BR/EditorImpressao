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

    class Guid(ctypes.Structure):
        """O GUID do Windows (para a pasta conhecida)."""
        _fields_ = [("a", wintypes.DWORD), ("b", wintypes.WORD), ("c", wintypes.WORD), ("d", ctypes.c_ubyte * 8)]

    guid = Guid.from_buffer_copy(uuid.UUID("f1b32785-6fba-4fcf-9d55-7b8e7f157091").bytes_le)
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
        assert windows.e_atalho(atalho)
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
        resposta = windows.desfecho_do_trabalho(codigo, relatorio)
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
        return windows.problemas_do_passo(passo)

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

def test_pedir_licenca_errado_para_antes_da_pergunta():
    """Pedido sem passos, com passo fora da lista ou com um programa que não existe: "falhou" em português, e a
    pergunta do Windows nem chega a ser feita. Todos pedem um programa que não existe: mesmo que a conferência do
    pedido sumisse, o Windows não abriria pergunta nenhuma (só "não achei"); a frase do pedido errado prova qual
    conferência parou."""
    nao_existe = ["C:\\nao\\existe\\EditorImpressao.exe"]
    r = windows.pedir_licenca([], programa=nao_existe)
    assert r.desfecho == windows.FALHOU and "pedido ao Windows está errado" in r.motivo
    r = windows.pedir_licenca([windows.Passo("formatar_o_disco", "x", {})], programa=nao_existe)
    assert r.desfecho == windows.FALHOU and "pedido ao Windows está errado" in r.motivo
    r = windows.pedir_licenca([windows.passo_script("s", "x")], programa=["C:\\nao\\existe\\EditorImpressao.exe"])
    assert r.desfecho == windows.FALHOU and "não achei o programa" in r.motivo


def test_o_desfecho_vem_do_relatorio_nunca_so_do_codigo():
    """Sem relatório, nunca "deu certo" (nem com o código 0); relatório recusado, pela metade ou com um passo que
    falhou: "falhou", com o passo; só tudo feito e o código 0 dão "deu certo"."""
    ok = {"passos": [{"descricao": "a", "resultado": windows.DEU_CERTO}], "terminou": True, "recusado": ""}
    assert windows.desfecho_do_trabalho(0, None).desfecho == windows.FALHOU
    assert "não é só desta conta" in windows.desfecho_do_trabalho(windows.SAIDA_PASTA_RECUSADA, None).motivo
    assert windows.desfecho_do_trabalho(0, {**ok, "recusado": "sem licença"}).desfecho == windows.FALHOU
    assert windows.desfecho_do_trabalho(0, {**ok, "terminou": False}).desfecho == windows.FALHOU
    falhou = {**ok, "passos": [{"descricao": "criar a tarefa", "resultado": windows.FALHOU, "motivo": "m"}]}
    r = windows.desfecho_do_trabalho(1, falhou)
    assert r.desfecho == windows.FALHOU and r.motivo.startswith("criar a tarefa")
    assert windows.desfecho_do_trabalho(1, ok).desfecho == windows.FALHOU
    assert windows.desfecho_do_trabalho(0, {**ok, "passos": []}).desfecho == windows.FALHOU
    assert windows.desfecho_do_trabalho(0, ok).deu_certo


def test_o_erro_do_windows_e_o_daquela_chamada():
    """Etapa 5, defeito 2 (18/11): o "Não" na pergunta do Windows virava "deu certo" porque o erro era lido sem
    guardar o último erro da chamada. Aqui, pelo comportamento: a peça pergunta por uma marca que não existe, e só
    lendo o erro daquela chamada ("não achado") ela responde "não existe" (False); lido do jeito antigo, o erro vem 0
    e a resposta seria "não deu para saber" (None)."""
    assert windows.marca_existe(f"Local\\EditorImpressao-nao-existe-{time.time_ns()}") is False
    assert windows.ERRO_CANCELADO == 1223


def test_o_nao_e_so_o_nao_e_uma_falha_nunca_vira_nao():
    """Achado 3 de quem tentou quebrar (19/11): nenhum teste provava que o "Não" vira "você disse Não" e que uma
    falha não vira "Não". O erro "cancelado" (1223) é "nao"; qualquer outro é "erro:<n>". E o desfecho: "nao" é
    DISSE_NAO (nunca "deu certo"); erro é FALHOU (nunca DISSE_NAO); passou do tempo é FALHOU e diz que o trabalho pode
    continuar; terminou sem relatório é FALHOU."""
    assert windows.o_que_houve_ao_abrir(windows.ERRO_CANCELADO) == "nao"
    for erro in (2, 3, 5, 1155, 1460, 0):
        assert windows.o_que_houve_ao_abrir(erro) == f"erro:{erro}"
    pedidos = [{"tipo": "script", "descricao": "a"}]
    ok = {"passos": [{"tipo": "script", "descricao": "a", "resultado": windows.DEU_CERTO}], "terminou": True,
          "recusado": ""}
    r = windows.resposta_do_pedido("nao", None, "t", None, pedidos, 60)
    assert r.desfecho == windows.DISSE_NAO and "Não" in r.motivo
    r = windows.resposta_do_pedido("erro:5", None, "t", None, pedidos, 60)
    assert r.desfecho == windows.FALHOU and "não deixou" in r.motivo
    r = windows.resposta_do_pedido("erro:2", None, "t", None, pedidos, 60)
    assert r.desfecho == windows.FALHOU and "não achei" in r.motivo
    r = windows.resposta_do_pedido("tempo", None, "t", ok, pedidos, 600)
    assert r.desfecho == windows.FALHOU and "pode continuar" in r.motivo
    r = windows.resposta_do_pedido("sem_acompanhar", None, "t", ok, pedidos, 600)
    assert r.desfecho == windows.FALHOU and "pode continuar" in r.motivo
    assert windows.resposta_do_pedido("terminou", 0, "t", None, pedidos, 60).desfecho == windows.FALHOU
    assert windows.resposta_do_pedido("terminou", 0, "t", ok, pedidos, 60).deu_certo


def test_o_relatorio_tem_de_bater_com_o_pedido():
    """Achado 14 de quem tentou quebrar: um relatório com menos passos (ou outros) que o pedido, todos "deu certo",
    não vira "deu certo"."""
    pedidos = [{"tipo": "script", "descricao": "a"}, {"tipo": "criar_tarefa", "descricao": "b"}]
    so_um = {"passos": [{"tipo": "script", "descricao": "a", "resultado": windows.DEU_CERTO}], "terminou": True,
             "recusado": ""}
    r = windows.desfecho_do_trabalho(0, so_um, pedidos)
    assert r.desfecho == windows.FALHOU and "não bate" in r.motivo
    outro = {**so_um, "passos": [{"tipo": "script", "descricao": "a", "resultado": windows.DEU_CERTO},
                                 {"tipo": "script", "descricao": "b", "resultado": windows.DEU_CERTO}]}
    assert windows.desfecho_do_trabalho(0, outro, pedidos).desfecho == windows.FALHOU


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
        # Dono (regra do Windows, não do ambiente): com o Controle de Conta ligado e sem a licença, a conta; com a
        # licença ligada (programa aberto como administrador, Controle de Conta desligado, a conta Administrador
        # embutida, o Windows do GitHub), o grupo Administradores. É por isso que o arquivo do programa com licença
        # tem outro dono (o defeito 3 acima). A regra da peça aceita os dois.
        esperado = windows.SID_ADMINISTRADORES if windows.tem_licenca_de_administrador() else sid
        assert lic.dono == esperado
        assert windows.problemas_da_pasta_de_troca(lic, sid) == []
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

    assert windows.problemas_da_pasta_de_troca(lic(sid, linha(sid, 0x1F01FF)), sid) == []
    assert windows.problemas_da_pasta_de_troca(lic(sid, linha("S-1-1-0", 0x2)), sid)          # Todos gravam
    assert windows.problemas_da_pasta_de_troca(lic(sid, linha(windows.SID_USUARIOS, 0x1301BF)), sid)
    assert windows.problemas_da_pasta_de_troca(lic("S-1-5-21-9-9-9-1002", linha(sid, 0x1F01FF)), sid)
    assert windows.problemas_da_pasta_de_troca(windows.Licencas("x", sid, "", False, True, ()), sid)  # sem lista
    # Achado 8 de quem tentou quebrar: outra conta que LÊ também é problema (o segredo cifrado para o computador fica
    # ali enquanto o pedido roda).
    assert windows.problemas_da_pasta_de_troca(lic(sid, linha(windows.SID_USUARIOS, 0x1200A9)), sid)
    assert windows.problemas_da_pasta_de_troca(lic(sid, linha(sid, 0x1F01FF), linha("S-1-1-0", 0x120089)), sid)
    # Dono Administradores (a pasta criada por quem já roda com a licença ligada): aceita, porque só administrador
    # muda as licenças dela; uma conta comum continua sem poder gravar.
    assert windows.problemas_da_pasta_de_troca(lic(windows.SID_ADMINISTRADORES, linha(sid, 0x1F01FF)), sid) == []
    assert windows.problemas_da_pasta_de_troca(lic(windows.SID_ADMINISTRADORES, linha(sid, 0x1F01FF),
                                                    linha(windows.SID_USUARIOS, 0x2)), sid)


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
    A ferramenta de tarefas escreve na tabela OEM do console: a resposta da peça é igual à resposta crua lida como OEM
    (no Windows em português: "ERRO: O sistema não pode encontrar..."; lida como ANSI, o "não" sai trocado)."""
    nome = "EditorImpressao\\Tarefa que nao existe do teste"
    r = windows.rodar_tarefa(nome)
    assert r.desfecho == windows.FALHOU
    cru = subprocess.run([str(Path(os.environ["SystemRoot"]) / "System32" / "schtasks.exe"), "/Run", "/TN", nome],
                         capture_output=True, creationflags=windows.CREATE_NO_WINDOW)
    assert r.dados["erros"] == cru.stderr.decode("oem").strip()
    if any(b > 127 for b in cru.stderr):                        # Windows em português: tem letra com acento
        assert cru.stderr.decode("cp1252", "replace").strip() != r.dados["erros"]


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
    assert r.desfecho == windows.FALHOU and "saiu sem começar" in r.motivo and "código" not in r.motivo
    assert "código 7" in r.detalhe and r.dados["codigo"] == 7


def test_lancar_powershell_solto_roda_e_apaga_a_propria_pasta(tmp_path):
    """O script lançado solto dá o sinal, roda (com acento) e apaga a própria pasta de troca no fim."""
    saida = tmp_path / "saida.txt"

    def trocas() -> set:
        """As pastas de troca que existem agora."""
        mae = Path(os.environ["LOCALAPPDATA"]) / "EditorImpressao" / windows.NOME_DA_PASTA_MAE_DA_TROCA
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
    assert windows.problemas_da_pasta_segura(windows.ler_licencas(comuns)) == []
    pasta = windows.criar_pasta_de_troca()
    try:
        assert windows.problemas_da_pasta_segura(windows.ler_licencas(pasta))
    finally:
        windows.apagar_pasta_de_troca(pasta)
    le = windows.Licenca(windows.SID_USUARIOS, "", "permite", 0x1200A9, True, False)
    grava = windows.Licenca(windows.SID_USUARIOS, "", "permite", 0x1301BF, True, False)
    adm = windows.Licenca(windows.SID_ADMINISTRADORES, "", "permite", 0x1F01FF, True, False)
    base = windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False, (adm, le))
    assert windows.problemas_da_pasta_segura(base) == []
    assert windows.problemas_da_pasta_segura(windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False,
                                                               (adm, le, grava)))
    assert windows.problemas_da_pasta_segura(windows.Licencas("x", windows.SID_ADMINISTRADORES, "", False, False,
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


# ---------------------------------------------------------------------------------------------------------------------
# A volta de quem tentou quebrar (19/11): um teste por achado
# ---------------------------------------------------------------------------------------------------------------------

def test_a_peca_e_fechada_rodar_e_lancar_recusam_os_programas_com_funcao_propria(tmp_path):
    """Achado 12 (escolha técnica da gerente): o rodar e o lançar genéricos recusam os programas que têm função
    própria na peça (tarefas, licenças de pasta, PowerShell, pedido de licença, cmd...), com ou sem o caminho inteiro,
    em qualquer caixa de letra; nada roda. A regra é pela pasta do Windows: qualquer programa de lá é recusado
    (whoami, aqui), e os de fora com função própria (o atualizador do Velopack) também."""
    sistema = Path(os.environ["SystemRoot"]) / "System32"
    for programa in ("schtasks", str(sistema / "schtasks.exe"), "ICACLS.EXE", "cmd", "runas.exe", "reg",
                     str(sistema / "whoami.exe"), "whoami",
                     str(sistema / "WindowsPowerShell" / "v1.0" / "powershell.exe"), '"C:\\x\\Update.exe"'):
        r = windows.rodar_e_esperar([programa, "/?"])
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, programa
        sinal = tmp_path / "nao-pode.txt"
        r = windows.lancar_solto([programa, "/?"], sinal, espera_s=1)
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo and not sinal.exists(), programa
    assert windows.rodar_e_esperar([]).desfecho == windows.FALHOU
    assert windows.rodar_e_esperar([PY, "-c", "print('x')"], letras="utf-8").deu_certo


def test_a_peca_e_fechada_ninguem_usa_o_que_tem_sublinhado_fora_dela():
    """Achado 12: o que tem "_" no nome é de dentro da peça. Nenhum arquivo do projeto fora de core/windows.py (a
    janela de prova, os testes, o programa) usa ou importa um nome com "_" da peça."""
    proibido = re.compile(r"\bwindows\._[A-Za-z]|from\s+core\.windows\s+import\s+[^\n]*\b_[A-Za-z]")
    achados = []
    for arquivo in RAIZ.rglob("*.py"):
        partes = arquivo.relative_to(RAIZ).parts
        if partes[0] in (".venv", ".claude", "build", "dist", "saida_teste", "terceiros", "velhos") or \
                arquivo == RAIZ / "core" / "windows.py":
            continue
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        achados += [f"{arquivo.relative_to(RAIZ)}: {m.group(0)}" for m in proibido.finditer(texto)]
    assert achados == []


def test_o_script_falha_quando_um_programa_de_fora_falha():
    """Achado 10: um programa de fora que falha dentro do script (o PowerShell não para sozinho) dá "falhou" no fim
    do script; e `Confere-Comando` para o script na hora, com a frase de quem falhou. A resposta e o erro chegam
    separados (achado 11)."""
    r = windows.rodar_powershell("cmd /c exit 5\n[Console]::Out.Write('depois')")
    assert r.desfecho == windows.FALHOU and r.dados["codigo"] == 5
    assert r.dados["saida"] == "depois" and "código 5" in r.dados["erros"]
    r = windows.rodar_powershell("cmd /c exit 4\nConfere-Comando 'o cmd de teste'\n[Console]::Out.Write('nunca')")
    assert r.desfecho == windows.FALHOU and "o cmd de teste falhou (código 4)" in r.detalhe
    assert "nunca" not in r.dados["saida"]
    r = windows.rodar_powershell("[Console]::Error.Write('AVISO'); [Console]::Out.Write('{\"a\":1}')")
    assert r.deu_certo and r.dados["saida"] == '{"a":1}' and r.dados["erros"] == "AVISO"


def test_o_lado_com_licenca_recusa_a_pasta_onde_outra_conta_grava():
    """Achado 4: o programa com licença recusa uma pasta de troca onde outra conta (Todos) pode gravar, no lugar onde
    a regra age (`atender_trabalho_de_administrador`), e não escreve nada nela. A pasta é do próprio teste, dentro do
    projeto; a licença para Todos é posta só nela."""
    base = RAIZ / "saida_teste" / f"troca-aberta-{os.getpid()}-{time.time_ns()}"
    pasta = base / windows.NOME_DA_PASTA_MAE_DA_TROCA / (windows.PREFIXO_DA_TROCA + "aberta")
    pasta.mkdir(parents=True)
    try:
        aviso = {"formato": windows.FORMATO_DO_AVISO, "pedido_por": windows.sid_desta_conta(), "criado_em": "agora",
                 "passos": [{"tipo": "script", "descricao": "x", "dados": {"texto": "", "com_segredo": False,
                                                                         "limite_s": 10}}]}
        (pasta / windows.NOME_DO_AVISO).write_text(json.dumps(aviso), encoding="utf-8")
        subprocess.run([str(Path(os.environ["SystemRoot"]) / "System32" / "icacls.exe"), str(pasta), "/grant",
                        "*S-1-1-0:(OI)(CI)(M)"], check=True, capture_output=True)
        assert "outra conta pode gravar" in " ".join(
            windows.problemas_da_pasta_de_troca(windows.ler_licencas(pasta), windows.sid_desta_conta()))
        assert windows.atender_trabalho_de_administrador([str(pasta)]) == windows.SAIDA_PASTA_RECUSADA
        assert not (pasta / windows.NOME_DO_RELATORIO).exists()
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_o_lado_com_licenca_recusa_aviso_ligado_a_outro_arquivo():
    """Achado 13 (M10): o aviso que é uma ligação para outro arquivo (o mesmo conteúdo com dois nomes) é recusado."""
    pasta = _troca_com_aviso([{"tipo": "script", "descricao": "x", "dados": {"texto": "", "com_segredo": False,
                                                                             "limite_s": 10}}])
    try:
        os.link(pasta / windows.NOME_DO_AVISO, pasta / "outro-nome.json")
        assert windows.atender_trabalho_de_administrador([str(pasta)]) == windows.SAIDA_PASTA_RECUSADA
        assert not (pasta / windows.NOME_DO_RELATORIO).exists()
    finally:
        windows.apagar_pasta_de_troca(pasta)


def test_a_pasta_segura_que_nao_confere_e_apagada_de_novo_e_conferida(monkeypatch, tmp_path):
    """Achados 13 (M11) e 7: a pasta segura criada é conferida; se não confere (aqui, criada numa pasta do teste, onde
    a conta comum é dona e grava), a resposta é "falhou" e ela é apagada de novo, conferindo que sumiu. Arquivos de
    Programas é trocado só para o lugar (a criação e a conferência são as de verdade)."""
    monkeypatch.setattr(windows, "pasta_de_programas", lambda: tmp_path)
    r = windows.criar_pasta_segura(windows.NOME_DA_PASTA_SEGURA_DE_PROVA)
    assert r.desfecho == windows.FALHOU and "não confere" in r.motivo and "apagada de novo" in r.motivo
    assert r.dados["sobrou"] is False and not (tmp_path / windows.NOME_DA_PASTA_SEGURA_DE_PROVA).exists()


def test_a_tarefa_criada_que_nao_confere_e_apagada(monkeypatch):
    """Achados 13 (M12) e 5: depois de pedir a tarefa, a peça lê de volta; se o que o Windows tem não é o pedido, ela
    apaga a tarefa e confere que sumiu. A leitura da tarefa é trocada só para dizer, na primeira vez, que a tarefa
    ficou diferente; depois volta a ser a de verdade. SÓ no Windows do GitHub (com licença, uma máquina que é jogada
    fora): lá cria de verdade e a peça apaga, e o teste confere e tira a pasta do Agendador. No PC do Samuel não roda,
    nem num terminal com a licença ligada: nada de tarefa criada escondida (D-785; achado N4 de quem tentou quebrar).
    A conferência em si é provada sem o Windows em
    `test_a_licenca_da_tarefa_e_comparada_pelo_sentido_com_o_que_o_windows_devolve`."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        pytest.skip("só no Windows do GitHub: no PC do Samuel nenhuma tarefa é criada escondida (D-785)")
    nome = f"EditorImpressao\\Teste da peca {os.getpid()}"
    xml = windows.xml_da_tarefa_do_sistema("C:\\nao\\existe.exe", "", "teste da peça (pode apagar)",
                                           "D:(A;;FA;;;BA)(A;;FA;;;SY)")
    real = windows.ler_tarefa
    vezes = []

    def lida(n: str, limite_s: float = 60) -> windows.Tarefa:
        """Na primeira leitura, a tarefa "ficou diferente"; nas outras, a leitura de verdade."""
        vezes.append(n)
        if len(vezes) == 1:
            return windows.Tarefa(n, True, True, comando="C:\\outro.exe", usuario=windows.SID_SISTEMA,
                                  licenca="D:(A;;FA;;;BA)(A;;FA;;;SY)")
        return real(n, limite_s)

    existia = windows.pasta_de_tarefas_existe()
    monkeypatch.setattr(windows, "ler_tarefa", lida)
    r = windows.criar_tarefa(nome, xml)
    assert r.desfecho == windows.FALHOU and "apagada de novo" in r.motivo, r
    assert real(nome).existe is False
    if windows.tem_licenca_de_administrador() and existia is False:
        assert windows.apagar_pasta_de_tarefas().deu_certo
        assert windows.pasta_de_tarefas_existe() is False


def test_a_licenca_da_tarefa_e_comparada_pelo_sentido_com_o_que_o_windows_devolve():
    """Achado 5: o Agendador não devolve a licença como recebeu (acrescenta as herdadas e escreve "FRFX" como número).
    A comparação é pelo sentido, lendo pelo próprio Windows: o caso de verdade da tarefa de desfragmentar (lido em
    19/11) confere; uma conta que perde direitos, ou uma conta comum que ganha o de mudar, não conferem."""
    pedida = "D:AI(A;;FA;;;BA)(A;;FA;;;SY)(A;;FRFX;;;LS)(A;;FR;;;AU)"
    efetiva = ("D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;0x1200a9;;;LS)(A;;FR;;;AU)(A;ID;0x1f019f;;;BA)(A;ID;0x1f019f;;;SY)"
               "(A;ID;FR;;;AU)(A;ID;FR;;;LS)(A;ID;FR;;;NS)(A;ID;FA;;;SY)(A;;FR;;;SY)")
    assert windows.problemas_da_licenca_da_tarefa(pedida, efetiva) == []
    import atualizacao

    assert windows.problemas_da_licenca_da_tarefa(atualizacao.QUEM_PODE_MANDAR_RODAR,
                                                  "D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;0x1200a9;;;AU)") == []
    assert windows.problemas_da_licenca_da_tarefa(atualizacao.QUEM_PODE_MANDAR_RODAR,
                                                  "D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;FR;;;AU)")
    assert windows.problemas_da_licenca_da_tarefa("D:(A;;FA;;;BA)", "D:(A;;FA;;;BA)(A;;FA;;;BU)")
    lida = windows.Tarefa("EditorImpressao\\x", True, True, comando="C:\\a.exe", argumentos="",
                          usuario=windows.SID_SISTEMA, licenca="D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;0x1200a9;;;AU)")
    xml = windows.xml_da_tarefa_do_sistema("C:\\a.exe", "", "d", atualizacao.QUEM_PODE_MANDAR_RODAR)
    assert windows.problemas_da_tarefa_criada(xml, lida) == []
    assert windows.problemas_da_tarefa_criada(xml, windows.Tarefa("EditorImpressao\\x", True, True,
                                                                  comando="C:\\a.exe", usuario=windows.SID_SISTEMA))
    sem_rodar = windows.Tarefa("EditorImpressao\\x", True, True, comando="C:\\a.exe", argumentos="",
                               usuario=windows.SID_SISTEMA, licenca="D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;FR;;;AU)")
    assert "direitos pedidos" in " ".join(windows.problemas_da_tarefa_criada(xml, sem_rodar))


def test_a_pasta_do_programa_no_agendador_e_lida_sem_licenca():
    """Achado 6: a peça lê se a pasta do programa existe no Agendador (True ou False), e o passo de apagá-la (só
    vazia) é aceito pelas regras."""
    from dataclasses import asdict

    assert windows.pasta_de_tarefas_existe() in (True, False)
    assert windows.problemas_do_passo(asdict(windows.passo_apagar_pasta_de_tarefas())) == []


def test_o_desfazer_vai_ate_o_fim_mesmo_com_um_passo_que_falha():
    """Achado 1 (o desfazer da pergunta 3): com "ate_o_fim", um passo que falha não impede os seguintes. Sem a
    licença (o PC do Samuel), o trabalho é recusado antes; com a licença (o Windows do GitHub), o primeiro script
    falha e o segundo roda mesmo assim, e o relatório diz os dois."""
    pasta = windows.criar_pasta_de_troca()
    marca = pasta / "o-segundo-rodou.txt"
    passos = [{"tipo": "script", "descricao": "falha de propósito", "dados": {"texto": "throw 'x'",
                                                                            "com_segredo": False, "limite_s": 60}},
              {"tipo": "script", "descricao": "roda mesmo assim",
               "dados": {"texto": f"[System.IO.File]::WriteAllText('{marca}', 'sim')", "com_segredo": False,
                         "limite_s": 60}}]
    aviso = {"formato": windows.FORMATO_DO_AVISO, "pedido_por": windows.sid_desta_conta(), "criado_em": "agora",
             "ate_o_fim": True, "passos": passos}
    (pasta / windows.NOME_DO_AVISO).write_text(json.dumps(aviso), encoding="utf-8")
    try:
        codigo = windows.atender_trabalho_de_administrador([str(pasta)])
        relatorio = json.loads((pasta / windows.NOME_DO_RELATORIO).read_text(encoding="utf-8"))
        if windows.tem_licenca_de_administrador():
            assert codigo == windows.SAIDA_UM_PASSO_FALHOU
            assert [p["resultado"] for p in relatorio["passos"]] == [windows.FALHOU, windows.DEU_CERTO]
            assert marca.read_text(encoding="utf-8") == "sim"
        else:
            assert codigo == windows.SAIDA_SEM_LICENCA and not marca.exists()
    finally:
        windows.apagar_pasta_de_troca(pasta)


# ---------------------------------------------------------------------------------------------------------------------
# A segunda volta de quem tentou quebrar (19/11)
# ---------------------------------------------------------------------------------------------------------------------

def test_as_bibliotecas_da_peca_guardam_o_erro_de_cada_chamada():
    """N1 (etapa 5, defeito 2): cada biblioteca do Windows da peça guarda o erro da chamada, em especial a shell32,
    que lê o "Não" da pergunta do Windows; o jeito antigo (`ctypes.windll`) não guarda. Pela função pública de
    conferência da peça (nada de dentro dela)."""
    guardam = windows.bibliotecas_guardam_o_erro()
    assert set(guardam) == {"kernel32", "advapi32", "shell32", "user32", "ole32", "crypt32"}
    assert guardam["shell32"] is True and all(guardam.values()), guardam
    assert not ctypes.windll.shell32._FuncPtr._flags_ & getattr(ctypes, "_FUNCFLAG_USE_LASTERROR", 0x10)


def test_a_recusa_vale_para_o_caminho_escrito_de_outro_jeito():
    """N2: o mesmo programa da pasta do Windows escrito de outro jeito também é recusado: com o prefixo de caminho
    longo ou de dispositivo, por caminho de rede (o "C$" e o "ADMIN$" do próprio computador, ou qualquer outro), com
    barra normal ou com "..". Programa de fora do Windows passa."""
    barra = chr(92)
    for caminho in (barra * 2 + "?" + barra + "C:" + barra + "Windows" + barra + "System32" + barra + "schtasks.exe",
                    barra * 2 + "." + barra + "C:" + barra + "Windows" + barra + "System32" + barra + "cmd.exe",
                    barra * 2 + "localhost" + barra + "C$" + barra + "Windows" + barra + "System32" + barra + "schtasks.exe",
                    barra * 2 + "127.0.0.1" + barra + "ADMIN$" + barra + "System32" + barra + "schtasks.exe",
                    barra * 2 + "?" + barra + "UNC" + barra + "localhost" + barra + "C$" + barra + "x.exe",
                    barra * 2 + "outro-computador" + barra + "pasta" + barra + "programa.exe",
                    "C:/Windows/System32/whoami.exe",
                    "C:" + barra + "Windows" + barra + ".." + barra + "Windows" + barra + "System32" + barra + "whoami.exe"):
        r = windows.rodar_e_esperar([caminho, "/?"])
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, caminho
    assert windows.rodar_e_esperar([PY, "-c", "print(1)"], letras="utf-8").deu_certo
    # o prefixo de caminho longo sai antes de comparar: um programa de fora do Windows escrito com ele continua passando
    assert windows.rodar_e_esperar([barra * 2 + "?" + barra + PY, "-c", "print(1)"], letras="utf-8").deu_certo


# Licenças de pastas do Agendador lidas neste PC em 19/11 (só leitura). A "de fábrica" é a que uma pasta criada por
# administrador herda da raiz; a "da conta comum" é uma pasta que a conta comum criou e deu a "Todos".
_PASTA_DE_FABRICA = ("O:BAD:AI(A;CIID;FA;;;BA)(A;OIIOID;0x1f019f;;;BA)(A;CIID;FA;;;SY)(A;OIIOID;0x1f019f;;;SY)"
                     "(A;CIID;FW;;;AU)(A;CIID;FW;;;NS)(A;CIID;FW;;;LS)(A;OICIIOID;FA;;;CO)")
_PASTA_DA_CONTA_COMUM = ("O:S-1-5-21-1-2-3-1001D:AI(A;;FA;;;WD)(A;CIID;FA;;;BA)(A;OIIOID;0x1f019f;;;BA)(A;CIID;FA;;;SY)"
                         "(A;OIIOID;0x1f019f;;;SY)(A;CIID;FW;;;AU)(A;ID;FA;;;S-1-5-21-1-2-3-1001)(A;OICIIOID;FA;;;CO)")


def test_a_pasta_do_agendador_tem_de_ser_do_sistema_ou_dos_administradores():
    """N3: a pasta do programa no Agendador com as licenças de fábrica passa; criada antes por uma conta comum (dona),
    ou dando controle total a "Todos", ou passando para as tarefas o direito de uma conta comum gravar, não passa."""
    assert windows.problemas_da_pasta_de_tarefas(_PASTA_DE_FABRICA) == []
    problemas = windows.problemas_da_pasta_de_tarefas(_PASTA_DA_CONTA_COMUM)
    assert "o dono da pasta do programa no Agendador é outra conta deste computador" in problemas[0]
    assert "Todos podem mexer na pasta do programa no Agendador" in problemas
    assert "outra conta deste computador pode mexer na pasta do programa no Agendador" in problemas
    assert windows.problemas_da_pasta_de_tarefas("O:BAD:(A;;FA;;;BA)(A;OI;FW;;;AU)")          # passa para as tarefas
    assert windows.problemas_da_pasta_de_tarefas("O:BAD:(A;;FA;;;BA)(A;;WD;;;BU)")            # muda a licença
    assert windows.conferir_pasta_de_tarefas().dados.get("existe") in (True, False)


def test_a_tarefa_nao_e_criada_numa_pasta_do_agendador_que_nao_e_segura(monkeypatch):
    """N3: se a pasta do programa no Agendador já existe e não é segura, a peça recusa ANTES de pedir a tarefa ao
    Windows, com o aviso em português, e nada é criado. A leitura da pasta é trocada só para dizer que ela existe e
    não confere."""
    nome = f"EditorImpressao\\Teste da pasta insegura {os.getpid()}"
    monkeypatch.setattr(windows, "pasta_de_tarefas_existe", lambda: True)
    monkeypatch.setattr(windows, "conferir_pasta_de_tarefas", lambda: windows.Resposta(
        windows.FALHOU, "a pasta do programa no Agendador não é segura: Todos podem mexer"))
    xml = windows.xml_da_tarefa_do_sistema("C:\\nao\\existe.exe", "", "teste", "D:(A;;FA;;;BA)(A;;FA;;;SY)")
    r = windows.criar_tarefa(nome, xml)
    assert r.desfecho == windows.FALHOU and "não é segura" in r.motivo and "não foi criada" in r.motivo
    assert windows.ler_tarefa(nome).existe is False


def test_a_pasta_de_troca_fica_so_quando_o_trabalho_pode_continuar():
    """Mutação A9 da segunda volta: a pasta de troca fica depois do tempo esgotado ou sem dar para acompanhar (o
    trabalho com licença ainda pode estar usando); em todos os outros casos, ela é apagada."""
    assert windows.manter_a_pasta_de_troca("tempo") and windows.manter_a_pasta_de_troca("sem_acompanhar")
    for houve in ("terminou", "nao", "erro:2", "erro:5"):
        assert not windows.manter_a_pasta_de_troca(houve), houve


def test_apagar_a_pasta_do_agendador_confere_que_sumiu(monkeypatch):
    """Mutação A6b da segunda volta: depois de pedir para apagar a pasta do programa no Agendador, a peça confere que
    ela sumiu; se a leitura ainda diz que existe, é "falhou". Só roda quando a pasta de verdade não existe (o pedido de
    apagar não acha nada para apagar); a leitura é trocada para dizer sempre que existe."""
    if windows.pasta_de_tarefas_existe() is not False:
        pytest.skip("a pasta do programa existe neste Windows: o teste não pede para apagá-la")
    monkeypatch.setattr(windows, "pasta_de_tarefas_existe", lambda: True)
    assert windows.apagar_pasta_de_tarefas().desfecho == windows.FALHOU


def test_as_frases_da_peca_dizem_as_contas_em_portugues_e_nunca_o_numero():
    """As contas de fábrica são ditas pela peça em português a partir do número delas (o Windows traduz o nome: "Todos"
    aqui, "Everyone" no Windows do GitHub, em inglês); conta sem nome é "outra conta deste computador"; nenhuma frase
    mostra o número cru (S-1-...). Vale para a pasta de troca, a pasta segura, o Agendador e a licença da tarefa."""
    assert windows.nome_para_mostrar("S-1-1-0", "Everyone") == "Todos"
    assert windows.nome_para_mostrar(windows.SID_USUARIOS, "BUILTIN\\Users") == "Usuários"
    assert windows.nome_para_mostrar(windows.SID_AUTENTICADOS) == "Usuários autenticados"
    assert windows.nome_para_mostrar(windows.SID_SISTEMA) == "o sistema"
    assert windows.nome_para_mostrar(windows.SID_ADMINISTRADORES) == "Administradores"
    assert windows.nome_para_mostrar("S-1-5-21-1-2-3-1001") == "outra conta deste computador"
    assert windows.nome_para_mostrar("S-1-5-21-1-2-3-1001", "PC\\kaique") == "kaique"     # sem o computador
    sid = "S-1-5-21-1-2-3-1001"

    def lic(dono: str, *linhas) -> windows.Licencas:
        """Licenças montadas."""
        return windows.Licencas("x", dono, "", False, False, tuple(linhas))

    def linha(quem: str, mascara: int) -> windows.Licenca:
        """Uma linha montada, sem o nome do Windows."""
        return windows.Licenca(quem, "", "permite", mascara, True, False)

    frases = (windows.problemas_da_pasta_de_troca(lic("S-1-5-21-9-9-9-1002", linha("S-1-1-0", 0x1F01FF),
                                                      linha(windows.SID_USUARIOS, 0x120089)), sid)
              + windows.problemas_da_pasta_segura(lic(sid, linha(windows.SID_USUARIOS, 0x1301BF)))
              + windows.problemas_da_pasta_de_tarefas(_PASTA_DA_CONTA_COMUM)
              + windows.problemas_da_licenca_da_tarefa("D:(A;;FA;;;BA)(A;;GRGX;;;AU)", "D:(A;;FA;;;BA)(A;;FA;;;WD)")
              + lic(sid, linha("S-1-1-0", 0x1F01FF)).para_mostrar())
    assert frases and not [f for f in frases if "S-1-" in f], frases
    assert "outra conta pode gravar na pasta: Todos" in frases
    assert "outra conta pode ler a pasta: Usuários" in frases
    assert "uma conta que não é administradora pode gravar na pasta: Usuários" in frases
    assert "Usuários autenticados não ficaram com os direitos pedidos na tarefa" in frases
    assert "Todos podem mudar a tarefa" in frases


# ---------------------------------------------------------------------------------------------------------------------
# A terceira volta de quem tentou quebrar (19/11)
# ---------------------------------------------------------------------------------------------------------------------

def test_a_recusa_resolve_o_caminho_inteiro_antes_de_tirar_o_prefixo():
    """T1: o caminho com o prefixo longo é resolvido inteiro antes de perder o prefixo: pela "raiz global" e pelo
    "volume por número" (o do disco C: deste Windows), a ferramenta do Windows também é recusada. Programa de fora
    escrito com o prefixo continua passando."""
    from ctypes import wintypes

    barra = chr(92)
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.GetVolumeNameForVolumeMountPointW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    disco = os.environ["SystemRoot"][:3]                                      # "C:" e a barra
    volume = ctypes.create_unicode_buffer(100)
    assert k.GetVolumeNameForVolumeMountPointW(disco, volume, 100), "o Windows não disse o volume do disco do sistema"
    for caminho in (barra * 2 + "?" + barra + "GLOBALROOT" + barra + "SystemRoot" + barra + "System32" + barra
                    + "schtasks.exe",
                    volume.value + "Windows" + barra + "System32" + barra + "schtasks.exe",
                    barra * 2 + "?" + barra + "GLOBALROOT" + barra + "Device" + barra + "Coisa" + barra + "x.exe",
                    barra * 2 + "." + barra + "pipe" + barra + "programa.exe"):       # não vira letra de disco
        r = windows.rodar_e_esperar([caminho, "/?"])
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, caminho
    assert windows.rodar_e_esperar([barra * 2 + "?" + barra + PY, "-c", "print(1)"], letras="utf-8").deu_certo
    # o mesmo programa de fora pelo "volume por número" do disco dele: a peça não o recusa, porque o caminho é resolvido
    # inteiro (sem resolver, ele seria recusado); quem não o roda é o próprio Windows, que não abre programa por esse
    # caminho ("parâmetro incorreto"): a resposta é "falhou", mas não a recusa da peça.
    volume_do_python = ctypes.create_unicode_buffer(100)
    assert k.GetVolumeNameForVolumeMountPointW(PY[:3], volume_do_python, 100)
    r = windows.rodar_e_esperar([volume_do_python.value + PY[3:], "-c", "print(1)"], letras="utf-8")
    assert "função própria" not in r.motivo, r


def test_a_tarefa_numa_pasta_do_agendador_que_mudou_no_meio_e_apagada(monkeypatch):
    """T2: a pasta do programa no Agendador não existia antes e, depois de criar a tarefa, não é segura (mudou entre
    as duas conferências): a peça apaga a tarefa de novo, confere que sumiu e a resposta diz isso. SÓ no Windows do
    GitHub (com licença, máquina jogada fora): lá a tarefa é criada de verdade; a segunda leitura da pasta é trocada
    para dizer que ela não é segura. No PC do Samuel não roda: nenhuma tarefa criada escondida (D-785)."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        pytest.skip("só no Windows do GitHub: no PC do Samuel nenhuma tarefa é criada escondida (D-785)")
    nome = f"EditorImpressao\\Teste da pasta que mudou {os.getpid()}"
    import atualizacao

    xml = windows.xml_da_tarefa_do_sistema("C:\\nao\\existe.exe", "", "teste da peça (pode apagar)",
                                           atualizacao.QUEM_PODE_MANDAR_RODAR)
    existia = windows.pasta_de_tarefas_existe()
    real = windows.conferir_pasta_de_tarefas
    leituras = []

    def conferir() -> windows.Resposta:
        """A leitura antes é a de verdade; a de depois de criar diz que a pasta não é segura."""
        leituras.append(1)
        if len(leituras) == 1 and existia is not False:
            return real()
        return windows.Resposta(windows.FALHOU, "a pasta do programa no Agendador não é segura: Todos podem mexer")

    monkeypatch.setattr(windows, "conferir_pasta_de_tarefas", conferir)
    r = windows.criar_tarefa(nome, xml)
    assert r.desfecho == windows.FALHOU and "não é segura" in r.motivo and "apagada de novo" in r.motivo, r
    assert windows.ler_tarefa(nome).existe is False
    if existia is False:
        assert windows.apagar_pasta_de_tarefas().deu_certo


def test_as_frases_concordam_e_nao_levam_numero_do_windows():
    """T3: o verbo concorda com a conta ("Todos podem", "Administradores podem", "fotog pode"); as contas de fábrica
    fora das mais comuns também saem em português pelo número (Convidados, os serviços, o administrador embutido),
    venha o nome do Windows em que língua vier; e as frases que a pessoa lê não levam o número do erro do Windows (ele
    fica no técnico)."""
    barra = chr(92)
    assert windows.frase_da_conta("S-1-1-0", "Everyone", "pode x", "podem x") == "Todos podem x"
    assert windows.frase_da_conta(windows.SID_ADMINISTRADORES, "", "pode x", "podem x") == "Administradores podem x"
    assert windows.frase_da_conta("S-1-5-21-1-2-3-1001", "PC" + barra + "fotog", "pode x", "podem x") == "fotog pode x"
    assert windows.nome_para_mostrar("S-1-5-32-546", "BUILTIN" + barra + "Guests") == "Convidados"
    assert windows.nome_para_mostrar("S-1-5-80-1-2-3-4-5", "NT SERVICE" + barra + "Algo") == "um serviço do Windows"
    assert windows.nome_para_mostrar("S-1-5-21-1-2-3-500", "PC" + barra + "Administrator") == \
        "o administrador embutido do Windows"
    r = windows.rodar_e_esperar([PY, "-c", "raise SystemExit(3)"], letras="utf-8")
    assert "código" not in r.motivo and "0x" not in r.motivo and "código 3" in r.detalhe
    assert "código" not in windows.desfecho_do_trabalho(
        1, {"passos": [{"descricao": "a", "resultado": windows.DEU_CERTO}], "terminou": True, "recusado": ""}).motivo
    for erro in (2, 3, 5, 1155, 1460):
        assert "código" not in windows.resposta_do_pedido(f"erro:{erro}", None, "t", None, [], 60).motivo



# ---------------------------------------------------------------------------------------------------------------------
# A assinatura digital de um arquivo (passo 2 do plano: o PowerShell do empacotar passa pela peça)
# ---------------------------------------------------------------------------------------------------------------------

def test_a_assinatura_digital_e_lida_pela_peca_de_verdade(tmp_path):
    """Passo 2 (lista de exceções, K01): o publicar lia a assinatura digital do Visual C++ abrindo o PowerShell por
    conta própria (`empacotar.assinatura_do_arquivo`). Agora a peça tem a função própria (`ler_assinatura_digital`),
    que roda de verdade, sem pergunta do Windows: um programa assinado pela Microsoft (o próprio PowerShell do Windows)
    dá "Valid" com o assinante da Microsoft; um script sem assinatura dá "NotSigned"; um arquivo que não existe dá
    FALHOU (nunca um "não assinado" inventado), com a frase em português."""
    powershell_do_windows = windows.pasta_do_sistema() / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    assinado = windows.ler_assinatura_digital(powershell_do_windows)
    assert assinado.deu_certo, assinado
    assert assinado.dados["status"] in ("Valid", "NotTrusted", "UnknownError"), assinado.dados
    assert "Microsoft" in assinado.dados["assinante"] or assinado.dados["status"] != "Valid", assinado.dados
    falso = tmp_path / "sem assinatura, com acento ção.ps1"     # script sem assinatura: o Windows diz NotSigned
    falso.write_text("Write-Output 'oi'", encoding="utf-8")
    sem = windows.ler_assinatura_digital(falso)
    assert sem.deu_certo and sem.dados["status"] == "NotSigned", sem
    assert sem.dados["assinante"] == ""
    nada = windows.ler_assinatura_digital(tmp_path / "nao-existe.exe")
    assert nada.desfecho == windows.FALHOU and nada.motivo and "código" not in nada.motivo, nada


def test_o_empacotar_le_a_assinatura_pela_peca_e_nao_abre_o_powershell(tmp_path, monkeypatch):
    """Passo 2: `empacotar.assinatura_do_arquivo` chama a função da peça (um lugar só) e não abre nenhum programa por
    conta própria. Falha da peça vira "erro: <motivo>" (o mesmo formato de antes), que nunca confere."""
    import empacotar

    rodou = []
    monkeypatch.setattr(empacotar.subprocess, "run", lambda *a, **k: rodou.append(a))
    pedidos = []

    def ler(arquivo):
        """A peça de mentira só para ver que é ela que o empacotar chama (o teste de cima roda a de verdade)."""
        pedidos.append(Path(arquivo))
        return windows.Resposta(windows.FALHOU, "o arquivo sumiu", "teste")

    monkeypatch.setattr(windows, "ler_assinatura_digital", ler)
    lido = empacotar.assinatura_do_arquivo(tmp_path / "x.exe")
    assert pedidos == [tmp_path / "x.exe"] and rodou == []
    assert lido["status"].startswith("erro: ") and empacotar.vc_redist_confere(lido)


def test_o_powershell_nao_herda_os_modulos_do_powershell_7(tmp_path, monkeypatch):
    """Bug de 19/11/2026 (achado na rodada 44642471223 do GitHub, passo 2): no Windows do GitHub o Python roda dentro do
    PowerShell 7, e o PowerShell do Windows aberto pela peça herdava a lista de pastas de módulos dele (PSModulePath);
    o "Get-AuthenticodeSignature" falhava ("CouldNotAutoloadMatchingModule") e a assinatura do Visual C++ nunca era
    lida (o teste antigo do empacotar não via: erro também "não confere"). A Microsoft documenta o caso
    (about_PSModulePath, 5.1: "Inherited PowerShell 7 module paths precede the Windows PowerShell system module path
    [...] This breaks module autoloading"). Agora a peça abre o PowerShell sem a lista herdada (ele monta a de fábrica).
    Aqui o caso é refeito no PC: uma pasta de módulos na frente da lista, com um módulo de segurança que o PowerShell
    do Windows não consegue carregar; o rodar e o lançar solto da peça continuam funcionando."""
    falso = tmp_path / "Modulos7" / "Microsoft.PowerShell.Security"
    falso.mkdir(parents=True)
    (falso / "Microsoft.PowerShell.Security.psd1").write_text(
        "@{ ModuleVersion = '7.0.0.0'; RootModule = 'quebrado.psm1'; "
        "FunctionsToExport = @('Get-AuthenticodeSignature'); CmdletsToExport = @() }", encoding="utf-8")
    (falso / "quebrado.psm1").write_text("throw 'este modulo nao carrega no Windows PowerShell'", encoding="utf-8")
    monkeypatch.setenv("PSModulePath", f"{tmp_path / 'Modulos7'};{os.environ.get('PSModulePath', '')}")
    powershell_do_windows = windows.pasta_do_sistema() / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    lido = windows.ler_assinatura_digital(powershell_do_windows)
    assert lido.deu_certo and lido.dados["status"], lido
    saida = tmp_path / "solto.txt"
    r = windows.lancar_powershell_solto(
        f"$s = Get-AuthenticodeSignature -LiteralPath {windows.aspas_do_powershell(powershell_do_windows)}\n"
        f"[System.IO.File]::WriteAllText({windows.aspas_do_powershell(saida)}, [string]$s.Status)\n"
        # espera um pouco antes de sair: um script que termina antes de a peça ver o sinal é dado como "saiu sem
        # começar" (o fim do script apaga a pasta com o sinal); defeito do lançar solto anotado para a Lista de bugs
        "[System.Threading.Thread]::Sleep(2000)")
    assert r.deu_certo, r
    for _ in range(100):
        if saida.exists():
            break
        time.sleep(0.1)
    assert saida.exists() and saida.read_text(encoding="utf-8-sig").strip(), "o lançado solto não leu a assinatura"


def test_o_lancado_solto_apaga_a_pasta_de_troca_sem_seguir_atalho(tmp_path):
    """D-809 (Samuel, 19/11: "ok"; o atalho de pasta só sai sem levar o que está do outro lado): o script lançado solto
    apaga a própria pasta de troca no fim. Antes ele usava o apagar recursivo do PowerShell, que, no PowerShell do
    Windows, entra num atalho (junção) que esteja dentro da pasta e apaga o que está do outro lado (o mesmo desenho
    do caso da pasta modelos/ esvaziada em 18/11). Agora ele confere cada item: atalho sai só ele (o Windows tira só a
    junção, RemoveDirectory), o resto é apagado. Aqui o próprio script põe na pasta de troca um atalho para uma pasta
    de verdade com um arquivo; depois do fim, a pasta de troca sumiu e o arquivo do outro lado continua."""
    alvo = tmp_path / "pasta de verdade"
    alvo.mkdir()
    (alvo / "importante.txt").write_text("fica", encoding="utf-8")
    sinal = tmp_path / "pasta-de-troca.txt"
    copia = tmp_path / "o-script-lancado.ps1"
    r = windows.lancar_powershell_solto(
        "New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot 'atalho') "
        f"-Target {windows.aspas_do_powershell(alvo)} | Out-Null\n"
        f"[System.IO.File]::Copy($PSCommandPath, {windows.aspas_do_powershell(copia)}, $true)\n"
        f"[System.IO.File]::WriteAllText({windows.aspas_do_powershell(sinal)}, $PSScriptRoot)\n"
        "[System.Threading.Thread]::Sleep(1500)")
    assert r.deu_certo, r
    for _ in range(150):
        if sinal.exists() and not Path(sinal.read_text(encoding="utf-8-sig").strip()).exists():
            break
        time.sleep(0.1)
    troca = Path(sinal.read_text(encoding="utf-8-sig").strip())
    assert not troca.exists(), "a pasta de troca tinha de ser apagada"
    assert (alvo / "importante.txt").is_file(), "o apagar entrou no atalho e apagou o que estava do outro lado"
    # O jeito antigo (o apagar recursivo do PowerShell) não entrou no atalho NESTE Windows (conferido em 19/11), mas o
    # comportamento muda com a versão e a Microsoft avisa do "known issue" do -Recurse: o que o teste cobra para não
    # voltar é o script lançado não usar o apagar recursivo e conferir o atalho antes (o que o porteiro também acusa).
    lancado = copia.read_text(encoding="utf-8-sig")
    assert "-Recurse" not in lancado and "ReparsePoint" in lancado, lancado


def test_o_lancado_solto_curto_nunca_vira_saiu_sem_comecar():
    """Bug de 19/11/2026 (anotado no passo 2 e medido por quem tentou quebrar: 4 de 15 com um script vazio): o script
    lançado solto dava o sinal de vida DENTRO da pasta que ele mesmo apaga no fim; um script curto apagava o sinal antes
    de a peça olhar, e a peça dizia "o processo lançado saiu sem começar" de uma coisa que rodou (quem tentasse de novo
    faria a coisa duas vezes). Agora o sinal fica numa pasta de troca à parte, que só a peça apaga depois de ver. A
    falha era de tempo: o teste lança 20 vezes um script vazio, e todas têm de dar certo."""
    falhas = [r for r in (windows.lancar_powershell_solto("") for _ in range(20)) if not r.deu_certo]
    assert falhas == [], f"{len(falhas)} de 20: {falhas[0]}"


_PAI_E_FILHO = r'''
import subprocess, sys, time
from pathlib import Path
pasta = Path(sys.argv[1])
if sys.argv[2] == "pai":
    subprocess.Popen([sys.executable, __file__, str(pasta), "filho"])
import os
n = 0
while True:
    n += 1
    provisorio = pasta / (sys.argv[2] + ".tmp")
    provisorio.write_text(str(n))
    try:
        os.replace(provisorio, pasta / (sys.argv[2] + ".txt"))
    except OSError:
        pass
    time.sleep(0.1)
'''


def _ainda_vive(arquivo: Path, espera_s: float = 1.5) -> bool:
    """O processo que escreve neste arquivo a cada 0,1 s ainda escreve?"""
    def ler() -> str:
        """O número escrito agora (vazio se não deu para ler)."""
        try:
            return arquivo.read_text()
        except OSError:
            return ""

    antes = ler()
    time.sleep(espera_s)
    return ler() not in ("", antes)


def test_fechar_o_programa_em_grupo_fecha_tambem_o_que_ele_abriu(tmp_path):
    """Passo 2, achado 2 de quem tentou quebrar: a vigia do espaço fechava o vpk e deixava o programa que ele abre para
    fazer o .msi (cmd.exe e wix.exe) escrevendo no C:. Agora o programa roda num grupo do Windows (`abrir_em_grupo`), e
    `fechar_tudo` fecha ele e tudo o que ele abriu, e confere no Windows que nenhum ficou vivo. De verdade: um processo
    abre outro; os dois escrevem num arquivo a cada 0,1 s; depois de fechar, nenhum escreve mais."""
    script = tmp_path / "pai_e_filho.py"
    script.write_text(_PAI_E_FILHO, encoding="utf-8")
    programa, r = windows.abrir_em_grupo([PY, str(script), str(tmp_path), "pai"])
    assert r.deu_certo and programa is not None, r
    with programa:
        for _ in range(100):
            if (tmp_path / "filho.txt").exists():
                break
            time.sleep(0.1)
        assert _ainda_vive(tmp_path / "filho.txt", 0.5) and programa.vivos() >= 2   # o python do .venv abre outro
        fechado = programa.fechar_tudo()
        assert fechado.deu_certo, fechado
        assert programa.vivos() == 0
    assert not _ainda_vive(tmp_path / "pai.txt") and not _ainda_vive(tmp_path / "filho.txt")
    recusado, r = windows.abrir_em_grupo([str(windows.pasta_do_sistema() / "cmd.exe"), "/c", "exit"])
    assert recusado is None and r.desfecho == windows.FALHOU, "o grupo também recusa programa com função própria"


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 3 (relatório 2 de quem tentou quebrar, 19/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

def test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo(tmp_path, monkeypatch):
    """Achado 3 do relatório 2 de quem tentou quebrar (19/11/2026, família F2, "o vizinho passa"): a peça fechada
    recusava os programas da pasta do Windows, mas um arquivo .bat ou .cmd de fora dela passava, e o Windows o rodava
    pelo C:\\Windows\\System32\\cmd.exe (o próprio CreateProcess entrega o lote ao cmd.exe; documentação do subprocess:
    "batch files (*.bat or *.cmd) may be launched by the operating system in a system shell"). Agora o rodar genérico,
    o lançar solto e o grupo recusam pela MESMA regra o que não é programa do Windows de verdade: a extensão depois de
    o Windows completar o caminho, e o começo do arquivo ("MZ"). De verdade: o lote escreveria um arquivo; nada é
    escrito. Os jeitos de escrever: maiúscula, ponto e espaço no fim (o Windows tira), o prefixo de caminho longo, o
    fluxo de dados (::$DATA), só o nome (pela pasta atual) e um lote com o nome de .exe."""
    marca = tmp_path / "o-lote-rodou.txt"
    lote = f'@echo %COMSPEC%> "{marca}"\r\n'
    for nome in ("x.bat", "y.cmd", "Z.BAT", "disfarcado.exe"):
        (tmp_path / nome).write_text(lote, encoding="ascii")
    jeitos = [str(tmp_path / "x.bat"), str(tmp_path / "y.cmd"), str(tmp_path / "Z.BAT"), str(tmp_path / "x.bat") + ".",
              str(tmp_path / "x.bat") + " ", "\\\\?\\" + str(tmp_path / "y.cmd"), str(tmp_path / "x.bat") + "::$DATA",
              str(tmp_path / "disfarcado.exe"), "x.bat", "y.cmd"]
    monkeypatch.chdir(tmp_path)
    for jeito in jeitos:
        r = windows.rodar_e_esperar([jeito])
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, (jeito, r)
        r = windows.lancar_solto([jeito], tmp_path / "sinal.txt", espera_s=1)
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, (jeito, r)
        programa, r = windows.abrir_em_grupo([jeito])
        assert programa is None and "função própria" in r.motivo, (jeito, r)
    time.sleep(0.5)
    assert not marca.exists(), "um arquivo de lote rodou pelo cmd.exe: " + marca.read_text(errors="replace")
    # o programa de verdade continua passando (a recusa não pega o que não devia)
    assert windows.rodar_e_esperar([PY, "-c", "print(1)"], letras="utf-8").deu_certo
    assert "não achei" in windows.rodar_e_esperar(["C:\\nao\\existe.exe"]).motivo


# Um pai que abre um filho logo ao começar; os dois anotam o número do processo e escrevem uma batida a cada 0,1 s, e
# saem sozinhos depois de 20 s (se algum escapar do grupo num teste, não fica rodando para sempre).
_PAI_E_FILHO_QUE_ACABA = r'''
import os, subprocess, sys, time
from pathlib import Path
pasta, papel = Path(sys.argv[1]), sys.argv[2]
if papel == "pai":
    subprocess.Popen([sys.executable, __file__, str(pasta), "filho"])
(pasta / (papel + ".pid")).write_text(str(os.getpid()))
fim = time.monotonic() + 20
n = 0
while time.monotonic() < fim:
    n += 1
    provisorio = pasta / (papel + ".tmp")
    provisorio.write_text(str(n))
    try:
        os.replace(provisorio, pasta / (papel + ".txt"))
    except OSError:
        pass
    time.sleep(0.1)
'''


def _esperar(arquivo: Path, limite_s: float = 20) -> None:
    """Espera o arquivo aparecer (o processo começou)."""
    fim = time.monotonic() + limite_s
    while not arquivo.exists() and time.monotonic() < fim:
        time.sleep(0.1)


def _fechar_o_que_sobrou(pasta: Path) -> None:
    """Fecha, pelo número anotado, os processos de teste que escaparam (só os deste teste)."""
    for pid in pasta.glob("*.pid"):
        try:
            os.kill(int(pid.read_text()), 9)
        except (OSError, ValueError):
            pass


def test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo(tmp_path, monkeypatch):
    """Achado 4 do relatório 2 de quem tentou quebrar (19/11/2026, família F5): o programa era aberto já rodando e
    posto no grupo depois; um filho aberto nesse instante ficava fora do grupo, e o `fechar_tudo` dizia "fechados
    (conferido)" com ele vivo. Agora ele nasce parado, entra no grupo, a peça confere que entrou e só então o solta. De
    verdade: o instante entre abrir o programa e pô-lo no grupo é aumentado de propósito em 3 s (o abrir do Python
    demora 3 s a mais para devolver; mais que o Python leva para abrir o filho); mesmo assim o filho nasce dentro do
    grupo e o `fechar_tudo` fecha os dois."""
    verdadeiro = subprocess.Popen

    class PopenQueDemora(verdadeiro):
        """O abrir de sempre, que só devolve 3 s depois (o instante de antes, aumentado)."""

        def __init__(self, *argumentos, **opcoes):
            super().__init__(*argumentos, **opcoes)
            time.sleep(3)

    script = tmp_path / "pai_e_filho.py"
    script.write_text(_PAI_E_FILHO_QUE_ACABA, encoding="utf-8")
    monkeypatch.setattr(windows.subprocess, "Popen", PopenQueDemora)
    try:
        programa, r = windows.abrir_em_grupo([PY, str(script), str(tmp_path), "pai"])
        monkeypatch.setattr(windows.subprocess, "Popen", verdadeiro)
        assert r.deu_certo and programa is not None, r
        with programa:
            _esperar(tmp_path / "filho.txt")
            assert _ainda_vive(tmp_path / "filho.txt", 0.5), "o filho não começou"
            fechado = programa.fechar_tudo()
            assert fechado.deu_certo and "conferido" in fechado.motivo, fechado
            assert not _ainda_vive(tmp_path / "filho.txt") and not _ainda_vive(tmp_path / "pai.txt"), \
                "o filho escapou do grupo e continua rodando"
    finally:
        _fechar_o_que_sobrou(tmp_path)


def test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou(tmp_path, monkeypatch):
    """Achado 4 do relatório 2 (a frase "conferido" sem teste que a acuse) e achado 9 (sem a leitura do grupo, a frase
    dizia "algum continua rodando"). Três casos, num programa de verdade no grupo: (1) o filho morre JÁ no
    `fechar_tudo`, antes de soltar o grupo (o fechar-ao-fechar do fim do `with` não conta); (2) se a leitura do grupo
    diz que um continua vivo (trocada de propósito), a resposta é "continua(m) rodando", nunca "conferido"; (3) se o
    Windows não responde à leitura do grupo, a resposta é "não deu para conferir"."""
    script = tmp_path / "pai_e_filho.py"
    script.write_text(_PAI_E_FILHO_QUE_ACABA, encoding="utf-8")
    try:
        programa, r = windows.abrir_em_grupo([PY, str(script), str(tmp_path), "pai"])
        assert r.deu_certo, r
        with programa:
            _esperar(tmp_path / "filho.txt")
            fechado = programa.fechar_tudo()
            assert fechado.deu_certo, fechado
            assert not _ainda_vive(tmp_path / "filho.txt"), "o filho só morreu ao soltar o grupo"
        for arquivo in tmp_path.glob("*.txt"):
            arquivo.unlink()
        programa, r = windows.abrir_em_grupo([PY, str(script), str(tmp_path), "pai"])
        assert r.deu_certo, r
        with programa:
            _esperar(tmp_path / "filho.txt")
            monkeypatch.setattr(programa, "vivos", lambda: 1)                          # um continua vivo
            fechado = programa.fechar_tudo(espera_s=1)
            assert fechado.desfecho == windows.FALHOU and "continua" in fechado.motivo, fechado
            monkeypatch.setattr(programa, "vivos", lambda: None)                       # o Windows não responde
            fechado = programa.fechar_tudo(espera_s=1)
            assert fechado.desfecho == windows.FALHOU and "não deu para conferir" in fechado.motivo, fechado
            assert "continua rodando" not in fechado.motivo
            monkeypatch.undo()
            assert programa.fechar_tudo().deu_certo
    finally:
        _fechar_o_que_sobrou(tmp_path)


def test_o_lancado_solto_apaga_a_primeira_pasta_se_a_segunda_nao_nasce(monkeypatch):
    """Achado 9 do relatório 2 (a mesma linha de cuidado): se a segunda pasta de troca (a do sinal de vida) não pudesse
    ser criada, a primeira ficava no disco até a limpeza do dia seguinte. Agora ela é apagada na hora."""
    criadas = []
    verdadeira = windows.criar_pasta_de_troca

    def segunda_falha():
        """A primeira nasce de verdade; a segunda, disco cheio."""
        if criadas:
            raise OSError(28, "No space left on device (de mentira)")
        criadas.append(verdadeira())
        return criadas[-1]

    monkeypatch.setattr(windows, "criar_pasta_de_troca", segunda_falha)
    r = windows.lancar_powershell_solto("")
    assert r.desfecho == windows.FALHOU and criadas
    assert not criadas[0].exists(), f"a primeira pasta de troca ficou: {criadas[0]}"


def test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao(tmp_path):
    """Achado 3 do relatório 2, a outra metade da regra: quando a peça não acha o arquivo (o Windows procura o nome
    sozinho em lugares onde a peça não olha, como a pasta do programa que chama; CreateProcessW, "the system searches
    for the executable file in the following sequence"), o começo do arquivo não pode ser lido; a extensão .bat ou .cmd,
    lida do caminho completado pelo Windows, recusa mesmo assim. (Rodado: um .bat que começa com "MZ" não vai ao cmd.exe,
    o Windows recusa com o erro 216; por isso o começo do arquivo basta quando ele existe.)"""
    # Passo 2, volta 4, achado 9 do relatório 3 de quem tentou quebrar (voltou a quem escreveu pela D-775): os caminhos
    # em texto cru. Antes, num texto comum, o "\n" virava quebra de linha e o "\e" dava o aviso de escape inválido: o
    # caminho testado não era o escrito.
    for nome in (r"C:\nao\existe.bat", r"C:\nao\existe.CMD", r"C:\nao\existe.bat. ", "nao-existe-em-lugar-nenhum.cmd"):
        r = windows.rodar_e_esperar([nome])
        assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, (nome, r)


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 4 (relatório 3 de quem tentou quebrar, 20/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

def _tres_caminhos_recusam(programa: str, tmp_path: Path, frase: str = "função própria") -> list[str]:
    """Passa o programa pelos três caminhos genéricos da peça (rodar, lançar solto, grupo) e devolve os que NÃO
    recusaram com a frase (vazio = os três recusaram)."""
    falhas = []
    r = windows.rodar_e_esperar([programa], limite_s=20)
    if not (r.desfecho == windows.FALHOU and frase in r.motivo):
        falhas.append(f"rodar: {r.desfecho} {r.motivo!r} {(r.dados or {}).get('saida', '')[:20]!r}")
    r = windows.lancar_solto([programa], tmp_path / "sinal.txt", espera_s=1)
    if not (r.desfecho == windows.FALHOU and frase in r.motivo):
        falhas.append(f"lançar: {r.desfecho} {r.motivo!r}")
    programa_no_grupo, r = windows.abrir_em_grupo([programa])
    if programa_no_grupo is not None:
        with programa_no_grupo:
            programa_no_grupo.fechar_tudo()
        falhas.append("grupo: abriu")
    elif frase not in r.motivo:
        falhas.append(f"grupo: {r.motivo!r}")
    return falhas


def test_volta4_o_nome_com_ponto_no_fim_e_lido_como_o_windows_completa(tmp_path, monkeypatch):
    """Achado 2 do relatório 3 de quem tentou quebrar (20/11/2026, família F2, "o vizinho passa"): a regra única da
    peça lia o nome do programa de dois jeitos. O lote era conferido pelo nome completado pelo Windows, mas a lista de
    nomes com função própria e o nome sozinho, pelo texto cru: `pwsh.exe.`, `pwsh.exe..` e `Update.exe.` passavam, e
    o Windows tira o ponto do fim e roda o programa (Microsoft Learn, "File path formats", "Trim characters": "all
    trailing periods and spaces (U+0020) are removed"). Achado junto nesta volta: o nome sozinho `whoami.exe.` rodava o
    whoami DA PASTA DO WINDOWS (o Windows acha pelo PATH; o `shutil.which` não). Agora o nome é lido uma vez só, como o
    Windows o completa, e todas as conferências usam esse nome. De verdade: um "pwsh.exe" e um "Update.exe" de prova
    (cópias do hostname.exe do Windows, inofensivo) numa pasta do teste, pelos três caminhos; e o programa de fora com
    ponto no fim continua passando (a recusa não pega o que não devia)."""
    sistema = windows.pasta_do_sistema()
    pasta_do_pwsh = tmp_path / "PowerShell" / "7"
    pasta_do_pwsh.mkdir(parents=True)
    pwsh = pasta_do_pwsh / "pwsh.exe"
    update = tmp_path / "Update.exe"
    comum = tmp_path / "provaeco.exe"
    for copia in (pwsh, update, comum):
        shutil.copyfile(sistema / "hostname.exe", copia)
    jeitos = [str(pwsh) + ".", str(pwsh) + "..", str(pwsh) + ". ", str(pwsh) + " .", str(update) + ".",
              str(update) + "...", "whoami.exe.", "hostname.exe..", "whoami.exe. "]
    falhas = {jeito: _tres_caminhos_recusam(jeito, tmp_path) for jeito in jeitos}
    assert not any(falhas.values()), {j: f for j, f in falhas.items() if f}
    # pelo PATH também (o nome sozinho, como o Windows procura): o "pwsh.exe." achado na pasta do PowerShell de prova
    monkeypatch.setenv("PATH", str(pasta_do_pwsh) + os.pathsep + os.environ["PATH"])
    assert _tres_caminhos_recusam("pwsh.exe.", tmp_path) == []
    # o programa de fora, com o ponto no fim, continua rodando (o Windows tira o ponto; não está na lista)
    r = windows.rodar_e_esperar([str(comum) + "."])
    assert r.deu_certo and r.dados["saida"], r


def test_volta4_o_programa_que_nao_deixa_ler_e_recusado_com_frase_propria(tmp_path):
    """Achado 6 do relatório 3 (regressão sem uso hoje): os atalhos de aplicativo da Loja (`winget.exe` e outros em
    %LOCALAPPDATA%\\Microsoft\\WindowsApps) não deixam ler o começo do arquivo, e a peça os recusava com "este programa
    do Windows tem função própria na peça: use a função dela", uma função que não existe. Recusar na dúvida continua
    certo; a frase agora é a verdadeira: "não consegui ler o programa para saber se é um programa do Windows". De
    verdade: um programa de prova (cópia do hostname.exe) aberto por outro sem deixar ninguém ler (compartilhamento
    zero, pelo Windows); e, se este computador tiver algum atalho da Loja, ele também."""
    import _winapi

    programa = tmp_path / "trancado.exe"
    shutil.copyfile(windows.pasta_do_sistema() / "hostname.exe", programa)
    trancado = _winapi.CreateFile(str(programa), _winapi.GENERIC_READ, 0, 0, _winapi.OPEN_EXISTING, 0, 0)
    try:
        with pytest.raises(OSError):
            open(programa, "rb").close()
        assert _tres_caminhos_recusam(str(programa), tmp_path, "não consegui ler o programa") == []
    finally:
        _winapi.CloseHandle(trancado)
    assert windows.rodar_e_esperar([str(programa)]).deu_certo, "solto, o mesmo programa roda"
    da_loja = sorted((Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps").glob("*.exe"))
    for atalho in da_loja[:3]:
        try:
            open(atalho, "rb").close()
            continue                                   # este deixa ler: não é o caso
        except OSError:
            pass
        r = windows.rodar_e_esperar([str(atalho), "--version"], limite_s=20)
        assert r.desfecho == windows.FALHOU and "não consegui ler o programa" in r.motivo, (atalho, r)
        assert "função própria" not in r.motivo


def test_volta4_a_segunda_olhada_depois_do_path_recusa_o_lote_achado_pelo_pathext(tmp_path, monkeypatch):
    """Achado 10 do relatório 3 (família F3, proteção sem teste): a olhada de depois de achar o nome sozinho pelo PATH
    (`shutil.which`, que usa as extensões do PATHEXT) não tinha teste. Caso em que só ela recusa: um lote numa pasta do
    PATH, pedido só pelo nome, sem extensão: o `which` o acha como .BAT; antes disso nada indica lote (o nome não tem
    extensão e não existe na pasta atual)."""
    pasta = tmp_path / "no-path"
    pasta.mkdir()
    marca = tmp_path / "o-lote-rodou.txt"
    (pasta / "loteprovav4.bat").write_text(f'@echo x> "{marca}"\r\n', encoding="ascii")
    monkeypatch.setenv("PATH", str(pasta) + os.pathsep + os.environ["PATH"])
    monkeypatch.chdir(tmp_path)
    assert _tres_caminhos_recusam("loteprovav4", tmp_path) == []
    assert not marca.exists()


def test_volta4_rodar_em_grupo_e_o_laco_unico_com_a_saida_a_vigia_e_o_tempo(tmp_path, monkeypatch):
    """Achado 8 do relatório 3 (§11.12, ponto 1: uma peça só para cada conversa com o que está fora): o laço "rodar um
    programa, olhar a vigia e fechar" estava escrito no `rodar_vpk` (pela peça, num grupo) e no gh do publicar (com o
    subprocess direto, sem grupo, fechando só o gh). Agora é `windows.rodar_em_grupo`, que os dois usam. De verdade:
    (1) com a saída guardada, o código de saída e o que o programa escreveu; (2) a vigia manda parar: o programa E o
    filho que ele abriu são fechados (conferido no Windows); (3) o tempo esgotado também fecha tudo; (4) o que tem
    função própria é recusado sem abrir."""
    r = windows.rodar_em_grupo([PY, "-c", "import sys; print('oi'); print('erro', file=sys.stderr); sys.exit(3)"],
                               capturar=True)
    assert r.desfecho == windows.FALHOU and r.dados["codigo"] == 3, r
    assert r.dados["saida"] == "oi" and r.dados["erros"] == "erro", r
    assert windows.rodar_em_grupo([PY, "-c", "print('certo')"], capturar=True).dados["saida"] == "certo"
    script = tmp_path / "pai_e_filho.py"
    script.write_text(_PAI_E_FILHO_QUE_ACABA, encoding="utf-8")
    try:
        def vigia():
            """Manda parar quando o filho já escreve."""
            return "o disco ficou abaixo da reserva (de mentira)" if (tmp_path / "filho.txt").exists() else None

        # o soltar do grupo é segurado (como no teste do achado 4 da volta 3): quem fecha o filho tem de ser o laço,
        # não o fechar-ao-fechar do fim do `with` (com ele, fechar só o programa principal também passaria)
        segurados = []
        soltar_de_verdade = windows.ProgramaEmGrupo.soltar
        monkeypatch.setattr(windows.ProgramaEmGrupo, "soltar", lambda self: segurados.append(self))
        try:
            r = windows.rodar_em_grupo([PY, str(script), str(tmp_path), "pai"], vigia=vigia, intervalo_s=0.2,
                                       capturar=True)
            assert segurados, "o grupo não passou pelo soltar"
            assert r.desfecho == windows.FALHOU and r.dados["parou"] == "o disco ficou abaixo da reserva (de mentira)", r
            assert r.dados["codigo"] is None and r.dados["fechado"] is True, r
            assert not _ainda_vive(tmp_path / "filho.txt") and not _ainda_vive(tmp_path / "pai.txt")
        finally:
            monkeypatch.setattr(windows.ProgramaEmGrupo, "soltar", soltar_de_verdade)
            for programa in segurados:
                soltar_de_verdade(programa)
        for arquivo in tmp_path.glob("*.txt"):
            arquivo.unlink()
        inicio = time.monotonic()
        r = windows.rodar_em_grupo([PY, str(script), str(tmp_path), "pai"], limite_s=3, intervalo_s=0.2)
        assert time.monotonic() - inicio < 15 and "não terminou em 3 segundos" in r.dados["parou"], r
        assert not _ainda_vive(tmp_path / "filho.txt")
    finally:
        _fechar_o_que_sobrou(tmp_path)
    r = windows.rodar_em_grupo([str(windows.pasta_do_sistema() / "cmd.exe"), "/c", "exit"])
    assert r.desfecho == windows.FALHOU and "função própria" in r.motivo and not r.dados.get("abriu"), r


def test_volta4_a_peca_manda_gravar_no_disco_antes_de_trocar_o_nome(tmp_path, monkeypatch):
    """Achado 11 do relatório 3: o que grava num nome provisório e troca pelo nome certo não pedia ao Windows para
    gravar no disco antes de trocar (se a luz cair logo depois, o nome certo podia ficar com o conteúdo pela metade).
    Agora a peça tem um lugar só para isso (`windows.gravar_no_disco`: o flush do Python e o os.fsync, que no Windows é
    o _commit, "Flushes a file directly to disk"), usado antes de trocar o nome. Aqui: a ordem, lida pelo que o Python
    pede ao sistema (o os.fsync de verdade roda), na gravação do script de um PowerShell de verdade (a mesma gravação
    do aviso, da tarefa e da pasta segura)."""
    ordem = []
    verdadeiro_fsync, verdadeiro_replace = os.fsync, os.replace
    monkeypatch.setattr(os, "fsync", lambda fd: (ordem.append("gravar no disco"), verdadeiro_fsync(fd))[1])
    monkeypatch.setattr(os, "replace", lambda a, b: (ordem.append(("trocar", Path(b).name)), verdadeiro_replace(a, b))[1])
    r = windows.rodar_powershell("[Console]::Out.Write('gravado')")
    assert r.deu_certo and r.dados["saida"] == "gravado", r
    i = ordem.index(("trocar", "script.ps1"))
    assert i > 0 and ordem[i - 1] == "gravar no disco", ordem
    with open(tmp_path / "x.bin", "wb") as arquivo:
        arquivo.write(b"x")
        windows.gravar_no_disco(arquivo)
    assert ordem[-1] == "gravar no disco"


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 5 (relatório 4 de quem tentou quebrar, 20/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

def test_volta5_o_programa_num_fluxo_escondido_de_outro_arquivo_e_recusado(tmp_path, monkeypatch):
    """Achado 5 do relatório 4 de quem tentou quebrar (família F2, D-813): o programa gravado como FLUXO escondido de
    outro arquivo (`nada.txt:pwsh.exe`) passava pela peça, que lia o nome como "nada.txt:pwsh.exe" e não achava "pwsh"
    na lista; o Windows roda esse caminho. Lido (Microsoft Learn, "File Streams"): o nome completo de um fluxo é
    "filename:stream name:stream type"; o ":" é reservado num nome ("Naming Files, Paths, and Namespaces") e, depois da
    letra do disco, só aparece para dizer um fluxo. Agora qualquer ":" depois da letra do disco é recusado, com frase
    própria, pelos três caminhos. De verdade: uma cópia do hostname.exe gravada como fluxo (com o nome da lista e com
    outro nome); sem a peça, o Windows a roda; pela peça, não. O "::$DATA" de um lote continua com a frase do lote."""
    sistema = windows.pasta_do_sistema()
    nada = tmp_path / "nada.txt"
    nada.write_text("nada", encoding="utf-8")
    programa = (sistema / "hostname.exe").read_bytes()
    for fluxo in ("pwsh.exe", "outro.exe"):
        with open(str(nada) + ":" + fluxo, "wb") as arquivo:
            arquivo.write(programa)
    sem_a_peca = subprocess.run([str(nada) + ":pwsh.exe"], capture_output=True, timeout=20)
    assert sem_a_peca.returncode == 0 and sem_a_peca.stdout.strip(), "o Windows não rodou o fluxo (o caso não vale)"
    monkeypatch.chdir(tmp_path)
    for jeito in (str(nada) + ":pwsh.exe", str(nada) + ":outro.exe", str(nada) + ":pwsh.exe:$DATA",
                  "nada.txt:pwsh.exe", str(nada) + ":pwsh.exe."):
        assert _tres_caminhos_recusam(jeito, tmp_path, "fluxo escondido") == [], jeito
    (tmp_path / "x.bat").write_text("@echo x\r\n", encoding="ascii")
    r = windows.rodar_e_esperar([str(tmp_path / "x.bat") + "::$DATA"])
    assert r.desfecho == windows.FALHOU and "função própria" in r.motivo, r
