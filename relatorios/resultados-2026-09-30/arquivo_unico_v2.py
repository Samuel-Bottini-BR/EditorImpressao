# Segunda versao do arquivo unico de resultados para o Kaique (30/09/2026):
# exemplos aprovados pelo Samuel nas conferencias 1, 2 e 3, pedidos de mudanca e o que falta.
import base64, io, json, re
from PIL import Image
BASE = "resultados-2026-09-30/"
SECOES = [
 {"classe":"bom","titulo":"Aprovado pelo Samuel","sub":"Resultados que o Samuel conferiu e aprovou. Clique na foto para ver grande.","itens":[
  ["1-papel-branco","Retrato: papel branco, desenho intacto","O papel amarelado vira branco e o retrato fica com todos os traços. (Palatino, pág. 5)"],
  ["palatino57","Página com moldura e letra antiga","Papel branco, moldura, laços e letras inteiros. (Palatino, pág. 57)"],
  ["palatino67","Sem a caixa cinza em volta da linha","Antes ficava uma caixa cinza em volta de uma linha; agora não. (Palatino, pág. 67)"],
  ["2-pintura-cor","Pintura mantém a cor","O anjo continua colorido; só o papel em volta fica branco. (Na escola de Jesus, pág. 35)"],
  ["escola7","Gravura inteira","A gravura do céu sai inteira e o papel fica branco. (Na escola de Jesus, pág. 7)"],
  ["3-corte","O corte das bordas não come o texto","Antes o programa cortava o começo das linhas e o número da página (\"37\" virava \"3\")."],
  ["horas13","Moldura dourada e título colorido","Moldura dourada inteira, títulos em vermelho e azul, papel branco. (Livro de Horas, pág. 13)"],
  ["horas26","Calendário com moldura dourada","A moldura sai inteira (antes saía cheia de furinhos). (Livro de Horas, pág. 26)"],
  ["horas27","Calendário com moldura dourada","Moldura inteira e as letras do calendário certas. (Livro de Horas, pág. 27)"],
  ["horas47","Página toda decorada","As pinturas e os dourados ficam intactos e o centro fica branco. (Livro de Horas, pág. 47)"],
  ["4-tirar-fundo","Tirar o fundo: a foto fica igual","Em livros baixados do Internet Archive, o programa tira o fundo e a foto fica igual ao original. (Opus Majus, pág. 20)"],
  ["opus20-fotos","Livro com fotos","Com a opção \"Este livro tem fotos\", a foto da estátua sai inteira. (Opus Majus, pág. 20)"],
  ["opus165","Figuras e diagramas","As figuras ficam inteiras e o papel branco. (Opus Majus, pág. 165)"],
  ["opus256","Tabela grande","A tabela inteira, com o fundo tirado. (Opus Majus, pág. 256)"],
  ["rhetorica18","Página com filetes","As letras que encostam na borda ficam. (Rhetorica Christiana, pág. 18)"],
  ["graduale222","Partitura","A pauta e as notas não são mais tratadas como desenho; papel branco. (Graduale, pág. 222)"],
  ["7-partitura","Partitura: a clave","A clave e o começo da pauta ficam inteiros. (Graduale, pág. 222)"],
  ["marial153","Título de capítulo","O título não é mais tratado como desenho (some a caixa cinza). (Marial, pág. 153)"],
  ["8-pergunta","O programa pergunta antes de tirar o fundo","Ao abrir um livro desse tipo, o programa pergunta se você quer tirar o fundo. Nada muda sem você dizer \"sim\"."],
 ]},
 {"classe":"andamento","titulo":"Pedidos de mudança (já decididos, falta aplicar)","sub":"O Samuel pediu estas mudanças em 30/09. Ainda vão ser feitas no programa.","itens":[
  ["pb-moldura","Preto e branco: a moldura dourada fica colorida","No Preto e branco, o texto sai preto e nítido. Decidido: a moldura dourada mantém a cor (como no meio da imagem, \"ANTES\"); traço preto (à direita) só se a pessoa escolher."],
  ["n2-foto-pb","Preto e branco: foto em tons de cinza","Hoje a foto fica ruim no Preto e branco. Decidido: foto e pintura vão sair em tons de cinza. (Opus Majus, pág. 20)"],
  ["n3-titulo-vermelho-pb","Preto e branco: título vermelho sai preto","Hoje os títulos vermelhos somem no Preto e branco. Decidido: vão sair pretos. (Livro de Horas, pág. 13)"],
  ["n1-iluminura","Cor da página decorada","A página perde a cor original (a cena azul de baixo fica lavada) e sobra sujeira na margem. Vai ser corrigido. (Livro de Horas, pág. 11)"],
  ["corte-crista","O corte cortou uma letra","Num exemplo, o corte da borda cortou o \"A\" de \"Crista\". O corte não pode comer texto: vai ser corrigido."],
 ]},
 {"classe":"ruim","titulo":"Ainda não está bom","sub":"Problemas que ainda estão sendo estudados.","itens":[
  ["n4-papel-atras-titulo","Papel atrás do título","O papel atrás das letras do título ainda não fica totalmente branco. (Marial, pág. 153)"],
  ["marial7","Manchas na folha","A faixa escura da borda sumiu, mas ainda ficam várias manchas na folha. (Marial, pág. 7)"],
 ]},
]
html = open(BASE + "resultados.html", encoding="utf-8").read()
ini = html.index("const SECOES = ["); fim = html.index("const CHAVE")
html = html[:ini] + "const SECOES = " + json.dumps(SECOES, ensure_ascii=False, indent=1) + ";\n\n" + html[fim:]
html = html.replace('const CHAVE = "resultados-kaique-2026-09-30";', 'const CHAVE = "resultados-kaique-2026-09-30-v2";')
html = html.replace("<h1>Editor de Impressão: o que já melhorou</h1>", "<h1>Editor de Impressão: em que pé estamos</h1>")
html = html.replace("<title>Editor de Impressão - resultados</title>", "<title>Editor de Impressão - resultados (30/09/2026)</title>")
dados = {}
for sec in SECOES:
    for n, _, _ in sec["itens"]:
        img = Image.open(BASE + "img2/" + n + ".jpg").convert("RGB")
        if img.width > 1500: img = img.resize((1500, int(img.height * 1500 / img.width)), Image.LANCZOS)
        b = io.BytesIO(); img.save(b, "JPEG", quality=78, optimize=True)
        dados[n] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
js = "const IMAGENS = " + json.dumps(dados) + ";\n"
html = html.replace("<script>\n", "<script>\n" + js, 1)
assert 'src="img/${img}.jpg"' in html
html = html.replace('src="img/${img}.jpg"', 'src="${IMAGENS[img]}"')
saida = "Editor-de-Impressao-resultados-2026-09-30.html"
open(saida, "w", encoding="utf-8").write(html)
print(sum(len(s["itens"]) for s in SECOES), "exemplos;", round(len(html.encode()) / 1e6, 1), "MB")
