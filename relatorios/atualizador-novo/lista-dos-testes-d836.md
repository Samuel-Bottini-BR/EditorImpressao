# Os testes antigos do atualizador, teste por teste (D-836)

Atualizador novo, 23/11/2026. Ramo `atualizador-novo-2026-11-23`. Para o Fable conferir antes de "quem tenta quebrar".

Palavras do Samuel (chat 23/11, pergunta 5 do plano): "5 – não quero ver antes, mas a lista dos testes vai para o Fable
conferir na entrega". A regra (D-836): os testes que conferem peças que saem **saem**, e cada decisão que eles cobravam
e continua valendo ganha um teste novo pelo caminho novo; os que cobram as mesmas decisões **passam a chamar o caminho
novo** (adaptado); os que cobram decisões que ele mudou **passam a cobrar o que vale hoje**. Teste fora do atualizador
não foi mexido.

Legenda: **saiu** (a peça que ele conferia saiu) · **adaptado** (mesmo nome, a mesma conferência pelo caminho novo) ·
**vale hoje** (a decisão mudou; cobra a de hoje; às vezes com nome novo) · **igual** (nenhuma linha mudou).
Os testes novos que substituem estão em `tests/test_atualizador_novo.py` (o executor, as 13 proteções),
`tests/test_fases_da_atualizacao.py` (a regra inteira, 807 casos), `tests/test_windows_preparo_do_computador.py` (a
peça do Windows), `tests/test_velopack_de_verdade.py` (a biblioteca de verdade) e
`tests/test_porteiro_licenca_que_acrescenta.py` (a K03, D-837). A comparação foi feita pela árvore do código contra a
ponta `fda954aa` (o plano).

## tests/test_decisoes_atualizacao.py (38 antes, 35 agora)

| Teste | O que aconteceu | Decisão | O que cobra agora / quem substitui |
|---|---|---|---|
| test_d714_a_tarefa_roda_ao_ligar_como_o_sistema_sem_janela | saiu | D-714 (a parte "ao ligar" já trocada pela D-732) | o ajudante saiu; a procura é só ao abrir: `test_atualizador_novo::test_d732_a_procura_e_so_ao_abrir_nada_roda_por_tras_depois` e a tabela da regra |
| test_d714_criar_e_apagar_a_tarefa_pelo_schtasks | saiu | D-714 | não há tarefa a criar: `test_atualizador_novo::test_d731_o_atualizador_novo_nao_poe_tarefa_no_windows`, `::test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta` |
| test_d714_programa_fechado_baixa_e_troca_e_reabre_escondido_para_conferir | saiu | D-714/D-718 | quem trocava com o programa fechado era o ajudante; hoje a troca do "Sim" ao fechar: `test_atualizador_novo::test_d831_depois_e_sim_ao_fechar_troca_sem_janela`, `::test_d769_reabertura_sem_janela_que_passa_sai_sem_janela` |
| test_d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga | vale hoje (nome novo: test_d720_depois_do_depois_a_versao_entra_ao_fechar) | D-720 → D-769, D-794, D-831 | "Depois" não troca; fechar pergunta; "Sim" troca |
| test_d723_o_portatil_nunca_cria_nem_apaga_a_tarefa | saiu | D-723 | o portátil não pergunta nem procura: `test_decisoes_atualizacao::test_d723_o_pacote_portatil_do_ensaio_nunca_mexe_no_windows` (adaptado), `test_atualizador_novo::test_o_portatil_nao_pergunta_nem_procura`, `test_decisoes_desinstalar::test_d731_desinstalar_o_portatil_nao_manda_nada` |
| test_d724_versao_com_assinatura_errada_e_recusada_antes_de_baixar | adaptado | D-724 | o executor de verdade; não baixa; "não tentar" |
| test_d724_versao_sem_arquivo_de_assinatura_e_recusada | adaptado | D-724 | idem, sem o arquivo da assinatura |
| test_d724_pacote_trocado_depois_de_assinado_e_recusado | adaptado | D-724 | o índice com outra soma que a assinada |
| test_d724_versao_que_ja_falhou_nao_e_tentada_de_novo | adaptado | D-724/D-718 | só procura; nada baixado |
| test_d715_programa_aberto_fica_pendente_e_a_tela_avisa | adaptado | D-715 | a janela recebe o aviso; nada trocado |
| test_sem_internet_nao_e_falha_e_nao_avisa | adaptado | D-719 | nada na tela, nada anotado |
| test_d720_o_aviso_tem_reiniciar_agora_e_depois_e_depois_nao_troca | adaptado + vale hoje (o texto, D-835) | D-720, D-835 | pela `PonteDaTela` de verdade: os dois botões e a frase nova |
| test_d720_reiniciar_agora_fecha_gravando_e_so_depois_troca | adaptado | D-720, D-828 | fecha pela janela antes de trocar; janela que recusa fechar não troca |
| test_d835_ao_fechar_a_pergunta_curta_e_o_sim_esconde_a_janela_e_troca | novo | D-835, D-831 | a caixa "Atualizar agora?" palavra por palavra; "Sim" esconde e troca; "Não" não troca |
| test_pelo_codigo_o_aviso_nao_liga | adaptado | D-728 | sem executor da abertura, nada liga |
| test_d719_a_falha_aparece_na_tela_uma_vez_so | adaptado | D-719, D-778 | uma vez por conta, com a frase do caso |
| test_d719_o_erro_vai_para_o_registro_no_programdata | adaptado | D-719 | `anotar_falha` (o nome da função única mudou) |
| test_d718_versao_nova_que_nao_passa_no_teste_volta_para_a_anterior | adaptado | D-718 | pela reabertura de verdade |
| test_d718_versao_nova_que_passa_no_teste_fica | adaptado | D-718 | idem |
| test_d718_troca_desfeita_pelo_velopack_conta_como_falha | adaptado | D-718 | a reabertura na versão de antes |
| test_d718_a_volta_so_aceita_o_pacote_assinado | adaptado | D-718, D-724 | a volta pela biblioteca |
| test_d719_nenhum_token_dentro_do_programa | adaptado | D-719 | deixou de procurar uma palavra no texto do código: confere o que a peça do Velopack faz (a fonte do GitHub só com o endereço) |
| test_d723_o_pacote_portatil_do_ensaio_nunca_mexe_no_windows | adaptado | D-723 | o `.portable` na raiz |
| test_d714_a_instalacao_de_verdade_nao_cria_a_tarefa | adaptado | B1, D-733 | os ganchos não falam com o Windows |
| test_d723_instalacao_de_verdade_prepara_o_computador | adaptado | D-723, D-727 | o Visual C++ e o Inno são passos da pergunta, antes da licença |
| os outros 14 (d714_a_versao_vem_de_um_lugar_so, os_textos_do_aviso_sem_emoji_e_com_acento, d719_a_frase_da_falha_e_a_combinada, os 4 d724 do publicar e da chave, d723_o_comando_que_tira_o_inno, d723_o_desinstalador_do_inno_nao_apaga_os_projetos, os 3 d727, pelo_codigo_a_linha_de_comando..., o_main_chama_a_atualizacao_por_um_ponto_so) | igual | — | — |

## tests/test_decisoes_ajudante_da_atualizacao.py (37 antes, 22 agora)

| Teste | O que aconteceu | Decisão | O que cobra agora / quem substitui |
|---|---|---|---|
| test_d732_o_ajudante_nao_roda_mais_ao_ligar_o_computador | saiu | D-732 | `test_atualizador_novo::test_d732_a_procura_e_so_ao_abrir...` |
| test_d733_a_conta_comum_pode_mandar_rodar_mas_nao_mudar_o_ajudante | saiu | D-733 | não há ajudante; o antigo é apagado antes da licença: `test_atualizador_novo::test_protecoes_5_e_6...` |
| test_d733_depois_de_trocar_o_ajudante_e_refeito_como_o_sistema | saiu | D-733 | idem |
| test_d733_o_passo_de_preparar_roda_este_exe_escondido_e_nao_para_a_pergunta | saiu | D-733, D-825 | os passos rodam direto no trabalho com licença: `test_windows_preparo_do_computador::test_os_passos_do_preparo_nao_aceitam_dados_no_pedido` |
| test_d733_o_modo_preparar_cria_o_ajudante_e_prepara_o_computador | saiu | D-733 | `test_decisoes_atualizacao::test_d723_instalacao_de_verdade_prepara_o_computador` |
| test_d733_a_linha_de_comando_atende_o_preparar | saiu | D-733 | o `--preparar-o-computador` saiu (D-825) |
| test_d733_o_script_escondido_vai_codificado_e_solto | saiu | — | não há PowerShell no atualizador |
| test_d736_o_samuel_manda_atualizar_de_longe_pelo_mesmo_ajudante | saiu | D-736 | não construída nesta entrega (vem com os testes à distância, D-824); o lugar está pronto (o mesmo "procurar, conferir, baixar") |
| test_regra_num_lugar_so_todos_os_caminhos_chamam_o_ajudante_pelo_mesmo_comando | saiu | §11.12 | `test_atualizador_novo::test_protecao_13_so_um_lugar_chama_a_troca_do_velopack`, `::test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia` |
| test_d741_a_marca_e_de_fabrica_falsa_e_gravada_so_pelo_sim | saiu | D-741, D-825 | a marca saiu; o "preparado?" é o teste de gravar: `test_atualizador_novo::test_o_teste_de_gravar_cria_e_apaga` |
| test_d742_a_janelinha_aparece_durante_a_espera_e_some_quando_o_programa_abre | vale hoje (nome novo: test_d742_a_janelinha_da_troca_e_a_do_velopack) | D-742 → D-832 | a janelinha nossa não existe mais |
| test_d742_o_texto_e_o_combinado_e_a_janelinha_nao_tem_botao, test_d742_a_janelinha_so_na_abertura_depois_do_depois_e_a_troca_fica_igual, test_d742_quem_pede_a_janelinha, test_d742_o_script_com_a_janelinha_e_powershell_sem_erro_de_escrita, test_d742_se_o_programa_ja_abriu_a_janelinha_nem_aparece | vale hoje / saíram | D-742 → D-832 | `test_d742_a_janelinha_da_troca_e_a_do_velopack` (o texto antigo sumiu do programa) e `test_atualizador_novo::test_d832_a_troca_usa_a_janelinha_do_velopack` (a troca pede a janelinha do Velopack, sem o modo silencioso) |
| test_d734_depois_a_versao_entra_na_proxima_abertura_antes_da_janela | vale hoje (nome novo: test_d734_depois_a_versao_entra_ao_fechar) | D-734 → D-769, D-794, D-831 | ao fechar |
| test_d734_a_linha_de_comando_sai_sem_janela_quando_a_troca_comecou | vale hoje (nome novo: test_d734_a_abertura_nunca_troca_antes_da_janela) | D-734 → D-769 | a abertura não troca |
| test_d734_o_aviso_diz_que_entra_na_proxima_abertura_e_fechar_nao_troca | vale hoje (nome novo: test_d734_o_aviso_diz_que_atualiza_ao_fechar) | D-734 → D-835 | a frase de hoje |
| test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so | vale hoje (nome novo: test_d733_com_a_senha_nada_dos_testes_vai_na_pergunta) | D-733 → D-825, D-834 | a senha não liga; a pergunta só com os 4 passos |
| test_d732_ao_abrir_o_programa_manda_o_ajudante_procurar | adaptado (nome novo: test_d732_ao_abrir_o_programa_procura_a_versao_nova) | D-732 | o nome dizia "ajudante" |
| test_d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso | adaptado (nome novo: test_d732_a_janela_aberta_liga_o_aviso) | D-732 | idem |
| test_d733_reiniciar_agora_chama_o_ajudante_e_nao_pede_licenca | adaptado (nome novo: test_d733_reiniciar_agora_nao_pede_licenca) | D-733 | nenhuma pergunta do Windows no "Reiniciar agora" |
| test_b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa | adaptado | B1 | os ganchos não falam com o Windows |
| test_d735_sem_a_senha..., test_d735_agora_nao_na_senha..., test_d735_com_a_opcao_desligada... | adaptados | D-735, D-834 | a pergunta é a da abertura, com ou sem a senha; a janela da senha não toca o Windows |
| test_d733_disse_nao_fica_anotado_e_nada_quebra | adaptado | D-733 | idem pelo executor |
| test_d736_aberto_por_teste_a_distancia_nao_procura_nem_troca | adaptado | D-736 | idem |
| test_d741_nao_a_pergunta_volta..., test_d741_sim_na_primeira_abertura..., test_d741_na_conta_de_testes... | adaptados | D-741, D-825 | o "preparado?" é o teste de gravar na pasta |
| test_etapa5_pela_fonte_de_teste_a_assinatura_e_conferida_igual | adaptado | D-724 | idem pelo executor |
| test_d736_a_conta_de_testes_e_reconhecida_pelo_nome_fixo e os 3 test_etapa5_ restantes | igual | — | — |

## tests/test_decisoes_preparo_d749.py (5 antes, 2 agora)

| Teste | O que aconteceu | Decisão | O que cobra agora / quem substitui |
|---|---|---|---|
| test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta | adaptado | D-749 | "Sim" com a pasta ainda sem gravar → não procura; pergunta de novo |
| test_d749_visual_c_ou_inno_que_falham_contam_como_erro | adaptado | D-749 | as regras do Visual C++ e do Inno dão falha; a licença é o último passo |
| test_d749_uma_anotacao_velha_nao_conta | saiu | D-749 | não há anotação (o `preparo.txt` saiu): o que vale é o teste de gravar de cada abertura (`test_atualizador_novo::test_d749_sim_com_a_pasta_ainda_sem_gravar_conta_como_nao_feito`) |
| test_d749_o_modo_preparar_devolve_erro_quando_algo_falha_no_meio | saiu | D-749 | o modo saiu; a peça para no primeiro passo que falha (regra existente da peça) |
| test_d749_o_passo_anota_como_o_preparo_terminou | saiu | D-749 | idem |

## tests/test_decisoes_desinstalar.py (37 antes, 36 agora)

| Teste | O que aconteceu | Decisão | O que cobra agora / quem substitui |
|---|---|---|---|
| test_d731_desinstalar_manda_rodar_a_tarefa_desfazer | adaptado | D-731 | sem a "tarefa da atualização" (o ajudante saiu); confere que ela não existe mais |
| test_d731_desinstalar_o_portatil_nao_manda_nada | adaptado | D-723, D-731 | idem |
| test_d731_desinstalar_sem_a_tarefa_nao_quebra | adaptado | D-731 | idem |
| test_d731a_sem_os_testes_ligados_desinstalar_apaga_a_tarefa_da_atualizacao | saiu | D-731 | a primeira abertura não cria mais o ajudante nem o "desfazer": `test_atualizador_novo::test_d731_o_atualizador_novo_nao_poe_tarefa_no_windows` |
| os outros 33 | igual | — | — |

## tests/test_decisoes_testes_a_distancia.py (13)

| Teste | O que aconteceu | Decisão | O que cobra agora |
|---|---|---|---|
| test_d721_primeira_vez_pede_a_senha_e_liga | vale hoje (o nome ficou) | D-721 → D-825, D-834 | a janela da senha aparece uma vez; a senha não liga; nenhuma pergunta do Windows daqui |
| test_d728_instalado_primeira_vez_pede_a_senha | vale hoje | D-728, D-825 | idem |
| os outros 11 | igual | — | — |

## tests/test_decisoes_brasao.py (22 antes, 20 agora)

| Teste | O que aconteceu | Decisão | O que cobra agora |
|---|---|---|---|
| test_d748_a_janelinha_some_quando_o_brasao_aparece_e_nunca_ficam_juntos, test_d748_o_brasao_poe_a_marca_antes_de_olhar_a_janelinha_e_espera_ela_sumir, test_d748_a_janelinha_pega_a_marca_dela_antes_de_olhar_o_programa_e_solta_depois_de_fechar | vale hoje (um só, nome novo: test_d748_o_brasao_nao_espera_janelinha_nenhuma) | D-748 → D-832 | o brasão aparece na hora, sem marca nem espera; "nunca juntos" vem do Velopack (fecha a janelinha antes de reabrir) e da conferência antes do brasão |
| os outros 19 | igual | — | — |

## tests/test_windows_peca.py (71)

| Teste | O que aconteceu | Decisão | O que cobra agora |
|---|---|---|---|
| test_a_licenca_da_tarefa_e_comparada_pelo_sentido_com_o_que_o_windows_devolve | adaptado | (peça) | a mesma conferência; a licença do ajudante (`atualizacao.QUEM_PODE_MANDAR_RODAR`, que saiu) escrita no teste |
| test_a_tarefa_numa_pasta_do_agendador_que_mudou_no_meio_e_apagada | adaptado | (peça) | idem |
| os outros 69 | igual | — | — |

## tests/test_trava_windows.py (deste ramo; a gerente liberou)

| Teste | O que aconteceu | O que cobra agora |
|---|---|---|
| test_o_mapa_dos_donos_so_usa_capacidades_que_existem | o mapa ganhou a capacidade "Velopack" (dono `core/conversa_com_o_velopack.py`) | o mapa de hoje |
| test_velopack_so_no_dono | novo | `import velopack` fora do dono é acusado |
| test_cada_capacidade_so_no_seu_dono | igual (a catraca desceu: 12 lugares do `atualizacao.py` saíram, TETO 46 → 34) | — |

## Fora do atualizador, adaptados com o "sim" do Samuel (24/11/2026)

| Teste | O que aconteceu | O que cobra agora |
|---|---|---|
| tests/test_conferencias_pacote.py::test_o_pacote_mostra_os_lugares_da_lista_nos_arquivos_do_pedido | adaptado: só o arquivo de exemplo (`atualizacao.py` → `core/testes_a_distancia.py`), porque o `atualizacao.py` ficou sem lugares na lista | o mesmo: o pacote mostra a seção "Lugares da lista de exceções nos seus arquivos" e o aviso |
| tests/test_conferencias_pacote.py::test_q3_o_pacote_do_passo_diz_as_funcoes_de_outros_passos_que_nao_se_mexem | adaptado: só o arquivo de exemplo (`atualizacao.py`, passo 3, com `criar_as_tarefas` do passo 5 → `core/testes_a_distancia.py`, passo 4, com `_passos_das_nossas_tarefas` do passo 5), pelo mesmo motivo | o mesmo: o pacote do passo lista as funções de outros passos e não as do próprio |

Os dois continuam cobrando o que cobravam: com o pacote sem a seção dos lugares, o primeiro falha; com o pacote sem a
lista das funções de outros passos, o segundo falha (conferido trocando o `regras_dos_agentes/montar_pacote.py` numa
cópia de trabalho e devolvendo o arquivo depois). Os 26 do arquivo passam.


## Volta 2 (24/11/2026): os achados de quem tentou quebrar

| Arquivo :: teste | O que aconteceu | Por quê |
|---|---|---|
| `tests/test_atualizador_volta2.py` (32) | novos | um por achado (G1, M1, M2, M4, leves 2, 3, 7) e um por mutação que sobrevivia (Q1-Q5, Q7, Q8, Q14, Q15); 20 falham no código de `cd4b8414` |
| `tests/test_atualizador_volta2.py::test_q1..q4`, `motor_estragado_no_lugar...`, `sem_o_arquivo...`, `volta2_medio1...` | vindos do conserto 4 do `atualizador-4` (`tests/test_atualizador_4.py`), pelo caminho novo | D-833 ("o que foi feito no conserto 4 passa para o desenho novo"); os que cobravam o ajudante (`rodar_ao_ligar`, `procurar_e_preparar`) não vieram: o "sem motor nada anunciado nem trocado" está no M2 e na 4a/4b |
| `tests/test_fases_da_atualizacao.py` (a tabela) | mudado pelo conserto | a regra mudou: o "Reiniciar agora" passa pela fase nova (conferir antes de fechar, M1) e guarda `trocando_com_janela`; linhas novas para a troca em curso (G1), o estado que não grava (M4), o motor da versão nova (M2) e a conferência; mais 2 testes (M1, M4) |
| `tests/test_porteiro_licenca_que_acrescenta.py` (a amostra `CERTO` e duas linhas dela) | mudado pelo conserto | a K03 passou a aceitar só a linha do experimento escrita igual (leve 2); a amostra passou a ser essa linha; o que os testes cobram não mudou |
| `tests/ajudante_do_atualizador.py` | mudado | os pacotes de prova passaram a ter o `motor-exigido.json` (M2); a peça do Windows de mentira ganhou o que a de verdade ganhou (a troca em curso, abrir de novo) |

## Volta 2b (24/11/2026): as frases D-839 e D-840

| Arquivo :: teste | O que aconteceu | Por quê |
|---|---|---|
| `tests/test_atualizador_volta2.py::test_leve1_a_frase_da_troca_espera_a_resposta_do_samuel` | vale hoje (cobra a frase nova) | existia para a frase da falha "troca" não mudar calada até a resposta do Samuel; ele respondeu (D-839, chat 24/11: "sim"); a gerente liberou a troca deste teste |
| `tests/test_atualizador_novo.py::test_d835_e_d778_os_textos_da_tela_palavra_por_palavra` (só a linha "troca" do dicionário) | vale hoje (cobra a frase nova) | a mesma decisão: a D-839 deu frase própria à falha "troca"; as outras três linhas (as da D-778) e os textos da D-835 não mudaram |
| `tests/test_fases_da_atualizacao.py` (a tabela) | uma linha nova, nenhuma mudada | o evento novo "conferida_outra_janela" (D-840): DEPOIS, com o registro e a frase; o "conferida_nao" continua igual (nada na tela) |
| `tests/test_decisoes_atualizacao.py::test_d839_*` (3), `::test_d840_*` (3) | novos | as provas das duas decisões pelo caminho inteiro (a regra, o executor e a ponte da tela); 4 falham no código de `63bd8546` (`volta2b-testes-no-codigo-antigo.txt`); os 2 de "só com outra janela" passam lá e aqui (nada mudou nos outros casos) |
| `tests/test_atualizador_volta2.py::test_m1_reiniciar_agora_que_nao_pode_trocar_nao_fecha_a_janela` (uma linha) | vale hoje | D-841 (chat 24/11: "1, desde que seja a volta à fase 'pronta'"): com outra janela aberta a fase depois do "Reiniciar agora" é PRONTA (o aviso volta), não DEPOIS; o resto do teste não mudou |
| `tests/test_fases_da_atualizacao.py` (a linha `conferida_outra_janela`) e `tests/test_decisoes_atualizacao.py::test_d840_reiniciar_agora_com_outra_janela_...` | vale hoje | D-841: depois da frase, o aviso aparece de novo |
| `tests/test_decisoes_atualizacao.py::test_d841_depois_da_frase_o_aviso_volta_e_com_a_outra_fechada_troca` | novo | a prova da D-841; falha em `4f542399` |

## Volta 3 (24/11/2026): a emenda do Fable e os achados do segundo "quem tenta quebrar"

O que mudou e por quê, em uma frase: a abertura passou a olhar o que existe (a versão que roda, a última boa guardada,
o pacote esperando) em vez da anotação da troca; só o teste rápido reprovado põe a versão em "não tentar"; a volta usa o
pacote guardado; o "Reiniciar agora" que não pode responde com a frase (D-845, título D-846); a licença da pergunta
única vale também para a pasta do registro. Todo teste abaixo é do atualizador. Fora do atualizador, só a
configuração comum dos testes (`tests/conftest.py`) mudou: ela passou a trocar também o PROGRAMDATA, como já trocava o
LOCALAPPDATA (leve 1: dois testes escreviam no registro de verdade do PC); nenhum teste de fora do atualizador mudou.

| Arquivo :: teste | O que aconteceu | Por quê (a decisão ou o achado) |
|---|---|---|
| `tests/test_fases_da_atualizacao.py` (a tabela inteira) | vale hoje (reescrita) | a regra recebe o que existe (`ultima_boa`, `pendente`, `reaberto_de/para`, `frase_guardada`) no lugar da anotação (`troca_de/para`, `falha_anotada`, `estado_grava`); fases novas GUARDANDO; efeitos novos `Reprovar`, `GuardarUltimaBoa`, `GuardarFrase`; saem `AnotarFalha`, `AnotarOk`, `PedirParaFecharAOutraJanela` (que virou `MostrarFalha(nao_deu_agora)`). Teste novo: `test_m1_so_o_teste_reprovado_poe_a_versao_em_nao_tentar` (em TODOS os pares, o "não tentar" só cresce pelo `Reprovar`, e só no teste que falhou) |
| `tests/test_atualizador_novo.py::test_protecao_2_...` | vale hoje | a assinatura recusada não vai mais para "não tentar" (emenda: "Só o teste rápido reprovado põe versão em 'não tentar'"); continua não baixando e mostrando a frase 2 |
| `::test_protecao_8_...` | adaptado | a chave do bilhete é `reprovadas` |
| `::test_d720_reiniciar_agora_fecha_a_janela_e_so_depois_troca` | vale hoje (uma linha) | nada é anotado antes de trocar (o bilhete fica vazio) |
| `::test_protecao_10_a_janela_que_nao_fecha_nao_troca` | vale hoje (uma linha) | D-845: o clique tem resposta (a frase "o programa não conseguiu fechar") antes da pergunta ao fechar |
| `::test_protecao_3_pacote_trocado_depois_de_baixar_nao_troca` | vale hoje (uma linha) | não troca e fica no registro; não vai para "não tentar" |
| `::test_d718_reaberto_na_versao_nova_que_passa_no_teste` | vale hoje | o teste roda porque a versão não é a última boa; passou, vira a última boa (D-844) |
| `::test_d718_teste_que_falha_volta_para_a_anterior_assinada` | vale hoje | a volta pelo pacote guardado (o `baixar` com a pasta da última boa); o bilhete só com `reprovadas` |
| `::test_protecao_11_a_volta_sem_a_assinatura_...` | vale hoje | a assinatura que vale é a guardada com o pacote da última boa |
| `::test_a_troca_que_nao_aconteceu_avisa_uma_vez` | vale hoje | M1: a frase da D-839 continua, a versão NÃO vai para "não tentar" |
| `::test_d769_reabertura_sem_janela_que_passa_sai_sem_janela` | vale hoje | sai sem janela e a última boa fica guardada antes de sair |
| `::test_d719_a_falha_vai_para_a_janela_uma_vez_so_nesta_conta` | vale hoje | a frase (1) é derivada (rodando a última boa com a mais nova reprovada), não anotada |
| `::test_d835_e_d778_os_textos_da_tela_palavra_por_palavra` | vale hoje (uma linha a mais) | D-843: a frase do motor novo no dicionário das frases |
| `::test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia` | adaptado | a volta precisa da última boa guardada |
| `tests/test_atualizador_volta2.py::test_g1_abrir_pelo_atalho_no_meio_da_troca_...`, `::test_g1_sem_saber_...` | adaptado | a mesma proteção (sai sem janela; sem saber, segue e nada é anotado), agora disparada pelo pacote esperando, sem a anotação |
| `::test_g1_a_troca_que_acabou_sem_trocar_continua_sendo_falha` | vale hoje (nome novo: `test_g1_a_troca_que_acabou_sem_trocar_nao_e_falha_e_a_reabertura_nao_pergunta`) | M1 da emenda: "Troca que não aconteceu não é falha de versão" |
| `::test_m2_a_volta_confere_o_motor_da_anterior_e_volta` | adaptado | a volta precisa da última boa guardada; o bilhete diz `reprovadas` |
| `::test_m2_a_versao_nova_sem_o_motor_dela_nao_e_anunciada` | vale hoje | D-843: no lugar de nada na tela, a frase do motor novo |
| `::test_m4_com_o_estado_que_nao_grava_nada_e_procurado_nem_trocado` | vale hoje (nome novo: `test_m4_com_o_estado_que_nao_grava_a_atualizacao_continua_e_o_registro_diz`) | M4 da emenda: "Se não puder ser gravado, o programa continua atualizando e registra o motivo" |
| `::test_q7_a_licenca_tem_de_chegar_ao_arquivo_de_dentro` | adaptado | quem pede diz o arquivo de dentro a conferir (a mesma função serve às duas pastas) |
| `::test_q14_sem_a_lista_de_processos_nao_troca` | adaptado | a conferência única direto (saiu o embrulho `conferir_troca`) |
| `tests/test_decisoes_atualizacao.py::test_d724_versao_com_assinatura_errada_...`, `::test_d724_versao_sem_arquivo_...`, `::test_d724_pacote_trocado_...` | vale hoje | D-724 igual (não baixa); a versão não vai para "não tentar"; a frase 2 na tela (ou, já vista, o registro) |
| `::test_d724_versao_que_ja_falhou_nao_e_tentada_de_novo` | adaptado | a chave `reprovadas` |
| `::test_d719_a_falha_aparece_na_tela_uma_vez_so` | vale hoje | a frase (1) derivada |
| `::test_d719_o_erro_vai_para_o_registro_no_programdata` | adaptado | a função única que reprova é `reprovar` |
| `::test_d718_versao_nova_que_nao_passa_no_teste_volta_para_a_anterior`, `::test_d718_versao_nova_que_passa_no_teste_fica`, `::test_d718_a_volta_so_aceita_o_pacote_assinado` | vale hoje | a volta e a guarda pela última boa (D-844) |
| `::test_d718_troca_desfeita_pelo_velopack_conta_como_falha` | vale hoje (nome novo: `test_d718_troca_desfeita_pelo_velopack_mostra_a_frase_e_nao_proibe_a_versao`) | D-839 (a frase) continua; M1: não proíbe a versão |
| `::test_d839_a_troca_que_nao_aconteceu_...` (2) | adaptado | sem janela, a frase vai pelo bilhete (`frase`) para a próxima abertura |
| `::test_d840_reiniciar_agora_com_outra_janela_...`, `::test_d841_...` | vale hoje (o título) | D-846: o título da caixa é "Atualização" |
| `::test_d840_a_frase_so_aparece_com_outra_janela_aberta` (2) | vale hoje | D-845: nos outros casos aparece "Não deu para atualizar agora: [motivo]..." (antes, nada) |
| `tests/test_porteiro_licenca_que_acrescenta.py` (a amostra `CERTO`) | adaptado | a K03 aceita a linha do experimento com `pasta` (a mesma função para as duas pastas); nada mais mudou na K03 |
| `tests/ajudante_do_atualizador.py` | mudado | a `Prova` ganhou `ultima_boa` e `pendente`; o Velopack de mentira copia da pasta (como a fonte de pasta do Velopack, conferindo a soma) e falha sem a fonte (como sem internet); a peça do Windows de mentira usa a leitura de verdade `caminho_conferido` |
| `tests/test_atualizador_volta3.py` (33) | novos | um por achado do segundo "quem tenta quebrar" (G1, M1 a M9, L1 a L4) e pela D-844; 23 falham no código de `012c849c` pelo comportamento (`volta3-testes-no-codigo-antigo.txt`); os 8 do M9 passam lá (as proteções existiam; faltava o teste: a prova é a rodada de mutações) |
| `tests/test_atualizador_volta3_de_verdade.py` (5) | novos | o Velopack de verdade (a volta pela pasta da última boa sem índice e sem SHA1; o pendente), o `icacls` de verdade numa pasta de prova com o bilhete e o registro dentro, a recusa do arquivo ligado e do atalho |
