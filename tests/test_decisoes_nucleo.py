"""Provas de comportamento dos consertos de núcleo da etapa 9c da obra
(26/10/2026; CLAUDE.md §11, regra 4: "Cada decisão tem uma prova de
comportamento"). Cada teste diz a decisão (ou o defeito) e falha no código de
antes do conserto (teste de reversão, regras de 19/10).

Itens:
  1. D-027 / D-227 (promessas P-078 e P-075): "Deixar a folha em branco" e
     "pintar de branco" chegam ao PDF numa página em Original, com e sem
     "Limpar a folha". Antes o Original devolvia a página como veio e o papel
     marcado à mão era ignorado.
  2. nome do arquivo de saída sem acento (modelos.nome_de_saida_sugerido).
  3. projeto.json ilegível: a cópia estragada fica guardada e a tela recebe um
     sinal para avisar (projetos.py).
  4. "Parece em branco" falso em página com texto (core/analise.py).
  5. "Endireitar: as contas discordam" em página reta (core/analise.py).
  6. textos do núcleo que aparecem na tela (plural, acento, "aba", D-479).
  7. "Menor que o corte" com os dois números iguais.

Páginas sintéticas de propósito onde a medida é de lugar e de cor (onde o
bloco preto foi parar, se o papel saiu branco); cada teste de PDF passa pelo
caminho inteiro do core.pipeline.processar (o mesmo do "Confirmar e
processar").
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

from core.filtros import ORIGINAL
from core.pipeline import processar
from core.selecao import AUTOMATICO, MAO, PAPEL, RETANGULO, Regiao, Selecao
from modelos import ConfigFolha, ConfigPagina, Projeto

DPI = 150
LARGURA_PX, ALTURA_PX = 600, 840
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- ajudantes ----------------------------------------------------------------

def _pagina_de_teste() -> np.ndarray:
    """Papel amarelado com um bloco preto (o "texto") e uma linha preta."""
    img = np.full((ALTURA_PX, LARGURA_PX, 3), AMARELADO, np.uint8)
    img[300:500, 80:280] = 0
    img[650:660, 100:500] = 0
    return img


def _pdf(caminho, img: np.ndarray) -> None:
    ok, buffer = cv2.imencode(".png", img)
    assert ok
    doc = fitz.open()
    largura_pt, altura_pt = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
    pagina = doc.new_page(width=largura_pt, height=altura_pt)
    pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()


def _projeto(tmp_path, nome="saida", limpar=False) -> Projeto:
    """Livro de uma página em Original; `limpar` = a caixinha "Limpar a folha"."""
    entrada = tmp_path / "entrada.pdf"
    if not entrada.exists():
        _pdf(entrada, _pagina_de_teste())
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(tmp_path / f"{nome}.pdf"),
                      nome="teste")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = False
    projeto.limpar = limpar
    projeto.detectar_regioes = False
    projeto.montar_cadernos = False
    projeto.filtro_padrao = ORIGINAL
    projeto.qualidade_dpi = DPI
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)]
    return projeto


def _gerar(projeto: Projeto) -> np.ndarray:
    caminho = processar(projeto)
    with fitz.open(caminho) as doc:
        assert len(doc) == 1, "a página tem de continuar no livro (mesmo lugar)"
        pix = doc[0].get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        return img.copy()


def _marcar(projeto: Projeto, x0, y0, x1, y1, origem=MAO) -> None:
    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                               origem=origem))
    projeto.paginas[0].guardar_selecao(selecao)


def _amarelado(trecho: np.ndarray) -> bool:
    return bool(np.abs(trecho.astype(int) - np.array(AMARELADO[::-1])).max() <= 8)


# --- item 1: "Deixar a folha em branco" e "pintar de branco" no Original ------

@pytest.mark.parametrize("limpar", [True, False], ids=["com_limpar_a_folha", "sem_limpar_a_folha"])
def test_d027_folha_em_branco_no_original_sai_branca(tmp_path, limpar):
    """D-027 (30/09/2026): "essa é uma página que eu poderia simplesmente
    escolher a opção para virar uma folha branca". Promessa P-078. O menu
    Marcar > "Deixar a folha em branco" marca a folha inteira como papel, à mão
    (ui/tela_conferir._folha_em_branco). Página em Original (a de fábrica,
    D-134): o PDF sai com a folha toda branca, no mesmo lugar.

    Defeito B da bateria de promessas (26/10/2026): em Original a página saía
    com tudo, amarelada, mesmo com "Limpar a folha" marcada - o Original
    devolvia a página como veio (core.filtros.aplicar_filtro_com_selecao) e o
    papel marcado à mão era ignorado."""
    projeto = _projeto(tmp_path, limpar=limpar)
    _marcar(projeto, 0.0, 0.0, 1.0, 1.0)
    img = _gerar(projeto)
    assert img.min() >= 250, f"a folha devia sair toda branca (mínimo {img.min()})"


@pytest.mark.parametrize("limpar", [True, False], ids=["com_limpar_a_folha", "sem_limpar_a_folha"])
def test_d227_pintar_de_branco_no_original_sai_branco_so_na_area(tmp_path, limpar):
    """D-227: "clicar numa área laranja e 'pintar de branco' → no PDF sai
    branca". Promessa P-075. A área pintada (em volta do bloco preto) sai
    branca; o resto da página continua como veio (Original): a linha preta
    embaixo e o papel amarelado."""
    projeto = _projeto(tmp_path, limpar=limpar)
    _marcar(projeto, 0.10, 0.33, 0.50, 0.62)        # cobre o bloco (80..280 x 300..500)
    img = _gerar(projeto)
    assert img[310:490, 90:270].min() >= 250, "a área pintada de branco não saiu branca"
    assert img[652:658, 120:480].max() < 60, "a linha preta fora da área sumiu"
    assert _amarelado(img[40:200, 350:550]), "o papel fora da área mudou (devia ficar como veio)"


def test_papel_que_a_maquina_marcou_nao_branqueia_o_original(tmp_path):
    """O outro lado: o papel que a MÁQUINA marcou (a detecção, origem
    automática) não vale no Original - "Original" é a página como veio
    (D-134). Só o papel marcado à mão (o pedido "quero esta área em branco")
    vai a branco."""
    projeto = _projeto(tmp_path, limpar=True)
    projeto.detectar_regioes = True       # a marcação da máquina vale (marca_sozinho)
    _marcar(projeto, 0.0, 0.0, 1.0, 1.0, origem=AUTOMATICO)
    img = _gerar(projeto)
    assert img[310:490, 90:270].max() < 60, "o bloco preto sumiu com papel da máquina"
    assert _amarelado(img[40:200, 350:550])
