# Ordem de serviço da vistoria das gambiarras (26/11/2026)

Colada pelo Samuel no chat da gerente em 26/11/2026, sem mudar nada. É esta a ordem que vale; a gerente não acrescentou
nada a ela. O que a gerente preparou antes do agente começar está no fim.

---

Vistoria das gambiarras — decisão do Samuel, 26/11/2026 (frente 1). Começa agora, pela tela de trabalho.

O QUE É. Um agente NOVO, que só lê e não conserta nada, vistoria o programa e escreve uma lista. Nenhuma linha de código muda. Nada vai para o CLAUDE.md nem para os arquivos dos agentes. Ramo: obra-2026-10-26.

ANTES DE ABRIR O CÓDIGO, ele lê, nesta ordem:
1. Esta ordem de serviço inteira.
2. relatorios/vistoria-gambiarras-2026-11-26/ONDE-PAREI.md (se existir: pedaços feitos, próximo pedaço, rascunho de suspeitas).
3. relatorios/vistoria-gambiarras-2026-11-26/lista.md (se existir: é o modelo de como anotar e mostra as contas que já apareceram).
4. O que já se sabe: relatorios/para-o-fable-2026-11-23/resposta-do-fable.md (Pergunta 2 e Pergunta 5), os 16 remendos do relatorio-para-o-fable.md, e a fila da Central LIDA DA PÁGINA (coleção respostas, itens "pode consertar" / "na fila"; a cópia em docs/plano/central é de 27/10 e está velha). Tudo isso é registro, não prova: cada item é confirmado no código de hoje antes de entrar na lista.

FERRAMENTA PRIMEIRO. Antes do agente começar, gere com um script (AST, sem rodar o programa) a tabela "campo de ConfigPagina/ConfigFolha → todos os lugares de core/ e ui/ que gravam nele", em relatorios/vistoria-gambiarras-2026-11-26/campos.md. É insumo do agente: duas gravações do mesmo campo em lugares diferentes são suspeita obrigatória.

OS CINCO TIPOS que ele procura:
1. A mesma regra ou conta escrita em mais de um lugar, com código diferente.
2. Conta ou regra feita em ui/ que deveria estar em core/ (a tela calcula, decide, ou monta campos de ConfigPagina/ConfigFolha em vez de só mostrar e receber clique).
3. Desvio por caso: "se veio de tal botão / tal lugar, faz diferente".
4. Peça que só existe para proteger outra peça: espera, cadeado, arquivo de marca, segundo caminho "de reserva".
5. Código morto (começando por configuracoes.espaco_livre_mb).

GRAVE / MÉDIO / LEVE — pelo risco de o próximo conserto quebrar algo ao lado:
- GRAVE: a mesma regra em 3 ou mais lugares, OU em peça que o Kaique usa toda hora (girar, dividir, desfazer, conferir/"está certo", filtros, miniaturas).
- MÉDIO: regra em 2 lugares, conta na tela, ou desvio por caso em peça usada de vez em quando.
- LEVE: código morto; peça de proteção que hoje não atrapalha ninguém.

CADA ACHADO É UMA LINHA: onde (arquivo e função) · tipo (1–5) · grave/médio/leve · as outras cópias, se houver · POR QUÊ (o commit e a data em que entrou, pelo git log, e o pedido ou decisão D-xxx que o motivou, pelo Livro; se não achar, escrever "não achei o motivo", nunca inventar) · qual item da Central ele explica, se houver (o id da pergunta) · o que o Kaique perderia se essa peça sumisse hoje.

ORDEM E PEDAÇOS. Primeiro a tela de trabalho (ui/tela_conferir.py e o que ela chama), dividida em pedaços pequenos por assunto: girar · dividir · desfazer · aplicar-em / "o que vai junto" · como-fica (as renderizações) · marcações · contagens e situação da página (conferida, em branco, tirada, avisos) · o resto da tela. Um pedaço de cada vez. Ao terminar um pedaço: grava na lista.md, atualiza o ONDE-PAREI.md (pedaços feitos, próximo, tempo gasto neste pedaço) e só então segue. Ele nunca para no meio de um pedaço.

DOIS DESTINOS. Certeza vai para a lista. Dúvida que ele não consegue confirmar agora (ex.: "esta conta do girar parece existir também no dividir, que ainda não li") vai para a seção "Suspeitas" do ONDE-PAREI, uma linha, na hora em que vê. Quem ler o pedaço seguinte confirma ou descarta. Nada é escrito duas vezes.

CONTEXTO. Você acompanha o consumo do agente. Se apertar, ele termina o pedaço em que está e para; você abre um agente novo com esta mesma ordem de serviço, e ele continua pelo ONDE-PAREI. O que já foi vistoriado não se relê.

ENTREGA DO PRIMEIRO PEDAÇO. Quando o pedaço "girar" estiver gravado, me avise com: o tempo que levou, quantos achados por tipo e gravidade, e o caminho da lista. O Fable lê antes de o agente seguir para o segundo pedaço — mas o agente não espera: continua no pedaço seguinte enquanto a leitura acontece. Depois de cada pedaço, uma linha no chat com o tempo.

A LISTA NÃO FECHA NADA. Nenhum item da Central muda de estado por causa da vistoria. Só o "deu certo" do Samuel, depois de testar um conserto, fecha item. Sem propostas de conserto na lista, sem plano.

Antes de começar: me diga quanto tempo estima para a tela de trabalho inteira e confirme que o agente não vai tocar em código.

---

## O que a gerente preparou (26/11/2026)

- `fila-da-central.md` (nesta pasta): as 37 respostas da coleção `respostas` da Central, lidas da página em 26/11,
  em que "pode consertar" ou "na fila" aparece na opção, no comentário do Samuel ou na resposta da gerente. O agente
  não tem acesso à Central; esta é a cópia lida da página que a ordem pede.
- `campos.md` e `campos_que_gravam.py` (nesta pasta): a tabela da "FERRAMENTA PRIMEIRO", gerada pela AST.
- Os relatórios do Fable ficam na pasta principal do projeto (`D:\programas\EditorImpressao\relatorios\para-o-fable-2026-11-23\`),
  não nesta cópia.
