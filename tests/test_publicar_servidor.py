"""Testes do servidor das versões de prova (`servidor_das_versoes.py`; plano da parte do Windows, peça 10b; D-773).

Rodam o servidor DE VERDADE (HTTP em 127.0.0.1, numa porta livre que o Windows escolhe) e pedem como o programa do
Kaique pede (o Velopack 1.2.161 com um endereço http://: `releases.win.json?localVersion=...` e depois o arquivo pelo
nome). A pasta servida é montada pelo próprio destino do publicar (`DestinoPasta`), para os dois usarem o mesmo
desenho. A janela é aberta fora da tela (QT_QPA_PLATFORM=offscreen): a prova à vista é da gerente com o Samuel.

Seguro mexer: acrescentar casos.
"""

from __future__ import annotations

import http.client
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import publicar_versao_kaique as pub  # noqa: E402
import servidor_das_versoes as srv  # noqa: E402


def _publicar_na_pasta(pasta: Path, etiqueta: str, arquivos: dict[str, bytes], liberar: bool = True) -> None:
    """Põe uma publicação na pasta pelo destino do publicar (rascunho, enviar, liberar)."""
    destino = pub.DestinoPasta(pasta)
    destino.criar_rascunho(etiqueta, "t", "n")
    for nome, dados in arquivos.items():
        arquivo = pasta.parent / "envio" / nome
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_bytes(dados)
        destino.enviar(etiqueta, arquivo)
    if liberar:
        destino.liberar(etiqueta)


def _indice(versao: str, nome: str) -> bytes:
    """Um releases.win.json com uma versao (o formato que o vpk grava)."""
    return json.dumps({"Assets": [{"PackageId": "P", "Version": versao, "Type": "Full", "FileName": nome,
                                   "SHA256": "AA", "Size": 1}]}).encode()


@pytest.fixture
def servidor(tmp_path):
    """Uma pasta com duas versões liberadas, um rascunho e o motor; o servidor de verdade atendendo nela."""
    pasta = tmp_path / "versoes"
    _publicar_na_pasta(pasta, "v1.0.0", {"P-1.0.0-full.nupkg": b"pacote 1.0.0", "releases.win.json": _indice(
        "1.0.0", "P-1.0.0-full.nupkg"), "P-1.0.0.assinatura": b"assinatura 1.0.0"})
    _publicar_na_pasta(pasta, "v1.10.0", {"P-1.10.0-full.nupkg": b"pacote 1.10.0", "releases.win.json": _indice(
        "1.10.0", "P-1.10.0-full.nupkg")})
    _publicar_na_pasta(pasta, "v2.0.0", {"P-2.0.0-full.nupkg": b"rascunho", "releases.win.json": _indice(
        "2.0.0", "P-2.0.0-full.nupkg")}, liberar=False)
    _publicar_na_pasta(pasta, "motor-kraken-1", {"motor-kraken-1.zip": os.urandom(2 * 1024 * 1024)})
    linhas: list[str] = []
    s = srv.Servidor(pasta, porta=0, dizer=linhas.append)
    s.iniciar()
    s.linhas = linhas
    yield s
    s.fechar()


def _pedir(s: srv.Servidor, caminho: str) -> tuple[int, bytes]:
    """Pede ao servidor como um cliente comum: (codigo, o que chegou)."""
    try:
        with urllib.request.urlopen(s.endereco + caminho, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as erro:
        return erro.code, b""


def _tem_linha(s: srv.Servidor, trecho: str) -> bool:
    """A linha aparece (o servidor escreve a linha de "entregue" depois de enviar: espera um pouco)."""
    for _ in range(40):
        if any(trecho in linha for linha in s.linhas):
            return True
        time.sleep(0.05)
    return False


def test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho(servidor):
    """D-773 ("A"): o servidor faz o papel do GitHub: o índice que o programa pede (com a pergunta do Velopack) junta
    as versões liberadas, a mais nova primeiro (1.10.0 antes de 1.0.0), e o rascunho não aparece."""
    codigo, dados = _pedir(servidor, "releases.win.json?localVersion=1.0.0&id=P&stagingId=x")
    assert codigo == 200
    versoes = [a["Version"] for a in json.loads(dados)["Assets"]]
    assert versoes == ["1.10.0", "1.0.0"]
    assert _tem_linha(servidor, "releases.win.json: entregue")


def test_os_arquivos_das_versoes_liberadas_sao_entregues_inteiros(servidor):
    """O pacote, a assinatura e o arquivo do motor saem pelo nome, iguais ao que o publicar pôs na pasta."""
    assert _pedir(servidor, "P-1.0.0-full.nupkg") == (200, b"pacote 1.0.0")
    assert _pedir(servidor, "P-1.0.0.assinatura") == (200, b"assinatura 1.0.0")
    codigo, dados = _pedir(servidor, "motor-kraken-1.zip")
    original = (servidor.versoes.pasta / "motor-kraken-1" / "motor-kraken-1.zip").read_bytes()
    assert codigo == 200 and dados == original
    assert _tem_linha(servidor, "motor-kraken-1.zip: entregue inteiro")


@pytest.mark.parametrize("caminho", ["P-2.0.0-full.nupkg", "../versoes/v1.0.0/P-1.0.0-full.nupkg",
                                     "%2e%2e/x", "v1.0.0/P-1.0.0-full.nupkg", ".rascunho-v2.0.0",
                                     "nao-existe.nupkg", "C:%5CWindows%5Cwin.ini"])
def test_o_que_nao_esta_numa_versao_liberada_e_recusado(servidor, caminho):
    """O rascunho, o que sai da pasta e o que não existe: 404, com a linha na janela."""
    assert _pedir(servidor, caminho)[0] == 404
    assert _tem_linha(servidor, "não existe aqui (404)")


def test_d773_fechar_e_a_internet_caindo_no_meio_do_download(tmp_path):
    """D-773 ("fechar a janela prova a internet caindo no meio"): com o envio lento, fechar o servidor no meio corta
    o download (quem baixa recebe menos do que o tamanho anunciado), e a linha diz "CORTADO"; depois, nada atende."""
    pasta = tmp_path / "versoes"
    grande = os.urandom(3 * 1024 * 1024)
    _publicar_na_pasta(pasta, "motor-kraken-1", {"motor-kraken-1.zip": grande})
    linhas: list[str] = []
    s = srv.Servidor(pasta, porta=0, limite_kb_s=256, dizer=linhas.append)
    s.iniciar()
    recebido = {}

    def baixar() -> None:
        """Baixa como um cliente comum e anota quanto chegou e se deu erro."""
        porta = int(s.endereco.rstrip("/").rsplit(":", 1)[1])
        conexao = http.client.HTTPConnection(srv.ENDERECO, porta, timeout=20)
        conexao.request("GET", "/motor-kraken-1.zip")
        resposta = conexao.getresponse()
        recebido["anunciado"] = int(resposta.getheader("Content-Length"))
        dados = b""
        try:
            while pedaco := resposta.read(32 * 1024):
                dados += pedaco
        except (http.client.IncompleteRead, ConnectionError, OSError) as erro:
            recebido["erro"] = erro.__class__.__name__
        recebido["bytes"] = len(dados)

    fio = threading.Thread(target=baixar)
    fio.start()
    time.sleep(1.5)
    s.fechar()
    fio.join(30)
    assert not fio.is_alive()
    assert recebido["anunciado"] == len(grande)
    assert recebido["bytes"] < len(grande), "o download tinha de ser cortado no meio"
    for _ in range(50):
        if any("CORTADO no meio" in linha for linha in linhas):
            break
        time.sleep(0.1)
    assert any("CORTADO no meio" in linha for linha in linhas), linhas
    with pytest.raises(OSError):
        urllib.request.urlopen(s.endereco + "motor-kraken-1.zip", timeout=3)


def test_a_porta_ocupada_vira_frase_e_a_janela_diz_que_nao_serve(servidor, tmp_path, monkeypatch):
    """Porta ocupada: o segundo servidor não abre (OSError) e a janela diz "NÃO ESTÁ SERVINDO"; fechar a janela fecha o
    servidor. A janela é desenhada fora da tela (offscreen)."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    app = QApplication.instance() or QApplication([])
    porta = int(servidor.endereco.rstrip("/").rsplit(":", 1)[1])
    outro = srv.Servidor(servidor.versoes.pasta, porta=porta, dizer=lambda t: None)
    with pytest.raises(OSError):
        outro.iniciar()
    janela = srv.montar_janela(outro, None, "a porta está ocupada")
    textos = " ".join(r.text() for r in janela.findChildren(QLabel))
    assert "NÃO ESTÁ SERVINDO" in textos
    janela.close()
    boa = srv.montar_janela(servidor, tmp_path / "registro.txt")
    textos = " ".join(r.text() for r in boa.findChildren(QLabel))
    assert servidor.endereco in textos and "v1.0.0" in textos and "v2.0.0" not in textos
    app.processEvents()
    boa.close()
    assert servidor.fechado.is_set()
    assert "servindo" in (tmp_path / "registro.txt").read_text(encoding="utf-8")


def test_n13_o_servidor_nao_serve_por_uma_juncao(tmp_path):
    """N13 e achado 7 (quem tentou quebrar): uma "publicação" que é junção para outra pasta não é servida (a mesma
    regra do publicar, `DestinoPasta.liberadas`, num lugar só)."""
    import subprocess

    alvo = tmp_path / "outra pasta"
    alvo.mkdir()
    (alvo / "segredo.nupkg").write_bytes(b"de outro lugar")
    pasta = tmp_path / "versoes"
    pasta.mkdir()
    feito = subprocess.run(["cmd", "/c", "mklink", "/J", str(pasta / "v9.9.9"), str(alvo)], capture_output=True)
    assert feito.returncode == 0
    try:
        s = srv.Servidor(pasta, porta=0, dizer=lambda t: None)
        assert s.versoes.publicacoes() == [] and s.versoes.achar("segredo.nupkg") is None
    finally:
        subprocess.run(["cmd", "/c", "rmdir", str(pasta / "v9.9.9")], check=True)   # só o atalho
    assert (alvo / "segredo.nupkg").is_file()


def test_achado7_nome_repetido_em_duas_versoes_nao_e_entregue(tmp_path):
    """Achado 7: o .msi do vpk tinha o mesmo nome em toda versão, e o servidor entregava o da primeira pasta. Agora o
    publicar põe a versão no nome do .msi, e um nome repetido em duas publicações não é entregue (não se sabe qual)."""
    import empacotar

    pasta = tmp_path / "versoes"
    _publicar_na_pasta(pasta, "v1.2.0", {"igual.msi": b"1.2.0", empacotar.nome_do_msi_publicado("1.2.0"): b"msi 1.2.0"})
    _publicar_na_pasta(pasta, "v1.10.0", {"igual.msi": b"1.10.0",
                                          empacotar.nome_do_msi_publicado("1.10.0"): b"msi 1.10.0"})
    versoes = srv.Versoes(pasta)
    assert versoes.achar("igual.msi") is None
    assert versoes.achar(empacotar.nome_do_msi_publicado("1.2.0")).read_bytes() == b"msi 1.2.0"
    assert empacotar.nome_do_msi_publicado("1.2.0") != empacotar.nome_do_msi_publicado("1.10.0")
