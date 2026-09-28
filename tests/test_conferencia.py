"""A página de antes/depois de qualquer item (conferencia.py, item 0.4 do plano).

Testes de máquina: as partes puras (ler a lista, escolher as colunas, recortar
pelo detalhe, nome da pasta, item que não existe), o alinhamento que acha o
mesmo ponto do livro em cada coluna, e uma conferência inteira num gabarito de
mentira, com o "depois" vindo de uma pasta de imagens prontas (sem processar
pelo programa, que é lento demais para um teste automático).

Se a lista do gabarito (gabarito/lista.json) mudar de estrutura, os testes que
leem a lista de verdade quebram de propósito: o conferencia.py lê essa lista.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pytest

import conferencia
from conferencia import (
    ANTERIOR,
    CAMSCANNER,
    ORIGINAL,
    RESULTADO,
    SCANTAILOR,
    ErroDeUso,
)

LISTA_DE_VERDADE = Path(__file__).resolve().parent.parent / "gabarito" / "lista.json"


@pytest.fixture(scope="module")
def lista():
    return conferencia.ler_lista(LISTA_DE_VERDADE)


def funcao_de_exemplo(caminho_pdf, antes):
    """Usada pelo teste do --funcao: devolve a imagem clareada, e (imagem, x)
    como os filtros do programa."""
    return cv2.add(antes, 10), False


# ---------------------------------------------------------------------------
# a lista do gabarito
# ---------------------------------------------------------------------------


def test_paginas_de_um_item_que_existe(lista):
    assert conferencia.paginas_do_item(lista, "6.7") == ["horas_p026", "horas_p027", "escola_p035"]


def test_item_que_nao_existe_diz_quais_existem(lista):
    with pytest.raises(ErroDeUso) as erro:
        conferencia.paginas_do_item(lista, "9.9")
    mensagem = str(erro.value)
    assert "9.9" in mensagem and "não existe" in mensagem
    for item in ("fase1", "2.2", "6.2", "6.7"):
        assert item in mensagem
    assert "Comparação final com o CamScanner" in mensagem


def test_sem_item_tambem_lista_os_itens(lista):
    with pytest.raises(ErroDeUso) as erro:
        conferencia.paginas_do_item(lista, None)
    assert "fase1" in str(erro.value)


def test_paginas_pedidas_trocam_a_lista_do_item(lista):
    assert conferencia.paginas_do_item(lista, "6.7", ["escola_p035"]) == ["escola_p035"]


def test_pagina_pedida_que_nao_existe_e_dita_pelo_nome(lista):
    with pytest.raises(ErroDeUso) as erro:
        conferencia.paginas_do_item(lista, "6.7", ["horas_p026", "nao_existe_p999"])
    assert "nao_existe_p999" in str(erro.value)


def test_separar_paginas_na_ordem_sem_repetir():
    assert conferencia.separar_paginas(" a, b,,c,a ") == ["a", "b", "c"]
    assert conferencia.separar_paginas("") == []


def test_toda_pagina_do_gabarito_tem_detalhe_valido(lista):
    """O "detalhe" foi escolhido olhando cada página (item 0.4). Página nova
    no gabarito sem detalhe mostraria a página inteira no lugar do ampliado."""
    for pid, entrada in lista["paginas"].items():
        detalhe = conferencia.ler_detalhe(entrada)
        assert detalhe is not None, f"{pid} não tem detalhe"
        x0, y0, x1, y1 = detalhe
        assert (x1 - x0) * (y1 - y0) < 0.6, f"o detalhe de {pid} é quase a página inteira"


def test_toda_foto_do_camscanner_tem_o_recorte_da_pagina(lista):
    for chave, entrada in lista["camscanner"].items():
        for foto in ("original", "magico_pro"):
            caixa = conferencia.recorte_da_captura(entrada, foto)
            assert caixa is not None, f"{chave} ({foto}) sem recorte_da_pagina"
            arquivo = LISTA_DE_VERDADE.parent / entrada[foto]
            if arquivo.is_file():   # a pasta do gabarito fica fora do git
                altura, largura = conferencia.ler_imagem(arquivo).shape[:2]
                x0, y0, x1, y1 = caixa
                assert x1 <= largura and y1 <= altura
                # a página ocupa uns 520 px de largura no meio da captura
                assert 300 <= x1 - x0 <= largura


def test_detalhe_invalido_e_recusado():
    for valor in ([0.5, 0.1, 0.4, 0.3], [0, 0, 1.2, 1], [0.1, 0.2, 0.3], "0,0,1,1"):
        with pytest.raises(ErroDeUso):
            conferencia.ler_detalhe({"detalhe": valor})
    assert conferencia.ler_detalhe({}) is None


# ---------------------------------------------------------------------------
# as colunas
# ---------------------------------------------------------------------------


def test_colunas_com_o_camscanner(lista):
    assert conferencia.escolher_colunas(lista, "horas_p026", False) == [ORIGINAL, RESULTADO, CAMSCANNER]


def test_camscanner_e_achado_pela_pagina_do_gabarito_e_nao_pelo_nome_das_fotos(lista):
    """As fotos se chamam escola_p037 (número impresso), mas são a p. 35 do PDF."""
    assert CAMSCANNER in conferencia.escolher_colunas(lista, "escola_p035", False)
    assert conferencia.referencia_camscanner(lista, "escola_p035")["chave"] == "escola_p037"


def test_colunas_com_o_scantailor(lista):
    assert conferencia.escolher_colunas(lista, "horas_p011", False) == [ORIGINAL, RESULTADO, SCANTAILOR]


def test_scantailor_sem_saida_nao_vira_coluna(lista):
    assert conferencia.escolher_colunas(lista, "rhetorica_p073", False) == [ORIGINAL, RESULTADO]


def test_rodada_anterior_vem_logo_depois_do_original(lista):
    assert conferencia.escolher_colunas(lista, "palatino_p005", True) == [
        ORIGINAL, ANTERIOR, RESULTADO, SCANTAILOR]


# ---------------------------------------------------------------------------
# recortar pelo detalhe
# ---------------------------------------------------------------------------


def test_detalhe_em_pixels():
    assert conferencia.caixa_em_pixels((0.1, 0.2, 0.5, 0.6), 1000, 500) == (100, 100, 500, 300)
    assert conferencia.caixa_em_pixels((0.0, 0.0, 1.0, 1.0), 640, 480) == (0, 0, 640, 480)


def test_detalhe_minusculo_tem_pelo_menos_um_pixel():
    x0, y0, x1, y1 = conferencia.caixa_em_pixels((0.5, 0.5, 0.5001, 0.5001), 100, 100)
    assert x1 > x0 and y1 > y0


def test_recortar_dentro_da_imagem_devolve_os_mesmos_pixels():
    img = np.random.default_rng(1).integers(0, 255, (60, 80, 3), dtype=np.uint8)
    assert np.array_equal(conferencia.recortar(img, (10, 5, 30, 25)), img[5:25, 10:30])


def test_o_que_cai_fora_da_imagem_vira_xadrez_e_o_tamanho_se_mantem():
    img = np.zeros((50, 50, 3), np.uint8)
    corte = conferencia.recortar(img, (40, 40, 70, 60))
    assert corte.shape == (20, 30, 3)
    assert np.all(corte[:10, :10] == 0)            # o pedaço que existe
    fora = corte[:, 10:]
    assert set(np.unique(fora)) <= {206, 236}       # o resto é o quadriculado


# ---------------------------------------------------------------------------
# nomes, tempos, filtros
# ---------------------------------------------------------------------------


def test_nome_da_pasta_tem_o_item_e_a_hora():
    assert conferencia.nome_da_pasta("6.7", datetime(2026, 9, 25, 16, 40)) == "6.7-2026-09-25-1640"
    assert conferencia.nome_da_pasta("fase1", datetime(2026, 1, 2, 3, 4)) == "fase1-2026-01-02-0304"


def test_nome_da_pasta_sem_acento_e_sem_caractere_proibido():
    nome = conferencia.nome_da_pasta("Fase 1: ação/teste", datetime(2026, 9, 25, 16, 40))
    assert nome == "Fase-1-acao-teste-2026-09-25-1640"
    assert not any(c in nome for c in '<>:"/\\|?* ')


def test_nome_do_relatorio_nao_tem_ponto():
    """Até 28/09 o relatorio.gravar cortava o nome no último ponto:
    "conferencia-6.7" virava "conferencia-6.md" (aconteceu na primeira rodada
    de verdade, 25/09). Consertado lá; o hífen fica para as rodadas novas
    terem o mesmo nome das antigas."""
    assert conferencia.nome_do_relatorio("6.7") == "conferencia-6-7"
    assert conferencia.nome_do_relatorio("fase1") == "conferencia-fase1"


def test_duas_rodadas_no_mesmo_minuto_nao_se_misturam(tmp_path):
    quando = datetime(2026, 9, 25, 16, 40)
    primeira = conferencia.criar_pasta(tmp_path, "6.7", quando)
    segunda = conferencia.criar_pasta(tmp_path, "6.7", quando)
    assert primeira != segunda and primeira.is_dir() and segunda.is_dir()
    assert segunda.name == "6.7-2026-09-25-1640-2"


@pytest.mark.parametrize("segundos, esperado", [
    (0.4, "0,4 segundo"),
    (17.56, "17,6 segundos"),
    (60, "1 minuto"),
    (125, "2 minutos e 5 segundos"),
    (None, "não medido"),
])
def test_tempo_em_portugues(segundos, esperado):
    assert conferencia.formatar_segundos(segundos) == esperado


def test_filtro_pelo_nome_que_a_pessoa_escreve():
    assert conferencia.achar_filtro("Mágico pro") == "magico_pro"
    assert conferencia.achar_filtro("preto e branco") == "preto_e_branco"
    assert conferencia.achar_filtro("MELHORAR") == "melhorar"
    with pytest.raises(ErroDeUso):
        conferencia.achar_filtro("sépia")


@pytest.mark.parametrize("aspecto, quantos, esperado", [
    (0.7, 5, 5),    # cinco páginas em pé cabem numa linha
    (2.4, 3, 3),    # três detalhes largos também
    (3.8, 3, 1),    # faixa muito larga: uma embaixo da outra
    (2.0, 4, 2),    # quatro largos: 2 + 2, e não 3 + 1
    (1.6, 5, 3),    # cinco detalhes: 3 + 2
    (2.2, 2, 2),
    (0.7, 1, 1),
])
def test_quantos_paineis_por_linha(aspecto, quantos, esperado):
    assert conferencia.paineis_por_linha(aspecto, quantos) == esperado


# ---------------------------------------------------------------------------
# a função do --funcao
# ---------------------------------------------------------------------------


def test_funcao_por_nome_de_modulo():
    funcao = conferencia.carregar_funcao("tests.test_conferencia:funcao_de_exemplo")
    assert funcao is funcao_de_exemplo


def test_funcao_por_caminho_de_arquivo(tmp_path):
    arquivo = tmp_path / "minha_funcao.py"
    arquivo.write_text("def inverter(pdf, antes):\n    return 255 - antes\n", encoding="utf-8")
    fonte = conferencia.FonteFuncao(f"{arquivo}:inverter")
    antes = np.full((10, 10, 3), 200, np.uint8)
    depois = fonte.obter("x", tmp_path / "x.pdf", antes)
    assert depois.imagem is not None and int(depois.imagem[0, 0, 0]) == 55
    assert depois.segundos is not None
    assert int(antes[0, 0, 0]) == 200, "a função não pode estragar o original"


def test_funcao_que_da_erro_vira_aviso_e_nao_derruba(tmp_path):
    arquivo = tmp_path / "quebrada.py"
    arquivo.write_text("def f(pdf, antes):\n    raise ValueError('de propósito')\n", encoding="utf-8")
    depois = conferencia.FonteFuncao(f"{arquivo}:f").obter("x", tmp_path / "x.pdf",
                                                           np.zeros((5, 5, 3), np.uint8))
    assert depois.imagem is None and "de propósito" in depois.aviso


@pytest.mark.parametrize("especificacao", ["sem_dois_pontos", "modulo_que_nao_existe:f",
                                           "tests.test_conferencia:nao_existe"])
def test_funcao_mal_escrita_explica(especificacao):
    with pytest.raises(ErroDeUso):
        conferencia.carregar_funcao(especificacao)


# ---------------------------------------------------------------------------
# o texto: PRONTO PARA CONFERIR só com opinião, e nunca "aprovado"
# ---------------------------------------------------------------------------


def _dados_minimos(opiniao=None):
    return {
        "item": "6.7", "nome_do_item": "Comparação final com o CamScanner",
        "quando": "2026-09-25T16:40:00", "comando": "conferencia.py 6.7",
        "pasta": "relatorios\\conferir\\6.7-2026-09-25-1640",
        "origem": {"tipo": "programa", "filtro": "magico_pro", "nome_do_filtro": "Mágico pro",
                   "detector": True, "aquecimento_s": 0.9, "dpi": 300},
        "anterior": None, "opiniao": opiniao, "duracao_s": 30.0, "versoes": "Python 3.14",
        "paginas": [{
            "numero": 1, "id": "horas_p026", "livro_nome": "Livro de Horas - Luís XIV",
            "pagina": 26, "para_que": "calendário NOVEMBRE", "a_confirmar": True,
            "observacao": "", "aspecto_detalhe": 1.6, "tempo_s": 17.6, "tempo_analise_s": 0.4,
            "partes": 2, "avisos": [], "falhou": False,
            "colunas": [
                {"chave": ORIGINAL, "titulo": "1. Original", "painel": "paineis/a.jpg",
                 "detalhe": "paineis/a-detalhe.jpg", "cheia": "../x.png", "aspecto": 0.67},
                {"chave": RESULTADO, "titulo": "2. Resultado: Mágico pro", "painel": None,
                 "detalhe": None, "cheia": None, "aviso": "o programa deu erro", "aspecto": None},
            ]}],
    }


def test_sem_opiniao_diz_que_falta_e_nao_diz_pronto():
    texto = conferencia.montar_texto(_dados_minimos())
    assert "Falta a opinião do verificador" in texto
    assert "PRONTO PARA CONFERIR" not in texto
    assert "aprovad" not in texto.lower()


def test_com_opiniao_diz_pronto_e_traz_o_texto_do_verificador():
    texto = conferencia.montar_texto(_dados_minimos("O papel saiu branco. Ressalva: a borda."))
    assert "PRONTO PARA CONFERIR" in texto
    assert "O papel saiu branco. Ressalva: a borda." in texto
    assert "Falta a opinião do verificador" not in texto
    assert "aprovad" not in texto.lower()


def test_bloco_da_pagina_tem_o_que_olhar_o_tempo_e_os_avisos():
    texto = conferencia.montar_texto(_dados_minimos())
    assert "**O que olhar:** calendário NOVEMBRE" in texto
    assert "Processada em 17,6 segundos" in texto
    assert "a confirmar" in texto
    assert "dividiu esta folha em 2 páginas" in texto
    assert "Sem imagem: o programa deu erro" in texto
    assert "resultado-alvo" in texto   # diz por que o Mágico pro é o padrão


def test_as_paginas_vem_antes_da_explicacao_longa():
    """O Samuel tem 10 minutos: a primeira página aparece logo, a explicação
    de como ler fica no fim."""
    texto = conferencia.montar_texto(_dados_minimos())
    assert texto.index("## 1. ") < texto.index("## Como ler esta página")


def test_titulo_da_coluna_fica_na_mesma_celula_da_imagem():
    """Numa linha de cabeçalho separada, a quebra de página do PDF deixava o
    título numa folha e a imagem na seguinte."""
    colunas = _dados_minimos()["paginas"][0]["colunas"]
    tabela = conferencia.tabela_de_paineis(colunas, "painel", 0.67)
    assert "<th" not in tabela
    assert '<td><b>1. Original</b><a href="../x.png"' in tabela
    assert 'width="' in tabela   # a largura que o PDF usa


# ---------------------------------------------------------------------------
# alinhamento: o mesmo ponto do livro em cada coluna
# ---------------------------------------------------------------------------


def _pagina_de_mentira(largura=900, altura=1300, semente=0):
    """Papel amarelado com "letras" e "gravuras" aleatórias: pontos de sobra
    para o alinhamento, sem repetir palavra (repetição confunde o SIFT)."""
    rng = np.random.default_rng(semente)
    img = np.full((altura, largura, 3), (200, 225, 235), np.uint8)
    letras = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    y = 50
    while y < altura - 30:
        x = 30
        while x < largura - 140:
            palavra = "".join(rng.choice(list(letras), int(rng.integers(3, 8))))
            escala = float(rng.uniform(0.6, 1.1))
            cv2.putText(img, palavra, (x, y), cv2.FONT_HERSHEY_SIMPLEX, escala,
                        (40, 40, 60), 2, cv2.LINE_AA)
            x += int(18 * escala * len(palavra)) + 25
        y += 38
    for _ in range(15):
        centro = (int(rng.integers(40, largura - 40)), int(rng.integers(40, altura - 40)))
        cv2.circle(img, centro, int(rng.integers(8, 45)), (30, 60, 150), 3)
    return img


def _entortar(img, escala, graus, dx, dy, corte=0.04):
    """Como o programa faz: corta as bordas, endireita, muda o tamanho.
    Devolve (imagem, matriz original -> nova)."""
    altura, largura = img.shape[:2]
    matriz = cv2.getRotationMatrix2D((largura / 2, altura / 2), graus, escala)
    matriz[:, 2] += (dx - corte * largura * escala, dy - corte * altura * escala)
    tamanho = (int(largura * escala * (1 - 2 * corte)), int(altura * escala * (1 - 2 * corte)))
    nova = cv2.warpAffine(img, matriz, tamanho, borderValue=(255, 255, 255))
    return nova, matriz


def test_alinhamento_acha_o_mesmo_ponto_depois_de_cortar_girar_e_reduzir():
    original = _pagina_de_mentira()
    depois, verdade = _entortar(original, escala=0.8, graus=1.5, dx=5, dy=-3)
    alinhamento = conferencia.alinhar(conferencia.achar_pontos(original),
                                      conferencia.achar_pontos(depois))
    assert alinhamento.certo
    caixa = (200, 300, 500, 500)
    cantos = np.array([[200, 300], [500, 300], [500, 500], [200, 500]], float)
    esperado = cantos @ verdade[:, :2].T + verdade[:, 2]
    levados, _, certo = conferencia.levar_detalhe(caixa, (0, 0, 1, 1), alinhamento, depois.shape)
    assert certo
    assert np.abs(levados - esperado).max() < 4.0


def test_copia_bem_menor_alinha_com_a_pagina_do_mesmo_tamanho():
    """A foto do CamScanner da "Escola" tem 426 pixels de largura; o original
    reduzido, 1446. Com as duas páginas do mesmo tamanho o alinhamento acerta
    (achado na primeira rodada de verdade, 25/09). Aqui a cópia tem metade do
    tamanho: nesta página de mentira, sem igualar os tamanhos, o alinhamento
    não passa nas conferências (medido); a 0,28 a página de mentira já não tem
    ponto nenhum reconhecível, e a foto de verdade tem (a gravura colorida)."""
    original = _pagina_de_mentira(largura=1500, altura=2100, semente=3)
    pequena, verdade = _entortar(original, escala=0.5, graus=0.8, dx=2, dy=-4, corte=0.0)
    pontos = conferencia.achar_pontos(original)
    alinhamento = conferencia.alinhar(pontos, conferencia.achar_pontos(
        pequena, largura_da_pagina=pontos.escala * original.shape[1]))
    assert alinhamento.certo
    cantos = np.array([[300, 400], [900, 400], [900, 900], [300, 900]], float)
    levados, _, _ = conferencia.levar_detalhe((300, 400, 900, 900), (0, 0, 1, 1), alinhamento,
                                              pequena.shape)
    assert np.abs(levados - (cantos @ verdade[:, :2].T + verdade[:, 2])).max() < 3.0


def test_detalhe_que_o_programa_cortou_fica_quadriculado_e_nao_muda_de_lugar():
    matriz = np.array([[1.0, 0.0, -50.0], [0.0, 1.0, 0.0]])   # 50 pixels cortados à esquerda
    alinhamento = conferencia.Alinhamento(matriz, 100, True)
    _, caixa, certo = conferencia.levar_detalhe((0, 0, 100, 100), (0, 0, 0.1, 0.1),
                                                alinhamento, (1000, 800, 3))
    assert certo and caixa == (-50, 0, 50, 100)
    assert conferencia.fracao_dentro(caixa, (1000, 800, 3)) == pytest.approx(0.5)


def test_imagem_sem_nada_em_comum_cai_na_posicao_proporcional_e_avisa():
    original = _pagina_de_mentira(semente=1)
    outra = _pagina_de_mentira(semente=2)
    alinhamento = conferencia.alinhar(conferencia.achar_pontos(original),
                                      conferencia.achar_pontos(outra))
    _, caixa, certo = conferencia.levar_detalhe((90, 130, 450, 520), (0.1, 0.1, 0.5, 0.4),
                                                alinhamento, outra.shape)
    assert not certo
    assert caixa == conferencia.caixa_em_pixels((0.1, 0.1, 0.5, 0.4), 900, 1300)


def test_conteudo_pequeno_numa_folha_branca_grande_e_recortado_para_alinhar():
    """A saída do ScanTailor: o conteúdo no meio de uma folha enorme e branca."""
    folha = np.full((3000, 2000), 255, np.uint8)
    folha[1000:1600, 700:1100] = 30
    a, b, c, d = conferencia.caixa_do_conteudo(folha)
    assert a < 700 < 1100 < c and b < 1000 < 1600 < d
    assert (c - a) * (d - b) < 0.2 * 3000 * 2000


# ---------------------------------------------------------------------------
# uma conferência inteira, num gabarito de mentira
# ---------------------------------------------------------------------------


def _gabarito_de_mentira(raiz: Path) -> tuple[Path, Path]:
    """Duas páginas, uma com foto do CamScanner (captura de tela com a página
    no meio), e uma pasta de "depois" com as duas páginas cortadas, giradas e
    reduzidas. Devolve (gabarito, pasta do depois)."""
    gabarito = raiz / "gabarito"
    (gabarito / "paginas").mkdir(parents=True)
    (gabarito / "camscanner").mkdir()
    depois = raiz / "depois"
    depois.mkdir()

    paginas = {}
    for numero, semente in ((1, 10), (2, 11)):
        pid = f"teste_p{numero:03d}"
        pagina = _pagina_de_mentira(semente=semente)
        conferencia.gravar_imagem(gabarito / "paginas" / f"{pid}.png", pagina)
        nova, _ = _entortar(pagina, escala=0.75, graus=-1.0, dx=0, dy=0)
        extensao = ".png" if numero == 1 else ".jpg"   # as duas extensões são aceitas
        conferencia.gravar_imagem(depois / f"{pid}{extensao}", nova, 95)
        paginas[pid] = {
            "livro": "C:\\livros\\Livro de Teste.pdf", "pagina": numero,
            "pdf": f"paginas/{pid}.pdf", "png": f"paginas/{pid}.png",
            "para_que": f"o que olhar na página {numero}",
            "a_confirmar": numero == 2, "observacao": "página a confirmar" if numero == 2 else "",
            "detalhe": [0.1, 0.1, 0.5, 0.4] if numero == 1 else [0.5, 0.6, 0.9, 0.9],
        }

    # a captura de tela: fundo escuro do aplicativo e a página pequena no meio
    captura = np.full((1280, 576, 3), (28, 28, 30), np.uint8)
    pagina = cv2.imread(str(gabarito / "paginas" / "teste_p001.png"))
    pequena = cv2.resize(pagina, (520, 751), interpolation=cv2.INTER_AREA)
    captura[82:82 + 751, 28:548] = pequena
    conferencia.gravar_imagem(gabarito / "camscanner" / "foto_magico_pro.jpg", captura, 95)
    conferencia.gravar_imagem(gabarito / "camscanner" / "foto_original.jpg", captura, 95)

    lista = {
        "paginas": paginas,
        "camscanner": {"foto": {
            "pagina_gabarito": "teste_p001", "original": "camscanner/foto_original.jpg",
            "magico_pro": "camscanner/foto_magico_pro.jpg",
            "recorte_da_pagina": {"original": [28, 82, 548, 833], "magico_pro": [28, 82, 548, 833]}}},
        "scantailor_24_09": {},
        "itens": {"6.9": ["teste_p001", "teste_p002"]},
        "nomes_dos_itens": {"6.9": "Item de teste"},
    }
    (gabarito / "lista.json").write_text(json.dumps(lista, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    return gabarito, depois


def _rodar(argv, gabarito, destino):
    return conferencia.main(argv, gabarito=gabarito, destino=destino,
                            referencias=destino / "_referencias")


def test_conferencia_inteira_com_imagens_prontas(tmp_path):
    gabarito, depois = _gabarito_de_mentira(tmp_path)
    destino = tmp_path / "conferir"

    assert _rodar(["6.9", "--pasta-depois", str(depois)], gabarito, destino) == 0

    (pasta,) = [p for p in destino.iterdir() if p.name.startswith("6.9-")]
    for nome in ("conferencia-6-9.md", "conferencia-6-9.html", "conferencia-6-9.pdf", "dados.json",
                 "resultado/teste_p001.png", "resultado/teste_p002.jpg"):
        assert (pasta / nome).is_file(), nome
    # a imagem pronta é copiada byte a byte, sem gravar de novo
    assert (pasta / "resultado" / "teste_p002.jpg").read_bytes() == (depois / "teste_p002.jpg").read_bytes()
    dados = json.loads((pasta / "dados.json").read_text(encoding="utf-8"))
    primeira, segunda = dados["paginas"]
    assert [c["chave"] for c in primeira["colunas"]] == [ORIGINAL, RESULTADO, CAMSCANNER]
    assert [c["chave"] for c in segunda["colunas"]] == [ORIGINAL, RESULTADO]
    for coluna in primeira["colunas"][1:] + segunda["colunas"][1:]:
        assert coluna["alinhamento"]["certo"], coluna["chave"]
        assert (pasta / coluna["painel"]).is_file() and (pasta / coluna["detalhe"]).is_file()

    # o detalhe do Resultado caiu onde a transformação de verdade o leva
    _, verdade = _entortar(np.zeros((1300, 900, 3), np.uint8), escala=0.75, graus=-1.0, dx=0, dy=0)
    cantos = np.array([[90, 130], [450, 130], [450, 520], [90, 520]], float)
    esperado = cantos @ verdade[:, :2].T + verdade[:, 2]
    caixa = primeira["colunas"][1]["caixa"]
    assert abs(caixa[0] - esperado[:, 0].min()) < 6 and abs(caixa[3] - esperado[:, 1].max()) < 6

    # o recorte da foto do CamScanner ficou guardado uma vez só
    assert list((destino / "_referencias" / "camscanner").glob("*.png"))

    texto = (pasta / "conferencia-6-9.md").read_text(encoding="utf-8")
    assert "Falta a opinião do verificador" in texto
    assert "PRONTO PARA CONFERIR" not in texto
    assert "aprovad" not in texto.lower()
    assert "o que olhar na página 1" in texto and "a confirmar" in texto

    import fitz

    with fitz.open(pasta / "conferencia-6-9.pdf") as pdf:
        assert sum(len(p.get_images()) for p in pdf) > 0, "o PDF tem de levar os painéis"


def test_rodada_anterior_e_opiniao(tmp_path):
    gabarito, depois = _gabarito_de_mentira(tmp_path)
    destino = tmp_path / "conferir"
    assert _rodar(["6.9", "--pasta-depois", str(depois)], gabarito, destino) == 0
    (primeira,) = list(destino.glob("6.9-*"))

    opiniao = tmp_path / "opiniao.txt"
    opiniao.write_text("As duas páginas saíram iguais à rodada anterior. Ressalva: teste.",
                       encoding="utf-8")
    # o "depois" é a própria conferência anterior: pôr a opinião sem processar de novo
    assert _rodar(["6.9", "--pasta-depois", str(primeira), "--comparar-com", str(primeira),
                   "--opiniao", str(opiniao), "--paginas", "teste_p001"], gabarito, destino) == 0

    (segunda,) = [p for p in destino.glob("6.9-*") if p != primeira]
    dados = json.loads((segunda / "dados.json").read_text(encoding="utf-8"))
    assert [p["id"] for p in dados["paginas"]] == ["teste_p001"]
    assert [c["chave"] for c in dados["paginas"][0]["colunas"]] == [
        ORIGINAL, ANTERIOR, RESULTADO, CAMSCANNER]
    texto = (segunda / "conferencia-6-9.md").read_text(encoding="utf-8")
    assert "PRONTO PARA CONFERIR" in texto
    assert "As duas páginas saíram iguais à rodada anterior." in texto
    assert "Rodada anterior" in texto


def test_item_que_nao_existe_sai_com_mensagem_clara(tmp_path, capsys):
    gabarito, _ = _gabarito_de_mentira(tmp_path)
    assert _rodar(["9.9"], gabarito, tmp_path / "conferir") == 2
    saida = capsys.readouterr().out
    assert "não existe" in saida and "6.9" in saida
    assert not (tmp_path / "conferir").exists(), "pedido errado não cria pasta"


def test_imagem_que_falta_na_pasta_vira_aviso_e_a_pagina_sai_mesmo_assim(tmp_path):
    gabarito, depois = _gabarito_de_mentira(tmp_path)
    (depois / "teste_p002.jpg").unlink()
    destino = tmp_path / "conferir"
    assert _rodar(["6.9", "--pasta-depois", str(depois)], gabarito, destino) == 1
    (pasta,) = list(destino.glob("6.9-*"))
    texto = (pasta / "conferencia-6-9.md").read_text(encoding="utf-8")
    assert "não achei teste_p002.png" in texto
    assert (pasta / "conferencia-6-9.pdf").is_file()
