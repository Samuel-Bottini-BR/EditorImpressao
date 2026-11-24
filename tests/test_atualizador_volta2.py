"""Volta 2 do atualizador novo (24/11/2026): cada achado de quem tentou quebrar
(`relatorios/atualizador-novo/quem-tenta-quebrar-1/relatorio.md`) vira um teste que cobra o comportamento CERTO.

As provas dele (`provas/test_qtq_provas.py`, test_A a test_F) passavam mostrando o defeito; aqui cada uma cobra o
contrário, e falha no código de antes (`cd4b8414`): conferido trocando os arquivos do programa pelos de `cd4b8414` e
rodando este arquivo (o resultado está no ONDE-PAREI, volta 2). As peças de mentira só na borda
(`tests/ajudante_do_atualizador.py`); o resto é o de verdade. As mutações que sobreviveram (Q1-Q5, Q7, Q8, Q14, Q15)
ganham cada uma o seu teste aqui; os do motor vêm do conserto 4 do `atualizador-4` (`tests/test_atualizador_4.py`),
pelo caminho novo.
"""

from __future__ import annotations

import sys
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest

import atualizacao
import versao
from core import fases_da_atualizacao as fases
from core import windows
from tests.ajudante_do_atualizador import (ANTERIOR, NOVA, Prova, _ate_o_aviso, _estado, _registro,  # noqa: F401
                                          programdata_de_prova)

no_windows = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado e o registro numa pasta de prova."""


def _abrir_como(tmp_path, nome, versao_que_roda, monkeypatch, *argumentos, **kw):
    """Uma abertura (um processo) que roda `versao_que_roda`."""
    monkeypatch.setattr(versao, "VERSAO", versao_que_roda)
    p = Prova(tmp_path / nome, publicar_nova=False, **kw)
    saida = p.abrir(*argumentos)
    p.ligar_a_tela()
    return p, saida


# ---------------------------------------------------------------------------------------------------------------------
# G1: abrir pelo atalho no meio da troca
# ---------------------------------------------------------------------------------------------------------------------

def test_g1_abrir_pelo_atalho_no_meio_da_troca_nao_anota_falha_e_sai_sem_janela(tmp_path, monkeypatch):
    """Achado grave 1 da volta 1 (era `test_A` de quem tentou quebrar). D-828 (1): "abrir o programa pelo atalho no
    meio da troca não estraga a troca"; D-770: "em vez de o programa ser fechado à força e acusar uma falha que não
    houve". Volta 3 (D-836: adaptado ao desenho novo, sem a anotação da troca): com uma versão baixada esperando (o
    Velopack diz) e o atualizador do Velopack rodando, a abertura pelo atalho não anota nada e sai sem janela."""
    de, para = "1.1.0", "1.1.2"
    p2, saida = _abrir_como(tmp_path, "p2", de, monkeypatch, troca_em_curso=True, ultima_boa=de, pendente=para)
    assert saida == 0 and p2.tela == []
    assert _estado() == {}, "nada anotado"
    assert p2.win.perguntas_do_atualizador == [p2.raiz]


def test_g1_sem_saber_se_a_troca_acontece_nada_e_anotado(tmp_path, monkeypatch):
    """Achado grave 1 (era `test_A2`): sem saber se o atualizador do Velopack roda (o Windows não deu a lista), nada é
    anotado; a abertura segue (com janela). Volta 3 (D-836): sem a anotação da troca, o "nada anotado" é o bilhete
    vazio."""
    de, para = "1.1.0", "1.1.2"
    p2, saida = _abrir_como(tmp_path, "p2", de, monkeypatch, troca_em_curso=None, ultima_boa=de, pendente=para)
    assert saida is None and _estado() == {}
    assert "não deu para saber se a troca está acontecendo" in _registro()


def test_g1_a_troca_que_acabou_sem_trocar_nao_e_falha_e_a_reabertura_nao_pergunta(tmp_path, monkeypatch):
    """O outro lado do G1. Volta 3 (D-836: era "a troca que acabou sem trocar continua sendo falha"; a emenda do Fable
    e o M1 do segundo "quem tenta quebrar" mudaram isso: "troca que não aconteceu não é falha de versão: o pacote
    continua em packages, o aviso volta"): com o atualizador parado e o pacote esperando, a abertura é a comum (nada
    em "não tentar"); e a reabertura do Velopack, que vem com a linha de comando, nem pergunta se ele roda (ele pode
    ainda estar saindo: apply.rs 47-75)."""
    de, para = "1.1.0", "1.1.2"
    p2, saida = _abrir_como(tmp_path, "p2", de, monkeypatch, troca_em_curso=False, ultima_boa=de, pendente=para)
    assert saida is None and "reprovadas" not in _estado() and p2.atual.estado.fase is not fases.Fase.CONFERINDO_NOVA
    p3, _ = _abrir_como(tmp_path, "p3", de, monkeypatch, atualizacao.ARG_CONFERIR_NOVA, de, para, troca_em_curso=True,
                        ultima_boa=de, pendente=para)
    assert p3.win.perguntas_do_atualizador == [], "a reabertura do Velopack não consulta a troca em curso"
    assert [e.tipo for e in p3.tela if isinstance(e, fases.MostrarFalha)] == [fases.FALHA_TROCA]     # a D-839


@no_windows
def test_g1_a_peca_ve_o_atualizador_do_velopack_pelo_caminho_dele(tmp_path):
    """A peça responde "não roda" numa instalação de prova sem o atualizador rodando (só lê a lista do Windows)."""
    assert windows.atualizador_do_velopack_rodando(tmp_path) is False


# ---------------------------------------------------------------------------------------------------------------------
# M1: "Reiniciar agora" confere antes de fechar; o que falha depois reabre o programa
# ---------------------------------------------------------------------------------------------------------------------

def test_m1_reiniciar_agora_que_nao_pode_trocar_nao_fecha_a_janela(tmp_path):
    """Achado médio 1 (era `test_B` e `test_E`). Com outra janela do programa aberta, "Reiniciar agora" NÃO fecha a
    janela (a conferência é antes de fechar): nada trocado, a janela continua aberta e, ao fechar, a pergunta
    "Atualizar agora?" vem como no "Depois"."""
    p = _ate_o_aviso(tmp_path, outras=[(7, "C:\\Program Files\\EditorImpressaoPrograma\\current\\EditorImpressao.exe")])
    vistos = []

    def tela(ef):
        vistos.append(type(ef).__name__)
        if isinstance(ef, fases.FecharJanela):
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert "FecharJanela" not in vistos and "trocar" not in p.vp.nomes()
    # D-841 (Samuel, 24/11/2026: "1, desde que seja a volta à fase 'pronta'"): com outra janela aberta, a regra volta a
    # PRONTA (o aviso aparece de novo); antes desta decisão era DEPOIS. Ao fechar, a pergunta vem igual nas duas.
    assert p.atual.estado.fase is fases.Fase.PRONTA
    p.atual.evento(fases.Fechando())
    assert vistos[-1] == "PerguntarAoFechar"


def test_m1_a_troca_que_falha_depois_de_fechar_reabre_o_programa(tmp_path):
    """Achado médio 1, o que só falha depois de fechar (o Velopack não aceitou o pedido): o programa é aberto de novo,
    pela peça do Windows, com o sinal de vida; nunca some calado."""
    p = _ate_o_aviso(tmp_path)

    def recusa(*a):
        raise RuntimeError("o atualizador do Velopack não abriu")

    p.vp.trocar = recusa
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    assert len(p.win.reaberturas) == 1 and atualizacao.ARG_SINAL_DE_VIDA in p.win.reaberturas[0]
    assert "tentando" not in _estado()


def test_m1_o_sinal_de_vida_e_dado_antes_de_tudo(tmp_path):
    """O programa reaberto cria o arquivo do sinal logo ao começar (é o que a peça espera para dar o "abrir de novo"
    como feito), e o resto da linha de comando segue (pelo código: abre normalmente)."""
    sinal = tmp_path / "sinal"
    assert atualizacao.atender_linha_de_comando(["main.py", atualizacao.ARG_SINAL_DE_VIDA, str(sinal)]) is None
    assert sinal.exists()


# ---------------------------------------------------------------------------------------------------------------------
# M2: o motor da versão que entra
# ---------------------------------------------------------------------------------------------------------------------

def test_m2_a_volta_confere_o_motor_da_anterior_e_volta(tmp_path, monkeypatch):
    """Achado médio 2 (era `test_C`). D-833: "a versão nova só é anunciada com o motor DELA no lugar"; D-790: "a volta
    para a versão anterior acha o motor antigo na pasta dele". A versão nova pede o motor 2 (fora do lugar) e falha no
    teste rápido; a anterior pede o motor 1, que está no lugar: a volta acontece."""
    monkeypatch.setattr(versao, "VERSAO", NOVA)
    p = Prova(tmp_path, teste=(False, "falta o motor do Kraken"), motores={NOVA: 2, ANTERIOR: 1},
              motores_no_lugar={1}, ultima_boa=ANTERIOR)
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, NOVA)
    assert saida == 0 and p.vp.chamadas[-1][:2] == ("trocar", ANTERIOR)
    assert _estado()["reprovadas"] == [NOVA]          # volta 3 (D-836): a reprovação, no lugar da falha anotada


def test_m2_a_versao_nova_sem_o_motor_dela_nao_e_anunciada(tmp_path):
    """D-833: a versão nova que pede o motor 2 (fora do lugar) é baixada (é o download que diz o motor), mas não é
    anunciada nem trocada; com o motor 2 no lugar, é. Volta 3 (D-843, D-836): no lugar do aviso, a frase "Esta versão
    precisa de um motor novo. Avise o Samuel." (uma vez)."""
    p = Prova(tmp_path / "a", motores={NOVA: 2}, motores_no_lugar={1})
    p.abrir()
    p.ligar_a_tela()
    assert [(type(e).__name__, getattr(e, "tipo", "")) for e in p.tela] == [("MostrarFalha", fases.FALHA_MOTOR)]
    assert "trocar" not in p.vp.nomes()
    q = Prova(tmp_path / "b", motores={NOVA: 2}, motores_no_lugar={1, 2})
    q.abrir()
    q.ligar_a_tela()
    assert q.tipos_na_tela() == ["MostrarVersaoNova"]


def test_m2_o_motor_exigido_e_lido_de_dentro_do_pacote(tmp_path):
    """O `motor-exigido.json` de dentro do pacote (o lugar onde o publicar o põe) diz o motor; sem ele, ou com o pacote
    estragado, não se sabe (None, e a troca não acontece)."""
    import empacotar
    from tests.ajudante_do_atualizador import pacote_de_prova

    assert atualizacao.CAMINHO_DO_MOTOR_EXIGIDO_NO_PACOTE == empacotar.PASTA_NO_NUPKG + empacotar.NOME_DO_MOTOR_EXIGIDO
    arquivo = tmp_path / "p.nupkg"
    arquivo.write_bytes(pacote_de_prova("x", 3))
    assert atualizacao.motor_exigido_pelo_pacote(arquivo) == 3
    arquivo.write_bytes(pacote_de_prova("x", None))
    assert atualizacao.motor_exigido_pelo_pacote(arquivo) is None
    arquivo.write_bytes(b"nao e zip")
    assert atualizacao.motor_exigido_pelo_pacote(arquivo) is None


# ---------------------------------------------------------------------------------------------------------------------
# M4: o estado que não grava
# ---------------------------------------------------------------------------------------------------------------------

def test_m4_com_o_estado_que_nao_grava_a_atualizacao_continua_e_o_registro_diz(tmp_path, monkeypatch):
    """Achado médio 4. Volta 3 (D-836: era "nada é procurado nem trocado"; a emenda do Fable mudou: "Se não puder ser
    gravado, o programa continua atualizando e registra o motivo; nunca para calado"): com o estado.json recusando
    gravação, a versão nova é procurada e anunciada, a volta acontece, e o registro diz que a reprovação não ficou
    gravada. Nada da troca depende do bilhete."""
    monkeypatch.setattr(atualizacao, "gravar_estado", lambda estado: False)
    p = Prova(tmp_path / "a")
    p.abrir()
    assert p.vp.nomes() == ["procurar", "baixar"]
    monkeypatch.setattr(versao, "VERSAO", NOVA)
    q = Prova(tmp_path / "b", teste=(False, "código 1"), ultima_boa=ANTERIOR)
    assert q.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, NOVA) == 0
    assert "trocar" in q.vp.nomes(), "a volta é pedida mesmo sem o bilhete gravar"
    assert "NÃO ficou gravada" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# M3: as proteções sem teste (Q1-Q5, Q7, Q8, Q14, Q15) e os testes do motor do conserto 4
# ---------------------------------------------------------------------------------------------------------------------

def _instalacao_com_o_motor_no_instalador(tmp_path: Path) -> tuple[Path, Path]:
    """Uma instalação de prova como o .msi deixa: <raiz>\\current\\instalar\\motor-kraken-<v>.zip (o motor de prova,
    com a ficha gravada pela função de verdade). Devolve (raiz, current). Do conserto 4 do `atualizador-4`."""
    from core import ocr_kraken
    from tests.test_publicar_motor import _motor

    motor = _motor(tmp_path / "motor-montado")
    raiz = tmp_path / "EditorImpressaoPrograma"
    current = raiz / "current"
    instalar = current / atualizacao.PASTA_DO_QUE_SE_INSTALA
    instalar.mkdir(parents=True)
    with zipfile.ZipFile(instalar / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR), "w") as z:
        for arquivo in motor.rglob("*"):
            if arquivo.is_file():
                z.write(arquivo, arquivo.relative_to(motor).as_posix())
    return raiz, current


def test_q3_conserto4_o_motor_do_instalador_vai_para_o_lugar_dele(tmp_path):
    """Q3 e o conserto 4 (D-788, D-833): `garantir_o_motor` põe o motor em <raiz>\\motor-kraken\\1, conferido; a
    segunda vez não refaz nada."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current) is True
    destino = ocr_kraken.pasta_do_motor_instalado(raiz)
    assert destino == raiz / "motor-kraken" / "1" and ocr_kraken.conferir_motor(destino) == []
    assert not (raiz / "motor-kraken" / ".chegando-1").exists()
    antes = (destino / ocr_kraken.NOME_DA_FICHA).stat().st_mtime_ns
    assert atualizacao.garantir_o_motor(raiz, current) is True
    assert (destino / ocr_kraken.NOME_DA_FICHA).stat().st_mtime_ns == antes


def test_q1_conserto4_sem_espaco_nao_comeca(tmp_path):
    """Q1: sem o espaço do motor aberto mais a folga, não começa, e nada fica."""
    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current, livre=lambda p: 10) is False
    assert not (raiz / "motor-kraken" / "1").exists() and not (raiz / "motor-kraken" / ".chegando-1").exists()
    assert "falta espaço" in _registro()


def test_q2_conserto4_motor_estragado_nunca_fica_com_o_nome_final(tmp_path):
    """Q2: um arquivo do motor que não confere (um arquivo da ficha faltando) é recusado: o nome final nunca aparece
    pela metade e a pasta provisória some."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    arquivo = current / atualizacao.PASTA_DO_QUE_SE_INSTALA / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    with zipfile.ZipFile(arquivo) as z:
        nomes = [n for n in z.namelist() if not n.endswith("/")]
        conteudo = {n: z.read(n) for n in nomes[:-1]}
    with zipfile.ZipFile(arquivo, "w") as z:
        for nome, dados in conteudo.items():
            z.writestr(nome, dados)
    assert atualizacao.garantir_o_motor(raiz, current) is False
    assert not (raiz / "motor-kraken" / "1").exists() and not (raiz / "motor-kraken" / ".chegando-1").exists()


def test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador(tmp_path):
    """Conserto 4: um motor no nome final que não confere é posto de lado e o do instalador entra."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.garantir_o_motor(raiz, current)
    destino = ocr_kraken.pasta_do_motor_instalado(raiz)
    (destino / "python" / "python.exe").write_bytes(b"x")
    assert ocr_kraken.conferir_motor(destino)
    assert atualizacao.garantir_o_motor(raiz, current) is True and ocr_kraken.conferir_motor(destino) == []
    assert [p.name for p in (raiz / "motor-kraken").iterdir()] == ["1"]


def test_conserto4_sem_o_arquivo_e_sem_o_motor_diz_e_nao_finge(tmp_path):
    """Conserto 4: sem o motor no lugar e sem o arquivo do instalador, False e registro (nunca "deu certo")."""
    raiz = tmp_path / "EditorImpressaoPrograma"
    (raiz / "current").mkdir(parents=True)
    assert atualizacao.garantir_o_motor(raiz, raiz / "current") is False
    assert "motor do Kraken: não está" in _registro()


def test_q4_conserto4_o_motor_no_lugar_e_a_mesma_conferencia(tmp_path):
    """Q4 (D-833): `motor_esta_no_lugar` lê a pasta única e a conferência única do motor, da versão de motor pedida;
    pelo código é sempre True."""
    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    assert atualizacao.motor_esta_no_lugar(raiz) is False
    atualizacao.garantir_o_motor(raiz, current)
    assert atualizacao.motor_esta_no_lugar(raiz) is True
    assert atualizacao.motor_esta_no_lugar(raiz, 2) is False, "o motor 2 não está: a pergunta é por versão de motor"
    assert atualizacao.motor_esta_no_lugar() is True, "pelo código"


@pytest.mark.parametrize("estrago", ["fluxo invalido", "cortado"])
def test_volta2_medio1_conserto4_arquivo_do_motor_estragado_de_qualquer_jeito(tmp_path, estrago):
    """Conserto 4, médio 1 do relatório 1 do `atualizador-4`: o arquivo do motor estragado de qualquer jeito (um bloco
    inválido, ou cortado) é apagado e registrado; o provisório nunca sobra."""
    from core import ocr_kraken

    raiz, current = _instalacao_com_o_motor_no_instalador(tmp_path)
    arquivo = current / atualizacao.PASTA_DO_QUE_SE_INSTALA / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    with zipfile.ZipFile(arquivo) as z:
        conteudo = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(arquivo, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in conteudo.items():
            z.writestr(nome, dados)
    with zipfile.ZipFile(arquivo) as z:
        info = max(z.infolist(), key=lambda i: i.compress_size)
    dados = bytearray(arquivo.read_bytes())
    comeco = info.header_offset + 30 + len(info.filename.encode("utf-8")) + len(info.extra)
    if estrago == "fluxo invalido":
        dados[comeco] = 0xFF
    else:
        dados[comeco + 1:comeco + info.compress_size] = b"\x00" * (info.compress_size - 1)
    arquivo.write_bytes(bytes(dados))
    assert atualizacao.garantir_o_motor(raiz, current) is False
    assert not (raiz / "motor-kraken" / ".chegando-1").exists() and not (raiz / "motor-kraken" / "1").exists()
    assert "motor do Kraken: não deu para pôr no lugar" in _registro()


@no_windows
def test_q5_a_pasta_que_existe_e_nao_aceita_gravacao_nao_conta_como_preparada():
    """Q5 (D-741, D-749): o "preparado?" é gravar de verdade, não ver se a pasta existe. A pasta do sistema existe e
    não aceita gravação pela conta comum. (Com a licença de administrador ligada ela aceitaria: pulado.)"""
    if windows.tem_licenca_de_administrador():
        pytest.skip("com a licença de administrador a pasta do sistema aceita gravação")
    assert atualizacao.pasta_aceita_gravacao(windows.pasta_do_sistema()) is False


@no_windows
def test_q7_a_licenca_tem_de_chegar_ao_arquivo_de_dentro(tmp_path, monkeypatch):
    """Q7 (D-837, §11.12 ponto 2): a raiz ganhou a licença, mas o manifesto de `current` não: o passo FALHA. (A
    ferramenta e as leituras do Windows trocadas por respostas de prova: só a regra em volta.)"""
    from tests.test_windows_preparo_do_computador import ANTES, DEPOIS_CERTO

    raiz = tmp_path / "raiz"
    (raiz / "current").mkdir(parents=True)
    (raiz / "current" / "sq.version").write_text("x", encoding="utf-8")
    leituras = iter([ANTES, DEPOIS_CERTO])
    monkeypatch.setattr(windows, "_rodar", lambda *a, **k: windows.Resposta(windows.DEU_CERTO))
    monkeypatch.setattr(windows, "ler_licencas", lambda c: next(leituras) if Path(c) == raiz else ANTES)
    r = windows.dar_licenca_aos_usuarios(raiz, raiz / "current" / "sq.version")    # volta 3: quem pede diz qual
    assert r.desfecho == windows.FALHOU and "sq.version" in r.motivo


@no_windows
def test_q8_o_visual_c_que_uma_conta_comum_pode_trocar_nao_roda(tmp_path, monkeypatch):
    """Q8: o instalador do Visual C++ que Usuários podem trocar NÃO é rodado com a licença de administrador."""
    from tests.test_windows_preparo_do_computador import DEPOIS_CERTO

    pasta = tmp_path / "current"
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA).mkdir(parents=True)
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ")
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setattr(windows, "ler_versao_do_visual_c", lambda: None)
    monkeypatch.setattr(windows, "ler_licencas", lambda c: replace(DEPOIS_CERTO, dono=windows.SID_SISTEMA))
    monkeypatch.setattr(windows, "_rodar", lambda *a, **k: pytest.fail("rodou o instalador que Usuários trocam"))
    assert windows.instalar_visual_c_do_programa(pasta).desfecho == windows.FALHOU


def test_q14_sem_a_lista_de_processos_nao_troca(tmp_path):
    """Q14: o Windows não deu a lista de processos: não dá para dizer que não há outra janela aberta, e não troca."""
    p = _ate_o_aviso(tmp_path)
    p.win.outras = None
    c = p.atual.conferencia_da_troca(p.atual._achada)            # volta 3: a conferência única, sem o embrulho
    assert c.pode is False and "não deu para saber" in c.motivo and c.motivo_da_tela == fases.MOTIVO_SEM_LISTA


@no_windows
def test_q15_o_processo_cujo_caminho_nao_da_para_ler_conta(tmp_path):
    """Q15: o processo do Windows cujo caminho não dá para ler (o "System") conta como de dentro quando o nome dele é
    um dos nomes pedidos (nunca se dá como fechado o que não deu para conferir)."""
    achados = windows.programas_rodando_de(tmp_path, nomes={"system"})
    assert any(pid == 4 and "não deu para ler" in caminho for pid, caminho in achados)


def test_leve3_a_familia_respeita_a_hora_em_que_cada_um_nasceu():
    """Leve 3: o Windows reaproveita números; um processo que nasceu ANTES do "pai" não é da família dele."""
    pais = {2: 1, 3: 1}
    assert windows.familia_de(1, pais, {1: 100, 2: 200, 3: 50}) == {1, 2}
    assert windows.familia_de(1, pais) == {1, 2, 3}


# ---------------------------------------------------------------------------------------------------------------------
# Leve 2: a licença que só acrescenta, mais estrita (a leitura de volta e o porteiro)
# ---------------------------------------------------------------------------------------------------------------------

@no_windows
def test_leve2_uma_licenca_a_mais_na_pasta_e_acusada():
    """D-837 ("só para acrescentar Usuários podem modificar"): qualquer linha nova além dessa (ex.: Todos com Controle
    total) faz o passo falhar; Usuários com Controle total também."""
    from tests.test_windows_preparo_do_computador import DEPOIS_CERTO, ANTES, L

    todos = replace(DEPOIS_CERTO, lista=DEPOIS_CERTO.lista + (L("S-1-1-0", 0x1F01FF, herdada=False),))
    assert any("não era para acrescentar" in p for p in windows.problemas_da_licenca_dos_usuarios(ANTES, todos))
    total = replace(ANTES, lista=ANTES.lista + (L(windows.SID_USUARIOS, 0x1F01FF, herdada=False),))
    assert any("não era para acrescentar" in p for p in windows.problemas_da_licenca_dos_usuarios(ANTES, total))


def _k03(arquivos):
    from regras_dos_agentes import porteiro

    achados = porteiro.conferir_codigo(arquivos, lambda c: arquivos.get(c))
    return [(a.arquivo, a.linha) for a in achados if a.conferencia == "K03"]


@pytest.mark.parametrize("arquivo, texto", [
    ("core/windows.py", 'def dar_licenca_aos_usuarios(raiz):\n    ferramenta = pasta_do_sistema() / "icacls.exe"\n'
                        '    return _rodar([ferramenta, raiz, "/grant", "*S-1-1-0:(OI)(CI)F", "/T"], 1800)\n'),
    ("core/windows.py", 'def outra(raiz):\n    return _rodar([pasta_do_sistema() / ("ica" + "cls.exe"), raiz, "/remove", '
                        '"*S-1-5-32-545"], 60)\n'),
    ("core/windows.py", 'FERRAMENTA = "ica" "cls.exe"\ndef outra(raiz):\n    return _rodar([pasta_do_sistema() / '
                        'FERRAMENTA, raiz, "/setown" "er", "*S-1-5-32-545"], 60)\n'),
    ("atualizacao.py", 'from core import windows\ndef liberar_o_windows():\n    return windows.dar_licenca_aos_usuarios('
                       'Path("C:/Windows"))\n'),
])
def test_leve2_o_porteiro_acusa_o_que_a_d837_nao_deixa(arquivo, texto):
    """Leve 2 (a prova `prova_porteiro_k03.py` de quem tentou quebrar): Todos com Controle total na função da exceção;
    a ferramenta escrita em pedaços em outra função (tirando licença ou trocando o dono); e a função da exceção chamada
    de fora dos passos da peça. Todos acusados pela K03."""
    assert _k03({arquivo: '"""Exemplo."""\n' + texto})


# ---------------------------------------------------------------------------------------------------------------------
# A frase da falha "troca" (leve 1): pergunta ao Samuel; até lá, a de hoje
# ---------------------------------------------------------------------------------------------------------------------

def test_leve1_a_frase_da_troca_espera_a_resposta_do_samuel():
    """Leve 1 (era `test_D`): a D-778 não tinha frase para "a troca não aconteceu e o programa continua na versão de
    antes". Até a resposta do Samuel, este teste cobrava a frase (1), para a mudança não entrar calada. Ele respondeu
    (D-839, chat 24/11/2026: "sim"): a frase nova entra aqui, palavra por palavra, e a (1) fica para a versão que entrou
    e voltou. A prova pelo caminho inteiro (a regra, o executor e a ponte da tela) é
    `test_decisoes_atualizacao::test_d839_*`."""
    assert atualizacao.FRASES_DA_FALHA[fases.FALHA_TROCA] == (
        "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel.")
    assert atualizacao.FRASES_DA_FALHA[fases.FALHA_TESTE] == atualizacao.FRASE_DA_FALHA


def test_os_comentarios_do_desfazer_nao_citam_o_que_saiu():
    """Leve 7 (§11.12: comentário "como X" se confere): os comentários dos testes à distância não citam mais funções do
    atualizador que saíram."""
    texto = (Path(__file__).resolve().parent.parent / "core" / "testes_a_distancia.py").read_text(encoding="utf-8")
    for saiu in ("preparar_como_administrador", "preparar_o_computador(", "criar_as_tarefas"):
        assert f"atualizacao.{saiu}" not in texto, saiu
