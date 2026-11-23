# Atualizador, publicar e o motor do Kraken (a atualização que chega sozinha no notebook do Kaique)

Ficha criada no checkpoint de 18/11/2026 ([PARTE -38](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)),
como o plano da parte do Windows sugeriu (plano-v2 §6.1, risco 17). **O que manda:** o Livro de decisões (no ramo
`obra-2026-10-26`, `docs/plano/DECISOES.md`), o [PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md) e o plano da
parte do Windows (`relatorios/plano-windows-2026-11-18/plano-v2.md`, ramo `plano-windows-2026-11-18`, esperando a
aprovação do Samuel). Ficha irmã: [testes-a-distancia.md](testes-a-distancia.md). O instalador em si: [itens/6.8.md](../itens/6.8.md).

## Situação (22/11/2026)

- **Entrega em duas vezes (D-824, 21/11):** primeiro o programa que se atualiza, só com 4 consertos do que falhou em 18/11; os testes à distância e o resto do plano depois, em atualizações ("Sim, mas como vai ser feito esses 4 consertos, preciso que isso seja feito de forma rapida" · "vamos fazer com um só, uma coisa de cade vez.").
- **Ramo `atualizador-4-consertos-2026-11-21`** (não juntado): voltas 1 a 4. Prova à vista nº 1 (22/11): funcionaram o "Não" e o "Sim" do Windows lidos do Windows, a conta comum lendo as tarefas, o motor posto pelo ajudante, o aviso de versão nova e a volta com o aviso de falha; não funcionaram a troca do "Reiniciar agora", a pergunta no meio da tela e a segunda preparação (pasta trancada) — consertados na volta 4 (D-828), esperando a resposta dele sobre 3 testes e a prova nº 2 ([PARTE -44](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).

### Situação de antes (18/11/2026)

- **Não está pronto para o Kaique.** Rodou de verdade pela primeira vez na etapa 5 (18/11, PC do Samuel): funcionou
  procurar, baixar, conferir a assinatura, trocar pelo ajudante, voltar da versão estragada e recusar a assinatura
  falsa; **não funcionou** o "Reiniciar agora" e o "Depois" (com uma versão esperando, o programa nem abre).
- Nenhuma linha mudou depois disso. A parte que conversa com o Windows vai ser refeita pelo plano-v2 (7 passos);
  nenhum conserto começa antes da entrega (D-765), e o plano-v2 é o caminho da entrega.

## O que vale hoje

- **Primeira entrega (D-824, D-825, D-826, D-828):** a janela da senha fica na primeira abertura e o Kaique clica "Agora não"; nesta entrega a senha digitada não liga nada (D-825, "ok"); o pedido de licença passa pela peça única e só sai com a janela do programa na frente; o "preparado" é lido do Windows (as duas tarefas); depois do "Sim", erro só no Visual C++ ou na instalação antiga o ajudante completa sozinho (escolha do agente da volta 2, construída, **sem resposta dele**: a perguntar de novo); se o Windows não deixa ler as tarefas, a pergunta volta sempre (D-826); a troca só começa com nada rodando de `current`, e abrir o atalho no meio da troca sai em silêncio (volta 4); a pasta dos testes à distância é a pasta segura `C:\Program Files\EditorImpressaoAjudante`, sem licença à mão (volta 4, saída B).
- **Regra de trabalho D-827 (22/11):** proteção sem teste nunca é "baixo"; trocar uma conferência por outra só depois de listar o que a antiga cobria ("porque a regra não funcionou?" · "2 - mas isso não estpa nas regras?").
- **Publicar (20-21/11):** a pasta montada do zero recebe o Visual C++ na montagem; a pasta já montada é conferida igual à montada do zero, pela mesma régua (D-818: "vai ter que reprogramar?" · "A"); as peças (motor do Kraken, Visual C++) vêm de uma pasta escrita num lugar só, `D:\programas\EditorImpressao-arquivos\ferramentas`, rodando da pasta principal ou de uma cópia de trabalho; se faltar, para e avisa (D-820: "não era melhor só ver se está instaldo no pc?" · "A"). Provado à vista em 20/11 (prova nº 2, 7 passos), antes da volta 10; falta o pedaço curto da prova e juntar (ramo `passo2-publicar-2026-11-19`).

- **A peça:** Velopack 1.2.161, que fica, com a nossa proteção em volta dos dois defeitos dele (D-779: "ta vamos
  continuar com ele, mas o que fazemos para ele não dar defeito e porque nossa peças em voltadele deram defeito?").
- **Nome interno do pacote:** `EditorImpressaoPrograma` (`versao.ID_DO_PACOTE`, um lugar só; D-763, "ok, pode fazer").
  Nunca pode ser o nome da pasta dos projetos (`%LOCALAPPDATA%\EditorImpressao`); não muda depois da primeira
  instalação. O programa instala em `C:\Program Files\EditorImpressaoPrograma`; o Kaique vê "Editor de Impressão".
- **Quando "Depois":** a versão nova entra ao fechar o programa, por trás (D-769, "b"). **Janelinha "Atualizando o
  programa, espere um pouco..."** em toda troca: depois do "Reiniciar agora" e ao abrir no meio da troca (D-770, "a").
  Se uma diz "toda troca" e a outra "por trás" ao fechar: ponto 2 da seção 6.3 do plano-v2, **esperando ele**.
- **O motor do Kraken sai do pacote que se atualiza** (D-768: "mas dai vai ter que baixar o motor do kraken toda vez e
  reinstalar ele de novo?" · "vou escolher a 16"): mora em `C:\Program Files\EditorImpressaoPrograma\motor-kraken\<versão>`
  (D-788, "1"); vem no instalador; motor novo é tudo ou nada (D-790, "A").
- **Cada atualização vai inteira, sem o motor** (~460 MB; troca de 2 a 3 min, conta), e a assinatura confere tudo
  (D-789, "A"). A diferença ("só o que mudou") sai.
- **Três frases para o aviso de falha** (D-778, "A"): estragou e voltou; sem a assinatura do Samuel; não conseguiu voltar.
- **Publicar:** no C:, nunca deixando menos de 20 GB livres (D-776: "Sim, no C só tem que cuidar para não encher o disco
  C inteiro"; 20 GB: "ok"); o instalador (.msi) só na primeira entrega e quando o Samuel pedir (D-777, "ok, fica assim").
  Se o Setup.exe continua saindo sem o motor: ponto 1 da seção 6.3 do plano-v2, **esperando ele**.
- **Provas:** versões de verdade servidas por uma janela visível no PC dele, mais um rascunho no GitHub (D-773, "A"); a
  ordem escrever → testes → outro agente tenta quebrar → prova na tela (D-775); os testes antigos que cobram o jeito
  errado mudam (D-774, "ok").
- **Depois da entrega:** cada conserto pode virar versão nova quando ele quiser (D-766: "os proximos consertos eu quero
  poder arrumar e poder atualizar a versão dele sempre que eu puder").

## Mudou em

- 21-22/11/2026 — a ordem da entrega (D-765: o .exe e os testes à distância juntos) → em duas vezes (D-824); a senha digitada liga os testes na mesma pergunta (D-733/D-735) → nesta entrega não liga nada (D-825); erro no meio da preparação sempre traz a pergunta de volta (D-749) → só se as tarefas não ficaram prontas (D-826).
- 16/11/2026 — a frente do notebook do Kaique: Velopack escolhido (D-723, "velopack"), assinatura grátis (D-724),
  procurar ao abrir (D-732), ajudante como SYSTEM (D-733), "Depois" entra na próxima abertura (D-734, **trocada pela
  D-769** em 18/11), janelinha só nesse caso (D-742, **ampliada pela D-770**).
- 17/11/2026 — nome interno `EditorImpressao` → `EditorImpressaoPrograma` (D-763, D-764; juntado `8d567c4a`).
- 18/11/2026 — baixar só a diferença → a versão inteira, sem o motor (D-768, D-789); publicar no D: → no C: (D-776);
  instalador em toda versão → só quando ele pedir (D-777); uma frase de falha → três (D-778).

## Tentado e descartado

- 21/11/2026 — trocar a conferência da tarefa do ajudante pela da peça única sem listar o que a antiga cobria (volta 2, a pedido da gerente): com a licença ilegível, deixou de conferir o resto (um passo para trás); voltou na volta 3 (D-827).
- 22/11/2026 — lançar o PowerShell da troca solto sem dizer a pasta de trabalho: herda `current` e impede o Velopack de renomeá-la (erro 32); a troca desiste (prova nº 1).
- 20-21/11/2026 — achar a pasta das ferramentas perguntando ao git onde fica a pasta principal (voltas 9 e 10 do passo 2): sem resposta do git, voltava calado à pasta errada (relatório 8); trocado pelo caminho escrito num lugar só (D-820). A gerente tinha aceitado o jeito do git sem perguntar (D-819).

- **A diferença ("só o que mudou"):** ~20 MB para baixar, mas o notebook remonta o pacote inteiro (22-23 min contra
  7,5 min inteiro, medido) e a assinatura não confere a diferença (lido no código, não provado).
- **Trocar de peça:** Velopack 1.3.39 (de teste), MSIX (certificado pago), tufup, WinSparkle, fazer a nossa (18/11).
- **O motor como um segundo programa** (dois itens na lista de programas): "remendo", segundo o estudo.
- **Abrir o PowerShell da troca com `DETACHED_PROCESS`:** ele fecha sem rodar (provado na etapa 5).

## Comportamento real já provado (não redescobrir)

- **Prova nº 1 (22/11):** a conta comum lê as tarefas do ajudante (`Get-ScheduledTask` sem licença); como o sistema, o `WaitPid` do Velopack dá "Acesso negado" e ele segue sem esperar; o registro do Velopack como o sistema fica em `C:\Windows\System32\config\systemprofile\AppData\Local\velopack\`; o .msi aberto por janela com licença abre o programa com licença no "Iniciar" do fim; a fonte de pasta lê `releases.win.json` na raiz (o publicar grava `v<versão>\`); o .msi com o motor instala ~1,2 GB em 3 min; o motor posto pelo ajudante em 1 min; o aviso olha 4 s depois de abrir e de 5 em 5 min (só lê um bilhete local; a procura na internet é só ao abrir).
- Sem administrador, o Velopack grava `Update.exe` numa pasta de reserva `LocalAppData\<nome do pacote>`; o desinstalador
  apaga `LocalAppData\<título>` (prova de 17/11, ramos `velopack-pasta-2026-11-17` e `nome-pacote-2026-11-17`).
- Abrir o programa no meio da troca faz o Velopack fechá-lo à força (lido no código, revisão do atualizador).
- 98% dos 35.103 arquivos são do motor do Kraken; publicar no D: (HD externo) leva 20,5 min onde no C: leva 3,6
  (estudo `publicar-rapido-2026-11-18`).
- O aviso de versão nova pode demorar até 5 min depois de abrir; cada troca da etapa 5 levou de 7 a 23 min.

## De onde veio

- Pedido de 16/11: "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de
  novo um instalador fazer tudo de novo" ([PARTE -37](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §1).
- 18/11: "fazer tudo de novo sempre, eu acho que está errado né?" · "as atualizações deveriam ser rapidas" (Lista de bugs
  18/11); "não faça mais nada escodindo ou de mentira" (D-767).
- Relatórios (fora do `fase-1`): etapa 5 (`etapa5-2026-11-17`), `revisao-atualizador-2026-11-18`,
  `publicar-rapido-2026-11-18`, `kraken-separado-2026-11-18`, `plano-windows-2026-11-18`.
