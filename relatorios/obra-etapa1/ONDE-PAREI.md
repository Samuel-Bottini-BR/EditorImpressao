# ONDE-PAREI — obra de 26/10/2026, etapa 1: "o que é feito à mão sempre vale no PDF"

Implementador · ramo `obra-etapa1-2026-10-26` (base `obra-2026-10-26` = `fase-1` `ddd4d74`) · worktree
`.claude/worktrees/obra-etapa1` · worktree de apoio (código antigo, só leitura, para a prova):
`.claude/worktrees/obra-etapa1-antes` (`ddd4d74`, solta, com as junções `modelos` e `gabarito\paginas`).

## Decisões que esta tarefa precisa cumprir (do Livro de decisões, `docs/plano/DECISOES.md`)

- **D-009 (26/10/2026):** "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
  manualmente." → O que é feito à mão sempre vale no PDF, com a etapa do automático ligada ou não.
- **D-004 (28/09/2026):** "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." → marca "mexida à mão" por página/folha e por etapa (esta etapa cria a marca; a pergunta é da etapa 3).
- **D-016 (escolha da gerente pela D-014):** a montagem da página segue a ordem obrigatória (endireita, depois corta
  uma vez só, no fim).
- **D-008 (parte de processamento; 22/09 e 26/10/2026):** "quero conseguir redimensionar o conteudo tambem" · "a
  ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como
  é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser" → mover/redimensionar o conteúdo
  chega ao PDF. Teste do Kaique (26/10, tarefa 5): "Mover conteúdo" arrastado para o meio não sai no meio do PDF
  (margens 15 × 53).
- **D-014 (26/10/2026):** obra até o fim sem pausas; os detalhes técnicos eu decido e anoto aqui.
- **D-017 (escolha da gerente):** aumentar além da beirada não corta nada escondido (o aviso e a marca na tela são da
  etapa 5) — tocada de leve aqui: o PDF não pode jogar o mover fora.

## Situação

Em andamento (começado 26/10/2026).

## Escolhas técnicas (D-014: decido e anoto)

1. **Um lugar só: `core/etapas.py`.** Cada etapa separa "o automático mede" (a caixinha: `corta_sozinho`,
   `endireita_sozinho`, `marca_sozinho` = "Limpar a folha" + "Procurar gravura e letra") de "o feito à mão vale"
   (`recorte_a_mao`, `angulo_a_mao`, `filtro_a_mao`/`filtro_que_vale`, `marcacao_a_mao`, `conteudo_mexido`). A
   pergunta do pipeline é "vale nesta página?" = automático ligado OU feito à mão (`corta`, `endireita`, `filtra`).
   O automático **nunca** passa a medir com a caixinha desligada (é o que mantém o livro novo de fábrica igual).
2. **Projeto antigo sai igual — campo `Projeto.feito_a_mao_sempre_vale`.** Livro novo: `True`. `projeto.json`
   gravado antes desta etapa (sem o campo): `False` (`Projeto.de_dicionario`, `setdefault`, como o
   `ordem_do_preparo` de 09/10). No projeto antigo o valor à mão com a etapa desligada continua ignorado, a não ser
   que a página tenha a **marca** daquela etapa — isto é, que a pessoa mexa de novo pela tela (quando a etapa 2/3
   ligar as marcas). Assim nenhum PDF antigo muda ao abrir, e o que ele fizer daqui para frente segue a D-009. O
   projeto antigo regravado guarda `false` e continua antigo. (A janela, quando o trabalho salvo combina, usa o
   próprio objeto salvo — `ui/janela_principal._analise_pronta`, `projeto = salvo` —, então o campo atravessa sem
   mexer em `ui/`.)
3. **A marca "mexida à mão" (D-004):** `ConfigPagina.mexida_a_mao` e `ConfigFolha.mexida_a_mao` = lista de etapas
   (`cortar`, `endireitar`, `filtro`, `marcar`, `mover`; `dividir`, `girar` na folha). Funções para a tela:
   `etapas.marcar_mexida_a_mao(item, etapa)` / `desmarcar_mexida_a_mao`. Para a pergunta da etapa 3:
   `paginas_mexidas_a_mao(projeto, etapa=None)`, `folhas_mexidas_a_mao`, `mexida_a_mao`, `etapas_mexidas_a_mao`
   (marca OU valor que só a pessoa põe). Migração `marcar_pelos_valores` (chamada em `de_dicionario`): livro novo
   marca todo valor à mão; projeto antigo só onde o valor **já valia** (etapa ligada) e nunca `mover`.
4. **O que conta como valor à mão sem marca (livro novo):** corte = `recorte` gravado; ângulo = `angulo_manual`;
   marcação = região com origem `mao`; mover = escala ≠ 1, deslocamento ≠ 0 ou tamanho de folha; folha = girada.
   **Filtro e dividir: só pela marca da tela, nunca pelo valor.** Tentei primeiro "filtro da página ≠ filtro do
   livro" e os testes mostraram o risco: o filtro do livro pode mudar depois na tela "O que fazer" (o radio fica
   escolhido mesmo com "Limpar" desligado) e as páginas ficam com o de antes — o livro inteiro viraria "mexido à
   mão" e sairia filtrado com "Limpar" desligado (prova: `test_d009_filtro_do_livro_trocado_depois_...`). O mesmo
   com a folha dividida por uma análise antiga. Consequência: **até a etapa 2 ligar a marca, o filtro escolhido à
   mão numa página com "Limpar" desligado ainda não chega ao PDF** (o corte, o ângulo, a marcação e o mover já
   chegam). O resto (força do preto, linha de divisão arrastada) também só pela marca.
5. **Filtro com "Limpar a folha" desligado (livro novo):** página sem nada à mão sai como veio; filtro escolhido à
   mão → caminho inteiro com esse filtro e **só a marcação à mão** (o detector de gravura é automático e fica
   desligado); só marcação à mão → página no Original com só o marcado mudando (`_so_a_marcacao_a_mao`: pedaço,
   "pintar por cima"...). `filtro_que_vale` substitui todos os "`projeto.limpar and pagina.filtro == X`".
6. **Mover (D-008) — o que achei:** `compor_na_folha` jogava o mover fora em dois casos: (a) sem tamanho de folha
   (devolvia a página sem mexer); (b) folha do tamanho do corte arredondada a 0,01 cm (a janela "tamanho..." do
   teste do Kaique mostrou 16,23 × 21,01): a folha sai 1 ponto menor que o conteúdo e a "rede de segurança"
   desistia de compor — o deslocamento sumia. Conserto: parâmetro `mexido_a_mao` (= `etapas.conteudo_mexido`):
   sem folha, a folha é a própria página; com folha, não desiste por caber 1 ponto a menos — cola e corta só o que
   passa da beirada (D-017: a página fica do mesmo tamanho; o aviso é da etapa 5). Sem mover à mão, a conta de
   sempre, linha por linha. **Lado da tela (etapa 5, não mexi):** o `Visualizador._mover_conteudo` prende o
   retângulo dentro da folha — com a folha do tamanho do corte o conteúdo nem anda (no teste do Kaique o arrastar
   provavelmente não gravou deslocamento nenhum); a prévia (`TelaConferir`, `compor_na_folha` sem `mexido_a_mao`)
   precisa passar `mexido_a_mao=etapas.conteudo_mexido(...)` para a tela = PDF; `_mover_conteudo` da tela sai cedo
   sem tamanho de folha.
7. **Caminho rápido "só cadernos"** (`Projeto.so_cadernos`): não é usado se houver feito à mão que vale
   (`etapas.tem_feito_a_mao_que_vale`), senão a folha girada/dividida à mão, o corte etc. sumiam do PDF.
8. **Ordem obrigatória (D-016):** nada muda na montagem: o feito à mão entra nas mesmas contas (`_geometria`,
   `_geometria_endireitando_antes`, `_preparar_endireitando_antes`), endireita a página inteira e corta uma vez no
   fim. Prova: mesma página com as etapas ligadas ou desligadas, com ângulo e corte à mão (`test_d016_...`).
9. **A análise do livro** (`analisar_projeto`, `_analisar_a_folha`) continua olhando só as caixinhas: ali só existe
   o automático (o livro acabou de ser lido, não há nada à mão).
10. **Resumo da tela "O que fazer"** (`resumo_em_portugues`): acrescenta "manter o que você fez à mão em N páginas"
    só quando há feito à mão numa etapa desligada (sem isso, frase igual à de antes).

## Para as etapas 2, 3 e 5 (o que a tela precisa ligar)

- Ao mexer à mão: chamar `core.etapas.marcar_mexida_a_mao(pagina_ou_folha, etapa)` (corte, ângulo, filtro da
  página e seus ajustes, marcação, mover/tamanho da folha; dividir/girar na folha). Ao "voltar ao automático":
  `desmarcar_mexida_a_mao`. Sem isso, no **projeto antigo** o feito à mão novo com a etapa desligada não vale (no
  livro novo vale pelo valor).
- Pergunta "pular as páginas mexidas?" (D-004, etapa 3): `etapas.paginas_mexidas_a_mao(projeto, etapa)`.
- Etapa 5: prévia com `mexido_a_mao`; mover sem tamanho de folha (a folha é a página: em `conteudo_como_retangulo`
  / `deslocamento_do_retangulo` passar o tamanho da própria página em cm); não prender o retângulo na folha.

## Passos

- [ ] Prova "Desligado de fábrica" no código antigo (somas das 32 páginas × 3 filtros), por trás.
- [ ] `core/etapas.py` (um lugar só) + marca "mexida à mão" no modelo, com migração.
- [ ] `core/pipeline.py`: checagens de caixinha trocadas por `core/etapas.py`.
- [ ] Mover/redimensionar chegando ao PDF (`core/folha.compor_na_folha`).
- [ ] `tests/test_decisoes.py` (D-009, D-004/marca, D-008, projeto antigo igual).
- [ ] Prova "Desligado de fábrica" no código novo + prova do projeto antigo com valores à mão.
- [ ] Testes por arquivo; commits; push.

## Perguntas para o Samuel

Nenhuma até agora.
