# Vistoria das gambiarras: o que foi vistoriado e o que ficou de fora (27/11/2026)

**O programa inteiro foi vistoriado, em 11 pedaços grandes, de 26/11 às 15:40 a 27/11 às 16:43 (relógio da máquina).**
Só leitura: nenhuma linha do programa mudou, e ninguém rodou o programa nem os testes; o que depende de uso está escrito
"pela leitura, não rodei". O que ficou sem ler por dentro foi lido só pela lista das funções e pelas buscas, sem cópia
achada; quase sempre é o algoritmo (uma conta só) ou montagem de botões e desenho. O detalhe, com as linhas, está no
`ONDE-PAREI` (cópia em `4-onde-parei`).

## Fora da vistoria, por decisão do Samuel (resposta do Fable, 27/11)

- Os 33 scripts soltos de teste e de régua (na raiz do projeto).
- As regras dos agentes (`regras_dos_agentes/`).
- No atualizador, os tipos 1 a 3 (a mesma regra em mais de um lugar, conta na tela, desvio por caso): "o resto já passou
  por cinco rodadas". Lá só se procuraram peças de proteção e código morto.

## O que ficou sem ler por dentro, em cada pedaço

| pedaço | achados | o que ficou sem ler por dentro |
|---|---|---|
| tela de trabalho (26/11) | 81 | a montagem dos botões e da barra de baixo, o corpo das abas fora do já lido, os encaixes e o rótulo do livro, a "peça" nos pares, o zoom (estes trechos foram lidos depois, no pedaço grande 1) |
| 1. peças da tela | 25 | a coluna de ícones, a sanfona e o painel solto dos painéis; o desenho do visualizador, da tira, da grade e do editor; a folha de estilo; os 123 `getattr` de página e de folha foram contados, não conferidos campo a campo |
| 2. preparar a página | 19 | as contas por dentro do cortar, da caixa do impresso, da borda preta, do endireitar e do desentortar, das guias e das páginas diferentes |
| 3. filtros e limpeza | 20 | as contas de cada filtro (binarizar, sombra da lombada, fundo e ombro, cores), o "Só as letras" por dentro, as camadas, as chamadas das DLLs do ScanTailor |
| 4. gravuras e marcações | 13 | nenhum arquivo de fora; as contas por dentro do detector, lidas como algoritmo |
| 5. Automático e avisos | 22 | as contas do estudo do "Para revisar", os textos de cada aviso (lidos só pelos códigos e botões), o desenho de uma linha da lista |
| 6. abrir, guardar e desfazer | 28 | a tela "O que fazer" (código morto inteiro, AB-01); partes da janela principal (montagem, menu, trocas de tela) e da tela inicial; o servidor de páginas por dentro; a compressão do PDF |
| 7. gerar o PDF e cadernos | 18 | a montagem dos controles da janela "Montar para imprimir"; o desenho e a tela grande das folhas do caderno |
| 8. atualizador (só tipos 4 e 5) | 9 | as contas por dentro das licenças de pasta e do pedido de licença do Windows; os comandos do PowerShell dos testes à distância; a assinatura por dentro |
| 9. achar texto | 8 | a leitura do hOCR do Tesseract; parte do diagnóstico |
| 10. ferramentas do Samuel | 16 | o leitor de DLL do montar do motor; as mensagens do empacotar; o instalador antigo (não é Python) |

Total: 259 achados.

## Ressalvas

- Os pedaços foram rápidos (os grandes, de 6 a 35 minutos cada). O Fable conferiu seis achados da tela no código (G-03, G-06, G-12,
  SP-05, SP-15, DF-01), e os seis bateram; o resto não foi conferido por outra pessoa.
- A régua de gravidade mudou no meio (resposta do Fable, ajuste b): os 81 da tela usam a antiga, os 178 do programa
  inteiro usam a nova.
