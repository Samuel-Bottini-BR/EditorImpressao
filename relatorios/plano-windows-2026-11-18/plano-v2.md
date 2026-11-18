# Plano da parte do Windows, versão 2: atualizador, testes à distância e o motor do Kraken à parte (18/11/2026)

Plano de um implementador, só lendo e escrevendo. **Nenhuma linha do programa nem dos testes mudou.** Nenhuma janela
na tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada apagado. Ramo `plano-windows-2026-11-18`.

A versão 1 (`plano.md`, nesta mesma pasta) fica como histórico. Esta versão 2 põe no lugar as escolhas do Samuel de
hoje (D-767 a D-790), junta o estudo do motor do Kraken à parte (ramo `kraken-separado-2026-11-18`) e a ordem de cada
passo que ele aprovou (escrever, testes, outro agente tenta quebrar, prova à vista). Livro lido: o do ramo
`obra-2026-10-26` (`48d2c3a8`, até a D-790). O código é o mesmo que a versão 1 leu (de lá para cá só mudaram o Livro e o
CLAUDE.md).

---

## Resumo para o Samuel

Este é o plano da parte do programa que não aparece nas telas dos livros: o instalador, a atualização que chega sozinha
no notebook do Kaique e os testes à distância (você entrar no notebook dele daqui). É a segunda versão: ela já tem
todas as suas escolhas de hoje.

**O que as suas escolhas mudam:**
- O motor do Kraken fica numa pasta só dele, dentro da pasta do programa. Ele vem no instalador e só é baixado de novo
  quando ele mesmo mudar. Cada atualização fica com uns 460 MB, e a troca no notebook com uns 2 a 3 minutos (conta; vai
  ser medido nas provas).
- Quando o Kaique clica "Depois", a versão nova entra quando ele fecha o programa. A janelinha "Atualizando o programa,
  espere um pouco..." aparece depois do "Reiniciar agora" e quando ele abre o programa no meio da troca.
- Se a atualização falhar, o aviso diz qual dos três casos aconteceu.
- Na pergunta "Deseja permitir...?" do Windows aparece "Editor de Impressão", e o programa avisa antes: "Clique em Sim".
- Ligar os testes à distância é tudo ou nada, e a tela mostra o que o computador tem de verdade. A janela da senha tem
  dois campos e o botão para ver a senha.
- Publicar uma versão é feito no disco de dentro do seu PC, sem nunca deixar menos de 20 GB livres. O instalador só sai
  na primeira entrega e quando você pedir.

**Como o trabalho anda:** são 7 passos. O primeiro arruma as regras que cada agente recebe. Cinco constroem as peças. O
último é a confirmação com a versão que vai para o Kaique. Em cada passo, um agente escreve, os testes rodam, outro
agente tenta quebrar, e só então a gerente chama você para ver a prova na sua tela.

**O que você vai ver e fazer:** 5 sessões no seu PC, com umas 19 perguntas "Deseja permitir...?" (você clica "Sim" ou
"Não" quando a gerente pedir), e depois a confirmação, com 5 ou 6. Em duas provas a gerente vai pedir algo a mais:
desligar o computador no meio de uma troca de versão e tirar a internet do PC por uns minutos. Ela pergunta antes como
você prefere.

**Quanto tempo:** de 60 a 91 horas de trabalho dos agentes (chute: nada parecido foi medido); de 4 h 40 a 6 h 35 com
você por perto, em sessões separadas; e 1 h 30 a 2 h na confirmação.

**O que espera você:** as perguntas que faltam sobre as regras dos agentes (duas delas entram já no primeiro passo), o
desenho da janela da senha antes de ela ser construída, o print da janelinha da troca quando ela existir, o jeito das
duas provas acima, e alguns textos de tela que ainda não foram escolhidos. E três pontos em que duas escolhas suas,
lidas ao pé da letra, não combinam: estão no fim do plano, sem resolver, esperando você (seção 6.3).

(Para consulta: D-765 a D-790.)

---

## Para a gerente, em poucas linhas

- **7 passos** (0 a 6): o pacote de regras; o porteiro do Windows; publicar com o motor à parte; o atualizador; os
  testes à distância; desinstalar; a confirmação. **10 peças** (as 8 da versão 1, mais o motor no lugar e as janelas de
  prova).
- **Tempo:** escrita 52 a 78 h e quem tenta quebrar 8 a 13 h (chute); com o Samuel 4 h 40 a 6 h 35, em 5 sessões, 19
  perguntas do Windows (+2 opcionais); versões de prova 1 h 20 a 2 h 10 (conta); confirmação 1 h 30 a 2 h, com 5 a 6
  perguntas. Na versão 1: 27 a 40 h de escrita, 4 h a 4 h 45 com ele.
- **Aberto sem depender dele:** os riscos que o passo 1 prova primeiro (a pergunta do Windows com o programa atrás e o
  nome que o Windows mostra para um programa sem certificado), o socorro dentro do Velopack, e a leitura do estado do PC
  dele depois da etapa 5 (seção 6.1).
- **Depende dele:** as 4 perguntas restantes da proposta das regras (as conferências e o formulário entram no passo 0),
  as contradições das regras que faltam (o pedido diz 6; pelo Livro são 7, ver 6.2), o desenho da janela da senha, o
  print da janelinha, textos de tela novos, o jeito das provas de desligar e de tirar a internet (seção 6.2).
- **Decisões que não combinam ao pé da letra (seção 6.3):** o Setup.exe que continua saindo contra o motor sempre dentro
  do instalador; "a janelinha em toda troca" contra "a troca ao fechar por trás"; e o nome "Editor de Impressão" na
  pergunta do Windows, que pode exigir o arquivo do programa com acento (contra a regra técnica de caminho sem acento).

---

## 1. O que cada escolha de hoje muda no plano

Uma linha por decisão: o que muda nas peças, nos passos e nas provas. As decisões que não mudam peça nenhuma (regras
de trabalho) estão no fim da lista.

- **D-767 (nada escondido nem de mentira).** Toda peça que mexe no Windows só fica "pronta" depois de rodar de verdade e
  à vista no PC do Samuel (passo 4 de cada passo, seção 3). O alcance foi fechado pela D-773.
- **D-768, D-788, D-789, D-790 (o motor do Kraken à parte).** Peça nova 9 ("o motor no lugar"). O motor mora em
  `C:\Program Files\EditorImpressaoPrograma\motor-kraken\<versão do motor>\`, ao lado do `current\` que o Velopack troca;
  vem no instalador como um arquivo só; o ajudante o põe no lugar; quando muda, o ajudante baixa só ele, com a assinatura
  do Samuel, e a versão nova só entra depois que o motor chegou inteiro. Cada atualização vai inteira, sem o pacote de
  diferença (~460 MB). Mexe nas peças 4, 7 e 8 e nos passos 2, 3 e 5. A antiga decisão 16 ("para depois") deixou de
  existir; a decisão 1 da versão 1 está fechada.
- **D-769 ("Depois" troca ao fechar).** Peça 4: quando o Kaique fecha o programa depois de "Depois", a troca começa
  sozinha, por trás, sem janelinha e sem reabrir; na próxima abertura ele já está na versão nova. Desligar no meio não
  perde nada. Passo 3 prova, inclusive desligando no meio. Muda a D-734 e o teste antigo do `trocar_antes_de_abrir`.
- **D-770 (a janelinha em toda troca).** Peça 4: a janelinha aparece depois do "Reiniciar agora" e quando o Kaique abre o
  programa no meio da troca; espera o sinal de fim (não um relógio) e abre o programa sozinha. O print vai ao Samuel
  quando ela existir (seção 6.2).
- **D-771 (ligar é tudo ou nada).** Peça 5: o ligar desfaz sozinho, de trás para frente, o que fez naquela vez se um
  passo falhar; a tela diz "Desligado" e o motivo; nenhum botão novo. Sai a opção "Ligado pela metade" com dois botões da
  versão 1.
- **D-772 (o servidor OpenSSH vem do Windows Update).** Peça 5: antes de ligar, o aviso de que precisa de internet e pode
  levar até 15 minutos; se falhar, o motivo. Passo 4 prova ligando sem internet.
- **D-773 (as versões de prova).** Peça nova 10b: uma janela pequena e visível no PC do Samuel serve versões de verdade
  pela rede de verdade (fechá-la é a internet caindo); o publicar é provado com uma versão de teste no GitHub como
  rascunho, liberada só na prova e apagada no fim. Passos 2, 3 e 4.
- **D-774 (os testes antigos que mudam).** Os 4 principais e os outros 5 da seção 4.2 da versão 1 mudam, cada um no
  passo que muda o comportamento que ele cobra (seção 8). Os "provavelmente mudam" vão ao Samuel antes, numa lista, um
  por um.
- **D-775 (a ordem de cada passo).** Todo passo da seção 3 tem as quatro etapas: escrever; testes; outro agente tenta
  quebrar (com o relatório dele no formulário); só então a prova à vista. Sai o desenho da versão 1 de escrever tudo e
  provar em três sessões no fim.
- **D-776 (publicar no C:, nunca menos de 20 GB livres).** Peça 8: confere o espaço antes (com o que vai usar de
  verdade), vigia durante, para com aviso perto da reserva e apaga o rascunho no fim, também com erro. Passo 2 prova.
- **D-777 (o .msi só na primeira entrega e quando pedir).** Peça 8: a atualização sai sem .msi e sem o zip portátil; o
  Setup.exe continua saindo. O .msi sai no passo 2 (prova), no passo 5 (para reinstalar na prova) e no passo 6 (a
  primeira entrega). Ver 6.3, ponto 1.
- **D-778 (as três frases).** Peça 4: uma frase para cada caso (voltou; sem a assinatura; não conseguiu voltar), uma vez
  por caso, marcada como vista só depois de aparecer. Passo 3 tira o print de cada uma.
- **D-779 (Velopack 1.2.161 com a nossa proteção).** Peça 4: o socorro guarda a versão que funciona fora do que é
  trocado e volta sozinho se a troca estragar; a janela do Kaique deixa de criar o Velopack (a pasta que sobrava não
  nasce). Nenhuma troca de versão do Velopack. Passos 3 e 5 provam.
- **D-780 (as duas trancas, sem prova do celular).** Peças 1 e 5: a regra do firewall (só a rede do Tailscale) e a
  segunda tranca dentro do próprio servidor de entrar de longe (só a conta de testes, só vinda do Tailscale); depois de
  ligar, o programa lê as duas no Windows e no próprio servidor e diz na tela se faltar alguma. Sai a prova com o
  celular da versão 1. A entrada vinda de fora fica "construída e conferida por dentro, não provada de fora" até o
  primeiro teste no notebook do Kaique (D-739).
- **D-781 (senha em dois campos e botão de ver).** Peça 6b: "Senha" e "Repita a senha", o aviso "as duas senhas não são
  iguais, digite de novo", o botão de ver e esconder; a mesma janela na primeira abertura e nas Configurações. O desenho
  vai ao Samuel antes de construir (seção 6.2). Passo 4 prova.
- **D-782 (a pergunta mostra "Editor de Impressão").** Peça 1 muda de desenho: quem pede a licença ao Windows é o próprio
  programa do Editor, que se abre de novo, sem janela, só para fazer o trabalho de administrador (e pode chamar o
  PowerShell por dentro, já com a licença). A janelinha avisa antes: "O Windows vai perguntar se pode deixar o Editor de
  Impressão fazer alterações. Clique em Sim." Passo 1 prova; risco 2 da seção 6.1; ver 6.3, ponto 3.
- **D-783 (o Samuel desliga o Controle Inteligente de Aplicativos ao instalar).** Não é peça: vai para a lista da
  instalação no notebook do Kaique (etapa 6), com o cuidado de que depois de desligado ele não liga mais sem reinstalar
  o Windows. Está no fim do passo 6.
- **D-784 (cada agente recebe o pacote de regras do trabalho dele).** Passo 0 monta o pacote, e cada passo da seção 3
  diz os arquivos que mexe e as etiquetas que eles dão (para a tabela).
- **D-785 (o que roda à vista e o que pode ficar escondido).** Cada passo diz o que é à vista e o que pode ficar
  escondido. Instalar, desinstalar, a pergunta do Windows, a primeira abertura, toda a atualização, os testes à
  distância, as tarefas, o que muda o Windows e o publicar: à vista. Os testes automáticos, os prints para a Central e o
  teste que clica nos botões: podem ficar escondidos.
- **D-786 e D-787 (velocidade e testes no PC).** Valem para todos os passos (seção 3, "Regras de todos os passos").
- **D-765 e D-766.** O plano é só da frente do notebook do Kaique; nada de conserto do resto do programa. Depois da
  entrega, cada conserto vira uma versão pelo publicar deste plano.

---

## 2. As peças (10)

Cada peça mora num lugar só (CLAUDE.md §11.12). As peças 1 e 2 são a base; as outras as usam. O que a versão 1 já
dizia e continua igual está resumido; o detalhe está no `plano.md`, seção 1.2.

**Peça 1. O porteiro do Windows** (`core/windows.py`, novo). Uma peça só para pedir licença, lançar solto, rodar e
esperar, mexer em tarefas, a pasta de troca e ler como o Windows está. Sempre uma de três respostas: deu certo, a
pessoa disse "Não", falhou (com o motivo em português). **Muda com a D-782:** pedir licença passa a abrir **o próprio
programa** do Editor com a licença de administrador e um aviso de trabalho (um arquivo na pasta de troca), em vez do
PowerShell. Esse programa aberto com licença não mostra janela nem brasão: faz o trabalho (pode rodar os scripts do
PowerShell por dentro, pelo caminho inteiro, com a marca de UTF-8), escreve o relatório na pasta de troca e sai. A
janela do Kaique continua dona da pergunta e vem para a frente antes. **Muda com a D-780:** a leitura sem licença inclui
as duas trancas (a regra do firewall e o que o próprio servidor de entrar de longe diz que aceita). O resto como na
versão 1.

**Peça 2. A pasta segura do programa.** Como na versão 1: uma pasta própria em Arquivos de Programas, ao lado da pasta do
programa, nunca dentro; licenças de fábrica, nenhum comando de licença à mão; criada na pergunta da primeira abertura;
`C:\ProgramData\EditorImpressao` deixa de existir. Guarda o estado, o registro, o socorro e a cópia para voltar (agora
~460 MB em vez de 788 MB, sem o motor), os scripts do desfazer, o caderninho do antes e a fonte de teste.

**Peça 3. Perguntar ao Windows como está.** Como na versão 1. "Preparado" passa a ser a resposta do Windows (a tarefa do
ajudante existe, aponta para o socorro, roda como o sistema, a pasta segura confere, a tarefa de limpeza existe, o motor
está no lugar). Nos testes à distância, "como está agora" lê o serviço, a conta, as duas trancas e a porta. **Muda com a
D-771:** o ligar nunca deixa "pela metade"; mas a leitura continua precisando dizer a verdade quando o próprio desfazer
falhar ou alguém mudar o Windows por fora (o texto desse caso está em aberto, seção 6.2).

**Peça 4. A troca de versão.** Como na versão 1 (um jeito só de pedir a troca, sinal de fim, marca "trocando", falha
passageira que não risca, o socorro fora do que é trocado, o aviso logo que a versão baixa, a janela sem o Velopack),
com:
- **D-769:** o "Depois" lança a troca quando a janela fecha, por trás, sem janelinha nem reabrir;
- **D-770:** a janelinha depois do "Reiniciar agora" e na abertura no meio da troca, até o sinal de fim;
- **D-778:** as três frases, escolhidas num lugar só (`registrar_falha` e `o_que_avisar`);
- **D-779:** o socorro e a janela que não cria o Velopack, sobre o Velopack 1.2.161;
- **D-790:** antes de trocar, "garantir o motor que a versão nova pede" (peça 9); sem o motor inteiro, não troca;
- o teste rápido depois da troca passa a abrir o motor e esperar o "pronto" (estudo do Kraken, §3).

**Peça 5. Ligar e desligar os testes à distância.** Como na versão 1 (relatório sempre lido, preparo e ligar separados,
a senha numa codificação só, conferida antes nas regras de senha do Windows, segunda tranca, porta ocupada conferida
antes, nomes dos passos sem número de decisão), com **D-771** (tudo ou nada, sem botão novo), **D-772** (o aviso de
internet e de até 15 minutos; o motivo se falhar) e **D-780** (o ligar só termina bem depois de ler as duas trancas
certas; se faltar uma, é falha e o ligar desfaz o que fez).

**Peça 6. A tela.** Dividida em duas:
- **6a. A primeira abertura sem congelar** (passo 3): a pergunta e o preparo saem de antes do laço da janela e rodam por
  trás; a janelinha da D-782 antes da pergunta.
- **6b. A tela dos testes à distância** (passo 4): Configurações > Testes à distância mostra o que foi lido do Windows;
  ligar e desligar por trás; a janela da senha da D-781.

**Peça 7. Desinstalar limpo, como o sistema.** Como na versão 1 (tarefa de limpeza disparada pelo aviso do Windows de
programa removido, que confere antes se o programa saiu mesmo; desfaz os testes; apaga tarefas, pasta segura e sobras;
nunca toca os projetos; lista no registro de eventos do Windows), com: **confere que `motor-kraken\` saiu** e apaga o que
sobrou (a limpeza do Velopack ignora erros, estudo do Kraken §4.2).

**Peça 8. Publicar.** Como na versão 1 (uma função só roda o vpk; no GitHub nunca pela metade; um número de versão só),
com: **D-789** (sem o pacote de diferença; `assinatura.py` não muda); **D-776** (no C:, reserva de 20 GB, conta do espaço
feita com o que vai usar de verdade, vigiada durante, rascunho apagado também com erro); **D-777** (sem .msi e sem zip
portátil nas atualizações; o .msi só quando pedido); **D-768/D-788** (as três saídas num lugar só: a pasta portátil, com
o motor solto como hoje; a atualização, sem o motor e com o `motor-exigido.json`; o instalador, que é a atualização mais
o motor num arquivo só em `current\instalar\` e o .msi; e a publicação própria do motor, rara, com etiqueta
`motor-kraken-<v>`; antes de liberar uma versão, confere que o motor que ela pede está publicado e o lê de volta).

**Peça 9 (nova). O motor no lugar** (estudo do Kraken, §2 a §4). Uma peça só que acha, confere e põe o motor no lugar,
venha ele do instalador ou da internet. A versão do motor tem um lugar só (`VERSAO_DO_MOTOR` em `core/ocr_kraken.py`); a
conferência "inteiro e da versão certa" é uma só (lê o `motor.json`), usada pelo motor, pelo teste rápido, pelo
`--conferir-ocr`, pelo ajudante e pelo empacotador. O motor novo chega em `.chegando-<v>`, é conferido e só um renomear
dá o nome final; ficam as duas versões mais novas (a volta acha o motor dela sem internet). É chamada no começo de cada
rodada do ajudante (a primeira vez e o conserto sozinho) e antes da troca (o motor novo).

**Peça 10 (nova). As janelas de prova** (D-767, D-773). Ferramentas das provas, que rodam o código de verdade das peças
(importado do programa, nunca uma cópia):
- **10a. A janela de prova:** pequena e visível; uma linha por prova; mostra o que o Windows responde, lido por fora do
  programa.
- **10b. O servidor das versões de prova:** janela pequena e visível que faz o papel do GitHub, serve as versões de
  verdade e mostra cada pedido; fechá-la é a internet caindo. O programa instalado o acha pela fonte de teste, que só o
  administrador cria (peça 2).

---

## 3. Os passos

### Regras de todos os passos

- **A ordem de cada passo (D-775):** (1) um agente escreve; (2) os testes automáticos rodam, cobrando o jeito certo; (3)
  outro agente, que não escreveu, tenta quebrar; (4) só então a prova à vista na tela do Samuel. Se a etapa 3 achar
  problema, volta à 1. O Samuel só é chamado quando o passo passou pelas três primeiras. **Um passo por vez:** o próximo
  só começa depois da prova do anterior.
- **O pedido de cada passo sai com o pacote (D-784)** montado pelos arquivos listados no passo. Arquivo novo fora da
  tabela recebe todas as regras, e a gerente acrescenta a linha (cada passo diz qual).
- **Antes de escrever (CLAUDE.md §11.12, pontos 3 e 6):** no ONDE-PAREI, a lista do que pode falhar e o que o programa
  faz em cada caso (os seis de sempre: sem licença, sem internet, disco cheio, "Não", arquivo preso, desligar no meio, e
  os do passo), e o que cada peça de fora faz em cada caso que usamos, com a fonte (documento ou linha do código). Mais
  as seções de sempre: decisões a cumprir, o que já está escolhido e testado, como fica para quem usa.
- **Testes (D-787):** no PC, um arquivo de teste por vez, o do que o passo mexeu; o conjunto inteiro e o teste dos
  botões no GitHub em toda entrega, com o número da rodada; antes de juntar, a gerente roda o inteiro no PC com os outros
  agentes parados (CLAUDE.md §4.6). Teste antigo só muda pela D-774 (seção 8).
- **Velocidade (D-786):** nenhum passo mexe no processamento das páginas. O passo 2 mexe em `core/ocr_kraken.py` (onde
  o motor é achado), que o caminho do livro hoje não usa (D-164); a gerente decide se roda o filtro de velocidade do
  GitHub ali. A medida que vale no PC é a do fim da fase.
- **As provas (D-767, D-785):** na área de trabalho de verdade, nunca escondida, nenhuma janela empurrada para fora da
  tela; a janela de prova (peça 10a) diz o que está fazendo e mostra o resultado; nada de peça de mentira no lugar do
  Windows; o Samuel clica "Sim" ou "Não" quando a gerente pedir; antes de cada sessão a gerente diz o que vai aparecer.
  No fim de cada sessão, a lista do que foi desfeito no PC dele (D-722). **Pode ficar escondido:** os testes
  automáticos, os prints das telas para a Central e o teste que clica nos botões.
- **Quem tenta quebrar** recebe o pacote com todas as regras (D-784), o formulário do outro e o código, e devolve o
  relatório com os seis campos da proposta das regras (§6): o que leu; o que conferiu nos campos de falhas, de peça de
  fora e de caminhos, e como; caminhos que o outro não listou; falhas não pensadas e resultado não conferido; as regras
  que conferiu; os achados numerados com o lugar no código. Cada passo abaixo diz o foco dele. Ele roda o que dá sem
  pergunta do Windows; o que mexe no Windows não roda escondido (D-785: na dúvida, pergunta à gerente).
- **"Pronto para conferir"** só com o relatório de quem tentou quebrar (cada achado com destino: consertado no commit X,
  não é defeito e porquê, ou vira pergunta) e com a prova de verdade (data, hora, à vista, print ou registro da janela de
  prova).

### Passo 0. O pacote de regras (e, se o Samuel disser sim, as conferências automáticas e o formulário da entrega)

- **O que faz:** transforma os esboços da proposta das regras (catálogo, tabela de etiquetas, montador do pacote) em
  programa de verdade, no lugar que a gerente escolher; acrescenta à tabela as linhas dos arquivos novos deste plano; um
  teste cobra que todo arquivo do git tem linha. **Se ele disser sim à pergunta 2 da proposta:** as 24 conferências da
  §5.1 viram testes em `tests/`, com a lista de exceções que só diminui (os lugares do código que este plano ainda vai
  mudar; cada passo apaga as suas). **Se disser sim à pergunta 4:** a conferência do formulário da entrega (F1 a F20, em
  três etapas) e dos seis campos de quem quebra. No fim, monta o pacote do passo 1 e entrega à gerente.
- **Arquivos:** os esboços de `relatorios/regras-agentes-2026-11-18/esbocos/` (ramo `regras-agentes-2026-11-18`) no
  lugar final; `tests/test_conferencias_*.py` (novo, nome a escolher). Nada em `core/`, `ui/` ou nos arquivos do
  programa. Etiquetas: TESTE, GER. O texto do CLAUDE.md e dos agentes que passa a apontar para o pacote é da gerente, só
  com o "sim" do Samuel.
- **Testes:** os novos; nenhum antigo muda.
- **Quem tenta quebrar (curto):** roda as conferências no código de hoje e mostra que elas acham os defeitos 1 e 4 da
  etapa 5 (o jeito de abrir o PowerShell do "Reiniciar agora" e a tranca da pasta); confere que o pacote do passo 1 traz
  as regras de Windows; procura arquivo deste plano sem linha na tabela.
- **Prova à vista:** não há (nada mexe no Windows; D-785). **Perguntas do Windows: 0.**
- **Depende dele antes:** as perguntas 2 e 4 da proposta. Com "não" nas duas, o passo 0 faz só o pacote.
- **Tempo:** 4 a 7 h de escrita (só o pacote: 2 a 3 h), 30 min a 1 h para quebrar (chute).

### Passo 1. O porteiro do Windows e a pasta segura, com o próprio programa pedindo a licença (peças 1, 2 e 10a)

- **O que faz:** escreve `core/windows.py` (peças 1 e 2, com o desenho da D-782) e a entrada do "trabalho de
  administrador" no começo do `main.py` (antes de qualquer janela ou do brasão; só aceita um aviso de trabalho da pasta
  de troca). Nenhum chamador muda ainda. Escreve a janela de prova (10a).
- **Antes de escrever, ler (§11.12.6):** como o Windows mostra o nome do programa na pergunta quando o programa não tem
  certificado pago (risco 2); o código de erro do "Não" no pedido de licença; como uma janela de fundo pode dar a vez à
  pergunta; as tarefas do Windows; a leitura do PowerShell sem a marca de UTF-8; e, se o caminho for abrir o atalho de
  partida do Velopack em vez do programa, se ele repassa o aviso de trabalho (código do Velopack).
- **Arquivos:** `core/windows.py` (novo; WIN); `main.py` (só a entrada nova; TELA WIN); `tests/test_windows_*.py` (novo;
  TESTE WIN); a janela de prova (novo, **fora da tabela**: a gerente acrescenta uma linha "janelas de prova → WIN
  TESTE"); talvez `empacotar.py` (o nome ou a descrição do arquivo do programa), **só se** a leitura do risco 2 pedir, e
  então isso vira pergunta antes (seção 6.3, ponto 3).
- **Testes antigos que mudam:** nenhum.
- **Quem tenta quebrar, o foco:** nenhum caminho transforma "Não" ou falha em "deu certo"; o código do erro é lido como a
  documentação diz; o programa com licença não faz nada além do aviso de trabalho que veio da pasta de troca (outra
  conta não consegue mandar ele fazer outra coisa); a pasta segura nasce sem comando de licença e não é um atalho para
  outro lugar; nada espera no fio da tela; a exceção da conferência deste arquivo pode sair.
- **Prova à vista (sessão A), sem o programa instalado:** antes, a pasta do programa é montada no C: à vista (5 a 11 min,
  0 perguntas; a reserva de 20 GB conferida), para que a pergunta do Windows seja do programa de verdade. Na janela de
  prova:
  - lançar solto: "o processo lançado rodou às HH:MM:SS", também depois de quem lançou fechar (0 perguntas);
  - **pergunta 1, "Sim":** a pergunta mostra "Editor de Impressão" (foto do celular, se ele quiser tirar); no mesmo "Sim",
    a pasta segura de prova nasce com as licenças de fábrica (a janela mostra quais); uma tarefa de prova roda como o
    sistema; a conta comum lê a pasta e não consegue gravar; uma senha de prova com acento chega igual do outro lado
    (comparada pela soma, nunca escrita); um texto com acento dentro do script chega igual;
  - **pergunta 2, "Não":** "você disse Não; nada mudou";
  - **pergunta 3, com o navegador na frente, "Sim":** a pergunta vem para o meio da tela; esse "Sim" apaga a tarefa e a
    pasta de prova, e a leitura diz "não existe";
  - pedido para um arquivo que não existe: frase em português, sem a caixa crua do Windows (0); a resposta do Windows com
    "ÊXITO" certo (0).
  **3 perguntas do Windows, 25 a 35 min.** Se a pergunta não vier para a frente, ou não mostrar "Editor de Impressão", o
  plano para e a gerente leva o resultado a ele antes de seguir.
- **Tempo:** escrita 8 a 11 h; quebrar 1 h 30 a 2 h 30 (chute).

### Passo 2. Publicar, o motor do Kraken à parte e o servidor das versões de prova (peças 8, 9 na parte de empacotar, 10b)

- **O que faz:** a peça 8 inteira (seção 2); a parte da peça 9 que o publicar usa (`VERSAO_DO_MOTOR`, o `motor.json`
  gravado pelo `montar_motor_kraken.py`, a conferência única do motor no lugar da do empacotador, os dois nomes
  diferentes para "onde achar o motor para montar" e "onde o programa o procura"); a publicação própria do motor; o
  servidor das versões de prova (10b).
- **Arquivos:** `publicar_versao_kaique.py` (WIN); `empacotar.py` (WIN); `montar_motor_kraken.py` (WIN IMG);
  `core/ocr_kraken.py` (IMG WIN); `versao.py` (WIN; o nome do pacote do motor); o servidor das versões (novo, na linha
  "janelas de prova"); `tests/test_empacotar.py` (só testes novos) e testes novos do publicar (a gerente acrescenta a
  linha `tests/*publicar*` → TESTE WIN, que a tabela não tem). `assinatura.py` **não muda** (o motor usa a mesma peça com
  outro nome de pacote); se precisar mudar, o agente para e pergunta.
- **Testes antigos que mudam:** nenhum (nenhum teste antigo cobra o motor dentro do pacote, estudo do Kraken §6). Os do
  Inno continuam. O defeito antigo dos testes do motor que pulam calados numa cópia (Lista de bugs nº 330) continua.
- **Quem tenta quebrar, o foco:** o vpk roda mesmo sem a diferença (ler a documentação e o código do vpk); a conta do
  espaço usa o que vai ser usado e para antes da reserva; o rascunho é apagado também quando dá erro no meio; no GitHub,
  nada liberado antes da assinatura lida de volta; nenhuma versão liberada sem o motor que ela pede publicado e lido de
  volta; a diferença entre atualização e instalador está num lugar só; o `motor-exigido.json` vai dentro do que a
  assinatura cobre.
- **Prova à vista (o Samuel olha a janela, não clica nada):**
  - publicar uma versão de prova no C: sem o .msi: o espaço antes e depois (volta ao que era) e o tempo de montar (D-789);
  - publicar outra com o .msi pedido (D-777): medir o .msi com o motor num arquivo só (nunca medido);
  - o aviso de pouco espaço: a conta de verdade do espaço, com a reserva aumentada só nesta prova (o C: nunca é enchido;
    a gerente diz isso a ele antes);
  - a versão de teste no GitHub como rascunho: sobe, é lida de volta, liberada só na prova e apagada no fim (D-773);
  - a publicação do motor 1 (e, para o passo 3, a do motor 2 de prova).
  **0 perguntas do Windows.** Máquina: 1 h a 1 h 40 (conta e chute); com ele: 15 a 20 min para olhar a janela e os
  números.
- **Depois da prova, montar as versões de prova do passo 3** (à vista, sem precisar dele): a primeira com o .msi (motor
  1); uma boa; uma que nem abre (o programa quebrado de propósito); uma com a assinatura de uma chave falsa; uma que pede
  o motor 2, com o motor 2 verdadeiro e o motor 2 com assinatura falsa; e uma boa para o atualizar de longe do passo 4.
  A lista exata vai no ONDE-PAREI. Tempo: 1 h 20 a 2 h 10 (conta: 12 a 16 min por versão, pelo estudo; o .msi não
  medido).
- **Tempo:** escrita 11 a 16 h; quebrar 1 a 2 h (chute).

### Passo 3. O atualizador, o motor no lugar e a primeira abertura (peças 3 na parte do atualizador, 4, 6a e 9)

- **O que faz:** o atualizador passa a usar o porteiro; tudo o que a peça 4 diz (seção 2); a peça 9 ligada ao ajudante
  (a primeira vez, vindo do `current\instalar\`; o motor novo antes da troca; o conserto sozinho); o "preparado" lido do
  Windows (sai a marca das Configurações); a primeira abertura sem congelar, com a janelinha da D-782; a fonte de teste
  apontando para o servidor das versões. O socorro leva antes **um plano curto próprio**, porque mexe no que o ajudante
  roda (risco 3).
- **Arquivos:** `atualizacao.py` (WIN; as funções da peça 4 da versão 1, mais `procurar_e_preparar` com o motor e o teste
  rápido que abre o motor); `main.py` (TELA WIN; o começo: a marca "trocando", a janelinha, a pergunta por trás);
  `ui/aviso_de_atualizacao.py` (TELA WIN; as três frases, a troca ao fechar); `ui/testes_a_distancia_ui.py` (TELA WIN; só
  o `primeira_vez_se_preciso`: o preparo por trás e a janelinha da D-782); `configuracoes.py` (TELA WIN; sai a marca do
  preparo); `core/ocr_kraken.py` (`lugares_do_motor` no programa instalado); a peça 9 (arquivo novo ou dentro de
  `atualizacao.py`, o agente diz no ONDE-PAREI; se novo, a gerente acrescenta a linha WIN); `core/windows.py` só se
  faltar algo (a mudança volta a quem quebra). Os três arquivos de `ui/` precisam estar escritos no pedido (regra do
  implementador; ver contradição X7 na seção 6.2).
- **Testes antigos que mudam (D-774):** o do jeito de lançar o "Reiniciar agora" (item 1 da seção 8); a linha da marca do
  preparo nas Configurações (item 5); o "é portátil" (item 6); a falha da troca que fica riscada (item 7); o
  `trocar_antes_de_abrir` (item 8, pela D-769). **Antes, ao Samuel, um por um:** os que cobram o "preparado" como anotação
  e os do `preparo.txt` no ProgramData (`test_decisoes_preparo_d749.py`).
- **Quem tenta quebrar, o foco:** o socorro contra o que o Velopack 1.2.161 faz de verdade (as linhas do código lidas no
  estudo); o sinal de fim com um ajudante já rodando ("IgnoreNew": um "Reiniciar agora" no meio do motor chegando); o
  instante entre o clique no atalho e a marca "trocando"; cada erro classificado como passageiro ou "risca" (a lista
  inteira, um por um); o motor nunca com o nome final pela metade; a leitura do pacote baixado na pasta do Velopack
  (risco 5); a troca ao fechar quando o Windows desliga; a janela nunca cria o Velopack na conta do Kaique; cada frase
  aparece uma vez por caso; as exceções da conferência deste passo podem sair.
- **Prova à vista (sessão B), com o programa instalado pelo .msi e as versões do servidor visível:**
  - **pergunta 1:** a foto do computador com administrador (para comparar no fim); no mesmo "Sim", a fonte de teste
    aponta para o servidor das versões;
  - **pergunta 2:** instalar pelo .msi, com a barra do instalador na tela;
  - primeira abertura: a janela da senha com "Agora não" (o ligar é do passo 4); a janelinha da D-782; **pergunta 3,
    "Não":** "Nada mudou"; a janela de prova lê "preparado: não"; fechar e abrir: a pergunta volta;
  - **pergunta 4, "Sim":** enquanto o Windows trabalha, ele arrasta a janela e ela responde; "preparado: sim" lido do
    Windows; a pasta `motor-kraken\1\` nasce e a leitura diz "motor 1, inteiro";
  - versão nova sem motor novo, "Reiniciar agora": a janelinha o tempo todo, o programa volta na versão nova; o motor não
    foi baixado (o registro e a data da pasta provam); medir o download e a troca (D-789) (0 perguntas);
  - versão nova, "Depois", fechar: a troca acontece por trás; abrir de novo: já na versão nova, sem esperar (0);
  - **desligar no meio da troca** (do jeito que ele escolher, seção 6.2): ao religar, nada se perdeu e a troca tenta de
    novo (0);
  - no meio de uma troca, clicar no atalho: a janelinha aparece, nada é fechado à força, o programa abre no fim (0);
  - falha passageira: fechar a janela do servidor na hora de ler a assinatura: nenhum aviso; reabrir: a versão entra (0);
  - a versão que nem abre: o socorro volta para a anterior sem internet; **print da frase 1** (0);
  - a assinatura falsa: recusada antes de baixar; **print da frase 2** (0);
  - a volta forçada a falhar (a cópia guardada tirada antes, à vista): **print da frase 3** (0);
  - a versão que pede o motor 2: fechar o servidor no meio do motor: continua a de antes; reabrir: o motor chega inteiro
    e só então a versão entra; o teste rápido abre o motor 2 (0);
  - o motor 2 com assinatura falsa: recusado com a frase 2, tudo fica como estava (0).
  **4 perguntas do Windows, 2 h a 2 h 45** (pode ser em duas sentadas).
- **Depende dele antes:** o print da janelinha para aprovar, assim que ela existir (antes da sessão B); o jeito de
  desligar no meio da troca; os testes antigos "provavelmente" (um por um); os textos de tela novos deste passo (seção
  6.2).
- **Tempo:** escrita 18 a 27 h; quebrar 2 a 3 h (chute).

### Passo 4. Os testes à distância e a tela (peças 3 na parte dos testes, 5 e 6b)

- **O que faz:** tudo o que as peças 5 e 6b dizem (seção 2): relatório sempre lido; tudo ou nada; a senha; o aviso de
  internet e de até 15 minutos; a porta ocupada; as duas trancas e a leitura delas depois de ligar; "como está agora";
  ligar e desligar por trás; a janela da senha da D-781 (o desenho aprovado antes).
- **Arquivos:** `core/testes_a_distancia.py` (WIN); `core/_testes_a_distancia_windows.py` (WIN; vira chamadas do
  porteiro ou sai); `ui/testes_a_distancia_ui.py` (TELA WIN; a janela da senha, o ligar por trás);
  `ui/tela_configuracoes.py` (TELA WIN); `configuracoes.py` (TELA WIN); `core/windows.py` (a leitura das trancas, se não
  ficou pronta no passo 1).
- **Testes antigos que mudam (D-774):** o do lugar do caderninho (item 2), o do comando de tranca no ligar (item 3), o da
  pasta do desfazer protegida (item 4). **Antes, ao Samuel, um por um:** os de `test_decisoes_testes_a_distancia.py` que
  cobram "ligado" e "pronto" como anotação.
- **Quem tenta quebrar, o foco:** o desfazer tira só o que foi feito naquela vez, de trás para frente; o que acontece se
  o próprio desfazer falhar (a tela diz exatamente o que ficou); a senha nunca vai para arquivo, linha de comando,
  registro ou print (busca no código); as trancas lidas no próprio servidor e no Windows, não no nosso arquivo; a faixa
  de endereços do Tailscale também no tipo novo (IPv6); um valor antigo no arquivo de configuração do servidor antes do
  nosso bloco; o Windows Update desligado ou sem internet dão o motivo certo; "Não" no desligar deixa "Ligado"; nenhum
  número de decisão nos textos que aparecem.
- **Prova à vista (sessão C1).** Antes, sem pergunta do Windows, a gerente lê como o PC dele ficou depois da etapa 5 (se
  o servidor de entrar de longe já está instalado, a prova do "sem internet" não passa pelo Windows Update; então ele é
  tirado antes, à vista, com +1 pergunta, e só com o "sim" dele). Na sessão:
  - Configurações abertas: "Desligado" lido do Windows (0);
  - a janela da senha: **print** com as senhas diferentes (o aviso) e **print** com o botão de ver apertado, digitando um
    texto de exemplo, nunca a senha dos testes (0);
  - **pergunta 1:** ligar com a porta ocupada de propósito por uma janela visível: o motivo na tela, nada ligado;
  - **pergunta 2:** ligar sem internet (ele tira a internet por uns minutos, seção 6.2): o aviso antes, o motivo depois, o
    computador como estava, lido pela janela de prova (prova a D-772 e a D-771 juntas, se a ordem dos passos do ligar
    puser o Windows Update depois de algum passo feito; o agente escreve no ONDE-PAREI qual passo falha e o que já foi
    feito antes dele);
  - **pergunta 3:** ligar de verdade, com a senha dele digitada na janela nova (com acento, se ele quiser): a janela não
    para; depois "Ligado" lido do Windows; o programa mostra as duas trancas lidas, e a janela de prova as lê por fora;
    ele entra pela janela de entrar de longe (do próprio PC, como na etapa 5; a entrada de fora fica para o notebook,
    D-780);
  - prioridade baixa e atualizar de longe de novo, para conferir que nada do que funcionava mudou (0, 12 a 15 min);
  - **pergunta 4,** desligar com "Não": continua "Ligado"; **pergunta 5,** desligar com "Sim": "Desligado" só quando o
    Windows confirma;
  - **pergunta 6:** ligar de novo com uma senha nova: a nova entra, a velha não (a sessão termina ligada, para o passo 5).
  **6 perguntas do Windows (+1 se o servidor precisar sair antes), 1 h 15 a 1 h 45.** Foto da pergunta mostrando "Editor
  de Impressão", se ele quiser.
- **Depende dele antes:** o desenho da janela da senha; os textos de tela novos (seção 6.2); o jeito de tirar a
  internet; os testes antigos "provavelmente".
- **Tempo:** escrita 7 a 11 h; quebrar 1 h 30 a 2 h 30 (chute).

### Passo 5. Desinstalar limpo (peça 7), com o motor

- **O que faz:** a peça 7 (seção 2): a tarefa de limpeza nasce na pergunta da primeira abertura; confere que o programa
  saiu; desfaz os testes; apaga tarefas, pasta segura, sobras do Velopack; confere que o motor saiu; nunca toca os
  projetos; registro de eventos; o perfil preso tenta de novo uma vez. O gancho de desinstalar do Velopack deixa de
  limpar.
- **Arquivos:** `atualizacao.py` (WIN; `ao_desinstalar`, `criar_as_tarefas`); `core/testes_a_distancia.py` (WIN;
  `plano_de_desfazer`, `xml_da_tarefa_do_desfazer`); `core/windows.py` (o registro de eventos, se faltar).
- **Testes antigos:** **antes, ao Samuel, um por um:** os de `test_decisoes_desinstalar.py` e
  `test_decisoes_desinstalar_pasta.py` que cobram o gancho do Velopack como quem limpa.
- **Quem tenta quebrar, o foco:** a limpeza confere antes de agir (instalar por cima); nunca chega a
  `%LOCALAPPDATA%\EditorImpressao`; o motor e a cópia do socorro saem; a segunda tentativa só uma vez; a sobra na conta
  do Kaique não nasce.
- **Prova à vista (sessão C2), com os testes ligados do passo 4:**
  - a versão com o passo 5 chega pelo servidor (0); como falta a tarefa de limpeza, o Windows responde "não preparado" e
    a pergunta volta: **pergunta 1, "Sim"**;
  - **pergunta 2:** desinstalar pelas Configurações do Windows, como o Kaique faria; a janela de prova lista o que saiu
    (servidor, conta, perfil, regra, tarefas, pasta segura, `motor-kraken\`, sobras) e que os projetos são os mesmos
    arquivos;
  - **perguntas 3 e 4:** reinstalar pelo .msi desta versão (montado à vista antes, 15 a 40 min, não medido) e abrir: a
    pergunta volta, o ajudante nasce, o motor volta sem baixar;
  - **pergunta 5:** desinstalar de novo; **pergunta 6:** a foto final com administrador, comparada com a do começo da
    sessão B.
  **6 perguntas do Windows (+1 opcional: instalar por cima e ver que a limpeza não age), 45 min a 1 h 10.**
- **Tempo:** escrita 4 a 6 h; quebrar 1 a 1 h 30 (chute).

### Passo 6. A confirmação com a versão do Kaique

- **O que faz:** monta à vista a versão que vai para o Kaique, com o .msi (a primeira entrega, D-777), e repete a etapa
  5 curta: instalar, primeira abertura (a senha em dois campos, a pergunta com "Editor de Impressão"), uma atualização
  com "Reiniciar agora", uma com "Depois" e fechar, ligar, entrar de longe, atualizar de longe, desligar, desinstalar,
  foto. Relatório final nos três formatos, com cada print ao lado das palavras dele da decisão, e a lista do que foi
  desfeito no PC dele.
- **Arquivos:** nenhum do programa (só o relatório).
- **Quem tenta quebrar:** confere a lista "decisão → prova" (seção 10) contra o relatório antes de chamar o Samuel.
- **Prova à vista:** **5 a 6 perguntas do Windows, 1 h 30 a 2 h.** Montar: 30 a 55 min (conta e chute).
- **Fica para a etapa 6 (a instalação no notebook do Kaique), na lista dela:** o Samuel confere e desliga o "Controle
  Inteligente de Aplicativos" (Segurança do Windows > Controle de aplicativos e navegador) antes de rodar o instalador,
  sabendo que depois de desligado ele não liga mais sem reinstalar o Windows (D-783); o Tailscale do Kaique (D-739); os
  discos dele (D-743). **Fica para a etapa 7:** provar que a entrada pelo Tailscale entra e pelo Wi-Fi não (D-780,
  D-739); e, depois da entrega, cada conserto sair como versão nova (D-766).

---

## 4. Como fica para quem usa (o Kaique) e no livro

- **Instalar:** um .msi, uma pergunta do Windows. O motor do Kraken vem dentro.
- **Primeira abertura:** a janela da senha com "Senha", "Repita a senha" e o botão de ver; depois a janelinha "O Windows
  vai perguntar se pode deixar o Editor de Impressão fazer alterações. Clique em Sim."; a pergunta do Windows mostra
  "Editor de Impressão" com a faixa amarela "Editor: Desconhecido"; a janela do programa continua respondendo. Com
  "Não", aparece "Nada mudou" e a pergunta volta na próxima abertura.
- **Versão nova:** o aviso aparece logo que ela chega. "Reiniciar agora" mostra a janelinha até o programa voltar (uns 2
  a 3 min, conta). "Depois": quando ele fecha o programa, a troca acontece por trás; na próxima vez ele já abre na
  versão nova. Se abrir no meio da troca, a janelinha aparece em vez de o programa sumir. O motor só é baixado quando
  muda, e a versão nova só entra depois dele.
- **Falha:** uma das três frases, uma vez; falha passageira não mostra nada.
- **Configurações > Testes à distância:** a frase diz o que o computador tem de verdade. Ligar avisa da internet e dos
  até 15 minutos; se der errado, o computador fica como estava e a tela diz "Desligado" e o motivo.
- **Desinstalar:** o notebook fica como era, sem o motor; os projetos ficam.
- **Nada muda nos livros nem no PDF.** O Kraken hoje não é usado no caminho do livro (estudo do Kraken, ponto 7).

---

## 5. Tempo estimado

| Parte | Tempo | De onde vem |
|---|---|---|
| Escrever (passos 0 a 5) | 52 a 78 h | chute (nada parecido foi medido). Versão 1: 27 a 40 h; estudo do Kraken: +12 a 18 h; o que as decisões de hoje acrescentam (o próprio programa pedir a licença, a troca ao fechar, a janela da senha, a leitura das trancas, o servidor das versões, o espaço vigiado): +9 a 13 h; o passo 0: +4 a 7 h |
| Quem tenta quebrar | 8 a 13 h | chute (o estudo do Kraken dizia 1 a 2 h só para a parte dele). Não conta as voltas à escrita quando ele acha problema: podem somar de 10 a 30% (chute) |
| Provas com o Samuel | 4 h 40 a 6 h 35, em 5 sessões, 19 perguntas do Windows (+2 opcionais) | chute, com partes medidas: a troca de 7,5 min e o ligar de 13 min da etapa 5. A troca de 2 a 3 min sem o motor é conta |
| Montar a pasta da sessão A | 5 a 11 min | medido 10 min 16 s no D:; no C:, conta |
| Publicar (prova do passo 2) | 1 h a 1 h 40 de máquina | conta (12 a 16 min por versão sem o motor, estudo do Kraken) e chute (.msi com o motor num arquivo só, nunca medido) |
| Versões de prova | 1 h 20 a 2 h 10, mais 15 a 40 min do .msi do passo 5 | conta e chute |
| Relatórios das provas | 2 a 3 h (sem ele) | chute |
| Confirmação | montar 30 a 55 min; provas 1 h 30 a 2 h, 5 a 6 perguntas | chute, a partir da etapa 5 |

**Medido** (etapa 5 e estudos de hoje): a troca de 7,5 min com o motor e de 22 a 23 min pela diferença; o ligar de 13
min (Windows Update); a parte do publicar que leva 20 min e meio no D: e 3 min e meio no C:; o pacote sem o motor com 582
arquivos e ~460 MB; desempacotar o resto em 42,8 s no D:; a primeira abertura do motor de 52 a 65 s depois de instalar.
**Conta:** a troca de 2 a 3 min; o publicar de 12 a 16 min; os tempos de download. **Chute:** a escrita, quem quebra e
as sessões.

---

## 6. O que ainda está aberto

### 6.1 Não depende do Samuel para começar (riscos; os primeiros são provados antes de construir em cima)

1. **A pergunta do Windows com o programa atrás de outra janela.** O Windows limita quem vem para a frente. A sessão A
   prova primeiro; se falhar, o plano para (talvez uma frase nova na janelinha, que precisaria do "sim" dele).
2. **O nome que a pergunta do Windows mostra para um programa sem certificado pago (D-782).** Não li ainda se o Windows
   mostra o nome do arquivo (hoje `EditorImpressao.exe`) ou a descrição gravada nele. O agente lê a documentação da
   Microsoft antes de escrever, e a sessão A prova. Se for o nome do arquivo, mostrar "Editor de Impressão" pede mudar o
   nome do arquivo do programa (seção 6.3, ponto 3).
3. **O socorro por dentro do Velopack 1.2.161 (D-779).** Reaplicar a versão guardada quando o Velopack deixar o programa
   sem a pasta dele depende de como o Update.exe se comporta nesse estado. Plano curto próprio no começo do passo 3 e a
   prova "versão que nem abre".
4. **Abrir no meio da troca:** o instante entre o clique no atalho e a marca "trocando" (sessão B).
5. **Ler o pacote baixado na pasta do Velopack para saber que motor a versão pede** (estudo do Kraken, risco 1): detalhe
   de dentro do Velopack; falha segura se mudar (não troca), mas precisa ser relido a cada versão do Velopack.
6. **O estado do PC do Samuel depois da etapa 5:** se o servidor de entrar de longe, a regra ou a conta ficaram, as
   provas do passo 4 mudam. Leitura sem pergunta do Windows antes do passo 4.
7. **A troca ao fechar quando o Windows desliga** (D-769): quanto o Windows espera a tarefa do ajudante e o que o Velopack
   faz se for cortado no meio. Coberto pela proteção da D-779; provado na sessão B.
8. **O .msi com o motor num arquivo só:** nunca medido; o instalador e a atualização da mesma versão ficam com
   conteúdos diferentes (estudo do Kraken, risco 5): tem de estar escrito num lugar só do publicar.
9. **"Instalar por cima" com outro .msi:** não se sabe o que o Windows faz (estudo do Kraken §4.3; versão 1, risco 4).
   Prova opcional na sessão C2.
10. **A segunda tranca no servidor** depende de ele aceitar endereço na regra e da faixa nova (IPv6) do Tailscale.
    Sessão C1.
11. **Desfazer o servidor de entrar de longe** (tudo ou nada com o Windows Update) pode pedir reiniciar o computador ou
    levar minutos. A lista de falhas do passo 4 diz o que o programa faz.
12. **O perfil preso da conta de testes** pode precisar de reiniciar; a limpeza tenta de novo uma vez.
13. **O script sem a marca de UTF-8** continua valendo para os scripts que o programa com licença rodar por dentro;
    sessão A prova.
14. **O espaço no C::** hoje uns 40 GB livres; o estudo viu o C: perder 14 GB sem explicação em uma hora. O publicar
    confere antes e vigia durante (D-776).
15. **A primeira abertura do motor** levou 52 a 65 s no PC dele (antivírus lendo arquivos novos); o teste rápido depois
    da troca tem de contar com isso no limite de tempo.
16. **O notebook do Kaique:** processador, internet, antivírus, espaço livre e se a conta dele é de administrador não
    são conhecidos (versão 1, riscos 7 a 9; estudo do Kraken, riscos 2 e 3).
17. **Não existem fichas da memória** do atualizador, dos testes à distância e do motor. Sugestão: criar no próximo
    `/checkpoint`.
18. **Dois agentes ao mesmo tempo** encurtariam a escrita, mas os passos 3 a 5 mexem no `atualizacao.py`. O plano vai um
    agente por vez (quem escreve, depois quem quebra).
19. **A estimativa de escrita é chute** e pode crescer se o socorro (risco 3) complicar.

### 6.2 Depende do Samuel antes de algum passo

1. **Antes do passo 0: as 4 perguntas restantes da proposta das regras.** A 2 (as conferências que barram o trabalho) e a
   4 (o formulário da entrega conferido por um programa) entram no passo 0 e valem já para o passo 1. A 3 (tirar dos
   agentes a ferramenta de abrir outro agente e a de gravar na Central) muda o texto dos agentes: só com o "sim". A 5
   (trazer as contradições uma por vez) já está acontecendo na prática.
2. **As contradições das regras que faltam.** O pedido fala em 6; pelo Livro, 3 das 10 foram respondidas hoje (a janela
   escondida, a velocidade e os testes no PC: D-785, D-786, D-787), então **faltam 7** (X3, X4, X5, X6, X7, X9, X10 da
   proposta). Se outra foi respondida e não está no Livro, a gerente corrige. As que tocam este plano:
   - **X7 (o agente de tela só mexe em `ui/`, mas a regra sem gambiarra manda a regra em `core/`):** antes do passo 3,
     porque os passos 3 e 4 mexem em `ui/aviso_de_atualizacao.py`, `ui/testes_a_distancia_ui.py` e
     `ui/tela_configuracoes.py`. Quem escreve essas partes?
   - **X5 (onde se junta: `master`, `fase-1` ou `obra-2026-10-26`):** antes de juntar o passo 1.
   - **X4 (quem escreve "PRONTO PARA CONFERIR"):** antes da primeira entrega.
   - **X9 (o ritmo: a obra e a D-765 suspendem regras que os agentes não citam):** o plano segue a D-765.
   - **X6 (quantos agentes):** o plano roda um por vez, e cabe em qualquer resposta.
   - X3 e X10 não tocam este plano.
3. **Antes do passo 2: se as três respostas ao estudo do Kraken valem como a aprovação do estudo** que a D-768 pede ("o
   Samuel aprova esse estudo"). A situação da D-768 no Livro ainda diz "falta o estudo".
4. **Antes do passo 3:**
   - o **print da janelinha "Atualizando"** para ele aprovar, assim que ela existir (D-770);
   - **como desligar no meio da troca:** pelo botão Desligar do Windows, ou cortando a energia (a prova mais forte, mas o
     PC é dele e pode ter outro trabalho aberto);
   - os **textos de tela novos** que nenhuma decisão escolheu: a janelinha enquanto o Windows trabalha (a versão 1
     propunha "Esperando o Windows. Isto pode levar até 15 minutos."); o que a janelinha diz se a troca não terminar
     (o ajudante parou);
   - os testes antigos "provavelmente mudam" do passo 3, um por um (D-774).
5. **Antes do passo 4:**
   - o **desenho da janela da senha** (D-781), com o nome e o jeito do botão de ver;
   - **como tirar a internet** na prova do "ligar sem internet": desligar o Wi-Fi ou o cabo por uns minutos (a conversa
     com a gerente cai junto e volta depois);
   - se o servidor de entrar de longe já estiver no PC dele, **tirá-lo antes da prova** (+1 pergunta do Windows);
   - os **textos de tela novos:** a frase exata do aviso de internet e dos 15 minutos (a D-772 diz o que avisar, não as
     palavras); o que a tela diz quando o próprio desfazer falhar ou uma tranca sumir depois de ligar (D-771, D-780:
     "diz na tela"); e o "não deu para saber" (quando o Windows não responde);
   - os testes antigos "provavelmente mudam" do passo 4, um por um.
6. **Antes do passo 5:** os testes antigos do desinstalar, um por um; se quer a prova opcional de instalar por cima.
7. **Opcional:** a velocidade da internet do Kaique (para os números de download).

### 6.3 Decisões de hoje que, ao pé da letra, não dá para cumprir juntas (apontadas, não resolvidas)

1. **O Setup.exe que continua saindo (D-777) e o motor sempre dentro do instalador, sem nada baixado na hora (D-788 e
   D-727).** O Setup.exe é feito a partir da atualização, que não leva o motor. Se alguém instalar o programa por ele, o
   motor não vem, e o ajudante teria de baixá-lo na hora, o que as duas outras decisões proíbem. As três só se cumprem
   juntas se o Setup.exe nunca for usado para instalar. **O que o Samuel escolhe** (sem sugestão minha, porque cada
   saída muda uma decisão dele): o Setup.exe deixa de sair; ou sai, mas com o motor dentro como o .msi; ou sai como hoje
   e fica escrito que ele não serve para instalar.
2. **"A janelinha aparece em toda troca de versão" (D-770) e "com Depois, a troca acontece sozinha, por trás, quando o
   Kaique fecha o programa" (D-769).** A D-770 lista os dois casos (depois do "Reiniciar agora" e ao abrir no meio da
   troca), e a D-769 diz "por trás". O plano segue as duas listas: **ao fechar, nada aparece**. Mas "toda troca", lida
   sozinha, inclui a troca ao fechar. Confirmar com ele.
3. **O nome "Editor de Impressão" na pergunta do Windows (D-782) e a regra técnica de caminho de disco sem acento
   (CLAUDE.md §3).** Não é decisão de hoje contra decisão de hoje, mas pode virar: se o Windows mostrar o nome do arquivo
   para um programa sem certificado (risco 2), o arquivo teria de se chamar "Editor de Impressão.exe", com acento e
   espaço. O atalho de partida do Velopack já tem esse nome; se for ele quem pede a licença, a regra não é ferida, mas
   isso depende de ele repassar o aviso de trabalho (a ler no código do Velopack). Só se sabe depois da leitura do
   passo 1; se der conflito, vira pergunta antes de escrever.

**Pontos que parecem não combinar, mas combinam (para ninguém tropeçar):**
- "A troca ao fechar à vista" (D-785, item 4) e "a troca por trás" (D-769): a D-785 é sobre as provas no PC do Samuel; a
  D-769, sobre o que o Kaique vê.
- "A senha nunca vai para print" (D-781) e "o print com o botão de ver apertado" (a prova da mesma D-781): na prova se
  digita um texto de exemplo, nunca a senha dos testes.
- "Só conta pronto o que rodou de verdade e à vista" (D-767) e "a entrada de fora fica construída e conferida por
  dentro" (D-780): a D-780, mais nova e específica, aceita essa parte sem a prova de fora até o notebook do Kaique. Ela
  fica marcada como "não provada de fora" no relatório do passo 6.
- O número "6 a 10 GB" da D-776 é de antes do motor à parte; sem o motor, uma versão usa uns 2,5 a 3 GB no C: (conta).
  A regra dos 20 GB livres continua; a conta do espaço usa o que vai ser usado de verdade.

---

## 7. A lista dos defeitos

A lista de 63 itens da versão 1 (`plano.md`, seção 2) continua valendo, cada um com a peça que o resolve. Mudou:
- **6** (a pergunta mostra "Windows PowerShell"): resolvido pela D-782, peça 1.
- **26** (a senha errada sem ter como ver): D-781, peça 6b.
- **27** (o servidor vem do Windows Update): D-772, peça 5 (aviso e motivo).
- **29** (nada prova que só o Tailscale entra): D-780, as duas trancas e a leitura delas; a prova de fora fica para o
  notebook.
- **41** (a mesma frase em três casos): D-778.
- **44 e 46** (a troca lenta e a assinatura que não confere pela diferença): D-789, sem a diferença.
- **45** (o defeito do Velopack na segunda troca de pastas): D-779, a nossa proteção.
- **55** (publicar de 70 a 93 min): D-776, D-777 e o motor à parte; uns 12 a 16 min por versão (conta).
- **58** (o motor em toda versão) **deixa de ficar fora:** D-768, D-788 a D-790, peça 9.
- **62** (o Controle Inteligente de Aplicativos): D-783, lista da etapa 6.
- **Novo 64:** o teste rápido depois da troca só confere que o arquivo do motor existe; passa a abrir o motor (estudo do
  Kraken §3). Peça 4.
- **Novo 65:** a mensagem "É preciso reinstalar o programa" do motor de versão diferente (`core/ocr_kraken.py`) deixa de
  ser verdade com o motor à parte. É texto de tela que hoje não aparece (nenhuma tela usa o Kraken); muda só com o "sim"
  dele quando a tela existir. Fica anotado, fora deste plano.

---

## 8. Os testes antigos que mudam (D-774), por passo

Cada um muda para cobrar o jeito certo, falha no código de hoje e passa no consertado; o verificador roda no código
antigo e mostra que acusa o defeito. Nenhum muda "para passar". O nome de cada um vai na mensagem do commit, citando a
D-774 (a conferência de teste antigo do passo 0 confere).

1. `test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto` (o jeito de lançar
   que fez o "Reiniciar agora" não voltar): passo 3.
2. `test_decisoes_desinstalar.py::test_d731_o_caderninho_fica_onde_o_plano_diz` (o caminho no ProgramData): passo 4.
3. `test_decisoes_desinstalar.py::test_d731_ligar_anota_o_antes_primeiro_e_so_na_primeira_vez` (o comando de tranca):
   passo 4.
4. `test_decisoes_desinstalar.py::test_d731a_a_pasta_do_desfazer_fica_protegida` (o comando de tranca): passo 4.
5. `test_decisoes_ajudante_da_atualizacao.py`, a linha da marca da pergunta do Windows nas Configurações: passo 3.
6. `test_decisoes_atualizacao.py`, o "é portátil" perguntado ao Velopack: passo 3.
7. `test_decisoes_atualizacao.py`, a falha da troca que fica riscada: passo 3.
8. Os testes do `trocar_antes_de_abrir` em `test_decisoes_ajudante_da_atualizacao.py` (a D-769 escolheu "ao fechar"):
   passo 3.
9. As três frases: nenhum teste antigo muda (o da frase de hoje continua para o caso "voltou"); entram testes novos.

**Vão ao Samuel antes, numa lista, um por um** (a lista exata no ONDE-PAREI de cada passo): os que cobram "pronto" e
"ligado" como anotação (`test_decisoes_testes_a_distancia.py`, `test_decisoes_ajudante_da_atualizacao.py`), os do
`preparo.txt` no ProgramData (`test_decisoes_preparo_d749.py`), as preparações que apontam o `PROGRAMDATA` para uma pasta
de mentira, e os do desinstalar que cobram o gancho do Velopack.

---

## 9. Decisões de antes de hoje que mudaram, e o que continua além do combinado

**Mudadas pelas de hoje:** D-734 (na próxima abertura) → D-769 (ao fechar). D-742 e D-748 (a janelinha só na abertura
depois do "Depois") → ampliadas pela D-770. D-712 e D-721 (as frases das Configurações) → completadas pela D-771. D-727
(tudo dentro do instalador) → exceção só para o servidor de entrar de longe (D-772). D-713 (nada no GitHub nesta etapa)
→ ajustada só para o rascunho de prova (D-773). D-719 (a frase única) → três frases (D-778). D-723 (o Velopack, "baixa
só o que mudou") → o Velopack fica (D-779), sem a diferença (D-789). D-739 (a prova de fora no notebook) → mantida pela
D-780. **Não mudam:** D-724 (a assinatura grátis; `assinatura.py` não muda), D-733, D-741 e D-749 (mudam só por dentro),
D-731 (cumprida pela peça 7), D-764, D-705, D-711, D-715, D-716, D-717, D-718, D-720, D-722, D-728 a D-730, D-732, D-735,
D-736, D-743, D-744 a D-747, D-763.

**Continua além do combinado (versão 1, seção 1.3), agora com a situação:** o socorro fora do que é trocado foi aprovado
("a nossa proteção", D-779). Continuam sem decisão própria dele, com o porquê na versão 1: o estado e o registro do
atualizador saem do ProgramData (fere a D-717); a janela do Kaique deixa de usar o Velopack para saber a versão (é a
causa da sobra que a D-779 manda não nascer); o publicar (pedido dele de publicar rápido). A assinatura (`assinatura.py`)
deixa de mudar (D-789). Ficam de fora de propósito, como na versão 1, os outros lugares que abrem programas de fora (os
motores de achar texto, o servidor de páginas, o brasão, o `--conferir-ocr`), pela D-765.

---

## 10. Conferência contra o Livro: decisão → onde está no plano

- **D-765** (nenhum conserto até a entrega) → o alcance do plano (cabeçalho, seção 1, seção 9); o passo 0 não é conserto
  do programa.
- **D-766** (depois da entrega, cada conserto vira versão) → peça 8 e passo 2 (publicar rápido); passo 3 (a versão
  chega); passo 6 (etapa 7).
- **D-767** (só conta o que rodou de verdade e à vista) → seção 3, "Regras de todos os passos"; a prova à vista de cada
  passo; o alcance fechado pela D-773.
- **D-768** (o motor sai do pacote que se atualiza) → peça 9; passos 2, 3 e 5; seção 7, item 58.
- **D-769** ("Depois" troca ao fechar) → peça 4; passo 3 (prova com "Depois", fechar e desligar no meio); seção 8, item
  8; seção 6.3, ponto 2.
- **D-770** (a janelinha em toda troca) → peça 4; passo 3; seção 6.2, item 4 (o print); seção 6.3, ponto 2.
- **D-771** (ligar é tudo ou nada) → peças 3 e 5; passo 4 (prova sem internet e porta ocupada); seção 6.2, item 5 (o
  texto do desfazer que falha).
- **D-772** (o servidor vem do Windows Update, com aviso) → peça 5; passo 4; seção 6.1, item 11; seção 6.2, item 5.
- **D-773** (as versões de prova de verdade e o rascunho no GitHub) → peça 10b; passo 2 (rascunho e servidor); passos 3
  e 4.
- **D-774** (os testes antigos que mudam) → seção 8; cada passo, "Testes antigos que mudam".
- **D-775** (escrever, testes, quebrar, prova à vista) → seção 3, "Regras de todos os passos"; o foco de quem quebra em
  cada passo.
- **D-776** (publicar no C:, 20 GB livres) → peça 8; passo 2 (prova do espaço e do aviso); seção 6.3, último ponto.
- **D-777** (o .msi só na primeira entrega e quando pedir) → peça 8; passos 2, 5 e 6; seção 6.3, ponto 1.
- **D-778** (as três frases) → peça 4; passo 3 (o print de cada uma); seção 8, item 9.
- **D-779** (Velopack 1.2.161 com a nossa proteção) → peça 4; passos 3 e 5; seção 6.1, item 3.
- **D-780** (as duas trancas, sem o celular) → peças 1 e 5; passo 4 (a leitura das trancas); passo 6 (a prova de fora na
  etapa 7).
- **D-781** (dois campos e o botão de ver) → peça 6b; passo 4 (os prints, a senha nova); seção 6.2, item 5 (o desenho).
- **D-782** (a pergunta mostra "Editor de Impressão") → peça 1; passo 1 (prova); passo 3 (a janelinha); seção 6.1, item
  2; seção 6.3, ponto 3.
- **D-783** (o Samuel desliga o Controle Inteligente de Aplicativos) → passo 6, a lista da etapa 6; seção 7, item 62.
- **D-784** (o pacote de regras do trabalho) → passo 0; os arquivos e as etiquetas de cada passo.
- **D-785** (o que roda à vista e o que fica escondido) → seção 3, "Regras de todos os passos"; a prova de cada passo.
- **D-786** (a velocidade medida no GitHub) → seção 3, "Regras de todos os passos".
- **D-787** (um arquivo de teste por vez no PC) → seção 3, "Regras de todos os passos".
- **D-788** (a pasta do motor dentro da pasta do programa) → peça 9; passo 3 (o motor nasce); passo 5 (sai junto).
- **D-789** (a atualização inteira, sem a diferença) → peça 8; passo 2 (medir o montar); passo 3 (medir o download e a
  troca).
- **D-790** (o motor novo é tudo ou nada) → peças 4 e 9; passo 3 (o servidor fechado no meio do motor).

Nenhuma das 26 ficou de fora.

---

## Detalhe técnico (para a gerente)

- Fontes: o plano da versão 1 e o ONDE-PAREI dele; o estudo do Kraken (ramo `kraken-separado-2026-11-18`); a proposta das
  regras (ramo `regras-agentes-2026-11-18`: §3 a tabela, §5 as conferências, §6 o formulário, §9 as perguntas); o Livro
  do ramo `obra-2026-10-26` (`48d2c3a8`: D-765 a D-790 lidas inteiras, e D-712, D-721, D-724, D-727, D-739, D-741 para
  conferir as que elas mudam); o CLAUDE.md inteiro (com a §11.12 ampliada e a §11.13); o `implementador.md`; o
  `memoria/INDICE.md`.
- Conferido no código (só leitura): o programa se chama `EditorImpressao.exe` (`empacotar.NOME`, `--mainExe`) e o título
  do pacote é "Editor de Impressão" (`empacotar.TITULO_DO_PACOTE`); hoje o pedido de licença abre o `powershell.exe` com
  "runas" (`core/_testes_a_distancia_windows.py`, `_rodar_elevado`); a janela da senha de hoje tem "Agora não" e "OK"
  (`ui/testes_a_distancia_ui.py`).
- O pedido falava em "6 contradições restantes"; pelo Livro faltam 7 (seção 6.2, item 2). Não mudei nada por isso: só
  apontei.
- Nada desta tarefa tocou o programa, os testes, o Windows ou o PC fora da cópia `plano-windows`.
