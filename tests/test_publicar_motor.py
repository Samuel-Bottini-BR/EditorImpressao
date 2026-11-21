"""Testes do motor do Kraken à parte, na parte que o publicar usa (plano da parte do Windows, passo 2, peça 9):
a versão do motor, a ficha (motor.json) gravada pelo montar_motor_kraken.py, a conferência única
(core/ocr_kraken.conferir_motor), o arquivo do motor (empacotar.zipar_motor) e os nomes (versao.py).

Rodam com um motor de mentira (a forma de um motor, arquivos pequenos): a conferência lê a pasta e o zip de verdade.
O motor de verdade (34 mil arquivos) é conferido na prova à vista (D-785). Seguro mexer: acrescentar casos.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path, PureWindowsPath

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import empacotar  # noqa: E402
import historico  # noqa: E402
import montar_motor_kraken  # noqa: E402
import versao  # noqa: E402
from core import ocr_kraken  # noqa: E402


def _motor(pasta: Path, ficha: bool = True) -> Path:
    """Um motor de mentira com a forma de um motor do jeito novo (e, de fábrica, a ficha gravada pela função de
    verdade)."""
    kraken = pasta / "python" / "Lib" / "site-packages" / "kraken"
    kraken.mkdir(parents=True)
    (pasta / "python" / "python.exe").write_bytes(b"MZ python")
    (kraken / "blla.mlmodel").write_bytes(b"modelo" * 100)
    (kraken / "outro.py").write_text("x = 1\n", encoding="utf-8")
    (pasta / ocr_kraken.NOME_DO_SERVIDOR).write_text(f"VERSAO_PROTOCOLO = {ocr_kraken.VERSAO_PROTOCOLO}\n",
                                                     encoding="utf-8")
    if ficha:
        montar_motor_kraken.gravar_ficha_do_motor(pasta)
    return pasta


def test_a_ficha_gravada_pelo_montar_confere_pela_conferencia_unica(tmp_path):
    """A ficha que o montar grava lista cada arquivo com o tamanho, a versão do motor e a do protocolo (lidas do lugar
    único), e a conferência única diz "confere"."""
    motor = _motor(tmp_path / "m")
    ficha = json.loads((motor / ocr_kraken.NOME_DA_FICHA).read_text(encoding="utf-8"))
    assert ficha["versao_do_motor"] == ocr_kraken.VERSAO_DO_MOTOR
    assert ficha["versao_protocolo"] == ocr_kraken.VERSAO_PROTOCOLO
    assert ["python/python.exe", len(b"MZ python")] in ficha["arquivos"]
    assert not any(a[0] == ocr_kraken.NOME_DA_FICHA for a in ficha["arquivos"])
    assert ocr_kraken.conferir_motor(motor) == []
    assert not list(motor.glob("*.gravando")), "a ficha é gravada num provisório e trocada de uma vez"


@pytest.mark.parametrize("estrago, trecho", [
    ("sem ficha", "não tem a ficha"),
    ("arquivo sumiu", "faltam 1 arquivo"),
    ("arquivo mudou", "diferentes da ficha"),
    ("outra versão", "é da versão 99"),
    ("outro protocolo", "protocolo 99"),
    ("fora da pasta", "faltam 1 arquivo"),
])
def test_o_motor_estragado_ou_de_outra_versao_nao_confere(tmp_path, estrago, trecho):
    """A conferência única acusa cada estrago (e nunca dá "confere" sem a ficha)."""
    motor = _motor(tmp_path / "m", ficha=estrago != "sem ficha")
    caminho_da_ficha = motor / ocr_kraken.NOME_DA_FICHA
    if estrago == "arquivo sumiu":
        (motor / "python" / "Lib" / "site-packages" / "kraken" / "outro.py").unlink()
    elif estrago == "arquivo mudou":
        (motor / "python" / "Lib" / "site-packages" / "kraken" / "blla.mlmodel").write_bytes(b"cortado")
    elif estrago in ("outra versão", "outro protocolo", "fora da pasta"):
        ficha = json.loads(caminho_da_ficha.read_text(encoding="utf-8"))
        if estrago == "outra versão":
            ficha["versao_do_motor"] = 99
        elif estrago == "outro protocolo":
            ficha["versao_protocolo"] = 99
        else:
            (tmp_path / "segredo.txt").write_text("x", encoding="utf-8")
            ficha["arquivos"].append(["../segredo.txt", 1])
        caminho_da_ficha.write_text(json.dumps(ficha), encoding="utf-8")
    problemas = ocr_kraken.conferir_motor(motor)
    assert any(trecho in p for p in problemas), problemas


def test_o_empacotador_usa_a_forma_do_motor_do_lugar_unico(tmp_path):
    """A forma do motor (Python, servidor, modelo) mora em core/ocr_kraken.problemas_da_forma; a regra do empacotador
    (empacotar.conferir_motor_kraken) dá as mesmas frases e acrescenta só a de montagem (jeito velho)."""
    sem_python = tmp_path / "vazio"
    sem_python.mkdir()
    assert empacotar.conferir_motor_kraken(sem_python) == ocr_kraken.problemas_da_forma(sem_python)
    motor = _motor(tmp_path / "m", ficha=False)
    (motor / ocr_kraken.NOME_DO_SERVIDOR).write_text("VERSAO_PROTOCOLO = 99\n", encoding="utf-8")
    assert ocr_kraken.problemas_da_forma(motor) and \
        set(ocr_kraken.problemas_da_forma(motor)) <= set(empacotar.conferir_motor_kraken(motor))


def test_o_arquivo_do_motor_leva_tudo_da_ficha_e_e_conferido(tmp_path):
    """O motor comprimido num arquivo só leva a ficha e cada arquivo dela; a conferência do zip usa a mesma regra da
    pasta (conferir_ficha); um zip sem um arquivo não confere."""
    motor = _motor(tmp_path / "m")
    destino = tmp_path / "saida" / versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)
    destino.parent.mkdir()
    assert empacotar.zipar_motor(motor, destino, livre=lambda p: 500 * empacotar.GB) is None
    assert destino.is_file() and not destino.with_name(destino.name + ".fazendo").exists()
    assert empacotar.problemas_do_zip_do_motor(destino) == []
    quebrado = tmp_path / "quebrado.zip"
    with zipfile.ZipFile(destino) as z, zipfile.ZipFile(quebrado, "w") as q:
        for nome in z.namelist():
            if not nome.endswith("outro.py"):
                q.writestr(nome, z.read(nome))
    assert any("faltam 1 arquivo" in p for p in empacotar.problemas_do_zip_do_motor(quebrado))


def test_d776_comprimir_o_motor_para_quando_o_disco_cai_abaixo_da_reserva(tmp_path):
    """D-776: a compressão do motor vigia o espaço; abaixo da reserva para, sem deixar arquivo pela metade."""
    motor = _motor(tmp_path / "m")
    destino = tmp_path / "motor.zip"
    motivo = empacotar.zipar_motor(motor, destino, livre=lambda p: 5 * empacotar.GB)
    assert motivo and "reserva" in motivo
    assert not destino.exists() and not destino.with_name(destino.name + ".fazendo").exists()


def test_d763_o_nome_do_pacote_do_motor_e_outro_e_nao_e_pasta_de_dados():
    """D-763 e D-724: o motor assina com outro nome de pacote (a assinatura de um nunca vale pelo outro), que não é o
    nome da pasta dos projetos; as etiquetas e o nome do arquivo saem de versao.py."""
    assert versao.ID_DO_PACOTE_DO_MOTOR != versao.ID_DO_PACOTE
    local = PureWindowsPath(r"C:\Users\Kaique\AppData\Local")
    assert str(local / versao.ID_DO_PACOTE_DO_MOTOR).casefold() != str(local / historico.pasta_de_dados().name).casefold()
    assert versao.etiqueta_do_motor(1) == "motor-kraken-1" and versao.arquivo_do_motor(1) == "motor-kraken-1.zip"
    assert versao.etiqueta_da_versao("1.2.0") == "v1.2.0"
    assert isinstance(ocr_kraken.VERSAO_DO_MOTOR, int) and ocr_kraken.VERSAO_DO_MOTOR >= 1


def test_o_motor_exigido_diz_o_motor_publicado(tmp_path):
    """O motor-exigido.json (o que a versão pede) tem o nome do pacote do motor, a versão, a etiqueta, o arquivo e a
    soma assinada; a saída sem motor tira de instalar\\ um arquivo de motor que sobrou."""
    motor = empacotar.MotorPublicado(1, versao.arquivo_do_motor(1), "AB" * 32, versao.etiqueta_do_motor(1))
    pasta = tmp_path / "p"
    (pasta / "instalar").mkdir(parents=True)
    (pasta / "instalar" / versao.arquivo_do_motor(1)).write_bytes(b"sobra")
    assert empacotar.preparar_saida(pasta, empacotar.ATUALIZACAO, None, motor) == []
    lido = json.loads((pasta / empacotar.NOME_DO_MOTOR_EXIGIDO).read_text(encoding="utf-8"))
    assert lido == {"formato": 1, "pacote": versao.ID_DO_PACOTE_DO_MOTOR, "versao": 1,
                    "etiqueta": "motor-kraken-1", "arquivo": "motor-kraken-1.zip", "sha256": "ab" * 32}
    assert not (pasta / "instalar" / versao.arquivo_do_motor(1)).exists()
    assert "falta o arquivo do motor" in " ".join(empacotar.preparar_saida(pasta, empacotar.INSTALADOR, None, motor))
