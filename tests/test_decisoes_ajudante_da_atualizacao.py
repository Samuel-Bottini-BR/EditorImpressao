"""Provas do ajudante da atualizacao: D-732 a D-736 e o achado B1 (17/11/2026).

Decisoes do Samuel provadas aqui (docs/plano/DECISOES.md), sem tocar o Windows:
o schtasks, o PowerShell escondido e a pergunta do Windows sao trocados por
pecas de mentira que so anotam o que SERIA feito.

  D-732  (17/11/2026) a versao nova e procurada quando o programa ABRE, nao
         quando o computador liga.
  D-733  (17/11/2026) jeito 1: uma pergunta do Windows na primeira abertura
         cria o ajudante (tarefa como o sistema, que a conta comum pode mandar
         rodar) e faz o resto que pede licenca; depois, nenhuma pergunta por
         atualizacao nem na volta.
  D-734  (17/11/2026) com "Depois", entra na proxima vez que o Kaique abrir,
         com uma espera curta antes da janela; fechar nao troca nada.
  D-735  (17/11/2026) a pergunta do Windows da primeira abertura aparece
         sempre, com ou sem a senha.
  D-736  (17/11/2026) aberto por um teste a distancia, nao procura; o Samuel
         manda atualizar de longe pelo mesmo ajudante.
  B1     (achado de 16/11/2026, plano.md da D-731) os ganchos do .msi rodam
         sem administrador: ao_instalar/ao_atualizar nao podem criar a tarefa.

Nada aqui grava no %ProgramData% nem no %LOCALAPPDATA% de verdade.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

import pytest

import atualizacao
import configuracoes
from core import testes_a_distancia as td

RAIZ = Path(__file__).resolve().parent.parent
EXE = Path(r"C:\Program Files\EditorImpressao\current\EditorImpressao.exe")


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (as Configuracoes nascem limpas)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


class FakeExecutor(td.Executor):
    """A pergunta do Windows de mentira: anota os passos, nao toca o Windows."""

    def __init__(self, cancelado: bool = False) -> None:
        self.chamadas: list[tuple[list[td.Passo], str]] = []
        self._cancelado = cancelado

    def aplicar(self, passos, senha):
        self.chamadas.append((list(passos), senha))
        if self._cancelado:
            return td.Resultado(False, cancelado=True, passos=passos)
        return td.Resultado(True, passos=passos)


@pytest.fixture
def fake(monkeypatch):
    f = FakeExecutor()
    monkeypatch.setattr(td, "_executor", f)
    return f


def _proibido(*_a, **_k):
    pytest.fail("tocou o Windows de verdade")


# ---------------------------------------------------------------------------
# D-732 / D-733: o ajudante nao roda ao ligar; a conta comum manda rodar
# ---------------------------------------------------------------------------

def test_d732_o_ajudante_nao_roda_mais_ao_ligar_o_computador():
    """D-732 (17/11/2026): "não, faz quando o programa é aberto". A tarefa nao tem hora para rodar."""
    xml = atualizacao.xml_da_tarefa(EXE)
    assert "<BootTrigger>" not in xml and "<Triggers>" not in xml and "LogonTrigger" not in xml
    assert "<AllowStartOnDemand>true</AllowStartOnDemand>" in xml
    # o resto da etapa 3 continua: como o sistema, prioridade baixa, sem janela
    assert "<UserId>S-1-5-18</UserId>" in xml and "<Priority>7</Priority>" in xml
    assert f"<Arguments>{atualizacao.ARG_PROCURAR}</Arguments>" in xml


def test_d733_a_conta_comum_pode_mandar_rodar_mas_nao_mudar_o_ajudante():
    """D-733 (17/11/2026): a conta do Kaique (e a de testes) manda rodar; so administrador muda."""
    xml = atualizacao.xml_da_tarefa(EXE)
    sddl = re.search(r"<SecurityDescriptor>(.*?)</SecurityDescriptor>", xml).group(1)
    regras = re.findall(r"\(A;;(\w+);;;(\w+)\)", sddl)
    assert ("GRGX", "AU") in regras, "as contas que entraram no Windows leem e mandam rodar"
    assert dict((quem, direito) for direito, quem in regras) == {"BA": "FA", "SY": "FA", "AU": "GRGX"}


def test_d732_ao_abrir_o_programa_manda_o_ajudante_procurar():
    """D-732 (17/11/2026): abrir o programa chama o ajudante (sem pergunta: schtasks /Run)."""
    pedidos = []
    chamou = atualizacao.procurar_ao_abrir(rodar=lambda c, tempo=120: pedidos.append(c) or (0, ""),
                                           conta_de_testes=lambda: False, portatil=lambda: False)
    assert chamou and pedidos == [["schtasks", "/Run", "/TN", atualizacao.NOME_DA_TAREFA]]
    assert not any("runas" in " ".join(p).lower() for p in pedidos)


def test_d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso(monkeypatch):
    """D-732 (17/11/2026): o main.py chama ligar_na_janela uma vez; ela procura e liga o vigia."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QWidget

    from ui import aviso_de_atualizacao as aviso

    QApplication.instance() or QApplication([])
    monkeypatch.setattr(atualizacao, "marcar_programa_aberto", lambda: None)
    procurou = []
    janela = QWidget()
    vigia = aviso.ligar_na_janela(janela, instalado=lambda: True, conta_de_testes=lambda: False,
                                  procurar=lambda: procurou.append(1) or True)
    assert procurou == [1] and vigia is not None
    vigia.relogio.stop()


def test_b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa():
    """B1 (achado de 16/11/2026; conserto de 17/11/2026, D-733): os ganchos do .msi
    rodam SEM administrador, e criar a tarefa ali sempre falharia. Teste de
    reversao: no codigo antigo ao_instalar chamava criar_tarefa e rodar_tarefa_agora."""
    pedidos = []
    original = (atualizacao.criar_tarefa, atualizacao.rodar_tarefa_agora, atualizacao._rodar)
    try:
        atualizacao.criar_tarefa = lambda *a, **k: pedidos.append("criar") or True
        atualizacao.rodar_tarefa_agora = lambda *a, **k: pedidos.append("rodar") or True
        atualizacao._rodar = lambda *a, **k: pedidos.append("comando") or (0, "")
        atualizacao.ao_instalar("1.2.0", portatil=lambda: False)
        atualizacao.ao_atualizar("1.2.0", portatil=lambda: False)
    finally:
        atualizacao.criar_tarefa, atualizacao.rodar_tarefa_agora, atualizacao._rodar = original
    assert pedidos == [], "os ganchos do instalador não pedem nada que precise de administrador"


def test_d733_depois_de_trocar_o_ajudante_e_refeito_como_o_sistema():
    """D-733 / B1 (17/11/2026): refazer o ajudante saiu do gancho de atualizar e foi para
    o --conferir-a-versao-nova (roda como SYSTEM), so se a versao nova passou."""
    criou = []
    fonte = atualizacao.Fonte("x")
    assert atualizacao.conferir_e_refazer_o_ajudante(fonte, "1.2.0", conferir=lambda f, v: 0,
                                                     criar=lambda: criou.append(1) or True,
                                                     portatil=lambda: False) == 0
    assert criou == [1]
    assert atualizacao.conferir_e_refazer_o_ajudante(fonte, "1.2.0", conferir=lambda f, v: 1,
                                                     criar=_proibido, portatil=lambda: False) == 1
    atualizacao.conferir_e_refazer_o_ajudante(fonte, "1.2.0", conferir=lambda f, v: 0,
                                              criar=_proibido, portatil=lambda: True)


# ---------------------------------------------------------------------------
# D-733 / D-735: a pergunta do Windows da primeira abertura
# ---------------------------------------------------------------------------

# Desde os 4 consertos do atualizador (D-825, Samuel 21/11/2026: "ok"), estes testes cobram o MESMO comportamento das
# D-733/D-735/D-741 pelo caminho novo: a pergunta pela peca unica do Windows (atualizacao.pedir_licenca_ao_windows) e o
# "preparado" lido do Windows (atualizacao.o_que_falta_no_computador), sem a marca nas Configuracoes. O Windows de
# mentira e o de tests/test_atualizador_4.py (nada do Windows de verdade e tocado).

from tests.test_atualizador_4 import WindowsDeMentira  # noqa: E402


@pytest.fixture
def windows_de_mentira(tmp_path, monkeypatch):
    """O Windows de mentira do atualizador (cada pergunta: "sim", salvo `respostas`)."""
    return WindowsDeMentira().instalar(monkeypatch, tmp_path)


def _passo_de_preparo(passos):
    return [p for p in passos if atualizacao.ARG_PREPARAR in p.dados.get("texto", "")]


def _abrir_ja(tdui, conta_de_testes=False):
    """Uma abertura do programa instalado, com o trabalho de tras rodando na hora (para o teste ver o resultado)."""
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: conta_de_testes,
                                 por_tras=lambda trabalho: trabalho())


def test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so(windows_de_mentira, fake, monkeypatch):
    """D-733 (17/11/2026), ajustada pela D-825 (21/11/2026, opcao B): o ajudante, o Visual C++ e o Inno numa pergunta
    so; nesta entrega a senha digitada NAO liga os testes a distancia (nenhum passo deles vai a pergunta).
    Antes (4a775ba8): a senha ligava os testes na mesma pergunta, pelo pedido antigo que lia o "Nao" como "Sim"."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "segredo")
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1, "uma pergunta do Windows só"
    passos, _ = windows_de_mentira.pedidos[0]
    assert len(passos) == 1 and _passo_de_preparo(passos) == passos
    assert fake.chamadas == [], "a peça dos testes à distância não foi chamada"
    assert not td.esta_pronto() and atualizacao.o_que_falta_no_computador() == []


def test_d735_sem_a_senha_a_pergunta_do_windows_aparece_assim_mesmo(windows_de_mentira):
    """D-735 (17/11/2026): sem a senha, so o preparo; a pergunta do Windows aparece, e com o "Sim" o Windows fica
    preparado (lido nele)."""
    assert atualizacao.preparar_na_primeira_abertura() == []
    assert len(windows_de_mentira.pedidos) == 1
    passos, _ = windows_de_mentira.pedidos[0]
    assert passos == _passo_de_preparo(passos) and len(passos) == 1
    assert not td.esta_pronto(), "sem senha, os testes à distância não ligam (D-721)"


def test_d735_agora_nao_na_senha_nao_pula_a_pergunta_do_windows(windows_de_mentira, monkeypatch):
    """D-735 (17/11/2026): "Agora não" na janela da senha -> a pergunta do Windows aparece, e o aviso "Sem a senha..."
    de sempre tambem. Na segunda abertura, ja preparado, nada e perguntado."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    avisos = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda pai, titulo, texto, **k: avisos.append(texto))
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1 and _passo_de_preparo(windows_de_mentira.pedidos[0][0])
    assert avisos and "Sem a senha" in avisos[0]
    assert td.senha_ja_perguntada() and not td.esta_pronto()
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1, "na segunda abertura não pergunta de novo"


def test_d735_com_a_opcao_desligada_a_pergunta_do_windows_aparece(windows_de_mentira, monkeypatch):
    """D-735 (17/11/2026): "aparece sempre": opcao dos testes desligada -> sem janela da senha, mas com a pergunta do
    Windows (o ajudante da atualizacao nasce)."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    configuracoes.escrever(td.CHAVE_LIGADO, False)
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: pytest.fail("pediu a senha"))
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: pytest.fail("avisou"))
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1 and _passo_de_preparo(windows_de_mentira.pedidos[0][0])
    assert atualizacao.o_que_falta_no_computador() == []


def test_d733_disse_nao_fica_anotado_e_nada_quebra(windows_de_mentira):
    """D-733 (17/11/2026): "Nao" na pergunta do Windows -> anotado no registro; nada quebra; o computador continua
    sem preparar (lido no Windows). Antes (4a775ba8), o "Nao" lido como 0 dava "preparado"."""
    windows_de_mentira.respostas = ["nao"]
    falta = atualizacao.preparar_na_primeira_abertura()
    assert falta
    assert "disse \"Não\"" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


def test_d733_o_passo_de_preparar_roda_este_exe_escondido_e_nao_para_a_pergunta():
    """D-733 (17/11/2026): o passo roda <exe> --preparar-o-computador, escondido, e espera; nunca a senha. Desde os 4
    consertos (D-825) o passo e da peca unica e NAO engole o erro: o preparo que falha faz a pergunta dar "falhou"
    (D-749). Antes (4a775ba8) o passo terminava em "catch { }"."""
    passo = atualizacao.passo_de_preparar_o_computador(EXE)
    texto = passo.dados["texto"]
    assert passo.tipo == "script" and passo.dados["com_segredo"] is False
    assert f"'{EXE}'" in texto and f"'{atualizacao.ARG_PREPARAR}'" in texto
    assert "-Wait" in texto and "-WindowStyle Hidden" in texto and "-PassThru" in texto
    assert "catch" not in texto and "throw" in texto and "ExitCode" in texto
    assert td.VARIAVEL_DA_SENHA not in texto and "D-7" not in passo.descricao


def test_d733_o_modo_preparar_cria_o_ajudante_e_prepara_o_computador():
    """D-733 (17/11/2026): dentro da pergunta: o ajudante, o Visual C++ e o Inno (a regra de sempre)."""

    class Gerente:
        def get_is_portable(self):
            return False

    feito = []
    assert atualizacao.preparar_como_administrador(Gerente(), criar=lambda: feito.append("ajudante") or True,
                                                   preparar=lambda g: feito.append("vc e inno")) == 0
    assert feito == ["ajudante", "vc e inno"]
    # no pacote portatil do ensaio, nada
    assert atualizacao.preparar_como_administrador(Gerente(), criar=_proibido, preparar=_proibido,
                                                   portatil=lambda g: True) == 0


def test_d733_a_linha_de_comando_atende_o_preparar(monkeypatch):
    """D-733 (17/11/2026): --preparar-o-computador e um modo escondido (sem janela)."""
    monkeypatch.setattr(atualizacao, "_rodar_o_velopack", lambda: None)
    monkeypatch.setattr(atualizacao, "preparar_como_administrador", lambda: 7)
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe", atualizacao.ARG_PREPARAR]) == 7


# ---------------------------------------------------------------------------
# D-733 / D-734: "Reiniciar agora" e "Depois" sem pergunta do Windows
# ---------------------------------------------------------------------------

def _script(lancados):
    assert len(lancados) == 1
    return lancados[0]


def test_d733_reiniciar_agora_chama_o_ajudante_e_nao_pede_licenca():
    """D-733 (17/11/2026): nenhuma pergunta por atualizacao. O "Reiniciar agora" nao usa mais o
    apply_updates_and_restart do Velopack (que pedia "Deseja permitir...?")."""
    lancados = []
    assert atualizacao.aplicar_agora_e_reabrir(
        trocar=lambda: atualizacao.trocar_e_reabrir(lancar=lancados.append, exe=EXE, pid=4321))
    script = _script(lancados)
    assert "Wait-Process -Id 4321" in script, "espera a janela sair (gravou o trabalho)"
    assert f"'{atualizacao.NOME_DA_TAREFA}'" in script and "'/Run'" in script
    assert f"Start-Process -FilePath '{EXE}' -ArgumentList '{atualizacao.ARG_DEPOIS_DA_TROCA}'" in script
    assert not re.search(r"runas|-Verb", script, re.I), "nada pede administrador"
    assert script.index("Wait-Process") < script.index("schtasks") < script.index("Start-Process")
    assert ".apply_updates_and_restart(" not in Path(atualizacao.__file__).read_text(encoding="utf-8")


def test_d733_o_script_escondido_vai_codificado_e_solto(monkeypatch):
    """D-733 (17/11/2026), pela D-774 (Samuel 18/11: "ok", o teste que cobrava o jeito errado muda para o certo): o
    script da troca vai solto (sobrevive ao programa), PELA PECA UNICA DO WINDOWS (core.windows.lancar_powershell_solto:
    arquivo com a marca de UTF-8, sem a bandeira de processo sem console, com o sinal de vida), e so conta como
    comecado com o sinal de vida. Defeito 1 da etapa 5 (18/11): o PowerShell aberto com DETACHED_PROCESS saia sem
    rodar e o "Reiniciar agora" nao voltava. Antes (4a775ba8) este teste EXIGIA o DETACHED_PROCESS."""
    from core import windows

    lancados = []
    monkeypatch.setattr(windows, "lancar_powershell_solto",
                        lambda texto, espera_s=30: lancados.append(texto) or windows.Resposta(windows.DEU_CERTO))
    assert atualizacao.trocar_e_reabrir(exe=EXE, pid=4321) is True
    assert len(lancados) == 1 and "Wait-Process -Id 4321" in lancados[0]
    monkeypatch.setattr(windows, "lancar_powershell_solto",
                        lambda texto, espera_s=30: windows.Resposta(windows.FALHOU, "não deu sinal de vida"))
    assert atualizacao.trocar_e_reabrir(exe=EXE, pid=4321) is False, "sem sinal de vida, a troca não começou"
    assert "não deu sinal de vida" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    codigo = Path(atualizacao.__file__).read_text(encoding="utf-8")
    assert "EncodedCommand" not in codigo and "_lancar_escondido" not in codigo
    assert codigo.count('getattr(subprocess, "DETACHED_PROCESS", 0)') == 1, "só a volta do Update.exe (ressalva)"


def _pendente():
    return {"fase": "pendente", "nova": "1.2.0", "anterior": "1.1.0"}


def test_d734_depois_a_versao_entra_na_proxima_abertura_antes_da_janela():
    """D-734 (17/11/2026): com "Depois", ao abrir de novo a troca comeca antes da janela."""
    trocou = []
    comum = dict(instalado=lambda: True, conta_de_testes=lambda: False, portatil=lambda: False,
                 versao_atual=lambda: "1.1.0", trocar=lambda: trocou.append(1) or True)
    assert atualizacao.trocar_antes_de_abrir([], ler=_pendente, **comum) is True and trocou == [1]
    # reaberto pela troca: abre normalmente (nunca fica reabrindo sem fim)
    assert atualizacao.trocar_antes_de_abrir([atualizacao.ARG_DEPOIS_DA_TROCA], ler=_pendente, **comum) is False
    # nada esperando: abre normalmente
    assert atualizacao.trocar_antes_de_abrir([], ler=lambda: {}, **comum) is False
    # versao ja falhou: abre normalmente
    assert atualizacao.trocar_antes_de_abrir(
        [], ler=lambda: {"fase": "falhou", "id": "teste-1.2.0"}, **comum) is False
    assert trocou == [1]


def test_d734_a_linha_de_comando_sai_sem_janela_quando_a_troca_comecou(monkeypatch):
    """D-734 (17/11/2026): a "espera curta antes da janela": o programa sai e volta trocado."""
    monkeypatch.setattr(atualizacao, "instalado_pelo_velopack", lambda: True)
    monkeypatch.setattr(atualizacao, "_rodar_o_velopack", lambda: None)
    monkeypatch.setattr(atualizacao, "trocar_antes_de_abrir", lambda argumentos: True)
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe"]) == 0
    monkeypatch.setattr(atualizacao, "trocar_antes_de_abrir", lambda argumentos: False)
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe"]) is None

    def quebra(argumentos):
        raise RuntimeError("Velopack fora do ar")

    monkeypatch.setattr(atualizacao, "trocar_antes_de_abrir", quebra)
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe"]) is None, "um erro aqui nunca impede abrir"


def test_d734_o_aviso_diz_que_entra_na_proxima_abertura_e_fechar_nao_troca():
    """D-734 (17/11/2026): o texto do aviso fala da proxima abertura, nao do computador ligar;
    e nada no fechar da janela chama a troca."""
    assert "próxima vez que você abrir o programa" in atualizacao.FRASE_DA_VERSAO_NOVA
    assert "computador ligar" not in atualizacao.FRASE_DA_VERSAO_NOVA
    janela = (RAIZ / "ui" / "janela_principal.py").read_text(encoding="utf-8")
    assert "atualizacao" not in janela, "o fechar da janela não troca nada"


# ---------------------------------------------------------------------------
# D-736: testes a distancia
# ---------------------------------------------------------------------------

def test_d736_a_conta_de_testes_e_reconhecida_pelo_nome_fixo(monkeypatch):
    """D-736 (17/11/2026): a regra unica de "aberto por um teste a distancia"."""
    assert atualizacao.e_a_conta_de_testes(td.NOME_DA_CONTA)
    assert atualizacao.e_a_conta_de_testes(td.NOME_DA_CONTA.lower())
    assert not atualizacao.e_a_conta_de_testes("Kaique")
    monkeypatch.setenv("USERNAME", td.NOME_DA_CONTA)
    assert atualizacao.e_a_conta_de_testes()


def test_d736_aberto_por_teste_a_distancia_nao_procura_nem_troca(monkeypatch):
    """D-736 (17/11/2026): na conta de testes nada de atualizacao roda sozinho."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QWidget

    import ui.testes_a_distancia_ui as tdui
    from ui import aviso_de_atualizacao as aviso

    QApplication.instance() or QApplication([])
    monkeypatch.setenv("USERNAME", td.NOME_DA_CONTA)
    assert atualizacao.procurar_ao_abrir(rodar=_proibido, portatil=lambda: False) is False
    assert atualizacao.trocar_antes_de_abrir([], instalado=lambda: True, portatil=lambda: False,
                                             ler=_pendente, versao_atual=lambda: "1.1.0",
                                             trocar=_proibido) is False
    marcou = []
    monkeypatch.setattr(atualizacao, "marcar_programa_aberto", lambda: marcou.append(1))
    assert aviso.ligar_na_janela(QWidget(), instalado=lambda: True, procurar=_proibido) is None
    assert marcou == [1], "a marca de programa aberto fica: o ajudante não troca no meio de um teste"
    monkeypatch.setattr(tdui, "perguntar_senha", _proibido)
    monkeypatch.setattr(atualizacao, "preparar_na_primeira_abertura", _proibido)
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True)
    assert not td.senha_ja_perguntada()


def test_d736_o_samuel_manda_atualizar_de_longe_pelo_mesmo_ajudante():
    """D-736 (17/11/2026): o comando de longe chama o MESMO ajudante (mesma assinatura e volta),
    pela conta de testes, que a tarefa deixa mandar rodar (AU)."""
    comando = atualizacao.comando_de_longe_para_atualizar("notebook-do-kaique")
    assert comando == ('ssh EditorTestes@notebook-do-kaique schtasks /Run /TN '
                       '"EditorImpressao\\Procurar versao nova"')
    assert atualizacao.comando_de_rodar_a_tarefa()[-1] == atualizacao.NOME_DA_TAREFA
    assert "(A;;GRGX;;;AU)" in atualizacao.xml_da_tarefa(EXE)
    assert "atualizacao.log" in atualizacao.comando_de_longe_para_ler_o_registro("notebook-do-kaique")


def test_regra_num_lugar_so_todos_os_caminhos_chamam_o_ajudante_pelo_mesmo_comando():
    """CLAUDE.md §11.12 (17/11/2026): abrir, trocar, rodar agora e o comando de longe usam
    comando_de_rodar_a_tarefa; nenhum escreve o schtasks /Run por conta propria."""
    pedidos = []
    rodar = lambda c, tempo=120: pedidos.append(c) or (0, "")  # noqa: E731
    atualizacao.procurar_ao_abrir(rodar=rodar, conta_de_testes=lambda: False, portatil=lambda: False)
    atualizacao.rodar_tarefa_agora(rodar=rodar)
    assert pedidos == [atualizacao.comando_de_rodar_a_tarefa()] * 2
    texto = Path(atualizacao.__file__).read_text(encoding="utf-8")
    assert texto.count('"/Run"') == 1, "o schtasks /Run está escrito num lugar só"


# ---------------------------------------------------------------------------
# A fonte de teste da etapa 5 (pedido da gerente, 17/11/2026)
# ---------------------------------------------------------------------------

ADMIN, KAIQUE = "S-1-5-32-544", "S-1-5-21-1-2-3-1001"


def _arquivo_da_fonte(pasta: Path) -> Path:
    arquivo = atualizacao.caminho_da_fonte_de_teste()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(str(pasta) + "\n", encoding="utf-8")
    return arquivo


def test_etapa5_sem_o_arquivo_as_versoes_vem_do_github():
    """17/11/2026: no notebook do Kaique o arquivo nao existe: tudo como sempre (o GitHub)."""
    assert atualizacao.fonte_de_teste(dono=_proibido) is None
    assert atualizacao.fonte_da_linha([]).endereco == atualizacao.REPOSITORIO


def test_etapa5_o_arquivo_do_administrador_aponta_a_pasta_de_teste(tmp_path):
    """17/11/2026: o arquivo que so o administrador grava aponta a pasta da versao de mentira."""
    (tmp_path / "servidor").mkdir()
    _arquivo_da_fonte(tmp_path / "servidor")
    fonte = atualizacao.fonte_de_teste(dono=lambda p: ADMIN)
    assert fonte is not None and fonte.endereco == str(tmp_path / "servidor") and not fonte.e_github
    # a mesma regra de sempre: --fonte na linha vence; sem ele, a fonte de teste
    assert atualizacao.fonte_da_linha([], de_teste=lambda: fonte) is fonte
    assert atualizacao.fonte_da_linha([atualizacao.ARG_FONTE, "outra"], de_teste=_proibido).endereco == "outra"
    # o conferir, reaberto pelo Velopack, recebe a mesma fonte
    assert atualizacao._argumentos_da_fonte(fonte) == [atualizacao.ARG_FONTE, str(tmp_path / "servidor")]


def test_etapa5_arquivo_de_conta_comum_e_ignorado(tmp_path):
    """17/11/2026: uma conta comum consegue criar o arquivo, mas ele fica dela e e ignorado."""
    (tmp_path / "servidor").mkdir()
    _arquivo_da_fonte(tmp_path / "servidor")
    assert atualizacao.fonte_de_teste(dono=lambda p: KAIQUE) is None
    assert atualizacao.fonte_de_teste(dono=lambda p: None) is None
    assert "não é do administrador" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    _arquivo_da_fonte(tmp_path / "nao-existe")
    assert atualizacao.fonte_de_teste(dono=lambda p: ADMIN) is None


def test_etapa5_pela_fonte_de_teste_a_assinatura_e_conferida_igual(tmp_path):
    """17/11/2026 / D-724: a versao de mentira assinada por outra chave e recusada antes de baixar."""
    import assinatura

    class Pacote:
        PackageId, Version, SHA256 = "EditorImpressao", "9.9.9", "ab" * 32
        FileName = "EditorImpressao-9.9.9-full.nupkg"

    class Gerente:
        baixou = False

        def get_current_version(self):
            return "1.0.0"

        def check_for_updates(self):
            return type("Info", (), {"TargetFullRelease": Pacote()})()

        def download_updates(self, info):
            Gerente.baixou = True

    servidor = tmp_path / "servidor"
    servidor.mkdir()
    v = assinatura.VersaoAssinada(Pacote.PackageId, Pacote.Version, Pacote.FileName, Pacote.SHA256)
    (servidor / assinatura.nome_do_arquivo_da_assinatura(Pacote.PackageId, Pacote.Version)).write_text(
        assinatura.escrever_assinatura(bytes(range(1, 33)), v), encoding="utf-8")
    _arquivo_da_fonte(servidor)
    fonte = atualizacao.fonte_de_teste(dono=lambda p: ADMIN)
    assert atualizacao.procurar_e_preparar(Gerente(), fonte, lambda: False) == "recusada"
    assert not Gerente.baixou


# ---------------------------------------------------------------------------
# D-741 (Samuel, 17/11/2026: "Sim"): depois de um "Nao", a pergunta do Windows volta a cada abertura
# ---------------------------------------------------------------------------

def test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais(windows_de_mentira, monkeypatch):
    """D-741 (Samuel, 17/11/2026: "Sim"): "Nao" a pergunta do Windows da primeira abertura -> abrir de novo -> a
    pergunta volta (so ela: a janela da senha nao, D-721); "Nao" de novo -> volta de novo; "Sim" -> nunca mais.
    Desde a D-825 quem decide e a leitura do Windows. Antes (4a775ba8) o "Nao" lido como 0 gravava a marca e a pergunta
    nao voltava."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    windows_de_mentira.respostas = ["nao", "nao", "sim"]
    senhas = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: senhas.append(1) or "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)

    _abrir_ja(tdui)                                 # 1a abertura: a senha ("Agora não") e a pergunta: "Não"
    assert len(windows_de_mentira.pedidos) == 1 and senhas == [1]
    _abrir_ja(tdui)                                 # 2a abertura: a pergunta volta, sem a janela da senha
    assert len(windows_de_mentira.pedidos) == 2, "D-741: depois do \"Não\", a pergunta do Windows volta ao abrir de novo"
    assert senhas == [1], "a janela da senha não volta (D-721: a senha vai nas Configurações)"
    assert _passo_de_preparo(windows_de_mentira.pedidos[1][0])
    _abrir_ja(tdui)                                 # 3a abertura: volta de novo; agora "Sim"
    assert len(windows_de_mentira.pedidos) == 3
    _abrir_ja(tdui)                                 # depois do "Sim": nunca mais
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 3, "D-741: depois do \"Sim\", a pergunta nunca mais aparece"
    assert not atualizacao.falta_a_pergunta_do_windows()


def test_d741_sim_na_primeira_abertura_nao_volta_mais(windows_de_mentira, monkeypatch):
    """D-741 (17/11/2026): "Sim" ja na primeira abertura -> a pergunta nunca mais aparece (o Windows mostra tudo no
    lugar). A senha digitada nao liga os testes nesta entrega (D-825)."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "segredo")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1
    _abrir_ja(tdui)
    assert len(windows_de_mentira.pedidos) == 1
    assert not atualizacao.falta_a_pergunta_do_windows()


def test_d741_na_conta_de_testes_nada_pergunta_mesmo_depois_de_um_nao(windows_de_mentira, monkeypatch):
    """D-741 e D-736 (17/11/2026): na conta de testes, nada pergunta, nem a pergunta que ficou do "Nao"; pelo codigo,
    nada tambem."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    windows_de_mentira.respostas = ["nao"]
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)
    _abrir_ja(tdui)
    assert atualizacao.falta_a_pergunta_do_windows()
    monkeypatch.setattr(atualizacao, "preparar_ao_abrir", _proibido)
    _abrir_ja(tdui, conta_de_testes=True)
    tdui.primeira_vez_se_preciso(None, instalado=lambda: False, conta_de_testes=lambda: False,
                                 por_tras=lambda trabalho: trabalho())  # pelo código
    assert len(windows_de_mentira.pedidos) == 1


def test_d741_a_marca_e_de_fabrica_falsa_e_gravada_so_pelo_sim(windows_de_mentira):
    """D-741 (17/11/2026), pela D-774 e pela D-825: a regra unica (falta_a_pergunta_do_windows) nasce "falta" e e LIDA
    NO WINDOWS: "Nao" nao a muda; "Sim" com o Windows preparado a desliga; nada e gravado nas Configuracoes.
    Antes (4a775ba8) era a marca "atualizacao_computador_preparado" nas Configuracoes."""
    assert "atualizacao_computador_preparado" not in configuracoes.PADROES, "a marca saiu das Configurações"
    assert atualizacao.falta_a_pergunta_do_windows()
    windows_de_mentira.respostas = ["nao"]
    atualizacao.preparar_na_primeira_abertura()
    assert atualizacao.falta_a_pergunta_do_windows()
    assert "volta na próxima abertura" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    atualizacao.preparar_na_primeira_abertura()
    assert not atualizacao.falta_a_pergunta_do_windows()
    assert configuracoes.carregar().get("atualizacao_computador_preparado") is None, "nada gravado como marca"


# ---------------------------------------------------------------------------
# D-742 (Samuel, 17/11/2026: "Sim"): a janelinha "Atualizando o programa, espere um pouco..."
# ---------------------------------------------------------------------------

# A janela do Windows Forms de mentira: New-Object devolve, para os tipos do Windows Forms, um objeto que so
# anota (nenhuma janela e criada; nada aparece na tela). Os outros tipos (Size, Font) sao os de verdade.
_JANELA_DE_MENTIRA = r"""
function New-Object { param([string]$TypeName, [object[]]$ArgumentList)
  if ($TypeName -like 'System.Windows.Forms.*') {
    Write-Host ('CRIOU ' + $TypeName)
    $o = [pscustomobject]@{ Text=''; ControlBox=$true; FormBorderStyle=''; StartPosition=''; ShowInTaskbar=$true;
                            TopMost=$false; ClientSize=$null; Dock=''; TextAlign=''; Font=$null; Controls=$null }
    $c = [pscustomobject]@{}
    $c | Add-Member -MemberType ScriptMethod -Name Add -Value { param($x) Write-Host ('TEXTO ' + $x.Text) }
    $o.Controls = $c
    $o | Add-Member -MemberType ScriptMethod -Name Show -Value { Write-Host 'MOSTROU' }
    $o | Add-Member -MemberType ScriptMethod -Name Close -Value {
      Write-Host ('FECHOU ControlBox=' + $this.ControlBox + ' TopMost=' + $this.TopMost + ' Titulo=[' + $this.Text + ']') }
    return $o }
  Microsoft.PowerShell.Utility\New-Object -TypeName $TypeName -ArgumentList $ArgumentList }
"""


def _powershell():
    import shutil
    import sys

    caminho = shutil.which("powershell")
    if sys.platform != "win32" or not caminho:
        pytest.skip("a janelinha de mentira usa o powershell.exe")
    return caminho


def test_d742_a_janelinha_aparece_durante_a_espera_e_some_quando_o_programa_abre(tmp_path):
    """D-742 (Samuel, 17/11/2026: "Sim"): na abertura em que a versao nova entra (D-734), uma janelinha com o
    texto exato "Atualizando o programa, espere um pouco..." fica na tela enquanto a troca acontece e some quando
    o programa abre (a marca de "programa aberto" aparece). Sem botao nenhum. Offscreen: a janela do Windows
    Forms e trocada por uma de mentira que so anota; nada aparece na tela. Falha no codigo de antes (nao havia
    janelinha)."""
    import ctypes
    import subprocess
    import threading
    import time
    import uuid

    powershell = _powershell()
    marca = f"Local\\EditorImpressao-teste-{uuid.uuid4().hex}"
    script = tmp_path / "janelinha.ps1"
    script.write_text(_JANELA_DE_MENTIRA + "\n" + atualizacao.script_da_janelinha(marca=marca, limite_s=60),
                      encoding="utf-8-sig")
    processo = subprocess.Popen([powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                 "-File", str(script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
    linhas: list[str] = []
    leitor = threading.Thread(target=lambda: linhas.extend(l.rstrip() for l in processo.stdout), daemon=True)
    leitor.start()
    handle = None
    try:
        limite = time.monotonic() + 60
        while "MOSTROU" not in linhas and time.monotonic() < limite and processo.poll() is None:
            time.sleep(0.1)
        assert "MOSTROU" in linhas, f"a janelinha não apareceu: {linhas}"
        time.sleep(1.5)  # a troca ainda acontecendo: a janelinha continua
        assert processo.poll() is None and not any(l.startswith("FECHOU") for l in linhas), \
            "a janelinha sumiu antes de o programa abrir"
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, marca)  # o programa abriu
        assert handle
        processo.wait(timeout=30)
        leitor.join(timeout=10)
    finally:
        if processo.poll() is None:
            processo.kill()
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
    fechou = [l for l in linhas if l.startswith("FECHOU")]
    assert fechou, f"a janelinha não sumiu quando o programa abriu: {linhas}"
    assert linhas.index("MOSTROU") < linhas.index(fechou[0])
    assert f"TEXTO {atualizacao.TEXTO_DA_JANELINHA}" in linhas
    assert "ControlBox=False" in fechou[0] and "TopMost=True" in fechou[0] and "Titulo=[]" in fechou[0]
    assert not any("Button" in l for l in linhas), "a janelinha não tem botão"


def test_d742_o_texto_e_o_combinado_e_a_janelinha_nao_tem_botao():
    """D-742 (17/11/2026): o texto palavra por palavra; nenhum botao; some sozinha (marca do programa aberto)."""
    assert atualizacao.TEXTO_DA_JANELINHA == "Atualizando o programa, espere um pouco..."
    texto = atualizacao.script_da_janelinha()
    assert "Button" not in texto and "$janela.ControlBox = $false" in texto
    assert f"'{atualizacao.MARCA_DE_ABERTO}'" in texto, "some quando o programa marca que abriu"
    assert "ShowDialog" not in texto, "não prende ninguém: a troca segue sem esperar a janelinha"


def test_d742_a_janelinha_so_na_abertura_depois_do_depois_e_a_troca_fica_igual():
    """D-742 (17/11/2026): a janelinha so entra na abertura depois do "Depois" (D-734). Ela abre ANTES da
    espera, numa linha de execucao separada, e a troca, a volta (D-718) e a reabertura ficam iguais, letra por
    letra. O "Reiniciar agora" (D-720) fica como era: nenhuma outra tela muda."""
    sem = atualizacao.script_de_trocar_e_reabrir(EXE, 4321, Path("C:/x/estado.json"))
    com = atualizacao.script_de_trocar_e_reabrir(EXE, 4321, Path("C:/x/estado.json"), janelinha=True)
    assert atualizacao.TEXTO_DA_JANELINHA not in sem
    inicio, fim = atualizacao._linhas_da_janelinha()
    linhas_sem = sem.split("\n")
    assert com == "\n".join([linhas_sem[0], *inicio, *linhas_sem[1:], *fim])
    assert "'STA'" in inicio[0] and "BeginInvoke" in inicio[-1], "abre e segue sem esperar"
    assert com.index("BeginInvoke") < com.index("Wait-Process") < com.index("Start-Process") < com.index("EndInvoke")


def test_d742_quem_pede_a_janelinha(monkeypatch):
    """D-742 (17/11/2026): trocar_antes_de_abrir (o "Depois") pede a janelinha; o "Reiniciar agora" nao."""
    de_verdade = atualizacao.trocar_e_reabrir
    pedidos = []
    monkeypatch.setattr(atualizacao, "trocar_e_reabrir", lambda **k: pedidos.append(k) or True)
    assert atualizacao.trocar_antes_de_abrir([], instalado=lambda: True, conta_de_testes=lambda: False,
                                             portatil=lambda: False, ler=_pendente, versao_atual=lambda: "1.1.0")
    assert atualizacao.aplicar_agora_e_reabrir()
    assert pedidos == [{"janelinha": True}, {}]
    lancados = []
    assert de_verdade(lancar=lancados.append, exe=EXE, pid=1, janelinha=True)
    assert atualizacao.TEXTO_DA_JANELINHA in lancados[0]


def test_d742_o_script_com_a_janelinha_e_powershell_sem_erro_de_escrita(tmp_path):
    """D-742 (17/11/2026): o script da troca com a janelinha passa pelo leitor do PowerShell (so le o texto)."""
    import subprocess

    powershell = _powershell()
    for nome, texto in {"troca": atualizacao.script_de_trocar_e_reabrir(EXE, 1, Path("C:/x/e.json"), janelinha=True),
                        "janelinha": atualizacao.script_da_janelinha()}.items():
        arquivo = tmp_path / f"{nome}.ps1"
        arquivo.write_text(texto, encoding="utf-8-sig")
        ler = ("$e = $null; [System.Management.Automation.Language.Parser]::ParseFile('" + str(arquivo)
               + "', [ref]$null, [ref]$e) | Out-Null; $e | ForEach-Object { $_.Message }")
        feito = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-Command", ler],
                               capture_output=True, text=True, timeout=120)
        assert feito.returncode == 0 and not feito.stdout.strip(), f"{nome}: {feito.stdout} {feito.stderr}"


def test_d742_se_o_programa_ja_abriu_a_janelinha_nem_aparece(tmp_path):
    """D-742 (17/11/2026): se o programa ja abriu enquanto a janelinha se montava, ela nem aparece (nada pisca
    na tela). Offscreen, com a janela de mentira."""
    import ctypes
    import subprocess
    import uuid

    powershell = _powershell()
    marca = f"Local\EditorImpressao-teste-{uuid.uuid4().hex}"
    handle = ctypes.windll.kernel32.CreateMutexW(None, False, marca)
    try:
        script = tmp_path / "janelinha.ps1"
        script.write_text(_JANELA_DE_MENTIRA + "\n" + atualizacao.script_da_janelinha(marca=marca, limite_s=60),
                          encoding="utf-8-sig")
        feito = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                "-File", str(script)], capture_output=True, text=True, timeout=120,
                               encoding="utf-8", errors="replace")
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    linhas = feito.stdout.splitlines()
    assert "MOSTROU" not in linhas and any(l.startswith("FECHOU") for l in linhas), linhas
