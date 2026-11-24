# Atualizador novo: o plano (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`, ponta `732a143e`.
Pedido da gerente de 23/11/2026: **só o plano, nenhuma linha de código nem de teste.** O código só começa com o "pode"
da gerente. As voltas da trava (abaixo deste plano) ficam como estavam.

**Situação: plano escrito, esperando a gerente.** Nada do programa mudou. Li: `resposta-do-fable.md` (inteiro, com a
correção das 20:42 e a revisão das 20:50), `experimento-passo-1.md`, a Parte 2 do `relatorio-para-o-fable.md`, as
decisões D-705 a D-833 do Livro mais novo (`obra-juncao`), `atualizacao.py` e `core/windows.py` deste ramo, o
`atualizacao.py` do ramo `atualizador-4-consertos-2026-11-21`, `ui/aviso_de_atualizacao.py`, `ui/testes_a_distancia_ui.py`,
`main.py`, a trava (`tests/test_trava_windows.py`), o porteiro (`regras_dos_agentes/porteiro.py`, `excecoes.py`,
`tests/conferencias_excecoes.json`) e o código do Velopack 1.2.161 (clone na etiqueta `1.2.161`, no rascunho).

Em resumo, o desenho: **o único ato com licença é dar à pasta do programa a licença de Modificar para Usuários, uma vez,
na primeira abertura, antes da janela. Depois disso o próprio programa, na conta do Kaique, procura, confere a
assinatura, confere o motor, baixa e pede ao Velopack para trocar; o Velopack espera o programa sair, troca, mostra a
janelinha dele e reabre na conta do Kaique.** Nenhum processo nosso roda como o sistema, nenhum PowerShell, nenhuma
marca, nenhum canal entre contas.

---

## 1. Decisões que esta tarefa precisa cumprir (§11.3)

Palavras dele copiadas do Livro (`obra-juncao/docs/plano/DECISOES.md`). Quando duas se contradizem, vale a mais nova
(anotado em cada linha).

### O que o atualizador faz

| Decisão | Palavras dele | Como o desenho novo cumpre |
|---|---|---|
| D-706 | "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um instalador fazer tudo de novo" | O Velopack troca a pasta `current`; o instalador só na primeira vez. |
| D-713 | "não precisa ser privado" | As versões vêm dos "Releases" do projeto público (`Fonte.padrao()`, fica). |
| D-714 | "1 - vamos seguir sua sugestão" (publicada de propósito) | Nada muda no publicar. A parte "toda vez que o pc inicializar" foi trocada pela D-732. |
| D-715 | "ele dá um aviso se o programa estiver aberto, um aviso para salvar o trabalho atual e reinicializar o programa" | Baixou com o programa aberto → aviso. "Reiniciar agora" fecha pela janela (o fechar grava) e só depois pede a troca. |
| D-718 | "Sim, e tem que avisar a gente de alguma maneira" | A versão nova reaberta roda o teste rápido antes da janela; falhou → volta para a anterior (pacote assinado) e anota. |
| D-719 | "1" (aviso na tela e registro lido de longe) | O aviso uma vez por falha; o registro fica em `%ProgramData%\EditorImpressao\atualizacao\atualizacao.log`, que outra conta do PC lê. A leitura "de longe" depende dos testes à distância (ficam para depois). |
| D-720 | "Sim" (Reiniciar agora / Depois) | Os dois botões ficam. O "Depois" muda de efeito pela D-769/D-794/D-831 (abaixo). |
| D-723 | "velopack" | Velopack 1.2.161, sem trocar (D-779). |
| D-724 | "gratis, mas o que é essa assinatura e é segura?" | A assinatura é conferida **antes de baixar** (fica) e, novo, **de novo no arquivo baixado, logo antes de trocar** (com Modificar para Usuários, outra conta poderia trocar o arquivo em `packages\`). |
| D-727 | "se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" | O Visual C++ e o motor do Kraken continuam dentro do instalador; nada baixado na instalação. |
| D-732 | "não, faz quando o programa é aberto" | A procura roda **só ao abrir** (correção das 20:42: o "de 5 em 5 minutos" era do código antigo e sai). Nada roda por trás depois. |
| D-733 | "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?" | Uma pergunta do Windows só, na primeira abertura; depois nenhuma, nem na volta. O programa continua em Arquivos de Programas, fora da conta do Kaique, então os testes à distância continuam possíveis depois. O "ajudante" que a D-733 descrevia era o jeito; a D-830 ("refazer") troca o jeito e mantém a escolha "1". |
| D-735 | "Sim" (a pergunta aparece sempre, com ou sem a senha) | A pergunta não depende da senha: vem antes da janela, em toda abertura em que a pasta ainda não tem a licença. |
| D-741 | "Sim" (depois do "Não", volta a cada abertura até o "Sim") | "Preparado?" = a pasta do programa aceita gravação pela conta que abriu (o mesmo teste que o Velopack faz). Sem isso, pergunta de novo. Na conta de testes, nada pergunta. |
| D-749 | "Sim" (preparação pela metade conta como não feita) | A licença da pasta é o **último** passo do pedido, e a peça para no primeiro passo que falha. Então "a pasta aceita gravação" só acontece se o Visual C++ e a retirada do Inno deram certo antes. |
| D-763/D-764 | "ok, pode fazer" · "ok" | O nome do pacote continua `versao.ID_DO_PACOTE`. Bônus: com a pasta gravável, o Velopack deixa de usar a pasta de reserva no `%LOCALAPPDATA%` (fato, `locator.rs` L152-176). |
| D-765 | "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique [...]" | Só o atualizador muda. Nada de ferramenta, filtro ou tela de trabalho. |
| D-767 | "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" | O que mexe no Windows só conta como pronto depois da prova à vista (seção 11). |
| D-768/D-788/D-789 | "vou escolher a 16" · "1" · "A" | O motor mora em `<raiz>\motor-kraken\<versão>`, fora de `current`; a atualização vai inteira e sem o motor. |
| D-769 | "b" (com "Depois", entra ao fechar) | Mudada pela D-794 e confirmada pela D-831. |
| D-778 | "A" (três frases para as três falhas) | **Adiada pela D-824** ("os três avisos" ficam para depois). Ver pergunta 4: o desenho novo mostraria a frase errada em dois casos se continuar adiada. |
| D-779 | "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito [...]" | Fica a 1.2.161. A "proteção em volta" (guardar a versão que funciona fora da pasta trocada) **fica de fora nesta entrega**: é parte do "resto do plano da parte do Windows" que a D-824 deixou para depois. Ver ressalva 6. |
| D-790 | "A" (tudo ou nada do motor) | Pela D-833, o que vem é o conserto 4 da volta 1: sem o motor no lugar, nada é anunciado nem trocado. **Baixar só o motor pela internet fica de fora**, como já estava no ramo `atualizador-4` ("Nesta entrega nao baixa motor da internet"). |
| D-794 | "eu acho que deveria aparecer o aviso para atualizar ou não na hora de fechar e se ele disser sim, o programa fecha e fica uma janelinha em segundo plano tipo esses iconizinhos, mostrando porcentagem atualizando" · "da proxima vez que ele abrir o programa" | Com versão pronta e "Depois", fechar pergunta "Atualizar agora?". Sim → o programa grava, fecha, e o Velopack troca. Não → fecha sem trocar; o aviso volta na próxima abertura. **O ícone perto do relógio: ver pergunta 3** (a D-832 diz "janelinha do Velopack"). |
| D-805 | "a" (na pergunta fica "EditorImpressao.exe") | A pergunta abre o próprio `EditorImpressao.exe` pela peça (como hoje). |
| D-806 | "então pode ser opção A" (a licença pedida no instante do clique, com o programa na frente) | A pergunta é feita **antes do brasão e da janela**, cerca de um segundo depois do clique no atalho, quando o programa ainda tem o direito de vir para a frente que o Velopack lhe passa (fato: `stub.rs` L41 e `start_windows_impl.rs` L132 chamam `AllowSetForegroundWindow` para o programa aberto). Sai a espera pela janela na frente. |
| D-824 | "vamos fazer com um só, uma coisa de cade vez." (entrega em duas vezes) | Esta entrega: o programa que se atualiza. Ficam para depois: testes à distância, os três avisos, a janelinha nossa, o desinstalar limpo dos testes. |
| D-825 | "ok" (B: a senha não liga os testes nesta entrega) | A janela da senha continua na primeira abertura; o que se digita não liga nada (como no `atualizador-4`). |
| D-826 | (a parte do "erro pequeno" **não tem resposta dele**) | No desenho novo ela some: qualquer passo que falha deixa a pasta sem a licença, e a pergunta volta (vale a D-749, que é dele). |
| D-828 | "foi eu, pode consertar essas coisas" | (1) Quem espera o programa fechar é o Velopack, pelo número do **nosso** processo (`--waitPid`), e o programa só sai depois de gravar. Um clique no atalho no meio da troca não estraga a troca: o Velopack fecha à força o que roda da pasta antes de trocar (fato, `apply_windows_impl.rs` L159). (2) A pergunta no clique (D-806). (3) Não há pasta trancada: nenhuma tranca à mão. |
| D-830 | "refazer" | Este plano. |
| D-831 | "a" (o "Depois" ao fechar, com "Atualizar agora?", já nesta entrega) | `wait_exit_then_apply_updates` ao fechar, provado no experimento de 23/11. |
| D-832 | "pode ser velopack, deixamos para mudar isso mais para frente" | A troca é chamada com a janelinha do Velopack ligada (sem `--silent`). Em português no Windows em português: "Atualização do Editor de Impressão / Instalando Atualização / Atualizando para a versão X, aguarde..." (fato, `locales/pt-BR.ftl` L2, L64-65). Nenhuma janelinha nossa. |
| D-833 | "motor do Kraken tudo ou nada continua" | `garantir_o_motor` e `motor_esta_no_lugar` vêm do `atualizador-4`, agora rodando na conta do Kaique (a pasta tem a licença). |

### Testes à distância (deixados de fora nesta entrega, D-824/D-825)

D-705, D-711, D-712, D-717, D-721, D-728, D-731, D-736, D-739, D-743, D-771, D-772, D-780, D-781:
- **Continuam como estão:** a janela da senha na primeira abertura (D-721) e o botão nas Configurações (D-712); pelo
  código nada aparece (D-728); na conta de testes nada procura nem pergunta (D-736, D-741).
- **D-736 ("Se tiver nova versão eu quero poder mandar atualizar aqui pelo meu pc, mas o programa não precisa procurar
  versão nova")** depende do comando de longe (SSH), que vem com os testes à distância. **Não é construída agora.** O
  desenho deixa o lugar: o mesmo "procurar, conferir e baixar" que a abertura usa serviria a um `--baixar-atualizacao`
  rodado de longe; a troca entraria na próxima abertura ou no "Reiniciar agora" (como o Fable descreveu).
- **D-731 ("ok": desinstalar tira junto o que os testes puseram):** nesta entrega os testes não põem nada (D-825), e o
  desenho novo não põe tarefa nenhuma no Windows. O desinstalar do `.msi` apaga a pasta inteira do programa, com o motor
  dentro. O gancho de desinstalar continua mandando rodar o "desfazer" dos testes **se** ele existir (como hoje).

### Regras de trabalho

D-605 / §11.8 (nada de mudar o que está testado sem o "sim"), D-637 / §11.9, §11.12 (uma peça só; nada dado como feito
sem conferir; a lista das falhas; ler a peça de fora), §11.13, D-775 (quem tenta quebrar antes da prova), D-785 (à
vista), D-793 / §11.11 (não abrir agente), D-809 (nada que mude o `.git` inteiro), D-811 a D-813 e D-827 (cada
proteção com o teste que a acusa), D-815, D-819 (comparar o jeito mais simples e dizer por quê).

---

## 2. O que já está escolhido e testado aqui (§11.8)

Legenda: **F** = continua igual, sem mudar uma linha. **C** = cobra a mesma decisão, mas chama o caminho novo (muda a
chamada, não a conferência). **S** = testa uma peça que sai. **M** = cobra uma decisão que ele mesmo mudou depois.
**Nenhum teste muda nem sai sem o "sim" dele** (pergunta 5). Os C marcados "D-825" já têm o "sim" de 21/11 para passar
ao "caminho novo [...], o 'preparado' lido do Windows" — a gerente confere se esse "sim" cobre a leitura da pasta (no
lugar da leitura das tarefas).

**`tests/test_decisoes_atualizacao.py` (38):**
- F: `d714_a_versao_vem_de_um_lugar_so`, `os_textos_do_aviso_sem_emoji_e_com_acento`, `pelo_codigo_o_aviso_nao_liga`,
  `d719_a_frase_da_falha_e_a_combinada`, `d719_o_erro_vai_para_o_registro_no_programdata`, `d719_nenhum_token_dentro_do_programa`,
  os 3 `d724_publicar_*`, `d724_a_chave_nunca_dentro_do_repositorio`, `d724_o_que_o_publicar_assina_o_programa_aceita`,
  `d723_o_desinstalador_do_inno_nao_apaga_os_projetos`, `d714_a_instalacao_de_verdade_nao_cria_a_tarefa`, os 2
  `d727_o_vpk_*`/`o_visual_c_vai_dentro`, `pelo_codigo_a_linha_de_comando_nao_faz_nada_nem_importa_o_velopack`,
  `o_main_chama_a_atualizacao_por_um_ponto_so`.
- C: os 4 `d724` de procurar (assinatura errada, sem arquivo, pacote trocado, já falhou: sai só o argumento "programa
  aberto?"), `d715_programa_aberto_fica_pendente_e_a_tela_avisa`, `sem_internet_nao_e_falha_e_nao_avisa`,
  `d720_reiniciar_agora_fecha_gravando_e_so_depois_troca`, `d719_a_falha_aparece_na_tela_uma_vez_so`, os 4 `d718`
  (volta, fica, troca desfeita, só pacote assinado: a versão de antes e a nova passam a vir na linha de comando da
  reabertura), `d723_o_comando_que_tira_o_inno`, `d723_o_pacote_portatil_*`, `d723_instalacao_de_verdade_prepara_o_computador`,
  `d727_o_visual_c_so_roda_se_faltar` (as três últimas: o Visual C++ e o Inno passam a ser passos da peça).
- S: `d714_a_tarefa_roda_ao_ligar_*`, `d714_criar_e_apagar_a_tarefa_pelo_schtasks`,
  `d714_programa_fechado_baixa_e_troca_e_reabre_escondido_*` (quem trocava com o programa fechado era o ajudante),
  `d723_o_portatil_nunca_cria_nem_apaga_a_tarefa`.
- M: `d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga` (já era da D-714 antiga), `d720_o_aviso_tem_reiniciar_agora_e_depois_*`
  (cobra a frase "próxima vez que você abrir o programa"; o "Depois" agora pergunta ao fechar).

**`tests/test_decisoes_ajudante_da_atualizacao.py` (37):**
- F: `b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa`, `d736_a_conta_de_testes_e_reconhecida_pelo_nome_fixo`, os 4
  `etapa5_*` (a fonte de teste do administrador: fica; só a leitura do dono do arquivo passa para a peça).
- C: `d732_ao_abrir_o_programa_manda_o_ajudante_procurar` e `d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso`
  (procura ao abrir, agora no próprio programa), os 3 `d735_*` (D-825), `d733_disse_nao_fica_anotado_e_nada_quebra`
  (D-825), `d733_reiniciar_agora_chama_o_ajudante_e_nao_pede_licenca` (continua sem licença, pelo Velopack),
  `d736_aberto_por_teste_a_distancia_nao_procura_nem_troca`, os 3 `d741_*` de pergunta voltar (D-825).
- S: `d732_o_ajudante_nao_roda_mais_ao_ligar_o_computador`, `d733_a_conta_comum_pode_mandar_rodar_mas_nao_mudar_o_ajudante`,
  `d733_depois_de_trocar_o_ajudante_e_refeito_como_o_sistema`, `d733_o_passo_de_preparar_roda_este_exe_escondido_*` (D-825),
  `d733_o_modo_preparar_cria_o_ajudante_e_prepara_o_computador`, `d733_a_linha_de_comando_atende_o_preparar`,
  `d733_o_script_escondido_vai_codificado_e_solto`, `d736_o_samuel_manda_atualizar_de_longe_pelo_mesmo_ajudante`,
  `regra_num_lugar_so_todos_os_caminhos_chamam_o_ajudante_pelo_mesmo_comando`, `d741_a_marca_e_de_fabrica_falsa_*` (a
  marca nas Configurações já saiu pela D-825).
- M: `d733_com_a_senha_preparo_e_testes_numa_pergunta_so` (D-825: a senha não liga), os 3 `d734_*` (entra na próxima
  abertura → ao fechar), os 6 `d742_*` (a nossa janelinha → a do Velopack, D-832).

**`tests/test_decisoes_preparo_d749.py` (5):** C: `sim_com_a_preparacao_parada_no_meio_a_pergunta_volta`,
`visual_c_ou_inno_que_falham_contam_como_erro` (D-825). S: `uma_anotacao_velha_nao_conta`, `o_modo_preparar_devolve_erro_*`,
`o_passo_anota_como_o_preparo_terminou` (o `preparo.txt` e o `--preparar-o-computador` saem; D-825).

**`tests/test_decisoes_desinstalar.py` (37):** F: os 31 dos testes à distância. C: os 3 `d731_desinstalar_*` (trocam
`atualizacao.apagar_tarefa`, que sai; o "manda rodar o desfazer" fica). S: `d731a_sem_os_testes_ligados_desinstalar_apaga_a_tarefa_da_atualizacao`,
`d731a_com_os_testes_ligados_o_desfazer_inteiro_apaga_tambem_a_tarefa_da_atualizacao`,
`d731a_a_primeira_abertura_nao_troca_o_desfazer_inteiro_pelo_curto` (a primeira abertura deixa de criar o "desfazer" e
o ajudante não existe). **`tests/test_decisoes_desinstalar_pasta.py` (4):** F.

**`tests/test_decisoes_testes_a_distancia.py` (13):** F: 11. C (D-825): `d721_primeira_vez_pede_a_senha_e_liga`,
`d728_instalado_primeira_vez_pede_a_senha`.

**`tests/test_decisoes_brasao.py` (22):** F: 19 (o `d744_o_brasao_some_quando_a_janela_principal_abre` importa
`ui.aviso_de_atualizacao`, que continua existindo). M: os 3 `d748_*` (a janelinha nossa e as duas marcas saem; o
brasão deixa de esperar a janelinha).

**`tests/test_windows_peca.py` (71):** F: 69. C: `a_licenca_da_tarefa_e_comparada_pelo_sentido_*` e
`a_tarefa_numa_pasta_do_agendador_que_mudou_no_meio_e_apagada` usam `atualizacao.QUEM_PODE_MANDAR_RODAR` como dado de
exemplo; a constante sai com o ajudante (pergunta 5: o texto vai escrito no próprio teste).

**`tests/test_nome_do_pacote.py` (5), `tests/test_publicar_*.py`:** F (o publicar não muda).

**`tests/test_trava_windows.py` (deste ramo, ainda não juntado):** a catraca muda pelo jeito previsto nela mesma (seção 10).

**`tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`:** vai falhar até a
gerente gerar a lista de novo (seção 10). Não mexo nele nem na lista.

Os testes do ramo `atualizador-4` (`test_atualizador_4.py`, `test_atualizador_volta4.py`) não existem aqui. Vêm só os
do motor (conserto 4) que cobram o que passa (seção 5).

---

## 3. Como fica para quem usa e no livro (§11.9)

**No livro (PDF): nada muda.** Só o atualizador muda. Pelo atalho "(desenvolvimento)" e pelo código, nada muda (o
programa não está instalado pelo Velopack: nada roda).

**Primeira abertura (programa recém-instalado pelo `.msi`):**
- Antes: clique → brasão → janela → janela da senha → "Agora não" → a pergunta do Windows (às vezes só piscando na
  barra) → nada na tela enquanto prepara.
- Depois: clique → **logo em seguida** a pergunta do Windows ("Deseja permitir que este aplicativo... EditorImpressao.exe",
  faixa amarela) no meio da tela → "Sim" → o brasão e a janela abrem normalmente, enquanto a preparação (Visual C++,
  tirar a instalação antiga, a licença da pasta) termina por trás, num processo separado → a janela da senha aparece
  como hoje (pergunta 1: a ordem muda). Depois da preparação, o programa põe o motor do Kraken no lugar e procura versão
  nova, por trás, sem nada na tela.

**Pergunta recusada com "Não":** a janela abre normalmente; nada é feito; na próxima abertura a pergunta aparece de
novo, logo no clique, até o "Sim". Sem o "Sim", nada se procura (se procurasse, o Velopack pediria licença a cada versão,
o jeito 2 que ele recusou).

**Abertura comum com versão nova publicada:** clique → brasão → janela (nada atrasa: a procura e o download rodam por
trás). Quando o download termina (uns 460 MB), aparece o aviso de hoje: "Reiniciar agora" / "Depois".

**"Reiniciar agora":** a janela fecha pelo caminho de sempre (grava o trabalho) → aparece a janelinha do Velopack
("Atualizando para a versão X, aguarde...") → some → uns segundos sem nada na tela (o teste rápido da versão nova) → o
brasão e a janela, já na versão nova. Ressalva 3: os segundos sem nada na tela.

**"Depois":** nada muda agora; ele continua trabalhando. Ao fechar o programa aparece "Atualizar agora?" (texto na
pergunta 2). "Sim" → o programa grava e fecha → a janelinha do Velopack aparece até a troca acabar → nada abre (D-769:
na próxima vez ele já abre na versão nova, sem esperar). "Não" → fecha sem trocar; na próxima abertura o aviso de versão
nova aparece de novo.

**Versão nova que falha no teste rápido:** depois da janelinha do Velopack, a versão nova não passa no teste; ela anota,
baixa de novo a versão anterior assinada (uns minutos, nada na tela: ressalva 4), pede a troca de volta (janelinha do
Velopack de novo) e abre a anterior, que mostra uma vez "A atualização não deu certo. O programa voltou para a versão
anterior e continua funcionando. Avise o Samuel." Essa versão não é tentada de novo; espera uma mais nova.

**Clique no atalho no meio da troca:** a troca não se estraga (o Velopack fecha à força o que abriu da pasta antes de
trocar). O clique pode se perder: ele clica de novo depois que a janelinha do Velopack sumir.

**Duas janelas do programa abertas e "Atualizar agora? Sim" numa delas:** a troca não acontece (o Velopack fecharia a
outra à força, com o que estiver nela); fica anotado, e o aviso volta na próxima abertura. Nenhum texto novo na tela.

**O que pode virar problema novo:** (a) a ordem da primeira abertura (pergunta 1); (b) "Programas e Recursos" continua
mostrando a versão do instalador (fato do experimento: "Failed to update uninstall entry"; o Fable deixou para depois da
entrega); (c) se a conta do Kaique for padrão (não administrador), a pergunta do Windows pede a senha de um
administrador (não conferi o tipo da conta dele; ressalva 7).

---

## 4. O desenho

### 4.1 As peças (uma para cada conversa com o que está fora)

| Peça | Arquivo | Só ela pode |
|---|---|---|
| A regra (máquina de estados) | `core/fases_da_atualizacao.py` (novo, puro) | decidir o que acontece: `proxima_fase(estado, evento) -> (estado, efeitos)`. Não importa nada além de `dataclasses`, `enum` e `typing` (um teste lê a árvore e cobra). |
| O Windows | `core/windows.py` (existe) | a pergunta do Windows, os passos com licença, ler licenças, dono de arquivo, registro do Windows, tarefas, rodar o teste rápido, a lista de processos. |
| O Velopack | `core/conversa_com_o_velopack.py` (novo) | `import velopack`: os ganchos, a versão, procurar, baixar, o pendente, montar o pacote da anterior, trocar. **Uma função só chama a troca** (`trocar`). |
| O executor | `atualizacao.py` (refeito) | rodar os efeitos que a regra devolve, chamando as duas peças acima; o `estado.json`, o registro, o motor, a fonte de teste, a linha de comando. |
| A tela | `ui/aviso_de_atualizacao.py` | só transforma clique em evento e efeito em caixa. Nenhuma conta. |

### 4.2 "Preparado?" (§11.12 ponto 2)

É o que o Windows responde agora: **a conta que abriu consegue criar um arquivo na raiz da instalação?** É o mesmo teste
que o próprio Velopack faz para decidir se vai pedir licença na troca (fato: `misc.rs` L73-85, `is_directory_writable`,
arquivo `.velopack_dir_test` com apagar-ao-fechar; `locator.rs` L152-176 decide por ele). Fazemos igual, com outro nome
de arquivo, em `atualizacao.py` (só o disco, sem a biblioteca do Windows: leva cerca de 1 ms; ler a licença pela peça
carregaria o `core/windows.py`, ~100 ms por abertura, medidos em 19/11).
- Por que não ler a lista de licenças (D-819, o mais simples contra o outro): o teste de gravar responde exatamente "a
  troca vai pedir licença?", inclusive com grupos e negações que uma leitura da lista teria de recalcular. A leitura da
  lista (`core.windows.ler_licencas`) fica para conferir, depois do "Sim", que a licença nova está lá e herdada (seção 7).
- `os.access` não serve: no Windows ele só olha o atributo "só leitura" (a conferir na leitura do CPython antes do código).

### 4.3 Onde mora a pergunta do Windows (D-806)

`main.py` → `atualizacao.atender_linha_de_comando` (já roda **antes** do brasão e da janela) → abertura comum do programa
instalado, fora da conta de testes, pasta sem a licença → efeito `PedirLicenca` → `core.windows.comecar_pedido_de_licenca(passos)`.
- **Mudança na peça:** hoje `pedir_licenca` pergunta e espera o trabalho com licença acabar (pode levar minutos com o
  Visual C++). Ela vira duas metades da mesma conta: `comecar_pedido_de_licenca` (prepara o pedido e faz a pergunta; volta
  logo depois da resposta: "disse Não", "falhou" ou "começou") e `PedidoDeLicenca.esperar()` (espera e lê o relatório).
  `pedir_licenca` passa a ser `comecar(...).esperar()`, sem conta copiada; quem já a usa não muda.
- A espera roda num fio de trás, depois que a janela abriu. Fechar o programa no meio não estraga: o trabalho com
  licença é outro processo e termina sozinho; a próxima abertura testa a pasta de novo.

### 4.4 Os passos do pedido, nesta ordem (a peça para no primeiro que falha)

1. **Apagar o ajudante antigo** (`passo_apagar_tarefa`, já existe), só se a leitura sem licença (`core.windows.ler_tarefa`)
   achou `\EditorImpressao\Procurar versao nova`. **Segurança:** essa tarefa roda o `.exe` da pasta como o sistema; com
   Modificar para Usuários, qualquer conta poderia trocar esse `.exe`. Por isso ela sai **antes** da licença, no mesmo
   pedido. Só existe no PC do Samuel (seção 8).
2. **Instalar o Visual C++ se faltar** — tipo novo de passo `instalar_visual_c`: o lado com licença calcula sozinho o
   caminho (`<pasta do programa>\instalar\vc_redist.x64.exe`, nunca vindo do aviso), confere a assinatura da Microsoft
   (`ler_assinatura_digital`, já na peça), roda `/install /quiet /norestart` e confere a versão lida no registro depois.
3. **Tirar a instalação antiga do Inno, se houver** — tipo novo `tirar_instalacao_do_inno`: o lado com licença lê a chave
   do Inno (AppId fixo), aceita só um desinstalador `unins*.exe` dentro da pasta que a chave diz, roda em silêncio e
   confere que a chave sumiu. Os projetos não são tocados (teste `d723_o_desinstalador_do_inno_nao_apaga_os_projetos`).
4. **Dar Modificar para Usuários na raiz** — tipo novo `dar_licenca_aos_usuarios`: o lado com licença calcula a raiz
   (a pasta acima de `current`, que tem `current\sq.version` e fica em Arquivos de Programas; nada vem do aviso),
   **acrescenta** uma linha "Usuários (`S-1-5-32-545`): Modificar, passa para pastas e arquivos" e confere lendo de volta
   (a raiz e um arquivo de dentro de `current`). Nunca tira herança, nunca troca dono, nunca apaga linha (o defeito de
   18/11 foi o `/inheritance:r`). Jeito: `SetNamedSecurityInfoW` só na raiz, porque "the system automatically propagates
   any inheritable access control entries (ACEs) to existing child objects" (Microsoft, `SetNamedSecurityInfoW`,
   Remarks). O experimento provou o `icacls ... /grant ... /T`; se a prova à vista mostrar que a herança não chegou a
   algum arquivo, o passo usa o jeito provado. **O porteiro barra isso hoje (K03): pergunta 6.**

Os passos 2 e 3 já existiam (`instalar_visual_c_se_faltar`, `comando_para_tirar_o_inno`, `atualizacao.py`), rodando dentro
do "exe elevado que abre PowerShell que abre exe". Passam para a peça como passos da lista fechada; a regra de cada um
continua num lugar só.

### 4.5 Cada momento, e o que se chama

| Momento | O que acontece | Chama |
|---|---|---|
| Abrir (qualquer abertura) | `atender_linha_de_comando`: modos escondidos; ganchos do Velopack | `conversa_com_o_velopack.atender_ganchos()` (o `velopack.App().set_auto_apply_on_startup(False)...run()` de hoje; sem troca automática, senão o "Não" ao fechar trocaria na abertura seguinte) |
| Abrir, sem licença na pasta | pergunta do Windows, antes da janela | `core.windows.comecar_pedido_de_licenca` |
| Depois do "Sim" (fio de trás) | espera; testa a pasta de novo; confere a licença lida | `PedidoDeLicenca.esperar()`, `core.windows.ler_licencas` |
| Abrir com licença (fio de trás) | motor; procurar; assinatura; baixar | `atualizacao.garantir_o_motor` (do `atualizador-4`); `conversa_com_o_velopack.procurar()` (`check_for_updates`); `atualizacao.conferir_assinatura_do`; `conversa_com_o_velopack.baixar()` (`download_updates`, que confere tamanho e SHA256: fato, `manager.rs` L537-561) |
| Baixou | aviso "Reiniciar agora"/"Depois" | efeito `MostrarVersaoNova` → `ui/aviso_de_atualizacao.py` |
| "Reiniciar agora" | fecha a janela (grava); então pede a troca e sai | `conversa_com_o_velopack.trocar(alvo, reabrir=[conferir, de, para])` → `wait_exit_then_apply_updates(alvo, silent=False, restart=True, restart_args=...)` |
| Fechar com versão pronta | "Atualizar agora?"; Sim → grava, pede a troca, sai | a mesma `trocar(alvo, reabrir=[conferir, de, para, sem janela])` |
| Reaberto pelo Velopack | versão atual = a nova → teste rápido (outro processo, sem janela); = a anterior → a troca não aconteceu (o Velopack reabre a anterior com os mesmos argumentos quando a troca falha: fato, `apply.rs` L56-60) | `core.windows.rodar_e_esperar([este exe, --teste-rapido])` |
| Teste rápido falhou | anota a falha; monta o pacote da anterior; baixa; pede a troca de volta | `conversa_com_o_velopack.pacote_da_versao(anterior)` + `baixar` + `trocar(..., reabrir=[])` |

- **Antes de toda troca** (dentro de `trocar`, um lugar só): o arquivo em `packages\` tem a soma assinada? o motor está
  no lugar? há outra janela do programa aberta (`core.windows.programas_rodando_de`, vinda do `atualizador-4`, sem os
  processos filhos deste)? Qualquer "não" → não troca e anota.
- **A volta pela biblioteca, sem `Update.exe` à mão:** fato, `sources/github.rs` L129-138: o Velopack procura o arquivo
  pelo nome em todos os "Releases" lidos; `UpdateInfo` e `VelopackAsset` se montam pelo Python (`__init__.pyi` L225, L400);
  o tamanho e a soma vêm do `releases.win.json` da versão anterior, lido pela `Fonte` (como a assinatura), e a soma tem de
  bater com a assinada. Assim nenhuma linha nossa roda o `Update.exe` (K01 continua sem exceção nova).
- **Ler a versão:** `versao.VERSAO` (o número com que o pacote foi montado, D-714) em vez de perguntar ao Velopack: não
  carrega a biblioteca na abertura. "Instalado pelo Velopack" = programa empacotado com `current\sq.version` ao lado;
  "portátil" = `.portable` na raiz (fato, `locator.rs` L376). Nenhum dos dois cita o `Update.exe`.

### 4.6 A máquina de estados (`core/fases_da_atualizacao.py`)

`proxima_fase(estado, evento) -> (estado, efeitos)`, sem I/O. O estado guarda a fase, a versão atual, a nova, a
anterior e o que veio do `estado.json` (versões que não tentar, a última falha). Fases:

`fora` (código, portátil, conta de testes) · `sem_licenca` · `preparando` · `motor` · `procurando` · `conferindo` ·
`baixando` · `pronta` · `depois` · `fechando_para_trocar` · `trocando` · `conferir_nova` · `voltando` · `parado`.

Eventos: `Abriu(instalado, conta_de_testes, portatil, pasta_grava, reaberto_de, reaberto_para, sem_janela)` ·
`LicencaRespondida(desfecho)` · `PreparoTerminou(pasta_grava, motivo)` · `MotorConferido(no_lugar)` · `Procurou(versao|None, erro)` ·
`Assinatura(certa, motivo)` · `Baixou(certo, erro)` · `Escolheu(reiniciar|depois)` · `JanelaFechou(fechou)` · `Fechando` ·
`RespondeuAoFechar(sim|nao)` · `PodeTrocar(sim, motivo)` · `TesteRapido(passou, detalhe)` · `VoltaPedida(certa, motivo)`.

Efeitos: `PedirLicenca(passos)` · `EsperarPreparo` · `GarantirMotor` · `Procurar` · `ConferirAssinatura(v)` · `Baixar(v)` ·
`MostrarVersaoNova(v)` · `FecharJanela` · `PerguntarAoFechar` · `ConferirAntesDeTrocar` · `Trocar(v, reabrir)` ·
`AnotarTentativa(de, para)` · `RodarTesteRapido` · `AnotarOk(v)` · `AnotarFalha(tipo, de, para, motivo)` ·
`Voltar(v)` · `MostrarFalha(tipo)` · `Registrar(texto)` · `AbrirJanela` · `Sair(codigo)`.

Todo par (fase, evento) tem resposta escrita; o que não faz sentido naquela fase vira `Registrar` e a fase fica (nunca
exceção). O `estado.json` (`%ProgramData%\EditorImpressao\atualizacao\`, gravado pela conta do Kaique) guarda só o que
precisa passar de uma abertura para outra: as versões que não tentar, a falha a mostrar uma vez e "tentando X a partir
de Y" (para a abertura seguinte saber, comparando com a versão que de fato roda, que uma troca não aconteceu). "Há versão
baixada esperando" não se anota: é o que o Velopack diz (`get_update_pending_restart`, fato `manager.rs` L272-281).

---

## 5. O que sai, o que fica, o que vem do `atualizador-4`

**Sai de `atualizacao.py` (deste ramo):** `NOME_DA_TAREFA`, `QUEM_PODE_MANDAR_RODAR`, `LIMITE_DA_TROCA_S`,
`ESPERA_DA_VOLTA_S`, `MARCA_DE_ABERTO`, `MARCA_DA_JANELINHA`, `TEXTO_DA_JANELINHA`, `ARG_PREPARAR`, `ARG_DEPOIS_DA_TROCA`,
`_dono_do_arquivo` (vai para a peça), `update_exe`, `criar_gerente`/`versao_que_roda` (vão para a peça do Velopack),
`rodar_ao_ligar`, `_argumentos_da_fonte`, `_aplicar_pacote_quando_sair`, `marcar_programa_aberto`, `_marca_existe`,
`ha_programa_aberto`, `ha_janelinha`, `_rodar`, `script_da_janelinha`, `_linhas_da_janelinha`, `script_de_trocar_e_reabrir`,
`_aspas_do_powershell`, `_lancar_escondido`, `trocar_e_reabrir`, `aplicar_agora_e_reabrir`, `trocar_antes_de_abrir`,
`comando_de_rodar_a_tarefa`, `procurar_ao_abrir`, `comando_de_longe_para_atualizar`, `comando_de_longe_para_ler_o_registro`,
`xml_da_tarefa`, `criar_tarefa`, `rodar_tarefa_agora`, `apagar_tarefa`, `_ler_versao_do_visual_c` e `_ler_chave_do_inno`
(vão para a peça), `instalar_visual_c_se_faltar`/`tirar_instalacao_antiga`/`comando_para_tirar_o_inno` (viram passos),
`preparar_o_computador`, `preparar_como_administrador`, `criar_as_tarefas`, `arquivo_do_preparo`,
`passo_de_preparar_o_computador`, `preparo_deu_certo`, `preparar_na_primeira_abertura`,
`CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA`, `falta_a_pergunta_do_windows`, `conferir_e_refazer_o_ajudante`, `_rodar_o_velopack`.
`ARG_PROCURAR` fica só para ser reconhecido: a tarefa antiga que sobrar num PC chama o `.exe` novo com ele; o programa
anota e sai sem fazer nada.

**As peças de hoje, uma a uma:**

| Peça | Sai ou fica | Por quê |
|---|---|---|
| O ajudante (tarefa SYSTEM) | sai | Só existia para trocar em Arquivos de Programas sem pergunta. Com a licença da pasta, a conta do Kaique troca (experimento de 23/11). |
| Os scripts PowerShell (trocar e reabrir; janelinha; no `atualizador-4` também o vigia e o "só de reabrir") | saem | O Velopack espera o processo certo (o nosso) e reabre na conta certa (fato, `manager.rs` L602-675). |
| O vigia | sai (nem entra) | Só segurava a marca da troca no caminho sem script. |
| As marcas (programa aberto, janelinha, troca, reabrir) | saem | Ninguém em outra conta precisa saber se o programa está aberto. |
| `estado.json` entre contas | sai como canal | Fica um arquivo da conta do Kaique, só com o que passa de uma abertura para outra (4.6). |
| Lista de processos (esperar 30 s) | sai como espera | O `--waitPid` é o nosso. Fica `programas_rodando_de` só para "outra janela aberta → não troca". |
| `GerenteComAMarcaDaTroca`, `TrocaSemAMarca`, `FASES_EM_QUE_HA_TROCA` | saem (nem entram) | Existiam para a marca da troca. "Uma troca só por um lugar" passa a ser `conversa_com_o_velopack.trocar`. |
| Espera pela janela na frente | sai (nem entra) | A pergunta vem antes da janela (D-806). |
| A nossa janelinha | sai | D-832: a do Velopack. |
| `--preparar-o-computador` (exe elevado → PowerShell → exe) | sai | Os passos rodam direto no trabalho com licença da peça. |
| A tarefa "desfazer" na primeira abertura | sai desta entrega | Era para apagar o ajudante e desfazer os testes ao desinstalar; não há ajudante, e os testes não ligam nesta entrega. Volta com os testes à distância. |

**Fica:** `Fonte`, `fonte_da_linha`, `fonte_de_teste` (o dono do arquivo passa a ser lido pela peça), `registrar`,
`ler_estado`/`gravar_estado`, `registrar_falha`, `situacao`/`o_que_avisar` (adaptadas às fases), `_versao_assinada_do`,
`conferir_assinatura_do`, `teste_rapido`, `voltar_para_a_anterior` (pela biblioteca), `conferir_versao_nova` (com a
versão de antes e a nova pela linha de comando), `e_a_conta_de_testes`, `e_portatil`, `instalado_pelo_velopack`,
`ao_instalar`, `ao_atualizar`, `ao_desinstalar` (continua mandando o "desfazer" dos testes, se existir),
`atender_linha_de_comando`, os textos (`TITULO_*`, `FRASE_*`, `BOTAO_*`), as constantes do Inno e do Visual C++ (vão para
a peça, que as usa nos passos).

**Vem do `atualizador-4`:** `garantir_o_motor`, `motor_esta_no_lugar`, `_apagar_pasta_do_motor`, `FOLGA_DO_MOTOR_BYTES` e
o ramo "sem motor → nada anunciado" (D-833); `core/ocr_kraken.py`: `pasta_do_motor_instalado` e o lugar único do motor no
programa instalado; o teste rápido conferindo o motor pela `core/ocr_kraken`; `configuracoes.py` sem a marca
`atualizacao_computador_preparado`; `ui/testes_a_distancia_ui.py`: a senha não liga nada (D-825); `core/windows.py`:
`programas_rodando_de`; e os testes do conserto 4 que cobram o motor. **Não vem:** o resto da volta 2 a 4 (marca da
troca, vigia, esperar a janela, ler as tarefas, os 30 s, as 30 tentativas do `gravar_estado`).

---

## 6. Caminho → função (§11.12)

| Caminho | Entra por | A regra | A ação |
|---|---|---|---|
| Abrir pelo atalho | `main.py` → `atualizacao.atender_linha_de_comando` | `proxima_fase(Abriu)` | `PedirLicenca` → `core.windows.comecar_pedido_de_licenca`; ou `GarantirMotor`/`Procurar` no fio de trás |
| Abrir na conta de testes / pelo código / portátil | o mesmo | `proxima_fase(Abriu)` → `fora` | nada |
| Reaberto pelo Velopack | o mesmo, com os argumentos de conferir | `proxima_fase(Abriu(reaberto_*))` | `RodarTesteRapido` → `core.windows.rodar_e_esperar` |
| "Reiniciar agora" | `ui/aviso_de_atualizacao.py` → evento `Escolheu(reiniciar)` | `proxima_fase` | `FecharJanela`, depois `Trocar` → `conversa_com_o_velopack.trocar` |
| "Depois" | o mesmo → `Escolheu(depois)` | `proxima_fase` | nada agora |
| Fechar o programa | `ui/janela_principal.py` `closeEvent` → `ui/aviso_de_atualizacao.ao_fechar` → `Fechando` | `proxima_fase` | `PerguntarAoFechar` → `RespondeuAoFechar` → `Trocar` → `conversa_com_o_velopack.trocar` |
| A volta para a anterior | `proxima_fase(TesteRapido(falhou))` | `proxima_fase` | `Voltar` → `atualizacao.voltar_para_a_anterior` → `conversa_com_o_velopack.baixar` + `trocar` |
| O motor do Kraken | `proxima_fase` (antes de procurar; e dentro de `trocar`) | `motor_esta_no_lugar` (uma só) | `atualizacao.garantir_o_motor` (o único que mexe em `motor-kraken\`) |
| Os ganchos do Velopack (instalar, atualizar, desinstalar) | `atender_linha_de_comando` → `conversa_com_o_velopack.atender_ganchos` | — | `ao_instalar`/`ao_atualizar`/`ao_desinstalar` |
| A tarefa antiga chamando `--procurar-atualizacao` | `atender_linha_de_comando` | — | `Registrar` e sai |

Toda troca passa por **uma** função (`conversa_com_o_velopack.trocar`), e só ela chama `wait_exit_then_apply_updates`.
Prova: um teste que lê a árvore e cobra que esse nome aparece só ali; e um teste que passa por "Reiniciar agora", "Sim ao
fechar" e a volta e cobra que os três chegam a `trocar`, com a mesma conferência antes.

---

## 7. A lista das falhas (§11.12 ponto 3)

Regra para todas: nada fica pela metade sem a tela dizer, nunca "deu certo" sem conferir, e o erro técnico vai para o
registro, nunca para a tela.

**A pergunta do Windows e a preparação**
- A pessoa clica "Não" (ou fecha a pergunta): a peça devolve "disse Não" (erro 1223, já provado na peça). Nada muda; a
  janela abre; na próxima abertura pergunta de novo. Tela: nada.
- A conta é padrão e ninguém sabe a senha de administrador: igual ao "Não". Pergunta toda abertura (D-741). Ressalva 7.
- O Windows não abre o pedido (sem licença de rodar, programa sumiu): "falhou"; abre a janela; registra; pergunta de novo
  na próxima.
- Ninguém responde à pergunta: a abertura fica parada na pergunta (ela está no meio da tela, com o resto escurecido).
- Visual C++ falha / Inno falha: a peça para ali; a licença não é dada; a pasta continua sem gravar; a pergunta volta
  (D-749). Registro: qual passo e o motivo.
- A licença não "pega" (lida de volta sem a linha, ou um arquivo de dentro sem ela): o passo devolve "falhou" com o que
  faltou; a pergunta volta. Se a raiz já grava mas um arquivo de dentro não, a troca do Velopack falharia num arquivo:
  por isso a conferência lê também um arquivo de `current`.
- Desligar no meio da preparação: o que já foi feito fica (o Visual C++ é transacional; o Inno pode ficar pela metade e é
  tentado de novo); a licença ou foi dada ou não. A próxima abertura testa a pasta e decide.
- A tarefa antiga do ajudante existe e não dá para apagar: a peça para nesse passo; a licença **não** é dada (segurança).

**Procurar, conferir, baixar**
- Sem internet / GitHub fora do ar: `check_for_updates` levanta; registra; tela nada; tenta na próxima abertura.
- A assinatura errada ou ausente: não baixa; anota a falha ("recusada") e a versão em "não tentar"; a tela mostra o aviso
  de falha uma vez (qual frase: pergunta 4).
- O motor do Kraken não está no lugar e o arquivo dele não está em `current\instalar\`: nada é baixado nem anunciado
  (D-833); registra; tenta de novo na próxima. Disco sem espaço para o motor: confere antes (como no `atualizador-4`).
- Disco cheio no download: o Velopack falha; o arquivo `.partial` fica e é apagado no próximo download (fato, `manager.rs`
  L437-480); registra; tela nada.
- Outro download segurando a tranca do Velopack (duas janelas abertas): `download_updates` falha pela tranca (fato,
  `manager.rs` L406); registra; a outra janela segue.
- Fechar o programa no meio do download: o fio de trás morre com o programa; fica o `.partial`; nada a desfazer.

**Trocar**
- O arquivo em `packages\` não tem a soma assinada (trocado depois de baixar): não troca; anota "recusada".
- Outra janela do programa aberta: não troca; registra; o aviso volta na próxima abertura.
- A janela não fecha no "Reiniciar agora" (ela recusou fechar): nada é trocado; o aviso continua valendo.
- O programa demora mais de 60 s para sair depois de pedir a troca: o Velopack o fecha à força (fato, documentação
  `docs.velopack.io/integrating/overview`). Por isso a troca é pedida só **depois** de gravar e parar os trabalhos.
- Outro programa segura um arquivo de `current` (antivírus, Explorador aberto na pasta): o Velopack tenta 10 vezes e
  desiste antes de mexer ("Unable to start the update", fato, `apply_windows_impl.rs` L161-163); reabre a anterior com os
  nossos argumentos (fato, `apply.rs` L56-60); ela vê que continua na versão de antes, anota a falha "troca" e a tela
  avisa uma vez.
- Falha da **segunda** troca de nome ("the app was left in a broken state", fato, L174-176): `current` fica faltando; o
  programa não abre. Remédio: reinstalar pelo `.msi` (os projetos ficam). É o defeito do Velopack que a D-779 quer cercar;
  a proteção ficou para depois (ressalva 6).
- Desligar no meio da troca: o mesmo caso acima, se for entre as duas trocas de nome; senão, ou trocou ou não trocou.
- A volta precisa de internet (baixar a anterior); sem internet: anota a falha, a tela diz o que ficou (pergunta 4) e a
  versão nova abre se conseguir.
- A versão anterior não está entre os 10 "Releases" mais novos do GitHub: o Velopack não a acha (fato, `sources/github.rs`
  L80, `per_page=10`); igual a "sem internet". Só acontece se houver mais de 9 versões publicadas depois dela.

**A pasta sem a licença (instalação antiga, reinstalação):** igual à primeira abertura: pergunta. Sem o "Sim", nada se
procura (se procurasse, o Velopack usaria a pasta de reserva e pediria licença em toda troca: fato, `locator.rs` L159-176
e `apply_windows_impl.rs` "Re-launching as administrator").

---

## 8. O que o desenho antigo deixou nos PCs

- **No notebook do Kaique:** nada. O desenho antigo nunca foi instalado lá (lá há só o instalador antigo de 28/10, que o
  passo 3 tira).
- **No PC do Samuel:** as tarefas `\EditorImpressao\Procurar versao nova` (desligada no experimento) e
  `\EditorImpressao\Desfazer testes a distancia`, a pasta `\EditorImpressao` do Agendador, `C:\ProgramData\EditorImpressao\atualizacao\`
  (do sistema; a conta comum só lê; o programa novo não conseguiria gravar o registro ali), `...\testes-a-distancia\desfazer.ps1`
  e o `fonte-de-teste.txt` (fica: o programa novo continua usando nas provas).
- **O que o programa novo limpa sozinho:** só o ajudante antigo, e só por segurança (passo 1 de 4.4), na mesma pergunta,
  antes da licença. Nada mais: escrever limpeza para um estado que só existe num PC é código a mais (D-819).
- **O resto:** à mão, pela gerente, com o Samuel vendo, numa pergunta do Windows, antes da prova à vista. O jeito mais
  limpo: desinstalar a 1.1.x por "Programas e Recursos" (o gancho dela manda rodar o "desfazer", que apaga o ajudante e a
  si mesmo), conferir só lendo o que sobrou e apagar o resto com o "sim" dele (pergunta 7). Fora do projeto, eu não apago
  nada.
- **Não sei se o experimento de 23/11 foi desfeito** (o passo 6 do roteiro). Se a pasta continua com Modificar para
  Usuários e a tarefa do ajudante existe (desligada), um administrador que a ligasse rodaria como o sistema um `.exe` que
  qualquer conta pode trocar. Sugestão à gerente: conferir só lendo (`icacls` da raiz e `schtasks /Query`) e, se for o
  caso, apagar a tarefa logo.

---

## 9. Os arquivos que vou mexer

Programa:
- `atualizacao.py` (refeito; ~400 linhas).
- `core/fases_da_atualizacao.py` (novo).
- `core/conversa_com_o_velopack.py` (novo).
- `core/windows.py`: `comecar_pedido_de_licenca`/`PedidoDeLicenca` (e `pedir_licenca` por cima delas); os três tipos de
  passo novos; `ler_versao_do_visual_c`, `ler_instalacao_do_inno`, `dono_do_arquivo`; `programas_rodando_de` (do
  `atualizador-4`).
- `core/ocr_kraken.py`: o lugar do motor no instalado (do `atualizador-4`).
- `configuracoes.py`: sai a marca (do `atualizador-4`).
- `main.py`: só comentários (a ordem já é a certa).
- **Tela, precisa do "pode" explícito da gerente (o implementador não mexe em `ui/` sem isso):**
  `ui/aviso_de_atualizacao.py` (sai o relógio de 5 em 5 minutos; recebe os efeitos; o "Atualizar agora?"),
  `ui/janela_principal.py` (uma chamada no `closeEvent`, antes de aceitar o fechar), `ui/testes_a_distancia_ui.py` (a
  primeira abertura não pergunta mais nada ao Windows; a senha não liga nada), `ui/brasao_girando.py` (deixa de pôr a marca
  e de esperar a janelinha).

Testes:
- novos: `tests/test_fases_da_atualizacao.py`, `tests/test_atualizador_novo.py` (e os do motor vindos do `atualizador-4`).
- `tests/test_trava_windows.py` (catraca, seção 10).
- os antigos da seção 2, **só depois do "sim" dele** (pergunta 5).

Não mexo: `empacotar.py`, `publicar_versao_kaique.py`, `core/testes_a_distancia.py`, `core/_testes_a_distancia_windows.py`,
o porteiro e a lista de exceções. Qualquer outro arquivo, só com o "pode" da gerente.

---

## 10. As travas

**A catraca (`tests/test_trava_windows.py`):** saem da `LISTA_CONGELADA` as 12 linhas de `atualizacao.py` (o
`import subprocess`; as 5 de `_dono_do_arquivo`; as 2 de `marcar_programa_aberto`; as 2 de `_marca_existe`; a de
`_ler_versao_do_visual_c`; a de `_ler_chave_do_inno`). `TETO` desce de 46 para **34**. As 8 de
`core/_testes_a_distancia_windows.py` ficam (os testes à distância não mudam nesta entrega). Os arquivos novos não usam
`ctypes`, `subprocess`, `winreg` nem `os.startfile`. O `core/windows.py` é o dono (não entra na lista). Se no meio do
código eu precisar de um lugar novo fora dos donos, a catraca falha e eu paro.
- Proposta (só com o "pode" da gerente; não é lugar novo, é capacidade nova): "Velopack" como capacidade com dono
  `core/conversa_com_o_velopack.py`, para a trava cobrar que ninguém mais importa `velopack`.

**O porteiro (`tests/conferencias_excecoes.json`, eu não mexo):** quando `atualizacao.py` for refeito,
`tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` vai falhar com:
- **40 linhas "a lista de exceções tem um lugar que o código já não tem (sobraram 0 de 1): tire ou diminua o item ..."**,
  uma por item de `atualizacao.py`: 33 K01 (`_aplicar_pacote_quando_sair` 2, `_dono_do_arquivo` 5, `_lancar_escondido` 3,
  `_ler_chave_do_inno` 4, `_ler_versao_do_visual_c` 5, `_linhas_da_janelinha` 1, `_marca_existe` 3, `apagar_tarefa` 1,
  `comando_de_rodar_a_tarefa` 1, `criar_tarefa` 1, `marcar_programa_aberto` 1, `passo_de_preparar_o_computador` 1,
  `script_de_trocar_e_reabrir` 4, `update_exe` 1), 2 K02 e 5 K04. O comando que a mensagem sugere é o da gerente.
- **Um K03 novo em `core/windows.py`** (a função do passo `dar_licenca_aos_usuarios`): a K03 vale "em qualquer arquivo do
  programa (até na peça única)". Não há como dar a licença sem isso. Pergunta 6.
- Os arquivos novos não terão nenhuma palavra da K01 no código (nem `Update.exe`: ver 4.5) nem número de decisão em texto
  de tela ou de registro (K04).
- O juiz do GitHub usa a lista da versão de teste: a rodada vai dizer "BARROU" até a gerente juntar a lista nova.

---

## 11. Como vai provar (D-767, D-811 a D-813, D-827)

**Testes de comportamento, não de texto.** Nenhum teste confere se uma palavra está num texto de PowerShell (não haverá
PowerShell no atualizador).
- **A regra, exaustiva:** `tests/test_fases_da_atualizacao.py` passa por **todos** os pares (fase, evento) e cobra a
  fase e os efeitos de cada um, numa tabela escrita no teste; e lê a árvore do arquivo para cobrar que ele não importa
  nada que fale com o mundo de fora.
- **O executor, com as duas peças de mentira só na borda** (a de mentira anota o que pediram; a lógica em volta é a de
  verdade): abrir sem licença → o primeiro efeito é a pergunta e nenhum `procurar`; "Não" → nada procurado nem gravado;
  "Sim" com o Visual C++ falhando → a licença não é pedida (a peça de verdade para no passo; teste da peça); assinatura
  errada → nenhum `baixar`; motor fora → nada anunciado; "Reiniciar agora" → a janela fecha antes de `trocar`; "Depois" +
  fechar + "Sim" → `trocar` com "sem janela"; reaberto na anterior → falha "troca"; teste rápido falha → `voltar` com o
  pacote assinado; outra janela aberta → não troca.
- **Uma prova por proteção, que falha quando ela é desligada** (o verificador desliga cada uma numa cópia e mostra a
  falha): (1) sem licença não procura; (2) assinatura antes de baixar; (3) soma conferida no arquivo antes de trocar; (4)
  motor antes de anunciar e antes de trocar; (5) a licença é o último passo; (6) o ajudante antigo sai antes da licença;
  (7) a conta de testes não procura nem pergunta; (8) versão que falhou não é tentada de novo; (9) outra janela aberta
  não troca; (10) a troca só depois de a janela fechar; (11) a volta só com pacote assinado; (12) pelo código nada roda;
  (13) só `trocar` chama a troca do Velopack.
- **A biblioteca do Velopack de verdade**, sem trocar nada: uma instalação falsa numa pasta de prova (como a do
  pesquisador), uma fonte de pasta com duas versões: `procurar` acha a nova; o pacote da anterior é montado e **baixado**
  para a pasta de prova com o tamanho e a soma conferidos pelo próprio Velopack. Não chama `trocar` (isso roda o
  atualizador do Velopack: só à vista).
- **A peça do Windows de verdade, no GitHub** (máquina jogada fora, como os testes de tarefa de hoje; no PC do Samuel
  não roda, D-785): o passo da licença numa pasta de prova → um arquivo de dentro passa a ter Modificar herdado, nenhuma
  linha antiga sumiu, a herança não foi cortada; e o teste de gravar dá "não" antes e "sim" depois.

**Só se prova rodando de verdade, à vista, no PC do Samuel** (D-767, D-785, D-773: as versões servidas por uma janela
visível; uma conta sem a janela "como administrador"):
1. Instalar pelo `.msi`; primeira abertura: a pergunta vem no meio da tela, logo no clique (print). "Não" → abre; fechar
   e abrir → pergunta de novo. "Sim" → abre; a licença lida de volta; o motor posto; o Inno de 01/09 tirado (D-729).
2. Publicar uma versão de prova; abrir → aviso; "Reiniciar agora" → janelinha do Velopack (print) → abre na nova.
3. Outra versão; "Depois"; fechar → "Atualizar agora?" (print) → "Sim" → janelinha → abrir → já na nova, sem espera.
   "Não" → abrir → o aviso volta.
4. Uma versão quebrada de propósito → volta para a anterior → a frase (print).
5. Uma versão com assinatura falsa → recusada → a frase (print).
6. Fechar a janela das versões no meio do download → nada na tela, nada quebrado; abrir de novo → baixa.
7. Tirar o motor do lugar → nada anunciado.
8. Clicar no atalho durante a janelinha do Velopack → a troca termina.
9. Desinstalar → a pasta inteira some (com o motor); os projetos ficam.
10. Medir: quanto tempo a abertura do programa instalado leva antes e depois (o teste de gravar), e os segundos sem
    nada na tela depois da troca.

Antes da prova, quem tenta quebrar (agente novo, D-775/D-815) confere a leitura do Velopack desta seção e da 4.5 contra o
código dele.

---

## 12. Perguntas para o Samuel (§11.13; a gerente leva à Central)

Antes de cada uma procurei no Livro (D-705 a D-833) e no `resposta-do-fable.md`; o porquê de ainda estar aberta vai em
cada uma. Prints: não há tela nova ainda; os prints das perguntas 1 a 3 só existem depois do código (a gerente pode
montar um desenho da caixa com o texto antes de publicar).

**Pergunta 1 — A ordem da primeira abertura**
- *Do que se trata:* a primeira vez que o Kaique abre o programa instalado. Hoje aparece primeiro a janelinha da senha
  dos testes à distância e, depois do clique nela, a pergunta do Windows "Deseja permitir...?".
- *O que muda:* para a pergunta do Windows vir sempre no meio da tela (como você escolheu em 19/11), ela passa a vir
  **logo depois do clique no atalho, antes da janela do programa**. A janelinha da senha aparece depois, quando a janela
  já abriu. A senha continua sem ligar nada nesta versão, como você decidiu em 21/11.
- *O que você escolhe:* (1) **sugestão:** a pergunta do Windows primeiro, a senha depois; (2) a senha primeiro, e a
  pergunta do Windows depois dela, só na primeira vez (nas aberturas seguintes, depois de um "Não", ela vem antes da janela
  do mesmo jeito); (3) só comentário.
- *O que muda no que já funciona:* só a ordem das duas janelas na primeira vez. Situação: plano, nada feito.
- *Por que pergunto:* você decidiu a pergunta "no instante do clique" e a senha "na primeira vez", mas nunca a ordem
  entre as duas.

**Pergunta 2 — O texto da pergunta ao fechar e do aviso da versão nova**
- *Do que se trata:* quando chega uma versão nova com o programa aberto, aparece o aviso "Reiniciar agora / Depois". Hoje
  ele diz: "Se escolher "Depois", a versão nova entra sozinha na próxima vez que você abrir o programa." Com a sua
  escolha de 19/11, o "Depois" passa a perguntar ao fechar. Você disse que o texto da pergunta ao fechar seria decidido
  antes de construir.
- *O que você escolhe:*
  - Aviso: (A) "Se escolher "Depois", o programa pergunta de novo quando você fechar." (B) "Se escolher "Depois", você
    pode atualizar quando fechar o programa."
  - Pergunta ao fechar: (A, sugestão) título "Atualizar agora?", texto "Há uma versão nova do programa pronta. Quer
    atualizar agora, ao fechar? Leva uns 2 minutos e da próxima vez o programa já abre na versão nova.", botões
    "Atualizar agora" e "Agora não". (B) o mesmo título, texto curto "Quer atualizar o programa agora, ao fechar?",
    botões "Sim" e "Não". (C) só comentário.
- *O que muda no que já funciona:* só esses textos. Situação: plano.

**Pergunta 3 — O ícone perto do relógio**
- *Do que se trata:* em 19/11 você pediu que, no "Sim" ao fechar, aparecesse um ícone perto do relógio com a
  porcentagem. Em 23/11 você disse que a janelinha da troca é a do próprio Velopack, por enquanto. A janelinha do
  Velopack aparece no meio da tela, em português ("Atualizando para a versão X, aguarde..."), com uma barra.
- *O que você escolhe:* (1) **sugestão:** nesta versão, no "Sim" ao fechar aparece a mesma janelinha do Velopack do
  "Reiniciar agora"; o ícone perto do relógio vai para a lista de espera, junto com o texto e o brasão nossos; (2) fazer o
  ícone agora (é uma janela nossa, que precisa ficar viva depois que o programa fecha: volta parte do que o desenho novo
  tirou); (3) só comentário.

**Pergunta 4 — Os três avisos de falha**
- *Do que se trata:* em 18/11 você escolheu três frases, uma para cada falha da atualização; em 21/11 elas ficaram para
  uma atualização depois. Hoje existe só uma: "A atualização não deu certo. O programa voltou para a versão anterior e
  continua funcionando. Avise o Samuel."
- *O que acontece se continuar uma só:* em dois casos a frase diz uma coisa que não aconteceu: quando a versão chega sem
  a sua assinatura (o programa nem saiu da versão dele) e quando a volta não deu certo (ela diria "voltou").
- *O que você escolhe:* (1) **sugestão:** as três frases que você já escolheu entram agora (é só escolher a frase certa
  para cada caso; nada de tela nova); (2) continua uma frase só nesta versão; (3) só comentário.

**Pergunta 5 — Os testes antigos do atualizador**
- *Do que se trata:* o programa tem testes automáticos que conferem, a cada mudança, o que você decidiu sobre a
  atualização. Muitos conferem as peças que saem (o ajudante que rodava como o sistema, os scripts, a nossa janelinha, as
  marcas) ou decisões que você mesmo mudou depois (o "Depois" na próxima abertura virou "ao fechar"; a nossa janelinha
  virou a do Velopack).
- *O que você escolhe:* (1) **sugestão:** (a) os que conferem peças que saem saem, e cada decisão que eles cobravam e
  continua valendo ganha um teste novo pelo caminho novo; (b) os que cobram as mesmas decisões passam a chamar o caminho
  novo, com a mesma conferência; (c) os que cobram decisões que você mudou passam a cobrar o que vale hoje. A lista, teste
  por teste, vai com a entrega, e o verificador mostra cada teste novo falhando no código de antes; (2) mostrar a lista
  antes, um por um; (3) só comentário.
- *O que muda no que já funciona:* nenhum comportamento que você escolheu deixa de ser conferido.

**Pergunta 6 — O porteiro e a licença da pasta**
- *Do que se trata:* o porteiro é a conferência automática que barra código com erro já conhecido. Uma das regras
  proíbe mexer na licença de pasta em qualquer parte do programa, por causa do defeito de 18/11 (uma tranca feita à mão
  deixou arquivos sem leitura). O desenho novo precisa fazer isso uma vez: **acrescentar** "Usuários podem modificar" na
  pasta do programa, sem tirar nada.
- *O que você escolhe:* (1) **sugestão:** a regra passa a deixar só essa função da peça do Windows, e só para acrescentar
  (nunca tirar herança nem trocar dono); continua barrando em todo o resto; (2) o lugar entra na lista de exceções; (3) só
  comentário.
- *O que muda no que já funciona:* nada para o Kaique. Sem uma das duas, o trabalho não entra.

**Pergunta 7 — A limpeza do seu PC antes da prova**
- *Do que se trata:* o atualizador antigo deixou no seu PC duas tarefas do Windows, uma pasta delas no Agendador e duas
  pastas em `C:\ProgramData\EditorImpressao` (uma delas impede o programa novo de gravar o registro da atualização). No
  notebook do Kaique não há nada disso.
- *O que você escolhe:* (1) **sugestão:** antes da prova, desinstalar a versão de teste pelo "Programas e Recursos" (ela
  mesma apaga as tarefas), a gerente confere só lendo o que sobrou e mostra a lista, e o que sobrar é apagado com o seu
  "sim", com você vendo; o programa novo só apaga sozinho a tarefa antiga do ajudante, se achar, por segurança; (2) o
  programa novo apaga tudo isso sozinho, em qualquer PC; (3) só comentário.

---

## Ressalvas do plano

1. **A pergunta sem janela dona:** pedir a licença antes de existir janela confia no direito de vir para a frente que o
   Velopack passa ao programa. Li o código que dá esse direito; não provei que a pergunta vem no meio da tela assim. É o
   primeiro item da prova à vista; se piscar, a saída é perguntar com a janela já aberta (o que a espera da volta 4
   tentava resolver).
2. **A herança da licença em arquivos abertos:** não conferi que o Windows muda a licença de um arquivo em uso (o
   programa roda de `current` durante a preparação). A leitura de volta pega; a prova à vista confirma.
3. **Segundos sem nada na tela** depois da janelinha do Velopack, enquanto o teste rápido roda. Não medi.
4. **A volta baixa a anterior** (uns minutos, nada na tela; a versão quebrada fica aberta nesse tempo). É o
   comportamento do `atualizador-4`; guardar a versão que funciona (a proteção da D-779) resolveria e ficou para depois.
5. **Uma troca que falha por um arquivo preso** põe a versão em "não tentar" (como hoje), mesmo sendo passageira.
6. **O defeito do Velopack** na segunda troca de nome (programa sem `current`) continua sem proteção nesta entrega.
7. **Conta padrão:** se a do Kaique não for administradora, a pergunta pede a senha de um administrador. Não conferi.
8. **"Programas e Recursos"** fica na versão do instalador (o Fable deixou para depois).
9. **O registro no `ProgramData`** é criado pela conta do Kaique: outra conta do PC só lê, e desinstalar não o apaga.
10. **O botão das Configurações dos testes à distância** continua chamando o caminho antigo (`core/_testes_a_distancia_windows.py`,
    com o "Não" lido como 0 por falta do `use_last_error`). Não faz parte desta entrega (D-825 só tirou a senha da
    primeira abertura), mas está ao alcance do Kaique.
11. **A leitura do Velopack** foi feita no código da etiqueta `1.2.161` (clone no rascunho, `92d6a1c9`), arquivos e
    linhas citados acima; o que não citei com linha não conferi.

## Ideias para a Lista de espera

- Guardar o pacote da versão que funciona antes de trocar (volta sem internet e sem os minutos de espera; é a D-779).
- Uma troca que falha por arquivo preso não deveria pôr a versão em "não tentar".
- O brasão girando durante o teste rápido da versão nova.

---

# ONDE-PAREI — a trava dos donos, terceira volta (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`, a partir de
`d792ebfc`. Pedido da gerente de 23/11/2026, com a revisão do Fable aos 5 pontos que não fechavam na segunda volta.

**Situação: a terceira volta está feita e esperando a gerente.** A trava passa hoje, pela catraca: 46 lugares
congelados, `TETO = 46`. Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q`:
**40 passed, 3 skipped** (as três pendências paradas). Só mudaram `tests/test_trava_windows.py` e este arquivo. As voltas
anteriores ficam abaixo, como estavam.

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer", e a trava do Fable: cada capacidade só no seu dono, "binário, sem lista de
  exceções". Nesta volta: a catraca no lugar do `xfail`, o mapa final, os nomes proibidos ao dono das DLLs e as raízes.
- **D-765:** nenhuma linha do programa muda. Não mudou: só o teste e o ONDE-PAREI.
- **§11.8 / D-605:** nenhum teste antigo muda. Nenhum teste de fora deste arquivo foi tocado (ver a ressalva 6 sobre as
  provas da segunda volta, que são deste mesmo arquivo novo).
- **D-809:** nada de comando que mude o `.git` inteiro. Só `git ls-files` pela peça do git, e `git add`/`commit`/`push`.
- **D-793 / §11.11:** não abri outro agente. Não abri janela nem rodei o programa.
- **Do pedido:** nada no porteiro e nada no `empacotar.py`.

## Como cumpri cada uma

- D-830: a trava é binária para lugar novo (falha na hora) e sem lista de exceções que cresça (a lista congelada só
  diminui, com teto). Provas na seção "As provas".
- D-765, porteiro, `empacotar.py`: `git diff --stat` mostra só `tests/test_trava_windows.py` e este arquivo.
- §11.8: nenhum arquivo de teste além deste foi aberto para escrita.
- D-809 / D-793: só os comandos acima; nenhum agente aberto.

## O que já está escolhido e testado aqui

- A primeira e a segunda volta deste mesmo teste (só neste ramo). O desenho dos donos da segunda volta continua; o mapa
  mudou pelo pedido (o `subprocess` agora tem dois donos).
- O porteiro e a lista de exceções (`regras_dos_agentes/`): não mexi. O porteiro (`conferir_codigo`) rodado no arquivo
  novo dá 0 achados.

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF: nenhuma linha do programa mudou. O que muda é a rodada do GitHub: a trava agora
passa (sem `xfail`) e fica vermelha na hora em que alguém usar uma capacidade num lugar novo fora do dono, ou quando
um lugar da lista for consertado sem tirar a linha.

## O que mudou no teste

1. **Catraca no lugar do `xfail`.** A marca saiu. `LISTA_CONGELADA` tem os 46 lugares de hoje, um por linha, separados
   em grupos com comentário. `conferir_a_catraca` cobra:
   - **lugar novo:** chave acusada que não está na lista falha na hora ("LUGAR NOVO ...", com a linha onde está);
   - **lugar perdoado à toa:** chave da lista que não é mais acusada falha com "tire esta linha da lista e abaixe o
     teto";
   - **o teto:** `assert len(LISTA_CONGELADA) <= TETO`, `TETO = 46`; e linha repetida na lista também falha.
   - Falha de leitura (raiz que falta, `OCULTOS` ilegível, arquivo que não abre) nunca entra na catraca: sempre falha.
2. **A chave do lugar:** `"arquivo | função onde mora | capacidade | o que foi achado"`, sem o número da linha. Ex.:
   `atualizacao.py | _marca_existe | Windows pelo ctypes | usa ...windll`. A função vem da peça de leitura do porteiro
   (`leitura.funcao_em_volta`, com a classe na frente: `BibliotecaScanTailor._carregar`); fora de função, `(fora de
   função)`. **Por quê:** escrever código acima não muda nenhuma das quatro partes (tem prova: dez linhas novas acima,
   mesma chave, linha diferente). Quando o lugar muda de verdade (outra função, outro jeito de importar, outra
   capacidade), a chave muda, e a catraca acusa um novo e um que sumiu, que é o certo. O mesmo jeito repetido na mesma
   função é um lugar só (os doze `wintypes.DWORD` do corpo de `core/_testes_a_distancia_windows.py` são uma linha).
3. **Mapa final dos donos:** `core/windows.py` → `ctypes` (com "Windows pelo ctypes"), `winreg`, `os.startfile`,
   `subprocess`; `core/nativo_dll.py` → `ctypes` e carregar DLL; `core/processos.py` → `subprocess`. O
   `core/windows.py:91` (`import subprocess`) saiu da lista. O `explorer /select` do `historico.py` continua acusado.
4. **`os.system/popen/spawn*/exec*`:** continuam proibidos em todo lugar, inclusive nos donos. Nada mudou
   (`test_rodar_programa_pelo_os_nao_tem_dono`).
5. **Os nomes do Windows no dono das DLLs:** `windll`, `WinDLL`, `oledll`, `OleDLL`, `wintypes`, `get_last_error`,
   `FormatError`, `GetLastError` viraram a capacidade "Windows pelo ctypes", cujo único dono é `core/windows.py`. São
   acusados como atributo (pelo nome, venha de onde vier: `ctypes.windll`, `kernel32.GetLastError`), como nome importado
   (`from ctypes import windll` e o uso dele), no `import ctypes.wintypes`, no `from ctypes.wintypes import ...` e no
   `getattr(ctypes, "windll")`. Ver o ponto 2 de "O que não fechou": isso vale em todo arquivo, não só no dono das DLLs.
6. **Raízes do fechamento** (`raizes_do_programa`): `main.py`; `motor_kraken/servidor_kraken.py`, procurando os módulos
   na pasta dele (roda com `python -I servidor_kraken.py`, então a pasta do script é onde o Python procura); e os módulos
   nossos da `OCULTOS` do `empacotar.py`.
   - **A `OCULTOS` dá para ler sem rodar:** é `OCULTOS = [...]` no corpo do `empacotar.py` (linha 165), uma lista de
     textos fixos, usada só em `for modulo in OCULTOS: comando += ["--hidden-import", modulo]` (linhas 883-884). Lida
     com `ast.literal_eval`. Se um dia ela for montada por função, ganhar `append`/`+=`, outra atribuição, um
     `--hidden-import` fora do laço, ou aparecer `--collect-submodules`/`--collect-all`/`--hiddenimport`, a leitura
     falha e diz a linha. Módulo que parece nosso (`core.x`) e não tem arquivo também falha. O `empacotar.py` não mudou.
   - Os 8 módulos nossos da `OCULTOS` (`core.gravura_scantailor`, `core.st_ferramentas`, `core.ocr_comum`,
     `core.ocr_doctr`, `core.ocr_tesseract`, `core.ocr_kraken`, `core.ocr_comparar`, `core.ocr_diagnostico`) já estavam
     no fechamento do `main.py`. Os de fora (`doxapy`, `skimage.filters`, `PIL._tkinter_finder`, `onnxtr...`) ficam fora.
   - O fechamento passou de 121 para 122 arquivos: entrou só o `motor_kraken/servidor_kraken.py`.
   - **O motor do Kraken não usa nenhuma das capacidades** (nenhum lugar acusado nele). Ele só importa a biblioteca do
     Python, o numpy, o PIL, o kraken, o torch e o psutil. Não inventei dono.
7. **As duas pendências do `subprocess`**, paradas enquanto `core/processos.py` não existir (como a do `CDLL`):
   `test_pendencia_a_peca_do_windows_so_lanca_programa_da_pasta_do_windows` e
   `test_pendencia_a_peca_dos_processos_recusa_programa_da_pasta_do_windows`. Ver o ponto 1 de "O que não fechou".

## A contagem nova: 46 lugares, TETO = 46

- **(a1) Atualizador e testes à distância: 20.** `atualizacao.py` 12 (o `import subprocess`; `_dono_do_arquivo` 5;
  `marcar_programa_aberto` 2; `_marca_existe` 2; `_ler_versao_do_visual_c` e `_ler_chave_do_inno`, o `winreg`);
  `core/_testes_a_distancia_windows.py` 8 (5 no corpo do arquivo, 3 em `_rodar_elevado`, entre eles o `get_last_error`).
- **(a2) Windows de verdade em outras partes: 9.** `core/nucleos.py` 2, `core/ocr_comum.py` (`abrir_processo`) 2,
  `historico.py` 3 (o `explorer /select` e os dois `os.startfile`), `ui/brasao_girando.py` 2.
- **(b) As nossas DLLs: 12.** Os 10 `import ctypes` e os 2 `CDLL`.
- **(b) Os nossos processos: 5.** `core/ocr_comum.py`, `core/ocr_kraken.py`, `core/ocr_tesseract.py`,
  `core/paginas_em_outro_processo.py`, `ui/tela_de_carregamento.py`.
- Diferença para a segunda volta (34): sai o `core/windows.py:91` (−1); a contagem agora é por chave, e não por linha
  (não muda nada nos 33 que ficam: nenhuma chave deles se repete); e entram 13 chaves de "Windows pelo ctypes" (5 em
  `atualizacao.py`, 5 nos testes à distância, 1 em cada um de `core/nucleos.py`, `core/ocr_comum.py` e
  `ui/brasao_girando.py`). 34 − 1 + 13 = 46. Por linha seriam 61 (os `wintypes` repetidos).

## As provas (40 passam, 3 paradas)

- **Lugar novo falha:** `test_catraca_lugar_novo_falha_na_hora` (sozinho, e ao lado de um da lista). Conferido também no
  repositório de verdade, fora do teste: tirando a primeira linha da lista, a catraca diz "LUGAR NOVO ...
  atualizacao.py | (fora de função) | subprocess | import subprocess [atualizacao.py:114 ...]".
- **Lugar consertado falha pedindo para tirar da lista:** `test_catraca_lugar_consertado_pede_para_tirar_da_lista`.
  No repositório de verdade, com uma linha inventada a mais: "este lugar não é mais acusado: tire esta linha da lista e
  abaixe o teto: ...".
- **O teto:** `test_catraca_a_lista_nunca_passa_do_teto`. No de verdade, com `TETO` 45: "a lista congelada tem 46
  linhas e o TETO é 45: a lista só pode diminuir".
- **A chave não muda com código acima:** `test_catraca_a_chave_nao_muda_quando_se_escreve_codigo_acima`; e
  `test_catraca_o_mesmo_jeito_na_mesma_funcao_e_um_lugar_e_linha_repetida_na_lista_falha`.
- **Nomes proibidos no dono das DLLs:** `test_o_dono_das_dlls_nao_pode_o_windows_pelo_ctypes` (8 casos, um por nome:
  atributo, nome importado e atributo de variável; o mesmo texto em `core/windows.py` dá zero) e
  `test_o_dono_das_dlls_nao_pode_importar_o_wintypes_nem_pegar_por_getattr`.
- **Cada raiz entra no fechamento:** `test_raiz_do_hidden_import_entra_no_fechamento` (um módulo que só a `OCULTOS` põe
  é acusado; sem a raiz, escaparia), `test_raiz_do_motor_do_kraken_procura_na_pasta_dele`,
  `test_a_lista_dos_ocultos_montada_de_outro_jeito_e_falha` (7 jeitos) e `test_cada_raiz_de_verdade_entra_no_fechamento`
  (no repositório de verdade: as raízes lidas sem falha, e cada uma no fechamento).
- As provas da segunda volta continuam, três delas ajustadas ao mapa novo (ressalva 6).

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| a trava (repositório) | `lugares_do_repositorio` → `raizes_do_programa` + `lugares_da_trava` → `conferir_a_catraca` |
| as provas com arquivos de exemplo | `lugares_da_trava` / `falhas_da_trava` (a mesma conta, sem ler o disco) |
| as raízes | `raizes_do_programa` → `ocultos_do_empacotar` (árvore do `empacotar.py`) |
| o fechamento | `fechamento` → `_indice` (por pasta de busca) → `modulos_pedidos` |
| as capacidades | `_usos_na_arvore` (uma só; `capacidades_usadas` é ela a partir do texto) |
| a função onde mora | `leitura.funcao_em_volta`, a do porteiro |
| ler o código / a lista do git | `leitura.arvore` / `git.arquivos_do_git`, as do porteiro |

## A peça de fora usada (§11.12.6)

- `ast.literal_eval` (https://docs.python.org/3/library/ast.html#ast.literal_eval): avalia só literais (textos, listas,
  tuplas...); com qualquer outra coisa (uma chamada de função, um nome) levanta `ValueError`. É o que transforma
  "lista montada de outro jeito" em falha. Recebe o nó, não o texto.
- `ast.For.iter` e `ast.Name.ctx` (`Load`, `Store`, `Del`): o laço do `--hidden-import` e as escritas na `OCULTOS`.
- O resto do `ast`, como na primeira volta.

## O que não fechou (não ajeitei; para a gerente decidir)

1. **A pendência "a peça do Windows só lança programa da pasta do Windows" não é o que a peça faz hoje.**
   `_caminho_do_programa` (`core/windows.py`, linha 1078) só deixa o caminho como o Windows o completa, para comparar.
   A regra do rodar genérico, `_por_que_recusa` (linha 1195), faz o contrário: recusa o programa da pasta do Windows
   (linha 1245) e deixa rodar os de fora. Hoje quem usa esse caminho para programa de fora: o `vpk`
   (`empacotar.py:1559`) e o `gh` (`publicar_versao_kaique.py:476`), pelo `rodar_em_grupo`; e o `janela_de_prova.py:209`,
   que roda o próprio Python. Os três são scripts, fora do fechamento do programa. **Escolhi parar as duas pendências
   até `core/processos.py` existir**, porque só então os de fora têm para onde ir. Se a gerente quiser outro momento,
   é uma linha em cada pendência. Também fica para decidir se o `vpk` e o `gh` vão para a peça dos processos ("os
   nossos processos" hoje são OCR, Kraken, servidor de páginas e brasão).
2. **"Windows pelo ctypes" vale em todo arquivo, não só no dono das DLLs.** O pedido diz "dentro de
   `core/nativo_dll.py`". Fiz como capacidade com um dono (`core/windows.py`), que é uma regra num lugar só. Por isso
   ela também acusa fora do dono, onde o `import ctypes` já era acusado: são 13 das 46 chaves. Ela separa sozinha o
   ctypes do Windows (vai para `core/windows.py`) do ctypes das DLLs (vai para `core/nativo_dll.py`). Acusar só dentro
   do `core/nativo_dll.py` daria 33 chaves, mas seria uma regra só para um arquivo.
3. **A catraca não impede a troca de uma linha por outra.** Quem conserta um lugar e, na mesma mudança, põe um lugar
   novo na lista no lugar dele, mantém o tamanho e passa no `<= TETO`. Só a revisão da mudança pega. Com `<=`, também
   não é obrigatório abaixar o teto ao tirar linha (a mensagem pede, mas passa sem). Pôr `==` obrigaria a abaixar e
   fecharia essa folga; não pus porque o pedido diz `<=`.

## Ressalvas

1. O mesmo jeito repetido na mesma função é um lugar só. Um segundo `windll` dentro de uma função que já tem um não é
   lugar novo. Um `windll` numa função nova é.
2. Renomear uma função muda a chave dos lugares dela: a catraca acusa um novo e um que sumiu, e a lista precisa ser
   trocada (é a troca do ponto 3 acima, por motivo bom).
3. Atributo com nome do Windows é acusado venha de onde vier (`x.GetLastError`). Hoje não dá alarme falso no programa.
   Se um dia der, aparece como lugar novo, nunca calado.
4. O motor do Kraken é lido procurando na pasta dele. Se um dia ele importar `core.x`, a trava não segue (no motor o
   `core` não vai junto, e o import quebraria lá).
5. O que a trava não pega continua escrito na docstring do teste.
6. **Três provas da segunda volta, deste mesmo arquivo, mudaram** porque o mapa mudou:
   `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros` (o Windows agora pode `subprocess`),
   `test_o_mapa_dos_donos_so_usa_capacidades_que_existem` (dois donos do `subprocess`; a capacidade nova) e
   `test_acusa_cada_jeito_de_importar_e_de_usar` (dois achados a mais de "Windows pelo ctypes"). São do arquivo novo
   deste ramo, que ainda não entrou em lugar nenhum; nenhum teste de fora dele mudou.
7. Não disparei a rodada do GitHub (`[skip ci]`; o pedido manda rodar só este arquivo).

## Ideias para a Lista de espera

- Proteger a `LISTA_CONGELADA` e o `TETO` como os arquivos que só a gerente muda (a K17 do porteiro), para a troca de
  uma linha por outra (ponto 3 de "O que não fechou") não passar sem ela ver; e trocar o `<=` por `==`.

---

# Segunda volta — cabeçalho original (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23` (saiu de `obra-2026-10-26` em `c8531595`), worktree
`.claude/worktrees/atualizador-novo`. Pedido da gerente de 23/11/2026.

**Situação: a segunda volta (a última, D-815) está feita e esperando a gerente.** O teste continua em
`tests/test_trava_windows.py`, agora com o desenho dos donos do Fable. A trava acusa **34 lugares** e está marcada
`xfail(strict=True)`. As 14 provas passam, e a pendência do `CDLL` fica parada. A primeira volta, mais abaixo, fica como
histórico.

# Segunda volta (D-815, recado da gerente com a resposta do Fable aos 7 pontos)

## O que mudou no teste

- **A pergunta é outra.** Antes era "este import é permitido?". Agora é "quem é o dono desta capacidade?". O mapa está
  escrito uma vez, em `DONOS`, e as capacidades em `CAPACIDADES`.
  - `core/windows.py` pode `ctypes`, `winreg` e `os.startfile`.
  - `core/nativo_dll.py` pode `ctypes` e é o único que pode carregar DLL (`CDLL`, `cdll`, `PyDLL`, `pydll`).
  - `core/processos.py` pode `subprocess`.
  - "Rodar programa pelo `os`" (`os.system`, `os.popen`, `os.spawn*`, `os.exec*`) não tem dono.
  - O dono é acusado pelas capacidades que não são dele.
- **O que é programa:** o fechamento das importações a partir do `main.py` (`fechamento`). Não é lista nem a
  definição do porteiro. Hoje dá 121 arquivos, e nenhum deixou de ser lido.
  - **Importação dentro de função, de `if` e de `try`:** entra. O motivo é que o PyInstaller põe as quatro no `.exe`. A
    fonte é o PyInstaller 6.21.0 instalado, `PyInstaller/building/build_main.py`, linhas 60-77: `IMPORT_TYPES` e o
    texto "conditional: imported within an if-statement / delayed: imported within a function / optional: imported
    within a try-except-statement".
  - **`__import__("x")` e `importlib.import_module("x")` com o nome escrito por inteiro:** entram. O PyInstaller não os
    segue ("Analysis can detect nothing", https://pyinstaller.org/en/stable/when-things-go-wrong.html), mas o programa
    os carrega quando roda. O nome numa variável não se segue.
  - **Pacotes de cima** (`a/__init__.py` ao importar `a.b`) e **o `x` de `from a import x`** entram. O relativo vira
    absoluto. O que não é do repositório não entra. Ciclo não trava.
- **`CDLL`:** a trava só diz quem pode chamá-lo. O teste de execução ("todo caminho carregado está sob `core/nativo/`")
  está escrito como pendência, `test_pendencia_o_dono_das_dlls_so_carrega_dll_de_core_nativo`.
  - Ele fica parado enquanto `core/nativo_dll.py` não existe.
  - Ele falha no dia em que a peça existir sem a prova escrita.
  - A peça não foi inventada.
- **Marca:** `@pytest.mark.xfail(strict=True, reason="D-830: lista de trabalho do atualizador novo")`, só na trava.

## A nova contagem: 34 lugares

**(a1) Atualizador e testes à distância (10).** É a lista de trabalho do atualizador novo.
- `atualizacao.py`: 114 (`subprocess`), 432, 433, 750, 759 (`ctypes`), 1194, 1279 (`winreg`).
- `core/_testes_a_distancia_windows.py`: 32, 36 (`ctypes`), 34 (`subprocess`).

**(a2) Windows de verdade em outras partes (6).** Nada mudado nelas.
- `core/nucleos.py:44`: `ctypes`. A linha 78 usa o `kernel32` para ler a memória livre.
- `core/ocr_comum.py:209`: `ctypes`. A linha 211 usa `WinDLL kernel32` e o `SetDllDirectoryW`.
- `historico.py:7`: `subprocess`, para o `explorer /select`.
- `historico.py:199` e `:212`: `os.startfile`, para abrir a pasta e para imprimir.
- `ui/brasao_girando.py:223`: `ctypes`. Usa o `OpenProcess` para saber se o programa continua aberto.

**(b) DLL nossa (12).**
- Os `import ctypes`, mesmo os que só pegam os tipos: `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`,
  `core/desentortar_scantailor.py:69`, `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`,
  `core/gravura_scantailor.py:47`, `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`,
  `core/preto_e_branco_scantailor.py:60` e `core/st_ferramentas.py:43`.
- Os dois `CDLL`: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.

**(b) Processo nosso (5).**
- `core/ocr_comum.py:39`
- `core/ocr_kraken.py:89`
- `core/ocr_tesseract.py:87`
- `core/paginas_em_outro_processo.py:64`
- `ui/tela_de_carregamento.py:38`

**O próprio dono do Windows (1).** `core/windows.py:91`: `subprocess`. Ver o ponto 1 de "O que não fecha".

Conta: 10 + 6 + 12 + 5 + 1 = 34.

## O que saiu do escopo pela definição nova, e por quê

Saíram 31 lugares da primeira volta. Os arquivos onde eles estão não são importados a partir do `main.py`, então não
vão no `.exe`.
- `avaliar.py`: 3 lugares (26, 31 e 1655), a régua dos filtros. São a Área de Trabalho e o `python -c`.
- `teste_velocidade.py`: 17 lugares, o PowerShell, o registro e o `kernel32`.
- `compilar_detector_gravura.py`, `compilar_st_ferramentas.py`, `empacotar.py`, `empacotar_teste_velocidade.py` e
  `montar_motor_kraken.py`: os scripts de montar.
- `gerar_prints.py` e `teste_completo.py`.
- `conferencia.py` e `publicar_versao_kaique.py`.
- `teste_bateria.py` e `teste_robustez.py`.

Fora do fechamento há 45 arquivos que o porteiro conta como programa. Eles estão na lista `fora` da conferência que
rodei: os scripts da raiz, `motor_kraken/servidor_kraken.py` e três telas que nada importa (`ui/tela_opcoes.py`,
`ui/widgets/folhear_pdf.py`, `ui/widgets/trilha_ferramentas.py`). Nada entrou no fechamento que o porteiro não contasse
como programa.

## O que não fecha no desenho (não ajeitei: implementei ao pé da letra e deixo para decidir)

1. **O dono do Windows precisa rodar programas do Windows** (`schtasks`, PowerShell, `icacls`: `core/windows.py`, linhas
   1285, 1487 e 1662), mas o mapa não lhe dá `subprocess`. Ao pé da letra, ele é acusado (`core/windows.py:91`). Há
   dois caminhos: ele ganha o `subprocess`, e aí são dois donos do `subprocess`; ou ele pede ao `core/processos.py` para
   rodar, e aí "processos" deixa de ser "os nossos processos". O mesmo vale para o `explorer /select` do `historico.py`.
2. **"Rodar programa pelo `os`" não tem dono no desenho.** Ao pé da letra, ficou proibido em todo lugar, até nos três
   donos. Tem prova: `test_rodar_programa_pelo_os_nao_tem_dono`. Hoje ninguém do programa usa.
3. **O dono das DLLs pode o `ctypes` inteiro.** Então ele poderia chamar o Windows (`windll`, `WinDLL`) sem ser
   acusado. O desenho não separa "ctypes para a DLL nossa" de "ctypes para o Windows", e a trava não separa.
4. **O `.exe` não é só o `main.py`.**
   - O motor do Kraken é um programa à parte (`motor_kraken/servidor_kraken.py`, montado por `montar_motor_kraken.py`)
     e vai para o Kaique. Ele fica fora do fechamento. Hoje não usa nenhuma capacidade, mas a trava não o vigia.
   - O `empacotar.py` também põe `--hidden-import` (`OCULTOS`). Hoje todos os módulos nossos dessa lista já estão no
     fechamento. Um módulo que entrasse só ali escaparia.
5. **O `SetDllDirectoryW` do `core/ocr_comum.py:211`** é do Windows pelo desenho, mas é um passo de "abrir o nosso
   processo". Quando o código for mudado, o `core/processos.py` terá de chamar o `core/windows.py` para isso. É
   coerente, mas fica escrito.

## As provas (14 passam, 1 parada, a trava `xfail`)

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **14 passed, 1 skipped, 1 xfailed.**

- `test_fechamento_dentro_acusa_e_fora_nao_acusa`: o mesmo `import ctypes` é acusado em `core/usa.py`, que o
  `main.py` importa, e não é acusado em `solto.py`, que ninguém importa.
- `test_fechamento_segue_funcao_if_try_relativo_from_e_texto`: a importação dentro de função, de `if`, de `try`, a
  relativa, o `from pacote import modulo`, o `import_module("x")` e o `pacote/__init__.py` entram.
- `test_fechamento_aguenta_ciclo_e_ignora_o_que_nao_e_do_repositorio` e
  `test_fechamento_que_nao_le_e_falha_nunca_passou` (arquivo que não abre, código ilegível, falta do `main.py`).
- `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros`:
  - o Windows com `ctypes`, `winreg` e `startfile` não é acusado, e com `subprocess` e `CDLL` é;
  - as DLLs com `CDLL` não são acusadas, e com `subprocess` são;
  - os processos com `subprocess` não são acusados, e com `ctypes` são.
- `test_ctypes_so_para_os_tipos_tambem_e_acusado_fora_do_dono`: o `.ctypes` do numpy não é acusado à parte.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: 17 achados, cada um com a capacidade certa.
- `test_rodar_programa_pelo_os_nao_tem_dono`, `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido` (inclui
  `platform.system()` e `x.exec()`), `test_cada_modulo_proibido_e_acusado` (4 módulos) e
  `test_o_mapa_dos_donos_so_usa_capacidades_que_existem`.

## Ressalvas da segunda volta

- **A trava não pega:** `multiprocessing`, `asyncio.create_subprocess_*`, `sys.modules[...]`, o nome montado em
  pedaços, `nt`/`posix`, a importação com o nome numa variável, e o que o `.exe` leva sem o `main.py` importar (ponto 4
  acima). Está escrito na docstring do teste.
- **O `xfail(strict=True)` deixa a rodada passar com a trava falhando.** Se algum lugar sair da lista, ela continua
  `xfail`. Só quando zerar ela vira "passou inesperado" e falha, pedindo para tirar a marca. Então lugar novo também não
  deixa a rodada vermelha. Isso é o efeito da marca pedida, não um defeito.
- **Não disparei a rodada do GitHub** (`[skip ci]`; o pedido manda rodar só este arquivo).

# Primeira volta (histórico; o desenho e a lista de lá foram trocados pela segunda volta)

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer". E a mensagem do Fable que o Samuel colou: "ela pode mandar escrever a primeira trava
  (o teste que diz 'só core/windows.py fala com o Windows'). Esse teste vai falhar hoje de propósito — a lista do que
  falha é a lista de trabalho do atualizador novo". Pela resposta do Fable, a trava é um "Teste de AST em `tests/`:
  `ctypes`, `subprocess`, `winreg`, `os.startfile` importados somente em `core/windows.py`. Binário, sem lista de
  exceções."
- **D-765 (17/11):** "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique [...]". Nenhuma linha do
  programa muda nesta tarefa.
- **D-791 / D-801 / D-802:** a lista de exceções do porteiro só ganha item com o "sim" dele. Esta tarefa não põe item
  nela.
- **D-605 (§11.8):** "nenhuma função nova [...] pode alterar o que já está escolhido e testado". Nenhum teste antigo foi
  mudado, e nenhum teste antigo quebra.
- **§11.12 (uma peça só):** a trava não pode virar uma segunda conferência da mesma regra ao lado da K01.
- **D-809:** nenhum comando que mude o `.git` inteiro. O teste só lê a lista do git (`git ls-files`), pela peça única
  do git.
- **D-793 / §11.11:** não abri outro agente.

## O que já está escolhido e testado aqui

- O porteiro (`regras_dos_agentes/porteiro.py`). A K01 procura a conversa com o Windows por palavras
  (`PALAVRAS_DO_WINDOWS`, PROTEGIDA "nao_some" em `protecao.py`). A definição de programa é `e_programa`, com
  `NAO_E_PROGRAMA` PROTEGIDA "igual". A peça única é `PECA_UNICA_DO_WINDOWS`.
- `tests/test_conferencias_*.py`: as provas do porteiro. Entre elas, `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`,
  que barra qualquer achado fora da lista "valendo". Esses arquivos estão em `porteiro_mudancas.PROTEGIDOS` (K17): só a
  gerente os muda.
- O juiz do GitHub (`juiz.py`) julga o ramo com o porteiro e a lista **da versão de teste**, não com os do ramo.

## A escolha: teste à parte, e não uma conferência dentro do porteiro

**Escolhi um teste à parte, `tests/test_trava_windows.py`. Quando for juntado, ele deve substituir a parte da K01 que
procura as mesmas coisas por palavras.** Os motivos:

1. **Pôr a regra dentro do porteiro quebraria um teste antigo.** A lista de exceções está "valendo". Uma conferência
   nova (K26, ou uma K01 que lê a estrutura) acharia os 62 lugares. Nenhum deles está na lista com essa conferência,
   então `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` passaria a falhar. Para ele voltar a passar, seria
   preciso pôr 62 itens na lista, o que exige o "sim" do Samuel (D-791) e foi proibido no pedido.
2. **O juiz do GitHub nem veria a conferência nova.** Ele usa o porteiro da versão de teste. Uma K26 feita neste ramo só
   valeria depois que a gerente a juntasse.
3. **Trocar a K01 por uma versão que lê a estrutura afrouxa a proteção.** Tirar linhas de `PALAVRAS_DO_WINDOWS` (o
   `winreg`, o `os.startfile`, o `windll`) é barrado por `protecao.py` ("nao_some") e pela K17. Não contornei. É mudança
   da gerente, com o "sim" do Samuel.
4. **Uma peça só, sem definição copiada.** O teste não tem definição própria de "programa" nem de "peça única". Ele
   importa `porteiro.e_programa` e `porteiro.PECA_UNICA_DO_WINDOWS`, lê o código com `leitura_do_codigo.arvore`, que é a
   mesma leitura do porteiro, e pega a lista dos arquivos com `conversa_com_o_git.arquivos_do_git`.
   **A sobreposição que existe hoje:** a K01 acusa por palavra `winreg`, `os.startfile`, `windll`/`WinDLL`/`CDLL` de DLL
   do Windows e o apelido da biblioteca. A trava acusa por estrutura o `import` de `ctypes`, `subprocess`, `winreg` e o
   uso de `startfile`. São duas conferências da mesma regra até a gerente decidir. Sugestão para quando juntar: a parte
   de imports, `winreg` e `startfile` da K01 sai, e fica a trava. As palavras do PowerShell, do `schtasks`, do `icacls`
   etc. continuam na K01 até virarem a segunda trava do Fable ("nenhum literal de string fora de `core/windows.py`
   contém `powershell`, `-Command` ou `.ps1`").

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF. Nenhuma linha do programa mudou, só um teste novo em `tests/`. O que muda é a rodada
do GitHub: **ela vai falhar enquanto houver lugar na lista**. Isso é de propósito (D-830), mas tem consequência. Veja as
ressalvas.

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| o teste da trava (repositório inteiro) | `falhas_do_repositorio` → `falhas_nos_arquivos` → `lugares_proibidos` |
| as provas com arquivo de exemplo | `falhas_nos_arquivos` → `lugares_proibidos` (a mesma conta, sem ler o disco) |
| o que é programa | `porteiro.e_programa` (`NAO_E_PROGRAMA`), o mesmo do porteiro |
| a peça única | `porteiro.PECA_UNICA_DO_WINDOWS` |
| ler o código | `leitura_do_codigo.arvore`, a mesma do porteiro (aceita a marca de UTF-8 e levanta `CodigoIlegivel`) |
| a lista dos arquivos | `conversa_com_o_git.arquivos_do_git` (`git ls-files`, só lê), o mesmo de `porteiro.achados_do_repositorio` |

## O que pode falhar, e o que a trava faz em cada caso

- **Arquivo do programa que não abre ou não é texto UTF-8:** vira falha `arquivo:0: não deu para ler`. Nunca passa.
- **Código que o Python 3.14 não consegue ler:** vira falha `arquivo:0: o código não pôde ser lido`.
- **O git não responde:** `GitFalhou` sobe e o teste falha com o motivo. Nunca passa calado.
- **Comentário ou docstring que fala de `ctypes`:** não conta. Não é árvore de código. Tem prova.
- **O `.ctypes` de uma imagem do numpy** (`imagem.ctypes.data_as`, usado para entregar a imagem à DLL do ScanTailor):
  não é o módulo. Não conta sozinho, mas o `import ctypes` do mesmo arquivo é acusado, então nada fica escondido. Tem
  prova. Na primeira versão da trava eu contava esse `.ctypes`. Ela deu 80 lugares, 18 deles esse alarme falso, e
  estreitei a regra: só conta o módulo pego dentro de outro módulo importado no arquivo (`windows.subprocess`).

## A peça de fora usada: o `ast` do Python (§11.12.6)

Fonte: https://docs.python.org/3/library/ast.html (Python 3.14).
- `ast.Import`: `names` é uma lista de `alias(name, asname)`, e `name` traz o nome com ponto (`ctypes.wintypes`).
- `ast.ImportFrom`: tem `module` (None em `from . import x`), `names` e `level` (0 = absoluto; 1 ou mais = relativo).
- `ast.Call`: `func` e `args`. `ast.Attribute`: `value` e `attr`. `ast.walk` passa por todos os nós e não segue ordem.
  Por isso o resultado é ordenado no fim.
- Comentário não vira nó. Docstring é um `ast.Constant` e só conta se estiver numa das formas acima, o que não acontece.
- `__import__` (https://docs.python.org/3/library/functions.html#import__) e `importlib.import_module`
  (https://docs.python.org/3/library/importlib.html) recebem o nome do módulo como texto. Só o texto escrito por inteiro
  é lido.
- `os.startfile` só existe no Windows (https://docs.python.org/3/library/os.html#os.startfile) e está em `os.__all__`
  lá. Por isso `from os import *` é acusado.

## A prova de que a trava funciona

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **1 failed, 11 passed**.
- **Falha hoje:** `test_so_core_windows_fala_com_o_windows` acusa 62 lugares (a lista abaixo).
- **Acusa fora da peça e não acusa dentro:** `test_acusa_import_ctypes_fora_da_peca_e_nao_acusa_dentro` usa um arquivo
  de exemplo com `import ctypes`. Em `atualizacao.py` e em `core/qualquer.py` ele é acusado. O mesmo texto em
  `core/windows.py` dá zero.
- `test_usa_a_definicao_de_programa_do_porteiro`: o que está em `tests/`, `relatorios/`, `regras_dos_agentes/` e `docs/`
  não é acusado. Pasta nova e `.pyw` são acusados.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: os 12 jeitos de importar ou usar, uma linha cada.
- `test_acusa_from_os_import_estrela_que_traz_o_startfile`, `test_o_ctypes_de_uma_imagem_do_numpy_...`,
  `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido`,
  `test_codigo_ilegivel_e_arquivo_que_nao_abre_sao_falha_nunca_passou` e `test_cada_modulo_proibido_e_acusado` (4
  módulos).
- O porteiro rodado no próprio `tests/test_trava_windows.py` dá zero achados. O arquivo não tem comando do git (K25) e
  todas as funções têm docstring (K12).
- Não mexi no porteiro, então `tests\test_conferencias_codigo.py` não precisou rodar.

## A lista do que falha hoje (62 lugares, arquivo:linha)

### (a) Conversa com o Windows de verdade

**(a1) O atualizador e os testes à distância: a lista de trabalho do atualizador novo (10)**
- `atualizacao.py:114` `import subprocess`. Usado no `Update.exe apply` (L671), no PowerShell (L965), nos comandos do
  Windows de `_rodar` (L789) e no teste rápido, que roda o nosso próprio exe (L632).
- `atualizacao.py:432`, `:433` `ctypes`/`wintypes`: `GetNamedSecurityInfoW`, o dono do arquivo.
- `atualizacao.py:750` `ctypes`: `CreateMutexW`, a marca de "programa aberto".
- `atualizacao.py:759` `ctypes`: `OpenMutexW`, para conferir a marca.
- `atualizacao.py:1194` `winreg`: o Visual C++ está instalado?
- `atualizacao.py:1279` `winreg`: a chave do instalador antigo (Inno).
- `core/_testes_a_distancia_windows.py:32`, `:34`, `:36`: `ShellExecuteExW` "runas", PowerShell e `schtasks`.

**(a2) Windows de verdade em outras partes. Não é do atualizador; estão na lista de exceções como "depois da entrega"
(D-800/D-802) (24)**
- `avaliar.py:26`, `:1655`: `SHGetFolderPathW`, onde fica a Área de Trabalho (régua dos filtros).
- `core/nucleos.py:44`: `GlobalMemoryStatusEx`, a memória livre.
- `historico.py:7`, `:199`, `:212`: abrir a pasta no Explorer (`explorer /select`, `os.startfile`) e imprimir
  (`os.startfile(..., "print")`).
- `teste_velocidade.py:75` (PowerShell), `:362`, `:432` (`winreg`: placa de vídeo, processador), `:476`, `:641`,
  `:642`, `:1676`, `:1736`, `:1737`, `:1755`, `:1756`, `:1903`, `:1904`, `:1918`, `:1919`, `:2230`, `:2250`
  (`kernel32`/`user32`/`psapi`: memória, não dormir, janela preta, console).
- `ui/brasao_girando.py:223`: `OpenProcess`/`WaitForSingleObject`, o programa continua aberto?

### (b) Não é o Windows: DLL nossa, processo nosso, ferramenta de montar (27)

**DLL nossa do ScanTailor (`core/nativo/st_ferramentas.dll`, `st_gravura.dll`) (10).** Sugestão: uma peça única das
nossas DLLs. Hoje duas carregam a DLL, `core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`, cada uma com o
seu `CDLL` e o seu `add_dll_directory`. As outras só usam os tipos do `ctypes`.
- `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`, `core/desentortar_scantailor.py:69`,
  `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`, `core/gravura_scantailor.py:47`,
  `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`, `core/preto_e_branco_scantailor.py:60`,
  `core/st_ferramentas.py:43`.

**Processo nosso (5).** Sugestão: uma peça única para abrir os nossos processos. `core/ocr_comum.abrir_processo` já
faz isso para os OCRs.
- `core/ocr_comum.py:39`: `abrir_processo`, o `Popen` dos OCRs.
- `core/ocr_kraken.py:89`: o motor do Kraken, com `PIPE` e `TimeoutExpired`.
- `core/ocr_tesseract.py:87`: `tesseract.exe --version` e `_matar`.
- `core/paginas_em_outro_processo.py:64`: o servidor de páginas.
- `ui/tela_de_carregamento.py:38`: o brasão em outro processo (`abrir=subprocess.Popen`).

**Ferramentas de montar, publicar e testar, que ficam na raiz e não vão no programa do Kaique (8).** Sugestão:
decidir se esses scripts são "programa" para a trava. Hoje são, pela definição do porteiro.
- `compilar_detector_gravura.py:42`, `compilar_st_ferramentas.py:44`: o `cmake`.
- `empacotar.py:115`: o PyInstaller e o compilador do Inno.
- `empacotar_teste_velocidade.py:68`: o PyInstaller.
- `montar_motor_kraken.py:98`: o `python`/`pip` do motor.
- `gerar_prints.py:15`: roda a si mesmo.
- `teste_completo.py:326`: roda `teste_robustez_completo.py`.
- `avaliar.py:31`: roda `python -c` para medir a abertura.

**Import que não conversa com nada (4).** Sugestão: tirar o import, quando a D-765 deixar mexer.
- `conferencia.py:71`: só `subprocess.list2cmdline`, que monta um texto.
- `publicar_versao_kaique.py:70`: só o tipo `CompletedProcess`. O `gh` roda por outra peça.
- `teste_bateria.py:15`, `teste_robustez.py:12`: `import ctypes` sobrando, que nem é usado. A docstring diz que trocou
  para o `psutil`.

### (c) Dúvida (1)

- `core/ocr_comum.py:209`: chama o Windows de verdade (`kernel32.SetDllDirectoryW`), mas só para o OCR que roda à
  parte não herdar a pasta de DLLs do programa. É Windows, então iria para `core/windows.py`. Mas faz parte de "abrir um
  processo nosso", então iria para a peça dos processos. Precisa de decisão de desenho.

**Conta, conferida com a saída do teste linha por linha:** 10 (a1) + 24 (a2: 2 + 1 + 3 + 17 + 1) + 27 (b: 10 + 5 + 8 +
4) + 1 (c) = 62. Nenhuma linha se repete. O `core/ocr_comum.py` tem duas linhas: a 39 está em (b) e a 209 em (c).

## A mesma lista separada pela sugestão do Fable (recado da gerente, 23/11; ainda não é decisão do Livro)

A sugestão:
- **Proibido fora de `core/windows.py`:** `ctypes.windll`, `ctypes.WinDLL`, `wintypes`, `winreg`, `os.startfile`.
- **Permitido em qualquer lugar:** `ctypes.CDLL` carregando as DLLs de `core/nativo/`.
- **`subprocess`:** só numa lista fixa de arquivos: `core/windows.py`, o servidor de páginas, o lançador do Kraken e
  `empacotar.py`.

Não mudei a trava: ela continua como o pedido manda. Abaixo está só a separação. Conferi os lugares de uso lendo a
árvore de cada arquivo, não só a linha do `import`.

### Proibido, fora do atualizador (grupo à parte: não muda nada nelas)

- `core/nucleos.py:78`: `ctypes.windll.kernel32.GlobalMemoryStatusEx`, que lê a memória livre para decidir quantas
  páginas trabalham ao mesmo tempo. O import está na linha 44.
- `core/ocr_comum.py:211`: `ctypes.WinDLL("kernel32")`, `GetDllDirectoryW`/`SetDllDirectoryW`. Por um instante, tira a
  pasta de DLLs do programa para o OCR que roda à parte não herdá-la. O import está na linha 209.
- `historico.py:199`: `os.startfile(pasta)`, que abre a pasta no Explorer.
- `historico.py:212`: `os.startfile(caminho, "print")`, que manda imprimir pelo Windows.
- `avaliar.py:1655` e `:1659`: `windll`/`wintypes` e `SHGetFolderPathW`, que pergunta onde fica a Área de Trabalho
  (régua dos filtros). O `import ctypes` está na linha 26.
- `ui/brasao_girando.py:225`: `ctypes.windll.kernel32` `OpenProcess`/`WaitForSingleObject`, que confere se o programa
  continua aberto enquanto o brasão gira.
- `teste_velocidade.py`, 17 lugares de import e o uso deles:
  - `winreg` nas linhas 362 e 432 (a placa de vídeo e o processador);
  - `windll` nas linhas 479, 1678 e 2233 (a memória, "não dormir" e a lista de processos do console);
  - `WinDLL`/`wintypes` nas linhas 642 a 664, 1737 a 1759, 1904 a 1922 e 2250 a 2254 (a memória do processo, a janela
    preta e a classe da janela).

### Proibido, no atualizador e nos testes à distância (a lista de trabalho do atualizador novo)

- `atualizacao.py`:
  - `wintypes` nas linhas 433, 438 e 441;
  - `windll` nas linhas 435, 752 e 761;
  - `winreg` nas linhas 1194 e 1279.
- `core/_testes_a_distancia_windows.py`: `wintypes` nas linhas 36 e 63 a 77; `windll` nas linhas 94 a 99.

### Permitido pela sugestão

- `ctypes.CDLL` das DLLs nossas: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.
- `subprocess` nos arquivos da lista: `core/paginas_em_outro_processo.py:64`, `empacotar.py:115` e, se "o lançador do
  Kraken" for `core/ocr_kraken.py`, o `:89` (ver "o que cai fora" abaixo).

### `subprocess` fora da lista de arquivos: falharia pela sugestão (16)

- **Atualizador e testes à distância:** `atualizacao.py:114` e `core/_testes_a_distancia_windows.py:34`.
- **Outras partes do programa:**
  - `core/ocr_comum.py:39`: o `abrir_processo` dos OCRs, por onde o Kraken abre de verdade;
  - `core/ocr_tesseract.py:87`: o `tesseract.exe`;
  - `historico.py:7`: o `explorer /select`;
  - `ui/tela_de_carregamento.py:38`: o brasão;
  - `teste_velocidade.py:75`: o PowerShell.
- **Scripts de apoio:**
  - `avaliar.py:31`;
  - `compilar_detector_gravura.py:42` e `compilar_st_ferramentas.py:44`;
  - `empacotar_teste_velocidade.py:68`;
  - `montar_motor_kraken.py:98`;
  - `gerar_prints.py:15`;
  - `teste_completo.py:326`;
  - `conferencia.py:71`: só `list2cmdline`;
  - `publicar_versao_kaique.py:70`: só o tipo.

### O que cai fora da sugestão (ela não diz o que fazer)

1. **"O lançador do Kraken" não é um arquivo só.** O `Popen` de verdade está em `core/ocr_comum.py`
   (`abrir_processo`, L185-219), que também abre o `tesseract.exe`. O `core/ocr_kraken.py` usa o `subprocess` para
   `PIPE`, `TimeoutExpired` e o tipo. Pela sugestão ao pé da letra, um dos dois falha, ou os dois entram na lista.
2. **O `import ctypes` só para os tipos** (`c_double`, `c_void_p`, `create_string_buffer`) nos 8 arquivos
   `core/*_scantailor.py` que chamam a DLL nossa sem carregá-la: caixas, cores, desentortar, dividir, endireitar, luz,
   pontinhos e preto e branco. A sugestão não proíbe nem permite. Pela letra dela, passam, porque não usam `windll`,
   `WinDLL` nem `wintypes`.
3. **`import ctypes` sobrando**, sem uso nenhum: `teste_bateria.py:15` e `teste_robustez.py:12`. Pela letra, passam.
4. **"CDLL carregando as DLLs de `core/nativo/`" não se confere lendo o código.** O caminho vem de uma variável
   (`ctypes.CDLL(str(self.caminho))`). Uma trava que lê a estrutura não sabe se o caminho é de `core/nativo/`. Ou ela
   aceita todo `CDLL`, e aí `CDLL("kernel32")` passa, ou só aceita o `CDLL` nos dois arquivos, o que já é uma lista de
   arquivos.
5. **Jeitos de falar com o sistema que a sugestão não lista:** `ctypes.oledll`, `ctypes.cdll.kernel32` e
   `ctypes.CDLL("kernel32")` (a K01 pega por palavra), além de `os.system`, `os.popen` e `os.spawn*`.
6. **A lista fixa de arquivos para o `subprocess`** é uma lista de lugares permitidos. Isso não bate com o "binário,
   sem lista de exceções" da primeira mensagem do Fable. Ela pode ser lida como "as peças únicas de cada coisa", desde
   que cada arquivo da lista tenha um papel escrito. Isso é decisão, não minha.
7. **Os scripts de montar** (`compilar_*`, `montar_motor_kraken.py`, `empacotar_teste_velocidade.py`) rodam `cmake`,
   PyInstaller e `pip`. A sugestão só põe o `empacotar.py` na lista. Pela letra, os outros falham.

## Perguntas para o Samuel

(A gerente adapta para a Central. Não há print, porque nada na tela muda: é uma conferência do código.)

**1. Os pedaços do programa que conversam com outras coisas que não são o Windows (grupo b).**
- *Do que se trata:* a trava nova diz "só um arquivo do programa pode rodar outro programa ou carregar uma DLL". Ela
  acusa 27 lugares que não conversam com o Windows: as ferramentas do ScanTailor que viraram DLL nossa, o leitor de
  texto (OCR) e o servidor de páginas, que rodam à parte, e os scripts de montar o instalador.
- *O que acontece hoje:* cada um faz isso por conta própria. Isso não é defeito que o Kaique vê; é jeito de escrever o
  código.
- *O que você escolhe:*
  - (1) Tudo vai para o mesmo arquivo do Windows. É simples, mas mistura as ferramentas do ScanTailor com o Windows.
  - (2) **Sugestão do implementador:** um arquivo só para as DLLs nossas e um arquivo só para os programas nossos que
    rodam à parte. A trava diz qual dos três arquivos pode fazer cada coisa e continua sem lista de exceções. Os
    scripts de montar o instalador ficam de fora da trava, porque não vão para o Kaique.
  - (3) Só comentário.
- *O que muda no que já funciona:* nada agora. A mudança só aconteceria depois da entrega ao Kaique (D-765), e o
  programa faria o mesmo de antes.

## Ressalvas

- **A rodada do GitHub vai falhar por causa deste teste**, de propósito (D-830). Enquanto ele estiver no ramo, a
  rodada inteira sai vermelha, e uma falha nova de outro teste fica misturada com esta. Sugestão técnica para a
  gerente: na hora de juntar, decidir se ele entra como `xfail(strict=True)` até o atualizador novo ficar pronto ou se
  fica falhando. Não fiz isso por conta própria: o pedido diz "vai falhar hoje de propósito".
- **Não disparei a rodada do GitHub.** O pedido manda rodar só o arquivo novo e fazer commit com `[skip ci]`. Por
  isso não há número de rodada.
- **O que a trava não pega:** `os.system`, `os.popen`, `os.spawn*`, `os.exec*`, `multiprocessing`,
  `asyncio.create_subprocess_*`, `sys.modules["ctypes"]`, o nome montado em pedaços (`__import__("ct" + "ypes")`) e um
  módulo nosso que guarda o `subprocess` com outro nome e o devolve por uma função. Está escrito na docstring do teste.
  A K01 pega `os.system` e `os.popen` por palavra.
- **A sobreposição com a K01** continua até a gerente juntar e decidir. Ver "A escolha".
- Rodei o teste no PC. Ele só lê arquivos. Nenhuma janela abriu e nada do Windows foi mexido.

## Ideias para a Lista de espera

- Duas peças carregam a mesma DLL do ScanTailor (`core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`), cada
  uma com o seu `CDLL` e o seu `add_dll_directory`. É uma regra em dois lugares (§11.12).
- A trava poderia pegar também `os.system`, `os.popen` e `os.spawn*`, para a regra "rodar outro programa" ficar inteira.
  Não estava no pedido do Fable.

## Bugs para a Lista de bugs

- 23/11/2026, `teste_bateria.py:15` e `teste_robustez.py:12`: `import ctypes` que não é usado (sobrou da troca para o
  `psutil`). Não impede nada.

## Commits

- `cdbaec25`: `tests/test_trava_windows.py` e este ONDE-PAREI, com push no ramo `atualizador-novo-2026-11-23`.
