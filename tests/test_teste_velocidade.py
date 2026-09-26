"""Teste de velocidade (item 0.5 do plano): as partes que tem resposta certa.

As medicoes em si (abrir o livro, trocar de pagina, processar) nao entram aqui:
dependem da maquina e levam minutos. O que se testa e o que nao depende de
gosto nem de maquina: o numero escrito em portugues, qual livro o teste
escolhe, onde o relatorio vai parar, quais paginas entram na medicao, o resumo
das rodadas e o texto do relatorio.

Do item 0.6 (o .exe para o notebook do Kaique): a janela preta nao fecha
sozinha no fim (despedir/executar), o notebook nao dorme no meio da medicao
(computador_acordado), um clique dentro da janela preta nao pausa a medicao
(edicao_rapida_desligada, com a janela de mentira _JanelaPreta no lugar do
Windows), o relatorio diz em que janela o teste rodou - a classica, o
Terminal novo ou nenhuma (janela_do_teste, com as chamadas do Windows de
mentira) -, um Enter apertado durante a medicao nao fecha a janela no fim
(esvaziar_o_teclado, com o Windows de mentira e num console de verdade sem
janela) e a linha "Disco do livro" nao some com o PATH mexido (o PowerShell
e chamado pelo caminho completo). O empacotamento em si e conferido pelo
proprio empacotar_teste_velocidade.py, que confere o pacote que acabou de
gerar.
"""

from __future__ import annotations

import contextlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

import teste_velocidade as tv

# ---------------------------------------------------------------------------
# numeros em portugues
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("segundos, esperado", [
    (0.04, "0,04 segundo"),
    (0.4, "0,4 segundo"),
    (1.52, "1,5 segundo"),
    (2.0, "2,0 segundos"),
    (12.44, "12,4 segundos"),
    (59.97, "1 minuto"),
    (65.2, "1 minuto e 5 segundos"),
    (121, "2 minutos e 1 segundo"),
    (3725, "1 hora e 2 minutos"),
])
def test_segundos_por_extenso(segundos, esperado):
    assert tv.segundos_por_extenso(segundos) == esperado


def test_tempo_que_nao_foi_medido_nao_vira_zero():
    """Um 0 calado ja fez teste de vazamento passar sempre (teste_robustez.py)."""
    assert tv.segundos_por_extenso(None) == "não medido"
    assert tv.segundos_curto(None) == "não medido"


@pytest.mark.parametrize("segundos, esperado", [
    (0.4, "0,4 s"),
    (42.06, "42,1 s"),
    (125, "2 min 5 s"),
    (120, "2 min"),
    (3725, "1 h 2 min"),
])
def test_segundos_curto_para_as_tabelas(segundos, esperado):
    assert tv.segundos_curto(segundos) == esperado


def test_numero_com_virgula_decimal_e_ponto_de_milhar():
    assert tv.formatar_numero(12.44, 1) == "12,4"
    assert tv.formatar_numero(1234.56, 1) == "1.234,6"
    assert tv.formatar_numero(0.5, 2) == "0,50"
    assert tv.formatar_numero(812.4, 0) == "812"


def test_memoria_em_mb():
    assert tv.formatar_mb(812.4) == "812 MB"
    assert tv.formatar_mb(1234.6) == "1.235 MB"
    assert tv.formatar_mb(None) == "não medida"


def test_memoria_em_gb():
    assert tv.formatar_gb(16.0) == "16 GB"
    assert tv.formatar_gb(15.43) == "15,4 GB"


# ---------------------------------------------------------------------------
# onde as coisas ficam
# ---------------------------------------------------------------------------


def test_pasta_do_programa_rodando_pelo_python(tmp_path):
    script = tmp_path / "projeto" / "teste_velocidade.py"
    pasta = tv.pasta_do_programa(congelado=False, executavel=str(tmp_path / "python.exe"),
                                 arquivo=str(script))
    assert pasta == script.parent.resolve()


def test_pasta_do_programa_empacotado_e_a_do_exe_e_nao_a_temporaria(tmp_path):
    """Empacotado, __file__ aponta para a pasta onde o PyInstaller se
    desempacota, que some ao fechar. O livro e os resultados moram ao lado do
    .exe."""
    exe = tmp_path / "entrega" / "teste_velocidade.exe"
    temporaria = tmp_path / "_MEI123" / "teste_velocidade.pyc"
    pasta = tv.pasta_do_programa(congelado=True, executavel=str(exe), arquivo=str(temporaria))
    assert pasta == exe.parent.resolve()


def _pdf_falso(caminho: Path) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(b"%PDF-1.4")
    return caminho


def test_livro_do_argumento_vem_primeiro(tmp_path):
    _pdf_falso(tmp_path / tv.NOME_DO_LIVRO)
    outro = _pdf_falso(tmp_path / "outro livro.pdf")

    achado, _tentados = tv.escolher_livro(str(outro), tmp_path)

    assert achado == outro


def test_livro_ao_lado_do_programa_vem_antes_do_gabarito(tmp_path):
    ao_lado = _pdf_falso(tmp_path / tv.NOME_DO_LIVRO)
    _pdf_falso(tmp_path / "gabarito" / "velocidade" / tv.NOME_DO_LIVRO)

    achado, _tentados = tv.escolher_livro(None, tmp_path)

    assert achado == ao_lado


def test_livro_do_gabarito_quando_nao_ha_outro(tmp_path):
    gabarito = _pdf_falso(tmp_path / "gabarito" / "velocidade" / tv.NOME_DO_LIVRO)

    achado, _tentados = tv.escolher_livro(None, tmp_path)

    assert achado == gabarito


def test_sem_livro_diz_onde_procurou(tmp_path):
    achado, tentados = tv.escolher_livro(None, tmp_path)

    assert achado is None
    assert tentados == [tmp_path / tv.NOME_DO_LIVRO,
                        tmp_path / "gabarito" / "velocidade" / tv.NOME_DO_LIVRO]


def test_argumento_que_nao_existe_nao_troca_de_livro_calado(tmp_path):
    """Quem aponta um livro e erra o caminho tem de saber. Medir o livro
    padrao no lugar daria numeros de outro livro sem ninguem notar."""
    _pdf_falso(tmp_path / tv.NOME_DO_LIVRO)
    sumido = tmp_path / "sumiu.pdf"

    achado, tentados = tv.escolher_livro(str(sumido), tmp_path)

    assert achado is None
    assert tentados == [sumido]


def test_resultados_vao_para_relatorios_quando_roda_do_projeto(tmp_path):
    assert tv.pasta_de_resultados(tmp_path, congelado=False) == (
        tmp_path / "relatorios" / "velocidade")


def test_resultados_vao_para_a_pasta_ao_lado_do_exe(tmp_path):
    assert tv.pasta_de_resultados(tmp_path, congelado=True) == tmp_path / "resultados"


def test_pasta_escolhida_ganha(tmp_path):
    escolhida = tmp_path / "outra"
    assert tv.pasta_de_resultados(tmp_path, congelado=True, escolhida=str(escolhida)) == escolhida


def test_nome_do_relatorio_tem_o_computador_e_a_hora():
    quando = datetime(2026, 9, 25, 15, 7)
    assert tv.nome_base("SAMUEL-PC", quando, rapido=False) == (
        "velocidade-SAMUEL-PC-2026-09-25-1507")


def test_teste_rapido_fica_marcado_no_nome():
    quando = datetime(2026, 9, 25, 15, 7)
    assert tv.nome_base("SAMUEL-PC", quando, rapido=True).endswith("-rapido")


def test_nome_do_computador_vira_nome_de_arquivo_sem_acento():
    """Regra do projeto: caminho de disco sem acento."""
    quando = datetime(2026, 9, 25, 8, 0)
    assert tv.nome_base("Estação São Bento?", quando, rapido=False) == (
        "velocidade-Estacao-Sao-Bento-2026-09-25-0800")


# ---------------------------------------------------------------------------
# quais paginas entram na medicao
# ---------------------------------------------------------------------------


def test_paginas_espalhadas_pelo_livro_inteiro():
    paginas = tv.paginas_espalhadas(300, 20)

    assert len(paginas) == 20
    assert paginas == sorted(set(paginas))
    assert paginas[0] < 20 and paginas[-1] > 280
    assert all(0 <= p < 300 for p in paginas)


@pytest.mark.parametrize("total, quantas", [(300, 20), (20, 3), (40, 20), (7, 3), (600, 20)])
def test_nenhuma_pagina_medida_foi_adiantada_pela_anterior(total, quantas):
    """Ao virar a pagina o programa ja adianta as 3 seguintes. Se a proxima
    pagina medida estivesse entre elas, ja estaria pronta - e a medida "sem
    cache" mentiria."""
    paginas = tv.paginas_espalhadas(total, quantas, folga=3)

    assert all(depois - antes > 3 for antes, depois in zip(paginas, paginas[1:]))


def test_livro_pequeno_demais_mede_menos_trocas():
    assert len(tv.paginas_espalhadas(7, 3, folga=3)) == 1
    assert len(tv.paginas_espalhadas(40, 20, folga=3)) == 10


def test_paginas_espalhadas_de_livro_vazio_ou_de_uma_pagina():
    assert tv.paginas_espalhadas(0, 20) == []
    assert tv.paginas_espalhadas(1, 20) == [0]


def test_paginas_seguidas_do_meio_do_livro():
    assert tv.paginas_seguidas_do_meio(300, 10) == list(range(145, 155))
    assert tv.paginas_seguidas_do_meio(20, 2) == [9, 10]
    assert tv.paginas_seguidas_do_meio(5, 10) == [0, 1, 2, 3, 4]
    assert tv.paginas_seguidas_do_meio(0, 10) == []


def test_processar_comeca_no_inicio_de_uma_folha_dividida():
    """Numa folha dividida as duas metades saem da mesma leitura da folha.
    Comecar numa metade da direita leria uma folha a mais so para meia."""
    metades = ["esquerda", "direita"] * 10
    assert tv.alinhar_ao_comeco_da_folha([9, 10, 11], metades) == [8, 9, 10]
    assert tv.alinhar_ao_comeco_da_folha([8, 9, 10], metades) == [8, 9, 10]
    assert tv.alinhar_ao_comeco_da_folha([3, 4], ["inteira"] * 10) == [3, 4]
    assert tv.alinhar_ao_comeco_da_folha([], metades) == []


# ---------------------------------------------------------------------------
# resumo das rodadas
# ---------------------------------------------------------------------------


def _rodada(abrir=12.4, media=1.8, pior=3.1, magico=48.0, pb=30.2,
            memoria=(400.0, 500.0, 800.0, 700.0)) -> dict:
    """Uma rodada com a mesma forma que rodar_uma_rodada devolve."""
    return {
        "abrir": {"arquivo_s": 0.1, "analise_s": abrir - 0.1, "total_s": abrir,
                  "folhas": 300, "paginas": 300},
        "trocas": {"paginas": [7, 157], "tempos_s": [media * 0.5, pior],
                   "media_s": media, "pior_s": pior, "pior_pagina": 157},
        "processar": {
            "magico_pro": {"segundos": magico, "paginas": 10,
                           "por_pagina_s": magico / 10, "tamanho_saida_mb": 30.0},
            "preto_e_branco": {"segundos": pb, "paginas": 10,
                               "por_pagina_s": pb / 10, "tamanho_saida_mb": 3.0},
        },
        "memoria_pico_mb": dict(zip(
            ("abrir", "trocas", "processar_magico_pro", "processar_preto_e_branco"),
            memoria)),
        "duracao_s": 100.0,
    }


def test_resumo_separa_a_primeira_e_tira_a_mediana():
    rodadas = [_rodada(abrir=12.4), _rodada(abrir=9.8), _rodada(abrir=10.5)]

    resumo = tv.resumir(rodadas)

    assert resumo["abrir_total_s"]["primeira"] == 12.4
    assert resumo["abrir_total_s"]["mediana"] == 10.5
    assert resumo["abrir_total_s"]["rodadas"] == [12.4, 9.8, 10.5]


def test_mediana_nao_e_puxada_por_uma_rodada_ruim():
    rodadas = [_rodada(magico=10.0), _rodada(magico=10.2), _rodada(magico=60.0)]

    assert tv.resumir(rodadas)["processar_magico_pro_s"]["mediana"] == 10.2


def test_resumo_tem_todas_as_medidas_do_relatorio():
    resumo = tv.resumir([_rodada()])

    assert set(resumo) == {
        "abrir_total_s", "abrir_arquivo_s", "abrir_analise_s",
        "troca_media_s", "troca_pior_s",
        "processar_magico_pro_s", "processar_preto_e_branco_s",
    }


def test_pico_de_memoria_diz_em_que_etapa_foi():
    rodadas = [_rodada(memoria=(400.0, 500.0, 800.0, 800.3)),
               _rodada(memoria=(800.3, 800.3, 800.5, 800.5))]

    pico, onde = tv.onde_foi_o_pico(350.0, rodadas)

    assert pico == 800.5
    assert onde == "ao processar em Mágico pro (rodada 1)"


def test_pico_de_memoria_de_uma_rodada_so_nao_fala_em_rodada():
    pico, onde = tv.onde_foi_o_pico(350.0, [_rodada(memoria=(900.0, 900.0, 900.0, 900.0))])

    assert (pico, onde) == (900.0, "ao abrir o livro")


def test_pico_de_memoria_nao_medido():
    rodada = _rodada()
    rodada["memoria_pico_mb"] = dict.fromkeys(rodada["memoria_pico_mb"])

    assert tv.onde_foi_o_pico(None, [rodada]) == (None, None)


# ---------------------------------------------------------------------------
# o texto do relatorio
# ---------------------------------------------------------------------------


def _resultado(rapido=False, rodadas=3, detector=True, na_tomada=True,
               edicao_rapida=None, janela=None) -> dict:
    lista = [_rodada(abrir=12.4, media=1.8, pior=3.1, magico=48.0, pb=30.2),
             _rodada(abrir=9.8, media=1.6, pior=2.7, magico=45.2, pb=29.0),
             _rodada(abrir=10.5, media=1.5, pior=2.9, magico=44.0, pb=28.1)][:rodadas]
    return tv.montar_resultado(
        rapido=rapido,
        quando=datetime(2026, 9, 25, 15, 40),
        maquina={
            "computador": "SAMUEL-PC",
            "processador": "AMD Ryzen 7 5800H with Radeon Graphics",
            "nucleos_fisicos": 8, "nucleos_logicos": 16,
            "memoria_instalada_gb": 16.0, "memoria_utilizavel_gb": 15.4,
            "placas_de_video": ["AMD Radeon(TM) Graphics", "NVIDIA GeForce GTX 1650"],
            "windows": "Windows 11 Home Single Language 25H2 (compilação 26200.9457)",
            "energia": {"na_tomada": na_tomada,
                        "texto": "na tomada" if na_tomada else "na bateria (80%)"},
        },
        versoes={"python": "3.14.0", "pymupdf": "1.28.0", "opencv": "5.0.0",
                 "numpy": "2.5.1", "onnxruntime": "1.28.0", "pyside6": "6.11.1",
                 "empacotado": False},
        livro={"arquivo": "marial_300.pdf", "caminho": "D:/x/marial_300.pdf",
               "tamanho_mb": 67.7, "folhas": 300, "paginas": 300,
               "disco": "SSD", "recortado": False},
        configuracao={"rodadas": rodadas, "trocas": 20, "paginas_processadas": 10,
                      "dpi_analise": 150, "dpi_previa": 110, "dpi_saida": 300,
                      "filtro_do_livro": "magico_pro", "paginas_adiantadas": 3,
                      "lista_trocas": [7, 157], "lista_processadas": list(range(145, 155))},
        preparo={"aquecimento_s": 3.2, "detector_de_regioes": detector, "memoria_mb": 350.0},
        rodadas=lista,
        duracao_total_s=754.0,
        edicao_rapida=edicao_rapida,
        janela=janela,
    )


def test_relatorio_frase_primeiro_numero_depois():
    texto = tv.montar_texto(_resultado())

    assert "Abrir o livro de 300 páginas:** 12,4 segundos na primeira vez, " \
           "10,5 segundos de costume." in texto
    assert "Processar 10 páginas em Mágico pro:** 48,0 segundos na primeira vez" in texto
    assert "Processar 10 páginas em Preto e branco:**" in texto
    assert "Trocar de página:**" in texto
    assert "Memória máxima usada:** 800 MB" in texto


def test_relatorio_usa_virgula_decimal():
    texto = tv.montar_texto(_resultado())

    assert not re.search(r"\d\.\d+ ?(segundo|s\b|MB|GB)", texto), (
        "número com ponto decimal no relatório")


def test_relatorio_mostra_a_maquina():
    texto = tv.montar_texto(_resultado())

    for pedaco in ("AMD Ryzen 7 5800H", "8 físicos, 16 lógicos", "16 GB",
                   "NVIDIA GeForce GTX 1650", "Windows 11 Home Single Language",
                   "25/09/2026 15:40", "na tomada"):
        assert pedaco in texto, pedaco


def test_relatorio_diz_qual_funcao_do_programa_mediu_cada_etapa():
    texto = tv.montar_texto(_resultado())

    for funcao in ("analisar_projeto", "TarefaAnalise", "GerenciadorPrevias.pegar",
                   "pre_carregar", "TarefaProcessar", "processar"):
        assert funcao in texto, funcao


def test_relatorio_do_teste_rapido_avisa_que_nao_vale():
    texto = tv.montar_texto(_resultado(rapido=True, rodadas=1))

    assert "NÃO valem como medição" in texto
    assert "de costume" not in texto, "uma rodada só não tem valor do meio"


def test_relatorio_de_verdade_nao_tem_o_aviso_do_rapido():
    assert "NÃO valem como medição" not in tv.montar_texto(_resultado())


def test_relatorio_avisa_quando_o_detector_nao_carregou():
    texto = tv.montar_texto(_resultado(detector=False))

    assert "NÃO carregou" in texto


def test_relatorio_avisa_quando_o_notebook_estava_na_bateria():
    texto = tv.montar_texto(_resultado(na_tomada=False))

    assert "bateria" in texto.lower()
    assert "Atenção" in texto


def test_paginas_no_relatorio_contam_a_partir_de_1():
    assert tv._lista_de_paginas([7, 22, 37]) == "8, 23 e 38"
    assert tv._lista_de_paginas([3]) == "4"
    assert tv._intervalo_de_paginas(list(range(145, 155))) == "146 a 155"
    assert tv._intervalo_de_paginas([9, 10]) == "10 e 11"
    assert tv._intervalo_de_paginas([3, 10]) == "4 e 11"


def test_relatorio_diz_quais_paginas_foram_medidas():
    texto = tv.montar_texto(_resultado())

    assert "Páginas: 8 e 158." in texto
    assert "nas páginas 146 a 155" in texto


def test_relatorio_de_livro_dividido_fala_em_folhas_e_paginas():
    resultado = _resultado()
    resultado["livro"].update(folhas=300, paginas=600)

    assert "Abrir o livro de 300 folhas (600 páginas depois de dividir):**" in (
        tv.montar_texto(resultado))


def test_relatorio_sai_nos_tres_formatos_e_no_json(tmp_path):
    resultado = _resultado()

    arquivos = tv.gravar_resultados(resultado, tmp_path / "velocidade-SAMUEL-PC-2026-09-25-1540")

    assert {"md", "html", "pdf", "json"} <= set(arquivos)
    for caminho in arquivos.values():
        assert caminho.exists() and caminho.stat().st_size > 0
    assert json.loads(arquivos["json"].read_text(encoding="utf-8")) == resultado


@pytest.mark.parametrize("situacao, pedaco", [
    ("desligado", "ficou desligado durante a medição"),
    ("ja_desligado", "já estava desligado"),
    ("sem_janela", "não havia o que desligar"),
    ("falhou", "o teste pode ter pausado"),
])
def test_relatorio_diz_se_a_edicao_rapida_foi_desligada(situacao, pedaco):
    """Quem le o relatorio precisa saber se um clique na janela preta podia
    ter pausado a medicao sem ninguem ver."""
    resultado = _resultado(edicao_rapida=situacao)

    texto = tv.montar_texto(resultado)

    assert resultado["edicao_rapida"] == situacao, "vai para o .json"
    linhas = [linha for linha in texto.splitlines() if "edição rápida" in linha]
    assert len(linhas) == 1, "uma linha so"
    assert linhas[0].startswith("- **Janela preta:**")
    assert pedaco in linhas[0]


def test_toda_situacao_da_edicao_rapida_tem_frase_no_relatorio():
    for situacao in tv.SITUACOES_DA_EDICAO_RAPIDA:
        assert "edição rápida" in tv.montar_texto(_resultado(edicao_rapida=situacao)), situacao


def test_relatorio_de_antes_da_linha_da_edicao_rapida_abre_sem_ela():
    """Os .json gravados antes desta linha existir nao tem a chave: o
    relatorio refeito deles sai sem a linha, e sem erro."""
    resultado = _resultado()
    resultado.pop("edicao_rapida", None)
    resultado.pop("janela", None)

    texto = tv.montar_texto(resultado)

    assert "edição rápida" not in texto
    assert "Janela preta" not in texto
    assert "## O que este teste não mede" in texto


@pytest.mark.parametrize("situacao, pedaco", [
    ("classica", "rodou na janela clássica do Windows"),
    ("terminal_novo", "rodou no Terminal novo do Windows"),
    ("sem_janela", "rodou sem janela preta"),
    ("desconhecida", "não deu para saber em que janela"),
])
def test_relatorio_diz_em_que_janela_o_teste_rodou(situacao, pedaco):
    """A prova, no relatorio do Kaique, de que a medicao foi na janela
    classica: na mesma linha "Janela preta", antes da edicao rapida."""
    janela = {"situacao": situacao, "classe": "ConsoleWindowClass"}
    resultado = _resultado(edicao_rapida="desligado", janela=janela)

    texto = tv.montar_texto(resultado)

    assert resultado["janela"] == janela, "vai para o .json"
    linhas = [linha for linha in texto.splitlines() if "Janela preta" in linha]
    assert len(linhas) == 1, "uma linha so"
    assert linhas[0].startswith("- **Janela preta:**")
    assert pedaco in linhas[0]
    assert "O modo de edição rápida ficou desligado durante a medição" in linhas[0], (
        "a edicao rapida continua na linha, como frase nova")
    assert linhas[0].index(pedaco) < linhas[0].index("edição rápida"), "primeiro a janela"


def test_toda_situacao_da_janela_tem_frase_no_relatorio():
    for situacao in tv.SITUACOES_DA_JANELA:
        texto = tv.montar_texto(_resultado(janela={"situacao": situacao, "classe": None}))
        linhas = [linha for linha in texto.splitlines() if linha.startswith("- **Janela preta:**")]
        assert len(linhas) == 1, situacao


def test_relatorio_de_antes_da_linha_da_janela_sai_como_antes():
    """Os .json gravados so com a edicao rapida (antes de a janela entrar no
    relatorio) saem com a linha exatamente como era."""
    resultado = _resultado(edicao_rapida="desligado")
    resultado.pop("janela", None)

    linhas = [linha for linha in tv.montar_texto(resultado).splitlines()
              if linha.startswith("- **Janela preta:**")]

    assert linhas == ["- **Janela preta:** o modo de edição rápida ficou desligado durante a "
                      "medição: um clique dentro da janela não pausava o teste."]


@pytest.mark.parametrize("janela", ["classica", {"situacao": ["classica"]}, {"classe": "x"}])
def test_janela_estranha_no_json_nao_quebra_o_relatorio(janela):
    """Um .json mexido a mao (a janela escrita como texto, a situacao numa
    lista, a situacao faltando) sai sem a parte da janela, e sem erro."""
    resultado = _resultado(edicao_rapida="desligado")
    resultado["janela"] = janela

    linhas = [linha for linha in tv.montar_texto(resultado).splitlines()
              if linha.startswith("- **Janela preta:**")]

    assert len(linhas) == 1 and "janela clássica" not in linhas[0]


# ---------------------------------------------------------------------------
# preparar o livro de teste
# ---------------------------------------------------------------------------


def _livro_de_mentira(caminho: Path, paginas: int) -> Path:
    import fitz

    doc = fitz.open()
    for numero in range(1, paginas + 1):
        doc.new_page().insert_text((72, 72), f"pagina {numero}")
    doc.save(caminho)
    doc.close()
    return caminho


def test_preparar_copia_so_as_primeiras_paginas_sem_mexer_no_original(tmp_path):
    import fitz

    original = _livro_de_mentira(tmp_path / "original.pdf", 5)
    antes = original.read_bytes()
    destino = tmp_path / "gabarito" / "velocidade" / "livro_3.pdf"

    feito = tv.preparar_livro(original, destino, folhas=3)

    assert feito is True
    with fitz.open(destino) as copia:
        assert copia.page_count == 3
        assert "pagina 1" in copia[0].get_text()
        assert "pagina 3" in copia[2].get_text()
    assert original.read_bytes() == antes, "o original nao pode mudar"
    assert not list(destino.parent.glob("*.parcial")), "sobrou arquivo pela metade"


def test_preparar_de_novo_nao_refaz(tmp_path):
    original = _livro_de_mentira(tmp_path / "original.pdf", 5)
    destino = tmp_path / "livro_3.pdf"
    tv.preparar_livro(original, destino, folhas=3)
    feito_em = destino.stat().st_mtime_ns

    feito = tv.preparar_livro(original, destino, folhas=3)

    assert feito is False
    assert destino.stat().st_mtime_ns == feito_em


def test_preparar_nunca_grava_dentro_do_acervo(tmp_path):
    original = _livro_de_mentira(tmp_path / "original.pdf", 2)
    no_acervo = tmp_path / "EditorImpressao-arquivos" / "LIVROS PARA TESTE" / "x.pdf"

    with pytest.raises(tv.ErroNaMedicao):
        tv.preparar_livro(original, no_acervo, folhas=1)
    assert not no_acervo.exists()


# ---------------------------------------------------------------------------
# a maquina e a memoria
# ---------------------------------------------------------------------------


def test_dados_da_maquina_trazem_o_que_o_relatorio_mostra():
    dados = tv.dados_da_maquina()

    for chave in ("computador", "processador", "nucleos_fisicos", "nucleos_logicos",
                  "memoria_instalada_gb", "memoria_utilizavel_gb", "placas_de_video",
                  "windows", "energia"):
        assert chave in dados, chave
    assert dados["nucleos_logicos"] >= 1
    assert dados["processador"]
    assert isinstance(dados["placas_de_video"], list)


def test_tipo_do_disco_responde_sem_quebrar():
    """Depende da maquina (SSD, HD, USB...); o que se exige e nao quebrar e
    dizer algo legivel ou None."""
    tipo = tv.tipo_do_disco(Path(tv.__file__))

    assert tipo is None or tipo.startswith(("SSD", "HD", "disco"))


def _windows_de_mentira(pasta: Path, com_powershell: bool = True) -> Path:
    """Uma pasta com a cara de C:\\Windows, com (ou sem) o powershell.exe no
    lugar de sempre. O arquivo e vazio: os testes que usam isto nao rodam."""
    if com_powershell:
        exe = pasta / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b"")
    else:
        pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _anotar_chamadas(monkeypatch, saida: bytes = b"SSD|NVMe\r\n") -> list:
    """Troca o subprocess.run por um que so anota o comando e responde
    `saida`, como o PowerShell responderia."""
    chamadas: list = []

    def rodar(comando, **_kwargs):
        chamadas.append(comando)
        return subprocess.CompletedProcess(comando, 0, stdout=saida, stderr=b"")

    monkeypatch.setattr(tv.subprocess, "run", rodar)
    return chamadas


def test_powershell_pelo_caminho_completo_e_nao_pelo_path(tmp_path, monkeypatch):
    """Com o PATH mexido, "powershell" pelo nome nao e achado, o teste nao
    diz nada e a linha "Disco do livro" some - e e ela que mostraria um teste
    rodado direto do pendrive."""
    windows = _windows_de_mentira(tmp_path / "Windows")
    monkeypatch.setenv("SystemRoot", str(windows))
    monkeypatch.setenv("PATH", "")
    chamadas = _anotar_chamadas(monkeypatch)

    assert tv._powershell("Get-PhysicalDisk") == ["SSD|NVMe"]
    assert chamadas[0][0] == str(windows / "System32" / "WindowsPowerShell" / "v1.0"
                                 / "powershell.exe")


def test_powershell_pelo_path_so_quando_o_caminho_completo_nao_existe(tmp_path, monkeypatch):
    monkeypatch.setenv("SystemRoot", str(_windows_de_mentira(tmp_path / "Windows",
                                                             com_powershell=False)))
    chamadas = _anotar_chamadas(monkeypatch)

    assert tv._powershell("Get-PhysicalDisk") == ["SSD|NVMe"]
    assert chamadas[0][0] == "powershell"


def test_sem_systemroot_procura_o_powershell_no_windir(tmp_path, monkeypatch):
    windows = _windows_de_mentira(tmp_path / "Windows")
    monkeypatch.delenv("SystemRoot", raising=False)
    monkeypatch.setenv("windir", str(windows))

    assert tv._caminho_do_powershell() == str(
        windows / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe")


def test_disco_do_livro_nao_some_com_o_path_vazio(monkeypatch):
    """De verdade, neste Windows: sem PATH nenhum, o PowerShell ainda
    responde. Antes da correcao, isto devolvia lista vazia."""
    if not Path(tv._caminho_do_powershell()).is_absolute():
        pytest.skip("este Windows nao tem o PowerShell no lugar de sempre")
    monkeypatch.setenv("PATH", "")

    assert tv._powershell("Write-Output 'o PowerShell respondeu'") == [
        "o PowerShell respondeu"]


def test_pico_de_memoria_pelo_windows_bate_com_o_psutil():
    """O plano B (ctypes) ja devolveu 0 calado numa versao antiga, com o
    handle truncado em 64 bits. Tem de dar o mesmo numero que o psutil."""
    psutil = pytest.importorskip("psutil")

    pelo_windows = tv._pico_pelo_windows()
    pelo_psutil = psutil.Process().memory_info().peak_wset / 1024 / 1024

    assert pelo_windows is not None and pelo_windows > 10
    assert abs(pelo_windows - pelo_psutil) < max(5.0, 0.1 * pelo_psutil)


# ---------------------------------------------------------------------------
# o notebook nao pode dormir no meio da medicao (item 0.6)
# ---------------------------------------------------------------------------

# Valores da documentacao da Microsoft (SetThreadExecutionState).
_CONTINUO, _SISTEMA, _TELA = 0x80000000, 0x00000001, 0x00000002


def test_computador_fica_acordado_durante_a_medicao_e_libera_no_fim():
    """Processador trabalhando nao conta como uso para o Windows: sem o
    pedido, o notebook dormiria no meio de uma medicao sem ninguem mexer."""
    pedidos = []

    def pedir(estado):
        pedidos.append(estado)
        return True

    with tv.computador_acordado(pedir) as ligado:
        assert ligado is True
        assert pedidos == [_CONTINUO | _SISTEMA | _TELA]
    assert pedidos == [_CONTINUO | _SISTEMA | _TELA, _CONTINUO]


def test_computador_acordado_libera_mesmo_se_a_medicao_parar_no_meio():
    pedidos = []

    with pytest.raises(RuntimeError):
        with tv.computador_acordado(lambda estado: pedidos.append(estado) or True):
            raise RuntimeError("a medicao parou")

    assert pedidos[-1] == _CONTINUO


def test_sem_o_pedido_ao_windows_a_medicao_segue():
    pedidos = []

    def recusar(estado):
        pedidos.append(estado)
        return False

    with tv.computador_acordado(recusar) as ligado:
        assert ligado is False
    assert pedidos == [_CONTINUO | _SISTEMA | _TELA], "nada a liberar se nao ligou"


def test_pedido_de_verdade_ao_windows_nao_quebra():
    with tv.computador_acordado() as ligado:
        assert ligado in (True, False)


def test_a_medicao_inteira_roda_com_o_computador_acordado(tmp_path, monkeypatch):
    """O pedido tem de cobrir rodar_medicao, e ser desfeito depois."""
    import contextlib

    livro = _pdf_falso(tmp_path / "livro.pdf")
    estado = {"acordado": False, "mediu_acordado": None}

    @contextlib.contextmanager
    def acordado(pedir=None):
        estado["acordado"] = True
        try:
            yield True
        finally:
            estado["acordado"] = False

    def medir(*_args, **_kwargs):
        estado["mediu_acordado"] = estado["acordado"]
        return _resultado(rapido=True, rodadas=1)

    monkeypatch.setattr(tv, "computador_acordado", acordado)
    monkeypatch.setattr(tv, "rodar_medicao", medir)
    monkeypatch.setattr(tv, "dados_da_maquina", lambda: _resultado()["maquina"])

    codigo = tv.main([str(livro), "--rapido", "--saida", str(tmp_path / "saida")])

    assert codigo == 0
    assert estado["mediu_acordado"] is True
    assert estado["acordado"] is False


# ---------------------------------------------------------------------------
# um clique dentro da janela preta nao pode pausar a medicao (item 0.6)
# ---------------------------------------------------------------------------

# Valores da documentacao da Microsoft (SetConsoleMode).
_EDICAO_RAPIDA, _BITS_ESTENDIDOS, _INSERCAO = 0x0040, 0x0080, 0x0020
# O modo de uma janela preta classica nova: 0x1F7, com a edicao rapida ligada.
_MODO_DE_FABRICA = 0x01F7


class _JanelaPreta:
    """Uma janela preta de mentira, no lugar do Windows: guarda o modo como
    GetConsoleMode/SetConsoleMode guardariam e anota cada mudanca pedida.

    `modo` None = sem janela preta. `aceita` False = o Windows recusa a
    mudanca. `teimosa` = responde que recusou mas muda assim mesmo (a janela
    classica faz isso com certos modos). `erro` = toda chamada levanta."""

    def __init__(self, modo=_MODO_DE_FABRICA, aceita=True, teimosa=False, erro=None):
        self.modo = modo
        self.aceita = aceita
        self.teimosa = teimosa
        self.erro = erro
        self.mudancas: list[int] = []

    def ler(self):
        if self.erro is not None:
            raise self.erro
        return self.modo

    def mudar(self, modo):
        self.mudancas.append(modo)
        if self.erro is not None:
            raise self.erro
        if self.aceita or self.teimosa:
            self.modo = modo
        return self.aceita


def test_clique_na_janela_nao_pausa_a_medicao_e_o_modo_volta_no_fim():
    janela = _JanelaPreta()

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "desligado"
        assert not janela.modo & _EDICAO_RAPIDA
        assert janela.modo & _BITS_ESTENDIDOS, "sem este bit o Windows ignora o pedido"
        assert janela.modo == (_MODO_DE_FABRICA & ~_EDICAO_RAPIDA) | _BITS_ESTENDIDOS, (
            "so a edicao rapida muda; o resto (Ctrl+C, insercao...) fica como estava")

    assert janela.modo == _MODO_DE_FABRICA
    assert janela.mudancas[-1] == _MODO_DE_FABRICA


@pytest.mark.parametrize("interrupcao", [RuntimeError("a medicao parou"), KeyboardInterrupt()])
def test_modo_volta_mesmo_se_a_medicao_parar_no_meio(interrupcao):
    janela = _JanelaPreta()

    with pytest.raises(type(interrupcao)):
        with tv.edicao_rapida_desligada(janela.ler, janela.mudar):
            raise interrupcao

    assert janela.modo == _MODO_DE_FABRICA


def test_sem_janela_preta_nao_mexe_em_nada():
    """Teste chamado por outro programa, ou com a entrada vinda de arquivo."""
    janela = _JanelaPreta(modo=None)

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "sem_janela"

    assert janela.mudancas == []


def test_edicao_rapida_ja_desligada_fica_como_esta():
    janela = _JanelaPreta(modo=_MODO_DE_FABRICA & ~_EDICAO_RAPIDA)

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "ja_desligado"

    assert janela.mudancas == []


def test_windows_que_recusa_a_mudanca_nao_para_a_medicao():
    janela = _JanelaPreta(aceita=False)

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "falhou"

    assert janela.modo == _MODO_DE_FABRICA


def test_windows_que_diz_que_recusou_mas_mudou_conta_como_desligado():
    """A janela classica responde "falhou" a certos modos e aplica assim
    mesmo: vale o que ela diz DEPOIS da mudanca, e o modo volta no fim."""
    janela = _JanelaPreta(aceita=False, teimosa=True)

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "desligado"

    assert janela.modo == _MODO_DE_FABRICA


def test_chamada_ao_windows_que_quebra_nao_para_a_medicao():
    janela = _JanelaPreta(erro=OSError("sem console"))

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "sem_janela"


def test_mudar_que_quebra_no_meio_nao_para_a_medicao():
    """Ler funciona, mudar levanta: a medicao segue, e no fim nada levanta."""
    janela = _JanelaPreta()

    def mudar(_modo):
        raise OSError("o Windows caiu no meio")

    with tv.edicao_rapida_desligada(janela.ler, mudar) as situacao:
        assert situacao == "falhou"


def test_modo_lido_sem_os_bits_estendidos_ainda_desliga():
    """Se outro programa mudou o modo sem o bit estendido, o Windows nao diz
    como a edicao rapida esta: desliga mesmo assim, e o modo lido volta no
    fim."""
    janela = _JanelaPreta(modo=0x0007)

    with tv.edicao_rapida_desligada(janela.ler, janela.mudar) as situacao:
        assert situacao == "desligado"
        assert janela.modo & _BITS_ESTENDIDOS and not janela.modo & _EDICAO_RAPIDA

    assert janela.modo == 0x0007


def test_chamada_de_verdade_a_janela_preta_nao_quebra():
    """Aqui (pytest) a entrada nao e o teclado de uma janela preta; de
    qualquer jeito, nada pode levantar."""
    with tv.edicao_rapida_desligada() as situacao:
        assert situacao in tv.SITUACOES_DA_EDICAO_RAPIDA


# ---------------------------------------------------------------------------
# em que janela o teste rodou: a classica, o Terminal novo ou nenhuma (item 0.6)
# ---------------------------------------------------------------------------

# Um identificador de janela qualquer (o Windows da numeros assim).
_JANELA = 0x2A0F1C


def _windows_que_responde(janela, classe):
    """GetConsoleWindow e GetClassNameW de mentira, no lugar do Windows:
    devolvem `janela` e `classe` (ou levantam, se forem uma excecao) e anotam
    de que janela a classe foi pedida. Devolve (pegar_janela, pegar_classe,
    as janelas pedidas)."""
    pedidas: list = []

    def pegar_janela():
        if isinstance(janela, BaseException):
            raise janela
        return janela

    def pegar_classe(identificador):
        pedidas.append(identificador)
        if isinstance(classe, BaseException):
            raise classe
        return classe

    return pegar_janela, pegar_classe, pedidas


@pytest.mark.parametrize("classe, situacao", [
    ("ConsoleWindowClass", "classica"),
    ("PseudoConsoleWindow", "terminal_novo"),
])
def test_janela_pela_classe_que_o_windows_diz(classe, situacao):
    """ConsoleWindowClass e a janela preta classica (o conhost);
    PseudoConsoleWindow e a janela escondida do pseudoconsole, que o Terminal
    novo usa."""
    pegar_janela, pegar_classe, pedidas = _windows_que_responde(_JANELA, classe)

    janela = tv.janela_do_teste(pegar_janela, pegar_classe)

    assert janela == {"situacao": situacao, "classe": classe}
    assert pedidas == [_JANELA], "a classe e a da janela do console, e nao de outra"


@pytest.mark.parametrize("sem_janela", [0, None])
def test_sem_console_e_sem_janela(sem_janela):
    """GetConsoleWindow devolve 0 (None pelo ctypes) quando o processo nao
    tem console: nem se pergunta a classe."""
    pegar_janela, pegar_classe, pedidas = _windows_que_responde(sem_janela, "nunca pedida")

    assert tv.janela_do_teste(pegar_janela, pegar_classe) == {"situacao": "sem_janela",
                                                              "classe": None}
    assert pedidas == []


def test_janela_de_outra_classe_fica_anotada():
    """Outro programa que mostra a janela preta (nenhum dos dois conhecidos):
    nao da para dizer qual, mas a classe vai para o .json, para quem investigar."""
    pegar_janela, pegar_classe, _ = _windows_que_responde(_JANELA, "OutraJanelaQualquer")

    assert tv.janela_do_teste(pegar_janela, pegar_classe) == {
        "situacao": "desconhecida", "classe": "OutraJanelaQualquer"}


@pytest.mark.parametrize("janela, classe", [
    (OSError("sem kernel32"), "ConsoleWindowClass"),
    (_JANELA, OSError("a janela fechou no meio")),
    (_JANELA, ""),
    (_JANELA, None),
    (_JANELA, ["nao", "e", "texto"]),
])
def test_windows_que_falha_nao_derruba_o_teste(janela, classe):
    pegar_janela, pegar_classe, _ = _windows_que_responde(janela, classe)

    assert tv.janela_do_teste(pegar_janela, pegar_classe) == {"situacao": "desconhecida",
                                                              "classe": None}


def test_chamada_de_verdade_a_janela_nao_quebra():
    """Aqui (pytest) pode haver ou nao uma janela de console; de qualquer
    jeito, nada pode levantar, e a resposta e uma das conhecidas."""
    janela = tv.janela_do_teste()

    assert janela["situacao"] in tv.SITUACOES_DA_JANELA
    assert janela["classe"] is None or isinstance(janela["classe"], str)


@pytest.mark.skipif(sys.platform != "win32", reason="so no Windows")
def test_le_a_classe_de_uma_janela_de_verdade():
    """GetClassNameW de verdade, na janela da area de trabalho: ela sempre
    existe, e o Windows fixou a classe dela em "#32769". Prova que a leitura
    da classe funciona (se devolvesse vazio, toda janela seria desconhecida)."""
    import ctypes

    user32 = ctypes.WinDLL("user32")
    user32.GetDesktopWindow.restype = ctypes.c_void_p

    assert tv._classe_da_janela(user32.GetDesktopWindow()) == "#32769"


def _preparar_main_sem_medir(tmp_path, monkeypatch, eventos: list, problema=None):
    """main/executar sem medir nada: a edicao rapida, o computador acordado,
    a medicao e a despedida trocados por versoes que so anotam em `eventos`.
    Devolve os argumentos para executar()."""
    livro = _pdf_falso(tmp_path / "livro.pdf")

    @contextlib.contextmanager
    def desligada(*_args, **_kwargs):
        eventos.append("desligou")
        try:
            yield "desligado"
        finally:
            eventos.append("devolveu")

    @contextlib.contextmanager
    def acordado(*_args, **_kwargs):
        yield True

    def medir(*_args, edicao_rapida=None, janela=None, **_kwargs):
        eventos.append("mediu")
        if problema is not None:
            raise problema
        return _resultado(rapido=True, rodadas=1, edicao_rapida=edicao_rapida, janela=janela)

    monkeypatch.setattr(tv, "edicao_rapida_desligada", desligada)
    monkeypatch.setattr(tv, "computador_acordado", acordado)
    monkeypatch.setattr(tv, "rodar_medicao", medir)
    monkeypatch.setattr(tv, "dados_da_maquina", lambda: _resultado()["maquina"])
    monkeypatch.setattr(tv, "despedir", lambda codigo, **_: eventos.append("despediu"))
    return [str(livro), "--rapido", "--saida", str(tmp_path / "saida")]


def test_a_medicao_inteira_roda_com_a_edicao_rapida_desligada(tmp_path, monkeypatch):
    """O modo cobre rodar_medicao, volta ANTES da despedida ("Aperte Enter
    para fechar") e o que aconteceu vai para o .json e para o relatorio."""
    eventos: list = []
    argumentos = _preparar_main_sem_medir(tmp_path, monkeypatch, eventos)

    assert tv.executar(argumentos) == 0

    assert eventos == ["desligou", "mediu", "devolveu", "despediu"]
    gravados = list((tmp_path / "saida").glob("*.json"))
    assert len(gravados) == 1
    assert json.loads(gravados[0].read_text(encoding="utf-8"))["edicao_rapida"] == "desligado"
    relatorio = gravados[0].with_suffix(".md").read_text(encoding="utf-8")
    assert "ficou desligado durante a medição" in relatorio


def test_a_medicao_diz_em_que_janela_rodou(tmp_path, monkeypatch):
    """main pergunta a janela uma vez e ela chega ao .json e ao relatorio."""
    eventos: list = []
    argumentos = _preparar_main_sem_medir(tmp_path, monkeypatch, eventos)
    classica = {"situacao": "classica", "classe": "ConsoleWindowClass"}
    monkeypatch.setattr(tv, "janela_do_teste", lambda *_a, **_k: dict(classica))

    assert tv.executar(argumentos) == 0

    gravados = list((tmp_path / "saida").glob("*.json"))
    assert len(gravados) == 1
    assert json.loads(gravados[0].read_text(encoding="utf-8"))["janela"] == classica
    relatorio = gravados[0].with_suffix(".md").read_text(encoding="utf-8")
    assert "rodou na janela clássica do Windows" in relatorio


@pytest.mark.parametrize("problema, codigo", [
    (tv.ErroNaMedicao("a prévia não chegou"), 1),
    (RuntimeError("problema inesperado de teste"), 1),
    (KeyboardInterrupt(), 130),
])
def test_modo_volta_antes_da_despedida_mesmo_se_a_medicao_parar(tmp_path, monkeypatch,
                                                                problema, codigo):
    eventos: list = []
    argumentos = _preparar_main_sem_medir(tmp_path, monkeypatch, eventos, problema)

    assert tv.executar(argumentos) == codigo

    assert eventos == ["desligou", "mediu", "devolveu", "despediu"]


# ---------------------------------------------------------------------------
# empacotado: a janela preta nao pode fechar sozinha (item 0.6)
# ---------------------------------------------------------------------------


def _esvaziar_de_mentira() -> bool:
    """No lugar de esvaziar o teclado de verdade (esvaziar_o_teclado): o
    pytest pode estar rodando na janela preta de alguem, e as teclas dela
    nao sao do teste."""
    return True


class _Teclado:
    """Uma entrada de terminal de mentira: diz que e terminal e conta quantas
    vezes o programa esperou o Enter."""

    def __init__(self, terminal=True, erro=None):
        self.terminal = terminal
        self.erro = erro
        self.esperas = 0

    def isatty(self):
        return self.terminal

    def readline(self):
        self.esperas += 1
        if self.erro is not None:
            raise self.erro
        return "\n"


def test_fim_com_dois_cliques_no_exe_espera_o_enter():
    """Sozinho na janela (dois cliques no .exe), ela fecha junto com o
    programa: a ultima frase tem de ficar ate a pessoa apertar Enter."""
    import io

    tela, teclado = io.StringIO(), _Teclado()

    esperou = tv.despedir(0, congelado=True, sozinho=True, entrada=teclado, saida=tela,
                          esvaziar=_esvaziar_de_mentira)

    assert esperou is True
    assert teclado.esperas == 1
    assert ("Terminou. O resultado está na pasta resultados. Aperte Enter para fechar."
            in tela.getvalue())


def test_fim_pelo_bat_nao_espera_duas_vezes():
    """Aberto pelo RODAR O TESTE.bat, o .bat ja segura a janela (pause)."""
    import io

    tela, teclado = io.StringIO(), _Teclado()

    esperou = tv.despedir(0, congelado=True, sozinho=False, entrada=teclado, saida=tela,
                          esvaziar=_esvaziar_de_mentira)

    assert esperou is False
    assert teclado.esperas == 0
    assert "Terminou. O resultado está na pasta resultados." in tela.getvalue()
    assert "Enter" not in tela.getvalue()


def test_fim_rodando_pelo_python_nao_diz_nem_espera_nada():
    import io

    tela, teclado = io.StringIO(), _Teclado()

    assert tv.despedir(0, congelado=False, sozinho=True, entrada=teclado, saida=tela) is False
    assert tela.getvalue() == ""
    assert teclado.esperas == 0


def test_fim_sem_ninguem_no_teclado_nao_trava():
    """Entrada que nao e terminal (execucao automatica, entrada mandada de
    um arquivo): esperar o Enter prenderia o programa para sempre."""
    import io

    tela, teclado = io.StringIO(), _Teclado(terminal=False)

    assert tv.despedir(0, congelado=True, sozinho=True, entrada=teclado, saida=tela,
                       esvaziar=_esvaziar_de_mentira) is False
    assert teclado.esperas == 0


def test_fim_sem_janela_nenhuma_nao_quebra(monkeypatch):
    """Empacotado sem console, sys.stdin e sys.stdout sao None."""
    monkeypatch.setattr(tv.sys, "stdin", None)
    monkeypatch.setattr(tv.sys, "stdout", None)

    assert tv.despedir(0, congelado=True, sozinho=True) is False


def test_fim_com_entrada_quebrada_nao_quebra():
    import io

    class Quebrada:
        def isatty(self):
            raise ValueError("I/O operation on closed file")

    assert tv.despedir(0, congelado=True, sozinho=True, entrada=Quebrada(),
                       saida=io.StringIO(), esvaziar=_esvaziar_de_mentira) is False


def test_fechar_a_janela_com_ctrl_c_na_espera_nao_mostra_erro():
    import io

    teclado = _Teclado(erro=KeyboardInterrupt())

    assert tv.despedir(0, congelado=True, sozinho=True, entrada=teclado,
                       saida=io.StringIO(), esvaziar=_esvaziar_de_mentira) is True


# ---------------------------------------------------------------------------
# um Enter apertado durante a medicao nao fecha a janela no fim (item 0.6)
# ---------------------------------------------------------------------------


def test_fim_joga_fora_as_teclas_guardadas_antes_da_ultima_frase():
    """Um Enter apertado durante a medicao fica guardado na janela e
    responderia na hora ao "Aperte Enter para fechar": a janela fecharia sem
    dar tempo de ler o fim. As teclas guardadas vao fora ANTES da ultima
    frase e da espera."""
    import io

    eventos: list = []

    class Tela(io.StringIO):
        def write(self, texto):
            eventos.append("escreveu")
            return super().write(texto)

    class Teclado(_Teclado):
        def readline(self):
            eventos.append("esperou o Enter")
            return super().readline()

    def esvaziar():
        eventos.append("esvaziou")
        return True

    assert tv.despedir(0, congelado=True, sozinho=True, entrada=Teclado(), saida=Tela(),
                       esvaziar=esvaziar) is True

    assert eventos[0] == "esvaziou"
    assert eventos.count("esvaziou") == 1
    assert eventos[-1] == "esperou o Enter"


def test_fim_pelo_bat_tambem_joga_fora_as_teclas_guardadas():
    """Pelo .bat o teste nao espera o Enter (quem segura a janela e o pause
    do .bat, que ja descarta sozinho o que foi digitado antes dele), mas
    esvaziar nao custa nada e vale do mesmo jeito."""
    import io

    esvaziadas: list = []

    tv.despedir(0, congelado=True, sozinho=False, entrada=_Teclado(), saida=io.StringIO(),
                esvaziar=lambda: esvaziadas.append(1) or True)

    assert esvaziadas == [1]


def test_rodando_pelo_python_nao_mexe_no_teclado():
    """Pelo Python, num terminal de alguem, as teclas guardadas podem ser o
    proximo comando que a pessoa ja digitou: nada vai fora."""
    import io

    esvaziadas: list = []

    tv.despedir(0, congelado=False, sozinho=True, entrada=_Teclado(), saida=io.StringIO(),
                esvaziar=lambda: esvaziadas.append(1) or True)

    assert esvaziadas == []


@pytest.mark.parametrize("problema", [OSError("sem console"), RuntimeError("inesperado")])
def test_esvaziar_que_quebra_nao_impede_a_despedida(problema):
    import io

    def quebrar():
        raise problema

    tela, teclado = io.StringIO(), _Teclado()

    assert tv.despedir(0, congelado=True, sozinho=True, entrada=teclado, saida=tela,
                       esvaziar=quebrar) is True
    assert "Terminou" in tela.getvalue()
    assert teclado.esperas == 1


class _Kernel32DeMentira:
    """O kernel32 de mentira, no lugar do Windows: anota em que entrada
    FlushConsoleInputBuffer foi pedido e responde `resposta` (1 = esvaziou,
    0 = o Windows recusou)."""

    def __init__(self, resposta=1):
        self.pedidos: list = []

        def esvaziar(entrada):
            self.pedidos.append(entrada)
            return resposta

        self.FlushConsoleInputBuffer = esvaziar


# Um identificador de entrada qualquer (o Windows da numeros assim).
_ENTRADA_DA_JANELA = 0x54


def test_esvazia_a_entrada_da_janela_preta(monkeypatch):
    """A entrada esvaziada e a da janela preta (a mesma de GetConsoleMode,
    ver _entrada_da_janela_preta), e nao outra."""
    kernel32 = _Kernel32DeMentira()
    monkeypatch.setattr(tv, "_entrada_da_janela_preta", lambda: (kernel32, _ENTRADA_DA_JANELA))

    assert tv.esvaziar_o_teclado() is True
    assert kernel32.pedidos == [_ENTRADA_DA_JANELA]


def test_windows_que_nao_esvazia_nao_derruba_nada(monkeypatch):
    kernel32 = _Kernel32DeMentira(resposta=0)
    monkeypatch.setattr(tv, "_entrada_da_janela_preta", lambda: (kernel32, _ENTRADA_DA_JANELA))

    assert tv.esvaziar_o_teclado() is False


def test_sem_janela_preta_esvaziar_nao_derruba_nada(monkeypatch):
    def sem_console():
        raise OSError("sem console")

    monkeypatch.setattr(tv, "_entrada_da_janela_preta", sem_console)

    assert tv.esvaziar_o_teclado() is False


# O que o processo de dentro roda, num console SEM janela: guarda um Enter na
# entrada da janela, chama esvaziar_o_teclado e conta o que sobrou.
_GUARDAR_E_ESVAZIAR = r"""
import ctypes, json, sys
from ctypes import wintypes
sys.path.insert(0, sys.argv[2])
import teste_velocidade as tv

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
kernel32.GetStdHandle.restype = wintypes.HANDLE
kernel32.GetNumberOfConsoleInputEvents.argtypes = [wintypes.HANDLE,
                                                   ctypes.POINTER(wintypes.DWORD)]

class Tecla(ctypes.Structure):
    _fields_ = [("bKeyDown", wintypes.BOOL), ("wRepeatCount", wintypes.WORD),
                ("wVirtualKeyCode", wintypes.WORD), ("wVirtualScanCode", wintypes.WORD),
                ("UnicodeChar", wintypes.WCHAR), ("dwControlKeyState", wintypes.DWORD)]

class Evento(ctypes.Structure):
    class _Qual(ctypes.Union):
        _fields_ = [("KeyEvent", Tecla), ("_folga", ctypes.c_byte * 16)]
    _fields_ = [("EventType", wintypes.WORD), ("Event", _Qual)]

kernel32.WriteConsoleInputW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Evento),
                                        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
entrada = kernel32.GetStdHandle(-10 & 0xFFFFFFFF)

def pendentes():
    quantos = wintypes.DWORD(0)
    kernel32.GetNumberOfConsoleInputEvents(entrada, ctypes.byref(quantos))
    return quantos.value

eventos = (Evento * 2)()
for i, apertada in enumerate((True, False)):
    eventos[i].EventType = 1
    eventos[i].Event.KeyEvent = Tecla(apertada, 1, 0x0D, 0x1C, "\r", 0)
escritos = wintypes.DWORD(0)
kernel32.WriteConsoleInputW(entrada, eventos, 2, ctypes.byref(escritos))
antes = pendentes()
esvaziou = tv.esvaziar_o_teclado()
with open(sys.argv[1], "w", encoding="utf-8") as arquivo:
    json.dump({"escritos": escritos.value, "antes": antes, "esvaziou": esvaziou,
               "depois": pendentes()}, arquivo)
"""


@pytest.mark.skipif(sys.platform != "win32", reason="so no Windows")
def test_enter_guardado_some_de_verdade(tmp_path):
    """Com o Windows de verdade, num console SEM janela (CREATE_NO_WINDOW):
    nenhuma janela aparece, e nenhuma tecla de quem usa o computador chega
    nele. Um Enter guardado ali some com esvaziar_o_teclado."""
    resultado = tmp_path / "sobrou.json"
    raiz = str(Path(tv.__file__).resolve().parent)

    subprocess.run([sys.executable, "-c", _GUARDAR_E_ESVAZIAR, str(resultado), raiz],
                   timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)

    sobrou = json.loads(resultado.read_text(encoding="utf-8"))
    assert sobrou["escritos"] == 2 and sobrou["antes"] == 2, "o Enter ficou guardado"
    assert sobrou["esvaziou"] is True
    assert sobrou["depois"] == 0


@pytest.mark.parametrize("codigo, pedaco", [
    (0, "Terminou. O resultado está na pasta resultados."),
    (1, "parou"),
    (2, "livro"),
    (130, "interrompido"),
])
def test_a_ultima_frase_diz_como_o_teste_terminou(codigo, pedaco):
    assert pedaco in tv.mensagem_do_fim(codigo)


def test_so_a_frase_de_sucesso_fala_em_resultado_pronto():
    for codigo in (1, 2, 130):
        assert "Terminou" not in tv.mensagem_do_fim(codigo)


def test_contar_os_programas_da_janela_nao_quebra():
    assert tv._sozinho_no_console() in (True, False)


def test_executar_despede_com_o_codigo_da_medicao(monkeypatch):
    codigos = []
    monkeypatch.setattr(tv, "main", lambda argv=None: 0)
    monkeypatch.setattr(tv, "despedir", lambda codigo, **_: codigos.append(codigo))

    assert tv.executar([]) == 0
    assert codigos == [0]


def test_executar_segura_a_janela_ate_num_erro_inesperado(monkeypatch, capsys):
    """Um erro fora da medicao nao pode fechar a janela sem dizer nada."""
    codigos = []

    def quebrar(argv=None):
        raise RuntimeError("erro inesperado de teste")

    monkeypatch.setattr(tv, "main", quebrar)
    monkeypatch.setattr(tv, "despedir", lambda codigo, **_: codigos.append(codigo))

    assert tv.executar([]) == 1
    assert codigos == [1]
    assert "erro inesperado de teste" in capsys.readouterr().err


@pytest.mark.parametrize("opcoes, codigo", [(["--opcao-que-nao-existe"], 2), (["--help"], 0)])
def test_opcao_digitada_errada_ou_ajuda_saem_sem_despedida(monkeypatch, opcoes, codigo):
    """So se chega aqui digitando opcoes (terminal ou .bat, que nao fecham
    sozinhos), e nenhuma frase do fim serve: "Terminou. O resultado esta na
    pasta resultados" depois do --help seria mentira."""
    codigos = []
    monkeypatch.setattr(tv, "despedir", lambda codigo, **_: codigos.append(codigo))

    assert tv.executar(opcoes) == codigo
    assert codigos == []


def test_ctrl_c_fora_da_medicao_despede_como_interrompido(monkeypatch):
    codigos = []

    def interromper(argv=None):
        raise KeyboardInterrupt

    monkeypatch.setattr(tv, "main", interromper)
    monkeypatch.setattr(tv, "despedir", lambda codigo, **_: codigos.append(codigo))

    assert tv.executar([]) == 130
    assert codigos == [130]
