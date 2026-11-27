# Parte B: os tipos de erro que já aconteceram e o destino de cada um (27/11/2026)

**Em uma frase:** os erros que já aconteceram cabem em 31 tipos; em 29 deles o pedido do Samuel estava claro e foi
feito diferente (erro de programação), e em 2 não dá para saber sem ele. As vezes em que ele mudou de ideia depois de
ver (38 decisões trocadas por outra mais nova) não são erro: ficam só como registro, numa seção à parte.

Feito pelo agente da triagem, só lendo (D-887). Nenhum arquivo do projeto mudou. Não é uma linha por erro: é uma linha
por tipo, com 3 exemplos que dá para conferir na fonte.

## De onde veio

| fonte | o que li | onde achei |
|---|---|---|
| Livro de decisões | as 898 linhas (861 decisões, até a D-886), filtradas pelas palavras dele que mostram erro; as 97 de "Testes e forma de trabalhar" e as 220 de 26/10 em diante, inteiras | `docs/plano/DECISOES.md` desta cópia |
| Central, lida da página em 27/11 | as 353 respostas (207 comentários dele, com os anteriores e a conversa) e as 28 abas, inclusive as 6 de auditoria | pasta `central-27-11` da gerente (fora do git) |
| Quem tenta quebrar o atualizador | os 5 relatórios, inteiros nas seções de achados | `relatorios/atualizador-novo/quem-tenta-quebrar-1` a `-5/relatorio.md` |
| Resposta do Fable | inteira | **só na pasta principal**: `D:\programas\EditorImpressao\relatorios\para-o-fable-2026-11-23\resposta-do-fable.md` (não existe nesta cópia) |
| Lista de bugs | as contagens e os títulos | `memoria/bugs.md` (pasta principal e esta cópia) |
| Testes guiados | a lista única de 23/10 (50 itens) e o "o que deu errado" de 26/10 | `relatorios/testes-guiados/` |
| Conferências antigas | os 19 títulos, sem ler um a um (as palavras dele já estão no Livro) | `relatorios/conferencia-samuel-*.md` |
| Auditoria das escolhas | inteira no resumo e nas seções B e C | `relatorios/obra-auditoria-escolhas/auditoria.md` |
| Fontes a mais, que já agrupavam erros | o catálogo dos erros (76 erros, famílias F1 a F10), as lições (A1 a G3) e a lista da vistoria (só leitura) | `memoria/catalogo-de-erros.md`, `memoria/licoes.md`, `obra-juncao/.../vistoria-gambiarras-2026-11-26/lista.md` |

## Como ler

- **causa**: **1** = erro de programação (o pedido estava claro e foi feito diferente); **2** = mudança de ideia (foi
  feito como pedido e ele quis outra coisa depois de ver; fica só como registro); **3** = dúvida (não dá para saber).
  A coluna "por quê" diz que frase dele comparei com o que foi entregue.
- **vezes**: conta aproximada, com a fonte da conta. Um mesmo erro pode aparecer em duas fontes; não somei entre tipos.
- **destino**: os mesmos da Parte A. **quem cobriria**: o fiscal, skill, gancho ou permissão que pegaria o próximo,
  em palavras; nada disso é plano de construção.

## A tabela

### Construído diferente do que ele mandou

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E01 | Decisão anotada e não construída, ou feita só na aparência | "Photoshop puro" de 25/09 feito só no desenho, a regra de julho ficou por baixo (`testes-guiados/2026-10-26-sessao-1/o-que-deu-errado.md`); Auditoria 2 da Central: 24 "não feito"; D-594: "no automatico não tem opções que encontramos nos filtros [...] isso era uma coisa obvia que deveria ter" | ~80 (24 da Auditoria 2, 32 "com ressalva" da Auditoria 3, mais as "pela metade" do Livro) | 1 | as palavras de 25/09 e a D-594 estão no Livro; o entregue não as cumpria | FISCAL GITHUB | toda decisão "construída" com a sua prova de comportamento rodando (as `test_decisoes*.py`); um fiscal rápido que acuse decisão "construída" sem prova citada |
| E02 | O agente acrescentou o que não foi pedido, ou mudou o que ele decidiu | auditoria de 27/10: 17 acréscimos e 6 mudanças (`obra-auditoria-escolhas/auditoria.md`); `k0711-voltar-inserida`: "Isso é uma alucinação é justamente o erro que nossos agentes têm cometido o tempo inteiro"; `211-reduzir`: "quando foi que eu pedi para fazer isso?" | ~45 (23 da auditoria, 19 "escolhas da gerente" da Auditoria 5, 37 cartões "acrescentei sem você pedir"; 44 decisões do Livro dizem "escolha da gerente") | 1 | D-549: "é só para fazer o que eu já tinha mandado"; o acréscimo não tem frase dele | FISCAL RÁPIDO | arquivo ou campo novo fora do "Dentro" da ordem barra (hoje a K14 só avisa) |
| E03 | O que o Kaique escolheu não vale (caixinha desmarcada roda, volta marcada) | `caixinhas-endireitar-cortar-limpar`: "quando volto no automatico as coisas que rodaram estão marcadas, elas tem que voltar todas desmarcadas"; D-589 (desmarcar "Montar cadernos" não valia); lista única 2.5 "mudar as caixinhas num livro já conferido não vale" (aberto desde 29/09) | ~6 | 1 | o pedido do Kaique e do Samuel é literal; o programa fazia outra coisa | FISCAL GITHUB | prova de comportamento: desmarcar → a etapa não roda e volta desmarcada |

### Remendo e estrutura do código

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E04 | Conserto só no caminho do defeito (a mesma ferramenta faz diferente em outro lugar) | D-662 feita só no "todas as folhas" → D-666 e D-667 ("quando eu mandei fazer, porque o gerente não fez em tudo?"); "Só as letras" consertado só nas figurinhas, errado no "comparar" (revisão de 10/11, A2); D-640 → D-645 | 17 remendos (revisão de 10/11); o Girar em 9 voltas (Fable) | 1 | D-667: a ferramenta inteira; o pedido ao agente nomeou um item só (parte é da gerente) | FISCAL RÁPIDO | leitura do código: cada campo gravado por uma porta só; e um teste que cobra o mesmo resultado por todos os caminhos |
| E05 | A mesma conta ou lista escrita em mais de um lugar, que diverge | vistoria G-06: a página girada desenhada em cinco lugares; revisão M9: os campos do filtro em seis lugares, já diferentes; `lu-2-numeros`: "o motor de contagem deveria valer para todo o programa e não fazer uma conta em cada lugar" (D-760) | 113 na vistoria até agora (tipo 1, de 167 achados); 10 dos 16 remendos (Fable, Pergunta 5) | 1 | §11.12 (13/11) pede um lugar só; o código tem vários | FISCAL RÁPIDO | as travas do Fable (Pergunta 2): listas tiradas do modelo de dados; uma porta única de comandos; leitura de código que acusa a segunda cópia |
| E06 | Conta ou decisão feita na tela, em vez do núcleo | vistoria tipo 2 (G-05: a regra da D-640/D-645 mora na tela); Fable: `_registrar` carrega regra de domínio na tela; vistoria FL e PT (perfis, prévias) | 9 na vistoria | 1 | §11.12: "de preferência em `core/` (a tela só chama)" | FISCAL RÁPIDO | leitura do código: método de `ui/` que monta campos da página (a "trava inversa" do Fable, Pergunta 6) |
| E07 | Desvio por caso ("se veio de tal lugar, faz diferente") | vistoria G-01: o girar escolhe entre seis jeitos pelo jeito de ver a tela; `if alcance == ALCANCE_TODAS` só para a D-662; revisão A4: o Automático e o "não dividir esta" deixam a folha inteira de dois jeitos | 13 na vistoria | 1 | §11.12: "Nada de desvio para um caso" | FISCAL GITHUB | um teste por ferramenta que passa por todos os caminhos e cobra o mesmo resultado (R109) |
| E08 | Peça que só existe para proteger outra (camada a mais) | Fable: no atualizador antigo, ajudante de sistema, 2 scripts, vigia, 3 cadeados, bilhete entre contas; quem tenta quebrar 3 e 4: os graves todos na volta automática e na última boa; vistoria tipo 4 | 13 na vistoria; o atualizador inteiro refeito (D-830) | 3 | o pedido ("volta sozinho", D-718) foi cumprido; o que falhou foi o desenho, e ele tirou a volta depois de ver o custo (D-868) | DÚVIDA | — (precisa dele: conta como erro de programação ou como pedido que custou mais que valia?) |
| E09 | Código morto | D-876: `configuracoes.espaco_livre_mb`, de julho, ninguém chama; vistoria tipo 5; a tela "O que fazer" que ficou no repositório sem abrir (D-488) | 19 na vistoria | 1 | ninguém pediu para guardar | FISCAL RÁPIDO | caça de função sem quem chame, lendo o código (Fable, frentes depois da entrega) |

### Conferir e testar

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E10 | Dá como feito o que não conferiu; a tela mostra o que o programa anotou | etapa 5: "Desligado" gravado sem desligar (§11.12, 18/11); P1-ger-1: escreveu que `modelos/` "continua inteiro" sem conferir, e estava vazia; quem tenta quebrar 2, G1: "voltou para a versão anterior" sem ter voltado | ~25 (9 da família F5; os 7+26 da etapa 5 em boa parte; os graves 1 a 4 de quem tenta quebrar) | 1 | §11.12 ponto 2 (18/11); A1 das lições (57 commits "feito") | FISCAL GITHUB | desligar a conferência numa cópia e ver um teste falhar (mutação automática, Fable Pergunta 3) |
| E11 | Proteção que nenhum teste acusa quando desligada | quem tenta quebrar 1, M3: nove proteções; quem tenta quebrar 2, M9: cinco; P1-v1-13: três (M10 a M12) | 6 erros na família F3 e 5 rodadas seguidas do atualizador (27 proteções) | 1 | D-811 e D-827 ("nunca é pequeno"), e continuou | FISCAL GITHUB | mutação automática a cada envio, sobre as peças do Windows e a máquina de estados |
| E12 | Teste que confere texto e não comportamento, ou peça de mentira que passa | Fable: `assert "MarcaExiste" in lancados[0]`, trocar `return $true` por `$false` e os 55 testes passaram; etapa 5: os testes trocavam o Windows por peças de mentira (D-767); C3 das lições: o clique simulado passou e o uso real falhou (22/09, duas vezes) | ~6 casos grandes | 1 | §11.4 ("aparência não é prova"), D-767 | FISCAL GITHUB | mutação automática; e fiscal rápido que acuse teste que só procura uma palavra num texto de comando |
| E13 | Teste que supõe o computador, a língua ou o estado de hoje | P1-gh-3: o Windows do GitHub escreve "Everyone", o teste procurava "Todos"; P1-gh-1: pasta temporária no D:; D-751: o teste da chave privada falhou só no GitHub | 8 (família F4) | 1 | não havia regra até a D-810 (19/11); depois, a regra existe | REGRA POR PASTA | a lista dos três computadores entregue a quem escreve teste do Windows (R157) |
| E14 | A conferência acredita num dado que o próprio conferido escreve | P0-N1 e P0-R1: o "sim" do Samuel forjável copiando 12 letras; P0-R2: o juiz escolhido pelo próprio ramo; P1-v1-02: um arquivo da vez anterior fazia a prova dizer "rodou" | 15 (família F1) | 1 | não havia regra até a D-812 | FISCAL RÁPIDO | a pergunta F22 do formulário ("de onde vem cada dado"), conferida por quem tenta quebrar |
| E15 | A recusa olha o jeito mais comum e o vizinho passa | P0-v1-02: a busca do Windows conhecia 13 palavras, outra palavra passava; P1-v2-N2: `\\?\` e `\\localhost\C$` passavam; P0-S2/S3: `.pyw` e `.pyd` não eram lidos | 20 (família F2, mais P1-v3-T1) | 1 | a D-813 (19/11) pede listar tudo o que a peça aceita | FISCAL RÁPIDO | conferência por estrutura (o que o código importa), não por lista de palavras (Fable, Pergunta 4) |
| E16 | Falso alarme da conferência | P0-N5: `creationflags=0` contava como Windows; P0-R6: abrir sem a janela preta contava; P1-port-1: o nome da ferramenta numa lista de recusa | 4 (família F8) | 1 | erro do próprio fiscal | FISCAL RÁPIDO | já resolvido do jeito de hoje: cada falso alarme vira teste com o exemplo certo |
| E17 | O novo estragou o que já funcionava (sem ninguém ver antes dele) | D-668: os quadrados brancos começaram em dois commits de 26/10; D-659: "todas aquelas mudanças [...] no manual não está funcionando, isso é um grande erro"; `lu-1-remendos` nos rostos (Lusíadas 14) | ~10 (provas do Lusíadas, 13 cartões; graves de 10/11) | 1 | D-605 (03/11): "nenhuma função nova [...] pode alterar o que já está escolhido e testado" | FISCAL GITHUB | prova por decisão e medida de imagem nas páginas do gabarito, a cada mudança |
| E18 | Tela, miniatura, prévia e PDF diferentes | `lu-tc-igual`: "O pdf está saindo diferente da tela gerada"; `k0711-miniatura-pdf`: "Isso é um erro grave. O preview as miniaturas tem que estar sincronizada"; Fable: três jeitos de desenhar o "como fica" | ~10 respostas da Central | 1 | D-066 e D-473: "precisamos que o pdf saia que nem está na tela" | FISCAL GITHUB | teste de pixels: os três caminhos de desenho devolvem a mesma imagem (Fable, Pergunta 2, item 3) |
| E19 | Velocidade medida do jeito errado | C2 das lições: medida com a máquina dividida (29 e 30/09); F9: medir direto no GitHub (20/10); P1-ger-2: a rodada inteira no PC com um jogo aberto | ~3 | 1 | as regras de 19/10 (D-458) e a D-807 | FISCAL GITHUB | o filtro de velocidade do GitHub, antes e depois na mesma máquina (já existe) |

### O computador e as coisas do Samuel

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E20 | Comando que mexe no que é do Samuel (pastas, git, junções) | D1 das lições: `D:\d` apagada (29/09); D2 e P1-ger-1: `modelos/` esvaziada por uma junção (07/10 e 18/11); P0-ger-1: `git fetch --depth=1` deixou o repositório do PC raso (19/11) | ~8 (D1, D2, D4, C4, C9 das lições; F9 com 4) | 1 | §10.9 (29/09) e D-809 | PERMISSÃO | o agente não poder apagar fora do projeto nem rodar comando que muda o `.git` inteiro; a K25 já acusa em script |
| E21 | Janela ou caixa na tela do Samuel, ou programa dele fechado | quem tenta quebrar 5: caixa de prova na tela dele às 14:17 e Explorador e app do Claude fechados às 14:27 (25/11); C5 das lições: "Tirar da lista?" esperando clique (30/09); P1-ger-2: a tela piscou e o serviço da Predator caiu | ~6 | 1 | o verificador.md (16/09 e 22/09) e a memória da gerente | PERMISSÃO | o agente não poder fechar processo que não criou; já existe a prova "sem janela na tela" (`test_sem_janela_na_tela.py`) |
| E22 | Agente abrindo agente, ou agentes demais no PC | 10/11: "pera ai, tem 5 agentes trabalhando" (§11.11); D3 das lições: quatro agentes esgotaram a memória (07/10); F1b: o limite da conta com 5 a 8 agentes | 3 | 1 | §11.11 e D-465 ("1") | PERMISSÃO | já feito: os agentes não têm a ferramenta (D-793, K23) |
| E23 | Trabalho perdido: sem commit, contexto acabou | D6 das lições: sem commit desde 17/09; F1 e F1b: o limite de uso derrubou agentes três vezes; D7: a cópia do plano do Samuel sobrescrita (25/09) | ~5 | 1 | as regras de 19/10 (commit e push a cada passo) | FISCAL RÁPIDO | a K18 (sem commit ou push) e um gancho ao terminar que lembre o commit |

### Falar com o Samuel

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E24 | Relatório ou pergunta que ele não entendeu | `dv-211-215`: "Um monte de texto e não consigo saber o que era para saber realmente"; `cantinho-outros-casos`: "esse teste é totalmente inconslusivo para mim"; `nm-tela-livros`: "Suas respostas ainda não são claras" | 40 das 353 respostas tiveram "Ainda não entendi" em algum momento; 24 decisões do Livro citam "não entendi"; 106 casos lidos para o §11.13 | 1 | D-383 (01/08): "seja mais direto" e D-450 (12/10) já pediam; continuou depois do §11.13 (13/11: `nm-*`, 17/11) | SKILL | a skill "como perguntar ao Samuel"; e a conferência da gerente antes de publicar |
| E25 | Pergunta sem prova, ou print que não prova o que o texto diz | `girar-capa-dividir-duas`: "como eu vou responder algo sem provas ou exemplos?"; `ac-tampa`: "essa resposta não tem print provando que esse modo funciona"; `au-d-541`: "Isso não é um print da ferramenta mover" | ~20 respostas da Central; B4 a B6 das lições (retângulo cobrindo o "A", 72 DPI, grade 3×3) | 1 | D-441 (05/10): "eu quero ver a coisa quando eu for escolher algo" | SKILL | a skill do print no modelo do girar; e um fiscal que barre pergunta sem imagem anexada |
| E26 | Exemplo ou teste com a página errada (lombada, folha não dividida, caminho pela metade) | `29-horas`: "essa lombada de couro não seria impressa nunca"; `n0411-caderno-pagina-em-branco`: "Porque usou uma folha sem estar divida?"; D-461: cortar sem ter endireitado antes | ~6 | 1 | D-461 e D-462 (20-21/10); depois delas o erro voltou (13/11) | SKILL | a skill do teste de imagem (caminho inteiro); a lista das páginas que não se imprimem guardada com o gabarito |
| E27 | Pergunta repetida, ou "como você escolheu" sobre o que ele não escolheu | D-452: "Porque essa opção voltou ? eu já não tinha respondido?"; `d602-juntada`: "eu já respondi, não deveria estar aqui como não respondido"; P0-R4: "como você escolheu" sobre 54 lugares, quando ele escolheu uns 10 | ~10 (B2 das lições, F6 com 4, 6 respostas da Central) | 1 | D-452 (14/10) | FISCAL RÁPIDO | a pergunta F23 ("decisões procuradas antes de cada pergunta"), cruzada com o Livro |
| E28 | Palavra de dentro (código, número de decisão, nome de etapa) na tela ou na pergunta | `k0611-codigo-g2`: "Não se deve usar código na nomeação de coisas"; as 9 exceções da K04 (dicas do Automático com "D-068" e "D-094"); "Que Obra?" (§11.13, regra 2) | ~12 | 1 | §11.13 regra 2 e o pedido de tela sem jargão (§1) | FISCAL RÁPIDO | a K04 para a tela (já existe); a mesma busca no texto para o Samuel |

### Registros e regras

| nº | tipo | 3 exemplos | vezes | causa | por quê | destino | quem cobriria |
|---|---|---|---|---|---|---|---|
| E29 | O escrito não bate com o código (registro que mente) | E1 das lições: checkpoint dizia "corrigido" e o CLAUDE.md o contrário (menu "Abrir"); A5: a mancha do verso dada como "feito e conferido"; P0-v1-16: o docstring do porteiro e o gancho não batiam com o código | ~8 (F7 com 4, E1, E2, A5) | 1 | §10.8 (22/09) | FISCAL RÁPIDO | o formulário já confere que a função e o teste citados existem |
| E30 | A gerente aceitou sem conferir (plano, "Fica", achado pequeno) | D-819: aceitou o plano de perguntar ao git quando havia o lugar fixo; D-827: tratou proteção sem teste como pequena; Fable, 24/11: "aceitei o 'Fica' sem perguntar por que essas duas ficavam" | ~5 | 1 | D-819, D-827, D-842 vieram dele depois de cada caso | FISCAL RÁPIDO | achado sem "consertar" ou "deixo para depois" dito por ele barra a prova (D-842); a ordem com "o jeito mais simples" comparado |
| E31 | Duas regras que se contradizem | catálogo das regras: 10 contradições (X1 a X10) e 6 diferenças pequenas; P0-v1-18: a cor da barra no §9 contra a da K22; X9: a obra, a D-765 e "uma fase por vez" | 16, das quais 4 ainda sem resposta (X3, X6, X9, X10) | 3 | não é pedido mal cumprido: são textos de datas diferentes | DÚVIDA | — (as 4 abertas precisam dele; as 6 resolvidas só precisam do texto acertado) |

## Mudança de ideia (causa 2): só registro

Não é tipo de erro, mas a ordem pede que fique separado. São pedidos feitos como ele pediu e que ele trocou depois de
ver. **Não precisam de fiscal.**

| exemplos | vezes |
|---|---|
| D-868: a volta automática sai da primeira entrega, depois de três rodadas ("é melhor a opção A; os aplicativos geralmente usam isso"); D-732: procurar versão ao abrir, não ao ligar o computador ("assim como todo aplicativo faz"); `ng-2-10-ver-o-livreto`: "Não gostei da tela que mostra o livreto, podemos mudar depois" | 38 decisões do Livro estão "substituída por" outra mais nova; 16 decisões autorizam trocar teste antigo, a maior parte porque o jeito mudou (D-644, D-663, D-740) |

## Contagens

- **Tipos:** 31. **Causa 1 (erro de programação):** 29 tipos (E01 a E07 e E09 a E30). **Causa 3 (dúvida):** 2 tipos
  (E08 e E31); e o E04 tem uma parte que é da gerente (o pedido ao agente nomeou um item só), contado como 1.
  **Causa 2 (mudança de ideia):** fora dos tipos, só no registro acima (38 decisões substituídas).
- **Por destino:** FISCAL RÁPIDO 13 · FISCAL GITHUB 9 · SKILL 3 · PERMISSÃO 3 · REGRA POR PASTA 1 · DÚVIDA 2 ·
  GANCHO, FICA NO CLAUDE.md e APAGAR: 0. Dois tipos teriam um gancho como segundo jeito: E23 (lembrar o commit ao
  terminar) e E24 (avisar a gerente quando aparece pergunta nova).

## Ressalvas

- **A Lista de bugs não foi classificada linha por linha.** Ela tinha 208 linhas até 20/10 (107 abertas) e mais os
  achados de 28/10 a 10/11. São defeitos do programa; os que li caem quase todos em E01, E03, E04, E17 e E18. Contar um
  por um pediria ler cada conserto no código.
- **A vistoria ainda está correndo.** Os números de E05 a E09 são os da lista em 27/11 às 15h (167 achados, ponta
  `543c719a` da cópia `obra-juncao`). Vão crescer.
- **"Vezes" é aproximado.** Onde a fonte já contava (catálogo dos erros, vistoria, auditorias da Central), usei a conta
  dela; onde não, contei os casos que achei por busca de palavras (ex.: "não entendi", "print", "prova").
- **Causa 1 ou 2:** comparei a frase dele guardada no Livro ou na Central com o que foi entregue. Quando a frase dele
  veio depois do erro (ex.: a D-810 para o E13), contei como 1 só a partir da data da regra; antes dela, era coisa que
  ninguém tinha pedido, e marquei isso na coluna "por quê".
- **As conferências antigas (`conferencia-samuel-*.md`) foram lidas pelos títulos.** As palavras dele que estão nelas
  foram trazidas para o Livro na etapa 0 (26/10), e foi pelo Livro que li.
- **Os 4 relatórios de quem tenta quebrar antes de 23/11** (passos 0, 1 e 2) entraram pelo catálogo dos erros, que já
  os agrupou; não os reli.
