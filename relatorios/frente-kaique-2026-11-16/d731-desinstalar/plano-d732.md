# Plano D-732: procurar a versão nova quando o programa abre

**O que é.** O Samuel decidiu em 17/11 que a versão nova é procurada quando o programa abre, como os aplicativos
fazem, e não mais quando o computador liga ("não, faz quando o programa é aberto"). Este plano diz como isso funciona
com o programa em Arquivos de Programas, instalado pelo `.msi` "para a máquina toda", com os ganchos do instalador sem
licença de administrador (achado B1, conferido pela gerente).

**Situação.** Só plano (D-709). Nenhum arquivo do programa ou dos testes mudou e nada foi feito no Windows. Completa o
`plano.md` desta pasta (D-731).

## 1. O que o Velopack 1.2.161 faz quando a pasta do programa pede administrador

Conferido nos textos de dentro do `Update.exe` do `vpk` 1.2.161 (`vendor/update_x64.exe`) e do `velopack.pyd` do
`.venv`, que usam o mesmo código para achar as pastas:

- **Onde baixa.** O `velopack.pyd` e o `Update.exe` primeiro conferem se a pasta do programa aceita gravação ("Root
  directory '...' writable"). Se não aceita, usam uma pasta do próprio usuário: "Using fallback directory", "Copied
  Update.exe from root to fallback", "Root directory is not writable and LocalAppData is unavailable".
  - Quando é o Kaique que procura, **baixa sem pedir nada**, numa pasta dentro do `LocalAppData` dele.
  - O nome exato da pasta não aparece nos textos. O nome do pacote é `EditorImpressao`, igual ao da pasta dos
    projetos (`%LOCALAPPDATA%\EditorImpressao`). É possível que os pacotes caiam dentro dela. Isso se confere na
    etapa 5, no registro do Velopack.
- **Quando troca.** Trocar os arquivos em Arquivos de Programas precisa de administrador. O `Update.exe` mesmo pede a
  licença:
  - ele anota "Re-launching as administrator to update in ...";
  - abre a si mesmo pela pergunta do Windows (`runas`), com `apply --norestart --package --rootDir`;
  - espera até 10 minutos ("Waiting (up to 10 minutes) for elevated process");
  - depois reabre o programa sem administrador.
  - Antes da pergunta do Windows, ele pode mostrar uma janela dele, em português: "O Editor de Impressão precisa de
    permissão de administrador para instalar a versão ...". Com o `silent=True` que o programa usa, talvez não
    mostre (a conferir na etapa 5).
- **Quantas perguntas por atualização, sem a tarefa.**
  - **Uma** pergunta "Deseja permitir...?" a cada atualização. O editor aparece como "desconhecido", porque não há
    certificado pago (D-724).
  - **Mais uma** se a versão nova falhar e o programa voltar para a anterior (D-718), porque a volta também troca
    arquivos.
  - Se o Kaique disser "Não", a troca não acontece e ele continua na versão que tem.
- **O ensaio da etapa 3 não passou por isso.** Ele usou um pacote portátil, numa pasta que aceita gravação.

**A tarefa do Windows ainda serve para alguma coisa?** Tudo o que precisa de administrador precisa de um momento com
administrador. Os ganchos do instalador não têm (B1).
- Tirar o Inno antigo (D-723): precisa, uma vez.
- Instalar o Visual C++ que vai no pacote (D-727): precisa, uma vez.
  - Falta conferir se o programa abre antes disso, só com as DLLs que vêm dentro dele. Se não abrir, a pergunta tem
    de vir antes da janela.
- A volta se falhar (D-718): precisa, a cada volta.
- Trocar a versão: precisa, a cada atualização.
- A tarefa faria tudo isso sem perguntar, porque roda como o sistema. Mas o gancho não consegue criá-la (B1), e ela
  não pode mais esperar o computador ligar (D-732).

## 2. As alternativas (recomendo a B)

**A. A pergunta do Windows a cada atualização, sem tarefa.**
- Para o Kaique:
  - ao abrir, a versão nova é procurada e baixada por trás, sem perguntar nada;
  - para entrar, o Windows pergunta "Deseja permitir...?";
  - na primeira abertura, mais uma pergunta, para o Visual C++ e para tirar o Inno (junta com a da senha dos testes,
    quando ele a puser).
- Decisões que mudam:
  - D-723: a tarefa sai;
  - D-718: a volta pede outra pergunta;
  - D-720: o "Depois" precisa de um jeito novo;
  - D-722: a lista muda;
  - D-731: fica a pergunta do "Não" ao desinstalar (seção 3).
- O que precisa de cuidado:
  - a conta de testes (D-717) não pode procurar nem trocar versão, porque ninguém responde à pergunta numa sessão de
    longe;
  - o download vai para o `LocalAppData` de cada conta.
- É o jeito do instalador "para todos os usuários" do VS Code.

**B. Recomendada: um ajudante do Windows faz a troca sem perguntar, chamado pelo programa ao abrir.**
- A mesma tarefa da etapa 3, como o sistema, com três diferenças:
  - não roda mais quando o computador liga;
  - o programa a chama quando abre e quando fecha;
  - ela é criada na primeira abertura, numa pergunta só do Windows, junto com o Visual C++, o Inno e, se houver
    senha, os testes à distância.
- A tarefa recebe uma licença para que a conta do Kaique possa mandá-la rodar. Ela só roda o nosso `.exe` de
  Arquivos de Programas, com argumentos fixos, e só aceita versão assinada (D-724).
- Para o Kaique:
  - uma pergunta na primeira abertura;
  - depois, **nenhuma** a cada atualização, nem na volta se falhar;
  - o aviso "Reiniciar agora / Depois" fica igual.
- Decisões que mudam: só o que a D-732 já mudou.
  - D-714: deixa de procurar ao ligar o computador;
  - D-720: o "Depois" precisa de um jeito novo;
  - D-723: a tarefa é criada na primeira abertura, e não na instalação.
  - Ficam como estão: D-715, D-718, D-719, D-722 (a lista continua com a tarefa) e D-727.
- O que precisa de cuidado:
  - no "Reiniciar agora", quem reabre o programa é a conta do Kaique, depois que a tarefa terminar. A tarefa roda como
    o sistema e não pode abrir a janela;
  - a conta de testes não chama a tarefa: os testes rodam na versão que o Kaique tem.
- É o jeito do Chrome e do Edge "para a máquina toda", que usam um ajudante do sistema.
- **De quebra resolve a D-731 sem pergunta nova.** O `ligar` cria uma segunda tarefa, "desfazer os testes à
  distância", que roda como o sistema e que a conta do Kaique pode mandar rodar. O script dela fica numa pasta que só
  o administrador grava. O gancho de desinstalar só manda essa tarefa rodar: sem segunda pergunta e sem o problema do
  "Não". O caderninho do "antes" e o `plano_de_desfazer` do `plano.md` ficam iguais.

**C. Instalar só para a conta do Kaique, fora de Arquivos de Programas (o padrão do Velopack, como o Discord).**
- Para o Kaique: nunca pergunta nada nas atualizações. O Visual C++, o Inno e os testes à distância ainda pedem
  administrador uma vez.
- Decisões que quebram:
  - **D-717 / D-705:** a conta de testes não enxerga a pasta do Kaique, então não consegue abrir o programa. Os testes
    à distância deixam de funcionar sem uma segunda cópia do programa para ela;
  - D-723 (Arquivos de Programas).
- Risco grave: a pasta seria `%LOCALAPPDATA%\EditorImpressao`, a mesma dos projetos. Desinstalar apaga a pasta do
  programa inteira. Só dá para usar trocando o nome do pacote antes da etapa 6.
- Não recomendo.

**D. Arquivos de Programas com a pasta liberada para todos gravarem.** Nunca pergunta, mas qualquer programa da conta
do Kaique poderia trocar o nosso `.exe`. Não recomendo.

## 3. Como ficam B1 a B4 e a D-731

- **B1** (os ganchos sem administrador): deixa de ser defeito a consertar no gancho. Em A e em B, o que pede
  administrador vai para a pergunta da primeira abertura. O `ao_instalar` deixa de tentar criar a tarefa. O
  `ao_atualizar` também (hoje ele refaz a tarefa a cada versão; em B isso passa para a própria tarefa).
- **B2, B3, B4** (`sshd_config` dentro do bloco "Match", ligar depois de desligar, desligar um OpenSSH que é do
  dono): não mudam. Continuam na Lista de bugs.
- **D-731:**
  - em A: o plano do `plano.md` fica como está, com a segunda pergunta do Windows ao desinstalar e a pergunta do "Não";
  - em B: a tarefa "desfazer" troca a segunda pergunta, e a pergunta do "Não" deixa de existir.

  O resto do `plano.md` vale nos dois: caderninho, marcas, perfil pelo SID e provas.
- Achado novo: o nome do pacote `EditorImpressao` é igual ao da pasta dos projetos. Isso pesa nas alternativas A e C.
  O nome se troca antes da etapa 6, se a etapa 5 mostrar a mistura.

## 4. Perguntas que só o Samuel responde

1. Para a versão nova entrar no notebook do Kaique, qual jeito?
   - (B, sugestão) um ajudante do Windows troca sozinho: o Kaique responde uma pergunta do Windows na primeira vez
     que abre o programa e nunca mais;
   - (A) o Windows pergunta "Deseja permitir...?" a cada atualização, e mais uma vez se ela falhar e voltar;
   - (C) instalar só para a conta dele, sem perguntas, mas aí os testes à distância não conseguem abrir o programa.
2. No aviso da versão nova, com "Depois", quando ela entra?
   - (sugestão) quando ele fechar o programa: ao abrir de novo, já é a nova;
   - ou na próxima vez que ele abrir, com uma espera curta antes da janela.
3. A pergunta do Windows na primeira abertura aparece sempre, mesmo sem a senha dos testes?
   - (sugestão) sim, porque prepara o computador (o Visual C++, a instalação velha) e, se houver senha, liga os testes
     na mesma pergunta;
   - não: aí o Visual C++ e a instalação velha ficam sem jeito de entrar.
4. Quando o Samuel testa de longe, o programa procura versão nova?
   - (sugestão) não: os testes rodam na mesma versão que o Kaique tem, e nada troca no meio de um teste;
   - sim: o teste pode trocar a versão do Kaique.
5. Só se for a opção A: ao desinstalar, se o Kaique disser "Não" à segunda pergunta, o que fica?
   - (sugestão) o programa sai, o comando de longe fica, e isso fica anotado; para tirar, instala e desinstala de
     novo;
   - ou uma janelinha avisa o Kaique.
   - Na B essa pergunta não existe.

## 5. O que só a etapa 5 prova

- A pergunta do Windows no `apply` do Velopack, e se a janela dele aparece com `silent=True`.
- A pasta onde ele baixa, e se ela cai dentro da pasta dos projetos.
- Se o programa abre antes do Visual C++.
- Em B: que a conta do Kaique consegue mandar a tarefa rodar e que o "Reiniciar agora" reabre o programa na conta
  dele.
