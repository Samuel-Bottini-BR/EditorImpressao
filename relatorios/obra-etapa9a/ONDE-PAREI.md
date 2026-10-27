# ONDE PAREI — etapa 9a da obra de 26/10/2026 (agente de layout)

Ramo `obra-etapa9a-2026-10-26` (base `66a91d4`), worktree `.claude/worktrees/obra-etapa9a`.
Obra D-014: feita até o fim sem pausas; o Samuel confere tudo no fim. Os detalhes decididos por mim estão em
"Escolhas que fiz sozinho".

## Decisões que esta tarefa precisa cumprir (do Livro, `docs/plano/DECISOES.md`)

1. **D-012** (26/10/2026) — "2" (o "imprimir agora" fica para a etapa 9). Na prática: clicar "imprimir agora" pede
   impressora, cópias e confirmação. Ligada a **D-325** (`imp-5`: "Também manda direto para a impressora") e
   **D-332** (`b-5`). Lista única 5.1: "imprimir agora" manda o livro inteiro à impressora padrão sem perguntar.
2. **D-333** (22/10/2026) — `fr-26`: "Está bom" + "Só tem que melhorar esse layout, cheio de letras uma em cima da
   outra , tudo bagunçado e dificil de saber o que é o que." · `fr-26-qual`: "2- mandei o print." Na prática: janela
   "Montar para imprimir" organizada, o texto do resultado separado das opções; nada sobreposto em 1280×657 (150%) nem
   na janela mínima; singular/plural certos ("são 1 cadernos"). Respeitando as decisões de impressão:
   - **D-314** "o programa tem duas fases separadas" (formato só na hora de imprimir);
   - **D-315** "Quero TODAS essas opções dentro do programa" (nenhuma opção some na arrumação);
   - **D-316** livreto automático na ordem da dobra; **D-317** escala por lado (esquerda/direita/as duas);
   - **D-318** margens 1,3 cm do papel e 1 cm na costura; **D-319** aviso de margem abaixo de 1 cm;
   - **D-320** folha muito maior gira e reduz, com aviso;
   - **D-321** `imp-1` "Uma página só"; **D-322** `imp-2` "Já entra dentro das margens"; **D-323** `imp-3` "No meio
     da sua metade"; **D-324** `imp-4` "Último caderno menor, só com as folhas necessárias"; **D-325** `imp-5`
     "Também manda direto para a impressora"; **D-326** `imp-6` "Precisa: sem ela sai algo errado" (imprimir como
     imagem ligada de fábrica);
   - **D-330** `b-3-cadernos-antigo` "Deixar os dois" (o "Montar cadernos" antigo e o "Montar para imprimir").
3. **Rodinha do mouse** (teste do Kaique, 26/10: "ao rolar a janela 'Montar para imprimir' com a rodinha do mouse, o
   campo 'Páginas da esquerda (pares)' passou de 100% para 60% sozinho"): número e lista só mudam com a rodinha
   quando clicados (com o foco), no diálogo todo; ajuste reaproveitável para o resto do programa.
4. **Janelas de abrir e salvar arquivo em português** (teste do Kaique: "Look in", "File name", "Open"; digitar o
   caminho não abriu e não avisou; sem atalho para Área de trabalho/Downloads). Ligada a **D-301** ("escolher onde
   salvar o PDF [...] lembrar a última pasta usada [...] avisar em português").
5. Lista única **5.12** (dois "montar cadernos" com nomes parecidos; a "Ficou pronto!" não diz qual usar) e **5.15**
   (nome sugerido com acento "mágico pro") — só o que estiver nos meus arquivos.
6. **D-332** (22/10/2026) — `b-5-imprimir-direto`: "Testo uma folha na EPSON quando a conferência chegar
   (recomendado)". Eu não imprimo; deixo o roteiro curto para ele.

## Andamento

- [x] Li CLAUDE.md, layout.md, DECISOES (impressão), o plano, a lista única e o relatório do teste do Kaique.
- [x] Print do "antes": `prints/antes-montar-*.png` (as opções espremidas a uma faixa, texto atrás da barra de
      rolagem, botão "var o arquivo para impri" cortado).
- [ ] D-012 imprimir agora com confirmação
- [ ] D-333 janela refeita
- [ ] rodinha
- [ ] janelas de arquivo
- [ ] 5.12 / 5.15
- [ ] roteiro EPSON
- [ ] testes, prints, entrega

## Achado importante (janelas de arquivo em inglês)

O piloto do teste do Kaique ligou `Qt.AA_DontUseNativeDialogs` (`piloto/piloto.py:372`, "diálogo de arquivo do Qt
(fica fora da tela)"). Com isso o Qt usa a janela **dele**, em inglês, porque o programa não carrega a tradução do Qt
(`ui/perguntas.py:4`). No programa de verdade, no Windows, as janelas de abrir/salvar já são as do Windows (em
português, com Área de Trabalho e Downloads). Mesmo assim o conserto cobre os dois casos (ver "Como cumpri").
