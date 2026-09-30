"""Testes da ponte até o motor do Kraken (core/ocr_kraken.py) e do próprio motor (item 1.3).

DUAS PARTES
    1. Sem o motor (rodam sempre, em segundos): a ponte com um "motor de
       mentira" (um script Python do próprio .venv no lugar do motor) que
       morre, trava, responde lixo, fala outra versão, escreve muito aviso,
       etc. Em todos os casos: aviso em português, nenhuma exceção, nada
       travado. É o teste de "nenhuma exceção derruba o programa".
    2. Com o motor montado (montar_motor_kraken.py): as linhas do motor contra
       as do Kraken do WSL guardadas no 1.3 (saida_teste/ocr-1.3/linhas/K1,
       fora do git). Mesma contagem de linhas e área coberta >= 99% nos dois
       sentidos. Pulados se o motor ou as páginas do 1.3 não estiverem no disco.

       Por padrão rodam 4 páginas (~1 min). As 22 páginas do 1.3 (~4 min)
       rodam com a variável KRAKEN_22=1:
           set KRAKEN_22=1 && .venv\\Scripts\\python.exe -m pytest tests\\test_ocr_kraken.py -s
       Com -s, o tempo de cada página e o de abrir o motor aparecem na tela.

ARRISCADO MUDAR
    AREA_MINIMA (0,99) e a regra "mesma contagem": são o critério pedido pela
    gerente para dizer que o motor do Windows = Kraken do WSL.
"""

from __future__ import annotations

import ast
import json
import os
import sys
import textwrap
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import ocr_kraken
from core.ocr_comum import ResultadoOCR
from core.ocr_kraken import MotorKraken

RAIZ = Path(__file__).resolve().parent.parent
PASTA_13 = RAIZ / "saida_teste" / "ocr-1.3"
IMAGENS_13 = PASTA_13 / "imagens"
LINHAS_WSL = PASTA_13 / "linhas" / "K1"
AREA_MINIMA = 0.99

TODAS_AS_PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]
# As 4 do padrão: a menor (Opus 20, 2 linhas), linhas curvas (Graduale 222),
# a tabela com as 8 linhas que o Kraken joga fora (Opus 256) e uma página
# cheia de texto antigo (Palatino 57).
PAGINAS_PADRAO = ["opusmajus_p020", "graduale_p222", "opusmajus_p256", "palatino_p057"]
PAGINAS = TODAS_AS_PAGINAS if os.environ.get("KRAKEN_22") == "1" else PAGINAS_PADRAO


# =====================================================================
# 1. Sem o motor: a ponte com motores de mentira
# =====================================================================

_MOTOR_DE_MENTIRA = textwrap.dedent('''
    import json, sys, time
    modo = sys.argv[1]
    def mandar(m):
        sys.stdout.write(json.dumps(m) + "\\n"); sys.stdout.flush()
    if modo == "morre_ao_abrir":
        sys.stderr.write("Traceback: faltou uma DLL\\n"); sys.exit(3)
    if modo == "falhou":
        mandar({"tipo": "falhou", "erro": "ImportError: torch"}); sys.exit(1)
    if modo == "nunca_abre":
        time.sleep(60); sys.exit(0)
    versao = 99 if modo == "outra_versao" else 1
    mandar({"tipo": "pronto", "versao_protocolo": versao, "kraken": "de mentira"})
    for linha in sys.stdin:
        pedido = json.loads(linha)
        if pedido.get("comando") == "sair":
            mandar({"id": pedido.get("id"), "ok": True}); break
        if modo == "morre_na_pagina":
            sys.stderr.write("Windows fatal exception: access violation\\n"); sys.stderr.flush()
            sys.exit(5)
        if modo == "trava_na_pagina":
            time.sleep(60)
        if modo == "lixo":
            sys.stdout.write("isto nao e json\\n"); sys.stdout.flush(); continue
        if modo == "formato_errado":
            mandar({"id": pedido["id"], "ok": True, "linhas": [{"poligono": [[1, 2]]}]}); continue
        if modo == "recusa":
            mandar({"id": pedido["id"], "ok": False, "erro": "OSError: imagem ilegivel"}); continue
        if modo == "fala_muito":
            for i in range(20000):
                sys.stderr.write("Polygonizer failed on line 0: aviso longo de teste numero %d\\n" % i)
        # responde "certo": devolve a cor do primeiro ponto na linha de base, para
        # conferir a ordem das cores, e o caminho da imagem
        import numpy as np
        img = np.load(pedido["imagem"])
        cor = [int(v) for v in np.atleast_1d(img[0, 0])]
        mandar({"id": pedido["id"], "ok": True, "largura": int(img.shape[1]), "altura": int(img.shape[0]),
                "segundos": 0.01, "linhas": [{"linha_de_base": [[0, 0], [5, 0]],
                                              "poligono": [[0, 0], [5, 0], [5, 3], [0, 3]]}],
                "falhas_contorno": 2, "linhas_sem_contorno": 0, "regioes": {"text": 1},
                "cor": cor, "arquivo": pedido["imagem"]})
''')


@pytest.fixture
def motor_de_mentira(tmp_path):
    script = tmp_path / "motor_de_mentira.py"
    script.write_text(_MOTOR_DE_MENTIRA, encoding="utf-8")
    abertos = []

    def fabricar(modo: str, **opcoes) -> MotorKraken:
        motor = MotorKraken(comando=[sys.executable, "-X", "utf8", str(script), modo], **opcoes)
        abertos.append(motor)
        return motor

    yield fabricar
    for motor in abertos:
        motor.fechar()


def _pagina(altura=40, largura=30, cor=(10, 20, 30)):
    img = np.zeros((altura, largura, 3), np.uint8)
    img[:] = cor
    return img


def _sem_excecao_e_indisponivel(r: ResultadoOCR, trecho_do_motivo: str):
    assert isinstance(r, ResultadoOCR)
    assert r.motor == "kraken"
    assert not r.disponivel
    assert r.linhas is None
    assert trecho_do_motivo in r.motivo
    assert r.detalhe_tecnico   # o erro técnico existe (vai para o log), separado do aviso


def test_motor_ausente_da_aviso_e_nao_quebra(tmp_path):
    motor = MotorKraken(pasta=tmp_path / "nao_existe")
    inicio = time.perf_counter()
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "não está instalado")
    # a segunda página não tenta de novo (e não demora)
    assert not motor.segmentar(_pagina()).disponivel
    assert time.perf_counter() - inicio < 2
    assert motor.diagnostico() is None
    motor.fechar()


def test_achar_pasta_do_motor_nao_quebra():
    pasta = ocr_kraken.achar_pasta_do_motor()
    assert pasta is None or (pasta / "python" / "python.exe").is_file()
    assert len(ocr_kraken.lugares_do_motor()) >= 2


def test_motor_que_morre_ao_abrir(motor_de_mentira):
    r = motor_de_mentira("morre_ao_abrir").segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "não conseguiu abrir")
    assert "faltou uma DLL" in r.detalhe_tecnico   # a saída de erro do motor vai para o log


def test_motor_que_diz_que_falhou(motor_de_mentira):
    r = motor_de_mentira("falhou").segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "não conseguiu abrir")
    assert "ImportError" in r.detalhe_tecnico


def test_motor_de_outra_versao_e_recusado(motor_de_mentira):
    motor = motor_de_mentira("outra_versao")
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "outra versão")
    assert not motor.aberto


def test_motor_que_nunca_abre_passa_do_tempo(motor_de_mentira):
    motor = motor_de_mentira("nunca_abre", tempo_para_abrir=1.5)
    inicio = time.perf_counter()
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "demorou demais")
    assert time.perf_counter() - inicio < 10
    assert not motor.aberto   # foi fechado à força


def test_motor_que_morre_no_meio_da_pagina(motor_de_mentira):
    motor = motor_de_mentira("morre_na_pagina")
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "parou de funcionar")
    assert "access violation" in r.detalhe_tecnico
    # a próxima página abre um motor novo (e ele morre de novo, sem quebrar nada)
    r2 = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r2, "parou de funcionar")


def test_motor_que_trava_na_pagina_passa_do_tempo(motor_de_mentira):
    motor = motor_de_mentira("trava_na_pagina", tempo_por_pagina=1.0)
    inicio = time.perf_counter()
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "demorou demais")
    assert time.perf_counter() - inicio < 10
    assert not motor.aberto


def test_cancelar_fecha_o_motor(motor_de_mentira):
    motor = motor_de_mentira("trava_na_pagina")
    inicio = time.perf_counter()
    r = motor.segmentar(_pagina(), cancelar=lambda: time.perf_counter() - inicio > 0.5)
    _sem_excecao_e_indisponivel(r, "Cancelado")
    assert time.perf_counter() - inicio < 10
    assert not motor.aberto


def test_cancelar_que_quebra_vira_cancelar(motor_de_mentira):
    def quebra():
        raise RuntimeError("bug de quem chamou")

    r = motor_de_mentira("trava_na_pagina").segmentar(_pagina(), cancelar=quebra)
    _sem_excecao_e_indisponivel(r, "Cancelado")


@pytest.mark.parametrize("modo", ["lixo", "formato_errado"])
def test_resposta_errada(motor_de_mentira, modo):
    r = motor_de_mentira(modo).segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "não entendeu")


def test_motor_que_recusa_a_pagina(motor_de_mentira):
    motor = motor_de_mentira("recusa")
    r = motor.segmentar(_pagina())
    _sem_excecao_e_indisponivel(r, "não conseguiu ler esta página")
    assert "imagem ilegivel" in r.detalhe_tecnico
    assert motor.aberto   # recusar uma página não fecha o motor


def test_imagem_invalida_nao_abre_o_motor(motor_de_mentira):
    motor = motor_de_mentira("certo")
    for ruim in (np.zeros((10, 10), np.float32), np.zeros((0, 5, 3), np.uint8),
                 np.zeros((4, 4, 2), np.uint8), "nao_existe.png", None):
        r = motor.segmentar(ruim)
        assert not r.disponivel and r.motivo
    assert not motor.aberto
    assert not motor.segmentar(_pagina(), ordem="CMYK").disponivel


def test_resposta_certa_e_cores_em_rgb(motor_de_mentira, tmp_path):
    motor = motor_de_mentira("certo")
    r = motor.segmentar(_pagina(cor=(10, 20, 30)))           # BGR, como o programa
    assert r.disponivel and r.motivo is None
    assert len(r.linhas) == 1
    assert r.linhas[0].poligono.shape == (4, 2) and r.linhas[0].poligono.dtype == np.float32
    assert r.linhas[0].linha_de_base.shape == (2, 2)
    assert (r.largura, r.altura) == (30, 40)
    assert r.perdidas == 2 and r.precisa_revisar
    assert r.extra == {"regioes": {"text": 1}, "falhas_contorno": 2, "linhas_sem_contorno": 0}
    assert r.motor == "kraken" and r.palavras is None
    assert r.linhas[0].confianca is None and r.linhas[0].palavras == 0
    # o motor recebeu a página em RGB (a ponte inverte o BGR do programa)
    motor._proximo_id  # noqa: B018 - só para deixar claro que é o mesmo motor
    resposta = motor._pedir({"comando": "segmentar", "imagem": _salvar_npy(tmp_path, _pagina(cor=(1, 2, 3)))},
                            10, None)
    assert resposta["cor"] == [1, 2, 3]   # o motor devolve o que recebeu, sem trocar
    r_rgb = motor.segmentar(_pagina(cor=(10, 20, 30)), ordem="RGB")
    assert r_rgb.disponivel


def test_ponte_inverte_bgr_para_rgb():
    bgr = _pagina(cor=(10, 20, 30))
    assert ocr_kraken._para_rgb(bgr, "BGR")[0, 0].tolist() == [30, 20, 10]
    assert ocr_kraken._para_rgb(bgr, "RGB")[0, 0].tolist() == [10, 20, 30]
    quatro = np.zeros((3, 3, 4), np.uint8)
    quatro[..., 0] = 7
    assert ocr_kraken._para_rgb(quatro, "BGR")[0, 0].tolist() == [0, 0, 7]
    assert ocr_kraken._para_rgb(np.zeros((3, 3), np.uint8), "BGR").shape == (3, 3)


def _salvar_npy(pasta: Path, img: np.ndarray) -> str:
    caminho = pasta / "img.npy"
    np.save(caminho, img)
    return str(caminho)


def test_temporario_da_pagina_e_apagado(motor_de_mentira, tmp_path, monkeypatch):
    monkeypatch.setattr(ocr_kraken.tempfile, "tempdir", str(tmp_path))
    motor = motor_de_mentira("certo")
    r = motor.segmentar(_pagina())
    assert r.disponivel
    assert not list(tmp_path.glob("kraken-pagina-*.npy"))


def test_motor_que_escreve_muito_aviso_nao_trava(motor_de_mentira):
    # 20.000 linhas na saída de erro (~1,5 MB): sem ler a saída de erro em
    # paralelo, o cano enche e os dois processos ficam esperando para sempre.
    motor = motor_de_mentira("fala_muito", tempo_por_pagina=60)
    inicio = time.perf_counter()
    r = motor.segmentar(_pagina())
    assert r.disponivel
    assert time.perf_counter() - inicio < 30


def test_varias_paginas_no_mesmo_motor_e_fechar(motor_de_mentira):
    motor = motor_de_mentira("certo")
    for _ in range(5):
        assert motor.segmentar(_pagina()).disponivel
    processo = motor._processo
    motor.fechar()
    assert processo.poll() is not None      # saiu pelo pedido "sair"
    assert not motor.aberto
    motor.fechar()                          # fechar duas vezes não quebra
    assert motor.segmentar(_pagina()).disponivel   # e dá para abrir de novo


def test_core_nao_importa_ui_nem_qt():
    arvore = ast.parse((RAIZ / "core" / "ocr_kraken.py").read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes |= {a.name for a in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    assert not any(n.split(".")[0] in ("ui", "PySide6", "PyQt5", "PyQt6") for n in nomes), nomes


def test_protocolo_igual_nos_tres_arquivos():
    import montar_motor_kraken

    servidor = (RAIZ / "motor_kraken" / "servidor_kraken.py").read_text(encoding="utf-8")
    assert f"VERSAO_PROTOCOLO = {ocr_kraken.VERSAO_PROTOCOLO}\n" in servidor
    assert montar_motor_kraken.VERSAO_PROTOCOLO == ocr_kraken.VERSAO_PROTOCOLO


def test_arquivo_travado_tem_versao_exata_e_soma_em_todas():
    import montar_motor_kraken as m

    blocos = m._blocos_do_travado(m.ARQUIVO_TRAVADO)
    assert len(blocos) == 73
    for nome, versao, texto in blocos:
        assert versao and "--hash=sha256:" in texto, nome
    nomes = {n.lower() for n, _, _ in blocos}
    assert {"kraken", "torch", "numpy", "scipy", "scikit-image", "pillow"} <= nomes
    assert dict((n.lower(), v) for n, v, _ in blocos)["kraken"] == "7.1.1"


def test_leitor_de_importacoes_de_dll():
    import montar_motor_kraken as m

    # o python.exe do próprio .venv importa pelo menos a DLL do Python
    importadas = [n.lower() for n in m.importacoes_da_dll(Path(sys.executable))]
    assert any(n.startswith("python3") or n == "kernel32.dll" for n in importadas), importadas
    assert m.importacoes_da_dll(RAIZ / "CLAUDE.md") == []


def test_quais_pacotes_servem_ao_motor():
    import montar_motor_kraken as m

    assert m._roda_no_motor("torch-2.14.0-cp312-cp312-win_amd64.whl")
    assert m._roda_no_motor("six-1.17.0-py2.py3-none-any.whl")
    assert m._roda_no_motor("psutil-7.2.2-cp37-abi3-win_amd64.whl")
    assert not m._roda_no_motor("torch-2.14.0-cp313-cp313-win_amd64.whl")
    assert not m._roda_no_motor("numpy-2.4.6-cp312-cp312-manylinux_2_28_x86_64.whl")
    assert not m._roda_no_motor("coremltools-9.0.tar.gz")


# =====================================================================
# 2. Com o motor montado: igual ao Kraken do WSL
# =====================================================================

_PASTA_DO_MOTOR = ocr_kraken.achar_pasta_do_motor()
precisa_do_motor = pytest.mark.skipif(
    _PASTA_DO_MOTOR is None, reason="motor do Kraken não montado (rode montar_motor_kraken.py)")
precisa_das_paginas = pytest.mark.skipif(
    not (IMAGENS_13.is_dir() and LINHAS_WSL.is_dir()),
    reason="páginas e linhas do WSL do 1.3 não estão em saida_teste/ocr-1.3 (fora do git)")

_TEMPOS: dict[str, tuple[float, int, int, float]] = {}   # página: (s, linhas, WSL, área)


@pytest.fixture(scope="module")
def motor_de_verdade():
    motor = MotorKraken()
    inicio = time.perf_counter()
    diag = motor.diagnostico()       # abre o motor
    arranque = time.perf_counter() - inicio
    yield motor, diag, arranque
    motor.fechar()
    if _TEMPOS:
        print(f"\n[motor do Kraken] abrir: {arranque:.1f} s "
              f"(importar {motor.info.get('segundos_importar', 0):.1f} s + modelo "
              f"{motor.info.get('segundos_modelo', 0):.1f} s); por página:")
        for pagina, (segundos, linhas, wsl, area) in _TEMPOS.items():
            print(f"    {pagina:16s} {segundos:6.1f} s   {linhas:4d} linhas (WSL {wsl:4d})   "
                  f"área em comum {100 * area:6.2f}%")
        valores = sorted(v[0] for v in _TEMPOS.values())
        print(f"    mediana {valores[len(valores) // 2]:.1f} s em {len(valores)} página(s)")


def _mascara(poligonos, largura: int, altura: int) -> np.ndarray:
    mascara = np.zeros((altura, largura), np.uint8)
    for p in poligonos:
        pontos = np.round(np.asarray(p, np.float64)).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(mascara, [pontos], 1)
    return mascara.astype(bool)


@precisa_do_motor
def test_motor_de_verdade_abre_e_usa_o_visual_c_certo(motor_de_verdade):
    """O Visual C++ vem do motor (motor antigo, até 29/09) ou do Windows\\System32
    (o normal desde 29/09: o instalador roda o vc_redist oficial). De nenhum outro lugar."""
    import montar_motor_kraken

    motor, diag, arranque = motor_de_verdade
    assert diag is not None, "o motor montado não abriu"
    assert motor.info.get("kraken") == "7.1.1"
    assert motor.info.get("python", "").startswith("3.12.")
    dlls = diag["dlls_da_microsoft"]
    assert any("msvcp140.dll" in d.lower() for d in dlls), dlls
    assert montar_motor_kraken.dlls_de_lugar_errado(dlls, _PASTA_DO_MOTOR) == [], dlls


def test_tirar_dlls_do_python_so_tira_as_do_visual_c(tmp_path):
    import montar_motor_kraken as m

    for nome in ("python.exe", "python312.dll", "vcruntime140.dll", "vcruntime140_1.dll", "libffi-8.dll"):
        (tmp_path / nome).write_bytes(b"x")
    assert m.tirar_dlls_do_python(tmp_path) == ["vcruntime140.dll", "vcruntime140_1.dll"]
    assert sorted(f.name for f in tmp_path.iterdir()) == ["libffi-8.dll", "python.exe", "python312.dll"]
    assert all(m._PADRAO_DLL_DA_MICROSOFT.match(n) for n in m.DLLS_DO_VISUAL_C)


def test_dll_de_lugar_errado(tmp_path):
    import os
    import montar_motor_kraken as m

    sistema = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
    motor = tmp_path / "motor"
    assert m.dlls_de_lugar_errado([str(sistema / "msvcp140.dll"),
                                   str(motor / "python" / "vcomp140.dll")], motor) == []
    outro = str(tmp_path / "OutroPrograma" / "msvcp140.dll")
    assert m.dlls_de_lugar_errado([outro], motor) == [outro]


@precisa_do_motor
@precisa_das_paginas
@pytest.mark.parametrize("pagina", PAGINAS)
def test_mesmas_linhas_do_kraken_do_wsl(motor_de_verdade, pagina):
    motor, _, _ = motor_de_verdade
    referencia = json.loads((LINHAS_WSL / f"{pagina}.json").read_text(encoding="utf-8"))["linhas"]
    r = motor.segmentar(IMAGENS_13 / f"{pagina}.png")
    assert r.disponivel, (r.motivo, r.detalhe_tecnico)
    novo = _mascara([l.poligono for l in r.linhas], r.largura, r.altura)
    wsl = _mascara([l["poligono"] for l in referencia], r.largura, r.altura)
    comum = np.count_nonzero(novo & wsl)
    area = min(comum / max(1, np.count_nonzero(wsl)), comum / max(1, np.count_nonzero(novo)))
    _TEMPOS[pagina] = (r.segundos, len(r.linhas), len(referencia), area)
    assert len(r.linhas) == len(referencia), f"{pagina}: {len(r.linhas)} linhas, WSL {len(referencia)}"
    assert comum / max(1, np.count_nonzero(wsl)) >= AREA_MINIMA, pagina
    assert comum / max(1, np.count_nonzero(novo)) >= AREA_MINIMA, pagina
    if pagina == "opusmajus_p256":
        # a tabela: o Kraken perde 8 linhas em silêncio ("Polygonizer failed")
        assert r.extra["falhas_contorno"] == 8
        assert r.perdidas >= 8 and r.precisa_revisar
    elif pagina in ("opusmajus_p020", "graduale_p222", "palatino_p057"):
        assert r.extra["falhas_contorno"] == 0 and not r.precisa_revisar


@precisa_do_motor
@precisa_das_paginas
def test_pagina_em_memoria_bgr_da_o_mesmo_que_o_arquivo(motor_de_verdade):
    motor, _, _ = motor_de_verdade
    pagina = IMAGENS_13 / "opusmajus_p020.png"
    pelo_arquivo = motor.segmentar(pagina)
    bgr = cv2.imdecode(np.fromfile(str(pagina), np.uint8), cv2.IMREAD_COLOR)
    pela_memoria = motor.segmentar(bgr)            # BGR, como o programa usa
    assert pelo_arquivo.disponivel and pela_memoria.disponivel
    assert len(pelo_arquivo.linhas) == len(pela_memoria.linhas)
    for a, b in zip(pelo_arquivo.linhas, pela_memoria.linhas):
        assert np.array_equal(a.poligono, b.poligono)
        assert np.array_equal(a.linha_de_base, b.linha_de_base)


def test_caminho_relativo_vai_absoluto_para_o_motor(motor_de_mentira, tmp_path, monkeypatch):
    """O motor roda com a pasta dele como pasta atual: um caminho relativo
    apontaria para dentro do motor (achado em 29/09)."""
    arquivo = tmp_path / "pagina.png"
    arquivo.write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    motor = motor_de_mentira("certo")
    pedidos = []

    def pedir(pedido, tempo, cancelar):
        pedidos.append(pedido)
        return {"ok": False, "erro": "so para o teste"}

    motor._abrir = lambda: None
    motor._pedir = pedir
    motor.segmentar("pagina.png")
    assert pedidos and Path(pedidos[0]["imagem"]).is_absolute()
    assert Path(pedidos[0]["imagem"]) == arquivo.resolve()
