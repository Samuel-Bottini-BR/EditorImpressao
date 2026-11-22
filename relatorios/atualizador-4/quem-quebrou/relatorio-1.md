# Quem tentou quebrar: os 4 consertos do atualizador (relatório 1)

Verificador, 21/11/2026. Trabalho conferido: ramo `atualizador-4-consertos-2026-11-21` (código em `75cfa928`/`dd06e85f`, ponta
`2d5d912b`), contra a base `4a775ba8`. Não abri janela na tela do Samuel, não pedi licença ao Windows, não mudei o código do
programa. As provas foram feitas em duas cópias minhas no rascunho (o código de antes e uma cópia para desligar proteções),
tiradas no fim.

## Veredito

**NÃO ESTÁ PRONTO.** Os 4 consertos fazem o que prometem no caminho normal, e as provas automáticas pegam quase todas as
proteções. Mas achei três falhas médias que o escritor não pensou, todas do mesmo tipo: quando alguma coisa dá errada ou
muda com o motor do Kraken ou com o Visual C++, o programa fica dizendo o que não é, ou a atualização para de chegar, sem
avisar ninguém. Nenhuma faz o Kaique perder o programa ou o trabalho (nenhuma grave). As três são raras e têm conserto
pequeno.

Máquina ou olho: tudo aqui é **máquina** (leitura do código, testes, cópias com proteção desligada, scripts). Nada foi
conferido à vista; a pergunta do Windows, a troca e o motor de verdade ficam para a prova à vista da gerente (D-767).

## As três falhas médias

### Médio 1. O arquivo do motor estragado de um certo jeito trava a atualização em silêncio

- **O que é.** O ajudante põe o motor do Kraken no lugar a partir do arquivo que veio no instalador. Se esse arquivo
  estiver estragado de um jeito (o pedaço comprimido de um arquivo inválido), o Python dá um erro que o conserto não
  espera (`zlib.error`; o `EOFError` de arquivo cortado também não está na lista). O erro escapa: a pasta provisória
  `motor-kraken\.chegando-1` fica no disco pela metade, o registro não diz nada do motor, e o ajudante desiste antes de
  procurar a versão nova (o registro diz "não consegui procurar a versão nova", que engana).
- **Como acontece.** Instalar com um `instalar\motor-kraken-1.zip` estragado (disco, cópia). Toda abertura: o ajudante
  apaga o provisório, abre o arquivo de novo até o pedaço estragado (minutos de disco) e para. Nenhuma versão nova chega,
  e nada avisa.
- **Provado.** Script `zip_estragado.py` (na cópia, sem mudar o código): com a soma errada o conserto se sai bem
  (devolve "não", apaga o provisório, registra); com o fluxo comprimido inválido sai "LEVANTOU zlib error ... invalid
  block type", "sobrou o provisorio: True", "registro: (nada)".
- **Onde.** `atualizacao.py`, `garantir_o_motor`: `except (OSError, zipfile.BadZipFile, ValueError)`. A docstring diz
  "Qualquer erro: apaga o .chegando, registra e devolve False", e isso não é verdade. E `rodar_ao_ligar` chama
  `garantir_o_motor` antes de procurar, sem separar o erro do motor da procura.
- **Gravidade.** Médio: a atualização não chega. Raro (o instalador tem as próprias conferências), mas foi pedido
  conferir este caso.

### Médio 2. Sem o motor no lugar, a tela diz "versão nova" e cada abertura tenta trocar, sem fim

- **O que é.** O conserto 4 diz: sem o motor no lugar, não troca, "fica pendente e tenta na próxima vez". Mas
  "pendente" é o mesmo estado que diz à tela "chegou uma versão nova, esperando você reiniciar". Então o Kaique vê o aviso
  "Chegou uma versão nova... Reiniciar agora / Depois". Se clica "Reiniciar agora", o programa fecha, o ajudante de novo
  não troca, e o programa volta na mesma versão, com o mesmo aviso. Se clica "Depois", toda abertura seguinte mostra a
  janelinha "Atualizando o programa, espere um pouco...", sai, não troca e reabre. Isso se repete a cada abertura,
  enquanto o motor não estiver no lugar, e nada diz o porquê.
- **Como acontece.** O caso mais provável: o notebook com menos de uns 1,7 GB livres (o motor aberto, ~1,2 GB, mais a
  folga de 500 MB) na primeira vez que o ajudante roda. Também: um instalador feito sem o arquivo do motor, ou um arquivo
  do motor que o antivírus tirou depois da primeira atualização (aí o arquivo do instalador já não existe, D-790 fica para
  depois).
- **Provado.** Teste temporário na minha cópia (apagado depois), com as peças de teste que já existem: com o programa
  fechado e o motor fora do lugar, `procurar_e_preparar` devolve "pendente"; a tela (`o_que_avisar`) devolve
  `('versao-nova', '1.2.0')`; a abertura seguinte (`trocar_antes_de_abrir`) devolve True (sai para trocar, com a
  janelinha).
- **Antes deste trabalho** a versão entrava, falhava no teste rápido, voltava e mostrava a frase da D-719 ("A atualização
  não deu certo... Avise o Samuel"). Agora não volta nada, mas fica o aviso falso sem fim. É falha nova deste trabalho.
- **Onde.** `atualizacao.py`, `procurar_e_preparar` (o bloco novo `if not (motor_no_lugar or motor_esta_no_lugar)()` grava
  `{"fase": "pendente"}`), junto com `situacao` e `trocar_antes_de_abrir`, que leem "pendente" como "versão nova
  esperando".
- **Gravidade.** Médio: o programa diz o que não é ("chegou uma versão nova") e a versão não entra.

### Médio 3. Depois do "Sim", a pergunta do Windows pode voltar sem precisar

- **O que é.** "Preparado" agora é lido do Windows a cada abertura, e qualquer coisa que falte faz a pergunta "Deseja
  permitir...?" voltar. Um dos quatro itens é "o Visual C++ do pacote está instalado". Quando uma versão nova traz um
  Visual C++ mais novo (o empacotador baixa o mais recente da Microsoft), quem o instala é o ajudante, na abertura
  seguinte, por trás. Mas a leitura da janela leva poucos segundos e o Visual C++ leva de meio minuto a minutos: a
  leitura vê "falta o Visual C++" e a pergunta do Windows aparece para o Kaique, que já tinha dito "Sim". Se ele diz "Sim",
  duas instalações do Visual C++ correm juntas (uma delas falha). Se diz "Não", na próxima abertura some.
- **Mesmo efeito** quando a leitura do Windows falha ("não deu para saber" conta como falta): por exemplo, um antivírus
  que barra o PowerShell; aí a pergunta volta toda vez e o "Sim" não resolve.
- **Contra o que ele decidiu.** D-741: "Depois do 'Sim', nunca mais aparece (as atualizações seguem sem perguntar)". D-735:
  "Nas atualizações seguintes, nenhuma pergunta."
- **Onde.** `atualizacao.py`, `o_que_falta_no_computador` (item 3, `visual_c_que_falta`, lido na janela do Kaique) e a
  ordem: depois de uma troca, `conferir_e_refazer_o_ajudante` não roda `preparar_o_computador`; o Visual C++ novo só entra
  quando o ajudante roda de novo, ao mesmo tempo que a leitura. Lido no código; não dá para provar sem a troca de verdade.
- **Gravidade.** Médio (contra uma decisão dele), raro (só quando uma versão traz um Visual C++ mais novo, ou quando o
  Windows não deixa ler).

## Os pontos que o escritor levantou

- **(a) A soma do arquivo do motor contra o `motor-exigido.json` saiu.** Baixo nesta entrega. O arquivo do motor e o
  `motor-exigido.json` vêm do mesmo instalador, na mesma pasta de Arquivos de Programas, que só o administrador grava: quem
  consegue trocar um consegue trocar o outro e o próprio programa. A montagem já confere a soma assinada ao pôr o arquivo
  no instalador (`empacotar.preparar_saida`). Estrago no disco a soma interna do zip pega quase sempre (o buraco que sobra é
  o médio 1). Mas ficaram dois comentários que dizem o contrário: `core/ocr_kraken.conferir_motor` ("a conferência forte é
  na chegada do motor (a soma assinada do arquivo do motor...)") e `empacotar.NOME_DO_MOTOR_EXIGIDO` ("Quem le e o
  ajudante (passo 3)"). Pela regra de não deixar comentário falso, precisam ser corrigidos ou a conferência feita.
- **(b) O XML do ajudante e as aspas do PowerShell escritos duas vezes.** Já existiam antes (a base `4a775ba8` já tinha
  `core.windows.xml_da_tarefa_do_sistema` e `aspas_do_powershell` ao lado das cópias de `atualizacao.py`). Este trabalho
  não criou nem aumentou: os usos de `_aspas_do_powershell` caíram de 18 para 14. Mas criou uma duplicação nova parecida:
  `o_que_falta_no_computador` escreveu a própria conferência "a tarefa lida é a do programa?" (comando, argumentos, quem
  roda), quando a peça única já tem `core.windows.problemas_da_tarefa_criada`, que confere também a licença "quem pode
  mandar rodar". Hoje as duas comparam o caminho de jeitos diferentes (a peça, texto igual; a nova, caminho normalizado).
  Baixo no efeito, mas é conta duplicada (§11.12); ver baixo 3.
- **(c) A volta com o lançar antigo do Update.exe** (`_aplicar_pacote_quando_sair`, linhas 695-700; `update_exe`, 494-496).
  Não mudou, está na lista de exceções do porteiro desde 19/11 e funcionou na etapa 5 (o Update.exe não é o PowerShell; a
  bandeira que matava o PowerShell não o mata). Baixo e fora destes 4 consertos. Só lembro que a volta também dá como feita
  sem conferir (o registro anota "voltando" logo depois de lançar).
- **(d) O tempo da troca de 300 para 900 s.** Razoável e coberto por teste. O custo: se o ajudante travar, a janelinha do
  "Depois" (por cima de tudo, sem botão) pode ficar até 18 minutos na tela (900 + 60 + 120 s); antes eram 8. Baixo.
- **(e) A conta comum consegue ler as tarefas do sistema?** Não deu para provar sem licença: neste PC as duas tarefas não
  existem (li com a peça, sem licença: "existe=False" nas duas; o registro do Agendador também não tem a pasta). Pelo
  código, as duas tarefas dão leitura às contas comuns ("GRGX" para "AU"), então deve funcionar. Se não funcionar, o Windows
  pode responder "não existe" em vez de "sem licença", e a pergunta voltaria a cada abertura, para sempre, mesmo depois do
  "Sim". A prova à vista confere (passo 2 abaixo).

## Pedidos específicos da gerente

- **O motor nunca fica com o nome final pela metade:** confirmado no código e por teste (abre no provisório, confere, só
  então renomeia). Desligar a proteção (abrir direto no nome final) é acusado por teste.
- **Faltar espaço:** confere antes; não começa; registra. Mas leva ao médio 2.
- **A extração parar no meio** (desligar, travar): sobra só o provisório, que a vez seguinte apaga. Certo.
- **Arquivo do instalador estragado:** soma errada, certo; fluxo comprimido inválido, médio 1.
- **A troca sem motor no lugar não acontece:** confirmado (teste e mutação). Mas ver o médio 2.
- **A senha (opção B):** com a senha digitada, só uma frase fixa vai ao registro; a senha não é passada a função nenhuma,
  não vai a arquivo, registro, linha de comando nem à pergunta do Windows (procurei no código; o fio de trás leva só o
  número da janela). Ligar os testes à distância com a senha é acusado por teste (mutação M13). Lembrete, fora desta
  entrega: o botão das Configurações (e a frase da janela "pode pôr depois, em Configurações") continua ligando os testes
  pelo pedido antigo, que ainda lê o "Não" como "Sim".
- **"Reiniciar agora", "Depois", "Não" e "Sim":** todos os caminhos passam pela mesma peça e pela mesma leitura do Windows;
  conferido no código e nos testes. O erro no meio da preparação faz a pergunta voltar (D-749), lido do Windows.
- **A lista de exceções do porteiro:** só saíram itens: 175 para 168, 7 saídas, 0 entradas (comparei as duas listas item
  por item).
- **A rodada do GitHub 44975834257:** testou este ramo, no commit `70ceaf61` (todas as partes dizem "codigo trocado pelo de
  atualizador-4-consertos-2026-11-21 (70ceaf61...)"). O código de `70ceaf61` é igual ao da ponta `2d5d912b` e ao de
  `dd06e85f` (só o ONDE-PAREI muda). Resultado: sucesso na 2ª tentativa; a 1ª falhou só na parte 1 (o escritor diz que foi
  o Qt quebrando no `test_promessas.py`; não consegui abrir o registro da 1ª tentativa para confirmar). Os arquivos destes
  consertos rodaram lá: `test_atualizador_4.py` 34, `test_decisoes_ajudante_da_atualizacao.py` 37,
  `test_decisoes_preparo_d749.py` 9, `test_decisoes_testes_a_distancia.py` 13, `test_windows_peca.py` 71,
  `test_conferencias_excecoes.py` 14, todos passando. O ONDE-PAREI diz que a rodada testou `dd06e85f`; foi `70ceaf61`
  (mesmo código).

## Testes de reversão e mutações

- **No código de antes** (`4a775ba8`, cópia minha): os 34 testes novos falham, e os 16 testes antigos mudados também (11 +
  3 + 2); os 26 + 2 + 11 testes não mudados desses arquivos passam lá, como devem. Ressalva: quase todos os 34 novos falham
  porque a função nova não existe no código de antes ("has no attribute", "missing argument"), não porque viram o defeito.
  Isso prova pouco. A prova forte são as mutações abaixo.
- **Mutações** (desliguei cada proteção numa cópia e rodei os 4 arquivos, um por vez): 29 proteções; 24 acusadas por algum
  teste. **5 não acusadas:**
  - M05: não comparar os argumentos e a conta do ajudante (um ajudante que roda outra coisa, ou como outra conta, passaria
    por "preparado");
  - M06: não conferir a tarefa "desfazer";
  - M07: não conferir o Visual C++;
  - M08: não conferir a instalação antiga do Inno;
  - M27: o teste rápido não conferir o motor (só ver se ele tem a forma).
  As M06 a M08 passam porque o Windows de mentira dos testes sempre deixa faltar mais de uma coisa ao mesmo tempo. Cada item
  do "preparado" precisa de um teste em que só ele falta.

## Os baixos (vão para a lista, não seguram a entrega)

1. **As 5 proteções sem teste** (acima).
2. **Comentários que já não são verdade:** a docstring de `garantir_o_motor` ("Qualquer erro: apaga o .chegando...", ver
   médio 1); `ocr_kraken.conferir_motor` e `empacotar.NOME_DO_MOTOR_EXIGIDO` (ver (a)); o ONDE-PAREI diz que o fim da
   primeira abertura "volta ao fio da tela por um sinal do Qt": no código não há sinal nenhum (o aviso "Sem a senha..."
   aparece antes, e o ajudante é chamado do fio de trás, o que não tem problema). E a rodada (ver acima).
3. **Conta duplicada:** `o_que_falta_no_computador` repete a conferência da tarefa que a peça já tem
   (`core.windows.problemas_da_tarefa_criada`), sem conferir a licença "quem pode mandar rodar". Um ajudante sem essa
   licença passaria por "preparado", e o programa do Kaique não conseguiria chamá-lo (só o registro diria).
4. **O motor é conferido inteiro a cada abertura do programa.** O ajudante roda a cada abertura e começa conferindo os
   34.522 arquivos do motor (o tamanho de cada um). Medi neste PC, na pasta do motor das ferramentas: 53 s na primeira vez
   e 10 s na segunda. Antes de trocar confere de novo, e o teste rápido de novo. Não trava a janela (é por trás, como o
   sistema), mas é disco ocupado por um minuto a cada abertura no notebook, e alonga o "Reiniciar agora", que fica sem nada
   na tela. Bastaria a conferência leve a cada abertura e a inteira só antes de trocar.
5. **No pacote portátil do Velopack** o programa procura o motor num lugar que ninguém enche (`lugares_do_motor` usa
   `instalado_pelo_velopack`, que inclui o portátil; quem põe o motor nunca roda no portátil). Hoje o publicar não faz mais
   o portátil (`--noPortable`), então não acontece; mas as duas regras deviam ser uma.
6. **O motor não é gravado no disco antes de ganhar o nome final** (o `zipar_motor` usa `windows.gravar_no_disco`; aqui
   não). Se faltar luz logo depois, podem ficar arquivos do tamanho certo e conteúdo vazio, e a conferência por tamanho não
   vê.
7. **Pasta `.estragado-...` que não sai inteira** (arquivo preso) fica para sempre; só a `.chegando` é limpa depois.
8. **Com "Agora não", o aviso "Sem a senha..." vem antes da pergunta do Windows** (antes vinha depois). O instante da
   pergunta passa a ser o "OK" do aviso, não o "Agora não". Funciona; só muda a ordem.
9. **"Na dúvida, é portátil" vira "preparado".** Se o Velopack não responder, `e_portatil` diz "portátil" e
   `o_que_falta_no_computador` devolve "nada falta" sem ler o Windows. É a regra antiga, mas aqui ela dá como feito o que
   não conferiu.
10. **Segunda conta do Windows no mesmo notebook:** na primeira abertura dela, a pergunta vem sem ler o Windows antes, mesmo
    com o computador já preparado (era assim antes também).

## O que a prova à vista precisa conferir

1. Instalar pelo .msi novo. Primeira abertura, "Agora não": a pergunta do Windows vem logo, no meio da tela, mostrando
   "EditorImpressao.exe". Dizer "Não". Fechar e abrir: a pergunta volta.
2. Dizer "Sim". No registro da atualização (`C:\ProgramData\EditorImpressao\atualizacao\`) aparece "o computador está
   preparado (lido no Windows)". **Fechar e abrir duas vezes: a pergunta não pode voltar.** Se voltar, a conta comum não está
   lendo as tarefas (ponto (e)): ler no registro qual item "falta".
3. Num prompt comum (sem administrador), `schtasks /Query /TN "EditorImpressao\Procurar versao nova" /XML` mostra a tarefa:
   prova que a conta comum lê. Se der, também numa conta comum de verdade (não administradora), se o Kaique usar uma.
4. Ver nascer `C:\Program Files\EditorImpressaoPrograma\motor-kraken\1` (sem sobrar `.chegando-1`). Anotar quanto tempo
   leva e quanto o disco do notebook tem livre.
5. Publicar uma versão nova. "Reiniciar agora": o programa volta sozinho, na versão nova (anotar quanto tempo fica sem nada
   na tela). `--conferir-ocr` acha o motor.
6. Outra versão, "Depois", fechar e abrir: a janelinha "Atualizando o programa, espere um pouco..." aparece e o programa
   abre na versão nova (é a primeira vez que essa janelinha roda pelo lançar novo).
7. Depois de cada troca, abrir o programa: nenhuma pergunta do Windows (D-735, D-741; ver médio 3).
8. Na abertura logo depois da primeira, olhar o Gerenciador de Tarefas: o ajudante lendo o disco por quanto tempo (baixo 4).

## Caminhos

- Este relatório: `relatorios/atualizador-4/quem-quebrou/relatorio-1.html` (também `.md` e `.pdf`).
- Os scripts que usei (fora do git, no rascunho do verificador): `mutar.py`, `zip_estragado.py`, `medir_motor.py`,
  `comparar_testes.py`.
