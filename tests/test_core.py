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
    """50 tem que dar exatamente o k=0,20, que e o padrão para livro."""
    assert k_do_sauvola(50) == pytest.approx(0.20)
    assert k_do_sauvola(0) == pytest.approx(0.40)
    assert k_do_sauvola(100) == pytest.approx(0.06)


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
