# Editor de Impressão: inventário de telas e funções (02/10/2026)

**Para que serve este documento.** O Editor de Impressão é um programa de Windows que recupera PDFs de livros antigos escaneados (séculos XVI a XIX) e prepara o livro para ser reimpresso em cadernos: divide a folha dupla em duas páginas, corta as bordas pretas do scanner, endireita as páginas tortas, deixa o papel branco sem estragar letras e gravuras, e monta os cadernos para imprimir, dobrar e costurar. É um projeto do Instituto São Bento (Pe. Rosenei) para reeditar livros esgotados. **Quem usa no dia a dia é o Kaique, impressor, sem formação técnica**: a tela não pode ter jargão ("Força do preto", nunca nome de algoritmo). **Quem decide é o Samuel**, que confere cada mudança. O fluxo é: arrastar o PDF, marcar o que fazer, conferir página por página, escolher onde salvar e processar. Este inventário descreve **todas as telas que existem hoje** (código do ramo `fase-1`, lido em 02/10/2026), cada botão com o texto exato, as funções agrupadas por assunto, os problemas de tela já conhecidos, o que está planejado e **ainda não existe**, e os prints que já foram tirados. Serve para uma conversa do Claude desenhar como as telas novas podem ficar (Fase 4 do plano: layout no estilo Photoshop / After Effects).

**Como ler.** Texto entre aspas é exatamente o que aparece na tela. "De fábrica" é o valor com que o controle começa. "A conferir" quer dizer que eu li o código mas não vi na janela, ou não tenho certeza. Nenhum print novo foi tirado para este documento. A última coluna de cada tela ("Referência") é só para a conversa gerente achar o arquivo.

**Regras de tela que valem para qualquer desenho novo** (do plano e do `CLAUDE.md`): português do Brasil sem jargão; nenhum emoji em rótulo (os ícones são desenhados à mão); a janela nunca congela (todo trabalho pesado roda por trás, com barra de progresso e "cancelar" que funciona); toda função automática tem botão de ligar e desligar (regra 8 do plano); toda área de clicar ou arrastar precisa de pista visual (cursor, alça, contorno); não existe botão "salvar" (o programa grava sozinho, ver seção 3); o programa precisa caber no notebook do Kaique (tela 1920 × 1080 com escala de 125% ou 150% do Windows, área útil de cerca de 1280 × 657 pontos a 150%).

---

## 1. O caminho do usuário

```
Abrir o programa
   |
   v
[TELA INICIAL]  arrastar um PDF novo, clicar para procurar, ou "continuar" um livro já começado
   |                       (menu Arquivo > "Abrir um livro..." / Ctrl+O também abre)
   v
(se o PDF tem fundo separado, do Internet Archive, e ainda não perguntou:)
   caixa "Este livro tem fundo separado. Quer tirar o fundo?"
   |
   v
[O QUE FAZER]  marcar as opções (dividir, limpar + filtro, gravuras e fotos, endireitar, cortar, cadernos)
   |  "voltar" -> TELA INICIAL           "Conferir" ->
   v
[PROGRESSO "Olhando o livro..."]  análise do livro inteiro, com barra e "cancelar"
   |  "cancelar" -> volta para O QUE FAZER (ou para a conferência, se já havia uma)
   v
[CONFERIR]  abas Onde cortar / Bordas / Endireitar / Marcar / Filtro, painéis à direita,
   |         miniaturas embaixo. Aqui se corrige página por página.
   |  menu Arquivo > "Voltar para as opções" -> O QUE FAZER
   |  janelas que abrem por cima: "Ver de perto", "Tamanho da folha", "Configurações"...
   |  "Confirmar e processar" (ou Ctrl+Enter) ->
   v
(se há páginas com dúvida:) caixa "Antes de processar"
   v
[JANELA "Confirmar e processar"]  pasta, nome do arquivo, avisos -> "Processar"
   v
(se o arquivo já existe:) caixa "Já existe um arquivo com esse nome"
   v
[PROGRESSO "Processando o livro..."]  com "cancelar" (volta para CONFERIR)
   v
[PRONTO "Ficou pronto!"]  "abrir a pasta", "imprimir agora", "fazer outro" (-> TELA INICIAL)
```

Outras formas de chegar e de sair:

- **Abrir pelo Windows:** dar dois cliques num PDF associado ao programa abre direto na tela "O que fazer".
- **Mesmo livro de novo:** abrir um PDF que já tem projeto (por qualquer caminho) continua o projeto de antes, com as opções salvas; não cria outro.
- **"continuar" num cartão** da tela inicial pula a tela "O que fazer": vai direto para "Olhando o livro..." e depois para a conferência, na página em que parou.
- **Fechar a janela** a qualquer momento grava tudo antes, sem perguntar nada.
- **A barra de menu** existe em todas as telas, mas fora da tela de conferir só "Arquivo", "Ver" e "Ajuda" ficam acesos (os outros aparecem apagados, para a barra não mudar de largura).

---

## 2. As telas, uma por uma

### 2.0 A barra de menu (no alto da janela, em todas as telas)

Os sete menus: "Arquivo" · "Editar" · "Marcar" · "Filtro" · "Página" · "Ver" · "Ajuda". Fora da tela de conferir, só "Arquivo", "Ver" e "Ajuda" ficam acesos, e dentro de "Arquivo" ficam apagados "Escolher a pasta de saída...", "Nome do arquivo...", "Confirmar e processar" e "Voltar para as opções".

| Menu | Item (texto exato) | Atalho de fábrica | O que faz | Observação |
|---|---|---|---|---|
| Arquivo | "Abrir um livro..." | Ctrl+O | Abre a caixa do Windows "Escolha o PDF do livro" | Funciona em qualquer tela |
| Arquivo | "Livros recentes" | — | Submenu | **Vazio: nada preenche esta lista** |
| Arquivo | "Escolher a pasta de saída..." | — | Caixa do Windows "Onde salvar o livro pronto"; lembra a pasta e mostra o aviso "Pasta escolhida" | Só na conferência |
| Arquivo | "Nome do arquivo..." | — | Caixa "Nome do arquivo" ("Como o PDF pronto vai se chamar:") | Só na conferência |
| Arquivo | "Confirmar e processar" | Ctrl+Enter | Abre a janela "Confirmar e processar" | Só na conferência. **A conferir:** pelo menu (e pelo atalho) parece pular a caixa "Antes de processar", que o botão mostra |
| Arquivo | "Voltar para as opções" | — | Grava e volta para "O que fazer" | Só na conferência |
| Arquivo | "Configurações..." | — | Abre a janela "Configurações" (atalhos de teclado) | |
| Arquivo | "Sair" | Ctrl+Q | Fecha o programa (grava antes) | |
| Editar | "Desfazer" | Ctrl+Z | Desfaz a última ação da conferência | Também Ctrl+Y / Ctrl+Shift+Z para refazer pelo teclado |
| Editar | "Refazer" | Ctrl+Shift+Z | Refaz | |
| Editar | "Mostrar o histórico" | — | — | **Não faz nada (não está ligado a nenhuma ação)** |
| Marcar | "Procurar de novo" | — | Na página atual, tira o que a máquina marcou e procura gravuras e fotos de novo; o que foi marcado à mão fica | Mesmo que o botão "detectar automaticamente" da aba Marcar |
| Marcar | "Limpar tudo" | — | Apaga toda a marcação da página atual | |
| Marcar | "Deixar a folha em branco" | — | Marca a página inteira como papel: ela sai em branco | Desfaz com Desfazer |
| Filtro | "Original", "Preto e branco", "Melhorar", "Mágico pro" | 1, 2, 3, 4 | Troca o filtro da página atual | Itens com marca de escolha, mas **a marca não acompanha a página** (a conferir). **"Tirar o fundo" não está neste menu** |
| Página | "Ir para a página..." | Ctrl+G | Caixa "Ir para a página" ("Página (1 a N):") | |
| Página | "Girar" | — | Gira a folha atual 90 graus | Também tecla R e botão "girar" da aba Onde cortar |
| Página | "Apagar esta página" | Del | Apaga (ou restaura) a página atual | |
| Página | "Restaurar página apagada" | — | — | **Não faz nada** (restaurar só pelo botão "restaurar página" ou pela tecla Del de novo) |
| Ver | "Aproximar" / "Afastar" / "Ajustar à tela" | Ctrl++ / Ctrl+- / Ctrl+0 | — | **Os três não fazem nada** |
| Ver | "Painel: Para revisar", "Painel: Marcar como", "Painel: Filtro da página", "Painel: Histórico" | — | Deveriam mostrar/esconder cada painel da direita | Vêm marcados. **Os quatro não fazem nada** |
| Ver | "Modo comparar" | — | — | **Não faz nada** (o comparar existe só dentro de "Ver de perto") |
| Ajuda | "Lista de atalhos" | F1 | Caixa "Lista de atalhos" | |

Referência: `ui/barra_de_menu.py`, ligações em `ui/janela_principal.py` (`_montar_menu`).

---

### 2.1 Tela inicial

**Para que serve:** abrir um livro novo ou continuar um que já foi começado.

| Elemento | Texto exato | O que faz | Quando aparece / desligado | De fábrica |
|---|---|---|---|---|
| Título | "Editor de Impressão" | — | sempre | |
| Subtítulo | "Recupere um livro escaneado e prepare para reimprimir" | — | sempre | |
| Faixa de arrastar (62 px de altura, borda tracejada, ícone de folha desenhado) | "Arraste o PDF de um livro novo aqui" / "ou clique para procurar no computador" | Soltar um PDF abre o livro; clicar abre a caixa do Windows "Escolha o PDF do livro" (só PDF) | Fica azul enquanto um PDF é arrastado por cima; cursor de mãozinha | |
| Título de seção | "Continuar de onde parou" | — | sempre | |
| Campo de busca | (texto fraco dentro) "procurar pelo nome" | Filtra os cartões pelo nome, com um "x" para limpar | sempre | vazio |
| Grade de cartões | — | Um cartão por livro já aberto, quantos couberem por linha (4 numa tela de 1366) | sempre | |
| Recado da grade vazia | "Nenhum livro ainda. Arraste o primeiro PDF ali em cima para começar." ou 'Nenhum projeto com "…" no nome.' | — | sem projetos / busca sem resultado | |

**O cartão de cada livro** (304 × 220 px):

| Elemento | Texto exato | O que faz | Quando |
|---|---|---|---|
| Capa | miniatura da 1ª página, ou "sem capa" | É o que distingue livros de nome igual | sempre |
| Nome | nome do projeto, cortado com reticências | Dica do mouse mostra o nome inteiro e o caminho do PDF | sempre |
| Linha de detalhe | "N páginas · hoje" (ou "ontem", "há N dias", data) | — | sempre |
| Barra fina de andamento | — | Azul com o andamento; verde cheia se o PDF já foi gerado | livro no lugar |
| Frase do andamento | "X de Y conferidas", "ainda não olhado" ou "pronto, PDF gerado" | — | livro no lugar |
| Botão azul | "continuar" | Confere se o PDF ainda está lá e é o mesmo livro, e retoma o trabalho | livro no lugar, sem PDF gerado |
| Botão branco | "abrir a pasta" | Abre a pasta do PDF pronto | depois de gerar o PDF |
| Cartão laranja + aviso | "o PDF saiu do lugar" e o link "procurar de novo" | O link abre "Onde está o livro de …?" para apontar o PDF | quando o PDF sumiu ou foi trocado |
| Duplo clique no cartão | — | Igual a "continuar" | livro no lugar |
| **Menu do botão direito** | "continuar" (ou "procurar o livro", se perdido) · "começar de novo" · "renomear" · "abrir a pasta de saída" · "remover da lista" | Ver as caixas na seção 2.11 | "abrir a pasta de saída" fica apagado, com a dica "Este livro ainda não gerou PDF nenhum.", até haver PDF |

Atalhos: Ctrl+O (abrir). Referência: `ui/tela_inicio.py`, `ui/widgets/area_arrastar.py`.

---

### 2.2 Tela "O que fazer"

**Para que serve:** escolher, para o livro inteiro, o que o programa vai fazer, olhando o PDF ao lado.

Layout: título em cima; à esquerda (3/5 da largura) um cartão branco com as opções, dentro de uma área com rolagem; abaixo dele uma faixa azul com o resumo; à direita (2/5) o livro para folhear; embaixo, "voltar" à esquerda e "Conferir" à direita.

| Elemento | Texto exato (frase cinza embaixo) | O que faz | Quando aparece / desligado | De fábrica |
|---|---|---|---|---|
| Título | "Marque o que você quer fazer" | — | sempre | |
| Linha do arquivo | "nome.pdf  -  N folhas" | — | sempre | |
| Caixinha | "Dividir folhas ao meio" ("esta folha tem 2 páginas do livro") | Divide cada folha escaneada em duas páginas | sempre | marcada |
| Caixinha | "Limpar a folha" ("tira o amarelado") | Liga os filtros e o grupo "Gravuras e fotos" | sempre | marcada |
| Escolha de um (bolinhas), 2 por linha | "Original" ("não mexe na página") · "Preto e branco" ("tira o amarelado, arquivo pequeno") · "Melhorar" ("limpa o fundo e mantém as cores") · "Mágico pro" ("cor viva e texto nítido") · "Tirar o fundo" ("tira o papel e deixa só o que está impresso") | O filtro com que todas as páginas nascem | só com "Limpar a folha" marcada; "Tirar o fundo" só em PDF com fundo separado (Internet Archive) | "Original" |
| Caixinha (com quadrado) | "No Preto e branco, molduras e iluminuras também em preto e branco" ("desmarcada, a moldura dourada e a iluminura ficam com a cor do original; marcada, saem só com o traço em preto") | Vale para o livro inteiro | só com "Limpar a folha" | desmarcada |
| Título do grupo | "Gravuras e fotos" | — | só com "Limpar a folha" | |
| Caixinha (com quadrado) | "Achar gravuras e fotos" ("separa desenho, foto e moldura do texto, para cada um ser tratado do seu jeito") | É o ligar/desligar do detector de gravuras (desmarcada = não procurar) | só com "Limpar a folha" | marcada |
| Caixinha (com quadrado) | "Este livro tem fotos" ("procura em retângulo, que pega a foto inteira; desmarcada, segue o contorno do desenho") | Troca o contorno "livre" pelo "retangular" no livro inteiro | só com "Achar gravuras e fotos" | desmarcada |
| Botão de texto azul | "Mais opções" / "Menos opções" | Mostra ou esconde as três opções abaixo | só com "Achar gravuras e fotos"; abre sozinho se alguma das três estiver fora do padrão | fechado |
| Deslizante + número | "Sensibilidade" 0 a 100 ("só com fotos: no máximo, o retângulo pega a foto inteira; menos, aperta o retângulo e deixa de fora a beirada mais rala") | Quanto o retângulo abraça a foto | dentro de "Mais opções"; **apagado (cinza) sem "Este livro tem fotos"** | 100 |
| Caixinha (com quadrado) | "Procurar também imagens claras" ("acha desenho e foto bem apagados; pode pegar mancha junto") | Detector mais sensível | dentro de "Mais opções" | desmarcada |
| Caixinha (com quadrado) | "Igualar a luz da página antes" ("acerta a página mais escura de um lado antes de procurar") | Normaliza a iluminação antes de procurar | dentro de "Mais opções" | marcada |
| Caixinha | "Endireitar folhas tortas" ("corrige páginas inclinadas") | Liga o endireitar automático | sempre | marcada |
| Caixinha | "Cortar as bordas" ("tira a borda preta e a sombra do scanner") | Liga o corte automático das bordas | sempre | marcada |
| Caixinha | "Montar cadernos para impressão" ("para imprimir, dobrar ao meio e costurar") | Monta o PDF já na ordem dos cadernos | sempre | **desmarcada** |
| Lista de escolha | "páginas por caderno:" 8 · 12 · 16 · 20 · 24 · 32 · 40 | Tamanho do caderno | só com "Montar cadernos" | 20 |
| Faixa azul de resumo | ex.: "Vou dividir as 80 folhas em 160 páginas, endireitar as tortas e cortar as bordas." Sem nada marcado: "Marque pelo menos uma coisa para eu fazer." | Confirma em português o que foi marcado, ao vivo | sempre, fora da rolagem | |
| Rótulo da coluna direita | "O livro, como está agora" | — | sempre | |
| Visor do livro | a folha como está no PDF, sem filtro | Roda do mouse aproxima; duplo clique abre "Folhear o livro" | sempre | folha 1 |
| Botões de folhear | "<" · "folha N de M" · ">" · "tela cheia" | Viram a folha; "tela cheia" abre "Folhear o livro" | "<" e ">" apagam nas pontas | |
| Botão | "voltar" | Volta à tela inicial | sempre | |
| Botão azul grande | "Conferir" | Começa a análise ("Olhando o livro...") | **apagado se nada estiver marcado** | |

Teclado: setas e Page Up/Page Down viram a folha do visor (quando ele tem o foco).

**Caixinhas sem quadrado visível nesta tela (problema O1):** "Dividir folhas ao meio", "Limpar a folha", "Endireitar folhas tortas", "Cortar as bordas", "Montar cadernos para impressão" e as bolinhas dos filtros. As do grupo "Gravuras e fotos" e a do Preto e branco já têm o quadrado.

Referência: `ui/tela_opcoes.py`, `ui/widgets/folhear_pdf.py`; resumo em `core/pipeline.py` (`resumo_em_portugues`).

---

### 2.3 Janela "Folhear o livro" (tela cheia do PDF original)

**Para que serve:** olhar a folha original grande, antes de escolher as opções.

| Elemento | Texto | O que faz |
|---|---|---|
| Visor | a folha (melhor qualidade que a do lado) | roda do mouse aproxima; com zoom, botão do meio arrasta |
| Botões | "<" · "folha N de M" · ">" · "fechar" (azul) | viram a folha / fecham (volta na folha em que parou) |
| Teclado | setas, Page Up/Down; Esc fecha | |

Abre maximizada. Referência: `ui/widgets/folhear_pdf.py` (`TelaCheiaDoPDF`).

---

### 2.4 Tela de progresso

**Para que serve:** mostrar que o programa está trabalhando, quanto falta, e deixar cancelar.

| Elemento | Texto exato | Quando |
|---|---|---|
| Título | "Olhando o livro..." (análise) ou "Processando o livro..." (gerar o PDF) | |
| Barra de progresso | 0 a 100% | |
| Linha de detalhe | "Analisando a folha N de M", "Página N de M" ou "Montando a folha N de M", e depois de alguns segundos "  -  faltam poucos segundos" / "faltam cerca de N segundos" / "faltam cerca de N minutos" | |
| Botão | "cancelar" | Na análise, volta para "O que fazer" (ou para a conferência de antes, intacta); no processamento, volta para a conferência |

Referência: `ui/tela_final.py` (`TelaProgresso`).

---

### 2.5 Tela de conferir (a tela de trabalho)

**Para que serve:** ver a prévia de cada página e corrigir o que o automático errou, antes de gerar o PDF.

**Como a tela é montada, de cima para baixo:**

1. Barra de abas (só as abas das opções marcadas em "O que fazer").
2. Barra de opções da ferramenta (faixa fina de 38 px; mostra os controles da ferramenta escolhida na trilha).
3. Meio: **trilha de ferramentas** (coluna de 42 px à esquerda) · **a página**, com "<" e ">" dos lados · **coluna de quatro painéis** (172 px à direita, com rolagem).
4. Faixa de explicação (azul quando está tudo bem, laranja quando a página tem um alerta), com o botão laranja de sugestão à direita.
5. Linha de botões da aba atual.
6. Tira de miniaturas, com o botão azul grande "Confirmar e processar" no canto direito.

**Atenção para quem for desenhar:** a trilha de ferramentas, a barra de opções e os painéis "Marcar como" e "Filtro da página" (parte "só neste pedaço") aparecem **em todas as abas**, mas só fazem efeito na aba **Marcar**. Existe também um cabeçalho escondido (título "Confira antes de processar", contador "tudo certo" / "N páginas para você olhar", botões "Desfazer" e "Refazer", e as "observações do livro"), criado mas nunca mostrado; por isso as observações do livro inteiro (ex.: qualidade baixa, uma página por folha) **não aparecem em lugar nenhum** (a conferir).

#### Elementos comuns a todas as abas

| Elemento | Texto exato | O que faz | Quando |
|---|---|---|---|
| Abas | "Onde cortar" · "Bordas" · "Endireitar" · "Marcar" · "Filtro" | Trocam o que a área da página edita | "Onde cortar" só com "Dividir folhas ao meio"; "Bordas" só com "Cortar as bordas"; "Endireitar" só com "Endireitar folhas tortas"; "Marcar" e "Filtro" só com "Limpar a folha" (o "Filtro" aparece também se nenhuma outra aba existir) |
| Setas | "<" e ">" dos lados da página | Página (ou folha) anterior / seguinte | sempre |
| Prévia | "Preparando a prévia..." enquanto não chega; selo "atualizando..." no canto quando muda | Roda do mouse aproxima (até 8x); com zoom, botão do meio (ou Ctrl + botão esquerdo) arrasta a vista; **duplo clique abre "Ver de perto"** | sempre |
| Faixa de explicação | frase da aba (ver cada aba) ou a frase do alerta | — | sempre |
| Botão laranja de sugestão | texto do alerta (tabela de alertas abaixo) | Aplica a correção mais provável | só quando a página tem alerta e ainda não foi conferida |
| Tira de miniaturas | número embaixo de cada miniatura; " !" e moldura laranja nas páginas com dúvida; "apagada" nas apagadas; moldura azul grossa na atual | Clique vai para a página; duplo clique abre "Ver de perto" | sempre; na aba "Onde cortar" mostra folhas, nas outras mostra páginas. Dica do mouse: "A selecionada tem borda grossa. As laranjas são as que eu não tive certeza." |
| Botão azul grande | "Confirmar e processar" | Se houver páginas com dúvida, pergunta antes ("Antes de processar"); depois abre a janela "Confirmar e processar" | sempre |

#### Atalhos de teclado da conferência (todos mudáveis em "Configurações", menos os marcados com *)

| Tecla de fábrica | O que faz |
|---|---|
| Seta esquerda / seta direita | Página anterior / próxima |
| Espaço | "Marcar como certo e avançar" |
| Tab | "Ir para a próxima dúvida" (a próxima página com alerta) |
| 1 · 2 · 3 · 4 | Filtro Original · Preto e branco · Melhorar · Mágico pro (não vale na aba "Onde cortar"; "Tirar o fundo" não tem tecla) |
| Del | Apagar / restaurar a página (não vale na aba "Onde cortar") |
| R* | Girar a folha 90 graus (só se a aba "Onde cortar" existir). **Conflito:** R é também a tecla da ferramenta Retângulo, que é tratada antes; na prática a tecla R escolhe o Retângulo (a conferir) |
| R O L P B V C Z E | Ferramentas de marcar e de navegar (ver aba Marcar) |
| M · T | "Espelhado" · "Proporção travada" da aba Bordas |
| Ctrl+Z · Ctrl+Shift+Z ou Ctrl+Y* | Desfazer · refazer |
| Ctrl+Enter | Confirmar e processar |
| Ctrl+G · Ctrl+O · Ctrl+Q · F1 | Ir para a página · abrir livro · sair · lista de atalhos |

#### Aba "Onde cortar" (edita a FOLHA do PDF: onde fica a lombada)

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Linha azul tracejada vertical, com a pega azul "arraste" no topo | "arraste" | Arrastar muda onde a folha é dividida; cursor de seta para os lados em toda a área | posição achada pela análise |
| Faixa | "Achei a lombada e vou cortar na linha azul. Se estiver errado, arraste a linha." ou "Esta folha não vai ser dividida." | | |
| Botão | "está certo" | Marca a folha como conferida | |
| Botão | "não dividir esta" / "dividir esta" | Liga ou desliga a divisão só desta folha | o texto troca conforme a folha |
| Botão | "girar" | Gira a folha 90 graus | |
| Botão | "usar em todas" | Leva a posição da linha para todas as folhas | |

A tira desta aba mostra **folhas**, não páginas.

#### Aba "Bordas" (edita o corte de cada PÁGINA)

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Retângulo verde com 8 alças verdes (cantos e meios), fora dele escurecido | — | Arrastar alça redimensiona; arrastar dentro move. Cursor muda sobre as alças. **Enquanto arrasta** aparecem etiquetas escuras com as medidas em cm de cada margem e "L × A cm" do tamanho final | Corte automático: o retângulo cobre a folha toda (problema conhecido, Fase 2) |
| Faixa | "Vou cortar a borda sozinho. Arraste o retangulo se quiser mudar." ou "Você ajustou o corte desta página." | | |
| Botão | "está certo" | Marca a página como conferida | |
| Botão | "não cortar esta" | Página sem corte nenhum | |
| Botão | "voltar ao automático" | Desfaz o corte à mão desta página | |
| Botão | "usar em todas" | Leva este corte para todas as páginas | |
| Botão | "tamanho..." | Abre a janela "Tamanho da folha" | **Não faz nada, sem avisar, se a imagem ainda não chegou** (bug conhecido) |
| Botão de liga/desliga | "Espelhado" (dica "Espelhado  (M)") | Arrastar um lado move o lado oposto igual | desligado; liga um desliga o outro |
| Botão de liga/desliga | "Proporção travada" (dica "Proporção travada  (T)") | Mantém a proporção do retângulo | desligado |
| Botão de liga/desliga | "Mover conteúdo" | Troca para arrastar a página dentro da folha escolhida: contorno azul, 4 alças azuis nos cantos (redimensiona proporcional), linhas-guia laranja que "grudam" no centro e nas bordas; cursor de mover | **Apagado até escolher um tamanho de folha em "tamanho..."**. Dica: "Arrastar a página dentro da folha escolhida (aba "tamanho..."). Só disponível quando a folha é maior que o recorte." |
| Lista de escolha | "Qualidade:" "Rápida" · "Média" · "Alta" (dica "Rápida: abre logo. Alta: mais nítida no zoom, demora mais por página.") | Resolução da prévia; fica gravada para as próximas vezes | "Rápida" |

Com uma folha escolhida, a prévia mostra a página já posta na folha, com a margem branca de verdade.

#### Aba "Endireitar" (edita o ângulo de cada PÁGINA)

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Linhas-guia laranja tracejadas horizontais + texto no canto | "inclinacao: +0.0 graus" | Arrastar para os lados **em qualquer ponto da página** gira; ao soltar vira uma ação | **Sem alça nem cursor especial (falta pista visual)** |
| Faixa | "Vou endireitar sozinho. Arraste sobre a página para girar na mao." ou "Você girou esta página em +N graus." | | |
| Botão | "está certo" | Marca como conferida | |
| Botão | "não endireitar esta" | Ângulo zero nesta página | |
| Botão | "voltar ao automático" | Volta ao endireitar automático | |

#### Aba "Marcar" (marcar à mão onde há gravura, letra e papel)

As marcas aparecem pintadas por cima da página: **gravura em laranja-avermelhado, letra em azul, papel em verde** (transparentes). O programa marca sozinho e a pessoa corrige por cima; procurar de novo não apaga o que foi marcado à mão.

**Trilha de ferramentas** (coluna à esquerda; ícone desenhado + letra do atalho embaixo; dica do mouse com o nome; um traço separa as 7 de marcar das 2 de navegar; rola com a roda se não couber):

| Ferramenta (nome na dica) | Tecla | Como se usa (frase que aparece embaixo, na linha de aviso) |
|---|---|---|
| "Retângulo" | R | "Arraste de um canto ao outro." |
| "Oval" | O | "Arraste para desenhar um oval." |
| "Laço" | L | "Contorne a área com o botão apertado." |
| "Ponto a ponto" | P | "Clique ponto a ponto. Duplo clique fecha." (Esc cancela) |
| "Pincel" | B | "Pinte por cima. A roda do mouse muda a espessura." |
| "Varinha mágica" | V | "Clique numa cor e ela pega a mancha inteira." |
| "Pegar tudo desta cor" | C | "Clique numa cor e ela pega TUDO daquela cor na página. A roda do mouse muda o quanto a cor pode variar." |
| "Zoom" | Z | "Clique para aproximar. Com Alt, afasta. A roda do mouse também aproxima e afasta." (cursor em cruz) |
| "Mão" | E | "Arraste para andar pela página aproximada." (cursor de mão) |

De fábrica: "Retângulo".

**Barra de opções** (faixa fina acima da página; muda com a ferramenta):

| Ferramenta | Controles (texto exato) | De fábrica |
|---|---|---|
| todas | rótulo com o nome, ex. "Retângulo:" | |
| Pegar tudo desta cor | "variação" + deslizante + "média"; dica "a roda do mouse também muda a variação" | 30 |
| Varinha mágica | "tolerância" + deslizante; "a roda do mouse também muda a tolerância" | 30 |
| Pincel | "tamanho" + deslizante; "a roda do mouse também muda o tamanho" | 2% da página |
| Zoom | "aproximar" + deslizante + "%"; botão "ajustar à tela"; "clique na página para aproximar; com Alt, afasta" | 100% |
| Mão | "arraste a página para andar por ela" | |
| as 7 de marcar | botões "somar" e "tirar", sempre à direita (o escolhido fica azul) | "somar" |

**Linha de botões da aba Marcar:**

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Rótulo de linha | "Marcação:" | | |
| Botão | "detectar automaticamente" | Procura de novo nesta página (igual a Marcar > "Procurar de novo") | |
| Botão | "usar em todas" (dica "Copia a marcação desta página (gravura, letra, papel) para todas as páginas.") | | Com a página vazia: "Marque ou detecte algo nesta página antes de usar em todas." |
| Botão | "só nas próximas" (dica "Copia a marcação desta página para esta e as páginas seguintes.") | | |
| Rótulo de linha | "Foto:" | | |
| Caixinha (com quadrado) | "Esta página tem foto" | Procura a gravura **só desta página** em retângulo | marcada se o livro está com "Este livro tem fotos"; **apagada** se o livro está em "não procurar" (dica explica) |
| Botão | "usar em todas" / "só nas próximas" (da linha "Foto:") | Leva o "Esta página tem foto" para todas / para as seguintes | |
| Linha de aviso (texto pequeno) | ex.: 'Nada marcado ainda. Clique em "detectar automaticamente" ou marque à mão.', "Procurando de novo, com as opções deste livro. O que você marcou à mão continua.", "Tirei tudo. O filtro volta a tratar a folha inteira igual.", "Esta folha vai sair em branco. Para voltar atrás, desfazer.", "Zoom: 150%", "Peguei 3% da página nessa cor, em 12 pedaços.", "Área pequena demais. Aumente a tolerância com a roda." | Resumo do que está marcado e respostas das ferramentas | |

A faixa desta aba diz "Esta página vai sair em [filtro]." (ou a frase do alerta). Ctrl+Z dentro da página desfaz a última marca.

#### Aba "Filtro" (escolher o filtro de cada PÁGINA)

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Frase de cima | "A mesma página nos quatro filtros - clique no que preferir" (ou "cinco") | | |
| Cartões (um por filtro, com a página de verdade já filtrada) | "Original" ("sem mexer") · "Preto e branco" ("tira o amarelado") · "Melhorar" ("mantem a cor") · "Mágico pro" ("cor viva") · "Tirar o fundo" ("só o que está impresso") | **Clicar escolhe o filtro desta página E abre "Ver de perto"** | O escolhido tem borda azul grossa. "preparando..." até a imagem chegar. "Tirar o fundo" só em PDF com fundo separado (leva 1 a 3 s para aparecer) |
| Bloco "AJUSTE" | medidor: rótulo + ponta esquerda + deslizante com marcas + ponta direita + palavra do valor | Ajuste do filtro desta página, com prévia ao vivo; ao soltar vira uma ação | **Some no "Original" e no "Tirar o fundo"**. Preto e branco: "Força do preto" ("mais fraco" / "mais escuro"); Melhorar: "Clareza do fundo" ("suave" / "bem clara"); Mágico pro: "Intensidade" ("suave" / "bem forte"). Palavras: "bem fraco", "leve", "normal", "forte", "bem forte". De fábrica: meio ("normal") |
| Lista de escolha | "Algoritmo:" "Automático" · "Sauvola (padrão)" · "Otsu (letra grossa/gótica)" · "Wolf (scan de baixo contraste)" | Qual receita de preto e branco usar nesta página | só no Preto e branco; "Automático". **Jargão na tela** |
| Caixinha | "limpar poeirinha" (dica "Remove manchas pretas pequenas demais pra ser letra. Ligado é o comportamento de sempre.") | | só no Preto e branco; marcada. **Sem quadrado visível (O1)** |
| Rótulo | "Aplicar em:" | | |
| Botão azul | "só nesta" | Confirma o filtro só nesta página (marca como conferida) | |
| Botão | "todas" | Leva filtro e ajustes desta página para todas | |
| Botão | "só nas próximas" | Para esta e as seguintes | |
| Botão vermelho (depois de um separador) | "apagar página" / "restaurar página" | Tira a página do PDF final (ou devolve) | o texto troca conforme a página |

Bug conhecido: com Mágico pro, numa janela de 1440 × 880, os botões "Aplicar em" ficam espremidos e sem texto.

#### Os quatro painéis da direita (em todas as abas)

Cada painel recolhe e abre clicando no título.

| Painel | Elementos (texto exato) | O que faz |
|---|---|---|
| "Para revisar" (título com fundo laranja e o total, ex. "Para revisar          5") | Um botão por tipo de alerta, ex. "Lombada incerta   (3)" (dica "páginas: 4, 9, 17"); "nada pendente"; "clicar leva à primeira" | Clicar vai para a primeira página daquele tipo |
| "Marcar como" | "gravura ou foto" · "letra e traço" · "papel" (o escolhido em azul) | O tipo da próxima marca da aba Marcar. De fábrica: "gravura ou foto" |
| "Filtro da página" | nome do filtro + "tecla N"; o deslizante do filtro ("força do preto", "clareza do fundo" ou "intensidade"); "só neste pedaço" com "o mesmo da página" · "Original" · "Preto e branco" · "Melhorar" · "Mágico pro" | O "só neste pedaço" escolhe o filtro do que for marcado daqui em diante na aba Marcar (de fábrica "o mesmo da página"). **O deslizante deste painel parece não gravar: volta ao valor (a conferir)**; o que vale é o do bloco "AJUSTE" |
| "Histórico" | as 12 últimas ações (a mais recente embaixo, em azul), ex. "Filtro da página 12: Original para Melhorar"; dica "clicar volta o trabalho até aqui"; "nada ainda"; "clicar volta até a ação" | Clicar desfaz tudo até aquela ação |

#### Os alertas (frase na faixa laranja e botão de sugestão)

| Nome no painel | Frase na faixa | Botão laranja |
|---|---|---|
| "Tem cor" | "Esta página tem cor - o preto e branco vai perder a ilustração." | "usar Mágico pro nesta" |
| "Desenho ou escrita?" | "Não tenho certeza se esta página é desenho ou escrita. Confira na aba Marcar - se for escrita, marque como letra." | (nenhum) |
| "Conferir o fundo tirado" | "Tirei o fundo desta página, e pode ter sumido escrita fraca ou traço fino junto: confira." | "está bom assim" |
| "Lombada incerta" | "Não tenho certeza de onde cortar. Confira a linha." | "aceitar o corte" |
| "Não parece dupla" | "Esta folha parece ter uma página só. Confirme se devo dividir." | "não dividir esta" |
| "Muito torta" | "Esta página estava bem torta. Veja se ficou certa." | "está bom assim" |
| "Alinhamento duvidoso" | "Não consegui achar o alinhamento do texto direito." | "não endireitar esta" |
| "Parece em branco" | "Esta página parece estar em branco. Quer apagar?" | "apagar esta página" |
| "Ficou escura" | "Ficou muito escura. Tente mais fraco na força do preto." | "usar mais fraco" (**não funciona**, ver seção 4) |
| "Texto quase sumiu" | "O texto quase sumiu. Tente mais escuro." | "usar mais escuro" (**não funciona**) |
| "Corte encostou no texto" | "O corte da borda pode ter pegado parte do texto." | "não cortar esta" |
| "Qualidade baixa" | "Esta página foi escaneada em qualidade baixa. O resultado pode não ficar bom." | "está bom assim" |
| "Tamanho diferente" | "Esta folha tem tamanho diferente das outras." | "está bom assim" |
| "Folha menor que o corte" | "A folha escolhida é menor que o corte desta página - ele não vai caber inteiro nela. Ajuste o tamanho da folha ou o corte." | "está bom assim" |

Referência: `ui/tela_conferir.py`, `ui/widgets/visualizador.py`, `ui/widgets/editor_selecao.py`, `ui/widgets/trilha_ferramentas.py`, `ui/widgets/barra_opcoes.py`, `ui/widgets/paineis.py`, `ui/widgets/cartao_filtro.py`, `ui/widgets/medidor.py`, `ui/widgets/tira_miniaturas.py`; textos dos alertas em `core/analise.py`.

---

### 2.6 Janela "Ver de perto" (a página ampliada)

**Para que serve:** olhar a página grande e em melhor qualidade, e comparar dois filtros lado a lado.

Abre: clicando num cartão de filtro, com duplo clique numa miniatura ou com duplo clique na prévia. O que ela edita depende da aba de onde veio: "Onde cortar" mostra a folha com a linha da lombada (arrastável); "Bordas" mostra o retângulo de corte (arrastável); as outras mostram o filtro.

| Elemento | Texto exato | O que faz | Quando / de fábrica |
|---|---|---|---|
| Rótulo | "Página N de M" ou "Folha N de M" | | |
| Etiqueta azul | nome do filtro, "onde cortar", ou "Filtro A  \|  Filtro B" no comparar | | |
| Botões | "-" (dica "Afastar") · "100%" · "+" (dica "Aproximar") · "ajustar à tela" | Zoom | |
| Botão de liga/desliga | "comparar" | Abre uma segunda página ao lado, com zoom e posição amarrados | desligado |
| Lista de escolha | os filtros do livro | Qual filtro a página da direita mostra | só no comparar; começa num filtro diferente do atual |
| Botão | "X" (dica "Fechar (Esc)") | Fecha | |
| Setas | "<" e ">" | Página anterior / próxima | |
| Rodapé | "Filtro:" + um botão por filtro ("Original", "Preto e branco", "Melhorar", "Mágico pro", "Tirar o fundo") | Escolhe o filtro da página | só no modo filtro |
| Dica do rodapé | "roda do mouse: aproximar   -   arrastar com o botão do meio: mover   -   setas: mudar de página   -   1 2 3 4: filtros   -   Esc: voltar" | | |

Teclado: Esc, setas, + / -, 0 (ajustar), 1 a 4 (filtros). Referência: `ui/tela_ampliada.py`.

---

### 2.7 Janela "Tamanho da folha"

**Para que serve:** escolher o tamanho físico da folha impressa (o corte continua o mesmo; a página é posta dentro da folha, com margem branca).

| Elemento | Texto exato | O que faz | De fábrica |
|---|---|---|---|
| Frase | "Tamanho final da folha impressa:" | | |
| Campo numérico | "Largura:" (em cm, 1 a 200, duas casas) | | o tamanho do corte atual (ou a folha já escolhida) |
| Campo numérico | "Altura:" | | idem |
| Botões | "Papel comum:" "A4" · "A5" · "Carta" | Preenchem os dois campos (21 × 29,7; 14,8 × 21; 21,59 × 27,94) | |
| Aviso laranja | "Esse tamanho é menor que o corte que você já fez (L × A cm) - não vou mudar o seu corte, mas ele não vai caber inteiro na folha." | Só avisa, nunca impede | só quando não cabe |
| Botões | "OK" · "Cancelar" | | |

Referência: `ui/dialogo_tamanho_da_folha.py`.

---

### 2.8 Janela "Confirmar e processar"

**Para que serve:** escolher onde salvar e o nome do PDF, com os avisos, antes de começar a gerar.

| Elemento | Texto exato | O que faz | Quando |
|---|---|---|---|
| Título | "Onde salvar o livro pronto" | | |
| Linha | "Salvar em:" + caminho da pasta (encurtado no meio, dica com o caminho inteiro) + botão "Escolher pasta" | Caixa do Windows "Escolha a pasta onde salvar o PDF" | De fábrica: a última pasta usada |
| Linha | "Nome do arquivo:" + campo (texto fraco "nome do arquivo.pdf") | | De fábrica: nome sugerido pelo livro |
| Aviso vermelho | motivo de a pasta não servir, ex. "Não consegui criar essa pasta. Escolha outra." / "Esse caminho não é uma pasta." | | pasta sem permissão |
| Aviso cinza | "Já existe um arquivo com esse nome - eu pergunto antes de substituir." | | nome repetido |
| Faixa laranja | "Já existe um arquivo chamado **x.pdf** nessa pasta. Se continuar, ele será substituído." | | arquivo já existe (**a conferir:** só se atualiza ao trocar a pasta, não ao digitar o nome) |
| Faixa laranja | "Ainda há **N página(s)** que você não conferiu. Dá para processar assim mesmo, mas o que não foi olhado sai do jeito que o programa decidiu sozinho." | | páginas não conferidas |
| Frase | "N páginas vão para o PDF, e M foram apagadas." | | |
| Botões | "Processar" (azul) · "voltar" | | "Processar" apagado se a pasta não aceita gravar (dica com o motivo) |

Referência: `ui/janela_confirmar.py`, `ui/widgets/destino.py`.

---

### 2.9 Tela "Pronto"

**Para que serve:** dizer onde o PDF ficou, como imprimir os cadernos e se a ordem está certa.

| Elemento | Texto exato | Quando |
|---|---|---|
| Círculo verde com um visto (desenhado) | — | |
| Título | "Ficou pronto!" | |
| Nome | nome do arquivo PDF | |
| Detalhe | "N páginas  -  X,X MB" (+ "  -  N cadernos  -  N folhas para imprimir") | cadernos só com "Montar cadernos" |
| Local | "Salvo em: pasta" | |
| Cartão | "Como imprimir:" 1. "Imprima frente e verso, virando na borda curta." 2. "Separe as folhas em grupos de N." 3. "Dobre cada grupo ao meio - são N cadernos prontos." + recado verde ("Conferido: as N páginas saem na ordem certa depois de dobrar, sem nenhuma repetida nem faltando." ou "... e sobram N páginas em branco no fim do último caderno.") ou vermelho ("... Não imprima assim: avise quem cuida do programa.") | só com "Montar cadernos" |
| Botões | "abrir a pasta" · "imprimir agora" (manda para a impressora padrão do Windows) · "fazer outro" (azul, volta à tela inicial) | |

Referência: `ui/tela_final.py` (`TelaFinal`); textos em `core/cadernos.py`.

---

### 2.10 Janela "Configurações"

**Para que serve:** trocar as teclas de atalho. Pensada para receber outras seções depois.

| Elemento | Texto exato | O que faz |
|---|---|---|
| Título | "Atalhos de teclado" | |
| Frase | "Clique numa tecla e aperte a combinação que você quer usar no lugar." | |
| Lista com rolagem | um nome por linha (ex. "Abrir um livro...", "Recorte: espelhado", "Página anterior", "Marcar como certo e avançar", "Ir para a próxima dúvida", "Retângulo"...) e um campo que captura a tecla | 30 atalhos; grava na hora |
| Aviso vermelho | 'A tecla "X" já é usada por "Y" - escolha outra.' | Recusa tecla repetida |
| Botões | "Restaurar todos os padrões" · "Fechar" | |

Referência: `ui/tela_configuracoes.py`, `atalhos.py`.

---

### 2.11 Caixas de pergunta e de aviso

| Título da caixa | Texto exato | Botões | Quando aparece |
|---|---|---|---|
| "Fundo separado" | "Este livro tem fundo separado. Quer tirar o fundo?" + "Tirar o fundo deixa o papel branco e só o que está impresso, em todas as páginas. Dá para mudar depois, página por página, na lista de filtros." | "Sim, tirar o fundo" · "Não, deixar como está" (padrão; Esc e X valem "Não") | Uma vez por livro, ao abrir um PDF com fundo separado (Internet Archive); volta depois de "começar de novo" |
| "Começar de novo?" | "Isto joga fora todos os ajustes de [livro] e abre o livro limpo. O livro em si não é tocado. O que se perde é a conferência já feita." | "Começar de novo" · "Não, deixar" (padrão) | menu do cartão |
| "Tirar da lista?" | "[livro] sai desta tela e a conferência feita nele se perde. O livro em PDF continua onde está - ele nunca esteve guardado aqui dentro." (+ quantas cópias de segurança vão ficar guardadas e onde) | "Tirar da lista" · "Não, deixar" (padrão) | menu do cartão, "remover da lista" |
| "Renomear" | "Nome deste projeto:" + campo | "OK" · "Cancelar" | menu do cartão (só muda o nome do projeto, não o arquivo) |
| "Este não é o mesmo livro" | "Existe um arquivo chamado X nesse lugar, mas ele não é o livro deste projeto - alguém o substituiu. Não vou aplicar os ajustes deste projeto num livro diferente: isso estragaria o trabalho sem aparecer. Use "procurar de novo" e aponte onde está o livro certo." (ou, ao apontar o arquivo errado: "Esse arquivo não é o livro deste projeto...") | "entendi" | "continuar" ou "procurar de novo" com o PDF trocado |
| (Windows) "Onde está o livro de [livro]?" | caixa de abrir arquivo, só PDF | | "procurar de novo" / "procurar o livro" |
| (Windows) "Escolha o PDF do livro" | caixa de abrir arquivo, "Arquivos PDF (*.pdf)" | | clicar na faixa de arrastar / Ctrl+O |
| "Nome do arquivo" | "Como o PDF pronto vai se chamar:" | "OK" · "Cancelar" | Arquivo > "Nome do arquivo..." |
| "Ir para a página" | "Página (1 a N):" + número | "OK" · "Cancelar" | Ctrl+G |
| (Windows) "Onde salvar o livro pronto" | caixa de escolher pasta | | Arquivo > "Escolher a pasta de saída..." |
| "Pasta escolhida" | "O livro pronto vai para: [pasta]" | "entendi" | depois de escolher a pasta pelo menu |
| "Antes de processar" | "Ainda tem N páginas que eu não tive certeza." + "Quer conferir antes ou processar assim mesmo?" | "conferir" (vai para a próxima dúvida) · "processar assim mesmo" | botão "Confirmar e processar" com páginas em alerta |
| "Já existe um arquivo com esse nome" | "Já existe um arquivo chamado: x.pdf" + "Posso substituir o antigo ou salvar como: x (2).pdf" | "substituir o antigo" · "salvar como x (2).pdf" (padrão) · "cancelar" | arquivo de saída já existe. **"salvar como..." dá erro (ver seção 4)** |
| "Um momento" | "Não consegui fazer isso agora." + "O programa continua funcionando e o seu trabalho está salvo. Tente de novo, ou passe para a próxima página." | "entendi" | qualquer botão da conferência que der erro |
| "Um momento" | avisos diversos, ex. "Não consegui abrir esse arquivo. Ele pode não ser um PDF.", "Comecei a conferência deste livro de novo: [motivo]. O trabalho anterior não foi apagado. Guardei uma cópia dele, que pode ser recuperada: [caminho]", "O computador foi desligado no meio da última gravação, e N ação(ões) do fim se perderam. O resto do trabalho está aqui.", erros da análise ou do processamento ("Não consegui gravar o arquivo. Verifique se ha espaço em disco.") | "entendi" | conforme o caso |
| "Gravuras e fotos" | "As gravuras e fotos vão ser procuradas de novo, com as opções novas, em N páginas já marcadas. O que você marcou à mão fica." (ou "Este livro não vai mais procurar gravuras e fotos: ...") + onde ficou a cópia; ou a frase de quando o detector de gravuras falta ou falha | "entendi" | mudar "Gravuras e fotos" num livro já conferido; detector ausente (uma vez por sessão) |
| "Lista de atalhos" | "O que dá para fazer, e por qual tecla:" + a lista (sai dos próprios menus) | "fechar" e o botão do Qt "Show Details..." (**em inglês**) | F1 |
| "Um momento" | "Aconteceu um problema inesperado, mas o programa continua funcionando." | "entendi" | qualquer erro não previsto |

Referência: `ui/janela_principal.py`, `ui/tela_inicio.py`, `ui/perguntas.py`, `main.py`.

---

## 3. Funcionalidades, por assunto (e em que tela ficam)

**Abrir e guardar o trabalho**

- Abrir livro novo: tela inicial (arrastar ou clicar), Arquivo > "Abrir um livro..." (Ctrl+O), ou dois cliques no PDF no Windows.
- Continuar um livro: cartão da tela inicial ("continuar", duplo clique, menu do botão direito). Volta na página em que parou, com o desfazer da sessão anterior.
- **Não há botão de salvar:** o programa grava sozinho cerca de 0,6 s depois de cada mudança, ao trocar de tela, ao processar e ao fechar. Nunca pergunta "quer salvar?".
- Projeto reconhecido pela "assinatura" do arquivo: mover o PDF de pasta não perde o trabalho; PDF sumido deixa o cartão laranja com "procurar de novo".
- Renomear, começar de novo, remover da lista: menu do botão direito do cartão.
- Cópias de segurança: quando a conferência precisa recomeçar (mudou uma opção que muda o número de páginas, livro trocado, opções de gravura mudadas), o trabalho antigo é guardado ao lado e o aviso diz onde. "Tirar da lista" guarda as cópias na pasta "copias-de-seguranca". **Não existe tela para recuperar essas cópias** (só pelo caminho no aviso).

**Opções do livro inteiro** (tela "O que fazer"): dividir folhas, limpar + filtro do livro, molduras e iluminuras no Preto e branco, gravuras e fotos (achar / tem fotos / sensibilidade / imagens claras / igualar a luz), endireitar, cortar bordas, cadernos.

**Filtros:** "Original", "Preto e branco", "Melhorar", "Mágico pro" e, só em PDF com fundo separado, "Tirar o fundo".
- Filtro do livro: tela "O que fazer".
- Filtro de cada página: aba Filtro (cartões), menu Filtro, teclas 1 a 4, rodapé da "Ver de perto".
- Ajuste do filtro ("Força do preto", "Clareza do fundo", "Intensidade"): bloco "AJUSTE" da aba Filtro (e o deslizante do painel "Filtro da página", que parece não gravar).
- Receita do Preto e branco ("Algoritmo:") e "limpar poeirinha": aba Filtro, só no Preto e branco.
- Levar para outras páginas: "todas" / "só nas próximas" da aba Filtro.
- Filtro só num pedaço da página: painel "Filtro da página" > "só neste pedaço" + marcar a área na aba Marcar.
- Comparar dois filtros: "comparar" na "Ver de perto".

**Gravuras e fotos (separar desenho, foto e moldura do texto)**
- Por livro: grupo "Gravuras e fotos" da tela "O que fazer" (o desligar é desmarcar "Achar gravuras e fotos").
- Por página: "Esta página tem foto" na aba Marcar.
- À mão: aba Marcar (9 ferramentas, somar/tirar, tipo gravura / letra / papel), "detectar automaticamente", "usar em todas", "só nas próximas"; menu Marcar ("Procurar de novo", "Limpar tudo", "Deixar a folha em branco").

**Dividir a folha:** aba "Onde cortar" (linha arrastável, "não dividir esta", "girar", "usar em todas"); opção geral em "O que fazer".

**Bordas e corte:** aba "Bordas" (retângulo, medidas em cm ao arrastar, "não cortar esta", "voltar ao automático", "usar em todas", "Espelhado", "Proporção travada", "Qualidade:"); "Ver de perto" vinda da aba Bordas.

**Tamanho da folha e posição na folha:** "tamanho..." (janela "Tamanho da folha": cm, A4/A5/Carta) e "Mover conteúdo" na aba Bordas.

**Endireitar e girar:** aba "Endireitar" (arrastar, "não endireitar esta", "voltar ao automático"); girar 90 graus na aba "Onde cortar", menu Página e tecla R.

**Apagar páginas:** "apagar página" / "restaurar página" (aba Filtro), menu Página, tecla Del, sugestão "apagar esta página". Página em branco: Marcar > "Deixar a folha em branco".

**Conferir e alertas:** faixa laranja + botão de sugestão em cada aba; painel "Para revisar"; miniaturas laranja; Tab vai à próxima dúvida; Espaço marca como certo e avança; "está certo" / "só nesta" marcam como conferida; caixa "Antes de processar" e aviso na janela "Confirmar e processar".

**Desfazer / refazer:** menu Editar, Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y, painel "Histórico" (clicar volta até a ação). O desfazer sobrevive a fechar o programa. Na aba Marcar, Ctrl+Z dentro da página desfaz só a última marca.

**Navegar e ver de perto:** setas "<" ">", teclas de seta, tira de miniaturas, Ctrl+G, roda do mouse (zoom na prévia), ferramentas "Zoom" e "Mão" (aba Marcar), janela "Ver de perto", "Folhear o livro" (tela "O que fazer").

**Salvar o PDF e imprimir:** "Confirmar e processar" (botão, menu, Ctrl+Enter), janela "Confirmar e processar", Arquivo > "Escolher a pasta de saída..." / "Nome do arquivo...", tela "Pronto" ("abrir a pasta", "imprimir agora").

**Cadernos para impressão:** opção e "páginas por caderno" em "O que fazer"; instruções e conferência automática da ordem na tela "Pronto".

**Configurações:** Arquivo > "Configurações..." (só atalhos de teclado hoje); "Qualidade:" da prévia fica gravada (aba Bordas).

**Ajuda:** F1, "Lista de atalhos".

**O que o programa faz sem tela própria:** OCR (docTR e Kraken instalados, Tesseract desligado) **não aparece em nenhuma tela**; detector de camadas (só aparece como o filtro "Tirar o fundo" e a pergunta); avisos de erro vão para o arquivo `erros.log` (nunca para a tela).

---

## 4. Problemas de tela já conhecidos

**Do plano (Lista de bugs, decisões e Registro de mudanças):**

| Data | Problema | Onde | Situação |
|---|---|---|---|
| 30/09 e 02/10 | **Caixinhas desmarcadas e bolinhas sem quadrado ou círculo visível** na janela real ("Montar cadernos", os filtros...). **Decisão O1 do Samuel (02/10): "todas iguais, com o quadrado visível"** (e os filtros com a bolinha). Hoje só "Gravuras e fotos", a caixinha do Preto e branco e "Esta página tem foto" têm quadrado. Faltam: "Dividir folhas ao meio", "Limpar a folha", "Endireitar folhas tortas", "Cortar as bordas", "Montar cadernos para impressão", "limpar poeirinha" e as bolinhas dos filtros | todo o programa | decidido, não feito |
| 30/09 | Grupo "Gravuras e fotos" espremido e ilegível a 1440 × 880 e cortado a 1600 × 1000 | "O que fazer" | consertado (rolagem), a conferir; prints em 125% e 150% |
| 30/09 | Janela não cabia no notebook do Kaique a 150% (altura mínima 680, tela útil ~657) | janela principal | consertado (mínimo 1000 × 600), a conferir |
| 29/09 | Com Mágico pro, numa janela de 1440 × 880, os botões "Aplicar em" ficam espremidos e sem texto (também sem camadas) | aba Filtro | aberto |
| 29/09 | Aba Bordas: "tamanho..." não faz nada, sem avisar, quando a imagem ainda não chegou | aba Bordas | aberto |
| 28/09 | Aba Bordas mostra a folha inteira quando o corte é automático | aba Bordas | Fase 2 |
| 28/09 | O aviso "encostou no conteúdo" pode não bater com o corte de verdade | alertas | Fase 2 |
| 29/09 | Clicar num cartão de filtro às vezes abre a "Ver de perto" (pelo código, **sempre** abre: é de propósito) | aba Filtro | não investigado |
| 29/09 | "Conferir a pagina 1" sem acento no Histórico | painel Histórico | aberto |
| 29/09 | O aviso do Preto e branco ("O texto quase sumiu. Tente mais escuro.") aparece em página que está em outro filtro | aba Filtro | aberto |
| 01/10 | Aviso falso "Esta página tem cor - o preto e branco vai perder a ilustração" com a caixinha de decoração desmarcada | alertas | aberto |
| 01/10 | O resumo de "O que fazer" ainda diz "deixar tudo em preto e branco", mas moldura e iluminura agora ficam em cor | "O que fazer" | aberto |
| 01/10 | O botão do filtro diz "arquivo pequeno", mas o Preto e branco com decoração em cor gera PDF pesado (até 25,6 MB por página) | "O que fazer" | decisão P3 do Samuel: deixar como está até o 1.6 |
| 29/09 | Resto do bug das caixinhas: o que se muda em "O que fazer" depois de uma conferência ainda se perde nas opções que não mudam o número de páginas | "O que fazer" | aberto |
| 29/09 | Depois de um recomeço, as ações antigas continuam no Histórico | painel Histórico | aberto |
| 29/09 | Projetos antigos sem resumo não aparecem na tela inicial; dois cartões do Boécio com o mesmo nome; projetos de teste aparecendo na tela inicial do Samuel | tela inicial | aberto (apagar só com autorização) |
| 30/09 | Ainda seguram a janela ~0,3 a 0,5 s: leitura das camadas do "Tirar o fundo", o folhear de "O que fazer" nos livros do Internet Archive, gravar o projeto ao abrir a conferência | várias | aberto |
| 15-16/09, 24/09 | Zoom que às vezes não funciona e travamento com muitos cliques (aba Marcar) | aba Marcar | item 3.8 |
| 29/09 | O cartão "Tirar o fundo" leva de 1,2 a 2,8 s para aparecer | aba Filtro | Lista de espera |
| 08/08 | Barra de rolagem cinza médio (`#a8a49e`), intencional: o Kaique pediu preta em 05/08 e foi revertida | todo o programa | decisão do Samuel adiada |

**Achados nesta leitura do código (02/10), não estão na Lista de bugs** — todos "a conferir na janela", porque nenhum foi visto rodando:

1. **Onze itens de menu não fazem nada:** "Livros recentes" (submenu vazio), "Mostrar o histórico", "Restaurar página apagada", "Aproximar", "Afastar", "Ajustar à tela", os quatro "Painel: ..." e "Modo comparar". As teclas Ctrl++, Ctrl+- e Ctrl+0 aparecem no menu mas também não fazem nada.
2. **Botões laranja "usar mais fraco" e "usar mais escuro"** (alertas "Ficou escura" e "Texto quase sumiu") chamam uma função que não existe: aparece "Não consegui fazer isso agora."
3. **"salvar como x (2).pdf"** na caixa "Já existe um arquivo com esse nome" procura um campo de destino que não existe mais na tela de conferir: aparece "Aconteceu um problema inesperado..." e o PDF não é gerado. "substituir o antigo" funciona. Nenhum teste passa por esse caminho.
4. **Deslizante do painel "Filtro da página"** parece não gravar nada (volta ao valor de antes).
5. **Trilha de ferramentas, barra de opções, "Marcar como" e "só neste pedaço"** aparecem em todas as abas, mas só funcionam na aba Marcar; sem a aba Marcar ("Limpar a folha" desmarcada), as letras das ferramentas podem dar erro.
6. **Observações do livro inteiro** e o contador "tudo certo / N páginas para você olhar" ficam num cabeçalho escondido: nunca aparecem.
7. **Menu Filtro:** a marca de escolha não acompanha o filtro da página, e "Tirar o fundo" não está no menu nem tem tecla.
8. **Conflito da tecla R:** girar a folha e ferramenta Retângulo; a ferramenta ganha.
9. **Menu "Confirmar e processar" e Ctrl+Enter** parecem pular a caixa "Antes de processar" que o botão mostra (os dois chegam na janela "Confirmar e processar", que também avisa das páginas não conferidas).
10. **Aba Endireitar sem pista visual:** gira arrastando em qualquer lugar da página, sem alça e com o cursor de seta comum.
11. **Na janela "Confirmar e processar"**, digitar um nome que já existe não acende a faixa laranja de "Já existe" (só trocar de pasta acende).
12. **Textos sem acento:** "Arraste o retangulo se quiser mudar.", "Arraste sobre a página para girar na mao.", "inclinacao: +0.0 graus" (e com ponto, não vírgula), "Conferir a pagina N" e "Angulo da página N" (Histórico), "mantem a cor" (cartão Melhorar), "Verifique se ha espaço em disco.", "Nao ha paginas para conferir." (tela Pronto, caso raro).
13. **Jargão na tela:** "Algoritmo:" com "Sauvola (padrão)", "Otsu (letra grossa/gótica)", "Wolf (scan de baixo contraste)".
14. **Botão em inglês:** "Show Details..." na caixa "Lista de atalhos".
15. **Mesmo texto, funções diferentes:** "procurar de novo" do cartão (procura o PDF sumido) e "Procurar de novo" do menu Marcar (procura gravuras de novo). "usar em todas" existe em quatro abas, cada uma levando uma coisa diferente.
16. **A dica de "Mover conteúdo"** fala em 'aba "tamanho..."', mas "tamanho..." é um botão.
17. **Controles repetidos em vários lugares** (não é defeito, mas pesa no desenho): girar (botão, menu, tecla), apagar página (botão, menu, Del), procurar de novo (botão e menu), desfazer (menu, teclas, Histórico), zoom (roda, ferramenta Zoom, barra de opções, "Ver de perto"), filtro da página (cartões, menu, teclas, "Ver de perto").

---

## 5. O que está planejado e AINDA NÃO EXISTE na tela

Tudo abaixo vem do `PLANO-DEFINITIVO.md`, com as palavras do plano. Onde já existe um pedaço, está dito.

### Fase 1 (o que ficou para depois)

| Item | O que o plano pede | Hoje |
|---|---|---|
| 1.3 | **Ligar/desligar de cada OCR na tela** ("todos os OCRs instalados, com ligar/desligar e comparação automática entre eles (onde discordam, a página vai para 'Para revisar')"; de fábrica docTR + Kraken, Tesseract desligado). "O ligar/desligar de cada OCR na tela fica para quando o 1.4/1.5 voltarem." | **AINDA NÃO EXISTE** (os OCRs estão instalados, mas nenhum aparece na tela) |
| 1.4 | Máscara de tinta como o Internet Archive (achar a tinta só dentro das linhas de texto, guardando a cor original) | **AINDA NÃO EXISTE** (sem tela prevista) |
| 1.5 | **Caixinha "Só as letras" dentro do Preto e branco**, como o modo Misto do ScanTailor: "desmarcada, a página inteira vira preto e branco; marcada, só as letras viram preto e branco, e gravuras, fotos, molduras, iluminuras e outros detalhes coloridos ficam como no original. Vale para o livro inteiro ou para uma página só." | **AINDA NÃO EXISTE** |
| 1.5 | Filtro por zona automático ("Aplicar qualquer filtro só onde o detector de gravura ou o OCR achou", Lista de espera 30/09) | **AINDA NÃO EXISTE** (à mão já existe: "só neste pedaço" + aba Marcar) |
| Fase 1 | **Botão de manter ou tirar a moldura** ("o botão simples entra na Fase 1; a aparência fica para o layout (Fase 4)") | **AINDA NÃO EXISTE** |
| 1.6 | **PDF de saída em duas camadas** (letra em cima, fundo embaixo), **como opção** (Samuel: "quero ter a opção 1.6, mas quero poder deixar como está também") | **AINDA NÃO EXISTE** |
| Lista de espera 01/10 | **Tirar as ilustrações**: "eu quero ter a opção de tirar a iluminura se eu quiser, no caso, apagar todos os desenhos do livro e deixar só escrita." (1.5 ou Fase 3) | **AINDA NÃO EXISTE** |
| Lista de espera 01/10 | **Foto em Original dentro de uma página em Preto e branco** ("espero ter a escolha de conseguir deixar a foto em original"). | parte existe na aba Marcar ("só neste pedaço" com outro filtro) |

### Fase 2: as ferramentas do ScanTailor Advanced (adiantada em 01/10; começa pelo modo Misto)

Ordem decidida pelo Samuel (D1, 02/10): **Misto com zonas à mão**, limpar pontinhos, tipos de preto e branco, claro no escuro e cores; depois geometria; 2.15; 2.10 com o 1.6; 2.12; 2.16; 2.19. Decisão D2: as zonas da aba Marcar passam a ser guardadas em relação à folha original (com cópia de segurança dos projetos).

| # | Ferramenta (palavras do plano) | Hoje na tela |
|---|---|---|
| — | **Modo Misto com zonas à mão** (primeiro item; ligado ao "Só as letras" e à 2.18) | **AINDA NÃO EXISTE** como modo; existe a aba Marcar |
| 2.1 | Dividir a folha (sabe quando é uma página só) | existe a aba "Onde cortar" (nossa); a do ScanTailor **AINDA NÃO EXISTE** |
| 2.2 | Endireitar ("quero usar o do scantailor, pois o nosso não é tão intuitivo de se usar") | existe a aba "Endireitar" (nossa); a do ScanTailor **AINDA NÃO EXISTE** |
| 2.3 | Orientação / girar (usar o do ScanTailor) | existe "girar" 90 graus; a do ScanTailor **AINDA NÃO EXISTE** |
| 2.4 | Margens iguais em todas as páginas + alinhamento | **AINDA NÃO EXISTE** |
| 2.5 | Caixa da página e guias | **AINDA NÃO EXISTE** (as guias de "Mover conteúdo" são outra coisa) |
| 2.6 | Tamanho final da página em cm/mm | parte existe ("tamanho...", só cm) |
| 2.7 | Limpar pontinhos, com controle de força | existe só a caixinha "limpar poeirinha" (sem força) |
| 2.8 | Preto e branco Sauvola e Wolf (conferir o que já existe) | existe a lista "Algoritmo:" (com jargão) |
| 2.9 | Texto claro em fundo escuro | **AINDA NÃO EXISTE** |
| 2.10 | Separar a saída em duas camadas (junto com o 1.6) | **AINDA NÃO EXISTE** |
| 2.11 | Segmentação de cor / reduzir cores | **AINDA NÃO EXISTE** |
| 2.12 | Desentortar página curva perto da lombada | **AINDA NÃO EXISTE** |
| 2.13 | Detectar a página dentro da borda preta do scanner | **AINDA NÃO EXISTE** (o corte automático atual é nosso) |
| 2.14 | Preencher o que sobra fora da página com branco | **AINDA NÃO EXISTE** |
| 2.15 | Destacar páginas diferentes das outras | parte existe (alerta "Tamanho diferente") |
| 2.16 | Usar todos os núcleos do processador | sem tela |
| 2.17 | Normalizar iluminação e suavizar | parte existe ("Igualar a luz da página antes", só para achar gravuras) |
| 2.18 | **Edição manual das zonas de gravura (retângulo, polígono, laço, copiar, colar)** | parte existe na aba Marcar (retângulo, ponto a ponto, laço...); **copiar e colar AINDA NÃO EXISTEM** |
| 2.19 | Unidades cm/mm, perfis de configuração, tema claro/escuro | **AINDA NÃO EXISTE** |

"Já no programa, a aperfeiçoar nesta fase": aba Bordas e margens (recorte com Espelhado e Proporção travada, medidas em cm, tamanho da folha, moldura e margem branca, mover e redimensionar o conteúdo, qualidade da prévia); aba Filtro (três tipos de preto e branco, limpar pontinhos, aviso de escuro/apagado demais).

### Fase 3: seleção manual no nível do Photoshop

| # | Item (palavras do plano) | Hoje |
|---|---|---|
| 3.1 | Selecionar objeto com um clique (a IA só aponta, não desenha) | **AINDA NÃO EXISTE** na tela (há código pronto para isso, sem botão) |
| 3.2 | Seleção rápida (pincel que gruda na borda) | **AINDA NÃO EXISTE** (o "Pincel" atual não gruda) |
| 3.3 | Varinha mágica com tolerância e "só a área encostada" | parte existe ("Varinha mágica" com tolerância) |
| 3.4 | Intervalo de cores com suavidade (substitui o "pegar tudo desta cor" atual) | existe "Pegar tudo desta cor" |
| 3.5 | Laço, laço magnético, retângulo, oval | existem laço, retângulo e oval; **laço magnético AINDA NÃO EXISTE** |
| 3.6 | Refinar a borda da seleção | **AINDA NÃO EXISTE** |
| 3.7 | Somar, tirar e cruzar seleções; salvar seleção | existem "somar" e "tirar"; **cruzar e salvar AINDA NÃO EXISTEM** |
| 3.8 | Consertar o zoom que às vezes não funciona e o travamento com muitos cliques | bug aberto |
| 3.9 | Tudo testado com mouse de verdade | — |
| a aperfeiçoar | Aba Marcar: detecção automática por botão e "usar em todas" / "só nas próximas" | existe |

### Fase 4: layout (o motivo deste documento)

- "Layout Photoshop / After Effects", feito pelo agente de layout a partir do plano que o Samuel vai escrever.
- A aperfeiçoar: "Tela de Configurações com atalhos de teclado editáveis" (existe, ver 2.10).

### Ideias de layout e de tela da Lista de espera (seção 6 do plano)

| Data | Ideia (palavras do plano) | Imagem de referência |
|---|---|---|
| 24/09 | "Ver todas as páginas do livro em grade, como o 'Organizar páginas' do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir." | `docs/plano/referencias-layout/updf-todas-as-paginas.jpg` |
| 24/09 | "Layout limpo como o do UPDF: página no centro, poucas ferramentas em ícones numa barra fina no topo, miniaturas numa coluna à esquerda que dá para esconder, navegação e zoom num canto de baixo." | `docs/plano/referencias-layout/updf-tela-de-leitura.jpg` |
| 24/09 | "Aviso que o Kaique pediu (ainda sem descrição)" | — |
| 29/09 | "Os cartões de filtro e o 'comparar' da tela ampliada mostrarem o 'tirar o fundo' quando ele vale naquela página" (Fase 4) | — |
| 29/09 | "Filtro 'Tirar o fundo' também no menu 'Filtro' (e talvez tecla 5) e no 'só neste pedaço'" | — |
| 29/09 | "Tela 'Idiomas e modelos' para os quatro OCRs": instalado e para baixar, "baixar da internet", "importar um arquivo de modelo" (Fase 7) | — |
| 29/09 | "'Recuperar o trabalho anterior' no menu do cartão do projeto, listando as cópias guardadas antes de recomeçar" | — |
| 29/09 | Treinar os OCRs e o detector dentro do próprio programa (corrigir algumas páginas e ajustar o modelo, em segundo plano) (depois da Fase 7) | — |
| 30/09 | "Transformar uma página em folha branca" (hoje existe Marcar > "Deixar a folha em branco") | — |
| 30/09 | "Pergunta do fundo também dentro do programa, depois de abrir o livro, e a opção de voltar ao original" (Fase 1 ou 4) | — |
| 30/09 | "Melhorar o contorno das letras" | — |
| 01/10 | "Alerta de linha apagada: ... para que se olhe o original e se reescreva manualmente" | — |

---

## 6. Prints que já existem (nenhum novo foi tirado)

Todos na pasta do projeto `D:\programas\EditorImpressao\`. Prints de **08/08/2026 são de antes de muitas mudanças** e podem não bater com a tela de hoje.

| Caminho | O que mostra | Data |
|---|---|---|
| `relatorios/prints/5 - tela inicial - cartoes.png` | Tela inicial com cartões | 08/08 (antigo) |
| `relatorios/prints/6 - cartao de PDF que saiu do lugar.png` | Cartão laranja "o PDF saiu do lugar" | 08/08 (antigo) |
| `relatorios/prints/1 - tela de trabalho.png` e `1 - tela de trabalho - 150%.png` | Tela de conferir inteira (100% e 150%) | 08/08 (antigo) |
| `relatorios/prints/2.1 ... cor.png`, `2.2 ... pincel.png`, `2.3 ... zoom.png` | Barra de opções nas ferramentas cor, pincel e zoom | 08/08 (antigo) |
| `relatorios/prints/3.1 - painel Historico - com acoes.png`, `3.2 ... uma acao desfeita.png` | Painel Histórico | 08/08 (antigo) |
| `relatorios/prints/4 - painel Para revisar - agrupado por tipo.png` | Painel Para revisar | 08/08 (antigo) |
| `relatorios/prints/7.1 - antes de fechar.png`, `7.2 - depois de reabrir.png` | Conferência antes de fechar e depois de reabrir | 08/08 (antigo) |
| `relatorios/prints/8 - janela de confirmacao.png` | Janela "Confirmar e processar" | 08/08 (antigo) |
| `relatorios/conferir/fase1-1.2-tela-2026-09-30/prints/` (19 arquivos; explicação em `prints-tela-1-2.html`) | **Tela "O que fazer"** com o grupo "Gravuras e fotos" em 1366×768, 1440×880, 1600×1000, 1920×1080, a 100%, 125% e 150% (os "-rolada" mostram o fim da rolagem); `antes-125-1440x880.png` = o grupo espremido antes do conserto; `marcar-125-1440x880.png` e `marcar-150-1920x1080.png` = **aba Marcar** com "Esta página tem foto" | 30/09 |
| `relatorios/conferir/fase1-2026-09-30-rodada-geral/verificador/r01` a `r22` | r01–r05 "Gravuras e fotos" (espremido, cortado, 1920, tem fotos, não procurar); r06–r08, r10, r11 aba Marcar; r09 aviso de opção mudada; r12 aviso de detector ausente; r13 pergunta do fundo; r14 "Sim" só nas de Original; r15 tela mostrando "Tirar o fundo" depois de desfazer; r16–r18 "continuar"; r19, r22 "Dividir" desmarcado; r20 "Olhando o livro..."; r21 cancelou | 30/09 |
| `relatorios/conferir/pb-mp-decoracao-2026-10-01/verificador/reproducoes/prints/p01` a `p19` | p01 tela inicial; p02, p12, p15, p17 "O que fazer" (p19 em **1000×600** e **1366×768**); p03, p06, p13 caixinha do Preto e branco; p04, p08 conferência; p05, p09, p18 **aba Filtro**; p07, p14 progresso; p10, p11 reabrir e continuar; p16 depois de cancelar | 01/10 |
| `relatorios/conferencia-4-2026-10-01/tela/o-que-fazer.png` e `tela-caixinha.jpg` (iguais em `conferencia-5-2026-10-01/tela/`) | "O que fazer" com a caixinha do Preto e branco | 01/10 |
| `relatorios/conferencia-2-2026-09-30/gravuras/o-que-fazer-fabrica.png`, `o-que-fazer-tem-fotos.png`, `g1-o-que-fazer.jpg` | "O que fazer" de fábrica e com "Este livro tem fotos" | 30/09 |
| `relatorios/conferir/fase1-2026-09-29-1826/verificador/t01` a `t25` | t01 pergunta do fundo; t03, t21 cinco e quatro cartões da aba Filtro; t06, t15, t22 "Ver de perto" e o comparar; **t07 e t23 botões "Aplicar em" espremidos**; t10 "O que fazer" | 29/09 |
| `relatorios/conferir/fase1-2026-09-29-1603/verificador/t01` a `t14` | A caixinha antiga "Tirar o fundo sozinho" (já removida), "Ver de perto", alertas na faixa e na aba Bordas | 29/09 (tela já mudou) |
| `relatorios/conferir/fase1-2026-09-29-trabalho-salvo/verificador/p01`–`p29`, `...-trabalho-salvo-2/verificador/q01`–`q26`, `...-trabalho-salvo-3/verificador/s01`–`s36` | Tela inicial e cartões (livro movido, mesmo nome, dois projetos do mesmo PDF), avisos de recomeço, "O que fazer", "Olhando o livro...", caixa "Começar de novo?" com botões em inglês (s25, já consertado), "Ver de perto" (q26) | 29 e 30/09 |
| `docs/plano/referencias-layout/updf-tela-de-leitura.jpg` e `updf-todas-as-paginas.jpg` | Referências do Samuel (UPDF), não são deste programa | 24/09 |

**Telas sem nenhum print achado:** janela "Tamanho da folha", janela "Configurações", tela "Pronto", "Folhear o livro", caixas "Antes de processar" e "Já existe um arquivo com esse nome". As abas "Onde cortar", "Bordas" (com "Mover conteúdo") e "Endireitar" só aparecem, se aparecerem, nos prints antigos de 08/08 e nos de conferência do verificador (a conferir).

---

## 7. Resumo em números

- **Telas e janelas:** 5 telas da janela principal (inicial, "O que fazer", progresso, conferir, "Pronto"), com 5 abas e 4 painéis na de conferir; 6 janelas à parte ("Folhear o livro", "Ver de perto", "Tamanho da folha", "Confirmar e processar", "Configurações", "Lista de atalhos"); 14 caixas de pergunta ou aviso do programa; 4 caixas do Windows (abrir PDF, procurar o livro, duas de escolher pasta). **Total: 29**, sem contar abas e painéis.
- **Controles** (botões, caixinhas, bolinhas, deslizantes, listas, campos, itens de menu, alças e áreas de arrastar), contados à mão: cerca de **230** — 31 itens de menu, 11 na tela inicial (contando um cartão), 23 em "O que fazer", 3 no "Folhear", 1 no progresso, cerca de 76 na conferência (com as 9 ferramentas e os 4 painéis), 13 em "Ver de perto", 4 em "Confirmar e processar", 7 em "Tamanho da folha", 32 em "Configurações" (30 campos de tecla), 3 em "Pronto" e cerca de 27 nas caixas. Mais cerca de 30 atalhos de teclado.


---

## 8. Perguntas do Samuel (02/10): dá para mexer nas peças sem reescrever a tela de conferir?

Respondido só lendo o código (ramo `fase-1`), sem abrir o programa. Linhas de `ui/tela_conferir.py`, salvo quando outro arquivo é dito.

### 8.1 As peças são separadas ou estão presas na tela de conferir?

**São peças separadas, cada uma num arquivo próprio, mas quem as monta, liga e alimenta é a tela de conferir.** Ela é a "cola": põe cada peça no lugar (uma lista fixa, de cima para baixo, no `_montar`, l. 263–342), liga os sinais e, a cada mudança, chama um único `atualizar()` (l. 1495) que redesenha tudo. As peças não sabem nada do livro nem umas das outras (exceção: o painel "Marcar como", que a tela mexe por dentro, l. 886–890).

| Peça | Onde é criada | Quanto da lógica dela mora na tela de conferir | (a) recolher em ícones | (b) mudar de lugar | (c) esconder/mostrar por aba | (d) destacável/arrastável como no Photoshop | Referência |
|---|---|---|---|---|---|---|---|
| Os 4 painéis da direita | `_montar`, l. 300 (a coluna inteira) | Ligações em `_ligar_paineis` (l. 345–353); conteúdo refeito em `_atualizar_paineis` (l. 1518–1526) e quando chega um alerta; "Marcar como" mexido por dentro (l. 886–890) | **médio**: recolher até a barra de título **já existe** (clique no título); virar ícone pede ícone desenhado e um modo estreito, porque a coluna e os botões são travados em 172 px | **barato**: uma linha no `_montar` (ex.: à esquerda) | **barato**: já existe `mostrar_painel` (`paineis.py` l. 425) e o menu Ver já tem os itens, só falta ligar | **médio** se só encaixar nos lados da tela de conferir; **caro** se for espaço de trabalho livre com arranjo salvo | `ui/widgets/paineis.py` |
| Trilha de ferramentas | `_montar`, l. 288 | Ligações em `_ligar_ferramentas` (l. 364–384) e `escolher_ferramenta` (l. 386–390); só funciona se a aba Marcar existir | já é de ícones | **barato** noutra coluna; **médio** para virar barra no alto (desenho e clique são contas de coluna vertical) | **barato**: mostrar/esconder na troca de aba (l. 1439) | **médio** | `ui/widgets/trilha_ferramentas.py` |
| Barra de opções da ferramenta | `_montar`, l. 279 | Ligações em l. 371–381; o estado fica nela mesma | não se aplica | **barato** em qualquer faixa horizontal; **médio** se ficar em pé | **barato** | **médio** | `ui/widgets/barra_opcoes.py` |
| Tira de miniaturas | `_montar`, l. 332 (junto com "Confirmar e processar") | Montagem e decisão "folhas ou páginas" em `_montar_tira` (l. 1337–1373); molduras de alerta em `_atualizar_tira` (l. 1811–1818) | **barato** esconder; não tem ícone | **barato** mudar de faixa; **médio** virar coluna à esquerda como no UPDF (hoje é linha de altura fixa) | **barato** | **médio** | `ui/widgets/tira_miniaturas.py` |
| A página (prévia) | **uma por aba**, em `_area_de_visualizador` (l. 457–482), com "<" e ">" dos lados; a aba Marcar usa outra peça, o editor de marcação (l. 799); a aba Filtro não tem página, tem cartões (l. 1174–1181) | O que cada aba mostra é decidido em `_atualizar_previa` (l. 1528–1571); o zoom fica dentro de cada peça | não se aplica | **barato** tirar as setas dos lados e pôr navegação e zoom num canto | já é por aba | não se aplica | `ui/widgets/visualizador.py`, `ui/widgets/editor_selecao.py` |
| Faixa de explicação + botão laranja | `_montar`, l. 306–314 | Texto decidido por aba (l. 1742–1767) e pelos alertas | — | **barato** | **barato** | — | — |
| Linha de botões de cada aba | cada `_montar_aba_...` (l. 492, 506, 757, 770, 1152) | Os botões são da aba, mas o que fazem são funções da tela (l. 1913–2310) | — | **barato** (ex.: virar barra no alto) | já é por aba | — | — |

**As abas são separáveis?** Em parte. Cada aba é **montada** por uma função própria (Onde cortar l. 492, Bordas l. 506, Endireitar l. 757, Marcar l. 770, Filtro l. 1152), e as peças de cada uma ficam guardadas em listas separadas. Mas **dividem o mesmo estado e o mesmo "cérebro"**: a página atual (Onde cortar conta folhas, as outras contam páginas, l. 1387–1399), a resolução da prévia, o desfazer, a faixa, a fila de botões, e um único `atualizar()` que pergunta "qual aba está na frente?" em vários lugares (l. 1528–1571, 1742–1767, 1790–1809, e o teclado em l. 2392–2461). Há ligações cruzadas: o editor da aba Marcar é usado pelo menu Marcar, pela trilha e pelos painéis; botões da aba Bordas são lidos pelo teclado e pela prévia; o medidor e o "apagar página" da aba Filtro são acertados em `_atualizar_botoes`. Separar cada aba num arquivo seria mudança de estrutura (média a cara; o `CLAUDE.md` pede para não reescrever módulos inteiros) e **não é preciso para o desenho novo**.

**Barato no desenho novo:** trocar ordem e lugar das faixas e colunas (painéis à esquerda, botões da aba em cima, tira em cima ou embaixo); esconder ou mostrar painéis, trilha e barra de opções conforme a aba (resolve "a trilha aparece onde não funciona"); recolher painéis até a barra de título (já existe); ligar os itens do menu Ver; pôr navegação e zoom num canto; trocar textos, cores e o quadrado das caixinhas.

**Médio:** painéis que recolhem em ícones; painéis destacáveis encaixados nos lados da tela de conferir; trilha em barra horizontal no alto; tira de miniaturas em coluna à esquerda (o layout do UPDF); uma só área de página para todas as abas (hoje cada aba tem a sua, a Marcar é outra peça e a Filtro mostra cartões).

**Caro:** espaço de trabalho livre como o do Photoshop, com painéis soltos em qualquer lugar e arranjo salvo; a grade "todas as páginas" do UPDF com seleção múltipla, girar, apagar, extrair, inserir e dividir (peça nova inteira); separar as abas em arquivos próprios.

### 8.2 Quais achados "a conferir" foram vistos na janela de verdade?

**Nenhum.** Tudo foi só leitura do código; não abri o programa nem tirei print. Todos os achados da seção 4 continuam "a conferir na janela".

**Cabeçalho escondido (observações do livro e contador de dúvidas):**

| O quê | Referência |
|---|---|
| É criado por `_montar_cabecalho`, chamado no `_montar` | l. 269 e l. 392–436 |
| A caixa nasce presa à tela, **fora de qualquer arrumação**, e é escondida | l. 408–409 |
| Dentro dela: "Confira antes de processar", as observações do livro, o contador ("tudo certo" / "N páginas para você olhar"), "Desfazer" e "Refazer" | l. 411–435 |
| Contador e observações são atualizados a cada mudança, mas dentro da caixa escondida (o "mostrar" das observações não adianta: a caixa de fora continua escondida) | l. 1820–1839 (l. 1837) |
| Algum caminho mostra a caixa? **Não.** Nenhum outro arquivo a usa; só o `teste_botoes.py` clica nesses botões por código | `teste_botoes.py` l. 624 |

Consequência: as observações do livro inteiro, vindas da análise, **não aparecem em lugar nenhum**. O contador e o desfazer têm substitutos à vista (painel "Para revisar", menu Editar, painel "Histórico").

**Conflito da tecla R:**

| O quê | Referência |
|---|---|
| R da ferramenta Retângulo é **registrada** (aparece em Configurações e dá para trocar), junto com O L P B V C Z E | `ui/widgets/editor_selecao.py` l. 106–122 |
| "Girar a folha" com R **não é registrado**: está escrito direto no código e não aparece em Configurações | l. 2449–2451 |
| O menu "Girar" não tem tecla | `ui/barra_de_menu.py` l. 133 |
| Caminho da tecla: o editor da aba Marcar (se tiver o foco) não trata R e passa adiante; a janela manda a tecla para a tela de conferir | `editor_selecao.py` l. 600–610; `ui/janela_principal.py` l. 1086–1093 |
| Ordem na tela de conferir: 1º Ctrl+Z / Ctrl+Y / Ctrl+Enter; **2º letras das ferramentas** (R = Retângulo, e para aí); 3º M e T da aba Bordas; 4º setas, Espaço, Tab; 5º Del; **6º R = girar**; 7º 1 a 4 | l. 2401–2459 |

Quem ganha: **em todas as abas, R escolhe a ferramenta Retângulo**; o "girar" nunca é alcançado (só seria se a tecla do Retângulo fosse trocada em Configurações). Fora da aba Marcar, apertar R não faz nada visível (só troca a ferramenta na trilha). **Se a aba Marcar não existir** ("Limpar a folha" desmarcada), escolher a ferramenta procura o editor de marcação, que não foi criado (l. 386–390; ele só nasce em l. 799): pela leitura, cai no aviso geral "Aconteceu um problema inesperado..." (vale também para as outras letras de ferramenta e para Marcar > "Limpar tudo" / "Deixar a folha em branco"). A conferir na janela.
