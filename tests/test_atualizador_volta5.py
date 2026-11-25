"""Volta 5 do atualizador novo (25/11/2026): as proteções técnicas por trás das decisões D-867 a D-871 (as provas das
decisões estão em `tests/test_decisoes_atualizacao_volta5.py`).

O que se prova aqui:
- a caixa do Windows (`core.windows.mostrar_caixa_do_windows`, D-868): não é chamada sem área de trabalho à vista (a
  linha ficaria parada esperando um OK que ninguém vê); só o OK conta como "a pessoa viu"; só a peça chama a caixa;
- a caixa que não pôde aparecer: a frase fica guardada com o mesmo nome e aparece na abertura seguinte, uma vez;
- a regra da frase guardada que deixou de ser verdade (M1) e a leitura da versão no nome da frase;
- o atualizador do Velopack conferido num lugar só (M2).

Cada proteção tem o teste que falha quando ela é desligada (D-811, D-827): a prova é a rodada de mutações
`relatorios/atualizador-novo/volta5-provas/mutacoes_volta5.py`. Os testes que cobram peças novas (a caixa, a regra
da frase velha) falham no código de antes por não existirem lá (a saída: `volta5-testes-no-codigo-antigo.txt`).
Nada aqui mostra caixa nenhuma na tela: a caixa de verdade só roda nas provas, numa área de trabalho separada.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

import atualizacao
from core import fases_da_atualizacao as fases
from core import windows
from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, NOVA, PUBLICA, Prova, WindowsFalso,  # noqa: F401
                                          programdata_de_prova)

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent
TEXTO_D868 = "A versão nova não funcionou. Não desinstale nada. Avise o Samuel."


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado, o registro e as frases vistas numa pasta de prova."""


# ---------------------------------------------------------------------------------------------------------------------
# A caixa do Windows, na peça
# ---------------------------------------------------------------------------------------------------------------------

class _User32DeMentira:
    """Só o `MessageBoxW`, que devolve o que o teste manda e anota que foi chamado."""

    def __init__(self, volta: int):
        self.volta, self.chamadas = volta, []

    def MessageBoxW(self, dona, texto, titulo, tipo):  # noqa: N802 - o nome da função do Windows
        self.chamadas.append((dona, texto, titulo, tipo))
        return self.volta


@pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")
def test_a_caixa_nao_e_chamada_sem_area_de_trabalho_a_vista(monkeypatch):
    """Sem área de trabalho à vista (o programa aberto por uma conexão de longe; "Interactive Services": a estação sem
    WSF_VISIBLE), ou sem saber, a peça NÃO chama a caixa e devolve FALHOU: uma caixa ali ninguém vê, e a linha ficaria
    parada para sempre. Desligar essa conferência faz este teste falhar."""
    falsa = _User32DeMentira(volta=1)
    monkeypatch.setattr(windows, "_win", lambda: type("W", (), {"user32": falsa})())
    for a_vista in (False, None):
        monkeypatch.setattr(windows, "area_de_trabalho_a_vista", lambda a=a_vista: a)
        r = windows.mostrar_caixa_do_windows("Atualização", TEXTO_D868)
        assert r.desfecho == windows.FALHOU and "área de trabalho" in r.motivo
    assert falsa.chamadas == []


@pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")
@pytest.mark.parametrize("volta, deu_certo", [(1, True), (0, False), (2, False)])
def test_a_caixa_so_conta_o_ok(monkeypatch, volta, deu_certo):
    """Só a volta IDOK (1) é "a pessoa viu e clicou OK"; zero (o Windows não mostrou) e qualquer outra são FALHOU
    (§11.12 ponto 2: nada dá como feito o que não conferiu). A caixa vai sem janela dona, com só o OK, o ícone "i",
    em cima e pedindo a frente; título e texto como vieram."""
    falsa = _User32DeMentira(volta=volta)
    monkeypatch.setattr(windows, "_win", lambda: type("W", (), {"user32": falsa})())
    monkeypatch.setattr(windows, "area_de_trabalho_a_vista", lambda: True)
    r = windows.mostrar_caixa_do_windows("Atualização", TEXTO_D868)
    assert r.deu_certo is deu_certo
    assert falsa.chamadas == [(None, TEXTO_D868, "Atualização", 0x00000000 | 0x40 | 0x10000 | 0x40000)]


@pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")
def test_a_area_de_trabalho_a_vista_le_o_windows_de_verdade():
    """A leitura de verdade (GetProcessWindowStation + GetUserObjectInformationW) responde sem mostrar nada: True,
    False ou None. Rodada num processo à parte, para não depender do que o processo dos testes já carregou."""
    r = subprocess.run([sys.executable, "-c", "from core import windows; print(windows.area_de_trabalho_a_vista())"],
                       capture_output=True, text=True, cwd=str(RAIZ_DO_REPOSITORIO), timeout=60)
    assert r.returncode == 0 and r.stdout.strip() in ("True", "False", "None"), r.stderr


def test_so_a_peca_do_windows_chama_a_caixa():
    """§11.12 ponto 1 (uma peça só para cada conversa com o Windows) e o pedido da gerente ("Ninguém mais chama
    `MessageBoxW` por conta própria"): no programa, o nome `MessageBoxW` só aparece no código de `core/windows.py`."""
    saida = subprocess.run(["git", "-C", str(RAIZ_DO_REPOSITORIO), "ls-files", "*.py"], capture_output=True,
                           text=True, check=True).stdout.split()
    fora = ("tests/", "relatorios/", ".claude/", "docs/", "memoria/", "regras_dos_agentes/", "terceiros/", "velhos/")
    achados = []
    for arq in saida:
        if arq.startswith(fora) or arq == "core/windows.py":
            continue
        try:
            arvore = ast.parse((RAIZ_DO_REPOSITORIO / arq).read_text(encoding="utf-8-sig"))
        except (OSError, SyntaxError, ValueError):
            continue
        for no in ast.walk(arvore):
            nome = no.attr if isinstance(no, ast.Attribute) else no.id if isinstance(no, ast.Name) else None
            if nome in ("MessageBoxW", "MessageBoxA", "MessageBox") or (
                    isinstance(no, ast.Constant) and isinstance(no.value, str) and "MessageBoxW" == no.value):
                achados.append((arq, no.lineno))
    assert achados == []


# ---------------------------------------------------------------------------------------------------------------------
# A caixa que não pôde aparecer
# ---------------------------------------------------------------------------------------------------------------------

class _Win(WindowsFalso):
    """A caixa do Windows de mentira (anota; `aparece` diz se a pessoa vê e clica OK)."""

    def __init__(self, aparece: bool, **k):
        super().__init__(**k)
        self.caixas, self.aparece = [], aparece

    def mostrar_caixa_do_windows(self, titulo, texto):
        self.caixas.append((titulo, texto))
        return windows.Resposta(windows.DEU_CERTO if self.aparece else windows.FALHOU, "de prova")


def _abrir(p: Prova, aparece: bool, teste=(False, "de prova"), argumentos=()):
    win = _Win(aparece, pasta_de_troca=p.raiz.parent / "troca")
    a = atualizacao.Atualizacao(
        windows=win, velopack=p.vp, raiz=p.raiz, fonte=p.atual.fonte, por_tras=lambda trabalho: trabalho(),
        pasta_grava=lambda raiz: True, garantir_motor=lambda: True, motor_no_lugar=lambda m=None: True,
        teste=lambda: teste, chave_publica=PUBLICA)
    return win, a.abrir(list(argumentos))


def test_a_frase_que_a_caixa_nao_mostrou_fica_para_a_proxima_abertura(tmp_path):
    """Pedido da gerente ("Diga o que acontece se a caixa não puder aparecer") e §11.12 ponto 2: a caixa do Windows
    que não apareceu (sem área de trabalho à vista) não conta como vista: a frase vai para o bilhete com o MESMO nome,
    o registro diz por quê, e o programa abre assim mesmo. A abertura seguinte, com a tela à vista, mostra a caixa uma
    vez; a outra depois, não. Desligar a guarda (ou marcar vista sem o OK) faz este teste falhar."""
    p = Prova(tmp_path, publicar_nova=False)
    p.pacote_em_packages(ATUAL)
    win, saida = _abrir(p, aparece=False, argumentos=(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL))
    assert saida is None and win.caixas == [("Atualização", TEXTO_D868)]
    frase = atualizacao.ler_estado().get("frase") or {}
    assert (frase.get("tipo"), frase.get("nome")) == ("reprovada", f"reprovada-{ATUAL}")
    assert f"reprovada-{ATUAL}" not in atualizacao.ler_vistos()
    assert "não apareceu" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    win2, _ = _abrir(p, aparece=True)
    assert win2.caixas == [("Atualização", TEXTO_D868)]
    win3, _ = _abrir(p, aparece=True)
    assert win3.caixas == []


# ---------------------------------------------------------------------------------------------------------------------
# A frase guardada que deixou de ser verdade (M1), na regra
# ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("tipo, nome, roda, vale", [
    ("nao_deu_agora", "nao_deu_agora-1.2.0-2026-11-25T10:00:00", "1.1.0", True),    # a troca ainda não aconteceu
    ("nao_deu_agora", "nao_deu_agora-1.2.0-2026-11-25T10:00:00", "1.2.0", False),   # aconteceu depois (M1)
    ("nao_deu_agora", "nao_deu_agora-1.2.0-2026-11-25T10:00:00", "1.3.0", False),
    ("recusada", "recusada-1.2.0-2026-11-25T10:00:00", "1.2.0", False),
    ("troca", "troca-1.2.0-2026-11-25T10:00:00", "1.1.0", True),
    ("reprovada", "reprovada-1.2.0-2026-11-25T10:00:00", "1.2.0", True),           # fala da versão que roda
    ("reprovada", "reprovada-1.2.0", "1.3.0", False),                              # já veio uma versão por cima
    ("nao_deu_agora", "um-nome-de-outro-jeito", "9.9.9", True),                    # sem versão: na dúvida, aparece
])
def test_m1_a_frase_guardada_so_aparece_enquanto_e_verdade(tipo, nome, roda, vale):
    """M1 do quarto "quem tenta quebrar" (D-870), a regra num lugar só (`fases._frase_guardada_vale`, pela abertura):
    a frase sobre uma troca para a versão X só aparece enquanto a que roda é mais velha que X; a da reprovada, enquanto
    a que roda não é mais nova que ela; sem versão no nome, aparece."""
    e = fases.Abriu(instalado=True, conta_de_testes=False, portatil=False, pasta_grava=True, versao=roda,
                    ultima_boa=roda, frase_guardada=(tipo, nome, ""))
    _, efeitos = fases.proxima_fase(fases.Estado(), e)
    mostradas = [ef.nome for ef in efeitos if isinstance(ef, fases.MostrarFalha)]
    assert mostradas == ([nome] if vale else [])


def test_a_versao_da_frase_e_lida_do_nome_que_o_programa_escreve():
    """O par de `id_da_falha` (lugar único do nome): a versão volta do nome com a hora; nome de outro jeito, ""."""
    nome = f"{fases.id_da_falha('nao_deu_agora', '1.2.0')}-2026-11-25T10:00:00"
    assert fases.versao_da_falha("nao_deu_agora", nome) == "1.2.0"
    assert fases.versao_da_falha("reprovada", "reprovada-1.2.0") == "1.2.0"
    assert fases.versao_da_falha("troca", "nao_deu_agora-1.2.0") == ""
    assert fases.versao_da_falha("troca", "troca-x.y") == ""


# ---------------------------------------------------------------------------------------------------------------------
# O atualizador do Velopack conferido num lugar só (M2)
# ---------------------------------------------------------------------------------------------------------------------

def test_m2_o_update_exe_e_conferido_por_uma_funcao_so():
    """§11.12 (um dado lido por uma função só): no executor, só `tem_o_atualizador` olha o `Update.exe`; a conferência
    da troca e o pedido da troca a chamam."""
    arvore = ast.parse((RAIZ_DO_REPOSITORIO / "atualizacao.py").read_text(encoding="utf-8"))
    quem_olha, quem_chama = set(), set()
    for funcao in ast.walk(arvore):
        if not isinstance(funcao, ast.FunctionDef):
            continue
        for no in ast.walk(funcao):
            if isinstance(no, ast.Attribute) and no.attr == "NOME_DO_ATUALIZADOR_DO_VELOPACK":
                quem_olha.add(funcao.name)
            if isinstance(no, ast.Constant) and no.value == "Update.exe":
                quem_olha.add(funcao.name)
            if isinstance(no, ast.Call) and getattr(no.func, "id", "") == "tem_o_atualizador":
                quem_chama.add(funcao.name)
    assert quem_olha == {"tem_o_atualizador"}
    assert quem_chama == {"conferencia_da_troca", "trocar_para"}


def test_m2_o_atualizador_no_lugar_e_o_da_raiz(tmp_path):
    """O que a biblioteca exige (`locator.rs` 114-117 e 372: `<raiz>\\Update.exe` com a raiz aceitando gravação)."""
    assert atualizacao.tem_o_atualizador(tmp_path) is False
    (tmp_path / "Update.exe").write_bytes(b"MZ")
    assert atualizacao.tem_o_atualizador(tmp_path) is True
    (tmp_path / "Update.exe").unlink()
    (tmp_path / "Update.exe").mkdir()                               # uma pasta com o nome não é o atualizador
    assert atualizacao.tem_o_atualizador(tmp_path) is False
