# D-609 — arrastar a linha azul na folha inteira (04/11/2026)

Ramo `dividir-arrastar-2026-11-04` (saiu de `obra-2026-10-26`, `e17410fe`). Commits: `ecf5e3a1` (código e provas),
`6e5b4cdd` (uma linha de um teste antigo, ver Ressalva 1), `2c169489` (prints).

## O que foi feito

Na ferramenta Dividir, a linha azul da folha dupla ainda inteira agora se arrasta com o mouse, com a mesma pega
"arraste", em "Uma página" e em "Duas lado a lado". O "dividir esta" e o "dividir todas" cortam onde a pessoa a deixou;
sem arrastar, continuam cortando na linha do motor.

## Arquivos

- `modelos.py`: campo novo `ConfigFolha.linha_a_mao` = [rotação, motor] em que a linha da folha inteira foi arrastada
  (None = não foi). Projeto antigo: None, sai igual.
- `ui/tela_conferir.py`: `_linha_arrastada`, `_acertar_a_linha_do_dividir` (linha arrastável),
  `_mover_corte` → `_mover_a_linha_da_folha_inteira`, `_dividir_esta`, `_dividir_as_lidas` ("dividir todas"),
  `_trocar_jeito_da_folha` (apaga a marca), `_so_as_divididas` (a medida do "Parece em branco" só nas folhas divididas
  quando só a linha muda, no `_registrar` e no refazer).
- `tests/test_decisoes_dividir_arrastar.py` (novo, 13 provas).
- `tests/test_decisoes_dividir_linha.py`: só a linha 127 (Ressalva 1).
- `relatorios/dividir-arrastar/`: ONDE-PAREI, piloto, anotações e prints.

## Como cumpri cada uma

| Decisão | Como | Prova |
|---|---|---|
| D-609 arrastar na folha inteira | linha com pega e arrasto em "Uma página" e "Duas lado a lado" | `test_reversao_d609_linha_se_arrasta_na_folha_dupla_inteira[uma/duas]`; prints p02 (Uma página, folha 2) e p06 (Duas, folha 4) |
| D-609 "dividir esta" corta onde ficou | usa `posicao_corte` arrastada | `test_reversao_d609_dividir_esta_corta_onde_a_linha_ficou`; p03 (metade esquerda estreita) e p04 (corte em 40%) |
| D-602 sem arrastar, linha do motor | inalterado | mesma prova (a outra folha) + `test_decisoes_dividir_linha.py` |
| D-602 folha de uma página sem linha | inalterado; mouse nela não grava nada | `test_d609_folha_de_uma_pagina_continua_sem_linha_e_o_mouse_nao_mexe` |
| Desfazer/refazer | arrasto = 1 ação; Ctrl+Z/Ctrl+Y duas vezes devolvem páginas, folhas, linha, avisos, "com dúvida" e botão iguais | `test_d609_desfazer_e_refazer_...`, `test_d609_ctrl_z_do_teclado_volta_a_linha`; piloto com Ctrl+Z/Ctrl+Y do Windows (anotacoes.txt) |
| D-606 trocar o motor | a marca sai na mesma ação; a linha vai para a do motor novo; Ctrl+Z devolve motor e linha arrastada | `test_d609_trocar_o_motor_depois_de_arrastar_refaz_a_conta` |
| "dividir todas" | a arrastada na sua linha; as outras, na do motor; uma ação | `test_d609_dividir_todas_corta_a_arrastada_...` |
| D-090 "usar em todas" | copia a linha desta folha (a arrastada); a folha arrastada vem desmarcada (marca "mexida à mão") | `test_d609_usar_em_todas_copia_a_linha_arrastada`, `..._deixa_desmarcada_a_folha_arrastada` |
| D-498 folha juntada | se arrasta; "dividir esta" devolve as páginas como estavam, cortadas onde ficou | `test_d609_folha_juntada_arrastada_volta_como_estava_na_linha_nova` |
| D-608 setas | depois de arrastar, → passa de folha | `test_d609_seta_passa_de_folha_depois_de_arrastar`; piloto (folha 4 → 5) |
| D-601 | "Uma página" mostra a metade depois de dividir; frase da barra igual | p03; `test_decisoes_dividir_metade.py` |
| Item 7 (nada além) | nenhuma frase, botão ou lugar mudou ("Esta folha não vai ser dividida." igual, p02/p06) | prints |
| D-605 | "O que já está escolhido e testado" no ONDE-PAREI; testes antigos do Dividir passando | abaixo |

Reversão: em `e17410fe`, 11 das 13 provas falham; as 2 que passam lá são as das escolhas que continuam (folha de uma
página, seta).

## Ressalvas

1. **Um teste antigo tinha de mudar.** `test_decisoes_dividir_linha.py::test_reversao_d602_...` (linha 127) dizia
   `assert not vista.corte_arrastavel`, com o comentário "a linha da folha inteira é só para ver: arrastar não muda
   nada (pergunta ao Samuel)". É exatamente o que a D-609 tira (resposta "Sim" à pergunta `d602-arrastar`). Troquei
   só essa linha para `assert vista.corte_arrastavel`, num commit separado (`6e5b4cdd`) para a gerente conferir ou
   tirar. O resto do teste ficou igual.
2. **Escolhas técnicas minhas (D-014), para a gerente conferir:**
   - Arrastar na folha inteira **não** marca a folha como "conferida" (na dividida, marca). Motivo: ela ainda não foi
     dividida; o "dividir esta" marca. Assim o "N de M conferidas" e o "com dúvida" não mudam só por arrastar.
   - A linha arrastada vale na rotação e no motor em que foi arrastada: girar a folha mostra a linha do motor na folha
     girada (o Ctrl+Z do giro devolve a arrastada). Sem isso, a linha cairia num lugar sem sentido na folha girada.
   - Soltar a linha onde ela já estava não grava nada.
   - A medida do "Parece em branco" (D-497) deixou de rodar quando só a linha de uma folha **inteira** muda (no
     arrasto, no refazer e no "usar em todas" em folhas inteiras): a página dela não muda, e medir pararia a medida que
     já andava (ex.: logo depois de um "dividir esta"). Nas folhas divididas continua igual.
   - Na folha juntada, arrastar e depois "dividir esta" devolve as páginas como estavam (D-498) **na linha nova**
     (D-609 é a mais recente); sem arrastar, na linha de antes, como sempre.
3. O desfazer do "dividir esta" devolve `conteudo_deslocamento` das páginas como lista em vez de tupla (mesmo valor).
   Já era assim antes; não muda nada na tela. A prova compara pelo jeito do projeto.json.
4. Não rodei o filtro de velocidade: não mexi em `core/`.

## Testes

- PC, um arquivo por vez: ver a seção "Rodadas".
- GitHub: ver a seção "Rodadas".

## Ideias para a Lista de espera / bugs para a Lista de bugs

- (Observação, não mexi) Numa folha inteira **sem arrastar**, o "usar em todas" copia o `posicao_corte` guardado
  (o meio de fábrica, 0,5), e não a linha do motor que a tela mostra. E nas folhas inteiras que recebem a linha do
  "usar em todas", a tela continua mostrando a linha do motor (D-602 "fica como está"). Pode valer uma pergunta ao
  Samuel.

## Rodadas
