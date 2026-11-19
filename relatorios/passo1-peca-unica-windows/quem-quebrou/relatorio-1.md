# Passo 1 do plano da parte do Windows: primeira conferência de quem tentou quebrar (19/11/2026)

Sou o verificador que tenta quebrar o passo 1 (D-775). Não escrevi este código e não mexi nele. Não rodei nada que
peça a licença de administrador, nem abri janela na tela do Samuel.

## Pedido

- Papel: verificador
- Commit de partida: 39d7c556
- Ramo: passo1-peca-unica-windows

## Arquivos que vou mexer

- `relatorios/passo1-peca-unica-windows/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO.** A janela de prova não consegue fazer duas das três perguntas da sessão à vista. O nome da tarefa
da pergunta 2 tem parênteses, e a própria peça recusa esse nome antes de chamar o Windows. Por isso a pergunta 2
("Não") nunca aparece. E a pergunta 3, a que apaga o que a pergunta 1 criou, também nunca aparece. Se a sessão for
feita assim, a pasta de prova fica em Arquivos de Programas e a tarefa de prova fica no Agendador do PC do Samuel, sem
o caminho previsto para desfazer.

Fora isso, a peça está bem feita e os quatro defeitos da etapa 5 que ela devia fechar estão fechados e provados. Mas
há mais quatro achados médios. Dois deles (o "Não" que vira "deu certo" e "outra conta manda o programa com licença")
são justamente o foco deste passo e não têm teste que os pegue.

Não escrevo "PRONTO PARA CONFERIR" (D-798): o achado 1 impede a prova à vista.

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro, `memoria/INDICE.md`.
- O meu pacote (`anexos/pacote-quem-quebra.md`) e o do outro (`anexos/pacote-passo1.md`).
- O formulário dele (`ONDE-PAREI.md`) inteiro, com a seção "O dono da pasta de troca quando quem pede já tem a licença".
- O plano v3 (worktree `plano-windows`): "Regras de todos os passos", passo 1, peças 1, 2 e 10a, riscos 1 e 2. E a
  lista de defeitos do plano v1 (seção 2, itens 1 a 16), para ver quais tocam a peça 1.
- O código inteiro: `core/windows.py` (1559 linhas), a entrada nova do `main.py`, `janela_de_prova.py`,
  `tests/test_windows_peca.py`, `tests/test_windows_janela_de_prova.py`. Mais `historico.pasta_de_dados`,
  `atualizacao.xml_da_tarefa` e `QUEM_PODE_MANDAR_RODAR`, e a K01 do porteiro (`regras_dos_agentes/porteiro.py`).
- A documentação da Microsoft de `SHELLEXECUTEINFOW` (lida de novo por mim, na fonte).
- As rodadas do GitHub 44558364601 (sucesso, sobre `1b1b0fa6`, conferido no registro: "TESTADO_SHA: 1b1b0fa6...") e
  44553075293 (a falha que mostrou o dono "S-1-5-32-544" com a conta 500 do GitHub).
- Desde `1b1b0fa6` só mudaram o formulário e o pacote (conferido com `git diff --stat`).

## O que conferi nos campos de falhas, de peça de fora e de caminhos, e como

Tudo por máquina, no PC, sem licença e sem mudar o Windows.

- **Testes no PC, um arquivo por vez**, com `QT_QPA_PLATFORM=offscreen`:
  - `test_windows_peca.py`: 31 passaram;
  - `test_windows_janela_de_prova.py`: 3;
  - `test_conferencias_codigo.py`: 77;
  - `test_conferencias_excecoes.py`: 14;
  - `test_decisoes_brasao.py`: 22;
  - `test_decisoes_atualizacao.py`: 38.

  O repositório continuou inteiro: `--is-shallow-repository` deu false antes e depois.
- **Prova de reversão, numa cópia à parte**, feita com `git archive` no rascunho, fora do projeto. Fiz 14 mutações em
  `core/windows.py`, cada uma voltando uma proteção ao jeito antigo ou desligando a proteção, e rodei
  `test_windows_peca.py` depois de cada uma:
  - **Acusadas (8):**
    - a pasta de troca criada do jeito do `mkdtemp` (defeito 3);
    - o `shell32` sem guardar o erro (defeito 2);
    - a resposta lida como ANSI ("ÒXITO");
    - o script sem a marca de UTF-8;
    - o lançar solto com a bandeira de processo sem console (defeito 1);
    - a regra da pasta de troca desligada;
    - o lado com licença sem conferir a licença;
    - o desfecho decidido pelo código de saída.
  - **Nenhum teste acusou (6):**
    - M7: o lado com licença sem conferir quem grava na pasta;
    - M8: o "Não" devolvendo "deu certo";
    - M9: todo erro do Windows lido como "Não";
    - M10: o aviso aceito mesmo ligado a outro arquivo;
    - M11: a pasta segura criada sem conferir;
    - M12: a tarefa criada sem ler de volta.

  Os achados 3, 4 e 13 vêm daí.
- **Os nomes da janela de prova contra a lista fechada da peça:** rodei só a regra (`_problemas_do_passo`), sem
  chamar o Windows. O resultado é o achado 1.
- **Leitura do Windows sem licença:** pelo leitor da própria peça, a pasta `\EditorImpressao` do Agendador não
  existe hoje neste PC (0x80070002). Daí sai o achado 6. Não existe tarefa nossa para ler e conferir o desenho
  devolvido pelo Windows (achado 5).
- **O PowerShell pela peça, em cinco casos:**
  - erro de escrita no script: falhou (código 1);
  - erro que não para o script: falhou (código 1);
  - comando de fora que falha (`cmd /c exit 5`) seguido de mais uma linha: **deu certo** (achado 10);
  - o que o script escreve como erro chega colado na resposta (`'{"codigo":0}AVISO'`, achado 11);
  - os acentos chegam certos.
- **O porteiro em arquivos inventados**, só lendo texto:
  - `schtasks` direto num arquivo do programa: barrado;
  - `ctypes.WinDLL` direto: barrado;
  - bandeira de lançar processo direto: barrada;
  - `windows._win().kernel32...` e `windows.rodar_e_esperar([windows.caminho_do_schtasks(), '/Delete', ...])` num
    arquivo de `ui/` ou `core/`: **nada barrado** (achado 12).
- **A leitura das peças de fora que o outro anotou, conferida na fonte:**
  - O `SEE_MASK_FLAG_NO_UI` diz "Security prompts are exempted and will still be shown". Confere.
  - O erro do `ShellExecuteExW` sai do `GetLastError`, e o código guarda o erro logo depois da chamada, sem outra
    chamada no meio. Confere.
  - O tamanho da estrutura (112 bytes no Windows de 64 bits) confere com o cabeçalho da Microsoft.
  - Os valores de `NOCLOSEPROCESS`, `NOASYNC` e `UNICODE` conferem.
  - A documentação avisa: "ShellExecuteEx does not always return an hProcess, even if a process is launched". O código
    trata esse caso como "o Windows não abriu o programa" (achado 9).
- **O tempo de importar a peça (a justificativa do texto copiado no `main.py`):** 87 a 88 ms para `import
  core.windows`, contra 73 a 74 ms só para a biblioteca padrão que ela usa. A conta dele (~100 ms) está perto.
- **O dono Administradores na pasta de troca (a decisão que a gerente pediu para olhar):** concordo com ela.
  - Uma pasta com dono "Administradores" só nasce de um programa que já roda com a licença. Uma conta comum não
    consegue pôr esse dono.
  - Quem é dono ganha licença de mudar as licenças da pasta. Esse dono só dá isso aos administradores, que já podem
    tudo.
  - A regra continua recusando qualquer outra conta que possa gravar, e foi isso que o teste novo cobrou ("dono
    Administradores com conta comum que grava": recusado).
  - O caso foi visto de verdade no GitHub (conta 500, dono S-1-5-32-544).
  - Não abre caminho novo para outra conta. O caminho que fica aberto é outro, o achado 4 (a regra não é provada no
    lado com licença).
- **A entrada no `main.py` (D-605):** só age se o primeiro argumento for exatamente `--trabalho-de-administrador`. A
  abertura normal e a abertura com um PDF não mudam. O teste do brasão passa.

## Caminhos que o outro não listou

- **A janela de prova chamando a peça com nomes fora da lista dela** (achado 1). O ensaio dele rodou só as provas 1, 5
  e 6, as que não pedem licença. As provas 2, 3 e 4 nunca passaram nem pela regra do pedido.
- **Rodar a sessão de novo.** A pasta segura de prova que já existe é aceita como está, com o arquivo da tarefa da
  vez anterior dentro (achado 2).
- **A pasta do Agendador** `\EditorImpressao`, que a primeira tarefa cria e que apagar a tarefa não apaga (achado 6).
- **Outro arquivo do programa usando a biblioteca crua da peça** (`_win()`) ou o "rodar e esperar" genérico com o
  caminho do `schtasks` (achado 12).
- **O trabalho com licença que continua depois do "não terminou no tempo"** (achado 9).

## Falhas não pensadas e resultado não conferido

- A tarefa criada e não conferida fica no Windows (achado 5).
- A pasta segura que "foi apagada de novo" sem conferir (achado 7).
- Quem pode **ler** a pasta de troca não é conferido, e o segredo cifrado ali abre em qualquer conta do computador
  (achado 8).
- O script que "deu certo" com um comando de dentro falhando (achado 10).
- O relatório com menos passos que o pedido vira "deu certo" (achado 14).

## As regras que conferi

- **CLAUDE.md §11.12:**
  - Ponto 1, uma peça só: sim, mas a peça deixa a porta aberta para o "cada um do seu jeito" por dentro dela (achado
    12).
  - Ponto 2, nada dá como feito sem conferir: falha nos achados 5, 7 e 14.
  - Ponto 3, a lista das falhas: está boa, faltam os casos dos achados 6, 8 e 9.
  - Ponto 4, peça de mentira: os testes não fingem o Windows. A prova de verdade é a sessão A.
  - Ponto 6, ler a peça de fora: conferido acima.
- **CLAUDE.md §4.7, teste de reversão:** provado por mutação para 8 proteções. Seis não têm teste (achados 3, 4 e 13).
- **D-767 e D-785:** não pedi licença, não criei tarefa, não mexi em Arquivos de Programas e não abri janela na tela.
- **D-605:** o `main.py` só muda com o argumento novo. Nenhum teste antigo mudou.
- **D-791, D-801 e D-802:** o porteiro e a lista de exceções estão iguais aos de `b9f07e43` (o `git diff` não toca
  `regras_dos_agentes/`). `core/windows.py` é o único lugar liberado.
- **D-782, nome na pergunta:** pela metade, e o outro já disse isso com todas as letras. Pela leitura, a pergunta vai
  mostrar "EditorImpressao.exe", e a pergunta ao Samuel está pronta. Pelo plano, se o nome não aparecer, a sessão para
  na pergunta 1.
- **D-722, tudo desfeito no fim:** hoje não se cumpre, pelos achados 1 e 6.
- **D-798:** não escrevo o rótulo, por causa do achado 1.

## Achados

1. **GRAVE: a janela de prova não consegue fazer a pergunta 2 nem a pergunta 3**
   (`janela_de_prova.py:56`, `TAREFA_DO_NAO = "EditorImpressao\\Prova da peca do Windows (Nao)"`, contra
   `core/windows.py:100`, `_NOME_DE_TAREFA`, que só aceita letras, números, espaço, ponto, sublinhado e hífen).
   - Rodei só a regra, sem o Windows. O nome "(Nao)" é recusado: "nome de tarefa fora da pasta do programa".
   - A pergunta 2 cria essa tarefa, e a pergunta 3 a apaga. Nas duas, `pedir_licenca` devolve "falhou: o pedido ao
     Windows está errado" **antes** de chamar o Windows.
   - Na sessão à vista, o Samuel esperaria uma pergunta que não vem. O que a pergunta 1 criou (a pasta
     `C:\Program Files\EditorImpressaoProvaPastaSegura` e a tarefa `\EditorImpressao\Prova da peca do Windows`)
     ficaria no PC dele sem o desfazer previsto. Isso quebra a D-722.
   - O teste da janela não pega, porque não confere os passos das provas 2 a 4.
   - O que pedir:
     - um nome sem parênteses;
     - um teste que passe todos os passos das seis provas por `_problemas_do_passo`, sem o Windows (esse teste falha
       no código de hoje, então serve de reversão);
     - na pergunta 3, apagar a pasta e as tarefas mesmo que um passo falhe. Hoje o trabalho para no primeiro passo que
       falha, e para desfazer isso deixa mais coisa para trás.

2. **MÉDIO, e vai acontecer por causa do 1: a prova "a tarefa rodou como o sistema" pode ser enganada por um arquivo
   da vez anterior** (`janela_de_prova.py:215-222`; `core/windows.py:1135-1136`).
   - `criar_pasta_segura` aceita a pasta de prova que já existe e não esvazia nada.
   - A janela só olha se `tarefa-rodou.txt` existe. Se a sessão for repetida (o que o achado 1 força), o arquivo velho
     faz a janela escrever "A tarefa rodou às <hora velha> como ... é o sistema, certo", mesmo que a tarefa nem rode.
   - O que pedir: conferir a hora do arquivo contra a hora do pedido, ou zerar o arquivo nos passos com licença antes
     de mandar rodar.

3. **MÉDIO: nenhum teste prova que o "Não" vira "você disse Não" e que uma falha não vira "Não"**
   (`core/windows.py:1477-1479` e `1536-1537`). É o primeiro item do foco deste passo.
   - A mutação M8 (o "Não" devolvendo "deu certo") passou nos 31 testes.
   - A mutação M9 (todo erro lido como "Não") também passou.
   - O teste de hoje só confere que as bibliotecas guardam o erro e que o número 1223 está certo.
   - A lógica em volta pode ser provada sem o Windows: um `_abrir_com_licenca` de mentira devolvendo "nao", "erro:2"
     e "tempo", cobrando o desfecho de cada um. Isso é lógica em volta, que a D-767 aceita. O "Não" de verdade fica
     para a sessão à vista.
   - A prova 5 da janela ("programa que não existe") também não chega ao Windows. Ela para antes, na conferência do
     Python (`core/windows.py:1516`). Então não prova o que o plano diz ("sem a caixa crua do Windows"). Para provar,
     a prova teria de chamar o Windows com um arquivo que não existe. A documentação diz que isso não abre caixa nem
     pergunta, mas eu não rodei, para não arriscar uma caixa na tela do Samuel.

4. **MÉDIO: nenhum teste prova que o programa com licença recusa uma pasta de troca onde outra conta grava**
   (`core/windows.py:1317-1323`, `_conferir_a_troca`). É o segundo item do foco ("outra conta não consegue mandar ele
   fazer outra coisa").
   - Com a mutação M7, que tira essa conferência do lado com licença, os 31 testes passam. Só a função da regra é
     testada, com licenças montadas à mão.
   - O próprio outro achou um lugar real onde "Todos" gravam: a pasta de dados dos testes no D:. Um teste que monte
     ali uma pasta de troca com aviso e cobre `SAIDA_PASTA_RECUSADA` provaria a regra no lugar onde ela age, sem mudar
     o Windows.

5. **MÉDIO: `criar_tarefa` deixa a tarefa no Windows quando a leitura de volta não confere, e o desenho devolvido
   pelo Windows nunca foi visto** (`core/windows.py:1060-1064`).
   - Se o que foi lido não bate com o pedido, a resposta é "a tarefa não ficou criada como pedido", mas a tarefa criada
     fica lá, com outro conteúdo. Isso é a "pela metade" do §11.12.3.
   - A comparação inclui o texto `RegistrationInfo/SecurityDescriptor` devolvido pelo Windows. Nada no projeto mostra
     que o Windows devolve esse texto igual ao que recebeu. O outro código do projeto põe a licença da tarefa por
     `SetSecurityDescriptor` (`core/testes_a_distancia.py:350`). Não há tarefa nossa neste PC para ler, e criar uma é
     da sessão à vista.
   - Se o Windows devolver o texto diferente, a pergunta 1 falha em "criar a tarefa" e deixa a tarefa criada. A janela
     ainda corta o técnico em 300 letras (`janela_de_prova.py:111`), e a parte "lida: ..." que explicaria a falha
     pode sumir.
   - O que pedir:
     - apagar o que foi criado quando não confere, e conferir que sumiu;
     - ler a licença da tarefa pelo próprio Windows (`GetSecurityDescriptor`);
     - mostrar o técnico inteiro no registro da janela.

6. **MÉDIO: a pergunta 3 deixa a pasta `\EditorImpressao` no Agendador, e "o que foi desfeito" não diz isso**
   (`janela_de_prova.py:245-252`).
   - Hoje essa pasta não existe neste PC (lido: 0x80070002).
   - A primeira tarefa da sessão cria a pasta. Apagar a tarefa não apaga a pasta, e a janela não lê a pasta no fim.
     Isso fere a D-722 ("tudo o que o teste pôs no Windows dele é desfeito").
   - Pela minha leitura, apagar a tarefa não apaga a pasta. Não testei, porque criar a pasta é da sessão à vista.

7. **BAIXO: "a pasta criada agora foi apagada de novo" sem conferir** (`core/windows.py:1143-1145`). Usa
   `shutil.rmtree(..., ignore_errors=True)` e não olha se a pasta sumiu, ao contrário de `apagar_pasta_segura`, logo
   abaixo.

8. **BAIXO a MÉDIO, conta no passo 4: ninguém confere quem pode ler a pasta de troca**
   (`core/windows.py:588-598` e `892-907`).
   - O segredo vai cifrado "para este computador", então qualquer conta do computador que consiga ler o arquivo
     consegue abri-lo.
   - O formulário diz que "só a conta e os administradores leem", mas a regra só confere quem grava.
   - Na pasta da conta, de fábrica, está certo. Numa pasta de dados que outras contas leem, a senha dos testes ficaria
     exposta enquanto o pedido roda.

9. **BAIXO: depois do "não terminou no tempo", o programa com licença continua trabalhando sem ninguém saber**
   (`core/windows.py:1487-1488`, `1540-1542` e `1554-1559`).
   - Quem pediu apaga a pasta de troca e diz "não terminou em 30 minutos". O programa com licença segue fazendo os
     passos, e o relatório dele se perde.
   - A frase deveria dizer que a mudança pode acontecer depois. Hoje ela dá a entender que nada aconteceu.
   - Dois casos vizinhos:
     - se o Windows não devolver o processo aberto (a documentação diz que pode acontecer), a resposta é "o Windows
       não abriu o programa", mas ele pode ter aberto;
     - se a espera do Windows falhar, o laço gira sem parar até o limite.

10. **BAIXO agora, conta nos passos 3 a 5: o passo "script" dá "deu certo" com um comando de dentro falhando.**
    Conferido: `cmd /c exit 5` seguido de outra linha deu "deu certo" (`core/windows.py:720-723` e `726-733`).
    - A docstring avisa, mas é a mesma família do "nada dá como feito o que não conferiu".
    - O que pedir: os scripts dos próximos passos conferem o `$LASTEXITCODE` (uma ajuda na cabeça do script, que
      todos usam) ou terminam lendo o resultado.

11. **BAIXO: a resposta junta o que o programa escreve como saída com o que escreve como erro**
    (`core/windows.py:719`).
    - Conferido: `'{"codigo":0}AVISO'`.
    - Na leitura de tarefa, cai no lado seguro: "não deu para saber".
    - Na janela de prova, a conta da soma do segredo usa essa mesma resposta.
    - O que pedir: separar as duas.

12. **MÉDIO para a gerente decidir, porque mexe no porteiro: a peça entrega a biblioteca crua do Windows e o "rodar
    qualquer ferramenta" a qualquer arquivo, e o porteiro não vê.**
    - Lugares: `core/windows.py:329-334` (`_win()`), `701` (`rodar_e_esperar`) e `392-394` (`caminho_do_schtasks`).
    - Conferido com arquivos inventados: `windows._win().kernel32.CreateProcessW(...)` em `ui/` e
      `windows.rodar_e_esperar([windows.caminho_do_schtasks(), "/Delete", ...])` em `core/` passam sem achado.
    - Assim, nos passos 3 a 5, cada chamador pode voltar a falar com o Windows "do seu jeito", só que por dentro da
      peça.
    - O porteiro já lista "uma segunda peça com outro nome" como coisa que ele não pega, mas aqui a porta é nova e vem
      deste passo.
    - Sugestão: deixar privadas as partes cruas, ou ensinar a K01 a acusar `_win(` e o caminho das ferramentas fora
      da peça.

13. **BAIXO: proteções sem teste.**
    - M10, o aviso ligado a outro arquivo.
    - M11, a pasta segura criada sem conferir.
    - M12, a tarefa criada sem ler de volta.
    - M11 e M12 só rodam com a licença. O Windows do GitHub roda com ela, numa máquina que se joga fora no fim. Fica
      para a gerente decidir se vale como prova extra, que não substitui a sessão à vista (D-785).

14. **BAIXO: quem pede não compara os passos do relatório com os que pediu** (`core/windows.py:1427-1447`). Um
    relatório com menos passos, todos "deu certo", vira "deu certo". Isso só acontece se alguém trocar o aviso, e esse
    alguém teria de ser a própria conta.

15. **BAIXO, para os passos 3 e 4, sem mudar nada agora: a mesma conta, sem licença, consegue trocar o script ou o
    desenho da tarefa que o programa com licença grava na pasta de troca da conta, antes de ele usar.**
    - Lugares: `rodar_powershell` e `criar_tarefa` dentro do trabalho com licença.
    - A Microsoft não trata a passagem da mesma conta para a licença de administrador como fronteira de segurança.
    - O plano só pede "outra conta".
    - Para o ajudante que roda como o sistema (passo 3), nada que ele roda deve vir de pasta que a conta comum grava.

16. **Observação, não é defeito: o texto do argumento escrito à mão no `main.py`** (`main.py:125`).
    - Segue o jeito dos outros três modos do `main.py` (`--servidor-de-paginas`, `--brasao-girando`,
      `--conferir-ocr`), e um teste cobra que é igual ao da peça.
    - Medi 87 a 88 ms para importar a peça. Um arquivo pequeno só com o texto custaria ~1 ms. Fica a critério da
      gerente.
    - Mais duas coisas que o programa com licença faz além do aviso, ambas pequenas:
      - limpa as pastas de troca velhas da conta;
      - escreve no `erros.log`.

17. **BAIXO, só da ferramenta de prova: fechar a janela de prova no meio de uma pergunta derruba o processo dela.**
    - Lugar: `janela_de_prova.py:289-358`, o fio de trabalho ainda rodando.
    - O programa com licença termina sozinho, mas o registro fica pela metade.
    - Na sessão à vista, a gerente não deve fechar a janela no meio de uma prova.

## O que falta para a prova à vista

1. O outro consertar o achado 1, com o teste de reversão. De preferência também os achados 2, 3, 4 e 5, que mexem no
   que a sessão prova, e o 6 (ler e apagar a pasta do Agendador, ou dizer na lista do que foi desfeito que ela ficou).
2. Nova rodada do GitHub sobre o commit do conserto.
3. Eu (ou outro verificador) conferir o conserto.
4. A gerente montar a pasta do programa no C:, à vista, a partir desse commit, com 0 perguntas e a reserva de 20 GB
   conferida.
5. A sessão A com o Samuel, com as 3 perguntas do Windows e o registro da janela guardado.

Antes da sessão, a gerente diz ao Samuel que, pela leitura, a pergunta vai mostrar "EditorImpressao.exe". Pelo plano,
isso para a sessão na pergunta 1, e a pergunta sobre o nome que o outro preparou vai à Central.

Só depois disso, e com cada achado com destino, cabe "PRONTO PARA CONFERIR" (D-798). Nunca "aprovado": só o Samuel
aprova.

## Para a gerente: o que ficou fora do projeto

- Na pasta de rascunho desta conversa
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\`)
  deixei:
  - a cópia da prova de reversão, `copia-reversao\` (os `.py` da raiz, `core\` e três arquivos de `tests\`, tirados
    com `git archive`);
  - os scripts `checar_nomes.py`, `ler_tarefas_existentes.py`, `porteiro_sintetico.py`, `powershell_casos.py` e
    `mutacoes.py`.
  - Não apaguei nada disso.
- **Aviso, por honestidade:** dois scripts meus criaram, cada um, uma pasta própria em
  `C:\Users\fotog\AppData\Local\Temp` (`quemquebra-*` e `quemquebra-ps-*`), para a pasta de troca da peça não ir para
  o D:. Cada script apagou a sua pasta no fim. Elas só tinham as pastas de troca que a própria peça cria e apaga.
  Foi apagar fora do projeto algo que eu mesmo tinha criado segundos antes. A regra diz "nunca", então registro aqui.
- Nada mudou no Windows: nenhuma tarefa, nenhuma licença, nenhuma pasta em Arquivos de Programas, nenhuma pergunta de
  administrador.
