"""Prova EXECUTADA (quem tenta quebrar 3, 24/11/2026): a regra de verdade (`core.fases_da_atualizacao.proxima_fase`,
do ramo, sem nada trocado) nos caminhos que eu quis olhar. É a lógica só (sem disco nem Windows): o que ela MANDA o
programa fazer. Cada caso diz de onde vem o evento no programa de verdade.

R1  "Sim" ao fechar, e a troca não pode (outra janela, o pacote sumiu, o motor, a lista do Windows, o pacote trocado,
    o atualizador que não começou): alguma frase aparece, agora ou na próxima abertura?
R2  Sem última boa guardada (a primeira versão depois do .msi, quando a guarda não conseguiu), a versão nova entra e
    não passa no teste: o que aparece, e ela é reprovada?
R3  A guarda da versão nova falhou (sem espaço, assinatura não lida): o que acontece nas aberturas seguintes?
R4  ReabrirOPrograma: em quais "não deu" da troca depois de a janela fechar ele é mandado.
R5  "Tente ao fechar o programa" (a frase guardada da reabertura) numa abertura sem internet: ao fechar, a pergunta vem?
R6  A abertura com um pacote baixado esperando (o Velopack diz "pendente"), sem internet: o aviso volta?
Uso: python prova_regra.py (saída em prova_regra-resultado.txt)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAMO))

from core import fases_da_atualizacao as f  # noqa: E402

TELA = (f.MostrarFalha, f.GuardarFrase, f.MostrarVersaoNova, f.PerguntarAoFechar)


def abriu(**k) -> f.Abriu:
    base = dict(instalado=True, conta_de_testes=False, portatil=False, pasta_grava=True, versao="1.1.0",
                ultima_boa="1.1.0")
    base.update(k)
    return f.Abriu(**base)


def seguir(estado, eventos):
    todos = []
    for e in eventos:
        estado, efs = f.proxima_fase(estado, e)
        todos += efs
    return estado, todos


def so_tela(efs):
    return [repr(e) for e in efs if isinstance(e, TELA)]


def main() -> None:
    res: dict = {}
    ate_perguntar = [abriu(), f.MotorConferido(True), f.Procurou("1.2.0"), f.Assinatura(True), f.Baixou(True),
                     f.Escolheu(False), f.Fechando(), f.RespondeuAoFechar(True)]
    r1 = {}
    for nome, pedida in (
            ("outra janela aberta", f.TrocaPedida(False, "x", outra_janela=True, motivo_da_tela=f.MOTIVO_OUTRA_JANELA)),
            ("o pacote sumiu", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_PACOTE_SUMIU)),
            ("o motor fora do lugar", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_MOTOR)),
            ("sem a lista do Windows", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_SEM_LISTA)),
            ("o pacote trocado (sem a soma assinada)", f.TrocaPedida(False, "x", recusada=True)),
            ("o atualizador não começou", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_ATUALIZADOR))):
        estado, efs = seguir(f.Estado(), ate_perguntar + [pedida])
        r1[nome] = {"fase": estado.fase.value, "na tela ou guardado para a próxima abertura": so_tela(efs[-3:]),
                    "efeitos depois do Sim": [repr(e) for e in efs[efs.index(next(x for x in efs
                                                                                  if isinstance(x, f.Trocar))) + 1:]]}
    res["R1 Sim ao fechar e a troca não pode"] = r1

    r2 = {}
    for como, k in (("reaberto pelo Reiniciar agora (com janela)", {}),
                    ("reaberto pelo Sim ao fechar (sem janela)", {"sem_janela": True}),
                    ("a abertura seguinte, pelo atalho", {"reaberto_de": "", "reaberto_para": ""})):
        a = dict(versao="1.2.0", ultima_boa="", reaberto_de="1.1.0", reaberto_para="1.2.0")
        a.update(k)
        estado, efs = f.proxima_fase(f.Estado(), abriu(**a))
        teste = [e for e in efs if isinstance(e, f.RodarTesteRapido)]
        depois = []
        if teste:
            estado, depois = f.proxima_fase(estado, f.TesteRapido(False, "código 1"))
        r2[como] = {"o teste roda?": [repr(t) for t in teste], "depois do teste reprovado": [repr(e) for e in depois],
                    "frase": so_tela(efs + depois), "reprovada?": any(isinstance(e, f.Reprovar) for e in depois)}
    res["R2 sem última boa, a versão nova reprovada no teste"] = r2

    r3 = []
    for abertura in (1, 2, 3):
        estado, efs = seguir(f.Estado(), [abriu(versao="1.2.0", ultima_boa="1.1.0"), f.TesteRapido(True),
                                           f.UltimaBoaGuardada(False, "sem espaço no disco")])
        r3.append({"abertura": abertura, "efeitos": [repr(e) for e in efs], "frase": so_tela(efs)})
    res["R3 a guarda da 1.2.0 falhou: as aberturas seguintes"] = r3

    r4 = {}
    ate_fechar = [abriu(), f.MotorConferido(True), f.Procurou("1.2.0"), f.Assinatura(True), f.Baixou(True),
                  f.Escolheu(True), f.TrocaConferida(True), f.JanelaFechou(True)]
    for nome, pedida in (("outra janela", f.TrocaPedida(False, "x", outra_janela=True)),
                         ("o pacote trocado", f.TrocaPedida(False, "x", recusada=True)),
                         ("o pacote sumiu", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_PACOTE_SUMIU)),
                         ("o motor", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_MOTOR)),
                         ("sem a lista", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_SEM_LISTA)),
                         ("sem conferir", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_SEM_CONFERIR)),
                         ("o atualizador não começou", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_ATUALIZADOR)),
                         ("erro inesperado", f.TrocaPedida(False, "x", motivo_da_tela=f.MOTIVO_ERRO))):
        _, efs = seguir(f.Estado(), ate_fechar + [pedida])
        r4[nome] = "REABRE" if any(isinstance(e, f.ReabrirOPrograma) for e in efs) else "não reabre"
    res["R4 ReabrirOPrograma: os casos que o mandam (todos depois de a janela fechar)"] = r4

    estado, efs = seguir(f.Estado(), [abriu(frase_guardada=(f.NAO_DEU_AGORA, "nao_deu_agora-1.2.0-x",
                                                            f.MOTIVO_ATUALIZADOR)),
                                      f.MotorConferido(True), f.Procurou(None, "sem internet"), f.Fechando()])
    res["R5 a frase 'Tente ao fechar o programa' e, sem internet, o fechar"] = {
        "na tela": so_tela(efs), "a pergunta ao fechar veio?": any(isinstance(e, f.PerguntarAoFechar) for e in efs),
        "fase no fim": estado.fase.value}

    estado, efs = seguir(f.Estado(), [abriu(pendente="1.2.0"), f.MotorConferido(True),
                                      f.Procurou(None, "sem internet"), f.Fechando()])
    res["R6 o pacote baixado esperando, sem internet"] = {
        "o aviso volta?": any(isinstance(e, f.MostrarVersaoNova) for e in efs),
        "a pergunta ao fechar vem?": any(isinstance(e, f.PerguntarAoFechar) for e in efs),
        "a regra usa o campo pendente em algum lugar?": "pendente" in (RAMO / "core" / "fases_da_atualizacao.py").read_text(
            encoding="utf-8").split("def proxima_fase")[0].split("def _ao_abrir")[1]}
    texto = json.dumps(res, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_regra-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
