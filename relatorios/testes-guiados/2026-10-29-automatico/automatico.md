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

## Causa do a-2 (lida no código da versão de teste, `obra-2026-10-26`)

Não é a página que deixa de mudar: o processamento está certo (o "antes / depois" mostra o Preto e branco). O que
acontece é que a vista da página (a mesma para o Zoom, a Mão e as ferramentas de marcar: `FERRAMENTAS_DE_NAVEGACAO` em
`ui/widgets/editor_selecao.py:95` são ferramentas do mesmo editor) pinta **sempre** toda a marcação da
página por cima da imagem, cada tipo numa cor (`ui/widgets/editor_selecao.py`, `_pintar_marcacao`, cores nas linhas
193-199: letra azul, gravura salmão, papel verde). Depois que o Automático roda a etapa de gravuras e fotos, a página
inteira fica marcada, e a imagem some debaixo das cores. A caixinha "Mostrar as áreas achadas" (D-237) só liga o
contorno laranja; não esconde o colorido. Então o conserto do a-2 e o "jeito de aparecer e desaparecer" são a mesma
coisa: um botão que mostra e esconde o colorido das marcações.
