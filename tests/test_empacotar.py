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
    from core import detectar_regioes, ocr_doctr, rede_selecao

    origens = {origem for origem, _ in empacotar.modelos_do_programa()}

    assert origens == {detectar_regioes.CAMINHO_MODELO,
                       rede_selecao.CODIFICADOR, rede_selecao.DECODIFICADOR,
                       ocr_doctr.CAMINHO_MODELO}


def test_cada_modelo_vai_para_onde_o_codigo_empacotado_procura():
    """O codigo procura em <pasta acima de core>/modelos/... Empacotado, core/
    mora em _internal/ (ou na raiz do _MEIxxxx, no arquivo unico): o
    '--add-data origem;destino' tem de reproduzir o mesmo caminho relativo."""
    from core import detectar_regioes

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    destinos = {origem.relative_to(raiz_do_codigo).parent.as_posix(): destino
                for origem, destino in empacotar.modelos_do_programa()}

    assert destinos == {"modelos": "modelos", "modelos/mobile_sam": "modelos/mobile_sam",
                        "modelos/doctr": "modelos/doctr"}


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
    monkeypatch.setattr(empacotar, "_avisar_pecas_faltando", lambda motor=None: object())

    assert empacotar.main(["--modo", "entrega"]) == 0

    entregue = area / empacotar.PASTA_DE_ENTREGA / "EditorImpressao-Setup.exe"
    assert entregue.read_bytes() == b"instalador novo"
    for gerado in empacotar.gerados_em_dist(raiz):
        assert not gerado.exists(), f"{gerado.name} ficou em dist"
    _confere_intactos(raiz, protegidos)


# ---------------------------------------------------------------------------
# os detectores de texto (item 1.3, 29/09/2026): motor do Kraken, Tesseract,
# Visual C++ oficial. A mesma trava dos modelos: faltou peca, para.
# ---------------------------------------------------------------------------

BARRA = "\\"


def _motor_falso(pasta: Path, *, velho: bool = False, com_bin: bool = False,
                 protocolo: int | None = None) -> Path:
    from core import ocr_kraken

    kraken = pasta / "python" / "Lib" / "site-packages" / "kraken"
    kraken.mkdir(parents=True)
    (pasta / "python" / "python.exe").write_bytes(b"x")
    (kraken / "blla.mlmodel").write_bytes(b"modelo")
    versao = ocr_kraken.VERSAO_PROTOCOLO if protocolo is None else protocolo
    (pasta / "servidor_kraken.py").write_text(f"VERSAO_PROTOCOLO = {versao}\n", encoding="utf-8")
    if velho:
        (pasta / "python" / "msvcp140.dll").write_bytes(b"x")
    if com_bin:
        (kraken.parent / "bin").mkdir()
    return pasta


def test_motor_do_jeito_novo_passa(tmp_path):
    assert empacotar.conferir_motor_kraken(_motor_falso(tmp_path / "m")) == []


@pytest.mark.parametrize("defeito, trecho", [
    ({"velho": True}, "jeito velho, com o Visual C++"),
    ({"com_bin": True}, "atalhos"),
    ({"protocolo": 99}, "outra versão"),
])
def test_motor_com_defeito_e_recusado(tmp_path, defeito, trecho):
    problemas = empacotar.conferir_motor_kraken(_motor_falso(tmp_path / "m", **defeito))
    assert any(trecho in p for p in problemas), problemas


def test_pasta_sem_motor_e_recusada(tmp_path):
    assert "não há motor montado" in empacotar.conferir_motor_kraken(tmp_path)[0]


def test_achar_motor_pula_o_velho_e_fica_com_o_novo(tmp_path, monkeypatch):
    velho = _motor_falso(tmp_path / "velho", velho=True)
    novo = _motor_falso(tmp_path / "novo")
    monkeypatch.setattr(empacotar, "LUGARES_DO_MOTOR", [tmp_path / "nao_existe", velho, novo])
    assert empacotar.achar_motor_kraken() == (novo.resolve(), [])
    so_velho, problemas = empacotar.achar_motor_kraken(velho)
    assert so_velho is None and any("jeito velho" in p for p in problemas)


def test_pecas_faltando_param_antes_do_pyinstaller(tmp_path, monkeypatch, capsys):
    """Sem o motor do Kraken, o Tesseract ou o Visual C++, o empacotamento
    para ANTES de rodar o PyInstaller, dizendo o que falta."""
    monkeypatch.setattr(empacotar, "_avisar_modelos_faltando", lambda: True)
    monkeypatch.setattr(empacotar, "LUGARES_DO_MOTOR", [tmp_path / "nao_existe"])
    monkeypatch.setattr(empacotar, "achar_pasta_do_tesseract", lambda: None)
    monkeypatch.setattr(empacotar, "preparar_vc_redist",
                        lambda baixar=True: (None, "", ["falta o vc_redist (teste)"]))
    rodou: list = []
    monkeypatch.setattr(empacotar.subprocess, "run", lambda *a, **k: rodou.append(a))

    assert empacotar.construir_pasta() is None
    assert rodou == [], "nao pode chegar a rodar o PyInstaller"
    saida = capsys.readouterr().out
    assert "PAREI" in saida and "motor do Kraken" in saida and "Tesseract" in saida
    assert "falta o vc_redist (teste)" in saida
    assert empacotar.main(["--modo", "pasta"]) == 1
    assert rodou == []


def _assinatura(**trocas):
    boa = {"status": "Valid",
           "assinante": "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
           "produto": "Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211",
           "versao": "14.44.35211.0"}
    boa.update(trocas)
    return boa


def test_vc_redist_oficial_confere():
    assert empacotar.vc_redist_confere(_assinatura()) == []


@pytest.mark.parametrize("trocas, trecho", [
    ({"status": "HashMismatch"}, "assinatura digital não confere"),
    ({"status": "NotSigned", "assinante": ""}, "não foi assinado pela Microsoft"),
    ({"assinante": "CN=Microsoft Corporation Falsa, O=Outra"}, "não foi assinado pela Microsoft"),
    ({"produto": "Microsoft Visual C++ 2015-2022 Redistributable (x86)"}, "não é o Visual C++"),
    ({"versao": "12.0.1"}, "versão inesperada"),
])
def test_vc_redist_que_nao_confere(trocas, trecho):
    assert any(trecho in p for p in empacotar.vc_redist_confere(_assinatura(**trocas)))


def test_assinatura_de_um_arquivo_sem_assinatura(tmp_path):
    """O leitor da assinatura (PowerShell) roda de verdade: um arquivo
    qualquer nao e o vc_redist oficial."""
    falso = tmp_path / "vc_redist.x64.exe"
    falso.write_bytes(b"MZ nao sou da Microsoft")
    assert empacotar.vc_redist_confere(empacotar.assinatura_do_arquivo(falso))


def test_registro_do_inno_tem_de_listar_cada_peca(tmp_path):
    pecas = empacotar.PecasDosDetectores(tmp_path / "motor", tmp_path / "tess", tmp_path / "tess" / "doc",
                                         tmp_path / "tessdata", tmp_path / "vc_redist.x64.exe", "14.44")
    esperadas = empacotar.pecas_esperadas_no_instalador(pecas)
    b = BARRA
    for caminho in (f"tesseract{b}tesseract.exe", f"tesseract{b}tessdata{b}script{b}Fraktur.traineddata",
                    f"tesseract{b}LICENSE", f"build{b}vc_redist.x64.exe", f"motor-kraken{b}python{b}python.exe"):
        assert caminho in esperadas, caminho
    registro = "".join(f"   Compressing: D:{b}x{b}dist{b}EditorImpressao{b}{r}\n" for r in esperadas)
    assert empacotar.pecas_faltando_no_registro_do_inno(registro, pecas) == []
    lat = f"tesseract{b}tessdata{b}lat.traineddata"
    sem_um = registro.replace(lat, f"outra{b}coisa")
    assert empacotar.pecas_faltando_no_registro_do_inno(sem_um, pecas) == [lat]


def test_registro_do_inno_com_versao_no_fim_da_linha(tmp_path):
    """O Inno escreve a versao no fim da linha de um .exe versionado sem
    ignoreversion (o vc_redist). Achado em 29/09: sem isto, a trava apagava
    o instalador bom."""
    b = BARRA
    pecas = empacotar.PecasDosDetectores(tmp_path / "motor", tmp_path / "tess", tmp_path / "tess" / "doc",
                                         tmp_path / "tessdata", tmp_path / "vc_redist.x64.exe", "14.44")
    linha = f"   Compressing: D:{b}x{b}build{b}vc_redist.x64.exe   (14.44.35211.0)"
    comprimidos = empacotar._comprimidos(linha)
    assert len(comprimidos) == 1 and comprimidos[0].endswith(f"d:{b}x{b}build{b}vc_redist.x64.exe")
    faltando = empacotar.pecas_faltando_no_registro_do_inno(linha, pecas)
    assert f"build{b}vc_redist.x64.exe" not in faltando


def test_o_script_do_inno_recusa_pasta_sem_as_pecas():
    """Quem compilar o instalador.iss na mao tambem nao gera instalador sem
    os detectores de texto, e o Visual C++ so roda se faltar."""
    from core import ocr_tesseract

    b = BARRA
    script = (empacotar.RAIZ / "instalador.iss").read_text(encoding="utf-8")
    for trecho in (f"motor-kraken{b}python{b}python.exe", f"motor-kraken{b}servidor_kraken.py",
                   f"tesseract{b}tesseract.exe", f"tesseract{b}LICENSE", f"build{b}vc_redist.x64.exe",
                   f"SOFTWARE{b}Microsoft{b}VisualStudio{b}14.0{b}VC{b}Runtimes{b}x64",
                   "/install /quiet /norestart", "HKLM64", "HKLM32", "1638", "3010"):
        assert trecho in script, trecho
    for idioma in ocr_tesseract.IDIOMAS_DO_INSTALADOR:
        assert f'Idioma("{idioma.replace("/", b)}")' in script, idioma


def test_os_27_arquivos_sao_os_que_o_tesseract_carrega():
    """A lista fixa ARQUIVOS_DO_TESSERACT = o tesseract.exe e as DLLs da pasta
    dele que ele (e elas) importam, lidas da tabela de importacao."""
    import montar_motor_kraken as m

    pasta = empacotar.achar_pasta_do_tesseract()
    if pasta is None:
        pytest.skip("Tesseract não instalado")
    locais = {f.name.lower(): f for f in pasta.iterdir() if f.is_file()}
    vistos, fila = set(), ["tesseract.exe"]
    while fila:
        nome = fila.pop().lower()
        if nome in vistos or nome not in locais:
            continue
        vistos.add(nome)
        fila.extend(m.importacoes_da_dll(locais[nome]))
    assert vistos == {n.lower() for n in empacotar.ARQUIVOS_DO_TESSERACT}



# ---------------------------------------------------------------------------
# o detector de gravura do ScanTailor (item 1.2, 29/09/2026): a DLL
# core/nativo/st_gravura.dll vai junto, com a mesma trava dos modelos
# ---------------------------------------------------------------------------

def test_a_dll_da_gravura_vai_para_onde_o_codigo_procura():
    """core/gravura_scantailor.CAMINHO_DLL = <raiz do codigo>/core/nativo/:
    empacotado, a raiz do codigo e _internal/, entao o destino e core/nativo."""
    from core import gravura_scantailor

    nativos = dict(empacotar.nativos_do_programa())
    assert set(nativos) == {gravura_scantailor.CAMINHO_DLL,
                            gravura_scantailor.CAMINHO_DLL.with_suffix(".txt")}
    assert set(nativos.values()) == {"core/nativo"}


@pytest.mark.parametrize("onefile", [False, True])
def test_o_comando_do_pyinstaller_leva_a_dll_da_gravura(onefile):
    comando = empacotar.comando_do_pyinstaller(onefile)
    dados = _valor_de(comando, "--add-data")
    for origem, destino in empacotar.nativos_do_programa():
        assert f"{origem}{SEPARADOR}{destino}" in dados
    assert "core.gravura_scantailor" in _valor_de(comando, "--hidden-import")


def test_dll_da_gravura_existe_para_empacotar():
    assert empacotar.nativos_faltando() == []


def test_dll_da_gravura_faltando_para_antes_do_pyinstaller(tmp_path, monkeypatch, capsys):
    sumida = tmp_path / "core" / "nativo" / "st_gravura.dll"
    monkeypatch.setattr(empacotar, "nativos_do_programa", lambda: [(sumida, "core/nativo")])
    monkeypatch.setattr(empacotar, "modelos_faltando", lambda: [])
    rodou: list = []
    monkeypatch.setattr(empacotar.subprocess, "run", lambda *a, **k: rodou.append(a))

    assert empacotar.construir_pasta() is None
    assert empacotar.construir_arquivo_unico() is None
    assert rodou == [], "nao pode chegar a rodar o PyInstaller"
    saida = capsys.readouterr().out
    assert str(sumida) in saida and "compilar_detector_gravura.py" in saida


def test_conferir_no_pacote_pega_dll_ausente_ou_pela_metade(tmp_path, monkeypatch):
    origem = tmp_path / "origem"
    origem.mkdir()
    dll = origem / "st_gravura.dll"
    dll.write_bytes(b"0123456789")
    txt = origem / "st_gravura.txt"
    txt.write_bytes(b"origem")
    monkeypatch.setattr(empacotar, "nativos_do_programa",
                        lambda: [(dll, "core/nativo"), (txt, "core/nativo")])
    pasta = tmp_path / "EditorImpressao"
    (pasta / "_internal" / "core" / "nativo").mkdir(parents=True)

    assert len(empacotar.conferir_nativos_no_pacote(pasta)) == 2
    (pasta / "_internal" / "core" / "nativo" / "st_gravura.dll").write_bytes(b"01234")
    (pasta / "_internal" / "core" / "nativo" / "st_gravura.txt").write_bytes(b"origem")
    problemas = empacotar.conferir_nativos_no_pacote(pasta)
    assert len(problemas) == 1 and "pela metade" in problemas[0]
    (pasta / "_internal" / "core" / "nativo" / "st_gravura.dll").write_bytes(b"0123456789")
    assert empacotar.conferir_nativos_no_pacote(pasta) == []


def test_registro_do_inno_tem_de_listar_a_dll_da_gravura():
    b = BARRA
    registro = "".join(
        f"   Compressing: D:{b}x{b}dist{b}EditorImpressao{b}_internal{b}core{b}nativo{b}{n}\n"
        for n in ("st_gravura.dll", "st_gravura.txt"))
    assert empacotar.nativos_faltando_no_registro_do_inno(registro) == []
    so_o_txt = registro.splitlines()[1]
    assert empacotar.nativos_faltando_no_registro_do_inno(so_o_txt) == [
        f"_internal{b}core{b}nativo{b}st_gravura.dll"]


def test_o_script_do_inno_recusa_pasta_sem_a_dll_da_gravura():
    b = BARRA
    script = (empacotar.RAIZ / "instalador.iss").read_text(encoding="utf-8")
    for origem, destino in empacotar.nativos_do_programa():
        caminho = f"_internal{b}{destino.replace('/', b)}{b}{origem.name}"
        assert f'FileExists(PastaDoPrograma + "{caminho}")' in script, caminho
