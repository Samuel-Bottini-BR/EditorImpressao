# Editor de Impressão — relatório completo

Escrito em 07/08/2026. Tem duas coisas dentro:

1. **Todos os pedidos que o Samuel fez**, do primeiro ao último, palavra por
   palavra, tirados dos transcritos de todas as conversas. São 68.
2. **O relatório do trabalho**: o que o programa é, o que foi feito, o que falta.

Os dois documentos gigantes — a especificação original e o prompt de testes —
estão inteiros nos apêndices, no fim.

Pasta do projeto: `C:\Users\fotog\Desktop\EditorImpressao`

---

# PARTE 1 — Todos os pedidos, palavra por palavra


## Pedido 1 — 18/07/2026 14:53

*Documento longo (40,566 caracteres). Está inteiro no **Apêndice A — A especificação original**, no fim deste arquivo.*

> # Editor de Impressão — especificação completa e prompt para o Claude Code


## Pedido 2 — 18/07/2026 14:58

> sim, siga no modo automatico e faça todo app


## Pedido 3 — 18/07/2026 16:19

> você terminou?


## Pedido 4 — 18/07/2026 16:23

> onde está o arquivo .exe?


## Pedido 5 — 18/07/2026 16:30

> dsfsdfDuas coisas:
>
> 1. A pasta dist está vazia — não achei o .exe. Confira o que 
> aconteceu e gere de novo.
>
> 2. Quero um INSTALADOR de verdade, não só o programa portátil.
> Use Inno Setup para gerar um "EditorImpressao-Setup.exe" que:
> - instale em "Arquivos de Programas"
> - crie atalho no menu Iniciar e na área de trabalho
> - apareça na lista "Adicionar ou remover programas" do Windows
> - tenha o assistente em português
> - inclua desinstalador
> Deixe o script .iss no repositório e um comando pra gerar tudo 
> de uma vez (empacotar + instalador).
> Continue gerando também a versão portátil em pasta, pra quem 
> preferir rodar de pendrive.
>
> 3. FALTOU uma função importante: escolher onde salvar o PDF.
> Hoje ele salva sempre em Documentos. Quero:
> - na tela final (ou antes de processar), um botão "Escolher pasta"
>   abrindo o seletor de pastas do Windows
> - campo mostrando o caminho escolhido, com opção de editar o nome
>   do arquivo
> - lembrar a última pasta usada e sugerir ela na próxima vez
>   (guardar nas configurações)
> - avisar se já existir arquivo com o mesmo nome, oferecendo
>   substituir ou renomear
> - se a pasta não tiver permissão de escrita, avisar em português
>   e sugerir outr


## Pedido 6 — 18/07/2026 16:54

> onde está o .exe?


## Pedido 7 — 18/07/2026 16:57

> [Image #3] não estou achando o .exe, eu quero que faça uma nova pasta e faça o .exe


## Pedido 8 — 18/07/2026 17:17

> Quero limpar tudo e ficar só com o instalador. Faça nesta ordem:
>
> 1. CORRIJA O TRAVAMENTO
> Ao clicar nos botões da tela de conferir ("esta certo", 
> "nao cortar esta", "voltar ao automatico", "usar em todas"), 
> o programa fecha sozinho. Encontre a causa e corrija.
> Depois, envolva os handlers de evento com tratamento de erro: 
> nenhuma exceção pode fechar a janela — deve virar aviso em 
> português e registrar no log.
>
> 2. CORRIJA O LAYOUT SOBREPOSTO
> A caixa azul de explicação e os botões estão sendo desenhados 
> POR CIMA da imagem da página, escondendo o conteúdo.
> Empilhe na tela de conferir, de cima para baixo, sem nenhuma 
> sobreposição:
>   1. cabeçalho (título + alertas + desfazer/refazer)
>   2. abas
>   3. área da imagem  ← ocupa o espaço que sobrar (stretch)
>   4. caixa azul de explicação
>   5. linha de botões
>   6. tira de miniaturas
>   7. rodapé (voltar / confirmar e processar)
> Use QVBoxLayout de verdade. NÃO usar setGeometry, move() nem 
> widget flutuando sobre o visualizador.
> Teste redimensionando a janela em vários tamanhos.
>
> 3. TESTE VOCÊ MESMO antes de me entregar
> Abra o programa, carregue um PDF, clique em TODOS os botões de 
> todas as abas, redimensione a janela. Só me chame quando não 
> travar mais e o layout estiver correto.
>
> 4. LIMPE TUDO E ME ENTREGUE SÓ O INSTALADOR
> - apague as pastas build/ e dist/ e qualquer .exe ou versão 
>   portátil anterior
> - gere APENAS o instalador com Inno Setup
> - coloque o arquivo final na minha Área de Trabalho, dentro de 
>   uma pasta chamada "Editor de Impressao"
> - dentro dessa pasta quero SÓ o "EditorImpressao-Setup.exe", 
>   nada mais — sem _internal, sem pastas de bibliotecas
> - o instalador deve instalar em Arquivos de Programas, criar 
>   atalho no menu Iniciar e na área de trabalho, aparecer em 
>   "Adicionar ou remover programas", e ter desinstalador
> - assistente em português
>
> Pode usar as versões de teste durante o desenvolvimento, mas o 
> que sobra pra mim no final é só o instalador.


## Pedido 9 — 18/07/2026 17:54

> Três coisas para ajustar:
>
> ════════════════════════════════════════════════
> 1. AMPLIAR A PÁGINA EM TELA GRANDE
> ════════════════════════════════════════════════
> Quero poder ver a página em tamanho grande para conferir de perto.
>
> - Clicar em qualquer um dos quatro cartões de filtro abre a 
>   página AMPLIADA, ocupando a janela inteira
> - Duplo clique numa miniatura da tira também abre ampliado
> - Na tela ampliada:
>   · zoom com a roda do mouse, mais botões + / - / "ajustar à tela"
>   · arrastar com o mouse para mover a imagem quando com zoom
>   · setas ← → continuam mudando de página
>   · teclas 1 2 3 4 trocam o filtro sem sair da tela ampliada
>   · Esc ou X volta para a tela normal
>   · nome do filtro visível num canto
> - Modo COMPARAR na tela ampliada: dois filtros lado a lado, com 
>   zoom e posição sincronizados, para eu comparar de perto
> - Mesma coisa nas abas "Onde cortar" e "Bordas": clicar amplia, 
>   e a linha de corte / as alças continuam arrastáveis ampliadas
> - A imagem ampliada deve ser gerada em resolução maior que a da 
>   prévia — não basta esticar a miniatura, fica pixelada
>
> ════════════════════════════════════════════════
> 2. REORGANIZAR OS CONTROLES + MEDIDORES DESLIZANTES
> ════════════════════════════════════════════════
>
> 2.1 Separar AJUSTES de AÇÕES
> Hoje "Força do preto" está na mesma linha que "só nesta / usar em 
> todas / apagar página" — são coisas diferentes e confunde.
> Reorganize em blocos empilhados:
>
>   [ caixa azul de explicação ]
>
>   ┌─ Ajuste ───────────────────────────────────┐
>   │  Força do preto   fraco ──●──── escuro  leve│
>   └─────────────────────────────────────────────┘
>
>   Aplicar em:  [só nesta] [todas] [só nas próximas] | [apagar página]
>
> - O bloco "Ajuste" tem fundo e borda próprios, separado visualmente
> - "apagar página" afastado dos outros por um separador — é ação 
>   destrutiva, não pode ficar colada nas demais
> - "só nesta" é o botão primário (destacado)
>
> 2.2 Trocar os três botões por medidor deslizante (QSlider)
> Em vez de "mais fraco / normal / mais escuro":
>
> - PRETO E BRANCO → slider "Força do preto", 0 a 100, padrão 50
>   · mapeia o k do Sauvola: 0 → k=0.40 (bem fraco), 
>     50 → k=0.20 (normal), 100 → k=0.06 (bem escuro)
>   · rótulos "mais fraco" e "mais escuro" nas pontas
>   · texto ao lado em palavras: bem fraco / leve / normal / forte / 
>     bem forte
>
> - MÁGICO PRO → slider "Intensidade", 0 a 100, padrão 50
>   · controla junto: saturação (1.0 a 2.2), clipLimit do CLAHE 
>     (1.0 a 3.5) e força da nitidez
>   · rótulos "suave" e "bem forte"
>
> - MELHORAR → slider "Clareza do fundo", 0 a 100, padrão 50
>   · quanto empurra o fundo em direção ao branco
>
> Cada slider só aparece quando o filtro correspondente está 
> selecionado. O valor é por página, e vale também para "todas" e 
> "só nas próximas".
>
> 2.3 Prévia ao vivo
> Ao arrastar o slider a prévia atualiza em tempo real. Para não 
> travar: processar em resolução baixa durante o arrasto e refazer 
> em resolução normal ao soltar. Debounce de ~150ms.
>
> ════════════════════════════════════════════════
> 3. ACENTOS (já pedi duas vezes e continua errado)
> ════════════════════════════════════════════════
> A interface ainda mostra: "Impressao", "pagina", "Magico", 
> "so nesta", "proximas", "Forca", "Espaco", "duvida", "nao", 
> "laranjas eu nao tive certeza".
>
> Corrija TODOS os textos da interface para português correto:
> Impressão, página, Mágico, só nesta, próximas, Força, Espaço, 
> dúvida, não.
>
> Verifique se os arquivos .py estão salvos em UTF-8 e se as 
> strings estão sendo lidas corretamente pelo Qt. Passe por todos 
> os arquivos de ui/ conferindo cada texto.
>
> ════════════════════════════════════════════════
> Faça na ordem 3 → 2 → 1 (do mais simples ao mais complexo) e me 
> mostre funcionando ao final.


## Pedido 10 — 18/07/2026 19:02

> a parta com o arquivo .exe sumiu


## Pedido 11 — 18/07/2026 19:28

> Coloquei vários PDFs de teste reais na pasta pdfs_teste/ do 
> projeto. Use TODOS eles na bateria de testes, em vez dos PDFs 
> sintéticos.
>
> Para cada arquivo, me diga:
> - qual o tipo (folhas duplas ou simples, colorido ou P&B, 
>   qualidade do scan)
> - o que o programa detectou e se acertou
> - onde ele errou
>
> E me traga as imagens comparativas dos quatro filtros de cada 
> um, escolhendo as páginas mais difíceis de cada arquivo — as 
> mais amareladas, as mais tortas, as com texto do verso 
> transparecendo.
>
> Importante: adicione pdfs_teste/ ao .gitignore, para os 
> arquivos não irem para o repositório.


## Pedido 12 — 18/07/2026 19:55

> você continua não fazendo o .exe, cade?


## Pedido 13 — 18/07/2026 20:02

> INSTALA NO MEU COMPUTADOR E COLOCA NA MINHA AREA DE TRABALHO


## Pedido 14 — 18/07/2026 20:24

*Documento longo (9,195 caracteres). Está inteiro no **Apêndice B — O prompt de testes**, no fim deste arquivo.*

> # Prompt de testes — colar no Claude Code


## Pedido 15 — 29/07/2026 14:35

> vamos fazer mudanças no projeto do editor de impressão?


## Pedido 16 — 29/07/2026 14:46

> faça um resumo do programa para o claude que eu possa colar lá na conversa


## Pedido 17 — 29/07/2026 16:27

> consegue olhar essa pasta "C:\Users\fotog\Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros" ver o que eu escrevi nos blocos de notas e ver e comparar as fotos que estão lá, para ver quais problemas quero resolver, depois me de uma lista aqui do que você leu, para eu poder ver se fez certo.


## Pedido 18 — 01/08/2026 17:19

> eu fechei sem querer o trabalho que estavamos fazendo, pode recuperar, tambem tinha escrito algumas coisas no na barra recupera o trabalho estamos no editor de impressão


## Pedido 19 — 01/08/2026 17:24

> 2


## Pedido 20 — 01/08/2026 17:46

> ok e agora?


## Pedido 21 — 01/08/2026 18:05

> explique eu não entendi


## Pedido 22 — 01/08/2026 18:06

> eu quero que o papel saia branco, e o desenho também saia perfeito.


## Pedido 23 — 01/08/2026 18:22

> não entendi, o jeito que você escreve fica dificil para eu entender as informações, seja mais direto por favor


## Pedido 24 — 01/08/2026 18:26

> ok, continue os testes.


## Pedido 25 — 01/08/2026 18:31

> aqui não está aparecendo que você está trabalhando


## Pedido 26 — 01/08/2026 18:32

> não era para aparecer um contador enquanto você está trabalhando ?


## Pedido 27 — 01/08/2026 18:34

> você consegue me mandar notificação pop up quando tiver alguma coisa nova? ou quando precisar de alguma informação? aplique isso para os três projetos que estão rodando no claude code.


## Pedido 28 — 01/08/2026 18:51

> quando terminar vai fazer o pop up?


## Pedido 29 — 01/08/2026 18:53

> aparece nas notificações mas não pula na minha tela


## Pedido 30 — 01/08/2026 18:59

> quando eu clicar na janelinha eu quero ir direto para o terminal que está enviando a notificação, e quero que seja notificado só quando tiver responder alguma coisa e não enquanto está trabalhando codificando


## Pedido 31 — 01/08/2026 19:03

> ok


## Pedido 32 — 01/08/2026 19:04

> eu quero pode ver algum tipo de carregamento aqui no terminal enquanto você trabalha


## Pedido 33 — 01/08/2026 19:08

> vou olhar as imagens


## Pedido 34 — 02/08/2026 11:39

> pode continuar fazendo outras coisas enquanto eu não vejo os ultimos testes?


## Pedido 35 — 02/08/2026 11:48

> vai concertar os filtros e depois a gente volta para parte de seleção.


## Pedido 36 — 03/08/2026 21:35

> por favor, confira os teste que você fez sozinho, não vou ter como fazer isso.[


## Pedido 37 — 03/08/2026 21:57

> deixa eu ver os testes que você fez


## Pedido 38 — 04/08/2026 03:05

> recuperar


## Pedido 39 — 04/08/2026 03:07

> pq estava pedindo para resumir a sessão?


## Pedido 40 — 04/08/2026 03:09

> o que tem para fazer agora no programa?


## Pedido 41 — 04/08/2026 03:11

> pq o melhoramento dos filtros não está nesta lista?


## Pedido 42 — 04/08/2026 12:35

> opa e agora, o que está fazendo?


## Pedido 43 — 04/08/2026 13:12

> manda print dos testes para eu ver


## Pedido 44 — 04/08/2026 13:39

> ok, o que falta ainda fazer, acho que estamos quase chegando no perfeito na seleção.


## Pedido 45 — 04/08/2026 17:22

> vamos continuar o trabalho do editor de impressão


## Pedido 46 — 04/08/2026 18:22

> porque você continua travando , porque não vai até o final?


## Pedido 47 — 04/08/2026 18:44

> me da um resumo de tudo que tu fez agora em arquivo md, as perguntas que me fez os prints que eu te mandei, os pedidos que eu te fiz em toda a conversa, as questões que tu perguntou para mim e o que falta para o programa estar pronto de acordo com o que eu quero e como ele deve funcionar


## Pedido 48 — 04/08/2026 19:10

> você esqueceu de colocar os meus pedidos que eu fiz ao longo da conversa no relatorio só me da um relatorio em md para eu mandar para o claude


## Pedido 49 — 05/08/2026 14:53

> o que falta agora? porque você parou?


## Pedido 50 — 05/08/2026 16:26

> ok, o que falta fazer ainda de tudo que eu já pedi e apontei?


## Pedido 51 — 05/08/2026 16:42

> muita coisa para eu ler, seja mais consigo por favor, fale em quatro linhas o que eu preciso escolher


## Pedido 52 — 05/08/2026 16:44

> continue 1 e depois 2 e termine tudo, só me chame quando terminar tudo


## Pedido 53 — 06/08/2026 13:04

> pera ai, faz um resumo pra mim


## Pedido 54 — 06/08/2026 13:06

> o que falta fazer?


## Pedido 55 — 06/08/2026 13:17

> a ferramenta de seleção está finalizada também?


## Pedido 56 — 06/08/2026 13:23

> ok, vamos continuar os testes do selecionador, além disso pesquise sobre como treinar selecionadores como programar esse tipo de coisas, procure também respositorios no reddit e como grandes apps como photoshop e adobe pdf fazem isso para nos ajudar a testar nosso programa e deixar ele zero, só pare quando estiver 99% de certeza e dai quando chegar nesse numero deixe amostras do seu trabalho lá na pasta de testes. depois disso continue a aplicar esse selecionador em conjunto com nossos filtros para que com o selecionador possamos aplicar filtro só em uma parte selecionada, ou melhorar o trabalho de um filtro, entendeu?


## Pedido 57 — 06/08/2026 14:07

> consegue ativar o modo voz


## Pedido 58 — 06/08/2026 14:08

> É explica para mim poucas palavras O que falta fazer no Programa


## Pedido 59 — 06/08/2026 14:09

> Tambão conserta todas essas coisas e só volta aqui a me chamar quando terminar tudo isso


## Pedido 60 — 06/08/2026 17:38

> não entendi do que você está falando, seja mais simples


## Pedido 61 — 06/08/2026 17:40

> eu quero ter opção de transformar uma capa em branco. 2 - pode continuar mexendo no programa, precisa treinar o programa poder selecionar cores né? e tambem letras antigas tambem.


## Pedido 62 — 06/08/2026 17:47

> eu quero que ele reconheça cores mesmo, para eu ter uma ferramenta a mais de seleção para eu poder selecionar por cor quando o programa dar errado.


## Pedido 63 — 06/08/2026 20:13

> sim, pode continuar


## Pedido 64 — 06/08/2026 23:09

> resolva


## Pedido 65 — 08/08/2026 02:32

> me faz um resumo de tudo que tu fez, tudo que já pedi coloca tudo em documento texto para eu mandar no claude, o prompt inicial tudo bem explicado e o que falta fazer.


## Pedido 66 — 08/08/2026 02:37

> você anexou todos os meus pedidos durante a conversa nesse relatorio?


## Pedido 67 — 08/08/2026 02:40

> não, eu fiz varios outros pedidos sobre o programa sobre funcionalidades, apotamentos sobre os testes que você fez, leia a conversa inteira antiga para lembrar


## Pedido 68 — 08/08/2026 02:46

> ta faz um novo relatorio e agora, coloca todos os meus pedidos dentro dele por favor, durante a conversa, junto com o relatorio da conversa completa



---

# PARTE 2 — O que é o programa

Aplicativo de desktop para Windows que **recupera PDFs de livros antigos
escaneados e os prepara para reimpressão em cadernos**. Projeto do Pe. Rosenei,
de um instituto de preservação de livros. Um "CamScanner para PC".

**Quem usa é o Kaique, impressor, sem formação técnica.** Toda a interface é em
português do Brasil, sem jargão: ele nunca vê "Sauvola", "k" ou "deskew" — vê
"Força do preto", "Melhorar", "girar a folha".

**Duas versões anteriores fracassaram.** Uma travava (customtkinter), a outra
dava qualidade ruim (fórmula caseira de filtro). Daí vêm as regras rígidas
abaixo — nenhuma é preferência de estilo, cada uma é cicatriz.

## As regras que não se negociam

- **PySide6, nunca tkinter.**
- **Uma página por vez na memória.** O pico não pode crescer com o tamanho do
  livro; há livro de 300 MB no acervo.
- **Nenhum emoji em rótulo de interface.**
- **Textos de interface com acento. Caminhos de disco sem acento.**
- **Algoritmo consagrado em vez de fórmula própria.**
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.

## Os quatro filtros

| Filtro | O que faz |
|---|---|
| Original | não mexe |
| Preto e branco | Sauvola do DoxaPy: tira o amarelado e o texto do verso |
| Melhorar | divide pelo fundo estimado: limpa a iluminação sem tocar na cor |
| Mágico pro | Melhorar + contraste local + cor + nitidez, para capas e gravuras |

## As duas réguas

- **`avaliar.py`** — a régua dos filtros. Roda sobre os nove livros e responde:
  alguma página saiu **pior** do que entrou? O critério é que isso seja **zero**.
- **`avaliar_selecao.py`** — a régua da seleção, criada em 06/08/2026. Mede se o
  programa acertou o que é gravura, letra e papel, em 26 páginas.

## O protocolo

**Medir antes, uma mudança por vez, medir de novo, reverter se qualquer número
piorar.** Se parecer valer a pena mesmo assim, não reverter sozinho: apresentar
os dois resultados.

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
core/pipeline.py           dividir, cortar, endireitar, filtrar, impor
core/cadernos.py           imposição e conferência da sequência
avaliar.py                 a régua dos filtros
avaliar_selecao.py         a régua da seleção
conferir.py                a tela de conferir amostras falando
relatorios/melhorias.md    tudo que foi tentado, inclusive o que falhou
```

Acervo: `Desktop\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE`, nove livros,
2903 folhas. As queixas do Kaique estão em
`Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros` — `.txt` soltos com um
print ao lado, e **são fonte de requisito**.

```
.venv\Scripts\python.exe main.py                 o programa
.venv\Scripts\python.exe -m pytest tests -q      os 150 testes
.venv\Scripts\python.exe avaliar.py              a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py      a régua da seleção
.venv\Scripts\python.exe conferir.py             conferir amostras falando
```

---

# PARTE 3 — Os pedidos que valem como regra permanente

Seis dos 68 não são tarefa: são o modo de trabalhar. **Quem pegar este projeto
deve ler estes primeiro.**

- **"seja mais direto"** e **"seja mais conciso — em quatro linhas"** — texto
  curto no chat; o detalhe vai para arquivo.
- **"não entendi do que você está falando, seja mais simples"** — e não é o
  mesmo que ser curto. É falar em português comum: "o programa estava estragando
  a capa dos livros", e não "o balanço de branco eleva o ruído de 5,5 para 17,5".
  O número entra depois da frase que se entende, nunca no lugar dela.
- **"confira os testes que você fez sozinho, não vou ter como fazer isso"** —
  abrir todas as imagens antes de dizer que funcionou.
- **"porque não vai até o final?"** — decidir sozinho dentro da alçada e
  executar o protocolo inteiro, em vez de parar a cada passo.
- **"vai consertar os filtros e depois a gente volta para a seleção"** — a ordem
  combinada.
- **"eu quero que o papel saia branco, e o desenho também saia perfeito"** — o
  critério final, em uma frase.

---

# PARTE 4 — As dez queixas do Kaique

| Queixa, nas palavras dele | Situação |
|---|---|
| "as letras estão ficando pixeladas, precisamos que fiquem mais arredondadas" | **Feito e conferido na imagem** |
| "o mágico pro está deixando muito pixelado a imagem" | **Feito e conferido** |
| "às vezes a parte de trás fica com uma mancha da parte da frente" | **Feito e conferido** |
| "o programa não localizou as bordas corretamente" | **Feito e conferido em dois casos** |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | **Feito** |
| "colocar botão clicável nas páginas que o programa não tem certeza" | **Existe** |
| "a barra de scroll devia ser preta" | **Feito em 06/08** |
| "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | **Feito em 06/08** — o programa simula a dobra e confere |
| "no mágico pro o fundo deveria remover o amarelado e deixar totalmente branco" | **Em grande parte feito** |
| "queremos que fique branco a página e só as letras pretas" | **Atendido em número**; falta escolher o binarizador por página |

---

# PARTE 5 — O que foi feito de 04 a 07/08/2026

São 12 commits. **A régua dos filtros saiu de 27 motivos de reprovação para 4**,
e a seleção ganhou régua própria e está em 23 de 26.

## Os filtros

**A causa do fundo que escurece.** Sete das oito reprovações vinham de um passo
só: o realce de cor do Mágico pro multiplica o S do HSV mantendo o V — preserva
o brilho, mas não a luminância, e papel velho é sempre amarelo-pardo. Três
saídas foram implementadas e medidas no acervo inteiro, e **as três foram
revertidas**: todas consertavam o papel e engrossavam a rubricação vermelha, que
é entupimento de letra, o defeito mais grave que existe aqui.

**A capa não é papel.** Numa capa não há papel a branquear — o que ali parece
papel é o couro. Três passos tiveram de sair, cada um com sua medição:

| Passo retirado | Medido |
|---|---|
| branqueamento e ponto de preto | ruído do Boécio 5,5 → 17,5 |
| achatamento da iluminação | couro verde do Horas 219 → 194 |
| recomposição da rampa | couro vermelho do Graduale 47,4 → 43,9 |

## A régua

**A rampa da borda passou a ser rampa de verdade.** Contava pixels de tom
intermediário perto do contorno, e o grão do papel entrava na conta: limpar o
papel aparecia como estragar a letra. Agora é contraste dividido pela
inclinação, e sai em pixels. Validada contra casos extremos: imagem binarizada
dá exatamente 1,00; desfocada com sigma 4 dá 3,19.

**A régua parou de medir letra onde não há letra.** As páginas em que ela
afrouxa saem **nomeadas** no relatório, de propósito.

**Um erro meu, achado abrindo as imagens.** A primeira versão dessa regra
desligou a verificação em 30 das 63 páginas, incluindo uma partitura manuscrita
cheia de texto. Apertei a regra, caiu para 13, e abri as treze.

## A seleção

**Ganhou régua própria**, com 26 páginas e uma expectativa escrita olhando cada
uma.

**O defeito que ela achou de cara: o Preto e branco apagava a capa dos livros.**
A capa de pergaminho do Boécio saía uma folha branca, sobrando só a etiqueta da
biblioteca. Capa e folha em branco pedem coisas opostas, e isso foi medido. O
detector passou a perguntar se aquilo é **objeto ou folha**.

## Ferramentas novas

**"Pegar tudo desta cor"** — a sétima ferramenta da aba Marcar. Na partitura do
Graduale a varinha antiga vaza e leva 99,8% da folha; a nova pega 7,7% — as
vinte pautas vermelhas e as letras rubricadas. Compara só o **matiz**.

**"Filtro só neste pedaço"** — a folha vai a Preto e branco e a gravura fica no
Original. Testado: o texto sai com 2 tons e a gravura mantém 256.

**Marcar a folha inteira como papel = folha em branco**, para a capa que não se
quer no livro reimpresso.

**A tela de conferir** (`conferir.py`) — as amostras uma a uma, com caixa para
dizer o que está errado. Aceita o **ditado do Windows: Win+H e falar**.

## Fora da imagem

**A barra de rolagem ficou preta.**

**A sequência dos cadernos passou a ser conferida**: o programa simula a dobra e
verifica que a leitura sai 1, 2, 3 até o fim, que as folhas saem em pares de
frente e verso, e que nenhuma página sumiu ou repetiu.

**Um travamento sério consertado:** o gerador de relatório entrava em laço
infinito com tabela grande e deixava um PDF de zero byte. Podia travar o
programa na mão do Kaique, sem mensagem e sem fim.

**O aviso "tem cor" parou de ser decidido na navalha.** O limiar de 5% caía
dentro da faixa das páginas coloridas; passou para 2%, no meio do vão medido.

---

# PARTE 6 — O que falta

## 1. A pergunta que ficou sem resposta desde 18/07

No prompt de testes (Apêndice B) você pediu, com todas as letras:

> "Ao final, me diga em uma frase: **o programa já substitui o CamScanner para o
> trabalho do Kaique? Sim, não, ou ainda não.**"

**Isso nunca foi respondido.** A pasta `para_comparar/` foi montada, com as dez
imagens — as cinco páginas difíceis antes e depois —, mas a comparação lado a
lado com o CamScanner nunca foi feita nem o veredito dado.

É o teste que você chamou de decisivo, e o único que mede o programa contra o
que o Kaique usa hoje. Devia vir antes de qualquer refinamento novo.

## 2. Dois critérios de aceitação nunca conferidos

- **"menos de 10% das páginas marcadas para revisão"** — hoje o acervo tem 349
  páginas com "ângulo suspeito" e 305 com "tem cor" em 2903 folhas. Só o
  primeiro já passa de 12%. O alerta corre o risco de virar ruído, que é
  exatamente o que a especificação mandava evitar.
- **"aplicar filtros diferentes em páginas diferentes, gerando um PDF só"** — o
  filtro é por página no modelo de dados, mas nunca foi conferido ponta a ponta
  num livro de verdade.

## 3. A régua dos filtros: 4 motivos

- **Três são a mesma página** — a 126 do Graduale, uma partitura manuscrita que
  o detector marca como desenho. Conserta-se consertando a detecção.
- **Um é o Pesel 76** — o fundo escurece de 156 para 148 no Mágico pro.

## 4. A régua da seleção: 3 de 26

As três têm a mesma raiz: o modelo de layout foi treinado em documento moderno.

- **Graduale 126** — partitura manuscrita marcada 100% gravura.
- **Siebmacher 45** — as legendas impressas da prancha não viram letra.
- **Pesel 73** — o título impresso sai como foto.

**Cinco sinais foram medidos para separar escrita antiga de foto** — pedaços de
glifo, papel à vista, meio-tom, periodicidade do perfil de linhas e uniformidade
da parte clara — e **em todos os cinco os números das duas se cruzam**. Está em
`relatorios/melhorias.md`, para ninguém repetir.

Como não dá para decidir pela imagem, o programa agora **admite a dúvida**: a
página fica laranja com "Desenho ou escrita? Não tenho certeza."

**O conserto de verdade é somar um modelo treinado em documento histórico** —
Eynollah, dhSegment ou Kraken —, e existe dataset anotado para validar: o
DIVA-HisDB, 150 páginas de manuscritos medievais da competição ICDAR 2017.

## 5. A rubricação vermelha virando preta

No Preto e branco, a rubricação vermelha do Graduale e do Livro de Horas vira
barra preta. A causa suspeita: a conversão para cinza trata vermelho como
escuro. O DoxaPy oferece oito métodos de conversão a investigar.

## 6. Escolher o binarizador por página

Foram comparados os 18 binarizadores do DoxaPy em 36 páginas: **não existe
vencedor único**. No Palatino, de letra gótica pesada, o Otsu sai sólido
enquanto o Sauvola quebra o traço; noutras páginas se inverte.

## 7. Falta um número na régua: "guardou a sujeira"

O Otsu marca zero pioras mas guarda o dobro de tinta do Sauvola — em papel
envelhecido isso quer dizer manter a mancha como se fosse letra, e **nenhum
critério atual pega isso**.

## 8. O caminho para treinar

Para reconhecer letra antiga o programa precisa de gabarito, e **a aba Marcar já
é a ferramenta que o produz**. O caminho:

1. Marcar à mão 30 ou 40 páginas difíceis, das que ele erra.
2. Guardar essas marcações como gabarito.
3. Com gabarito dá para **medir de verdade** — Interseção sobre União por
   classe, como a competição ICDAR avalia — em vez de julgar no olho.
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



---

# APÊNDICE A — A especificação original

Pedido 1, de 18/07/2026. É a lista de funcionalidades do programa, e vale reler inteira.

---


# Editor de Impressão — especificação completa e prompt para o Claude Code

Projeto do Pe. Rosenei — Instituto de preservação de livros.
Aplicativo de desktop para recuperar livros antigos escaneados e preparar para reimpressão.
Usuário final: **Kaique** (impressor, sem conhecimento técnico).

---

# PARTE 1 — Recapitulação das decisões

## Objetivo
Um **"CamScanner para PC"**: programa único de desktop que limpa o amarelado, endireita páginas tortas, divide folhas escaneadas com duas páginas e monta os cadernos prontos para impressão.

## Histórico do projeto (por que estamos refazendo)
1. Começou com um script Python de imposição de cadernos (`imposicao_cadernos.py`) — a matemática estava correta
2. Virou app de navegador (v1, v2) — só imposição
3. v3 no navegador — ganhou filtros e deskew, mas em JavaScript, lento
4. v4/v5 desktop com customtkinter — ganhou 4 filtros e 4 modos, mas **travava** e a **qualidade dos filtros ficou insatisfatória**

**Conclusão:** refazer do zero em Python/OpenCV, mantendo o que funcionava e resolvendo o que não funcionava.

## O que reaproveitar (já comprovado)
- A **matemática da imposição de cadernos** (arquivo `imposicao_cadernos.py`)
- O **processamento página a página** — resolveu o travamento com livros de 500+ páginas a 400 DPI
- A **cópia direta de páginas** no modo "só cadernos" (não rasteriza)

## O que trocar
- **customtkinter → PySide6**: o customtkinter foi a origem dos erros de abrir e dos travamentos
- **Filtros feitos à mão → DoxaPy + receitas OpenCV consagradas**

## Como os projetos do GitHub entram
| Projeto | Papel | Licença |
|---|---|---|
| **DoxaPy** (brandonmpetty/Doxa) | **Dependência real.** Sauvola/Wolf para o Preto e branco | CC0 (domínio público) |
| **scikit-image** | Plano B se DoxaPy não compilar no Windows | BSD |
| **hasanfirnas/PDF_Magic-Color_filter** | Receita de referência para o Mágico Pro | — |
| **ArashNasrEsfahani/Python-Document-Scanner-OpenCV** | Receita (vibração de cor + nitidez) | — |
| **ScanTailor Advanced / Experimental** | Referência de algoritmo apenas. **Não embutir** (C++/Qt, GPL) | GPL v3 |
| **OCRmyPDF** | Adiado para a v2 | — |

## Fora do escopo da v1
- OCR / texto pesquisável
- Escanear direto do scanner

---

# PARTE 2 — Prompt para colar no Claude Code

> Cole tudo daqui até o fim da Parte 2.

---

Quero construir um aplicativo de desktop em Python chamado **Editor de Impressão**. Ele recupera PDFs de livros antigos escaneados e prepara para reimpressão em cadernos. O usuário final é um impressor sem conhecimento técnico nenhum — a interface precisa ser à prova de erro, em português do Brasil, sem jargão.

Leia esta especificação inteira antes de escrever qualquer código.

---

## 1. Stack obrigatória

- **Python 3.11+**
- **PySide6** para a interface — NÃO usar tkinter nem customtkinter (foram a causa de travamentos na versão anterior)
- **PyMuPDF (fitz)** para ler e escrever PDF
- **OpenCV (cv2)** + **numpy** para processamento de imagem
- **DoxaPy** (`pip install doxapy`, licença CC0) para binarização adaptativa. Se não compilar no Windows, cair automaticamente para `skimage.filters.threshold_sauvola`
- **Pillow** para conversões auxiliares
- Empacotamento: **PyInstaller** → um `.exe` único, sem instalador, sem dependência externa

---

## 1.1 Projetos de referência (consulte antes de implementar os filtros)

Estes projetos já resolveram partes deste problema. **Estude-os antes de escrever os filtros** — não reinvente o que já está resolvido.

**Para usar de verdade (dependência):**
- **brandonmpetty/Doxa** → `pip install doxapy`. Licença **CC0 (domínio público)** — uso livre, sem restrição. Implementa Otsu, Niblack, **Sauvola**, **Wolf**, Gatos, NICK, ISauvola, Su. É a base do filtro Preto e branco.
- **scikit-image** (`skimage.filters.threshold_sauvola`, `threshold_niblack`) — licença BSD. Plano B se o DoxaPy não compilar no Windows.

**Para ler a receita e implementar a nossa versão (NÃO copiar código, apenas estudar a abordagem):**
- **hasanfirnas/PDF_Magic-Color_filter** — efeito Magic Color do CamScanner em OpenCV, trabalhando sobre PDF. É a referência mais direta para o filtro **Mágico pro**.
- **ArashNasrEsfahani/Python-Document-Scanner-OpenCV** — pipeline que reforça vibração de cor e nitidez para deixar documento limpo e legível, replicando o CamScanner.
- **satvik007/Scanner_OP** — receita clássica de "magic color"; código de protótipo, útil para entender a matemática.
- **andrewdcampbell/OpenCV-Document-Scanner** — detecção automática de bordas/cantos e realce; boa referência para o deskew e para uma futura função de corrigir foto tirada torta.

**Referência de algoritmo, NÃO embutir no projeto:**
- **ScanTailor Advanced** e **ScanTailor Experimental** (forks vivos do ScanTailor) — é o padrão-ouro de limpeza de livro escaneado, usado por bibliotecas. Usa **binarização local Sauvola e Wolf** para papel amarelado e filtros específicos para remover **bleed-through** (texto do verso transparecendo). **Atenção:** é C++/Qt sob licença **GPL v3** — não dá para fundir com este projeto Python, e a licença é incompatível. Serve apenas como confirmação de que Sauvola/Wolf são o caminho certo. O ScanTailor original (repositório `scantailor/scantailor`) está arquivado desde 2020 — ignorar.

**Adiado para a v2, não implementar agora:**
- **OCRmyPDF** — camada de texto pesquisável. Já traz o **unpaper** embutido (limpeza de artefatos) quando usado com `--clean`.
- **NAPS2** — captura direto do scanner; tem linha de comando (CLI), útil se um dia quisermos integrar o escaneamento.

**Regra de licença:** só incorporar código de projetos com licença permissiva (CC0, MIT, BSD, Apache). Nada de GPL. Quando a referência for GPL ou de linguagem diferente, implementar a nossa própria versão a partir da descrição do algoritmo.

---

## 2. Arquitetura obrigatória

Separação total entre processamento e interface. O `core/` NÃO pode importar nada de `ui/` — quero poder rodar todo o processamento por linha de comando, sem abrir janela.

```
editor_impressao/
├── core/
│   ├── __init__.py
│   ├── pdf_io.py           # abrir/salvar PDF, página → imagem, imagem → página
│   ├── filtros.py          # os 3 filtros + original
│   ├── dividir.py          # detectar lombada, dividir folha
│   ├── endireitar.py       # deskew
│   ├── cadernos.py         # imposição
│   ├── analise.py          # detectar cor, confiança, sugestões
│   └── pipeline.py         # orquestra tudo, página por página
├── ui/
│   ├── __init__.py
│   ├── janela_principal.py # QMainWindow + QStackedWidget das 4 telas
│   ├── tela_inicio.py
│   ├── tela_opcoes.py
│   ├── tela_conferir.py
│   ├── tela_final.py
│   └── widgets/
│       ├── area_arrastar.py
│       ├── visualizador.py      # prévia com linha de corte arrastável
│       ├── tira_miniaturas.py
│       └── cartao_filtro.py
├── modelos.py              # dataclasses: Projeto, Pagina, Config, Acao
├── historico_acoes.py      # pilhas de desfazer/refazer + gravação em acoes.jsonl
├── historico.py            # projetos anteriores (JSON local)
├── recursos/               # ícones
└── main.py
```

---

## 3. REGRAS CRÍTICAS (não violar)

### 3.1 Memória
Livros têm 500+ páginas a 400 DPI. **Processar sempre uma página por vez**: ler → processar → escrever no PDF de saída → liberar da memória. **NUNCA** montar uma lista com todas as páginas processadas. Isso travou a versão anterior.

Limitar o DPI automaticamente: se `largura_px * altura_px > 40_000_000`, reduzir o DPI até caber.

### 3.2 Interface nunca congela
Todo processamento roda em `QThread` (ou `QThreadPool`), nunca na thread da interface. Sempre com barra de progresso e botão de cancelar funcional.

### 3.3 Nunca travar com erro
Qualquer exceção vira aviso amigável em português numa caixa de diálogo. O programa continua aberto. Registrar o erro técnico num arquivo de log, não na tela.

### 3.4 Nada de emoji no código da interface
A versão anterior quebrou no Windows por causa de emojis em labels. Usar ícones vetoriais ou texto puro.

---

## 4. Funcionalidades

Cada função é **independente, marcável por checkbox**. O usuário pode ligar uma, várias ou todas, em qualquer combinação. Nunca forçar combinação.

Ordem obrigatória do processamento (quando várias estão ligadas):
```
1. dividir folhas → 2. cortar bordas → 3. endireitar → 4. filtro → 5. montar cadernos
```
Páginas marcadas como **apagadas** são descartadas logo após a etapa 1.

### 4.1 Dividir folhas ao meio

Muitos escaneamentos trazem duas páginas do livro numa folha só (formato paisagem).

**Detecção automática:**
1. Verificar se a página é paisagem (`largura > altura * 1.2`)
2. Converter para escala de cinza
3. Somar a intensidade dos pixels por coluna → vetor de perfil vertical
4. Suavizar o perfil (filtro de média móvel)
5. Procurar o **mínimo de intensidade** (faixa mais escura = sombra da lombada) dentro da faixa central (entre 35% e 65% da largura)
6. Calcular a **confiança**: quão pronunciado é o vale em relação à média, e quão perto do centro está

**Confiança baixa quando:** o vale é raso, está longe do centro, ou a página não é paisagem. Marcar essas páginas para revisão.

**Controle manual obrigatório:**
- Arrastar a linha de corte com o mouse
- Botão "não dividir esta página" (capa, ilustração de página inteira)
- Botão "usar em todas" — aplica a posição relativa ajustada ao livro inteiro
- Botão "girar" (90° horário/anti-horário)

**Saída:** cada folha dividida vira duas páginas, na ordem esquerda → direita.

### 4.2 Limpar a folha — os três filtros

Todos precisam remover o fundo amarelado do papel envelhecido.

#### a) Preto e branco (Eco)
```python
# Usar DoxaPy com Sauvola ou Wolf
# Parâmetros de partida (deixar ajustáveis em constantes no topo do arquivo):
JANELA = 75          # tamanho da janela local (ímpar); ~1/20 da altura da página
K_SAUVOLA = 0.2      # sensibilidade
```
- Converter para escala de cinza
- Aplicar binarização adaptativa local (Sauvola ou Wolf via DoxaPy)
- Opcional: despeckle (remover componentes conectados com menos de ~8 px)
- Salvar como **1 bit** no PDF (arquivo fica minúsculo)

**Por que Sauvola/Wolf:** é o que o ScanTailor usa. Resolve amarelado E bleed-through (texto do verso transparecendo) de uma vez — que era o problema não resolvido nas versões anteriores.

#### b) Melhorar
Normalização de iluminação, preservando cor:
```python
# 1. Estimar o fundo: desfoque forte
fundo = cv2.GaussianBlur(img, (0,0), sigmaX=altura/20)
# 2. Dividir a imagem pelo fundo, por canal
normalizada = (img.astype(float) / (fundo.astype(float) + 1)) * 255
# 3. Cortar em 0-255 e normalizar contraste suavemente
```
- Fundo fica branco limpo, **cores originais preservadas**
- NÃO saturar nem realçar — apenas limpar
- Para documentos coloridos que precisam ficar fiéis

#### c) Mágico pro
Base do "Melhorar" + realce estilo magic color:
```python
# 1. Mesma normalização de iluminação do Melhorar
# 2. CLAHE no canal L (espaço LAB), clipLimit=2.0, tileGridSize=(8,8)
# 3. Saturação: converter para HSV, multiplicar canal S por 1.6
# 4. Nitidez (unsharp mask): img + 0.6 * (img - GaussianBlur(img))
# 5. Empurrar o branco: pixels acima de ~230 viram 255
```
- Resultado: cor viva, texto nítido, fundo branco
- Para capas e páginas ilustradas

#### d) Original
Não processa. Copia a página como está.

**Filtro por página (obrigatório):** igual ao CamScanner — o filtro vale **por página**, e páginas diferentes podem ter filtros diferentes dentro do mesmo livro, gerando **um PDF só** no final.

Casos reais que precisam funcionar:
- Livro inteiro em Preto e branco, **só a capa** em Mágico pro
- Miolo em Preto e branco, **as páginas com gravura** em Melhorar
- Uma página específica que ficou ruim no filtro geral, trocada só ela

Como o usuário aplica:
- **"só nesta página"** — muda apenas a página atual
- **"usar em todas"** — aplica ao livro inteiro
- **"só nas próximas"** — aplica desta página em diante (útil quando o livro muda de característica no meio, tipo um caderno de fotos)

O filtro escolhido fica salvo em `ConfigPagina.filtro` de cada página. O "filtro padrão" da tela 2 é apenas o valor inicial de todas — a partir daí cada página é independente.

### 4.3 Sistema de alertas — o programa avisa onde pode ter errado

Princípio central do aplicativo: **o programa faz tudo sozinho, mas é honesto sobre onde teve dificuldade.** O usuário não deve conferir 500 páginas uma a uma — deve conferir só as que o programa marcou. Isso é o que separa este app do ScanTailor (onde tudo é manual) e do CamScanner (que não avisa nada).

Em `core/analise.py`, cada página recebe uma lista de alertas. Casos a detectar:

| Alerta | Como detectar | Mensagem ao usuário |
|---|---|---|
| **Página colorida** | HSV: saturação média e % de pixels com S > 40 acima do limiar | "Esta página tem cor. Quer usar Mágico pro em vez de preto e branco?" |
| **Lombada incerta** | Vale de intensidade raso, ou longe do centro (fora de 40–60%) | "Não tenho certeza de onde cortar. Confira a linha." |
| **Não parece dupla** | Página em retrato num livro onde as outras são paisagem | "Esta folha parece ter uma página só. Confirme se devo dividir." |
| **Muito torta** | Ângulo de deskew detectado acima de 3° | "Esta página estava bem torta. Veja se ficou certa." |
| **Ângulo suspeito** | Detecção de ângulo com baixa confiança (variância pouco definida) | "Não consegui achar o alinhamento do texto direito." |
| **Página em branco** | Quase nenhum pixel escuro após binarizar | "Esta página parece estar em branco. Quer apagar?" |
| **Página escura demais** | Após o filtro, > 40% de pixels pretos | "Ficou muito escura. Tente 'mais fraco' na força do preto." |
| **Página apagada demais** | Após o filtro, < 1% de pixels pretos (texto sumiu) | "O texto quase sumiu. Tente 'mais escuro'." |
| **Corte pegou conteúdo** | O recorte automático de bordas encostou em pixels escuros | "O corte da borda pode ter pegado parte do texto." |
| **Resolução baixa** | Menos de ~150 DPI estimados | "Esta página foi escaneada em qualidade baixa. O resultado pode não ficar bom." |
| **Tamanho diferente** | Dimensões destoando das demais páginas do livro | "Esta folha tem tamanho diferente das outras." |

**Como mostrar:**

1. **Contador no topo da tela de conferir**, clicável:
   ```
   ⚠ 7 páginas para você olhar
   ```
   Clicar leva para a primeira delas. `Tab` pula para a próxima.

2. **Miniatura destacada em laranja** com "!" na tira inferior. Página sem alerta fica normal.

3. **Faixa explicativa** na página atual, em português simples, dizendo o motivo e **sugerindo a correção**:
   ```
   ⚠ Esta página tem cor — o preto e branco vai perder a ilustração.
     [ usar Mágico pro nesta ]   [ está bom assim ]
   ```
   O botão de sugestão aplica a correção com um clique.

4. **Painel "Páginas para revisar"** — lista todas as páginas com alerta, agrupadas por tipo:
   ```
   Páginas para revisar (7)
   ├ Têm cor (2) ................. págs. 1, 68
   ├ Lombada incerta (3) ......... folhas 12, 34, 51
   ├ Muito tortas (1) ............ pág. 89
   └ Parecem em branco (1) ....... pág. 136
   ```
   Clicar num item leva direto à página.

5. **Aviso antes de processar:** se ainda houver páginas não revisadas, perguntar:
   "Ainda tem 3 páginas que eu não tive certeza. Quer conferir antes ou processar assim mesmo?"
   Nunca bloquear — apenas avisar. O usuário pode processar sem revisar.

**Nunca alertar à toa:** página comum, só de texto, bem escaneada, não gera alerta nenhum. Se o programa marcar tudo, o alerta perde a função. Calibrar os limiares para que, num livro bem escaneado, menos de 10% das páginas sejam marcadas.

**REGRA IMPORTANTE — o botão de sugestão NÃO substitui o controle manual.**
O botão do alerta é apenas um atalho para a correção mais provável. **Todos** os controles manuais da seção 4.6 continuam disponíveis o tempo todo, com ou sem alerta:

| O alerta oferece | O usuário também pode, sempre |
|---|---|
| "usar Mágico pro nesta" | escolher qualquer um dos 4 filtros, inclusive um não sugerido |
| "aceitar o corte" | arrastar a linha de corte para onde quiser |
| "tente mais fraco" | usar o controle de força do preto livremente |
| "quer apagar?" | apagar ou manter, por decisão própria |
| "confira se ficou reta" | ajustar o ângulo na mão, arrastando |

E o contrário também vale: **páginas sem alerta nenhum podem ser ajustadas normalmente**. O usuário navega por qualquer página e muda o que quiser, mesmo que o programa tenha achado que estava tudo certo. O alerta chama atenção, nunca restringe.

### 4.4 Endireitar folhas tortas (deskew)
- Detectar o ângulo pelo **perfil de projeção**: rotacionar de -5° a +5° em passos de 0.1°, calcular a variância das somas por linha, escolher o ângulo de maior variância (texto alinhado = picos e vales bem marcados)
- Alternativa mais rápida: `cv2.minAreaRect` sobre os pixels de texto
- Rotacionar preenchendo com branco
- **Limitar a ±5°** — não mexer se o ângulo detectado for maior (provavelmente é erro de detecção)
- Se o ângulo for menor que 0.1°, não fazer nada (evita perda de qualidade à toa)

### 4.5 Montar cadernos para impressão (imposição)

- Reorganizar as páginas em cadernos (assinaturas) para imprimir frente e verso, dobrar ao meio e fechar
- Páginas por caderno configurável, **múltiplo de 4**, padrão **20**
- Completar com páginas em branco quando não fechar a conta
- Para um caderno de N páginas, a ordem de cada folha é:
  ```
  folha i (0-based), frente: [N - 2i]  [1 + 2i]
  folha i,           verso:  [2 + 2i]  [N - 1 - 2i]
  ```
- **Montar duas páginas por folha já no PDF de saída** (folha A4 paisagem com duas páginas lado a lado). O usuário só manda imprimir frente e verso — sem configurar nada no Acrobat
- Ao final, gerar instruções de impressão em português na tela final

**OTIMIZAÇÃO IMPORTANTE:** se **apenas** esta opção estiver marcada (sem filtro, sem dividir, sem endireitar), copiar as páginas direto com PyMuPDF **sem rasterizar** — preserva qualidade e texto vetorial, e é muito mais rápido.

### 4.6 Ajustes manuais (o automático propõe, o usuário corrige)

Filosofia: o programa faz tudo sozinho e mostra o resultado. Quando erra, o usuário corrige **sem precisar entender de técnica**. Nada de campos numéricos ou termos como "limiar" — sempre linguagem do dia a dia.

**a) Força do preto e branco**
- Controle de três posições na aba Filtro, visível apenas quando "Preto e branco" está selecionado:
  ```
  Força do preto:   [ mais fraco ]  [ normal ]  [ mais escuro ]
  ```
- Internamente ajusta o `k` do Sauvola: mais fraco ≈ 0.34, normal ≈ 0.2, mais escuro ≈ 0.1
- Resolve os dois casos comuns: texto que sumiu (papel muito claro) e página que ficou suja de manchas (papel muito escuro)
- Prévia atualiza na hora
- Vale por página, com os mesmos botões "usar em todas" / "só nas próximas"

**b) Cortar as bordas**
- Detectar automaticamente a área útil da página e recortar: borda preta do scanner, sombra que sobra da lombada, faixa escura da margem
- Método: binarizar, achar o retângulo que contém o conteúdo, deixar uma folga de ~2% e cortar
- Na prévia, mostrar um **retângulo com alças arrastáveis** — o usuário puxa se o corte pegou texto ou deixou sujeira
- Checkbox próprio na tela 2: "Cortar as bordas — tira a borda preta e a sombra do scanner"
- Botão "usar em todas" (é o caso mais comum: a borda é igual no livro inteiro)

**c) Apagar páginas**
- Na tira de miniaturas, botão para **excluir uma página do resultado**
- Casos reais: páginas em branco no fim do caderno, folha que saiu tremida, dedo do operador aparecendo no scan
- Páginas excluídas ficam acinzentadas na tira, com opção de restaurar
- O contador do topo atualiza ("136 páginas · 2 apagadas")
- **Importante:** se "Montar cadernos" estiver ligado, recalcular a imposição depois das exclusões

**d) Ajustar o ângulo na mão**
- Quando o endireitar automático errar, permitir girar a página **arrastando com o mouse** sobre a prévia
- Mostrar linhas-guia horizontais sobre a imagem para o usuário alinhar com o texto
- Indicador discreto do ângulo atual
- Botão "voltar ao automático"

**e) Desfazer / refazer — ilimitado e salvo em arquivo**

- **Ctrl+Z** desfaz, **Ctrl+Shift+Z** refaz (aceitar também Ctrl+Y como alternativa de refazer)
- **Sem limite de ações.** O usuário pode desfazer quantas vezes quiser, até o começo do projeto
- **O histórico é gravado em arquivo**, não só na memória. Se o programa for fechado no meio de um livro e reaberto depois, o histórico de ações continua disponível e ainda dá para desfazer

**Como implementar (padrão Command):**
NÃO guardar cópias do estado inteiro a cada mexida — com centenas de páginas isso fica pesado. Guardar apenas a **ação**, que ocupa pouquíssimo espaço e torna o desfazer ilimitado viável:

```python
@dataclass
class Acao:
    momento: str          # ISO datetime
    tipo: str             # mudar_filtro | mover_corte | girar | apagar |
                          # restaurar | ajustar_angulo | recortar |
                          # forca_preto | nao_dividir | aplicar_em_todas
    paginas: list[int]    # índices afetados (uma, várias ou todas)
    antes: dict           # valores anteriores dos campos alterados
    depois: dict          # valores novos
    descricao: str        # texto em português: "Filtro da página 42: P&B → Mágico pro"
```

- Manter duas pilhas: `desfeitas` e `refazer`
- Desfazer = aplicar o `antes`; refazer = aplicar o `depois`
- Nova ação depois de um desfazer **limpa** a pilha de refazer (comportamento padrão)
- Ações em lote ("usar em todas") são **uma única ação** com muitos índices — um Ctrl+Z desfaz o lote inteiro, não página por página

**Arquivo de projeto:**
Cada projeto ganha uma pasta própria em `<dados_do_usuario>/EditorImpressao/projetos/<nome>/` contendo:
```
projeto.json     # o Projeto e a lista de ConfigPagina (estado atual)
acoes.jsonl      # uma ação por linha (JSON Lines) — o histórico completo
thumbs/          # miniaturas em cache
```
- Usar **JSON Lines** (uma ação por linha): permite acrescentar ao fim do arquivo sem reescrever tudo, e é seguro se o programa fechar de repente
- Gravar a ação no arquivo assim que ela acontece (append), não só ao sair
- Ao reabrir o projeto, ler `projeto.json` para o estado e `acoes.jsonl` para o histórico
- Registrar também a posição atual na pilha, para o refazer sobreviver ao fechamento

**Na interface:**
- Botões ↶ ↷ no canto da tela de conferir, desabilitados quando não há o que desfazer/refazer
- Ao passar o mouse, mostrar a descrição da ação: "Desfazer: Filtro da página 42"
- Painel opcional "Histórico de ações" (lista com hora e descrição em português), com a possibilidade de clicar numa ação e voltar o projeto àquele ponto

**Fora de escopo (não implementar):** seleção de conteúdo e margens uniformes ao estilo ScanTailor. É a etapa mais trabalhosa daquele programa, dá pouco retorno para reimpressão e é onde os usuários desistem. Fica para uma versão futura, se fizer falta.

---

### 4.7 Atalhos de teclado

Para quem processa muitos livros, atalho economiza horas:

| Tecla | Ação |
|---|---|
| `←` `→` | página anterior / próxima |
| `Espaço` | marcar como "está certo" e ir para a próxima |
| `Tab` | pular para a próxima página marcada em laranja |
| `1` `2` `3` `4` | aplicar Original / P&B / Melhorar / Mágico pro |
| `R` | girar 90° |
| `Delete` | apagar a página |
| `Ctrl+Z` | desfazer |
| `Ctrl+Shift+Z` ou `Ctrl+Y` | refazer |
| `Ctrl+Enter` | confirmar e processar |

Mostrar uma legenda discreta dos atalhos no rodapé da tela de conferir.

---

## 5. Interface — layout de cada tela

Janela: mínimo 1000x680, redimensionável. Tema claro por padrão.

### TELA 1 — Início

```
┌──────────────────────────────────────────────────────────────┐
│  [icone] Editor de Impressão                      – ▢ ✕      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│      ┌────────────────────────────────────────────────┐      │
│      │                                                │      │
│      │              [ícone de arquivo]                │      │
│      │                                                │      │
│      │        Arraste o PDF do livro aqui             │      │
│      │         ou clique para procurar                │      │
│      │                                                │      │
│      └────────────────────────────────────────────────┘      │
│              (borda tracejada, aceita drag & drop)           │
│                                                              │
│   Projetos recentes                            [ver todos]   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [min] Gradus Primus            10/07/2026 · 136 págs   │  │
│  │       Preto e branco                  [abrir] [pasta]  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [min] Missal Romano 1962       08/07/2026 · 232 págs   │  │
│  │       Mágico pro                      [abrir] [pasta]  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [min] Catecismo de Trento      02/07/2026 · 180 págs   │  │
│  │       Melhorar                        [abrir] [pasta]  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

- Área de arrastar: borda tracejada, muda de cor ao arrastar por cima
- Cada linha do histórico: miniatura da primeira página, nome, data, nº de páginas, filtro usado
- "abrir" recarrega o projeto com as mesmas configurações; "pasta" abre a pasta do arquivo gerado
- Se não houver histórico, mostrar mensagem simpática no lugar da lista

### TELA 2 — O que fazer

```
┌──────────────────────────────────────────────────────────────┐
│  [icone] Editor de Impressão      Gradus Primus.pdf · 68 f.  │
├──────────────────────────────────────────────────────────────┤
│  Marque o que você quer fazer                                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [x]  [ic] Dividir folhas ao meio                       │  │
│  │           esta folha tem 2 páginas do livro            │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Limpar a folha                               │  │
│  │           tira o amarelado                             │  │
│  │                                                        │  │
│  │      ( ) Original  (o) Preto e branco                  │  │
│  │      ( ) Melhorar  ( ) Mágico pro                      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Endireitar folhas tortas                     │  │
│  │           corrige páginas inclinadas                   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [x]  [ic] Cortar as bordas                             │  │
│  │           tira a borda preta e a sombra do scanner     │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [ ]  [ic] Montar cadernos para impressão               │  │
│  │           páginas por caderno: [ 20 ▾]                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ (i) Vou dividir as 68 folhas em 136 páginas, endireitar│  │
│  │     as tortas e deixar tudo em preto e branco.         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  [ voltar ]                        [   Conferir  →   ]       │
└──────────────────────────────────────────────────────────────┘
```

- Os filtros só aparecem quando "Limpar a folha" está marcada
- O campo de páginas por caderno só aparece quando "Montar cadernos" está marcada
- A caixa (i) é um resumo em português, **atualizado ao vivo** conforme as marcações
- Se nada estiver marcado, o botão fica desabilitado

### TELA 3 — Conferir (a prévia mora aqui)

Uma tela só, com abas internas. As abas aparecem conforme o marcado na tela 2.

```
┌──────────────────────────────────────────────────────────────┐
│  Conferir antes de processar        ⚠ 3 folhas para olhar    │
├──────────────────────────────────────────────────────────────┤
│  ┌ Onde cortar ┐ ┌ Filtro ┐                                  │
│  └─────────────┘ └────────┘                                  │
│                                                              │
│                      [ arraste ]                             │
│        ┌──────────────────┊───────────────────┐              │
│        │                  ┊                   │              │
│   ‹    │   página esq.    ┊   página dir.     │    ›         │
│        │                  ┊                   │              │
│        │                  ┊                   │              │
│        └──────────────────┊───────────────────┘              │
│                    (linha tracejada azul,                    │
│                     arrastável com o mouse)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ (i) Achei a lombada e vou cortar na linha azul.        │  │
│  │     Se estiver errado, arraste a linha.                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  [✓ está certo] [✕ não dividir esta] [↻ girar] [⧉ usar em todas]│
│                                                              │
│  Folhas — as laranjas eu não tive certeza                    │
│  ┌──┐┌──┐┌██┐┌!!┐┌──┐┌──┐┌!!┐┌──┐┌──┐┌──┐┌──┐  ...          │
│  └──┘└──┘└██┘└!!┘└──┘└──┘└!!┘└──┘└──┘└──┘└──┘               │
│                                                              │
│  [ voltar ]                  [  Confirmar e processar  ]     │
└──────────────────────────────────────────────────────────────┘
```

**Aba "Filtro":**

```
┌──────────────────────────────────────────────────────────────┐
│  Conferir o filtro              ⚠ 2 páginas coloridas        │
├──────────────────────────────────────────────────────────────┤
│  ┌ Onde cortar ┐ ┌ Filtro ┐                                  │
│                 └────────┘                                   │
│      A mesma página nos quatro filtros — toque no que preferir│
│                                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│  │ [pág.]  │ │ [pág.]  │ │ [pág.]  │ │ [pág.]  │             │
│  │amarelada│ │  P&B    │ │ colorida│ │ vibrante│             │
│  ├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤             │
│  │Original │ │ P&B ✓   │ │Melhorar │ │Mágico pro│            │
│  │sem mexer│ │tira amar│ │mantém cor│ │cor viva │             │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
│                (selecionado com borda azul)                  │
│                                                              │
│  Força do preto:  [mais fraco] [ normal ▪] [mais escuro]     │
│         (só aparece com Preto e branco selecionado)          │
│                                                              │
│  [✓ só nesta] [⧉ usar em todas] [→ só nas próximas] [🔍 ampliar]│
│                                        [🗑 apagar página]     │
│                                                              │
│  Páginas — laranja: achei cor, confira                       │
│  ┌──┐┌──┐┌██┐┌!!┐┌──┐┌──┐┌──┐┌!!┐┌──┐┌──┐  ...              │
│  └──┘└──┘└██┘└!!┘└──┘└──┘└──┘└!!┘└──┘└──┘                   │
│                                                              │
│  ↶ ↷        ← → páginas · Espaço ok · Tab próxima dúvida     │
│  [ voltar ]                  [  Confirmar e processar  ]     │
└──────────────────────────────────────────────────────────────┘
```

**Comum às duas abas:**
- Setas ‹ › e teclas de seta do teclado navegam entre páginas
- Tira de miniaturas embaixo, clicável, com rolagem horizontal
- Páginas com **baixa confiança** destacadas em laranja com "!"
- Contador no topo: "3 folhas para você olhar" — permite pular direto para elas
- Os quatro cartões de filtro mostram a **página real processada**, não exemplos genéricos

**DESEMPENHO OBRIGATÓRIO:**
- Gerar prévia apenas das páginas visíveis, em resolução baixa (~150 DPI, máx. 900 px de altura)
- Pré-carregar as 3 próximas em segundo plano
- Cache em memória limitado (LRU, ~30 páginas)
- Miniaturas em resolução bem baixa (~80 px), geradas em lote em segundo plano
- A tela precisa abrir em poucos segundos mesmo com 500 páginas

### TELA 4 — Pronto

```
┌──────────────────────────────────────────────────────────────┐
│                        [ícone de check]                      │
│                                                              │
│                      Ficou pronto!                           │
│                                                              │
│         Gradus Primus — preto e branco.pdf                   │
│         136 páginas · 4,2 MB · 7 cadernos                    │
│         Salvo em: Documentos / Editor de Impressão           │
│                                                              │
│   ┌────────────────────────────────────────────────────┐     │
│   │ Como imprimir:                                     │     │
│   │ 1. Imprima frente e verso, virando na borda curta  │     │
│   │ 2. Separe as folhas em grupos de 5                 │     │
│   │ 3. Dobre cada grupo ao meio — cadernos prontos     │     │
│   └────────────────────────────────────────────────────┘     │
│                                                              │
│  [ abrir a pasta ]  [ imprimir agora ]  [ fazer outro ]      │
└──────────────────────────────────────────────────────────────┘
```

- O bloco "Como imprimir" só aparece se "Montar cadernos" foi usado
- Registrar o trabalho no histórico ao chegar nesta tela

### Tela de progresso (durante o processamento)

```
        Processando o livro...

        ████████████████░░░░░░░░░░░  62%

        Página 84 de 136 · faltam ~40 segundos

              [ cancelar ]
```

- Estimativa de tempo baseada na média das páginas já processadas
- Cancelar precisa funcionar de verdade e deixar o programa em estado limpo

---

## 6. Modelos de dados

```python
@dataclass
class ConfigPagina:
    indice: int
    dividir: bool = True
    posicao_corte: float = 0.5      # 0.0 a 1.0, relativo à largura
    confianca_corte: float = 0.0    # 0.0 a 1.0
    rotacao: int = 0                # 0, 90, 180, 270
    angulo_manual: float | None = None   # deskew ajustado na mão; None = automático
    recorte: tuple | None = None    # (x, y, w, h) relativo 0-1; None = automático
    filtro: str = "preto_e_branco"  # original | preto_e_branco | melhorar | magico_pro
    forca_preto: str = "normal"     # mais_fraco | normal | mais_escuro
    apagada: bool = False
    tem_cor: bool = False
    alertas: list[str] = field(default_factory=list)  # ver seção 4.3
    revisada: bool = False          # usuário já olhou e aprovou
    precisa_revisao: bool = False

@dataclass
class Projeto:
    caminho_entrada: str
    caminho_saida: str
    dividir_folhas: bool
    limpar: bool
    filtro_padrao: str
    endireitar: bool
    cortar_bordas: bool
    montar_cadernos: bool
    paginas_por_caderno: int = 20
    paginas: list[ConfigPagina] = field(default_factory=list)
```

**Histórico de ações:** ver seção 4.6(e). Guardar **ações** (padrão Command), não cópias de estado — isso permite desfazer ilimitado. Persistir em `acoes.jsonl` dentro da pasta do projeto.

**Histórico** (`historico.json` na pasta de dados do usuário):
```json
{
  "projetos": [
    {
      "nome": "Gradus Primus",
      "caminho_entrada": "C:/.../gradus.pdf",
      "caminho_saida": "C:/.../Gradus Primus - preto e branco.pdf",
      "data": "2026-07-10T14:32:00",
      "num_paginas": 136,
      "filtro": "preto_e_branco",
      "funcoes": ["dividir", "limpar", "endireitar"],
      "miniatura": "thumbs/gradus.png"
    }
  ]
}
```

---

## 7. Linguagem da interface

Português do Brasil, sem jargão técnico. Obrigatório:

| Nunca escrever | Escrever assim |
|---|---|
| imposição | montar para impressão |
| deskew | endireitar folhas tortas |
| DPI / resolução | qualidade: normal / alta |
| split / binarização | dividir folhas ao meio / preto e branco |
| threshold, kernel, pipeline | (nunca aparecem na interface) |

Mensagens de erro sempre gentis:
- ❌ "FileNotFoundError: [Errno 2]"
- ✅ "Não consegui abrir esse arquivo. Ele pode ter sido movido ou não ser um PDF."

---

## 8. Ordem de construção

Vá por etapas e **me mostre o resultado de cada uma antes de seguir para a próxima**.

**Etapa 1 —** Estrutura de pastas + `core/pdf_io.py`
Abrir PDF, extrair página como array numpy, escrever imagem de volta como página. Script de teste por linha de comando.

**Etapa 2 —** `core/filtros.py` com os três filtros
Antes de escrever, **releia a seção 1.1** e estude as abordagens dos projetos de referência.
**Testar em páginas reais e me mostrar as imagens antes de qualquer interface.** Esta é a parte mais importante do projeto — foi onde as versões anteriores falharam. Gere um comparativo lado a lado (original / P&B / melhorar / mágico pro) para eu avaliar.

**Etapa 3 —** `core/dividir.py` + `core/endireitar.py`
Testar a detecção de lombada num PDF real com folhas duplas e mostrar onde ele cortaria.

**Etapa 4 —** `core/cadernos.py`
Imposição. Reaproveitar a lógica do `imposicao_cadernos.py` que vou anexar.

**Etapa 5 —** `core/analise.py` + `core/pipeline.py`
Amarra tudo, página por página, com callback de progresso.

**Etapa 6 —** Interface PySide6, uma tela por vez, na ordem 1 → 2 → 3 → 4.

**Etapa 7 —** Histórico.

**Etapa 8 —** Empacotamento com PyInstaller e teste do `.exe` em máquina limpa.

---

## 9. Qualidade

- Escrever testes simples para o `core/` conforme for construindo (pytest)
- Usar `git` desde o primeiro commit, com um commit por etapa. A versão anterior virou uma bagunça de arquivos duplicados (`app__1_.html`, `app__2_.html`, cinco `.exe` idênticos) por não ter controle de versão
- Type hints no `core/`
- Comentários em português nas partes de algoritmo, explicando o *porquê*

---

## 10. Critérios de aceitação

O aplicativo está pronto quando:

1. Abre um PDF de 500+ páginas sem travar e sem estourar memória
2. Detecta e divide corretamente folhas com duas páginas, permitindo correção manual
3. O filtro Preto e branco remove o amarelado **e** o texto do verso transparecendo
4. O filtro Mágico pro deixa capas coloridas vivas e nítidas, com fundo branco
5. É possível usar cada função isoladamente ou em qualquer combinação
6. É possível aplicar filtros diferentes em páginas diferentes do mesmo livro, gerando um PDF só
7. O programa avisa onde teve dificuldade (cor, lombada, torta, branca, escura demais) e sugere a correção com um clique
8. Num livro bem escaneado, menos de 10% das páginas são marcadas para revisão — o alerta não vira ruído
9. A tela de conferir abre em poucos segundos mesmo com livros grandes
10. O PDF de cadernos imprime corretamente em frente e verso, sem configurar nada no Acrobat
11. O histórico guarda e reabre projetos anteriores
12. Todo ajuste automático pode ser corrigido na mão: linha de corte, ângulo, recorte, filtro, força do preto
13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz
14. Fechar e reabrir o programa preserva o projeto **e o histórico de ações** — ainda é possível desfazer
15. Roda como `.exe` único numa máquina sem Python instalado

---

**Comece pela Etapa 1 e me mostre o resultado antes de continuar.**

---

# PARTE 3 — Material de apoio

Anexar ao Claude Code junto com o prompt:

1. **`imposicao_cadernos.py`** — a lógica de imposição que já funcionava
2. **PDF do Gradus Primus** (Paulo Rónai, Cultrix) — arquivo de teste ideal:
   - 68 folhas, todas em paisagem com duas páginas do livro por folha
   - sombra de lombada bem visível no meio
   - capa colorida azul, miolo em preto e branco
   - papel envelhecido, levemente amarelado
   - cobre os casos de dividir + filtro por página + detecção de corC:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf


---

# APÊNDICE B — O prompt de testes

Pedido 14, de 18/07/2026. Define os quatro casos que são o critério de sucesso do Kaique, e o teste decisivo contra o CamScanner.

---


# Prompt de testes — colar no Claude Code

---

## ⚠ IMPORTANTE — LEIA ANTES DE COMEÇAR

Isto é uma bateria de **TESTES no aplicativo que VOCÊ JÁ CONSTRUIU**, que está em `C:\Users\fotog\Desktop\EditorImpressao`.

- **NÃO** recomece o projeto do zero
- **NÃO** reescreva módulos que já funcionam
- **NÃO** mude a arquitetura

O que eu quero é:
1. **RODAR** o programa existente com esses livros
2. **MEDIR e RELATAR** o que acontece
3. **CORRIGIR** apenas os problemas específicos que os testes revelarem, com a menor alteração possível

Antes de mexer em qualquer arquivo, me diga **o que pretende alterar e por quê**. Ajuste de parâmetro (janela e `k` do Sauvola, limiares de detecção de cor, ângulo de deskew) é bem-vindo. Reescrita de módulo, só se eu autorizar.

**Faça commit no git antes de começar os testes**, para dar para voltar atrás se algo quebrar.

---

## ONDE ESTÃO OS ARQUIVOS

Os PDFs de teste estão em:

```
C:\Users\fotog\Desktop\LIVROS PARA FAZER TESTE
```

Use essa pasta em todos os testes (ignore qualquer menção anterior a `pdfs_teste/`).

**Atenção:** o nome da pasta tem espaços — use aspas nos caminhos para não dar erro.

**NÃO modifique nem sobrescreva os PDFs originais.** São digitalizações de manuscritos e impressos históricos, arquivos do acervo do instituto. Trabalhe sempre gerando cópias em outra pasta.

Salve os relatórios `.txt` e as imagens **dentro dessa mesma pasta**, ao lado dos PDFs, para eu conferir tudo junto.

---

## PARTE 1 — O QUE O USUÁRIO FINAL PRECISA (critério de sucesso)

O Kaique é o impressor que vai usar este programa. Ele descreveu com as próprias palavras os problemas reais que enfrenta. **Isto é o critério de sucesso** — se o programa resolver estes quatro casos, está pronto; se não, não serve.

### Caso 1 — Folha amarelada com texto preto
Palavras dele: *"remover o amarelo e deixar as letras"*
→ filtro **Preto e branco**

### Caso 2 — Livro antigo amarelado COM imagens coloridas
Palavras dele: *"tem que preservar... ele vai remover o fundo amarelo e vai deixar as partes coloridas, as pinturas, e ele dá até uma melhorada nas cores"*
→ filtros **Melhorar** e **Mágico pro**
→ Note que ele espera **remover o amarelo E preservar a cor ao mesmo tempo** — não é "ou um ou outro"

### Caso 3 — Páginas tortas
→ **endireitar (deskew)**

### Caso 4 — O MAIS DIFÍCIL: bleed-through
Palavras dele: *"a folha é tão antiga que ela já está quase transparente, então as letras da parte de trás acabam aparecendo. Esses filtros no scanner, ele remove."*

→ O papel envelheceu tanto que ficou translúcido e o texto do verso aparece por trás.
→ **O CamScanner que ele usa hoje JÁ RESOLVE isso.** Nosso programa precisa resolver pelo menos tão bem.
→ É exatamente para isso que está o **DoxaPy com Sauvola/Wolf** na especificação.
→ **Se este caso não for resolvido, o programa não substitui o CamScanner e o projeto falha.**

---

## PARTE 2 — FICHA ESCRITA DE CADA LIVRO

Para cada PDF da pasta, gere um arquivo `.txt` com o **mesmo nome do PDF**, salvo na mesma pasta.
Exemplo: `Graduale - Saeculum XIV.txt`

Escreva em português, de forma legível para quem **não é técnico**. Modelo:

```
ARQUIVO: Graduale - Saeculum XIV.pdf
Testado em: 18/07/2026 16:30

O QUE ESTE ARQUIVO É
- 320 páginas · 277 MB · ~400 DPI
- folhas duplas: sim / não
- colorido / cinza / preto e branco
- estado do papel: amarelado / manchado / translúcido

O QUE O PROGRAMA DETECTOU
- páginas com cor: 45  (págs. 1, 3, 7, ...)
- páginas tortas: 12   (maior ângulo: 4,2°)
- páginas em branco: 2
- lombada incerta: 5
- alertas disparados: [lista por tipo]
- os alertas faziam sentido? [sua avaliação honesta]

DESEMPENHO
- tempo total: 4 min 12 s
- tempo por página: 0,8 s
- PICO DE MEMÓRIA: 1,2 GB
- tamanho do arquivo final: 18 MB (redução de 93%)

RESULTADO DE CADA FUNÇÃO
- dividir folhas: acertou 315 de 320 — errou nas págs. X, Y
- endireitar: ok / problemas em...
- cortar bordas: ok / cortou texto na pág...
- filtro preto e branco: tirou o amarelo? tirou o bleed-through?
                         o texto ficou nítido ou empastelado?
- filtro melhorar: preservou as cores? removeu o amarelo?
- filtro mágico pro: melhorou ou exagerou?
- montar cadernos: 16 cadernos · numeração conferida: sim/não

OS 4 CASOS DO KAIQUE NESTE ARQUIVO
1. amarelado com texto preto: resolvido / parcial / não resolvido
2. amarelado com imagem colorida: resolvido / parcial / não
3. páginas tortas: resolvido / parcial / não
4. bleed-through: resolvido / parcial / NÃO RESOLVIDO
   (se não resolveu, explique o porquê e o que tentou)

PROBLEMAS ENCONTRADOS
- [lista honesta, sem suavizar]

IMAGENS GERADAS
- pasta: resultados/Graduale/
```

Gere também um **`RELATORIO_GERAL.txt`** na pasta, contendo:
- tabela comparando os 9 livros (páginas, tamanho, tempo, memória, acertos)
- ranking: o que o programa resolve bem, o que resolve mal, o que não resolve
- sua recomendação do que ajustar primeiro, em ordem de prioridade

---

## PARTE 3 — TESTES POR FUNÇÃO

Rode cada função **isoladamente**, para saber exatamente qual falha:

1. só dividir folhas
2. só endireitar
3. só cortar bordas
4. só filtro — os quatro, um de cada vez
5. só montar cadernos
6. tudo junto

Reporte o resultado de cada combinação por livro.

---

## PARTE 4 — ATENÇÃO ESPECIAL A ESTES ARQUIVOS

### Memória — os arquivos grandes
`Graduale` (277 MB), `Marial de sermoens` (209 MB), `Livro de Horas` (108 MB).

São o teste real da regra de memória. Meça o pico e **reporte com honestidade** — se estourar ou demorar demais, é exatamente o que preciso saber agora.

### Manuscritos iluminados
`Graduale - Saeculum XIV` e `Livro de Horas - Luís XIV` têm iluminuras: letras capitulares em ouro e vermelho, miniaturas coloridas.

- O filtro **Preto e branco destruiria** essas páginas
- A **detecção automática de cor precisa marcar** todas elas
- Verifique se está acertando e reporte a taxa de acerto
- Me mostre **uma iluminura ampliada** no Original, Melhorar e Mágico pro — quero ver se preserva o ouro e o vermelho sem exagerar na saturação

### Xilogravuras
`Rhetorica Christiana` e `Schön Neues Modell Buch` têm gravuras em preto e branco com traço muito fino.

- Teste se o filtro P&B **preserva o traço ou empastela**
- Ampliação obrigatória de pelo menos duas gravuras

### Bleed-through (o caso 4 do Kaique)
Procure em todos os livros páginas onde o texto do verso aparece por trás.

- Recorte um pedaço onde dê para ver o texto de trás
- Me mostre **o mesmo pedaço ampliado, antes e depois**
- Se ainda der para ler o texto do verso, o filtro **não está bom o suficiente**
- Ajuste janela e `k` do Sauvola até resolver, e me diga quais valores funcionaram melhor para cada tipo de papel

---

## PARTE 5 — TESTES DE ROBUSTEZ

Teste e relate cada um:

1. **cancelar** o processamento no meio — o programa fica em estado limpo?
2. **fechar e reabrir** — o projeto e o histórico de desfazer sobreviveram?
3. **processar o mesmo arquivo duas vezes** — o resultado é idêntico?
4. **PDF protegido por senha** — avisa em português ou trava?
5. **PDF corrompido** — avisa ou trava?
6. **PDF com páginas de tamanhos diferentes** misturados
7. **PDF de 1 página só**
8. **arquivo que não é PDF**, renomeado para `.pdf`
9. **pasta de destino sem permissão** de escrita
10. **espaço em disco insuficiente**

### Vazamento de memória
Processe **5 livros seguidos sem fechar o programa**. Meça a memória depois de cada um. Se só sobe e nunca baixa, tem vazamento — investigue e corrija.

### Integridade da contagem
Confirme que **N folhas duplas viram exatamente 2N páginas**. Confira que nenhuma página se perdeu nem duplicou. Erro aqui passa despercebido e estraga o livro inteiro na impressão.

### Imposição — simular a dobra
Para um caderno de 20 páginas, verifique **programaticamente** que ao dobrar as folhas a sequência sai 1, 2, 3... 20. Me mostre a conta.

### Interface
Abra o programa e: clique em todos os botões de todas as abas, use todos os atalhos de teclado, redimensione a janela em vários tamanhos, desfaça e refaça 20 vezes seguidas, amplie e feche várias vezes, troque de página rapidamente. Anote tudo que travou ou ficou estranho.

---

## PARTE 6 — COMPARAÇÃO COM O CAMSCANNER (teste decisivo)

O CamScanner é o que o Kaique usa hoje. É a régua real.

Prepare o material para eu fazer a comparação:

1. Escolha **5 páginas difíceis**, uma de cada tipo:
   - papel bem amarelado, só texto
   - com bleed-through visível
   - com iluminura colorida
   - com xilogravura de traço fino
   - bem torta
2. Exporte cada uma como **imagem em alta resolução, ANTES do processamento**, numa pasta `para_comparar/`
3. Gere também o **resultado do nosso programa** para cada uma, com o filtro mais adequado
4. Nomeie de forma clara: `01_amarelada_ORIGINAL.png`, `01_amarelada_NOSSO.png`, etc.

Assim eu processo as mesmas páginas no CamScanner e comparo lado a lado.

---

## COMO QUERO O RETORNO

- Seja **crítico e honesto**. Prefiro descobrir agora o que está ruim.
- Não suavize resultado ruim. Se o bleed-through não foi resolvido, diga com todas as letras.
- Ao final, me diga em uma frase: **o programa já substitui o CamScanner para o trabalho do Kaique? Sim, não, ou ainda não.**