# Ajustes do Dividir e da janela do Automático (03/11/2026)

**Os seis achados do verificador clicando de 03/11 estão resolvidos ou respondidos, sem mudar o que já estava
escolhido. Na segunda parte: o Ctrl+Y que perdia os "Parece em branco" (já existia antes; provado) e a D-608 foram
consertados. Ver "Segunda parte", no fim.** Cinco foram consertados (motor na folha juntada, aviso do "juntar todas", setas depois da lista, tira
depois do Ctrl+Z, etapa 6 cortada). O sexto ("7 com dúvida") não é defeito: são as páginas em branco do livro, e o
"dividir esta" folha a folha dá as mesmas 7. PRONTO PARA CONFERIR (quem confere é o verificador e o Samuel).

Ramo `dividir-ajustes-2026-11-03` (saiu de `75ed04af`). Testes: de máquina. Prints: na janela de verdade do Windows,
posta fora da tela, no Gradus Primus copiado para uma pasta de dados só desta tarefa
(`piloto.py`, anotações em `anotacoes.txt`).

## Decisões que esta tarefa precisava cumprir — como cumpri cada uma

| Decisão | Como cumpri | Prova |
|---|---|---|
| **D-606** "Ele deve fazer a conta novamente com o novo motor" | Na folha juntada, trocar o motor lê a folha pelo motor novo e a linha vai para onde ele acha; o Ctrl+Z devolve motor e linha | Gradus folha 5: linha de antes 0,44 → motor "o do Editor" → 0,5033 (p02, p03). `tests/test_decisoes_dividir.py::test_reversao_d606_*` e `test_d606_depois_do_juntar_todas_*` |
| **D-607** "só temos que mudar o aviso, avisar que as páginas foram juntadas e que vão ser separadas se o processar continuar." | Só o texto muda. Título, explicação de baixo, botões, contagem e o que cada botão faz ficam iguais | p07 (Gradus, 70 juntadas). `tests/test_decisoes_automatico.py::test_*d607*` (4) |
| **D-605** o novo não estraga o escolhido | Lista "O que já está escolhido e testado" no ONDE-PAREI antes de mexer; nenhum teste antigo mudou; todos passam no PC (um por um) e no GitHub | ver "Testes" |
| **D-602** linha azul, "dividir esta", "dividir todas", lista nunca trava | Nada mudou nisso; `tests/test_decisoes_dividir_linha.py` passa sem mudança (13) | PC e GitHub |
| **D-498** "não dividir esta" devolve a linha de antes | Continua enquanto o motor não é trocado (p02: 0,44 depois de juntar) | `test_d602_folha_juntada_mostra_a_linha_de_antes` e o novo teste D-606 |
| **D-090** "usar em todas" copia a linha desta folha · **D-601** arrastar em "Duas lado a lado" | Não mexidos | `test_d602_usar_em_todas_*`, `test_decisoes_dividir_metade.py` |
| **D-004** pular as mexidas · **D-590** caixinha desmarcada fica | Contagem, botões e o pular iguais; caixinha não mexida | `test_d004_*`, `test_decisoes_juntar_todas.py`, `test_dividir_desmarcada_caixinha.py` |

## Item por item

1. **D-606, motor na folha juntada.** Antes a linha ficava parada nos dois motores. Agora a troca do motor na folha
   juntada refaz a conta (a mesma da folha nunca dividida) e grava a linha nova na mesma ação do desfazer. "dividir
   esta" depois corta nela e devolve as páginas de antes (D-498). Se o motor novo achar a folha de uma página só, a
   linha some (como na folha nunca dividida) e o "dividir esta" usaria a conta forçada.
   Arquivo: `ui/tela_conferir.py` (`_trocar_jeito_da_folha`, `_linha_com_o_motor`).
2. **D-607, o aviso.** Texto exato quando só há folhas juntadas:
   > 70 páginas foram juntadas no Dividir e vão ser separadas se o processar continuar nelas. Pular essas páginas?

   Uma só: "1 página foi juntada no Dividir e vai ser separada se o processar continuar nela. Pular essas páginas?"
   Mistura (3 juntadas e 1 mexida de outro jeito):
   > 3 páginas foram juntadas no Dividir e vão ser separadas se o processar continuar nelas. 1 página foi mexida à mão nas etapas que vão rodar. Pular essas páginas?

   Sem juntadas: o texto de sempre, letra por letra. Botões "Pular as N" / "Rodar nelas também" / "cancelar" e a
   explicação de baixo, iguais. "Juntada" = folha não dividida que guarda as duas páginas de antes ("não dividir
   esta" ou "juntar todas") e o pedido tem o Dividir. Arquivos: `core/automatico.py` (`paginas_juntadas`),
   `ui/janela_principal.py` (`texto_das_mexidas`, `_perguntar_mexidas`).
3. **Setas depois da lista "motor de corte".** A lista pegava o teclado ao ser clicada. Agora não pega (como as
   outras listas da área de trabalho). No Gradus: → da folha 6 para a 7, troca do motor na 7, → foi para a 8, ← voltou
   à 7 (p01). Arquivo: `ui/tela_conferir.py` (uma linha).
4. **Tira depois do Ctrl+Z.** A tira rolava antes de os quadros novos estarem no lugar e caía no começo. Agora rola
   de novo quando estão. Gradus: folha 60, Ctrl+Z do "dividir todas" → miniatura 60 à vista (p05); refazer →
   miniatura 119 (folha 60) à vista (p06). Arquivo: `ui/widgets/tira_miniaturas.py`.
5. **"7 com dúvida" — não é defeito, nada mudou.** São os avisos "Parece em branco" das metades esquerdas que são
   páginas em branco no livro: folhas 2, 3, 7, 8, 62, 63 e 69 (páginas 3, 5, 13, 15, 123, 125, 137 depois de dividir).
   Desfazendo e dando "dividir esta" só nessas 7 folhas, saem os mesmos 7 avisos, nas mesmas metades. Ao abrir o livro,
   0 dúvidas (a folha inteira não tem página branca). Print da folha 7 (metade esquerda branca, "7 com dúvida"): p04.
6. **Etapa 6 cortada.** A janela principal de 1536 x 824 abre a do Automático com 92% (1413 x 758): a coluna do meio
   tinha 674 pontos e a linha "página menor, de cima a baixo: [no meio] de um lado ao outro: [no meio]" pedia 732.
   Agora essa linha dobra em duas só quando não cabe (mesmos textos, controles e ordem); onde cabe (janela de 1536
   de largura) fica numa linha, como era. Medido na janela de verdade: rolagem de lado 58 → 0 (p08).
   Arquivo: `ui/automatico.py` (`_LinhaQueDobra`, `_opcoes_margens`).

## Testes

- Testes de reversão (todos falham no código de `75ed04af` e passam no novo): D-606 (2), D-607 (3 de 4; o 4º é a
  guarda "sem juntadas, texto de sempre"), setas, tira, etapa 6 (`tests/test_dividir_ajustes_03_11.py`; mais uma
  guarda: onde cabe, a linha fica como era).
- PC, um arquivo por vez: todos passaram (23 arquivos, nenhum teste antigo mudou):
  - `tests/test_decisoes_dividir_linha.py`: 13 passed in 16.36s
  - `tests/test_decisoes_dividir.py`: 21 passed in 74.94s (0:01:14)
  - `tests/test_decisoes_dividir_metade.py`: 6 passed in 11.33s
  - `tests/test_decisoes_juntar_todas.py`: 4 passed in 10.11s
  - `tests/test_dividir_desmarcada_caixinha.py`: 3 passed in 14.31s
  - `tests/test_dividir_na_tela.py`: 9 passed in 32.96s
  - `tests/test_dividir_no_programa.py`: 19 passed in 21.41s
  - `tests/test_automatico_pular_depois_de_dividir.py`: 4 passed in 0.51s
  - `tests/test_decisoes_automatico.py`: 29 passed in 73.16s (0:01:13)
  - `tests/test_decisoes_automatico_margens_no_depois.py`: 5 passed in 19.84s
  - `tests/test_decisoes_automatico_opcoes_do_filtro.py`: 21 passed in 123.80s (0:02:03)
  - `tests/test_decisoes_automatico_ver_como_fica.py`: 22 passed in 105.34s (0:01:45)
  - `tests/test_decisoes_9b1.py`: 25 passed, 16 warnings in 38.36s
  - `tests/test_decisoes_9b2.py`: 30 passed in 58.89s
  - `tests/test_miniaturas_novas.py`: 5 passed in 4.42s
  - `tests/test_decisoes_avisos.py`: 22 passed in 50.07s
  - `tests/test_decisoes_caderno_tela_grande.py`: 11 passed in 41.06s
  - `tests/test_decisoes.py`: 26 passed in 5.48s
  - `tests/test_decisoes_tela.py`: 35 passed, 4 warnings in 46.96s
  - `tests/test_dividir_ajustes_03_11.py`: 4 passed in 12.91s
  - `tests/test_decisoes_filtro_automatico.py`: 4 passed in 15.42s
  - `tests/test_decisoes_montar_cadernos.py`: 13 passed in 95.21s (0:01:35)
  - `tests/test_menu_paineis.py`: 3 passed in 1.76s
- GitHub, conjunto inteiro + `teste_botoes.py` (rodada **41759151010**, ramo no commit `abd8cd0a`; depois disso só
  mudaram arquivos de relatório): **passou**. Na 1ª tentativa a parte 5 falhou em um teste de outra área
  (`test_gravura_na_aba_marcar.py::test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita`, Marcar/gravura, que
  esta tarefa não tocou); ele passa 3 de 3 no PC e passou ao repetir só a parte que falhou. Fica como ressalva:
  falha às vezes, por tempo.
- GitHub, filtro de velocidade `75ed04af` → `abd8cd0a` (rodada **41759125497**, mexi em `core/automatico.py`):
  **ainda rodando na entrega** (começou às 02:11 UTC; os de hoje levaram cerca de 1 h 40). Não consegui esperar até
  o fim: meus próprios vigias gastaram o limite por hora de consultas ao GitHub. A gerente precisa conferir o
  resultado. A mudança em `core/` só acrescenta uma função chamada uma vez quando se aperta "Rodar" (e só quando há
  páginas mexidas); não fica no caminho do processamento.

## Ressalvas

- Item 1: a linha "acertada à mão" da folha 5 (0,44) foi posta pelo sinal da linha (como o arrastar), não com o
  mouse; o resto foi clique e tecla do Windows.
- Item 2: página que é de folha juntada e também foi mexida de outro jeito entra na parte das "juntadas" (a soma das
  duas partes é sempre a contagem dos botões). A palavra "processar" é a do Samuel; o botão da janela diz "Rodar".
- Item 3: a lista não pega mais o teclado. Os **botões** do painel também pegavam; isso virou a D-608 (abaixo) e
  foi feito.
- Item 5: no Dividir a faixa da folha 7 mostra a frase do Dividir, não o "Parece em branco" (o aviso é da página e
  aparece no "Para revisar" e nas outras ferramentas). Isso já era assim.

## Bugs para a Lista de bugs

- Nenhum aberto. Os dois anotados na 1ª entrega foram consertados (ver "Segunda parte").

## Prints (pasta `relatorios/dividir-ajustes/`)

- p01 — item 3: depois de trocar o motor na folha 7, a seta → foi para a folha 8.
- p02 — item 1: folha 5 juntada, linha de antes (0,44), motor "o do ScanTailor".
- p03 — item 1: a mesma folha com o motor "o do Editor": linha em 0,5033.
- p04 — item 5: folha 7 depois do "dividir todas", metade esquerda em branco, "7 com dúvida".
- p05 — item 4: folha 60 depois do Ctrl+Z, a miniatura 60 escolhida e à vista.
- p06 — item 4: depois do refazer, a miniatura da folha 60 à vista.
- p07 — item 2: o aviso novo depois do "juntar todas" (70 páginas).
- p08 — item 6: a etapa 6 inteira, janela do Automático aberta da janela de 1536 x 824.
- p09 — Ctrl+Y depois do "dividir todas": "7 com dúvida" de volta (triângulo com 7), folha 7.
- p10 — D-608: folha 5 logo depois do clique em "dividir esta" (o botão ficou com o teclado).
- p11 — D-608: tecla → depois desse clique: "folha 6 de 70".

---

# Segunda parte (03/11/2026, depois da leitura do Samuel)

Samuel: "cara, ele burlou a regra, colocou um defeito novo, concerta isso ai, pode fazer o teste no meu pc mesmo se
não está dando certo no git hub".

## 1. O Ctrl+Y que perdia os 7 "Parece em branco": de onde veio

**Não veio destes ajustes, nem da D-602: já existia antes.** Mesmo caminho no Gradus ("dividir todas", Ctrl+Z,
Ctrl+Y), contando as dúvidas, com o código de cada versão (programa sem janela, pasta de dados própria):

| Código | Ao abrir | "dividir todas" | Ctrl+Z | Ctrl+Y |
|---|---|---|---|---|
| `75ed04af` (antes dos ajustes) | 0 | 7 | 0 | **0** |
| `abd8cd0a` (1ª entrega) | 0 | 7 | 0 | **0** |
| `046c5b3b` em diante (conserto) | 0 | 7 | 0 | **7** (folhas 2, 3, 7, 8, 62, 63, 69) |

E com "dividir esta" só na folha 7 (`abd8cd0a`): 1 → 0 → **0**. Ou seja, o refazer nunca mediu o em branco desde a
etapa 7 (27/10), quando a medida por trás entrou. A ação guarda as páginas de antes da medida, e o refazer as
devolvia assim. Eu tinha anotado isso como bug sem conferir de onde vinha; agora está provado e consertado.

**Conserto na causa:** `TelaConferir.refazer` mede o "Parece em branco" como o `_registrar` mede depois de aplicar
a mesma ação (`_medir_o_em_branco_ao_refazer`: ação de folha que troca as páginas ou a linha). A medida é a mesma
função, que põe ou tira o aviso. O desfazer não mudou.
Teste de reversão `tests/test_dividir_ajustes_03_11.py::test_reversao_refazer_devolve_o_parece_em_branco`
("dividir todas" e "dividir esta"; Ctrl+Z e Ctrl+Y duas vezes): falha no código de antes e passa no novo.
Print p09 (janela de verdade, Ctrl+Y por tecla do Windows): "7 com dúvida".

## 2. Nenhum outro problema do mesmo tipo nos ajustes

Ida e volta no Gradus, comparando TUDO (cada página: metade, avisos, avisos aceitos, em branco, tirada do livro;
cada folha: dividida, linha, motor, avisos; e o número de dúvidas):

| Passo | `75ed04af` | novo |
|---|---|---|
| "dividir todas": Ctrl+Z = ao abrir | igual | igual |
| "dividir todas": Ctrl+Y = depois de dividir | **diferente** (0 em vez de 7) | igual |
| "dividir todas": Ctrl+Z de novo | igual | igual |
| "dividir todas": Ctrl+Y de novo | **diferente** | igual |
| "juntar todas": Ctrl+Z | **diferente** (herdado do Ctrl+Y) | igual |
| "juntar todas": Ctrl+Y | igual | igual |
| motor trocado na folha juntada (D-606): Ctrl+Z | igual | igual |
| motor trocado na folha juntada (D-606): Ctrl+Y | igual | igual |
| "dividir esta" (folha 7): Ctrl+Z | igual | igual |
| "dividir esta" (folha 7): Ctrl+Y | **diferente** (0 em vez de 1) | igual |
| "não dividir esta": Ctrl+Z | **diferente** (herdado) | igual |
| "não dividir esta": Ctrl+Y | igual | igual |

No novo, 14 de 14 iguais (12 na tabela mais os dois Ctrl+Z do "dividir todas"). A tira e a lista do motor não
mudam dados (só onde a tira rola e quem fica com o teclado). O aviso da D-607 só muda texto. A etapa 6 só muda o
desenho da coluna.

## 3. D-608: depois de clicar num botão do painel, as setas continuam passando de página

Pergunta: "Quer que, depois de clicar num botão do painel, as setas continuem passando de página, em todas as
ferramentas? As caixas de número continuam como estão." → "ok".

- As teclas ← →, Page Up/Down, Home e End que chegam a um **botão** da tela de conferir (painel, faixa, barra de
  baixo) vão para a página. É o mesmo filtro único de teclas que já leva a Tab à próxima dúvida
  (`ui/tela_conferir.py`, `_FiltroDaTab` e `TelaConferir._tecla_de_andar_num_botao`).
- Caixa de número, campo de texto, lista e bolinha de opção não são tocados. O Espaço e o Enter continuam apertando o
  botão. Janelas por cima (avisos, Automático) não são tocadas.
- Provas (`tests/test_dividir_ajustes_03_11.py`): clicar "dividir esta" e → anda (← volta, End, Home, Page Down);
  no Cortar, clicar "não cortar esta" e → anda. Os dois falham em `75ed04af`. Guarda: na caixa do ângulo do
  Endireitar a seta ↑ sobe 0,1°, a seta ← não troca de página e o botão de 0,1° gira (D-083).
- Janela de verdade: "Duas lado a lado", clique em "dividir esta", → : "folha 6 de 70"; ← volta à 5 (p10, p11).
  Achado no caminho: com a janela por trás de outra o Qt ainda manda a tecla ao botão, mas o "foco da aplicação" é
  nenhum; a condição usa o teclado da janela (o print pegou isso; o teste sem janela não pegava).
- O que já estava escolhido e testado sobre teclado está no ONDE-PAREI (D-021, 9b-1, 1.10, botões dos avisos, D-083),
  com os testes, que passam sem mudança.

## 4. Testes no PC e velocidade

No PC do Samuel, um arquivo por vez, depois de todos os consertos (commit `42f359a4`): **36 arquivos, todos passaram**. São os 23 de antes, mais o de gravura que tinha falhado uma vez no GitHub, os do histórico e os de teclado (D-021, 9b-1, D-083, atalhos, painéis, promessas). Nenhum teste antigo foi mudado.

- `tests/test_decisoes_dividir_linha.py`: 13 passed in 15.77s
- `tests/test_decisoes_dividir.py`: 21 passed in 47.04s
- `tests/test_decisoes_dividir_metade.py`: 6 passed in 9.68s
- `tests/test_decisoes_juntar_todas.py`: 4 passed in 8.62s
- `tests/test_dividir_desmarcada_caixinha.py`: 3 passed in 11.95s
- `tests/test_dividir_na_tela.py`: 9 passed in 27.85s
- `tests/test_dividir_no_programa.py`: 19 passed in 14.43s
- `tests/test_automatico_pular_depois_de_dividir.py`: 4 passed in 0.40s
- `tests/test_decisoes_automatico.py`: 29 passed in 57.61s
- `tests/test_decisoes_automatico_margens_no_depois.py`: 5 passed in 11.91s
- `tests/test_decisoes_automatico_opcoes_do_filtro.py`: 21 passed in 96.88s (0:01:36)
- `tests/test_decisoes_automatico_ver_como_fica.py`: 22 passed in 75.20s (0:01:15)
- `tests/test_decisoes_9b1.py`: 25 passed, 16 warnings in 30.87s
- `tests/test_decisoes_9b2.py`: 30 passed in 55.75s
- `tests/test_miniaturas_novas.py`: 5 passed in 3.75s
- `tests/test_decisoes_avisos.py`: 22 passed in 47.59s
- `tests/test_decisoes_caderno_tela_grande.py`: 11 passed in 41.54s
- `tests/test_decisoes.py`: 26 passed in 5.12s
- `tests/test_decisoes_tela.py`: 35 passed, 4 warnings in 43.46s
- `tests/test_dividir_ajustes_03_11.py`: 9 passed in 20.21s
- `tests/test_decisoes_filtro_automatico.py`: 4 passed in 17.44s
- `tests/test_decisoes_montar_cadernos.py`: 13 passed in 92.07s (0:01:32)
- `tests/test_menu_paineis.py`: 3 passed in 1.86s
- `tests/test_gravura_na_aba_marcar.py`: 8 passed in 6.70s
- `tests/test_historico_depois_de_reabrir.py`: 11 passed in 0.74s
- `tests/test_recomeco_limpa_o_historico.py`: 13 passed in 42.67s
- `tests/test_endireitar_g5.py`: 13 passed in 7.06s
- `tests/test_endireitar_na_tela.py`: 5 passed in 7.70s
- `tests/test_para_revisar_na_tela.py`: 26 passed in 20.74s
- `tests/test_girar_na_tela.py`: 22 passed in 51.08s
- `tests/test_decisoes_ver.py`: 11 passed in 29.57s
- `tests/test_decisoes_mover.py`: 13 passed in 17.16s
- `tests/test_atalhos.py`: 15 passed in 0.43s
- `tests/test_paineis_na_tela.py`: 22 passed in 59.81s
- `tests/test_barra_de_menu.py`: 20 passed in 4.99s
- `tests/test_promessas.py`: 267 passed, 1 xfailed, 74 warnings in 1055.07s (0:17:35)

Velocidade: não medi no PC (o Samuel: "se está medindo lá porque medir aqui, o mais urgente é concertar os problemas agora"). O filtro do GitHub 41759125497 (`75ed04af` → `abd8cd0a`) fica com a gerente. Os consertos desta segunda parte mexem só em `ui/tela_conferir.py`; nenhum mexe em `core/`. A única mudança em `core/` da tarefa toda é a da 1ª entrega (`core/automatico.py`, `paginas_juntadas`, já dentro do `abd8cd0a`).
