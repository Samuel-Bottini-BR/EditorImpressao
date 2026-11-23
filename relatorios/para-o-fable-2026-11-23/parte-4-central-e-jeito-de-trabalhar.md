# Parte 4. A Central e o jeito de trabalhar

Escrita pela conversa gerente em 23/11/2026. Fato e opinião separados: a opinião está no fim, marcada.

## 4.1 Quem faz o quê

- **O dono (Samuel)** decide o que o programa faz e confere o resultado. Não é programador. Lê em português simples.
- **O usuário (Kaique)** é impressor e não tem formação técnica. Recebe o programa instalado no notebook dele.
- **A conversa gerente** é uma sessão do Claude Code aberta com o Samuel. Ela conversa com ele, divide o trabalho,
  manda os subagentes, junta os ramos e mantém os documentos. Pela regra, não escreve código do programa
  (`CLAUDE.md` §10.1).
- **Os subagentes** têm as regras em `.claude/agents/`. Cada arquivo tem de 10 a 14 KB.
  - `implementador.md`: código de `core/` e scripts.
  - `verificador.md`: testes, antes/depois, pilotar a janela; nunca aprova.
  - `pesquisador.md`: lê código e documentação de fora.
  - `layout.md`: só `ui/`.
  - Desde 20/11 (D-815), quem confere é um **agente novo a cada volta** ("quem tenta quebrar"). Ele lê o código,
    desliga as proteções uma a uma (mutação manual) e roda demonstrações no Windows de verdade. Um mesmo escritor
    fica no máximo 2 voltas.
- **Limite:** no máximo 2 agentes ao mesmo tempo, ou 3 quando o terceiro só lê (§11.11). Agente não abre agente.

## 4.2 Os documentos que mandam

Ordem de leitura obrigatória, no topo do `CLAUDE.md`:

| Documento | Onde | Tamanho em 23/11 | O que é |
|---|---|---|---|
| Livro de decisões | `docs/plano/DECISOES.md`; a cópia que vale está no ramo da versão de teste `obra-2026-10-26` | 618 KB, 841 linhas de decisão (D-001 a D-829) | Cada decisão do Samuel: palavras exatas, o que quer dizer, onde toca, prova de comportamento, situação, dono |
| Estado atual | `docs/plano/ESTADO-ATUAL.md` (`fase-1`) | pequeno | Onde o projeto está |
| Plano | `docs/plano/PLANO-DEFINITIVO.md` (`fase-1`) | 395 KB | Fases, Lista de bugs, Lista de espera, Registro de mudanças |
| Regras técnicas | `CLAUDE.md` (raiz) | 71 KB | Regras do projeto; a seção 11 tem 13 regras, de 26/10 a 18/11 |
| Memória | `memoria/` (índice em `memoria/INDICE.md`) | vários arquivos | Fichas por assunto, `bugs.md`, `catalogo-de-erros.md` (só nos ramos `obra-2026-10-26` e seguintes) |
| Histórico | `historico/Editor de Impressao - resumo para o Claude.md` | 784 KB | Um "PARTE -N" por checkpoint, o mais novo no topo |

- O plano e o Livro têm uma segunda cópia em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\`, fora do
  git, onde o Samuel edita. A gerente mantém as duas iguais (§10.4).
- Todo relatório para o Samuel sai em `.md`, `.html` e `.pdf` por `relatorio.gravar` (`relatorio.py`, linha 346),
  porque ele não abre `.md`.
- Os comandos `/projeto` e `/checkpoint` ficam fora do repositório (`C:\Users\fotog\.claude\commands\`).
  - `/projeto` obriga a conversa nova a ler as regras inteiras.
  - `/checkpoint` grava o estado no histórico e faz commit.

## 4.3 Ramos

- **`fase-1`**: a versão oficial. Tem o plano e o histórico.
- **`obra-2026-10-26`**: a versão de teste, que o Samuel instala e testa. É o ramo onde o Livro vale. Worktree em
  `.claude/worktrees/obra-juncao`.
- **Um ramo por trabalho**, cada um no seu worktree em `.claude/worktrees/`. Em 23/11 havia 200 worktrees (194 em `.claude/worktrees/`)
  (`git worktree list`). Só a gerente junta os ramos.
- O atualizador está em `atualizador-4-consertos-2026-11-21`, que ainda não foi juntado.

## 4.4 Testes

- O `pytest` inteiro roda no GitHub num Windows da nuvem, pela ação "Testes no Windows":
  `.github/workflows/testes-windows.yml` no ramo `claude/list-server-files-gkos8v`.
  - Comando: `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f ramo=<ramo>`.
  - Leva cerca de 2 h.
- No PC do Samuel, um arquivo de teste por vez enquanto o agente trabalha. A suíte inteira roda só antes de juntar no
  `fase-1`.
- Há um filtro de velocidade no GitHub: antes e depois alternados (§4.6).
- Todo conserto de bug ganha um teste que falha no código antigo (§4.7).
- Cada decisão tem uma prova de comportamento em `tests/test_decisoes*.py` (§11.4).

### O porteiro: a barreira automática que já existe

Este fato a gerente tinha esquecido e só achou ao escrever esta parte.

- **O que é.** Existe uma barreira automática desde 18/11 (D-791; ligada no GitHub em 19/11, D-801): o "porteiro", em `regras_dos_agentes/porteiro.py`
  (1.048 linhas) e `porteiro_mudancas.py`. Ele tem 25 conferências, K01 a K25.
- **O que confere.** Algumas leem o código parado. Exemplos:
  - K01: conversa com o Windows fora de `core/windows.py`;
  - K02: `DETACHED_PROCESS`;
  - K03: licença de pasta à mão.

  Outras olham o que a entrega mudou.
- **Onde roda.** No GitHub, em toda entrega (`tests/test_conferencias_codigo.py`), e por
  `python -m regras_dos_agentes porteiro`.
- **O gancho que não roda.** Existe um gancho antes do commit (`ganchos/pre-commit`), mas ele **não está instalado** no
  clone do PC: `.git/hooks/pre-commit` não existe e `core.hooksPath` não está definido.
- **A lista de exceções.** O que já estava errado em 19/11 fica em `tests/conferencias_excecoes.json`, um item por
  lugar, ligada com o "sim" dele (D-801/D-802). No ramo do atualizador (`aa1963b7`) ela tem **164 lugares** (175 na versão de teste, `0f58346a`). Os que mais pesam:
  - 52 em `teste_velocidade.py`;
  - 50 em `core/testes_a_distancia.py`;
  - 33 em `atualizacao.py`;
  - 12 em `core/_testes_a_distancia_windows.py`.
- **Rodado no código da volta 4** (`aa1963b7`, 23/11): "Porteiro: nada novo (5000 arquivos lidos; a lista deixa 164
  lugares)". Ele não pegou o médio 5 por dois motivos:
  - `New-Item -ItemType Directory` não está na lista de palavras da K01;
  - o arquivo já tem 50 lugares de conversa com o Windows aceitos como exceção.
- **O que ele não pode pegar.** Uma mesma lógica escrita de dois jeitos, como o médio 2: é texto diferente fazendo a
  mesma coisa.

## 4.5 A Central de decisões

- **O que é.** Uma página do claude.ai, um "artifact" com banco de dados:
  https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy. Só abre logado na conta do Samuel. **O código da página não
  está no git**: ele só é lido e publicado pela ferramenta de artifacts da conversa gerente.
- **Para que serve.** É onde o Samuel responde perguntas com imagens grandes, escolhe uma opção, comenta, dá
  ordens e registra testes. As respostas ficam gravadas na hora.
- **As abas:** Decidir agora · Conferência · Respostas · Quadro dos trabalhos · Etapas · Agentes · Defeitos ·
  Velocidade · Ordens e ideias.
- **As coleções do banco:**
  - `respostas`: o que ele escolheu e comentou. A gerente responde no próprio documento, com os campos
    `gerente`, `gerenteEm` e `lida`, e com `reabrir`/`anteriores` para pedir uma resposta de novo sem perder a
    antiga.
  - `conferencias`: um relatório por aba.
  - `ordens`, `testes`, `ideias` e `config`: escritas pela página. A gerente marca `estado`.
  - O resto, gerado pela gerente.
- **Como é alimentada:**
  1. A gerente mantém `docs/plano/central/fonte.json`, com as chaves `geral`, `trabalhos`, `agentes` e
     `velocidade`.
  2. `docs/plano/para_a_central.py` junta esse arquivo com o plano, o `memoria/bugs.md` e o git, e grava lotes
     JSON em `D:\programas\EditorImpressao-arquivos\central-banco\`.
  3. A gerente grava esses lotes no banco, de 50 em 50, com a ferramenta de dados de artifacts (ação `batch`).
  4. As abas da Conferência saem de `docs/plano/central/extrair_conferencia.py`, e há 18 arquivos em
     `docs/plano/central/conferencias/`.
- **As regras de escrita** estão no `CLAUDE.md` §10.10 e §11.13. São dez pontos sobre como perguntar ao Samuel,
  tirados de 106 casos de "Ainda não entendi" e 176 comentários dele. Há também um modelo de print com faixas
  coloridas de antes e depois, em `docs/plano/central/modelo-de-print/`.
- **Outras páginas** do mesmo tipo: "Escolhas do Editor de Impressão", "Layout do Editor de Impressão" e "Quando
  revisar uma página". Os endereços estão no `CLAUDE.md` §10.10.
- **Situação:** o quadro dos trabalhos não é atualizado desde 18/11.

## 4.6 Como um trabalho anda, do pedido ao programa

1. O Samuel pede, no chat ou na Central. A gerente grava a decisão no Livro, com as palavras dele, e no Registro
   do plano.
2. A gerente escreve o pedido ao agente. Ele leva as decisões que tocam aquilo e as regras de que o agente lê o
   arquivo dele, o `CLAUDE.md` inteiro e o índice da memória.
3. O agente escreve no seu `ONDE-PAREI.md`, antes de mexer:
   - as decisões que precisa cumprir;
   - o que já está escolhido e testado;
   - como fica para quem usa;
   - a causa;
   - os caminhos que chegam na função;
   - a lista das falhas.

   Depois faz o código e os testes, e entrega à gerente.
4. A gerente manda a rodada inteira no GitHub. Depois vem um agente novo que tenta quebrar.
5. Se ele acha problema, volta para o escritor, numa nova "volta".
6. Quando não acha mais nada, o trabalho entra na versão de teste e o Samuel testa no PC dele. Só ele marca
   aprovado.

## 4.7 O que não está funcionando

Fatos:

- **As regras crescem e os erros continuam.**
  - A seção 11 do `CLAUDE.md` nasceu em 26/10/2026 e tem hoje 13 regras.
  - A regra 12 ("sem gambiarra") ocupa mais de uma página. Foi escrita em 13/11 e estendida a todo o código em
    18/11.
  - De 18 a 22/11 entraram mais decisões de processo: D-796 a D-798, D-807, D-811 a D-813, D-815, D-819 e
    D-827. Várias ainda não viraram texto nas regras.
- **Antes de trabalhar, cada agente lê cerca de 95 KB de regras:** o `CLAUDE.md` (71 KB), o arquivo dele (10 a 14 KB) e o índice (12 KB). Mais
  as decisões copiadas no pedido.
- **O caso do atualizador:** 4 consertos pedidos em 21/11 já levaram 4 voltas, mais uma prova à vista no PC do
  Samuel, e a quinta volta está pendente. A volta 4 foi escrita por um agente que leu a regra 12. Mesmo assim, o
  agente seguinte achou 5 problemas médios, dois deles do tipo que a regra proíbe:
  - a mesma leitura do arquivo de estado com duas regras, uma no vigia e outra no script da troca;
  - a pasta segura criada por `New-Item` próprio em vez de `core.windows.criar_pasta_segura`.

  Detalhe na Parte 2.
- **O mesmo padrão antes do atualizador:** o Girar, o "Só as letras", o "usar em todas" e o Automático. A revisão de
  código de 10/11 achou 17 remendos desse tipo. Detalhe na Parte 1, seção "Os outros ciclos".
- **A gerente também falhou.**
  - Passou a volta 4 para a conferência sem procurar duplicação antes.
  - Em 23/11 disse ao Samuel que não havia barreira automática. O porteiro (acima) existe desde 19/11. As regras e
    os documentos já são tantos que a própria gerente perde o que está construído.

## 4.8 Anatomia dos ciclos

Fatos tirados das Partes 1 e 2. Os casos são o Girar, as três contas do "como fica com este filtro", o "usar em
todas", o Automático contra o "não dividir esta", a lista "o que é do filtro" e a volta 4 do atualizador. O ciclo
tem sempre os mesmos passos:

1. **O pedido chega como um caso.** O Samuel vê um defeito ou decide algo olhando uma página, um botão, um item do
   "aplicar em". A decisão é gravada com as palavras dele sobre aquele caso.
2. **O conserto vai para o lugar onde o caso apareceu.** O agente muda o método que o print mostra. A regra não mora
   num lugar só: fica espalhada em métodos parecidos de `ui/tela_conferir.py` (10.187 linhas) ou em textos de
   PowerShell montados dentro de `atualizacao.py` (2.314 linhas).
   - Exemplo do programa: a D-662 entrou só no "todas as folhas" do Girar.
   - Exemplo do atualizador: a leitura que tenta de novo entrou só no vigia.
3. **O teste prova o caso pedido.** Ninguém cobra que todos os caminhos deem o mesmo resultado. Então a divergência não
   deixa nenhum teste vermelho.
4. **O Samuel ou o agente que tenta quebrar acha o mesmo defeito no caminho vizinho.** Abre-se uma volta nova.
   - O Girar levou 9 voltas.
   - As figurinhas e o "comparar" levaram 5.
   - O porteiro (o passo 0 da parte do Windows) teve 6 rodadas de conferência, com 19, 9, 7, 6, 3 e 1 achados.
5. **Quando o defeito é de efeito colateral, entra uma proteção nova em vez de sair a causa.** Na volta 4 do
   atualizador, quatro peças que só protegem outra nasceram num commit só (`586b483f`). Três dos cinco problemas novos
   moram nelas.

Dois fatos agravam o ciclo:

- **O que se sabe errado não é desfeito.** Dos 17 remendos que a revisão de 10/11 listou, 16 continuam no código. A
  decisão D-765, de 17/11, congelou os consertos do programa até a entrega ao Kaique, e o código novo continua sendo
  escrito em cima deles.
- **A resposta a cada ciclo foi escrever uma regra nova.** A regra 12 ("sem gambiarra") nasceu do Girar em 13/11. A
  ampliação de 18/11 nasceu do atualizador. A volta 4 foi escrita depois das duas e repetiu o padrão.

O único caso em que o ciclo fechou foi o "Tirar o fundo" (caso 6 da Parte 1). Ali o dado passou a ter uma função só
em `core/`, e os caminhos foram levados até ela.

## 4.9 Opinião da gerente (separada)

- Escrever mais regra não segurou o erro. O que segurou foi o agente que tenta quebrar, e ele só entra no fim da
  volta, quando o código já está escrito.
- Parte das voltas do atualizador vem do desenho dele: peças que existem para proteger outras peças nossas. Cada
  conserto acrescentou uma peça em vez de tirar uma causa. A Parte 2 diz quais peças parecem ser assim.
- O peso de leitura antes de cada tarefa (regras longas, documentos de centenas de KB) provavelmente atrapalha mais
  do que ajuda. Isso é palpite, não medição.
