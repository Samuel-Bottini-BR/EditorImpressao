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
- [ ] Relatório nos três formatos + plano das etapas 3 e 4.

## Perguntas para o Samuel

(nenhuma ainda)
