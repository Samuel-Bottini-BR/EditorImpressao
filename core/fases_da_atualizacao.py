"""A regra da atualização pela internet: em que fase ela está e o que fazer com cada acontecimento.

Atualizador novo (D-830, 23/11/2026; plano em `relatorios/atualizador-novo/plano-do-atualizador-novo.md`, seção 4.6),
com a emenda do Fable de 24/11/2026 (volta 3: "a verdade vem do disco, não do bilhete"). O desenho é o que o Fable
propôs e o Samuel aceitou ("refazer"): a regra é uma função só, sem disco, sem rede, sem Windows e sem tela,

    proxima_fase(estado, evento) -> (estado novo, efeitos)

e quem faz alguma coisa (perguntar ao Windows, procurar, baixar, trocar, mostrar o aviso) é o executor
(`atualizacao.Atualizacao`), que roda os efeitos que esta função devolve e manda de volta o que aconteceu como um evento
novo. Assim a decisão "o que vem agora" está num lugar só e é testada inteira, par por par
(`tests/test_fases_da_atualizacao.py` passa por todas as fases com todos os eventos).

A VERDADE VEM DO DISCO (emenda do Fable, A). A cada abertura o executor olha três coisas que existem e as manda no
`Abriu`: (1) a versão que roda; (2) a "última boa", a última versão que passou no teste rápido, guardada com o pacote
dela (`ultima_boa`); (3) se há pacote baixado esperando a troca (`pendente`, o que o Velopack diz). Daí:
    - rodando uma versão que não é a última boa e que não tem a marca de "aprovada" nem a de "sem volta": ela ainda
      não passou no teste; o teste rápido roda NESTA abertura, antes da janela. Passou: ganha a marca de aprovada e não
      é testada de novo (volta 4, D-856); o pacote dela é guardado como a última boa, se couber. Não passou: volta para
      a última boa, pelo pacote guardado (segundos, sem internet; D-844), UMA vez (D-855). Uma volta interrompida antes
      de ser pedida (o notebook desligou) é refeita na abertura seguinte, porque o disco ainda diz "rodando a nova,
      última boa a de antes" (G1 da volta 2).
    - a volta leva a marca `--voltando <de> <para>` (D-855): reaberta a de antes, a frase (1); reaberta a que falhou (o
      Windows não deixou trocar), a marca de "sem volta" no disco, a frase (3), e a abertura segue sem testar. Com a
      marca de "sem volta" nenhuma abertura testa nem volta de novo (D-863); volta ao normal com a próxima atualização.
    - a primeira versão instalada (sem última boa e sem o pacote dela em `packages\\`, que o .msi não põe) não é
      testada, nada é baixado, não há volta (D-857). Sem última boa mas com o pacote (uma atualização entrou), testa;
      não passou: a frase (3) e para.
    - sem internet, o pacote esperando (`pendente`) é oferecido pela assinatura guardada quando ele foi conferido
      (volta 4, D-859).
    - troca que não aconteceu (desligou, arquivo preso, o Windows recusou) NÃO é falha de versão: o pacote continua
      esperando e o aviso volta (M1). Só o teste rápido reprovado põe uma versão em "não tentar".
    - a frase (1) "voltou para a versão anterior" é DERIVADA: rodando igual à última boa e há reprovação de uma versão
      mais nova. Nunca é anotada antes de acontecer (G1).
O bilhete (`estado.json`) guarda só "versões reprovadas" (`nao_tentar` aqui) e "frase a mostrar uma vez" (para quando
o processo que a viu não tem janela). Nada mais decide nada.

AS FASES (`Fase`), na ordem em que costumam acontecer numa abertura do programa instalado:
    INICIO          ainda não abriu (só aceita `Abriu`).
    FORA            nada roda: pelo código, pacote portátil, ou a conta dos testes à distância (D-728, D-736, D-741).
    SEM_LICENCA     a pasta do programa não aceita gravação pela conta que abriu: a pergunta do Windows foi feita,
                    antes da janela (D-806, D-834); espera a resposta.
    PREPARANDO      a pessoa disse "Sim": o trabalho com licença (o ajudante antigo sai, o Visual C++, a instalação
                    antiga do Inno, a licença da pasta) roda por trás, com a janela já aberta.
    CONFERINDO_NOVA o teste rápido da versão que roda, que ainda não é a última boa nem foi aprovada (D-718), sempre
                    antes da janela (volta 4: o teste por trás, com a janela aberta, saiu).
    GUARDANDO       passou no teste: a marca de aprovada e o pacote dela guardado como a nova última boa, se couber
                    (D-844, D-856).
    VOLTANDO        não passou: a volta para a última boa, pelo pacote guardado (D-718, D-844).
    MOTOR           o motor do Kraken: sem ele no lugar, nada é anunciado (D-790, D-833).
    PROCURANDO      perguntando ao Velopack se há versão nova (só ao abrir, D-732).
    CONFERINDO      a assinatura do Samuel na versão achada, antes de baixar (D-724).
    BAIXANDO        baixando (o Velopack confere o tamanho e a soma do que baixou).
    PRONTA          baixada; o aviso "Reiniciar agora" / "Depois" está na tela (D-715, D-720).
    CONFERINDO_TROCA "Reiniciar agora": a conferência única da troca (o pacote, o motor da versão nova, outra janela
                    aberta) roda POR TRÁS, com a janela respondendo (volta 3, M2); a janela fecha quando ela termina.
                    Não pode: com outra janela aberta, a frase da D-840 e o aviso de novo (D-841); por qualquer outro
                    motivo, a frase da D-845 com o motivo (M3), e a pergunta vem ao fechar.
    DEPOIS          escolheu "Depois" (ou o "Reiniciar agora" não pôde): ao fechar, "Atualizar agora?" (D-831, D-835).
    FECHANDO        a conferência deixou: a janela fecha pelo caminho de sempre (grava o trabalho).
    PERGUNTANDO     a pergunta "Atualizar agora?" ao fechar está na tela.
    TROCANDO        a troca foi pedida ao Velopack; o programa sai e ele troca (D-828). Não depende de bilhete nenhum:
                    a abertura seguinte olha o disco.
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
de `Assinatura(certa)`; (3) `Trocar` só depois de a janela fechar ou do "Sim" ao fechar; (4) só o teste rápido reprovado
põe a versão em `nao_tentar` (`Reprovar`); (5) na conta de testes, `FORA`; (6) a volta só antes da janela, uma vez
(D-855, D-863); (7) a versão aprovada não é testada de novo (D-856).
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
    CONFERINDO_NOVA = "conferindo_nova"
    GUARDANDO = "guardando"
    VOLTANDO = "voltando"
    MOTOR = "motor"
    PROCURANDO = "procurando"
    CONFERINDO = "conferindo"
    BAIXANDO = "baixando"
    PRONTA = "pronta"
    CONFERINDO_TROCA = "conferindo_troca"
    DEPOIS = "depois"
    FECHANDO = "fechando"
    PERGUNTANDO = "perguntando"
    TROCANDO = "trocando"
    PARADO = "parado"


# Os tipos de frase da tela (um lugar só: o executor escolhe o texto por eles, `atualizacao.frase_da_falha`).
FALHA_TESTE = "teste"          # a versão nova não passou no teste rápido e o programa voltou (frase 1, derivada)
FALHA_TROCA = "troca"          # o Velopack não conseguiu trocar e reabriu a versão de antes (a frase da D-839)
FALHA_RECUSADA = "recusada"    # a versão não tem a assinatura do Samuel (frase 2)
FALHA_VOLTA = "volta"          # a versão nova falhou e a volta para a anterior não deu certo (frase 3)
FALHA_MOTOR = "motor"          # a versão nova pede um motor do Kraken que não está no lugar (D-843)
NAO_DEU_AGORA = "nao_deu_agora"  # o "Reiniciar agora" não pôde trocar (D-840 com outra janela; D-845 com o motivo)
TIPOS_DE_FALHA = (FALHA_TESTE, FALHA_TROCA, FALHA_RECUSADA, FALHA_VOLTA, FALHA_MOTOR, NAO_DEU_AGORA)

# Os motivos do "Não deu para atualizar agora: [motivo]" (D-845). Só a chave mora aqui; o texto em português, em
# `atualizacao.MOTIVOS_DA_TELA` (a tela só lê de lá). O da outra janela, em resposta ao clique, tem a frase dele (D-840) e
# não entra em `MOTIVOS`; o da outra janela no "Sim" ao fechar, mostrado na abertura seguinte, é o da D-864.
MOTIVO_OUTRA_JANELA = "outra_janela"
MOTIVO_HAVIA_OUTRA_JANELA = "havia_outra_janela"
MOTIVO_SEM_VERSAO = "sem_versao"
MOTIVO_PACOTE_SUMIU = "pacote_sumiu"
MOTIVO_PACOTE_INCOMPLETO = "pacote_incompleto"
MOTIVO_MOTOR = "motor"
MOTIVO_SEM_LISTA = "sem_lista"
MOTIVO_SEM_CONFERIR = "sem_conferir"
MOTIVO_NAO_FECHOU = "nao_fechou"
MOTIVO_ATUALIZADOR = "atualizador"
MOTIVO_ERRO = "erro"
MOTIVOS = (MOTIVO_HAVIA_OUTRA_JANELA, MOTIVO_SEM_VERSAO, MOTIVO_PACOTE_SUMIU, MOTIVO_PACOTE_INCOMPLETO, MOTIVO_MOTOR,
           MOTIVO_SEM_LISTA, MOTIVO_SEM_CONFERIR, MOTIVO_NAO_FECHOU, MOTIVO_ATUALIZADOR, MOTIVO_ERRO)

# Como o Velopack reabre o programa depois de uma troca (um lugar só).
REABRIR_COM_JANELA = "com_janela"      # "Reiniciar agora": abre a versão nova com a janela
REABRIR_SEM_JANELA = "sem_janela"      # "Sim" ao fechar: só o teste rápido, sem janela; nada abre na tela (D-769)


def id_da_falha(tipo: str, versao: str) -> str:
    """O nome de uma frase mostrada ao abrir (a tela mostra cada uma uma vez só, pelo nome). Lugar único."""
    return f"{tipo}-{versao}"


# ---------------------------------------------------------------------------------------------------------------------
# O estado
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Estado:
    """Onde a atualização está nesta abertura: a fase, a versão que roda (`versao`), a nova achada ou a que está sendo
    conferida (`nova`), a última boa guardada (`anterior`: para onde a volta vai; "" = nenhuma), as versões reprovadas
    no teste (`nao_tentar`), o pacote esperando (`pendente`, D-859), se este processo é a reabertura sem janela
    (`sem_janela`) e se a troca em andamento é a do "Reiniciar agora" (`trocando_com_janela`). Nada aqui vai para o
    disco por si."""

    fase: Fase = Fase.INICIO
    versao: str = ""
    nova: str = ""
    anterior: str = ""
    nao_tentar: tuple[str, ...] = ()
    pendente: str = ""
    sem_janela: bool = False
    trocando_com_janela: bool = False


# ---------------------------------------------------------------------------------------------------------------------
# Os eventos (o que aconteceu), mandados pelo executor
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Abriu:
    """O programa abriu. O que o executor leu do disco e do Windows AGORA (nunca de uma anotação):
    `instalado`: pelo instalador do Velopack (pelo código é False). `pasta_grava`: a conta que abriu consegue gravar na
    pasta do programa (o "preparado?", D-741). `versao`: a que roda. `ultima_boa`: a última que passou no teste, com o
    pacote guardado ("" = nenhuma). `aprovada`: a versão que roda tem a marca de aprovada no teste (D-856).
    `sem_volta`: a versão que roda tem a marca de "a volta já foi tentada e não deu" (D-863). `pacote_da_versao`: o
    pacote da versão que roda está em `packages\\` (depois do .msi não está: é a primeira versão instalada, D-857).
    `reaberto_voltando`: o pedido da reabertura era a volta (`--voltando`, D-855). `nao_tentar`: as reprovadas no
    teste (do bilhete). `pendente`: a versão baixada
    esperando a troca, pelo Velopack ("" = nenhuma). `troca_em_curso`: o atualizador do Velopack está rodando agora
    (True / False / None = não deu para saber); só é perguntado quando há troca possível e o programa não foi reaberto
    por ele. `reaberto_de`/`reaberto_para`: o pedido com que o Velopack reabriu o programa (a linha de comando).
    `sem_janela`: a reabertura do "Sim" ao fechar. `frase_guardada`: (tipo, nome, motivo) da frase que o bilhete guarda
    para mostrar uma vez."""

    instalado: bool
    conta_de_testes: bool
    portatil: bool
    pasta_grava: bool
    versao: str
    ultima_boa: str = ""
    aprovada: bool = False
    sem_volta: bool = False
    pacote_da_versao: bool = True
    nao_tentar: tuple[str, ...] = ()
    pendente: str = ""
    troca_em_curso: bool | None = False
    reaberto_de: str = ""
    reaberto_para: str = ""
    reaberto_voltando: bool = False
    sem_janela: bool = False
    frase_guardada: tuple[str, str, str] | None = None


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
    """A assinatura do Samuel na versão achada confere? `sem_rede`: não deu para saber, porque a rede não respondeu
    (volta 4: não é "recusada"; a frase (2) é só para a versão publicada sem a assinatura certa)."""

    certa: bool
    motivo: str = ""
    sem_rede: bool = False


@dataclass(frozen=True)
class Baixou:
    """O download terminou (o Velopack conferiu tamanho e soma) ou deu erro. `motor_da_nova`: o motor que a versão
    baixada pede (o `motor-exigido.json` de dentro dela) está inteiro no lugar (True/False), ou o pacote não diz qual
    motor pede (None) (D-833, D-843)."""

    certo: bool
    erro: str = ""
    motor_da_nova: bool | None = True


@dataclass(frozen=True)
class TrocaConferida:
    """A conferência única da troca, feita POR TRÁS antes de a janela fechar no "Reiniciar agora" (volta 2, M1; volta
    3, M2): pode trocar? `recusada`: o pacote baixado não tem a soma assinada. `outra_janela`: há OUTRA janela do
    programa aberta, conferida pelo caminho (leva à frase da D-840). `motivo`: o técnico, para o registro.
    `motivo_da_tela`: a chave do motivo em português (`MOTIVOS`, D-845)."""

    pode: bool
    motivo: str = ""
    recusada: bool = False
    outra_janela: bool = False
    motivo_da_tela: str = ""


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
    """O pedido da troca ao Velopack, pelo lugar único (`atualizacao.Atualizacao.trocar_para`). `certa`: pedido feito
    (o programa sai e ele troca). Os "não" trazem os mesmos campos da conferência (`TrocaConferida`), e o
    `motivo_da_tela` dos que não são da conferência (o atualizador não começou, um erro inesperado)."""

    certa: bool
    motivo: str = ""
    recusada: bool = False
    outra_janela: bool = False
    motivo_da_tela: str = ""


@dataclass(frozen=True)
class TesteRapido:
    """O teste rápido da versão que roda passou?"""

    passou: bool
    detalhe: str = ""


@dataclass(frozen=True)
class UltimaBoaGuardada:
    """O pacote da versão que passou no teste foi guardado como a última boa (conferido pela soma assinada)?"""

    certa: bool
    motivo: str = ""


@dataclass(frozen=True)
class VoltaPedida:
    """A volta para a última boa: o pacote guardado conferido e a troca pedida (`certa`), ou não deu (sem o pacote
    guardado, a soma não confere, o Velopack não aceitou)."""

    certa: bool
    motivo: str = ""


Evento = Union[Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
               JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, UltimaBoaGuardada, VoltaPedida,
               TrocaConferida]
TIPOS_DE_EVENTO = (Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
                   JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, UltimaBoaGuardada, VoltaPedida,
                   TrocaConferida)


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
    """Pôr o motor do Kraken no lugar, se faltar, e dizer se está (por trás)."""


@dataclass(frozen=True)
class Procurar:
    """Perguntar ao Velopack se há versão nova."""


@dataclass(frozen=True)
class ConferirAssinatura:
    """Conferir a assinatura do Samuel na versão achada, antes de baixar. `guardada`: a do pacote esperando, pela
    assinatura guardada quando ele foi conferido (sem internet, D-859)."""

    versao: str
    guardada: bool = False


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
    """Rodar o teste rápido da versão que roda (num processo à parte, sem janela), nesta linha, antes de a janela
    abrir."""


@dataclass(frozen=True)
class MarcarAprovada:
    """A marca de aprovada da versão no disco (D-856): ela não é testada de novo."""

    versao: str


@dataclass(frozen=True)
class MarcarSemVolta:
    """A marca de "a volta desta versão foi tentada e não deu" no disco (D-863): nenhuma abertura testa nem volta de
    novo; volta ao normal com a próxima atualização."""

    versao: str


@dataclass(frozen=True)
class GuardarUltimaBoa:
    """Guardar o pacote da versão `versao` (que passou no teste) como a última boa, conferido pela soma assinada
    (D-844). `por_tras`: com a janela abrindo (na reabertura sem janela, nesta linha, antes de sair)."""

    versao: str
    por_tras: bool = True


@dataclass(frozen=True)
class Reprovar:
    """A ÚNICA forma de pôr uma versão em "não tentar": ela não passou no teste rápido (no bilhete e no registro)."""

    versao: str
    motivo: str


@dataclass(frozen=True)
class Voltar:
    """Voltar de `de` para `para` (a última boa), pelo pacote guardado, e pedir a troca. `reabrir`: o Velopack abre a
    anterior com a janela depois (False na reabertura sem janela: nada abre na tela)."""

    de: str
    para: str
    reabrir: bool


@dataclass(frozen=True)
class MostrarFalha:
    """Mostrar na janela a frase do `tipo` (`TIPOS_DE_FALHA`), com o `motivo_da_tela` quando é o "não deu agora".
    `sempre`: é a resposta a um clique e aparece toda vez; senão, uma vez por `nome`, nesta conta (D-719)."""

    tipo: str
    nome: str = ""
    motivo_da_tela: str = ""
    sempre: bool = False


@dataclass(frozen=True)
class GuardarFrase:
    """Guardar no bilhete a frase do `tipo` sobre a versão `versao` (e o `motivo_da_tela`), para a próxima abertura com
    janela mostrar uma vez: é para quando este processo não tem janela (a reabertura sem janela, ou a janela já
    fechou)."""

    tipo: str
    versao: str
    motivo_da_tela: str = ""


@dataclass(frozen=True)
class Registrar:
    """Uma linha no registro da atualização (nunca na tela)."""

    texto: str


@dataclass(frozen=True)
class ConferirTroca:
    """A conferência única da troca (`atualizacao.Atualizacao.conferencia_da_troca`), por trás, sem pedir nada ao
    Velopack."""


@dataclass(frozen=True)
class ReabrirOPrograma:
    """Abrir o programa de novo (o "Reiniciar agora" cuja troca não pôde ser pedida depois de a janela fechar: o
    programa nunca some calado; volta 2, achado M1)."""


@dataclass(frozen=True)
class Sair:
    """Este processo sai sem abrir a janela, com o código `codigo`."""

    codigo: int = 0


Efeito = Union[PedirLicenca, EsperarPreparo, GarantirMotor, Procurar, ConferirAssinatura, Baixar, MostrarVersaoNova,
               FecharJanela, PerguntarAoFechar, Trocar, RodarTesteRapido, MarcarAprovada, MarcarSemVolta,
               GuardarUltimaBoa, Reprovar, Voltar,
               MostrarFalha, GuardarFrase, Registrar, Sair, ConferirTroca, ReabrirOPrograma]


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


def _frase(estado: Estado, tipo: str, versao: str, motivo_da_tela: str = "") -> list[Efeito]:
    """Uma frase de falha desta abertura: na janela, uma vez por nome; sem janela, guardada no bilhete para a próxima
    abertura com janela (um lugar só para essa escolha)."""
    if estado.sem_janela:
        return [GuardarFrase(tipo, versao, motivo_da_tela)]
    return [MostrarFalha(tipo, id_da_falha(tipo, versao), motivo_da_tela)]


def _frases_ao_abrir(novo: Estado, e: Abriu) -> list[Efeito]:
    """As frases que esta abertura mostra, todas derivadas do que existe (nada anotado antes de acontecer):
    - a troca que o Velopack não fez: ele reabre a versão de antes com o pedido de troca (apply.rs 56-60): a frase da
      D-839 (não é falha de versão: nada vai para "não tentar", e o aviso volta);
    - a (1) "voltou para a versão anterior": rodando a última boa, e há uma versão mais nova reprovada no teste
      (a mais nova delas dá o nome, para aparecer uma vez por versão reprovada);
    - a frase que o bilhete guarda (de um processo que não tinha janela).
    A volta que o Windows não deixou (reaberta com `--voltando`) é tratada em `_ao_abrir` (ela também marca o disco)."""
    efeitos: list[Efeito] = []
    if e.reaberto_para and not e.reaberto_voltando and e.versao == e.reaberto_de and \
            _mais_nova(e.reaberto_para, e.versao):
        efeitos += [Registrar(f"o Velopack não trocou para a {e.reaberto_para} e reabriu a {e.versao}: o aviso volta "
                              "quando ela for achada de novo")] + _frase(novo, FALHA_TROCA, e.reaberto_para)
    reprovadas_mais_novas = [v for v in e.nao_tentar if _mais_nova(v, e.versao)]
    if e.ultima_boa and e.versao == e.ultima_boa and reprovadas_mais_novas and not novo.sem_janela:
        mais_nova = max(reprovadas_mais_novas, key=_numeros)
        efeitos.append(MostrarFalha(FALHA_TESTE, id_da_falha(FALHA_TESTE, mais_nova)))
    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA and not novo.sem_janela:
        tipo, nome, motivo = e.frase_guardada
        efeitos.append(MostrarFalha(tipo, nome, motivo))
    return efeitos


def _precisa_do_teste(e: Abriu) -> bool:
    """A versão que roda precisa do teste rápido? A ÚNICA regra disso (volta 4): não é a última boa, não foi aprovada
    (D-856), não tem a marca de "sem volta" (D-863), e não é a primeira versão instalada (sem última boa e sem o pacote
    dela em `packages\\`: D-857)."""
    if e.versao == e.ultima_boa or e.aprovada or e.sem_volta:
        return False
    return bool(e.ultima_boa) or e.pacote_da_versao


def _ao_abrir(estado: Estado, e: Abriu) -> tuple[Estado, list[Efeito]]:
    """`Abriu` (só na fase INICIO): a verdade vem do disco (ver o topo)."""
    if not e.instalado or e.conta_de_testes or e.portatil:
        return replace(estado, fase=Fase.FORA, versao=e.versao), []
    novo = replace(estado, versao=e.versao, anterior=e.ultima_boa, nao_tentar=tuple(e.nao_tentar),
                   pendente=e.pendente, sem_janela=e.sem_janela)
    antes: list[Efeito] = []
    if e.troca_em_curso:
        # Volta 2, achado G1 (D-828 (1), D-770): o atualizador do Velopack está rodando (o clique no atalho no meio da
        # troca, ou da volta): este processo sai sem janela (o Velopack o fecharia à força) e nada é feito.
        return replace(novo, fase=Fase.PARADO), [Registrar(
            "o atualizador do Velopack está rodando (a troca está acontecendo agora): saio sem janela"), Sair(0)]
    if e.troca_em_curso is None:
        antes.append(Registrar("não deu para saber se a troca está acontecendo agora: a abertura segue"))
    if e.reaberto_voltando and e.reaberto_de and e.versao == e.reaberto_de:
        # Volta 4, G1 do terceiro "quem tenta quebrar" (D-855, D-863): a volta foi pedida e o Windows não deixou trocar
        # (o Velopack reabre a que falhou com o mesmo pedido). Uma vez só: a marca de "sem volta", a frase (3), e a
        # abertura segue sem testar; nenhuma abertura seguinte tenta de novo.
        antes += [Registrar(f"a volta da {e.versao} para a {e.reaberto_para} não aconteceu (o Velopack reabriu a "
                            f"{e.versao}): não tento de novo"), MarcarSemVolta(e.versao)]
        antes += _frase(novo, FALHA_VOLTA, e.versao)
        novo = replace(novo, fase=Fase.MOTOR)
        return novo, antes + _frases_ao_abrir(novo, e) + [GarantirMotor()]
    antes += _frases_ao_abrir(novo, e)
    if not e.pasta_grava:
        if e.sem_janela:
            return replace(novo, fase=Fase.PARADO), antes + [Registrar("reaberto sem janela numa pasta que não aceita "
                                                                       "gravação: nada a fazer"), Sair(0)]
        return replace(novo, fase=Fase.SEM_LICENCA), antes + [PedirLicenca()]
    if _precisa_do_teste(e):
        # A versão que roda não passou no teste: o teste antes da janela (D-718). Vale para a reabertura depois da troca
        # e para qualquer abertura em que a troca aconteceu sem a reabertura (desligou no meio, a volta interrompida).
        return replace(novo, fase=Fase.CONFERINDO_NOVA, nova=e.versao), antes + [RodarTesteRapido()]
    if e.sem_janela:
        return replace(novo, fase=Fase.PARADO), antes + [Registrar("reaberto sem janela sem nada a conferir"), Sair(0)]
    return replace(novo, fase=Fase.MOTOR), antes + [GarantirMotor()]


def _volta_que_nao_deu(estado: Estado, motivo: str) -> tuple[Estado, list[Efeito]]:
    """A volta que não aconteceu nesta abertura (sem última boa para voltar, ou a volta não pôde ser pedida): a marca de
    "sem volta" (nenhuma abertura testa nem volta de novo, D-863), a frase (3) e para (D-857). Um lugar só."""
    efeitos: list[Efeito] = [Registrar(motivo), MarcarSemVolta(estado.nova)] + _frase(estado, FALHA_VOLTA, estado.nova)
    if estado.sem_janela:
        return replace(estado, fase=Fase.PARADO), efeitos + [Sair(0)]
    return replace(estado, fase=Fase.PARADO), efeitos


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
            # A janela já abriu: o motor e a procura. Se a versão que roda precisar do teste, a próxima abertura o faz,
            # antes da janela (volta 4: o teste por trás saiu).
            return replace(estado, fase=Fase.MOTOR), [Registrar("o computador está preparado: a pasta do programa "
                                                                "aceita gravação"), GarantirMotor()]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"a preparação do computador não terminou ({e.motivo}); a pasta continua sem aceitar gravação e a "
            "pergunta volta na próxima abertura")]

    if isinstance(e, TesteRapido) and f is Fase.CONFERINDO_NOVA:
        if e.passou:
            # D-856: a marca de aprovada ANTES de guardar (se a cópia não couber, a versão não é testada de novo).
            return replace(estado, fase=Fase.GUARDANDO), [
                MarcarAprovada(estado.nova), GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela)]
        motivo = f"a versão {estado.nova} não passou no teste rápido ({e.detalhe})"
        reprovada = replace(estado, nao_tentar=_com_mais(estado.nao_tentar, estado.nova))
        if estado.anterior and estado.anterior != estado.nova:
            return (replace(reprovada, fase=Fase.VOLTANDO),
                    [Reprovar(estado.nova, motivo), Voltar(estado.nova, estado.anterior, reabrir=not estado.sem_janela)])
        # D-857: sem última boa para voltar, a frase (3) e para.
        fase_nova, efeitos = _volta_que_nao_deu(reprovada, f"{motivo}; não há versão guardada para voltar")
        return fase_nova, [Reprovar(estado.nova, motivo)] + efeitos

    if isinstance(e, UltimaBoaGuardada) and f is Fase.GUARDANDO:
        efeitos: list[Efeito] = [Registrar(
            f"a versão {estado.nova} passou no teste rápido e está guardada como a última boa" if e.certa else
            f"a versão {estado.nova} passou no teste rápido, mas o pacote dela não foi guardado ({e.motivo}): o teste "
            "roda de novo na próxima abertura")]
        novo = replace(estado, anterior=estado.nova) if e.certa else estado
        if estado.sem_janela:
            return replace(novo, fase=Fase.PARADO), efeitos + [Sair(0)]
        return replace(novo, fase=Fase.MOTOR), efeitos + [GarantirMotor()]

    if isinstance(e, VoltaPedida) and f is Fase.VOLTANDO:
        if e.certa:
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"a volta para a {estado.anterior} foi pedida ao Velopack; o programa sai e ele troca"), Sair(0)]
        return _volta_que_nao_deu(estado, f"a volta para a {estado.anterior} não deu certo ({e.motivo})")

    if isinstance(e, MotorConferido) and f is Fase.MOTOR:
        if e.no_lugar:
            return replace(estado, fase=Fase.PROCURANDO), [Procurar()]
        return replace(estado, fase=Fase.PARADO), [Registrar(
            f"o motor do Kraken não está no lugar ({e.motivo}): nenhuma versão é procurada nem anunciada")]

    if isinstance(e, Procurou) and f is Fase.PROCURANDO:
        if e.erro:
            if estado.pendente and _mais_nova(estado.pendente, estado.versao) and \
                    estado.pendente not in estado.nao_tentar:
                # D-859: sem internet, o pacote que já chegou e espera a troca, pela assinatura guardada.
                return replace(estado, fase=Fase.CONFERINDO, nova=estado.pendente), [
                    Registrar(f"não consegui procurar a versão nova ({e.erro}); a {estado.pendente} já está baixada"),
                    ConferirAssinatura(estado.pendente, guardada=True)]
            return replace(estado, fase=Fase.PARADO), [Registrar(f"não consegui procurar a versão nova: {e.erro}")]
        if e.versao is None:
            return replace(estado, fase=Fase.PARADO), [Registrar(f"procurei: nenhuma versão nova (esta é a "
                                                                 f"{estado.versao})")]
        if not _mais_nova(e.versao, estado.versao):
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"procurei: a publicada ({e.versao}) não é mais nova que a {estado.versao}")]
        if e.versao in estado.nao_tentar:
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"a versão {e.versao} não passou no teste rápido antes; espero uma mais nova")]
        return replace(estado, fase=Fase.CONFERINDO, nova=e.versao), [ConferirAssinatura(e.versao)]

    if isinstance(e, Assinatura) and f is Fase.CONFERINDO:
        if e.certa:
            return replace(estado, fase=Fase.BAIXANDO), [
                Registrar(f"versão {estado.nova} publicada e assinada pelo Samuel: baixando"), Baixar(estado.nova)]
        if e.sem_rede:
            # Volta 4: a rede que não respondeu não é a assinatura recusada (a frase 2 seria falsa).
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"não deu para ler a assinatura da versão {estado.nova} ({e.motivo}): tento na próxima abertura")]
        return replace(estado, fase=Fase.PARADO), [
            Registrar(f"a versão {estado.nova} não foi baixada: assinatura recusada ({e.motivo})"),
            MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova))]

    if isinstance(e, Baixou) and f is Fase.BAIXANDO:
        if e.certo and e.motor_da_nova is None:
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"o pacote da versão {estado.nova} não diz que motor do Kraken pede: ela não é anunciada")]
        if e.certo and not e.motor_da_nova:
            # D-843: a frase uma vez, e a versão não é anunciada nem trocada (D-833).
            return replace(estado, fase=Fase.PARADO), [Registrar(
                f"o motor do Kraken que a versão {estado.nova} pede não está no lugar: ela não é anunciada"),
                MostrarFalha(FALHA_MOTOR, id_da_falha(FALHA_MOTOR, estado.nova))]
        if e.certo:
            return replace(estado, fase=Fase.PRONTA), [MostrarVersaoNova(estado.nova)]
        return replace(estado, fase=Fase.PARADO), [Registrar(f"não consegui baixar a versão {estado.nova}: {e.erro}")]

    if isinstance(e, Escolheu) and f is Fase.PRONTA:
        if e.reiniciar:
            return replace(estado, fase=Fase.CONFERINDO_TROCA), [ConferirTroca()]
        return replace(estado, fase=Fase.DEPOIS), [Registrar(
            f"versão {estado.nova} pronta; o Kaique escolheu \"Depois\": a pergunta vem ao fechar")]

    if isinstance(e, TrocaConferida) and f is Fase.CONFERINDO_TROCA:
        if e.pode:
            return replace(estado, fase=Fase.FECHANDO), [FecharJanela()]
        if e.recusada:
            # O pacote não tem a soma assinada: a frase 2, em resposta ao clique (toda vez), e nada mais.
            return replace(estado, fase=Fase.PARADO), [
                Registrar(f"\"Reiniciar agora\": recusado ({e.motivo})"),
                MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova), sempre=True)]
        if e.outra_janela:
            # D-840 e D-841: com outra janela do programa aberta, a frase para fechá-la e, no mesmo evento, a volta à
            # fase PRONTA com o mesmo aviso de sempre ("Reiniciar agora" / "Depois"). Sem espera, sem temporizador.
            return replace(estado, fase=Fase.PRONTA), [
                Registrar(f"\"Reiniciar agora\": a troca não pode ser pedida agora ({e.motivo}); a frase para fechar a "
                          "outra janela e o aviso de novo"),
                MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=MOTIVO_OUTRA_JANELA, sempre=True),
                MostrarVersaoNova(estado.nova)]
        # D-845: qualquer outro "não pode agora": a frase com o motivo; a janela continua aberta e a pergunta vem ao
        # fechar (o clique nunca fica sem resposta).
        return replace(estado, fase=Fase.DEPOIS), [
            Registrar(f"\"Reiniciar agora\": a troca não pode ser pedida agora ({e.motivo}); a janela continua aberta "
                      "e a pergunta vem ao fechar"),
            MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=e.motivo_da_tela or MOTIVO_ERRO, sempre=True)]

    if isinstance(e, JanelaFechou) and f is Fase.FECHANDO:
        if e.fechou:
            return (replace(estado, fase=Fase.TROCANDO, trocando_com_janela=True),
                    [Trocar(estado.versao, estado.nova, REABRIR_COM_JANELA)])
        return replace(estado, fase=Fase.DEPOIS), [
            Registrar("\"Reiniciar agora\": a janela não fechou; nada foi trocado (a pergunta vem ao fechar)"),
            MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=MOTIVO_NAO_FECHOU, sempre=True)]

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
        efeitos = [Registrar(f"a troca para a {estado.nova} não foi pedida ({e.motivo}); fica para a próxima "
                             "abertura")]
        if not estado.trocando_com_janela:
            # O "Sim" ao fechar: o programa fecha mesmo; a frase vai pelo bilhete para a abertura seguinte (volta 4,
            # D-858: a mesma do "Reiniciar agora"; com outra janela aberta, a da D-864; o pacote trocado, a 2).
            if e.recusada:
                return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(FALHA_RECUSADA, estado.nova)]
            motivo_da_tela = MOTIVO_HAVIA_OUTRA_JANELA if e.outra_janela else (e.motivo_da_tela or MOTIVO_ERRO)
            return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(NAO_DEU_AGORA, estado.nova,
                                                                              motivo_da_tela)]
        if e.outra_janela:
            # Volta 3, M5: outra janela do programa abriu nos segundos do fechar: o Kaique já tem uma janela aberta,
            # que vai mostrar o aviso; reabrir esta daria duas janelas.
            return replace(estado, fase=Fase.PARADO), efeitos + [Registrar(
                "há outra janela do programa aberta: o programa não é reaberto (ela mostra o aviso)")]
        # Volta 2, M1: depois de a janela fechar no "Reiniciar agora", a troca que não pôde ser pedida reabre o
        # programa (nunca some calado), e a frase vai junto, pelo bilhete (volta 3, M3: D-845).
        if e.recusada:
            frase = [GuardarFrase(FALHA_RECUSADA, estado.nova)]
        else:
            frase = [GuardarFrase(NAO_DEU_AGORA, estado.nova, e.motivo_da_tela or MOTIVO_ERRO)]
        return replace(estado, fase=Fase.PARADO), efeitos + frase + [ReabrirOPrograma()]

    return _ignorado(estado, e)
