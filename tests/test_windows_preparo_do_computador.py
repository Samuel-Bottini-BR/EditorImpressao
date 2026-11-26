"""A peça do Windows no atualizador novo (23/11/2026): os três passos do preparo, a licença que só acrescenta (D-837),
as duas metades do pedido de licença (D-806, D-834) e a lista de processos sem a família deste.

O que roda de verdade aqui: a leitura da lista de processos (só lê) e as regras puras. O que muda licença no Windows
(`dar_licenca_aos_usuarios`) roda de verdade só numa pasta de prova e só onde o pedido manda: no Windows do GitHub
(máquina jogada fora) ou com `EDITOR_PROVA_DO_WINDOWS=1`; nunca na pasta do programa de verdade. A pergunta do Windows
nunca é feita aqui (ela abriria na tela): as provas dela são as das regras e a prova à vista com o Samuel.
"""

from __future__ import annotations

import os
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

import atualizacao
from core import windows

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")

U, A, S = windows.SID_USUARIOS, windows.SID_ADMINISTRADORES, windows.SID_SISTEMA


def L(sid, mascara, herdada=True, objetos=True, pastas=True, tipo="permite", so_dentro=False):
    return windows.Licenca(sid, "", tipo, mascara, herdada, so_dentro, objetos, pastas)


ANTES = windows.Licencas("C:\\x", S, "", False, False, (L(S, 0x1F01FF), L(A, 0x1F01FF), L(U, 0x1200A9)))
DEPOIS_CERTO = replace(ANTES, lista=ANTES.lista + (L(U, 0x1301BF, herdada=False),))


# ---------------------------------------------------------------------------------------------------------------------
# A licença que só acrescenta (D-837)
# ---------------------------------------------------------------------------------------------------------------------

def test_d837_so_acrescentar_usuarios_modificar_confere():
    """O que o passo exige depois do `icacls`: tudo o que havia continua, o dono e a herança são os mesmos, e há uma
    linha própria de Usuários com Modificar passando para dentro."""
    assert windows.problemas_da_licenca_dos_usuarios(ANTES, DEPOIS_CERTO) == []


@pytest.mark.parametrize("depois, trecho", [
    (replace(DEPOIS_CERTO, protegida=True), "herança"),
    (replace(DEPOIS_CERTO, dono=U), "dono"),
    (replace(DEPOIS_CERTO, lista=DEPOIS_CERTO.lista[1:]), "sumiu"),
    (ANTES, "não ficou"),
    (replace(ANTES, lista=ANTES.lista + (L(U, 0x1301BF, herdada=False, pastas=False),)), "não ficou"),
    (replace(ANTES, lista=ANTES.lista + (L(U, 0x1301BF, herdada=False, so_dentro=True),)), "não ficou"),
    (replace(ANTES, lista=ANTES.lista + (L(U, 0x1200A9, herdada=False),)), "não ficou"),
    (replace(DEPOIS_CERTO, sem_lista=True, lista=()), "sem lista"),
])
def test_d837_o_que_tira_ou_nao_acrescenta_e_acusado(depois, trecho):
    """Cada jeito de o passo não cumprir "só acrescentar" vira problema (e o passo FALHA): cortar a herança (o defeito
    de 18/11), trocar o dono, sumir uma linha, não acrescentar, acrescentar sem passar para as pastas ou só para dentro,
    acrescentar menos que Modificar, tirar a lista inteira."""
    problemas = windows.problemas_da_licenca_dos_usuarios(ANTES, depois)
    assert problemas and any(trecho in p for p in problemas), problemas


def test_d837_a_linha_juntada_pelo_windows_com_uma_igual_conta_como_continuando():
    """Quando já havia uma linha própria igual de Usuários (uma reinstalação), o Windows a junta com a nova: ela
    "cresce" e não conta como sumida."""
    antes = replace(ANTES, lista=ANTES.lista + (L(U, 0x1200A9, herdada=False),))
    depois = replace(ANTES, lista=ANTES.lista + (L(U, 0x1301BF, herdada=False),))
    assert windows.problemas_da_licenca_dos_usuarios(antes, depois) == []


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") != "true" and os.environ.get("EDITOR_PROVA_DO_WINDOWS") != "1",
                    reason="muda licença de verdade: só no Windows do GitHub ou com EDITOR_PROVA_DO_WINDOWS=1")
def test_d837_de_verdade_numa_pasta_de_prova(tmp_path):
    """O passo de verdade (o `icacls ... /grant "*S-1-5-32-545:(OI)(CI)M" /T` da peça), numa pasta de prova com o
    desenho da instalação (`current\\sq.version` dentro): dá certo, a raiz e o arquivo de dentro passam a deixar
    Usuários modificar, nenhuma linha antiga sumiu, a herança e o dono não mudaram. Rodar de novo também dá certo
    (só acrescenta)."""
    raiz = tmp_path / "EditorImpressaoProva"
    (raiz / "current").mkdir(parents=True)
    (raiz / "current" / "sq.version").write_text("<versao/>", encoding="utf-8")
    antes = windows.ler_licencas(raiz)
    r = windows.dar_licenca_aos_usuarios(raiz)
    assert r.deu_certo, (r.motivo, r.detalhe)
    depois = windows.ler_licencas(raiz)
    assert windows.problemas_da_licenca_dos_usuarios(antes, depois) == []
    assert windows.usuarios_modificam(windows.ler_licencas(raiz / "current" / "sq.version"))
    assert windows.dar_licenca_aos_usuarios(raiz).deu_certo


def test_d837_a_pasta_que_nao_existe_falha_sem_rodar_nada(tmp_path):
    """Sem a pasta (ou com um atalho no lugar), FALHOU antes de rodar qualquer coisa."""
    r = windows.dar_licenca_aos_usuarios(tmp_path / "nao-existe")
    assert r.desfecho == windows.FALHOU


# ---------------------------------------------------------------------------------------------------------------------
# Os passos não aceitam dado nenhum, e só rodam no programa instalado
# ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("passo", [windows.passo_instalar_visual_c(), windows.passo_tirar_instalacao_do_inno(),
                                   windows.passo_dar_licenca_aos_usuarios()])
def test_os_passos_do_preparo_nao_aceitam_dados_no_pedido(passo):
    """O lado com licença calcula a pasta e o instalador sozinho: um aviso que trouxesse uma pasta ou um programa
    (trocado por outra conta) é recusado antes de qualquer coisa."""
    certo = asdict(passo)
    assert windows.problemas_do_passo(certo) == []
    errado = {**certo, "dados": {"raiz": "C:\\Windows"}}
    assert windows.problemas_do_passo(errado)


def test_a_raiz_da_instalacao_so_dentro_de_arquivos_de_programas(tmp_path, monkeypatch):
    """`raiz_da_instalacao`: o programa em `<raiz>\\current` com o manifesto do Velopack, e a raiz dentro de Arquivos de
    Programas (perguntado ao Windows). Fora disso, recusa."""
    programas = tmp_path / "Programas"
    exe = programas / "EditorImpressaoPrograma" / "current" / "EditorImpressao.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"MZ")
    with pytest.raises(OSError):
        windows.raiz_da_instalacao(exe)                      # sem o manifesto
    (exe.parent / "sq.version").write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        windows.raiz_da_instalacao(exe)                      # fora de Arquivos de Programas
    monkeypatch.setattr(windows, "pasta_de_programas", lambda: programas)
    assert windows.raiz_da_instalacao(exe) == exe.parent.parent.resolve()
    outro = programas / "x" / "outro" / "EditorImpressao.exe"
    outro.parent.mkdir(parents=True)
    with pytest.raises(OSError):
        windows.raiz_da_instalacao(outro)                    # não está numa pasta current
    with pytest.raises(OSError):
        windows.raiz_da_instalacao()                         # pelo código (é o que os três passos chamam antes)


def test_o_visual_c_confere_lendo_de_novo_depois_de_instalar(tmp_path, monkeypatch):
    """D-727/D-749: o instalador do Visual C++ que termina com 0 mas não deixa a versão no registro conta como NÃO
    instalado; o que deixa, como instalado; sem precisar, nem roda."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    pasta = tmp_path / "current"
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA).mkdir(parents=True)
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ")
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_VERSAO).write_text("14.44.35211.0")
    rodou = []
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None,
                                                   rodar=lambda c, t: rodou.append(c) or (0, "")) is False
    lidas = iter([None, (14, 44, 35211)])
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: next(lidas), rodar=lambda c, t: (0, "")) is True
    rodou.clear()
    assert atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: (14, 50, 0),
                                                   rodar=lambda c, t: rodou.append(c) or (0, "")) is True
    assert rodou == []


def test_o_inno_antigo_so_conta_como_tirado_quando_a_chave_some(tmp_path, monkeypatch):
    """D-723: a instalação antiga só sai como "tirada" quando a chave dela sumiu do registro (o desinstalador do Inno
    continua numa cópia dele depois de sair: a conferência espera); se a chave fica, FALHOU. Sem instalação antiga, ou
    com um caminho que não parece seguro, dá certo sem tirar (como antes)."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    antiga = tmp_path / "Antiga"
    chave = {"UninstallString": str(antiga / "unins000.exe"), "InstallLocation": str(antiga)}
    assert windows.tirar_instalacao_do_inno(tmp_path / "nova", ler=lambda: None).deu_certo
    insegura = {"UninstallString": str(tmp_path / "x" / "unins000.exe"), "InstallLocation": str(antiga)}
    r = windows.tirar_instalacao_do_inno(tmp_path / "nova", ler=lambda: insegura)
    assert r.deu_certo and "de propósito" in r.motivo
    leituras = iter([chave, chave, chave, None])
    assert windows.tirar_instalacao_do_inno(tmp_path / "nova", ler=lambda: next(leituras), esperar_s=30).deu_certo
    r = windows.tirar_instalacao_do_inno(tmp_path / "nova", ler=lambda: chave, esperar_s=0)
    assert r.desfecho == windows.FALHOU


# ---------------------------------------------------------------------------------------------------------------------
# As duas metades do pedido de licença, e a lista de processos
# ---------------------------------------------------------------------------------------------------------------------

def test_o_pedido_errado_volta_na_hora_sem_perguntar():
    """`comecar_pedido_de_licenca` com um passo que não existe, ou sem passos, ou sem o programa: volta logo, sem
    perguntar ao Windows, com FALHOU; `esperar` devolve a mesma resposta, sempre."""
    for passos, programa in (([windows.Passo("formatar_o_disco", "x", {})], None), ([], None),
                             ([windows.passo_instalar_visual_c()], ["C:\\nao\\existe\\EditorImpressao.exe"])):
        pedido = windows.comecar_pedido_de_licenca(passos, programa=programa)
        assert not pedido.comecou
        r = pedido.esperar()
        assert r.desfecho == windows.FALHOU and pedido.esperar() is r


def test_a_familia_deste_processo_fica_de_fora():
    """A conta da família (os processos que este abriu, e os que esses abriram) e a lista de verdade do Windows:
    este processo roda de dentro da pasta do Python; com `menos_a_familia_de`, ele some da lista."""
    assert windows.familia_de(1, {2: 1, 3: 2, 4: 9, 1: 0}) == {1, 2, 3}
    pasta = Path(sys.base_prefix).resolve()          # o Python de verdade (o .venv só tem um lançador)
    eu = windows.numero_deste_processo()
    com = windows.programas_rodando_de(pasta)
    sem = windows.programas_rodando_de(pasta, menos_a_familia_de=eu)
    assert com is not None and sem is not None
    assert eu in {pid for pid, _ in com} and eu not in {pid for pid, _ in sem}
