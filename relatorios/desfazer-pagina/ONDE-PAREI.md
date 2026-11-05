# ONDE-PAREI: desfazer nesta página (D-621)

Ramo `desfazer-pagina-2026-11-04` (saiu de `obra-2026-10-26`, `1d2ed264`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\desfazer-pagina`.

## Decisões que esta tarefa precisa cumprir

- **D-621** (04/11/2026): "eu quero um botão para desfazer ajustes em uma pagina só [...] eu quero poder
  clicar e falar quais coisas eu quero que sejam tirar, porque geralmnete quando a pagina já foi
  dividida, ela está certa e se eu juntar uma pagina na outra, a outra pagina que está certa vai voltar a
  ser uma junto com a que está errada [...] e eu quero fazer só em uma." · "com o botão direito clicando
  na pagina eu posso escolher a opção desfazer tudo" · "A2" (caixinhas).
  Na prática: botão direito na página (área de trabalho) ou na miniatura (tira) → "Desfazer nesta
  página" → lista das etapas que mexeram nela (Endireitar, Corte das bordas, Mover e tamanho, Filtro,
  Gravuras e fotos), cada uma com caixinha, e o botão "desfazer". Só as marcadas voltam ao que veio do
  scan, só nessa página. A divisão não entra; a outra página da folha não muda. Uma ação só no
  desfazer (Ctrl+Z volta tudo, Ctrl+Y refaz).
- **D-004** (28/09): "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." → depois de desfazer, a página segue o que o programa já faz com "deixar como veio" e
  "não cortar esta" (as duas gravam a marca "mexida à mão" da etapa).
- **D-368** (12/10): "B — “deixar como veio” e “usar o ângulo do programa”" (Endireitar) e "usar o corte
  do programa" (Cortar). Endireitar desfeito = o mesmo que "deixar como veio" (ângulo 0).
- **D-583 / D-586** (29/10): caixinha "Respeitar as gravuras achadas" por página; desligada, o filtro
  vale na página inteira (o que a máquina achou não vale). **D-587**: com "Só as letras", o "Só as
  letras" manda.
- **D-589** (30-31/10): "se algo não está marcado, não é para fazer".
- **D-590** (30/10): "juntar todas"; a divisão não é desfeita por aqui.
- **D-601 / D-610 / D-612**: "Uma página" / "Duas lado a lado" no Dividir; ferramentas também nos pares e
  no "antes / depois" (agem no depois).
- **D-618** (04/11): girar só a página da tela numa folha dividida (outra cópia faz; não mexo).
- **D-605 / §11.8** (03/11): "nenhuma função nova [...] pode alterar o que já está escolhido e testado".
- **§6 do CLAUDE.md**: alterar o desfazer precisa de aprovação: o Samuel pediu este (D-621).

## O que já está escolhido e testado aqui (D-605)

O que vou tocar e o que já existe ali:

- `ui/tela_conferir.py`: só métodos novos e duas ligações (o botão direito na área da página e na
  tira). Não mudo `_registrar`, `_angulo_zero`, `_sem_recorte`, `_conteudo_como_veio`,
  `_escolher_filtro`, `_selecao_mudou`, `desfazer`, `refazer`.
  Testes que já existem e têm de continuar passando: `test_endireitar_na_tela.py`,
  `test_endireitar_g5.py`, `test_paineis_na_tela.py` ("deixar como veio", "não cortar esta"),
  `test_decisoes_mover.py`, `test_decisoes_mover_lado.py`, `test_decisoes_9b2.py` (desfazer da
  marcação, D-020), `test_decisoes_respeitar_gravuras.py`, `test_decisoes_ferramentas_lado.py`,
  `test_decisoes_ferramentas_antes_depois.py`, `test_historico_depois_de_reabrir.py`,
  `test_decisoes.py` (D-004), `test_decisoes_marcacoes.py`, `test_decisoes_filtro_automatico.py`.
- `ui/widgets/visualizador.py`: o menu do botão direito do Mover (D-056, linhas de apoio) **continua
  igual**; fora do Mover o botão direito não fazia nada.
- `ui/widgets/tira_miniaturas.py`: clique, duplo clique e arrastar continuam iguais; só um sinal novo
  para o botão direito. Testes: `test_miniaturas_novas.py`, `test_decisoes_tira_em_pares.py`,
  `test_decisoes_tira_pares_juntas.py`.
- `ui/widgets/paginas_lado_a_lado.py`: clique continua escolhendo a página da vez; só um método novo
  que diz qual página está debaixo de um ponto.
- `core/`: **não mexo**.

## Como vai funcionar (o que cada etapa desfeita grava, só nessa página)

| etapa | grava | igual a |
|---|---|---|
| Endireitar | `angulo_manual = 0` | "deixar como veio" |
| Corte das bordas | `recorte = (0, 0, 1, 1)` | "não cortar esta" |
| Mover e tamanho | `conteudo_escala = 1`, `conteudo_deslocamento = (0, 0)` | "voltar como veio" do Mover |
| Filtro | `filtro = Original` | escolher "Original" no painel |
| Gravuras e fotos | marcação vazia + "Respeitar as gravuras achadas" desligada | "Limpar tudo" + a caixinha da D-586 |

Mais: a marca "mexida à mão" de cada etapa desfeita (como os botões acima) e `revisada = True` (como
eles). Tudo numa ação só do Histórico.

## Andamento

- [x] ONDE-PAREI (este arquivo)
- [x] testes novos (`tests/test_decisoes_desfazer_pagina.py`, 14; falham no código de antes:
  `reversao.txt`)
- [x] código (`ui/desfazer_nesta_pagina.py`; ligações em `ui/tela_conferir.py` e
  `ui/widgets/visualizador.py`; `core/` não muda) — commit `5f081246`
- [x] testes no PC, arquivo por arquivo (`testes-no-pc.txt`)
- [x] janela de verdade com prints (`piloto.py`, `anotacoes.txt`, `prints/`)
- [x] relatório (`relatorio-d621.md/.html/.pdf`)
- [x] push e GitHub (junto com a D-623, abaixo)
- [x] SEGUNDA entrega: D-623 (página em branco pelo botão direito na tira), pedida pela gerente
  em 04/11 durante a D-621. Traz a obra (`git merge obra-2026-10-26`, D-615) e mexe em `core/` e
  `modelos.py` (filtro de velocidade no GitHub). Andamento dela na seção D-623 abaixo.

# D-623: página em branco pelo botão direito na tira (segunda entrega)

## Decisões que esta parte precisa cumprir

- **D-623** (04/11/2026), print a-80: "as paginas ainda estão em lugar errado né? eu queria
  conseguir com botão direito apertando no meio das paginas aperece opção de adicionar folha em
  branco." → botão direito numa miniatura da tira: "adicionar página em branco antes" /
  "depois"; tamanho das vizinhas; entra no livro, no PDF e nos cadernos; "tirar do livro" remove;
  Ctrl+Z desfaz; mesmo menu da D-621. Muda o modelo de dados: projeto antigo abre igual.
- **D-487** (27/10): "'Inserir' página não foi feito nesta etapa (precisa de páginas que não vêm
  do PDF de entrada: muda o modelo de dados)". A D-623 autoriza essa mudança.
- **D-621** (acima): o mesmo menu do botão direito.
- **D-615 / D-616** (04/11): ordem das páginas mudada arrastando; a página em branco também anda.
- **§6 do CLAUDE.md**: formato dos arquivos de dados e desfazer: autorizados pela D-623 ("Muda o
  modelo de dados", "Ctrl+Z desfaz").

## O que já está escolhido e testado aqui (D-605)

- `modelos.py`, `core/ordem_das_paginas.py`, `core/dividir_a_mao.py`, `core/automatico.py`,
  `core/pipeline.py`, `historico_acoes.py`: toda mudança só vale para página com `inserida > 0`;
  página que veio do PDF (`inserida = 0`, a de todo projeto antigo) segue o caminho de antes.
  Testes de antes que têm de continuar: `test_decisoes*.py`, `test_core.py`,
  `test_historico_depois_de_reabrir.py`, `test_recomeco_limpa_o_historico.py`, `test_projetos.py`,
  `test_caderno_segue_as_etapas.py`, `test_dividir_desmarcada_caixinha.py`,
  `test_trabalho_nao_se_perde.py`, `test_salva_sozinho.py` e os da tira/tela da D-621.
- Menu da área de trabalho: continua só com o "Desfazer nesta página" (D-621).

## Andamento (D-623)

- [x] código e 9 testes novos (`tests/test_decisoes_pagina_em_branco.py`) — `d3550841`
- [x] janela de verdade no Gradus (`piloto_d623.py`, `anotacoes-d623.txt`, `prints-d623/`) — `dd1fb46b`
- [x] 05/11: `git merge obra-2026-10-26` (f06e0c15, D-617 parte 2): sem conflito, nenhum arquivo
  em comum com a D-623
- [x] reversão: os 9 falham no código de antes (`reversao-d623.txt`)
- [x] projeto antigo de verdade (Gradus) abre igual (`prova-projeto-antigo.txt`, `prova_projeto_antigo.py`)
- [ ] testes no PC, arquivo por arquivo (`testes-no-pc-d623.txt`)
- [ ] GitHub: testes 41949496078, velocidade 41949515821
- [ ] relatório nos três formatos (`relatorio-d623.md/.html/.pdf`)

## Como cumpri cada decisão (D-621)

- D-621: botão direito na página (Uma página, Duas lado a lado, antes/depois, Dividir) e na
  miniatura → "Desfazer nesta página" com as 5 etapas em caixinhas (apagadas as que não mexeram)
  e o botão "desfazer"; uma ação só. Provas: `test_d621_*` (14). Prints `03` a `16`.
- D-004/D-368: a página fica como com "deixar como veio"/"não cortar esta" (mesmo valor, marca
  "mexida à mão", "conferida"): `test_d621_a_pagina_fica_igual_a_deixar_como_veio_e_nao_cortar_esta`.
- D-586/D-587: Gravuras desfeitas = sem marcações e "Respeitar as gravuras achadas" desligada;
  com "Só as letras", o "Só as letras" manda (ressalva no relatório).
- D-590: a divisão não entra; a outra página e a folha não mudam (provas comparam campo a campo e
  o PDF ponto a ponto).
- D-612: nos pares vale a página clicada; com a peça da ferramenta no par, a página da vez.
- D-605: o menu das linhas de apoio do Mover continua igual (prova e print); nenhum teste antigo
  mudou.

## Perguntas para o Samuel

(nenhuma aberta)
