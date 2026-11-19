# Passo 0 do plano da parte do Windows: quinta conferência de quem tentou quebrar (19/11/2026)

Esta é a quinta volta do mesmo verificador, que não escreveu o passo 0. Conferi os consertos de Q1 a Q7 e tentei
quebrar de novo pelo mesmo caminho e por caminhos vizinhos. Não mexi no código entregue. As provas rodaram numa cópia
e numa pasta de juiz temporárias, fora do projeto.

## Pedido

- Papel: quebrador
- Commit de partida: 47fb68fa
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO, mas falta pouco.** Q1 a Q7 estão fechados de verdade, e não resta nada grave.

Sobram três consertos pequenos. Os três são o mesmo tipo de furo do Q2: código que o Python carrega e o porteiro não
lê.

- **S1, médio:** a pasta `historico/` está na lista das que não são programa. Mas o programa importa `historico`, o
  arquivo `historico.py` da raiz. Um `historico/__init__.py` toma o lugar dele no import, e o porteiro não o lê.
- **S2, médio-baixo:** no Windows, o Python importa `.pyw` como código-fonte, e o porteiro só lê `.py`.
- **S3, baixo:** uma extensão compilada (`.pyd`) passa. O `.pyc` agora é acusado.

O formulário ficar "não conferido" até a gerente ligar a lista é o combinado e não conta como achado.

## O que li

- O `relatorios/passo0-2026-11-19/ONDE-PAREI.md` na ponta `47fb68fa` ("Como ficou cada achado da quarta volta") e o
  anexo `anexos/funcoes-que-nao-se-mexem.md`.
- O código mudado de `b66e6be9` a `a664329e`:
  - `conversa_com_o_github.py` (`marca_do_juiz`, `marca_do_porteiro`);
  - `porteiro.py` (`NAO_E_PROGRAMA`, `e_programa`, o código compilado);
  - `juiz.py` (`tirados_sem_conserto`);
  - `montar_pacote.py` (`--passo`);
  - `texto_para_o_samuel.py` e os testes.
- O texto `lista-de-excecoes-para-o-samuel.md`.

## O que conferi nas falhas, nas peças de fora e nos caminhos

- **Recontagem:** igual à volta passada. São 176 lugares: 107 no plano, 13 depois da entrega e 56 a perguntar. O
  porteiro de hoje acha os mesmos 176.
- **Q1, fechado.** Repeti o registro de mentira, agora no formato do GitHub e com a marca como linha inteira: a suíte
  escreve "PORTEIRO: CONFERIDO", e o juiz "NAO CONFERIDO". `ler_rodada` devolveu o do juiz.
  - Pelo vizinho: um texto do agente só aparece no registro do juiz quando ele barra. Por exemplo, o texto de um item
    novo da lista com uma quebra de linha e uma marca falsa dentro. Nesse caso, a rodada já falha, e a K21 recusa por
    "não passou". Não serve como ataque.
- **Q2, fechado no caminho provado.** `servicos/__init__.py` com `schtasks` agora dá "BARROU" no juiz com a lista
  "valendo".
  - Conferi as pastas de `NAO_E_PROGRAMA` uma a uma. Não há `.py` em `terceiros/`, `velhos/`, `historico/`,
    `gabarito/` nem `ganchos/`. Em `docs/` e `memoria/` há só scripts de apoio, que o programa não importa.
  - `tests` é um pacote importado por três scripts da raiz que não vão para o Kaique (`gerar_prints.py`,
    `teste_ampliar.py`, `teste_interface.py`).
  - **Hoje, nenhuma dessas pastas esconde código do programa.**
  - Mas `historico` é também o nome de um arquivo do programa (S1).
- **Q3, fechado.** As funções que não se mexem nos passos 3 e 4 estão no anexo e saem do montador com `--passo`.
- **Q4, fechado.** `.pyc` e `.pyo` dão K00. Pelo vizinho, `.pyd` passa (S3).
- **Q5:** é o combinado, fora da conta.
- **Q6, fechado no mesmo caminho.** Com a lista "proposta", tirar o item de `update_exe` sem consertar dá "BARROU",
  "item tirado da lista sem conserto".
  - Pelo vizinho: reescrevi a mesma linha (`return (pasta_do_programa().parent / "Update.exe")`) e tirei o item. O juiz
    deu "NAO CONFERIDO", porque o lugar velho sumiu e o novo não é julgado antes do "sim".
  - Isso não fica escondido: na primeira rodada depois de a gerente ligar a lista, essa linha aparece como erro novo e
    barra. Não é defeito (ver "Falhas não pensadas").
- **Q7:** a gerente aceitou. O texto diz por que a pergunta não tem print.
- **Os vizinhos novos, no juiz com a lista "valendo" como ficará depois do "sim":**
  - `historico/__init__.py` com `schtasks`: "CONFERIDO". Conferi que o Python carrega a pasta `historico/` no lugar do
    `historico.py` quando os dois existem: a pasta ganha.
  - `core/segredo.pyw` com `schtasks`: "CONFERIDO". `importlib.machinery.SOURCE_SUFFIXES` no Python 3.14 do Windows é
    `['.py', '.pyw']`, e testei: `import segredo` carrega o `.pyw`.
  - `core/x.pyd`: "CONFERIDO".

## Caminhos que o outro não listou

- Um pacote numa pasta de `NAO_E_PROGRAMA` com o mesmo nome de um arquivo do programa. Hoje, o caso é o `historico`,
  importado por `projetos.py:42`, `configuracoes.py:93` e `registro.py:18` (S1).
- O código-fonte `.pyw` (S2).
- A extensão compilada `.pyd` (S3).

## Falhas não pensadas e resultado não conferido

- Antes do "sim", uma linha da lista reescrita, com o mesmo erro e o item tirado, passa como "consertada" (o vizinho do
  Q6). **Não é defeito, e por quê:** a gerente liga a lista na versão de teste, e a rodada seguinte julga o código com
  a lista ligada. O erro reescrito aparece como erro novo e barra. Nada fica escondido depois de ligar. O efeito é só a
  contagem que vai ao Samuel ficar menor que a real até lá.
- Nenhum resultado não conferido novo.

## As regras que conferi

- **CLAUDE.md §11.12:**
  - ponto 1, uma peça só: cumprida;
  - ponto 2, nada dado como feito sem conferir: cumprida (Q1 fechado);
  - ponto 3, a lista do que pode falhar: faltam S1 a S3;
  - ponto 4, peça de mentira: cumprida.
- **CLAUDE.md §11.13:** o texto para o Samuel continua cumprindo, e a falta de print está explicada e aceita.
- **Decisões tocadas:**
  - D-791: cumprida no essencial, com S1 a S3;
  - D-800, D-796, D-798, D-792, D-784, D-605 e D-797: cumpridas.

## Achados

Os números começam com "S" (quinta volta). Fechados de verdade: Q1, Q2 (no caminho provado), Q3, Q4 (`.pyc` e
`.pyo`) e Q6 (no caminho provado). O Q5 é o combinado, e o Q7 foi aceito pela gerente.

1. **S1, médio: a pasta `historico/` está fora da vista do porteiro, mas o programa importa `historico`**
   (`regras_dos_agentes/porteiro.py:126`).
   - Um `historico/__init__.py` toma o lugar do `historico.py` da raiz no import de `projetos.py:42`,
     `configuracoes.py:93` e `registro.py:18`.
   - Provado: com a lista "valendo", o juiz deu "CONFERIDO" com um `schtasks` ali dentro.
   - Destino: consertar. Uma pasta de `NAO_E_PROGRAMA` não pode ter o nome de um módulo da raiz (`historico.py`), ou o
     porteiro lê os `.py` dela quando ela tiver esse nome. Um teste cobra que nenhuma pasta da lista tenha nome de
     arquivo `.py` da raiz.
2. **S2, médio-baixo: o `.pyw` é código-fonte que o Python importa no Windows, e o porteiro só lê `.py`**
   (`regras_dos_agentes/porteiro.py:138`, `e_programa`).
   - Provado: `core/segredo.pyw` com `schtasks` deu "CONFERIDO", com a lista "valendo".
   - Destino: consertar. `e_programa`, e as outras conferências que olham `.py`, leem também `.pyw`. Hoje não há
     nenhum `.pyw` no git, então a lista não muda.
3. **S3, baixo: uma extensão compilada (`.pyd`) passa, como o `.pyc` passava antes do Q4**
   (`regras_dos_agentes/porteiro.py:707`).
   - Provado: `core/x.pyd` deu "CONFERIDO".
   - Destino: consertar. Acrescentar `.pyd` ao código compilado acusado (K00). Hoje não há nenhum `.pyd` no git. As
     DLLs do ScanTailor (`core/nativo`, `.dll`) não são importadas pelo Python como módulo, então não entram.

## Para a gerente: o que ficou fora do projeto

- Na cópia temporária (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`)
  ficou mais o ramo de prova `prova5`.
- Ficaram também as pastas `...\quebrar\juiz5`, `...\quebrar\imp` e `...\quebrar\imp2` (as provas do import).
- Nada foi apagado.
