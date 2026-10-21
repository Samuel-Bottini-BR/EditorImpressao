# Para revisar — Decidido pelo Samuel, a fazer: o "Para revisar" (rodadas 3 a 5)

Fase 2 (bloco sem número) · **PRONTO no ramo `fase2-para-revisar` (`8cb84b8`); aba 4 da conferência publicada (18 quadros, 3 perguntas, decisão `pr`) e SEM resposta** · ficha montada em 20/10/2026 · o que manda: [PLANO-DEFINITIVO, Fase 2, bloco "Decidido pelo Samuel, a fazer: o 'Para revisar'"](../../docs/plano/PLANO-DEFINITIVO.md)

## Situação

- **Atualização de 21/10/2026 ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); vale sobre os pontos de 20/10 abaixo:** o "Para revisar" foi juntado **ao layout aprovado** (`adf4e69`, 20/10/2026: 64/64 saídas iguais; suíte 2172/0; 3 testes de reversão) e ganhou as frases da rodada 14 e dois consertos: ramo `fase2-para-revisar` em **`8cb84b8`**, **PRONTO**. **Aba 4** da página de conferência publicada, **sem resposta**: 18 quadros, 3 perguntas (`pr-medir-o-livro`, `pr-contagens`, `pr-tela-igual-ao-pdf`), decisão `pr`. Ressalva que vai junto: o Boécio chega a 34% no "Para revisar". Não juntado ao `fase-1`.
- **Pronto em ramo, não juntado:** ramo `fase2-para-revisar`, commit `ce2b835` (13/10/2026). Os seis pedaços estão construídos. Suíte no Windows do GitHub: 116 arquivos, 2101 passaram, 0 falharam (Registro 13/10/2026).
- **Segunda conferência do verificador feita, mas parada pelo Samuel em 13/10/2026 às 17:30** (checkpoint): ramo `verif-para-revisar-2026-10-13`, commit `f506ec3`. Os 8 pontos foram conferidos na janela de verdade: 7 valem, 1 "em parte" (teclado: a seta não troca de página na janela de teste, igual ao programa de hoje). Falta: abrir uma a uma 19 imagens novas; reabrir Opus Majus 20, Antiphon 260, Cursus 3 e Camões 66 (`ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`).
- **Liberado de novo em 19/10/2026**: "Verificador - ok" (conferência do "Para revisar"), palavras do Samuel no [plano, Registro 19/10/2026](../../docs/plano/PLANO-DEFINITIVO.md). Conferido no git em 20/10/2026: os dois ramos continuam com o último commit de 13/10 (`ce2b835` e `f506ec3`); nada novo no GitHub ainda.
- **Marca no plano:** nenhuma. O bloco não tem número nem caixinha `[ ]`.
- **Conferido pelo Samuel:** não. Ele decidiu *o que* fazer (rodadas 3 a 5), mas ainda não viu o resultado construído. A conferência dele seria a **aba 4 da página de conferência** (https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX), **ainda por montar**, a partir do `conferencia.json` do verificador (18 quadros `pr-*` e as três perguntas abaixo) ([histórico, PARTE -15 §4 item 6](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)). As perguntas com opções precisam de um desenho novo na página (as abas de hoje só têm "Está bom / Melhorar / Está pior").

## O que vale hoje

O "Para revisar" é a lista de páginas que o programa acha que o Kaique deve olhar. A regra e os botões foram decididos pelo Samuel em cinco rodadas na página "Quando revisar uma página" (https://claude.ai/artifact/NeCgyTotRfqsdXntn9vMUc). O plano diz o lugar: "Sem número de item: lugar sugerido pela gerente, junto da regra do 'Para revisar' (`core/analise.py`, `core/pipeline.py`)". A aparência fica com o agente de layout: "a questão das funcionalidades eu acho que é contigo, mas a questão visual é com o agente de layout, deve ser feito as funcionalidades e depois passado relatorio para ele né" (rodada 4, 08/10/2026).

Os seis pedaços, como decididos (literais em [rodada 4](../../relatorios/revisar-decisoes/rodada-4/respostas-samuel.md), [pedidos da rodada 4](../../relatorios/revisar-decisoes/rodada-4/pedidos-funcionalidade.md) e [rodada 5](../../relatorios/revisar-decisoes/rodada-5/respostas-samuel.md)), e o que o ramo faz:

1. **Regra ajustada** (`rv4-resumo`: "Fica assim"). Mede o que foi apagado no resultado (desenho apagado, texto falhado, página sem conteúdo, figura além da gravura, faixa escura na beirada). Sai o aviso "Tinta forte fora do texto". A faixa em 70% ou mais das páginas medidas vira um aviso só, do livro. No ramo: `core/revisar.py`.
2. **Um aviso para cada coisa, com dois botões** (`rv4-em-branco`: "Tem que ter um tipo de aviso para cada coisa, e um botão de apagar folha e outro realmente de só mudar para um folha branca."; `rv5-em-branco`: "Fica assim"). "Parece em branco" e "Página sem conteúdo" separados, cada um com "Deixar em branco" e "Tirar do livro" (`rv5-erro-5-sem-conteudo`: "Os dois botões"). Depois da conferência do verificador ganharam também "está bom assim".
3. **Conserto rápido como botão no aviso** (`rv4-conserto-desenho`: "(a) Botão no aviso"). "Trazer de volta nesta página", com o lugar já marcado: "eu acho que pode ser a opção 1, mas onde sumiu, tem que aparecer selecionado automaticamente, como na opção 3" (`rv5-erro-1-desenho`, 09/10/2026) e "opção 1, mas aparece marcado como apareceu na segunda opção." (`rv5-erro-6-so-texto`). No ramo, o lugar aparece num retângulo laranja tracejado (só mostra, não é área ajustável; ver 2.18).
4. **Força do preto sozinha quando o texto sai falhado** (`rv4-erro-4-texto-falhado`: "Força sozinha" + "mas temos que melhorar o reconhecimento de tintas, para não sair falhado assim, não precisar usar sempre o reforço."). Força 85 só na página, aviso com "Desfazer", caixinha de ligar e desligar na tela "O que fazer" (livro novo ligado; projeto antigo desligado). O certo de verdade é o 1.4 (ver [../itens/1.4.md](1.4.md)).
5. **Janela "Antes de processar" lista as páginas e os motivos** (`rv5-aviso-so-texto`, 08/10/2026: "Lista as páginas e os motivos"), com "ver" e "continuar assim mesmo".
6. **"Está bom" em cada nível** (`rv4-aviso-so-texto`): "Eu tenho que conseguir fazer isso com uma pagina individual, com um motivo individual de uma pagina e com todas as paginas ou com todos os motivos de todas as paginas, e eu devo conseguir abrir um selecionador em aba grande mostrando todas as paginas com aquele problema e deselecionar ou dar ok em todas, mas quando eu resolver aquele problema, o programa já vai automaticamente ver que eu resolvi? [...] quando alguém tentar imprimir sem ver os alertas o programa para e mostra os alertas e a pessoa diz se quer ver ou continuar". Seletor só com "Selecionar todas" e "Nenhuma" (`rv5-conserto-faixa`); é o mesmo seletor do corte (2.13).

Mais duas decisões do bloco: **pauta com pouca falha não vai** (`rv4-pag-antiphonal1547-006`: "Entendi; a página não precisa ir") e **linhas pretas da beirada no livro todo: aviso no livro basta** (`rv4-pag-camoes-066`: "São as linhas pretas: aviso no livro basta"; depende do corte, 2.13).

**Decisões técnicas da gerente, dentro da alçada** (13/10/2026; [histórico, PARTE -15 §3](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md); Registro 13/10/2026):
- reacertar só os limites da regra no preparo do livro novo (G6): tamanho do pedaço grande 1,5 → **1,2**; mínimo da guarda da linha 0,20 → **0,13**. Resultado nas 89 páginas: **22 vão e 75 certas** (o aprovado era 21 e 78). As 5 que ainda diferem: Antiphon 260, Cursus 3, Matemática 72, Opus Majus 20, Palatino 66;
- força do preto sozinha só com **4 ou mais linhas falhadas (ou todas)** e só fica se as falhas caírem ("P3"); nas 89 páginas age só no Camões 27 e 104;
- a marcação que vale é a do **tamanho do PDF, procurada por trás** depois da prévia (a prévia de 110 DPI erra: 39 vão, 60 certas).

**Campos novos no projeto salvo** (mudança de formato de dados; avisar o Samuel na conferência): na página `em_branco`, `alertas_aceitos`, `forca_antes_do_reforco`, `reforco_desfeito`, `faixa_na_beirada`, `marcacao_provisoria`; na folha `alertas_aceitos`; no livro `reforcar_texto_falhado`. Todos com valor padrão: projeto antigo abre e sai igual ponto por ponto (teste `test_projeto_antigo_sai_igual_ponto_por_ponto_mesmo_com_texto_falhado`).

**Mágico pro +1,1% mais lento: fica para a Fase 5.** Palavras do Samuel em 19/10/2026: "vamos deixar esse concerto de lentidão para o final, para a fase de desempenho." ([plano, Registro 19/10/2026](../../docs/plano/PLANO-DEFINITIVO.md); `CLAUDE.md` §4.6).

**O que fica de fora do ramo** (de propósito): "Deixar em branco" e "Tirar do livro" em qualquer página, sem aviso, é da Lista de espera, Fase 6 (`rv5-erro-5-sem-conteudo`: "Essa opção de tirar do livro ou deixar folha em branco eu quero ter em outras paginas"); o "Parece em branco" continua com a conta antiga (bug da Gladstone 18); a regra só vale no "Só as letras" com "Guardar a tinta forte" ou "Guardar só o texto" (o "Só as letras" mora em [1.5](1.5.md)).

**Frase da rodada 14 (20/10/2026):** `r14-aviso-marcar` "C — Diz onde fica o "letra e traço"" (a frase nova do aviso `core/analise.py`).

**Mágico pro +1,1% do "Para revisar":** Fase 5 ("vamos deixar esse concerto de lentidão para o final, para a fase de desempenho.", 19/10/2026).

**"Parece em branco" consertado** (ramo `consertos-2026-10-21`, Gladstone 18): passa a avisar 49% das páginas do Egenloff (versos realmente vazios); acima de 70% vira aviso do **livro inteiro** ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §4).

## Mudou em

- 05/10/2026 — antes: não havia aviso por tinta fora do texto → ficou: "REVISAR Mandar para 'Para revisar' sozinho?: Sim" (conferência 8, [respostas](../../relatorios/conferencia-samuel-2026-10-05-f.md)).
- 06/10/2026 — antes: limite "a partir de 10%" posto pela gerente até ele decidir → ficou: "Como está hoje (a partir de 10%)", mas "não ficou claro ainda" e "gostaria de saber qual é o criterio para um pagina entrar em revisão" ([respostas de 06/10](../../relatorios/conferencia-samuel-2026-10-06.md)).
- 06/10/2026 — estudo pedido por ele ("coloque um agente só para pensar nisso e testar isso, e me traga o relatorio"): hoje 35 de 59 vão e só 7 erradas ([estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)). Rodadas 1 e 2 respondidas no mesmo dia.
- 07/10/2026 — rodada 3: concordou em 22 de 30 páginas e discordou de 8; pediu "mais opções de como vai ser concertado esses erros" ([rodada 3](../../relatorios/revisar-decisoes/rodada-3/respostas-samuel.md)).
- 08/10/2026 — antes: aviso "Tinta forte fora do texto" acima de 10% → ficou: regra ajustada, "Fica assim" (89 páginas: hoje vão 55 e acertam 52; a regra ajustada manda 21 e acerta 78) ([rodada 4](../../relatorios/revisar-decisoes/rodada-4/respostas-samuel.md)).
- 09/10/2026 — rodada 5 fecha o como de cada botão ([rodada 5](../../relatorios/revisar-decisoes/rodada-5/respostas-samuel.md)); os 13 pedidos entram no plano.
- 13/10/2026 — limites reacertados pela gerente para o preparo novo (1,5 → 1,2; 0,20 → 0,13) e força sozinha mais cautelosa (P3). Não muda nenhuma decisão do Samuel; o resultado (22/75) fica perto do aprovado (21/78).
- 19/10/2026 — o Mágico pro +1,1% vai para a Fase 5 (literal acima).

- 20/10/2026 — antes: pronto em `ce2b835`, esperando a 2ª conferência do verificador → ficou: juntado ao layout aprovado (`adf4e69`), com 64/64 iguais, suíte 2172/0 e 3 testes de reversão; 21/10/2026: `8cb84b8` e aba 4 publicada (Registro 20/10/2026 e 21/10/2026).

## Tentado e descartado

- Aviso por "tinta forte fora do texto > 10%": manda 35 de 59 páginas, 20 certas à toa ([histórico, PARTE -12 §4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
- "Pedaço de figura pego como texto" como critério de revisar: 35 páginas, 23 certas; não serve (PARTE -12 §4).
- Perguntas "o jeito rápido e o manual" sem imagem de cada um: ele não entendeu ("não entendi", "o que eu estour espondendo?", rodada 4); foram refeitas com imagem na rodada 5 (PARTE -13 §4).
- Procurar a marcação do tamanho do PDF **na frente** da prévia: a primeira prévia foi de 1,14 para 1,92 s; recusado pela regra 6 e trocado pela busca por trás, numa fila, só com o pool de prévias parado (PARTE -15 §5; `ramo fase2-para-revisar: relatorios/para-revisar-impl/ONDE-PAREI.md`).
- Medir a regra na prévia de 110 DPI: 39 vão e 60 certas (22 diferentes do estudo). Por isso a regra só mede no tamanho do PDF.
- Força sozinha com 2 linhas falhadas (antes da P3): escurecia o Palatino 66 sem precisar e piorava o Egenloff 3.

- **O mesmo código nem sempre dava a mesma imagem** (Horas 11, Mágico pro, achado em 20/10/2026): com pouca memória o modelo de regiões ficava desligado a sessão inteira e o detector de gravura caía no antigo. Provas de "sai igual" por soma podiam acusar diferença falsa. Consertado em `2ff16e7` (tenta de novo); ver [horas-011](../paginas-de-teste/horas-011.md).

## Ramos e commits

| Ramo | Commit | Data | O que fez | No `fase-1`? |
|---|---|---|---|---|
| `fase2-para-revisar` | `7695b46`, `90d0708`, `fbe0b7f` | 12/10/2026 | regra ajustada; lista e "está bom"; os botões na tela | não |
| idem | `2e400c8` | 12/10/2026 | junção do `fase-1` com o G6 (`8968704`) | — |
| idem | `8923370`, `f0d758c`, `280d40f` | 13/10/2026 | regra medida só no tamanho do PDF; ONDE-PAREI; suíte | não |
| idem | `36b9e32` | 13/10/2026 | dois limites reacertados para o livro novo | não |
| idem | `b5b224f` | 13/10/2026 | `teste_botoes`: roteiro apagava as duas páginas | não |
| idem | `027e50d` a `c19f054` | 13/10/2026 | consertos da 1ª conferência (medida, dois cliques, "está bom assim", teclado, frase da janela) | não |
| idem | `0541236` | 13/10/2026 | força sozinha P3 | não |
| idem | `a841fd0`, `36a6549`, `bdc8142`, **`ce2b835`** | 13/10/2026 | marcação do tamanho do PDF procurada por trás; ONDE-PAREI final | não |
| `verif-para-revisar-2026-10-13` | `2d820d6` | 13/10/2026 | 1ª conferência na janela (voltou ao implementador) | não |
| idem | `ba50856`, `7d205c8`, **`f506ec3`** | 13/10/2026 | 2ª conferência, parada pelo Samuel | não |

Nada deste bloco está no `fase-1` (`b8e9af7`). O ramo saiu do `fase-1` em `9c51801` e não recebeu o layout juntado em 14/10 (`ccc84aa`): ao juntar, conflitos são esperados em `ui/`. A junção com o conserto do corte do G6 é numa linha só de `core/pipeline.py` (`ramo conserto-corte-g6-2026-10-13: relatorios/conserto-corte-g6/ONDE-PAREI.md`).

- `fase2-para-revisar`: `adf4e69` (20/10/2026, junção ao layout aprovado), **`8cb84b8`** (21/10/2026). Verificação: `verif-para-revisar-2026-10-13` (retomada em 20/10/2026).

## Testes que cobrem

- No `fase-1`: [tests/test_misto_no_programa.py](../../tests/test_misto_no_programa.py) (o aviso de hoje, "Tinta forte fora do texto"), [tests/test_paineis.py](../../tests/test_paineis.py) e [tests/test_paineis_na_tela.py](../../tests/test_paineis_na_tela.py) (painel "Para revisar").
- Só no ramo `fase2-para-revisar` (não existem em W): `tests/test_revisar.py` (23 testes), `tests/test_avisos.py` (34), `tests/test_para_revisar_na_tela.py` (25), `tests/test_marcacao_por_tras.py` (4, com os fios de verdade); mexidos `tests/test_misto_no_programa.py` (41) e `tests/test_gravura_no_processamento.py` (43).
- **Testes de reversão (regra de 19/10/2026, `CLAUDE.md` §4.7):** os consertos da conferência do verificador têm testes com o nome do defeito (`test_dois_cliques_no_cartao_do_filtro_nao_dao_a_pagina_por_conferida`, `test_os_botoes_do_aviso_nao_ficam_com_o_teclado`, `test_esta_bom_assim_no_aviso_de_pagina_em_branco`, `test_usar_mais_escuro_nao_aparece_com_a_forca_ja_no_mais_escuro`), mas **nenhum foi provado falhando no código antigo** (a regra é posterior). Faltam testes de reversão para o bug `_escolher_forca` (consertado no ramo) e para a medida que dependia da prévia. O verificador que retomar precisa provar.

- 20/10/2026: 64/64 saídas iguais; suíte 2172/0; 3 testes de reversão (Registro 20/10/2026).

## Velocidade medida

- Conta da regra: 268 ms por página em média nas 89 (a mais lenta 1,09 s), só nas páginas em "Só as letras" (ONDE-PAREI do implementador).
- Medir uma página na resolução do PDF: média 3,6 a 4,4 s, mediana 2,5 a 3,0 s, pior 20 a 31 s (Antiphon 88 e 260). Livro de 300 páginas todo em "Só as letras": 13 a 15 minutos pela mediana (um fio só).
- Primeira prévia: antes de tudo 1,18 a 1,31 s; com a busca na frente 2,08 a 2,57 s (recusado); com a busca por trás **1,09 a 1,31 s**.
- Folheando com "Só as letras" (verificador, 13/10/2026): trocar de página não ficou mais lento; **o trabalho por trás depois de parar passou de 8 a 9 s para 44 a 47 s**.
- `teste_velocidade.py` no PC, Marial 300, 2 rodadas de cada (verificador, 13/10/2026): abrir, trocar de página e Preto e branco sem diferença que dê para medir; **Mágico pro 54,6 → 55,2 s em 10 páginas (+1,1%)**, os dois pares para o mesmo lado. **Exceção aceita pelo Samuel:** vai para a Fase 5 ("vamos deixar esse concerto de lentidão para o final, para a fase de desempenho.", 19/10/2026).
- O teste de velocidade não liga o "Só as letras", então não mede o custo novo (Registro 13/10/2026).

## Páginas de teste e livros

- [../paginas-de-teste/antiphonal-046.md](../paginas-de-teste/antiphonal-046.md): letra T grande que some; "Trazer de volta"; é também a página do defeito "a tela mostra o que o PDF não tem".
- [../paginas-de-teste/camoes-066.md](../paginas-de-teste/camoes-066.md): linhas pretas da beirada, "aviso no livro basta" (depende do 2.13).
- [../paginas-de-teste/camoes-104.md](../paginas-de-teste/camoes-104.md): força sozinha age (título falhado) e "figura além da gravura".
- [../paginas-de-teste/egenloff-003.md](../paginas-de-teste/egenloff-003.md): texto vermelho; a força não resolve; o limite 0,13 apoia-se numa linha dela.
- [../paginas-de-teste/egenloff-047.md](../paginas-de-teste/egenloff-047.md): tarja e moldura; "O Kaique escolhe por livro" (2.13 / 2.14).
- [../paginas-de-teste/rariora-008.md](../paginas-de-teste/rariora-008.md): página sem conteúdo, "Vai para a lista, com botão".
- [../paginas-de-teste/gladstone-018.md](../paginas-de-teste/gladstone-018.md): "Parece em branco" erra (tem título); ganhou "está bom assim".
- [../paginas-de-teste/antiphon-260.md](../paginas-de-teste/antiphon-260.md) e [../paginas-de-teste/cursus-003.md](../paginas-de-teste/cursus-003.md): duas das 5 que ainda diferem do estudo no livro novo.
- [../paginas-de-teste/matematica-032.md](../paginas-de-teste/matematica-032.md), [../paginas-de-teste/pesel-021.md](../paginas-de-teste/pesel-021.md), [../paginas-de-teste/ljs47-103.md](../paginas-de-teste/ljs47-103.md), [../paginas-de-teste/righetti-006.md](../paginas-de-teste/righetti-006.md): páginas do estudo e das rodadas 1 e 2.
- Outras do critério (sem ficha própria): Camões 27 e 11, Egenloff 12, Graduale 222, Palatino 66 e 76, Antiphonal 252, Matemática 72, Opus Majus 20. Livros: [antiphonal](../livros/antiphonal.md), [camoes](../livros/camoes.md), [egenloff](../livros/egenloff.md), [rariora](../livros/rariora.md), [gladstone](../livros/gladstone.md), [righetti](../livros/righetti.md), [graduale](../livros/graduale.md).

## Conferências

Ver também [../conferencias.md](../conferencias.md).

- 05/10/2026, conferência 8: "REVISAR Mandar para 'Para revisar' sozinho?: Sim" ([respostas](../../relatorios/conferencia-samuel-2026-10-05-f.md)).
- 06/10/2026, página de escolhas (`misto-para-revisar`): "explique melhor."; depois "Como está hoje (a partir de 10%)", "não ficou claro ainda" ([respostas](../../relatorios/conferencia-samuel-2026-10-06.md)).
- 06/10/2026, rodada 1 (17 páginas) e rodada 2 (regra "Quase: quero mudar": "ok, agora preciso saber, como vamos resolver esses problemas dentro do programa, e quero mais paginas para eu conferir, pode até pegar outros livros do hd para fazer essa conferencia, pegue mais 5 livros e me traga 30 paginas.") ([rodada 1](../../relatorios/revisar-decisoes/rodada-1/respostas-samuel.md), [rodada 2](../../relatorios/revisar-decisoes/rodada-2/respostas-samuel.md)).
- 07/10/2026, rodada 3 (37 respostas) ([respostas](../../relatorios/revisar-decisoes/rodada-3/respostas-samuel.md)).
- 08/10/2026, rodada 4 (21 respostas) ([respostas](../../relatorios/revisar-decisoes/rodada-4/respostas-samuel.md)).
- 08 e 09/10/2026, rodada 5 (10 respostas, todas `decidida`) ([respostas](../../relatorios/revisar-decisoes/rodada-5/respostas-samuel.md)).
- O resultado construído **ainda não foi conferido por ele** (aba 4 por montar).

- 21/10/2026 — aba 4 da página de conferência (https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX): 18 quadros `pr-*`, 3 perguntas, decisão `pr`. **Sem resposta.**

## Perguntas abertas

Três perguntas escritas pelo verificador no `conferencia.json` (`ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/conferencia.json`), ainda não publicadas (vão na aba 4):
1. `pr-medir-o-livro` — "Quando o programa mede as páginas que você não visitou?" (medir o livro inteiro por trás, depois de abrir — sugestão do verificador; ou medir o que falta só ao clicar em "Confirmar e processar"; ...). Hoje só a página visitada é medida (Lista de espera, 12/10/2026).
2. `pr-contagens` — "Os três números de páginas e avisos não batem. Qual deve valer?" (no Camões: painel 39, lista "Antes de processar" 75 páginas e 104 avisos, janela de salvar 106). Opções: o painel lista também os motivos de folha; a janela de salvar conta as páginas com aviso pendente (sugestão do verificador); deixar como está.
3. `pr-tela-igual-ao-pdf` — "A tela deve mostrar a página igual à do PDF?" (trocar sozinha pela imagem do PDF quando chegar — sugestão do verificador; um botão "ver como sai no PDF"; deixar como está). É a causa do bug grave de 13/10/2026.

Mais, sem pergunta montada: a aba Marcar que "se acerta sozinha" uma vez por página (Graduale 221: 9 áreas viram 18 em 10,7 s) — a gerente decide se fica (ressalva 1 do implementador); onde fica a caixinha da força sozinha (hoje só aparece rolando a tela "O que fazer").

- (21/10/2026) As três perguntas e a decisão `pr` da aba 4, sem resposta. E, para levar: "Parece em branco" — avisar uma vez para o livro inteiro quando os versos são vazios (Egenloff 49%)? ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §5).

## De onde veio

- Plano: bloco "Decidido pelo Samuel, a fazer: o 'Para revisar'" na Fase 2, acrescentado em 09/10/2026 ([plano](../../docs/plano/PLANO-DEFINITIVO.md)). Pedidos ligados: ver [../pedidos.md](../pedidos.md).
- Histórico: PARTE -11 (conferência 8), PARTE -12 §4 (estudo), PARTE -13 §2-§4 (rodadas 4 e 5), PARTE -14, PARTE -15 §2-§6, PARTE -16 §4 ([histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
- Pesquisa de onde nasceu o "Para revisar" sozinho no Misto (05/10/2026): [fase2-misto-letras-fora-do-ocr.md](../../docs/pesquisa/fase2-misto-letras-fora-do-ocr.md) (o "Só as letras" em si mora na ficha [1.5](1.5.md)).
- Relatórios: [estudo de 06/10](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md); rodadas 1 a 5 em `relatorios/revisar-decisoes/`; `ramo fase2-para-revisar: relatorios/para-revisar-impl/ONDE-PAREI.md` e `reacerto-dos-limites.md`; `ramo verif-para-revisar-2026-10-13: relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`.
- **Lista de bugs ligada** ([plano, seção 5](../../docs/plano/PLANO-DEFINITIVO.md)):
  - 06/10/2026 — o aviso "Tinta forte fora do texto" nas outras páginas só aparece ou some quando se abre a página (o painel fica atrasado); **grave:** no "Só as letras" de fábrica a parte clara de um desenho não reconhecido vai a branco (Palatino 76, Palatino 67, ljs47 103); quando o leitor não acha nenhuma linha, a página sai "Tudo em preto e branco" sem aviso.
  - 08/10/2026 — "Parece em branco. Quer apagar?" erra (aparece na Gladstone 18, que tem título; não aparece no Egenloff 12 nem na Rariora 8).
  - 12/10/2026 — marcar "letra e traço" à mão não protege a tinta do "Só as letras"; as observações do livro vão para um rótulo escondido; `[x]` "usar mais escuro" / "usar mais fraco" chamavam `_escolher_forca`, que não existia (consertado no ramo `fase2-para-revisar`).
  - 13/10/2026 — **grave:** "a tela mostra o que o PDF não tem" (letra T do Antiphonal 46; já era assim antes); **grave, do G6:** faixa preta no Cursus 3 (ver [2.2](2.2.md)); Antiphon 260 com a iluminura chapada sem aviso; Camões 66 sem aviso das linhas pretas (depende do 2.13); em 1280×657 o nome do filtro cobre a miniatura.
  - 13/10/2026, só no ONDE-PAREI do implementador (não achado na Lista de bugs do plano): o Ctrl+Z de "Ajustar o pedaço à figura" depois de a busca por trás trocar a marcação devolve as áreas da prévia marcadas como se fossem as do tamanho do PDF. Raro.
- **Entradas do Registro de mudanças** ([plano, seção 7](../../docs/plano/PLANO-DEFINITIVO.md)):
  - 05/10/2026 — conferência 8: "Para revisar" sozinho quando sobra tinta forte fora das linhas: Sim.
  - 06/10/2026 — Modo Misto juntado, com o "Para revisar" a partir de 10% até o Samuel decidir.
  - 06/10/2026 — página de escolhas: "Quando mandar a página para 'Para revisar'?": "explique melhor".
  - 06/10/2026 — "Para revisar": "Como está hoje (a partir de 10%)", mas "não ficou claro ainda".
  - 06/10/2026 — "Para revisar" continua 10%; pergunta do critério.
  - 06/10/2026 — estudo do "Para revisar" entregue.
  - 06/10/2026 — rodada 1 respondida; rodada 2 publicada.
  - 06/10/2026 — layout rodada 9 + "Para revisar" rodada 2 respondida.
  - 07/10/2026 — apagar página: dois botões ("Deixar em branco" / "Tirar do livro").
  - 07/10/2026 — layout rodada 11 + "Para revisar" rodada 3 respondida.
  - 08/10/2026 — "Para revisar" rodada 4 respondida.
  - 09/10/2026 — "Para revisar" rodada 5 respondida.
  - 09/10/2026 — plano posto em dia (o bloco entra no plano).
  - 12/10/2026 — agentes postos a trabalhar: implementador no ramo `fase2-para-revisar`.
  - 13/10/2026 — construído no ramo (`280d40f`), PRONTO PARA CONFERIR, limites a reacertar.
  - 13/10/2026 — parecer do verificador na janela (`36b9e32`): voltou ao implementador.
  - 13/10/2026 — consertos e dois ajustes (`ce2b835`), de volta ao verificador; as três perguntas.
  - 13/10/2026 — segunda conferência do verificador feita; Mágico pro 1,1% mais lento, a decidir.
  - 19/10/2026 — verificador liberado; Mágico pro +1,1% para a Fase 5.

- 20/10/2026 — Registro "Layout, rodada 14" ("Para revisar" juntado ao layout aprovado, `adf4e69`) e "Exceção à regra da suíte no PC"; 21/10/2026 — Registro "Pausa pedida pelo Samuel"; [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §2, §4, §5.
