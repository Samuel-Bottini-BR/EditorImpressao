"""Obra de 26/10/2026, etapa 10b: defeitos na imagem final (testes de reversão;
CLAUDE.md §4.7: "um defeito consertado nunca volta escondido, nem os de imagem").

Cada teste diz o defeito, de onde veio (lista única de 23/10/2026, seção 4; Lista
de bugs; Livro de decisões) e uma MEDIDA que pega o defeito. Todos falham no
código de antes (ab38208, worktree `obra-etapa10b-antes`) e passam no novo - a
conta de cada um, antes e depois, está no `relatorios/obra-etapa10b/ONDE-PAREI.md`.

Dois tipos:
  - páginas de verdade, pelo caminho inteiro do programa (livro NOVO de fábrica:
    core.pipeline.analisar_projeto e o mesmo corpo do processar,
    core.pipeline._pagina_pronta; regra de 21/10): só no PC do Samuel (o acervo,
    "Livros para editar" e o projeto salvo do teste dos 14 livros ficam fora do
    git; sem eles, pulam);
  - páginas sintéticas, que rodam em qualquer lugar (GitHub), para a regra que
    mudou (o mesmo defeito, desenhado).
Regra de 21/10: nenhuma página é lombada nem capa de couro.
"""

from __future__ import annotations

import json
import zlib
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

from core import filtros as F
from core.selecao import AUTOMATICO, GRAVURA, LETRA, RETANGULO, Regiao, Selecao

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
TESTES_DOS_LIVROS = Path(r"D:\programas\EditorImpressao-arquivos\testes-livros-saida")
LIVROS = {
    "boecio": "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
    "matematica": "Matemática Para vencer.pdf",
    "palatino": "Giovambattista Palatino cittadino romano.pdf",
    "pesel": "POINTS d´ANCIENNES BRODERIES ANGLAISES - Louisa F. Pesel.pdf",
    "valades": "Rhetorica Christiana -  Fray Diego Valadés.pdf",
    "antiphon": "Antiphon_25.pdf",
}
OUTROS = {
    "antiphonal1547": Path("D:/Livros para editar/Antiphonal 1547.pdf"),
    "atanasio": Path("D:/Livros para editar/2 - TEOLOGIA/Patrologia/Patrística/"
                     "aula_18_atanasio_de_alexandria_e_a_controversia_ar.pdf"),
}
GABARITO = Path(__file__).resolve().parents[1] / "gabarito" / "paginas"


# --- ajudantes ----------------------------------------------------------------

def _precisa(caminho: Path) -> None:
    if not caminho.exists():
        pytest.skip(f"sem {caminho} (só no PC do Samuel)")


def _precisa_da_dll() -> None:
    from core import st_ferramentas

    if st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None:
        pytest.skip("sem a DLL do ScanTailor")


def _limpar_guardados() -> None:
    from core import pipeline

    for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()


def _livro_novo(tmp_path: Path, origem: Path, numero: int, **campos):
    """Livro novo de fábrica com só a página `numero` de `origem` (cópia numa
    pasta temporária; a origem é só lida)."""
    from core import pipeline
    from modelos import Projeto

    _precisa(origem)
    _limpar_guardados()
    destino = tmp_path / f"p{numero:03d}.pdf"
    with fitz.open(str(origem)) as doc:
        um = fitz.open()
        um.insert_pdf(doc, from_page=numero - 1, to_page=numero - 1)
        um.save(str(destino))
        um.close()
    projeto = Projeto(caminho_entrada=str(destino), caminho_saida=str(tmp_path / "saida.pdf"),
                      nome=destino.stem)
    for chave, valor in campos.items():
        setattr(projeto, chave, valor)
    return pipeline.analisar_projeto(projeto)


def _pronta(projeto, filtro: str, **da_pagina):
    """(a página pronta como vai para o PDF, a pagina) com `filtro`."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    pagina = projeto.paginas_ativas[0]
    pagina.filtro = filtro
    for chave, valor in da_pagina.items():
        setattr(pagina, chave, valor)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _mono = pipeline._pagina_pronta(projeto, doc, projeto.folhas[pagina.folha], pagina,
                                             pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    return img


def _do_acervo(tmp_path, livro: str, numero: int, filtro: str, **campos):
    """(original, com o filtro) da página do acervo como livro novo."""
    _precisa_da_dll()
    projeto = _livro_novo(tmp_path, ACERVO / LIVROS[livro], numero, **campos)
    return _pronta(projeto, F.ORIGINAL), _pronta(projeto, filtro)


def _cinza(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img


def _projeto_do_teste(livro: str, pdf: str):
    """O projeto salvo do teste dos 14 livros (23/10/2026), apontando para a
    cópia do PDF (só leitura)."""
    from modelos import Projeto

    base = TESTES_DOS_LIVROS / livro / "trab"
    pasta = base / "projetos" / Path(pdf).stem
    _precisa(pasta / "projeto.json")
    _limpar_guardados()
    projeto = Projeto.de_dicionario(json.loads((pasta / "projeto.json").read_text(encoding="utf-8")))
    projeto.caminho_entrada = str(base / pdf)
    return projeto


def _pagina_do_teste(projeto, numero: int, filtro: str):
    from core import pipeline
    from core.pdf_io import abrir_pdf

    pagina = next(p for p in projeto.paginas if p.folha == numero - 1 and not p.apagada)
    pagina.filtro = filtro
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = pipeline._pagina_pronta(projeto, doc, projeto.folhas[pagina.folha], pagina,
                                         pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    return img


# --- 4.1 gravura estragada no Preto e branco ------------------------------------

def _preto_chapado_sem_tinta_cheia(original: np.ndarray, pb: np.ndarray) -> float:
    """A fração da página que é BLOCO preto (sobra da abertura por um disco de 9
    pontos) onde o original NÃO é tinta cheia (o cinza alisado passa de 60% do
    papel): o "traço fino virou áreas pretas chapadas" do 4.1."""
    cinza = cv2.GaussianBlur(_cinza(original), (0, 0), 1.0)
    papel = np.percentile(cinza[::4, ::4], 85)
    preto = (_cinza(pb) < 128).astype(np.uint8)
    bloco = cv2.morphologyEx(preto, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
    return float((bloco & (cinza >= 0.6 * papel)).mean())


@pytest.mark.parametrize("livro,numero", [("palatino", 74), ("valades", 41)])
def test_reversao_4_1_gravura_nao_vira_bloco_preto(tmp_path, livro, numero):
    """Lista única 4.1 (23/10/2026, P-1 e V-1): "No Palatino 74 [...] o fundo
    virou chuvisco preto e branco com manchas pretas grandes; no Valadés 41
    [...] o traço fino virou áreas pretas chapadas e os rostos perderam
    detalhe". Causa: no desenho de 1 bit a mancha escura pequena era enchida de
    preto inteira (core.filtros.DESENHO_TINTA_CHEIA). Medido: 1,4% (Palatino 74)
    e 2,0% (Valadés 41) da página em bloco preto sem tinta cheia; agora < 0,2%."""
    original, pb = _do_acervo(tmp_path, livro, numero, F.PRETO_E_BRANCO)
    assert _preto_chapado_sem_tinta_cheia(original, pb) < 0.002


def test_4_1_hachura_sintetica_nao_vira_bloco():
    """O mesmo defeito, desenhado: hachura fechada (riscos de 2 pontos, cinza
    70, com o vão de 2 pontos borrado, cinza 130, contra papel 200 - o Valadés
    41) numa mancha pequena de uma gravura de traço. Antes a mancha saía preta
    inteira; agora o vão entre os riscos fica branco."""
    img = np.full((600, 600, 3), 200, np.uint8)
    img[250:290, 250:290] = 130                        # o vão da hachura, borrado no scan
    for y in range(250, 290, 4):
        img[y:y + 2, 250:290] = 70                     # hachura 40 x 40
    img[100:110, 100:500] = 60                         # um traço comprido
    feito = F._desenho_em_preto_e_branco(img, 200.0, 600)
    miolo = feito[254:286, 254:286]
    assert 0.25 < float((miolo == 0).mean()) < 0.75


def test_4_1_nota_quadrada_cheia_continua_cheia():
    """A regra antiga continua: a nota quadrada larga (tinta de ponta a ponta)
    sai cheia (Graduale 222; tests/test_preto_e_branco_regra_30_09.py)."""
    img = np.full((600, 600, 3), 200, np.uint8)
    img[300:340, 300:340] = 50
    feito = F._desenho_em_preto_e_branco(img, 200.0, 600)
    assert float((feito[305:335, 305:335] == 0).mean()) > 0.95


# --- 4.3 folha branca sai cinza e manchada -----------------------------------------

def test_reversao_4_3_folha_de_guarda_sai_branca(tmp_path):
    """Lista única 4.3 (B-2): "Uma folha de guarda branca sai cinza e toda
    manchada: a textura e as rugas do papel viram desenho (Boécio 49, Marial
    2)". Causa: a folha sem tinta tomada por objeto ("capa") vira foto em cinza
    com os níveis esticados do mais escuro ao mais claro DELA. Medido no Boécio
    49: mediana 189 e 65% da página abaixo de 200; agora segue o papel."""
    _, pb = _do_acervo(tmp_path, "boecio", 49, F.PRETO_E_BRANCO)
    cinza = _cinza(pb)
    assert float(np.median(cinza)) >= 225
    assert float((cinza < 200).mean()) < 0.20


def test_4_3_capa_sintetica_segue_o_papel():
    """A mesma regra, desenhada: folha quase lisa (215 a 235, com rugas) e um
    carimbo escuro. Com os níveis da "capa" (core.filtros._niveis_da_capa) o
    papel sai claro e o carimbo continua escuro; com os níveis de antes (os da
    foto, esticados do mais escuro ao mais claro da folha) a ruga virava
    mancha."""
    rng = np.random.default_rng(3)
    img = (225 + rng.normal(0, 5, (400, 300))).clip(0, 255).astype(np.uint8)
    img = cv2.GaussianBlur(img, (0, 0), 3)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.circle(img, (150, 200), 40, (60, 60, 60), 4)          # o carimbo
    saida = F._foto_em_tons_de_cinza(img, F._niveis_da_capa(img))
    papel = saida[20:120, 20:280]
    assert float(np.median(papel)) >= 235
    assert float(papel.std()) < 8                             # sem a ruga virar mancha
    assert float(saida[195:205, 108:114].min()) < 120         # o traço do carimbo
    antes = F._foto_em_tons_de_cinza(img, F._niveis_da_foto(img))
    assert float(antes[20:120, 20:280].std()) > float(papel.std())


# --- Matemática 40 e 66: a sombra da lombada ----------------------------------------

def test_reversao_matematica_66_a_sombra_da_lombada_nao_vira_faixa_preta(tmp_path):
    """Lista única 4.2 (M-1), Matemática 66: "cada número de questão [...] virou
    borrão preto" (etapa 10a: o corte está certo; quem apaga é o Preto e
    branco). Causa: o Otsu (um limiar só para a página) pinta de preto a sombra
    da lombada. Medido: 4,7% da faixa da esquerda (7% da largura) preta; agora
    < 1%."""
    _, pb = _do_acervo(tmp_path, "matematica", 66, F.PRETO_E_BRANCO)
    preto = _cinza(pb) < 128
    h, w = preto.shape
    assert float(preto[int(.05 * h):int(.95 * h), :int(.07 * w)].mean()) < 0.01


def test_reversao_matematica_40_as_primeiras_letras_ficam():
    """Lista única 4.2 (M-2), Matemática 40: "as primeiras letras de cada linha,
    perto da lombada, sumiram ('Suponha que' -> '~cha que')". Causa: a letra
    borrada na sombra é "fundo" para o Sauvola. Medida (o projeto do teste de
    23/10): a tinta na faixa da sombra, metade de cima: 7,1% antes, 13% agora."""
    projeto = _projeto_do_teste("matematica", "matematica.pdf")
    original = _cinza(_pagina_do_teste(projeto, 40, F.ORIGINAL))
    pb = _cinza(_pagina_do_teste(projeto, 40, F.PRETO_E_BRANCO))
    achada = F._faixa_da_sombra_da_lombada(original)
    assert achada is not None
    _luz, faixa = achada
    h = pb.shape[0]
    assert float((pb[int(.03 * h):int(.6 * h)][:, faixa] < 128).mean()) >= 0.10


def test_sombra_sintetica_na_beirada_nao_vira_faixa_preta():
    """Desenhado: página com sombra de lombada na esquerda (papel de 135 subindo
    para 245 em 12% da largura) e linhas de texto (cinza 90) que entram na
    sombra. Com o Otsu, antes a sombra saía preta; agora não, e as letras dela
    ficam."""
    h, w = 900, 700
    luz = np.ones(w, np.float32)
    rampa = int(0.12 * w)
    luz[:rampa] = np.linspace(0.55, 1.0, rampa)
    img = np.full((h, w), 245, np.float32) * luz[None, :]
    letras = np.zeros((h, w), bool)
    for y in range(80, 860, 40):
        for x in range(20, 660, 26):
            img[y:y + 14, x:x + 14] *= 0.37                    # "letras" (impressão gasta)
            letras[y + 2:y + 12, x + 2:x + 12] = True
    img = cv2.cvtColor(img.clip(0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    pb = F.filtro_preto_e_branco(img, algoritmo=F.ALGORITMO_OTSU, despeckle=False)
    linhas = np.arange(h)
    entre_as_letras = (linhas >= 60) & (linhas < 860) & ((linhas % 40) >= 20) & ((linhas % 40) < 38)
    papel_sem_letra = pb[entre_as_letras][:, :rampa]
    assert float((papel_sem_letra == 0).mean()) < 0.02          # sombra não pintada
    na_sombra = letras.copy()
    na_sombra[:, rampa:] = False
    assert float((pb[na_sombra] == 0).mean()) > 0.9             # letra na sombra fica


def test_pagina_sem_sombra_sai_igual():
    """Sem sombra, o preto e branco é o MESMO de antes, ponto a ponto."""
    rng = np.random.default_rng(1)
    img = np.full((600, 500), 240, np.uint8)
    for y in range(50, 560, 30):
        img[y:y + 10, 40:460] = rng.integers(20, 80)
    binaria = F.binarizar(img, algoritmo=F.ALGORITMO_SAUVOLA, k=0.2)
    assert F._sem_a_sombra_da_lombada(img, binaria) is binaria


def test_reversao_foto_de_celular_a_sombra_da_mao_nao_vira_mancha(tmp_path):
    """Lista de bugs (23/10/2026): "Páginas fotografadas (celular): o Preto e
    branco transforma a sombra da mão ou da página numa grande mancha preta"
    (Atanásio 8). Medida: a fração da página em bloco preto (abertura por um
    disco de 15 pontos)."""
    _precisa_da_dll()
    projeto = _livro_novo(tmp_path, OUTROS["atanasio"], 8)
    pb = _pronta(projeto, F.PRETO_E_BRANCO)
    preto = (_cinza(pb) < 128).astype(np.uint8)
    bloco = cv2.morphologyEx(preto, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    assert float(bloco.mean()) < 0.01


# --- 4.5 PDF (desfeito na 9d: D-304, sem perda) ------------------------------------------------------------

def _pagina_de_tons(semente: int = 5) -> np.ndarray:
    """Papel creme com o grão do scan (ruído), uma faixa colorida e "letras":
    o que faz o PDF sem perda ficar enorme."""
    rng = np.random.default_rng(semente)
    img = np.full((1600, 1100, 3), (200, 225, 238), np.float32)
    img += rng.normal(0, 6, img.shape)
    img[200:260, 100:1000] = (40, 40, 180)                     # título vermelho
    for y in range(400, 1500, 40):
        img[y:y + 18, 100:1000] *= 0.3
    return img.clip(0, 255).astype(np.uint8)


def test_d304_pagina_de_tons_vai_sem_perda(tmp_path):
    """D-304 (Samuel, P3, 01/10/2026): "Eu quero ter a opção 1.6, mas eu quero
    poder deixar como está também, o tamanho do arquivo depois não importa".

    A etapa 10b tinha passado a gravar a página de tons (cor e cinza) em JPEG
    92 para o PDF ficar menor (lista única 4.5); a ordem do Samuel de
    27/10/2026 ("os agentes estão mudando coisas que eu já tinha definido, é
    só para fazer o que eu já tinha mandado") desfez isso na etapa 9d: a
    página de tons volta a ir SEM PERDA (zlib, /FlateDecode), com os mesmos
    pixels que entraram. Este teste falha no código da 10b (JPEG)."""
    from core.pdf_io import EscritorPDF

    img = _pagina_de_tons()
    with EscritorPDF(tmp_path / "x.pdf") as escritor:
        escritor.escrever_imagem(img, dpi=300)
    with fitz.open(str(tmp_path / "x.pdf")) as doc:
        xref = doc[0].get_images()[0][0]
        assert doc.xref_get_key(xref, "Filter") == ("name", "/FlateDecode")
        pix = fitz.Pixmap(doc, xref)
        lida = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)[..., ::-1]
    assert np.array_equal(lida, img), "a página de tons devia sair no PDF ponto a ponto igual"


def test_4_5_preto_e_branco_de_1_bit_continua_sem_perda(tmp_path):
    """O Preto e branco puro continua em 1 bit sem perda (os pixels lidos são
    os mesmos)."""
    from core.pdf_io import EscritorPDF

    img = np.where(_cinza(_pagina_de_tons()) > 128, 255, 0).astype(np.uint8)
    with EscritorPDF(tmp_path / "x.pdf") as escritor:
        escritor.escrever_imagem(img, dpi=300, monocromatico=True)
    with fitz.open(str(tmp_path / "x.pdf")) as doc:
        xref = doc[0].get_images()[0][0]
        assert doc.xref_get_key(xref, "Filter") == ("name", "/FlateDecode")
        pix = fitz.Pixmap(doc, xref)
        lida = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    assert np.array_equal(np.where(lida > 127, 255, 0), img)


# --- 4.7 retângulos brancos no cartão da Pesel ----------------------------------------

def test_reversao_4_7_cartao_da_pesel_sem_retangulo_branco(tmp_path):
    """Lista única 4.7 (PE-1): "o cartão marrom em volta virou um remendo: o
    título e cada bloco de texto ganharam um retângulo branco por cima, com a
    letra engrossada, e sobrou uma tira branca torta na beirada esquerda"
    (Pesel 51, Mágico pro). Medida: a fração do CARTÃO (fundo do original abaixo
    de 140) que sai branca: 32% antes; agora < 10%."""
    original, magico = _do_acervo(tmp_path, "pesel", 51, F.MAGICO_PRO)
    fundo = cv2.GaussianBlur(_cinza(original), (0, 0), 25)
    cartao = fundo < 140
    branco = magico.min(axis=2) >= 240
    assert float((branco & cartao).sum() / max(1, cartao.sum())) < 0.10


# --- 4.11 mancha vira ponto preto --------------------------------------------------------

def test_reversao_4_11_mancha_redonda_nao_vira_disco_preto(tmp_path):
    """Lista única 4.11 (V-2): "Valadés 203: uma mancha marrom pequena em cima de
    uma palavra virou um ponto preto em cima de 'Idiomate'". Causa: a mancha
    passava pela regra da "letra colorida sai preta". Medida: a fração preta no
    quadrado da mancha: 93% antes; agora < 70% (fica só a letra e o miolo
    escuro como tinta)."""
    original, pb = _do_acervo(tmp_path, "valades", 203, F.PRETO_E_BRANCO)
    lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB).astype(np.float32)
    croma = cv2.GaussianBlur(np.hypot(lab[..., 1] - 128, lab[..., 2] - 128), (0, 0), 5)
    h = croma.shape[0]
    croma[int(.9 * h):] = 0
    y, x = np.unravel_index(int(np.argmax(croma)), croma.shape)
    r = int(0.008 * h)
    assert float((_cinza(pb)[y - r:y + r, x - r:x + r] < 128).mean()) < 0.70


def test_4_11_mancha_sintetica_e_letra_colorida():
    """Desenhado: um disco cor de ferrugem (mancha) e uma letra vermelha (traço)
    no mesmo papel creme. A letra vermelha continua preta (regra V1 de 30/09);
    a mancha não vira disco preto."""
    img = np.full((800, 600, 3), (205, 228, 240), np.uint8)
    cv2.circle(img, (200, 300), 14, (60, 120, 200), -1)          # mancha de ferrugem
    cv2.putText(img, "ABC", (300, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, (40, 40, 200), 6)
    branca = np.full(img.shape[:2], 255, np.uint8)
    saida = F._com_a_tinta_colorida(img, branca)
    assert float((saida[290:310, 190:210] == 0).mean()) < 0.2     # mancha
    assert int((saida[430:520, 300:520] == 0).sum()) > 500        # letra vermelha


# --- 4.12 pontinhos laranja na margem ---------------------------------------------------

def _pontinhos_laranja(img: np.ndarray) -> int:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    laranja = ((hsv[..., 0] >= 8) & (hsv[..., 0] <= 30) & (hsv[..., 1] >= 50)
               & (hsv[..., 2] >= 120)).astype(np.uint8)
    _n, _r, caixas, _c = cv2.connectedComponentsWithStats(laranja, 8)
    return int(((caixas[1:, 4] >= 4) & (caixas[1:, 4] < 600)).sum())


def test_reversao_4_12_pontinhos_laranja_na_margem(tmp_path):
    """Lista única 4.12 (A-5): "Antiphon 56: sobraram pontinhos laranja das
    manchas do pergaminho na margem da direita" (Mágico pro). Medida: os
    pontinhos laranja (4 a 600 pontos) nos 15% da direita: 2.656 antes; agora
    menos de 400."""
    _original, magico = _do_acervo(tmp_path, "antiphon", 56, F.MAGICO_PRO)
    w = magico.shape[1]
    assert _pontinhos_laranja(magico[:, int(.85 * w):]) < 400


def test_4_12_grao_sintetico_no_bloco_de_letra():
    """Desenhado: bloco de letra (marcado) com letras pretas e grão laranja
    claro do pergaminho entre elas. No Mágico pro o grão vai a branco; as
    letras ficam."""
    rng = np.random.default_rng(9)
    img = np.full((900, 700, 3), (190, 222, 236), np.uint8)
    for y in range(140, 800, 60):
        cv2.putText(img, "Quam magna multitudo", (70, y), cv2.FONT_HERSHEY_SIMPLEX, 1.3,
                    (30, 30, 35), 3, cv2.LINE_AA)
    letras_antes = int((_cinza(img) < 100).sum())
    for _ in range(300):
        y, x = int(rng.integers(150, 790)), int(rng.integers(70, 640))
        if (y - 140) % 60 > 25:
            cv2.circle(img, (x, y), 2, (90, 150, 215), -1)       # grão laranja
    sel = Selecao()
    sel.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[(0.05, 0.05), (0.95, 0.95)],
                           origem=AUTOMATICO, rotulo="letra"))
    saida, _ = F.aplicar_filtro_com_selecao(img, F.MAGICO_PRO, sel)
    assert _pontinhos_laranja(saida) < 80
    assert int((_cinza(saida) < 100).sum()) > 0.8 * letras_antes


# --- a letra T do Antiphonal 46 (tela e PDF da mesma conta) ------------------------------

def test_reversao_t_do_antiphonal_46_sai_no_pdf_como_na_tela(tmp_path):
    """Lista de bugs, 13/10/2026 (grave): "No 'Só as letras', a tela mostra o
    que o PDF não tem: o cartão do filtro e o 'Ver de perto' mostram a letra T
    do Antiphonal 46 inteira; no PDF gerado pela janela ela sumiu" (D-473: "Tela
    e PDF saem da mesma conta"). Causa: a "tinta forte" era medida no cinza da
    resolução de cada desenho. Medida: a tinta da caixa da T no PDF (300 DPI) e
    na prévia (110 DPI): antes 3% contra 12%; agora 11% e 12%."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    _precisa_da_dll()
    projeto = _livro_novo(tmp_path, OUTROS["antiphonal1547"], 46, misto_so_as_letras=True,
                          filtro_padrao=F.PRETO_E_BRANCO)
    pdf = _cinza(_pronta(projeto, F.PRETO_E_BRANCO))
    pagina = projeto.paginas_ativas[0]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        previa, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=pipeline.DPI_PREVIA)
    finally:
        doc.close()
    previa = cv2.resize(_cinza(previa), (pdf.shape[1], pdf.shape[0]), interpolation=cv2.INTER_AREA)

    def tinta_da_t(img):
        h, w = img.shape
        return float((img[int(.27 * h):int(.36 * h), int(.03 * w):int(.11 * w)] < 128).mean())

    assert tinta_da_t(pdf) > 0.07
    assert abs(tinta_da_t(pdf) - tinta_da_t(previa)) < 0.04


def test_tinta_forte_e_medida_na_escala_da_linha():
    """A conta da "tinta forte" do Misto não depende da resolução: a mesma
    página desenhada grande (como o PDF) e reduzida (como a prévia, 1/2,7) dá
    a mesma resposta para uma letra grande e vermelha (o escuro dela, 75, fica
    mais claro que o miolo da letra do texto, 30). Antes, no tamanho grande a
    letra grande ia embora."""
    from core import misto

    h, w = 1620, 1350
    grande = np.full((h, w), 230, np.uint8)
    linhas = np.zeros((h, w), bool)
    for y in range(800, 1500, 80):
        for x in range(100, 1250, 22):
            grande[y:y + 27, x:x + 8] = 30                       # traços das letras
        linhas[y - 5:y + 35, :] = True
    grande[160:430, 160:430] = 75                                 # a letra grande vermelha
    grande[160:200, 120:470] = 75
    grande = cv2.GaussianBlur(grande, (0, 0), 1.2)

    def guarda_a_letra(img, linhas_aqui, altura):
        _, binaria = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
        saida = misto._fora_do_texto(binaria, img, linhas_aqui, altura, misto.FORA_REDE,
                                     np.ones(img.shape, bool))
        a, b = img.shape[0], img.shape[1]
        t = saida[int(.12 * a):int(.25 * a), int(.13 * b):int(.30 * b)]
        return float((t == 0).mean())

    pequena = cv2.resize(grande, (w * 10 // 27, h * 10 // 27), interpolation=cv2.INTER_AREA)
    linhas_p = cv2.resize(linhas.astype(np.uint8), (pequena.shape[1], pequena.shape[0]),
                          interpolation=cv2.INTER_NEAREST) > 0
    assert guarda_a_letra(grande, linhas, 40.0) > 0.9
    assert guarda_a_letra(pequena, linhas_p, 40.0 * 10 / 27) > 0.9


# --- lu-tc-igual / D-193: a tela cheia com a letra do PDF ----------------------------------

@pytest.mark.parametrize("jeito", ["st_otsu", "st_wolf"])
def test_reversao_d193_tela_cheia_com_a_mesma_tinta_do_pdf(tmp_path, jeito):
    """D-193 (22/10/2026, `lu-tc-igual`): "O pdf está saindo diferente da tela
    gerada, na tela gerada a letra está mais grossa, isso é um perigo". Causa:
    os jeitos do ScanTailor fazem a conta pelo DPI da imagem, e a tela cheia
    (150 DPI) saía 10 a 17% mais grossa que o PDF (300). Medida (Boécio 22): a
    tinta da tela cheia sobre a do PDF reduzido ao mesmo tamanho: 1,17 antes;
    agora entre 0,85 e 1,08."""
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    _precisa_da_dll()
    entrada = GABARITO / "boecio_p022.pdf"
    _precisa(entrada)
    _limpar_guardados()
    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(entrada), nome="b22",
                                                caminho_saida=str(tmp_path / "s.pdf")))
    pagina = projeto.paginas_ativas[0]
    pagina.filtro = F.PRETO_E_BRANCO
    pagina.algoritmo_preto_branco = jeito
    doc = abrir_pdf(str(entrada))
    try:
        tela, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=150)
        pdf, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    reduzido = cv2.resize(_cinza(pdf), (tela.shape[1], tela.shape[0]), interpolation=cv2.INTER_AREA)
    razao = float((255 - _cinza(tela).astype(np.float64)).mean()
                  / max(1e-6, (255 - reduzido.astype(np.float64)).mean()))
    assert 0.85 <= razao <= 1.08


# --- D-189: "Reduzir cores" não apaga parte da letra ---------------------------------------

def test_reversao_d189_reduzir_cores_nao_apaga_meia_palavra(tmp_path):
    """D-189 (21/10/2026, `211-reduzir`): "Ele está apagando as letras" (Horas 26,
    "S. Leonard", "Theodore": metade da palavra preta e metade clara). Causa: o
    "forçar preto e branco" da posterização joga a cor mais escura das letras no
    preto. Medida: a fração das letras (com a cor delas) que vira PRETO com o
    "Reduzir cores": 20% antes; agora < 2%."""
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    _precisa_da_dll()
    entrada = GABARITO / "horas_p026.pdf"
    _precisa(entrada)
    _limpar_guardados()
    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(entrada), nome="h26",
                                                caminho_saida=str(tmp_path / "s.pdf")))
    com_cor = _pronta(projeto, F.PRETO_E_BRANCO, letras_com_a_cor=True)
    reduzida = _pronta(projeto, F.PRETO_E_BRANCO, letras_com_a_cor=True, reduzir_cores=True)
    luz_a = cv2.cvtColor(com_cor, cv2.COLOR_BGR2LAB)[..., 0].astype(int)
    luz_b = cv2.cvtColor(reduzida, cv2.COLOR_BGR2LAB)[..., 0].astype(int)
    letras = luz_a < 200
    assert float((luz_b[letras] < 20).mean()) < 0.02
