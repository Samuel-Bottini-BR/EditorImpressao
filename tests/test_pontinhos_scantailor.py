"""Limpar pontinhos do ScanTailor (item M4 da Fase 2, 06/10/2026).

Testes de máquina (o "fica melhor ou pior" é teste de olho, do Samuel):
- as forças "pouco / normal / muito" são as três do ScanTailor (1, 2, 3);
- pontinho solto no papel sai; letra fica; pingo do "i" perto da letra fica;
- só tira preto, nunca põe; não mexe na imagem de entrada;
- largura que não é múltiplo de 32 (o ScanTailor guarda 32 pontos por palavra)
  e imagem que não é contígua voltam certas;
- o DPI acompanha: a mesma página a 600 DPI dá o mesmo que a 300;
- entrada ruim não chega à DLL;
- sem a DLL, o Preto e branco com o do ScanTailor cai no de hoje, igual
  ponto a ponto;
- chamado sem escolha (despeckle=True, o padrão da função, que os scripts e
  testes antigos usam), o Preto e branco continua com o nosso. A ligação ao
  programa (06/10/2026) é testada em tests/test_limpar_pontinhos_no_programa.py.
"""

from __future__ import annotations

import numpy as np
import pytest

from core import filtros as F
from core import pontinhos_scantailor as ps
from core import st_ferramentas as st

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def pagina_com_i(dpi: int = 300, largura: int = 400) -> tuple[np.ndarray, dict]:
    """Uma linha de hastes de letra, o pingo do "i" em cima da primeira e um
    pontinho solto no papel. Medidas a 300 DPI, levadas ao `dpi`."""
    e = dpi / 300
    img = np.full((int(400 * e), int(largura * e)), 255, np.uint8)
    onde = {}

    def pintar(nome, y0, y1, x0, x1):
        fatia = (slice(int(y0 * e), int(y1 * e)), slice(int(x0 * e), int(x1 * e)))
        img[fatia] = 0
        onde[nome] = fatia

    for k in range(8):
        pintar(f"haste{k}", 200, 230, 100 + k * 20, 105 + k * 20)
    pintar("pingo", 190, 194, 100, 104)        # 4 x 4, 6 pontos acima da haste
    pintar("solto", 50, 54, 300, 304)          # 4 x 4, longe de tudo
    return img, onde


# ------------------------------------------------------------- as forças

def test_forcas_sao_as_tres_do_scantailor():
    assert ps.FORCAS == {"pouco": 1.0, "normal": 2.0, "muito": 3.0}
    assert ps.forca_em_numero("muito") == 3.0
    assert ps.forca_em_numero(0.5) == 0.5 and ps.forca_em_numero(3.5) == 3.5
    for ruim in ("forte", 0.4, 3.6, 0):
        with pytest.raises(ValueError):
            ps.forca_em_numero(ruim)


# ------------------------------------------------------------- entrada ruim

class _BibliotecaDeMentira:
    """Conta as chamadas: prova que a entrada ruim é recusada SEM chegar à DLL."""

    def __init__(self):
        self.chamadas = 0
        self.motivo_indisponivel = None
        self.detalhe_indisponivel = None

    def funcao(self, nome):
        def chamar(*argumentos):
            self.chamadas += 1
            return st.OK
        return chamar


@pytest.mark.parametrize("img, dpi, forca", [
    (np.zeros((10, 10, 3), np.uint8), 300, "normal"),      # colorida
    (np.zeros((10, 10), np.float32), 300, "normal"),       # não é uint8
    (np.zeros((10, 10), np.uint8), 0, "normal"),           # DPI zero
    (np.zeros((10, 10), np.uint8), 29, "normal"),          # DPI abaixo do piso
    (np.zeros((10, 10), np.uint8), 2401, "normal"),        # DPI acima do teto
    (np.zeros((10, 10), np.uint8), 300, "forte"),          # força desconhecida
    (np.zeros((10, 10), np.uint8), 300, 4.0),              # força fora da faixa
    (np.zeros((0, 10), np.uint8), 300, "normal"),          # vazia
    ("nao e imagem", 300, "normal"),
])
def test_entrada_ruim_nao_chega_a_dll(img, dpi, forca):
    falsa = _BibliotecaDeMentira()
    resultado = ps.limpar_pontinhos(img, dpi, forca, biblioteca=falsa)
    assert not resultado.disponivel and resultado.motivo
    assert falsa.chamadas == 0


def test_sem_a_dll_fica_indisponivel(tmp_path):
    sem = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    img, _ = pagina_com_i()
    resultado = ps.limpar_pontinhos(img, 300, biblioteca=sem)
    assert not resultado.disponivel
    assert "não foram encontradas" in resultado.motivo


def _pagina_de_letras() -> np.ndarray:
    """Página sintética com tom de papel, letras escuras e poeira."""
    rng = np.random.default_rng(7)
    img = np.full((900, 700, 3), 225, np.uint8)
    for linha in range(10):
        for letra in range(25):
            y, x = 80 + linha * 70, 60 + letra * 24
            img[y:y + 30, x:x + 6] = 40
            img[y:y + 6, x:x + 16] = 40
    for _ in range(300):                                    # poeira
        y, x = rng.integers(0, 897), rng.integers(0, 697)
        img[y:y + 2, x:x + 2] = 60
    return img


def test_sem_a_dll_o_preto_e_branco_e_o_de_hoje(tmp_path):
    sem = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    img = _pagina_de_letras()
    binaria, resultado = ps.preto_e_branco_com_pontinhos_do_scantailor(img, 300, biblioteca=sem)
    assert not resultado.disponivel and resultado.motivo
    assert np.array_equal(binaria, F.filtro_preto_e_branco(img))


def test_o_preto_e_branco_de_hoje_nao_mudou():
    """Chamado sem escolha (despeckle=True, o padrão da função), o Preto e
    branco continua com o nosso limpar pontinhos (a mesma conta, ponto a
    ponto). No programa, quem escolhe é a página (ver
    tests/test_limpar_pontinhos_no_programa.py)."""
    img = _pagina_de_letras()
    hoje = F.filtro_preto_e_branco(img)
    sem_limpar = F.filtro_preto_e_branco(img, despeckle=False)
    assert np.array_equal(hoje, F._despeckle(sem_limpar, sem_limpar.shape[0]))


# ------------------------------------------------------------- com a DLL

@precisa_da_dll
@pytest.mark.parametrize("forca", ["pouco", "normal", "muito"])
def test_pontinho_solto_sai_letra_e_pingo_ficam(forca):
    img, onde = pagina_com_i()
    resultado = ps.limpar_pontinhos(img, 300, forca)
    assert resultado.disponivel, resultado.motivo
    saida = resultado.imagem
    assert (saida[onde["solto"]] == 255).all()
    assert (saida[onde["pingo"]] == 0).all()
    for k in range(8):
        assert (saida[onde[f"haste{k}"]] == 0).all()


@precisa_da_dll
def test_so_tira_preto_e_nao_mexe_na_entrada():
    rng = np.random.default_rng(3)
    img = np.where(rng.random((600, 500)) < 0.02, 0, 255).astype(np.uint8)
    img[100:300, 100:140] = 0
    copia = img.copy()
    for forca in ("pouco", "normal", "muito"):
        saida = ps.limpar_pontinhos(img, 300, forca).imagem
        assert set(np.unique(saida)) <= {0, 255}
        assert not ((saida == 0) & (img == 255)).any()       # nada de preto novo
    assert np.array_equal(img, copia)


@precisa_da_dll
def test_mais_forca_tira_mais():
    rng = np.random.default_rng(5)
    img = np.full((800, 800), 255, np.uint8)
    for _ in range(400):                                      # manchas de vários tamanhos
        y, x, lado = rng.integers(0, 790), rng.integers(0, 790), rng.integers(1, 9)
        img[y:y + lado, x:x + lado] = 0
    pretos = [(ps.limpar_pontinhos(img, 300, f).imagem == 0).sum() for f in ("pouco", "normal", "muito")]
    assert pretos[0] >= pretos[1] >= pretos[2]
    assert pretos[0] > pretos[2]


@precisa_da_dll
@pytest.mark.parametrize("largura", [1, 31, 32, 33, 63, 65, 401])
def test_largura_qualquer_volta_certa(largura):
    """Sem nada para limpar (só peças grandes), a imagem volta igual - em
    qualquer largura (o ScanTailor guarda 32 pontos por palavra)."""
    img = np.full((60, largura), 255, np.uint8)
    img[10:50, : max(1, largura // 2 + 1)] = 0
    img[:, -1] = 0                                            # a última coluna, pintada inteira
    saida = ps.limpar_pontinhos(img, 300, "muito").imagem
    assert np.array_equal(saida, img)


@precisa_da_dll
def test_imagem_que_nao_e_contigua():
    img, onde = pagina_com_i(largura=400)
    larga = np.full((img.shape[0], img.shape[1] * 2), 255, np.uint8)
    larga[:, ::2] = img
    vista = larga[:, ::2]                                     # mesma imagem, passo diferente
    assert not vista.flags["C_CONTIGUOUS"]
    assert np.array_equal(ps.limpar_pontinhos(vista, 300).imagem, ps.limpar_pontinhos(img, 300).imagem)


@precisa_da_dll
def test_dpi_acompanha_a_resolucao():
    """A mesma página desenhada a 600 DPI (o dobro de pontos) limpa igual à de 300."""
    a300, onde300 = pagina_com_i(300)
    a600, onde600 = pagina_com_i(600)
    for forca in ("pouco", "muito"):
        s300 = ps.limpar_pontinhos(a300, 300, forca).imagem
        s600 = ps.limpar_pontinhos(a600, 600, forca).imagem
        for nome in onde300:
            assert (s300[onde300[nome]] == 0).all() == (s600[onde600[nome]] == 0).all(), nome
    # e o DPI errado muda: a página de 600 tratada como 150 guarda o pontinho solto
    errado = ps.limpar_pontinhos(a600, 150, "pouco").imagem
    assert (errado[onde600["solto"]] == 0).all()


@precisa_da_dll
def test_preto_e_branco_com_o_do_scantailor():
    img = _pagina_de_letras()
    sem_limpar = F.filtro_preto_e_branco(img, despeckle=False)
    binaria, resultado = ps.preto_e_branco_com_pontinhos_do_scantailor(img, 300, "normal")
    assert resultado.disponivel, resultado.motivo
    assert binaria.shape == img.shape[:2] and set(np.unique(binaria)) <= {0, 255}
    assert not ((binaria == 0) & (sem_limpar == 255)).any()


@precisa_da_dll
def test_a_diferenca_para_o_nosso():
    """O que muda de verdade (medido em 06/10/2026 nesta página sintética):
    - mancha MAIOR que a do nosso (6 x 6 pontos, 36 > 8), solta no papel: o do
      ScanTailor tira, o nosso deixa;
    - poeira de 2 x 2 COLADA na letra (2 pontos de folga): o nosso tira (só
      olha o tamanho), o do ScanTailor deixa na força "pouco" (está perto da
      letra, como um pingo de "i")."""
    img = np.full((400, 600, 3), 225, np.uint8)
    for letra in range(10):
        x = 40 + letra * 24
        img[100:130, x:x + 6] = 40
        img[100:106, x:x + 16] = 40
    img[300:306, 450:456] = 40                 # mancha 6x6 longe de tudo
    img[132:134, 41:43] = 60                   # poeira 2x2 logo abaixo da 1.a letra
    nosso = F.filtro_preto_e_branco(img)
    dele, resultado = ps.preto_e_branco_com_pontinhos_do_scantailor(img, 300, "pouco")
    assert resultado.disponivel
    assert (nosso[300:306, 450:456] == 0).any() and (dele[300:306, 450:456] == 255).all()
    assert (nosso[132:134, 41:43] == 255).all() and (dele[132:134, 41:43] == 0).any()


@precisa_da_dll
def test_pode_ser_chamado_de_varias_linhas_ao_mesmo_tempo():
    """O programa processa numa QThread; o ctypes solta o GIL na chamada."""
    from concurrent.futures import ThreadPoolExecutor

    img, _ = pagina_com_i()
    esperado = ps.limpar_pontinhos(img, 300, "normal").imagem
    with ThreadPoolExecutor(4) as grupo:
        saidas = list(grupo.map(lambda _: ps.limpar_pontinhos(img, 300, "normal").imagem, range(8)))
    assert all(np.array_equal(s, esperado) for s in saidas)
