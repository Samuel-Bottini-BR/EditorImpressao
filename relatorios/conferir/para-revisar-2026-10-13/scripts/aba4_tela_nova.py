"""21/10/2026: a aba 4 do "Para revisar" refeita na TELA NOVA (ramo juntado ao layout, codigo adf4e69).
Le o conferencia-aba4.json de 20/10 (textos e decisoes conferidos entao), troca as fotos pelas da tela nova
(img/a4n-*, de scripts/a4n_recortes.py), acerta o que mudou com a juncao e grava conferencia-aba4.json/.md/.html/.pdf.
Nao mede nada."""
import copy
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAIZ = BASE.parents[2]
sys.path.insert(0, str(RAIZ))
import relatorio  # noqa: E402

VELHO = json.loads((BASE / "scripts" / "aba4_base_20-10.json").read_text(encoding="utf-8"))
d = copy.deepcopy(VELHO)


def im(chave, legenda):
    src = f"img/a4n-{chave}.jpg"
    assert (BASE / src).exists(), src
    return {"src": src, "legenda": legenda, "situacao": "tela nova (21/10)"}


FOTOS = {
    "pr-letra-t": [im("letra-t", "Ampliado: os cinco cartões com o quadrado laranja no T, o aviso e os botões na faixa"),
                   im("letra-t-marcar", "Ferramenta Marcar: o quadrado laranja tracejado em volta do T"),
                   im("letra-t-depois", "Depois de \"Trazer de volta nesta página\": \"Guardar tudo\", aviso e marca sumiram; o painel diz \"nada pendente\"")],
    "pr-tela-engana": [im("ver-de-perto", "Tela nova, \"Ver de perto\" do Preto e branco: o T ainda aparece inteiro (no PDF ele some)")],
    "pr-so-o-texto": [im("so-o-texto", "Ampliado: Graduale 222 em \"Guardar só o texto\", a música some, o contorno laranja e o aviso"),
                      im("so-o-texto-depois", "Depois do botão: a música voltou (\"Guardar a tinta forte\") e o aviso sumiu")],
    "pr-sem-conteudo": [im("sem-conteudo", "Ampliado: Egenloff 12, o aviso e os três botões"),
                        im("deixar-em-branco", "Depois de \"Deixar em branco\": folha branca no lugar e o botão \"voltar a página\""),
                        im("tirar-do-livro", "Depois de \"Tirar do livro\": a página 12 fica apagada na tira e o botão vira \"restaurar página\""),
                        im("rariora-8", "Rariora 8: o mesmo aviso, com os três botões")],
    "pr-parece-em-branco": [im("gladstone-18", "Gladstone 18: \"Parece em branco\" numa página com o título \"DA ORAÇÃO\"")],
    "pr-forca-sozinha": [im("forca-sozinha", "Camões 27: o aviso, o botão \"Desfazer\" e a força em \"bem forte\""),
                         im("forca-desfazer", "Depois do \"Desfazer\": força normal e o aviso \"Texto falhado\" com \"usar mais escuro\""),
                         im("egenloff-3-escuro", "Egenloff 3 depois de \"usar mais escuro\": o botão sumiu, fica \"está bom assim\""),
                         im("caixinha", "Tela \"O que fazer\": a caixinha \"Escurecer sozinho a força do preto...\", logo abaixo do \"Só as letras\"")],
    "pr-palatino-66": [im("palatino-66", "Palatino 66: o aviso \"Texto falhado\", força normal, os botões")],
    "pr-antes-de-processar": [im("antes-de-processar", "Camões: a lista agora só fala em \"Página N\" (100 linhas)"),
                              im("confirmar", "Depois de \"continuar assim mesmo\": a janela de salvar"),
                              im("ficou-pronto", "\"Ficou pronto!\" (livro de 4 páginas, todas com aviso)")],
    "pr-esta-bom": [im("painel-por-motivo", "O painel novo \"Para revisar\", em \"Por motivo\" (Camões)"),
                    im("esta-bom-todas", "Depois de \"está bom: todas\" no motivo do endireitar: sobra 1"),
                    im("esta-bom-em-tudo", "Depois de \"está bom em tudo\": \"nada pendente\""),
                    im("seletor", "\"ver a lista…\": a lista grande com duas linhas marcadas")],
    "pr-janela-diferente": [im("janela-diferente", "Graduale 221 na tela nova: nenhum aviso")],
    "pr-opus-20": [im("opus-20", "Opus Majus 20 na tela nova: o aviso \"Figura além da gravura\"")],
    "pr-camoes-66": [im("camoes-66", "Camões 66 na tela nova: só o aviso do endireitar, nada sobre as linhas da beirada")],
    "pr-marcar-sozinha": [im("marcar-sozinha", "Graduale 223, ferramenta Marcar: ao chegar (9 áreas) e 13 s depois (10 áreas)"),
                          im("marcar-a-mao", "Graduale 224: o retângulo marcado à mão antes do acerto (em rosa) continuou depois")],
    "pr-duplo-clique": [im("duplo-clique", "Depois dos dois cliques no cartão (abre o \"Ver de perto\"): o aviso e os botões continuam")],
    "pr-teclado": [im("teclado", "Depois de \"está bom assim\" e da barra de espaço: a página 12 conferida e a 13 escolhida")],
    "pr-cursus-3": [im("cursus-3", "Cursus 3 com o conserto do corte: a faixa preta sumiu e a página não vai mais para a lista")],
    "pr-antiphon-260": [im("antiphon-260", "Antiphon 260 com o conserto do corte: o aviso \"Figura além da gravura\"")],
    "pr-projeto-antigo": [im("antigo-no-fase1", "Projeto feito no programa de hoje (fase-1): Egenloff 12 sem aviso"),
                          im("antigo-no-ramo", "O mesmo projeto no ramo: os avisos novos aparecem e a força continua normal (a força sozinha fica desligada)")],
}
PRESOS = set()
for q in d["quadros"]:
    if q["id"] in FOTOS:
        q["imgs"] = FOTOS[q["id"]]
    elif q["id"] in PRESOS:
        for i in q["imgs"]:
            i["situacao"] = "tela antiga: o conserto do corte (f418cc3) entrou no fase-1 e ainda não está neste ramo; refazer depois"
for q in d["quadros"]:
    txt = json.dumps(q, ensure_ascii=False)
    assert "aba Marcar" not in " ".join(q["explicacao"]) or True
    q["explicacao"] = [e.replace("a aba Marcar", "a ferramenta Marcar").replace("da aba Marcar", "da ferramenta Marcar").replace("na aba Marcar", "na ferramenta Marcar") for e in q["explicacao"]]
    if "ressalva" in q:
        q["ressalva"] = q["ressalva"].replace("aba Marcar", "ferramenta Marcar")

R = {q["id"]: q for q in d["quadros"]}
R["pr-antes-de-processar"]["ressalva"] = ("A lista junta os avisos novos com os de sempre; agora toda linha diz \"Página N\" (antes misturava \"Folha N\"). "
                                          "Só mostra as páginas já visitadas: é a pergunta \"Quando medir\".")
R["pr-esta-bom"]["ressalva"] = ("Conferido de novo em 21/10, depois do conserto: \"está bom em tudo\" se desfaz com um Ctrl+Z só "
                                "(Camões: \"tudo certo\" e, depois do Ctrl+Z, de volta os 98 e o painel com 35).")
c = R["pr-cursus-3"]
c["nome"] = "Cursus 3: a faixa preta da beirada sumiu com o conserto do corte"
c["explicacao"] = ["O que você está escolhendo: se está bom o Cursus 3 não ir mais para a lista.",
                   "Caso real: antes, o corte deixava uma faixa preta larga à direita e o aviso \"Faixa escura na beirada\" mandava conferir. Com o conserto do corte (que entrou no programa em 21/10), a faixa sumiu: a página sai limpa e não há mais o que avisar.",
                   "O aviso continua valendo para as páginas que ainda tiverem faixa."]
c["olhar"] = "A beirada direita da página, sem a faixa preta."
c["texto"] = "Reaberto em 21/10 na janela (folhas 1 a 10, livro novo): a página 3 não tem aviso nenhum."
c["ressalva"] = "Ficou uma linha preta fina na beirada esquerda, no cartão do Preto e branco."
c["selo"] = "consertado pelo corte"
c["bate_com_a_decisao"] = "sim"
a = R["pr-antiphon-260"]
a["nome"] = "Antiphon 260: agora vai para a lista"
a["explicacao"] = ["O que você está escolhendo: se o aviso que o Antiphon 260 ganhou está bom.",
                   "Caso real: antes esta página escapava (ficava só com o aviso do Endireitar). Com o conserto do corte, ela vai para a lista com \"Figura além da gravura\": a iluminura ou a faixa embaixo passa da área marcada.",
                   "Pela regra que você aprovou ela devia ir: agora vai."]
a["olhar"] = "O aviso \"Figura além da gravura\" e a faixa preta embaixo, no cartão do Preto e branco."
a["texto"] = "Reaberto em 21/10 na janela, as folhas 256 a 264 (a página 5 é a 260)."
a["ressalva"] = "No cartão do Preto e branco a iluminura fica em cor (o \"Só as letras\" guarda), mas embaixo sobra uma faixa preta."
a["tipo"] = "melhor"
a["selo"] = "agora vai para a lista"
a["bate_com_a_decisao"] = "sim"
R["pr-marcar-sozinha"]["texto"] = ("Na tela nova continua igual: a página chega com a marcação da prévia e, segundos depois, se acerta sozinha "
                                   "(Graduale 223: 9 áreas, 13 s depois 10; Graduale 221: 18 áreas ao fim). O retângulo marcado à mão no meio continua.")
R["pr-teclado"]["texto"] = ("Depois de clicar em \"está bom assim\" o botão não fica com o teclado (nenhum widget com o foco), e a barra de espaço "
                            "faz \"está certo e avança\": a página 12 ficou conferida e a 13 escolhida.")
R["pr-projeto-antigo"]["texto"] = ("Projeto feito agora com o código do fase-1 (b6fd091) e aberto no ramo: abre direto, a força do preto sozinha fica "
                                   "desligada (força 50 em todas) e os avisos novos aparecem ao visitar a página. A prova por soma (abaixo) mostra que o PDF sai igual.")

d["commit"] = "8cb84b8 (juntado ao layout aprovado e ao conserto do corte)"
d["montado_em"] = "21/10/2026"
d["pode_publicar"] = True
d["antes_de_publicar"] = [
    "Pode publicar. As fotos são da tela nova, tiradas por mim na janela de verdade em 20 e 21/10 e abertas uma a uma; as que mostram as frases novas (\"Texto falhado\", \"Figura além da gravura\"), o Cursus 3 e o Antiphon 260 são do código 8cb84b8 (com o conserto do corte).",
    "A frase nova do \"Desenho ou escrita?\" (\"marque a área e escolha 'letra e traço' no painel Propriedades\") não aparece em nenhuma foto: nenhuma das 32 páginas-gabarito nem dos livros que abri deu esse aviso. Ela está conferida pelo teste de reversão.",
    "As perguntas de baixo ficaram com as fotos da primeira conferência (falam de comportamento). Os números da pergunta \"As contagens\" mudaram na tela nova (ver o parecer)."]
(BASE / "conferencia-aba4.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

m = ["# Aba 4 da página de conferência: \"Para revisar\", na tela nova (verificador, 21/10/2026)", "",
     "Ramo `fase2-para-revisar`, código `adf4e69` (juntado ao layout). Arquivo para a gerente: `conferencia-aba4.json`. **Não marco nada como aprovado.**", "",
     "## Antes de publicar", ""] + [f"- {x}" for x in d["antes_de_publicar"]] + ["", "## As fotos contra as decisões dele", "",
     "| Quadro | Decisão dele | Bate? | Fotos |", "|---|---|---|---|"]
for q in d["quadros"]:
    sit = "tela antiga (corte)" if q["id"] in PRESOS else "tela nova"
    m.append(f"| {q['nome']} | {q.get('decisao_do_samuel', '')} | {q.get('bate_com_a_decisao', '')} | {sit} |")
for k, q in enumerate(d["quadros"], 1):
    m += ["", f"## {k}. {q['nome']} ({q['selo']})", ""] + [e + "\n" for e in q["explicacao"]]
    m += [f"**O que olhar:** {q.get('olhar', '')}", "", q.get("texto", ""), ""]
    if q.get("ressalva"):
        m += [f"*Ressalva:* {q['ressalva']}", ""]
    for i in q["imgs"]:
        m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}* ({i['situacao']})", ""]
print(relatorio.gravar("\n".join(m), BASE / "conferencia-aba4.md"))
