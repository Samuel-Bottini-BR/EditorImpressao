# Obra de 26/10/2026 — etapa 9b-1 (menus, impressão, janelas e lado direito): ONDE PAREI

Ramo `obra-etapa9b1-2026-10-26` (base `obra-2026-10-26` = `27b4c52`), worktree `.claude/worktrees/obra-etapa9b1`.
Agente: layout + implementador. Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha mandado, fazer as
ferramentas que colocamos no programa funcionem como deveriam e como eu tinha escolhido."

**Situação: EM ANDAMENTO** (começada em 27/10/2026).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Item | Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|---|
| 1 | Auditoria C3 · `fr-26` (22/10) / D-333 | "Está bom" + "Só tem que melhorar esse layout, cheio de letras uma em cima da outra, tudo bagunçado e dificil de saber o que é o que." | Disposição nova (duas colunas) fica; os NOMES voltam aos de antes. |
| 1 | D-315 (14/10) | "todas as outras opções que aparecem nos prints do PDF que mandei. Quero TODAS essas opções dentro do programa" · `fr22`: APROVADO | Os nomes das opções do UPDF, como estavam no `fase-1`. |
| 1 | D-374 (22/10) | "Anote a ideia de depois revisarmos todos os nomes de botão com um novo agente que vai ser criado." | Nome novo só pela revisão de nomes (etapa 11), decidido por ele. |
| 2 | D-033 (05/10) · R14 902 (20/10) | "Quer os quatro jeitos no app, escolhendo dentro dele: sanfona (o primeiro), abas no alto, ícones na borda, painel flutuante" · `r14-lado-direito-onde`: "C — Nos dois lugares" | Os 4 jeitos no menu Ver > "Lado direito" e em Configurações > Aparência. |
| 2 | R7 203 D (rodada 7) | "Ícones na borda, tudo fechado" + "Mas eu também quero ter a opção da area de trabalho 1." | Ícones na borda continua o de fábrica. |
| 3 | D-492 (27/10, escolha da gerente) · P-085 | "o botão tem que ser provado que ele faz o que se diz" | O tique do menu Filtro acompanha o filtro da página aberta. |
| 4 | D-274 (08/10) · P-127 | "quando alguém tentar imprimir sem ver os alertas o programa para e mostra os alertas e a pessoa diz se quer ver ou continuar" | Menu Arquivo > "Confirmar e processar" (Ctrl+Return) passa pela "Antes de processar", igual ao botão. |
| 5 | D-555 (27/10) | Central `ac-nome-sem-acento`: "Voltar com acento (recomendo)" | Nome sugerido do PDF com acento ("Ofício da Imaculada Conceição - mágico pro.pdf"). |
| 5 | D-365 (18/07) | "Corrija TODOS os textos da interface para português correto" | — |
| 6 | D-283 (21-22/10) · `lm22` | `pr-antes-de-processar`: "Melhorar" + "ficou meio embolado, deve ficar mais claro e não tão grande." · `lm-antes-de-processar`: "Está bom" / `lm22` "Aprovado" (com o "Mostrar" cortado a consertar) | "Antes de processar" do commit `138e425`, e o motivo inteiro no "Mostrar". |
| 6 | D-061 (21-23/10) | `lm22`: "Aprovado" | Trabalho aprovado vai para o programa como estava. |
| 6 | D-285 (21/10) · etapa 7 | `pr-contagens`: "A janela de salvar passa a contar as páginas com aviso pendente" | A contagem da etapa 7 continua (um número só). |
| 7 | D-250 (22/10) | `fr-218-aviso`: "A — Avisar (recomendo)" · no chat: "1- sim" | "Pintar por cima" sobre letras → aviso com "Pintar assim mesmo" e "Voltar"; nada pintado sem confirmar. |
| 8 | D-561 (27/10) | Central `ac-letras`: "Manter (recomendo)" — D, X, I, F, Shift+Del | As teclas não mudam; só passam a chegar à página com o foco na lista do Automático. |
| 9 | D-057 (20-21/10) | `r14-menu-paineis`: "B — Um menu novo, “Painéis”" · `ly-paineis`: "Está bom" | Os "Painel: …" saíram do Ver para o menu Painéis; cada item abre o painel. |
| 9 | D-020 (18/07) · P-125 | "13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz" | Desfazer apagado sem nada para desfazer (barra de baixo e menu). |
| 9 | D-309 (05/10) | "pode mandar concertar, mas continue com a fase 2 em paralelo" | O cartão só diz "PDF gerado" quando o PDF é o do trabalho de agora. |
| 9 | D-342 (05/10) | "o programa quando estiver pronto, ele vai ter que ser capaz de abrir arquivos de versões anteriores." | `projeto.json` ilegível: cópia guardada e aviso na tela. |
| 10 | D-045 (06/10) · D-015 (22/10) · etapa 7 ressalva 1 | R9 405: "C — Os dois" · "Uma página / Duas lado a lado" na barra de baixo | Barra de baixo com tudo o que tem; o contador inteiro a 1280 com painel aberto, sem tirar nada. |
| 11 | D-272 · D-280 · P-092 · P-094 | "com todas as paginas ou com todos os motivos" | Testes estáveis sem mudar o programa só para o teste passar. |

## Andamento

(preenchido a cada passo)
