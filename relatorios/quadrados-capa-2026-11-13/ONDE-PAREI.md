# ONDE-PAREI — quadrados na capa (investigação, 13/11/2026)

Verificador (investigação). Ramo `quadrados-capa-2026-11-13`, a partir do `obra-2026-10-26` (`84b32df8`, a versão de
teste). Worktree `.claude/worktrees/quadrados-capa`, com as junções `modelos\` e `gabarito\paginas\`.
**Nenhuma linha do programa muda.** Tudo sem janela (`QT_QPA_PLATFORM=offscreen`), prioridade baixa, dados num
`LOCALAPPDATA` à parte (`_trabalho/dados`, fora do git). O projeto do Samuel foi só copiado (`_tmp/samuel-gradus`,
fora do git), da pasta de dados da versão de teste
(`D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\...\pdfcoffee-com_gradus-primus-pdf-pdf-free`).

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro)

- **D-147** (30/09): "Cinza (tons de cinza): BOM" — no Preto e branco, foto e pintura saem em tons de cinza, nunca
  pontilhadas.
- **D-163** (05/10): padrão do "Só as letras" = "(1) A - Guardar a tinta forte".
- **D-583 / D-586** (29/10): "Respeitar as gravuras achadas", "De início vem ligada [...] Desligada, o filtro vale na
  página inteira: no Preto e branco, a capa sairia toda em preto e branco".
- **D-587** (29/10): com "Só as letras" ligado, a "Respeitar" fica cinza (o "Só as letras" manda).
- **D-588** (29/10, 01/11): "Gravuras em tons de cinza"; nasceu de "essa parece que está dando um negativo" (capa do
  *Na escola de Jesus*, Preto e branco, "Respeitar" desmarcada).
- **D-659** (09/11): no Preto e branco à mão, a gravura é procurada só na página onde a opção vale.
- **D-668** (10/11, conserto C, fora da versão de teste): Melhorar e Mágico pro procuram a gravura; a limpeza do papel
  só pinta de branco onde em volta também é papel.
- **D-473**: tela, prévia, miniaturas e PDF da mesma conta. **D-605**: nada novo muda o que já foi escolhido e testado.
  **D-667**: mudou a ferramenta, muda em todos os lugares.
- Regras do pedido: não abrir janela na tela dele; não mexer na Central nem no Livro; não abrir outros agentes;
  apagar só o que eu criei.

## O que já está escolhido e testado aqui (D-605)

Nada é mexido (só investigação). As provas que guardam o assunto: `tests/test_decisoes_respeitar_gravuras.py`,
`tests/test_decisoes_gravuras_cinza.py`, `tests/test_decisoes_gravura_a_mao.py`,
`tests/test_preto_e_branco_regra_30_09.py`, e, no ramo do conserto C, `tests/test_decisoes_quadrados_brancos.py`.

## Andamento

- [x] Li regras, CLAUDE.md, INDICE, investigação anterior e relatório do conserto C.
- [x] Worktree criada, junções feitas, livro e projeto do Samuel copiados.
- [x] 13-01 e 13-02 reproduzidos pela conta do programa (prévia, cartão e PDF iguais aos prints).
- [x] Causa do branco achada: o passo "sombra da foto de celular" do Preto e branco (`_sombra_em_quadros`,
      etapa 10b da obra, `c8844671`, 27/10 12:02). Sem ele: capa preta lisa (13-01) e caixa PRETA (13-02).
- [x] 13-02: o buraco vem da marcação (a "letra" achada em "PAULO RÓNAI" fura a gravura da capa); existia antes da
      obra (caixa preta); o branco dentro dele é o passo acima.
- [x] Versões: antes da obra (`ddd4d74a`) e antes da etapa 10b (`ab38208c`) sem branco; desde `c8844671`, branco.
- [x] Conserto C (`adf35fbf`): não muda nada nos dois casos.
- [x] Quem desmarcou a "Respeitar": o Samuel (acoes.jsonl, 16:09:49, "antes" true → "depois" false).
- [x] Tela (prévia), cartão e PDF: o mesmo defeito nos três (imagem 4).
- [x] Capa do *Na escola de Jesus*, Preto e branco com "Respeitar" desmarcada: os mesmos quadrados (7,4% dos
      pontos mudam sem o passo da sombra). Matemática: nada muda.
- [x] Cor na "sombra": fotos de celular 39-80 (média), capas 116-168: dá para separar (sugestão de conserto).
- [ ] Matriz (rodando em segundo plano, `scripts/rodar_matriz.sh`, log em `_trabalho/matriz.log`).
- [ ] Imagens no modelo do girar, relatório em três formatos, perguntas.

## Perguntas para o Samuel

(a preencher no fim)
