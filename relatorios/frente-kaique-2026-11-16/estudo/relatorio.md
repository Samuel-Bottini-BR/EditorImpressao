# Atualização sozinha e testes à distância: o estudo

**O que é:** o estudo que você pediu antes de mexer no programa, para deixar o notebook do Kaique pronto. Ele
responde duas coisas: com qual ferramenta pronta o programa vai se atualizar sozinho pela internet, e como o programa
liga e desliga os testes que você vai fazer de longe no notebook dele. **Nada do programa mudou.** Nada foi instalado
no Windows. Feito em 16/11/2026.

**Situação de agora:** só estudo. Falta você escolher a ferramenta e o tipo de assinatura (no fim). Depois disso vem a
parte de empacotar e instalar numa pasta de teste, e só então a construção, com o plano que está no fim desta página.

Não há prints aqui porque nenhuma tela mudou ainda. Os prints vêm quando houver a janela do aviso e a opção nas
Configurações.

---

## 1. A atualização sozinha

**O que o Kaique vai ver.** Na primeira vez, ele instala como hoje. Depois, nunca mais instala nada. Toda vez que o
notebook liga, o programa procura a versão nova por trás, sem janela. Se o programa estiver fechado, a versão nova
entra ali mesmo, e na próxima vez que ele abrir já é a nova. Se estiver aberto, aparece o aviso para salvar e
reiniciar, com "Reiniciar agora" e "Depois". Os livros e os projetos dele nunca são tocados: ficam numa pasta à parte,
que a atualização não mexe.

**A ferramenta recomendada: Velopack.** É de graça e de código aberto (licença MIT, que só pede manter o aviso de
quem fez). Está sendo atualizada: a última versão é de setembro de 2026. É a continuação do atualizador que o Slack e
o Discord usaram.

Por que ela:

- Funciona com o nosso Python e com o jeito que o programa é empacotado hoje. Eu instalei e abri ela num teste à parte.
- Baixa só os arquivos que mudaram. Se só o programa mudou, o detector de linhas (a parte de 1,2 GB) não é baixado de
  novo.
- Troca a versão de uma vez só. Se a troca der errado no meio, ela devolve a versão anterior sozinha. Isso eu li no
  código dela.
- Busca as versões direto no GitHub do projeto, sem senha nenhuma dentro do programa.

**A outra candidata séria: tufup.** Também é de graça. Tem uma assinatura muito boa, conferida pelo próprio programa.
Mas tem três problemas para nós:

- Com o nosso Python, ela só instalou depois de eu compilar uma peça à mão.
- Ela copia a versão nova por cima da velha. Se parar no meio, o programa fica metade novo, metade velho, e não volta.
- O "baixar só o que mudou" dela é feito no programa inteiro de uma vez. Com 1,9 GB, isso leva horas. Na prática, o
  Kaique baixaria uns 600 MB a cada versão.

**As que ficaram de fora.** O PyUpdater foi abandonado em 2022. O WinSparkle baixa o instalador inteiro e só funciona
com o programa aberto. O jeito do Windows (o mesmo que o Slack usa hoje) instala o programa separado para cada pessoa
do computador, e aí a conta dos seus testes não teria o mesmo programa do Kaique.

**Como os programas grandes fazem a atualização quando o computador liga.** O Chrome e o Edge deixam uma tarefa do
Windows que roda quando o computador liga, com licença do próprio sistema, e por isso não perguntam nada a ninguém.
Nenhuma ferramenta pronta faz essa parte sozinha: em todas, é uma tarefa do Windows. O instalador cria essa tarefa uma
vez, na primeira instalação, aproveitando a licença que o Kaique já dá ao instalar.

**O que muda com o Velopack, além da atualização:**

- O instalador de hoje é trocado pelo instalador do próprio Velopack. O Kaique continua vendo uma instalação comum, no
  mesmo lugar do computador.
- A peça da Microsoft que o programa precisa (o Visual C++) passa a ser baixada da internet na instalação, em vez de ir
  dentro do instalador.
- O Kaique já tem o programa instalado (o de 28/10). A primeira instalação nova precisa tirar a antiga antes, para não
  ficarem dois.
- Quando ele clicar em "Reiniciar agora", o Windows pode perguntar "Deseja permitir que este aplicativo faça
  alterações?". Vou tentar evitar essa pergunta no plano; se não der, é só ele clicar em "Sim". Com "Depois", não
  aparece pergunta nenhuma.

**O que eu não consigo garantir com nenhuma ferramenta.** Se a versão nova se instalar certinho, mas tiver um defeito
nosso que a impeça de abrir, nenhuma das duas volta sozinha. O plano resolve isso assim: depois de instalar, o
programa faz um teste rápido escondido. Se falhar, ele pede a versão anterior ao próprio Velopack, que tem esse
recurso. Aí aparece para o Kaique: "A atualização não deu certo. O programa voltou para a versão anterior e continua
funcionando. Avise o Samuel."

## 2. A assinatura que prova que o arquivo é nosso

Você decidiu que a versão vem do GitHub com uma assinatura. Com o Velopack, isso tem um detalhe.

O que o Velopack já faz sozinho: confere se o arquivo chegou inteiro. Isso **não** prova que é nosso. Se alguém
entrasse na conta do GitHub, poderia publicar uma versão falsa, e ela também chegaria "inteira".

Há dois jeitos de provar que é nosso:

- **De graça:** o seu PC assina cada versão com uma chave que só ele tem. O programa do Kaique leva só a parte
  pública da chave e confere antes de instalar. É o mesmo método que o Mac usa nos programas dele e que o tufup usa.
  Ninguém mais consegue fazer uma versão que passe.
- **Pago:** um certificado de assinatura do Windows. Ele tira o aviso "editor desconhecido" e faz os antivírus
  desconfiarem menos. Tem custo todo ano e pede comprovar identidade. O serviço barato da Microsoft (10 dólares por
  mês) não aceita pessoas do Brasil. Existe um serviço grátis para programas de código aberto, mas ele exige que o
  programa seja montado inteiro no GitHub, e hoje partes dele são montadas no seu PC.

## 3. Os testes à distância

**O que o Kaique vai ver.** Na primeira vez que abrir o programa novo, uma janela pequena pede "a senha dos testes à
distância". Ele digita a que você passar. Logo depois, o Windows faz **uma** pergunta: "Deseja permitir que este
aplicativo faça alterações no seu dispositivo?". Ele clica em "Sim", e está pronto. Se clicar em "Não", nada é
instalado, os testes ficam desligados, e dá para ligar depois nas Configurações. Ele não vê mais nada: nem a conta de
testes na tela de entrada, nem janela do programa quando você testa de longe.

**O que o programa faz com esse "Sim", tudo com o que o próprio Windows traz:**

- instala o comando de longe do Windows (Servidor OpenSSH);
- deixa ele ligando sozinho com o Windows;
- fecha a porta para todo mundo e abre só para a rede do Tailscale, nem o Wi-Fi da casa entra;
- cria a conta só dos testes, sem poder de administrador, com a senha digitada, escondida da tela de entrada;
- deixa entrar por ali **só** essa conta (nem a conta do Kaique entra de longe).

**Home ou Pro.** Não se sabe qual Windows o notebook tem. Não faz diferença: tudo isso existe no Windows 11 Home e no
Pro.

**Prioridade baixa ou normal.** O Windows faz isso sozinho: quando um programa começa em prioridade baixa, tudo o que
ele abre por baixo também fica em baixa. Basta o seu pedido de teste começar em baixa (ou normal, se você disser).

**Desligar.** Na opção das Configurações: o comando de longe para, deixa de ligar com o Windows, a porta fecha, e a
conta de testes fica desativada, com os projetos de teste guardados.

**Os riscos, sem esconder:**

- **Parece vírus.** Conta escondida, mais porta de comando, mais regra de firewall, é exatamente como um vírus de
  acesso remoto trabalha. O antivírus do notebook pode reclamar ou bloquear. Ajuda ter a opção à vista nas
  Configurações e o programa assinado.
- **Senha.** Só quem está na sua rede do Tailscale chega até a porta. Lembrete: o Tailscale do seu PC está entrando
  na conta do servidor de livros, então quem estiver nessa rede também chega à porta (ainda precisa da senha).
- **Pastas fora da conta.** A conta de testes não enxerga a pasta pessoal do Kaique. Mas pastas soltas no disco (por
  exemplo uma pasta de livros direto no disco) costumam ficar abertas para qualquer conta. O teste final tem de olhar
  onde ele guarda os livros.

**Como fazem os programas de suporte remoto** (TeamViewer, AnyDesk). Eles não abrem porta: o computador liga para
fora, num servidor deles. Usam uma senha que o dono define. E mostram um aviso na tela enquanto alguém está conectado.
O nosso jeito também não abre porta para a internet (o Tailscale faz o papel do servidor do meio) e não mostra a tela
do Kaique, só roda comandos. O que eles têm e o nosso não: o aviso visível de "alguém está conectado".

---

## O que você escolhe

**Pergunta 1. Qual ferramenta de atualização?**

- **Velopack (sugestão).** Volta sozinho se a troca falhar, baixa só o que mudou, já lê o GitHub. Muda o instalador.
  Nada do que já funciona no programa muda.
- **tufup.** Mantém o instalador de hoje e tem a assinatura completa pronta. Mas não volta se falhar no meio, e o
  Kaique baixa uns 600 MB por versão.
- **Só comentário.**

**Pergunta 2. Que assinatura?**

- **A de graça, conferida pelo programa (sugestão).** Prova que a versão é sua. Não tira o aviso "editor
  desconhecido" do Windows.
- **A de graça mais um certificado pago do Windows.** Prova que é sua e tira o aviso. Tem custo todo ano e precisa
  comprovar identidade. Dá para acrescentar depois, se o antivírus do Kaique reclamar.
- **Só comentário.**

**Ainda não decidido, para depois:** o que acontece com a conta de testes e o comando de longe se um dia o programa for
desinstalado do notebook.

---

## O plano das próximas etapas (com o Velopack)

Cada etapa só começa com o seu "sim". Nenhum agente abre janela na sua tela. Tudo é provado primeiro no seu PC, numa
pasta de teste, e desfeito no fim.

### Etapa 3. A atualização

**O que muda, e onde:**

1. O programa passa a saber a própria versão (hoje ele não sabe).
2. No começo do programa, entra o Velopack e um modo escondido "procurar versão nova", que roda sem janela.
3. No empacotamento: o programa é empacotado como hoje, e o Velopack monta o instalador e os pacotes de atualização.
   As conferências de hoje (modelos, detectores, peças) continuam travando, agora antes de montar.
4. Um comando nosso para publicar a "versão para o Kaique" no GitHub, de propósito, nunca a cada salvamento. Ele
   assina, sobe e confere.
5. A tarefa do Windows que roda quando o computador liga.
6. O aviso "Reiniciar agora / Depois", a mensagem de quando falha, e um registro do erro num lugar que a gerente
   consegue ler de longe.
7. A primeira instalação nova tira a instalação antiga do Kaique.

**Por quê:** é o que você decidiu. Cada parte é da ferramenta pronta ou do próprio Windows. O que é nosso é só a cola
entre elas.

**Riscos:**

- Os testes que hoje conferem o instalador antigo deixam de valer. Nenhum é mudado calado: o plano lista quais saem e
  por quê, e você diz "sim".
- O disco precisa de espaço para duas versões durante a troca (perto de 4 GB por alguns minutos).
- O antivírus pode demorar na primeira abertura depois de atualizar, como já acontece hoje com o detector de linhas.
- Falta confirmar no seu PC que a tarefa do Windows aplica sem perguntar nada.

**Como provar:**

- Publicar uma versão de mentira, religar o computador de teste, e o programa abre na versão nova, com os projetos
  iguais.
- Abrir o programa antes, publicar, e ver o aviso. "Depois", religar, e abre a nova.
- Publicar uma versão de mentira estragada de propósito, e ver ela voltar para a anterior, com a mensagem na tela e o
  erro no registro.
- Uma versão com a assinatura errada é recusada.
- Tudo o que já funcionava no programa continua igual: todos os testes do GitHub passando.

### Etapa 4. Os testes à distância

**O que muda, e onde:**

1. Nas Configurações, a opção "Deixar o Samuel fazer testes neste computador (pela rede do Tailscale)", ligada de
   fábrica.
2. Na primeira abertura, a janela da senha.
3. Um ajudante que liga, desliga e desfaz tudo, com uma só pergunta do Windows, e anota o que fez.
4. Um jeito de pedir cada teste em prioridade baixa ou normal (sem dizer, baixa).

**Riscos:** o antivírus reclamar; a senha nunca pode aparecer em lugar que outros programas leiam; pastas soltas no
disco do Kaique.

**Como provar:**

- Do seu PC, um comando de longe entra na conta de testes, roda a medida de velocidade e traz o resultado.
- Um comando tenta enxergar a pasta do Kaique (e a dos livros) e não consegue.
- Um comando de fora do Tailscale não entra.
- Desligar a opção fecha tudo.
- No fim, a lista do que foi desfeito no seu PC.

---

**De onde veio:** dos seus pedidos de 16/11 no chat. A comparação foi feita lendo a documentação e o código das
ferramentas, e instalando as duas candidatas num teste à parte, fora do programa. O detalhe técnico, com os links,
está no documento de pesquisa do projeto.
