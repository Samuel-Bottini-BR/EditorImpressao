# Quem tentou quebrar: os 4 consertos do atualizador (relatório 2, a última conferência)

Verificador, 22/11/2026. Trabalho conferido: ramo `atualizador-4-consertos-2026-11-21`, ponta `80be0770` (o código é o de
`f523ec2e`; depois dele só o formulário mudou). A volta 2 do escritor: `f5d73572`, `ebc4891e`, `9979419d`, `6efa58d7`,
`f523ec2e`. Não abri janela na tela do Samuel, não pedi licença ao Windows, não mudei o código do programa. As provas foram
feitas numa cópia minha no rascunho (tirada no fim).

## Veredito

**PRONTO PARA CONFERIR.** Os três médios do relatório 1 foram consertados pela causa, cada um num lugar só, e cada
proteção nova tem um teste que acusa quando ela é desligada (15 de 15). O que já estava certo continua certo. Não achei
nada grave nem médio criado pela volta 2. Achei 6 baixos e uma pergunta que precisa ir ao Samuel antes da entrega: em dois
casos raros a atualização para de chegar **sem nada avisar** (sem o motor do Kraken no lugar; e depois de um "Não", se o
Windows não deixar ler as tarefas). O código faz o que foi decidido; avisar exigiria uma frase nova na tela, e isso só o
Samuel decide.

Máquina ou olho: tudo aqui é **máquina** (leitura do código, testes, cópia com proteções desligadas, uma leitura sem
licença no Windows deste PC). A pergunta do Windows, a troca e o motor de verdade ficam para a prova à vista (D-767).

## Os 3 médios do relatório 1: consertados

| Médio | Como ficou | Teste que acusa |
|---|---|---|
| 1. Arquivo do motor estragado escapava sem registro | `garantir_o_motor` pega qualquer erro, apaga o provisório, registra; `rodar_ao_ligar` não deixa um erro do motor impedir a procura | desligar cada uma das duas proteções é acusado (V01, V02) |
| 2. Sem o motor no lugar, "Chegou uma versão nova" sem fim | A conferência do motor vem **antes** de baixar, num lugar só (`procurar_e_preparar`); sem motor, não baixa nem anuncia; um "pendente" de antes vira "esperando-o-motor", que a tela, a abertura e o script da troca leem como "nada" | V03, V04, V05 e V14 (baixar antes de conferir) acusados |
| 3. A pergunta do Windows voltava depois do "Sim" | A regra única (`o_que_falta_no_computador`) lê só as duas tarefas que só a pergunta cria; o Visual C++ e a instalação antiga ficam com o ajudante; "não deu para saber" não traz a pergunta | V06, V10, V12 (Visual C++ de volta na pergunta), V13 acusados |

Item 4 (a conta duplicada): saiu a conferência própria (`_mesmo_caminho`); a pergunta "o ajudante é o deste programa?" usa a
da peça única (`core.windows.problemas_da_tarefa_criada`), que confere também quem pode mandar rodar. V08 e V09 acusados.
Item 5 (comentários): `core/ocr_kraken.conferir_motor` e `empacotar.NOME_DO_MOTOR_EXIGIDO` agora dizem a verdade.

Procurei de propósito leitores do estado da atualização em outros arquivos: só o `atualizacao.py` lê a "fase" (a tela usa
`situacao`; o script da troca para assim que a fase não é "pendente" nem "aplicando", então "esperando-o-motor" reabre o
programa na mesma versão, sem aviso). Nenhum desvio para um caso; nenhuma conta nova duplicada.

## Testes de reversão e mutações

- **Os testes novos no código da volta 1** (`2d5d912b`, numa cópia minha): 13 falham, 30 passam. Falham justamente os da
  volta 2 (médio 1 dos dois jeitos de estrago, médio 2 com o programa aberto e fechado, médio 3, item 4) e os 4 da volta 1
  que mudaram junto. Aqui as falhas são por comportamento (o erro escapa, a versão é anunciada, a pergunta volta), não por
  função que não existe.
- **Mutações** (cada proteção nova desligada, os 5 arquivos rodados um por vez): 15 de 15 acusadas.
  V01 except estreito · V02 sem o try do motor no ajudante · V03 sem conferir o motor · V04 o "pendente" não vira
  "esperando-o-motor" · V05 a tela lê "esperando-o-motor" como versão nova · V06 "não deu para saber" vira falta · V07 o
  ajudante que não existe deixa de contar · V08 licença ilegível vira falta · V09 sem a conferência da peça · V10 o
  desfazer ilegível vira falta · V11 o desfazer que não existe deixa de contar (o M06 do relatório 1 agora é acusado) ·
  V12 o Visual C++ volta para a pergunta · V13 "existe mas não lê" vira falta · V14 baixar antes de conferir o motor.
  (Na primeira tentativa a V12 passou por um erro meu: eu chamei a leitura do Visual C++ de um jeito que o Windows de
  mentira do teste não troca. Refeita do jeito certo, foi acusada.)

## Nada do que a primeira conferência deu como certo quebrou

- Os 4 consertos originais: os arquivos deles passam no PC (um por vez) e no GitHub: `test_atualizador_4.py` 43,
  `test_decisoes_ajudante_da_atualizacao.py` 37, `test_decisoes_preparo_d749.py` 9, `test_decisoes_atualizacao.py` 38,
  `test_decisoes_testes_a_distancia.py` 13, `test_windows_peca.py` 71, `test_conferencias_excecoes.py` 14. O "Reiniciar
  agora", o "Depois" e a pergunta no meio da tela não foram tocados pela volta 2.
- A senha (opção B): `ui/testes_a_distancia_ui.py` e `main.py` não mudaram na volta 2.
- A lista de exceções do porteiro: não mudou na volta 2; contra a base, 91 linhas saíram e nenhuma entrou. O porteiro do
  GitHub passou.
- O `empacotar.py`: só o comentário de `NOME_DO_MOTOR_EXIGIDO` (1 linha de comentário trocada por 3). Nada mais.
- Frase nova na tela: nenhuma. Todo texto novo da volta 2 vai para o registro da atualização.

## As duas mudanças de comportamento que vão ao Samuel

**(a) "Sim" com o Visual C++ ou a instalação antiga falhando: a pergunta não volta; o ajudante completa.** Confere com o
código. A preparação cria as duas tarefas primeiro e só depois instala o Visual C++ e tira a instalação antiga. Se um dos
dois falha, a pergunta termina como "não deu certo", mas a leitura acha as duas tarefas: a pergunta não volta, e o programa
chama o ajudante na mesma hora. O ajudante roda como o sistema (tem licença sem perguntar) e, toda vez que roda, tenta de
novo o Visual C++ e a instalação antiga.
- **Se o ajudante também falhar:** a falha vai para o registro ("Visual C++ ...: NÃO instalado") e ele segue: põe o motor,
  procura e troca de versão normalmente. Isso se repete a cada abertura, em silêncio, sem pergunta nem aviso. Se a versão
  nova não abrir por isso, o teste rápido pega e ela volta para a anterior com o aviso que o Samuel já escolheu.
- Risco escondido, pequeno: uma instalação do Visual C++ que trava segura o ajudante até 10 minutos a cada abertura. Isso
  atrasa a procura e pode estourar o tempo do "Reiniciar agora". Já era assim antes desta volta.
- O teste da D-749 com a preparação "no meio" continua passando, mas o Windows de mentira dele cria o ajudante e não cria o
  desfazer. A preparação de verdade cria os dois antes do Visual C++. Então esse teste não mostra o caso (a); quem mostra é
  o teste novo do Visual C++.

**(b) Depois de um "Não", se o Windows não deixar ler as tarefas, a pergunta não aparece naquela abertura.** Confere com o
código, e provei numa cópia: com a leitura falhando sempre, depois de um "Não", três aberturas seguidas não perguntaram
nada. **Risco escondido:** se a leitura falhar sempre (um antivírus que barra o PowerShell, por exemplo), a pergunta nunca
mais volta, o computador nunca fica preparado e nenhuma versão chega. O registro anota "não pergunto de novo por isso",
mas ninguém o lê de longe nesta entrega (com a opção B, os testes à distância ficam desligados). Quando o Windows não
responde de vez em quando, a pergunta volta na abertura seguinte.
- Para comparar: antes da volta 2 era o contrário. Com a leitura falhando sempre, a pergunta voltava em toda abertura, e o
  "Sim" não resolvia. Os dois casos são raros; a escolha entre eles é do Samuel.

**Pergunta que sobra para o Samuel, do mesmo tipo:** sem o motor do Kraken no lugar (o notebook com menos de uns 1,7 GB
livres na primeira vez, ou o arquivo do motor estragado), a versão nova agora não é anunciada nem trocada. Isso é o certo,
e o aviso falso saiu. Mas nada avisa ninguém: a atualização simplesmente não chega até o motor entrar. Se o espaço for
liberado, ela chega sozinha. Se o arquivo do motor estiver estragado, ela não chega nunca, e a cada abertura o ajudante
abre o arquivo de novo (minutos de disco). Avisar exigiria uma frase nova na tela.

## Achados novos (todos baixos)

1. **O registro diz o que não é depois de um "Não" com a leitura falhando.** Provado numa cópia. O registro fica com "o
   Kaique disse Não... a pergunta volta" e logo depois "as tarefas do programa estão no Windows; o que faltou (o Visual C++
   ou a instalação antiga) o ajudante completa sozinho". As tarefas não estão lá. O programa também manda rodar um ajudante
   que não existe (não faz mal). Onde: `atualizacao.py`, `preparar_na_primeira_abertura`, o último `else`, que só pergunta
   "nada falta?" e não "eu consegui ler?". A tela não mostra nada disso.
2. **Licença do ajudante que não dá para ler: o resto da conferência também pula.** Quando a licença não vem, o programa
   não confere mais nada da tarefa: nem o programa que ela roda, nem os argumentos, nem a conta. Provado numa cópia: uma
   tarefa que roda `C:\Outro\Programa.exe` passa como "preparado". Na volta 1 isso era conferido. É raro: neste PC, sem
   licença de administrador, li a licença de três tarefas do Windows sem problema. Onde: `o_que_falta_no_computador`, o
   ramo `elif ajudante.lida and not ajudante.licenca`. O jeito simples: comparar o resto e pular só a licença.
3. **O formulário ainda diz que o caminho da tarefa é comparado pela "coisa de verdade, caminho normalizado" (D-813).**
   Desde o item 4 a comparação é do texto (a da peça). Esse erro só pode fazer a pergunta voltar sem precisar, nunca deixar
   passar uma tarefa errada. E o caminho vem da mesma função dos dois lados, já normalizado. Onde: ONDE-PAREI, a linha
   da D-813.
4. **A docstring de `garantir_o_motor` diz "nunca levanta".** Mas a primeira conferência do motor e o "o arquivo existe?"
   ficam fora da proteção. Se derem erro de disco, o erro sobe, e quem segura é o `rodar_ao_ligar` (a procura continua).
   O comentário está um pouco além da verdade; o efeito está certo.
5. **Uma conferência inteira do motor a mais.** Quando há versão nova, o motor (34 mil arquivos) é conferido antes de
   baixar, agora também com o programa aberto. Some ao baixo 2 do relatório 1 (10 a 53 s de disco por vez, por trás).
6. **O teste da D-749 "no meio"** não mostra a preparação de verdade (ver (a) acima). Ele continua cobrando o que
   cobrava; só não cobre o caso novo.

Os 11 baixos do relatório 1 que ficaram para depois estão no formulário do escritor e não mudaram. O M05 e o M27
continuam sem teste próprio; o M06 agora é acusado (V11).

## A rodada do GitHub 44982726269

- Testou este ramo. Na 2ª tentativa, as partes 1, 3, 4 e 5, o porteiro e os botões são da 1ª, no commit `f523ec2e`. A
  parte 2 foi refeita no commit `02602e30` (todas dizem "codigo trocado pelo de atualizador-4-consertos-2026-11-21").
  Esses dois commits têm o mesmo código da ponta `80be0770`: entre eles só muda o ONDE-PAREI. Resultado: sucesso.
- A queda da 1ª tentativa (parte 2): `test_decisoes_gravura_a_mao.py::test_d659_g_..._de_antes[original]`, "procurou:
  [0]". O detector de gravura de mentira foi chamado uma vez na página 0, quando devia ficar quieto: a prévia de outro fio
  correu na hora errada. **Não tem relação com estes consertos.** Esse teste não usa `atualizacao.py`, o motor nem o
  `empacotar.py`. A volta 2 não mexeu em nada de `ui/` nem do processamento (no `core/ocr_kraken.py`, só um comentário).
  Na 2ª tentativa ele passou. Parece um teste que falha de vez em quando por causa do tempo; vale anotar na Lista de bugs.

## O que a prova à vista precisa conferir

1. Instalar pelo .msi novo. Primeira abertura, "Agora não": a pergunta do Windows vem logo, no meio da tela, com
   "EditorImpressao.exe". Dizer "Não". Fechar e abrir: a pergunta volta.
2. Dizer "Sim". No registro (`C:\ProgramData\EditorImpressao\atualizacao\`): "o computador está preparado (lido no
   Windows)". **Não pode aparecer** "não deu para ler o ajudante" nem "não deu para ler a licença": se aparecer, a conta
   do Kaique não está lendo as tarefas, e o caso (b) e o baixo 2 deixam de ser raros.
3. Fechar e abrir duas vezes: nenhuma pergunta.
4. Ver nascer `C:\Program Files\EditorImpressaoPrograma\motor-kraken\1`, sem sobrar `.chegando-1`. Anotar o tempo e o
   espaço livre do disco.
5. Publicar uma versão nova. "Reiniciar agora": o programa volta sozinho na versão nova. `--conferir-ocr` acha o motor.
6. Outra versão, "Depois", fechar e abrir: a janelinha "Atualizando o programa, espere um pouco..." aparece e o programa
   abre na versão nova.
7. Depois de cada troca, abrir o programa: nenhuma pergunta do Windows.
8. Se der tempo (é o caso do médio 2): renomear `motor-kraken\1` como administrador e publicar outra versão. Não pode
   aparecer "Chegou uma versão nova". O registro diz "não baixo nem anuncio esta versão". Pôr o nome de volta: na
   abertura seguinte, a versão chega.

## Caminhos

- Este relatório: `relatorios/atualizador-4/quem-quebrou/relatorio-2.html` (também `.md` e `.pdf`).
- Os scripts que usei (fora do git, no rascunho do verificador): `scripts/mutar2.py`; o teste temporário dos casos (a),
  (b) e dos baixos 1 e 2 foi apagado junto com a cópia.
