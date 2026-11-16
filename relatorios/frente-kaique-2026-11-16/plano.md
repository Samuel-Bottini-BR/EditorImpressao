# Plano: deixar o notebook do Kaique pronto (16/11/2026)

**Para o Samuel aprovar antes de qualquer agente começar.** Nada do programa mudou ainda.

## O que você pediu

- "antes de tudo isso, agora vamos começar os testes já no pc do Kaique" · "eu quero instalar a api, para que eu possa
  chamar testes dentro do pc dele aqui pelo meu claude code"
- "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um
  instalador fazer tudo de novo"
- "não faremos os testes agora no computador do kaique, mas quero deixar tudo pronto para que isso possa ser feito,
  assim quando eu tiver mais pressa, posso colocar agentes trabalhando no meu pc e testes rodando no pc dele e no git
  hub"

## O que já está decidido (no Livro, D-705 a D-717)

**Testes à distância**
- Pelo comando de longe do próprio Windows (Servidor OpenSSH), só pela rede do Tailscale. Sem porta nova dentro do
  programa.
- Uma opção nas Configurações liga e desliga: "Deixar o Samuel fazer testes neste computador (pela rede do
  Tailscale)". Vem ligada de fábrica. O instalador não pergunta nada disso.
- Liga sozinho junto com o Windows.
- Entra numa conta do Windows só para os testes: sem poder de administrador, escondida da tela de entrada, com a senha
  que você criar. Os projetos de teste nunca se misturam com os do Kaique.
- Você escolhe, a cada teste, prioridade baixa ou normal. Sem dizer nada, roda em baixa.

**Atualização**
- Como os apps: o instalador só na primeira vez; depois a versão nova chega sozinha.
- O programa procura e instala a versão nova por trás, toda vez que o computador liga.
- Se o programa estiver aberto quando a versão nova chegar: um aviso para salvar o trabalho e reiniciar.
- A "versão para o Kaique" é publicada de propósito, nunca a cada salvamento no GitHub.
- Vem do GitHub do projeto, que continua público, com uma assinatura que prova que o arquivo é nosso.
- A ferramenta que faz isso é uma pronta, que outros programas já usam.

**A versão**
- Vai a versão de teste, a mais nova. A principal só recebe a versão de teste depois da sua conferência final.

**Desempenho** (D-707): fica para a Fase 5, não entra nesta frente.

## As 5 perguntas, já respondidas (16/11)

1. Se a atualização falhar, volta para a versão anterior: "Sim, e tem que avisar a gente de alguma maneira". O aviso
   (opção "1"): na tela do Kaique, "A atualização não deu certo. O programa voltou para a versão anterior e continua
   funcionando. Avise o Samuel.", e o erro vai para um registro que a gerente lê daqui. Nenhuma senha dentro do
   programa (D-718, D-719).
2. O aviso de reiniciar tem "Reiniciar agora" e "Depois"; com "Depois", entra na próxima vez que o computador ligar:
   "Sim" (D-720).
3. A senha dos testes: uma janela pequena na primeira abertura pede "a senha dos testes à distância"; o Kaique digita
   a que o Samuel passar; sem ela, os testes à distância ficam desligados e a senha pode entrar depois nas
   Configurações: "ok" (D-721).
4. Testar antes no PC do Samuel e desfazer tudo no fim, com a lista do que foi desfeito: "Sim" (D-722).
5. A versão que o Kaique tem: "a ultima vesão foi a que eu deixei na minha area de trabalho o .exe lá". É o
   instalador feito em 28/10 da versão de teste daquele dia (ramo `obra-2026-10-26`, perto do `3961fbff`); a versão
   de teste de hoje tem mais de 600 salvamentos depois dele. A etapa 2 confere que um projeto salvo por ela abre igual.

## As etapas

Cada agente começa entregando o plano dele (o que vai fazer, por que, onde mexe, como prova), e só mexe depois do seu
"sim". Nenhum abre janela na sua tela. Nenhum abre outro agente.

**Etapa 1. Estudo, sem mexer no programa** (agente pesquisador, Opus 5.5)
- Qual ferramenta pronta de atualização funciona com o nosso Python 3.14 e com o empacotador de hoje (o programa é
  empacotado em pasta e instalado em Arquivos de Programas, o que pede licença de administrador para trocar os
  arquivos). Candidatas: tufup, Velopack e outras que ele achar. Para cada uma: licença, se baixa só o que mudou, se
  volta para a versão antiga, como assina, se consegue atualizar quando o computador liga.
- Como o programa liga e desliga o comando de longe: instalar o OpenSSH, ligar com o Windows, aceitar só o
  Tailscale, criar e esconder a conta de testes, rodar com prioridade baixa ou normal.
- Como outros programas fazem as duas coisas.
- Entrega: um relatório com a recomendação e os riscos. Você escolhe a ferramenta.

**Etapa 2. Empacotar a versão de teste como está e instalar numa pasta de teste** (agente verificador, Opus 5.5)
- O instalador nunca foi instalado de verdade. Primeiro, provar que ele instala, abre e processa um livro, sem
  aparecer na sua tela.
- Abrir um projeto salvo pela versão que o Kaique tem hoje (pergunta 5) e conferir que nada se perde.

**Etapa 3. A atualização** (agente implementador, Opus 5.5)
- Pôr a ferramenta escolhida no programa: procurar a versão nova quando o computador liga, instalar por trás, voltar
  se der erro, o aviso de reiniciar com o programa aberto.
- Um comando nosso para publicar a "versão para o Kaique" no GitHub, assinada.
- Prova: publicar uma versão de mentira, religar o computador de teste, e o programa abre na versão nova com os
  projetos iguais.

**Etapa 4. Os testes à distância** (agente implementador, Opus 5.5)
- A opção nas Configurações, ligada de fábrica, e a janela da senha (pergunta 3).
- Ligar: instala o OpenSSH, liga com o Windows, aceita só o Tailscale, cria a conta de testes escondida.
- Desligar: para tudo e fecha a entrada.
- Prova: um comando de longe que entra na conta de testes, roda a medida de velocidade e volta o resultado; e um
  comando que tenta enxergar a pasta do Kaique e não consegue.

**Etapa 5. Conferência por quem não construiu** (outro agente verificador, Opus 5.5)
- Instalação do zero, atualização de mentira, opção dos testes ligada e desligada, e o que já funcionava no programa
  continua igual (regra de 03/11: o novo não estraga o testado).
- Desfazer no seu PC tudo o que o teste instalou (pergunta 4).
- Relatório nos três formatos, com prints. Você confere.

**Etapa 6. Mandar para o Kaique** (você e a gerente)
- Você manda o instalador. Ele instala, aceita a pergunta do Windows e digita a senha.
- O notebook dele precisa estar na rede do Tailscale.
- Daqui, eu confiro a versão dele por um teste leve.

**Etapa 7. A primeira atualização de verdade** (gerente)
- Publicar uma "versão para o Kaique" pequena e ver ela chegar sozinha no notebook dele.

## O que não muda

- Os filtros, as ferramentas e tudo o que você já escolheu e testou. Esta frente mexe só no começo do programa (a
  procura da versão nova), nas Configurações (a opção nova) e no empacotamento.
- Os livros e os projetos do Kaique: atualizar nunca apaga nada.

## O que espera enquanto isso

Os 5 agentes da lista de hoje (programinha das falas, Tirar o fundo, retângulos na capa, "Montar para imprimir",
conferência final da obra) esperam o seu comando, como você mandou: "antes de tudo isso".
