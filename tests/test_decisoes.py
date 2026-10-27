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
    ignorado (o papel continuava amarelo)."""
    projeto = _projeto_tudo_desligado(tmp_path)
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    img = _gerar(projeto)
    papel = img[50:250, 350:550]
    assert papel.min() >= 250, "o papel devia sair branco (Preto e branco à mão)"
    sem = _gerar(_projeto_tudo_desligado(tmp_path, "sem"))
    assert np.abs(sem[50:250, 350:550].astype(int) - np.array(AMARELADO[::-1])).max() <= 6


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
    filtro diferente do livro, marcação à mão, mover, folha girada) e vai e
    volta pelo projeto.json."""
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
        etapas.CORTAR, etapas.ENDIREITAR, etapas.FILTRO, etapas.MARCAR, etapas.MOVER]
    assert etapas.etapas_mexidas_a_mao(projeto, projeto.folhas[0]) == [etapas.GIRAR]
    volta = Projeto.de_dicionario(projeto.para_dicionario())
    assert volta.feito_a_mao_sempre_vale is True
    assert volta.paginas[0].mexida_a_mao == [
        etapas.CORTAR, etapas.ENDIREITAR, etapas.FILTRO, etapas.MARCAR, etapas.MOVER]
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
    assert projeto.paginas[0].mexida_a_mao == [etapas.ENDIREITAR, etapas.FILTRO]
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
