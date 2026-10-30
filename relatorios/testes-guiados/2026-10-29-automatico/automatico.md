# Automático — apontamentos do Samuel, 29/10/2026

Trabalho: uma coisa por vez, e ele testa cada uma assim que fica pronta (D-576).

| # | Palavras dele | Print | O que é |
|---|---|---|---|
| a-1 | "vamos começar com a 1" (ver como vai ficar conforme as opções, na janela do Automático; 2-11 de 28/10) | — | D-577 |
| a-2 | "um bug que acontece quando nós usamos o automatico, de vez as paginas mudarem, elas continuam iguais, mas o que aparece são as marcações feitas no pdf, de gravura e de letras, tem que ter um jeito de aparecer e desaparecer essas marcações nas paginas." · "1- print quando estamos com a opção 1 pagina selecionada 2- quando estamos com o antes e depois" | ![](a-01-uma-pagina-marcacoes.png) ![](a-02-antes-depois.png) | D-578. *Na escola de Jesus*, página 12 de 199, ferramenta Pincel (marcar). No "antes / depois" a página sai certa (Preto e branco, gravura colorida); em "Uma página" aparece pintada de azul (letras), salmão (gravura) e verde (papel). |
| a-2b | "não tem nenhuma opção de marcação escolhida, está o zoom escolhido" (correção dele à explicação da gerente) | ![](a-03-zoom-tambem-mostra.png) | Página 8 de 199, ferramenta Zoom: as cores aparecem também. A gerente tinha dito "só nas ferramentas de marcar": errado. Ver a causa corrigida abaixo. |
| a-3 | "Outra coisa para adicionar ai, quando usamo o automatico temos que conseguir depois de ter passado ele diminuir ou aumentar ou mudar opções, caso não tenha saido como a gente queria e dai o programa recalcula isso que mudamos, nós mudamos em uma pagina e ele faz no resto" | — | D-579 |
| a-4 | "e quando mostra para fazer os cadernos lá na parte de fazer caderno tem que ter um botão para ver como vai ficar o caderno." | — | Já era a D-574 (28/10, 2-10: "eu deveria conseguir ver o livreto pronto aqui nessa tela"); palavras de hoje acrescentadas a ela. |
| a-5 | "outra coisa para adicionar na nossa lista, eu desfiz todo o historico e continuou a marcação antiga nas paginas. acho que como eu desfiz tudo, as marcações deveriam sumir também né?" | ![](a-05-desfez-tudo-marcacao-fica.png) | D-581. Print: histórico com todas as ações desfeitas (inclusive "Automático: endireitar folhas tortas, cortar ..."), faixa "Livro novo: ainda não passou pelo automático" de volta. Pela D-020 (18/07, "Ctrl+Z desfaz qualquer alteração"), sim: é defeito. |
| a-6 | "depois de rodar o automatico, quando eu tento escolher outro filtro para uma folha só, ele joga o filtro em cima do filtro que já tinha sido aplicado, e quando eu escolho outro filtro ainda, ele nem mostra a mudança em tela mesmo eu estando na opção antes e depois. Precisamos da opção de jogar o filtro em cima de outro filtro ou só substituir o filtro que está colocado em cima. ou só colocar os filtros em cima das gravuras, por exemplo nesse livro eu gostaria de passa o magico pro em cima de todas as gravuras que ele achou muito bem, mas não dá." | ![](a-06-filtro-em-cima-de-filtro.png) | D-582 (defeito), D-583 (empilhar ou substituir), D-221 (30/09: filtro nas áreas achadas; palavras de hoje acrescentadas). Print: capa, página 1, "antes / depois", Original × Preto e branco; a gravura sai colorida no Preto e branco com "Só as letras" desligado. |

## Causa do a-2 (lida no código da versão de teste, `obra-2026-10-26`)

Não é a página que deixa de mudar: o processamento está certo (o "antes / depois" mostra o Preto e branco). O que
acontece é que a vista da página (a mesma para o Zoom, a Mão e as ferramentas de marcar: `FERRAMENTAS_DE_NAVEGACAO` em
`ui/widgets/editor_selecao.py:95` são ferramentas do mesmo editor) pinta **sempre** toda a marcação da
página por cima da imagem, cada tipo numa cor (`ui/widgets/editor_selecao.py`, `_pintar_marcacao`, cores nas linhas
193-199: letra azul, gravura salmão, papel verde). Depois que o Automático roda a etapa de gravuras e fotos, a página
inteira fica marcada, e a imagem some debaixo das cores. A caixinha "Mostrar as áreas achadas" (D-237) só liga o
contorno laranja; não esconde o colorido. Então o conserto do a-2 e o "jeito de aparecer e desaparecer" são a mesma
coisa: um botão que mostra e esconde o colorido das marcações.

## Teste do item 1 (botão "marcações"), 29/10

- Pergunta dele: "Assim que eu abro o livro as marcações já aparecem se eu apertar no botão marcação, elas já estão feitas, acho que o programa já procura elas quando a gente abre ele né? mas se eu desmarcar elas saem." Resposta (código): o programa acha gravura, letra e papel sozinho ao desenhar uma página com filtro (`core/pipeline.garantir_selecao`); neste livro parte delas sobrou do Automático desfeito (D-581, item 2).
- Resultado dele: "deu certo, deu tudo certo, vamos para o proximo". D-578, D-580 e D-584 marcadas como testadas no Livro.

## Item 3 (D-582), investigação de 29/10
- Não é defeito de tela: a tela mostra o filtro escolhido toda vez (diferença 0,0 entre o que aparece e o desenho do filtro). O filtro não vai por cima do outro: cada escolha desenha a página de novo a partir do scan.
- O que fica "por cima" é a marcação que o Automático deixou ("Gravuras e fotos"): na capa, 82% da página virou "enfeite colorido", que guarda a cor em todos os filtros (D-144, D-127, D-128). Por isso Preto e branco, Melhorar e Mágico pro saem quase iguais (diferença 2,2 de 255) e parece que nada muda.
- Imagem da explicação: `relatorios/automatico-filtro/5-capa-nos-4-filtros-com-e-sem-a-marcacao.jpg` (ramo `automatico-filtro-2026-10-29`, commit `d4407e9`, só provas e relatório).
- Vira a pergunta D-583 ao Samuel; achado à parte na Lista de bugs (figurinhas do painel sem a marcação).
- "Só as letras" do Automático conferido em 29/10: funciona (livro, página herdada, tela, PDF, desfazer). D-585: causa achada (escrita por cima da pintura), sem conserto seguro; Samuel: "deixar como está e deixar anotado, vamos continuar para o que temos que fazer".

## Teste da caixinha "Respeitar as gravuras achadas" (D-583, D-586, D-587), 29/10
- Página 17 (pintura colorida saindo cinza no Preto e branco): é a D-147 (pintura e foto em tons de cinza). Os riscos laranja são o contorno das áreas achadas, ligado sozinho nas páginas com "!" (D-237); ele perguntou "porque estão ali, não são marcações". Pergunta da gerente (o botão "marcações" também esconder o laranja?) ficou sem resposta.
- Capa, caixinha desmarcada: "onde está a opção que deixa só cinza e branco ,essa parece que está dando um negativo". Não existe; vira a D-588.
- Resultado dele: "beleza, vamos deixar esse problema para resolver logo após terminamos os que nós propomos a fazer, o programa está mudando de efeito como deveria". D-583, D-586 e D-587 marcadas como testadas no Livro.

## Ordem da lista, 29/10 (fim do dia)
- Ele pediu a lista de novo ("acho que você está confundindo, olha a conversa e veja a lista e passa ela aqui pra mim"); a gerente repassou a de 14h59 (itens 1 a 8) com a situação de cada um.
- Ordem nova, palavras dele: "vamos deixar a 5 para depois, é mais importante fazer a 6 e a 7 e 8". Fica: D-577 (ver como vai ficar), D-579 (mudar e refazer o resto), D-574 (ver o caderno), depois D-221 (filtro nas gravuras achadas), depois D-588 (gravura em tons de cinza).

## Teste do item 6 (D-577, ver como fica na janela do Automático), 30/10
- Palavras dele: "ele não está funcionando, e não funciona em tela cheia também, como pode ver pelo print ele não muda no antes e depois conforme eu troco os filtros"
- ![](a-07-ver-como-fica-nao-muda-com-o-filtro.png) Janela do Automático, *Na escola de Jesus*, página 1 de 199 (capa), etapa 4 "Limpar a folha", Preto e branco + "Só as letras" + "Guardar a tinta forte", "Escurecer sozinho" ligado. O "depois" mostra a capa inteira em preto e branco duro (a pintura também), e não muda quando ele troca o filtro.
- ![](a-08-ver-como-fica-tela-cheia.png) "tela cheia": mostra a folha 1 de 199 crua, colorida (sem antes e depois). No canto de cima à esquerda aparece um quadro solto com uma imagem laranja e preta (a origem ainda não foi vista).
- Situação: D-577 **não passou no teste dele**. A causa está em investigação.
- **Causa achada (30/10, na versão de teste):** a prévia supõe sempre "pular as páginas mexidas à mão" (`EstadoDoAutomatico.pedido()` com `pular_mexidas=True`; D-004). No livro de teste, a capa (página 1) e a página 17 estão marcadas como mexidas à mão no filtro (`mexida_a_mao: ['filtro']`, dos testes de 29/10). Então o Automático pula a capa, e o "depois" fica igual ao que já está no livro: a capa em 1 bit do teste da D-588. Prova numa cópia do projeto: na página 1, Preto e branco × Mágico pro dá diferença de 2,1 (de 255) pulando e muda sem pular; na página 3 (não mexida), dá 17,4 (muda). Nas páginas não mexidas a prévia funciona.
- "tela cheia" mostra a folha crua do PDF: foi escolha do construtor ("como antes", TelaCheiaDoPDF), uma das ressalvas dadas a ele.
- Pergunta da gerente: "Minha sugestão: na prévia, a página mexida à mão também mostra como ela fica com as opções escolhidas. Quando você apertar "Rodar", o programa continua perguntando se pula essas páginas. Responda sim ou não."
- Resposta dele (30/10): "ok, então quando for dar o ok, ele vai perguntar se querermos mudar as paginas que foram mudadas a mão. Mas na previa ali, ele mostra a mudança em todas as paginas mas só muda as que nós autorizarmos ( no caso as que foram mexidas a mão), segundo tem que dar para ver na previa em tela grande e poder dar zoom na previa em tela grande, terceiro - essa opção que eu mandei print, quero saber como eu posso marcar e desmarcar ela."
  - 1: a prévia mostra a mudança em todas as páginas, inclusive as mexidas à mão; ao "Rodar", a pergunta da D-004 continua decidindo.
  - 2: o antes e depois da prévia também em tela grande, com zoom (o "tela cheia" hoje mostra a folha crua).
  - 3: ![](a-09-caixinha-molduras-cinza.png) a caixinha "No Preto e branco, molduras e iluminuras também em preto e branco" fica cinza porque "Só as letras" está marcada (D-168: `ui/automatico.py`, `cx_decoracao_pb.setEnabled(not (so_letras and no_pb))`). Desmarcando "Só as letras", ela volta a funcionar.
- Quarta coisa (30/10, palavras dele): "quarta coisa, quando você mexe no antes e depois, ele começa a mostrar o antes de qual pagina, parece que ele troca o antes conforme se troca os perfis dos filtros." Pela D-577, o "antes" é a página como está agora no livro e não muda com as opções. Vai para o construtor investigar e reproduzir.
