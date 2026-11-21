# Pacote de regras: Passo 2 do plano da parte do Windows, volta 5: tentar quebrar os consertos da volta 5

Papel: **quebrador**. Tipo de trabalho (sai dos arquivos): git e arquivos, testes, Windows e instalador (e qualquer conversa com programa de fora).


Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais arquivos você pode mexer, e a gerente compara com este pacote.

## Pedido

- Papel: quebrador
- Commit de partida: 384df3f6
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `core/windows.py`
- `tests/test_windows_peca.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `relatorios/passo2-publicar/`

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

## 2. As regras do seu trabalho (94)

**Windows e instalador (e qualquer conversa com programa de fora)**
- A janela nunca congela: Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min). (CLAUDE.md §3)
- Texto com acento, caminho sem acento: Texto de tela com acento (UTF-8); caminho de disco sem acento. (CLAUDE.md §3)
- core/ não importa ui/: core/ nunca importa ui/: o processamento roda por linha de comando, sem janela. (CLAUDE.md §7)
- Onde o programa guarda estado: %LOCALAPPDATA%\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta. (CLAUDE.md §7)
- Uma peça só para conversar com o que está fora: Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito). (CLAUDE.md §11.12.1)
- Antes de escrever, a lista das falhas: No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade. (CLAUDE.md §11.12.3)
- Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-785): à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele.**
- Pesquisador: roda aqui e no notebook do Kaique?: Windows, Python 3.14, GTX 1650; notebook i5-1235U, 32 GB, Iris Xe. Se precisar de Linux/WSL, dizer. (pesquisador.md 'O que você faz')

**Testes**
- Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
- Teste de olho: prepara, abre tudo, para e chama: Antes/depois, abrir TODAS as imagens (nunca amostra: '10 de 10' com seis erradas), opinião com ressalvas, parar e chamar. (CLAUDE.md §4.2) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
- Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-787): vale a regra de 19/10: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.**
- Filtro de velocidade no GitHub: Mudança em processamento passa pelo filtro de velocidade do GitHub (antes e depois na mesma máquina). Não rodar o teste_velocidade completo no PC. (CLAUDE.md §4.6) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-786): vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase.**
- Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
- Teste de imagem pelo caminho inteiro: Teste de imagem e conferência levam a página por dividir → endireitar → cortar → filtro, com ajustes de fábrica, até a ferramenta testada. (CLAUDE.md §4.10)
- Só páginas que vão ser impressas: Nunca lombada, capa ou contracapa de couro ou papelão nos testes. (CLAUDE.md §4.10)
- Régua e velocidade; nada mais lento: Rodar a régua e o teste de velocidade; piorou, reverter ou apresentar os dois. Nenhum item deixa o programa mais lento. (CLAUDE.md §8 passo 5) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-786): vale a regra de 19/10: velocidade no GitHub a cada mudança; no PC, no fim da fase.**
- Antes/depois só nas páginas-gabarito do item: O verificador gera o antes/depois só com as páginas-gabarito do item (gabarito/lista.json) e abre todas. (CLAUDE.md §8 passo 6) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Item de tela: janela real com mouse nativo: Item de tela se prova pilotando a janela real com mensagens nativas de mouse; clique simulado do Qt sozinho não vale (passou duas vezes com o uso real falhando). (CLAUDE.md §8 passo 6)
- Quem confere não construiu, e confere do zero: Quem confere nunca é quem construiu; abre o programa do zero; para cada decisão: cumprida / pela metade / não cumprida, com print ao lado das palavras. (CLAUDE.md §11.5)
- Verificador confere o que funcionava ao redor: O verificador confere também o que já funcionava ao redor (clicando, em trabalho de tela). (CLAUDE.md §11.8)
- Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
- Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')
- Verificador: não conserta código: Achou falha: relate. Nunca altere core/ ou ui/. (verificador.md passo 1)
- Verificador: skill conferir-testes-visuais: Abrir as imagens uma por uma seguindo a skill .claude/skills/conferir-testes-visuais. (verificador.md passo 4)
- Pilotar: instância nova, nunca a dele: Abrir uma instância nova (pythonw main.py) e fechar a sua com WM_CLOSE. (verificador.md 'Como pilotar')
- Pilotar: mouse por mensagem nativa ao hwnd: SendMessage/PostMessage direto no hwnd: funciona sem foco e não rouba o mouse dele. (verificador.md 'Como pilotar')
- Pilotar: nunca pywinauto click_input/send_keys: click_input e send_keys tomam o mouse e o teclado do Samuel. (verificador.md 'Como pilotar')
- Pilotar: roda do mouse não funciona sem foco: WM_MOUSEWHEEL sem foco não funciona (100 tentativas); se depender de roda, dizer na ressalva. (verificador.md 'Como pilotar')
- Pilotar: print fora da tela: Janela em -32000 com SW_SHOWNOACTIVATE e PrintWindow com PW_RENDERFULLCONTENT (minimizada sai preta). (verificador.md 'Como pilotar') **Outro texto das regras diz diferente; resolvido pelo Samuel (D-785): à vista o que mexe com o Windows (a lista da D-785); escondidos os testes que não dependem dele.**
- offscreen não tem fonte: QT_QPA_PLATFORM=offscreen serve para geometria e imagem, não para conferir texto. (verificador.md 'Como pilotar')
- Verificador: prova de reversão numa cópia à parte: Rodar o teste novo no código antigo numa cópia à parte e mostrar que falha; teste que passa nos dois é ressalva grave. (verificador.md 19/10)

**Git e arquivos**
- Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
- Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
- Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Outro texto das regras diz diferente; resolvido pelo Samuel (D-796): o agente de tela mexe em core/ só nos arquivos que o pedido nomear; sem isso, só ui/.**

**Todo trabalho**
- Ordem de leitura e quem manda: Quem manda: o Livro de decisões e o plano; o CLAUDE.md vem depois. O que ele disser contra o plano, vale o plano. (CLAUDE.md topo) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- PEDIDOS.md e handoff são histórico: PEDIDOS.md e o handoff em historico/ só servem de consulta; não dizem o que fazer. (CLAUDE.md topo)
- Critério final do livro: 'Eu quero que o papel saia branco, e o desenho também saia perfeito.' (CLAUDE.md §1)
- Não recomeçar do zero: Não reescrever módulo inteiro nem reorganizar o que funciona. Testar não é licença para reconstruir. (Duas versões já fracassaram.) (CLAUDE.md §2)
- Ir até o fim dentro da alçada: Decidir o que é da alçada e executar tudo, sem parar a cada passo. Se o contexto acabar, parar num commit com o programa rodando. (CLAUDE.md §2)
- Primeiro a frase, depois o número: Primeiro a frase que se entende ('estava estragando a capa'), o número depois, nunca no lugar. (CLAUDE.md §2)
- Conciso: essencial no chat, detalhe em arquivo: O essencial no chat; o detalhe em arquivo. (CLAUDE.md §2)
- Claro e direto com o Samuel: Poucas linhas, uma ideia por frase, os nomes da tela, no máximo uma pergunta sim/não com a sugestão; nada de tabela, número de decisão ou nome de arquivo. (CLAUDE.md §2)
- Honesto: avisar erro e risco: Se o Samuel ou a gerente estiver enganado ou correndo risco, avisar. Não concordar para agradar. (CLAUDE.md §2)
- Relatório em três formatos: Todo relatório sai com relatorio.gravar (.md, .html, .pdf). O Samuel não abre .md. (CLAUDE.md §2)
- PySide6, nunca tkinter: PySide6, nunca tkinter nem customtkinter (uma versão anterior travava). (CLAUDE.md §3)
- Uma página por vez na memória: O pico de memória não cresce com o livro (há livro de 300 MB). Nunca uma lista com todas as páginas processadas. (CLAUDE.md §3)
- Nenhuma exceção fecha a janela: Erro vira aviso em português numa caixa; o técnico vai para o log. (CLAUDE.md §3)
- Nenhum emoji em rótulo: Nenhum emoji em rótulo de tela (quebrou no Windows). (CLAUDE.md §3)
- Algoritmo consagrado: Algoritmo consagrado em vez de fórmula própria (a fórmula caseira deu qualidade ruim). (CLAUDE.md §3)
- Nenhum modelo generativo: Nada que desenhe pixel ou invente texto: inventaria detalhe numa gravura de 1579. Rede neural só aponta onde está a coisa. (CLAUDE.md §3)
- Python 3.14, não rebaixar: A máquina só tem Python 3.14. Nunca sugerir rebaixar. (CLAUDE.md §3)
- GPU sem float16 rápido: GTX 1650 4 GB, sem tensor cores: nada que dependa de float16 rápido. O notebook do Kaique não tem placa de vídeo. (CLAUDE.md §3)
- Erro nunca como stack trace: sys.excepthook grava em erros.log e mostra 'Aconteceu um problema inesperado, mas o programa continua funcionando.' (CLAUDE.md §3)
- Licença: GPL pode entrar: Código GPL pode ser incorporado (17/09); a licença de cada peça tem de estar escrita. (CLAUDE.md §3)
- Ler a memória antes: Antes de começar, ler memoria/INDICE.md e as fichas do assunto. A memória nunca contradiz o plano. (CLAUDE.md §4.9)
- Cada foto diz o caminho e as opções: Toda foto diz por onde a página passou ('endireitada, cortada, Preto e branco + Só as letras'). (CLAUDE.md §4.10)
- Protocolo de mudança de imagem: Medir antes, uma mudança, medir de novo; piorou, reverter. Se valer mesmo assim, não reverter sozinho: apresentar os dois. (CLAUDE.md §5)
- Tudo o que foi tentado vai para melhorias.md: O que foi tentado, inclusive o que falhou, vai para relatorios/melhorias.md (para ninguém repetir caminho fechado). (CLAUDE.md §5)
- O que o agente decide sozinho: Pode decidir: limiar, janela, k, bloco, ordem interna do filtro, binarizador, cache, paralelismo, memória. (CLAUDE.md §6)
- Modelo de dados em dois níveis: ConfigFolha (o que veio) e ConfigPagina (o que sai); ajustes de cada filtro separados; recorte e ângulo na página. (CLAUDE.md §7)
- Desempenho já resolvido, não refazer: Análise a 150 DPI e fundo estimado em miniatura de ~400 px: não refazer. (CLAUDE.md §7)
- Ordem obrigatória do processamento: Livro novo: dividir → endireitar → cortar → filtro → cadernos. Projeto de antes de 09/10 sem ordem_do_preparo: a ordem antiga, idêntica. (CLAUDE.md §7)
- Queixas do Kaique são requisito: Os .txt com print em 'Teste de livros' são fonte de requisito. (CLAUDE.md §7)
- Item da fase atual, na ordem: O item vem da fase atual do plano; Lista de bugs no começo da fase. (CLAUDE.md §8 passo 1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Mancha do verso: o defeito mais grave: O Preto e branco escurece a mancha do verso; a régua não pega. Caminho recomendado: espelhar o verso e subtrair. (CLAUDE.md §9)
- A régua precisa de critérios novos: Comparar onde havia mancha, olhar a moldura, medir sujeira guardada. (CLAUDE.md §9)
- Amarelado está na tinta: A tinta de 1579 é marrom; cuidado: rubricação desbotada também é marrom. (CLAUDE.md §9)
- Não há binarizador vencedor: Os 18 do DoxaPy se invertem de livro para livro. (CLAUDE.md §9)
- Não desfazer a correção do 'magic color': Dividir pelo fundo relativo ao papel, ganho igual nos três canais, curva de ombro no L: não desfazer (a receita comum estraga capa colorida). (CLAUDE.md §9)
- Scan de baixa resolução não se recupera: O remédio é reescanear; é o único lugar onde 'até ficar perfeito' não vale. (CLAUDE.md §9)
- Barra de rolagem cinza, de propósito: A barra de rolagem é cinza #a8a49e de propósito; não reverter sem decisão do Samuel. (CLAUDE.md §9)
- Layout só começa com o plano de layout: O layout só começa com o plano de layout entregue; sem ele, responder 'O plano de layout ainda não foi entregue. Não comecei.' (CLAUDE.md §10.1)
- Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs: Ideia nova: não fazer, anotar para a Lista de espera. Bug que impede a tarefa: consertar e dizer. Bug que não impede: anotar com data e print. (CLAUDE.md §10.2) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Docstring em tudo o que tocar: Todo arquivo e função tocados ganham docstring: o que faz e o que é seguro ou arriscado mudar. (CLAUDE.md §10.5)
- Plano novo não apaga pendência: Plano novo diz o que resolve e o que deixa de fora; nunca apaga pendência por omissão. (CLAUDE.md §10.6)
- Prosa de checkpoint não é prova: Quando o estado importa, conferir o código e o git log, não o texto de checkpoint. (CLAUDE.md §10.8)
- Modelo de print (o do girar): Imagem-resumo; faixas azul (antes), laranja e verde (as opções); as mesmas páginas em todas; o que olhar circulado em vermelho; imagens separadas com legenda. (CLAUDE.md §10.10)
- Perguntar: print que prova: Toda pergunta e todo 'está feito' com print do caso real no modelo do girar; uma imagem por opção. (CLAUDE.md §11.13.3)
- Perguntar: o caso que o Kaique encontra, print conferido: O livro e a página onde acontece de verdade, pelo caminho inteiro; abrir o print e conferir. (CLAUDE.md §11.13.4)
- Perguntar: o caminho, e se é defeito ou escolha: Dizer o caminho que a página fez e, com todas as letras, se é defeito ou efeito de escolha (ou 'ainda não se sabe'). (CLAUDE.md §11.13.5)
- Perguntar: curto, sem ficha: Poucas frases; nada de ficha com campos; responder cada pergunta dele na ordem; a resposta se explica sozinha. (CLAUDE.md §11.13.7)
- Perguntar: ele continua no controle?: Dá para ligar e desligar? ajustar? onde aparece? quando age? (CLAUDE.md §11.13.8)
- Perguntar: de onde veio: Pedido dele (data e palavras), ScanTailor, ou escolha de agente sem pedido (dito com todas as letras); como outros programas fazem. (CLAUDE.md §11.13.9)
- Perguntar: a situação de agora, sem repetir: Em que pé está; procurar no Livro e na Central antes; se já respondeu, citar data e palavras. (CLAUDE.md §11.13.10)
- Obra D-014: o que não vale durante a obra: Durante a obra não valem 'conferir cada item antes do próximo' nem 'uma fase por vez'; nada entra no fase-1 antes da conferência final; duas decisões que se contradizem: vale a mais recente. (CLAUDE.md fim) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
- Defeitos conhecidos da Fase 1 em destaque: Até a Fase 1 ficar pronta, avisar que moldura dourada e iluminura são defeito conhecido; conferir as regras do resultado da Fase 1. (verificador.md passo 6)
- Pesquisador: não repetir caminho fechado: Ler antes TESTE-SCANTAILOR-MISTO, OCR-PESQUISA, melhorias.md e docs/pesquisa/. (pesquisador.md 'Leia antes')
- Pesquisador: resumir com as próprias palavras: Pode citar arquivo, função e trecho curto para localizar; o resumo é seu. (pesquisador.md 'O que você faz')
- Pesquisa gravada em docs/pesquisa/ com data e links: As conversas não se enxergam: só os documentos ficam. (pesquisador.md 'O que você faz')
- Não instalar no .venv sem pedido: Nunca instalar nada no .venv do projeto sem a gerente pedir. (pesquisador.md 'nunca')
- Layout: pista visual em toda área de clicar: Toda área de clicar ou arrastar tem cursor, alça ou contorno (um arrasto 'não funcionava' só porque ninguém via onde clicar). (layout.md 'Regras de tela')
- Toda função automática tem ligar e desligar: Toda função automática tem botão de ligar e desligar (regra 8 do plano). (layout.md 'Regras de tela')
- Layout: ler a Lista de espera e as referências: Há ideias de layout do Samuel na Lista de espera, com imagens em docs/plano/referencias-layout/. (layout.md 'Leia antes')

## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)

- **D-767** (18/11/2026): Chat, na etapa 5, depois dos 7 defeitos achados no Windows de verdade (a gerente explicou que os testes automáticos trocam as peças do Windows por peças de mentira): "não faça mais nada escodindo ou de mentira" · logo depois: "não quero fazer consertos quero que funcione" · e: "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
  Na prática: O que mexe no Windows (pergunta de administrador, PowerShell, tarefas, licenças de pasta, instalar e desinstalar, testes à distância) só conta como pronto quando roda de verdade no Windows, à vista, e funciona. Teste automático com peça de mentira não prova que funciona. Nada de área de trabalho escondida nos testes. O objetivo não é remendar cada defeito, é a parte do Windows funcionar inteira (CLAUDE.md §11.12). O alcance exato (por exemplo, as versões de teste servidas de uma pasta do D: em vez do GitHub) está sendo confirmado com o Samuel.
- **D-773** (18/11/2026): Chat, decisão 6 do plano da parte do Windows ("de onde vêm as versões nas provas"; A = versões de verdade servidas por uma janela visível no PC do Samuel, mais uma versão de teste no GitHub como rascunho, liberada só na prova e apagada no fim, sugestão; B = tudo pelo GitHub; C = sem GitHub): "A"
  Na prática: Nas provas, as versões são versões de verdade do programa, baixadas pela rede de verdade de uma janela pequena e visível no PC do Samuel que faz o papel do GitHub (fechar a janela prova a internet caindo no meio). Para provar o publicar, uma versão de teste vai ao GitHub como rascunho, é liberada só durante a prova e apagada no fim (ninguém tem o programa instalado). Define o alcance da D-767 para as versões de prova; ajusta a D-713 (nada no GitHub nesta etapa) só para esse rascunho de prova.
- **D-775** (18/11/2026): Chat: "o agente vai tentar quebrar antes de fazer o teste real na tela né?" (a gerente descreveu a ordem abaixo) · "ok"
  Na prática: A ordem de cada passo do plano da parte do Windows: (1) um agente escreve a peça; (2) os testes automáticos rodam, cobrando o jeito certo; (3) outro agente, que não escreveu, tenta quebrar (lê procurando falha não pensada, resultado não conferido e peça duplicada; roda o que dá sem pergunta do Windows); (4) só então a prova de verdade e à vista na tela do Samuel. Se o passo 3 achar problema, volta ao 1; o Samuel só é chamado quando a peça passou pelos três primeiros. Completa a D-767.
- **D-776** (18/11/2026): Chat, decisão 8 do plano da parte do Windows ("montar a versão no disco de dentro do PC"; A = no C:, sugestão; B = continua no D:): "Sim, no C só tem que cuidar para não encher o disco C inteiro"
  Na prática: Publicar monta a versão no C: (o disco de dentro, muito mais rápido que o HD externo), com cuidado para nunca encher o C:: antes de começar, o publicar confere o espaço e não começa se, somando o que vai usar (6 a 10 GB), o C: ficaria com menos de 20 GB livres (Samuel, 18/11, à pergunta "Fica 20 GB?", depois de a gerente explicar as atualizações do Windows e a memória virtual: "ok"; a sugestão de 15 GB foi trocada por 20 GB a pedido dele: "acha que isso é suficiente?"); ele vigia o espaço durante o trabalho e para com aviso se cair perto da reserva; e o rascunho é apagado no fim, também quando dá erro. O Kaique recebe exatamente a mesma atualização.
- **D-795** (19/11/2026): Chat, ponto 1 do plano-v2 §6.3 (o Setup.exe que continua saindo, D-777, contra o motor sempre dentro do instalador, D-788/D-727). Ele: "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o que isso serve?". A gerente corrigiu o "pequeno" (é rápido de fazer, 2 s, mas leva o pacote inteiro, ~826 MB, `relatorios/publicar-rapido-2026-11-18/relatorio.md`), explicou que é o instalador padrão do Velopack, que a 1.2.161 recusa `--noInst` com `--noPortable` (medido) e que usamos o .msi por instalar em Arquivos de Programas para todas as contas (`--msi --instLocation PerMachine`, `docs/pesquisa/atualizacao-e-testes-a-distancia.md`, ramo `estudo-kaique-2026-11-16`), e perguntou "Então ele vai continuar sendo feito, mas não precisa ir para o GitHub nem para o Kaique. Sugiro apagar no fim de cada publicação. Pode ser?": "ok"
  Na prática: O Setup.exe continua sendo feito pela ferramenta (ela não deixa tirar), mas não é publicado no GitHub nem mandado ao Kaique: o publicar o apaga no fim de cada publicação, também quando dá erro. O Kaique só recebe o .msi (primeira entrega e quando o Samuel pedir, D-777) e as atualizações. Responde o ponto 1 do plano-v2 §6.3; ajusta a D-777 ("ele continua saindo").
- **D-798** (19/11/2026): Chat, contradição X4 das regras dos agentes (CLAUDE.md §4.3: "o Claude Code pode escrever PRONTO PARA CONFERIR"; `implementador.md`: "quem escreve isso é o verificador"). A gerente: "quem pode dizer que um trabalho está "pronto para você conferir"? [...] Sugiro: só o que confere, e nunca o que construiu. Pode ser?": "fechou"
  Na prática: Só o agente que confere (o verificador, ou o que tenta quebrar, D-775) escreve "PRONTO PARA CONFERIR", e nunca sobre um trabalho que ele mesmo construiu. Quem constrói entrega à gerente sem esse rótulo. "APROVADO" continua sendo só do Samuel. Resolve a contradição X4 (completa o CLAUDE.md §11.5).
- **D-811**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)
- **D-812**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)
- **D-813**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)

## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)

Use estes títulos de seção, exatamente assim. "Não se aplica" só vale com o motivo ("não se aplica: este passo não pede licença ao Windows"). Nas decisões, as palavras do Samuel vêm entre aspas logo depois do número, copiadas do Livro; o seu comentário vem depois de "Aqui:". Confira antes de entregar: `python -m regras_dos_agentes entrega relatorios/<pasta>/ONDE-PAREI.md --etapa quebrar`.

## O que li

(a preencher)

## O que conferi nas falhas, nas peças de fora e nos caminhos

(a preencher)

## Caminhos que o outro não listou

(a preencher)

## Falhas não pensadas e resultado não conferido

(a preencher)

## As regras que conferi

(a preencher)

## Achados

(a preencher)

## 5. O que você não recebeu, e quando parar

Este pacote não traz as regras de: nada (recebeu todas). Se precisar mexer num arquivo fora da lista do pedido, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.
