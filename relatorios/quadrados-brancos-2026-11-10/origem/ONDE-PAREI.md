# ONDE-PAREI — de onde vieram os quadrados brancos (investigador, 10/11/2026)

Ramo `quadrados-origem-2026-11-10` (a partir de `obra-2026-10-26`, ponta `d9f80eb4`), worktree
`.claude/worktrees/quadrados-origem`. Só investigação: nenhuma linha do programa muda. Acervo só lido;
tudo em cópias, sem janela (`QT_QPA_PLATFORM=offscreen`), `LOCALAPPDATA` à parte, prioridade baixa.

## O que o Samuel perguntou

Central, 10/11, resposta "Ainda não entendi" ao relatório `relatorios/quadrados-brancos-2026-11-10/`:

> "Mas antes ele não fazia isso né, você tentou usar o motor do scantailor para achar gravura e onde achar
> gravura ele não deixar esses pontos brancos assim, pois eu nunca tinha visto o programa fazer isso, descubra
> que agente fez o programa começar a fazer isso, é só você ver os testes que fizemos antes com o melhorar e
> magico pro."

## Decisões que esta tarefa precisa cumprir

- Regra da Fase 1 (28/09): "todo o papel totalmente branco, inclusive o papel dentro da gravura"; "sem
  quadradinhos" (bug 202, roupa do anjo da Escola 35, `tests/test_papel_dentro_da_gravura.py`).
- D-009 (26/10): "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente."
- D-002 (25/09 e 26/10): o livro abre direto na área de trabalho; o Automático é um painel.
- D-586 / D-583 (29/10): "Respeitar as gravuras achadas" ligada = o filtro respeita a marcação.
- D-659 (09/11): no Preto e branco à mão, "Respeitar" marcada faz o programa procurar a gravura.
- D-605 (03/11): o novo não estraga o já escolhido e testado.
- CLAUDE.md §9: a correção do "magic color" não se desfaz. Não abrir janela na tela do Samuel (09/11).
- CLAUDE.md §10: modelo de print do girar. §2: relatório em três formatos. §11.7: só o que ele mandou.

## O que já está escolhido e testado aqui

- `core/filtros.py`, `_limpar_o_papel_de_verdade` (mancha do verso, "fundo meio amarelado"); o caminho de
  dentro da gravura (bug 202, `tests/test_papel_dentro_da_gravura.py`).
- `core/pipeline.py`, `garantir_selecao`; `core/etapas.py` (`marca_sozinho`, `respeitar_procura`, D-659/D-661);
  `tests/test_decisoes.py` (D-009), `tests/test_decisoes_respeitar_gravuras.py`, `tests/test_decisoes_gravura_a_mao.py`.
- Nada disso foi tocado: só scripts de medida e o relatório.

## Andamento

- [x] ramo e worktree; versões antigas em cópias (`git worktree` e `git archive`), apagadas no fim
- [x] página 13 em dez versões (bisseção)
- [x] oito páginas, Livro de Horas 47 e Boécio em cinco situações
- [x] livro inteiro (199 páginas, os dois filtros): antes, hoje e só a mudança desfeita
- [x] o caso do print 10 e o programa de antes sem a procura
- [x] imagens no modelo de print (`imagens/0` a `7`)
- [x] relatório nos três formatos (`relatorio-completo.md`, `.html`; o `.pdf` fica fora do git), commit e push

## O que achei

1. **Antes o programa não fazia isso.** Versão de 26/10 antes da obra (`ddd4d74a`, igual ao `fase-1`), livro
   inteiro: 2 páginas com buraco visível (43 e 173, céu claro liso, sem blocos), contra 65 (Melhorar) e 83
   (Mágico pro) hoje. Letras quebradas: 0 páginas antes, 25 a 28 hoje.
2. **Começou na obra de 26/10, com duas mudanças juntas:**
   - `175addb7` (26/10 21h25, etapa 1, Implementador da etapa 1, para cumprir a D-009): `garantir_selecao`
     passou a procurar a gravura só com o Automático ("Limpar a folha" + "Procurar gravura e letra"). Escolha
     técnica nº 5 do agente, pela D-014, não pedida pelo Samuel.
   - `e2321b16` (26/10 23h33, etapa 3, para cumprir a D-002; juntada à versão de teste em 27/10 11h45,
     `427e3ae2`): o livro abre direto com o Automático desligado e o filtro do painel vira "mexido à mão".
   - Bisseção na página 13: inteira em `a329166d`, `ddd4d74a`, `175addb7` (livro aberto como na época) e
     `4d535ab6`; buracos em `175addb7` com "Limpar a folha" desmarcada, `e2321b16`, `99a3cdc5`, `9f765d75`,
     `d25e2b76` e `d9f80eb4`.
   - A mesma causa deu o defeito do Preto e branco de 09/11; o conserto D-659 (`88731637`) voltou a procurar
     só no Preto e branco ("Melhorar e Magico pro a mao nao procuram").
3. **A ideia do Samuel está certa:** antes o motor do ScanTailor achou a gravura em 197 das 199 páginas e
   não houve blocos; hoje, no Melhorar/Mágico pro à mão, o motor não é chamado em nenhuma página. O programa
   de antes com "Procurar gravura e letra" desmarcada também fazia os buracos (22,8% na página 13).
4. **Só a mudança desfeita (simulação):** livro inteiro volta a 2 e 2 páginas (igual ao antes); letras
   inteiras; Horas 47 inteira; Boécio com papel mais branco (papel não branco de 3–17% para menos de 0,5%).
   Custa ~5 s a mais na primeira vez de cada página (Melhorar 2,4 → 7,7 s), procura também nas páginas no
   Original, e não muda o print 10 (27,4% igual). Conserto C: igual nas pinturas; print 10 vai a 5,8%.

## Perguntas para o Samuel

1. **Como o Melhorar e o Mágico pro escolhidos à mão devem voltar a proteger as pinturas?**
   - **Verde — voltar como era antes da obra** (procura a gravura em toda página mostrada, com "Procurar
     gravura e letra" ligada; ~5 s a mais na primeira vez de cada página; não muda o print 10).
   - **Roxo — conserto C** (procura só nas páginas com Melhorar/Mágico pro e "Respeitar" marcada, como a
     D-659, mais a regra "em volta é papel"; mesmo resultado nas pinturas; conserta a maior parte do print 10).
   - **Laranja — deixar como está.**
   Sugestão do investigador: roxo. Imagens: `imagens/0-resumo.png` a `imagens/7-quando-a-gravura-nao-e-usada.png`.
