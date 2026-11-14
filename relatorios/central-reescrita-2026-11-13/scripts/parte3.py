"""Parte 3 da reescrita da Central (13/11/2026): as abas de auditoria 3, 4, 5 e 6.

As perguntas que esperam o Samuel (141) saem da "ficha" (Situação / Você pediu / O que isso quer dizer /
Solução / Parte do programa / Ressalva) para o formato do CLAUDE.md §11.13, curto:
  1. onde fica e o que é;
  2. o que ele pediu, com a data e as palavras (ou: escolha da gerente, sem perguntar a ele);
  3. como está hoje (e o que ainda falta, quando há ressalva);
  4. se ele já testou depois da auditoria (Livro de decisões: decisões mais novas que a substituem ou
     reforçam e que ele testou);
  5. o que ele escolhe.
O número da decisão vai só no fim, entre parênteses. As perguntas já respondidas ficam iguais.
Os ids das perguntas e das opções não mudam; as imagens são as que já existem.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import livro
from parte1 import gravar, ler

PASTA = Path(__file__).resolve().parent.parent
RESPOSTAS = PASTA / "dados" / "respostas"
ABAS = ["auditoria-3-com-ressalva", "auditoria-4-funciona", "auditoria-5-escolhas-da-gerente",
        "auditoria-6-para-depois"]
L, TEXTO_DO_LIVRO = livro.ler()

# ---------------------------------------------------------------------------------------------
# Já testado por ele depois da auditoria (29/10): achado no Livro (situação das decisões mais novas
# que citam esta). "sai" = pode sair da lista; "parte" = testado em parte (fica, com a frase).
# ---------------------------------------------------------------------------------------------
TESTADAS = {
    "D-486": ("sai", "Isto foi trocado por um pedido seu: em 29/10 você pediu que a página da direita mostre o "
                     "antes e depois com as opções escolhidas, e testou em 01/11: \"está funcionando\". Esta escolha "
                     "da gerente não vale mais."),
    "D-547": ("sai", "Você pediu de novo em 07/11 (\"o pdf do final tem que sair como a edição foi mostrada no "
                     "preview\"), foi consertado e você testou em 13/11: \"funcionando\"."),
    "D-004": ("sai", "Você já usou e testou este aviso: em 04/11, o aviso depois do \"juntar todas\" (\"7- ok\"); e "
                     "em 10/11, o \"Pular\" que deixa a página como você deixou (\"fiz os dois testes que você pediu "
                     "e estão funcionando\")."),
    "D-568": ("parte", "Você testou o zoom junto com a roda: em 01/11, Ctrl + roda (\"1- funcionando\"); em 02/11, "
                       "Shift + roda (\"shift funcionando\"). A roda sem Ctrl (trocar de página) não foi testada "
                       "sozinha."),
    "D-021": ("parte", "Você testou em 10/11 que as setas continuam passando de página depois de clicar num botão "
                       "do painel (\"sim\"). As setas fixas na tira e a barra mais alta ainda faltam."),
    "D-373": ("parte", "Você testou a ferramenta Dividir em 10/11 (\"ok\"), com esses nomes na lista; o nome em si "
                       "não foi perguntado de novo."),
    "D-090": ("parte", "Você testou o Dividir em 10/11 (\"ok\"). O \"usar em todas\" do Cortar não foi testado "
                       "sozinho depois da auditoria."),
    "D-487": ("parte", "O \"inserir página\", que faltava aqui, foi feito depois como \"adicionar página em branco\" "
                       "(botão direito na miniatura) e você testou em 09/11: \"pagina em branco funciona\". Os outros "
                       "botões da grade não foram testados depois da auditoria."),
    "D-168": ("parte", "Você testou em 29/10 uma caixinha que funciona do mesmo jeito (\"Respeitar as gravuras "
                       "achadas\" fica cinza com \"Só as letras\"): \"o programa está mudando de efeito como deveria\". "
                       "A caixinha das molduras não foi testada sozinha."),
    "D-007": ("parte", "Isto mudou em 02/11, a seu pedido, dentro da ferramenta Dividir (com \"Uma página\", a folha "
                       "dividida mostra só uma metade). Você testou o Dividir em 10/11 (\"ok\")."),
    "D-334": ("parte", "O \"inserir\" que faltava aqui foi feito depois como \"adicionar página em branco\" (botão "
                       "direito na miniatura) e você testou em 09/11: \"pagina em branco funciona\". Os botões da grade "
                       "não foram testados depois da auditoria."),
    "D-095": ("parte","O cantinho que o giro abre na beirada foi mexido em 06/11 e você testou em 10/11: \"a cor é "
                       "diferente da cor do papel\" (fica como está por enquanto). O resto desta lista não foi testado."),
}
NAO_TESTADA = "Você ainda não testou isto depois da auditoria de 29/10 (não há teste seu no Livro de decisões)."


# ---------------------------------------------------------------------------------------------
# limpeza das palavras de dentro (regra 2)
# ---------------------------------------------------------------------------------------------

def _data_da(num: str) -> str:
    d = L.get(num, {}).get("data", "")
    m = re.match(r"(\d{2}/\d{2})", d)
    return m.group(1) if m else ""


def limpar(t: str) -> str:
    if not t:
        return t
    t = t.replace("(paráfrase da fonte)", "(resumo, sem as suas palavras exatas)")
    t = re.sub(r"`[^`]*`", "", t)                                     # arquivos e funções
    t = re.sub(r"\s*\((?:escolha da gerente, )?D-0?14[^)]*\)", "", t)
    t = re.sub(r"\bpela regra D-014\b", "pela regra de escolher sozinha detalhe técnico", t)
    t = re.sub(r"\s*\((?:[^()]*?\b(?:etapa|junção|commit|ramo|prova)\b[^()]*)\)", "", t)
    t = re.sub(r",?\s*\bna etapa \d+[a-z]?(?:-\d+)?\b", "", t)
    t = re.sub(r"\b(?:da |na |a )?etapa \d+[a-z]?(?:-\d+)?(?: da obra)?\b", "a rodada de consertos", t)
    t = re.sub(r"\bda obra\b", "da rodada de consertos", t)
    t = re.sub(r"\ba obra\b", "a rodada de consertos", t)
    t = re.sub(r"\s*\((?:D-\d+(?:[,;/ e]+D-\d+)*)\)", "", t)            # (D-123) e (D-1, D-2)
    t = re.sub(r"\s*\(D-\d+[:;,][^)]*\)", "", t)                       # (D-123: ...)

    def troca(m):
        pre, num = m.group(1) or "", m.group(2)
        data = _data_da(num)
        nome = f"decisão de {data}" if data else "outra decisão"
        if pre.strip() in ("a", "na", "da", "pela", "à", "como a", "com a"):
            return f"{pre}{nome}"
        return f"{pre}a {nome}" if pre else f"a {nome}"
    t = re.sub(r"\b((?:como a|com a|na|da|pela|a|à) )?(D-\d+)\b", troca, t)
    t = re.sub(r"\b[a-z]{1,6}\d*(?:-[a-z0-9]+){1,6}: ", "", t)         # ids de pergunta ("rv5-erro-5-...: ")
    t = re.sub(r"\s*\((?:item )?\d\.\d{1,2}(?:\s*[/+e]\s*(?:caixa do )?\d\.\d{1,2})*\)", "", t)
    t = re.sub(r"\b(?:[Ii]tem )?\d\.\d{1,2}(?:/\d\.\d{1,2})*:\s*", "", t)
    t = re.sub(r",?\s*pergunta \d{3}(?:, opção [A-D])?", "", t)
    t = re.sub(r"(?:R\d+ )?\b\d{3} [A-D]\b(?:\s*/\s*\d{3} [A-D])?\s*(?:·\s*)?", "", t)
    t = re.sub(r"\bR\d+ \d{3}:\s*", "", t)
    t = re.sub(r",\s*[a-z]{1,6}\d(?:-[a-z0-9]+){1,6}\)", ")", t)
    t = re.sub(r"\s*\([a-z]{1,6}\d*(?:-[a-z0-9]+){1,6}\)", "", t)
    t = re.sub(r"\b[a-z]{1,6}\d+(?:-[a-z0-9]+){1,6}\b:?\s*", "", t)
    t = re.sub(r"\b(quadro|pergunta)\s+(?!A[3-5]\b)[A-Z]{1,2}\d{1,2}\b(?:\s+do plano)?", r"\1", t)
    t = re.sub(r",\s*(?!A[3-5]\b)[A-Z]{1,2}\d{1,2}(?:\s*a\s*[A-Z]\d{1,2})?\)", ")", t)
    t = re.sub(r"(?<![\w-])(?!A[3-5]\b)[A-Z]{1,2}\d{1,2}(?: \(comentário\))?(?:, \d{2}/\d{2})?:\s", "", t)
    t = re.sub(r",\s*(?!A[3-5]\b)[A-Z]{1,2}\d{1,2}:", ":", t)
    t = re.sub(r"\b(?!A[3-5]\b)[A-Z]\d{1,2} e [A-Z]\d{1,2}:", "os dois quadros:", t)
    t = re.sub(r"\s\((?!A[3-5]\))(?:R|M|G|F|P|N|O|S|C)\d{1,2}\)", "", t)
    t = re.sub(r"\b(?!A[3-5]\b)(?:G|P|O|N|S|C|F|M)\d{1,2}\s+(?=[\"“A-Za-zÀ-ú(])", "", t)
    t = re.sub(r"\bregra R\d+ do plano\b", "regra do plano", t)
    t = t.replace("depois da junção", "depois de juntar as frentes").replace("para a junção", "para quando juntar as frentes")
    t = t.replace("escolha da gerente", "a gerente escolheu sem perguntar a você")
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"(decisão de (\d{2}/\d{2})) \(\2\)", r"\1", t)
    t = re.sub(r"a decisão de (\d{2}/\d{2})/a decisão de \1", r"as decisões de \1", t)
    t = re.sub(r"a decisão de (\d{2}/\d{2})/a decisão de (\d{2}/\d{2})", r"as decisões de \1 e \2", t)
    t = re.sub(r"(\"|\b\d) a rodada de consertos", r"\1 da rodada de consertos", t)
    t = re.sub(r"\b[a-z]+-(?=\")", "", t)
    t = t.replace("out of path", "fora do caminho")
    t = re.sub(r"\((\d-\d{1,2})\)", r"(seu print \1)", t)
    t = re.sub(r"\b(pedido|bug) a rodada de consertos", r"\1 da rodada de consertos", t).replace("bug da rodada", "defeito da rodada")
    t = re.sub(r"\s{2,}", " ", t).replace(" ,", ",").replace(" .", ".").replace(" ;", ";").strip()
    return t


def campos(p: dict) -> dict:
    c = {"pediu_rotulo": "", "pediu": "", "sit": "", "quer": "", "sol": "", "parte": "", "ressalva": "",
         "junto": ""}
    for e in p["explicacao"]:
        m = re.match(r"^([^:]{2,60}):\s*(.*)$", e, re.S)
        if not m:
            continue
        rot, txt = m.group(1), m.group(2).strip()
        if rot.startswith("Você pediu") or rot.startswith("Escolha da gerente"):
            c["pediu_rotulo"], c["pediu"] = rot, txt
        elif rot.startswith("Situação"):
            c["sit"] = txt
        elif rot.startswith("O que isso quer dizer"):
            c["quer"] = txt
        elif rot.startswith("Solução"):
            c["sol"] = txt
        elif rot.startswith("Parte do programa"):
            c["parte"] = txt
        elif rot.startswith("Ressalva"):
            c["ressalva"] = txt
        elif rot.startswith("Resolvida junto"):
            c["junto"] = txt
    return c


def _ponto(t: str) -> str:
    t = t.strip()
    return t if not t or t[-1] in ".!?\"”)" else t + "."


def _maiuscula(t: str) -> str:
    return t[:1].upper() + t[1:] if t else t


ESCOLHAS = {
    "auditoria-3-com-ressalva": "O que você escolhe: se fica como está, se entra na lista de fazer (escreva no comentário o "
                                "que quer diferente) ou se você testa antes de responder.",
    "auditoria-4-funciona": "O que você escolhe: se fica como está, se entra na lista de fazer (escreva no comentário o que "
                            "quer diferente) ou se você testa antes de responder.",
    "auditoria-5-escolhas-da-gerente": "O que você escolhe: se concorda (aí passa a valer como decisão sua), se quer diferente "
                                       "(entra na lista de fazer) ou se testa antes de responder.",
    "auditoria-6-para-depois": "O que você escolhe: se entra agora na lista de fazer (a gerente faz uma coisa de cada vez e "
                               "chama você para testar), se continua para depois ou se você não quer mais.",
}
OPCOES = {
    "certo": ("Está certo assim", "Fica como está hoje na versão de teste."),
    "mudar": ("Quero mudar: pôr na lista de fazer", "Escreva no comentário o que quer diferente; entra na fila de trabalho."),
    "testar": ("Vou testar antes de responder", "Fica marcada para você testar pelo atalho da versão de teste."),
    "concordo": ("Concordo, fica assim", "Passa a valer como decisão sua."),
    "diferente": ("Quero diferente: pôr na lista de fazer", "Escreva no comentário como quer; entra na fila de trabalho."),
    "fazer": ("Pôr na lista de fazer", "Entra na fila de trabalho; a gerente faz uma coisa de cada vez e chama você para testar."),
    "depois": ("Fica para depois", "Continua anotada no Livro, sem prazo."),
    "nao-quero": ("Não quero mais", "Fica descartada no Livro, com a sua resposta."),
}


SOBRE = {
    "au-d-003": {"quer": "A ordem das etapas do Automático pode ser mudada arrastando com o mouse. Ainda está em aberto "
                         "se isso muda também a ordem em que a página é montada."},
    "au-d-016": {"quer": "Arrastar as etapas no Automático muda a ordem em que elas rodam (o que o programa procura e "
                         "decide primeiro). A montagem da página segue sempre a mesma ordem (endireita, depois corta uma "
                         "vez só, no fim), para não comer a página.",
                 "pediu": "\"Ordem das etapas: livre. [...] muda arrastando com o mouse. Sem cadeados.\" (28/09) e, em "
                          "09/10, endireitar antes de cortar, como o ScanTailor.",
                 "titulo": "Arrastar as etapas do Automático muda a ordem em que rodam, mas não a montagem da página"},
    "au-d-113": {"titulo": "Página curva com moldura escura do scanner: pintar a moldura de branco antes de desentortar",
                 "quer": "Página curva com moldura escura do scanner: o programa pinta a moldura de branco antes de "
                         "desentortar, para o desentortador não confundir a moldura com as letras."},
    "au-d-095": {"titulo": "Consertos que ficaram do corte de 12/10 (moldura colada, título colado, cantinhos brancos)",
                 "quer": "Consertos que ficaram da conferência do corte de 12/10: moldura colada em cima (Siebmacher 9), "
                         "título colado (Escola 7) e cantinhos brancos com o corte até a beirada (Boécio 8, Marial 7, "
                         "Graduale 221)."},
    "au-d-304": {"pediu": "(resumo) PDF em duas camadas (letra em cima, fundo embaixo) · 01/10: \"(b) Deixar como está até "
                          "o PDF em camadas chegar na ordem - Eu quero ter a opção, mas eu quero poder deixar como está "
                          "também, o tamanho do arquivo depois não importa\" · \"Está bom\""},
    "au-d-488": {"titulo": "A tela antiga \"O que fazer\" sai do caminho (o arquivo dela continua guardado, sem uso)",
                 "quer": "A tela \"O que fazer\" não abre mais: tudo o que ela tinha mora no Automático. O arquivo do "
                         "programa com essa tela continua guardado, sem uso; apagar fica para depois."},
    "au-d-494": {"titulo": "No corte \"até a moldura\", as páginas não são forçadas ao mesmo tamanho",
                 "quer": "No corte \"até a moldura\", as páginas não são forçadas ao mesmo tamanho; a caixinha "
                         "\"Margens iguais\" fica à vista na tela do corte para quem quiser."},
    "au-d-477": {"quer": "Ferrugem rosada da Pesel 2 no \"Tirar o fundo\": deve sumir, não só mudar de cor, como as "
                         "outras manchas. Entra junto com as manchas vermelhas e marrons (Fase 6). Até lá fica como defeito "
                         "pequeno conhecido, como você aprovou em 02/10.",
                 "titulo": "Ferrugem rosada da Pesel 2 no \"Tirar o fundo\": deve sumir, como as outras manchas"},
    "au-d-480": {"titulo": "Os manuscritos (Graduale, Palatino) entram na leitura do texto da Fase 7",
                 "quer": "Os manuscritos (Graduale, Palatino) entram na leitura do texto (Fase 7), com um leitor de "
                         "manuscrito, porque o leitor de hoje não lê letra à mão."},
    "au-d-476": {"titulo": "\"Marcar como\" com \"iluminura ou pintura\" e \"moldura\" fica para depois da rodada de consertos",
                 "quer": "\"Marcar como\" com \"iluminura ou pintura\" e \"moldura\" entra depois da rodada de "
                         "consertos, junto com separar o texto de dentro da iluminura, porque muda o processamento "
                         "(não é só tela)."},
    "au-d-549": {"quer": "Só o que você mandou: por isso o limite de resolução foi cancelado e o PDF voltou a sair sem "
                         "perda, como você decidiu (\"o tamanho do arquivo depois não importa\"); o \"PDF gigante\" era "
                         "achado de agente, não pedido seu. As escolhas da gerente que acrescentam ou mudam algo voltam "
                         "a você como pergunta.",
                 "sol": "auditoria das escolhas: o PDF com perda desfeito, os nomes do \"Montar para imprimir\" de volta, "
                        "os quatro jeitos do lado direito feitos.",
                 "titulo": "Só o que você mandou: os agentes não mudam o que você já decidiu"},
    "au-d-551": {"titulo": "Fica a frase da tela \"Ficou pronto!\" sobre montar para imprimir em A4",
                 "quer": "Fica a frase da tela \"Ficou pronto!\" sobre montar para imprimir em A4."},
    "au-d-066": {"titulo": "Tela e PDF iguais, já na rodada de consertos (não só na fase de velocidade)",
                 "quer": "A tela mostra a página igual ao PDF, já na rodada de consertos (não só na fase de velocidade)."},
    "au-d-285": {"ressalva": "O número que muda ao folhear não foi feito."},
    "au-d-522": {"quer": "Livro com muitas páginas em branco (versos): um aviso só do livro em vez de um por página. "
                         "\"Muitas\" = 40% ou mais das páginas: o número foi a gerente que pôs, porque você não disse."},
    "au-d-195": {"titulo": "\"Igualar a luz\" em todos os filtros, desligado de fábrica, com aviso de tinta lavada no "
                           "Melhorar e no Mágico pro",
                 "quer": "\"Igualar a luz\" em todos os filtros, desligado de fábrica, com aviso de tinta lavada no "
                         "Melhorar e no Mágico pro."},
    "au-d-092": {"titulo": "Tarja da biblioteca e moldura do scanner: o Kaique escolhe por livro entre cortar fora e "
                           "pintar de branco",
                 "quer": "Tarja da biblioteca e moldura do scanner: o Kaique escolhe por livro entre cortar fora e pintar "
                         "de branco."},
    "au-d-025": {"pediu": "(resumo, sem as suas palavras exatas) caixa da página e guias."},
    "au-d-026": {"pediu": "(resumo, sem as suas palavras exatas) consertar o zoom que às vezes não funciona e o "
                          "travamento com muitos cliques (defeitos de 15-16/09 e 24/09)."},
    "au-d-074": {"pediu": "(resumo, sem as suas palavras exatas) dividir a folha sabendo quando é uma página só."},
    "au-d-480-pediu": {"pediu": "(escolha da gerente) sua decisão de 28/09: \"OCR de manuscrito desde o começo\", e o "
                                "item do plano de treinar o leitor de manuscrito."},
    "au-d-490": {"pediu": "(escolha da gerente) a pergunta \"Quer tirar o fundo?\" ao abrir o livro, que você aprovou.",
                 "titulo": "O \"Sim\" do aviso do fundo, ao abrir o livro, vale na hora (e dá para desfazer)"},
    "au-d-104": {"titulo": "Os outros 8 lugares que podem comer a página: provar em páginas reais, depois consertar"},
    "au-d-017": {"titulo": "Aumentar o conteúdo além da beirada não corta nada escondido: a parte de fora fica marcada "
                           "e a página ganha aviso"},
    "au-d-543": {"titulo": "Quando aparece o aviso \"Parte do impresso fica de fora\" (ferramenta Mover)"},
    "au-d-479": {"titulo": "\"o do Editor\" / \"a do Editor\" em todo lugar onde aparece a conta do próprio programa"},
    "au-d-485": {"titulo": "O que conta como \"mexida à mão\" no aviso do Automático (inclusive em livro antigo)"},
    "au-d-491": {"titulo": "O corte de página endireitada: \"fica\" ou \"acompanha\", em três lugares (Configurações, "
                           "livro e página)"},
    "au-d-542": {"titulo": "\"Centralizar\" e o ímã do Mover olham o que está impresso, não a moldura da página"},
    "au-d-475": {"titulo": "\"Só as pares\" num livro dividido: o aviso fala da página e da folha que o Kaique vê"},
    "au-d-489": {"titulo": "\"Começar a conferência de novo\" só acontece quando o PDF mudou ou o trabalho não dá para ler"},
    "au-d-492": {"titulo": "O tique do menu Filtro acompanha o filtro da página aberta"},
    "au-d-501": {"titulo": "O livro nunca abre na ferramenta Dividir; o Dividir fica a um clique"},
    "au-d-070": {"titulo": "\"Laboratório\" no Automático em tela cheia: provar receitas lado a lado"},
    "au-d-212": {"titulo": "Opções de achar as gravuras na tela, por livro, com os valores de fábrica do ScanTailor"},
    "au-d-545": {"titulo": "\"usar em todas...\" do Mover leva o tamanho e o lugar do conteúdo às páginas escolhidas"},
    "au-d-498": {"titulo": "\"não dividir esta\" junta as duas páginas; \"dividir esta\" devolve as duas como estavam"},
    "au-d-500": {"titulo": "Corte do ScanTailor na beirada da folha não é a lombada: vale a conta do Editor e a folha vai "
                           "para \"Lombada incerta\""},
    "au-d-541": {"titulo": "Como a ferramenta Mover mexe: arrastar, puxar o canto e o número do tamanho"},
    "au-d-478": {"titulo": "Espaços \"Limpo / Completo\" viram arranjos de painéis salvos com nome"},
}


def reescrever(aba: str, p: dict) -> dict:
    c = campos(p)
    sobre = {**SOBRE.get(p["id"], {}), **SOBRE.get(p["id"] + "-pediu", {})}
    c.update({k: v for k, v in sobre.items() if k != "titulo"})
    m = re.match(r"au-d-(\d+)", p["id"])
    num = f"D-{int(m.group(1)):03d}"
    titulo = re.sub(r"^D-\d+(?:\s*\([^)]*\))?\s*·\s*", "", p["titulo"]).strip()
    titulo = sobre.get("titulo") or limpar(titulo)
    if titulo.endswith("…") and not sobre.get("titulo"):
        # o título antigo vinha cortado: usa a primeira frase do "o que é", se couber
        primeira = re.split(r"(?<=[.!?])\s", limpar(c["quer"]))[0].rstrip(".")
        if len(primeira) <= 170:
            titulo = primeira
    quer = limpar(c["quer"])
    parte = limpar(c["parte"]).rstrip(".")
    ex = []
    # 1. onde fica e o que é
    if parte:
        ex.append(f"Onde fica: {parte}. O que é: {_ponto(quer)}")
    else:
        ex.append(f"O que é: {_ponto(quer)}")
    # 2. de onde veio
    gerente = c["pediu_rotulo"].startswith("Escolha da gerente") or c["pediu"].startswith("(escolha da gerente")
    if gerente:
        data = re.search(r"\((\d{2}/\d{2})", c["pediu_rotulo"])
        resto = limpar(re.sub(r"^\(escolha da gerente[^)]*\)\s*", "", c["pediu"]))
        resto = re.sub(r"^apoiada\s+(?:em|no|na|nos|nas)\s+", "", resto)
        resto = re.sub(r"\bitem \d\.\d{1,2}\s*", "", resto)
        resto = re.sub(r"\bno \(", "na pergunta (", resto)
        frase = (f"De onde veio: ninguém perguntou a você. A gerente escolheu sozinha"
                 f"{' em ' + data.group(1) if data else ''}, durante a rodada de consertos.")
        if resto and not resto.lower().startswith("(escolha") and len(resto) > 3:
            frase += f" Ela se apoiou em: {_ponto(resto)}"
        ex.append(frase)
    elif c["pediu"]:
        data = re.search(r"\((.*)\)\s*$", c["pediu_rotulo"])
        quando = f" ({limpar(data.group(1))})" if data else ""
        ex.append(f"O que você pediu{quando}: {_ponto(limpar(c['pediu']))}")
    # 3. como está hoje
    sol = limpar(c["sol"])
    sit = c["sit"].rstrip(".")
    if aba == "auditoria-6-para-depois":
        hoje = f"Como está hoje: combinado para depois desta rodada; na versão de teste: {_ponto(sol)}"
    else:
        hoje = f"Como está hoje (versão de teste): {_ponto(_maiuscula(sol))}"
        if sit and sit.lower() not in ("funciona",):
            hoje += f" Na auditoria de 29/10: {sit.lower()}."
    if c["ressalva"]:
        hoje += f" O que ainda não está bom: {_ponto(limpar(c['ressalva']))}"
    ex.append(hoje)
    # 4. já testado ou já respondido por ele?
    teste = TESTADAS.get(num)
    for irma in re.findall(r"D-(\d+)", c["junto"]):
        arq = RESPOSTAS / f"au-d-{int(irma):03d}.json"
        if arq.exists() and not teste:
            r = json.loads(arq.read_text(encoding="utf-8"))
            com = (r.get("comentario") or "").strip()
            em = r.get("em", "")
            teste = ("sai-resp", f"Já respondido por você: esta pergunta foi resolvida junto com outra, que você "
                                 f"respondeu em {em[8:10]}/{em[5:7]}: \"{r.get('opcaoNome', '')}\""
                                 + (f" (\"{com}\")" if com else "") + ". Vale o mesmo aqui.")
    if teste and teste[0] == "sai-resp":
        ex.append(teste[1])
    else:
        ex.append(("Já testado por você: " + teste[1]) if teste else NAO_TESTADA)
    # 5. o que escolhe
    ex.append(ESCOLHAS[aba])
    junto = re.findall(r"D-\d+", c["junto"])
    ex.append(f"(Para consulta: {num}" + (f"; resolvida junto com {', '.join(junto)}" if junto else "") + ".)")
    p["titulo"] = titulo
    p["explicacao"] = ex
    for o in p["opcoes"]:
        if o["id"] in OPCOES:
            o["nome"], o["texto"] = OPCOES[o["id"]]
    if teste and teste[0] == "sai":
        p["sugestao"] = "Pode sair da lista: já testado e funcionando (ver \"Já testado por você\")."
    elif teste and teste[0] == "sai-resp":
        p["sugestao"] = "Pode sair da lista: você já respondeu a mesma coisa na pergunta irmã."
    for e in p.get("exemplos", []):
        e["legenda"] = limpar(e.get("legenda", ""))
    if p.get("primeira_imagem"):
        p["primeira_imagem"]["legenda"] = limpar(p["primeira_imagem"].get("legenda", ""))
    p["_teste"] = teste[0] if teste else ""
    return p


def resumo(aba: str, doc: dict, n_espera: int) -> None:
    nomes = {
        "auditoria-3-com-ressalva": ("Auditoria 3: funciona, mas com um senão",
                                     "Decisões suas que funcionam na versão de teste, mas com algo que ainda não está bom."),
        "auditoria-4-funciona": ("Auditoria 4: funciona", "Decisões suas que funcionam na versão de teste."),
        "auditoria-5-escolhas-da-gerente": ("Auditoria 5: o que a gerente escolheu sem perguntar",
                                            "Aqui não há decisão sua: são escolhas que a gerente fez sozinha na rodada de "
                                            "consertos. Ficam separadas para você dizer se concorda."),
        "auditoria-6-para-depois": ("Auditoria 6: combinado para depois",
                                    "Decisões suas que ficaram combinadas para depois da rodada de consertos."),
    }
    titulo, frase = nomes[aba]
    doc["resumo"] = {"titulo": f"{titulo} ({n_espera} esperando você)", "paragrafos": [
        frase,
        "Cada quadro diz: onde fica e o que é; o que você pediu, com a data e as suas palavras; como está hoje; e se "
        "você já testou depois da auditoria de 29/10. As que você já testou e funcionam dizem \"Pode sair da lista\".",
        "As imagens são as que já existiam (prints de quando o assunto foi decidido).",
    ]}


def montar():
    relatorio = {}
    for aba in ABAS:
        doc = ler(aba)
        espera = 0
        lista = []
        for p in doc["perguntas"]:
            if (RESPOSTAS / f"{p['id']}.json").exists():
                continue
            espera += 1
            reescrever(aba, p)
            lista.append((p["id"], p.pop("_teste")))
        resumo(aba, doc, espera)
        gravar(aba, doc)
        relatorio[aba] = lista
    (PASTA / "cru" / "parte3-lista.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    return relatorio


if __name__ == "__main__":
    r = montar()
    print({k: len(v) for k, v in r.items()}, sum(len(v) for v in r.values()))
