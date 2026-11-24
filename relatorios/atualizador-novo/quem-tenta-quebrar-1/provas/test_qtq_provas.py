"""Provas de quem tenta quebrar o atualizador novo (24/11/2026). Nao fazem parte da suite do programa.

Cada prova usa o executor de verdade (atualizacao.Atualizacao), a regra de verdade (core/fases_da_atualizacao.py) e o
estado.json de verdade numa pasta de prova, com as mesmas pecas de mentira SO NA BORDA que os testes do implementador
usam (tests/ajudante_do_atualizador.py). Nada roda no Windows de verdade.

Cada prova PASSA quando o defeito acontece (ela mostra o defeito). Rodar com o PYTHONPATH na raiz do worktree:
    set PYTHONPATH=<worktree>
    python -m pytest <esta pasta>\\test_qtq_provas.py -q -p no:cacheprovider --basetemp=<pasta no D:>
"""

from __future__ import annotations

import pytest

import atualizacao
import versao
from core import fases_da_atualizacao as fases
from tests.ajudante_do_atualizador import ANTERIOR, NOVA, Prova, _ate_o_aviso, _estado


@pytest.fixture(autouse=True)
def _pastas_de_prova(tmp_path, monkeypatch):
    """O ProgramData e a pasta de dados da conta numa pasta de prova (este arquivo esta fora de tests/, entao o
    conftest de la nao vale aqui: sem isto, os avisos vistos iriam para a pasta de dados de verdade)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    monkeypatch.setenv("USERNAME", "Kaique")


def _abrir_como(tmp_path, nome, versao_que_roda, monkeypatch, *argumentos, **kw):
    """Uma abertura do programa (um processo) que roda a versao `versao_que_roda`."""
    monkeypatch.setattr(versao, "VERSAO", versao_que_roda)
    p = Prova(tmp_path / nome, publicar_nova=False, **kw)
    saida = p.abrir(*argumentos)
    p.ligar_a_tela()
    return p, saida


def test_A_abrir_pelo_atalho_no_meio_da_troca_anota_uma_falha_que_nao_houve(tmp_path, monkeypatch):
    """Achado grave 1. O Kaique escolhe "Sim" ao fechar (ou "Reiniciar agora"). O programa anota "tentando 1 -> 2" e
    pede a troca ao Velopack. Enquanto o Velopack espera o programa sair e abre o pacote (antes de renomear a pasta),
    o Kaique clica no atalho: abre a versao 1 de novo (o atalho do Velopack so abre current\\, sem esperar a troca).
    Essa abertura le "tentando", ve que roda a 1 e anota FALHA "troca", com a 2 em "nao tentar". O Velopack fecha essa
    janela a forca, troca e reabre a 2, que passa no teste. Na abertura seguinte, a tela mostra a frase de falha
    ("A atualizacao nao deu certo. O programa voltou para a versao anterior..."), com o programa ja na versao nova."""
    de, para = "1.1.0", "1.1.2"
    # processo 1 (versao 1.1.0): a troca foi pedida (o que trocar_para grava antes de chamar o Velopack)
    monkeypatch.setattr(versao, "VERSAO", de)
    atualizacao.anotar_tentativa(de, para, False)
    # processo 2: o clique no atalho no meio da troca (versao 1.1.0 ainda em current\, sem argumentos)
    p2, _ = _abrir_como(tmp_path, "p2", de, monkeypatch)
    assert _estado()["falha"]["tipo"] == fases.FALHA_TROCA
    assert para in _estado()["nao_tentar"]
    # processo 3: o Velopack trocou e reabriu a 1.1.2 com --conferir-a-versao-nova 1.1.0 1.1.2; o teste rapido passa
    p3, _ = _abrir_como(tmp_path, "p3", para, monkeypatch, atualizacao.ARG_CONFERIR_NOVA, de, para)
    assert "tentando" not in _estado()
    assert _estado()["falha"]["tipo"] == fases.FALHA_TROCA      # a falha falsa continua anotada
    # processo 4: a abertura seguinte do Kaique, ja na 1.1.2
    p4, _ = _abrir_como(tmp_path, "p4", para, monkeypatch)
    falhas_p2 = [e.tipo for e in p2.tela if isinstance(e, fases.MostrarFalha)]
    falhas_p4 = [e.tipo for e in p4.tela if isinstance(e, fases.MostrarFalha)]
    # a frase aparece numa das duas: na janela que o Velopack fecha a forca (p2) ou, se ela nao chegou a mostrar,
    # na abertura seguinte (p4). Nas duas, a falha nao aconteceu.
    assert falhas_p2 == [fases.FALHA_TROCA]
    print("frase mostrada:", atualizacao.FRASES_DA_FALHA[falhas_p2[0]])
    print("na abertura seguinte (ja vista na p2):", falhas_p4)


def test_A2_se_a_janela_fechada_a_forca_nao_chegou_a_mostrar_a_frase_vem_na_abertura_seguinte(tmp_path, monkeypatch):
    """O mesmo achado, quando o Velopack fecha a segunda abertura antes de a janela dela abrir (o mais comum: a frase
    so vai para a tela quando a janela liga): a frase falsa aparece na abertura seguinte, ja na versao nova."""
    de, para = "1.1.0", "1.1.2"
    monkeypatch.setattr(versao, "VERSAO", de)
    atualizacao.anotar_tentativa(de, para, False)
    monkeypatch.setattr(versao, "VERSAO", de)
    p2 = Prova(tmp_path / "p2", publicar_nova=False)
    p2.abrir()                       # a janela dela nunca liga: o Velopack a fecha a forca antes
    _abrir_como(tmp_path, "p3", para, monkeypatch, atualizacao.ARG_CONFERIR_NOVA, de, para)
    p4, _ = _abrir_como(tmp_path, "p4", para, monkeypatch)
    assert [e.tipo for e in p4.tela if isinstance(e, fases.MostrarFalha)] == [fases.FALHA_TROCA]
    assert versao.VERSAO == para     # e o programa ja esta na versao nova


def test_B_reiniciar_agora_com_a_troca_recusada_fecha_o_programa_e_nada_reabre(tmp_path):
    """Achado medio 2. "Reiniciar agora" fecha a janela PRIMEIRO e so depois confere se pode trocar (outra janela
    aberta, o motor, a soma do pacote). Se nao pode, a regra vai para PARADO com uma linha no registro: o programa ja
    fechou e nada o reabre, e nada na tela diz o que houve."""
    p = _ate_o_aviso(tmp_path, outras=[(7, "C:\\Program Files\\EditorImpressaoPrograma\\current\\EditorImpressao.exe")])
    depois_de_fechar = []
    fechou = []

    def tela(ef):
        if fechou:
            depois_de_fechar.append(type(ef).__name__)
        if isinstance(ef, fases.FecharJanela):
            fechou.append(True)
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert fechou == [True]
    assert "trocar" not in p.vp.nomes()
    assert p.atual.estado.fase is fases.Fase.PARADO
    assert depois_de_fechar == []        # nenhum aviso, nada reabre
    assert p.atual.saida is None


def test_C_a_volta_e_recusada_pelo_motor_da_versao_que_falhou(tmp_path):
    """Achado medio 3. A versao nova nao passa no teste rapido porque o motor DELA nao esta no lugar (uma versao que
    pede outro motor). A volta para a anterior passa pela troca unica, que confere o motor DESTA versao (a que falhou)
    e recusa: a volta nao acontece e a tela diz a frase 3 ("nao conseguiu voltar sozinho. Nao desinstale nada"), com o
    motor da anterior inteiro no lugar."""
    p = Prova(tmp_path, teste=(False, "falta o motor do Kraken"), motor=False)
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, versao.VERSAO)
    p.ligar_a_tela()
    assert "baixar" in p.vp.nomes()          # baixou a anterior assinada...
    assert "trocar" not in p.vp.nomes()      # ...e nao pediu a troca de volta
    assert _estado()["falha"]["tipo"] == fases.FALHA_VOLTA
    assert "motor" in _estado()["falha"]["motivo"]
    assert saida is None                     # a versao que falhou abre a janela
    assert [e.tipo for e in p.tela if isinstance(e, fases.MostrarFalha)] == [fases.FALHA_VOLTA]


def test_D_a_falha_da_troca_usa_a_frase_de_que_voltou(tmp_path):
    """Leve: quando o Velopack nao troca (arquivo preso), o programa nunca saiu da versao de antes, e a tela diz "O
    programa voltou para a versao anterior". A D-778 tem tres frases; a escolha da (1) para esse caso e do agente."""
    assert atualizacao.FRASES_DA_FALHA[fases.FALHA_TROCA] == atualizacao.FRASE_DA_FALHA
    assert "voltou para a versão anterior" in atualizacao.FRASE_DA_FALHA


def test_E_a_regra_pura_reiniciar_com_troca_recusada_nao_tem_efeito_de_tela(tmp_path):
    """A mesma coisa do achado 2, so na regra: depois de FECHANDO -> JanelaFechou(True) -> TrocaPedida(False) nao ha
    efeito nenhum alem do registro."""
    e = fases.Estado(fase=fases.Fase.TROCANDO, versao="1.1.0", nova="1.1.2")
    novo, efeitos = fases.proxima_fase(e, fases.TrocaPedida(False, "há outra janela do programa aberta"))
    assert novo.fase is fases.Fase.PARADO
    assert [type(x).__name__ for x in efeitos] == ["Registrar"]


def test_F_se_o_estado_nao_grava_a_versao_quebrada_volta_a_ser_baixada_e_o_aviso_some(tmp_path, monkeypatch):
    """Achado medio 4. `trocar_para` ignora o que `anotar_tentativa` devolve (atualizacao.py, linha da chamada), e
    `anotar_falha` ignora o que `gravar_estado` devolve. Se o estado.json nao aceita gravacao pela conta do Kaique (ex.:
    o arquivo nasceu de um processo com licenca, como o programa aberto no fim do .msi), a troca e pedida mesmo assim e
    a falha nao fica anotada: a versao que falhou volta a ser procurada, baixada e anunciada na abertura seguinte, e a
    frase da falha nunca aparece."""
    monkeypatch.setattr(atualizacao, "gravar_estado", lambda estado: False)   # o disco nao aceita (sem licenca)
    # processo 1: o Velopack reabriu a versao nova; o teste rapido falha; a volta para a anterior e pedida
    monkeypatch.setattr(versao, "VERSAO", NOVA)
    p1 = Prova(tmp_path / "p1", teste=(False, "codigo 1"))
    assert p1.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, NOVA) == 0
    assert "trocar" in p1.vp.nomes()                 # a troca de volta foi pedida sem a anotacao gravada
    # processo 2: a anterior reaberta pelo Velopack (sem argumentos na volta)
    monkeypatch.setattr(versao, "VERSAO", ANTERIOR)
    p2 = Prova(tmp_path / "p2")
    p2.abrir()
    p2.ligar_a_tela()
    assert p2.vp.nomes() == ["procurar", "baixar"]   # a versao que acabou de falhar e baixada de novo
    assert p2.tipos_na_tela() == ["MostrarVersaoNova"]   # e anunciada; a frase da falha nao aparece
