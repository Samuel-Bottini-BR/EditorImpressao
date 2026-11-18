# Pacote de regras: o porteiro do Windows e a pasta segura (passo 1 do plano da parte do Windows)

Papel: **implementador**. Arquivos: `core/windows.py` (novo), `tests/test_windows.py` (novo).
Tipo de trabalho (sai dos arquivos): git e arquivos, testes, Windows e instalador (e qualquer conversa com programa de fora).

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
- Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**

**Testes**
- Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
- Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
- Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
- Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
- Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')

**Git e arquivos**
- Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
- Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
- Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**

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
- **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
  Na prática: Nenhuma coisa nova (função ou escolha nova) muda o que já está escolhido e testado, nem cria problema novo. Antes de mexer, o agente lista o que já está escolhido e testado ali; se a coisa nova mudaria isso, para e pergunta; teste antigo que quebra faz a entrega voltar (nunca se muda o teste antigo para passar); o verificador confere também o que já funcionava ao redor.
- **D-637** (05/11/2026): No chat, ao aprovar a D-636: "1- pode ser, só garanta que não crie mais problemas fazendo isso, você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai mudar algo, deixe isso anotado."
  Na prática: Regra: antes de mudar qualquer coisa, pensar na experiência de quem usa (o Kaique) e no resultado final do livro dentro do programa, e garantir que a mudança não cria problema novo. Isso fica escrito: no ONDE-PAREI de cada tarefa, uma seção "Como fica para quem usa e no livro" (o que a pessoa vê e faz, passo a passo, e o que muda no PDF), antes de começar e conferida na entrega. Junta-se à D-605.
- **D-741** (17/11/2026): Chat, à pergunta "Se o Kaique clicar "Não" [no "Deseja permitir...?" da primeira abertura], do jeito que está, a pergunta não volta, e ele fica sem a atualização sozinha. Faço a pergunta voltar toda vez que ele abrir o programa, até ele clicar "Sim"? Sugiro que sim.": "Sim"
  Na prática: Se o Kaique disser "Não" à pergunta do Windows da primeira abertura (D-733, D-735), ela volta a cada vez que ele abrir o programa, até ele dizer "Sim". Depois do "Sim", nunca mais aparece (as atualizações seguem sem perguntar). Na conta de testes, nada pergunta (D-736).
- **D-763** (17/11/2026): Chat, à pergunta "Posso mandar um agente fazer esse conserto? Sugiro que sim." (prova de 17/11, ramo `velopack-pasta-2026-11-17`: o nome interno do pacote, "EditorImpressao", é igual ao da pasta dos projetos; a cada abertura o Velopack grava ali uma cópia do Update.exe, e o desinstalador do .msi apagou a pasta `%LOCALAPPDATA%\<nome do pacote>` inteira, com o projeto de mentira dentro): "ok, pode fazer"
  Na prática: O nome interno do pacote do Velopack deixa de ser igual ao nome da pasta dos projetos (`%LOCALAPPDATA%\EditorImpressao`), antes da primeira instalação de verdade. A troca é num lugar só (`versao.ID_DO_PACOTE`), que todo o resto lê; o Kaique continua vendo "Editor de Impressão". Uma prova cobra que o nome do pacote nunca é o da pasta dos projetos, e a prova da pasta de reserva e do desinstalar é repetida com o nome novo. O nome novo exato é detalhe técnico (escolha da gerente, D-014). A instalação no PC do Samuel (etapa 5) espera esse conserto.
- **D-717** (16/11/2026): Chat: "Fica a conta separada, escondida, só para os testes?" → "sim"
  Na prática: No notebook do Kaique, os testes à distância entram numa conta do Windows só para eles, sem poder de administrador, escondida da tela de entrada, com a senha que o Samuel criar (D-711). Os projetos de teste ficam na pasta dessa conta e nunca se misturam com os do Kaique.
- **D-771** (18/11/2026): Chat, decisão 4 do plano da parte do Windows ("se ligar os testes à distância der erro no meio"; A = desfazer tudo, sugestão; B = deixar o que deu certo, com "Ligado pela metade"): "A"
  Na prática: Ligar os testes à distância é tudo ou nada: se um dos passos falhar, o programa desfaz sozinho o que fez naquela vez, deixa o computador como estava e diz na tela "Desligado" e o motivo. A tela sempre mostra o que o Windows tem de verdade (D-767). Nenhum botão novo. Completa a D-712/D-721.

## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)

- [ ] **Arquivos que vou mexer** (antes de ir ao agente que tenta quebrar)
- [ ] **Decisões que esta tarefa precisa cumprir** (antes de ir ao agente que tenta quebrar)
- [ ] **O que já está escolhido e testado aqui** (antes de ir ao agente que tenta quebrar)
- [ ] **Como fica para quem usa e no livro** (antes de ir ao agente que tenta quebrar)
- [ ] **A causa, a regra e todos os caminhos** (antes de ir ao agente que tenta quebrar)
- [ ] **O que pode falhar e o que o programa faz** (antes de ir ao agente que tenta quebrar)
- [ ] **O que li da peça de fora e onde** (antes de ir ao agente que tenta quebrar)
- [ ] **O que foi feito** (antes de ir ao agente que tenta quebrar)
- [ ] **Arquivos criados ou alterados** (antes de ir ao agente que tenta quebrar)
- [ ] **Como cumpri cada uma** (antes de ir ao agente que tenta quebrar)
- [ ] **Testes** (antes de ir ao agente que tenta quebrar)
- [ ] **Caminho e função** (antes de ir ao agente que tenta quebrar)
- [ ] **Máquina ou olho** (antes de ir ao agente que tenta quebrar)
- [ ] **Ressalvas** (antes de ir ao agente que tenta quebrar)
- [ ] **Ideias e bugs** (antes de ir ao agente que tenta quebrar)
- [ ] **Perguntas para o Samuel** (antes de ir ao agente que tenta quebrar)
- [ ] **Commit** (antes de ir ao agente que tenta quebrar)
- [ ] **O que o agente que tentou quebrar achou** (antes da prova à vista)
- [ ] **A prova de verdade** (antes de 'pronto para conferir')

## 5. O que você não recebeu, e quando parar

Este pacote não traz as regras de: imagem, filtros e processamento do livro, perguntas e relatórios ao Samuel, pesquisa de peça de fora, tela (ui/). Se precisar mexer num arquivo fora da lista acima, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.
