"""A caixa da página e a do conteúdo do ScanTailor na DLL comum (itens 2.13 e
2.5 da Fase 2, 12/10/2026).

Testes de máquina:
- cópia fiel: a "cola" copiada de ImageSettings.cpp é igual, letra por letra,
  ao original v1.2.1 (guardado em terceiros/.../referencia); os arquivos de
  referência são os originais; os do select_content estão entre os conferidos
  pela soma (o teste geral de cópia fiel é tests/test_st_ferramentas.py);
- a função em C em folhas de mentira: a faixa preta do scanner sai da caixa da
  página; a caixa do conteúdo fica no texto e não corta letra; página em
  branco não tem conteúdo; parâmetro errado não derruba nada;
- core/caixas_scantailor.py: os modos, os milímetros, a trava de memória, o
  "indisponível" sem a DLL, e que NINGUÉM no programa chama o módulo ainda;
- nas páginas que o pesquisador mediu em 12/10 com o programa de teste dele
  (o mesmo código original, ligado em outra biblioteca), a DLL dá as MESMAS
  caixas (tests/dados/caixas_scantailor_pesquisador.json);
- o DPI muda a caixa (Horas 13 a 72 e a 150 DPI);
- página sem borda preta: a caixa da página não tira nada da folha e a caixa
  do conteúdo não parte letra (Palatino 66, Escola 35 e o Siebmacher).

As páginas de verdade ficam fora do git (gabarito/paginas, e pastas somente
leitura fora do projeto): onde faltarem, o teste é pulado.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import re
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import caixas_scantailor as cs
from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
COLA = TERCEIROS / "ligacao-ferramentas" / "caixas.cpp"
REF_IMAGESETTINGS = TERCEIROS / "referencia" / "ImageSettings.cpp"
REF_TASK = TERCEIROS / "referencia" / "select_content" / "Task.cpp"
GABARITO = RAIZ / "gabarito" / "paginas"
# Somente leitura, fora do projeto (onde o pesquisador pegou as páginas).
ARQUIVOS = Path(r"D:\programas\EditorImpressao-arquivos")
FAIXA = ARQUIVOS / "revisar-decisoes-trabalho" / "faixa"
LIVROS = ARQUIVOS / "TESTES EDITOR DE IMPRESSAO" / "LIVROS PARA TESTE"
PESQUISADOR = json.loads((RAIZ / "tests" / "dados" / "caixas_scantailor_pesquisador.json")
                         .read_text(encoding="utf-8"))["paginas"]

# SHA-256 dos dois arquivos do ScanTailor Advanced v1.2.1 (commit 5eaac18)
# guardados em referencia/, tirados do git do ScanTailor (fim de linha LF).
SHA256_IMAGESETTINGS = "6ff9901b60ea3f26abe43bfa0f47fb5c436337310184b551dc204c1a27b08776"
SHA256_TASK = "ed5c1f5c7392d881baff52436a76d50638058f230e803add70ac36cd63b392cd"

# TOLERÂNCIA da comparação com o pesquisador, em pontos da imagem. O programa
# de teste dele imprimiu as caixas com UMA casa decimal (%.1f): o número dele
# pode estar até 0,05 ponto longe do valor exato. 0,06 = esse arredondamento
# mais uma folga para a conta em ponto flutuante. Não é folga para a conta do
# ScanTailor: as duas rodam o mesmo código e têm de dar o mesmo retângulo.
TOLERANCIA_DO_PESQUISADOR = 0.06

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _sem_cr(caminho: Path) -> str:
    return caminho.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


# ------------------------------------------------------------- cópia fiel

def test_referencias_sao_os_originais():
    assert hashlib.sha256(_sem_cr(REF_IMAGESETTINGS).encode("utf-8")).hexdigest() == SHA256_IMAGESETTINGS
    assert hashlib.sha256(_sem_cr(REF_TASK).encode("utf-8")).hexdigest() == SHA256_TASK


def test_cola_copiada_sem_mudanca():
    """O trecho entre as marcas de caixas.cpp é igual às linhas 48-51 de ImageSettings.cpp."""
    cola = _sem_cr(COLA)
    trecho = re.search(r"// ---- COPIADO SEM MUDANCA[^\n]*\n(?:// [^\n]*\n)*(.*?)// ---- FIM DO TRECHO COPIADO",
                       cola, re.S)
    assert trecho, "marcas do trecho copiado sumiram de caixas.cpp"
    original = "\n".join(_sem_cr(REF_IMAGESETTINGS).split("\n")[47:51]) + "\n"
    assert trecho.group(1) == original


def test_select_content_esta_entre_os_conferidos():
    somas = (TERCEIROS / "somas-v1.2.1.txt").read_text(encoding="utf-8")
    for rel in ("core/filters/select_content/PageFinder.cpp", "core/filters/select_content/PageFinder.h",
                "core/filters/select_content/ContentBoxFinder.cpp",
                "core/filters/select_content/ContentBoxFinder.h",
                "core/filters/select_content/PhysSizeCalc.cpp", "core/FilterData.cpp", "core/FilterData.h",
                "core/ImageSettings.h", "imageproc/MaxWhitespaceFinder.cpp", "imageproc/SEDM.cpp"):
        assert f"src/{rel}" in somas


def test_so_vieram_os_arquivos_do_select_content_que_a_cola_usa():
    """Os filtros do ScanTailor têm arquivos de MESMO nome (Settings.h, Task.h,
    Utils.h...). Da pasta select_content só podem estar os três pares que a
    cola usa, senão um #include pelo nome pega o arquivo errado."""
    pasta = TERCEIROS / "src" / "core" / "filters" / "select_content"
    assert sorted(p.name for p in pasta.iterdir()) == [
        "ContentBoxFinder.cpp", "ContentBoxFinder.h", "PageFinder.cpp", "PageFinder.h",
        "PhysSizeCalc.cpp", "PhysSizeCalc.h"]


# ------------------------------------------------------------- folhas de mentira

PAPEL, TINTA = 235, 30


def _folha(largura=1000, altura=1400, texto=(150, 200, 800, 1200), faixa_direita=0, faixa_de_cima=0):
    """Folha clara com um bloco de "palavras" (retângulos de 36 x 12 pontos) na
    área `texto` (x0, y0, x1, y1) e, se pedido, faixas pretas de ponta a ponta
    (o fundo do scanner) à direita e em cima."""
    img = np.full((altura, largura), PAPEL, np.uint8)
    x0, y0, x1, y1 = texto
    for y in range(y0, y1 - 12 + 1, 30):
        for x in range(x0, x1 - 36 + 1, 50):
            img[y:y + 12, x:x + 36] = TINTA
    if faixa_direita:
        img[:, largura - faixa_direita:] = 0
    if faixa_de_cima:
        img[:faixa_de_cima, :] = 0
    return img


def _tinta_do_texto(img, faixa_direita=0, faixa_de_cima=0):
    """(x0, y0, x1, y1) de toda a tinta do bloco de palavras (sem as faixas pretas)."""
    miolo = img[faixa_de_cima:, :img.shape[1] - faixa_direita] < 128
    ys, xs = np.nonzero(miolo)
    return xs.min(), ys.min() + faixa_de_cima, xs.max() + 1, ys.max() + 1 + faixa_de_cima


@precisa_da_dll
def test_folha_sem_borda_preta_a_pagina_e_a_folha_inteira():
    img = _folha()
    r = cs.achar(img, 150)
    assert r.disponivel, r.motivo
    assert r.pagina.como_tupla() == pytest.approx((0, 0, 1000, 1400), abs=1.0)
    assert r.preto_no_branco


@precisa_da_dll
def test_a_caixa_do_conteudo_fica_no_texto_e_nao_corta_letra():
    img = _folha()
    r = cs.achar(img, 150)
    assert r.tem_conteudo
    x0, y0, x1, y1 = _tinta_do_texto(img)
    c = r.conteudo
    # Não corta: toda a tinta fica dentro (1 ponto de folga do arredondamento).
    assert c.x0 <= x0 + 1 and c.y0 <= y0 + 1 and c.x1 >= x1 - 1 and c.y1 >= y1 - 1
    # E fica no texto: não sobra mais que 15 pontos (2,5 mm a 150 DPI) de papel em volta.
    assert c.x0 >= x0 - 15 and c.y0 >= y0 - 15 and c.x1 <= x1 + 15 and c.y1 <= y1 + 15


@precisa_da_dll
def test_a_faixa_preta_do_scanner_sai_da_caixa_da_pagina():
    img = _folha(faixa_direita=80, faixa_de_cima=60)
    r = cs.achar(img, 150)
    assert r.disponivel, r.motivo
    p = r.pagina
    assert p.x0 == pytest.approx(0, abs=1.0) and p.y1 == pytest.approx(1400, abs=1.0)
    assert p.x1 == pytest.approx(920, abs=2.0)      # a faixa da direita começa em 920
    assert p.y0 == pytest.approx(60, abs=2.0)       # a de cima acaba em 60
    # O conteúdo continua sendo o texto, dentro da página.
    x0, y0, x1, y1 = _tinta_do_texto(img, faixa_direita=80, faixa_de_cima=60)
    c = r.conteudo
    assert c.x0 <= x0 + 1 and c.y0 <= y0 + 1 and c.x1 >= x1 - 1 and c.y1 >= y1 - 1
    assert c.x1 <= p.x1 and c.y0 >= p.y0


@precisa_da_dll
def test_sem_achar_a_pagina_ela_e_a_folha_inteira():
    img = _folha(faixa_direita=80)
    r = cs.achar(img, 150, achar_pagina=False)
    assert r.pagina.como_tupla() == pytest.approx((0, 0, 1000, 1400), abs=1e-6)


@precisa_da_dll
def test_sem_achar_o_conteudo_ele_e_a_caixa_da_pagina():
    img = _folha(faixa_direita=80)
    r = cs.achar(img, 150, achar_conteudo=False)
    assert r.tem_conteudo
    assert r.conteudo == r.pagina
    assert r.pagina.x1 == pytest.approx(920, abs=2.0)


_PALAVRAS = "mente felizes inclinados ao bem isentos de enfermidades e da morte".split()


def _folha_de_texto(largura=1000, altura=1400, x0=150, x1=900, y0=200, y1=1300):
    """Folha clara com linhas de palavras escritas (cv2.putText), de tamanhos
    diferentes, como um texto de verdade. Use ESTA quando o texto fica perto de
    uma faixa preta: a grade de retângulos iguais de _folha(), com as colunas
    alinhadas, parece uma tabela de riscos em pé, e o ScanTailor joga fora as
    colunas vizinhas da faixa (medido em 12/10/2026: com a faixa a 50 pontos, a
    caixa da grade começou em 749 em vez de 149, e a conta levou 5 s)."""
    img = np.full((altura, largura), PAPEL, np.uint8)
    k, y = 0, y0
    while y < y1:
        x = x0
        while True:
            palavra = _PALAVRAS[k % len(_PALAVRAS)]
            k += 1
            (w, _), _ = cv2.getTextSize(palavra, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            if x + w > x1:
                break
            cv2.putText(img, palavra, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 40, 2, cv2.LINE_AA)
            x += w + 12
        y += 30
    return img


@precisa_da_dll
@pytest.mark.parametrize("faixa", [60, 100, 140])
def test_texto_colado_na_faixa_preta_nao_e_cortado(faixa):
    """Faixa preta do scanner à esquerda, chegando a 10 pontos (1,7 mm a 150
    DPI) do começo das linhas: a página começa depois da faixa, o conteúdo fica
    dentro da página e nenhuma letra fica de fora."""
    img = _folha_de_texto()
    ys, xs = np.nonzero(img < 128)
    img[:, :faixa] = 0
    r = cs.achar(img, 150)
    assert r.disponivel and r.tem_conteudo
    p, c = r.pagina, r.conteudo
    assert p.x0 == pytest.approx(faixa, abs=2.0)
    assert c.x0 >= p.x0 - 1e-6 and c.y0 >= p.y0 - 1e-6 and c.x1 <= p.x1 + 1e-6 and c.y1 <= p.y1 + 1e-6
    assert c.x0 <= xs.min() + 1 and c.y0 <= ys.min() + 1 and c.x1 >= xs.max() and c.y1 >= ys.max()
    assert c.x0 >= xs.min() - 15 and c.x1 <= xs.max() + 16


@precisa_da_dll
def test_folha_colorida_da_o_mesmo_que_cinza():
    cinza = _folha(faixa_direita=80)
    cor = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    a, b = cs.achar(cinza, 150), cs.achar(cor, 150)
    assert a.pagina == b.pagina and a.conteudo == b.conteudo
    com_alfa = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGRA)
    assert cs.achar(com_alfa, 150).conteudo == a.conteudo


@precisa_da_dll
def test_pagina_em_branco_nao_tem_conteudo():
    r = cs.achar(np.full((1400, 1000), PAPEL, np.uint8), 150)
    assert r.disponivel, r.motivo
    assert not r.tem_conteudo
    assert r.conteudo is None and r.conteudo_mm is None and r.tamanho_do_conteudo_mm is None
    assert r.pagina.como_tupla() == pytest.approx((0, 0, 1000, 1400), abs=1.0)


@precisa_da_dll
def test_os_milimetros():
    img = _folha()
    r = cs.achar(img, 150)
    c, mm = r.conteudo, r.conteudo_mm
    assert mm.x0 == pytest.approx(c.x0 * 25.4 / 150) and mm.y1 == pytest.approx(c.y1 * 25.4 / 150)
    assert r.pagina_mm.largura == pytest.approx(r.pagina.largura * 25.4 / 150)
    # O tamanho que o ScanTailor guarda (PhysSizeCalc) é o mesmo, a menos do
    # arredondamento dos pontos por metro dele (1 parte em 10 mil).
    largura_mm, altura_mm = r.tamanho_do_conteudo_mm
    assert largura_mm == pytest.approx(mm.largura, rel=2e-4)
    assert altura_mm == pytest.approx(mm.altura, rel=2e-4)
    assert r.dpi == (150, 150)


@precisa_da_dll
def test_o_dpi_dito_muda_o_tamanho_em_mm_e_pode_mudar_a_caixa():
    img = _folha()
    a, b = cs.achar(img, 150), cs.achar(img, 300)
    assert a.tem_conteudo and b.tem_conteudo
    assert b.pagina_mm.largura == pytest.approx(a.pagina_mm.largura / 2, rel=0.01)


@precisa_da_dll
def test_claro_no_escuro():
    """Folha de letras claras em fundo escuro: o ScanTailor decide sozinho
    (None) que é "claro no escuro" e acha o mesmo conteúdo da folha comum."""
    comum = _folha()
    invertida = 255 - comum
    r = cs.achar(invertida, 150, claro_no_escuro=None)
    assert r.disponivel and not r.preto_no_branco
    assert r.conteudo == cs.achar(comum, 150, claro_no_escuro=False).conteudo
    # Forçando: a mesma conta.
    assert cs.achar(invertida, 150, claro_no_escuro=True).conteudo == r.conteudo
    assert cs.achar(comum, 150, claro_no_escuro=None).preto_no_branco


@precisa_da_dll
def test_tempo_medido_por_parte():
    r = cs.achar(_folha(faixa_direita=80), 150)
    assert r.segundos > 0
    assert r.segundos_da_pagina > 0 and r.segundos_do_conteudo > 0
    partes = r.segundos_do_preparo + r.segundos_da_pagina + r.segundos_do_conteudo
    assert partes <= r.segundos + 0.05


@precisa_da_dll
def test_parametro_errado_nao_derruba():
    funcao = st.padrao().funcao("st_ferramentas_caixas")
    img = np.ascontiguousarray(_folha(200, 300, (20, 20, 180, 280)))
    saida4 = [(ctypes.c_double * 4)() for _ in range(3)]
    mm = (ctypes.c_double * 2)()
    achou, pnb = ctypes.c_int(), ctypes.c_int()
    ms = (ctypes.c_double * 3)()
    erro = ctypes.create_string_buffer(256)

    def chamar(largura=200, altura=300, canais=1, dpi=150, modo_pagina=1, modo_conteudo=1, claro=0,
               tolerancia=0.1, pixels=img.ctypes.data):
        return funcao(pixels, largura, altura, 200, canais, dpi, dpi, modo_pagina, 0, 0.0, 0.0, tolerancia,
                      modo_conteudo, claro, saida4[0], saida4[1], saida4[2], mm, ctypes.byref(achou),
                      ctypes.byref(pnb), ms, erro, len(erro))

    assert chamar() == st.OK
    for errado in (dict(largura=0), dict(altura=-1), dict(canais=2), dict(dpi=0), dict(modo_pagina=2),
                   dict(modo_conteudo=-1), dict(claro=2), dict(claro=-2), dict(tolerancia=1.5),
                   dict(tolerancia=float("nan")), dict(pixels=None)):
        assert chamar(**errado) == st.ERRO_PARAMETRO, errado
        assert b"parametros" in erro.value


# ------------------------------------------------------------- o módulo em Python

def test_entrada_errada_fica_indisponivel_sem_excecao():
    for img, dpi in ((None, 150), (np.zeros((10,), np.uint8), 150), (np.zeros((10, 10, 2), np.uint8), 150),
                     (_folha(), 0), (_folha(), "abc"), (_folha(), 10), (_folha(), 5000)):
        r = cs.achar(img, dpi)
        assert not r.disponivel and r.motivo
        assert r.conteudo is None and not r.tem_conteudo
    r = cs.achar(_folha(), 150, tamanho_esperado_mm=(-1, 10))
    assert not r.disponivel and "tamanho esperado" in r.motivo
    r = cs.achar(_folha(), 150, tolerancia=2)
    assert not r.disponivel


def test_trava_de_memoria_pagina_ampliada_demais():
    """3000 x 4000 pontos ditos a 30 DPI virariam 300 milhões de pontos a 150
    DPI: a página é recusada antes de ir à DLL."""
    assert cs.pontos_a_150(3000, 4000, 30, 30) == pytest.approx(300e6)
    r = cs.achar(np.zeros((4000, 3000), np.uint8), 30)
    assert not r.disponivel
    assert "grande demais" in r.motivo
    # A maior página do acervo medida (Antiphon, 2742 x 3750 a 150 DPI) passa.
    assert cs.pontos_a_150(2742, 3750, 150, 150) < cs.PONTOS_MAXIMOS_A_150
    # E o Livro de Horas dito a 72 DPI (ampliado 2 vezes) também.
    assert cs.pontos_a_150(1024, 1533, 72, 72) < cs.PONTOS_MAXIMOS_A_150


def test_sem_a_dll_fica_indisponivel(tmp_path):
    biblioteca = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    r = cs.achar(_folha(), 150, biblioteca=biblioteca)
    assert not r.disponivel
    assert "não foram encontradas" in r.motivo


def test_caixa_em_mm():
    c = cs.Caixa(150, 300, 450, 900)
    assert c.largura == 300 and c.altura == 600
    assert c.em_mm(150).como_tupla() == pytest.approx((25.4, 50.8, 76.2, 152.4))
    assert c.em_mm(150, 300).y1 == pytest.approx(76.2)


def test_o_dpi_do_programa_e_o_das_outras_ferramentas_do_scantailor():
    """achar_na_pagina diz à DLL o MESMO DPI do limpar pontinhos e do endireitar."""
    from core.endireitar_scantailor import dpi_para_o_endireitar
    from core.pontinhos_scantailor import dpi_para_os_pontinhos

    for largura, altura, dpi, scan in ((1024, 1453, 72, 72.0), (1929, 2943, 400, 400.0),
                                       (1420, 2089, 200, 200.0), (961, 1396, 72, 72.0), (2000, 3000, 300, None)):
        esperado = dpi_para_os_pontinhos(largura, altura, dpi, scan)
        assert cs.dpi_para_as_caixas(largura, altura, dpi, scan) == esperado
        assert dpi_para_o_endireitar(largura, altura, dpi, scan) == esperado
    # O Livro de Horas (o PDF diz 72, que não é a resolução de verdade) vai a
    # mais que o dobro: a página deixa de ser ampliada.
    assert 130 < cs.dpi_para_as_caixas(1024, 1453, 72, 72.0) < 150
    assert cs.dpi_para_as_caixas(100, 100, None) is None


def test_so_o_corte_pelo_conteudo_chama_as_caixas():
    """Decisão do Samuel (G8, 05/10/2026): entra DESLIGADO de fábrica. Ligado
    em 20/10/2026 SÓ pelo corte que segue o conteúdo (item 2.5,
    core/corte_pelo_conteudo.py, com a opção do livro desligada de fábrica; a
    prova de que desligado nada é chamado está em
    tests/test_corte_pelo_conteudo_no_programa.py). Nada mais em core/, em
    ui/ ou na raiz pode usar o módulo direto: a busca da página dentro da
    borda preta (item 2.13) espera a pergunta g7-borda-ate-onde. A busca da
    página dentro da borda preta (2.13) entra só pelo livro com a borda preta."""
    permitidos = {"caixas_scantailor.py", "st_ferramentas.py", "corte_pelo_conteudo.py",
                  "borda_preta.py"}   # 2.13 (g7, 20/10/2026)
    usam = []
    for pasta in ("core", "ui"):
        for arquivo in (RAIZ / pasta).rglob("*.py"):
            if arquivo.name in permitidos:
                continue
            texto = arquivo.read_text(encoding="utf-8", errors="replace")
            if "caixas_scantailor" in texto or "st_ferramentas_caixas" in texto:
                usam.append(arquivo.relative_to(RAIZ).as_posix())
    for arquivo in RAIZ.glob("*.py"):
        if arquivo.name == "compilar_st_ferramentas.py":      # só a prova depois de compilar
            continue
        if "caixas_scantailor" in arquivo.read_text(encoding="utf-8", errors="replace"):
            usam.append(arquivo.name)
    assert usam == []
    # A busca da página (2.13) só liga pelo livro com a borda preta: o
    # corte_pelo_conteudo.medir a deixa desligada de fábrica, e quem a pede é
    # só core/pipeline.py com Projeto.borda_preta "até a moldura" (liberado
    # pela g7-borda-ate-onde, 20/10/2026).
    import inspect
    from core import corte_pelo_conteudo as cpc

    assert inspect.signature(cpc.medir).parameters["achar_pagina"].default is False
    # Desde 20/10/2026 nem o 2.13 usa a busca da página do ScanTailor (cortava o
    # cartão do Pesel 21); a página vem de core/borda_preta.so_o_preto.
    pipeline_txt = (RAIZ / "core" / "pipeline.py").read_text(encoding="utf-8")
    assert "achar_pagina=True" not in pipeline_txt


# ------------------------------------------------------------- as páginas de verdade

def _carregar(fonte: dict):
    """A imagem (BGR) de uma página medida pelo pesquisador, ou None se a fonte
    não existe neste PC (gabarito e pastas de fora ficam fora do git)."""
    if fonte["tipo"] == "gabarito":
        caminho = GABARITO / fonte["png"]
        return cv2.imread(str(caminho), cv2.IMREAD_COLOR) if caminho.is_file() else None
    if fonte["tipo"] == "faixa":
        caminho = FAIXA / fonte["png"]
        return cv2.imread(str(caminho), cv2.IMREAD_COLOR) if caminho.is_file() else None
    livro = Path(fonte["livro"])
    if not livro.is_absolute():
        livro = LIVROS / livro
    if not livro.is_file():
        return None
    import fitz

    with fitz.open(str(livro)) as doc:
        pix = doc[fonte["pagina"] - 1].get_pixmap(dpi=fonte["dpi_do_desenho"], alpha=False)
        rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_GRAY2BGR)


def _pagina_medida(nome: str):
    """(imagem, o que o pesquisador mediu) ou pula o teste."""
    esperado = PESQUISADOR[nome]
    img = _carregar(esperado["fonte"])
    if img is None:
        pytest.skip(f"sem a página {nome} neste PC")
    assert (img.shape[1], img.shape[0]) == (esperado["largura"], esperado["altura"])
    return img, esperado


@precisa_da_dll
@pytest.mark.parametrize("nome", sorted(PESQUISADOR))
def test_mesmas_caixas_do_programa_de_teste_do_pesquisador(nome):
    """A caixa da página e a do conteúdo (dentro dela) são as que o programa de
    teste do pesquisador achou com o mesmo código do ScanTailor, no mesmo DPI.
    Ver TOLERANCIA_DO_PESQUISADOR.

    O programa dele tratava toda página como "preto no branco"; aqui a função
    é chamada como vem de fábrica (o ScanTailor decide), e o teste confere que
    em todas estas páginas ele decide "preto no branco" - a mesma conta."""
    img, esperado = _pagina_medida(nome)
    r = cs.achar(img, esperado["dpi"])
    assert r.disponivel, r.motivo
    assert r.preto_no_branco
    assert r.pagina.como_tupla() == pytest.approx(tuple(esperado["pagina"]), abs=TOLERANCIA_DO_PESQUISADOR)
    # O pesquisador imprimiu o que o achador devolveu, antes do corte pela página.
    assert r.conteudo_bruto.como_tupla() == pytest.approx(tuple(esperado["conteudo_na_pagina"]),
                                                          abs=TOLERANCIA_DO_PESQUISADOR)
    # O que vale (o que o ScanTailor guarda) é o bruto cortado pela página.
    p, b, c = r.pagina, r.conteudo_bruto, r.conteudo
    assert c.como_tupla() == pytest.approx((max(b.x0, p.x0), max(b.y0, p.y0), min(b.x1, p.x1), min(b.y1, p.y1)),
                                           abs=1e-6)


@precisa_da_dll
@pytest.mark.parametrize("nome", ["ljs47_p046", "ljs47_p068"])
def test_o_achador_passa_da_pagina_e_o_corte_devolve(nome):
    """ljs47 (preto em volta toda): o achador do ScanTailor devolve um conteúdo
    que passa da caixa da página embaixo (caixas.cpp, "O que não é óbvio no
    código original"); o que o ScanTailor guarda, e o que vale aqui, é o
    conteúdo cortado pela página. Quem usar o bruto corta dentro do preto."""
    img, esperado = _pagina_medida(nome)
    r = cs.achar(img, esperado["dpi"])
    p, b, c = r.pagina, r.conteudo_bruto, r.conteudo
    assert b.y1 > p.y1 + 10                     # o bruto passa da página (16 a 108 pontos)
    assert c.y1 == pytest.approx(p.y1, abs=1e-6)
    assert c.x0 >= p.x0 and c.y0 >= p.y0 and c.x1 <= p.x1


# As outras duas contas que ele mediu (sem a caixa da página; com o "ajustar
# os cantos"), em poucas páginas, para o teste não demorar: uma de cada tipo.
_PAGINAS_DAS_VARIANTES = ("siebmacher_p007", "palatino_p066", "escola_p035", "camoes_p066", "marial_p007")


@precisa_da_dll
@pytest.mark.parametrize("nome", _PAGINAS_DAS_VARIANTES)
def test_mesmas_caixas_sem_a_pagina_e_com_os_cantos(nome):
    img, esperado = _pagina_medida(nome)
    folha = cs.achar(img, esperado["dpi"], achar_pagina=False, claro_no_escuro=False)
    assert folha.conteudo_bruto.como_tupla() == pytest.approx(tuple(esperado["conteudo_folha"]),
                                                              abs=TOLERANCIA_DO_PESQUISADOR)
    cantos = cs.achar(img, esperado["dpi"], ajustar_cantos=True, claro_no_escuro=False)
    assert cantos.pagina.como_tupla() == pytest.approx(tuple(esperado["pagina_cantos"]),
                                                       abs=TOLERANCIA_DO_PESQUISADOR)
    assert cantos.conteudo_bruto.como_tupla() == pytest.approx(tuple(esperado["conteudo_na_pagina_cantos"]),
                                                               abs=TOLERANCIA_DO_PESQUISADOR)


@precisa_da_dll
def test_o_dpi_muda_a_caixa_da_horas_13():
    """Horas 13: a moldura vai de 96 a 804 na largura (medida do pesquisador).
    Com 72 DPI ditos (o que o PDF diz) a caixa do conteúdo fica quase na folha
    inteira; com 150, fica por DENTRO da moldura. Mesma imagem, só o DPI."""
    img, a72 = _pagina_medida("horas_p013")
    _, a150 = _pagina_medida("horas_p013@150")
    r72 = cs.achar(img, 72, claro_no_escuro=False)
    r150 = cs.achar(img, 150, claro_no_escuro=False)
    assert r72.conteudo_bruto.como_tupla() == pytest.approx(tuple(a72["conteudo_na_pagina"]),
                                                            abs=TOLERANCIA_DO_PESQUISADOR)
    assert r150.conteudo_bruto.como_tupla() == pytest.approx(tuple(a150["conteudo_na_pagina"]),
                                                             abs=TOLERANCIA_DO_PESQUISADOR)
    assert r72.conteudo.x1 > 1000 and r72.conteudo.largura > 0.85 * img.shape[1]     # quase a folha
    assert 96 < r150.conteudo.x0 and r150.conteudo.x1 < 804                         # dentro da moldura
    # Em mm a mesma página tem tamanhos diferentes: quem diz o DPI decide.
    assert r72.pagina_mm.largura == pytest.approx(r150.pagina_mm.largura * 150 / 72, rel=1e-3)


# ------------------------------------------------------------- não cortar conteúdo

def _pecas_de_tinta(img: np.ndarray, dpi: float):
    """As peças de tinta da página (preto e branco Otsu, peças ligadas), sem os
    pontinhos: (x, y, largura, altura, encosta na beirada da folha?). Peça que
    encosta na beirada da folha é fundo do scanner ou folha vizinha, não letra."""
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    limiar, _ = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    n, _, caixas, _ = cv2.connectedComponentsWithStats((cinza < limiar).astype(np.uint8), 8)
    altura, largura = cinza.shape
    minimo = 4 * (dpi / 100.0) ** 2            # 4 pontos a 100 DPI: menor que isto é pontinho
    pecas = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in caixas[i])
        if area >= minimo:
            pecas.append((x, y, w, h, x <= 1 or y <= 1 or x + w >= largura - 1 or y + h >= altura - 1))
    return pecas


def _partidas_e_de_fora(pecas, caixa: cs.Caixa):
    """(peças que a caixa atravessa, peças inteiras do lado de fora), sem as que
    encostam na beirada da folha. 1 ponto de folga: a caixa do ScanTailor cai
    na grade de 150 DPI e a peça é contada em pontos inteiros."""
    partidas, de_fora = [], []
    for x, y, w, h, na_beirada in pecas:
        if na_beirada:
            continue
        dentro = x >= caixa.x0 - 1 and y >= caixa.y0 - 1 and x + w <= caixa.x1 + 1 and y + h <= caixa.y1 + 1
        fora = x + w <= caixa.x0 or x >= caixa.x1 or y + h <= caixa.y0 or y >= caixa.y1
        if fora:
            de_fora.append((x, y, w, h))
        elif not dentro:
            partidas.append((x, y, w, h))
    return partidas, de_fora


def _do_gabarito(nome: str):
    caminho = GABARITO / f"{nome}.png"
    if not caminho.is_file():
        pytest.skip("sem a pasta do gabarito")
    return cv2.imread(str(caminho), cv2.IMREAD_COLOR), PESQUISADOR[nome]["dpi"]


@precisa_da_dll
@pytest.mark.parametrize("nome", ["palatino_p066", "escola_p035"])
def test_pagina_sem_borda_preta_nada_e_cortado(nome):
    """Páginas do gabarito do corte SEM borda preta (conferência do corte de
    01/10): ligar "achar a página" não pode tirar nada da folha, e a caixa do
    conteúdo não parte nem deixa de fora nenhuma peça de tinta (letra, número
    de página, figura)."""
    img, dpi = _do_gabarito(nome)
    altura, largura = img.shape[:2]
    r = cs.achar(img, dpi)
    assert r.disponivel and r.tem_conteudo
    # A caixa da página é a folha inteira. Folga de 3 pontos: a conta é feita a
    # 150 DPI, e um ponto de lá vale até 2,7 pontos nestas páginas (400 DPI).
    assert r.pagina.como_tupla() == pytest.approx((0, 0, largura, altura), abs=3.0)
    partidas, de_fora = _partidas_e_de_fora(_pecas_de_tinta(img, dpi), r.conteudo)
    assert partidas == []
    assert de_fora == []


@precisa_da_dll
@pytest.mark.parametrize("nome", ["siebmacher_p007", "siebmacher_p009"])
def test_siebmacher_o_preto_sai_e_nenhuma_letra_e_partida(nome):
    """Siebmacher (fundo preto do scanner à direita, folha torta): a caixa da
    página quase não corta (o preto não cobre 95% do lado), e é a caixa do
    conteúdo que deixa o preto de fora, sem partir nenhuma peça de tinta."""
    img, dpi = _do_gabarito(nome)
    altura, largura = img.shape[:2]
    r = cs.achar(img, dpi)
    assert r.disponivel and r.tem_conteudo
    p, c = r.pagina, r.conteudo
    assert p.x1 > 0.98 * largura                    # a página ainda vai até o preto
    assert c.x1 < 0.83 * largura                    # o conteúdo para antes dele
    assert c.x0 >= p.x0 and c.y0 >= p.y0 and c.x1 <= p.x1 and c.y1 <= p.y1
    partidas, _ = _partidas_e_de_fora(_pecas_de_tinta(img, dpi), c)
    assert partidas == []
