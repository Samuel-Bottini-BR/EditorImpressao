"""As provas de comportamento das decisões de 25/11/2026 sobre o atualizador (volta 5; CLAUDE.md §11.4): D-867 a D-871.

Palavras do Samuel (chat 25/11/2026): "Li com o Fable o relatório do quem-tenta-quebrar 4. Decidi a opção A: a volta
automática sai da primeira entrega." Cada teste cita a decisão e as palavras dele.

Como rodam: o executor de verdade (`atualizacao.Atualizacao`), a regra de verdade, o disco de verdade numa pasta de
prova, as assinaturas com uma chave de prova. De mentira só a borda: a peça do Windows (`_Win`, que anota a caixa do
Windows em vez de mostrá-la) e a do Velopack (`VelopackFalso`). A caixa do Windows de verdade, numa área de trabalho
separada, está em `relatorios/atualizador-novo/volta5-provas/` (D-767).

Os testes montam o executor aqui (`_executor`), sem os parâmetros novos, para rodarem também no código de antes da volta
5 (`aba7b844`) e falharem lá PELO COMPORTAMENTO (a saída: `relatorios/atualizador-novo/volta5-testes-no-codigo-antigo.txt`).
Por isso a caixa de mentira (`_Win.mostrar_caixa_do_windows`) está escrita aqui também, igual à de
`tests/ajudante_do_atualizador.py` (o ajudante de antes não a tem).
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

import assinatura
import atualizacao
import versao
from core import conversa_com_o_velopack as conversa
from core import fases_da_atualizacao as fases
from core import windows
from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, CHAVE, NOVA, OUTRA_CHAVE, PACOTE, PUBLICA, Prova,  # noqa
                                          WindowsFalso, _ate_o_aviso, programdata_de_prova)

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent
TITULO = "Atualização"                                                       # D-846
TEXTO_D868 = "A versão nova não funcionou. Não desinstale nada. Avise o Samuel."  # D-868, palavra por palavra
FRASE_1 = "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. Avise o Samuel."
FRASE_3 = ("A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise o "
           "Samuel.")


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado, o registro e as frases vistas numa pasta de prova."""


class _Win(WindowsFalso):
    """A peça do Windows de mentira com a caixa do Windows que só anota (título, texto) e responde OK."""

    def __init__(self, *a, caixa_aparece: bool = True, quando_a_caixa=None, **k):
        super().__init__(*a, **k)
        self.caixas: list[tuple[str, str]] = []
        self.caixa_aparece = caixa_aparece
        self._quando_a_caixa = quando_a_caixa

    def mostrar_caixa_do_windows(self, titulo, texto):
        self.caixas.append((titulo, texto))
        if self._quando_a_caixa:
            self._quando_a_caixa()
        if self.caixa_aparece:
            return windows.Resposta(windows.DEU_CERTO)
        return windows.Resposta(windows.FALHOU, "não há área de trabalho à vista (de prova)")


class _Conta:
    """O teste rápido de mentira que conta quantas vezes rodou."""

    def __init__(self, passa: bool):
        self.passa, self.vezes = passa, 0

    def __call__(self):
        self.vezes += 1
        return self.passa, "erro ao abrir: ImportError (de prova)"


def _executor(p: Prova, *, teste=None, win: _Win | None = None, vp=None):
    """Uma abertura do programa na instalação de prova `p`, com a caixa de mentira (a caixa de verdade do executor:
    `_caixa_do_windows` chama `win.mostrar_caixa_do_windows`)."""
    win = win or _Win(pasta_de_troca=p.raiz.parent / "troca")
    a = atualizacao.Atualizacao(
        windows=win, velopack=vp or p.vp, raiz=p.raiz, fonte=p.atual.fonte, por_tras=lambda trabalho: trabalho(),
        pasta_grava=lambda raiz: True, garantir_motor=lambda: True, motor_no_lugar=lambda m=None: True,
        teste=teste or (lambda: (True, "")), chave_publica=PUBLICA)
    return win, a


def _frases_na_janela(a) -> list[str]:
    """Liga a janela e devolve o texto de cada frase que ela recebe."""
    tela: list = []
    a.ligar_a_tela(tela.append)
    return [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in tela if isinstance(e, fases.MostrarFalha)]


# ---------------------------------------------------------------------------------------------------------------------
# D-868: a versão reprovada, pela caixa do Windows, e o programa abre
# ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("com_ultima_boa", [False, True], ids=["primeira_depois_do_msi", "com_ultima_boa"])
def test_d868_a_versao_reprovada_mostra_a_caixa_do_windows_e_depois_abre(tmp_path, com_ultima_boa):
    """D-868 ("Se reprovar: versão vai para 'reprovadas' e a frase aparece pela caixa do Windows, pela peça
    (`MessageBoxW`), nunca pela janela do programa: 'A versão nova não funcionou. Não desinstale nada. Avise o Samuel.'
    Depois o programa tenta abrir assim mesmo."): nesta ordem, a reprovação no bilhete, a caixa do Windows com a frase
    palavra por palavra (título "Atualização"), e a abertura volta para o programa abrir (None). A janela, quando abre,
    não recebe a frase. Com e sem última boa (D-857: a "frase (3)" dela é esta). No código de antes: a volta (com
    última boa) ou a frase (3) na fila da janela (sem ela), e nenhuma caixa do Windows (o G1 do quarto)."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR if com_ultima_boa else None)
    p.pacote_em_packages(ATUAL)
    no_bilhete_na_hora_da_caixa: list = []
    win = _Win(pasta_de_troca=tmp_path / "troca",
               quando_a_caixa=lambda: no_bilhete_na_hora_da_caixa.append(atualizacao.ler_estado().get("reprovadas")))
    _, a = _executor(p, teste=_Conta(passa=False), win=win)
    saida = a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL])
    assert win.caixas == [(TITULO, TEXTO_D868)]
    assert no_bilhete_na_hora_da_caixa == [[ATUAL]], "a reprovação vem antes da caixa"
    assert saida is None, "depois do OK, o programa tenta abrir"
    assert _frases_na_janela(a) == [], "nunca pela janela do programa"


def test_d868_a_reprovada_nao_e_testada_de_novo_e_a_caixa_nao_se_repete(tmp_path):
    """D-868 e o pedido da gerente ("A versão reprovada não pode ser testada de novo a cada abertura nem ficar em
    laço"): a abertura seguinte (o atalho, na mesma conta) não roda o teste, não mostra a caixa de novo, e abre."""
    p = Prova(tmp_path, publicar_nova=False)
    p.pacote_em_packages(ATUAL)
    win, a = _executor(p, teste=_Conta(passa=False))
    a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL])
    assert win.caixas == [(TITULO, TEXTO_D868)]
    for _ in range(2):
        conta = _Conta(passa=False)
        win2, b = _executor(p, teste=conta)
        assert b.abrir([]) is None
        assert (conta.vezes, win2.caixas) == (0, [])


def test_d868_depois_do_sim_ao_fechar_a_caixa_vem_na_abertura_seguinte(tmp_path):
    """D-868 com a D-769 ("Sim" ao fechar: nada abre na tela depois): a versão nova testada sem janela (a reabertura do
    "Sim" ao fechar) que reprova não mostra nada na hora (sai); a próxima abertura mostra a caixa do Windows com a frase
    da D-868, antes da janela. No código de antes: a volta, ou a frase (3) para a janela."""
    p = Prova(tmp_path, publicar_nova=False)
    p.pacote_em_packages(ATUAL)
    win, a = _executor(p, teste=_Conta(passa=False))
    assert a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL, atualizacao.ARG_SEM_JANELA]) == 0
    assert win.caixas == [] and p.vp.chamadas == []
    win2, b = _executor(p, teste=_Conta(passa=False))
    assert b.abrir([]) is None
    assert win2.caixas == [(TITULO, TEXTO_D868)]


@pytest.mark.parametrize("caso", ["d839_troca_que_nao_aconteceu", "d845_frase_guardada", "frase_2_recusada",
                                  "d843_motor"])
def test_d868_toda_frase_de_antes_da_janela_vai_pela_caixa_do_windows(tmp_path, caso):
    """D-868 ("Toda frase que pode aparecer antes da janela existir usa esse caminho"): cada frase do atualizador que
    chega antes de a janela abrir aparece na caixa do Windows, com as palavras de sempre, e a janela não a recebe de
    novo. Os quatro caminhos: a troca que o Velopack não fez (D-839), a frase guardada no bilhete (D-845), a assinatura
    recusada e o motor (D-843) quando a procura e o download (por trás) terminam antes de a janela abrir."""
    esperado = {
        "d839_troca_que_nao_aconteceu": "A atualização não deu certo. O programa continua na versão de antes e "
                                        "funcionando. Avise o Samuel.",
        "d845_frase_guardada": "Não deu para atualizar agora: o arquivo da versão nova sumiu do computador. Tente ao "
                               "fechar o programa.",
        "frase_2_recusada": "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O "
                            "programa continua funcionando. Avise o Samuel.",
        "d843_motor": "Esta versão precisa de um motor novo. Avise o Samuel.",
    }[caso]
    argumentos: list[str] = []
    if caso == "d839_troca_que_nao_aconteceu":
        p = Prova(tmp_path, publicar_nova=False)
        argumentos = [atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA]
    elif caso == "d845_frase_guardada":
        p = Prova(tmp_path, publicar_nova=False)
        atualizacao.guardar_frase(fases.NAO_DEU_AGORA, NOVA, fases.MOTIVO_PACOTE_SUMIU)
    elif caso == "frase_2_recusada":
        p = Prova(tmp_path, chave_da_nova=OUTRA_CHAVE)
    else:
        p = Prova(tmp_path, motores={NOVA: 2}, motores_no_lugar={1})
    motor = (lambda m=None: m in {1, None}) if caso == "d843_motor" else (lambda m=None: True)
    win = _Win(pasta_de_troca=tmp_path / "troca")
    a = atualizacao.Atualizacao(
        windows=win, velopack=p.vp, raiz=p.raiz, fonte=p.atual.fonte, por_tras=lambda trabalho: trabalho(),
        pasta_grava=lambda raiz: True, garantir_motor=lambda: True, motor_no_lugar=motor,
        teste=lambda: (True, ""), chave_publica=PUBLICA)
    a.abrir(argumentos)
    assert win.caixas == [(TITULO, esperado)]
    assert _frases_na_janela(a) == []


def test_d868_com_a_janela_aberta_a_frase_vai_para_a_janela(tmp_path):
    """O que já funcionava não muda (§11.8): com a janela aberta, a resposta a um clique ("Reiniciar agora" com outra
    janela do programa aberta, D-840) vai para a caixa da janela, e não para a do Windows."""
    p = Prova(tmp_path, outras=[(7, r"C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe")])
    win = _Win(pasta_de_troca=tmp_path / "troca", outras=p.win.outras)
    _, a = _executor(p, win=win)
    a.abrir([])
    tela: list = []
    a.ligar_a_tela(tela.append)
    a.evento(fases.Escolheu(True))
    frases = [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in tela if isinstance(e, fases.MostrarFalha)]
    assert frases == ["Feche a outra janela do programa e clique de novo."] and win.caixas == []


# ---------------------------------------------------------------------------------------------------------------------
# D-867: a volta automática saiu
# ---------------------------------------------------------------------------------------------------------------------

PROGRAMA = ["atualizacao.py", "main.py", "core/fases_da_atualizacao.py", "core/conversa_com_o_velopack.py",
            "core/windows.py", "ui/aviso_de_atualizacao.py"]


def test_d867_nada_da_volta_automatica_sobrou_no_programa():
    """D-867 ("Tirar a volta automática: a marca 'sem volta', o 'uma vez só', a segunda tentativa, o `--voltando`, a
    fase de volta"; prova do Livro: "Procurar no código: nenhum `--voltando`, nenhuma marca `.sem-volta`, nenhuma fase
    de volta"): nos arquivos do atualizador, nenhum desses nomes no código, e as frases (1) e (3) da D-778 não estão em
    texto nenhum do programa. No código de antes, todos estão lá."""
    proibidos_no_codigo = {"ARG_VOLTANDO", "MARCA_SEM_VOLTA", "MarcarSemVolta", "Voltar", "VoltaPedida", "VOLTANDO",
                           "_voltar", "_volta_que_nao_deu", "reaberto_voltando", "sem_volta", "FALHA_VOLTA",
                           "FALHA_TESTE", "FRASE_DA_FALHA_SEM_VOLTA", "permitir_voltar"}
    achados = []
    for arq in PROGRAMA:
        arvore = ast.parse((RAIZ_DO_REPOSITORIO / arq).read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            nome = (no.id if isinstance(no, ast.Name) else no.attr if isinstance(no, ast.Attribute) else
                    no.name if isinstance(no, (ast.FunctionDef, ast.ClassDef)) else no.arg if isinstance(no, ast.arg)
                    else None)
            if nome in proibidos_no_codigo:
                achados.append((arq, no.lineno, nome))
            if isinstance(no, ast.Constant) and isinstance(no.value, str) and (
                    "--voltando" in no.value or "sem-volta" in no.value or no.value in ("volta", "voltando")
                    or FRASE_1 in no.value or FRASE_3 in no.value):       # o Python junta os textos partidos em um
                achados.append((arq, no.lineno, no.value[:40]))
    assert achados == []
    assert set(atualizacao.FRASES_DA_FALHA.values()).isdisjoint({FRASE_1, FRASE_3})


def test_d867_a_reprovada_nao_pede_nada_ao_velopack(tmp_path):
    """D-867 (prova do Livro: "versão reprovada → nada é pedido ao Velopack"): com a última boa guardada, a versão que
    reprova não monta pedido, não copia, não troca, não procura. No código de antes: a volta pela última boa."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    _, a = _executor(p, teste=_Conta(passa=False))
    a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL])
    assert p.vp.chamadas == []


# ---------------------------------------------------------------------------------------------------------------------
# D-869: a última boa continua guardada, e nada automático depende dela
# ---------------------------------------------------------------------------------------------------------------------

def test_d869_a_ultima_boa_continua_guardada_e_a_reprovada_nao_mexe_nela(tmp_path, monkeypatch):
    """D-869 ("A última boa continua sendo guardada (de `packages\\`, sem internet), mas nada automático depende dela";
    prova do Livro: "Troca aprovada → `ultima-boa` tem o pacote; versão reprovada → nada lê a última boa"): a versão
    que passa no teste é guardada como a última boa, copiada de `packages` sem internet; a versão seguinte que reprova
    não pede nada ao Velopack (o pacote guardado não é usado) e a pasta fica byte por byte como estava. No código de
    antes: a reprovada voltava pela última boa."""
    p = Prova(tmp_path, publicar_nova=False)
    p.pacote_em_packages(ATUAL)
    _, a = _executor(p, teste=_Conta(passa=True))
    a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL])
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    assert (pasta / atualizacao.nome_do_pacote(ATUAL)).read_bytes() == p.conteudo_de(ATUAL)
    antes = {f.name: f.read_bytes() for f in pasta.iterdir()}
    estragada = "9.9.1"
    (p.raiz / "packages" / atualizacao.nome_do_pacote(estragada)).write_bytes(b"pacote da versao estragada")
    monkeypatch.setattr(versao, "VERSAO", estragada)
    vp = type(p.vp)(p.raiz)
    _, b = _executor(p, teste=_Conta(passa=False), vp=vp)
    assert b.abrir([atualizacao.ARG_CONFERIR_NOVA, ATUAL, estragada]) is None
    assert vp.chamadas == []
    assert {f.name: f.read_bytes() for f in pasta.iterdir()} == antes


# ---------------------------------------------------------------------------------------------------------------------
# D-870: M1, M2 e M5 do quarto "quem tenta quebrar"
# ---------------------------------------------------------------------------------------------------------------------

def test_d870_m1_a_frase_da_outra_janela_nao_aparece_depois_da_troca_certa(tmp_path, monkeypatch):
    """D-870, M1 ("a frase 'havia outra janela do programa aberta' nunca aparece depois de a troca ter dado certo"): o
    "Sim" da primeira janela guardou a frase (havia outra janela); o "Sim" da segunda trocou; a abertura seguinte, já na
    versão nova, não mostra a frase (nem na caixa do Windows, nem na janela). Se a troca não aconteceu (a versão que
    roda ainda é a de antes), a frase aparece, como a D-858/D-864 pedem. No código de antes: aparece nas duas."""
    p = Prova(tmp_path, publicar_nova=False)
    atualizacao.guardar_frase(fases.NAO_DEU_AGORA, NOVA, fases.MOTIVO_HAVIA_OUTRA_JANELA)
    win, a = _executor(p)
    a.abrir([])
    assert [t for _, t in win.caixas] + _frases_na_janela(a) == [
        "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa."]

    q = Prova(tmp_path / "trocou", publicar_nova=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData-trocou"))       # outra conta: nada "visto"
    atualizacao.guardar_frase(fases.NAO_DEU_AGORA, NOVA, fases.MOTIVO_HAVIA_OUTRA_JANELA)
    monkeypatch.setattr(versao, "VERSAO", NOVA)                                    # o "Sim" da segunda janela trocou
    atualizacao.marcar(q.raiz, atualizacao.MARCA_APROVADA, NOVA)                   # e a nova passou no teste
    win2, b = _executor(q)
    b.abrir([])
    textos = [t for _, t in win2.caixas] + _frases_na_janela(b)
    assert not [t for t in textos if "havia outra janela" in t], textos


def _sem_o_atualizador(p: Prova) -> None:
    """O antivírus pôs de lado o `Update.exe` da instalação de prova."""
    (p.raiz / "Update.exe").unlink(missing_ok=True)


def test_d870_m2_reiniciar_agora_sem_o_update_exe_nao_fecha_e_tem_frase_propria(tmp_path):
    """D-870, M2 ("`Update.exe` que some: frase própria, sem 'tente ao fechar'"): com a versão nova pronta e o
    `Update.exe` posto de lado, o "Reiniciar agora" não fecha a janela (nada a trocar), mostra a frase própria (sem
    "Tente ao fechar o programa"), e fechar não pergunta nada. No código de antes: a janela fechava por nada."""
    p = _ate_o_aviso(tmp_path)
    _sem_o_atualizador(p)
    p.tela.clear()
    p.atual.evento(fases.Escolheu(True))
    assert "FecharJanela" not in p.tipos_na_tela()
    frases = [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in p.tela if isinstance(e, fases.MostrarFalha)]
    assert frases == [getattr(atualizacao, "FRASE_SEM_ATUALIZADOR", None)]
    assert "Tente ao fechar" not in frases[0]
    p.tela.clear()
    p.atual.evento(fases.Fechando())
    assert p.tela == [] and "trocar" not in p.vp.nomes()


def test_d870_m2_sim_ao_fechar_sem_o_update_exe_e_a_frase_na_abertura_seguinte(tmp_path):
    """D-870, M2: o "Sim" ao fechar sem o `Update.exe` não pede a troca e guarda a frase própria; a abertura seguinte
    a mostra pela caixa do Windows (D-868). No código de antes: o pedido ia ao Velopack (que recusaria)."""
    p = _ate_o_aviso(tmp_path)
    _sem_o_atualizador(p)
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    win, b = _executor(p)
    b.abrir([])
    assert win.caixas == [(TITULO, getattr(atualizacao, "FRASE_SEM_ATUALIZADOR", None))]


@pytest.mark.parametrize("some", [True, False], ids=["o_update_exe_some_no_pedido", "o_atualizador_nao_comecou"])
def test_d870_m2_o_motivo_do_pedido_que_falha_vem_do_disco(tmp_path, some):
    """D-870, M2: o `Update.exe` estava lá na conferência e sumiu nos segundos do pedido: o motivo é o da frase própria,
    conferido no disco (não pelo texto do erro). Se ele continua lá e o pedido falha, é o "o atualizador do programa
    não começou" de sempre (D-847). No código de antes: sempre o "não começou"."""
    p = _ate_o_aviso(tmp_path)

    def trocar(endereco, v, reabrir, argumentos):
        if some:
            _sem_o_atualizador(p)
        raise conversa.ErroDoVelopack("This application is not properly installed: Update.exe does not exist")

    p.vp.trocar = trocar
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert atualizacao.ler_estado()["frase"]["motivo"] == ("sem_atualizador" if some else "atualizador")


def test_d870_m2_quando_o_update_exe_volta_a_versao_e_oferecida_de_novo(tmp_path):
    """D-870, M2 ("e oferecer de novo quando voltar"): depois da frase própria, com o `Update.exe` de volta, a abertura
    seguinte mostra o aviso da versão nova. (Passa também no código de antes: nada marcava a versão. A prova com a
    biblioteca do Velopack de verdade está em `relatorios/atualizador-novo/volta5-provas/`.)"""
    p = _ate_o_aviso(tmp_path)
    _sem_o_atualizador(p)
    p.atual.evento(fases.Escolheu(True))
    (p.raiz / "Update.exe").write_bytes(b"MZ")                                    # voltou
    win, b = _executor(p)
    b.abrir([])
    tela: list = []
    b.ligar_a_tela(tela.append)
    assert [type(e).__name__ for e in tela] == ["MostrarVersaoNova"]


def test_d870_m5_x11_o_404_do_github_e_a_versao_sem_a_assinatura(monkeypatch):
    """D-870, M5 (X11 do quarto "quem tenta quebrar"): no GitHub, a resposta 404 ao pedir a assinatura é "a versão não
    tem a assinatura" (a frase 2), e qualquer outra resposta (503, sem rede) é "não deu para saber" (só o registro, a
    próxima abertura tenta). Desligar a proteção (o 404 virar "sem rede") faz este teste falhar."""
    import urllib.error
    import urllib.request

    def responde(codigo):
        def abrir(endereco, timeout=60):
            raise urllib.error.HTTPError(endereco, codigo, "de prova", {}, None)
        return abrir

    fonte = atualizacao.Fonte(atualizacao.REPOSITORIO)
    alvo = conversa.VersaoDoVelopack(PACOTE, "9.9.9", f"{PACOTE}-9.9.9-full.nupkg", "00" * 32, 1)
    monkeypatch.setattr(urllib.request, "urlopen", responde(404))
    with pytest.raises(FileNotFoundError):
        fonte.ler("9.9.9", "x.assinatura")
    motivo = atualizacao.conferir_assinatura_do(fonte, alvo, PUBLICA)
    assert motivo and "não achei a assinatura" in motivo
    monkeypatch.setattr(urllib.request, "urlopen", responde(503))
    with pytest.raises(OSError) as erro:
        fonte.ler("9.9.9", "x.assinatura")
    assert not isinstance(erro.value, FileNotFoundError)
    with pytest.raises(OSError):
        atualizacao.conferir_assinatura_do(fonte, alvo, PUBLICA)


@pytest.mark.parametrize("chave", ["do_samuel", "de_outra_conta"])
def test_d870_m5_x18_a_assinatura_guardada_do_pacote_esperando_e_conferida(tmp_path, chave):
    """D-870, M5 (X18 do quarto "quem tenta quebrar"; D-724 "só pacote assinado" no caminho da D-859): sem internet, o
    pacote esperando só é oferecido se a assinatura guardada for do Samuel e afirmar o pacote de `packages`. Uma
    assinatura posta por outra conta na pasta da última boa (que Usuários podem modificar, D-837), com a soma do pacote
    trocado, NÃO leva ao aviso. Desligar a conferência faz o caso "de_outra_conta" falhar."""
    p = Prova(tmp_path, publicar_nova=False, erro_ao_procurar="sem internet", pendente=NOVA)
    dado = p.conteudos[NOVA]
    nome = atualizacao.nome_do_pacote(NOVA)
    (p.raiz / "packages").mkdir(parents=True, exist_ok=True)
    (p.raiz / "packages" / nome).write_bytes(dado)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    pasta.mkdir(parents=True, exist_ok=True)
    texto = assinatura.escrever_assinatura(CHAVE if chave == "do_samuel" else OUTRA_CHAVE, assinatura.VersaoAssinada(
        PACOTE, NOVA, nome, hashlib.sha256(dado).hexdigest()))
    (pasta / (assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA) + ".chegando")).write_bytes(texto.encode("utf-8"))
    p.abrir()
    p.ligar_a_tela()
    if chave == "do_samuel":
        assert "MostrarVersaoNova" in p.tipos_na_tela()
    else:
        assert "MostrarVersaoNova" not in p.tipos_na_tela()


# ---------------------------------------------------------------------------------------------------------------------
# D-871: os testes da volta saíram; a prova é o aviso
# ---------------------------------------------------------------------------------------------------------------------

def test_d871_nenhum_teste_pede_a_volta_e_o_aviso_e_a_prova(tmp_path):
    """D-871 ("Os testes da volta automática saem com ela. A D-718 fica no Livro como 'adiada para depois da entrega',
    com a prova de que o programa avisa quando a versão nova falha."; prova do Livro: "Versão de mentira que falha no
    teste rápido → a frase da D-868 aparece; nenhum teste pede volta"): nenhum arquivo de teste usa no código os nomes
    da volta, e a versão de mentira que falha mostra a frase da D-868."""
    nomes_da_volta = {"ARG_VOLTANDO", "MARCA_SEM_VOLTA", "MarcarSemVolta", "Voltar", "VoltaPedida", "VOLTANDO",
                      "_voltar", "reaberto_voltando", "FALHA_VOLTA", "FALHA_TESTE", "FRASE_DA_FALHA_SEM_VOLTA"}
    achados = []
    for arq in sorted((RAIZ_DO_REPOSITORIO / "tests").glob("*.py")):
        if arq.name == Path(__file__).name:
            continue
        for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8-sig"))):
            nome = no.id if isinstance(no, ast.Name) else no.attr if isinstance(no, ast.Attribute) else None
            if nome in nomes_da_volta:
                achados.append((arq.name, no.lineno, nome))
            if isinstance(no, ast.Constant) and isinstance(no.value, str) and no.value == "--voltando":
                achados.append((arq.name, no.lineno, no.value))
    assert achados == []
    p = Prova(tmp_path, publicar_nova=False)
    p.pacote_em_packages(ATUAL)
    win, a = _executor(p, teste=_Conta(passa=False))
    a.abrir([atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL])
    assert win.caixas == [(TITULO, TEXTO_D868)]


# ---------------------------------------------------------------------------------------------------------------------
# D-877: a segunda recusa do Windows para a mesma versão também avisa
# ---------------------------------------------------------------------------------------------------------------------

def test_d877_cada_recusa_do_windows_avisa_uma_vez_e_nao_se_repete(tmp_path, monkeypatch):
    """D-877 (Samuel, 25/11/2026: "Conserta agora só o aviso da segunda recusa do Windows (M1)"; o M1 do quinto "quem
    tenta quebrar", o caso L1): o Windows não deixa trocar da 7.0.0 para a 7.0.1, e o Velopack reabre a 7.0.0 com o
    pedido. Na primeira recusa aparece a frase da D-839; numa SEGUNDA recusa para a mesma versão (outro momento), ela
    aparece de novo (no código de `0d9cac4e` a segunda não dizia nada: o nome da frase não tinha o momento). E ela nunca
    se repete sozinha: a abertura seguinte pelo atalho (sem o pedido) não mostra nada (§11.8)."""
    frase = "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel."
    monkeypatch.setattr(versao, "VERSAO", "7.0.0")
    p = Prova(tmp_path, publicar_nova=False)
    horas = iter(["2026-11-25T10:00:00", "2026-11-26T09:30:00", "2026-11-26T09:31:00"])
    monkeypatch.setattr(atualizacao, "_agora", lambda: next(horas))
    caixas = []
    for argumentos in ([atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1"], [atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1"],
                       []):
        win, a = _executor(p)
        a.abrir(argumentos)
        caixas.append([t for _, t in win.caixas] + _frases_na_janela(a))
    assert caixas == [[frase], [frase], []]
