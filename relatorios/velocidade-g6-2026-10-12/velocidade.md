# Velocidade do G6 (endireitar antes de cortar) no PC do Samuel, 12/10/2026

Verificador. Conferido por **máquina** (teste de velocidade). Só medi e relato: não juntei ramo, não mexi em código e **não marco nada como aprovado**.

## A resposta em uma frase

**Ficou igual: nesta medição não apareceu lentidão do G6.** As diferenças entre o programa de hoje e o G6 são todas menores que o vai-e-vem entre duas rodadas iguais do mesmo programa. Por isso, para diferenças pequenas, **não dá para dizer** nem "mais lento" nem "mais rápido".

- **Abrir o livro de 300 folhas:** 58,1 s antes, 58,3 s depois. Diferença de +0,2 s no livro inteiro (+0,001 s por folha). Rodadas iguais variaram de 4,7 a 6,3 s entre si.
- **Trocar de página:** 2,54 s antes, 2,61 s depois (+0,07 s por página). Rodadas iguais variaram de 0,2 a 0,3 s.
- **Processar em Mágico pro:** 6,2 s por página antes, 6,0 s depois (10 páginas: 61,8 s e 59,8 s, ou seja, 2,0 s a menos). Rodadas iguais variaram de 3,0 s (antes) a 16,6 s (depois).
- **Processar em Preto e branco:** 2,8 s por página antes, 2,6 s depois (10 páginas: 27,9 s e 26,5 s, ou seja, 1,3 s a menos). Rodadas iguais variaram de 2,1 a 5,7 s.
- **Memória máxima:** 1.378 MB antes, 1.384 MB depois (igual).

No livro inteiro de 300 páginas, pela conta das 10 páginas medidas, processar em Mágico pro daria perto de 31 minutos antes e 30 minutos depois. É conta de multiplicar, com o mesmo ruído: vale como "igual".

O que esta medição garante: **não há lentidão grande**. O que ela não alcança: a diferença de 0,05 s por página que o implementador mediu é muito menor que o ruído deste PC, e aqui não dá para confirmar nem negar (em trocar de página apareceu +0,07 s, dentro do ruído de 0,2 a 0,3 s). Se essa diferença valesse para cada folha ao abrir o livro, seriam 15 s a mais em 300 folhas, e isso não apareceu (+0,2 s).

## O que foi comparado

| | Antes | Depois |
|---|---|---|
| Programa | o de hoje, `fase-1` (9c51801) | G6, `fase2-endireitar-2` (44cbf21) |
| Pasta | `.claude\worktrees\velocidade-antes` | `.claude\worktrees\endireitar` |

- O código do programa no `fase-1` de hoje é o mesmo do ponto em que o G6 começou (4bf3888): de lá para cá o `fase-1` só mudou documentos e dois arquivos de `tests/`. A diferença entre as duas pastas é só o G6.
- O `teste_velocidade.py` é idêntico nos dois ramos (versão 1 do teste).
- Mesmo livro para as duas: `gabarito\velocidade\marial_300.pdf` da pasta principal, só lido (300 folhas, 67,9 MB, conferi que é o mesmo arquivo do ramo `dados-de-teste`). Disco: HD externo (USB).
- Mesmo Python (`.venv` da pasta principal, 3.14.3), detector de gravura e letra carregado em todas, notebook na tomada em todas.
- Cada rodada é uma execução inteira do teste, que repete tudo 3 vezes (como no GitHub): abrir o livro, 20 trocas de página, processar as páginas 146 a 155 em Mágico pro e em Preto e branco.
- Ordem alternada: antes, depois, antes, depois, antes, depois. Uma de cada vez. Cada uma levou de 12 a 13,5 minutos.
- Prova de que o G6 estava ligado no "depois": o PDF de saída em Mágico pro saiu com 70,7 MB nas três rodadas do depois e 71,3 MB nas três do antes (o corte muda).

## Todas as rodadas

Cada número é o valor do meio (mediana) das 3 repetições daquela execução.

| Rodada | Hora | Memória livre antes | Processador antes | Abrir o livro | Trocar (média) | Trocar (a pior) | Mágico pro, 10 pág. | Preto e branco, 10 pág. | Memória máxima | Durou |
|---|---|---|---|---|---|---|---|---|---|---|
| antes-1 | 18:52 | 4,93 GB | 5% | 60,3 s | 2,68 s | 3,91 s | 62,9 s | 29,0 s | 1.369 MB | 12,9 min |
| depois-1 | 19:06 | 4,91 GB | 4% | 60,9 s | 2,65 s | 4,22 s | 68,6 s | 29,9 s | 1.382 MB | 13,5 min |
| antes-2 | 19:19 | 4,15 GB | 8% | 58,4 s | 2,56 s | 3,81 s | 62,7 s | 26,9 s | 1.378 MB | 12,7 min |
| depois-2 | 19:32 | 5,09 GB | 8% | 59,3 s | 2,49 s | 3,44 s | 52,0 s | 24,2 s | 1.389 MB | 11,9 min |
| antes-3 | 19:44 | 5,30 GB | 5% | 55,6 s | 2,37 s | 3,52 s | 59,9 s | 27,7 s | 1.386 MB | 12,0 min |
| depois-3 | 19:57 | 5,38 GB | 7% | 54,6 s | 2,69 s | 4,00 s | 58,9 s | 25,5 s | 1.382 MB | 12,5 min |

A memória livre nunca ficou abaixo de 3 GB (o mínimo foi 4,15 GB).

## Antes contra depois, e o ruído

"Vai-e-vem" é a distância entre a menor e a maior das três rodadas iguais. Se a diferença é menor que o vai-e-vem, não dá para dizer.

| Medida | Antes | Depois | Diferença | Vai-e-vem do antes | Vai-e-vem do depois | Par a par (depois menos antes) | Dá para dizer? |
|---|---|---|---|---|---|---|---|
| Abrir o livro (300 folhas) | 58,1 s | 58,3 s | +0,2 s (+0,3%) | 4,7 s | 6,3 s | +0,6; +0,9; -1,0 s | não: igual |
| Trocar de página (média de 20) | 2,54 s | 2,61 s | +0,07 s (+2,9%) | 0,30 s | 0,20 s | -0,02; -0,07; +0,31 s | não |
| Trocar de página (a pior das 20) | 3,75 s | 3,89 s | +0,14 s (+3,7%) | 0,39 s | 0,78 s | +0,31; -0,37; +0,48 s | não |
| Mágico pro, 10 páginas | 61,8 s | 59,8 s | -2,0 s (-3,3%) | 3,0 s | 16,6 s | +5,7; -10,8; -0,9 s | não |
| Preto e branco, 10 páginas | 27,9 s | 26,5 s | -1,3 s (-4,8%) | 2,1 s | 5,7 s | +0,9; -2,6; -2,3 s | não |

Em nenhuma medida os três pares apontam para o mesmo lado.

## Cada repetição (3 por execução)

| Rodada | Medida | 1ª | 2ª | 3ª |
|---|---|---|---|---|
| antes-1 | Abrir o livro | 59,6 s | 60,3 s | 61,8 s |
| antes-1 | Trocar (média) | 2,79 s | 2,61 s | 2,68 s |
| antes-1 | Trocar (a pior) | 3,24 s | 3,91 s | 3,94 s |
| antes-1 | Mágico pro | 65,1 s | 62,9 s | 61,9 s |
| antes-1 | Preto e branco | 29,4 s | 29,0 s | 24,2 s |
| depois-1 | Abrir o livro | 54,9 s | 61,9 s | 60,9 s |
| depois-1 | Trocar (média) | 2,95 s | 2,65 s | 2,52 s |
| depois-1 | Trocar (a pior) | 4,14 s | 4,31 s | 4,22 s |
| depois-1 | Mágico pro | 74,3 s | 68,6 s | 63,0 s |
| depois-1 | Preto e branco | 36,7 s | 29,0 s | 29,9 s |
| antes-2 | Abrir o livro | 60,9 s | 56,2 s | 58,4 s |
| antes-2 | Trocar (média) | 3,02 s | 2,23 s | 2,56 s |
| antes-2 | Trocar (a pior) | 4,11 s | 3,03 s | 3,81 s |
| antes-2 | Mágico pro | 65,0 s | 59,3 s | 62,7 s |
| antes-2 | Preto e branco | 26,2 s | 26,9 s | 28,0 s |
| depois-2 | Abrir o livro | 59,3 s | 59,6 s | 50,3 s |
| depois-2 | Trocar (média) | 3,01 s | 2,49 s | 2,12 s |
| depois-2 | Trocar (a pior) | 3,83 s | 3,44 s | 3,21 s |
| depois-2 | Mágico pro | 61,3 s | 52,0 s | 50,3 s |
| depois-2 | Preto e branco | 28,3 s | 24,2 s | 24,0 s |
| antes-3 | Abrir o livro | 50,7 s | 58,7 s | 55,6 s |
| antes-3 | Trocar (média) | 2,63 s | 2,37 s | 2,26 s |
| antes-3 | Trocar (a pior) | 3,63 s | 3,52 s | 3,48 s |
| antes-3 | Mágico pro | 59,9 s | 57,6 s | 61,5 s |
| antes-3 | Preto e branco | 27,7 s | 27,2 s | 29,0 s |
| depois-3 | Abrir o livro | 58,3 s | 54,6 s | 51,7 s |
| depois-3 | Trocar (média) | 2,99 s | 2,69 s | 2,55 s |
| depois-3 | Trocar (a pior) | 4,00 s | 4,34 s | 3,84 s |
| depois-3 | Mágico pro | 58,8 s | 60,6 s | 58,9 s |
| depois-3 | Preto e branco | 25,5 s | 24,8 s | 28,1 s |

Juntando as 9 repetições de cada lado: abrir o livro, antes de 50,7 a 61,8 s e depois de 50,3 a 61,9 s; Mágico pro, antes de 57,6 a 65,1 s e depois de 50,3 a 74,3 s.

## Ressalvas

1. **O PC não estava parado só para o teste.** Não sei se o Samuel estava usando. O processador estava entre 4% e 8% antes de cada rodada, mas durante a medição a pasta principal recebeu dois commits da gerente (19:20, "agentes postos a trabalhar", e 19:57): outros agentes podem ter trabalhado neste PC ao mesmo tempo.
2. **Duas rodadas destoaram, as duas do "depois", uma para cada lado.** A depois-1 (19:06) foi a mais lenta em Mágico pro (74,3 s na primeira repetição) e a memória livre caiu 0,7 GB enquanto ela rodava. A depois-2 (19:32) foi a mais rápida (52,0 e 50,3 s nas duas últimas repetições). É por isso que o vai-e-vem do depois em Mágico pro é de 16,6 s.
3. **O PC foi ficando mais rápido ao longo da noite** (abrir o livro: 60,3; 60,9; 58,4; 59,3; 55,6; 54,6 s, na ordem em que rodaram). Como o "depois" sempre rodou logo depois do seu "antes", isso favorece um pouco o depois, perto de 1 s em abrir o livro. Mesmo somando isso, a diferença continua bem dentro do ruído.
4. **O teste rodou sem janela preta** (chamado por outro programa), e não na janela clássica do Windows. Vale igual para os dois lados.
5. **Não medi:** a janela de verdade do programa (o teste não tem tela); o notebook do Kaique; outro livro além do Marial; projeto antigo reaberto (que no G6 continua na ordem de antes); a diferença de 0,05 s por página do implementador (menor que o ruído daqui).
6. **Achado fora desta tarefa, para a gerente:** abrir o livro levou perto de 58 s hoje **nas duas pastas**, e nas medições guardadas deste PC (26/09 a 30/09, mesmo livro, mesmo disco) levava de 25,5 a 44,4 s (a última, de 30/09 às 22:42, deu 25,5 s). Não é do G6, porque o programa de hoje sem o G6 dá o mesmo. Não investiguei a causa (pode ser mudança que já entrou no `fase-1` depois de 30/09, ou o estado do PC). As outras medidas de hoje estão dentro da faixa das guardadas.

## Comandos que rodei e o que criei

Na pasta principal `D:\programas\EditorImpressao` só rodei leitura e o `fetch`; ela continua no `fase-1`, o livro e a pasta `modelos\` estão inteiros (18 arquivos, 289.910.409 bytes, antes e depois).

```
git -C D:\programas\EditorImpressao fetch origin
git -C D:\programas\EditorImpressao\.claude\worktrees\endireitar merge --ff-only origin/fase2-endireitar-2
    (avanço simples, de a742bf4 para 44cbf21; a pasta estava limpa)
git -C D:\programas\EditorImpressao worktree add --detach .claude/worktrees/velocidade-antes origin/fase-1
    (sem ramo, em 9c51801)
New-Item -ItemType Junction -Path D:\programas\EditorImpressao\.claude\worktrees\velocidade-antes\modelos -Target D:\programas\EditorImpressao\modelos
    (igual à junção modelos da worktree endireitar; as de gabarito não criei, o teste de velocidade não usa)
```

Cada rodada, pelo `rodar_uma.ps1` desta pasta (espera 3 GB livres, anota hora, memória e processador, põe TEMP e TMP em `saida_teste\tmp-velocidade` da própria worktree e roda, com a pasta de trabalho na worktree):

```
D:\programas\EditorImpressao\.venv\Scripts\python.exe teste_velocidade.py "D:\programas\EditorImpressao\gabarito\velocidade\marial_300.pdf" --saida "<esta pasta>\rodadas\<nome>"
```

Ordem: `aquecimento-antes` e `aquecimento-depois` (com `--rapido`, 18:50 e 18:51, só para ver que funcionava; não entram na conta), depois `antes-1`, `depois-1`, `antes-2`, `depois-2`, `antes-3`, `depois-3`. Todas terminaram com saída 0 e sem nada no arquivo de erros.

O que criei:

- a worktree `D:\programas\EditorImpressao\.claude\worktrees\velocidade-antes` (sem ramo), com a junção `modelos` e uma pasta `saida_teste` vazia;
- nesta worktree (`endireitar`), só a pasta `relatorios\velocidade-g6-2026-10-12\` (sem commit): este relatório nos três formatos, `rodar_uma.ps1`, `juntar.py` (monta as tabelas a partir dos `.json`) e `rodadas\` com o relatório, o `.json`, o texto do terminal e a anotação de cada rodada;
- arquivos `__pycache__` nas duas worktrees (fora do git).

As duas pastas temporárias `saida_teste\tmp-velocidade` eu mesmo removi no fim, vazias.

Para desfazer a worktree nova, **primeiro a junção, depois a worktree**:

```
(Get-Item D:\programas\EditorImpressao\.claude\worktrees\velocidade-antes\modelos).Delete()
    (conferir que D:\programas\EditorImpressao\modelos continua com os 18 arquivos)
git -C D:\programas\EditorImpressao worktree remove .claude/worktrees/velocidade-antes
```

Sem tirar a junção antes, o `worktree remove` apaga a pasta com tudo o que há dentro e pode levar junto os modelos de verdade.
