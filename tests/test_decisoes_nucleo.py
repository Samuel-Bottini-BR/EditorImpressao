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


# --- item 2: o nome do arquivo de saída sem acento ----------------------------

def test_nome_de_saida_sugerido_sai_sem_acento():
    """Lista única 5.15 (teste do Kaique, 23/10/2026): o nome sugerido saía
    "antiphon-trecho - mágico pro.pdf". Regra do projeto (CLAUDE.md §3):
    caminho de disco sem acento - o nome do livro e o do filtro. O mesmo
    sem_acento do nome "para imprimir" (ui/dialogo_impressao.sem_acento)."""
    from core.filtros import MAGICO_PRO
    from modelos import nome_de_saida_sugerido

    projeto = Projeto(caminho_entrada="x.pdf", caminho_saida="", nome="Ofício da Imaculada Conceição")
    projeto.limpar, projeto.filtro_padrao, projeto.montar_cadernos = True, MAGICO_PRO, False
    nome = nome_de_saida_sugerido(projeto)
    assert nome == "Oficio da Imaculada Conceicao - magico pro.pdf"
    assert nome.isascii()


# --- item 3: projeto.json ilegível não some calado ----------------------------

def _pasta_do_projeto(tmp_path, conteudo: str | None):
    import projetos

    pasta = tmp_path / "proj"
    pasta.mkdir()
    if conteudo is not None:
        (pasta / projetos.ARQUIVO_ESTADO).write_text(conteudo, encoding="utf-8")
    return projetos.Resumo(pasta=str(pasta)), pasta


@pytest.mark.parametrize("estragado", ["{ isto nao e json", '{"paginas": 5}', "[1, 2]"],
                         ids=["json_quebrado", "campos_errados", "nao_e_um_projeto"])
def test_d342_projeto_ilegivel_guarda_a_copia_e_avisa(tmp_path, estragado):
    """D-342 (05/10/2026): "o programa quando estiver pronto, ele vai ter que
    ser capaz de abrir arquivos de versões anteriores." Etapa 9c: um
    projeto.json que não dá para ler fazia a conferência recomeçar SEM AVISO
    (carregar_estado devolvia None calado, e o trabalho ia embora com a
    próxima gravação). Agora a leitura guarda a cópia do arquivo estragado ao
    lado (nunca apaga o original) e devolve o sinal com a frase para a tela."""
    import projetos

    resumo, pasta = _pasta_do_projeto(tmp_path, estragado)
    lido = projetos.ler_estado(resumo)
    assert lido.projeto is None
    assert lido.ilegivel
    assert lido.copia is not None and lido.copia.parent == pasta
    assert lido.copia.read_text(encoding="utf-8") == estragado
    assert (pasta / projetos.ARQUIVO_ESTADO).read_text(encoding="utf-8") == estragado
    assert lido.aviso.startswith("Não consegui ler o trabalho salvo deste livro")
    assert str(lido.copia) in lido.aviso.replace("⁠", "")
    # o caminho antigo continua: None para quem só quer o Projeto
    assert projetos.carregar_estado(resumo) is None


def test_projeto_ilegivel_lido_varias_vezes_guarda_uma_copia_so(tmp_path):
    """A janela lê o projeto.json várias vezes ao abrir (abrir_livro,
    continuar, fim da análise): uma cópia só do mesmo arquivo estragado."""
    import projetos

    resumo, pasta = _pasta_do_projeto(tmp_path, "{ quebrado")
    copias = {projetos.ler_estado(resumo).copia for _ in range(3)}
    assert len(copias) == 1
    assert len(list(pasta.glob("projeto.estragado-*"))) == 1


def test_projeto_legivel_ou_ausente_nao_avisa(tmp_path):
    import projetos
    from modelos import Projeto as P

    resumo, pasta = _pasta_do_projeto(tmp_path, None)
    lido = projetos.ler_estado(resumo)
    assert lido.projeto is None and not lido.ilegivel and lido.aviso == ""
    import json
    (pasta / projetos.ARQUIVO_ESTADO).write_text(
        json.dumps(P(caminho_entrada="a.pdf", caminho_saida="", nome="a").para_dicionario()),
        encoding="utf-8")
    lido = projetos.ler_estado(resumo)
    assert lido.projeto is not None and not lido.ilegivel and lido.aviso == ""
    assert not list(pasta.glob("projeto.estragado-*"))


# --- item 4: "Parece em branco" falso em página com texto ---------------------

def _folha_dupla_texto_e_branco() -> np.ndarray:
    """Folha deitada de livro aberto: a página da esquerda com linhas de
    texto, a da direita em branco (só o papel)."""
    img = np.full((800, 1200, 3), 245, np.uint8)
    for y in range(120, 680, 28):                 # linhas de "texto" na esquerda
        img[y:y + 8, 90:520] = 20
    return img


def _projeto_da_folha_dupla(tmp_path) -> Projeto:
    entrada = tmp_path / "dupla.pdf"
    _pdf(entrada, _folha_dupla_texto_e_branco())
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(tmp_path / "s.pdf"),
                      nome="dupla")
    projeto.dividir_folhas = True
    projeto.endireitar = projeto.cortar_bordas = projeto.limpar = False
    projeto.detectar_regioes = projeto.montar_cadernos = False
    projeto.filtro_padrao = ORIGINAL
    projeto.qualidade_dpi = DPI
    # a análise dividiu errado (a 10%, como o ScanTailor na folha 4 do
    # "La vida eterna"): a "página" da esquerda era uma tira de margem, sem
    # texto, e ganhou "Parece em branco"; a da direita, com o texto, não
    folha = ConfigFolha(indice=0, dividir=True, posicao_corte=0.10, e_paisagem=True)
    projeto.folhas = [folha]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, metade="esquerda", filtro=ORIGINAL),
                       ConfigPagina(indice=1, folha=0, metade="direita", filtro=ORIGINAL)]
    return projeto


def test_d271_parece_em_branco_sai_quando_a_divisao_muda_e_a_pagina_tem_texto(tmp_path):
    """D-271 ("Tem que ter um tipo de aviso para cada coisa") e D-288 (página
    com conteúdo não recebe "Parece em branco"). Teste do Kaique (sessão 1,
    26/10/2026, print s1-06; lista única 5.7): "Esta página parece estar em
    branco" na página 7 do "La vida eterna", que tem texto.

    Causa: o aviso é decidido UMA vez, na análise, na metade da folha que a
    análise dividiu (core.pipeline._analisar_a_folha). O ScanTailor dividiu
    a folha 4 a 10% (a linha escura da beirada), a página 7 era uma tira de
    margem e ganhou o aviso; com a divisão acertada (arrastando a linha), a
    página 7 passou a ser a página de texto e o aviso ficou. Antes deste
    conserto nada media o aviso de novo.

    Agora a prévia (renderizar_pagina) mede de novo, na mesma escala da
    análise, a página como ela está dividida agora: com texto, o aviso sai."""
    from core import analise
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina

    projeto = _projeto_da_folha_dupla(tmp_path)
    esquerda, direita = projeto.paginas
    esquerda.alertas = [analise.EM_BRANCO]
    projeto.folhas[0].posicao_corte = 0.5          # a pessoa acertou a divisão
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        renderizar_pagina(doc, projeto, esquerda)
    finally:
        doc.close()
    assert analise.EM_BRANCO not in esquerda.alertas, "página com texto continua 'Parece em branco'"


def test_parece_em_branco_continua_na_pagina_branca_de_verdade(tmp_path):
    """O outro lado: a página branca de verdade (a da direita, só papel)
    continua com o aviso depois da prévia, na prévia de sempre (150 DPI) e na
    do tamanho do PDF (300 DPI)."""
    from core import analise
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina

    projeto = _projeto_da_folha_dupla(tmp_path)
    projeto.folhas[0].posicao_corte = 0.5
    direita = projeto.paginas[1]
    direita.alertas = [analise.EM_BRANCO]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for dpi in (150, 300, 55):
            renderizar_pagina(doc, projeto, direita, dpi=dpi)
            assert analise.EM_BRANCO in direita.alertas, f"a página branca perdeu o aviso ({dpi} DPI)"
    finally:
        doc.close()


LA_VIDA_ETERNA = r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf"


@pytest.mark.skipif(not __import__("os").path.isfile(LA_VIDA_ETERNA),
                    reason="o 'La vida eterna' não está neste computador")
def test_la_vida_eterna_pagina_7_com_texto_perde_o_aviso_e_as_brancas_ficam(tmp_path, monkeypatch):
    """O caso do Kaique, no livro de verdade (só lido; as 6 primeiras folhas
    copiadas para a pasta do teste). A análise de fábrica dava "Parece em
    branco" às páginas 2, 7 e 9 (como no print dele). Com a divisão das folhas
    4 e 5 no meio (a linha azul do print s1-07, 0,55), a página 7 é a página de
    texto "8" e perde o aviso; a 2 (verso em branco da folha 1) e a 9 (verso
    em branco da folha 5) continuam com ele.
    Obra 26/10, etapa 4: a causa das páginas 7 e 9 da análise (o ScanTailor
    dividindo a 10%, na linha da beirada) foi consertada no dividir
    (dividir_scantailor.na_beirada; tests/test_decisoes_dividir.py). Para este
    teste continuar provando o "Parece em branco" que sai quando a divisão
    muda, a análise aqui usa o ScanTailor sem o conserto (na_beirada sempre
    False), como era quando o Kaique viu."""
    from core import analise, dividir_scantailor
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto, renderizar_pagina

    monkeypatch.setattr(dividir_scantailor, "na_beirada", lambda resultado: False)

    copia = tmp_path / "vida6.pdf"
    with fitz.open(LA_VIDA_ETERNA) as livro, fitz.open() as novo:
        novo.insert_pdf(livro, from_page=0, to_page=5)
        novo.save(str(copia))
    projeto = Projeto(caminho_entrada=str(copia), caminho_saida=str(tmp_path / "s.pdf"),
                      nome="vida")
    projeto.dividir_folhas, projeto.endireitar = True, True
    projeto.cortar_bordas = projeto.limpar = False
    analisar_projeto(projeto)
    com_aviso = [p.indice + 1 for p in projeto.paginas if analise.EM_BRANCO in p.alertas]
    assert com_aviso == [2, 7, 9]
    projeto.folhas[3].posicao_corte = 0.55
    projeto.folhas[4].posicao_corte = 0.55
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for indice in (1, 6, 8):
            renderizar_pagina(doc, projeto, projeto.paginas[indice])
    finally:
        doc.close()
    com_aviso = [p.indice + 1 for p in projeto.paginas if analise.EM_BRANCO in p.alertas]
    assert com_aviso == [2, 9]


def test_parece_em_branco_nao_conta_a_beirada_do_livro_como_conteudo():
    """A página branca de verdade com a beirada do livro escaneado (uma
    linha escura comprida embaixo e outra do lado, um pouco tortas, como o
    verso da folha 5 do "La vida eterna") continua "em branco": linha reta
    comprida não é conteúdo. A mesma página com uma só palavra de texto, e
    a página de texto com as mesmas linhas, não são."""
    from core.analise import parece_em_branco

    branca = np.full((1240, 900, 3), 250, np.uint8)
    cv2.line(branca, (180, 1050), (890, 1046), (20, 20, 20), 3)     # beirada de baixo
    cv2.line(branca, (180, 250), (183, 1050), (20, 20, 20), 3)      # beirada do lado
    assert parece_em_branco(branca)
    com_texto = branca.copy()
    for y in range(300, 900, 28):
        com_texto[y:y + 8, 260:760] = 20
    assert not parece_em_branco(com_texto)
    titulo = branca.copy()
    cv2.putText(titulo, "DA ORACAO", (300, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (20, 20, 20), 3)
    assert not parece_em_branco(titulo), "página com título não é 'em branco' (D-288)"


# --- item 5: "as contas discordam" em página reta -----------------------------

@pytest.mark.parametrize("nosso, do_scantailor", [(-0.1, 0.25), (0.1, -0.25), (0.3, 0.0), (-0.15, 0.2)])
def test_d082_pagina_reta_nas_duas_contas_nao_avisa(nosso, do_scantailor):
    """D-082 (05/10/2026): "quando os dois discordarem mais de 0,3 grau, a
    página fica marcada 'conferir'". Etapa 9c (Lista de bugs de 09/10:
    "Endireitar: as contas discordam" em página reta): quando as duas contas
    dão a página quase reta - cada uma a no máximo 0,3 grau do reto, a mesma
    tolerância da decisão -, não há o que conferir. No Boécio (50 páginas),
    eram 4 dos 12 avisos: -0,1 x +0,25, +0,1 x -0,25..."""
    from core.endireitar_scantailor import discordam

    assert not discordam(nosso, do_scantailor)


@pytest.mark.parametrize("nosso, do_scantailor", [(-2.2, -0.25), (-0.1, 0.56), (0.5, 0.12), (-0.0, -1.0)])
def test_d082_contas_que_discordam_de_verdade_continuam_avisando(nosso, do_scantailor):
    """O outro lado: com uma das contas longe do reto e a diferença acima de
    0,3 grau, o aviso continua (Boécio p. 2: -2,2 x -0,4, o print da lista
    única 5.8)."""
    from core.endireitar_scantailor import discordam

    assert discordam(nosso, do_scantailor)


# --- item 7: "menor que o corte" com os dois números iguais ------------------

@pytest.mark.parametrize("unidade", ["cm", "mm", "polegada"])
@pytest.mark.parametrize("recorte", [(13.944, 20.031), (14.8, 21.0), (12.3456, 18.7654)])
def test_folha_do_tamanho_do_corte_nao_avisa_menor_que_o_corte(unidade, recorte):
    """Teste do Kaique / Lista de bugs de 02/10: "'Tamanho da folha' abre com
    o aviso 'menor que o corte' mesmo com tamanho igual ao corte". A janela
    abre com os campos no tamanho do corte, arredondado às casas da unidade
    (core.unidades.CASAS: 13,944 cm vira 13,94); a conta exigia 0,001 cm de
    folga, e o arredondamento para baixo bastava para o aviso aparecer com os
    dois números iguais. Agora a folga é a do arredondamento dos campos."""
    from core import unidades
    from core.folha import tamanho_da_folha_cabe

    unidade = {"cm": unidades.CM, "mm": unidades.MM, "polegada": unidades.POLEGADA}[unidade]
    escolhido = tuple(unidades.para_cm(round(unidades.de_cm(v, unidade), unidades.CASAS[unidade]),
                                       unidade) for v in recorte)
    assert tamanho_da_folha_cabe(escolhido, recorte)


def test_folha_menor_de_verdade_continua_avisando():
    from core.folha import tamanho_da_folha_cabe

    assert not tamanho_da_folha_cabe((13.8, 20.0), (13.944, 20.031))     # 1,4 mm menor
    assert not tamanho_da_folha_cabe((14.8, 20.9), (14.8, 21.0))         # 1 mm mais baixa


# --- item 6: textos do núcleo que aparecem na tela ----------------------------

def test_d479_o_jeito_do_proprio_programa_se_chama_o_do_editor():
    """D-479 (26/10/2026): "o do Editor" / "a do Editor" em todo lugar onde
    aparece o jeito ou a conta do próprio programa. Os nomes do núcleo (que
    a frase-resumo de "O que fazer" e o Histórico usam) diziam "o do
    programa" / "a do programa"."""
    from core import dividir_scantailor as ds
    from core import endireitar_scantailor as es

    assert ds.NOMES_DOS_JEITOS[ds.JEITO_PROGRAMA] == "o do Editor"
    assert es.NOMES_DOS_JEITOS[es.JEITO_PROGRAMA] == "a do Editor"
    assert all("do programa" not in t for t in (*ds.NOMES_DOS_JEITOS.values(),
                                                 *es.NOMES_DOS_JEITOS.values()))


def test_d479_resumo_do_livro_diz_o_do_editor():
    from core import dividir_scantailor as ds
    from core.pipeline import resumo_em_portugues

    projeto = Projeto(caminho_entrada="x.pdf", caminho_saida="", nome="x")
    projeto.dividir_folhas, projeto.dividir_como = True, ds.JEITO_PROGRAMA
    texto = resumo_em_portugues(projeto, 10)
    assert "(jeito: o do Editor)" in texto and "do programa" not in texto


def test_textos_com_singular_no_1_e_acento():
    """D-365 ("Corrija TODOS os textos da interface para português correto")
    e o teste do Kaique (auditoria de 26/10: "1 foram apagadas", "1
    cadernos"): no núcleo, o Histórico do girar dizia "(1 folhas)", o "Tirar o
    fundo" dizia "1 figura(s)" e a conferência dos cadernos "Nao ha
    paginas"."""
    from core import cadernos, girar

    frase = girar.descricao_do_giro(90, girar.ALCANCE_DAQUI, 179, 1)
    assert "(1 folha)" in frase and "1 folhas" not in frase and "virada como" in frase
    assert "(3 folhas)" in girar.descricao_do_giro(90, girar.ALCANCE_DAQUI, 177, 3)
    assert cadernos.conferir_sequencia(0, 16)[1] == "Não há páginas para conferir."
    assert "1 caderno pronto" in cadernos.instrucoes_de_impressao(8, 16)[-1]
