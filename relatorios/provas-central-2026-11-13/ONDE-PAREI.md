# Onde parei: prints de prova para a Central (verificador, 13/11/2026)

**TERMINADO.** Nenhuma linha do programa mudou. Sem commit no repositório do Samuel. Nada posto na Central.

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro)
- D-559 / D-692 (`ac-tampa`): "sumir em todo o livro, e o Kaique escolhe por livro cortar ou pintar de branco" · "O jeito como ela some deveria poder ser escolhido no automático, pintar de branco ou cortar. E essa resposta não tem print provando que esse modo funciona."
- D-189 / D-191 (`dv-211-215`): "Ele está apagando as letras" · "entra no programa e a caixinha não fica escondida."
- D-604 (`n0411-caderno-pagina-em-branco`): "o verso da folha 1 e 19 não podem ter a numeração de folha 1 - e 19 tem que dizer a numeração que elas realmente teriam." · "Porque usou uma folha sem estar divida?"
- `n0411-o-que-vai-sair`: "Como assim, o que vai sair? Quero um exemplo disso."
- D-693 (`v-capa`): "Fazer o botão de acertar os pares" (aqui só o problema, sem tela nova).

## Como cumpri cada uma
Ver `relatorio.html` (uma seção por pergunta, com as imagens e o que cada uma prova). Achados: cores ainda em duas
cores por palavra (D-189); Gradus dividido sem lugar vazio (prova no Righetti, D-604); "O que vai sair" abre sem nem o
título à vista.

## O que ficou
- Worktree `.claude/worktrees/provas-central` (obra-2026-10-26, 3a721bf8, junções `modelos` e `gabarito\paginas`),
  com os scripts e as fotos cruas em `_tmp\` (cópias dos livros e PDFs grandes já apagados). Para tirar: primeiro
  `(Get-Item <junção>).Delete()` nas duas junções, depois `git worktree remove`.
- A worktree do programa de antes (`provas-central-antes`, 50f03701) já foi removida (junções tiradas antes).
