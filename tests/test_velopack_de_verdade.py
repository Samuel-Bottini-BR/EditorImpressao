"""A peça do Velopack (core/conversa_com_o_velopack.py) com a BIBLIOTECA DE VERDADE, sem trocar nada (atualizador novo,
23/11/2026; plano, seção 11: "A biblioteca do Velopack de verdade").

Uma instalação de prova numa pasta (o manifesto `current\\sq.version`, a pasta `packages\\`) e uma fonte de pasta com
duas versões publicadas (o `releases.win.json` e os pacotes). O Velopack 1.2.161 de verdade: `procurar` acha a nova;
o pedido da anterior (a volta) é montado pela peça, sem rede, e BAIXADO para a pasta de prova com o tamanho e a soma
conferidos pelo próprio Velopack; um pedido com a soma errada é recusado por ele. A troca (`trocar`) NÃO roda aqui: ela
abre o atualizador do Velopack, que mexe na pasta e reabre o programa; só na prova à vista com o Samuel (D-767, D-785).

O que isto prova: que a peça monta o `UpdateInfo`/`VelopackAsset` do jeito que a biblioteca aceita, e que a biblioteca
confere o que baixa (o que a volta para a anterior usa). O que NÃO prova: o GitHub (a fonte aqui é uma pasta), a
troca, a janelinha.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core import conversa_com_o_velopack as conversa

velopack = pytest.importorskip("velopack")
PACOTE = "EditorImpressaoPrograma"
NUSPEC = ('<?xml version="1.0"?><package><metadata><id>EditorImpressaoPrograma</id><version>1.1.0</version>'
          '<title>Editor</title><authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe>'
          '</metadata></package>')


@pytest.fixture
def instalacao(tmp_path):
    """(o localizador da instalação de prova, a pasta dos pacotes, a fonte, os dados de cada versão publicada)."""
    raiz = tmp_path / "instalado"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "current" / "sq.version").write_text(NUSPEC, encoding="utf-8")
    # O atualizador do Velopack de mentira: a biblioteca só confere que o arquivo existe ("not properly installed"
    # sem ele); nada aqui o roda (a troca não é chamada).
    (raiz / "Update.exe").write_bytes(b"MZ")
    fonte = tmp_path / "fonte"
    fonte.mkdir()
    publicadas = {}
    for v, dado in (("1.0.0", b"anterior" * 100), ("1.2.0", b"nova" * 100)):
        nome = f"{PACOTE}-{v}-full.nupkg"
        (fonte / nome).write_bytes(dado)
        publicadas[v] = {"PackageId": PACOTE, "Version": v, "Type": "Full", "FileName": nome,
                         "SHA1": hashlib.sha1(dado).hexdigest(), "SHA256": hashlib.sha256(dado).hexdigest(),
                         "Size": len(dado), "NotesMarkdown": "", "NotesHtml": ""}
    (fonte / "releases.win.json").write_text(json.dumps({"Assets": list(publicadas.values())}), encoding="utf-8")
    localizador = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                 raiz / "current" / "sq.version", raiz / "current", False)
    return localizador, raiz / "packages", str(fonte), publicadas


def test_procurar_acha_a_versao_nova_com_a_soma_do_indice(instalacao):
    """`procurar` pela biblioteca de verdade: na instalação 1.1.0, a publicada mais nova é a 1.2.0, com o nome do
    arquivo, a soma e o tamanho do índice publicado (o que a assinatura do Samuel tem de afirmar)."""
    localizador, _, fonte, publicadas = instalacao
    achada = conversa.procurar(fonte, localizador)
    assert (achada.pacote, achada.versao, achada.arquivo) == (PACOTE, "1.2.0", publicadas["1.2.0"]["FileName"])
    assert achada.sha256.lower() == publicadas["1.2.0"]["SHA256"] and achada.tamanho == publicadas["1.2.0"]["Size"]


def test_a_volta_baixa_a_anterior_e_o_velopack_confere_a_soma(instalacao):
    """D-718 (a volta pela biblioteca): o pedido da anterior montado pela peça (`pacote_da_versao`, sem rede) é aceito
    pela biblioteca, e o pacote chega em `packages\\` inteiro. Com a soma errada, o próprio Velopack recusa e o pacote
    não fica com o nome final (fica o `.partial`)."""
    localizador, pacotes, fonte, publicadas = instalacao
    a = publicadas["1.0.0"]
    v = conversa.pacote_da_versao(PACOTE, "1.0.0", a["FileName"], a["SHA256"], a["SHA1"], a["Size"])
    conversa.baixar(fonte, v, localizador)
    baixado = pacotes / a["FileName"]
    assert hashlib.sha256(baixado.read_bytes()).hexdigest() == a["SHA256"]
    baixado.unlink()
    errado = conversa.pacote_da_versao(PACOTE, "1.0.0", a["FileName"], "00" * 32, a["SHA1"], a["Size"])
    with pytest.raises(conversa.ErroDoVelopack):
        conversa.baixar(fonte, errado, localizador)
    assert not baixado.exists()


def test_sem_a_fonte_procurar_levanta_o_erro_da_peca(instalacao, tmp_path):
    """Sem a fonte (como sem internet), a peça levanta o erro dela, que o executor transforma em "não procurou"."""
    localizador, _, _, _ = instalacao
    with pytest.raises(conversa.ErroDoVelopack):
        conversa.procurar(str(tmp_path / "nao-existe"), localizador)
