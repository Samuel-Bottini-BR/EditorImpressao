"""SEGUNDA CONFERENCIA do "Para revisar" (ramo em ce2b835): atualiza a entrega.

Parte do conteudo da primeira (montar_conferencia.py) e troca o que mudou:
veredito, itens, quadros (mesmos id), as tres perguntas, a velocidade
(rodadas-2 e o folhear na janela), os bugs que sobraram. Grava o
conferencia.json e o relatorio nos tres formatos. Nao mede nada.
"""
import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import montar_conferencia as M  # noqa: E402

BASE, img, n = M.BASE, M.img, M.n
extra = json.loads((BASE / "trabalho" / "segunda-extra.json").read_text(encoding="utf-8")) \
    if (BASE / "trabalho" / "segunda-extra.json").exists() else {}

M.COMMIT, M.COMMIT_ANTES, M.RODADAS = "ce2b835", "94f71bd", "rodadas-2"
M.TITULO = "# Segunda conferência do \"Para revisar\" (Fase 2), 13/10/2026"
M.NOTA_COMMIT = "A primeira conferência (commit `2d820d6` deste ramo) foi em `36b9e32`."

M.RESUMO_PARAGRAFOS = [
    M.RESUMO_PARAGRAFOS[0],
    "Quando o texto sai muito falhado (4 linhas ou mais), o programa escurece sozinho a força do preto só naquela página e avisa; dá para desfazer, "
    "e há uma caixinha para desligar na tela \"O que fazer\". Ao clicar em \"Confirmar e processar\" com avisos sem olhar, aparece a lista "
    "\"Página N - motivo\", com \"ver\" e \"continuar assim mesmo\".",
    "O Kaique pode dizer \"está bom\" numa página, num motivo de uma página, num motivo em todas ou em tudo, e o Ctrl+Z desfaz. "
    "Novo desta rodada: os avisos de página em branco ganharam o botão \"está bom assim\", e na aba Marcar as áreas que o programa achou "
    "se acertam sozinhas uns 10 segundos depois de chegar numa página nova.",
]

M.VEREDITO = ("PRONTO PARA CONFERIR: os consertos valem na janela de verdade e a regra voltou a decidir igual nos dois caminhos (22 vão, 75 certas); "
              "sobram três coisas que são escolha do Samuel (a tela que mostra a letra que o PDF apaga, a lista só com as páginas visitadas e as contagens que não batem) "
              "e um custo novo: depois de folhear 12 páginas o programa trabalha por trás uns 45 segundos, contra 9 antes.")

M.ITENS = [
    "BOM: Graduale 221 não recebe mais o aviso errado, e as 89 páginas dão 22 vão e 75 certas tanto direto quanto na ordem da janela (antes: 24 e 73 na janela).",
    "BOM: dois cliques no cartão do filtro abrem o \"Ver de perto\" e não mexem em nada; o aviso continua.",
    "BOM: \"Parece em branco\" e \"Página sem conteúdo\" têm agora o terceiro botão, \"está bom assim\" (Gladstone 18, Egenloff 12, Rariora 8).",
    "BOM: os botões do aviso não ficam mais com o teclado; depois do clique a barra de espaço faz \"está certo e avança\".",
    "BOM: a frase da lista diz \"75 páginas (104 avisos na lista)\"; \"usar mais escuro\" some quando a força já está em 85.",
    "BOM: a força do preto sozinha ficou cautelosa: age no Camões 27 e no 104; no Palatino 66, no Egenloff 3 e no Camões 11 fica só o aviso \"Texto falhado\".",
    "BOM: na aba Marcar, a área marcada à mão enquanto o programa ainda procurava continuou lá depois do acerto.",
    "BOM: processar até \"Ficou pronto!\" e abrir um projeto da primeira conferência continuam funcionando no programa novo." if extra.get("processar_ok") else
    "NÃO CONFERIDO de novo: processar até \"Ficou pronto!\" no programa novo.",
    "RESSALVA: depois de folhear 12 páginas com \"Só as letras\", o programa continua trabalhando por trás de 44 a 47 segundos; no programa de hoje, de 8 a 9. A troca de página em si não ficou mais lenta.",
    "RESSALVA: a tela continua mostrando a letra T que o PDF apaga (Antiphonal 46). Virou pergunta para o Samuel.",
    "RESSALVA: a lista \"Antes de processar\" continua só com as páginas visitadas. Pergunta para o Samuel.",
    "RESSALVA: painel, lista e janela de salvar contam coisas diferentes (Camões: 39, 75 e 106). Pergunta para o Samuel.",
    "RESSALVA: a seta do teclado não troca de página na minha janela de teste, nem no ramo nem no programa de hoje (ela fica na tira ou no medidor da força). Não dá para dizer que o conserto do teclado vale para a seta.",
    "RESSALVA: continuam como estavam, sem ser deste conserto: o \"Parece em branco\" errado da Gladstone 18, a faixa preta do Cursus 3 (é do corte), a iluminura do Antiphon 260 sem aviso e as linhas pretas do Camões 66.",
]

por_id = {q["id"]: q for q in M.QUADROS}


def muda(qid, **campos):
    por_id[qid].update(campos)


muda("pr-tela-engana", ressalva="Não foi mexido nesta rodada, de propósito: é a pergunta \"A tela igual ao PDF\", mais abaixo. Conferi de novo no programa novo: o \"Ver de perto\" continua mostrando a letra T.",
     imgs=por_id["pr-tela-engana"]["imgs"] + [img("duplo-clique-2-ver-de-perto", "No programa novo (segunda conferência): o \"Ver de perto\" da mesma página continua com a letra T")])
muda("pr-sem-conteudo",
     olhar="Os três botões: \"Deixar em branco\", \"Tirar do livro\" e, novo, \"está bom assim\".",
     texto="\"Deixar em branco\" põe uma folha branca no lugar (o livro continua com o mesmo número de páginas). \"Tirar do livro\" apaga a página. \"está bom assim\" tira só esse aviso da lista e deixa a página como está. Os três voltam com Ctrl+Z.",
     ressalva="",
     imgs=[img("sem-conteudo-1-egenloff-recorte", "Egenloff 12: o aviso e os três botões (ampliado)"),
           img("sem-conteudo-2-egenloff-tela", "A tela inteira"),
           img("sem-conteudo-3-deixar-em-branco-recorte", "Depois de \"Deixar em branco\": folha branca no lugar e botão \"voltar a página\" (print da primeira conferência)"),
           img("sem-conteudo-4-tirar-do-livro-recorte", "Depois de \"Tirar do livro\": a página 12 fica apagada na tira (print da primeira conferência)"),
           img("sem-conteudo-5-rariora-recorte", "Rariora 8: o mesmo aviso, com os três botões")])
muda("pr-parece-em-branco", tipo="misto", selo="erro conhecido, com saída",
     texto="O erro da Gladstone 18 continua (já está na Lista de bugs e não era deste trabalho): a página tem título e o programa diz que parece em branco. O que mudou: agora o aviso tem o botão \"está bom assim\", que deixa a página como está.",
     ressalva="O aviso errado continua vindo com \"Tirar do livro\" ao lado. Com o terceiro botão há saída certa; o conserto do aviso em si fica para a Lista de bugs.",
     imgs=[img("parece-em-branco-1-recorte", "Gladstone 18: \"Parece em branco\", agora com \"está bom assim\" (ampliado)"),
           img("parece-em-branco-2-tela", "A tela inteira"),
           img("parece-em-branco-3-a-pagina", "A página de perto: tem o título \"DA ORAÇÃO\"")])
muda("pr-forca-sozinha", nome="Camões 27, Egenloff 3 e Palatino 66: a força do preto sozinha, mais cautelosa",
     texto="A força só muda sozinha quando 4 linhas ou mais saem falhadas. No Camões 27 e no 104 ela vai de 50 para 85 e avisa, com \"Desfazer\". No Egenloff 3, no Palatino 66 e no Camões 11 ela não mexe mais: fica só o aviso \"Texto falhado\", com o botão \"usar mais escuro\". Com a força já em 85, esse botão não aparece.",
     ressalva="A caixinha só aparece depois de rolar a lista de opções para baixo. No Egenloff 3, com a força em 85, a frase do aviso ainda diz \"tente a força do preto mais escura\".",
     imgs=[img("forca-1-camoes-recorte", "Camões 27: o aviso, o medidor em \"bem forte\" e o \"Desfazer\" (ampliado)"),
           img("forca-2-camoes-tela", "A tela inteira"),
           img("forca-3-desfazer-recorte", "Depois do \"Desfazer\": força normal e o aviso \"Texto falhado\" (print da primeira conferência)"),
           img("forca-4-egenloff-3-recorte", "Egenloff 3 agora: só o aviso \"Texto falhado\", força normal"),
           img("forca-7-egenloff-3-forca-85-recorte", "Egenloff 3 depois de \"usar mais escuro\": o botão sumiu, fica \"está bom assim\""),
           img("forca-5-caixinha-recorte", "A caixinha \"Escurecer sozinho a força do preto quando o texto sair falhado\""),
           img("forca-6-caixinha-tela", "A tela \"O que fazer\" inteira")])
muda("pr-antes-de-processar", selo="funciona, contagens em pergunta",
     texto="\"ver\" leva à página e não processa. \"continuar assim mesmo\" segue para escolher a pasta e processa até \"Ficou pronto!\". Fechar no X não processa. A frase de cima agora diz quantas páginas e quantos avisos: \"75 páginas (104 avisos na lista)\".",
     ressalva="A lista continua juntando os avisos novos com os de sempre (Camões: 104 linhas, 4 da regra nova). E os três números continuam diferentes: é a pergunta \"As contagens\", mais abaixo.",
     imgs=[img("antes-3-lista-camoes", "Camões: a frase nova, \"75 páginas (104 avisos na lista)\""),
           img("antes-2-depois-do-ver-tela", "Depois de \"ver\": o programa foi para a página do aviso e não processou"),
           img("antes-4-confirmar", "Depois de \"continuar assim mesmo\": a janela de salvar"),
           img("antes-5-ficou-pronto-tela", "\"Ficou pronto!\"")])
muda("pr-janela-diferente", nome="Graduale 221: a janela voltou a decidir igual à conferência das 89", tipo="melhor", selo="consertado",
     olhar="Não há mais aviso nem marca laranja nesta página.",
     texto="Na primeira conferência a janela dava \"Desenho apagado\" aqui, e medindo direto não dava. Agora a medida usa sempre as áreas achadas na página do tamanho do PDF. Na janela a página ficou sem aviso, e as 89 páginas dão o mesmo resultado nos dois caminhos.",
     ressalva="O resultado é 22 vão e 75 certas, não os 21 e 78 combinados com o Samuel: 5 páginas ainda decidem diferente do estudo no livro novo (Antiphon 260, Cursus 3, Matemática 72, Opus Majus 20, Palatino 66). Isso já estava escrito pelo implementador.",
     imgs=[img("janela-diferente-1-graduale-221-recorte", "Graduale 221 na janela, depois do conserto: sem aviso (ampliado)"),
           img("janela-diferente-2-graduale-221-tela", "A tela inteira (página 3 do pedaço de 7 páginas)")])
muda("pr-cursus-3", ressalva="É defeito do corte do livro novo, não do aviso. O conserto do corte está sendo conferido em outro ramo; não reabri esta página na segunda conferência.")
muda("pr-opus-20", nome="Opus Majus 20: pela conta, agora vai para a lista", tipo="misto", selo="vai sem precisar",
     texto="Na primeira conferência a janela não mandava esta página. Com o conserto, a janela passou a decidir igual à conta direta, e por ela a página vai, por \"figura além da gravura\". A foto sai intacta: a página não precisava ir.",
     ressalva="Não reabri esta página na janela na segunda conferência: o que digo vem da conta das 89 páginas na ordem da janela. É uma das 5 que decidem diferente do estudo.",
     imgs=[img("opus-majus-20-1-pagina-recorte", "A página como sai, de perto: a foto ficou intacta (print da primeira conferência)")])
muda("pr-palatino-66", nome="Palatino 66: a força não mexe mais; fica o aviso", tipo="melhor", selo="melhorou",
     olhar="O medidor da força do preto em \"normal\" e o aviso \"Texto falhado\" com \"usar mais escuro\".",
     texto="Antes o programa escurecia a força sozinho e sujava a moldura desta página de caligrafia. Agora não mexe: mostra o aviso \"Texto falhado\" e deixa a escolha para a pessoa.",
     ressalva="A página continua indo para a lista sem precisar (é uma das 5 que decidem diferente do estudo), mas agora sem estragar nada.",
     imgs=[img("palatino-66-2-aviso-recorte", "Palatino 66 agora: força normal e o aviso \"Texto falhado\" (ampliado)"),
           img("palatino-66-3-tela", "A tela inteira"),
           img("palatino-66-1-pagina-recorte", "Como saía antes do conserto, com a força escurecida (print da primeira conferência)")])
muda("pr-antiphon-260", ressalva=por_id["pr-antiphon-260"]["ressalva"] + " Não mudou nesta rodada e não reabri a página.")
muda("pr-projeto-antigo",
     ressalva=("Na segunda conferência abri no programa novo um projeto gravado pelo programa da primeira (sem o campo novo da marcação): "
               + extra.get("antigo_frase", "não consegui conferir.") + " Projeto de antes de 09/10 continua sem conferir (só existe na pasta de dados do Samuel)."))

NOVOS = [
    {"id": "pr-marcar-sozinha", "nome": "Aba Marcar: as áreas se acertam sozinhas", "tipo": "misto", "selo": "novo, para saber",
     "olhar": "As áreas azuis (letra) e verdes (papel) mudam sozinhas uns 10 segundos depois de chegar na página.",
     "texto": "Ao chegar numa página nova, a aba Marcar mostra as áreas achadas na página pequena da tela: 9 no Graduale 221. O programa procura de novo, por trás, na página do tamanho do PDF, e troca: 18 áreas, 10,7 segundos depois de chegar. Só acontece uma vez por página. Marquei um retângulo à mão nesse intervalo, na página 5, e ele continuou lá depois da troca.",
     "ressalva": "Quem estiver olhando vê as áreas mudarem sem ter feito nada, e nada avisa que o programa ainda está procurando. Não testei apagar ou mexer numa área do programa nesse intervalo, só marcar uma nova.",
     "imgs": [img("marcar-1-antes-e-depois", "Graduale 221 na aba Marcar: ao chegar e 10,7 segundos depois"),
              img("marcar-2-antes-tela", "A tela ao chegar: \"Marcado: 4 de letra e traço e 5 de papel\""),
              img("marcar-3-depois-tela", "A tela depois: \"Marcado: 7 de letra e traço e 11 de papel\""),
              img("marcar-4-a-mao-recorte", "Página 5: o retângulo que marquei à mão continuou depois do acerto (1 de gravura ou foto)")]},
    {"id": "pr-duplo-clique", "nome": "Dois cliques no cartão não tiram mais o aviso", "tipo": "melhor", "selo": "consertado",
     "olhar": "Depois dos dois cliques, o aviso e os botões laranja continuam na tela.",
     "texto": "Dei dois cliques no cartão do Preto e branco na página da letra T. Abriu o \"Ver de perto\", nada foi gravado no histórico e o aviso continuou de pé.",
     "ressalva": "",
     "imgs": [img("duplo-clique-1-aviso-continua-recorte", "Depois dos dois cliques e de fechar o \"Ver de perto\": o aviso continua (ampliado)"),
              img("bug-duplo-clique-tira-o-aviso-tela", "A tela inteira")]},
    {"id": "pr-teclado", "nome": "O teclado depois de clicar num botão do aviso", "tipo": "misto", "selo": "espaço sim, seta não sei",
     "olhar": "Depois de \"Deixar em branco\" e da barra de espaço, o programa passou para a página 13.",
     "texto": "Os botões do aviso não ficam mais com o teclado. Depois de clicar em \"Deixar em branco\", a barra de espaço fez \"está certo e avança\" (antes ela apertava o botão). Com Tab, 40 vezes, o foco nunca parou num botão do aviso.",
     "ressalva": "A seta para a direita não trocou de página na minha janela de teste. Fiz o mesmo no programa de hoje e deu igual: a seta fica na tira de miniaturas ou no medidor da força, que é quem está com o teclado. Não é deste conserto, mas não posso dizer que a seta funciona. A minha janela de teste nunca fica ativa (não tomo o teclado do Samuel).",
     "imgs": [img("teclado-1-recorte", "Depois de \"Deixar em branco\" na página 12 e da barra de espaço: página 13 (ampliado)"),
              img("teclado-2-tela", "A tela inteira")]},
]
M.QUADROS = M.QUADROS + NOVOS

# ------------------------------------------------------------------ as tres perguntas
M.PERGUNTA_MEDIR["explicacao"] = [
    "O que você está escolhendo: em que hora o programa confere as páginas que ninguém abriu. Hoje ele só confere a página que está na tela. "
    "As outras só são conferidas na hora de gerar o PDF, quando já não dá para parar.",
    "Por isso a lista \"Antes de processar\" só mostra as páginas que você visitou. No Antiphonal de 298 páginas, com 2 visitadas, a lista mostrou 2 avisos de desenho apagado; "
    "visitei mais 4 e ela passou a mostrar 4. E a força do preto sozinha pode escurecer uma página que ninguém viu.",
    "Conferir uma página custa tempo: na janela, de 4 a 15 segundos nos livros comuns e de 20 a 26 no Antiphon, de folha grande. "
    "O implementador mediu, sem a tela, de 13 a 15 minutos para um livro de 300 páginas.",
]
M.PERGUNTA_MEDIR["opcoes"][0]["imgs"] = [img("medir-1-listas", "Hoje: a lista cresce conforme as páginas são visitadas (print da primeira conferência; a frase de cima hoje traz também \"(M avisos na lista)\")")]
M.PERGUNTA_MEDIR["opcoes"][1]["imgs"] = [img("antes-3-lista-camoes", "A lista \"Antes de processar\": é ela que ficaria completa, depois da espera")]
M.PERGUNTA_MEDIR["opcoes"][2]["imgs"] = [img("medir-2-lista-inteira", "A lista de hoje no Antiphonal, com 2 páginas visitadas de 298 (print da primeira conferência)")]

PERGUNTA_CONTAGENS = {
    "id": "pr-contagens",
    "titulo": "Os três números de páginas e avisos não batem. Qual deve valer?",
    "explicacao": [
        "O que você está escolhendo: o que cada número da tela conta. Hoje são três contas diferentes, e elas aparecem uma atrás da outra.",
        "No Camões (106 páginas): o painel \"Para revisar\" diz 39, porque conta só os avisos de página. A lista \"Antes de processar\" diz 75 páginas e 104 avisos, "
        "porque junta os avisos de página com os de folha (qualidade baixa, tamanho diferente). E a janela de salvar diz 106, porque conta toda página em que ninguém clicou \"está certo\".",
        "Quem dá \"continuar assim mesmo\" para 75 páginas lê, na janela seguinte, que ainda há 106 sem conferir.",
    ],
    "opcoes": [
        {"id": "painel-com-folhas", "nome": "O painel passa a listar também os motivos de folha",
         "texto": "Bom: o painel e a lista mostram os mesmos avisos (no Camões, 104 nos dois). Ruim: o painel fica comprido, e a janela de salvar continua dizendo 106.",
         "imgs": [img("contagens-2-painel-tela", "O painel de hoje (39): só os avisos de página")]},
        {"id": "salvar-conta-pendentes", "nome": "A janela de salvar passa a contar as páginas com aviso pendente",
         "texto": "Bom: o número da janela de salvar fica igual ao da lista que acabou de aparecer (no Camões, 75), e some quando todos os avisos foram vistos. Ruim: ela deixa de lembrar as páginas sem \"está certo\" que não têm aviso nenhum.",
         "sugestao_do_verificador": True,
         "imgs": [img("contagens-3-salvar", "A janela de salvar de hoje: 106 páginas")]},
        {"id": "deixar-como-esta", "nome": "Deixar como está",
         "texto": "Bom: não muda nada. Ruim: três números diferentes em três telas seguidas.",
         "imgs": [img("contagens-1-lado-a-lado", "Os três números no Camões: 39, 75 (104 avisos) e 106")]},
        {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito, com mais exemplos.", "imgs": []},
    ],
    "sugestao": "Sugestão do verificador (é minha, não é decisão): a janela de salvar contar as páginas com aviso pendente. É o número que aparece por último, logo antes de processar, "
                "e hoje é o que mais desmente a lista. Se couber, a primeira opção junto.",
}

PERGUNTA_TELA = {
    "id": "pr-tela-igual-ao-pdf",
    "titulo": "A tela deve mostrar a página igual à do PDF?",
    "explicacao": [
        "O que você está escolhendo: se a página que aparece na tela, no \"Só as letras\", passa a ser a mesma que vai para o PDF.",
        "Hoje a tela usa uma imagem menor, para ser rápida. No Antiphonal 46 essa imagem mostra a letra T grande; no PDF a letra some. "
        "O aviso \"Desenho apagado\" está certo, mas quem olha a tela vê a letra no lugar.",
        "O programa já desenha por trás a página do tamanho do PDF, para medir os avisos. Ela chega de 4 a 15 segundos depois de abrir a página (20 a 26 em folha grande). "
        "Dá para aproveitar essa imagem na tela quase sem custo.",
    ],
    "opcoes": [
        {"id": "trocar-sozinha", "nome": "A tela troca sozinha pela imagem do PDF quando ela chegar",
         "texto": "Bom: o que se vê é o que sai, sem precisar pedir. Ruim: a página muda sozinha na tela alguns segundos depois de aparecer, e nesse meio tempo ainda mostra a imagem menor.",
         "sugestao_do_verificador": True,
         "imgs": [img("tela-engana-1-comparacao", "A mesma página 46: a tela (com a letra T) e o PDF que saiu (sem ela)")]},
        {"id": "botao-ver-como-sai", "nome": "Um botão \"ver como sai no PDF\"",
         "texto": "Bom: nada muda sozinho; quem quiser conferir aperta o botão. Ruim: quem não apertar continua vendo a letra que não vai sair.",
         "imgs": [img("tela-engana-2-ver-de-perto-tela", "O \"Ver de perto\" de hoje, com o aviso de pé: a letra T aparece")]},
        {"id": "deixar-como-esta", "nome": "Deixar como está",
         "texto": "Bom: a tela continua rápida e igual. Ruim: só o aviso diz a verdade; pelo olho a página parece certa.",
         "imgs": [img("letra-t-0-marca-recorte", "Hoje: a marca laranja em volta de uma letra que, na tela, está lá")]},
        {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito, com mais exemplos.", "imgs": []},
    ],
    "sugestao": "Sugestão do verificador (é minha, não é decisão): trocar sozinha quando chegar. Aviso que manda olhar uma coisa que a tela não mostra não ajuda o Kaique; "
                "e a troca só vale no \"Só as letras\", onde a imagem do PDF já é desenhada de qualquer jeito.",
}


def md_pergunta(p):
    m = [f"## Pergunta para o Samuel: {p['titulo']}", ""] + [e + "\n" for e in p["explicacao"]]
    for o in p["opcoes"]:
        m.append(f"- **{o['nome']}**{' (sugestão do verificador)' if o.get('sugestao_do_verificador') else ''}. {o['texto']}")
    m += ["", p["sugestao"], ""]
    for o in p["opcoes"]:
        for i in o["imgs"]:
            m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}*", ""]
    return m


# ------------------------------------------------------------------ folhear (o que o teste de velocidade nao mede)
def folhear():
    pasta = BASE / "trabalho" / "folhear"
    linhas = []
    for nome in ("antes-1", "depois-1", "antes-2", "depois-2"):
        d = json.loads((pasta / f"{nome}.json").read_text(encoding="utf-8"))
        linhas.append({"rodada": nome, "codigo": "programa de hoje (94f71bd)" if nome.startswith("antes") else "ramo (ce2b835)",
                       "parando_media": statistics.mean(d["parando_1_5s"]), "parando_meio": statistics.median(d["parando_1_5s"]),
                       "parando_pior": max(d["parando_1_5s"]), "sem_parar_media": statistics.mean(d["sem_parar"]),
                       "sem_parar_meio": statistics.median(d["sem_parar"]), "sem_parar_pior": max(d["sem_parar"]),
                       "por_tras_parando": d["resto_depois_de_parar_s"], "por_tras_sem_parar": d["resto_depois_sem_parar_s"]})
    return linhas


FOLHEAR = folhear()
md = []
for p in (PERGUNTA_CONTAGENS, PERGUNTA_TELA):
    md += md_pergunta(p)
md += ["## Folhear com \"Só as letras\" na janela (o que o teste de velocidade não mede)", "",
       "Antiphonal 1547 (298 folhas), livro novo, clicando no botão \">\" 12 vezes parando 1,5 s em cada página e mais 12 sem parar. "
       "Tempo até a página nova aparecer, e quanto o programa continua trabalhando por trás depois da última. A medida não enxerga menos que 0,05 s.", "",
       "| Rodada | Parando 1,5 s: média | do meio | pior | Sem parar: média | do meio | pior | Por trás depois (parando) | Por trás depois (sem parar) |",
       "|---|---|---|---|---|---|---|---|---|"]
for l in FOLHEAR:
    md.append(f"| {l['rodada']}, {l['codigo']} | {n(l['parando_media'], 2)} s | {n(l['parando_meio'], 2)} s | {n(l['parando_pior'], 2)} s | "
              f"{n(l['sem_parar_media'], 2)} s | {n(l['sem_parar_meio'], 2)} s | {n(l['sem_parar_pior'], 2)} s | **{n(l['por_tras_parando'])} s** | **{n(l['por_tras_sem_parar'])} s** |")
md += ["", "**Trocar de página não ficou mais lento** (o ramo saiu igual ou um pouco melhor nas duas rodadas). "
       "**O trabalho por trás depois de parar passou de 8 a 9 segundos para 44 a 47.** A tela não trava nesse tempo, mas o processador fica ocupado. "
       "O implementador mediu uns 22 s contra 3 a 5 s, com o filtro de fábrica; com \"Só as letras\" deu o dobro.", ""]
M.EXTRA_MD = "\n".join(md)
M.TEMPOS_MD = ("Tempos da medida na janela, na segunda conferência (do clique na página até a medida chegar): Camões 8 a 15 s; Egenloff 11 a 14 s; "
               "Antiphonal 8 s; páginas avulsas e pedaços pequenos 2 s. Na primeira: de 4 a 11 s nos livros comuns e de 20 a 26 s no Antiphon.")
M.AS_89 = {"combinado_com_o_samuel": [21, 78], "implementador_direto_a_300": [22, 75], "na_ordem_da_janela": [22, 75],
           "na_ordem_da_janela_na_primeira_conferencia": [24, 73], "mudam_de_decisao": []}
M.EXTRA_JSON = {"conferencia": "para-revisar-2026-10-13 (segunda conferência)", "primeira_conferencia_em": "36b9e32",
                "pergunta_contagens": PERGUNTA_CONTAGENS, "pergunta_tela_igual_ao_pdf": PERGUNTA_TELA, "folhear_na_janela": FOLHEAR,
                "os_8_pontos": extra.get("os_8_pontos")}
M.EXTRA_COMO = [
    "- **Segunda conferência:** ramo trazido com `git merge origin/fase2-para-revisar` (ce2b835). Pasta de dados nova (`trabalho/dados_teste2`), para todo livro ser livro novo. "
    "Roteiros `scripts/q1_consertos.py` (os pontos 1, 2, 3, 4, 6, 7 e 8), `q2_setas.py`, `q3_camoes_contagens.py` (pontos 5 e 7 e as contagens), `q4_folhear.py`, `q5_processar_e_antigo.py`.",
    "- O \"antes\" da velocidade e do folhear é a minha worktree `velocidade-antes-pr` (origin/fase-1, 94f71bd), porque a `velocidade-antes` estava em uso por outro verificador. "
    "O `fase-1` de hoje não tem código que o ramo não tenha: a diferença entre os dois é só este trabalho.",
]
M.BUGS = [
    ("13/10/2026", "(para o Samuel decidir) A tela mostra o que o PDF não tem no \"Só as letras\": Antiphonal 46, a letra T aparece na tela e some no PDF.", "img/tela-engana-1-comparacao.jpg"),
    ("13/10/2026", "(para o Samuel decidir) Painel, lista e janela de salvar contam coisas diferentes: Camões, 39, 75 (104 avisos) e 106.", "img/contagens-1-lado-a-lado.jpg"),
    ("13/10/2026", "(para o Samuel decidir) A lista \"Antes de processar\" só traz as páginas visitadas.", "img/medir-1-listas.jpg"),
    ("13/10/2026", "Depois de folhear 12 páginas com \"Só as letras\", o programa trabalha por trás de 44 a 47 s (programa de hoje: 8 a 9 s). Não trava a tela.", ""),
    ("13/10/2026", "Na aba Marcar as áreas mudam sozinhas uns 10 s depois de chegar na página (Graduale 221: 9 viram 18) e nada avisa que o programa ainda está procurando.", "img/marcar-1-antes-e-depois.jpg"),
    ("13/10/2026", "A seta do teclado não troca de página quando o teclado está na tira de miniaturas ou no medidor da força (visto na janela de teste, igual no programa de hoje e no ramo).", ""),
    ("13/10/2026", "Egenloff 3 com a força em 85: a frase do aviso \"Texto falhado\" ainda manda tentar a força mais escura (o botão já não aparece).", "img/forca-7-egenloff-3-forca-85-recorte.jpg"),
    ("13/10/2026", "Continuam, sem ser deste conserto: \"Parece em branco\" errado na Gladstone 18; faixa preta do corte no Cursus 3; iluminura do Antiphon 260 chapada e sem aviso; Camões 66 sem aviso das linhas pretas.", "img/parece-em-branco-1-recorte.jpg"),
]
M.NAO_CONFERI = [
    "Teclado com a janela ativa: a minha janela de teste fica fora da tela e nunca ativa, para não tomar o teclado do Samuel. Por isso não sei dizer se a seta troca de página no uso de verdade.",
    "Opus Majus 20, Antiphon 260, Cursus 3 e Camões 66: não reabri na segunda conferência (não eram dos consertos). O que digo do Opus Majus 20 vem da conta das 89 páginas.",
    "Aba Marcar: só testei marcar uma área nova à mão enquanto o programa procurava. Não testei apagar ou mudar uma área do programa nesse intervalo.",
    "A segunda metade da força sozinha (\"só fica se as falhas caírem\"): não achei página que a exercite na janela.",
    "Projeto de antes de 09/10: só existe na pasta de dados do Samuel.",
    "Janela maximizada: nada novo; continua só a tela do Antiphonal 46 da primeira conferência.",
    "A roda do mouse; a suíte inteira e o `teste_botoes.py` (não rodei).",
]
if extra.get("nao_conferi"):
    M.NAO_CONFERI = extra["nao_conferi"] + M.NAO_CONFERI


def tabela2(vel):
    p8 = [
        ("1. A medida não depende mais da prévia (Graduale 221; as 89 páginas)", "janela + máquina", "Vale. Graduale 221 sem aviso; 22 vão e 75 certas nos dois caminhos, nenhuma página diferente."),
        ("2. Dois cliques no cartão do filtro", "janela", "Vale. Abre o \"Ver de perto\", não grava ação, o aviso continua."),
        ("3. \"está bom assim\" em \"Parece em branco\" e \"Página sem conteúdo\"", "janela", "Vale nas três páginas (Gladstone 18, Egenloff 12, Rariora 8); Ctrl+Z desfaz."),
        ("4. Teclado depois do clique no botão do aviso", "janela (nunca ativa)", "Em parte. O botão não fica com o teclado e a barra de espaço funciona. A seta não troca de página na janela de teste, igual no programa de hoje."),
        ("5. Frase da janela \"Antes de processar\"", "janela", "Vale: \"75 páginas (104 avisos na lista)\". As três contagens continuam diferentes (pergunta)."),
        ("6. \"usar mais escuro\" com a força em 85", "janela", "Vale: o botão não aparece (Egenloff 3)."),
        ("7. Força do preto sozinha, mais cautelosa", "janela", "Vale. Camões 27 e 104: age. Palatino 66, Egenloff 3 e Camões 11: só o aviso."),
        ("8. Aba Marcar se acerta sozinha", "janela", "Acontece: Graduale 221, 9 áreas viram 18 em 10,7 s. A área marcada à mão no intervalo não se perdeu."),
        ("Processar até \"Ficou pronto!\" no programa novo", "janela", extra.get("processar_frase", "Não conferido de novo.")),
        ("Folhear com \"Só as letras\" (hoje contra o ramo)", "janela", "Trocar de página: igual ou melhor. Por trás depois de parar: 44 a 47 s contra 8 a 9 s."),
    ]
    if vel:
        piores = [c for c in vel["comparacao"] if c["veredito"] == "mais lento"]
        p8.append(("Velocidade (Marial de 300 folhas, 2 rodadas de cada, alternadas)", "máquina",
                   ("Mais lento em: " + "; ".join(c["medida"] for c in piores)) if piores
                   else "Não dá para dizer que ficou mais lento. O teste não liga o \"Só as letras\"."))
    else:
        p8.append(("Velocidade", "máquina", "As rodadas não terminaram."))
    return [{"o_que": a, "como": b, "resultado": c} for a, b, c in p8]


_vel = M.velocidade


def velocidade2():
    """Igual a da primeira, mas mostra o commit do PROGRAMA no braco "depois" (a worktree de
    conferencia esta em ba50856, que e o ce2b835 do ramo mais os arquivos desta conferencia)."""
    vel = _vel()
    if vel:
        for r in vel["rodadas"]:
            if r["rodada"].startswith("depois"):
                r["commit"] = "ce2b835"
    return vel


M.velocidade = velocidade2
M.tabela = tabela2
M.main()
d = json.loads((BASE / "conferencia.json").read_text(encoding="utf-8"))
citadas = set()
def cata(x):
    if isinstance(x, dict):
        if "src" in x:
            citadas.add(x["src"].split("/")[-1])
        for v_ in x.values():
            cata(v_)
    elif isinstance(x, list):
        for v_ in x:
            cata(v_)
cata(d)
sobra = sorted(p.name for p in (BASE / "img").glob("*.jpg") if p.name not in citadas)
print("quadros:", len(d["quadros"]), "| imagens citadas:", len(citadas), "| em img/ sem citar:", sobra)
