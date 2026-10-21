# Onde parei: Fase 2, itens que faltam, igual ao ScanTailor (implementador)

Pedido da gerente em 20/10/2026. Ramo `fase2-scantailor-itens-2026-10-19` (do `origin/fase-1` em `b8e9af7`),
worktree `D:\programas\EditorImpressao\.claude\worktrees\fase2-itens` (junções: `modelos`, `gabarito\paginas`,
`gabarito\scantailor-24-09` — nunca `Remove-Item -Recurse` nelas).

Regra (Samuel, 13/10): igual ao ScanTailor, ajustes de fábrica dele, desligado de fábrica quando muda a imagem.
Decisões já tomadas que valem aqui (conferência 10, 05/10, `relatorios/conferencia-samuel-2026-10-05-b.md`):
P8 (b) "Trazer os dez do ScanTailor como opções a mais"; P9 (a) caixinha por página "Letra clara em fundo escuro",
à mão; P10 (a) "letras com a cor delas" como opção desligada de fábrica.

Ordem (D1 de 02/10, depois a lista da gerente): 2.8 → 2.9 → 2.11 → 2.15 → 2.12 → 2.16 → 2.19 → 2.17.

## Estado por item

| Item | Estado | Commits | Rodada do GitHub |
|---|---|---|---|
| 2.8 preto e branco (os dez do ScanTailor) | **entregue à gerente** (falta verificador e Samuel) | `77e9446` (core), `34b3d0e` (tela), `b36b540` (script) | 39395632426: 2084 passaram, 0 falharam; botões 221 ações, 0 falhas |
| 2.9 claro no escuro | **entregue à gerente** | `4cec7a9` (core), `0f4ee58` (tela) | 39470347203: 2097 passaram, 0 falharam; botões 221 ações, 0 falhas |
| 2.11 cores | **entregue à gerente** | `b7dcc14`, `40a5ce1` (core), `02c2cea` (tela) | 39474481779: 2109 passaram, 0 falharam; botões 221, 0 falhas |
| 2.15 páginas diferentes | **entregue à gerente, com uma pergunta** (calibragem) | `a8b1b2e` | 39553730620: 2124 passaram, 0 falharam; botões 221, 0 falhas |
| 2.12 desentortar | não começado | | |
| 2.16 todos os núcleos | não começado | | |
| 2.19 unidades e perfis | não começado | | |
| 2.17 iluminação e suavizar | não começado | | |

## Anotações

- `memoria/` ainda não existe no `fase-1` (20/10): nada a ler.
- Filtro de velocidade do GitHub (antes x depois) ainda **não existe**: outro agente está montando
  (`ONDE-PAREI-filtro-velocidade.md` no ramo `claude/list-server-files-gkos8v`, passo 1 de 9).
- A DLL `st_ferramentas` também muda no ramo `fase2-caixa-conteudo` (versão 4, não juntado). Aqui a versão
  pula para 5, para não brigar; quem juntar os dois recompila a DLL (`compilar_st_ferramentas.py`).

## 2.8 — o que foi feito e onde olhar

- Os dez jeitos do ScanTailor (Otsu, Sauvola, Wolf, Fox, Window, Bradley, Grad, EdgePlus, BlurDiv, EdgeDiv), com o
  código dele (`ligacao-ferramentas/saida.cpp`, `core/preto_e_branco_scantailor.py`), como opções a mais na lista
  "Algoritmo" da aba Filtro. De fábrica continua "Automático".
- Prova de "desligado de fábrica": `2.8/somas-antigo.json` (código `b8e9af7`) = `2.8/somas-novo.json` nas 32 páginas
  do gabarito × Original, Preto e branco, Melhorar (96 de 96 iguais, ponto a ponto).
- Antes/depois (Original · Hoje · Otsu ST · Sauvola ST · Wolf ST), 32 páginas + recorte ampliado de cada:
  `relatorios/conferir/fase2-itens/2.8/` (fora do git, só neste PC). Números por página: `2.8/numeros/`.
  Script: `scripts/rodada_gabarito.py` (uma página por processo; `scripts/rodar_todas.sh` roda as 32).
- Horas 13 falhou uma vez por falta de memória do PC (outros agentes); rodada de novo sozinha, deu certo.

## 2.9 — o que foi feito e onde olhar

- Caixinha por página "Letra clara em fundo escuro" (aba Filtro, bloco AJUSTE). Igual ao ScanTailor: inverte na
  entrada, caminho de sempre, inverte no fim. Desmarcada de fábrica.
- Prova de fábrica: `2.9/somas-novo.json` = `2.8/somas-antigo.json` (código `b8e9af7`), 96 de 96.
- Página de verdade achada no acervo (script `scripts/procurar_claro_no_escuro.py`, 14 livros lidos): só uma,
  Livro de Horas p. 187 (a lombada de couro escuro com "HEURES DE LOVIS XIV" dourado). Antes/depois em
  `relatorios/conferir/fase2-itens/2.9/` (fora do git), números em `2.9/numeros/`.
- Filtro de velocidade do GitHub (b8e9af7 x 0f4ee58): rodada 39470417724, disparada.

## 2.11 — o que foi feito e onde olhar

- "Letras com a cor delas" (só Preto e branco) e "Reduzir cores", por página, desmarcadas de fábrica
  (`core/cores_scantailor.py`, `st_ferramentas_cores` na DLL versão 6).
- Prova de fábrica: `2.11/somas-novo.json` = `2.8/somas-antigo.json`, 96 de 96.
- Antes/depois em 7 páginas com cor (Horas 13, 26, 27, 47; Graduale 221; Palatino 67; Escola 7):
  `relatorios/conferir/fase2-itens/2.11/` (fora do git); números em `2.11/numeros/`.
- Próximo: 2.15 (destacar páginas diferentes).

## Conserto pedido pela gerente (verificador do 2.8): falha do ScanTailor no erros.log

`ba5eefe`: os quatro "avisar uma vez" (preto e branco, endireitar, limpar pontinhos, cores do ScanTailor) gravam
com `registro.registrar_erro` (`st_ferramentas.anotar_no_erros_log`). Teste de reversão
`tests/test_falha_do_scantailor_vai_ao_erros_log.py`: 5 falharam no código antigo, 5 passam no novo.
Suíte GitHub 39478778828: 2114 passaram, 0 falharam; botões 221 ações, 0 falhas.

## Velocidade (filtro do GitHub, rodada 39470417724: `b8e9af7` x `0f4ee58` = 2.8 + 2.9)

Veredito "igual (dentro do vai-e-vem)": abrir 36,2 → 36,3 s; trocar de página 1,99 → 1,97 s; Mágico pro 43,9 → 42,5 s;
Preto e branco 20,9 → 20,9 s. O 2.11 (`02c2cea`) ainda não passou no filtro.

## PAUSA (20/10, ~15h no PC) — pedida pela gerente para a suíte no PC

Parei num ponto limpo: tudo commitado e enviado, nada rodando no PC. Ao retomar:
1. disparar o filtro de velocidade `b8e9af7` x último commit (cobre 2.11 e o conserto do log);
2. entregar o 2.11 à gerente (já pronto: ver a seção do 2.11);
3. seguir com o 2.15 (destacar páginas diferentes: DeviationProvider.h do ScanTailor).

## Retomada (21/10)

- Velocidade do 2.11 + conserto do log (39482416807, `b8e9af7` x `d490c61`): "igual" (abrir 60,4 → 60,6 s).
- Velocidade do 2.15 (39553741406, `d490c61` x `a8b1b2e`): disparada, resultado ainda não lido.

## 2.15 — o que foi feito e a pergunta

- `core/paginas_diferentes.py` (DeviationProvider.h em Python, fábrica do ScanTailor). Só o ângulo do endireitar:
  conteúdo (2.5) e margens (2.4) estão em `fase2-caixa-conteudo`, fora do `fase-1`; as contas deles já estão prontas.
- Aviso "Inclinação diferente das outras" posto na análise (livro novo); não muda imagem.
- Contagem (`2.15/livro1..5.json`): Boécio 9/50 (18%), Palatino 8/134 (6%), Siebmacher 8/134 (6%),
  Horas 15/191 (7,8%), Catecismo 33/199 (16,6%: páginas com só 0,4° a 0,9°, desvio do livro 0,28°).
- **Pergunta:** dois livros passam da regra "menos de 10% das páginas" (core/analise.py). No ScanTailor é só um
  asterisco; aqui vai para "Para revisar". Ver a entrega à gerente.
