# Passo 2 do plano da parte do Windows: décima conferência de quem tentou quebrar (volta 11, 21/11/2026)

Do que se trata: é a ferramenta que prepara as versões do programa para o notebook do Kaique (o "publicar"), que roda
só no PC do Samuel. A volta 11 consertou os 4 problemas pequenos do relatório 9 e as frases que saíam "em a pasta",
"de a pasta" e "em o GitHub" em vez de "na pasta", "da pasta" e "no GitHub".

Sou um agente novo nesta volta (D-815). Não escrevi nada desta volta nem das anteriores. Não mexi no código: as
mutações e as sondas foram em cópias (`git archive`) na pasta de rascunho desta conversa, `v10q\`.

O que **não** fiz:

- não rodei o publicar, o PyInstaller, o vpk nem o `gh release` de verdade (D-785, item 8: a gerente roda, à vista);
- não abri janela nem pergunta do Windows na tela do Samuel;
- não disparei rodada do GitHub (só li a 44936850048);
- não rodei `tests/test_ocr_kraken.py` (esta volta não mexe no Kraken); um Python por vez, um arquivo de teste por vez,
  com a memória livre conferida antes de cada rodada (entre 3,5 e 3,9 GB, com o jogo aberto);
- não mexi em `C:\EditorImpressaoProva` (só listei), na pasta errada de 19/11 nem na junção `modelos`; nenhum comando
  de git que muda o `.git` (`--is-shallow-repository` = false na cópia e na pasta principal, antes e depois).

## Pedido

- Papel: quebrador
- Commit de partida: edd39a9f (a ponta conferida: baba4eb8; o último código: 97a5c4b6)
- Ramo: passo2-publicar-2026-11-19

## Veredito

**PRONTO PARA CONFERIR: os quatro consertos resolvem a causa num lugar só, as 33 junções de "em"/"de" com o nome do
destino passaram todas pela mesma função, e o único teste antigo que mudou foi a linha que o Samuel autorizou (D-821).**
Nenhum dos três problemas que achei chega ao Kaique nem ao livro.

Ficam 3 baixos e 4 observações:

- **Baixo 1:** a guarda que impede "em {destino}" escrito à mão olha só um jeito de escrever. Escrito de outros quatro
  jeitos ("em " + nome, uma variável, "(em {…})", `.format`), passa em todos os testes. Hoje nenhuma frase está errada
  (contei: zero junções à mão).
- **Baixo 2:** o item 19 do roteiro da prova à vista manda usar a pasta `versoes 3` "nova e vazia", e ela já tem o motor
  publicado na prova 3. Repetido como está, não para onde o roteiro espera.
- **Baixo 3:** duas frases do formulário ficaram com o texto de antes da resposta do Samuel (dizem que a frase da D-816
  não mudou).

Nunca "aprovado": só o Samuel aprova.

O que está certo (provado rodando, não só lido):

- **A reversão confere com a do outro, teste por teste.** No código de partida (`edd39a9f`) com os testes novos, falham
  os 3 casos das frases e o "quem decide o pode gravar"; no código de antes da D-821 (`1624a05a`), falham o teste da
  volta 3 mudado e a guarda (anexo `anexos-10/reversao-no-codigo-antigo.txt`).
- **As contas do outro conferem:** a guarda acha 33 junções em `edd39a9f`, 2 em `1624a05a` (as da D-816) e 0 agora
  (anexo `anexos-10/contar-juncoes-resultado.txt`).
- **Os consertos dos baixos 2, 3 e 4 têm teste que acusa:** as minhas mutações B1, B2, B3 e D1 foram todas acusadas.
- **No PC, um arquivo por vez, tudo passa;** no GitHub, a rodada 44936850048 testou `97a5c4b6` (o último código) e deu
  success em tudo.

## Decisões que esta tarefa precisa cumprir

Palavras copiadas do Livro da `obra-2026-10-26`.

- **D-767** "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Conferi: os
  testes novos dos baixos 3 e 4 rodam o código de verdade de uma cópia de trabalho de verdade; a única peça trocada é a
  regra dizendo "não" (no teste de "quem decide"), escrita como tal. **Cumprida.**
- **D-775** "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Esta é a etapa 3. **Cumprida.**
- **D-785** "ok, mais ainda existem mais casos na opção A" · "ok". Nada à vista rodado; só o roteiro mudou. **Cumprida**
  (com o baixo 2 no roteiro).
- **D-798** só quem confere escreve "PRONTO PARA CONFERIR". O formulário do outro não traz o rótulo. **Cumprida.**
- **D-807** o conjunto inteiro só no GitHub. Li a rodada, não rodei o inteiro no PC. **Cumprida.**
- **D-813** "a recusa compara a coisa de verdade, não o texto". A guarda das frases compara o texto de um jeito só
  (baixo 1). **Pela metade** na guarda; o código de hoje está certo.
- **D-815** agente novo em cada volta de quem quebra. **Cumprida** (sou novo).
- **D-816** "A , mas onde estamos antes de você fazer qualquer processo". O que o publicar faz depois do pedido de
  liberar não mudou (os `test_d816_*` passam); só as palavras, pela D-821. **Cumprida.**
- **D-817** "pode". O teste que saiu na volta 4 continua fora; o substituto passa. **Cumprida.**
- **D-818** "vai ter que reprogramar?" · "A". A régua do Visual C++ e a conferência da pasta já montada não mudaram
  (`test_d818_*` passam). **Cumprida.**
- **D-819** "sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer". Cada conserto traz o mais simples
  e o escolhido, com o porquê. **Cumprida.**
- **D-820** "A". A pasta das ferramentas continua num lugar só; a montagem do Visual C++ agora pergunta só a ela.
  **Cumprida.**
- **D-821** "ok, mas qual vai ser o proximo passo, todo resto está funcionando?". A frase da D-816 sai "na pasta"/"no
  GitHub"; o teste da volta 3 mudou numa linha só (conferido no `git diff`); a guarda não tem exceção. **Cumprida.**
- **D-605 / CLAUDE.md §11.8** nenhum teste antigo muda para passar. Conferido linha a linha (abaixo). **Cumprida.**

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro (§4.6, §4.7, §11.8, §11.12 com os seis pontos e a D-813,
  §11.13), `memoria/INDICE.md`, `memoria/licoes.md` e o caderno dos erros da `obra-2026-10-26` (famílias F1 a F10).
- Na cópia `passo2` (ponta `baba4eb8`): o ONDE-PAREI (o começo e a Volta 11 inteira, em todas as seções), o relatório 9
  (os achados que esta volta consertou), a prova 3 de hoje e os anexos `reversao-volta11-*` e `volta11-*`.
- O Livro da `obra-2026-10-26`: D-767, D-775, D-785, D-798, D-807, D-813, D-815 a D-821, inteiras.
- O código: `git diff edd39a9f..baba4eb8` inteiro (`empacotar.py`, `publicar_versao_kaique.py` e os dois arquivos de
  teste), `core/pasta_das_ferramentas.py`, e todo uso de `.nome` e `.onde` de destino no programa.

## O que conferi

### A rodada do GitHub (lida, não disparada)

Rodada 44936850048: o log diz 71 vezes o commit `97a5c4b6` (o último que mexe em código; depois dele só o
ONDE-PAREI mudou, conferido com `git diff --stat 97a5c4b6..baba4eb8`). Success no porteiro (o juiz da versão de
teste), nos botões e prints da janela real e nas cinco partes do conjunto inteiro. Lá: `test_pasta_das_ferramentas.py`
17 passaram, `test_publicar_versao.py` 125.

### No PC, um arquivo por vez

| Arquivo | Resultado |
|---|---|
| `tests/test_pasta_das_ferramentas.py` | 17 passaram |
| `tests/test_publicar_versao.py` | 125 passaram |
| `tests/test_empacotar.py` | 43 passaram |
| `tests/test_publicar_motor.py` | 12 passaram |
| `tests/test_publicar_servidor.py` | 14 passaram |
| `tests/test_decisoes_atualizacao.py` | 38 passaram |
| `tests/test_decisoes.py` | 27 passaram |
| as nove `tests/test_conferencias_*.py` | 12, 77, 2, 14, 34, 9, 21, 20 e 11: todas passam |
| o porteiro no repositório inteiro | "nada novo (4922 arquivos lidos; a lista deixa 175 lugares)" |
| o conferidor do formulário, etapa "quebrar", com o pacote da volta 11 | passa, com um aviso K14 (observação 2) |

A cópia `passo2` ficou sem nenhuma mudança depois de cada rodada (`git status` vazio).

### Algum teste antigo mudou além da linha da D-821? (§11.8)

Li `git diff edd39a9f..baba4eb8 -- tests/` linha a linha:

- `tests/test_publicar_versao.py`: dentro de testes antigos, só a linha autorizada
  (`"ficou liberada em"` → `"ficou liberada na pasta"`) e um comentário em cima dela. O resto é acrescentado no fim (a
  guarda e o teste das frases).
- `tests/test_pasta_das_ferramentas.py`: nenhum teste antigo mudou. Mudou a ajuda `_copiar_o_codigo` (o pedido do baixo
  2): ela agora **para** quando não acha a linha do caminho, em vez de seguir. Isso deixa os testes antigos mais
  rigorosos, não mais fáceis: está escrito no formulário. O resto é acrescentado no fim.

### Cada conserto resolve a causa, num lugar só? (§11.12)

- **Baixo 1 e observação 4 (o roteiro):** os itens 19 e 21 agora são só da cópia, e os comandos têm o Python da pasta
  principal escrito inteiro. Resolve. Mas o item 19 ficou com uma pasta que não está mais vazia (baixo 2 deste relatório).
- **Baixo 2 (a cópia de prova dos testes):** a troca do caminho continua num lugar só (`_copiar_o_codigo`), e agora para
  com `pytest.fail` quando a linha não aparece exatamente uma vez. A mutação B1 (só parar quando aparece mais de uma
  vez) foi acusada.
- **Baixo 3 (o "pode gravar?" do Visual C++):** a conta própria (`DOWNLOADS.parent.is_dir()`) e a segunda frase saíram;
  quem decide é `problema_para_gravar`. Procurei outra conta da mesma pergunta no programa: não há (o caminho só está
  escrito em `core/pasta_das_ferramentas.py`; os outros lugares são textos de ajuda). As mutações B2 (criar a
  `downloads` antes de perguntar) e B3 (só perguntar quando a pasta de cima não existe) foram acusadas.
- **Baixo 4 (a frase do `--motor-kraken`):** um teste pelo que o empacotar imprime e um pelo `Parou` do
  `publicar --motor`. As mutações M3 e M4 do outro mostram que cada um acusa só o seu lugar.
- **As frases:** as 33 junções passam pela `com_preposicao`; nenhuma ficou à mão (contei pela própria guarda, e procurei
  à mão todo uso de `destino.nome`, `self.nome` e `Apagado.onde`: os que sobram são "para a pasta", o nome no começo da
  linha e o `Apagado(..., destino.nome)` que a frase do apagar junta pela mesma função). Fora do publicar, nenhum arquivo
  usa o nome de um destino numa frase. As mutações C1 e C2 (tirar uma contração da tabela) foram acusadas, e D1 (a
  segunda junção da D-816 de volta para "liberada em") também.

### A guarda pega o vizinho? (F2, D-813; anexo `anexos-10/mutacoes-g-c-b-d-resultado.txt`)

Numa cópia de `baba4eb8`, uma mutação por vez, `tests/test_publicar_versao.py` inteiro:

| Mutação | O que sai na frase | Resultado |
|---|---|---|
| G1 | `"o motor publicado em " + destino.nome` | 125 passam |
| G2 | `onde = destino.nome` e depois `f"... liberada em {onde}"` (no instalador que não chegou) | 125 passam |
| G3 | `f"... (em {destino.nome}) ..."` (no índice estragado) | 125 passam |
| G4 | `"não consegui liberar {} em {} ({})".format(...)` | 125 passam |
| G5 | `f"... deixado por {destino.nome}"` ("por a pasta") | 125 passam |

As cinco saem "em a pasta" (ou "por a pasta") para quem lê, e nenhum teste vê. O outro escreveu a ressalva só do G2 (a
variável). O G3 é o mais perto do jeito que a guarda procura: é um f-string com `destino.nome`, e passa só porque a
guarda pede um espaço antes do "em" (`endswith(" em ")`), e ali há um parêntese.

## Achados

1. **BAIXO: a guarda das frases olha um jeito só de escrever "em {destino}".**
   - Onde: `tests/test_publicar_versao.py`, `_preposicao_a_mao` (a comparação `antes.value.endswith(" em ")` /
     `" de "`, só f-string, só `{… .nome}` e `{… .onde}` logo depois).
   - Provado: as mutações G1 a G4 acima. Quatro jeitos de escrever "em a pasta" passam em todos os testes. O G5 mostra
     que a `com_preposicao` só conhece "de" e "em" ("por" e "a" também se juntam com o artigo: "pela pasta", "à pasta");
     hoje não há frase assim.
   - Hoje nenhuma frase está errada: contei zero junções à mão e li todos os usos do nome do destino. É a família F2 de
     novo (a conferência olha o jeito mais comum).
   - O que pedir: a guarda cobrar a coisa de verdade, não o texto em volta. Uma ideia simples: todo uso de `.nome` (e
     `.onde`) de um destino no `publicar_versao_kaique.py` tem de estar dentro de `com_preposicao(...)`, no começo da
     frase ou depois de "para " (uma lista curta dos lugares aceitos); qualquer outro uso, inclusive guardar numa
     variável, é acusado. Isso pega G1 a G4. Se a gerente achar que não vale a pena agora, basta a ressalva do outro
     ganhar os quatro jeitos.

2. **BAIXO: o item 19 do roteiro manda usar uma pasta que já não está vazia.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md`, "A prova de verdade", item 19 (o reescrito na volta 11): "numa
     pasta de provas nova e vazia com espaço no nome: ... `--pasta "C:\EditorImpressaoProva\versoes 3"` tem de parar com
     'publique o motor antes'".
   - Provado (só listei): `C:\EditorImpressaoProva\versoes 3` tem `motor-kraken-1`, publicado na prova 3 de hoje
     (11h33). Repetido como está, o publicar não para em "publique o motor antes", porque o motor já está lá. O item 21
     também usa `versoes 3` (ali não faz mal: a versão 1.1.0 foi apagada no fim da prova).
   - O item diz que a gerente o repete "da pasta principal" depois da junção. É o mesmo tipo do baixo 1 do relatório 9
     (roteiro que não dá para seguir ao pé da letra).
   - O que pedir: trocar o nome da pasta do item 19 por uma nova (ex.: `versoes 6`), e conferir antes que ela não existe.

3. **BAIXO: duas frases do formulário dizem que a frase da D-816 não mudou.**
   - Onde: `relatorios/passo2-publicar/ONDE-PAREI.md`, "Como cumpri cada uma", Volta 11, D-816 ("a frase de depois do
     pedido de liberar não mudou (nem as palavras)"); e "Como fica para quem usa e no livro", Volta 11 ("A frase do
     caminho de erro depois do pedido de liberar (a da D-816) fica como está até a resposta da pergunta").
   - Provado (lido): depois da D-821 (`97a5c4b6`), as palavras dessa frase mudaram ("pedi para liberar na pasta", "se
     ficou liberada na pasta"). O resto do formulário já diz isso (a seção D-821 logo abaixo, "O que foi feito", item 18).
   - É a família F7 (o escrito não bate com o código), num texto pequeno; o conferidor do formulário não pega isso.
   - O que pedir: acertar as duas frases ("as palavras mudaram pela D-821; o que o publicar faz, não").

4. **OBSERVAÇÃO 1: a reversão e as mutações do outro conferem.**
   - A minha reversão deu o mesmo resultado que o anexo dele, teste por teste, nos dois códigos de antes. As mutações M1
     a M9 dele não repeti (li o script; as minhas B1 a B3, C1, C2 e D1 cobrem os mesmos lugares de outro jeito, e foram
     todas acusadas).
   - Três dos testes novos passam no código de partida (a montagem sem a `ferramentas` e o `--motor-kraken` nas duas
     telas): eles cobram o que o código já fazia certo sem teste. A prova deles é a mutação, não a reversão; está
     escrito assim no formulário. Não é ressalva grave, porque não são conserto de defeito, são proteção nova.

5. **OBSERVAÇÃO 2: o registro do servidor das versões no git (a gerente pediu a minha opinião, não a decisão).**
   - O que é: `relatorios/servidor-das-versoes/registro-2026-11-21-111014.txt`, uma linha ("servindo
     C:\EditorImpressaoProva\versoes 3 em http://127.0.0.1:8765/"), escrita pelo servidor na prova 3. Entrou no git no
     commit `0a3b54a9`, só ele, sem mudar.
   - Minha opinião: **pode ficar** (é pequeno, não tem segredo e é o registro de uma prova de verdade). Mas a causa
     continua: o servidor grava o registro dentro do repositório por padrão (`servidor_das_versoes.py`, o `--registro`
     de fábrica em `relatorios/servidor-das-versoes/`). Cada prova nova vai criar outro arquivo fora do git, o
     conferidor vai acusar, e alguém vai pôr no git de novo. O conferidor também avisa (K14) que o arquivo está fora da
     lista do pedido. Duas saídas, para a gerente escolher: o roteiro passar `--registro` para
     `C:\EditorImpressaoProva\` (onde já ficam os outros registros da prova), ou uma linha no `.gitignore` para esses
     registros. Qualquer das duas é mudança fora desta volta.

6. **OBSERVAÇÃO 3: a `com_preposicao` é chamada em 33 lugares com a mesma tabela.**
   - É o jeito certo (uma regra, um lugar só). Só anoto que ela depende de o nome do destino começar pelo artigo ("a
     pasta", "o GitHub"); o `test_obs6` acusa se isso mudar (a mutação C1 foi acusada por ele).

7. **OBSERVAÇÃO 4: o Livro desta cópia é antigo.**
   - O `pacote` da ferramenta das regras, rodado da cópia, não acha D-816 a D-820 (o outro anotou para a Lista de bugs).
     Conferi as palavras no Livro da `obra-2026-10-26`: as que o formulário copiou batem.

## O que falta

- Para a prova à vista: o baixo 2 (a pasta do item 19). O resto do roteiro está como o relatório 9 pediu.
- Para juntar: os baixos 1 e 3 (ou a decisão da gerente de deixar o 1 como ressalva).

## Para a gerente: o que ficou fora do projeto

Na pasta de rascunho desta conversa,
`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\52740cda-b98f-4183-a448-ea9ff84b0439\scratchpad\` (criada
nesta tarefa):

- `v10q\antigo`, `v10q\meio` e `v10q\novo`: o código de `edd39a9f`, `1624a05a` e `baba4eb8` (`git archive`, inteiro:
  **uns 826 MB cada, 2,5 GB no total**; eu devia ter tirado as pastas grandes). Em `antigo\tests\` e `meio\tests\` estão
  por cima os dois arquivos de teste de `baba4eb8`. A `novo\` voltou como saiu do git: conferi depois, arquivo por arquivo, os quatro que mudei contra o
  `git show baba4eb8`, iguais sem contar o fim de linha (o `git archive` grava com CRLF). A última linha do meu script
  (`sem mutacao: ... -> 0`) não conferia nada (comparava o arquivo com ele mesmo); a conferência que vale é esta.
  Não apaguei: pela regra, quem decide é a gerente.
- `mutar.py`, `contar.py`, `mutacoes.txt`, `reversao.txt`, `dec.md`, `pub_edd.py`, `pub_1624.py` e `run.log` (o
  registro da rodada 44936850048, uns 0,9 MB). As cópias que importam estão em `quem-quebrou/anexos-10/`.

O pytest também cria as pastas dele em `C:\Users\fotog\AppData\Local\Temp\pytest-of-fotog\` (ele guarda só as últimas).
Não apaguei nada em lugar nenhum.

## Fontes

- Python 3.14, módulo `ast`: um f-string vira `JoinedStr` com partes `Constant` e `FormattedValue`; dois pedaços de
  f-string lado a lado viram um só (por isso a guarda vê as frases de duas linhas); concatenação com `+` é `BinOp`, e
  `.format` é uma chamada: nenhum dos dois é `JoinedStr` (por isso G1 e G4 passam).
- Rodada do GitHub 44936850048 (lida com `gh run view`).
