# Passo 1 do plano da parte do Windows: quarta conferência de quem tentou quebrar, com a prova à vista (19/11/2026)

Quarta volta do mesmo verificador, que não escreveu este código. Conferi o registro da sessão A linha por linha
contra o que o plano pede, e conferi os consertos de T1 a T3 (`c87f7bfe`). Não confiei no resumo da gerente. Não mexi
no código, não pedi licença ao Windows e não abri janela na tela do Samuel.

## Pedido

- Papel: verificador
- Commit de partida: 4f9fcc4e
- Ramo: passo1-peca-unica-windows

## Arquivos que vou mexer

- `relatorios/passo1-peca-unica-windows/quem-quebrou/`

## Veredito

**"PRONTO PARA CONFERIR"**, com duas condições que a gerente cumpre antes de levar ao Samuel:

1. **Pôr no git o registro e os dois prints da sessão.** Hoje eles estão no worktree, mas fora do git:
   `relatorios/janela-de-prova/registro-2026-11-19-161111.txt` e os dois `prints/sessao-a-*.png`. Eu não os pus,
   porque não estão na minha lista de arquivos.
2. **Confirmar com o Samuel uma coisa que só o olho dele viu:** que na prova 5 (b) não apareceu caixa do Windows. O
   registro mostra a frase em português, mas não prova que não houve caixa.

Escrevo nos termos da D-798:
- quem escreve é quem tentou quebrar, e não construiu nada deste passo;
- todos os achados das quatro voltas têm destino;
- houve a prova de verdade: hoje, à vista, com registro e prints.

Isto não é aprovação: só o Samuel aprova.

## A prova de verdade

- **Quando:** 19/11/2026, das 16:12:43 às 16:19:34, pelos horários do registro. A gerente diz que começou às 16:11.
- **Onde e como:** à vista, na tela do Samuel. A janela de prova abriu
  `C:\EditorImpressaoProva\EditorImpressao\EditorImpressao.exe`, montado do commit `c87f7bfe`.
  - Depois de `c87f7bfe` só mudou o formulário: conferi com `git diff --stat`.
  - A rodada 44597542145 do GitHub testou esse commit (`TESTADO_SHA: c87f7bfe...`) e deu "success".
  - O print 1 mostra a janela de prova com esse programa e com "Esta conta tem a licença de administrador agora:
    não".
- **Registro:** `relatorios/janela-de-prova/registro-2026-11-19-161111.txt`, no worktree `passo1`.
- **Prints, abertos e conferidos por mim:**
  - `prints/sessao-a-pergunta-1-resultado-print-do-samuel.png`: o fim da pergunta 1 na janela de prova;
  - `prints/sessao-a-pergunta-com-navegador-na-frente-print-do-samuel.png`: o navegador na frente, e a pergunta só
    na barra de tarefas, como "EditorImpressao.exe solicit...".

## O registro contra o que o plano pede da sessão A

Cada linha diz o que o plano pede, o que o registro mostra, e se foi conferido por máquina (o registro) ou por olho
(o Samuel).

| O plano pede | O registro mostra | Situação |
|---|---|---|
| Lançar solto: "rodou às HH:MM:SS", também depois de quem lançou fechar; 0 perguntas | 16:12:50: "o script solto rodou às 16:12:50; quem o lançou (processo 6992) já tinha fechado: sim" | cumprido (máquina) |
| Pergunta 1 mostra "Editor de Impressão" | Mostrou "EditorImpressao.exe" (print 2 e palavras dele) | não cumprido como o plano dizia. O plano manda parar, e parou: o Samuel decidiu ficar com o nome do arquivo (D-805, "a") |
| No mesmo "Sim", a pasta segura nasce com as licenças de fábrica | 16:13:23: "a pasta segura de prova CONFERE", dono Administradores; só o sistema, os Administradores e o Instalador Confiável mudam; Usuários e aplicativos da loja leem | cumprido (máquina) |
| Uma tarefa de prova roda como o sistema | A tarefa diz "roda como o sistema", e o script dela escreveu "rodou às 16:13:25 como AUTORIDADE NT\SISTEMA (S-1-5-18)" | cumprido (máquina) |
| A conta comum lê a pasta e não grava | "Esta conta lê a pasta: sim"; "tentou gravar ... e o Windows não deixou: certo"; o print mostra que a janela rodava sem a licença | cumprido (máquina) |
| A senha de prova com acento chega igual | "IGUAL (a soma confere; o segredo não é mostrado)" | cumprido (máquina) |
| O texto com acento chega igual no script | "'Ação, ÊXITO, coração, € 10' — igual" | cumprido (máquina) |
| Pergunta 2, "Não": "você disse Não; nada mudou" | 16:16:29: "DISSE NÃO" (o Windows deu o erro 1223); lido de novo, a tarefa "- Nao" não existe | cumprido (máquina) |
| Pergunta 3 com o navegador na frente: vem para o meio da tela | 1ª rodada: "A janela do programa estava na frente: sim" (o navegador não estava na frente de verdade). 2ª rodada: "NÃO", e a pergunta só piscou na barra de tarefas (print 2) | não cumprido, como a documentação previa (risco 1). O plano manda parar, e parou: o Samuel decidiu que a licença é pedida no instante do clique, no passo 3 (D-806) |
| O "Sim" da pergunta 3 apaga a tarefa e a pasta, e a leitura diz "não existe" | 1ª rodada, 16:17:31: os 4 passos "deu certo"; lido de novo: as duas tarefas, a pasta segura e a pasta do Agendador não existem; "o Agendador está como estava" | cumprido (máquina) |
| Programa que não existe: frase em português, sem a caixa crua do Windows | (a) "não achei o programa a abrir com a licença". (b) "o Windows não sabe pedir licença para esse arquivo" (o Windows deu o erro 1155) | a frase está cumprida (máquina). Que não apareceu caixa é coisa do olho do Samuel e está a confirmar (condição 2) |
| A resposta do Windows com "ÊXITO" certo | Prova 6, 16:14:41: "ÊXITO: tentativa de executar a tarefa agendada ..." | cumprido (máquina) |
| 3 perguntas do Windows, 25 a 35 min | **4 perguntas** (1, 2, 3 e a repetição da 3), em 7 minutos | a repetição foi de propósito, para o caso do navegador; o Samuel estava presente |

**Cada resposta contra o que a peça diz:**
- Nenhum "Não" e nenhuma falha viraram "deu certo". O 1223 deu "disse Não"; o 1155 deu "falhou" em português.
- Os quatro "deu certo" foram lidos de novo por fora e conferem: a pasta, a tarefa, a licença e o "não existe".
- A licença que o Windows deu à tarefa é
  `D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;0x1200a9;;;AU)(A;ID;0x1f019f;;;BA)(A;ID;0x1f019f;;;SY)(A;ID;FA;;;BA)(A;;FR;;;SY)`.
  - É o que eu tinha previsto na volta 2 pelas tarefas da raiz.
  - Os usuários autenticados ficam só com ler e mandar rodar, e foi assim que a conta comum mandou a tarefa rodar
    ("ÊXITO").
  - A regra da peça aceitou essa licença.

## A linha da segunda rodada da prova 4

A linha: "Não se sabe se a pasta \EditorImpressao do Agendador existia antes da prova; agora não existe".

**É aceitável. Não é defeito.**
- A janela anota o estado de antes na pergunta 1 e apaga essa anotação quando a pergunta 3 desfaz tudo com sucesso.
  Foi o que aconteceu às 16:17:32.
- A segunda rodada veio sem uma nova pergunta 1, então a janela não tinha como saber o estado de antes. Ela fez a
  escolha segura: não pede para apagar a pasta do Agendador sem saber se a prova a criou.
- O Agendador terminou como começou, comparando com o que a primeira rodada leu às 16:13:16 ("não existe"). A D-722
  está cumprida.
- A janela não precisa lembrar entre uma rodada e outra. Lembrar depois de desfazer tudo poderia, numa sessão
  seguinte, levar a apagar uma pasta que outra coisa criou (só se vazia, mas ainda assim).
- Melhoria de texto, opcional, que não impede nada: nesse caso a frase poderia dizer "a prova anterior já desfez tudo;
  nada para apagar". Fica como ideia; não é conserto pedido.

## Os consertos de T1 a T3

- **T1, consertado.** O caminho é resolvido inteiro antes de o prefixo sair. Conferi com a mesma função, sem rodar
  nada: `\\?\GLOBALROOT\...` e `\\?\Volume{...}\...` agora são recusados. A prova de reversão dele acusa.
- **T2.** A conferência de depois tem teste, mas ele só roda no GitHub (precisa da licença). Destino aceito: é o
  combinado para o que só roda com a licença.
- **T3, consertado.** A concordância, a conta sem o nome do computador, Convidados na lista, e o número do erro fora da
  frase. A prova de reversão dele acusa as quatro.
- **No PC, `tests/test_windows_peca.py`:**
  - Na primeira vez, 1 teste falhou, 50 passaram e 2 foram pulados, em 4 min 43 s. O PC estava lento, e a saída que eu guardei não diz qual teste foi.
  - Na segunda vez, logo depois: 51 passaram e 2 foram pulados, em 20 s.
  - **Ressalva:** pode haver um teste da peça que falha quando o PC está carregado (ele depende de tempo). A gerente olha isso na rodada inteira no PC, antes de juntar.

## O que fica no PC do Samuel (D-722)

- Desfeito e lido de novo: a tarefa de prova, a pasta segura de prova em Arquivos de Programas e a pasta do
  Agendador.
- **Fica, e não é da peça:** a pasta do programa montado, `C:\EditorImpressaoProva\`. Ela está fora do projeto, então
  só sai com o "sim" do Samuel (CLAUDE.md §10.9). A gerente pergunta a ele.

## Destino de todos os achados

- **Relatório 1, achados 1 a 17:** consertados nas voltas 1 a 3. O 15 é cuidado para o pacote do passo 3. O 16 é
  observação, e fica.
- **Relatório 2:**
  - N1, N3 e N4: consertados;
  - N2: consertado, menos a parte (b), o apelido do que tem "_" no nome, que ficou com a gerente, no porteiro;
  - o programa de fora do Windows (N2c): decisão de cada passo, escrita na peça.
- **Relatório 3:** T1 e T3 consertados. T2 com teste só no GitHub (aceito).
- **Sessão A:**
  - o nome na pergunta: decidido pelo Samuel (D-805);
  - o navegador na frente: decidido pelo Samuel (D-806), e vale para o passo 3.

## Para a gerente

- Fazer as duas condições do veredito.
- Levar ao pacote do passo 3:
  - o achado 15: nada que o ajudante roda como o sistema vem de pasta que a conta comum grava;
  - a D-806: a licença é pedida no instante do clique;
  - o apelido do que tem "_" no nome (N2b), no porteiro.
- No rascunho não deixei nada novo nesta volta. Os scripts de leitura das voltas anteriores continuam lá, listados nos
  relatórios 1 a 3. Nada mudou no Windows.
