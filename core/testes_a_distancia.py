"""Liga e desliga os testes a distancia no notebook do Kaique.

De onde vem (frente do notebook do Kaique, 16/11/2026; decisoes no Livro
docs/plano/DECISOES.md):
  D-705  testes a distancia pelo comando de longe do Windows (Servidor
         OpenSSH), SO pela rede do Tailscale, SEM porta de API dentro do
         programa; uma opcao nas Configuracoes liga e desliga.
  D-711  liga sozinho com o Windows; entra com SENHA, nao com chave.
  D-712  a opcao vem LIGADA DE FABRICA; o instalador nao pergunta nada.
  D-717  conta do Windows SO para os testes, SEM administrador, ESCONDIDA da
         tela de entrada; os projetos de teste nunca se misturam com os do
         Kaique.
  D-721  na primeira abertura, uma janela pede a senha; sem senha, os testes
         ficam desligados; da para por a senha depois nas Configuracoes.
  D-722  testar no PC do Samuel e, no fim, DESFAZER tudo (etapa 5).

A REGRA NUM LUGAR SO (CLAUDE.md 11.12, sem gambiarra). Este arquivo e o unico
lugar que sabe QUAIS comandos ligam, desligam e desfazem os testes a distancia.
Todos os caminhos da tela (a janela da senha na primeira abertura, a caixinha
das Configuracoes, o botao "Por a senha") chamam `ligar`/`desligar` daqui -
nenhum monta comando por conta propria.

A PECA QUE FALA COM O WINDOWS esta isolada em `Executor`. `ExecutorWindows` e
a de verdade (uma pergunta de administrador so, para todos os passos). Os
testes trocam o executor por um de mentira que anota os comandos que SERIAM
dados, sem tocar o Windows. Por isso nada aqui muda o computador por si: quem
muda e o `ExecutorWindows`, e so na producao.

A SENHA nunca aparece na linha de comando (outros programas enxergariam a
linha de comando). Nos passos ela e a variavel `$SenhaDosTestes`; o
`ExecutorWindows` a entrega por dentro, cifrada pelo proprio Windows (DPAPI da
conta do usuario), e nao a guarda em lugar nenhum alem da conta criada com ela.

Este arquivo NAO importa nada de ui/ (core/__init__.py). Importa `configuracoes`
(raiz, nao ui/) so para lembrar o estado da opcao, como fazem outros assuntos.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

import configuracoes

# --- nomes fixos (caminho em disco / Windows, SEM acento) --------------------
# Mudar qualquer um destes muda a conta, a regra do firewall ou a chave do
# registro que o programa cria no Windows. Nao mudar sem o Samuel.
NOME_DA_CONTA = "EditorTestes"            # a conta so dos testes (D-717)
NOME_DA_REGRA = "EditorImpressao-Testes"  # a regra do firewall que abre so o Tailscale (D-705)
REGRA_LARGA_DO_OPENSSH = "OpenSSH-Server-In-TCP"  # a que a instalacao cria e libera a porta a todos
CAPACIDADE_OPENSSH = "OpenSSH.Server~~~~0.0.1.0"   # o recurso do Windows a instalar
SID_USUARIOS = "S-1-5-32-545"             # o grupo "Usuarios" (sem administrador), igual em qualquer idioma
PORTA_SSH = 22
# A faixa de enderecos do Tailscale (IPv4 100.64.0.0/10 e IPv6; tailscale.com/kb/1015).
# SO estes entram; o Wi-Fi da casa (ex.: 192.168.x) nao (D-705).
FAIXAS_DO_TAILSCALE = "100.64.0.0/10,fd7a:115c:a1e0::/48"
PLACA_DO_TAILSCALE = "Tailscale"          # prende a regra a placa do Tailscale
SSHD_CONFIG = r"C:\ProgramData\ssh\sshd_config"
CHAVE_USERLIST = (r"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                  r"\Winlogon\SpecialAccounts\UserList")
VARIAVEL_DA_SENHA = "$SenhaDosTestes"     # o lugar da senha nos passos (NUNCA o texto dela)

# Chaves das Configuracoes (configuracoes.PADROES tem os valores de fabrica).
CHAVE_LIGADO = "testes_a_distancia_ligado"              # intencao do Kaique (de fabrica True, D-712)
CHAVE_PRONTO = "testes_a_distancia_pronto"              # o lado do Windows ja foi montado?
CHAVE_SENHA_PERGUNTADA = "testes_a_distancia_senha_perguntada"  # a janela da 1a vez ja apareceu?


@dataclass
class Passo:
    """Um passo do plano: o que ele faz (em portugues) e o comando do Windows.

    `precisa_senha` marca o passo que usa `$SenhaDosTestes` - a prova confere
    que a senha nunca vira texto no comando.
    """

    nome: str
    comando: str
    precisa_senha: bool = False


@dataclass
class Resultado:
    """O que o executor devolve.

    ok          deu certo (todos os passos aplicados).
    cancelado   a pessoa disse "Nao" a pergunta do Windows (erro 1223): nada
                foi instalado (D-705/estudo 2.3).
    mensagem    frase em portugues para a tela, quando nao deu certo (regra 3.3:
                nunca rastro de erro na tela).
    passos      o que foi (ou seria) feito, para o registro "o que o teste fez".
    """

    ok: bool
    cancelado: bool = False
    mensagem: str = ""
    passos: list[Passo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# A REGRA: os tres planos de comandos (um lugar so)
# ---------------------------------------------------------------------------

def plano_de_ligar() -> list[Passo]:
    """Os passos para ligar os testes a distancia, na ordem (estudo 2.2).

    Tudo com o que o proprio Windows traz, igual no Home e no Pro. A senha
    entra como `$SenhaDosTestes` (o executor a fornece por dentro).
    """
    return [
        Passo("Instalar o Servidor OpenSSH do Windows",
              f"Add-WindowsCapability -Online -Name {CAPACIDADE_OPENSSH}"),
        Passo("Deixar o Servidor OpenSSH ligando sozinho com o Windows (D-711)",
              "Set-Service -Name sshd -StartupType Automatic; Start-Service -Name sshd"),
        # Firewall so para o Tailscale (D-705): fecha a regra larga que a
        # instalacao cria (libera a porta a todos) e abre uma nossa so para a
        # faixa do Tailscale, presa a placa do Tailscale. O Wi-Fi da casa nao entra.
        Passo("Fechar a porta para todo mundo (regra larga do OpenSSH)",
              f"Disable-NetFirewallRule -Name {REGRA_LARGA_DO_OPENSSH}"),
        Passo("Abrir a porta so para a rede do Tailscale (D-705)",
              f"New-NetFirewallRule -Name {NOME_DA_REGRA}"
              f" -DisplayName 'Editor de Impressao - testes a distancia'"
              f" -Direction Inbound -Protocol TCP -LocalPort {PORTA_SSH}"
              f" -RemoteAddress {FAIXAS_DO_TAILSCALE}"
              f" -InterfaceAlias {PLACA_DO_TAILSCALE} -Action Allow"),
        # A conta so dos testes (D-717): sem administrador (New-LocalUser nao
        # poe em nenhum grupo; acrescentamos SO ao grupo Usuarios pelo SID, que
        # e igual em qualquer idioma do Windows). A senha e $SenhaDosTestes.
        Passo("Criar a conta so dos testes, sem poder de administrador (D-717)",
              f"New-LocalUser -Name {NOME_DA_CONTA} -Password {VARIAVEL_DA_SENHA}"
              f" -FullName 'Testes do Editor de Impressao'"
              f" -Description 'Conta so para os testes a distancia'"
              f" -AccountNeverExpires -PasswordNeverExpires;"
              f" Add-LocalGroupMember -SID {SID_USUARIOS} -Member {NOME_DA_CONTA}",
              precisa_senha=True),
        # Esconder da tela de entrada (D-717): valor 0 (DWORD) no UserList.
        Passo("Esconder a conta de testes da tela de entrada (D-717)",
              f"New-Item -Path '{CHAVE_USERLIST}' -Force | Out-Null;"
              f" New-ItemProperty -Path '{CHAVE_USERLIST}' -Name {NOME_DA_CONTA}"
              f" -Value 0 -PropertyType DWord -Force | Out-Null"),
        # So a conta de testes entra pelo comando de longe (nem a conta do
        # Kaique); entra com senha, nao chave (D-711).
        Passo("Deixar entrar pelo comando de longe so a conta de testes (D-711)",
              f"Add-Content -Path '{SSHD_CONFIG}' -Value"
              f" \"`nAllowUsers {NOME_DA_CONTA}`nPasswordAuthentication yes`nMaxAuthTries 3\";"
              f" Restart-Service -Name sshd"),
    ]


def plano_de_desligar() -> list[Passo]:
    """Os passos para desligar: para o servico e fecha a entrada (estudo 2.4).

    A conta e os projetos de teste ficam guardados (a conta so e desativada).
    """
    return [
        Passo("Parar o Servidor OpenSSH e tira-lo do arranque do Windows",
              "Stop-Service -Name sshd -ErrorAction SilentlyContinue;"
              " Set-Service -Name sshd -StartupType Disabled"),
        Passo("Fechar a porta do Tailscale (apagar a regra do firewall)",
              f"Remove-NetFirewallRule -Name {NOME_DA_REGRA} -ErrorAction SilentlyContinue"),
        Passo("Desativar a conta de testes (os projetos de teste ficam guardados)",
              f"Disable-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue"),
    ]


def plano_de_desfazer() -> list[Passo]:
    """Os passos para desfazer TUDO (etapa 5, D-722): tira o OpenSSH, apaga a
    conta e o perfil, limpa o registro e o sshd_config.

    So a etapa 5 roda isto, no PC do Samuel, e com a lista do que foi desfeito.
    O que fazer ao DESINSTALAR o programa ainda nao esta decidido (pergunta ao
    Samuel): NAO entra aqui como automatico.
    """
    passos = list(plano_de_desligar())
    passos += [
        Passo("Apagar a conta de testes",
              f"Remove-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue"),
        Passo("Apagar o perfil da conta de testes",
              f"Get-CimInstance Win32_UserProfile | Where-Object {{ $_.LocalPath -like '*\\{NOME_DA_CONTA}' }}"
              f" | Remove-CimInstance -ErrorAction SilentlyContinue"),
        Passo("Tirar a conta de testes do registro (UserList)",
              f"Remove-ItemProperty -Path '{CHAVE_USERLIST}' -Name {NOME_DA_CONTA}"
              f" -ErrorAction SilentlyContinue"),
        Passo("Devolver o sshd_config (tirar as linhas acrescentadas)",
              f"(Get-Content '{SSHD_CONFIG}') | Where-Object {{ $_ -notmatch"
              f" 'AllowUsers {NOME_DA_CONTA}|PasswordAuthentication yes|MaxAuthTries 3' }}"
              f" | Set-Content '{SSHD_CONFIG}'"),
        Passo("Tirar o Servidor OpenSSH do Windows",
              f"Remove-WindowsCapability -Online -Name {CAPACIDADE_OPENSSH}"),
    ]
    return passos


# ---------------------------------------------------------------------------
# A PECA QUE FALA COM O WINDOWS (isolada; os testes a trocam)
# ---------------------------------------------------------------------------

class Executor:
    """A peca que aplica os passos no Windows.

    `aplicar` recebe os passos e a senha, aplica TODOS numa pergunta de
    administrador so, e devolve um Resultado. Os testes implementam uma de
    mentira que so anota os comandos.
    """

    def aplicar(self, passos: list[Passo], senha: str) -> Resultado:  # pragma: no cover
        raise NotImplementedError


class ExecutorWindows(Executor):
    """A de verdade: uma pergunta de administrador so para todos os passos.

    ATENCAO: so roda na producao. Sob o pytest (PYTEST_CURRENT_TEST no
    ambiente) ela se RECUSA a rodar, para nenhum teste tocar o Windows por
    engano - alem de os testes ja trocarem o executor por um de mentira.

    A etapa 5 (no PC do Samuel, D-722) e quem prova isto de verdade; a ligacao
    com o runas e a passagem da senha por dentro (DPAPI) estao marcadas como
    ressalva no relatorio.
    """

    def aplicar(self, passos: list[Passo], senha: str) -> Resultado:
        if "PYTEST_CURRENT_TEST" in os.environ:
            raise RuntimeError(
                "ExecutorWindows nao roda sob o pytest: troque por um de mentira.")
        if sys.platform != "win32":
            return Resultado(False, mensagem="Os testes a distancia so funcionam no Windows.")
        from core._testes_a_distancia_windows import aplicar_no_windows

        return aplicar_no_windows(passos, senha)


# O executor de hoje. Troca-se com `definir_executor` (os testes poem um de
# mentira; a producao usa o ExecutorWindows).
_executor: Executor = ExecutorWindows()


def definir_executor(executor: Executor) -> None:
    """Troca a peca que fala com o Windows (os testes poem a de mentira)."""
    global _executor
    _executor = executor


def executor_atual() -> Executor:
    """A peca que fala com o Windows agora."""
    return _executor


# ---------------------------------------------------------------------------
# O ESTADO (nas Configuracoes)
# ---------------------------------------------------------------------------

def esta_ligado() -> bool:
    """A opcao esta marcada? De fabrica True (D-712)."""
    return bool(configuracoes.ler(CHAVE_LIGADO))


def esta_pronto() -> bool:
    """O lado do Windows ja foi montado (a conta existe, o OpenSSH liga)?"""
    return bool(configuracoes.ler(CHAVE_PRONTO))


def senha_ja_perguntada() -> bool:
    """A janela da senha da primeira vez ja apareceu?"""
    return bool(configuracoes.ler(CHAVE_SENHA_PERGUNTADA))


def marcar_senha_perguntada() -> None:
    """Lembra que a janela da primeira vez ja apareceu (D-721)."""
    configuracoes.escrever(CHAVE_SENHA_PERGUNTADA, True)


# ---------------------------------------------------------------------------
# A PORTA UNICA que a tela usa (ligar / desligar)
# ---------------------------------------------------------------------------

def ligar(senha: str) -> Resultado:
    """Liga os testes a distancia com a senha dada (D-705, D-711, D-712, D-717).

    Monta o plano (um lugar so), manda o executor aplicar numa pergunta de
    administrador so, e guarda o estado. Sem senha, nao faz nada (D-721).
    Todos os caminhos da tela chamam esta funcao.
    """
    if not senha:
        # Sem senha os testes ficam desligados (D-721): nada e instalado.
        configuracoes.escrever(CHAVE_PRONTO, False)
        return Resultado(False, mensagem="Sem a senha, os testes à distância ficam desligados. "
                                         "Você pode pôr a senha depois nas Configurações.")
    passos = plano_de_ligar()
    resultado = executor_atual().aplicar(passos, senha)
    if resultado.ok:
        configuracoes.escrever(CHAVE_LIGADO, True)
        configuracoes.escrever(CHAVE_PRONTO, True)
    elif resultado.cancelado:
        # Disse "Nao" a pergunta do Windows: nada foi instalado, a opcao fica
        # DESLIGADA, com um aviso em portugues (pedido do Samuel; estudo 2.3).
        configuracoes.escrever(CHAVE_LIGADO, False)
        configuracoes.escrever(CHAVE_PRONTO, False)
        if not resultado.mensagem:
            resultado.mensagem = ("Nada foi instalado. Os testes à distância continuam desligados. "
                                  "Você pode ligar depois nas Configurações.")
    return resultado


def desligar() -> Resultado:
    """Desliga os testes a distancia: para o servico e fecha a entrada (D-705).

    A conta e os projetos de teste ficam guardados (estudo 2.4).
    """
    resultado = executor_atual().aplicar(plano_de_desligar(), senha="")
    configuracoes.escrever(CHAVE_LIGADO, False)
    return resultado
