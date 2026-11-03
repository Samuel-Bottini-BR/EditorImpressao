# ONDE-PAREI — D-602 (Dividir: linha antes de cortar, "dividir todas", "motor de corte")

Ramo `dividir-linha-2026-11-03` (saiu do `obra-2026-10-26`, ponta `8846017`). Worktree
`.claude/worktrees/dividir-linha`. Implementador, pedido da gerente de 03/11/2026.

## Decisões que esta tarefa precisa cumprir

- **D-602 (03/11/2026)** — palavras dele: "quando eu entro no dividir não aparece a linha azul, então eu aperto
  dividir folha, ele já dividi automaticamente sem mostrar a linha azul, ela não aparece mais em nenhuma folha, só
  aparece quando eu aperto duas lado a lado. Quando eu estiver na ferramenta de dividir, o programa deveria carregar
  com a conta que está escolhida, e dai eu conseguir ver a linha e dai eu clicar e dividir esta, dai ele reparte, se
  eu apertasse para todas as folhas ele carregaria para todas as folhas, faria a leitura em todas as folhas. teve um
  momento também que o botão do jeito ( que eu acho um nome bem ruim, acho que o nome poderia ser motor de corte)
  ficou travado e não dava para mudar." · "quando a folha for dupla, ela vai aparecer a linha de divisão ou até quando
  for só uma folha vai aparecer?" → só nas duplas → "pode ser assim na questão do divisor."
  Na prática: folha dupla ainda inteira já mostra a linha azul onde o motor escolhido cortaria (também em "Uma
  página"), nada cortado; folha de uma página só: sem linha; "dividir esta" corta nessa linha; botão novo "dividir
  todas" (cada dupla na sua linha, simples ficam inteiras); "usar em todas" fica como está; "jeito" vira "motor de
  corte" no Dividir e no Automático (opções "o do ScanTailor"/"o do Editor" não mudam); a lista travada: achar a
  causa e consertar.
- **D-090 (08/10/2026)** — "fazer um corte e mandar para todas as paginas e alterar em algumas paginas só o corte
  quando cortamos alguma, assim quando mudar de um não muda de todas [...]": "usar em todas" copia a linha desta
  folha, com as de linha própria desmarcadas. Não quebrar.
- **D-373 (20/10/2026)** — "B — “o do Editor”": nomes das opções do motor ("o do Editor", "o do ScanTailor"). Não
  mudar.
- **D-528 (27/10/2026)** — ao dividir uma folha pela primeira vez, as marcações da folha inteira vão para a metade em
  que estão. Não quebrar.
- Achadas no grep (linha azul / Dividir):
  - **D-601 (02/11/2026)** — "Uma página" mostra só a metade da folha dividida; "Duas lado a lado", a folha inteira
    com a linha para arrastar; tira: dividida = duas miniaturas, não dividida = uma dupla. Não quebrar.
  - **D-590** — "juntar todas" ao lado de "não dividir esta". Não quebrar.
  - **D-498** — "não dividir esta" guarda as duas páginas; "dividir esta" de novo as devolve, na linha de antes.
  - **D-495 / D-499** — a tampa do scanner é achada quando a pessoa divide (ou acerta a linha) à mão.
  - **D-500** — corte do ScanTailor na beirada (fora de 20%–80%) não é a lombada: vale a conta do Editor.
  - **D-074** — não tentar dividir folha que é claramente uma página só.
  - **D-080 / D-089** — o motor (jeito) é escolhido por livro, com troca numa folha.
  - **D-558** — "dividir" da grade Todas as páginas usa a conta do "dividir esta" (não mexer).
  - Regras do CLAUDE.md §3: a tela nunca congela (conta em QThread), progresso e "parar" que funciona.

## Andamento

- [ ] testes de reversão (lista travada; linha na folha dupla inteira em "Uma página") — falhar no `8846017`
- [ ] conta do motor por trás + linha na folha inteira
- [ ] "dividir esta" corta na linha mostrada
- [ ] "dividir todas"
- [ ] "jeito" → "motor de corte" (Dividir e Automático)
- [ ] provas D-602
- [ ] testes no PC, GitHub, filtro de velocidade
- [ ] prints da janela real (Gradus Primus)

## Perguntas para o Samuel

(nenhuma ainda)
