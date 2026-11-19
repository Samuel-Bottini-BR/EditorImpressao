# Passo 0 do plano da parte do Windows: quarta conferência de quem tentou quebrar (19/11/2026)

Esta é a quarta volta do mesmo verificador, que não escreveu o passo 0. Conferi os consertos do relatório 3 (R1 a R7)
e tentei quebrar o juiz novo, que roda o porteiro e a lista da versão de teste. Não mexi no código entregue. As provas
rodaram numa cópia e numa pasta de juiz temporárias, fora do projeto.

## Pedido

- Papel: quebrador
- Commit de partida: edb87d32
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO, mas os dois furos graves da volta passada fecharam pela estrutura.** Ninguém mais põe item na lista
por um ramo de agente, e quem julga vem de fora do ramo.

Tentei quebrar o juiz por oito caminhos:
- erro novo no código;
- porteiro do ramo afrouxado, com um item tirado da lista;
- linha da lista mudada de função, com a função trocada no item;
- `sitecustomize.py` e um arquivo `.pth` no ramo.

Nesses quatro, o juiz barrou ou não se deixou enganar. Restam:
- **dois problemas para consertar:**
  - o formulário pode ler a marca do juiz no registro de outro trabalho da rodada, que roda o código do agente (Q1);
  - o código do programa posto numa pasta nova fica fora da vista do porteiro (Q2);
- três coisas para escrever ou decidir (Q3, Q5, Q6);
- dois detalhes (Q4, Q7).

## O que li

- O `relatorios/passo0-2026-11-19/ONDE-PAREI.md` na ponta `edb87d32`: "Como ficou cada achado da terceira volta" e "A
  mudança do workflow".
- O código mudado de `fc1ca18e` a `93ab77fb`: `juiz.py` (novo), `excecoes.py` (a chave agora tem a função),
  `porteiro_mudancas.py` (`mudancas_na_lista`), `porteiro.py` (`_bandeiras_do_windows` e o apelido corrigido),
  `conversa_com_o_github.py` (a marca) e `formulario.py` (a K21).
- Os anexos `juiz-no-workflow/porteiro_juiz.sh` e `job-porteiro.yml`.
- No ramo dos testes `claude/list-server-files-gkos8v`, commit `c41e4309`: o `.github/scripts/porteiro_juiz.sh`
  aplicado, idêntico ao anexo (conferido com `fc`), e o job `porteiro` no workflow, com `VERSAO_DE_TESTE:
  obra-2026-10-26`, `PORTEIRO_LIGADO: "0"` e `needs: [suite, janela, porteiro]` no resumo.
- A rodada 44479180201. Ainda estava rodando ao fechar este relatório: o trabalho "Porteiro (juiz da versao de teste)"
  terminou com "success", mas o registro só sai com a rodada inteira terminada. Por isso não li a marca dela (Q5).
- O texto `lista-de-excecoes-para-o-samuel.md` e o print `prints/caso-real-reiniciar-agora.png`.

## O que conferi nas falhas, nas peças de fora e nos caminhos

### A recontagem: bate

- **176 lugares em 176 itens**, com "quantas" igual a 1 em todos.
- Meu script independente acha 111 linhas de conversa com o Windows pelas palavras. A lista tem mais 47 que só
  aparecem pelo apelido da biblioteca. São 158 nessa conferência.
- Com 2 de `DETACHED_PROCESS`, 2 de licença de pasta e 14 números de decisão, dá 176.
- Por grupo: o plano conserta 107 (1, 38, 50 e 18); 13 ficam para depois da entrega; 56 são pergunta.
- **Os 13 de "depois da entrega" batem com as palavras da D-800:**
  - a régua dos filtros: 2 linhas da mesma função `achar_acervo`, que pergunta onde fica a Área de Trabalho;
  - o teste de velocidade: 9, que são `_placas_de_video` 5, `tipo_do_disco` 2 e `_caminho_do_powershell` 2. É a
    leitura da placa de vídeo e do disco pelo PowerShell. Duas linhas de `_placas_de_video` leem o registro, mas estão
    na mesma função;
  - as duas dicas do Automático: 2.
- **Os falsos alarmes da volta passada saíram:** `atualizacao.py:748` e `teste_velocidade.py:2317` não estão mais na
  lista. No meu exemplo de antes, as 4 linhas falsas não são mais acusadas.
- A janela escondida (`CREATE_NO_WINDOW`) não conta mais. Os dois `creationflags` do `atualizacao.py` que continuam na
  lista estão na mesma chamada que o `DETACHED_PROCESS`, e isso é certo.

### O juiz: tentativas de quebrar

Montei uma pasta de juiz como o `porteiro_juiz.sh` faz: o `git archive` de `regras_dos_agentes/` e da lista, com a
lista "valendo", como ficará na versão de teste depois do "sim". Rodei
`python -m regras_dos_agentes juiz --conferido <cópia>` de dentro dela.

- **Ramo igual à versão de teste:** "PORTEIRO: CONFERIDO".
- **Erro novo** (um `schtasks` numa função nova): "BARROU".
- **O porteiro do ramo afrouxado** (sem a busca que ignora maiúscula) **e os itens com `powershell.exe` tirados da
  lista:** "BARROU", com as 3 linhas listadas. Afrouxar o porteiro do ramo não serve para nada, porque o juiz usa o
  dele.
- **Pôr item novo mudando a função de uma linha que já tem exceção:** renomeei `update_exe` e troquei a função no
  item. "BARROU", com "item novo na lista (só a gerente põe [...])".
- **`sitecustomize.py` e `x.pth` na raiz do ramo:** nenhum dos dois rodou. O juiz roda de dentro da pasta dele, e a
  pasta do ramo não entra no caminho de busca do Python. O `git` chamado pelo juiz também não é procurado na pasta do
  ramo.
- **Uma pasta nova de programa** (`servicos/__init__.py` com `schtasks`, importada pelo `main.py`): "CONFERIDO". O
  porteiro só olha `core/`, `ui/` e a raiz (Q2).
- **Um `.pyc` sem fonte em `core/`**, que o Python importa: "CONFERIDO" (Q4).
- **O nome da versão de teste no código do ramo:** não conta mais. O juiz usa o `VERSAO_DE_TESTE` escrito no workflow
  do ramo dos testes. O `trocar_codigo.sh` não traz a `.github/` do ramo do agente.

### A marca do juiz no formulário: dá para forjar

- `ler_rodada` (`regras_dos_agentes/conversa_com_o_github.py:83`) fica com a primeira marca "PORTEIRO: ..." que achar
  no registro de qualquer trabalho da rodada.
- Na rodada 44479180201, a ordem é: "Botoes e prints da janela real" e as partes 3, 2 e 4 da suíte primeiro, o
  porteiro depois. Esses trabalhos rodam o código do agente.
- Provei com um registro de mentira na mesma ordem: o teste do agente imprime "PORTEIRO: CONFERIDO" no trabalho dos
  botões, e o juiz de verdade diz "NAO CONFERIDO". `ler_rodada` devolveu `CONFERIDO`.

### A função na identificação do lugar: atrapalha os passos 3 e 4

- Dentro do próprio passo não atrapalha: no fim do passo, os lugares dele somem.
- Atrapalha onde um passo mexe num arquivo que tem lugares de um passo seguinte:
  - em `atualizacao.py`, que é do passo 3, há 2 lugares do passo 5, nas funções `criar_as_tarefas` e `ao_desinstalar`;
  - em `core/testes_a_distancia.py`, que é do passo 4, há 16 lugares do passo 5 (o desfazer e as tarefas dele).
- Se o passo 3 ou o 4 renomear, dividir ou mover essas funções, os 18 lugares viram "item novo" e o juiz barra. Só um
  commit da gerente direto na versão de teste destrava (Q3).

### O texto para o Samuel

- O §11.13 está cumprido no principal:
  - primeira linha: o que é e onde fica;
  - o print do caso real, circulado;
  - o que a conferência faz e o que não faz;
  - "como você escolheu" agora só para os 13 lugares da D-800, com a conta de antes e a de agora;
  - os 43 do teste de velocidade explicados em palavras simples, na pergunta;
  - "O que você escolhe", a sugestão e de onde veio.
- Falta só um print na pergunta dos 56 (Q7).

## Caminhos que o outro não listou

- O registro de outros trabalhos da rodada, lido pela K21 (Q1).
- O programa fora de `core/`, `ui/` e da raiz: uma pasta nova importada pelo `main.py` (Q2). O teste da tabela de
  etiquetas acusaria uma pasta nova, mas ele roda o código do ramo, e o agente pode acrescentar a linha da tabela.
  Quem barra hoje é só a conferência das mudanças (K17), rodada pela gerente.
- Os `.pyc` sem fonte (Q4).
- Os 18 lugares do passo 5 dentro dos arquivos dos passos 3 e 4 (Q3).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido:** a marca que a K21 aceita pode não ser a do juiz (Q1).
- **Falha não pensada:** até o "sim" do Samuel, o juiz sempre diz "NAO CONFERIDO" para o código. Então a K21 deixa
  pendente (código 3) o formulário de toda entrega. Os passos 1 em diante não passam no formulário antes de a gerente
  ligar a lista (Q5).
- **Falha não pensada:** enquanto a lista é "proposta", nada confere que ela bate com o código. O juiz diz "NAO
  CONFERIDO", e o teste do repositório no ramo fica parado. Um ramo pode tirar itens sem conserto, e, se for juntado, a
  lista que vai ao "sim" encolhe sem ninguém ver (Q6).

## As regras que conferi

- **CLAUDE.md §11.12:**
  - ponto 1, uma peça só: cumprida, porque o juiz é o mesmo porteiro, da versão de teste;
  - ponto 2, nada dado como feito sem conferir: pela metade (Q1);
  - ponto 3, a lista do que pode falhar: faltam Q5 e Q6;
  - ponto 4, peça de mentira: cumprida, porque o juiz foi provado com o git e o bash de verdade, pelo construtor e por
    mim.
- **CLAUDE.md §11.13:** cumprido, menos o print da segunda pergunta (Q7).
- **Cada decisão tocada:**
  - D-791: cumprida no essencial (a lista só diminui e ninguém põe item por ramo), com Q1 e Q2;
  - D-800: cumprida (os 13 lugares batem com os pedaços dela);
  - D-796, D-798, D-792 e D-784: cumpridas;
  - D-605: cumprida;
  - D-797: cumprida (a versão de teste é o juiz).

## Achados

Os números começam com "Q" (quarta volta). Fechados de verdade: R1, R2, R3, R4, R5, R6 e R7.

1. **Q1, médio: a K21 aceita a marca "PORTEIRO: ..." de qualquer trabalho da rodada**
   (`regras_dos_agentes/conversa_com_o_github.py:83`).
   - Os trabalhos dos botões e da suíte rodam o código do agente e aparecem antes do porteiro.
   - Provado com um registro de mentira: devolve `CONFERIDO` quando o juiz disse `NAO CONFERIDO`.
   - Até o "sim", isso esconde o "não conferido". Depois, o "BARROU" de verdade já faz a rodada falhar.
   - Destino: consertar. Ler a marca só no trabalho de nome "Porteiro (juiz da versao de teste)", que vem do workflow
     do ramo dos testes, e só na linha do passo do juiz.
2. **Q2, médio: o porteiro não vê programa fora de `core/`, `ui/` e da raiz** (`regras_dos_agentes/porteiro.py:124`,
   `e_programa`). Provado no juiz: `servicos/__init__.py` com `schtasks`, importado pelo `main.py`, deu "CONFERIDO".
   Destino: consertar. Todo `.py` conta como programa, menos as pastas que não são (`tests/`, `relatorios/`, `docs/`,
   `terceiros/`, `velhos/`, `regras_dos_agentes/`, `.github/`...). Recontar a lista depois.
3. **Q3, baixo: a função na chave trava os passos 3 e 4 se mexerem nas funções que guardam lugares do passo 5**
   (`regras_dos_agentes/excecoes.py:82`). São 18 lugares: `atualizacao.py` (`criar_as_tarefas`, `ao_desinstalar`) e 16
   em `core/testes_a_distancia.py`. Destino: escrever no pacote dos passos 3 e 4 quais funções não se renomeiam nem se
   movem, ou que a gerente atualiza o item na versão de teste ao juntar. É o combinado (lugar = função e texto); não é
   defeito.
4. **Q4, baixo: um `.pyc` sem fonte, que o Python importa, passa** (`regras_dos_agentes/porteiro.py:124`). Destino:
   escrever na ressalva, ou acusar todo `.pyc` que esteja no git.
5. **Q5, baixo: até o "sim", toda entrega fica com o formulário pendente pela K21** (`regras_dos_agentes/formulario.py:403`).
   - Isso é coerente com "não conferido nunca vale como passou". Mas quer dizer que o passo 1 não fecha antes de a
     gerente ligar a lista.
   - Destino: pergunta à gerente. Ou o "sim" vem antes da entrega do passo 1, ou há uma regra escrita para esse
     intervalo.
   - Também: não li a marca da rodada 44479180201, que ainda roda. A gerente confere a linha "PORTEIRO: NAO CONFERIDO
     (a versão de teste ... ainda não tem o porteiro)" quando ela terminar.
6. **Q6, baixo: enquanto a lista é "proposta", nada confere que ela bate com o código** (`regras_dos_agentes/juiz.py:63`).
   Um ramo pode tirar itens sem consertar, e a lista que vai ao "sim" encolhe. Destino: consertar. O juiz, mesmo com a
   lista "proposta", roda o porteiro da versão de teste e barra só o item tirado que o código ainda tem. Ou escrever na
   ressalva que a gerente confere a contagem antes de levar a lista ao Samuel.
7. **Q7, baixo: a pergunta dos 56 lugares não tem print**
   (`relatorios/passo0-2026-11-19/lista-de-excecoes-para-o-samuel.md:30`, regra 3 do §11.13). Destino: consertar (um
   print de um caso, por exemplo a tela de início com "Imprimir"), ou a gerente aceita só o texto nessa pergunta.

## Para a gerente: o que ficou fora do projeto

- Na cópia temporária (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`)
  ficou mais o ramo de prova `prova4-base`. Busquei a ponta `edb87d32` do GitHub, porque a busca na pasta do projeto
  falhou com "did not send all necessary objects".
- A pasta do juiz de prova: `...\quebrar\juiz`.
- Nada foi apagado.
