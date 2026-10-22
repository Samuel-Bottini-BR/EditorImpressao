# O PC do Samuel, o GitHub e a velocidade

Montado em 20/10/2026. Fontes: [CLAUDE.md §3 e §4.6](../../CLAUDE.md), [plano, Registro de mudanças](../../docs/plano/PLANO-DEFINITIVO.md)
(28/09/2026 a 19/10/2026) e a Lista de bugs, as PARTES -16 a -8 do
[histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), os relatórios de velocidade em
`relatorios/` e o `ONDE-PAREI-filtro-velocidade.md` do ramo `claude/list-server-files-gkos8v`. O software instalado está
em [ambiente.md](ambiente.md). **O plano manda**; esta ficha só junta o que está espalhado.

---

## 1. O PC do Samuel (SAMUEL-PC)

- É um **notebook**: AMD Ryzen 7 5800H (8 núcleos, 16 lógicos), **16 GB de RAM, 15,4 GB disponíveis** para o Windows,
  Windows 11 Home 25H2 (relatório de velocidade de 26/09/2026, `relatorios/velocidade/velocidade-SAMUEL-PC-2026-09-26-1305.md`).
  As medições valem **na tomada**.
- **Placa de vídeo: GTX 1650 4 GB, sem tensor cores** — "nada que dependa de float16 rápido" ([CLAUDE.md §3](../../CLAUDE.md)).
  Há também a Radeon integrada.
- **O D: é um HD USB giratório (WD easystore)** (PARTE -11 §4): lento, e "pode desconectar" (PARTE -13 §2). Todo o
  projeto, o acervo e os livros estão nele. Por isso a gravação do projeto foi para um fio por trás: qualquer escrita
  no fio da janela podia pará-la por segundos.
- **O C: já encheu.** Em 07/10/2026, às 18h36, quatro agentes rodando testes ao mesmo tempo esgotaram os 15 GB de
  memória: "o Windows aumentou o `C:\pagefile.sys` até 33 GB, o C: chegou a 0 GB e o Claude Code caiu, levando os
  agentes junto" (PARTE -13 §0). O `pagefile.sys` "cresce sozinho até ~33 GB quando a memória acaba e só volta ao normal
  ao reiniciar"; a memória comprometida chegou a 95% (29,8 de 31,2 GB) com VS Code, a VM do Claude Desktop, Chrome,
  Bloons TD6 e Steam abertos (PARTE -13 §5). O C: tinha ~14 GB livres em 06/10 e ~66 GB em 08/10/2026, depois da
  limpeza autorizada.
- **O `vmmem` de 0,9 GB não é o WSL** (14/10/2026): continuou depois do `wsl --shutdown`, sem distribuição rodando;
  "provavelmente a máquina virtual de outro programa: não mexer" (PARTE -16 §3).
- **O relógio do PC está em UTC-4 (America/Cuiaba); o GitHub e as respostas das páginas do claude.ai estão em UTC**
  (PARTE -15 §6). Ex.: commit das 04h20 no PC = 08h20 UTC.

## 2. Regras de uso do PC (por causa dos acidentes de 07/10/2026)

Registro de 07/10/2026 ("Regras de trabalho depois de dois acidentes no PC do Samuel") e PARTE -13 §0:

- **No máximo 3 a 4 agentes ao mesmo tempo.** (Em 25-29/09 a recomendação era "no máximo 2", PARTE -8; vale a mais
  nova, 3 a 4.)
- **Um arquivo de pytest por vez** (ou um `rodar.py`): `pytest tests\<arquivo> -q -p no:cacheprovider`.
- **TEMP, TMP e `--basetemp` dentro da worktree** do agente.
- **Esperar enquanto houver menos de 3 GB livres** (`FreePhysicalMemory`). Em 14/10/2026 o PC não passou de 2,6 GB
  livres mesmo depois de fechar o CapCut e de `wsl --shutdown`; para a medição de velocidade a exigência **baixou para
  2,5 GB** ("o teste usa no máximo 1,4 GB"; as rodadas começaram com 3,8 a 4,4 GB) (PARTE -16 §3). Com 3 ou 4 agentes o
  PC ficou entre 3,4 e 5,8 GB livres (PARTE -15 §6).
- **Nunca mover nem apagar uma árvore de pastas sem listar as junções antes** (ver §8).
- Nada de abrir janela na tela do Samuel nos testes (desde 30/09/2026, `tests/conftest.py` põe o Qt sem tela).

## 3. Onde roda cada teste (decisões do Samuel, 19/10/2026)

Tabela do [CLAUDE.md §4.6](../../CLAUDE.md), copiada:

| Onde | O que roda | Quando |
|---|---|---|
| **GitHub** (Windows da nuvem) | As ~2.050 conferências (`pytest`), o `teste_botoes.py` e os prints da janela real | Em **toda** entrega de agente, antes de ir ao verificador |
| **GitHub** | **Filtro de velocidade**: antes e depois **na mesma máquina, alternados** (`teste_velocidade.py` + Marial 300). Se acusar lentidão, volta para o agente | Em toda mudança que mexe em processamento (`core/`) |
| **PC do Samuel** | Um arquivo de teste por vez (`pytest tests\<arquivo> -q`) | Enquanto o agente trabalha |
| **PC do Samuel** | As ~2.050 conferências e o `teste_botoes.py` inteiros, com os outros agentes parados | **Antes de qualquer trabalho entrar no `fase-1`** (a gerente roda) |
| **PC do Samuel** | Janela de verdade pilotada pelo verificador | Nos trabalhos de tela |
| **PC do Samuel** | **Medida de velocidade que vale** para a regra 6 (alternada, PC sem agentes) | **No fim de cada fase** |
| **Notebook do Kaique** | Régua final de velocidade (item 0.6 / Fase 5) | Quando ele puder |

As palavras do Samuel no chat de 19/10/2026 ([plano, Registro 19/10/2026](../../docs/plano/PLANO-DEFINITIVO.md)):
suíte **"B: GitHub e meu PC"**; velocidade **"opção 2"** (filtro no GitHub sempre, PC no fim de cada fase); lentidão
pequena no meio de uma fase vai para a Fase 5: "vamos deixar esse concerto de lentidão para o final, para a fase de
desempenho." Pergunta dele: "mas nós precisamos medir a velocidade no meu pc sempre? porque o programa deveria conseguir
se desenvolver bem em qualquer computador né?" (resposta registrada: o notebook do Kaique é a régua final; o PC é a
régua por ser sempre a mesma máquina).

O **notebook do Kaique**: Samsung Galaxy Book2, i5-1235U, 32 GB, SSD NVMe, vídeo integrado Iris Xe (item
[0.6](../itens/0.6.md), ainda `[~]`). Teste de reversão obrigatório em todo conserto: [CLAUDE.md §4.7](../../CLAUDE.md).

## 4. Rodar os testes no GitHub

O workflow **"Testes no Windows"** (`.github/workflows/testes-windows.yml`) mora **só no ramo
`claude/list-server-files-gkos8v`** (não está no `fase-1`). Autorizado pelo Samuel em 09/10/2026 (PARTE -14 §1).
O repositório `Samuel-Bottini-BR/EditorImpressao` é **público**.

```
gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f ramo=<ramo>
gh run watch <id> -R Samuel-Bottini-BR/EditorImpressao --exit-status
```

- `-f ramo=<ramo ou commit>`: o **código do programa** vem desse ramo; a `.github/` continua a do
  `claude/list-server-files-gkos8v`. Nada é gravado no ramo testado.
- `-f so_janela=true`: só o `teste_botoes.py` e os prints da janela real (sem a suíte).
- Outras opções: `velocidade` (o `teste_velocidade.py`, sem veredito), `antes_depois` (antes/depois do endireitar nas
  páginas-gabarito), `velocidade_ab` (o filtro novo, §6), `rapido`.
- Leva **6 a 12 minutos** (PARTE -15 §6): a suíte em **5 máquinas Windows em paralelo**, cada uma arquivo por arquivo,
  com Python 3.14.3 e as versões do `.venv` do Samuel (`.github/requisitos-windows.txt`), TEMP/TMP/`LOCALAPPDATA`
  dentro da pasta de trabalho; o `teste_botoes.py` e os prints na tela de verdade (1920×1080), nos três temas.
- **Ramo `dados-de-teste`** (`12bbb01`): cópia somente leitura de `gabarito/` e `modelos/` e o `marial_300.pdf`,
  publicada com autorização do Samuel; fora só o `horas_p047.tif` (154 MB). O Tesseract não está lá (os 2 testes dele
  pulam).
- **Ramo `prints-testes`**: os prints de cada rodada, pasta `data_hora_sha_ramo` (ex.: `2026-10-09_1942_8c07656_fase-1`).
- O próprio workflow diz o que é **proibido**: "pular, desligar ou marcar xfail qualquer teste para 'ficar verde'".
- Os commits do ramo `claude/list-server-files-gkos8v` levam `[skip ci]`: sem isso cada push dispara a suíte inteira.

### Rodadas do GitHub citadas no plano e no histórico

| Rodada | Data | O quê | Resultado |
|---|---|---|---|
| (09/10) | 09/10/2026 | primeira referência, `fase-1` | 1947 passaram, 0 falharam, 72 pulados (13 a mais que no PC: 11 do acervo inteiro e 2 do Tesseract, que não estão lá) |
| **38326255291** | 12/10/2026 | junção do G6 ao `fase-1` (`4a7f288`) | 112 arquivos, **1992 passaram**, 0 falharam, 72 pulados; botões e prints: passou |
| **38469423649** | 13/10/2026 | layout juntado (`juntar-layout3-2026-10-13`, `f35bcaf`) | `completed / success`, lida às 21h24 UTC; "o detalhe por tarefa não foi lido, o GitHub devolveu erro 502" |
| **38662254297** | 14/10/2026 | `fase-1` (`6f79734`+) com o layout | 114 arquivos, **2049 passaram**, 0 falharam, 72 pulados; botões e prints da janela real: success |
| 39394176019 | 20/10/2026 08:32 UTC | rodada curta (`rapido`) do filtro de velocidade | em andamento quando lido (ONDE-PAREI, passo 5) |

Ressalvas conhecidas: um teste instável (`tests/test_gravura_na_aba_marcar.py::test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita`,
1 falha em ~7 rodadas); velocidade no GitHub **sem** o filtro alternado não dá veredito ("as máquinas variam até 70% entre
si", PARTE -14 §1).

## 5. Quantos testes havia em cada época

| Data | Testes | Fonte |
|---|---|---|
| 07/09/2026 | 241 funções `def test_` em 15 arquivos; **279 casos** coletados | [CLAUDE.md §4.5](../../CLAUDE.md) |
| 23/09/2026 | **434** passando (eram 349 no início da sessão) | [ESTADO-ATUAL §3](../../docs/plano/ESTADO-ATUAL.md); PARTE -6 |
| 26/09/2026 | **666** casos | [CLAUDE.md §7](../../CLAUDE.md) |
| 29/09/2026 | 826 (de manhã); **897** no commit `dfe3b89` | PARTE -8 §9; Registro 29/09/2026 |
| 02 e 03/10/2026 | 1346 e 1369 passaram (PC, suíte inteira, 7 a 8,5 min) | PARTE -9 §9; PARTE -10 §8 |
| 05/10/2026 | **1301** passaram | Registro 05/10/2026 (consertos da janela) |
| 06/10/2026 | **1464**; depois **1663** (1 pulado); `fase-1` com consertos 1757 | Registro 06/10/2026; PARTE -12 §7 |
| 08/10/2026 | **1960** passaram, 0 falharam, 59 pulados (110 arquivos, `5ecc4dc`, PC) | Registro 08/10/2026; PARTE -13 §1 |
| 12/10/2026 | **1992** (GitHub, 38326255291) | Registro 12/10/2026 |
| 13/10/2026 | **2081** (PC, ramo `fase2-caixa-conteudo`, 113 arquivos); **2101** (GitHub, ramo `fase2-para-revisar`, 116 arquivos) | Registro 13/10/2026 |
| 14/10/2026 | **2049** (GitHub, `fase-1`, 38662254297) | PARTE -16 §1 |
| 20/10/2026 | 115 arquivos `test_*.py`, 1672 funções `def test_` no `fase-1` (`b8e9af7`); "~2.050 conferências" | contado nesta ficha; [CLAUDE.md §4.6](../../CLAUDE.md) |

Os números não sobem em linha reta porque cada um é de um ramo diferente (o `fase-1` de 14/10 tem menos que o ramo do
"Para revisar" de 13/10). "Passaram" sempre conta só o que não foi pulado; os pulados são os do OCR (59 no PC, 72 no
GitHub).

## 6. Velocidade

### O teste e o livro

- [`teste_velocidade.py`](../../teste_velocidade.py) (item [0.5](../itens/0.5.md)): mede **abrir o livro** (até a
  análise de todas as folhas terminar), **trocar de página** (prévia de uma página nunca vista; 20 trocas),
  **processar 10 páginas** (146 a 155) em **Mágico pro** e em **Preto e branco**, e a **memória máxima**. Cada coisa 3
  vezes; vale a mediana ("de costume"). Uma rodada leva 11 a 13 minutos.
- O livro: **Marial de sermoens, 300 folhas** — `gabarito\velocidade\marial_300.pdf` (67,9 MB; fora do git; cópia no
  ramo `dados-de-teste`). Aberto com o filtro Mágico pro (Registro, 26/09/2026: "Mantido").
- **Regra 6 do plano**: "Nenhum item pode deixar o programa mais lento." Exceções dadas pelo Samuel: a primeira prévia
  ~0,5 s mais lenta pelo detector do 1.2, "até a Fase 5" (Registro, 30/09/2026); o Mágico pro +1,1% do "Para revisar"
  vai para a Fase 5 (19/10/2026).
- **Só vale com o PC parado.** Em 30/09 16:26 deu "tudo mais lento" e era o emulador Android, o OBS e o Chrome do
  Samuel; o código antigo medido na mesma hora também saiu lento (PARTE -9 §1). Daí a regra: **medir alternado** (A, B,
  A, B) em duas worktrees.

### Como medir alternado no PC

- Scripts em `relatorios\velocidade-g6-2026-10-12\` ([`rodar_uma.ps1`](../../relatorios/velocidade-g6-2026-10-12/rodar_uma.ps1),
  [`juntar.py`](../../relatorios/velocidade-g6-2026-10-12/juntar.py)) e, adaptados, em `relatorios\velocidade-layout3-2026-10-14\`
  ([`rodar_todas.ps1`](../../relatorios/velocidade-layout3-2026-10-14/rodar_todas.ps1),
  [`rodar_uma.ps1`](../../relatorios/velocidade-layout3-2026-10-14/rodar_uma.ps1),
  [`juntar.py`](../../relatorios/velocidade-layout3-2026-10-14/juntar.py)).
- `rodar_todas.ps1`: aquecimento curto nas duas cópias, depois antes-1, depois-1, antes-2, depois-2, antes-3, depois-3,
  uma por vez; para na primeira que falhar. `rodar_uma.ps1 -braco antes|depois -nome <pasta>`: espera a memória livre,
  põe TEMP/TMP na worktree, só lê o livro e usa o Python do `.venv` da pasta principal. Para medir outro ramo, troque as
  duas pastas (`antes` = worktree `velocidade-antes`; `depois` = a do ramo). `juntar.py` monta a tabela e o veredito.
- Veredito usado: diferença entre as medianas maior que o vai-e-vem entre rodadas iguais = mudou; senão, "igual".

### O filtro de velocidade no GitHub (em construção, 20/10/2026)

ONDE-PAREI em `ramo claude/list-server-files-gkos8v: ONDE-PAREI-filtro-velocidade.md` (pedido da gerente em 20/10/2026):
- Feito: passos 1 a 4 — `.github/scripts/velocidade_ab.py` (roda alternando e junta a tabela), `preparar_versao.sh`,
  conferido com os números do PC de 14/10 ("igual" nas quatro medidas), e o modo novo `velocidade_ab` no workflow
  (`-f velocidade_ab=true -f ramo_antes=<ramo> -f ramo_depois=<ramo> -f rodadas_ab=3`; cada rodada leva 10 a 20 min).
- Falta: passo 5 (rodada curta 39394176019, disparada 20/10 08:32 UTC), 6 e 7 (validação com antes = `1d37f8f`, depois
  = `3bdbab3`), 8 (controle: antes = depois) e 9 (entrega à gerente).
- Anotação do agente: a regra do veredito, "simulada com ruido puro e 3 rodadas: ~3% de 'falso lento' por medida (~12%
  em alguma das 4)"; se acusar lentidão, repetir antes de devolver ao agente.

### Números de referência ao longo do tempo (PC do Samuel, Marial 300)

| Medição | Abrir o livro | Trocar de página | Mágico pro, 10 p. | Preto e branco, 10 p. | Memória | Fonte |
|---|---|---|---|---|---|---|
| **26/09/2026 13:05** (a referência da Fase 0) | 38,9 s (45,0 na 1ª vez) | 2,3 s (pior 2,8) | 1 min 14 s (7,4 s/p.) | 33,1 s | 1.641 MB | `relatorios/velocidade/velocidade-SAMUEL-PC-2026-09-26-1305.md` |
| 29/09/2026 14:45 | 44,4 s | 2,7 s | 1 min 19 s | 34,0 s | — | **não conclusivo** (PC em uso), Registro 29/09/2026 |
| **29/09/2026 18:09** (PC parado, com o 1.1) | 37,9 s | 2,1 s | 1 min 9 s | 30,1 s | 1.600 MB | Registro 29/09/2026: "Regra 6 cumprida até aqui" |
| 30/09/2026 16:26 | "tudo mais lento" | | | | | descartada: emulador/OBS/Chrome abertos (PARTE -9 §1) |
| **30/09/2026 22:42** (teste oficial) | 25,5 s | 2,3 s (pior 3,0) | 54,5 s | 27,3 s | 1.571 MB | PARTE -9 §3 (`velocidade-SAMUEL-PC-2026-09-30-2242`) |
| **12/10/2026, G6** (alternado, 3+3) | 58,1 → 58,3 s | 2,54 → 2,61 s | 6,2 → 6,0 s **por página** | 2,8 → 2,6 s **por página** | — | Registro 12/10/2026; [`velocidade.md`](../../relatorios/velocidade-g6-2026-10-12/velocidade.md) |
| **14/10/2026, layout** (alternado, 3+3) | 55,2 → 55,6 s | 2,36 → 2,31 s | 57,0 → 55,2 s | 26,0 → 26,4 s | 1.375–1.406 → 1.261–1.379 MB | PARTE -16 §1; [`velocidade.md`](../../relatorios/velocidade-layout3-2026-10-14/velocidade.md) |

Cuidado ao comparar: as linhas de 12/10 dão Mágico pro e Preto e branco **por página**; as outras, as 10 páginas.
Antes → depois = o ramo antigo e o novo na mesma sessão; vale a diferença entre os dois, não o número solto.

### O achado "abrir o Marial leva ~58 s" (Lista de bugs, 12/10/2026, aberto)

"Abrir o livro de 300 folhas (Marial) levou perto de 58 s no PC do Samuel em 12/10, com e sem o G6 (seis rodadas: 54,6 a
60,9 s). Nas medições guardadas de 26 a 30/09, no mesmo PC, livro e disco, levava de 25,5 a 44,4 s. Não é do G6. Causa
não investigada: pode ser o PC ocupado (outros agentes trabalhavam) ou algo que entrou no programa em outubro. Medir de
novo com o PC parado e, se continuar, achar em que commit mudou." Em 14/10 continuou em ~55 s. Item [5.1](../itens/5.1.md).

## 7. O limite de uso da conta e como não perder trabalho

- **O limite de uso da conta derruba os agentes no meio do trabalho**: três vezes em 25-29/09 (PARTE -8: "Preferir no
  máximo 2 agentes") e **três vezes em 12-13/10/2026** (PARTE -15 §6).
- O que fazer: **cada agente faz commit e push no próprio ramo a cada passo** e mantém um **`ONDE-PAREI.md`**;
  **retomar com `SendMessage` para o mesmo agente** (ele continua do ponto). As conversas dos subagentes ficam em
  `C:\Users\fotog\.claude\projects\d--programas\<sessão>\subagents\` (PARTE -13 §5).
- **Tudo no GitHub** (Samuel, 08/10/2026): cada agente dá push no próprio ramo depois de cada commit; **o push do
  `fase-1` é só da gerente**. Avançar o `fase-1` na pasta principal precisa do "pode atualizar o programa" do Samuel.
- O painel do Claude Code mostra o agente como "terminado" quando ele só espera um teste em segundo plano (PARTE -13 §5).
- Quando o Claude Code (extensão do VS Code) cai, a sessão volta com o mesmo id; os processos de teste dos agentes ficam
  órfãos (fechar só com o ok do Samuel: "pode fechar os testes antigos").

## 8. Armadilhas do Windows neste PC

- **PowerShell 5.1** (PARTE -15 §6): mensagem de commit com aspas quebra em `-m` → usar **`git commit -F arquivo`**.
  **`Set-Content -Encoding utf8` põe BOM** (o título do commit `7485e1b` ficou com um). **`&&` e `||` não existem** no
  5.1 (usar `; if ($?) { ... }`). Um guarda do Claude Code confunde `/1GB` com caminho e bloqueia o comando (PARTE -13 §4).
- **Junções nas worktrees**: várias worktrees em `.claude\worktrees\` têm junções para `modelos`, `gabarito\paginas` e
  `gabarito\scantailor-24-09` da pasta principal. **Nunca `Remove-Item -Recurse`** nelas; desfazer **só com
  `(Get-Item <junção>).Delete()`** (PARTE -15 §2). Em 07/10/2026 um `robocopy /MOVE` sem `/XJ` seguiu as junções de um
  scratchpad e esvaziou `modelos\` (18 arquivos) e `gabarito\paginas\` + `scantailor-24-09\` (117 arquivos) das 19h20 às
  22h; foi restaurado da cópia no D: (PARTE -13 §0).
- **Apagar arquivo ou pasta** fora do projeto: nunca sem perguntar ao Samuel ([CLAUDE.md §10 item 9](../../CLAUDE.md),
  regra de 29/09/2026, depois que um agente apagou `D:\d`).
- Ao editar o plano por script: caminhos com `/`, conferir "caracteres de controle = 0" depois; o plano no disco é CRLF
  (PARTE -9).

## 9. A sessão na nuvem (09 a 12/10/2026)

O Samuel trabalhou de 09 a 12/10/2026 numa sessão do Claude Code **na nuvem**: "cópia do GitHub num Linux, sem Windows,
sem as DLLs do ScanTailor, sem a janela" ([plano, Registro 09/10/2026](../../docs/plano/PLANO-DEFINITIVO.md); PARTE -14).
O que ela **não tem** (PARTE -13 §0): `modelos\` (doclayout, doctr, mobile_sam, tessdata), `gabarito\paginas\`,
`gabarito\scantailor-24-09\`, as imagens de `relatorios\`, os livros de teste do D:, a `.venv`; as DLLs
`core/nativo/*.dll` e a janela PySide6 são do Windows. "Na nuvem, muitos testes pulam ou falham por falta disso: **não
conclua que o código quebrou**." Ela lia o HD pelo servidor WebDAV da rede privada do Samuel (endereço fora desta memória) e só gravou
na cópia do plano e em `D:\programas\EditorImpressao-arquivos\sessao-nuvem-2026-10-09\`, nunca dentro da pasta do
projeto. Serve para escrever código, preparar perguntas e atualizar o plano; foi dela que nasceram os testes no Windows
do GitHub (§4). O contêiner pode reiniciar e matar os agentes: push a cada commit.

## 10. Atualização de 19 a 21/10/2026 ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md))

- **Filtro de velocidade adotado.** O workflow `Testes no Windows` (ramo `claude/list-server-files-gkos8v`, `6f6fe76`) ganhou o modo `velocidade_ab`: roda antes e depois **na mesma máquina, alternando**. Provado com uma versão lenta de propósito (ramo `teste-filtro-lento-2026-10-20`, **nunca juntar**). Comando: `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f velocidade_ab=true -f ramo_antes=<a> -f ramo_depois=<b>`. A seção "em construção" acima descreve o começo; vale esta.
- **Por quê alternar:** medir direto no GitHub não serve, as máquinas variam até 70%. Funcionou medir antes e depois na mesma máquina, alternando, com espera do processador (< 15%) e piso de 2%.
- **Limite de consultas do GitHub (HTTP 403):** vários agentes com `gh run watch` ao mesmo tempo esgotam a API. Disparar e ler **uma vez só, no fim**.
- **Limite de uso da conta:** três vezes com 5 a 8 agentes juntos (20/10 de manhã, 20/10 à tarde, 21/10 de madrugada); os agentes param no meio e voltam com SendMessage depois do horário do erro. Nada se perde com commit + `ONDE-PAREI.md`.
- **Suíte no PC (antes de juntar):** com TEMP dentro da worktree e os agentes parados: `TEMP=<worktree>\_tmp TMP=<worktree>\_tmp .venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp=<worktree>\_tmp\bt` (~13 min) e `teste_botoes.py` (~5 min). Última no PC (junção do corte, 20/10/2026): 2085 passaram, 1 falhou (teste que depende da ordem, consertado em `consertos-2026-10-21`), botões 221/0. Última do `fase-1` no GitHub: 39478983864 (junção do corte), passou.
- **Rede privada:** o endereço da rede privada do Samuel foi tirado desta ficha antes de a memória ser publicada (PARTE -17 §3).
