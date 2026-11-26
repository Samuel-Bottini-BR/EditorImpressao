"""Volta 3 do atualizador novo (24/11/2026): o que a emenda do Fable usa do mundo de fora, rodado DE VERDADE (D-767),
numa instalação de prova e em pastas de prova (nunca no programa instalado nem no ProgramData do PC).

1. O Velopack 1.2.161 de verdade (a biblioteca, sem trocar nada):
   - a volta pela pasta da última boa: o `baixar` com a PASTA de endereço (a fonte de pasta do Velopack) copia o pacote
     para `packages\\` conferindo o tamanho e a soma, SEM índice nenhum na pasta (a pasta da última boa não tem o
     `releases.win.json`) e sem a SHA1 (a assinatura do Samuel só afirma a SHA256); com a soma errada, recusa;
   - o `pendente` (`get_update_pending_restart`): o pacote mais novo esperando em `packages\\`.
2. O `icacls` de verdade (a licença que só acrescenta) numa pasta como a do registro no ProgramData, com o bilhete e o
   registro dentro: depois, Usuários modificam a pasta E os arquivos que já estavam lá (o M4). Só com
   `EDITOR_PROVA_DO_WINDOWS=1` ou no Windows do GitHub (muda licença de verdade, numa pasta de prova).
3. A recusa da pasta com um arquivo ligado a outro (um "hard link"): de verdade, sem mudar licença nenhuma.

A troca (`trocar`) NÃO roda aqui (ela abre o atualizador do Velopack, que mexe na pasta e reabre o programa): só na
prova à vista com o Samuel (D-767, D-785).
"""

from __future__ import annotations

import hashlib
import io
import os
import sys
import zipfile
from pathlib import Path

import pytest

from core import conversa_com_o_velopack as conversa

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="o Velopack e a peça do Windows só no Windows")
velopack = pytest.importorskip("velopack")
PACOTE = "EditorImpressaoPrograma"


def _nuspec(v: str) -> str:
    """O manifesto de um pacote do Velopack (o que ele lê de dentro do .nupkg)."""
    return (f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>{v}</version><title>Editor</title>'
            '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
            '</package>')


def _nupkg(v: str) -> bytes:
    """Um .nupkg de prova que o Velopack sabe ler (o manifesto dentro)."""
    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr(f"{PACOTE}.nuspec", _nuspec(v))
        z.writestr("lib/app/leia.txt", f"pacote {v}")
    return dados.getvalue()


@pytest.fixture
def instalacao(tmp_path):
    """(localizador, pasta dos pacotes) de uma instalação de prova na versão 1.1.0."""
    raiz = tmp_path / "instalado"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "current" / "sq.version").write_text(_nuspec("1.1.0"), encoding="utf-8")
    (raiz / "Update.exe").write_bytes(b"MZ")      # a biblioteca só confere que existe; nada aqui o roda
    localizador = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                 raiz / "current" / "sq.version", raiz / "current", False)
    return localizador, raiz / "packages"


def test_d844_a_volta_pela_pasta_da_ultima_boa_sem_indice_e_sem_sha1(instalacao, tmp_path):
    """D-844 (a volta pelo pacote guardado, sem internet), com a biblioteca de verdade: a pasta da última boa só tem o
    pacote (sem `releases.win.json`); o pedido vai com a SHA256 que a assinatura afirma e sem a SHA1. O Velopack copia
    o pacote para `packages\\` e confere; com uma SHA256 errada, recusa e não deixa o nome final."""
    localizador, pacotes = instalacao
    ultima_boa = tmp_path / "ultima-boa"
    ultima_boa.mkdir()
    dado = _nupkg("1.0.0")
    nome = f"{PACOTE}-1.0.0-full.nupkg"
    (ultima_boa / nome).write_bytes(dado)
    sha = hashlib.sha256(dado).hexdigest()
    errado = conversa.pacote_da_versao(PACOTE, "1.0.0", nome, "00" * 32, "", len(dado))
    with pytest.raises(conversa.ErroDoVelopack):
        conversa.baixar(str(ultima_boa), errado, localizador)
    assert not (pacotes / nome).exists()
    certo = conversa.pacote_da_versao(PACOTE, "1.0.0", nome, sha, "", len(dado))
    conversa.baixar(str(ultima_boa), certo, localizador)
    assert hashlib.sha256((pacotes / nome).read_bytes()).hexdigest() == sha
    assert (ultima_boa / nome).exists(), "o guardado continua lá (o Velopack copia, não move)"


def test_a_abertura_le_o_pacote_esperando_pelo_velopack(instalacao):
    """A emenda do Fable, A (3): "se há pacote baixado esperando (`get_update_pending_restart` do Velopack)". Sem nada:
    ""; com um pacote mais VELHO que a versão que roda (a anterior, na volta): ""; com um mais novo: a versão dele."""
    localizador, pacotes = instalacao
    assert conversa.pendente(str(pacotes), localizador) == ""
    (pacotes / f"{PACOTE}-1.0.0-full.nupkg").write_bytes(_nupkg("1.0.0"))
    assert conversa.pendente(str(pacotes), localizador) == ""
    (pacotes / f"{PACOTE}-1.2.0-full.nupkg").write_bytes(_nupkg("1.2.0"))
    assert conversa.pendente(str(pacotes), localizador) == "1.2.0"


def test_a_pasta_com_um_arquivo_ligado_a_outro_e_recusada_de_verdade(tmp_path):
    """Volta 3: a licença que só acrescenta passa para tudo o que está dentro (`/T`); um arquivo ligado a outro de
    fora da pasta receberia a licença junto. A peça acha o arquivo ligado (um "hard link" de verdade, criado aqui) e
    recusa ANTES de rodar a ferramenta (nada é mudado)."""
    from core import windows

    pasta = tmp_path / "atualizacao"
    pasta.mkdir()
    fora = tmp_path / "de-fora.txt"
    fora.write_text("x", encoding="utf-8")
    os.link(fora, pasta / "estado.json")
    antes = windows.ler_licencas(pasta)
    assert windows.ligacoes_dentro(pasta) == [str(pasta / "estado.json")]
    r = windows.dar_licenca_aos_usuarios(pasta, pasta / "estado.json")
    assert r.desfecho == windows.FALHOU and "ligado" in r.motivo
    assert windows.ler_licencas(pasta) == antes


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") != "true" and os.environ.get("EDITOR_PROVA_DO_WINDOWS") != "1",
                    reason="muda licença de verdade: só no Windows do GitHub ou com EDITOR_PROVA_DO_WINDOWS=1")
def test_m4_de_verdade_a_pasta_do_registro_com_os_arquivos_dentro(tmp_path):
    """M4 (24/11/2026), de verdade numa pasta de prova: a pasta do registro e do bilhete, com o `estado.json` e o
    `atualizacao.log` já dentro (como os que nasceram de uma abertura com licença de administrador), recebe pela MESMA
    função da peça (`dar_licenca_aos_usuarios`, o `icacls ... /grant "*S-1-5-32-545:(OI)(CI)M" /T`) a licença de
    Modificar para Usuários, e os arquivos que JÁ estavam lá também (o `/T`): a conta comum volta a gravar neles.
    Nenhuma linha antiga sumiu; rodar de novo também dá certo."""
    from core import windows

    pasta = windows.pasta_da_atualizacao_no_programdata(tmp_path / "ProgramDataDeProva")
    (pasta / "estado.json").write_text("{}", encoding="utf-8")
    (pasta / "atualizacao.log").write_text("linha\n", encoding="utf-8")
    antes = windows.ler_licencas(pasta)
    r = windows.dar_licenca_aos_usuarios(pasta, pasta / "atualizacao.log")
    assert r.deu_certo, (r.motivo, r.detalhe)
    assert windows.problemas_da_licenca_dos_usuarios(antes, windows.ler_licencas(pasta)) == []
    assert windows.usuarios_modificam(windows.ler_licencas(pasta / "estado.json"))
    assert windows.usuarios_modificam(windows.ler_licencas(pasta / "atualizacao.log"))
    assert windows.dar_licenca_aos_usuarios(pasta, pasta / "atualizacao.log").deu_certo


def test_a_pasta_do_registro_que_e_um_atalho_e_recusada(tmp_path):
    """A pasta do registro no ProgramData pode ser criada por uma conta comum antes do preparo (o ProgramData deixa):
    se ela (ou a de cima) é um atalho para outro lugar, a peça recusa antes de dar a licença."""
    import subprocess

    from core import windows

    alvo = tmp_path / "outro-lugar"
    alvo.mkdir()
    base = tmp_path / "pd"
    (base).mkdir()
    feito = subprocess.run(["cmd", "/c", "mklink", "/J", str(base / "EditorImpressao"), str(alvo)],
                           capture_output=True, text=True)
    if feito.returncode != 0:
        pytest.skip(f"não deu para criar a junção de prova: {feito.stderr}")
    with pytest.raises(OSError):
        windows.pasta_da_atualizacao_no_programdata(base)
    assert not (alvo / "atualizacao").exists()
