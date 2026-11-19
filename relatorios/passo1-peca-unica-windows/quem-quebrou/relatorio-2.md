# Passo 1 do plano da parte do Windows: segunda conferência de quem tentou quebrar (19/11/2026)

Segunda volta do mesmo verificador, que não escreveu este código. Conferi o destino de cada achado do relatório 1 no
código de `a21b311a`, com o formulário em `d1f6be95`, e procurei o que os consertos podem ter quebrado. Não mexi no
código, não pedi licença ao Windows e não abri janela na tela do Samuel.

## Pedido

- Papel: verificador
- Commit de partida: d1f6be95
- Ramo: passo1-peca-unica-windows

## Arquivos que vou mexer

- `relatorios/passo1-peca-unica-windows/quem-quebrou/`

## Veredito

**Pode ir para a prova à vista. Ainda não escrevo "PRONTO PARA CONFERIR".**
- O achado grave (as perguntas 2 e 3 que não apareciam) está consertado. Conferi que as três perguntas chegam à
  chamada do Windows.
- Os outros consertos pegam a causa. Os testes novos acusam a volta do código antigo.
- Achei quatro coisas novas de gravidade média. Nenhuma impede a sessão à vista. Uma delas vale consertar antes (N1,
  uma linha de teste).
- Pela D-798, o rótulo só vem depois da prova de verdade (data, hora, à vista, registro da janela de prova). Essa prova
  ainda não aconteceu.

## O que li

- O ONDE-PAREI em `d1f6be95`: "O que o agente que tentou quebrar achou" (o destino de cada achado), as ressalvas da
  volta 1 e o anexo `reversao-volta1-resultado.txt`.
- O diff de `5de9c52d` a `a21b311a`:
  - `core/windows.py`: +521 linhas;
  - `janela_de_prova.py`;
  - os dois arquivos de teste;
  - o `main.py` e `regras_dos_agentes/` não mudaram (conferido).
- A rodada 44571676129: "success" na segunda tentativa, segundo a gerente. Não reli o registro dela.

## O que conferi, e como

Tudo por máquina, no PC, sem licença.

- **Testes no PC, um arquivo por vez:**
  - na cópia de `a21b311a`, `test_windows_peca.py` e `test_windows_janela_de_prova.py`: 49 passaram;
  - no ramo, `test_conferencias_codigo.py` (77), `test_decisoes_atualizacao.py` (38) e `test_decisoes_brasao.py`
    (22): passaram.
  - O repositório continuou inteiro: `--is-shallow-repository` deu false antes e depois.
- **As perguntas chegam ao Windows (achado 1).** Rodei as provas 2, 3 e 4 da janela numa cópia, trocando só a chamada
  que abriria a pergunta por uma que anota o pedido e responde "Não".
  - As três chegam à chamada, com o programa e o argumento certos.
  - A pergunta 3 leva os quatro passos de desfazer (as duas tarefas, a pasta segura de prova e a pasta do Agendador),
    com "ir até o fim" ligado.
  - O estado de antes do Agendador ficou anotado ("não existia").
  - Antes, as perguntas 2 e 3 paravam na regra da própria peça.
- **Prova de reversão, minha, numa segunda cópia à parte** (`git archive` de `a21b311a` no rascunho). Fiz 20
  mutações, cada uma desfazendo um conserto, e rodei os dois arquivos de teste:
  - **Acusadas (12):**
    - A1, o nome com parênteses de volta;
    - A2b, a pergunta 1 sem zerar o resultado;
    - A3, o "Não" virando "deu certo";
    - A4, o lado com licença sem conferir a pasta;
    - A8, ninguém conferindo quem lê a pasta de troca;
    - A9b, a frase do tempo esgotado sem o aviso de que o trabalho continua;
    - A10, o script sem a conferência do fim;
    - A12 e A12c, o rodar e o lançar genéricos sem a recusa;
    - A17, a janela fechando no meio da prova;
    - mais as do anexo dele, que confere com o que eu vi.
  - **Não acusadas (8):**
    - A1b, o desfazer parando no primeiro passo que falha (só o GitHub prova, porque no PC o trabalho é recusado antes
      de rodar os passos);
    - A1c, a pergunta 3 sem pedir "ir até o fim";
    - A2, a janela sem conferir a hora do resultado;
    - A6, a janela nunca apagando a pasta do Agendador;
    - A6b, a pasta do Agendador apagada sem conferir depois;
    - A9, a pasta de troca apagada mesmo com o tempo esgotado;
    - A9c, a espera que falha girando até o limite;
    - **M2 e M2b, a biblioteca que lê o "Não" sem guardar o erro (achado N1).**
- **O Agendador, lido sem licença** (só leitura):
  - a pasta raiz, a licença das tarefas da raiz e a das pastas;
  - `\EditorImpressao` continua não existindo neste PC, mesmo depois de as minhas rodadas de teste chamarem
    `schtasks /Create` uma vez por rodada (ver N4).
- **A regra "pela pasta do Windows" (achado 12)**, testada só como função, sem rodar nada, com várias formas de
  caminho. Resultado no achado N2.
- **O porteiro e o teste do "sublinhado"** em arquivos inventados, só lendo texto. Resultado no achado N2.

## Cada destino do relatório 1

1. **Consertado; pega a causa.**
   - O nome agora é aceito, e um teste passa todo pedido de toda prova pelas regras da peça. O teste falha com o nome
     antigo (A1 acusada).
   - A pergunta 3 vai até o fim com um passo que falha. Isso só é provado no GitHub (A1b).
   - Que a janela peça "ir até o fim" na pergunta 3 não tem teste (A1c), mas a minha simulação mostra que ela pede.
     Baixo.
2. **Consertado, em duas camadas.**
   - O passo com licença zera o resultado antes de criar a tarefa (acusado).
   - A janela só aceita o que foi escrito depois de mandar rodar. Essa conferência não tem teste (A2). Baixo, porque a
     primeira camada já fecha o caso.
3. **Consertado.**
   - A decisão do "Não" saiu para uma função só, com teste (A3 e M9 acusadas).
   - A prova 5 ganhou a parte (b), que chega ao Windows de verdade. Ela só roda à vista.
   - Mas a proteção que lê o "Não" na hora perdeu o teste dela: achado N1.
4. **Consertado** (A4 acusada). O teste põe "Todos" numa pasta do próprio teste e cobra a recusa no lado com licença.
5. **Consertado.**
   - A licença é lida pelo Windows e comparada pelo sentido. O que não confere é apagado, e a peça confere que sumiu.
   - Li as tarefas da raiz neste PC. O Agendador dá ao dono da tarefa o controle total, por herança:
     - criada com a licença: o dono é "Administradores" (ACCBackgroundApplication, "App Explorer");
     - criada pela conta comum: o dono é a conta (Launch Adobe CCXProcess).
   - Com a licença, como na sessão A, a regra deve conferir.
   - Se o Windows não aplicar a licença escrita no desenho da tarefa, a pergunta 1 falha de forma honesta e a tarefa é
     apagada. Só a sessão A diz.
6. **Consertado na janela.**
   - O estado de antes fica num arquivo, e a pergunta 3 apaga a pasta só se a prova a criou e se ela estiver vazia.
   - O fluxo está certo na simulação, mas não tem teste (A6 e A6b). Baixo.
   - Uma frase engana: quando a pasta nunca foi criada e a resposta é "Não", a janela escreve "foi apagada, o
     Agendador ficou como estava". O lugar é `janela_de_prova.py`, em `prova_pergunta_3`. Baixo.
   - Ver também o achado N3.
7. **Consertado** (acusado no anexo dele).
8. **Consertado** (A8 acusada).
9. **Consertado.**
   - A frase agora diz que o trabalho pode continuar (A9b acusada).
   - Manter a pasta de troca depois do tempo esgotado (A9) e parar quando a espera falha (A9c) não têm teste. Baixo.
10. **Consertado** (A10 acusada).
11. **Consertado.**
12. **A recusa pela pasta do Windows não é larga demais, mas tem buracos** (achado N2).
    - Ela recusa todo programa de `C:\Windows`. Cada ferramenta do Windows de que os passos 3 a 5 precisarem vai virar
      uma função da peça, e isso cumpre a "peça fechada" (§11.12.1).
    - Não quebra nada que existe hoje: nenhum chamador do programa usa a peça.
13. **Consertado** (acusado no anexo dele).
14. **Consertado** (acusado no anexo dele).
15. **Concordo que não é defeito deste passo.**
    - O plano pede "outra conta". A frase do Russinovich é real ("UAC elevations are conveniences and not security
      boundaries", de 2007).
    - Peço à gerente que o cuidado entre no pacote do passo 3 como regra: "nada que o ajudante roda como o sistema vem
      de pasta que a conta comum grava".
17. **Consertado** (A17 acusada).

## Achados novos

**N1. MÉDIO: o conserto do achado 12 apagou a prova do defeito 2 da etapa 5, o "Não" lido do jeito errado.**
- O teste antigo conferia que as seis bibliotecas da peça guardam o erro de cada chamada. O novo
  (`test_o_erro_do_windows_e_o_daquela_chamada`) só confere uma, a de `kernel32`, pelo comportamento.
- O teste antigo foi tirado porque usava `windows._win()`, e o teste novo do "sublinhado" proíbe isso também nos
  testes.
- A biblioteca que lê o "Não" é a `shell32` (`ShellExecuteExW` e depois `GetLastError`). Tirei dela o
  `use_last_error=True` (M2) e todos os testes passaram. O mesmo aconteceu com a `advapi32` (M2b).
- Saiu também do teste do pedido errado a troca que garantia que a pergunta nunca é feita. Hoje ele se apoia só num
  programa que não existe.
- Destino sugerido:
  - devolver a conferência das seis bibliotecas, com uma exceção escrita para o teste dentro da regra do "sublinhado";
  - ou dar à peça uma função pública que diga quais bibliotecas guardam o erro.
- Lugares: `tests/test_windows_peca.py`, `test_o_erro_do_windows_e_o_daquela_chamada` e
  `test_a_peca_e_fechada_ninguem_usa_o_que_tem_sublinhado_fora_dela`; `core/windows.py:305-310`.

**N2. MÉDIO, conta nos passos 3 a 5: a "peça fechada" tem três portas abertas** (`core/windows.py`,
`_programa_com_funcao_propria` e o topo "A PEÇA É FECHADA").
- **(a) Caminho escrito de outro jeito.** `\\?\C:\Windows\System32\schtasks.exe`,
  `\\localhost\C$\Windows\System32\schtasks.exe` e `\\127.0.0.1\ADMIN$\System32\schtasks.exe` **não são recusados**.
  Testei só a função, sem rodar nada. Sugestão: comparar o arquivo de verdade (o mesmo arquivo no disco), não o texto
  do caminho, ou recusar caminho de rede e o prefixo `\\?\`.
- **(b) O que tem "_" no nome só é privado de nome.**
  - `from core import windows as w` seguido de `w._rodar([...])`, ou `getattr(windows, "_rodar")`, passam pelo teste
    do sublinhado (ele procura o texto `windows._`) e pelo porteiro. Testei com arquivos inventados.
  - Assim o rodar sem nenhum filtro (`_rodar`) e a biblioteca crua (`_win()`) continuam ao alcance de qualquer
    arquivo.
  - Sugestão: o teste olhar a estrutura do código (todo acesso a nome com "_" na peça, com qualquer apelido), ou a
    gerente levar isso ao porteiro.
- **(c) Programas que não são do Windows passam pelo rodar genérico.**
  - Ex.: `C:\Program Files\Tailscale\tailscale.exe` (passo 4) e o Git.
  - A lista de fora tem só `pwsh` e `update`.
  - Cada programa de fora que um passo usar precisa entrar na lista, ou ganhar função própria. Isso vale anotar no
    pacote dos passos 2 a 4.

**N3. MÉDIO, conta no passo 3: qualquer conta do computador pode criar antes a pasta `\EditorImpressao` no Agendador,
com as licenças que quiser.**
- Lido neste PC: a pasta raiz do Agendador deixa "Usuários Autenticados" criar pastas (`(A;CI;FW;;;AU)`).
- `\SoftLanding` e `\GoogleUserPEH` foram criadas pela conta comum do Samuel. A `\SoftLanding` dá controle total a
  "Todos" (`(A;;FA;;;WD)`).
- Na criação, a peça confere a licença da tarefa, e isso pega uma licença herdada que deixa outra conta mudar a tarefa.
  Mas a peça **não confere o dono nem a licença da própria pasta**.
- Quem é dono da pasta pode mudar a licença dela depois. Se o Agendador passar a mudança para as tarefas, o ajudante
  (que roda como o sistema) ficaria mudável por outra conta. Isso não li nem provei.
- No passo 1, isso só toca a prova: se a pasta já existir, a janela não a apaga.
- Sugestão para o passo 3: conferir (e, se preciso, recusar) o dono e a licença da pasta `\EditorImpressao` antes de
  criar o ajudante, e na leitura do "preparado".

**N4. BAIXO, para a gerente decidir: um teste novo chama `schtasks /Create` de verdade no PC do Samuel**
(`test_a_tarefa_criada_que_nao_confere_e_apagada`).
- Sem a licença, o Windows recusa: conferi que a pasta `\EditorImpressao` continua não existindo depois de umas 20
  rodadas minhas.
- Mas se o conjunto rodar num terminal com a licença ligada (Controle de Conta desligado, ou "Executar como
  administrador"), ele cria e apaga uma tarefa do sistema no PC dele, escondido. Isso fere a D-785, que manda as
  tarefas serem sempre à vista.
- Sugestão: esse teste só criar a tarefa no Windows do GitHub (pela variável de ambiente do GitHub) e, fora dele,
  provar só a lógica.

## As regras que conferi

- **§4.7, reversão:** provada por mim em 12 mutações. As 8 sem teste estão acima; uma delas é a N1.
- **§11.12:**
  - ponto 1, uma peça só: N2;
  - ponto 2, nada dá como feito sem conferir: consertado nos achados 5, 7 e 14;
  - ponto 3, a lista das falhas: N3 é falha não pensada;
  - ponto 4, peça de mentira: N4.
- **D-605:** `main.py` e `regras_dos_agentes/` sem mudança.
- **D-722:** a pergunta 3 agora desfaz até a pasta do Agendador (simulado), com a frase da observação no item 6.
- **D-785:** não rodei nada com licença. A N4 é o único ponto de atrito.
- **D-798:** sem rótulo até a prova à vista.

## O que falta para a prova à vista e para o rótulo

1. De preferência antes da sessão: a N1 (devolver a prova do "Não").
2. N2, N3 e N4: dar destino. Consertar, levar ao pacote dos passos 3 e 4, ou a gerente aceitar.
3. A gerente monta o programa no C:, à vista, com a reserva conferida.
4. A sessão A, com as 3 perguntas e o registro da janela guardado.

Pela leitura, a pergunta vai mostrar "EditorImpressao.exe", e o plano para a sessão na pergunta 1 se o nome não for
"Editor de Impressão". A pergunta sobre o nome está pronta no formulário.

Só depois da sessão, com cada achado com destino, cabe "PRONTO PARA CONFERIR". Nunca "aprovado".

## Para a gerente: o que ficou fora do projeto

- No rascunho
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\`)
  ficou mais isto, nada apagado:
  - a cópia `copia-reversao-2\`;
  - as pastas `dados-leitura-agendador\` (as pastas de troca das minhas leituras) e `saida_teste` dentro da cópia;
  - os scripts `mutacoes2.py`, `provas_chegam_ao_windows.py`, `ler_licencas_agendador.py`,
    `ler_pasta_agendador.py` e `regra_pasta.py`;
  - o arquivo `estado-de-antes-teste.json`.
- Nada mudou no Windows:
  - não houve pergunta de administrador, licença mudada nem pasta em Arquivos de Programas;
  - houve, sim, tentativas de `schtasks /Create` vindas dos testes do outro (N4), todas recusadas pelo Windows, e a
    pasta do Agendador continua não existindo.
