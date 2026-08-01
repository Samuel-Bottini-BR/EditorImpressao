---
name: conferir-testes-visuais
description: Use SEMPRE que for julgar o resultado de qualquer teste que produza imagem — detecção de regiões, comparação antes/depois de filtro, máscara, recorte, prévia. Obriga a abrir cada imagem gerada antes de dar veredito, e proíbe concluir a partir de percentuais. Dispara com "testar detector", "comparar filtro", "gerar prints", "ver resultado", "quantas acertou", ou qualquer relatório do tipo "N de N corretas".
---

# Conferir teste visual antes de dizer que funcionou

## Por que esta regra existe

Em 30/07/2026 eu rodei o detector de regiões em dez páginas do acervo, olhei
**uma** imagem, vi que dez percentuais batiam com expectativas que eu mesmo
tinha escrito, e reportei "10 de 10 corretas".

Estavam erradas seis delas. Uma capa de couro lisa marcada como gravura de
página inteira. Uma página inteira de poema com só o título marcado. Uma
partitura tratada como uma grande ilustração. O Samuel abriu os arquivos e
achou tudo em cinco minutos.

O erro não foi de algoritmo. Foi ter julgado por número quando o que estava em
questão era imagem, e ter conferido contra a minha própria expectativa em vez
de contra a página.

## O que fazer

### 1. Abrir todas as imagens. Todas.

Se o teste gerou dez arquivos, leia os dez com a ferramenta Read antes de
escrever qualquer conclusão. Não amostrar. Não "a primeira estava boa, as
outras devem estar".

Se são muitas para abrir uma a uma, gere uma folha de contato com todas juntas
e abra essa — mas alguma imagem de cada caso tem de passar pelos seus olhos.

### 2. A expectativa vem da página, não da sua cabeça

Antes de julgar um caso, olhe o ORIGINAL e descreva o que está ali:

> "página de couro marrom, sem texto e sem gravura, com uma etiqueta no canto"

Só então compare com o que o programa marcou. Escrever `esperado="gravura
alta"` para uma capa em branco e depois confirmar contra isso é confirmar o
próprio engano.

### 3. Veredito por imagem, não agregado

Errado:

> 10 de 10 corretas

Certo:

> 1. capa marrom — 90,7% gravura. ERRADO, a página está vazia.
> 2. Boécio texto — só o título marcado, corpo do poema fora. ERRADO.
> 3. catecismo — gravura no quadro, letra no texto. certo.

Um número agregado esconde exatamente o caso que interessa.

### 4. Percentual não é veredito

`28,9% de gravura` não diz se a área certa foi marcada. Uma página pode ter o
percentual perfeito com a marcação no lugar errado. O percentual serve para
comparar duas versões do mesmo caso, nunca para decidir se um caso está certo.

### 5. Ao reportar, diga quantas você abriu

> "Abri as dez imagens. Seis certas, quatro erradas, listadas abaixo."

Se não abriu todas, diga isso em vez de dar veredito:

> "Gerei dez imagens e abri três. Do que vi, duas certas e uma errada. Falta
> conferir sete."

## O que nunca fazer

- Dizer "funcionou", "está bom", "N de N" sem ter aberto as imagens
- Concluir a partir de percentuais, contagens ou tempo de execução
- Usar expectativa escrita por quem implementou como critério de acerto
- Reportar sucesso quando abriu uma imagem de um conjunto

## Onde guardar, e em que formato

Crie a pasta com `relatorio.pasta_de_teste(assunto, filtro)`:

```
2026-08-01 14h30 - magico pro - contraste local no papel
```

Data e hora ordenam sozinho e deixam comparar duas rodadas do mesmo dia. O
filtro no nome faz achar tudo do Mágico pro junto.

Dentro vai **sempre** um relatório explicando o que foi testado, o que se
esperava e o que aconteceu — gravado com `relatorio.gravar`, que produz `.md`,
`.html` e `.pdf` de uma vez. O Samuel não abre `.md`; gravar só ele é o mesmo
que não entregar.

A pasta precisa se explicar sozinha daqui a seis meses, sem ninguém para
perguntar.

## Vale também para

Comparação antes/depois de filtro, prévia de página, recorte de bordas,
divisão de folha, máscara de seleção, imposição de cadernos — qualquer coisa
cujo resultado uma pessoa julgaria olhando.
