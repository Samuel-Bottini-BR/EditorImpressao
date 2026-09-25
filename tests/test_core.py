"""Testes do core que não dependem de nenhum PDF real."""

from __future__ import annotations

import numpy as np
import pytest

import configuracoes

from core.analise import detectar_cor, fracao_de_tinta, tamanhos_fora_do_padrao
from core.dividir import detectar_lombada, dividir_imagem
from core.endireitar import ANGULO_MAXIMO, detectar_angulo, rotacionar
from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    janela_para_altura,
    k_do_sauvola,
    palavra_do_ajuste,
)
from core.recortar import aplicar_recorte, detectar_bordas
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import ConfigFolha, ConfigPagina, Projeto


def folha_dupla(com_sombra: bool = True) -> np.ndarray:
    """Uma folha branca com duas colunas de texto e uma lombada no meio."""
    img = np.full((600, 1000, 3), 235, dtype=np.uint8)
    for bloco_x in (120, 620):
        for linha in range(12):
            y = 100 + linha * 30
            img[y : y + 10, bloco_x : bloco_x + 260] = 30
    if com_sombra:
        img[:, 490:510] = 150
    return img


# --- filtros ---------------------------------------------------------------

def test_preto_e_branco_devolve_um_canal_so_com_preto_e_branco():
    saida, mono = aplicar_filtro(folha_dupla(), PRETO_E_BRANCO)
    assert mono is True
    assert saida.ndim == 2
    assert set(np.unique(saida)).issubset({0, 255})


def test_preto_e_branco_preserva_o_texto():
    saida, _ = aplicar_filtro(folha_dupla(), PRETO_E_BRANCO)
    tinta = (saida == 0).mean()
    assert 0.01 < tinta < 0.40, f"tinta fora do esperado: {tinta:.3f}"


def test_forcas_do_preto_sao_ordenadas():
    """Subir o medidor tem que deixar mais preto, sempre."""
    img = folha_dupla()
    pretos = [
        (aplicar_filtro(img, PRETO_E_BRANCO, forca_preto=v)[0] == 0).mean()
        for v in (0, 25, 50, 75, 100)
    ]
    assert pretos == sorted(pretos), pretos
    assert pretos[0] < pretos[-1], "o medidor não mudou nada"


def test_medidor_do_meio_cai_no_k_recomendado():
    """O meio do medidor cai no k que a LETRA da pagina pede.

    Era um numero fixo para o acervo inteiro, e nao existe numero fixo que
    sirva: letra fina aguenta k alto - que e o que mata a mancha do verso -
    e letra grossa nao aguenta, o Sauvola come a barriga do traco. Ver
    k_para_a_letra.
    """
    from core.filtros import K_PARA_LETRA_FINA, K_PARA_LETRA_GROSSA

    # sem dizer o k do meio, vale o padrao de sempre
    assert k_do_sauvola(50) == pytest.approx(0.30)
    assert k_do_sauvola(0) == pytest.approx(0.40)
    assert k_do_sauvola(100) == pytest.approx(0.06)

    # com o k da letra, o meio do medidor passa a ser ele
    for k in (K_PARA_LETRA_FINA, K_PARA_LETRA_GROSSA):
        assert k_do_sauvola(50, k) == pytest.approx(k)
        assert k_do_sauvola(0, k) == pytest.approx(0.40)
        assert k_do_sauvola(100, k) == pytest.approx(0.06)
        andando = [k_do_sauvola(v, k) for v in range(0, 101, 10)]
        assert andando == sorted(andando, reverse=True), andando


def test_k_cai_conforme_o_medidor_sobe():
    valores = [k_do_sauvola(v) for v in range(0, 101, 10)]
    assert valores == sorted(valores, reverse=True), valores


def test_medidor_aceita_valor_fora_da_faixa():
    assert k_do_sauvola(-30) == k_do_sauvola(0)
    assert k_do_sauvola(300) == k_do_sauvola(100)


def test_palavras_do_medidor():
    assert palavra_do_ajuste(0) == "bem fraco"
    assert palavra_do_ajuste(50) == "normal"
    assert palavra_do_ajuste(100) == "bem forte"


def test_intensidade_do_magico_muda_a_saturacao():
    """Subir a intensidade tem que deixar a cor mais viva, de fato."""
    import cv2

    capa = np.full((400, 300, 3), (150, 90, 40), dtype=np.uint8)
    capa[:60, :] = 240   # uma faixa de papel, para haver o que balancear

    saturacoes = []
    for valor in (0, 50, 100):
        saida, _ = aplicar_filtro(capa, MAGICO_PRO, intensidade=valor)
        hsv = cv2.cvtColor(saida, cv2.COLOR_BGR2HSV)
        saturacoes.append(float(hsv[200:, :, 1].mean()))

    assert saturacoes == sorted(saturacoes), saturacoes
    assert saturacoes[-1] > saturacoes[0] * 1.2, saturacoes


def test_clareza_do_melhorar_clareia_o_fundo():
    """Subir a clareza tem que deixar o papel mais claro, nunca mais escuro."""
    img = folha_dupla()
    img[:] = (200, 210, 225)          # papel amarelado, sem texto
    img[100:120, 100:400] = 40        # uma linha de texto

    fundos = []
    for valor in (0, 50, 100):
        saida, _ = aplicar_filtro(img, MELHORAR, clareza=valor)
        fundos.append(float(saida[300:400, 100:400].mean()))

    assert fundos == sorted(fundos), fundos


@pytest.mark.parametrize("filtro", [ORIGINAL, MELHORAR, MAGICO_PRO])
def test_filtros_coloridos_mantem_tres_canais(filtro):
    saida, mono = aplicar_filtro(folha_dupla(), filtro)
    assert mono is False
    assert saida.ndim == 3


def test_melhorar_nao_lava_uma_area_colorida_uniforme():
    """A capa azul: o Melhorar tem que devolver azul, não um borrao claro.

    E a regressao que motivou trocar a divisão pelo fundo por uma correcao
    com peso - a versão ingenua lavava a capa e trocava as cores.
    """
    img = np.full((600, 400, 3), 235, dtype=np.uint8)
    img[:, 200:] = (150, 70, 20)   # metade direita azul escuro (BGR)

    saida, _ = aplicar_filtro(img, MELHORAR)
    azul = saida[300, 300].astype(int)

    assert azul[0] > azul[2] + 40, f"o azul deixou de ser azul: {azul}"
    assert azul[0] < 235, f"o azul foi lavado até o branco: {azul}"


def test_janela_do_sauvola_e_sempre_impar():
    for altura in (300, 1000, 2480, 5000):
        assert janela_para_altura(altura) % 2 == 1


# --- dividir ---------------------------------------------------------------

def test_acha_a_lombada_no_meio():
    lombada = detectar_lombada(folha_dupla())
    assert lombada.e_paisagem
    assert abs(lombada.posicao - 0.5) < 0.05
    assert lombada.confianca > 0.5


def test_acha_a_lombada_mesmo_sem_sombra():
    """Scan limpo: sobra só a ausencia de texto para nos guiar."""
    lombada = detectar_lombada(folha_dupla(com_sombra=False))
    assert abs(lombada.posicao - 0.5) < 0.06


def test_pagina_em_retrato_nao_e_dupla():
    retrato = np.full((900, 600, 3), 240, dtype=np.uint8)
    lombada = detectar_lombada(retrato)
    assert lombada.e_paisagem is False
    assert lombada.confianca == 0.0


def test_dividir_devolve_esquerda_e_direita():
    esq, dir_ = dividir_imagem(folha_dupla(), 0.5)
    assert esq.shape[1] == 500 and dir_.shape[1] == 500


# --- endireitar ------------------------------------------------------------

def test_detecta_a_inclinacao_que_aplicamos():
    img = rotacionar(folha_dupla(), -2.0)
    detectado = detectar_angulo(img)
    assert abs(detectado.angulo - 2.0) < 0.6, detectado.angulo


def test_nao_gira_quando_o_angulo_e_minimo():
    img = folha_dupla()
    assert rotacionar(img, 0.05) is img


def test_pagina_em_branco_nao_tem_angulo():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    assert detectar_angulo(branca).angulo == 0.0


def test_nunca_passa_do_limite():
    for _ in range(3):
        assert abs(detectar_angulo(folha_dupla()).angulo) <= ANGULO_MAXIMO


# --- recortar --------------------------------------------------------------

def test_recorte_tira_a_borda_preta_do_scanner():
    img = folha_dupla()
    img[:, :40] = 0        # borda preta na esquerda
    recorte = detectar_bordas(img)
    cortada = aplicar_recorte(img, recorte)
    assert cortada.shape[1] < img.shape[1]
    assert cortada[:, :5].mean() > 100, "sobrou borda preta depois do corte"


def test_a_rampa_da_borda_sobrevive_ao_filtro():
    """O defeito mais frequente do acervo, medido pela regua do projeto.

    As curvas que limpam a pagina deixam o salto entre tinta e papel mais
    ingreme, e a borda da letra perde o meio-tom que a arredonda: a rampa do
    Graduale caia de 2,38 para 0,68 pixels. Eram 35 das 53 paginas que sairam
    piores que o original.
    """
    import cv2

    from core.filtros import filtro_magico_pro, filtro_melhorar

    img = np.full((400, 400, 3), 226, np.uint8)
    for linha in range(6):
        y = 60 + linha * 50
        for palavra in range(5):
            x = 40 + palavra * 70
            img[y:y + 26, x:x + 40] = 40                 # o traco
            img[y - 3:y, x:x + 40] = 150                 # a rampa em cima
            img[y + 26:y + 29, x:x + 40] = 150           # e embaixo

    def rampa(m):
        cinza = cv2.cvtColor(m, cv2.COLOR_BGR2GRAY) if m.ndim == 3 else m
        return float(((cinza > 90) & (cinza < 200)).sum())

    antes = rampa(img)
    for filtro in (filtro_melhorar, filtro_magico_pro):
        depois = rampa(filtro(img))
        assert depois > antes * 0.5, (
            f"{filtro.__name__} comeu a rampa: {antes:.0f} -> {depois:.0f}")


def test_o_branco_nao_come_a_orla_da_letra():
    """A rampa que arredonda a letra tem de sobreviver ao empurrao do branco.

    Era a queixa 1 do Kaique, "letras pixeladas": todo pixel acima de 235 virava
    255, inclusive os poucos tons intermediarios que ficam colados no traco. Sem
    eles a letra vira escada.
    """
    from core.filtros import _empurrar_branco

    img = np.full((200, 200, 3), 252, np.uint8)
    img[80:120, 80:120] = 20                       # o traco
    img[76:80, 80:120] = 200                       # a rampa em cima dele
    img[120:124, 80:120] = 240                     # e a rampa embaixo

    saida = _empurrar_branco(img)

    assert (saida[10:40, 10:40] == 255).all(), "o papel aberto nao foi a branco"
    assert saida[120, 100, 0] != 255, "a orla colada na letra foi apagada"
    assert saida[78, 100, 0] == 200, "a rampa escura foi mexida"


def test_risca_do_vinco_nao_segura_o_corte():
    """A risca da dobra atravessa a pagina e nao pode mandar no recorte.

    E o caso das paginas 429 e 536 do Graduale: o vinco do livro aberto deixa
    uma risca fina de ponta a ponta que prendia o corte na largura inteira.
    """
    img = folha_dupla(com_sombra=False)
    img[:, 30:33] = 60  # o vinco, de cima a baixo, colado na margem esquerda

    recorte = detectar_bordas(img)

    assert recorte.x > 0.05, "a risca do vinco segurou a borda esquerda"


def test_moldura_da_gravura_e_preservada():
    """O que nao encosta na borda da imagem e conteudo, e fica.

    A moldura de uma gravura tambem e uma linha comprida, mas comeca depois de
    uma margem - e por isso que da para apagar o vinco sem comer a moldura.
    """
    img = np.full((600, 1000, 3), 235, dtype=np.uint8)
    img[60:540, 80:83] = 30       # lado esquerdo da moldura
    img[60:540, 917:920] = 30     # lado direito
    img[60:63, 80:920] = 30       # topo
    img[537:540, 80:920] = 30     # base

    recorte = detectar_bordas(img)

    assert recorte.x <= 80 / 1000, "comeu o lado esquerdo da moldura"
    assert recorte.x + recorte.largura >= 920 / 1000, "comeu o lado direito"


def test_pagina_em_branco_nao_e_recortada():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    recorte = detectar_bordas(branca)
    assert recorte.tupla == (0.0, 0.0, 1.0, 1.0)


# --- analise ---------------------------------------------------------------

def test_texto_preto_no_branco_nao_conta_como_colorido():
    tem_cor, _ = detectar_cor(folha_dupla())
    assert tem_cor is False


def test_capa_colorida_conta_como_colorida():
    capa = np.full((600, 400, 3), (170, 90, 30), dtype=np.uint8)
    tem_cor, _ = detectar_cor(capa)
    assert tem_cor is True


def test_pagina_em_branco_quase_nao_tem_tinta():
    branca = np.full((600, 400, 3), 250, dtype=np.uint8)
    assert fracao_de_tinta(branca) < 0.01


def test_marca_a_folha_de_tamanho_diferente():
    tamanhos = [(842.0, 595.0)] * 9 + [(595.0, 842.0)]
    fora = tamanhos_fora_do_padrao(tamanhos)
    assert fora[-1] is True
    assert not any(fora[:-1])


# --- desfazer / refazer ----------------------------------------------------

def projeto_de_teste() -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(3)]
    projeto.paginas = [
        ConfigPagina(indice=i, folha=i // 2, filtro=PRETO_E_BRANCO) for i in range(6)
    ]
    return projeto


def test_desfazer_e_refazer_uma_alteracao():
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes()

    acao = montar_acao(projeto, "mudar_filtro", "pagina", [2],
                       {"filtro": MAGICO_PRO}, "Filtro da página 3")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert projeto.paginas[2].filtro == MAGICO_PRO

    acoes.desfazer(projeto)
    assert projeto.paginas[2].filtro == PRETO_E_BRANCO
    acoes.refazer(projeto)
    assert projeto.paginas[2].filtro == MAGICO_PRO


def test_um_ctrl_z_desfaz_o_lote_inteiro():
    """'Usar em todas' e UMA acao, mesmo mexendo em 6 páginas."""
    projeto = projeto_de_teste()
    projeto.paginas[0].filtro = MELHORAR   # valor diferente, para conferir a volta
    acoes = HistoricoAcoes()

    indices = [p.indice for p in projeto.paginas]
    acao = montar_acao(projeto, "aplicar_em_todas", "pagina", indices,
                       {"filtro": MAGICO_PRO}, "Mágico pro em todas")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert all(p.filtro == MAGICO_PRO for p in projeto.paginas)

    acoes.desfazer(projeto)
    assert projeto.paginas[0].filtro == MELHORAR, "cada página volta ao SEU valor"
    assert all(p.filtro == PRETO_E_BRANCO for p in projeto.paginas[1:])


def test_acao_nova_limpa_a_pilha_de_refazer():
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes()

    for filtro in (MAGICO_PRO, MELHORAR):
        acao = montar_acao(projeto, "mudar_filtro", "pagina", [0], {"filtro": filtro}, "x")
        aplicar(projeto, acao, acao.depois)
        acoes.registrar(acao)

    acoes.desfazer(projeto)
    assert acoes.pode_refazer

    acao = montar_acao(projeto, "mudar_filtro", "pagina", [1], {"filtro": ORIGINAL}, "y")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert not acoes.pode_refazer


def test_historico_sobrevive_a_fechar_o_programa(tmp_path):
    """Criterio 14: reabrir o programa mantem o desfazer E o refazer."""
    projeto = projeto_de_teste()
    acoes = HistoricoAcoes(tmp_path)

    for filtro in (MAGICO_PRO, MELHORAR):
        acao = montar_acao(projeto, "mudar_filtro", "pagina", [0], {"filtro": filtro}, "x")
        aplicar(projeto, acao, acao.depois)
        acoes.registrar(acao)
    acoes.desfazer(projeto)   # sobra 1 aplicada e 1 para refazer

    # "fecha e reabre"
    outro = HistoricoAcoes(tmp_path)
    outro.carregar()
    assert len(outro.feitas) == 1
    assert outro.pode_desfazer and outro.pode_refazer


def test_desfazer_tamanho_da_folha_devolve_tupla():
    """Bug latente achado no plano (secao 3a): `conteudo_deslocamento` ja
    tinha esse problema, nunca pego por nunca ter sido lido antes.
    `tamanho_folha_cm` (novo) precisa do mesmo tratamento que `recorte` -
    senao o Ctrl+Z devolve uma LISTA (o JSON engoliu a tupla), e qualquer
    comparacao `== (w, h)` depois de desfazer falha."""
    projeto = projeto_de_teste()
    projeto.paginas[2].tamanho_folha_cm = (21.0, 29.7)
    acoes = HistoricoAcoes()

    acao = montar_acao(projeto, "tamanho_folha", "pagina", [2],
                       {"tamanho_folha_cm": (14.8, 21.0)}, "Tamanho da folha")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)
    assert projeto.paginas[2].tamanho_folha_cm == (14.8, 21.0)

    acoes.desfazer(projeto)
    valor = projeto.paginas[2].tamanho_folha_cm
    assert valor == (21.0, 29.7)
    assert isinstance(valor, tuple), f"devolveu {type(valor)}, nao tupla"


def test_desfazer_conteudo_deslocamento_devolve_tupla():
    """Mesmo bug latente, agora no campo que ja existia mas nunca era lido."""
    projeto = projeto_de_teste()
    projeto.paginas[0].conteudo_deslocamento = (0.1, -0.2)
    acoes = HistoricoAcoes()

    acao = montar_acao(projeto, "mover_conteudo", "pagina", [0],
                       {"conteudo_deslocamento": (0.3, 0.4)}, "Mover conteúdo")
    aplicar(projeto, acao, acao.depois)
    acoes.registrar(acao)

    acoes.desfazer(projeto)
    valor = projeto.paginas[0].conteudo_deslocamento
    assert valor == (0.1, -0.2)
    assert isinstance(valor, tuple), f"devolveu {type(valor)}, nao tupla"


def test_apagar_paginas_nao_quebra_a_contagem():
    projeto = projeto_de_teste()
    projeto.paginas[1].apagada = True
    projeto.paginas[4].apagada = True
    assert projeto.total_apagadas == 2
    assert len(projeto.paginas_ativas) == 4


# --- destino de gravacao ---------------------------------------------------

def test_pasta_normal_aceita_gravacao(tmp_path):
    pode, motivo = configuracoes.pode_gravar_em(tmp_path)
    assert pode and motivo == ""


def test_unidade_inexistente_e_recusada():
    pode, motivo = configuracoes.pode_gravar_em("Z:/nao_existe_mesmo")
    assert not pode
    assert "Não consegui criar" in motivo


def test_permissao_negada_vira_frase_em_portugues(tmp_path, monkeypatch):
    """O usuario nunca pode ver 'PermissionError' na tela (regra 3.3)."""
    import tempfile as _tempfile

    def recusar(*_args, **_kwargs):
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(_tempfile, "NamedTemporaryFile", recusar)
    pode, motivo = configuracoes.pode_gravar_em(tmp_path)

    assert not pode
    assert "permissão" in motivo.lower(), "a mensagem tem que estar acentuada"
    assert "Error" not in motivo and "Errno" not in motivo
    assert "Documentos" in motivo, "a mensagem precisa sugerir uma saida"


def test_disco_cheio_vira_frase_em_portugues(tmp_path, monkeypatch):
    import tempfile as _tempfile

    def recusar(*_args, **_kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(_tempfile, "NamedTemporaryFile", recusar)
    pode, motivo = configuracoes.pode_gravar_em(tmp_path)
    assert not pode and "Error" not in motivo


def test_nome_repetido_ganha_numero(tmp_path):
    (tmp_path / "livro.pdf").write_bytes(b"x")
    assert configuracoes.caminho_sem_repetir(tmp_path, "livro.pdf").name == "livro (2).pdf"

    (tmp_path / "livro (2).pdf").write_bytes(b"x")
    assert configuracoes.caminho_sem_repetir(tmp_path, "livro.pdf").name == "livro (3).pdf"


def test_nome_livre_fica_como_esta(tmp_path):
    assert configuracoes.caminho_sem_repetir(tmp_path, "livro.pdf").name == "livro.pdf"


# --- alerta que vale para o livro inteiro ----------------------------------

def test_alerta_de_todas_as_paginas_vira_observacao():
    """Marcar 100% das páginas nao ajuda: o contador perde o sentido.

    Achado num manuscrito colorido de 4 páginas em que os tres alertas eram
    verdadeiros e todos valiam para o livro todo - 100% marcado.
    """
    from core.analise import COR, NAO_PARECE_DUPLA, separar_observacoes

    listas = [[NAO_PARECE_DUPLA, COR] for _ in range(4)]
    observacoes, remover = separar_observacoes(listas)

    assert remover == {NAO_PARECE_DUPLA, COR}
    assert len(observacoes) == 2
    assert all(isinstance(o, str) and o for o in observacoes)


def test_alerta_de_poucas_paginas_continua_na_pagina():
    """O caso normal: 1 capa colorida em 10 páginas continua sendo alerta."""
    from core.analise import COR, separar_observacoes

    listas = [[COR]] + [[] for _ in range(9)]
    observacoes, remover = separar_observacoes(listas)

    assert remover == set()
    assert observacoes == []


def test_livro_curto_nao_vira_observacao():
    """Com 3 páginas nao da para concluir nada sobre o livro."""
    from core.analise import COR, separar_observacoes

    observacoes, remover = separar_observacoes([[COR], [COR], [COR]])
    assert observacoes == [] and remover == set()


def test_o_limiar_e_respeitado():
    from core.analise import COR, separar_observacoes

    # 6 de 10 = 60%, abaixo do limiar de 70%
    listas = [[COR] for _ in range(6)] + [[] for _ in range(4)]
    assert separar_observacoes(listas)[1] == set()

    # 7 de 10 = 70%, no limiar
    listas = [[COR] for _ in range(7)] + [[] for _ in range(3)]
    assert separar_observacoes(listas)[1] == {COR}


# --- qualidade do scan -----------------------------------------------------

def _pdf_com_imagem(caminho, largura_px: int, altura_px: int, largura_pt: float):
    """PDF de uma página só, com uma imagem embutida de tamanho conhecido."""
    import cv2
    import fitz

    arte = np.full((altura_px, largura_px, 3), 240, dtype=np.uint8)
    arte[100:140, 100:400] = 20
    ok, buffer = cv2.imencode(".png", arte)
    assert ok

    doc = fitz.open()
    altura_pt = largura_pt * altura_px / largura_px
    pagina = doc.new_page(width=largura_pt, height=altura_pt)
    pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt),
                        stream=buffer.tobytes())
    doc.save(caminho)
    doc.close()


def test_dpi_real_vem_da_imagem_embutida(tmp_path):
    """O DPI tem que sair do scan, não do tamanho com que rasterizamos.

    Este teste existe porque a versão anterior media na imagem que ela mesma
    acabara de rasterizar: devolvia sempre o DPI pedido, e o alerta de
    qualidade baixa nunca disparava - nem num scan de 112 DPI.
    """
    import fitz

    from core.pdf_io import dpi_real_da_pagina

    caminho = tmp_path / "scan.pdf"
    # 1200 px numa página de 8 polegadas (576 pt) = 150 DPI
    _pdf_com_imagem(caminho, largura_px=1200, altura_px=1600, largura_pt=576)

    doc = fitz.open(caminho)
    try:
        assert dpi_real_da_pagina(doc, 0) == pytest.approx(150, abs=1)
    finally:
        doc.close()


def test_dpi_real_independe_do_dpi_de_leitura(tmp_path):
    import fitz

    from core.pdf_io import dpi_real_da_pagina, pagina_para_array

    caminho = tmp_path / "scan.pdf"
    _pdf_com_imagem(caminho, largura_px=900, altura_px=1200, largura_pt=576)

    doc = fitz.open(caminho)
    try:
        medido = dpi_real_da_pagina(doc, 0)
        for dpi_de_leitura in (72, 150, 300):
            pagina_para_array(doc, 0, dpi=dpi_de_leitura)
            assert dpi_real_da_pagina(doc, 0) == pytest.approx(medido)
        assert medido == pytest.approx(112.5, abs=1)
    finally:
        doc.close()


def test_scan_ruim_dispara_o_alerta_de_qualidade(tmp_path):
    from core.analise import DPI_BAIXO, RESOLUCAO_BAIXA, analisar_folha
    from core.dividir import Lombada
    from core.endireitar import Inclinacao
    from core.recortar import Recorte

    alertas = analisar_folha(
        folha_dupla(), Lombada(0.5, 0.9, True), Inclinacao(0.0, 1.0),
        Recorte.inteiro(), vai_dividir=False, vai_endireitar=False,
        vai_cortar=False, dpi_real=112.0,
    )
    assert RESOLUCAO_BAIXA in alertas, f"112 DPI e menos que {DPI_BAIXO}"


def test_scan_bom_nao_dispara_o_alerta(tmp_path):
    from core.analise import RESOLUCAO_BAIXA, analisar_folha
    from core.dividir import Lombada
    from core.endireitar import Inclinacao
    from core.recortar import Recorte

    alertas = analisar_folha(
        folha_dupla(), Lombada(0.5, 0.9, True), Inclinacao(0.0, 1.0),
        Recorte.inteiro(), vai_dividir=False, vai_endireitar=False,
        vai_cortar=False, dpi_real=300.0,
    )
    assert RESOLUCAO_BAIXA not in alertas


# --- caminhos em disco -----------------------------------------------------
#
# Estes testes existem porque acentuar um caminho ja quebrou o programa duas
# vezes: o historico.json virou histórico.json e a pasta de saida ganhou um
# til, deixando para tras o que o usuario ja tinha gravado.

def test_nomes_de_arquivo_nao_tem_acento():
    import historico
    import historico_acoes

    for nome in (historico.ARQUIVO_HISTORICO, historico_acoes.ARQUIVO_ACOES,
                 historico_acoes.ARQUIVO_POSICAO):
        assert nome.isascii(), f"nome de arquivo com acento: {nome}"


def test_pasta_de_saida_reaproveita_a_de_uma_versao_anterior(monkeypatch, tmp_path):
    """Achar a pasta antiga vale mais que criar uma nova com o nome bonito."""
    import historico

    documentos = tmp_path / "Documents"
    documentos.mkdir()
    antiga = documentos / "Editor de Impressao"     # nome da versão anterior
    antiga.mkdir()
    (antiga / "livro pronto.pdf").write_bytes(b"x")

    monkeypatch.setattr(historico.Path, "home", staticmethod(lambda: tmp_path))
    escolhida = historico.pasta_de_saida_padrao()

    assert escolhida == antiga, "os PDFs ja gerados ficariam orfaos"
    assert (escolhida / "livro pronto.pdf").exists()


def test_pasta_de_saida_nova_usa_o_nome_atual(monkeypatch, tmp_path):
    import historico

    (tmp_path / "Documents").mkdir()
    monkeypatch.setattr(historico.Path, "home", staticmethod(lambda: tmp_path))

    escolhida = historico.pasta_de_saida_padrao()
    assert escolhida.name == historico.NOMES_DA_PASTA_DE_SAIDA[0]
    assert escolhida.is_dir()


def test_pasta_sugerida_cai_no_padrao_quando_a_ultima_sumiu(monkeypatch, tmp_path):
    monkeypatch.setattr(configuracoes, "ler", lambda _c: str(tmp_path / "apagada"))
    monkeypatch.setattr(
        "historico.pasta_de_saida_padrao", lambda: tmp_path / "padrao"
    )
    (tmp_path / "padrao").mkdir()
    assert configuracoes.pasta_de_saida_sugerida() == tmp_path / "padrao"


def test_nome_de_saida_sugerido_descreve_o_que_foi_feito():
    from modelos import nome_de_saida_sugerido

    projeto = projeto_de_teste()
    projeto.nome = "Gradus Primus"
    projeto.limpar, projeto.filtro_padrao = True, PRETO_E_BRANCO
    assert nome_de_saida_sugerido(projeto) == "Gradus Primus - preto e branco.pdf"

    projeto.montar_cadernos = True
    assert nome_de_saida_sugerido(projeto) == "Gradus Primus - cadernos.pdf"


def test_nome_de_saida_tira_caractere_proibido_no_windows():
    from modelos import nome_de_saida_sugerido

    projeto = projeto_de_teste()
    projeto.nome = 'Missal: Romano/1962'
    projeto.limpar = False
    nome = nome_de_saida_sugerido(projeto)
    assert not any(c in nome for c in '<>:"/\\|?*')


def test_caminho_rapido_so_com_cadernos():
    projeto = projeto_de_teste()
    projeto.montar_cadernos = True
    projeto.dividir_folhas = projeto.limpar = False
    projeto.endireitar = projeto.cortar_bordas = False
    assert projeto.so_cadernos is True

    projeto.paginas[0].apagada = True
    assert projeto.so_cadernos is False, "apagar página exige regravar o PDF"


def test_pagina_toda_desenho_nao_e_cobrada_como_texto():
    """Pagina que o detector diz ser desenho de ponta a ponta nao tem letra.

    A pagina 199 do Catecismo e uma estampa colorida de pagina inteira, sem uma
    letra. A conta de tinta e cor a chamava de TEXTO - a tinta e so 7%, porque a
    estampa e clara, e o "tem cor" saia falso por um fio: a analise roda a 150
    DPI e ali a fracao de pixels coloridos da 0,0499 contra o limiar de 0,05.
    Resultado: a regua cobrava dela os vazios internos das letras e reprovava os
    tres filtros por "as letras entupiram", numa pagina sem letra nenhuma.
    """
    import avaliar
    from core.selecao import GRAVURA, LETRA, RETANGULO, Regiao, Selecao

    folha_inteira = [(0.0, 0.0), (1.0, 1.0)]

    so_desenho = Selecao()
    so_desenho.acrescentar(
        Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=folha_inteira))
    assert avaliar.e_so_desenho(so_desenho, 400, 300)

    # com texto marcado, ainda que pouco, a regua continua cobrando letra
    com_texto = Selecao()
    com_texto.acrescentar(
        Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=folha_inteira))
    com_texto.acrescentar(
        Regiao(tipo=LETRA, forma=RETANGULO,
               pontos=[(0.0, 0.0), (1.0, 0.2)]))
    assert not avaliar.e_so_desenho(com_texto, 400, 300)

    # sem deteccao nenhuma nao se afrouxa nada
    assert not avaliar.e_so_desenho(Selecao(), 400, 300)


def test_folha_inteira_marcada_papel_sai_em_branco():
    """Marcar a folha toda como papel quer dizer "quero esta folha em branco".

    Serve para a capa que nao se quer no livro reimpresso. Antes sobrava a
    etiqueta da biblioteca e a sujeira da borda no meio do branco, porque a
    protecao que impede o branco de comer a borda da letra tambem protegia isso.
    Marcar SO UM PEDACO como papel continua protegendo a letra.
    """
    import cv2
    from core.filtros import MELHORAR, aplicar_filtro_com_selecao
    from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

    pagina = np.full((300, 220, 3), 150, np.uint8)
    pagina[40:70, 30:190] = 20          # uma etiqueta escura, como a do Boecio
    pagina[:, :6] = 15                  # a lombada escura da borda

    inteira = Selecao()
    inteira.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO,
                               pontos=[(0.0, 0.0), (1.0, 1.0)], origem=MAO))
    saida, _mono = aplicar_filtro_com_selecao(pagina.copy(), MELHORAR, inteira)
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY) if saida.ndim == 3 else saida
    assert float((cinza < 250).mean()) == 0.0, "sobrou coisa na folha em branco"

    so_o_topo = Selecao()
    so_o_topo.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO,
                                 pontos=[(0.0, 0.0), (1.0, 0.12)], origem=MAO))
    saida2, _m = aplicar_filtro_com_selecao(pagina.copy(), MELHORAR, so_o_topo)
    cinza2 = cv2.cvtColor(saida2, cv2.COLOR_BGR2GRAY) if saida2.ndim == 3 else saida2
    assert float((cinza2 < 250).mean()) > 0.05, "a etiqueta tinha de sobreviver"
