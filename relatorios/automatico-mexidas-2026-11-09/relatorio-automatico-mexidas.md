# Automático e páginas mexidas: o aviso pergunta quando deve?

Verificador, 09/11/2026. Teste de **máquina** (não precisa de olho). Ramo `obra-2026-10-26`
(cópia `obra-juncao`). Nenhuma janela abriu na tela: tudo rodou com a janela principal escondida
(offscreen). Nenhuma linha do programa foi mudada.

## Em poucas palavras

- **Mexida à mão: o aviso funciona.** Filtro (também o Preto e branco escolhido à mão), cortar,
  endireitar e dividir: o Automático com aquela etapa pergunta "1 página foi mexida à mão...",
  "Pular" deixa a página como estava (igual no PDF, ponto por ponto) e "Rodar nelas também" passa
  por cima. Com a etapa desmarcada, não pergunta e o que foi feito à mão fica.
- **Marcar, mover e girar à mão nunca entram no aviso**, mas também não se perdem: o Automático
  não tem etapa que passe por cima deles (a marcação à mão, o tamanho e lugar do conteúdo e o giro
  ficaram iguais em todas as rodadas). Uma ressalva no girar, abaixo.
- **O caso do Samuel funciona:** filtro em 3 páginas, depois só "Montar cadernos" no livro todo
  → não pergunta nada, as 3 páginas continuam com o filtro, os cadernos saem com todas as
  páginas na ordem certa, sem erro. Também no livro de verdade (Boécio, 50 páginas).
- **Rodada do Automático por cima de outra rodada: hoje não pergunta.** Filtro em 3 páginas e
  depois outro filtro no livro todo → as 3 páginas trocam de filtro sem aviso. Pela D-660 (nova,
  09/11) ele deveria perguntar: **errado pela D-660 (ainda não construída)**.
- **Cuidado (sem decisão escrita):** depois da rodada em 3 páginas, ao voltar ao Automático a
  caixinha "Limpar a folha" já vem marcada. Se só se marcar "Montar cadernos" e rodar no livro
  todo, o filtro vai para as 24 páginas, sem perguntar.
- Os testes que já existiam do aviso: **16 de 16 passaram**.

## Como foi testado

Pelo caminho de verdade: a janela principal do programa (escondida), o livro aberto como o
Kaique abre, as mexidas feitas pelos mesmos comandos que os botões da área de trabalho chamam,
o painel do Automático com as etapas marcadas e o "Rodar". Só a caixa da pergunta foi trocada
por uma resposta fixa ("Pular" ou "Rodar nelas também"), como os testes do programa já fazem; o
texto anotado é o que a caixa mostraria. No fim, o PDF foi gerado como o "Confirmar e processar"
grava. O filtro de cada página foi conferido **no PDF** (comparando com o mesmo livro gerado
todo em cada filtro), e a ordem dos cadernos lendo o número de cada página impresso nela.
Erros: o `erros.log` da rodada (pasta de dados separada) e qualquer erro inesperado.

Livros: um livro de teste feito para isso (24 páginas, cada uma com o seu número em
quadradinhos; e um de 4 folhas para o caso 1) e o **Boécio** do acervo (50 páginas, só lido).

Script: `relatorios/automatico-mexidas-2026-11-09/test_verificador_mexidas.py` (36 casos;
todos passaram). O que cada caso viu, em detalhe: `resultados.json`, na mesma pasta.

## Caso 1: mudança à mão, uma etapa por vez

O que se esperava (D-004, 28/09: "Automático em livro já mexido à mão: o programa pergunta se
quer pular as páginas mexidas."; D-485: o filtro escolhido à mão conta): com a etapa mexida
marcada, pergunta; "Pular" mantém; etapa desmarcada, não pergunta e a página fica.

| Mexida à mão | Automático com | Perguntou? | "Pular" | "Rodar nelas também" | Etapa desmarcada | Páginas do PDF / erros |
|---|---|---|---|---|---|---|
| Filtro (Melhorar à mão) | Limpar em Preto e branco | sim, 1 página(s) | ficou (página igual no PDF) | passou por cima | Endireitar + Cortar: não perguntou, o Melhorar ficou | 4 / vazio |
| Preto e branco à mão (e força do preto) | Limpar em Melhorar | sim, 1 página(s) | ficou (página igual no PDF) | passou por cima | Endireitar + Cortar: não perguntou, o Preto e branco ficou | 4 / vazio |
| Cortar (corte à mão) | Cortar as bordas | sim, 1 página(s) | ficou (página igual no PDF) | passou por cima | Endireitar + Limpar: não perguntou, o corte ficou | 4 / vazio |
| Endireitar (1,5 grau à mão) | Endireitar | sim, 1 página(s) | ficou (página igual no PDF) | passou por cima | Cortar + Limpar: não perguntou, o ângulo ficou | 4 / vazio |
| Dividir (linha posta à mão) | Dividir | sim, 2 página(s) | ficou (página igual no PDF) | passou por cima | Endireitar + Cortar + Limpar: não perguntou, a linha ficou | 5 / vazio |
| Marcar (gravura marcada à mão) | Limpar + Gravuras e fotos | não | ficou | ficou (não há o que passar por cima) | Endireitar + Cortar: não perguntou, a marcação ficou | 4 / vazio |
| Mover (conteúdo em 80%) | Margens iguais | não | ficou | ficou (não há o que passar por cima) | Endireitar + Cortar + Limpar: não perguntou, o tamanho ficou | 4 / vazio |
| Girar (1/4 à direita) | Dividir + Endireitar + Cortar + Limpar | não | ficou | ficou (não há o que passar por cima) | só Montar cadernos: não perguntou, o giro ficou | 6 / vazio |

Notas:

- "Rodar nelas também" (filtro, cortar, endireitar, dividir): o valor à mão sai e a marca de
  mexida também; o Automático passa a valer na página. Dividir: as 2 páginas da folha dividida à
  mão contam (pergunta "2 páginas"); com "Pular" a linha fica em 0,47, com "Rodar" o programa põe
  a dele.
- Marcar, mover e girar: **não perguntam**, mesmo com "Rodar nelas também" não há nada a passar
  por cima: a gravura marcada à mão, o conteúdo em 80% e o giro ficaram. No Livro não há decisão
  dizendo que essas três devem entrar no aviso (o código conta só dividir, endireitar, cortar e
  filtro). **Certo** pelo que está escrito.
- **Ressalva do girar (sem decisão escrita):** o giro não entra no aviso do Dividir. Página que
  veio deitada no PDF e foi posta em pé à mão: o Dividir **não** a partiu (1
  página, certo). Mas uma página em pé que a pessoa deitou à mão (fica larga, como uma folha
  aberta) foi partida em 2 pelo Dividir, sem perguntar. É um caso raro
  (não há motivo para deitar uma página em pé), por isso só fica anotado. É por isso que a linha
  "Girar" da tabela tem 6 páginas no PDF (a folha dupla e a página deitada, as duas partidas).

Veredito do caso 1: **certo** (D-004, D-485).

## Caso 2: o caso do Samuel

Automático só nas páginas 4, 8 e 12, só com "Limpar a folha" em Preto e branco. Depois,
Automático no livro todo só com "Montar cadernos".

O que se esperava (D-589: o que não está marcado não é feito; D-660: "Rodar no livro todo só o
'Montar cadernos', depois de um filtro em algumas páginas, funciona sem erro e não mexe no filtro
delas"): sem pergunta, as 3 páginas com o filtro, cadernos certos, sem erro.

O que aconteceu:

- Primeira rodada: não perguntou (nada mexido à mão).
- Ao voltar ao Automático: a caixinha "Limpar a folha" vem marcada ("ligada em 3 páginas").
- Segunda rodada (só "Montar cadernos"): não perguntou.
- Filtro no PDF: todas em Original menos pág. 4: Preto e branco, pág. 8: Preto e branco, pág. 12: Preto e branco.
- Cadernos: 12 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só (24 páginas em cadernos de 20: um de 20 e um de 4).
- erros.log vazio, nenhum erro.
- Livro de verdade (Boécio, 50 páginas, o mesmo caminho): não perguntou;
  as páginas 4, 8 e 12 continuam em Preto e branco e as outras no Original (filtro que vale em cada página do projeto); 26 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só
  (cadernos de 20, 20 e 12; a ordem conferida achando cada metade entre as páginas do PDF);
  erros.log vazio, nenhum erro.

Veredito do caso 2: **certo** (D-589, D-660).

### Variação 2b: sem desmarcar o "Limpar a folha" que voltou marcado

Se depois da primeira rodada a pessoa só marca "Montar cadernos" (o "Limpar a folha" já estava
marcado) e roda no livro todo: não perguntou; filtro no PDF: todas em Preto e branco;
12 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só; erros.log vazio, nenhum erro.

Não estraga as 3 páginas (continuam em Preto e branco), mas o filtro vai para o livro inteiro sem
aviso. Isso depende da pergunta ainda aberta das caixinhas depois de rodar (D-628,
`n0411-caixinhas-depois-de-rodar`; Samuel, 04/11: "elas tem que voltar todas desmarcadas"):
**sem decisão escrita** até essa resposta.

## Caso 3: a segunda rodada tem outro filtro

O mesmo do caso 2, só que a segunda rodada no livro todo tem "Limpar a folha" em Melhorar +
"Montar cadernos".

O que se esperava: D-660 (Samuel, 09/11: "mas caso o o automatico for mudar alguma coisa que foi
feito na ultima rodada ele deve perguntar."): perguntar antes de trocar o filtro das 3 páginas, e
"Pular" as manter.

O que aconteceu: não perguntou. Filtro no PDF: todas em Melhorar: as páginas 4, 8
e 12 perderam o Preto e branco. 12 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só. erros.log vazio, nenhum erro.

Veredito do caso 3: **errado pela D-660 (ainda não construída)**. Funciona sem erro, mas troca o
filtro da rodada anterior sem perguntar.

Por que (no código): a contagem do aviso (`core/automatico.paginas_mexidas`) só conta a marca de
mexida à mão; a página em que o Automático rodou só nela (`ConfigPagina.automatico`) é tirada da
conta de propósito (`_filtro_trocado_na_pagina`). Para reproduzir: abrir um livro, Automático
"nas escolhidas" (3 páginas) só com "Limpar a folha" em Preto e branco, "Rodar"; depois
Automático "no livro todo" com "Limpar a folha" em Melhorar, "Rodar" → nenhuma caixa aparece e as
3 páginas saem em Melhorar.

## Caso 4: mistura

Uma página mexida à mão (Mágico pro escolhido à mão) + as 3 páginas da primeira rodada (Preto e
branco) + segunda rodada no livro todo com "Limpar a folha" em Melhorar + "Montar cadernos".

O que se esperava: D-004 pergunta da página mexida à mão; D-660 também das 3 da rodada anterior
(contagem 4).

| Como | Perguntou | "Pular" | "Rodar nelas também" |
|---|---|---|---|
| página 6 mexida à mão antes da 1ª rodada | 1 página | todas em Melhorar menos pág. 6: Mágico pro | todas em Melhorar |
| página 8 (uma das 3) mexida à mão depois da 1ª rodada | 1 página | todas em Melhorar menos pág. 8: Mágico pro | todas em Melhorar |
| Boécio, página 6 à mão | 1 página | página 6 em Mágico pro, as outras em Melhorar (no projeto) | (não rodado) |

Cadernos: em todos, 12 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só; no Boécio, 26 lados de folha no PDF dos cadernos, na ordem certa da dobra, todas as páginas uma vez só.
Erros: nenhum (erros.log vazio em todos).

Veredito do caso 4: a parte da mão está **certa** (D-004: conta 1, "Pular" mantém o Mágico pro,
"Rodar" passa por cima). A parte da rodada anterior está **errada pela D-660 (ainda não
construída)**: a contagem é 1, não 4, e as páginas 4, 8 e 12 vão para Melhorar mesmo com
"Pular". A página 8 mexida à mão depois da rodada conta como mexida (certo).

## Caso 5: os testes que já existiam

`pytest tests/test_decisoes_automatico.py tests/test_decisoes.py
tests/test_automatico_pular_depois_de_dividir.py -q -k "d004 or mexid or pular or d607"`:
**16 passaram**, 44 de fora pelo filtro (como a gerente viu).

## Resumo dos vereditos

- Caso 1 (à mão, uma etapa por vez): **certo**. Marcar, mover e girar não entram no aviso e não
  se perdem; ressalva do girar + Dividir anotada (sem decisão escrita).
- Caso 2 (filtro em 3 páginas, depois só cadernos): **certo**, também no Boécio.
- Variação 2b ("Limpar" volta marcado e vai para o livro todo): **sem decisão escrita** (espera a
  pergunta das caixinhas, D-628).
- Caso 3 (outro filtro na segunda rodada): **errado pela D-660 (ainda não construída)**.
- Caso 4 (mistura): mão **certo**; rodada anterior **errado pela D-660 (ainda não construída)**.
- Caso 5: **16 de 16 passaram**.
- Nenhum erro, nenhum `erros.log`, nenhum PDF com página a mais ou a menos, cadernos sempre na
  ordem da dobra.
