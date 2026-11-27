# Parte C: a ordem de serviço dos agentes (27/11/2026)

**Em uma frase:** hoje cada pedido a agente é escrito de um jeito; o modelo com lista de arquivos e conferência
automática existiu de 19 a 21/11 e deixou de ser usado; esta parte mostra o que existe, propõe os campos obrigatórios e
duas opções de onde a trava morar, sem construir nada.

Feito pelo agente da triagem, só lendo (D-887). Proposta, não plano de construção. Este arquivo não é a ordem do Samuel
desta triagem (essa é `ordem-de-servico-da-triagem.md`, que não muda).

## 1. Como os pedidos são escritos hoje

### O que as regras mandam pôr no pedido

| desde | o que manda | onde está | situação |
|---|---|---|---|
| 26/10 | as decisões do Livro que tocam o trabalho, com as palavras dele | CLAUDE.md §11.3 e os 4 agentes | é seguido (59 dos 60 ONDE-PAREI criados depois de 27/10 têm "Decisões que esta tarefa precisa cumprir"; falta no da prova à vista do atualizador) |
| 10/11 | pedir sobre a ferramenta inteira e listar todos os lugares (opções, telas, tela grande, tira, PDF) | CLAUDE.md §11.10 | é o "modelo fixo de 10/11" que achei; não existe um documento separado com esse nome (procurei no CLAUDE.md, na memória e no histórico) |
| 10/11 | "não abra outros agentes" em todo pedido | CLAUDE.md §11.11 | seguido; desde 18/11 a ferramenta nem existe (D-793) |
| 13/11 | pôr a regra "sem gambiarra" em todo pedido de conserto | CLAUDE.md §11.12 | seguido como texto colado |
| 09/11 | D-685: "precisamos padronizar isso para quando formos fazer os pedidos, pois estamos fazendo muito retrabalho" | Livro | "não construída"; o Livro diz "mostrar a ele o modelo de pedido aos agentes" |
| 16/11 | D-709: a gerente manda o plano e o guia de leitura; o agente entrega o plano com o porquê do erro | Livro | não está no CLAUDE.md nem nos agentes; falta ele responder se o agente espera o "sim" depois do plano |
| 18/11 | D-784: o pacote (papel, commit de partida, ramo, "Arquivos que vou mexer", as regras pelas etiquetas dos arquivos) | `regras_dos_agentes/pedido.py`, `montar_pacote.py` | construído; usado nos passos 0, 1 e 2 (19 a 21/11); **não achei uso depois** |
| 18/11 | D-792: o formulário único da entrega (F1 a F23) | `regras_dos_agentes/formulario.py` | construído; mesma situação do pacote |

### Exemplos reais (o que o agente copiou do pedido no ONDE-PAREI)

| trabalho | data | como o pedido aparece | o que tinha | o que faltava |
|---|---|---|---|---|
| gravura à mão (D-659) | 09/11 | "O defeito (Samuel, 09/11)", decisões, já escolhido, como fica, plano | as palavras dele, as decisões, o plano antes | lista de arquivos que podem mudar; cópias conhecidas da regra |
| passo 2, publicar | 19 a 21/11 | "Pedido" (papel, partida, ramo) e "Arquivos que vou mexer", depois o formulário inteiro | tudo do pacote; a lista de arquivos; o porteiro conferia | a regra do programa numa frase; o ONDE-PAREI passou de 3.900 linhas |
| atualizador novo, volta 5 | 25/11 | "Antes de mexer (§11.12)", decisões, a tabela das falhas | o porquê, a tabela passos × falhas (pedido do Fable) | "Pedido" e "Arquivos que vou mexer" sumiram: o porteiro de entrega não tinha o que comparar |
| vistoria das gambiarras (D-885) | 26/11 | a ordem do Samuel colada inteira | o que é, o que ler, os tipos, o formato de cada achado, a entrega, o "não toca em código" | "Dentro" e "Fora" como lista que se confere (estava só em prosa) |
| esta triagem (D-887) | 27/11 | a ordem do Samuel e o pedido da gerente | as fontes, as decisões, a pasta onde pode gravar, a entrega | a pasta permitida está só em prosa; nada barra um arquivo fora dela |

**O que se repete nos que deram problema (Parte B):** o pedido diz o defeito, mas não diz **a regra do programa** que o
defeito toca nem **onde ela já está escrita** (E04, E05: a D-662 pedida só no "todas"); a lista de arquivos, quando
existe, não barra (K14 só avisa: E02); a prova que falha antes está nas regras (§4.7), não no pedido.

## 2. O modelo proposto: os campos obrigatórios

Cada campo diz de onde vem e que erro da Parte B ele miraria. Os seis primeiros são os que a ordem do Samuel pede.

| campo | o que vai | quem preenche | miraria |
|---|---|---|---|
| **A regra do programa** | uma frase: o que o programa decide (ex.: "quais páginas giram quando se escolhe um item do 'aplicar em'") | a gerente | E04, E07 |
| **Onde ela deve morar no `core/`** | o arquivo e a função; ou "a decidir no plano, com o porquê" | a gerente (o agente confirma no plano) | E05, E06 |
| **Todas as cópias conhecidas** | os achados da vistoria que tocam essa regra (ex.: G-01 a G-06 para o girar), com arquivo e função | copiado da lista da vistoria | E04, E05 |
| **Dentro** | os arquivos e pastas que podem mudar (o mesmo formato do "Arquivos que vou mexer" de hoje) | a gerente | E02 |
| **Fora** | o que não pode mudar: pastas, telas, decisões que ficam como estão, testes antigos | a gerente | E02, E17 |
| **A prova que falha antes e passa depois** | o nome do teste e o commit de partida onde ele tem de falhar | a gerente diz o que provar; o agente escreve | E10, E11, E12 |
| **O que o Kaique vê** | antes e depois, passo a passo, e o que muda no PDF | a gerente esboça; o agente completa (§11.9) | E01, E18 |
| Cabeçalho | papel, cópia de trabalho, ramo, commit de partida | a gerente | — (é o "Pedido" de hoje) |
| Decisões | número e palavras, copiadas do Livro (a K20 já confere letra por letra) | a gerente | E01, E02 |
| O que já está escolhido e testado | decisões e testes que já existem ali (D-605) | a gerente | E17 |
| Guia de leitura | o que ler antes (D-709) | a gerente | E26 |
| Tamanho da conferência | conferência curta, do tamanho da mudança, ou completa (D-879) | a gerente | — |
| Entrega | o formulário da entrega (F1 a F23) e onde gravar | fixo | E29 |

**Não entra no modelo** o que o Livro ainda não decidiu: se o agente espera o "sim" depois do plano (D-709) e qual
modelo de agente usar por tipo de tarefa (D-710). Vão como dúvida no resumo.

## 3. Como travar (sem construir)

As duas travas que a ordem pede:

1. **Antes de abrir o agente:** um programinha lê a ordem e recusa se faltar um dos campos obrigatórios (ou se o
   "Dentro" estiver vazio, ou se uma decisão citada não bater com o Livro).
2. **Na entrega:** o verificador marca todo arquivo mudado fora do "Dentro". Hoje existe a K14, que compara com a lista
   do pedido, **mas só avisa**; e a K13 barra só pelo papel (ex.: implementador em `ui/`).

### Onde a trava pode morar: duas opções

| | Opção 1: no programa das regras dos agentes | Opção 2: num gancho do Claude Code, antes de abrir o agente |
|---|---|---|
| onde | `regras_dos_agentes/`, ao lado do pacote e do formulário (a leitura do pedido já é uma peça só, `pedido.py`) | `.claude/settings.json` do projeto (não existe hoje), um gancho que roda quando a gerente pede para abrir um agente |
| quem dispara | a gerente roda a conferência antes de abrir o agente; o juiz do GitHub confere de novo na entrega | o próprio Claude Code, sozinho, toda vez que um agente vai ser aberto |
| o que já existe | a lista de arquivos do pedido, a K13, a K14 e os testes delas (`test_conferencias_mudancas.py`) | nada; é peça de fora: antes de usar, ler a documentação dos ganchos do Claude Code (§11.12, ponto 6) |
| a fraqueza | depende de a gerente lembrar: o pacote existiu de 19 a 21/11 e deixou de ser usado sem ninguém decidir | o gancho roda na conversa da gerente; se a ordem for colada no chat (como a da vistoria), ele precisa achar o texto da ordem num arquivo |
| "Fora do Dentro" | a K14 passa de avisar para barrar, na entrega | o mesmo, mais um aviso na hora em que o agente grava fora (gancho depois de mexer em arquivo) |

**Recomendação (minha, para o Samuel e o Fable decidirem):** a conferência mora num lugar só, no programa das regras dos
agentes (opção 1, porque a leitura do pedido e a lista de arquivos já estão lá e já têm teste), e quem a dispara é o
gancho do Claude Code (opção 2), para não depender de a gerente lembrar. Assim são as duas, mas com uma peça só: o
gancho não confere nada sozinho, só chama a conferência. O "Fora do Dentro" passa a barrar na entrega.

## Ressalvas

- **Não achei um documento chamado "modelo fixo de 10/11".** Tratei como modelo de 10/11 o que o CLAUDE.md §11.10 e
  §11.11 mandam pôr em todo pedido desde 10/11. Se havia um texto da gerente com esse nome (num chat ou na Central), não
  está nas fontes que li.
- **"Não achei uso depois de 21/11"** é por leitura dos ONDE-PAREI (as seções "Pedido" e "Arquivos que vou mexer"); não
  rodei o porteiro de entrega para confirmar.
- **O gancho da opção 2 não foi estudado.** Não li a documentação dos ganchos do Claude Code nesta tarefa (a ordem não
  pede construção); se o Samuel escolher essa opção, a leitura vem antes.
- **A ordem das duas últimas tarefas (vistoria e triagem) foi escrita pelo Samuel**, não pela gerente. O modelo proposto
  serve para os dois jeitos; quem preenche cada campo está na tabela.
