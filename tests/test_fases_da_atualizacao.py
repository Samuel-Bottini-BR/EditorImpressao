"""A regra da atualização, inteira: todas as fases com todos os eventos (atualizador novo, 23/11/2026, D-830).

O que se prova (o plano, seção 11: "A regra, exaustiva"): `core.fases_da_atualizacao.proxima_fase` responde a TODO par
(fase, evento). A tabela `ESPERADO` diz, caso por caso, a fase nova, o que muda no estado e os efeitos; todo par que
não está nela é "não faz sentido aqui": fica na mesma fase e só anota (o `Fechando` fica e não faz nada). Mudar uma
transição sem mudar esta tabela faz o teste falhar: é para isso que ela existe. Cada linha diz a decisão do Samuel que
protege.

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
COMUM = dict(instalado=True, conta_de_testes=False, portatil=False, pasta_grava=True, versao="1.1.0",
             nao_tentar=("1.3.0",))

# Os eventos de amostra (cada caso que a regra separa tem o seu).
EVENTOS = {
    "abriu_codigo": f.Abriu(**{**COMUM, "instalado": False}),
    "abriu_testes": f.Abriu(**{**COMUM, "conta_de_testes": True}),
    "abriu_portatil": f.Abriu(**{**COMUM, "portatil": True}),
    "abriu_sem_licenca": f.Abriu(**{**COMUM, "pasta_grava": False}),
    "abriu_com_licenca": f.Abriu(**COMUM),
    "abriu_com_falha": f.Abriu(**COMUM, falha_anotada=("teste", "teste-1.2.0")),
    "abriu_com_falha_estranha": f.Abriu(**COMUM, falha_anotada=("outra", "x")),
    "abriu_trocou": f.Abriu(**{**COMUM, "versao": "1.2.0"}, troca_de="1.1.0", troca_para="1.2.0"),
    "abriu_trocou_sem_janela": f.Abriu(**{**COMUM, "versao": "1.2.0"}, troca_de="1.1.0", troca_para="1.2.0",
                                       sem_janela=True),
    "abriu_nao_trocou": f.Abriu(**COMUM, troca_de="1.1.0", troca_para="1.2.0"),
    "abriu_nao_trocou_sem_licenca": f.Abriu(**{**COMUM, "pasta_grava": False}, troca_de="1.1.0", troca_para="1.2.0"),
    "abriu_nao_trocou_sem_janela": f.Abriu(**COMUM, troca_de="1.1.0", troca_para="1.2.0", sem_janela=True),
    "abriu_volta_ok": f.Abriu(**COMUM, troca_de="1.2.0", troca_para="1.1.0", troca_volta=True,
                              falha_anotada=("teste", "teste-1.2.0")),
    "abriu_volta_nao": f.Abriu(**{**COMUM, "versao": "1.2.0"}, troca_de="1.2.0", troca_para="1.1.0", troca_volta=True),
    "abriu_volta_nao_sem_janela": f.Abriu(**{**COMUM, "versao": "1.2.0"}, troca_de="1.2.0", troca_para="1.1.0",
                                          troca_volta=True, sem_janela=True),
    "abriu_velha": f.Abriu(**{**COMUM, "versao": "1.3.0"}, troca_de="1.1.0", troca_para="1.2.0"),
    "abriu_velha_sem_janela": f.Abriu(**{**COMUM, "versao": "1.3.0"}, troca_de="1.1.0", troca_para="1.2.0",
                                      sem_janela=True),
    "abriu_sem_janela_sem_troca": f.Abriu(**COMUM, sem_janela=True),
    # Volta 2 (G1): a troca anotada ainda acontecendo, ou sem saber; (M4) o estado que não grava.
    "abriu_troca_em_curso": f.Abriu(**COMUM, troca_de="1.1.0", troca_para="1.2.0", troca_em_curso=True),
    "abriu_troca_sem_saber": f.Abriu(**COMUM, troca_de="1.1.0", troca_para="1.2.0", troca_em_curso=None),
    "abriu_volta_em_curso": f.Abriu(**{**COMUM, "versao": "1.2.0"}, troca_de="1.2.0", troca_para="1.1.0",
                                    troca_volta=True, troca_em_curso=True),
    "abriu_estado_nao_grava": f.Abriu(**COMUM, estado_grava=False),
    "lic_comecou": f.LicencaRespondida("comecou"),
    "lic_nao": f.LicencaRespondida("disse_nao"),
    "lic_falhou": f.LicencaRespondida("falhou", "o Windows não abriu"),
    "prep_ok": f.PreparoTerminou(True),
    "prep_nao": f.PreparoTerminou(False, "o Visual C++ falhou"),
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
    "conferida_pode": f.TrocaConferida(True),
    "conferida_nao": f.TrocaConferida(False, "outra janela aberta"),
    "conferida_recusada": f.TrocaConferida(False, "a soma não confere", recusada=True),
    "reiniciar": f.Escolheu(True),
    "depois": f.Escolheu(False),
    "fechou": f.JanelaFechou(True),
    "nao_fechou": f.JanelaFechou(False),
    "fechando": f.Fechando(),
    "sim": f.RespondeuAoFechar(True),
    "nao": f.RespondeuAoFechar(False),
    "troca_ok": f.TrocaPedida(True),
    "troca_recusada": f.TrocaPedida(False, "a soma não confere", recusada=True),
    "troca_nao": f.TrocaPedida(False, "outra janela aberta"),
    "teste_ok": f.TesteRapido(True),
    "teste_nao": f.TesteRapido(False, "código 1"),
    "volta_ok": f.VoltaPedida(True),
    "volta_nao": f.VoltaPedida(False, "sem internet"),
}

R = ("Registrar",)            # uma linha no registro (o texto não importa aqui)


def forma(efeitos) -> list[tuple]:
    """Os efeitos sem as frases (o texto do registro e o motivo da falha não são regra)."""
    saida = []
    for e in efeitos:
        if isinstance(e, f.Registrar):
            saida.append(R)
        elif isinstance(e, f.AnotarFalha):
            saida.append(("AnotarFalha", e.tipo, e.fica, e.falhou))
        else:
            saida.append((type(e).__name__, *e.__dict__.values()))
    return saida


def E(fase, efeitos, **muda):
    """O esperado: a fase nova, o que muda no estado e os efeitos."""
    return fase, muda, efeitos


F = f.Fase
ESPERADO = {
    # A abertura (só no começo). D-728/D-736/D-741: pelo código, portátil e na conta de testes, nada.
    (F.INICIO, "abriu_codigo"): E(F.FORA, [], versao="1.1.0"),
    (F.INICIO, "abriu_testes"): E(F.FORA, [], versao="1.1.0"),
    (F.INICIO, "abriu_portatil"): E(F.FORA, [], versao="1.1.0"),
    # D-735/D-741/D-806/D-834: sem a licença na pasta, a pergunta do Windows, e nada é procurado.
    (F.INICIO, "abriu_sem_licenca"): E(F.SEM_LICENCA, [("PedirLicenca",)], versao="1.1.0", nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_com_licenca"): E(F.MOTOR, [("GarantirMotor",)], versao="1.1.0", nao_tentar=("1.3.0",)),
    # D-719/D-778: a falha anotada vai para a janela (que a mostra uma vez por conta).
    (F.INICIO, "abriu_com_falha"): E(F.MOTOR, [("MostrarFalha", "teste", "teste-1.2.0"), ("GarantirMotor",)],
                                     versao="1.1.0", nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_com_falha_estranha"): E(F.MOTOR, [("GarantirMotor",)], versao="1.1.0", nao_tentar=("1.3.0",)),
    # D-718: reaberto na versão nova, o teste rápido antes da janela.
    (F.INICIO, "abriu_trocou"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido",)], versao="1.2.0", nova="1.2.0",
                                  anterior="1.1.0", nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_trocou_sem_janela"): E(F.CONFERINDO_NOVA, [("RodarTesteRapido",)], versao="1.2.0", nova="1.2.0",
                                             anterior="1.1.0", nao_tentar=("1.3.0",), sem_janela=True),
    # A troca não aconteceu: falha "troca" (frase 1), a versão vai para "não tentar".
    (F.INICIO, "abriu_nao_trocou"): E(F.MOTOR, [("AnotarFalha", "troca", "1.1.0", "1.2.0"),
                                                ("MostrarFalha", "troca", "troca-1.2.0"), ("GarantirMotor",)],
                                      versao="1.1.0", nao_tentar=("1.2.0", "1.3.0")),
    (F.INICIO, "abriu_nao_trocou_sem_licenca"): E(F.SEM_LICENCA, [("AnotarFalha", "troca", "1.1.0", "1.2.0"),
                                                                  ("MostrarFalha", "troca", "troca-1.2.0"),
                                                                  ("PedirLicenca",)],
                                                  versao="1.1.0", nao_tentar=("1.2.0", "1.3.0")),
    (F.INICIO, "abriu_nao_trocou_sem_janela"): E(F.PARADO, [("AnotarFalha", "troca", "1.1.0", "1.2.0"), ("Sair", 0)],
                                                 versao="1.1.0", nao_tentar=("1.2.0", "1.3.0"), sem_janela=True),
    # A volta aconteceu: a anterior abre, mostra a falha (frase 1) e apaga a anotação da troca.
    (F.INICIO, "abriu_volta_ok"): E(F.MOTOR, [("MostrarFalha", "teste", "teste-1.2.0"), ("AnotarOk", "1.1.0"),
                                              ("GarantirMotor",)], versao="1.1.0", nao_tentar=("1.3.0",)),
    # A volta não aconteceu: falha "volta" (frase 3).
    (F.INICIO, "abriu_volta_nao"): E(F.MOTOR, [("AnotarFalha", "volta", "1.2.0", "1.2.0"),
                                               ("MostrarFalha", "volta", "volta-1.2.0"), ("GarantirMotor",)],
                                     versao="1.2.0", nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_volta_nao_sem_janela"): E(F.PARADO, [("AnotarFalha", "volta", "1.2.0", "1.2.0"), ("Sair", 0)],
                                                versao="1.2.0", nao_tentar=("1.3.0",), sem_janela=True),
    (F.INICIO, "abriu_velha"): E(F.MOTOR, [R, ("AnotarOk", "1.3.0"), ("GarantirMotor",)], versao="1.3.0",
                                 nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_velha_sem_janela"): E(F.PARADO, [R, ("AnotarOk", "1.3.0"), ("Sair", 0)], versao="1.3.0",
                                            nao_tentar=("1.3.0",), sem_janela=True),
    (F.INICIO, "abriu_sem_janela_sem_troca"): E(F.PARADO, [R, ("Sair", 0)], versao="1.1.0", nao_tentar=("1.3.0",),
                                                sem_janela=True),
    # Volta 2, G1 (D-828 (1), D-770): a troca ainda acontecendo (o clique no atalho no meio dela): nada anotado, sai.
    (F.INICIO, "abriu_troca_em_curso"): E(F.PARADO, [R, ("Sair", 0)], versao="1.1.0", nao_tentar=("1.3.0",)),
    (F.INICIO, "abriu_volta_em_curso"): E(F.PARADO, [R, ("Sair", 0)], versao="1.2.0", nao_tentar=("1.3.0",)),
    # Sem saber se ainda acontece: nada anotado, a abertura segue.
    (F.INICIO, "abriu_troca_sem_saber"): E(F.MOTOR, [R, ("GarantirMotor",)], versao="1.1.0", nao_tentar=("1.3.0",)),
    # Volta 2, M4: o estado que não grava fica no estado (a procura é barrada depois do motor).
    (F.INICIO, "abriu_estado_nao_grava"): E(F.MOTOR, [("GarantirMotor",)], versao="1.1.0", nao_tentar=("1.3.0",),
                                            estado_grava=False),
    # A resposta à pergunta do Windows (D-741: depois do "Não", nada; a pergunta volta na próxima abertura).
    (F.SEM_LICENCA, "lic_comecou"): E(F.PREPARANDO, [("EsperarPreparo",)]),
    (F.SEM_LICENCA, "lic_nao"): E(F.PARADO, [R]),
    (F.SEM_LICENCA, "lic_falhou"): E(F.PARADO, [R]),
    # D-749: a preparação conta como feita só se a pasta aceita gravação DEPOIS dela.
    (F.PREPARANDO, "prep_ok"): E(F.MOTOR, [R, ("GarantirMotor",)]),
    (F.PREPARANDO, "prep_nao"): E(F.PARADO, [R]),
    # D-790/D-833: sem o motor, nada é procurado nem anunciado.
    (F.MOTOR, "motor_ok"): E(F.PROCURANDO, [("Procurar",)]),
    (F.MOTOR, "motor_nao"): E(F.PARADO, [R]),
    # D-732: a procura; sem internet não é falha.
    (F.PROCURANDO, "proc_erro"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_nada"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_igual"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_velha"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_estranha"): E(F.PARADO, [R]),
    # D-718: a versão que falhou não é tentada de novo.
    (F.PROCURANDO, "proc_ja_falhou"): E(F.PARADO, [R]),
    (F.PROCURANDO, "proc_nova"): E(F.CONFERINDO, [("ConferirAssinatura", "1.2.0")], nova="1.2.0"),
    # D-724: baixar só com a assinatura certa; sem ela, falha "recusada" (frase 2).
    (F.CONFERINDO, "ass_ok"): E(F.BAIXANDO, [R, ("Baixar", "1.2.0")]),
    (F.CONFERINDO, "ass_nao"): E(F.PARADO, [("AnotarFalha", "recusada", "1.1.0", "1.2.0"),
                                            ("MostrarFalha", "recusada", "recusada-1.2.0")],
                                 nao_tentar=("1.2.0", "1.3.0")),
    # D-715/D-720: baixada, o aviso.
    (F.BAIXANDO, "baixou_ok"): E(F.PRONTA, [("MostrarVersaoNova", "1.2.0")]),
    (F.BAIXANDO, "baixou_nao"): E(F.PARADO, [R]),
    # Volta 2, M2 (D-833): sem o motor que a versão nova pede, ela não é anunciada.
    (F.BAIXANDO, "baixou_sem_o_motor_da_nova"): E(F.PARADO, [R]),
    # Volta 2, M1: "Reiniciar agora" confere ANTES de fechar; sem poder, a janela fica aberta.
    (F.PRONTA, "reiniciar"): E(F.CONFERINDO_TROCA, [("ConferirTroca",)]),
    (F.CONFERINDO_TROCA, "conferida_pode"): E(F.FECHANDO, [("FecharJanela",)]),
    (F.CONFERINDO_TROCA, "conferida_nao"): E(F.DEPOIS, [R]),
    (F.CONFERINDO_TROCA, "conferida_recusada"): E(F.PARADO, [("AnotarFalha", "recusada", "1.1.0", "1.2.0"),
                                                             ("MostrarFalha", "recusada", "recusada-1.2.0")],
                                                  nao_tentar=("1.2.0", "1.3.0")),
    (F.PRONTA, "depois"): E(F.DEPOIS, [R]),
    # D-769/D-794/D-831: ao fechar com versão pronta, a pergunta.
    (F.PRONTA, "fechando"): E(F.PERGUNTANDO, [("PerguntarAoFechar",)]),
    (F.DEPOIS, "fechando"): E(F.PERGUNTANDO, [("PerguntarAoFechar",)]),
    # D-720/D-828: a troca só depois de a janela fechar (gravando).
    (F.FECHANDO, "fechou"): E(F.TROCANDO, [("Trocar", "1.1.0", "1.2.0", f.REABRIR_COM_JANELA)],
                              trocando_com_janela=True),
    (F.FECHANDO, "nao_fechou"): E(F.DEPOIS, [R]),
    # D-769: com o "Sim" ao fechar, nada abre na tela depois (só a conferência, sem janela).
    (F.PERGUNTANDO, "sim"): E(F.TROCANDO, [("Trocar", "1.1.0", "1.2.0", f.REABRIR_SEM_JANELA)]),
    (F.PERGUNTANDO, "nao"): E(F.PARADO, [R]),
    (F.TROCANDO, "troca_ok"): E(F.TROCANDO, [R]),
    (F.TROCANDO, "troca_recusada"): E(F.PARADO, [("AnotarFalha", "recusada", "1.1.0", "1.2.0")],
                                      nao_tentar=("1.2.0", "1.3.0")),
    (F.TROCANDO, "troca_nao"): E(F.PARADO, [R]),
    # D-718: o teste rápido; falhou, volta para a anterior (só pacote assinado, quem confere é o executor).
    (F.CONFERINDO_NOVA, "teste_ok"): E(F.MOTOR, [("AnotarOk", "1.2.0"), ("GarantirMotor",)]),
    (F.CONFERINDO_NOVA, "teste_nao"): E(F.VOLTANDO, [("AnotarFalha", "teste", "1.0.0", "1.2.0"),
                                                     ("Voltar", "1.2.0", "1.0.0", True)],
                                        nao_tentar=("1.2.0", "1.3.0")),
    (F.VOLTANDO, "volta_ok"): E(F.PARADO, [("Sair", 0)]),
    (F.VOLTANDO, "volta_nao"): E(F.PARADO, [("AnotarFalha", "volta", "1.2.0", "1.2.0"),
                                            ("MostrarFalha", "volta", "volta-1.2.0")]),
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


@pytest.mark.parametrize("nome, fase_nova, esperados", [
    ("teste_ok", F.PARADO, [("AnotarOk", "1.2.0"), ("Sair", 0)]),
    ("teste_nao", F.VOLTANDO, [("AnotarFalha", "teste", "1.0.0", "1.2.0"), ("Voltar", "1.2.0", "1.0.0", False)]),
])
def test_d769_na_reabertura_sem_janela_nada_abre(nome, fase_nova, esperados):
    """D-769 (com "Depois", entra ao fechar; nada abre): na reabertura sem janela, o teste que passa sai sem janela, e
    a volta é pedida sem reabrir."""
    antes = replace(BASE, fase=F.CONFERINDO_NOVA, sem_janela=True)
    depois, efeitos = f.proxima_fase(antes, EVENTOS[nome])
    assert depois.fase is fase_nova and forma(efeitos) == esperados


def test_d769_a_volta_que_falha_sem_janela_sai_sem_janela():
    """A volta que não deu, na reabertura sem janela: anota a falha (frase 3 na próxima abertura) e sai."""
    antes = replace(BASE, fase=F.VOLTANDO, sem_janela=True)
    depois, efeitos = f.proxima_fase(antes, EVENTOS["volta_nao"])
    assert depois.fase is F.PARADO and forma(efeitos) == [("AnotarFalha", "volta", "1.2.0", "1.2.0"), ("Sair", 0)]


def test_um_evento_desconhecido_nunca_levanta():
    """Qualquer coisa que não seja um evento: fica e anota."""
    for fase in f.Fase:
        depois, efeitos = f.proxima_fase(_estado(fase), object())
        assert depois == _estado(fase) and forma(efeitos) == [R]


def test_as_falhas_tem_nome_unico_por_tipo_e_versao():
    """O nome da falha (a tela mostra uma vez por nome) é o tipo e a versão que falhou."""
    assert f.id_da_falha("teste", "1.2.0") == "teste-1.2.0"
    assert set(f.TIPOS_DE_FALHA) == {"teste", "troca", "recusada", "volta"}


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


def test_m1_a_troca_do_reiniciar_que_nao_foi_pedida_reabre_o_programa():
    """Volta 2, achado M1: depois de a janela fechar no "Reiniciar agora", a troca que não pôde ser pedida (o Velopack
    recusou, ou a conferência mudou nos segundos do fechar) reabre o programa; no "Sim" ao fechar, não (ia fechar)."""
    com = replace(BASE, fase=F.TROCANDO, trocando_com_janela=True)
    assert forma(f.proxima_fase(com, EVENTOS["troca_nao"])[1]) == [R, ("ReabrirOPrograma",)]
    assert forma(f.proxima_fase(com, EVENTOS["troca_recusada"])[1]) == [("AnotarFalha", "recusada", "1.1.0", "1.2.0"),
                                                                       ("ReabrirOPrograma",)]
    assert forma(f.proxima_fase(BASE.__class__(**{**BASE.__dict__, "fase": F.TROCANDO}), EVENTOS["troca_nao"])[1]) == [R]


def test_m4_sem_o_estado_gravando_nada_e_procurado():
    """Volta 2, achado M4: com o estado que não grava, o motor no lugar não leva à procura (a versão que falhasse não
    ficaria em "não tentar")."""
    antes = replace(BASE, fase=F.MOTOR, estado_grava=False)
    depois, efeitos = f.proxima_fase(antes, EVENTOS["motor_ok"])
    assert depois.fase is F.PARADO and forma(efeitos) == [R]
