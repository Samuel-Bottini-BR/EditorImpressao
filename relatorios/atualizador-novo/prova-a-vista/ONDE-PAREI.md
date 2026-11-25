# Prova à vista do atualizador novo: a preparação (25/11/2026)

Pedido da gerente (25/11/2026): preparar a prova à vista do atualizador novo no PC do Samuel (a gerente pilota, ele
clica "Sim" nas perguntas do Windows). **Só preparar:** montar as versões, escrever o roteiro, conferir o que dá sem a
tela dele. Não começar a prova. Ramo `atualizador-novo-2026-11-23`, a partir de `8e09e193`. Não abri outro agente.
O código do programa não muda (nenhuma linha fora de `relatorios/atualizador-novo/prova-a-vista/`).

**Situação: em andamento.** Ver "Onde estou", no fim.

## Decisões que a prova precisa mostrar (§11.3, copiadas do Livro)

| Decisão | Palavras dele | O que a prova mostra |
|---|---|---|
| D-767 | "não faça mais nada escodindo ou de mentira" | tudo no Windows de verdade, à vista |
| D-773 | (A) "versões de verdade servidas por uma janela visível no PC do Samuel" | as versões são de verdade; **a janela das versões não serve** com o código de hoje (ver "Perguntas") |
| D-785 | (lista do que é sempre à vista: instalar, desinstalar, a pergunta do Windows, a atualização inteira) | todos os passos na tela dele |
| D-733/D-735/D-741 | "1- sim" · "Sim" · "Sim" | a pergunta do Windows na primeira abertura; "Não" → ela volta na abertura seguinte |
| D-806/D-834 | "então pode ser opção A" · "1 – sim (pergunta do Windows antes da senha)" | a pergunta vem logo depois do clique no atalho, antes da janela |
| D-805 | "a" | a pergunta mostra "EditorImpressao.exe" |
| D-729 | "pode" | o Editor antigo de 01/09: **já não está no PC** (conferido em 25/11), então nada a tirar |
| D-838/D-882 | "Na limpeza, desinstala você as duas entradas..." | a limpeza já foi feita hoje; o roteiro só confere o começo |
| D-732 | "não, faz quando o programa é aberto" | procura ao abrir |
| D-724 | (assinatura grátis) | só entra versão assinada pelo Samuel |
| D-715/D-720/D-875 | "ele dá um aviso..." · "Sim" · "As frases do aviso de versão nova ficam como estão." | o aviso "Versão nova do programa", palavra por palavra |
| D-769/D-794/D-831/D-835 | "b" · "...aparecer o aviso para atualizar ou não na hora de fechar..." · "a" · "2 – B (texto curto)" | "Depois" → fechar → "Atualizar agora?" → "Sim" troca; "Não" → o aviso volta na abertura seguinte |
| D-832 | "pode ser velopack, deixamos para mudar isso mais para frente" | a janelinha da troca é a do Velopack |
| D-833/D-788/D-790 | "motor do Kraken tudo ou nada continua" · "1" · "A" | sem o motor no lugar, nada é anunciado |
| D-843 | "vamos fazer b..." | (não provado nesta prova: não há versão com motor novo) |
| D-856/D-857/D-869 | "Versão aprovada no teste rápido ganha uma marca..." · "A primeira versão instalada não tem volta automática..." · "A última boa continua sendo guardada [...] é para a volta manual." | a 1ª versão não baixa nada; depois da 1ª troca boa, a marca e a última boa aparecem, sem internet |
| D-867/D-868 | "a volta automática sai da primeira entrega" · "a frase aparece pela caixa do Windows [...] 'A versão nova não funcionou. Não desinstale nada. Avise o Samuel.' Depois o programa tenta abrir assim mesmo." | a versão quebrada: a caixa do Windows, depois a tentativa de abrir; nada volta sozinho |
| D-859 | "a regra usa o 'pacote esperando'" | sem resposta da fonte e com a versão já baixada, o aviso volta |
| D-778 (2)/D-848 | "A" · "2 — sim, a frase de 18/11." | a versão com a assinatura falsa: a frase (2) |
| D-839/D-877 | "sim" · "Conserta agora só o aviso da segunda recusa do Windows (M1)." | o Windows recusando a troca: a frase, nas duas vezes |
| D-840/D-841/D-845/D-846 | "sim" · "1, desde que seja a volta à fase 'pronta'..." · "ok" | (só se aparecer; não é passo desta prova) |
| D-870/D-873 | "Fica a A." | o atualizador posto de lado: a frase própria, a janela não fecha; de volta, o aviso volta |
| D-842 | "Zero itens abertos antes da prova." | a lista final já foi decidida (D-881) |
| D-881 | "Todos os itens da lista ficam para depois, inclusive o da frase quando a janela não abre." | a caixa "Um momento / Aconteceu um problema inesperado..." depois da versão quebrada é esperada (fica para depois) |

## O que já está escolhido e testado aqui (§11.8)

- Escolhido: tudo o que está na tabela acima. Esta preparação **não muda nenhuma linha do programa**; os scripts novos
  ficam em `relatorios/atualizador-novo/prova-a-vista/` e nenhum entra no pacote (o empacotador só leva o programa).
- Testes que já existem e cobram isso: os 12 arquivos do atualizador e os `tests/test_decisoes*.py` (rodados na volta 5
  e na conferência curta da D-877; o GitHub roda todos). Nenhum muda.

## Como fica para quem usa e no livro (§11.9)

- Para o Kaique: nada muda (a prova é no PC do Samuel, com versões de prova 1.9.x que nunca vão ao GitHub nem a ele).
- Para o Samuel: durante a prova ele vê o programa instalado como o Kaique verá, clica "Sim" ou "Não" nas perguntas do
  Windows quando a gerente pedir. Os projetos dele não são tocados pela preparação (conferido a cada versão montada);
  o programa instalado usa a mesma pasta de dados (`%LOCALAPPDATA%\EditorImpressao`) que o atalho dele, como sempre.
- No livro (PDF): nada muda.

## A lista das falhas desta preparação (§11.12 ponto 3)

| O que pode falhar | O que acontece |
|---|---|
| o C: ficaria com menos de 20 GB | `montar_as_versoes.py` e o publicar param antes, com a frase |
| o publicar de uma versão para no meio | o próprio publicar apaga o rascunho e diz o que ficou; o script para e diz qual registro ler; a cópia de montagem volta ao commit |
| a pasta dos projetos do Samuel muda durante o publicar | o script compara antes e depois (nomes, tamanhos, datas) e para |
| a cópia de montagem não volta ao commit | o script confere (`git status`) e para |
| a assinatura falsa sai aceita | o script confere com a função do programa e para |
| a fonte com índice e arquivos desencontrados | `fonte_da_prova.py` grava o índice por último e confere arquivo por arquivo depois de cada mudança |
| o `segurar-a-pasta` ficar preso | ele sai sozinho no tempo dado (padrão 15 min) ou com `soltar`; ninguém é fechado à força |

## O que rodei antes e o que só roda na prova

(preenchido no fim)

## Perguntas para o Samuel (§11.13; a gerente leva à Central)

(preenchido no fim)

## Onde estou

- 17:40 a cópia de montagem criada (`.claude\worktrees\prova-a-vista-montagem`, destacada em `8e09e193`, com uma cópia
  de `modelos\`, 242 MB, sem junção).
- 17:47 começou a montagem das versões (`montar_as_versoes.py`, por trás).
- 17:53 o ensaio dos scripts A, B e C passou (`ensaio_dos_scripts.py`; registro em
  `C:\EditorImpressaoProva\prova-a-vista-25-11\registros\ensaio-ABC.txt`).
