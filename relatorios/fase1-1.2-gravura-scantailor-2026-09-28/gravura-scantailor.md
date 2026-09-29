# Item 1.2: o seletor de gravura do ScanTailor, compilado (régua e páginas obrigatórias)

Gerado em 28/09/2026 23:07 por `conferir_gravura_scantailor.py`. DLL: ScanTailor-Advanced/scantailor-advanced v1.2.1 (commit 5eaac1884cdc), Qt 6.11.1.

## 1. Régua: a DLL contra as máscaras que o próprio ScanTailor gravou em 24/09 (teste de máquina)

Com a mesma geometria do ScanTailor (giro, escala para 600 DPI e retângulo de trabalho), ponto a ponto, dentro do conteúdo. **IoU** = parte em comum / parte marcada por um ou pelo outro (1 = idênticas). **Iguais** = pontos com a mesma resposta.

| Página | DPI | Gravura (ScanTailor) | Gravura (DLL) | IoU | Iguais | Só DLL | Só ScanTailor | Tempo |
|---|---|---|---|---|---|---|---|---|
| escola_p007 | 338 | 37,94% | 37,94% | 0,9990 | 99,96% | 3694 | 4150 | 2,2 s |
| horas_p011 | 168 | 39,67% | 70,55% | 0,3948 | 52,18% | 37162996 | 7995896 | 9,4 s |
| horas_p013 | 168 | 4,21% | 4,24% | 0,9863 | 99,94% | 20128 | 7564 | 4,7 s |
| horas_p047 | 168 | 88,61% | 88,65% | 0,9981 | 99,83% | 79741 | 51479 | 10,3 s |
| palatino_p005 | 400 | 51,39% | 51,49% | 0,9952 | 99,75% | 16172 | 7067 | 1,5 s |
| palatino_p009 | 400 | 0,00% | 0,00% | (as duas vazias) | 100,00% | 0 | 0 | 1,4 s |
| rhetorica_p018 | 400 | 0,00% | 0,00% | (as duas vazias) | 100,00% | 0 | 0 | 1,9 s |
| horas_p011, página invertida | 168 | 39,67% | 44,30% | 0,8119 | 91,28% | 6302614 | 1927194 | - |

Imagens `regua_<página>.jpg`: cinza = os dois marcam; **vermelho = só a DLL**; **azul = só o ScanTailor** (engrossado para aparecer).

## 2. Como o programa vai usar: a página inteira, sem a geometria do ScanTailor

A mesma comparação, mas a DLL recebe a página como ela é (sem giro, sem o recorte do ScanTailor), no DPI dela e a 150 DPI (o DPI em que `core/camadas.py` chama o detector). A máscara é levada depois para o lugar da do ScanTailor.

| Página | IoU no DPI da página | Iguais | IoU a 150 DPI | Iguais | Tempo (DPI da página / 150) |
|---|---|---|---|---|---|
| escola_p007 | 0,9986 | 99,95% | 0,9967 | 99,88% | 1,28 s / 0,61 s |
| horas_p011 | 0,3951 | 52,17% | 0,3956 | 52,31% | 3,67 s / 2,64 s |
| horas_p013 | 0,6618 | 97,85% | 0,6578 | 97,81% | 2,64 s / 2,80 s |
| horas_p047 | 0,9880 | 98,92% | 0,9880 | 98,93% | 3,78 s / 3,41 s |
| palatino_p005 | 0,9904 | 99,50% | 0,9885 | 99,41% | 1,06 s / 0,43 s |
| palatino_p009 | (vazias) | 100,00% | 1,0000 | 100,00% | 1,00 s / 0,31 s |
| rhetorica_p018 | (vazias) | 100,00% | 1,0000 | 100,00% | 1,35 s / 0,57 s |

## 3. Páginas obrigatórias da Fase 1 (teste de olho: o Samuel decide)

Imagens `obrigatoria_<página>.jpg`: original | **DLL do ScanTailor (vermelho)** | detector de hoje, zona gravura (azul).

| Página | DPI | Tamanho | Gravura (DLL) | Gravura (hoje) | Retangular | Mais sensível | Tempo DLL no DPI dela | a 150 DPI | a 300 DPI | Tempo do detector de hoje | IoU 150 x DPI dela | IoU 300 x DPI dela |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| palatino_p005 | 400 | 1929 x 2943 | 38,02% | 100,00% | 50,60% | 50,79% | 0,95 s | 0,46 s | 0,72 s | 2,87 s | 0,994 | 0,997 |
| escola_p035 | 200 | 1517 x 2098 | 28,54% | 29,09% | 29,71% | 45,09% | 1,07 s | 0,78 s | 1,37 s | 2,54 s | 0,998 | 0,998 |
| horas_p011 | 72 | 1024 x 1446 | 65,49% | 58,73% | 74,39% | 84,05% | 2,93 s | 2,75 s | 5,00 s | 1,19 s | 0,993 | 0,993 |
| horas_p013 | 72 | 1024 x 1453 | 4,34% | 3,26% | 55,66% | 93,41% | 2,25 s | 2,88 s | 4,29 s | 0,86 s | 0,675 | 0,700 |
| horas_p026 | 72 | 1024 x 1533 | 52,50% | 0,00% | 96,13% | 58,08% | 1,86 s | 3,15 s | 4,80 s | 0,90 s | 0,988 | 0,992 |
| horas_p027 | 72 | 1024 x 1471 | 4,09% | 0,00% | 90,36% | 93,46% | 1,88 s | 2,71 s | 4,46 s | 0,89 s | 0,700 | 0,693 |
| opusmajus_p020 | 400 | 2212 x 3620 | 25,39% | 49,83% | 49,17% | 48,98% | 0,94 s | 0,39 s | 0,86 s | 1,91 s | 0,889 | 0,985 |

Imagens `obrigatoria_<página>_opcoes.jpg`: original | forma retangular | "maior sensibilidade de busca" (as duas opções do ScanTailor que mudam a forma).

**Aviso da Fase 1:** moldura e iluminura ainda são defeito conhecido até a Fase 1 ficar pronta.
