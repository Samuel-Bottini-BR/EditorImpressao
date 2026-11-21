"""Testes do publicar (plano da parte do Windows, passo 2, peça 8): `publicar_versao_kaique.py` e a parte do Velopack de
`empacotar.py`.

O QUE ESTES TESTES PROVAM, E O QUE NÃO PROVAM (D-767, D-785)
    Provam a lógica em volta: a ordem (nada liberado antes da assinatura lida de volta), o que vai ao destino (nunca o
    Setup.exe), o que é apagado no fim (o rascunho e o Setup.exe, também com erro), a conta do espaço, a vigia, a
    recusa sem o motor publicado, a diferença entre atualização e instalador. O destino é uma pasta DE VERDADE (a
    mesma que o servidor das versões de prova serve); o rascunho é uma pasta de verdade; a vigia fecha um processo de
    verdade.
    NÃO provam que o vpk de verdade e o GitHub de verdade fazem o que se espera: o vpk aqui é um vpk de mentira (um
    script que escreve o que o vpk 1.2.161 escreve, com os nomes lidos no código dele), e o GitHub é um gh de mentira
    em memória. Isso só conta na prova à vista (publicar uma versão de prova no C:, o rascunho no GitHub), como manda
    a D-785 (item 8: publicar é sempre à vista).

Seguro mexer: acrescentar casos. Arriscado: trocar a pasta de destino de verdade por uma de mentira (deixa de provar).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import assinatura  # noqa: E402
import atualizacao  # noqa: E402
import empacotar  # noqa: E402
import montar_motor_kraken  # noqa: E402
import publicar_versao_kaique as pub  # noqa: E402
import versao  # noqa: E402
from core import ocr_kraken  # noqa: E402

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="o publicar só roda no Windows")

CHAVE = bytes(range(32))
PUBLICA = assinatura.secret_to_public(CHAVE).hex()
OUTRA_CHAVE = bytes(range(1, 33))
OUTRA_PUBLICA = assinatura.secret_to_public(OUTRA_CHAVE).hex()
VERSAO = "9.9.9"
ETIQUETA = versao.etiqueta_da_versao(VERSAO)

# O vpk de mentira: escreve na pasta de saída o que o vpk 1.2.161 escreve (os nomes de DefaultName.cs), com o pacote
# sendo um zip de verdade da pasta (em lib/app/), e anota cada vez que rodou. VPK_FALSO_FALHA=1: deixa o Setup.exe e
# sai com erro. VPK_FALSO_ESPERA=N: espera N segundos antes (para a vigia). VPK_FALSO_FILHO=<arquivo>: abre antes um
# programa filho que escreve um número nesse arquivo a cada 0,1 s (como o vpk abre o cmd.exe e o wix.exe do .msi).
# VPK_FALSO_SEM=<começo>: deixa de fora do pacote os arquivos cujo caminho (com /) começa assim (passo 2, volta 7,
# achado 3 do relatório 6: para a conferência do pacote depois do vpk ter o que acusar). Vazio: o pacote é a pasta
# inteira, como sempre.
VPK_FALSO = r'''
import hashlib, json, os, sys, time, zipfile
from pathlib import Path
a = sys.argv[1:]
def valor(nome):
    return a[a.index(nome) + 1]
Path(os.environ["VPK_FALSO_DIARIO"]).open("a", encoding="utf-8").write(json.dumps(a) + "\n")
Path(os.environ["VELOPACK_TEMP"], "vpk-usou-o-temp.txt").write_text("x")
if os.environ.get("VPK_FALSO_FILHO"):
    import subprocess
    batida = ("import os, sys, time\nn = 0\nwhile True:\n    n += 1\n    open(sys.argv[1] + '.tmp', 'w').write(str(n))\n"
              "    try:\n        os.replace(sys.argv[1] + '.tmp', sys.argv[1])\n    except OSError:\n        pass\n"
              "    time.sleep(0.1)\n")
    subprocess.Popen([sys.executable, "-c", batida, os.environ["VPK_FALSO_FILHO"]])
time.sleep(float(os.environ.get("VPK_FALSO_ESPERA", "0")))
pacote, ver, pasta, saida = valor("--packId"), valor("--packVersion"), Path(valor("--packDir")), Path(valor("--outputDir"))
saida.mkdir(parents=True, exist_ok=True)
(saida / f"{pacote}-win-Setup.exe").write_bytes(b"MZ setup de mentira")
if os.environ.get("VPK_FALSO_FALHA") == "1":
    sys.exit(3)
nupkg = saida / f"{pacote}-{ver}-full.nupkg"
with zipfile.ZipFile(nupkg, "w") as z:
    sem = os.environ.get("VPK_FALSO_SEM", "")
    for f in sorted(pasta.rglob("*")):
        if f.is_file() and not (sem and f.relative_to(pasta).as_posix().startswith(sem)):
            z.write(f, "lib/app/" + f.relative_to(pasta).as_posix())
if "--msi" in a:
    (saida / f"{pacote}-win.msi").write_bytes(b"msi de mentira")
dados = nupkg.read_bytes()
item = {"PackageId": pacote, "Version": ver, "Type": "Full", "FileName": nupkg.name,
        "SHA1": hashlib.sha1(dados).hexdigest().upper(), "SHA256": hashlib.sha256(dados).hexdigest().upper(),
        "Size": len(dados)}
(saida / "releases.win.json").write_text(json.dumps({"Assets": [item]}), encoding="utf-8")
(saida / "assets.win.json").write_text("[]", encoding="utf-8")
(saida / "RELEASES").write_text("x", encoding="utf-8")
'''


def _programa_de_prova(exe: Path, script: str) -> Path:
    """Um programa de prova DE VERDADE (um .exe), que roda o Python deste computador com o script. Volta 3 do passo 2
    (achado 3 do relatório 2 de quem tentou quebrar): o vpk de mentira era um vpk.cmd, que o Windows roda pelo cmd.exe,
    e a peça passou a recusar o .bat e o .cmd. É o lançador que o pip usa nos programas que instala (o t64.exe da
    distlib, que vem dentro do pip do .venv; distlib/scripts.py, ScriptMaker._write_script): o lançador, a linha
    "#!<o python>" e um zip com o __main__.py, colados num arquivo só. O lançador roda "<o python> <o próprio .exe>
    <os argumentos>", espera e devolve o código de saída do Python. O que ele e o Python abrem fica no grupo do Windows
    do vpk (Microsoft Learn, AssignProcessToJobObject: o filho só sai de um grupo que deixa sair; o nosso não deixa)."""
    import io

    from pip._vendor.distlib import scripts as distlib_scripts

    lancador = Path(distlib_scripts.__file__).with_name("t64.exe").read_bytes()
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as z:
        z.writestr("__main__.py", script)
    python = sys.executable if " " not in sys.executable else f'"{sys.executable}"'
    exe.write_bytes(lancador + b"#!" + python.encode("utf-8") + b"\n" + memoria.getvalue())
    return exe


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Tudo o que um publicar de teste precisa: a chave fora do 'repositório', o vpk de mentira, o destino (uma pasta
    de verdade), a base do rascunho, a pasta de saída, um motor com ficha e uma pasta do programa pronta.

    Passo 2, volta 7 (D-818, Samuel: "vai ter que reprogramar?" · "A"): a conferência da pasta passou a ler a
    assinatura digital do Visual C++ (a régua da montagem). Os Visual C++ de prova (poucos bytes, reconhecidos pelo
    conteúdo: `_VISUAL_C_DE_PROVA`) respondem como o Visual C++ oficial da Microsoft (`_ASSINATURA_DO_VISUAL_C_DE_PROVA`);
    qualquer outro arquivo vai à leitura DE VERDADE do Windows (`empacotar.assinatura_do_arquivo`). É peça de mentira só
    para a lógica em volta (D-767); a leitura de verdade tem os seus testes (tests/test_empacotar.py e
    tests/test_windows_peca.py)."""
    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")     # tmp_path pode estar dentro da cópia
    chave = tmp_path / "chave.txt"
    chave.write_text(assinatura.texto_da_chave_privada(CHAVE), encoding="utf-8")
    outra = tmp_path / "outra-chave.txt"
    outra.write_text(assinatura.texto_da_chave_privada(OUTRA_CHAVE), encoding="utf-8")
    vpk = _programa_de_prova(tmp_path / "vpk.exe", VPK_FALSO)
    diario = tmp_path / "vpk-rodou.txt"
    monkeypatch.setenv("VPK_FALSO_DIARIO", str(diario))
    monkeypatch.delenv("VPK_FALSO_FALHA", raising=False)
    monkeypatch.delenv("VPK_FALSO_ESPERA", raising=False)
    monkeypatch.delenv("VPK_FALSO_FILHO", raising=False)
    monkeypatch.delenv("VPK_FALSO_SEM", raising=False)
    ler_de_verdade = empacotar.assinatura_do_arquivo

    def assinatura_de_prova(arquivo):
        """O Visual C++ de prova responde como o oficial; o resto, pela leitura de verdade."""
        try:
            conteudo = Path(arquivo).read_bytes()
        except OSError:
            conteudo = None
        if conteudo in _VISUAL_C_DE_PROVA:
            return dict(_ASSINATURA_DO_VISUAL_C_DE_PROVA)
        return ler_de_verdade(arquivo)

    monkeypatch.setattr(empacotar, "assinatura_do_arquivo", assinatura_de_prova)
    # muito espaço livre (o disco do teste pode ser pequeno); os testes do espaço trocam isto
    monkeypatch.setattr(empacotar, "espaco_livre", lambda pasta: 500 * empacotar.GB)
    motor = _motor_com_ficha(tmp_path / "motor")
    a = {"tmp": tmp_path, "chave": chave, "outra": outra, "vpk": vpk, "diario": diario,
         "servidor": tmp_path / "servidor", "rascunho": tmp_path / "disco-de-dentro", "saida": tmp_path / "saida",
         "motor": motor, "pasta": _pasta_pronta(tmp_path / "EditorImpressao", VERSAO)}
    return a


def _motor_com_ficha(pasta: Path) -> Path:
    """Um motor de mentira com a forma de um motor do jeito novo, e a ficha gravada pela função de verdade."""
    kraken = pasta / "python" / "Lib" / "site-packages" / "kraken"
    kraken.mkdir(parents=True)
    (pasta / "python" / "python.exe").write_bytes(b"MZ python")
    (kraken / "blla.mlmodel").write_bytes(b"modelo" * 100)
    (pasta / ocr_kraken.NOME_DO_SERVIDOR).write_text(f"VERSAO_PROTOCOLO = {ocr_kraken.VERSAO_PROTOCOLO}\n",
                                                     encoding="utf-8")
    montar_motor_kraken.gravar_ficha_do_motor(pasta)
    return pasta


# Passo 2, volta 7 (D-818): o Visual C++ de prova da pasta de mentira e o que a leitura da assinatura responde por ele
# (o mesmo que o Windows responde pelo vc_redist.x64.exe oficial; tests/test_empacotar.py::_assinatura).
VERSAO_DO_VISUAL_C_DE_PROVA = "14.44.35211.0"
_ASSINATURA_DO_VISUAL_C_DE_PROVA = {
    "status": "Valid",
    "assinante": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
    "produto": "Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211",
    "versao": VERSAO_DO_VISUAL_C_DE_PROVA}


def _pasta_pronta(pasta: Path, versao_da_pasta: str) -> Path:
    """Uma pasta do programa pronta (o que o empacotador confere no pacote: o .exe, os modelos, as DLLs, o Visual C++),
    sem o motor solto, com a ficha da versão escrita pela função de verdade.

    Passo 2, volta 7 (D-818, Samuel: "vai ter que reprogramar?" · "A"; achado 1 do relatório 6): a pasta de mentira
    passou a trazer o que a pasta de verdade traz e a conferência agora cobra: o arquivo da versão do Visual C++ e o
    Tesseract (os mesmos caminhos que a montagem copia, lidos de `empacotar._destinos_das_pecas`). Antes ela só passava
    porque a conferência não os procurava."""
    (pasta / empacotar.INTERNO).mkdir(parents=True)
    (pasta / f"{empacotar.NOME}.exe").write_bytes(b"MZ editor")
    for origem, destino in [*empacotar.modelos_do_programa(), *empacotar.nativos_do_programa()]:
        alvo = pasta / empacotar.INTERNO / destino / origem.name
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(b"x")
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    instalar.mkdir()
    (instalar / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ visual c")
    (instalar / atualizacao.VC_REDIST_VERSAO).write_text(VERSAO_DO_VISUAL_C_DE_PROVA, encoding="utf-8")
    origem = pasta.parent / "origem-de-mentira"
    pecas = empacotar.PecasDosDetectores(None, origem, origem / "doc", origem / "tessdata", origem / "vc", "")
    for _, relativo in empacotar._destinos_das_pecas(pecas):
        (pasta / relativo).parent.mkdir(parents=True, exist_ok=True)
        (pasta / relativo).write_bytes(b"tesseract de prova: " + relativo.encode())
    empacotar.gravar_ficha_da_versao(pasta, empacotar.ATUALIZACAO)
    ficha = json.loads((pasta / empacotar.NOME_DA_FICHA_DA_VERSAO).read_text(encoding="utf-8"))
    ficha["versao"] = versao_da_pasta
    (pasta / empacotar.NOME_DA_FICHA_DA_VERSAO).write_text(json.dumps(ficha), encoding="utf-8")
    return pasta


def _publicar_o_motor(a, destino=None, chave=None, publica=PUBLICA) -> str:
    """Publica o motor de mentira (com a ficha de verdade) no destino do teste."""
    return pub.publicar_motor(motor_escolhido=a["motor"], arquivo_da_chave=chave or a["chave"],
                              chave_publica=publica, rascunho_base=a["rascunho"],
                              destino=destino or pub.DestinoPasta(a["servidor"]))


def _publicar(a, destino=None, **extra) -> Path:
    """Publica a versao de teste com a pasta pronta e o vpk de mentira."""
    opcoes = dict(pasta_pronta=a["pasta"], arquivo_da_chave=a["chave"], chave_publica=PUBLICA, vpk=a["vpk"],
                  rascunho_base=a["rascunho"], pasta_de_saida=a["saida"],
                  destino=destino or pub.DestinoPasta(a["servidor"]))
    opcoes.update(extra)
    return pub.publicar(VERSAO, **opcoes)


def _vezes_que_o_vpk_rodou(a) -> list[list[str]]:
    """Os argumentos de cada vez que o vpk de mentira rodou."""
    if not a["diario"].exists():
        return []
    return [json.loads(linha) for linha in a["diario"].read_text(encoding="utf-8").splitlines()]


def _tudo_em(pasta: Path) -> list[str]:
    """Tudo o que ha dentro da pasta (caminhos relativos)."""
    return sorted(p.relative_to(pasta).as_posix() for p in pasta.rglob("*")) if pasta.exists() else []


def _rascunhos_que_sobraram(a) -> list[str]:
    """O que ficou na base do rascunho (tem de ficar vazia)."""
    base = a["rascunho"]
    return [p.name for p in base.iterdir()] if base.exists() else []


# ---------------------------------------------------------------------------------------------------------------------
# O caminho inteiro, numa pasta de verdade
# ---------------------------------------------------------------------------------------------------------------------

def test_d768_o_motor_e_a_versao_publicados_numa_pasta_sem_o_motor_no_pacote(ambiente):
    """D-768 ("mas dai vai ter que baixar o motor do kraken toda vez...?"), D-789, D-795: o motor tem publicação
    própria; a versão do programa sai sem o motor solto, com o motor-exigido.json que aponta para o motor publicado
    (a soma da assinatura dele); ao destino vão só o pacote, o índice e a assinatura; o Setup.exe e o rascunho somem;
    e o programa do Kaique aceita a assinatura publicada."""
    a = ambiente
    assert _publicar_o_motor(a) == versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    _publicar(a)
    publicados = sorted(f.name for f in (a["servidor"] / ETIQUETA).iterdir())
    nupkg = empacotar.nupkg_inteiro(a["servidor"] / ETIQUETA, VERSAO)
    assert publicados == sorted([nupkg.name, empacotar.NOME_DO_INDICE,
                                 assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, VERSAO)])
    with zipfile.ZipFile(nupkg) as z:
        nomes = z.namelist()
        exigido = json.loads(z.read(empacotar.PASTA_NO_NUPKG + empacotar.NOME_DO_MOTOR_EXIGIDO))
    assert not any(n.startswith(empacotar.PASTA_NO_NUPKG + empacotar.PASTA_DO_MOTOR) for n in nomes)
    arquivo_do_motor = a["servidor"] / exigido["etiqueta"] / exigido["arquivo"]
    assert exigido["sha256"] == assinatura.soma_sha256(arquivo_do_motor)
    assert exigido["pacote"] == versao.ID_DO_PACOTE_DO_MOTOR and exigido["versao"] == ocr_kraken.VERSAO_DO_MOTOR
    setup = empacotar.nome_do_setup()
    assert setup not in " ".join(_tudo_em(a["servidor"]) + _tudo_em(a["saida"]))
    assert _rascunhos_que_sobraram(a) == []
    alvo = type("Alvo", (), {"PackageId": versao.ID_DO_PACOTE, "Version": VERSAO, "FileName": nupkg.name,
                             "SHA256": assinatura.soma_sha256(nupkg)})()
    assert atualizacao.conferir_assinatura_do(atualizacao.Fonte(str(a["servidor"] / ETIQUETA)), alvo, PUBLICA) is None
    vezes = _vezes_que_o_vpk_rodou(a)
    assert len(vezes) == 1 and "--msi" not in vezes[0]
    assert vezes[0][vezes[0].index("--delta") + 1] == "None" and "--noPortable" in vezes[0]


def test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro(ambiente, monkeypatch, capsys):
    """D-795 ("porque fazer isso?" · "ok") e D-776: o vpk deixa o Setup.exe e falha no meio; o publicar para, e no
    fim o Setup.exe não está na pasta de saída nem no destino, o rascunho do disco de dentro foi apagado e o destino
    não tem nem a versão nem rascunho dela. A conferência do fim diz isso."""
    a = ambiente
    _publicar_o_motor(a)
    monkeypatch.setenv("VPK_FALSO_FALHA", "1")
    with pytest.raises(pub.Parou, match="empacotamento"):
        _publicar(a)
    assert len(_vezes_que_o_vpk_rodou(a)) == 1, "o vpk tinha de ter rodado (e falhado)"
    setup = empacotar.nome_do_setup()
    assert setup not in " ".join(_tudo_em(a["servidor"]) + _tudo_em(a["saida"]) + _tudo_em(a["rascunho"]))
    assert _rascunhos_que_sobraram(a) == []
    assert pub.DestinoPasta(a["servidor"]).situacao(ETIQUETA) is None
    saida = capsys.readouterr().out
    assert "apagado (conferido)" in saida and "não está na pasta de saída nem no destino (conferido)" in saida


def test_d776_sem_espaco_para_antes_do_vpk_e_nada_fica(ambiente, monkeypatch):
    """D-776 ("Sim, no C só tem que cuidar para não encher o disco C inteiro"; 20 GB): com 21 GB livres, a conta do
    que o trabalho usa deixaria o disco abaixo de 20 GB: o publicar para antes de rodar o vpk, com a frase dos GB, e
    nada fica (nem rascunho, nem nada no destino)."""
    a = ambiente
    _publicar_o_motor(a)
    monkeypatch.setattr(empacotar, "espaco_livre", lambda pasta: 21 * empacotar.GB)
    with pytest.raises(pub.Parou, match=r"pelo menos 20 GB livres"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []
    assert _rascunhos_que_sobraram(a) == []
    assert pub.DestinoPasta(a["servidor"]).situacao(ETIQUETA) is None


def test_d776_a_vigia_fecha_o_vpk_quando_o_disco_cai_abaixo_da_reserva(ambiente, monkeypatch, tmp_path):
    """D-776 ("ele vigia o espaço durante o trabalho e para com aviso se cair perto da reserva"): um vpk (processo de
    verdade) que demoraria 60 s é fechado pela vigia em poucos segundos quando o espaço livre lido cai abaixo da
    reserva; a frase diz quanto ficou."""
    monkeypatch.setenv("VPK_FALSO_ESPERA", "60")
    rascunho = tmp_path / "publicar-vigia"
    rascunho.mkdir()
    leituras = []

    def livre(_pasta):
        """O espaço "lido": bom na primeira leitura, abaixo da reserva depois (como se outro programa enchesse o C:)."""
        leituras.append(1)
        return 100 * empacotar.GB if len(leituras) == 1 else 19 * empacotar.GB

    inicio = time.perf_counter()
    motivo = empacotar.rodar_vpk(empacotar.comando_do_vpk(ambiente["vpk"], ambiente["pasta"], rascunho / "saida",
                                                          VERSAO, com_msi=False),
                                 rascunho, intervalo_s=0.5, livre=livre)
    assert time.perf_counter() - inicio < 30, "a vigia não fechou o vpk"
    assert motivo and "19.0 GB" in motivo and "reserva" in motivo
    assert (rascunho / "temp" / "vpk-usou-o-temp.txt").is_file(), "a pasta temporária do vpk tem de ser a do rascunho"


def test_d790_sem_o_motor_publicado_nada_e_montado(ambiente):
    """D-790 ("A") e D-768: a versão que pede um motor que não está publicado não é montada nem publicada."""
    a = ambiente
    with pytest.raises(pub.Parou, match=r"publique o motor antes"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []
    assert _tudo_em(a["servidor"]) == [] and _rascunhos_que_sobraram(a) == []


def test_d724_o_motor_com_a_assinatura_de_outra_chave_e_recusado(ambiente):
    """D-724: o motor publicado com outra chave não serve para a versão assinada pela chave do programa."""
    a = ambiente
    _publicar_o_motor(a, chave=a["outra"], publica=OUTRA_PUBLICA)
    with pytest.raises(pub.Parou, match=r"motor publicado .* não confere"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []


def test_d777_o_instalador_so_quando_pedido_e_o_publicado_e_o_da_atualizacao(ambiente):
    """D-777 ("ok, fica assim") e D-788: com o instalador pedido, o vpk roda duas vezes (a atualização sem .msi; o
    instalador com o .msi e o arquivo do motor publicado em instalar\\). O .msi vai para a pasta de saída; o pacote
    publicado é o da atualização (sem o arquivo do motor) e o .msi vai junto à publicação; a pasta do programa volta
    sem o arquivo do motor."""
    a = ambiente
    _publicar_o_motor(a)
    _publicar(a, com_instalador=True)
    vezes = _vezes_que_o_vpk_rodou(a)
    assert len(vezes) == 2 and "--msi" not in vezes[0] and "--msi" in vezes[1]
    msi = empacotar.nome_do_msi_publicado(VERSAO)
    assert VERSAO in msi and (a["saida"] / ETIQUETA / msi).is_file()
    assert (a["servidor"] / ETIQUETA / msi).is_file(), "o .msi pedido vai à publicação (como antes), com o número"
    nome_do_motor = versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    with zipfile.ZipFile(empacotar.nupkg_inteiro(a["servidor"] / ETIQUETA, VERSAO)) as z:
        assert not any(n.endswith(nome_do_motor) for n in z.namelist())
    assert not (a["pasta"] / atualizacao.PASTA_DO_QUE_SE_INSTALA / nome_do_motor).exists()
    assert empacotar.nome_do_setup() not in " ".join(_tudo_em(a["servidor"]) + _tudo_em(a["saida"]))
    assert _rascunhos_que_sobraram(a) == []


def test_a_pasta_pronta_de_outra_versao_e_recusada(ambiente):
    """Defeito 54 do plano (a pasta pronta de uma 1.1.0 publicada como 1.1.5): recusada antes do vpk."""
    a = ambiente
    _publicar_o_motor(a)
    _pasta_pronta(a["tmp"] / "outra" / "EditorImpressao", "1.0.0")
    with pytest.raises(pub.Parou, match=r"é da versão 1.0.0"):
        _publicar(a, pasta_pronta=a["tmp"] / "outra" / "EditorImpressao")
    assert _vezes_que_o_vpk_rodou(a) == []


def test_a_versao_que_ja_existe_no_destino_e_recusada(ambiente):
    """Um número de versão só: a versão já publicada (ou um rascunho que sobrou dela) é recusada antes de tudo."""
    a = ambiente
    _publicar_o_motor(a)
    (a["servidor"] / (pub.NOME_DO_RASCUNHO_NO_DESTINO + ETIQUETA)).mkdir(parents=True)
    with pytest.raises(pub.Parou, match="já existe"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []


# ---------------------------------------------------------------------------------------------------------------------
# Nada liberado antes de ler de volta (o defeito 53 do plano)
# ---------------------------------------------------------------------------------------------------------------------

class _DestinoQueAnota(pub.DestinoPasta):
    """Uma pasta de verdade que anota a ordem dos pedidos (e pode errar a soma de um arquivo de propósito)."""

    def __init__(self, raiz, errar_soma_de: str | None = None):
        """A pasta de verdade; errar_soma_de: o arquivo cuja soma "lida" sai errada."""
        super().__init__(raiz)
        self.pedidos: list[tuple[str, str]] = []
        self.errar_soma_de = errar_soma_de

    def enviar(self, etiqueta, arquivo):
        """Anota e envia."""
        self.pedidos.append(("enviar", Path(arquivo).name))
        super().enviar(etiqueta, arquivo)

    def baixar(self, etiqueta, nome, pasta_local):
        """Anota e lê de volta."""
        self.pedidos.append(("ler", nome))
        return super().baixar(etiqueta, nome, pasta_local)

    def soma(self, etiqueta, nome):
        """Anota e soma (errada de propósito, se pedido)."""
        self.pedidos.append(("soma", nome))
        if nome == self.errar_soma_de:
            return "0" * 64
        return super().soma(etiqueta, nome)

    def liberar(self, etiqueta):
        """Anota e libera."""
        self.pedidos.append(("liberar", etiqueta))
        super().liberar(etiqueta)


def test_d53_nada_e_liberado_antes_da_assinatura_lida_de_volta(ambiente):
    """Defeito 53 do plano (no GitHub, a versão era liberada antes de a assinatura subir): agora a liberação é o último
    pedido, depois de enviar tudo e de ler de volta a assinatura e o índice do destino."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueAnota(a["servidor"])
    _publicar(a, destino=destino)
    nome = assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, VERSAO)
    pedidos = destino.pedidos
    assert pedidos[-1] == ("liberar", ETIQUETA)
    assert ("enviar", nome) in pedidos and ("ler", nome) in pedidos and ("ler", empacotar.NOME_DO_INDICE) in pedidos
    assert pedidos.index(("ler", nome)) > pedidos.index(("enviar", nome))
    assert not any(n.endswith("Setup.exe") for _, n in pedidos)


def test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino(ambiente):
    """Se o pacote lido do destino não tem a soma do pacote enviado, nada é liberado e o rascunho do destino some
    (conferido); a frase diz que foi apagado."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueAnota(a["servidor"], errar_soma_de=empacotar.nupkg_inteiro(Path("."), VERSAO).name)
    with pytest.raises(pub.Parou, match=r"chegou diferente.*apagada"):
        _publicar(a, destino=destino)
    assert ("liberar", ETIQUETA) not in destino.pedidos
    assert destino.situacao(ETIQUETA) is None and _rascunhos_que_sobraram(a) == []


# ---------------------------------------------------------------------------------------------------------------------
# O GitHub, com um gh de mentira (só a lógica: o de verdade é da prova à vista)
# ---------------------------------------------------------------------------------------------------------------------

class _GitHubDeMentira:
    """Guarda as publicações em memória e responde como o gh 2.99 (o formato lido no código dele)."""

    def __init__(self, tmp: Path, falhar_ao_ver: bool = False):
        """falhar_ao_ver: o "view" responde erro de rede (para o caso de o GitHub não responder)."""
        self.tmp = tmp
        self.publicacoes: dict[str, dict] = {}
        self.pedidos: list[list[str]] = []
        self.falhar_ao_ver = falhar_ao_ver
        self.etiquetas_apagadas: list[str] = []
        self.falhar_ao_apagar_a_etiqueta = False

    def __call__(self, *argumentos, limite_s=600):
        """Responde um pedido do gh (release view/create/upload/download/edit/delete)."""
        a = list(argumentos)
        self.pedidos.append(a)
        _, sub, etiqueta = a[0], a[1], a[2]
        feito = lambda codigo=0, saida="", erro="": subprocess.CompletedProcess(a, codigo, saida, erro)  # noqa: E731
        p = self.publicacoes.get(etiqueta)
        if sub == "view":
            if self.falhar_ao_ver:
                return feito(1, "", "error connecting to api.github.com")
            if p is None:
                return feito(1, "", "release not found")
            assets = [{"name": n, "size": len(d), "digest": "sha256:" + __import__("hashlib").sha256(d).hexdigest()}
                      for n, d in p["arquivos"].items()]
            return feito(0, json.dumps({"isDraft": p["rascunho"], "tagName": etiqueta, "assets": assets}))
        if sub == "create":
            assert "--draft" in a
            self.publicacoes[etiqueta] = {"rascunho": True, "arquivos": {}}
            return feito()
        if p is None:
            return feito(1, "", "release not found")
        if sub == "upload":
            p["arquivos"][Path(a[3]).name] = Path(a[3]).read_bytes()
        elif sub == "download":
            nome, pasta = a[a.index("--pattern") + 1], Path(a[a.index("--dir") + 1])
            (pasta / nome).write_bytes(p["arquivos"][nome])
        elif sub == "edit":
            assert "--draft=false" in a
            p["rascunho"] = False
        elif sub == "delete":
            # Como o gh 2.99 (cli/cli, pkg/cmd/release/delete/delete.go, deleteRun e deleteTag): apaga a publicação e,
            # com --cleanup-tag, apaga DEPOIS a etiqueta; num rascunho a etiqueta não existe ("pending tag") e o gh
            # sai com o erro do GitHub, mesmo tendo apagado a publicação.
            era_rascunho = p["rascunho"]
            del self.publicacoes[etiqueta]
            if "--cleanup-tag" in a:
                if era_rascunho:
                    return feito(1, "", "HTTP 422: Reference does not exist (https://api.github.com/repos/x/y/git/refs/"
                                        f"tags/{etiqueta})")
                if self.falhar_ao_apagar_a_etiqueta:
                    return feito(1, "", "HTTP 500: o GitHub não respondeu ao apagar a etiqueta")
                self.etiquetas_apagadas.append(etiqueta)
        return feito()


def test_o_github_sobe_como_rascunho_le_de_volta_e_so_entao_libera(ambiente, monkeypatch):
    """No GitHub (gh de mentira): o motor e a versão sobem como rascunho ("create --draft"), são lidos de volta
    ("download" da assinatura), e "edit --draft=false" é o último pedido de cada um. Nada de Setup.exe."""
    a = ambiente
    gh = _GitHubDeMentira(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    _publicar(a, destino=destino)
    for etiqueta in (versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR), ETIQUETA):
        dele = [p for p in gh.pedidos if p[2] == etiqueta and p[1] != "view"]
        mudancas = [p[1] for p in dele if p[1] in ("create", "upload", "edit", "delete")]
        assert mudancas[0] == "create" and mudancas[-1] == "edit" and mudancas.count("edit") == 1
        liberou = next(i for i, p in enumerate(dele) if p[1] == "edit")
        assert any(p[1] == "download" and p[p.index("--pattern") + 1].endswith(".assinatura")
                   for p in dele[:liberou]), "a assinatura tem de ser lida de volta antes de liberar"
        assert gh.publicacoes[etiqueta]["rascunho"] is False
    assert not any(n.endswith("Setup.exe") for p in gh.publicacoes.values() for n in p["arquivos"])


def test_o_github_sem_resposta_nunca_vira_nao_publicada(ambiente, monkeypatch):
    """CLAUDE.md §11.12, ponto 2: um erro do GitHub ao perguntar não vira "não existe" (o publicar para)."""
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", _GitHubDeMentira(ambiente["tmp"], falhar_ao_ver=True))
    with pytest.raises(pub.Parou, match="não consegui perguntar ao GitHub"):
        destino.situacao(ETIQUETA)
    certo = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(certo, "_gh", _GitHubDeMentira(ambiente["tmp"]))
    assert certo.situacao(ETIQUETA) is None


# ---------------------------------------------------------------------------------------------------------------------
# O empacotador: o comando, o pacote, a conta
# ---------------------------------------------------------------------------------------------------------------------

def test_d789_d777_o_comando_do_vpk_sem_diferenca_sem_portatil_e_o_msi_so_quando_pedido():
    """D-789 (sem a diferença), D-777 (sem o zip portátil; o .msi só no instalador). O padrão do parâmetro continua o
    do instalador (os testes antigos da D-727 conferem esse comando)."""
    sem = empacotar.comando_do_vpk(Path("vpk.exe"), Path("p"), Path("s"), "1.2.0", com_msi=False)
    com = empacotar.comando_do_vpk(Path("vpk.exe"), Path("p"), Path("s"), "1.2.0")
    for comando in (sem, com):
        assert comando[comando.index("--delta") + 1] == "None" and "--noPortable" in comando
        assert "--noInst" not in comando, "o vpk 1.2.161 recusa --noInst com --noPortable"
    assert "--msi" not in sem and "--instLocation" not in sem
    assert "--msi" in com and com[com.index("--instLocation") + 1] == "PerMachine"
    assert empacotar.INSTALADOR.com_msi and not empacotar.ATUALIZACAO.com_msi


def test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado(tmp_path):
    """D-768: se o motor solto (motor-kraken\\) estiver no pacote da atualização, a conferência do pacote acusa."""
    esperados = empacotar.esperados_no_pacote_do_velopack(None, empacotar.ATUALIZACAO)
    nupkg = tmp_path / "p.nupkg"
    with zipfile.ZipFile(nupkg, "w") as z:
        for relativo in esperados:
            z.writestr(empacotar.PASTA_NO_NUPKG + relativo, b"x")
    assert empacotar.conferir_pacote_do_velopack(nupkg, None, empacotar.ATUALIZACAO) == []
    with zipfile.ZipFile(nupkg, "a") as z:
        z.writestr(empacotar.PASTA_NO_NUPKG + "motor-kraken/python/python.exe", b"x")
    assert any("motor-kraken" in p for p in empacotar.conferir_pacote_do_velopack(nupkg, None, empacotar.ATUALIZACAO))
    assert empacotar.NOME_DO_MOTOR_EXIGIDO in esperados
    assert not any(e.startswith(empacotar.PASTA_DO_MOTOR) for e in esperados)
    no_instalador = empacotar.esperados_no_pacote_do_velopack(None, empacotar.INSTALADOR)
    assert f"instalar/{versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)}" in no_instalador


def test_d776_a_conta_do_espaco_e_a_reserva_de_20_gb(tmp_path, monkeypatch):
    """D-776: a conta (3 vezes a pasta na atualização; 5 vezes com o .msi, mais o motor; mais a margem) e a reserva de
    20 GB: com o que sobra abaixo de 20 GB, não começa; acima, começa."""
    um_gb = empacotar.GB
    so_atualizacao = empacotar.espaco_que_vai_usar(um_gb, (empacotar.ATUALIZACAO,))
    com_instalador = empacotar.espaco_que_vai_usar(um_gb, (empacotar.ATUALIZACAO, empacotar.INSTALADOR), um_gb // 2)
    assert so_atualizacao == 4 * um_gb + empacotar.MARGEM_DA_CONTA
    assert com_instalador == um_gb + 7 * (um_gb + um_gb // 2) + empacotar.MARGEM_DA_CONTA
    assert empacotar.RESERVA_DO_DISCO == 20 * um_gb
    monkeypatch.setattr(empacotar, "espaco_livre", lambda pasta: 25 * um_gb)
    assert empacotar.conferir_espaco(tmp_path, so_atualizacao) is None
    assert "20 GB" in empacotar.conferir_espaco(tmp_path, com_instalador)


def test_o_rascunho_so_apaga_o_que_e_dele(tmp_path):
    """O publicar só apaga pasta com o nome dele, dentro da base, e confere que sumiu (§10.9 e F9 do catálogo)."""
    base = tmp_path / "base"
    alheia = base / "nao-e-do-publicar"
    alheia.mkdir(parents=True)
    (alheia / "importante.txt").write_text("fica", encoding="utf-8")
    velho = base / f"{pub.PREFIXO_DO_RASCUNHO}velho"
    velho.mkdir()
    (velho / "sobra.bin").write_bytes(b"x")
    um_dia = time.time() - 24 * 3600
    os.utime(velho, (um_dia, um_dia))
    recente = base / f"{pub.PREFIXO_DO_RASCUNHO}de-outro-publicar-rodando"
    recente.mkdir()
    novo = pub.criar_rascunho(base)
    assert novo.parent == base and not velho.exists() and (alheia / "importante.txt").is_file()
    assert recente.is_dir(), "o rascunho recente pode ser de outro publicar rodando agora: não se apaga"
    assert pub.apagar_rascunho(alheia) and (alheia / "importante.txt").is_file()
    assert pub.apagar_rascunho(novo) == [] and not novo.exists()


def test_o_publicar_sem_a_chave_continua_parando_antes_de_tudo(tmp_path, monkeypatch):
    """D-724 (o teste antigo cobra o mesmo pelo caminho antigo): sem a chave, nem o motor nem a versão rodam nada."""
    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")
    rodou = []
    monkeypatch.setattr(pub.subprocess, "run", lambda *a, **k: rodou.append(a))
    monkeypatch.setattr(empacotar.subprocess, "Popen", lambda *a, **k: rodou.append(a))
    for chamar in (lambda: pub.publicar(VERSAO, destino_pasta=tmp_path / "s", arquivo_da_chave=tmp_path / "x.txt"),
                   lambda: pub.publicar_motor(destino_pasta=tmp_path / "s", arquivo_da_chave=tmp_path / "x.txt")):
        with pytest.raises(pub.Parou, match="não achei a chave privada"):
            chamar()
    assert rodou == [] and not (tmp_path / "s").exists()


def test_d776_a_reserva_so_aumenta_na_linha_de_comando(tmp_path, monkeypatch):
    """D-776 (20 GB): o --reserva-gb existe só para a prova do aviso de pouco espaço e só AUMENTA a reserva; pedir
    menos de 20 GB deixa os 20."""
    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")
    monkeypatch.setattr(empacotar, "RESERVA_DO_DISCO", 20 * empacotar.GB)
    sem_chave = ["--pasta", str(tmp_path / "s"), "--chave", str(tmp_path / "nao-existe.txt")]
    assert pub.main(["--reserva-gb", "5", *sem_chave]) == 1
    assert empacotar.RESERVA_DO_DISCO == 20 * empacotar.GB
    assert pub.main(["--reserva-gb", "500", *sem_chave]) == 1
    assert empacotar.RESERVA_DO_DISCO == 500 * empacotar.GB
    monkeypatch.setattr(empacotar, "espaco_livre", lambda pasta: 100 * empacotar.GB)
    assert "500 GB" in empacotar.conferir_espaco(tmp_path, 0)


def test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado(tmp_path):
    """D-809: se a subpasta de uma publicação no destino for um atalho (junção) para outra pasta, o apagar para e não
    apaga nada do outro lado; e, dentro de uma publicação de verdade, uma junção sai sem levar o que está do outro lado
    (o rmtree do Python não entra em junção)."""
    alvo = tmp_path / "pasta de verdade"
    alvo.mkdir()
    (alvo / "importante.txt").write_text("fica", encoding="utf-8")
    servidor = tmp_path / "servidor"
    servidor.mkdir()
    feito = subprocess.run(["cmd", "/c", "mklink", "/J", str(servidor / ETIQUETA), str(alvo)],
                           capture_output=True, text=True)
    assert feito.returncode == 0, feito.stderr
    destino = pub.DestinoPasta(servidor)
    with pytest.raises(pub.Parou, match="atalho"):
        pub.apagar_publicacao(destino, ETIQUETA)
    assert (alvo / "importante.txt").is_file()
    subprocess.run(["cmd", "/c", "rmdir", str(servidor / ETIQUETA)], check=True)   # só o atalho
    assert (alvo / "importante.txt").is_file()
    (servidor / ETIQUETA).mkdir()
    subprocess.run(["cmd", "/c", "mklink", "/J", str(servidor / ETIQUETA / "dentro"), str(alvo)], check=True,
                   capture_output=True)
    pub.apagar_publicacao(destino, ETIQUETA)
    assert not (servidor / ETIQUETA).exists() and (alvo / "importante.txt").is_file()


# ---------------------------------------------------------------------------------------------------------------------
# Volta 2 (achados de quem tentou quebrar, relatorio-1.md, 19/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

def _batida_viva(arquivo: Path, espera_s: float = 1.5) -> bool:
    """O programa que escreve um número neste arquivo a cada 0,1 s ainda escreve?"""
    def ler() -> str:
        """O número de agora (vazio se não deu para ler)."""
        try:
            return arquivo.read_text()
        except OSError:
            return ""

    antes = ler()
    time.sleep(espera_s)
    return ler() not in ("", antes)


def _esperar_arquivo(arquivo: Path, limite_s: float = 15) -> None:
    """Espera o arquivo aparecer (o filho do vpk de mentira começou)."""
    fim = time.monotonic() + limite_s
    while time.monotonic() < fim and not arquivo.exists():
        time.sleep(0.1)


def test_achado2_a_vigia_fecha_o_vpk_e_o_que_ele_abriu(ambiente, monkeypatch, tmp_path):
    """Achado 2: a vigia do espaço fechava só o vpk; o programa que ele abre para o .msi (cmd.exe, wix.exe) continuava
    gravando no C:. Agora o vpk roda num grupo do Windows e a vigia fecha tudo. De verdade: o vpk de mentira abre um
    filho que escreve a cada 0,1 s; depois de a vigia parar, o filho não escreve mais, e a frase diz "conferido"."""
    batida = tmp_path / "filho-do-vpk.txt"
    monkeypatch.setenv("VPK_FALSO_ESPERA", "60")
    monkeypatch.setenv("VPK_FALSO_FILHO", str(batida))
    rascunho = tmp_path / "publicar-vigia2"
    rascunho.mkdir()
    leituras = []

    def livre(_pasta):
        """Bom enquanto o filho não começou; abaixo da reserva depois."""
        leituras.append(1)
        return 100 * empacotar.GB if not batida.exists() else 19 * empacotar.GB

    motivo = empacotar.rodar_vpk(empacotar.comando_do_vpk(ambiente["vpk"], ambiente["pasta"], rascunho / "s", VERSAO,
                                                          com_msi=False), rascunho, intervalo_s=0.3, livre=livre)
    assert motivo and "reserva" in motivo and "fechados (conferido)" in motivo, motivo
    assert not _batida_viva(batida), "o programa que o vpk abriu continuou rodando"


def test_n10_ctrl_c_fecha_o_vpk_e_o_que_ele_abriu(ambiente, monkeypatch, tmp_path):
    """N10: o Ctrl+C no meio do vpk fecha o vpk e o que ele abriu, e repassa a interrupção."""
    batida = tmp_path / "filho-do-vpk.txt"
    monkeypatch.setenv("VPK_FALSO_ESPERA", "60")
    monkeypatch.setenv("VPK_FALSO_FILHO", str(batida))
    rascunho = tmp_path / "publicar-ctrlc"
    rascunho.mkdir()

    def livre(_pasta):
        """Simula o Ctrl+C assim que o filho começou."""
        if batida.exists():
            raise KeyboardInterrupt
        return 100 * empacotar.GB

    with pytest.raises(KeyboardInterrupt):
        empacotar.rodar_vpk(empacotar.comando_do_vpk(ambiente["vpk"], ambiente["pasta"], rascunho / "s", VERSAO,
                                                     com_msi=False), rascunho, intervalo_s=0.3, livre=livre)
    assert not _batida_viva(batida)


def test_achado1_apagar_um_rascunho_no_github_le_de_volta_e_nao_acusa_erro_falso(ambiente, monkeypatch):
    """Achado 1: o gh, com --cleanup-tag num rascunho, apaga a publicação e sai com erro (a etiqueta de um rascunho não
    existe; delete.go). Antes o publicar dizia "o GitHub não deixou apagar". Agora: rascunho sem --cleanup-tag, versão
    liberada com, e quem decide é a leitura de volta. O gh de mentira imita o de verdade."""
    gh = _GitHubDeMentira(ambiente["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    destino.criar_rascunho(ETIQUETA, "t", "n")
    assert pub.apagar_publicacao(destino, ETIQUETA) is None and destino.situacao(ETIQUETA) is None
    apagou = [p for p in gh.pedidos if p[1] == "delete"]
    assert apagou and "--cleanup-tag" not in apagou[-1]
    destino.criar_rascunho(ETIQUETA, "t", "n")
    destino.liberar(ETIQUETA)
    pub.apagar_publicacao(destino, ETIQUETA)
    assert destino.situacao(ETIQUETA) is None and gh.etiquetas_apagadas == [ETIQUETA]


def test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou(ambiente, monkeypatch):
    """Achado 1, o caminho da prova (o erro de propósito): a soma lida do GitHub não bate; o rascunho é apagado e a
    frase diz "foi apagada (conferido)", nunca "ATENÇÃO ... apague à mão"."""
    a = ambiente
    gh = _GitHubDeMentira(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    real = destino.soma
    monkeypatch.setattr(destino, "soma", lambda e, n: "0" * 64 if n.endswith("-full.nupkg") else real(e, n))
    with pytest.raises(pub.Parou) as erro:
        _publicar(a, destino=destino)
    assert "foi apagada" in str(erro.value) and "ATENÇÃO" not in str(erro.value), erro.value
    assert destino.situacao(ETIQUETA) is None


class _DestinoQueNaoLeDepoisDeLiberar(pub.DestinoPasta):
    """Uma pasta de verdade em que a leitura da situação falha (a internet caindo) logo depois de liberar."""

    def __init__(self, raiz):
        """liberou: já pediu para liberar."""
        super().__init__(raiz)
        self.liberou = False

    def liberar(self, etiqueta):
        """Libera de verdade e marca."""
        super().liberar(etiqueta)
        self.liberou = True

    def situacao(self, etiqueta):
        """Depois de liberar, não responde (como sem internet)."""
        if self.liberou:
            raise pub.Parou("não consegui perguntar ao destino (sem internet, de mentira)")
        return super().situacao(etiqueta)


def test_achado4_depois_de_liberar_a_leitura_que_falha_nao_apaga_a_versao(ambiente):
    """Achado 4 (decisão técnica da gerente, D-014, 19/11): se a leitura logo depois de liberar falhar, a versão
    liberada NÃO é apagada (o número não pode ficar livre para outro conteúdo); a frase diz "não deu para reconferir
    agora" e "NÃO apaguei"."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueNaoLeDepoisDeLiberar(a["servidor"])
    with pytest.raises(pub.Parou) as erro:
        _publicar(a, destino=destino)
    assert "não deu para reconferir agora" in str(erro.value) and "NÃO apaguei" in str(erro.value)
    assert (a["servidor"] / ETIQUETA).is_dir(), "a versão liberada foi apagada"


def test_achado5_erro_do_disco_vira_frase(ambiente, monkeypatch, capsys):
    """Achado 5: um erro do disco (o lugar do rascunho ocupado por um arquivo) saía como a tela de erro do Python.
    Agora a linha de comando diz "PAREI: o disco não deixou terminar" e devolve 1."""
    a = ambiente
    ocupado = a["tmp"] / "rascunho-ocupado"
    ocupado.write_text("sou um arquivo", encoding="utf-8")
    monkeypatch.setattr(pub, "pasta_do_rascunho", lambda: ocupado)
    monkeypatch.setattr(pub, "achar_chave", lambda *x, **k: CHAVE)
    # o vpk de mentira: no Windows do GitHub não há vpk instalado, e a linha de comando o procura antes do rascunho
    # (achado da rodada 44661337397; o teste supunha o PC do Samuel, família F4 do catálogo)
    monkeypatch.setattr(empacotar, "achar_vpk", lambda: a["vpk"])
    _publicar_o_motor(a)
    assert pub.main(["--pasta", str(a["servidor"])]) == 1
    saida = capsys.readouterr().out
    assert "PAREI: o disco não deixou terminar" in saida and "Traceback" not in saida


def test_achado8_o_arquivo_do_motor_em_instalar_e_recusado_na_atualizacao(tmp_path):
    """Achado 8: a conferência do pacote da atualização recusa também o arquivo do motor em instalar\\ (lido de
    SAIDAS), e o do instalador o exige."""
    nupkg = tmp_path / "p.nupkg"
    with zipfile.ZipFile(nupkg, "w") as z:
        for relativo in empacotar.esperados_no_pacote_do_velopack(None, empacotar.ATUALIZACAO):
            z.writestr(empacotar.PASTA_NO_NUPKG + relativo, b"x")
        z.writestr(empacotar.PASTA_NO_NUPKG + "instalar/" + versao.arquivo_do_motor(1), b"x")
    assert any("instalar/motor-kraken-" in p
               for p in empacotar.conferir_pacote_do_velopack(nupkg, None, empacotar.ATUALIZACAO))
    assert not empacotar.proibidos_no_pacote_do_velopack(empacotar.INSTALADOR)[1:]


def test_achado11_etiqueta_com_quebra_de_linha_e_recusada():
    """Achado 11: "v1.2.0" com quebra de linha no fim passava (o "$" casa antes dela); agora a etiqueta é conferida
    inteira."""
    assert pub.e_etiqueta("v1.2.0") and pub.e_etiqueta("motor-kraken-1")
    for errada in ("v1.2.0\n", "v1.2.0\r\n", "motor-kraken-1\n", " v1.2.0", "v1.2", "../v1.2.0"):
        assert not pub.e_etiqueta(errada), repr(errada)
        with pytest.raises(pub.Parou):
            pub.DestinoPasta(Path("x")).situacao(errada)


class _DestinoQueMente(pub.DestinoPasta):
    """Uma pasta de verdade que, na leitura de volta, mente de um jeito escolhido (para provar cada conferência)."""

    def __init__(self, raiz, mentira: str, servidor: Path | None = None):
        """mentira: 'arquivo a mais' | 'indice' | 'assinatura' | 'motor sumiu' | 'nao apaga'."""
        super().__init__(raiz)
        self.mentira = mentira
        self.servidor = servidor
        self.enviados = 0

    def arquivos(self, etiqueta):
        """'arquivo a mais': a lista lida tem um arquivo que não foi enviado."""
        lidos = super().arquivos(etiqueta)
        if self.mentira == "arquivo a mais" and etiqueta == ETIQUETA:
            lidos[empacotar.nome_do_setup()] = 1
        return lidos

    def baixar(self, etiqueta, nome, pasta_local):
        """'indice': o índice lido aponta para outra soma; 'assinatura': a assinatura lida é de outra chave."""
        baixado = super().baixar(etiqueta, nome, pasta_local)
        if etiqueta == ETIQUETA and self.mentira == "indice" and nome == empacotar.NOME_DO_INDICE:
            baixado.write_text(baixado.read_text(encoding="utf-8").replace('"SHA256": "', '"SHA256": "00'),
                               encoding="utf-8")
        if etiqueta == ETIQUETA and self.mentira == "assinatura" and nome.endswith(".assinatura"):
            nupkg = empacotar.nupkg_inteiro(Path("."), VERSAO).name
            v = assinatura.VersaoAssinada(versao.ID_DO_PACOTE, VERSAO, nupkg, super().soma(etiqueta, nupkg))
            baixado.write_text(assinatura.escrever_assinatura(OUTRA_CHAVE, v), encoding="utf-8")
        return baixado

    def enviar(self, etiqueta, arquivo):
        """'motor sumiu': depois do primeiro envio da versão, a publicação do motor some do destino."""
        super().enviar(etiqueta, arquivo)
        if self.mentira == "motor sumiu" and etiqueta == ETIQUETA:
            shutil.rmtree(self.raiz / versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR), ignore_errors=True)

    def apagar(self, etiqueta):
        """'nao apaga': diz que apagou e não apaga."""
        if self.mentira == "nao apaga":
            return None
        return super().apagar(etiqueta)


@pytest.mark.parametrize("mentira, frase", [
    ("arquivo a mais", "e o enviado foi"),              # N1: a lista lida do destino ("nada a mais")
    ("indice", "não aponta para o pacote"),             # N3: o índice lido de volta
    ("assinatura", "assinatura lida"),                  # N14: a assinatura lida de volta do destino
    ("motor sumiu", "não está publicado"),              # N4: o motor lido de novo antes de liberar (D-790)
])
def test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar(ambiente, mentira, frase):
    """N1, N3, N4, N14 (achado 3): cada conferência da leitura de volta tem o seu teste. O destino mente num ponto; a
    versão não é liberada, a frase diz o quê, e o rascunho do destino é apagado."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueMente(a["servidor"], mentira)
    with pytest.raises(pub.Parou, match=frase):
        _publicar(a, destino=destino)
    assert destino.situacao(ETIQUETA) is None


def test_n5_o_apagar_que_nao_apaga_e_acusado(ambiente):
    """N5 (achado 3): o --apagar confere, lendo de volta, que sumiu; um destino que diz que apagou e não apaga é
    acusado ("continua lá")."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueMente(a["servidor"], "nao apaga")
    with pytest.raises(pub.Parou, match="continua lá"):
        pub.apagar_publicacao(destino, versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR))


def test_n6_a_conferencia_do_fim_acusa_o_setup_exe(tmp_path):
    """N6 (achado 3): a conferência do fim (a tela da D-795) acusa o Setup.exe na pasta de saída e no destino."""
    saida = tmp_path / "saida"
    saida.mkdir()
    (saida / empacotar.nome_do_setup()).write_bytes(b"x")
    destino = pub.DestinoPasta(tmp_path / "servidor")
    linhas = pub.conferencia_do_fim(destino, ETIQUETA, saida, None)
    assert any("ATENÇÃO" in l and "pasta de saída" in l for l in linhas), linhas
    (saida / empacotar.nome_do_setup()).unlink()
    destino.criar_rascunho(ETIQUETA, "t", "n")
    falso = tmp_path / empacotar.nome_do_setup()
    falso.write_bytes(b"x")
    destino.enviar(ETIQUETA, falso)
    linhas = pub.conferencia_do_fim(destino, ETIQUETA, saida, None)
    assert any("ATENÇÃO" in l and "no destino" in l for l in linhas), linhas


def test_n8_o_msi_nao_fica_na_pasta_de_saida_se_a_versao_nao_saiu(ambiente):
    """N8 (achado 3): com o instalador pedido e a publicação falhando depois, o .msi não fica na pasta de saída."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueMente(a["servidor"], "indice")
    with pytest.raises(pub.Parou):
        _publicar(a, destino=destino, com_instalador=True)
    assert len(_vezes_que_o_vpk_rodou(a)) == 2, "as duas passadas do vpk tinham de rodar"
    assert not any(n.endswith(".msi") for n in _tudo_em(a["saida"])), _tudo_em(a["saida"])


def test_achado1_quem_decide_se_apagou_e_a_leitura_de_volta(ambiente, monkeypatch):
    """Achado 1 (o "leia de volta se sumiu", F5): o gh apaga a publicação liberada e sai com erro porque a etiqueta não
    saiu; a leitura diz que a publicação sumiu, então ela está apagada, e a frase traz o aviso do gh (a etiqueta pode
    ter ficado). Nunca "não apagou" sem ler."""
    gh = _GitHubDeMentira(ambiente["tmp"])
    gh.falhar_ao_apagar_a_etiqueta = True
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    destino.criar_rascunho(ETIQUETA, "t", "n")
    destino.liberar(ETIQUETA)
    aviso = pub.apagar_publicacao(destino, ETIQUETA)
    assert destino.situacao(ETIQUETA) is None and aviso and "HTTP 500" in aviso


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 3 (relatório 2 de quem tentou quebrar, 19/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

class _DestinoQueLiberaEPerdeAResposta(pub.DestinoPasta):
    """Uma pasta de verdade em que o liberar MUDA a pasta e depois devolve erro (a resposta se perdeu na rede), e a
    primeira leitura da situação depois disso ainda vê o estado antigo ("rascunho", uma leitura atrasada); as outras
    veem o de verdade. É o caso 1 do anexo `liberada_apagada.py.txt` do relatório 2."""

    def __init__(self, raiz):
        """atrasadas: quantas leituras ainda vão mentir "rascunho" depois de liberar."""
        super().__init__(raiz)
        self.atrasadas = None

    def liberar(self, etiqueta):
        """Libera de verdade e diz que deu erro."""
        super().liberar(etiqueta)
        if etiqueta == ETIQUETA:
            self.atrasadas = 1
            raise pub.Parou("a resposta do liberar se perdeu (de mentira)")

    def situacao(self, etiqueta):
        """A leitura atrasada logo depois de liberar."""
        if etiqueta == ETIQUETA and self.atrasadas:
            self.atrasadas -= 1
            return "rascunho"
        return super().situacao(etiqueta)


def test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada(ambiente):
    """Achado 1 do relatório 2 de quem tentou quebrar (19/11/2026, família F5): a regra "só o rascunho é apagado" era
    decidida numa leitura, e o apagar lia de novo por conta própria; com uma leitura atrasada ("rascunho") logo depois
    de um liberar que chegou ao destino e devolveu erro, o publicar apagou a versão LIBERADA e disse "foi apagada
    (conferido)". Agora o apagar do caminho de erro só apaga o rascunho, lido de novo ali dentro (apagar_publicacao com
    so_rascunho, e o próprio destino só toca no rascunho): a versão liberada continua e a frase diz "NÃO apaguei"."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueLiberaEPerdeAResposta(a["servidor"])
    with pytest.raises(pub.Parou) as erro:
        _publicar(a, destino=destino)
    assert (a["servidor"] / ETIQUETA).is_dir(), "a versão liberada foi apagada"
    assert sorted(f.name for f in (a["servidor"] / ETIQUETA).iterdir()), "a versão liberada ficou vazia"
    assert "NÃO apaguei" in str(erro.value) and "foi apagada" not in str(erro.value), erro.value
    # D-821 (Samuel, 21/11/2026: "ok", à troca de "em a pasta" por "na pasta"): antes "ficou liberada em"
    assert "ficou liberada na pasta" in str(erro.value), "a frase tem de dizer que a versão ficou liberada (lido depois)"


class _GitHubQueLiberaEPerdeAResposta(_GitHubDeMentira):
    """O gh de mentira em que o "edit --draft=false" libera e devolve erro, e o "view" seguinte ainda diz isDraft (uma
    leitura atrasada do GitHub)."""

    def __init__(self, tmp: Path):
        """atrasadas: quantos "view" ainda vão mentir "rascunho" depois de liberar."""
        super().__init__(tmp)
        self.atrasadas = 0

    def __call__(self, *argumentos, limite_s=600):
        """Como o gh de mentira, com o liberar que perde a resposta e a leitura atrasada."""
        a = list(argumentos)
        if a[1] == "edit" and a[2] == ETIQUETA:
            super().__call__(*argumentos, limite_s=limite_s)
            self.atrasadas = 1
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502: a resposta se perdeu (de mentira)")
        if a[1] == "view" and a[2] == ETIQUETA and self.atrasadas:
            self.atrasadas -= 1
            p = self.publicacoes[ETIQUETA]
            return subprocess.CompletedProcess(a, 0, json.dumps({"isDraft": True, "tagName": ETIQUETA, "assets": [
                {"name": n, "size": len(d)} for n, d in p["arquivos"].items()]}), "")
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada(ambiente, monkeypatch):
    """Achado 1 do relatório 2, no GitHub (gh de mentira; o de verdade é da prova à vista): o liberar chega e a resposta
    se perde; o primeiro "view" ainda diz rascunho. O apagar do caminho de erro lê de novo no próprio destino logo antes
    de pedir (DestinoGitHub.apagar_rascunho), vê "liberada" e NÃO pede para apagar."""
    a = ambiente
    gh = _GitHubQueLiberaEPerdeAResposta(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    with pytest.raises(pub.Parou) as erro:
        _publicar(a, destino=destino)
    assert gh.publicacoes[ETIQUETA]["rascunho"] is False, "a versão liberada foi apagada"
    assert not any(p[1] == "delete" and p[2] == ETIQUETA for p in gh.pedidos), "pediu para apagar a liberada"
    assert "NÃO apaguei" in str(erro.value), erro.value


class _DestinoQueNaoLibera(pub.DestinoPasta):
    """Uma pasta de verdade em que o liberar falha e não muda nada (continua rascunho)."""

    def liberar(self, etiqueta):
        """Não libera."""
        raise pub.Parou("o destino não deixou liberar (de mentira)")


# O teste da volta 3 "test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho" (achado 5 do
# relatório 2) cobrava que, quando o PEDIDO de liberar falha e a publicação continua rascunho, o rascunho era apagado.
# A D-816 (Samuel, 20/11/2026: "A , mas onde estamos antes de você fazer qualquer processo") tirou esse comportamento:
# "depois de pedir ao GitHub para liberar a versão, o programa nunca apaga nada"; "Na pasta das provas (não no GitHub)
# vale a mesma regra". O mesmo caso (o _DestinoQueNaoLibera, na pasta) e o do GitHub passaram a ser cobrados do jeito
# novo, com a prova de que o antigo saiu (o rascunho continua e a frase diz o comando), em
# test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando (volta 4, mais abaixo). CLAUDE.md §11,
# ponto 4: quando a decisão substitui um comportamento antigo, a prova confere que o antigo saiu. O achado voltou a quem
# escreveu pela D-775 (volta 4).


class _DestinoQueTrocaOMotor(pub.DestinoPasta):
    """Uma pasta de verdade em que, durante a publicação da versão, o motor publicado é trocado por OUTRO com a mesma
    etiqueta e uma assinatura válida da mesma chave (alguém publicou de novo no meio)."""

    def enviar(self, etiqueta, arquivo):
        """Depois do primeiro envio da versão, troca o motor publicado (o arquivo e a assinatura)."""
        super().enviar(etiqueta, arquivo)
        if etiqueta == ETIQUETA and not getattr(self, "trocado", False):
            self.trocado = True
            v = ocr_kraken.VERSAO_DO_MOTOR
            zip_do_motor = self.raiz / versao.etiqueta_do_motor(v) / versao.arquivo_do_motor(v)
            zip_do_motor.write_bytes(zip_do_motor.read_bytes() + b"outro conteudo")
            pub.assinar_arquivo(CHAVE, zip_do_motor, versao.ID_DO_PACOTE_DO_MOTOR, str(v), PUBLICA)


def test_volta3_achado6_o_motor_trocado_durante_a_publicacao_impede_liberar(ambiente):
    """Achado 6 do relatório 2 (família F3): a comparação "o motor publicado mudou durante a publicação" não tinha
    teste (o do N4 apaga o motor e a leitura para antes). Aqui o motor é trocado por outro, com a mesma etiqueta e
    assinatura válida: a versão não é liberada (o motor-exigido.json dela aponta para o motor de antes)."""
    a = ambiente
    _publicar_o_motor(a)
    destino = _DestinoQueTrocaOMotor(a["servidor"])
    with pytest.raises(pub.Parou, match="o motor publicado mudou durante a publicação"):
        _publicar(a, destino=destino)
    assert destino.situacao(ETIQUETA) is None


class _EscritaQueEnche:
    """Um arquivo aberto para escrever que grava 10 bytes e depois dá "disco cheio" (como o D: enchendo no meio)."""

    def __init__(self, real):
        """real: o arquivo de verdade."""
        self.real = real
        self.escritos = 0

    def write(self, dados):
        """Grava até 10 bytes no total; depois, disco cheio."""
        falta = 10 - self.escritos
        if len(dados) > falta:
            self.real.write(bytes(dados[:max(falta, 0)]))
            self.real.flush()
            self.escritos = 10
            raise OSError(28, "Não há espaço suficiente no disco (de mentira)", self.real.name)
        self.escritos += len(dados)
        return self.real.write(dados)

    def __enter__(self):
        """Para o `with` de quem abriu."""
        return self

    def __exit__(self, *erro):
        """Fecha o arquivo de verdade."""
        self.real.close()

    def __getattr__(self, nome):
        """O resto, do arquivo de verdade."""
        return getattr(self.real, nome)


def test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo(ambiente, monkeypatch, capsys):
    """Achado 2 do relatório 2 de quem tentou quebrar (19/11/2026, família F5): depois de a versão estar liberada, a
    cópia do .msi para a pasta de saída falhou no meio (disco cheio) e ficou um .msi de 10 bytes COM O NOME CERTO, e a
    frase dizia "o que esta vez fez pela metade foi apagado". Agora a cópia vai para um nome provisório e só ganha o
    nome certo depois de conferida (tamanho e soma lidos de volta); na falha o pedaço é apagado (conferido), a frase
    diz que a versão FOI publicada e que o instalador está inteiro na publicação, e a conferência do fim diz que o
    instalador NÃO está na pasta de saída. A falha do disco é provocada no arquivo que se abre para escrever na pasta de
    saída (o mesmo ponto no código antigo e no novo)."""
    import builtins

    a = ambiente
    _publicar_o_motor(a)
    verdadeiro = builtins.open

    def aberto(arquivo, modo="r", *x, **k):
        """Escrever um .msi na pasta de saída enche o disco no meio."""
        real = verdadeiro(arquivo, modo, *x, **k)
        caminho = Path(str(arquivo))
        if "w" in modo and a["saida"] in caminho.parents and ".msi" in caminho.name:
            return _EscritaQueEnche(real)
        return real

    monkeypatch.setattr(builtins, "open", aberto)
    with pytest.raises((pub.Parou, OSError)) as erro:
        _publicar(a, com_instalador=True)
    monkeypatch.undo()
    saida = capsys.readouterr().out
    assert _tudo_em(a["saida"] / ETIQUETA) == [], f"ficou na pasta de saída: {_tudo_em(a['saida'] / ETIQUETA)}"
    assert pub.DestinoPasta(a["servidor"]).situacao(ETIQUETA) == "liberada"
    assert "FOI publicada" in str(erro.value) and "está inteiro na publicação" in str(erro.value), erro.value
    assert "NÃO está na pasta de saída" in saida, saida


def test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho(ambiente, capsys, tmp_path):
    """Achado 2 do relatório 2: a conferência do fim compara o .msi da pasta de saída com o feito no rascunho (tamanho e
    soma, lidos do arquivo de lá). Com o caminho inteiro: igual. Direto na conferência: um .msi diferente, um que não foi
    feito agora e um pedaço de cópia (.copiando) são acusados."""
    a = ambiente
    _publicar_o_motor(a)
    _publicar(a, com_instalador=True)
    assert "igual ao feito agora (tamanho e soma conferidos)" in capsys.readouterr().out
    saida = tmp_path / "saida-direta"
    saida.mkdir()
    nome = empacotar.nome_do_msi_publicado(VERSAO)
    (saida / nome).write_bytes(b"outro msi")
    (saida / "velho-win.msi").write_bytes(b"x")
    (saida / (nome + ".copiando")).write_bytes(b"x")
    feito = (nome, len(b"msi certo"), assinatura.soma_sha256(a["tmp"] / "chave.txt"))
    linhas = pub.conferencia_do_fim(pub.DestinoPasta(a["servidor"]), ETIQUETA, saida, None, feito)
    assert any("ATENÇÃO" in l and "diferente do feito agora" in l for l in linhas), linhas
    assert any("ATENÇÃO" in l and "velho-win.msi" in l and "não foi feito agora" in l for l in linhas), linhas
    assert any("ATENÇÃO" in l and ".copiando" in l for l in linhas), linhas
    (saida / nome).unlink()
    linhas = pub.conferencia_do_fim(pub.DestinoPasta(a["servidor"]), ETIQUETA, saida, None, feito)
    assert any("NÃO está na pasta de saída" in l for l in linhas), linhas


def test_volta3_achado2_a_frase_do_fim_nao_diz_apagado_sem_conferir(ambiente, monkeypatch, capsys):
    """Achado 2 do relatório 2: a linha de comando dizia "O que esta vez fez pela metade foi apagado" depois de qualquer
    erro do disco, sem conferir. Agora aponta para o que foi lido (a conferência do fim)."""
    a = ambiente
    ocupado = a["tmp"] / "rascunho-ocupado"
    ocupado.write_text("sou um arquivo", encoding="utf-8")
    monkeypatch.setattr(pub, "pasta_do_rascunho", lambda: ocupado)
    monkeypatch.setattr(pub, "achar_chave", lambda *x, **k: CHAVE)
    monkeypatch.setattr(empacotar, "achar_vpk", lambda: a["vpk"])
    _publicar_o_motor(a)
    assert pub.main(["--pasta", str(a["servidor"])]) == 1
    saida = capsys.readouterr().out
    assert "PAREI: o disco não deixou terminar" in saida and "conferência do fim" in saida
    assert "foi apagado" not in saida.split("PAREI:")[-1], saida


def test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia(ambiente, monkeypatch):
    """Achado 7 do relatório 2 (D-776): o arquivo do motor baixado para o rascunho (o instalador) ficava fora da conta
    do espaço e da vigia. Agora: (1) a conta soma o baixado (espaco_que_vai_usar, baixado_para_o_rascunho), e o
    publicar o passa; (2) o download é vigiado pela vigia única (vigia_do_espaco): com o disco abaixo da reserva no
    começo do download, ele para, o segundo vpk nem roda, e nada fica pela metade."""
    a = ambiente
    um_gb = empacotar.GB
    so_vpk = empacotar.espaco_que_vai_usar(um_gb, (empacotar.ATUALIZACAO, empacotar.INSTALADOR), um_gb // 2)
    com_baixado = empacotar.espaco_que_vai_usar(um_gb, (empacotar.ATUALIZACAO, empacotar.INSTALADOR), um_gb // 2,
                                                baixado_para_o_rascunho=um_gb // 2)
    assert com_baixado == so_vpk + um_gb // 2
    _publicar_o_motor(a)
    pedidos = []
    verdadeira = empacotar.conferir_espaco
    monkeypatch.setattr(empacotar, "conferir_espaco", lambda pasta, precisa, *x: pedidos.append(precisa) or
                        verdadeira(pasta, precisa, *x))
    v = ocr_kraken.VERSAO_DO_MOTOR
    tamanho = (a["servidor"] / versao.etiqueta_do_motor(v) / versao.arquivo_do_motor(v)).stat().st_size
    pasta = empacotar.tamanho_da_pasta(a["pasta"])
    _publicar(a, com_instalador=True)
    assert pedidos[0] == empacotar.espaco_que_vai_usar(pasta, (empacotar.ATUALIZACAO, empacotar.INSTALADOR), tamanho,
                                                       baixado_para_o_rascunho=tamanho)
    # (2) a vigia no download: o disco cai abaixo da reserva assim que a pasta do motor baixado nasce
    shutil.rmtree(a["servidor"] / ETIQUETA)
    shutil.rmtree(a["saida"], ignore_errors=True)
    a["diario"].unlink()

    def livre(pasta_do_disco):
        """Muito espaço, até o download do motor começar."""
        baixando = any(p.name == "motor" for p in Path(a["rascunho"]).rglob("motor"))
        return 5 * um_gb if baixando else 500 * um_gb

    monkeypatch.setattr(empacotar, "espaco_livre", livre)
    with pytest.raises(pub.Parou, match="reserva"):
        _publicar(a, com_instalador=True)
    assert len(_vezes_que_o_vpk_rodou(a)) == 1, "o segundo vpk rodou com o disco abaixo da reserva"
    assert _rascunhos_que_sobraram(a) == []


def test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia(tmp_path, monkeypatch):
    """Achado 7 do relatório 2, no GitHub: o download pelo gh é vigiado enquanto o gh roda (DestinoGitHub._gh com a
    vigia). De verdade: um "gh" de prova (um programa de verdade que demoraria 60 s) é fechado assim que a vigia manda
    parar, e a frase diz o motivo."""
    lento = _programa_de_prova(tmp_path / "gh.exe", "import time\ntime.sleep(60)\n")
    monkeypatch.setattr(empacotar, "INTERVALO_DA_VIGIA_S", 0.2)
    destino = pub.DestinoGitHub("dono/projeto", gh=str(lento))
    inicio = time.perf_counter()
    with pytest.raises(pub.Parou, match="abaixo da reserva"):
        destino.baixar_vigiado(versao.etiqueta_do_motor(1), versao.arquivo_do_motor(1), tmp_path / "motor",
                               lambda: "o disco ficou abaixo da reserva (de mentira)")
    assert time.perf_counter() - inicio < 20, "a vigia não fechou o gh"


def test_volta3_achado7_o_nome_do_motor_so_em_versao_py():
    """Achado 7 do relatório 2 (§11.12, "uma lista é escrita uma vez"): o começo "motor-kraken-" dos nomes do motor
    publicado estava escrito à mão no publicar (a etiqueta aceita) e em dois lugares do empacotar. Agora só em
    versao.py (PREFIXO_DO_MOTOR, etiqueta_do_motor, arquivo_do_motor). Lido no código (os textos do programa, fora os
    comentários e as explicações das funções)."""
    import ast

    for arquivo in ("publicar_versao_kaique.py", "empacotar.py", "servidor_das_versoes.py"):
        arvore = ast.parse((RAIZ / arquivo).read_text(encoding="utf-8"))
        explicacoes = {id(no.body[0].value) for no in ast.walk(arvore)
                       if isinstance(no, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
                       and no.body and isinstance(no.body[0], ast.Expr) and isinstance(no.body[0].value, ast.Constant)}
        textos = [no.value for no in ast.walk(arvore) if isinstance(no, ast.Constant) and isinstance(no.value, str)
                  and id(no) not in explicacoes and "motor-kraken-" in no.value]
        assert textos == [], f"{arquivo} escreve o nome do motor à mão: {textos}"
    assert pub.e_etiqueta(versao.etiqueta_do_motor(3)) and not pub.e_etiqueta(versao.PREFIXO_DO_MOTOR + "x")


class _EscritaQueTroca(_EscritaQueEnche):
    """Um arquivo aberto para escrever que troca um byte do que grava, sem dar erro (o disco que grava errado)."""

    def write(self, dados):
        """Grava com o primeiro byte trocado."""
        dados = bytes(dados)
        return self.real.write(bytes([dados[0] ^ 0xFF]) + dados[1:] if dados else dados)


def test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia(tmp_path, monkeypatch):
    """Achado 2 do relatório 2 (a cópia conferida, empacotar.copiar_inteiro, o lugar único da cópia do publicar): cada
    proteção dela tem o seu caso. (1) A cópia que sai diferente (um byte trocado ao gravar, sem erro) é recusada pela
    leitura de volta e não fica nada com o nome certo nem o pedaço; (2) a vigia que manda parar no meio para a cópia e
    apaga o pedaço; (3) a que manda parar antes nem começa ("nada foi copiado"); (4) a cópia certa chega inteira."""
    import builtins

    origem = tmp_path / "origem.bin"
    origem.write_bytes(os.urandom(300_000))
    alvo = tmp_path / "saida" / "copia.bin"
    alvo.parent.mkdir()
    verdadeiro = builtins.open

    def aberto(arquivo, modo="r", *x, **k):
        """Gravar na pasta de saída troca um byte."""
        real = verdadeiro(arquivo, modo, *x, **k)
        return _EscritaQueTroca(real) if "w" in modo and alvo.parent in Path(str(arquivo)).parents else real

    monkeypatch.setattr(builtins, "open", aberto)
    with pytest.raises(OSError, match="saiu diferente"):
        empacotar.copiar_inteiro(origem, alvo)
    monkeypatch.setattr(builtins, "open", verdadeiro)
    assert list(alvo.parent.iterdir()) == []
    monkeypatch.setattr(empacotar, "PEDACO_DA_COPIA", 50_000)
    monkeypatch.setattr(empacotar, "VIGIA_A_CADA", 50_000)
    olhadas = []

    def vigia():
        """Deixa começar; manda parar na segunda olhada (no meio da cópia)."""
        olhadas.append(1)
        return "o disco ficou abaixo da reserva (de mentira)" if len(olhadas) >= 2 else None

    with pytest.raises(OSError, match="parei de copiar.*foi apagado"):
        empacotar.copiar_inteiro(origem, alvo, vigia)
    assert list(alvo.parent.iterdir()) == []
    with pytest.raises(OSError, match="nada foi copiado"):
        empacotar.copiar_inteiro(origem, alvo, lambda: "parar (de mentira)")
    empacotar.copiar_inteiro(origem, alvo, lambda: None)
    assert alvo.read_bytes() == origem.read_bytes() and [p.name for p in alvo.parent.iterdir()] == ["copia.bin"]


def test_volta3_achado4_a_vigia_fecha_o_filho_do_vpk_antes_de_soltar_o_grupo(ambiente, monkeypatch, tmp_path):
    """Achado 4 do relatório 2 (família F3): com o fechamento do grupo desligado e a frase "conferido" posta direto, os
    testes do achado 2 e do N10 passavam, porque quem fechava o filho era o fechar-ao-fechar do fim do `with`, depois
    da frase. Aqui o soltar do grupo é segurado até o fim do teste: o filho do vpk tem de estar parado quando o
    rodar_vpk devolve a frase, só pelo `fechar_tudo` (fechar só o vpk não passa)."""
    from core import windows

    batida = tmp_path / "filho-do-vpk.txt"
    monkeypatch.setenv("VPK_FALSO_ESPERA", "60")
    monkeypatch.setenv("VPK_FALSO_FILHO", str(batida))
    segurados = []
    verdadeiro = windows.ProgramaEmGrupo.soltar
    monkeypatch.setattr(windows.ProgramaEmGrupo, "soltar", lambda self: segurados.append(self))
    rascunho = tmp_path / "publicar-vigia4"
    rascunho.mkdir()
    try:
        motivo = empacotar.rodar_vpk(empacotar.comando_do_vpk(ambiente["vpk"], ambiente["pasta"], rascunho / "s",
                                                              VERSAO, com_msi=False), rascunho, intervalo_s=0.3,
                                     livre=lambda _p: 19 * empacotar.GB if batida.exists() else 100 * empacotar.GB)
        assert segurados, "o grupo não passou pelo soltar"
        assert motivo and "fechados (conferido)" in motivo, motivo
        assert not _batida_viva(batida), "o filho do vpk só pararia ao soltar o grupo"
    finally:
        for programa in segurados:
            verdadeiro(programa)


def test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo(tmp_path):
    """Achado 2 do relatório 2, o caso que o apagar do pedaço não cobre: o publicar é fechado no meio da cópia (o
    Gerenciador de Tarefas, a energia), e nada roda depois para limpar. Com a cópia indo para um nome provisório, o que
    fica é o "<nome>.copiando", nunca um arquivo pela metade com o nome certo (que a conferência do fim e quem abre a
    pasta tomariam por inteiro). De verdade: um processo que copia devagar é fechado à força no meio."""
    origem = tmp_path / "grande.bin"
    origem.write_bytes(os.urandom(2_000_000))
    alvo = tmp_path / "saida" / "grande.bin"
    alvo.parent.mkdir()
    copiador = tmp_path / "copiador.py"
    copiador.write_text(
        "import sys, time\n"
        f"sys.path.insert(0, {str(RAIZ)!r})\n"
        "import empacotar\n"
        "empacotar.PEDACO_DA_COPIA = empacotar.VIGIA_A_CADA = 100_000\n"
        f"empacotar.copiar_inteiro({str(origem)!r}, {str(alvo)!r}, lambda: time.sleep(0.3))\n", encoding="utf-8")
    processo = subprocess.Popen([sys.executable, str(copiador)])
    try:
        fim = time.monotonic() + 30
        while time.monotonic() < fim and not any(p.stat().st_size > 0 for p in alvo.parent.iterdir()):
            time.sleep(0.05)
        assert any(alvo.parent.iterdir()), "a cópia nem começou"
    finally:
        processo.kill()
        processo.wait()
    assert not alvo.exists(), "ficou um arquivo pela metade com o nome certo"


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 4 (relatório 3 de quem tentou quebrar, 20/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

ETIQUETA_DO_MOTOR = versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR)


class _PastaQueLiberaEAtrasa(pub.DestinoPasta):
    """Uma pasta de verdade em que o liberar da etiqueta escolhida MUDA a pasta e devolve erro (a resposta se perdeu),
    e as `atrasos` leituras seguintes da situação ainda dizem "rascunho" (leituras atrasadas)."""

    def __init__(self, raiz, alvo: str, atrasos: int, libera: bool = True, interromper: bool = False):
        """alvo: a etiqueta; libera=False: o liberar falha sem mudar nada; interromper: o liberar vira Ctrl+C."""
        super().__init__(raiz)
        self.alvo, self.atrasos, self.libera, self.interromper = alvo, atrasos, libera, interromper
        self.atrasadas = 0
        self.apagar_pedido: list[str] = []

    def liberar(self, etiqueta):
        """Libera (ou não) e devolve erro (ou Ctrl+C)."""
        if etiqueta != self.alvo:
            return super().liberar(etiqueta)
        if self.libera:
            super().liberar(etiqueta)
        self.atrasadas = self.atrasos
        if self.interromper:
            raise KeyboardInterrupt
        raise pub.Parou("a resposta do liberar se perdeu (de mentira)")

    def situacao(self, etiqueta):
        """As leituras atrasadas depois de liberar."""
        if etiqueta == self.alvo and self.atrasadas:
            self.atrasadas -= 1
            return "rascunho"
        return super().situacao(etiqueta)

    def apagar(self, etiqueta):
        """Anota e apaga."""
        self.apagar_pedido.append(etiqueta)
        return super().apagar(etiqueta)

    def apagar_rascunho(self, etiqueta):
        """Anota e apaga o rascunho."""
        self.apagar_pedido.append(etiqueta)
        return super().apagar_rascunho(etiqueta)


class _GitHubQueLiberaEAtrasa(_GitHubDeMentira):
    """O gh de mentira em que o "edit --draft=false" da etiqueta escolhida libera (ou não) e devolve erro, e os
    `atrasos` "view" seguintes ainda dizem isDraft (leituras atrasadas do GitHub). É o Q1 de quem tentou quebrar,
    com o número de atrasos escolhido."""

    def __init__(self, tmp, alvo: str, atrasos: int, libera: bool = True):
        """alvo: a etiqueta; libera=False: o GitHub não libera (continua rascunho)."""
        super().__init__(tmp)
        self.alvo, self.atrasos, self.libera = alvo, atrasos, libera
        self.atrasadas = 0

    def __call__(self, *argumentos, limite_s=600):
        """Como o gh de mentira, com o liberar que perde a resposta e as leituras atrasadas."""
        a = list(argumentos)
        if a[1] == "edit" and a[2] == self.alvo:
            if self.libera:
                super().__call__(*argumentos, limite_s=limite_s)
            else:
                self.pedidos.append(a)
            self.atrasadas = self.atrasos
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502: a resposta se perdeu (de mentira)")
        if a[1] == "view" and a[2] == self.alvo and self.atrasadas:
            self.atrasadas -= 1
            self.pedidos.append(a)
            p = self.publicacoes[self.alvo]
            return subprocess.CompletedProcess(a, 0, json.dumps({"isDraft": True, "tagName": self.alvo, "assets": [
                {"name": n, "size": len(d)} for n, d in p["arquivos"].items()]}), "")
        return super().__call__(*argumentos, limite_s=limite_s)


def _publicar_um(a, o_que: str, destino):
    """Publica a versão (o motor já publicado antes) ou o motor, no destino dado; devolve a exceção do publicar."""
    if o_que == "versao":
        with pytest.raises(pub.Parou) as erro:
            _publicar(a, destino=destino)
    else:
        with pytest.raises(pub.Parou) as erro:
            _publicar_o_motor(a, destino=destino)
    return erro.value


def _conferir_frase_d816(frase: str, destino, etiqueta: str) -> None:
    """A frase da D-816: nada apagado, o que pode ter ficado, como conferir e o comando de apagar o rascunho."""
    assert "NÃO apaguei" in frase and "foi apagada" not in frase, frase
    assert "pode ter ficado" in frase and "liberada" in frase and "rascunho" in frase, frase
    assert "não deu para reconferir agora" in frase, frase
    assert destino.como_conferir(etiqueta) in frase, frase
    assert destino.comando_de_apagar(etiqueta) in frase, frase


@pytest.mark.parametrize("atrasos", [1, 2, 3, 10])
@pytest.mark.parametrize("onde", ["pasta", "github"])
def test_d816_depois_do_pedido_de_liberar_nada_e_apagado_com_qualquer_atraso(ambiente, monkeypatch, onde, atrasos):
    """D-816 (Samuel, 20/11/2026: "A , mas onde estamos antes de você fazer qualquer processo"; achado 1 do relatório 3
    de quem tentou quebrar, família F5): depois de pedir para liberar, o publicar nunca apaga nada, em nenhum destino,
    sem depender de leitura. Antes, com DUAS leituras atrasadas do GitHub depois de um liberar cuja resposta se perdeu,
    o publicar apagava a versão liberada e dizia "foi apagada (conferido)"; o teste do conserto anterior imitava só uma.
    Aqui: 1, 2, 3 e 10 leituras atrasadas, na pasta das provas e no GitHub (gh de mentira; o de verdade é da prova à
    vista): a versão liberada continua, nenhum pedido de apagar sai, e a frase diz o que pode ter ficado e os comandos."""
    a = ambiente
    if onde == "pasta":
        destino = _PastaQueLiberaEAtrasa(a["servidor"], ETIQUETA, atrasos)
    else:
        gh = _GitHubQueLiberaEAtrasa(a["tmp"], ETIQUETA, atrasos)
        destino = pub.DestinoGitHub("dono/projeto")
        monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    _conferir_frase_d816(frase, destino, ETIQUETA)
    if onde == "pasta":
        assert (a["servidor"] / ETIQUETA).is_dir() and any((a["servidor"] / ETIQUETA).iterdir())
        assert ETIQUETA not in destino.apagar_pedido
    else:
        assert gh.publicacoes[ETIQUETA]["rascunho"] is False, "a versão liberada foi apagada"
        assert not any(p[1] == "delete" and p[2] == ETIQUETA for p in gh.pedidos), "pediu para apagar"
    assert _rascunhos_que_sobraram(a) == []


@pytest.mark.parametrize("onde", ["pasta", "github"])
def test_d816_o_motor_tambem_nunca_e_apagado_depois_do_pedido_de_liberar(ambiente, monkeypatch, onde):
    """D-816, o outro caminho que chega em publicar_arquivos: a publicação do motor (--motor). O mesmo resultado da
    versão: duas leituras atrasadas depois do liberar e nada é apagado; a frase é a mesma."""
    a = ambiente
    if onde == "pasta":
        destino = _PastaQueLiberaEAtrasa(a["servidor"], ETIQUETA_DO_MOTOR, 2)
    else:
        gh = _GitHubQueLiberaEAtrasa(a["tmp"], ETIQUETA_DO_MOTOR, 2)
        destino = pub.DestinoGitHub("dono/projeto")
        monkeypatch.setattr(destino, "_gh", gh)
    frase = str(_publicar_um(a, "motor", destino))
    _conferir_frase_d816(frase, destino, ETIQUETA_DO_MOTOR)
    if onde == "pasta":
        assert (a["servidor"] / ETIQUETA_DO_MOTOR).is_dir()
    else:
        assert gh.publicacoes[ETIQUETA_DO_MOTOR]["rascunho"] is False
        assert not any(p[1] == "delete" for p in gh.pedidos)


@pytest.mark.parametrize("onde", ["pasta", "github"])
def test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando(ambiente, monkeypatch, onde):
    """D-816 ("Se sobrar um rascunho, a tela diz exatamente o que ficou e o comando para apagar depois"; "Na pasta das
    provas (não no GitHub) vale a mesma regra"): o pedido de liberar falha e a publicação continua rascunho. Antes
    (volta 3, achado 5 do relatório 2), o rascunho era apagado; a D-816 tirou isso: depois do pedido de liberar, nada
    se apaga. O rascunho fica, e a frase diz o comando de apagar."""
    a = ambiente
    if onde == "pasta":
        destino = _DestinoQueNaoLibera(a["servidor"])           # o mesmo caso do teste antigo da volta 3
        _publicar_o_motor(a)                                    # o motor, na mesma pasta, por uma que libera
    else:
        gh = _GitHubQueLiberaEAtrasa(a["tmp"], ETIQUETA, 0, libera=False)
        destino = pub.DestinoGitHub("dono/projeto")
        monkeypatch.setattr(destino, "_gh", gh)
        _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    _conferir_frase_d816(frase, destino, ETIQUETA)
    assert destino.situacao(ETIQUETA) == "rascunho", "o rascunho foi apagado depois do pedido de liberar"
    if onde == "github":
        assert not any(p[1] == "delete" and p[2] == ETIQUETA for p in gh.pedidos)
    # e o comando da frase apaga mesmo (o fim da prova)
    pub.apagar_publicacao(destino, ETIQUETA)
    assert destino.situacao(ETIQUETA) is None


def test_d816_ctrl_c_depois_do_pedido_de_liberar_nao_apaga(ambiente, capsys):
    """D-816 com o Ctrl+C logo depois do pedido de liberar: a interrupção segue, nada é apagado, e a frase sai na tela."""
    a = ambiente
    destino = _PastaQueLiberaEAtrasa(a["servidor"], ETIQUETA, 2, interromper=True)
    _publicar_o_motor(a, destino=destino)
    with pytest.raises(KeyboardInterrupt):
        _publicar(a, destino=destino)
    assert (a["servidor"] / ETIQUETA).is_dir() and ETIQUETA not in destino.apagar_pedido
    _conferir_frase_d816(capsys.readouterr().out, destino, ETIQUETA)


class _GitHubQueCaiDepoisDeApagar(_GitHubDeMentira):
    """O envio do pacote falha (antes do pedido de liberar); o apagar do rascunho dá certo; as leituras seguintes não
    respondem (a rede caiu). É o Q2 de quem tentou quebrar, no caminho de antes de liberar."""

    def __init__(self, tmp, cair_antes: bool = False):
        """cair_antes: a rede cai já na leitura de antes de apagar (nada é pedido)."""
        super().__init__(tmp)
        self.cair_antes = cair_antes
        self.caiu = False

    def __call__(self, *argumentos, limite_s=600):
        """O envio do .nupkg falha; depois do apagar (ou já no erro, com cair_antes), o "view" não responde."""
        a = list(argumentos)
        if a[1] == "upload" and a[2] == ETIQUETA and a[3].endswith(".nupkg"):
            self.pedidos.append(a)
            self.caiu = self.cair_antes
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502 ao enviar (de mentira)")
        if a[1] == "view" and a[2] == ETIQUETA and self.caiu:
            self.pedidos.append(a)
            return subprocess.CompletedProcess(a, 1, "", "error connecting to api.github.com")
        r = super().__call__(*argumentos, limite_s=limite_s)
        if a[1] == "delete" and a[2] == ETIQUETA:
            self.caiu = True
        return r


def test_volta4_achado3_a_frase_diz_se_pediu_para_apagar(ambiente, monkeypatch):
    """Achado 3 do relatório 3 de quem tentou quebrar (família F5): a frase dizia "NÃO apaguei" tendo pedido para
    apagar (e apagado). Agora quem escreve a frase é o apagar, que sabe se pediu: (1) pediu, apagou, e a leitura de
    depois não respondeu: "pedi para apagar ... não deu para conferir se sumiu", nunca "NÃO apaguei"; (2) a leitura de
    antes de apagar não respondeu: "NÃO pedi para apagar". Nos dois, o comando para conferir e apagar."""
    a = ambiente
    gh = _GitHubQueCaiDepoisDeApagar(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    assert [p for p in gh.pedidos if p[1] == "delete" and p[2] == ETIQUETA], "o rascunho tinha de ser pedido para apagar"
    assert "pedi para apagar" in frase and "não deu para conferir se sumiu" in frase, frase
    assert "NÃO apaguei" not in frase and "NÃO pedi" not in frase and "foi apagada" not in frase, frase
    assert destino.comando_de_apagar(ETIQUETA) in frase, frase
    primeiro = gh
    gh = _GitHubQueCaiDepoisDeApagar(a["tmp"], cair_antes=True)
    gh.publicacoes = {ETIQUETA_DO_MOTOR: primeiro.publicacoes[ETIQUETA_DO_MOTOR]}    # o motor já publicado
    monkeypatch.setattr(destino, "_gh", gh)
    frase = str(_publicar_um(a, "versao", destino))
    assert not [p for p in gh.pedidos if p[1] == "delete"], "pediu para apagar sem ler antes"
    assert "NÃO pedi para apagar" in frase and "pedi para apagar o" not in frase, frase
    assert destino.comando_de_apagar(ETIQUETA) in frase, frase


class _GitHubQueNaoVeORascunhoNovo(_GitHubDeMentira):
    """Logo depois de criar o rascunho da versão, o "view" ainda não o acha (leitura atrasada); o envio falha. É o Q3
    de quem tentou quebrar. Com perder_o_criar: o "create" cria e devolve erro (a resposta se perdeu)."""

    def __init__(self, tmp, perder_o_criar: bool = False):
        """perder_o_criar: o rascunho é criado e a resposta se perde (o view o vê normalmente)."""
        super().__init__(tmp)
        self.perder_o_criar = perder_o_criar

    def __call__(self, *argumentos, limite_s=600):
        """O envio falha; o view não vê o rascunho novo (ou o criar perde a resposta)."""
        a = list(argumentos)
        if a[1] == "create" and a[2] == ETIQUETA and self.perder_o_criar:
            super().__call__(*argumentos, limite_s=limite_s)
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502 ao criar (de mentira)")
        if a[1] == "upload" and a[2] == ETIQUETA:
            self.pedidos.append(a)
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502 ao enviar (de mentira)")
        if a[1] == "view" and a[2] == ETIQUETA and ETIQUETA in self.publicacoes and not self.perder_o_criar:
            self.pedidos.append(a)
            return subprocess.CompletedProcess(a, 1, "", "release not found")
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta4_achado4_nao_achei_logo_depois_de_criar_nao_e_apagado(ambiente, monkeypatch):
    """Achado 4 do relatório 3 de quem tentou quebrar (família F5): o rascunho acabou de ser criado, o envio falhou e a
    leitura ainda não o achava; o apagar entendia "já sumiu", não pedia nada, e a frase dizia "foi apagada
    (conferido)" com o rascunho no GitHub. Agora "não achei" logo depois de criar não é "sumiu": a frase diz "não achei
    o rascunho para apagar" e o comando para conferir e apagar. E o criar_rascunho entrou no caminho de erro: se ele
    cria e a resposta se perde, o rascunho é procurado e apagado (conferido), em vez de ficar calado no GitHub."""
    a = ambiente
    gh = _GitHubQueNaoVeORascunhoNovo(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    assert "foi apagada" not in frase and "não achei o rascunho" in frase, frase
    assert destino.comando_de_apagar(ETIQUETA) in frase, frase
    assert not [p for p in gh.pedidos if p[1] == "delete" and p[2] == ETIQUETA]
    perde = _GitHubQueNaoVeORascunhoNovo(a["tmp"], perder_o_criar=True)
    perde.publicacoes = {ETIQUETA_DO_MOTOR: gh.publicacoes[ETIQUETA_DO_MOTOR]}
    monkeypatch.setattr(destino, "_gh", perde)
    frase = str(_publicar_um(a, "versao", destino))
    assert ETIQUETA not in perde.publicacoes, "o rascunho criado (com a resposta perdida) ficou no GitHub"
    assert "foi apagada" in frase and "(conferido)" in frase, frase


# Um "gh" de prova DE VERDADE (um programa, pelo lançador do pip): anota os argumentos num arquivo; "view" responde a
# publicação SEM a soma pronta ("digest"); "download" abre um filho que escreve uma batida a cada 0,1 s e espera 60 s
# (para a vigia e o grupo).
_GH_DE_PROVA = r'''
import json, os, subprocess, sys, time
from pathlib import Path
a = sys.argv[1:]
Path(os.environ["GH_DE_PROVA_DIARIO"]).open("a", encoding="utf-8").write(json.dumps(a) + "\n")
if a[1] == "view":
    print(json.dumps({"isDraft": False, "tagName": a[2], "assets": [{"name": "grande.nupkg", "size": 10}]}))
    sys.exit(0)
if a[1] == "download":
    # o filho sai sozinho depois de 30 s: se um teste falhar e ele escapar do grupo, não fica rodando para sempre
    batida = ("import os, sys, time\nn = 0\nfim = time.monotonic() + 30\nwhile time.monotonic() < fim:\n    n += 1\n"
              "    open(sys.argv[1] + '.tmp', 'w').write(str(n))\n"
              "    try:\n        os.replace(sys.argv[1] + '.tmp', sys.argv[1])\n    except OSError:\n        pass\n"
              "    time.sleep(0.1)\n")
    subprocess.Popen([sys.executable, "-c", batida, os.environ["GH_DE_PROVA_FILHO"]])
    time.sleep(60)
sys.exit(1)
'''


def _gh_de_prova(tmp_path: Path, monkeypatch) -> tuple[Path, Path, Path]:
    """O gh de prova, o diário dos argumentos e o arquivo da batida do filho."""
    diario, batida = tmp_path / "gh-rodou.txt", tmp_path / "filho-do-gh.txt"
    monkeypatch.setenv("GH_DE_PROVA_DIARIO", str(diario))
    monkeypatch.setenv("GH_DE_PROVA_FILHO", str(batida))
    return _programa_de_prova(tmp_path / "gh.exe", _GH_DE_PROVA), diario, batida


def test_volta4_achado7_sem_a_soma_pronta_o_download_vai_ao_rascunho_pela_vigia(tmp_path, monkeypatch):
    """Achado 7 do relatório 3 de quem tentou quebrar (D-776, "no C só tem que cuidar para não encher o disco C
    inteiro"): quando o GitHub não dá a soma pronta de um arquivo, a leitura de volta o baixava inteiro para a pasta
    temporária da conta (%TEMP%, no C:), fora do rascunho, da vigia e da conta. Agora o download vai para o rascunho do
    publicar, pela peça que já baixa vigiada (baixar_vigiado), com a vigia única. De verdade: um gh de prova que demora
    60 s a baixar é fechado pela vigia, junto com o filho que ele abriu, e o pedido de download apontava para dentro do
    rascunho. Sem rascunho dado, a soma para com a frase (nunca baixa para outro lugar)."""
    gh, diario, batida = _gh_de_prova(tmp_path, monkeypatch)
    monkeypatch.setattr(empacotar, "INTERVALO_DA_VIGIA_S", 0.2)
    rascunho = tmp_path / "publicar-rascunho"
    rascunho.mkdir()
    destino = pub.DestinoGitHub("dono/projeto", gh=str(gh))
    destino.usar_rascunho(rascunho, lambda: "o disco ficou abaixo da reserva (de mentira)" if batida.exists() else None)
    inicio = time.perf_counter()
    with pytest.raises(pub.Parou, match="abaixo da reserva"):
        destino.soma(ETIQUETA, "grande.nupkg")
    assert time.perf_counter() - inicio < 30, "a vigia não fechou o download"
    assert not _batida_viva(batida), "o filho do gh continuou rodando"
    pedidos = [json.loads(linha) for linha in diario.read_text(encoding="utf-8").splitlines()]
    baixar = [p for p in pedidos if p[1] == "download"]
    assert baixar and rascunho in Path(baixar[0][baixar[0].index("--dir") + 1]).parents, baixar
    assert list(rascunho.iterdir()) == [], "a pasta do download para somar ficou no rascunho"
    sem = pub.DestinoGitHub("dono/projeto", gh=str(gh))
    with pytest.raises(pub.Parou, match="rascunho"):
        sem.soma(ETIQUETA, "grande.nupkg")


def test_volta4_achado7_a_conta_do_espaco_soma_o_que_a_soma_pode_baixar(ambiente, monkeypatch):
    """Achado 7 do relatório 3, a conta (D-776): no GitHub, a leitura de volta pode baixar um arquivo para somar; a
    conta do espaço soma o maior deles (a pasta do programa, ou o motor publicado). Na pasta das provas a soma nunca
    baixa, e a conta continua a de antes (o teste da volta 3 cobra)."""
    a = ambiente
    gh = _GitHubDeMentira(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    pedidos = []
    verdadeira = empacotar.conferir_espaco
    monkeypatch.setattr(empacotar, "conferir_espaco", lambda pasta, precisa, *x: pedidos.append(precisa) or
                        verdadeira(pasta, precisa, *x))
    pasta = empacotar.tamanho_da_pasta(a["pasta"])           # antes (o publicar acrescenta arquivos à pasta)
    motor = len(gh.publicacoes[ETIQUETA_DO_MOTOR]["arquivos"][versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)])
    _publicar(a, destino=destino)
    sem_o_download = empacotar.espaco_que_vai_usar(pasta, (empacotar.ATUALIZACAO,), 0, baixado_para_o_rascunho=0)
    assert pedidos[0] == sem_o_download + max(pasta, motor), (pedidos, sem_o_download, pasta, motor)
    assert pub.DestinoPasta(a["servidor"]).soma_pode_baixar is False and destino.soma_pode_baixar is True


def test_volta4_achado8_o_gh_roda_pelo_laco_unico_da_peca_e_fecha_o_que_abriu(tmp_path, monkeypatch):
    """Achado 8 do relatório 3 de quem tentou quebrar (§11.12, ponto 1): o gh do publicar rodava com o subprocess
    direto, fora da peça do Windows e sem grupo: fechar pela vigia fechava só o gh. Agora o gh e o vpk passam pelo
    mesmo laço da peça (windows.rodar_em_grupo). De verdade: (1) os dois caminhos chamam o laço único; (2) o gh de prova
    abre um filho e é fechado pela vigia: o filho também para; (3) o Ctrl+C no meio também fecha os dois."""
    from core import windows

    chamadas = []
    verdadeiro = windows.rodar_em_grupo
    monkeypatch.setattr(windows, "rodar_em_grupo", lambda comando, **k: chamadas.append(Path(comando[0]).name) or
                        verdadeiro(comando, **k))
    gh, diario, batida = _gh_de_prova(tmp_path, monkeypatch)
    monkeypatch.setattr(empacotar, "INTERVALO_DA_VIGIA_S", 0.2)
    destino = pub.DestinoGitHub("dono/projeto", gh=str(gh))
    assert destino.situacao(ETIQUETA) == "liberada"
    with pytest.raises(pub.Parou, match="abaixo da reserva"):
        destino.baixar_vigiado(ETIQUETA, "grande.nupkg", tmp_path / "baixado",
                               lambda: "o disco ficou abaixo da reserva (de mentira)" if batida.exists() else None)
    assert not _batida_viva(batida), "o filho do gh continuou rodando depois da vigia"
    batida.unlink()

    def ctrl_c():
        """O Ctrl+C assim que o filho começou."""
        if batida.exists():
            raise KeyboardInterrupt
        return None

    # o soltar do grupo é segurado: quem fecha no Ctrl+C tem de ser o laço, não o fechar-ao-fechar do fim do `with`
    segurados = []
    soltar_de_verdade = windows.ProgramaEmGrupo.soltar
    monkeypatch.setattr(windows.ProgramaEmGrupo, "soltar", lambda self: segurados.append(self))
    try:
        with pytest.raises(KeyboardInterrupt):
            destino.baixar_vigiado(ETIQUETA, "grande.nupkg", tmp_path / "baixado", ctrl_c)
        assert segurados, "o grupo não passou pelo soltar"
        assert not _batida_viva(batida), "o filho do gh continuou rodando depois do Ctrl+C"
    finally:
        monkeypatch.setattr(windows.ProgramaEmGrupo, "soltar", soltar_de_verdade)
        for programa in segurados:
            soltar_de_verdade(programa)
    vpk = _programa_de_prova(tmp_path / "vpk.exe", "import sys\nsys.exit(0)\n")
    rascunho = tmp_path / "publicar-laco"
    rascunho.mkdir()
    assert empacotar.rodar_vpk([str(vpk)], rascunho, livre=lambda _p: 500 * empacotar.GB) is None
    assert chamadas.count("gh.exe") == 3 and chamadas[-1] == "vpk.exe", chamadas


def test_volta4_achado11_a_copia_e_o_motor_gravam_no_disco_antes_de_conferir_e_trocar(tmp_path, monkeypatch):
    """Achado 11 do relatório 3 de quem tentou quebrar: a cópia conferida dizia "lida de volta do disco" sem pedir ao
    Windows para gravar no disco, e trocava o nome; o motor comprimido também. Agora as duas pedem (pela função única
    da peça, windows.gravar_no_disco: o os.fsync, que no Windows é o _commit, "Flushes a file directly to disk") ANTES
    de ler de volta e de trocar o nome. Aqui: a ordem do que o Python pede ao sistema (o os.fsync de verdade roda)."""
    import builtins

    motor = _motor_com_ficha(tmp_path / "motor")          # antes de anotar (a ficha também troca um nome)
    ordem = []
    verdadeiro_fsync, verdadeiro_replace, verdadeiro_open = os.fsync, os.replace, builtins.open
    monkeypatch.setattr(os, "fsync", lambda fd: (ordem.append("gravar no disco"), verdadeiro_fsync(fd))[1])
    monkeypatch.setattr(os, "replace", lambda a, b: (ordem.append("trocar o nome"), verdadeiro_replace(a, b))[1])

    def aberto(arquivo, modo="r", *x, **k):
        """Anota a leitura de volta do provisório."""
        if "r" in modo and "+" not in modo and str(arquivo).endswith(".copiando"):
            ordem.append("ler de volta")
        return verdadeiro_open(arquivo, modo, *x, **k)

    monkeypatch.setattr(builtins, "open", aberto)
    origem = tmp_path / "origem.bin"
    origem.write_bytes(os.urandom(200_000))
    empacotar.copiar_inteiro(origem, tmp_path / "copia.bin")
    assert ordem == ["gravar no disco", "ler de volta", "trocar o nome"], ordem
    ordem.clear()
    assert empacotar.zipar_motor(motor, tmp_path / "motor.zip", livre=lambda p: 500 * empacotar.GB) is None
    assert ordem == ["gravar no disco", "trocar o nome"], ordem


class _GitHubQueNaoRespondeAoApagar(_GitHubDeMentira):
    """O envio do pacote falha (antes do pedido de liberar), e o pedido de apagar sai e fica sem resposta (o gh é fechado
    por tempo: o _gh de verdade levanta SemResposta, como aqui)."""

    def __call__(self, *argumentos, limite_s=600):
        """O envio do .nupkg falha; o "delete" fica sem resposta."""
        a = list(argumentos)
        if a[1] == "upload" and a[2] == ETIQUETA and a[3].endswith(".nupkg"):
            self.pedidos.append(a)
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502 ao enviar (de mentira)")
        if a[1] == "delete" and a[2] == ETIQUETA:
            self.pedidos.append(a)
            raise pub.SemResposta("parei o pedido ao GitHub (release delete): o programa não terminou em 600 segundos")
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta4_achado3_o_pedido_de_apagar_sem_resposta_diz_que_pediu(ambiente, monkeypatch):
    """Achado 3 do relatório 3, o terceiro desfecho: o pedido de apagar SAIU e ficou sem resposta (o gh fechado por
    tempo). A frase diz "pedi para apagar ... não deu para conferir se sumiu", nunca "não apaguei"."""
    a = ambiente
    gh = _GitHubQueNaoRespondeAoApagar(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    assert "pedi para apagar" in frase and "não deu para conferir se sumiu" in frase, frase
    assert "não apaguei" not in frase.lower() and "foi apagada" not in frase, frase


class _PastaQueLiberaNaHoraDeApagar(pub.DestinoPasta):
    """Uma pasta de verdade em que, no instante do pedido de apagar o rascunho, outro publicar o libera (troca o nome
    da subpasta), e o pedido de apagar não acha mais o rascunho."""

    def apagar_rascunho(self, etiqueta):
        """Outro libera bem agora; depois, o apagar de sempre (que só toca no rascunho)."""
        os.rename(self._rascunho(etiqueta), self._liberada(etiqueta))
        return super().apagar_rascunho(etiqueta)


def test_volta4_achado3_liberada_no_meio_do_apagar_nunca_vira_apagada(tmp_path):
    """Achado 3 do relatório 3 (a frase diz o que aconteceu): antes do pedido de liberar, o caminho de erro pede para
    apagar o rascunho e, no meio, outro publicar o libera. A leitura de depois diz liberada: a resposta é
    "PublicacaoLiberada" ("pedi para apagar o rascunho ... e ele está liberado agora"), nunca "apagada" nem "continua
    lá", e a versão liberada continua."""
    destino = _PastaQueLiberaNaHoraDeApagar(tmp_path / "servidor")
    destino.criar_rascunho(ETIQUETA, "t", "n")
    with pytest.raises(pub.PublicacaoLiberada, match="pedi para apagar o rascunho") as erro:
        pub.apagar_publicacao(destino, ETIQUETA, so_rascunho=True, acabou_de_criar=True)
    assert "liberado agora" in str(erro.value)
    assert destino.situacao(ETIQUETA) == "liberada"


class _GitHubSemASomaPronta(_GitHubDeMentira):
    """O gh de mentira em que o GitHub NÃO dá a soma pronta ("digest") de nenhum arquivo, e que aceita a vigia do
    download como o _gh de verdade (anota quem a passou)."""

    def __init__(self, tmp):
        """vigiados: os downloads que vieram com a vigia."""
        super().__init__(tmp)
        self.vigiados: list[str] = []

    def __call__(self, *argumentos, limite_s=600, vigia=None):
        """Como o gh de mentira, sem o digest, anotando a vigia."""
        a = list(argumentos)
        if vigia is not None:
            self.vigiados.append(a[a.index("--pattern") + 1])
            assert vigia() is None
        r = super().__call__(*argumentos, limite_s=limite_s)
        if a[1] == "view" and r.returncode == 0:
            lido = json.loads(r.stdout)
            for asset in lido.get("assets", []):
                asset.pop("digest", None)
            r = subprocess.CompletedProcess(r.args, 0, json.dumps(lido), "")
        return r


def test_volta4_achado7_no_publicar_sem_a_soma_pronta_tudo_e_baixado_no_rascunho(ambiente, monkeypatch):
    """Achado 7 do relatório 3, o caminho inteiro: com o GitHub sem a soma pronta, o motor e a versão são publicados
    (a leitura de volta baixa cada arquivo para somar) e TODO download vai para dentro do rascunho do publicar (no C:,
    apagado no fim), os da soma com a vigia; nada vai para a pasta temporária da conta. A conta do motor (--motor)
    também soma a cópia que a leitura de volta baixa."""
    a = ambiente
    gh = _GitHubSemASomaPronta(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    pedidos = []
    verdadeira = empacotar.conferir_espaco
    monkeypatch.setattr(empacotar, "conferir_espaco", lambda pasta, precisa, *x: pedidos.append(precisa) or
                        verdadeira(pasta, precisa, *x))
    _publicar_o_motor(a, destino=destino)
    assert pedidos[0] == 2 * empacotar.tamanho_da_pasta(a["motor"]) + empacotar.MARGEM_DA_CONTA, pedidos
    _publicar(a, destino=destino)
    baixados = [p for p in gh.pedidos if p[1] == "download"]
    assert baixados, "a leitura de volta tinha de baixar"
    for p in baixados:
        assert a["rascunho"] in Path(p[p.index("--dir") + 1]).parents, p
    nupkg = empacotar.nupkg_inteiro(Path("."), VERSAO).name
    assert nupkg in gh.vigiados and versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR) in gh.vigiados, gh.vigiados
    assert gh.publicacoes[ETIQUETA]["rascunho"] is False and _rascunhos_que_sobraram(a) == []


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 5 (relatório 4 de quem tentou quebrar, 20/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

def _seguir_a_frase_sem_tocar_o_github(frase: str, destino, etiqueta: str, monkeypatch) -> None:
    """A frase tem o comando de apagar do lugar único (com o --pasta da pasta das provas); rodar EXATAMENTE esse
    comando apaga na pasta e nunca fala com o GitHub (o gh de qualquer DestinoGitHub falha o teste se for chamado)."""
    import shlex

    comando = destino.comando_de_apagar(etiqueta)
    assert comando in frase and "--pasta" in comando, frase
    argumentos = [a.strip('"') for a in shlex.split(comando, posix=False)][1:]

    def nao_pode(self, *argumentos, **k):
        """Seguir a frase da pasta não pode chegar ao GitHub."""
        raise AssertionError(f"a frase da pasta foi ao GitHub: {argumentos}")

    monkeypatch.setattr(pub.DestinoGitHub, "_gh", nao_pode)
    assert pub.main(argumentos) == 0
    assert destino.situacao(etiqueta) is None


@pytest.mark.parametrize("onde", ["publicar_arquivos", "versao", "motor"])
def test_volta5_achado1_as_frases_de_ja_existe_dao_o_comando_do_destino(ambiente, monkeypatch, onde):
    """Achado 1 do relatório 4 de quem tentou quebrar (20/11/2026, §11.12: conta duplicada): três frases do publicar
    ("sobrou um rascunho" em publicar_arquivos, e os dois "já existe", da versão e do motor) escreviam `--apagar
    <etiqueta>` à mão, sem o destino; na pasta das provas, quem seguia a frase apagava no GitHub (lá, a versão do Kaique
    LIBERADA, com a etiqueta). Agora as três usam o lugar único (`comando_de_apagar`, com o `--pasta`). Aqui, na pasta
    das provas, com um rascunho que sobrou: a frase de cada uma tem o comando do destino, e seguir a frase apaga o
    rascunho da pasta sem nunca falar com o GitHub."""
    a = ambiente
    destino = pub.DestinoPasta(a["servidor"])
    if onde == "motor":
        etiqueta = ETIQUETA_DO_MOTOR
        destino.criar_rascunho(etiqueta, "t", "n")
        with pytest.raises(pub.Parou) as erro:
            _publicar_o_motor(a)
    else:
        etiqueta = ETIQUETA
        _publicar_o_motor(a)
        destino.criar_rascunho(etiqueta, "t", "n")
        with pytest.raises(pub.Parou) as erro:
            if onde == "versao":
                _publicar(a)
            else:
                pub.publicar_arquivos(destino, etiqueta, "t", "n", [], lambda: None)
    _seguir_a_frase_sem_tocar_o_github(str(erro.value), destino, etiqueta, monkeypatch)


class _GhQueTravaNaLeituraDeDentroDoApagar(_GitHubDeMentira):
    """O envio do .nupkg falha (antes de liberar). Depois disso, a SEGUNDA leitura da etiqueta (a de dentro do
    DestinoGitHub.apagar_rascunho, logo antes de pedir) fica sem resposta. É o Q1 de quem tentou quebrar (volta 4)."""

    def __init__(self, tmp):
        """Conta as leituras depois do envio que falhou."""
        super().__init__(tmp)
        self.falhou_o_envio = False
        self.leituras_depois = 0

    def __call__(self, *argumentos, limite_s=600):
        """O envio falha; a 2ª leitura de depois fica sem resposta (o _gh de verdade levanta SemResposta)."""
        a = list(argumentos)
        if a[1] == "upload" and a[2] == ETIQUETA and a[3].endswith(".nupkg"):
            self.pedidos.append(a)
            self.falhou_o_envio = True
            return subprocess.CompletedProcess(a, 1, "", "HTTP 502 ao enviar (de mentira)")
        if a[1] == "view" and a[2] == ETIQUETA and self.falhou_o_envio:
            self.leituras_depois += 1
            if self.leituras_depois == 2:
                self.pedidos.append(a)
                raise pub.SemResposta("parei o pedido ao GitHub (release view): o programa não terminou em 600 "
                                      "segundos")
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta5_achado2_a_leitura_sem_resposta_antes_do_pedido_nao_vira_pedi_para_apagar(ambiente, monkeypatch):
    """Achado 2 do relatório 4 (família F5, o vizinho ao contrário do achado 3 do relatório 3): a leitura que o apagar
    do rascunho faz logo antes de pedir ficou sem resposta, e a frase dizia "pedi para apagar ... não deu para conferir
    se sumiu", sem nenhum pedido de apagar ter saído. Agora só o pedido de apagar em si diz "pedi"; a leitura sem
    resposta é "não apaguei". O rascunho continua no GitHub e a frase dá o comando."""
    a = ambiente
    gh = _GhQueTravaNaLeituraDeDentroDoApagar(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    assert not any(p[1] == "delete" and p[2] == ETIQUETA for p in gh.pedidos), "um pedido de apagar saiu"
    assert "pedi para apagar" not in frase and "não apaguei" in frase, frase
    assert destino.comando_de_apagar(ETIQUETA) in frase and ETIQUETA in gh.publicacoes, frase


# Um "gh" de prova DE VERDADE (um programa) para o pedido de apagar que fica sem resposta: "view" diz rascunho;
# "delete" anota e espera 60 s (o _gh o fecha pelo tempo).
_GH_QUE_DEMORA_A_APAGAR = r'''
import json, os, sys, time
from pathlib import Path
a = sys.argv[1:]
Path(os.environ["GH_DE_PROVA_DIARIO"]).open("a", encoding="utf-8").write(json.dumps(a) + "\n")
if a[1] == "view":
    print(json.dumps({"isDraft": True, "tagName": a[2], "assets": []}))
    sys.exit(0)
if a[1] == "delete":
    time.sleep(60)
sys.exit(1)
'''


def test_volta5_achado3a_o_gh_de_verdade_fechado_por_tempo_no_apagar_diz_que_pediu(tmp_path, monkeypatch):
    """Achado 3 do relatório 4, (a) (família F3, proteção sem teste): no _gh de verdade, o gh fechado por tempo vira
    "sem resposta" (o pedido saiu e não se sabe se foi feito). Os testes do achado 3 do relatório 3 levantavam isso
    direto do gh de mentira, sem passar por essa linha. De verdade: um gh de prova que demora a apagar, com o tempo do
    pedido curto; o apagar diz "pedi para apagar ... não deu para conferir se sumiu", nunca "não apaguei"."""
    diario = tmp_path / "gh-rodou.txt"
    monkeypatch.setenv("GH_DE_PROVA_DIARIO", str(diario))
    monkeypatch.setattr(empacotar, "INTERVALO_DA_VIGIA_S", 0.2)
    gh = _programa_de_prova(tmp_path / "gh.exe", _GH_QUE_DEMORA_A_APAGAR)
    destino = pub.DestinoGitHub("dono/projeto", gh=str(gh))
    destino.LIMITE_DO_PEDIDO_S = 3
    inicio = time.perf_counter()
    with pytest.raises(pub.Parou) as erro:
        pub.apagar_publicacao(destino, ETIQUETA, so_rascunho=True, acabou_de_criar=True)
    assert time.perf_counter() - inicio < 30, "o tempo do pedido não fechou o gh"
    frase = str(erro.value)
    assert "pedi para apagar" in frase and "não deu para conferir se sumiu" in frase, frase
    assert "não apaguei" not in frase.lower(), frase
    pedidos = [json.loads(linha)[1] for linha in diario.read_text(encoding="utf-8").splitlines()]
    assert "delete" in pedidos, pedidos


class _GitHubQueLiberaAntesDoPedido(_GitHubDeMentira):
    """O rascunho é liberado por outra pessoa entre a leitura de apagar_publicacao e a de dentro do
    DestinoGitHub.apagar_rascunho (logo antes do pedido)."""

    def __init__(self, tmp):
        """Conta as leituras."""
        super().__init__(tmp)
        self.leituras = 0

    def __call__(self, *argumentos, limite_s=600):
        """Depois da primeira leitura, a publicação está liberada."""
        a = list(argumentos)
        r = super().__call__(*argumentos, limite_s=limite_s)
        if a[1] == "view" and a[2] == ETIQUETA:
            self.leituras += 1
            if self.leituras == 1:
                self.publicacoes[ETIQUETA]["rascunho"] = False
        return r


def test_volta5_achado3b_liberada_antes_do_pedido_no_github_continua_publicacao_liberada(ambiente, monkeypatch):
    """Achado 3 do relatório 4, (b) (família F3): o `except PublicacaoLiberada: raise` de apagar_publicacao não tinha
    teste. No GitHub, a leitura de dentro do apagar do rascunho (logo antes do pedido) vê a publicação liberada por
    outra pessoa: nada é pedido, e a resposta continua sendo "PublicacaoLiberada" (o caminho de erro diz "outra pessoa
    ou outro publicar a liberou no meio"), e não um "não apaguei" comum."""
    gh = _GitHubQueLiberaAntesDoPedido(ambiente["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    destino.criar_rascunho(ETIQUETA, "t", "n")
    with pytest.raises(pub.PublicacaoLiberada, match="NÃO apaguei"):
        pub.apagar_publicacao(destino, ETIQUETA, so_rascunho=True, acabou_de_criar=True)
    assert not any(p[1] == "delete" for p in gh.pedidos) and gh.publicacoes[ETIQUETA]["rascunho"] is False


class _GhQueNaoAbreNoLiberar(_GitHubDeMentira):
    """O gh não abre no pedido de liberar (o _gh de verdade levanta NadaSaiu: o programa nem começou). É o Q2 de quem
    tentou quebrar (volta 4)."""

    def __call__(self, *argumentos, limite_s=600):
        """O "edit" nem sai do PC."""
        a = list(argumentos)
        if a[1] == "edit" and a[2] == ETIQUETA:
            raise pub.NadaSaiu("não consegui falar com o GitHub pelo gh (não consegui abrir o programa)")
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta5_achado4_o_gh_que_nem_abre_no_liberar_nao_conta_como_pedido(ambiente, monkeypatch):
    """Achado 4 do relatório 4 (escolha técnica da gerente, pela D-816): o gh que nem abre no pedido de liberar (nada
    saiu do PC) contava como "pedi para liberar", e o rascunho ficava no GitHub com a frase "pedi para liberar". Agora o
    "não abriu" comprovado não conta como pedido: pela D-816 ("Antes do pedido de liberar, erro no meio continua apagando
    o rascunho na hora"), o rascunho é apagado e conferido. Qualquer outro erro depois de o gh abrir continua contando
    como pedido (os testes da D-816 cobram)."""
    a = ambiente
    gh = _GhQueNaoAbreNoLiberar(a["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    _publicar_o_motor(a, destino=destino)
    frase = str(_publicar_um(a, "versao", destino))
    assert ETIQUETA not in gh.publicacoes, "o rascunho ficou no GitHub"
    assert "pedi para liberar" not in frase and "foi apagada" in frase and "(conferido)" in frase, frase


def test_volta5_achado4_so_o_gh_que_nao_abriu_de_verdade_e_nada_saiu(tmp_path, monkeypatch):
    """Achado 4 do relatório 4, o _gh de verdade: o gh que não existe (o programa nem começa) é NadaSaiu; o gh que abre
    e responde erro é um Parou comum (o pedido saiu), nunca NadaSaiu."""
    destino = pub.DestinoGitHub("dono/projeto", gh=str(tmp_path / "nao-existe" / "gh.exe"))
    with pytest.raises(pub.NadaSaiu):
        destino.liberar(ETIQUETA)
    monkeypatch.setenv("GH_DE_PROVA_DIARIO", str(tmp_path / "gh-rodou.txt"))
    gh = _programa_de_prova(tmp_path / "gh.exe", _GH_QUE_DEMORA_A_APAGAR)       # "edit" sai com o código 1
    with pytest.raises(pub.Parou) as erro:
        pub.DestinoGitHub("dono/projeto", gh=str(gh)).liberar(ETIQUETA)
    assert not isinstance(erro.value, pub.NadaSaiu), erro.value



# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 6 (a prova à vista de 20/11/2026 e o relatório 5 de quem tentou quebrar)
# ---------------------------------------------------------------------------------------------------------------------

VC_DE_PROVA = b"MZ o Visual C++ de prova (o de verdade e conferido pela assinatura da Microsoft, em preparar_vc_redist)"


def _pyinstaller_de_prova(onefile: bool) -> bool:
    """No lugar SÓ do PyInstaller (que leva uns 4 minutos e não roda no Windows do GitHub sem os modelos): escreve o que
    o PyInstaller 6 escreve, lido do PRÓPRIO comando (`empacotar.comando_do_pyinstaller`): o .exe em
    `--distpath\\--name\\` e cada `--add-data origem;destino` em `<pasta>\\<--contents-directory>\\<destino>\\`. Foi o que a
    prova de 20/11 achou na pasta do PyInstaller de verdade (`relatorios/passo2-publicar/anexos/volta6-a-pasta-da-prova.txt`).
    Tudo o que o `construir_pasta` faz depois (as peças, as conferências, o Visual C++, a ficha) é o código de verdade."""
    comando = empacotar.comando_do_pyinstaller(onefile)
    valor = lambda opcao: comando[comando.index(opcao) + 1]  # noqa: E731
    pasta = Path(valor("--distpath")) / valor("--name")
    interno = pasta / valor("--contents-directory")
    interno.mkdir(parents=True)
    (pasta / f"{valor('--name')}.exe").write_bytes(b"MZ o programa montado de prova")
    for i, item in enumerate(comando):
        if item == "--add-data":
            origem, destino = (Path(p) for p in comando[i + 1].rsplit(";", 1))
            if origem.is_dir():
                shutil.copytree(origem, interno / destino, dirs_exist_ok=True)
            else:
                (interno / destino).mkdir(parents=True, exist_ok=True)
                shutil.copy2(origem, interno / destino / origem.name)
    return True


@pytest.fixture
def montar_de_verdade(ambiente, monkeypatch):
    """O `empacotar.construir_pasta` DE VERDADE, numa pasta do teste: `empacotar.RAIZ` aponta para ela (a pasta montada
    fica em <tmp>\\repositorio-do-empacotar\\dist\\EditorImpressao, nunca no dist\\ desta cópia). Trocados só: o PyInstaller
    (`_pyinstaller_de_prova`), os modelos (os mesmos nomes e destinos de `empacotar.modelos_do_programa`, com arquivos
    do teste: no Windows do GitHub os modelos não existem) e as peças dos detectores (`empacotar.juntar_pecas`: um
    Tesseract com os 27 arquivos e as licenças, os idiomas e um Visual C++ de prova; no Windows do GitHub não há
    Tesseract instalado nem o Visual C++ baixado, e o de verdade baixaria da internet). Devolve o que o teste precisa."""
    a = ambiente
    from core import ocr_tesseract

    raiz = a["tmp"] / "repositorio-do-empacotar"
    monkeypatch.setattr(empacotar, "RAIZ", raiz)
    monkeypatch.setattr(empacotar, "_pyinstaller", _pyinstaller_de_prova)
    monkeypatch.setattr(empacotar, "_PECAS", None)
    modelos = []
    for origem, destino in empacotar.modelos_do_programa():
        copia = a["tmp"] / "modelos-de-prova" / destino / origem.name
        copia.parent.mkdir(parents=True, exist_ok=True)
        copia.write_bytes(b"modelo de prova " + origem.name.encode())
        modelos.append((copia, destino))
    monkeypatch.setattr(empacotar, "modelos_do_programa", lambda: modelos)
    tesseract = a["tmp"] / "tesseract-de-prova"
    (tesseract / "doc").mkdir(parents=True)
    for nome in empacotar.ARQUIVOS_DO_TESSERACT:
        (tesseract / nome).write_bytes(b"nao e programa: so um arquivo de prova " + nome.encode())
    for nome in empacotar.LICENCAS_DO_TESSERACT:
        (tesseract / "doc" / nome).write_text(f"{nome} de prova", encoding="utf-8")
    idiomas = a["tmp"] / "tessdata-de-prova"
    for idioma in ocr_tesseract.IDIOMAS_DO_INSTALADOR:
        (idiomas / f"{idioma}.traineddata").parent.mkdir(parents=True, exist_ok=True)
        (idiomas / f"{idioma}.traineddata").write_bytes(b"idioma " + idioma.encode())
    vc = a["tmp"] / "downloads-de-prova" / empacotar.VC_REDIST_NOME
    vc.parent.mkdir()
    vc.write_bytes(VC_DE_PROVA)

    def pecas_de_prova(motor_escolhido=None, baixar=True, com_motor=True):
        """As peças, como o juntar_pecas de verdade as devolve (o motor só na pasta portátil)."""
        return empacotar.PecasDosDetectores(a["motor"] if com_motor else None, tesseract, tesseract / "doc", idiomas,
                                            vc, "14.44.35211.0"), []

    monkeypatch.setattr(empacotar, "juntar_pecas", pecas_de_prova)
    return {"pasta": raiz / "dist" / empacotar.NOME, "vc": vc}


def _no_pacote(nupkg: Path) -> dict[str, bytes]:
    """O que está dentro do pacote do Velopack (o caminho dentro da pasta do programa: o conteúdo)."""
    with zipfile.ZipFile(nupkg) as z:
        return {n.removeprefix(empacotar.PASTA_NO_NUPKG): z.read(n) for n in z.namelist()
                if n.startswith(empacotar.PASTA_NO_NUPKG)}


@pytest.mark.parametrize("com_instalador", [False, True])
def test_volta6_a_versao_montada_do_zero_leva_o_visual_c_e_e_publicada(ambiente, montar_de_verdade, com_instalador):
    """O defeito da prova à vista de 20/11/2026 (14h33 a 14h39; registro em C:\\EditorImpressaoProva\\publicar-versao.log):
    `publicar_versao_kaique.py --pasta <pasta>` SEM `--pasta-pronta` montava a pasta (`empacotar.construir_pasta`,
    797 MB) e parava sempre em "a pasta do programa não serve: ... não tem o Visual C++ em instalar\\": a conferência
    (`empacotar.conferir_pasta_pronta`) rodava antes de o Visual C++ ser posto (só em `preparar_saida`, dentro do
    `construir_pacote_do_velopack`). Nenhuma versão montada do zero saía. Os testes não pegavam porque todos usavam a
    pasta de mentira `_pasta_pronta`, que já vem com o Visual C++ (D-767: "não faça mais nada escodindo ou de mentira").
    Agora a montagem põe o Visual C++ em instalar\\ antes da ficha (D-727: ele vai dentro), a mesma conferência aceita a
    pasta, e a versão é publicada na pasta das provas com o Visual C++, o Tesseract e sem o motor solto, com e sem o
    instalador. Rodado no código de b9300da8: falha com "não tem o Visual C++ em instalar\\"."""
    a = ambiente
    _publicar_o_motor(a)
    pub.publicar(versao.VERSAO, arquivo_da_chave=a["chave"], chave_publica=PUBLICA, vpk=a["vpk"],
                 rascunho_base=a["rascunho"], pasta_de_saida=a["saida"], destino=pub.DestinoPasta(a["servidor"]),
                 com_instalador=com_instalador)
    etiqueta = versao.etiqueta_da_versao(versao.VERSAO)
    dentro = _no_pacote(empacotar.nupkg_inteiro(a["servidor"] / etiqueta, versao.VERSAO))
    instalar = atualizacao.PASTA_DO_QUE_SE_INSTALA
    assert dentro[f"{instalar}/{atualizacao.VC_REDIST_NOME}"] == VC_DE_PROVA
    assert dentro[f"{instalar}/{atualizacao.VC_REDIST_VERSAO}"] == b"14.44.35211.0"
    assert "tesseract/tesseract.exe" in dentro and "tesseract/tessdata/script/Fraktur.traineddata" in dentro
    assert not any(n.startswith(empacotar.PASTA_DO_MOTOR + "/") for n in dentro)
    assert empacotar.conferir_pasta_pronta(montar_de_verdade["pasta"], versao.VERSAO) == []
    vezes = _vezes_que_o_vpk_rodou(a)
    assert len(vezes) == (2 if com_instalador else 1)
    assert (a["saida"] / etiqueta / empacotar.nome_do_msi_publicado(versao.VERSAO)).is_file() == com_instalador
    assert _rascunhos_que_sobraram(a) == []


def test_volta6_a_mesma_conferencia_da_pasta_em_todos_os_caminhos(ambiente, montar_de_verdade, capsys):
    """CLAUDE.md §11.12 (uma regra, um lugar): "a pasta está pronta para o vpk" é decidido por uma função só
    (`empacotar.conferir_pasta_pronta`), e todos os caminhos chegam a ela com a pasta no mesmo estado:
    - a montagem para a atualização (`construir_pasta(ATUALIZACAO)`) deixa o Visual C++ em instalar\\ e passa;
    - a mesma pasta SEM o Visual C++ (como a que vem de fora, e como a da prova de 20/11) é recusada com a frase de
      sempre, pela montagem conferida e pela pasta pronta de mentira, igual;
    - o empacotar chamado direto com essa pasta para ANTES de rodar o vpk (antes, o vpk rodava e só a conferência do
      pacote pegava);
    - o empacotar chamado direto sem pasta monta e empacota com o Visual C++;
    - a pasta portátil (o Inno) continua SEM instalar\\ (o Inno pega o Visual C++ de build\\).
    Rodado no código de b9300da8: falha na primeira conferência (a montagem não punha o Visual C++)."""
    a = ambiente
    pasta = empacotar.construir_pasta(empacotar.ATUALIZACAO)
    assert pasta == montar_de_verdade["pasta"]
    vc = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME
    assert vc.is_file() and vc.read_bytes() == VC_DE_PROVA, "a montagem para a atualização tem de pôr o Visual C++"
    assert empacotar.conferir_pasta_pronta(pasta, versao.VERSAO) == []
    assert empacotar.conferir_pasta_pronta(pasta, versao.VERSAO, empacotar.INSTALADOR) == []

    sem_vc = f"não tem o Visual C++ em {atualizacao.PASTA_DO_QUE_SE_INSTALA}\\"
    vc.unlink()
    assert empacotar.conferir_pasta_pronta(pasta, versao.VERSAO) == [f"a pasta {pasta} {sem_vc}"]
    de_fora = _pasta_pronta(a["tmp"] / "de-fora" / "EditorImpressao", versao.VERSAO)
    (de_fora / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME).unlink()
    assert empacotar.conferir_pasta_pronta(de_fora, versao.VERSAO) == [f"a pasta {de_fora} {sem_vc}"]

    motor = empacotar.MotorPublicado(ocr_kraken.VERSAO_DO_MOTOR, versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR),
                                     "0" * 64, ETIQUETA_DO_MOTOR)
    capsys.readouterr()
    assert empacotar.construir_pacote_do_velopack(a["tmp"] / "saida-1", versao.VERSAO, empacotar.ATUALIZACAO, de_fora,
                                                  motor, vpk=a["vpk"]) is None
    assert _vezes_que_o_vpk_rodou(a) == [], "o vpk rodou com uma pasta sem o Visual C++"
    assert sem_vc in capsys.readouterr().out

    nupkg = empacotar.construir_pacote_do_velopack(a["tmp"] / "saida-2", versao.VERSAO, empacotar.ATUALIZACAO,
                                                   motor=motor, vpk=a["vpk"])
    assert nupkg is not None
    assert _no_pacote(nupkg)[f"{atualizacao.PASTA_DO_QUE_SE_INSTALA}/{atualizacao.VC_REDIST_NOME}"] == VC_DE_PROVA

    portatil = empacotar.construir_pasta(empacotar.PORTATIL)
    assert portatil is not None and not (portatil / atualizacao.PASTA_DO_QUE_SE_INSTALA).exists()
    assert (portatil / empacotar.PASTA_DO_MOTOR).is_dir()


def test_volta6_a_copia_do_visual_c_pela_metade_nao_deixa_a_ficha(ambiente, montar_de_verdade, monkeypatch):
    """A falha que o conserto acrescenta: se o Visual C++ não chega inteiro a instalar\\, a montagem para e NÃO grava a
    ficha da versão (a ficha é o sinal de "montada inteira"): um `--pasta-pronta` nessa pasta é recusado ("não tem a
    ficha"), e o publicar para antes do vpk."""
    a = ambiente
    original = shutil.copy2

    def copia_cortada(origem, alvo, *x, **k):
        """Corta só a cópia do Visual C++ (o resto copia de verdade)."""
        if Path(origem) == montar_de_verdade["vc"]:
            Path(alvo).write_bytes(VC_DE_PROVA[:10])
            return alvo
        return original(origem, alvo, *x, **k)

    monkeypatch.setattr(empacotar.shutil, "copy2", copia_cortada)
    assert empacotar.construir_pasta(empacotar.ATUALIZACAO) is None
    pasta = montar_de_verdade["pasta"]
    assert not (pasta / empacotar.NOME_DA_FICHA_DA_VERSAO).exists()
    assert any("ficha da versão" in p for p in empacotar.conferir_pasta_pronta(pasta, versao.VERSAO))
    _publicar_o_motor(a)
    with pytest.raises(pub.Parou, match="montagem da pasta do programa parou"):
        pub.publicar(versao.VERSAO, arquivo_da_chave=a["chave"], chave_publica=PUBLICA, vpk=a["vpk"],
                     rascunho_base=a["rascunho"], pasta_de_saida=a["saida"], destino=pub.DestinoPasta(a["servidor"]))
    assert _vezes_que_o_vpk_rodou(a) == []


class _GhQueNaoAbreNoApagar(_GitHubDeMentira):
    """Lê como o gh de mentira; o pedido de APAGAR passa pelo `DestinoGitHub._gh` DE VERDADE com um gh que não existe (o
    programa nem começa: o laço da peça devolve "não abriu" e o `_gh` levanta `NadaSaiu`)."""

    def __init__(self, tmp: Path):
        """O gh de verdade aponta para um programa que não existe."""
        super().__init__(tmp)
        self.de_verdade = pub.DestinoGitHub("dono/projeto", gh=str(tmp / "nao-existe" / "gh.exe"))

    def __call__(self, *argumentos, limite_s=600):
        """O "delete" vai ao _gh de verdade (que não abre); o resto, ao gh de mentira."""
        if list(argumentos)[1] == "delete":
            self.pedidos.append(list(argumentos))
            return pub.DestinoGitHub._gh(self.de_verdade, *argumentos, limite_s=limite_s)
        return super().__call__(*argumentos, limite_s=limite_s)


def test_volta6_achado1_o_apagar_em_que_o_gh_nem_abre_diz_nao_apaguei(ambiente, monkeypatch):
    """Achado 1 do relatório 5 de quem tentou quebrar (20/11/2026, família F3: proteção sem teste): se o gh nem abre no
    pedido de apagar, nada saiu do PC, e a frase tem de dizer "não apaguei" (com o comando para conferir e apagar),
    nunca "pedi para apagar ... e não deu para conferir se sumiu". Isso vale porque `NadaSaiu` não é um caso de
    `SemResposta` (o `_pedir_para_apagar` só troca o "sem resposta" por "pedi"); nenhum teste o percorria (a mutação X3,
    `NadaSaiu` como caso de `SemResposta`, passava nos 78). O pedido de apagar passa pelo `_gh` de verdade."""
    gh = _GhQueNaoAbreNoApagar(ambiente["tmp"])
    destino = pub.DestinoGitHub("dono/projeto")
    monkeypatch.setattr(destino, "_gh", gh)
    destino.criar_rascunho(ETIQUETA, "t", "n")
    with pytest.raises(pub.Parou) as erro:
        pub.apagar_publicacao(destino, ETIQUETA, so_rascunho=True, acabou_de_criar=True)
    frase = str(erro.value)
    assert "não apaguei" in frase and "pedi para apagar" not in frase, frase
    assert "não consegui falar com o GitHub pelo gh" in frase and destino.comando_de_apagar(ETIQUETA) in frase, frase
    assert any(p[1] == "delete" for p in gh.pedidos), "o pedido de apagar nem foi tentado"
    assert gh.publicacoes[ETIQUETA]["rascunho"] is True, "o rascunho tinha de continuar lá"


@pytest.mark.parametrize("onde", ["pasta", "github"])
def test_volta6_achado2_a_frase_do_motor_que_falta_da_o_comando_do_destino(ambiente, monkeypatch, onde):
    """Achado 2 do relatório 5 de quem tentou quebrar (20/11/2026, família F2, o vizinho do achado 1 do relatório 4): na
    pasta das provas, a frase "o motor ... não está publicado ...: publique o motor antes (--motor)" mandava rodar o
    `--motor` SEM o `--pasta`; seguida ao pé da letra, publicava (e liberava) o motor no GitHub (D-773: no GitHub, só
    um rascunho durante a prova). Agora o comando vem do destino (`comando_de_publicar_o_motor`, ao lado do
    `comando_de_apagar`): na pasta, com o `--pasta`; no GitHub, sem. Seguir a frase da pasta publica o motor na pasta e
    nunca fala com o GitHub."""
    import shlex

    a = ambiente
    if onde == "pasta":
        destino = pub.DestinoPasta(a["servidor"])
    else:
        destino = pub.DestinoGitHub("dono/projeto")
        monkeypatch.setattr(destino, "_gh", _GitHubDeMentira(a["tmp"]))
    with pytest.raises(pub.Parou, match="publique o motor antes") as erro:
        _publicar(a, destino=destino)
    frase = str(erro.value)
    assert ("--pasta" in frase) == (onde == "pasta"), frase
    comando = destino.comando_de_publicar_o_motor()
    assert comando in frase and "--motor" in comando, frase
    assert ("--pasta" in comando) == (onde == "pasta"), comando
    if onde == "github":
        return
    pedidos = []
    monkeypatch.setattr(pub, "publicar_motor", lambda destino_pasta=None, *x, **k: pedidos.append(destino_pasta))

    def nao_pode(self, *argumentos, **k):
        """Seguir a frase da pasta não pode chegar ao GitHub."""
        raise AssertionError(f"a frase da pasta foi ao GitHub: {argumentos}")

    monkeypatch.setattr(pub.DestinoGitHub, "_gh", nao_pode)
    assert pub.main([p.strip('"') for p in shlex.split(comando, posix=False)][1:]) == 0
    assert pedidos == [a["servidor"]], pedidos


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 7 (D-818 e o relatório 6 de quem tentou quebrar, 20/11/2026)
# ---------------------------------------------------------------------------------------------------------------------

# Os Visual C++ de prova que a preparação (`ambiente`) dá como assinados pela Microsoft: o da pasta de mentira e o da
# montagem de verdade do teste. Qualquer outro conteúdo vai à leitura de verdade do Windows.
_VISUAL_C_DE_PROVA = (b"MZ visual c", VC_DE_PROVA)


def _estragar(pasta: Path, defeito: str) -> None:
    """Deixa a pasta com um dos defeitos que a D-818 manda recusar (o mesmo jeito para a pasta pronta e a montada)."""
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    if defeito == "sem o Tesseract":
        shutil.rmtree(pasta / empacotar.PASTA_DO_TESSERACT)
    elif defeito == "sem um idioma do Tesseract":
        (pasta / empacotar.PASTA_DO_TESSERACT / "tessdata" / "lat.traineddata").unlink()
    elif defeito == "um arquivo do Tesseract vazio":
        (pasta / empacotar.PASTA_DO_TESSERACT / "libtesseract-5.dll").write_bytes(b"")
    elif defeito == "um Visual C++ falso":
        (instalar / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ nao sou o Visual C++ da Microsoft")
    elif defeito == "sem a versao do Visual C++":
        (instalar / atualizacao.VC_REDIST_VERSAO).unlink()
    elif defeito == "a versao do Visual C++ errada":
        (instalar / atualizacao.VC_REDIST_VERSAO).write_text("14.29.30133.0", encoding="utf-8")
    else:
        raise AssertionError(defeito)


_DEFEITOS = {"sem o Tesseract": "não tem o Tesseract",
             "sem um idioma do Tesseract": "tessdata/lat.traineddata",
             "um arquivo do Tesseract vazio": "tesseract/libtesseract-5.dll",
             "um Visual C++ falso": "não é o oficial da Microsoft",
             "sem a versao do Visual C++": atualizacao.VC_REDIST_VERSAO,
             "a versao do Visual C++ errada": "14.29.30133.0"}


@pytest.mark.parametrize("defeito", list(_DEFEITOS))
def test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero(ambiente, montar_de_verdade, defeito):
    """D-818 (Samuel, 20/11/2026, à pergunta "A (sugiro): consertar. A pasta já montada passa a ser conferida igual à
    montada do zero, e os testes antigos ganham as peças que faltam. [...]": "vai ter que reprogramar?" · "A"; achado 1
    do relatório 6 de quem tentou quebrar): a pasta já montada (`--pasta-pronta`) sem o Tesseract, com um Visual C++
    que não é o oficial (lido pela peça DE VERDADE do Windows: o arquivo não tem assinatura) ou sem o arquivo da versão
    dele passava na conferência (só o nome do Visual C++ era olhado) e era publicada. Agora o publicar recusa antes do
    vpk, e a frase é a mesma que a pasta montada do zero recebe com o mesmo defeito (é a mesma conferência). A pasta
    montada do zero, inteira, continua passando. Rodado em db4b377a: a pasta estragada é publicada."""
    a = ambiente
    _publicar_o_motor(a)
    montada = empacotar.construir_pasta(empacotar.ATUALIZACAO)
    assert empacotar.conferir_pasta_pronta(montada, versao.VERSAO) == [], "a montada do zero tem de passar inteira"
    pronta = _pasta_pronta(a["tmp"] / "ja-montada" / "EditorImpressao", versao.VERSAO)
    assert empacotar.conferir_pasta_pronta(pronta, versao.VERSAO) == [], "a pasta de mentira inteira tem de passar"
    _estragar(pronta, defeito)
    _estragar(montada, defeito)
    with pytest.raises(pub.Parou, match="a pasta do programa não serve") as erro:
        pub.publicar(versao.VERSAO, pasta_pronta=pronta, arquivo_da_chave=a["chave"], chave_publica=PUBLICA,
                     vpk=a["vpk"], rascunho_base=a["rascunho"], pasta_de_saida=a["saida"],
                     destino=pub.DestinoPasta(a["servidor"]))
    assert _DEFEITOS[defeito] in str(erro.value), str(erro.value)
    assert _vezes_que_o_vpk_rodou(a) == [], "o vpk rodou com uma pasta que a D-818 manda recusar"
    assert pub.DestinoPasta(a["servidor"]).situacao(versao.etiqueta_da_versao(versao.VERSAO)) is None
    da_pronta = empacotar.conferir_pasta_pronta(pronta, versao.VERSAO)
    da_montada = empacotar.conferir_pasta_pronta(montada, versao.VERSAO)
    assert da_pronta and [p.replace(str(pronta), "<pasta>") for p in da_pronta] == \
        [p.replace(str(montada), "<pasta>") for p in da_montada], (da_pronta, da_montada)


@pytest.mark.parametrize("falta", ["instalar/vc_redist.x64.exe", "instalar/vc_redist.versao.txt", "tesseract/",
                                   "tesseract/tessdata/script/Fraktur.traineddata"])
def test_volta7_achado3_o_pacote_sem_uma_peca_e_recusado_depois_do_vpk(ambiente, monkeypatch, capsys, falta):
    """Achado 3 do relatório 6 de quem tentou quebrar (20/11/2026, família F3: proteção sem teste): a conferência do
    pacote depois do vpk (`conferir_pacote_do_velopack`) não tinha teste que a acusasse no Visual C++ nem no Tesseract
    (o vpk de mentira copiava a pasta inteira; as mutações Z2 e Z4 passavam), e não procurava nunca a versão do Visual
    C++ nem, com a pasta já montada, o Tesseract. Agora um vpk que deixa uma dessas peças de fora do pacote faz o publicar
    parar ("o pacote do Velopack saiu errado", com a peça), e nada é publicado. Rodado em db4b377a: a versão do Visual C++
    e o Tesseract que faltam no pacote passam."""
    a = ambiente
    _publicar_o_motor(a)
    monkeypatch.setenv("VPK_FALSO_SEM", falta)
    capsys.readouterr()
    with pytest.raises(pub.Parou, match="empacotamento da atualização parou"):
        _publicar(a)
    saida = capsys.readouterr().out
    assert "o pacote do Velopack saiu errado" in saida and falta.rstrip("/") in saida, saida
    assert pub.DestinoPasta(a["servidor"]).situacao(ETIQUETA) is None
    assert _rascunhos_que_sobraram(a) == []


def test_volta7_achado3_o_pacote_montado_do_zero_sem_o_tesseract_e_recusado(ambiente, montar_de_verdade, monkeypatch,
                                                                            capsys):
    """Achado 3 do relatório 6, o outro caminho (a mutação Z4: o publicar montado do zero sem as peças): a pasta montada
    do zero, com um vpk que deixa o Tesseract de fora, também para em "o pacote do Velopack saiu errado"; a conferência
    do pacote cobra o Tesseract pela mesma lista, com ou sem as peças."""
    a = ambiente
    _publicar_o_motor(a)
    monkeypatch.setenv("VPK_FALSO_SEM", "tesseract/")
    capsys.readouterr()
    with pytest.raises(pub.Parou, match="empacotamento da atualização parou"):
        pub.publicar(versao.VERSAO, arquivo_da_chave=a["chave"], chave_publica=PUBLICA, vpk=a["vpk"],
                     rascunho_base=a["rascunho"], pasta_de_saida=a["saida"], destino=pub.DestinoPasta(a["servidor"]))
    assert "o pacote do Velopack saiu errado" in capsys.readouterr().out
    assert pub.DestinoPasta(a["servidor"]).situacao(versao.etiqueta_da_versao(versao.VERSAO)) is None


def test_volta7_achado4_o_empacotar_chamado_sozinho_recusa_antes_de_mexer_na_pasta(ambiente):
    """Achado 4 do relatório 6 de quem tentou quebrar (20/11/2026): `construir_pacote_do_velopack` chamado sozinho com
    uma pasta que a conferência recusa mexia nela antes de recusar (`preparar_saida` gravava o motor-exigido.json e
    apagava o zip do motor de instalar\\). Agora a conferência vem antes: a pasta recusada fica exatamente como estava,
    e o vpk não roda. Rodado em db4b377a: o zip some e o motor-exigido.json aparece."""
    a = ambiente
    de_fora = _pasta_pronta(a["tmp"] / "de-fora" / "EditorImpressao", VERSAO)
    instalar = de_fora / atualizacao.PASTA_DO_QUE_SE_INSTALA
    (instalar / atualizacao.VC_REDIST_NOME).unlink()
    (instalar / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)).write_bytes(b"zip do motor de outra vez")
    antes = {p: p.read_bytes() for p in de_fora.rglob("*") if p.is_file()}
    motor = empacotar.MotorPublicado(ocr_kraken.VERSAO_DO_MOTOR, versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR),
                                     "0" * 64, ETIQUETA_DO_MOTOR)
    assert empacotar.construir_pacote_do_velopack(a["tmp"] / "saida-vpk", VERSAO, empacotar.ATUALIZACAO, de_fora, motor,
                                                  vpk=a["vpk"]) is None
    depois = {p: p.read_bytes() for p in de_fora.rglob("*") if p.is_file()}
    assert depois == antes, "a pasta recusada foi mudada antes da recusa"
    assert _vezes_que_o_vpk_rodou(a) == []


def test_volta7_achado5_a_pasta_das_provas_com_espaco_no_nome(ambiente, monkeypatch):
    """Achado 5 do relatório 6 de quem tentou quebrar (20/11/2026, família F3): as aspas do `--pasta "<pasta>"` nos
    comandos das frases não tinham teste (as pastas dos testes não tinham espaço; a mutação Z6, sem as aspas, passava).
    Aqui a pasta das provas tem espaço no nome: seguir ao pé da letra a frase do motor que falta publica o motor NESSA
    pasta, e seguir a do rascunho que sobrou apaga o rascunho NELA; nenhuma fala com o GitHub."""
    import shlex

    a = ambiente
    pasta = a["tmp"] / "versoes de prova"
    destino = pub.DestinoPasta(pasta)
    with pytest.raises(pub.Parou, match="publique o motor antes") as erro:
        _publicar(a, destino=destino)
    comando = destino.comando_de_publicar_o_motor()
    assert comando in str(erro.value) and f'"{pasta}"' in comando, str(erro.value)
    pedidos = []
    publicar_de_verdade = pub.publicar_motor
    monkeypatch.setattr(pub, "publicar_motor", lambda destino_pasta=None, *x, **k: pedidos.append(destino_pasta))

    def nao_pode(self, *argumentos, **k):
        """Seguir a frase da pasta não pode chegar ao GitHub."""
        raise AssertionError(f"a frase da pasta foi ao GitHub: {argumentos}")

    monkeypatch.setattr(pub.DestinoGitHub, "_gh", nao_pode)
    assert pub.main([p.strip('"') for p in shlex.split(comando, posix=False)][1:]) == 0
    assert pedidos == [pasta], pedidos
    monkeypatch.setattr(pub, "publicar_motor", publicar_de_verdade)
    destino.criar_rascunho(ETIQUETA, "t", "n")
    with pytest.raises(pub.Parou, match="sobrou um rascunho") as erro:
        pub.publicar_arquivos(destino, ETIQUETA, "t", "n", [], lambda: None)
    _seguir_a_frase_sem_tocar_o_github(str(erro.value), destino, ETIQUETA, monkeypatch)


# ---------------------------------------------------------------------------------------------------------------------
# Passo 2, volta 8 (a prova à vista de 20/11/2026, 18h a 19h30, e o relatório 7 de quem tentou quebrar)
# ---------------------------------------------------------------------------------------------------------------------

def _gh_de_mentira_na_classe(monkeypatch, tmp: Path) -> "_GitHubDeMentira":
    """O gh de mentira atrás de todo `DestinoGitHub` (inclusive o que o `main` cria sozinho, sem o teste vê-lo)."""
    gh = _GitHubDeMentira(tmp)
    monkeypatch.setattr(pub.DestinoGitHub, "_gh", lambda self, *argumentos, **k: gh(*argumentos))
    return gh


@pytest.mark.parametrize("onde", ["pasta", "github"])
@pytest.mark.parametrize("etiqueta", [ETIQUETA, versao.etiqueta_do_motor(ocr_kraken.VERSAO_DO_MOTOR)])
def test_volta8_defeito2_o_apagar_diz_que_apagou_quando_apagou(ambiente, monkeypatch, capsys, onde, etiqueta):
    """O defeito 2 da prova à vista de 20/11/2026 (provas 3a, 5 e 7c; registros em C:\\EditorImpressaoProva): o
    `--apagar` apagou de verdade (na pasta e no GitHub, conferido pela gerente), mas a única frase foi "v1.1.0: não
    existe em ... (conferido)", a mesma de quando não havia nada para apagar. O `main` escrevia a frase por conta própria,
    sem saber qual dos dois casos foi (o lugar único do apagar devolvia só o aviso do gh). Agora a frase sai do lugar
    único (`apagar_e_conferir`, o `Apagado.frase`): "foi apagada (conferido)" quando havia o que apagar, e "não existia
    ..., e nada foi apagado (conferido)" quando não havia. Na pasta das provas e no GitHub, para a versão e para o motor.
    Rodado em 21f1fc50: a frase depois de apagar é "não existe em"."""
    a = ambiente
    argumentos = ["--apagar", etiqueta]
    if onde == "pasta":
        destino = pub.DestinoPasta(a["servidor"])
        destino.criar_rascunho(etiqueta, "t", "n")
        destino.liberar(etiqueta)
        argumentos += ["--pasta", str(a["servidor"])]
    else:
        gh = _gh_de_mentira_na_classe(monkeypatch, a["tmp"])
        gh.publicacoes[etiqueta] = {"rascunho": False, "arquivos": {}}
        destino = pub.DestinoGitHub()
    assert destino.situacao(etiqueta) == "liberada"
    capsys.readouterr()
    assert pub.main(argumentos) == 0
    frase = capsys.readouterr().out
    assert destino.situacao(etiqueta) is None, "o --apagar não apagou"
    assert "foi apagada" in frase and "(conferido)" in frase, frase
    assert "não exist" not in frase, frase
    assert frase.strip() == pub.Apagado(etiqueta, destino.nome, existia=True).frase, frase
    assert pub.main(argumentos) == 0, "apagar o que já não existe não é erro"
    frase = capsys.readouterr().out
    assert "não existia" in frase and "nada foi apagado" in frase and "(conferido)" in frase, frase
    assert "foi apagada" not in frase, frase
    assert frase.strip() == pub.Apagado(etiqueta, destino.nome, existia=False).frase, frase


def test_volta8_defeito2_o_caminho_de_erro_usa_a_mesma_frase_do_apagar(ambiente):
    """Defeito 2, o outro caminho que apaga (CLAUDE.md §11.12: a frase de cada desfecho num lugar só): o erro antes do
    pedido de liberar apaga o rascunho e diz "foi apagada (conferido)" com a MESMA frase do `--apagar`
    (`Apagado.frase`), e não com uma escrita à parte. O que é apagado não muda (D-816: depois do pedido de liberar, nada
    se apaga; aqui o erro vem antes). Rodado em 21f1fc50: `pub.Apagado` não existia."""
    a = ambiente
    destino = pub.DestinoPasta(a["servidor"])

    def ler_de_volta_errado():
        """A leitura de volta da assinatura acusa (um erro antes do pedido de liberar)."""
        raise pub.Parou("a assinatura lida de volta não confere")

    with pytest.raises(pub.Parou, match="não confere") as erro:
        pub.publicar_arquivos(destino, ETIQUETA, "t", "n", [], ler_de_volta_errado)
    assert destino.situacao(ETIQUETA) is None
    assert pub.Apagado(ETIQUETA, destino.nome, existia=True).frase in str(erro.value), str(erro.value)


def test_volta8_defeito2_o_que_o_apagar_devolve_nao_mudou(ambiente, monkeypatch):
    """D-605: `apagar_publicacao` continua devolvendo o que devolvia (o aviso do gh, ou nada) e o `apagar_e_conferir`
    diz, pela mesma conta, se havia o que apagar. O caso do gh que avisa ao apagar uma liberada (a etiqueta que falha,
    achado 1 da volta 1) volta como aviso nos dois e entra na frase."""
    a = ambiente
    gh = _gh_de_mentira_na_classe(monkeypatch, a["tmp"])
    destino = pub.DestinoGitHub()
    gh.publicacoes[ETIQUETA] = {"rascunho": True, "arquivos": {}}
    assert pub.apagar_publicacao(destino, ETIQUETA) is None
    assert pub.apagar_publicacao(destino, ETIQUETA) is None
    gh.publicacoes[ETIQUETA] = {"rascunho": False, "arquivos": {}}
    gh.falhar_ao_apagar_a_etiqueta = True
    feito = pub.apagar_e_conferir(destino, ETIQUETA)
    assert feito.existia and feito.aviso and "o gh avisou" in feito.aviso, feito
    assert feito.aviso in feito.frase and "foi apagada" in feito.frase, feito.frase
    nada = pub.apagar_e_conferir(destino, ETIQUETA)
    assert not nada.existia and nada.aviso is None


_VC_OFICIAL = "14.44.35211.0"


@pytest.mark.parametrize("conteudo, aceita", [
    (_VC_OFICIAL.encode("utf-8"), True),
    ((_VC_OFICIAL + "\r\n").encode("utf-8"), True),
    (("  " + _VC_OFICIAL + "  ").encode("utf-8"), True),
    (b"\xef\xbb\xbf" + _VC_OFICIAL.encode("utf-8"), False),          # a marca de UTF-8 no começo
    (_VC_OFICIAL.encode("utf-16"), False),
    (b"", False),
    (b"14.44", False),
])
def test_volta8_baixo6_a_versao_do_visual_c_e_lida_por_uma_funcao_so(ambiente, conteudo, aceita):
    """Achado 6 do relatório 7 de quem tentou quebrar (20/11/2026, CLAUDE.md §11.12: "um dado é lido e gravado por uma
    função só"): o arquivo da versão do Visual C++ do pacote era lido de dois jeitos, um na conferência do publicar
    (`empacotar.conferir_pasta_pronta`) e outro no programa instalado (`atualizacao.instalar_visual_c_se_faltar`, que
    decide se instala o Visual C++ no notebook do Kaique). Agora os dois leem por
    `atualizacao.versao_do_visual_c_do_pacote` (o jeito do publicar, o que a prova conferiu). Para cada jeito de arquivo
    que o relatório 7 testou: o que a conferência aceita, o programa instalado lê exatamente como a versão conferida; o
    resto a conferência recusa. Rodado em 21f1fc50: a função única não existia."""
    a = ambiente
    pasta = a["pasta"]
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_VERSAO).write_bytes(conteudo)
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert (problemas == []) == aceita, problemas
    if aceita:
        assert atualizacao.versao_do_visual_c_do_pacote(pasta) == VERSAO_DO_VISUAL_C_DE_PROVA
    else:
        assert any("Visual C++" in p for p in problemas), problemas


def test_volta8_baixo6_o_publicar_e_o_programa_instalado_usam_a_mesma_leitura(ambiente, monkeypatch):
    """Achado 6 do relatório 7, a prova do "caminho → função" (§11.12): trocada só a função única da leitura, a
    conferência do publicar e o programa instalado passam a ver a mesma versão trocada (e, sem o arquivo, cada um faz o
    que fazia: o publicar recusa; o programa instalado usa "0.0.0", e só instala se não há Visual C++ nenhum).
    Rodado em 21f1fc50: a troca não muda nada nos dois (cada um lia por conta própria)."""
    a = ambiente
    pasta = a["pasta"]
    monkeypatch.setattr(atualizacao, "versao_do_visual_c_do_pacote", lambda p: "7.7.7", raising=False)
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert any("diz que o Visual C++ é o 7.7.7" in p for p in problemas), problemas
    registrado = []
    monkeypatch.setattr(atualizacao, "registrar", registrado.append)
    atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: (0, ""))
    assert any("Visual C++ 7.7.7" in r for r in registrado), registrado
    monkeypatch.setattr(atualizacao, "versao_do_visual_c_do_pacote", lambda p: None)
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert any("não tem a versão do Visual C++" in p for p in problemas), problemas
    registrado.clear()
    rodou = []
    atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: (14, 0, 0),
                                            rodar=lambda c, t: rodou.append(c) or (0, ""))
    assert rodou == [], "sem o arquivo da versão e com um Visual C++ instalado, não instala (como antes)"
    atualizacao.instalar_visual_c_se_faltar(pasta, ler=lambda: None, rodar=lambda c, t: rodou.append(c) or (0, ""))
    assert rodou and any("Visual C++ 0.0.0" in r for r in registrado), registrado


def test_volta8_baixo1a_a_leitura_da_assinatura_que_falha_nunca_vira_passou(ambiente, monkeypatch):
    """Achado 1 do relatório 7 de quem tentou quebrar, (a) (família F3: proteção sem teste; a mutação W5, "a leitura que
    falha vira passou na régua única", passava em todos os testes): a peça do PowerShell responde "não terminou no
    tempo" ao ler a assinatura do Visual C++. A pasta já montada é recusada porque o Visual C++ "não é o oficial da
    Microsoft" (e não só porque a versão ficou diferente), a montagem recusa o arquivo da pasta de downloads, e o
    publicar para antes do vpk. Com a W5, a montagem aceitaria o arquivo com a versão vazia."""
    from core import windows

    a = ambiente
    pasta = a["pasta"]
    visual_c = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_NOME
    visual_c.write_bytes(b"MZ um Visual C++ que o Windows nao chega a ler")
    baixado = a["tmp"] / "downloads-que-nao-le" / empacotar.VC_REDIST_NOME
    baixado.parent.mkdir()
    baixado.write_bytes(b"MZ um Visual C++ que o Windows nao chega a ler")
    lidos = []

    def powershell_que_nao_termina(texto, limite_s=120, **k):
        """A conversa com o PowerShell que passa do tempo (como a peça responde quando ele não termina)."""
        lidos.append(texto)
        return windows.Resposta(windows.FALHOU, "o PowerShell não terminou no tempo", "passou de 120 s")

    monkeypatch.setattr(windows, "rodar_powershell", powershell_que_nao_termina)
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert lidos, "a conferência não chegou a pedir a leitura ao Windows"
    assert any("não é o oficial da Microsoft" in p and "não conseguiu ler" in p for p in problemas), problemas
    monkeypatch.setattr(empacotar, "DOWNLOADS", baixado.parent)
    arquivo, versao_lida, da_montagem = empacotar.preparar_vc_redist(baixar=False)
    assert arquivo is None and versao_lida == "" and da_montagem, (arquivo, versao_lida, da_montagem)
    assert "não é o oficial da Microsoft" in da_montagem[0], da_montagem
    _publicar_o_motor(a)
    with pytest.raises(pub.Parou, match="a pasta do programa não serve"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []


def _copia_do_powershell_do_windows(destino: Path) -> Path:
    """Uma cópia do powershell.exe do próprio Windows (existe em todo Windows, também no do GitHub): um arquivo de
    verdade, com assinatura de verdade da Microsoft, que NÃO é o Visual C++ (assinado por "CN=Microsoft Windows")."""
    original = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / \
        "powershell.exe"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, destino)
    return destino


def test_volta8_baixo1b_um_programa_da_microsoft_que_nao_e_o_visual_c_e_recusado_pela_mesma_regua(ambiente,
                                                                                                   monkeypatch):
    """Achado 1 do relatório 7 de quem tentou quebrar, (b) (família F3; a mutação W1, "a conferência da pasta com régua
    própria, que aceita qualquer arquivo com assinatura válida", passava): o teste da régua única usava só um arquivo
    sem assinatura, que qualquer régua recusa. Aqui o "Visual C++" é uma cópia do powershell.exe do Windows: o Windows
    diz que a assinatura é VÁLIDA (lida pela peça de verdade, sem mentira; D-767), mas quem assinou é "CN=Microsoft
    Windows" e o produto não é o Visual C++. A pasta já montada (com o arquivo da versão igual à versão que o Windows lê
    nele, para só a régua decidir) e a montagem recusam, pelo assinante; o publicar para antes do vpk."""
    a = ambiente
    pasta = a["pasta"]
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    copia = _copia_do_powershell_do_windows(instalar / atualizacao.VC_REDIST_NOME)
    lida = empacotar.assinatura_do_arquivo(copia)
    assert lida["status"] == "Valid" and "CN=Microsoft Windows" in lida["assinante"], lida
    (instalar / atualizacao.VC_REDIST_VERSAO).write_text(lida["versao"], encoding="utf-8")
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert any("não é o oficial da Microsoft" in p and "não foi assinado pela Microsoft" in p for p in problemas), \
        problemas
    baixado = _copia_do_powershell_do_windows(a["tmp"] / "downloads-powershell" / empacotar.VC_REDIST_NOME)
    monkeypatch.setattr(empacotar, "DOWNLOADS", baixado.parent)
    arquivo, _, da_montagem = empacotar.preparar_vc_redist(baixar=False)
    assert arquivo is None and da_montagem and "não foi assinado pela Microsoft" in da_montagem[0], da_montagem
    assert baixado.is_file(), "a montagem nunca apaga o arquivo que não confere"
    _publicar_o_motor(a)
    with pytest.raises(pub.Parou, match="não foi assinado pela Microsoft"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []


@pytest.mark.parametrize("conteudo", ["", "14.44", "14.44.35211", "14", " \n"])
def test_volta8_baixo2_o_arquivo_da_versao_vazio_ou_pela_metade_e_recusado(ambiente, conteudo):
    """Achado 2 do relatório 7 de quem tentou quebrar (família F3; a mutação W4, a versão comparada por "começa com",
    passava): o único caso de teste era uma versão inteira e diferente. O arquivo da versão vazio, ou com só um pedaço
    da versão, é recusado (o programa instalado lê esse arquivo para decidir se instala o Visual C++ no notebook do
    Kaique: um pedaço faria a conta errada)."""
    a = ambiente
    pasta = a["pasta"]
    (pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA / atualizacao.VC_REDIST_VERSAO).write_text(conteudo, encoding="utf-8")
    problemas = empacotar.conferir_pasta_pronta(pasta, VERSAO)
    assert any("diz que o Visual C++ é o" in p for p in problemas), problemas
    _publicar_o_motor(a)
    with pytest.raises(pub.Parou, match="diz que o Visual C"):
        _publicar(a)
    assert _vezes_que_o_vpk_rodou(a) == []


@pytest.mark.parametrize("licenca", empacotar.LICENCAS_DO_TESSERACT)
def test_volta8_baixo3_sem_a_licenca_do_tesseract_a_pasta_e_o_pacote_sao_recusados(ambiente, monkeypatch, capsys,
                                                                                   licenca):
    """Achado 3 do relatório 7 de quem tentou quebrar (família F3; as mutações W2 e W3, tirar as licenças da conferência
    da pasta e da do pacote, passavam): a licença do Tesseract tem de ir junto com ele. A pasta sem a licença é recusada
    antes do vpk; e um vpk que deixa a licença de fora do pacote faz o publicar parar ("o pacote do Velopack saiu
    errado"), sem nada publicado."""
    a = ambiente
    relativo = f"{empacotar.PASTA_DO_TESSERACT}/{licenca}"
    sem_licenca = _pasta_pronta(a["tmp"] / "sem-licenca" / "EditorImpressao", VERSAO)
    (sem_licenca / relativo).unlink()
    problemas = empacotar.conferir_pasta_pronta(sem_licenca, VERSAO)
    assert any("não tem o Tesseract inteiro" in p and relativo in p for p in problemas), problemas
    _publicar_o_motor(a)
    with pytest.raises(pub.Parou, match="a pasta do programa não serve"):
        _publicar(a, pasta_pronta=sem_licenca)
    assert _vezes_que_o_vpk_rodou(a) == []
    monkeypatch.setenv("VPK_FALSO_SEM", relativo)
    capsys.readouterr()
    with pytest.raises(pub.Parou, match="empacotamento da atualização parou"):
        _publicar(a)
    saida = capsys.readouterr().out
    assert "o pacote do Velopack saiu errado" in saida and relativo in saida, saida
    assert pub.DestinoPasta(a["servidor"]).situacao(ETIQUETA) is None



def test_obs6_a_frase_do_apagar_sai_com_a_contracao(tmp_path):
    """Observação 6 do relatório 8 de quem tentou quebrar (21/11/2026): a frase do apagar saía "foi apagada de a pasta
    ...", "de o GitHub (...)" e "não existia em a pasta ...", sem a contração. Agora, no lugar único das frases do apagar
    (`Apagado.frase`, pela `com_preposicao`): "da pasta", "do GitHub", "na pasta", "no GitHub", nos dois destinos. O
    sentido não muda: "foi apagada" e "(conferido)" continuam só quando havia o que apagar. Rodado em 6fa766c4: sai
    "de a pasta"."""
    pasta = pub.DestinoPasta(tmp_path / "versoes de prova")
    github = pub.DestinoGitHub("dono/nome")
    esperado = [(pasta, "da pasta", "na pasta"), (github, "do GitHub (dono/nome)", "no GitHub (dono/nome)")]
    for destino, de, em in esperado:
        apagada = pub.Apagado("v9.9.9", destino.nome, existia=True).frase
        assert apagada.startswith(f"a publicação v9.9.9 foi apagada {de}") and apagada.endswith("(conferido)"), apagada
        nao_havia = pub.Apagado("v9.9.9", destino.nome, existia=False).frase
        assert nao_havia.startswith(f"v9.9.9: não existia {em}") and "nada foi apagado (conferido)" in nao_havia, nao_havia
        for errado in (" de a ", " de o ", " em a ", " em o "):
            assert errado not in apagada and errado not in nao_havia, (errado, apagada, nao_havia)
    assert pub.com_preposicao("de", "uma pasta") == "de uma pasta"



# ---------------------------------------------------------------------------------------------------------------------
# Volta 11 (21/11/2026): as frases do publicar com a contração ("na pasta", "no GitHub"), pela com_preposicao
# ---------------------------------------------------------------------------------------------------------------------

# A guarda não tem exceção (D-821, Samuel, 21/11/2026: "ok"): a frase da D-816, que ficou de fora até a resposta
# dele, também passa pela com_preposicao.


# Os lugares onde o nome de um destino pode aparecer no publicar (volta 12, baixo 1 do relatório 10): as chamadas que
# recebem o nome (a com_preposicao, que junta a preposição; o Apagado, que guarda o nome e escreve a frase pela
# com_preposicao) e, dentro de uma frase, o começo (só espaço antes) ou logo depois de "para " ("para a pasta" está
# certo). Seguro mexer: acrescentar um lugar quando a frase nova estiver certa em português. Arriscado: aceitar um uso
# solto (variável, soma de textos, .format): é por onde "em a pasta" volta sem ninguém ver.
_RECEBEM_O_NOME_DO_DESTINO = {"com_preposicao", "Apagado"}
_ANTES_DO_NOME_NA_FRASE = ("para ",)


def _preposicao_a_mao(fonte: str) -> list[tuple[int, str, str]]:
    """Todo uso do nome de um destino (`.nome` ou `.onde`) fora dos lugares aceitos: (linha, função, o trecho). Lido
    pela árvore do Python (`ast`), não pelo texto da linha.

    Volta 12 (baixo 1 do relatório 10 de quem tentou quebrar, 21/11/2026): a guarda da volta 11 procurava um texto ("em
    "/"de " logo antes de `{… .nome}` num f-string), e quatro outros jeitos de escrever a mesma junção passavam
    (mutações G1 a G4: somar com `+`, guardar o nome numa variável, um parêntese antes do "em", o `.format`). Agora ela
    cobra a coisa de verdade: o nome do destino só aparece dentro de `com_preposicao(...)`, passado ao `Apagado(...)`,
    no começo de uma frase ou logo depois de "para "; qualquer outro uso é acusado."""
    import ast

    arvore = ast.parse(fonte)
    pai, funcao = {}, {}

    def olhar(no, dentro: str) -> None:
        """Anota o pai de cada nó e a função de fora."""
        for filho in ast.iter_child_nodes(no):
            pai[filho] = no
            nome = filho.name if isinstance(filho, (ast.FunctionDef, ast.AsyncFunctionDef)) else dentro
            funcao[filho] = nome
            olhar(filho, nome)

    olhar(arvore, "(fora de função)")

    def aceito(uso) -> bool:
        """O uso está num dos lugares aceitos?"""
        de_cima = pai.get(uso)
        if isinstance(de_cima, ast.Call) and uso in de_cima.args:
            chamada = de_cima.func
            nome = chamada.id if isinstance(chamada, ast.Name) else getattr(chamada, "attr", "")
            return nome in _RECEBEM_O_NOME_DO_DESTINO
        if isinstance(de_cima, ast.FormattedValue) and de_cima.format_spec is None:
            frase = pai.get(de_cima)
            if not isinstance(frase, ast.JoinedStr):
                return False
            i = frase.values.index(de_cima)
            if i == 0:
                return True
            antes = frase.values[i - 1]
            return (isinstance(antes, ast.Constant) and isinstance(antes.value, str)
                    and (antes.value.strip() == "" and i == 1 or antes.value.endswith(_ANTES_DO_NOME_NA_FRASE)))
        return False

    return [(uso.lineno, funcao.get(uso, "?"), ast.unparse(pai.get(uso, uso))[:60])
            for uso in ast.walk(arvore)
            if isinstance(uso, ast.Attribute) and uso.attr in ("nome", "onde") and isinstance(uso.ctx, ast.Load)
            and not aceito(uso)]


def test_volta11_nenhuma_frase_do_publicar_junta_em_ou_de_com_o_destino_a_mao():
    """Lista de bugs de 21/11/2026 ("Umas 20 frases do publicar saem 'em a pasta ...' e 'em o GitHub ...'"; vistas de
    novo na prova à vista de 21/11: "não está publicado em a pasta", "lido de volta de a pasta", "liberada em a
    pasta"): as frases juntavam a preposição com o nome do destino à mão (`f"... em {destino.nome}"`), e o nome abre com
    o artigo ("a pasta ...", "o GitHub (...)"). A junção tem um lugar só, `com_preposicao` (volta 10, a do apagar). Esta
    guarda lê o código do publicar e acusa toda frase que volte a escrever "em "/"de " antes do nome do destino, sem
    exceção: a frase da D-816, que ficou de fora até a resposta do Samuel, também (D-821, 21/11/2026: "ok"). Rodado em
    edd39a9f: acusa 33 junções (31 frases e as duas da D-816); em 1624a05a: acusa as duas da D-816. Volta 12 (baixo 1 do
    relatório 10): a guarda acusa qualquer uso do nome do destino fora dos lugares aceitos (`_preposicao_a_mao`), não só
    o texto "em {…}"; as mutações G1 a G4 (e a G5, "por a pasta") do relatório são acusadas. A mudança desta guarda foi
    autorizada pela D-822 (Samuel, 21/11/2026, à pergunta "Conserto as 3 agora?": "ok")."""
    fonte = (RAIZ / "publicar_versao_kaique.py").read_text(encoding="utf-8")
    achados = _preposicao_a_mao(fonte)
    assert achados == [], f"frases com a preposição escrita à mão (use com_preposicao): {achados}"


@pytest.mark.parametrize("onde", ["pasta", "github"])
def test_volta11_as_frases_do_publicar_saem_com_a_contracao_na_pasta_e_no_github(ambiente, monkeypatch, capsys, onde):
    """Lista de bugs de 21/11/2026 (as frases "em a pasta", "de a pasta", "em o GitHub"): pelos caminhos principais do
    publicar, na pasta das provas e no GitHub (o gh de mentira dos testes; o de verdade é da prova à vista, D-785), o
    que sai na tela e nas frases de parada diz "na pasta"/"no GitHub" e "da pasta"/"do GitHub": a versão antes do motor
    (para: "não está publicado na pasta"), o motor e a versão ("lido de volta da pasta", "liberada na pasta"), os dois
    de novo ("já existe na pasta"), e a leitura de uma publicação que não há ("não há publicação ... na pasta"). O que
    o publicar faz em cada caminho não muda (os outros testes deste arquivo cobram). Rodado em edd39a9f: "em a pasta"."""
    a = ambiente
    if onde == "pasta":
        destino = pub.DestinoPasta(a["servidor"])
        de, em = f"da pasta {a['servidor']}", f"na pasta {a['servidor']}"
    else:
        destino = pub.DestinoGitHub("dono/projeto")
        monkeypatch.setattr(destino, "_gh", _GitHubDeMentira(a["tmp"]))
        de, em = "do GitHub (dono/projeto)", "no GitHub (dono/projeto)"
    textos = []

    def parada(fazer) -> str:
        """A frase da parada (Parou) de um caminho, guardada para a conferência do fim."""
        with pytest.raises(pub.Parou) as erro:
            fazer()
        textos.append(str(erro.value))
        return str(erro.value)

    frase = parada(lambda: _publicar(a, destino=destino))
    assert f"não está publicado {em}" in frase, frase
    _publicar_o_motor(a, destino=destino)
    _publicar(a, destino=destino)
    saida = capsys.readouterr().out
    textos.append(saida)
    assert f"lido de volta {de}:" in saida and f"{ETIQUETA} liberada {em}" in saida, saida
    assert f"já existe {em}" in parada(lambda: _publicar(a, destino=destino))
    assert f"já existe {em}" in parada(lambda: _publicar_o_motor(a, destino=destino))
    assert f"não há publicação v0.0.1 {em}" in parada(lambda: destino.arquivos("v0.0.1"))
    assert f"não está na publicação {ETIQUETA} {em}" in parada(lambda: destino.soma(ETIQUETA, "nao-ha.txt"))
    for texto in textos:
        for errado in (" em a pasta", " de a pasta", " em o GitHub", " de o GitHub"):
            assert errado not in texto, (errado, texto)
