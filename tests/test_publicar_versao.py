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
    for f in sorted(pasta.rglob("*")):
        if f.is_file():
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


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Tudo o que um publicar de teste precisa: a chave fora do 'repositório', o vpk de mentira, o destino (uma pasta
    de verdade), a base do rascunho, a pasta de saída, um motor com ficha e uma pasta do programa pronta."""
    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")     # tmp_path pode estar dentro da cópia
    chave = tmp_path / "chave.txt"
    chave.write_text(assinatura.texto_da_chave_privada(CHAVE), encoding="utf-8")
    outra = tmp_path / "outra-chave.txt"
    outra.write_text(assinatura.texto_da_chave_privada(OUTRA_CHAVE), encoding="utf-8")
    script = tmp_path / "vpk_falso.py"
    script.write_text(VPK_FALSO, encoding="utf-8")
    vpk = tmp_path / "vpk.cmd"
    vpk.write_text(f'@"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
    diario = tmp_path / "vpk-rodou.txt"
    monkeypatch.setenv("VPK_FALSO_DIARIO", str(diario))
    monkeypatch.delenv("VPK_FALSO_FALHA", raising=False)
    monkeypatch.delenv("VPK_FALSO_ESPERA", raising=False)
    monkeypatch.delenv("VPK_FALSO_FILHO", raising=False)
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


def _pasta_pronta(pasta: Path, versao_da_pasta: str) -> Path:
    """Uma pasta do programa pronta (o que o empacotador confere no pacote: o .exe, os modelos, as DLLs, o Visual C++),
    sem o motor solto, com a ficha da versão escrita pela função de verdade."""
    (pasta / empacotar.INTERNO).mkdir(parents=True)
    (pasta / f"{empacotar.NOME}.exe").write_bytes(b"MZ editor")
    for origem, destino in [*empacotar.modelos_do_programa(), *empacotar.nativos_do_programa()]:
        alvo = pasta / empacotar.INTERNO / destino / origem.name
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(b"x")
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    instalar.mkdir()
    (instalar / atualizacao.VC_REDIST_NOME).write_bytes(b"MZ visual c")
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
