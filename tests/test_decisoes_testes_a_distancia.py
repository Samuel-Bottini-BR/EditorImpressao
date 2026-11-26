"""Provas das decisões dos testes à distância (frente do notebook do Kaique, 16/11/2026).

Cada teste prova uma decisão do Livro (docs/plano/DECISOES.md) com a peça que fala com o Windows
trocada por uma DE MENTIRA, que só anota os comandos que SERIAM dados - nada toca o Windows.

  D-705  só pelo Tailscale, sem porta de API no programa; liga/desliga nas Configurações
  D-711  liga sozinho com o Windows; entra com senha, não chave
  D-712  opção ligada de fábrica; o instalador não pergunta nada
  D-717  conta separada, sem administrador, escondida da tela de entrada
  D-721  janela da senha na primeira abertura; sem senha, nada liga; pôr a senha depois

A senha nunca pode aparecer na linha de comando (um teste cobra isto em todos os passos).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import configuracoes
from core import testes_a_distancia as td

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def dados(tmp_path, monkeypatch):
    """Uma pasta de dados só deste teste, para as Configurações nascerem limpas."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("APPDATA", raising=False)
    return tmp_path


class FakeExecutor(td.Executor):
    """A peça que fala com o Windows, de mentira: anota os passos, não toca o Windows."""

    def __init__(self, ok: bool = True, cancelado: bool = False) -> None:
        self.chamadas: list[tuple[list[td.Passo], str]] = []
        self._ok = ok
        self._cancelado = cancelado

    def aplicar(self, passos: list[td.Passo], senha: str) -> td.Resultado:
        self.chamadas.append((list(passos), senha))
        if self._cancelado:
            return td.Resultado(False, cancelado=True, passos=passos)
        return td.Resultado(self._ok, passos=passos)


@pytest.fixture
def fake(monkeypatch):
    """Põe o executor de mentira (auto-restaurado no fim do teste)."""
    f = FakeExecutor()
    monkeypatch.setattr(td, "_executor", f)
    return f


# --- D-712: ligada de fábrica, instalador não pergunta nada ----------------------------------

def test_d712_opcao_ligada_de_fabrica(dados):
    """D-712: "já vem selecionado de fabrica". Config limpa → a opção vem ligada."""
    assert configuracoes.PADROES["testes_a_distancia_ligado"] is True
    assert td.esta_ligado() is True
    assert td.esta_pronto() is False, "sem senha ainda, o lado do Windows não está montado"


def test_d712_instalador_nao_pergunta_nada():
    """D-712: "o instalador não pergunta nada disso". O instalador não cita os testes à distância."""
    iss = (RAIZ / "instalador.iss").read_text(encoding="utf-8", errors="replace").lower()
    for palavra in ("openssh", "tailscale", "testes à distância", "testes a distancia",
                    "sshd", "distância"):
        assert palavra not in iss, f"o instalador cita '{palavra}' (D-712: não pode)"


# --- D-721: a janela da senha na primeira abertura, sem senha nada liga -----------------------

def test_d721_primeira_vez_pede_a_senha_e_liga(dados, fake, monkeypatch):
    """D-721: na primeira abertura, a janela da senha aparece uma vez; na segunda, não aparece sozinha.
    Adaptado pela D-836, com a D-825 (21/11/2026, opção B: "ok"): nesta versão a senha digitada NÃO liga os testes
    (o nome do teste ficou o de antes); e, pela D-834, a janela da senha não faz mais pergunta do Windows."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    vezes = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: (vezes.append(1), "segredo")[1])
    assert not td.senha_ja_perguntada()

    tdui.primeira_vez_se_preciso(None, instalado=lambda: True)  # D-728: so no programa instalado
    assert vezes == [1], "a janela da senha apareceu uma vez"
    assert td.senha_ja_perguntada() and not td.esta_pronto()
    assert fake.chamadas == [], "D-825: a senha não liga nada; D-834: nenhuma pergunta do Windows daqui"

    tdui.primeira_vez_se_preciso(None, instalado=lambda: True)
    assert vezes == [1], "na segunda abertura a janela não aparece sozinha"


def test_d721_sem_senha_nada_liga(dados, fake, monkeypatch):
    """D-721: "Sem essa senha, os testes à distância ficam desligados". Ninguém toca o Windows."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)
    tdui.primeira_vez_se_preciso(None)
    assert fake.chamadas == [], "sem senha, o Windows não é tocado"
    assert td.esta_pronto() is False


def test_ligar_sem_senha_nao_chama_o_windows(dados, fake):
    """A porta única `ligar("")` não chama o executor e avisa em português."""
    resultado = td.ligar("")
    assert fake.chamadas == []
    assert not resultado.ok and "senha" in resultado.mensagem.lower()
    assert td.esta_pronto() is False


# --- os comandos exatos de ligar (D-705, D-711, D-717) ---------------------------------------

def test_ligar_da_os_comandos_esperados(dados, fake):
    """Ligar dá, numa pergunta de administrador só, os comandos certos:
    OpenSSH, serviço automático, firewall só Tailscale, conta sem administrador e escondida."""
    resultado = td.ligar("segredo-do-samuel")
    assert resultado.ok and td.esta_pronto()
    assert len(fake.chamadas) == 1, "uma pergunta de administrador só (todos os passos juntos)"
    passos, senha = fake.chamadas[0]
    texto = "\n".join(p.comando for p in passos)

    # D-705/estudo: instala o OpenSSH, liga sozinho com o Windows
    assert "Add-WindowsCapability" in texto and "OpenSSH.Server" in texto
    assert "Set-Service -Name sshd -StartupType Automatic" in texto
    # D-705: firewall só para o Tailscale, e a regra larga do OpenSSH é fechada
    assert "100.64.0.0/10" in texto, "abre para a faixa do Tailscale"
    assert "Disable-NetFirewallRule -Name OpenSSH-Server-In-TCP" in texto
    assert "New-NetFirewallRule" in texto and td.NOME_DA_REGRA in texto
    # D-717: a conta de testes, SEM administrador e ESCONDIDA da tela de entrada
    assert "New-LocalUser" in texto and td.NOME_DA_CONTA in texto
    assert "Administ" not in texto, "a conta de testes não entra no grupo de administradores (D-717)"
    assert td.SID_USUARIOS in texto, "a conta vai só para o grupo Usuários"
    assert "UserList" in texto and f"-Name {td.NOME_DA_CONTA} -Value 0" in texto
    # D-711: só a conta de testes entra pelo comando de longe, com senha (não chave)
    assert f"AllowUsers {td.NOME_DA_CONTA}" in texto
    assert "PasswordAuthentication yes" in texto
    assert "PubkeyAuthentication" not in texto, "entra com senha, não chave (D-711)"


def test_a_senha_nunca_aparece_no_comando(dados, fake):
    """A senha nunca vira texto num comando (outros programas enxergam a linha de comando)."""
    resultado = td.ligar("MinhaSenhaSecreta123")
    passos, senha = fake.chamadas[0]
    assert senha == "MinhaSenhaSecreta123", "a senha chega ao executor por fora dos comandos"
    for passo in passos:
        assert "MinhaSenhaSecreta123" not in passo.comando
    # o passo que usa a senha a referencia pela variável, não pelo texto
    com_senha = [p for p in passos if p.precisa_senha]
    assert com_senha and all(td.VARIAVEL_DA_SENHA in p.comando for p in com_senha)


# --- disse "Não" à pergunta do Windows: nada muda -------------------------------------------

def test_disse_nao_nada_e_instalado(dados, monkeypatch):
    """Se a pessoa disser "Não" ao Windows, nada é instalado e a opção fica desligada, com aviso."""
    monkeypatch.setattr(td, "_executor", FakeExecutor(cancelado=True))
    resultado = td.ligar("segredo")
    assert resultado.cancelado and not resultado.ok
    assert resultado.mensagem, "há um aviso em português"
    assert td.esta_pronto() is False
    assert td.esta_ligado() is False, "a opção fica desligada quando o Windows é recusado"


# --- desligar fecha ---------------------------------------------------------------------------

def test_desligar_para_o_servico_e_fecha_a_entrada(dados, fake):
    """Desligar: para o serviço, fecha a porta e desativa a conta; a opção fica desligada."""
    td.ligar("segredo")
    fake.chamadas.clear()
    resultado = td.desligar()
    assert resultado.ok
    assert td.esta_ligado() is False
    passos, _ = fake.chamadas[0]
    texto = "\n".join(p.comando for p in passos)
    assert "Stop-Service -Name sshd" in texto
    assert "Set-Service -Name sshd -StartupType Disabled" in texto
    assert f"Remove-NetFirewallRule -Name {td.NOME_DA_REGRA}" in texto
    assert f"Disable-LocalUser -Name {td.NOME_DA_CONTA}" in texto


# --- desfazer tudo (etapa 5, D-722): a peça sabe o que desfazer ------------------------------

def test_desfazer_tira_a_conta_e_o_openssh(dados):
    """D-722 (etapa 5): o plano de desfazer apaga a conta, o perfil, o registro e tira o OpenSSH."""
    texto = "\n".join(p.comando for p in td.plano_de_desfazer())
    assert f"Remove-LocalUser -Name {td.NOME_DA_CONTA}" in texto
    assert "Win32_UserProfile" in texto
    assert "Remove-ItemProperty" in texto and "UserList" in texto
    assert "Remove-WindowsCapability" in texto and "OpenSSH.Server" in texto


# --- o executor de verdade não roda sob o pytest (proteção) ----------------------------------

def test_executor_de_verdade_se_recusa_sob_o_pytest(dados):
    """O ExecutorWindows nunca toca o Windows durante os testes."""
    with pytest.raises(RuntimeError):
        td.ExecutorWindows().aplicar(td.plano_de_ligar(), "x")


# --- D-728 (16/11/2026): a janela da senha só no programa instalado pelo instalador -----------
# Palavras do Samuel, à pergunta "a janelinha aparece só no programa instalado pelo instalador
# [...] No seu atalho ela nunca aparece. Pode ser assim?": "ok, mas eu nunca criei nenhuma senha".
# A regra de "instalado" é a mesma da atualização: atualizacao.instalado_pelo_velopack.

def test_d728_pelo_codigo_nenhuma_janela_e_nada_marcado(dados, fake, monkeypatch):
    """D-728 (16/11/2026): aberto pelo código (atalho "(desenvolvimento)"), a janela da senha
    não aparece, nada liga e "senha já perguntada" NÃO é marcada - para o programa instalado
    continuar perguntando na primeira vez dele."""
    pytest.importorskip("PySide6")
    import atualizacao
    import ui.testes_a_distancia_ui as tdui

    assert atualizacao.instalado_pelo_velopack() is False, "sob o pytest o programa roda pelo código"
    vezes = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: (vezes.append(1), "segredo")[1])
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: None)

    tdui.primeira_vez_se_preciso(None)  # como o main.py chama: sem dizer nada de "instalado"
    assert vezes == [], "pelo código a janela da senha não pode aparecer (D-728)"
    assert fake.chamadas == [], "pelo código nada dos testes à distância liga (D-728)"
    assert td.senha_ja_perguntada() is False, "pelo código não marca 'senha já perguntada' (D-728)"
    assert td.esta_pronto() is False


def test_d728_instalado_primeira_vez_pede_a_senha(dados, fake, monkeypatch):
    """D-728 (16/11/2026): no programa instalado pelo instalador, na primeira vez, a janela da senha aparece (D-721).
    A janela é trocada por uma de mentira: nada abre na tela. Adaptado pela D-836 (D-825: a senha não liga nada;
    D-834: nenhuma pergunta do Windows a partir da janela da senha)."""
    pytest.importorskip("PySide6")
    import ui.testes_a_distancia_ui as tdui

    vezes = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: (vezes.append(1), "segredo")[1])
    assert not td.senha_ja_perguntada()

    tdui.primeira_vez_se_preciso(None, instalado=lambda: True)
    assert vezes == [1], "instalado, primeira vez: a janela da senha apareceu uma vez"
    assert td.senha_ja_perguntada() and not td.esta_pronto()
    assert fake.chamadas == []

    tdui.primeira_vez_se_preciso(None, instalado=lambda: True)
    assert vezes == [1], "na segunda abertura a janela não aparece sozinha"
