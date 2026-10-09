# Rodada 5 do "Para revisar": respostas do Samuel (literais)

Lidas da coleção `respostas` da página "Quando revisar uma página" (https://claude.ai/artifact/NeCgyTotRfqsdXntn9vMUc) em 09/10/2026, depois do aviso dele "respondi tudo". Três foram respondidas em 08/10 entre 01:30 e 01:32 e sete em 09/10 entre 15:52 e 15:57 (horário de Brasília). Texto dos comentários sem alteração.

| id | Pergunta | Resposta | Comentário | Respondida em |
|---|---|---|---|---|
| `rv5-erro-1-desenho` | Quando o programa apaga uma letra grande: o que o aviso do 'Para revisar' oferece? | **Botão 'Trazer de volta nesta página'** | eu acho que pode ser a opção 1, mas onde sumiu, tem que aparecer selecionado automaticamente, como na opção 3 | 09/10 15:57 |
| `rv5-erro-5-sem-conteudo` | Página sem conteúdo (em branco, ou só a mancha da página de trás): que botões o aviso mostra? | **Os dois botões: 'Deixar em branco' e 'Tirar do livro'** | Essa opção de tirar do livro ou deixar folha em branco eu quero ter em outras paginas, mas no caso essa ai aparece com aviso quando o programa detectar se tem uma folha em branco ou manchada. | 09/10 15:52 |
| `rv5-erro-6-so-texto` | Com 'Guardar só o texto', sumiu a música: o que o aviso do 'Para revisar' oferece? | **Botão 'Trazer de volta nesta página'** | opção 1, mas aparece marcado como apareceu na segunda opção. | 09/10 15:53 |
| `rv5-erro-2-gravura` | Achar as figuras com mais acerto: quando fazer? | **Fica no plano (1.5 e 2.18)** |  | 09/10 15:54 |
| `rv5-erro-4-tintas` | Reconhecer melhor a tinta (para a letra clara ou colorida não sair falhada): quando fazer? | **Fica no plano; até lá, a força sozinha** |  | 09/10 15:55 |
| `rv5-conserto-gravura` | O delineado das áreas achadas: como aumentar ou diminuir uma área? | **Os dois** |  | 09/10 15:57 |
| `rv5-conserto-faixa` | O corte da borda preta: o seletor de páginas. | **'Selecionar todas' e 'Nenhuma'** |  | 09/10 15:56 |
| `rv5-aviso-so-texto` | Os avisos: dar 'está bom' em uma página, num motivo ou em tudo; e o que acontece ao processar. | **Lista as páginas e os motivos** |  | 08/10 01:32 |
| `rv5-em-branco` | Um aviso para cada coisa, com os botões 'Deixar em branco' e 'Tirar do livro' separados: fica assim? | **Fica assim** |  | 08/10 01:31 |
| `rv5-pag-egenloff-047` | Egenloff 47: a moldura do scanner e a tarja da biblioteca saem do livro. Cortar fora ou pintar de branco? | **O Kaique escolhe por livro** |  | 08/10 01:30 |

## Como fica cada decisão (para o plano)

Os três comentários são refinamento, não dúvida: viram parte da decisão, sem pergunta nova.

- **Letra grande que some** (`rv5-erro-1-desenho`): o aviso tem o botão "Trazer de volta nesta página" (opção 1) **e** o lugar onde a letra sumiu já aparece marcado sozinho, como na opção 3 (o retângulo da aba Marcar, "letra e traço"), para o Kaique ver e ajustar antes de clicar.
- **Página sem conteúdo** (`rv5-erro-5-sem-conteudo`): o aviso tem os dois botões, "Deixar em branco" e "Tirar do livro". O aviso aparece quando o programa acha uma folha em branco ou manchada. Os dois botões também têm de existir em **qualquer** página, sem aviso (pedido que vai para a Lista de espera, junto do item de 07/10 "Página branca no lugar da página apagada").
- **"Guardar só o texto" que apaga a música** (`rv5-erro-6-so-texto`): o aviso tem o botão "Trazer de volta nesta página" (opção 1) **e** o que sumiu já aparece marcado, como na imagem da segunda opção (o retângulo em volta do que volta).
- **Detector de figuras** (`rv5-erro-2-gravura`): sem estudo agora; segue o plano (itens 1.5 e 2.18). Até lá, o delineado e a mão.
- **Reconhecer a tinta** (`rv5-erro-4-tintas`): o item 1.4 não é adiantado; até lá, a força do preto sozinha quando o texto sai falhado.
- **Mudar o tamanho das áreas achadas** (`rv5-conserto-gravura`): os dois jeitos, puxar pelos quadradinhos (cantos e lados) e pincel "somar"/"tirar" (item 2.18).
- **Seletor de páginas do corte da borda preta** (`rv5-conserto-faixa`): só os botões "Selecionar todas" e "Nenhuma" (sem "só as pares"/"só as ímpares").
- **Janela "Antes de processar"** (`rv5-aviso-so-texto`): lista as páginas e os motivos, com "ver" e "continuar assim mesmo" (hoje só diz quantas páginas).
- **Um aviso para cada coisa** (`rv5-em-branco`): fica assim: "Parece em branco" e "Página sem conteúdo" viram dois avisos, cada um com os dois botões separados.
- **Moldura do scanner e tarja da biblioteca** (`rv5-pag-egenloff-047`): o Kaique escolhe por livro entre cortar fora (item 2.13) e pintar de branco (item 2.14).

As 10 perguntas foram marcadas `decidida` no banco da página em 09/10, com a frase acima no campo `decisao`.
