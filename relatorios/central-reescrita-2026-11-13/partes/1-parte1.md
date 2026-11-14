## Parte 1: as perguntas que destravam consertos (8 perguntas mudaram)

Arquivos: `novas/perg-revisao-codigo.json` (4), `novas/acrescentei-27-10.json` (3 das 37; as outras 34 iguais),
`novas/perg-mover-rotulo.json` (1).

Em todas: a primeira frase diz o que é e onde fica, com o caminho de clique; saíram os números de decisão do meio do
texto (ficam só no fim, entre parênteses, "para consulta"), "motor", "escolha da gerente" e as citações longas do
Livro; entrou "O que muda no que já funciona", "Situação" e "O que você escolhe"; cada opção diz o que acontece.

### rev-usar-em-todas ("usar em todas" deixa de fora as páginas mexidas à mão?)
- **Mudou:** título e texto; o nome do botão em cada ferramenta ("usar em todas" / "aplicar em: todas"); o caso real
  numa frase por ferramenta; **acrescentei o que muda no que já funciona**: com "Sim", no Girar a página virada à mão
  deixa de acompanhar as outras (muda em parte a decisão de 06/10, "Todas ficam viradas como a folha da vez"). Isso
  não estava dito e é regra 6 / D-605.
- **Por quê:** ele ainda não respondeu; o texto antigo tinha um parágrafo só de citações com números (D-090, D-091,
  D-545, D-035, D-667), o padrão de "Não sei de que obra está falando" e "Não se deve usar código na nomeação".
- **Prints:** os de 10/11 continuam valendo (conferi: nenhuma mudança no código do "usar em todas" desde então). Já
  estão no modelo do girar (azul antes, laranja como é hoje, verde a outra opção).

### rev-letra-clara-todas ("Letra clara em fundo escuro" vai junto no "Aplicar em: todas"?)
- **Mudou:** título e texto; onde fica a caixinha ("Mais ajustes" do painel "Filtro da página"); "é defeito";
  **acrescentei**: com "Sim", a caixinha vai como está na página da vez, então também DESMARCA nas outras se nela
  estiver desmarcada (é como o Automático já faz: conferido em `core/automatico.py`, que grava o valor em todas as
  páginas em que roda).
- **Conferido no programa hoje:** a lista do "Aplicar em" (`ui/tela_conferir._campos_do_aplicar_em`, juntada em 13/11)
  ainda não tem a caixinha. O fato da pergunta continua verdadeiro.

### rev-dividir-grade-linha (o "dividir" da grade corta onde você deixou a linha?)
- **Mudou:** título e texto; "linha do motor" virou "onde o programa acha a lombada" (também nas legendas); tirei a
  afirmação de que o "dividir todas" também corta na linha arrastada (não conferi); acrescentei que na folha sem linha
  arrastada nada muda.

### rev-girar-grade (o girar da grade deixa todas viradas do mesmo jeito?)
- **Mudou:** título ("como a página da vez" na grade é ambíguo: na grade não há página da vez; troquei por "todas
  viradas do mesmo jeito"); acrescentei a perda: quem usa a grade para girar cada página ¼ a partir de onde está perde
  esse jeito com "Sim".

### b-abas-nomes (os nomes curtos das abas do "Abas no alto")
- **Motivo:** "Ainda não entendi" + "No caso, isso é uma opção a mais do que a que temos hoje?" (06/11). A gerente
  respondeu no chat da pergunta em 07/11, mas a pergunta continuou igual (com o código de rodada
  `7-paineis-da-direita-opcao-1`, "402 C" e "D-033" no texto).
- **Mudou:** responde primeiro a dúvida dele ("Não: já existe hoje; é um dos quatro jeitos que você pediu em 05/10");
  diz onde fica (menu Ver > Lado direito) e que o de fábrica é outro ("Ícones na borda"); diz com todas as letras que
  os nomes curtos foram escolhidos por um agente sem perguntar a ele (regra 9).
- **Opção nova:** `nomes-inteiros` ("As abas com o nome inteiro do painel"), como segunda sugestão de nome (regra 6:
  duas ou três opções de nome). Avisa que precisa conferir se cabe em 1280 de largura.
- **Print novo:** `b-abas-nomes-resumo.png`: o menu Ver > Lado direito (versão de teste, hoje), o lado de fábrica
  (Gradus, cópia, hoje) e o "Abas no alto" (print de 28/10, Palatino).
- **Achado ao tirar o print (não confirmado em janela de verdade):** no programa de hoje, sem janela na tela, ao
  trocar para "Abas no alto" a barra de menu (Arquivo, Editar...) some: `menuBar().isVisible()` = falso, nas duas
  vezes que tentei (`cru/p2/e-abas-no-alto.png`, `cru/p3/4-abas-depois-de-redimensionar.png`). No print de 28/10 ela
  aparecia. Pode ser só do modo sem tela; precisa conferir na janela de verdade. Por isso usei o print de 28/10 nessa
  faixa.

### b-pdf-desatualizado (o cartão deve dizer "PDF desatualizado"?)
- **Motivo:** "Ainda não entendi" + "Isso se aplica só se eu fizer alterações né?" (06/11).
- **Mudou:** responde primeiro ("Sim, só quando você muda alguma página; folhear não conta", conferido na regra do
  programa `ui/janela_principal._ver_se_o_pdf_ficou_velho`); diz que não é defeito, de onde veio (o conserto que ele
  mandou em 05/10), que "PDF desatualizado" é coisa nova e o que muda em cada opção. Tirei o "etapa 9b-1", "Lista de
  bugs 332" e "D-309" do meio do texto.
- **Print novo:** `b-pdf-desatualizado-resumo.png`, montado com os prints de 28/10 (a regra do programa não mudou
  desde então), cortados só na barra do alto e no cartão, para tirar as páginas cinzas ainda carregando e o botão
  cortado "ontinua" que distraíam.

### v-capa-aviso (pares trocados: quando o programa avisa?)
- **Motivo:** comentário de 13/11: "mas vai ter um botão para fazer isso antes do imprimir livros?"
- **Mudou:** responde primeiro: sim, o botão que ele mandou fazer em 09/11 vai ficar no "Duas lado a lado" e ele usa
  quando quiser, antes de "Montar para imprimir"; ainda não está feito. **Acrescentei que já hoje dá para acertar à
  mão**: botão direito na miniatura da capa, "adicionar página em branco depois" (função que ele testou em 09/11:
  "pagina em branco funciona"). Disse como o Acrobat faz (a escolha de mostrar a capa sozinha no modo de duas páginas).
- **Print novo:** `v-capa-aviso-resumo.png` (La vida eterna, cópia, dividido pelo Automático, "Duas lado a lado"):
  azul, a página 7 impressa à esquerda; verde, o menu do botão direito e, depois do clique, a 7 à direita.
- **Não conferido:** que a página em branco anda também os cadernos do "Montar para imprimir". Está escrito no
  Livro (D-623: "entra no livro, no PDF e nos cadernos") e ele testou a página em branco, mas não montei os cadernos
  deste livro.

### mover-rotulo-antes (o Mover com o "antes / depois")
- **Motivo:** "Ainda não entendi" + "Isso ficou bem estranho né, acho que não deveria dar para ver o antes/depois
  enquanto se mexe na folha, no caso do mover." (07/11). A pergunta antiga era sobre o lugar do rótulo; o comentário
  dele pede outra coisa.
- **Mudou:** título, texto e opções. Diz o que é o "antes / depois" e o Mover, como é hoje (o que ele aprovou em
  04/11) e que as opções novas mudam essa decisão só no Mover.
- **Opções novas:** `so-a-pagina` ("Com o Mover, só a página", sugestão) e `some-ao-arrastar` (a proposta da
  gerente de 07/11). As antigas `fica` e `mudar` continuam, com texto mais claro.
- **Print novo:** `mover-rotulo-antes-resumo.png` (Gradus, cópia, dividido, página 11, ferramenta Mover): azul, com
  "antes / depois" ligado; verde, só a página.

### Fatos que não consegui confirmar no programa (Parte 1)
1. Cadernos com a página em branco posta à mão (v-capa-aviso): não montei os cadernos; vale o Livro e o teste dele.
2. "dividir todas" com a linha arrastada (rev-dividir-grade-linha): não conferi; tirei a frase.
3. Se as abas com o nome inteiro cabem na coluna da direita em 1280 de largura (b-abas-nomes): escrito como algo a
   conferir antes de fazer.
4. A barra de menu que some no "Abas no alto" sem tela: não conferi na janela de verdade.

