"""Volta 3, segunda parte (24/11/2026): as respostas do Samuel às perguntas da volta 3 (D-847 a D-853).

- D-848 ("2 — sim, a frase de 18/11"): o pacote que não bate com a assinatura, no "Reiniciar agora", mostra a frase 2
  da D-778, não a frase com motivo da D-845. Pela ponte da tela de verdade.
- D-851 ("5 — não: a última versão boa deve ser guardada copiando o pacote que já está na pasta packages\\ do programa
  [...] sem internet; baixar só se o arquivo não estiver lá. O agente confere isso, não supõe."): a guarda copia de
  `packages\\` sem internet; só baixa se o pacote não estiver lá. Conferido de verdade
  (`relatorios/atualizador-novo/volta3-provas/prova_packages-resultado.txt`): depois de cada troca ele está lá; depois
  do .msi, NÃO está (o nosso .msi não tem arquivo em `packages\\`). Volta 4: a D-857 mudou a D-851 ("sem baixar 460 MB na
  primeira abertura"); sem o pacote lá, nada é baixado (tests/test_atualizador_volta4.py).

Só a borda é de mentira (`tests/ajudante_do_atualizador.py`).
"""

from __future__ import annotations

import pytest

import assinatura
import atualizacao
from core import fases_da_atualizacao as fases
from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, NOVA, OUTRA_CHAVE, PACOTE, Prova, _ate_o_aviso,  # noqa: F401
                                          _estado, _publicar, _registro, programdata_de_prova)

FRASE_2 = ("Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O programa "
           "continua funcionando. Avise o Samuel.")


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado, o registro e as frases vistas numa pasta de prova."""


def _ponte(p: Prova, respostas: list[bool], avisos: list):
    """A ponte da tela de verdade, com as caixas de mentira (cada caixa vira uma linha em `avisos`)."""
    from PySide6.QtWidgets import QApplication, QWidget

    from ui import aviso_de_atualizacao as aviso

    QApplication.instance() or QApplication([])
    pai = QWidget()
    ponte = aviso.PonteDaTela(pai, p.atual, perguntar=lambda j, t, x, sim, nao: avisos.append((t, x)) or respostas.pop(0),
                              avisar=lambda j, t, x, icone=None: avisos.append((t, x)))
    pai._ponte_da_atualizacao = ponte
    return ponte, pai


# ---------------------------------------------------------------------------------------------------------------------
# D-848: o pacote sem a assinatura certa no "Reiniciar agora"
# ---------------------------------------------------------------------------------------------------------------------

def test_d848_reiniciar_agora_com_o_pacote_trocado_mostra_a_frase_2(tmp_path):
    """D-848 (Samuel, 24/11/2026: "2 — sim, a frase de 18/11."): o pacote baixado foi trocado depois de conferido (a
    soma não é a que a assinatura do Samuel afirma); "Reiniciar agora" mostra, com o título "Atualização", a frase 2 da
    D-778, nunca a do "Não deu para atualizar agora", e nada é trocado."""
    p = Prova(tmp_path)
    p.abrir()
    (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(b"trocado por outra conta")
    avisos: list = []
    ponte, _ = _ponte(p, [True], avisos)
    p.atual.ligar_a_tela(ponte.receber)
    assert avisos[1:] == [("Atualização", FRASE_2)]
    assert not any("Não deu para atualizar agora" in x for _, x in avisos)
    assert "trocar" not in p.vp.nomes()


def test_d848_trocado_nos_segundos_do_fechar_a_reabertura_mostra_a_frase_2(tmp_path):
    """D-848, o outro caminho: o pacote é trocado nos segundos em que a janela fecha (a segunda conferência acha); o
    programa reaberto mostra a frase 2 (guardada no bilhete), não a do "Não deu para atualizar agora"."""
    p = _ate_o_aviso(tmp_path)

    def tela(ef):
        if isinstance(ef, fases.FecharJanela):
            (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(b"trocado")
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert len(p.win.reaberturas) == 1 and _estado()["frase"]["tipo"] == fases.FALHA_RECUSADA
    assert atualizacao.frase_da_falha(_estado()["frase"]["tipo"], _estado()["frase"]["motivo"]) == FRASE_2


# ---------------------------------------------------------------------------------------------------------------------
# D-851: a última boa copiada de packages, sem internet; baixada só se não estiver lá
# ---------------------------------------------------------------------------------------------------------------------

def _sem_internet(p: Prova, tmp_path) -> None:
    """A fonte das versões fora do ar (como sem internet)."""
    p.atual.fonte = atualizacao.Fonte(str(tmp_path / "sem-internet"))


def test_d851_com_o_pacote_em_packages_guarda_sem_internet_e_sem_baixar(tmp_path):
    """D-851: depois de uma troca (o pacote da versão que roda está em `packages`, e a assinatura dela foi guardada
    quando ela foi conferida), a versão que passa no teste vira a última boa SEM internet e sem baixar nada."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, ATUAL)
    (atualizacao.pasta_da_ultima_boa(p.raiz) / nome).write_bytes((p.fonte_pasta / nome).read_bytes())
    _sem_internet(p, tmp_path)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert atualizacao.ler_ultima_boa(p.raiz) == ATUAL
    assert "baixar" not in p.vp.nomes()


# Volta 4 (D-857, lista da D-836): os três testes do "baixar só se o arquivo não estiver lá" saíram junto com o
# download (a D-851 foi mudada pela D-857: sem baixar nada); o que vale hoje está em tests/test_atualizador_volta4.py.
