# Onde parei: estudo da atualização e dos testes à distância (etapa 1 da frente do Kaique, 16/11/2026)

Agente pesquisador. Ramo `estudo-kaique-2026-11-16`, cópia `.claude/worktrees/estudo-kaique`. **Só estudo: nenhuma linha
do programa muda; nada é instalado no Windows nem no `.venv`.**

## Decisões que esta tarefa precisa cumprir (copiadas do Livro, `docs/plano/DECISOES.md`, linhas de 16/11/2026)

- **D-705** — "os testes podem ser feitos via tailscale também, sem precisar de uma porta api? no caso eu pedir diretamente para um gerente aqui abrir o programa e fazer testes como faz no meu pc?" · "acho que esse botão pode ficar dentro do programa né? nas configurações." · "não faremos os testes agora no computador do kaique, mas quero deixar tudo pronto para que isso possa ser feito". Na prática: Servidor OpenSSH do Windows, só pela rede do Tailscale, sem porta/API dentro do programa; opção nas Configurações "Deixar o Samuel fazer testes neste computador (pela rede do Tailscale)".
- **D-706** — "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um instalador fazer tudo de novo, como os apps renomados fazem isso?" · "as atualizaçõpes não podem estar ligadas via api". Atualização como Chrome/VS Code/Discord; instalador só na primeira vez; não passa pelos testes à distância.
- **D-711** — "vai a versão de teste, mas atualizada para ele." · "liga sozinho com o windows, eu vou fazer uma senha, e não vai sr chave". OpenSSH liga com o Windows; entra com senha, não chave.
- **D-712** — "E sim o botão fica nas configurações e já vem selecionado de fabrica." Ferramenta de atualização pronta ("ok"); instalador não pergunta nada.
- **D-713** — "não precisa ser privado". Projeto continua público no GitHub; atualização vem dele, com assinatura.
- **D-714** — "1 - vamos seguir sua sugestão" · "e sim o programa pega sozinho, toda vez que o pc inicializar em segundo plano, assim como os nossos testes acontecem." Versão para o Kaique publicada de propósito; procura e instala por trás toda vez que o PC liga.
- **D-715** — "ele dá um aviso se o programa estiver aberto, um aviso para salvar o trabalho atual e reinicializar o programa".
- **D-716** — "eu quero ter o poder de escolher se vai estar com prioridade baixa ou não". Prioridade baixa ou normal a cada teste (sem dizer, baixa).
- **D-717** — "Fica a conta separada, escondida, só para os testes?" → "sim". Conta só para testes, sem administrador, escondida da tela de entrada; projetos de teste não se misturam com os do Kaique.
- **D-718** — "Sim, e tem que avisar a gente de alguma maneira". Se a atualização falhar, volta sozinha para a anterior.
- **D-719** — "1". Aviso na tela: "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. Avise o Samuel." e o erro num registro. Nenhuma senha dentro do programa.
- **D-720** — "Sim". Aviso com "Reiniciar agora" e "Depois"; "Depois" = entra quando o PC ligar de novo.
- **D-721** — "ok". Primeira abertura: janela pede "a senha dos testes à distância"; sem ela, testes desligados; dá para pôr depois nas Configurações.
- **D-722** — "Sim". Teste de verdade no PC do Samuel (etapa 5), desfazendo tudo depois. Nada é testado agora no notebook do Kaique.
- **CLAUDE.md §3** — "Algoritmo consagrado em vez de fórmula própria." (ferramenta pronta, nunca uma nossa inventada).
- **D-709** (regra pedida em 16/11) — plano antes de qualquer conserto ou ferramenta nova.

## O que já está escolhido e testado aqui (D-605)

- Empacotamento: PyInstaller em pasta (`--onedir --contents-directory _internal`), Inno Setup em `C:\Program Files`
  com `PrivilegesRequired=admin`, `AppId` fixo, `vc_redist` oficial; travas e testes em `tests/test_empacotar.py`.
- Pasta de dados em `%LOCALAPPDATA%\EditorImpressao`, que desinstalar não apaga.
- Este estudo não muda nada disso; o plano das etapas 3 e 4 diz o que mudaria.

## Como fica para quem usa e no livro (D-637)

- Nada muda agora (só estudo). O plano no fim do relatório descreve o que o Kaique veria depois.

## Andamento

- [x] Leitura das regras, do plano, das decisões, de `empacotar.py`, `instalador.iss`, `main.py`.
- [x] Pesquisa A (atualização): tufup, Velopack, PyUpdater, WinSparkle, Inno + verificador, MSIX.
- [x] Teste de instalação dos pacotes num ambiente virtual novo (pasta `estudo/venv-teste`, fora do git).
- [x] Pesquisa B (OpenSSH, firewall, conta, prioridade, UAC).
- [x] Pesquisa C (o que falta no empacotamento).
- [x] Documento `docs/pesquisa/atualizacao-e-testes-a-distancia.md`.
- [x] Relatório nos três formatos + plano das etapas 3 e 4 (`relatorio.md/.html/.pdf`; o `.pdf` fora do git).

**ENTREGUE em 16/11/2026.** Pesquisa: `docs/pesquisa/atualizacao-e-testes-a-distancia.md`.

## Como cumpri cada uma

- **D-705, D-711, D-712, D-716, D-717, D-721:** o estudo (§2 da pesquisa) usa só o OpenSSH do Windows, firewall preso à faixa e à placa do Tailscale, nenhuma porta dentro do programa, opção nas Configurações ligada de fábrica, instalador sem pergunta, senha (não chave), conta sem administrador escondida, prioridade baixa por padrão herdada pelos filhos (fonte Microsoft), e uma só pergunta do Windows na primeira abertura.
- **D-706, D-713, D-714, D-715, D-718, D-719, D-720:** Velopack (pronta, MIT) lendo o GitHub público sem senha; tarefa SYSTEM ao ligar o PC; aviso "Reiniciar agora/Depois"; volta da versão anterior (troca: da ferramenta, lido no código; versão nova que não abre: `AllowVersionDowngrade` da ferramenta, a provar); registro em `C:\ProgramData` legível pela conta de testes; assinatura discutida em §1.6 (o Velopack sozinho só confere SHA-256).
- **D-722:** nada instalado, nenhuma conta, nenhuma tarefa; o único teste foi um ambiente virtual novo em `estudo/venv-teste` (fora do git). Para o OpenSSH, só leitura (listar recursos pediu elevação e parei).
- **CLAUDE.md §3 (consagrado):** só ferramentas prontas; "Inno + verificador nosso" descartado por isso.
- Provas em `tests/test_decisoes.py`: não se aplicam (nenhuma linha do programa mudou).

## Perguntas para o Samuel (formato do §11.13)

**Pergunta 1. Qual ferramenta vai atualizar o programa sozinho pela internet?**
Do que se trata: a parte do programa que, toda vez que o notebook do Kaique liga, procura a versão nova no GitHub e instala por trás. Situação: só estudo; nada construído. De onde veio: seu pedido de 16/11 ("como funciona com apps"); as duas candidatas foram instaladas num teste à parte.
O que você escolhe:
- **Velopack (sugestão).** Volta para a versão anterior se a troca falhar, baixa só o que mudou, já lê o GitHub. Troca o instalador de hoje pelo dele (o Kaique vê uma instalação comum). Nada do que já funciona no programa muda.
- **tufup.** Mantém o instalador de hoje e já traz assinatura completa. Não volta se parar no meio, e o Kaique baixa uns 600 MB a cada versão.
- **Só comentário.**

**Pergunta 2. Que assinatura prova que a versão é sua?**
Do que se trata: a "assinatura" que você pediu para a versão que vem do GitHub. Situação: só estudo. Como outros fazem: o Mac (Sparkle) e o tufup usam uma chave grátis conferida pelo programa; programas comerciais compram certificado do Windows.
O que você escolhe:
- **A de graça, conferida pelo programa (sugestão).** Ninguém mais consegue fazer uma versão que o programa aceite. Não tira o aviso "editor desconhecido" do Windows.
- **A de graça mais um certificado pago do Windows.** Também tira o aviso e acalma antivírus; custo todo ano e comprovar identidade (o serviço barato da Microsoft não aceita pessoas do Brasil). Dá para acrescentar depois.
- **Só comentário.**

Sem print: nenhuma tela mudou ainda (os prints vêm com a janela do aviso e a opção nas Configurações).
