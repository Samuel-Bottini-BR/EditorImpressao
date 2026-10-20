# Pedidos do Samuel, palavra por palavra, e onde cada um está hoje

Montado em 20/10/2026 pelo ajudante C da memória (pedido do Samuel de 19/10/2026, CLAUDE.md §4.9).

## Como ler este arquivo

- Aqui estão **os 68 pedidos numerados** que o Samuel fez de 18/07 a 08/08/2026, os **pedidos de 07/09/2026** e as **seis regras permanentes**, todos copiados do [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 3291 a 3807).
- Para cada pedido: número, data e hora, quem pediu, o **texto literal** (entre aspas ou em citação; nos muito longos, só os trechos que pedem algo, com "[...]" nos cortes), **onde ele mora hoje no plano** e a **situação**.
- **O que vale hoje é o plano.** O `PEDIDOS.md` e o handoff viraram histórico em 24/09/2026 ([CLAUDE.md](../CLAUDE.md), topo; [ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md), começo: "O `PEDIDOS.md` virou histórico em 24/09: a lista que vale é o Plano Definitivo."). Quando este arquivo e o [plano](../docs/plano/PLANO-DEFINITIVO.md) discordarem, vale o plano e a entrada mais nova do Registro de mudanças (seção 7).
- Quem pediu: nos 68, sempre o **Samuel** (são as mensagens dele nas conversas). Quando o pedido traz palavras do **Kaique** dentro, isso está dito.
- "Hoje" = 20/10/2026. O programa de referência é o ramo `fase-1` em `b8e9af7`.

### O que quer dizer cada situação

| Situação | Quer dizer |
|---|---|
| **feito** | Está no programa (`fase-1`) ou já aconteceu. Feito **não** é aprovado: aprovado só quando o Samuel marcou `[x]` no plano. |
| **em ramo** | Pronto ou em andamento num ramo, ainda não juntado ao `fase-1`. |
| **falta** | Tem lugar no plano e não foi feito (ou só em parte). |
| **descartado** | O Samuel disse que não quer mais (com data). |
| **superado** | Uma decisão mais nova trocou o pedido por outra coisa (com a data). |
| **situação não confirmada** | Não deu para saber pelas fontes; o porquê vai escrito. |
| **regra** | Não é tarefa: virou regra de trabalho escrita (CLAUDE.md, plano). Vale sempre. |
| **conversa** | Pergunta ou resposta do momento ("você terminou?", "ok"), sem tarefa para o programa. Fica registrada porque é literal. |

## Tabela-resumo

| | Os 68 numerados | Pedidos de 07/09/2026 (11) | Regras permanentes (6) | Total |
|---|---|---|---|---|
| feito | 11 | 8 | 0 | 19 |
| em ramo | 0 (partes de 9 e 61 estão em ramo) | 0 | 0 | 0 |
| falta | 2 | 0 | 0 | 2 |
| descartado | 0 | 0 | 0 | 0 |
| superado | 5 | 0 | 1 | 6 |
| situação não confirmada | 6 | 0 | 0 | 6 |
| regra | 6 | 2 | 5 | 13 |
| conversa | 38 | 1 | 0 | 39 |

Quando um pedido tem várias partes, a situação é a da parte que ainda decide (as outras vão escritas ao lado).

Os dois que **faltam** são os mais importantes da lista: o **pedido 14** (o teste decisivo contra o CamScanner e a mancha do verso, hoje itens [6.7](itens/6.7.md) e [6.1](itens/6.1.md)) e o **pedido 56** (seleção boa de verdade, hoje Fase 3 e itens [1.5](itens/1.5.md) e [2.18](itens/2.18.md)). Os resultados que o Samuel quer ver estão em [resultados-R1-a-R9.md](resultados-R1-a-R9.md).

## As duas listas antigas: PARTE 2 do histórico × PEDIDOS.md

**Não são a mesma lista, e não dá para comparar linha a linha.**

- A **PARTE 2 do histórico** (07/09/2026) é a lista **cronológica**: as 68 mensagens do Samuel, palavra por palavra, de 18/07 a 08/08/2026, mais os pedidos de 07/09 e as seis regras.
- O [`PEDIDOS.md`](../PEDIDOS.md) (07/09/2026, com o BLOCO 11 de 22/09/2026) é um **caderno de conferência**: cerca de 109 linhas em 11 blocos, por assunto ("o que fazer · o que esperar · quem confere"), com marcas `[ ]`/`[x]`. Não traz os pedidos literais nem as datas; traz o que se esperava de cada função. Em 12/09/2026 contava "109 itens, zero aprovados" ([histórico, PARTE -3](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), "Descoberta dura").

Onde as duas se tocam (e onde diferem):

| PEDIDOS.md | De que pedido veio | Diferença | Onde está hoje |
|---|---|---|---|
| BLOCO 1 (abrir e carregar; robustez) | pedido 1 (especificação), pedido 14 | não existe pedido literal "cartões", "religar PDF"; vieram da especificação e de consertos | trabalho salvo: Lista de bugs de 29-30/09 (consertados); tela inicial: [layout](layout.md), etapa 7 |
| BLOCO 2 (dividir) | pedido 1 (§4.1) | — | [2.1](itens/2.1.md) juntado em 07/10/2026; girar [2.3](itens/2.3.md) juntado em 06/10/2026 |
| BLOCO 3 (cortar e endireitar) | pedido 1 (§4.4, §4.6) | — | [2.2](itens/2.2.md) (G6 juntado em 12/10/2026), [2.13](itens/2.13.md), [2.5](itens/2.5.md) |
| BLOCO 4 (os quatro filtros, ampliar, comparar, sliders) | pedidos 1 e 9 | o PEDIDOS.md acrescenta os defeitos abertos (mancha do verso, rubricação, halo, folha de guarda) | Fase 1 ([1.4](itens/1.4.md), [1.5](itens/1.5.md)), [2.7](itens/2.7.md), [2.8](itens/2.8.md), [6.1](itens/6.1.md), [6.3](itens/6.3.md); ampliar e comparar: [layout](layout.md) |
| BLOCO 5 (alertas, "menos de 10%") | pedido 1 (§4.3 e critério 8) | — | o "Para revisar" ([para-revisar.md](para-revisar.md), ramo `fase2-para-revisar`) |
| BLOCO 6 (seleção) | pedidos 56, 61, 62 | — | Fase 3 ([3.1](itens/3.1.md) a [3.9](itens/3.9.md)), [1.2](itens/1.2.md), [2.18](itens/2.18.md) |
| BLOCO 7 (cadernos, marca de alceamento, chapas vermelho/preto) | pedido 1 (§4.5) | marca de alceamento, numeração e chapas não estão nos 68 | [6.5](itens/6.5.md), [6.6](itens/6.6.md); impressão: [2.6](itens/2.6.md) |
| BLOCO 8 (salvar, desfazer, instalar) | pedidos 5, 8 | — | [6.8](itens/6.8.md); Lista de bugs |
| BLOCO 9 (as dez queixas do Kaique) | pedido 17 (ler as queixas) | as queixas são do **Kaique**, não do Samuel; ver abaixo, "Queixas do Kaique" | R1, R2, [6.1](itens/6.1.md) |
| BLOCO 10 (o veredito do CamScanner) | pedido 14 | igual | [6.7](itens/6.7.md) |
| BLOCO 11 (pendências resgatadas, 22/09) | PARTE 1C do histórico (navegação, de um handoff de 29/07) | os 7 pedidos de navegação (setas fixas na tira, roda do mouse, "ir para página", Page Up/Down, Home/End, barra de rolagem mais alta) **não estão** entre os 68 numerados | **sem lugar no plano** (a tira de miniaturas está no [layout](layout.md), etapa 5, mas esses 7 comportamentos não foram achados no plano; procurei "Page Up", "ir para página", "Home" no PLANO-DEFINITIVO) |

Os **pedidos de 07/09/2026** e as **seis regras permanentes** só existem na PARTE 2; o PEDIDOS.md não os tem.

### Contradições entre as listas antigas (e o que vale)

| Assunto | Uma fonte diz | Outra diz | Vale |
|---|---|---|---|
| Mancha do verso | histórico, PARTE 3: "**Feito e conferido**" | PEDIDOS.md, BLOCO 9: "**NÃO corrigido**" | **não corrigida** ([ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md) §4; CLAUDE.md §9; item [6.1](itens/6.1.md) aberto) |
| Barra de rolagem | histórico, PARTE 3 e PARTE 1B: preta, "Feito em 06/08" | PEDIDOS.md, BLOCO 9: "feita, e depois revertida para cinza médio em 08/08" | **cinza médio `#a8a49e`** (CLAUDE.md §9; ESTADO-ATUAL §4, "decisão adiada"; o Samuel em 07/09/2026: "isso é irrelevante agora, deixe para depois.", histórico PARTE -1) |
| Livros de teste | PLANO-RETOMADA (07/09): cinco PDFs | PEDIDOS.md (07/09): "Sete livros fixos" | **nenhum dos dois**: valem as páginas de `gabarito/lista.json` (Registro 25/09/2026) |
| Arquivar a área de trabalho no D: | PARTE 2: "ainda em andamento" | "Estado hoje" (mesmo documento): "feita em 07/09/2026" | **feita** ("Estado hoje" foi escrito depois, no fim da mesma sessão) |

---

## Os 68 pedidos

### Pedido 1 — 18/07/2026 14:53 — Samuel

Documento longo (40.566 caracteres): a especificação original. Texto inteiro no [histórico, APÊNDICE A](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 4047 a 4844). Trechos que pedem algo:

> "Um **"CamScanner para PC"**: programa único de desktop que limpa o amarelado, endireita páginas tortas, divide folhas escaneadas com duas páginas e monta os cadernos prontos para impressão."
>
> "Cada função é **independente, marcável por checkbox**. O usuário pode ligar uma, várias ou todas, em qualquer combinação. Nunca forçar combinação."
>
> "1. dividir folhas → 2. cortar bordas → 3. endireitar → 4. filtro → 5. montar cadernos"
>
> [...] "## 10. Critérios de aceitação" [...] "3. O filtro Preto e branco remove o amarelado **e** o texto do verso transparecendo" [...] "6. É possível aplicar filtros diferentes em páginas diferentes do mesmo livro, gerando um PDF só" [...] "8. Num livro bem escaneado, menos de 10% das páginas são marcadas para revisão — o alerta não vira ruído" [...] "13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz" [...] "15. Roda como `.exe` único numa máquina sem Python instalado"

- **Liga-se a:** o plano inteiro. Critério 2 → [2.1](itens/2.1.md); 3 → [6.1](itens/6.1.md) (R2); 4 → R6; 7 e 8 → [para-revisar.md](para-revisar.md); 10 → [6.5](itens/6.5.md); 15 → [6.8](itens/6.8.md). Critério 6 ("um PDF só"): sem item próprio (PEDIDOS.md, BLOCO 4, "Nunca conferido ponta a ponta").
- **Situação: superado** pelo PLANO-DEFINITIVO de 24/09/2026 (Registro 24/09/2026, "Plano criado e discutido ponto por ponto"). Grande parte foi feita (filtros, alertas, desfazer que sobrevive a fechar — consertos de 06/10/2026 —, cadernos, instalador, `.exe` único em `empacotar.py --modo arquivo`). **A ordem do processamento mudou** para livro novo em 09/10/2026 (endireitar antes de cortar, G6; CLAUDE.md §7). O critério 3 (verso) continua **aberto** (R2). O "OCR / texto pesquisável" estava fora da v1 e voltou ao plano em 24/09/2026 (só para achar o texto; ESTADO-ATUAL §2).

### Pedido 2 — 18/07/2026 14:58 — Samuel

> "sim, siga no modo automatico e faça todo app"

- **Liga-se a:** regra de trabalho (CLAUDE.md §2 e §8).
- **Situação: superado.** O programa foi feito; mas o jeito "tudo de uma vez" foi trocado por "uma mudança por vez" e "uma fase de cada vez" (plano, regra 1, 24/09/2026; CLAUDE.md §2), porque 57+ commits marcados "feito" deram zero aprovados (CLAUDE.md §4).

### Pedido 3 — 18/07/2026 16:19 — Samuel

> "você terminou?"

- **Situação: conversa.**

### Pedido 4 — 18/07/2026 16:23 — Samuel

> "onde está o arquivo .exe?"

- **Situação: conversa** (o `.exe`: ver pedidos 5 e 8).

### Pedido 5 — 18/07/2026 16:30 — Samuel

Texto inteiro no [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 3314 a 3345). Começa com "dsfsdf" (assim mesmo) e **termina cortado na fonte** ("sugerir outr"). Trechos:

> "1. A pasta dist está vazia — não achei o .exe. Confira o que aconteceu e gere de novo."
>
> "2. Quero um INSTALADOR de verdade, não só o programa portátil. Use Inno Setup para gerar um "EditorImpressao-Setup.exe" que: - instale em "Arquivos de Programas" - crie atalho no menu Iniciar e na área de trabalho - apareça na lista "Adicionar ou remover programas" do Windows - tenha o assistente em português - inclua desinstalador [...] Continue gerando também a versão portátil em pasta, pra quem preferir rodar de pendrive."
>
> "3. FALTOU uma função importante: escolher onde salvar o PDF. [...] um botão "Escolher pasta" abrindo o seletor de pastas do Windows - campo mostrando o caminho escolhido, com opção de editar o nome do arquivo - lembrar a última pasta usada e sugerir ela na próxima vez [...] - avisar se já existir arquivo com o mesmo nome, oferecendo substituir ou renomear - se a pasta não tiver permissão de escrita, avisar em português e sugerir outr"

- **Liga-se a:** [6.8](itens/6.8.md) (instalador testado no notebook do Kaique); Lista de bugs de 25/09 ("O instalador não leva os modelos", `[~]`); PEDIDOS.md, BLOCO 8.
- **Situação: feito**, falta o teste no notebook do Kaique (6.8). Conferido no código em 20/10/2026: `instalador.iss` (português, desinstalador), `empacotar.py` (modos pasta, arquivo único para pendrive, instalador, entrega), `ui/widgets/destino.py` ("Escolher pasta", aviso de pasta sem permissão e de arquivo que já existe), `configuracoes.py` (`ultima_pasta_de_saida`). Consertos ligados: "salvar como (2)" (`25d916e`, 02/10/2026), gerar de novo sem travar e "substituir" + cancelar sem apagar o PDF antigo (Registro 05/10/2026).

### Pedido 6 — 18/07/2026 16:54 — Samuel

> "onde está o .exe?"

- **Situação: conversa.**

### Pedido 7 — 18/07/2026 16:57 — Samuel

> "[Image #3] não estou achando o .exe, eu quero que faça uma nova pasta e faça o .exe"

- **Situação: conversa** (atendido na época; hoje ver pedido 5).

### Pedido 8 — 18/07/2026 17:17 — Samuel

Texto inteiro no [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 3354 a 3402). Trechos:

> "1. CORRIJA O TRAVAMENTO Ao clicar nos botões da tela de conferir ("esta certo", "nao cortar esta", "voltar ao automatico", "usar em todas"), o programa fecha sozinho. [...] nenhuma exceção pode fechar a janela — deve virar aviso em português e registrar no log."
>
> "2. CORRIJA O LAYOUT SOBREPOSTO A caixa azul de explicação e os botões estão sendo desenhados POR CIMA da imagem da página [...] Use QVBoxLayout de verdade. NÃO usar setGeometry, move() nem widget flutuando sobre o visualizador."
>
> "3. TESTE VOCÊ MESMO antes de me entregar Abra o programa, carregue um PDF, clique em TODOS os botões de todas as abas, redimensione a janela. Só me chame quando não travar mais e o layout estiver correto."
>
> "4. LIMPE TUDO E ME ENTREGUE SÓ O INSTALADOR [...] coloque o arquivo final na minha Área de Trabalho, dentro de uma pasta chamada "Editor de Impressao" - dentro dessa pasta quero SÓ o "EditorImpressao-Setup.exe" [...]"

- **Liga-se a:** parte 1 → regra do CLAUDE.md §3 ("Nenhuma exceção fecha a janela"; `sys.excepthook` em `main.py`); parte 2 → [layout](layout.md); parte 3 → regra do CLAUDE.md §4.1 e `teste_botoes.py`; parte 4 → [6.8](itens/6.8.md) e [0.2](itens/0.2.md).
- **Situação: feito.** Parte 1: feito e virou regra. Parte 2: **superado** pelo layout novo (tela de trabalho sem abas, etapas 2 e 3 juntadas ao `fase-1` em 14/10/2026). Parte 3: virou regra (o `teste_botoes.py` clica em todas as telas; roda no GitHub em toda entrega, CLAUDE.md §4.6). Parte 4: existe o `empacotar.py --modo entrega`; para testar, o Samuel usa o atalho "(desenvolvimento)" (CLAUDE.md §8, passo 9; item 0.2 `[~]`).

### Pedido 9 — 18/07/2026 17:54 — Samuel

Texto inteiro no [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 3403 a 3496). Trechos:

> "1. AMPLIAR A PÁGINA EM TELA GRANDE [...] Clicar em qualquer um dos quatro cartões de filtro abre a página AMPLIADA, ocupando a janela inteira [...] Modo COMPARAR na tela ampliada: dois filtros lado a lado, com zoom e posição sincronizados [...] A imagem ampliada deve ser gerada em resolução maior que a da prévia — não basta esticar a miniatura, fica pixelada"
>
> "2. REORGANIZAR OS CONTROLES + MEDIDORES DESLIZANTES [...] PRETO E BRANCO → slider "Força do preto", 0 a 100, padrão 50 [...] MÁGICO PRO → slider "Intensidade" [...] MELHORAR → slider "Clareza do fundo" [...] Ao arrastar o slider a prévia atualiza em tempo real."
>
> "3. ACENTOS (já pedi duas vezes e continua errado) [...] Corrija TODOS os textos da interface para português correto: Impressão, página, Mágico, só nesta, próximas, Força, Espaço, dúvida, não."

- **Liga-se a:** ampliar e comparar → [layout](layout.md) (rodada 11 de 07/10/2026: tela cheia dos filtros "um grande" com "Comparar com o Original"; etapa 6 da obra); sliders → "Aba Filtro, a aperfeiçoar" da Fase 2 (junto de [2.7](itens/2.7.md) e [2.8](itens/2.8.md)); acentos → Lista de bugs.
- **Situação: feito**, com sobras. Ampliar e comparar existem (`ui/tela_ampliada.py`, conferido em 20/10/2026); a tela cheia nova do layout está **em ramo** (`layout-etapas4a7-2026-10-19`, começando). Sliders existem (`forca_preto`, `clareza_melhorar`, `intensidade_magico` em `modelos.py`; medidor de força acertado em 02/10/2026, `bf9680f`); bug aberto: "deslizante do painel 'Filtro da página' que volta a 50" (Lista de bugs, 02/10). Acentos: **ainda sobram** textos sem acento na Lista de bugs ("retangulo" na faixa do Cortar, 09/10; "mantem a cor", 12/10; "Conferir a pagina 5", 13/10).

### Pedido 10 — 18/07/2026 19:02 — Samuel

> "a parta com o arquivo .exe sumiu"

- **Situação: conversa.**

### Pedido 11 — 18/07/2026 19:28 — Samuel

> "Coloquei vários PDFs de teste reais na pasta pdfs_teste/ do projeto. Use TODOS eles na bateria de testes, em vez dos PDFs sintéticos. Para cada arquivo, me diga: - qual o tipo (folhas duplas ou simples, colorido ou P&B, qualidade do scan) - o que o programa detectou e se acertou - onde ele errou E me traga as imagens comparativas dos quatro filtros de cada um, escolhendo as páginas mais difíceis de cada arquivo — as mais amareladas, as mais tortas, as com texto do verso transparecendo. Importante: adicione pdfs_teste/ ao .gitignore, para os arquivos não irem para o repositório."

- **Liga-se a:** [0.3](itens/0.3.md) (pasta `gabarito/`).
- **Situação: superado.** Feito na época (`pdfs_teste/` está no `.gitignore`, linha 12, conferido em 20/10/2026). Trocado por: o acervo em `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE` (07/09/2026) e as páginas fixas de `gabarito/lista.json` (item 0.3 `[x]`; Registro 25/09/2026).

### Pedido 12 — 18/07/2026 19:55 — Samuel

> "você continua não fazendo o .exe, cade?"

- **Situação: conversa.**

### Pedido 13 — 18/07/2026 20:02 — Samuel

> "INSTALA NO MEU COMPUTADOR E COLOCA NA MINHA AREA DE TRABALHO"

- **Liga-se a:** [0.2](itens/0.2.md) (atalho antigo), [6.8](itens/6.8.md).
- **Situação: superado.** Feito na época (havia programa instalado no PC do Samuel, "instalador de 01/09", Lista de bugs de 25/09). Para testar, vale desde 07/09/2026 o atalho "Editor de Impressao (desenvolvimento)", que roda o código direto (histórico, PARTE -1; CLAUDE.md §8, passo 9).

### Pedido 14 — 18/07/2026 20:24 — Samuel (com palavras do Kaique dentro)

Documento longo (9.195 caracteres): o prompt de testes. Texto inteiro no [histórico, APÊNDICE B](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linhas 4845 em diante). Trechos:

> "O Kaique é o impressor que vai usar este programa. Ele descreveu com as próprias palavras os problemas reais que enfrenta. **Isto é o critério de sucesso** — se o programa resolver estes quatro casos, está pronto; se não, não serve."
>
> Caso 1: *"remover o amarelo e deixar as letras"* (Kaique). Caso 2: *"tem que preservar... ele vai remover o fundo amarelo e vai deixar as partes coloridas, as pinturas, e ele dá até uma melhorada nas cores"* (Kaique). Caso 3: páginas tortas. Caso 4: *"a folha é tão antiga que ela já está quase transparente, então as letras da parte de trás acabam aparecendo. Esses filtros no scanner, ele remove."* (Kaique) [...] "**Se este caso não for resolvido, o programa não substitui o CamScanner e o projeto falha.**"
>
> "## PARTE 6 — COMPARAÇÃO COM O CAMSCANNER (teste decisivo) [...] Escolha **5 páginas difíceis** [...] Assim eu processo as mesmas páginas no CamScanner e comparo lado a lado."
>
> Citado na PARTE 5 §6 do histórico: "Ao final, me diga em uma frase: **o programa já substitui o CamScanner para o trabalho do Kaique? Sim, não, ou ainda não.**"

- **Liga-se a:** [6.7](itens/6.7.md) ("Comparação final com o CamScanner: o programa já substitui?"), [6.1](itens/6.1.md) (caso 4 = mancha do verso, R2), plano §2 (resultado-alvo); PEDIDOS.md, BLOCO 10.
- **Situação: falta.** A pasta `para_comparar/` foi montada, mas o veredito nunca foi dado (histórico, PARTE 5 §6). Hoje as fotos do CamScanner feitas pelo Kaique (24/09) estão em `gabarito/camscanner/` (Registro 25/09/2026). O caso 4 (verso) é "o defeito mais grave aberto" (CLAUDE.md §9). Os casos 1 a 3 avançaram (R1, R6, R5 em [resultados-R1-a-R9.md](resultados-R1-a-R9.md)).

### Pedido 15 — 29/07/2026 14:35 — Samuel

> "vamos fazer mudanças no projeto do editor de impressão?"

- **Situação: conversa.**

### Pedido 16 — 29/07/2026 14:46 — Samuel

> "faça um resumo do programa para o claude que eu possa colar lá na conversa"

- **Situação: feito** (o handoff de 29/07, base da PARTE 1C do histórico).

### Pedido 17 — 29/07/2026 16:27 — Samuel

> "consegue olhar essa pasta "C:\Users\fotog\Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros" ver o que eu escrevi nos blocos de notas e ver e comparar as fotos que estão lá, para ver quais problemas quero resolver, depois me de uma lista aqui do que você leu, para eu poder ver se fez certo."

- **Liga-se a:** regra do CLAUDE.md §7 (as queixas "São fonte de requisito"); a pasta mudou em 07/09/2026 para `D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros`.
- **Situação: feito** (a lista virou a PARTE 3 do histórico, "As dez queixas do Kaique"; ver o fim deste arquivo).

### Pedido 18 — 01/08/2026 17:19 — Samuel

> "eu fechei sem querer o trabalho que estavamos fazendo, pode recuperar, tambem tinha escrito algumas coisas no na barra recupera o trabalho estamos no editor de impressão"

- **Situação: conversa.**

### Pedido 19 — 01/08/2026 17:24 — Samuel

> "2"

- **Situação: conversa.**

### Pedido 20 — 01/08/2026 17:46 — Samuel

> "ok e agora?"

- **Situação: conversa.**

### Pedido 21 — 01/08/2026 18:05 — Samuel

> "explique eu não entendi"

- **Situação: conversa.**

### Pedido 22 — 01/08/2026 18:06 — Samuel

> "eu quero que o papel saia branco, e o desenho também saia perfeito."

- **Liga-se a:** CLAUDE.md §1 ("O critério final, em uma frase"); plano §2 (resultado-alvo); [resultados-R1-a-R9.md](resultados-R1-a-R9.md).
- **Situação: regra.** É o critério final do projeto; vale para tudo.

### Pedido 23 — 01/08/2026 18:22 — Samuel

> "não entendi, o jeito que você escreve fica dificil para eu entender as informações, seja mais direto por favor"

- **Liga-se a:** CLAUDE.md §2 ("Ser conciso"; "Português comum, sem jargão").
- **Situação: regra.**

### Pedido 24 — 01/08/2026 18:26 — Samuel

> "ok, continue os testes."

- **Situação: conversa.**

### Pedido 25 — 01/08/2026 18:31 — Samuel

> "aqui não está aparecendo que você está trabalhando"

- **Liga-se a:** sem lugar no plano (é sobre o Claude Code, não sobre o programa).
- **Situação: situação não confirmada.** Existe um `statusline.ps1` em `C:\Users\fotog\.claude\` (fora do repositório); não conferi se ele é a resposta a este pedido.

### Pedido 26 — 01/08/2026 18:32 — Samuel

> "não era para aparecer um contador enquanto você está trabalhando ?"

- **Liga-se a:** sem lugar no plano (Claude Code).
- **Situação: situação não confirmada** (mesmo motivo do 25).

### Pedido 27 — 01/08/2026 18:34 — Samuel

> "você consegue me mandar notificação pop up quando tiver alguma coisa nova? ou quando precisar de alguma informação? aplique isso para os três projetos que estão rodando no claude code."

- **Liga-se a:** sem lugar no plano (Claude Code, vale para todos os projetos).
- **Situação: situação não confirmada.** Em 20/10/2026 há um gancho "Notification" em `C:\Users\fotog\.claude\settings.json` e um `notificar.ps1` ao lado (fora do repositório). Não conferi se ele faz o que os pedidos 29 e 30 pedem.

### Pedido 28 — 01/08/2026 18:51 — Samuel

> "quando terminar vai fazer o pop up?"

- **Situação: conversa** (pergunta sobre o 27).

### Pedido 29 — 01/08/2026 18:53 — Samuel

> "aparece nas notificações mas não pula na minha tela"

- **Liga-se a:** pedido 27.
- **Situação: situação não confirmada** (ver 27).

### Pedido 30 — 01/08/2026 18:59 — Samuel

> "quando eu clicar na janelinha eu quero ir direto para o terminal que está enviando a notificação, e quero que seja notificado só quando tiver responder alguma coisa e não enquanto está trabalhando codificando"

- **Liga-se a:** pedido 27.
- **Situação: situação não confirmada** (ver 27).

### Pedido 31 — 01/08/2026 19:03 — Samuel

> "ok"

- **Situação: conversa.**

### Pedido 32 — 01/08/2026 19:04 — Samuel

> "eu quero pode ver algum tipo de carregamento aqui no terminal enquanto você trabalha"

- **Liga-se a:** sem lugar no plano (Claude Code).
- **Situação: situação não confirmada** (ver 25).

### Pedido 33 — 01/08/2026 19:08 — Samuel

> "vou olhar as imagens"

- **Situação: conversa.**

### Pedido 34 — 02/08/2026 11:39 — Samuel

> "pode continuar fazendo outras coisas enquanto eu não vejo os ultimos testes?"

- **Situação: conversa.** (A ideia voltou como regra em 28/09/2026: "Seguir sem esperar a aprovação item a item", Registro 28/09/2026.)

### Pedido 35 — 02/08/2026 11:48 — Samuel

> "vai concertar os filtros e depois a gente volta para parte de seleção."

- **Liga-se a:** a ordem das fases do plano (Fase 1 separar o escrito do fundo; Fase 3 seleção manual).
- **Situação: superado.** Foi "a ordem de trabalho combinada" (regras permanentes, abaixo). Trocada pela ordem das fases do PLANO-DEFINITIVO de 24/09/2026, e depois pela Fase 2 adiantada em 01/10/2026 (Registro 01/10/2026, "Fase 2 adiantada"). A seleção automática entrou antes, no item [1.2](itens/1.2.md) (aprovado em 02/10/2026).

### Pedido 36 — 03/08/2026 21:35 — Samuel

> "por favor, confira os teste que você fez sozinho, não vou ter como fazer isso.["

- **Liga-se a:** CLAUDE.md §4.1 e §4.2 (o Claude Code roda tudo e **abre todas as imagens**; o Samuel só decide o que é de olho).
- **Situação: regra.**

### Pedido 37 — 03/08/2026 21:57 — Samuel

> "deixa eu ver os testes que você fez"

- **Situação: conversa.** (Hoje as conferências vão em páginas do claude.ai, CLAUDE.md §10, item 10.)

### Pedido 38 — 04/08/2026 03:05 — Samuel

> "recuperar"

- **Situação: conversa.**

### Pedido 39 — 04/08/2026 03:07 — Samuel

> "pq estava pedindo para resumir a sessão?"

- **Situação: conversa.**

### Pedido 40 — 04/08/2026 03:09 — Samuel

> "o que tem para fazer agora no programa?"

- **Situação: conversa.**

### Pedido 41 — 04/08/2026 03:11 — Samuel

> "pq o melhoramento dos filtros não está nesta lista?"

- **Situação: conversa.** (Hoje os filtros estão na Fase 1, itens [1.4](itens/1.4.md) e [1.5](itens/1.5.md), e na Fase 2, [2.7](itens/2.7.md) e [2.8](itens/2.8.md).)

### Pedido 42 — 04/08/2026 12:35 — Samuel

> "opa e agora, o que está fazendo?"

- **Situação: conversa.**

### Pedido 43 — 04/08/2026 13:12 — Samuel

> "manda print dos testes para eu ver"

- **Situação: conversa.** (Ver pedido 37.)

### Pedido 44 — 04/08/2026 13:39 — Samuel

> "ok, o que falta ainda fazer, acho que estamos quase chegando no perfeito na seleção."

- **Situação: conversa.** (A seleção feita até ali foi trocada pelo detector original do ScanTailor em 24/09/2026; ver pedido 56.)

### Pedido 45 — 04/08/2026 17:22 — Samuel

> "vamos continuar o trabalho do editor de impressão"

- **Situação: conversa.**

### Pedido 46 — 04/08/2026 18:22 — Samuel

> "porque você continua travando , porque não vai até o final?"

- **Liga-se a:** CLAUDE.md §2 ("Ir até o fim dentro da alçada").
- **Situação: regra.**

### Pedido 47 — 04/08/2026 18:44 — Samuel

> "me da um resumo de tudo que tu fez agora em arquivo md, as perguntas que me fez os prints que eu te mandei, os pedidos que eu te fiz em toda a conversa, as questões que tu perguntou para mim e o que falta para o programa estar pronto de acordo com o que eu quero e como ele deve funcionar"

- **Situação: feito** (relatório da época; ver pedido 68).

### Pedido 48 — 04/08/2026 19:10 — Samuel

> "você esqueceu de colocar os meus pedidos que eu fiz ao longo da conversa no relatorio só me da um relatorio em md para eu mandar para o claude"

- **Situação: feito** (ver pedido 68).

### Pedido 49 — 05/08/2026 14:53 — Samuel

> "o que falta agora? porque você parou?"

- **Situação: conversa.**

### Pedido 50 — 05/08/2026 16:26 — Samuel

> "ok, o que falta fazer ainda de tudo que eu já pedi e apontei?"

- **Situação: conversa.**

### Pedido 51 — 05/08/2026 16:42 — Samuel

> "muita coisa para eu ler, seja mais consigo por favor, fale em quatro linhas o que eu preciso escolher"

- **Liga-se a:** CLAUDE.md §2 ("Ser conciso. O essencial no chat, o detalhe em arquivo.").
- **Situação: regra.**

### Pedido 52 — 05/08/2026 16:44 — Samuel

> "continue 1 e depois 2 e termine tudo, só me chame quando terminar tudo"

- **Situação: conversa.**

### Pedido 53 — 06/08/2026 13:04 — Samuel

> "pera ai, faz um resumo pra mim"

- **Situação: conversa.**

### Pedido 54 — 06/08/2026 13:06 — Samuel

> "o que falta fazer?"

- **Situação: conversa.**

### Pedido 55 — 06/08/2026 13:17 — Samuel

> "a ferramenta de seleção está finalizada também?"

- **Situação: conversa.**

### Pedido 56 — 06/08/2026 13:23 — Samuel

> "ok, vamos continuar os testes do selecionador, além disso pesquise sobre como treinar selecionadores como programar esse tipo de coisas, procure também respositorios no reddit e como grandes apps como photoshop e adobe pdf fazem isso para nos ajudar a testar nosso programa e deixar ele zero, só pare quando estiver 99% de certeza e dai quando chegar nesse numero deixe amostras do seu trabalho lá na pasta de testes. depois disso continue a aplicar esse selecionador em conjunto com nossos filtros para que com o selecionador possamos aplicar filtro só em uma parte selecionada, ou melhorar o trabalho de um filtro, entendeu?"

- **Liga-se a:** [1.2](itens/1.2.md) (seletor de gravura do ScanTailor), [1.5](itens/1.5.md) (juntar os detectores), Fase 3 ([3.1](itens/3.1.md) a [3.9](itens/3.9.md), "nível do Photoshop"), [2.18](itens/2.18.md) (edição manual das zonas); treino: Lista de espera 29/09/2026 ("Treinar os OCRs e o detector de gravura dentro do próprio programa", fase nova depois da Fase 7).
- **Situação: falta**, com partes feitas e partes superadas.
  - **Feito:** "aplicar filtro só em uma parte selecionada" é o "Filtro só neste pedaço" (histórico, PARTE 4), que passou a valer no Preto e branco em 05/10/2026 (Samuel, conferência 13: Escola 7 e Opus 20 "BOM"); o modo "Só as letras" está no `fase-1` desde 06/10/2026.
  - **Superado:** o caminho de "recriar" o seletor até 99% foi trocado em 24/09/2026 pelo **código original do ScanTailor** (ESTADO-ATUAL §3 e §4: o seletor recriado "falhou"; "usar o código original (decisão de 24/09)", 24/09/2026). O 1.2 foi aprovado em 02/10/2026 ("M2 Item 1.2: detector de gravura do ScanTailor: [x] Aprovado", `relatorios/decisoes-samuel-2026-10-02.md`).
  - **Falta:** detector mais certeiro (1.5 e 2.18; "Para revisar", rodada 5, 09/10/2026: "Fica no plano (1.5 e 2.18)") e a seleção manual da Fase 3.

### Pedido 57 — 06/08/2026 14:07 — Samuel

> "consegue ativar o modo voz"

- **Situação: conversa** (sobre o Claude Code). O que entrou no projeto foi o ditado do Windows (Win+H) na caixa do `conferir.py` (histórico, PARTE 4).

### Pedido 58 — 06/08/2026 14:08 — Samuel

> "É explica para mim poucas palavras O que falta fazer no Programa"

- **Situação: conversa.**

### Pedido 59 — 06/08/2026 14:09 — Samuel

> "Tambão conserta todas essas coisas e só volta aqui a me chamar quando terminar tudo isso"

- **Situação: conversa.**

### Pedido 60 — 06/08/2026 17:38 — Samuel

> "não entendi do que você está falando, seja mais simples"

- **Liga-se a:** CLAUDE.md §2 ("Português comum, sem jargão. Primeiro a frase que se entende, depois o número.").
- **Situação: regra.**

### Pedido 61 — 06/08/2026 17:40 — Samuel

> "eu quero ter opção de transformar uma capa em branco. 2 - pode continuar mexendo no programa, precisa treinar o programa poder selecionar cores né? e tambem letras antigas tambem."

- **Liga-se a:** capa em branco → [para-revisar.md](para-revisar.md) ("Deixar em branco" / "Tirar do livro") e Lista de espera 30/09/2026 ("Transformar uma página em folha branca") e 07/10/2026 ("Página branca no lugar da página apagada", Fase 6); cores → [3.4](itens/3.4.md); letras antigas → [1.3](itens/1.3.md) (OCR com Kraken, aprovado em 02/10/2026) e [7.2](itens/7.2.md)/[7.3](itens/7.3.md).
- **Situação: feito** (a capa). "Marcar a folha inteira como papel = folha em branco" está no programa (histórico, PARTE 4 e PARTE 1B). A forma nova, com os dois botões "Deixar em branco" e "Tirar do livro", está **em ramo** (`fase2-para-revisar`, `ce2b835`, Registro 13/10/2026), só para as páginas com aviso; os dois botões em **qualquer** página ficam para a Fase 6 (Lista de espera 07/10/2026; Samuel, rodada 5, 09/10/2026: "Essa opção de tirar do livro ou deixar folha em branco eu quero ter em outras paginas, mas no caso essa ai aparece com aviso quando o programa detectar se tem uma folha em branco ou manchada."). Letras antigas: o OCR de manuscrito (Kraken) já acha as linhas (1.3); treinar fica para a Fase 7.

### Pedido 62 — 06/08/2026 17:47 — Samuel

> "eu quero que ele reconheça cores mesmo, para eu ter uma ferramenta a mais de seleção para eu poder selecionar por cor quando o programa dar errado."

- **Liga-se a:** [3.4](itens/3.4.md) ("Intervalo de cores com suavidade (substitui o 'pegar tudo desta cor' atual)").
- **Situação: feito.** A ferramenta "Pegar tudo desta cor" existe (`ui/widgets/editor_selecao.py`, conferido em 20/10/2026; histórico, PARTE 4). Vai ser trocada por uma melhor no 3.4 (Fase 3, falta).

### Pedido 63 — 06/08/2026 20:13 — Samuel

> "sim, pode continuar"

- **Situação: conversa.**

### Pedido 64 — 06/08/2026 23:09 — Samuel

> "resolva"

- **Situação: conversa.**

### Pedido 65 — 08/08/2026 02:32 — Samuel

> "me faz um resumo de tudo que tu fez, tudo que já pedi coloca tudo em documento texto para eu mandar no claude, o prompt inicial tudo bem explicado e o que falta fazer."

- **Situação: feito** (ver 68).

### Pedido 66 — 08/08/2026 02:37 — Samuel

> "você anexou todos os meus pedidos durante a conversa nesse relatorio?"

- **Situação: conversa.**

### Pedido 67 — 08/08/2026 02:40 — Samuel

> "não, eu fiz varios outros pedidos sobre o programa sobre funcionalidades, apotamentos sobre os testes que você fez, leia a conversa inteira antiga para lembrar"

- **Situação: conversa** (cobrança; atendida no 68).

### Pedido 68 — 08/08/2026 02:46 — Samuel

> "ta faz um novo relatorio e agora, coloca todos os meus pedidos dentro dele por favor, durante a conversa, junto com o relatorio da conversa completa"

- **Situação: feito.** O relatório de 07-08/08 (`Editor de Impressao - relatorio completo.md`, guardado fora do git em `D:\programas\EditorImpressao-arquivos\Contexto para Claude (24-09-2026)\03 - Documentos do Samuel e do Kaique\`) e, depois, a própria PARTE 2 do histórico (07/09/2026), de onde esta lista foi copiada. Este arquivo continua o pedido.

---

## Pedidos de 07/09/2026, fora da numeração

Fonte: [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), "Pedidos desta sessão (07/09/2026), fora da numeração acima" (linhas 3752 a 3784). Data: 07/09/2026; sem hora na fonte. Quem: Samuel. Conversa de organização e planejamento, não de código.

| # | Texto literal (como está na fonte) | Liga-se a | Situação |
|---|---|---|---|
| a | Retomada do projeto via o fluxo `/projeto`, escolhendo o Editor de Impressão. (resumo da fonte, não é fala literal) | — | **feito** |
| b | "quero saber todas as funcionalidades que eu já pedi para ter nesse app." | — | **feito** (histórico, PARTE 1B) |
| c | "você leu as conversas passadas e o claude.md para saber disso, verificou nossas conversas passadas?" | CLAUDE.md §10, item 8 ("checar o código e o `git log`, não só confiar no texto") | **regra** |
| d | "quero que verifique diretamente." | idem | **regra** |
| e | "Seleção de letras e gravuras está aí?" | — | **feito** (respondido conferindo o código; PARTE 1B, "conferido direto no código hoje") |
| f | "ok, então me da o handoff completo com todas as funcionalidades e coisas que o aplicativo vai fazer." | — | **feito** (PARTE 1B) |
| g | "mas o editor de impressão não está mais no dico local c, agora ele está no disco local d" | — | **feito** (investigação: o C: era a cópia ativa; histórico, PARTE -1) |
| h | "que é um hd externo" | — | **conversa** |
| i | "então vamos mudar tudo para o disco local D" | ESTADO-ATUAL §4 ("Pasta do código") | **feito** (`D:\programas\EditorImpressao`; o C: virou backup) |
| j | "Ta bom, agora cria um handolf bem completo com tudo, com o maximo de informação possivel, até as mensagens e pedidos que eu fiz, para eu ir para a conversa com claude e tentar melhorar o planejamento desse aplicativo." | — | **feito** (o histórico de 07/09) |
| k | "eu acho que poderia arquivar tudo em uma pasta unica no disco local D, tirar o que for do editor de impressão da area de trabalho." | — | **feito** ("Estado hoje": "Arrumação da área de trabalho, feita em 07/09/2026", em `D:\programas\EditorImpressao-arquivos\`). A PARTE 2 diz "ainda em andamento": vale o "Estado hoje", escrito depois. Sobra: a pasta `LIVROS PARA FAZER TESTE (duplicata)` (~1,5 GB) **nunca confirmado se o Samuel quer apagar** (PEDIDOS.md, BLOCO 11; CLAUDE.md §10, item 9: fora do projeto nada se apaga sem perguntar). |

## As seis regras permanentes

Fonte: [histórico, PARTE 2](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), "Os pedidos que valem como regra permanente" (linhas 3785 a 3807): "Estes seis não são tarefa: são o modo de trabalhar. **Quem pegar este projeto deve ler esta lista primeiro.**"

| Regra (literal) | Pedido de origem | Onde está hoje | Situação |
|---|---|---|---|
| "seja mais direto" e "seja mais conciso — em quatro linhas" | 23, 51 | CLAUDE.md §2 ("Ser conciso") | **regra** |
| "não entendi do que você está falando, seja mais simples" | 60 | CLAUDE.md §2 ("Português comum, sem jargão") | **regra** |
| "confira os testes que você fez sozinho, não vou ter como fazer isso" | 36 | CLAUDE.md §4.1 e §4.2 | **regra** |
| "porque não vai até o final?" | 46 | CLAUDE.md §2 ("Ir até o fim dentro da alçada") | **regra** |
| "vai consertar os filtros e depois a gente volta para a seleção" | 35 | — | **superado** pela ordem das fases do plano (24/09/2026) e pela Fase 2 adiantada (01/10/2026) |
| "eu quero que o papel saia branco, e o desenho também saia perfeito" | 22 | CLAUDE.md §1; plano §2 | **regra** (critério final) |

Atenção: o texto das regras na fonte é um pouco diferente do pedido literal (ex.: regra "vai consertar os filtros e depois a gente volta para a seleção" × pedido 35 "vai concertar os filtros e depois a gente volta para parte de seleção."). Quando citar, use o do pedido numerado.

## As dez queixas do Kaique (contexto do pedido 17)

As queixas são do **Kaique**, não do Samuel; ficam aqui só como ponte. Fonte: [histórico, PARTE 3](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (linha 3808) e [PEDIDOS.md](../PEDIDOS.md), BLOCO 9. As duas fontes têm pequenas diferenças de palavra (ex.: PARTE 3 "precisamos que fiquem mais arredondadas" × PEDIDOS.md "precisam ficar mais arredondadas"; PARTE 3 "deveria remover o amarelado e deixar totalmente branco" × PEDIDOS.md "deveria ficar totalmente branco, preservando as cores"). Os `.txt` originais estão fora do git, em `D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros` (não abertos nesta montagem). A ficha do Kaique é [geral/kaique.md](geral/kaique.md).

| Queixa (texto da PARTE 3) | Onde está hoje | Situação hoje |
|---|---|---|
| "as letras estão ficando pixeladas, precisamos que fiquem mais arredondadas" | R1 | situação não confirmada (nenhuma aprovação do Samuel sobre isto achada) |
| "o mágico pro está deixando muito pixelado a imagem" | R1 | situação não confirmada (idem) |
| "às vezes a parte de trás fica com uma mancha da parte da frente" | [6.1](itens/6.1.md), R2 | **falta** (CLAUDE.md §9) |
| "o programa não localizou as bordas corretamente" | [2.13](itens/2.13.md), [2.5](itens/2.5.md) | corte com 1 mm aprovado em 02/10/2026 (conferência 6, C1 a C4 "BOM"); borda preta do scanner **em ramo** (`fase2-caixa-conteudo`, não ligada) |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | [2.1](itens/2.1.md) | dividir do ScanTailor juntado em 07/10/2026; não marcado `[x]` |
| "colocar botão clicável nas páginas que o programa não tem certeza" | [para-revisar.md](para-revisar.md) | botão no próprio aviso **em ramo** (`fase2-para-revisar`) |
| "a barra de scroll devia ser preta" | CLAUDE.md §9 | cinza médio; decisão adiada pelo Samuel em 07/09/2026 ("isso é irrelevante agora, deixe para depois.") |
| "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | [6.5](itens/6.5.md) | **feito** (o programa simula a dobra; `core/cadernos.py`) |
| "no mágico pro o fundo deveria remover o amarelado e deixar totalmente branco" | R1, R6 | aprovado em parte (conferências 5 e 6, 01-02/10/2026; ver [resultados-R1-a-R9.md](resultados-R1-a-R9.md)) |
| "queremos que fique branco a página e só as letras pretas" (Preto e branco) | R1, [2.8](itens/2.8.md) | aprovado em parte; Horas 47 no Preto e branco "RUIM" em 05/10/2026 ("continuam apresentando falhas, pixels apagados no meio das letras"); os dez jeitos do ScanTailor **em ramo** (`fase2-scantailor-itens-2026-10-19`, 2.8 em andamento em 20/10/2026) |
