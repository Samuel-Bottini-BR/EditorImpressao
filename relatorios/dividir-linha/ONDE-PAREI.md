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

## Andamento (03/11/2026)

- [x] testes de reversão: `test_reversao_d602_lista_do_motor_nao_trava_na_folha_inteira` e
      `test_reversao_d602_linha_azul_na_folha_dupla_inteira_em_uma_pagina` — **falharam no `8846017`** (lista cinza;
      `corte_visivel` False), passam no novo
- [x] leitura do motor por trás (`core/dividir_a_mao.ler_a_linha`, `ui/tarefas.TarefaLerLinhas`) + linha na folha
      inteira (`TelaConferir._acertar_a_linha_do_dividir`), selo "atualizando..." enquanto lê
- [x] "dividir esta" corta na linha mostrada
- [x] "dividir todas" (andamento + "parar", uma ação do desfazer, não marca "conferidas")
- [x] "jeito" → "motor de corte" (Dividir e Automático)
- [x] provas D-602: `tests/test_decisoes_dividir_linha.py` (13)
- [x] testes no PC (um arquivo por vez): ver relatório
- [ ] GitHub: rodada 41706257524 (conjunto + teste_botoes); filtro de velocidade 41706298782 (8846017 → d2c6ffa1)
- [x] prints da janela real (Gradus Primus e Boécio, pasta de dados isolada no scratchpad): `depois-*.png` aqui

## Causa da lista travada

`ui/tela_conferir.py`, `_atualizar_botoes`: `combo_jeito_da_folha.setEnabled(bool(folha.dividir))`. A lista só
ficava acesa em folha DIVIDIDA. Livro aberto sem Dividir (o Gradus) = todas as folhas inteiras = lista cinza em todas
(no tema escuro quase não se vê a diferença, por isso "travada"), e `_trocar_jeito_da_folha` também voltava sem fazer
nada em folha inteira. Depois de "dividir esta" ela acendia; depois de "não dividir esta"/"juntar todas", apagava de
novo. Conserto na causa: acesa em toda folha; na folha inteira, trocar grava o motor desta folha (uma ação do
desfazer) e a linha é lida de novo pelo motor novo, sem cortar.

## Perguntas para o Samuel

1. **Arrastar a linha na folha ainda inteira.** Hoje a linha da folha inteira é só para ver (não arrasta, sem a pega
   "arraste"); para mudar onde corta, divide e depois usa "Duas lado a lado" (D-601). Quer poder arrastar a linha
   ANTES de dividir? (print `depois-1-folha-5-inteira-uma-pagina.png`)
2. **Frase da faixa na folha inteira com linha.** Continua "Esta folha não vai ser dividida." (não mexi). Quer outra
   frase quando a linha aparece? (mesmo print)
3. **Lugar do botão "dividir todas".** Ficou ao lado do "usar em todas", na linha de baixo (dois por linha, como
   "não dividir esta" / "juntar todas"). Está bom aí? (mesmo print)
4. **Aviso quando não há o que dividir.** "dividir todas" sem folha dupla inteira mostra "Nenhuma folha dupla para
   dividir: as que faltam são de uma página só." (ou "Todas as folhas já estão divididas."). Pode ser assim?
5. **"Conferidas".** O "dividir todas" não marca as folhas como conferidas (como o "juntar todas", D-590); o "dividir
   esta" continua marcando a folha. Pode ser assim? (print `depois-4-depois-de-dividir-todas-folha-5.png`: "0 de 70
   conferidas")
6. **Folha que você juntou.** Mostra a linha de antes (onde o "dividir esta" a devolve, D-498), se o motor acha a
   folha dupla; o "dividir todas" a devolve como estava. Pode ser assim?
