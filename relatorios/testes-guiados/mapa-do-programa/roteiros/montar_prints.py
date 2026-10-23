"""Monta os prints recortados e legendados do mapa (relatorios/testes-guiados/mapa-do-programa/prints)
a partir dos prints brutos dos roteiros p1..p5 (fora do git). Coordenadas em pixels do print bruto
(janela de 1536 x 800 pontos = 1920 x 1000 px). Uso: python montar_prints.py"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendar import _fonte, lado_a_lado, recortar  # noqa: E402

B = Path(r"D:\programas\EditorImpressao-arquivos\mapa-do-programa-prints\brutos")
P = Path(__file__).resolve().parent.parent / "prints"
SAMUEL = Path(__file__).resolve().parent.parent.parent / "2026-10-23-sessao-0"


def r(nome, bruto, caixa, legenda, marcas=(), largura=1100):
    recortar(B / bruto, P / nome, caixa, legenda, marcas, largura)
    print("ok", nome)


def numerar_coluna(bruto, caixa, centros, destino, legenda, escala=2, lado="direita"):
    """Recorta uma coluna de ícones, aumenta e põe um número ao lado de cada ícone."""
    im = Image.open(B / bruto).convert("RGB").crop(caixa)
    im = im.resize((im.width * escala, im.height * escala), Image.LANCZOS)
    larg = max(im.width + 70, 720)
    folha = Image.new("RGB", (larg, im.height), "white")
    x_img = 0 if lado == "direita" else 70
    folha.paste(im, (x_img, 0))
    d = ImageDraw.Draw(folha)
    f = _fonte(26)
    for i, y in enumerate(centros, 1):
        yy = (y - caixa[1]) * escala
        x = im.width + 8 if lado == "direita" else 6
        d.rectangle((x, yy - 16, x + 50, yy + 16), fill=(230, 40, 40))
        d.text((x + 8, yy - 15), str(i), fill="white", font=f)
    tmp = B / "_tmp_coluna.png"
    folha.save(tmp)
    recortar(tmp, P / destino, None, legenda, largura=max(folha.width, 400))
    print("ok", destino)


# ---------------------------------------------------------------- 1. tela inicial
r("01-inicio-vazia.jpg", "p1-01-inicio-vazia.png", (0, 0, 1920, 560),
  "Tela inicial, sem livro nenhum. 1 = \"Abrir um PDF\" (clique ou arraste o PDF para cá). "
  "2 = \"Configurações\" e \"Ajuda\", no canto de cima.",
  [((26, 78, 686, 530), "1"), ((1655, 20, 1900, 62), "2")])
r("02-inicio-com-livro.jpg", "p2-01-livros-com-cartao.png", (0, 0, 1920, 400),
  "Tela inicial com um livro. 1 = \"Abrir um PDF novo\". 2 = o cartão do livro (um clique abre o livro na "
  "tela inteira; botão direito abre o menu do livro). 3 = o botão \"continuar\", em cima da capa (vai direto "
  "para a tela de conferir). 4 = \"procurar pelo nome\". 5 = \"Configurações\". 6 = \"Ajuda\".",
  [((26, 78, 268, 380), "1"), ((288, 76, 532, 380), "2"), ((434, 229, 522, 257), "3"),
   ((1356, 18, 1631, 61), "4"), ((1660, 25, 1795, 57), "5"), ((1815, 25, 1892, 57), "6")])
r("03-menu-do-cartao.jpg", "p2-02-menu-do-cartao.png", None,
  "Menu do botão direito no cartão (o mesmo do \"Mais...\" do livro aberto): continuar, começar de novo, "
  "renomear, abrir a pasta de saída (cinza até o livro gerar um PDF), remover da lista.", largura=400)
r("04-livro-aberto.jpg", "p2-03-livro-aberto.png", None,
  "O livro aberto na tela inteira (um clique no cartão). 1 = \"Voltar para os livros  Esc\". 2 = \"Mais...\". "
  "3 = \"Continuar\" (vai para a tela de conferir). 4 = \"Rodar o automático...\" (leva para a tela \"Marque o que "
  "você quer fazer\"; não roda nada sozinho). 5 = \"Ver todas as páginas\". 6 = \"Confirmar e processar...\". "
  "7 = jeitos de mostrar e de caber. 8 = \"página 1 de 180 · ir para\". Aqui as páginas são as do PDF como veio.",
  [((25, 15, 278, 63), "1"), ((1804, 15, 1895, 63), "2"), ((25, 78, 143, 125), "3"), ((154, 78, 360, 125), "4"),
   ((371, 78, 572, 125), "5"), ((583, 78, 805, 125), "6"), ((313, 948, 1213, 985), "7"), ((1515, 940, 1905, 995), "8")])
r("05-ver-todas-do-livro-aberto.jpg", "p2-05-ver-todas-as-paginas.png", (0, 0, 1920, 600),
  "\"Ver todas as páginas\" do livro aberto: a grade das folhas. Em cima: \"uma a uma\" / \"em pares\", "
  "\"todas\" / \"só as que precisam de atenção (0)\" e \"voltar ao livro\". Repare no (0): aqui ele não conta as "
  "dúvidas que a tela de conferir mostra.")

# ---------------------------------------------------------------- 2. o que fazer
r("06-opcoes.jpg", "p1-02-opcoes-fabrica.png", None,
  "\"Marque o que você quer fazer\" (abre ao abrir um PDF novo e pelo \"Rodar o automático...\"). 1 = a fila "
  "\"Receita\". 2 = as caixinhas (rolam para baixo). 3 = a frase do que vai ser feito. 4 = \"O livro, como está agora\" "
  "(folhear, \"tela cheia\"). 5 = \"voltar\". 6 = \"Conferir\" (é ele que faz o programa trabalhar sozinho).",
  [((84, 195, 1076, 245), "1"), ((84, 258, 1076, 815), "2"), ((58, 840, 1124, 894), "3"),
   ((1150, 175, 1862, 895), "4"), ((58, 918, 143, 965), "5"), ((1714, 913, 1862, 972), "6")])
r("07-opcoes-inteira-de-fabrica.jpg", "p1-03-opcoes-fabrica-inteira.png", None,
  "Todas as caixinhas de um livro novo, sem rolar (de fábrica): Dividir desmarcada; Limpar a folha marcada "
  "com o filtro Original (que \"não mexe na página\"); Achar gravuras e fotos marcada; Endireitar e Cortar "
  "as bordas marcadas; o resto desmarcado. Caixinha marcada = só o tique, sem quadrado.", largura=800)
r("08-opcoes-preto-e-branco.jpg", "p1-04b-opcoes-preto-e-branco-inteira.png", None,
  "Com o Preto e branco escolhido aparecem \"Só as letras\", \"Escurecer sozinho a força do preto...\" e "
  "\"Limpar a sujeira\". Achado 0-2: a do meio vem MARCADA e CINZA (só vale com \"Só as letras\").",
  [((20, 425, 1020, 465), "0-2")], largura=800)
r("09-opcoes-tudo-aberto.jpg", "p1-07-opcoes-tudo-aberto.png", None,
  "O que cada caixinha abre embaixo dela quando é marcada: Dividir abre \"Jeito de dividir\"; Endireitar abre "
  "\"Conta do endireitar\"; \"Achar a página dentro da borda preta\" abre \"Cortar: até a moldura / cortar fora\"; "
  "\"Margens iguais\" abre as quatro margens e o alinhamento; \"Montar cadernos\" abre \"páginas por caderno\".",
  largura=800)

# ---------------------------------------------------------------- 3. tela de conferir
r("11-conferir.jpg", "p3-01-conferir.png", None,
  "A tela de conferir. 1 = menus. 2 = coluna de ferramentas (esquerda). 3 = nome da ferramenta da vez. "
  "4 = girar a folha (canto). 5 = coluna de ícones dos painéis (direita; o número laranja = páginas com dúvida). "
  "6 = a faixa do aviso com \"está certo\" e \"próxima dúvida\". 7 = miniaturas (\"FOLHAS\", \"•••\", \"ver todas\"). "
  "8 = \"Confirmar e processar\". 9 = rodapé (folha, desfazer, refazer, histórico, contagem).",
  [((0, 0, 580, 46), "1"), ((2, 55, 54, 540), "2"), ((598, 6, 728, 44), "3"), ((1710, 60, 1850, 106), "4"),
   ((1868, 55, 1918, 320), "5"), ((56, 766, 1865, 814), "6"), ((56, 820, 1566, 960), "7"),
   ((1578, 871, 1852, 931), "8"), ((56, 965, 960, 1000), "9")])
numerar_coluna("p3-01-conferir.png", (0, 50, 56, 540), [73, 113, 153, 208, 248, 288, 328, 368, 421, 461, 515],
               "12-coluna-da-esquerda.jpg",
               "Coluna da esquerda, de cima para baixo: 1 Dividir a folha · 2 Cortar as bordas · 3 Endireitar · "
               "4 Retângulo [R] (e Oval [O]) · 5 Laço [L] (e Ponto a ponto [P]) · 6 Pincel [B] · 7 Varinha mágica [V] "
               "(e Pegar tudo desta cor [C]) · 8 Mover e mudar o tamanho da área [A] · 9 Zoom [Z] · 10 Mão [E] · "
               "11 Os quatro filtros. O nome só aparece ao parar o mouse em cima.")
numerar_coluna("p3-01-conferir.png", (1866, 50, 1920, 320), [120, 163, 209, 254, 299],
               "13-coluna-da-direita.jpg",
               "Coluna da direita, de cima para baixo (a seta \"»\" no alto esconde os ícones): 1 Para revisar (com o número "
               "de páginas com dúvida) · 2 Automático · 3 Propriedades · 4 Filtro da página · 5 Histórico. "
               "Um clique abre o painel; outro clique no mesmo ícone fecha.")
for n, (bruto, leg) in enumerate([
        ("p3-02-ferramenta-dividir.png", "Dividir a folha (1º ícone da esquerda): a linha azul \"arraste\" é onde a folha "
         "vai ser dividida. Ao escolher, abre sozinho o painel Propriedades: girar a folha, \"jeito\", \"não dividir "
         "esta\", \"usar em todas\" e \"mudar nas opções do livro...\". As miniaturas mostram FOLHAS."),
        ("p3-02-ferramenta-cortar.png", "Cortar as bordas (2º ícone): o retângulo verde é o corte. Propriedades: \"não cortar "
         "esta\", \"usar o corte do programa\", \"usar em todas\", \"tamanho...\", Espelhado (M), Proporção travada (T), "
         "\"Mover conteúdo\" (cinza), \"Linhas automáticas\", \"Qualidade da prévia\". As miniaturas passam a mostrar PÁGINAS."),
        ("p3-02-ferramenta-endireitar.png", "Endireitar (3º ícone): \"Inclinação desta página\" com os botões de 0,1°, "
         "\"deixar como veio\", \"usar o ângulo do programa\", \"Conta\" e \"Desentortar perto da lombada\". A página "
         "demorou a aparecer (\"Preparando a prévia...\")."),
        ("p3-11-os-quatro-filtros.png", "Os quatro filtros (último ícone da esquerda): a mesma página em Original, Preto e "
         "branco, Melhorar e Mágico pro; um clique escolhe o filtro desta página. Teclas 1, 2, 3, 4.")], 14):
    r(f"{n}-{Path(bruto).stem[3:]}.jpg", bruto, None, leg)
lado_a_lado([(B / f"p3-03-painel-{k}.png", (1490, 48, 1866, 1000), t) for k, t in
             (("revisar", "Para revisar"), ("automatico", "Automático"), ("props", "Propriedades"),
              ("filtro", "Filtro da página"), ("historico", "Histórico"))],
            P / "18-paineis-da-direita.jpg",
            "Os cinco painéis da coluna da direita, abertos um de cada vez (todos começam fechados). Para revisar: a lista "
            "das páginas com dúvida (Por página / Por motivo), \"ver a lista...\", \"está bom em tudo\". Automático: só "
            "MOSTRA as etapas ligadas neste livro e o botão \"Voltar para as opções\" (não tem botão de rodar). "
            "Propriedades: muda conforme a ferramenta. Filtro da página: os quatro filtros, Ajuste, Só neste pedaço, "
            "\"apagar página\", \"Aplicar em\". Histórico: o que foi feito, Desfazer/Refazer.", altura=800)
lado_a_lado([(B / "p3-04-antes-do-esta-certo.png", (56, 760, 1920, 1000), "antes do clique em \"está certo\""),
             (B / "p3-05-depois-do-esta-certo.png", (56, 760, 1920, 1000), "depois do clique")],
            P / "19-esta-certo.jpg",
            "Achado 0-3: \"está certo\" na folha 1 (Dividir a folha). Antes e depois do clique, a tela fica IGUAL: mesma "
            "frase na faixa, a miniatura 1 sem marca nova, o rodapé continua \"0 de 360 conferidas\", e o programa não "
            "vai para a próxima folha. Só a barra de espaço marca e avança.", altura=240, largura_max=1400)
r("20-proxima-duvida.jpg", "p3-06-depois-da-proxima-duvida.png", None,
  "\"próxima dúvida\" pulou da folha 1 para a folha 4 (miniatura com \"!\" laranja). A faixa fica laranja, com a "
  "frase da dúvida e o botão laranja da sugestão (aqui \"aceitar o corte\").",
  [((56, 766, 1865, 814), "")])
r("21-barra-de-espaco.jpg", "p3-07-depois-da-barra-de-espaco.png", None,
  "Barra de espaço na folha 1: o programa marcou e foi para a folha 2. Mesmo assim o rodapé continua "
  "\"0 de 360 conferidas\" (ele conta páginas, e no Dividir se confere folha).",
  [((56, 965, 960, 1000), "")])
r("22-ver-todas-na-conferencia.jpg", "p3-10-ver-todas.png", None,
  "\"ver todas\" (em cima das miniaturas, ou Ver > Todas as páginas): a grade de páginas, com as que têm dúvida "
  "em laranja e o motivo embaixo. \"voltar ao trabalho\" no canto. A tecla Esc NÃO volta (no teste, ficou na grade).")
r("23-filtros-tela-cheia.jpg", "p3-12-filtros-tela-cheia.png", None,
  "Ver > \"Filtros em tela cheia\" (ou o ícone de quadrado no título do painel Filtro da página): uma janela por "
  "cima, com os quatro filtros à esquerda, \"Comparar com o Original\", \"Aplicar em\", \"Fechar sem mudar\" e "
  "\"Usar <filtro>\".")
menus = ["Arquivo", "Editar", "Marcar", "Filtro", "Página", "Ver", "Painéis", "Ajuda"]
lado_a_lado([(B / f"p3-menu-{m}.png", None, m) for m in menus[:4]], P / "24-menus-1.jpg",
            "Menus do alto (1 de 2): Arquivo, Editar, Marcar, Filtro. Na tela \"Marque o que você quer fazer\" "
            "eles aparecem também, mas Editar, Marcar, Filtro, Página e Painéis ficam cinza.", altura=420)
lado_a_lado([(B / f"p3-menu-{m}.png", None, m) for m in menus[4:]], P / "25-menus-2.jpg",
            "Menus do alto (2 de 2): Página, Ver, Painéis, Ajuda.", altura=420)

# ---------------------------------------------------------------- respostas (b) e (c)
im4 = Image.open(SAMUEL / "image4.png").convert("RGB")
lado_a_lado([(im4, (0, 60, 300, 620), "print do Samuel"),
             (B / "p1b-de-conferir.png", (0, 48, 375, 750), "Dividir + Endireitar"),
             (B / "p1b-dc-conferir.png", (0, 48, 375, 750), "Dividir + Cortar"),
             (B / "p1-10-conferir-dividir-e-limpar.png", (0, 48, 375, 750), "Dividir + Limpar")],
            P / "b-icones-da-esquerda.jpg",
            "(b) A coluna da esquerda conforme as caixinhas. O print do Samuel (2 ícones: a folha aberta e um retângulo "
            "inclinado) é igual ao de Dividir + Endireitar, com \"Limpar a folha\" e \"Cortar as bordas\" desmarcadas. "
            "Com Dividir + Limpar aparecem 9 botões (Dividir, as ferramentas de marcar, Zoom, Mão e Os quatro filtros).",
            altura=520)
r("b-opcoes-dividir-e-endireitar.jpg", "p1b-de-opcoes.png", (40, 170, 1130, 900),
  "(b) As caixinhas que dão os 2 ícones do Samuel: Dividir e Endireitar marcadas, \"Limpar a folha\" e \"Cortar as "
  "bordas\" desmarcadas. A contagem bate com o print dele: \"58 com dúvida\". Marcada = só o tique, sem quadrado; "
  "desmarcada = quadrado vazio: fácil desmarcar \"Limpar a folha\" achando que está marcando.")
lado_a_lado([(B / "pdf-original-pag5.png", None, "PDF original, página 5"),
             (B / "p3-08-folha-5-dividir.png", (510, 87, 1410, 725), "\"Dividir a folha\", folha 5")],
            P / "c-folha-5.jpg",
            "(c) À esquerda, a página 5 do PDF aberta direto do arquivo; à direita, a mesma folha na tela \"Dividir a "
            "folha\". O texto já está em cima no PDF (\"PRIMERA PARTE\" cortado no alto): o deslocamento vem do scan, não "
            "do programa. Nesta folha o programa pôs a linha de dividir quase na beirada esquerda e avisa \"Não tenho "
            "certeza de onde cortar\".", altura=520)

# ---------------------------------------------------------------- 4. processar e pronto
r("26-antes-de-processar.jpg", "p4-01-antes-de-processar.png", None,
  "\"Confirmar e processar\" com dúvidas abertas: a janela \"Antes de processar\" lista as páginas e o motivo. "
  "\"ver\" leva à página marcada (não processa); \"está bom nas marcadas\" tira da lista; \"continuar assim mesmo\" "
  "segue. Repare nos números: aqui \"67 páginas (69 avisos)\"; o rodapé e o Para revisar dizem 56.", largura=720)
r("27-confirmar.jpg", "p4-02-confirmar.png", None,
  "Depois vem \"Confirmar e processar\": \"Salvar em\" (de fábrica, a pasta Documentos > Editor de Impressao), \"Escolher "
  "pasta\", \"Nome do arquivo\" (o nome do filtro entra no nome: \"- original.pdf\"), o aviso das páginas não "
  "conferidas, \"Gravar em duas camadas...\" e \"Processar\" / \"voltar\".", largura=850)
r("28-processando.jpg", "p4-04-processando.png", (0, 380, 1920, 650),
  "\"Processando o livro...\" com a barra, \"Página N de 360\" e \"cancelar\". Neste livro (360 páginas, filtro "
  "Original, endireitar e cortar) levou 11 minutos.")
r("29-ficou-pronto.jpg", "p4-05-ficou-pronto.png", (300, 320, 1620, 980),
  "A tela \"Ficou pronto!\": nome, páginas e tamanho do PDF e onde ficou. Botões: \"abrir a pasta\", \"imprimir "
  "agora\" (manda DIRETO para a impressora padrão, sem perguntar nada), \"montar para imprimir em A4 (com "
  "margens)...\" e \"fazer outro\". Os cadernos \"no tamanho do scan\" só saem se a caixinha \"Montar cadernos\" "
  "estava marcada (aí aparece aqui o \"Como imprimir\").",
  [((656, 902, 816, 952), "!")])
r("30-montar-para-imprimir.jpg", "p4-06-montar-para-imprimir.png", None,
  "\"montar para imprimir em A4 (com margens)...\": Formato (Livreto A4 deitada, na ordem dos cadernos), Papel, "
  "Folha, Tamanho, Escala, Rotação e Centralizar automáticos, Margens da encadernação (vêm das Configurações > "
  "Impressão), escala de cada lado; \"gravar o arquivo para imprimir\", \"mandar para a impressora\", \"fechar\".",
  largura=860)

# ---------------------------------------------------------------- 5. configurações, luz, área
for nome, i, leg in (
        ("31-configuracoes-atalhos.jpg", 2, "Configurações (botão no alto da tela inicial, ou Arquivo > Configurações...): as "
         "partes ficam na lista da esquerda (Aparência, Atalhos de teclado, Velocidade, Medidas e receitas, Impressão). "
         "Atalhos de teclado: clique numa tecla e aperte a nova."),
        ("32-configuracoes-velocidade.jpg", 3, "Velocidade: \"Páginas ao mesmo tempo\" (de fábrica, \"Todos os núcleos do "
         "processador\"). Só muda a velocidade, nunca o resultado."),
        ("32b-configuracoes-medidas.jpg", 4, "Medidas e receitas: \"Medidas em\" (centímetros, milímetros, polegadas) e "
         "\"Receita de todo livro novo\" (as receitas se guardam na tela \"Marque o que você quer fazer\")."),
        ("32c-configuracoes-impressao.jpg", 5, "Impressão: \"Margem da encadernação\" (10,0 mm) e \"A impressora não "
         "imprime\" (3,0 mm da beirada). São as margens que a janela \"montar para imprimir\" usa.")):
    r(nome, f"p5-01-configuracoes-{i}.png", (8, 38, 1264, 420), leg, largura=900)
r("33-ajuda.jpg", "p5-02-ajuda.png", None,
  "\"Ajuda\" (tela inicial) ou Ajuda > Lista de atalhos (F1): uma caixinha que só diz \"O que dá para fazer, e por "
  "qual tecla:\". A lista só aparece clicando em \"Show Details...\" (em inglês).", largura=400)
r("34-luz-mais-ajustes.jpg", "p5-04-filtro-pb-mais-ajustes.png", (1490, 48, 1866, 1000),
  "Onde ficou a Luz: painel \"Filtro da página\" (4º ícone da direita) > parte \"Mais ajustes\" (abre clicando na "
  "seta). Só aparece com Preto e branco, Melhorar ou Mágico pro (no Original não há \"Mais ajustes\"). A Luz é a "
  "última linha: \"Igualar a luz\", \"Suavizar\" e \"Tirar o chuvisco\", com os nomes cortados (\"Igual\", \"Suav\", "
  "\"Tirar o ch\").", [((1515, 755, 1830, 800), "Luz")], largura=420)
r("35-area-propriedades.jpg", "p5-05-propriedades-marcar.png", (1490, 48, 1866, 1000),
  "Onde ficou a \"Área\": com uma ferramenta de marcar (ex.: Retângulo, 4º ícone da esquerda), painel "
  "\"Propriedades\" (3º ícone da direita), lá no fim, depois de \"Marcar como\", \"Marcação desta página\" e "
  "\"Foto\": \"Mostrar as áreas achadas\" e os botões da área. Precisa rolar o painel para ver.",
  [((1500, 915, 1840, 1000), "Área")], largura=420)

# ---------------------------------------------------------------- (a) o automático
r("a-rodar-o-automatico-leva-aqui.jpg", "p2-06-depois-do-rodar-o-automatico.png", (0, 0, 1920, 1000),
  "(a) Depois do clique em \"Rodar o automático...\" (livro aberto): o programa vai para a tela \"Marque o que você "
  "quer fazer\" deste livro. Não roda nada sozinho; quem faz o programa trabalhar é o \"Conferir\" (6).",
  [((1714, 913, 1862, 972), "6")])
r("a-mudou-e-nao-valeu.jpg", "p2-07-conferir-de-fabrica-com-dividir.png", (0, 0, 1920, 1000),
  "(a) Cuidado: neste livro já conferido uma vez (só Dividir + Limpar), marquei também Endireitar e Cortar e cliquei "
  "\"Conferir\". A frase dizia \"vou dividir, endireitar e cortar\", mas a tela de conferir voltou igual: sem os "
  "ícones de Cortar e Endireitar na coluna da esquerda e com as mesmas 10 dúvidas. É o defeito de 29/09 da Lista de "
  "bugs (o trabalho salvo volta por cima das caixinhas).",
  [((2, 55, 54, 540), ""), ((1868, 90, 1918, 135), "")])
