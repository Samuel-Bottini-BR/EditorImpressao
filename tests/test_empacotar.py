"""Empacotamento do programa de verdade (empacotar.py): os modelos vao junto.

Bug de 25/09/2026 (Lista de bugs do plano): o instalador saia SEM os modelos
- o detector de gravura e letra (modelos/doclayout.onnx) e a selecao por
clique (modelos/mobile_sam/) -, que ficam fora do git. O programa instalado
rodava sem os dois e sem avisar nada.

O PyInstaller em si nao roda aqui (leva minutos); o proprio empacotar.py
confere o pacote que gera (conferir_modelos_no_pacote e
modelos_faltando_no_registro_do_inno). Aqui fica o que tem resposta certa:

- a lista de modelos e EXATAMENTE a dos caminhos em que o codigo os procura;
- cada um vai para a pasta do pacote em que o codigo empacotado o procura;
- so vai o que o codigo usa (nada do .zip, do script de referencia, do
  config.yaml);
- faltando um modelo, o empacotamento para ANTES de rodar o PyInstaller, com
  mensagem que diz qual e onde;
- as conferencias depois de empacotar pegam modelo ausente ou pela metade.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import empacotar

SEPARADOR = ";" if sys.platform == "win32" else ":"


def _valor_de(comando: list[str], opcao: str) -> list[str]:
    return [comando[i + 1] for i, item in enumerate(comando) if item == opcao]


def test_a_lista_de_modelos_e_a_que_o_codigo_procura():
    """Os caminhos vem do proprio codigo: se alguem mudar onde o core procura
    um modelo, o empacotamento acompanha sozinho."""
    from core import detectar_regioes, rede_selecao

    origens = {origem for origem, _ in empacotar.modelos_do_programa()}

    assert origens == {detectar_regioes.CAMINHO_MODELO,
                       rede_selecao.CODIFICADOR, rede_selecao.DECODIFICADOR}


def test_cada_modelo_vai_para_onde_o_codigo_empacotado_procura():
    """O codigo procura em <pasta acima de core>/modelos/... Empacotado, core/
    mora em _internal/ (ou na raiz do _MEIxxxx, no arquivo unico): o
    '--add-data origem;destino' tem de reproduzir o mesmo caminho relativo."""
    from core import detectar_regioes

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    destinos = {origem.relative_to(raiz_do_codigo).parent.as_posix(): destino
                for origem, destino in empacotar.modelos_do_programa()}

    assert destinos == {"modelos": "modelos", "modelos/mobile_sam": "modelos/mobile_sam"}


@pytest.mark.parametrize("onefile", [False, True])
def test_o_comando_do_pyinstaller_leva_cada_modelo(onefile):
    dados = _valor_de(empacotar.comando_do_pyinstaller(onefile), "--add-data")

    for origem, destino in empacotar.modelos_do_programa():
        assert f"{origem}{SEPARADOR}{destino}" in dados


def test_so_vai_o_que_o_codigo_usa():
    """Nem o .zip do mobile_sam (36 MB repetidos), nem o script de referencia,
    nem o config.yaml, nem a pasta modelos/ inteira."""
    dados = _valor_de(empacotar.comando_do_pyinstaller(False), "--add-data")
    origens = [d.rsplit(SEPARADOR, 1)[0] for d in dados]

    assert all(Path(o).suffix == ".onnx" for o in origens if "modelos" in o)
    assert not any(o.endswith(("mobile_sam.zip", ".py", "config.yaml")) for o in origens)
    assert str(empacotar.RAIZ / "modelos") not in origens


def test_modelo_faltando_para_antes_do_pyinstaller(tmp_path, monkeypatch, capsys):
    """Sem o modelo o instalador sai incompleto e ninguem percebe: o programa
    so deixa de achar gravura e letra. Melhor parar, dizendo qual falta."""
    sumido = tmp_path / "modelos" / "doclayout.onnx"
    monkeypatch.setattr(empacotar, "modelos_do_programa",
                        lambda: [(sumido, "modelos")])
    rodou: list = []
    monkeypatch.setattr(empacotar.subprocess, "run",
                        lambda *a, **k: rodou.append(a))

    assert empacotar.construir_pasta() is None
    assert rodou == [], "nao pode chegar a rodar o PyInstaller"
    saida = capsys.readouterr().out
    assert str(sumido) in saida and "doclayout.onnx" in saida


def test_modelos_faltando_lista_so_os_ausentes(tmp_path, monkeypatch):
    presente = tmp_path / "a.onnx"
    presente.write_bytes(b"x")
    ausente = tmp_path / "b.onnx"
    monkeypatch.setattr(empacotar, "modelos_do_programa",
                        lambda: [(presente, "modelos"), (ausente, "modelos")])

    assert empacotar.modelos_faltando() == [ausente]


def test_conferir_no_pacote_pega_modelo_ausente_ou_pela_metade(tmp_path, monkeypatch):
    origem = tmp_path / "origem"
    (origem / "mobile_sam").mkdir(parents=True)
    inteiro = origem / "doclayout.onnx"
    inteiro.write_bytes(b"0123456789")
    cortado = origem / "mobile_sam" / "enc.onnx"
    cortado.write_bytes(b"0123456789")
    sumido = origem / "mobile_sam" / "dec.onnx"
    sumido.write_bytes(b"0123456789")
    monkeypatch.setattr(empacotar, "modelos_do_programa", lambda: [
        (inteiro, "modelos"), (cortado, "modelos/mobile_sam"),
        (sumido, "modelos/mobile_sam")])

    pasta = tmp_path / "EditorImpressao"
    (pasta / "_internal" / "modelos" / "mobile_sam").mkdir(parents=True)
    (pasta / "_internal" / "modelos" / "doclayout.onnx").write_bytes(b"0123456789")
    (pasta / "_internal" / "modelos" / "mobile_sam" / "enc.onnx").write_bytes(b"01234")

    problemas = empacotar.conferir_modelos_no_pacote(pasta)

    assert len(problemas) == 2
    assert any("enc.onnx" in p for p in problemas)
    assert any("dec.onnx" in p for p in problemas)
    assert not any("doclayout" in p for p in problemas)


def test_registro_do_inno_tem_de_listar_cada_modelo(monkeypatch, tmp_path):
    """O ISCC escreve uma linha 'Compressing:' por arquivo que entra no
    instalador. E a prova de que o modelo esta DENTRO do Setup.exe."""
    monkeypatch.setattr(empacotar, "modelos_do_programa", lambda: [
        (tmp_path / "doclayout.onnx", "modelos"),
        (tmp_path / "mobile_sam.encoder.onnx", "modelos/mobile_sam")])
    registro_completo = (
        "   Compressing: D:\\x\\dist\\EditorImpressao\\_internal\\modelos\\doclayout.onnx\n"
        "   Compressing: D:\\x\\dist\\EditorImpressao\\_internal\\modelos\\mobile_sam\\"
        "mobile_sam.encoder.onnx\n")
    registro_sem_um = registro_completo.splitlines()[0]

    assert empacotar.modelos_faltando_no_registro_do_inno(registro_completo) == []
    assert empacotar.modelos_faltando_no_registro_do_inno(registro_sem_um) == [
        "_internal\\modelos\\mobile_sam\\mobile_sam.encoder.onnx"]


def test_o_script_do_inno_recusa_pasta_sem_os_modelos():
    """Quem compilar o instalador.iss na mao, sem passar pelo empacotar.py,
    tambem nao pode gerar instalador sem os modelos: o proprio script para
    (#error) se algum faltar em dist\\EditorImpressao\\_internal\\."""
    script = (empacotar.RAIZ / "instalador.iss").read_text(encoding="utf-8")

    for origem, destino in empacotar.modelos_do_programa():
        caminho = f"_internal\\{destino.replace('/', chr(92))}\\{origem.name}"
        assert caminho in script, f"instalador.iss nao confere {caminho}"
    assert "#error" in script


# ---------------------------------------------------------------------------
# a limpeza: o empacotar.py so apaga o que ele mesmo gera (bug de 28/09/2026)
# ---------------------------------------------------------------------------
#
# O modo entrega apagava a pasta dist\ INTEIRA, no comeco e no fim. Em dist\
# mora tambem o teste de velocidade do notebook do Kaique (gerado pelo
# empacotar_teste_velocidade.py): a pasta TesteVelocidade\, o .txt com o passo
# a passo e o .zip da Fase 0, que nao pode ser apagado nem refeito (Registro de
# mudancas, 28/09). Tudo aqui roda numa pasta temporaria, nunca no dist\ real.

NOME_DO_ZIP = "TesteVelocidade-notebook-do-Kaique.zip"
NOME_DO_TXT = "COMO RODAR NO NOTEBOOK DO KAIQUE.txt"


def _dist_com_o_teste_do_kaique(raiz: Path) -> dict[str, bytes]:
    """Monta raiz/dist/ como o de verdade: o que o empacotar.py gera e o
    que o empacotar_teste_velocidade.py gera (o .zip somente leitura, como o
    real). Devolve {caminho relativo: conteudo} do que NAO pode sumir."""
    import os
    import stat

    dist = raiz / "dist"
    (dist / "EditorImpressao" / "_internal").mkdir(parents=True)
    (dist / "EditorImpressao" / "EditorImpressao.exe").write_bytes(b"programa")
    (dist / "EditorImpressao.exe").write_bytes(b"arquivo unico")
    (dist / "EditorImpressao-Setup.exe").write_bytes(b"instalador")

    (dist / "TesteVelocidade" / "_internal").mkdir(parents=True)
    protegidos = {
        f"dist/{NOME_DO_ZIP}": b"zip da fase 0",
        f"dist/{NOME_DO_TXT}": b"passo a passo",
        "dist/TesteVelocidade/TesteVelocidade.exe": b"teste",
        "dist/TesteVelocidade/_internal/base_library.zip": b"python",
        "dist/outra coisa qualquer.txt": b"nao e deste script",
    }
    for relativo, conteudo in protegidos.items():
        (raiz / relativo).write_bytes(conteudo)
    os.chmod(dist / NOME_DO_ZIP, stat.S_IREAD)
    return protegidos


def _confere_intactos(raiz: Path, protegidos: dict[str, bytes]) -> None:
    import os

    for relativo, conteudo in protegidos.items():
        caminho = raiz / relativo
        assert caminho.is_file(), f"{relativo} sumiu"
        assert caminho.read_bytes() == conteudo, f"{relativo} mudou"
    assert not os.access(raiz / "dist" / NOME_DO_ZIP, os.W_OK), (
        "o .zip da Fase 0 deixou de ser somente leitura")


def _devolver_escrita(raiz: Path) -> None:
    """Tira o somente leitura do .zip falso: o pytest precisa apagar a pasta
    temporaria depois."""
    import os
    import stat

    for zip_ in raiz.rglob(NOME_DO_ZIP):
        os.chmod(zip_, stat.S_IWRITE | stat.S_IREAD)


@pytest.fixture
def raiz_temporaria(tmp_path):
    """tmp_path, com o somente leitura desfeito no fim, passe o teste ou nao."""
    yield tmp_path
    _devolver_escrita(tmp_path)


def test_limpeza_apaga_so_o_que_o_script_gera(raiz_temporaria):
    raiz = raiz_temporaria
    protegidos = _dist_com_o_teste_do_kaique(raiz)
    (raiz / "build" / "pasta").mkdir(parents=True)

    sobrou = empacotar.apagar_o_que_gerou(raiz)

    assert sobrou == []
    for gerado in empacotar.gerados_em_dist(raiz):
        assert not gerado.exists(), f"{gerado.name} ficou"
    assert not (raiz / "build").exists()
    _confere_intactos(raiz, protegidos)


def test_dist_so_com_o_que_o_script_gera_some_inteira(tmp_path):
    """Sem nada de outro script, a pasta dist/ vazia vai embora, como antes."""
    dist = tmp_path / "dist"
    (dist / "EditorImpressao").mkdir(parents=True)
    (dist / "EditorImpressao-Setup.exe").write_bytes(b"instalador")

    assert empacotar.apagar_o_que_gerou(tmp_path) == []
    assert not dist.exists()


def test_os_gerados_sao_os_tres_que_o_script_produz(tmp_path):
    """Pasta, arquivo unico e instalador - nada mais. Se o script passar a
    gerar outra coisa em dist/, ela entra aqui; o resto de dist/ e de
    outros scripts."""
    nomes = {c.name for c in empacotar.gerados_em_dist(tmp_path)}

    assert nomes == {"EditorImpressao", "EditorImpressao.exe", "EditorImpressao-Setup.exe"}
    assert all(c.parent == tmp_path / "dist" for c in empacotar.gerados_em_dist(tmp_path))


def test_modo_entrega_nao_apaga_o_teste_do_kaique(raiz_temporaria, monkeypatch):
    """O caminho inteiro do modo entrega (main --modo entrega), numa copia:
    o PyInstaller e o Inno Setup sao trocados por um falso que so escreve os
    arquivos que eles escreveriam, e a Area de Trabalho e uma pasta
    temporaria. O instalador chega na 'Area de Trabalho', o que o script
    gerou sai de dist/, e o teste do Kaique fica intacto."""
    raiz = raiz_temporaria / "projeto"
    protegidos = _dist_com_o_teste_do_kaique(raiz)
    area = raiz_temporaria / "Desktop"
    area.mkdir()

    def instalador_falso():
        dist = raiz / "dist"
        (dist / "EditorImpressao").mkdir(parents=True, exist_ok=True)
        (dist / "EditorImpressao-Setup.exe").write_bytes(b"instalador novo")
        return dist / "EditorImpressao-Setup.exe"

    monkeypatch.setattr(empacotar, "RAIZ", raiz)
    monkeypatch.setattr(empacotar, "AREA_DE_TRABALHO", area)
    monkeypatch.setattr(empacotar, "construir_instalador", instalador_falso)
    monkeypatch.setattr(empacotar, "_avisar_modelos_faltando", lambda: True)

    assert empacotar.main(["--modo", "entrega"]) == 0

    entregue = area / empacotar.PASTA_DE_ENTREGA / "EditorImpressao-Setup.exe"
    assert entregue.read_bytes() == b"instalador novo"
    for gerado in empacotar.gerados_em_dist(raiz):
        assert not gerado.exists(), f"{gerado.name} ficou em dist"
    _confere_intactos(raiz, protegidos)
