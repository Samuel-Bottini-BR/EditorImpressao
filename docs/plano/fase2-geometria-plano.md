# Fase 2, frente de geometria: plano curto (proposta do implementador, 05/10/2026)

**Não é decisão.** É a ordem e as perguntas para a gerente levar ao Samuel. Nada destes itens foi implementado.
Base: `docs/pesquisa/fase2-mapa-scantailor.md` (seções 4 e 6.1–6.6), a comparação D3 (`relatorios/fase2-geometria-d3-2026-10-05/`) e a decisão D2 (zonas na folha original, ramo `fase2-geometria`).

## Já feito nesta frente (05/10)

- **D3:** comparação nosso × ScanTailor (girar, dividir, endireitar) nas páginas-gabarito. Resumo: girar não tem automático em nenhum dos dois; no endireitar empatam em 25 de 32 páginas, cada um ganha 2 das outras; no dividir os dois erram (o nosso parte a folha do Siebmacher no meio; o ScanTailor divide a tabela do Opus 256 e o "corte da sobra" dele come letra).
- **D2:** as zonas da aba Marcar ficam presas à folha original (`core/zonas_na_folha.py`). **Pendência que trava os itens abaixo:** página de projeto antigo só é convertida quando é desenhada. Antes de qualquer item que mude o corte ou o ângulo **automático** (2.1, 2.2, 2.5, 2.13), as páginas ainda no formato antigo precisam ser convertidas com a conta de hoje (guardar uma cópia da conta atual, `pipeline._geometria`, só para isso), senão as zonas delas andam.

## A ordem (a do ScanTailor; cada etapa usa a anterior)

| # | Item | Só `core/` (sem pergunta) | Exige mudar tela (pergunta ao Samuel) |
|---|---|---|---|
| 1 | **2.3 Girar** | Nada a trazer em C (o ScanTailor também é só à mão). Conferir que girar refaz dividir, corte, endireitar e leva as zonas (já acontece pela chave da geometria e pelo D2): só teste. | Botões e "aplicar em". Pergunta G1. |
| 2 | **2.1 Dividir** | Função do ScanTailor na DLL comum (`estimatePageLayout`, três modos: uma página / uma página + sobra / duas páginas), chamada pelo Python; o resultado vira `ConfigFolha.dividir` + `posicao_corte`. | Escolha por livro e por página, e o padrão. Perguntas G2 e G3. |
| 3 | **2.2 Endireitar** | Função do ScanTailor na DLL (`SkewFinder` + a limpeza das sombras), com a imagem e o DPI certos (no D3 o ângulo dele mudou até 0,5° com a resolução). Bug da Lista que entra: "páginas endireitadas ficam com menos de 1 mm nos cantos". | Tela da aba Endireitar e a ordem do processamento. Perguntas G4, G5 e G6. |
| 4 | **2.13 Página dentro da borda preta** | `PageFinder` na DLL, como opção por livro (desligada de fábrica, como no ScanTailor). Precisa de páginas com borda preta no gabarito (o Siebmacher tem fundo preto à direita). | Uma caixinha por livro. Pergunta G7. |
| 5 | **2.5 Caixa do conteúdo e guias** | `ContentBoxFinder` na DLL, como **opção** ("seguir a moldura/o papel"), sem trocar o corte de fábrica aprovado em 01/10. Bugs da Lista que entram: "Cvii" do Graduale 221, aviso "encostou no conteúdo" calculado a 150 DPI. | Opção e guias na aba Bordas (e o bug "aba Bordas mostra a folha inteira"). Pergunta G8. |
| 6 | **2.4 Margens iguais + alinhamento** | As contas do ScanTailor (maior conteúdo do livro + margens em mm + alinhamento) e uma passada no livro inteiro. | Margens, alinhamento, pares/ímpares. Pergunta G9. |
| 7 | **2.6 Tamanho final** | Manter o nosso (A4/A5/Carta, `core/folha.py`), recebendo a conta do 2.4. | Só se mudar o que acontece quando não cabe. Pergunta G10. |

**Antes de começar o 1:** combinar com a frente do modo Misto a **DLL comum** (`st_ferramentas`, seção 4.2 do mapa): as funções de geometria entram na mesma DLL, compilada uma vez, e o teste "copiado sem mudança" vale para as duas frentes.

## Perguntas exatas ao Samuel

**G1 — Girar (2.3).** "No ScanTailor, girar é botão: girar à esquerda, à direita, e 'aplicar em: só esta / todas / daqui em diante / pares / ímpares'. Como você quer?"
(a) igual ao ScanTailor; (b) o botão de hoje e só acrescentar "pares / ímpares"; (c) outra coisa (dizer o quê). Observação: hoje a tecla R serve para girar e para o Retângulo, e o Retângulo ganha (Lista de bugs, 02/10).

**G2 — Dividir, o padrão de um livro novo (2.1).** "No teste, o automático do ScanTailor dividiu toda folha deitada: partiu em duas a tabela dobrável do Opus Majus 256 e, no Siebmacher, deixou uma 'página' só com a beirada do livro. O nosso partiu o Siebmacher no meio do poema. O que o programa faz num livro novo?"
(a) **uma página por folha**, e a pessoa marca "este livro tem duas páginas por folha"; (b) o automático do ScanTailor, com toda folha dividida saindo "conferir"; (c) o nosso de hoje (procura a lombada nas folhas deitadas).

**G3 — "Corte da sobra" (2.1).** "O ScanTailor tem um modo 'uma página + sobra' que corta a beirada da folha vizinha. No teste ele cortou letra na Escola 7 e na Escola 35 e levou o 'Cvij' do Graduale 221. Trazer?"
(a) não trazer; (b) trazer como opção, desligada; (c) trazer ligado.

**G4 — Endireitar, qual conta (2.2).** "No teste, o do ScanTailor acertou a Horas 11 e a Horas 47, que o nosso erra, mas errou a Horas 27 e a Palatino 57, que o nosso acerta; nas outras 25 páginas dá igual. Você disse 'quero usar o do scantailor'. Confirma?"
(a) só o do ScanTailor; (b) o do ScanTailor de fábrica, e quando os dois discordarem mais de 0,3° a página sai "conferir"; (c) manter o nosso e só mudar a tela.

**G5 — Tela do endireitar (2.2).** "Hoje a aba Endireitar gira arrastando em qualquer lugar, sem pista visual (Lista de bugs, 02/10). No ScanTailor: grade sobre a página, o ângulo em número com setas de 0,1°, e 'aplicar em'. Como quer?"
(a) como o ScanTailor; (b) o arrastar de hoje + o número com setas; (c) outra.

**G6 — Ordem do processamento (2.2).** "O `CLAUDE.md` manda cortar antes de endireitar; o ScanTailor endireita antes de achar o corte (no teste isso explica parte das diferenças). Trazer o endireitar dele muda essa regra?"
(a) sim, passa a ser girar → dividir → endireitar → cortar (como o ScanTailor; o corte de todas as páginas muda um pouco e vai ter de ser reconferido); (b) não, manter cortar → endireitar.

**G7 — Borda preta do scanner (2.13).** "Quer a opção 'achar a página dentro da borda preta' por livro, desligada de fábrica? Quais livros do acervo têm borda preta para entrar no gabarito?"
(a) sim, desligada, gabarito com o Siebmacher (fundo preto à direita) e o que mais você indicar; (b) não trazer agora.

**G8 — Caixa do conteúdo (2.5).** "O corte de fábrica (pela tinta, com 1 mm de folga) foi aprovado em 01/10. O do ScanTailor segue a moldura e o papel, mas no teste do pesquisador deixou de fora a moldura dourada da Horas 13."
(a) trazer como opção "seguir a moldura/o papel", desligada; (b) trocar o corte de fábrica; (c) não trazer.

**G9 — Margens (2.4).** "No ScanTailor, cada página ganha margens em mm (de fábrica 10 mm dos lados e 5 mm em cima e embaixo), todas ficam do tamanho da maior do livro, e dá para pôr margens diferentes nas pares e ímpares (para a costura, R3). Quais margens de fábrica?"
(a) as do ScanTailor; (b) outras (dizer quanto: dentro / fora / cima / baixo); e (c) igualar todas ao tamanho da maior: sim ou não.

**G10 — Quando não cabe na folha (2.6).** "Se o conteúdo mais as margens passarem do A4, hoje o programa não reduz. O que fazer?"
(a) reduzir até caber; (b) avisar e não reduzir; (c) cortar as margens até caber.

## O que fica para depois (fora desta frente)

2.15 páginas diferentes (precisa dos números do 2.2, 2.5, 2.4), 2.12 desentortar (depois da geometria estável), 2.16 todos os núcleos (decisão sobre a memória), 2.10 duas camadas (com o 1.6), 2.19 unidades/perfis/tema.
