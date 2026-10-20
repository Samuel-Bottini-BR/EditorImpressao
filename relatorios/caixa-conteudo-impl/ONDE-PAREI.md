# Caixa da página e caixa do conteúdo do ScanTailor: onde parei

## 20/10/2026 — Parte 1 (ligar a caixa do conteúdo, 2.5) — EM ANDAMENTO

Pedido da gerente (20/10): olhar os livros de folha grande; ligar a caixa do conteúdo e as
linhas de apoio conforme `g8-guias`, `g8-moldura-tinta-fora`, `g9-pagina-muito-maior`. A borda
preta (2.13, Parte 2) só quando a gerente mandar (depende da `g7-borda-ate-onde`).

Passos (marque ao terminar):
- [x] `origin/fase-1` (b8e9af7) juntado ao ramo, sem conflito (`a67e1f0`; o fase-1 só mexeu em
      `core/analise.py`, que este ramo não toca).
- [x] Folha grande olhada: `scripts/olhar_folha_grande.py`, imagens em `img/folha-grande/`
      (9 páginas: ljs47 10/46/68, Antiphon 88/123/260, Egenloff 3/12/47, com as quatro beiradas
      ampliadas), números em `dados/folha-grande.json`. Resumo e causa: seção "Folha grande" abaixo.
- [ ] Ligar no núcleo (opção do livro, desligada de fábrica).
- [ ] Aviso "o corte deixou tinta de fora" (g8) + corte alargado.
- [ ] Conta do tamanho do livro sem a folha muito maior (g9).
- [ ] Linhas de apoio (g8-guias): núcleo; tela só o mínimo, commit separado.
- [ ] Testes (um arquivo por vez), GitHub, antes/depois no gabarito, entrega.

### Folha grande (20/10): o que vi, a causa, a proposta

**O que vi (abri as 18 imagens):** no ljs47 e no Antiphon a caixa "encolhida" (DPI do programa)
é a certa: abraça o texto e as notas, deixa de fora a beirada do livro, a folha vizinha e o
papel vazio. A caixa "grande" (DPI que o PDF diz, a das imagens de 12/10) é que estava errada:
pega quase a folha inteira. Nas beiradas ampliadas, nenhuma letra do ljs47 nem do Antiphon 88 e
123 é partida (algumas encostam na linha; a folga de 1 mm resolve). **Problemas reais:**
(1) Antiphon 260: no alto, a caixa corta o enfeite da esquerda e as notas da pauta de cima, que
o próprio scan já cortou; à direita, letras que vão até a beirada da imagem ficam de fora (as
duas contas, de DPI do programa e do PDF, fazem isso). (2) Egenloff 3 e 47: a caixa passa no
meio dos carimbos da biblioteca e da anotação "3865"; no 3 deixa de fora a etiqueta vermelha
impressa de 1880 ("1880 neu aufgelegt von George Gilbers"). (3) **Egenloff 12** (verso quase em
branco, só o carimbo): a caixa vira uma tira de 231 x 22 pontos em cima do risco de caneta do
carimbo. Usada como corte, a página viraria uma tira.

**A causa:** esses PDFs dizem 72 ou 96 DPI, então "a folha" teria 35 x 46 a 46 x 63 cm; mas a
imagem de verdade tem só 1.000 a 1.800 pontos de altura (Antiphon 1316 x 1800, ljs47 1379 x
1800, Egenloff 1000 x 1300). O programa diz à DLL o mesmo DPI das outras ferramentas do
ScanTailor (`dpi_para_as_caixas`, que põe a página grande em no máximo 7 milhões de pontos a
300 DPI): a DLL vê uma página de uns 19 x 26 cm, perto da resolução de verdade do scan. As
regras do ScanTailor para "sujeira" e "lixo da beirada" são em milímetros; com o DPI do PDF a
beirada do livro e a folha vizinha ficam "grandes" e entram como conteúdo. A 300 DPI (como o
programa desenha) a caixa é a mesma (diferença de até 4 pontos).

**Proposta:** manter o DPI do programa (é o certo). Ao usar a caixa como corte: (a) página com
conteúdo pequeno demais (Egenloff 12: 0,1% da página; a menor página boa medida tem 35%) não usa
a caixa, fica o corte comum, e avisa; (b) o aviso de tinta partida/de fora (`g8`) pega o
Antiphon 260 e os carimbos do Egenloff. Ressalva: carimbo de biblioteca vai disparar o aviso.

**Quem:** agente implementador · **Datas:** 12 e 13/10/2026 · **Ramo:** `fase2-caixa-conteudo` (saiu do `fase-1` em `4b19a9b`; **não juntado**) · **Pedido:** gerente (a base dos itens 2.13 e 2.5, que serve para qualquer resposta do Samuel às seis perguntas de 12/10).

## Em uma frase

O programa passou a ter, guardada e testada, a conta original do ScanTailor que acha a página dentro da borda preta e o retângulo do conteúdo; ela dá as mesmas caixas que o pesquisador mediu nas 37 páginas dele, e **ninguém no programa a chama ainda**.

**PRONTO PARA CONFERIR** (teste de máquina; eu não olhei imagem nenhuma). Não é "aprovado": quem aprova é o Samuel.

## O que está feito

| O quê | Onde | Commit |
|---|---|---|
| 18 arquivos do ScanTailor Advanced v1.2.1, sem mudança, com a soma conferida | `terceiros/scantailor-advanced/src/` e `somas-v1.2.1.txt` | `330da14` |
| A "cola" em C: `st_ferramentas_caixas` (a interface da DLL subiu para a versão 4) | `terceiros/scantailor-advanced/ligacao-ferramentas/caixas.cpp`, `st_ferramentas.h` | `330da14` |
| A DLL recompilada (298 KB; era 215 KB) | `core/nativo/st_ferramentas.dll` e `.txt` | `330da14` |
| A porta em Python: `achar(img, dpi)` e `achar_na_pagina(base, dpi_do_desenho, dpi_do_scan)` | `core/caixas_scantailor.py` | `330da14` |
| Os testes (76 casos) e os números do pesquisador | `tests/test_caixas_scantailor.py`, `tests/dados/caixas_scantailor_pesquisador.json` | `330da14`, `1c20d58` |
| As medidas (caixas, tempos, memória, DLL anterior) e os scripts | `relatorios/caixa-conteudo-impl/dados/`, `scripts/` | `330da14`, `1c20d58` |
| O LEIA-ME de `terceiros/` com a seção "As caixas" | `terceiros/scantailor-advanced/LEIA-ME.md` | `1c20d58` |
| Este arquivo | `relatorios/caixa-conteudo-impl/ONDE-PAREI.md` | `28fabf0` e o seguinte |

**O que a função devolve:** a caixa da página e a caixa do conteúdo em pontos da imagem e em milímetros, o tamanho do conteúdo em mm como o ScanTailor guarda (é o número que as margens do 2.4 usam), se a página tem conteúdo (página em branco: não tem), se a conta foi feita na página invertida ("claro no escuro"), e o tempo de cada parte. Sem a DLL, ou com entrada errada, devolve "indisponível" com o motivo em português, sem exceção.

**O que NÃO foi mexido:** `core/pipeline.py`, `core/analise.py`, `modelos.py`, `ui/`. O teste `test_ninguem_no_programa_chama_as_caixas_ainda` falha se alguém ligar sem querer. A `st_gravura.dll` não foi tocada.

## Os testes (de máquina)

- `tests/test_caixas_scantailor.py`: **76 de 76** (1 min 50 s). O que prende:
  - **as mesmas caixas do pesquisador** nas 37 páginas dele, mais a Horas 13 e o Graduale 222 a 150 DPI (39 medidas): página, conteúdo dentro da página, e, em 5 páginas, conteúdo na folha inteira e as duas com "ajustar os cantos". **Tolerância 0,06 ponto**: o programa dele imprimiu com uma casa decimal, então o número dele pode estar até 0,05 longe do valor exato; a maior diferença medida foi 0,04. Não é folga para a conta: é só o arredondamento da impressão.
  - **o DPI muda a caixa**: Horas 13 a 72 DPI dá quase a folha inteira (104 a 1006 de 1024); a 150 fica por dentro da moldura (121 a 775).
  - **página sem borda preta** (Palatino 66, Escola 35): a caixa da página é a folha inteira (folga de 3 pontos, o tamanho de um ponto de 150 DPI nessas páginas) e a caixa do conteúdo não parte nem deixa de fora nenhuma peça de tinta.
  - **Siebmacher 7 e 9**: a caixa da página ainda vai até o preto, a do conteúdo para antes dele, e nenhuma peça de tinta é partida.
  - folhas de mentira: faixa preta sai da página; texto a 10 pontos da faixa não é cortado; página em branco; colorida igual a cinza; "claro no escuro"; parâmetro errado não derruba; trava de memória; cópia fiel do trecho copiado.
- As três ferramentas que já estavam na DLL (limpar pontinhos, dividir, endireitar) dão **o mesmo** com a DLL nova e com a anterior nas 32 páginas do gabarito: 96 de 96, 96 de 96 e 32 de 32 (`dados/dll-anterior.json`).
- Um arquivo por vez: `test_st_ferramentas` 10, `test_dividir_scantailor` 13, `test_endireitar_scantailor` 17, `test_pontinhos_scantailor` 30, `test_gravura_scantailor` 24, todos passam.
- **A bateria inteira:** 2081 passaram, nenhum falhou, 59 pulados (ver "A bateria", no fim).

## Os tempos (item 5 do pedido; para o 2.16)

Medido no PC do Samuel em 12/10, com outros agentes rodando (os números sobem e descem com a carga: a mesma página do Antiphon levou de 2,5 a 5,5 s). Uma chamada = as duas caixas. Números em `dados/medidas.json`.

| Livro (DPI dito) | Tamanho a 150 DPI | Tempo por página | Caixa da página | Caixa do conteúdo |
|---|---|---|---|---|
| Siebmacher (400) | 0,5 milhão de pontos | 0,2 s | 20% | 60% |
| Palatino, Opus Majus (400) | 0,8 a 1,3 | 0,4 a 0,7 s | 22% | 56% |
| Escola (200) | 1,7 a 1,8 | 0,6 a 0,7 s | 19% | 74% |
| Camões, Cursus, Matemática, Righetti (150) | 0,4 a 2,2 | 0,3 a 0,9 s | 24% | 71% |
| Marial (72) | 2,9 | 1,2 s | 25% | 75% |
| Graduale (72) | 5,6 a 5,8 | 2,6 a 3,3 s | 20% | 79% |
| Livro de Horas (72) | 6,4 a 6,8 | 2,4 a 2,9 s | 24% | 75% |
| Egenloff, ljs47 (150) | 5,6 a 6,1 | 2,9 a 3,7 s | 17% | 80% |
| Antiphon (150) | 10,2 a 10,3 | 4,3 a 5,5 s | 18% | 78% |

**Onde está lento:**

1. **O tempo segue o tamanho da página depois de levada a 150 DPI**: cerca de meio segundo por milhão de pontos. Página comum de livro: menos de 1 s. Folha grande de verdade (Antiphon, 46 x 63 cm): 4 a 5 s.
2. **DPI errado para baixo amplia a página e triplica o tempo.** O Horas e o Graduale dizem 72 DPI, que não é a resolução de verdade. Com o DPI que as outras ferramentas do ScanTailor já usam no programa (`achar_na_pagina`: uns 130 a 140), o Horas cai de 2,4-2,9 s para 0,8-1,2 s e o Graduale de 2,6-3,3 s para 0,6-1,2 s.
3. **A caixa do conteúdo é 3/4 do tempo** nas páginas grandes; a da página, 1/5.
4. **Desperdício no código original** (não mexi: a regra é o código original): o `PageFinder` calcula cinco preto e branco e usa um; cada uma das duas contas leva a página a 150 DPI de novo (a mesma imagem, duas vezes).
5. **Um caso estranho:** numa folha de mentira com uma grade de retângulos iguais ao lado de uma faixa preta, a conta levou 5 s numa página de 1,4 milhão de pontos (dez vezes o normal) e jogou fora as colunas vizinhas da faixa. Com texto escrito de verdade não acontece. Pode acontecer com tabela de colunas ao lado de borda preta: **não testei em página de verdade**.

**Memória:** cerca de 20 MB por milhão de pontos a 150 DPI (Antiphon: 200 MB a mais). A função recusa página com mais de 16 milhões (uns 320 MB) antes de ir à DLL (`PONTOS_MAXIMOS_A_150`), para um DPI errado não ampliar a página até acabar a memória.

**Para o 2.16:** a chamada solta o Python enquanto a DLL trabalha (como as outras), então dá para rodar várias páginas ao mesmo tempo. **Não testei** duas chamadas ao mesmo tempo; antes de usar todos os núcleos, isso precisa de teste (resultado igual e sem travar).

## O que falta para ligar no programa, por resposta do Samuel

Comum a todas: o botão por livro (desligado de fábrica; regra 8 do plano), o campo no projeto e no `modelos.py`, onde chamar no `core/pipeline.py` (depois do endireitar, que é a ordem do ScanTailor e a do livro novo; **no projeto começado antes de 09/10 a ordem é cortar e depois endireitar, e a conta não foi pensada para isso**), guardar a caixa para não refazer a cada desenho, o teste de velocidade e a conferência a olho.

| Pergunta | Resposta | O que falta |
|---|---|---|
| `g7-borda-ate-onde` | "só o preto" | **A função não basta.** A caixa da página do ScanTailor só tira faixa preta reta que cobre 95% do lado: serve no ljs47, Egenloff, Cursus, Camões; no Siebmacher quase não corta. A opção mostrada ao Samuel foi uma conta do pesquisador ("anda da beirada enquanto o meio do lado é escuro"), que é conta nossa, a escrever e testar. |
| | "até a moldura" | A função basta: a sugestão é `conteudo` (mais a folga de 1 mm que o Samuel já decidiu). Falta ligar à sugestão de corte, ao "aceitar / mudar / mandar para todas" e ao seletor de páginas. |
| `g8-moldura-tinta-fora` | "avisa" | Falta a conta que diz "ficou tinta de fora" (peças de tinta partidas pela caixa ou sozinhas do lado de fora; a ideia está em `_partidas_e_de_fora` do teste) e o aviso no "Para revisar". |
| | "alarga" | Falta a conta "alarga sozinho" (do pesquisador, testada por ele só em 3 páginas): juntar à caixa as peças de tinta partidas ou sozinhas de fora. É conta nossa por cima do ScanTailor; precisa rodar no gabarito inteiro. |
| | "volta ao corte comum" | Falta a mesma conta de "ficou tinta de fora" e, quando der sim, usar `core.recortar.detectar_bordas` (o corte de hoje). |
| `g8-guias` | qualquer uma | É de tela (`ui/widgets/visualizador.py`). Desta função só usa `conteudo_mm`. |
| `g9-pagina-muito-maior` | "fica de fora" ou "entra" | Falta o 2.4 inteiro: as contas de margens do ScanTailor (`page_layout/Utils.cpp`, **não trazidas**) e uma passada no livro todo para saber o maior conteúdo (soma dos tempos acima: um livro de 300 páginas comuns, uns 2 a 4 minutos em um núcleo). Entrada pronta: `tamanho_do_conteudo_mm` de cada página. "Fica de fora" pede mais uma regra nossa (quando uma folha é "muito maior"). |
| `g10-papel-ou-pagina`, `g10-ajustar-todas` | qualquer uma | É de `core/folha.py` e `core/cadernos.py`; não depende desta função. |

## Ressalvas

1. **Não olhei imagem nenhuma.** Os testes dizem que a DLL dá as caixas do pesquisador; se essas caixas são boas quem viu foi ele (Horas 14 perde a barra dourada; Opus Majus 137 perde o número do pé).
2. **O DPI muda muito a caixa, e as imagens das perguntas de 12/10 foram feitas a 72 DPI no Horas, no Graduale e no Marial.** Com o DPI que o programa diria (o das outras ferramentas), as caixas são outras. Exemplos (em pontos): Horas 14, de 249-955 x 172-1231 para 253-932 x 225-1211; Horas 13, de 104-1006 x 37-1435 para 119-775 x 221-1149; Graduale 221, de 78-877 x 72-1350 para 84-961 x 43-1196 (e a caixa da página passa a começar em 8). Antes de ligar, alguém precisa olhar essas páginas com o DPI que o programa vai usar. Os números estão em `dados/medidas.json` (`com_o_dpi_do_programa`).
3. **Qual imagem vai à DLL** (a da prévia ou a do PDF final) não foi decidido nem medido; a caixa pode mudar alguns pontos entre uma e outra.
4. **Página endireitada:** no ScanTailor os cantos que aparecem com o giro são pintados de escuro antes desta conta. Não testei com páginas giradas pelo endireitar do programa.
5. **"Claro no escuro":** de fábrica a função deixa o ScanTailor decidir (como o endireitar). Nas 37 páginas ele decidiu "preto no branco" em todas, então dá igual ao do pesquisador; em página que ele decidir o contrário, a caixa é feita na página invertida.
6. **`conteudo` e `conteudo_bruto`:** no código original, a procura do conteúdo passa da caixa da página à direita e embaixo quando a página não começa no canto (no ljs47, 16 a 108 pontos dentro do preto). O ScanTailor corta depois pela página, e a função devolve as duas; **vale `conteudo`**.
7. **A `st_gravura.dll` do 1.2 não foi recompilada** com os 18 arquivos novos em `src/` (os de `core/` e `imageproc/` entram na biblioteca dela). A DLL guardada é a mesma (o teste confere a soma); o risco é só o de a próxima recompilação dela precisar de ajuste.
8. **O teste de velocidade (`teste_velocidade.py`) não foi rodado:** nada do programa chama a função, e as três ferramentas antigas dão o mesmo ponto a ponto. A DLL ficou 83 KB maior.
9. **Os milímetros** são pontos x 25,4 / DPI dito: se o DPI dito não é o de verdade (Horas), os mm também não são.
10. As páginas de verdade ficam fora do git: num PC sem `gabarito/paginas` e sem o acervo, 51 dos 76 testes são pulados.

## Como compilar de novo

Da raiz da worktree, com a `.venv` da pasta principal e `TEMP`/`TMP` dentro da worktree:

    D:\programas\EditorImpressao\.venv\Scripts\python.exe compilar_st_ferramentas.py --rascunho D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo\saida_teste\caixa-conteudo\build-st-ferramentas

Levou 166 s (a biblioteca inteira do ScanTailor é recompilada). Precisa do que já estava instalado: CMake, Visual Studio 2022 Build Tools, e o Qt 6.11.1 e o Boost 1.78 de `D:\programas\EditorImpressao-arquivos\ferramentas\` (nada foi instalado nem baixado). O caminho completo em `--rascunho` deixa o rascunho dentro da worktree.

Refazer as medidas: `relatorios\caixa-conteudo-impl\scripts\medir.py` (caixas e tempos), `medir_memoria.py` (memória) e `comparar_dll_anterior.py` (as três ferramentas antigas).

## Na minha worktree, fora do git

`saida_teste\caixa-conteudo\` (rascunho da compilação, a DLL anterior tirada do git e logs; 17 MB). Junções criadas por mim: `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09` (apontam para a pasta principal; **não apagar com `Remove-Item -Recurse`**). Fora de `D:\programas\EditorImpressao` não criei nem apaguei nada.

## Ideias para a Lista de espera

- A função já diz "página sem conteúdo" (`tem_conteudo` falso): pode servir ao aviso "Página sem conteúdo" do "Para revisar".
- O tamanho esperado da página em mm (`tamanho_esperado_mm`, opção do ScanTailor) pode ajudar onde a borda preta é irregular; não medi.

## Bugs para a Lista de bugs

Nenhum do programa. Do código original do ScanTailor (não consertados, só anotados em `caixas.cpp`): o retângulo da página montado com direita/baixo no lugar de largura/altura (`ContentBoxFinder.cpp`, linhas 102-103) e os cinco preto e branco do `PageFinder`.

## A bateria

Rodada em 13/10/2026, de 01:52 a 02:08, **um arquivo de pytest por vez** (113 arquivos de `tests/`, cada um no seu processo, esperando 3 GB de memória livre antes de cada um): **2081 passaram, nenhum falhou, 59 pulados**, no commit `28fabf0` (o código é o de `1c20d58`). Os pulados são de arquivos que não toquei (nenhum de `test_caixas_scantailor.py`, que passou os 76); não comparei a lista de pulados com a do `fase-1`.
