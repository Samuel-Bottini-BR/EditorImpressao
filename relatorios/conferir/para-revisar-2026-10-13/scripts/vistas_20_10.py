"""20/10/2026: o que o verificador viu na retomada (as 19 imagens, as quatro paginas reabertas, o
teclado, as fotos contra as decisoes) - grava imagens_vistas_20-10.json, que o terceira.py le.
Os textos sao escritos aqui, a mao, depois de abrir cada imagem. Nao mede nada."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent

DEZENOVE = [
    ("duplo-clique-1-aviso-continua-recorte", "Antiphonal 46 (pedaço de 6 páginas): cinco cartões com o quadrado laranja no T, o aviso \"Pode ter sumido parte de um desenho...\" de pé e os botões \"Trazer de volta nesta página\" e \"está bom assim\". O aviso continuou depois dos dois cliques. Bate com o parecer."),
    ("duplo-clique-2-ver-de-perto", "\"Ver de perto\", página 3 de 6, Preto e branco: a letra T aparece (é a tela que engana). Bate."),
    ("teclado-1-recorte", "Egenloff, página 13 escolhida na tira (moldura azul) e \"Esta página vai sair em Preto e branco\": a barra de espaço avançou da 12 para a 13. Bate."),
    ("teclado-2-tela", "A mesma tela inteira, 1280 x 657 (com as abas da tela antiga). Bate."),
    ("forca-1-camoes-recorte", "Camões 27: aviso \"O texto desta página saía falhado: escureci a força do preto só nela\", medidor em \"bem forte\", \"Desfazer\" e \"está bom assim\". Bate. (Print da primeira conferência; o comportamento no Camões 27 não mudou.)"),
    ("forca-2-camoes-tela", "Camões 27 na tela inteira, painel \"Para revisar 35\", \"Desfazer\". Bate."),
    ("forca-4-egenloff-3-recorte", "Egenloff 3 (folha de rosto): só o aviso \"Texto falhado\" (aviso 1 de 2), força \"normal\", botões \"usar mais escuro\" e \"está bom assim\"; marcas laranja na linha do carimbo embaixo. Bate: a força não mexe mais sozinha."),
    ("sem-conteudo-1-egenloff-recorte", "Egenloff 12 (verso só com o carimbo): aviso \"Esta página parece não ter nada do livro\" (aviso 1 de 2) e os três botões. Bate."),
    ("sem-conteudo-2-egenloff-tela", "A mesma tela inteira, painel \"Para revisar 6\". Bate."),
    ("sem-conteudo-5-rariora-recorte", "Rariora 8 (folha de rosto com o título muito fraco): o mesmo aviso, com os três botões. Bate. Repare: o cartão do Preto e branco ainda mostra a página amarelada, quase igual ao Original (a prévia talvez ainda não tivesse chegado)."),
    ("janela-diferente-1-graduale-221-recorte", "Graduale 221 (página 3 do pedaço): quatro cartões e a faixa \"Esta página vai sair em Preto e branco\", sem aviso. Bate."),
    ("janela-diferente-2-graduale-221-tela", "A mesma tela inteira: a página 3 sem \"!\" na tira (a 1 tem). Bate."),
    ("marcar-2-antes-tela", "Aba Marcar, Graduale 221: \"Marcado: 4 de letra e traço e 5 de papel\" (9 áreas). Bate. Repare: na aba Marcar o painel diz \"Para revisar: nada pendente\"."),
    ("marcar-3-depois-tela", "A mesma página uns 10 s depois: \"Marcado: 7 de letra e traço e 11 de papel\" (18 áreas); a diferença à vista é pequena (faixas à esquerda). Bate."),
    ("palatino-66-3-tela", "Palatino 66: marcas laranja na linha \"Palatinus Romae\", aviso \"Texto falhado\", força \"normal\", \"usar mais escuro\". Bate."),
    ("parece-em-branco-2-tela", "Gladstone 18: os cartões com o título \"DA ORAÇÃO\" pequeno e o aviso \"Esta página parece estar em branco...\", com os três botões. Bate (o aviso é o erro conhecido)."),
    ("contagens-2-painel-tela", "Camões 66: painel \"Para revisar 39\", aviso do Endireitar e só \"está bom assim\". Bate (o 39 da pergunta)."),
    ("contagens-3-salvar", "Janela \"Onde salvar o livro pronto\": \"Ainda há 106 página(s) que você não conferiu\" e \"106 páginas vão para o PDF\". Bate (o 106 da pergunta)."),
    ("bug-duplo-clique-tira-o-aviso-tela", "Apesar do nome, é a tela DEPOIS do conserto: pedaço do Antiphonal, página 3 com o aviso de pé e os dois botões. Bate com o quadro dos dois cliques (o nome do arquivo vem da primeira conferência e engana)."),
]

dados = {
    "dezenove": [{"img": f"img/{n}.jpg", "vi": t} for n, t in DEZENOVE],
}
(AQUI / "imagens_vistas_20-10.parcial.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(DEZENOVE), "imagens")
