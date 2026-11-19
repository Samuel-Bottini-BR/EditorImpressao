# Passo 1 do plano da parte do Windows: terceira conferência de quem tentou quebrar (19/11/2026)

Terceira volta do mesmo verificador, que não escreveu este código. Conferi os consertos de N1 a N4, a frase da pasta
do Agendador, os testes das mutações que passavam e o conserto dos nomes das contas. O código conferido é o de
`6bf3459a`, e o formulário, o de `d66b6cd3`. Não mexi no código, não pedi licença ao Windows e não abri janela na tela
do Samuel.

## Pedido

- Papel: verificador
- Commit de partida: d66b6cd3
- Ramo: passo1-peca-unica-windows

## Arquivos que vou mexer

- `relatorios/passo1-peca-unica-windows/quem-quebrou/`

## Veredito

**Sim, pode ir para a prova à vista.**
- Não há achado grave nem achado que mude o que a sessão prova.
- Ainda não escrevo "PRONTO PARA CONFERIR": pela D-798, o rótulo só vem depois da prova de verdade, à vista, com data,
  hora e o registro da janela de prova.
- Ficam três achados pequenos, que podem ser consertados depois da sessão ou levados ao passo 3.

## O que conferi, e como

Tudo por máquina, no PC, sem licença.

- **Testes no PC, um arquivo por vez:**
  - `test_windows_peca`: 49 passaram e 1 foi pulado (o que cria tarefa, agora só no GitHub);
  - `test_windows_janela_de_prova`: 10;
  - `test_conferencias_codigo`: 77;
  - `test_decisoes_atualizacao`: 38;
  - o repositório continuou inteiro (`--is-shallow-repository` deu false).
- **A prova de reversão dele** (`anexos/reversao-volta2-resultado.txt`): 26 mutações acusadas, de 27.
  - A que fica de fora é a da tarefa criada sem ler de volta. Ela só pode ser provada com a licença, no GitHub. É o
    combinado.
- **A minha prova, numa cópia à parte de `6bf3459a`:**
  - "o nome da conta vira o número": acusada;
  - "criar a tarefa sem conferir a pasta do Agendador antes": acusada;
  - "criar a tarefa sem conferir a pasta depois": **nenhum teste acusou** (achado T2).
- **O caminho escrito de outro jeito (N2)**, testando só a função de recusa, sem rodar nenhum programa:

  | Caminho | O que a regra faz |
  |---|---|
  | `\\?\UNC\localhost\C$\...` | recusa (certo) |
  | letra de disco minúscula | recusa (certo) |
  | `C:/Windows` com barra | recusa (certo) |
  | `C:\Windows\..\Windows\...` | recusa (certo) |
  | espaço ou ponto no fim | recusa (certo) |
  | uma junção minha no rascunho apontando para a pasta do sistema | recusa (certo); depois tirei só a junção, e a pasta do sistema continua inteira |
  | `\\?\GLOBALROOT\SystemRoot\System32\schtasks.exe` | **aceita** (achado T1) |
  | `\\?\Volume{...}\Windows\System32\schtasks.exe` | **aceita** (achado T1) |

  Os dois aceitos são o mesmo arquivo da pasta do sistema (conferido com `os.path.samefile`).
- **A conferência da pasta do Agendador (N3), com as licenças de verdade deste PC** (só leitura).
  - Conferem: `\Microsoft` (dono: o sistema), `\GoogleSystem`, `\PowerToys` e `\Remediation` (dono: Administradores).
  - Não conferem: `\SoftLanding` e `\GoogleUserPEH` (dono: a conta comum; a `\SoftLanding` dá controle total a
    "Todos").
  - A regra separa certo o que um administrador cria do que uma conta comum cria.
- **A pasta criada entre a conferência e a criação da tarefa.** Li o código, não testei de verdade.
  - A conferência de antes não fecha essa janela de tempo.
  - A de depois fecha. Depois de criar, a peça confere a pasta de novo e, se ela não for segura, apaga a tarefa e
    confere que sumiu.
  - O pior caso: uma conta que criou a pasta nesse segundo e negou aos administradores o acesso às tarefas dela. Aí a
    peça não consegue apagar, e a resposta diz com todas as letras "NÃO deu para apagar: ela ficou no Windows". A
    tarefa que fica é a nossa, que roda o nosso script. Pela minha leitura, uma conta comum não consegue registrar de
    novo uma tarefa que roda como o sistema; não provei isso.
  - Essa conferência de depois não tem teste (T2).
- **O Agendador continua como estava:** a pasta `\EditorImpressao` não existe neste PC.

## Cada destino da segunda volta

- **N1, a prova do "Não" lido do jeito certo: consertado.** Uma função da peça diz se cada uma das 6 bibliotecas
  guarda o erro de cada chamada, e o teste cobra as 6. As mutações M2 e M2b são acusadas.
- **N2, o caminho escrito de outro jeito: consertado em parte.**
  - Os casos que a gerente pediu para olhar estão todos recusados.
  - Ficaram dois jeitos de escrever o caminho (achado T1).
  - O apelido do que tem "_" no nome (N2, parte b) ficou com a gerente, no porteiro. É um destino aceitável.
  - Programa de fora do Windows ficou escrito na peça como decisão de cada passo. Também é aceitável.
- **N3, a pasta do Agendador criada antes por outra conta: consertado.**
  - A pasta é conferida antes e depois de criar a tarefa, e a regra acerta nas pastas de verdade deste PC.
  - A conferência de depois não tem teste (T2).
- **N4, o teste que chamava `schtasks /Create` no PC: consertado.** O teste agora só cria a tarefa no Windows do
  GitHub.
- **A frase da pasta do Agendador: consertada.** Ela nunca mais diz "foi apagada" quando a pasta não foi criada, e há
  teste.
- **As mutações que passavam (A1b, A1c, A2, A6, A6b, A9, A9c):** agora todas têm teste, menos A1b, que só o GitHub
  prova.
- **Os nomes das contas, achado pelo GitHub: consertado.**
  - O nome sai por `nome_para_mostrar()`, num lugar só. Nenhuma frase da peça mostra mais o número cru da conta: sem
    nome, sai "outra conta deste computador".
  - Detalhe das frases no achado T3.

## Achados novos

**T1. BAIXO a MÉDIO, conta nos passos 3 a 5: dois jeitos de escrever o caminho ainda passam pela recusa.**
- Os caminhos: `\\?\GLOBALROOT\SystemRoot\System32\schtasks.exe` e `\\?\Volume{...}\Windows\System32\schtasks.exe`.
- Lugar: `core/windows.py`, `_caminho_do_programa`. Essa função tira o prefixo `\\?\` antes de resolver o caminho.
  Sem o prefixo, o resto vira um caminho relativo, que não fica dentro de `C:\Windows`.
- Conferi: resolver o texto inteiro, **antes** de tirar o prefixo, dá `\\?\C:\Windows\System32\schtasks.exe` nos
  dois casos (`os.path.realpath`).
- Sugestão: resolver primeiro e tirar o prefixo depois. Ou comparar o arquivo de verdade, e não o texto.
- Para usar esse buraco, é preciso escrever o caminho assim de propósito. Não muda nada na sessão A.

**T2. BAIXO: a conferência da pasta do Agendador depois de criar a tarefa não tem teste.**
- Lugar: `core/windows.py`, em `criar_tarefa`, o trecho "if lida.existe: depois = conferir_pasta_de_tarefas()".
- Desliguei esse trecho na cópia e todos os testes passaram.
- É ela que cobre a pasta criada no meio. Dá para provar só a lógica em volta: a pasta "não existia antes" e "existe e
  não é segura depois", com a criação da tarefa trocada por uma de mentira (D-767 permite isso para a lógica).

**T3. BAIXO: as frases novas.**
- Nenhuma tem número de conta, nem código interno, nem número de decisão.
- Três detalhes de texto:
  - **Concordância:** "Todos pode mexer na pasta do programa no Agendador" e "Administradores pode..." deviam ser
    "podem".
  - **Nome com a máquina:** uma conta comum aparece como o Windows a escreve, com o nome do computador na frente
    ("SAMUEL-PC\fotog"). É um nome, não um código, mas fica mais técnico que o resto.
  - **Contas de fábrica fora da lista:** as que não estão em `_NOMES_DE_FABRICA` (Convidados, Rede, Serviço,
    Operadores de cópia...) continuam saindo na língua do Windows. Hoje nenhuma delas aparece nas pastas que a peça
    lê.
- Fora das frases novas: frases antigas da peça ainda trazem o número do erro do Windows. Exemplos: "o Windows
  respondeu 0x…" (o número em hexadecimal), "o Windows respondeu com erro (código 1)", "saiu sem começar (código 7)".
  - Hoje só a janela de prova mostra essas frases.
  - Quando a tela do Kaique usar a peça (passos 3 e 4), essas frases precisam passar pela regra de "nenhum código"
    (CLAUDE.md §11.13).

## As regras que conferi

- **§4.7, reversão:** o anexo dele confere com as três mutações que eu mesmo fiz. A de depois é o T2.
- **§11.12:**
  - ponto 1, uma peça só: T1;
  - ponto 2, nada dá como feito sem conferir: a tarefa e a pasta do Agendador são lidas de volta;
  - ponto 3, a lista das falhas: a pasta criada no meio está coberta pela conferência de depois;
  - ponto 4, peça de mentira: o teste que criava tarefa no PC foi para o GitHub.
- **§11.13, as frases:** T3.
- **D-605:** `main.py` e `regras_dos_agentes/` sem mudança.
- **D-785:** nada rodou com licença. A junção que criei ficou no rascunho, apontou para a pasta do sistema só para a
  função ler, e foi tirada.
- **D-798:** sem o rótulo até a prova à vista.

## O que falta

1. A gerente dar destino a T1, T2 e T3: consertar agora, ou levar ao pacote do passo 3.
2. A gerente montar o programa no C:, à vista.
3. A sessão A, com as 3 perguntas do Windows e o registro da janela guardado.
   - Pela leitura, a pergunta vai mostrar "EditorImpressao.exe". Pelo plano, isso para a sessão na pergunta 1.
4. Depois disso, com cada achado com destino, cabe "PRONTO PARA CONFERIR". Nunca "aprovado".

## Para a gerente: o que ficou fora do projeto

- No rascunho
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\`)
  ficou mais isto, nada apagado:
  - a cópia `copia-reversao-3\`;
  - os scripts `regra_pasta2.py`, `regra_pasta3.py` e `pasta_agendador_real.py`.
- A junção `juncao-para-o-sistema`, que eu mesmo criei no rascunho, foi tirada sozinha, com `os.rmdir`, que tira só o
  atalho. Conferi que a pasta do sistema continua inteira.
- Nada mudou no Windows.
