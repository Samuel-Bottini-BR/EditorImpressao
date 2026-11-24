"""A regra da atualização, inteira: todas as fases com todos os eventos (atualizador novo, 23/11/2026, D-830; volta 3,
24/11/2026: a emenda do Fable, "a verdade vem do disco, não do bilhete").

O que se prova (o plano, seção 11: "A regra, exaustiva"): `core.fases_da_atualizacao.proxima_fase` responde a TODO par
(fase, evento). A tabela `ESPERADO` diz, caso por caso, a fase nova, o que muda no estado e os efeitos; todo par que
não está nela é "não faz sentido aqui": fica na mesma fase e só anota (o `Fechando` fica e não faz nada). Mudar uma
transição sem mudar esta tabela faz o teste falhar: é para isso que ela existe. Cada linha diz a decisão do Samuel que
protege.

Mudou na volta 3 (lista da D-836, `relatorios/atualizador-novo/lista-dos-testes-d836.md`): a abertura recebe o que
existe (a versão que roda, a última boa guardada, o pacote esperando, o pedido da reabertura) em vez da anotação da
troca; só o teste rápido reprovado põe a versão em "não tentar"; a volta é pelo pacote guardado; o "Reiniciar agora"
que não pode responde com a frase (D-840/D-845).

E o arquivo da regra não fala com o mundo de fora: só importa `dataclasses`, `enum` e `typing` (lido pela árvore).

Nada aqui roda o Windows, o Velopack, o disco ou a tela.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from core import fases_da_atualizacao as f

RAIZ = Path(__file__).resolve().parent.parent

# O estado de partida de cada fase (menos INICIO, que parte do estado vazio).
BASE = f.Estado(versao="1.1.0", nova="1.2.0", anterior="1.0.0", nao_tentar=("1.3.0",))
# A abertura comum: rodando a última boa, com uma reprovada MAIS VELHA (não dá a frase 1).
COMUM = dict(instalado=True, conta_de_testes=False, portatil=False, pasta_grava=True, versao="1.1.0",
             ultima_boa="1.1.0", nao_tentar=("1.0.5",))
NOVA = {**COMUM, "versao": "1.2.0"}               # rodando uma versão que ainda não passou no teste

# Os eventos de amostra (cada caso que a regra separa tem o seu).
EVENTOS = {
    "abriu_codigo": f.Abriu(**{**COMUM, "instalado": False}),
    "abriu_testes": f.Abriu(**{**COMUM, "conta_de_testes": True}),
    "abriu_portatil": f.Abriu(**{**COMUM, "portatil": True}),
    "abriu_sem_licenca": f.Abriu(**{**COMUM, "pasta_grava": False}),
    "abriu_com_licenca": f.Abriu(**COMUM),
    # A frase (1), derivada: rodando a última boa, com uma versão mais nova reprovada no teste.
    "abriu_depois_da_volta": f.Abriu(**{**COMUM, "nao_tentar": ("1.0.5", "1.2.0")}),
    "abriu_depois_da_volta_sem_janela": f.Abriu(**{**COMUM, "nao_tentar": ("1.0.5", "1.2.0")}, sem_janela=True),
    # A versão que roda não é a última boa: o teste antes da janela (pela reabertura ou pelo atalho, tanto faz).
    "abriu_nova": f.Abriu(**NOVA),
    "abriu_nova_reaberta": f.Abriu(**NOVA, reaberto_de="1.1.0", reaberto_para="1.2.0"),
    "abriu_nova_sem_janela": f.Abriu(**NOVA, reaberto_de="1.1.0", reaberto_para="1.2.0", sem_janela=True),
    "abriu_nova_sem_licenca": f.Abriu(**{**NOVA, "pasta_grava": False}),
    # O Velopack não trocou e reabriu a de antes com o pedido (a frase da D-839; nada vai para "não tentar").
    "abriu_troca_recusada": f.Abriu(**COMUM, reaberto_de="1.1.0", reaberto_para="1.2.0"),
    "abriu_troca_recusada_sem_janela": f.Abriu(**COMUM, reaberto_de="1.1.0", reaberto_para="1.2.0",
                                               sem_janela=True),
    # A primeira abertura depois de instalar: nenhuma última boa guardada.
    "abriu_sem_ultima_boa": f.Abriu(**{**COMUM, "ultima_boa": ""}),
    "abriu_sem_ultima_boa_sem_pacote": f.Abriu(**{**COMUM, "ultima_boa": ""}, pacote_da_versao=False),
    "abriu_sem_janela_sem_nada": f.Abriu(**COMUM, sem_janela=True),
    # Volta 2, G1: o atualizador do Velopack rodando (o clique no atalho no meio da troca), ou sem saber.
    "abriu_troca_em_curso": f.Abriu(**NOVA, troca_em_curso=True),
    "abriu_troca_sem_saber": f.Abriu(**COMUM, pendente="1.2.0", troca_em_curso=None),
    # A frase que o bilhete guarda (de um processo sem janela).
    "abriu_frase_guardada": f.Abriu(**COMUM, frase_guardada=("nao_deu_agora", "nao_deu_agora-1.2.0-x", "motor")),
    "abriu_frase_estranha": f.Abriu(**COMUM, frase_guardada=("outra", "x", "")),
    "lic_comecou": f.LicencaRespondida("comecou"),
    "lic_nao": f.LicencaRespondida("disse_nao"),
    "lic_falhou": f.LicencaRespondida("falhou", "o Windows não abriu"),
    "prep_ok": f.PreparoTerminou(True),
    "prep_nao": f.PreparoTerminou(False, "o Visual C++ falhou"),
    "teste_ok": f.TesteRapido(True),
    "teste_nao": f.TesteRapido(False, "código 1"),
    "guardada_ok": f.UltimaBoaGuardada(True),
    "guardada_nao": f.UltimaBoaGuardada(False, "sem o pacote"),
    "volta_ok": f.VoltaPedida(True),
    "volta_nao": f.VoltaPedida(False, "sem o pacote guardado"),
    "motor_ok": f.MotorConferido(True),
    "motor_nao": f.MotorConferido(False, "sem o arquivo"),
    "proc_erro": f.Procurou(None, "sem internet"),
    "proc_nada": f.Procurou(None),
    "proc_igual": f.Procurou("1.1.0"),
    "proc_velha": f.Procurou("1.0.0"),
    "proc_estranha": f.Procurou("1.2"),
    "proc_ja_falhou": f.Procurou("1.3.0"),
    "proc_nova": f.Procurou("1.2.0"),
    "ass_ok": f.Assinatura(True),
    "ass_nao": f.Assinatura(False, "não confere"),
    "baixou_ok": f.Baixou(True),
    "baixou_nao": f.Baixou(False, "disco cheio"),
    "baixou_sem_o_motor_da_nova": f.Baixou(True, motor_da_nova=False),
    "baixou_sem_dizer_o_motor": f.Baixou(True, motor_da_nova=None),
    "conferida_pode": f.TrocaConferida(True),
    "conferida_nao": f.TrocaConferida(False, "sem a lista", motivo_da_tela=f.MOTIVO_SEM_LISTA),
    "conferida_recusada": f.TrocaConferida(False, "a soma não confere", recusada=True),
    "conferida_outra_janela": f.TrocaConferida(False, "há outra janela do programa aberta", outra_janela=True,
                                               motivo_da_tela=f.MOTIVO_OUTRA_JANELA),
    "reiniciar": f.Escolheu(True),
    "depois": f.Escolheu(False),
    "fechou": f.JanelaFechou(True),
    "nao_fechou": f.JanelaFechou(False),
    "fechando": f.Fechando(),
    "sim": f.RespondeuAoFechar(True),
    "nao": f.RespondeuAoFechar(False),
    "troca_ok": f.TrocaPedida(True),
    "troca_recusada": f.TrocaPedida(False, "a soma não confere", recusada=True),
    "troca_nao": f.TrocaPedida(False, "o atualizador não abriu", motivo_da_tela=f.MOTIVO_ATUALIZADOR),
    "troca_outra_janela": f.TrocaPedida(False, "outra janela", outra_janela=True,
                                        motivo_da_tela=f.MOTIVO_OUTRA_JANELA),
}

R = ("Registrar",)            # uma linha no registro (o texto não importa aqui)


def forma(efeitos) -> list[tuple]:
    """Os efeitos sem as frases (o texto do registro e o motivo da reprovação não são regra)."""
    saida = []
    for e in efeitos:
        if isinstance(e, f.Registrar):
            saida.append(R)
        elif isinstance(e, f.Reprovar):
            saida.append(("Reprovar", e.versao))
        else:
            saida.append((type(e).__name__, *e.__dict__.values()))
    return saida


def E(fase, efeitos, **muda):
    """O esperado: a fase nova, o que muda no estado e os efeitos."""
    return fase, muda, efeitos


F = f.Fase
A = dict(versao="1.1.0", anterior="1.1.0", nao_tentar=("1.0.5",))       # o que a abertura comum põe no estado
ESPERADO = {
    # A abertura (só no começo). D-728/D-736/D-741: pelo código, portátil e na conta de testes, nada.
    (F.INICIO, "abriu_codigo"): E(F.FORA, [], versao="1.1.0"),
    (F.INICIO, "abriu_testes"): E(F.FORA, [], versao="1.1.0"),
    (F.INICIO, "abriu_portatil"): E(F.FORA, [], versao="1.1.0"),
    # D-735/D-741/D-806/D-834: sem a licença na pasta, a pergunta do Windows, e nada é procurado.
    (F.INICIO, "abriu_sem_licenca"): E(F.SEM_LICENCA, [("PedirLicenca",)], **A),
    (F.INICIO, "abriu_com_licenca"): E(F.MOTOR, [("GarantirMotor",)], **A),
    # D-718/D-778 e volta 3 (G1): a frase (1) é derivada, uma vez por versão reprovada; sem janela, nada (a próxima
    # abertura com janela deriva de novo).
    (F.INICIO, "abriu_depois_da_volta"): E(F.MOTOR, [("MostrarFalha", "teste", "teste-1.2.0", "", False),
                                                     ("GarantirMotor",)], **{**A, "nao_tentar": ("1.0.5", "1.2.0")}),
    (F.INICIO, "abriu_depois_da_volta_sem_janela"): E(F.PARADO, [R, ("Sair", 0)],
                                                      **{**A, "nao_tentar": ("1.0.5", "1.2.0")}, sem_janela=True),
    # D-718 e volta 3 (A): a versão que roda não é a última boa: o teste rápido antes da janela, pela reabertura ou
    # pelo atalho (a troca que aconteceu sem a reabertura, a volta interrompida).
    (F.INICIO, "abriu_nova"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido", True)], **{**A, "versao": "1.2.0"},
                                nova="1.2.0", antes_da_janela=True),
    (F.INICIO, "abriu_nova_reaberta"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido", True)], **{**A, "versao": "1.2.0"},
                                         nova="1.2.0", antes_da_janela=True),
    (F.INICIO, "abriu_nova_sem_janela"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido", True)],
                                           **{**A, "versao": "1.2.0"}, nova="1.2.0", antes_da_janela=True,
                                           sem_janela=True),
    (F.INICIO, "abriu_nova_sem_licenca"): E(F.SEM_LICENCA, [("PedirLicenca",)], **{**A, "versao": "1.2.0"}),
    # D-839 e volta 3 (M1): o Velopack não trocou e reabriu a de antes: a frase, e a versão NÃO vai para "não tentar".
    (F.INICIO, "abriu_troca_recusada"): E(F.MOTOR, [R, ("MostrarFalha", "troca", "troca-1.2.0", "", False),
                                                    ("GarantirMotor",)], **A),
    (F.INICIO, "abriu_troca_recusada_sem_janela"): E(F.PARADO, [R, ("GuardarFrase", "troca", "1.2.0", ""), R,
                                                                ("Sair", 0)], **A, sem_janela=True),
    # A primeira abertura: sem última boa, o teste por trás (não há para onde voltar); sem o pacote, nem isso.
    (F.INICIO, "abriu_sem_ultima_boa"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido", False)],
                                          **{**A, "anterior": ""}, nova="1.1.0"),
    (F.INICIO, "abriu_sem_ultima_boa_sem_pacote"): E(F.MOTOR, [R, ("GarantirMotor",)], **{**A, "anterior": ""}),
    (F.INICIO, "abriu_sem_janela_sem_nada"): E(F.PARADO, [R, ("Sair", 0)], **A, sem_janela=True),
    # Volta 2, G1 (D-828 (1), D-770): o atualizador do Velopack rodando: nada feito, sai sem janela.
    (F.INICIO, "abriu_troca_em_curso"): E(F.PARADO, [R, ("Sair", 0)], **{**A, "versao": "1.2.0"}),
    # Sem saber se ele roda: a abertura segue.
    (F.INICIO, "abriu_troca_sem_saber"): E(F.MOTOR, [R, ("GarantirMotor",)], **A),
    (F.INICIO, "abriu_frase_guardada"): E(F.MOTOR, [("MostrarFalha", "nao_deu_agora", "nao_deu_agora-1.2.0-x",
                                                     "motor", False), ("GarantirMotor",)], **A),
    (F.INICIO, "abriu_frase_estranha"): E(F.MOTOR, [("GarantirMotor",)], **A),
    # A resposta à pergunta do Windows (D-741: depois do "Não", nada; a pergunta volta na próxima abertura).
    (F.SEM_LICENCA, "lic_comecou"): E(F.PREPARANDO, [("EsperarPreparo",)]),
    (F.SEM_LICENCA, "lic_nao"): E(F.PARADO, [R]),
    (F.SEM_LICENCA, "lic_falhou"): E(F.PARADO, [R]),
    # D-749: a preparação conta como feita só se a pasta aceita gravação DEPOIS dela; então, rodando o que não é a
    # última boa (aqui, 1.1.0 contra 1.0.0), o teste por trás (a janela já abriu).
    (F.PREPARANDO, "prep_ok"): E(F.CONFERINDO_NOVA, [R, ("RodarTesteRapido", False)], nova="1.1.0"),
    (F.PREPARANDO, "prep_nao"): E(F.PARADO, [R]),
    # D-718/D-844: passou, o pacote é guardado como a última boa; com a janela aberta, não volta (fica para a próxima
    # abertura, antes da janela).
    (F.CONFERINDO_NOVA, "teste_ok"): E(F.GUARDANDO, [("GuardarUltimaBoa", "1.2.0", True)]),
    (F.CONFERINDO_NOVA, "teste_nao"): E(F.PARADO, [R]),
    (F.GUARDANDO, "guardada_ok"): E(F.MOTOR, [R, ("GarantirMotor",)], anterior="1.2.0"),
    (F.GUARDANDO, "guardada_nao"): E(F.MOTOR, [R, ("GarantirMotor",)]),
    (F.VOLTANDO, "volta_ok"): E(F.PARADO, [R, ("Sair", 0)]),
    (F.VOLTANDO, "volta_nao"): E(F.PARADO, [R, ("MostrarFalha", "volta", "volta-1.2.0", "", False)]),
    # D-790/D-833: sem o motor, nada é procurado nem anunciado.
    (F.MOTOR, "motor_ok"): E(F.PROCURANDO, [("Procurar",)]),
    (F.MOTOR, "motor_nao"): E(F.PARADO, [R]),
    # D-732: a procura; sem internet não é falha.
    (F.PROCURANDO, "proc_erro"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_nada"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_igual"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_velha"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_estranha"): E(F.PARADO, [R]),
    # D-718: a versão reprovada no teste não é tentada de novo.
    (F.PROCURANDO, "proc_ja_falhou"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_nova"): E(F.CONFERINDO, [("ConferirAssinatura", "1.2.0")], nova="1.2.0"),
    # D-724: baixar só com a assinatura certa; sem ela, a frase 2 uma vez (e não vai para "não tentar": volta 3).
    (F.CONFERINDO, "ass_ok"): E(F.BAIXANDO, [R, ("Baixar", "1.2.0")]),
    (F.CONFERINDO, "ass_nao"): E(F.PARADO, [R, ("MostrarFalha", "recusada", "recusada-1.2.0", "", False)]),
    # D-715/D-720: baixada, o aviso.
    (F.BAIXANDO, "baixou_ok"): E(F.PRONTA, [("MostrarVersaoNova", "1.2.0")]),
    (F.BAIXANDO, "baixou_nao"): E(F.PARADO, [R]),
    # D-833/D-843: sem o motor que a versão nova pede, ela não é anunciada, e a frase aparece uma vez.
    (F.BAIXANDO, "baixou_sem_o_motor_da_nova"): E(F.PARADO, [R, ("MostrarFalha", "motor", "motor-1.2.0", "", False)]),
    (F.BAIXANDO, "baixou_sem_dizer_o_motor"): E(F.PARADO, [R]),
    # Volta 2, M1 e volta 3, M2: "Reiniciar agora" confere (por trás) ANTES de fechar.
    (F.PRONTA, "reiniciar"): E(F.CONFERINDO_TROCA, [("ConferirTroca",)]),
    (F.CONFERINDO_TROCA, "conferida_pode"): E(F.FECHANDO, [("FecharJanela",)]),
    # D-845: qualquer outro "não pode": a frase com o motivo, em resposta ao clique; a pergunta vem ao fechar.
    (F.CONFERINDO_TROCA, "conferida_nao"): E(F.DEPOIS, [R, ("MostrarFalha", "nao_deu_agora", "", "sem_lista",
                                                            True)]),
    # D-840 e D-841: com outra janela aberta, a frase dela e a volta a PRONTA com o mesmo aviso de sempre.
    (F.CONFERINDO_TROCA, "conferida_outra_janela"): E(F.PRONTA, [R, ("MostrarFalha", "nao_deu_agora", "",
                                                                     "outra_janela", True),
                                                                 ("MostrarVersaoNova", "1.2.0")]),
    (F.CONFERINDO_TROCA, "conferida_recusada"): E(F.PARADO, [R, ("MostrarFalha", "recusada", "recusada-1.2.0", "",
                                                                 True)]),
    (F.PRONTA, "depois"): E(F.DEPOIS, [R]),
    # D-769/D-794/D-831: ao fechar com versão pronta, a pergunta.
    (F.PRONTA, "fechando"): E(F.PERGUNTANDO, [("PerguntarAoFechar",)]),
    (F.DEPOIS, "fechando"): E(F.PERGUNTANDO, [("PerguntarAoFechar",)]),
    # D-720/D-828: a troca só depois de a janela fechar (gravando).
    (F.FECHANDO, "fechou"): E(F.TROCANDO, [("Trocar", "1.1.0", "1.2.0", f.REABRIR_COM_JANELA)],
                              trocando_com_janela=True),
    (F.FECHANDO, "nao_fechou"): E(F.DEPOIS, [R, ("MostrarFalha", "nao_deu_agora", "", "nao_fechou", True)]),
    # D-769: com o "Sim" ao fechar, nada abre na tela depois (só a conferência, sem janela).
    (F.PERGUNTANDO, "sim"): E(F.TROCANDO, [("Trocar", "1.1.0", "1.2.0", f.REABRIR_SEM_JANELA)]),
    (F.PERGUNTANDO, "nao"): E(F.PARADO, [R]),
    # O "Sim" ao fechar (sem janela): o programa ia fechar mesmo; só fica no registro.
    (F.TROCANDO, "troca_ok"): E(F.TROCANDO, [R]),
    (F.TROCANDO, "troca_recusada"): E(F.PARADO, [R]),
    (F.TROCANDO, "troca_nao"): E(F.PARADO, [R]),
    (F.TROCANDO, "troca_outra_janela"): E(F.PARADO, [R]),
}


def _estado(fase: f.Fase) -> f.Estado:
    return f.Estado() if fase is f.Fase.INICIO else replace(BASE, fase=fase)


@pytest.mark.parametrize("fase", list(f.Fase), ids=lambda x: x.value)
@pytest.mark.parametrize("nome", list(EVENTOS))
def test_todo_par_fase_evento_tem_a_resposta_escrita(fase, nome):
    """Para cada fase e cada evento: o caso da tabela, ou "fica e anota" (o fechar: fica e não faz nada)."""
    antes = _estado(fase)
    depois, efeitos = f.proxima_fase(antes, EVENTOS[nome])
    if (fase, nome) in ESPERADO:
        fase_nova, muda, esperados = ESPERADO[(fase, nome)]
        assert depois == replace(antes, fase=fase_nova, **muda)
        assert forma(efeitos) == esperados
    elif nome == "fechando":
        assert (depois, efeitos) == (antes, [])
    else:
        assert depois == antes
        assert forma(efeitos) == [R]


def test_a_tabela_so_tem_pares_que_existem():
    """Nenhuma linha da tabela fala de evento ou fase que não existe (uma tabela errada passaria calada)."""
    assert {n for _, n in ESPERADO} <= set(EVENTOS)
    assert {type(e) for e in EVENTOS.values()} == set(f.TIPOS_DE_EVENTO)


@pytest.mark.parametrize("fase", list(f.Fase), ids=lambda x: x.value)
@pytest.mark.parametrize("nome", list(EVENTOS))
def test_m1_so_o_teste_reprovado_poe_a_versao_em_nao_tentar(fase, nome):
    """Volta 3, M1 (D-769: "nada se perde e a troca tenta de novo depois"): em NENHUM par (fase, evento) o "não
    tentar" cresce sem o efeito `Reprovar`, e `Reprovar` só sai do teste rápido que não passou. A troca que não
    aconteceu, a assinatura recusada e o "Reiniciar agora" que não pôde nunca proíbem a versão."""
    for antes in (_estado(fase), replace(_estado(fase), antes_da_janela=True, trocando_com_janela=True)):
        depois, efeitos = f.proxima_fase(antes, EVENTOS[nome])
        reprovou = [e for e in efeitos if isinstance(e, f.Reprovar)]
        lidas = set(EVENTOS[nome].nao_tentar) if isinstance(EVENTOS[nome], f.Abriu) else set()  # as do bilhete
        cresceu = set(depois.nao_tentar) - set(antes.nao_tentar) - lidas
        assert cresceu == {e.versao for e in reprovou}
        if reprovou:
            assert (fase, nome) == (f.Fase.CONFERINDO_NOVA, "teste_nao")


def test_d718_o_teste_antes_da_janela_que_falha_volta_pela_ultima_boa():
    """D-718/D-844: com o teste antes da janela e uma última boa, a versão vai para "não tentar" e a volta é pedida."""
    antes = replace(BASE, fase=F.CONFERINDO_NOVA, antes_da_janela=True)
    depois, efeitos = f.proxima_fase(antes, EVENTOS["teste_nao"])
    assert depois.fase is F.VOLTANDO and depois.nao_tentar == ("1.2.0", "1.3.0")
    assert forma(efeitos) == [("Reprovar", "1.2.0"), ("Voltar", "1.2.0", "1.0.0", True)]


def test_sem_ultima_boa_o_teste_que_falha_nao_volta_e_segue():
    """Sem última boa (a primeira abertura), não há para onde voltar: fica no registro e a abertura segue."""
    antes = replace(BASE, fase=F.CONFERINDO_NOVA, anterior="", nova="1.1.0")
    depois, efeitos = f.proxima_fase(antes, EVENTOS["teste_nao"])
    assert depois.fase is F.MOTOR and forma(efeitos) == [R, ("GarantirMotor",)] and depois.nao_tentar == ("1.3.0",)


@pytest.mark.parametrize("nome, fase_nova, esperados", [
    ("teste_ok", F.GUARDANDO, [("GuardarUltimaBoa", "1.2.0", False)]),
    ("teste_nao", F.VOLTANDO, [("Reprovar", "1.2.0"), ("Voltar", "1.2.0", "1.0.0", False)]),
])
def test_d769_na_reabertura_sem_janela_nada_abre(nome, fase_nova, esperados):
    """D-769 (com "Depois", entra ao fechar; nada abre): na reabertura sem janela, a guarda é feita nesta linha (o
    processo sai logo depois), e a volta é pedida sem reabrir."""
    antes = replace(BASE, fase=F.CONFERINDO_NOVA, sem_janela=True, antes_da_janela=True)
    depois, efeitos = f.proxima_fase(antes, EVENTOS[nome])
    assert depois.fase is fase_nova and forma(efeitos) == esperados


def test_d769_sem_janela_guardada_ou_volta_que_falha_sai():
    """Sem janela: guardada a última boa, sai; a volta que não deu guarda a frase (3) para a próxima abertura e sai."""
    guardando = replace(BASE, fase=F.GUARDANDO, sem_janela=True)
    assert forma(f.proxima_fase(guardando, EVENTOS["guardada_ok"])[1]) == [R, ("Sair", 0)]
    voltando = replace(BASE, fase=F.VOLTANDO, sem_janela=True)
    depois, efeitos = f.proxima_fase(voltando, EVENTOS["volta_nao"])
    assert depois.fase is F.PARADO and forma(efeitos) == [R, ("GuardarFrase", "volta", "1.2.0", ""), ("Sair", 0)]


def test_um_evento_desconhecido_nunca_levanta():
    """Qualquer coisa que não seja um evento: fica e anota."""
    for fase in f.Fase:
        depois, efeitos = f.proxima_fase(_estado(fase), object())
        assert depois == _estado(fase) and forma(efeitos) == [R]


def test_as_falhas_tem_nome_unico_por_tipo_e_versao():
    """O nome da frase (a tela mostra uma vez por nome) é o tipo e a versão."""
    assert f.id_da_falha("teste", "1.2.0") == "teste-1.2.0"
    assert set(f.TIPOS_DE_FALHA) == {"teste", "troca", "recusada", "volta", "motor", "nao_deu_agora"}


def test_a_regra_nao_fala_com_o_mundo_de_fora():
    """O arquivo da regra só importa `dataclasses`, `enum`, `typing` (e o `__future__`): nada de disco, rede, Windows,
    Velopack ou tela. Lido pela árvore do código."""
    arvore = ast.parse((RAIZ / "core" / "fases_da_atualizacao.py").read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            importados.add((no.module or "").split(".")[0])
        elif isinstance(no, ast.Call) and getattr(no.func, "id", "") in ("open", "__import__", "exec", "eval"):
            importados.add(no.func.id)
    assert importados <= {"__future__", "dataclasses", "enum", "typing"}, importados


def test_m1_m3_m5_a_troca_do_reiniciar_que_nao_foi_pedida_reabre_com_a_frase():
    """Volta 2, M1 e volta 3, M3/M5: depois de a janela fechar no "Reiniciar agora", a troca que não pôde ser pedida
    reabre o programa e guarda a frase da D-845 (ou a 2, se o pacote foi trocado) para a reabertura mostrar; com outra
    janela do programa aberta, NÃO reabre (seriam duas janelas). No "Sim" ao fechar, nada (ia fechar)."""
    com = replace(BASE, fase=F.TROCANDO, trocando_com_janela=True)
    assert forma(f.proxima_fase(com, EVENTOS["troca_nao"])[1]) == [
        R, ("GuardarFrase", "nao_deu_agora", "1.2.0", "atualizador"), ("ReabrirOPrograma",)]
    assert forma(f.proxima_fase(com, EVENTOS["troca_recusada"])[1]) == [
        R, ("GuardarFrase", "recusada", "1.2.0", ""), ("ReabrirOPrograma",)]
    assert forma(f.proxima_fase(com, EVENTOS["troca_outra_janela"])[1]) == [R, R]
    assert forma(f.proxima_fase(replace(BASE, fase=F.TROCANDO), EVENTOS["troca_nao"])[1]) == [R]


def test_preparado_rodando_a_ultima_boa_vai_ao_motor():
    """Depois do "Sim", rodando a última boa: o motor e a procura (sem teste)."""
    antes = replace(BASE, fase=F.PREPARANDO, anterior="1.1.0")
    depois, efeitos = f.proxima_fase(antes, EVENTOS["prep_ok"])
    assert depois.fase is F.MOTOR and forma(efeitos) == [R, ("GarantirMotor",)]
