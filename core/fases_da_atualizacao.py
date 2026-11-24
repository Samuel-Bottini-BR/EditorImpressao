"""A regra da atualização pela internet: em que fase ela está e o que fazer com cada acontecimento.

Atualizador novo (D-830, 23/11/2026; plano em `relatorios/atualizador-novo/ONDE-PAREI.md`, seção 4.6). O desenho é o que
o Fable propôs e o Samuel aceitou ("refazer"): a regra é uma função só, sem disco, sem rede, sem Windows e sem tela,

    proxima_fase(estado, evento) -> (estado novo, efeitos)

e quem faz alguma coisa (perguntar ao Windows, procurar, baixar, trocar, mostrar o aviso) é o executor
(`atualizacao.Atualizacao`), que roda os efeitos que esta função devolve e manda de volta o que aconteceu como um evento
novo. Assim a decisão "o que vem agora" está num lugar só e é testada inteira, par por par
(`tests/test_fases_da_atualizacao.py` passa por todas as fases com todos os eventos).

AS FASES (`Fase`), na ordem em que costumam acontecer numa abertura do programa instalado:
    INICIO          ainda não abriu (só aceita `Abriu`).
    FORA            nada roda: pelo código, pacote portátil, ou a conta dos testes à distância (D-728, D-736, D-741).
    SEM_LICENCA     a pasta do programa não aceita gravação pela conta que abriu: a pergunta do Windows foi feita,
                    antes da janela (D-806, D-834); espera a resposta.
    PREPARANDO      a pessoa disse "Sim": o trabalho com licença (o ajudante antigo sai, o Visual C++, a instalação
                    antiga do Inno, a licença da pasta) roda por trás, com a janela já aberta.
    MOTOR           o motor do Kraken: sem ele no lugar, nada é anunciado (D-790, D-833).
    PROCURANDO      perguntando ao Velopack se há versão nova (só ao abrir, D-732).
    CONFERINDO      a assinatura do Samuel na versão achada, antes de baixar (D-724).
    BAIXANDO        baixando (o Velopack confere o tamanho e a soma do que baixou).
    PRONTA          baixada; o aviso "Reiniciar agora" / "Depois" está na tela (D-715, D-720).
    DEPOIS          escolheu "Depois": ao fechar, a pergunta "Atualizar agora?" (D-769, D-794, D-831, D-835).
    FECHANDO        escolheu "Reiniciar agora": a janela fecha pelo caminho de sempre (grava o trabalho).
    PERGUNTANDO     a pergunta "Atualizar agora?" ao fechar está na tela.
    TROCANDO        a troca foi pedida ao Velopack; o programa sai e ele troca (D-828).
    CONFERINDO_NOVA reaberto depois de uma troca: o teste rápido da versão nova, antes da janela (D-718).
    VOLTANDO        a versão nova não passou no teste: buscando e pedindo a anterior assinada (D-718).
    PARADO          nada mais a fazer nesta abertura.

A REGRA DO QUE NÃO FAZ SENTIDO: todo par (fase, evento) tem resposta. O que não faz sentido naquela fase (um "Escolheu"
quando nenhum aviso está na tela, um segundo "Abriu") fica na mesma fase e só vira uma linha no registro (`Registrar`);
nunca exceção. A única exceção a essa regra é o `Fechando` (fechar o programa): em qualquer fase sem versão pronta, fechar
é normal e não anota nada.

O QUE ESTE ARQUIVO NÃO FAZ: não lê arquivo, não fala com o Velopack nem com o Windows, não sabe de tela. Por isso só
importa `dataclasses`, `enum` e `typing` (um teste lê a árvore deste arquivo e cobra isso). A comparação de versões é a
mesma de `versao.numeros` ("1.2.3"), escrita aqui de novo só por esse motivo; versão fora do formato nunca conta como
mais nova (`_mais_nova`).

Seguro mexer: as frases do `Registrar` (vão só para o registro, nunca para a tela, e não levam número de decisão: K04).
Arriscado: qualquer transição. Cada uma protege uma decisão do Samuel e tem o seu caso na tabela do teste; mudar uma
sem mudar o teste faz o teste falhar (é para isso que ele existe). Em especial: (1) sem licença, `PedirLicenca` e nunca
`Procurar` (sem a licença, o Velopack pediria licença em toda troca, o jeito 2 que ele recusou); (2) `Baixar` só depois
de `Assinatura(certa)`; (3) `Trocar` só depois de a janela fechar ou do "Sim" ao fechar; (4) a versão que falhou entra em
`nao_tentar` e não é tentada de novo; (5) na conta de testes, `FORA`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Union


class Fase(str, Enum):
    """As fases da atualização numa abertura do programa (ver o topo do arquivo)."""

    INICIO = "inicio"
    FORA = "fora"
    SEM_LICENCA = "sem_licenca"
    PREPARANDO = "preparando"
    MOTOR = "motor"
    PROCURANDO = "procurando"
    CONFERINDO = "conferindo"
    BAIXANDO = "baixando"
    PRONTA = "pronta"
    DEPOIS = "depois"
    FECHANDO = "fechando"
    PERGUNTANDO = "perguntando"
    TROCANDO = "trocando"
    CONFERINDO_NOVA = "conferindo_nova"
    VOLTANDO = "voltando"
    PARADO = "parado"


# Os tipos de falha (um lugar só: o executor escolhe a frase da tela por eles, D-778).
FALHA_TESTE = "teste"          # a versão nova não passou no teste rápido e o programa voltou (frase 1)
FALHA_TROCA = "troca"          # o Velopack não conseguiu trocar; o programa continua na versão de antes (frase 1)
FALHA_RECUSADA = "recusada"    # a versão não tem a assinatura do Samuel (frase 2)
FALHA_VOLTA = "volta"          # a versão nova falhou e a volta para a anterior não deu certo (frase 3)
TIPOS_DE_FALHA = (FALHA_TESTE, FALHA_TROCA, FALHA_RECUSADA, FALHA_VOLTA)

# Como o Velopack reabre o programa depois de uma troca (um lugar só).
REABRIR_COM_JANELA = "com_janela"      # "Reiniciar agora": abre a versão nova com a janela
REABRIR_SEM_JANELA = "sem_janela"      # "Sim" ao fechar: só o teste rápido, sem janela; nada abre na tela (D-769)


def id_da_falha(tipo: str, versao: str) -> str:
    """O nome de uma falha anotada (a tela mostra cada uma uma vez só, pelo nome). Lugar único."""
    return f"{tipo}-{versao}"


# ---------------------------------------------------------------------------------------------------------------------
# O estado
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Estado:
    """Onde a atualização está nesta abertura: a fase, a versão que roda (`versao`), a nova achada ou que entrou
    (`nova`), a de antes da troca (`anterior`), as versões que já falharam (`nao_tentar`) e se este processo é a
    reabertura sem janela (`sem_janela`). Nada aqui vai para o disco por si: o executor grava só o que passa de uma
    abertura para outra (`atualizacao.gravar_estado`)."""

    fase: Fase = Fase.INICIO
    versao: str = ""
    nova: str = ""
    anterior: str = ""
    nao_tentar: tuple[str, ...] = ()
    sem_janela: bool = False


# ---------------------------------------------------------------------------------------------------------------------
# Os eventos (o que aconteceu), mandados pelo executor
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Abriu:
    """O programa abriu. `instalado`: pelo instalador do Velopack (pelo código é False). `pasta_grava`: a conta que abriu
    consegue gravar na pasta do programa (é o "preparado?", D-741). `troca_de`/`troca_para`: uma troca foi pedida antes
    desta abertura (pela linha de comando da reabertura ou pela anotação do disco); `troca_volta`: essa troca era a volta
    para a anterior. `sem_janela`: a reabertura do "Sim" ao fechar. `falha_nao_vista`: (tipo, nome) de uma falha
    anotada que esta conta ainda não viu."""

    instalado: bool
    conta_de_testes: bool
    portatil: bool
    pasta_grava: bool
    versao: str
    nao_tentar: tuple[str, ...] = ()
    troca_de: str = ""
    troca_para: str = ""
    troca_volta: bool = False
    sem_janela: bool = False
    falha_nao_vista: tuple[str, str] | None = None


@dataclass(frozen=True)
class LicencaRespondida:
    """A pergunta do Windows teve resposta: "comecou" (disse Sim e o trabalho com licença começou), "disse_nao" ou
    "falhou" (o Windows nem perguntou, ou não abriu o trabalho)."""

    desfecho: str
    motivo: str = ""


@dataclass(frozen=True)
class PreparoTerminou:
    """O trabalho com licença terminou; `pasta_grava` é o teste de gravar feito DE NOVO depois dele (nunca o que o
    trabalho anotou), e `motivo` o que ele disse."""

    pasta_grava: bool
    motivo: str = ""


@dataclass(frozen=True)
class MotorConferido:
    """O motor do Kraken está inteiro no lugar dele (ou acabou de ser posto)?"""

    no_lugar: bool
    motivo: str = ""


@dataclass(frozen=True)
class Procurou:
    """A procura terminou: a versão publicada mais nova (None = nenhuma) ou o erro (sem internet, GitHub fora do ar)."""

    versao: str | None
    erro: str = ""


@dataclass(frozen=True)
class Assinatura:
    """A assinatura do Samuel na versão achada confere?"""

    certa: bool
    motivo: str = ""


@dataclass(frozen=True)
class Baixou:
    """O download terminou (o Velopack conferiu tamanho e soma) ou deu erro."""

    certo: bool
    erro: str = ""


@dataclass(frozen=True)
class Escolheu:
    """O botão do aviso da versão nova: "Reiniciar agora" (`reiniciar`) ou "Depois"."""

    reiniciar: bool


@dataclass(frozen=True)
class JanelaFechou:
    """A janela fechou pelo caminho de sempre (grava o trabalho) depois do "Reiniciar agora"? False = recusou fechar."""

    fechou: bool


@dataclass(frozen=True)
class Fechando:
    """O Kaique está fechando o programa (o fechar da janela principal)."""


@dataclass(frozen=True)
class RespondeuAoFechar:
    """A resposta à pergunta "Atualizar agora?" ao fechar: "Sim" (`sim`) ou "Não"."""

    sim: bool


@dataclass(frozen=True)
class TrocaPedida:
    """O pedido da troca ao Velopack. `certa`: pedido feito (o programa sai e ele troca). `recusada`: o arquivo baixado
    não tem a soma assinada (foi trocado depois de baixar). Os outros "não" (outra janela aberta, o motor fora do
    lugar, o Velopack não aceitou) vêm com `certa` e `recusada` falsos e o `motivo`."""

    certa: bool
    motivo: str = ""
    recusada: bool = False


@dataclass(frozen=True)
class TesteRapido:
    """O teste rápido da versão que acabou de entrar passou?"""

    passou: bool
    detalhe: str = ""


@dataclass(frozen=True)
class VoltaPedida:
    """A volta para a anterior: pacote assinado buscado e troca pedida (`certa`), ou não deu (sem internet, sem a
    assinatura, o Velopack não aceitou)."""

    certa: bool
    motivo: str = ""


Evento = Union[Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
               JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, VoltaPedida]
TIPOS_DE_EVENTO = (Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
                   JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, VoltaPedida)


# ---------------------------------------------------------------------------------------------------------------------
# Os efeitos (o que o executor tem de fazer)
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class PedirLicenca:
    """Fazer a pergunta do Windows (os passos são os da peça, sempre os mesmos: `atualizacao.passos_do_preparo`)."""


@dataclass(frozen=True)
class EsperarPreparo:
    """Esperar o trabalho com licença terminar (por trás) e testar de novo se a pasta aceita gravação."""


@dataclass(frozen=True)
class GarantirMotor:
    """Pôr o motor do Kraken no lugar, se faltar, e dizer se está."""


@dataclass(frozen=True)
class Procurar:
    """Perguntar ao Velopack se há versão nova."""


@dataclass(frozen=True)
class ConferirAssinatura:
    """Conferir a assinatura do Samuel na versão achada, antes de baixar."""

    versao: str


@dataclass(frozen=True)
class Baixar:
    """Baixar a versão achada (só depois da assinatura certa)."""

    versao: str


@dataclass(frozen=True)
class MostrarVersaoNova:
    """O aviso "Reiniciar agora" / "Depois" na janela."""

    versao: str


@dataclass(frozen=True)
class FecharJanela:
    """Fechar a janela pelo caminho de sempre (o fechar grava o trabalho) e dizer se fechou."""


@dataclass(frozen=True)
class PerguntarAoFechar:
    """A pergunta "Atualizar agora?" ao fechar."""


@dataclass(frozen=True)
class Trocar:
    """Pedir a troca de `de` para `para` ao Velopack, pelo lugar único da troca (`atualizacao.trocar_para`, que antes
    confere a soma assinada do arquivo baixado, o motor e se há outra janela aberta). `reabrir`: `REABRIR_COM_JANELA` ou
    `REABRIR_SEM_JANELA`."""

    de: str
    para: str
    reabrir: str


@dataclass(frozen=True)
class RodarTesteRapido:
    """Rodar o teste rápido da versão que roda (num processo à parte, sem janela)."""


@dataclass(frozen=True)
class AnotarOk:
    """A versão que roda está conferida: apagar a anotação da troca em andamento."""

    versao: str


@dataclass(frozen=True)
class AnotarFalha:
    """A única forma de anotar uma falha: no disco (a falha a mostrar uma vez, pelo nome `id_da_falha(tipo, falhou)`;
    a versão `falhou` em "não tentar") e no registro. `fica`: a versão em que o programa continua."""

    tipo: str
    fica: str
    falhou: str
    motivo: str


@dataclass(frozen=True)
class Voltar:
    """Buscar a versão `para` (a anterior) assinada e pedir a troca de volta. `reabrir`: o Velopack abre a anterior
    com a janela depois (False na reabertura sem janela: nada abre na tela)."""

    de: str
    para: str
    reabrir: bool


@dataclass(frozen=True)
class MostrarFalha:
    """Mostrar na janela a frase da falha `tipo` (uma vez por `nome`, nesta conta)."""

    tipo: str
    nome: str


@dataclass(frozen=True)
class Registrar:
    """Uma linha no registro da atualização (nunca na tela)."""

    texto: str


@dataclass(frozen=True)
class Sair:
    """Este processo sai sem abrir a janela, com o código `codigo`."""

    codigo: int = 0


Efeito = Union[PedirLicenca, EsperarPreparo, GarantirMotor, Procurar, ConferirAssinatura, Baixar, MostrarVersaoNova,
               FecharJanela, PerguntarAoFechar, Trocar, RodarTesteRapido, AnotarOk, AnotarFalha, Voltar,
               MostrarFalha, Registrar, Sair]


# ---------------------------------------------------------------------------------------------------------------------
# A regra
# ---------------------------------------------------------------------------------------------------------------------

def _numeros(v: str) -> tuple[int, int, int] | None:
    """"1.2.3" -> (1, 2, 3); None fora do formato (a mesma regra de `versao.numeros`, sem importar nada de fora)."""
    partes = str(v).strip().split(".")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        return None
    return int(partes[0]), int(partes[1]), int(partes[2])


def _mais_nova(a: str, b: str) -> bool:
    """`a` é mais nova que `b`? Fora do formato nunca é."""
    na, nb = _numeros(a), _numeros(b)
    return na is not None and nb is not None and na > nb


def _com_mais(nao_tentar: tuple[str, ...], versao: str) -> tuple[str, ...]:
    """`nao_tentar` com mais esta versão (sem repetir, em ordem)."""
    return tuple(sorted(set(nao_tentar) | {versao})) if versao else nao_tentar


def _ignorado(estado: Estado, evento: Evento) -> tuple[Estado, list[Efeito]]:
    """O que não faz sentido nesta fase: fica e anota (ver o topo)."""
    return estado, [Registrar(f"{type(evento).__name__} na fase {estado.fase.value}: nada a fazer")]


def _abertura_comum(estado: Estado, abriu: Abriu, antes: list[Efeito]) -> tuple[Estado, list[Efeito]]:
    """A abertura do programa instalado depois de tratar a troca anterior: sem licença na pasta, a pergunta do
    Windows; com licença, o motor (e depois a procura)."""
    if not abriu.pasta_grava:
        return replace(estado, fase=Fase.SEM_LICENCA), antes + [PedirLicenca()]
    return replace(estado, fase=Fase.MOTOR), antes + [GarantirMotor()]


def _ao_abrir(estado: Estado, e: Abriu) -> tuple[Estado, list[Efeito]]:
    """`Abriu` (só na fase INICIO)."""
    if not e.instalado or e.conta_de_testes or e.portatil:
        return replace(estado, fase=Fase.FORA, versao=e.versao), []
    novo = replace(estado, versao=e.versao, nao_tentar=tuple(e.nao_tentar), sem_janela=e.sem_janela)
    if e.troca_para:
        if e.troca_volta:
            if e.versao == e.troca_para:          # a volta aconteceu: esta é a anterior, que funcionava
                return _abertura_comum(novo, e, _falha_a_mostrar(e) + [AnotarOk(e.versao)])
            if e.versao == e.troca_de:            # a volta não aconteceu: a versão que falhou continua
                nome = id_da_falha(FALHA_VOLTA, e.troca_de)
                efeitos: list[Efeito] = [AnotarFalha(FALHA_VOLTA, e.troca_de, e.troca_de,
                                                     f"a troca de volta para a {e.troca_para} não aconteceu")]
                if e.sem_janela:
                    return replace(novo, fase=Fase.PARADO), efeitos + [Sair(0)]
                return _abertura_comum(novo, e, efeitos + [MostrarFalha(FALHA_VOLTA, nome)])
        else:
            if e.versao == e.troca_para:          # a troca aconteceu: o teste rápido antes da janela
                return (replace(novo, fase=Fase.CONFERINDO_NOVA, nova=e.troca_para, anterior=e.troca_de),
                        [RodarTesteRapido()])
            if e.versao == e.troca_de:            # a troca não aconteceu: continua na versão de antes
                nome = id_da_falha(FALHA_TROCA, e.troca_para)
                efeitos = [AnotarFalha(FALHA_TROCA, e.troca_de, e.troca_para,
                                       "o Velopack não trocou; o programa continua na versão de antes")]
                novo = replace(novo, nao_tentar=_com_mais(novo.nao_tentar, e.troca_para))
                if e.sem_janela:
                    return replace(novo, fase=Fase.PARADO), efeitos + [Sair(0)]
                return _abertura_comum(novo, e, efeitos + [MostrarFalha(FALHA_TROCA, nome)])
        # nem a de antes nem a nova: a anotação é velha (de outra instalação)
        antes = _falha_a_mostrar(e) + [Registrar(f"a troca anotada ({e.troca_de} para {e.troca_para}) não é desta "
                                                 f"versão ({e.versao}): anotação velha, apagada"),
                                       AnotarOk(e.versao)]
        if e.sem_janela:
            return replace(novo, fase=Fase.PARADO), antes + [Sair(0)]
        return _abertura_comum(novo, e, antes)
    if e.sem_janela:                              # reabertura sem janela sem troca nenhuma: nada a conferir
        return replace(novo, fase=Fase.PARADO), [Registrar("reaberto sem janela sem troca anotada"), Sair(0)]
    return _abertura_comum(novo, e, _falha_a_mostrar(e))


def _falha_a_mostrar(e: Abriu) -> list[Efeito]:
    """A falha anotada que esta conta ainda não viu, mostrada uma vez (D-719, D-778)."""
    if e.falha_nao_vista and e.falha_nao_vista[0] in TIPOS_DE_FALHA:
        return [MostrarFalha(e.falha_nao_vista[0], e.falha_nao_vista[1])]
    return []


def proxima_fase(estado: Estado, evento: Evento) -> tuple[Estado, list[Efeito]]:
    """A regra inteira: dado onde a atualização está e o que aconteceu, a fase nova e o que fazer (ver o topo).

    Nunca levanta: evento desconhecido, ou fora de lugar, fica na mesma fase e só anota."""
    f, e = estado.fase, evento

    if isinstance(e, Abriu):
        return _ao_abrir(estado, e) if f is Fase.INICIO else _ignorado(estado, e)

    if isinstance(e, LicencaRespondida) and f is Fase.SEM_LICENCA:
        if e.desfecho == "comecou":
            return replace(estado, fase=Fase.PREPARANDO), [EsperarPreparo()]
        if e.desfecho == "disse_nao":
            return replace(estado, fase=Fase.PARADO), [Registrar(
                "a pessoa disse Não à pergunta do Windows: nada foi mudado e nada é procurado; a pergunta volta na "
                "próxima abertura")]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"a pergunta do Windows não deu certo ({e.motivo}); nada é procurado; a pergunta volta na próxima abertura")]

    if isinstance(e, PreparoTerminou) and f is Fase.PREPARANDO:
        if e.pasta_grava:
            return replace(estado, fase=Fase.MOTOR), [Registrar("o computador está preparado: a pasta do programa "
                                                                "aceita gravação"), GarantirMotor()]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"a preparação do computador não terminou ({e.motivo}); a pasta continua sem aceitar gravação e a "
            "pergunta volta na próxima abertura")]

    if isinstance(e, MotorConferido) and f is Fase.MOTOR:
        if e.no_lugar:
            return replace(estado, fase=Fase.PROCURANDO), [Procurar()]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"o motor do Kraken não está no lugar ({e.motivo}): nenhuma versão é procurada nem anunciada")]

    if isinstance(e, Procurou) and f is Fase.PROCURANDO:
        if e.erro:
            return replace(estado, fase=Fase.PARADO), [Registrar(f"não consegui procurar a versão nova: {e.erro}")]
        if e.versao is None:
            return replace(estado, fase=Fase.PARADO), [Registrar(f"procurei: nenhuma versão nova (esta é a "
                                                                 f"{estado.versao})")]
        if not _mais_nova(e.versao, estado.versao):
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"procurei: a publicada ({e.versao}) não é mais nova que a {estado.versao}")]
        if e.versao in estado.nao_tentar:
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"a versão {e.versao} já falhou antes; espero uma mais nova")]
        return replace(estado, fase=Fase.CONFERINDO, nova=e.versao), [ConferirAssinatura(e.versao)]

    if isinstance(e, Assinatura) and f is Fase.CONFERINDO:
        if e.certa:
            return replace(estado, fase=Fase.BAIXANDO), [
                Registrar(f"versão {estado.nova} publicada e assinada pelo Samuel: baixando"), Baixar(estado.nova)]
        return (replace(estado, fase=Fase.PARADO, nao_tentar=_com_mais(estado.nao_tentar, estado.nova)),
                [AnotarFalha(FALHA_RECUSADA, estado.versao, estado.nova, f"assinatura recusada: {e.motivo}"),
                 MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova))])

    if isinstance(e, Baixou) and f is Fase.BAIXANDO:
        if e.certo:
            return replace(estado, fase=Fase.PRONTA), [MostrarVersaoNova(estado.nova)]
        return replace(estado, fase=Fase.PARADO), [Registrar(f"não consegui baixar a versão {estado.nova}: {e.erro}")]

    if isinstance(e, Escolheu) and f is Fase.PRONTA:
        if e.reiniciar:
            return replace(estado, fase=Fase.FECHANDO), [FecharJanela()]
        return replace(estado, fase=Fase.DEPOIS), [Registrar(
            f"versão {estado.nova} pronta; o Kaique escolheu \"Depois\": a pergunta vem ao fechar")]

    if isinstance(e, JanelaFechou) and f is Fase.FECHANDO:
        if e.fechou:
            return replace(estado, fase=Fase.TROCANDO), [Trocar(estado.versao, estado.nova, REABRIR_COM_JANELA)]
        return replace(estado, fase=Fase.DEPOIS), [Registrar(
            "\"Reiniciar agora\": a janela não fechou; nada foi trocado (a pergunta vem ao fechar)")]

    if isinstance(e, Fechando):
        if f in (Fase.PRONTA, Fase.DEPOIS):
            return replace(estado, fase=Fase.PERGUNTANDO), [PerguntarAoFechar()]
        return estado, []

    if isinstance(e, RespondeuAoFechar) and f is Fase.PERGUNTANDO:
        if e.sim:
            return replace(estado, fase=Fase.TROCANDO), [Trocar(estado.versao, estado.nova, REABRIR_SEM_JANELA)]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"\"Não\" ao fechar: a versão {estado.nova} fica para a próxima abertura (o aviso volta)")]

    if isinstance(e, TrocaPedida) and f is Fase.TROCANDO:
        if e.certa:
            return estado, [Registrar(f"troca para a {estado.nova} pedida ao Velopack; o programa sai e ele troca")]
        if e.recusada:
            return (replace(estado, fase=Fase.PARADO, nao_tentar=_com_mais(estado.nao_tentar, estado.nova)),
                    [AnotarFalha(FALHA_RECUSADA, estado.versao, estado.nova, e.motivo)])
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"a troca para a {estado.nova} não foi pedida ({e.motivo}); fica para a próxima abertura")]

    if isinstance(e, TesteRapido) and f is Fase.CONFERINDO_NOVA:
        if e.passou:
            ok: list[Efeito] = [AnotarOk(estado.nova)]
            if estado.sem_janela:
                return replace(estado, fase=Fase.PARADO), ok + [Sair(0)]
            return replace(estado, fase=Fase.MOTOR), ok + [GarantirMotor()]
        return (replace(estado, fase=Fase.VOLTANDO, nao_tentar=_com_mais(estado.nao_tentar, estado.nova)),
                [AnotarFalha(FALHA_TESTE, estado.anterior, estado.nova,
                             f"a versão nova não passou no teste rápido ({e.detalhe})"),
                 Voltar(estado.nova, estado.anterior, reabrir=not estado.sem_janela)])

    if isinstance(e, VoltaPedida) and f is Fase.VOLTANDO:
        if e.certa:
            return replace(estado, fase=Fase.PARADO), [Sair(0)]
        efeitos = [AnotarFalha(FALHA_VOLTA, estado.nova, estado.nova,
                               f"a volta para a {estado.anterior} não deu certo ({e.motivo})")]
        if estado.sem_janela:
            return replace(estado, fase=Fase.PARADO), efeitos + [Sair(0)]
        return replace(estado, fase=Fase.PARADO), efeitos + [MostrarFalha(FALHA_VOLTA,
                                                                          id_da_falha(FALHA_VOLTA, estado.nova))]

    return _ignorado(estado, e)

