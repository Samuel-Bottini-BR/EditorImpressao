"""As provas de comportamento das decisões do Samuel (Livro de decisões,
docs/plano/DECISOES.md; CLAUDE.md §11, regra 4: "Cada decisão tem uma prova de
comportamento em tests/test_decisoes.py").

Cada teste diz a decisão e as palavras dele. Aparência não conta: aqui tudo é
medido no PDF que o programa gera (core.pipeline.processar, o mesmo do botão
"Confirmar e processar") ou no projeto gravado.

Obra de 26/10/2026, etapa 1 (implementador):
  - D-009 (26/10/2026): "eu deveria conseguir abrir o livro sem escolher
    nenhuma opção para fazer tudo manualmente." -> o feito à mão (corte,
    ângulo, filtro da página, marcação à mão, mover) aparece no PDF com a
    etapa do automático DESLIGADA. E o comportamento antigo saiu: antes o
    valor à mão era jogado fora (provado contra o projeto antigo, que continua
    saindo como antes - escolha documentada em core/etapas.py).
  - D-004 (28/09/2026): "Automático em livro já mexido à mão: o programa
    pergunta se quer pular as páginas mexidas." -> a marca "mexida à mão" por
    página/folha e por etapa existe, é gravada no projeto e nasce dos valores
    à mão (a pergunta é da etapa 3).
  - D-008 (22/09 e 26/10/2026): "quero conseguir redimensionar o conteudo
    tambem" / "a ferramenta de mover não deveria estar vinculada ao corte de
    bordas" -> mover e aumentar o conteúdo sem escolher tamanho de folha chega
    ao PDF, no lugar e no tamanho novos; e o caso do teste do Kaique (folha do
    tamanho do corte, arredondada) não joga mais o mover fora.
  - D-016 (escolha da gerente, D-014): a montagem segue a ordem obrigatória
    (endireita, depois corta uma vez só) também com o feito à mão.

Páginas sintéticas de propósito: a regra de 21/10 (caminho inteiro, só
páginas que vão ser impressas) vale para conferência de IMAGEM; aqui a medida
é de lugar e de tamanho (onde o bloco preto foi parar), e cada teste passa
pelo caminho inteiro do processar.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

from core import etapas
from core.filtros import ORIGINAL, PRETO_E_BRANCO
from core.pipeline import processar
from core.selecao import MAO, RETANGULO, Regiao, Selecao
from modelos import ConfigFolha, ConfigPagina, Projeto

DPI = 150
LARGURA_PX, ALTURA_PX = 600, 840      # 10,16 x 14,22 cm a 150 DPI
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- ajudantes ----------------------------------------------------------------

def _pagina_de_teste() -> np.ndarray:
    """Papel amarelado com um bloco preto fora do meio (um "texto deslocado")
    e uma linha preta deitada (para ver o giro)."""
    img = np.full((ALTURA_PX, LARGURA_PX, 3), AMARELADO, np.uint8)
    img[300:500, 80:280] = 0                 # bloco: esquerda do meio
    img[650:660, 100:500] = 0                # linha deitada
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


def _projeto_tudo_desligado(tmp_path, nome="saida", img=None) -> Projeto:
    """D-009: o livro aberto SEM nenhuma opção do automático."""
    entrada = tmp_path / "entrada.pdf"
    if not entrada.exists():
        _pdf(entrada, _pagina_de_teste() if img is None else img)
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(tmp_path / f"{nome}.pdf"),
                      nome="teste")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = False
    projeto.limpar = False
    projeto.detectar_regioes = False
    projeto.montar_cadernos = False
    projeto.filtro_padrao = ORIGINAL
    projeto.qualidade_dpi = DPI
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)]
    return projeto


def _gerar(projeto: Projeto) -> np.ndarray:
    """Processa e devolve a primeira página do PDF gerado, desenhada no DPI do
    livro (BGR... na verdade RGB/cinza do MuPDF, 3 canais)."""
    caminho = processar(projeto)
    with fitz.open(caminho) as doc:
        pix = doc[0].get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        return img.copy()


def _caixa_do_preto(img: np.ndarray):
    """(x0, y0, x1, y1) do que é preto (< 60) na página."""
    cinza = img.min(axis=2)
    ys, xs = np.nonzero(cinza < 60)
    assert len(xs), "não sobrou nada preto na página"
    return xs.min(), ys.min(), xs.max(), ys.max()


def _como_projeto_antigo(projeto: Projeto) -> Projeto:
    """O mesmo projeto como se tivesse sido gravado ANTES desta etapa (sem o
    campo feito_a_mao_sempre_vale nem as marcas): ida e volta pelo
    projeto.json, apagando os campos novos do dicionário."""
    dados = projeto.para_dicionario()
    dados.pop("feito_a_mao_sempre_vale")
    for item in (*dados["paginas"], *dados["folhas"]):
        item.pop("mexida_a_mao", None)
    return Projeto.de_dicionario(dados)


# --- D-009: o feito à mão vale com o automático desligado ---------------------

def test_d009_corte_a_mao_com_cortar_as_bordas_desligado_sai_no_pdf(tmp_path):
    """D-009. Corte à mão (só a metade da direita) com "Cortar as bordas"
    desligado: o PDF sai com a metade da largura. Antes da obra o corte era
    jogado fora (a página saía inteira) - prova de que o antigo saiu."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.paginas[0].recorte = (0.5, 0.0, 0.5, 1.0)
    img = _gerar(projeto)
    assert abs(img.shape[1] - LARGURA_PX / 2) <= 2
    assert abs(img.shape[0] - ALTURA_PX) <= 2


def test_d009_angulo_a_mao_com_endireitar_desligado_sai_no_pdf(tmp_path):
    """D-009. Ângulo à mão de 10 graus com "Endireitar" desligado: a linha
    deitada sai inclinada no PDF (a altura do que é preto em volta dela cresce
    de 10 pontos para mais de 50)."""
    sem = _gerar(_projeto_tudo_desligado(tmp_path, "sem"))
    projeto = _projeto_tudo_desligado(tmp_path, "com")
    projeto.paginas[0].angulo_manual = 10.0
    com = _gerar(projeto)
    faixa = slice(600, 760)
    _x0, y0, _x1, y1 = _caixa_do_preto(sem[faixa])
    assert y1 - y0 <= 12                      # deitada, sem giro
    _x0, y0, _x1, y1 = _caixa_do_preto(com[faixa])
    assert y1 - y0 > 50                       # girada pelo ângulo à mão


def test_d009_filtro_da_pagina_com_limpar_a_folha_desligado_sai_no_pdf(tmp_path):
    """D-009. "Limpar a folha" desligado e a página posta em Preto e branco à
    mão: o papel amarelado sai branco no PDF. Antes o filtro da página era
    ignorado (o papel continuava amarelo). O filtro é o único que só conta pela
    marca que a tela grava ao escolher (core/etapas.py explica por quê); aqui
    o teste faz o que a tela vai fazer (etapa 2 da obra liga)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    etapas.marcar_mexida_a_mao(projeto.paginas[0], etapas.FILTRO)
    img = _gerar(projeto)
    papel = img[50:250, 350:550]
    assert papel.min() >= 250, "o papel devia sair branco (Preto e branco à mão)"
    sem = _gerar(_projeto_tudo_desligado(tmp_path, "sem"))
    assert np.abs(sem[50:250, 350:550].astype(int) - np.array(AMARELADO[::-1])).max() <= 6


def test_d009_filtro_do_livro_trocado_depois_nao_filtra_com_limpar_desligado(tmp_path):
    """O risco que fez o filtro contar só pela marca: as páginas em Preto e
    branco (o filtro do livro de antes), o filtro do livro trocado depois na
    tela "O que fazer" e "Limpar a folha" desligado. Ninguém escolheu filtro à
    mão: o papel continua amarelado."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    projeto.filtro_padrao = ORIGINAL
    img = _gerar(projeto)
    assert np.abs(img[50:250, 350:550].astype(int) - np.array(AMARELADO[::-1])).max() <= 6


def test_d009_marcacao_a_mao_com_a_marcacao_desligada_sai_no_pdf(tmp_path):
    """D-009. Sem "Limpar a folha" nem "Procurar gravura e letra", um pedaço
    marcado à mão com "só neste pedaço: Preto e branco" (a metade de cima):
    no PDF a metade de cima sai branca e a de baixo continua amarelada.
    Antes, o pedaço não valia com "Limpar a folha" desligado
    (core.pipeline._filtrar_a_pagina, achado do verificador de 05/10)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    pedaco = Selecao()
    pedaco.acrescentar(Regiao(tipo="papel", forma=RETANGULO,
                              pontos=[(0.0, 0.0), (1.0, 0.5)], origem=MAO,
                              filtro=PRETO_E_BRANCO))
    projeto.paginas[0].guardar_selecao(pedaco)
    img = _gerar(projeto)
    assert img[40:200, 350:550].min() >= 250            # em cima: Preto e branco
    baixo = img[700:800, 520:580].astype(int)
    assert np.abs(baixo - np.array(AMARELADO[::-1])).max() <= 6   # embaixo: como veio


def test_d008_mover_sem_tamanho_de_folha_sai_no_lugar_novo(tmp_path):
    """D-008 ("a ferramenta de mover não deveria estar vinculada ao corte de
    bordas"). Sem escolher tamanho de folha, o conteúdo movido 20% para a
    direita sai 20% para a direita no PDF, e a página continua do mesmo
    tamanho. Antes o mover sem folha escolhida era jogado fora."""
    sem = _gerar(_projeto_tudo_desligado(tmp_path, "sem"))
    projeto = _projeto_tudo_desligado(tmp_path, "com")
    projeto.paginas[0].conteudo_deslocamento = (0.2, 0.0)
    com = _gerar(projeto)
    assert com.shape == sem.shape
    x0_sem = _caixa_do_preto(sem[300:500])[0]
    x0_com = _caixa_do_preto(com[300:500])[0]
    assert abs((x0_com - x0_sem) - 0.2 * LARGURA_PX) <= 3


def test_d008_mover_para_o_meio_mede_as_margens_iguais(tmp_path):
    """D-008, o caso do teste do Kaique (26/10/2026, tarefa 5: "mover ele para
    o meio da folha"; no PDF as margens do texto ficaram 15 x 53). O bloco
    está à esquerda; movido para o meio, as duas margens dele no PDF ficam
    iguais (diferença de até 2 pontos)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    # o bloco vai de 80 a 280 (centro 180); o meio da página é 300
    projeto.paginas[0].conteudo_deslocamento = ((300 - 180) / LARGURA_PX, 0.0)
    img = _gerar(projeto)
    x0, _y0, x1, _y1 = _caixa_do_preto(img[300:500])
    esquerda, direita = x0, img.shape[1] - 1 - x1
    assert abs(esquerda - direita) <= 2, (esquerda, direita)


def test_d008_aumentar_sem_tamanho_de_folha_sai_maior(tmp_path):
    """D-008 ("quero conseguir redimensionar o conteudo tambem"). Aumentar o
    conteúdo para 120% sem folha escolhida: o bloco sai 20% maior no PDF e a
    página fica do mesmo tamanho (D-017: o que passa da beirada fica de fora;
    o aviso é da etapa 5)."""
    sem = _gerar(_projeto_tudo_desligado(tmp_path, "sem"))
    projeto = _projeto_tudo_desligado(tmp_path, "com")
    projeto.paginas[0].conteudo_escala = 1.2
    com = _gerar(projeto)
    assert com.shape == sem.shape
    x0, y0, x1, y1 = _caixa_do_preto(com[200:600])
    assert abs((x1 - x0 + 1) - 200 * 1.2) <= 3


def test_d008_folha_do_tamanho_do_corte_arredondada_nao_joga_o_mover_fora(tmp_path):
    """O defeito do teste do Kaique (26/10/2026, tarefa 5): a janela
    "tamanho..." mostra o corte arredondado a 0,01 cm, a folha sai 1 ponto
    menor que o conteúdo e compor_na_folha desistia - o mover sumia do PDF.
    Teste de reversão (CLAUDE.md §4.7): falha no código de antes (o bloco não
    anda) e passa agora."""
    projeto = _projeto_tudo_desligado(tmp_path)
    largura_cm = round((LARGURA_PX - 1) / DPI * 2.54, 2)
    altura_cm = round(ALTURA_PX / DPI * 2.54, 2)
    pagina = projeto.paginas[0]
    pagina.tamanho_folha_cm = (largura_cm, altura_cm)
    pagina.conteudo_deslocamento = (0.1, 0.0)
    img = _gerar(projeto)
    x0 = _caixa_do_preto(img[300:500])[0]
    assert x0 >= 80 + 0.1 * img.shape[1] - 4, "o mover foi jogado fora"


# --- D-016: a ordem obrigatória vale para o feito à mão -----------------------

def test_d016_feito_a_mao_com_etapa_desligada_monta_igual_a_etapa_ligada(tmp_path):
    """D-016 (endireita, depois corta uma vez só) e D-009 juntos: o mesmo
    ângulo e o mesmo corte à mão dão a MESMA página com as etapas do
    automático ligadas ou desligadas (o automático não mede nada quando a
    página tem os dois à mão), no livro novo ("endireitar_antes")."""
    desligado = _projeto_tudo_desligado(tmp_path, "desligado")
    ligado = _projeto_tudo_desligado(tmp_path, "ligado")
    ligado.endireitar = True
    ligado.cortar_bordas = True
    for projeto in (desligado, ligado):
        projeto.paginas[0].angulo_manual = 4.0
        projeto.paginas[0].recorte = (0.1, 0.2, 0.7, 0.6)
    a, b = _gerar(desligado), _gerar(ligado)
    assert a.shape == b.shape
    assert np.array_equal(a, b)


# --- o projeto antigo sai igual -----------------------------------------------

def test_projeto_antigo_com_valores_a_mao_e_etapas_desligadas_sai_igual(tmp_path):
    """Escolha da obra (etapa 1, documentada em core/etapas.py): o projeto
    gravado ANTES desta etapa, com corte, ângulo, filtro, pedaço e mover à mão
    em etapas desligadas, sai como saía - esses valores eram ignorados. Prova:
    o PDF dele é idêntico ao do mesmo livro sem nenhum valor à mão."""
    projeto = _projeto_tudo_desligado(tmp_path, "antigo")
    pagina = projeto.paginas[0]
    pagina.recorte = (0.5, 0.0, 0.5, 1.0)
    pagina.angulo_manual = 10.0
    pagina.filtro = PRETO_E_BRANCO
    pagina.conteudo_deslocamento = (0.2, 0.0)
    pedaco = Selecao()
    pedaco.acrescentar(Regiao(tipo="papel", forma=RETANGULO, pontos=[(0.0, 0.0), (1.0, 0.5)],
                              origem=MAO, filtro=PRETO_E_BRANCO))
    pagina.guardar_selecao(pedaco)
    antigo = _como_projeto_antigo(projeto)
    assert antigo.feito_a_mao_sempre_vale is False
    assert antigo.paginas[0].mexida_a_mao == []      # nada valia: nada marcado
    limpo = _projeto_tudo_desligado(tmp_path, "limpo")
    assert np.array_equal(_gerar(antigo), _gerar(limpo))


def test_projeto_antigo_mexido_de_novo_pela_tela_vale(tmp_path):
    """No projeto antigo, o que a pessoa mexer DEPOIS desta versão (a tela
    grava a marca: core.etapas.marcar_mexida_a_mao) vale com a etapa
    desligada, como no livro novo (D-009)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.paginas[0].recorte = (0.5, 0.0, 0.5, 1.0)
    antigo = _como_projeto_antigo(projeto)
    etapas.marcar_mexida_a_mao(antigo.paginas[0], etapas.CORTAR)
    img = _gerar(antigo)
    assert abs(img.shape[1] - LARGURA_PX / 2) <= 2


def test_projeto_antigo_o_que_ja_valia_continua_e_ganha_a_marca(tmp_path):
    """Migração: no projeto antigo com "Cortar as bordas" LIGADO, o corte à
    mão já valia - continua valendo e ganha a marca (D-004); se depois a
    pessoa desligar o corte, ele continua valendo (D-009)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.cortar_bordas = True
    projeto.paginas[0].recorte = (0.5, 0.0, 0.5, 1.0)
    antigo = _como_projeto_antigo(projeto)
    assert antigo.paginas[0].mexida_a_mao == [etapas.CORTAR]
    antigo.cortar_bordas = False
    img = _gerar(antigo)
    assert abs(img.shape[1] - LARGURA_PX / 2) <= 2


# --- D-004: a marca "mexida à mão" ---------------------------------------------

def test_d004_marca_mexida_a_mao_por_pagina_folha_e_etapa():
    """D-004. A marca existe por página e por folha, por etapa; a tela marca e
    desmarca (core.etapas.marcar_mexida_a_mao / desmarcar_mexida_a_mao) e a
    lista das páginas mexidas é o que a pergunta do Automático vai usar."""
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=0, dividir=False), ConfigFolha(indice=1, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0), ConfigPagina(indice=1, folha=1)]
    assert etapas.paginas_mexidas_a_mao(projeto) == []
    assert etapas.marcar_mexida_a_mao(projeto.paginas[1], etapas.ENDIREITAR) is True
    assert etapas.marcar_mexida_a_mao(projeto.paginas[1], etapas.ENDIREITAR) is False
    assert etapas.paginas_mexidas_a_mao(projeto) == [projeto.paginas[1]]
    assert etapas.paginas_mexidas_a_mao(projeto, etapas.CORTAR) == []
    etapas.marcar_mexida_a_mao(projeto.folhas[0], etapas.DIVIDIR)
    assert etapas.folhas_mexidas_a_mao(projeto) == [projeto.folhas[0]]
    assert etapas.desmarcar_mexida_a_mao(projeto.paginas[1], etapas.ENDIREITAR) is True
    assert etapas.paginas_mexidas_a_mao(projeto) == []


def test_d004_marca_nasce_dos_valores_a_mao_e_vai_para_o_projeto_gravado():
    """D-004. A marca nasce dos valores à mão que já existem (corte, ângulo,
    marcação à mão, mover, folha girada; o filtro só pela marca da tela) e vai
    e volta pelo projeto.json."""
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=0, dividir=False, rotacao=90)]
    pagina = ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO, recorte=(0, 0, 1, 1),
                          angulo_manual=1.5, conteudo_escala=1.1)
    pedaco = Selecao()
    pedaco.acrescentar(Regiao(tipo="gravura", forma=RETANGULO, pontos=[(0.1, 0.1), (0.5, 0.5)],
                              origem=MAO))
    pagina.guardar_selecao(pedaco)
    projeto.paginas = [pagina]
    assert etapas.etapas_mexidas_a_mao(projeto, pagina) == [
        etapas.CORTAR, etapas.ENDIREITAR, etapas.MARCAR, etapas.MOVER]
    etapas.marcar_mexida_a_mao(pagina, etapas.FILTRO)       # o que a tela faz
    assert etapas.etapas_mexidas_a_mao(projeto, projeto.folhas[0]) == [etapas.GIRAR]
    volta = Projeto.de_dicionario(projeto.para_dicionario())
    assert volta.feito_a_mao_sempre_vale is True
    assert sorted(volta.paginas[0].mexida_a_mao) == sorted([
        etapas.CORTAR, etapas.ENDIREITAR, etapas.FILTRO, etapas.MARCAR, etapas.MOVER])
    assert volta.folhas[0].mexida_a_mao == [etapas.GIRAR]


def test_d004_projeto_antigo_sem_os_campos_abre_e_funciona():
    """Migração: o projeto.json de antes desta etapa (sem
    feito_a_mao_sempre_vale nem mexida_a_mao) abre sem erro, como projeto
    antigo, e só marca o que valia (etapa ligada)."""
    dados = {
        "caminho_entrada": "x.pdf", "endireitar": True, "cortar_bordas": False,
        "limpar": True, "filtro_padrao": ORIGINAL,
        "folhas": [{"indice": 0, "dividir": False}],
        "paginas": [{"indice": 0, "folha": 0, "filtro": PRETO_E_BRANCO,
                     "recorte": [0.1, 0.1, 0.8, 0.8], "angulo_manual": 2.0}],
    }
    projeto = Projeto.de_dicionario(dados)
    assert projeto.feito_a_mao_sempre_vale is False
    assert projeto.paginas[0].mexida_a_mao == [etapas.ENDIREITAR]
    assert etapas.recorte_a_mao(projeto, projeto.paginas[0]) is None      # era ignorado
    assert etapas.angulo_a_mao(projeto, projeto.paginas[0]) == 2.0


def test_caminho_rapido_so_cadernos_nao_joga_fora_o_feito_a_mao():
    """D-009 no caminho rápido "só montar cadernos" (que não desenha página
    nenhuma): com uma folha girada à mão no livro novo, o livro passa pelo
    caminho inteiro. No projeto antigo continua o caminho rápido (sai igual)."""
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.dividir_folhas = projeto.limpar = projeto.endireitar = projeto.cortar_bordas = False
    projeto.montar_cadernos = True
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    assert projeto.so_cadernos
    projeto.folhas[0].rotacao = 90
    assert not projeto.so_cadernos
    assert _como_projeto_antigo(projeto).so_cadernos


def test_d009_resumo_diz_que_o_feito_a_mao_vai_junto():
    """D-009 na frase da tela "O que fazer" (core.pipeline.resumo_em_portugues):
    com nada marcado e um corte à mão, ela não diz mais "Marque pelo menos uma
    coisa para eu fazer." - diz que mantém o que foi feito à mão. Sem nada à
    mão a frase é a de sempre."""
    from core.pipeline import resumo_em_portugues

    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.dividir_folhas = projeto.limpar = projeto.endireitar = projeto.cortar_bordas = False
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    assert resumo_em_portugues(projeto, 1) == "Marque pelo menos uma coisa para eu fazer."
    projeto.paginas[0].recorte = (0.1, 0.1, 0.8, 0.8)
    assert resumo_em_portugues(projeto, 1) == "Vou manter o que você fez à mão em 1 página."


# --- Obra de 26/10/2026, etapa 10a: o corte não come a página -----------------
#
# D-104 / D-466 (22/10/2026, `a-comer-pagina`): "Tem mais alguma função que pode
# fazer essa mesma coisa de comer parte da pagina sem que a gente queira no nosso
# programa?" -> os lugares que comem a página, provados em páginas de verdade
# (tests/test_etapa10a_nao_comer.py) e consertados. D-077 (28/09): "não comer
# conteúdo". D-098 (13/10, `g8-moldura-tinta-fora`): "Só avisa" (a peça inteira
# de fora continua fora, com o aviso). D-113 (23/10, `d212-1`): "o primeiro passo
# em uma pagina dessas seria tirar essa moldura preta transformando a pagina em
# totalmente branca sem mexer nas letras". D-095 (12/10, ressalvas do G6):
# "cunhas brancas com corte até a beirada".

def _projeto_borda_ate_a_moldura(tmp_path, img) -> Projeto:
    """Livro com só a borda preta "até a moldura" e o cortar ligados (o resto
    desligado, para a medida ser só do corte)."""
    projeto = _projeto_tudo_desligado(tmp_path, img=img)
    projeto.cortar_bordas = True
    projeto.borda_preta = True
    projeto.borda_preta_ate = "ate_a_moldura"
    return projeto


def _medida_fixa(caixa):
    """corte_pelo_conteudo.medir trocado por uma caixa fixa (a do ScanTailor),
    em pontos da imagem medida; o limite (a página achada) é ela inteira."""
    from core import corte_pelo_conteudo as cc

    def medir(img, dpi_do_desenho=None, dpi_do_scan=None, **_):
        alt, larg = img.shape[:2]
        mm = 25.4 / DPI
        x0, y0, x1, y1 = caixa
        return cc.MedidaDoConteudo(larg, alt, caixa, ((x1 - x0) * mm, (y1 - y0) * mm), (mm, mm),
                                   None, (0.0, 0.0, float(larg), float(alt)))
    return medir


def test_d104_d077_a_caixa_do_scantailor_nao_parte_uma_letra(tmp_path, monkeypatch):
    """D-104 / D-077: a caixa do conteúdo do ScanTailor ("até a moldura") passava
    no meio de uma letra e a cortava. Agora a borda vai até o fim da peça (o
    mesmo limite do corte comum). Prova: a "letra" (20 x 30 pontos) sai inteira."""
    from core import corte_pelo_conteudo as cc

    img = np.full((ALTURA_PX, LARGURA_PX, 3), 245, np.uint8)
    img[300:330, 140:160] = 0                         # a letra que a caixa parte
    for x in range(200, 500, 40):                      # o resto do "texto"
        img[300:330, x:x + 20] = 0
        img[400:430, x:x + 20] = 0
    monkeypatch.setattr(cc, "medir", _medida_fixa((150.0, 290.0, 520.0, 440.0)))
    saida = _gerar(_projeto_borda_ate_a_moldura(tmp_path, img))
    pretos = int((saida.min(axis=2) < 60).sum())
    assert pretos >= 17 * 20 * 30, pretos             # 16 letras do texto + a partida, inteiras


def test_d104_folha_quase_em_branco_nao_vira_tira(tmp_path, monkeypatch):
    """D-104 (lista única 4.8/4.10: Siebmacher 74 e ljs47 2 viravam tiras de
    2,6 x 8,6 cm e 21 x 11 cm): com a caixa do ScanTailor abraçando só uma
    etiqueta pequena, a página fica a página achada. Prova: a página sai com
    pelo menos 90% da largura e da altura da folha."""
    from core import corte_pelo_conteudo as cc

    img = np.full((ALTURA_PX, LARGURA_PX, 3), 235, np.uint8)
    img[700:760, 60:140] = 40                          # a etiqueta no canto
    monkeypatch.setattr(cc, "medir", _medida_fixa((60.0, 700.0, 140.0, 760.0)))
    saida = _gerar(_projeto_borda_ate_a_moldura(tmp_path, img))
    assert saida.shape[1] >= 0.9 * LARGURA_PX and saida.shape[0] >= 0.9 * ALTURA_PX, saida.shape


def test_d113_moldura_escura_sai_antes_do_desentortar_sem_mexer_nas_letras():
    """D-113 (`d212-1`): a moldura escura do scanner é tirada (fica branca) na
    página que o desentortar mede, e as letras ficam. Prova: a cópia sem a
    moldura tem a beirada branca e a mesma tinta dentro da página."""
    from core import desentortar_scantailor as ds

    img = np.full((ALTURA_PX, LARGURA_PX, 3), 220, np.uint8)
    img[:, :40] = 30                                   # moldura escura (scanner)
    img[:30, :] = 30
    for y in range(120, 700, 50):                      # as linhas de texto
        img[y:y + 20, 100:500] = 20
    sem = ds.sem_a_moldura_do_scanner(img)
    assert sem[:, :35].min() >= 250 and sem[:25, :].min() >= 250
    assert np.array_equal(sem[120:700, 100:500], img[120:700, 100:500])


def test_d113_o_desentortar_mede_a_caixa_do_conteudo_sem_a_moldura(monkeypatch):
    """D-113: a caixa do conteúdo que vai ao desentortar é medida sem a moldura
    escura (a causa achada no d212: "com a caixa do programa (pega a moldura
    escura) nada muda")."""
    from core import desentortar_scantailor as ds

    img = np.full((ALTURA_PX, LARGURA_PX, 3), 220, np.uint8)
    img[:, :40] = 30
    vistas = []
    monkeypatch.setattr(ds, "caixa_do_conteudo", lambda im, caixa, dpi: vistas.append(im) or (0, 0, 8, 8))
    monkeypatch.setattr(ds, "desentortar", lambda *a, **k: ds.Resultado(None, motivo="teste"))
    pagina = ConfigPagina(indice=0, folha=0)
    pagina.desentortar = ds.AUTOMATICO
    ds.preparar_no_corte(img, (0, 0, LARGURA_PX, ALTURA_PX), pagina, 150)
    assert vistas and vistas[0][:, :35].min() >= 250


def test_d095_cunha_do_giro_nao_fica_branca_na_beirada(tmp_path):
    """D-095 (ressalvas do G6, 12/10): "cunhas brancas com corte até a beirada".
    Página de papel amarelado girada a mão 1,5 grau, corte a mão até a beirada:
    a cunha do giro sai com a cor do papel, não branca. Prova: quase nenhum
    ponto branco puro nas beiradas da página do PDF."""
    img = np.full((ALTURA_PX, LARGURA_PX, 3), AMARELADO, np.uint8)
    img[300:500, 150:450] = 0
    projeto = _projeto_tudo_desligado(tmp_path, img=img)
    projeto.paginas[0].angulo_manual = 1.5
    projeto.paginas[0].recorte = (0.0, 0.0, 1.0, 1.0)
    saida = _gerar(projeto)
    beiradas = np.concatenate([saida[:, :8].reshape(-1, 3), saida[:, -8:].reshape(-1, 3),
                               saida[:8].reshape(-1, 3), saida[-8:].reshape(-1, 3)])
    assert float((beiradas.min(axis=1) >= 254).mean()) < 0.01


# --- obra de 26/10/2026, etapa 10b (defeitos na imagem final) ------------------
# As medidas nas páginas de verdade estão em tests/test_etapa10b_imagem.py; aqui,
# a prova de comportamento de cada decisão tocada (regra 4 do CLAUDE.md §11).

def _texto_com_notas_na_margem() -> np.ndarray:
    """Página com duas colunas de texto e notas da margem dos dois lados (como
    a página de teste do D-113, Marial 41): as notas só em poucas linhas."""
    img = np.full((ALTURA_PX * 2, LARGURA_PX * 2, 3), 225, np.uint8)
    for y in range(160, 1560, 36):
        for x in range(260, 560, 22):                   # coluna 1
            img[y:y + 16, x:x + 14] = 30
        for x in range(640, 940, 22):                   # coluna 2
            img[y:y + 16, x:x + 14] = 30
    for y in (300, 336, 900):                           # notas da esquerda
        img[y:y + 12, 120:200] = 40
    for y in (500, 536, 1200, 1236):                    # notas da direita
        img[y:y + 12, 1000:1120] = 40
    return img


def test_d493_o_desentortar_segue_so_o_bloco_do_texto():
    """D-493 (27/10/2026, escolha da gerente apoiada em D-113): "O desentortar
    segue só o bloco do texto, sem as notas da margem". Prova: a caixa do
    conteúdo que vai ao desentortar começa no texto (não nas notas da
    esquerda) e acaba no texto (não nas notas da direita). Antes ela ia de nota
    a nota."""
    from core import desentortar_scantailor as ds

    img = _texto_com_notas_na_margem()
    h, w = img.shape[:2]
    x, _y, largura, _a = ds.caixa_do_conteudo(img, (0, 0, w, h), 300)
    assert x >= 240, x
    assert x + largura <= 960, (x, largura)


def test_d493_pagina_sem_notas_tem_a_caixa_de_sempre():
    """D-493: sem nota da margem, a caixa é a de sempre (o texto inteiro)."""
    from core import desentortar_scantailor as ds

    img = _texto_com_notas_na_margem()
    img[:, :230] = 225
    img[:, 960:] = 225
    h, w = img.shape[:2]
    x, _y, largura, _a = ds.caixa_do_conteudo(img, (0, 0, w, h), 300)
    assert x <= 262 and x + largura >= 930


def test_d189_reduzir_cores_no_preto_e_branco_nao_forca_preto(monkeypatch):
    """D-189 (21/10/2026): "Reduzir cores" não pode apagar parte da letra ("Ele
    está apagando as letras"). Prova de comportamento: no Preto e branco com
    "Letras com a cor delas", a posterização vai SEM o "forçar preto e branco"
    (o que jogava metade da palavra no preto); nos outros filtros fica o de
    fábrica do ScanTailor."""
    from core import cores_scantailor as cs

    pedidos = []

    def cores(img, dpi, *, preto_e_branco=None, posterizar=False, opcoes=cs.FABRICA, biblioteca=None):
        pedidos.append(opcoes)
        return cs.st.Resultado(np.zeros(img.shape[:2] + (3,), np.uint8), None, None)

    monkeypatch.setattr(cs, "cores", cores)
    pagina_pb = np.full((60, 80), 255, np.uint8)
    pagina_pb[20:40, 20:60] = 0
    preparada = np.full((60, 80, 3), 200, np.uint8)
    cs.aplicar(preparada, pagina_pb, PRETO_E_BRANCO, True, True, 300)
    cs.aplicar(preparada, preparada, ORIGINAL, False, True, 300)
    assert pedidos[0].forcar_preto_e_branco is False
    assert pedidos[1].forcar_preto_e_branco is True


def test_d193_previa_dos_jeitos_do_scantailor_faz_a_conta_no_dpi_do_pdf(monkeypatch):
    """D-193 (22/10/2026, `lu-tc-igual`): "precisamos que o pdf saia que nem está
    na tela" (a tela cheia mostrava a letra mais grossa). Prova: na prévia, o
    jeito do ScanTailor recebe a página no tamanho e no DPI do PDF, e o
    resultado volta ao tamanho da prévia; no desenho do PDF, nada muda."""
    from core import filtros
    from core import preto_e_branco_scantailor as pbst
    from core.pontinhos_scantailor import Pontinhos

    vistos = []

    def binarizar(img, metodo, forca=50, dpi=None, **_):
        vistos.append((img.shape[:2], dpi))
        return np.full(img.shape[:2], 255, np.uint8)

    monkeypatch.setattr(pbst, "preto_e_branco", binarizar)
    img = np.full((200, 150, 3), 230, np.uint8)
    previa = filtros._preto_e_branco_do_scantailor(img, 50, "st_otsu",
                                                   Pontinhos("desligado", 150.0, 300.0))
    assert vistos[0] == ((400, 300), 300.0) and previa.shape == (200, 150)
    filtros._preto_e_branco_do_scantailor(img, 50, "st_otsu", Pontinhos("desligado", 300.0))
    assert vistos[1] == ((200, 150), 300.0)


def test_d473_d066_a_tinta_forte_do_so_as_letras_nao_depende_da_resolucao():
    """D-473 ("Tela e PDF saem da mesma conta") e D-066 ("precisamos que o pdf
    saia que nem está na tela"), o caso da letra T do Antiphonal 46: no "Só as
    letras" a letra grande vermelha (mais clara que o texto) fica no desenho
    grande (o PDF) E no pequeno (a prévia). Antes, ficava só na prévia."""
    from core import misto

    h, w = 1620, 1350
    grande = np.full((h, w), 230, np.uint8)
    linhas = np.zeros((h, w), bool)
    for y in range(800, 1500, 80):
        for x in range(100, 1250, 22):
            grande[y:y + 27, x:x + 8] = 30
        linhas[y - 5:y + 35, :] = True
    grande[160:430, 160:430] = 75
    grande = cv2.GaussianBlur(grande, (0, 0), 1.2)

    def fica(img, linhas_aqui, altura):
        _, binaria = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
        saida = misto._fora_do_texto(binaria, img, linhas_aqui, altura, misto.FORA_REDE,
                                     np.ones(img.shape, bool))
        a, b = img.shape
        return float((saida[int(.12 * a):int(.25 * a), int(.13 * b):int(.30 * b)] == 0).mean())

    pequena = cv2.resize(grande, (w * 10 // 27, h * 10 // 27), interpolation=cv2.INTER_AREA)
    linhas_p = cv2.resize(linhas.astype(np.uint8), (pequena.shape[1], pequena.shape[0]),
                          interpolation=cv2.INTER_NEAREST) > 0
    assert fica(grande, linhas, 40.0) > 0.9
    assert fica(pequena, linhas_p, 40.0 * 10 / 27) > 0.9
