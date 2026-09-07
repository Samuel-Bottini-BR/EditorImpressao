# Editor de Impressão — documento para colar no Claude

Atualizado em 07/09/2026. Reúne o que o programa é, tudo que já foi pedido, tudo
que já foi feito e o que falta. Serve para começar uma conversa nova sem perder
nada.

Pasta do projeto: `C:\Users\fotog\Desktop\EditorImpressao`

---

# PARTE 1 — O que é o programa

Aplicativo de desktop para Windows que **recupera PDFs de livros antigos
escaneados e os prepara para reimpressão em cadernos**. Projeto do Pe. Rosenei,
de um instituto de preservação de livros.

**Quem usa é o Kaique, impressor, sem formação técnica.** Toda a interface é em
português do Brasil, sem jargão: ele nunca vê "Sauvola", "k" ou "deskew" — vê
"Força do preto", "Melhorar", "girar a folha".

**Duas versões anteriores fracassaram.** Uma travava (feita em customtkinter), a
outra dava qualidade ruim (fórmula caseira de filtro). Daí vêm as regras rígidas
abaixo, e nenhuma delas é preferência de estilo: cada uma é cicatriz.

## As regras que não se negociam

- **PySide6, nunca tkinter.** Foi o que travou a versão anterior.
- **Uma página por vez na memória.** Ler, processar, escrever, soltar. O pico
  não pode crescer com o tamanho do livro; há livro de 300 MB no acervo.
- **Nenhum emoji em rótulo de interface.**
- **Textos de interface com acento. Caminhos de disco sem acento** — uma vez a
  pasta de saída sumiu da vista por causa disso.
- **Algoritmo consagrado em vez de fórmula própria.** A binarização é o Sauvola
  do DoxaPy, o mesmo caminho do ScanTailor.
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.

## Os quatro filtros

| Filtro | O que faz |
|---|---|
| Original | não mexe |
| Preto e branco | binarização local de Sauvola: tira o amarelado e o texto do verso |
| Melhorar | divide pelo fundo estimado: limpa a iluminação sem tocar na cor |
| Mágico pro | Melhorar + contraste local + cor + nitidez, para capas e gravuras |

## O fluxo

Arrasta o PDF → marca o que quer fazer → confere página a página → escolhe onde
salvar → processa. Atalhos: setas navegam, Espaço marca "está certo", Tab pula
para a próxima dúvida, 1 2 3 4 trocam o filtro, Ctrl+Z desfaz.

## As duas réguas

O projeto mede antes de mexer. São dois programas de medição:

- **`avaliar.py`** — a régua dos filtros. Roda sobre os nove livros do acervo e
  responde: alguma página saiu **pior** do que entrou? O critério de aceitação é
  que esse número seja **zero**.
- **`avaliar_selecao.py`** — a régua da seleção, criada em 06/08/2026. Mede se o
  programa acertou o que é gravura, o que é letra e o que é papel, em 26 páginas
  escolhidas.

## O protocolo de trabalho

**Medir antes, uma mudança por vez, medir de novo, reverter se qualquer número
piorar.** Se a mudança parecer valer a pena mesmo assim, não reverter por conta
própria: apresentar os dois resultados.

E antes de julgar qualquer resultado visual: **abrir todas as imagens.**
Percentual não é veredito. Essa regra existe porque já foi reportado "10 de 10
corretas" tendo olhado uma imagem — seis estavam erradas.

## Fronteira de autonomia

**Pode decidir sozinho:** limiar, janela, `k`, tamanho de bloco, ordem interna
de operações dentro de um filtro, troca de algoritmo de binarização, cache,
paralelismo, memória.

**Precisa perguntar antes:** criar ou remover filtro, mudar nome de filtro,
mudar qualquer tela, acrescentar ou tirar controle da interface, mudar o formato
dos arquivos de dados, alterar desfazer/refazer, trocar biblioteca.

## Onde ficam as coisas

```
core/filtros.py            os quatro filtros
core/selecao.py            as regiões marcadas (gravura, letra, papel)
core/detectar_regioes.py   acha sozinho o que é o quê
core/pipeline.py           a ordem: dividir, cortar, endireitar, filtrar, impor
core/cadernos.py           imposição e conferência da sequência
avaliar.py                 a régua dos filtros
avaliar_selecao.py         a régua da seleção
conferir.py                a tela de conferir amostras falando
relatorios/melhorias.md    o histórico de tudo que foi tentado, inclusive o que falhou
```

Acervo de teste: `Desktop\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE`, nove
livros, 2903 folhas. As queixas do Kaique estão na pasta antiga,
`Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros` — são `.txt` soltos com
um print ao lado, e **são fonte de requisito**.

Como rodar:

```
.venv\Scripts\python.exe main.py                 o programa
.venv\Scripts\python.exe -m pytest tests -q      os 150 testes
.venv\Scripts\python.exe avaliar.py              a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py      a régua da seleção
.venv\Scripts\python.exe conferir.py             conferir amostras falando
```

---

# PARTE 1B — Todas as funcionalidades: o que o app faz, o que falta

Lista mestra, cruzando a especificação original (18/07), os 68 pedidos feitos
desde então e uma conferência direta no código em 07/09/2026 — não só no que
este documento dizia. `[x]` feito e conferido, `[~]` parcial, `[ ]` falta.

## Processamento da página

- `[x]` Dividir a folha ao meio, detectando a lombada sozinho — corrigir
  arrastando a linha, "não dividir esta", "usar em todas", girar 90°
- `[x]` Endireitar sozinho (perfil de projeção, até ±5°, não mexe abaixo de
  0,1°) — ajuste manual arrastando o mouse, com linhas-guia
- `[x]` Cortar bordas sozinho, com alças arrastáveis na prévia
- `[x]` Apagar página, com opção de restaurar
- `[x]` Aplicar filtros diferentes em páginas diferentes, saindo num PDF só
- `[x]` Transformar uma capa inteira em página branca ("marcar como papel")
- `[~]` Filtro só numa parte da página — existe ("Filtro só neste pedaço", aba
  Marcar) mas nunca foi conferido ponta a ponta num livro real

## Os quatro filtros

- `[x]` Original / Preto e branco (Sauvola) / Melhorar / Mágico pro
- `[ ]` Escolher o binarizador certo por página — hoje usa um só para tudo;
  comparados os 18 do DoxaPy, não existe vencedor único
- `[ ]` Rubricação vermelha não virar barra preta no Preto e branco

## Ferramenta de seleção (aba Marcar) — conferido direto no código hoje

- `[x]` Marcar à mão: gravura, letra, papel (`core/selecao.py`)
- `[x]` Detecção automática das três (`core/detectar_regioes.py`,
  `core/rede_selecao.py`)
- `[x]` "Pegar tudo desta cor" (compara por matiz, não vaza como a varinha)
- `[x]` Marcar a folha inteira como papel = fica em branco
- `[x]` Selecionar por cor manualmente, para quando o automático errar
- `[~]` Reconhecer letra antiga — 23 de 26 na régua da seleção; os 3 que
  faltam pedem um modelo treinado em documento histórico (Eynollah, dhSegment
  ou Kraken/eScriptorium), o que por sua vez pede marcar 30-40 páginas à mão
  como gabarito primeiro

## Sistema de alertas (onze tipos — "o princípio central do app")

- `[x]` página colorida, lombada incerta, não parece dupla, muito torta,
  ângulo suspeito, em branco, escura demais, apagada demais, corte pegou
  conteúdo, resolução baixa, tamanho diferente
- `[x]` Contador clicável, miniatura laranja, faixa explicativa com botão de
  correção, painel "Páginas para revisar" agrupado por tipo, aviso antes de
  processar
- `[ ]` Critério "menos de 10% das páginas marcadas" nunca foi conferido —
  hoje só "ângulo suspeito" já passa de 12% do acervo

## Ajustes manuais

- `[x]` Medidores deslizantes: Força do preto, Intensidade, Clareza do fundo
  (0 a 100, prévia ao vivo)
- `[x]` Desfazer ilimitado gravado em arquivo, sobrevive fechar e reabrir

## Navegação e tela

- `[x]` Zoom, arrastar, atalhos (setas, Espaço, Tab, 1-4, R, Delete, Ctrl+Z,
  Ctrl+Shift+Z, Ctrl+Enter)
- `[x]` Modo comparar: dois filtros lado a lado, zoom sincronizado
- `[x]` Barra de rolagem preta
- `[x]` Regras de fundo respeitadas: sem emoji, acento certo, PySide6

## Salvar o resultado

- `[x]` Escolher pasta, editar nome, lembrar última pasta usada, avisar
  duplicata ou pasta sem permissão

## Cadernos (o objetivo final)

- `[x]` Montar cadernos (imposição), caminho rápido sem rasterizar quando só
  isso está marcado
- `[x]` Conferir a sequência simulando a dobra
- `[ ]` Critério "filtros diferentes por página, um PDF só" nunca foi
  conferido ponta a ponta num livro de verdade

## Instalador

- `[x]` Inno Setup: instala em Arquivos de Programas, atalhos, aparece em
  Adicionar/remover programas, assistente em português, desinstalador

## Medição e testes (para o Claude, não para o Kaique)

- `[x]` `avaliar.py` (régua dos filtros) — 4 motivos de reprovação restantes,
  3 deles a mesma página (Graduale 126, uma partitura manuscrita)
- `[x]` `avaliar_selecao.py` (régua da seleção) — 3 de 26 restantes
- `[x]` `conferir.py`, com ditado por voz (Win+H)
- `[ ]` Falta um número na régua: "guardou a sujeira" — o Otsu passa zero
  pioras mas guarda o dobro de tinta do Sauvola, e nenhum critério pega isso
- `[ ]` **A pergunta decisiva, pendente desde 18/07:** comparar com o
  CamScanner nas 5 páginas difíceis já preparadas em `para_comparar/`, e
  responder em uma frase — sim, não, ou ainda não substitui

---

# PARTE 2 — Tudo que eu já pedi

Recuperado dos transcritos de todas as conversas.

## 18/07/2026 — a especificação original

O pedido nº 1 foi uma especificação de 40 mil caracteres. Ela não é "um pedido":
é **a lista de funcionalidades do programa**, e vale reler inteira. O essencial:

**O que o programa tem de fazer**

- **Dividir folhas ao meio** — detectar a lombada, e deixar corrigir na mão.
- **Os três filtros**, com receita definida: Preto e branco por Sauvola/Wolf do
  DoxaPy; Melhorar por divisão pelo fundo estimado; Mágico pro por CLAHE no L do
  LAB + saturação + nitidez + empurrão do branco.
- **Endireitar** por perfil de projeção, limitado a ±5°, sem mexer abaixo de 0,1°.
- **Montar cadernos** com duas páginas por folha já no PDF, para o Kaique só
  mandar imprimir frente e verso sem configurar nada no Acrobat. E um **caminho
  rápido**: se só a imposição estiver marcada, copiar as páginas sem rasterizar.

**O sistema de alertas — "o princípio central do aplicativo"**

> "O programa faz tudo sozinho, mas é honesto sobre onde teve dificuldade. O
> usuário não deve conferir 500 páginas uma a uma — deve conferir só as que o
> programa marcou."

Onze tipos de alerta especificados: página colorida, lombada incerta, não parece
dupla, muito torta, ângulo suspeito, em branco, escura demais, apagada demais,
corte pegou conteúdo, resolução baixa, tamanho diferente. Com contador clicável
no topo, miniatura laranja, faixa explicativa com botão de correção, **painel
"Páginas para revisar" agrupado por tipo**, e aviso antes de processar.

> "**Nunca alertar à toa.** Num livro bem escaneado, menos de 10% das páginas
> devem ser marcadas. Se o programa marcar tudo, o alerta perde a função."

**Ajustes manuais — "o automático propõe, o usuário corrige"**

Força do preto; cortar bordas com **alças arrastáveis**; apagar páginas com
opção de restaurar; **ajustar o ângulo arrastando o mouse**, com linhas-guia; e
**desfazer ilimitado gravado em arquivo** (JSON Lines, uma ação por linha),
que sobrevive a fechar e reabrir o programa.

**Os 15 critérios de aceitação.** Entre eles, dois que ainda pesam hoje:

> 6. É possível **aplicar filtros diferentes em páginas diferentes** do mesmo
>    livro, gerando um PDF só.
> 8. Num livro bem escaneado, **menos de 10%** das páginas são marcadas para
>    revisão.

## 18/07/2026 — depois da especificação

2. "sim, siga no modo automatico e faça todo app"
3. "você terminou?" / "onde está o arquivo .exe?"
4. **Instalador de verdade**, não só o portátil: Inno Setup, instala em Arquivos
   de Programas, atalho no menu Iniciar e na área de trabalho, aparece em
   "Adicionar ou remover programas", assistente em português, desinstalador.
5. **Escolher onde salvar o PDF**: botão, campo com o caminho, editar o nome,
   lembrar a última pasta, avisar se o arquivo já existe, avisar se a pasta não
   tem permissão.
6. **Corrigir o travamento** dos botões da tela de conferir — nenhuma exceção
   pode fechar a janela.
7. **Corrigir o layout sobreposto**: a caixa azul e os botões desenhados por
   cima da imagem. QVBoxLayout de verdade, sem `setGeometry`.
8. "TESTE VOCÊ MESMO antes de me entregar."
9. **Ampliar a página em tela grande**: zoom com a roda, arrastar, setas mudam
   de página, 1 2 3 4 trocam de filtro, **modo comparar** com dois filtros lado
   a lado e zoom sincronizado, imagem gerada em resolução maior.
10. **Separar ajustes de ações** e trocar os três botões por **medidores
    deslizantes** — Força do preto, Intensidade, Clareza do fundo, 0 a 100 com
    50 no meio, com o texto em palavras e prévia ao vivo.
11. **Acentos** — "já pedi duas vezes e continua errado".
12. Bateria de testes com PDFs reais, com imagens comparativas dos quatro
    filtros nas páginas mais difíceis.
13. **O prompt de testes** (9 mil caracteres), que definiu os quatro casos que
    são o critério de sucesso do Kaique, ficha escrita por livro, testes por
    função, testes de robustez, e:

    - **Atenção especial** a manuscritos iluminados, xilogravuras, bleed-through
      e aos arquivos grandes (memória).
    - **A comparação com o CamScanner como teste decisivo** — "é o que o Kaique
      usa hoje, é a régua real". Pediu 5 páginas difíceis exportadas antes e
      depois, numa pasta `para_comparar/`.
    - **Como quer o retorno:** *"Seja crítico e honesto. Não suavize resultado
      ruim. Ao final, me diga em uma frase: o programa já substitui o CamScanner
      para o trabalho do Kaique? Sim, não, ou ainda não."*

    A pasta `para_comparar/` existe e tem as dez imagens. **A pergunta final
    nunca foi respondida** — está na lista do que falta.

## 29/07/2026 — as queixas do Kaique entram

13. "faça um resumo do programa para o claude que eu possa colar lá na conversa"
14. "olhe a pasta `BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros`, veja o que eu
    escrevi nos blocos de notas e compare as fotos, para ver quais problemas
    quero resolver"

## 01/08 a 04/08/2026 — filtros e jeito de trabalhar

15. **"eu quero que o papel saia branco, e o desenho também saia perfeito."**
16. **"seja mais direto"** — o jeito de escrever estava difícil de entender.
17. Notificação pop-up quando tiver novidade, e só quando precisar de resposta.
18. Ver algum tipo de carregamento no terminal enquanto trabalho.
19. **"vai consertar os filtros e depois a gente volta para parte de seleção."**
20. **"por favor, confira os testes que você fez sozinho, não vou ter como fazer
    isso."**
21. "manda print dos testes para eu ver"

## 04/08 a 07/08/2026 — esta rodada

Aqui vai **tudo**, inclusive as mensagens curtas, porque várias delas são
correção de rumo e valem mais que os pedidos longos.

22. "vamos continuar o trabalho do editor de impressão"
23. *(resposta a uma pergunta minha)* **conferir a página de imagens primeiro**,
    antes de mexer em qualquer coisa
24. *(resposta a uma pergunta minha)* **corrigir os textos e commitar**
25. **"porque você continua travando, porque não vai até o final?"**
26. Resumo em `.md` com os pedidos, as perguntas, os prints e o que falta
27. "você esqueceu de colocar os meus pedidos que eu fiz ao longo da conversa no
    relatório — só me dá um relatório em md para eu mandar para o Claude"
28. "procure todos os pedidos que eu já fiz para colocar no relatório"
29. **"o que falta agora? porque você parou?"**
30. "ok, o que falta fazer ainda de tudo que eu já pedi e apontei?"
31. **"muita coisa para eu ler, seja mais conciso — fale em quatro linhas o que
    eu preciso escolher"**
32. **"continue 1 e depois 2 e termine tudo, só me chame quando terminar tudo"**
33. "pera aí, faz um resumo pra mim"
34. **"não entendi do que você está falando, seja mais simples"**
35. "o que falta fazer?"
36. **"conserta todas essas coisas e só volta a me chamar quando terminar"**
37. "a ferramenta de seleção está finalizada também?"
38. **Continuar os testes do selecionador**, pesquisar como se treina esse tipo
    de coisa, procurar repositórios e ver **como Photoshop e Adobe PDF fazem**,
    **parar só com 99% de certeza**, deixar amostras na pasta de testes, e
    depois **juntar seleção e filtro para aplicar filtro só numa parte
    selecionada, ou melhorar o trabalho de um filtro**.
39. **"consegue ativar o modo voz?"**
40. **Modo voz dentro do Claude**, para eu ir olhando os prints e falando o que
    está errado, e você ir anotando conforme o print que está na tela.
41. **Opção de transformar uma capa em branco.**
42. "pode continuar mexendo no programa — precisa treinar o programa poder
    selecionar cores né? e também letras antigas."
43. **"eu quero que ele reconheça cores mesmo, para eu ter uma ferramenta a mais
    de seleção, para eu poder selecionar por cor quando o programa der errado."**
44. "sim, pode continuar"
45. **"resolva"**
46. Este documento: resumo de tudo, com o prompt inicial bem explicado.

## Os pedidos que valem como regra permanente

Estes seis não são tarefa: são o modo de trabalhar. **Quem pegar este projeto
deve ler esta lista primeiro.**

- **"seja mais direto"** e **"seja mais conciso — em quatro linhas"** — texto
  curto no chat. O detalhe vai para arquivo, não para a conversa.
- **"não entendi do que você está falando, seja mais simples"** — e não é o
  mesmo que ser curto. É falar em português comum: "o programa estava estragando
  a capa dos livros", e não "o balanço de branco eleva o ruído de 5,5 para 17,5".
  O número entra depois da frase que se entende, nunca no lugar dela.
- **"confira os testes que você fez sozinho, não vou ter como fazer isso"** —
  abrir todas as imagens antes de dizer que funcionou. Percentual não é veredito.
- **"porque não vai até o final?"** — decidir sozinho dentro da alçada e
  executar o protocolo inteiro, em vez de parar a cada passo perguntando por
  onde seguir.
- **"vai consertar os filtros e depois a gente volta para a seleção"** — a ordem
  de trabalho combinada.
- **"eu quero que o papel saia branco, e o desenho também saia perfeito"** — o
  critério final, em uma frase.

---

# PARTE 3 — As dez queixas do Kaique, e onde está cada uma

| Queixa, nas palavras dele | Situação |
|---|---|
| "as letras estão ficando pixeladas, precisamos que fiquem mais arredondadas" | **Feito e conferido na imagem** |
| "o mágico pro está deixando muito pixelado a imagem" | **Feito e conferido** |
| "às vezes a parte de trás fica com uma mancha da parte da frente" | **Feito e conferido** |
| "o programa não localizou as bordas corretamente" | **Feito e conferido em dois casos** |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | **Feito** — trocado o limiar global por Sauvola local |
| "colocar botão clicável nas páginas que o programa não tem certeza" | **Existe** |
| "a barra de scroll devia ser preta" | **Feito em 06/08** |
| "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | **Feito em 06/08** — o programa simula a dobra e confere |
| "no mágico pro o fundo deveria remover o amarelado e deixar totalmente branco" | **Em grande parte feito**; ver o que falta |
| "queremos que fique branco a página e só as letras pretas" (Preto e branco) | **Atendido em número**, mas falta escolher o binarizador por página |

---

# PARTE 4 — O que foi feito nesta rodada (04 a 07/08/2026)

São 12 commits. O placar: **a régua dos filtros saiu de 27 motivos de
reprovação para 4**, e a seleção ganhou régua própria e está em 23 de 26.

## Os filtros

**A causa do fundo que escurece, achada e medida.** Sete das oito reprovações
vinham de um passo só: o realce de cor do Mágico pro multiplica o S do HSV
mantendo o V — isso preserva o brilho, mas não a luminância, e papel velho é
sempre amarelo-pardo. Três saídas foram implementadas e medidas no acervo
inteiro (cor em LAB, cor em YCrCb, devolver o cinza pixel a pixel) e **as três
foram revertidas**: todas consertavam o papel e engrossavam a rubricação
vermelha, que é entupimento de letra — o defeito mais grave que existe aqui.
O que resolveu foi não realçar quando a única cor da folha é o amarelado do
próprio papel: papel velho é sempre âmbar, uma capa colorida pode ser de
qualquer matiz.

**A capa não é papel.** Depois que o detector passou a marcar capa como gravura,
as capas caíram no caminho de branqueamento — e numa capa não há papel a
branquear, o que ali parece papel é o couro. Três passos tiveram de sair, e cada
um custou uma medição própria:

| Passo retirado | Medido |
|---|---|
| branqueamento e ponto de preto | ruído do Boécio 5,5 → 17,5 |
| achatamento da iluminação | couro verde do Horas 219 → 194 |
| recomposição da rampa | couro vermelho do Graduale 47,4 → 43,9 |

## A régua

**A rampa da borda passou a ser rampa de verdade.** Ela contava pixels de tom
intermediário perto do contorno, e o grão do papel entrava na conta: limpar o
papel — que é o certo — aparecia como estragar a letra. Agora é contraste
dividido pela inclinação, medida em cima do contorno, e sai em pixels. Validada
contra casos extremos: imagem binarizada dá exatamente 1,00, desfocada com sigma
4 dá 3,19.

**A régua parou de medir letra onde não há letra.** Uma estampa colorida de
página inteira era reprovada por "as letras entupiram" — numa página sem uma
letra. As páginas em que a régua afrouxa saem **nomeadas** no relatório, de
propósito.

**Um erro meu, achado abrindo as imagens.** A primeira versão dessa regra
desligava a cobrança em 30 das 63 páginas medidas, incluindo uma partitura
manuscrita cheia de texto. Apertei a regra e caiu para 13, e abri as treze.

## A seleção

**Ganhou régua própria** (`avaliar_selecao.py`), com 26 páginas e uma expectativa
escrita olhando cada uma.

**O defeito que ela achou de cara: o Preto e branco apagava a capa dos livros.**
Página sem marcação nenhuma é binarizada inteira — a capa de pergaminho do
Boécio saía uma folha branca, sobrando só a etiqueta da biblioteca. A regra
antiga do projeto mandava o contrário do que devia. Capa e folha em branco pedem
coisas opostas, e isso foi medido: sem marcação a capa some e a folha em branco
vai a branco; marcada como gravura a capa sai inteira e a folha para no creme.
O detector passou a perguntar se aquilo é **objeto ou folha** — objeto tem
textura, ou está sobre fundo mais escuro.

## Ferramentas novas

**"Pegar tudo desta cor"** — a sétima ferramenta da aba Marcar. Clica numa cor e
ela pega **tudo daquela cor na página**, não só a mancha onde clicou. A varinha
antiga é preenchimento por semente: na partitura do Graduale ela vaza pelo
pergaminho e leva 99,8% da folha. A nova pega 7,7% — as vinte pautas vermelhas e
as letras rubricadas. Compara só o **matiz**, então a parte iluminada e a parte
na sombra da mesma tinta contam como a mesma cor.

**"Filtro só neste pedaço"** — a folha inteira vai a Preto e branco e a gravura
fica no Original. Testado na xilogravura da Rhetorica: o texto sai com 2 tons e a
gravura mantém os 256 da hachura.

**Marcar a folha inteira como papel = folha em branco.** Serve para a capa que
não se quer no livro reimpresso. Sai com zero pixels que não sejam brancos.

**A tela de conferir** (`conferir.py`) — mostra as amostras uma a uma, com uma
caixa para dizer o que está errado. A caixa aceita o **ditado do Windows: Win+H
e falar**. Nenhuma biblioteca nova entrou por causa disso.

## Fora da imagem

**A barra de rolagem ficou preta**, a pedido do Kaique.

**A sequência dos cadernos passou a ser conferida**, e não só instruída: o
programa simula a dobra e verifica que a leitura sai 1, 2, 3 até o fim, que as
folhas saem em pares de frente e verso, e que nenhuma página sumiu ou repetiu. O
resultado aparece na tela final, em verde ou em vermelho com "não imprima assim".

**Um travamento sério consertado:** o gerador de relatório entrava em laço
infinito com tabela grande e deixava um PDF de zero byte. O `Story` do PyMuPDF
devolve "ainda tem mais" sem consumir nada quando um elemento não cabe. Isso
podia travar o programa na mão do Kaique, sem mensagem e sem fim.

**O aviso "tem cor" parou de ser decidido na navalha.** O limiar de 5% caía
dentro da faixa das páginas coloridas: a estampa do Catecismo dá 0,0499 a 150
DPI e 0,0500 a 300. Passou para 2%, no meio do vão medido.

---

# PARTE 5 — O que falta

## 1. A régua dos filtros: 4 motivos

- **Três são a mesma página** — a 126 do Graduale, uma partitura manuscrita que
  o detector marca como desenho. O ruído sobe porque ela é tratada como gravura.
  **Conserta-se consertando a detecção.**
- **Um é o Pesel 76** — o fundo escurece de 156 para 148 no Mágico pro.

## 2. A régua da seleção: 3 de 26

As três têm a mesma raiz: o modelo de layout foi treinado em documento moderno.

- **Graduale 126** — partitura manuscrita marcada 100% gravura.
- **Siebmacher 45** — as legendas impressas da prancha não viram letra.
- **Pesel 73** — o título impresso sai como foto; as quatro legendas do pé, não.

**Cinco sinais foram medidos para separar escrita antiga de foto** — pedaços de
glifo, papel à vista, meio-tom, periodicidade do perfil de linhas e uniformidade
da parte clara — e **em todos os cinco os números das duas se cruzam**. Está
tudo em `relatorios/melhorias.md`, para ninguém repetir.

Como não dá para decidir pela imagem, o programa agora **admite a dúvida**: a
página fica laranja com "Desenho ou escrita? Não tenho certeza. Confira na aba
Marcar". Acende em 2 de 7 páginas testadas — as duas genuinamente difíceis.

**O conserto de verdade é somar um modelo treinado em documento histórico.** A
pesquisa apontou três abertos que fazem exatamente isso: **Eynollah**,
**dhSegment** e **Kraken/eScriptorium**. E existe dataset anotado pixel a pixel
para validar: o **DIVA-HisDB**, 150 páginas de manuscritos medievais da
competição ICDAR 2017.

## 3. A rubricação vermelha virando preta

No Preto e branco, a rubricação vermelha do Graduale e do Livro de Horas vira
barra preta. A causa suspeita já está escrita: a conversão para cinza trata
vermelho como escuro, e o DoxaPy oferece oito métodos de conversão a investigar.

## 4. Escolher o binarizador por página

Foram comparados os 18 binarizadores do DoxaPy em 36 páginas. A conclusão: **não
existe vencedor único**. No Palatino, de letra gótica pesada, o Otsu sai sólido
enquanto o Sauvola quebra o traço; noutras páginas se inverte. Hoje o programa
usa um só para tudo.

## 5. Falta um número na régua: "guardou a sujeira"

O Otsu marca zero pioras mas guarda o dobro de tinta do Sauvola — em papel
envelhecido isso quer dizer manter a mancha como se fosse letra, e **nenhum
critério atual pega isso**. Enquanto esse número não existir, a régua pode
aprovar o filtro errado.

## 6. A pergunta que ficou sem resposta desde 18/07

No prompt de testes você pediu, com todas as letras:

> "Ao final, me diga em uma frase: **o programa já substitui o CamScanner para o
> trabalho do Kaique? Sim, não, ou ainda não.**"

**Isso nunca foi respondido.** A pasta `para_comparar/` foi montada, com as dez
imagens — as cinco páginas difíceis antes e depois — mas a comparação lado a
lado com o CamScanner nunca foi feita nem o veredito dado.

É o teste que você chamou de decisivo, e é o único que mede o programa contra o
que o Kaique usa hoje. Devia vir antes de qualquer refinamento novo.

## 7. Dois critérios de aceitação que ainda não foram conferidos

Dos quinze da especificação original, estes dois nunca foram medidos:

- **"menos de 10% das páginas marcadas para revisão"** — hoje o acervo tem 349
  páginas com "ângulo suspeito" e 305 com "tem cor" em 2903 folhas. Só o
  primeiro já passa de 12%. O alerta corre o risco de virar ruído, que é
  exatamente o que a especificação mandava evitar.
- **"aplicar filtros diferentes em páginas diferentes, gerando um PDF só"** — o
  filtro é por página no modelo de dados, mas isso nunca foi conferido ponta a
  ponta num livro de verdade.

## 8. O caminho para treinar

Para reconhecer letra antiga o programa precisa de gabarito, e **a aba Marcar já
é a ferramenta que o produz**: cada página corrigida à mão é um exemplo do
certo. O caminho combinado:

1. Marcar à mão 30 ou 40 páginas difíceis, das que ele erra.
2. Guardar essas marcações como gabarito.
3. Com gabarito dá para **medir de verdade** — Interseção sobre União por
   classe, que é como a competição ICDAR avalia — em vez de julgar no olho.
4. E aí dá para treinar, ou validar um dos três modelos prontos.

O passo 1 é o único que o programa não faz sozinho.

---

# Estado hoje

- **150 testes** automatizados passam.
- **20 de 20 casos de robustez**: PDF corrompido, protegido por senha, arquivo
  que some no meio, disco cheio, livro de 1010 páginas, cancelar no meio. Em
  nenhum o programa fecha, e em nenhum se perde trabalho.
- **57 commits**, cada um com o defeito que resolveu escrito por extenso.
- Memória sob controle: o pico não cresce com o tamanho do livro.
