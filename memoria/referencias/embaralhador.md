# Referência: o embaralhador antigo (o primeiro programa de imposição)

Conferido em 20/10/2026. **O plano manda**: itens [2.6](../itens/2.6.md) e [6.5](../itens/6.5.md) do
[PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md).

## Em uma frase

O "embaralhador antigo" é o primeiro programa que o Samuel fez com o Claude, antes do Editor de Impressão: um script
Python (`imposicao_cadernos.py`) que pegava o PDF inteiro e embaralhava as páginas na ordem de caderno, duas por folha.
A conta dele está hoje em `core/cadernos.py`; o que o Samuel quer agora é o livreto em **A4 deitada com duas A5**, com
escala e margens, "como o embaralhador antigo já fazia".

## O que o Samuel disse (literal)

Explicação da impressão, chat de 14/10/2026
([`relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md`](../../relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md)):

> "O livreto o programa monta automático, como o embaralhador antigo (o primeiro que fizemos) já fazia: pegava tudo,
> punha no tamanho livreto e embaralhava sozinho. Quero isso dentro do programa."

E o formato que ele quer escolher na hora de imprimir: "Livreto na horizontal (A4 deitada com duas páginas A5 lado a
lado, embaralhadas na ordem de caderno — imposição)". O resto (escala por lado, margens de 1 cm contadas na A5,
costura 1 cm, "A impressora ainda come mais uns 3 mm na borda.", aviso de margem abaixo de 1 cm) está no mesmo arquivo
e no item 2.6; as opções da janela de imprimir estão em [updf.md](updf.md).

## Onde está o embaralhador

- **A conversa de origem:** [`historico/genesis-conversa-imposicao-cadernos.md`](../../historico/genesis-conversa-imposicao-cadernos.md)
  (1.338 linhas; sem data no arquivo). O pesquisador da impressão achou o embaralhador nas linhas 80 a 620 (ONDE-PAREI
  do ramo `pesquisa-impressao-2026-10-19`, `docs/pesquisa/ONDE-PAREI-impressao.md`).
- **Cuidado:** a mesma conversa continua até uma versão com customtkinter ("Editor e Programador de Impressão.exe"),
  que é a versão velha que **fracassou**. [ESTADO-ATUAL §4](../../docs/plano/ESTADO-ATUAL.md): "`genesis` usam
  customtkinter: **versão velha, ignorar**". Da conversa, só vale a **conta da imposição**.
- **Por que ele é a base:** a especificação original de 18/07/2026 (histórico, APÊNDICE A,
  [resumo](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)) conta: "1. Começou com um script
  Python de imposição de cadernos (`imposicao_cadernos.py`) — a matemática estava correta"; e manda reaproveitar "A
  **matemática da imposição de cadernos** (arquivo `imposicao_cadernos.py`)" e "A **cópia direta de páginas** no modo
  'só cadernos' (não rasteriza)". Etapa 4 da especificação: "`core/cadernos.py` — Imposição. Reaproveitar a lógica do
  `imposicao_cadernos.py` que vou anexar."

## Como ele funcionava (resumo da conversa de origem)

1. O problema que deu origem (primeira linha da conversa, palavras do Samuel): "o que acontece, eu imprimo 4 paginas
   de uma folha a4 ai eu imprimo 5 folhas que da 20 paginas, ai eu fecho elas e da um caderno, do 1 ao 20 fechou mas
   na impressão o 20 sai no outro caderno". Depois: "como imprimir um pdf de 100 paginas com 5 cadernos de 20 paginas
   de uma só vez."
2. O script `imposicao_cadernos.py` (PyPDF2): `calcular_imposicao(n)` dá, para a folha *i* de um caderno de *n*
   páginas, frente `[n − 2i] [1 + 2i]` e verso `[2 + 2i] [n − 1 − 2i]` (caderno de 20: 20-1 / 2-19, 18-3 / 4-17 ...).
   Cadernos de 20 páginas de fábrica (`--paginas-por-caderno`, múltiplo de 4); completa o último caderno com páginas
   em branco.
3. Primeiro saía com as páginas soltas reordenadas (para imprimir "2 por folha"). O Samuel achou que a ordem estava
   errada: "Eu que você revise, por que a ordem não está certa para fazer um livreto". A ordem estava certa; o problema
   era o modo de imprimir. Então o programa passou a **montar as duas páginas lado a lado** numa folha em paisagem
   (`criar_pagina_dupla`): "O PDF já sai com as páginas montadas lado a lado (2-up em paisagem) ... NÃO use Livreto ...
   Frente e verso → virar na borda curta".
4. Virou app de navegador (HTML, também no celular), depois app Windows, e depois ganhou filtros (amarelado, alinhar)
   em versões com customtkinter, que travavam. Daí nasceu o Editor de Impressão.

## O que existe hoje no programa (`core/cadernos.py`)

[`core/cadernos.py`](../../core/cadernos.py) (256 linhas) tem a mesma conta, na docstring do topo:
"frente da folha i: [ N - 2i ] [ 1 + 2i ] / verso da folha i: [ 2 + 2i ] [ N - 1 - 2i ]". Fábrica: 20 páginas por
caderno (`PAGINAS_POR_CADERNO_PADRAO`), arredondado para múltiplo de 4. Funções: `ordem_do_caderno`, `montar_ordem`,
`impor_pdf`, `conferir_sequencia` (simula a dobra; "Feito em 06/08" para a queixa do Kaique "como ter certeza que os
cadernos estão na sequência correta sem olhar folha por folha?", histórico, PARTE 3) e `instrucoes_de_impressao`
("Imprima frente e verso, virando na borda curta.").

**Diferença para o que o Samuel pediu em 14/10:** o `impor_pdf` de hoje faz cada folha com **o dobro da largura da
maior página do livro** (`largura * 2` × `altura`), sem papel-alvo, sem escala e sem margens. O pedido é escolher o
papel (A4 deitada com duas A5, ou A4 em pé, ou as outras opções da janela do UPDF), a escala (um lado ou os dois) e as
margens (1 cm na A5, costura 1 cm, 1,3 cm da beirada do papel). Decisões já tomadas: Registro 14/10/2026 (`g10`,
`g11`, `g12`; ver [updf.md](updf.md)).

Bug aberto ligado: "depois de 'Voltar para as opções' num livro já trabalhado, marcar 'Montar cadernos' é ignorado sem
aviso" (Lista de bugs, 05/10/2026; [bugs](../bugs.md)).

## Itens do plano que tocam nele

- [2.6](../itens/2.6.md) "Tamanho final da página em cm/mm": a explicação de 14/10 está anotada nele (livreto "com
  imposição automática como o embaralhador antigo").
- [6.5](../itens/6.5.md) "Cadernos: caminho rápido, marca de alceamento, numeração".
- [2.4](../itens/2.4.md) (margens) e o 6.6 (chapas vermelho/preto) entram na pesquisa da impressão.

## Quem está trabalhando nele hoje

Ramo `pesquisa-impressao-2026-10-19` (pesquisador; worktree `.claude/worktrees/pesquisa-impressao`), só documentos em
`docs/pesquisa/`. ONDE-PAREI de 19-20/10: feito, ler o pedido e achar o embaralhador ("é o `imposicao_cadernos.py`
(PyPDF2) da conversa de origem ... A mesma conta vive hoje em `core/cadernos.py`"); falta pesquisar cada opção do UPDF
e como fazer com PyMuPDF, escrever `docs/pesquisa/fase-impressao.md` nos três formatos e entregar à gerente. Ver
[ramos](../ramos.md).
