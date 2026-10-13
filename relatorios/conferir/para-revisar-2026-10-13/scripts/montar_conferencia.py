"""Monta o conferencia.json (para a gerente montar a pagina do Samuel) e o
relatorio nos tres formatos (conferencia.md / .html / .pdf, com relatorio.gravar).

So junta o que foi conferido: os textos estao aqui, as imagens em img/, os
numeros da velocidade em velocidade/rodadas/ e os das 89 paginas em
conferir-89-como-a-janela.json. Nao mede nada e nao muda o programa.
"""
import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
RAIZ = BASE.parents[2]
sys.path.insert(0, str(RAIZ))
IMG = BASE / "img"


def n(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


def img(nome, legenda):
    assert (IMG / f"{nome}.jpg").exists(), nome
    return {"src": f"img/{nome}.jpg", "legenda": legenda}


# ------------------------------------------------------------------ velocidade
MEDIDAS = [("abrir_total_s", "Abrir o livro (300 folhas)", 1),
           ("troca_media_s", "Trocar de página (média de 20)", 2),
           ("troca_pior_s", "Trocar de página (a pior das 20)", 2),
           ("processar_magico_pro_s", "Processar 10 páginas em Mágico pro", 1),
           ("processar_preto_e_branco_s", "Processar 10 páginas em Preto e branco", 1)]


def velocidade():
    pasta = BASE / "velocidade" / RODADAS
    rodadas = []
    for nome in ("antes-1", "depois-1", "antes-2", "depois-2"):
        arqs = sorted((pasta / nome).glob("velocidade-*.json")) if (pasta / nome).is_dir() else []
        if not arqs:
            continue
        d = json.loads(arqs[0].read_text(encoding="utf-8"))
        a = json.loads((pasta / nome / "anotacao.json").read_text(encoding="utf-8-sig"))
        rodadas.append({"nome": nome, "braco": nome.split("-")[0], "d": d, "a": a})
    if len(rodadas) < 4:
        return None
    linhas = []
    for r in rodadas:
        res = r["d"]["resumo"]
        linhas.append({"rodada": r["nome"], "commit": r["a"]["commit"], "hora": r["a"]["inicio"][11:16],
                       "memoria_livre_gb": r["a"]["memoria_livre_antes_gb"],
                       "processador_pct": r["a"]["processador_antes_pct"],
                       "outros_pythons": r["a"].get("outros_pythons"),
                       "minutos": r["a"]["minutos"], "saida": r["a"]["codigo_de_saida"],
                       "pico_mb": round(r["d"]["memoria"]["pico_mb"]),
                       **{ch: res[ch]["mediana"] for ch, *_ in MEDIDAS}})
    comp = []
    for ch, nome, casas in MEDIDAS:
        a = [r["d"]["resumo"][ch]["mediana"] for r in rodadas if r["braco"] == "antes"]
        d = [r["d"]["resumo"][ch]["mediana"] for r in rodadas if r["braco"] == "depois"]
        ma, md = statistics.fmean(a), statistics.fmean(d)
        ruido = max(max(a) - min(a), max(d) - min(d))
        dif = md - ma
        pares = [d[i] - a[i] for i in range(2)]
        mesmo_lado = all(p > 0 for p in pares) or all(p < 0 for p in pares)
        if abs(dif) <= ruido or not mesmo_lado:
            veredito = "não dá para dizer (diferença menor que o vai-e-vem entre rodadas iguais)"
        else:
            veredito = "mais lento" if dif > 0 else "mais rápido"
        comp.append({"medida": nome, "antes": ma, "depois": md, "diferenca": dif, "pct": dif / ma * 100,
                     "vai_e_vem_antes": max(a) - min(a), "vai_e_vem_depois": max(d) - min(d),
                     "pares": pares, "veredito": veredito, "casas": casas})
    return {"rodadas": linhas, "comparacao": comp}


# ------------------------------------------------------------------ conteudo
COMMIT = "36b9e32"
COMMIT_ANTES = "88d7ff2"
RODADAS = "rodadas"
TITULO = "# Conferência do \"Para revisar\" (Fase 2), 13/10/2026"
EXTRA_MD = ""          # texto a mais depois da pergunta (2a conferencia)
EXTRA_JSON = {}        # campos a mais no conferencia.json
EXTRA_COMO = []        # linhas a mais em "Como foi feito"
AS_89 = None
TEMPOS_MD = None
NOTA_COMMIT = "O `b5b224f` (só o `teste_botoes.py`) não foi trazido: o programa é o mesmo."

RESUMO_PARAGRAFOS = [
    "O programa passa a avisar, página por página, quando o \"Só as letras\" do Preto e branco pode ter estragado alguma coisa: "
    "um desenho ou letra grande que sumiu, texto que saiu falhado, página que não tem nada do livro. Cada aviso traz o botão do conserto: "
    "\"Trazer de volta nesta página\", \"Deixar em branco\", \"Tirar do livro\", \"Desfazer\".",
    "Quando o texto sai falhado, o programa escurece sozinho a força do preto só naquela página e avisa (dá para desfazer, e há uma caixinha "
    "para desligar isso na tela \"O que fazer\"). Ao clicar em \"Confirmar e processar\" com avisos sem olhar, aparece a lista "
    "\"Página N - motivo\", com \"ver\" e \"continuar assim mesmo\".",
    "O Kaique pode dizer \"está bom\" numa página, num motivo de uma página, num motivo em todas as páginas ou em tudo, e o Ctrl+Z desfaz cada um. "
    "Na janela de verdade os seis pedaços funcionaram e o livro foi processado até \"Ficou pronto!\" três vezes, sem erro.",
]

VEREDITO = ("PRONTO PARA CONFERIR, com duas ressalvas graves: os seis pedaços funcionam na janela, mas a tela mostra a letra que o PDF vai apagar "
            "(quem confere pelo olho dá \"está bom\" numa página que sai errada), e na janela a regra não decide igual à conferência das 89 páginas.")

ITENS = [
    "BOM: os seis pedaços funcionam na janela de verdade, com mouse e teclado nativos (Antiphonal 46, Graduale 222, Egenloff 3 e 12, Rariora 8, Camões 27).",
    "BOM: processar até \"Ficou pronto!\" funcionou três vezes (com aviso pendente, passando por \"ver\" e por \"continuar assim mesmo\"; sem aviso; e depois de \"está bom nas marcadas\"). Os PDFs saíram com as 6 páginas e o erros.log ficou vazio.",
    "BOM: todos os \"está bom\" e todos os botões de conserto voltam com Ctrl+Z.",
    "BOM: projeto feito no programa de hoje abre no ramo em 7 segundos, o aviso antigo \"Tinta forte fora do texto\" some sozinho e a força do preto sozinha vem desligada nele.",
    "RESSALVA GRAVE: a tela não mostra o defeito. No Antiphonal 46 o aviso está certo (a letra T some no PDF), mas o cartão e o \"Ver de perto\" mostram a letra T inteira. Quem olha conclui que está bom.",
    "RESSALVA GRAVE: na janela a regra não mede igual à conferência do implementador. Medindo as 89 páginas na ordem em que a janela mede (primeiro a prévia, depois a medida), vão 24 e acertam 73; o implementador mediu 22 e 75; o combinado com o Samuel era 21 e 78.",
    "RESSALVA: só a página visitada é medida. Num livro de 298 páginas, com 2 visitadas, a lista mostrou 2 avisos de desenho apagado; depois de visitar mais 4, mostrou 4. É a pergunta para o Samuel.",
    "RESSALVA: dar dois cliques no cartão para ver de perto conta como \"está certo\" e o aviso some (o Ctrl+Z traz de volta).",
    "RESSALVA: nos avisos \"Parece em branco\" e \"Página sem conteúdo\" não há botão \"está bom assim\"; só \"Deixar em branco\" e \"Tirar do livro\". Na Gladstone 18 (que tem título e não está em branco) isso é ruim.",
    "RESSALVA: a lista \"Antes de processar\" mistura os avisos novos com os de sempre. No Camões são 105 linhas, e só 5 são da regra nova.",
    "RESSALVA: o teste de velocidade não liga o \"Só as letras\"; ele mostra que o resto não ficou mais lento, não mede o custo novo. Na janela, a medida de cada página visitada chegou de 4 a 11 segundos depois de trocar de página nos livros comuns e de 20 a 26 segundos no Antiphon (folha grande).",
    "RESSALVA: no tamanho de janela maximizada só conferi uma tela (Antiphonal 46, onde a marca laranja aparece bem). Todo o resto foi em 1280 x 657.",
]

QUADROS = [
    {"id": "pr-letra-t", "nome": "Antiphonal 46: a letra T que some", "tipo": "melhor", "selo": "funciona",
     "olhar": "O aviso laranja, o quadradinho laranja em volta da letra T nos cartões e o botão \"Trazer de volta nesta página\".",
     "texto": "O aviso aparece sozinho uns 8 segundos depois de chegar na página, com o lugar marcado em laranja. O botão troca só essa página para \"Guardar tudo\", o aviso some e a página sai da lista. O Ctrl+Z desfaz.",
     "ressalva": "Em 1280 x 657 os cartões são pequenos: a marca laranja quase não se vê e o nome do filtro fica escrito por cima da miniatura. No tamanho de maximizada aparece bem. Repare que no cartão a letra T continua lá: é o defeito do quadro seguinte.",
     "imgs": [img("letra-t-0-marca-recorte", "A marca laranja em volta da letra T nos cartões (ampliado, janela no tamanho de maximizada)"),
              img("letra-t-1-aviso-recorte", "Os cinco cartões, o aviso e os dois botões"),
              img("letra-t-2-aviso-tela", "A tela inteira no tamanho de janela maximizada (1920 x 1020), página 46 de 298"),
              img("letra-t-5-aviso-tela-1280x657", "A mesma tela em 1280 x 657: os cartões ficam pequenos e o nome do filtro fica por cima da miniatura"),
              img("letra-t-3-trazer-de-volta-recorte", "Depois de \"Trazer de volta nesta página\": \"Guardar tudo\" ligado, aviso e marca sumiram"),
              img("letra-t-4-ctrlz-tela", "Depois do Ctrl+Z: o aviso e os botões voltaram")]},
    {"id": "pr-tela-engana", "nome": "A tela mostra a letra T, o PDF sai sem ela", "tipo": "pior", "selo": "defeito grave",
     "olhar": "A letra T grande à esquerda: na tela ela aparece; na página do PDF que saiu, não.",
     "texto": "O aviso diz a verdade, a tela não. A página que aparece na tela é desenhada pequena, e nesse tamanho a letra T fica. O PDF é desenhado grande, e nele a letra some. Processei o livro na janela: no PDF a letra T sumiu mesmo.",
     "ressalva": "Quem confere olhando a tela vê a letra no lugar e clica \"está bom assim\". Enquanto a tela não mostrar o que sai no PDF, o aviso manda olhar uma coisa que não dá para ver. Já era assim antes desta mudança; ela só deixou à vista.",
     "imgs": [img("tela-engana-1-comparacao", "O mesmo pedaço da página 46: à esquerda o \"Ver de perto\" da janela; à direita o PDF que o programa gerou"),
              img("tela-engana-2-ver-de-perto-tela", "O \"Ver de perto\" inteiro, com o aviso de pé: a letra T está lá"),
              img("tela-engana-3-pagina-do-pdf", "A página inteira tirada do PDF gerado pela janela: no lugar da letra T sobrou um tracinho")]},
    {"id": "pr-so-o-texto", "nome": "Graduale 222: \"Guardar só o texto\" apaga a música", "tipo": "melhor", "selo": "funciona",
     "olhar": "O cartão do Preto e branco sem as pautas, a marca laranja na página inteira e o botão \"Trazer de volta nesta página\".",
     "texto": "No jeito de fábrica (\"Guardar a tinta forte\") a página 222 não tem aviso nenhum. Trocando para \"Guardar só o texto\", o aviso aparece e o botão devolve só essa página para \"Guardar a tinta forte\". As outras páginas não mudam.",
     "ressalva": "Usei um pedaço de 7 páginas do Graduale (219 a 225), para não abrir as 750 folhas. Na janela a página se chama 4.",
     "imgs": [img("so-o-texto-1-aviso-recorte", "O aviso do \"Guardar só o texto\", com a marca laranja (ampliado)"),
              img("so-o-texto-2-aviso-tela", "A tela inteira"),
              img("so-o-texto-3-trazer-de-volta-recorte", "Depois do botão: a música voltou e o aviso sumiu")]},
    {"id": "pr-sem-conteudo", "nome": "Egenloff 12 e Rariora 8: página sem conteúdo", "tipo": "melhor", "selo": "funciona",
     "olhar": "Os dois botões, \"Deixar em branco\" e \"Tirar do livro\", e o que cada um faz com a página.",
     "texto": "\"Deixar em branco\" põe uma folha branca no lugar: o livro continua com 138 páginas. \"Tirar do livro\" apaga a página: ficam 137. Os dois voltam com Ctrl+Z, e depois de \"Deixar em branco\" aparece o botão \"voltar a página\".",
     "ressalva": "Esse aviso não tem \"está bom assim\". Quem quiser a página como está só consegue pelo painel, pela lista ou pela barra de espaço.",
     "imgs": [img("sem-conteudo-1-egenloff-recorte", "Egenloff 12: o aviso e os dois botões (ampliado)"),
              img("sem-conteudo-2-egenloff-tela", "A tela inteira"),
              img("sem-conteudo-3-deixar-em-branco-recorte", "Depois de \"Deixar em branco\": folha branca no lugar e botão \"voltar a página\""),
              img("sem-conteudo-4-tirar-do-livro-recorte", "Depois de \"Tirar do livro\": a página 12 fica apagada na tira e o botão vira \"restaurar página\""),
              img("sem-conteudo-5-rariora-recorte", "Rariora 8: o mesmo aviso, com os dois botões")]},
    {"id": "pr-parece-em-branco", "nome": "Gladstone 18: \"Parece em branco\" numa página com título", "tipo": "igual", "selo": "erro conhecido",
     "olhar": "A página tem o título \"DA ORAÇÃO\" e mesmo assim o programa pergunta se quer deixar em branco ou tirar do livro.",
     "texto": "Os dois avisos ficaram separados, como o Samuel pediu, e cada um tem os dois botões. O erro da Gladstone 18 continua igual: já está na Lista de bugs e não fazia parte deste trabalho.",
     "ressalva": "Agora o aviso errado vem com o botão \"Tirar do livro\" ao lado e sem \"está bom assim\". Um clique distraído tira do livro uma página que tem título.",
     "imgs": [img("parece-em-branco-1-recorte", "Gladstone 18: o aviso \"Parece em branco\" e os dois botões (ampliado)"),
              img("parece-em-branco-2-tela", "A tela inteira"),
              img("parece-em-branco-3-a-pagina", "A página de perto: tem o título \"DA ORAÇÃO\"")]},
    {"id": "pr-forca-sozinha", "nome": "Camões 27 e Egenloff 3: a força do preto sozinha", "tipo": "melhor", "selo": "funciona",
     "olhar": "O medidor em \"bem forte\", o aviso \"escureci a força do preto só nela\" e o botão \"Desfazer\".",
     "texto": "O programa leva a força do preto de 50 para 85 só nessa página e avisa. \"Desfazer\" devolve para 50 e aí aparece o aviso \"Texto falhado\" com \"usar mais escuro\"; o Ctrl+Z refaz. No Egenloff 3 a força não resolve o vermelho e os dois avisos ficam juntos. A caixinha fica na tela \"O que fazer\" e vem ligada no livro novo.",
     "ressalva": "A caixinha só aparece depois de rolar a lista de opções para baixo. No Camões 104 a força mais escura trouxe dois avisos novos (desenho apagado e figura além da gravura).",
     "imgs": [img("forca-1-camoes-recorte", "Camões 27: o aviso, o medidor em \"bem forte\" e o \"Desfazer\" (ampliado)"),
              img("forca-2-camoes-tela", "A tela inteira"),
              img("forca-3-desfazer-recorte", "Depois do \"Desfazer\": força normal e o aviso \"Texto falhado\""),
              img("forca-4-egenloff-3-recorte", "Egenloff 3: aviso 1 de 3 desta página"),
              img("forca-5-caixinha-recorte", "A caixinha \"Escurecer sozinho a força do preto quando o texto sair falhado\""),
              img("forca-6-caixinha-tela", "A tela \"O que fazer\" inteira")]},
    {"id": "pr-antes-de-processar", "nome": "A janela \"Antes de processar\"", "tipo": "misto", "selo": "funciona, lista longa",
     "olhar": "As linhas \"Página N - motivo\", e os botões \"ver\" e \"continuar assim mesmo\".",
     "texto": "\"ver\" leva à página e não processa. \"continuar assim mesmo\" segue para escolher a pasta e processa até \"Ficou pronto!\". Fechar no X não processa. O PDF saiu com as 6 páginas em 5 segundos e o erros.log ficou vazio.",
     "ressalva": "A lista junta os avisos novos com os de sempre. No Camões são 105 linhas: 59 de qualidade baixa, 35 do endireitar, e só 5 da regra nova. A frase de cima diz \"100 páginas\" e o painel ao lado diz 40. Logo depois, a janela de salvar diz \"6 páginas que você não conferiu\", outra conta.",
     "imgs": [img("antes-1-lista-egenloff", "Egenloff: 31 linhas, uma por motivo de cada página"),
              img("antes-2-depois-do-ver-tela", "Depois de \"ver\": o programa foi para a página do aviso e não processou"),
              img("antes-3-lista-camoes", "Camões: 105 linhas; as da regra nova ficam perdidas no meio"),
              img("antes-4-confirmar", "Depois de \"continuar assim mesmo\": a janela de salvar"),
              img("antes-5-ficou-pronto-tela", "\"Ficou pronto!\": 6 páginas")]},
    {"id": "pr-esta-bom", "nome": "\"Está bom\" em cada nível, com Ctrl+Z", "tipo": "melhor", "selo": "funciona",
     "olhar": "O número do painel \"Para revisar\" e o contador de páginas descendo em cada nível.",
     "texto": "Um motivo de uma página: de 31 para 30 avisos, e o aviso seguinte da página aparece. Um motivo em todas: de 31 para 6. Em tudo: \"tudo certo\". Na lista grande, marquei duas linhas e dei \"está bom nas marcadas\": de 31 para 29. O Ctrl+Z desfez cada um.",
     "ressalva": "Os botões \"ver a lista…\" e \"está bom em tudo\" ficam no fim do painel e só aparecem rolando a coluna da direita.",
     "imgs": [img("esta-bom-1-um-motivo-recorte", "Egenloff 3 depois de \"está bom assim\" no primeiro aviso: agora mostra o segundo (aviso 1 de 2)"),
              img("esta-bom-2-motivo-em-todas-tela", "Depois de \"está bom: todas\" no motivo do endireitar: sobram 4 páginas"),
              img("esta-bom-3-em-tudo-tela", "Depois de \"está bom em tudo\": nenhuma página marcada na tira"),
              img("esta-bom-4-seletor", "A lista grande com duas linhas marcadas")]},
    {"id": "pr-janela-diferente", "nome": "Graduale 221: na janela o aviso aparece, na conferência das 89 não", "tipo": "pior", "selo": "regra muda",
     "olhar": "O aviso \"Desenho apagado\" e as marcas laranja na beirada esquerda, onde não sumiu desenho nenhum.",
     "texto": "O implementador mediu cada página direto no tamanho do PDF. Na janela, a página pequena da tela é desenhada antes, e isso muda a medida que vem depois. Refiz as 89 páginas na ordem da janela: 4 mudam de decisão e 3 mudam de motivo.",
     "ressalva": "Na ordem da janela: 24 vão, 73 certas (implementador: 22 e 75; combinado com o Samuel: 21 e 78). Passam a ir sem precisar o Graduale 221, a Matemática 72 e o Palatino 113; o Opus Majus 20 deixa de ir. Medi com a força sozinha desligada, como ele.",
     "imgs": [img("janela-diferente-1-graduale-221-recorte", "Graduale 221 na janela: \"Desenho apagado\", com a marca na beirada esquerda (ampliado)"),
              img("janela-diferente-2-graduale-221-tela", "A tela inteira (página 3 do pedaço de 7 páginas)")]},
    {"id": "pr-cursus-3", "nome": "Cursus 3: passou a ir para a lista", "tipo": "misto", "selo": "aviso certo",
     "olhar": "A faixa preta larga à direita da página e a linha preta à esquerda.",
     "texto": "O aviso faz sentido para quem olha: a página sai com uma faixa preta larga. O que está errado é o corte do livro novo, que deixa a faixa; no corte de antes ela não sobrava. O aviso só conta o que o corte fez.",
     "ressalva": "É defeito do corte do livro novo, não do aviso. Vale a gerente olhar junto do item do corte.",
     "imgs": [img("cursus-3-1-pagina-recorte", "A página 3 como sai em Preto e branco, de perto"),
              img("cursus-3-2-aviso-recorte", "O aviso \"Faixa escura na beirada\""),
              img("cursus-3-3-tela", "A tela inteira")]},
    {"id": "pr-opus-20", "nome": "Opus Majus 20: na janela não foi para a lista", "tipo": "igual", "selo": "sem aviso",
     "olhar": "A foto da estátua fica inteira, como no original.",
     "texto": "Pelos números do implementador ela passaria a ir (\"figura além da gravura\"). Na janela não foi: só apareceu o aviso do endireitar, que não é deste trabalho. A página está boa e não precisava ir.",
     "ressalva": "É mais um caso em que a janela decide diferente da conferência das 89 páginas (aqui, para melhor). Abri a página sozinha, do gabarito; o livro inteiro não está no acervo.",
     "imgs": [img("opus-majus-20-1-pagina-recorte", "A página como sai, de perto: a foto ficou intacta"),
              img("opus-majus-20-2-aviso-recorte", "O único aviso é o do endireitar"),
              img("opus-majus-20-3-tela", "A tela inteira")]},
    {"id": "pr-palatino-66", "nome": "Palatino 66: passou a ir, com a força escurecida", "tipo": "pior", "selo": "sem precisar",
     "olhar": "Os pontinhos pretos em volta da moldura e as letras de traço fino.",
     "texto": "O programa achou o texto falhado, escureceu a força do preto e avisou. Para quem olha, o aviso se entende, mas a página não precisava: é uma página de caligrafia, de traço fino de propósito, e a força mais escura sujou a moldura.",
     "ressalva": "Aqui a força sozinha mexeu numa página que estava boa. Com o \"Desfazer\" volta ao normal.",
     "imgs": [img("palatino-66-1-pagina-recorte", "A página 66 com a força escurecida, de perto"),
              img("palatino-66-2-aviso-recorte", "O aviso e o \"Desfazer\""),
              img("palatino-66-3-tela", "A tela inteira")]},
    {"id": "pr-antiphon-260", "nome": "Antiphon 260: deixou de ir e devia ir", "tipo": "pior", "selo": "escapa",
     "olhar": "A iluminura no meio da página saiu chapada em preto e branco, e há uma faixa preta larga embaixo.",
     "texto": "Na primeira visita apareceu o aviso da faixa escura. Depois de visitar mais três páginas, a faixa virou aviso do livro e a página 260 ficou sem aviso nenhum da regra. A iluminura estragada, que era o motivo de ela ir, ninguém avisa.",
     "ressalva": "O aviso da faixa aparece e some conforme a pessoa visita outras páginas (vira aviso do livro quando 70% das páginas medidas têm faixa). No Antiphon cada página levou de 20 a 26 segundos para ser medida.",
     "imgs": [img("antiphon-260-1-pagina-recorte", "A página 260 como sai em Preto e branco, de perto"),
              img("antiphon-260-2-aviso-recorte", "Depois de visitar outras páginas: só o aviso do endireitar"),
              img("antiphon-260-3-tela", "A tela inteira: a faixa virou frase do livro, no alto do painel (meio encoberta pelo título do painel)")]},
    {"id": "pr-camoes-66", "nome": "Camões 66: as linhas pretas da beirada", "tipo": "igual", "selo": "sem aviso",
     "olhar": "O aviso desta página é só o do endireitar. Não há aviso das linhas pretas, nem na página nem no livro.",
     "texto": "O Samuel decidiu que basta um aviso no livro. Ele não aparece no Camões: nas 5 páginas que visitei o programa não contou faixa em nenhuma, porque as linhas são finas. As linhas continuam saindo no resultado.",
     "ressalva": "O plano já diz que isso depende do corte (item 2.13). Fica registrado que hoje o Camões não recebe aviso nenhum disso.",
     "imgs": [img("camoes-66-1-recorte", "Camões 66: o único aviso é o do endireitar (ampliado)"),
              img("camoes-66-2-tela", "A tela inteira")]},
    {"id": "pr-projeto-antigo", "nome": "Projeto feito antes desta mudança", "tipo": "igual", "selo": "abre igual",
     "olhar": "No ramo, a página 3 mostra \"Texto falhado\" com a força em \"normal\": o programa não escureceu sozinho.",
     "texto": "Criei um projeto no programa de hoje, com o aviso antigo \"Tinta forte fora do texto\" em 8 páginas, fechei e abri no ramo. Abriu em 7 segundos, o aviso antigo sumiu sozinho, a força do preto sozinha veio desligada e o erros.log ficou vazio.",
     "ressalva": "É um projeto de hoje (já com o endireitar antes de cortar). Não abri um projeto de antes de 09/10, porque esses só existem na pasta de dados de verdade do Samuel.",
     "imgs": [img("antigo-1-no-programa-de-hoje-recorte", "No programa de hoje, página 12: o aviso antigo \"Tinta forte fora do texto\""),
              img("antigo-4-no-ramo-p12-recorte", "O mesmo projeto no ramo, página 12: o aviso antigo sumiu e, depois de medir, veio \"Página sem conteúdo\""),
              img("antigo-2-no-ramo-recorte", "No ramo, página 3: \"Texto falhado\", força normal, botão \"usar mais escuro\""),
              img("antigo-3-no-ramo-tela", "A tela inteira")]},
]

PERGUNTA_MEDIR = {
    "id": "pr-medir-o-livro",
    "titulo": "Quando o programa mede as páginas que você não visitou?",
    "explicacao": [
        "O que você está escolhendo: em que hora o programa confere as páginas que ninguém abriu. Hoje ele só confere a página que está na tela. "
        "As outras só são conferidas na hora de gerar o PDF, quando já não dá para parar.",
        "Por isso a lista \"Antes de processar\" só mostra as páginas que você visitou. No Antiphonal de 298 páginas, com 2 visitadas, a lista mostrou 2 avisos de desenho apagado; "
        "visitei mais 4 e ela passou a mostrar 4. E a força do preto sozinha pode escurecer uma página que ninguém viu.",
        "Conferir uma página custa tempo: na janela, de 4 a 11 segundos nos livros comuns e de 20 a 26 segundos no Antiphon, de folha grande. "
        "O implementador mediu, sem a tela, de 13 a 15 minutos para um livro de 300 páginas.",
    ],
    "opcoes": [
        {"id": "medir-por-tras", "nome": "Medir o livro inteiro por trás, depois de abrir",
         "texto": "Bom: a lista fica completa enquanto você confere, e nenhuma página muda sem aparecer na lista. Ruim: o PC trabalha de 13 a 15 minutos num livro de 300 páginas (pela conta do implementador; na janela pode chegar a 50 minutos, e a umas 2 horas em livro de folha grande), e a tela pode ficar mais lenta nesse tempo.",
         "sugestao_do_verificador": True,
         "imgs": [img("medir-1-listas", "Hoje: a lista cresce conforme as páginas são visitadas")]},
        {"id": "medir-ao-processar", "nome": "Medir o que falta só ao clicar em \"Confirmar e processar\"",
         "texto": "Bom: o PC só trabalha quando você pede, e a lista sai completa antes do PDF. Ruim: você espera esse mesmo tempo parado na hora de processar, olha a lista, e depois espera de novo o PDF ser gerado.",
         "imgs": []},
        {"id": "deixar-como-esta", "nome": "Deixar como está",
         "texto": "Bom: nada fica mais lento. Ruim: a lista só mostra as páginas visitadas; as outras saem no PDF do jeito que o programa decidiu, e o aviso só aparece depois.",
         "imgs": [img("medir-2-lista-inteira", "A lista de hoje no Antiphonal, com 2 páginas visitadas de 298")]},
        {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito, com mais exemplos.", "imgs": []},
    ],
    "sugestao": "Sugestão do verificador (é minha, não é decisão): \"Medir o livro inteiro por trás, depois de abrir\", com uma barra de andamento. "
                "É a única em que a lista está completa na hora em que o Kaique decide, e a espera acontece enquanto ele já está conferindo.",
}

BUGS = [
    ("13/10/2026", "A tela mostra o que o PDF não tem: no \"Só as letras\", a página da tela (e do \"Ver de perto\") é desenhada pequena e mostra a letra T do Antiphonal 46; no PDF a letra some. O aviso está certo, mas não dá para conferir pelo olho.", "img/tela-engana-1-comparacao.jpg"),
    ("13/10/2026", "A medida do \"Para revisar\" muda quando a prévia da tela foi desenhada antes (é sempre o caso na janela). Nas 89 páginas, na ordem da janela: 24 vão e 73 certas, contra 22 e 75 medindo direto. Mudam Graduale 221, Matemática 72, Palatino 113 (passam a ir) e Opus Majus 20 (deixa de ir).", "img/janela-diferente-1-graduale-221-recorte.jpg"),
    ("13/10/2026", "Dois cliques no cartão do filtro (o jeito de abrir o \"Ver de perto\") gravam \"Filtro da página: Preto e branco para Preto e branco\", a página fica como conferida e o aviso some. O Ctrl+Z desfaz. Pelo duplo clique na miniatura da tira não acontece.", "img/bug-duplo-clique-tira-o-aviso-tela.jpg"),
    ("13/10/2026", "Os avisos \"Parece em branco\" e \"Página sem conteúdo\" não têm \"está bom assim\": só \"Deixar em branco\" e \"Tirar do livro\". Na Gladstone 18, que tem título, o aviso errado só oferece essas duas saídas.", "img/parece-em-branco-1-recorte.jpg"),
    ("13/10/2026", "A lista \"Antes de processar\" mistura os avisos da regra com os de sempre (Camões: 105 linhas, 5 da regra). A frase diz \"100 páginas\", o painel diz 40, e a janela de salvar, logo depois, diz \"6 páginas que você não conferiu\".", "img/antes-3-lista-camoes.jpg"),
    ("13/10/2026", "Depois de clicar num botão do aviso, o teclado fica nesse botão: a seta para a direita não troca de página (pula para outro botão) e a barra de espaço aperta o botão em que o foco parou, em vez de \"está certo e avança\". A tecla Tab nunca chega ao \"próximo aviso\": só anda pelos botões.", ""),
    ("13/10/2026", "O corte do livro novo deixa uma faixa preta larga no Cursus 3 (no corte de antes não sobrava). O aviso \"Faixa escura na beirada\" está certo.", "img/cursus-3-1-pagina-recorte.jpg"),
    ("13/10/2026", "Antiphon 260: a iluminura sai chapada em preto e branco e nenhum aviso fala disso; o aviso da faixa aparece na primeira visita e some quando vira aviso do livro.", "img/antiphon-260-1-pagina-recorte.jpg"),
    ("13/10/2026", "Palatino 66: a força do preto sozinha escurece uma página de caligrafia que estava boa e suja a moldura.", "img/palatino-66-1-pagina-recorte.jpg"),
    ("13/10/2026", "Pequenos: no Egenloff 3 o aviso \"Texto falhado\" oferece \"usar mais escuro\" com a força já no mais escuro que o botão põe; em 1280 x 657 o nome do filtro fica escrito por cima da miniatura dos cartões; a caixinha da força sozinha só aparece rolando a lista de opções.", "img/esta-bom-1-um-motivo-recorte.jpg"),
]

NAO_CONFERI = [
    "Janela maximizada: só uma tela (Antiphonal 46), com a janela fora da tela no tamanho que teria maximizada (1920 x 1020). Os cliques e todo o resto foram em 1280 x 657.",
    "Botão escondido com o foco do teclado, com a janela ativa: a minha janela de teste nunca fica ativa (não posso tomar o teclado do Samuel). Nela, depois de \"Tirar do livro\", o botão escondido ficou com o foco e engoliu uma barra de espaço sem fazer nada. Não sei dizer se na janela ativa o foco sai do botão.",
    "Projeto de antes de 09/10 (ordem antiga do preparo): só existe na pasta de dados de verdade do Samuel, que eu não uso.",
    "O custo novo na velocidade: o teste de velocidade não liga o \"Só as letras\". Os tempos da medida que anotei são os da janela, sem comparação com o programa de hoje.",
    "A roda do mouse (não funciona sem a janela em foco).",
    "O Opus Majus inteiro e o Graduale inteiro: usei a página do gabarito e um pedaço de 7 páginas.",
    "A suíte inteira e o teste_botoes.py: a gerente rodou no GitHub.",
]


def tabela(vel):
    linhas = [
        ("1. Regra ajustada (quando a página vai para a lista)", "janela + máquina",
         "Funciona, com ressalva grave: na janela 24 vão e 73 certas nas 89 páginas (implementador: 22 e 75)."),
        ("2. \"Parece em branco\" e \"Página sem conteúdo\" separados, dois botões cada", "janela", "Funciona. Falta \"está bom assim\" nesses dois avisos."),
        ("3. \"Trazer de volta nesta página\", com o lugar marcado em laranja", "janela + olho", "Funciona. A tela mostra a letra que o PDF apaga."),
        ("4. Força do preto sozinha, com \"Desfazer\" e caixinha", "janela", "Funciona. No Palatino 66 escureceu sem precisar."),
        ("5. Janela \"Antes de processar\" com \"ver\" e \"continuar assim mesmo\"", "janela", "Funciona. A lista fica longa e mistura avisos."),
        ("6. \"Está bom\" em cada nível, com Ctrl+Z; o aviso some quando se resolve", "janela", "Funciona nos quatro níveis e na lista grande."),
        ("Processar até \"Ficou pronto!\" (3 vezes)", "janela + máquina", "6 páginas no PDF nas três; 5 s, 2 s e 6 s; erros.log vazio."),
        ("As quatro páginas que o implementador não olhou", "olho, na janela", "Cursus 3: aviso certo (o corte deixa faixa). Opus Majus 20: não foi. Palatino 66: foi sem precisar. Antiphon 260: escapa."),
        ("Lista com poucas páginas visitadas (ressalva 2)", "janela", "Confirmado: 2 visitadas, 2 avisos; mais 4 visitadas, 4 avisos."),
        ("Projeto feito antes da mudança", "janela", "Abre, o aviso antigo some, a força sozinha vem desligada."),
        ("Botões escondidos acionados pelo teclado", "janela", "Não achei atalho; o Tab não chega a botão escondido. Não conferi com a janela ativa."),
    ]
    if vel:
        piores = [c for c in vel["comparacao"] if c["veredito"] == "mais lento"]
        linhas.append(("Velocidade (Marial de 300 folhas, 2 rodadas de cada, alternadas)", "máquina",
                       ("Mais lento em: " + "; ".join(c["medida"] for c in piores)) if piores
                       else "Não dá para dizer que ficou mais lento: as diferenças são menores que o vai-e-vem entre rodadas iguais. O teste não liga o \"Só as letras\"."))
    else:
        linhas.append(("Velocidade", "máquina", "As rodadas não terminaram."))
    return [{"o_que": a, "como": b, "resultado": c} for a, b, c in linhas]


def markdown(dados, vel):
    m = [TITULO, "",
         f"Verificador. Ramo `fase2-para-revisar`, commit `{COMMIT}`, em livro novo (endireitar antes de cortar). "
         "Pilotei a janela de verdade com mouse e teclado nativos, em 1280 x 657, com pasta de dados de teste. "
         "**Não mudei código e não marco nada como aprovado.**", "",
         "## Veredito", "", f"**{VEREDITO}**", "",
         "## O que mudou para o Kaique", ""]
    m += [p + "\n" for p in RESUMO_PARAGRAFOS]
    m += ["## O que está bom e as ressalvas", ""] + [f"- {i}" for i in ITENS] + [""]
    m += ["## O que foi conferido", "", "| O que | Como | Resultado |", "|---|---|---|"]
    m += [f"| {t['o_que']} | {t['como']} | {t['resultado']} |" for t in dados["resumo"]["tabela"]] + [""]
    m += ["## Quadro por quadro", ""]
    for q in QUADROS:
        m += [f"### {q['nome']} ({q['selo']})", "", f"**O que olhar:** {q['olhar']}", "", q["texto"], ""]
        if q.get("ressalva"):
            m += [f"**Ressalva:** {q['ressalva']}", ""]
        for i in q["imgs"]:
            m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}*", ""]
    p = PERGUNTA_MEDIR
    m += ["## A pergunta para o Samuel: quando medir as páginas não visitadas", ""] + [e + "\n" for e in p["explicacao"]]
    for o in p["opcoes"]:
        m += [f"- **{o['nome']}**{' (sugestão do verificador)' if o.get('sugestao_do_verificador') else ''}. {o['texto']}"]
    m += ["", p["sugestao"], "", f"![As duas listas]({p['opcoes'][0]['imgs'][0]['src']})", ""]
    m += [EXTRA_MD, "", "## Velocidade", ""]
    if vel:
        m += [f"Marial de 300 folhas, o programa de hoje (`fase-1`, {COMMIT_ANTES}) contra o ramo ({COMMIT}), alternando, 2 rodadas de cada. "
              "Cada número é o valor do meio das 3 repetições da rodada. **O teste não liga o \"Só as letras\": ele confere que o resto do programa não ficou mais lento; "
              "o custo novo (medir a página visitada) não entra nele.**", "",
              "| Rodada | Hora | Memória livre | Processador | Outros Python | Abrir | Trocar (média) | Trocar (pior) | Mágico pro, 10 pág. | Preto e branco, 10 pág. | Memória máxima | Durou |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in vel["rodadas"]:
            m.append(f"| {r['rodada']} ({r['commit']}) | {r['hora']} | {n(r['memoria_livre_gb'], 2)} GB | {r['processador_pct']}% | {r['outros_pythons']} | "
                     f"{n(r['abrir_total_s'])} s | {n(r['troca_media_s'], 2)} s | {n(r['troca_pior_s'], 2)} s | {n(r['processar_magico_pro_s'])} s | "
                     f"{n(r['processar_preto_e_branco_s'])} s | {r['pico_mb']} MB | {n(r['minutos'])} min |")
        m += ["", "| Medida | Antes | Depois | Diferença | Vai-e-vem do antes | Vai-e-vem do depois | Par a par (depois menos antes) | Dá para dizer? |", "|---|---|---|---|---|---|---|---|"]
        for c in vel["comparacao"]:
            k = c["casas"]
            m.append(f"| {c['medida']} | {n(c['antes'], k)} s | {n(c['depois'], k)} s | {c['diferenca']:+.{k}f} s ({c['pct']:+.1f}%) | "
                     f"{n(c['vai_e_vem_antes'], k)} s | {n(c['vai_e_vem_depois'], k)} s | {'; '.join(f'{p:+.{k}f}' for p in c['pares'])} s | {c['veredito']} |".replace(".", ","))
        m += [""]
    else:
        m += ["As rodadas não terminaram.", ""]
    m += [TEMPOS_MD, ""] if TEMPOS_MD else ["Tempos da medida na janela (do clique na página até a medida chegar, já descontada a espera do meu roteiro): Camões 4 a 5 s; Gladstone 4 a 6 s; "
          "Antiphonal 6 a 7 s; Egenloff e Palatino 7 a 10 s; Rariora 11 s; Antiphon 20 a 26 s.", ""]
    m += ["## O que não consegui conferir", ""] + [f"- {x}" for x in NAO_CONFERI] + [""]
    m += ["## Bugs para a Lista de bugs", "", "| Data | Bug | Print |", "|---|---|---|"]
    m += [f"| {d} | {b} | {('`' + i + '`') if i else '(sem print: está na saída dos roteiros p32 e p33)'} |" for d, b, i in BUGS]
    m += ["", "## Como foi feito", "",
          "- Janela de verdade do ramo, aberta fora da tela, com cliques, arrastos e teclas nativos do Windows (`scripts/piloto.py`, `scripts/v.py`); as leituras do estado só leem. Ida às páginas: arrastando a barra da tira de miniaturas e clicando na miniatura.",
          "- Pasta de dados de teste em `trabalho/dados_teste` (fora do git). A pasta de dados do Samuel não foi usada. O `erros.log` de teste ficou vazio em todas as sessões.",
          "- Livros inteiros abertos como livro novo: Antiphonal 1547 (298 folhas), Egenloff (138), Camões (106), Gladstone (146), Rariora (414), Palatino (134), Cursus (402), Antiphon (305). Pedaços: Antiphonal 44 a 49 (para processar até o fim), Graduale 219 a 225, Egenloff 1 a 14 (projeto antigo). Opus Majus 20: a página do gabarito.",
          "- Máquina: `scripts/desenhar.py` e `scripts/ver_pdf.py` (a página na tela contra a do PDF), `scripts/ordem_da_medida.py` e `scripts/conferir_89_como_a_janela.py` (as 89 páginas na ordem da janela; resultado em `conferir-89-como-a-janela.json`), `velocidade/` (as quatro rodadas).",
          "- Imagens: 58 em `img/`. Abri 41 uma a uma; as outras 17 são a tela inteira ou o recorte da mesma captura de uma que abri. Sete prints tinham saído com a imagem velha da janela (o primeiro print depois de abrir o programa); achei por máquina (`scripts/achar_prints_velhos.py`), refiz os que entram aqui e nenhum velho ficou em `img/`.",
          *EXTRA_COMO,
          f"- Tudo no commit `{COMMIT}` do programa. {NOTA_COMMIT}", ""]
    return "\n".join(m)


def main():
    vel = velocidade()
    dados = {
        "conferencia": "para-revisar-2026-10-13", "ramo": "fase2-para-revisar", "commit": COMMIT,
        "resumo": {"paragrafos": RESUMO_PARAGRAFOS, "veredito": VEREDITO, "itens": ITENS, "tabela": tabela(vel)},
        "quadros": QUADROS,
        "pergunta_medir": PERGUNTA_MEDIR,
        "velocidade": vel,
        "nao_conferi": NAO_CONFERI,
        "bugs": [{"data": d, "bug": b, "print": i} for d, b, i in BUGS],
        "as_89_paginas": AS_89 or {"combinado_com_o_samuel": [21, 78], "implementador_direto_a_300": [22, 75],
                          "na_ordem_da_janela": [24, 73],
                          "mudam_de_decisao": ["graduale_p221 (passa a ir)", "matematica_p072 (passa a ir)",
                                               "palatino_p113 (passa a ir)", "opusmajus_p020 (deixa de ir)"]},
    }
    dados.update(EXTRA_JSON)
    (BASE / "conferencia.json").write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    import relatorio
    print(relatorio.gravar(markdown(dados, vel), BASE / "conferencia.md"))
    print("quadros:", len(QUADROS), "| imagens citadas:", sum(len(q["imgs"]) for q in QUADROS) + 2, "| velocidade:", bool(vel))


if __name__ == "__main__":
    main()
