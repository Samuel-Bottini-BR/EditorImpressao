# Pacote de regras: Regras novas do catálogo dos erros (D-809 a D-814): regras dos agentes, conferência nova do porteiro e perguntas novas do formulário

Papel: **implementador**. Tipo de trabalho (sai dos arquivos): git e arquivos, testes, Windows e instalador (e qualquer conversa com programa de fora).


Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais arquivos você pode mexer, e a gerente compara com este pacote.

## Pedido

- Papel: implementador
- Commit de partida: 0fe54cb3
- Ramo: regras-catalogo-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
- `relatorios/regras-catalogo-2026-11-19/`

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

- **D-791** (18/11/2026): Chat, pergunta 2 da proposta das regras dos agentes ("as conferências automáticas"; a gerente explicou como um porteiro que barra o trabalho com um erro já conhecido; A = uma semana só avisando e depois barra, sugestão; B = barra desde o primeiro dia): "não sei do que você está falando" · "b"
  Na prática: As conferências automáticas (o "porteiro") barram o trabalho desde o primeiro dia: se o código tiver um erro já conhecido (ex.: pedir licença ao Windows fora da peça única, `DETACHED_PROCESS`, a tranca da pasta à mão, número de decisão na tela), o trabalho não entra. Lista de exceções, confirmada por ele em 19/11 (01h12 UTC): à pergunta "o que já está errado no código fica numa lista, que só diminui e só ganha item com o seu "sim"?", depois da explicação dos dois tipos de erro (1: erro no jeito de escrever o código, que o porteiro acha lendo o código, os 24 tipos; 2: defeito que só aparece usando o programa, que o porteiro não acha e fica na Lista de bugs), ele: "Sim" (entendeu) e, a "Então [...]
- **D-792** (18/11/2026): Chat, pergunta 3 da proposta das regras dos agentes ("o formulário da entrega"): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for enviado um trabalho para um agente?" (a gerente: um formulário só, fixo, cada pergunta nascida de uma regra que já falhou, mais as perguntas das etiquetas do trabalho, pela mesma tabela da D-784) · "ok"
  Na prática: Toda entrega de agente tem o formulário único, fixo (umas 20 perguntas, cada uma ligada a uma regra), mais as perguntas das etiquetas do trabalho (Windows: quantas perguntas do Windows o Samuel vê; tela: qual print prova; imagem: em quais páginas foi conferido), montado sozinho pela tabela, sem reescrever a cada trabalho. Um programa confere se todas foram respondidas; faltando alguma, o trabalho volta ao agente sem chegar à gerente nem ao Samuel. A qualidade das respostas é conferida pelo agente que tenta quebrar (D-775). Pergunta nova só entra quando nasce regra nova, com o "sim" do Samuel. Começa no trabalho da parte do Windows.
- **D-798** (19/11/2026): Chat, contradição X4 das regras dos agentes (CLAUDE.md §4.3: "o Claude Code pode escrever PRONTO PARA CONFERIR"; `implementador.md`: "quem escreve isso é o verificador"). A gerente: "quem pode dizer que um trabalho está "pronto para você conferir"? [...] Sugiro: só o que confere, e nunca o que construiu. Pode ser?": "fechou"
  Na prática: Só o agente que confere (o verificador, ou o que tenta quebrar, D-775) escreve "PRONTO PARA CONFERIR", e nunca sobre um trabalho que ele mesmo construiu. Quem constrói entrega à gerente sem esse rótulo. "APROVADO" continua sendo só do Samuel. Resolve a contradição X4 (completa o CLAUDE.md §11.5).
- **D-803** (19/11/2026): Chat, no passo 1 do plano da parte do Windows (depois de o GitHub achar o aviso com "Everyone" em vez de "Todos"). Ele: "pera ai, quando acontece esses erros, eles são catalogados para virarem regras depois?". A gerente: hoje cada erro fica só no relatório de quem quebrou e na ficha do passo; "Proposta: no fim de cada passo, eu junto os erros achados num catálogo. Os que se repetem viram uma regra nova para os agentes, ou uma conferência nova do porteiro, sempre só com o seu 'sim'. Faço assim?" Ele: "ok"
  Na prática: Catálogo dos erros achados, passo a passo. No fim de cada passo do plano, a gerente junta num catálogo os erros achados (pelos testes, pelo GitHub, por quem tenta quebrar e na prova à vista): o que foi, a causa, onde, em que passo. O que se repete vira proposta de regra nova dos agentes ou de conferência nova do porteiro, levada a ele; só entra com o "sim" dele.
- **D-804** (19/11/2026): Chat, como organizar o catálogo da D-803. Ele: "como vai ser organizado esse catologo de erros?" · "coloque um agente para pensar nisso"; depois da proposta do agente (`relatorios/catalogo-erros-2026-11-19/proposta.md`), "e a organização do caderno como ficou?"; a gerente explicou (um caderno só, escrito só por ela no fim de cada passo; de cada erro, o que aconteceu, por que, quem achou e o que devia ter pegado antes; os da mesma causa juntos num tipo, dez hoje; o tipo que aparece em dois passos ou três vezes no mesmo passo vira pergunta; regra nova se não havia regra, conferência do porteiro se a regra não bastou, lista de defeitos se é defeito do programa; o caderno aponta para os relatórios, não copia) e perguntou "Organizo assim?". Ele: "ok"
  Na prática: O catálogo fica em `memoria/catalogo-de-erros.md`, na versão de teste, como a proposta descreve, já com os 76 erros dos passos 0 e 1 em dez famílias. As seis famílias que se repetem viram seis perguntas, uma por vez, na Central (§11.13), só com o "sim" dele. Ainda não respondido: começar a trazer as seis agora (a gerente sugeriu; ele respondeu só à organização).
- **D-808** (19/11/2026): Chat. A gerente: "Começo a trazer as seis perguntas do caderno de erros, uma por vez?" Ele: "1- pode"
  Na prática: A gerente traz as seis perguntas das famílias que se repetem no catálogo dos erros (D-803, D-804), uma por vez, no chat. O que ele aprovar é feito junto, por um agente, depois das seis (regras dos agentes, porteiro, formulário).
- **D-809** (19/11/2026): Chat, pergunta 1 de 6 do catálogo dos erros (família F9, "comando que muda o que é do Samuel sem ele ver": o repositório do PC cortado por um `git fetch --depth=1` em 19/11; a pasta `modelos/` esvaziada ao tirar um atalho em 18/11). Ele: "não entendi nada"; à versão curta ("A proposta é proibir esses comandos perigosos e fazer o porteiro barrar quando um agente tentar usar"): "ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha o porteiro para ele não fazer isso" (respostas: as duas recuperadas; não havia regra para esses casos; o porteiro ainda não existia e não confere esses comandos); "Fica assim?": "ok"
  Na prática: Regra nova dos agentes: a cópia do agente divide o `.git` com o repositório do Samuel; comando que muda o `.git` inteiro (`fetch --depth`, `gc`, `prune`, `stash`, `config`, mexer em ramo que não é o seu) não roda na cópia, nem em script ou teste, a não ser num repositório de prova em pasta temporária; atalho de pasta (junção) só sai com `cmd /c rmdir`, contando os arquivos da pasta de verdade antes e depois. Conferência nova do porteiro: acusa esses comandos em scripts e testes fora das peças de git que já existem (`conversa_com_o_git.py`, `repositorio_de_prova.py`).
- **D-810** (19/11/2026): Chat, pergunta 2 de 6 do catálogo dos erros (família F4, "o teste supõe o computador": três rodadas do GitHub perdidas no passo 1 por Windows em inglês, licença de administrador já ligada e pasta temporária no D:). A gerente: "Proposta: os agentes que escrevem testes recebem uma lista curta dessas diferenças entre o seu PC, o GitHub e o PC do Kaique, para já escrever o teste certo de primeira. Fica assim?" Ele: "ok"
  Na prática: Regra nova dos agentes (etiquetas Windows e testes): o teste do Windows roda em três computadores diferentes. GitHub: Windows em inglês ("Everyone", "Administrators"), licença de administrador já ligada (o dono do que se cria é o grupo Administradores), pasta temporária no D:. PC do Samuel: português, sem a licença, o D: dá controle total a "Todos". Notebook do Kaique: a conferir. O teste compara a conta pelo número dela, nunca pelo nome escrito, e não supõe o estado de hoje da lista ou da versão de teste. Só regra, sem conferência do porteiro (daria falso alarme).
- **D-811** (19/11/2026): Chat, pergunta 3 de 6 do catálogo dos erros (famílias F3 e F5: proteção sem teste e resultado não conferido; no passo 1, quem quebrou desligou proteções e nenhum teste reclamou). A gerente: "Proposta: na ficha de entrega, quem escreve passa a mostrar, para cada proteção, o teste que falha quando ela é desligada. [...] Fica assim?" Ele: "ok"
  Na prática: Pergunta nova no formulário da entrega (trabalho de Windows e de instalador): "Cada proteção e cada conferência do resultado (recusa, leitura de volta, desfazer) → o teste que falha quando ela é desligada, provado numa cópia." O programa do formulário confere que a lista existe e que cada teste citado existe; quem tenta quebrar confere se a lista está completa.
- **D-812** (19/11/2026): Chat, pergunta 4 de 6 do catálogo dos erros (família F1, "a conferência acredita num dado que não prova nada": o "sim" que o agente podia escrever sozinho, no passo 0; o arquivo de uma rodada anterior aceito como de agora, no passo 1). A gerente: "É como deixar o aluno corrigir a própria prova. Proposta: toda conferência diz de onde vem cada informação que usa. Informação que o conferido pode trocar não vale como prova. [...] Fica assim?" Ele: "ok"
  Na prática: Regra nova dos agentes: toda conferência (do porteiro, de um teste ou do programa) diz de onde vem cada dado que usa; dado que o próprio conferido escreve ou pode trocar (o ramo do agente, o ONDE-PAREI, a anotação do programa, a pasta de troca, o arquivo da vez anterior) não serve de prova. Pergunta nova no formulário, para trabalho que confere algo: "De onde vem cada dado que a sua conferência usa?"
- **D-813** (19/11/2026): Chat, pergunta 5 de 6 do catálogo dos erros (família F2, "a conferência olha o jeito mais comum e o vizinho passa": no passo 1, a peça recusava `C:\Windows` e aceitava o mesmo lugar escrito de outros jeitos; três voltas de quem quebra para fechar). A gerente: "Proposta: acrescentar à sua regra de 'ler antes de usar peça de fora' que, quando o programa recusa ou procura alguma coisa, o agente lista antes todos os jeitos que o Windows ou o Python aceitam para ela. E a proteção passa a comparar a coisa de verdade, não o texto escrito. Fica assim?" Ele: "ok"
  Na prática: Acréscimo à regra 6 do CLAUDE.md §11.12 (ler antes de usar peça de fora): "Quando o nosso código recusa, filtra ou procura algo, a leitura da peça de fora lista também tudo o que ela aceita como entrada, com a fonte (ex.: o Python importa `.py`, `.pyw`, `.pyd`, `.pyc`, pasta com e sem `__init__`, `.zip` no caminho; o Windows aceita `\\?\`, `\\localhost\C$`, nome curto), e a recusa compara a coisa de verdade, não o texto." Também vira foco de quem tenta quebrar.
- **D-814** (19/11/2026): Chat, pergunta 6 de 6 do catálogo dos erros (família F6, "o texto ao Samuel foge do combinado": pergunta que repetia o que ele já tinha decidido, ou "como você escolheu" sobre o que ele não escolheu). A gerente: "Proposta: antes de mandar qualquer pergunta para você, o agente anota em quais decisões suas procurou e por que essa ainda não está respondida. A pergunta só chega a você depois disso. Fica assim?" Ele: "ok"
  Na prática: Pergunta nova no formulário da entrega: "Para cada pergunta ao Samuel: as decisões do Livro que você procurou antes, e por que esta ainda não está respondida." A gerente confere antes de levar (§11.13, ponto 10). As famílias F7, F8 e F10 não viraram pergunta (o que já existe cuida delas, ou ficam em observação).

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
