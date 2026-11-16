# Disco cheio na rodada de 16/11/2026: o que se achou

**Resposta curta: não consegui fazer nenhum teste encher o disco. O culpado NÃO foi achado.**

## Em qual teste a saída parou
A saída parcial tem 3554 caracteres (49 linhas de 72 + 26). A coleta (`--collect-only`) tem 3699 testes. Contando, o teste que estava rodando quando a saída parou é:

`tests/test_trilha_agrupada.py::test_os_menus_ficam_a_esquerda_em_todas_as_telas` (o 3555o). O último que terminou foi `test_as_setinhas_do_angulo_mudam_de_cor_com_o_tema`.

Os que falharam (posição na rodada):
- F 536: `test_converter_zonas_ao_abrir.py::test_janela_converte_por_tras_sem_congelar_e_mostra_o_andamento`
- F 1472 e 1473: `test_decisoes_tira_pares_juntas.py::test_d611_uma_pagina_continua_uma_a_uma_com_o_mesmo_vao` e `::test_d611_ver_em_pares_do_menu_continua_com_o_jeito_aprovado`
- F 2018: `test_girar_na_tela.py::test_as_teclas_do_giro_nao_brigam_com_nenhuma_outra`
- F 2047: `test_gravar_por_tras.py::test_folhear_com_o_disco_lento_nao_para_a_janela`
- F 3129: `test_sem_janela_na_tela.py::test_caixa_modal_sem_resposta_e_fechada_pelo_vigia_e_o_teste_falharia`
- E 3130: `test_sem_janela_na_tela.py::test_caixa_respondida_a_tempo_nao_e_afetada`
- F 3394: `test_tirar_da_lista_nao_volta.py::test_tirar_com_o_relogio_contando_nao_traz_de_volta`

(Eram 7 F e 1 E, não 2 F e 1 E.) Todos são testes de tempo ou de tela.

## O que rodei (sempre um arquivo ou teste por vez, com vigia)
O vigia (`D:gente_discoigia.py`) olha a cada 2 s o livre do C: e o tamanho das pastas de teste, e mata tudo se passar de 1 GB ou do tempo. Pasta de teste em `D:gente_discot`.
- O teste "parado" sozinho: passou em 7 s, pico de 15 MB.
- Todos os arquivos que vêm depois dele na ordem (trilha_agrupada, trilha_e_opcoes, trocar_de_livro_grava, unidades_e_perfis, visualizador, zonas_na_folha, zoom_no_ponteiro): todos passaram, pico máximo 68 MB.
- Os arquivos anteriores que mais escrevem (trabalho_nao_se_perde, tirar_fundo_no_programa, substituir_e_cancelar, teste_velocidade, sem_janela_na_tela, gravar_por_tras): todos passaram, pico máximo 68 MB.
- Os 3 arquivos juntos, na ordem, num só processo (tirar_fundo + trabalho_nao_se_perde + trilha_agrupada): 155 passaram em 7 min, pico 68 MB.
- Os 7 testes que deram F/E: **todos passam quando rodados sozinhos** (e o arquivo `test_gravar_por_tras.py` e `test_sem_janela_na_tela.py` inteiros também). Não rodei no ramo `obra-2026-10-26` porque não há falha para comparar.
- O C: ficou em 29,4 GB livres o tempo todo; nada cresceu.

## O que explica os F e o E
- O E de `test_sem_janela_na_tela` vem do F logo antes: esse teste deixa a lista `_CAIXAS_SEM_RESPOSTA` suja quando falha antes da linha `clear()`, e o teste seguinte quebra. É efeito dominó, não defeito novo.
- Os outros F são de tempo (janela que "não pode ficar parada mais de 0,5 s", relógio, disco lento de mentira). Sozinhos passam. Com a máquina sufocada (disco enchendo, outro pytest rodando) eles falham por lentidão. Ou seja: provavelmente são **consequência** da pressão no disco/CPU, não a causa. Mas isto é hipótese, não provei.

## Por que não achei o que escreve sem parar
Não há no código nenhum teste com laço de gravação sem fim. Os testes de "disco cheio" (`test_core.py`, `test_substituir_e_cancelar.py`, `test_gravar_por_tras.py`, `test_trabalho_nao_se_perde.py`, `test_historico_depois_de_reabrir.py`, `test_zonas_na_folha.py`) só fazem uma função levantar `OSError`, e nenhum escreve de verdade; todos passaram com pico minúsculo.

## O que provavelmente aconteceu (hipóteses, em ordem)
1. Havia **outro processo escrevendo** na mesma hora: os arquivos de andamento mostram, na mesma sessão, a rodada de `test_promessas` (que a gerente tirou da rodada com `--ignore`), a do `teste_botoes` e uma de `kaique-etapa3` em paralelo. Quando comecei, havia um `pytest tests/test_promessas.py` de outra cópia (aberto 15:50, 4 GB de memória) com servidores `core.paginas_em_outro_processo` filhos. Ainda assim, o C: ficou estável durante meu trabalho com ele rodando, então não é prova.
2. Um dos servidores de páginas (`core.paginas_em_outro_processo`, processo filho do pytest, "dois processos python") ficou preso depois que um teste de tempo falhou, e escrevia cache/miniaturas na pasta temporária. Combina com "matar os dois processos e apagar `pytest-3671` devolveu 27 GB", mas não consegui reproduzir.
3. O Windows pode ter parado a saída por outra razão (suspensão, antivírus), e o disco encher ser outro assunto (por exemplo, arquivo de paginação ou outro programa).

## Ideia de conserto (não feita)
- Rodar a rodada completa com `--basetemp` em D: e com um vigia (como o meu) que mata se o C: perder 1 GB ou se a saída ficar parada por 10 min. Assim, se repetir, a pasta e o teste ficam preservados para olhar antes de apagar.
- Pedir ao pytest `-p timeout` (plugin pytest-timeout, `--timeout=300`) para qualquer teste travado virar falha com a pilha impressa.
- Fazer `test_sem_janela_na_tela` limpar `_CAIXAS_SEM_RESPOSTA` num `try/finally`, para um F não derrubar o teste seguinte.
- Ao reencontrar o problema, anotar na hora qual processo cresce (`Get-Process` e `Get-CimInstance Win32_Process`).

Limite desta investigação: reproduzi por partes (um arquivo por vez), nunca o conjunto inteiro, como combinado. Interação que só aparece na rodada inteira pode ter escapado.
