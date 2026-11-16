# Etapa 4 — Os testes à distância (ONDE-PAREI)

Agente implementador. Ramo `kaique-etapa4-2026-11-16`. Começado em 16/11/2026.

Esta etapa constrói, no programa, a opção dos testes à distância e a janela da senha, e a peça que
fala com o Windows (OpenSSH + Tailscale). **Nada é executado de verdade no Windows de ninguém.** A
peça que fala com o Windows fica isolada numa classe só; os testes a trocam por uma de mentira que
anota os comandos que *seriam* dados.

---

## Decisões que esta tarefa precisa cumprir (número + palavras do Samuel)

- **D-705** — "os testes podem ser feitos via tailscale também, sem precisar de uma porta api?"
  · "acho que esse botão pode ficar dentro do programa né? nas configurações." Testes à distância pelo
  comando de longe do Windows (Servidor OpenSSH), só pela rede do Tailscale, **sem porta de API dentro
  do programa**. Opção nas Configurações liga e desliga.
- **D-711** — "liga sozinho com o windows, eu vou fazer uma senha, e não vai sr chave". O comando de
  longe liga sozinho com o Windows e entra com uma **senha** (não chave).
- **D-712** — "E sim o botão fica nas configurações e já vem selecionado de fabrica." A opção vem
  **ligada de fábrica**; o **instalador não pergunta nada** disso.
- **D-716** — "eu quero ter o poder de escolher se vai estar com prioridade baixa ou não". O Samuel
  escolhe, a cada teste, prioridade baixa ou normal; sem dizer, baixa. (É do lado de quem chama.)
- **D-717** — "sim" (conta separada, escondida, só para os testes). Conta do Windows **só para os
  testes, sem poder de administrador, escondida da tela de entrada**, com a senha que ele criar; os
  projetos de teste nunca se misturam com os do Kaique.
- **D-721** — "ok". Na **primeira vez** que o programa abre, uma **janela pequena** pede "a senha dos
  testes à distância"; sem a senha, os testes ficam **desligados**; dá para pôr a senha depois nas
  Configurações.
- **D-722** — "Sim". Testar antes no PC do Samuel e, no fim, **desfazer tudo** (é a etapa 5; aqui só
  deixo a peça que sabe desfazer, com a lista do que fez).
- **D-725** — "ok" (se o antivírus reclamar da conta escondida, liberar só ela). Ressalva para a
  etapa 5.

## O que já está escolhido e testado aqui (o novo não pode estragar — D-605/§11.8)

- **Configurações em partes** (D-363, lista à esquerda; `tests/test_configuracoes_em_partes.py`,
  `tests/test_promessas.py` P-170): acrescento **uma parte no fim** da lista ("Testes à distância").
  As partes de antes (Aparência, Atalhos, Velocidade, Medidas, Impressão) ficam na mesma ordem e
  nos mesmos índices — os testes delas continuam valendo.
- **O tema de fábrica, os atalhos, as medidas, a velocidade, a impressão**: nada muda.
- **Prova de que cada botão faz o que diz** (D-010; `tests/test_promessas.py`): a parte nova
  acrescenta o botão "Fechar" (como toda parte) e o botão "Pôr a senha dos testes". Acrescento a
  promessa dos dois em `tests/promessas/promessas.md` e a prova do segundo em `test_promessas.py`
  (não mudo nenhuma prova antiga). A caixinha de ligar/desligar é QCheckBox: a varredura não cobra
  promessa de caixinha (fica de fora de propósito).
- **Nenhum teste toca o Windows:** `tests/conftest.py` já isola a pasta de dados. A peça que fala com
  o Windows (`ExecutorWindows`) **se recusa a rodar quando o pytest está rodando** (olha
  `PYTEST_CURRENT_TEST`), e os testes sempre trocam o executor por um de mentira. Dupla proteção.

## Como fica para quem usa e no livro (D-637)

- **Kaique, primeira vez que abre o programa novo:** aparece uma janela pequena "Testes à distância"
  pedindo "a senha dos testes à distância". Ele digita a que o Samuel passar e clica "OK" → o Windows
  faz **uma** pergunta ("Deseja permitir que este aplicativo faça alterações no seu dispositivo?"); ele
  clica "Sim" e pronto. Se clicar "Agora não" (ou deixar em branco), nada é instalado, a opção fica
  ligada mas **sem efeito**, e ele pode pôr a senha depois.
- **Nas Configurações > Testes à distância:** uma caixinha "Deixar o Samuel fazer testes neste
  computador (pela rede do Tailscale)", já marcada. Embaixo, uma frase diz o estado ("Ligado e pronto"
  / "Falta a senha" / "Desligado") e, quando falta a senha, o botão "Pôr a senha dos testes".
- **No PDF e no trabalho dele:** **nada muda.** Esta frente mexe só no começo do programa (a janela da
  senha na primeira vez) e nas Configurações (a parte nova). Os filtros, as ferramentas, os livros e os
  projetos do Kaique não são tocados. Os testes à distância rodam numa conta separada, sem enxergar os
  arquivos dele.

## O plano (o que vou fazer, onde, e a regra num lugar só)

**Por que precisa:** é um pedido novo do Samuel (16/11), não há remendo antigo. A "ferramenta" aqui é
*ligar/desligar os testes à distância*. Para não virar gambiarra (§11.12), a **regra fica num lugar
só** — `core/testes_a_distancia.py` — e todos os caminhos da tela chamam essa mesma função.

1. **`core/testes_a_distancia.py`** (novo; não importa `ui/`). A regra num lugar só:
   - `plano_de_ligar`, `plano_de_desligar`, `plano_de_desfazer`: a lista de passos (comandos do
     Windows), como dados. A senha entra como **variável** `$SenhaDosTestes`, **nunca** o texto da
     senha no comando.
   - `Executor` (a peça que fala com o Windows) + `ExecutorWindows` (roda **uma** pergunta de
     administrador para todos os passos; a senha vai por dentro, cifrada pelo próprio Windows, nunca na
     linha de comando) + `Resultado`. `ExecutorWindows` se recusa a rodar sob o pytest.
   - `ligar(senha)`, `desligar()`: chamam o executor atual e guardam o estado nas Configurações.
   - estado em Configurações: `testes_a_distancia_ligado` (de fábrica `True`, D-712),
     `testes_a_distancia_pronto` (Windows configurado), `testes_a_distancia_senha_perguntada`.
2. **`configuracoes.py`**: as três chaves novas em `PADROES`.
3. **`ui/testes_a_distancia_ui.py`** (novo): a janela pequena da senha e a função da primeira vez.
4. **`ui/tela_configuracoes.py`**: a parte "Testes à distância" (caixinha + estado + "Pôr a senha"),
   acrescentada ao fim de `PARTES`.
5. **`main.py`**: na primeira abertura, chamar a janela da senha (só na produção).
6. Provas: `tests/test_decisoes_testes_a_distancia.py` (novo) + a promessa/prova da parte nova.

**Os caminhos que chegam na regra (caminho → função) — a prova de que não há gambiarra:**

| Caminho | Função que ele usa |
|---|---|
| Janela da senha na primeira abertura (`ui/testes_a_distancia_ui.primeira_vez_se_preciso`) | `core.testes_a_distancia.ligar` |
| Caixinha das Configurações marcada | `core.testes_a_distancia.ligar` |
| Caixinha das Configurações desmarcada | `core.testes_a_distancia.desligar` |
| Botão "Pôr a senha dos testes" | `core.testes_a_distancia.ligar` |

Todos os quatro caminhos passam pela **mesma** `ligar`/`desligar`, que monta os comandos no **mesmo**
`plano_de_ligar`/`plano_de_desligar`. Nenhum caminho tem comando próprio.

## Perguntas para o Samuel (§11.13)

(Preenchidas na entrega, se surgirem. Até agora:)

1. **Do que se trata:** quando o programa for tirado do notebook (desinstalado), o que fazer com a
   conta de testes escondida e com o Servidor OpenSSH — apagar os dois, ou deixar? · **Sua dúvida:**
   ainda não há decisão (o Livro não responde). · **O que você escolhe:** (a) apagar a conta e tirar o
   OpenSSH ao desinstalar; (b) deixar como está; (c) só comentário. **Nada foi feito nisso nesta
   etapa**, como você mandou.

## Andamento

- [x] Ler regras, decisões, estudo, código. Plano escrito.
- [x] `core/testes_a_distancia.py` (a regra num lugar só: planos, Executor, ligar/desligar, estado)
- [x] `core/_testes_a_distancia_windows.py` (a peça de verdade: runas + senha por DPAPI; NÃO rodada)
- [x] `configuracoes.py` (3 chaves em PADROES; `testes_a_distancia_ligado` = True de fábrica)
- [x] `ui/testes_a_distancia_ui.py` (janela da senha, `pedir_senha_e_ligar`, `primeira_vez_se_preciso`)
- [x] `ui/tela_configuracoes.py` (parte "Testes à distância" no FIM de PARTES)
- [x] `main.py` (chama `primeira_vez_se_preciso` depois de `janela.show()`)
- [x] `tests/test_decisoes_testes_a_distancia.py` — **11 passaram no PC** (16/11).
- [x] `tests/promessas/promessas.md`: chave `configurações/Testes à distância/Fechar` em P-170; promessa
      nova **P-215** "Pôr a senha dos testes" (P-172 já era de outro botão). Prova `test_p215_...`
      acrescentada no FIM de `tests/test_promessas.py` (nenhuma prova antiga mudada).
- [x] `relatorios/.../etapa4/prints.py` escrito (NÃO rodado ainda).
- [ ] **`tests/test_promessas.py` no PC: PARADO no meio por ordem da gerente (o Samuel ia desligar o
      PC). Resultado desconhecido.** Não rodar mais testes grandes no PC.
- [ ] Rodada do GitHub (o conjunto inteiro).
- [ ] Prints (rodar `prints.py`, fora da tela) e relatório nos três formatos.

## ONDE PAREI (16/11/2026, ~11:10) e o próximo passo

Parei por ordem da gerente, com tudo salvo e empurrado. Programa: os arquivos passam na checagem de
sintaxe; o arquivo novo de provas passou inteiro no PC.

Próximo passo, nesta ordem:
1. Disparar o GitHub: `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref
   claude/list-server-files-gkos8v -f ramo=kaique-etapa4-2026-11-16` e ler o resultado uma vez no fim.
   Olhar com atenção: `test_promessas.py` (`test_todo_botao_tem_promessa`, `test_toda_promessa_tem_botao`,
   `test_p170`, `test_p215`), `test_configuracoes_em_partes.py`, `test_decisoes*.py`.
2. Se `test_promessas` acusar botão sem promessa na parte nova, acertar só `promessas.md` (nunca uma
   prova antiga).
3. Rodar `prints.py` (pequeno, fora da tela), abrir os dois PNGs e conferir.
4. Relatório com `relatorio.gravar` em `relatorios/frente-kaique-2026-11-16/etapa4/relatorio` (o `.pdf`
   fora do git), commit, push, entrega à gerente.
