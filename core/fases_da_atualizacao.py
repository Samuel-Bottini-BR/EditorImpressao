"""A regra da atualização pela internet: em que fase ela está e o que fazer com cada acontecimento.

Atualizador novo (D-830, 23/11/2026; plano em `relatorios/atualizador-novo/plano-do-atualizador-novo.md`, seção 4.6),
com a emenda do Fable de 24/11/2026 (volta 3: "a verdade vem do disco, não do bilhete"). O desenho é o que o Fable
propôs e o Samuel aceitou ("refazer"): a regra é uma função só, sem disco, sem rede, sem Windows e sem tela,

    proxima_fase(estado, evento) -> (estado novo, efeitos)

e quem faz alguma coisa (perguntar ao Windows, procurar, baixar, trocar, mostrar o aviso) é o executor
(`atualizacao.Atualizacao`), que roda os efeitos que esta função devolve e manda de volta o que aconteceu como um evento
novo. Assim a decisão "o que vem agora" está num lugar só e é testada inteira, par por par
(`tests/test_fases_da_atualizacao.py` passa por todas as fases com todos os eventos).

A VERDADE VEM DO DISCO (emenda do Fable, A). A cada abertura o executor olha o que existe e manda no `Abriu`: (1) a
versão que roda; (2) a "última boa", a última versão que passou no teste rápido, guardada com o pacote dela
(`ultima_boa`; só os nomes da pasta); (3) as marcas do disco e se o pacote da versão que roda está em `packages\\`;
(4) se há pacote baixado esperando a troca (`pendente`, o que o Velopack diz). Daí:
    - rodando uma versão que ainda não passou nem falhou no teste rápido (`precisa_do_teste`): o teste roda NESTA
      abertura, antes da janela. Passou: ganha a marca de aprovada e não é testada de novo (volta 4, D-856); o pacote
      dela é guardado como a última boa, se couber. Não passou (volta 5, D-868): vai para as reprovadas, a frase da
      D-868 aparece (antes da janela: pela caixa do Windows, escolhido pelo executor), e a abertura segue como sempre
      (o programa tenta abrir assim mesmo). Nada volta sozinho: a volta automática saiu da primeira entrega (D-867); a
      última boa continua guardada para a volta à mão do Samuel (D-869). A reprovada não é testada de novo.
    - a primeira versão instalada (sem última boa e sem o pacote dela em `packages\\`, que o .msi não põe) não é
      testada e nada é baixado (D-857).
    - sem internet, o pacote esperando (`pendente`) é oferecido pela assinatura guardada quando ele foi conferido
      (volta 4, D-859).
    - troca que não aconteceu (desligou, arquivo preso, o Windows recusou) NÃO é falha de versão: o pacote continua
      esperando e o aviso volta (M1 da volta 3). Só o teste rápido reprovado põe uma versão em "não tentar".
    - a frase guardada no bilhete sobre uma troca que não aconteceu só aparece se a versão que roda ainda é mais velha
      que a da frase (volta 5, M1 do quarto "quem tenta quebrar": se a troca aconteceu depois, a frase deixou de ser
      verdade). `_frase_guardada_vale`.
O bilhete (`estado.json`) guarda só "versões reprovadas" (`nao_tentar` aqui) e "frase a mostrar uma vez" (para quando
o processo que a viu não tem janela). Nada mais decide nada.

AS FASES (`Fase`), na ordem em que costumam acontecer numa abertura do programa instalado:
    INICIO          ainda não abriu (só aceita `Abriu`).
    FORA            nada roda: pelo código, pacote portátil, ou a conta dos testes à distância (D-728, D-736, D-741).
    SEM_LICENCA     a pasta do programa não aceita gravação pela conta que abriu: a pergunta do Windows foi feita,
                    antes da janela (D-806, D-834); espera a resposta.
    PREPARANDO      a pessoa disse "Sim": o trabalho com licença (o ajudante antigo sai, o Visual C++, a instalação
                    antiga do Inno, a licença da pasta) roda por trás, com a janela já aberta.
    CONFERINDO_NOVA o teste rápido da versão que roda, que ainda não passou nem falhou nele, sempre antes da janela
                    (volta 4: o teste por trás, com a janela aberta, saiu).
    GUARDANDO       passou no teste: a marca de aprovada e o pacote dela guardado como a nova última boa, se couber
                    (D-844, D-856). Não passou: nada a guardar; a abertura segue (volta 5, D-868).
    MOTOR           o motor do Kraken: sem ele no lugar, nada é anunciado (D-790, D-833).
    PROCURANDO      perguntando ao Velopack se há versão nova (só ao abrir, D-732).
    CONFERINDO      a assinatura do Samuel na versão achada, antes de baixar (D-724).
    BAIXANDO        baixando (o Velopack confere o tamanho e a soma do que baixou).
    PRONTA          baixada; o aviso "Reiniciar agora" / "Depois" está na tela (D-715, D-720).
    CONFERINDO_TROCA "Reiniciar agora": a conferência única da troca (o pacote, o motor da versão nova, outra janela
                    aberta) roda POR TRÁS, com a janela respondendo (volta 3, M2); a janela fecha quando ela termina.
                    Não pode: com outra janela aberta, a frase da D-840 e o aviso de novo (D-841); sem o atualizador do
                    Velopack (`Update.exe`), a frase própria e nada mais (volta 5, M2: fechar não pergunta, porque não
                    há como trocar); por qualquer outro motivo, a frase da D-845 com o motivo (M3), e a pergunta vem
                    ao fechar.
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
põe a versão em `nao_tentar` (`Reprovar`); (5) na conta de testes, `FORA`; (6) a versão aprovada, e a reprovada, não
são testadas de novo (D-856; volta 5); (7) nenhuma transição pede volta ao Velopack (D-867: a volta automática saiu).
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


# Os tipos de frase da tela (um lugar só: o executor escolhe o texto por eles, `atualizacao.frase_da_falha`). Volta 5:
# saíram o "teste" (a frase 1, "voltou para a versão anterior") e o "volta" (a frase 3), com a volta automática (D-867);
# entrou o "reprovada" (D-868).
FALHA_REPROVADA = "reprovada"  # a versão nova não passou no teste rápido (a frase da D-868)
FALHA_TROCA = "troca"          # o Velopack não conseguiu trocar e reabriu a versão de antes (a frase da D-839)
FALHA_RECUSADA = "recusada"    # a versão não tem a assinatura do Samuel (frase 2)
FALHA_MOTOR = "motor"          # a versão nova pede um motor do Kraken que não está no lugar (D-843)
NAO_DEU_AGORA = "nao_deu_agora"  # o "Reiniciar agora" não pôde trocar (D-840 com outra janela; D-845 com o motivo)
TIPOS_DE_FALHA = (FALHA_REPROVADA, FALHA_TROCA, FALHA_RECUSADA, FALHA_MOTOR, NAO_DEU_AGORA)

# Os motivos do "Não deu para atualizar agora: [motivo]" (D-845). Só a chave mora aqui; o texto em português, em
# `atualizacao.MOTIVOS_DA_TELA` (a tela só lê de lá). O da outra janela, em resposta ao clique, tem a frase dele (D-840) e
# não entra em `MOTIVOS`; o da outra janela no "Sim" ao fechar, mostrado na abertura seguinte, é o da D-864. O do
# atualizador do Velopack que sumiu (volta 5, M2) também tem a frase própria, sem "Tente ao fechar o programa"
# (`atualizacao.FRASE_SEM_ATUALIZADOR`), e não entra em `MOTIVOS`.
MOTIVO_OUTRA_JANELA = "outra_janela"
MOTIVO_SEM_ATUALIZADOR = "sem_atualizador"
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
    """O nome de uma frase mostrada ao abrir (a tela mostra cada uma uma vez só, pelo nome). Lugar único. A frase
    guardada no bilhete acrescenta a hora depois (`atualizacao.guardar_frase`: "<tipo>-<versão>-<hora>")."""
    return f"{tipo}-{versao}"


def versao_da_falha(tipo: str, nome: str) -> str:
    """A versão de que uma frase fala, lida do nome dela (o par de `id_da_falha`: "<tipo>-<versão>[-<hora>]"); "" se o
    nome não é desse jeito. Lugar único (volta 5, M1)."""
    prefixo = f"{tipo}-"
    if not nome.startswith(prefixo):
        return ""
    v = nome[len(prefixo):].split("-")[0]
    return v if _numeros(v) else ""


# ---------------------------------------------------------------------------------------------------------------------
# O estado
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Estado:
    """Onde a atualização está nesta abertura: a fase, a versão que roda (`versao`), a nova achada ou a que está sendo
    conferida (`nova`), as versões reprovadas no teste (`nao_tentar`), o pacote esperando (`pendente`, D-859), se este
    processo é a reabertura sem janela (`sem_janela`) e se a troca em andamento é a do "Reiniciar agora"
    (`trocando_com_janela`). Nada aqui vai para o disco por si. (Volta 5: saiu o `anterior`, "para onde a volta vai".)"""

    fase: Fase = Fase.INICIO
    versao: str = ""
    nova: str = ""
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
    pacote guardado ("" = nenhuma; só para saber se a versão que roda já passou: nada volta para ela, D-869).
    `aprovada`: a versão que roda tem a marca de aprovada no teste (D-856). `pacote_da_versao`: o pacote da versão que
    roda está em `packages\\` (depois do .msi não está: é a primeira versão instalada, D-857). `nao_tentar`: as
    reprovadas no teste (do bilhete). `pendente`: a versão baixada
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
    pacote_da_versao: bool = True
    nao_tentar: tuple[str, ...] = ()
    pendente: str = ""
    troca_em_curso: bool | None = False
    reaberto_de: str = ""
    reaberto_para: str = ""
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


Evento = Union[Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
               JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, UltimaBoaGuardada, TrocaConferida]
TIPOS_DE_EVENTO = (Abriu, LicencaRespondida, PreparoTerminou, MotorConferido, Procurou, Assinatura, Baixou, Escolheu,
                   JanelaFechou, Fechando, RespondeuAoFechar, TrocaPedida, TesteRapido, UltimaBoaGuardada,
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
class MostrarFalha:
    """Mostrar a frase do `tipo` (`TIPOS_DE_FALHA`), com o `motivo_da_tela` quando é o "não deu agora". `sempre`: é a
    resposta a um clique e aparece toda vez; senão, uma vez por `nome`, nesta conta (D-719). ONDE ela aparece não é
    regra daqui: o executor a põe na caixa da janela, ou, se a janela ainda não existe, na caixa do Windows (volta 5,
    D-868: `atualizacao.Atualizacao._para_a_tela`)."""

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
               FecharJanela, PerguntarAoFechar, Trocar, RodarTesteRapido, MarcarAprovada, GuardarUltimaBoa, Reprovar,
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


def _frase_guardada_vale(tipo: str, nome: str, versao_que_roda: str) -> bool:
    """A frase guardada no bilhete ainda é verdade? A ÚNICA regra disso (volta 5, M1 do quarto "quem tenta quebrar").
    A versão de que ela fala vem do nome (`versao_da_falha`).
    - A frase da versão reprovada (D-868) fala da versão que roda: vale enquanto a que roda não é mais nova que ela.
    - Todas as outras falam de uma troca para a versão da frase que não aconteceu (o "Sim" ao fechar que não trocou,
      D-858/D-864; o pacote trocado, D-848; a troca que o Velopack não fez, D-839; o atualizador que sumiu, M2): valem
      só enquanto a que roda é mais velha que ela. Se a troca aconteceu depois (o "Sim" da outra janela, o "Reiniciar
      agora" da abertura seguinte), a frase deixou de ser verdade e não aparece.
    Sem a versão no nome (um nome de outro jeito): vale (na dúvida, a frase aparece; esconder uma frase verdadeira seria
    pior)."""
    v = versao_da_falha(tipo, nome)
    if not v:
        return True
    if tipo == FALHA_REPROVADA:
        return not _mais_nova(versao_que_roda, v)
    return _mais_nova(v, versao_que_roda)


def _frases_ao_abrir(novo: Estado, e: Abriu) -> list[Efeito]:
    """As frases que esta abertura mostra, todas derivadas do que existe (nada anotado antes de acontecer):
    - a troca que o Velopack não fez: ele reabre a versão de antes com o pedido de troca (apply.rs 56-60): a frase da
      D-839 (não é falha de versão: nada vai para "não tentar", e o aviso volta);
    - a frase que o bilhete guarda (de um processo que não tinha janela), se ainda é verdade (`_frase_guardada_vale`).
    (Volta 5: a frase (1), "voltou para a versão anterior", saiu com a volta automática, D-867.)"""
    efeitos: list[Efeito] = []
    if e.reaberto_para and e.versao == e.reaberto_de and _mais_nova(e.reaberto_para, e.versao):
        efeitos += [Registrar(f"o Velopack não trocou para a {e.reaberto_para} e reabriu a {e.versao}: o aviso volta "
                              "quando ela for achada de novo")] + _frase(novo, FALHA_TROCA, e.reaberto_para)
    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA and not novo.sem_janela:
        tipo, nome, motivo = e.frase_guardada
        if _frase_guardada_vale(tipo, nome, e.versao):
            efeitos.append(MostrarFalha(tipo, nome, motivo))
        else:
            efeitos.append(Registrar(f"a frase guardada \"{nome}\" deixou de ser verdade (a versão que roda é a "
                                     f"{e.versao}): não aparece"))
    return efeitos


def precisa_do_teste(versao: str, ultima_boa: str, aprovada: bool, pacote_da_versao: bool,
                     nao_tentar: tuple[str, ...]) -> bool:
    """A versão que roda precisa do teste rápido? A ÚNICA regra disso (a regra a chama pela abertura; o executor, para
    saber se uma troca pode estar acontecendo). Não precisa se: é a última boa ou tem a marca de aprovada (já passou,
    D-856); já foi reprovada (volta 5: o teste daria o mesmo, e a frase da D-868 já foi dada; a marca de "sem volta"
    da volta 4 saiu, D-867); ou é a primeira versão instalada (sem última boa e sem o pacote dela em `packages\\`,
    D-857)."""
    if versao == ultima_boa or aprovada or versao in nao_tentar:
        return False
    return bool(ultima_boa) or pacote_da_versao


def _precisa_do_teste(e: Abriu) -> bool:
    """`precisa_do_teste` com o que a abertura leu."""
    return precisa_do_teste(e.versao, e.ultima_boa, e.aprovada, e.pacote_da_versao, tuple(e.nao_tentar))


def _ao_abrir(estado: Estado, e: Abriu) -> tuple[Estado, list[Efeito]]:
    """`Abriu` (só na fase INICIO): a verdade vem do disco (ver o topo)."""
    if not e.instalado or e.conta_de_testes or e.portatil:
        return replace(estado, fase=Fase.FORA, versao=e.versao), []
    novo = replace(estado, versao=e.versao, nao_tentar=tuple(e.nao_tentar), pendente=e.pendente,
                   sem_janela=e.sem_janela)
    antes: list[Efeito] = []
    if e.troca_em_curso:
        # Volta 2, achado G1 (D-828 (1), D-770): o atualizador do Velopack está rodando (o clique no atalho no meio da
        # troca, ou da volta): este processo sai sem janela (o Velopack o fecharia à força) e nada é feito.
        return replace(novo, fase=Fase.PARADO), [Registrar(
            "o atualizador do Velopack está rodando (a troca está acontecendo agora): saio sem janela"), Sair(0)]
    if e.troca_em_curso is None:
        antes.append(Registrar("não deu para saber se a troca está acontecendo agora: a abertura segue"))
    antes += _frases_ao_abrir(novo, e)
    if not e.pasta_grava:
        if e.sem_janela:
            return replace(novo, fase=Fase.PARADO), antes + [Registrar("reaberto sem janela numa pasta que não aceita "
                                                                       "gravação: nada a fazer"), Sair(0)]
        return replace(novo, fase=Fase.SEM_LICENCA), antes + [PedirLicenca()]
    if _precisa_do_teste(e):
        # A versão que roda ainda não passou nem falhou no teste: o teste antes da janela. Vale para a reabertura depois
        # da troca e para qualquer abertura em que a troca aconteceu sem a reabertura (desligou no meio).
        return replace(novo, fase=Fase.CONFERINDO_NOVA, nova=e.versao), antes + [RodarTesteRapido()]
    if e.sem_janela:
        return replace(novo, fase=Fase.PARADO), antes + [Registrar("reaberto sem janela sem nada a conferir"), Sair(0)]
    return replace(novo, fase=Fase.MOTOR), antes + [GarantirMotor()]


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
        # Volta 5 (D-867, D-868): nada volta sozinho. A versão vai para as reprovadas (não é testada nem oferecida de
        # novo), a frase da D-868 aparece (antes da janela, pela caixa do Windows; sem janela, guardada para a próxima
        # abertura), e a abertura segue como sempre: o programa tenta abrir assim mesmo, com o motor e a procura (uma
        # correção publicada é oferecida se a janela abrir). Nenhum pedido ao Velopack.
        reprovada = replace(estado, nao_tentar=_com_mais(estado.nao_tentar, estado.nova))
        efeitos = [Reprovar(estado.nova, f"a versão {estado.nova} não passou no teste rápido ({e.detalhe})")]
        efeitos += _frase(reprovada, FALHA_REPROVADA, estado.nova)
        if estado.sem_janela:
            return replace(reprovada, fase=Fase.PARADO), efeitos + [Sair(0)]
        return replace(reprovada, fase=Fase.MOTOR), efeitos + [GarantirMotor()]

    if isinstance(e, UltimaBoaGuardada) and f is Fase.GUARDANDO:
        efeitos: list[Efeito] = [Registrar(
            f"a versão {estado.nova} passou no teste rápido e está guardada como a última boa" if e.certa else
            f"a versão {estado.nova} passou no teste rápido, mas o pacote dela não foi guardado ({e.motivo}): o teste "
            "roda de novo na próxima abertura")]
        if estado.sem_janela:
            return replace(estado, fase=Fase.PARADO), efeitos + [Sair(0)]
        return replace(estado, fase=Fase.MOTOR), efeitos + [GarantirMotor()]

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
        if e.motivo_da_tela == MOTIVO_SEM_ATUALIZADOR:
            # Volta 5, M2 do quarto "quem tenta quebrar" (D-870): sem o atualizador do Velopack não há como trocar. A
            # frase própria (sem "Tente ao fechar o programa"), e nada mais: fechar não pergunta (a pergunta levaria à
            # mesma falha). Quando ele voltar, a abertura seguinte acha a versão (ou o pacote esperando) e o aviso volta.
            return replace(estado, fase=Fase.PARADO), [
                Registrar(f"\"Reiniciar agora\": a troca não pode ser pedida ({e.motivo})"),
                MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=MOTIVO_SEM_ATUALIZADOR, sempre=True)]
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
