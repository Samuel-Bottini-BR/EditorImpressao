# Relatório da sessão com o Fable — Editor de Impressão

23/11/2026, 18:23 às 19:36 (horário de Campo Grande). Escrito pelo Fable 5.1 (claude.ai) a pedido do Samuel, para ser entregue a outra IA. Linguagem técnica onde precisa, com o contexto que uma IA de fora precisa para continuar.

## 1. O que foi pedido ao Fable

Auditoria externa do projeto Editor de Impressão (app Windows em Python 3.14 + PySide6 que restaura PDFs de livros antigos escaneados para reimpressão). O Samuel entregou um relatório de 981 linhas (`relatorios/para-o-fable-2026-11-23/relatorio-para-o-fable.md`, no repositório `Samuel-Bottini-BR/EditorImpressao`) com 6 perguntas na Parte 5, e três regras para a resposta: nada de regra nova no `CLAUDE.md`, checklist ou documento; só estrutura de código, desenho e travas mecânicas (código/teste que impossibilita o erro); separar certeza (visto no código) de palpite.

Contexto resumido do relatório: há um mês cada volta de conserto cria erros novos. O atualizador (Velopack) levou 4 voltas e ainda tem 5 problemas médios. No programa, uma revisão de 10/11 achou 17 remendos e 16 continuam. A resposta de cada falha foi escrever regra nova (o `CLAUDE.md` tem 71 KB). A D-765 (17/11) congelou todo conserto do programa até o `.exe` ser entregue ao Kaique, o usuário final.

## 2. O que o Fable fez

- Leu o relatório inteiro.
- Pediu acesso à pasta `D:\programas\EditorImpressao` e conferiu o código **nos objetos git dos commits citados** (`0f58346a` = programa, ramo `obra-2026-10-26`; `aa1963b7` = atualizador, ramo `atualizador-4-consertos-2026-11-21`), porque o checkout local está no `fase-1`, desatualizado.
- Abriu, além do que o relatório citava: `modelos.py`, `core/girar.py`, `core/automatico.py`, `ui/tela_ampliada.py`, `ui/desfazer_nesta_pagina.py`, cabeçalho de `core/windows.py`, `core/_testes_a_distancia_windows.py`, `tests/test_atualizador_volta4.py`, `regras_dos_agentes/porteiro.py`, `tests/conferencias_excecoes.json`, e depois os dois commits da trava nova (`0f3598a1`, `d792ebfc`).
- Gravou a auditoria em `relatorios/para-o-fable-2026-11-23/resposta-do-fable.md` (no repositório).
- Explicou tudo em linguagem leiga ao Samuel e respondeu, em duas rodadas, às dúvidas levantadas pelo agente do Claude Code que escreveu a trava.

## 3. Os achados (certezas, conferidas no código)

**Achado novo, que o relatório não trazia:** os testes do atualizador testam texto, não comportamento. `tests/test_atualizador_volta4.py` faz `assert "MarcaExiste" in lancados[0]` — confere que a string do PowerShell contém uma palavra. Por isso um revisor pôde estragar uma linha de propósito e os 55 testes continuaram passando.

**Atualizador (`atualizacao.py`, 2.314 linhas):** 256 linhas são literais de string montando PowerShell; 3 mutexes globais; `estado.json` como canal entre a conta SYSTEM e a do Kaique; 7 processos em duas contas para um "Reiniciar agora". Causa raiz: quem troca a versão é o próprio `EditorImpressao.exe` da pasta `current`, rodando como SYSTEM — ele tem de sair antes da troca, e daí vêm vigia, marcas, scripts de reabrir, lista de processos. Os 5 problemas médios do relatório 3 moram em peças que só existem para proteger outras peças.

**Testes à distância:** `core/_testes_a_distancia_windows.py` ainda tem um `runas` próprio com `ctypes.windll` e `get_last_error()` sem `use_last_error` (o "Não" do UAC vira sucesso). A peça única `core/windows.py` já tem as funções certas (`pedir_licenca`, `passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa`) e nunca foi usada pelo ligar/desligar.

**Programa (`ui/tela_conferir.py`, 10.187 linhas, 398 métodos):**
- A lista "o que vai junto no Aplicar em" está escrita à mão em quatro lugares: `_campos_do_aplicar_em` (L9133), `CAMPOS_DA_PAGINA` (`core/automatico.py` L149), `MARCAS_DA_PAGINA` (L10152), mais perfis e chave das prévias. `claro_no_escuro` está em duas e falta na terceira.
- A ação do desfazer é montada em 4 lugares: `tela_conferir.py` L2266, L5955 (`_registrar`), L9512 e `ui/desfazer_nesta_pagina.py`. `_registrar` carrega regra de domínio dentro da UI.
- Girar: 14 métodos na tela; `(rotacao + giro) % 360` à mão em L7322 e L7382 enquanto `girar.nova_rotacao` existe em `core/girar.py` L170.
- Três renderizações do "como fica com este filtro": `_filtrar_a_pagina` (pipeline L3437), `filtro_com_as_caixinhas` (L3546), `_imagem_do_outro_filtro` (`tela_ampliada.py` L304, sem marcação nem "Só as letras").
- 10 dos 16 remendos conhecidos (A1–A4, M1, M2, M5, M6, M7, M9) são instâncias do mesmo problema: regra em mais de um lugar.

**Porteiro (barreira automática):** K01 é lista de regex (`PALAVRAS_DO_WINDOWS`); lista de palavras vaza por construção (`New-Item` passou). 164 exceções concentradas em 4 arquivos.

**Repositório:** 1.206 commits e +29.584 linhas de `core/`+`ui/` no `obra-2026-10-26` que nunca entraram no `fase-1`; 200 worktrees dentro de `.claude/worktrees/` (um `grep -r` na raiz estourou 120 s).

## 4. As respostas às 6 perguntas (resumo)

1. **Atualizador:** refazer, não consertar os 5 médios. Desenho: nenhum processo nosso fora da sessão do Kaique. Na primeira abertura, um único UAC (D-733, jeito 1) dá a Users permissão Modificar na raiz da instalação do Velopack; dali em diante o próprio programa, na conta do Kaique, faz `check_for_updates` → `download_updates` → `apply_updates_and_restart` ("Reiniciar agora") ou `wait_exit_then_apply_updates` ("Depois"). D-736 (mandar de longe): por SSH, `EditorImpressao.exe --baixar-atualizacao` baixa e deixa pronto; a troca acontece na próxima abertura. Some: ajudante SYSTEM, 2 scripts PowerShell, vigia, 3 mutexes, `estado.json`, lista de processos. Plano B se o experimento falhar: tarefa SYSTEM que chama só `Update.exe apply --waitPid`, nunca o nosso exe.
2. **Por que o ciclo se repete:** a regra não mora num lugar só; cada decisão vira um `if` no método onde o print apareceu. Refatoração mínima (~3 dias, depois da entrega): (1) metadados nos campos de `ConfigPagina`/`ConfigFolha`, listas derivadas de `dataclasses.fields()`, teste que falha se faltar classificação; (2) porta única `core/comandos.py` com `executar(projeto, acoes, comando) -> Efeitos`, teste de AST que só permite `montar_acao` em um arquivo; (3) uma renderização, teste de pixels comparando os três caminhos.
3. **Peso das regras:** converter cada regra da §11 que pode virar teste em teste e apagar o texto; mutação automática (`mutmut`) no lugar do "desligar proteções à mão".
4. **Porteiro:** conferência estrutural (AST) em vez de palavras; exceções somem ao conformar os 4 arquivos; gate rápido no CI (core sem Qt, < 2 min).
5. **16 remendos:** ordem certa, mas o descongelamento começa pela estrutura (refatorações 1–3), não pelos sintomas.
6. **Não perguntado:** o `obra` é o tronco de fato; os worktrees dentro do repositório; falta a trava inversa "`ui/` não monta `campos`".

Limite honesto dado ao Samuel: isso resolve o retrabalho "consertei aqui, quebrou ao lado". Não resolve pedido que muda depois de pronto nem agente que dá como feito o que não conferiu.

## 5. O que foi pedido ao Claude Code (pela gerente) e o que aconteceu

A gerente é a sessão do Claude Code que coordena os agentes. O Samuel levou a ela as mensagens do Fable; ela mandou dois agentes.

### Agente 1 — Passo a passo do experimento (em andamento)
Pedido: preparar, sem rodar nada, o experimento de 10 minutos que decide o desenho do atualizador: (1) como administrador, `icacls "C:\Program Files\EditorImpressaoPrograma" /grant *S-1-5-32-545:(OI)(CI)M /T`; (2) como conta comum, o fluxo normal do Velopack dentro do programa; (3) registrar se o download gravou em `packages\`, se `Update.exe` renomeou `current` sem UAC, se o programa reabriu na conta certa; (4) repetir com o programa fechado. Nenhuma linha de `atualizacao.py` muda. A gerente acrescentou: o Samuel precisa estar no PC (é ele quem clica no UAC), as tarefas sobradas da prova de 22/11 têm de sair antes, e deve haver instrução de desfazer. **Situação: o agente ainda estava escrevendo o passo a passo ao fim da sessão.**

### Agente 2 — A primeira trava (duas voltas, concluídas)
Pedido: um teste em `tests/` que falha quando código fora de `core/windows.py` fala com o Windows. Falhar hoje de propósito: a lista do que falha é a lista de trabalho do atualizador novo. Nada do programa muda (D-765).

**Volta 1** (commit `0f3598a1`, ramo `atualizador-novo-2026-11-23`): `tests/test_trava_windows.py`, lê o AST, sem exceções, acusa 62 lugares. **Deu certo:** a trava funciona e tem provas próprias; a separação dos 62 (Windows de verdade / não é Windows / dúvida) estava correta. **Deu errado (na regra do Fable, não no agente):** a regra "só `core/windows.py` pode importar `ctypes`/`subprocess`" misturava três coisas diferentes — falar com o Windows, carregar as DLLs do ScanTailor compiladas pelo projeto, e abrir processos nossos (OCR, Kraken, servidor de páginas). O agente levantou 7 pontos em que a regra não fechava (Kraken em dois arquivos; `import ctypes` só para tipos em 8 arquivos; imports sem uso; "CDLL de `core/nativo/`" não se confere por AST; nomes faltando; lista de arquivos vs. "sem exceções"; scripts de montar).

**Resposta do Fable aos 7:** trocar "qual import é permitido" por "quem é o dono da capacidade". Três donos: `core/windows.py` (Windows), `core/nativo_dll.py` (DLLs nossas, arquivo a criar depois), `core/processos.py` (processos nossos, a criar depois). Escopo = fechamento de imports a partir de `main.py`, para os scripts de montar caírem fora sozinhos. `os.system/popen/spawn*/exec*` proibidos em todo lugar. E — **erro do Fable** — `xfail(strict=True)` para a rodada do GitHub não ficar vermelha.

**Volta 2** (commit `d792ebfc`): três donos, fechamento a partir de `main.py` (121 arquivos), `xfail(strict=True)`. Acusa 34 lugares (10 atualizador/testes à distância; 6 Windows em outras partes; 12 DLL nossa; 5 processo nosso; 1 no próprio `core/windows.py`). Saíram 31 scripts. **Deu certo:** a lista agora é só o que vai ao Kaique. **Deu errado:** o agente achou 5 pontos; o mais grave, apontado corretamente, é que o `xfail` esconde lugar novo — 34 ou 40 lugares, "falhou como esperado"; a trava só voltaria a cobrar quando a lista zerasse.

**Resposta do Fable aos 5 (última mensagem da sessão, ainda não executada):**
1. `core/windows.py` ganha `subprocess` (precisa rodar `schtasks`, `icacls`, PowerShell). Dois arquivos importam `subprocess`, com capacidades separadas em execução: `windows.py` só lança programas da pasta do Windows (regra que já tem), `processos.py` só lança programas nossos (teste espelho). Não fazer um repassar ao outro. `explorer /select` do `historico.py` vira função da peça do Windows.
2. `os.system/popen/spawn/exec` proibidos até nos donos — está certo, manter.
3. Dentro de `core/nativo_dll.py`, acusar por nome `windll`, `WinDLL`, `oledll`, `OleDLL`, `wintypes`, `get_last_error`, `FormatError`, `GetLastError`; ligar o teste de execução (hoje `skipped`) que confere que todo `CDLL` carrega de `core/nativo/`.
4. Raízes do fechamento: `main.py`, `motor_kraken/servidor_kraken.py` e a lista de `--hidden-import` lida do próprio `empacotar.py` (derivada, não listada).
5. **Trocar o `xfail` por uma catraca:** a lista dos 34 congelada dentro do teste, linha por linha, com `TETO = 34`. O teste falha se aparecer lugar fora da lista (nenhum lugar novo passa) e falha se um lugar da lista deixou de ser acusado sem ser removido ("tire da lista e abaixe o teto"). A lista só encolhe, no mesmo commit do conserto. Quando chegar a zero, lista e teto saem.

## 6. O que foi decidido pelo Samuel

- **"refazer"** (23/11, 18:50; registrado pela gerente como D-830): o atualizador será refeito no desenho simples **antes** de entregar ao Kaique, e não a volta 4 consertada. A D-765 continua valendo para o programa.
- Confirmado com o Samuel, em linguagem leiga: nada do programa é refeito do zero, nunca. Só `atualizacao.py` é reescrito; as refatorações do programa são dentro do código existente, com os 4.668 testes rodando, e só depois da entrega.
- Mandar dois agentes em paralelo (experimento + trava) foi considerado correto pelo Fable: são independentes e nenhum mexe no programa.
- Na Central, a pergunta sobre os três donos deve ir com a opção (2) do implementador ("um arquivo para as DLLs e outro para os processos nossos") como recomendada.

## 7. Onde parou, e o próximo passo

1. **Pendente (Claude Code):** ajustar o teste da trava conforme a resposta aos 5 pontos — catraca no lugar do `xfail`, `subprocess` em `windows.py`, nomes proibidos no dono das DLLs, raízes do fechamento. Só o teste muda.
2. **Pendente (Samuel no PC):** o experimento de 10 minutos, quando o passo a passo ficar pronto. Resultado esperado em uma frase: "a troca funcionou sem administrador" ou "parou no passo N com a mensagem X".
3. **Depois do experimento:** ramo novo do atualizador no desenho simples (ou plano B), com as duas travas; testes à distância pela peça única; entrega ao Kaique.
4. **Depois da entrega:** refatorações 1–3 do programa, nesta ordem; só então os 6 remendos independentes (M3, M4, M8, B1, B3, B4) e a fila de bugs.

## 8. Avisos para quem continuar

- Desconfiar de conserto que **acrescenta** arquivo ou camada em vez de tirar — em especial um arquivo novo que só repassa chamadas para contornar a trava.
- O mapa de donos tem 3 entradas. Se crescer "porque este caso era especial", virou a lista de exceções com outro nome.
- "Os testes passam" não vale para o atualizador atual: eles conferem substrings de script.
- Arquivos de referência: `relatorios/para-o-fable-2026-11-23/relatorio-para-o-fable.md` (o relatório original), `resposta-do-fable.md` (a auditoria), `relatorios/atualizador-novo/ONDE-PAREI.md` (as duas voltas da trava, com os 62 e os 34 lugares linha por linha), `tests/test_trava_windows.py`.
