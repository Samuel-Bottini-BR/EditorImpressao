"""Provas do ajudante da atualizacao: D-732 a D-736 e o achado B1 (17/11/2026).

ATUALIZADOR NOVO (23/11/2026, D-830; D-836 para os testes): o ajudante (a tarefa que rodava como o sistema), os
scripts do PowerShell, a marca de "computador preparado" e a janelinha nossa SAIRAM. As provas que cobravam essas peças
saíram com elas; as que cobravam decisões que continuam passaram a chamar o caminho novo (o executor de verdade, com
só a borda de mentira, tests/ajudante_do_atualizador.py); as das decisões que o Samuel mudou (D-769/D-794/D-831: o
"Depois" entra ao fechar; D-832: a janelinha é a do Velopack; D-825: a senha não liga nada) cobram o que vale hoje.
A lista teste por teste: relatorios/atualizador-novo/lista-dos-testes-d836.md. O texto abaixo é o de 17/11.

Decisoes do Samuel provadas aqui (docs/plano/DECISOES.md), sem tocar o Windows:
o schtasks, o PowerShell escondido e a pergunta do Windows sao trocados por
pecas de mentira que so anotam o que SERIA feito.

  D-732  (17/11/2026) a versao nova e procurada quando o programa ABRE, nao
         quando o computador liga.
  D-733  (17/11/2026) jeito 1: uma pergunta do Windows na primeira abertura
         cria o ajudante (tarefa como o sistema, que a conta comum pode mandar
         rodar) e faz o resto que pede licenca; depois, nenhuma pergunta por
         atualizacao nem na volta.
  D-734  (17/11/2026) com "Depois", entra na proxima vez que o Kaique abrir,
         com uma espera curta antes da janela; fechar nao troca nada.
  D-735  (17/11/2026) a pergunta do Windows da primeira abertura aparece
         sempre, com ou sem a senha.
  D-736  (17/11/2026) aberto por um teste a distancia, nao procura; o Samuel
         manda atualizar de longe pelo mesmo ajudante.
  B1     (achado de 16/11/2026, plano.md da D-731) os ganchos do .msi rodam
         sem administrador: ao_instalar/ao_atualizar nao podem criar a tarefa.

Nada aqui grava no %ProgramData% nem no %LOCALAPPDATA% de verdade.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

import pytest

import atualizacao
import configuracoes
from core import testes_a_distancia as td

RAIZ = Path(__file__).resolve().parent.parent
EXE = Path(r"C:\Program Files\EditorImpressao\current\EditorImpressao.exe")


@pytest.fixture(autouse=True)
def _pastas_de_mentira(tmp_path, monkeypatch):
    """ProgramData e LOCALAPPDATA de mentira (as Configuracoes nascem limpas)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setenv("USERNAME", "Kaique")
    yield


class FakeExecutor(td.Executor):
    """A pergunta do Windows de mentira: anota os passos, nao toca o Windows."""

    def __init__(self, cancelado: bool = False) -> None:
        self.chamadas: list[tuple[list[td.Passo], str]] = []
        self._cancelado = cancelado

    def aplicar(self, passos, senha):
        self.chamadas.append((list(passos), senha))
        if self._cancelado:
            return td.Resultado(False, cancelado=True, passos=passos)
        return td.Resultado(True, passos=passos)


@pytest.fixture
def fake(monkeypatch):
    f = FakeExecutor()
    monkeypatch.setattr(td, "_executor", f)
    return f


def _proibido(*_a, **_k):
    pytest.fail("tocou o Windows de verdade")


# ---------------------------------------------------------------------------
# D-732 / D-733: o ajudante nao roda ao ligar; a conta comum manda rodar
# ---------------------------------------------------------------------------

def test_b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa(monkeypatch):
    """B1 (16/11/2026) (adaptado pela D-836): os ganchos do .msi rodam sem administrador; nenhum deles pede nada ao
    Windows (no desenho novo não há tarefa nenhuma a criar)."""
    from core import windows

    for nome in ("comecar_pedido_de_licenca", "pedir_licenca", "criar_tarefa", "rodar_tarefa", "apagar_tarefa"):
        monkeypatch.setattr(windows, nome, _proibido)
    atualizacao.ao_instalar("1.2.0")
    atualizacao.ao_atualizar("1.2.0")


# ---------------------------------------------------------------------------
# D-733 / D-735: a pergunta do Windows da primeira abertura
# ---------------------------------------------------------------------------

def test_d735_sem_a_senha_a_pergunta_do_windows_aparece_assim_mesmo(fake, monkeypatch, tmp_path):
    """D-735 (adaptado pela D-836): a pergunta do Windows não depende da senha: com a pasta sem a licença ela aparece
    na abertura, tenha a janela da senha aparecido ou não."""
    p = _prova(tmp_path, grava=False)
    p.abrir()
    assert len(p.win.pedidos) == 1
    assert fake.chamadas == []


def test_d735_agora_nao_na_senha_nao_pula_a_pergunta_do_windows(fake, monkeypatch, tmp_path):
    """D-735 (adaptado pela D-836; D-834: a pergunta vem ANTES da janela, a senha depois): "Agora não" na janela da
    senha mostra o aviso "Sem a senha..." de sempre e não toca o Windows; a pergunta do Windows é a da abertura, que já
    aconteceu (e volta enquanto a pasta não aceitar gravação)."""
    import ui.testes_a_distancia_ui as tdui

    avisos = []
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "")
    monkeypatch.setattr(tdui.perguntas, "avisar", lambda *a, **k: avisos.append(a[2]))
    p = _prova(tmp_path, grava=False)
    p.abrir()
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: False)
    assert len(p.win.pedidos) == 1 and fake.chamadas == []
    assert avisos and "senha" in avisos[0].lower()


def test_d735_com_a_opcao_desligada_a_pergunta_do_windows_aparece(fake, monkeypatch, tmp_path):
    """D-735 (adaptado pela D-836): com a opção dos testes desligada não há janela da senha, e a pergunta do Windows da
    abertura aparece do mesmo jeito."""
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(td, "esta_ligado", lambda: False)
    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: pytest.fail("a janela da senha apareceu"))
    p = _prova(tmp_path, grava=False)
    p.abrir()
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: False)
    assert len(p.win.pedidos) == 1


def test_d733_disse_nao_fica_anotado_e_nada_quebra(tmp_path):
    """D-733 (adaptado pela D-836): "Não" à pergunta do Windows → anotado no registro; a janela abre (nada quebra)."""
    p = _prova(tmp_path, grava=False, licenca="disse_nao")
    assert p.abrir() is None
    assert "disse Não" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# D-733 / D-734: "Reiniciar agora" e "Depois" sem pergunta do Windows
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# D-736: testes a distancia
# ---------------------------------------------------------------------------

def test_d736_a_conta_de_testes_e_reconhecida_pelo_nome_fixo(monkeypatch):
    """D-736 (17/11/2026): a regra unica de "aberto por um teste a distancia"."""
    assert atualizacao.e_a_conta_de_testes(td.NOME_DA_CONTA)
    assert atualizacao.e_a_conta_de_testes(td.NOME_DA_CONTA.lower())
    assert not atualizacao.e_a_conta_de_testes("Kaique")
    monkeypatch.setenv("USERNAME", td.NOME_DA_CONTA)
    assert atualizacao.e_a_conta_de_testes()


def test_d736_aberto_por_teste_a_distancia_nao_procura_nem_troca(tmp_path, monkeypatch):
    """D-736 (adaptado pela D-836): na conta de testes nada de atualização roda (nem a pergunta, nem a procura)."""
    monkeypatch.setenv("USERNAME", td.NOME_DA_CONTA)
    p = _prova(tmp_path, grava=False)
    p.abrir()
    assert p.win.pedidos == [] and p.vp.chamadas == []


# ---------------------------------------------------------------------------
# A fonte de teste da etapa 5 (pedido da gerente, 17/11/2026)
# ---------------------------------------------------------------------------

ADMIN, KAIQUE = "S-1-5-32-544", "S-1-5-21-1-2-3-1001"


def _arquivo_da_fonte(pasta: Path) -> Path:
    arquivo = atualizacao.caminho_da_fonte_de_teste()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(str(pasta) + "\n", encoding="utf-8")
    return arquivo


def test_etapa5_sem_o_arquivo_as_versoes_vem_do_github():
    """17/11/2026: no notebook do Kaique o arquivo nao existe: tudo como sempre (o GitHub)."""
    assert atualizacao.fonte_de_teste(dono=_proibido) is None
    assert atualizacao.fonte_da_linha([]).endereco == atualizacao.REPOSITORIO


def test_etapa5_o_arquivo_do_administrador_aponta_a_pasta_de_teste(tmp_path):
    """17/11/2026: o arquivo que so o administrador grava aponta a pasta da versao de mentira."""
    (tmp_path / "servidor").mkdir()
    _arquivo_da_fonte(tmp_path / "servidor")
    fonte = atualizacao.fonte_de_teste(dono=lambda p: ADMIN)
    assert fonte is not None and fonte.endereco == str(tmp_path / "servidor") and not fonte.e_github
    # a mesma regra de sempre: --fonte na linha vence; sem ele, a fonte de teste
    assert atualizacao.fonte_da_linha([], de_teste=lambda: fonte) is fonte
    assert atualizacao.fonte_da_linha([atualizacao.ARG_FONTE, "outra"], de_teste=_proibido).endereco == "outra"
    # o conferir, reaberto pelo Velopack, recebe a mesma fonte
    assert atualizacao._argumentos_da_fonte(fonte) == [atualizacao.ARG_FONTE, str(tmp_path / "servidor")]


def test_etapa5_arquivo_de_conta_comum_e_ignorado(tmp_path):
    """17/11/2026: uma conta comum consegue criar o arquivo, mas ele fica dela e e ignorado."""
    (tmp_path / "servidor").mkdir()
    _arquivo_da_fonte(tmp_path / "servidor")
    assert atualizacao.fonte_de_teste(dono=lambda p: KAIQUE) is None
    assert atualizacao.fonte_de_teste(dono=lambda p: None) is None
    assert "não é do administrador" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    _arquivo_da_fonte(tmp_path / "nao-existe")
    assert atualizacao.fonte_de_teste(dono=lambda p: ADMIN) is None


def test_etapa5_pela_fonte_de_teste_a_assinatura_e_conferida_igual(tmp_path):
    """17/11/2026 / D-724 (adaptado pela D-836): pela fonte de teste, a versão assinada por outra chave é recusada
    antes de baixar, como pelo GitHub."""
    from tests.ajudante_do_atualizador import OUTRA_CHAVE

    p = _prova(tmp_path, chave_da_nova=OUTRA_CHAVE)
    p.abrir()
    assert "baixar" not in p.vp.nomes()


# ---------------------------------------------------------------------------
# D-741 (Samuel, 17/11/2026: "Sim"): depois de um "Nao", a pergunta do Windows volta a cada abertura
# ---------------------------------------------------------------------------

def test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais(tmp_path):
    """D-741 ("Sim") (adaptado pela D-836: o "preparado?" passou a ser o teste de gravar na pasta do programa, D-825):
    "Não" → abrir de novo → a pergunta volta; "Não" de novo → volta de novo; "Sim" (a pasta passa a aceitar gravação)
    → nunca mais."""
    from tests.ajudante_do_atualizador import Prova

    p = _prova(tmp_path, grava=False, licenca="disse_nao")
    for _ in range(2):
        p.atual = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz, fonte=p.atual.fonte,
                                          por_tras=lambda t: t(), pasta_grava=lambda r: p.grava["agora"],
                                          garantir_motor=lambda: True, motor_no_lugar=lambda: True,
                                          chave_publica=p.atual._chave)
        p.abrir()
    assert len(p.win.pedidos) == 2
    p.win.licenca = "comecou"
    p.atual = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz, fonte=p.atual.fonte,
                                      por_tras=lambda t: t(), pasta_grava=lambda r: p.grava["agora"],
                                      garantir_motor=lambda: True, motor_no_lugar=lambda: True,
                                      chave_publica=p.atual._chave)
    p.abrir()
    assert len(p.win.pedidos) == 3 and p.grava["agora"] is True
    q = Prova(tmp_path / "depois", grava=True)
    q.win = p.win
    q.atual.windows = p.win
    q.abrir()
    assert len(p.win.pedidos) == 3, "com a pasta aceitando gravação, a pergunta não volta"


def test_d741_sim_na_primeira_abertura_nao_volta_mais(tmp_path):
    """D-741 (adaptado pela D-836): "Sim" já na primeira abertura → a pasta aceita gravação → nas aberturas seguintes,
    nenhuma pergunta."""
    from tests.ajudante_do_atualizador import Prova

    p = _prova(tmp_path, grava=False, licenca="comecou")
    p.abrir()
    assert len(p.win.pedidos) == 1 and p.grava["agora"]
    q = Prova(tmp_path / "seguinte", grava=True)
    q.abrir()
    assert q.win.pedidos == []


def test_d741_na_conta_de_testes_nada_pergunta_mesmo_depois_de_um_nao(tmp_path, monkeypatch):
    """D-741/D-736 (adaptado pela D-836): depois de um "Não" na conta do Kaique, a conta de testes não pergunta nada."""
    p = _prova(tmp_path, grava=False, licenca="disse_nao")
    p.abrir()
    monkeypatch.setenv("USERNAME", td.NOME_DA_CONTA)
    from tests.ajudante_do_atualizador import Prova

    q = Prova(tmp_path / "testes", grava=False)
    q.abrir()
    assert q.win.pedidos == []


# ---------------------------------------------------------------------------
# D-742 (Samuel, 17/11/2026: "Sim"): a janelinha "Atualizando o programa, espere um pouco..."
# ---------------------------------------------------------------------------

# A janela do Windows Forms de mentira: New-Object devolve, para os tipos do Windows Forms, um objeto que so
# anota (nenhuma janela e criada; nada aparece na tela). Os outros tipos (Size, Font) sao os de verdade.
_JANELA_DE_MENTIRA = r"""
function New-Object { param([string]$TypeName, [object[]]$ArgumentList)
  if ($TypeName -like 'System.Windows.Forms.*') {
    Write-Host ('CRIOU ' + $TypeName)
    $o = [pscustomobject]@{ Text=''; ControlBox=$true; FormBorderStyle=''; StartPosition=''; ShowInTaskbar=$true;
                            TopMost=$false; ClientSize=$null; Dock=''; TextAlign=''; Font=$null; Controls=$null }
    $c = [pscustomobject]@{}
    $c | Add-Member -MemberType ScriptMethod -Name Add -Value { param($x) Write-Host ('TEXTO ' + $x.Text) }
    $o.Controls = $c
    $o | Add-Member -MemberType ScriptMethod -Name Show -Value { Write-Host 'MOSTROU' }
    $o | Add-Member -MemberType ScriptMethod -Name Close -Value {
      Write-Host ('FECHOU ControlBox=' + $this.ControlBox + ' TopMost=' + $this.TopMost + ' Titulo=[' + $this.Text + ']') }
    return $o }
  Microsoft.PowerShell.Utility\New-Object -TypeName $TypeName -ArgumentList $ArgumentList }
"""


def _prova(tmp_path, **kw):
    """Uma abertura do programa instalado pelo caminho novo (o executor de verdade, só a borda de mentira:
    tests/ajudante_do_atualizador.py)."""
    from tests.ajudante_do_atualizador import Prova

    return Prova(tmp_path, **kw)


def test_d732_ao_abrir_o_programa_procura_a_versao_nova(tmp_path):
    """D-732 ("não, faz quando o programa é aberto") (adaptado pela D-836; era
    `test_d732_ao_abrir_o_programa_manda_o_ajudante_procurar`): abrir o programa instalado procura a versão nova, sem
    pergunta do Windows (a pasta já aceita gravação) e sem ajudante."""
    p = _prova(tmp_path)
    p.abrir()
    assert p.win.pedidos == [] and p.vp.nomes()[0] == "procurar"


def test_d732_a_janela_aberta_liga_o_aviso(tmp_path):
    """D-732 (adaptado pela D-836; era `test_d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso`): o main.py chama
    `ligar_na_janela` uma vez; ela liga a janela ao executor desta abertura, e o aviso que esperava chega."""
    from PySide6.QtWidgets import QApplication, QWidget

    from ui import aviso_de_atualizacao as aviso

    QApplication.instance() or QApplication([])
    p = _prova(tmp_path, publicar_nova=False)
    p.abrir()
    janela = QWidget()
    ponte = aviso.ligar_na_janela(janela, atual=p.atual)
    assert ponte is not None and janela._ponte_da_atualizacao is ponte
    assert p.atual._tela == ponte.receber
    assert aviso.ligar_na_janela(QWidget()) is None, "sem executor desta abertura (pelo código), nada liga"


def test_d733_com_a_senha_nada_dos_testes_vai_na_pergunta(fake, monkeypatch, tmp_path):
    """Era `test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so`. A decisão mudou (D-825, opção B: "ok"; D-834):
    a senha digitada NÃO liga os testes nesta versão, e a pergunta do Windows é a da abertura, antes da janela, só com
    os passos do preparo. Cobra o que vale hoje (D-836): com a senha, a janela da senha não chama o Windows nem os
    testes à distância; a pergunta da abertura leva só os quatro passos do preparo."""
    import ui.testes_a_distancia_ui as tdui

    monkeypatch.setattr(tdui, "perguntar_senha", lambda parent=None: "a senha do Samuel")
    tdui.primeira_vez_se_preciso(None, instalado=lambda: True, conta_de_testes=lambda: False)
    assert fake.chamadas == []
    p = _prova(tmp_path, grava=False)
    p.abrir()
    assert p.win.pedidos == [["apagar_tarefa", "instalar_visual_c", "tirar_instalacao_do_inno",
                              "dar_licenca_aos_usuarios"]]


def test_d733_reiniciar_agora_nao_pede_licenca(tmp_path):
    """D-733 ("nenhuma pergunta por atualização") (adaptado pela D-836; era
    `test_d733_reiniciar_agora_chama_o_ajudante_e_nao_pede_licenca`): o "Reiniciar agora" troca pelo Velopack, na
    conta de quem abriu, sem nenhuma pergunta do Windows (a pasta aceita gravação)."""
    from core import fases_da_atualizacao as fases
    from tests.ajudante_do_atualizador import _ate_o_aviso

    p = _ate_o_aviso(tmp_path)
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    assert "trocar" in p.vp.nomes() and p.win.pedidos == []


def test_d734_depois_a_versao_entra_ao_fechar(tmp_path):
    """Era `test_d734_depois_a_versao_entra_na_proxima_abertura_antes_da_janela`. A decisão mudou (D-769 "b", D-794,
    D-831 "a"): com "Depois", a versão entra AO FECHAR. Cobra o que vale hoje (D-836): a abertura seguinte não troca
    antes da janela; fechar com "Sim" troca."""
    from core import fases_da_atualizacao as fases
    from tests.ajudante_do_atualizador import _ate_o_aviso

    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" in p.vp.nomes()


def test_d734_a_abertura_nunca_troca_antes_da_janela(tmp_path):
    """Era `test_d734_a_linha_de_comando_sai_sem_janela_quando_a_troca_comecou`. A decisão mudou (D-769/D-794): uma
    versão baixada e esperando não é trocada na abertura (nem pelo Velopack: a troca automática na abertura fica
    desligada). Cobra o que vale hoje (D-836): abrir com uma versão já baixada mostra o aviso e não troca."""
    p = _prova(tmp_path)
    assert p.abrir() is None
    assert "trocar" not in p.vp.nomes()


def test_d734_o_aviso_diz_que_atualiza_ao_fechar(tmp_path):
    """Era `test_d734_o_aviso_diz_que_entra_na_proxima_abertura_e_fechar_nao_troca`. A decisão mudou (D-835, "B"):
    o aviso diz "Se escolher "Depois", você pode atualizar quando fechar o programa.", e fechar pergunta. Cobra o que
    vale hoje (D-836)."""
    assert atualizacao.FRASE_DA_VERSAO_NOVA.endswith(
        "Se escolher \"Depois\", você pode atualizar quando fechar o programa.")
    assert "próxima vez que você abrir" not in atualizacao.FRASE_DA_VERSAO_NOVA


def test_d742_a_janelinha_da_troca_e_a_do_velopack():
    """Era `test_d742_a_janelinha_aparece_durante_a_espera_e_some_quando_o_programa_abre` (e os outros cinco da
    janelinha nossa). A decisão mudou (D-832, "pode ser velopack, deixamos para mudar isso mais para frente"): a
    janelinha da troca é a do próprio Velopack. Cobra o que vale hoje (D-836): a janelinha nossa e o texto dela não
    existem mais no programa (a troca pede a do Velopack: `tests/test_atualizador_novo.py::test_d832_...`)."""
    assert not hasattr(atualizacao, "TEXTO_DA_JANELINHA") and not hasattr(atualizacao, "script_da_janelinha")
    programa = [RAIZ / "atualizacao.py", RAIZ / "core" / "conversa_com_o_velopack.py",
                RAIZ / "ui" / "aviso_de_atualizacao.py", RAIZ / "ui" / "brasao_girando.py"]
    for arquivo in programa:
        assert "Atualizando o programa, espere um pouco" not in arquivo.read_text(encoding="utf-8"), arquivo.name
