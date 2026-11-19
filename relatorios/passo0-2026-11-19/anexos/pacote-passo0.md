# Pacote de regras: Passo 0 do plano da parte do Windows: o pacote de regras, o porteiro (as conferências automáticas) com a lista de exceções, e o formulário da entrega (montado pelo próprio agente a partir do pedido da gerente de 19/11)

Papel: **implementador**. Tipo de trabalho (sai dos arquivos): git e arquivos, testes, Windows e instalador (e qualquer conversa com programa de fora).


Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais arquivos você pode mexer, e a gerente compara com este pacote.

## Pedido

- Papel: implementador
- Commit de partida: 746dbda6
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/`
- `tests/test_conferencias_*.py`
- `tests/conferencias_excecoes.json`
- `ganchos/pre-commit`
- `relatorios/passo0-2026-11-19/`

## 1. Sempre (todo trabalho)

1. **Só o que foi pedido e decidido.** Faça só o que o pedido e as decisões do Samuel mandam. Nada de botão, aviso, texto ou comportamento a mais. Se a decisão parecer impossível, contraditória ou pouco clara, ou se a única saída for um remendo: pare e escreva a pergunta (não faça diferente em silêncio, nem 'por enquanto'). *Por quê:* É a falha que mais se repetiu: decisões de 25/09 nunca construídas, e agentes mudando o que ele tinha definido (§11.7).
2. **O novo não estraga o que já funciona.** Antes de mexer, anote o que já está escolhido e testado ali. Teste antigo que quebra faz a entrega voltar; nunca mude um teste antigo para ele passar. *Por quê:* Ele disse: 'essa é uma nova regra que todos os agentes precisam ler' (D-605).
3. **Sem gambiarra, em tudo.** Ache a causa, a função que decide, e todos os caminhos que chegam nela (grep). Mude num lugar só e faça todos os caminhos usarem esse lugar. Nada de desvio para um caso, nem conta ou lista copiada. *Por quê:* 17 remendos achados em 10/11 e os 33 defeitos do atualizador em 18/11 têm a mesma causa (§11.12).
4. **Nada é feito sem conferir de verdade.** Só diga 'feito' do que você conferiu de verdade (abrindo o arquivo, olhando a imagem, perguntando ao Windows). Escreva toda ressalva. Nunca escreva 'APROVADO': só o Samuel aprova. *Por quê:* 57 commits 'feito' e zero aprovados; '10 de 10 corretas' com seis erradas; 'Desligado' gravado sem desligar.
5. **Leia a peça de fora antes de usar.** Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido. *Por quê:* Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6).
6. **Decisões do Livro: cumprir e provar cada uma.** As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória. *Por quê:* As decisões se perdiam entre o pedido e o código (§11.3 e §11.4).
7. **Pense em quem usa e no livro que sai.** Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira. *Por quê:* Regra do Samuel para todo agente (D-637).
8. **Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele.** Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. Você nunca grava na Central. *Por quê:* 106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10).
9. **Seu ramo, commit a cada passo, nada se apaga fora.** Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de D:\programas\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler. *Por quê:* O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\d inteira.
10. **Não abra agente, não use a tela dele, entregue à gerente.** Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente. *Por quê:* Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10).

## 2. As regras do seu trabalho (29)

**Windows e instalador (e qualquer conversa com programa de fora)**
- A janela nunca congela: Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min). (CLAUDE.md §3)
- Texto com acento, caminho sem acento: Texto de tela com acento (UTF-8); caminho de disco sem acento. (CLAUDE.md §3)
- core/ não importa ui/: core/ nunca importa ui/: o processamento roda por linha de comando, sem janela. (CLAUDE.md §7)
- Onde o programa guarda estado: %LOCALAPPDATA%\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta. (CLAUDE.md §7)
- Uma peça só para conversar com o que está fora: Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito). (CLAUDE.md §11.12.1)
- Antes de escrever, a lista das falhas: No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade. (CLAUDE.md §11.12.3)
- Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-785): à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele.**

**Testes**
- Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
- Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
- Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-787): vale a regra de 19/10: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.**
- Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
- Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
- Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')

**Git e arquivos**
- Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
- Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
- Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-796): o agente de tela mexe em core/ só nos arquivos que o pedido nomear; sem isso, só ui/.**

**Todo trabalho**
- Ordem de leitura e quem manda: Quem manda: o Livro de decisões e o plano; o CLAUDE.md vem depois. O que ele disser contra o plano, vale o plano. (CLAUDE.md topo) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- PEDIDOS.md e handoff são histórico: PEDIDOS.md e o handoff em historico/ só servem de consulta; não dizem o que fazer. (CLAUDE.md topo)
- Não recomeçar do zero: Não reescrever módulo inteiro nem reorganizar o que funciona. Testar não é licença para reconstruir. (Duas versões já fracassaram.) (CLAUDE.md §2)
- Ir até o fim dentro da alçada: Decidir o que é da alçada e executar tudo, sem parar a cada passo. Se o contexto acabar, parar num commit com o programa rodando. (CLAUDE.md §2)
- Honesto: avisar erro e risco: Se o Samuel ou a gerente estiver enganado ou correndo risco, avisar. Não concordar para agradar. (CLAUDE.md §2)
- Python 3.14, não rebaixar: A máquina só tem Python 3.14. Nunca sugerir rebaixar. (CLAUDE.md §3)
- Ler a memória antes: Antes de começar, ler memoria/INDICE.md e as fichas do assunto. A memória nunca contradiz o plano. (CLAUDE.md §4.9)
- Item da fase atual, na ordem: O item vem da fase atual do plano; Lista de bugs no começo da fase. (CLAUDE.md §8 passo 1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs: Ideia nova: não fazer, anotar para a Lista de espera. Bug que impede a tarefa: consertar e dizer. Bug que não impede: anotar com data e print. (CLAUDE.md §10.2) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Docstring em tudo o que tocar: Todo arquivo e função tocados ganham docstring: o que faz e o que é seguro ou arriscado mudar. (CLAUDE.md §10.5)
- Plano novo não apaga pendência: Plano novo diz o que resolve e o que deixa de fora; nunca apaga pendência por omissão. (CLAUDE.md §10.6)
- Prosa de checkpoint não é prova: Quando o estado importa, conferir o código e o git log, não o texto de checkpoint. (CLAUDE.md §10.8)
- Obra D-014: o que não vale durante a obra: Durante a obra não valem 'conferir cada item antes do próximo' nem 'uma fase por vez'; nada entra no fase-1 antes da conferência final; duas decisões que se contradizem: vale a mais recente. (CLAUDE.md fim) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**

## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)

- **D-767** (18/11/2026): Chat, na etapa 5, depois dos 7 defeitos achados no Windows de verdade (a gerente explicou que os testes automáticos trocam as peças do Windows por peças de mentira): "não faça mais nada escodindo ou de mentira" · logo depois: "não quero fazer consertos quero que funcione" · e: "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Na prática: O que mexe no Windows (pergunta de administrador, PowerShell, tarefas, licenças de pasta, instalar e desinstalar, testes à distância) só conta como pronto quando roda de verdade no Windows, à vista, e funciona. Teste automático com peça de mentira não prova que funciona. Nada de área de trabalho escondida nos testes. O objetivo não é remendar cada defeito, é a parte do Windows funcionar inteira (CLAUDE.md §11.12). O alcance exato (por exemplo, as versões de teste servidas de uma pasta do D: em vez do GitHub) está sendo confirmado com o Samuel.
- **D-775** (18/11/2026): Chat: "o agente vai tentar quebrar antes de fazer o teste real na tela né?" (a gerente descreveu a ordem abaixo) · "ok"
  Na prática: A ordem de cada passo do plano da parte do Windows: (1) um agente escreve a peça; (2) os testes automáticos rodam, cobrando o jeito certo; (3) outro agente, que não escreveu, tenta quebrar (lê procurando falha não pensada, resultado não conferido e peça duplicada; roda o que dá sem pergunta do Windows); (4) só então a prova de verdade e à vista na tela do Samuel. Se o passo 3 achar problema, volta ao 1; o Samuel só é chamado quando a peça passou pelos três primeiros. Completa a D-767.
- **D-784** (18/11/2026): Chat, pergunta 1 da proposta das regras dos agentes ("cada agente recebe só as regras do trabalho dele"; a gerente explicou a tabela de etiquetas por arquivo): "ok, mas como vai saber que regras enviar para o agente?" · "ok"
  Na prática: Cada agente recebe um pacote curto de regras: as "sempre" mais as das etiquetas dos arquivos que o trabalho mexe (tabela "arquivo → etiquetas", montada por um programa, não pela memória da gerente), cada uma com o caso que a originou. Arquivo fora da tabela: o agente recebe todas e a gerente é avisada. O livro de regras inteiro continua para consulta, e o agente que tenta quebrar (D-775) recebe todas. A gerente confere no fim se os arquivos mexidos batem com os do pedido. Proposta no ramo `regras-agentes-2026-11-18`.
- **D-785** (18/11/2026): Chat, contradição 1 de 10 das regras dos agentes (janela escondida ou à vista: a regra antiga "nunca abrir janela na tela do Samuel; testes offscreen" contra a D-767 "não faça mais nada escodindo ou de mentira"); A = cada uma no seu lugar, sugestão: "ok, mais ainda existem mais casos na opção A"; a gerente completou a lista: "ok"
  Na prática: Sempre à vista, na tela do Samuel (mexe com o Windows): (1) instalar e desinstalar; (2) a pergunta "Deseja permitir...?"; (3) a primeira abertura com o preparo; (4) toda a atualização: procurar, baixar, a janelinha "Atualizando", "Reiniciar agora", a troca ao fechar e a volta; (5) os testes à distância: ligar, desligar, a janela da senha; (6) as tarefas do Windows (o ajudante, o desfazer); (7) qualquer coisa que mude o Windows (firewall, contas, pastas fora do projeto, configurações); (8) publicar uma versão (montar, assinar, o rascunho no GitHub); (9) as janelas do próprio Windows dentro do programa quando o teste é sobre elas ("Abrir", "Salvar como", arrastar o arquivo, imprimir). Podem [...]
- **D-786** (18/11/2026): Chat, contradição 2 de 10 das regras dos agentes (quando medir a velocidade: a regra antiga do §8 e dos agentes, medir no PC a cada mudança e voltar se ficar mais lento, contra a de 19/10 do §4.6; A = vale a de 19/10, sugestão): "a"
  Na prática: Vale a regra de 19/10 (CLAUDE.md §4.6): a cada mudança em processamento, a velocidade é medida no GitHub, antes e depois, na mesma máquina e alternando; no PC do Samuel, a medida que vale é no fim de cada fase; lentidão pequena achada no meio vai para a fase de desempenho. O texto antigo (§8 passo 5, implementador e verificador) é corrigido para apontar para o §4.6. Resolve a contradição X1.
- **D-787** (18/11/2026): Chat, contradição 3 de 10 das regras dos agentes (rodar todos os testes no PC antes de entregar, contra a de 19/10: um arquivo por vez no PC, o inteiro no GitHub; A = vale a de 19/10, sugestão): "A"
  Na prática: Vale a regra de 19/10 (CLAUDE.md §4.6): enquanto o agente trabalha, no PC do Samuel roda um arquivo de testes por vez, o do que ele mexeu; o conjunto inteiro roda no GitHub em toda entrega; no PC, o inteiro só roda antes de um trabalho entrar na versão de teste, pela gerente, com os outros agentes parados. O texto antigo dos agentes ("rode pytest tests -q antes de entregar") é corrigido para apontar para o §4.6. Resolve a contradição X2.
- **D-791** (18/11/2026): Chat, pergunta 2 da proposta das regras dos agentes ("as conferências automáticas"; a gerente explicou como um porteiro que barra o trabalho com um erro já conhecido; A = uma semana só avisando e depois barra, sugestão; B = barra desde o primeiro dia): "não sei do que você está falando" · "b"
  Na prática: As conferências automáticas (o "porteiro") barram o trabalho desde o primeiro dia: se o código tiver um erro já conhecido (ex.: pedir licença ao Windows fora da peça única, `DETACHED_PROCESS`, a tranca da pasta à mão, número de decisão na tela), o trabalho não entra. Lista de exceções, confirmada por ele em 19/11 (01h12 UTC): à pergunta "o que já está errado no código fica numa lista, que só diminui e só ganha item com o seu "sim"?", depois da explicação dos dois tipos de erro (1: erro no jeito de escrever o código, que o porteiro acha lendo o código, os 24 tipos; 2: defeito que só aparece usando o programa, que o porteiro não acha e fica na Lista de bugs), ele: "Sim" (entendeu) e, a "Então [...]
- **D-792** (18/11/2026): Chat, pergunta 3 da proposta das regras dos agentes ("o formulário da entrega"): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for enviado um trabalho para um agente?" (a gerente: um formulário só, fixo, cada pergunta nascida de uma regra que já falhou, mais as perguntas das etiquetas do trabalho, pela mesma tabela da D-784) · "ok"
  Na prática: Toda entrega de agente tem o formulário único, fixo (umas 20 perguntas, cada uma ligada a uma regra), mais as perguntas das etiquetas do trabalho (Windows: quantas perguntas do Windows o Samuel vê; tela: qual print prova; imagem: em quais páginas foi conferido), montado sozinho pela tabela, sem reescrever a cada trabalho. Um programa confere se todas foram respondidas; faltando alguma, o trabalho volta ao agente sem chegar à gerente nem ao Samuel. A qualidade das respostas é conferida pelo agente que tenta quebrar (D-775). Pergunta nova só entra quando nasce regra nova, com o "sim" do Samuel. Começa no trabalho da parte do Windows.
- **D-793** (18/11/2026): Chat, pergunta 4 da proposta das regras dos agentes ("tirar duas ferramentas dos agentes": abrir outro agente e gravar na Central, que as regras já proíbem): "ok"
  Na prática: Os agentes do projeto ficam sem a ferramenta de abrir outro agente e sem a de gravar na Central (a lista de ferramentas de cada arquivo em `.claude/agents/` passa a dizer só o que ele pode usar). A máquina impede, em vez de depender da memória do agente. Ressalva técnica achada pela gerente: a lista só vale quando o agente é chamado pelo nome do papel dele, e esta conversa abriu fora da pasta do projeto, onde esses papéis não aparecem; o jeito de fazer valer foi ao Samuel ("papeis? do que você está falando, explica melhor" · "no caso quando eu escolher o projeto do editor de impressão ele vai abrir na pasta do disco d automaticamente?" · à escolha A = abrir o VS Code na pasta do projeto, B [...]
- **D-796** (19/11/2026): Chat, contradição X7 das regras dos agentes (o agente de layout "só mexe em ui/", CLAUDE.md §10.1 e `layout.md`, contra o §11.12, "de preferência em core/ (a tela só chama)"), explicada com o exemplo do Girar (sete jeitos na tela; o conserto é um jeito só por trás, que todos os botões usam): "não entendi" → "1, mas tem que ser explissito o pedido né" (opção 1: "Ele pode mexer nas duas partes, quando o pedido disser antes")
  Na prática: O agente de tela pode mexer também no processamento (`core/`) quando o conserto precisa levar a regra para um lugar só, mas só se o pedido da gerente disser isso explicitamente, antes, nomeando os arquivos de `core/` que ele pode mexer. Sem isso escrito no pedido, continua só em `ui/`. O porteiro barra (ele, logo depois: "o porteiro tem que bloquear"): se o agente de tela mexer num arquivo de `core/` que o pedido não nomeou, o trabalho não entra (a lista dos arquivos permitidos vai no pedido e no formulário da entrega, D-792, onde o porteiro lê). Resolve a contradição X7.
- **D-797** (19/11/2026): Chat, contradição X5 das regras dos agentes (ramo principal: o CLAUDE.md §10.3, o implementador e o layout falam do `master`; o §4.6 e o §11.4 do `fase-1`; a obra, D-014, junta no `obra-2026-10-26`). A gerente: "a versão de teste [...] recebe todo o trabalho novo; a versão oficial [...] parou em 23/10 e só recebe o que você aprovar na conferência final; um terceiro lugar antigo, parado desde setembro, que ninguém usa. Sugiro escrever nas regras exatamente isso". Ele: "Só precisa de dois lugares né?" → "o terceiro sai das regras e ninguém mais usa. Sugiro não apagar, só deixar guardado como está": "ok"
  Na prática: Dois lugares só: a versão de teste (ramo `obra-2026-10-26`, atalho "rodada de consertos"), onde os agentes juntam o trabalho (pela gerente, D-014); e a versão oficial (ramo `fase-1`, atalho "(desenvolvimento)"), que só recebe o que o Samuel aprovar na conferência final e guarda o plano e o handoff. O `master` sai das regras (parado desde 28/09); não é apagado, fica guardado como está. Resolve a contradição X5.
- **D-798** (19/11/2026): Chat, contradição X4 das regras dos agentes (CLAUDE.md §4.3: "o Claude Code pode escrever PRONTO PARA CONFERIR"; `implementador.md`: "quem escreve isso é o verificador"). A gerente: "quem pode dizer que um trabalho está "pronto para você conferir"? [...] Sugiro: só o que confere, e nunca o que construiu. Pode ser?": "fechou"
  Na prática: Só o agente que confere (o verificador, ou o que tenta quebrar, D-775) escreve "PRONTO PARA CONFERIR", e nunca sobre um trabalho que ele mesmo construiu. Quem constrói entrega à gerente sem esse rótulo. "APROVADO" continua sendo só do Samuel. Resolve a contradição X4 (completa o CLAUDE.md §11.5).
- **D-799** (19/11/2026): Chat, depois do resumo de uma página aberto no navegador dele (`relatorios/plano-windows-2026-11-18/resumo-v3.html`, ramo `plano-windows-2026-11-18`, `7210b383`) e da explicação dos 5 lugares de fora ("que 5?"): "Aprova o plano?" → "ok"
  Na prática: Aprovado o plano da parte do Windows, versão 3 (`relatorios/plano-windows-2026-11-18/plano-v3.md`): 7 passos (0 a 6), cada um escrito por um agente, testado, atacado por outro agente que não escreveu e só então provado à vista na tela do Samuel (D-775). Antes do passo 0 vai a ele a pergunta dos 5 lugares de fora da parte do Windows (plano-v3 §6.3, ponto 1). Tempos do plano são chute (escrita 57 h 30 a 87 h; quem quebra 8 h 30 a 14 h; com ele 4 h 55 a 7 h em 5 sessões). A lista de exceções de partida (43 lugares, contada pelo agente) é recontada pelo programa do passo 0 e vai a ele para aprovar.
- **D-800** (19/11/2026): Chat, ponto 1 do plano-v3 §6.3 (os 5 lugares de fora da parte do Windows na lista de exceções do porteiro: duas dicas do Automático com "D-068" e "D-094", `ui/automatico.py`; o teste de velocidade lendo placa de vídeo e disco pelo PowerShell por conta própria, `teste_velocidade.py`, 2; a régua dos filtros perguntando ao Windows onde fica a Área de Trabalho, `avaliar.py`). Ele primeiro: "2, mas o que vai ser consertado?" · "achar a area de trabalho?" · "dicas do automatico?"; depois de cada explicação, à pergunta "Fica assim, com os três consertos?": "esses consertos deixa para depois"
  Na prática: Os 5 lugares ficam para depois da entrega ao Kaique (vale a D-765). Ficam na lista de exceções do porteiro até lá, cada um com a data e "depois da entrega"; a lista não termina vazia no fim do plano da parte do Windows (exceção dele à D-791). O Kaique recebe as duas dicas do Automático com os números. Os consertos, quando vierem, são os já explicados: tirar só o número das dicas (D-755) e passar as duas perguntas ao Windows pela peça única.
- **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
  Na prática: Nenhuma coisa nova (função ou escolha nova) muda o que já está escolhido e testado, nem cria problema novo. Antes de mexer, o agente lista o que já está escolhido e testado ali; se a coisa nova mudaria isso, para e pergunta; teste antigo que quebra faz a entrega voltar (nunca se muda o teste antigo para passar); o verificador confere também o que já funcionava ao redor.
- **D-637** (05/11/2026): No chat, ao aprovar a D-636: "1- pode ser, só garanta que não crie mais problemas fazendo isso, você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai mudar algo, deixe isso anotado."
  Na prática: Regra: antes de mudar qualquer coisa, pensar na experiência de quem usa (o Kaique) e no resultado final do livro dentro do programa, e garantir que a mudança não cria problema novo. Isso fica escrito: no ONDE-PAREI de cada tarefa, uma seção "Como fica para quem usa e no livro" (o que a pessoa vê e faz, passo a passo, e o que muda no PDF), antes de começar e conferida na entrega. Junta-se à D-605.

## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)

Use estes títulos de seção, exatamente assim. "Não se aplica" só vale com o motivo ("não se aplica: este passo não pede licença ao Windows"). Nas decisões, as palavras do Samuel vêm entre aspas logo depois do número, copiadas do Livro; o seu comentário vem depois de "Aqui:". Confira antes de entregar: `python -m regras_dos_agentes entrega relatorios/<pasta>/ONDE-PAREI.md --etapa quebrar`.

## Decisões que esta tarefa precisa cumprir

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que já está escolhido e testado aqui

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Como fica para quem usa e no livro

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## A causa, a regra e todos os caminhos

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que pode falhar e o que o programa faz

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que li da peça de fora e onde

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que foi feito

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Arquivos criados ou alterados

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Como cumpri cada uma

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Testes

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Caminho e função

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Máquina ou olho

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Ressalvas

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Ideias e bugs

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Perguntas para o Samuel

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## Commit

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## O que o agente que tentou quebrar achou

(a preencher; obrigatório antes da prova à vista)

## A prova de verdade

(a preencher; obrigatório antes do rótulo de pronto para conferir)

## Perguntas do Windows que o Samuel vê

(a preencher; obrigatório antes de ir ao agente que tenta quebrar)

## 5. O que você não recebeu, e quando parar

Este pacote não traz as regras de: imagem, filtros e processamento do livro, perguntas e relatórios ao Samuel, pesquisa de peça de fora, tela (ui/). Se precisar mexer num arquivo fora da lista do pedido, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.
