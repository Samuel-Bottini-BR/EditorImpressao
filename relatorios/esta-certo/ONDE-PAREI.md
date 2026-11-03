# D-572 "depois de 'está certo' a faixa diz conferida": onde parei

Ramo `esta-certo-2026-11-02` (saiu de `obra-2026-10-26`, commit `a3a7405`), cópia
`.claude/worktrees/esta-certo`. Construtor (layout/ui), 02/11/2026. Não juntei nada em nenhum outro ramo.

## O pedido (palavras dele)

- 02/11, testando o Dividir no Gradus Primus: "o aviso não sai, mesmo clicando no está certo" (print
  `relatorios/testes-guiados/2026-10-29-automatico/a-43-esta-certo-aviso-nao-sai.png`: folha 1 com tique
  verde, "1 de 70 conferidas", e a faixa continua "Achei a lombada e vou cortar na linha azul. Se estiver
  errado, arraste a linha." com o "está certo"). Depois: "quero".

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

- **D-572** (28/10): "eu cliquei está certo mas o livro continua com o aviso naquela folha, não devia ter
  mais aviso se eu apertei está certo" · "o está certo deixou o tique verde mas continuou com o aviso na
  pagina, dá para ver que a opção esta certo continua aparecendo, deveria sumir quando eu aperto está
  certo." · 31/10, Central: "A faixa diz "Página 7 conferida." e fica só "próxima dúvida" (recomendo)" ·
  "Mas nas paginas que não foi dado o ok, ela vai aparecer ainda né?" (gerente: sim).
  → **depois de "está certo", a faixa diz "Página N conferida." e fica só o "próxima dúvida"; nas páginas
  sem o ok, o aviso e o "está certo" continuam.** Prova: Palatino 7 → "está certo" → tique verde e a faixa
  sem "está certo".
- **D-259** (05/10): "Opção 1 (faixa fina)" · "Aprovado": aviso, "está certo" e "próxima dúvida" numa
  faixa fina embaixo da página. (A faixa continua a mesma; só some o "está certo" na conferida.)
- **D-010 / P-101**: "a folha fica conferida, tique na miniatura, contador sobe, vai para a próxima
  dúvida" (o "está certo" continua fazendo tudo isso).
- **D-497**: "o aviso que ela tirou não volta" (não mexo na conta dos avisos, só no que a faixa diz).
- **D-007**: no Dividir se vê a folha inteira; fora dele, uma página por vez (a unidade do Dividir é a folha).
- CLAUDE.md §3, §4.6, §4.7 (teste de reversão), §10 item 5 (comentário no que for tocado), §11 item 7
  ("só o que ele mandou": nenhum botão, aviso ou texto além do decidido).

## Escolhas dentro do pedido (a gerente mandou decidir pelo que o código já usa)

- **O que conta como "conferida" (resposta da gerente, 02/11, à minha pergunta 1):** "A sua pergunta 1 (mexer à
  mão já põe o tique) tem resposta no Livro, D-572, comentário do Samuel em 31/10: "Mas nas paginas que não foi dado
  o ok, ela vai aparecer ainda né?" [...] O "ok" dele é o botão "está certo". Então a faixa segue o **"está certo"
  apertado**, não o tique que a edição à mão põe". Primeira versão (commit `aa2ed95`) seguia o tique; trocada no
  commit seguinte. Como guardo a diferença **sem mudar o formato do projeto**: o ok é a ação "revisar" do Histórico
  (a que `_marcar_revisada` grava; o Histórico já fica gravado em `acoes.jsonl` e volta ao reabrir). Mexer à mão grava
  outras ações ("recortar", "ajustar_angulo", "mudar_filtro", a linha da lombada...), que põem o tique mas não são o ok. A faixa diz
  "conferida" quando a folha/página tem o tique **e** a ação "revisar" dela ainda está feita (`_ok_dado`).
- **O texto no Dividir:** lá a tira mostra FOLHAS ("Folhas - as laranjas eu não tive certeza"), o rodapé diz
  "folha 1 de 70" e "1 de 70 conferidas" conta folhas. Então a faixa diz **"Folha N conferida."**, com o N
  que o Kaique vê no "folha N de M" (Gradus Primus folha 1 → "Folha 1 conferida."). Nas outras ferramentas,
  **"Página N conferida."** com o N do "página N de M".
- **Ctrl+Z:** o desfazer do "está certo" tira a ação e o tique → a faixa volta ao texto de antes e o "está certo"
  volta (como o tique).
- **Mexer depois do ok:** a ação "revisar" continua feita e o tique fica → continua "conferida" (como o tique).
- **Números das páginas que andam:** juntar/dividir uma folha à mão ou o Automático refazer a lista mudam o número das
  páginas dali em diante. Para não pôr o ok de uma página em outra, a busca para nessa ação quando ela é desta folha,
  de uma folha antes dela, ou da lista inteira: aí a página volta à frase de sempre com o "está certo" (o tique fica).
  Folhas nunca mudam de número.
- **Quais botões contam como ok (todos gravam a mesma ação "revisar"):** o "está certo", a barra de espaço ("marca e
  já vai para a próxima"), o "está bom assim" do último aviso da página, e os botões que só dão a página por
  conferida: "só nesta" do "Aplicar em" do Filtro, o "Usar" da tela cheia dos filtros com o mesmo filtro, o "não
  dividir esta" numa folha que já tem uma página só, e o "ver o corte alargado" quando ainda não há corte alargado.

## O que mudou

| Arquivo | O quê |
|---|---|
| `ui/tela_conferir.py` | `_atualizar_faixa`: um caso novo entre a página em branco e a frase de sempre: a folha/página com o tique **e** o ok no Histórico (`_conferida_na_faixa`, `_ok_dado`) mostra `_texto_conferida()` ("Página N conferida." / no Dividir "Folha N conferida."), sem botão de aviso; o "está certo" fica escondido só nesse caso. `_texto_tranquilo` ganhou docstring. Nada mais muda: o "próxima dúvida", o clique do "está certo", a barra de espaço, os avisos e as contas ficam iguais. |
| `tests/test_decisoes_avisos.py` | 9 provas `test_d572_*` (página com aviso e a vizinha sem o ok; Dividir folha 1 como no Gradus; Cortar, Endireitar, Marcar/Filtro e Mover; Ctrl+Z na página e no Dividir; mexer à mão põe o tique e a faixa continua com a frase e o "está certo"; juntar uma folha depois não tira o ok das páginas de antes). |
| `tests/promessas/promessas.md` | P-101 diz o que a faixa mostra depois do "está certo" (D-572). |

Fora do caso novo (ficam como eram): a página "em branco" (continua "Esta página vai sair em branco" com
"voltar a página" e o "está certo") e a página tirada do livro.

## Perguntas para o Samuel

1. ~~Mexer à mão também põe o tique~~ → **respondida pela gerente (02/11)** com o Livro (D-572, 31/10): a faixa segue
   o "está certo" apertado. Feito (acima).
2. **Respondida pelo Samuel (02/11, pela gerente): "pode deixar do jeito que ele esta fazendo".** Fica: na página,
   "Página N conferida." e só o "próxima dúvida" (escolha de 31/10); no Dividir, "Folha N conferida.". Pergunta que
   foi: lá quem fica conferida é a folha (a tira mostra
   "FOLHAS" e a barra de baixo diz "folha 1 de 70"), então a faixa diz "Folha 1 conferida.". Está certo assim, ou
   prefere "Página" também ali?
3. **Para a gerente decidir se leva:** os botões "só nesta" (Aplicar em, painel Filtro) e "Usar" (tela cheia dos
   filtros, com o mesmo filtro) gravam o mesmo "conferir" do "está certo", então também deixam a faixa "conferida".
   Separar exigiria um tipo novo de ação no Histórico (mudaria o que fica gravado em `acoes.jsonl`); não fiz.
