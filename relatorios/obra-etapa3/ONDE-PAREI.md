# Obra de 26/10/2026 — etapa 3 (layout + core): ONDE PAREI

Ramo `obra-etapa3-2026-10-26` (base `obra-2026-10-26` = `fdabf0d`, com as etapas 1, 2 e 9a), worktree
`.claude/worktrees/obra-etapa3`. Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo no fim.

**Situação: EM ANDAMENTO** (começado em 26/10/2026, noite).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-002 (25/09) + Kaique 22/09 + 26/10 | "Trabalho automático = painel 'Automático' que abre e fecha (substitui a tela 7). [...] Funciona antes/ao abrir o livro e depois, na área de trabalho (ex.: abrir o PDF sem mexer e rodar as etapas depois)." · Kaique: "Essa pagina não era mais para aparecer – nós tínhamos que abrir direto na área de trabalho" · 26/10: "eu quero poder sim fazer automatico para todo livro, mas também quero pode fazer uma a uma." | O livro abre direto na área de trabalho; a tela "Marque o que você quer fazer" sai do caminho; painel Automático + janela grande, que roda no livro todo, em páginas escolhidas, numa página só ou uma etapa só, ao abrir ou depois. |
| Tudo de "O que fazer" | (pedido da gerente, auditoria de 26/10; rodada 2 nº 5 "Aprovado": "Ter as duas: painel (opção 1) com botão que abre a janela (opção 2). Escolher folhas abrindo a tela de todas as páginas (marcar/desmarcar). Na janela, ver a página ao lado, folhear e dar zoom.") | Grupos Página · Limpeza · Gravuras e fotos · Saída; molduras no Preto e branco; "Tirar o fundo"; jeito de dividir; conta do endireitar; G2; g7/g8; pergunta do fundo; borda preta; reforçar texto falhado; "Só as letras". Lista única 2.2, 2.7, 5.2, 5.3, 5.11. |
| D-003 (28/09) / D-016 (escolha D-014) | "Ordem das etapas: livre. [...] muda arrastando com o mouse. Sem cadeados." | Arrastar muda a ordem em que as etapas RODAM; a montagem da página segue a ordem obrigatória. |
| D-004 (28/09) | "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." | Rodar em livro com páginas mexidas pergunta; "pular" mantém essas páginas. |
| Marca "mexida à mão" (etapa 1) | (D-009, 26/10: "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente.") | Toda edição à mão (corte, ângulo, filtro da página, marcação, dividir/linha, mover, girar) grava a marca. |
| D-071 / D-355 (`fr-219`, 22/10) | "Está bom" + "Mas ainda pode melhorar a caixa de como escolhemos o que vai dentro da receita." | Receitas guardar/pôr/apagar no Automático, caixa do "o que vai na receita" mais clara; "Receita usada" no livro aberto. |
| D-005 (12/10) + D-018 (escolha D-014) | "B — Um aviso embaixo da página" ("Livro novo: ainda não passou pelo automático", "Rodar o automático…", "agora não") | Livro novo mostra o aviso; "Rodar o automático…" abre a janela grande com a receita de sempre marcada. |
| D-284 (`pr-medir-o-livro`, 21/10) + 29/09 | "Medir o livro inteiro por trás, depois de abrir" · "Página sempre abre em 'Original', sem mexer." | Ao abrir, passada leve; medição completa por trás só guardando; nenhuma página muda até rodar o automático. |
| D-334 (24/09) | "Ver todas as páginas do livro em grade, como o 'Organizar páginas' do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir." | Grade com várias escolhidas e ações; é onde "rodar em escolhidas" escolhe. |
| D-093 / D-094 (09/10) | `g6-retangulo`: "Fica no mesmo lugar da página (como no ScanTailor)" + "Posso ter as duas opções mas a opção do scantailor ficar como padrão?" · `g6-retangulo-onde`: "Na ferramenta Endireitar, por página" + "quero a b e c juntas." | "Fica no mesmo lugar / Acompanha o texto" em Configurações, no livro (janela do Automático) e na página (Endireitar). |
| Livro aberto (R6, 06/10) | "Sim, fica assim" | "Rodar o automático…" abre o Automático de verdade; "Para revisar" e "Receita usada". |
| Defeito de 29/09 + teste do Kaique 26/10 (tarefas 7 e 8) | (opções jogadas fora em livro já conferido) | O Automático grava no projeto aberto; mudar uma etapa num livro conferido vale e nada se perde; fica no Histórico/`acoes.jsonl`. "Só endireitar" não corta; "Preto e branco" vale. |
| D-068 (24/09) | "Toda função automática tem botão de ligar e desligar." | Cada etapa do Automático liga e desliga. |
| D-069 (30/09) | F5: a pergunta do fundo também dentro do programa, depois de abrir o livro, e a opção de voltar ao original | "Tirar o fundo" e "voltar ao original" com o livro aberto. |
| D-135 (29/09) | "Ao abrir um livro com camadas, o programa pode avisar: 'Este livro tem fundo separado. Quer tirar o fundo?'" · "De acordo" | A pergunta continua ao abrir direto na área de trabalho. |
| D-075, D-080, D-081, D-082, D-092, D-101, D-144, D-148, D-168, D-175, D-186/D-277, D-195, D-212, D-213 | (ver o Livro) | Cada opção que morava em "O que fazer" continua existindo, agora no Automático. |
| Atalhos (pergunta da etapa 2) | o Samuel quer "como o Photoshop" | Letras para Dividir, Cortar e Endireitar, sem conflito. |

## Plano (como vou fazer)

1. `core/etapas.py`: o automático também por página (`ConfigPagina.automatico`), além da caixinha do livro.
2. `core/automatico.py` (novo): as etapas, a ordem, o pedido (etapas + opções + páginas), as páginas mexidas, a
   medida (por trás) e o aplicar no projeto aberto, com a ação do Histórico.
3. Janela: abre direto na área de trabalho (passada leve; trabalho salvo volta sem análise nova), medição por trás,
   aviso do livro novo, painel Automático de verdade, janela grande, grade com várias escolhidas, pergunta das
   mexidas, marca "mexida à mão", retângulo do corte nos 3 lugares, letras dos atalhos.
4. Provas em `tests/test_decisoes_automatico.py`; testes antigos adaptados ao caminho novo.

## Escolhas da gerente (D-014) feitas aqui

(preenchido no fim)

## Passos

- [ ] núcleo (etapas por página, automatico.py, histórico)
- [ ] abrir direto na área de trabalho + medição por trás
- [ ] painel + janela grande + receitas
- [ ] grade com várias escolhidas
- [ ] pergunta das mexidas + marca mexida à mão
- [ ] retângulo do corte (3 lugares), atalhos
- [ ] livro aberto da tela inicial
- [ ] provas e testes antigos adaptados
- [ ] prints, velocidade, ONDE-PAREI final

## Perguntas para o Samuel

(nenhuma ainda)
