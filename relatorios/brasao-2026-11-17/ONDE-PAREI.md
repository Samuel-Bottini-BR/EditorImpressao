# ONDE-PAREI — brasão girando e ícone (17/11/2026)

Ramo `brasao-2026-11-17`, cópia `.claude/worktrees/brasao`, criada de `kaique-juntar-2026-11-17` (1a42dfb0).
Agente implementador (tela). Sem push (pedido da gerente).

## Decisões que esta tarefa precisa cumprir

- **D-744** (17/11): "o brasão do projeto está na area de tarbalho: brasão.ai pode fazer um motion dela girando em 3d sem
  mudar nada no brasão, tem que continuar exactamente igual só com o movimento enquanto carrega o programa e pode mudar o
  icone do programa também para esse brasão." · "entra agora na versão que vai ser enviada para ele."
- **D-745** (17/11): "A" (dá a volta inteira, como uma moeda girando) · "dá para ser sem fundo?" → de costas aparece de
  frente outra vez, sem espelhar; sem fundo e sem quadro, solto por cima da tela.
- **D-746** (17/11): "Sim, mas eu quero ver um exemplo" → o ícone é o brasão inteiro em todos os tamanhos (16 a 256),
  desenhado direto do vetor em cada tamanho, nunca uma imagem diminuída. Antes: "eu mandei um arquivo em .ai que daria
  para vetorizar sem problemas, porque não fez isso?"
- **D-747** (17/11): "brasão aprovado" — igual à página de exemplo
  (`D:\programas\EditorImpressao-arquivos\brasao-previas-17-11\exemplo-brasao.html`): uma volta a cada 2,5 s, sem fundo,
  de costas sem espelhar; ícone do vetor em cada tamanho.
- Tocadas de raspão: **D-736** (na conta dos testes à distância o programa só faz o necessário), **D-742** (a janelinha
  "Atualizando o programa...": não juntar com o brasão sem perguntar), **D-605/§11.8** (o novo não estraga o testado).

## O que já está escolhido e testado aqui

- `main.py`: a ordem dos modos sem janela (`--servidor-de-paginas`, `--conferir-ocr`, depois
  `atender_linha_de_comando(sys.argv)` uma vez só) e `ligar_na_janela(janela)` uma vez só
  (`tests/test_decisoes_atualizacao.py::test_o_main_chama_a_atualizacao_por_um_ponto_so`); nenhum token no main
  (`test_d719_nenhum_token_dentro_do_programa`); nenhum botão do Qt em inglês em `ui/` e `main.py`
  (`tests/test_botoes_em_portugues.py`); nenhum "quer salvar?" (`tests/test_salva_sozinho.py`).
- `empacotar.py`: o comando do PyInstaller e do vpk (`tests/test_empacotar.py`, `tests/test_empacotar_teste_velocidade.py`,
  `tests/test_decisoes_atualizacao.py` D-714/D-727).
- `instalador.iss`: versão de fora, [UninstallDelete], travas (`tests/test_empacotar.py`, `test_decisoes_atualizacao.py`,
  `test_decisoes_testes_a_distancia.py`).
- Nenhum teste abre janela na tela (`tests/test_sem_janela_na_tela.py`, `tests/conftest.py`).
- Nada disso muda: só acrescento. Nenhum teste antigo foi mexido.

## Como fica para quem usa e no livro (D-637)

- O Kaique clica no ícone do programa (agora o brasão). Logo aparece o brasão girando no meio da tela, sem quadro e sem
  fundo, por cima do que estiver aberto, uma volta a cada 2,5 s. Ele não aparece na barra de tarefas, não pega clique
  nem foco.
- Quando a janela do programa aparece, o brasão some.
- O ícone do brasão aparece na barra de tarefas, no título das janelas, no atalho, no menu Iniciar e no instalador.
- O PDF que sai não muda nada (nada de processamento foi tocado).

## A regra num lugar só (§11.12)

- Medidas, caminhos e escalas: `brasao.py` (um lugar só). Usado por `gerar_brasao.py`, `ui/brasao_girando.py`,
  `ui/tela_de_carregamento.py`, `main.py` e `empacotar.py`.
- O desenho do giro: `ui/brasao_girando.pintar` — a janela (paintEvent) e as fotos/testes (`desenhar_quadro`) usam a
  mesma função.
- Quando aparece / quando não aparece: `ui/tela_de_carregamento.nao_mostrar` (único lugar).
- Caminhos que chegam no ícone: janela (`app.setWindowIcon` no `main.py`), `.exe` e atalhos (`--icon` do PyInstaller),
  instalador Velopack (`--icon` do vpk), instalador Inno de reserva (`SetupIconFile`). Todos leem `brasao.ICONE`
  (o `.iss` tem o caminho escrito, conferido por teste).

## Como o giro fica liso (pedido: "se o carregamento travar o laço do Qt, explique")

Medido aqui (17/11, offscreen, com o PC já aquecido): importar a janela 0,4 s, montar 1,2 s, mostrar 0,4 s — tudo na linha
principal do Qt; a frio, a primeira medida deu 8,8 s + 13,8 s + 3,5 s. Nesse tempo um brasão no mesmo processo ficaria
parado. Solução: o brasão roda **num processo a parte** (o mesmo programa com `--brasao-girando <número do processo>`),
aberto no começo do `main()`, antes dos imports pesados. Ele tem o laço do Qt só para ele. O programa fecha esse processo
quando a janela principal aparece; se o programa morrer antes, o processo do brasão percebe (a cada 0,2 s) e fecha; e há
um limite de 3 minutos.

## Perguntas para o Samuel

**1. A janelinha "Atualizando o programa" e o brasão aparecem juntos?** Só numa abertura: chegou versão nova, o Kaique
clicou "Depois" e abre o programa de novo. Primeiro aparece a janelinha "Atualizando o programa, espere um pouco..."
enquanto a troca acontece; quando o programa reabre, o brasão começa a girar, e a janelinha só some quando a janela do
programa aparece. Por alguns segundos os dois ficam no meio da tela, um em cima do outro. Hoje está assim (não juntei).
O que você escolhe: (sugiro) quando o brasão aparece, a janelinha some na hora / os dois juntos, como hoje / na abertura
da troca, só a janelinha. Nada do que já funciona muda em nenhuma. Print: falta (precisa da troca de verdade, etapa 5).

## Como cumpri cada decisão

- D-744 (girar sem mudar o desenho, enquanto carrega; ícone): `test_d744_de_frente_o_desenho_e_o_vetor_sem_mudar_nada`,
  `test_d744_o_brasao_some_quando_a_janela_principal_abre`, `test_d744_o_main_abre_o_brasao_antes_dos_imports_pesados`;
  print 01.
- D-745 (volta inteira, de costas sem espelhar, sem fundo e sem quadro):
  `test_d745_de_costas_o_quadro_e_igual_ao_de_frente_nunca_espelhado`, `test_d745_de_lado_vira_uma_faixa_fina`,
  `test_d745_a_janela_e_transparente_sem_moldura_por_cima_e_fora_da_barra`; print 01.
- D-746 (ícone inteiro, do vetor em cada tamanho): `test_d746_*` (6 provas); prints 03 e 04.
- D-747 (igual à página de exemplo, 2,5 s): `test_d747_o_giro_e_o_da_pagina_de_exemplo_ponto_por_ponto`,
  `test_d747_uma_volta_a_cada_dois_segundos_e_meio`; print 02 (lado a lado com a página).
- D-736 (conta dos testes à distância): `test_d744_nunca_aparece_nos_testes_nem_na_conta_dos_testes_a_distancia`.
- D-742: não mexido; virou a pergunta 1.

## Andamento

- [x] Ler regras, decisões, página de exemplo.
- [x] Copiar o .ai para `arte/brasao/brasao.ai`; `brasao.py`; `gerar_brasao.py`; `recursos/brasao/` gerado.
- [x] `ui/brasao_girando.py`, `ui/tela_de_carregamento.py`, `main.py`, `empacotar.py`, `instalador.iss`.
- [x] Testes novos `tests/test_decisoes_brasao.py` (19 passaram).
- [x] Prints offscreen (`prints/`) e relatório (`relatorio.md/.html/.pdf`).
- [x] Testes pedidos, um arquivo por vez: todos passaram; `teste_botoes.py` 372 ações, 0 falhas.
- Entregue à gerente: PRONTO PARA CONFERIR. Falta: verificador olhar numa tela de verdade; `.exe` na etapa 5.

## 17/11 (tarde): D-748 e a pasta do Agendador (D-731)

- [x] D-748 ("Sim"): a janelinha some quando o brasão aparece; nunca juntos. Commit 5a407a6f. Teste de reversão
  falhou no código de antes (brasão 19,9 s antes de a janelinha sumir).
- [~] D-731, pasta vazia "EditorImpressao" no Agendador: feito no ramo `brasao-2026-11-17-pasta-agendador`
  (0d41b711), FORA do ramo principal, porque quebra o teste antigo
  `test_decisoes_desinstalar.py::test_d731a_sem_os_testes_ligados_desinstalar_apaga_a_tarefa_da_atualizacao` (a
  proteção dele recusa o serviço do Agendador). Pergunta: posso mudar a proteção para aceitar o Agendador de
  mentira e juntar? Sugestão: sim.
- Testes pedidos (um por vez, offscreen, basetemp brasao2): todos passaram; `teste_botoes.py` 372 ações, 0 falhas.
- Cópia de antes para as provas: `D:\agente_temp_testes\brasao2-antigo` (worktree, fora do projeto, não apagada).
