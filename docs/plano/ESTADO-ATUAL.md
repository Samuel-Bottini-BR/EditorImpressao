# Editor de Impressão — ESTADO ATUAL (leia primeiro)

Escrito em 24/09/2026. A ordem de autoridade é:

1. este documento
2. `PLANO-DEFINITIVO.md` (o que fazer e em que ordem)
3. `CLAUDE.md` (regras técnicas)

O resto é histórico. O `PEDIDOS.md` virou histórico em 24/09: a lista que vale é o Plano Definitivo.

> **Onde o projeto está em 20/11/2026, tarde (vale sobre tudo abaixo; detalhe na [PARTE -41](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - **Passo 2 (publicar, o Kraken à parte, o servidor das versões de prova): voltas 4 e 5 feitas.** A conferência da volta 5, por um agente novo, **não achou nada médio nem grave** (3 problemas pequenos, para depois da prova). As duas rodadas do GitHub passaram.
> - **D-817:** o teste antigo que cobrava "a liberação falha → apaga o rascunho" saiu; o mesmo caso é cobrado do jeito novo (D-816).
> - **Esperando ele:** o "sim" para gravar a ficha do motor do Kraken na pasta de ferramentas dele e a prova à vista do passo 2 (ele só olha). Pergunta sem resposta: pôr na Lista de espera a escolha automática dos testes.
> - Depois da prova: os 3 problemas pequenos com um escritor novo, outra conferência, e a junção do passo 2 e das regras do catálogo na versão de teste.
> - Nada do processamento das páginas mudou. O programa ainda não está pronto para o Kaique.
>
> **Antes (20/11, manhã), já superado:**
> **Onde o projeto está em 20/11/2026, manhã (vale sobre tudo abaixo; detalhe na [PARTE -40](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - **Passos 0 e 1 do plano da parte do Windows juntados** na versão de teste (sem mudança desde 19/11).
> - **Passo 2 (publicar, o Kraken à parte, o servidor das versões de prova): três voltas feitas; a terceira conferência achou 2 problemas médios** (a versão já liberada podia ser apagada se o GitHub demorasse duas vezes; um nome de programa com ponto no fim passava pela recusa). O primeiro tem a escolha dele: **D-816 ("A")**, depois de pedir para liberar, nada é apagado. Falta a volta 4 (agente novo), a conferência 4 e a prova à vista.
> - **As regras novas do catálogo dos erros (D-809 a D-814) estão prontas**, esperando o passo 2 entrar para serem juntadas logo depois.
> - **D-815:** quem confere é sempre um agente novo em cada volta; quem escreve, o mesmo por até duas voltas.
> - **Esperando ele:** o "sim" para começar a volta 4; o "sim" para gravar o `motor.json` antes da prova; a prova à vista do passo 2. A pasta `C:\EditorImpressaoProva` ele já apagou (20/11).
>
> **Antes (19/11, noite), já superado:**
> **Onde o projeto estava em 19/11/2026, noite (vale sobre tudo abaixo; detalhe na [PARTE -39](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - **Plano da parte do Windows, versão 3, aprovado (D-799)** e sendo feito um passo por vez. **Passo 0 (o porteiro: 24 conferências automáticas e a lista de exceções de 176 lugares) juntado e ligado** na versão de teste. **Passo 1 (a peça única do Windows) juntado**, com a prova à vista dele (sessão A): o "Não" é lido como "Não"; na pergunta do Windows fica "EditorImpressao.exe" (D-805); a licença é pedida no instante do clique (D-806, passo 3).
> - **Em andamento no checkpoint:** passo 2 (publicar, o Kraken à parte, o servidor das versões de prova) e as regras novas do catálogo dos erros (D-808 a D-814), cada um com um agente.
> - **D-807:** antes de juntar cada passo, o conjunto inteiro dos testes roda só no GitHub; no PC, só antes da versão oficial. **D-803/D-804:** catálogo dos erros em `memoria/catalogo-de-erros.md`, atualizado pela gerente no fim de cada passo.
> - A versão de teste é o `obra-2026-10-26` (`0fe54cb3` no checkpoint; GitHub 44632638815 passou com os passos 0 e 1). Nada do processamento das páginas mudou. O programa ainda não está pronto para o Kaique.
> - **Esperando ele:** conferir se apagou `C:\EditorImpressaoProva`; a prova à vista do passo 2; os itens antigos da PARTE -38 (§6 da PARTE -39).
>
> **Antes (18/11, noite), já superado:**
> **Onde o projeto estava em 18/11/2026, noite (vale sobre tudo abaixo; detalhe na [PARTE -38](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - **Etapa 5 feita de verdade no PC do Samuel (18/11), com ele clicando: o programa NÃO está pronto para o Kaique.** Funcionou: instalar (em `C:\Program Files\EditorImpressaoPrograma`), a primeira abertura com o programa na frente, receber versão pelo ajudante, voltar da versão estragada, recusar a assinatura falsa, entrar de longe com senha e atualizar de longe. 7 defeitos: o "Não" do Windows vira "preparado"; a pergunta não aparece com o programa atrás; "Reiniciar agora" não volta e, com versão esperando, o programa não abre; o programa não lê o relatório do próprio script; a tranca da pasta deixa os arquivos sem licença; "Desligado" sem desligar; o perfil da conta de testes preso. O PC dele foi limpo (fica `C:\Users\editortestes` até reiniciar). Ramo `etapa5-2026-11-17`: existe no GitHub (`f505e5dc`), mas faltam 40 commits sem push.
> - **Regra nova para tudo:** CLAUDE.md §11.12 "sem gambiarra, em tudo" (6 pontos, inclusive ler a peça de fora antes de usar) e D-767 ("não faça mais nada escodindo ou de mentira"); os 4 agentes com a lista de ferramentas (D-793) e a junção (ligação de pasta escondida do Claude Code, não fica na área de trabalho) `C:\Users\fotog\.claude\agents` → `.claude\agents` do projeto (falta provar numa conversa nova).
> - **Plano único da parte do Windows, versão 2** (ramo `plano-windows-2026-11-18`, `plano-v2.md`), com as decisões D-767 a D-793 tomadas uma por vez no chat, o motor do Kraken à parte (D-768, D-788 a D-790; falta ele dizer se as três respostas valem como a aprovação do estudo), publicar no C: (D-776) e cada atualização inteira (D-789). **Espera a aprovação dele.** Antes: os 3 pontos em que duas decisões não combinam (plano-v2 §6.3) e as contradições das regras X4, X5, X6, X7, X9, X10 (X3 adiada) e a lista de exceções do porteiro (complemento da gerente à D-791, sem resposta dele).
> - **Nenhuma linha do programa mudou em 18/11.** A versão de teste é o `obra-2026-10-26` (`c68f84d2` no dia do checkpoint; código do `8d567c4a`, o nome interno do pacote, D-763). GitHub 44202459161 passou. Nenhum conserto até a entrega ao Kaique (D-765).
> - **Esperando ele:** apagar `C:\pr-medida` e `D:\agente_temp_testes` pelo Explorador; avisar quando reiniciar; o cache do pip; a internet do Kaique; e as paradas pela D-765 (a pergunta do Claude Code no PC do Kaique, D-709, D-710, as 4 da revisão do código, as respostas da Central que voltaram).
>
> **Antes (17/11, noite), já superado:**
> **Onde o projeto estava em 17/11/2026, noite (detalhe na [PARTE -37](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - **Frente do notebook do Kaique** (pedido de 16/11, "antes de tudo isso"; D-705 a D-751). As etapas 1 a 4 estão feitas e juntadas na versão de teste: atualização pelo Velopack com assinatura, procura ao abrir o programa, testes à distância pelo OpenSSH e o Tailscale, desinstalar limpo. Junto entrou o brasão girando ao carregar e como ícone (D-744 a D-748). Ramo `obra-2026-10-26`, ponta `a9d81030`. A rodada inteira do GitHub passou (44166943005). Nada foi instalado de verdade ainda.
> - **Etapa 5 (instalar e testar no PC do Samuel e desfazer) parada antes de começar**: o agente achou que o Velopack, na janela sem administrador, guarda os pacotes em `%LOCALAPPDATA%\EditorImpressao\packages`, dentro da pasta dos projetos. A gerente conferiu parte disso (PARTE -37, topo). Pergunta aberta: provar onde ele grava (e depois consertar).
> - **38 respostas dele na Central de 17/11 sem leitura** (lista exata na PARTE -37, §4).
> - **Pergunta dele sem resposta da gerente (17/11 14h10):** "se eu instalar o claude code no pc do kaique você consegue ver lá? se a gente abrir a mesma conversa e ligar acesso remoto?" Falta o teste dele do Girar com a capa aberta.
> - Esperando ele: a senha dos testes à distância ("eu nunca criei nenhuma senha"); D-709 (esperar o "sim" depois do plano?); D-710 (modelos por tarefa); os itens da D-708; as 4 da revisão do código.
> - Atalho de teste dele: "Editor de Impressao (rodada de consertos)". Nos filtros e nas ferramentas, nada mudou desde 14/11.
>
> **Antes (14/11, fim da tarde), já superado:**
> **Onde o projeto está em 14/11/2026, fim da tarde (vale sobre tudo abaixo; detalhe na [PARTE -36](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - Versão de teste: a mesma, ramo `obra-2026-10-26`, ponta `c7e34fd8`. Nenhuma linha do programa mudou hoje. **O Samuel testa pelo atalho "Editor de Impressao (rodada de consertos)"**, com pasta de dados própria; o "(desenvolvimento)" abre a versão principal.
> - **Teste dele do Tirar o fundo: 4 problemas** (demora e trava ao abrir e ao tirar o fundo; páginas sem o fundo tirado; miniaturas com o papel velho; o "antes" do Automático com o papel velho). Prints na sessão 7 de testes. Falta investigar; a gerente perguntou se põe um agente, **sem resposta**.
> - Três agentes de estudo terminaram (nada mudou no programa): prints das 6 perguntas que faltavam; estudo da palavra em duas cores (D-701, 2 perguntas); provas dos erros do Lusíadas (12 ainda acontecem, o 6 já não). Tudo está na Central (`perg-14-11-fundo-capa-girar`, `perg-14-11-palavra-cor`, `perg-14-11-lusiadas-provas`), esperando ele.
> - Falta o teste dele: girar com a capa aberta, e os outros da lista numerada (PARTE -36, §5).
> - Perguntas no chat sem resposta: apagar o PDF que o teste gravou em `Documentos\Editor de Impressao`; agente para os 4 problemas do Tirar o fundo; arquivar as conferências antigas.
>
> **Antes (14/11, madrugada), já superado:**
> **Onde o projeto estava em 14/11/2026 (detalhe na [PARTE -35](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - Versão de teste: ramo `obra-2026-10-26` (worktree `.claude/worktrees/obra-juncao`, ponta `c7e34fd8`; o código é o do `4c48e899`, depois só o Livro). Entraram em 13/11 os graves (D-649, D-648), os quadrados C (D-668) e o Tirar o fundo (D-646, D-699).
> - **Testados pelo Samuel ("funcionando"):** D-649, D-648, D-668. **Falta o teste dele:** Tirar o fundo e girar com a capa aberta.
> - Suspenso por ordem dele: conserto da sombra do Preto e branco (D-700, retângulos na capa do *Gradus*).
> - Regras novas: CLAUDE.md §11.12 (sem gambiarra) e §11.13 (como perguntar e responder); §10: agente não grava na Central.
> - Livro de decisões (no obra) até a D-704. Central (página versão 43) com as perguntas reescritas no §11.13; nenhuma resposta esperando a gerente.
> - Pergunta aberta no chat: arquivar as conferências antigas que funcionam (89) e as para depois (10). Esperam ele na Central: as 4 da revisão do código (destravam o girar numa regra só) e o aviso dos pares.
>
> **Antes (10/11, noite), já superado:**
> **Onde o projeto estava em 10/11/2026, noite (vale sobre tudo abaixo; detalhe na [PARTE -34](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):**
> - Versão de teste: ramo `obra-2026-10-26` (worktree `.claude/worktrees/obra-juncao`, ponta `58806f81` + Livro do checkpoint). Entrou o conserto do "Livros recentes" (fechava o programa depois do F1, `d777370c`): **o Samuel começou o teste e disse "vou terminar depois"**.
> - Prontos e conferidos pela gerente, **não juntados** (esperam o fim desse teste): ramo `graves-2026-11-10` (D-649 miniatura = PDF; D-648 cartões da tela cheia) e ramo `quadrados-c-2026-11-10` (D-668, quadrados brancos). Juntam sem conflito.
> - Livro de decisões (no obra) até a D-668. Regras novas: D-667 / CLAUDE.md §11.10 ("se mudou a ferramenta, muda em todos os lugares") e §11.11 (agente não abre agente).
> - Esperam o Samuel na Central: `perg-desfazer-fundo` (lugar do botão da D-646), `perg-quadrados-provas` (3 provas antigas da D-659), `perg-revisao-codigo` (4 perguntas da revisão). Esperam a gerente: as mesmas 38 respostas de 08 a 10/11.
> - Depois: girar numa regra só (D-665, D-666 e o girar da grade), depois das respostas da revisão.
>
> **Antes (10/11, tarde), já superado:**
> - A versão de teste é o ramo `obra-2026-10-26` (worktree `.claude/worktrees/obra-juncao`, ponta `396c534c` + Livro do checkpoint). Dentro dela, além do que já havia: gravura no Preto e branco à mão (D-659) e o "Pular" que guarda a gravura (D-661), testados pelo Samuel (funcionam); girar com a capa aberta e no Dividir (D-638, D-640, D-645, D-662, D-663), suíte inteira ok, **falta o teste dele**.
> - O Livro de decisões (`docs/plano/DECISOES.md`, no obra) vai até a D-664.
> - Fila de consertos: nada começado; a ordem (graves: fechar em Livros recentes, folha espremida, Automático e Tirar o fundo; depois quadrados brancos, D-660, caixinhas) **espera o "sim" dele**.
> - Na Central esperam a gerente **38 respostas dele de 08 a 10/11** (`relatorios/central-respostas-esperando-2026-11-10.md`) e esperam ele 2 perguntas novas (quadrados brancos: qual conserto; girar no Dividir).
> - Regras de 09-10/11: nenhum agente abre o programa na tela dele (tudo offscreen); prints de pergunta no modelo do girar (CLAUDE.md §10); todo print dele guardado na hora com relatório nos três formatos; no máximo dois agentes.
> - Perguntas e respostas: na Central https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy (versão 41).
>
> **Antes (07/11), já superado:**
> Onde o projeto estava em 07/11/2026 (detalhe na [PARTE -32](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) do handoff):
> - A versão de teste é o ramo `obra-2026-10-26` (worktree `.claude/worktrees/obra-juncao`), com a obra de 26/10, as 6 entregas de 04-05/11 e o cantinho do giro (D-639). O `fase-1` só guarda o plano.
> - O Livro de decisões (`docs/plano/DECISOES.md`, no obra) vai até a D-658.
> - Fila de consertos: item 1 (cantinho) juntado; item 2 (girar com a capa aberta) feito e testado com a janela aberta no ramo `girar-capa-2026-11-07`, esperando a resposta do teste antigo do "daqui" para juntar; itens 3 em diante não começaram (graves: fechar em Livros recentes, folha espremida, Automático e Tirar o fundo).
> - Regra de 07/11: quando o Samuel não pode testar, um agente testa com a janela aberta na tela, como o Kaique; no máximo dois agentes (um de teste, um de conserto).
> - Perguntas e respostas: na Central https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy (aba Respostas com três jeitos).

> **Atualização de 02/10/2026:** a seção 3 abaixo ("Onde o projeto está de verdade") é de 23/09 e
> está desatualizada. O estado de hoje está no **Registro de mudanças** do `PLANO-DEFINITIVO.md`
> e no resumo da **PARTE -9** do handoff (`historico/Editor de Impressao - resumo para o Claude.md`).
> Em 01/10 o Samuel **adiantou a Fase 2** (ferramentas do ScanTailor); 1.4, 1.5, 1.6 e o botão da
> moldura ficaram para depois. Em 02/10 ele respondeu os dois formulários (`relatorios/decisoes-samuel-2026-10-02.md`
> e `relatorios/conferencia-samuel-2026-10-02.md`): **1.1, 1.2 e 1.3 aprovados**; a Fase 2 começa pelo modo Misto;
> A1 (Horas 47 no Preto e branco) e X2 (Opus 20 no Mágico pro) foram consertados e verificados, junto com
> o medidor de força, a Horas 11 e o "salvar como (2)"; esperam o Samuel no `relatorios/conferir-aqui-7.html`.
> Resumo da sessão de 02–03/10: **PARTE -10** do handoff.
>
> **Atualização de 06/10/2026:** juntados ao `fase-1` o modo Misto ("Só as letras"), as zonas presas à folha original com conversão por trás, a gravação do projeto por trás e os consertos de 05/10. Prontos em ramos: o item 2.3 girar (`fase2-geometria`, falta refazer a verificação dos consertos) e os consertos do pedaço (`pedaco-e-salvo-2-2026-10-05`, esperando o formulário 15). Decisões do Samuel em 05–06/10 no Registro de mudanças. Resumo da sessão: **PARTE -11** do handoff.
>
> **Atualização de 06/10/2026, noite:** juntados ao `fase-1` o ramo do pedaço, o girar com o "aplicar em", o conserto do desenho que sumia no "Só as letras" e três consertos (Ctrl+Z depois de reabrir; aviso das pares; testes sem a pasta de dados real). Prontos em ramo, esperando o Samuel: `fase2-misto-opcoes` (DLL comum do ScanTailor + limpar pontinhos; falta ele aceitar o tempo) e `fase2-dividir` (2.1, conferido). Em verificação: `recomeco-historico`. Em andamento: `fase2-endireitar`. As conferências agora são feitas em páginas do claude.ai (`CLAUDE.md` §10 item 10). Resumo da sessão: **PARTE -12** do handoff.

---

## 1. O que é o programa

Programa de Windows que restaura PDFs de livros antigos escaneados e monta os cadernos para reimpressão. Projeto do Instituto São Bento (Pe. Rosenei). Quem usa é o **Kaique**, impressor, sem formação técnica. Feito em Python + PySide6.
Código: `D:\programas\EditorImpressao` (GitHub `Samuel-Bottini-BR/EditorImpressao`). Material de apoio: `D:\programas\EditorImpressao-arquivos\`.

**O critério final, nas palavras do Samuel:** "Eu quero que o papel saia branco, e o desenho também saia perfeito."

## 2. O resultado que o Samuel quer (fonte: "Vamos recapitular...", 12/09/2026)

| # | Resultado | Página de exemplo |
|---|---|---|
| R1 | Papel branco, **letras e gravura intactas** (nada de amarelado) | Palatino p. 5, 7 e 9 |
| R2 | **Sumir com a mancha do verso** (texto da folha de trás) | Palatino p. 10 e Marial p. 862 |
| R3 | **Margens iguais em todas as folhas** / centralizar o texto, pensando na costura. Esquerda e direita diferentes | Palatino p. 57, Graduale p. 222-223, Horas p. 14 |
| R4 | Tirar manchas (vermelhas, marrons) **sem mexer no título** | Palatino p. 66 e 76 |
| R5 | Endireitar linhas tortas | Graduale p. 221, Escola de Jesus p. 7 |
| R6 | Manter cores de verdade (rubricação, iluminura, borda prata) | Horas p. 11, 13 e 47; Graduale p. 221 |
| R7 | Tamanho final A4, com margem certa para encadernar | Siebmacher p. 7 |
| R8 | Apagar em todas as páginas um texto repetido (ex.: endereço de site) | Escola de Jesus p. 7 |
| R9 | Seleção de letra / gravura / cor que funcione de verdade | TESTE 1 (Boécio) |

**Páginas de teste escolhidas em 25/09:** Palatino 67, Siebmacher 9, Marial 7. A tabela acima fica como estava no começo; valem estas. Conferido comparando com os prints do "Vamos recapitular": o print marcado "76" do Palatino é a página 67 do PDF; o marcado "7" do Siebmacher é a página 9 do PDF; o do Marial é a página 7 do PDF (a 862 veio de uma lista de 18/07). A lista completa de páginas por item está em `gabarito/lista.json`.

**OCR (mudou em 24/09):** volta ao plano na **Fase 1**, só para *achar onde está o texto* (fazer a máscara de tinta como o Internet Archive), não para transcrever. A transcrição fica na Fase 7.

## 3. Onde o projeto está de verdade (23/09/2026)

- **434 testes automáticos passando.** Isso só prova que "não quebra", não que "ficou bom".
- **Zero itens aprovados pelo Samuel.**
- **Tem trabalho sem commit desde 17/09** (~34 arquivos). O plano (Fase 0.1) manda guardar isso num ramo separado.
- Dos resultados R1-R9, **nenhum foi conferido e aprovado.**

### Por que o projeto parou

- O trabalho foi para a tela, não para a imagem.
- Muita coisa por vez; a sessão acabava antes do Samuel testar, e o trabalho acumulava sem commit.
- Testar era difícil: atalho antigo abrindo código velho, janelas antigas abertas.
- O plano mudava a cada conversa: 5 versões de handoff, ~110 itens, nenhum aprovado.
- O seletor de gravura foi **recriado** duas vezes a partir da descrição do ScanTailor (31/07 e 16/09) e falhou. O seletor **original** do ScanTailor, testado em 24/09, funciona bem melhor (ver `TESTE-SCANTAILOR-MISTO.md`).

## 4. Contradições resolvidas (o que vale hoje)

| Assunto | Vale hoje | Documentos antigos diziam |
|---|---|---|
| Pasta do código | `D:\programas\EditorImpressao` | `C:\Users\fotog\Desktop\EditorImpressao` |
| Licença | **GPL liberado** (17/09): se um dia distribuir, é grátis com código aberto | "nada de GPL", "ScanTailor não embutir" |
| Mancha do verso | **NÃO corrigida** | "feito e conferido" (PARTE 3 do resumo, **errado**) |
| Filtro padrão de página nova | **Original** | Preto e branco |
| Barra de rolagem | cinza médio `#a8a49e` (decisão adiada) | preta |
| Testes | 434 (`pytest tests -q`) | 51 / 59 / 150 / 279 / 349 |
| Stack | Python 3.14 + PySide6. **Nunca** tkinter/customtkinter | `Instalar_Editor_Impressao.md` e `genesis` usam customtkinter: **versão velha, ignorar** |
| Modo de trabalho | Conversa gerente + agentes (ver plano, seção 3) | "ir até o fim sem chamar" |
| Menu "Abrir" | corrigido (commit `9d27b76`) | "não corrigido" |
| Seletor de gravura do ScanTailor | **usar o código original** (decisão de 24/09) | recriar em Python a partir da descrição |

## 5. Não confundir com outro programa

O **ExtratorPDF** (em `D:\programas\Scan Tailor`) é **outro programa**, separado deste. Não misturar pastas nem pedidos. A pasta `D:\programas\Scan Tailor\Testes de ajuste\` guarda os testes do ScanTailor de 24/09.
