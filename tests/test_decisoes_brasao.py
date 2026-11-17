"""Provas das decisoes do brasao (D-744 a D-747, Samuel, 17/11/2026).

- D-744: "pode fazer um motion dela girando em 3d sem mudar nada no brasão,
  tem que continuar exactamente igual só com o movimento enquanto carrega o
  programa e pode mudar o icone do programa também para esse brasão."
- D-745: "A" (a volta inteira, como uma moeda girando) e "dá para ser sem
  fundo?": de costas aparece de frente outra vez, sem espelhar; sem fundo e
  sem quadro.
- D-746: o icone e o brasao inteiro em todos os tamanhos (16 a 256),
  desenhado direto do vetor em cada tamanho, nunca uma imagem diminuida.
- D-747: "brasão aprovado" - igual a pagina de exemplo (uma volta a cada
  2,5 s, perspectiva de 900 px, 200 px de largura).

Tudo fora da tela (offscreen): nenhum teste mostra o brasao na tela do Samuel.
Os processos do brasao abertos aqui herdam o QT_QPA_PLATFORM=offscreen do
tests/conftest.py.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("fitz")

from PySide6.QtCore import QPointF, Qt  # noqa: E402
from PySide6.QtGui import QIcon, QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import brasao  # noqa: E402
import empacotar  # noqa: E402
import gerar_brasao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _rgba(imagem: QImage):
    """Os pixels de uma QImage como bytes RGBA (sem a sobra no fim de cada linha)."""
    imagem = imagem.convertToFormat(QImage.Format.Format_RGBA8888)
    largura, altura, linha = imagem.width(), imagem.height(), imagem.bytesPerLine()
    bruto = bytes(imagem.constBits())[: linha * altura]
    return b"".join(bruto[y * linha: y * linha + largura * 4] for y in range(altura))


def _diferenca_media(a: bytes, b: bytes) -> float:
    assert len(a) == len(b)
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


# ---------------------------------------------------------------------------
# D-746: o icone
# ---------------------------------------------------------------------------

def test_d746_o_ico_tem_todos_os_tamanhos_cada_um_desenhado_do_vetor():
    """Cada tamanho do .ico e, pixel por pixel, o vetor desenhado de novo naquele tamanho."""
    imagens = gerar_brasao.ler_ico(brasao.ICONE.read_bytes())
    assert sorted(imagens) == [16, 20, 24, 32, 40, 48, 64, 128, 256] == list(brasao.TAMANHOS_DO_ICONE)
    for lado, imagem in imagens.items():
        assert imagem.size == (lado, lado)
        assert imagem.tobytes() == gerar_brasao.desenhar_icone(lado).tobytes(), f"o {lado} nao e o vetor"


def test_d746_nenhum_tamanho_e_o_grande_diminuido():
    """O pequeno desenhado do vetor nao e o 256 diminuido (que borra o contorno):
    se alguem trocar por um redimensionamento, este teste acusa."""
    from PIL import Image

    imagens = gerar_brasao.ler_ico(brasao.ICONE.read_bytes())
    for lado in (16, 32, 48):
        diminuido = imagens[256].resize((lado, lado), Image.Resampling.LANCZOS)
        assert imagens[lado].tobytes() != diminuido.tobytes()


def test_d746_o_icone_e_o_brasao_inteiro_num_quadrado_com_margem_transparente():
    """Como na pagina de exemplo: o brasao inteiro, de cima a baixo, centrado,
    com margem transparente dos lados (ele e mais alto que largo)."""
    imagens = gerar_brasao.ler_ico(brasao.ICONE.read_bytes())
    for lado, imagem in imagens.items():
        x0, y0, x1, y1 = imagem.getchannel("A").getbbox()
        assert y0 <= 1 and y1 >= lado - 1, f"o {lado} cortou o brasao em cima ou embaixo"
        assert x0 >= 1 and x1 <= lado - 1, f"o {lado} nao tem margem dos lados"
        assert abs(x0 - (lado - x1)) <= max(1, lado // 64), f"o {lado} nao esta no meio"


def test_d746_o_qt_le_todos_os_tamanhos_do_icone(app):
    tamanhos = {s.width() for s in QIcon(str(brasao.ICONE)).availableSizes()}
    assert set(brasao.TAMANHOS_DO_ICONE) <= tamanhos


def test_d746_o_icone_vale_para_o_exe_o_instalador_e_os_atalhos():
    """O .exe (PyInstaller --icon; os atalhos usam o icone do .exe), o
    instalador do Velopack (vpk --icon) e o de reserva do Inno (SetupIconFile)."""
    for onefile in (False, True):
        comando = empacotar.comando_do_pyinstaller(onefile)
        assert comando[comando.index("--icon") + 1] == str(brasao.ICONE)
    vpk = empacotar.comando_do_vpk(Path("vpk.exe"), Path("pasta"), Path("saida"), "1.2.0")
    assert vpk[vpk.index("--icon") + 1] == str(brasao.ICONE)
    iss = (RAIZ / "instalador.iss").read_text(encoding="utf-8")
    linha = next(li for li in iss.splitlines() if li.startswith("SetupIconFile="))
    assert (RAIZ / linha.split("=", 1)[1].replace("\\", "/")).resolve() == brasao.ICONE.resolve()
    assert brasao.ICONE.is_file()


def test_d746_o_main_poe_o_icone_em_todas_as_janelas():
    texto = (RAIZ / "main.py").read_text(encoding="utf-8")
    assert "app.setWindowIcon(QIcon(str(brasao.ICONE)))" in texto


# ---------------------------------------------------------------------------
# D-745 / D-747: o giro
# ---------------------------------------------------------------------------

def test_d745_as_imagens_do_giro_sao_o_vetor_em_cada_escala_da_tela():
    for escala in brasao.ESCALAS_DO_GIRO:
        from PIL import Image

        gravada = Image.open(brasao.arquivo_do_giro(escala)).convert("RGBA")
        assert gravada.size[0] == round(brasao.LARGURA_DO_GIRO * escala)
        assert gravada.tobytes() == gerar_brasao.desenhar_giro(escala).tobytes(), f"escala {escala}"


def test_d747_o_giro_e_o_da_pagina_de_exemplo_ponto_por_ponto(app):
    """A conta do navegador para "perspective: 900px; rotateY(a)" (CSS da
    pagina aprovada) e a do programa levam cada ponto ao mesmo lugar."""
    from ui import brasao_girando as bg

    largura, altura = brasao.tamanho_do_giro()
    for angulo in (10, 30, 60, 85, -20, -75):
        t = bg.transformacao(angulo, largura, altura, QPointF(0, 0))
        for x, y in ((0, 0), (largura, 0), (largura, altura), (0, altura), (largura * 0.3, altura * 0.6)):
            p = t.map(QPointF(x, y))
            dx, dy, d, a = x - largura / 2, y - altura / 2, brasao.PERSPECTIVA, math.radians(angulo)
            css_x = dx * math.cos(a) * d / (d + dx * math.sin(a))
            css_y = dy * d / (d + dx * math.sin(a))
            assert abs(p.x() - css_x) < 1e-6 and abs(p.y() - css_y) < 1e-6
    assert brasao.SEGUNDOS_POR_VOLTA == 2.5 and brasao.PERSPECTIVA == 900 and brasao.LARGURA_DO_GIRO == 200


def test_d744_de_frente_o_desenho_e_o_vetor_sem_mudar_nada(app):
    """Em 0 grau, o quadro tem o brasao pixel por pixel igual ao desenho do vetor:
    nem cor, nem corte, nem sombra (D-744)."""
    from ui import brasao_girando as bg

    quadro = bg.desenhar_quadro(0.0)
    vetor = QImage(str(brasao.arquivo_do_giro(1.0)))
    largura, altura = bg.tamanho_da_janela()
    x, y = (largura - vetor.width()) // 2, (altura - vetor.height()) // 2
    recorte = quadro.copy(x, y, vetor.width(), vetor.height())
    recorte.setDevicePixelRatio(1.0)
    # comparado no formato em que o Qt pinta a janela (cor ja multiplicada pela
    # transparencia); a ida e volta para o formato comum mudaria 1 nos semitransparentes
    assert _rgba(recorte) == _rgba(vetor.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied))
    # fora do brasao, nada: nem sombra nem fundo
    fora = _rgba(quadro)
    for linha in list(range(0, y)) + list(range(y + vetor.height(), altura)):
        alfas = fora[linha * largura * 4 + 3: (linha + 1) * largura * 4: 4]
        assert not any(alfas), f"tem desenho fora do brasao na linha {linha}"


def test_d745_de_costas_o_quadro_e_igual_ao_de_frente_nunca_espelhado(app):
    from ui import brasao_girando as bg

    frente = bg.desenhar_quadro(0.0)
    costas = bg.desenhar_quadro(180.0)
    assert _rgba(costas) == _rgba(frente), "de costas tem de ser o brasao de frente"
    for angulo in (20.0, 60.0, 80.0):
        assert _rgba(bg.desenhar_quadro(angulo + 180.0)) == _rgba(bg.desenhar_quadro(angulo))
    espelhado = frente.flipped(Qt.Orientation.Horizontal)
    assert _diferenca_media(_rgba(costas), _rgba(espelhado)) > 5, "de costas saiu espelhado"


def test_d745_de_lado_vira_uma_faixa_fina(app):
    from ui import brasao_girando as bg

    def largura_desenhada(angulo: float) -> int:
        img = bg.desenhar_quadro(angulo).convertToFormat(QImage.Format.Format_RGBA8888)
        dados, w = _rgba(img), img.width()
        colunas = {i % w for i in range(len(dados) // 4) if dados[i * 4 + 3] > 0}
        return len(colunas)

    assert largura_desenhada(0) >= 195
    assert largura_desenhada(88) <= 12
    assert largura_desenhada(90) == 0
    assert 130 <= largura_desenhada(45) <= 150


def test_d745_a_janela_e_transparente_sem_moldura_por_cima_e_fora_da_barra(app):
    from ui import brasao_girando as bg

    janela = bg.BrasaoGirando(escala_da_tela=1.0)
    try:
        sinais = janela.windowFlags()
        for sinal in (Qt.WindowType.FramelessWindowHint, Qt.WindowType.WindowStaysOnTopHint,
                      Qt.WindowType.NoDropShadowWindowHint, Qt.WindowType.WindowTransparentForInput):
            assert sinais & sinal, sinal
        assert (sinais & Qt.WindowType.WindowType_Mask) == Qt.WindowType.SplashScreen  # sem barra de tarefas
        assert janela.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert not janela.autoFillBackground()
        # o que a janela desenha: so o brasao, sobre fundo transparente (cantos e bordas vazios)
        janela.angulo = 30.0
        foto = QImage(janela.size(), QImage.Format.Format_ARGB32_Premultiplied)
        foto.fill(Qt.GlobalColor.transparent)
        janela.render(foto)
        dados, w, h = _rgba(foto), foto.width(), foto.height()
        borda = [dados[(y * w + x) * 4 + 3] for y in range(h) for x in (0, 1, w - 2, w - 1)]
        borda += [dados[(y * w + x) * 4 + 3] for y in (0, 1, h - 2, h - 1) for x in range(w)]
        assert not any(borda), "a janela tem quadro ou fundo"
        assert any(dados[3::4]), "a janela nao desenhou o brasao"
    finally:
        janela.deleteLater()


def test_d747_uma_volta_a_cada_dois_segundos_e_meio(app):
    from ui import brasao_girando as bg

    assert bg.angulo_no_tempo(0.0) == 0.0
    assert bg.angulo_no_tempo(0.625) == pytest.approx(90.0)
    assert bg.angulo_no_tempo(1.25) == pytest.approx(180.0)
    assert bg.angulo_no_tempo(2.5) == pytest.approx(0.0)
    assert bg.angulo_no_tempo(3.0) == pytest.approx(72.0)
    # a janela anda pelo relogio: o angulo fica entre o de antes e o de depois
    janela = bg.BrasaoGirando(escala_da_tela=1.0)
    try:
        janela.relogio.restart()
        time.sleep(0.3)
        antes = janela.relogio.elapsed() / 1000.0
        janela._andar()
        depois = janela.relogio.elapsed() / 1000.0
        assert bg.angulo_no_tempo(antes) - 1e-9 <= janela.angulo <= bg.angulo_no_tempo(depois) + 1e-9
    finally:
        janela.deleteLater()


# ---------------------------------------------------------------------------
# D-744: quando aparece e quando some
# ---------------------------------------------------------------------------

def test_d744_nunca_aparece_nos_testes_nem_na_conta_dos_testes_a_distancia():
    from ui import tela_de_carregamento as tc

    abertos = []
    assert tc.abrir_o_brasao(abrir=lambda *a, **k: abertos.append(a)).motivo == "teste"
    assert tc.nao_mostrar({"QT_QPA_PLATFORM": "offscreen"}, lambda: False) == "fora da tela"
    assert tc.nao_mostrar({}, lambda: True) == "conta dos testes a distancia"
    assert tc.nao_mostrar({}, lambda: False) is None
    assert abertos == []


def test_d744_abre_o_proprio_programa_sem_janela_preta():
    from ui import tela_de_carregamento as tc

    pedidos = []

    class Falso:
        def poll(self):
            return None

        def terminate(self):
            pedidos.append("fechou")

    aberto = tc.abrir_o_brasao(ambiente={}, conta_de_testes=lambda: False,
                               abrir=lambda comando, **opcoes: pedidos.append((comando, opcoes)) or Falso())
    comando, opcoes = pedidos[0]
    assert comando[-2:] == ["--brasao-girando", str(os.getpid())]
    assert comando[1] == str(RAIZ / "main.py")       # pelo codigo; empacotado e o proprio .exe
    assert opcoes["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)
    aberto.fechar()
    aberto.fechar()                                 # pode chamar de novo
    assert pedidos[1:] == ["fechou"]


def test_d744_um_erro_ao_abrir_nunca_impede_o_programa():
    from ui import tela_de_carregamento as tc

    def quebra(*_a, **_k):
        raise OSError("sem processo")

    aberto = tc.abrir_o_brasao(ambiente={}, conta_de_testes=lambda: False, abrir=quebra)
    assert aberto.motivo == "erro ao abrir" and not aberto.aberto
    aberto.fechar()


def test_d744_o_main_abre_o_brasao_antes_dos_imports_pesados():
    texto = (RAIZ / "main.py").read_text(encoding="utf-8")
    corpo = texto[texto.index("def main()"):]
    assert corpo.index("abrir_o_brasao()") < corpo.index("from PySide6")
    assert corpo.index("abrir_o_brasao()") < corpo.index("from ui.janela_principal import JanelaPrincipal")
    # o modo do processo do brasao e atendido antes de tudo, como o servidor de paginas
    assert texto.index('"--brasao-girando"') < texto.index("atender_linha_de_comando(sys.argv)")


def _processo_do_brasao(pid: int) -> subprocess.Popen:
    ambiente = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    return subprocess.Popen([sys.executable, str(RAIZ / "main.py"), "--brasao-girando", str(pid)],
                            cwd=str(RAIZ), env=ambiente, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def test_d744_o_brasao_fecha_sozinho_se_o_programa_morrer():
    programa = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(4)"])
    girando = _processo_do_brasao(programa.pid)
    try:
        time.sleep(2.0)
        assert girando.poll() is None, "o brasao fechou com o programa ainda aberto"
        programa.wait(timeout=30)
        assert girando.wait(timeout=30) == 0
    finally:
        for p in (programa, girando):
            if p.poll() is None:
                p.kill()


# Um main() de verdade, num processo a parte e fora da tela: a janela
# principal e trocada por uma leve (a de verdade leva segundos e nao muda o
# que se prova aqui), e o brasao e o processo de verdade, fora da tela.
_MAIN_DE_PROVA = textwrap.dedent(r"""
    import json, os, subprocess, sys, time, types
    sys.path.insert(0, sys.argv[1])
    os.chdir(sys.argv[1])
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QWidget

    import main
    import ui.tela_de_carregamento as tc
    import ui.testes_a_distancia_ui as tdui
    import ui.aviso_de_atualizacao as aviso
    import core.aquecimento as aquecimento
    import core.paginas_em_outro_processo as paginas

    resultado = {}

    def abrir_de_verdade():
        processo = subprocess.Popen([sys.executable, "main.py", "--brasao-girando", str(os.getpid())],
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        resultado["brasao"] = processo
        time.sleep(2.0)            # o carregamento pesado do programa
        return tc.BrasaoAberto(processo)

    class Janela(QWidget):
        def showEvent(self, evento):
            resultado["vivo_ao_mostrar"] = resultado["brasao"].poll() is None
            QTimer.singleShot(1500, self.conferir)
            super().showEvent(evento)

        def conferir(self):
            resultado["vivo_depois"] = resultado["brasao"].poll() is None
            resultado["icones"] = sorted({s.width() for s in QApplication.windowIcon().availableSizes()})
            QApplication.quit()

    tc.abrir_o_brasao = abrir_de_verdade
    sys.modules["ui.janela_principal"] = types.SimpleNamespace(JanelaPrincipal=Janela)
    tdui.primeira_vez_se_preciso = lambda janela: None
    aviso.ligar_na_janela = lambda janela: None
    aquecimento.aquecer_em_segundo_plano = lambda: None
    paginas.iniciar_em_segundo_plano = lambda: None
    sys.argv = ["main.py"]
    main.main()
    resultado.pop("brasao").wait(timeout=10)
    print("RESULTADO " + json.dumps(resultado))
""")


def test_d744_o_brasao_some_quando_a_janela_principal_abre(tmp_path):
    script = tmp_path / "main_de_prova.py"
    script.write_text(_MAIN_DE_PROVA, encoding="utf-8")
    ambiente = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    feito = subprocess.run([sys.executable, str(script), str(RAIZ)], cwd=str(RAIZ), env=ambiente,
                           capture_output=True, text=True, timeout=180,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    linha = next((li for li in feito.stdout.splitlines() if li.startswith("RESULTADO ")), None)
    assert linha, feito.stdout + feito.stderr
    resultado = json.loads(linha[len("RESULTADO "):])
    assert resultado["vivo_ao_mostrar"], "o brasao nao estava girando enquanto o programa carregava"
    assert not resultado["vivo_depois"], "o brasao continuou depois da janela principal aparecer"
    assert set(brasao.TAMANHOS_DO_ICONE) <= set(resultado["icones"]), "a janela ficou sem o icone do brasao"


# ---------------------------------------------------------------------------
# D-748 (Samuel, 17/11/2026: "Sim"): na abertura em que a versao nova entra, a
# janelinha "Atualizando o programa, espere um pouco..." (D-742) some na hora
# em que o brasao girando aparece; os dois nunca ficam juntos na tela.
# ---------------------------------------------------------------------------

# A janela do Windows Forms de mentira (como em tests/test_decisoes_ajudante_da_atualizacao.py), com a hora em
# que mostrou e fechou: nenhuma janela de verdade e criada, nada aparece na tela.
_JANELINHA_DE_MENTIRA = r"""
function New-Object { param([string]$TypeName, [object[]]$ArgumentList)
  if ($TypeName -like 'System.Windows.Forms.*') {
    $o = [pscustomobject]@{ Text=''; ControlBox=$true; FormBorderStyle=''; StartPosition=''; ShowInTaskbar=$true;
                            TopMost=$false; ClientSize=$null; Dock=''; TextAlign=''; Font=$null; Controls=$null }
    $c = [pscustomobject]@{}
    $c | Add-Member -MemberType ScriptMethod -Name Add -Value { param($x) }
    $o.Controls = $c
    $o | Add-Member -MemberType ScriptMethod -Name Show -Value { Write-Host ('MOSTROU ' + [DateTime]::UtcNow.Ticks) }
    $o | Add-Member -MemberType ScriptMethod -Name Close -Value { Write-Host ('FECHOU ' + [DateTime]::UtcNow.Ticks) }
    return $o }
  Microsoft.PowerShell.Utility\New-Object -TypeName $TypeName -ArgumentList $ArgumentList }
"""

# O processo do brasao de verdade (rodar_sozinho), fora da tela, com as marcas de teste; anota a hora em que a
# janela dele aparece e sai logo depois.
_BRASAO_DE_PROVA = textwrap.dedent(r"""
    import sys, time
    sys.path.insert(0, sys.argv[1])
    import atualizacao
    atualizacao.MARCA_DE_ABERTO = sys.argv[2]
    atualizacao.MARCA_DA_JANELINHA = sys.argv[3]
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui import brasao_girando as bg
    mostrar = bg.BrasaoGirando.mostrar_no_meio
    def mostrar_e_anotar(self):
        print("BRASAO %d" % (int(time.time() * 10_000_000) + 621355968000000000), flush=True)
        mostrar(self)
        QTimer.singleShot(500, QApplication.quit)
    bg.BrasaoGirando.mostrar_no_meio = mostrar_e_anotar
    sys.exit(bg.rodar_sozinho(sys.argv[4]))
""")


@pytest.mark.skipif(sys.platform != "win32", reason="a janelinha usa o PowerShell e as marcas do Windows")
def test_d748_a_janelinha_some_quando_o_brasao_aparece_e_nunca_ficam_juntos(tmp_path, monkeypatch):
    """D-748 (Samuel, 17/11/2026: "Sim"). A janelinha de verdade (o script da D-742, com a janela do Windows
    Forms trocada por uma de mentira que anota a hora) esta na tela; abre-se o processo do brasao de verdade.
    Ela tem de fechar ANTES de o brasao aparecer. Marcas com nome de teste: nada do programa de verdade e tocado.
    Teste de reversao: no codigo de antes o brasao nao punha a marca, e a janelinha so fechava no limite (20 s),
    muito depois de o brasao aparecer."""
    import shutil
    import threading
    import uuid

    import atualizacao

    powershell = shutil.which("powershell")
    assert powershell
    sufixo = uuid.uuid4().hex
    marca_aberto = f"Local\\EditorImpressao-teste-aberto-{sufixo}"
    marca_janelinha = f"Local\\EditorImpressao-teste-janelinha-{sufixo}"
    monkeypatch.setattr(atualizacao, "MARCA_DA_JANELINHA", marca_janelinha, raising=False)
    script = tmp_path / "janelinha.ps1"
    script.write_text(_JANELINHA_DE_MENTIRA + "\n" + atualizacao.script_da_janelinha(marca=marca_aberto, limite_s=20),
                      encoding="utf-8-sig")
    janelinha = subprocess.Popen([powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                  "-File", str(script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 encoding="utf-8", errors="replace",
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    linhas: list[str] = []
    leitor = threading.Thread(target=lambda: linhas.extend(l.strip() for l in janelinha.stdout), daemon=True)
    leitor.start()
    brasao_py = tmp_path / "brasao_de_prova.py"
    brasao_py.write_text(_BRASAO_DE_PROVA, encoding="utf-8")
    try:
        limite = time.monotonic() + 90
        while not any(l.startswith("MOSTROU") for l in linhas) and time.monotonic() < limite:
            assert janelinha.poll() is None, f"a janelinha parou antes de aparecer: {linhas}"
            time.sleep(0.1)
        assert any(l.startswith("MOSTROU") for l in linhas), f"a janelinha não apareceu: {linhas}"
        feito = subprocess.run([sys.executable, str(brasao_py), str(RAIZ), marca_aberto, marca_janelinha,
                                str(os.getpid())], cwd=str(RAIZ), capture_output=True, text=True, timeout=120,
                               env=dict(os.environ, QT_QPA_PLATFORM="offscreen"),
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        janelinha.wait(timeout=60)
        leitor.join(timeout=10)
    finally:
        if janelinha.poll() is None:
            janelinha.kill()
    brasao_apareceu = [int(l.split()[1]) for l in feito.stdout.splitlines() if l.startswith("BRASAO ")]
    fechou = [int(l.split()[1]) for l in linhas if l.startswith("FECHOU ")]
    assert brasao_apareceu, feito.stdout + feito.stderr
    assert fechou, f"a janelinha nunca fechou: {linhas}"
    assert fechou[0] <= brasao_apareceu[0], (
        f"o brasão apareceu {(fechou[0] - brasao_apareceu[0]) / 1e7:.2f} s antes de a janelinha sumir: os dois juntos")


def test_d748_o_brasao_poe_a_marca_antes_de_olhar_a_janelinha_e_espera_ela_sumir():
    """D-748: a ordem que garante "nunca juntos" (o brasao poe a marca de aberto, so depois olha a da
    janelinha) e a espera enquanto a janelinha existe. Na abertura comum (sem janelinha) nada espera."""
    from ui import brasao_girando as bg

    passos = []
    ainda = iter([True, True, False])
    bg.antes_de_mostrar(marcar=lambda: passos.append("marcou"),
                        ha_janelinha=lambda: passos.append("olhou") or next(ainda),
                        dormir=lambda s: passos.append("esperou"))
    assert passos == ["marcou", "olhou", "esperou", "olhou", "esperou", "olhou"]
    passos.clear()
    bg.antes_de_mostrar(marcar=lambda: passos.append("marcou"),
                        ha_janelinha=lambda: passos.append("olhou") or False, dormir=lambda s: passos.append("x"))
    assert passos == ["marcou", "olhou"]
    # se a janelinha travar, o brasao aparece mesmo assim depois do limite
    comeco = time.monotonic()
    bg.antes_de_mostrar(marcar=lambda: None, ha_janelinha=lambda: True, limite_s=0.2)
    assert time.monotonic() - comeco < 2


def test_d748_a_janelinha_pega_a_marca_dela_antes_de_olhar_o_programa_e_solta_depois_de_fechar():
    import atualizacao

    texto = atualizacao.script_da_janelinha()
    pega = texto.index(f"[System.Threading.Mutex]::new($false, '{atualizacao.MARCA_DA_JANELINHA}')")
    assert pega < texto.index("TryOpenExisting"), "a marca da janelinha vem antes de olhar a do programa aberto"
    assert texto.index("$janela.Close()") < texto.index("$minha.Dispose()")
    # a regra continua uma so: a mesma marca do programa aberto faz a janelinha sumir
    assert f"'{atualizacao.MARCA_DE_ABERTO}'" in texto
