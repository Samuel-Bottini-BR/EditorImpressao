# Teste de velocidade: SAMUEL-PC

Medido em 29/09/2026 às 00:07, no computador SAMUEL-PC. Livro: marial_300.pdf (300 páginas, 67,9 MB). O teste inteiro levou 12 minutos e 20 segundos.

## Quanto demora

Cada coisa foi medida 3 vezes. **Na primeira vez** é o que o Kaique sente ao abrir um livro pela primeira vez. **De costume** é o valor do meio entre as 3 vezes (a mediana): não é puxado nem pela vez mais rápida nem pela mais lenta.

- **Abrir o livro de 300 páginas:** 38,4 segundos na primeira vez, 38,6 segundos de costume.
- **Trocar de página:** na primeira vez, a prévia de uma página nunca vista ficou pronta em 2,5 segundos em média, e a mais demorada (página 143) levou 3,3 segundos. De costume: 2,3 segundos em média, e 2,8 segundos a mais demorada.
- **Processar 10 páginas em Mágico pro:** 1 minuto e 16 segundos na primeira vez (7,6 segundos por página), 1 minuto e 15 segundos de costume (7,5 segundos por página).
- **Processar 10 páginas em Preto e branco:** 35,9 segundos na primeira vez (3,6 segundos por página), 35,7 segundos de costume (3,6 segundos por página).
- **Memória máxima usada:** 1.601 MB, ao processar em Mágico pro (rodada 2).

## A máquina

| O quê | Nesta máquina |
|---|---|
| Computador | SAMUEL-PC |
| Processador | AMD Ryzen 7 5800H with Radeon Graphics |
| Núcleos | 8 físicos, 16 lógicos |
| Memória (RAM) | 16 GB (15,4 GB disponíveis para o Windows) |
| Placa de vídeo | AMD Radeon(TM) Graphics; NVIDIA GeForce GTX 1650 |
| Windows | Windows 11 Home Single Language 25H2 (compilação 26200.9457) |
| Energia | na tomada (bateria em 100%) |
| Disco do livro | HD externo (USB) |
| Data e hora | 29/09/2026 00:07 |

## Rodada a rodada

| O que | 1ª rodada | 2ª rodada | 3ª rodada | De costume |
|---|---|---|---|---|
| Abrir o livro | 38,4 s | 39,0 s | 38,6 s | 38,6 s |
| Abrir o livro: só o arquivo | 0,02 s | 0,02 s | 0,02 s | 0,02 s |
| Abrir o livro: olhar todas as folhas | 38,4 s | 39,0 s | 38,5 s | 38,5 s |
| Trocar de página: média | 2,5 s | 2,3 s | 2,3 s | 2,3 s |
| Trocar de página: a mais demorada | 3,3 s | 2,8 s | 2,8 s | 2,8 s |
| Processar 10 páginas em Mágico pro | 1 min 16 s | 1 min 15 s | 1 min 15 s | 1 min 15 s |
| Processar 10 páginas em Preto e branco | 35,9 s | 35,5 s | 35,7 s | 35,7 s |
| Memória máxima até o fim da rodada | 1.594 MB | 1.601 MB | 1.601 MB | - |

Os números crus (cada troca de página, cada etapa, a memória depois de cada etapa) estão no arquivo .json de mesmo nome.

## Como foi medido

Tudo pelas mesmas funções que o programa usa, na mesma ordem, sem abrir janela.

- **Abrir o livro** = `abrir_pdf` + `info_paginas` + `assinatura_do_arquivo` (o que `JanelaPrincipal.abrir_livro` faz com o arquivo escolhido) e depois `TarefaAnalise.run`, que chama `analisar_projeto`: a análise de todas as folhas (lombada, ângulo, bordas, cor e alertas), a 150 DPI. Opções: as que a tela "O que fazer" já traz marcadas (dividir, limpar, endireitar, cortar as bordas), com o filtro Mágico pro. Fica de fora o tempo em que o Kaique está na tela "O que fazer", e gravar o projeto na lista de projetos (o teste não mexe na lista do programa).
- **Trocar de página** = `GerenciadorPrevias.pegar` + `pre_carregar`, as duas chamadas que a tela de conferir faz ao virar a página (`TelaConferir._atualizar_previa`), com o mesmo adiantamento das 3 páginas seguintes, na qualidade de prévia "Rápida" (110 DPI, a padrão). Cada prévia passa por `renderizar_pagina`: ler a folha, cortar, endireitar, achar gravura e letra e aplicar o Mágico pro. O tempo vai do pedido até a prévia ficar pronta. Entre uma troca e outra o teste espera o programa terminar de adiantar as páginas seguintes, como o Kaique, que olha a página antes de passar. Páginas: 8, 23, 38, 53, 68, 83, 98, 113, 128, 143, 158, 173, 188, 203, 218, 233, 248, 263, 278 e 293.
- **Processar** = `TarefaProcessar.run`, que chama `processar` (o botão "Confirmar e processar"): dividir, cortar, endireitar, achar gravura e letra, filtro e gravar o PDF, a 300 DPI, nas páginas 146 a 155 (as do meio do livro). As outras páginas ficam marcadas como apagadas, que é como o programa deixa uma página de fora. O PDF sai numa pasta temporária, apagada no fim.
- **Memória** = o maior uso de memória do processo do teste, medido pelo próprio Windows. Não conta a tela do programa.
- **Detector de gravura e letra** (modelo doclayout.onnx): carregado.
- **Antes de medir**, o teste faz o mesmo aquecimento que o programa faz ao ligar (`aquecer_dependencias_pesadas`): levou 0,9 segundo, e não entra nos tempos acima.
- **Janela preta:** o teste rodou sem janela preta nenhuma. Não havia o que desligar: o teste não recebia o teclado de uma janela preta (foi chamado por outro programa, por exemplo), e o modo de edição rápida ficou como estava.

## O que este teste não mede

- A tela desenhando: a faixa de miniaturas (que roda em segundo plano logo depois de abrir o livro e disputa o leitor de PDF com as primeiras prévias), os cartões de filtro e o desenho da prévia. "Trocar de página" é o tempo até a prévia ficar pronta, não até ela aparecer pintada.
- A aba "Onde cortar", que mostra a folha crua, sem processamento, e é bem mais rápida.
- Disco frio de verdade: se o livro acabou de ser copiado para o computador, o Windows pode já tê-lo na memória, e a primeira vez sai mais rápida do que ao abrir um livro parado no disco há dias.

## Versões

Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1 · onnxruntime 1.28.0 · PySide6 6.11.1 · rodando pelo Python · teste de velocidade versão 1
