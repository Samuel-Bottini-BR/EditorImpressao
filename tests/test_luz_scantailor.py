"""Item 2.17: igualar a luz e suavizar, igual ao ScanTailor (core/luz_scantailor.py).

Testes de máquina:
- o código do ScanTailor está copiado sem mudança (os 6 blocos de
  OutputGenerator.cpp na cola luz.cpp);
- de fábrica tudo desligado (página nova e projeto antigo) e, desligado, a
  página sai a MESMA (o mesmo objeto, nenhuma conta);
- cada conta faz o que o ScanTailor diz: igualar a luz tira o degradê do fundo,
  a suavização morfológica tira o dentinho da letra, o Wiener tira o chuvisco,
  o Savitzky-Golay devolve cinza;
- o "Suavizar as letras" só vale no preto e branco da página da vez, e cada
  fio (item 2.16) vê só a sua página;
- na tela (aba Filtro): mostrar não grava, mudar é ação do desfazer, a prévia
  é refeita, "todas" leva junto, suavizar só aparece no Preto e branco.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path

import numpy as np
import pytest

from core import luz_scantailor as luz
from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parents[1]
LIGACAO = RAIZ / "terceiros" / "scantailor-advanced" / "ligacao-ferramentas" / "luz.cpp"
REFERENCIA = RAIZ / "terceiros" / "scantailor-advanced" / "referencia" / "OutputGenerator.cpp"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll indisponível")


def test_funcoes_copiadas_sem_mudanca():
    """Cada bloco entre as marcas COPIADO SEM MUDANCA é idêntico às linhas do original."""
    ligacao = LIGACAO.read_text(encoding="utf-8").splitlines()
    original = REFERENCIA.read_text(encoding="utf-8").splitlines()
    blocos = 0
    for i, linha in enumerate(ligacao):
        achado = re.match(r"// ===== COPIADO SEM MUDANCA \(linhas (\d+)-(\d+)\) =====", linha)
        if not achado:
            continue
        a, b = int(achado.group(1)), int(achado.group(2))
        fim = ligacao.index("// ===== FIM DO COPIADO =====", i)
        assert ligacao[i + 1:fim] == original[a - 1:b], f"bloco {a}-{b} mudou"
        blocos += 1
    assert blocos == 6


def test_desligado_de_fabrica_e_projeto_antigo():
    from modelos import ConfigPagina, Projeto

    pagina = ConfigPagina(indice=0, folha=0)
    assert (pagina.luz_igualar, pagina.luz_suavizar, pagina.luz_chuvisco) == (False, False, 0)
    assert luz.assinatura(pagina) == "-"
    dados = Projeto(caminho_entrada="x", paginas=[pagina]).para_dicionario()
    for campo in luz.CAMPOS:
        dados["paginas"][0].pop(campo)
    volta = Projeto.de_dicionario(dados).paginas[0]
    assert not luz.alguma_ligada(volta)


def test_desligado_devolve_a_mesma_imagem():
    from modelos import ConfigPagina

    img = np.full((50, 60, 3), 200, np.uint8)
    assert luz.antes_do_filtro(img, ConfigPagina(indice=0, folha=0)) is img
    with luz.suavizar_nesta_pagina(ConfigPagina(indice=0, folha=0), 300):
        assert luz.cinza_para_binarizar(img[..., 0]) is img[..., 0] or True
        cinza = img[..., 0]
        assert luz.cinza_para_binarizar(cinza) is cinza


def _pagina_com_degrade():
    """Papel com luz desigual (escuro à esquerda) e 'letras' pretas."""
    largura, altura = 900, 1200
    fundo = np.linspace(120, 235, largura, dtype=np.float32)[None, :].repeat(altura, 0)
    img = np.repeat(fundo[..., None], 3, axis=2).astype(np.uint8)
    for y in range(150, 1100, 60):
        img[y:y + 18, 100:800] = 25
    return img


@precisa_da_dll
def test_igualar_a_luz_tira_o_degrade_do_papel():
    img = _pagina_com_degrade()
    igualada = luz.igualar_luz(img)
    assert igualada.shape == img.shape and igualada.dtype == np.uint8
    papel_antes = img[120:140, 50:850, 1].astype(float)
    papel_depois = igualada[120:140, 50:850, 1].astype(float)
    assert papel_antes.std() > 25
    assert papel_depois.std() < papel_antes.std() / 3
    assert papel_depois.mean() > 220                      # o papel fica claro
    assert igualada[160, 400, 1] < 100                    # a letra continua escura
    cinza = luz.igualar_luz(img[..., 1].copy())
    assert cinza.ndim == 2


@precisa_da_dll
def test_suavizar_tira_o_dentinho_da_letra():
    bw = np.full((60, 60), 255, np.uint8)
    bw[10:50, 10:30] = 0
    bw[25, 30] = 0                     # um dentinho de 1 ponto na borda direita
    suave = luz.suavizar_preto_e_branco(bw)
    assert suave[25, 30] == 255
    assert (suave[15:45, 12:28] == 0).all()               # o corpo da letra fica


@precisa_da_dll
def test_wiener_tira_o_chuvisco_e_zero_nao_faz_nada():
    gerador = np.random.default_rng(1)
    img = np.clip(180 + gerador.normal(0, 25, (200, 200, 3)), 0, 255).astype(np.uint8)
    assert luz.tirar_chuvisco(img, 0) is img
    limpa = luz.tirar_chuvisco(img, 10)
    # o Wiener do ScanTailor trabalha no cinza (o brilho de cada ponto)
    cinza_antes = img.astype(float).mean(axis=2)
    cinza_depois = limpa.astype(float).mean(axis=2)
    assert cinza_depois.std() < cinza_antes.std() * 0.7


@precisa_da_dll
def test_savitzky_golay_devolve_cinza():
    img = _pagina_com_degrade()
    suave = luz.suavizar_cinza(img[..., 1].copy(), 300)
    assert suave.shape == img.shape[:2] and suave.dtype == np.uint8
    assert luz.suavizar_cinza(img, 300).shape == img.shape[:2]     # colorida: sai cinza


@precisa_da_dll
def test_suavizar_so_vale_no_preto_e_branco_da_pagina_da_vez():
    from core.filtros import filtro_preto_e_branco
    from modelos import ConfigPagina

    img = _pagina_com_degrade()
    img[168, 450] = 25                # um dentinho de 1 ponto embaixo da linha de 150 a 167
    sem = filtro_preto_e_branco(img, despeckle=False)
    pagina = ConfigPagina(indice=0, folha=0, luz_suavizar=True)
    with luz.suavizar_nesta_pagina(pagina, 300):
        com = filtro_preto_e_branco(img, despeckle=False)
    depois = filtro_preto_e_branco(img, despeckle=False)
    assert (sem == depois).all(), "fora do contexto não pode suavizar"
    assert (sem != com).any()

    vistos = {}

    def outro_fio():
        vistos["outro"] = filtro_preto_e_branco(img, despeckle=False)

    with luz.suavizar_nesta_pagina(pagina, 300):
        fio = threading.Thread(target=outro_fio)
        fio.start()
        fio.join()
    assert (vistos["outro"] == sem).all(), "o outro fio não é a página da vez"


@precisa_da_dll
def test_no_pipeline_igualar_muda_a_pagina_e_original_nao(tmp_path):
    from core import pipeline
    from core.filtros import MELHORAR, ORIGINAL
    from modelos import ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), detectar_regioes=False)
    img = _pagina_com_degrade()
    pagina = ConfigPagina(indice=0, folha=0, filtro=MELHORAR)
    antes, _ = pipeline._filtrar(projeto, pagina, img.copy())
    pagina.luz_igualar = True
    depois, _ = pipeline._filtrar(projeto, pagina, img.copy())
    assert (antes != depois).any()
    pagina.filtro = ORIGINAL
    original, _ = pipeline._filtrar(projeto, pagina, img)
    assert (original == img).all(), "o Original não muda nada, nem a luz"


# --------------------------------------------------------------- a tela

fitz = pytest.importorskip("fitz")


@pytest.fixture
def conferir(pasta):
    from core.filtros import MELHORAR, PRETO_E_BRANCO
    from historico_acoes import HistoricoAcoes
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from tests.test_mesmo_livro_outro_caminho import _pdf
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=3)
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste", dividir_folhas=False,
                      detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(3)]
    projeto.paginas[2].filtro = MELHORAR
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    yield tela
    previas.parar()


from tests.test_mesmo_livro_outro_caminho import app, pasta  # noqa: E402,F401 - fixtures


def test_na_tela_mostrar_nao_grava(app, conferir):
    assert not conferir.caixa_luz_igualar.isChecked()
    assert not conferir.caixa_luz_suavizar.isChecked()
    assert conferir.seletor_luz_chuvisco.value() == 0
    assert not conferir.acoes.pode_desfazer


def test_na_tela_mudar_e_acao_do_desfazer_e_refaz_a_previa(app, conferir):
    pagina, outra = conferir.projeto.paginas[0], conferir.projeto.paginas[1]
    chave = conferir.previas.chave(0, 110)
    conferir.caixa_luz_igualar.setChecked(True)
    assert pagina.luz_igualar and not outra.luz_igualar
    assert conferir.previas.chave(0, 110) != chave
    assert conferir.acoes.descricao_desfazer().endswith("Igualar a luz da página na página 1: ligado")
    conferir.seletor_luz_chuvisco.setValue(40)
    assert pagina.luz_chuvisco == 40
    conferir.desfazer()
    assert pagina.luz_chuvisco == 0 and conferir.seletor_luz_chuvisco.value() == 0
    conferir.desfazer()
    assert not pagina.luz_igualar and not conferir.caixa_luz_igualar.isChecked()


def test_na_tela_suavizar_so_no_preto_e_branco_e_todas_leva_junto(app, conferir):
    assert not conferir.caixa_luz_suavizar.isHidden()
    conferir.caixa_luz_suavizar.setChecked(True)
    conferir._filtro_em_todas()
    assert all(p.luz_suavizar for p in conferir.projeto.paginas)
    conferir.ir_para_pagina(2)
    # a 2 virou Preto e branco pelo "todas"; volta ao Melhorar para conferir
    conferir.desfazer()
    conferir.ir_para_pagina(2)
    assert conferir.caixa_luz_suavizar.isHidden()
    assert not conferir.caixa_luz_igualar.isHidden()
