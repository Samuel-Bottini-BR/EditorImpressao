"""Provas dos 4 consertos do atualizador para a primeira entrega ao Kaique (D-824, D-825; 21/11/2026).

Plano e caminhos: relatorios/atualizador-4/ONDE-PAREI.md. Cada teste diz o defeito que pega e falha no codigo de
antes (4a775ba8); quem confere roda la.

Conserto 1 (defeito de 18/11, Lista de bugs: "o pedido de licenca do Windows [...] le o erro errado: quando o pedido
falha, o programa entende 'deu certo'"): a pergunta da primeira abertura vai pela peca unica do Windows
(core.windows.pedir_licenca) e "preparado" e lido do Windows (o ajudante existe e aponta para o programa, a tarefa
"desfazer", o Visual C++, a instalacao antiga), nunca de uma anotacao.

NADA AQUI TOCA O WINDOWS: o pedido e a leitura sao trocados pelo Windows de mentira abaixo (D-767: isto prova a logica
em volta; o que vale e a sessao a vista). O pedido de verdade se recusa sob o pytest (um teste cobra).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import atualizacao
from core import testes_a_distancia as td
from core import windows


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (o registro e as Configuracoes nascem limpos)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


class WindowsDeMentira:
    """O Windows do notebook, de mentira, para o atualizador: a pergunta ("Deseja permitir...?") e o que ela muda.

    `respostas`: uma por pergunta, em ordem: "sim" (a preparacao inteira: o ajudante, o desfazer, o Visual C++ e a
    instalacao antiga tirada), "meio" (o ajudante criado e o Visual C++ nao: a preparacao parou no meio, a peca
    devolve "falhou"), "nao" (o Kaique disse Nao) ou "falhou" (o Windows nao abriu nada). `ler_tarefa` devolve o que
    foi "criado". Nada do Windows de verdade e tocado. `instalar(monkeypatch, pasta)` poe esta peca no atualizador,
    com a pasta do programa de mentira (com o Visual C++ no pacote) e uma instalacao antiga do Inno para tirar.
    """

    def __init__(self, respostas: list[str] | None = None) -> None:
        """O Windows de mentira comeca sem o ajudante, sem o Visual C++ e com a instalacao antiga para tirar."""
        self.respostas = list(respostas or [])
        self.pedidos: list[tuple[list, int | None]] = []
        self.tarefas: dict[str, windows.Tarefa] = {}
        self.visual_c: tuple | None = None
        self.inno: dict | None = None
        self.exe: Path | None = None
        self.ajudante_rodou = 0

    def instalar(self, monkeypatch, pasta: Path) -> "WindowsDeMentira":
        """Liga esta peca no atualizador (pedido, leitura das tarefas, registro do Windows, pasta do programa)."""
        programa = pasta / "EditorImpressaoPrograma" / "current"
        instalar = programa / atualizacao.PASTA_DO_QUE_SE_INSTALA
        instalar.mkdir(parents=True)
        (instalar / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ")
        (instalar / atualizacao.VC_REDIST_VERSAO).write_text("14.44.1", encoding="utf-8")
        antiga = pasta / "InstalacaoAntigaDoInno"
        self.inno = {"pasta": antiga, "desinstalador": antiga / "unins000.exe"}
        self.exe = programa / "EditorImpressao.exe"
        monkeypatch.setattr(atualizacao, "pasta_do_programa", lambda: programa)
        monkeypatch.setattr(atualizacao, "exe_do_programa", lambda: self.exe, raising=False)
        monkeypatch.setattr(atualizacao, "e_portatil", lambda gerente=None: False)
        monkeypatch.setattr(atualizacao, "pedir_licenca_ao_windows", self.pedir, raising=False)
        monkeypatch.setattr(atualizacao, "ler_tarefa_no_windows", self.ler_tarefa, raising=False)
        monkeypatch.setattr(atualizacao, "_ler_versao_do_visual_c", lambda: self.visual_c)
        monkeypatch.setattr(atualizacao, "achar_instalacao_do_inno", lambda ler_chave=None: self.inno)
        monkeypatch.setattr(atualizacao, "procurar_ao_abrir", self._rodar_o_ajudante)
        return self

    def _rodar_o_ajudante(self, *a, **k) -> bool:
        """No lugar de atualizacao.procurar_ao_abrir: so conta quantas vezes o ajudante foi chamado."""
        self.ajudante_rodou += 1
        return True

    def _criar_ajudante(self, comando: str | None = None) -> None:
        """O que a preparacao de verdade deixa no Agendador: o ajudante, rodando como o sistema."""
        nome = atualizacao.NOME_DA_TAREFA
        self.tarefas[nome] = windows.Tarefa(nome, True, True, comando=comando or str(self.exe),
                                            argumentos=atualizacao.ARG_PROCURAR, usuario=windows.SID_SISTEMA,
                                            licenca=atualizacao.QUEM_PODE_MANDAR_RODAR)

    def _criar_desfazer(self) -> None:
        """A tarefa "desfazer" que a preparacao cria (D-731)."""
        nome = td.nome_da_tarefa_do_desfazer()
        self.tarefas[nome] = windows.Tarefa(nome, True, True, comando="powershell.exe", usuario=windows.SID_SISTEMA)

    def pedir(self, passos, janela=None):
        """A pergunta de mentira (no lugar de atualizacao.pedir_licenca_ao_windows)."""
        self.pedidos.append((list(passos), janela))
        resposta = self.respostas.pop(0) if self.respostas else "sim"
        if resposta == "nao":
            return windows.Resposta(windows.DISSE_NAO, "você disse Não; nada mudou")
        if resposta == "falhou":
            return windows.Resposta(windows.FALHOU, "o Windows não abriu o programa")
        self._criar_ajudante()
        if resposta == "meio":
            return windows.Resposta(windows.FALHOU, "preparar o computador: a preparação do computador terminou "
                                                    "com o código 1")
        self._criar_desfazer()
        self.visual_c = (99, 0, 0)
        self.inno = None
        return windows.Resposta(windows.DEU_CERTO)

    def ler_tarefa(self, nome: str) -> windows.Tarefa:
        """A leitura de mentira (no lugar de atualizacao.ler_tarefa_no_windows)."""
        return self.tarefas.get(nome) or windows.Tarefa(nome, False)


@pytest.fixture
def windows_de_mentira(tmp_path, monkeypatch):
    """O Windows de mentira ligado no atualizador, sem resposta marcada (cada pergunta: "sim")."""
    return WindowsDeMentira().instalar(monkeypatch, tmp_path)


def _registro() -> str:
    """O registro da atualizacao (o de mentira, no ProgramData de mentira), ou "" se ainda nao existe."""
    caminho = atualizacao.caminho_do_registro()
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 1: o "Nao" e "Nao", e "preparado" vem do Windows
# ---------------------------------------------------------------------------------------------------------------------

def test_conserto1_o_nao_do_windows_nao_vira_preparado(windows_de_mentira):
    """Defeito de 18/11 (Lista de bugs, `_rodar_elevado`): o "Nao" virava "deu certo" e o computador ficava como
    preparado. Agora: "Nao" -> o Windows continua sem o ajudante -> falta, e a pergunta volta (D-741)."""
    windows_de_mentira.respostas = ["nao"]
    falta = atualizacao.preparar_na_primeira_abertura()
    assert falta and any("ajudante" in f for f in falta)
    assert atualizacao.falta_a_pergunta_do_windows()
    assert "disse \"Não\"" in _registro()


def test_conserto1_a_pergunta_vai_pela_peca_unica_com_um_passo_so(windows_de_mentira):
    """§11.12.1: o atualizador pede a licenca so por pedir_licenca_ao_windows (a peca unica), com o passo de preparar."""
    assert atualizacao.preparar_na_primeira_abertura() == []
    passos, _janela = windows_de_mentira.pedidos[0]
    assert len(windows_de_mentira.pedidos) == 1 and len(passos) == 1
    assert isinstance(passos[0], windows.Passo) and passos[0].tipo == "script"
    assert atualizacao.ARG_PREPARAR in passos[0].dados["texto"]
    texto = Path(atualizacao.__file__).read_text(encoding="utf-8")
    assert "executor_atual" not in texto and "_ComOPreparo" not in texto, "o pedido antigo saiu do atualizador"


def test_conserto1_o_pedido_de_verdade_nao_pergunta_nada_sob_os_testes():
    """O pedido de verdade nunca abre a pergunta do Windows na tela de quem roda os testes."""
    resposta = atualizacao.pedir_licenca_ao_windows([atualizacao.passo_de_preparar_o_computador(Path("C:/x.exe"))])
    assert resposta.desfecho == windows.FALHOU


def test_conserto1_sim_so_conta_com_o_windows_mostrando_o_ajudante(windows_de_mentira, monkeypatch):
    """§11.12.2: a peca diz "deu certo", mas o Windows nao tem o ajudante -> nao preparado (nunca pela anotacao)."""
    monkeypatch.setattr(windows_de_mentira, "_criar_ajudante", lambda comando=None: None)
    assert atualizacao.preparar_na_primeira_abertura()
    assert "não ficou preparado" in _registro()


def test_conserto1_ajudante_de_outro_programa_conta_como_falta(windows_de_mentira):
    """O ajudante existe, mas aponta para outro .exe (outra instalacao): falta (a pergunta refaz)."""
    windows_de_mentira.pedir([])
    windows_de_mentira._criar_ajudante(r"C:\Outro\EditorImpressao.exe")
    assert any("comando" in f for f in atualizacao.o_que_falta_no_computador())


def test_conserto1_o_mesmo_caminho_escrito_diferente_e_o_mesmo_ajudante(windows_de_mentira):
    """Volta 2 (item 4 da gerente, baixo 3 do relatorio 1): a conferencia "a tarefa lida e a do programa?" e a da peca
    unica (core.windows.problemas_da_tarefa_criada), a mesma da criacao: o texto que o programa gravou volta igual do
    Agendador. (O nome ficou da volta 1, quando havia uma conta propria que normalizava o caminho.)"""
    windows_de_mentira.pedir([])
    assert atualizacao.o_que_falta_no_computador() == []
    windows_de_mentira._criar_ajudante(str(windows_de_mentira.exe).replace("EditorImpressao.exe", "Outro.exe"))
    assert any("comando" in f for f in atualizacao.o_que_falta_no_computador())


@pytest.mark.parametrize("existe, lida", [(None, False), (True, False)])
def test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta(windows_de_mentira, existe, lida):
    """Volta 3 (D-826, Samuel 22/11/2026: "no caso raro a pergunta volta sempre"): "nao deu para saber" (o Windows nao
    respondeu) conta como FALTA, e a pergunta volta (D-741). "Existe, mas esta conta nao le" continua contando como
    existe (a tarefa so nasce com a licenca de administrador). Historia: na volta 1 os dois contavam como falta; na
    volta 2 (medio 3) nenhum contava, e o "Nao" com a leitura falhando nunca mais trazia a pergunta (relatorio 2, (b))."""
    windows_de_mentira.pedir([])
    nome = atualizacao.NOME_DA_TAREFA
    windows_de_mentira.tarefas[nome] = windows.Tarefa(nome, existe, lida, motivo="o Windows não respondeu")
    falta = atualizacao.o_que_falta_no_computador()
    if existe is None:
        assert falta and any("não deu para ler o ajudante" in f for f in falta)
    else:
        assert falta == []


def test_conserto1_reinstalado_sem_o_ajudante_a_pergunta_volta(windows_de_mentira):
    """Defeito 7 da revisao de 18/11: reinstalado, a marca das Configuracoes ficava e a pergunta nunca voltava.
    Agora o ajudante que sumiu faz a pergunta voltar."""
    assert atualizacao.preparar_na_primeira_abertura() == []
    windows_de_mentira.tarefas.clear()                       # desinstalou e instalou de novo
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=False) == []
    assert len(windows_de_mentira.pedidos) == 2, "a pergunta voltou"


def test_conserto1_preparado_nao_pergunta_e_depois_do_sim_o_ajudante_roda(windows_de_mentira):
    """Com tudo no lugar, a abertura nao pergunta nada; depois de um "Sim", o ajudante (que acabou de nascer) roda
    uma vez, como antes (quando a abertura esperava a pergunta)."""
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True) == []
    assert windows_de_mentira.ajudante_rodou == 1
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=False) == []
    assert len(windows_de_mentira.pedidos) == 1 and windows_de_mentira.ajudante_rodou == 1


def test_conserto1_visual_c_e_inno_sao_a_mesma_regra_de_quem_instala_e_tira(windows_de_mentira):
    """§11.12: "falta o Visual C++?" e uma regra so (visual_c_que_falta), a que quem instala usa. (Desde a volta 2 a
    pergunta do Windows nao a le mais: o ajudante completa o Visual C++ sozinho.)"""
    pasta = atualizacao.pasta_do_programa()
    assert atualizacao.visual_c_que_falta(pasta, lambda: None) == "14.44.1"
    assert atualizacao.visual_c_que_falta(pasta, lambda: (14, 44, 1)) is None
    rodados = []
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: (14, 44, 1),
                                                   rodar=lambda c, t: rodados.append(c) or (0, "")) is True
    assert rodados == [], "quando a regra diz que nada falta, nada é instalado"


def test_conserto1_a_instalacao_antiga_que_o_programa_nao_tira_de_proposito_nao_falta(windows_de_mentira, monkeypatch):
    """Como a D-749 ja dizia: o Inno de caminho estranho nao e tirado de proposito, e perguntar de novo nao mudaria
    nada (senao a pergunta voltaria para sempre)."""
    windows_de_mentira.pedir([])
    windows_de_mentira.inno = {"pasta": Path("C:/x"), "desinstalador": Path("C:/x/unins000.exe")}
    monkeypatch.setattr(atualizacao, "comando_para_tirar_o_inno", lambda antiga, pasta: None)
    assert atualizacao.o_que_falta_no_computador() == []


def test_conserto1_no_portatil_nada_falta(windows_de_mentira, monkeypatch):
    """O pacote portatil do ensaio nunca mexe no Windows (e_portatil): nada a preparar."""
    monkeypatch.setattr(atualizacao, "e_portatil", lambda gerente=None: True)
    assert atualizacao.o_que_falta_no_computador() == []


def test_conserto1_um_erro_inesperado_no_fio_de_tras_conta_como_falta(windows_de_mentira, monkeypatch):
    """O fio de tras nunca derruba o programa: o erro vai para o registro e a pergunta volta."""
    def quebra(*a, **k):
        raise RuntimeError("quebrou")

    monkeypatch.setattr(atualizacao, "preparar_na_primeira_abertura", quebra)
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True)
    assert "erro inesperado" in _registro()


def test_conserto1_a_tela_roda_a_pergunta_por_tras_e_nao_no_fio_da_tela(windows_de_mentira, monkeypatch):
    """CLAUDE.md §3 ("a janela nunca congela"): a tela entrega o trabalho a quem roda por tras; nada do Windows roda
    no fio da tela."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)
    trabalhos = []
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: False,
                                 por_tras=trabalhos.append)
    assert windows_de_mentira.pedidos == [], "nada foi perguntado no fio da tela"
    assert len(trabalhos) == 1
    trabalhos[0]()
    assert len(windows_de_mentira.pedidos) == 1


def test_conserto1_o_fio_de_tras_e_solto(monkeypatch):
    """O fio de tras e solto (daemon): fechar o programa no meio da pergunta nao o segura aberto."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    fio = tdui._rodar_por_tras(lambda: None)
    fio.join(5)
    assert fio.daemon


def test_d825_a_senha_digitada_nao_liga_nenhum_passo_dos_testes(windows_de_mentira, monkeypatch):
    """D-825, opcao B (Samuel, 21/11/2026: "ok"): nesta entrega a senha digitada nao liga os testes a distancia.
    Nenhum passo dos testes roda (a peca dos testes nem e chamada), nada fica marcado como ligado, a senha nao vai ao
    pedido, e a pergunta do Windows e uma so, com so o preparo. Falha no codigo de antes (a senha ia na pergunta)."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    class TestesQueNaoPodemRodar(td.Executor):
        def aplicar(self, passos, senha):
            pytest.fail("um passo dos testes à distância rodou")

        def aplicar_ja_como_administrador(self, passos):
            pytest.fail("um passo dos testes à distância rodou")

    monkeypatch.setattr(td, "_executor", TestesQueNaoPodemRodar())
    monkeypatch.setattr(td, "ligar", lambda senha: pytest.fail("ligou os testes à distância"))
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "segredo-de-prova")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: pytest.fail("avisou"))
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: False,
                                 por_tras=lambda trabalho: trabalho())
    assert len(windows_de_mentira.pedidos) == 1, "uma pergunta do Windows só"
    passos, _ = windows_de_mentira.pedidos[0]
    assert len(passos) == 1 and "segredo-de-prova" not in repr(passos)
    assert not td.esta_pronto()


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 2: a pergunta vem no meio da tela (a janela do programa e a dona e vem para a frente antes)
# ---------------------------------------------------------------------------------------------------------------------

class _JanelaDeMentira:
    """Uma janela que so sabe dizer o numero dela no Windows (como QWidget.winId)."""

    def __init__(self, numero: int) -> None:
        """Guarda o numero da janela no Windows."""
        self.numero = numero

    def winId(self) -> int:  # noqa: N802 - o nome do Qt
        """O numero da janela, como o QWidget.winId do Qt."""
        return self.numero


@pytest.mark.parametrize("ja_perguntada", [False, True])
def test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta(windows_de_mentira, monkeypatch, ja_perguntada):
    """Defeito de 18/11 (Lista de bugs: "a pergunta de administrador do Windows nao aparece quando o programa pede com
    as janelas fora da frente") e D-806 (19/11: "o programa pede a licenca do Windows no mesmo instante do clique [...]
    enquanto a janela do programa ainda esta na frente"): o pedido antigo ia sem a janela do programa. Agora a janela
    principal (o numero dela no Windows) vai ao pedido, na primeira abertura e nas seguintes."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    if ja_perguntada:
        td.marcar_senha_perguntada()
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)
    tdui.primeira_vez_se_preciso(_JanelaDeMentira(0x1234), instalado=lambda: True, conta_de_testes=lambda: False,
                                 por_tras=lambda trabalho: trabalho())
    assert [janela for _passos, janela in windows_de_mentira.pedidos] == [0x1234]


def test_conserto2_sem_janela_a_pergunta_sai_sem_dona():
    """Sem janela (ou o Qt sem o numero), a pergunta sai sem dona, sem quebrar."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    assert tdui.numero_da_janela(None) is None
    assert tdui.numero_da_janela(object()) is None
    assert tdui.numero_da_janela(_JanelaDeMentira(0)) is None


def test_conserto2_a_janela_que_nao_veio_para_a_frente_fica_anotada(windows_de_mentira, monkeypatch):
    """Quando o Windows nao deixa a janela vir para a frente (o Kaique estava noutra), a peca diz e o registro anota."""
    original = windows_de_mentira.pedir

    def pedir_sem_frente(passos, janela=None):
        r = original(passos, janela)
        return windows.Resposta(r.desfecho, r.motivo, r.detalhe, {**r.dados, "janela_na_frente": False})

    monkeypatch.setattr(atualizacao, "pedir_licenca_ao_windows", pedir_sem_frente)
    atualizacao.preparar_na_primeira_abertura(0x99)
    assert "não estava na frente" in _registro()


def test_conserto2_o_pedido_de_verdade_entrega_a_janela_a_peca(monkeypatch):
    """O pedido do atualizador passa a janela a core.windows.pedir_licenca (a peca a traz para a frente e a poe como
    dona do pedido)."""
    recebidos = {}
    monkeypatch.delenv("PYTEST_CURRENT_TEST")
    monkeypatch.setattr(windows, "pedir_licenca", lambda passos, **k: recebidos.update(k) or windows.Resposta(
        windows.DEU_CERTO))
    atualizacao.pedir_licenca_ao_windows([], 0x55)
    assert recebidos["janela"] == 0x55


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 3: "Reiniciar agora" volta, e com "Depois" o programa abre
# ---------------------------------------------------------------------------------------------------------------------

EXE_DE_MENTIRA = Path(r"C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe")


@pytest.fixture
def lancamentos(monkeypatch):
    """O lancar solto da peca, de mentira: anota o script e responde como `lancamentos.resposta` (padrao: comecou)."""
    class Lancamentos(list):
        resposta = windows.Resposta(windows.DEU_CERTO)

    lancados = Lancamentos()
    monkeypatch.setattr(windows, "lancar_powershell_solto",
                        lambda texto, espera_s=30: lancados.append(texto) or lancados.resposta)
    return lancados


def test_conserto3_reiniciar_agora_lanca_a_troca_pela_peca(lancamentos, monkeypatch):
    """Defeito de 18/11 (Lista de bugs: "'Reiniciar agora' fecha o programa e a versao nova nao entra: o programa nao
    volta", DETACHED_PROCESS): o botao (aplicar_agora_e_reabrir, o caminho do aviso) lanca o script pela peca unica,
    que so da como comecado com o sinal de vida."""
    monkeypatch.setattr(atualizacao, "exe_do_programa", lambda: EXE_DE_MENTIRA)
    assert atualizacao.aplicar_agora_e_reabrir() is True
    assert len(lancamentos) == 1 and atualizacao.ARG_DEPOIS_DA_TROCA in lancamentos[0]


def test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre(lancamentos, monkeypatch):
    """Defeito de 18/11: com uma versao esperando ("Depois"), o programa saia sem janela toda vez (o script nao
    rodava, e o programa achava que sim). Agora, sem o sinal de vida, a abertura segue na versao de hoje."""
    lancamentos.resposta = windows.Resposta(windows.FALHOU, "o processo lançado não deu sinal de vida")
    monkeypatch.setattr(atualizacao, "exe_do_programa", lambda: EXE_DE_MENTIRA)
    comum = dict(instalado=lambda: True, conta_de_testes=lambda: False, portatil=lambda: False,
                 ler=lambda: {"fase": "pendente", "nova": "1.2.0", "anterior": "1.1.0"}, versao_atual=lambda: "1.1.0")
    assert atualizacao.trocar_antes_de_abrir([], **comum) is False, "a janela abre"
    assert len(lancamentos) == 1 and "Atualizando o programa" in lancamentos[0], "com a janelinha (D-742)"
    lancamentos.resposta = windows.Resposta(windows.DEU_CERTO)
    assert atualizacao.trocar_antes_de_abrir([], **comum) is True


def test_conserto3_o_limite_da_troca_chega_ao_script_e_a_janelinha():
    """Defeitos 3 e 4 da revisao de 18/11: com 300 s o script reabria o programa no meio da troca. O limite (900 s)
    vai ao script e a janelinha espera tambem por ele."""
    assert atualizacao.LIMITE_DA_TROCA_S == 900
    script = atualizacao.script_de_trocar_e_reabrir(EXE_DE_MENTIRA, 1, Path("C:/x/estado.json"), janelinha=True)
    assert "AddSeconds(900)" in script
    assert f"AddSeconds({900 + atualizacao.ESPERA_DA_VOLTA_S + 120})" in atualizacao.script_da_janelinha()


# ---------------------------------------------------------------------------------------------------------------------
# Conserto 4: o motor do Kraken continua funcionando depois da atualizacao
# ---------------------------------------------------------------------------------------------------------------------

def _instalacao_com_o_motor_no_instalador(tmp_path: Path) -> tuple[Path, Path]:
    """Uma instalacao de mentira como o .msi deixa: <raiz>\current\instalar\motor-kraken-<v>.zip (o motor de
    mentira, com a ficha gravada pela funcao de verdade). Devolve (raiz, current)."""
    import zipfile

    import versao
    from core import ocr_kraken
    from tests.test_publicar_motor import _motor

    motor = _motor(tmp_path / "motor-montado")
    raiz = tmp_path / "EditorImpressaoPrograma"
    current = raiz / "current"
    instalar = current / atualizacao.PASTA_DO_QUE_SE_INSTALA
    instalar.mkdir(parents=True)
    with zipfile.ZipFile(instalar / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR), "w") as z:
        for arquivo in motor.rglob("*"):
            if arquivo.is_file():
                z.write(arquivo, arquivo.relative_to(motor).as_posix())
    return raiz, current


def test_conserto4_o_ajudante_poe_o_motor_do_instalador_no_lugar_dele(tmp_path):
    """Defeito de 21/11 (D-824: "o publicar novo manda a atualizacao sem o motor do Kraken e o atualizador antigo
    espera o motor dentro dela"): ninguem tirava o motor do arquivo do instalador. Agora garantir_o_motor o poe em
    <raiz>\motor-kraken\1, conferido; a segunda vez nao refaz nada."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current) is True
    destino = ocr_kraken.pasta_do_motor_instalado(raiz)
    assert destino == raiz / "motor-kraken" / "1"
    assert ocr_kraken.conferir_motor(destino) == []
    assert not (raiz / "motor-kraken" / ".chegando-1").exists()
    antes = (destino / ocr_kraken.NOME_DA_FICHA).stat().st_mtime_ns
    assert atualizacao.garantir_o_motor(raiz, current) is True
    assert (destino / ocr_kraken.NOME_DA_FICHA).stat().st_mtime_ns == antes, "já no lugar: nada é refeito"


def test_conserto4_sem_espaco_nao_comeca(tmp_path):
    """Sem o espaco do motor aberto mais a folga, nao comeca, e nada fica."""
    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current, livre=lambda p: 10) is False
    assert not (raiz / "motor-kraken" / "1").exists() and not (raiz / "motor-kraken" / ".chegando-1").exists()
    assert "falta espaço" in _registro()


def test_conserto4_motor_estragado_no_arquivo_nunca_fica_com_o_nome_final(tmp_path):
    """Um arquivo do motor que nao confere (um arquivo da ficha faltando) e recusado: o nome final nunca aparece pela
    metade e a pasta provisoria some."""
    import zipfile

    import versao
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    arquivo = current / atualizacao.PASTA_DO_QUE_SE_INSTALA / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    with zipfile.ZipFile(arquivo) as z:
        conteudo = {n: z.read(n) for n in z.namelist() if not n.endswith("outro.py")}
    with zipfile.ZipFile(arquivo, "w") as z:
        for nome, dados in conteudo.items():
            z.writestr(nome, dados)
    assert atualizacao.garantir_o_motor(raiz, current) is False
    assert not (raiz / "motor-kraken" / "1").exists() and not (raiz / "motor-kraken" / ".chegando-1").exists()


def test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador(tmp_path):
    """Um motor no nome final que nao confere (um arquivo cortado) e posto de lado e o do instalador entra."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current)
    destino = ocr_kraken.pasta_do_motor_instalado(raiz)
    (destino / "python" / "python.exe").write_bytes(b"x")
    assert ocr_kraken.conferir_motor(destino)
    assert atualizacao.garantir_o_motor(raiz, current) is True
    assert ocr_kraken.conferir_motor(destino) == []
    assert [p.name for p in (raiz / "motor-kraken").iterdir()] == ["1"], "o estragado posto de lado foi apagado"


def test_conserto4_sem_o_arquivo_e_sem_o_motor_diz_e_nao_finge(tmp_path):
    """Sem o motor no lugar e sem o arquivo do instalador: False e registro (nunca "deu certo")."""
    raiz = tmp_path / "EditorImpressaoPrograma"
    (raiz / "current").mkdir(parents=True)
    assert atualizacao.garantir_o_motor(raiz, raiz / "current") is False
    assert "motor do Kraken: não está" in _registro()


def test_conserto4_a_troca_nao_acontece_sem_o_motor_no_lugar(tmp_path):
    """D-788/D-790: com o programa fechado e o motor fora do lugar, a versao nova nao troca (a troca apagaria o unico
    arquivo do motor que veio no instalador). Volta 2 (medio 2): nem e anunciada ("sem-motor", nada de "pendente").
    Com o motor no lugar, troca."""
    from tests.test_decisoes_atualizacao import PUBLICA, GerenteFalso, _servidor

    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA,
                                           motor_no_lugar=lambda: False) == "sem-motor"
    assert gerente.trocou == [] and atualizacao.ler_estado().get("fase") != "pendente"
    assert "não baixo nem anuncio" in _registro()
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA,
                                           motor_no_lugar=lambda: True) == "aplicando"
    assert len(gerente.trocou) == 1


def test_conserto4_o_motor_no_lugar_e_a_mesma_conferencia(tmp_path, monkeypatch):
    """motor_esta_no_lugar (o que procurar_e_preparar pergunta) le a pasta unica e a conferencia unica do motor; pelo
    codigo (fora de uma instalacao do Velopack) e sempre True (nada e trocado ali)."""
    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.motor_esta_no_lugar(raiz) is False
    atualizacao.garantir_o_motor(raiz, current)
    assert atualizacao.motor_esta_no_lugar(raiz) is True
    assert atualizacao.motor_esta_no_lugar() is True, "pelo código"


def test_conserto4_o_ajudante_poe_o_motor_antes_de_procurar_e_nunca_no_portatil():
    """rodar_ao_ligar (o ajudante) poe o motor no lugar antes de procurar a versao nova; no portatil, nunca."""
    class Gerente:
        def __init__(self, portatil):
            self.portatil = portatil

        def get_is_portable(self):
            return self.portatil

        def get_current_version(self):
            return "1.1.0"

        def check_for_updates(self):
            return None

    for portatil, esperado in ((False, 1), (True, 0)):
        chamadas = []
        atualizacao.rodar_ao_ligar(atualizacao.Fonte("C:/nao-existe"), gerente=Gerente(portatil),
                                   preparar=lambda g: True, motor=lambda: chamadas.append(1) or True)
        assert len(chamadas) == esperado


def test_conserto4_o_programa_instalado_procura_o_motor_so_no_lugar_dele(tmp_path, monkeypatch):
    """O programa instalado pelo Velopack procura o motor em <raiz>\motor-kraken\<versao> (e nao mais em
    current\motor-kraken, que a atualizacao sem o motor nunca tem); o teste rapido depois da troca usa a mesma busca
    e a mesma conferencia."""
    import sys

    from core import ocr_kraken, pasta_das_ferramentas

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    monkeypatch.setattr(pasta_das_ferramentas, "empacotado", lambda: True)
    monkeypatch.setattr(atualizacao, "instalado_pelo_velopack", lambda: True)
    monkeypatch.setattr(atualizacao, "pasta_do_programa", lambda: current)
    assert ocr_kraken.lugares_do_motor() == [raiz / "motor-kraken" / "1"]
    assert ocr_kraken.achar_pasta_do_motor() is None
    (current / "tesseract").mkdir()
    (current / "tesseract" / "tesseract.exe").write_bytes(b"MZ")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    atualizacao.teste_rapido()
    assert "falta o motor do Kraken" in _registro()
    atualizacao.garantir_o_motor(raiz, current)
    assert ocr_kraken.achar_pasta_do_motor() == raiz / "motor-kraken" / "1"
    atualizacao.caminho_do_registro().unlink()
    atualizacao.teste_rapido()
    assert "motor do Kraken" not in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# Volta 2 (relatorio 1 de quem tentou quebrar)
# ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("estrago", ["fluxo invalido", "cortado"])
def test_volta2_medio1_arquivo_do_motor_estragado_de_qualquer_jeito_e_apagado_e_registrado(tmp_path, estrago):
    """Medio 1 do relatorio 1 (21/11/2026): com o pedaco comprimido de um arquivo invalido (zlib.error) ou o arquivo do
    motor cortado no meio, o erro escapava de garantir_o_motor: sobrava o motor-kraken\.chegando-1 pela metade, o
    registro nao dizia nada e o ajudante desistia antes de procurar a versao nova. A promessa ("qualquer erro: apaga o
    provisorio, registra e devolve False") tem de valer para todo erro."""
    import zipfile

    import versao
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    arquivo = current / atualizacao.PASTA_DO_QUE_SE_INSTALA / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    with zipfile.ZipFile(arquivo) as z:
        conteudo = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(arquivo, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in conteudo.items():
            z.writestr(nome, dados)
    with zipfile.ZipFile(arquivo) as z:
        info = max(z.infolist(), key=lambda i: i.compress_size)
    dados = bytearray(arquivo.read_bytes())
    comeco = info.header_offset + 30 + len(info.filename.encode("utf-8")) + len(info.extra)
    if estrago == "fluxo invalido":
        dados[comeco] = 0xFF                  # bloco do deflate de tipo invalido: zlib.error ao abrir
    else:
        dados[comeco + 1:comeco + info.compress_size] = b"\x00" * (info.compress_size - 1)
    arquivo.write_bytes(bytes(dados))
    assert atualizacao.garantir_o_motor(raiz, current) is False
    assert not (raiz / "motor-kraken" / ".chegando-1").exists(), "sobrou o provisório pela metade"
    assert not (raiz / "motor-kraken" / "1").exists()
    assert "motor do Kraken: não deu para pôr no lugar" in _registro()


def test_volta2_medio1_um_erro_no_motor_nao_impede_o_ajudante_de_procurar():
    """Medio 1: um erro inesperado ao por o motor no lugar nao faz o ajudante desistir de procurar a versao nova."""
    procurou = []

    class Gerente:
        def get_is_portable(self):
            return False

        def get_current_version(self):
            return "1.1.0"

        def check_for_updates(self):
            procurou.append(1)
            return None

    def quebra():
        raise RuntimeError("erro que ninguém esperava")

    assert atualizacao.rodar_ao_ligar(atualizacao.Fonte("C:/nao-existe"), gerente=Gerente(),
                                      preparar=lambda g: True, motor=quebra) == 0
    assert procurou == [1]


@pytest.mark.parametrize("aberto", [True, False])
def test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada(tmp_path, aberto):
    """Medio 2 do relatorio 1 (21/11/2026): sem o motor no lugar (ex.: falta de espaco), ficava gravado "pendente", e a
    tela mostrava "Chegou uma versao nova" para sempre; "Reiniciar agora" voltava na mesma versao; com "Depois", toda
    abertura mostrava a janelinha e nao trocava. Agora, sem o motor no lugar, a versao nao e baixada nem anunciada (nada
    na tela, nenhum texto novo); a abertura nao tenta trocar; o ajudante tenta de novo da proxima vez."""
    from tests.test_decisoes_atualizacao import PUBLICA, GerenteFalso, _servidor

    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    atualizacao.gravar_estado({"fase": "pendente", "nova": "1.2.0", "anterior": "1.1.0"})   # o aviso de antes
    resultado = atualizacao.procurar_e_preparar(gerente, fonte, lambda: aberto, chave_publica=PUBLICA,
                                                motor_no_lugar=lambda: False)
    assert resultado == "sem-motor"
    assert not gerente.baixou and gerente.trocou == []
    estado = atualizacao.ler_estado()
    assert atualizacao.o_que_avisar(estado, "1.1.0", set()) is None, "a tela anunciou uma versão que não entra"
    comum = dict(instalado=lambda: True, conta_de_testes=lambda: False, portatil=lambda: False,
                 ler=atualizacao.ler_estado, versao_atual=lambda: "1.1.0")
    assert atualizacao.trocar_antes_de_abrir([], trocar=lambda: pytest.fail("tentou trocar"), **comum) is False
    assert "motor do Kraken" in _registro()
    # com o motor no lugar, tudo volta ao normal
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: aberto, chave_publica=PUBLICA,
                                           motor_no_lugar=lambda: True) == ("pendente" if aberto else "aplicando")


def test_volta2_medio3_visual_c_mais_novo_numa_versao_nova_nao_traz_a_pergunta_de_volta(windows_de_mentira):
    """Medio 3 do relatorio 1 (21/11/2026), contra a D-741 ("Depois do 'Sim', nunca mais aparece") e a D-735 ("Nas
    atualizacoes seguintes, nenhuma pergunta"): depois do "Sim", uma versao nova com um Visual C++ mais novo fazia a
    leitura ver "falta o Visual C++" antes de o ajudante instala-lo, e a pergunta do Windows voltava. Agora a abertura so
    pergunta de novo pelo que so a pergunta faz (as tarefas do ajudante e do desfazer); o Visual C++ e a instalacao
    antiga o proprio ajudante completa, como o sistema, sem perguntar (preparar_o_computador, a cada vez que roda)."""
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True) == []
    windows_de_mentira.visual_c = None                      # a versao nova trouxe um Visual C++ mais novo
    windows_de_mentira.inno = {"pasta": Path("C:/Antiga"), "desinstalador": Path("C:/Antiga/unins000.exe")}
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=False) == []
    assert len(windows_de_mentira.pedidos) == 1, "a pergunta do Windows voltou depois do \"Sim\""


def test_volta3_item1_depois_do_sim_com_o_windows_que_nao_deixa_ler_a_pergunta_volta(windows_de_mentira, monkeypatch):
    """Volta 3, item 1 (D-826, Samuel 22/11/2026: "no caso raro a pergunta volta sempre"; era
    test_volta2_medio3_windows_que_nao_deixa_ler_nao_traz_a_pergunta_de_volta, que cobrava o contrario): quando o Windows
    nao deixa ler as tarefas ("nao deu para saber"), a pergunta volta, mesmo depois de um "Sim" (sem uma anotacao, o
    programa nao sabe que o "Sim" ja foi dado); o registro diz o que nao deu para ler. Nas duas tarefas."""
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True) == []
    for tarefa in (atualizacao.NOME_DA_TAREFA, td.nome_da_tarefa_do_desfazer()):
        lida = windows_de_mentira.tarefas[tarefa]
        windows_de_mentira.tarefas[tarefa] = windows.Tarefa(tarefa, None, motivo="o PowerShell não respondeu")
        antes = len(windows_de_mentira.pedidos)
        atualizacao.preparar_ao_abrir(None, primeira_vez=False)
        assert len(windows_de_mentira.pedidos) == antes + 1, f"{tarefa}: não deu para ler e a pergunta não voltou"
        windows_de_mentira.tarefas[tarefa] = lida
    assert "não deu para ler o ajudante" in _registro() and "não deu para ler a tarefa do desfazer" in _registro()


def test_volta3_item1_depois_do_nao_com_o_windows_que_nunca_deixa_ler_a_pergunta_volta_a_cada_abertura(
        windows_de_mentira, monkeypatch):
    """Volta 3, item 1 (D-826; D-741: depois do "Nao", a pergunta volta a cada abertura). Defeito do relatorio 2 de quem
    tentou quebrar, (b): depois de um "Nao", com a leitura das tarefas falhando sempre (ex.: um antivirus que barra o
    PowerShell), tres aberturas seguidas nao perguntavam nada: a pergunta nunca mais voltava e nenhuma versao chegava.
    Agora volta em cada abertura; e o ajudante (que nao existe) nao e chamado."""
    windows_de_mentira.respostas = ["nao"] * 4
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True)
    monkeypatch.setattr(atualizacao, "ler_tarefa_no_windows",
                        lambda nome: windows.Tarefa(nome, None, motivo="o PowerShell não respondeu"))
    for _abertura in range(3):
        assert atualizacao.preparar_ao_abrir(None, primeira_vez=False)
    assert len(windows_de_mentira.pedidos) == 4, "depois do \"Não\", a pergunta não voltou em cada abertura"
    assert windows_de_mentira.ajudante_rodou == 0, "chamou um ajudante que o Windows não mostrou"


def test_volta2_medio3_depois_do_nao_a_pergunta_continua_voltando(windows_de_mentira):
    """D-741 continua: depois de um "Nao" (as tarefas nao existem), a pergunta volta na abertura seguinte."""
    windows_de_mentira.respostas = ["nao", "sim"]
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=True)
    assert atualizacao.preparar_ao_abrir(None, primeira_vez=False) == []
    assert len(windows_de_mentira.pedidos) == 2



def test_volta2_item4_a_conferencia_do_ajudante_e_a_da_peca_com_a_licenca(windows_de_mentira, monkeypatch):
    """Item 4 da volta 2 (baixo 3 do relatorio 1; CLAUDE.md §11.12, uma peca so): "o ajudante e o deste programa?" usa
    a conferencia da peca unica (core.windows.problemas_da_tarefa_criada), que confere tambem quem pode mandar rodar.
    Um ajudante sem a licenca das contas comuns (o programa do Kaique nao conseguiria chama-lo) conta como falta; a
    licenca que nao deu para ler nao traz a pergunta de volta (medio 3)."""
    windows_de_mentira.pedir([])
    chamadas = []
    original = windows.problemas_da_tarefa_criada
    monkeypatch.setattr(windows, "problemas_da_tarefa_criada", lambda xml, lida: chamadas.append(1) or original(xml, lida))
    assert atualizacao.o_que_falta_no_computador() == [] and chamadas == [1]
    nome = atualizacao.NOME_DA_TAREFA
    sem_as_contas_comuns = "D:(A;;FA;;;BA)(A;;FA;;;SY)"
    windows_de_mentira.tarefas[nome] = windows.Tarefa(nome, True, True, comando=str(windows_de_mentira.exe),
                                                      argumentos=atualizacao.ARG_PROCURAR,
                                                      usuario=windows.SID_SISTEMA, licenca=sem_as_contas_comuns)
    assert atualizacao.o_que_falta_no_computador(), "o ajudante que a conta do Kaique não chama passou"
    windows_de_mentira.tarefas[nome] = windows.Tarefa(nome, True, True, comando=str(windows_de_mentira.exe),
                                                      argumentos=atualizacao.ARG_PROCURAR,
                                                      usuario=windows.SID_SISTEMA, licenca="")
    assert atualizacao.o_que_falta_no_computador() == []
    assert "licença" in _registro()
    assert "_mesmo_caminho" not in Path(atualizacao.__file__).read_text(encoding="utf-8"), "a conta própria saiu"
