"""Volta 3 do atualizador novo (24/11/2026): a emenda do Fable ("a verdade vem do disco, não do bilhete"; "a volta é
instantânea e sem internet") e os achados do segundo "quem tenta quebrar"
(`relatorios/atualizador-novo/quem-tenta-quebrar-2/relatorio.md`).

Um teste por achado (G1, M1 a M9, L1 a L4). Cada um FALHA no código de `012c849c` (a saída lá está em
`relatorios/atualizador-novo/volta3-testes-no-codigo-antigo.txt`) e passa neste. Para que a falha lá seja pelo
comportamento, e não só por um nome que mudou, os testes usam o que os dois códigos têm (a `Prova` com os parâmetros de
antes, o executor, a regra), e montam a pasta da última boa À MÃO (o código antigo a ignora).

O que é de mentira (D-767): só a borda (a peça do Windows e a do Velopack, as de `tests/ajudante_do_atualizador.py`).
Os testes de verdade no Windows (o Velopack de verdade, o `icacls` numa pasta de prova, dois processos) estão em
`relatorios/atualizador-novo/volta3-provas/` e nos testes marcados `de_verdade` abaixo.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

import pytest

import assinatura
import atualizacao
import versao
from core import fases_da_atualizacao as fases
from core import windows
from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, NOVA, PACOTE, PUBLICA, Prova, VelopackFalso,  # noqa: F401
                                          _ate_o_aviso, _estado, _registro, pacote_de_prova, programdata_de_prova)

no_windows = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado e o registro numa pasta de prova."""


class Morreu(BaseException):
    """O processo morreu no meio (o notebook desligou): nada do programa pega isto (ele só pega `Exception`)."""


def _guardar_a_mao(p: Prova, v: str) -> Path:
    """Põe em `<raiz>\\ultima-boa` o pacote e a assinatura da versão `v`, como o código novo deixa ao guardar (o código
    antigo não olha esta pasta). Os nomes são os que o Velopack e o publicar usam."""
    pasta = p.raiz / "ultima-boa"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{PACOTE}-{v}-full.nupkg").write_bytes(p.vp.conteudo[v])
    nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, v)
    (pasta / nome).write_bytes((p.fonte_pasta / nome).read_bytes())
    return pasta


def _outra_abertura(p: Prova, *, teste=(True, ""), vp=None, por_tras=None) -> atualizacao.Atualizacao:
    """Outro processo do programa na MESMA instalação de prova (a mesma raiz, a mesma fonte, o mesmo ProgramData)."""
    return atualizacao.Atualizacao(
        windows=p.win, velopack=vp or VelopackFalso(p.raiz, p.vp.publicada, "", p.vp.conteudo),
        raiz=p.raiz, fonte=p.atual.fonte, por_tras=por_tras or (lambda trabalho: trabalho()),
        pasta_grava=lambda raiz: True, garantir_motor=lambda: True, motor_no_lugar=lambda m=None: True,
        teste=lambda: teste, chave_publica=PUBLICA)


def _na_tela(atual) -> list:
    """Liga uma tela de lista ao executor e devolve a lista."""
    tela: list = []
    atual.ligar_a_tela(tela.append)
    return tela


# ---------------------------------------------------------------------------------------------------------------------
# A guarda interrompida (os testes do G1, a volta interrompida e a frase 1, saíram com a volta na volta 5: D-871)
# ---------------------------------------------------------------------------------------------------------------------


def test_g_a_guarda_interrompida_nao_vira_ultima_boa(tmp_path, monkeypatch):
    """A guarda da última boa interrompida no meio da cópia (o notebook desligou): o pedaço copiado não vira a última
    boa (a cópia vai para um nome provisório e só ganha o nome final depois da soma conferida); a de antes continua."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)

    def copia_que_morre(origem, copiar_para=None):
        if copiar_para is None:
            return original(origem)
        Path(copiar_para).write_bytes(Path(origem).read_bytes()[:10])
        raise Morreu()

    original = assinatura.soma_sha256
    # volta 4 (leve 5, D-836): a cópia somada é a conta única da soma (`assinatura.soma_sha256(copiar_para=...)`)
    monkeypatch.setattr(assinatura, "soma_sha256", copia_que_morre)
    with pytest.raises(Morreu):
        atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA)
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR


# ---------------------------------------------------------------------------------------------------------------------
# M1: a troca interrompida virava "a atualização não deu certo" e a versão nunca mais era tentada
# ---------------------------------------------------------------------------------------------------------------------

def test_m1_a_troca_interrompida_nao_e_falha_e_o_aviso_volta(tmp_path):
    """M1 (24/11/2026): "Sim" ao fechar, a troca é pedida e o notebook desliga antes de o Velopack trocar. Antes: a
    abertura seguinte dizia "A atualização não deu certo..." e a versão ia para "não tentar" (nunca mais chegava).
    Agora: a troca que não aconteceu não é falha de versão: a abertura seguinte é a comum e o aviso da versão nova
    volta (D-769: "nada se perde e a troca tenta de novo depois")."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" in p.vp.nomes()                # pedida; o Velopack "morre" antes de trocar
    segunda = _outra_abertura(p)
    segunda.abrir([])
    tela = _na_tela(segunda)
    assert [type(e).__name__ for e in tela] == ["MostrarVersaoNova"]
    assert NOVA not in (_estado().get("nao_tentar") or []) and NOVA not in (_estado().get("reprovadas") or [])


# ---------------------------------------------------------------------------------------------------------------------
# M2: "Reiniciar agora" deixava a janela parada enquanto conferia o pacote
# ---------------------------------------------------------------------------------------------------------------------

def test_m2_a_conferencia_do_reiniciar_agora_roda_por_tras(tmp_path, monkeypatch):
    """M2 (24/11/2026): o clique em "Reiniciar agora" voltava só depois da soma do pacote inteiro (~460 MB, até 8 s no
    disco frio), no fio da tela: a janela ficava parada. Agora a conferência roda por trás (o fio que já existe) e o
    clique volta logo; a janela fecha quando ela termina. (CLAUDE.md §3: "Interface nunca congela.")"""
    p = _ate_o_aviso(tmp_path)
    liberar = threading.Event()
    original = assinatura.soma_sha256

    def soma_demorada(arquivo):
        liberar.wait(5)
        return original(arquivo)

    monkeypatch.setattr(assinatura, "soma_sha256", soma_demorada)
    p.atual._por_tras = atualizacao._por_tras      # o fio de trás de verdade
    tela = _na_tela(p.atual)
    comeco = time.monotonic()
    p.atual.evento(fases.Escolheu(True))
    demorou = time.monotonic() - comeco
    liberar.set()
    fim = time.monotonic() + 5
    while not any(isinstance(e, fases.FecharJanela) for e in tela) and time.monotonic() < fim:
        time.sleep(0.01)
    assert demorou < 1.0, f"o clique ficou {demorou:.1f} s parado na conferência"
    assert any(isinstance(e, fases.FecharJanela) for e in tela), "a janela fecha quando a conferência termina"


# ---------------------------------------------------------------------------------------------------------------------
# M3: "Reiniciar agora" que não podia trocar por outro motivo não respondia nada (D-845, D-846)
# ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("porque", ["sem_lista", "pacote_sumiu", "motor"])
def test_m3_o_reiniciar_agora_que_nao_pode_responde_com_o_motivo(tmp_path, porque):
    """M3 (24/11/2026): fora "outra janela aberta", todo "não pode trocar agora" ia para "Depois" sem nada na tela.
    Agora (D-845: "Não deu para atualizar agora: [motivo]. Tente ao fechar o programa."): a frase, com o motivo em
    português, e a pergunta vem ao fechar. (Os casos são nomeados por texto para o teste ser coletado também no código
    de antes, onde as chaves dos motivos não existem.)"""
    motivo = getattr(fases, {"sem_lista": "MOTIVO_SEM_LISTA", "pacote_sumiu": "MOTIVO_PACOTE_SUMIU",
                             "motor": "MOTIVO_MOTOR"}[porque], porque)
    p = _ate_o_aviso(tmp_path)
    if porque == "sem_lista":
        p.win.outras = None
    elif porque == "pacote_sumiu":
        (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").unlink()
    else:
        p.motor["no_lugar"] = False
    tela = _na_tela(p.atual)
    p.atual.evento(fases.Escolheu(True))
    falhas = [e for e in tela if isinstance(e, fases.MostrarFalha)]
    assert len(falhas) == 1 and falhas[0].tipo == fases.NAO_DEU_AGORA and falhas[0].motivo_da_tela == motivo
    assert atualizacao.frase_da_falha(falhas[0].tipo, falhas[0].motivo_da_tela) == (
        f"Não deu para atualizar agora: {atualizacao.MOTIVOS_DA_TELA[motivo]}. Tente ao fechar o programa.")
    assert p.atual.estado.fase is fases.Fase.DEPOIS


def test_m3_todo_motivo_tem_o_texto_e_nenhum_tem_codigo():
    """D-845 e §11.13 (nenhuma palavra de dentro na tela): toda chave de motivo da regra tem o texto em português; nenhum
    texto tem número de decisão nem nome de arquivo; a frase montada termina com o pedido da D-845."""
    assert set(atualizacao.MOTIVOS_DA_TELA) == set(fases.MOTIVOS)
    for chave, texto in atualizacao.MOTIVOS_DA_TELA.items():
        assert texto and texto == texto.strip() and not texto.endswith(".")
        assert "D-" not in texto and ".py" not in texto and "Velopack" not in texto and "Kraken" not in texto
        assert atualizacao.frase_da_falha(fases.NAO_DEU_AGORA, chave).endswith("Tente ao fechar o programa.") or \
            chave == fases.MOTIVO_OUTRA_JANELA


# ---------------------------------------------------------------------------------------------------------------------
# M4: o estado.json que não aceitava gravação parava a atualização para sempre, calada
# ---------------------------------------------------------------------------------------------------------------------

def test_m4_o_bilhete_que_nao_grava_nao_para_a_atualizacao(tmp_path, monkeypatch):
    """M4 (24/11/2026): com o `estado.json` nascido de uma abertura com licença de administrador, a conta comum não
    conseguia regravá-lo, e toda abertura dava "nenhuma versão é procurada", calada. Agora (a emenda do Fable): a
    atualização não depende do bilhete; ela continua (procura, anuncia) e o registro diz o que não gravou."""
    monkeypatch.setattr(atualizacao, "gravar_estado", lambda estado: False)
    p = Prova(tmp_path)
    p.abrir()
    p.ligar_a_tela()
    assert "procurar" in p.vp.nomes() and "MostrarVersaoNova" in p.tipos_na_tela()


@no_windows
def test_m4_a_pergunta_unica_da_a_licenca_tambem_a_pasta_do_registro(tmp_path, monkeypatch):
    """M4, a causa: a pasta do registro e do bilhete (`%ProgramData%\\EditorImpressao\\atualizacao`) ganha
    Usuários: Modificar NO MESMO PASSO da pergunta única, pela MESMA função da peça (`dar_licenca_aos_usuarios`), depois
    da raiz (é a raiz que decide o "preparado?"). Antes, só a raiz."""
    pedidas = []
    raiz = tmp_path / "raiz"
    (raiz / "current").mkdir(parents=True)
    monkeypatch.setattr(windows, "raiz_da_instalacao", lambda exe=None: raiz)
    monkeypatch.setattr(windows, "dar_licenca_aos_usuarios",
                        lambda pasta, conferir_dentro=None: pedidas.append((Path(pasta), conferir_dentro))
                        or windows.Resposta(windows.DEU_CERTO))
    monkeypatch.setattr(windows, "pasta_de_dados_comum", lambda: tmp_path / "ProgramDataDoWindows", raising=False)
    # O despachante dos passos é de dentro da peça e só roda no programa aberto com a licença de administrador (não há
    # porta pública para um passo sem ela). Este teste o chama de propósito, pelo nome, para ver as duas pastas; está
    # nas ressalvas da volta 3 (a regra "ninguém usa o que tem sublinhado" de test_windows_peca não olha o getattr).
    despachante = getattr(windows, "_fazer_passo")
    r = despachante({"tipo": "dar_licenca_aos_usuarios", "dados": {}, "descricao": "x"}, None)
    assert r.deu_certo
    assert [p for p, _ in pedidas] == [raiz, tmp_path / "ProgramDataDoWindows" / "EditorImpressao" / "atualizacao"]
    assert pedidas[0][1] == raiz / "current" / "sq.version"


# ---------------------------------------------------------------------------------------------------------------------
# M5: o fechar-e-reabrir sem trocar (o bilhete preso) e as duas janelas
# ---------------------------------------------------------------------------------------------------------------------

def test_m5_o_bilhete_preso_nao_impede_a_troca_do_reiniciar_agora(tmp_path, monkeypatch):
    """M5 (24/11/2026): com o `estado.json` preso por outro processo, o "Reiniciar agora" passava na conferência, a
    janela fechava, a anotação da troca não gravava e o programa era reaberto sem trocar. Agora nada é anotado antes de
    trocar: a troca é pedida."""
    p = _ate_o_aviso(tmp_path)
    monkeypatch.setattr(atualizacao, "gravar_estado", lambda estado: False)
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    assert [c[:2] for c in p.vp.chamadas if c[0] == "trocar"] == [("trocar", NOVA)]
    assert p.win.reaberturas == []


def test_m5_outra_janela_aberta_nos_segundos_do_fechar_nao_reabre(tmp_path):
    """M5, a outra parte: outra janela do programa abriu nos segundos do fechar; a segunda conferência a vê e a troca
    não é pedida. Antes, o programa era reaberto e o Kaique ficava com DUAS janelas. Agora não reabre (a outra janela
    já está aberta e mostra o aviso)."""
    p = _ate_o_aviso(tmp_path)

    def tela(ef):
        if isinstance(ef, fases.FecharJanela):
            p.win.outras = [(9, str(p.raiz / "current" / "EditorImpressao.exe"))]   # abriu enquanto fechava
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert "trocar" not in p.vp.nomes() and p.win.reaberturas == []


# ---------------------------------------------------------------------------------------------------------------------
# M6: a versão que pede motor novo nunca era anunciada, e nada dizia por quê (D-843)
# ---------------------------------------------------------------------------------------------------------------------

def test_m6_a_versao_que_pede_motor_novo_mostra_a_frase_uma_vez(tmp_path):
    """M6 e D-843 (Samuel, 24/11/2026: "vamos fazer b e colocamos isso no plano"): a versão que pede um motor do
    Kraken que não está no lugar não é anunciada nem trocada, e a janela mostra uma vez "Esta versão precisa de um
    motor novo. Avise o Samuel."; a abertura seguinte não mostra de novo. Antes: nada na tela, para sempre."""
    p = Prova(tmp_path / "a", motores={NOVA: 7}, motores_no_lugar={1})
    p.abrir()
    p.ligar_a_tela()
    assert [(type(e).__name__, getattr(e, "tipo", "")) for e in p.tela] == [("MostrarFalha", "motor")]
    assert atualizacao.frase_da_falha("motor") == "Esta versão precisa de um motor novo. Avise o Samuel."
    assert "trocar" not in p.vp.nomes()
    q = Prova(tmp_path / "b", motores={NOVA: 7}, motores_no_lugar={1})
    q.abrir()
    q.ligar_a_tela()
    assert q.tela == []


# ---------------------------------------------------------------------------------------------------------------------
# M7: contar "pelo nome" o processo cujo caminho não dá para ler
# ---------------------------------------------------------------------------------------------------------------------

@no_windows
def test_m7a_o_update_exe_que_nao_da_para_ler_e_nao_deu_para_saber(tmp_path, monkeypatch):
    """M7 (a) (24/11/2026): um `Update.exe` de outro programa, de outra conta, cujo caminho não dá para ler, contava
    como "o atualizador desta instalação está rodando": o programa saía calado a cada clique no atalho. Agora é "não
    deu para saber" (None): a abertura segue. O desta instalação, com o caminho lido: True."""
    alheio = [(5, "Update.exe" + windows.SEM_CAMINHO)] if hasattr(windows, "SEM_CAMINHO") else \
        [(5, "Update.exe (o caminho não deu para ler)")]
    monkeypatch.setattr(windows, "programas_rodando_de", lambda pasta, menos_a_familia_de=None, nomes=None: alheio)
    assert windows.atualizador_do_velopack_rodando(tmp_path) is None
    monkeypatch.setattr(windows, "programas_rodando_de",
                        lambda pasta, menos_a_familia_de=None, nomes=None: [(6, str(tmp_path / "Update.exe"))])
    assert windows.atualizador_do_velopack_rodando(tmp_path) is True


def test_m7b_o_processo_sem_caminho_nao_e_a_outra_janela(tmp_path):
    """M7 (b): um processo de outro programa com o nome de um da pasta (o `tesseract.exe`), sem caminho legível, dava
    "Feche a outra janela do programa..." sem outra janela nenhuma. Agora é "não deu para conferir": a frase da D-845
    com o motivo, nunca a da outra janela."""
    p = _ate_o_aviso(tmp_path, outras=[(5, "tesseract.exe (o caminho não deu para ler)")])
    c = p.atual.conferencia_da_troca(p.atual._achada)
    assert c.pode is False and c.outra_janela is False


# ---------------------------------------------------------------------------------------------------------------------
# M8: o título da caixa da D-840 (D-846)
# ---------------------------------------------------------------------------------------------------------------------

def test_m8_a_caixa_da_outra_janela_tem_o_titulo_atualizacao(tmp_path):
    """M8 e D-846 (Samuel, 24/11/2026: "ok"): a caixa "Feche a outra janela do programa e clique de novo." tem o título
    "Atualização" (antes, "Versão nova do programa", sem decisão dele). Pela ponte da tela de verdade."""
    from PySide6.QtWidgets import QApplication, QWidget

    from ui import aviso_de_atualizacao as aviso

    QApplication.instance() or QApplication([])
    p = Prova(tmp_path, outras=[(7, r"C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe")])
    p.abrir()
    avisos, respostas = [], [True, False]
    pai = QWidget()
    ponte = aviso.PonteDaTela(pai, p.atual, perguntar=lambda j, t, x, sim, nao: respostas.pop(0),
                              avisar=lambda j, t, x, icone=None: avisos.append((t, x)))
    p.atual.ligar_a_tela(ponte.receber)
    assert avisos == [("Atualização", "Feche a outra janela do programa e clique de novo.")]


# ---------------------------------------------------------------------------------------------------------------------
# M9: as cinco proteções da volta 2 que nenhum teste acusava (V3, V9, V10, V11, V13)
# ---------------------------------------------------------------------------------------------------------------------
# Estas proteções existem em `012c849c` (por isso os testes PASSAM lá): o defeito era não haver teste que acusasse
# quando desligadas (D-827). A prova é a rodada de mutações (`relatorios/atualizador-novo/volta3-provas/`), em que cada
# uma, desligada, é acusada por estes testes. O V3 mudou de sentido (M7 a) e está no teste de cima.

def test_m9_v9_o_registro_so_diz_reaberto_com_o_sinal_de_vida(tmp_path):
    """V9: "o programa foi aberto de novo" só quando o programa aberto deu sinal de vida; sem ele, o registro diz que
    não reabriu (§11.12 ponto 2: o registro que a gerente lê diz o que aconteceu)."""
    p = _ate_o_aviso(tmp_path)
    p.win.lancar_solto = lambda comando, sinal, espera_s=30: windows.Resposta(windows.FALHOU, "sem sinal de vida")
    p.atual._reabrir()
    assert "não consegui reabrir o programa" in _registro() and "o programa foi aberto de novo" not in _registro()


def test_m9_v10_o_pacote_sem_o_motor_exigido_nao_e_anunciado(tmp_path):
    """V10 (D-833: sem saber o motor da versão nova, nada é anunciado): o pacote baixado sem o `motor-exigido.json`."""
    p = Prova(tmp_path, motores={NOVA: None})
    p.abrir()
    p.ligar_a_tela()
    assert "MostrarVersaoNova" not in p.tipos_na_tela() and "trocar" not in p.vp.nomes()


def test_m9_v11_o_pacote_sem_o_motor_exigido_nao_e_trocado(tmp_path):
    """V11 (D-833: nada é trocado sem o motor dela): o pacote em `packages` (com a soma assinada) sem o
    `motor-exigido.json` não passa na conferência da troca."""
    import hashlib

    p = _ate_o_aviso(tmp_path)
    sem_motor = pacote_de_prova("sem o motor", None)
    (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(sem_motor)
    p.atual._somas_assinadas[NOVA] = hashlib.sha256(sem_motor).hexdigest()
    c = p.atual.conferencia_da_troca(p.atual._achada)
    assert c.pode is False and c.recusada is False and "motor" in c.motivo


@pytest.mark.parametrize("numero", ["2", True, 2.0, None, [2]])
def test_m9_v13_o_numero_do_motor_tem_de_ser_numero_de_verdade(tmp_path, numero):
    """V13: a leitura única do `motor-exigido.json` aceita só um número inteiro (nem texto, nem "verdadeiro", nem
    número com vírgula)."""
    import io
    import json
    import zipfile

    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr(atualizacao.CAMINHO_DO_MOTOR_EXIGIDO_NO_PACOTE, json.dumps({"versao": numero}))
    arquivo = tmp_path / "p.nupkg"
    arquivo.write_bytes(dados.getvalue())
    assert atualizacao.motor_exigido_pelo_pacote(arquivo) is None


# ---------------------------------------------------------------------------------------------------------------------
# Os leves
# ---------------------------------------------------------------------------------------------------------------------

def test_l1_nenhum_teste_escreve_no_programdata_de_verdade(monkeypatch):
    """Leve 1 (24/11/2026): dois testes da primeira abertura escreviam no registro de VERDADE do PC
    (`C:\\ProgramData\\EditorImpressao\\atualizacao\\atualizacao.log`: 16 linhas achadas). Agora a configuração comum
    dos testes (`tests/conftest.py`) troca o PROGRAMDATA para a pasta da rodada, como já fazia com o LOCALAPPDATA:
    sem nenhuma fixture, o registro não está no ProgramData de verdade."""
    monkeypatch.undo()                                 # sem a fixture deste arquivo: só o que vale para todo teste
    real = os.environ.get("EDITOR_IMPRESSAO_PROGRAMDATA_REAL") or "C:\\ProgramData"
    registro = atualizacao.caminho_do_registro().resolve()
    assert not str(registro).lower().startswith(str(Path(real).resolve()).lower() + os.sep)
    assert "saida_teste" in str(registro)


def test_l2_o_laco_da_d841_nao_empilha_chamadas(tmp_path):
    """Leve 2 (24/11/2026): cada "Reiniciar agora" com a outra janela aberta abria a caixa seguinte POR DENTRO da
    anterior; no clique 142 o Python parava por profundidade e o aviso deixava de voltar. Agora a conferência roda por
    trás e a caixa seguinte chega pela fila do Qt, depois de a anterior terminar: 200 cliques, o aviso volta todos."""
    from PySide6.QtWidgets import QApplication, QWidget

    from ui import aviso_de_atualizacao as aviso

    app = QApplication.instance() or QApplication([])
    p = Prova(tmp_path, outras=[(7, r"C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe")])
    p.abrir()
    p.atual._por_tras = atualizacao._por_tras          # o fio de trás de verdade
    contas = {"avisos": 0, "profundidade": 0}

    def perguntar(j, t, x, sim, nao):
        import inspect

        contas["avisos"] += 1
        contas["profundidade"] = max(contas["profundidade"], len(inspect.stack(0)))
        return contas["avisos"] < 200                 # "Reiniciar agora" 199 vezes, então "Depois"

    pai = QWidget()
    ponte = aviso.PonteDaTela(pai, p.atual, perguntar=perguntar, avisar=lambda *a, **k: None)
    p.atual.ligar_a_tela(ponte.receber)
    fim = time.monotonic() + 60
    while contas["avisos"] < 200 and time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.001)
    assert contas["avisos"] == 200
    assert contas["profundidade"] < 120, f"a pilha cresceu até {contas['profundidade']}"


def test_l3_um_erro_fora_do_previsto_na_troca_reabre_o_programa(tmp_path, monkeypatch):
    """Leve 3 (24/11/2026): uma exceção fora do previsto dentro da troca era engolida sem `TrocaPedida`, e o
    "Reiniciar agora" fechava sem reabrir. Agora ela vira "não pedida" e o programa é reaberto (com a frase)."""
    p = _ate_o_aviso(tmp_path)
    conferencias = {"n": 0}
    original = p.atual.conferencia_da_troca

    def segunda_quebra(v):
        conferencias["n"] += 1
        if conferencias["n"] == 2:                    # a segunda, dentro da troca, depois de a janela fechar
            raise ValueError("fora do previsto")
        return original(v)

    monkeypatch.setattr(p.atual, "conferencia_da_troca", segunda_quebra)
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    assert len(p.win.reaberturas) == 1


def test_l4_a_abertura_comum_nao_regrava_o_bilhete(tmp_path, monkeypatch):
    """Leve 4 (24/11/2026): toda abertura lia e regravava o `estado.json` inteiro, sem tranca entre processos (o atalho
    e a reabertura sem janela podiam desfazer a anotação um do outro). Agora a abertura só LÊ o bilhete; ele só é
    escrito quando há o que anotar (uma reprovação, uma frase), e a anotação da troca em andamento não existe mais."""
    gravadas = []
    monkeypatch.setattr(atualizacao, "gravar_estado", lambda estado: gravadas.append(dict(estado)) or True)
    p = Prova(tmp_path)
    p.abrir()
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert gravadas == []


# ---------------------------------------------------------------------------------------------------------------------
# B (D-844): a volta pelo pacote guardado, sem internet; e o bilhete só com as duas chaves
# ---------------------------------------------------------------------------------------------------------------------


def test_d844_guardar_a_ultima_boa_confere_a_soma_e_troca_a_antiga(tmp_path):
    """D-844: o pacote da versão que passou é copiado de `packages` com a soma conferida contra a assinatura; a
    antiga sai; a cópia trocada no meio não vira a última boa."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    assert atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA) is None
    assert atualizacao.ler_ultima_boa(p.raiz) == ATUAL
    nomes = sorted(x.name for x in atualizacao.pasta_da_ultima_boa(p.raiz).iterdir())
    assert nomes == sorted([atualizacao.nome_do_pacote(ATUAL), assinatura.nome_do_arquivo_da_assinatura(PACOTE, ATUAL)])
    q = Prova(tmp_path / "q", publicar_nova=False, ultima_boa=ANTERIOR)
    (q.pacote_em_packages(ATUAL)).write_bytes(b"trocado")
    assert "soma" in (atualizacao.guardar_ultima_boa(q.raiz, ATUAL, q.atual.fonte, PUBLICA) or "")
    assert atualizacao.ler_ultima_boa(q.raiz) == ANTERIOR


def test_o_bilhete_so_guarda_as_duas_coisas(tmp_path):
    """O sinal de gambiarra da emenda ("o estado.json voltando a decidir qualquer coisa além de 'não tentar' e 'frase
    uma vez"): depois de um ciclo inteiro (reprovar, frase guardada, as chaves velhas no arquivo), só as duas chaves."""
    atualizacao.gravar_estado({"nao_tentar": ["0.0.1"], "falha": {"tipo": "troca"}, "tentando": {"de": "a"}})
    atualizacao.reprovar("9.9.9", "prova")
    atualizacao.guardar_frase(fases.NAO_DEU_AGORA, "9.9.9", fases.MOTIVO_ERRO)
    assert set(_estado()) == {"reprovadas", "frase"} and _estado()["reprovadas"] == ["9.9.9"]


# ---------------------------------------------------------------------------------------------------------------------
# As três proteções novas que a primeira rodada de mutações achou sem teste (N26, N27, N28; D-827)
# ---------------------------------------------------------------------------------------------------------------------

def test_n26_a_ultima_boa_e_o_pacote_com_a_assinatura_ao_lado(tmp_path):
    """D-844: a última boa é a versão que tem na pasta o pacote E a assinatura do Samuel; só o pacote (ou só a
    assinatura, a da versão que está chegando) não é última boa (a volta não teria como conferir o pacote)."""
    p = Prova(tmp_path, publicar_nova=False)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    pasta.mkdir(parents=True)
    (pasta / atualizacao.nome_do_pacote(ANTERIOR)).write_bytes(p.vp.conteudo[ANTERIOR])
    assert atualizacao.ler_ultima_boa(p.raiz) == ""
    (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA)).write_text("x", encoding="utf-8")
    assert atualizacao.ler_ultima_boa(p.raiz) == ""
    _guardar_a_mao(p, ANTERIOR)
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR


def test_n27_a_versao_nova_vira_a_ultima_boa_sem_internet(tmp_path, monkeypatch):
    """D-844 ("sem internet"): a assinatura da versão nova é guardada quando ela é conferida, antes de baixar; depois
    da troca, a versão nova passa no teste e é guardada como a última boa mesmo sem internet."""
    p = _ate_o_aviso(tmp_path, ultima_boa=ATUAL)
    monkeypatch.setattr(versao, "VERSAO", NOVA)
    depois = _outra_abertura(p)
    depois.fonte = atualizacao.Fonte(str(tmp_path / "sem-internet"))
    depois.abrir([atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA])
    assert atualizacao.ler_ultima_boa(p.raiz) == NOVA


def test_n28_sem_a_licenca_nada_do_velopack_e_perguntado(tmp_path):
    """Sem a licença na pasta, nenhuma troca nossa acontece (o Velopack pediria licença ao Windows): a abertura nem
    pergunta ao Velopack se há pacote esperando (só a pergunta do Windows)."""
    p = Prova(tmp_path, grava=False)
    p.abrir()
    assert p.vp.leituras == [] and p.vp.chamadas == []
