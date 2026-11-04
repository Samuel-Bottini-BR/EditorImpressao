"""As provas de comportamento da D-604: cada lado da folha do caderno diz as páginas do livro
que estão nele (CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

  D-604. 03/11/2026, print a-52 (etapa 7, "Folha 1 de 19 — frente" / "— verso"): "o verso da
      folha 1 e 19 não podem ter a numeração de folha 1 - e 19 tem que dizer a numeração que elas
      realmente teriam." · pergunta: "Folha 1 de 19, frente: páginas 20 e 1 [...] Folha 1 de 19,
      verso: páginas 2 e 19 [...] Ao virar para a folha 2, mostraria "frente: páginas 18 e 3", e
      assim por diante. É isso?" → "acredito que sim" · 04/11, print a-79: "é melhor colocar a
      numeração das paginas verdadeiras aqui".
      No Livro: "Nas folhas do caderno, cada lado diz as páginas do livro que estão nele, da
      esquerda para a direita [...] Vale onde aparecem as folhas do caderno (etapa 7 do
      Automático, tela grande de caderno, "Montar para imprimir", D-574)." Página em branco que o
      caderno acrescenta no fim: "a confirmar com ele se aparecer" (a gerente, 04/11: mostrar
      "em branco" no lugar do número, com print).
  Os números são os do livro COMO VAI SAIR: seguem a ordem mudada à mão (D-615), a capa aberta
  (D-616) e o Dividir marcado na prévia (D-603). Por isso a prova compara o número escrito com a
  página que está de fato desenhada naquele lugar da folha.

O que fica igual (D-605): o texto "Folha N de M — frente" continua no mesmo rótulo de sempre
(25 provas antigas comparam esse rótulo inteiro); as páginas vêm logo depois, na mesma linha,
num rótulo só delas (": páginas 20 e 1").

Teste de reversão (CLAUDE.md §4.7): no código antigo (`dac12a3f`) a folha não diz as páginas (não
existe o rótulo das páginas): todas estas provas falham lá.

Livros sintéticos: a página k (1, 2, ...) do scan é toda pintada de cinza 5*k, para ler pelo
desenho qual página caiu em cada metade da folha.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import impressao as imp  # noqa: E402
from tests.test_decisoes_automatico import _pdf  # noqa: E402
from tests.test_decisoes_caderno_tela_grande import (  # noqa: E402,F401 (fixtures app, janela)
    _assentar,
    _esperar,
    app,
    janela,
)
from tests.test_decisoes_livreto_ver import (  # noqa: E402
    _dialogo,
    _livro as _livro_a5,
    _paginas_na_tela,
    _previa_quieta,
)
from tests.test_decisoes_livreto_ver import _esperar as _esperar_que  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import pasta  # noqa: E402,F401 (fixture: dados à parte)

PASSO_DO_CINZA = 5


def _livro_cinza(caminho, paginas: int) -> str:
    """Livro de `paginas` páginas em pé; a página k (1, 2, ...) é toda cinza 5*k."""
    return _pdf(caminho, [np.full((420, 300, 3), PASSO_DO_CINZA * k, np.uint8)
                          for k in range(1, paginas + 1)])


def _qual(metade: np.ndarray):
    """A página do scan (1, 2, ...) pintada nesta metade da folha; None = branca."""
    cinza = metade.mean(axis=2) if metade.ndim == 3 else metade
    pintado = cinza < 245
    if pintado.sum() < 20:
        return None
    return round(float(np.median(cinza[pintado])) / PASSO_DO_CINZA)


def _no_desenho(face: np.ndarray) -> tuple:
    meio = face.shape[1] // 2
    return _qual(face[:, :meio]), _qual(face[:, meio:])


def _linha(rotulos, numeros, lado: str) -> str:
    """O que se lê na linha de cima de cada lado: o rótulo "Folha N de M — lado" e, logo
    depois, o das páginas. No código antigo não existe o das páginas: a prova falha aqui."""
    assert numeros is not None, "a folha não diz as páginas que estão nela (D-604)"
    return rotulos[lado].text() + numeros[lado].text()


def _abrir_etapa_7(janela, app, caminho: str, por_caderno: int = 20, mexer=None):
    janela.abrir_livro(caminho)
    _assentar(app)
    if mexer is not None:
        mexer(janela)
        _assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = por_caderno
    grande = janela.abrir_o_automatico(A.CADERNOS)
    assert grande is not None
    _assentar(app)
    return grande.folhas_do_caderno


# --- etapa 7 do Automático e a tela grande de caderno --------------------------------------

def test_d604_etapa_7_folhas_1_e_2_com_a_ordem_mudada(janela, app, tmp_path):
    """Livro de 40 páginas, 20 por caderno, com a página 5 do scan arrastada para o 2º lugar
    (D-615). Folha 1: "frente: páginas 20 e 1", "verso: páginas 2 e 19"; folha 2: "frente:
    páginas 18 e 3", "verso: páginas 4 e 17" (as palavras da D-604). O número é o do livro
    como vai sair: no lugar escrito "2" está desenhada a página que foi para o 2º lugar (a 5
    do scan), não a 2 do scan."""
    def mudar_a_ordem(jan):
        jan.tela_conferir._mover_da_tira(4, 1)     # a folha 5 do scan vai para antes da 2

    folhas = _abrir_etapa_7(janela, app, _livro_cinza(tmp_path / "quarenta.pdf", 40),
                            mexer=mudar_a_ordem)
    ordem = [p.folha + 1 for p in janela.projeto.paginas]
    assert ordem[:6] == [1, 5, 2, 3, 4, 6], "a ordem não mudou (o teste não montou o caso)"
    numeros = getattr(folhas, "numeros_das_paginas", None)
    _esperar(app, folhas)

    assert _linha(folhas.rotulos, numeros, "frente") == "Folha 1 de 10 — frente: páginas 20 e 1"
    assert _linha(folhas.rotulos, numeros, "verso") == "Folha 1 de 10 — verso: páginas 2 e 19"
    frente, verso = folhas.faces()
    # o desenho: no lugar da página N do livro está a página do scan que ficou em N
    assert _no_desenho(frente) == (ordem[19], ordem[0]) == (20, 1)
    assert _no_desenho(verso) == (ordem[1], ordem[18]) == (5, 19)

    # a seta: o texto troca na hora (D-574, "já troca"), antes do desenho chegar
    folhas.passar_folha(1)
    assert _linha(folhas.rotulos, numeros, "frente") == "Folha 2 de 10 — frente: páginas 18 e 3"
    assert _linha(folhas.rotulos, numeros, "verso") == "Folha 2 de 10 — verso: páginas 4 e 17"
    _esperar(app, folhas)
    frente, verso = folhas.faces()
    assert _no_desenho(frente) == (ordem[17], ordem[2]) == (18, 2)
    assert _no_desenho(verso) == (ordem[3], ordem[16]) == (3, 17)

    # a tela grande de caderno diz o mesmo
    folhas.abrir_em_tela_cheia()
    _assentar(app)
    tela = folhas.tela_grande
    assert _linha(tela.rotulos, getattr(tela, "numeros_das_paginas", None), "frente") \
        == "Folha 2 de 10 — frente: páginas 18 e 3"
    assert _linha(tela.rotulos, tela.numeros_das_paginas, "verso") \
        == "Folha 2 de 10 — verso: páginas 4 e 17"
    tela.botao_anterior.click()
    _assentar(app)
    assert _linha(tela.rotulos, tela.numeros_das_paginas, "frente") \
        == "Folha 1 de 10 — frente: páginas 20 e 1"
    tela.reject()


def test_d604_etapa_7_pagina_em_branco_do_fim_do_caderno(janela, app, tmp_path):
    """22 páginas, 20 por caderno: o 2º caderno tem 4 lugares para 2 páginas (imp-4), e os
    dois que sobram saem em branco. A gerente (04/11): "em branco" no lugar do número."""
    folhas = _abrir_etapa_7(janela, app, _livro_cinza(tmp_path / "vinte-e-duas.pdf", 22))
    numeros = getattr(folhas, "numeros_das_paginas", None)
    for _ in range(5):
        folhas.passar_folha(1)
    assert _linha(folhas.rotulos, numeros, "frente") \
        == "Folha 6 de 6 — frente: páginas em branco e 21"
    assert _linha(folhas.rotulos, numeros, "verso") \
        == "Folha 6 de 6 — verso: páginas 22 e em branco"
    _esperar(app, folhas)
    frente, verso = folhas.faces()
    assert _no_desenho(frente) == (None, 21)
    assert _no_desenho(verso) == (22, None)


def test_d604_etapa_7_dividir_e_capa_aberta_marcados(janela, app, tmp_path):
    """D-603 e D-616: com o Dividir marcado na prévia e "A 1ª folha é a capa aberta", os números
    são os das páginas DEPOIS de dividir: 20 folhas abertas viram 40 páginas (10 folhas de
    caderno, não 5), e a página 1 é a capa (a metade da direita da 1ª folha)."""
    from core import dividir_scantailor as ds

    abertas = [np.concatenate([np.full((420, 300, 3), PASSO_DO_CINZA * (2 * k + 1), np.uint8),
                               np.full((420, 300, 3), PASSO_DO_CINZA * (2 * k + 2), np.uint8)],
                              axis=1) for k in range(20)]
    janela.abrir_livro(_pdf(tmp_path / "abertas.pdf", abertas))
    _assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR, A.CADERNOS}
    estado.opcoes.update({"dividir_como": ds.JEITO_DO_PROJETO_ANTIGO, "capa_aberta": True,
                          "paginas_por_caderno": 20})
    grande = janela.abrir_o_automatico(A.CADERNOS)
    _assentar(app)
    folhas = grande.folhas_do_caderno
    numeros = getattr(folhas, "numeros_das_paginas", None)
    assert _linha(folhas.rotulos, numeros, "frente") == "Folha 1 de 10 — frente: páginas 20 e 1"
    assert _linha(folhas.rotulos, numeros, "verso") == "Folha 1 de 10 — verso: páginas 2 e 19"
    lista = folhas._depois()
    assert (lista[0][1], lista[0][2]) == (0, "direita"), "a página 1 não é a capa (D-616)"


# --- "Montar para imprimir" (D-574) ---------------------------------------------------------

def _linha_do_dialogo(dialogo, lado: str) -> str:
    numeros = getattr(dialogo, "paginas_da_face", None)
    assert numeros is not None, "a folha do \"Montar para imprimir\" não diz as páginas (D-604)"
    return dialogo.rotulos_da_face[lado].text() + numeros[lado].text()


def test_d604_montar_para_imprimir_folhas_1_e_2(app, pasta):
    """40 páginas, Livreto, 20 por caderno: as palavras da D-604, e o número bate com a página
    desenhada (o PDF de entrada aqui é o livro já processado: a ordem dele é a que sai)."""
    dialogo = _dialogo(_livro_a5(pasta / "livro.pdf"))
    try:
        assert _linha_do_dialogo(dialogo, imp.FRENTE) == "Folha 1 de 10 — frente: páginas 20 e 1"
        assert _linha_do_dialogo(dialogo, imp.VERSO) == "Folha 1 de 10 — verso: páginas 2 e 19"
        assert _paginas_na_tela(dialogo) == {imp.FRENTE: (20, 1), imp.VERSO: (2, 19)}
        dialogo.botao_folha_seguinte.click()
        # o texto troca na hora (D-574, "já troca")
        assert _linha_do_dialogo(dialogo, imp.FRENTE) == "Folha 2 de 10 — frente: páginas 18 e 3"
        assert _linha_do_dialogo(dialogo, imp.VERSO) == "Folha 2 de 10 — verso: páginas 4 e 17"
        assert _esperar_que(lambda: _previa_quieta(dialogo) and dialogo.folha_na_tela.numero == 2)
        assert _linha_do_dialogo(dialogo, imp.FRENTE) == "Folha 2 de 10 — frente: páginas 18 e 3"
        assert _paginas_na_tela(dialogo) == {imp.FRENTE: (18, 3), imp.VERSO: (4, 17)}
    finally:
        dialogo.reject()


def test_d604_montar_para_imprimir_costura_a_direita_e_branca(app, pasta):
    """Os números vão da esquerda para a direita como está no papel: com a encadernação à
    direita a frente da folha 1 é "páginas 1 e 20". A página em branco que o "Montar para
    imprimir" põe antes de um intervalo que começa numa página par sai "em branco"."""
    entrada = _livro_a5(pasta / "livro.pdf")
    dialogo = _dialogo(entrada, encadernacao=imp.DIREITA)
    try:
        assert _linha_do_dialogo(dialogo, imp.FRENTE) == "Folha 1 de 10 — frente: páginas 1 e 20"
        assert _paginas_na_tela(dialogo)[imp.FRENTE] == (1, 20)
    finally:
        dialogo.reject()
    dialogo = _dialogo(entrada, paginas_de=2, paginas_ate=4)
    try:
        # as páginas 2 a 4 com uma branca antes: [branca, 2, 3, 4] num caderno de 4
        assert _linha_do_dialogo(dialogo, imp.FRENTE) == "Folha 1 de 1 — frente: páginas 4 e em branco"
        assert _linha_do_dialogo(dialogo, imp.VERSO) == "Folha 1 de 1 — verso: páginas 2 e 3"
        assert _paginas_na_tela(dialogo) == {imp.FRENTE: (4, None), imp.VERSO: (2, 3)}
    finally:
        dialogo.reject()
