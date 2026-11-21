# Regras novas do catálogo dos erros: segunda conferência de quem tentou quebrar (20/11/2026)

Esta é a segunda volta do mesmo verificador, que não escreveu este código. Conferi:
- o código dos consertos (`c51285c4` e `32ff536a`);
- o ONDE-PAREI até `18f5c797`;
- os scripts da rodada no ramo dos testes (`411e8476`).

Não mexi no código, não pedi licença ao Windows e não abri janela na tela do Samuel. O repositório do PC continuou
inteiro: `--is-shallow-repository` deu false antes e depois. Consultei o GitHub duas vezes.

## Pedido

- Papel: verificador
- Commit de partida: 047fd330
- Ramo: regras-catalogo-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `regras_dos_agentes/protecao.py`
- `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
- `tests/test_conferencias_protecao.py`
- `relatorios/regras-catalogo-2026-11-19/`

(Copiado do pacote, sem mudar nada. Só escrevi em `relatorios/regras-catalogo-2026-11-19/quem-quebrou/`.)

## Veredito

**Pode juntar depois do passo 2, com uma condição: a primeira rodada do GitHub depois do passo 2 tem de passar.**

- **O grave da primeira volta está consertado pela causa.**
  - Os scripts da rodada buscam raso só quando a cópia já é rasa.
  - O `git clean` dos scripts só roda no GitHub.
  - O `git rm` não é mais lido como o `rm` do terminal.
- **Simulei a rodada no PC:** o ramo inteiro mais a `.github/` do commit `411e8476`. Sobra um lugar só, o
  `core/windows.py:1211`, que o passo 2 conserta.
- **A rodada 44657609512 ainda não prova isso.** Ela rodou com os scripts antigos (`781d64e6`; foi criada às 01h59 UTC
  e os scripts novos entraram às 02h03 UTC). Por isso a prova de verdade é a rodada depois do passo 2.
- **Não há achado grave novo.**
- **Há um achado médio novo: a liberação "só no GitHub" se engana fácil** (achado 1). Não impede juntar, mas precisa de
  destino.
- **O rótulo de pronto, ainda não.** A D-798 deixa que eu o escreva neste trabalho. Mas falta a rodada verde: o próprio
  formulário fica "não conferido" sem ela. Quando a rodada depois do passo 2 passar e os achados 2 e 5 abaixo forem
  acertados, as condições ficam cumpridas.

## O que li

- O que a gerente pediu nesta volta e o `relatorio-1.md`.
- O código mudado: `git diff 6ac413d8..18f5c797` de `porteiro.py`, `leitura_do_codigo.py`, `protecao.py`,
  `formulario.py`, `montar_pacote.py` e `catalogo.py`, e as provas novas e mudadas em `tests/`.
- O ONDE-PAREI, na seção "O que o agente que tentou quebrar achou" (o destino de cada achado), mais "Testes" e "Como
  cumpri cada uma".
- Os scripts consertados nos anexos (`anexos/workflow/`) e os do ramo dos testes (`411e8476`, comparando com
  `781d64e6`).
- O registro da rodada 44657609512 (as partes que falharam) e o resumo dela: o commit de lá e o horário.
- A peça de fora: o comportamento do `git clean -n` e do `--dry-run` (https://git-scm.com/docs/git-clean), que a
  expressão nova usa. E o `set -e` do Git Bash diante de `[ ... ] && comando`: o `[` que falha numa lista com `&&` não
  encerra o script. Isso é do manual do bash, conhecimento meu, não relido.

## O que conferi nas falhas, nas peças de fora e nos caminhos

Tudo por máquina, no PC.

- **Testes no PC, um arquivo por vez, no commit `18f5c797`** (o código é o de `32ff536a`):
  - codigo: 107 passaram;
  - pacote: 26;
  - protecao: 19;
  - formulario: 41;
  - juiz: 9;
  - copia_inteira: 2.
- **Prova de reversão:** as provas novas rodaram numa cópia à parte, feita com `git archive`, com o código da primeira
  volta (`ce3fa9c4`).
  - Falham lá, e passam no novo:
    - "o `rm` do git não é o `rm`";
    - "acusa o `git clean`";
    - "só no GitHub, na mesma linha";
    - "o `trocar_codigo.sh` consertado passa";
    - os achados 6 e 7 do formulário;
    - "a R157 vai ao Windows sem teste";
    - os três "desligar um jeito";
    - "tirar exemplo de um jeito".
  - O caso do `preparar_versao.sh` passa nos dois. É o esperado: o porteiro antigo já não acusava o script consertado,
    e já acusava as linhas antigas.
  - O teste mudado (achado 2) também passa nos dois. Ele não é prova de reversão.
- **As 108 variações da primeira volta, de novo** (`anexos/volta2-sondar_k25-resultado.txt`).
  - Agora são acusados: `git clean -fdx`, no Python e no `.sh`.
  - Não é mais acusado: `git rm -r --cached`, no Python e no `.sh`.
  - Nada mais mudou: o que passava continua passando. Esses casos são os achados que foram para a Lista de espera.
- **O conserto do `git rm`:** `git rm x && rm -rf "$PASTA"` na mesma linha continua acusado pelo segundo `rm`. Só o
  `rm` que vem logo depois do `git` é trocado.
- **A liberação "só no GitHub" (`SO_NO_GITHUB`), 19 casos** (`anexos/volta2-sondar_so_no_github.py.txt` e o
  resultado):
  - o jeito certo passa, no `.sh` e no Python;
  - `[ ... ] || git ...` (que roda fora do GitHub) é acusado;
  - `git clean -n` e `--dry-run` passam;
  - **onze casos enganam a conferência**, seis no `.sh` e cinco no Python (achado 1).
- **A proteção do GitHub contra afrouxar a K25** (`anexos/volta2-afrouxar_k25-resultado.txt`). Desliguei na memória
  cada jeito de ler o comando, e cada um é acusado agora:
  - o terminal: 3 exemplos;
  - a lista guardada: 1;
  - o texto guardado: 2;
  - tirar a K25: 12.

  **O achado 4 da primeira volta está consertado.** `SO_NO_GITHUB` e `EXEMPLOS_DA_K25` estão nas duas listas de
  protegidos.
- **Os scripts no ramo dos testes:**
  - o `trocar_codigo.sh` e o `preparar_versao.sh` do `411e8476` são iguais, byte por byte, aos de
    `anexos/workflow/`;
  - o `porteiro_juiz.sh` de lá não recebeu o comentário novo do achado 11 (achado 4). O comportamento é o mesmo; só o
    comentário difere.
- **O destino de cada achado** está escrito no ONDE-PAREI, um por um. Os achados 2, 3, 5, 8, 9 e 15 dizem "Lista de
  espera (gerente, 20/11)". O 12 diz outra coisa (achado 5).
- **O formulário do trabalho**, conferido pelo programa na etapa "prova", sem o GitHub:
  - a estrutura passa: o F19 cita o relatório 1 e cada achado tem destino;
  - fica "não conferido" só pela rodada. Com o GitHub, a rodada 44657609512 falhou (o esperado), então só uma rodada
    verde depois do passo 2 libera.

## Caminhos que o outro não listou

- **O texto de liberação na linha, sem olhar o que a linha faz.** A conferência procura o texto da guarda em qualquer
  lugar da linha. Não vê se o comando vem depois de um `;`, de um `|| `, de um `not`, nem se a guarda está dentro de
  um texto (achado 1).
- **A variável `GITHUB_ACTIONS` é escrita por quem roda.** O próprio script, ou quem o chama, pode ligá-la. Pela D-812,
  é dado que o conferido pode trocar. Ela serve para o caso honesto, não como prova.
- **A profundidade numa variável:** `git fetch $PROFUNDIDADE` não é lido. É o mesmo caso "comando montado numa
  variável" da primeira volta, que foi para a Lista de espera.
- **O que o `trocar_codigo.sh` ainda faz se rodado à mão no PC:** `git checkout FETCH_HEAD -- .` (linha 47) escreve
  por cima dos arquivos que o agente mudou e não fez commit. Não é ".git inteiro", então fica fora da K25. É o mesmo
  tipo de risco do `git clean` (achado 15 da primeira volta, Lista de espera).
- **A R157 no pacote da pesquisa.** O pacote de um trabalho sobre a pasta `docs/pesquisa/` inteira tem a etiqueta do
  Windows, porque há pesquisa do Windows lá dentro. Com `basta_uma`, a R157 vai para ele. Uma pesquisa de um arquivo
  só (`docs/pesquisa/x.md`) não recebe a regra (achado 2).

## Falhas não pensadas e resultado não conferido

- **"Rodadas novas já usam os scripts consertados":** é verdade para as próximas rodadas, mas nenhuma rodada provou
  isso ainda. A 44657609512 é de antes. A minha simulação no PC diz que vai dar certo, mas simulação não é a rodada.
- **O ONDE-PAREI diz o que o teste já não cobra:** a linha 242 diz "não no de pesquisa", e hoje a regra vai à pesquisa
  (achado 2).

## As regras que conferi

- **D-809** ("ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha
  o porteiro para ele não fazer isso" · "ok"): **cumprida.**
  - Os scripts da rodada não cortam mais a história de uma cópia inteira.
  - O `git clean` é acusado; o falso alarme saiu.
  - Na simulação, só sobra o lugar do passo 2.
  - O furo da liberação "só no GitHub" (achado 1) é um jeito novo de passar pela conferência, não uma falha da regra.
    Os furos da primeira volta estão na Lista de espera.
- **D-810** ("ok"): **cumprida.** A prova do Livro diz "O pacote dos agentes de Windows e de testes traz a lista": o
  trabalho do Windows sem teste agora recebe a regra (teste novo, que falha no código antigo).
- **D-811** ("ok"): **cumprida, com um resto pequeno.** Contar como teste só uma função `test_...` de verdade está
  consertado. Continuam passando a mesma prova citada para várias proteções e as proteções em linhas sem "-" embaixo do
  primeiro item (achado 3).
- **D-812** ("ok"): **pela metade, como na primeira volta** (o trabalho só de testes). Pela gerente, foi para a Lista de
  espera.
- **D-813** ("ok"): **cumprida.**
  - O comentário do juiz agora diz o que foi provado.
  - A K25 nova (o `git clean`) cita a documentação do `-n` e do `--dry-run`.
- **D-814** ("ok"): **cumprida.** "Nenhuma" com pergunta embaixo não desliga mais a conferência; provei com o meu caso
  da primeira volta.
- **D-791, D-792, D-798, D-803, D-804, D-808:** **cumpridas**, como na primeira volta.
- **Regra 8 do §11 (o novo não estraga o que já funciona):** as provas antigas dos arquivos tocados passam.
  - Uma prova deste mesmo trabalho foi mudada sem aviso (achado 2). Não é prova antiga, já aceita em outro trabalho.
  - Mesmo assim, a mudança precisa estar escrita.
- **Regra 12 do §11 (sem gambiarra):**
  - o `basta_uma` é um campo geral do catálogo, escrito na lista de campos, e lido num lugar só (`escolher_regras`).
    A busca no código não acha outra conta das etiquetas das regras. Não é desvio para um caso;
  - a liberação "só no GitHub" é uma exceção escrita como texto, com o mesmo desenho do "conferiu o atalho"
    (achado 9 da primeira volta).

## Achados

1. **(médio, novo) A liberação "só no GitHub" se engana com a guarda em qualquer lugar da linha.**
   `regras_dos_agentes/porteiro.py:416` (`SO_NO_GITHUB`) e `regras_dos_agentes/porteiro.py:819`.

   Passam sem acusação, e todos rodam o comando no PC:
   - `[ "$GITHUB_ACTIONS" = "true" ] && true || git gc`;
   - `[ ... ] && echo oi; git fetch --depth=1 ...`;
   - `GITHUB_ACTIONS=true; [ "$GITHUB_ACTIONS" = "true" ] && git gc`, ou o `export` na linha de cima;
   - `! [ ... ] && git gc`;
   - no Python, `if not os.environ.get("GITHUB_ACTIONS") == "true": subprocess.run(["git", "gc"])`;
   - a guarda dentro de um texto na mesma linha, e o `or True`.

   Escrever sem querer seria difícil, a não ser o `if not`. Além disso, a variável é um dado que quem roda pode trocar
   (D-812). Sugestão de destino: a Lista de espera, junto com o achado 9 da primeira volta (as duas exceções escritas
   como texto). Aceitar a guarda só no começo da linha e só com `&&` direto fecha a maior parte.
2. **(pequeno) O teste deste trabalho foi mudado sem aviso, e o ONDE-PAREI ficou dizendo o contrário.**
   `tests/test_conferencias_pacote.py:209` e `:211`. A conferência "a R157 não vai à pesquisa" virou "não vai ao
   trabalho de imagem".
   - O motivo existe e é bom: o pacote da pasta `docs/pesquisa/` tem a etiqueta do Windows, e a D-810 manda a regra ao
     trabalho do Windows.
   - Mas ele não está no commit `32ff536a` nem no ONDE-PAREI.
   - E `relatorios/regras-catalogo-2026-11-19/ONDE-PAREI.md:242` ainda diz "não no de pesquisa".
   - Destino sugerido: escrever o motivo e corrigir a linha 242. Não precisa mexer no código.
3. **(pequeno) Do achado 6 da primeira volta, falta a parte da lista.** `regras_dos_agentes/formulario.py:189`
   (`_itens`) e `regras_dos_agentes/formulario.py:331` (`_conferir_protecoes`).
   - Proteções escritas em linhas sem "-" embaixo do primeiro item viram continuação dele, e passam sem teste.
   - A mesma prova citada para cinco proteções também passa.
   - Pode ir para a Lista de espera com os outros. A parte principal (o que conta como teste) está consertada.
4. **(pequeno) O comentário novo do juiz não foi para o ramo dos testes.** É o comentário de
   `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh:52`.
   - O `.github/scripts/porteiro_juiz.sh` do `411e8476` ainda tem a frase antiga ("senão o `rm -rf` apagaria o
     conteúdo da pasta de verdade").
   - O comportamento é igual; só o comentário difere. A gerente copia quando puder.
5. **(pequeno) O destino do achado 12 da primeira volta difere do que a gerente disse.**
   `relatorios/regras-catalogo-2026-11-19/ONDE-PAREI.md:391` diz "vira pergunta ao Samuel se a gerente achar preciso".
   A gerente disse "Lista de espera". Basta uma das duas, escrita igual nos dois lugares.

## Para a gerente

- **Pode juntar depois do passo 2, se a primeira rodada do GitHub depois do passo 2 passar.**
  - A simulação no PC deixa só o `core/windows.py:1211`, que o passo 2 conserta.
  - A rodada 44657609512 ainda rodou com os scripts antigos.
- **Nada grave.**
  - Um médio novo: a liberação "só no GitHub" se engana com a guarda em qualquer lugar da linha. Sugiro a Lista de
    espera.
  - Quatro pequenos. Os dois de texto (achados 2 e 5) são rápidos.
- **O rótulo de pronto vem quando houver a rodada verde e os achados 2 e 5 estiverem acertados.**
