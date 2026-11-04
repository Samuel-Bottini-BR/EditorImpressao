"""As provas da D-617: na prévia do Automático, o número da folha pode ser escrito (CLAUDE.md §11,
regra 4; docs/plano/DECISOES.md).

  D-617 (04/11/2026). Samuel, print a-63 ("página 30 de 70" circulado): "queria poder escrever o
      numero da folha aqui para ir direto." No Livro: "o número em "página N de 70" pode ser
      escrito: digita o número, Enter, e a prévia vai direto para essa folha. As setas < >
      continuam como estão." Pedido da gerente: número fora do intervalo ou vazio volta ao número
      atual, sem mensagem de erro; as setas do teclado continuam como hoje na janela.
  D-605 (03/11/2026): "nenhuma função nova [...] pode alterar o que já está escolhido e testado".
      Por isso: o "página N de M" continua o mesmo texto (contador.text()), as setas < > andam
      como na D-614 (pelas metades com o Dividir marcado) e o campo novo não entra na fila do Tab
      nem rouba o foco ao abrir a janela (hoje as setas do teclado não viram a página na janela
      grande: relatorios/previa-numero/anotacoes-base.txt).

Teste de reversão (§4.7): no código de antes (`945505b2`) o número era um rótulo (não existia
`campo_pagina`): todas estas provas falham lá.

Livro sintético do tests/test_decisoes_automatico.py: 3 folhas (a 0 dupla, a 1 torta, a 2 reta).
"""

from __future__ import annotations

import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico import _livro  # noqa: E402
from tests.test_decisoes_automatico_ver_como_fica import (  # noqa: E402,F401
    _abrir, _assentar, _esperar, _marcar, app, janela, pasta)


def _escrever(painel, texto: str, enter: bool = True) -> None:
    """O que a pessoa faz: clica no número, apaga, escreve `texto` e aperta Enter."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    campo = painel.campo_pagina
    campo.setFocus()
    campo.selectAll()
    QTest.keyClick(campo, Qt.Key_Delete)
    if texto:
        QTest.keyClicks(campo, texto)
    if enter:
        QTest.keyClick(campo, Qt.Key_Return)


def test_d617_escrever_o_numero_e_enter_vai_direto_para_a_folha(janela, app, tmp_path):
    """"queria poder escrever o numero da folha aqui para ir direto": na página 1, escrever 3 e
    Enter mostra a página 3 (o antes e o depois dela) e o contador diz "página 3 de 3"."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    assert painel.contador.text() == "página 1 de 3"
    assert painel.campo_pagina.text() == "1"
    _escrever(painel, "3")
    assert painel._indice == 2, "o Enter não foi para a página escrita"
    _esperar(app, painel)
    assert painel._antes is not None and painel._antes[0] == 2
    assert painel._depois is not None and painel._depois[0] == 2
    assert painel.contador.text() == "página 3 de 3"
    assert painel.campo_pagina.text() == "3"
    assert not painel.botao_proxima.isEnabled() and painel.botao_anterior.isEnabled()


def test_d617_vazio_ou_fora_do_intervalo_volta_ao_numero_atual_sem_mensagem(janela, app, tmp_path):
    """Vazio, 0, número maior que o livro ou letras: a prévia fica onde está e o número volta ao
    atual, sem caixa de aviso."""
    from PySide6.QtWidgets import QApplication, QMessageBox

    grande = _abrir(janela, app, tmp_path, pagina=1)
    painel = grande.antes_e_depois
    for texto in ("", "0", "4", "99", "abc"):
        _escrever(painel, texto)
        _assentar(app)
        assert painel._indice == 1, f"{texto!r} + Enter mudou a página"
        assert painel.campo_pagina.text() == "2", f"{texto!r}: o número não voltou ao atual"
        assert painel.contador.text() == "página 2 de 3"
        avisos = [w for w in QApplication.topLevelWidgets()
                  if isinstance(w, QMessageBox) and w.isVisible()]
        assert not avisos, f"{texto!r}: apareceu mensagem"


def test_d617_o_enter_do_numero_nao_aperta_o_rodar(janela, app, tmp_path):
    """O "Rodar" é o botão padrão da janela (Enter aperta). O Enter do número só vai para a
    folha: o livro não roda e a janela continua aberta."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    _marcar(grande, {A.ENDIREITAR})
    _esperar(app, painel)
    assert grande.botao_rodar.isEnabled()
    # o padrão da janela (setDefault em JanelaDoAutomatico); sem janela ativa (offscreen) o Qt
    # pode tê-lo passado a outro botão: aqui ele volta a ser o "Rodar", como na tela de verdade
    grande.botao_rodar.setDefault(True)
    rodou = []
    grande.rodar_pedido.connect(lambda: rodou.append(True))
    _escrever(painel, "2")
    _assentar(app)
    assert not rodou, "o Enter do número apertou o Rodar"
    assert grande.isVisible() and janela.janela_do_automatico is grande
    assert painel._indice == 1
    _escrever(painel, "0")                           # também o Enter que volta ao atual
    _assentar(app)
    assert not rodou and grande.isVisible()


def test_d617_com_dividir_as_setas_continuam_pelas_metades(janela, app, tmp_path):
    """D-614 continua: com o Dividir marcado, < > andam pelas metades. Escrever o número da folha
    em que já se está não muda a metade; escrever outra folha vai para ela (a metade da
    esquerda, como marcar o Dividir); "<" de lá volta à metade da direita da folha anterior."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    assert (painel._indice, painel._metade) == (0, "esquerda")
    painel.botao_proxima.click()
    _esperar(app, painel)
    assert (painel._indice, painel._metade) == (0, "direita")
    assert painel.contador.text() == "página 1 de 3"
    _escrever(painel, "1")                           # a mesma folha: fica na metade da direita
    assert (painel._indice, painel._metade) == (0, "direita")
    _escrever(painel, "2")
    _esperar(app, painel)
    assert painel._indice == 1 and painel.contador.text() == "página 2 de 3"
    painel.botao_anterior.click()
    _esperar(app, painel)
    assert (painel._indice, painel._metade) == (0, "direita"), "o < não andou pela metade"
    assert painel.campo_pagina.text() == "1"


def test_d617_o_campo_nao_muda_o_teclado_da_janela(janela, app, tmp_path):
    """As setas do teclado continuam como hoje: o campo só pega o foco com o clique (não entra
    na fila do Tab, nem na das setas entre os botões), e ao abrir a janela o foco não vai para
    ele."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    assert painel.campo_pagina.focusPolicy() == Qt.ClickFocus
    assert QApplication.focusWidget() is not painel.campo_pagina
    assert grande.focusWidget() is not painel.campo_pagina


# --- D-617, parte 2 (04/11/2026): com o Dividir marcado, o número é o da página como sai -------
# Samuel, testando a D-617: "funciona , mas com o dividir marcado o numero de pagina tem que
# corresponder com a pagina que está sendo passada." Pedido da gerente: com o Dividir marcado, a
# metade da esquerda da folha 68 aparece como "página 135 de 140" e a da direita "136 de 140";
# escrever o número leva a essa página; sem o Dividir, tudo como está; a ordem é a do livro como
# vai sair (D-615, ordem mudada à mão; D-616, capa aberta = "página 1"); o "tela cheia" mostra o
# mesmo número. Reversão: no código da parte 1 (`501cc1de`) o contador dizia "página 1 de 3" nas
# duas metades.

def test_d617_com_dividir_o_numero_e_a_pagina_como_o_livro_vai_sair(janela, app, tmp_path):
    """Livro sintético com o Dividir marcado: sai com 4 páginas (a folha 0 vira duas). A metade da
    esquerda da folha 0 é "página 1 de 4", a da direita "2 de 4", a folha 1 "3 de 4"; o "tela
    cheia" diz o mesmo. Escrever 2 leva à metade da direita da folha 0; 4, à folha 2; 5 (fora)
    fica. Desmarcar o Dividir volta ao número de sempre ("página 3 de 3" na folha 2)."""
    grande = _abrir(janela, app, tmp_path, pagina=0)
    painel = grande.antes_e_depois
    assert painel.contador.text() == "página 1 de 3"            # sem o Dividir: como sempre
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    assert (painel._indice, painel._metade) == (0, "esquerda")
    assert painel.contador.text() == "página 1 de 4" and painel.campo_pagina.text() == "1"
    painel.botao_proxima.click()
    assert (painel._indice, painel._metade) == (0, "direita")
    assert painel.contador.text() == "página 2 de 4" and painel.campo_pagina.text() == "2"
    painel.botao_proxima.click()
    assert painel._indice == 1 and painel.contador.text() == "página 3 de 4"
    painel.botao_tela_cheia.click()
    _assentar(app)
    assert painel.tela_cheia.contador.text() == "página 3 de 4", "o tela cheia diz outro número"
    painel.tela_cheia.done(0)
    _escrever(painel, "2")
    assert (painel._indice, painel._metade) == (0, "direita"), "o 2 não foi à metade da direita"
    assert painel.contador.text() == "página 2 de 4"
    _escrever(painel, "4")
    assert painel._indice == 2 and painel.contador.text() == "página 4 de 4"
    _escrever(painel, "5")
    assert painel._indice == 2 and painel.campo_pagina.text() == "4"
    _esperar(app, painel)
    _marcar(grande, set())
    _esperar(app, painel)
    assert painel._indice == 2 and painel.contador.text() == "página 3 de 3", (
        "sem o Dividir o número não voltou ao de sempre")


def test_d617_com_dividir_o_numero_segue_a_ordem_mudada_a_mao(janela, app, tmp_path):
    """D-615: com a última folha posta à mão na frente, o livro sai folha 2, folha 0 (duas
    metades), folha 1. A metade da esquerda da folha 0 é "página 2 de 4"; escrever 1 leva à
    folha 2, que está na frente."""
    from core import ordem_das_paginas as O

    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    projeto = janela.projeto
    O.por_na_ordem(projeto, [[2, "inteira"], [0, "inteira"], [1, "inteira"]])
    assert [p.folha for p in projeto.paginas] == [2, 0, 1]
    janela.tela_conferir.ir_para_pagina(1)                      # a folha 0
    grande = janela.abrir_o_automatico()
    painel = grande.antes_e_depois
    _esperar(app, painel)
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    assert projeto.paginas[painel._indice].folha == 0 and painel._metade == "esquerda"
    assert painel.contador.text() == "página 2 de 4"
    _escrever(painel, "1")
    assert projeto.paginas[painel._indice].folha == 2 and painel.contador.text() == "página 1 de 4"
    _escrever(painel, "4")
    assert projeto.paginas[painel._indice].folha == 1 and painel.contador.text() == "página 4 de 4"


def test_d617_com_dividir_e_a_capa_aberta_a_capa_e_a_pagina_1(janela, app, tmp_path):
    """D-616: livro de folhas abertas com "A 1ª folha é a capa aberta" marcada: a capa (metade da
    direita da 1ª folha) é "página 1 de 6" e a contracapa (a da esquerda) "página 6 de 6"."""
    from tests.test_decisoes_capa_aberta import DO_EDITOR, _livro as _livro_aberto

    janela.abrir_livro(_livro_aberto(tmp_path))
    _assentar(app)
    janela.tela_conferir.ir_para_pagina(0)
    grande = janela.abrir_o_automatico(A.DIVIDIR)
    painel = grande.antes_e_depois
    estado = janela.estado_do_automatico
    estado.opcoes["dividir_como"] = DO_EDITOR
    grande.controles["capa_aberta"].setChecked(True)
    _marcar(grande, {A.DIVIDIR})
    _esperar(app, painel)
    painel.ir_para(0)
    assert (painel._indice, painel._metade) == (0, "direita"), "a prévia não começa pela capa"
    assert painel.contador.text() == "página 1 de 6"
    _escrever(painel, "6")
    assert (painel._indice, painel._metade) == (0, "esquerda")
    assert painel.contador.text() == "página 6 de 6"
    _escrever(painel, "2")
    assert (painel._indice, painel._metade) == (1, "esquerda")
