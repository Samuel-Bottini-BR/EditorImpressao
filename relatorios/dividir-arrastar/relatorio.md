# Dividir: D-609, D-610 e D-611 (04/11/2026)

Ramo `dividir-arrastar-2026-11-04` (saiu de `obra-2026-10-26`, `e17410fe`). Nada foi juntado.

## O que foi feito

- **D-609:** na folha dupla ainda inteira, a linha azul agora se arrasta com o mouse (mesma pega "arraste"), em "Uma
  página" e em "Duas lado a lado". "dividir esta" e "dividir todas" cortam onde ela ficou; sem arrastar, na linha do
  motor, como antes.
- **D-610:** dividir ("dividir esta" ou "dividir todas") com a vista em "Duas lado a lado" passa a vista sozinha para
  "Uma página"; a seta anda uma página por vez.
- **D-611:** com "Duas lado a lado" escolhida, a tira de miniaturas fica em pares (a 1 sozinha à direita, 2-3, 4-5...),
  em toda ferramenta; em "Uma página", como está.

Commits: `ecf5e3a1` (D-609), `6e5b4cdd` (uma linha de teste antigo, Ressalva 1), `2c169489` (prints D-609),
`bbecf4f7` (D-610), `784a5bf6` (fim de um teste antigo, Ressalva 1), `2fccd164` (D-611), `d7f1082f` (prints D-610/611).

## Arquivos

- `modelos.py`: campo novo `ConfigFolha.linha_a_mao` = [rotação, motor] do arrasto na folha inteira (None = não
  arrastada; projeto antigo: None, sai igual).
- `ui/tela_conferir.py` (só o Dividir e a barra Uma página / Duas lado a lado; nada do Mover): `_linha_arrastada`,
  `_acertar_a_linha_do_dividir`, `_mover_a_linha_da_folha_inteira`, `_dividir_esta`, `_dividir_as_lidas`,
  `_trocar_jeito_da_folha`, `_so_as_divididas`, `_uma_pagina_depois_de_dividir`, uma linha em
  `_acertar_a_vista_da_pagina` (D-611).
- `ui/widgets/tira_miniaturas.py`: `definir_pares_pela_vista`, `em_pares_agora` (D-611).
- Testes novos: `tests/test_decisoes_dividir_arrastar.py` (16), `tests/test_decisoes_tira_em_pares.py` (4).
- Testes antigos mudados: uma linha em `tests/test_decisoes_dividir_linha.py`, o fim de um teste em
  `tests/test_dividir_na_tela.py` (Ressalva 1).
- `relatorios/dividir-arrastar/`: ONDE-PAREI, piloto, anotações, prints p01 a p12.

## Como cumpri cada uma

| Decisão | Como | Prova |
|---|---|---|
| D-609 arrastar na folha inteira | pega "arraste" e arrasto em "Uma página" e "Duas" | `test_reversao_d609_linha_se_arrasta_na_folha_dupla_inteira[uma/duas]`; p02 (Uma página, folha 2 em 40%), p06 (Duas, folha 4 em 55%) |
| D-609 "dividir esta" corta onde ficou | usa a linha arrastada | `test_reversao_d609_dividir_esta_corta_onde_a_linha_ficou`; p03 (metade esquerda estreita), p04 (corte em 40%) |
| D-602 sem arrastar, linha do motor; uma página só sem linha | igual | mesmos testes + `test_d609_folha_de_uma_pagina_continua_sem_linha_e_o_mouse_nao_mexe` + `test_decisoes_dividir_linha.py` |
| Desfazer/refazer | o arrasto é 1 ação; Ctrl+Z/Ctrl+Y duas vezes devolvem páginas, folhas, linha, avisos, "com dúvida" e o botão iguais | `test_d609_desfazer_e_refazer_...`, `test_d609_ctrl_z_do_teclado_volta_a_linha`; piloto com Ctrl+Z/Ctrl+Y do Windows (anotacoes.txt, p05) |
| D-606 trocar o motor depois de arrastar | refaz a conta; Ctrl+Z devolve motor e linha arrastada | `test_d609_trocar_o_motor_depois_de_arrastar_refaz_a_conta` |
| "dividir todas" | a arrastada na sua linha; as outras na do motor | `test_d609_dividir_todas_corta_a_arrastada_...` |
| D-090 "usar em todas" | copia a linha desta folha; a arrastada vem desmarcada | `test_d609_usar_em_todas_*` |
| D-498 folha juntada | se arrasta; volta como estava, cortada onde ficou | `test_d609_folha_juntada_arrastada_volta_como_estava_na_linha_nova` |
| D-608 setas | depois de arrastar, → passa de folha | `test_d609_seta_passa_de_folha_depois_de_arrastar`; piloto (folha 4 → 5) |
| D-610 | "dividir esta"/"dividir todas" em Duas → Uma página; seta: metade direita, depois folha 2; arrastar e juntar não trocam a vista | `test_reversao_d610_*`, `test_d610_arrastar_em_duas_lado_a_lado_nao_troca_a_vista`; p07 → p08, anotações (seta: página 2, depois folha 2) |
| D-611 | tira em pares com Duas (Dividir e Cortar); uma a uma com Uma página; "Ver em pares" do menu não muda nem é gravado; escolhida marcada, à vista, clique vai a ela | `test_decisoes_tira_em_pares.py` (4); p09/p09b, p10/p10b (Dividir), p11/p12 (Cortar) |
| Item 7 (nada além) | nenhuma frase, botão ou lugar mudou | prints |
| D-605 | "O que já está escolhido e testado" no ONDE-PAREI; testes do Dividir e da tira passando | Rodadas |

Reversão (código de `e17410fe`): 14 das 16 provas do arrastar/D-610 falham e as 2 de reversão da tira falham; as que
passam lá são as das escolhas que continuam (folha de uma página sem linha, seta depois de arrastar, "Ver em pares" do
menu, a escolhida). Saída em `_tmp/reversao_todas.txt` (fora do git).

## Ressalvas

1. **Dois testes antigos tiveram de mudar, porque provavam justamente o que as decisões novas tiram** (commits
   separados, para a gerente conferir ou tirar):
   - `test_decisoes_dividir_linha.py`, linha 127: `assert not vista.corte_arrastavel`, comentada "a linha da folha
     inteira é só para ver: arrastar não muda nada (pergunta ao Samuel)". A D-609 respondeu "Sim" a essa pergunta
     (`d602-arrastar`). Agora `assert vista.corte_arrastavel`. Só essa linha.
   - `test_dividir_na_tela.py::test_linha_azul_some_quando_a_folha_nao_e_dividida`: dividia de novo em "Duas lado a
     lado" e esperava a linha à vista porque a vista ficava (D-601). Pela D-610 a vista vai para "Uma página"; o teste
     agora confere isso e volta ao "Duas lado a lado" para ver a linha. O que ele prova (a linha some ao juntar e volta
     ao dividir) continua.
2. **Escolhas técnicas minhas (D-014), para conferir:**
   - Arrastar na folha inteira **não** marca a folha como conferida (na dividida, marca): ela ainda não foi dividida;
     o "dividir esta" marca. Assim "N de M conferidas" e "com dúvida" não mudam só por arrastar.
   - A linha arrastada vale na rotação e no motor em que foi arrastada: girar a folha mostra a linha do motor na folha
     girada (o Ctrl+Z do giro devolve a arrastada).
   - Soltar a linha onde ela já estava não grava nada.
   - A medida do "Parece em branco" (D-497) não roda mais quando só a linha de uma folha **inteira** muda (arrasto,
     refazer, "usar em todas" em folhas inteiras): a página dela não muda, e medir pararia a medida que já andava.
   - Folha juntada, arrastada e dividida: as páginas voltam como estavam (D-498), cortadas na linha nova (D-609).
   - D-610: o Ctrl+Z do corte não volta a vista para "Duas lado a lado" (a vista não entra no desfazer, como sempre).
   - D-611: os pares são o mesmo arranjo do "Ver em pares" que já existia (6 px dentro do par, 22 px entre pares; p10b).
     O item "Ver em pares" do menu continua mostrando a escolha da pessoa (desmarcado), mesmo com a tira em pares por
     causa do "Duas lado a lado".
3. **GitHub, rodada 1 (`41785344022`, só a D-609):** parte 1 falhou com um ERRO no fim de
   `test_promessas.py::test_p083_jeitos_no_automatico[Guardar tudo-tudo]`: uma prévia por trás procurou o PDF do teste
   depois de ele ser apagado ("Não consegui achar esse arquivo"). É do Automático, não do Dividir. No PC, o `-k p083`
   deu 1 erro do mesmo tipo (noutro caso, `p083_jeitos_do_so_as_letras[rede]`) em 8 rodadas com o código novo e 0 em 3
   com o antigo. O mesmo ERRO aconteceu no ramo de outro agente, sem nada destas mudanças (`caderno-etapas`, rodada
   `41777456037`), e na rodada 2 deste ramo (os dois casos); repetida só a parte 1 da rodada 2, passou. Leio como
   intermitente e anterior a esta tarefa, mas fica a ressalva: apareceu nas duas primeiras tentativas daqui.
4. Não rodei o filtro de velocidade: não mexi em `core/` (só `modelos.py`, um campo novo).
5. O desfazer do "dividir esta" devolve `conteudo_deslocamento` das páginas como lista em vez de tupla (mesmo valor);
   já era assim. A prova compara como o projeto.json grava.

## Perguntas para o Samuel (também no ONDE-PAREI)

1. **D-611 no Dividir, com folhas ainda inteiras:** a tira junta de dois em dois pela ordem (1 sozinha; 2-3; 4-5).
   No Dividir, cada miniatura de folha inteira já é a folha dupla; então a tira junta, por exemplo, a capa (metade da
   folha 1) com a folha 2 inteira, e a folha 3 inteira com a folha 4 inteira (p10b). Quer assim, ou no Dividir prefere
   que cada folha fique junta (as duas metades da folha dividida lado a lado, como a vista grande mostra a folha
   inteira)?
2. **D-611, aparência:** os pares ficam com um vão pequeno entre as duas miniaturas do par e um vão um pouco maior entre
   um par e outro (o mesmo do "Ver em pares" que já existia; p10b). Quer as duas miniaturas do par encostadas, como no
   livro aberto?

## Ideias / bugs

- (Observação, não mexi) Numa folha inteira **sem arrastar**, o "usar em todas" copia o `posicao_corte` guardado (0,5
  de fábrica), não a linha do motor que a tela mostra; e nas folhas inteiras que recebem a linha, a tela continua
  mostrando a do motor (D-602 "fica como está"). Pode valer uma pergunta.

## Rodadas

- PC, um arquivo por vez (código final): `test_decisoes_dividir_arrastar` 16, `test_decisoes_dividir_linha` 13,
  `test_decisoes_dividir` 21, `test_dividir_ajustes_03_11` 9, `test_decisoes_juntar_todas` 4, `test_dividir_na_tela` 9,
  `test_decisoes_dividir_metade` 6, `test_dividir_no_programa` 19, `test_dividir_scantailor` 13,
  `test_dividir_desmarcada_caixinha` 3, `test_automatico_pular_depois_de_dividir` 4, `test_decisoes_9b2` 30,
  `test_decisoes_avisos` 22, `test_visualizador` 70, `test_decisoes` 26, `test_decisoes_tira_em_pares` 4,
  `test_miniaturas_novas` 5 — todos passaram.
- GitHub rodada 1 `41785344022` (D-609, `6e5b4cdd`): partes 2-5 e "Botões e prints da janela real" passaram; parte 1
  com 1 erro (Ressalva 3).
- GitHub rodada 2 `41788480788` (tudo, `d7f1082f`): 1ª tentativa, parte 1 com os 2 erros do p083 (Ressalva 3), o
  resto passou; 2ª tentativa (só a parte 1 de novo): **passou**. Conjunto inteiro + `teste_botoes.py` verdes.
